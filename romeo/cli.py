"""romeo CLI — route · card · new · validate · fixtures(check·report·parity) · approve · evidence · envelope · review · close · id · compile · doctor · vendor · notices."""
import argparse
import json
import sys
from pathlib import Path

from . import HARNESS_ROOT, __version__
from .evidence import RERUN_TIMEOUT
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
    from .policy import RouteError, load_project_state, route
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
        out = route(cls, project_state=load_project_state(_root(args)))
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
    from .policy import load_project_state, route
    prop = load_any(args.proposal)
    out = route(prop["candidate"], project_state=load_project_state(_root(args)))
    text = render_card(prop, out)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def cmd_new(args):
    from .docs import create_unit
    from .policy import load_project_state, route
    proposal, cls = _load_classification(args)
    out = route(cls, project_state=load_project_state(_root(args)))
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
    if args.action == "parity":
        from .parity import check_parity_cases, format_parity, load_parity_cases, run_parity
        cases = load_parity_cases(args.dir or str(HARNESS_ROOT / "fixtures/parity"))
        root = _root(args) if getattr(args, "root", None) else None
        errs = check_parity_cases(cases, harness_root=root)
        if errs:
            for p, e in errs.items():
                print(f"PARITY_INVALID {p}: {'; '.join(e)}", file=sys.stderr)
            return 1
        rep = run_parity(cases, harness_root=root, judge_mode=getattr(args, "judge_verdict", None))
        print(json.dumps(rep, ensure_ascii=False, indent=1) if args.json else format_parity(rep))
        # 판정은 두 층이다(D-b). 검사기가 옳은지 확인하지 못한 실행은 게이트 통과를 주장할 수 없다 —
        # '해당 없음'(합성 0건)을 0 으로 접으면 아무것도 확인하지 않은 실행이 성공으로 읽힌다(K-51).
        return 0 if rep["gate_verdict"] == "PASS" and rep["checker_verdict"] == "PASS" else 1
    from .fixtures import check_fixtures, format_report, load_fixtures, run_report
    fx = load_fixtures(args.dir or str(HARNESS_ROOT / "fixtures/requests"))
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
    fm = approve_unit(args.unit, args.by, project_root=_root(args), reapprove=args.reapprove, reason=args.reason)
    what = "reapproved" if args.reapprove else "approved"
    print(f"{what} {fm['id']} at {fm['approved_at']} by {fm['approved_by']}"
          + (f" (이전 승인 {len(fm['approval_history'])}건은 approval_history 에 남았다)" if args.reapprove else ""))
    print("  다음: 승인된 spec.md 를 커밋한다. 위임된 실행 공간은 커밋된 것만 본다(D-a). "
          "base_sha 는 적지 않았다 — 그 커밋의 SHA 가 base_sha 이고, "
          f"romeo envelope build --unit {fm['id']} --role implementer 는 --base-sha 를 생략하면 이력에서 승인 커밋을 스스로 찾는다")
    return 0


def cmd_evidence(args):
    from .evidence import add_approval, run_command
    ids = {"task_id": args.task_id, "dispatch_id": args.dispatch_id}
    if args.action == "run":
        command = " ".join(args.command)
        if not command:
            print("실행할 명령이 없다: romeo evidence run --unit ID -- <명령>", file=sys.stderr)
            return 2
        res = run_command(args.unit, command, run_name=args.run, label=args.label, project_root=_root(args), **ids)
        c = res["command"]
        print(f"[{'ok' if c['exit_code']==0 else 'exit '+str(c['exit_code'])}] {c['id']}: {c['command']} ({c['seconds']}s) → {res['evidence']}")
        print(f"  head {res['state']['head_sha'][:12]} tree {res['state']['dirty_tree_hash'][:12]} changed {res['state']['changed_files']}")
        return 0 if c["exit_code"] == 0 else 1
    if args.action == "checks":
        from .evidence import run_required_checks
        results = run_required_checks(args.unit, run_name=args.run, project_root=_root(args), **ids)
        if not results:
            # 실행할 것이 없다는 것은 성공이 아니다. 무엇이 없는지 말하고 비0 으로 끝낸다 — 조건 없이 부르는 명령이다.
            print(f"{args.unit}: spec.md 의 검증 계획에 required_checks 가 없다 — 실행할 검사가 하나도 없다. "
                  "검증 계획의 required_checks 블록을 채운 뒤 다시 실행한다.", file=sys.stderr)
            return 2
        rc = 0
        for res in results:
            c = res["command"]
            print(f"[{'ok' if c['exit_code']==0 else 'exit '+str(c['exit_code'])}] {c['id']}: {c['command']} ({c['seconds']}s)")
            rc = rc or (0 if c["exit_code"] == 0 else 1)
        print(f"  → {res['evidence']}  head {res['state']['head_sha'][:12]} changed {res['state']['changed_files']}")
        return rc
    if args.action == "approve":
        path = add_approval(args.unit, args.guard, args.by, note=args.note, run_name=args.run,
                            project_root=_root(args), **ids)
        print(f"approval recorded → {path}")
        return 0
    return 2


def cmd_envelope(args):
    if args.action == "check":
        from .envelope import check_result_envelope, format_result_check
        results = [check_result_envelope(p, args.unit, role=args.role, project_root=_root(args))
                   for p in args.paths]
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=1))
        else:
            for res in results:
                print(format_result_check(res))
        verdicts = {r["verdict"] for r in results}
        # 검사 불가(2)를 통과(0)로 접지 않는다 — 대조하지 못한 것은 통과가 아니다(K-51).
        return 1 if "FAIL" in verdicts else (2 if "UNVERIFIED" in verdicts else 0)
    from .envelope import write_envelope
    res = write_envelope(args.unit, args.role, project_root=_root(args),
                         base_sha=args.base_sha, run_name=args.run)
    env = res["envelope"]
    if args.json:
        print(json.dumps(env, ensure_ascii=False, indent=1))
    else:
        print(f"built {env['role']} 계약 → {res['path']}")
        print(f"  base_sha {env['base_sha'][:12]} · spec {env['spec_ref']['sha256'][:12]} "
              f"· 계약 sha256 {res['sha256'][:12]} · workspace {env['workspace']} "
              f"· guards {[g['id'] for g in env['guards']]} · required_checks {len(env['required_checks'])}건")
    return 0


def cmd_review(args):
    from .evidence import record_review_envelope
    res = record_review_envelope(args.unit, args.run, args.source, project_root=_root(args))
    c = res["command"]
    print(f"recorded → {res['path']} (sha256 {res['sha256'][:12]}) · evidence {res['evidence']} · "
          f"{c['id']} exit {c['exit_code']}")
    print("  다음: romeo envelope check --unit <id> --role reviewer <그 파일> 로 앵커 5개를 본다")
    return 0 if c["exit_code"] == 0 else 1


def cmd_close(args):
    from .close import close_unit, format_close
    res = close_unit(args.unit, project_root=_root(args), dry_run=args.dry_run,
                     rerun=not args.no_rerun, rerun_timeout=args.rerun_timeout)
    print(format_close(res))
    return 0 if res["verdict"] == "PASS" else 1


def cmd_id(args):
    from .ids import new_id
    print(new_id(args.unit, args.slug))
    return 0


def cmd_compile(args):
    from .compile import check_compiled, compile_all
    root = _root(args)
    if args.check:
        findings = check_compiled(root)
        for code, path, _, why in findings:
            print(f"{code} {path} — {why}", file=sys.stderr)
        print(f"compile 검사 {'PASS' if not findings else f'FAIL ({len(findings)}건)'}")
        return 0 if not findings else 1
    written = compile_all(root)
    if args.json:
        print(json.dumps({"outputs": written}, ensure_ascii=False, indent=1))
    else:
        for rel in written:
            print(f"  {rel}")
        print(f"compile 완료 · 산출물 {len(written)}개")
    return 0


def cmd_doctor(args):
    from .doctor import doctor, doctor_problem_count, format_report
    rep = doctor(_root(args))
    print(json.dumps(rep, ensure_ascii=False, indent=1) if args.json else format_report(rep))
    if args.strict:
        return 0 if doctor_problem_count(rep, args.scope) == 0 else 1
    return 0


def cmd_vendor(args):
    from .provenance import (UPSTREAM_EVIDENCE_PATH, check_vendor, check_provenance_ids,
                             verify_upstream)
    root = _root(args)
    if args.action == "verify-upstream":
        findings, evidence = verify_upstream(root)
        if args.json:
            print(json.dumps(evidence, ensure_ascii=False, indent=1))
        else:
            for code, who, what, why in findings:
                print(f"{code} {who} :: {what} — {why}", file=sys.stderr)
            status = evidence["status"]
            counts = evidence["counts"]
            commits = ", ".join(
                f"{item['source_repo']}@{item['source_sha']}" for item in evidence["vendors"])
            print(f"upstream 검증 {status} · vendors={counts['vendors']} files={counts['files']} "
                  f"findings={counts['findings']} · commits={commits} · "
                  f"evidence={UPSTREAM_EVIDENCE_PATH}")
        return 0 if not findings else 1

    findings, counts = check_vendor(root)
    id_findings, id_counts = check_provenance_ids(root)
    findings = findings + id_findings
    if args.json:
        print(json.dumps({"findings": [list(f) for f in findings],
                          "counts": {**counts, **id_counts}}, ensure_ascii=False, indent=1))
    else:
        for code, who, what, why in findings:
            print(f"{code} {who} :: {what} — {why}", file=sys.stderr)
        status = "PASS" if not findings else f"FAIL ({len(findings)}건)"
        print(f"vendor 검증 {status} · vendors={counts['vendors']} files={counts['files']} "
              f"(수정 0 대조) · provenance id 를 쓴 코어 파일 {id_counts['files_with_provenance']}개")
    return 0 if not findings else 1


def cmd_notices(args):
    from .provenance import check_notices, write_notices, NOTICES_PATH
    root = _root(args)
    if args.check:
        findings = check_notices(root)
        for code, path, _, why in findings:
            print(f"{code} {path} — {why}", file=sys.stderr)
        if not findings:
            print(f"{NOTICES_PATH} 는 imports.yaml 과 일치한다")
        return 0 if not findings else 1
    write_notices(root)
    print(f"{NOTICES_PATH} 생성")
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
    s.add_argument("--root", help="부착 상태(.harness/romeo.project.yaml)를 찾을 프로젝트 루트")
    s.set_defaults(fn=cmd_route)

    s = sub.add_parser("card", help="제안 카드 렌더링(≤30줄)")
    s.add_argument("--proposal", required=True)
    s.add_argument("--out")
    s.add_argument("--root", help="부착 상태(.harness/romeo.project.yaml)를 찾을 프로젝트 루트")
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

    s = sub.add_parser("fixtures", help="fixture 검사·리포트·동등성 판정")
    s.add_argument("action", choices=["check", "report", "parity"])
    s.add_argument("dir", nargs="?", default=None,
                   help="생략 시 check·report 는 fixtures/requests, parity 는 fixtures/parity")
    s.add_argument("--report", action="store_true", help="(parity) 리포트 출력 — parity 는 기본이 리포트다")
    s.add_argument("--root", help="(parity) 결과 계약 스키마를 찾을 루트")
    s.add_argument("--judge-verdict", choices=["advisory", "strict"], default=None,
                   help="(parity) 판정 역할의 판정을 다루는 방식 — 기본 advisory(D-76: 인쇄만), strict 는 D-73·D-74 결박(Q-10 실험용)")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_fixtures)

    s = sub.add_parser("approve", help="승인 사건 기록 (approved_at·active). base_sha 는 적지 않는다 — 승인 커밋은 이력에서 찾는다")
    s.add_argument("unit")
    s.add_argument("--by", required=True)
    s.add_argument("--reapprove", action="store_true",
                   help="이미 승인된 spec 을 다시 승인한다(검증 계획·확인란 변경). 이전 승인은 approval_history 에 남는다")
    s.add_argument("--reason", help="(--reapprove) 무엇이 바뀌어 다시 승인하는지")
    s.add_argument("--root")
    s.set_defaults(fn=cmd_approve)

    s = sub.add_parser("evidence", help="증거 기록")
    es = s.add_subparsers(dest="action", required=True)

    def _delegation_flags(sp):
        """위임 식별자(계획 §3.5 상태 계약). 한 run 은 한 위임에 속한다 — 값은 run 당 한 번만 기록된다."""
        sp.add_argument("--task-id", dest="task_id", help="위임 작업 id (오케스트레이터가 만든 값)")
        sp.add_argument("--dispatch-id", dest="dispatch_id", help="위임 dispatch id (오케스트레이터가 만든 값)")

    e_run = es.add_parser("run", help="명령 1개 실행·기록: romeo evidence run --unit ID [--run R] [--label L] -- <명령>")
    e_run.add_argument("--unit", required=True)
    e_run.add_argument("--run", help="evidence 파일 이름이자 run_id. 위임 실행이면 오케스트레이터 Run id 를 그대로 쓴다")
    e_run.add_argument("--label")
    _delegation_flags(e_run)
    e_run.add_argument("--root")
    e_run.add_argument("command", nargs=argparse.REMAINDER)
    e_run.set_defaults(fn=cmd_evidence)
    e_chk = es.add_parser("checks", help="spec 의 required_checks 를 문자열 그대로 전부 실행·기록")
    e_chk.add_argument("--unit", required=True)
    e_chk.add_argument("--run")
    _delegation_flags(e_chk)
    e_chk.add_argument("--root")
    e_chk.set_defaults(fn=cmd_evidence)
    e_ap = es.add_parser("approve", help="실행 가드 승인 사건 기록 (선행 run 이 없으면 승인 전용 레코드를 만든다)")
    e_ap.add_argument("--unit", required=True)
    e_ap.add_argument("--guard", required=True)
    e_ap.add_argument("--by", required=True)
    e_ap.add_argument("--note")
    e_ap.add_argument("--run")
    _delegation_flags(e_ap)
    e_ap.add_argument("--root")
    e_ap.set_defaults(fn=cmd_evidence)

    s = sub.add_parser("envelope", help="작업 계약(TaskEnvelope) 생성 · 결과 계약(ResultEnvelope) 검증")
    vs = s.add_subparsers(dest="action", required=True)
    v_b = vs.add_parser("build", help="docs/work/<id>/task/[<run>-]<role>.json 을 만든다. 같은 입력이면 같은 계약이다")
    v_b.add_argument("--unit", required=True)
    v_b.add_argument("--role", required=True, choices=["implementer", "reviewer"])
    v_b.add_argument("--base-sha", dest="base_sha",
                     help="승인된 spec.md 가 들어 있는 커밋. 생략하면 이력에서 승인 커밋(현재 승인이 처음 커밋된 자리)을 찾는다(D-a)")
    v_b.add_argument("--run", help="파일 이름 앞에 붙일 run 이름 — evidence·결과 계약과 같은 값을 쓴다")
    v_b.add_argument("--root")
    v_b.add_argument("--json", action="store_true")
    v_b.set_defaults(fn=cmd_envelope)
    v_c = vs.add_parser("check", help="결과 계약 파일을 검사한다 — 스키마·작업 단위·역할·앵커·역할 계약 능력 범위. "
                                      "종료 코드 0 통과 · 1 위반 · 2 검사 불가")
    v_c.add_argument("paths", nargs="+", help="검사할 결과 계약 파일 (예: docs/work/<id>/result/<run>-implementer.json)")
    v_c.add_argument("--unit", required=True, help="이 결과가 속해야 할 작업 단위 id — 봉투가 밝힌 값과 대조한다")
    v_c.add_argument("--role", choices=["implementer", "reviewer"],
                     help="이 결과를 낸 역할. 주면 대조하고, 생략하면 봉투의 역할로 능력 범위만 본다")
    v_c.add_argument("--root")
    v_c.add_argument("--json", action="store_true")
    v_c.set_defaults(fn=cmd_envelope)

    s = sub.add_parser("review", help="검토자 출력을 봉투로 기록한다 — review/<run>-reviewer.json 을 쓰고 그 sha256 을 같은 run 의 증거에 봉인")
    rs = s.add_subparsers(dest="action", required=True)
    r_rec = rs.add_parser("record", help="romeo review record --unit ID --run RUN <검토자 출력 JSON 파일>")
    r_rec.add_argument("source", help="검토자가 낸 결과 계약 JSON 파일(워크트리 밖 -o 출력 등)")
    r_rec.add_argument("--unit", required=True)
    r_rec.add_argument("--run", required=True, help="검토 run id — 봉투 이름과 증거 파일이 이 값으로 묶인다")
    r_rec.add_argument("--root")
    r_rec.set_defaults(fn=cmd_review)

    s = sub.add_parser("close", help="/plan-close 검사 → status done")
    s.add_argument("--unit", required=True)
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--root")
    s.add_argument("--no-rerun", action="store_true",
                   help="required_checks 를 다시 실행하지 않는다 — 기록만 읽은 판정이 되므로 "
                        "그 검사는 미검증으로 인쇄되고 done 을 선언하지 않는다")
    s.add_argument("--rerun-timeout", type=int, default=RERUN_TIMEOUT,
                   help=f"재실행 대조 한 건의 상한(초, 기본 {RERUN_TIMEOUT}). 초과하면 미검증이다")
    s.set_defaults(fn=cmd_close)

    s = sub.add_parser("id", help="ID 생성")
    s.add_argument("--unit", required=True, choices=["T0", "T1", "T2"])
    s.add_argument("--slug", required=True)
    s.set_defaults(fn=cmd_id)

    s = sub.add_parser("compile", help="코어 → 런타임 산출물 컴파일 (--check 로 대조)")
    s.add_argument("--check", action="store_true", help="쓰지 않고 최신인지만 검사")
    s.add_argument("--root")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_compile)

    s = sub.add_parser("doctor", help="부착 검증 — 런타임 프로브 + 충돌 fixture (K-68)")
    s.add_argument("--strict", action="store_true", help="문제가 있으면 exit 1")
    s.add_argument("--scope", choices=["all", "repository", "environment"], default="all",
                   help="--strict 가 무엇을 문제로 셀지. CI 는 repository (런타임 부재는 머신 문제다)")
    s.add_argument("--root")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_doctor)

    s = sub.add_parser("vendor", help="vendor 로컬 검사 또는 고정 upstream commit 대조")
    s.add_argument("action", nargs="?", default="check", choices=["check", "verify-upstream"])
    s.add_argument("--root")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_vendor)

    s = sub.add_parser("notices", help="THIRD_PARTY_NOTICES.md 생성 (--check 로 대조)")
    s.add_argument("--check", action="store_true", help="생성하지 않고 최신인지만 검사")
    s.add_argument("--root")
    s.set_defaults(fn=cmd_notices)
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
