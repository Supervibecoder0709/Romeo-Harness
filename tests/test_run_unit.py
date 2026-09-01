"""`romeo run-unit` — 관통 1회의 5단계와 **반복 중단 기준**(AGENTS.core §10).

반례 4건이 이 파일의 핵심이다. 중단 기준은 정당한 반복까지 막을 수 있으므로, 무엇이 막고 무엇이 막지 않는지가
코드가 아니라 여기 반례로 고정돼 있어야 한다.

  ① 연속 2회 실패가 기록돼 있으면 3회차 기동을 거부한다 (exit 1)
  ② `--after-review "<결론>"` 이 오면 그 결론을 기록하고 진행한다
  ③ 성공이 끼면 카운터가 0 으로 돌아간다 — 실패 2회여도 연속이 아니면 막지 않는다
  ④ `base_sha` 가 바뀌었다는 것은 리셋 사유가 아니다 — 같은 완료 정의를 다시 겨눈 시도다
"""
import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from romeo import frontmatter
from romeo.cli import main
from romeo.docs import approve_unit, create_unit
from romeo.policy import route
from romeo.run_unit import (CONSECUTIVE_FAILURE_LIMIT, STAGES, consecutive_failures, gate,
                            load_attempts, record_result, record_review, run_unit,
                            save_attempts, start_attempt)
from romeo.util import load_yaml

SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"
SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `README.md`"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          check=True).stdout.strip()


def _attempts(*results):
    """판정만 준 시도 목록. 회차 번호는 순서대로 매긴다."""
    return {"schema": "romeo/attempts@0.1.0", "unit_id": "u", "reviews": [],
            "attempts": [{"n": i, "run": f"run_{i}", "base_sha": "a" * 40, "result": r}
                         for i, r in enumerate(results, 1)]}


class TestStopRule(unittest.TestCase):
    """중단 기준의 계산만 본다 — 파일도 git 도 필요 없다."""

    def test_counter_counts_trailing_failures(self):
        self.assertEqual(consecutive_failures(_attempts()), 0)
        self.assertEqual(consecutive_failures(_attempts("fail")), 1)
        self.assertEqual(consecutive_failures(_attempts("fail", "fail")), 2)

    # ── 반례 ① 연속 2회 실패는 다음 기동을 막는다 ────────────────────────────
    def test_two_consecutive_failures_block(self):
        allowed, n, why = gate(_attempts("fail", "fail"))
        self.assertFalse(allowed)
        self.assertEqual(n, CONSECUTIVE_FAILURE_LIMIT)
        self.assertIn("재검토", why)

    # ── 반례 ③ 성공이 끼면 카운터가 0 으로 돌아간다 ──────────────────────────
    def test_success_resets_the_counter(self):
        self.assertEqual(consecutive_failures(_attempts("fail", "pass")), 0)
        self.assertTrue(gate(_attempts("fail", "pass"))[0])
        # 실패가 2건이어도 **연속**이 아니면 막지 않는다
        self.assertEqual(consecutive_failures(_attempts("fail", "pass", "fail")), 1)
        self.assertTrue(gate(_attempts("fail", "pass", "fail"))[0])
        # 성공 뒤에 다시 2연속 실패가 나면 그때는 막는다
        self.assertFalse(gate(_attempts("fail", "pass", "fail", "fail"))[0])

    # ── 반례 ④ base_sha 가 바뀌어도 리셋되지 않는다 ─────────────────────────
    def test_new_base_sha_does_not_reset_the_counter(self):
        data = _attempts("fail", "fail")
        data["attempts"][1]["base_sha"] = "b" * 40
        self.assertNotEqual(data["attempts"][0]["base_sha"], data["attempts"][1]["base_sha"])
        self.assertEqual(consecutive_failures(data), 2)
        self.assertFalse(gate(data)[0])

    # ── 반례 ② 재검토 기록이 해제한다 ────────────────────────────────────────
    def test_review_record_releases_the_gate(self):
        data = _attempts("fail", "fail")
        data["reviews"] = [{"after_attempt": 2, "conclusion": "완료 정의를 좁혔다", "by": "사람"}]
        # 재검토는 카운터를 **되돌리지 않는다** — 해제는 gate() 가 따로 판정한다(RepeatGate 참고)
        self.assertEqual(consecutive_failures(data), 2)
        self.assertTrue(gate(data)[0])
        # 해제 뒤에도 다시 2연속 실패가 쌓이면 또 막는다 — 한 번의 재검토가 영구 면제가 아니다
        data["attempts"] += [{"n": 3, "run": "run_3", "base_sha": "c" * 40, "result": "fail"},
                             {"n": 4, "run": "run_4", "base_sha": "c" * 40, "result": "fail"}]
        self.assertFalse(gate(data)[0])

    def test_unsettled_attempt_is_not_counted(self):
        data = _attempts("fail", "fail", "started")
        self.assertEqual(consecutive_failures(data), 2)


class _UnitRepo:
    """승인된 작업 단위 하나가 커밋돼 있는 임시 저장소. 계약 생성이 도는 최소 조건이다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        out = route({"unit": "T1", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        res = create_unit(out, "run-unit 테스트", "run-unit-t1", "관통 1회",
                          project_root=self.root, date="20260830")
        self.unit = res["id"]
        spec = Path(res["dir"]) / "spec.md"
        fm, body = frontmatter.read(spec)
        body = (body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
                    .replace('command: "채움"', 'command: "true"'))
        frontmatter.write(spec, fm, body)
        # 문서 패키지 **전체**를 채운다 — 위임 게이트가 spec 하나가 아니라 brief 까지 본다.
        # 이 helper 가 spec 만 채우던 것이 고치려는 결함과 같은 모양이었다(brief 를 아무도 읽지 않았다).
        for other in Path(res["dir"]).glob("*.md"):
            if other.name == "spec.md":
                continue
            ofm, obody = frontmatter.read(other)
            frontmatter.write(other, ofm, obody.replace("NEEDS_INPUT", "채움"))
        approve_unit(self.unit, "tester", project_root=self.root)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)
        self.base = git("rev-parse", "HEAD", cwd=self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, run="run_a", **kw):
        return run_unit(self.unit, project_root=self.root, run=run, base_sha=self.base, **kw)

    def _cli(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            code = main(list(argv))
        return code, buf.getvalue() + err.getvalue()


class TestRunUnit(_UnitRepo, unittest.TestCase):
    """실제 저장소 위에서 5단계와 중단 기준을 함께 본다."""

    # ── 5단계 ────────────────────────────────────────────────────────────────
    def test_dry_run_walks_five_stages_in_order(self):
        res = self._run()
        self.assertEqual(res["verdict"], "OK")
        self.assertEqual([s["stage"] for s in res["stages"]], [name for name, _ in STAGES])
        self.assertFalse(res["spawn"])

    def test_stage_one_actually_writes_both_contracts(self):
        res = self._run()
        udir = self.root / "docs/work" / self.unit
        for role in ("implementer", "reviewer"):
            path = udir / "task" / f"run_a-{role}.json"
            self.assertTrue(path.is_file(), f"{path} 가 없다")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["role"], role)
        self.assertEqual(res["base_sha"], self.base)

    def test_contracts_are_byte_identical_on_a_second_pass(self):
        self._run()
        path = self.root / "docs/work" / self.unit / "task" / "run_a-implementer.json"
        first = path.read_text(encoding="utf-8")
        self._run(run="run_a")
        self.assertEqual(first, path.read_text(encoding="utf-8"))

    def test_missing_envelopes_are_reported_as_waiting_not_as_pass(self):
        res = self._run()
        collect = next(s for s in res["stages"] if s["stage"] == "collect")
        self.assertEqual(collect["state"], "대기")
        self.assertEqual(len(collect["missing"]), 2)
        evidence = next(s for s in res["stages"] if s["stage"] == "evidence")
        self.assertEqual(evidence["state"], "대기")
        self.assertTrue(any("evidence checks" in c for _n, c in evidence["commands"]))

    def test_delegation_commands_are_printed_not_executed(self):
        res = self._run()
        delegate = next(s for s in res["stages"] if s["stage"] == "delegate")
        self.assertEqual(delegate["state"], "dry-run")
        self.assertTrue(delegate["commands"])
        self.assertNotIn("ran", delegate)

    def test_attempt_is_recorded_on_start(self):
        self._run()
        data = load_attempts(self.root, self.unit)
        self.assertEqual(len(data["attempts"]), 1)
        self.assertEqual(data["attempts"][0]["result"], "started")
        self.assertEqual(data["attempts"][0]["base_sha"], self.base)

    def test_record_settles_the_attempt(self):
        self._run(run="run_a")
        res = record_result(self.unit, "run_a", "fail", project_root=self.root,
                            failure_class="goal", note="완료 정의가 달성 불가")
        self.assertEqual(res["attempt"]["result"], "fail")
        self.assertEqual(res["attempt"]["failure_class"], "goal")
        self.assertEqual(res["consecutive_failures"], 1)
        data = load_yaml(self.root / "docs/work" / self.unit / "attempts.yaml")
        self.assertEqual(data["attempts"][0]["note"], "완료 정의가 달성 불가")

    def test_record_without_a_started_attempt_is_refused(self):
        with self.assertRaises(ValueError):
            record_result(self.unit, "run_없음", "pass", project_root=self.root)

    # ── 반례 ①·② 실제 실행 경로에서 ────────────────────────────────────────
    def test_third_attempt_is_refused_after_two_failures(self):
        for run in ("run_a", "run_b"):
            self._run(run=run)
            record_result(self.unit, run, "fail", project_root=self.root)
        res = self._run(run="run_c")
        self.assertEqual(res["verdict"], "BLOCKED_REPEAT")
        self.assertEqual(res["stages"], [])
        # 거부된 기동은 계약을 만들지도, 시도를 늘리지도 않는다
        self.assertFalse((self.root / "docs/work" / self.unit / "task" / "run_c-implementer.json").is_file())
        self.assertEqual(len(load_attempts(self.root, self.unit)["attempts"]), 2)

    def test_after_review_releases_and_is_recorded(self):
        for run in ("run_a", "run_b"):
            self._run(run=run)
            record_result(self.unit, run, "fail", project_root=self.root)
        res = self._run(run="run_c", after_review="완료 정의를 좁혔다", by="사람")
        self.assertEqual(res["verdict"], "OK")
        self.assertTrue(res["released_by_review"])
        data = load_attempts(self.root, self.unit)
        self.assertEqual(data["reviews"][-1]["conclusion"], "완료 정의를 좁혔다")
        self.assertEqual(data["reviews"][-1]["by"], "사람")
        self.assertEqual(data["reviews"][-1]["after_attempt"], 2)

    # ── 반례 ④ base_sha 를 바꾸는 것으로는 풀 수 없다 ───────────────────────
    def test_changing_base_sha_does_not_unblock(self):
        for run in ("run_a", "run_b"):
            self._run(run=run)
            record_result(self.unit, run, "fail", project_root=self.root)
        (self.root / "README.md").write_text("moved\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "move", cwd=self.root)
        new_base = git("rev-parse", "HEAD", cwd=self.root)
        self.assertNotEqual(new_base, self.base)
        res = run_unit(self.unit, project_root=self.root, run="run_c", base_sha=new_base)
        self.assertEqual(res["verdict"], "BLOCKED_REPEAT")

    # ── CLI 종료 코드 ────────────────────────────────────────────────────────
    def test_cli_exits_1_when_blocked_and_0_otherwise(self):
        code, out = self._cli("run-unit", "--unit", self.unit, "--run", "run_a",
                              "--base-sha", self.base, "--root", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("[1/5]", out)
        self.assertIn("[5/5]", out)
        self._cli("run-unit", "record", "--unit", self.unit, "--run", "run_a",
                  "--result", "fail", "--root", str(self.root))
        code, _ = self._cli("run-unit", "--unit", self.unit, "--run", "run_b",
                            "--base-sha", self.base, "--root", str(self.root))
        self.assertEqual(code, 0)
        self._cli("run-unit", "record", "--unit", self.unit, "--run", "run_b",
                  "--result", "fail", "--root", str(self.root))
        code, out = self._cli("run-unit", "--unit", self.unit, "--run", "run_c",
                              "--base-sha", self.base, "--root", str(self.root))
        self.assertEqual(code, 1, out)
        self.assertIn("BLOCKED_REPEAT", out)
        code, out = self._cli("run-unit", "--unit", self.unit, "--run", "run_c",
                              "--base-sha", self.base, "--root", str(self.root),
                              "--after-review", "완료 정의를 좁혔다")
        self.assertEqual(code, 0, out)

    def test_help_exits_zero(self):
        with self.assertRaises(SystemExit) as cm:
            self._cli("run-unit", "--help")
        self.assertEqual(cm.exception.code, 0)


class RepeatGate(_UnitRepo, unittest.TestCase):
    """브레이크가 실제로 걸리는가 — 재검토가 카운터를 리셋하지 않고, 게이트가 **모든 관통의 입구**에 선다.

    두 결함이 이 클래스의 이유다(2026-08-31 실측).

      ③ 실패 1·2 → 재검토 → 실패 3 이면 카운터가 1 로 돌아가 4회차가 재검토 없이 돌았다.
        재검토는 그 시점까지를 한 번 통과시키는 것이지 실패를 없애는 것이 아니다.
      Ⓔ 게이트를 부르는 곳이 `run_unit()` 하나뿐이라 RUNBOOK §3 을 손으로 관통하면 한 번도 평가되지 않았다.
        계약 생성(`envelope build`)은 어느 경로로 돌리든 반드시 지나는 자리다.
    """

    def _build(self, run="run_x"):
        return self._cli("envelope", "build", "--unit", self.unit, "--role", "implementer",
                         "--run", run, "--base-sha", self.base, "--root", str(self.root))

    def _write_attempts(self, *results, reviews=None):
        data = _attempts(*results)
        data["unit_id"] = self.unit
        data["reviews"] = reviews or []
        save_attempts(self.root, self.unit, data)

    def _task(self, run):
        return self.root / "docs/work" / self.unit / "task" / f"{run}-implementer.json"

    # ── ③ 재검토는 카운터를 리셋하지 않는다 ──────────────────────────────────
    def test_review_does_not_reset_counter(self):
        data = _attempts("fail", "fail")
        data["reviews"] = [{"after_attempt": 2, "conclusion": "완료 정의를 좁혔다", "by": "사람"}]
        # 재검토 직후는 통과한다 — 사람이 그 시점까지를 봤다
        self.assertTrue(gate(data)[0])
        # 그 뒤 실패가 **하나만 더** 쌓여도 다시 막힌다. 종전에는 카운터가 1 로 돌아가 4회차까지 돌았다
        data["attempts"].append({"n": 3, "run": "run_3", "base_sha": "c" * 40, "result": "fail"})
        self.assertEqual(consecutive_failures(data), 3, "재검토는 실패를 지우지 않는다")
        allowed, n, why = gate(data)
        self.assertFalse(allowed, "재검토 뒤 실패 1회로 다시 막혀야 한다")
        self.assertEqual(n, 3)
        self.assertIn("재검토", why)

    # ── ③ 성공은 여전히 리셋한다 ────────────────────────────────────────────
    def test_pass_resets_counter(self):
        data = _attempts("fail", "fail", "pass", "fail")
        self.assertEqual(consecutive_failures(data), 1, "성공 뒤의 실패 1회만 센다")
        self.assertTrue(gate(data)[0], "성공이 끼면 그 다음 실패 1회로는 막지 않는다")
        # 성공 뒤에 다시 2연속이 쌓이면 그때는 막는다 — 리셋이 면제가 아니다
        data["attempts"].append({"n": 5, "run": "run_5", "base_sha": "a" * 40, "result": "fail"})
        self.assertFalse(gate(data)[0])

    # ── Ⓔ 차단이면 계약을 만들지 않는다 ─────────────────────────────────────
    def test_envelope_build_refuses_when_blocked(self):
        self._write_attempts("fail", "fail")
        code, out = self._build()
        self.assertEqual(code, 1, out)
        self.assertIn("반복 중단", out)
        self.assertIn("연속 2회 실패", out)
        # 무엇을 해야 푸는지 한국어로 말한다
        self.assertIn("재검토", out)
        self.assertIn("--after-review", out)
        # 차단된 기동은 계약을 남기지 않는다
        self.assertFalse(self._task("run_x").is_file())

    # ── Ⓔ 안 걸린 경우엔 그대로 동작한다 ────────────────────────────────────
    def test_envelope_build_allows_when_not_blocked(self):
        # ① 시도 기록이 아예 없는 단위 — 지금 대부분이 그 상태다
        self.assertFalse((self.root / "docs/work" / self.unit / "attempts.yaml").is_file())
        code, out = self._build(run="run_none")
        self.assertEqual(code, 0, out)
        self.assertTrue(self._task("run_none").is_file())
        # ② 마지막이 pass 인 단위 — 성공이 카운터를 되돌렸다
        self._write_attempts("fail", "fail", "pass")
        code, out = self._build(run="run_pass")
        self.assertEqual(code, 0, out)
        self.assertTrue(self._task("run_pass").is_file())

    def test_a_released_attempt_can_rebuild_its_own_contract(self):
        """재검토로 해제한 회차는 **자기 계약을 다시 만들 수 있어야** 한다.

        진행 중(started)인 시도까지 재검토가 덮어야 할 대상으로 세면, `--after-review` 로 막 연 3회차의
        워커가 계약을 다시 만들려는 순간 자기 자신에게 막힌다 — 입구에 선 게이트에서 그것은 교착이다."""
        self._write_attempts("fail", "fail",
                             reviews=[{"after_attempt": 2, "conclusion": "좁혔다", "by": "사람"}])
        data = load_attempts(self.root, self.unit)
        start_attempt(data, "run_third", self.base)
        save_attempts(self.root, self.unit, data)
        code, out = self._build(run="run_third")
        self.assertEqual(code, 0, out)

    def test_after_review_through_run_unit_still_walks_the_stages(self):
        """게이트를 입구에 걸어도 `run-unit --after-review` 경로가 그대로 돈다.

        1단계(계약 생성)가 같은 게이트를 다시 지나므로, 재검토는 그 전에 디스크에 남아야 한다."""
        for run in ("run_a", "run_b"):
            self._run(run=run)
            record_result(self.unit, run, "fail", project_root=self.root)
        res = self._run(run="run_c", after_review="완료 정의를 좁혔다", by="사람")
        self.assertEqual(res["verdict"], "OK")
        self.assertTrue(res["released_by_review"])
        self.assertTrue(self._task("run_c").is_file())


class TestReviewOnlyRecord(_UnitRepo, unittest.TestCase):
    """재검토를 **기록만** 하는 경로 (Q-25).

    종전에는 반복 중단을 푸는 창구가 `run-unit start --after-review` 하나뿐이라, 재검토를 남기는 일이
    언제나 attempt 를 하나 함께 만들었다. 그 기록은 커밋돼야 워크트리 안의 계약 생성이 보고(D-a),
    커밋하면 HEAD 가 밀려 계약을 새 SHA 로 다시 만들어야 하므로 attempt 가 또 하나 생긴다 —
    2026-08-31 실측으로 `started` 유령이 세 개 남았다.

    이 클래스가 고정하는 것은 둘이다.
      ① 기록 전용 경로는 **시도 항목 수를 늘리지 않는다**
      ② 그 경로가 **브레이크를 우회하지 않는다** — 카운터는 그대로고, 실패가 하나 더 쌓이면 다시 막힌다
    """

    def _fail_twice(self):
        for run in ("run_a", "run_b"):
            self._run(run=run)
            record_result(self.unit, run, "fail", project_root=self.root)
        return load_attempts(self.root, self.unit)

    # ── ① 시도를 시작하지 않는다 ─────────────────────────────────────────────
    def test_review_only_record_does_not_start_an_attempt(self):
        before = self._fail_twice()
        self.assertEqual(len(before["attempts"]), 2)
        res = record_review(self.unit, "완료 정의를 좁혔다", project_root=self.root, by="사람")
        after = load_attempts(self.root, self.unit)
        self.assertEqual(len(after["attempts"]), 2, "기록 전용 경로가 시도를 늘렸다")
        self.assertEqual(res["attempts"], 2)
        self.assertEqual([a["result"] for a in after["attempts"]], ["fail", "fail"])

    def test_the_conclusion_is_recorded_with_who_and_how_far(self):
        self._fail_twice()
        record_review(self.unit, "완료 정의를 좁혔다", project_root=self.root, by="사람")
        rv = load_attempts(self.root, self.unit)["reviews"][-1]
        self.assertEqual(rv["conclusion"], "완료 정의를 좁혔다")
        self.assertEqual(rv["by"], "사람")
        self.assertEqual(rv["after_attempt"], 2)
        self.assertTrue(rv["at"])

    def test_it_works_on_a_unit_with_no_attempts_yet(self):
        res = record_review(self.unit, "먼저 재검토했다", project_root=self.root, by="사람")
        self.assertEqual(res["attempts"], 0)
        self.assertEqual(load_attempts(self.root, self.unit)["attempts"], [])

    # ── ② 브레이크를 우회하지 않는다 ─────────────────────────────────────────
    def test_it_releases_the_gate_but_does_not_reset_the_counter(self):
        self._fail_twice()
        self.assertFalse(gate(load_attempts(self.root, self.unit))[0])
        res = record_review(self.unit, "완료 정의를 좁혔다", project_root=self.root, by="사람")
        data = load_attempts(self.root, self.unit)
        self.assertTrue(res["released"])
        self.assertTrue(gate(data)[0])
        self.assertEqual(consecutive_failures(data), 2, "재검토는 실패를 지우지 않는다")
        self.assertEqual(res["consecutive_failures"], 2)

    def test_one_more_failure_blocks_again(self):
        """한 번의 재검토는 그 시점까지의 면제다 — 자동 해제 장치가 아니다."""
        self._fail_twice()
        record_review(self.unit, "완료 정의를 좁혔다", project_root=self.root, by="사람")
        self._run(run="run_c")
        record_result(self.unit, "run_c", "fail", project_root=self.root)
        data = load_attempts(self.root, self.unit)
        self.assertEqual(consecutive_failures(data), 3)
        allowed, _n, why = gate(data)
        self.assertFalse(allowed, "재검토 뒤 실패 1회로 다시 막혀야 한다")
        self.assertIn("재검토", why)

    def test_the_released_gate_lets_the_next_start_run(self):
        """기록만 한 뒤에 기동하면 그 회차가 정상으로 돈다 — 계약 생성도 같은 게이트를 지난다."""
        self._fail_twice()
        record_review(self.unit, "완료 정의를 좁혔다", project_root=self.root, by="사람")
        res = self._run(run="run_c")
        self.assertEqual(res["verdict"], "OK")
        self.assertFalse(res["released_by_review"], "해제는 이미 디스크의 기록이 했다")
        self.assertEqual(len(load_attempts(self.root, self.unit)["attempts"]), 3)

    # ── CLI ──────────────────────────────────────────────────────────────────
    def test_cli_review_needs_no_run_and_adds_no_attempt(self):
        self._fail_twice()
        code, out = self._cli("run-unit", "review", "--unit", self.unit,
                              "--after-review", "완료 정의를 좁혔다", "--by", "사람",
                              "--root", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertEqual(len(load_attempts(self.root, self.unit)["attempts"]), 2, out)
        self.assertEqual(load_attempts(self.root, self.unit)["reviews"][-1]["by"], "사람")

    def test_cli_review_without_a_conclusion_is_refused(self):
        code, out = self._cli("run-unit", "review", "--unit", self.unit, "--root", str(self.root))
        self.assertEqual(code, 2, out)
        self.assertEqual(load_attempts(self.root, self.unit)["reviews"], [])

    def test_cli_start_still_requires_a_run(self):
        """--run 을 옵션으로 바꾼 것이 start·record 의 요구를 풀지 않는다."""
        code, out = self._cli("run-unit", "--unit", self.unit, "--base-sha", self.base,
                              "--root", str(self.root))
        self.assertEqual(code, 2, out)
        self.assertIn("--run", out)
        code, out = self._cli("run-unit", "record", "--unit", self.unit, "--result", "fail",
                              "--root", str(self.root))
        self.assertEqual(code, 2, out)


if __name__ == "__main__":
    unittest.main()
