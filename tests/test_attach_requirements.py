"""attach 요구사항 목록이 실재하는 출처를 가리키고, 빠짐없이 담는지 대조한다.

요구가 사는 자리는 docs/planning/open-questions.md 이고 보는 자리는
docs/requirements/attach-requirements.md 다. 둘을 로드 시점에 대조한다(AGENTS §11).

판별력은 세 가상 상태로 매번 재확인한다 — 없는 Q id 주입 · 없는 단위 id 주입 ·
M1~M3 출처 Q 하나를 두 표에서 제거. 세 치환은 전부 **해당 표 행**을 통째로 갈아 끼운다.
문서 상단 산문에도 같은 문자열이 나오므로, 첫 등장만 바꾸면 표는 그대로인 채 통과한다.

**가상 상태는 실제 검사 함수에 먹인다.** 판정은 전부 coverage_violations·included_violations·
excluded_violations 안에 있고, 실검사와 가상 검사가 그 같은 함수를 부른다. 검사 하나를
그 함수에서 지우면 실검사가 아니라 **가상 검사가 먼저 깨진다** — 가상 상태를 따로 손으로
확인하면 그 확인은 실검사와 이어져 있지 않아 아무것도 판별하지 못한다.

**행은 Q 단위이고 중복은 살려서 읽는다.** 표를 Q id 를 키로 한 사전으로 읽으면 같은 Q 의
두 번째 행이 첫 행을 덮어써서 「정확히 한 번」(AC-1)을 볼 수 없다. 그래서 파서는 (Q, 셀) 쌍의
목록을 돌려주고, 출현 횟수를 세는 것은 coverage_violations 다.
"""

import collections
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "docs" / "requirements" / "attach-requirements.md"
OPEN_QUESTIONS = ROOT / "docs" / "planning" / "open-questions.md"
WORK = ROOT / "docs" / "work"

# 이 목록이 담아야 하는 관측을 낸 세 관통. 마일스톤 번호가 붙는 유일한 자리다.
SOURCE_UNITS = {
    "init-20260904-attach-payload-manual-rreq": "M1",
    "feat-20260904-m2-router-foreign-repo-ct5h": "M2",
    "feat-20260906-m3-close-foreign-repo-ik3u": "M3",
}

MISSING_UNIT = "feat-99999999-nonexistent-unit-zzzz"
MISSING_QID = "Q-99999"

Q_ROW = re.compile(r"^\|\s*(Q-\d+)\s*\|(.*)$")

# 위반 문구의 앞머리. 가상 검사는 이 표지로 「어느 검사가 잡았는가」를 지목한다 —
# 지목하지 않으면 엉뚱한 이유로 실패한 것을 판별로 착각한다.
V_MISSING = "목록에서 빠졌다"
V_UNKNOWN_Q_LISTED = "목록에만 있다"
V_REPEATED = "두 번 이상 나타난다"
V_QID_NOT_IN_OQ = "open-questions.md 에 없다"
V_UNIT_NOT_REGISTERED = "등록된 출처 단위가 아니다"
V_UNIT_DIR_ABSENT = "단위 폴더가 없다"
V_MILESTONE_MISMATCH = "마일스톤 표기가 그 단위와 어긋난다"
V_EMPTY_CELL = "칸이 비었다"
V_NO_REASON = "제외 사유가 없다"


def parse_requirements(text):
    """올린 것·뺀 것 두 표를 절 제목으로 갈라 읽는다. 중복 행을 살려 (Q, 셀) 목록으로 돌려준다."""
    included, excluded = [], []
    bucket = None
    for line in text.splitlines():
        if line.startswith("## 올린 것"):
            bucket = included
            continue
        if line.startswith("## 뺀 것"):
            bucket = excluded
            continue
        if line.startswith("## "):
            bucket = None
            continue
        if bucket is None:
            continue
        m = Q_ROW.match(line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        while cells and cells[-1] == "":
            cells.pop()
        bucket.append((m.group(1), cells))
    return included, excluded


def source_questions(text):
    """open-questions.md 에서 세 관통 중 하나를 출처로 가진 Q 집합."""
    found = set()
    for line in text.splitlines():
        m = Q_ROW.match(line)
        if m and any(unit in line for unit in SOURCE_UNITS):
            found.add(m.group(1))
    return found


def all_question_ids(text):
    return {m.group(1) for m in (Q_ROW.match(l) for l in text.splitlines()) if m}


def row_of(text, qid):
    """목록 문서에서 그 Q 의 표 행 한 줄을 집는다."""
    for line in text.splitlines():
        m = Q_ROW.match(line)
        if m and m.group(1) == qid:
            return line
    raise AssertionError(f"{qid} 의 표 행을 찾지 못했다")


def cells_of(rows, qid):
    for listed, cells in rows:
        if listed == qid:
            return cells
    raise AssertionError(f"{qid} 행이 목록에 없다")


# ── 판정 ────────────────────────────────────────────────────────────────
# 실검사와 가상 검사가 이 세 함수를 함께 부른다. 여기서 조건을 지우면 양쪽이 같이 바뀐다.


def coverage_violations(included, excluded, expected):
    """AC-1 — M1~M3 출처 Q 집합이 두 표 어느 한쪽에 정확히 한 번 나타나는가."""
    violations = []
    seen = collections.Counter(qid for qid, _ in included + excluded)
    for qid in sorted(expected - set(seen)):
        violations.append(f"{qid}: {V_MISSING}")
    for qid in sorted(set(seen) - expected):
        violations.append(f"{qid}: {V_UNKNOWN_Q_LISTED}")
    for qid, count in sorted(seen.items()):
        if count > 1:
            violations.append(f"{qid}: {V_REPEATED} ({count}회)")
    return violations


def included_violations(included, oq_text):
    """AC-2 — 「올린 것」의 각 행이 실재하는 Q·단위를 가리키고 마일스톤이 맞는가."""
    known_q = all_question_ids(oq_text)
    violations = []
    for qid, cells in included:
        if qid not in known_q:
            violations.append(f"{qid}: {V_QID_NOT_IN_OQ}")
        if len(cells) < 4:
            violations.append(f"{qid}: 열이 모자라다 ({len(cells)}칸)")
            continue
        requirement, condition, unit, milestone = cells[0], cells[1], cells[2], cells[3]
        if not requirement:
            violations.append(f"{qid}: 요구사항 {V_EMPTY_CELL}")
        if not condition:
            violations.append(f"{qid}: 충족 조건 {V_EMPTY_CELL}")
        # 아래 둘은 서로를 대신하지 않는다 — 등록 여부와 실재 여부는 다른 사실이고,
        # 한쪽을 지우면 그 가상 상태를 지목하는 검사가 깨진다.
        if unit not in SOURCE_UNITS:
            violations.append(f"{qid}: {V_UNIT_NOT_REGISTERED} ({unit})")
        elif SOURCE_UNITS[unit] != milestone:
            violations.append(f"{qid}: {V_MILESTONE_MISMATCH} ({unit} ≠ {milestone})")
        if not (WORK / unit).is_dir():
            violations.append(f"{qid}: {V_UNIT_DIR_ABSENT} ({unit})")
    return violations


def excluded_violations(excluded):
    """AC-3 — 「뺀 것」의 각 행에 제외 사유가 있는가."""
    return [
        f"{qid}: {V_NO_REASON}" for qid, cells in excluded if not (cells and cells[0])
    ]


class TestAttachRequirementsProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.req_text = REQUIREMENTS.read_text(encoding="utf-8")
        cls.oq_text = OPEN_QUESTIONS.read_text(encoding="utf-8")
        cls.included, cls.excluded = parse_requirements(cls.req_text)
        cls.expected = source_questions(cls.oq_text)

    def _tampered(self, text):
        """가상 상태 문서를 실검사와 같은 파이프라인에 태운다."""
        included, excluded = parse_requirements(text)
        return (
            coverage_violations(included, excluded, self.expected),
            included_violations(included, self.oq_text),
        )

    # ── 대조: 요구가 사는 자리와 보는 자리 ────────────────────────────────

    def test_source_questions_are_covered_exactly_once(self):
        self.assertTrue(self.expected, "출처 Q 집합이 비었다 — 대조가 성립하지 않는다")
        self.assertTrue(self.included, "「올린 것」 표가 비었다")
        self.assertEqual(
            [],
            coverage_violations(self.included, self.excluded, self.expected),
            "open-questions.md 에서 M1~M3 을 출처로 가진 Q 집합과 목록이 어긋난다",
        )

    def test_included_rows_point_at_existing_sources(self):
        self.assertTrue(self.included, "「올린 것」 표가 비었다")
        self.assertEqual([], included_violations(self.included, self.oq_text))

    def test_excluded_rows_carry_a_reason(self):
        self.assertTrue(self.excluded, "「뺀 것」 표가 비었다")
        self.assertEqual([], excluded_violations(self.excluded))

    # ── 판별력: 이 검사가 무엇을 잡는지 매번 재확인한다 (AGENTS §11) ──────────

    def test_detects_dropped_question(self):
        """M1~M3 출처 Q 하나를 두 표에서 모두 빼면 대조가 실패한다."""
        victim = sorted(qid for qid, _ in self.included)[0]
        broken = self.req_text.replace(row_of(self.req_text, victim) + "\n", "")
        included, _ = parse_requirements(broken)
        self.assertNotIn(victim, [qid for qid, _ in included], "치환이 표 행에 걸리지 않았다")
        coverage, _ = self._tampered(broken)
        self.assertIn(
            f"{victim}: {V_MISSING}", coverage, f"{victim} 을 빼도 대조가 통과했다"
        )

    def test_detects_unknown_question_id(self):
        """실재하지 않는 Q id 를 표에 넣으면 대조와 출처 검사가 함께 잡는다."""
        victim = sorted(qid for qid, _ in self.included)[0]
        row = row_of(self.req_text, victim)
        broken = self.req_text.replace(row, row.replace(victim, MISSING_QID, 1))
        included, _ = parse_requirements(broken)
        self.assertIn(MISSING_QID, [qid for qid, _ in included], "치환이 표 행에 걸리지 않았다")
        self.assertNotIn(MISSING_QID, all_question_ids(self.oq_text))
        coverage, provenance = self._tampered(broken)
        self.assertIn(
            f"{MISSING_QID}: {V_UNKNOWN_Q_LISTED}",
            coverage,
            "없는 Q id 를 넣어도 대조가 통과했다",
        )
        self.assertIn(
            f"{MISSING_QID}: {V_QID_NOT_IN_OQ}",
            provenance,
            "없는 Q id 를 넣어도 출처 검사가 통과했다",
        )

    def test_detects_unknown_source_unit(self):
        """실재하지 않는 단위 id 를 출처로 주면 출처 검사가 두 가지로 잡는다."""
        victim = sorted(qid for qid, _ in self.included)[0]
        row = row_of(self.req_text, victim)
        real_unit = cells_of(self.included, victim)[2]
        self.assertIn(real_unit, SOURCE_UNITS)
        broken = self.req_text.replace(row, row.replace(real_unit, MISSING_UNIT))
        included, _ = parse_requirements(broken)
        self.assertEqual(
            MISSING_UNIT, cells_of(included, victim)[2], "치환이 표 행의 출처 열에 걸리지 않았다"
        )
        self.assertFalse((WORK / MISSING_UNIT).is_dir())
        _, provenance = self._tampered(broken)
        # 등록 검사와 실재 검사 둘 다 잡아야 한다 — 어느 하나를 지우면 이 줄이 깨진다.
        self.assertIn(
            f"{victim}: {V_UNIT_NOT_REGISTERED} ({MISSING_UNIT})",
            provenance,
            "없는 단위를 출처로 줘도 등록 검사가 통과했다",
        )
        self.assertIn(
            f"{victim}: {V_UNIT_DIR_ABSENT} ({MISSING_UNIT})",
            provenance,
            "없는 단위를 출처로 줘도 실재 검사가 통과했다",
        )

    def test_detects_repeated_question_row(self):
        """같은 Q 가 두 번 나타나면 「정확히 한 번」(AC-1)이 깨진 것으로 잡는다."""
        victim = sorted(qid for qid, _ in self.excluded)[0]
        row = row_of(self.req_text, victim)
        broken = self.req_text.replace(row + "\n", row + "\n" + row + "\n", 1)
        _, excluded = parse_requirements(broken)
        self.assertEqual(
            2, [qid for qid, _ in excluded].count(victim), "행 복제가 표에 걸리지 않았다"
        )
        coverage, _ = self._tampered(broken)
        self.assertIn(
            f"{victim}: {V_REPEATED} (2회)", coverage, f"{victim} 을 두 번 적어도 대조가 통과했다"
        )


if __name__ == "__main__":
    unittest.main()
