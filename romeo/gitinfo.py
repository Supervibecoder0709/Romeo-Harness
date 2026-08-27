"""git 상태 조회. evidence 신선도(C-E1·C-E2)의 근거: HEAD SHA + dirty_tree_hash(계획 §3.5 정의)."""
import hashlib
import subprocess
from pathlib import Path


def _git(args, cwd, check=True):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=check)


def is_repo(cwd):
    try:
        _git(["rev-parse", "--is-inside-work-tree"], cwd)
        return True
    except Exception:
        return False


def head_sha(cwd):
    return _git(["rev-parse", "HEAD"], cwd).stdout.strip()


def untracked_files(cwd):
    out = _git(["ls-files", "--others", "--exclude-standard", "-z"], cwd).stdout
    return sorted(p for p in out.split("\0") if p)


def dirty_tree_hash(cwd):
    """tracked 수정분(git diff) + staged 변경(git diff --cached) + untracked(ignored 제외) 파일의 경로·내용을
    경로 순으로 sha256 한 값. 네 경우(커밋 이동은 head_sha, tracked 수정, staged, untracked 추가) 모두 값이 바뀐다."""
    h = hashlib.sha256()
    h.update(b"--cached\0")
    h.update(_git(["diff", "--cached", "--binary", "--no-color", "--no-ext-diff"], cwd).stdout.encode("utf-8", "surrogateescape"))
    h.update(b"--worktree\0")
    h.update(_git(["diff", "--binary", "--no-color", "--no-ext-diff"], cwd).stdout.encode("utf-8", "surrogateescape"))
    for path in untracked_files(cwd):
        h.update(b"--untracked\0" + path.encode("utf-8") + b"\0")
        p = Path(cwd) / path
        if p.is_file():
            with open(p, "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()


def changed_files(cwd, base_sha=None):
    """base_sha..HEAD 사이 변경 파일 + 작업 트리의 미커밋 변경(수정·staged·untracked). 경로 정렬, 중복 제거."""
    files = set()
    if base_sha:
        try:
            out = _git(["diff", "--name-only", base_sha, "HEAD"], cwd).stdout
            files.update(p for p in out.splitlines() if p)
        except subprocess.CalledProcessError:
            pass
    out = _git(["status", "--porcelain", "-z", "--untracked-files=all"], cwd).stdout
    for entry in out.split("\0"):
        if len(entry) >= 4:
            files.add(entry[3:])
    return sorted(files)


def artifact_hash(cwd, files):
    """변경 파일 내용의 sha256(경로 순). 삭제된 파일은 경로만 반영."""
    h = hashlib.sha256()
    for path in sorted(files):
        h.update(path.encode("utf-8") + b"\0")
        p = Path(cwd) / path
        if p.is_file():
            with open(p, "rb") as fh:
                h.update(fh.read())
        else:
            h.update(b"<deleted>")
        h.update(b"\0")
    return h.hexdigest()


def repo_id(cwd):
    try:
        url = _git(["remote", "get-url", "origin"], cwd).stdout.strip()
        if url:
            return url
    except Exception:
        pass
    return str(Path(cwd).resolve())
