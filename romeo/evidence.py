"""evidence 기록: 명령을 실제로 실행하고 HEAD SHA·dirty_tree_hash·변경 파일·산출물 해시와 함께 남긴다(C-E1).
원시 로그는 .harness/runs/ (git 제외, K-24), evidence yaml 에는 경로와 해시만. 손으로 쓰지 않는다."""
import platform
import subprocess
import sys
import time
from pathlib import Path

from . import __version__, frontmatter
from .docs import find_unit_dir
from .gitinfo import artifact_hash, changed_files, dirty_tree_hash, head_sha, is_repo, repo_id
from .util import dump_yaml, load_yaml, mask_secrets, now_iso, rel, sha256_bytes, sha256_file

EVIDENCE_SCHEMA = "romeo/evidence@0.1.0"


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
    runs.sort(key=lambda r: r.get("finished_at") or "")
    return runs


def _spec_ref(project_root, unit_id):
    spec = find_unit_dir(project_root, unit_id) / "spec.md"
    return {"path": rel(spec, project_root), "sha256": sha256_file(spec)}


def default_run_name():
    return time.strftime("run-%Y%m%d")


def _open_record(project_root, unit_id, run_name):
    """run 레코드를 열거나(없으면) 만든다. 명령 실행과 승인 기록이 같은 레코드 구조를 쓴다 —
    승인이 먼저 와도(절차 순서: 승인 → 실행) 기록할 곳이 있어야 한다."""
    udir = find_unit_dir(project_root, unit_id)
    edir = udir / "evidence"
    edir.mkdir(exist_ok=True)
    epath = edir / f"{run_name}.yaml"
    if epath.exists():
        return epath, load_yaml(epath)
    fm, _ = frontmatter.read(udir / "spec.md")
    base_sha = fm.get("base_sha") or (head_sha(project_root) if is_repo(project_root) else None)
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
    log_text = mask_secrets(f"$ {command}\n--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}\n--- exit {proc.returncode} ---\n")
    log_path.write_text(log_text, encoding="utf-8")
    cmd_rec = {
        "id": label, "command": mask_secrets(command), "exit_code": proc.returncode,
        "started_at": started, "finished_at": now_iso(), "seconds": elapsed,
        "log": rel(log_path, project_root), "log_sha256": sha256_bytes(log_text.encode("utf-8")),
        "stdout_tail": mask_secrets(proc.stdout[-400:]).strip(),
    }
    rec["commands"].append(cmd_rec)
    state = tree_state(project_root, unit_id, base_sha)
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
    rec.setdefault("approvals", []).append({"guard": guard, "approved_at": now_iso(), "approved_by": by, "note": note})
    path.write_text(dump_yaml(rec), encoding="utf-8")
    return str(path)


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
