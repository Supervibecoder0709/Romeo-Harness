"""어댑터 컴파일 계약.

지키는 것:
1. managed 마커 밖 텍스트는 절대 건드리지 않는다 (사용자가 쓴 CLAUDE.md 내용).
2. 두 번 컴파일해도 결과가 같다 (idempotent).
3. `.agents/skills/*` 는 실제 파일이다 — 심링크면 Windows 에서 깨진다.
4. vendor 투영본은 원문과 blob SHA 가 같다 (수정 0 이 투영 후에도 유지된다).
5. `--check` 가 stale(코어를 고치고 컴파일하지 않은 상태)과 managed block 손댐을 잡는다.
"""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from romeo.compile import (MANAGED_END, MANAGED_START, check_compiled, compile_all,
                           replace_managed_block)
from romeo.provenance import blob_sha
from romeo.util import project_root

REPO = project_root(Path(__file__).parent)
INPUTS = ["core", "adapters", "vendor", "provenance", "skills"]


def make_tree(dst: Path):
    for name in INPUTS:
        shutil.copytree(REPO / name, dst / name)
    (dst / ".harness").mkdir(exist_ok=True)
    shutil.copy(REPO / ".harness/bindings.yaml", dst / ".harness/bindings.yaml")
    return dst


def snapshot_outputs(root: Path):
    """컴파일이 소유하거나 보존 병합하는 경로의 바이트·종류·mode 스냅샷."""
    entries = {}
    for rel in ("AGENTS.md", "CLAUDE.md", ".agents", ".claude", ".harness/compiled.yaml"):
        start = root / rel
        paths = [start]
        if start.is_dir() and not start.is_symlink():
            paths.extend(sorted(start.rglob("*")))
        for path in paths:
            key = str(path.relative_to(root))
            if path.is_symlink():
                entries[key] = ("symlink", os.readlink(path))
            elif path.is_dir():
                entries[key] = ("dir", path.stat().st_mode & 0o777)
            elif path.is_file():
                entries[key] = ("file", path.stat().st_mode & 0o777, path.read_bytes())
            else:
                entries[key] = ("missing",)
    return entries


class TestManagedBlock(unittest.TestCase):
    """마커 치환 자체의 계약. 파일 전체를 다루기 전에 이것부터 맞아야 한다."""

    def test_inserts_when_absent(self):
        out = replace_managed_block("사용자 텍스트\n", "새 내용", source="core/x.md")
        self.assertIn("사용자 텍스트", out)
        self.assertIn("새 내용", out)
        self.assertIn(MANAGED_START, out)
        self.assertIn(MANAGED_END, out)

    def test_preserves_text_outside_markers(self):
        original = ("# 내 문서\n\n앞쪽 사용자 텍스트\n\n"
                    f"{MANAGED_START} source=core/x.md sha=aaaaaaaa -->\n옛 내용\n{MANAGED_END}\n\n"
                    "뒤쪽 사용자 텍스트\n")
        out = replace_managed_block(original, "새 내용", source="core/x.md")
        self.assertIn("앞쪽 사용자 텍스트", out)
        self.assertIn("뒤쪽 사용자 텍스트", out)
        self.assertIn("새 내용", out)
        self.assertNotIn("옛 내용", out)

    def test_is_idempotent(self):
        first = replace_managed_block("앞\n", "내용", source="core/x.md")
        second = replace_managed_block(first, "내용", source="core/x.md")
        self.assertEqual(first, second)

    def test_multiple_blocks_of_other_owners_are_untouched(self):
        original = (f"{MANAGED_START} source=core/x.md sha=aaaaaaaa -->\n옛\n{MANAGED_END}\n\n"
                    "<!-- openwiki:managed start -->\n남의 블록\n<!-- openwiki:managed end -->\n")
        out = replace_managed_block(original, "새", source="core/x.md")
        self.assertIn("남의 블록", out)
        self.assertIn("openwiki:managed", out)


class TestCompile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = make_tree(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_outputs_for_both_runtimes(self):
        compile_all(self.root)
        self.assertTrue((self.root / "CLAUDE.md").exists())
        self.assertTrue((self.root / "AGENTS.md").exists())
        self.assertTrue((self.root / ".claude/skills/plan/SKILL.md").exists())
        self.assertTrue((self.root / ".agents/skills/plan/SKILL.md").exists())
        self.assertTrue((self.root / ".claude/skills/plan-close/SKILL.md").exists())
        self.assertTrue((self.root / ".agents/skills/plan-close/SKILL.md").exists())

    def test_preserves_user_text_in_instructions_file(self):
        (self.root / "CLAUDE.md").write_text("# 프로젝트 지침\n\n사용자가 직접 쓴 규칙이다.\n", encoding="utf-8")
        compile_all(self.root)
        text = (self.root / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("사용자가 직접 쓴 규칙이다.", text)
        self.assertIn(MANAGED_START, text)

    def test_second_run_changes_nothing(self):
        compile_all(self.root)
        snapshot = {p: p.read_bytes() for p in sorted(self.root.rglob("*")) if p.is_file()}
        compile_all(self.root)
        after = {p: p.read_bytes() for p in sorted(self.root.rglob("*")) if p.is_file()}
        self.assertEqual(set(snapshot), set(after), "두 번째 컴파일이 파일 목록을 바꿨다")
        changed = [str(p.relative_to(self.root)) for p in snapshot if snapshot[p] != after[p]]
        self.assertEqual(changed, [], f"두 번째 컴파일이 내용을 바꿨다: {changed}")

    def test_vendor_skills_are_projected_verbatim(self):
        compile_all(self.root)
        src = self.root / "vendor/obra-superpowers@b36e082/skills/test-driven-development/SKILL.md"
        for runtime_dir in (".claude/skills", ".agents/skills"):
            dst = self.root / runtime_dir / "test-driven-development/SKILL.md"
            self.assertTrue(dst.exists(), f"{dst} 가 투영되지 않았다")
            self.assertEqual(blob_sha(dst.read_bytes()), blob_sha(src.read_bytes()),
                             f"{dst} 가 원문과 다르다")

    def test_vendor_reference_files_are_projected_too(self):
        compile_all(self.root)
        # SKILL.md 만 옮기면 본문이 참조하는 파일이 끊긴다
        self.assertTrue((self.root / ".claude/skills/test-driven-development/writing-good-tests.md").exists())
        self.assertTrue((self.root / ".agents/skills/systematic-debugging/root-cause-tracing.md").exists())

    def test_deferred_skills_are_not_projected(self):
        compile_all(self.root)
        for name in ("subagent-driven-development", "writing-plans", "brainstorming"):
            self.assertFalse((self.root / ".claude/skills" / name).exists(),
                             f"{name} 은 채택하지 않았는데 투영됐다")

    def test_local_skill_is_a_real_file_not_symlink(self):
        compile_all(self.root)
        target = self.root / ".agents/skills/repo-archive"
        self.assertTrue(target.exists())
        self.assertFalse(target.is_symlink(), "심링크는 Windows 에서 깨진다 — 실제 파일이어야 한다")
        self.assertTrue((target / "SKILL.md").is_file())
        self.assertFalse((target / "SKILL.md").is_symlink())

    def test_replaces_existing_symlink_dir_with_real_files(self):
        # 이 저장소의 .agents/skills/repo-archive 가 원래 심링크였다.
        target = self.root / ".agents/skills"
        target.mkdir(parents=True, exist_ok=True)
        (target / "repo-archive").symlink_to("../../skills/repo-archive", target_is_directory=True)
        compile_all(self.root)
        link = target / "repo-archive"
        self.assertFalse(link.is_symlink(), "심링크가 실제 디렉터리로 대체되지 않았다")
        self.assertTrue((link / "SKILL.md").is_file())

    def test_check_detects_symlinked_output_dir(self):
        compile_all(self.root)
        link = self.root / ".agents/skills/repo-archive"
        shutil.rmtree(link)
        link.symlink_to("../../skills/repo-archive", target_is_directory=True)
        codes = sorted(f[0] for f in check_compiled(self.root))
        self.assertIn("COMPILE_SYMLINK", codes, "디렉터리 심링크를 통과시키면 안 된다")

    def test_settings_deny_is_written(self):
        compile_all(self.root)
        import json
        data = json.loads((self.root / ".claude/settings.json").read_text(encoding="utf-8"))
        perms = data["permissions"]
        # 되돌릴 수 있지만 승인이 필요한 것은 ask, 승인으로도 정당화 못 하는 것은 deny
        self.assertIn("Bash(git push:*)", perms["ask"])
        self.assertIn("Bash(gh pr merge:*)", perms["ask"])
        self.assertIn("Bash(sudo rm:*)", perms["deny"])
        self.assertNotIn("Bash(git push:*)", perms["deny"])

    def test_settings_preserves_other_keys(self):
        import json
        p = self.root / ".claude/settings.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"model": "opus", "permissions": {"allow": ["Bash(ls:*)"]}},
                                ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        compile_all(self.root)
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(data["model"], "opus", "하네스가 소유하지 않는 키를 지웠다")
        self.assertEqual(data["permissions"]["allow"], ["Bash(ls:*)"])
        self.assertIn("Bash(git push:*)", data["permissions"]["ask"])

    def test_check_detects_removed_deny_rule(self):
        import json
        compile_all(self.root)
        p = self.root / ".claude/settings.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        data["permissions"]["ask"] = [d for d in data["permissions"]["ask"] if "git push" not in d]
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        codes = sorted(f[0] for f in check_compiled(self.root))
        self.assertIn("COMPILE_STALE", codes)

    def test_settings_user_keys_are_ignored_by_check_but_preserved_by_compile(self):
        import json
        compile_all(self.root)
        p = self.root / ".claude/settings.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        data["model"] = "sonnet"
        data["permissions"]["allow"] = ["Bash(ls:*)"]
        p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n",
                     encoding="utf-8")

        self.assertEqual(check_compiled(self.root), [],
                         "사용자 소유 키 변경을 하네스 산출물 stale 로 취급했다")

        data["permissions"]["deny"] = []
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.assertIn("COMPILE_STALE", sorted(f[0] for f in check_compiled(self.root)),
                      "사용자 키 변경이 하네스 소유 키 훼손을 가렸다")

        compile_all(self.root)
        repaired = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(repaired["model"], "sonnet")
        self.assertEqual(repaired["permissions"]["allow"], ["Bash(ls:*)"])
        self.assertTrue(repaired["permissions"]["deny"])

    def test_broken_source_symlink_is_rejected_before_outputs_change(self):
        from romeo.compile import CompileError
        compile_all(self.root)
        before = snapshot_outputs(self.root)
        broken = self.root / "skills/repo-archive/broken-reference.md"
        broken.symlink_to("missing-reference.md")

        failure = None
        try:
            compile_all(self.root)
        except Exception as exc:
            failure = exc

        self.assertEqual(snapshot_outputs(self.root), before)
        self.assertIsInstance(failure, CompileError)

    def test_invalid_existing_settings_is_rejected_before_outputs_change(self):
        from romeo.compile import CompileError
        compile_all(self.root)
        settings = self.root / ".claude/settings.json"
        settings.write_text("{ invalid json\n", encoding="utf-8")
        core = self.root / "core/principles/AGENTS.core.md"
        core.write_text(core.read_text(encoding="utf-8") + "\n새 원칙\n", encoding="utf-8")
        before = snapshot_outputs(self.root)

        with self.assertRaises(CompileError):
            compile_all(self.root)

        self.assertEqual(snapshot_outputs(self.root), before)

    def test_mid_commit_replace_failure_rolls_back_every_output(self):
        from unittest import mock
        from romeo.compile import CompileError
        compile_all(self.root)
        core = self.root / "core/principles/AGENTS.core.md"
        core.write_text(core.read_text(encoding="utf-8") + "\n교체될 새 원칙\n", encoding="utf-8")
        before = snapshot_outputs(self.root)
        real_replace = os.replace
        calls = []

        def fail_third_replace(src, dst):
            calls.append((str(src), str(dst)))
            if len(calls) == 3:
                raise PermissionError("injected replace denial")
            return real_replace(src, dst)

        with mock.patch.object(os, "replace", side_effect=fail_third_replace):
            with self.assertRaises(CompileError):
                compile_all(self.root)

        self.assertGreaterEqual(len(calls), 5, "실패 전 교체와 그 뒤 롤백이 모두 실행되지 않았다")
        self.assertEqual(snapshot_outputs(self.root), before)
        self.assertEqual(list(self.root.glob(".compile-*")), [])

    def test_deferred_skill_is_removed_on_recompile(self):
        # 채택을 취소하면 산출물이 남아 있으면 안 된다 — 남으면 라우터 게이트 없이 discovery 된다.
        import yaml
        compile_all(self.root)
        self.assertTrue((self.root / ".claude/skills/test-driven-development").exists())
        imports = self.root / "provenance/imports.yaml"
        data = yaml.safe_load(imports.read_text(encoding="utf-8"))
        for item in data["imports"]:
            if item["id"] == "sp-test-driven-development":
                item["status"] = "deferred"
        imports.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        compile_all(self.root)
        self.assertFalse((self.root / ".claude/skills/test-driven-development").exists(),
                         "채택 취소한 스킬이 남아 있다")
        self.assertFalse((self.root / ".agents/skills/test-driven-development").exists())
        self.assertEqual(check_compiled(self.root), [])

    def test_check_fails_without_state(self):
        compile_all(self.root)
        (self.root / ".harness/compiled.yaml").unlink()
        codes = sorted(f[0] for f in check_compiled(self.root))
        self.assertIn("COMPILE_NO_STATE", codes)

    def test_output_path_outside_repo_is_refused_before_writing(self):
        import yaml
        from romeo.compile import CompileError
        a = self.root / "adapters/claude/adapter.yaml"
        data = yaml.safe_load(a.read_text(encoding="utf-8"))
        data["settings_file"] = "../outside.json"
        a.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        outside = self.root.parent / "outside.json"
        before = outside.exists()
        with self.assertRaises(CompileError):
            compile_all(self.root)
        self.assertEqual(outside.exists(), before, "저장소 밖 파일을 건드렸다")

    def test_absolute_output_path_is_refused_before_staging_writes(self):
        import yaml
        from romeo.compile import CompileError
        a = self.root / "adapters/claude/adapter.yaml"
        data = yaml.safe_load(a.read_text(encoding="utf-8"))
        absolute = self.root / "ABSOLUTE-OUTPUT.md"
        data["instructions_file"] = str(absolute)
        a.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

        with self.assertRaises(CompileError):
            compile_all(self.root)

        self.assertFalse(absolute.exists(), "staging 이 절대경로를 따라 실제 산출물에 먼저 썼다")

    def test_managed_marker_inside_code_fence_is_not_touched(self):
        p = self.root / "CLAUDE.md"
        doc = ("# 문서\n\n마커 쓰는 법 설명:\n\n```markdown\n"
               f"{MANAGED_START} v0 source=x sha=1 -->\n사용자 예시\n{MANAGED_END}\n```\n")
        p.write_text(doc, encoding="utf-8")
        compile_all(self.root)
        text = p.read_text(encoding="utf-8")
        self.assertIn("사용자 예시", text, "코드펜스 안의 사용자 예시를 덮어썼다")

    def test_duplicate_romeo_block_is_refused(self):
        from romeo.compile import CompileError
        compile_all(self.root)
        p = self.root / "CLAUDE.md"
        p.write_text(p.read_text(encoding="utf-8")
                     + f"\n{MANAGED_START} v0 source=x sha=1 -->\n둘째\n{MANAGED_END}\n",
                     encoding="utf-8")
        with self.assertRaises(CompileError):
            compile_all(self.root)

    def test_crlf_file_keeps_single_block(self):
        p = self.root / "CLAUDE.md"
        compile_all(self.root)
        p.write_text(p.read_text(encoding="utf-8").replace("\n", "\r\n"), encoding="utf-8")
        compile_all(self.root)
        text = p.read_text(encoding="utf-8")
        self.assertEqual(text.count(MANAGED_START), 1, "CRLF 파일에 블록이 중복 생성됐다")

    def test_unclosed_marker_is_refused(self):
        from romeo.compile import CompileError
        p = self.root / "CLAUDE.md"
        p.write_text(f"# 문서\n\n{MANAGED_START} v0 source=x sha=1 -->\n닫히지 않음\n", encoding="utf-8")
        with self.assertRaises(CompileError):
            compile_all(self.root)

    def test_check_passes_right_after_compile(self):
        compile_all(self.root)
        self.assertEqual(check_compiled(self.root), [])

    def test_check_detects_stale_core_change(self):
        compile_all(self.root)
        core = self.root / "core/principles/AGENTS.core.md"
        core.write_text(core.read_text(encoding="utf-8") + "\n## 10. 새 원칙\n\n새로 넣었다.\n", encoding="utf-8")
        codes = sorted(f[0] for f in check_compiled(self.root))
        self.assertIn("COMPILE_STALE", codes)

    def test_check_detects_hand_edited_managed_block(self):
        compile_all(self.root)
        p = self.root / ".claude/skills/plan/SKILL.md"
        text = p.read_text(encoding="utf-8").replace("bin/romeo card", "bin/romeo CARD-손댐")
        p.write_text(text, encoding="utf-8")
        codes = sorted(f[0] for f in check_compiled(self.root))
        self.assertIn("COMPILE_STALE", codes)

    def test_check_ignores_user_text_outside_markers(self):
        compile_all(self.root)
        p = self.root / "CLAUDE.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n\n## 내가 나중에 추가한 절\n\n마커 밖이다.\n",
                     encoding="utf-8")
        self.assertEqual(check_compiled(self.root), [],
                         "마커 밖 사용자 텍스트는 컴파일 검사 대상이 아니다")

    def test_check_detects_missing_output(self):
        compile_all(self.root)
        shutil.rmtree(self.root / ".agents/skills/plan")
        codes = sorted(f[0] for f in check_compiled(self.root))
        self.assertIn("COMPILE_MISSING", codes)

    def test_overrides_appear_in_instructions(self):
        compile_all(self.root)
        text = (self.root / "CLAUDE.md").read_text(encoding="utf-8")
        # 원문을 고칠 수 없으므로 override 는 지침 파일에 인쇄되어야 실제로 읽힌다
        self.assertIn("orca worktree create", text)
        self.assertIn("read-only", text)

    def test_role_binding_appears_in_both_runtimes(self):
        compile_all(self.root)
        for f in ("CLAUDE.md", "AGENTS.md"):
            text = (self.root / f).read_text(encoding="utf-8")
            self.assertIn("implementer", text)
            self.assertIn("reviewer", text)

    def test_core_principles_reach_both_runtimes(self):
        compile_all(self.root)
        for f in ("CLAUDE.md", "AGENTS.md"):
            text = (self.root / f).read_text(encoding="utf-8")
            self.assertIn("실행은 완료가 아니다", text)


if __name__ == "__main__":
    unittest.main()
