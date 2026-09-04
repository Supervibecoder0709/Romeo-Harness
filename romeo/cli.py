"""romeo CLI — route · card · find · new · validate · fixtures(check·report·parity) · approve · evidence · envelope · review · close · run-unit · id · compile · doctor · vendor · notices."""
import argparse
import json
import sys
from pathlib import Path

from . import HARNESS_ROOT, __version__
from .evidence import RERUN_TIMEOUT
from .find import DEFAULT_LIMIT
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
        # 불일치나 gate 누락 의심이 1건이면 exit 1 이다(Q-37). 90% 임계값은 M0 진입 기준이었다 — 그 기준으로는 30/33 이 맞아도
        # exit 0 이라 required_checks 와 CI 의 이 명령이 무엇을 확인하는지 적혀 있는 채로 아무것도 확인하지 않았다(AGENTS.core §11).
        # 0/0 도 통과가 아니다 — 아무것도 대조하지 않은 실행을 성공으로 읽지 않는다(K-51).
        return 0 if rep["total"] and rep["matched"] == rep["total"] and rep["gate_misses"] == 0 else 1
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
        print(render_card(proposal, out, root=_root(args), harness_root=HARNESS_ROOT))
        return 0
    print(json.dumps(out, ensure_ascii=False, indent=1) if args.json else dump_yaml(out))
    return 0


def cmd_card(args):
    from .card import render_card
    from .policy import load_project_state, route
    prop = load_any(args.proposal)
    out = route(prop["candidate"], project_state=load_project_state(_root(args)))
    text = render_card(prop, out, root=_root(args), harness_root=HARNESS_ROOT)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def cmd_find(args):
    """재사용 검색 — 겹치는 기존 단위를 인쇄한다. 없음은 오류가 아니다(exit 0)."""
    from .find import search_units
    hits = search_units(_root(args), args.terms, limit=args.limit)
    if args.json:
        print(json.dumps({"terms": args.terms, "hits": hits}, ensure_ascii=False, indent=1))
    elif not hits:
        print("재사용 후보 없음")
    else:
        for h in hits:
            print(f"{h['id']}  score {h['score']} ({', '.join(h['matched'])})  {h['title']}")
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
    from .validate import DOC_NAMES, expand_targets, find_docs, validate_doc
    # 인자를 준 경우와 생략한 경우를 섞지 않는다 — 준 폴더가 비었다고 저장소 전체로 번지면
    # 사용자가 지목하지 않은 문서의 판정이 종료 코드에 섞인다.
    if args.paths:
        paths = expand_targets(args.paths)
        if not paths:
            print(f"검사할 문서가 없다 — 준 경로 아래에 {' · '.join(DOC_NAMES)} 가 없다")
            return 0
    else:
        paths = find_docs(_root(args))
        if not paths:
            print("검사할 문서가 없다")
            return 0
    rc = 0
    for p in paths:
        if not p.is_file():
            print(f"[FAIL] {p}")
            print("    ERROR NOT_A_FILE 읽을 수 있는 문서가 아니다")
            rc = 1
            continue
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
    # `route --fixtures … --report` 와 같은 공식이다(Q-37) — 같은 리포트를 내는 두 명령이 다른 판정을 내지 않는다.
    return 0 if rep["total"] and rep["matched"] == rep["total"] and rep["gate_misses"] == 0 else 1


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
    from .evidence import add_approval, add_rejection, run_command
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
    if args.action in ("approve", "reject"):
        # 설명 요구를 채우지 못하면 기록 자체가 만들어지지 않는다 — 비0 으로 끝내고 무엇이 빠졌는지 인쇄한다.
        # 기록되지 않았으므로 상태는 결정 전 그대로다(승인 전 상태 변경 0건).
        record = add_approval if args.action == "approve" else add_rejection
        try:
            path = record(args.unit, args.guard, args.by, note=args.note, run_name=args.run,
                          project_root=_root(args), **ids)
        except ValueError as exc:
            print(f"{args.action} 를 기록하지 않았다: {exc}", file=sys.stderr)
            return 2
        print(f"{'approval' if args.action == 'approve' else 'rejection'} recorded → {path}")
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
    # 「변경 범위」의 백틱 중 경로로 읽지 않은 토큰(Q-36) — 있을 때만 말한다. 계약 JSON 에는 없으므로 --json 이면 표준 오류로 낸다.
    ignored = res.get("scope_ignored") or []
    note = (f"  경로로 읽지 않은 백틱 {len(ignored)}개: " + " · ".join(f"`{tok}`" for tok in ignored)
            + " — 경로는 `/` 나 `.` 을 담고 공백이 없어야 한다. 설명은 괄호 안에 쓴다(core/templates/tech-spec.md 「변경 범위」)"
            ) if ignored else None
    if args.json:
        print(json.dumps(env, ensure_ascii=False, indent=1))
        if note:
            print(note, file=sys.stderr)
    else:
        print(f"built {env['role']} 계약 → {res['path']}")
        print(f"  base_sha {env['base_sha'][:12]} · spec {env['spec_ref']['sha256'][:12]} "
              f"· 계약 sha256 {res['sha256'][:12]} · workspace {env['workspace']} "
              f"· guards {[g['id'] for g in env['guards']]} · required_checks {len(env['required_checks'])}건")
        if note:
            print(note)
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


def cmd_run_unit(args):
    from .run_unit import (compare_attempts, compare_worktree_attempts, format_check, format_merge_check,
                           format_record, format_review, format_run, record_result, record_review, run_unit)
    if args.action == "check":
        # RUNBOOK §3.1 확인 4 — 커밋과 작업 트리의 attempts.yaml 을 **판정·재검토로만** 대조한다(Q-39). 아무것도 쓰지 않으므로
        # --run 도 요구하지 않는다. started 는 대조하지 않는다 — 계약 생성이 막 남긴 회차로 첫 관통을 막지 않는다.
        if not args.base_sha:
            print("run-unit check 는 --base-sha <커밋> 이 필요하다 — 그 커밋의 attempts.yaml 과 작업 트리의 것을 "
                  "판정·재검토로 대조한다(RUNBOOK §3.1 확인 4)", file=sys.stderr)
            return 2
        res = compare_attempts(_root(args), args.unit, args.base_sha)
        print(json.dumps(res, ensure_ascii=False, indent=1) if args.json else format_check(res))
        return 1 if res["diffs"] else 0
    if args.action == "merge-check":
        # 통합 직전 — 워크트리 사본이 이 체크아웃의 판정을 하나라도 잃는가(Q-48). 아무것도 쓰지 않으므로 --run 도 요구하지 않는다.
        # `check`(§3.1 확인 4)와 다른 자리다: 저것은 커밋과 작업 트리를, 이것은 **정본과 워크트리 사본**을 대조한다.
        if not args.worktree:
            print("run-unit merge-check 는 --worktree <워커 워크트리 절대경로> 가 필요하다 — 그 사본의 attempts.yaml 과 "
                  "이 체크아웃(정본)의 판정을 대조한다(RUNBOOK §3.10)", file=sys.stderr)
            return 2
        res = compare_worktree_attempts(_root(args), args.unit, args.worktree)
        print(json.dumps(res, ensure_ascii=False, indent=1) if args.json else format_merge_check(res))
        return 1 if res["diffs"] else 0
    if args.action == "review":
        # 재검토를 **기록만** 한다(Q-25). 시도를 시작하지 않으므로 --run 도 요구하지 않는다 —
        # 기록은 run 에 묶이지 않고 '몇 회차까지를 사람이 봤는가' 에 묶인다.
        if not args.after_review:
            print("run-unit review 는 --after-review \"<결론>\" 이 필요하다 — 기록할 재검토 결론이 없으면 남길 것이 없다",
                  file=sys.stderr)
            return 2
        res = record_review(args.unit, args.after_review, project_root=_root(args), by=args.by)
        print(json.dumps(res, ensure_ascii=False, indent=1) if args.json else format_review(res))
        return 0
    if not args.run:
        print(f"run-unit {args.action} 은 --run 이 필요하다 — 계약·증거·결과 봉투가 그 값 하나로 묶인다(RUNBOOK §3.3)",
              file=sys.stderr)
        return 2
    if args.action == "record":
        res = record_result(args.unit, args.run, args.result, project_root=_root(args),
                            failure_class=args.failure_class, note=args.note)
        print(json.dumps(res, ensure_ascii=False, indent=1) if args.json else format_record(res))
        return 0
    res = run_unit(args.unit, project_root=_root(args), run=args.run, base_sha=args.base_sha,
                   spawn=args.spawn, after_review=args.after_review, by=args.by)
    print(json.dumps(res, ensure_ascii=False, indent=1) if args.json else format_run(res))
    # 중단 기준에 걸린 기동은 통과가 아니다 — 3회차를 그 자리에서 멈추는 것이 이 명령의 일이다(AGENTS.core §10).
    return 1 if res["verdict"] == "BLOCKED_REPEAT" else 0


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
    s.add_argument("--report", action="store_true",
                   help="(fixtures) 리포트 출력 — 불일치나 gate 누락 의심이 1건이면 exit 1 이다(Q-37)")
    s.add_argument("--json", action="store_true")
    s.add_argument("--card", action="store_true", help="(proposal) 카드 렌더링")
    s.add_argument("--root", help="부착 상태(.harness/romeo.project.yaml)를 찾을 프로젝트 루트")
    s.set_defaults(fn=cmd_route)

    s = sub.add_parser("card", help="제안 카드 렌더링(≤30줄)")
    s.add_argument("--proposal", required=True)
    s.add_argument("--out")
    s.add_argument("--root", help="부착 상태(.harness/romeo.project.yaml)를 찾을 프로젝트 루트")
    s.set_defaults(fn=cmd_card)

    s = sub.add_parser("find", help="재사용 검색 — 핵심어와 겹치는 기존 작업 단위 (/plan 1단계)")
    s.add_argument("terms", nargs="+", help="핵심어 (slug·제목의 낱말)")
    s.add_argument("--root", help="검색할 프로젝트 루트")
    s.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"인쇄할 후보 수 (기본 {DEFAULT_LIMIT})")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_find)

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
    # 승인과 거부는 같은 인자를 받는다 — 같은 봉인으로 남고, 설명 넷을 똑같이 요구한다.
    # 거부에도 설명을 요구하는 이유: 무엇을 왜 거부했는지가 남아야 재요청이 같은 것을 반복하지 않는다.
    _NOTE_HELP = ("설명 요구 네 항목을 `라벨: 값` 으로 적는다 — 목록의 정본은 "
                  "core/policy/execution-guards.yaml 의 required_explanation 이다. "
                  '예: --note "영향 범위: … / 사전 백업: … / 복구 방법: … / 확인할 내용: …". '
                  "빠지거나 자리표시자뿐이면 기록하지 않고 비0 으로 끝난다")
    for action, helptext in (("approve", "실행 가드 승인 사건 기록 (선행 run 이 없으면 승인 전용 레코드를 만든다)"),
                             ("reject", "실행 가드 **거부** 사건 기록 — 승인과 같은 봉인으로 남는다. "
                                        "종료 검사는 '아직 안 물어봤다' 와 '사람이 거부했다' 를 다른 판정으로 말한다")):
        e_d = es.add_parser(action, help=helptext)
        e_d.add_argument("--unit", required=True)
        e_d.add_argument("--guard", required=True)
        e_d.add_argument("--by", required=True)
        e_d.add_argument("--note", help=_NOTE_HELP)
        e_d.add_argument("--run")
        _delegation_flags(e_d)
        e_d.add_argument("--root")
        e_d.set_defaults(fn=cmd_evidence)

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

    s = sub.add_parser("run-unit", help="관통 1회를 5단계로 엮는다 (계약 → 위임 명령 → 회수·앵커 → 증거 → 관측). "
                                        "기동은 기본이 dry-run 이고 --spawn 을 명시해야 실제로 띄운다")
    s.add_argument("action", nargs="?", default="start",
                   choices=["start", "record", "review", "check", "merge-check"],
                   help="start(기본) 관통 1회를 돌린다 · record 그 회차의 판정을 attempts.yaml 에 남긴다 · "
                        "review 재검토 결론만 남긴다(시도를 시작하지 않는다, Q-25) · "
                        "check 커밋과 작업 트리의 attempts.yaml 을 판정·재검토로만 대조한다(RUNBOOK §3.1 확인 4, Q-39) — "
                        "차이 없으면 exit 0, 있으면 exit 1. started 는 대조하지 않는다 · "
                        "merge-check 통합 직전에 --worktree 사본이 이 체크아웃(정본)의 판정을 하나라도 잃는지 본다"
                        "(RUNBOOK §3.10, Q-48) — 사라지는 판정이 없으면 exit 0, 있으면 exit 1")
    s.add_argument("--unit", required=True)
    s.add_argument("--run", help="계약·증거·결과 봉투를 묶는 run id — RUNBOOK §3.2 의 Run id 를 그대로 쓴다. "
                                 "start·record 에는 필수이고 review·check 에는 쓰지 않는다")
    s.add_argument("--base-sha", dest="base_sha",
                   help="승인된 spec.md 가 들어 있는 커밋. start 에서 생략하면 이력에서 승인 커밋을 찾는다(D-a). "
                        "check 에는 필수다 — 그 커밋의 attempts.yaml 과 작업 트리의 것을 대조한다")
    s.add_argument("--worktree",
                   help="(merge-check) 워커 워크트리의 절대 경로. 그 사본의 attempts.yaml 과 이 체크아웃의 판정을 대조한다 — "
                        "attempts.yaml 의 정본은 위임한 쪽이다")
    s.add_argument("--spawn", action="store_true",
                   help="위임 명령을 실제로 실행한다. 없으면 인쇄만 한다 — 기동은 비용이 드는 실행이다(K-66)")
    s.add_argument("--after-review", dest="after_review",
                   help="연속 실패 뒤 사람이 완료 정의를 재검토한 결론. start 에 주면 기록하고 진행하고, "
                        "review 에 주면 기록만 한다(AGENTS.core §10)")
    s.add_argument("--by", help="(--after-review) 재검토한 사람")
    s.add_argument("--result", choices=["pass", "fail"], help="(record) 이 회차의 판정")
    s.add_argument("--failure-class", dest="failure_class", choices=["outputs", "harness", "goal"],
                   help="(record) 사람이 적는 실패 분류. 기록만 하고 차단 판정에 쓰지 않는다")
    s.add_argument("--note", help="(record) 이 회차에 대해 남길 한 줄")
    s.add_argument("--root")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_run_unit)

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
