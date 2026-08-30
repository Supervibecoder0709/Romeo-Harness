"""어댑터 컴파일 계약.

지키는 것:
1. managed 마커 밖 텍스트는 절대 건드리지 않는다 (사용자가 쓴 CLAUDE.md 내용).
2. 두 번 컴파일해도 결과가 같다 (idempotent).
3. `.agents/skills/*` 는 실제 파일이다 — 심링크면 Windows 에서 깨진다.
4. vendor 투영본은 원문과 blob SHA 가 같다 (수정 0 이 투영 후에도 유지된다).
5. `--check` 가 stale(코어를 고치고 컴파일하지 않은 상태)과 managed block 손댐을 잡는다.
"""
import fnmatch
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from romeo.compile import (MANAGED_END, MANAGED_START, STAGE_GLOB, STATE_PATH,
                           _prepare_compile, _previous_outputs, _stage_compile,
                           _state_bytes, _strip_frontmatter, check_compiled, compile_all,
                           list_outputs, replace_managed_block)
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


def uncovered(touched, outputs):
    """`outputs` 가 담지 못한 경로. 끝에 `/` 가 붙은 항목은 그 아래 전부를 덮고, `*` 가 든 항목은
    이름이 매번 달라 미리 적을 수 없는 경로를 패턴으로 덮는다 — `allowed_paths` 를 읽는 방식과 같은 규칙이다."""
    entries = set(outputs)
    dirs = tuple(rel for rel in entries if rel.endswith("/") and "*" not in rel)
    globs = [rel.rstrip("/") for rel in entries if "*" in rel]

    def covered(rel):
        if rel in entries or (dirs and rel.startswith(dirs)):
            return True
        parts = rel.split("/")
        return any(fnmatch.fnmatch("/".join(parts[:i + 1]), pattern)
                   for i in range(len(parts)) for pattern in globs)

    return sorted(rel for rel in touched if not covered(rel))


def files_snapshot(root: Path):
    """작업 트리의 모든 일반 파일을 바이트로 찍는다. 어떤 경로가 바뀌었는지 실측으로 판정하기 위한 것이다."""
    out = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            out[str(path.relative_to(root))] = ("symlink", os.readlink(path))
        elif path.is_file():
            out[str(path.relative_to(root))] = ("file", path.read_bytes())
    return out


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

    def test_project_index_reaches_both_runtimes(self):
        """프로젝트 인덱스는 원본 하나에서 두 지침 파일로 간다(체크리스트 32).

        마커 밖에 손으로 유지하면 한쪽 런타임만 인덱스를 보는 상태가 만들어지고, 그 어긋남을
        검사하는 게이트가 없다. 같은 것을 보지 않는 두 실행의 판정이 같다는 것은 동등성의 증거가 아니다."""
        compile_all(self.root)
        _, index = _strip_frontmatter(
            (self.root / "core/principles/PROJECT.core.md").read_text(encoding="utf-8"))
        index = index.strip()
        self.assertIn("## 문서 인덱스", index, "인덱스 원본이 비었다 — 이 테스트가 아무것도 지키지 못한다")
        for name in ("CLAUDE.md", "AGENTS.md"):
            text = (self.root / name).read_text(encoding="utf-8")
            self.assertIn(index, text, f"{name} 에 프로젝트 인덱스 원본이 그대로 들어있지 않다")

    def test_both_runtimes_get_the_same_core_sections(self):
        """두 지침 파일의 공통 절(인덱스 + 행동 규칙)은 바이트까지 같아야 한다.

        다른 것은 역할 표·권한 상한처럼 그 런타임의 강제 수단을 인쇄하는 자리뿐이다."""
        compile_all(self.root)
        _, index = _strip_frontmatter(
            (self.root / "core/principles/PROJECT.core.md").read_text(encoding="utf-8"))
        _, principles = _strip_frontmatter(
            (self.root / "core/principles/AGENTS.core.md").read_text(encoding="utf-8"))
        shared = index.strip() + "\n\n---\n\n" + principles.strip()
        claude = (self.root / "CLAUDE.md").read_text(encoding="utf-8")
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(shared, claude)
        self.assertIn(shared, agents)

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

    def adapter_patterns(self):
        """어댑터가 선언한 ask·deny 패턴. 목록 자체는 사람이 바꾸는 값이므로 여기에 고정하지 않는다."""
        from romeo.util import load_yaml
        cfg = load_yaml(self.root / "adapters/claude/adapter.yaml")
        return cfg.get("settings_ask") or [], cfg.get("settings_deny") or []

    def test_settings_deny_is_written(self):
        """어댑터가 선언한 패턴이 그대로 나가고, 두 분류가 겹치지 않는다.

        특정 명령 이름을 여기에 적지 않는다 — 목록은 사람이 정하는 값이라
        적어 두면 상한을 조정할 때마다 테스트가 깨지고, 그때 고치고 싶어지는 것은
        정본이 아니라 테스트다. 이 검사가 지키는 것은 **목록의 내용이 아니라 배선**이다:
        어댑터가 선언한 것이 빠짐없이 나가는가, ask 와 deny 가 섞이지 않는가.
        """
        compile_all(self.root)
        import json
        data = json.loads((self.root / ".claude/settings.json").read_text(encoding="utf-8"))
        perms = data["permissions"]
        ask, deny = self.adapter_patterns()
        self.assertTrue(ask, "어댑터의 settings_ask 가 비었다 — 승인 게이트가 통째로 사라졌다")
        self.assertTrue(deny, "어댑터의 settings_deny 가 비었다 — 자동 거부가 통째로 사라졌다")
        self.assertEqual(perms["ask"], ask, "어댑터가 선언한 ask 와 산출물이 다르다")
        self.assertEqual(perms["deny"], deny, "어댑터가 선언한 deny 와 산출물이 다르다")
        self.assertEqual(set(perms["ask"]) & set(perms["deny"]), set(),
                         "같은 패턴이 ask 와 deny 에 동시에 있다 — 어느 쪽이 이기는지 알 수 없다")
        # deny 는 승인으로도 정당화되지 않는 것이다. 그중 하나는 반드시 관리자 권한 삭제다.
        self.assertIn("Bash(sudo rm:*)", perms["deny"])

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
        ask, _ = self.adapter_patterns()
        self.assertEqual(data["permissions"]["ask"], ask,
                         "사용자 키를 보존하면서 하네스 소유 키도 그대로 나가야 한다")

    def test_check_detects_removed_deny_rule(self):
        import json
        compile_all(self.root)
        p = self.root / ".claude/settings.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        # 어느 한 줄을 지우든 잡혀야 한다 — 무엇을 지웠는지가 아니라 지웠다는 사실이 판정 대상이다.
        data["permissions"]["ask"] = data["permissions"]["ask"][1:]
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

    def test_new_workflows_are_projected_to_both_runtimes(self):
        # 코어 절차가 늘어도 두 런타임이 같은 것을 받아야 한다 — 한쪽만 투영되면 역할 교체가 성립하지 않는다.
        compile_all(self.root)
        for skills_dir in (".claude/skills", ".agents/skills"):
            for name in ("implement", "review"):
                p = self.root / skills_dir / name / "SKILL.md"
                self.assertTrue(p.is_file(), f"{p} 가 투영되지 않았다")
                self.assertIn(f"core/workflows/{name}/SKILL.md", p.read_text(encoding="utf-8"),
                              f"{p} 가 코어 원본을 가리키지 않는다")

    def test_workflow_table_marks_non_entrypoints(self):
        # 진입점은 하나다(K-60). implement·review 를 "라우터 진입점" 으로 인쇄하면 지침 파일이 코어와 반대말을 한다.
        compile_all(self.root)
        for f in ("CLAUDE.md", "AGENTS.md"):
            rows = {}
            for line in (self.root / f).read_text(encoding="utf-8").split("\n"):
                if line.startswith("| `") and line.count("|") >= 4:
                    cells = [c.strip() for c in line.split("|")]
                    rows[cells[1].strip("`")] = cells[3]
            for name in ("implement", "review"):
                self.assertIn(name, rows, f"{f} 절차 표에 {name} 행이 없다")
                self.assertEqual(rows[name], "승인 뒤 라우터가 켤 때만",
                                 f"{f} 가 {name} 을 진입점처럼 인쇄했다")
            for name in ("plan", "plan-close"):
                self.assertEqual(rows[name], "라우터 진입점",
                                 f"{f} 가 기존 진입점 행을 바꿨다")

    # ── 역할 투영·바인딩 (리뷰 F-09 · F-11 · F-17 · F-31) ─────────────────────
    def test_role_contract_reaches_both_runtimes(self):
        # core/roles/*.yaml 을 읽는 코드가 테스트뿐이면 역할 계약은 어느 런타임에도 도달하지 않는다.
        compile_all(self.root)
        for f in ("CLAUDE.md", "AGENTS.md"):
            text = (self.root / f).read_text(encoding="utf-8")
            self.assertIn("core/roles/implementer.yaml", text, f"{f} 에 역할 계약 원본 링크가 없다")
            self.assertIn("core/roles/reviewer.yaml", text)
            self.assertIn("workspace-write", text, f"{f} 에 구현자 능력이 인쇄되지 않았다")
            self.assertIn("docs/work/{unit_id}/", text, f"{f} 에 쓰기 범위가 인쇄되지 않았다")
            self.assertIn("자기 역할의 산출물을 스스로 검토했다고 선언하는 것", text,
                          f"{f} 에 역할 금지 항목이 인쇄되지 않았다")

    def test_swap_enforcement_is_printed_in_both_directions(self):
        # 교체 실행에서 검토자가 되는 런타임의 강제 수단이 정본에도 산출물에도 있어야 한다.
        import yaml
        bindings = yaml.safe_load((self.root / ".harness/bindings.yaml").read_text(encoding="utf-8"))
        for key in ("roles", "parity_swap"):
            for name, role in bindings[key].items():
                self.assertTrue(isinstance(role, dict) and role.get("enforcement"),
                                f"bindings.yaml {key}.{name} 에 강제 수단 선언이 없다")
        compile_all(self.root)
        for f in ("CLAUDE.md", "AGENTS.md"):
            text = (self.root / f).read_text(encoding="utf-8")
            for key in ("roles", "parity_swap"):
                for name, role in bindings[key].items():
                    self.assertIn(role["enforcement"], text,
                                  f"{f} 에 {key}.{name} 의 강제 수단이 인쇄되지 않았다")
            self.assertIn("미관측", text, f"{f} 가 미검증 강제 수단을 관측된 것처럼 인쇄했다")

    def test_permission_ceiling_reaches_both_runtimes(self):
        # 권한 상한이 한쪽 런타임에만 컴파일되면 동등성 비교의 전제가 깨진다(K-66).
        import yaml
        bindings = yaml.safe_load((self.root / ".harness/bindings.yaml").read_text(encoding="utf-8"))
        ceiling = bindings["permission_ceiling"]
        compile_all(self.root)
        for f in ("CLAUDE.md", "AGENTS.md"):
            text = (self.root / f).read_text(encoding="utf-8")
            self.assertIn("## 권한 상한", text, f"{f} 에 권한 상한 절이 없다")
            for cmd in ceiling["approval_required"] + ceiling["never"]:
                self.assertIn(cmd, text, f"{f} 에 상한 항목 '{cmd}' 가 인쇄되지 않았다")
        # 두 런타임 모두 '자기가 구현자일 때' 의 상한을 인쇄해야 한다 — 기본 실행과 교체 실행이 서로 다른 런타임이다.
        claude = (self.root / "CLAUDE.md").read_text(encoding="utf-8")
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("기본 실행에서 이 런타임이 `implementer` 일 때", claude)
        self.assertIn("교체 실행에서 이 런타임이 `implementer` 일 때", agents)

    def test_claude_settings_ask_covers_declared_ceiling(self):
        # 정본 상한과 런타임 패턴이 갈라지면 설정 파일이 상한을 덜 막는다.
        import yaml
        bindings = yaml.safe_load((self.root / ".harness/bindings.yaml").read_text(encoding="utf-8"))
        adapter = yaml.safe_load((self.root / "adapters/claude/adapter.yaml").read_text(encoding="utf-8"))
        patterns = " ".join(adapter["settings_ask"])
        for cmd in bindings["permission_ceiling"]["approval_required"]:
            self.assertIn(cmd, patterns,
                          f"claude 어댑터의 settings_ask 가 상한 항목 '{cmd}' 를 덮지 않는다")

    def test_role_agents_are_projected_in_verified_format_only(self):
        compile_all(self.root)
        from romeo import frontmatter as fm
        for rid in ("implementer", "reviewer"):
            p = self.root / ".claude/agents" / f"{rid}.md"
            self.assertTrue(p.is_file(), f"{p} 가 투영되지 않았다")
            meta, _body = fm.split(p.read_text(encoding="utf-8"))
            self.assertEqual(meta.get("name"), rid)
            self.assertIn("스스로 켜지지 않는다", meta.get("description", ""),
                          f"{p} 의 description 에 K-60 방어 문장이 없다")
            self.assertIn(f"core/roles/{rid}.yaml", p.read_text(encoding="utf-8"))
        # 검토자는 읽기·검색만 한다(core/roles/reviewer.yaml capabilities). 쓰기·실행 도구를 주면 계약과 어긋난다.
        reviewer = fm.split((self.root / ".claude/agents/reviewer.md").read_text(encoding="utf-8"))[0]
        self.assertEqual([t.strip() for t in reviewer["tools"].split(",")], ["Read", "Grep", "Glob"])
        # 형식을 확인하지 못한 런타임에는 파일을 만들지 않는다 — 읽히지 않는 산출물이 더 나쁘다.
        self.assertFalse((self.root / ".codex").exists(),
                         "확인되지 않은 형식의 에이전트 정의를 만들었다")

    def test_role_agent_without_description_is_refused(self):
        import yaml
        from romeo.compile import CompileError
        a = self.root / "adapters/claude/adapter.yaml"
        data = yaml.safe_load(a.read_text(encoding="utf-8"))
        data["role_agents"]["reviewer"].pop("description")
        a.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        with self.assertRaises(CompileError):
            compile_all(self.root)

    def test_check_detects_hand_edited_role_agent(self):
        compile_all(self.root)
        p = self.root / ".claude/agents/reviewer.md"
        p.write_text(p.read_text(encoding="utf-8").replace("Read, Grep, Glob", "Read, Write, Bash"),
                     encoding="utf-8")
        codes = sorted(f[0] for f in check_compiled(self.root))
        self.assertIn("COMPILE_STALE", codes, "역할 산출물을 손으로 고친 것을 잡지 못했다")

    def test_projected_new_skills_have_name_and_description(self):
        # description 이 비면 doctor 가 "라우터가 켤 근거가 없다" 로 계상하고 discovery 가 안 된다.
        from romeo import frontmatter as fm
        compile_all(self.root)
        for skills_dir in (".claude/skills", ".agents/skills"):
            for name in ("implement", "review"):
                p = self.root / skills_dir / name / "SKILL.md"
                meta, _body = fm.split(p.read_text(encoding="utf-8"))
                self.assertTrue(meta, f"{p} 에 frontmatter 가 없다")
                self.assertEqual(meta.get("name"), name, f"{p} 의 name 이 폴더명과 다르다")
                self.assertTrue((meta.get("description") or "").strip(),
                                f"{p} 에 description 이 없다")


class TestListOutputsCoversEverythingCompileWrites(unittest.TestCase):
    """`--list-outputs` 가 컴파일이 실제로 건드리는 집합을 전부 담는가 (AC-4).

    이름만 세는 검사가 아니다 — 컴파일 전후로 작업 트리를 실측해 **바뀐 경로 전부**가 목록 안에 있는지 본다.
    구현자가 이 목록을 보고 spec 의 「변경 범위」를 쓰기 때문에, 목록이 하나라도 빠뜨리면 그 다음 위임이
    쓰기 상한 밖을 건드리고 폐기된다(결함 ④ 가 바로 그것이었다). 계획 산출물만 인쇄하고 **제거 대상**
    (이전 컴파일에만 있던 경로)을 빠뜨리는 것도 같은 누락이다 — 삭제도 작업 트리를 바꾼다.

    집합은 두 가지다. **완료 뒤 남는 산출물**은 이름을 그대로 인쇄하고, **컴파일 중에만 존재하는 staging**
    은 `mkdtemp` 라 이름이 매번 달라 미리 인쇄할 수 없으므로 패턴 한 줄로 세운다(AC-4). 성공한 컴파일은
    staging 을 지우므로 전후 스냅샷으로는 관찰되지 않는다 — 그래서 그 줄은 실제로 만들어지는 디렉터리와
    대조한다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = make_tree(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def _mark_as_previous_output(self, rel):
        """이전 컴파일이 그 경로를 만들었던 것처럼 상태 파일을 고친다 — 다음 컴파일의 제거 대상이 된다."""
        previous = _previous_outputs(self.root) or set()
        (self.root / STATE_PATH).write_bytes(_state_bytes(previous | {rel}))

    def test_lists_the_paths_the_acceptance_criterion_names(self):
        compile_all(self.root)
        outputs, _pruned, _transient = list_outputs(self.root)
        self.assertIn(STATE_PATH, outputs, "컴파일 상태 파일이 목록에 없다")
        self.assertTrue([rel for rel in outputs if rel.startswith(".agents/")],
                        f".agents/ 산출물이 목록에 없다: {outputs}")
        self.assertIn(".agents/skills/plan/SKILL.md", outputs)
        self.assertIn(".claude/agents/implementer.md", outputs)
        self.assertTrue([rel for rel in outputs if rel.startswith(".claude/")], outputs)
        self.assertIn("CLAUDE.md", outputs)
        self.assertIn("AGENTS.md", outputs)

    def test_listing_does_not_write(self):
        compile_all(self.root)
        before = files_snapshot(self.root)
        list_outputs(self.root)
        self.assertEqual(before, files_snapshot(self.root), "--list-outputs 가 작업 트리를 바꿨다")

    def test_prints_the_staging_directory_as_one_pattern(self):
        """컴파일 중에만 있는 staging 을 패턴 한 줄로 세우고, 그 패턴이 실제 디렉터리를 덮는가 (AC-4).

        `_stage_compile` 은 저장소 루트에 `mkdtemp` 로 디렉터리를 만들고, 반영과 rollback 이 모두 실패하면
        그것을 **지우지 않고 남긴다**. 이름이 매번 다르므로 목록에 적을 수 있는 것은 패턴뿐이다 — 여기서
        확인하는 것은 그 패턴이 실제로 만들어지는 이름을 덮는가이지 문자열이 그럴듯한가가 아니다.
        패턴이 어긋나면 쓰기 상한이 그 자리를 비워 두고, 실패한 컴파일 뒤의 다음 위임이 거기서 막힌다."""
        compile_all(self.root)
        outputs, _pruned, transient = list_outputs(self.root)
        self.assertEqual(len(transient), 1, f"staging 은 패턴 한 줄이어야 한다: {transient}")
        self.assertIn("*", transient[0], f"패턴이 아니라 고정된 이름이 인쇄됐다: {transient[0]}")
        self.assertEqual(transient, [STAGE_GLOB])
        self.assertNotIn(transient[0], outputs,
                         "완료 뒤 남는 산출물과 컴파일 중에만 있는 경로가 같은 목록에 섞였다")

        plan = _prepare_compile(self.root, True)
        stage = _stage_compile(self.root, plan)
        try:
            rel = str(stage.relative_to(self.root))
            self.assertTrue(rel.startswith("."), f"staging 이 저장소 루트에 만들어지지 않았다: {rel}")
            touched = {rel} | {str(path.relative_to(self.root)) for path in stage.rglob("*")}
            self.assertGreater(len(touched), 1, "staging 이 비어 있다 — 검사가 성립하지 않는다")
            self.assertTrue(uncovered(touched, outputs),
                            "완료 뒤 남는 산출물 목록이 staging 을 이미 덮는다 — 패턴 줄이 검사되지 않는다")
            missing = uncovered(touched, list(outputs) + list(transient))
            self.assertFalse(missing, f"실제 staging 경로를 패턴이 덮지 못한다: {missing[:5]}")
        finally:
            shutil.rmtree(stage, ignore_errors=True)

    def test_covers_every_path_a_real_compile_changes(self):
        compile_all(self.root)
        stray = ".claude/skills/gone-in-a-previous-compile/SKILL.md"
        (self.root / stray).parent.mkdir(parents=True, exist_ok=True)
        (self.root / stray).write_text("이전 컴파일이 남긴 산출물\n", encoding="utf-8")
        self._mark_as_previous_output(stray)

        outputs, pruned, _transient = list_outputs(self.root)
        self.assertIn(stray, pruned, "이전 상태에만 있는 경로를 제거 대상으로 잡지 못했다")
        self.assertIn(stray, outputs, "제거 대상이 전체 목록에서 빠졌다")

        before = files_snapshot(self.root)
        compile_all(self.root)
        after = files_snapshot(self.root)
        touched = {rel for rel in set(before) | set(after) if before.get(rel) != after.get(rel)}

        self.assertIn(stray, touched,
                      "이 테스트가 제거를 재현하지 못했다 — 검사가 성립하지 않는다")
        missing = uncovered(touched, outputs)
        self.assertFalse(missing, f"컴파일이 바꿨는데 --list-outputs 가 인쇄하지 않은 경로: {missing}")

    def test_a_fresh_tree_compile_changes_nothing_outside_the_list(self):
        """상태 파일이 없는 최초 컴파일 — 산출물이 통째로 생기는 경우에도 목록이 그것을 전부 담는가."""
        outputs, pruned, _transient = list_outputs(self.root)
        self.assertEqual(pruned, [], "상태 파일이 없으면 제거 대상은 없다")
        before = files_snapshot(self.root)
        compile_all(self.root)
        after = files_snapshot(self.root)
        touched = {rel for rel in set(before) | set(after) if before.get(rel) != after.get(rel)}
        self.assertTrue(touched, "최초 컴파일이 아무것도 만들지 않았다 — 검사가 성립하지 않는다")
        missing = uncovered(touched, outputs)
        self.assertFalse(missing, f"컴파일이 만들었는데 --list-outputs 가 인쇄하지 않은 경로: {missing}")


if __name__ == "__main__":
    unittest.main()
