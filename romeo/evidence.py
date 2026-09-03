"""evidence 기록: 명령을 실제로 실행하고 HEAD SHA·dirty_tree_hash·변경 파일·산출물 해시와 함께 남긴다(C-E1).
원시 로그는 .harness/runs/ (git 제외, K-24), evidence yaml 에는 경로와 해시만. 손으로 쓰지 않는다.

**기록은 위조할 수 있다.** 이 기계를 쓰는 사람은 evidence yaml 을 고치고 로그를 고치고 해시를 다시 계산할 수
있으므로, 여기서 만드는 것은 위조를 막는 장치가 아니라 **위조를 드러내는 사본들**이다:
종료 코드는 yaml 에도 원시 로그에도 적히고(`EXIT_LINE`), `log_sha256` 이 그 로그를 봉인한다.
셋이 어긋나면 종료 검사가 잡는다. 셋을 다 맞춰도 남는 것이 **재실행 대조**다(`replay`) —
기록을 고쳐도 명령을 다시 돌린 결과는 고칠 수 없다. 그것이 종점이고 AGENTS.core §4 가 말하는 것이다."""
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

from . import __version__, frontmatter
from .docs import find_unit_dir, first_approval_commit
from .gitinfo import artifact_hash, changed_files, dirty_tree_hash, head_sha, is_repo, repo_id
from .util import dump_yaml, load_yaml, mask_secrets, now_iso, rel, sha256_bytes, sha256_file

EVIDENCE_SCHEMA = "romeo/evidence@0.1.0"

# 원시 로그의 종료 코드 줄. 사람이 읽는 줄이자 기계가 대조하는 줄이다 — 두 벌을 적지 않는다.
EXIT_LINE = "--- exit {code} ---"
EXIT_LINE_RE = re.compile(r"^--- exit (-?\d+) ---$")
# 명령이 끝난 시점의 산출물 식별도 같은 로그에 적어 `log_sha256` 이 봉인하게 한다(4차 리뷰 구멍 B 의 한 겹).
# evidence yaml 의 head_sha·dirty_tree_hash 만 손으로 고치면 로그의 이 줄과 어긋난다.
# 원시 로그의 구획 표지. 기록자가 쓰는 자리와 대조가 읽는 자리를 같은 상수로 묶는다 —
# 한쪽만 바뀌면 여러 줄 명령의 헤더 경계가 어긋나고, 그 어긋남은 위조와 구별되지 않는다.
STDOUT_MARK = "--- stdout ---"
STDERR_MARK = "--- stderr ---"
HEAD_LINE = "--- head {sha} ---"
TREE_LINE = "--- tree {hash} ---"
HEAD_LINE_RE = re.compile(r"^--- head ([0-9a-f]{40}) ---$")
TREE_LINE_RE = re.compile(r"^--- tree ([0-9a-f]{64}) ---$")
# 가드 결정(승인·거부)의 원시 로그가 봉인하는 두 줄. `seq` 는 같은 시각에 들어온 결정의 순서를,
# `note` 는 설명 요구가 읽는 값을 담는다 — 둘 다 yaml 한 글자로 판정을 뒤집을 수 있는 자리다.
SEQ_LINE = "seq: {seq}"
SEQ_LINE_RE = re.compile(r"^seq: (\d+)$")
NOTE_LINE = "note: {note}"

# 재실행 대조의 기본 상한(초). 검증 명령이 이보다 오래 걸리면 대조하지 못한 것으로 인쇄한다.
# 상한은 재실행 **한 건**에 걸린다. 하네스 자신을 고치는 단위는 그 한 건에 전체 테스트를 넣는 것이
# 정당하므로(그때는 그것이 그 단위의 산출물이다) 이 값은 테스트가 늘수록 압박을 받는다 —
# 2026-09-02 실측에서 258초가 상한 300초에 붙어 이 값을 올렸다.
RERUN_TIMEOUT = 600

# 재실행 한 건이 상한의 이 비율 이상을 쓰면 close 가 경고한다 — 막지 않고 **막히기 전에** 드러낸다.
# 임계 아래에서는 인쇄하지 않는다: 늘 뜨는 경고는 아무것도 알리지 않는다.
RERUN_NEAR_TIMEOUT_RATIO = 0.8


# ── 가드 결정의 설명 요구 (AGENTS.core §11: 요구하는 자리와 보는 자리를 같게 둔다) ──────────────
# 요구는 `core/policy/execution-guards.yaml` 의 `required_explanation` 이 소유한다. 여기에는 라벨을 적지 않는다 —
# 적는 순간 정본이 둘이 되고, 한쪽만 고친 커밋이 "요구는 넷인데 검사는 셋" 을 만든다.
GUARD_POLICY_REL = "core/policy/execution-guards.yaml"

# 값이 이것뿐이면 적히지 않은 것과 같다. **자리표시자 단독**만 막는다 —
# "사전 백업: 없음 — 커밋 전이라 스냅샷이 없다" 처럼 이유가 붙으면 정직한 답이고 통과한다(§AC-7).
EXPLANATION_PLACEHOLDERS = (
    "tbd", "todo", "t.b.d", "n/a", "na", "none", "null", "nil", "-", "--", "?", "??",
    "later", "fixme", "xxx", "unknown", "pending", "채움", "미정", "나중에", "추후",
    "해당 없음", "해당없음", "없음", "모름", "확인 필요", "확인필요", "미확인",
)
# 값에서 지워도 뜻이 남지 않는 글자. 자리표시자만 남았는지 볼 때 쓴다.
_TRIVIAL_CHARS = " \t\n.,;:·…-—–_()[]{}\"'`~!*/|"


def required_explanation(harness_root=None):
    """설명 요구 네 항목을 정책표에서 읽는다 → [{key, label, why}].

    이 함수가 정책표를 읽는 **유일한 자리**이고, 기록(`add_approval`·`add_rejection`)과
    종료 검사(`romeo/close.py`)가 둘 다 이것을 통해 같은 목록을 본다."""
    from . import HARNESS_ROOT
    path = Path(harness_root or HARNESS_ROOT) / GUARD_POLICY_REL
    data = load_yaml(path) or {}
    items = data.get("required_explanation") or []
    out = []
    for it in items:
        if not isinstance(it, dict) or not it.get("key") or not it.get("label"):
            raise ValueError(f"{GUARD_POLICY_REL} 의 required_explanation 항목이 {{key, label, why}} 형태가 아니다: {it!r}")
        out.append({"key": str(it["key"]), "label": str(it["label"]), "why": str(it.get("why") or "")})
    if not out:
        raise ValueError(f"{GUARD_POLICY_REL} 에 required_explanation 이 없다 — 설명 요구의 출처가 비어 있다")
    return out


def _label_re(label):
    """라벨을 note 안에서 찾는 정규식. 라벨 안의 공백은 유연하게, 뒤의 구분자는 `:` 또는 `：`."""
    parts = [re.escape(x) for x in str(label).split()]
    return re.compile(r"(?:^|[\s·;,|/])(" + r"\s*".join(parts) + r")\s*[:：]", re.MULTILINE)


def _is_placeholder(value):
    """값이 자리표시자뿐인가. 자리표시자 토큰과 뜻 없는 글자를 걷어내고 남는 것이 있으면 답이다."""
    v = (value or "").strip().lower()
    if not v:
        return True
    for token in sorted(EXPLANATION_PLACEHOLDERS, key=len, reverse=True):
        v = v.replace(token, " ")
    return not v.strip(_TRIVIAL_CHARS).strip()


def parse_guard_explanation(note, harness_root=None):
    """가드 결정의 note 를 정책표의 라벨로 대조해 {key: 값} 으로 쪼갠다.

    **네 항목 중 하나라도 없거나 값이 자리표시자뿐이면 `ValueError` 다.** 그 자리에 글자가 있는지가 아니라
    그 문장이 답인지를 본다(AGENTS.core §11). 막는 것은 빈 승인이지 정직한 답이 아니다 —
    "사전 백업: 없음 — 아직 커밋 전이다" 는 유효하다."""
    items = required_explanation(harness_root)
    text = note if isinstance(note, str) else ""
    hits = []
    for it in items:
        m = _label_re(it["label"]).search(text)
        if m:
            hits.append((m.start(1), m.end(0), it))
    hits.sort()
    bounds = [h[0] for h in hits]
    values = {}
    for i, (_s, end, it) in enumerate(hits):
        stop = bounds[i + 1] if i + 1 < len(hits) else len(text)
        # 항목 사이 구분자(`/`·`·`·줄바꿈)는 값이 아니다 — 붙어 있으면 자리표시자 판정이 헛돈다.
        values[it["key"]] = text[end:stop].strip().strip("/|·;,").strip()
    missing = [it for it in items if it["key"] not in values]
    empty = [it for it in items if it["key"] in values and _is_placeholder(values[it["key"]])]
    if missing or empty:
        why = []
        if missing:
            why.append("빠진 항목: " + ", ".join(f"{it['label']}({it['why']})" for it in missing))
        if empty:
            why.append("값이 자리표시자뿐인 항목: " + ", ".join(it["label"] for it in empty))
        raise ValueError(
            "가드 결정의 --note 가 설명 요구를 채우지 못했다 — 기록하지 않는다. "
            + " / ".join(why)
            + ". 형식: --note \"" + " / ".join(f"{it['label']}: <{it['why']}>" for it in items) + "\""
        )
    return values


def exclusions(unit_id):
    """dirty_tree_hash·changed_files 에서 제외하는 경로: 하네스 원시 로그와 이 단위의 문서 디렉터리(기록 자체가 트리를 바꾸므로)."""
    return [".harness", f"docs/work/{unit_id}"]


def tree_state(project_root, unit_id, base_sha=None):
    ex = exclusions(unit_id)
    files = [f for f in changed_files(project_root, base_sha) if not any(f == e or f.startswith(e + "/") for e in ex)]
    return {
        "head_sha": head_sha(project_root),
        "dirty_tree_hash": dirty_tree_hash_excluding(project_root, ex),
        "changed_files": files,
        "artifact_hash": artifact_hash(project_root, files),
    }


def dirty_tree_hash_excluding(project_root, ex):
    import hashlib
    from .gitinfo import _git, untracked_files
    h = hashlib.sha256()
    pathspec = [".", *[f":(exclude){e}" for e in ex]]
    h.update(b"--cached\0")
    h.update(_git(["diff", "--cached", "--binary", "--no-color", "--no-ext-diff", "--", *pathspec], project_root).stdout.encode("utf-8", "surrogateescape"))
    h.update(b"--worktree\0")
    h.update(_git(["diff", "--binary", "--no-color", "--no-ext-diff", "--", *pathspec], project_root).stdout.encode("utf-8", "surrogateescape"))
    for path in untracked_files(project_root):
        if any(path == e or path.startswith(e + "/") for e in ex):
            continue
        h.update(b"--untracked\0" + path.encode("utf-8") + b"\0")
        p = Path(project_root) / path
        if p.is_file():
            with open(p, "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()


def evidence_dir(project_root, unit_id):
    return find_unit_dir(project_root, unit_id) / "evidence"


def list_runs(project_root, unit_id):
    d = evidence_dir(project_root, unit_id)
    if not d.is_dir():
        return []
    runs = [load_yaml(p) | {"_path": str(p)} for p in sorted(d.glob("*.yaml"))]
    # finished_at 은 초 단위라 같은 초에 끝난 run 은 동률이다 — 그때는 파일의 수정 시각으로 가른다(이름 순이 '최신' 으로 읽히지 않게).
    runs.sort(key=lambda r: (r.get("finished_at") or "", Path(r["_path"]).stat().st_mtime))
    return runs


def _spec_ref(project_root, unit_id):
    spec = find_unit_dir(project_root, unit_id) / "spec.md"
    return {"path": rel(spec, project_root), "sha256": sha256_file(spec)}


def default_run_name():
    return time.strftime("run-%Y%m%d")


def _change_base(project_root, unit_id, udir=None, run_name=None):
    """`changed_files` 의 기준 커밋.

    이 run 의 작업 계약(`task/<run>-implementer.json`)이 있으면 **그 계약의 `base_sha`** 다 — 워커가 출발한 리비전이고,
    거기서부터의 변경만이 이 실행의 변경이다(승인 뒤 tip 까지 쌓인 하네스 커밋이 섞이지 않는다 — 검토자가 '변경이
    allowed_paths 밖' 으로 오독하던 자리, 체크리스트 41 검토 finding). 계약이 없으면(가장 작은 단위·승인 전용 레코드)
    아래 규칙이다.

    이 단위가 **처음 승인되기 직전**의 커밋(첫 승인 커밋의 부모).

    approve 는 더 이상 base_sha 를 적지 않으므로(체크리스트 38) 이력에서 첫 승인 커밋을 찾고 그 부모를 쓴다. 승인 커밋 자체가 아니라
    부모인 이유: 가장 작은 단위(T0)는 승인과 구현을 한 커밋에 넣는다 — 기준을 승인 커밋으로 잡으면 그 커밋에 든 구현이 변경으로
    잡히지 않아 `HAS_CHANGE` 가 "아무것도 바뀌지 않았다" 로 떨어진다. 재승인 커밋이 아니라 **첫** 승인인 이유도 같다 — 구현 뒤에
    검증 계획을 고쳐 재승인하면 구현은 재승인 전에 있다. 이 값은 approve 가 예전에 적던 것(승인 시점의 HEAD)과 같은 의미이고,
    작업 계약의 `base_sha`(현재 승인 커밋 — 워커가 보는 리비전)와는 다른 것이다. 둘을 대조하는 검사는 없다.
    승인이 아직 커밋되지 않았거나(승인 전용 레코드) 첫 승인 커밋이 뿌리 커밋이면 HEAD 다."""
    if udir is not None and run_name:
        task = Path(udir) / "task" / f"{run_name}-implementer.json"
        if task.is_file():
            try:
                import json
                contract = json.loads(task.read_text(encoding="utf-8")) or {}
            except (OSError, ValueError):
                contract = {}
            sha = contract.get("base_sha")
            # 위임(worktree) 계약만 그 base 를 쓴다 — 워커가 출발한 리비전이다. 현재 작업 공간(current)의 T0 는 승인과 구현을
            # 한 커밋에 넣을 수 있어 계약 base(=승인 커밋)를 쓰면 그 구현이 변경으로 잡히지 않는다(검토 finding).
            if isinstance(sha, str) and sha and contract.get("workspace") == "worktree":
                return sha
    try:
        approval = first_approval_commit(project_root, unit_id)
    except ValueError:
        return head_sha(project_root)
    proc = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{approval}^"],
                          cwd=str(Path(project_root).resolve()), capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 and proc.stdout.strip() else approval


def _open_record(project_root, unit_id, run_name):
    """run 레코드를 열거나(없으면) 만든다. 명령 실행과 승인 기록이 같은 레코드 구조를 쓴다 —
    승인이 먼저 와도(절차 순서: 승인 → 실행) 기록할 곳이 있어야 한다."""
    udir = find_unit_dir(project_root, unit_id)
    edir = udir / "evidence"
    edir.mkdir(exist_ok=True)
    epath = edir / f"{run_name}.yaml"
    if epath.exists():
        return epath, load_yaml(epath)
    base_sha = _change_base(project_root, unit_id, udir, run_name) if is_repo(project_root) else None
    rec = {
        "schema": EVIDENCE_SCHEMA, "romeo_version": __version__,
        "repo_id": repo_id(project_root), "run_id": run_name, "task_id": None, "dispatch_id": None,
        "unit_id": unit_id, "spec_ref": _spec_ref(project_root, unit_id),
        "base_sha": base_sha, "head_sha": None, "dirty_tree_hash": None,
        "environment": {"os": platform.platform(), "python": sys.version.split()[0], "cwd": str(project_root)},
        "started_at": now_iso(), "finished_at": None,
        "commands": [], "changed_files": [], "artifact_hash": None,
        "reviewer": None, "verdict": None, "approvals": [],
    }
    return epath, rec


def _stamp_ids(rec, **ids):
    """위임 식별자를 run 당 한 번만 기록한다(계획 §3.5). 이미 다른 값이 있으면 덮어쓰지 않고 거부한다 —
    한 run 이 두 위임에 속한 것처럼 보이면 증거의 출처를 알 수 없다."""
    for key, val in ids.items():
        if val is None:
            continue
        cur = rec.get(key)
        if cur is not None and cur != val:
            raise ValueError(f"{key} 가 이미 {cur!r} 로 기록돼 있다 (요청값 {val!r}) — "
                             f"한 run 은 한 위임에 속한다. 다른 위임이면 --run 으로 새 run 을 만든다")
        rec[key] = val


def run_command(unit_id, command, run_name=None, label=None, project_root=".", task_id=None, dispatch_id=None):
    project_root = Path(project_root).resolve()
    if not is_repo(project_root):
        raise RuntimeError("git 저장소가 아니다 — evidence 는 HEAD SHA 에 묶여야 한다")
    run_name = run_name or default_run_name()
    epath, rec = _open_record(project_root, unit_id, run_name)
    _stamp_ids(rec, task_id=task_id, dispatch_id=dispatch_id)
    base_sha = rec.get("base_sha") or head_sha(project_root)
    n = len(rec["commands"]) + 1
    label = label or f"cmd-{n}"
    log_dir = project_root / ".harness" / "runs" / unit_id / run_name
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{n:02d}-{label}.log"
    started = now_iso()
    t0 = time.time()
    proc = subprocess.run(command, shell=True, cwd=str(project_root), capture_output=True, text=True)
    elapsed = round(time.time() - t0, 3)
    # 명령이 끝난 직후의 산출물 식별. 원시 로그(.harness)는 트리 해시에서 빠지므로 로그를 쓰기 전에 재도 값이 같다.
    state = tree_state(project_root, unit_id, base_sha)
    log_text = mask_secrets(f"$ {command}\n{STDOUT_MARK}\n{proc.stdout}\n{STDERR_MARK}\n{proc.stderr}\n"
                            + EXIT_LINE.format(code=proc.returncode) + "\n"
                            + HEAD_LINE.format(sha=state["head_sha"]) + "\n"
                            + TREE_LINE.format(hash=state["dirty_tree_hash"]) + "\n")
    log_path.write_text(log_text, encoding="utf-8")
    cmd_rec = {
        "id": label, "command": mask_secrets(command), "exit_code": proc.returncode,
        "started_at": started, "finished_at": now_iso(), "seconds": elapsed,
        "log": rel(log_path, project_root), "log_sha256": sha256_bytes(log_text.encode("utf-8")),
        "stdout_tail": mask_secrets(proc.stdout[-400:]).strip(),
        # 이 명령이 돈 산출물. run 의 head_sha·dirty_tree_hash 는 마지막 명령의 것이라, 한 run 안에서 검사가
        # 서로 다른 트리에서 돌았는지는 명령별 값으로만 알 수 있다(체크리스트 41 검토 finding).
        "head_sha": state["head_sha"], "dirty_tree_hash": state["dirty_tree_hash"],
    }
    rec["commands"].append(cmd_rec)
    rec.update(state)
    rec["finished_at"] = cmd_rec["finished_at"]
    rec["spec_ref"] = _spec_ref(project_root, unit_id)
    epath.write_text(dump_yaml(rec), encoding="utf-8")
    return {"evidence": str(epath), "command": cmd_rec, "state": state}


DECISIONS = {
    # 종류별로 다른 것: 레코드 키 · 시각/주체 필드 이름 · 원시 로그 파일 이름 · 로그 첫 줄.
    # 승인과 거부를 **같은 봉인**으로 남기되 **다른 배열**에 넣는다 — 기존 종료 검사는 `approvals` 의
    # 존재를 승인으로 세므로, 섞으면 거부가 승인으로 읽힌다.
    "approve": {"array": "approvals", "at": "approved_at", "by": "approved_by", "prefix": "approve"},
    "reject": {"array": "rejections", "at": "rejected_at", "by": "rejected_by", "prefix": "reject"},
}


def decision_log_text(spec, entry):
    """가드 결정 하나의 원시 로그 본문을 그 yaml 항목에서 만든다.

    **쓰는 자리와 대조하는 자리가 이 함수 하나를 쓴다.** 두 벌로 적으면 한쪽만 바뀐 커밋이
    위조와 구별되지 않는 불일치를 만들고, 그때 막히는 것은 지시대로 쓴 사람이다(AGENTS.core §11).

    `note` 는 여러 줄일 수 있다. 로그는 `note: ` 뒤부터 head·tree 두 줄 앞까지가 note 이므로
    항목에서 로그 전체를 다시 만들어 통째로 비교하면 여러 줄도 그대로 복원된다 —
    줄 단위로 잘라 맞추지 않는 것은 note 안의 개행 문자가 줄 경계로 읽혀 복원이 손실되기 때문이다.
    손실된 복원은 위조와 구별되지 않는다."""
    return mask_secrets(
        f"{spec['prefix']} guard={entry.get('guard')} by={entry.get(spec['by'])} "
        f"at={entry.get(spec['at'])}\n"
        + SEQ_LINE.format(seq=entry.get("seq")) + "\n"
        + NOTE_LINE.format(note=entry.get("note") or "") + "\n"
        + HEAD_LINE.format(sha=entry.get("head_sha")) + "\n"
        + TREE_LINE.format(hash=entry.get("dirty_tree_hash")) + "\n")


def _add_decision(kind, unit_id, guard, by, note=None, run_name=None, project_root=".",
                  task_id=None, dispatch_id=None, harness_root=None):
    """가드 결정(승인·거부) 하나를 evidence 에 기록한다.

    결정은 실행보다 **먼저** 온다 — 가드가 붙은 작업은 결정 전에 상태를 바꾸지 않기 때문이다.
    그래서 선행 run 이 없으면 결정 전용 레코드(`commands: []`)를 새로 만든다:
    결정 시점에 실행한 명령이 0건이라는 사실 자체가 '승인 전 상태 변경 0건' 의 증거다.
    선행 run 이 있으면 지금까지처럼 거기에 붙인다.

    **설명 요구를 기록 전에 본다.** 네 항목이 없으면 `ValueError` 를 내고 **아무것도 쓰지 않는다** —
    반쪽 기록(로그는 남고 배열은 비었거나 그 반대)을 남기지 않기 위해서다. 기록되지 않았으므로
    상태는 결정 전 그대로다."""
    spec = DECISIONS[kind]
    parse_guard_explanation(note, harness_root)   # 기록 전에 막는다. 통과한 값만 아래로 내려간다.
    project_root = Path(project_root).resolve()
    runs = list_runs(project_root, unit_id)
    if run_name:
        runs = [r for r in runs if r["run_id"] == run_name]
    if runs:
        rec = runs[-1]
        path = Path(rec.pop("_path"))
    else:
        path, rec = _open_record(project_root, unit_id, run_name or default_run_name())
    _stamp_ids(rec, task_id=task_id, dispatch_id=dispatch_id)
    entry = {"guard": guard, spec["at"]: now_iso(), spec["by"]: by, "note": note}
    # 결정 사건도 명령 기록과 같은 방식으로 봉인한다 — yaml 배열만 믿으면 한 항목을 손으로 써 넣는 것으로 가드가 열린다.
    run_name = rec.get("run_id") or path.stem
    log_dir = project_root / ".harness" / "runs" / unit_id / run_name
    log_dir.mkdir(parents=True, exist_ok=True)
    n = len(rec.get(spec["array"]) or []) + 1
    # 결정 순서. `now_iso()` 는 초 단위라 승인과 거부가 같은 초에 들어오면 시각만으로는 순서를 말할 수 없다 —
    # 그런데 "가장 최근 결정" 이 판정이므로 순서를 잃으면 거부가 승인으로 뒤집힌다. 이 레코드 안의 결정을
    # 종류에 상관없이 세어 붙이고, 로그에도 적어 `log_sha256` 이 함께 봉인하게 한다.
    seq = sum(len(rec.get(s["array"]) or []) for s in DECISIONS.values()) + 1
    log_path = log_dir / f"{spec['prefix']}-{n:02d}-{guard}.log"
    state = tree_state(project_root, unit_id, rec.get("base_sha"))
    entry["seq"] = seq
    entry["head_sha"], entry["dirty_tree_hash"] = state["head_sha"], state["dirty_tree_hash"]
    # 로그 본문은 **이 항목에서** 만든다 — 대조하는 자리가 부르는 함수와 같은 것이다(AGENTS.core §11).
    log_text = decision_log_text(spec, entry)
    log_path.write_text(log_text, encoding="utf-8")
    entry["log"] = rel(log_path, project_root)
    entry["log_sha256"] = sha256_bytes(log_text.encode("utf-8"))
    rec.setdefault(spec["array"], []).append(entry)
    path.write_text(dump_yaml(rec), encoding="utf-8")
    return str(path)


def add_approval(unit_id, guard, by, note=None, run_name=None, project_root=".",
                 task_id=None, dispatch_id=None, harness_root=None):
    """실행 가드 **승인** 사건을 evidence 에 기록한다(M1: 대화 승인)."""
    return _add_decision("approve", unit_id, guard, by, note=note, run_name=run_name,
                         project_root=project_root, task_id=task_id, dispatch_id=dispatch_id,
                         harness_root=harness_root)


def add_rejection(unit_id, guard, by, note=None, run_name=None, project_root=".",
                  task_id=None, dispatch_id=None, harness_root=None):
    """실행 가드 **거부** 사건을 evidence 에 기록한다.

    거부는 승인의 부재가 아니다. "아직 안 물어봤다" 와 "물어봤고 사람이 아니라고 했다" 는 다른 상태이고,
    후자는 재시도가 답이 아니다 — 종료 검사가 그 둘을 다른 판정으로 인쇄할 수 있으려면 거부가 **기록**돼야 한다.
    설명 넷은 거부에도 요구한다: 무엇을 왜 거부했는지가 남아야 재요청이 같은 것을 반복하지 않는다."""
    return _add_decision("reject", unit_id, guard, by, note=note, run_name=run_name,
                         project_root=project_root, task_id=task_id, dispatch_id=dispatch_id,
                         harness_root=harness_root)


def guard_decisions(runs, guard_id):
    """한 가드에 대한 승인·거부를 **시각순으로 병합**한다 → [{kind, entry, at, by}].

    같은 시각이면 기록된 순서를 따른다(승인·거부가 같은 초에 들어오는 것은 사람의 결정이 아니라 기계의 동률이다).
    마지막 항목이 그 가드의 **현재 결정**이다 — 거부 뒤 승인이 오면 승인이 이긴다(사람이 다시 판단한 것이다)."""
    out = []
    for seq, rec in enumerate(runs):
        for kind, spec in DECISIONS.items():
            for i, e in enumerate(rec.get(spec["array"]) or []):
                if isinstance(e, dict) and e.get("guard") == guard_id:
                    # `seq` 가 없는 옛 기록(거부가 없던 시절의 승인)은 배열 안 순서로 갈음한다.
                    order = e["seq"] if isinstance(e.get("seq"), int) else i
                    out.append({"kind": kind, "entry": e, "at": e.get(spec["at"]) or "",
                                "by": e.get(spec["by"]), "note": e.get("note"), "_ord": (seq, order)})
    out.sort(key=lambda d: (d["at"], d["_ord"]))
    return out


def approval_log_state(project_root, approval, kind="approve"):
    """가드 결정 항목 하나를 **원시 로그와 대조한다**. (상태, 이유) — True·False·None(대조 불가).

    로그가 없는 기록(이 봉인이 없던 시절, 또는 다른 체크아웃)은 None 이다 — 통과가 아니라 미검증이다.
    승인과 거부는 같은 봉인을 쓰므로 같은 대조를 받는다 — `kind` 가 첫 줄의 낱말과 필드 이름만 바꾼다.

    대조하는 것은 **로그 전체**다: 첫 줄·head·tree 뿐 아니라 `seq`(같은 시각에 들어온 결정의 순서)와
    `note`(설명 요구가 읽는 값)까지 항목에서 다시 만들어 비교한다. 봉인해 놓고 대조하지 않는 줄은
    yaml 한 글자로 판정을 뒤집을 수 있는 자리이고, 그 자리는 규칙이 아니라 장식이다(AGENTS.core §11)."""
    spec = DECISIONS[kind]
    label = "승인" if kind == "approve" else "거부"
    ref = approval.get("log")
    if not isinstance(ref, str) or not ref.strip():
        return None, f"{approval.get('guard')}: {label} 기록에 원시 로그가 없다 — 봉인 없이 적힌 {label}이다"
    root = Path(project_root).resolve()
    path = Path(ref)
    path = path if path.is_absolute() else root / path
    try:
        path.resolve().relative_to(root)
    except ValueError:
        return False, f"{approval.get('guard')}: {label} 로그 경로가 저장소 밖이다 ({ref})"
    if not path.is_file():
        return None, f"{approval.get('guard')}: {label} 로그가 없다 ({ref}) — 다른 체크아웃에서는 대조할 수 없다"
    data = path.read_bytes()
    if sha256_bytes(data) != approval.get("log_sha256"):
        return False, f"{approval.get('guard')}: {label} 로그가 기록 이후 바뀌었다 (log_sha256 불일치)"
    text = data.decode("utf-8", "replace")
    first = text.splitlines()[0] if text else ""
    want = (f"{spec['prefix']} guard={approval.get('guard')} by={approval.get(spec['by'])} "
            f"at={approval.get(spec['at'])}")
    if first != want:
        return False, f"{approval.get('guard')}: {label} 기록({want!r})이 원시 로그의 첫 줄({first!r})과 다르다 — 손으로 고쳐졌다"
    lines = text.splitlines()
    for key, regex in (("head_sha", HEAD_LINE_RE), ("dirty_tree_hash", TREE_LINE_RE)):
        recorded, in_log = approval.get(key), _last_match(regex, lines)
        if isinstance(recorded, str) and recorded and in_log != recorded:
            return False, f"{approval.get('guard')}: {label} 시점의 {key} 가 원시 로그와 다르다"
    # ── seq·note 도 같은 대조를 받는다 ──────────────────────────────────────
    # head_sha·dirty_tree_hash 를 대조하는 이유가 그대로 이 둘에도 걸린다: 로그에 적어 봉인해 놓고
    # 대조하지 않으면 yaml 한 글자로 판정이 뒤집힌다. `seq` 는 같은 시각에 들어온 승인·거부의 순서를,
    # `note` 는 종료 시점의 설명 요구가 읽는 값을 정한다.
    recorded_seq = approval.get("seq")
    in_log_seq = SEQ_LINE_RE.match(lines[1]) if len(lines) > 1 else None
    if in_log_seq is None or not isinstance(recorded_seq, int):
        return None, (f"{approval.get('guard')}: {label} 기록이나 그 로그에 seq 가 없다 — "
                      "결정 순서를 봉인하지 않던 옛 형식이라 대조할 수 없다")
    if int(in_log_seq.group(1)) != recorded_seq:
        return False, (f"{approval.get('guard')}: {label} 의 seq 가 원시 로그와 다르다 "
                       f"(기록 {recorded_seq} vs 로그 {in_log_seq.group(1)}) — 결정 순서가 기록 이후 바뀌었다")
    if not all(isinstance(approval.get(k), str) and approval.get(k)
               for k in ("head_sha", "dirty_tree_hash")):
        return None, (f"{approval.get('guard')}: {label} 기록에 head_sha·dirty_tree_hash 가 없다 — "
                      "로그를 항목에서 다시 만들어 대조할 수 없다")
    # 남은 차이는 note 뿐이다. 항목에서 로그를 통째로 다시 만들어 비교한다 — 여러 줄 note 도 그대로다.
    # 이 대조가 없으면 종료 시점의 설명 요구가 **봉인되지 않은 yaml 을 읽는다**:
    # 로그에는 빈 note 를 두고 yaml 에만 네 항목을 적는 것으로 승인·종료 두 지점이 한 지점이 된다.
    if text != decision_log_text(spec, approval):
        return False, (f"{approval.get('guard')}: {label} 의 note 가 원시 로그와 다르다 — "
                       "설명이 기록 이후 바뀌었다. 종료 시점이 읽는 것은 봉인된 note 여야 한다")
    return True, ""


def record_review_envelope(unit_id, run_name, source, project_root="."):
    """검토자의 출력(결과 계약 JSON)을 `docs/work/<id>/review/<run>-reviewer.json` 에 기록하고 **그 파일의 sha256 을 같은 run 의 증거에 남긴다.**

    검토자는 자기 결과를 쓰지 않는다 — 위임한 쪽이 쓴다(역할 계약). 지금까지 그 쓰기는 손이었고, 봉투의 판정 문자열은 어떤 기록에도 묶이지
    않았다(정직한 FAIL 봉투에서 `gate_verdict` 한 단어만 바꾸면 통과했다 — 설계 검토가 재현했다). 여기서 봉투를 쓰는 즉시 `shasum` 을 증거 기록
    명령으로 실행해 그 해시가 원시 로그와 `log_sha256` 에 봉인되게 한다. 종료 검사는 봉투의 현재 해시가 그 기록과 같은지 본다.
    이것도 로컬 파일이다 — 봉투·증거·로그·해시를 전부 앞뒤 맞게 고치면 뚫린다. 검토자 면에는 재실행 대조 같은 종점이 없다."""
    import json
    project_root = Path(project_root).resolve()
    src = Path(source)
    try:
        env = json.loads(src.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(f"검토자 출력 {source} 을 JSON 으로 읽을 수 없다 ({e})")
    if not isinstance(env, dict):
        raise ValueError(f"검토자 출력 {source} 이 JSON 객체가 아니다")
    udir = find_unit_dir(project_root, unit_id)
    rdir = udir / "review"
    rdir.mkdir(exist_ok=True)
    dest = rdir / f"{run_name}-reviewer.json"
    dest.write_text(json.dumps(env, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rel_dest = rel(dest, project_root)
    res = run_command(unit_id, f"shasum -a 256 {rel_dest}", run_name=run_name, label=REVIEW_RECORD_LABEL,
                      project_root=project_root)
    return {"path": str(dest), "sha256": sha256_file(dest), "evidence": res["evidence"], "command": res["command"]}


def review_record_state(project_root, run_rec, envelope_path, product=None):
    """검토 봉투가 그 run 의 증거에 **기록된 그대로**인지 본다. (상태, 이유) — True·False·None.

    `record_review_envelope` 가 남긴 `review-record` 명령 기록의 stdout(sha256)이 봉투의 현재 sha256 과 같아야 하고, 그 기록은
    원시 로그와 봉인이 맞아야 한다. 기록이 없으면 None(미검증) — 이 명령이 없던 시절의 봉투이거나 손으로 쓴 봉투다.
    `product` 를 주면 기록 명령이 **그 산출물 위에서** 돌았는지도 본다 — 검토가 끝난 뒤 트리가 바뀐 상태에서 기록한 봉투는
    그 검토의 봉투가 아니다(옛 run 에 새 봉투를 기록해 판정을 옮기는 길)."""
    root = Path(project_root).resolve()
    path = Path(envelope_path)
    if not path.is_file():
        return None, "봉투 파일이 없다"
    want = sha256_file(path)
    recs = [c for c in (run_rec.get("commands") or []) if isinstance(c, dict) and c.get("id") == REVIEW_RECORD_LABEL
            and rel(path, root) in str(c.get("command", ""))]
    if not recs:
        return None, (f"{path.name}: 이 봉투를 기록한 명령(review-record)이 검토 run 의 증거에 없다 — "
                      f"봉투는 romeo review record 로 기록한다")
    last = recs[-1]
    if want not in str(last.get("stdout_tail", "")):
        return False, (f"{path.name}: 봉투의 sha256 {want[:12]} 이 기록 시점의 값과 다르다 — 기록 뒤에 봉투가 바뀌었다")
    state, why = command_log_state(root, last)
    if state is False:
        return False, f"{path.name}: 봉투 기록이 원시 로그와 어긋난다 — {why}"
    if state is None:
        return None, f"{path.name}: 봉투 기록의 원시 로그를 대조할 수 없다 — {why}"
    if product is not None:
        at = (last.get("head_sha"), last.get("dirty_tree_hash"))
        if at != tuple(product):
            return False, (f"{path.name}: 봉투를 기록한 시점의 산출물({str(at[0])[:7]}+{str(at[1])[:12]})이 검토 시점의 산출물"
                           f"({product[0][:7]}+{product[1][:12]})과 다르다 — 검토가 끝난 뒤 바뀐 트리에서 기록한 봉투다")
    return True, ""


REVIEW_RECORD_LABEL = "review-record"


# ── 기록을 읽는 쪽 ───────────────────────────────────────────────────────────────
# 여기까지가 기록을 만드는 코드다. 아래는 그 기록을 **믿지 않고 다시 확인하는** 코드다.
# 두 쪽을 한 모듈에 두는 이유는 기록 형식(로그 줄·해시 필드)을 아는 곳이 하나여야 하기 때문이다.

def parse_log_exit_code(text):
    """원시 로그에 적힌 종료 코드. 없으면 None — 없는 것을 0 으로 접지 않는다(K-51).

    로그 끝에서부터 찾는다. 명령의 stdout 이 같은 모양의 줄을 뱉어도 기록자가 마지막에 쓴 줄이 이긴다."""
    for line in reversed(str(text).splitlines()):
        m = EXIT_LINE_RE.match(line)
        if m:
            return int(m.group(1))
    return None


def log_command_header(lines):
    """원시 로그가 적은 **명령 전체**를 돌려준다. 로그 모양이 아니면 `None`(헤더를 읽지 못했다).

    로그는 명령을 `$ {command}` 로 한 번에 쓴다 — 명령이 개행을 담으면 그 헤더도 여러 줄이 된다.
    첫 물리 줄만 기록된 명령과 비교하면 여러 줄 명령은 **어떤 구현으로도** 통과하지 못한다
    (2026-08-31 `feat-20260831-park-defects-actm` 2회차: 검사 14건이 전부 exit 0 인데 close 가 FAIL).
    그래서 경계는 `$ ` 뒤부터 **첫 `--- stdout ---` 표지 앞**까지다.

    첫 표지인 이유: 그 줄은 기록자가 명령 출력보다 **먼저** 쓴다. 명령의 stdout 이 같은 모양의 줄을
    뱉어도 헤더는 늘어나지 않는다(종료 코드는 반대로 마지막 줄이 이긴다 — 그것도 기록자가 마지막에 쓰기 때문이다).
    표지가 없으면 이 로그는 기록자가 쓴 형식이 아니므로 헤더를 짐작하지 않고 `None` 을 준다 —
    짐작한 값으로 대조하면 통과도 거부도 근거가 없다. **부르는 쪽은 그때 대조를 건너뛰지 않고 미검증으로 돌린다**:
    건너뛰면 표지 줄을 지우고 봉인만 다시 맞춘 로그가 조용히 통과한다(2026-09-01 검토 F2 실측).

    대조를 **약하게 만들지 않는다**: 헤더 안을 한 글자만 고쳐도, 한 줄을 지워도 결과가 달라진다."""
    for i, line in enumerate(lines):
        if line == STDOUT_MARK:
            if i == 0 or not lines[0].startswith("$ "):
                return None
            return "\n".join(lines[:i])[2:]
    return None


def command_log_state(project_root, cmd_rec):
    """기록된 명령 하나를 **원시 로그와 대조한다**. 돌려주는 것은 (상태, 이유)이고 상태는 True·False·None 이다.

    None 은 통과가 아니라 '대조가 성립하지 않았다' 는 뜻이다 — 부르는 쪽이 미검증으로 인쇄한다.

    evidence yaml 의 `exit_code` 는 손으로 고칠 수 있다. 그래서 같은 사실이 두 번 적혀 있다:
    원시 로그의 종료 코드 줄과, 그 로그를 봉인한 `log_sha256`. yaml 만 고치면 로그와 어긋나고,
    로그까지 고치면 봉인과 어긋난다. 셋을 다 맞추는 것은 재실행 대조가 받는다(`replay`)."""
    ref = cmd_rec.get("log")
    if not isinstance(ref, str) or not ref.strip():
        return None, f"{cmd_rec.get('id')}: 기록에 원시 로그 경로가 없다"
    root = Path(project_root).resolve()
    path = Path(ref)
    path = path if path.is_absolute() else root / path
    try:
        path.resolve().relative_to(root)
    except ValueError:
        return False, f"{cmd_rec.get('id')}: 원시 로그 경로가 저장소 밖이다 ({ref})"
    if not path.is_file():
        return None, (f"{cmd_rec.get('id')}: 원시 로그가 없다 ({ref}) — .harness 는 커밋되지 않으므로"
                      f" 다른 체크아웃에서는 대조할 수 없다. 이 기록은 로그로 확인되지 않았다")
    data = path.read_bytes()
    want = cmd_rec.get("log_sha256")
    if not isinstance(want, str) or not want:
        return None, f"{cmd_rec.get('id')}: 기록에 log_sha256 이 없다 — 로그를 봉인한 값이 없어 대조할 수 없다"
    got = sha256_bytes(data)
    if got != want:
        return False, (f"{cmd_rec.get('id')}: 원시 로그가 기록 이후 바뀌었다 "
                       f"(log_sha256 {want[:12]} vs 실제 {got[:12]})")
    text = data.decode("utf-8", "replace")
    lines = text.splitlines()
    logged_command = log_command_header(lines)
    if logged_command is None:
        # 표지 줄이 없으면 대조할 값이 없다. **건너뛰지 않는다** — 건너뛰면 표지를 지우고 봉인만 다시 맞춘
        # 로그가 명령 대조를 통과한다(종료 코드 줄이 없을 때와 같은 처리다). close 는 미검증을 통과로 세지 않는다(K-51).
        return None, f"{cmd_rec.get('id')}: 원시 로그에 명령 헤더가 없다 — 대조할 값이 없다"
    if logged_command != cmd_rec.get("command"):
        return False, (f"{cmd_rec.get('id')}: 기록된 명령 {cmd_rec.get('command')!r} 가 "
                       f"원시 로그가 실행한 {logged_command!r} 와 다르다 — 증거 파일이 손으로 고쳐졌다")
    logged = parse_log_exit_code(text)
    if logged is None:
        return None, f"{cmd_rec.get('id')}: 원시 로그에 종료 코드 줄이 없다 — 대조할 값이 없다"
    if logged != cmd_rec.get("exit_code"):
        return False, (f"{cmd_rec.get('id')}: 기록된 종료 코드 {cmd_rec.get('exit_code')} 가 "
                       f"원시 로그의 {logged} 와 다르다 — 증거 파일이 손으로 고쳐졌다")
    # 산출물 식별 줄 — 기록과 로그 양쪽에 있을 때만 대조한다(이 줄이 없던 시절의 기록은 그 줄로 판정하지 않는다).
    for key, regex, what in (("head_sha", HEAD_LINE_RE, "head_sha"), ("dirty_tree_hash", TREE_LINE_RE, "dirty_tree_hash")):
        recorded = cmd_rec.get(key)
        in_log = _last_match(regex, lines)
        if not (isinstance(recorded, str) and recorded):
            if in_log is not None:
                # 로그에는 봉인 줄이 있는데 기록에서 그 값이 사라졌다 — 옛 형식을 흉내내려고 기록만 지운 흔적이다.
                return False, (f"{cmd_rec.get('id')}: 원시 로그에는 {what} 봉인 줄이 있는데 기록에 그 값이 없다 — "
                               f"기록에서 봉인 값이 지워졌다")
            continue                       # 봉인 줄이 없던 시절의 기록 — 그 줄로 판정하지 않는다
        if in_log is None:
            return False, (f"{cmd_rec.get('id')}: 기록에는 {what} 가 있는데 원시 로그에 봉인 줄(--- {what.split('_')[0] if what == 'head_sha' else 'tree'} … ---)이 없다 — "
                           f"봉인 줄이 지워졌거나 옛 형식을 흉내낸 로그다")
        if in_log != recorded:
            return False, (f"{cmd_rec.get('id')}: 기록된 {what} {recorded[:12]} 가 원시 로그의 {in_log[:12]} 와 다르다 — "
                           f"증거 파일의 산출물 식별이 손으로 고쳐졌다")
    return True, ""


def sealed_product(rec):
    """run 이 기록한 산출물 식별 중 **봉인된 자리**(마지막 명령 기록)의 값. (식별자, 불일치 이유)

    close 와 동등성 판정이 읽는 것은 run 최상위의 head_sha·dirty_tree_hash 인데, 로그가 봉인하는 것은 명령별 값이다 —
    둘 사이가 대조되지 않으면 최상위 두 줄만 고쳐 판정을 다른 산출물로 옮길 수 있다(설계 검토가 재현했다).
    마지막 명령 기록에 값이 있으면 최상위 값과 같아야 하고, 다르면 이유를 돌려준다. 명령별 값이 없는 옛 기록은 최상위 값을 그대로 쓴다."""
    top = (rec.get("head_sha"), rec.get("dirty_tree_hash"))
    cmds = [c for c in (rec.get("commands") or []) if isinstance(c, dict)]
    last = cmds[-1] if cmds else None
    if last is None or not (isinstance(last.get("head_sha"), str) and isinstance(last.get("dirty_tree_hash"), str)):
        return top, None
    sealed = (last["head_sha"], last["dirty_tree_hash"])
    if sealed != top:
        return sealed, (f"run 최상위의 산출물 식별({str(top[0])[:7]}+{str(top[1])[:12]})이 마지막 명령 기록"
                        f"({sealed[0][:7]}+{sealed[1][:12]})과 다르다 — 봉인되지 않은 자리만 고쳐졌다")
    return sealed, None


def _last_match(regex, lines):
    for line in reversed(lines):
        m = regex.match(line)
        if m:
            return m.group(1)
    return None


def replay(project_root, command, timeout=RERUN_TIMEOUT):
    """검증 명령을 **다시 실행해서** 종료 코드만 돌려준다. 아무것도 기록하지 않는다.

    실행이 성립하지 않으면(시간 초과·실행 자체 실패) 종료 코드 대신 이유 문장을 돌려준다:
    (종료 코드, None) 또는 (None, 이유). 실행하지 못한 것을 0 으로도 실패로도 접지 않는다(K-51).

    기록과 달리 이것은 재현할 수 없는 위조 대상이다 — 명령을 다시 돌린 결과는 파일을 고쳐서 바꿀 수 없다."""
    try:
        proc = subprocess.run(command, shell=True, cwd=str(Path(project_root).resolve()),
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, f"재실행이 {timeout}초 안에 끝나지 않았다"
    except OSError as e:
        return None, f"재실행을 시작하지 못했다 ({e})"
    return proc.returncode, None


def run_required_checks(unit_id, run_name=None, project_root=".", task_id=None, dispatch_id=None):
    """spec.md 의 required_checks 를 문자열 그대로 순서대로 실행한다 — close 가 대조하는 명령과 정확히 일치시키기 위해."""
    from .close import required_checks
    udir = find_unit_dir(project_root, unit_id)
    _, body = frontmatter.read(udir / "spec.md")
    results = []
    for rc in required_checks(body):
        results.append(run_command(unit_id, rc["command"], run_name=run_name, label=rc.get("id"),
                                   project_root=project_root, task_id=task_id, dispatch_id=dispatch_id))
    return results
