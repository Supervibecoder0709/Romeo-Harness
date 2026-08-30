#!/usr/bin/env python3
"""archive/*/_source.md 의 `- License:` 값을 계획 §1.3 표와 대조한다.

AC-1(feat-20260829-license-field-46an)을 기계로 대조하는 검사다. 라이선스 값을 여기 하드코딩하지
않고 `docs/planning/implementation-plan.md` §1.3 표의 「아카이브」 열과 「`_source.md` 에 적는 값」
열을 읽는다 — 근거는 그 표 한 곳이고, 이 스크립트는 그것을 옮겨 적지 않는다.

판정 (아무것도 쓰지 않으며, 같은 입력이면 같은 결론이다):
  exit 0  archive/ 의 모든 아카이브가 표에 있고 값이 글자까지 같다
  exit 1  하나라도 다르거나(줄이 없는 것 포함), 표에 없는 아카이브가 있거나,
          표의 행이 가리키는 아카이브가 없거나 여럿에 맞는다 — 어긋난 항목을 전부 인쇄한다

표의 「아카이브」 열은 긴 이름을 `…` 로 줄여 적을 수 있다(예: `bmad-…-creative-intelligence-suite`).
`…` 는 임의 문자열로 읽되, 정확히 하나의 아카이브에만 맞아야 한다.

usage:
  check-archive-licenses.py                       # 저장소의 archive/ 와 계획 문서를 본다
  check-archive-licenses.py --archive-dir <dir>   # 사본을 검사할 때 (검증 계획의 부정 사례용)
  check-archive-licenses.py --plan <file>         # 다른 계획 문서를 볼 때
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ARCHIVE_DIR = REPO_ROOT / "archive"
PLAN_PATH = REPO_ROOT / "docs" / "planning" / "implementation-plan.md"

SECTION_HEADING = re.compile(r"^###\s+1\.3\b")
ANY_HEADING = re.compile(r"^#{1,6}\s")
NAME_COLUMN = "아카이브"
VALUE_COLUMN = "`_source.md` 에 적는 값"
# generate-archive-index.py 의 field() 와 같은 형태 — 두 스크립트가 같은 줄을 읽는다.
LICENSE_FIELD = re.compile(r"^[-*]\s*License\s*:\s*(.+)$", re.M)
ELLIPSIS = "…"


def split_row(line: str) -> list[str]:
    """`| a | b |` → ['a', 'b']. 셀 안의 `\\|` 는 파이프 문자로 되돌린다."""
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", inner)]


def strip_code(text: str) -> str:
    """셀 값이 `...` 로 감싸여 있으면 벗기고, 안쪽 공백은 하나로 다듬는다."""
    text = text.strip()
    if len(text) >= 2 and text[0] == "`" and text[-1] == "`":
        text = text[1:-1]
    return re.sub(r"\s+", " ", text).strip()


def section_1_3(plan_text: str) -> list[str]:
    """`### 1.3` 제목부터 다음 제목 전까지의 줄."""
    out: list[str] = []
    inside = False
    for line in plan_text.splitlines():
        if SECTION_HEADING.match(line):
            inside = True
            continue
        if inside and ANY_HEADING.match(line):
            break
        if inside:
            out.append(line)
    return out


def load_table(plan_path: pathlib.Path) -> dict[str, str]:
    """§1.3 표에서 {아카이브 이름(표기 그대로): `_source.md` 에 적는 값} 을 읽는다."""
    body = section_1_3(plan_path.read_text(encoding="utf-8"))
    rows = [split_row(line) for line in body if line.lstrip().startswith("|")]
    if len(rows) < 2:
        raise SystemExit(f"FAIL: {plan_path} §1.3 에서 표를 찾지 못했다")
    header = rows[0]
    try:
        name_idx = next(i for i, h in enumerate(header) if h.startswith(NAME_COLUMN))
        value_idx = next(i for i, h in enumerate(header) if h.startswith(VALUE_COLUMN))
    except StopIteration:
        raise SystemExit(
            f"FAIL: §1.3 표 헤더에 「{NAME_COLUMN}」 또는 「{VALUE_COLUMN}」 열이 없다: {header}"
        )
    table: dict[str, str] = {}
    for row in rows[1:]:
        if all(re.fullmatch(r":?-{3,}:?", c) for c in row):  # 구분선
            continue
        if len(row) <= max(name_idx, value_idx):
            continue
        name = strip_code(row[name_idx])
        if name:
            table[name] = strip_code(row[value_idx])
    return table


def resolve(label: str, names: list[str]) -> list[str]:
    """표의 이름을 실제 디렉터리 이름에 맞춘다. `…` 는 임의 문자열이다."""
    if ELLIPSIS not in label:
        return [n for n in names if n == label]
    rx = re.compile("^" + ".*".join(re.escape(p) for p in label.split(ELLIPSIS)) + "$")
    return [n for n in names if rx.match(n)]


def license_of(source: pathlib.Path) -> str | None:
    """`_source.md` 헤더의 License 값. 줄이 없거나 파일을 못 읽으면 None."""
    try:
        text = source.read_text(encoding="utf-8")
    except OSError:
        return None
    m = LICENSE_FIELD.search(text)
    return strip_code(m.group(1)) if m else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="archive/*/_source.md 의 License 값을 계획 §1.3 표와 대조한다."
    )
    parser.add_argument(
        "--archive-dir", type=pathlib.Path, default=ARCHIVE_DIR,
        help="검사할 archive 디렉터리 (기본: 저장소의 archive/)",
    )
    parser.add_argument(
        "--plan", type=pathlib.Path, default=PLAN_PATH,
        help="§1.3 표가 있는 계획 문서 (기본: docs/planning/implementation-plan.md)",
    )
    args = parser.parse_args()

    if not args.archive_dir.is_dir():
        print(f"FAIL: archive 디렉터리가 없습니다: {args.archive_dir}", file=sys.stderr)
        return 1
    if not args.plan.is_file():
        print(f"FAIL: 계획 문서가 없습니다: {args.plan}", file=sys.stderr)
        return 1

    table = load_table(args.plan)
    archives = sorted(
        (p for p in args.archive_dir.iterdir() if p.is_dir() and not p.name.startswith(".")),
        key=lambda p: p.name.lower(),
    )
    names = [p.name for p in archives]

    expected: dict[str, str] = {}  # 디렉터리 이름 → 표의 값
    problems: list[str] = []
    for label, value in table.items():
        hits = resolve(label, names)
        if len(hits) == 1:
            expected[hits[0]] = value
        elif not hits:
            problems.append(f"표에는 있으나 archive/ 에 없음: {label}")
        else:
            problems.append(f"표의 이름이 여러 아카이브에 맞음: {label} → {', '.join(hits)}")

    for archive in archives:
        actual = license_of(archive / "_source.md")
        if archive.name not in expected:
            shown = actual if actual is not None else "(없음)"
            problems.append(f"표에 없는 아카이브: {archive.name} (헤더 값: {shown})")
        elif actual is None:
            problems.append(f"License 줄 없음: {archive.name} (표: {expected[archive.name]})")
        elif actual != expected[archive.name]:
            problems.append(
                f"값 불일치: {archive.name} (헤더: {actual} / 표: {expected[archive.name]})"
            )

    if problems:
        print(f"FAIL: 아카이브 라이선스가 계획 §1.3 표와 어긋난다 ({len(problems)}건)", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"PASS: 아카이브 {len(archives)}개의 라이선스가 계획 §1.3 표와 일치한다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
