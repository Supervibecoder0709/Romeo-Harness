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

# 재실행 대조의 기본 상한(초). 검증 명령이 이보다 오래 걸리면 대조하지 못한 것으로 인쇄한다.
RERUN_TIMEOUT = 300


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


def add_approval(unit_id, guard, by, note=None, run_name=None, project_root=".", task_id=None, dispatch_id=None):
    """실행 가드 승인 사건을 evidence 에 기록한다(M1: 대화 승인).

    승인은 실행보다 **먼저** 온다 — 가드가 붙은 작업은 승인 전에 상태를 바꾸지 않기 때문이다.
    그래서 선행 run 이 없으면 승인 전용 레코드(`commands: []`)를 새로 만든다:
    승인 시점에 실행한 명령이 0건이라는 사실 자체가 '승인 전 상태 변경 0건' 의 증거다.
    선행 run 이 있으면 지금까지처럼 거기에 붙인다."""
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
    entry = {"guard": guard, "approved_at": now_iso(), "approved_by": by, "note": note}
    # 승인 사건도 명령 기록과 같은 방식으로 봉인한다 — yaml 의 approvals 배열만 믿으면 한 항목을 손으로 써 넣는 것으로 가드가 열린다.
    run_name = rec.get("run_id") or path.stem
    log_dir = project_root / ".harness" / "runs" / unit_id / run_name
    log_dir.mkdir(parents=True, exist_ok=True)
    n = len(rec.get("approvals") or []) + 1
    log_path = log_dir / f"approve-{n:02d}-{guard}.log"
    state = tree_state(project_root, unit_id, rec.get("base_sha"))
    log_text = mask_secrets(f"approve guard={guard} by={by} at={entry['approved_at']}\nnote: {note or ''}\n"
                            + HEAD_LINE.format(sha=state["head_sha"]) + "\n"
                            + TREE_LINE.format(hash=state["dirty_tree_hash"]) + "\n")
    log_path.write_text(log_text, encoding="utf-8")
    entry["log"] = rel(log_path, project_root)
    entry["log_sha256"] = sha256_bytes(log_text.encode("utf-8"))
    entry["head_sha"], entry["dirty_tree_hash"] = state["head_sha"], state["dirty_tree_hash"]
    rec.setdefault("approvals", []).append(entry)
    path.write_text(dump_yaml(rec), encoding="utf-8")
    return str(path)


def approval_log_state(project_root, approval):
    """가드 승인 항목 하나를 **원시 로그와 대조한다**. (상태, 이유) — True·False·None(대조 불가).

    로그가 없는 기록(이 봉인이 없던 시절, 또는 다른 체크아웃)은 None 이다 — 통과가 아니라 미검증이다."""
    ref = approval.get("log")
    if not isinstance(ref, str) or not ref.strip():
        return None, f"{approval.get('guard')}: 승인 기록에 원시 로그가 없다 — 봉인 없이 적힌 승인이다"
    root = Path(project_root).resolve()
    path = Path(ref)
    path = path if path.is_absolute() else root / path
    try:
        path.resolve().relative_to(root)
    except ValueError:
        return False, f"{approval.get('guard')}: 승인 로그 경로가 저장소 밖이다 ({ref})"
    if not path.is_file():
        return None, f"{approval.get('guard')}: 승인 로그가 없다 ({ref}) — 다른 체크아웃에서는 대조할 수 없다"
    data = path.read_bytes()
    if sha256_bytes(data) != approval.get("log_sha256"):
        return False, f"{approval.get('guard')}: 승인 로그가 기록 이후 바뀌었다 (log_sha256 불일치)"
    text = data.decode("utf-8", "replace")
    first = text.splitlines()[0] if text else ""
    want = f"approve guard={approval.get('guard')} by={approval.get('approved_by')} at={approval.get('approved_at')}"
    if first != want:
        return False, f"{approval.get('guard')}: 승인 기록({want!r})이 원시 로그의 첫 줄({first!r})과 다르다 — 손으로 고쳐졌다"
    lines = text.splitlines()
    for key, regex in (("head_sha", HEAD_LINE_RE), ("dirty_tree_hash", TREE_LINE_RE)):
        recorded, in_log = approval.get(key), _last_match(regex, lines)
        if isinstance(recorded, str) and recorded and in_log != recorded:
            return False, f"{approval.get('guard')}: 승인 시점의 {key} 가 원시 로그와 다르다"
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
