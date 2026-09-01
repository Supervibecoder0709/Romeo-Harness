"""차단(blocks) 집행 — 카탈로그·집행 매핑 대조, 승인 거부, 종료 판정(BLOCK_SATISFIED), 소급 금지.

라우터가 계산해 카드에 인쇄까지 하던 차단이 아무것도 막지 않던 결함(2026-09-01 실측)을 고정한다.
**막아야 할 입력이 실제로 막히는가**를 반례로 본다 — 통과만 보는 검사는 빈 검사다."""
import os
import re
import shutil
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
from romeo.policy import PolicyError, load_policy, route
from romeo.util import dump_yaml, load_yaml

#: load_policy 가 읽는 파일 전부. 임시 harness_root 를 만들 때 이만큼만 복사하면 된다.
POLICY_FILES = ("core/policy/classification.yaml", "core/policy/packages.yaml",
                "core/policy/execution-guards.yaml", "core/policy/capabilities.yaml",
                "core/schemas/fixture.json")

SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"
SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `scripts/` · `README.md`"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


def cls(**kw):
    base = {"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"],
            "gates": [], "blast_radius": "small", "uncertainty": "low"}
    base.update(kw)
    return base


class _Repo(unittest.TestCase):
    """git 저장소 하나와 그 안의 작업 단위를 만드는 공통 뼈대."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, classification, slug, date="20260901"):
        res = create_unit(route(classification), f"차단 테스트 {slug}", slug, "차단 집행 테스트",
                          project_root=self.root, date=date)
        self.assertEqual(res["skipped"], [], f"템플릿이 없어 건너뛴 문서가 있다: {res['skipped']}")
        return res["id"], {Path(f).name: Path(f) for f in res["files"]}

    def fill_spec(self, spec, tick_ac=True, command="true"):
        fm, body = frontmatter.read(spec)
        body = (body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
                    .replace('command: "채움"', f'command: "{command}"'))
        if tick_ac:
            body = body.replace("- [ ] AC-1", "- [x] AC-1")
        frontmatter.write(spec, fm, body)

    def fill_doc(self, path):
        fm, body = frontmatter.read(path)
        frontmatter.write(path, fm, body.replace("NEEDS_INPUT", "채움"))

    def set_inputs(self, doc, items, create=True):
        """`inputs:` 를 그 문서에 붙인다. `create` 면 가리키는 경로도 실제로 만든다 —
        차단이 경로 실재를 보므로, 없는 경로를 붙이는 것은 붙이지 않은 것과 같다."""
        fm, body = frontmatter.read(doc)
        fm["inputs"] = list(items)
        frontmatter.write(doc, fm, body)
        if create:
            for it in items:
                it = str(it).strip()
                if not it or it.startswith(("http://", "https://")):
                    continue
                target = (Path(doc).parent / it.split("#")[0]).resolve()
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_text("조사 결과(테스트)\n", encoding="utf-8")

    def research_doc(self, files):
        """조사 결과가 붙는 정본 문서 — brief 가 있으면 brief, 없으면 charter(카탈로그의 reads)."""
        return files.get("brief.md") or files.get("charter.md")

    def fill_package(self, files):
        """spec 밖의 패키지 문서를 채운다 — 미완료 검사가 패키지 전체를 본다."""
        for name, path in files.items():
            if name != "spec.md":
                self.fill_doc(path)

    def unblank_section(self, path, title, marker="채움"):
        """채워 둔 절 하나를 다시 미완료로 되돌린다 — 그 차단 하나만 어긋난 반례를 만든다."""
        text = path.read_text(encoding="utf-8")
        fm, body = frontmatter.split(text)
        sec = blocks.section(body, title)
        self.assertIsNotNone(sec, f"「{title}」 절이 없다")
        self.assertIn(marker, sec, f"「{title}」 절에 {marker} 가 없다")
        frontmatter.write(path, fm, body.replace(sec, sec.replace(marker, "NEEDS_INPUT", 1), 1))


class TestBlockCatalog(_Repo):
    """카탈로그가 있고, 실제로 쓰이는 차단이 카탈로그·집행 코드 양쪽에 있다."""

    def setUp(self):
        self.pk = load_policy()["packages"]

    def tearDown(self):
        pass

    def test_catalog_exists_with_the_five_blocks(self):
        cat = blocks.catalog(self.pk)
        self.assertEqual(sorted(cat), ["capability-probed", "discovery-result", "milestone-plan",
                                       "risk-plan-ready", "spec-ready"])
        for bid, meta in cat.items():
            self.assertTrue(meta.get("title"), bid)
            self.assertTrue(meta.get("requires"), bid)
            self.assertTrue(set(meta["enforced_at"]) <= set(blocks.ENFORCE_POINTS), bid)

    def test_every_used_block_is_in_catalog_and_in_enforcement(self):
        used = blocks.used_blocks(self.pk)
        self.assertEqual(sorted(used), ["capability-probed", "discovery-result", "milestone-plan",
                                        "risk-plan-ready", "spec-ready"])
        for bid in used:
            self.assertIn(bid, blocks.catalog(self.pk))
            self.assertIn(bid, blocks.BLOCK_CHECKS)

    def test_catalog_and_enforcement_are_the_same_set(self):
        self.assertEqual(sorted(blocks.catalog(self.pk)), sorted(blocks.BLOCK_CHECKS))

    def test_repo_policy_has_no_catalog_defect(self):
        self.assertEqual(blocks.catalog_defects(self.pk), [])

    def test_route_still_computes_the_blocks_it_always_did(self):
        self.assertEqual(route(cls())["blocks"], ["spec-ready"])
        self.assertEqual(route(cls(unit="T2"))["blocks"], ["spec-ready", "milestone-plan"])
        self.assertIn("discovery-result", route(cls(unit="T1", mode="discovery"))["blocks"])
        self.assertIn("risk-plan-ready", route(cls(facets=["copy", "legal"], gates=["legal"]))["blocks"])

    def test_unknown_block_id_is_not_silently_satisfied(self):
        with self.assertRaises(KeyError):
            blocks.satisfied("no-such-block", ".", {}, "")


class TestCatalogMappingMismatch(unittest.TestCase):
    """카탈로그와 집행 매핑이 어긋나면 **정책 로드 자체가 실패한다** — 아무것도 막지 않는 차단을 다시 만들지 않는다."""

    def _harness(self, mutate=None):
        tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for rel in POLICY_FILES:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(HARNESS_ROOT / rel, root / rel)
        if mutate:
            path = root / "core/policy/packages.yaml"
            data = load_yaml(path)
            mutate(data)
            path.write_text(dump_yaml(data), encoding="utf-8")
        return root

    def test_unmutated_copy_loads(self):
        self.assertEqual(load_policy(self._harness())["version"], load_policy()["version"])

    def test_catalog_entry_without_enforcement_fails_the_load(self):
        def add_ghost(data):
            data["blocks"]["ghost-block"] = {"title": "유령", "enforced_at": ["close"], "requires": "없음"}
        with self.assertRaises(PolicyError) as ctx:
            load_policy(self._harness(add_ghost))
        self.assertIn("ghost-block", "\n".join(ctx.exception.args[0]))

    def test_used_block_missing_from_catalog_fails_the_load(self):
        def drop(data):
            del data["blocks"]["discovery-result"]
        with self.assertRaises(PolicyError) as ctx:
            load_policy(self._harness(drop))
        joined = "\n".join(ctx.exception.args[0])
        self.assertIn("discovery-result", joined)

    def test_missing_catalog_fails_the_load(self):
        def drop_all(data):
            del data["blocks"]
        with self.assertRaises(PolicyError):
            load_policy(self._harness(drop_all))

    def test_unknown_enforcement_point_fails_the_load(self):
        def bad_point(data):
            data["blocks"]["spec-ready"]["enforced_at"] = ["merge"]
        with self.assertRaises(PolicyError) as ctx:
            load_policy(self._harness(bad_point))
        self.assertIn("merge", "\n".join(ctx.exception.args[0]))

    def test_two_enforcement_points_fail_the_load(self):
        """막기 시작하는 사건은 하나다 — 일괄 배치는 이름과 실제를 갈라 놓는다."""
        def blanket(data):
            data["blocks"]["spec-ready"]["enforced_at"] = ["approve", "close"]
        with self.assertRaises(PolicyError) as ctx:
            load_policy(self._harness(blanket))
        self.assertIn("하나", "\n".join(ctx.exception.args[0]))

    def test_missing_reads_fails_the_load(self):
        """정본 입력 문서를 적지 않으면 무엇을 읽을지 정해지지 않는다."""
        def no_reads(data):
            data["blocks"]["spec-ready"].pop("reads")
        with self.assertRaises(PolicyError) as ctx:
            load_policy(self._harness(no_reads))
        self.assertIn("reads", "\n".join(ctx.exception.args[0]))


class TestApproveRejectsUnsatisfied(_Repo):
    """차단이 미충족이면 `romeo approve` 가 거부하고, 어느 차단이 무엇 때문에 막았는지 말한다."""

    def test_approval_gate_blocks_until_risk_section_is_filled(self):
        unit, files = self.make(cls(facets=["copy", "legal"], gates=["legal"]), "gate-block")
        spec = files["spec.md"]
        self.fill_spec(spec)
        self.unblank_section(spec, "위험·백업·복구")
        with self.assertRaises(ValueError) as ctx:
            approve_unit(unit, "tester", project_root=self.root)
        msg = str(ctx.exception)
        self.assertIn("risk-plan-ready", msg)
        self.assertIn("위험·백업·복구", msg)
        self.fill_doc(spec)
        self.assertEqual(approve_unit(unit, "tester", project_root=self.root)["status"], "active")

    def test_spec_ready_blocks_when_the_user_check_has_no_acceptance_criteria(self):
        unit, files = self.make(cls(), "no-ac")
        spec = files["spec.md"]
        self.fill_spec(spec)
        fm, body = frontmatter.read(spec)
        frontmatter.write(spec, fm, body.replace("  - [x] AC-1 채움\n", ""))
        with self.assertRaises(ValueError) as ctx:
            approve_unit(unit, "tester", project_root=self.root)
        self.assertIn("spec-ready", str(ctx.exception))
        self.assertIn("수용 기준", str(ctx.exception))

    def test_spec_ready_does_not_duplicate_the_required_check_verdict(self):
        """검증 계획이 비어 있는 것은 close 의 REQUIRED_CHECK(UNVERIFIED)가 판정한다 — 차단이 겹쳐 잡지 않는다."""
        unit, files = self.make(cls(), "no-plan")
        spec = files["spec.md"]
        self.fill_spec(spec)
        fm, body = frontmatter.read(spec)
        frontmatter.write(spec, fm, body.replace('  - id: check-1\n    command: "true"\n', ""))
        self.assertEqual(blocks.required_checks(frontmatter.read(spec)[1]), [])
        self.assertEqual(approve_unit(unit, "tester", project_root=self.root)["status"], "active")

    def test_plain_t0_still_approves(self):
        """차단 집행이 지금까지 통과하던 승인을 막지 않는다 — 회귀 대조."""
        unit, files = self.make(cls(), "plain")
        self.fill_spec(files["spec.md"])
        self.assertEqual(approve_unit(unit, "tester", project_root=self.root)["status"], "active")

    def test_message_names_every_unmet_block_at_once(self):
        unit, files = self.make(cls(unit="T2", mode="discovery"), "many")
        spec = files["spec.md"]
        self.fill_spec(spec)
        # spec-ready 도 함께 미충족으로 만든다 — 확인란은 채워져 있는데 수용 기준이 없는 모양이다
        # (NEEDS_INPUT 을 되돌리면 approve 가 차단 판정 **전에** 거부해 메시지가 하나만 나온다).
        fm, body = frontmatter.read(spec)
        frontmatter.write(spec, fm, re.sub(r"^\s*- \[[ xX]\] AC-1.*$", "  - (없음)", body, flags=re.M))
        with self.assertRaises(ValueError) as ctx:
            approve_unit(unit, "tester", project_root=self.root)
        msg = str(ctx.exception)
        self.assertIn("milestone-plan", msg)
        self.assertIn("spec-ready", msg)
        # discovery-result 는 승인이 아니라 위임에서 막는다 — 승인 메시지에 나오면 순환이다.
        self.assertNotIn("discovery-result", msg)


class TestDiscoveryResultNeedsInputs(_Repo):
    """`discovery-result` — 조사 산출물은 복사가 아니라 `inputs:` 링크로만 붙는다(K-62)."""

    def setUp(self):
        super().setUp()
        self.unit, self.files = self.make(cls(unit="T1", mode="discovery"), "discovery")
        self.spec = self.files["spec.md"]
        self.fill_spec(self.spec)

    def test_empty_inputs_does_not_block_approval(self):
        """조사 단위는 조사 결과 없이도 **승인은 된다** — 승인에서 막으면 조사를 시작할 창구가 없다."""
        fm = approve_unit(self.unit, "tester", project_root=self.root)
        self.assertEqual(fm["status"], "active")

    def test_empty_inputs_blocks_dispatch(self):
        approve_unit(self.unit, "tester", project_root=self.root)
        self.fill_package(self.files)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)
        with self.assertRaises(ValueError) as ctx:
            write_envelope(self.unit, "implementer", project_root=self.root, run_name="run-d")
        msg = str(ctx.exception)
        self.assertIn("discovery-result", msg)
        self.assertIn("inputs:", msg)
        self.assertIn("K-62", msg)
        self.assertFalse((Path(self.spec).parent / "task").exists(), "막혔는데 계약이 쓰였다")

    def test_blank_entries_do_not_count_as_inputs(self):
        self.set_inputs(self.research_doc(self.files), ["   ", ""])
        ok, why = blocks.satisfied("discovery-result", Path(self.spec).parent, {}, "",
                                   {"reads": "brief|charter"})
        self.assertFalse(ok)
        self.assertIn("inputs:", why)

    def test_a_link_to_a_path_that_does_not_exist_does_not_count(self):
        """그럴듯한 거짓 값 — 경로 모양이지만 없는 파일. 빈 값만 막는 검사는 이것을 통과시킨다."""
        self.set_inputs(self.research_doc(self.files), ["../../research/없는파일.md"], create=False)
        ok, why = blocks.satisfied("discovery-result", Path(self.spec).parent, {}, "",
                                   {"reads": "brief|charter"})
        self.assertFalse(ok)
        self.assertIn("없는파일", why)

    def test_a_string_that_is_not_a_path_does_not_count(self):
        self.set_inputs(self.research_doc(self.files), ["ㅁㄴㅇㄹ"], create=False)
        ok, why = blocks.satisfied("discovery-result", Path(self.spec).parent, {}, "",
                                   {"reads": "brief|charter"})
        self.assertFalse(ok)

    def test_a_link_on_the_spec_does_not_count(self):
        """정본은 조사 계획이 사는 문서다 — spec 에 붙인 링크로는 충족되지 않는다."""
        self.set_inputs(self.spec, ["../../research/x.md"])
        ok, _why = blocks.satisfied("discovery-result", Path(self.spec).parent, {}, "",
                                    {"reads": "brief|charter"})
        self.assertFalse(ok)

    def test_a_real_link_on_the_research_doc_counts(self):
        self.set_inputs(self.research_doc(self.files), ["../../research/2026-09-01-discord.md"])
        ok, why = blocks.satisfied("discovery-result", Path(self.spec).parent, {}, "",
                                   {"reads": "brief|charter"})
        self.assertTrue(ok, why)

    def test_delivery_unit_is_not_touched_by_this_block(self):
        unit, files = self.make(cls(unit="T1"), "delivery")
        self.fill_spec(files["spec.md"])
        self.assertNotIn("discovery-result", route(cls(unit="T1"))["blocks"])
        self.assertEqual(approve_unit(unit, "tester", project_root=self.root)["status"], "active")


class TestMilestonePlanNeedsCharter(_Repo):
    """`milestone-plan` — T2 는 charter.md 의 「마일스톤 계획」이 채워진 뒤에만 열린다."""

    def setUp(self):
        super().setUp()
        self.unit, self.files = self.make(cls(unit="T2"), "initiative")
        self.spec = self.files["spec.md"]
        self.fill_spec(self.spec)

    def test_charter_is_generated_with_a_milestone_section(self):
        charter = self.files["charter.md"]
        self.assertTrue(charter.is_file())
        self.assertIn("## 마일스톤 계획", charter.read_text(encoding="utf-8"))

    def test_unfilled_milestone_section_blocks_approval(self):
        with self.assertRaises(ValueError) as ctx:
            approve_unit(self.unit, "tester", project_root=self.root)
        msg = str(ctx.exception)
        self.assertIn("milestone-plan", msg)
        self.assertIn("마일스톤 계획", msg)

    def test_missing_charter_blocks_approval(self):
        self.files["charter.md"].unlink()
        with self.assertRaises(ValueError) as ctx:
            approve_unit(self.unit, "tester", project_root=self.root)
        self.assertIn("charter.md 가 없다", str(ctx.exception))

    def test_filled_milestone_section_unblocks_approval(self):
        self.fill_doc(self.files["charter.md"])
        self.assertEqual(approve_unit(self.unit, "tester", project_root=self.root)["status"], "active")

    def test_t1_has_no_charter_and_is_not_blocked(self):
        unit, files = self.make(cls(unit="T1"), "t1-no-charter")
        self.assertNotIn("charter.md", files)
        self.fill_spec(files["spec.md"])
        self.assertEqual(approve_unit(unit, "tester", project_root=self.root)["status"], "active")


class _Closable(_Repo):
    """승인 → 구현 커밋 → 증거까지 진행해 close 를 돌릴 수 있는 단위."""

    def prepare(self, classification, slug, before_approve=None):
        unit, files = self.make(classification, slug)
        spec = files["spec.md"]
        self.fill_spec(spec)
        self.fill_package(files)
        if before_approve:
            before_approve(spec, files)
        approve_unit(unit, "tester", project_root=self.root)
        (self.root / f"{slug}.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl", cwd=self.root)
        run_command(unit, "true", run_name="run-test", label="check-1", project_root=self.root)
        return unit, spec, files


class TestCloseReportsBlockSatisfied(_Closable):
    """`romeo close` 가 그 단위에 걸린 차단마다 `BLOCK_SATISFIED` 판정을 낸다."""

    @staticmethod
    def rows(result):
        return [c for c in result["checks"] if c["id"] == "BLOCK_SATISFIED"]

    def test_t0_close_reports_spec_ready_and_passes(self):
        unit, _spec, _files = self.prepare(cls(), "t0-close")
        res = close_unit(unit, project_root=self.root, dry_run=True)
        rows = self.rows(res)
        self.assertEqual(len(rows), 1, res["checks"])
        self.assertTrue(rows[0]["ok"], rows[0])
        self.assertIn("spec-ready", rows[0]["detail"])
        self.assertEqual(res["verdict"], "PASS", [c for c in res["checks"] if not c["ok"]])

    def test_every_block_on_the_unit_gets_a_row(self):
        def link(_spec, files):
            self.set_inputs(self.research_doc(files), ["../../research/x.md"])
        unit, _spec, _files = self.prepare(cls(unit="T1", mode="discovery"), "t1-close", before_approve=link)
        res = close_unit(unit, project_root=self.root, dry_run=True, rerun=False)
        got = sorted(r["detail"].split(":")[0] for r in self.rows(res))
        self.assertEqual(got, ["discovery-result", "spec-ready"])
        self.assertTrue(all(r["ok"] for r in self.rows(res)), self.rows(res))

    def test_close_fails_when_a_block_breaks_after_approval(self):
        def link(_spec, files):
            self.set_inputs(self.research_doc(files), ["../../research/x.md"])
        unit, spec, files = self.prepare(cls(unit="T1", mode="discovery"), "t1-break", before_approve=link)
        self.set_inputs(self.research_doc(files), [])
        res = close_unit(unit, project_root=self.root, dry_run=True, rerun=False)
        broken = [r for r in self.rows(res) if not r["ok"]]
        self.assertEqual(len(broken), 1, self.rows(res))
        self.assertIn("discovery-result", broken[0]["detail"])
        self.assertEqual(res["verdict"], "FAIL")


class TestNoRetroactiveEffect(_Closable):
    """차단은 소급하지 않는다 — 이미 done 인 단위를 다시 검사해도 판정과 문서가 그대로다."""

    def test_done_unit_keeps_its_verdict_and_document(self):
        unit, spec, _files = self.prepare(cls(), "retro")
        self.assertEqual(close_unit(unit, project_root=self.root)["verdict"], "PASS")
        self.assertEqual(frontmatter.read(spec)[0]["status"], "done")
        # 닫힌 뒤에 차단 조건을 무너뜨린다 — 확인란을 다시 비운다.
        self.unblank_section(spec, "확인란")
        before = spec.read_bytes()
        res = close_unit(unit, project_root=self.root, rerun=False)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertIn("NOT_ALREADY_DONE", [c["id"] for c in res["checks"] if not c["ok"]])
        self.assertEqual([c for c in res["checks"] if c["id"] == "BLOCK_SATISFIED"], [])
        self.assertEqual(res["updated"], [])
        self.assertEqual(spec.read_bytes(), before)

    def test_open_unit_still_gets_block_rows(self):
        """소급 금지가 '차단을 아무 데서도 보지 않는다' 가 되지 않았음을 대조한다."""
        unit, _spec, _files = self.prepare(cls(), "open")
        res = close_unit(unit, project_root=self.root, dry_run=True)
        self.assertTrue([c for c in res["checks"] if c["id"] == "BLOCK_SATISFIED"])


if __name__ == "__main__":
    unittest.main()
