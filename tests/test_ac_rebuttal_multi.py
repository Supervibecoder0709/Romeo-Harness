"""반박 검사는 `inputs:` 의 **모든** 반박 파일을 본다 — Q-94.

반박을 두 번 돌려 AC 를 쪼개면 새 AC 는 1차 파일에 있을 수 없다. 첫 항목만 읽으면 그 AC 가
영영 미반박으로 남고, 사후에 1차 파일에 절을 더하는 것은 **거짓 기록**이다 —
그 반박은 그 AC 를 본 적이 없다.

**목록 밖 파일은 여전히 읽지 않는다.** 그것을 관측 가능하게 하려고 목록 밖 자리를 **디렉터리로 둔다** —
읽으려는 구현은 거기서 실패하므로, 통과 자체가 「읽지 않았다」의 관측이다.
반환값만 보면 「읽고 결과를 버리는」 구현과 구별되지 않는다.
"""
import tempfile
import unittest
from pathlib import Path

from romeo.docs import rebuttal_warnings
from romeo.policy import load_policy

POLICY = load_policy()
PREFIX = POLICY["packages"].get("ac_lint", {}).get("rebuttal_prefix", "inputs/ac-rebuttal-")
HEADING = POLICY["packages"].get("ac_lint", {}).get("rebuttal_heading", "### AC-")
BODY = """## 확인란

- **무엇을:** 무엇인가
- **수용 기준:**
  - [ ] AC-1 첫째 기준
  - [ ] AC-2 둘째 기준

## 변경 범위
"""
FIRST, SECOND = PREFIX + "1.md", PREFIX + "2.md"


def _rebuttal(*acs):
    return "\n\n".join(f"{HEADING}{n}\n- 반례: 없음" for n in acs) + "\n"


class TestUnionOfListedFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.udir = Path(self.tmp.name)
        (self.udir / Path(FIRST).parent).mkdir(parents=True, exist_ok=True)
        (self.udir / FIRST).write_text(_rebuttal(1), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def warn(self, inputs):
        return rebuttal_warnings(self.udir, {"inputs": list(inputs)}, BODY, POLICY)

    def test_two_files_cover_both(self):
        """① 두 파일이 AC 를 나눠 반박하면 경고가 0건이다."""
        (self.udir / SECOND).write_text(_rebuttal(2), encoding="utf-8")
        self.assertEqual([], self.warn([FIRST, SECOND]))

    def test_unlisted_file_is_not_counted(self):
        """② 둘째를 `inputs:` 에서 빼면 그 AC 가 경고에 나온다."""
        (self.udir / SECOND).write_text(_rebuttal(2), encoding="utf-8")
        self.assertEqual(["AC_UNREBUTTED AC-2"], self.warn([FIRST]))

    def test_unlisted_path_is_never_read(self):
        """③ 목록 밖 자리를 **디렉터리로** 두면 여전히 같은 경고가 나오고 예외가 오르지 않는다.

        그 경로를 읽으려는 구현은 여기서 실패한다 — 통과가 곧 「읽지 않았다」의 관측이다."""
        (self.udir / SECOND).mkdir()
        self.assertEqual(["AC_UNREBUTTED AC-2"], self.warn([FIRST]))

    def test_missing_file_reports_every_ac(self):
        """등록된 반박 파일이 하나도 실재하지 않으면 AC 전부가 경고에 나온다 — 종전 동작 그대로."""
        self.assertEqual(["AC_UNREBUTTED AC-1, AC-2"], self.warn([PREFIX + "없는파일.md"]))


if __name__ == "__main__":
    unittest.main()
