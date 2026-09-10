"""재작업 위임이 앞 워커의 죽음을 관측하고, 봉인된 run 의 거부를 절차 문서가 적는다 — Q-101 ·
`feat-20260910-sealed-run-worker-settle-37qi` AC-5·AC-6·AC-7 의 판별 규칙.

요구가 사는 자리(RUNBOOK §3.4.2·§7·§11 · 코어 implement 절차 7번)를 코드에서 읽어 고정한다(AGENTS.core §11).
봉인 라벨은 이 파일에 적지 않는다 — `romeo.evidence.REVIEW_RECORD_LABEL` 에서 import 로만 읽는다.
"""
import re
import unittest
from pathlib import Path

from romeo.evidence import REVIEW_RECORD_LABEL

REPO = Path(__file__).resolve().parents[1]
RUNBOOK = REPO / "adapters" / "orca" / "RUNBOOK.md"
IMPLEMENT_SKILL = REPO / "core" / "workflows" / "implement" / "SKILL.md"
OBSERVATIONS = REPO / ".harness" / "observations.yaml"

SETTLE_STATUSES = ("failed", "completed")


def _section(text, start_pat, end_pat):
    """`awk '/start/,/end/'` 와 같은 잘라내기 — 시작 헤더부터 다음 헤더 전까지."""
    out, on = [], False
    for line in text.splitlines():
        if not on and re.search(start_pat, line):
            on = True
            out.append(line)
            continue
        if on:
            if re.search(end_pat, line):
                break
            out.append(line)
    return "\n".join(out)


def _table_rows(text):
    """마크다운 표의 본문 행(구분선·헤더 제외)."""
    rows = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def _first_line_index(text, needle):
    for i, line in enumerate(text.splitlines()):
        if needle in line:
            return i
    return None


class TestReworkObservesSettle(unittest.TestCase):
    """AC-5 — §3.4.2 「밟을 순서」 의 첫 단계는 앞 dispatch 의 settle 관측이다."""

    def setUp(self):
        self.text = RUNBOOK.read_text(encoding="utf-8")
        self.body = _section(self.text, r"^### 3\.4\.2 ", r"^### ")
        self.assertTrue(self.body.startswith("### 3.4.2 "), self.body[:40])

    def test_worker_show_comes_before_task_update(self):
        show = _first_line_index(self.body, "worker-show --dispatch")
        update = _first_line_index(self.body, "task-update")
        self.assertIsNotNone(show, "§3.4.2 에 `worker-show --dispatch` 가 없다")
        self.assertIsNotNone(update, "§3.4.2 에 `task-update` 가 없다")
        self.assertLess(show, update, "settle 관측이 Task 닫기보다 앞이어야 한다")

    def test_worker_show_appears_at_least_twice(self):
        """(가) 의 관측과 (나) 의 재관측 — `worker-stop` 이 수락됐어도 다시 본다."""
        self.assertGreaterEqual(self.body.count("worker-show"), 2)

    def test_three_branches_and_their_fields(self):
        for needle in (".result.dispatch.status", ".result.observation.status", "exited", "worker-stop", "§7"):
            self.assertIn(needle, self.body, needle)
        for status in SETTLE_STATUSES:
            self.assertIn(f"`{status}`", self.body, status)

    def test_evidence_refusal_names_the_seal_label_in_backticks(self):
        self.assertIn(f"`{REVIEW_RECORD_LABEL}`", self.body)
        for cmd in ("evidence run", "evidence checks", "review record"):
            self.assertIn(cmd, self.body, cmd)


class TestRefusedWorkerStopRecovery(unittest.TestCase):
    """AC-6 — §7 「남은 상태」 표에 `worker-stop` 이 거부하는 행이 정확히 하나 있고, 그 행이 복구 순서 셋을 담는다."""

    def setUp(self):
        self.text = RUNBOOK.read_text(encoding="utf-8")
        self.sec7 = _section(self.text, r"^## 7\. ", r"^## ")
        self.assertTrue(self.sec7.startswith("## 7. "), self.sec7[:40])
        rows = [r for r in _table_rows(self.sec7) if any("is not stopping" in c for c in r)]
        self.assertEqual(len(rows), 1, rows)
        self.row = rows[0]
        self.row_text = " | ".join(self.row)

    def test_first_cell_carries_the_refusal_message(self):
        self.assertIn("is not stopping", self.row[0])

    def test_row_contains_recovery_command_ownership_fields_and_settle_fields(self):
        for needle in ("orca terminal close --terminal", "ownerDispatchId", "exactWorker",
                       "dispatch.status", "observation.status", "exited", "미관측", "worker-show"):
            self.assertIn(needle, self.row_text, needle)
        for status in SETTLE_STATUSES:
            self.assertIn(f"`{status}`", self.row_text, status)

    def test_close_follows_ownership_check_immediately(self):
        """① 소유 확인 → ② 그 직후 `terminal close` → ③ settle 재확인. ① 과 ② 사이에 다른 단계가 없다."""
        i_owner = self.row_text.index("ownerDispatchId")
        i_exact = self.row_text.index("exactWorker")
        i_close = self.row_text.index("orca terminal close --terminal")
        i_settle = self.row_text.index("dispatch.status")
        self.assertLess(i_owner, i_close)
        self.assertLess(i_exact, i_close)
        self.assertLess(i_close, i_settle)
        between = self.row_text[max(i_owner, i_exact):i_close]
        self.assertNotIn("worker-", between, between)
        self.assertNotIn("task-", between, between)

    def test_unobserved_and_its_basis(self):
        """② 가 거부된 워커를 실제로 죽이는지 **미관측**이고, 그 근거 — 이 저장소의 관측 기록에 `terminal close` 가 없다 —
        를 검사가 같이 본다. 관측 기록이 생기면 이 검사가 그 행의 「미관측」 을 지목한다."""
        self.assertIn("미관측", self.row_text)
        sec111 = _section(self.text, r"^### 11\.1 ", r"^### ")
        self.assertTrue(sec111.startswith("### 11.1 "), sec111[:40])
        self.assertNotIn("terminal close", sec111)
        self.assertNotIn("terminal close", OBSERVATIONS.read_text(encoding="utf-8"))

    def test_section_112_lists_terminal_close_as_unverified(self):
        sec112 = _section(self.text, r"^### 11\.2 ", r"^#{1,3} ")
        self.assertTrue(sec112.startswith("### 11.2 "), sec112[:40])
        self.assertIn("orca terminal close --terminal", sec112)


class TestCoreImplementProcedureStatesTheRefusal(unittest.TestCase):
    """AC-7 — 코어 implement 절차 7번 항목이 봉인 라벨을 백틱으로 담은 문장에서 「거부」 와 「새 run」 을 함께 말한다."""

    def setUp(self):
        text = IMPLEMENT_SKILL.read_text(encoding="utf-8")
        self.item7 = _section(text, r"^7\. \*\*증거\.\*\*", r"^8\. ")
        self.assertTrue(self.item7.startswith("7. **증거.**"), self.item7[:40])
        self.label = f"`{REVIEW_RECORD_LABEL}`"

    def _sentences(self):
        flat = " ".join(line.strip() for line in self.item7.splitlines())
        return [s.strip() for s in re.split(r"(?<=[.。])\s+", flat) if s.strip()]

    def test_one_sentence_carries_label_refusal_and_new_run(self):
        hits = [s for s in self._sentences() if self.label in s and "거부" in s and "새 run" in s]
        self.assertGreaterEqual(len(hits), 1, self._sentences())

    def test_no_sentence_mentions_the_label_without_refusal_or_new_run(self):
        bad = [s for s in self._sentences() if self.label in s and "거부" not in s and "새 run" not in s]
        self.assertEqual(bad, [])

    def test_this_file_does_not_spell_the_label(self):
        self.assertEqual(Path(__file__).read_text(encoding="utf-8").count(REVIEW_RECORD_LABEL), 0)


if __name__ == "__main__":
    unittest.main()
