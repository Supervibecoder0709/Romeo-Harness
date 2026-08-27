"""작업 단위 문서 생성·승인. docs/work/<unit-id>/ 경로는 불변이다(D-09)."""
from pathlib import Path

from . import HARNESS_ROOT, frontmatter
from .gitinfo import head_sha, is_repo
from .ids import new_id
from .policy import load_policy
from .util import now_iso, today

SPEC_EXTRA_ORDER = ["risk-backup-recovery", "environment-plan", "ui-state-table", "discovery-plan", "experiment-design", "capability-check"]


def work_dir(project_root):
    return Path(project_root) / "docs" / "work"


def find_unit_dir(project_root, unit_id):
    d = work_dir(project_root) / unit_id
    if not d.is_dir():
        raise FileNotFoundError(f"작업 단위 디렉터리가 없다: {d}")
    return d


def _template_body(harness_root, name):
    """템플릿의 frontmatter 는 자리표시자({{...}})라 YAML 로 읽지 않고 텍스트로 잘라 본문만 쓴다."""
    text = (Path(harness_root) / "core/templates" / name).read_text(encoding="utf-8")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5:]
    return text


def _section_template(harness_root, sid):
    p = Path(harness_root) / "core/templates/sections" / f"{sid}.md"
    if not p.exists():
        return f"## {sid}\n\nNEEDS_INPUT\n"
    return p.read_text(encoding="utf-8")


def _flow(items):
    return "[" + ", ".join(items) + "]"


def create_unit(route_out, title, slug, one_line=None, project_root=".", harness_root=None, date=None):
    """route 출력으로 문서 패키지를 만든다. 템플릿이 아직 없는 문서는 건너뛰고 skipped 에 적는다."""
    harness_root = Path(harness_root or HARNESS_ROOT)
    pol = load_policy(harness_root)
    pk = pol["packages"]
    unit = route_out["unit"]
    if not route_out["package"]:
        return {"id": None, "dir": None, "files": [], "skipped": [], "note": "문서를 만들지 않는 분류(unit none 또는 범위 밖)"}
    unit_id = new_id(unit, slug, date)
    udir = work_dir(project_root) / unit_id
    udir.mkdir(parents=True, exist_ok=False)
    c = route_out["classification"]
    files, skipped = [], []
    for doc in route_out["package"]:
        meta = pk["documents"][doc]
        tpl = harness_root / meta["template"]
        if not tpl.exists():
            skipped.append({"doc": doc, "reason": f"NOT_AVAILABLE_YET ({meta['available_from']})"})
            continue
        fm = {
            "id": unit_id, "type": doc, "title": title,
            "unit": unit, "mode": c["mode"], "intent": c["intent"],
            "facets": list(c["facets"]), "gates": list(route_out["gates"]),
            "profile": route_out["profile"], "blast_radius": c["blast_radius"], "uncertainty": c["uncertainty"],
            "status": "draft", "approved_at": None, "approved_by": None, "base_sha": None, "closed_at": None,
            "parent": None, "inputs": [], "evidence": [],
            "routing": {"policy_version": route_out["policy_version"], "fired_rules": list(route_out["fired_rules"]), "history": []},
            "created": date and f"{date[:4]}-{date[4:6]}-{date[6:]}" or today(), "updated": date and f"{date[:4]}-{date[4:6]}-{date[6:]}" or today(),
        }
        body = _template_body(harness_root, Path(meta["template"]).name)
        secs = route_out["sections"].get(doc, [])
        extra = "".join(_section_template(harness_root, s) + "\n" for s in SPEC_EXTRA_ORDER if s in secs)
        capsule = _section_template(harness_root, "capsule") + "\n" if "capsule" in secs else ""
        body = (body
                .replace("{{id}}", unit_id).replace("{{title}}", title)
                .replace("{{profile_label}}", route_out["profile_label"] or "-")
                .replace("{{unit}}", unit).replace("{{mode}}", c["mode"]).replace("{{intent}}", c["intent"])
                .replace("{{facets_text}}", ", ".join(c["facets"]) or "없음")
                .replace("{{gates_text}}", ", ".join(route_out["gates"]) or "없음")
                .replace("{{one_line}}", one_line or title)
                .replace("{{capsule_section}}", capsule)
                .replace("{{extra_sections}}", extra))
        path = udir / meta["file"]
        frontmatter.write(path, fm, body)
        files.append(str(path))
    return {"id": unit_id, "dir": str(udir), "files": files, "skipped": skipped}


def approve_unit(unit_id, by, project_root="."):
    """사람의 승인 사건을 기록한다: approved_at·approved_by·base_sha, status active. 확인란이 비어 있으면 거부."""
    udir = find_unit_dir(project_root, unit_id)
    spec = udir / "spec.md"
    fm, body = frontmatter.read(spec)
    if fm.get("status") != "draft":
        raise ValueError(f"status 가 draft 가 아니다: {fm.get('status')}")
    check = _section_text(body, "확인란")
    if check is None:
        raise ValueError("확인란 절이 없다")
    if "NEEDS_INPUT" in check:
        raise ValueError("확인란에 NEEDS_INPUT 이 남아 있다 — 사용자가 읽고 승인할 내용이 비어 있다")
    fm["approved_at"] = now_iso()
    fm["approved_by"] = by
    fm["base_sha"] = head_sha(project_root) if is_repo(project_root) else None
    fm["status"] = "active"
    fm["updated"] = today()
    frontmatter.write(spec, fm, body)
    return fm


def _section_text(body, title):
    lines = body.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == f"## {title}":
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end])
