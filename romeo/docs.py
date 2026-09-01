"""작업 단위 문서 생성·승인. docs/work/<unit-id>/ 경로는 불변이다(D-09)."""
import subprocess
from pathlib import Path

from . import HARNESS_ROOT, frontmatter
from .blocks import evaluate as evaluate_blocks
from .ids import new_id
from .policy import classification_from_frontmatter, load_policy, load_project_state, route
from .util import now_iso, rel, today

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


def _is_approved(fm):
    return fm.get("status") == "active" and bool(fm.get("approved_at"))


def approve_unit(unit_id, by, project_root=".", reapprove=False, reason=None):
    """사람의 승인 사건을 기록한다: approved_at·approved_by, status active. 확인란이 비어 있으면 거부.

    **base_sha 는 적지 않는다.** 승인 표시는 이 기록 *다음* 커밋에 들어가므로, 승인 시점의 HEAD 를 적으면
    그 커밋의 spec 에는 승인이 없다 — 언제나 승인 커밋의 부모를 가리켰다(체크리스트 38). 어떤 커밋도 자기 SHA 를
    자기 안에 담을 수 없으니 승인 커밋은 파일의 주장이 아니라 이력의 사실로 둔다(`approval_commit`).

    이미 승인된 spec 의 검증 계획·확인란이 바뀌면 다시 승인해야 한다(D-27). 그 경로는 `reapprove=True` 와 `reason` 이고,
    이전 승인은 `approval_history` 에 남는다 — status 를 손으로 draft 로 내리는 경로를 두지 않는다(체크리스트 37)."""
    udir = find_unit_dir(project_root, unit_id)
    spec = udir / "spec.md"
    fm, body = frontmatter.read(spec)
    status = fm.get("status")
    if status == "draft":
        if reapprove:
            raise ValueError("아직 승인되지 않은 spec 이다 — --reapprove 없이 승인한다")
    elif _is_approved(fm):
        if not reapprove:
            raise ValueError(f"이미 승인된 spec 이다 (approved_at={fm.get('approved_at')} by {fm.get('approved_by')}). "
                             f"검증 계획·확인란이 바뀌어 다시 승인하려면 --reapprove --reason <무엇이 바뀌었나> 를 준다 — "
                             f"status 를 손으로 내리지 않는다(체크리스트 37)")
        if not (reason and str(reason).strip()):
            raise ValueError("--reapprove 에는 --reason 이 필요하다 — 무엇이 바뀌어 다시 승인하는지 기록한다(D-27)")
    else:
        raise ValueError(f"status 가 draft 가 아니다: {status}")
    check = _section_text(body, "확인란")
    if check is None:
        raise ValueError("확인란 절이 없다")
    if "NEEDS_INPUT" in check:
        raise ValueError("확인란에 NEEDS_INPUT 이 남아 있다 — 사용자가 읽고 승인할 내용이 비어 있다")
    unmet = unmet_blocks(unit_id, fm, body, udir, project_root=project_root)
    if unmet:
        raise ValueError("차단이 충족되지 않아 승인할 수 없다(승인은 구현을 여는 사건이다, D-27) — "
                         + "; ".join(f"{bid}: {why}" for bid, why in unmet))
    now = now_iso()
    if reapprove:
        history = list(fm.get("approval_history") or [])
        history.append({"approved_at": str(fm.get("approved_at")), "approved_by": fm.get("approved_by"),
                        "superseded_at": now, "reason": str(reason).strip()})
        fm["approval_history"] = history
    fm["approved_at"] = now
    fm["approved_by"] = by
    fm["base_sha"] = None
    fm["status"] = "active"
    fm["updated"] = today()
    frontmatter.write(spec, fm, body)
    return fm


def unmet_blocks(unit_id, fm, body, unit_dir, project_root=".", point="approve", policy=None):
    """이 집행 지점에서 **막는** 차단 목록 → `[(block_id, 이유)]`. 라우팅을 문서 frontmatter 에서 다시 계산한다.

    차단은 분류에서 나오므로 저장된 값을 읽지 않고 재계산한다 — 문서의 `routing.fired_rules` 는 만든 시점의 기록이고,
    정책표가 바뀌면 낡는다. 재계산은 정책표를 원본으로 두는 유일한 방법이다(K-63)."""
    pol = policy or load_policy()
    out = route(classification_from_frontmatter(fm), pol, project_state=load_project_state(project_root))
    return [(bid, why) for bid, ok, why
            in evaluate_blocks(pol["packages"], out["blocks"], point, unit_dir, fm, body,
                               context=block_context(out, project_root)) if not ok]


def block_context(route_out, project_root):
    """차단 판정이 **문서 밖에서** 받아야 하는 사실. 문서에 적힌 값으로 그 문서를 판정하지 않는다.

    `capabilities` 는 라우터가 요구한 능력 목록이고, `project_root` 는 프로브가 흔적 경로를 볼 기준이다."""
    return {"capabilities": list((route_out or {}).get("capabilities") or []),
            "project_root": project_root, "harness_root": HARNESS_ROOT}


def _iso(value):
    """approved_at 을 문자열로 정규화한다. 따옴표 없이 적힌 값은 YAML 이 datetime 으로 읽어 `str()` 이 다른 모양이 된다."""
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _approval_key(fm):
    """승인 하나를 식별하는 값. 재승인은 approved_at 이 같은 초에 찍힐 수 있으므로 이력 길이를 함께 본다."""
    return (_iso(fm.get("approved_at")), len(fm.get("approval_history") or []))


def approval_key(fm):
    """작업 트리 spec 의 **현재 승인**을 식별하는 값. `approval_keys_known` 의 마지막 원소와 같다."""
    return _approval_key(fm)


def approval_keys_known(fm):
    """이 spec 이 겪은 모든 승인의 식별값 — 이력(`approval_history`) 순서대로, 마지막이 현재 승인이다.
    재승인 뒤에도 이전 승인으로 만든 계약·봉투를 **식별**할 수 있어야 한다(지우지 않는다 — 동등성 관측의 표본이다)."""
    history = fm.get("approval_history") or []
    keys = [(_iso((h or {}).get("approved_at")), i) for i, h in enumerate(history)]
    keys.append(_approval_key(fm))
    return keys


def approval_key_at(project_root, sha, unit_id):
    """커밋 `sha` 의 spec 블롭이 담은 승인의 식별값. 블롭이 없거나 승인 상태가 아니면 None."""
    project_root = Path(project_root).resolve()
    spec_rel = rel(find_unit_dir(project_root, unit_id) / "spec.md", project_root)
    proc = subprocess.run(["git", "show", f"{sha}:{spec_rel}"], cwd=str(project_root), capture_output=True)
    if proc.returncode != 0:
        return None
    cfm, _ = frontmatter.split(proc.stdout.decode("utf-8", "replace"))
    if not cfm or not _is_approved(cfm):
        return None
    return _approval_key(cfm)


def first_approval_commit(project_root, unit_id):
    """이 단위가 **처음** 승인된 커밋 — 이력에서 승인 상태의 spec 블롭(이 단위가 겪은 승인 중 하나)을 처음 담은 커밋.
    재승인이 있어도 움직이지 않는다. 증거의 변경 기준(`evidence._change_base`)이 쓴다 — 구현은 첫 승인 뒤에 시작되므로."""
    project_root = Path(project_root).resolve()
    spec = find_unit_dir(project_root, unit_id) / "spec.md"
    fm, _ = frontmatter.read(spec)
    if not fm.get("approved_at"):
        raise ValueError(f"{unit_id}: 승인 기록이 없다")
    # 이력의 가장 오래된 승인 블롭이다 — 이 단위의 spec 이 승인 상태로 커밋된 적이 있으면 그것이 첫 승인이다.
    # approval_history 없이 손으로 재승인한 옛 단위에서는 작업 트리가 그 승인을 '모르지만', 변경의 기준은 여전히 거기다.
    for sha, _cfm in _approved_blobs(project_root, unit_id):
        return sha
    raise ValueError(f"{unit_id}: 승인이 아직 커밋되지 않았다")


def _approved_blobs(project_root, unit_id):
    """현재 HEAD 이력에서 spec.md 가 승인 상태로 커밋된 (커밋, frontmatter) 를 오래된 순으로."""
    project_root = Path(project_root).resolve()
    spec_rel = rel(find_unit_dir(project_root, unit_id) / "spec.md", project_root)
    log = subprocess.run(["git", "log", "--reverse", "--format=%H", "--", spec_rel],
                         cwd=str(project_root), capture_output=True, text=True)
    out = []
    for sha in (log.stdout.split() if log.returncode == 0 else []):
        proc = subprocess.run(["git", "show", f"{sha}:{spec_rel}"], cwd=str(project_root), capture_output=True)
        if proc.returncode != 0:
            continue
        cfm, _ = frontmatter.split(proc.stdout.decode("utf-8", "replace"))
        if cfm and _is_approved(cfm):
            out.append((sha, cfm))
    return out


def approval_rollback_error(project_root, unit_id):
    """작업 트리의 승인이 **커밋된 것보다 뒤로 물러났는지** 본다. 물러났으면 이유, 아니면 None.

    승인 키의 원본은 작업 트리 frontmatter 다 — 커밋 없이 approved_at 을 옛 값으로 되돌리고 이력을 지우면 approval_commit() 이
    옛 승인 커밋을 찾아 재승인이 추가한 검사가 사라진다(설계 검토가 재현했다). 그래서 HEAD 의 spec 블롭과 대조한다:
    HEAD 블롭이 승인 상태면 그 승인들은 전부 작업 트리가 아는 승인이어야 하고(HEAD 의 승인 목록이 작업 트리 목록의 접두),
    작업 트리의 현재 승인이 HEAD 블롭의 이력 안(= 이미 대체된 승인)이면 물러난 것이다."""
    project_root = Path(project_root).resolve()
    spec = find_unit_dir(project_root, unit_id) / "spec.md"
    fm, _ = frontmatter.read(spec)
    spec_rel = rel(spec, project_root)
    proc = subprocess.run(["git", "show", f"HEAD:{spec_rel}"], cwd=str(project_root), capture_output=True)
    if proc.returncode != 0:
        return None
    hfm, _ = frontmatter.split(proc.stdout.decode("utf-8", "replace"))
    if not hfm or not _is_approved(hfm):
        return None
    head_keys, work_keys = approval_keys_known(hfm), approval_keys_known(fm)
    if work_keys[:len(head_keys)] != head_keys:
        return (f"작업 트리의 승인 기록이 HEAD 에 커밋된 것과 어긋난다 — HEAD {head_keys[-1][0]}(이력 {len(head_keys) - 1}건) vs "
                f"작업 트리 {work_keys[-1][0]}(이력 {len(work_keys) - 1}건). 승인은 앞으로만 간다: 커밋된 승인을 손으로 되돌리거나 "
                f"지우지 않는다(D-27). 다시 승인하려면 romeo approve --reapprove 를 쓴다")
    return None


def approval_chain_warnings(project_root, unit_id):
    """이력의 승인 블롭들이 **approve 명령을 거친 사슬**인지 본다 — 어긋난 자리마다 문장 하나.

    approve --reapprove 는 이전 승인을 approval_history 에 쌓으므로, 연속한 두 승인 블롭은 앞의 승인 목록이 뒤의 접두여야 한다.
    approved_at 만 손으로 새 값으로 바꿔 커밋하면(가짜 재승인) 사슬이 끊긴다. 옛 단위(이력 없이 손으로 재승인한 것)도 같은 모양이라
    이 검사는 차단이 아니라 경고다 — 승인 사건을 기계가 확인할 수 있는 형태(서명된 승인 커밋 등)로 만드는 것은 사용자 결정이다."""
    out = []
    prev = None
    for sha, cfm in _approved_blobs(project_root, unit_id):
        keys = approval_keys_known(cfm)
        if prev is not None and keys[:len(prev[1])] != prev[1] and keys != prev[1]:
            out.append(f"{prev[0][:12]} → {sha[:12]}: 승인 {prev[1][-1][0]} 이 {keys[-1][0]} 의 이력에 없다 — "
                       f"romeo approve --reapprove 를 거치지 않은 승인(손으로 바꾼 approved_at 이거나 옛 방식의 재승인)")
        prev = (sha, keys)
    return out


def approval_commit(project_root, unit_id):
    """승인 커밋 — 작업 트리 spec 의 **현재 승인**이 처음 커밋된 커밋(현재 HEAD 의 이력, 오래된 순).

    위임된 작업 공간은 커밋된 것만 보므로 계약은 승인이 들어 있는 커밋에서만 계산된다(D-a). 그 커밋을 파일에 적어 두면
    승인 시점의 HEAD 밖에 적을 수 없고 그것은 승인을 담지 않는 커밋이다(체크리스트 38). 그래서 여기서 이력을 걸어 찾는다:
    `git log --reverse -- spec.md` 의 각 커밋에서 spec 블롭의 frontmatter 를 읽어, 지금 작업 트리의 승인(approved_at·재승인 이력 길이)과
    같은 승인을 담은 첫 커밋이 승인 커밋이다. 재승인하면 새 승인을 담은 커밋이 새 승인 커밋이 된다.

    승인이 아직 커밋되지 않았으면 거부한다 — 이전 승인 커밋으로 조용히 되돌아가면 재승인 전의 계획으로 계약이 만들어진다."""
    project_root = Path(project_root).resolve()
    spec = find_unit_dir(project_root, unit_id) / "spec.md"
    fm, _ = frontmatter.read(spec)
    if not _is_approved(fm):
        raise ValueError(f"{unit_id}: 승인 기록이 없다 (status={fm.get('status')} approved_at={fm.get('approved_at')}) — "
                         f"romeo approve 로 승인을 기록한다(D-27)")
    rolled = approval_rollback_error(project_root, unit_id)
    if rolled:
        raise ValueError(f"{unit_id}: {rolled}")
    want = _approval_key(fm)
    for sha, cfm in _approved_blobs(project_root, unit_id):
        if _approval_key(cfm) == want:
            return sha
    raise ValueError(f"{unit_id}: 승인(approved_at {_iso(fm.get('approved_at'))})이 아직 커밋되지 않았다 — "
                     f"승인된 spec.md 를 커밋한 뒤 다시 실행한다. 다른 커밋을 쓰려면 --base-sha <승인 커밋 SHA> 를 명시한다(D-a). "
                     f"(작업 트리의 approved_at 이 따옴표 없이 적혀 형식만 다른 경우도 여기 걸린다)")


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
