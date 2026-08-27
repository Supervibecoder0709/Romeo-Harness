"""외부 자산 출처 검증 — provenance/imports.yaml 이 원본이다.

두 가지를 검사한다(계획 §6.2).
1. `vendor/` 파일이 `source_sha` 원문과 같은가 (수정 0). blob SHA 로 대조하므로 네트워크가 필요 없다.
2. 코어 파일 frontmatter 의 `provenance: [id]` 가 imports.yaml 에 있는가.

`THIRD_PARTY_NOTICES.md` 도 이 파일에서 생성한다. 손으로 고치지 않는다.
"""
import hashlib
from pathlib import Path

from .util import load_any, project_root as _project_root

IMPORTS_PATH = "provenance/imports.yaml"
NOTICES_PATH = "THIRD_PARTY_NOTICES.md"

# frontmatter 의 provenance id 를 검사할 대상. vendor/ 는 원문이라 제외한다.
CORE_GLOBS = ("core/**/*.md", "core/**/*.yaml", "adapters/**/*.md", "adapters/**/*.yaml")


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
        for rel, expected in sorted(recorded.items()):
            f = local_root / rel
            checked += 1
            if not f.is_file():
                findings.append(("FILE_MISSING", vid, rel, "기록된 파일이 없다"))
                continue
            actual = blob_sha(f.read_bytes())
            if actual != expected:
                findings.append(("FILE_MODIFIED", vid, rel, f"expected={expected} actual={actual}"))
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
