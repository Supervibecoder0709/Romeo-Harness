"""봉인 직전 방어 검사 부재 경고 — Q-103 · `feat-20260913-seal-fill-scope-alignment-5sek` AC-1·AC-2.

`romeo review record`(`record_review_envelope`)가 이 run 의 증거에 종료 검사(`romeo/close.py`)가 판정에 쓰는
방어 검사(`DEFENSIVE_LABELS`) 기록이 빠진 채로 봉인을 실행하면, 빠진 라벨을 **모두** 이름으로 말하는 경고를
표준 오류에 인쇄한다. 경고는 막지 않는다 — 봉인은 그대로 이뤄지고 명령의 종료 코드는 바뀌지 않는다(AC-1).

그 라벨 목록의 정의는 저장소에 `romeo.close.DEFENSIVE_LABELS` 하나뿐이고, 경고는 그 정의를 호출 시점에 읽는다 —
값을 복사한 구현은 그 정의를 바꿔도 경고가 따라가지 않는다(AC-2). 픽스처는 `test_sealed_run_refusal.py` 의
`SealedRunFixture` 를 그대로 쓴다 — 봉인 절차(임시 저장소·단위·방어 검사 헬퍼)를 다시 만들지 않는다.
"""
import io
import unittest
from contextlib import redirect_stderr
from unittest import mock

from romeo.evidence import REVIEW_RECORD_LABEL, record_review_envelope
from tests.test_sealed_run_refusal import SealedRunFixture


class TestReviewSealWarning(SealedRunFixture):

    def test_a_run_missing_the_defensive_records_warns_and_still_seals(self):
        # 대조군 — 방어 검사가 전부 있는 run. 경고 없이 봉인되고, 이 run 의 기록 명령 종료 코드가 비교 기준이다.
        self._defensive("run-complete")
        err_complete = io.StringIO()
        with redirect_stderr(err_complete):
            complete = record_review_envelope(self.unit, "run-complete", self._source("complete.json", self._envelope()),
                                              project_root=self.root)
        self.assertNotIn("review-tree-before", err_complete.getvalue())
        self.assertNotIn("review-tree-after", err_complete.getvalue())
        self.assertEqual(complete["command"]["exit_code"], 0)

        # 실험군 — 방어 검사가 하나도 없는 run. 봉인은 그대로 이뤄지고, 빠진 라벨 둘 다 경고에 이름으로 나온다.
        err_missing = io.StringIO()
        with redirect_stderr(err_missing):
            missing = record_review_envelope(self.unit, "run-missing", self._source("missing.json", self._envelope()),
                                             project_root=self.root)
        out = err_missing.getvalue()
        self.assertIn("review-tree-before", out)
        self.assertIn("review-tree-after", out)
        self.assertEqual(missing["command"]["exit_code"], complete["command"]["exit_code"])
        rec = self._rec("run-missing")
        self.assertEqual(rec["commands"][-1]["id"], REVIEW_RECORD_LABEL, "경고가 있어도 봉인은 이뤄진다")

    def test_the_warning_reads_the_label_list_close_judges_with(self):
        # 방어 검사 둘(원래 라벨)을 남긴 run 은 patched 목록 기준으로는 아무것도 갖고 있지 않다 —
        # 경고가 원래 라벨이 아니라 patch 된 이름을 말해야 close.DEFENSIVE_LABELS 를 그때그때 읽었다는 증거다.
        self._defensive("run-patched")
        with mock.patch("romeo.close.DEFENSIVE_LABELS", ("review-tree-alpha", "review-tree-beta")):
            err = io.StringIO()
            with redirect_stderr(err):
                record_review_envelope(self.unit, "run-patched", self._source("patched.json", self._envelope()),
                                       project_root=self.root)
        out = err.getvalue()
        self.assertIn("review-tree-alpha", out)
        self.assertIn("review-tree-beta", out)
        self.assertNotIn("review-tree-before", out)
        self.assertNotIn("review-tree-after", out)


if __name__ == "__main__":
    unittest.main()
