"""romeo CLI — route · card · new · validate · fixtures · approve · evidence · close · id."""
import argparse
import json
import sys
from pathlib import Path

from . import HARNESS_ROOT, __version__
from .util import load_any, project_root as _project_root, dump_yaml


def _root(args):
    return Path(args.root).resolve() if getattr(args, "root", None) else _project_root()


def _load_classification(args):
    if getattr(args, "proposal", None):
        prop = load_any(args.proposal)
        return prop, dict(prop["candidate"])
    data = load_any(args.classification)
    if "candidate" in data:
        return data, dict(data["candidate"])
    return None, data


def cmd_route(args):
    from .fixtures import check_fixtures, format_report, load_fixtures, run_report
    from .policy import RouteError, route
    from .card import render_card
    if args.fixtures:
        fx = load_fixtures(args.fixtures)
        errs = check_fixtures(fx)
        if errs:
            for p, e in errs.items():
                print(f"FIXTURE_INVALID {p}: {'; '.join(e)}", file=sys.stderr)
            return 1
        rep = run_report(fx)
        if args.json:
            print(json.dumps(rep, ensure_ascii=False, indent=1))
        else:
            print(format_report(rep))
        return 0 if rep["match_rate"] >= 0.9 and rep["gate_misses"] == 0 else 1
    proposal, cls = _load_classification(args)
    try:
        out = route(cls)
    except RouteError as e:
        for msg in e.args[0]:
            print(f"ROUTE_ERROR {msg}", file=sys.stderr)
        return 1
    if args.card:
        if not proposal:
            print("--card 는 --proposal 이 필요하다", file=sys.stderr)
            return 2
        print(render_card(proposal, out))
        return 0
    print(json.dumps(out, ensure_ascii=False, indent=1) if args.json else dump_yaml(out))
    return 0


def cmd_card(args):
    from .card import render_card
    from .policy import route
    prop = load_any(args.proposal)
    out = route(prop["candidate"])
    text = render_card(prop, out)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def cmd_new(args):
    from .docs import create_unit
    from .policy import route
    proposal, cls = _load_classification(args)
    out = route(cls)
    title = args.title or (cls.get("title") if cls else None) or (proposal or {}).get("request", {}).get("text", "")[:60]
    slug = args.slug or cls.get("slug") or title
    one_line = args.one_line or (proposal or {}).get("request", {}).get("text", "")[:120] or title
    res = create_unit(out, title, slug, one_line, project_root=_root(args))
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        if res["id"] is None:
            print(f"문서 없음: {res['note']}")
        else:
            print(f"created {res['id']} → {res['dir']}")
            for f in res["files"]:
                print(f"  {f}")
            for s in res["skipped"]:
                print(f"  skipped {s['doc']}: {s['reason']}")
    return 0


def cmd_validate(args):
    from .validate import find_docs, validate_doc
    paths = [Path(p) for p in args.paths] or find_docs(_root(args))
    if not paths:
        print("검사할 문서가 없다")
        return 0
    rc = 0
    for p in paths:
        r = validate_doc(p)
        status = "PASS" if not r["errors"] else "FAIL"
        if r["errors"]:
            rc = 1
        print(f"[{status}] {p} lines={r['info'].get('lines')} needs_input={r['info'].get('needs_input')} unchecked_ac={r['info'].get('unchecked_ac')}")
        for e in r["errors"]:
            print(f"    ERROR {e}")
        for w in r["warnings"]:
            print(f"    WARN  {w}")
    return rc


def cmd_fixtures(args):
    from .fixtures import check_fixtures, format_report, load_fixtures, run_report
    fx = load_fixtures(args.dir)
    errs = check_fixtures(fx)
    if args.action == "check":
        if errs:
            for p, e in errs.items():
                print(f"FAIL {p}: {'; '.join(e)}")
            return 1
        print(f"PASS {len(fx)} fixtures")
        return 0
    if errs:
        for p, e in errs.items():
            print(f"FIXTURE_INVALID {p}: {'; '.join(e)}", file=sys.stderr)
        return 1
    rep = run_report(fx)
    print(json.dumps(rep, ensure_ascii=False, indent=1) if args.json else format_report(rep))
    return 0 if rep["match_rate"] >= 0.9 and rep["gate_misses"] == 0 else 1


def cmd_approve(args):
    from .docs import approve_unit
    fm = approve_unit(args.unit, args.by, project_root=_root(args))
    print(f"approved {fm['id']} at {fm['approved_at']} by {fm['approved_by']} base_sha={fm.get('base_sha')}")
    return 0


def cmd_evidence(args):
    from .evidence import add_approval, run_command
    if args.action == "run":
        command = " ".join(args.command)
        if not command:
            print("실행할 명령이 없다: romeo evidence run --unit ID -- <명령>", file=sys.stderr)
            return 2
        res = run_command(args.unit, command, run_name=args.run, label=args.label, project_root=_root(args))
        c = res["command"]
        print(f"[{'ok' if c['exit_code']==0 else 'exit '+str(c['exit_code'])}] {c['id']}: {c['command']} ({c['seconds']}s) → {res['evidence']}")
        print(f"  head {res['state']['head_sha'][:12]} tree {res['state']['dirty_tree_hash'][:12]} changed {res['state']['changed_files']}")
        return 0 if c["exit_code"] == 0 else 1
    if args.action == "checks":
        from .evidence import run_required_checks
        rc = 0
        for res in run_required_checks(args.unit, run_name=args.run, project_root=_root(args)):
            c = res["command"]
            print(f"[{'ok' if c['exit_code']==0 else 'exit '+str(c['exit_code'])}] {c['id']}: {c['command']} ({c['seconds']}s)")
            rc = rc or (0 if c["exit_code"] == 0 else 1)
        print(f"  → {res['evidence']}  head {res['state']['head_sha'][:12]} changed {res['state']['changed_files']}")
        return rc
    if args.action == "approve":
        path = add_approval(args.unit, args.guard, args.by, note=args.note, run_name=args.run, project_root=_root(args))
        print(f"approval recorded → {path}")
        return 0
    return 2


def cmd_close(args):
    from .close import close_unit, format_close
    res = close_unit(args.unit, project_root=_root(args), dry_run=args.dry_run)
    print(format_close(res))
    return 0 if res["verdict"] == "PASS" else 1


def cmd_id(args):
    from .ids import new_id
    print(new_id(args.unit, args.slug))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="romeo", description="Romeo 하네스 CLI (라우터·문서·증거·종료)")
    p.add_argument("--version", action="version", version=f"romeo {__version__} @ {HARNESS_ROOT}")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("route", help="분류 → 정책표 계산 (또는 fixture 리포트)")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--classification", help="확정된 분류 YAML/JSON")
    g.add_argument("--proposal", help="제안 YAML/JSON (candidate 사용)")
    g.add_argument("--fixtures", help="fixture 디렉터리")
    s.add_argument("--report", action="store_true", help="(fixtures) 리포트 출력")
    s.add_argument("--json", action="store_true")
    s.add_argument("--card", action="store_true", help="(proposal) 카드 렌더링")
    s.set_defaults(fn=cmd_route)

    s = sub.add_parser("card", help="제안 카드 렌더링(≤30줄)")
    s.add_argument("--proposal", required=True)
    s.add_argument("--out")
    s.set_defaults(fn=cmd_card)

    s = sub.add_parser("new", help="docs/work/<id>/ 문서 패키지 생성")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--classification")
    g.add_argument("--proposal")
    s.add_argument("--title")
    s.add_argument("--slug")
    s.add_argument("--one-line", dest="one_line")
    s.add_argument("--root")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_new)

    s = sub.add_parser("validate", help="문서 검증 (경로 생략 시 docs/work 전체)")
    s.add_argument("paths", nargs="*")
    s.add_argument("--root")
    s.set_defaults(fn=cmd_validate)

    s = sub.add_parser("fixtures", help="fixture 검사·리포트")
    s.add_argument("action", choices=["check", "report"])
    s.add_argument("dir", nargs="?", default=str(HARNESS_ROOT / "fixtures/requests"))
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_fixtures)

    s = sub.add_parser("approve", help="승인 사건 기록 (approved_at·base_sha·active)")
    s.add_argument("unit")
    s.add_argument("--by", required=True)
    s.add_argument("--root")
    s.set_defaults(fn=cmd_approve)

    s = sub.add_parser("evidence", help="증거 기록")
    es = s.add_subparsers(dest="action", required=True)
    e_run = es.add_parser("run", help="명령 1개 실행·기록: romeo evidence run --unit ID [--run R] [--label L] -- <명령>")
    e_run.add_argument("--unit", required=True)
    e_run.add_argument("--run")
    e_run.add_argument("--label")
    e_run.add_argument("--root")
    e_run.add_argument("command", nargs=argparse.REMAINDER)
    e_run.set_defaults(fn=cmd_evidence)
    e_chk = es.add_parser("checks", help="spec 의 required_checks 를 문자열 그대로 전부 실행·기록")
    e_chk.add_argument("--unit", required=True)
    e_chk.add_argument("--run")
    e_chk.add_argument("--root")
    e_chk.set_defaults(fn=cmd_evidence)
    e_ap = es.add_parser("approve", help="실행 가드 승인 사건 기록")
    e_ap.add_argument("--unit", required=True)
    e_ap.add_argument("--guard", required=True)
    e_ap.add_argument("--by", required=True)
    e_ap.add_argument("--note")
    e_ap.add_argument("--run")
    e_ap.add_argument("--root")
    e_ap.set_defaults(fn=cmd_evidence)

    s = sub.add_parser("close", help="/plan-close 검사 → status done")
    s.add_argument("--unit", required=True)
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--root")
    s.set_defaults(fn=cmd_close)

    s = sub.add_parser("id", help="ID 생성")
    s.add_argument("--unit", required=True, choices=["T0", "T1", "T2"])
    s.add_argument("--slug", required=True)
    s.set_defaults(fn=cmd_id)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if getattr(args, "command", None) and args.command and args.command[0] == "--":
        args.command = args.command[1:]
    try:
        return args.fn(args) or 0
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
