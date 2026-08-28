"""외부 자산 출처 검증 — provenance/imports.yaml 이 원본이다.

두 가지를 검사한다(계획 §6.2).
1. `vendor/` 파일이 **채택 시점에 기록한 blob SHA** 와 같은가 (수정 0). 네트워크가 필요 없다.
   한계: 이것은 upstream 재조회가 아니라 **로컬 자기일관성 검사**다 — vendor 파일과 manifest 해시를
   같은 변경에서 함께 바꾸면 통과한다(Codex 리뷰 F-07). upstream 고정 커밋과의 대조는 채택 게이트와
   업데이트 시점에 사람이 수행하고 그 증거를 남긴다.
2. 코어 파일 frontmatter 의 `provenance: [id]` 가 imports.yaml 에 있는가.

`THIRD_PARTY_NOTICES.md` 도 이 파일에서 생성한다. 손으로 고치지 않는다.
"""
import hashlib
import json
import os
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .util import load_any, now_iso, project_root as _project_root

IMPORTS_PATH = "provenance/imports.yaml"
NOTICES_PATH = "THIRD_PARTY_NOTICES.md"
UPSTREAM_EVIDENCE_PATH = "provenance/upstream-verification.json"
GITHUB_API = "https://api.github.com"

# frontmatter 의 provenance id 를 검사할 대상. vendor/ 는 원문이라 제외한다.
CORE_GLOBS = ("core/**/*.md", "core/**/*.yaml", "adapters/**/*.md", "adapters/**/*.yaml")


class UpstreamVerificationError(RuntimeError):
    """upstream 을 완전하게 확인하지 못했으므로 PASS 로 간주할 수 없다."""


def blob_sha(data: bytes) -> str:
    """git 오브젝트 해시. upstream tree API 의 blob sha 와 같은 값이다."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_imports(root=None):
    root = Path(root) if root else _project_root()
    path = root / IMPORTS_PATH
    if not path.exists():
        return root, {"vendors": [], "imports": []}
    data = load_any(path) or {}
    data.setdefault("vendors", [])
    data.setdefault("imports", [])
    return root, data


def fetch_github_tree(source_repo, source_sha, timeout=30):
    """GitHub Git Trees API 에서 고정 commit 의 recursive tree 를 조회한다."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source_repo or ""):
        raise UpstreamVerificationError(f"잘못된 GitHub 저장소 이름: {source_repo!r}")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", source_sha or ""):
        raise UpstreamVerificationError(f"고정 commit SHA 가 40자리 hex 가 아니다: {source_sha!r}")
    repo = urllib.parse.quote(source_repo, safe="/")
    sha = urllib.parse.quote(source_sha, safe="")
    url = f"{GITHUB_API}/repos/{repo}/git/trees/{sha}?recursive=1"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "romeo-harness-upstream-verifier",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        remaining = exc.headers.get("X-RateLimit-Remaining", "?") if exc.headers else "?"
        reset = exc.headers.get("X-RateLimit-Reset", "?") if exc.headers else "?"
        detail = ""
        try:
            payload = json.loads(exc.read().decode("utf-8"))
            detail = str(payload.get("message") or "")
        except Exception:
            pass
        raise UpstreamVerificationError(
            f"GitHub tree 조회 실패 HTTP {exc.code} ({source_repo}@{source_sha}); "
            f"rate_remaining={remaining} rate_reset={reset} {detail}".rstrip()) from exc
    except urllib.error.URLError as exc:
        raise UpstreamVerificationError(
            f"GitHub tree 네트워크 실패 ({source_repo}@{source_sha}): {exc.reason}") from exc
    except OSError as exc:
        raise UpstreamVerificationError(
            f"GitHub tree 조회 실패 ({source_repo}@{source_sha}): {exc}") from exc
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise UpstreamVerificationError(
            f"GitHub tree 응답이 올바른 JSON 이 아니다 ({source_repo}@{source_sha}): {exc}") from exc
    return payload


def parse_upstream_tree(payload):
    """GitHub 응답을 path → blob/mode/type 으로 정규화한다. 네트워크 호출은 하지 않는다."""
    if not isinstance(payload, dict):
        raise UpstreamVerificationError("GitHub tree 응답 최상위가 object 가 아니다")
    if payload.get("truncated") is not False:
        raise UpstreamVerificationError("GitHub tree 응답이 잘렸거나 truncated 상태를 확인할 수 없다")
    tree_sha = payload.get("sha")
    if not isinstance(tree_sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", tree_sha):
        raise UpstreamVerificationError("GitHub tree 응답의 tree sha 가 올바르지 않다")
    tree = payload.get("tree")
    if not isinstance(tree, list):
        raise UpstreamVerificationError("GitHub tree 응답의 tree 가 목록이 아니다")
    entries = {}
    for index, item in enumerate(tree):
        if not isinstance(item, dict):
            raise UpstreamVerificationError(f"GitHub tree[{index}] 가 object 가 아니다")
        path = item.get("path")
        mode = str(item.get("mode") or "")
        kind = item.get("type")
        sha = item.get("sha")
        if (not isinstance(path, str) or not path or path.startswith("/")
                or ".." in Path(path).parts):
            raise UpstreamVerificationError(f"GitHub tree[{index}] path 가 올바르지 않다")
        if path in entries:
            raise UpstreamVerificationError(f"GitHub tree 에 중복 path 가 있다: {path}")
        if not re.fullmatch(r"[0-7]{6}", mode):
            raise UpstreamVerificationError(f"GitHub tree mode 가 올바르지 않다: {path}={mode!r}")
        if kind not in ("blob", "tree", "commit"):
            raise UpstreamVerificationError(f"GitHub tree type 이 올바르지 않다: {path}={kind!r}")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
            raise UpstreamVerificationError(f"GitHub tree sha 가 올바르지 않다: {path}")
        entries[path] = {"mode": mode, "type": kind, "sha": sha.lower()}
    return {"tree_sha": tree_sha.lower(), "entries": entries}


def compare_vendor_to_upstream(vendor, entries):
    """manifest 의 선택 파일 blob·mode 를 정규화된 upstream tree 와 대조한다."""
    vid = vendor.get("id", "?")
    files = vendor.get("files")
    modes = vendor.get("modes")
    if not isinstance(files, dict) or not isinstance(modes, dict):
        raise UpstreamVerificationError(f"{vid}: imports.yaml files·modes 는 mapping 이어야 한다")
    findings = []
    comparisons = []
    for rel, expected_sha in sorted(files.items()):
        expected_mode = str(modes.get(rel)) if rel in modes else None
        upstream = entries.get(rel)
        item_findings = []
        if expected_mode is None:
            item_findings.append(("MANIFEST_MODE_MISSING", vid, rel,
                                  "imports.yaml modes 에 파일 mode 가 없다"))
        if upstream is None:
            item_findings.append(("UPSTREAM_FILE_MISSING", vid, rel,
                                  f"고정 commit {vendor.get('source_sha')} tree 에 없다"))
            actual_sha = actual_mode = actual_type = None
        else:
            actual_sha = upstream["sha"]
            actual_mode = upstream["mode"]
            actual_type = upstream["type"]
            if actual_type != "blob":
                item_findings.append(("UPSTREAM_TYPE_MISMATCH", vid, rel,
                                      f"expected=blob actual={actual_type}"))
            if str(expected_sha).lower() != actual_sha:
                item_findings.append(("UPSTREAM_BLOB_MISMATCH", vid, rel,
                                      f"expected={expected_sha} actual={actual_sha}"))
            if expected_mode is not None and expected_mode != actual_mode:
                item_findings.append(("UPSTREAM_MODE_MISMATCH", vid, rel,
                                      f"expected={expected_mode} actual={actual_mode}"))
        findings.extend(item_findings)
        comparisons.append({
            "path": rel,
            "expected_blob": str(expected_sha).lower(),
            "actual_blob": actual_sha,
            "expected_mode": expected_mode,
            "actual_mode": actual_mode,
            "actual_type": actual_type,
            "result": "FAIL" if item_findings else "PASS",
        })
    for rel in sorted(set(modes) - set(files)):
        findings.append(("MANIFEST_MODE_ORPHAN", vid, rel,
                         "imports.yaml files 에 없는 mode 기록이다"))
    return findings, comparisons


def _write_upstream_evidence(root: Path, evidence):
    path = root / UPSTREAM_EVIDENCE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent),
                                         prefix=".upstream-", suffix=".json", delete=False) as fh:
            json.dump(evidence, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
            temp_name = fh.name
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)
    return path


def verify_upstream(root=None, fetcher=None, verified_at=None):
    """모든 vendor manifest 를 고정 upstream tree 와 대조하고 감사 증거를 남긴다."""
    root, data = load_imports(root)
    fetcher = fetcher or fetch_github_tree
    evidence = {
        "schema_version": 1,
        "command": "romeo vendor verify-upstream",
        "provider": "GitHub Git Trees API",
        "verified_at": verified_at or now_iso(),
        "status": "PASS",
        "vendors": [],
    }
    findings = []
    for vendor in data["vendors"]:
        record = {
            "id": vendor.get("id", "?"),
            "source_repo": vendor.get("source_repo"),
            "source_sha": vendor.get("source_sha"),
            "result": "UNVERIFIED",
            "comparisons": [],
        }
        evidence["vendors"].append(record)
        try:
            payload = fetcher(vendor.get("source_repo"), vendor.get("source_sha"))
            parsed = parse_upstream_tree(payload)
            vendor_findings, comparisons = compare_vendor_to_upstream(vendor, parsed["entries"])
            record["tree_sha"] = parsed["tree_sha"]
            record["comparisons"] = comparisons
            record["result"] = "FAIL" if vendor_findings else "PASS"
            findings.extend(vendor_findings)
        except Exception as exc:
            record["error"] = str(exc)
            evidence["status"] = "ERROR"
            try:
                _write_upstream_evidence(root, evidence)
            except OSError as write_exc:
                raise UpstreamVerificationError(
                    f"upstream 확인 실패 후 증거 기록도 실패했다: {exc}; evidence={write_exc}") from write_exc
            raise UpstreamVerificationError(
                f"{record['id']} upstream 을 확인하지 못했다; PASS 아님: {exc}; "
                f"evidence={UPSTREAM_EVIDENCE_PATH}") from exc
    if findings:
        evidence["status"] = "FAIL"
    evidence["counts"] = {
        "vendors": len(evidence["vendors"]),
        "files": sum(len(item["comparisons"]) for item in evidence["vendors"]),
        "findings": len(findings),
    }
    try:
        _write_upstream_evidence(root, evidence)
    except OSError as exc:
        raise UpstreamVerificationError(f"upstream 증거를 기록하지 못했다: {exc}") from exc
    return findings, evidence


def check_vendor(root=None):
    """vendor/ 트리를 imports.yaml 의 files 해시와 대조한다. (findings, counts) 반환."""
    root, data = load_imports(root)
    findings = []
    checked = 0
    for vendor in data["vendors"]:
        vid = vendor.get("id", "?")
        local_root = root / vendor["local_root"]
        recorded = vendor.get("files") or {}
        if not local_root.exists():
            findings.append(("VENDOR_MISSING", vid, vendor["local_root"], "디렉터리가 없다"))
            continue
        modes = vendor.get("modes") or {}
        for rel, expected in sorted(recorded.items()):
            f = local_root / rel
            checked += 1
            if f.is_symlink():
                # 링크가 가리키는 내용이 맞아도 통과시키지 않는다 — 외부 파일 의존이자 Windows 이식성 문제다.
                findings.append(("FILE_SYMLINK", vid, rel, "심링크다 — vendor 는 실제 파일이어야 한다"))
                continue
            if not f.is_file():
                findings.append(("FILE_MISSING", vid, rel, "기록된 파일이 없다"))
                continue
            actual = blob_sha(f.read_bytes())
            if actual != expected:
                findings.append(("FILE_MODIFIED", vid, rel, f"expected={expected} actual={actual}"))
            # YAML 은 100755 를 정수로 읽는다. 문자열로 맞춰 비교한다.
            want_exec = str(modes.get(rel, "100644")) == "100755"
            is_exec = bool(f.stat().st_mode & 0o111)
            if want_exec != is_exec:
                findings.append(("FILE_MODE", vid, rel,
                                 f"실행 비트가 원문과 다르다 (기록={modes.get(rel, '100644')}, 실제={'실행가능' if is_exec else '일반'})"))
        on_disk = {str(f.relative_to(local_root)) for f in local_root.rglob("*") if f.is_file()}
        for extra in sorted(on_disk - set(recorded)):
            findings.append(("FILE_UNTRACKED", vid, extra, "imports.yaml 에 없는 파일이다"))
        lic = vendor.get("license_file")
        if lic and lic not in recorded:
            findings.append(("LICENSE_MISSING", vid, lic, "라이선스 사본이 files 에 없다"))
    return findings, {"vendors": len(data["vendors"]), "files": checked}


def check_provenance_ids(root=None):
    """코어 파일 frontmatter 의 provenance id 가 imports.yaml 에 있는지 본다."""
    from . import frontmatter as fm

    root, data = load_imports(root)
    known = {item.get("id") for item in data["imports"]}
    findings = []
    seen = 0
    for pattern in CORE_GLOBS:
        for f in sorted(root.glob(pattern)):
            try:
                meta, _ = fm.split(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not meta:
                continue
            ids = meta.get("provenance")
            if not ids:
                continue
            seen += 1
            for pid in ids if isinstance(ids, list) else [ids]:
                if pid not in known:
                    findings.append(("PROVENANCE_UNKNOWN", str(f.relative_to(root)), pid,
                                     "imports.yaml 에 없는 id"))
    return findings, {"files_with_provenance": seen}


def render_notices(root=None):
    """imports.yaml → THIRD_PARTY_NOTICES.md 본문."""
    root, data = load_imports(root)
    vendors = {v["id"]: v for v in data["vendors"]}
    out = [
        "# 제3자 고지 (THIRD PARTY NOTICES)",
        "",
        "이 파일은 `provenance/imports.yaml` 에서 생성한다. **직접 고치지 않는다** —",
        "`romeo notices` 로 다시 만들고, `romeo notices --check` 가 CI 에서 대조한다.",
        "",
        "이 저장소 자체는 Apache-2.0 이다(`LICENSE`, D-41). 아래는 그와 별개로,",
        "원문을 그대로 담았거나(`verbatim`) 원칙만 가져온(`principle`) 외부 자산의 출처다.",
        "",
    ]

    verbatim = [i for i in data["imports"]
                if i.get("status") == "accepted" and i.get("adoption") == "verbatim"]
    if verbatim:
        out += ["## 원문 포함 (verbatim — 수정 0)", ""]
        by_vendor = {}
        for item in verbatim:
            local = item.get("local_path") or ""
            vid = next((v["id"] for v in data["vendors"]
                        if local.startswith(v["local_root"])), None)
            by_vendor.setdefault(vid, []).append(item)
        for vid, items in by_vendor.items():
            v = vendors.get(vid, {})
            out += [
                f"### {v.get('source_repo', vid)}",
                "",
                f"- 출처: `https://github.com/{v.get('source_repo', vid)}`",
                f"- 고정 커밋: `{v.get('source_sha', '?')}`",
                f"- 라이선스: **{v.get('license', '?')}** (사본: `{v.get('local_root','')}/"
                f"{v.get('license_file','LICENSE')}`, 확인일 {v.get('license_verified_at','?')})",
                f"- 로컬 경로: `{v.get('local_root','')}/`",
                f"- 채택 게이트: {v.get('gate','?')}",
                "",
                "| 채택 id | 원문 경로 | 로컬 override |",
                "| --- | --- | --- |",
            ]
            for item in sorted(items, key=lambda x: x["id"]):
                paths = item.get("source_path") or []
                ov = item.get("local_overrides") or []
                ov_text = "없음" if not ov else "; ".join(o.get("target", "?") for o in ov)
                out.append(f"| `{item['id']}` | " + "<br>".join(f"`{p}`" for p in paths)
                           + f" | {ov_text} |")
            out.append("")

    principle = [i for i in data["imports"]
                 if i.get("status") == "accepted" and i.get("adoption") == "principle"]
    if principle:
        out += ["## 원칙 채택 (principle — 재작성, 원문 복사 아님)", "",
                "| 채택 id | 출처 | 반영 위치 |", "| --- | --- | --- |"]
        for item in sorted(principle, key=lambda x: x["id"]):
            src = f"{item.get('source_repo','?')} `{(item.get('source_sha') or '')[:7]}`"
            out.append(f"| `{item['id']}` | {src} | `{item.get('local_path','-')}` |")
        out.append("")

    deferred = [i for i in data["imports"] if i.get("status") in ("deferred", "rejected")]
    if deferred:
        out += ["## 채택하지 않은 후보", "",
                "저장소에 파일이 없다. 재검토 이력을 남기기 위해 적는다.", "",
                "| 후보 id | 상태 | 게이트 |", "| --- | --- | --- |"]
        for item in sorted(deferred, key=lambda x: (x.get("status"), x["id"])):
            out.append(f"| `{item['id']}` | {item.get('status')} | {item.get('gate','-')} |")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def write_notices(root=None):
    root = Path(root) if root else _project_root()
    text = render_notices(root)
    (root / NOTICES_PATH).write_text(text, encoding="utf-8")
    return text


def check_notices(root=None):
    """디스크의 THIRD_PARTY_NOTICES.md 가 imports.yaml 과 일치하는지."""
    root = Path(root) if root else _project_root()
    path = root / NOTICES_PATH
    expected = render_notices(root)
    if not path.exists():
        return [("NOTICES_MISSING", NOTICES_PATH, "", "생성되지 않았다")]
    if path.read_text(encoding="utf-8") != expected:
        return [("NOTICES_STALE", NOTICES_PATH, "", "imports.yaml 과 다르다 — `romeo notices` 로 재생성")]
    return []
