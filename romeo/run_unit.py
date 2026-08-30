"""`romeo run-unit` — 관통 1회를 한 명령으로 엮는다.

RUNBOOK §3 의 수동 순서를 그대로 옮긴 상위 계층이다. 판정 로직을 새로 만들지 않는다 —
계약 생성은 `envelope build`, 앵커 검증은 `envelope check`, 증거는 `evidence` 모듈,
관측 등록은 `fixtures/parity/` 케이스 파일이 소유한다. 여기가 하는 일은 **순서와 기록**뿐이다.

두 가지를 더 한다.

1. **반복 중단**(`AGENTS.core.md` §10). 같은 작업 단위에서 관통이 연속 2회 실패하면 3회차 기동을 거부한다.
   사람이 완료 정의를 재검토하고 그 결론을 `--after-review` 로 주면 기록하고 진행한다.
   실패 원인 분류는 **기록만 하고 차단 판정에 쓰지 않는다** — 원인 오판이 그 반복을 만들었기 때문이다.
2. **기동은 기본이 dry-run 이다.** 실제로 워커를 띄우는 것은 비용이 드는 실행이라 `--spawn` 을 명시해야 한다(K-66).
"""
import re
import shlex
import subprocess
from pathlib import Path

from . import HARNESS_ROOT
from .close import harness_own_checks, required_checks
from .docs import find_unit_dir
from .envelope import check_result_envelope, write_envelope
from .frontmatter import read as read_frontmatter
from .util import dump_yaml, load_yaml, now_iso

ATTEMPTS_SCHEMA = "romeo/attempts@0.1.0"
ATTEMPTS_FILE = "attempts.yaml"
#: 연속 실패가 이 값에 이르면 다음 기동을 거부한다(`AGENTS.core.md` §10 의 상한).
CONSECUTIVE_FAILURE_LIMIT = 2
RESULTS = ("started", "pass", "fail")
#: 기록만 하는 분류다. 차단 판정에 쓰지 않는다 — 자동 분류를 신뢰하지 않는다.
FAILURE_CLASSES = ("outputs", "harness", "goal")

STAGES = [
    ("contract", "작업 계약 생성"),
    ("delegate", "위임 명령 출력"),
    ("collect", "결과 회수·앵커 검증"),
    ("evidence", "evidence 기록"),
    ("observe", "관측 모으기"),
]


# --------------------------------------------------------------------------- attempts

def attempts_path(project_root, unit_id):
    return find_unit_dir(Path(project_root), unit_id) / ATTEMPTS_FILE


def load_attempts(project_root, unit_id):
    path = attempts_path(project_root, unit_id)
    if not path.is_file():
        return {"schema": ATTEMPTS_SCHEMA, "unit_id": unit_id, "attempts": [], "reviews": []}
    data = load_yaml(path) or {}
    data.setdefault("schema", ATTEMPTS_SCHEMA)
    data.setdefault("unit_id", unit_id)
    data.setdefault("attempts", [])
    data.setdefault("reviews", [])
    return data


def save_attempts(project_root, unit_id, data):
    path = attempts_path(project_root, unit_id)
    path.write_text(dump_yaml(data), encoding="utf-8")
    return path


def _reviewed_through(data):
    """마지막 재검토가 몇 회차까지를 덮는가. 그 앞의 실패는 이미 사람이 한 번 본 것이다."""
    ns = [int(r.get("after_attempt") or 0) for r in (data.get("reviews") or [])]
    return max(ns) if ns else 0


def consecutive_failures(data):
    """마지막 재검토 **이후**의 연속 실패 수.

    성공(`pass`)이 나오면 거기서 끊긴다 — 카운터가 0 으로 돌아간다. 아직 판정이 없는 시도(`started`)는 세지 않는다.
    `base_sha` 는 보지 않는다: 새 base 로 다시 겨눈 시도도 **같은 완료 정의**를 겨눈 시도이므로 리셋 사유가 아니다."""
    floor = _reviewed_through(data)
    count = 0
    for att in reversed(data.get("attempts") or []):
        if int(att.get("n") or 0) <= floor:
            break
        result = att.get("result")
        if result == "fail":
            count += 1
        elif result == "pass":
            break
    return count


def gate(data):
    """기동해도 되는가. (허용 여부, 연속 실패 수, 사람이 읽을 이유)"""
    n = consecutive_failures(data)
    if n < CONSECUTIVE_FAILURE_LIMIT:
        return True, n, ""
    return False, n, (
        f"같은 작업 단위에서 관통이 연속 {n}회 실패했다 — {n + 1}회차를 돌기 전에 완료 정의가 달성 가능한지 "
        f"사람이 재검토한다(AGENTS.core §10). 재검토 결론을 --after-review \"<결론>\" 으로 주면 "
        f"그 결론을 기록하고 진행한다. 실패 원인 분류는 기록만 하고 이 판정에 쓰지 않는다.")


def add_review(data, conclusion, by=None):
    data.setdefault("reviews", []).append({
        "after_attempt": len(data.get("attempts") or []),
        "conclusion": str(conclusion),
        "by": by,
        "at": now_iso(),
    })
    return data


def start_attempt(data, run, base_sha):
    n = len(data.get("attempts") or []) + 1
    entry = {"n": n, "run": run, "base_sha": base_sha, "started_at": now_iso(),
             "result": "started", "failure_class": None, "note": None, "settled_at": None}
    data.setdefault("attempts", []).append(entry)
    return entry


def settle_attempt(data, run, result, failure_class=None, note=None):
    if result not in ("pass", "fail"):
        raise ValueError(f"판정을 모른다: {result!r} (허용: pass · fail)")
    if failure_class is not None and failure_class not in FAILURE_CLASSES:
        raise ValueError(f"실패 분류를 모른다: {failure_class!r} (허용: {' · '.join(FAILURE_CLASSES)})")
    for att in reversed(data.get("attempts") or []):
        if att.get("run") == run:
            att["result"] = result
            att["failure_class"] = failure_class
            att["note"] = note
            att["settled_at"] = now_iso()
            return att
    raise ValueError(f"run {run} 으로 시작한 시도가 attempts.yaml 에 없다 — 기동 기록 없이 판정만 남기지 않는다")


# --------------------------------------------------------------------------- 위임 명령

def delegation_commands(unit_id, run, base_sha, workspace):
    """RUNBOOK §3.2~§3.7 의 명령 문자열. 여기서 실행하지 않는다 — dry-run 은 인쇄까지다.

    문자열을 만드는 자리를 한 곳에 두는 것이 목적이다. 손으로 조립하면 회차마다 달라진다."""
    udir = f"docs/work/{unit_id}"
    task = f"{udir}/task/{run}"
    return [
        ("run-create", f"orca orchestration run-create --objective {shlex.quote(unit_id + ' 관통')} --json"),
        ("task-create:implementer",
         f"orca orchestration task-create --run {run} --task-title {shlex.quote(unit_id + ' implementer')} "
         f"--spec {shlex.quote(f'계약 {task}-implementer.json · 결과 {udir}/result/{run}-implementer.json · 증거 {udir}/evidence/{run}.yaml · 절차 core/workflows/implement/SKILL.md')} --json"),
        ("task-create:reviewer",
         f"orca orchestration task-create --run {run} --task-title {shlex.quote(unit_id + ' reviewer')} "
         f"--deps '[\"<implementer-task-id>\"]' "
         f"--spec {shlex.quote(f'계약 {task}-reviewer.json · 판정 {udir}/review/{run}-reviewer.json · 절차 core/workflows/review/SKILL.md · 읽기 전용')} --json"),
        ("worktree", f"orca worktree create --base-branch <승인 커밋이 tip 인 브랜치>  # workspace={workspace} · base_sha={base_sha[:12]}"),
        ("worker-start", f"orca orchestration worker-start --run {run} --task <implementer-task-id> --json"),
        ("identifiers",
         f"orca orchestration send --to dispatch:<dispatch-id> --type status --subject '위임 식별자' "
         f"--body '<task-id> · <dispatch-id> — 받기 전에는 evidence 기록을 시작하지 않는다'"),
        ("reviewer-spawn", "codex exec -s read-only -C <구현자 워크트리 절대경로> "
                           "--output-schema core/schemas/result-envelope.json -o <워크트리 밖 출력 파일>"),
    ]


# --------------------------------------------------------------------------- 5단계

def _stage(name, state, detail, commands=None):
    return {"stage": name, "label": dict(STAGES)[name], "state": state, "detail": detail,
            "commands": commands or []}


def _spec_body(project_root, unit_id):
    _fm, body = read_frontmatter(find_unit_dir(Path(project_root), unit_id) / "spec.md")
    return body or ""


def _stage_contract(project_root, unit_id, run, base_sha, harness_root):
    """① 작업 계약 생성. 두 역할분을 만든다 — 같은 입력이면 바이트까지 같은 계약이다."""
    built = []
    for role in ("implementer", "reviewer"):
        res = write_envelope(unit_id, role, project_root=project_root, harness_root=harness_root,
                             base_sha=base_sha, run_name=run)
        built.append({"role": role, "path": res["path"], "sha256": res["sha256"],
                      "base_sha": res["envelope"]["base_sha"]})
    detail = " · ".join(f"{b['role']} {Path(b['path']).name} sha256 {b['sha256'][:12]}" for b in built)
    stage = _stage("contract", "done", detail)
    stage["built"] = built

    # 페이로드 단위에 하네스 자신의 검사가 들어 있으면 알린다(core/templates/tech-spec.md 의 검증 계획 규칙).
    # 하네스 저장소 자신의 단위에서는 그 검사가 정당하므로 경고하지 않는다.
    if Path(project_root).resolve() != Path(harness_root or HARNESS_ROOT).resolve():
        own = harness_own_checks(required_checks(_spec_body(project_root, unit_id)))
        if own:
            stage["warnings"] = [
                f"페이로드 단위의 required_checks 에 하네스 자신의 검사가 있다: "
                + " · ".join(f"{c['id']}({c['command']})" for c in own)
                + " — 하네스가 깨진 동안 이 단위가 닫히지 못한다(core/templates/tech-spec.md)"]
    return stage


PLACEHOLDER_RE = re.compile(r"<[^<>]+>")


def _stage_delegate(unit_id, run, base_sha, workspace, spawn, cwd=None):
    """② 위임 명령 출력. 기본은 인쇄까지다 — 기동은 비용이 드는 실행이라 `--spawn` 을 명시해야 한다(K-66).

    `--spawn` 은 **자리표시자가 없는 명령까지만** 실행하고, 첫 자리표시자에서 멈춰 무엇이 필요한지 말한다.
    이어붙이려면 각 명령의 반환 JSON 에서 어느 필드가 그 값인지 알아야 하는데 그 필드 이름은 아직 실측되지 않았다
    (RUNBOOK §11). 모르는 것을 아는 것처럼 파싱하지 않는다(K-54) — 값이 정해지면 여기서 이어진다."""
    cmds = delegation_commands(unit_id, run, base_sha, workspace)
    if not spawn:
        return _stage("delegate", "dry-run", f"{len(cmds)}개 명령을 인쇄했다 — 실행하지 않았다(--spawn 없음)",
                      commands=cmds)
    ran, blocked = [], None
    for name, cmd in cmds:
        hole = PLACEHOLDER_RE.search(cmd)
        if hole:
            blocked = (name, hole.group(0))
            break
        proc = subprocess.run(cmd, shell=True, cwd=str(cwd) if cwd else None,
                              capture_output=True, text=True)
        ran.append({"name": name, "command": cmd, "exit_code": proc.returncode,
                    "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-2000:]})
        if proc.returncode != 0:
            blocked = (name, f"exit {proc.returncode}")
            break
    if blocked:
        state = "부분" if ran else "대기"
        detail = (f"{len(ran)}개 실행 뒤 {blocked[0]} 에서 멈췄다 — {blocked[1]} 를 사람이 채운다. "
                  f"이 경로는 아직 실측되지 않았다(RUNBOOK §11)")
    else:
        state = "spawn"
        detail = f"{len(ran)}개 실행 · 이 경로는 아직 실측되지 않았다(RUNBOOK §11)"
    stage = _stage("delegate", state, detail, commands=cmds)
    stage["ran"] = ran
    return stage


def _stage_collect(project_root, unit_id, run, harness_root):
    """③ 결과 회수·앵커 검증. 봉투가 그 자리에 있을 때만 `envelope check` 를 부른다."""
    udir = find_unit_dir(Path(project_root), unit_id)
    targets = [("implementer", udir / "result" / f"{run}-implementer.json"),
               ("reviewer", udir / "review" / f"{run}-reviewer.json")]
    checked, missing = [], []
    for role, path in targets:
        if not path.is_file():
            missing.append(f"{role}:{path.relative_to(Path(project_root).resolve())}")
            continue
        res = check_result_envelope(path, unit_id, role=role, project_root=project_root,
                                    harness_root=harness_root)
        checked.append({"role": role, "path": str(path), "verdict": res["verdict"],
                        "checks": res["checks"]})
    if missing:
        state = "대기" if not checked else "부분"
        detail = "아직 없는 봉투: " + " · ".join(missing)
    else:
        state = "done" if all(c["verdict"] == "PASS" for c in checked) else "fail"
        detail = " · ".join(f"{c['role']} {c['verdict']}" for c in checked)
    stage = _stage("collect", state, detail)
    stage["checked"] = checked
    stage["missing"] = missing
    return stage


def _stage_evidence(project_root, unit_id, run):
    """④ evidence 기록. 여기서 검사를 대신 돌리지 않는다 — 증거는 워커가 자기 산출물 위에서 만든다(K-51).

    이 단계가 하는 것은 그 run 의 증거가 실재하고 검증 계획을 **전부** 담았는지 보는 것이다."""
    udir = find_unit_dir(Path(project_root), unit_id)
    path = udir / "evidence" / f"{run}.yaml"
    plan = required_checks(_spec_body(project_root, unit_id))
    want = [str((rc or {}).get("id")) for rc in plan]
    record_cmd = (f"bin/romeo evidence checks --unit {unit_id} --run {run} "
                  f"--task-id <task-id> --dispatch-id <dispatch-id>")
    if not path.is_file():
        return _stage("evidence", "대기",
                      f"{path.relative_to(Path(project_root).resolve())} 가 아직 없다 — 워커가 만든다",
                      commands=[("evidence-checks", record_cmd)])
    rec = load_yaml(path) or {}
    got = [str((c or {}).get("id")) for c in (rec.get("commands") or [])]
    labels = {str((c or {}).get("label") or "") for c in (rec.get("commands") or [])}
    missing = [cid for cid in want if cid not in got and cid not in labels]
    exits = {str((c or {}).get("id")): (c or {}).get("exit_code") for c in (rec.get("commands") or [])}
    failed = [cid for cid, code in exits.items() if code not in (0, None)]
    state = "done" if not missing and not failed else ("부분" if not failed else "fail")
    detail = (f"명령 {len(got)}건 · 검증 계획 {len(want)}건"
              + (f" · 기록 없음 {missing}" if missing else "")
              + (f" · 실패 {failed}" if failed else ""))
    stage = _stage("evidence", state, detail, commands=[] if state == "done" else [("evidence-checks", record_cmd)])
    stage["evidence_ref"] = str(path.relative_to(Path(project_root).resolve()))
    return stage


def _stage_observe(project_root, unit_id, run, harness_root):
    """⑤ 관측 모으기. 케이스 파일을 여기서 쓰지 않는다 — 무엇을 어디에 채울지 값을 계산해 인쇄한다.

    쓰지 않는 이유는 RUNBOOK §6.4 와 같다: 게이트가 비교하는 값을 이 명령이 만들어 버리면 게이트가 아무것도 지키지 않는다(D-b)."""
    harness_root = Path(harness_root or HARNESS_ROOT)
    cases = sorted((harness_root / "fixtures/parity").glob("*-observed.yaml"))
    udir = f"docs/work/{unit_id}"
    values = {
        "unit_id": unit_id,
        "status": "executed",
        "source.kind": "observed",
        "source.ref": f"{udir}/evidence/{run}.yaml",
        "results.implementer": f"{udir}/result/{run}-implementer.json",
        "results.reviewer": f"{udir}/review/{run}-reviewer.json",
    }
    state = "dry-run" if cases else "대기"
    detail = ("채울 관측 케이스: " + " · ".join(c.name for c in cases)) if cases \
        else "fixtures/parity/ 에 관측 케이스 자리표가 없다"
    stage = _stage("observe", state, detail,
                   commands=[("parity", f"{harness_root}/bin/romeo fixtures parity --report")])
    stage["values"] = values
    stage["cases"] = [str(c.relative_to(harness_root)) for c in cases]
    return stage


# --------------------------------------------------------------------------- 진입점

def run_unit(unit_id, project_root=".", harness_root=None, run=None, base_sha=None,
             spawn=False, after_review=None, by=None, record=True):
    """관통 1회를 5단계로 수행한다. 중단 기준에 걸리면 아무 단계도 돌지 않고 `blocked` 로 끝난다.

    `record=False` 는 attempts.yaml 을 건드리지 않는다 — 같은 회차를 다시 인쇄해 볼 때 쓴다."""
    project_root = Path(project_root).resolve()
    harness_root = Path(harness_root or HARNESS_ROOT)
    if not run:
        raise ValueError("--run 이 필요하다 — 계약·증거·결과 봉투가 그 값 하나로 묶인다(RUNBOOK §3.3)")

    data = load_attempts(project_root, unit_id)
    allowed, failures, why = gate(data)
    released = False
    if not allowed:
        if not after_review:
            return {"unit_id": unit_id, "run": run, "verdict": "BLOCKED_REPEAT",
                    "consecutive_failures": failures, "blocked_reason": why,
                    "attempts_path": str(attempts_path(project_root, unit_id)), "stages": []}
        add_review(data, after_review, by=by)
        released = True

    # 계약을 만들기 전에 base_sha 를 확정한다 — 시도 기록에 남는 값과 계약의 값이 같아야 한다.
    stages = []
    contract = _stage_contract(project_root, unit_id, run, base_sha, harness_root)
    resolved_base = contract["built"][0]["base_sha"]
    workspace = "worktree"
    if record:
        start_attempt(data, run, resolved_base)
        save_attempts(project_root, unit_id, data)

    stages.append(contract)
    stages.append(_stage_delegate(unit_id, run, resolved_base, workspace, spawn, cwd=project_root))
    stages.append(_stage_collect(project_root, unit_id, run, harness_root))
    stages.append(_stage_evidence(project_root, unit_id, run))
    stages.append(_stage_observe(project_root, unit_id, run, harness_root))

    return {"unit_id": unit_id, "run": run, "base_sha": resolved_base,
            "verdict": "OK", "spawn": bool(spawn), "released_by_review": released,
            "consecutive_failures": failures,
            "attempts_path": str(attempts_path(project_root, unit_id)), "stages": stages}


def record_result(unit_id, run, result, project_root=".", failure_class=None, note=None):
    """관통 1회의 판정을 attempts.yaml 에 남긴다. 이것이 다음 회차의 중단 기준 입력이다."""
    project_root = Path(project_root).resolve()
    data = load_attempts(project_root, unit_id)
    entry = settle_attempt(data, run, result, failure_class=failure_class, note=note)
    path = save_attempts(project_root, unit_id, data)
    return {"unit_id": unit_id, "run": run, "attempt": entry,
            "consecutive_failures": consecutive_failures(data), "attempts_path": str(path)}


def format_run(res):
    lines = [f"romeo run-unit {res['unit_id']} · run {res['run']} → {res['verdict']}"]
    if res["verdict"] == "BLOCKED_REPEAT":
        lines.append(f"  연속 실패 {res['consecutive_failures']}회 — 기동하지 않았다")
        lines.append(f"  {res['blocked_reason']}")
        lines.append(f"  기록: {res['attempts_path']}")
        return "\n".join(lines)
    lines.append(f"  base_sha {res['base_sha'][:12]} · 연속 실패 {res['consecutive_failures']}회"
                 + (" · 재검토로 해제됨" if res.get("released_by_review") else "")
                 + ("" if res.get("spawn") else " · dry-run (--spawn 없음)"))
    for i, st in enumerate(res["stages"], 1):
        lines.append(f"  [{i}/{len(STAGES)}] {st['label']} — {st['state']}: {st['detail']}")
        for w in st.get("warnings") or []:
            lines.append(f"        WARN {w}")
        for name, cmd in st.get("commands") or []:
            lines.append(f"        {name}: {cmd}")
        for k, v in (st.get("values") or {}).items():
            lines.append(f"        {k}: {v}")
    lines.append(f"  기록: {res['attempts_path']}")
    return "\n".join(lines)


def format_record(res):
    att = res["attempt"]
    return (f"romeo run-unit record {res['unit_id']} · run {res['run']} → {att['result']}"
            f" (회차 {att['n']} · 분류 {att['failure_class'] or '없음'})\n"
            f"  연속 실패 {res['consecutive_failures']}회"
            + (f" — 다음 기동은 --after-review 없이는 거부된다(AGENTS.core §10)"
               if res["consecutive_failures"] >= CONSECUTIVE_FAILURE_LIMIT else "")
            + f"\n  기록: {res['attempts_path']}")
