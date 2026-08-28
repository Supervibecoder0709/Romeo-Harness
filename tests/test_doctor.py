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
                          observations, probe_runtimes, probe_skill_files, runtime_load_mark)
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

    def test_conflict_fixtures_run(self):
        _findings, ran = check_conflicts(REPO)
        # K-68 이 요구하는 3종이 최소치다. 리뷰가 찾아낸 종류를 추가하면 늘어난다.
        self.assertGreaterEqual(ran, 3, "K-68 은 충돌 fixture 3종 이상을 요구한다")

    def test_report_says_runtime_load_is_unproven(self):
        # 파일이 있다는 것과 런타임이 로드한다는 것은 다르다. 보고서가 그걸 숨기면 안 된다.
        rep = doctor(REPO)
        rep["observed_load"] = {}
        text = format_report(rep)
        self.assertIn("미관찰", text)
        self.assertNotIn("관찰됨", text, "관찰 기록이 없는데 관찰됐다고 인쇄한다")


class TestRuntimeLoadHonesty(unittest.TestCase):
    """'관찰됨' 은 관찰 기록이 지금의 스킬 목록을 **이름으로** 다 덮고, 그 기록이 **실재하는 증거**를
    가리킬 때만 쓴다(K-51).

    기록의 존재만 보고 '관찰됨' 을 인쇄하면, 10개를 관찰한 기록으로 12개의 로드를 주장하게 된다.
    이름 목록만 보는 것으로도 부족하다 — 손으로 이름 두 개를 더하면 '관찰됨' 이 된다.
    정직한 문장을 관찰 텍스트 안에 적어 두는 것으로는 부족하다: 한 줄 요약만 읽는 사람에게는
    헤더의 판정 토큰이 전부다.
    """

    def probe(self, names):
        return {"runtime": "codex", "dir": ".agents/skills", "count": len(names),
                "problems": [], "skills": sorted(names)}

    def entry(self, names, **over):
        """실재하는 증거를 가리키는 관찰 기록. `evidence_exists` 는 observations() 가 계산해 넣는다."""
        rec = {"observed_at": "2026-08-28", "skills": names,
               "evidence": "docs/reviews/2026-08-28-codex-m2-review/SKILLS_SEEN.md",
               "evidence_exists": True}
        rec.update(over)
        return rec

    def test_full_name_match_with_real_evidence_is_observed(self):
        probe = self.probe(["plan", "implement"])
        mark, _ = runtime_load_mark(probe, self.entry(["implement", "plan"]))
        self.assertIn("관찰됨", mark)
        self.assertIn("2/2", mark)

    def test_record_without_evidence_cannot_claim_observation(self):
        """이름 목록은 손으로 쓴 자기 신고다. 증거를 지목하지 않으면 '관찰됨' 을 쓰지 않는다(A-11)."""
        probe = self.probe(["plan", "implement"])
        mark, _ = runtime_load_mark(probe, {"observed_at": "2026-08-28", "skills": ["implement", "plan"]})
        self.assertNotIn("관찰됨", mark)
        self.assertIn("대조 불가", mark)
        self.assertIn("evidence", mark)

    def test_record_whose_evidence_does_not_exist_cannot_claim_observation(self):
        probe = self.probe(["plan", "implement"])
        entry = self.entry(["implement", "plan"], evidence="docs/reviews/NEVER-EXISTED/PROOF.md",
                           evidence_exists=False)
        mark, note = runtime_load_mark(probe, entry)
        self.assertNotIn("관찰됨", mark)
        self.assertIn("실재하지 않는다", mark)
        self.assertIn("실재하지 않는다", note, "없는 경로를 그대로 인쇄하면 증거처럼 읽힌다")

    def test_observations_checks_that_the_evidence_pointer_is_real(self):
        """실재 검사는 파일을 읽는 쪽(observations)이 한다 — 기록이 스스로 참이라고 말할 수 없다."""
        with tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP")) as tmp:
            root = Path(tmp)
            (root / ".harness").mkdir()
            (root / "docs").mkdir()
            (root / "docs/PROOF.md").write_text("본 것", encoding="utf-8")
            (root / ".harness/observations.yaml").write_text(
                "runtime_load:\n"
                "  claude:\n    skills: [plan]\n    evidence: docs/PROOF.md\n"
                "  codex:\n    skills: [plan]\n    evidence: docs/없는것.md\n"
                "  orca:\n    skills: [plan]\n    evidence: /etc/hosts\n",
                encoding="utf-8")
            obs = observations(root)
            self.assertTrue(obs["claude"]["evidence_exists"])
            self.assertFalse(obs["codex"]["evidence_exists"])
            self.assertFalse(obs["orca"]["evidence_exists"], "저장소 밖은 이 저장소의 관찰 기록이 아니다")

    def test_missing_name_is_partial_not_observed(self):
        probe = self.probe(["plan", "implement", "review"])
        mark, _ = runtime_load_mark(probe, {"observed_at": "2026-08-28", "skills": ["plan"]})
        self.assertNotIn("관찰됨", mark, "관찰하지 않은 스킬이 있는데 '관찰됨' 이라고 인쇄한다")
        self.assertIn("부분 관찰", mark)
        self.assertIn("implement", mark)
        self.assertIn("review", mark)

    def test_same_count_but_different_names_is_partial(self):
        # 개수만 대조하면 통과한다. 이름을 대조해야 잡힌다.
        probe = self.probe(["plan", "implement"])
        mark, _ = runtime_load_mark(probe, {"observed_at": "2026-08-28", "skills": ["plan", "repo-archive"]})
        self.assertNotIn("관찰됨", mark)
        self.assertIn("implement", mark)
        self.assertIn("repo-archive", mark, "기록에만 있는 이름도 보여야 한다")

    def test_free_text_record_cannot_be_compared(self):
        # 구조 이전의 자유 문자열 기록. 텍스트가 있다는 것은 관찰의 증거가 아니다.
        mark, note = runtime_load_mark(self.probe(["plan"]), "12개를 다 봤다")
        self.assertNotIn("관찰됨", mark)
        self.assertIn("대조 불가", mark)
        self.assertIn("12개를 다 봤다", note)

    def test_report_is_json_serializable(self):
        # 관찰 기록은 사람이 손으로 쓰는 YAML 이다. 따옴표 없는 날짜가 date 객체가 되어
        # `romeo doctor --json` 을 죽인 적이 있다 — 읽는 쪽에서 막는다.
        json.dumps(doctor(REPO), ensure_ascii=False)

    def test_repo_observations_do_not_claim_the_new_workflows_on_codex(self):
        # 이 저장소의 사실: codex 쪽 관찰은 10개 시점이고 implement · review 는 미관찰이다.
        # 두 스킬이 실제로 codex 세션 목록에서 관찰되어 .harness/observations.yaml 에 등록되면
        # 이 테스트가 깨진다 — 그때 기대를 '관찰됨' 으로 바꾼다.
        rep = doctor(REPO)
        probe = {p["runtime"]: p for p in rep["skills"]}["codex"]
        mark, _ = runtime_load_mark(probe, (rep["observed_load"] or {}).get("codex"))
        self.assertNotIn("관찰됨", mark, "codex 관찰 기록이 새 스킬 2종까지 덮는다고 주장한다")
        for name in ("implement", "review"):
            self.assertIn(name, mark)
        codex_line = [ln for ln in format_report(rep).splitlines() if ln.strip().startswith("codex")]
        self.assertTrue(codex_line)
        self.assertNotIn("관찰됨", codex_line[0])


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

    def test_new_workflows_have_loadable_frontmatter_in_both_skill_dirs(self):
        # 이 테스트는 **디스크의 파일만** 읽는다. 파일이 투영됐다는 것과 런타임이 실제로 로드한다는
        # 것은 다르다 — 'discovery' 라는 단어는 .harness/observations.yaml 이 소유한다.
        # probe 는 frontmatter 를 읽으므로, 여기 이름이 뜨면 name·description 이 살아 있다는 뜻이다.
        probes = {p["runtime"]: p for p in probe_skill_files(REPO)}
        for runtime in ("claude", "codex"):
            for name in ("implement", "review"):
                self.assertIn(name, probes[runtime]["skills"],
                              f"{runtime} 스킬 디렉터리의 {name} 에 로드 가능한 frontmatter 가 없다")
            self.assertEqual(probes[runtime]["problems"], [],
                             f"{runtime} 스킬 파일에 문제가 있다: {probes[runtime]['problems']}")


class TestConflictFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = make_tree(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_tree_has_no_conflicts(self):
        findings, ran = check_conflicts(self.root)
        self.assertEqual(findings, [], f"깨끗한 트리인데 충돌: {findings}")
        self.assertGreaterEqual(ran, 3)

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

    # ── c4: 위험 명령 지시 ─────────────────────────────────────────────
    def test_c4_flags_dangerous_instruction_without_override(self):
        # Codex 독립 리뷰가 c1 을 통과한 충돌 3건을 찾아냈다. 그 종류를 자동으로 잡는지 본다.
        import yaml
        b = self.root / ".harness/bindings.yaml"
        data = yaml.safe_load(b.read_text(encoding="utf-8"))
        del data["overrides"]["external_writes"]
        b.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        findings, _ = check_conflicts(self.root)
        c4 = [f for f in findings if f[0] == "c4-dangerous-instruction"]
        self.assertTrue(c4, "gh api 지시에 대응 override 가 없는데 통과했다")
        self.assertTrue(all("external_writes" in f[2] for f in c4),
                        "패턴마다 맞는 override 를 요구해야 한다 — 아무거나 하나면 통과시키면 안 된다")

    def test_c4_other_overrides_do_not_cover_each_other(self):
        import yaml
        b = self.root / ".harness/bindings.yaml"
        data = yaml.safe_load(b.read_text(encoding="utf-8"))
        del data["overrides"]["destructive_tdd"]
        b.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        findings, _ = check_conflicts(self.root)
        c4 = [f for f in findings if f[0] == "c4-dangerous-instruction"]
        self.assertTrue(any("destructive_tdd" in f[2] for f in c4))
        self.assertFalse(any("external_writes" in f[2] for f in c4),
                         "남아 있는 override 까지 없다고 보고했다")

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
