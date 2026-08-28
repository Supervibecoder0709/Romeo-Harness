import copy
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from romeo import HARNESS_ROOT
from romeo.cli import main
from romeo.fixtures import check_fixtures, load_fixtures, run_report
from romeo.policy import RouteError, load_project_state, route


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
        self.assertIn("approval-gate", out["blocks"])
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
        self.assertGreaterEqual(rep["match_rate"], 0.9)
        self.assertEqual(rep["gate_misses"], 0)


if __name__ == "__main__":
    unittest.main()
