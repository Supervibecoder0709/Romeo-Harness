"""재사용 검색 — 이미 있는 작업 단위를 핵심어로 찾는다.

`/plan` 절차 1단계가 요구하는 「재사용 검색」을 수행하는 자리다. 요구는 절차에 있었지만
그것을 수행하는 명령이 없었고, 수행했는지 보는 자리도 없었다(AGENTS.core §11).

**막지 않고 보이게 한다.** 겹치는 단위를 인쇄할 뿐이고, 재개할지·재분류할지·새로 열지는
사람이 정한다(K-61). 그래서 판정을 내리지 않는다 — 점수만 매겨 위에서부터 보여준다.

색인은 **단위 폴더 이름과 문서 제목** 둘이다. 폴더 이름에는 slug 가 들어 있고(`feat-<날짜>-<slug>-<접미>`),
제목은 사람이 읽는 이름이다. 본문은 색인하지 않는다 — 본문까지 넣으면 거의 모든 단위가 서로 겹쳐
「후보」 라는 말이 아무것도 좁히지 못한다.

형태소 분석기를 쓰지 않으므로 한국어 조사가 붙은 낱말(`재사용` vs `재사용을`)은 서로 다른 토큰이다.
그 회수율 손실을 아는 채로 둔다 — 어림짐작으로 잘라 내면 거짓 양성이 늘고, 거짓 양성이 늘면
사람이 이 줄을 읽지 않게 된다.
"""
import re
from pathlib import Path

from .frontmatter import read as _read_frontmatter

#: 이 저장소의 단위 이름·제목에 너무 흔해서 아무것도 좁히지 못하는 낱말.
#: id 접두사(feat·chg·init)와 문서 종류 이름, 그리고 저장소 전체의 주제어가 여기 든다.
STOPWORDS = frozenset({
    "feat", "chg", "init", "spec", "brief", "charter",
    "docs", "work", "current", "romeo", "harness",
    "the", "and", "for", "with",
})

#: 이보다 짧은 토큰은 버린다. 한국어 조사·어미와 영어 불용어가 대부분 여기 걸린다.
MIN_TOKEN = 3

#: 기본으로 인쇄할 후보 수. 더 필요하면 `--limit` 로 늘린다.
DEFAULT_LIMIT = 5

_SPLIT = re.compile(r"[^0-9A-Za-z가-힣]+")
#: 단위 문서. 앞에 있는 것을 먼저 본다 — id·title 의 정본은 spec 이다.
UNIT_DOCS = ("spec.md", "brief.md", "charter.md")
#: 검색 대상 디렉터리. `docs/current/` 는 M4 의 다음 마일스톤에서 생긴다 — 없으면 건너뛴다.
SEARCH_DIRS = ("docs/work", "docs/current")


def tokens(text):
    """검색·색인 공통 토큰화. 날짜 같은 순수 숫자와 불용어·짧은 토큰을 버린다."""
    out = set()
    for raw in _SPLIT.split((text or "").lower()):
        if not raw or raw.isdigit() or len(raw) < MIN_TOKEN or raw in STOPWORDS:
            continue
        out.add(raw)
    return out


def _unit_identity(unit_dir):
    """(id, title). frontmatter 가 있으면 그것이 정본이고, 없으면 폴더 이름이 id 다."""
    for name in UNIT_DOCS:
        doc = unit_dir / name
        if not doc.is_file():
            continue
        try:
            fm, _ = _read_frontmatter(doc)
        except Exception:
            # 문서 하나가 깨졌다고 검색 전체가 멈추지 않는다 — 그 단위는 폴더 이름으로만 색인한다.
            continue
        fm = fm or {}
        return str(fm.get("id") or unit_dir.name), str(fm.get("title") or "")
    return unit_dir.name, ""


def search_units(project_root=".", terms=(), limit=DEFAULT_LIMIT):
    """핵심어와 겹치는 기존 작업 단위를 점수순으로 돌려준다.

    반환은 `id`·`title`·`path`·`score`·`matched` 를 담은 dict 목록이다. 겹치는 것이 없으면
    빈 목록이다 — 없음은 오류가 아니다(AC-1).
    """
    root = Path(project_root)
    want = set()
    for term in terms:
        want |= tokens(term)
    hits = []
    if want:
        for base in SEARCH_DIRS:
            d = root / base
            if not d.is_dir():
                continue
            for unit_dir in sorted(p for p in d.iterdir() if p.is_dir()):
                uid, title = _unit_identity(unit_dir)
                matched = want & (tokens(unit_dir.name) | tokens(title))
                if not matched:
                    continue
                hits.append({"id": uid, "title": title,
                             "path": unit_dir.relative_to(root).as_posix(),
                             "score": len(matched), "matched": sorted(matched)})
    hits.sort(key=lambda h: (-h["score"], h["id"]))
    return hits[:limit] if limit else hits


def proposal_terms(proposal):
    """제안에서 검색어를 뽑는다 — slug·제목·요청 원문.

    카드가 제안의 `reuse_hits` 와 **무관하게** 자기 검색을 돌릴 때 쓰는 입력이다(AC-2)."""
    cand = proposal.get("candidate") or {}
    request = proposal.get("request") or {}
    return [cand.get("slug") or "", cand.get("title") or "", request.get("text") or ""]
