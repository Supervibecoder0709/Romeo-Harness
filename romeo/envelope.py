"""작업 계약(TaskEnvelope) 생성 — 승인된 Tech Spec 과 라우터 출력에서 계약을 계산한다.

계약을 만드는 주체는 하네스다. 에이전트가 JSON 을 손으로 쓰면 '같은 입력이면 같은 계약' 이 성립하지 않는다.
여기서 계약은 **커밋된 spec.md** 에서만 계산한다(`base_sha`) — 위임된 실행 공간은 커밋된 것만 볼 수 있고,
승인이 그 안에서 보이지 않으면 워커는 승인 없이 구현하게 되기 때문이다(D-a·D-27).
같은 (unit_id · role · base_sha · 정책표)에는 항상 바이트 단위로 같은 계약이 나온다 —
시각·난수 같은 비결정 값을 담지 않는다."""
import json
import re
import subprocess
from pathlib import Path

from . import HARNESS_ROOT, frontmatter
from .close import ENVELOPE_CHECKS, UNREADABLE, UNVERIFIED, envelope_checks, required_checks
from .docs import find_unit_dir
from .gitinfo import head_sha, is_repo
from .parity import load_role_contracts
from .policy import classification_from_frontmatter, load_policy, load_project_state, route
from .schema import validate as validate_schema
from .util import load_json, load_yaml, rel, sha256_bytes

SCHEMA_ID = "romeo/task-envelope@0.1.0"
TASK_SCHEMA = "core/schemas/task-envelope.json"
OUTPUT_SCHEMA = "core/schemas/result-envelope.json"
ROLES = ("implementer", "reviewer")
WORKSPACES = ("current", "worktree")


def _rev_parse(project_root, ref):
    proc = subprocess.run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
                          cwd=str(project_root), capture_output=True, text=True)
    if proc.returncode != 0:
        raise ValueError(f"base_sha 로 쓸 커밋을 찾을 수 없다: {ref}")
    return proc.stdout.strip()


def _committed_bytes(project_root, sha, relpath):
    """커밋 시점의 파일 내용(바이트). 없으면 None. 워커가 그 리비전에서 보게 될 것과 같은 바이트다."""
    proc = subprocess.run(["git", "show", f"{sha}:{relpath}"], cwd=str(project_root), capture_output=True)
    return None if proc.returncode != 0 else proc.stdout


def _approved(fm):
    return fm.get("status") == "active" and bool(fm.get("approved_at"))


def _head_hint(project_root, spec_rel, sha):
    """HEAD 에는 승인된 spec 이 있는데 지목된 커밋에는 없을 때, 무엇을 쓰면 되는지 알려준다."""
    try:
        head = head_sha(project_root)
    except Exception:
        return ""
    if head == sha:
        return ""
    raw = _committed_bytes(project_root, head, spec_rel)
    if raw is None:
        return ""
    fm, _ = frontmatter.split(raw.decode("utf-8", "replace"))
    if fm and _approved(fm):
        return f" HEAD({head[:12]}) 에는 승인된 spec.md 가 있다 — --base-sha {head} 로 다시 실행한다."
    return ""


CHANGE_SCOPE_HEADING = "## 변경 범위"
CHANGE_SCOPE_LABEL = "바뀌는 파일·모듈:"
# 항목 구분자. 라벨 자체에도 `·` 가 있으므로 라벨 뒤부터 나눈다.
CHANGE_SCOPE_SEP = "·"


def change_scope_paths(body):
    """승인된 spec 의 「변경 범위」가 **바뀌는 파일·모듈** 로 선언한 경로들. 백틱 안의 값만 읽는다.

    쓰기 상한을 역할 계약의 `must_include` 만으로 두면 작업 공간 전체(`.`)가 열린다 — 그러면
    검토 항목 '변경이 allowed_paths 안인가' 가 아무것도 걸러내지 못한다(2026-08-29 검토자 3명이 같은 자리를 지적했다).
    상한의 출처는 사람이 승인한 문장이어야 하므로, 승인된 spec 이 스스로 선언한 범위를 그대로 옮긴다.
    저장소 밖을 가리키는 값은 버린다 — 계약은 작업 공간 안에서만 유효하다(K-66)."""
    inside = False
    for line in (body or "").split("\n"):
        if line.startswith("## "):
            inside = line.strip() == CHANGE_SCOPE_HEADING
            continue
        if inside and CHANGE_SCOPE_LABEL in line:
            out = []
            # 항목은 `·` 로 나뉘고 **각 항목의 첫 백틱이 그 항목의 경로**다. 뒤따르는 백틱은 설명이다
            # (예: `scripts/generate-archive-index.py`(`collect` 에 …) — collect 는 함수 이름이지 경로가 아니다).
            for chunk in line.split(CHANGE_SCOPE_LABEL, 1)[1].split(CHANGE_SCOPE_SEP):
                found = re.search(r"`([^`]+)`", chunk)
                if not found:
                    continue
                text = found.group(1).strip().replace("\\", "/")
                if not text or text.startswith("/") or text.startswith("~") or ".." in text.split("/"):
                    continue
                if text not in out:
                    out.append(text)
            return out
    return []


def _allowed_paths(harness_root, role, unit_id, body=None):
    """역할 계약(core/roles/<role>.yaml)이 정한 범위와 **spec 이 선언한 변경 범위**의 교집합을 계약서에 적는다.

    계약이 정하지 않은 경로를 적지 않고(K-66), 승인이 정하지 않은 경로도 적지 않는다."""
    contract = load_yaml(Path(harness_root) / "core/roles" / f"{role}.yaml") or {}
    ap = contract.get("allowed_paths") or {}
    scope = ap.get("scope")
    paths = [str(p).replace("{unit_id}", unit_id) for p in (ap.get("must_include") or [])]
    if scope == "none":
        return []
    if scope == "workspace":
        scoped = change_scope_paths(body)
        if not scoped:
            raise ValueError(
                f"{unit_id}: spec 의 「{CHANGE_SCOPE_HEADING[3:]}」 절에서 '{CHANGE_SCOPE_LABEL}' 줄의 "
                f"백틱 경로를 읽지 못했다 — 쓰기 상한을 승인된 문장에서 가져오지 못하면 계약을 만들지 않는다(K-66). "
                f"그 줄에 바뀌는 파일·모듈을 백틱으로 적고 다시 승인·커밋한다(D-27).")
        for path in scoped:
            if path not in paths:
                paths.append(path)
        return paths
    raise ValueError(f"{role} 역할 계약의 allowed_paths.scope 를 모른다: {scope!r}")


def build_envelope(unit_id, role, project_root=".", harness_root=None, base_sha=None):
    """승인된 spec 에서 작업 계약을 계산한다(파일을 쓰지 않는다).

    base_sha 를 생략하면 spec frontmatter 의 base_sha 를 쓴다. 그 커밋에 승인된 spec.md 가 없으면
    계약을 만들지 않고 거부한다 — 워커가 볼 수 없는 승인은 승인이 아니다."""
    if role not in ROLES:
        raise ValueError(f"역할을 모른다: {role!r} (허용: {' · '.join(ROLES)})")
    project_root = Path(project_root).resolve()
    harness_root = Path(harness_root or HARNESS_ROOT)
    if not is_repo(project_root):
        raise ValueError("git 저장소가 아니다 — 작업 계약은 커밋된 승인(base_sha)에 묶인다")
    udir = find_unit_dir(project_root, unit_id)
    spec = udir / "spec.md"
    spec_rel = rel(spec, project_root)
    work_fm, _ = frontmatter.read(spec)
    ref = base_sha or work_fm.get("base_sha")
    if not ref:
        raise ValueError(f"{unit_id}: base_sha 가 없다 — 승인 기록이 없다(romeo approve 로 승인을 기록한다)")
    sha = _rev_parse(project_root, ref)
    raw = _committed_bytes(project_root, sha, spec_rel)
    if raw is None:
        raise ValueError(f"{sha[:12]} 에 {spec_rel} 가 없다 — 승인된 spec.md 를 커밋한 뒤 "
                         f"--base-sha <커밋 SHA> 로 다시 만든다(D-a)." + _head_hint(project_root, spec_rel, sha))
    fm, body = frontmatter.split(raw.decode("utf-8"))
    if fm is None:
        raise ValueError(f"{sha[:12]}:{spec_rel} 에 frontmatter 가 없다")
    if fm.get("id") != unit_id:
        raise ValueError(f"{sha[:12]}:{spec_rel} 의 id 가 {fm.get('id')!r} 다 — {unit_id!r} 의 계약이 아니다")
    if not _approved(fm):
        raise ValueError(f"{sha[:12]} 시점의 {spec_rel} 는 승인 상태가 아니다 "
                         f"(status={fm.get('status')} approved_at={fm.get('approved_at')}) — "
                         f"승인 없이 구현하지 않는다(D-27). 승인된 spec.md 를 커밋한 뒤 "
                         f"--base-sha <커밋 SHA> 로 다시 만든다(D-a)." + _head_hint(project_root, spec_rel, sha))

    pol = load_policy(harness_root)
    out = route(classification_from_frontmatter(fm), pol, project_state=load_project_state(project_root))
    if out["isolation"] not in WORKSPACES:
        raise ValueError(f"{unit_id}: 격리가 {out['isolation']!r} 다 — 문서 패키지가 없는 분류에는 작업 계약을 만들지 않는다")
    checks = []
    for rc in required_checks(body):
        item = {"id": str(rc.get("id") or ""), "command": str(rc.get("command") or "")}
        if rc.get("expect") is not None:
            item["expect"] = str(rc["expect"])
        checks.append(item)
    env = {
        "schema": SCHEMA_ID,
        "unit_id": unit_id,
        "role": role,
        "spec_ref": {"path": spec_rel, "sha256": sha256_bytes(raw)},
        "base_sha": sha,
        "allowed_paths": _allowed_paths(harness_root, role, unit_id, body),
        "guards": [{"id": g["id"], "name": g["name"]} for g in out["guards"]],
        "required_checks": checks,
        "output_schema": OUTPUT_SCHEMA,
        "workspace": out["isolation"],
    }
    errors = validate_schema(env, load_json(harness_root / TASK_SCHEMA))
    if errors:
        raise ValueError(f"작업 계약이 {TASK_SCHEMA} 에 맞지 않는다: " + "; ".join(errors))
    return env


def envelope_text(env):
    """직렬화 규칙은 한 곳에만 둔다 — 같은 계약은 같은 바이트여야 비교·해시가 성립한다."""
    return json.dumps(env, ensure_ascii=False, indent=2) + "\n"


def check_result_envelope(path, unit_id, role=None, project_root=".", harness_root=None):
    """결과 계약(ResultEnvelope) 파일 **하나**를 검사한다 — 결과를 회수한 쪽이 부르는 명령이다.

    검사 규칙은 여기에 다시 적지 않는다. 종료 검사가 검토자 봉투에 쓰는 함수(`close.envelope_checks`)를
    그대로 부른다 — 규칙이 두 벌이 되면 느슨한 쪽이 done 을 만든다(K-63).
    `role` 을 주면 그 역할의 결과인지 대조하고, 생략하면 봉투가 스스로 밝힌 역할로 능력 범위만 본다.

    돌려주는 판정은 셋이다: PASS(다섯 검사 모두 통과) · FAIL(하나라도 어긋남) ·
    UNVERIFIED(어긋난 것은 없으나 대조가 성립하지 않은 검사가 있다). 마지막은 통과가 아니다(K-51)."""
    project_root = Path(project_root).resolve()
    harness_root = Path(harness_root or HARNESS_ROOT)
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"결과 계약 파일이 없다: {path}")
    udir = find_unit_dir(project_root, unit_id)
    schema = load_json(harness_root / OUTPUT_SCHEMA)
    roles = load_role_contracts(harness_root)
    try:
        env = load_json(path)
    except Exception as e:
        rows = [("ENVELOPE_VALID", False, f"JSON 을 읽을 수 없다 ({e})")] + [
            (cid, UNVERIFIED, UNREADABLE) for cid in ENVELOPE_CHECKS[1:]]
    else:
        rows = envelope_checks(env, unit_id, role, project_root, udir, roles, schema, side="result",
                               harness_root=harness_root)
    states = [s for _cid, s, _why in rows]
    verdict = "FAIL" if False in states else ("UNVERIFIED" if UNVERIFIED in states else "PASS")
    return {"path": str(path), "unit_id": unit_id, "role": role, "verdict": verdict,
            "checks": [{"id": cid, "state": ("PASS" if s is True else "FAIL" if s is False else "UNVERIFIED"),
                        "detail": why} for cid, s, why in rows]}


def format_result_check(res):
    """검사 결과 한 건을 인쇄한다. 무엇이 왜 틀렸는지가 줄마다 보여야 한다 — 판정만으로는 고칠 수 없다."""
    lines = [f"romeo envelope check {res['path']} → {res['verdict']}"
             f" (unit {res['unit_id']}" + (f" · role {res['role']}" if res["role"] else "") + ")"]
    for c in res["checks"]:
        lines.append(f"  [{c['state']}] {c['id']}" + (f" — {c['detail']}" if c["detail"] else ""))
    return "\n".join(lines)


def write_envelope(unit_id, role, project_root=".", harness_root=None, base_sha=None, run_name=None):
    """계약을 작업 단위 폴더 안(`docs/work/<id>/task/`)에 쓴다 — 등록되지 않은 산출물은 종료 검사가 인정하지 않는다(K-62)."""
    project_root = Path(project_root).resolve()
    env = build_envelope(unit_id, role, project_root=project_root, harness_root=harness_root, base_sha=base_sha)
    tdir = find_unit_dir(project_root, unit_id) / "task"
    tdir.mkdir(exist_ok=True)
    path = tdir / (f"{run_name}-{role}.json" if run_name else f"{role}.json")
    text = envelope_text(env)
    path.write_text(text, encoding="utf-8")
    return {"path": str(path), "envelope": env, "sha256": sha256_bytes(text.encode("utf-8"))}
