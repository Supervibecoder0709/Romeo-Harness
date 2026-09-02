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
import re
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from romeo import HARNESS_ROOT, frontmatter
from romeo.cli import main
from romeo.docs import approve_unit, create_unit
from romeo.envelope import write_envelope
from romeo.policy import route
from romeo.run_unit import (CONSECUTIVE_FAILURE_LIMIT, STAGES, consecutive_failures, delegation_commands, gate,
                            load_attempts, record_result, record_review, run_unit,
                            save_attempts, start_attempt)
from romeo.util import load_yaml, sha256_file

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


class TestDelegationCommandsMatchRunbook(_UnitRepo, unittest.TestCase):
    """`[2/5]` 가 인쇄하는 위임 명령이 RUNBOOK §3.2~§3.7 과 같다 (Q-40·Q-41).

    직전 관통에서 두 자리가 어긋났다. ① 첫 명령이 `run-create` 라 `--run` 으로 받은 Orca Run 이 있는데도 새 Run 을 만들었고,
    ② 구현자 `task-create --spec` 이 §3.4 가 요구한 항목 5개(결과 계약 형식 · 체크박스는 구현자가 채운다 · 계약이 없으면
    스스로 만든다 · `--task-id`·`--dispatch-id` 플래그 · dispatch-id 는 기동 뒤 전달)를 담지 않았다. 요구하는 자리(RUNBOOK)와
    만드는 자리(`run_unit.py`)가 어긋난 §11 의 사례다 — 정본 절차 파일에서 채우게 해 둘을 같게 둔다.
    검토자 `--spec` 에는 해시를 넣지 않는다(Q-41) — 해시는 `fill_brief.py --task-sha256` 이 그 자리에서 계산한다."""

    BRIEF = HARNESS_ROOT / "adapters/orca/prompts/implementer-brief.md"
    #: §3.4 의 항목 5개가 정본에 있다는 것을 보는 문구
    BRIEF_PHRASES = ("core/schemas/result-envelope.json", "네가 채운다", "아직 없으면", "envelope build",
                     "--task-id <task-id> --dispatch-id <dispatch-id>", "받기 전에는")

    def _commands(self):
        res = self._run()
        contract = next(s for s in res["stages"] if s["stage"] == "contract")
        delegate = next(s for s in res["stages"] if s["stage"] == "delegate")
        return contract, delegate["commands"]

    @staticmethod
    def _one(cmds, name):
        found = [c for n, c in cmds if n == name]
        assert len(found) == 1, (name, [n for n, _ in cmds])
        return found[0]

    # ── ① run-create 가 없고 첫 명령이 run-show --id <run> 이다 ──────────────
    def test_no_run_create_and_the_first_command_shows_the_existing_run(self):
        _contract, cmds = self._commands()
        joined = "\n".join(c for _n, c in cmds)
        self.assertNotIn("run-create", joined)
        self.assertIn("orca orchestration run-show --id run_a", cmds[0][1])

    # ── ② 구현자 --spec 은 정본 절차 파일을 채운 것을 읽는다 ────────────────
    def test_implementer_spec_is_read_from_the_filled_brief(self):
        _contract, cmds = self._commands()
        impl = self._one(cmds, "task-create:implementer")
        spec_file = f".harness/runs/{self.unit}/run_a/implementer-spec.md"
        self.assertIn(f'--spec "$(cat {spec_file})"', impl)
        fill = self._one(cmds, "implementer-spec")
        self.assertIn(str(HARNESS_ROOT / "adapters/orca/prompts/implementer-brief.md"), fill)
        self.assertIn(f"mkdir -p .harness/runs/{self.unit}/run_a", fill)
        for placeholder, value in (("<id>", self.unit), ("<run-id>", "run_a"), ("<base-sha>", self.base)):
            self.assertIn(f"s/{placeholder}/{value}/g", fill)
        self.assertTrue(fill.rstrip().endswith(f"> {spec_file}"), fill)
        names = [n for n, _ in cmds]
        self.assertLess(names.index("implementer-spec"), names.index("task-create:implementer"))
        brief = self.BRIEF.read_text(encoding="utf-8")
        for phrase in self.BRIEF_PHRASES:
            self.assertIn(phrase, brief, phrase)

    def test_the_filled_brief_carries_the_five_items_with_no_delegator_placeholders_left(self):
        """인쇄된 채움 명령을 실제로 돌리면 정본의 자리표시자 셋이 채워지고 워커 몫(<task-id>·<dispatch-id>)만 남는다."""
        _contract, cmds = self._commands()
        fill = self._one(cmds, "implementer-spec")
        proc = subprocess.run(["bash", "-c", fill], cwd=str(self.root), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        filled = (self.root / ".harness/runs" / self.unit / "run_a" / "implementer-spec.md").read_text(encoding="utf-8")
        for gone in ("<id>", "<run-id>", "<base-sha>"):
            self.assertNotIn(gone, filled)
        self.assertIn(self.unit, filled)
        self.assertIn(self.base, filled)
        for phrase in ("core/schemas/result-envelope.json", "네가 채운다", "아직 없으면", "envelope build",
                       "--task-id <task-id> --dispatch-id <dispatch-id>", "받기 전에는"):
            self.assertIn(phrase, filled, phrase)
        self.assertFalse(filled.startswith("#"), "정본의 머리말(--- 앞)은 넘기지 않는다")

    # ── ③ 검토자 task-create 에는 해시가 없다 ────────────────────────────────
    def test_reviewer_spec_carries_paths_and_procedure_but_no_hash(self):
        _contract, cmds = self._commands()
        rev = self._one(cmds, "task-create:reviewer")
        self.assertIsNone(re.search(r"[0-9a-f]{64}", rev), rev)
        for want in (f"docs/work/{self.unit}/task/run_a-reviewer.json",
                     f"docs/work/{self.unit}/review/run_a-reviewer.json",
                     "core/workflows/review/SKILL.md", "§3.7", "해시는 거기서 계산한다", "읽기 전용"):
            self.assertIn(want, rev, want)

    # ── ④ fill_brief 명령이 1단계 검토자 계약의 sha256 을 그대로 싣는다 ──────
    def test_fill_brief_command_carries_the_reviewer_contract_sha256(self):
        contract, cmds = self._commands()
        sha = next(b["sha256"] for b in contract["built"] if b["role"] == "reviewer")
        self.assertEqual(sha, sha256_file(self.root / "docs/work" / self.unit / "task" / "run_a-reviewer.json"))
        fill = self._one(cmds, "reviewer-brief")
        self.assertIn(str(HARNESS_ROOT / "adapters/orca/prompts/fill_brief.py"), fill)
        self.assertIn(f"--task-sha256 {sha}", fill)
        self.assertIn(f"--unit {self.unit} --run run_a --base-sha {self.base}", fill)
        self.assertIn("--runtime codex --mode base", fill)
        self.assertIn(f"--out <W>/.harness/runs/{self.unit}/run_a/reviewer-brief.md", fill)
        names = [n for n, _ in cmds]
        self.assertLess(names.index("reviewer-brief"), names.index("reviewer-spawn"))

    def test_delegation_commands_takes_the_harness_root_and_the_reviewer_sha256(self):
        cmds = delegation_commands(self.unit, "run_x", self.base, "worktree", HARNESS_ROOT, "f" * 64)
        self.assertEqual(cmds[0][0], "run-show")
        self.assertIn("--task-sha256 " + "f" * 64, dict(cmds)["reviewer-brief"])

    # ── ⑤ 종전 동작 유지 — 인쇄까지다 ─────────────────────────────────────────
    def test_delegation_commands_are_printed_not_executed(self):
        res = self._run()
        delegate = next(s for s in res["stages"] if s["stage"] == "delegate")
        self.assertEqual(delegate["state"], "dry-run")
        self.assertTrue(delegate["commands"])
        self.assertNotIn("ran", delegate)
        self.assertFalse((self.root / ".harness").exists(), "dry-run 은 절차 파일도 만들지 않는다")


class TestAttemptsDrift(unittest.TestCase):
    """`attempts_drift` / `run-unit check` — §3.1 확인 4 를 **판정·재검토 대조**로 좁힌다 (Q-39).

    회차 기록이 계약 생성으로 옮겨진 뒤(Q-27) `attempts.yaml` 은 언제나 승인 커밋 뒤에 생기므로, 파일 전체를 `diff` 하던
    확인 4 는 첫 관통에서 항상 실패했고 지시된 해법은 순환이었다. 워커가 보지 못하면 실제로 판정이 바뀌는 것은
    **판정 난 시도(pass·fail)와 재검토(reviews)** 뿐이다 — 중단 게이트는 그 둘만 읽는다. `started` 는 대조하지 않는다."""

    UNIT = "feat-19700101-drift-unit-test"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        self.unit_dir = self.root / "docs" / "work" / self.UNIT
        self.unit_dir.mkdir(parents=True)
        (self.unit_dir / "spec.md").write_text("---\nid: x\n---\n", encoding="utf-8")
        self.base = self._commit("base")

    def tearDown(self):
        self.tmp.cleanup()

    def _commit(self, msg):
        git("add", "-A", cwd=self.root)
        git("commit", "-q", "-m", msg, cwd=self.root)
        return git("rev-parse", "HEAD", cwd=self.root)

    def _write(self, attempts=(), reviews=()):
        data = {"schema": "romeo/attempts@0.1.0", "unit_id": self.UNIT,
                "attempts": [{"n": i, "run": f"run_{i}", "base_sha": "a" * 40, "result": r}
                             for i, r in enumerate(attempts, 1)],
                "reviews": [{"after_attempt": n, "conclusion": c, "by": "사람", "at": "2026-01-01T00:00:00+09:00"}
                            for n, c in reviews]}
        save_attempts(self.root, self.UNIT, data)

    def _drift(self, base=None):
        from romeo.run_unit import attempts_drift   # 구현 전에는 이 이름이 없다 — 이 테스트만 실패한다
        return attempts_drift(self.root, self.UNIT, base or self.base)

    def _cli(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["run-unit", "check", "--unit", self.UNIT, "--root", str(self.root), *extra])
        return code, out.getvalue() + err.getvalue()

    def test_missing_on_both_sides_is_no_drift(self):
        self.assertFalse((self.unit_dir / "attempts.yaml").exists())
        self.assertEqual(self._drift(), [])

    def test_started_only_in_the_working_tree_is_no_drift(self):
        """첫 관통의 모양 — 계약 생성이 막 남긴 started 하나. 이것으로 막으면 어떤 관통도 시작하지 못한다."""
        self._write(attempts=("started",))
        self.assertEqual(self._drift(), [])

    def test_fail_only_in_the_working_tree_is_drift(self):
        self._write(attempts=("fail",))
        diffs = self._drift()
        self.assertEqual(len(diffs), 1, diffs)
        self.assertIn("fail", diffs[0])
        self.assertIn("run_1", diffs[0])

    def test_review_only_in_the_working_tree_is_drift(self):
        self._write(attempts=(), reviews=((0, "완료 정의를 좁혔다"),))
        diffs = self._drift()
        self.assertEqual(len(diffs), 1, diffs)
        self.assertIn("재검토", diffs[0])
        self.assertIn("완료 정의를 좁혔다", diffs[0])

    def test_a_committed_fail_turned_pass_in_the_working_tree_is_drift(self):
        self._write(attempts=("fail",))
        base = self._commit("attempts")
        self._write(attempts=("pass",))
        diffs = self._drift(base)
        self.assertTrue(diffs)
        self.assertTrue(any("pass" in d for d in diffs), diffs)
        self.assertTrue(any("fail" in d for d in diffs), diffs)

    def test_identical_is_no_drift(self):
        self._write(attempts=("fail", "pass"), reviews=((2, "좁혔다"),))
        base = self._commit("attempts")
        self.assertEqual(self._drift(base), [])

    def test_a_started_added_on_top_of_a_committed_record_is_no_drift(self):
        """재검토·판정은 커밋돼 있고 작업 트리에는 3회차 started 만 더 있다 — 브레이크를 풀고 막 기동한 자리다."""
        self._write(attempts=("fail", "fail"), reviews=((2, "좁혔다"),))
        base = self._commit("attempts")
        self._write(attempts=("fail", "fail", "started"), reviews=((2, "좁혔다"),))
        self.assertEqual(self._drift(base), [])

    # ── 양방향이다 — 커밋에는 있는 판정·재검토가 작업 트리에 없어도 차이다 ───────
    def test_a_committed_verdict_missing_from_the_working_tree_is_drift(self):
        """fail 을 커밋한 뒤 작업 트리의 파일을 지웠다 — 워커는 커밋의 fail 을 보는데 위임한 쪽은 없는 줄 안다. 한쪽만 보면 통과한다."""
        self._write(attempts=("fail",))
        base = self._commit("attempts")
        (self.unit_dir / "attempts.yaml").unlink()
        diffs = self._drift(base)
        self.assertEqual(len(diffs), 1, diffs)
        self.assertIn("커밋에만", diffs[0])
        self.assertIn("run_1", diffs[0])
        code, out = self._cli("--base-sha", base)
        self.assertEqual(code, 1, out)
        self.assertIn("커밋에만", out)

    def test_a_committed_verdict_emptied_in_the_working_tree_is_drift(self):
        """지우지 않고 `attempts: []` 로 비운 경우도 같다 — 파일이 있다는 것이 기록이 있다는 뜻은 아니다."""
        self._write(attempts=("fail",))
        base = self._commit("attempts")
        self._write(attempts=())
        diffs = self._drift(base)
        self.assertEqual(len(diffs), 1, diffs)
        self.assertIn("커밋에만", diffs[0])
        self.assertIn("fail", diffs[0])

    def test_a_committed_review_missing_from_the_working_tree_is_drift(self):
        self._write(attempts=("fail", "fail"), reviews=((2, "완료 정의를 좁혔다"),))
        base = self._commit("attempts")
        self._write(attempts=("fail", "fail"))
        diffs = self._drift(base)
        self.assertEqual(len(diffs), 1, diffs)
        self.assertIn("재검토", diffs[0])
        self.assertIn("커밋에만", diffs[0])
        self.assertIn("완료 정의를 좁혔다", diffs[0])

    def test_an_unknown_base_sha_is_an_error_not_an_empty_record(self):
        with self.assertRaises(ValueError):
            self._drift("0" * 40)

    # ── CLI ──────────────────────────────────────────────────────────────────
    def test_cli_exits_zero_and_says_what_it_did_not_compare(self):
        self._write(attempts=("started",))
        code, out = self._cli("--base-sha", self.base)
        self.assertEqual(code, 0, out)
        self.assertIn("→ 일치", out)
        self.assertIn("started 는 대조하지 않는다", out)
        self.assertIn("판정 0건", out)
        self.assertIn("재검토 0건", out)

    def test_cli_exits_one_and_prints_the_difference(self):
        self._write(attempts=("fail",), reviews=((1, "좁혔다"),))
        code, out = self._cli("--base-sha", self.base)
        self.assertEqual(code, 1, out)
        self.assertIn("run_1", out)
        self.assertIn("좁혔다", out)
        self.assertIn("커밋", out)

    def test_cli_check_requires_base_sha_and_not_run(self):
        code, out = self._cli()
        self.assertEqual(code, 2, out)
        self.assertIn("--base-sha", out)
        self.assertFalse((self.unit_dir / "attempts.yaml").exists(), "check 는 아무것도 쓰지 않는다")

    def test_cli_check_accepts_a_symbolic_ref(self):
        code, out = self._cli("--base-sha", "HEAD")
        self.assertEqual(code, 0, out)

    def test_cli_unknown_base_sha_exits_one_with_error(self):
        """없는 SHA 는 빈 기록이 아니라 ERROR 다 — 오타 난 SHA 가 「일치」 로 읽히면 안 된다."""
        code, out = self._cli("--base-sha", "0" * 40)
        self.assertEqual(code, 1, out)
        self.assertIn("ERROR", out)
        self.assertNotIn("일치", out)


class TestAttemptBaseShaFollowsReapproval(_UnitRepo, unittest.TestCase):
    """회차 기록의 `base_sha` 가 재승인을 따라간다 (Q-42).

    관통 도중 재승인하면 계약·증거는 새 승인 커밋으로 옮겨가는데 `attempts.yaml` 의 회차는 기동 시점 값에 고정돼
    「그 회차가 무엇을 겨눴는가」 를 이력에서 잘못 읽게 했다(2026-09-02 5회차: 기록 93f0c0a vs 계약 01ec50d).
    같은 run 으로 계약을 다시 만들면 회차를 늘리지 않고 `base_sha` 만 옮기고, 이전 값은 `base_sha_history` 에 남긴다."""

    def _build(self, base):
        return write_envelope(self.unit, "implementer", project_root=self.root, base_sha=base, run_name="run_a")

    def _reapprove(self, reason="검증 계획 변경"):
        approve_unit(self.unit, "tester", project_root=self.root, reapprove=True, reason=reason)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "reapprove", cwd=self.root)
        return git("rev-parse", "HEAD", cwd=self.root)

    def test_same_run_rebuilt_at_a_new_base_moves_base_sha_and_keeps_history(self):
        a = self.base
        self._build(a)
        b = self._reapprove()
        self.assertNotEqual(a, b)
        self._build(b)
        data = load_attempts(self.root, self.unit)
        self.assertEqual(len(data["attempts"]), 1, "회차 수는 늘지 않는다")
        self.assertEqual(data["attempts"][0]["base_sha"], b)
        self.assertEqual(data["attempts"][0]["base_sha_history"], [a])
        self.assertEqual(data["attempts"][0]["result"], "started")

    def test_rebuilding_at_the_same_base_changes_nothing(self):
        self._build(self.base)
        path = self.root / "docs/work" / self.unit / "attempts.yaml"
        before = path.read_text(encoding="utf-8")
        self._build(self.base)
        self.assertEqual(path.read_text(encoding="utf-8"), before)
        att = load_attempts(self.root, self.unit)["attempts"][0]
        self.assertNotIn("base_sha_history", att)

    def test_two_reapprovals_append_to_the_history_in_order(self):
        a = self.base
        self._build(a)
        b = self._reapprove("첫 재승인")
        self._build(b)
        c = self._reapprove("둘째 재승인")
        self._build(c)
        att = load_attempts(self.root, self.unit)["attempts"][0]
        self.assertEqual(att["base_sha"], c)
        self.assertEqual(att["base_sha_history"], [a, b])
        self.assertEqual(len(load_attempts(self.root, self.unit)["attempts"]), 1)

    def test_run_unit_at_the_new_base_reports_the_moved_base(self):
        self._run(run="run_a")
        b = self._reapprove()
        res = run_unit(self.unit, project_root=self.root, run="run_a", base_sha=b)
        self.assertEqual(res["base_sha"], b)
        data = load_attempts(self.root, self.unit)
        self.assertEqual(len(data["attempts"]), 1)
        self.assertEqual(data["attempts"][0]["base_sha"], b)
        self.assertEqual(data["attempts"][0]["base_sha_history"], [self.base])
