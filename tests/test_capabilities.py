"""능력 프로브(`core/policy/capabilities.yaml` + `romeo doctor`)와 라우터 추천(G-M3 부착).

이 단위가 지키려는 것은 하나다: **"설치돼 있다" 를 "동작한다" 로 승격하지 않는다.**
그래서 라벨은 present·absent 둘뿐이고, absent 는 결함이 아니다 — 없는 도구를 있는 것처럼
추천하지 않기 위해 인쇄만 한다(K-51).
"""
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from romeo.card import render_card
from romeo.doctor import (CAPABILITIES_PATH, doctor, doctor_problem_count, format_report,
                          load_capabilities, probe_capabilities)
from romeo.policy import load_policy, route
from romeo.util import load_any, project_root

REPO = project_root(Path(__file__).parent)
# 실행을 뜻하는 라벨. 프로브가 이 중 하나를 낼 수 있으면 그것은 설치 흔적이 아니라 실행 주장이다.
RUNTIME_WORDS = {"loaded", "running", "works", "working", "active", "executed", "verified"}


def _fake_manifest(root, modules=("core", "bmm"), platforms=("claude-code",)):
    p = Path(root) / "_bmad/_config/manifest.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump({"modules": list(modules), "platform_codes": list(platforms)},
                                allow_unicode=True), encoding="utf-8")
    return p


class TestCapabilityPolicy(unittest.TestCase):
    def test_policy_file_declares_the_bmad_probe(self):
        cap = load_capabilities(REPO)["discovery"]["bmad"]
        self.assertEqual(cap["kind"], "install_trace")
        self.assertEqual(cap["marker"], "_bmad/_config/manifest.yaml")
        self.assertEqual(sorted(cap["result_labels"]), ["absent", "present"])
        self.assertEqual(list(cap["reads"]), ["modules", "platform_codes"])
        self.assertTrue(str(cap.get("honesty") or "").strip(), "정직성 문장이 비어 있다")

    def test_no_result_label_means_execution(self):
        # AC-1. 라벨이 실행을 뜻하면 프로브 결과가 곧 '동작한다' 로 읽힌다.
        for group in load_capabilities(REPO).values():
            for cid, cap in group.items():
                for label in cap["result_labels"]:
                    self.assertNotIn(label.lower(), RUNTIME_WORDS,
                                     f"{cid}: 라벨 {label!r} 이 실행을 뜻한다")

    def test_policy_file_is_loadable_yaml_with_version(self):
        data = load_any(REPO / CAPABILITIES_PATH)
        self.assertIn("policy_version", data)
        self.assertIn("capabilities", data)


class TestProbe(unittest.TestCase):
    def test_absent_when_no_marker(self):
        # 판정 근거는 **marker 의 부재**이지 이 저장소의 설치 상태가 아니다.
        # 실제 저장소를 보게 하면 누가 BMAD 를 설치하는 순간 깨진다 — 그리고 그 설치는
        # 이 하네스의 로드맵이 하려던 일이었다(2026-08-31 run_67c238a254e1 실측).
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "core/policy").mkdir(parents=True)
            shutil.copy(REPO / CAPABILITIES_PATH, Path(tmp) / CAPABILITIES_PATH)
            probes = {p["id"]: p for p in probe_capabilities(tmp)}
        self.assertIn("discovery.bmad", probes)
        self.assertEqual(probes["discovery.bmad"]["label"], "absent")
        self.assertIn("설치 흔적 없음", probes["discovery.bmad"]["detail"])

    def test_present_reads_modules_and_platform_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "core/policy").mkdir(parents=True)
            shutil.copy(REPO / CAPABILITIES_PATH, Path(tmp) / CAPABILITIES_PATH)
            _fake_manifest(tmp, modules=["core", "cis"], platforms=["codex"])
            p = {x["id"]: x for x in probe_capabilities(tmp)}["discovery.bmad"]
        self.assertEqual(p["label"], "present")
        self.assertEqual(p["reads"]["modules"], ["core", "cis"])
        self.assertEqual(p["reads"]["platform_codes"], ["codex"])

    def test_present_does_not_invent_unrecorded_fields(self):
        # marker 는 있는데 modules 를 기록하지 않은 설치본. 없는 것을 있는 것처럼 채우지 않는다.
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "core/policy").mkdir(parents=True)
            shutil.copy(REPO / CAPABILITIES_PATH, Path(tmp) / CAPABILITIES_PATH)
            m = Path(tmp) / "_bmad/_config/manifest.yaml"
            m.parent.mkdir(parents=True)
            m.write_text("version: 6.0.0\n", encoding="utf-8")
            p = {x["id"]: x for x in probe_capabilities(tmp)}["discovery.bmad"]
        self.assertEqual(p["label"], "present")
        self.assertIsNone(p["reads"]["modules"])
        self.assertIsNone(p["reads"]["platform_codes"])

    def test_unreadable_marker_is_still_present_but_says_so(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "core/policy").mkdir(parents=True)
            shutil.copy(REPO / CAPABILITIES_PATH, Path(tmp) / CAPABILITIES_PATH)
            m = Path(tmp) / "_bmad/_config/manifest.yaml"
            m.parent.mkdir(parents=True)
            m.write_text("modules: [a\n  - broken", encoding="utf-8")
            p = {x["id"]: x for x in probe_capabilities(tmp)}["discovery.bmad"]
        self.assertEqual(p["label"], "present")
        self.assertIn("읽을 수 없다", p["detail"])

    def test_missing_policy_file_yields_no_probes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(probe_capabilities(tmp), [])


class TestDoctorReport(unittest.TestCase):
    def test_probe_label_never_changes_the_problem_count(self):
        # AC-2. 미설치는 결함이 아니다 — 종료 코드를 바꾸지 않는다. 설치돼 **있어도** 마찬가지다.
        # 라벨을 양쪽 극단으로 돌려도 결함 수가 같아야 이 절이 판정에 끼어들지 않는다는 뜻이다.
        # 결함 수가 지금 몇이든 상관없다 — 여기서 보는 것은 값이 아니라 **불변**이다.
        rep = doctor(REPO)
        self.assertTrue(rep["capabilities"], "프로브가 하나도 없으면 이 검사는 아무것도 확인하지 않는다")
        base = doctor_problem_count(rep, "repository")
        for label, detail in (("absent", "설치 흔적 없음"), ("present", "설치 흔적 확인")):
            rep["capabilities"] = [dict(p, label=label, detail=detail) for p in rep["capabilities"]]
            self.assertEqual(doctor_problem_count(rep, "repository"), base, format_report(rep))

    def test_this_repo_has_no_doctor_problems(self):
        # `romeo doctor --strict --scope repository` 와 같은 판정이다. 이것을 여기 두는 이유는
        # CI(.github/workflows/harness.yml)가 그 명령을 돌지 않기 때문이다 — `fixtures check` 는
        # 충돌 fixture 위반을 잡지 못한다(2026-08-31 실측: c7 위반이 있는 트리에서 exit 0).
        # 위 불변 검사와 분리해 둔다. 섞어 두면 저장소에 결함이 생겼을 때 엉뚱한 이름으로 깨진다.
        self.assertEqual(doctor_problem_count(doctor(REPO), "repository"), 0,
                         format_report(doctor(REPO)))

    def test_report_has_capability_section(self):
        self.assertIn("## 능력 프로브", format_report(doctor(REPO)))

    def test_report_says_not_installed_when_absent(self):
        # 문구를 정하는 것은 라벨이지 이 머신의 설치 상태가 아니다 —
        # 아래 present 쪽 검사와 같은 방식으로 라벨을 고정해서 본다.
        rep = doctor(REPO)
        self.assertTrue(rep["capabilities"], "프로브가 하나도 없으면 이 검사는 아무것도 확인하지 않는다")
        rep["capabilities"] = [dict(p, label="absent", detail="설치 흔적 없음")
                               for p in rep["capabilities"]]
        self.assertIn("설치 흔적 없음", format_report(rep))

    def test_report_never_calls_an_install_trace_an_execution(self):
        rep = doctor(REPO)
        rep["capabilities"] = [dict(p, label="present", detail="설치 흔적 확인",
                                    reads={"modules": ["bmm"], "platform_codes": ["codex"]})
                               for p in rep["capabilities"]]
        text = format_report(rep)
        self.assertIn("실행 증거가 아니다", text,
                      "present 를 인쇄하면서 그것이 실행 증거가 아니라는 말을 하지 않는다")

    def test_report_is_json_serializable(self):
        import json
        json.dumps(doctor(REPO), ensure_ascii=False)


class TestRouterRecommends(unittest.TestCase):
    def _discovery_route(self):
        return route({"unit": "T1", "mode": "discovery", "intent": "write", "facets": ["tooling"],
                      "gates": [], "blast_radius": "medium", "uncertainty": "medium"})

    def test_bmad_cis_is_accepted_with_eleven_recommends(self):
        # AC-3.
        part = load_policy()["packages"]["parts"]["bmad-cis"]
        self.assertEqual(part["status"], "accepted")
        self.assertEqual(part["gate"], "G-M3")
        self.assertEqual(len(part["recommends"]), 11)
        self.assertEqual(part["output_binding"], "inputs-link")
        self.assertEqual(part["capability"], "discovery.bmad")

    def test_recommends_match_provenance_router_recommends(self):
        imports = load_any(REPO / "provenance/imports.yaml")["imports"]
        allowed = [r for e in imports if e.get("status") == "accepted"
                   for r in (e.get("router_recommends") or [])]
        self.assertEqual(sorted(load_policy()["packages"]["parts"]["bmad-cis"]["recommends"]),
                         sorted(allowed))

    def test_route_surfaces_recommends_on_the_part(self):
        part = {p["id"]: p for p in self._discovery_route()["parts"]}["bmad-cis"]
        self.assertEqual(len(part["recommends"]), 11)
        self.assertEqual(part["output_binding"], "inputs-link")
        self.assertEqual(part["capability"], "discovery.bmad")

    def test_status_stays_pending_because_nothing_is_installed_yet(self):
        # accepted(결정) 와 active(부착) 는 다르다. 설치는 다음 단위다(K-63).
        part = {p["id"]: p for p in self._discovery_route()["parts"]}["bmad-cis"]
        self.assertNotEqual(part["status"], "active")


class TestCard(unittest.TestCase):
    def setUp(self):
        self.proposal = load_any(REPO / "fixtures/proposals/fx-bmad-discovery-recommend.yaml")
        self.out = route(self.proposal["candidate"])
        self.text = render_card(self.proposal, self.out, root=REPO)

    def test_card_prints_all_eleven_recommends(self):
        # AC-4. 하나라도 잘리면 사람이 본 목록과 정책표가 다르다.
        for skill in load_policy()["packages"]["parts"]["bmad-cis"]["recommends"]:
            self.assertIn(skill, self.text, f"{skill} 가 카드에 없다")

    def test_card_requires_inputs_link_not_copy(self):
        self.assertIn("inputs:", self.text)

    def test_card_prints_the_probe_result(self):
        # 카드가 인쇄해야 하는 것은 "absent" 라는 특정 값이 아니라 **프로브가 실제로 낸 값**이다.
        # 값을 못 박으면 이 머신에 BMAD 를 설치하는 순간 깨진다.
        probes = {p["id"]: p for p in probe_capabilities(REPO)}
        self.assertIn("discovery.bmad", self.text)
        self.assertIn(probes["discovery.bmad"]["label"], self.text)

    def test_card_stays_within_budget(self):
        limit = load_policy()["packages"]["budgets"]["card_max_lines"]
        self.assertLessEqual(len(self.text.splitlines()), limit)

    def test_card_without_recommends_has_no_parts_detail(self):
        # 추천이 없는 부품에까지 빈 줄을 인쇄하지 않는다.
        out = dict(self.out, parts=[{"id": "superpowers", "gate": "G-M2", "status": "active",
                                     "role": "x", "recommends": [], "output_binding": None,
                                     "capability": None}])
        self.assertNotIn("추천", render_card(self.proposal, out, root=REPO))


if __name__ == "__main__":
    unittest.main()
