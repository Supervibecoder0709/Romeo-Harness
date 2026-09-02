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

import yaml

from . import HARNESS_ROOT
from .close import harness_own_checks, required_checks
from .docs import find_unit_dir
from .envelope import _committed_bytes, _rev_parse, check_result_envelope, write_envelope
from .frontmatter import read as read_frontmatter
from .util import dump_yaml, load_yaml, now_iso, rel

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


def _settled_through(data):
    """판정이 난 마지막 시도의 회차 번호.

    진행 중(`started`)인 시도는 세지 않는다 — 아직 실패하지 않은 시도를 재검토가 덮었는지 묻는 것은 뜻이 없고,
    그렇게 물으면 재검토로 막 해제한 그 회차가 **자기 계약을 다시 만들지 못한다**(계약 생성이 게이트를 다시 지난다)."""
    ns = [int(a.get("n") or 0) for a in (data.get("attempts") or [])
          if a.get("result") in ("pass", "fail")]
    return max(ns) if ns else 0


def consecutive_failures(data):
    """마지막 성공(`pass`) **이후**의 연속 실패 수.

    성공(`pass`)이 나오면 거기서 끊긴다 — 카운터가 0 으로 돌아간다. 아직 판정이 없는 시도(`started`)는 세지 않는다.
    `base_sha` 는 보지 않는다: 새 base 로 다시 겨눈 시도도 **같은 완료 정의**를 겨눈 시도이므로 리셋 사유가 아니다.

    **재검토는 이 수를 줄이지 않는다.** 재검토는 그 시점까지를 한 번 통과시키는 것이지 실패를 없애는 것이 아니다 —
    줄이면 실패 1·2 → 재검토 → 실패 3 이 다시 1 이 되어 4회차가 재검토 없이 돈다(2026-08-31 실측).
    카운터를 되돌리는 것은 성공뿐이다(AGENTS.core §10). 해제 판정은 `gate()` 가 따로 한다."""
    count = 0
    for att in reversed(data.get("attempts") or []):
        result = att.get("result")
        if result == "fail":
            count += 1
        elif result == "pass":
            break
    return count


def gate(data):
    """기동해도 되는가. (허용 여부, 연속 실패 수, 사람이 읽을 이유)

    한도에 이르러도 **마지막 재검토가 판정 난 마지막 시도를 덮으면** 통과시킨다. 그 뒤에 실패가 하나 더 쌓이면
    다시 막힌다 — 한 번의 재검토는 그 시점까지의 면제이지 영구 면제가 아니다."""
    n = consecutive_failures(data)
    if n < CONSECUTIVE_FAILURE_LIMIT:
        return True, n, ""
    if _reviewed_through(data) >= _settled_through(data):
        return True, n, ""
    unit = data.get("unit_id") or "<단위>"
    return False, n, (
        f"같은 작업 단위에서 관통이 연속 {n}회 실패했다 — {n + 1}회차를 돌기 전에 완료 정의가 달성 가능한지 "
        f"사람이 재검토한다(AGENTS.core §10). 재검토 결론만 남기려면 "
        f"bin/romeo run-unit review --unit {unit} --after-review \"<결론>\" --by <사람> — "
        f"기록하고 끝난다(시도를 시작하지 않는다). 기록과 기동을 한 번에 하려면 "
        f"bin/romeo run-unit --unit {unit} --run <run> --base-sha <승인 커밋> "
        f"--after-review \"<결론>\" --by <사람>. 실패 원인 분류는 기록만 하고 이 판정에 쓰지 않는다.")


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

def delegation_commands(unit_id, run, base_sha, workspace, harness_root, reviewer_sha256):
    """RUNBOOK §3.2~§3.7 의 명령 문자열. 여기서 실행하지 않는다 — dry-run 은 인쇄까지다.

    문자열을 만드는 자리를 한 곳에 두는 것이 목적이다. 손으로 조립하면 회차마다 달라진다.
    요구하는 자리(RUNBOOK)와 만드는 자리(여기)가 어긋났던 곳을 맞췄다(Q-40·Q-41 · AGENTS.core §11):

    - `--run` 은 §3.2 에서 **이미 만든** Orca Run id 다. 첫 명령은 그 Run 이 있는지 보는 `run-show --id` 이고 `run-create` 는 없다 —
      종전 인쇄는 새 Run 을 만들고 그 뒤 명령의 `--run` 자리에 romeo run 이름을 박아, 그대로 실행하면 없는 Run 을 가리켰다.
    - 구현자 `task-create --spec` 은 손으로 조립하지 않는다. 정본 절차 파일(`adapters/orca/prompts/implementer-brief.md`)의
      자리표시자 `<id>`·`<run-id>`·`<base-sha>` 를 채워 `.harness/runs/<id>/<run>/implementer-spec.md` 에 두고 `$(cat …)` 로 읽는다.
      §3.4 가 요구한 항목 5개(결과 계약 형식 · 체크박스는 구현자가 채운다 · 계약이 없으면 스스로 만든다 · `--task-id`·`--dispatch-id` ·
      dispatch-id 는 기동 뒤 전달)는 그 정본에 있다 — 여기 다시 적으면 두 벌이 된다.
    - 검토자 `task-create --spec` 은 경로와 절차만이다. **해시를 넣지 않는다** — `--spec` 에 복사된 해시는 재승인 뒤 갱신되지 않아
      검토자에게 낡은 값이 도달했다(§3.4.1). 해시는 §3.7 의 `fill_brief.py --task-sha256` 이 그 자리에서 계산해 절차 파일에 적는다 —
      그 명령을 `reviewer-brief` 로 함께 인쇄하고, 1단계가 만든 검토자 계약의 sha256 을 그대로 싣는다.
      `<W>` 는 §3.5 가 만드는 구현자 워크트리의 절대 경로다 — 이 시점에는 없으므로 자리표시자로 남는다."""
    harness_root = Path(harness_root or HARNESS_ROOT)
    udir = f"docs/work/{unit_id}"
    task = f"{udir}/task/{run}"
    runs_dir = f".harness/runs/{unit_id}/{run}"
    impl_spec = f"{runs_dir}/implementer-spec.md"
    brief = shlex.quote(str(harness_root / "adapters/orca/prompts/implementer-brief.md"))
    fill_brief = shlex.quote(str(harness_root / "adapters/orca/prompts/fill_brief.py"))
    return [
        ("run-show", f"orca orchestration run-show --id {run} --json"
                     f"  # --run 은 §3.2 에서 이미 만든 Run id 다 — 없으면 여기서 exit≠0 으로 멈춘다"),
        ("implementer-spec",
         f"mkdir -p {runs_dir} && awk 'f;/^---$/{{f=1}}' {brief} "
         f"| sed \"s/<id>/{unit_id}/g; s/<run-id>/{run}/g; s/<base-sha>/{base_sha}/g\" > {impl_spec}"),
        ("task-create:implementer",
         f"orca orchestration task-create --run {run} --task-title {shlex.quote(unit_id + ' implementer')} "
         f"--spec \"$(cat {impl_spec})\" --json"),
        ("task-create:reviewer",
         f"orca orchestration task-create --run {run} --task-title {shlex.quote(unit_id + ' reviewer')} "
         f"--deps '[\"<implementer-task-id>\"]' "
         f"--spec {shlex.quote(f'계약 {task}-reviewer.json · 판정 {udir}/review/{run}-reviewer.json · 절차 core/workflows/review/SKILL.md · 절차 파일은 §3.7 이 채워 argv 로 넘긴다 — 해시는 거기서 계산한다 · 읽기 전용')} --json"),
        ("worktree", f"orca worktree create --base-branch <승인 커밋이 tip 인 브랜치>  # workspace={workspace} · base_sha={base_sha[:12]}"),
        ("worker-start", f"orca orchestration worker-start --run {run} --task <implementer-task-id> --json"),
        ("identifiers",
         f"orca orchestration send --to dispatch:<dispatch-id> --type status --subject '위임 식별자' "
         f"--body '<task-id> · <dispatch-id> — 받기 전에는 evidence 기록을 시작하지 않는다'"),
        ("reviewer-brief",
         f"python3 {fill_brief} --unit {unit_id} --run {run} --base-sha {base_sha} --task-sha256 {reviewer_sha256} "
         f"--runtime codex --mode base --out <W>/{runs_dir}/reviewer-brief.md"),
        ("reviewer-spawn", "codex exec -s read-only -C <구현자 워크트리 절대경로> "
                           "--output-schema core/schemas/result-envelope.json -o <워크트리 밖 출력 파일>"),
    ]


# --------------------------------------------------------------------------- 확인 4 — 판정·재검토 대조

def _attempts_at(project_root, unit_id, ref):
    """`<ref>` 커밋의 attempts.yaml. 파일이 없으면 빈 기록이고, 커밋 자체가 없으면 ValueError 다 —
    없는 커밋을 빈 기록으로 접으면 오타 난 SHA 가 「일치」 로 읽힌다."""
    sha = _rev_parse(project_root, ref)
    raw = _committed_bytes(project_root, sha, rel(attempts_path(project_root, unit_id), project_root))
    data = (yaml.safe_load(raw.decode("utf-8")) or {}) if raw is not None else {}
    return {"attempts": data.get("attempts") or [], "reviews": data.get("reviews") or []}, sha


def _verdicts(data):
    """판정 난 시도(pass·fail)의 식별자 — (n · run · result). `started` 는 없다."""
    return {(str(a.get("n")), str(a.get("run")), str(a.get("result")))
            for a in (data.get("attempts") or []) if (a or {}).get("result") in ("pass", "fail")}


def _reviews(data):
    """재검토의 식별자 — (after_attempt · conclusion · by)."""
    return {(str(r.get("after_attempt")), str(r.get("conclusion")), str(r.get("by")))
            for r in (data.get("reviews") or []) if r}


def compare_attempts(project_root, unit_id, base_sha):
    """RUNBOOK §3.1 확인 4 — 커밋과 작업 트리의 `attempts.yaml` 을 **판정(pass·fail)과 재검토(reviews)로만** 대조한다(Q-39).

    회차 기록이 계약 생성으로 옮겨진 뒤(Q-27) 이 파일은 언제나 승인 커밋 **뒤에** 생기므로, 파일 전체를 `diff` 하던 옛 확인은
    첫 관통에서 항상 실패했고 지시된 해법(승인 커밋에 담고 base-sha 를 다시 잡는다)은 순환이었다 — 새 base 로 계약을 다시 만들면
    회차가 또 추가돼 다시 어긋났다. 워커가 보지 못하면 실제로 판정이 바뀌는 것은 **판정과 재검토**뿐이다 — 중단 게이트(`gate`)는
    그 둘만 읽는다. 그래서 `started` 는 대조하지 않는다.

    아무것도 쓰지 않는다. → {"unit_id", "base_sha", "diffs": [차이 줄…], "verdicts": 작업 트리의 판정 수, "reviews": 재검토 수}"""
    project_root = Path(project_root).resolve()
    committed, sha = _attempts_at(project_root, unit_id, base_sha)
    working = load_attempts(project_root, unit_id)
    cv, wv = _verdicts(committed), _verdicts(working)
    cr, wr = _reviews(committed), _reviews(working)
    diffs = []
    for n, run, result in sorted(wv - cv):
        diffs.append(f"판정이 작업 트리에만 있다(커밋 밖): 회차 {n} · run {run} · {result}")
    for n, run, result in sorted(cv - wv):
        diffs.append(f"판정이 커밋에만 있다(작업 트리에서 바뀌었거나 지워졌다): 회차 {n} · run {run} · {result}")
    for after, conclusion, by in sorted(wr - cr):
        diffs.append(f"재검토가 작업 트리에만 있다(커밋 밖): {after}회차까지 · {by} · 「{conclusion}」")
    for after, conclusion, by in sorted(cr - wr):
        diffs.append(f"재검토가 커밋에만 있다(작업 트리에서 바뀌었거나 지워졌다): {after}회차까지 · {by} · 「{conclusion}」")
    return {"unit_id": unit_id, "base_sha": sha, "diffs": diffs, "verdicts": len(wv), "reviews": len(wr),
            "attempts_path": str(attempts_path(project_root, unit_id))}


def attempts_drift(project_root, unit_id, base_sha):
    """`compare_attempts(...)["diffs"]` — 비어 있으면 일치다."""
    return compare_attempts(project_root, unit_id, base_sha)["diffs"]


def format_check(res):
    head = f"romeo run-unit check {res['unit_id']} · base {res['base_sha'][:12]}"
    if not res["diffs"]:
        return head + f" → 일치 (판정 {res['verdicts']}건 · 재검토 {res['reviews']}건 · started 는 대조하지 않는다)"
    lines = [head + f" → 차이 {len(res['diffs'])}건 — 자식 워크트리의 워커는 커밋된 것만 본다(D-a)"]
    lines += [f"  {d}" for d in res["diffs"]]
    lines.append("  고치는 방법: 판정·재검토가 커밋 밖이면 그것을 커밋한다 — started 는 커밋하지 않아도 된다. "
                 "커밋 뒤 <base-sha> 를 그 커밋으로 다시 잡는다(RUNBOOK §3.1 확인 4)")
    lines.append(f"  기록: {res['attempts_path']}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- 5단계

def _stage(name, state, detail, commands=None):
    return {"stage": name, "label": dict(STAGES)[name], "state": state, "detail": detail,
            "commands": commands or []}


def _spec_body(project_root, unit_id):
    _fm, body = read_frontmatter(find_unit_dir(Path(project_root), unit_id) / "spec.md")
    return body or ""


def _stage_contract(project_root, unit_id, run, base_sha, harness_root, record=True):
    """① 작업 계약 생성. 두 역할분을 만든다 — 같은 입력이면 바이트까지 같은 계약이다.

    **회차 기록도 여기서 난다**(`envelope.record_start`). 이 함수가 부르는 `write_envelope` 가
    그것을 소유하므로 `run_unit` 은 따로 시작하지 않는다 — 상태의 주인은 하나다(K-63).
    두 역할분을 만들어도 회차는 하나다(같은 run 이면 기존 기록을 그대로 쓴다)."""
    built = []
    for role in ("implementer", "reviewer"):
        res = write_envelope(unit_id, role, project_root=project_root, harness_root=harness_root,
                             base_sha=base_sha, run_name=run, record_attempt=record)
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


def _stage_delegate(unit_id, run, base_sha, workspace, spawn, harness_root, reviewer_sha256, cwd=None):
    """② 위임 명령 출력. 기본은 인쇄까지다 — 기동은 비용이 드는 실행이라 `--spawn` 을 명시해야 한다(K-66).

    `--spawn` 은 **자리표시자가 없는 명령까지만** 실행하고, 첫 자리표시자에서 멈춰 무엇이 필요한지 말한다.
    이어붙이려면 각 명령의 반환 JSON 에서 어느 필드가 그 값인지 알아야 하는데 그 필드 이름은 아직 실측되지 않았다
    (RUNBOOK §11). 모르는 것을 아는 것처럼 파싱하지 않는다(K-54) — 값이 정해지면 여기서 이어진다."""
    cmds = delegation_commands(unit_id, run, base_sha, workspace, harness_root, reviewer_sha256)
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
        # 재검토를 **먼저** 디스크에 남긴다. 아래 1단계의 계약 생성이 같은 게이트를 다시 지나므로
        # (`envelope.write_envelope`), 메모리에만 있는 해제는 그 자리에서 보이지 않는다.
        save_attempts(project_root, unit_id, data)
        released = True

    # 계약을 만들기 전에 base_sha 를 확정한다 — 시도 기록에 남는 값과 계약의 값이 같아야 한다.
    stages = []
    contract = _stage_contract(project_root, unit_id, run, base_sha, harness_root, record=record)
    resolved_base = contract["built"][0]["base_sha"]
    workspace = "worktree"
    # 회차는 계약 생성이 이미 남겼다(K-63) — 여기서 다시 쓰면 그 기록을 낡은 사본으로 덮는다.
    data = load_attempts(project_root, unit_id)

    # 검토자 계약의 sha256 — §3.7 의 fill_brief 명령이 이 값을 --task-sha256 으로 싣는다. 손으로 적지 않는다.
    reviewer_sha256 = next(b["sha256"] for b in contract["built"] if b["role"] == "reviewer")
    stages.append(contract)
    stages.append(_stage_delegate(unit_id, run, resolved_base, workspace, spawn, harness_root, reviewer_sha256,
                                  cwd=project_root))
    stages.append(_stage_collect(project_root, unit_id, run, harness_root))
    stages.append(_stage_evidence(project_root, unit_id, run))
    stages.append(_stage_observe(project_root, unit_id, run, harness_root))

    return {"unit_id": unit_id, "run": run, "base_sha": resolved_base,
            "verdict": "OK", "spawn": bool(spawn), "released_by_review": released,
            "consecutive_failures": failures,
            "attempts_path": str(attempts_path(project_root, unit_id)), "stages": stages}


def record_review(unit_id, conclusion, project_root=".", by=None):
    """재검토 결론을 **기록만** 한다 — 시도를 시작하지 않는다(Q-25).

    반복 중단을 푸는 창구가 `run-unit start --after-review` 하나뿐이면, 재검토를 남기는 일이 언제나
    attempt 하나를 함께 만든다. 그런데 그 재검토 기록은 **커밋돼야** 워크트리 안의 계약 생성이 본다(D-a).
    커밋하면 HEAD 가 밀리고, 워크트리는 브랜치 tip 을 체크아웃하므로 계약의 `base_sha` 와 워크트리 head 가
    어긋나 계약을 새 SHA 로 다시 만들어야 한다 — 그때 attempt 가 또 하나 생긴다. 2026-08-31 실측으로
    `started` 로 남은 유령이 세 개였다. 이 경로는 그 둘을 나눈다.

    **브레이크를 우회하지 않는다.** 해제 판정은 그대로 `gate()` 가 하고, 연속 실패 카운터를 되돌리는 것은
    성공뿐이다(AGENTS.core §10). 여기서 바뀌는 것은 재검토를 남기는 **방법**이지 남긴 뒤의 판정이 아니다."""
    project_root = Path(project_root).resolve()
    data = load_attempts(project_root, unit_id)
    before = len(data.get("attempts") or [])
    add_review(data, conclusion, by=by)
    path = save_attempts(project_root, unit_id, data)
    after = len(data.get("attempts") or [])
    if after != before:
        raise AssertionError(f"기록 전용 경로가 시도를 늘렸다: {before} → {after}")
    allowed, failures, _why = gate(data)
    return {"unit_id": unit_id, "review": data["reviews"][-1], "attempts": after,
            "consecutive_failures": failures, "released": allowed,
            "attempts_path": str(path)}


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


def format_review(res):
    rv = res["review"]
    return (f"romeo run-unit review {res['unit_id']} → 기록됨 (시도 {rv['after_attempt']}회차까지 · {rv['by'] or '작성자 미기재'})\n"
            f"  결론: {rv['conclusion']}\n"
            f"  시도 항목 {res['attempts']}건 — 늘지 않았다(기록 전용 경로)\n"
            f"  연속 실패 {res['consecutive_failures']}회 · 다음 기동 "
            + ("허용" if res["released"] else "여전히 거부") + "\n"
            f"  기록: {res['attempts_path']}")


def format_record(res):
    att = res["attempt"]
    return (f"romeo run-unit record {res['unit_id']} · run {res['run']} → {att['result']}"
            f" (회차 {att['n']} · 분류 {att['failure_class'] or '없음'})\n"
            f"  연속 실패 {res['consecutive_failures']}회"
            + (f" — 다음 기동은 --after-review 없이는 거부된다(AGENTS.core §10)"
               if res["consecutive_failures"] >= CONSECUTIVE_FAILURE_LIMIT else "")
            + f"\n  기록: {res['attempts_path']}")
