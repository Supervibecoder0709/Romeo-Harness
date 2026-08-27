import copy
import unittest

from romeo import HARNESS_ROOT
from romeo.fixtures import check_fixtures, load_fixtures, run_report
from romeo.policy import RouteError, route


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
