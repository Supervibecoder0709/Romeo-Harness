import copy
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock
from pathlib import Path

from romeo import HARNESS_ROOT
from romeo.cli import main
from romeo.fixtures import check_fixtures, load_fixtures, run_report
from romeo.policy import RouteError, load_project_state, route
from romeo.util import dump_yaml, load_yaml


def cls(**kw):
    base = {"unit": "T0", "mode": "delivery", "intent": "write", "facets": [], "gates": [], "blast_radius": "small", "uncertainty": "low"}
    base.update(kw)
    return base


class TestRoute(unittest.TestCase):
    def test_t0_quick_single_spec(self):
        out = route(cls(facets=["tooling"]))
        self.assertEqual(out["profile"], "quick")
        self.assertEqual(out["package"], ["spec"])
        self.assertEqual(out["reviewer"], "none")
        self.assertEqual(out["isolation"], "current")
        self.assertIn("capsule", out["sections"]["spec"])
        self.assertEqual(out["sections"]["spec"][-1], "evidence")
        self.assertEqual([p["id"] for p in out["parts"]], [])

    def test_gate_raises_t0_to_standard_with_risk_section(self):
        out = route(cls(facets=["copy", "legal"], gates=["legal"]))
        self.assertEqual(out["profile"], "standard")
        self.assertIn("risk-backup-recovery", out["sections"]["spec"])
        self.assertIn("risk-plan-ready", out["blocks"])
        self.assertEqual(out["reviewer"], "opposite-runtime-readonly")
        self.assertIn("overlay:gate.any", out["fired_rules"])

    def test_gate_hint_unchecked_warns(self):
        out = route(cls(facets=["payment"]))
        self.assertEqual(out["gate_hints"]["unchecked"], ["payment"])
        self.assertIn("GATE_HINT_UNCHECKED", [w["id"] for w in out["warnings"]])
        out2 = route(cls(intent="read", facets=["payment"]))
        self.assertEqual(out2["gate_hints"]["unchecked"], [])  # 읽기만 하면 결제 게이트 힌트 없음

    def test_privacy_hint_applies_even_on_read(self):
        out = route(cls(unit="none", intent="read", facets=["privacy"]))
        self.assertEqual(out["gate_hints"]["hinted"], ["privacy-security"])

    def test_t1_profiles(self):
        self.assertEqual(route(cls(unit="T1"))["profile"], "standard")
        self.assertEqual(route(cls(unit="T1", uncertainty="high", blast_radius="medium"))["profile"], "deep")
        self.assertEqual(route(cls(unit="T1", uncertainty="high", blast_radius="small"))["profile"], "standard")
        self.assertEqual(route(cls(unit="T1", blast_radius="large"))["profile"], "deep")
        out = route(cls(unit="T1"))
        self.assertEqual(out["package"], ["brief", "spec"])
        self.assertEqual(out["isolation"], "worktree")
        self.assertIn("superpowers", [p["id"] for p in out["parts"]])

    def test_t2_and_discovery(self):
        out = route(cls(unit="T2"))
        self.assertEqual(out["profile"], "deep")
        self.assertEqual(out["package"], ["charter", "brief", "spec"])
        self.assertIn("milestone-plan", out["blocks"])
        self.assertIn("bmad-cis", [p["id"] for p in out["parts"]])
        disc = route(cls(unit="T1", mode="discovery", uncertainty="high"))
        self.assertEqual(disc["profile"], "deep")
        self.assertIn("discovery-plan", disc["sections"]["brief"])
        self.assertIn("discovery-result", disc["blocks"])

    def test_ui_section_placement(self):
        t1 = route(cls(unit="T1", facets=["ui"]))
        self.assertIn("ui-state-table", t1["sections"]["brief"])
        t0 = route(cls(unit="T0", facets=["ui"]))
        self.assertIn("ui-state-table", t0["sections"]["spec"])  # brief 가 없으면 spec 으로 fallback

    def test_guards_from_intent(self):
        self.assertEqual([g["id"] for g in route(cls(intent="delete", facets=["docs"]))["guards"]], ["deletion"])
        ids = [g["id"] for g in route(cls(unit="T1", intent="deploy", facets=["deploy"]))["guards"]]
        self.assertIn("production-deploy", ids)
        self.assertEqual(route(cls(intent="read", unit="none", facets=["ops-data"]))["guards"], [])

    def test_non_code_out_of_scope(self):
        out = route(cls(project_kind="non-code", facets=["docs"]))
        self.assertTrue(out["out_of_scope"])
        self.assertEqual(out["package"], [])
        self.assertIsNone(out["profile"])
        self.assertIn("OUT_OF_SCOPE_NON_CODE", [w["id"] for w in out["warnings"]])

    def test_unit_none_no_docs(self):
        out = route(cls(unit="none", intent="read", facets=["data"]))
        self.assertIsNone(out["profile"])
        self.assertEqual(out["package"], [])
        self.assertEqual(out["blocks"], [])

    def test_unknown_facet_or_gate_rejected(self):
        with self.assertRaises(RouteError):
            route(cls(facets=["nope"]))
        with self.assertRaises(RouteError):
            route(cls(gates=["nope"]))

    def test_deterministic(self):
        a = cls(unit="T1", intent="deploy", facets=["ops-data", "migration"], gates=["migration"], blast_radius="large")
        self.assertEqual(route(copy.deepcopy(a)), route(copy.deepcopy(a)))


CLASSIFICATION_T1 = """unit: T1
mode: delivery
intent: write
facets: [tooling]
gates: []
blast_radius: small
uncertainty: low
"""


class TestProjectState(unittest.TestCase):
    """부착 상태(.harness/romeo.project.yaml)가 부품 레지스트리의 기본 status 를 덮는다.
    파일이 없으면 덮지 않는다 — 부착을 관찰하지 못한 것을 부착으로 세지 않는다(K-51)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        (self.root / ".harness").mkdir()
        self.path = self.root / ".harness" / "romeo.project.yaml"

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, text):
        self.path.write_text(text, encoding="utf-8")

    def test_attached_module_is_active_and_clears_warning(self):
        self._write("schema_version: 1\nmodules:\n  superpowers: active\n")
        state = load_project_state(self.root)
        self.assertEqual(state["modules"]["superpowers"], "active")
        out = route(cls(unit="T1"), project_state=state)
        self.assertEqual(out["parts"][0]["id"], "superpowers")
        self.assertEqual(out["parts"][0]["status"], "active")
        self.assertNotIn("PART_PENDING_GATE", [w["id"] for w in out["warnings"]])

    def test_missing_file_keeps_pending_gate(self):
        self.assertIsNone(load_project_state(self.root))
        out = route(cls(unit="T1"), project_state=load_project_state(self.root))
        self.assertEqual(out["parts"][0]["status"], "pending_gate")
        self.assertIn("PART_PENDING_GATE", [w["id"] for w in out["warnings"]])

    def test_pending_gate_value_does_not_activate(self):
        self._write("schema_version: 1\nmodules:\n  superpowers: pending_gate\n")
        out = route(cls(unit="T1"), project_state=load_project_state(self.root))
        self.assertEqual(out["parts"][0]["status"], "pending_gate")

    def test_unknown_status_value_is_rejected(self):
        self._write("schema_version: 1\nmodules:\n  superpowers: activ\n")
        with self.assertRaises(ValueError):
            load_project_state(self.root)

    def test_broken_yaml_is_rejected(self):
        self._write("modules: [\n")
        with self.assertRaises(ValueError):
            load_project_state(self.root)

    def test_this_repository_declares_superpowers_active(self):
        state = load_project_state(HARNESS_ROOT)
        self.assertIsNotNone(state)
        self.assertEqual(state["modules"]["superpowers"], "active")


class TestRouterWiring(unittest.TestCase):
    """CLI 가 부착 상태를 라우터까지 실제로 배선하는가(F01·F07: 호출자 0건이었다)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        self.cls_path = self.root / "cls.yaml"
        self.cls_path.write_text(CLASSIFICATION_T1, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _attach(self):
        (self.root / ".harness").mkdir(exist_ok=True)
        (self.root / ".harness" / "romeo.project.yaml").write_text(
            "schema_version: 1\nmodules:\n  superpowers: active\n", encoding="utf-8")

    def _route_json(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["route", "--classification", str(self.cls_path), "--json", "--root", str(self.root)])
        self.assertEqual(rc, 0)
        return json.loads(buf.getvalue())

    def test_route_command_reads_attachment(self):
        out = self._route_json()
        self.assertEqual(out["parts"][0]["status"], "pending_gate")
        self._attach()
        out = self._route_json()
        self.assertEqual(out["parts"][0]["status"], "active")
        self.assertEqual([w["id"] for w in out["warnings"]], [])

    def test_new_command_records_attached_routing(self):
        self._attach()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["new", "--classification", str(self.cls_path), "--title", "부착 배선",
                       "--slug", "wiring", "--root", str(self.root), "--json"])
        self.assertEqual(rc, 0)
        res = json.loads(buf.getvalue())
        spec = Path([f for f in res["files"] if f.endswith("spec.md")][0])
        from romeo import frontmatter
        fm, _ = frontmatter.read(spec)
        self.assertNotIn("warn:PART_PENDING_GATE", fm["routing"]["fired_rules"])


class TestFixtures(unittest.TestCase):
    def test_bundled_fixtures_pass_threshold(self):
        fx = load_fixtures(HARNESS_ROOT / "fixtures/requests")
        self.assertGreaterEqual(len(fx), 15)
        self.assertEqual(check_fixtures(fx), {})
        rep = run_report(fx)
        # 90% 는 M0 진입 기준이었다 — 번들 fixture 는 전부 맞아야 한다(Q-37). 하나라도 어긋나면 그것이 결함이다.
        self.assertEqual(rep["matched"], rep["total"], [r for r in rep["rows"] if not r["ok"]])
        self.assertEqual(rep["gate_misses"], 0)


class TestFixtureReportExit(unittest.TestCase):
    """`route --fixtures <dir> --report` 는 **불일치 1건이면 exit 1** 이다 (Q-37).

    종전에는 일치율 90% 이상이면 exit 0 이라 30/33 이 맞아도 초록불이었다 — required_checks 와 CI 양쪽에서
    무엇을 확인하는지 적혀 있는 채로 아무것도 확인하지 않는 빈 검사였다(AGENTS.core §11). 90% 는 M0 진입 기준이었고
    지금 33/33 이 맞으므로, 기준을 「전부」 로 조여 fixture 가 하나라도 틀리면 로컬 명령도 CI 도 빨간불이 되게 한다."""

    SRC = HARNESS_ROOT / "fixtures/requests"
    #: 대안 일치(acceptable_alternatives)가 없는 fixture — 기대 profile 만 바꾸면 반드시 불일치가 된다
    TARGET = "fx-ab-tracking-plan-dashboard.yaml"
    #: 정책표의 profile 값(classification.yaml). 기대값이 아닌 **유효한** 값으로 바꿔야 스키마 검사가 아니라 대조가 판정한다
    PROFILES = ("quick", "standard", "deep")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _route(self, directory):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["route", "--fixtures", str(directory), "--report"])
        return rc, out.getvalue() + err.getvalue()

    def _copy_with_one_wrong_profile(self):
        dst = self.root / "requests"
        shutil.copytree(self.SRC, dst)
        target = dst / self.TARGET
        data = load_yaml(target)
        self.assertFalse(data.get("acceptable_alternatives"), "대안 일치가 있는 fixture 는 반례로 쓸 수 없다")
        wrong = next(p for p in self.PROFILES if p != data["expected"]["profile"])
        data["expected"]["profile"] = wrong
        target.write_text(dump_yaml(data), encoding="utf-8")
        return dst

    # ── ① 33건 중 1건만 틀려도(97% 일치) exit 1 ─────────────────────────────
    def test_one_mismatch_out_of_the_bundle_exits_one(self):
        directory = self._copy_with_one_wrong_profile()
        total = len(list(directory.glob("*.yaml")))
        rc, text = self._route(directory)
        self.assertEqual(rc, 1, text)
        self.assertIn(f"{total - 1}/{total} 일치", text)
        self.assertNotIn("FIXTURE_INVALID", text, "스키마가 아니라 대조가 판정해야 한다")

    # ── ② 원본 그대로는 exit 0 ───────────────────────────────────────────────
    def test_the_bundle_itself_exits_zero(self):
        rc, text = self._route(self.SRC)
        self.assertEqual(rc, 0, text)

    def test_an_empty_fixture_directory_is_not_a_pass(self):
        """0/0 은 전부 맞은 것이 아니다 — 아무것도 확인하지 않은 실행을 통과로 접지 않는다(K-51)."""
        empty = self.root / "empty"
        empty.mkdir()
        rc, _text = self._route(empty)
        self.assertEqual(rc, 1)

    # ── ④ 일치가 33/33 이어도 gate 누락 의심 1건이면 exit 1 ──────────────────
    def test_one_gate_miss_exits_one(self):
        """`run_report` 를 패치해 matched == total · gate_misses == 1 인 리포트를 돌려준다 — 번들 fixture 로는 그 상태를
        만들 수 없다(gate 누락 의심은 fixture 의 기대가 아니라 라우터 출력에서 나온다). 종료 코드가 `matched` 만 보면 여기서 0 이 난다."""
        from romeo import fixtures as fixtures_module
        real = fixtures_module.run_report

        def one_gate_miss(fx, policy=None):
            rep = real(fx, policy)
            self.assertEqual(rep["matched"], rep["total"], "전제 — 번들은 전부 일치한다")
            rep["gate_misses"] = 1
            return rep

        with mock.patch.object(fixtures_module, "run_report", one_gate_miss):
            rc, text = self._route(self.SRC)
        self.assertEqual(rc, 1, text)
        self.assertIn("gate 누락 의심 1", text)

    # ── ⑤ 같은 리포트를 내는 두 명령은 같은 판정을 낸다 ─────────────────────
    def _fixtures_report(self, directory):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            # `fixtures` 의 디렉터리는 위치 인자 `dir` 다(cli.py 실측) — `route` 의 `--fixtures <dir>` 와 같은 자리
            rc = main(["fixtures", "report", str(directory)])
        return rc, out.getvalue() + err.getvalue()

    def test_fixtures_report_agrees_with_route_report(self):
        matching, mismatching = self.SRC, self._copy_with_one_wrong_profile()
        for directory, expected in ((matching, 0), (mismatching, 1)):
            rc_route, text_route = self._route(directory)
            rc_fixtures, text_fixtures = self._fixtures_report(directory)
            self.assertEqual(rc_route, expected, text_route)
            self.assertEqual(rc_fixtures, rc_route, f"{directory}: fixtures report {rc_fixtures} vs route --report {rc_route}\n{text_fixtures}")

    # ── ③ CI 스텝은 명령을 바꾸지 않고 그 판정을 그대로 받는다 ──────────────
    def test_ci_step_takes_the_verdict_as_is(self):
        text = (HARNESS_ROOT / ".github/workflows/harness.yml").read_text(encoding="utf-8")
        lines = text.split("\n")
        run_lines = [i for i, l in enumerate(lines)
                     if l.rstrip().endswith("bin/romeo route --fixtures fixtures/requests --report")]
        self.assertEqual(len(run_lines), 1, run_lines)
        run_line = lines[run_lines[0]]
        self.assertIn("run:", run_line)
        self.assertNotIn("|| true", run_line)
        name_line = lines[run_lines[0] - 1]
        self.assertIn("- name:", name_line)
        self.assertIn("불일치 1건이면 실패", name_line, name_line)
        self.assertIn("Q-37", name_line)
        # 스텝 블록(`- name:` 부터 다음 `- name:` 전)에 판정을 삼키는 것이 없다 — `|| true` 도 `continue-on-error` 도
        start = run_lines[0] - 1
        end = next(i for i in range(start + 1, len(lines)) if lines[i].lstrip().startswith("- name:"))
        step = "\n".join(lines[start:end])
        self.assertNotIn("|| true", step, step)
        self.assertNotIn("continue-on-error", step, step)
        # job 수준에도 없다 — 스텝 밖의 `continue-on-error` 는 job 전체의 판정을 삼킨다. 파일 어디에도 두지 않는다(check-3 과 같은 조건)
        self.assertNotIn("continue-on-error", text)


if __name__ == "__main__":
    unittest.main()


class TestBlastSmallDropsReviewer(unittest.TestCase):
    """영향 반경이 작고 게이트가 없는 T1 은 검토자 없이 돈다 — 그리고 그 조건을 하나라도 벗어나면 돌지 않는다.

    이 클래스의 반례는 빈 값이 아니라 **그럴듯한 거짓 값**이다(AGENTS.core §11). 오버레이의
    `when` 에서 `gates: none` 을 빠뜨린 구현은 형태가 그럴듯하지만, optional_overlay 가
    hard_gate 보다 뒤에 평가되므로 gate.any 가 켠 검토자를 덮어써서 꺼 버린다.
    test_gate_keeps_reviewer 가 정확히 그 구현에서 실패한다.
    """

    def _reviewer(self, **kw):
        base = {"unit": "T1", "mode": "delivery", "intent": "write", "facets": ["tooling", "docs"],
                "gates": [], "blast_radius": "small", "uncertainty": "low"}
        base.update(kw)
        return route(base)

    def test_small_no_gate_drops_reviewer(self):
        out = self._reviewer()
        self.assertEqual(out["reviewer"], "none")
        self.assertIn("overlay:blast.small.no-reviewer", out["fired_rules"])
        # 격리는 내리지 않는다 — 이 단위가 바꾸지 않기로 한 것이다.
        self.assertEqual(out["isolation"], "worktree")

    def test_gate_keeps_reviewer(self):
        out = self._reviewer(facets=["tooling", "security"], gates=["privacy-security"])
        self.assertEqual(out["reviewer"], "opposite-runtime-readonly")
        self.assertNotIn("overlay:blast.small.no-reviewer", out["fired_rules"])

    def test_medium_and_large_keep_reviewer(self):
        for radius in ("medium", "large"):
            with self.subTest(radius=radius):
                self.assertEqual(self._reviewer(blast_radius=radius)["reviewer"],
                                 "opposite-runtime-readonly")

    def test_t2_keeps_reviewer(self):
        self.assertEqual(self._reviewer(unit="T2")["reviewer"], "opposite-runtime-readonly")

    def test_discovery_and_experiment_keep_reviewer(self):
        for mode in ("discovery", "experiment"):
            with self.subTest(mode=mode):
                self.assertEqual(self._reviewer(mode=mode)["reviewer"], "opposite-runtime-readonly")

    def test_read_intent_keeps_reviewer(self):
        self.assertEqual(self._reviewer(intent="mixed")["reviewer"], "opposite-runtime-readonly")

    def test_uncertain_method_keeps_reviewer(self):
        """방법이 일부 미정이면 검토자가 볼 것이 남아 있다.

        이 조건 없이 오버레이를 넣었을 때, 실제 세션 로그에서 온 fixture
        fx-coupang-rocket-badge-automation-plan(브라우저 자동화·외부 연동·불확실성 medium)이
        검토자를 잃었다. fixture 대조(bin/romeo route --fixtures)가 그것을 exit 1 로 잡았다.
        """
        for unc in ("medium", "high"):
            with self.subTest(uncertainty=unc):
                out = self._reviewer(uncertainty=unc)
                self.assertEqual(out["reviewer"], "opposite-runtime-readonly")
                self.assertNotIn("overlay:blast.small.no-reviewer", out["fired_rules"])

    def test_browser_automation_fixture_shape_keeps_reviewer(self):
        out = self._reviewer(facets=["browser-automation", "integration", "data"], uncertainty="medium")
        self.assertEqual(out["reviewer"], "opposite-runtime-readonly")
        self.assertIn("capability-check", out["sections"]["spec"])
