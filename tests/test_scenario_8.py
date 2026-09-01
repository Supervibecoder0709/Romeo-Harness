"""시나리오 8 자동 실행 — `scenarios/8-capability-absent.md` 의 8단계를 그대로 돌린다.

입력은 **기존 fixture** 다(`fixtures/requests/` · `fixtures/proposals/`). 시나리오 전용 입력을 새로 만들면
그 입력이 시나리오에 맞춰져 있어 아무것도 증명하지 못한다.

4 단계는 **막히는 것이 통과**다. 반례는 빈 값이 아니라 **그럴듯한 거짓 값**이다 —
빈 값(`NEEDS_INPUT`)은 고치기 전에도 막혔고, 통과한 것은 형태가 그럴듯하고 내용이 거짓인 값이었다.
5 단계는 그 반대다: **사실대로 적은 부재는 승인된다.** 부재를 막으면 「되는지 조사해 보자」 가 불가능해진다(Q-28).
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from romeo import HARNESS_ROOT, blocks, frontmatter
from romeo.card import render_card
from romeo.doctor import CAPABILITIES_PATH, adapter_markers, load_capabilities, probe_capabilities
from romeo.docs import approve_unit, create_unit
from romeo.policy import PolicyError, load_policy, load_project_state, route
from romeo.util import load_any, load_yaml

RUNBOOK = HARNESS_ROOT / "scenarios/8-capability-absent.md"
REQUEST_FX = HARNESS_ROOT / "fixtures/requests/fx-discord-computer-use-automation.yaml"
PROPOSAL_FX = HARNESS_ROOT / "fixtures/proposals/fx-discord-computer-use-automation.yaml"

#: 라우터가 요구하는 능력. 값을 여기 못 박는 이유는 **요구가 사라지는 것**도 결함이기 때문이다 —
#: 오버레이에서 `add_capabilities` 를 지우면 차단은 통과하고 아무도 그것을 알아채지 못한다.
REQUIRED = ["automation.ui-control", "automation.tool-server"]

#: 그럴듯한 거짓 값. 넷 다 미완료 토큰 검사(open-loop)는 통과한다 — 빈칸이 아니기 때문이다.
FAKE_PROBE_ID = "automation.desktop-control"   # 형태는 맞지만 카탈로그에 없다
ALT = "그 단계만 사람이 직접 수행한다"

SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"
SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `impl.txt`"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


def tree(root):
    """저장소 안의 파일 목록(상대 경로). 프로브 전후를 대조하는 데 쓴다."""
    return sorted(str(p.relative_to(root)) for p in Path(root).rglob("*") if p.is_file())


def row(name, probe_id, result, alt):
    return f"| {name} | `{probe_id}` | {result} | {alt} |"


class _Unit(unittest.TestCase):
    """임시 저장소에 이 fixture 의 작업 단위 하나를 세운다. 저장소의 docs/work 를 건드리지 않는다.

    프로젝트 루트와 하네스 루트를 **가른다** — 능력 카탈로그·어댑터 선언은 하네스가 갖고,
    흔적 파일이 있는가는 이 임시 저장소를 본다. 부착된 프로젝트에서의 배치와 같다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        self.fx = load_yaml(REQUEST_FX)
        self.out = route(self.fx["classification"], project_state=load_project_state(HARNESS_ROOT))
        res = create_unit(self.out, self.fx["id"], "capability-absent", self.fx["request_text"][:60],
                          project_root=self.root, date="20260901")
        self.unit = res["id"]
        self.files = {Path(f).name: Path(f) for f in res["files"]}
        self.spec = self.files["spec.md"]

    def tearDown(self):
        self.tmp.cleanup()

    def probes(self):
        return {p["id"]: p for p in probe_capabilities(self.root, HARNESS_ROOT)}

    def fill_rest(self):
        """「능력 확인」 을 뺀 나머지를 채운다 — 이 시나리오가 보는 것은 그 절 하나다."""
        fm, body = frontmatter.read(self.spec)
        cap = blocks.section(body, "능력 확인")
        rest = (body.replace(cap, "@@CAP@@")
                    .replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
                    .replace('command: "채움"', 'command: "true"').replace("- [ ] AC-1", "- [x] AC-1"))
        frontmatter.write(self.spec, fm, rest.replace("@@CAP@@", cap))
        for name, path in self.files.items():
            if name == "spec.md":
                continue
            dfm, dbody = frontmatter.read(path)
            frontmatter.write(path, dfm, dbody.replace("NEEDS_INPUT", "채움"))

    def set_table(self, rows):
        """「능력 확인」 절의 표 데이터 행을 통째로 바꾼다. 안내문과 헤더는 그대로 둔다."""
        fm, body = frontmatter.read(self.spec)
        cap = blocks.section(body, "능력 확인")
        head, sep = None, None
        kept = []
        for ln in cap.split("\n"):
            if ln.strip().startswith("|"):
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                if head is None:
                    head = ln
                elif sep is None and all(set(c) <= set("-: ") and c for c in cells):
                    sep = ln
                continue
            kept.append(ln)
        table = "\n".join([head, sep] + list(rows))
        frontmatter.write(self.spec, fm, body.replace(cap, "\n".join(kept).rstrip() + "\n\n" + table + "\n"))

    def truthful_rows(self):
        p = self.probes()
        return [row("화면 조작", cid, p[cid]["label"], ALT if p[cid]["label"] != "present" else "")
                for cid in REQUIRED]

    def approve(self):
        return approve_unit(self.unit, "tester", project_root=self.root)

    def refused(self):
        with self.assertRaises(ValueError) as ctx:
            self.approve()
        fm, _ = frontmatter.read(self.spec)
        self.assertEqual(fm["status"], "draft", "막혔는데 승인 표시가 남았다")
        return str(ctx.exception)


class TestRunbook(unittest.TestCase):
    def test_runbook_files_exist_with_the_five_sections(self):
        self.assertTrue(RUNBOOK.is_file())
        text = RUNBOOK.read_text(encoding="utf-8")
        for title in ("## 전제", "## 단계", "## 기대 판단", "## 산출물", "## 증거"):
            self.assertIn(title, text)
        self.assertIn("tests/test_scenario_8.py", text)

    def test_runbook_is_listed_in_the_index(self):
        # AC-9. 목록에 없는 런북은 다음 사람이 찾지 못한다.
        self.assertIn("8-capability-absent.md",
                      (HARNESS_ROOT / "scenarios/README.md").read_text(encoding="utf-8"))

    def test_runbook_names_where_the_implementer_must_stop(self):
        # AC-9. 통과만 보이지 않는다 — 구현자가 멈춰야 하는 자리를 문서가 지목한다.
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn("BLOCKED_CAPABILITY", text)
        self.assertIn("자동 설치", text)


class TestCapabilityCatalog(unittest.TestCase):
    """AC-1·AC-2 — 능력은 코어가 정의하고 흔적 경로는 어댑터가 갖는다."""

    def test_core_defines_both_capabilities_with_why_alternatives_honesty(self):
        caps = load_capabilities(HARNESS_ROOT)["automation"]
        for name in ("ui-control", "tool-server"):
            spec = caps[name]
            self.assertEqual(spec["kind"], "adapter_marker")
            self.assertEqual(sorted(spec["result_labels"]), ["absent", "present"])
            for field in blocks.CAPABILITY_REQUIRED_FIELDS:
                self.assertTrue(str(spec.get(field) or "").strip() if field != "alternatives"
                                else spec.get("alternatives"),
                                f"automation.{name}: {field} 가 비어 있다")
            self.assertGreaterEqual(len(spec["alternatives"]), 2)

    def test_core_does_not_know_the_marker_paths(self):
        # C-C6. 코어가 런타임 경로를 알면 그것이 곧 도구명이다.
        text = (HARNESS_ROOT / CAPABILITIES_PATH).read_text(encoding="utf-8")
        for group, caps in load_capabilities(HARNESS_ROOT).items():
            for name, spec in caps.items():
                if spec.get("kind") == "adapter_marker":
                    self.assertIsNone(spec.get("marker"),
                                      f"{group}.{name}: 코어가 흔적 경로를 들고 있다")
        for path in adapter_markers(HARNESS_ROOT).values():
            for _runtime, paths in path:
                for p in paths:
                    self.assertNotIn(p, text, "어댑터의 경로가 코어에도 적혀 있다 — 원본이 둘이다")

    def test_both_adapters_declare_capability_markers(self):
        # AC-2. 선언 자체는 양쪽에 있다. 값이 비는 것과 키가 없는 것은 다르다.
        for adapter in ("claude", "codex"):
            data = load_any(HARNESS_ROOT / f"adapters/{adapter}/adapter.yaml")
            self.assertIn("capability_markers", data, f"{adapter} 어댑터에 선언이 없다")
            self.assertEqual(sorted(data["capability_markers"]), sorted(REQUIRED))

    def test_a_capability_the_policy_requires_but_core_does_not_define_fails_the_load(self):
        """§11 — 요구하는 자리와 정의하는 자리가 어긋나면 **로드가 실패한다.**"""
        pk = {"blocks": {}, "sections": {}, "base": {}, "overlays": [
            {"id": "x", "add_capabilities": ["automation.없는능력"],
             "add_blocks": [blocks.CAPABILITY_BLOCK]}]}
        defects = blocks.capability_defects(pk, load_capabilities(HARNESS_ROOT))
        self.assertTrue(any("능력 카탈로그" in d for d in defects), defects)

    def test_requiring_a_capability_without_the_block_fails_the_load(self):
        """요구만 하고 대조하지 않으면 그럴듯한 거짓 값이 그대로 통과한다."""
        pk = {"overlays": [{"id": "x", "add_capabilities": REQUIRED, "add_blocks": []}]}
        defects = blocks.capability_defects(pk, load_capabilities(HARNESS_ROOT))
        self.assertTrue(any(blocks.CAPABILITY_BLOCK in d for d in defects), defects)

    def test_the_repo_policy_itself_has_no_capability_defect(self):
        pol = load_policy()
        self.assertEqual(blocks.capability_defects(pol["packages"], pol["capabilities"]), [])
        self.assertEqual(sorted(blocks.required_capabilities(pol["packages"])), sorted(REQUIRED))


class TestProbe(unittest.TestCase):
    """단계 6~8 — 어댑터가 경로를 주지 않으면 absent · 라벨은 흔적으로 뒤바뀐다 · 프로브는 읽기만 한다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _harness(self, claude_markers, codex_markers):
        """능력 카탈로그는 이 저장소 것을 그대로 쓰고, 어댑터 선언만 바꾼 하네스 사본."""
        h = self.root / "harness"
        (h / "core/policy").mkdir(parents=True)
        shutil.copy(HARNESS_ROOT / CAPABILITIES_PATH, h / CAPABILITIES_PATH)
        import yaml
        for name, markers in (("claude", claude_markers), ("codex", codex_markers)):
            d = h / "adapters" / name
            d.mkdir(parents=True)
            (d / "adapter.yaml").write_text(
                yaml.safe_dump({"id": name, "capability_markers": markers}, allow_unicode=True),
                encoding="utf-8")
        return h

    def test_step6_a_runtime_without_a_declared_path_is_absent(self):
        h = self._harness({"automation.ui-control": [".marker"]}, {"automation.ui-control": []})
        p = {x["id"]: x for x in probe_capabilities(self.root, h)}["automation.ui-control"]
        self.assertEqual(p["label"], "absent")
        self.assertEqual(p["by_runtime"]["codex"]["label"], "absent")
        self.assertIn("경로 선언 없음", p["detail"])

    def test_step6b_a_capability_no_adapter_declares_is_absent(self):
        h = self._harness({}, {})
        p = {x["id"]: x for x in probe_capabilities(self.root, h)}["automation.ui-control"]
        self.assertEqual(p["label"], "absent")
        self.assertIn("어댑터가 흔적 경로를 주지 않았다", p["detail"])

    def test_step7_the_label_flips_with_the_marker_and_flips_back(self):
        h = self._harness({"automation.ui-control": [".marker"]}, {"automation.ui-control": []})

        def label():
            return {x["id"]: x for x in probe_capabilities(self.root, h)}["automation.ui-control"]["label"]

        self.assertEqual(label(), "absent")
        (self.root / ".marker").write_text("x\n", encoding="utf-8")
        self.assertEqual(label(), "present")
        (self.root / ".marker").unlink()
        self.assertEqual(label(), "absent", "흔적을 지웠는데 present 로 남았다")

    def test_step8_probing_creates_nothing(self):
        # AC-8. 자동 설치 금지 — 프로브가 흔적을 만들면 그 다음 프로브는 자기가 만든 것을 본다.
        h = self._harness({"automation.ui-control": [".marker"]}, {"automation.ui-control": []})
        before = tree(self.root)
        probe_capabilities(self.root, h)
        probe_capabilities(self.root, h)
        self.assertEqual(tree(self.root), before)


class TestRouterAndCard(unittest.TestCase):
    """단계 1~2 — 라우터가 요구를 계산하고 카드가 결과·대안을 인쇄한다."""

    def test_step1_router_computes_the_required_capabilities(self):
        out = route(load_yaml(REQUEST_FX)["classification"])
        self.assertEqual(out["capabilities"], REQUIRED)
        self.assertIn(blocks.CAPABILITY_BLOCK, out["blocks"])

    def test_step1b_other_facets_require_nothing(self):
        out = route({"unit": "T1", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        self.assertEqual(out["capabilities"], [])
        self.assertNotIn(blocks.CAPABILITY_BLOCK, out["blocks"])

    def test_step1c_a_request_that_makes_no_document_still_requires_them(self):
        """AC-3 은 단위를 제한하지 않는다 — 문서 package 가 비어도 같은 facet 이면 같은 능력을 요구한다.

        시나리오 8 은 「분류는 정상 + 능력 부재 카드」다. 문서를 만들지 않는 요청에서는 **카드가 유일한
        기록**이므로, 여기서 능력 목록이 비면 사람은 그 능력이 있는 것으로 읽고 계획에 넣는다(K-51).
        차단은 문서를 읽어 판정하므로 package 가 없으면 걸리지 않는 것이 맞다 — 능력만 남는다."""
        out = route({"unit": "none", "mode": "delivery", "intent": "read", "facets": ["browser-automation"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        self.assertEqual(out["package"], [], "문서를 만드는 분기라면 이 검사는 T1 분기의 중복이다")
        self.assertEqual(out["capabilities"], REQUIRED)

    def test_step2_card_prints_each_capability_with_its_probe_result(self):
        # AC-4. 값을 못 박지 않는다 — 카드가 인쇄해야 하는 것은 **프로브가 실제로 낸 값**이다.
        proposal = load_any(PROPOSAL_FX)
        out = route(proposal["candidate"])
        text = render_card(proposal, out, root=HARNESS_ROOT)
        probes = {p["id"]: p for p in probe_capabilities(HARNESS_ROOT)}
        for cid in REQUIRED:
            self.assertIn(cid, text, f"{cid} 가 카드에 없다")
            line = next(ln for ln in text.split("\n") if cid in ln)
            self.assertIn(probes[cid]["label"], line)

    def test_step2b_card_prints_an_alternative_for_what_is_absent(self):
        proposal = load_any(PROPOSAL_FX)
        text = render_card(proposal, route(proposal["candidate"]), root=HARNESS_ROOT)
        probes = {p["id"]: p for p in probe_capabilities(HARNESS_ROOT)}
        for cid in REQUIRED:
            if probes[cid]["label"] == "present":
                continue
            line = next(ln for ln in text.split("\n") if cid in ln)
            self.assertIn("대안", line, f"{cid} 를 없다고 인쇄하면서 대안을 말하지 않는다")

    def test_step2e_card_prints_them_when_no_document_is_made(self):
        """AC-4 의 같은 분기 — 문서가 없어도 카드는 프로브 결과를 인쇄한다."""
        proposal = load_any(PROPOSAL_FX)
        out = route(dict(proposal["candidate"], unit="none"))
        text = render_card(proposal, out, root=HARNESS_ROOT)
        self.assertIn("문서: 없음", text, "문서를 만드는 분기라면 이 검사는 test_step2 의 중복이다")
        probes = {p["id"]: p for p in probe_capabilities(HARNESS_ROOT)}
        for cid in REQUIRED:
            line = next((ln for ln in text.split("\n") if cid in ln), None)
            self.assertIsNotNone(line, f"{cid} 가 카드에 없다")
            self.assertIn(probes[cid]["label"], line)

    def test_step2f_the_card_probes_the_repo_that_root_points_at(self):
        """AC-4 의 나머지 분기 — 하네스를 **부착한 프로젝트**에서 프로브 대상은 그 프로젝트다.

        카탈로그·어댑터 선언은 하네스의 내용이고 흔적 파일은 대상 저장소의 상태다(doctor.probe_capabilities
        의 두 루트). 이 둘을 배선하지 않으면 카드는 현재 저장소를 보거나 카탈로그를 못 찾아 「프로브 없음」 을
        인쇄한다 — 사람은 대상 프로젝트의 상태로 읽는다(K-51). 그래서 CLI 를 그대로 실행해서 본다.
        """
        with tempfile.TemporaryDirectory() as d:
            project = Path(d)
            (project / ".mcp.json").write_text("{}\n", encoding="utf-8")
            out = subprocess.run([str(HARNESS_ROOT / "bin/romeo"), "card", "--proposal", str(PROPOSAL_FX),
                                  "--root", str(project)], capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            here = {p["id"]: p for p in probe_capabilities(HARNESS_ROOT)}
            for cid in REQUIRED:
                line = next((ln for ln in out.stdout.split("\n") if cid in ln), None)
                self.assertIsNotNone(line, f"{cid} 가 카드에 없다 — 대상 저장소를 프로브하지 못했다")
                self.assertIn("present", line, f"{cid}: --root 가 가리킨 저장소가 아니라 다른 곳을 봤다")
                self.assertEqual(here[cid]["label"], "absent",
                                 "이 저장소에서도 present 면 이 검사는 두 루트를 구별하지 못한다")

    def test_step2c_these_capabilities_hang_on_no_part(self):
        """부품에 붙지 않은 능력도 인쇄한다 — 부품 절에만 매달면 한 줄도 나오지 않던 자리다."""
        parts = load_policy()["packages"]["parts"]
        attached = {p.get("capability") for p in parts.values()}
        for cid in REQUIRED:
            self.assertNotIn(cid, attached)

    def test_step2d_card_stays_within_budget(self):
        proposal = load_any(PROPOSAL_FX)
        text = render_card(proposal, route(proposal["candidate"]), root=HARNESS_ROOT)
        self.assertLessEqual(len(text.split("\n")),
                             load_policy()["packages"]["budgets"]["card_max_lines"])


class TestBlockCatalog(unittest.TestCase):
    """AC-5 — 차단이 카탈로그·집행 코드 양쪽에 있고, 절이 그것을 가리킨다."""

    def setUp(self):
        self.pk = load_policy()["packages"]

    def test_block_is_in_both_the_catalog_and_the_enforcement_map(self):
        self.assertIn(blocks.CAPABILITY_BLOCK, blocks.catalog(self.pk))
        self.assertIn(blocks.CAPABILITY_BLOCK, blocks.BLOCK_CHECKS)
        self.assertEqual(blocks.catalog_defects(self.pk), [])

    def test_enforced_at_is_approve_only(self):
        meta = blocks.catalog(self.pk)[blocks.CAPABILITY_BLOCK]
        self.assertEqual(meta["enforced_at"], ["approve"])
        self.assertEqual(meta["reads"], "spec")

    def test_the_section_points_at_this_block(self):
        section = self.pk["sections"]["capability-check"]
        self.assertIn(f"block:{blocks.CAPABILITY_BLOCK}", section["enforcement"])
        self.assertEqual(blocks.section_defects(self.pk), [])

    def test_close_still_sees_it_as_a_backstop(self):
        ids = [blocks.CAPABILITY_BLOCK]
        self.assertEqual(blocks.enforced_at(self.pk, ids, "approve"), ids)
        self.assertEqual(blocks.enforced_at(self.pk, ids, "dispatch"), [])
        self.assertEqual(blocks.enforced_at(self.pk, ids, "close"), ids)


class TestSection(_Unit):
    """단계 3 — 라우터가 요구한 절이 spec 에 붙고 열이 정해져 있다."""

    def test_step3_spec_carries_the_capability_section(self):
        body = self.spec.read_text(encoding="utf-8")
        self.assertIn("## 능력 확인", body)
        head = next(ln for ln in blocks.section(body, "능력 확인").split("\n") if ln.strip().startswith("|"))
        self.assertEqual([c.strip() for c in head.strip().strip("|").split("|")],
                         list(blocks.CAPABILITY_COLUMNS))


class TestFalseValuesAreRefused(_Unit):
    """단계 4 — **막히는 것이 판정이다.** 넷 중 하나라도 통과하면 이 시나리오는 실패다."""

    def setUp(self):
        super().setUp()
        self.fill_rest()

    def test_step4a_calling_an_absent_capability_present_is_refused(self):
        p = self.probes()
        self.assertTrue(all(p[c]["label"] == "absent" for c in REQUIRED),
                        "이 저장소에서 두 능력이 absent 가 아니면 이 반례는 성립하지 않는다")
        self.set_table([row("화면 조작", REQUIRED[0], "present", ""),
                        row("도구 서버", REQUIRED[1], "absent", ALT)])
        why = self.refused()
        self.assertIn("present", why)
        self.assertIn("absent", why)
        self.assertIn(REQUIRED[0], why)

    def test_step4b_a_probe_id_that_is_not_in_the_catalog_is_refused(self):
        self.set_table([row("화면 조작", FAKE_PROBE_ID, "absent", ALT),
                        row("도구 서버", REQUIRED[1], "absent", ALT)])
        why = self.refused()
        self.assertIn("능력 카탈로그에 없다", why)
        self.assertIn(FAKE_PROBE_ID, why)

    def test_step4c_absent_without_an_alternative_is_refused(self):
        self.set_table([row("화면 조작", REQUIRED[0], "absent", ""),
                        row("도구 서버", REQUIRED[1], "absent", ALT)])
        self.assertIn("대안 칸이 비어 있다", self.refused())

    def test_step4d_a_required_capability_missing_from_the_table_is_refused(self):
        self.set_table([row("화면 조작", REQUIRED[0], "absent", ALT)])
        why = self.refused()
        self.assertIn("라우터가 요구한 능력이 표에 없다", why)
        self.assertIn(REQUIRED[1], why)

    def test_step4e_the_untouched_placeholder_is_also_refused(self):
        """빈 값도 막힌다 — 다만 이것만으로는 **고치기 전 상태와 구별되지 않는다.**
        위 넷이 이 검사의 본체이고, 이 하나는 빈 값이 새 통로가 되지 않았는지만 본다."""
        fm, body = frontmatter.read(self.spec)
        self.assertIn("NEEDS_INPUT", blocks.section(body, "능력 확인"))
        self.assertIn("NEEDS_INPUT", self.refused())


class TestTruthfulAbsenceIsApproved(_Unit):
    """단계 5 — **부재는 막지 않는다.** 막으면 「되는지 조사해 보자」 가 불가능해진다(Q-28)."""

    def setUp(self):
        super().setUp()
        self.fill_rest()

    def test_step5_absent_written_truthfully_with_alternatives_is_approved(self):
        self.set_table(self.truthful_rows())
        fm = self.approve()
        self.assertEqual(fm["status"], "active")
        self.assertTrue(fm["approved_at"])
        # 승인이 났어도 표는 여전히 absent 다 — 승인은 능력을 만들지 않는다.
        body = self.spec.read_text(encoding="utf-8")
        self.assertIn("absent", blocks.section(body, "능력 확인"))

    def test_step5b_the_block_reason_says_absence_did_not_block(self):
        self.set_table(self.truthful_rows())
        fm, body = frontmatter.read(self.spec)
        ok, why = blocks.satisfied(blocks.CAPABILITY_BLOCK, self.spec.parent, fm, body,
                                   context={"capabilities": REQUIRED, "project_root": self.root,
                                            "harness_root": HARNESS_ROOT})
        self.assertTrue(ok, why)
        self.assertIn("부재는 막지 않는다", why)

    def test_step5c_a_present_row_needs_no_alternative(self):
        """능력이 실제로 있으면 대안 칸은 비어도 된다 — 대안은 부재를 메우는 칸이다."""
        marker = self.root / ".mcp.json"
        marker.write_text("{}\n", encoding="utf-8")
        try:
            p = self.probes()
            if any(p[c]["label"] != "present" for c in REQUIRED):
                self.skipTest("이 어댑터 선언에서는 흔적 파일 하나로 present 가 되지 않는다")
            self.set_table([row("화면 조작", REQUIRED[0], "present", ""),
                            row("도구 서버", REQUIRED[1], "present", "")])
            self.assertEqual(self.approve()["status"], "active")
        finally:
            marker.unlink(missing_ok=True)


class TestPolicyLoadIsTheAlignmentGate(unittest.TestCase):
    """§11 — 요구·정의·대조가 어긋나면 라우팅 이전에, 로드에서 난다."""

    def test_load_fails_when_the_capability_catalog_is_missing(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP")) as tmp:
            h = Path(tmp)
            for rel in ("core/policy/classification.yaml", "core/policy/packages.yaml",
                        "core/policy/execution-guards.yaml", "core/schemas/fixture.json"):
                (h / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(HARNESS_ROOT / rel, h / rel)
            with self.assertRaises(PolicyError) as ctx:
                load_policy(h)
            self.assertIn("능력 요구", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
