"""ID 규약 `type-YYYYMMDD-slug-entropy` (D-08, K-22). slug 규칙은 sindresorhus/slugify 원칙을 표준 라이브러리로 재작성
(provenance: sindresorhus-slugify rewrite). 순차 번호는 쓰지 않는다 — 병렬 worktree 에서 충돌한다."""
import datetime as _dt
import re
import secrets
import unicodedata

UNIT_PREFIX = {"T0": "chg", "T1": "feat", "T2": "init"}
PREFIX_UNIT = {v: k for k, v in UNIT_PREFIX.items()}
ID_RE = re.compile(r"^(chg|feat|init)-(\d{8})-([a-z0-9]+(?:-[a-z0-9]+)*)-([a-z0-9]{4})$")
_ALPHABET = "abcdefghijkmnpqrstuvwxyz23456789"  # 혼동 문자(l,o,0,1) 제외


def slugify(text, max_len=40):
    """ASCII 소문자·숫자·하이픈만 남긴다. 한글 등 비ASCII는 NFKD 분해 후 버린다(영문 slug 를 제안 단계에서 받는다)."""
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    if len(text) > max_len:
        text = text[:max_len].rstrip("-")
    return text or "unit"


def entropy(n=4):
    return "".join(secrets.choice(_ALPHABET) for _ in range(n))


def new_id(unit, slug, date=None):
    if unit not in UNIT_PREFIX:
        raise ValueError(f"unit {unit!r} 에는 문서 ID 가 없다 (none 은 문서를 만들지 않는다)")
    date = date or _dt.date.today().strftime("%Y%m%d")
    return f"{UNIT_PREFIX[unit]}-{date}-{slugify(slug)}-{entropy()}"


def parse_id(unit_id):
    m = ID_RE.match(unit_id)
    if not m:
        raise ValueError(f"ID 형식이 아님: {unit_id}")
    prefix, date, slug, ent = m.groups()
    return {"prefix": prefix, "unit": PREFIX_UNIT[prefix], "date": date, "slug": slug, "entropy": ent}
