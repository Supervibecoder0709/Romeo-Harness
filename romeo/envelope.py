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
from .docs import approval_commit, approval_key, approval_keys_known, find_unit_dir
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


def _approval_hint(project_root, unit_id):
    try:
        return approval_commit(project_root, unit_id)[:12]
    except ValueError:
        return "(아직 커밋되지 않았다)"


CHANGE_SCOPE_HEADING = "## 변경 범위"
CHANGE_SCOPE_LABEL = "바뀌는 파일·모듈:"
# 항목 구분자. 라벨 자체에도 `·` 가 있으므로 라벨 뒤부터 나눈다.
CHANGE_SCOPE_SEP = "·"
# 설명이 사는 자리 — 괄호 `(…)`·`（…）`. 안쪽 짝부터 반복해 지우므로 중첩도 지워진다(Q-36).
_PAREN_RE = re.compile(r"[(（][^()（）]*[)）]", re.S)
_BACKTICK_RE = re.compile(r"`([^`]+)`")
# 괄호를 지우기 전에 빼 두는 백틱 토큰 — 한 줄 안에서만 짝을 짓는다(옛 규칙도 줄마다 읽었다 — 줄을 넘긴 짝을 새로 만들지 않는다).
_HELD_BACKTICK_RE = re.compile(r"`[^`\n]+`")
_HOLD_MARK = "\x00"
_HELD_RE = re.compile(_HOLD_MARK + r"(\d+)" + _HOLD_MARK)


def _blank_parentheses(text):
    """**백틱 밖 구간의** 괄호 안을 공백으로 바꾼다 — **줄바꿈은 남긴다.**

    백틱 토큰을 먼저 자리표로 빼 두고 그 사이 텍스트에서만 괄호를 지운다. 경로 안의 괄호(`app/(g)/page.tsx`)는 경로의 일부라
    살아야 하고, 괄호 안의 백틱(`(설명 · `b/y.py` 는 그대로)`)은 설명이라 괄호와 함께 지워진다 — 자리표는 괄호 문자를 담지 않으므로
    괄호 짝의 안팎 어느 한쪽에 통째로 놓인다.
    줄을 지우면 괄호가 줄을 넘긴 뒤의 항목(`… ·\n  overlay · …) · `b/y.py``)이 앞 줄에 붙어 첫 백틱 규칙이 바뀐다.
    안쪽 짝부터 반복해 지우고, 짝이 없는 괄호는 그대로 둔다(뒤를 통째로 지우지 않는다)."""
    held = []

    def _hold(found):
        held.append(found.group(0))
        return f"{_HOLD_MARK}{len(held) - 1}{_HOLD_MARK}"

    text = _HELD_BACKTICK_RE.sub(_hold, text.replace(_HOLD_MARK, ""))
    while True:
        found = _PAREN_RE.search(text)
        if not found:
            break
        blanked = "".join("\n" if ch == "\n" else " " for ch in found.group(0))
        text = text[:found.start()] + blanked + text[found.end():]
    # 괄호 안에 있던 토큰의 자리표는 위에서 공백이 됐다 — 남은 자리표만 원래 토큰으로 되돌린다.
    return _HELD_RE.sub(lambda m: held[int(m.group(1))], text)


def _path_shaped(token):
    """경로 모양인가 — 공백이 없고 `/` 나 `.` 이 있다. 함수명(`cmd_card`)·플래그(`--root`)·문장(`a b`)은 경로가 아니다."""
    return re.search(r"\s", token) is None and ("/" in token or "." in token)


def change_scope_report(body):
    """승인된 spec 의 「변경 범위」가 **바뀌는 파일·모듈** 로 선언한 경로들과, 백틱이지만 경로로 읽지 않은 토큰들.

    → `{"paths": [...], "ignored": [...]}`. `paths` 가 쓰기 상한이고 `ignored` 는 인쇄용이다 — 계약 JSON 에는 들어가지 않는다.

    쓰기 상한을 역할 계약의 `must_include` 만으로 두면 작업 공간 전체(`.`)가 열린다 — 그러면
    검토 항목 '변경이 allowed_paths 안인가' 가 아무것도 걸러내지 못한다(2026-08-29 검토자 3명이 같은 자리를 지적했다).
    상한의 출처는 사람이 승인한 문장이어야 하므로, 승인된 spec 이 스스로 선언한 범위를 그대로 옮긴다.
    저장소 밖을 가리키는 값은 버린다 — 계약은 작업 공간 안에서만 유효하다(K-66).

    선언이 **한 줄을 넘겨도 전부 읽는다**(Q-18). 라벨 줄에서 곧바로 `return` 하면 뒤 줄의 경로가
    `allowed_paths` 에서 조용히 빠지는데, 빈 경우와 달리 부분 읽기는 아무 경고도 내지 않아
    계약은 정상으로 보이고 구현자가 쓰려는 순간에야 막힌다(2026-08-31 `feat-20260831-bmad-attach-probe-tgnb`
    1회차가 이것으로 실패했다 — 선언한 9개 중 2개만 실렸다).
    이어 읽기는 **다음 항목을 삼키지 않는다**: 다음 목록 항목(`- `)·다음 제목(`#`)·빈 줄에서 멈춘다.
    「영향을 받는 부분」 은 승인이 *쓰기 상한*으로 정한 것이 아니므로 상한에 들어가면 안 된다(K-66).

    **설명 산문은 상한이 아니다**(Q-36). 종전에는 `·` 로 자른 조각의 첫 백틱을 무조건 경로로 읽어, 괄호 안 설명이
    줄을 넘기자 다음 줄 첫 조각의 첫 백틱 — 함수명 `cmd_card` — 이 `allowed_paths` 에 실렸다(2026-09-02 시나리오 8 5회차).
    넓어지는 방향이라 판정은 안 바뀌었지만, 승인하지 않은 경로가 상한에 조용히 들어가는 구멍이다. 그래서 문법을 둔다:
    ① 괄호 `(…)`·`（…）` 안은 줄 경계를 보존한 채 공백으로 바꾼다(중첩은 반복 제거) — 괄호 안의 백틱은 경로 모양이어도 상한이 아니다.
       지우는 것은 **백틱 밖 구간**의 괄호다 — 경로 안의 괄호(`app/(g)/page.tsx`)는 경로의 일부라 남는다
    ② 줄마다 `·` 로 나눠 각 조각의 첫 백틱을 읽는 것은 그대로다 — 뒤따르는 백틱은 괄호 밖이어도 상한이 아니다
    ③ 읽은 토큰이 경로 모양이 아니면(공백이 있거나 `/` 도 `.` 도 없으면) 상한에 넣지 않고 `ignored` 에 모은다
    ④ 앞의 `./` 는 벗긴다 — 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다.
    이 문법은 spec 을 쓰는 사람이 읽는 자리(`core/templates/tech-spec.md` 「변경 범위」)에도 적혀 있다 — 요구하는 자리와
    보는 자리를 같게 둔다(AGENTS.core §11)."""
    inside = False
    lines = (body or "").split("\n")
    for i, line in enumerate(lines):
        if line.startswith("## "):
            inside = line.strip() == CHANGE_SCOPE_HEADING
            continue
        if inside and CHANGE_SCOPE_LABEL in line:
            declared = [line.split(CHANGE_SCOPE_LABEL, 1)[1]]
            for nxt in lines[i + 1:]:
                if nxt.startswith("#") or nxt.startswith("- ") or not nxt.strip():
                    break
                declared.append(nxt)
            paths, ignored = [], []
            # 항목은 `·` 로 나뉘고 **각 항목의 첫 백틱이 그 항목의 경로**다. 뒤따르는 백틱은 설명이다
            # (예: `scripts/generate-archive-index.py`(`collect` 에 …) — collect 는 함수 이름이지 경로가 아니다).
            for raw in _blank_parentheses("\n".join(declared)).split("\n"):
                for chunk in raw.split(CHANGE_SCOPE_SEP):
                    found = _BACKTICK_RE.search(chunk)
                    if not found:
                        continue
                    text = found.group(1).strip().replace("\\", "/")
                    if not text:
                        continue
                    if not _path_shaped(text):
                        if text not in ignored:
                            ignored.append(text)
                        continue
                    while text.startswith("./"):
                        text = text[2:]
                    if not text or text.startswith("/") or text.startswith("~") or ".." in text.split("/"):
                        continue
                    if text not in paths:
                        paths.append(text)
            return {"paths": paths, "ignored": ignored}
    return {"paths": [], "ignored": []}


def change_scope_paths(body):
    """`change_scope_report(body)["paths"]` — 승인된 spec 이 선언한 쓰기 상한. 규칙은 그 함수의 설명에 있다."""
    return change_scope_report(body)["paths"]


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
        report = change_scope_report(body)
        scoped = report["paths"]
        if not scoped:
            hint = ""
            if report["ignored"]:
                hint = (f" 백틱은 있었지만 경로 모양이 아니어서 읽지 않은 토큰: {report['ignored']} — "
                        f"경로는 `/` 나 `.` 을 담고 공백이 없어야 한다(루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다).")
            raise ValueError(
                f"{unit_id}: spec 의 「{CHANGE_SCOPE_HEADING[3:]}」 절에서 '{CHANGE_SCOPE_LABEL}' 줄의 "
                f"백틱 경로를 읽지 못했다 — 쓰기 상한을 승인된 문장에서 가져오지 못하면 계약을 만들지 않는다(K-66). "
                f"그 줄에 바뀌는 파일·모듈을 백틱으로 적고 다시 승인·커밋한다(D-27)." + hint)
        for path in scoped:
            if path not in paths:
                paths.append(path)
        return paths
    raise ValueError(f"{role} 역할 계약의 allowed_paths.scope 를 모른다: {scope!r}")


def build_envelope(unit_id, role, project_root=".", harness_root=None, base_sha=None, allow_superseded=False):
    """승인된 spec 에서 작업 계약을 계산한다(파일을 쓰지 않는다).

    base_sha 를 생략하면 **이력에서 승인 커밋을 찾는다**(`docs.approval_commit`) — spec frontmatter 의 base_sha 는 읽지 않는다.
    그 값은 승인 시점의 HEAD 라 승인을 담지 않는 커밋(승인 커밋의 부모)을 가리켰다(체크리스트 38).
    지목된 커밋에 승인된 spec.md 가 없으면 계약을 만들지 않고 거부한다 — 워커가 볼 수 없는 승인은 승인이 아니다.

    명시한 base_sha 도 검사한다: 그 커밋의 spec 이 담은 승인이 **지금의 승인**과 같아야 한다. 재승인 전 커밋을 주면
    이전 승인본의 검증 계획으로 계약이 만들어지므로(이 결함이 실제로 5건 대 6건으로 났다) 거부한다 —
    `allow_superseded=True` 는 종료 검사의 재계산 대조에서만 쓴다: 이전 승인으로 만든 봉투도 봉투로 **식별**은 돼야 하고,
    그것을 지금의 판정에 세지 않는 것은 그쪽의 일이다."""
    return _compute_envelope(unit_id, role, project_root=project_root, harness_root=harness_root,
                             base_sha=base_sha, allow_superseded=allow_superseded)[0]


def _compute_envelope(unit_id, role, project_root=".", harness_root=None, base_sha=None, allow_superseded=False):
    """`build_envelope` 의 본체 — (계약, 「변경 범위」 읽기 결과) 를 돌려준다.

    두 번째 값은 인쇄용이다(`write_envelope` 가 `scope_ignored` 로 싣는다). 계약 JSON 에는 넣지 않는다 —
    종료 검사와 동등성 관측이 계약을 승인 원본에서 다시 계산해 바이트로 대조하므로 필드가 늘면 옛 계약의 앵커가 전부 열리지 않는다."""
    if role not in ROLES:
        raise ValueError(f"역할을 모른다: {role!r} (허용: {' · '.join(ROLES)})")
    project_root = Path(project_root).resolve()
    harness_root = Path(harness_root or HARNESS_ROOT)
    if not is_repo(project_root):
        raise ValueError("git 저장소가 아니다 — 작업 계약은 커밋된 승인(base_sha)에 묶인다")
    udir = find_unit_dir(project_root, unit_id)
    spec = udir / "spec.md"
    spec_rel = rel(spec, project_root)
    ref = base_sha or approval_commit(project_root, unit_id)
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
    # 새 계약은 **지금의 승인**에서만 만든다. 재계산 대조(allow_superseded)는 식별만 하므로 이 검사를 건너뛴다 —
    # 이전 승인으로 낸 봉투를 지금의 판정에 세지 않는 것은 종료 검사의 일이다(`close._check_review`).
    if not allow_superseded:
        work_fm, _ = frontmatter.read(spec)
        blob_key, known = approval_key(fm), approval_keys_known(work_fm)
        if blob_key != known[-1]:
            if blob_key in known:
                raise ValueError(
                    f"{sha[:12]} 시점의 {spec_rel} 는 재승인 **전**의 승인(approved_at {fm.get('approved_at')})을 담고 있다 — "
                    f"지금의 승인은 approved_at {work_fm.get('approved_at')} 이고 그 계약은 이전 검증 계획으로 만들어진다. "
                    f"현재 승인이 처음 커밋된 커밋은 {_approval_hint(project_root, unit_id)} 이다(D-a)")
            raise ValueError(
                f"{sha[:12]} 시점의 {spec_rel} 가 담은 승인(approved_at {fm.get('approved_at')})은 이 작업 트리의 spec 이 겪은 "
                f"어느 승인과도 맞지 않는다(현재 approved_at {work_fm.get('approved_at')}) — 다른 브랜치의 승인이거나 "
                f"손으로 고친 spec 이거나 재승인 전 승인이다. 같은 승인을 보고 있지 않으면 계약을 만들지 않는다(D-a)")

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
    return env, change_scope_report(body)


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


def repeat_gate(project_root, unit_id):
    """반복 중단 게이트(`AGENTS.core.md` §10). 차단이면 예외를 던져 계약을 만들지 못하게 한다.

    이 자리에 두는 이유: **계약 생성은 모든 관통의 첫 동작**이다. 게이트를 `run-unit` 안에만 두면
    RUNBOOK §3 을 손으로 밟는 관통에서는 한 번도 평가되지 않는다 — 직전 관통이 실제로 그랬다(2026-08-31 실측).
    어느 경로로 돌리든 이 자리를 지나므로, 여기서 막으면 3회차가 시작되지 않는다.

    시도 기록(`attempts.yaml`)이 없으면 실패 0 으로 본다. 지금 대부분의 단위가 그 상태이고,
    입구에 선 게이트가 기록 없는 단위까지 막으면 어떤 관통도 시작하지 못한다.

    `run_unit` 을 함수 안에서 부르는 것은 순환 import 때문이다 — 그쪽이 이 모듈의 `write_envelope` 를 쓴다."""
    from .run_unit import gate, load_attempts  # 순환 import 를 피해 여기서 부른다
    allowed, n, why = gate(load_attempts(project_root, unit_id))
    if not allowed:
        raise ValueError(f"{unit_id}: 반복 중단 — 작업 계약을 만들지 않는다. {why}")
    return n


def dispatch_gate(project_root, unit_id, harness_root=None):
    """구현 위임 직전의 집행. 차단이면 예외를 던져 계약을 만들지 못하게 한다.

    두 가지를 본다.

    **`dispatch` 에 걸린 차단.** `discovery-result` 가 여기 있다 — 조사 단위는 승인까지는 되고
    **구현으로 넘어가는 자리**에서 막힌다. 승인에서 막던 동안 그 단위는 조사를 시작할 창구가 없었다.

    **문서 패키지 전체의 미완료 토큰.** spec 하나가 아니라 charter·brief·spec 을 다 본다.
    라우터가 요구한 절이 brief 로 가면 승인도 종료도 그것을 읽지 않았고, 「첫 마일스톤(spike)」가
    빈 채로 구현이 나갔다(2026-09-01 실측). 승인 창구는 확인란 하나라는 규칙(D-60)은 그대로 두고,
    **워커에게 넘기기 전에** 패키지가 채워졌는지를 여기서 본다 — 워커가 읽을 문서이기 때문이다."""
    from .blocks import unit_docs
    from .docs import unmet_blocks
    udir = find_unit_dir(project_root, unit_id)
    fm, body = frontmatter.read(udir / "spec.md")
    unmet = unmet_blocks(unit_id, fm, body, udir, project_root=project_root, point="dispatch",
                         policy=load_policy(harness_root))
    if unmet:
        raise ValueError(f"{unit_id}: 차단이 충족되지 않아 작업 계약을 만들지 않는다 — "
                         + "; ".join(f"{b}: {why}" for b, why in unmet))
    open_loops = []
    for name, path in unit_docs(udir):
        n = path.read_text(encoding="utf-8").count("NEEDS_INPUT")
        if n:
            open_loops.append(f"{path.name} {n}곳")
    if open_loops:
        raise ValueError(f"{unit_id}: 문서 패키지에 미완료가 남아 있어 작업 계약을 만들지 않는다 — "
                         + " · ".join(open_loops)
                         + ". 워커는 이 문서를 읽고 구현한다 — 빈칸을 넘기면 워커가 그것을 추측한다")


def write_envelope(unit_id, role, project_root=".", harness_root=None, base_sha=None, run_name=None,
                   record_attempt=True):
    """계약을 작업 단위 폴더 안(`docs/work/<id>/task/`)에 쓴다 — 등록되지 않은 산출물은 종료 검사가 인정하지 않는다(K-62).

    **반복 중단 게이트가 여기서 걸린다**(`repeat_gate`). 계약을 계산하는 `build_envelope` 가 아니라 **쓰는** 자리에
    두는 이유는, 종료 검사가 봉투를 대조할 때 그 계산을 다시 부르기 때문이다(`close._check_review`) —
    거기서 막으면 차단된 단위는 지난 관통의 판정조차 대조하지 못한다. 막아야 할 것은 **새 관통의 시작**이다."""
    project_root = Path(project_root).resolve()
    repeat_gate(project_root, unit_id)
    dispatch_gate(project_root, unit_id, harness_root=harness_root)
    if role == "reviewer" and not run_name:
        # 검토 봉투는 계약 경로의 <run> 으로 자기 run 의 증거(방어 검사)에 묶인다 — run 없는 자리(task/reviewer.json)의 계약으로 낸
        # 판정은 종료 검사가 세지 않는다. 만들 수 있는 자리를 두면 함정이므로 여기서 거부한다.
        raise ValueError("검토자 계약에는 --run 이 필요하다 — 검토 판정은 task/<run>-reviewer.json 의 <run> 으로 그 run 의 증거에 묶인다")
    env, scope = _compute_envelope(unit_id, role, project_root=project_root, harness_root=harness_root, base_sha=base_sha)
    tdir = find_unit_dir(project_root, unit_id) / "task"
    tdir.mkdir(exist_ok=True)
    path = tdir / (f"{run_name}-{role}.json" if run_name else f"{role}.json")
    text = envelope_text(env)
    path.write_text(text, encoding="utf-8")
    started = record_start(project_root, unit_id, run_name, env["base_sha"]) if (run_name and record_attempt) else None
    # `scope_ignored` 는 인쇄용이다 — 「변경 범위」의 백틱 중 경로로 읽지 않은 것(Q-36). 계약 JSON 에는 없다.
    return {"path": str(path), "envelope": env, "sha256": sha256_bytes(text.encode("utf-8")),
            "attempt": started, "scope_ignored": scope["ignored"]}


def record_start(project_root, unit_id, run, base_sha):
    """이 run 의 기동을 `attempts.yaml` 에 남긴다 — 이미 있으면 회차를 늘리지 않는다(두 역할분 계약이 한 회차다).

    **같은 run 인데 `base_sha` 가 다르면 새 값으로 옮기고 이전 값을 `base_sha_history` 에 남긴다**(Q-42).
    관통 도중 재승인하면 계약·증거는 새 승인 커밋으로 옮겨가는데 회차는 기동 시점 값에 고정돼, 이력을 읽는 사람이
    「그 회차가 무엇을 겨눴는가」 를 잘못 읽었다(2026-09-02 5회차: 기록 `93f0c0a` vs 계약·증거 `01ec50d`).
    같으면 아무것도 쓰지 않는다 — 같은 입력에 같은 파일이어야 한다.

    회차를 만드는 창구가 `run-unit` 의 시작 경로뿐이던 동안, RUNBOOK §3 을 손으로 밟은 관통은
    성공하든 실패하든 **회차가 하나도 남지 않았다**(Q-27). 그래서 §10 의 연속 2회 실패 차단이
    그 경로에서 한 번도 세지 않았다 — 규칙은 문서에 있고 집행은 다른 경로에만 있었다.
    반복 중단 게이트가 이 자리에 있는 것과 같은 이유로 회차 기록도 여기 둔다: **어느 경로로 돌리든 지난다.**"""
    from .run_unit import load_attempts, save_attempts, start_attempt  # 순환 import 를 피해 여기서 부른다
    data = load_attempts(project_root, unit_id)
    for att in data.get("attempts") or []:
        if att.get("run") == run:
            if base_sha and att.get("base_sha") != base_sha:
                history = list(att.get("base_sha_history") or [])
                history.append(att.get("base_sha"))
                att["base_sha_history"] = history
                att["base_sha"] = base_sha
                save_attempts(project_root, unit_id, data)
            return att
    entry = start_attempt(data, run, base_sha)
    save_attempts(project_root, unit_id, data)
    return entry
