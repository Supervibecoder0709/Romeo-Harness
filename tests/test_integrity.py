"""승격 문서와 코드의 대조·링크·id 중복 — `feat-20260909-promote-integrity-kchq`.

**반례는 빈 값이 아니라 그럴듯한 거짓 값이다.** 「목록이 비면 막힌다」만 증명한 검사는 고치기 전 상태와
구별되지 않는다 — 고치기 전에도 빈 목록은 아무것도 통과시키지 않았고, 통과한 것은 **형태가 그럴듯하고
내용이 거짓인** 목록이었다. 그래서 위조는 전부 유효한 문법·유효한 표 모양을 유지한다 —
목록이 없는 ④ 도 예외가 아니다. 거기서 그럴듯한 것은 빈 목록이 아니라 **아직 아무것도 올리지 않은 저장소**다.

**같은 사본에서 0 과 1 을 잇는다.** 위조 전 종료 코드 0 을 먼저 관측하고, 그 사본에 위조를 얹어 1 을 관측한다 —
그래야 종료 코드의 차이가 그 위조에서 나온 것이라고 말할 수 있다. 다른 사본의 0 과 이 사본의 1 을 나란히
놓는 것은 대조가 아니다(AC-3).
"""
import shutil
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from romeo import HARNESS_ROOT
from romeo.close import close_unit, format_close
from romeo.docs import _approval_key, _approved_blobs, find_unit_dir
from romeo.integrity import check_call_ids

#: 위조 사본에 옮기는 파일. 대조에 필요한 최소 집합이다 — 이만큼이면 `bin/romeo integrity` 가 exit 0 이다.
COPY_FILES = ("romeo/close.py", "romeo/validate.py", "core/policy/packages.yaml",
              "docs/current/enforcement.md")

FIXTURES = HARNESS_ROOT / "fixtures/integrity"
UNIT = "feat-20260909-promote-integrity-kchq"


def integrity(root):
    """`bin/romeo integrity --root <root>` 를 실행해 (종료 코드, 표준 출력+표준 오류) 를 돌려준다."""
    p = subprocess.run([str(HARNESS_ROOT / "bin/romeo"), "integrity", "--root", str(root)],
                       cwd=str(HARNESS_ROOT), capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class CleanRoot(unittest.TestCase):
    def test_repo_root_is_clean(self):
        """AC-6 — 인자 없이 저장소 루트에서 돌면 exit 0 이고 루트와 대조한 개수를 인쇄한다."""
        p = subprocess.run([str(HARNESS_ROOT / "bin/romeo"), "integrity"],
                           cwd=str(HARNESS_ROOT), capture_output=True, text=True)
        out = p.stdout + p.stderr
        self.assertEqual(p.returncode, 0, out)
        self.assertIn(str(HARNESS_ROOT), out)          # 검사한 루트 = 그 실행의 작업 디렉터리
        self.assertRegex(out, r"대조 \d+건")            # 대조한 id 개수


class Forgery(unittest.TestCase):
    """위조 상태. 각각 **같은 사본**에서 위조 전 0 과 위조 후 1 을 잇는다.

    ①②③ 은 AC-3 이 적은 셋이다. ④⑤ 는 1회차 검토자가 낸 두 결함을 재현한다 —
    셋 다 **양쪽 집합이 비지 않고 id 가 겹치지 않는** 위조라, 한쪽 집합이 통째로 비는 경우와
    같은 id 가 두 수준으로 적히는 경우를 건드리지 않았다. 그 두 자리가 ④⑤ 다."""

    def _copy(self, tmp):
        root = Path(tmp) / "copy"
        for rel in COPY_FILES:
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(HARNESS_ROOT / rel, dst)
        code, out = integrity(root)
        self.assertEqual(code, 0, f"위조 전 사본이 이미 어긋나 있다 — 위조의 효과를 말할 수 없다:\n{out}")
        return root

    def test_code_gains_a_judgment(self):
        """① 코드가 목록을 앞질러 간다 — 기존 호출과 같은 형태의 유효한 check() 한 줄을 더한다."""
        with TemporaryDirectory() as tmp:
            root = self._copy(tmp)
            src = root / "romeo/close.py"
            anchor = '    check("AC_ALL_CHECKED"'
            text = src.read_text(encoding="utf-8")
            self.assertIn(anchor, text)
            src.write_text(text.replace(anchor, '    check("PROMOTION_FORGED_ONE", True)\n' + anchor, 1),
                           encoding="utf-8")
            code, out = integrity(root)
            self.assertEqual(code, 1, out)
            self.assertIn("PROMOTION_FORGED_ONE", out)

    def test_document_loses_a_row(self):
        """② 목록에서 한 행을 지운다 — 코드에만 있는 판정이 인쇄된다."""
        with TemporaryDirectory() as tmp:
            root = self._copy(tmp)
            doc = root / "docs/current/enforcement.md"
            lines = doc.read_text(encoding="utf-8").split("\n")
            i, dropped = _first_row(lines)
            del lines[i]
            doc.write_text("\n".join(lines), encoding="utf-8")
            code, out = integrity(root)
            self.assertEqual(code, 1, out)
            self.assertIn(dropped, out)

    def test_document_renames_a_row(self):
        """③ 목록의 한 id 를 코드에 없는 그럴듯한 이름으로 바꾼다 — 양쪽 어긋남이 인쇄된다."""
        with TemporaryDirectory() as tmp:
            root = self._copy(tmp)
            doc = root / "docs/current/enforcement.md"
            lines = doc.read_text(encoding="utf-8").split("\n")
            i, real = _first_row(lines)
            lines[i] = lines[i].replace(f"`{real}`", "`PROMOTION_FORGED_THREE`", 1)
            doc.write_text("\n".join(lines), encoding="utf-8")
            code, out = integrity(root)
            self.assertEqual(code, 1, out)
            self.assertIn("PROMOTION_FORGED_THREE", out)   # 문서에만 있는 거짓 이름
            self.assertIn(real, out)                        # 코드에만 남은 진짜 이름

    def test_document_disappears(self):
        """④ 목록이 통째로 없어진다 — 한쪽 집합이 비어도 두 집합의 차이를 보고한다.

        빈 쪽을 「대조 건너뜀」으로 넘기면 판정이 49건 남은 코드가 목록 없이 통과한다.
        빈 값이 아니라 그럴듯한 거짓 값이어야 한다는 규칙(§11)의 예외가 아니다 —
        여기서 그럴듯한 것은 빈 목록이 아니라 **목록이 없다는 상태 자체**이고,
        그 상태는 고치기 전 코드에서 위반 0건으로 인쇄됐다."""
        with TemporaryDirectory() as tmp:
            root = self._copy(tmp)
            doc = root / "docs/current/enforcement.md"
            _i, real = _first_row(doc.read_text(encoding="utf-8").split("\n"))
            doc.unlink()
            code, out = integrity(root)
            self.assertEqual(code, 1, out)
            self.assertIn(real, out)              # 코드에만 남은 판정이 인쇄된다

    def test_document_repeats_an_id_at_another_level(self):
        """⑤ 같은 id 를 반대 수준으로 한 행 더 적는다 — 대조는 `(id, 수준)` **쌍**의 집합이다(AC-2).

        id 만 키로 삼으면 뒤에 오는 행이 앞의 행을 덮어써서, 문서에만 있는 쌍이 읽는 단계에서
        사라진다. 그러면 두 집합이 실제로 다른데도 일치로 처리된다."""
        with TemporaryDirectory() as tmp:
            root = self._copy(tmp)
            doc = root / "docs/current/enforcement.md"
            lines = doc.read_text(encoding="utf-8").split("\n")
            i, real = _first_row(lines)
            forged = _flip_level(lines[i])
            self.assertNotEqual(forged, lines[i])
            lines.insert(i, forged)               # 진짜 행 **앞**에 — 덮어쓰기면 사라지는 자리다
            doc.write_text("\n".join(lines), encoding="utf-8")
            code, out = integrity(root)
            self.assertEqual(code, 1, out)
            self.assertIn(real, out)              # 문서에만 있는 쌍의 id 가 인쇄된다


def _flip_level(line):
    """표 한 행의 수준 칸을 반대 수준으로 바꾼 사본. 나머지 칸은 그대로다 — 표의 모양은 유효하게 둔다."""
    cells = line.split("|")
    for i, cell in enumerate(cells):
        if cell.strip() == "error":
            cells[i] = cell.replace("error", "warning")
            return "|".join(cells)
        if cell.strip() == "warning":
            cells[i] = cell.replace("warning", "error")
            return "|".join(cells)
    raise AssertionError("표 행에서 수준 칸을 찾지 못했다")


def _first_row(lines):
    """표의 첫 데이터 행 (줄 번호, 그 행의 id). 백틱으로 감싼 첫 열을 id 로 본다."""
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("| `") and s.endswith("|"):
            return i, s.split("`")[1]
    raise AssertionError("승격 문서에서 표의 데이터 행을 찾지 못했다")


def _approval_commit_any_status(root, unit):
    """이 단위의 승인 커밋 — `status` 가 `done` 이 된 뒤에도 찾는다.

    `docs.approval_commit` 은 `status: active` 를 요구한다(`_is_approved`). 계약을 만드는 자리에서는 옳은 조건이지만,
    이 검사가 겨눈 것은 「승인 시점과 지금의 판정 id 집합이 같다」는 **과거 사실**이라 종료 뒤에도 참이어야 한다.
    그래서 승인 여부 게이트만 건너뛰고, 승인 커밋을 고르는 규칙(현재 승인 키와 같은 승인을 담은 첫 커밋)은 그대로 쓴다."""
    from romeo import frontmatter
    fm, _ = frontmatter.read(find_unit_dir(root, unit) / "spec.md")
    want = _approval_key(fm)
    for sha, cfm in _approved_blobs(root, unit):
        if _approval_key(cfm) == want:
            return sha
    raise AssertionError(f"{unit}: 현재 승인을 담은 커밋을 이력에서 찾지 못했다")


class UnchangedJudgments(unittest.TestCase):
    def test_close_registers_the_same_ids_as_at_approval(self):
        """AC-7 — 이 단위는 종료 판정을 더하지도 빼지도 않는다.

        승인 커밋은 `bin/romeo envelope build` 가 이력에서 찾는 것과 같은 커밋이다(`docs.approval_commit` 의 규칙)."""
        sha = _approval_commit_any_status(HARNESS_ROOT, UNIT)
        then = subprocess.run(["git", "show", f"{sha}:romeo/close.py"], cwd=str(HARNESS_ROOT),
                              capture_output=True, text=True, check=True).stdout
        now = (HARNESS_ROOT / "romeo/close.py").read_text(encoding="utf-8")
        self.assertEqual(set(check_call_ids(then)), set(check_call_ids(now)))


class PromotionCandidate(unittest.TestCase):
    """AC-8 — `bin/romeo close` 의 출력. cmd_close 가 인쇄하는 것이 곧 `format_close(close_unit(…))` 다."""

    def _close_output(self, root):
        return format_close(close_unit(UNIT, project_root=root, dry_run=True, rerun=False))

    def _root(self, tmp):
        """대조가 성립하는 최소 루트 — 판정을 뽑을 코드·정책표, 승격 문서, 그리고 닫으려는 단위 하나."""
        root = Path(tmp) / "root"
        for rel in COPY_FILES:
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(HARNESS_ROOT / rel, dst)
        unit = root / "docs/work" / UNIT
        unit.mkdir(parents=True)
        shutil.copy2(HARNESS_ROOT / "docs/work" / UNIT / "spec.md", unit / "spec.md")
        return root

    def test_no_line_when_the_two_sets_agree(self):
        with TemporaryDirectory() as tmp:
            out = self._close_output(self._root(tmp))
            self.assertNotIn("승격 후보", out)

    def test_line_when_the_two_sets_differ(self):
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            doc = root / "docs/current/enforcement.md"
            lines = doc.read_text(encoding="utf-8").split("\n")
            i, _dropped = _first_row(lines)
            del lines[i]
            doc.write_text("\n".join(lines), encoding="utf-8")
            out = self._close_output(root)
            self.assertTrue(any(ln.startswith("승격 후보") for ln in out.split("\n")), out)

    def test_line_when_the_document_is_missing(self):
        """목록이 통째로 없는 것도 「다른 상태」다(AC-8). 대조를 건너뛰면 이 줄이 사라진다 —
        판정이 남은 채 아무것도 올리지 않은 저장소가 종료 검사에서 아무 말도 듣지 않게 된다."""
        with TemporaryDirectory() as tmp:
            root = self._root(tmp)
            (root / "docs/current/enforcement.md").unlink()
            out = self._close_output(root)
            self.assertTrue(any(ln.startswith("승격 후보") for ln in out.split("\n")), out)


class Fixtures(unittest.TestCase):
    def test_broken_link(self):
        """AC-4 — docs/current 의 깨진 상대 링크를 인쇄하고 exit 1."""
        code, out = integrity(FIXTURES / "broken-link")
        self.assertEqual(code, 1, out)
        self.assertIn("없는-파일.md", out)

    def test_broken_link_notations(self):
        """AC-4 판별 — 괄호 안에 제목이나 공백이 더 붙어도 같은 규칙 하나가 판정한다.

        2회차의 `LINK_RE` 는 경로 **바로 뒤에** 닫는 괄호가 오는 표기만 모았다. 그래서
        `[없는 문서](missing.md "설명")` 과 `[없는 문서](missing.md )` 은 링크로 보이지도 않았고,
        대상이 없어도 아무것도 인쇄되지 않았다 — 다른 위반이 없으면 종료 코드는 0 이었다.
        표기를 하나씩 세어 더하는 대신 「첫 공백 앞까지가 경로 후보」 규칙 하나로 판정한다."""
        code, out = integrity(FIXTURES / "broken-link")
        self.assertEqual(code, 1, out)
        self.assertIn("없는-제목붙은.md", out)      # 경로 뒤에 공백과 따옴표 제목이 붙은 표기
        self.assertIn("없는-공백붙은.md", out)      # 경로 뒤에 공백만 붙은 표기
        # 같은 표기의 실재하는 대상은 **링크 위반으로** 잡지 않는다.
        # 출력 전체가 아니라 BROKEN_LINK 줄만 본다 — 이 fixture 루트의 문서는 승격 등록부에 없으므로
        # `UNCHECKED_PROMOTION` 줄에도 같은 이름이 나온다. 그것은 이 검사가 보는 것이 아니다.
        broken = [ln for ln in out.split("\n") if "BROKEN_LINK" in ln]
        self.assertNotIn("sibling.md", "\n".join(broken))

    def test_duplicate_unit_id(self):
        """AC-5 — 폴더 이름은 다르고 frontmatter id 만 같으면 exit 1 이고 그 id 와 폴더를 인쇄한다."""
        code, out = integrity(FIXTURES / "duplicate-id")
        self.assertEqual(code, 1, out)
        self.assertIn("feat-20260101-collision-aaaa", out)
        self.assertIn("first", out)
        self.assertIn("second", out)

    def test_same_title_is_not_duplicate(self):
        """AC-5 반대 방향 — id 는 다르고 title 만 같으면 exit 0. 제목으로 막지 않는다."""
        code, out = integrity(FIXTURES / "same-title")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
