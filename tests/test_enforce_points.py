"""집행 지점 어휘·차단 충족 조건·절 로드 대조 — `feat-20260901-enforce-point-alignment-9dfq`.

**반례는 빈 값이 아니라 그럴듯한 거짓 값이다.** 「빈칸이면 막힌다」만 증명한 검사는 고치기 전 상태와
구별되지 않는다 — 고치기 전에도 빈 값은 막혔고, 통과한 것은 `"ㅁㄴㅇㄹ"` 같은 **있는 척하는 값**이었다.
그래서 이 파일의 반례는 전부 형태가 그럴듯하고 내용이 거짓인 값이다.
"""
import copy
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from romeo import HARNESS_ROOT, blocks, frontmatter
from romeo.close import close_unit
from romeo.docs import approve_unit, create_unit
from romeo.envelope import write_envelope
from romeo.evidence import run_command
from romeo.policy import PolicyError, load_policy, load_project_state, route
from romeo.run_unit import load_attempts
from romeo.util import dump_yaml, load_yaml

#: 그럴듯한 거짓 값 셋. 셋 다 고치기 전에는 통과했다(2026-09-01 실측).
NOT_A_PATH = "ㅁㄴㅇㄹ"
MISSING_PATH = "docs/research/없는파일.md"
NOT_A_SPIKE = "spike 없이 곧바로 전체 구현한다"

DISCOVERY_FX = HARNESS_ROOT / "fixtures/requests/fx-discord-computer-use-automation.yaml"
SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"
SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `impl.txt`"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


class _Repo(unittest.TestCase):
    """임시 저장소에 discovery 단위 하나를 세운다. 저장소의 docs/work 를 건드리지 않는다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        fx = load_yaml(DISCOVERY_FX)
        out = route(fx["classification"], project_state=load_project_state(HARNESS_ROOT))
        res = create_unit(out, fx["id"], "enforce", fx["request_text"][:60],
                          project_root=self.root, date="20260901")
        self.unit = res["id"]
        self.files = {Path(f).name: Path(f) for f in res["files"]}
        self.udir = Path(res["dir"])

    def tearDown(self):
        self.tmp.cleanup()

    def fill_spec(self):
        spec = self.files["spec.md"]
        fm, body = frontmatter.read(spec)
        frontmatter.write(spec, fm, (body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
                                         .replace('command: "채움"', 'command: "true"')
                                         .replace("- [ ] AC-1", "- [x] AC-1")))

    def fill_brief(self, spike="채움"):
        brief = self.files["brief.md"]
        fm, body = frontmatter.read(brief)
        body = body.replace("**첫 마일스톤(spike):** NEEDS_INPUT", f"**첫 마일스톤(spike):** {spike}")
        frontmatter.write(brief, fm, body.replace("NEEDS_INPUT", "채움"))

    def set_inputs(self, doc, items, create=True):
        fm, body = frontmatter.read(doc)
        fm["inputs"] = list(items)
        frontmatter.write(doc, fm, body)
        if create:
            for it in items:
                target = (Path(doc).parent / str(it).split("#")[0]).resolve()
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("조사 결과(테스트)\n", encoding="utf-8")

    def ready(self, spike="채움"):
        self.fill_spec()
        self.fill_brief(spike=spike)

    def approve_and_commit(self):
        approve_unit(self.unit, "tester", project_root=self.root)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)

    def make_evidence(self):
        """close 가 NO_OPEN_LOOP 까지 가려면 증거가 있어야 한다 — 그 앞에서 HAS_EVIDENCE 로 멈춘다."""
        (self.root / "impl.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl", cwd=self.root)
        run_command(self.unit, "true", run_name="run-e", label="check-1", project_root=self.root)

    def dispatch(self, run="run-e1", role="implementer"):
        return write_envelope(self.unit, role, project_root=self.root, run_name=run)

    def discovery_verdict(self):
        return blocks.satisfied("discovery-result", self.udir, {}, "", {"reads": "brief|charter"})


class TestDispatchPoint(_Repo):
    """`dispatch` — 조사 단위는 승인까지 열리고 **구현 위임**에서 막힌다."""

    def test_dispatch_is_an_enforcement_point(self):
        self.assertIn("dispatch", blocks.ENFORCE_POINTS)

    def test_every_block_declares_exactly_one_blocking_event(self):
        for bid, meta in blocks.catalog(load_policy()["packages"]).items():
            self.assertEqual(len(meta["enforced_at"]), 1, f"{bid}: {meta['enforced_at']}")

    def test_every_block_declares_the_document_it_reads(self):
        for bid, meta in blocks.catalog(load_policy()["packages"]).items():
            self.assertTrue(meta.get("reads"), bid)
            for name in str(meta["reads"]).split("|"):
                self.assertIn(name.strip(), blocks.DOC_FILES, bid)

    def test_discovery_result_blocks_dispatch_not_approval(self):
        self.ready()
        approve_unit(self.unit, "tester", project_root=self.root)   # 승인은 열린다
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)
        with self.assertRaises(ValueError) as ctx:
            self.dispatch()
        self.assertIn("discovery-result", str(ctx.exception))

    def test_a_blocked_dispatch_writes_no_contract(self):
        self.ready()
        self.approve_and_commit()
        with self.assertRaises(ValueError):
            self.dispatch()
        self.assertFalse((self.udir / "task").exists())

    def test_dispatch_opens_once_the_research_link_is_real(self):
        self.ready()
        self.set_inputs(self.files["brief.md"], ["../../research/real.md"])
        self.approve_and_commit()
        self.assertTrue(Path(self.dispatch()["path"]).is_file())


class TestDiscoveryResultReadsRealPath(_Repo):
    """충족은 '그 자리에 글자가 있는가' 가 아니라 '그 문장이 참인가' 다."""

    def setUp(self):
        super().setUp()
        self.ready()

    def test_a_string_that_is_not_a_path_does_not_count(self):
        self.set_inputs(self.files["brief.md"], [NOT_A_PATH], create=False)
        ok, _why = self.discovery_verdict()
        self.assertFalse(ok, f"{NOT_A_PATH!r} 이 조사 결과로 셌다")

    def test_a_path_shaped_string_that_does_not_exist_does_not_count(self):
        self.set_inputs(self.files["brief.md"], [f"../../{MISSING_PATH}"], create=False)
        ok, why = self.discovery_verdict()
        self.assertFalse(ok)
        self.assertIn("없는파일", why)

    def test_a_real_path_counts(self):
        self.set_inputs(self.files["brief.md"], ["../../research/real.md"])
        ok, why = self.discovery_verdict()
        self.assertTrue(ok, why)

    def test_the_spec_is_not_the_canonical_input_document(self):
        """계획은 조사 결과를 Brief 에 붙이라고 한다 — spec 에 붙인 것으로 열리면 두 문서가 갈라진다."""
        self.set_inputs(self.files["spec.md"], ["../../research/real.md"])
        ok, _why = self.discovery_verdict()
        self.assertFalse(ok)

    def test_a_url_is_allowed_but_said_to_be_unverified(self):
        self.set_inputs(self.files["brief.md"], ["https://example.com/조사"], create=False)
        ok, why = self.discovery_verdict()
        self.assertTrue(ok, why)
        self.assertIn("바깥 주소", why)

    def test_a_mailto_is_not_a_research_output(self):
        """확인할 수 없는 것과 확인할 필요가 없는 것을 같이 두면 구멍이 넓어진다."""
        self.set_inputs(self.files["brief.md"], ["mailto:someone@example.com"], create=False)
        ok, _why = self.discovery_verdict()
        self.assertFalse(ok)

    def test_one_bad_link_among_good_ones_still_blocks(self):
        self.set_inputs(self.files["brief.md"], ["../../research/real.md"])
        self.set_inputs(self.files["brief.md"], ["../../research/real.md", NOT_A_PATH], create=False)
        ok, _why = self.discovery_verdict()
        self.assertFalse(ok)


class TestOpenLoopCoversPackage(_Repo):
    """미완료 검사는 spec 하나가 아니라 문서 패키지 전체를 본다."""

    def test_an_unfilled_brief_blocks_dispatch(self):
        self.fill_spec()
        self.set_inputs(self.files["brief.md"], ["../../research/real.md"])
        self.approve_and_commit()
        with self.assertRaises(ValueError) as ctx:
            self.dispatch()
        self.assertIn("brief.md", str(ctx.exception))

    def test_spike_ness_is_the_reviewers_call_not_the_machines(self):
        """**경계를 명시적으로 고정한다.** 기계는 「첫 마일스톤(spike)」 칸이 채워졌는지까지만 본다.
        그 값이 실제로 spike 인지는 의미 판단이라 기계가 판별할 수 없다 —
        낱말로 거르려 해도 `"spike 없이 곧바로 전체 구현한다"` 에 그 낱말이 들어 있다.
        이것을 기계 반례로 약속했다가 1회차 검토자에게 잡혔고, AC-9 에서 그 약속을 뺐다.
        경계를 검사로 적어 두지 않으면 다음 사람이 같은 약속을 다시 한다."""
        self.ready(spike=NOT_A_SPIKE)
        self.set_inputs(self.files["brief.md"], ["../../research/real.md"])
        self.approve_and_commit()
        self.assertTrue(Path(self.dispatch()["path"]).is_file())
        self.assertIn(NOT_A_SPIKE, self.files["brief.md"].read_text(encoding="utf-8"))

    def test_close_also_reads_the_whole_package(self):
        self.ready()
        self.set_inputs(self.files["brief.md"], ["../../research/real.md"])
        self.approve_and_commit()
        self.make_evidence()
        fm, body = frontmatter.read(self.files["brief.md"])
        frontmatter.write(self.files["brief.md"], fm, body + "\n- 남은 칸: NEEDS_INPUT\n")
        res = close_unit(self.unit, project_root=self.root, dry_run=True, rerun=False)
        bad = [c for c in res["checks"] if c["id"] == "NO_OPEN_LOOP" and not c["ok"]]
        self.assertTrue(bad, res["checks"])
        self.assertIn("brief.md", bad[0]["detail"])

    def test_a_filled_package_has_no_open_loop(self):
        self.ready()
        self.set_inputs(self.files["brief.md"], ["../../research/real.md"])
        self.approve_and_commit()
        self.make_evidence()
        res = close_unit(self.unit, project_root=self.root, dry_run=True, rerun=False)
        rows = [c for c in res["checks"] if c["id"] == "NO_OPEN_LOOP"]
        self.assertTrue(all(c["ok"] for c in rows), rows)


class _PolicyRepo(unittest.TestCase):
    """정책표를 한 곳만 바꾼 하네스 사본으로 로드를 시도한다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name) / "harness"
        (self.root / "core/policy").mkdir(parents=True)
        (self.root / "core/schemas").mkdir(parents=True)
        for rel in ("core/policy/classification.yaml", "core/policy/packages.yaml",
                    "core/policy/execution-guards.yaml", "core/schemas/fixture.json"):
            (self.root / rel).write_bytes((HARNESS_ROOT / rel).read_bytes())

    def tearDown(self):
        self.tmp.cleanup()

    def mutate(self, fn):
        data = load_yaml(self.root / "core/policy/packages.yaml")
        fn(data)
        (self.root / "core/policy/packages.yaml").write_text(dump_yaml(data), encoding="utf-8")
        return self.root


class TestSectionEnforcementReconciliation(_PolicyRepo):
    """라우터가 요구할 수 있는 절과 집행이 읽는 문서를 **로드 시점에** 맞춰 본다."""

    def test_the_repo_policy_has_no_section_defect(self):
        self.assertEqual(blocks.section_defects(load_policy()["packages"]), [])

    def test_a_section_without_an_enforcement_declaration_fails_the_load(self):
        root = self.mutate(lambda d: d["sections"]["discovery-plan"].pop("enforcement"))
        with self.assertRaises(PolicyError) as ctx:
            load_policy(root)
        self.assertIn("discovery-plan", "\n".join(ctx.exception.args[0]))

    def test_an_unknown_enforcement_value_fails_the_load(self):
        root = self.mutate(lambda d: d["sections"]["discovery-plan"].__setitem__("enforcement", ["나중에"]))
        with self.assertRaises(PolicyError) as ctx:
            load_policy(root)
        self.assertIn("나중에", "\n".join(ctx.exception.args[0]))

    def test_a_block_that_does_not_read_the_section_document_fails_the_load(self):
        """가장 그럴듯한 거짓 값 — 선언은 있는데 그 차단이 그 문서를 읽지 않는다."""
        def wrong(d):
            d["sections"]["discovery-plan"]["enforcement"] = ["open-loop", "block:milestone-plan"]
        with self.assertRaises(PolicyError) as ctx:
            load_policy(self.mutate(wrong))
        joined = "\n".join(ctx.exception.args[0])
        self.assertIn("discovery-plan", joined)
        self.assertIn("읽지 않는", joined)

    def test_a_block_that_is_not_in_the_catalog_fails_the_load(self):
        def ghost(d):
            d["sections"]["discovery-plan"]["enforcement"] = ["block:없는차단"]
        with self.assertRaises(PolicyError) as ctx:
            load_policy(self.mutate(ghost))
        self.assertIn("없는차단", "\n".join(ctx.exception.args[0]))

    def test_advisory_is_an_explicit_decision_not_an_omission(self):
        """아무도 읽지 않는다고 **적는** 것은 통과한다 — 적지 않아서 아무도 안 읽는 것과 다르다."""
        def advisory(d):
            d["sections"]["discovery-plan"]["enforcement"] = ["advisory"]
        load_policy(self.mutate(advisory))


class TestHandRunRecordsAttempt(_Repo):
    """손으로 위임 절차를 밟아도 회차가 남는다 — 반복 중단이 그 경로에서도 센다(Q-27)."""

    def setUp(self):
        super().setUp()
        self.ready()
        self.set_inputs(self.files["brief.md"], ["../../research/real.md"])
        self.approve_and_commit()

    def test_writing_a_contract_records_the_attempt(self):
        self.dispatch(run="run-hand")
        runs = [a["run"] for a in load_attempts(self.root, self.unit)["attempts"]]
        self.assertEqual(runs, ["run-hand"])

    def test_two_role_contracts_are_one_attempt(self):
        self.dispatch(run="run-hand", role="implementer")
        self.dispatch(run="run-hand", role="reviewer")
        self.assertEqual(len(load_attempts(self.root, self.unit)["attempts"]), 1)

    def test_a_second_run_is_a_second_attempt(self):
        self.dispatch(run="run-a")
        self.dispatch(run="run-b")
        self.assertEqual([a["run"] for a in load_attempts(self.root, self.unit)["attempts"]],
                         ["run-a", "run-b"])

    def test_the_attempt_carries_the_base_sha_of_the_contract(self):
        res = self.dispatch(run="run-hand")
        att = load_attempts(self.root, self.unit)["attempts"][0]
        self.assertEqual(att["base_sha"], res["envelope"]["base_sha"])
        self.assertEqual(att["result"], "started")


if __name__ == "__main__":
    unittest.main()


class TestClosureMatchesCode(unittest.TestCase):
    """닫힘으로 표시한 질문의 **해소문이 코드와 같은 말을 하는가.**

    취소선이 있는지만 보는 검사는 내용이 반대인 해소문을 통과시킨다 — 2회차 검토자가 그것을 잡았다.
    `mailto:` 를 코드에서는 막으면서 park 기록에는 「통과시킨다」 고 적어 둔 상태가 exit 0 이었다.
    **그 자리에 글자가 있는지가 아니라 그 문장이 참인지를 본다**(§11) — 이 단위가 차단에 적용한 규칙을
    이 단위의 검증 계획 자신에게도 적용한다.

    각 항목은 `(질문 id, 해소문에 있어야 하는 문장, 코드가 그렇게 도는지 확인하는 함수)` 다.
    문장만 맞고 코드가 다르거나, 코드만 맞고 문장이 다르면 둘 다 실패한다."""

    QUESTIONS = ("Q-27", "Q-28", "Q-29", "Q-30", "Q-31")

    #: 해소문이 주장하는 것 ↔ 그 주장이 참인지 실행으로 보는 것
    CLAIMS = (
        ("Q-29", "**`mailto:` 는 막는다**",
         lambda: blocks.URL_RE.match("mailto:someone@example.com") is None),
        ("Q-28", "dispatch",
         lambda: blocks.catalog(load_policy()["packages"])["discovery-result"]["enforced_at"] == ["dispatch"]),
        ("Q-31", "guards",
         lambda: "guards" in (blocks.catalog(load_policy()["packages"])["risk-plan-ready"].get("note") or "")),
    )

    def setUp(self):
        self.rows = {}
        for line in (HARNESS_ROOT / "docs/planning/open-questions.md").read_text(encoding="utf-8").split("\n"):
            for qid in self.QUESTIONS:
                if line.startswith(f"| {qid} |"):
                    self.rows[qid] = line

    def test_every_closed_question_has_a_row(self):
        self.assertEqual(sorted(self.rows), sorted(self.QUESTIONS))

    def test_every_closed_question_is_struck_through(self):
        for qid, row in self.rows.items():
            self.assertIn("~~", row, qid)

    def test_every_closed_question_names_the_unit_that_closed_it(self):
        for qid, row in self.rows.items():
            self.assertIn("해소(2026-09-01", row, qid)

    def test_the_closure_text_says_what_the_code_does(self):
        for qid, phrase, predicate in self.CLAIMS:
            with self.subTest(qid=qid):
                self.assertIn(phrase, self.rows[qid], f"{qid} 의 해소문에 {phrase!r} 가 없다")
                self.assertTrue(predicate(), f"{qid} 의 해소문은 그렇게 적었는데 코드는 다르게 돈다")
