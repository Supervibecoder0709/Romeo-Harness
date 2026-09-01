"""시나리오 3 자동 실행 — `scenarios/3-discovery-block.md` 의 9단계를 그대로 돌린다.

입력은 **기존 fixture** 다(`fixtures/requests/`). 시나리오 전용 입력을 새로 만들면 그 입력이 시나리오에
맞춰져 있어 아무것도 증명하지 못한다. 3·6 단계는 **막히는 것이 통과**다 — 통과만 보이는 런북은 빈 검사와 같다."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from romeo import HARNESS_ROOT, frontmatter
from romeo import blocks
from romeo.close import close_unit
from romeo.docs import approve_unit, create_unit
from romeo.envelope import write_envelope
from romeo.evidence import run_command
from romeo.doctor import probe_capabilities
from romeo.policy import (classification_from_frontmatter, load_policy, load_project_state,
                          route)
from romeo.util import load_yaml

RUNBOOK = HARNESS_ROOT / "scenarios/3-discovery-block.md"
DISCOVERY_FX = HARNESS_ROOT / "fixtures/requests/fx-discord-computer-use-automation.yaml"
T2_FX = HARNESS_ROOT / "fixtures/requests/fx-s16-edu-webapp-new.yaml"

SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"
SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `scripts/` · `README.md`"
RESEARCH_LINK = "../../research/2026-09-01-discord-computer-use.md"
#: 그럴듯한 거짓 값 — 경로 모양이지만 저장소에 없는 파일. 빈 값만 막는 검사는 이것을 통과시킨다.
#: 이 런북의 이전 판이 실제로 그랬다: 여기 적힌 경로는 한 번도 존재한 적이 없는데 승인이 통과했다.
MISSING_LINK = "../../research/없는파일.md"

#: 「능력 확인」 표의 자리표시자 행. 절이 걸린 단위의 spec 에만 있다.
CAPABILITY_ROW = "| NEEDS_INPUT | NEEDS_INPUT | NEEDS_INPUT | NEEDS_INPUT |"


def fill_capability_table(fm, body, root):
    """「능력 확인」 표를 **프로브가 실제로 낸 값**으로 채운다 — 카드가 인쇄한 것을 옮겨 적는 자리다.

    다른 절처럼 `NEEDS_INPUT` 를 아무 글자로 바꾸면 이 표는 미완료 토큰 검사만 통과하고
    차단(`capability-probed`)에 걸린다. 그것이 이 차단의 요점이다 — 형태가 그럴듯하고 내용이 거짓인 값.
    절이 걸리지 않은 단위에서는 아무것도 하지 않는다."""
    if CAPABILITY_ROW not in body:
        return body
    required = route(classification_from_frontmatter(fm),
                     project_state=load_project_state(HARNESS_ROOT))["capabilities"]
    probes = {c["id"]: c for c in probe_capabilities(root, HARNESS_ROOT)}
    rows = []
    for cid in required:
        c = probes[cid]
        alt = "" if c["label"] == "present" else (c.get("alternatives") or [""])[0]
        rows.append(f"| {c['title'] or cid} | {cid} | {c['label']} | {alt} |")
    return body.replace(CAPABILITY_ROW, "\n".join(rows))


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


class TestScenario3(unittest.TestCase):
    """단계 번호는 메서드 이름의 `stepN` 에 들어 있다 — 런북과 이 파일을 나란히 읽을 수 있게."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        self.discovery = load_yaml(DISCOVERY_FX)
        self.t2 = load_yaml(T2_FX)

    def tearDown(self):
        self.tmp.cleanup()

    # ── 도구 ─────────────────────────────────────────────────────────────────
    def route_of(self, fx):
        return route(fx["classification"], project_state=load_project_state(HARNESS_ROOT))

    def create(self, fx, slug):
        res = create_unit(self.route_of(fx), fx["id"], slug, fx["request_text"][:60],
                          project_root=self.root, date="20260901")
        self.assertEqual(res["skipped"], [], f"NOT_AVAILABLE_YET 로 건너뛴 문서가 있다: {res['skipped']}")
        return res["id"], {Path(f).name: Path(f) for f in res["files"]}

    def fill_spec(self, spec):
        fm, body = frontmatter.read(spec)
        body = fill_capability_table(fm, body, self.root)
        body = (body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
                    .replace('command: "채움"', 'command: "true"').replace("- [ ] AC-1", "- [x] AC-1"))
        frontmatter.write(spec, fm, body)

    def fill_doc(self, path):
        fm, body = frontmatter.read(path)
        frontmatter.write(path, fm, body.replace("NEEDS_INPUT", "채움"))

    def set_inputs(self, doc, items, create=True):
        """`inputs:` 를 붙이고, `create` 면 가리키는 경로도 실제로 만든다."""
        fm, body = frontmatter.read(doc)
        fm["inputs"] = list(items)
        frontmatter.write(doc, fm, body)
        if create:
            for it in items:
                target = (Path(doc).parent / str(it).split("#")[0]).resolve()
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("조사 결과(테스트)\n", encoding="utf-8")

    def commit(self, msg="c"):
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", msg, cwd=self.root)

    # ── 런북 자체 ────────────────────────────────────────────────────────────
    def test_runbook_files_exist_with_the_five_sections(self):
        self.assertTrue((HARNESS_ROOT / "scenarios/README.md").is_file())
        text = RUNBOOK.read_text(encoding="utf-8")
        for title in ("## 전제", "## 단계", "## 기대 판단", "## 산출물", "## 증거"):
            self.assertIn(title, text)
        self.assertIn("tests/test_scenario_3.py", text)

    # ── 단계 1~2 ─────────────────────────────────────────────────────────────
    def test_step1_router_blocks_and_recommends_match_the_fixture(self):
        out = self.route_of(self.discovery)
        self.assertEqual(out["blocks"], self.discovery["expected"]["blocks"])
        self.assertIn("discovery-result", out["blocks"])
        parts = {p["id"]: p for p in out["parts"]}
        self.assertEqual(sorted(parts), sorted(self.discovery["expected"]["parts"]))
        # 부품 추천은 산출물을 복사하지 않는다 — inputs: 링크로만 붙는다(K-62).
        self.assertEqual(parts["bmad-cis"]["output_binding"], "inputs-link")
        self.assertEqual(parts["bmad-cis"]["status"], "accepted")
        self.assertEqual(len(parts["bmad-cis"]["recommends"]), 11)
        self.assertIn("PART_PENDING_GATE", [w["id"] for w in out["warnings"]])

    def test_step2_package_carries_the_discovery_plan_section(self):
        _unit, files = self.create(self.discovery, "discovery-block")
        self.assertEqual(sorted(files), ["brief.md", "spec.md"])
        self.assertIn("## 조사·가설·검증 계획", files["brief.md"].read_text(encoding="utf-8"))

    # ── 단계 3~4: 조사는 승인까지 열리고 구현 위임에서 막힌다 ────────────────
    def _approved_discovery(self, slug="discovery-block"):
        unit, files = self.create(self.discovery, slug)
        self.fill_spec(files["spec.md"])
        self.fill_doc(files["brief.md"])
        return unit, files

    def test_step3a_approval_is_not_refused_without_research(self):
        """조사 단위는 조사 결과 없이도 **승인은 된다** — 승인에서 막으면 조사를 시작할 창구가 없다.
        차단이 `[approve, close]` 로 일괄 배치돼 있던 동안 이 자리가 순환이었다."""
        unit, files = self._approved_discovery()
        fm = approve_unit(unit, "tester", project_root=self.root)
        self.assertEqual(fm["status"], "active")

    def test_step3b_dispatch_is_refused_without_research_inputs(self):
        """**막는 것이 판정이다.** 조사 결과 없이 작업 계약이 만들어지면 이 시나리오는 실패다."""
        unit, files = self._approved_discovery()
        approve_unit(unit, "tester", project_root=self.root)
        self.commit("approve")
        with self.assertRaises(ValueError) as ctx:
            write_envelope(unit, "implementer", project_root=self.root, run_name="run-s3")
        msg = str(ctx.exception)
        self.assertIn("discovery-result", msg)
        self.assertIn("inputs:", msg)
        self.assertFalse((files["spec.md"].parent / "task").exists(), "막혔는데 계약이 쓰였다")

    def test_step3c_a_link_to_a_missing_path_is_still_refused(self):
        """그럴듯한 거짓 값 — 경로 모양이지만 없는 파일. 빈 값만 막는 검사는 여기서 통과한다."""
        unit, files = self._approved_discovery()
        self.set_inputs(files["brief.md"], [MISSING_LINK], create=False)
        approve_unit(unit, "tester", project_root=self.root)
        self.commit("approve")
        with self.assertRaises(ValueError) as ctx:
            write_envelope(unit, "implementer", project_root=self.root, run_name="run-s3")
        self.assertIn("없는파일", str(ctx.exception))

    def test_step3d_a_link_on_the_spec_is_still_refused(self):
        """정본은 조사 계획이 사는 문서(brief)다 — spec 에 붙인 링크로는 열리지 않는다."""
        unit, files = self._approved_discovery()
        self.set_inputs(files["spec.md"], [RESEARCH_LINK])
        approve_unit(unit, "tester", project_root=self.root)
        self.commit("approve")
        with self.assertRaises(ValueError):
            write_envelope(unit, "implementer", project_root=self.root, run_name="run-s3")

    def test_step4_linking_the_research_output_unblocks_dispatch(self):
        unit, files = self._approved_discovery()
        self.set_inputs(files["brief.md"], [RESEARCH_LINK])
        approve_unit(unit, "tester", project_root=self.root)
        self.commit("approve")
        res = write_envelope(unit, "implementer", project_root=self.root, run_name="run-s3")
        self.assertTrue(Path(res["path"]).is_file())
        # 회차도 함께 남는다 — 손으로 §3 을 밟은 관통이 기록되지 않던 자리다(Q-27).
        self.assertEqual(res["attempt"]["run"], "run-s3")

    def test_step4b_an_unfilled_brief_still_blocks_dispatch(self):
        """라우터가 요구한 절(첫 마일스톤 spike)이 brief 에 빈 채로 남아 있으면 위임하지 않는다."""
        unit, files = self.create(self.discovery, "discovery-block")
        self.fill_spec(files["spec.md"])
        self.set_inputs(files["brief.md"], [RESEARCH_LINK])
        approve_unit(unit, "tester", project_root=self.root)
        self.commit("approve")
        with self.assertRaises(ValueError) as ctx:
            write_envelope(unit, "implementer", project_root=self.root, run_name="run-s3")
        self.assertIn("brief.md", str(ctx.exception))

    # ── 단계 5~7: T2 는 마일스톤 계획 없이 열리지 않는다 ─────────────────────
    def test_step5_t2_package_starts_with_a_charter(self):
        _unit, files = self.create(self.t2, "initiative")
        self.assertEqual(sorted(files), ["brief.md", "charter.md", "spec.md"])
        self.assertIn("## 마일스톤 계획", files["charter.md"].read_text(encoding="utf-8"))

    def test_step6_approval_is_refused_while_the_milestone_plan_is_empty(self):
        unit, files = self.create(self.t2, "initiative")
        self.fill_spec(files["spec.md"])
        with self.assertRaises(ValueError) as ctx:
            approve_unit(unit, "tester", project_root=self.root)
        self.assertIn("milestone-plan", str(ctx.exception))

    def test_step7_filled_milestone_plan_unblocks_approval(self):
        unit, files = self.create(self.t2, "initiative")
        self.fill_spec(files["spec.md"])
        self.fill_doc(files["charter.md"])
        self.assertEqual(approve_unit(unit, "tester", project_root=self.root)["status"], "active")

    # ── 단계 8~9: 종료 판정과 소급 금지 ─────────────────────────────────────
    def _closable_discovery(self):
        unit, files = self.create(self.discovery, "discovery-block")
        self.fill_spec(files["spec.md"])
        self.fill_doc(files["brief.md"])
        self.set_inputs(files["brief.md"], [RESEARCH_LINK])
        approve_unit(unit, "tester", project_root=self.root)
        (self.root / "impl.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl", cwd=self.root)
        run_command(unit, "true", run_name="run-scenario3", label="check-1", project_root=self.root)
        return unit, files

    def test_step8_close_reports_one_block_satisfied_row_per_block(self):
        """**종료는 backstop 이다** — 막기 시작하는 사건은 차단마다 하나지만, 걸린 차단은 전부 다시 본다."""
        unit, _files = self._closable_discovery()
        res = close_unit(unit, project_root=self.root, dry_run=True, rerun=False)
        rows = [c for c in res["checks"] if c["id"] == "BLOCK_SATISFIED"]
        self.assertEqual(sorted(r["detail"].split(":")[0] for r in rows),
                         ["capability-probed", "discovery-result", "spec-ready"])
        self.assertTrue(all(r["ok"] for r in rows), rows)

    def test_step8b_close_catches_a_block_that_broke_after_dispatch(self):
        """위임에서 막는 차단도 종료에서 다시 본다 — 링크를 지우면 close 가 잡는다."""
        unit, files = self._closable_discovery()
        self.set_inputs(files["brief.md"], [], create=False)
        res = close_unit(unit, project_root=self.root, dry_run=True, rerun=False)
        bad = [c for c in res["checks"] if c["id"] == "BLOCK_SATISFIED" and not c["ok"]]
        self.assertTrue(any("discovery-result" in c["detail"] for c in bad), res["checks"])

    def test_step9_a_done_unit_is_not_re_judged(self):
        # T1 은 검토자가 붙어 close 가 PASS 하지 않으므로, 소급 금지는 done 을 만들 수 있는 T0 로 본다.
        out = route({"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        res = create_unit(out, "소급 금지", "no-retro", "이미 닫힌 단위", project_root=self.root, date="20260901")
        unit, spec = res["id"], Path(res["files"][0])
        self.fill_spec(spec)
        approve_unit(unit, "tester", project_root=self.root)
        (self.root / "impl.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl", cwd=self.root)
        run_command(unit, "true", run_name="run-scenario3", label="check-1", project_root=self.root)
        self.assertEqual(close_unit(unit, project_root=self.root)["verdict"], "PASS")
        # 닫힌 뒤에 차단 조건을 무너뜨려도 판정과 문서가 그대로다.
        fm, body = frontmatter.read(spec)
        sec = blocks.section(body, "확인란")
        frontmatter.write(spec, fm, body.replace(sec, sec.replace("채움", "NEEDS_INPUT", 1), 1))
        before = spec.read_bytes()
        res2 = close_unit(unit, project_root=self.root, rerun=False)
        self.assertEqual(res2["verdict"], "FAIL")
        self.assertIn("NOT_ALREADY_DONE", [c["id"] for c in res2["checks"] if not c["ok"]])
        self.assertEqual([c for c in res2["checks"] if c["id"] == "BLOCK_SATISFIED"], [])
        self.assertEqual(spec.read_bytes(), before)

    def test_fixture_expectations_still_hold_for_both_inputs(self):
        """런북의 전제가 fixture 와 어긋나지 않는지 — 정책표가 바뀌면 여기서 먼저 드러난다."""
        for fx in (self.discovery, self.t2):
            out = self.route_of(fx)
            self.assertEqual(out["blocks"], fx["expected"]["blocks"], fx["id"])
            self.assertEqual(out["package"], fx["expected"]["package"], fx["id"])
            for bid in out["blocks"]:
                self.assertIn(bid, blocks.BLOCK_CHECKS, fx["id"])
                self.assertIn(bid, blocks.catalog(load_policy()["packages"]), fx["id"])


if __name__ == "__main__":
    unittest.main()
