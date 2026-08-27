"""/plan-close 검사기. 결정적 차단 검사만 실패로 처리하고, 휴리스틱은 경고로 남긴다(C-E3). 검증 상태는 저장하지 않고 여기서 계산한다."""
import re
from pathlib import Path

import yaml

from . import HARNESS_ROOT, frontmatter
from .docs import find_unit_dir
from .evidence import exclusions, dirty_tree_hash_excluding, list_runs
from .gitinfo import head_sha
from .policy import classification_from_frontmatter, load_policy, route
from .util import dump_yaml, load_yaml, now_iso, rel, sha256_file, today
from .validate import UNCHECKED_RE, validate_doc

CHECKS_BLOCK_RE = re.compile(r"```yaml\s*\n(required_checks:.*?)\n```", re.S)


def required_checks(body):
    m = CHECKS_BLOCK_RE.search(body)
    if not m:
        return []
    data = yaml.safe_load(m.group(1)) or {}
    return data.get("required_checks") or []


def close_unit(unit_id, project_root=".", harness_root=None, dry_run=False):
    project_root = Path(project_root).resolve()
    harness_root = Path(harness_root or HARNESS_ROOT)
    pol = load_policy(harness_root)
    udir = find_unit_dir(project_root, unit_id)
    spec = udir / "spec.md"
    fm, body = frontmatter.read(spec)
    checks = []

    def check(cid, ok, detail="", level="error"):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail, "level": level})
        return ok

    v = validate_doc(spec, harness_root)
    check("FRONTMATTER_VALID", not v["errors"], "; ".join(v["errors"]))
    for w in v["warnings"]:
        check("DOC_WARNING", True, w, level="warning")
    if fm.get("status") == "done":
        check("NOT_ALREADY_DONE", False, f"이미 done ({fm.get('closed_at')})")
    check("APPROVED", fm.get("status") == "active" and fm.get("approved_at"), f"status={fm.get('status')} approved_at={fm.get('approved_at')}")
    runs = list_runs(project_root, unit_id)
    if not check("HAS_EVIDENCE", bool(runs), "evidence/*.yaml 없음 — romeo evidence run 으로 만든다"):
        return _finish(checks, fm, body, spec, runs, dry_run, project_root)
    ev = runs[-1]
    cur_head = head_sha(project_root)
    cur_dirty = dirty_tree_hash_excluding(project_root, exclusions(unit_id))
    check("FRESH_HEAD", ev.get("head_sha") == cur_head, f"evidence {str(ev.get('head_sha'))[:12]} vs 현재 {cur_head[:12]}")
    check("FRESH_TREE", ev.get("dirty_tree_hash") == cur_dirty, f"evidence {str(ev.get('dirty_tree_hash'))[:12]} vs 현재 {cur_dirty[:12]} (tracked 수정·staged·untracked 포함)")
    cmds = {c["command"]: c for c in ev.get("commands", [])}
    for rc in required_checks(body):
        cmd = rc.get("command", "")
        rec = cmds.get(cmd)
        if rec is None:
            check("REQUIRED_CHECK", False, f"{rc.get('id')}: evidence 에 명령 없음 — {cmd}")
        else:
            check("REQUIRED_CHECK", rec["exit_code"] == 0, f"{rc.get('id')}: exit {rec['exit_code']} — {cmd}")
    check("AC_ALL_CHECKED", not UNCHECKED_RE.search(body), f"미체크 {len(UNCHECKED_RE.findall(body))}개")
    check("NO_OPEN_LOOP", "NEEDS_INPUT" not in body, f"NEEDS_INPUT {body.count('NEEDS_INPUT')}곳")
    check("HAS_CHANGE", bool(ev.get("changed_files")), "changed_files 가 비어 있다 — 아무것도 바뀌지 않았다면 done 이 아니다")
    spec_sha = sha256_file(spec)
    check("SPEC_UNCHANGED_SINCE_EVIDENCE", (ev.get("spec_ref") or {}).get("sha256") == spec_sha, "spec.md 가 evidence 이후 바뀜(AC 체크 등). 확인만.", level="warning")
    out = route(classification_from_frontmatter(fm), pol)
    if out["reviewer"] != "none":
        review_dir = udir / "review"
        check("HAS_REVIEW", review_dir.is_dir() and any(review_dir.iterdir()), "검토자가 필요한 패키지인데 review/ 가 비어 있다(M2)")
    for g in out["guards"]:
        approved = any(a.get("guard") == g["id"] for r in runs for a in r.get("approvals", []))
        check("GUARD_APPROVED", approved, f"{g['id']} ({g['name']}) 승인 기록 없음")
    return _finish(checks, fm, body, spec, runs, dry_run, project_root)


def _finish(checks, fm, body, spec, runs, dry_run, project_root):
    failed = [c for c in checks if c["level"] == "error" and not c["ok"]]
    verdict = "PASS" if not failed else "FAIL"
    result = {"unit_id": fm.get("id"), "verdict": verdict, "checks": checks, "dry_run": dry_run, "updated": []}
    if verdict == "PASS" and not dry_run:
        ev_links = [rel(r["_path"], spec.parent) for r in runs]
        fm["status"] = "done"
        fm["closed_at"] = now_iso()
        fm["evidence"] = ev_links
        fm["updated"] = today()
        lines = body.split("\n")
        try:
            i = next(k for k, ln in enumerate(lines) if ln.strip() == "## 증거")
            j = i + 1
            while j < len(lines) and not lines[j].startswith("## "):
                j += 1
            block = ["", f"close PASS · {fm['closed_at']} · HEAD {runs[-1].get('head_sha', '')[:12]}", ""] + [f"- [{p}]({p}) — exit codes {[c['exit_code'] for c in r.get('commands', [])]}" for p, r in zip(ev_links, runs)] + [""]
            lines[i + 1:j] = block
            body = "\n".join(lines)
        except StopIteration:
            pass
        frontmatter.write(spec, fm, body)
        result["updated"].append(str(spec))
        last = runs[-1]
        path = last.pop("_path")
        last["verdict"] = "PASS"
        last["close"] = {"at": fm["closed_at"], "checks": [{"id": c["id"], "ok": c["ok"], "detail": c["detail"]} for c in checks]}
        Path(path).write_text(dump_yaml(last), encoding="utf-8")
        result["updated"].append(path)
    return result


def format_close(result):
    lines = [f"romeo close {result['unit_id']} → {result['verdict']}" + (" (dry-run)" if result["dry_run"] else "")]
    for c in result["checks"]:
        mark = "PASS" if c["ok"] else ("WARN" if c["level"] == "warning" else "FAIL")
        lines.append(f"  [{mark}] {c['id']}" + (f" — {c['detail']}" if c["detail"] else ""))
    for u in result["updated"]:
        lines.append(f"  updated: {u}")
    return "\n".join(lines)
