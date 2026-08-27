"""부착 검증(K-68) — 충돌 fixture 가 실제로 위반을 잡는지.

fixture 는 데이터라서 "통과한다" 만으로는 아무것도 증명하지 못한다.
각 fixture 마다 **일부러 위반 상태를 만들어** 잡히는지 본다.
"""
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from romeo.compile import compile_all
from romeo.doctor import (check_conflicts, doctor, doctor_problem_count, format_report,
                          probe_runtimes, probe_skill_files)
from romeo.util import project_root

REPO = project_root(Path(__file__).parent)
INPUTS = ["core", "adapters", "vendor", "provenance", "skills", "fixtures"]


def make_tree(dst: Path):
    for name in INPUTS:
        shutil.copytree(REPO / name, dst / name)
    (dst / ".harness").mkdir(exist_ok=True)
    shutil.copy(REPO / ".harness/bindings.yaml", dst / ".harness/bindings.yaml")
    compile_all(dst)
    return dst


def codes(findings):
    return sorted(f[0] for f in findings)


class TestRepoItself(unittest.TestCase):
    def test_repository_scope_passes_on_this_repo(self):
        # 저장소 내용 문제만 본다. 런타임 설치 여부는 머신마다 다르므로 여기 섞으면 CI 에서 무조건 깨진다.
        rep = doctor(REPO)
        self.assertEqual(doctor_problem_count(rep, scope="repository"), 0, format_report(rep))

    def test_missing_runtime_is_environment_not_repository(self):
        rep = doctor(REPO)
        rep["runtimes"] = [{"name": "codex", "ok": False, "detail": "PATH 에 없다", "why": "x"}]
        self.assertEqual(doctor_problem_count(rep, scope="repository"), 0,
                         "런타임 부재가 저장소 문제로 세어지면 CI 가 항상 실패한다")
        self.assertEqual(doctor_problem_count(rep, scope="environment"), 1)
        self.assertEqual(doctor_problem_count(rep), 1, "기본 scope 는 둘을 합친다")

    def test_three_conflict_fixtures_run(self):
        _findings, ran = check_conflicts(REPO)
        self.assertEqual(ran, 3, "K-68 은 충돌 fixture 3종을 요구한다")

    def test_report_says_runtime_load_is_unproven(self):
        # 파일이 있다는 것과 런타임이 로드한다는 것은 다르다. 보고서가 그걸 숨기면 안 된다.
        rep = doctor(REPO)
        rep["observed_load"] = {}
        self.assertIn("미관찰", format_report(rep))


class TestProbes(unittest.TestCase):
    def test_runtime_probe_shape(self):
        for r in probe_runtimes():
            self.assertIn("name", r)
            self.assertIn("ok", r)

    def test_skill_probe_counts_both_runtimes(self):
        probes = {p["runtime"]: p for p in probe_skill_files(REPO)}
        self.assertIn("claude", probes)
        self.assertIn("codex", probes)
        # 채택 7종 + plan + plan-close
        self.assertGreaterEqual(probes["claude"]["count"], 9)
        self.assertIn("test-driven-development", probes["claude"]["skills"])


class TestConflictFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = make_tree(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_tree_has_no_conflicts(self):
        findings, ran = check_conflicts(self.root)
        self.assertEqual(findings, [], f"깨끗한 트리인데 충돌: {findings}")
        self.assertEqual(ran, 3)

    # ── c1: 외부 계획 경로 ─────────────────────────────────────────────
    def test_c1_flags_external_path_without_override(self):
        import yaml
        b = self.root / ".harness/bindings.yaml"
        data = yaml.safe_load(b.read_text(encoding="utf-8"))
        del data["overrides"]["output_paths"]          # 흡수 규칙을 없애면
        b.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        findings, _ = check_conflicts(self.root)
        self.assertTrue(any(f[0] == "c1-external-plan-path" for f in findings),
                        "부품이 가리키는 외부 경로에 흡수 규칙이 없는데 통과했다")

    def test_c1_flags_newly_introduced_external_path(self):
        # 나중에 다른 부품을 채택했을 때도 잡아야 한다
        p = self.root / ".claude/skills/plan/SKILL.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n산출물은 _bmad-output/ 에 둔다.\n", encoding="utf-8")
        import yaml
        b = self.root / ".harness/bindings.yaml"
        data = yaml.safe_load(b.read_text(encoding="utf-8"))
        del data["overrides"]["output_paths"]
        b.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        findings, _ = check_conflicts(self.root)
        self.assertTrue(any("plan/SKILL.md" in f[1] for f in findings))

    # ── c2: 자동 트리거 ────────────────────────────────────────────────
    def test_c2_flags_repo_hook_file(self):
        (self.root / ".claude").mkdir(exist_ok=True)
        (self.root / ".claude/hooks.json").write_text("{}", encoding="utf-8")
        findings, _ = check_conflicts(self.root)
        self.assertTrue(any(f[0] == "c2-no-auto-trigger" and "hooks.json" in f[1] for f in findings))

    def test_c2_flags_hooks_key_in_settings(self):
        p = self.root / ".claude/settings.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        data["hooks"] = {"SessionStart": []}
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        findings, _ = check_conflicts(self.root)
        self.assertTrue(any("settings.json" in f[1] for f in findings))

    def test_c2_flags_always_on_phrase(self):
        # 제외한 using-superpowers 의 "1% 규칙" 이 어떤 경로로든 돌아오면 잡아야 한다
        d = self.root / ".claude/skills/sneaky"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            "---\nname: sneaky\ndescription: x\n---\n\nUse at the start of every conversation.\n",
            encoding="utf-8")
        findings, _ = check_conflicts(self.root)
        self.assertTrue(any(f[0] == "c2-no-auto-trigger" and "sneaky" in f[1] for f in findings))

    # ── c3: 이름·마커 충돌 ─────────────────────────────────────────────
    def test_c3_flags_duplicate_skill_name(self):
        d = self.root / ".claude/skills/tdd-copy"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            "---\nname: test-driven-development\ndescription: 사본\n---\n\n본문\n", encoding="utf-8")
        findings, _ = check_conflicts(self.root)
        self.assertTrue(any(f[0] == "c3-name-and-marker" and "test-driven-development" in f[1]
                            for f in findings))

    def test_c3_flags_foreign_marker_owner(self):
        p = self.root / "CLAUDE.md"
        p.write_text(p.read_text(encoding="utf-8")
                     + "\n<!-- openwiki:managed start -->\n남의 블록\n<!-- openwiki:managed end -->\n",
                     encoding="utf-8")
        findings, _ = check_conflicts(self.root)
        self.assertTrue(any("openwiki" in f[2] for f in findings))

    def test_c3_flags_second_romeo_block(self):
        p = self.root / "CLAUDE.md"
        p.write_text(p.read_text(encoding="utf-8")
                     + "\n<!-- romeo:managed start v0.1.0 source=x sha=1 -->\n둘째\n"
                       "<!-- romeo:managed end -->\n", encoding="utf-8")
        findings, _ = check_conflicts(self.root)
        self.assertTrue(any("둘 이상" in f[2] for f in findings))

    # ── 프로브 ────────────────────────────────────────────────────────
    def test_skill_without_description_is_flagged(self):
        d = self.root / ".claude/skills/nodesc"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\nname: nodesc\n---\n\n본문\n", encoding="utf-8")
        probes = {p["runtime"]: p for p in probe_skill_files(self.root)}
        self.assertTrue(any("description" in p for p in probes["claude"]["problems"]))

    def test_symlinked_skill_is_flagged(self):
        d = self.root / ".claude/skills/linked"
        d.mkdir(parents=True)
        (d / "SKILL.md").symlink_to(self.root / ".claude/skills/plan/SKILL.md")
        probes = {p["runtime"]: p for p in probe_skill_files(self.root)}
        self.assertTrue(any("심링크" in p for p in probes["claude"]["problems"]))


if __name__ == "__main__":
    unittest.main()
