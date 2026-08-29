"""문서 검증: frontmatter 스키마·필수 섹션·길이 예산·open loop·미체크 AC·링크. 결정적 차단(error)과 휴리스틱 경고(warning)를 분리한다(C-E3)."""
import re
from pathlib import Path

from . import HARNESS_ROOT, frontmatter
from .policy import RouteError, classification_from_frontmatter, load_policy, route
from .schema import validate as _validate
from .util import load_json

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
UNCHECKED_RE = re.compile(r"^\s*- \[ \]", re.M)
CHECKED_RE = re.compile(r"^\s*- \[[xX]\]", re.M)


def find_docs(project_root):
    base = Path(project_root) / "docs" / "work"
    if not base.is_dir():
        return []
    return sorted(p for p in base.glob("*/*.md") if p.name in ("spec.md", "brief.md", "charter.md"))


def section_lines(body, title):
    lines = body.split("\n")
    for i, ln in enumerate(lines):
        if ln.strip() == f"## {title}":
            j = i + 1
            while j < len(lines) and not lines[j].startswith("## "):
                j += 1
            return lines[i + 1:j]
    return None


def validate_doc(path, harness_root=None):
    harness_root = Path(harness_root or HARNESS_ROOT)
    pol = load_policy(harness_root)
    pk = pol["packages"]
    path = Path(path)
    errors, warnings, info = [], [], {}
    text = path.read_text(encoding="utf-8")
    fm, body = frontmatter.split(text)
    if fm is None:
        return {"path": str(path), "errors": ["frontmatter 가 없다"], "warnings": [], "info": {}}
    schema = load_json(harness_root / "core/schemas/frontmatter.json")
    errors += [f"FRONTMATTER_INVALID {e}" for e in _validate(fm, schema)]
    if errors:
        return {"path": str(path), "errors": errors, "warnings": warnings, "info": info}
    doc = fm["type"]
    # 라우팅 재계산 → 필수 섹션·profile 일관성
    try:
        out = route(classification_from_frontmatter(fm), pol)
        if out["profile"] != fm["profile"]:
            if fm["routing"]["policy_version"] != pol["version"]:
                warnings.append(f"POLICY_VERSION_CHANGED 문서 {fm['routing']['policy_version']} vs 현재 {pol['version']} — profile 재계산 결과 {out['profile']}")
            else:
                errors.append(f"PROFILE_MISMATCH frontmatter {fm['profile']} vs 정책표 {out['profile']}")
        for sid in out["sections"].get(doc, []):
            title = pk["sections"][sid]["title"]
            if section_lines(body, title) is None:
                errors.append(f"MISSING_SECTION '## {title}' ({sid})")
    except RouteError as e:
        errors.append(f"ROUTE_ERROR {'; '.join(e.args[0])}")
    # 길이 예산
    total = len(text.split("\n"))
    cap = pk["documents"][doc]["max_lines"]
    info["lines"] = total
    if total > cap:
        warnings.append(f"BUDGET_EXCEEDED {total} > {cap}")
    cap_lines = section_lines(body, "Planning Capsule")
    if cap_lines is not None:
        n = len([ln for ln in cap_lines if ln.strip()])
        info["capsule_lines"] = n
        if n > pk["budgets"]["capsule_max_lines"]:
            warnings.append(f"CAPSULE_TOO_LONG {n} > {pk['budgets']['capsule_max_lines']}")
    # open loop · AC
    info["needs_input"] = body.count("NEEDS_INPUT")
    info["unchecked_ac"] = len(UNCHECKED_RE.findall(body))
    info["checked_ac"] = len(CHECKED_RE.findall(body))
    if info["needs_input"]:
        warnings.append(f"OPEN_LOOP NEEDS_INPUT {info['needs_input']}곳")
    if info["unchecked_ac"]:
        warnings.append(f"UNCHECKED_AC {info['unchecked_ac']}개")
    # base_sha 는 더 이상 승인이 기록하지 않는다(체크리스트 38) — 남아 있는 값은 승인 커밋의 부모를 가리키는 낡은 사실이다.
    if fm.get("base_sha") and fm.get("status") not in ("done", "dropped", "superseded"):
        warnings.append(f"STALE_BASE_SHA frontmatter 의 base_sha {str(fm['base_sha'])[:12]} 는 승인 커밋이 아니다 — "
                        f"계약 생성은 이력에서 승인 커밋을 찾는다. 재승인하면 지워진다")
    # 링크
    for target in LINK_RE.findall(body):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        t = target.split("#")[0]
        if t and not (path.parent / t).exists():
            errors.append(f"BROKEN_LINK {target}")
    return {"path": str(path), "errors": errors, "warnings": warnings, "info": info}
