"""`run-unit merge-check` — 통합 직전에 **판정 손실**을 막는다 (Q-48).

워커는 자기 워크트리 안에서 `envelope build` 를 지나며 `attempts.yaml` 에 `started` 를 남기고, 그 회차의 판정(`pass`·`fail`)은
`run-unit record` 가 **위임한 쪽** 체크아웃에만 쓴다. 그래서 통합 시점에 두 파일이 갈린다 — 2026-09-03 실측:
워크트리 「1: fail / 2: started」 vs 위임 쪽 「1: fail / 2: pass」. 워크트리 것을 그대로 통합하면 `2: pass` 가 `started` 로 덮이고,
`run-unit check` 는 `started` 를 대조하지 않으므로(Q-39) 이 손실은 **어느 검사에도 걸리지 않았다.**

이 파일이 고정하는 것은 그 검사의 양면이다.

  ① 위임 쪽 판정이 워크트리 사본에 없으면 차이다 — 통합하면 사라지는 판정이므로 exit ≠ 0 이고 어느 회차의 어느 판정인지 인쇄한다
  ② 워크트리에 `started` 회차만 더 있는 것은 차이가 아니다 — 관통에서 **언제나 나는 모양**이고, 이것을 막으면 통합이 아무 때도 서지 않는다

②가 이 파일의 절반인 이유: 정상 통합을 막는 검사는 통합을 막을 뿐 아무것도 지키지 못한다.
"""
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from romeo.cli import main
from romeo.run_unit import compare_worktree_attempts, save_attempts


def _record(unit_id, attempts):
    """`attempts` 는 (n, run, result) 목록이다."""
    return {"schema": "romeo/attempts@0.1.0", "unit_id": unit_id,
            "attempts": [{"n": n, "run": run, "base_sha": "a" * 40, "result": result,
                          "failure_class": None, "note": None, "settled_at": None}
                         for n, run, result in attempts],
            "reviews": []}


class _TwoCheckouts(unittest.TestCase):
    """위임한 쪽(정본)과 워커 워크트리 사본, 두 트리를 만든다. git 은 필요 없다 — 이 대조는 커밋을 보지 않는다."""

    UNIT = "feat-19700101-merge-check-unit-test"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        root = Path(self.tmp.name)
        self.local = root / "delegator"          # 위임한 쪽 = attempts.yaml 의 정본
        self.wt = root / "worktree"              # 워커 워크트리 사본
        for r in (self.local, self.wt):
            (r / "docs" / "work" / self.UNIT).mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, root, attempts):
        save_attempts(root, self.UNIT, _record(self.UNIT, attempts))

    def _compare(self):
        return compare_worktree_attempts(self.local, self.UNIT, self.wt)

    def _cli(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["run-unit", "merge-check", "--unit", self.UNIT, "--root", str(self.local),
                         "--worktree", str(self.wt), *extra])
        return code, out.getvalue() + err.getvalue()


class TestVerdictLossBlocks(_TwoCheckouts):
    """① 통합하면 사라지는 판정이 하나라도 있으면 막는다 (AC-3)."""

    def test_the_observed_second_attempt_shape_is_a_loss(self):
        """2026-09-03 실측 그대로 — 위임 쪽 {1: fail, 2: pass} vs 워크트리 {1: fail, 2: started}."""
        self._write(self.local, [(1, "run_a", "fail"), (2, "run_b", "pass")])
        self._write(self.wt, [(1, "run_a", "fail"), (2, "run_b", "started")])
        res = self._compare()
        self.assertEqual(len(res["diffs"]), 1, res["diffs"])
        self.assertIn("회차 2", res["diffs"][0])
        self.assertIn("run_b", res["diffs"][0])
        self.assertIn("pass", res["diffs"][0])

    def test_a_round_missing_from_the_worktree_entirely_is_a_loss(self):
        self._write(self.local, [(1, "run_a", "fail")])
        self._write(self.wt, [])
        res = self._compare()
        self.assertEqual(len(res["diffs"]), 1, res["diffs"])
        self.assertIn("run_a", res["diffs"][0])
        self.assertIn("fail", res["diffs"][0])

    def test_a_verdict_flipped_in_the_worktree_is_a_loss(self):
        """그럴듯한 거짓 값 — 회차도 run 도 그대로인데 판정만 다르다. 형태만 보는 검사는 이것을 통과시킨다."""
        self._write(self.local, [(1, "run_a", "fail")])
        self._write(self.wt, [(1, "run_a", "pass")])
        res = self._compare()
        self.assertTrue(res["diffs"])
        self.assertTrue(any("fail" in d for d in res["diffs"]), res["diffs"])

    def test_the_worktree_file_missing_loses_every_verdict(self):
        self._write(self.local, [(1, "run_a", "fail"), (2, "run_b", "pass")])
        self.assertFalse((self.wt / "docs" / "work" / self.UNIT / "attempts.yaml").exists())
        self.assertEqual(len(self._compare()["diffs"]), 2)

    def test_reviews_are_not_compared_here(self):
        """재검토 대조는 §3.1 확인 4(`run-unit check`)의 몫이다 — 이 명령은 판정만 본다(비범위: Q-39 의 결정)."""
        local = _record(self.UNIT, [(1, "run_a", "fail")])
        local["reviews"] = [{"after_attempt": 1, "conclusion": "좁혔다", "by": "사람", "at": "2026-01-01T00:00:00+09:00"}]
        save_attempts(self.local, self.UNIT, local)
        self._write(self.wt, [(1, "run_a", "fail")])
        self.assertEqual(self._compare()["diffs"], [])


class TestNormalIntegrationPasses(_TwoCheckouts):
    """② 판정을 잃지 않은 통합은 그대로 통과한다 (AC-4)."""

    def test_a_started_only_in_the_worktree_is_not_a_loss(self):
        """관통에서 언제나 나는 모양 — 워커의 `envelope build` 가 회차 하나를 `started` 로 더 남겼다."""
        self._write(self.local, [(1, "run_a", "fail")])
        self._write(self.wt, [(1, "run_a", "fail"), (2, "run_b", "started")])
        res = self._compare()
        self.assertEqual(res["diffs"], [])
        self.assertEqual(res["verdicts"], 1)

    def test_the_first_run_through_shape_is_not_a_loss(self):
        """첫 관통 — 위임 쪽에는 판정이 하나도 없고 워크트리에만 `started` 가 있다."""
        self._write(self.local, [])
        self._write(self.wt, [(1, "run_a", "started")])
        self.assertEqual(self._compare()["diffs"], [])

    def test_identical_records_are_not_a_loss(self):
        self._write(self.local, [(1, "run_a", "fail"), (2, "run_b", "pass")])
        self._write(self.wt, [(1, "run_a", "fail"), (2, "run_b", "pass")])
        self.assertEqual(self._compare()["diffs"], [])

    def test_no_record_on_either_side_is_not_a_loss(self):
        self.assertEqual(self._compare()["diffs"], [])

    def test_an_extra_verdict_in_the_worktree_is_not_a_loss(self):
        """워크트리에만 있는 판정은 이 명령의 대상이 아니다 — 통합하면 사라지는 것이 아니라 들어오는 것이다."""
        self._write(self.local, [(1, "run_a", "fail")])
        self._write(self.wt, [(1, "run_a", "fail"), (2, "run_b", "pass")])
        self.assertEqual(self._compare()["diffs"], [])


class TestReturnedShape(_TwoCheckouts):
    """대조 함수가 돌려주는 것 — 판정 차이 목록 · 워크트리 경로 · 이 체크아웃의 판정 수 (구현 단위 1)."""

    def test_it_reports_the_worktree_and_the_local_verdict_count(self):
        self._write(self.local, [(1, "run_a", "fail"), (2, "run_b", "pass")])
        self._write(self.wt, [(1, "run_a", "fail"), (2, "run_b", "started")])
        res = self._compare()
        self.assertEqual(res["unit_id"], self.UNIT)
        self.assertEqual(Path(res["worktree"]).resolve(), self.wt.resolve())
        self.assertEqual(res["verdicts"], 2)
        self.assertEqual(res["worktree_verdicts"], 1)

    def test_it_writes_nothing(self):
        self._write(self.local, [(1, "run_a", "fail")])
        self._write(self.wt, [(1, "run_a", "started")])
        paths = [r / "docs" / "work" / self.UNIT / "attempts.yaml" for r in (self.local, self.wt)]
        before = {p: p.read_bytes() for p in paths}
        self._compare()
        for p, raw in before.items():
            self.assertEqual(p.read_bytes(), raw, p)

    def test_a_worktree_that_is_not_a_directory_is_an_error_not_a_match(self):
        """오타 난 경로를 「일치」 로 읽으면 이 검사는 아무것도 막지 않는다 — `_attempts_at` 이 없는 커밋을 거부하는 것과 같은 이유다."""
        self._write(self.local, [(1, "run_a", "fail")])
        with self.assertRaises(ValueError):
            compare_worktree_attempts(self.local, self.UNIT, self.wt / "없는-경로")


class TestCli(_TwoCheckouts):
    """`bin/romeo run-unit merge-check` — 종료 코드 자체가 조건이다 (AC-3·AC-4)."""

    def test_exit_is_not_zero_and_names_the_round_and_the_verdict(self):
        self._write(self.local, [(1, "run_a", "fail"), (2, "run_b", "pass")])
        self._write(self.wt, [(1, "run_a", "fail"), (2, "run_b", "started")])
        code, out = self._cli()
        self.assertNotEqual(code, 0, out)
        self.assertIn("회차 2", out)
        self.assertIn("run_b", out)
        self.assertIn("pass", out)

    def test_exit_is_zero_when_only_a_started_was_added(self):
        self._write(self.local, [(1, "run_a", "fail")])
        self._write(self.wt, [(1, "run_a", "fail"), (2, "run_b", "started")])
        code, out = self._cli()
        self.assertEqual(code, 0, out)

    def test_json_carries_the_same_verdict(self):
        self._write(self.local, [(1, "run_a", "fail"), (2, "run_b", "pass")])
        self._write(self.wt, [(1, "run_a", "fail"), (2, "run_b", "started")])
        code, out = self._cli("--json")
        self.assertNotEqual(code, 0, out)
        self.assertIn("run_b", out)

    def test_it_needs_a_worktree_and_refuses_without_one(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["run-unit", "merge-check", "--unit", self.UNIT, "--root", str(self.local)])
        self.assertEqual(code, 2, out.getvalue() + err.getvalue())
        self.assertIn("--worktree", out.getvalue() + err.getvalue())

    def test_it_does_not_require_a_run(self):
        """아무것도 쓰지 않으므로 봉투를 묶을 run 이 없다 — `check` 와 같다."""
        self._write(self.local, [])
        self._write(self.wt, [(1, "run_a", "started")])
        code, _ = self._cli()
        self.assertEqual(code, 0)


class TestRunbookNamesTheCommand(unittest.TestCase):
    """요구하는 자리(RUNBOOK)와 보는 자리(이 명령)를 같은 커밋에 둔다 (AC-5 · AGENTS.core §11)."""

    def setUp(self):
        from romeo import HARNESS_ROOT
        self.runbook = (Path(HARNESS_ROOT) / "adapters/orca/RUNBOOK.md").read_text(encoding="utf-8")

    def test_the_runbook_steps_the_command_before_integration(self):
        self.assertIn("run-unit merge-check", self.runbook)

    def test_the_runbook_says_which_side_owns_attempts(self):
        para = [p for p in self.runbook.split("\n\n") if "run-unit merge-check" in p]
        self.assertTrue(para)
        self.assertTrue(any("정본" in p for p in para), para)

    def test_the_handle_check_does_not_use_the_title(self):
        """제목은 런타임이 소유한 값이라 확인 기준이 될 수 없다 (AC-1·AC-2)."""
        self.assertNotIn("같은 제목", self.runbook)
        self.assertIn("result.terminal.worktreeId", self.runbook)
        self.assertIn("2026-09-03", self.runbook)


if __name__ == "__main__":
    unittest.main()
