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
                            load_attempts, record_result, run_unit)
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
        self.assertEqual(consecutive_failures(data), 0)
        self.assertTrue(gate(data)[0])
        # 해제 뒤에도 다시 2연속 실패가 쌓이면 또 막는다 — 한 번의 재검토가 영구 면제가 아니다
        data["attempts"] += [{"n": 3, "run": "run_3", "base_sha": "c" * 40, "result": "fail"},
                             {"n": 4, "run": "run_4", "base_sha": "c" * 40, "result": "fail"}]
        self.assertFalse(gate(data)[0])

    def test_unsettled_attempt_is_not_counted(self):
        data = _attempts("fail", "fail", "started")
        self.assertEqual(consecutive_failures(data), 2)


class TestRunUnit(unittest.TestCase):
    """실제 저장소 위에서 5단계와 중단 기준을 함께 본다."""

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


if __name__ == "__main__":
    unittest.main()
