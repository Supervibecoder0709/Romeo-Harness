"""남의 저장소 판정 — `scenarios/11-router-foreign-repo.md` 「검증」 표의 **조건 id 목록을 파일에서 읽어** 루트와 대조한다.

이 검사가 있는 이유는 「라우터가 남의 저장소에서 돌았다」가 **낱말로는 언제나 참**이기 때문이다.
명령을 돌렸다는 것도, 파일이 생겼다는 것도 그 주장을 만들지 못한다(K-51) — 무엇이 참이어야 하는가를
조건으로 적고 그 조건을 종료 코드로 판정해야 한다.

**목록의 주인은 이 파일이 아니라 런북이다.** 여기에 조건을 못 박으면 문서와 검사가 갈리고,
갈린 뒤에는 어느 쪽이 요구인지 말할 수 없다(§11 — 요구하는 자리와 보는 자리를 같게 둔다).
그래서 `conditions()` 가 런북을 읽고, `TestTheListIsWhatIsCompared` 가 **목록을 양쪽으로 바꿔 넣어**
바뀐 목록으로 대조된다는 것을 매번 재확인한다. 한 줄을 빼면 그 조건은 조용히 건너뛰어지는 것이
아니라 요구에서 사라지고, 판정 코드가 없는 id 를 더하면 그 자리에서 막힌다.

반례는 **빈 루트가 아니라 그럴듯한 거짓 루트**다(§11). 빈 루트는 고치기 전에도 막혔으므로
판별력을 증명하지 않는다. 여기서 만드는 거짓 루트 둘은 폴더가 서 있고 spec 도 있다 —
하나는 `status: draft` 라 승인이 없고, 하나는 승인까지 됐는데 `facets` 가 하네스 자기 영역뿐이다.

같은 이유로 런북 「두 라우팅 규칙이 만나는 자리」의 **인용도 이 파일이 못 박지 않는다.** 인용은
`> L<줄번호>: <원문>` 으로 적히고 `quotes()` 가 그것을 읽어 `check_quotes()` 가 대상 `CLAUDE.md` 의
같은 줄과 글자로 대조한다. 2회차 검토자가 잡은 것이 이 자리다 — 런북은 `CLAUDE.md:76` 을 인용하는데
증거 명령의 `sed -n '65,67p;72p'` 가 그 줄을 인쇄하지 않았다. 숫자 오기가 아니라 요구하는 자리와
보는 자리가 **각각 하드코딩된 것**이 원인이라, 범위를 맞추는 대신 대조를 여기로 옮겼다(D-80).

대상 저장소 자체는 이 검사가 읽지 않는다. 실제 루트 판정은 증거 `foreign-router-verdict`,
실제 `CLAUDE.md` 인용 대조는 증거 `foreign-router-claude-md` 이고 그 명령은

    python3 tests/test_foreign_router.py --verdict <대상 루트>
    python3 tests/test_foreign_router.py --claude-md <대상 루트>/CLAUDE.md

다 — `required_checks` 에 넣으면 대상 저장소가 없는 머신(CI)에서 이 단위가 영원히 닫히지 않는다.
그래서 인용 대조의 판별력은 **합성 fixture 양쪽**(일치 · 줄 번호는 맞고 텍스트가 한 글자 다른 것)이 여기서 증명한다.
"""
import re
import sys
import tempfile
import unittest
from collections import namedtuple
from pathlib import Path

if __package__ in (None, ""):  # 스크립트로 직접 부를 때 sys.path[0] 이 tests/ 다 — 저장소 루트를 넣는다
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from romeo import HARNESS_ROOT, frontmatter

RUNBOOK = HARNESS_ROOT / "scenarios/11-router-foreign-repo.md"
VERIFY_HEADING = "## 검증"
CONFLICT_HEADING = "## 두 라우팅 규칙이 만나는 자리"

#: 하네스가 자기 도구·문서를 가리킬 때 쓰는 영역. 이것 **밖**의 값이 하나라도 있어야 남의 영역이다.
HARNESS_FACETS = frozenset({"tooling", "docs"})

#: 첫 칸이 백틱 조건 id 하나뿐인 표 줄만 조건으로 읽는다. 런북의 「목록의 문법」과 같은 규칙이다.
_ROW = re.compile(r"^\|\s*`([a-z0-9-]+)`\s*\|")

#: 인용 한 줄. 런북의 「인용의 문법」과 같은 규칙이다 — 콜론 뒤 한 칸부터 줄 끝까지가 **원문 그대로**다.
_QUOTE = re.compile(r"^> L(\d+): (.*)$")

#: 인용 한 건 — 출처 줄 번호 · 원문 · 그 인용이 실린 소절 제목.
Quote = namedtuple("Quote", "lineno text section")

#: 대조 실패 한 건 — 그 줄 번호에서 런북이 요구한 것과 대상 파일에 실제로 있는 것.
Mismatch = namedtuple("Mismatch", "lineno expected actual section")


def conditions(runbook_path=RUNBOOK):
    """런북의 「## 검증」 절에서 완료 조건 id 목록을 읽는다. 문서가 목록의 주인이다."""
    lines = Path(runbook_path).read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == VERIFY_HEADING)
    except StopIteration:
        raise AssertionError(f"{runbook_path}: '{VERIFY_HEADING}' 절이 없다 — 목록을 읽을 자리가 없다")
    out = []
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        m = _ROW.match(ln)
        if m:
            out.append(m.group(1))
    if not out:
        raise AssertionError(f"{runbook_path}: '{VERIFY_HEADING}' 절에 백틱 조건 id 표가 없다")
    return out


def _conflict_lines(runbook_path=RUNBOOK):
    """런북 「## 두 라우팅 규칙이 만나는 자리」 절의 줄을 `(소절 제목, 줄)` 로 돌려준다. 코드 펜스 안은 뺀다."""
    lines = Path(runbook_path).read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == CONFLICT_HEADING)
    except StopIteration:
        raise AssertionError(f"{runbook_path}: '{CONFLICT_HEADING}' 절이 없다 — 인용을 읽을 자리가 없다")
    out, section, fenced = [], CONFLICT_HEADING, False
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        if ln.startswith("```"):
            fenced = not fenced          # 문법 설명의 예시가 인용으로 세어지지 않게 한다
            continue
        if fenced:
            continue
        if ln.startswith("### "):
            section = ln[4:].strip()
            continue
        out.append((section, ln))
    return out


def conflict_sections(runbook_path=RUNBOOK):
    """그 절의 `###` 소절 제목 목록. 「충돌이 있는지 없는지」를 인쇄할 때 쓴다."""
    seen = []
    for section, _ in _conflict_lines(runbook_path):
        if section != CONFLICT_HEADING and section not in seen:
            seen.append(section)
    return seen


def quotes(runbook_path=RUNBOOK):
    """런북 「두 라우팅 규칙이 만나는 자리」 절의 인용을 `Quote(줄번호, 원문, 소절)` 목록으로 읽는다.

    **인용의 주인은 이 파일이 아니라 런북이다** — `conditions()` 와 같은 이유다(§11).
    여기에 줄 번호나 원문을 못 박으면 요구하는 자리와 보는 자리가 다시 갈린다.
    """
    out = []
    for section, ln in _conflict_lines(runbook_path):
        m = _QUOTE.match(ln)
        if m:
            out.append(Quote(int(m.group(1)), m.group(2), section))
    if not out:
        raise AssertionError(
            f"{runbook_path}: '{CONFLICT_HEADING}' 절에 '> L<줄번호>: <원문>' 인용이 하나도 없다 — "
            f"대조할 것이 없으면 그 절은 검사되지 않는다(§11)")
    return out


def check_quotes(claude_md, items=None):
    """`items` 중 대상 파일의 **같은 줄과 글자로 일치하지 않는** 것을 돌려준다. 빈 목록이 통과다.

    파일이 없으면 전부 실패로 센다 — **부재를 통과로 읽지 않는다.**
    줄 번호가 파일 밖이면 `actual` 이 `None` 이다.
    """
    items = quotes() if items is None else list(items)
    path = Path(claude_md).expanduser()
    if not path.is_file():
        return [Mismatch(q.lineno, q.text, None, q.section) for q in items]
    lines = path.read_text(encoding="utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()                      # 파일 끝 개행이 만든 빈 원소 — 그것을 줄로 세면 파일 밖이 빈 줄로 읽힌다
    bad = []
    for q in items:
        actual = lines[q.lineno - 1] if 1 <= q.lineno <= len(lines) else None
        if actual != q.text:
            bad.append(Mismatch(q.lineno, q.text, actual, q.section))
    return bad


def managed_block(claude_md):
    """대상 파일의 두 블록 경계를 **마커에서 계산해** 돌려준다. 못 찾으면 `None` 이다.

    런북 표의 숫자를 읽어 오지 않는다 — 그것을 읽으면 또 하나의 하드코딩이 된다.
    """
    lines = Path(claude_md).expanduser().read_text(encoding="utf-8").split("\n")
    start = end = None
    for i, ln in enumerate(lines, 1):
        if start is None and "romeo:managed start" in ln:
            start = i
        if "romeo:managed end" in ln:
            end = i
    total = len(lines) - 1 if lines and lines[-1] == "" else len(lines)
    if start is None or end is None:
        return None, total
    return (start, end), total


def _units(root):
    """대상 루트의 작업 단위 폴더. 폴더가 하나도 없으면 조건은 전부 거짓이다."""
    work = Path(root) / "docs" / "work"
    if not work.is_dir():
        return []
    return sorted(p for p in work.iterdir() if p.is_dir())


def _spec_frontmatter(unit):
    """단위의 `spec.md` frontmatter. 파일이 없거나 비어 있거나 읽히지 않으면 None — **부재를 통과로 읽지 않는다.**"""
    spec = Path(unit) / "spec.md"
    if not spec.is_file() or spec.stat().st_size == 0:
        return None
    try:
        data, _ = frontmatter.read(spec)
    except Exception:
        return None
    return None if data is None else data


def _unit_exists(fm):
    """라우터가 그 저장소에서 문서를 세웠는가."""
    return fm is not None


def _unit_active(fm):
    """사람이 그 저장소에서 한 번 더 승인했는가(D-27). `status` 만으로는 승인이 아니다."""
    return bool(fm) and fm.get("status") == "active" and bool(fm.get("approved_at"))


def _unit_foreign_facet(fm):
    """하네스가 자기 도구·문서가 아닌 영역을 분류했는가."""
    if not fm:
        return False
    return any(str(f) not in HARNESS_FACETS for f in (fm.get("facets") or []))


#: 조건 id → 판정 함수. 런북 목록에 있는데 여기 없는 id 는 `check` 가 **막는다**.
VERDICTS = {
    "unit-exists": _unit_exists,
    "unit-active": _unit_active,
    "unit-foreign-facet": _unit_foreign_facet,
}


def check(root, ids=None):
    """`ids` 중 `root` 가 만족하지 못한 조건을 순서대로 돌려준다. 빈 목록이 통과다.

    세 조건은 **한 단위**가 전부 만족해야 한다 — 서로 다른 단위가 하나씩 만족하는 것은 통과가 아니다.
    그래서 단위별로 실패 목록을 만들고 **가장 짧은 것**을 돌려준다. 통과한 단위가 있으면 빈 목록이다.
    """
    ids = conditions() if ids is None else list(ids)
    unknown = [i for i in ids if i not in VERDICTS]
    if unknown:
        raise AssertionError(
            f"판정 코드가 없는 조건 id: {unknown} — 런북에 조건을 더했으면 {Path(__file__).name} 의 "
            f"VERDICTS 에 판정 함수를 같은 커밋에서 함께 넣는다(§11)")
    units = _units(root)
    if not units:
        return list(ids)
    best = None
    for unit in units:
        fm = _spec_frontmatter(unit)
        failed = [i for i in ids if not VERDICTS[i](fm)]
        if best is None or len(failed) < len(best):
            best = failed
        if not best:
            break
    return best


# --- 합성 루트 ---------------------------------------------------------------

_BODY = "\n# 합성 단위\n\n## 확인란\n\n- **무엇을:** 합성 루트다.\n"


def make_root(base, unit_id, status="active", approved=True, facets=("docs", "security"), spec=True):
    """대상 저장소 모양의 합성 루트를 만든다. `spec=False` 면 폴더만 서고 spec 이 없다."""
    root = Path(base)
    unit = root / "docs" / "work" / unit_id
    unit.mkdir(parents=True, exist_ok=True)
    if spec:
        frontmatter.write(unit / "spec.md", {
            "id": unit_id,
            "type": "spec",
            "title": "합성 단위",
            "unit": "T1",
            "mode": "delivery",
            "intent": "write",
            "facets": list(facets),
            "status": status,
            "approved_at": "2026-09-04T23:44:05+09:00" if approved else None,
            "approved_by": "Supervibecoder0709" if approved else None,
        }, _BODY)
    return root


def make_claude_md(base, items, mutate=None, truncate=None, name="CLAUDE.md"):
    """런북의 인용 목록 그대로를 담는 합성 `CLAUDE.md` 를 만든다.

    fixture 를 인용 목록에서 **생성**하므로, 런북이 바뀌면 fixture 도 함께 바뀐다 —
    한쪽만 고쳐도 다른 쪽이 따라오지 않는 구조를 여기서도 만들지 않는다(§11).

    `mutate` 에 줄 번호를 주면 그 줄의 텍스트를 **한 글자만** 바꾼다 — 줄 번호는 맞는데
    내용이 다른 **그럴듯한 거짓 값**이고, 빈 파일과 달리 고치기 전 상태와 구별된다.
    `truncate` 를 주면 파일을 그 줄 수에서 끊는다.
    """
    items = list(items)
    last = max(q.lineno for q in items)
    lines = [f"# 합성 CLAUDE.md {i}번째 줄 — 인용 대상이 아니다" for i in range(1, last + 1)]
    for q in items:
        text = q.text
        if mutate == q.lineno:
            text = text[:-1] + ("X" if not text.endswith("X") else "Y")
        lines[q.lineno - 1] = text
    if truncate is not None:
        lines = lines[:truncate]
    path = Path(base) / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


class TestConditionsComeFromTheRunbook(unittest.TestCase):
    """AC-2 앞부분 — 목록을 파일에서 읽는다."""

    def test_the_runbook_owns_the_list(self):
        ids = conditions()
        for cid in VERDICTS:
            self.assertIn(cid, ids, f"'{cid}' 가 런북 「검증」 표에 없다 — 판정 코드만 있고 요구가 없다(§11)")
        self.assertEqual(len(ids), len(set(ids)), f"런북 「검증」 표에 조건 id 가 중복된다: {ids}")

    def test_a_runbook_without_the_section_is_refused(self):
        """그럴듯한 거짓 값 — 절 제목만 바꿔도 검사는 조용히 0건으로 통과하지 않는다."""
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "runbook.md"
            fake.write_text(RUNBOOK.read_text(encoding="utf-8").replace(VERIFY_HEADING, "## 확인"),
                            encoding="utf-8")
            with self.assertRaises(AssertionError):
                conditions(fake)

    def test_the_runbook_carries_the_five_sections(self):
        """런북이 다섯 절을 담는가 — check-2 와 같은 것을 보지만 여기서는 어느 절이 빠졌는지 이름으로 말한다."""
        text = RUNBOOK.read_text(encoding="utf-8")
        for heading in ["## 어디서 실행하는가", "## 무엇이 대상 저장소에 서는가",
                        "## 두 라우팅 규칙이 만나는 자리", "## 검증", "## 되돌리기"]:
            self.assertIn(heading, text, f"런북에 '{heading}' 절이 없다")


class TestSyntheticRoots(unittest.TestCase):
    """AC-3 — 조건을 만족하지 않는 합성 루트에서 실패하고 만족하는 합성 루트에서 통과한다."""

    def setUp(self):
        self.ids = conditions()

    def test_satisfying_root_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-pass")
            self.assertEqual(check(root, self.ids), [])

    def test_draft_unit_fails(self):
        """그럴듯한 거짓 루트 ① — 폴더도 spec 도 서 있는데 `status: draft` 라 승인이 없다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-draft", status="draft", approved=False)
            self.assertEqual(check(root, self.ids), ["unit-active"])

    def test_harness_only_facets_fail(self):
        """그럴듯한 거짓 루트 ② — 승인까지 됐는데 `facets` 가 하네스 자기 영역뿐이다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-home", facets=("tooling", "docs"))
            self.assertEqual(check(root, self.ids), ["unit-foreign-facet"])

    def test_status_active_without_approved_at_fails(self):
        """그럴듯한 거짓 루트 ③ — `status: active` 만 손으로 적고 `approved_at` 이 비어 있다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-unapproved", approved=False)
            self.assertEqual(check(root, self.ids), ["unit-active"])

    def test_empty_root_fails_every_condition(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(check(td, self.ids), self.ids, "빈 루트에서 실패한 것이 목록 전체가 아니다")

    def test_folder_without_spec_is_not_a_unit(self):
        """**부재를 통과로 읽지 않는다** — 이름만 만든 폴더는 라우터가 세운 것이 아니다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-empty", spec=False)
            self.assertEqual(check(root, self.ids), self.ids)

    def test_conditions_split_across_two_units_is_not_a_pass(self):
        """한 단위가 전부 만족해야 한다 — 나눠 가진 두 단위는 통과가 아니다."""
        with tempfile.TemporaryDirectory() as td:
            make_root(td, "feat-20260904-synthetic-a", status="draft", approved=False,
                      facets=("docs", "security"))
            root = make_root(td, "feat-20260904-synthetic-b", facets=("tooling", "docs"))
            self.assertNotEqual(check(root, self.ids), [], "두 단위가 조건을 나눠 가졌는데 통과했다")


class TestTheListIsWhatIsCompared(unittest.TestCase):
    """AC-2 뒷부분 — 목록을 양쪽으로 바꿔 넣어 **바뀐 목록으로 대조한다**는 것을 재확인한다."""

    def setUp(self):
        self.ids = conditions()

    def _runbook_with(self, replace, into):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        fake = Path(td.name) / "runbook.md"
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn(replace, text, f"런북에 '{replace}' 줄이 없다 — 바꿔 넣을 자리가 사라졌다")
        fake.write_text(text.replace(replace, into, 1), encoding="utf-8")
        return fake

    def test_removing_a_row_removes_the_requirement(self):
        """`unit-foreign-facet` 줄을 지우면, 하네스 영역뿐인 루트가 **통과한다** — 건너뛰는 것이 아니라 요구가 사라진다."""
        row = "| `unit-foreign-facet` |"
        mutated = conditions(self._runbook_with(row, "| 그 줄을 지운다 |"))
        self.assertNotIn("unit-foreign-facet", mutated)
        self.assertEqual(len(mutated), len(self.ids) - 1)

        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-home", facets=("tooling", "docs"))
            self.assertEqual(check(root, self.ids), ["unit-foreign-facet"],
                             "원래 목록이 하네스 영역뿐인 루트를 잡지 못했다")
            self.assertEqual(check(root, mutated), [], "바뀐 목록이 여전히 남의 영역을 요구한다")

    def test_adding_a_condition_without_verdict_code_blocks(self):
        """그럴듯한 거짓 값 — 형태는 조건 id 인데 판정 코드가 없는 항목을 더하면 그 자리에서 막힌다."""
        fake_id = "unit-reviewed"
        mutated = conditions(self._runbook_with(
            "| `unit-foreign-facet` |",
            f"| `{fake_id}` | 판정 코드가 없는 그럴듯한 거짓 조건 |\n| `unit-foreign-facet` |"))
        self.assertIn(fake_id, mutated)
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-pass")
            self.assertEqual(check(root, self.ids), [], "만족하는 루트가 원래 목록에서 막혔다")
            with self.assertRaises(AssertionError):
                check(root, mutated)


class TestQuotesComeFromTheRunbook(unittest.TestCase):
    """AC-5 앞부분 — 인용 목록을 런북에서 읽는다."""

    def test_the_runbook_owns_the_quotes(self):
        items = quotes()
        self.assertGreaterEqual(len(items), 2, "런북 「두 라우팅 규칙이 만나는 자리」의 인용이 2건 미만이다")
        for q in items:
            self.assertGreater(q.lineno, 0, f"줄 번호가 1보다 작다: {q}")
            self.assertTrue(q.text, f"인용문이 비어 있다: {q}")
            self.assertTrue(q.section, f"소절 밖의 인용이다 — 어느 충돌의 근거인지 말할 수 없다: {q}")

    def test_the_syntax_example_is_not_counted_as_a_quote(self):
        """코드 펜스 안의 문법 설명이 인용으로 세어지지 않는다 — 세어지면 대조할 수 없는 자리표시자가 요구가 된다."""
        for q in quotes():
            self.assertNotIn("<줄번호>", q.text)
            self.assertNotIn("원문 그대로", q.text)

    def test_a_runbook_without_the_section_is_refused(self):
        """그럴듯한 거짓 값 — 절 제목만 바꿔도 검사는 조용히 0건으로 통과하지 않는다."""
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "runbook.md"
            fake.write_text(RUNBOOK.read_text(encoding="utf-8").replace(CONFLICT_HEADING, "## 두 규칙"),
                            encoding="utf-8")
            with self.assertRaises(AssertionError):
                quotes(fake)

    def test_the_conflicts_are_recorded_as_subsections(self):
        """충돌 관측이 소절로 남아 있는가 — 「없다」도 결과지만, 그때는 소절 0건인 것이 인쇄돼야 한다(K-51)."""
        sections = conflict_sections()
        self.assertEqual(sections, sorted(set(sections), key=sections.index), "소절 제목이 중복된다")


class TestSyntheticClaudeMd(unittest.TestCase):
    """AC-5 뒷부분 — 합성 fixture 로 **일치·불일치 양쪽**을 판정한다. 대상 파일이 없는 머신(CI)에서도 판별력이 남는다."""

    def setUp(self):
        self.items = quotes()

    def test_matching_fixture_passes(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(check_quotes(make_claude_md(td, self.items), self.items), [])

    def test_one_character_difference_fails(self):
        """그럴듯한 거짓 값 ① — 줄 번호는 맞는데 텍스트가 **한 글자** 다르다. 빈 파일과 달리 고치기 전 상태와 구별된다(§11)."""
        target = self.items[-1].lineno
        with tempfile.TemporaryDirectory() as td:
            bad = check_quotes(make_claude_md(td, self.items, mutate=target), self.items)
            self.assertEqual([m.lineno for m in bad], [target],
                             "한 글자 다른 줄을 잡지 못했거나 엉뚱한 줄까지 잡았다")
            self.assertNotEqual(bad[0].actual, bad[0].expected)
            self.assertEqual(len(bad[0].actual), len(bad[0].expected), "반례가 한 글자 차이가 아니다")

    def test_every_quoted_line_is_individually_load_bearing(self):
        """인용 한 줄씩 전부 바꿔 본다 — 어느 한 줄이라도 대조에서 빠져 있으면 여기서 드러난다."""
        with tempfile.TemporaryDirectory() as td:
            for q in self.items:
                bad = check_quotes(make_claude_md(td, self.items, mutate=q.lineno), self.items)
                self.assertEqual([m.lineno for m in bad], [q.lineno], f"L{q.lineno} 가 대조되지 않는다")

    def test_a_line_past_the_end_of_file_fails(self):
        """그럴듯한 거짓 값 ② — 파일이 짧아져 인용한 줄이 사라졌다. `actual` 이 None 으로 남는다."""
        target = max(q.lineno for q in self.items)
        with tempfile.TemporaryDirectory() as td:
            path = make_claude_md(td, self.items, truncate=target - 1)
            bad = check_quotes(path, self.items)
            self.assertIn(target, [m.lineno for m in bad])
            self.assertIsNone(next(m for m in bad if m.lineno == target).actual)

    def test_a_missing_file_fails_every_quote(self):
        with tempfile.TemporaryDirectory() as td:
            bad = check_quotes(Path(td) / "없는파일.md", self.items)
            self.assertEqual(len(bad), len(self.items), "파일 부재를 통과로 읽었다")


class TestTheQuoteListIsWhatIsCompared(unittest.TestCase):
    """AC-5 — 인용을 더하거나 지우면 **대조 대상이 함께 바뀐다**. AC-2 의 `TestTheListIsWhatIsCompared` 와 같은 패턴이다."""

    def setUp(self):
        self.items = quotes()

    def _runbook_with(self, replace, into):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        fake = Path(td.name) / "runbook.md"
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn(replace, text, f"런북에 '{replace}' 줄이 없다 — 바꿔 넣을 자리가 사라졌다")
        fake.write_text(text.replace(replace, into, 1), encoding="utf-8")
        return fake

    def test_adding_a_quote_adds_what_is_compared(self):
        """그럴듯한 거짓 값 — 형태는 인용인데 대상 파일의 그 줄과 다른 항목을 더하면 **그 자리에서 실패한다**."""
        first = self.items[0]
        row = f"> L{first.lineno}: {first.text}"
        added_line = 1 if first.lineno != 1 else 2
        mutated = quotes(self._runbook_with(row, f"> L{added_line}: 대상 파일에 없는 그럴듯한 인용\n{row}"))
        self.assertEqual(len(mutated), len(self.items) + 1)
        with tempfile.TemporaryDirectory() as td:
            path = make_claude_md(td, self.items)          # fixture 는 **원래** 목록으로 만든다
            self.assertEqual(check_quotes(path, self.items), [], "원래 목록이 맞는 fixture 에서 실패했다")
            self.assertEqual([m.lineno for m in check_quotes(path, mutated)], [added_line],
                             "더한 인용이 대조되지 않았다 — 목록을 늘려도 보는 자리가 그대로다")

    def test_removing_a_quote_removes_what_is_compared(self):
        """한 줄을 지우면 그 인용은 조용히 건너뛰어지는 것이 아니라 **요구에서 사라진다**."""
        gone = self.items[-1]
        row = f"> L{gone.lineno}: {gone.text}"
        mutated = quotes(self._runbook_with(row, "그 인용을 지운다."))
        self.assertNotIn(gone.lineno, [q.lineno for q in mutated])
        with tempfile.TemporaryDirectory() as td:
            path = make_claude_md(td, self.items, mutate=gone.lineno)
            self.assertEqual([m.lineno for m in check_quotes(path, self.items)], [gone.lineno])
            self.assertEqual(check_quotes(path, mutated), [], "지운 인용을 여전히 요구한다")

    def test_moving_a_quote_moves_what_is_compared(self):
        """줄 번호만 옮기면 대조하는 줄도 옮겨진다 — 옮긴 자리의 실제 줄이 다르면 실패한다."""
        q = self.items[0]
        moved_to = max(x.lineno for x in self.items) + 7
        mutated = quotes(self._runbook_with(f"> L{q.lineno}: {q.text}", f"> L{moved_to}: {q.text}"))
        self.assertIn(moved_to, [x.lineno for x in mutated])
        with tempfile.TemporaryDirectory() as td:
            path = make_claude_md(td, self.items)
            self.assertEqual([m.lineno for m in check_quotes(path, mutated)], [moved_to])


def _claude_md(path):
    """실제 대상 `CLAUDE.md` 를 판정한다 — 증거 `foreign-router-claude-md` 가 부르는 자리다.

    인쇄하는 것 셋: 두 블록의 **경계**(마커에서 계산) · 「충돌이 있는지 없는지」(소절 목록) ·
    인용 한 줄씩의 대조 결과. 충돌이 없으면 「없다」를 근거와 함께 적는 것이 결과다(K-51).
    """
    path = Path(path).expanduser()
    items = quotes()
    sections = conflict_sections()
    print(f"대상 파일: {path}")
    print(f"런북: {RUNBOOK.relative_to(HARNESS_ROOT)} 「{CONFLICT_HEADING}」 · 인용 {len(items)}건")
    if not path.is_file():
        print("판정: FAIL — 그런 파일이 없다")
        return 1

    block, total = managed_block(path)
    print(f"총 {total}줄")
    if block:
        print(f"두 블록의 경계(마커에서 계산): BMad 1-{block[0] - 1} · Romeo {block[0]}-{block[1]}")
    else:
        print("두 블록의 경계: romeo:managed 마커가 없다 — 이 파일에 Romeo 블록이 없다")

    if sections:
        print(f"충돌 실측: 소절 {len(sections)}건 — 같은 상황을 서로 다르게 지시하는 구절이 「없다」가 아니다")
        for s in sections:
            print(f"  · {s}")
    else:
        print("충돌 실측: 소절 0건 — 같은 상황을 서로 다르게 지시하는 구절이 「없다」는 것이 이 관통의 결과다(K-51)")

    bad = {m.lineno: m for m in check_quotes(path, items)}
    section = None
    for q in items:
        if q.section != section:
            section = q.section
            print(f"인용 대조 · {section}")
        if q.lineno in bad:
            actual = bad[q.lineno].actual
            print(f"  L{q.lineno} 불일치")
            print(f"    런북: {q.text!r}")
            print(f"    실제: {actual!r}" if actual is not None else "    실제: (그 줄이 파일에 없다)")
        else:
            print(f"  L{q.lineno} 일치 · {q.text}")
    print(f"판정: {'PASS — 인용 %d건 전부 실제 줄과 글자로 일치' % len(items) if not bad else 'FAIL — 불일치 %d건: %s' % (len(bad), sorted(bad))}")
    return 0 if not bad else 1


def _verdict(root):
    """실제 대상 루트를 판정한다 — 증거 `foreign-router-verdict` 가 부르는 자리다."""
    root = Path(root).expanduser()
    ids = conditions()
    print(f"대상 루트: {root}")
    print(f"런북: {RUNBOOK.relative_to(HARNESS_ROOT)} 「{VERIFY_HEADING}」 · 조건 {len(ids)}건 {ids}")
    if not root.is_dir():
        print("판정: FAIL — 그런 루트가 없다")
        return 1
    for unit in _units(root):
        fm = _spec_frontmatter(unit)
        got = {i: VERDICTS[i](fm) for i in ids}
        print(f"  {unit.name}: " + " · ".join(f"{k}={'참' if v else '거짓'}" for k, v in got.items()))
        if fm:
            print(f"    status={fm.get('status')!r} approved_at={fm.get('approved_at')!r} facets={fm.get('facets')!r}")
    failed = check(root, ids)
    print(f"판정: {'PASS' if not failed else 'FAIL — 만족하지 못한 조건: ' + ', '.join(failed)}")
    return 0 if not failed else 1


_EVIDENCE = {"--verdict": _verdict, "--claude-md": _claude_md}

if __name__ == "__main__":
    for flag, fn in _EVIDENCE.items():
        if flag in sys.argv:
            i = sys.argv.index(flag)
            if i + 1 >= len(sys.argv):
                print(f"사용법: python3 tests/test_foreign_router.py {flag} <경로>", file=sys.stderr)
                sys.exit(2)
            sys.exit(fn(sys.argv[i + 1]))
    unittest.main()
