#!/usr/bin/env python3
"""archive/ 하위 아카이브를 스캔해 archive/README.md 인덱스를 생성한다.

산출물은 결정적이다. 입력(archive/**)이 같으면 항상 같은 바이트를 낸다.
생성 시각처럼 매 실행마다 달라지는 값은 넣지 않는다. CI가 stale 여부를
`git diff --exit-code` 로 판정하기 때문이다.

usage:
  generate-archive-index.py            # archive/README.md 를 쓴다
  generate-archive-index.py --check    # 쓰지 않고, 최신이 아니면 exit 1
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ARCHIVE_DIR = REPO_ROOT / "archive"
INDEX_PATH = ARCHIVE_DIR / "README.md"

# repo 스킬이 만드는 아카이브 스키마. validate-repo-archive.sh 와 같은 목록이다.
REQUIRED_FILES = (
    "_source.md",
    "00-exploration.md",
    "02-workflow-summary.md",
    "04-components-table.md",
    "05-pm-harness-notes.md",
    "06-source-evidence.md",
)
REQUIRED_DIRS = ("01-docs", "03-components")

SCHEMA_ROWS = (
    ("`_source.md`", "고정 커밋 SHA와 수집 범위·한계"),
    ("`00-exploration.md`", "탐색 기록과 결론"),
    ("`01-docs/`", "원문 문서의 한국어 번역 (`*.ko.md`)"),
    ("`02-workflow-summary.md`", "레포가 무엇을 어떻게 하는지 요약"),
    ("`03-components/`", "구성요소별 상세"),
    ("`04-components-table.md`", "구성요소 표 (원문 위치·근거 상태 포함)"),
    ("`05-pm-harness-notes.md`", "기획 하네스 관점 메모"),
    ("`06-source-evidence.md`", "고정 SHA 기준 근거 링크"),
)


def read(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def field(source_text: str, key: str) -> str:
    """`- Key: value` 형태의 헤더 필드에서 value 를 뽑는다."""
    m = re.search(rf"^[-*]\s*{re.escape(key)}\s*:\s*(.+)$", source_text, re.M)
    return m.group(1).strip() if m else ""


def strip_markdown(text: str) -> str:
    text = re.sub(r"\[([SE]\d+)\](\s*[-–—]\s*\[([SE]\d+)\])?", "", text)  # [S5], [S5]-[S18]
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)                  # 링크 → 텍스트
    text = text.replace("`", "").replace("**", "").replace("*", "")
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, limit: int = 130) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    for sep in ("다. ", ". "):
        idx = cut.rfind(sep)
        if idx > limit * 0.5:
            return cut[: idx + 1].strip()
    return cut.rsplit(" ", 1)[0].rstrip(" ,·") + "…"


# 문단 앞에 붙는 라벨. "확인된 사실:", "무엇을 하는가:", "판단." 등을 떼어낸다.
LABEL_RE = re.compile(r"^(확인된 사실|판단|결론|요약|무엇을 하는가|무엇인가|개요)\s*[:.]\s*")

# 아카이브마다 반복되는 상투 문단. 요약으로 쓰면 레포를 설명하지 못한다.
BOILERPLATE_RE = re.compile(r"^(이 문서는|이 아카이브는|근거 ID|각 근거)")


def first_paragraph(block: str) -> str:
    """문단 블록에서 요약으로 쓸 만한 첫 산문 문단을 고른다."""
    for para in block.split("\n\n"):
        para = para.strip()
        # 헤딩·표·인용·리스트 항목은 건너뛴다. '**굵게**'로 시작하는 산문은 리스트가 아니다.
        if not para or para[0] in "#|>" or re.match(r"^[-*+]\s", para):
            continue
        cleaned = LABEL_RE.sub("", strip_markdown(para))
        if len(cleaned) >= 30 and not BOILERPLATE_RE.match(cleaned):
            return truncate(cleaned)
    return ""


def section(text: str, pattern: str) -> str:
    """`## 3. 무엇을 하는가` 처럼 번호가 붙어도 잡히도록 절 본문을 잘라낸다."""
    m = re.search(
        rf"^#{{2,4}}\s*(?:\d+[.)]\s*)?(?:{pattern})[^\n]*\n(.*?)(?=^#{{1,4}}\s|\Z)",
        text,
        re.M | re.S,
    )
    return m.group(1) if m else ""


def summary(archive: pathlib.Path) -> str:
    """레포가 '무엇인지'를 한 줄로. 분석 방법이 아니라 대상 설명을 우선한다."""
    workflow = read(archive / "02-workflow-summary.md")
    exploration = read(archive / "00-exploration.md")

    # 앞쪽일수록 '무엇을 하는가'에 가깝고, 뒤로 갈수록 최후 수단이다.
    for block in (
        section(workflow, "무엇을 하는가|무엇인가|개요"),
        workflow,          # `**무엇을 하는가**:` 처럼 인라인 라벨을 쓴 아카이브
        section(exploration, "결론"),
        exploration,
    ):
        found = first_paragraph(block)
        if found:
            return found
    return "—"


def parse_date(raw: str) -> str:
    """편차가 큰 Analysis timestamp 표기를 KST 날짜(YYYY-MM-DD)로 정규화한다."""
    raw = raw.replace("`", "").strip()
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})\s*(Z|[+-]\d{2}:?\d{2})?", raw)
    if not m:
        m2 = re.search(r"(\d{4}-\d{2}-\d{2})", raw)
        return m2.group(1) if m2 else "—"
    y, mo, d, hh, mm, ss, tz = m.groups()
    stamp = dt.datetime(int(y), int(mo), int(d), int(hh), int(mm), int(ss))
    if tz in (None, "Z"):
        offset = dt.timedelta(0)
    else:
        tz = tz.replace(":", "")
        sign = 1 if tz[0] == "+" else -1
        offset = sign * dt.timedelta(hours=int(tz[1:3]), minutes=int(tz[3:5]))
    return (stamp - offset + dt.timedelta(hours=9)).strftime("%Y-%m-%d")  # → KST


def collect(archive: pathlib.Path) -> dict:
    src = read(archive / "_source.md")
    url = field(src, "Origin URL").replace("`", "").strip().rstrip("/")
    url = re.sub(r"\.git$", "", url)
    slug = url.split("github.com/", 1)[1] if "github.com/" in url else archive.name

    ref = field(src, "Ref")
    ref = re.sub(r"\s*\(.*\)$", "", ref).replace("`", "").strip() or "—"

    sha_m = re.search(r"[0-9a-f]{40}", field(src, "Commit SHA"))
    sha = sha_m.group(0) if sha_m else ""

    # `- License:` 헤더 필드. 백틱을 벗기고 공백을 다듬는다. 없으면 em dash — 검증기가 따로 잡는다.
    license_ = re.sub(r"\s+", " ", field(src, "License").replace("`", "")).strip() or "—"

    missing = [f for f in REQUIRED_FILES if not (archive / f).is_file()]
    missing += [f"{d}/" for d in REQUIRED_DIRS if not (archive / d).is_dir()]

    return {
        "name": archive.name,
        "slug": slug,
        "url": url,
        "ref": ref,
        "sha": sha,
        "license": license_,
        "date": parse_date(field(src, "Analysis timestamp")),
        "summary": summary(archive),
        "docs": sum(1 for _ in archive.rglob("*.md")),
        "missing": missing,
    }


def cell(text: str) -> str:
    """표 셀 안에서 파이프가 열을 쪼개지 않도록 막는다."""
    return text.replace("|", "\\|")


def render(entries: list[dict]) -> str:
    total_docs = sum(e["docs"] for e in entries)
    out: list[str] = []
    add = out.append

    add("<!-- 이 파일은 scripts/generate-archive-index.py 가 생성합니다. 직접 수정하지 마세요. -->")
    add("<!-- archive/ 아래 항목을 추가·수정했다면 `python3 scripts/generate-archive-index.py` 를 실행해")
    add("     이 파일을 다시 만들고 함께 커밋하세요. CI(.github/workflows/archive-index.yml)가 최신인지")
    add("     검사하며, 오래되었으면 실패합니다. -->")
    add("")
    add("# 아카이브 인덱스")
    add("")
    add("`repo` 스킬로 GitHub 레포를 고정 커밋에 묶어 분석한 한국어 아카이브 모음입니다.")
    add("각 아카이브는 원본 레포를 수정하지 않고 읽기만 해서 작성했으며, 모든 서술은")
    add("`_source.md` 에 기록된 40자리 커밋 SHA를 근거로 합니다.")
    add("")
    add(f"현재 **아카이브 {len(entries)}개**, 문서 **{total_docs}개**.")
    add("")
    add("## 목록")
    add("")
    add("| 아카이브 | 원본 레포 | 고정 커밋 | 라이선스 | 분석일 | 요약 |")
    add("| --- | --- | --- | --- | --- | --- |")
    for e in entries:
        commit = (
            f"[`{e['sha'][:7]}`]({e['url']}/commit/{e['sha']})" if e["sha"] and e["url"] else "—"
        )
        repo = f"[{e['slug']}]({e['url']})" if e["url"] else e["name"]
        add(
            f"| [`{e['name']}`]({e['name']}/) | {repo} | {commit} <sup>{cell(e['ref'])}</sup> "
            f"| {cell(e['license'])} | {e['date']} | {cell(e['summary'])} |"
        )
    add("")

    broken = [e for e in entries if e["missing"]]
    if broken:
        add("## ⚠️ 스키마 미충족")
        add("")
        add("아래 아카이브는 필수 파일·디렉터리가 빠져 있습니다.")
        add("")
        for e in broken:
            add(f"- `{e['name']}` — 누락: {', '.join(f'`{m}`' for m in e['missing'])}")
        add("")

    add("## 아카이브 구조")
    add("")
    add("모든 아카이브가 같은 스키마를 따릅니다.")
    add("")
    add("| 경로 | 내용 |")
    add("| --- | --- |")
    for path, desc in SCHEMA_ROWS:
        add(f"| {path} | {desc} |")
    add("")
    add("`scripts/validate-repo-archive.sh <아카이브 경로>` 로 스키마를 검증할 수 있습니다.")
    add("")
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="archive/README.md 인덱스를 생성한다.")
    parser.add_argument("--check", action="store_true", help="쓰지 않고 최신 여부만 확인한다")
    args = parser.parse_args()

    if not ARCHIVE_DIR.is_dir():
        print(f"FAIL: archive 디렉터리가 없습니다: {ARCHIVE_DIR}", file=sys.stderr)
        return 1

    archives = sorted(
        (p for p in ARCHIVE_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")),
        key=lambda p: p.name.lower(),
    )
    content = render([collect(p) for p in archives])

    if args.check:
        if read(INDEX_PATH) == content:
            print(f"PASS: {INDEX_PATH.relative_to(REPO_ROOT)} 는 최신입니다 ({len(archives)}개).")
            return 0
        print(
            f"FAIL: {INDEX_PATH.relative_to(REPO_ROOT)} 가 오래되었습니다.\n"
            "      `python3 scripts/generate-archive-index.py` 를 실행하고 결과를 커밋하세요.",
            file=sys.stderr,
        )
        return 1

    changed = read(INDEX_PATH) != content
    INDEX_PATH.write_text(content, encoding="utf-8")
    state = "갱신함" if changed else "변경 없음"
    print(f"{state}: {INDEX_PATH.relative_to(REPO_ROOT)} (아카이브 {len(archives)}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
