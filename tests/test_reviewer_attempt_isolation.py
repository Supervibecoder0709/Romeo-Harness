"""검토자 계약은 관통 회차를 열지 않는다 — Q-95.

RUNBOOK §6.6 의 검토자-only 재실행은 **새 run** 을 쓴다. 회차를 여는 자리가 역할을 보지 않으면
구현은 한 번뿐인데 회차가 둘이 되고, §10 의 연속 실패 카운터가 검토 실행을 구현 회차로 센다 —
브레이크가 엉뚱한 자리에서 걸린다.

**그 사실을 버리지는 않는다.** 검토자 재실행은 `reviewer_runs:` 에 남는다. `reviews:` 가 아닌 이유는
그 목록이 §10 의 **사람 재검토** 기록이고 `gate()` 가 그것으로 차단을 풀기 때문이다 — 섞으면
사람이 완료 정의를 다시 보지 않은 채 다음 회차가 돈다.
"""
import unittest

from pathlib import Path

from romeo.envelope import record_start
from romeo.run_unit import add_review, gate, load_attempts, save_attempts, start_attempt

UNIT = "feat-20260101-fixture-unit-aaaa"
SHA = "0" * 40


def _root(tmp, attempts=None, reviews=None):
    """작업 단위 폴더만 있는 임시 루트. `attempts` 가 None 이면 `attempts.yaml` 자체가 없다."""
    root = Path(tmp)
    (root / "docs" / "work" / UNIT).mkdir(parents=True)
    if attempts is not None or reviews is not None:
        data = load_attempts(root, UNIT)
        for run, result in (attempts or []):
            entry = start_attempt(data, run, SHA)
            entry["result"] = result
        for conclusion in (reviews or []):
            add_review(data, conclusion, by="사람")
        save_attempts(root, UNIT, data)
    return root


class TestReviewerOpensNoAttempt(unittest.TestCase):
    def test_no_attempts_file(self):
        """상태 ① — `attempts.yaml` 이 아직 없다."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            self.assertIsNone(record_start(root, UNIT, "run_r1", SHA, "reviewer"))
            data = load_attempts(root, UNIT)
            self.assertEqual([], data["attempts"])
            self.assertEqual(["run_r1"], [r["run"] for r in data["reviewer_runs"]])

    def test_other_run_attempt_exists(self):
        """상태 ② — 다른 run 의 회차가 이미 있다. **그 항목이 바이트로 그대로 남는다.**

        필드를 골라 비교하지 않는다 — 비교하지 않은 필드(`started_at`·`base_sha`·`base_sha_history`)가
        바뀌어도 통과하기 때문이다. `attempts` 목록만 떼어 직렬화한 바이트를 비교한다."""
        import copy, tempfile
        from romeo.run_unit import attempts_path
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp, attempts=[("run_impl", "pass")])
            path = attempts_path(root, UNIT)
            before_file = path.read_bytes()
            before = copy.deepcopy(load_attempts(root, UNIT)["attempts"])
            self.assertIsNone(record_start(root, UNIT, "run_r1", SHA, "reviewer"))
            self.assertNotEqual(before_file, path.read_bytes(), "reviewer_runs 가 늘었어야 한다")
            # 항목을 **통째로** 비교한다 — 필드를 고르면 고르지 않은 필드가 바뀌어도 통과한다.
            self.assertEqual(before, load_attempts(root, UNIT)["attempts"])

    def test_whole_item_comparison_catches_any_field(self):
        """위 비교가 **어느 필드가 바뀌어도** 잡는가.

        고른 필드만 보면 나머지가 바뀌어도 통과한다 — 그것이 1회차 검토자 finding 이었다.
        여기서는 항목의 각 키를 하나씩 흔들어 비교가 실제로 갈리는 것을 보인다."""
        import copy, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp, attempts=[("run_impl", "pass")])
            before = copy.deepcopy(load_attempts(root, UNIT)["attempts"])
            self.assertTrue(before[0], "항목이 비어 있으면 비교할 것이 없다")
            for key in before[0]:
                shaken = copy.deepcopy(before)
                shaken[0][key] = "zzz-흔든-값"
                self.assertNotEqual(before, shaken, f"«{key}» 가 바뀌어도 같다고 나온다")

    def test_same_run_with_different_base_sha_is_untouched(self):
        """상태 ③의 반례 — 검토자 계약이 **다른 `base_sha`** 로 와도 기존 회차를 바꾸지 않는다.

        `base_sha` 갱신은 관통이 겨눈 승인이 바뀐 사건이고, 검토자를 다시 띄우는 것은 그 사건이 아니다."""
        import copy, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp, attempts=[("run_x", None)])
            before = copy.deepcopy(load_attempts(root, UNIT)["attempts"])
            entry = record_start(root, UNIT, "run_x", "f" * 40, "reviewer")
            self.assertEqual("run_x", entry["run"])
            self.assertEqual(before, load_attempts(root, UNIT)["attempts"])

    def test_same_run_attempt_exists(self):
        """상태 ③ — 같은 run 의 회차가 이미 있다. 그것을 그대로 돌려주고 파일은 바뀌지 않는다."""
        import tempfile
        from romeo.run_unit import attempts_path
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp, attempts=[("run_x", None)])
            before = attempts_path(root, UNIT).read_bytes()
            entry = record_start(root, UNIT, "run_x", SHA, "reviewer")
            self.assertIsNotNone(entry)
            self.assertEqual("run_x", entry["run"])
            self.assertEqual(before, attempts_path(root, UNIT).read_bytes(),
                             "같은 run·같은 base_sha 면 파일을 쓰지 않는다")

    def test_implementer_still_opens_an_attempt(self):
        """상태 ④ 여집합 — 같은 자리에서 구현자는 회차를 연다. 조건을 좁히며 옆을 부수지 않는다."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            entry = record_start(root, UNIT, "run_i1", SHA, "implementer")
            self.assertIsNotNone(entry)
            self.assertEqual(1, entry["n"])
            self.assertEqual(1, len(load_attempts(root, UNIT)["attempts"]))

    def test_reviewer_runs_is_append_only(self):
        """서로 다른 두 run 은 항목 둘, 같은 run 을 다시 만들면 늘지도 시각이 바뀌지도 않는다."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            record_start(root, UNIT, "run_r1", SHA, "reviewer")
            first = load_attempts(root, UNIT)["reviewer_runs"][0]["at"]
            record_start(root, UNIT, "run_r2", SHA, "reviewer")
            record_start(root, UNIT, "run_r1", SHA, "reviewer")
            runs = load_attempts(root, UNIT)["reviewer_runs"]
            self.assertEqual(["run_r1", "run_r2"], [r["run"] for r in runs])
            self.assertEqual(first, runs[0]["at"])


class TestBrakeIsUntouched(unittest.TestCase):
    """AC-6 — `gate()` 의 판정이 검토자 계약으로 바뀌지 않는다."""

    def test_blocked_state_stays_blocked(self):
        """판별 ① — 연속 2회 실패로 거부하는 상태."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp, attempts=[("run_a", "fail"), ("run_b", "fail")])
            before = gate(load_attempts(root, UNIT))
            self.assertFalse(before[0])
            record_start(root, UNIT, "run_r1", SHA, "reviewer")
            record_start(root, UNIT, "run_r2", SHA, "reviewer")
            self.assertEqual(before, gate(load_attempts(root, UNIT)))

    def test_repeat_gate_blocks_only_attempt_roles(self):
        """게이트 함수 자체 — 차단 상태에서 구현자 경로는 막힌다."""
        import tempfile
        from romeo.envelope import repeat_gate
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp, attempts=[("run_a", "fail"), ("run_b", "fail")])
            with self.assertRaises(ValueError):
                repeat_gate(root, UNIT)


class TestContractCreationPath(unittest.TestCase):
    """**실제 계약 생성 경로**(`write_envelope`)에서 검토자가 차단을 지나는가.

    회차 기록 함수만 부르는 것은 이 경로의 증거가 아니다 — `write_envelope` 는 역할과 무관하게
    `repeat_gate` 를 지났고, 차단 상태에서는 계약 생성 자체가 예외로 끝났다(1회차 검토자 finding)."""

    def setUp(self):
        import os, subprocess, tempfile
        from romeo import frontmatter
        from romeo.docs import approve_unit, create_unit
        from romeo.policy import route
        from tests.test_envelope import SCOPE_PATHS, SCOPE_TODO, git

        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        out = route({"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        res = create_unit(out, "회차 격리", "reviewer-gate", "검토자 계약과 반복 중단",
                          project_root=self.root, date="20260909")
        self.unit = res["id"]
        spec = Path(res["files"][0])
        fm, body = frontmatter.read(spec)
        body = (body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
                    .replace('command: "채움"', 'command: "true"'))
        frontmatter.write(spec, fm, body)
        approve_unit(self.unit, "tester", project_root=self.root)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def _make_blocked(self):
        """연속 2회 실패 상태로 만든다 — 사람 재검토는 없다."""
        data = load_attempts(self.root, self.unit)
        for run in ("run_a", "run_b"):
            start_attempt(data, run, SHA)["result"] = "fail"
        save_attempts(self.root, self.unit, data)
        self.assertFalse(gate(load_attempts(self.root, self.unit))[0])

    def test_implementer_contract_is_blocked(self):
        """구현자 계약은 차단 상태에서 만들어지지 않는다 — §10 이 지키는 것."""
        from romeo.envelope import write_envelope
        self._make_blocked()
        with self.assertRaises(ValueError):
            write_envelope(self.unit, "implementer", project_root=self.root, run_name="run_i")

    def test_reviewer_contract_is_created(self):
        """검토자 계약은 만들어지고, 회차를 늘리지 않으며, `gate()` 판정도 그대로다."""
        from romeo.envelope import write_envelope
        self._make_blocked()
        before = gate(load_attempts(self.root, self.unit))
        write_envelope(self.unit, "reviewer", project_root=self.root, run_name="run_r1")
        write_envelope(self.unit, "reviewer", project_root=self.root, run_name="run_r2")
        data = load_attempts(self.root, self.unit)
        self.assertEqual(2, len(data["attempts"]), "회차가 늘었다")
        self.assertEqual(["run_r1", "run_r2"], [r["run"] for r in data["reviewer_runs"]])
        self.assertEqual(before, gate(data))

    def test_released_state_stays_released(self):
        """판별 ② — 사람 재검토로 차단이 풀린 상태. `reviews:` 가 지워지면 여기서 걸린다."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp, attempts=[("run_a", "fail"), ("run_b", "fail")],
                         reviews=["완료 정의는 달성 가능하다"])
            before = gate(load_attempts(root, UNIT))
            self.assertTrue(before[0], "재검토가 있으면 통과해야 한다")
            record_start(root, UNIT, "run_r1", SHA, "reviewer")
            record_start(root, UNIT, "run_r2", SHA, "reviewer")
            self.assertEqual(before, gate(load_attempts(root, UNIT)))
            self.assertEqual(1, len(load_attempts(root, UNIT)["reviews"]))


if __name__ == "__main__":
    unittest.main()
