"""/plan-close 검사기. 결정적 차단 검사만 실패로 처리하고, 휴리스틱은 경고로 남긴다(C-E3). 검증 상태는 저장하지 않고 여기서 계산한다."""
import json
import re
import time
import subprocess
from pathlib import Path

from . import HARNESS_ROOT, frontmatter
from .blocks import evaluate as evaluate_blocks
from .blocks import required_checks
from .docs import approval_chain_warnings, approval_commit, approval_key, approval_key_at, find_unit_dir
from .evidence import (RERUN_NEAR_TIMEOUT_RATIO, RERUN_TIMEOUT, approval_log_state, command_log_state, dirty_tree_hash_excluding, exclusions,
                       guard_decisions, parse_guard_explanation, required_explanation,
                       list_runs, replay, review_record_state, sealed_product)
from .gitinfo import head_sha
from .parity import (_envelope_defects, _evidence_product, _product_of, _product_text, evidence_ref_error,
                     load_role_contracts, task_ref_error)
from .policy import classification_from_frontmatter, load_policy, load_project_state, route
from .schema import validate as validate_schema
from .util import dump_yaml, load_json, load_yaml, now_iso, rel, sha256_bytes, sha256_file, today
from .validate import UNCHECKED_RE, section_lines, validate_doc

RESULT_SCHEMA = "core/schemas/result-envelope.json"

# 검사가 성립하지 않았다는 상태. 어긴 것(FAIL)과 구분해 인쇄하되 **통과로 세지 않는다** —
# 대조하지 못했다는 사실을 PASS 로 인쇄하지 않고, 하나라도 남아 있으면 done 을 선언하지 않는다(K-51).
UNVERIFIED = "unverified"

# 결과 계약 하나에 적용하는 검사와 그 순서. close 와 `romeo envelope check` 가 같은 목록을 쓴다.
ENVELOPE_CHECKS = ("ENVELOPE_VALID", "TASK_ANCHORED", "BASE_SHA", "EVIDENCE_ANCHORED", "ROLE_CONTRACT")
UNREADABLE = "봉투를 읽을 수 없어 대조가 성립하지 않는다"


# 하네스 자신을 대상으로 하는 검사. 페이로드(하네스를 부착한 프로젝트) 작업 단위의 검증 계획에는 넣지 않는다 —
# 하네스가 깨진 동안 그 단위의 산출물이 멀쩡해도 완료가 서지 않고, 어느 쪽이 깨졌는지 구분되지 않는다
# (근거: feat-20260829-license-field-46an 의 check-5). 규칙의 원본은 core/templates/tech-spec.md 의 검증 계획 절이다.
HARNESS_OWN_CHECK_RE = re.compile(
    r"(?:^|[\s;&|(])(?:python3?\s+-m\s+unittest\b"
    r"|(?:\./)?(?:bin/)?romeo\s+(?:compile|validate|doctor|fixtures|vendor|notices)\b)")


def harness_own_checks(plan):
    """검증 계획 안에서 **하네스 자신**을 검사하는 항목들을 돌려준다. 판정하지 않고 열거만 한다.

    이 저장소(하네스 자신)의 작업 단위에서는 그 검사가 정당하므로 여기서 차단하지 않는다 —
    페이로드인지 아닌지는 부르는 쪽이 안다(`romeo/run_unit.py` 의 1단계가 작업 루트와 하네스 루트를 비교한다)."""
    out = []
    for rc in plan or []:
        command = str((rc or {}).get("command") or "")
        if HARNESS_OWN_CHECK_RE.search(command):
            out.append({"id": str((rc or {}).get("id") or ""), "command": command})
    return out


def _plan_key(plan):
    """검증 계획을 대조용 형태로 줄인다 — 무엇을 어떤 기대로 실행하기로 했는가."""
    return [(str((rc or {}).get("id")), str((rc or {}).get("command")), str((rc or {}).get("expect")))
            for rc in plan]


def _approved_body(project_root, spec, unit_id):
    """승인 커밋의 spec 본문. (본문, 승인 커밋 SHA, 실패 이유) — 승인이 커밋되지 않았으면 본문이 None 이다."""
    try:
        sha = approval_commit(project_root, unit_id)
    except ValueError as e:
        return None, None, str(e)
    relpath = rel(spec, project_root)
    proc = subprocess.run(["git", "show", f"{sha}:{relpath}"], cwd=str(project_root), capture_output=True)
    if proc.returncode != 0:
        return None, sha, f"승인 커밋 {sha[:12]} 에 {relpath} 가 없다"
    _fm, body = frontmatter.split(proc.stdout.decode("utf-8", "replace"))
    return body, sha, None


def _check_plan_committed(check, project_root, spec, plan, unit_id):
    """지금 읽고 있는 검증 계획이 **승인 시점의 계획**과 같은지 본다.

    재실행 대조를 붙이자 위조가 한 겹 옆으로 갔다: 실패하는 검사(`false`)를 지우고 `true` 로 바꾼 뒤
    그것을 진짜로 실행하면 기록도 로그도 재실행도 전부 맞는다. 고쳐진 것은 증거가 아니라 **주장 자체**다.
    `docs/work/<unit>/` 는 신선도 계산에서 제외돼 있어(기록 행위가 트리를 바꾸므로) 이 편집은 어디에도 걸리지 않았다.

    종전에는 HEAD 의 계획과 대조했다 — 그것은 절반의 앵커였다: 계획을 고치고 **커밋**하면 통과했다. 이제 원본은
    승인 커밋(`docs.approval_commit` — 현재 승인이 처음 커밋된 자리)의 계획이다. 계획을 바꾸려면 재승인해야 하고,
    재승인은 승인 커밋을 옮긴다(체크리스트 37·38). 승인이 커밋되지 않았으면 대조할 원본이 없다 — 미검증이다."""
    committed_body, sha, why = _approved_body(project_root, spec, unit_id)
    if committed_body is None:
        check("CHECK_PLAN_COMMITTED", UNVERIFIED,
              f"승인 시점의 검증 계획을 읽을 수 없다 — {why}. 승인된 spec.md 를 커밋한 뒤 다시 실행한다(D-a)")
        return
    try:
        committed = required_checks(committed_body)
    except Exception as e:
        check("CHECK_PLAN_COMMITTED", UNVERIFIED, f"승인 커밋 {sha[:12]} 의 spec.md 에서 검증 계획을 읽을 수 없다 ({e})")
        return
    if _plan_key(committed) != _plan_key(plan):
        check("CHECK_PLAN_COMMITTED", False,
              f"검증 계획이 승인 커밋 {sha[:12]} 의 것과 다르다 — 승인 {_plan_key(committed)} vs 지금 {_plan_key(plan)}. "
              f"실행할 검사를 바꾸는 것은 증거가 아니라 주장을 바꾸는 것이다: 다시 승인한다(romeo approve --reapprove, D-27)")
        return
    check("CHECK_PLAN_COMMITTED", True, f"검사 {len(plan)}건이 승인 커밋 {sha[:12]} 의 spec.md 와 같다")


def _normalized_user_check(body):
    """확인란 절을 체크 표시만 지운 형태로 — 사용자가 승인한 문장 자체를 대조하기 위해서다."""
    lines = section_lines(body or "", "확인란")
    if lines is None:
        return None
    return "\n".join(re.sub(r"^(\s*- )\[[xX]\]", r"\1[ ]", ln) for ln in lines).strip()


def _check_ac_text(check, project_root, spec, body, unit_id):
    """확인란의 **문장**이 승인 시점과 같은지 본다 — 체크 표시(`[x]`)만 다를 수 있다.

    구현자는 수용 기준 체크박스를 채운다(implement 절차 7번). 그 편집을 허용하면서 확인란 본문이 승인본과 같은지 보지 않으면,
    `[x]` 를 채우며 수용 기준 문구를 바꿔도 걸리지 않는다 — 확인란은 사용자가 승인하는 유일한 면이다(D-27·D-60).
    체크 표시를 지운 뒤 승인 커밋의 절과 바이트로 대조한다. 승인이 커밋되지 않았으면 미검증이다."""
    committed_body, sha, why = _approved_body(project_root, spec, unit_id)
    if committed_body is None:
        check("AC_TEXT_UNCHANGED", UNVERIFIED, f"승인 시점의 확인란을 읽을 수 없다 — {why}")
        return
    now, then = _normalized_user_check(body), _normalized_user_check(committed_body)
    if now is None or then is None:
        check("AC_TEXT_UNCHANGED", UNVERIFIED, "확인란 절이 없다 — 승인된 문장을 대조할 수 없다")
        return
    if now != then:
        check("AC_TEXT_UNCHANGED", False,
              f"확인란의 문장이 승인 커밋 {sha[:12]} 의 것과 다르다(체크 표시 외) — 확인란은 사용자가 승인한 면이므로 "
              f"고쳤으면 다시 승인한다(romeo approve --reapprove, D-27). 체크박스만 채우는 것은 여기 걸리지 않는다")
        return
    check("AC_TEXT_UNCHANGED", True, f"확인란의 문장이 승인 커밋 {sha[:12]} 과 같다(체크 표시 제외)")


def _check_evidence_logs(check, project_root, ev):
    """증거 기록의 명령들을 **원시 로그와 대조한다**(4차 리뷰 구멍 A, 2·3겹).

    close 는 지금까지 evidence yaml 만 읽었다 — 그래서 `exit_code: 1` 을 `0` 으로 고치는 것만으로
    전 항목 PASS 가 났다. 같은 사실이 원시 로그에도 적혀 있고 `log_sha256` 이 그 로그를 봉인한다.
    `log_sha256` 은 지금까지 **쓰기만 하고 아무도 읽지 않았다** — 여기서 읽는다.

    로그가 없는 경우(다른 체크아웃 — `.harness` 는 커밋되지 않는다)는 실패가 아니라 미검증이다.
    없는 것을 어긴 것으로도, 통과로도 세지 않는다(K-51)."""
    cmds = ev.get("commands") or []
    if not cmds:
        check("EVIDENCE_LOG", UNVERIFIED, "이 run 에는 실행 기록이 0건이다 — 로그와 대조할 것이 없다")
        return
    states, details = [], []
    for c in cmds:
        state, why = command_log_state(project_root, c)
        states.append(state)
        if why:
            details.append(why)
    _sealed, mismatch = sealed_product(ev)
    if mismatch:
        states.append(False)
        details.append(mismatch)
    detail = "; ".join(details)
    if False in states:
        check("EVIDENCE_LOG", False, detail)
    elif None in states:
        check("EVIDENCE_LOG", UNVERIFIED, detail)
    else:
        check("EVIDENCE_LOG", True, f"{len(cmds)}건이 원시 로그·log_sha256 과 일치 · 산출물 식별이 봉인된 자리와 같다")


def _skip_rerun(check, plan, why):
    """재실행을 하지 **않은** 이유를 검사 항목으로 남긴다.

    조용히 건너뛰면 '재실행 대조를 했다' 와 구분되지 않는다. 재실행이 없었다는 사실은 미검증이지
    통과가 아니다 — 그래서 UNVERIFIED 로 인쇄하고 done 을 막는다(K-51)."""
    for rc in plan:
        check("REQUIRED_CHECK_RERUN", UNVERIFIED, f"{rc.get('id')}: {why} — {rc.get('command', '')}")


def _check_rerun(check, project_root, unit_id, plan, cmds, rerun, timeout):
    """`required_checks` 를 **다시 실행해서** 기록된 종료 코드와 대조한다(4차 리뷰 구멍 A, 1겹 = 종점).

    로컬 파일을 위조 불가로 만들 수는 없다 — 기록도 로그도 해시도 그 기계를 쓰는 사람이 고칠 수 있다.
    고칠 수 없는 것은 **명령을 다시 돌린 결과**뿐이다. AGENTS.core §4 가 이미 그렇게 적혀 있다:
    "완료는 증거로만 선언한다 — 주장에 맞는 명령을 새로 실행하고, 그 출력·종료 코드를 기록해야 한다."

    재실행이 성립하지 않는 경우는 **막지 않고 드러낸다**: 부작용·비결정 때문에 다시 돌릴 수 없는 검사는
    검증 계획에서 `rerun: false` 로 선언하고 이유를 적는다. 그러면 미검증으로 인쇄되고 통과로 세지 않는다 —
    close 는 done 을 선언하지 않는다. 대조하지 못했다는 사실을 PASS 로 인쇄하는 것보다 낫다(K-51)."""
    before = dirty_tree_hash_excluding(project_root, exclusions(unit_id))
    ran = False
    for rc in plan:
        cmd = rc.get("command", "")
        cid = rc.get("id")
        rec = cmds.get(cmd)
        if rec is None:
            check("REQUIRED_CHECK_RERUN", UNVERIFIED,
                  f"{cid}: evidence 에 기록이 없어 재실행과 대조할 값이 없다 — {cmd}")
            continue
        if rc.get("rerun") is False:
            why = rc.get("rerun_reason") or "검증 계획이 재실행 대조를 선언하지 않았다"
            check("REQUIRED_CHECK_RERUN", UNVERIFIED,
                  f"{cid}: 재실행으로 확인되지 않았다 (rerun: false — {why}) — {cmd}")
            continue
        if not rerun:
            check("REQUIRED_CHECK_RERUN", UNVERIFIED,
                  f"{cid}: 재실행 대조를 건너뛰라고 했다(--no-rerun) — 기록만 읽은 판정이다: {cmd}")
            continue
        started = time.monotonic()
        code, why = replay(project_root, cmd, timeout=timeout)
        elapsed = time.monotonic() - started
        ran = True
        # **막지 않고 드러낸다.** 상한은 재실행 **한 건**에 걸리는데, 하네스 자신을 고치는 단위는
        # 그 한 건에 전체 테스트를 넣는 것이 정당하다 — 그때는 그것이 그 단위의 산출물이기 때문이다.
        # 그래서 이 값은 테스트가 늘수록 커지고, 상한을 넘는 날 그 검사가 미검증이 되어 완료가 서지 않는다.
        # 넘기 전까지 아무 신호가 없던 것이 이 경고를 만든 이유다(2026-09-02 실측: 258초 / 상한 300초).
        # 판정은 바꾸지 않는다 — 늘 뜨는 경고는 아무것도 알리지 않으므로 임계 아래에서는 인쇄하지 않는다.
        if timeout and elapsed >= timeout * RERUN_NEAR_TIMEOUT_RATIO:
            check("RERUN_NEAR_TIMEOUT", False,
                  f"{cid}: 재실행이 {elapsed:.0f}초 걸렸다 — 상한 {timeout}초의 "
                  f"{elapsed / timeout * 100:.0f}% 다. 넘으면 이 검사가 미검증이 되어 완료가 서지 않는다: {cmd}",
                  level="warning")
        if code is None:
            check("REQUIRED_CHECK_RERUN", UNVERIFIED, f"{cid}: {why} — {cmd}")
        elif code != rec.get("exit_code"):
            check("REQUIRED_CHECK_RERUN", False,
                  f"{cid}: evidence 는 exit {rec.get('exit_code')} 인데 지금 다시 실행하니 exit {code} 다 — "
                  f"기록이 실행과 다르다. 증거를 다시 만든다(romeo evidence checks): {cmd}")
        else:
            check("REQUIRED_CHECK_RERUN", True, f"{cid}: 재실행도 exit {code} — {cmd}")
    if ran and dirty_tree_hash_excluding(project_root, exclusions(unit_id)) != before:
        check("REQUIRED_CHECK_RERUN", UNVERIFIED,
              "재실행이 작업 트리를 바꿨다 — 부작용이 있는 검사이므로 재실행 전에 계산한 신선도 판정이 "
              "더는 성립하지 않는다. 그 검사는 검증 계획에서 rerun: false 로 선언하고 이유를 적는다")


def _run_name(r):
    return str(r.get("run_id") or Path(str(r.get("_path", ""))).stem or "?")


def select_check_record(runs, plan, cur_head=None, cur_dirty=None):
    """이 작업 단위의 **검사 기록**을 고른다 — `(run, 완전한가, 설명)`.

    종전에는 마지막 evidence 파일(`runs[-1]`)을 읽었다. 그런데 정규 절차가 evidence 를 하나만 남기지 않는다:
    검토자를 띄운 쪽은 실행마다 새 run 에 방어 검사(review-tree-before/after) 2건만 든 evidence 를 남기고(RUNBOOK §4·§6.6),
    그 파일이 마지막이 되면 close 는 구현자의 검사 기록 대신 그것을 읽어 `REQUIRED_CHECK` 전부가 '명령 없음' 이 됐다 —
    두 정규 절차가 서로를 깨뜨렸다(체크리스트 41).

    그래서 파일의 위치가 아니라 **내용**으로 고른다: 검증 계획(`required_checks`)의 명령을 **전부** 실행한 run 이 검사 기록이고,
    여럿이면 최신이다. run 들을 합치지 않는다 — 검사는 한 산출물(한 run 의 `head_sha`·`dirty_tree_hash`) 위에서 전부 돌아야
    무엇을 검사했는지 말할 수 있다. 전부 실행한 run 이 없으면 가장 많이 실행한 run 을 읽되 그 사실을 인쇄한다(통과가 아니다 —
    빠진 검사는 `REQUIRED_CHECK` 가 잡는다). 계획이 비어 있으면 종전처럼 마지막 run 이다.

    후보는 먼저 **지금 트리와 같은 산출물**(`head_sha`·`dirty_tree_hash`)을 기록한 run 으로 좁힌다 — 동등성 관측을 모으는
    절차(RUNBOOK §6.3)는 다른 산출물의 완전한 run 을 같은 evidence/ 에 두고, 최신 규칙만으로는 그쪽이 뽑혀 기준 산출물의
    검토 판정을 전부 낡은 것으로 보낸다. 같은 산출물의 run 이 없으면 전체에서 고르고 신선도 검사가 그 사실을 드러낸다."""
    pool, scope = runs, ""
    if cur_head and cur_dirty:
        same = [r for r in runs if r.get("head_sha") == cur_head and r.get("dirty_tree_hash") == cur_dirty]
        if same:
            pool = same
            scope = f" · 지금 트리와 같은 산출물의 run {len(same)}건/{len(runs)}건 중"
        else:
            scope = f" · 지금 트리와 같은 산출물의 run 이 없다({len(runs)}건 전체에서 골랐다 — 신선도 검사가 이것을 잡는다)"
    if not plan:
        ev = pool[-1]
        return ev, True, f"검사 기록 = {_run_name(ev)} — 검증 계획이 없어 마지막 run 을 읽는다{scope}"
    wanted = [str((rc or {}).get("command", "")) for rc in plan]

    def coverage(r):
        have = {c.get("command") for c in (r.get("commands") or []) if isinstance(c, dict)}
        return sum(1 for cmd in wanted if cmd in have)

    scored = [(coverage(r), r) for r in pool]
    full = [r for n, r in scored if n == len(wanted)]
    empty = [_run_name(r) for n, r in scored if n == 0]
    if full:
        ev = full[-1]
        detail = f"검사 기록 = {_run_name(ev)} — 검증 계획 {len(wanted)}건을 전부 실행한 run"
        others = [_run_name(r) for r in full if r is not ev]
        detail += f" {len(full)}건 중 최신(다른 완전한 기록: {others})" if others else ""
        if empty:
            detail += f" · 계획의 검사를 하나도 담지 않은 run {len(empty)}건은 검사 기록이 아니다(방어 검사 등): {empty}"
        return ev, True, detail + scope
    best = max(n for n, _ in scored)
    ev = [r for n, r in scored if n == best][-1]
    return ev, False, (f"검증 계획 {len(wanted)}건을 전부 실행한 run 이 없다 — 가장 많이 실행한 {_run_name(ev)}"
                       f"({best}/{len(wanted)})을 읽는다. 빠진 검사는 아래 REQUIRED_CHECK 가 잡는다: "
                       f"romeo evidence checks 로 한 run 에 전부 기록한다{scope}")


def close_unit(unit_id, project_root=".", harness_root=None, dry_run=False,
               rerun=True, rerun_timeout=RERUN_TIMEOUT):
    project_root = Path(project_root).resolve()
    harness_root = Path(harness_root or HARNESS_ROOT)
    pol = load_policy(harness_root)
    udir = find_unit_dir(project_root, unit_id)
    spec = udir / "spec.md"
    fm, body = frontmatter.read(spec)
    checks = []

    def check(cid, ok, detail="", level="error"):
        """`ok` 에 UNVERIFIED 를 주면 '검사가 성립하지 않았다' 로 기록한다 — PASS 로 인쇄하지 않고
        통과로 세지 않으므로 done 판정을 막는다(K-51). 어긴 것과는 구분해 인쇄한다."""
        unverified = ok is UNVERIFIED
        checks.append({"id": cid, "ok": False if unverified else bool(ok), "detail": detail,
                       "level": UNVERIFIED if unverified else level})
        return False if unverified else ok

    v = validate_doc(spec, harness_root)
    check("FRONTMATTER_VALID", not v["errors"], "; ".join(v["errors"]))
    for w in v["warnings"]:
        check("DOC_WARNING", True, w, level="warning")
    if fm.get("status") == "done":
        check("NOT_ALREADY_DONE", False, f"이미 done ({fm.get('closed_at')})")
    check("APPROVED", fm.get("status") == "active" and fm.get("approved_at"), f"status={fm.get('status')} approved_at={fm.get('approved_at')}")
    runs = list_runs(project_root, unit_id)
    if not check("HAS_EVIDENCE", bool(runs), "" if runs else "evidence/*.yaml 없음 — romeo evidence run 으로 만든다"):
        return _finish(checks, fm, body, spec, runs, dry_run, project_root, None)
    plan = required_checks(body)
    cur_head = head_sha(project_root)
    cur_dirty = dirty_tree_hash_excluding(project_root, exclusions(unit_id))
    ev, complete, why = select_check_record(runs, plan, cur_head, cur_dirty)
    check("EVIDENCE_SELECTED", complete, why, level="error" if complete else "warning")
    check("FRESH_HEAD", ev.get("head_sha") == cur_head, f"evidence {str(ev.get('head_sha'))[:12]} vs 현재 {cur_head[:12]}")
    check("FRESH_TREE", ev.get("dirty_tree_hash") == cur_dirty, f"evidence {str(ev.get('dirty_tree_hash'))[:12]} vs 현재 {cur_dirty[:12]} (tracked 수정·staged·untracked 포함)")
    cmds = {c["command"]: c for c in ev.get("commands", [])}
    if not plan:
        # 실행 대조의 앵커(검증 계획)가 없다. 검사할 것이 0건인 것을 조용히 지나가지 않는다 — 인쇄한다(K-51).
        check("REQUIRED_CHECK", UNVERIFIED,
              "spec.md 의 검증 계획에 required_checks 가 없다 — evidence 와 대조할 검사가 하나도 없다")
    for rc in plan:
        cmd = rc.get("command", "")
        rec = cmds.get(cmd)
        if rec is None:
            check("REQUIRED_CHECK", False, f"{rc.get('id')}: evidence 에 명령 없음 — {cmd}")
        elif isinstance(rec.get("dirty_tree_hash"), str) and rec["dirty_tree_hash"] != ev.get("dirty_tree_hash"):
            # 한 run 의 검사는 한 산출물 위에서 전부 돌아야 한다 — run 의 산출물은 마지막 명령의 것이므로,
            # 그 전에 다른 트리에서 돈 검사의 결과는 이 산출물에 대한 결과가 아니다(명령별 값이 없는 옛 기록은 대조하지 않는다).
            check("REQUIRED_CHECK", UNVERIFIED,
                  f"{rc.get('id')}: exit {rec['exit_code']} 이지만 다른 트리에서 돌았다 "
                  f"(그때 {rec['dirty_tree_hash'][:12]} vs 이 run 의 산출물 {str(ev.get('dirty_tree_hash'))[:12]}) — "
                  f"이 산출물에서 다시 실행해 기록한다: {cmd}")
        else:
            check("REQUIRED_CHECK", rec["exit_code"] == 0, f"{rc.get('id')}: exit {rec['exit_code']} — {cmd}")
    _check_evidence_logs(check, project_root, ev)
    # 라우팅과 가드 승인은 **재실행보다 먼저** 판정한다. 재실행은 spec.md 의 셸 명령을 실제로 돌리므로,
    # 승인되지 않은 가드가 걸린 단위에서 그것을 먼저 돌리면 K-66(승인 없이 실행하지 않는다)을 어긴다.
    # dry-run 도 마찬가지다 — 읽기만 한다고 알려진 명령이 부작용을 내면 안 된다.
    out = route(classification_from_frontmatter(fm), pol, project_state=load_project_state(project_root))
    # 차단(blocks) — **종료는 backstop 이다.** 차단마다 막기 시작하는 사건은 하나지만(approve 또는 dispatch),
    # 여기서는 걸린 차단을 **전부** 다시 본다. 승인이나 위임 뒤에 조건이 무너지는 것(조사 링크를 지우거나
    # 마일스톤 절을 비우는 것)을 잡을 자리가 이것 하나뿐이기 때문이다.
    # **이미 done 인 단위에는 소급하지 않는다** — 그 단위는 닫힐 때의 규칙으로 이미 닫혔고, 지금 다시 막을 것이 없다.
    if fm.get("status") != "done":
        from .docs import block_context
        for bid, ok, why in evaluate_blocks(pol["packages"], out["blocks"], "close", udir, fm, body,
                                            context=block_context(out, project_root)):
            check("BLOCK_SATISFIED", ok, f"{bid}: {why}")
    unapproved = []
    for g in out["guards"]:
        # 한 가드의 판정은 **가장 최근 결정**이다(execution-guards.yaml 의 approval.last_decision).
        # 거부 뒤 승인이 오면 승인이 이긴다 — 사람이 다시 판단한 것이다.
        decisions = guard_decisions(runs, g["id"])
        if not decisions:
            check("GUARD_APPROVED", False, f"{g['id']} ({g['name']}) 승인 기록 없음 — 아직 묻지 않았다")
            unapproved.append(g["id"])
            continue
        last = decisions[-1]
        # 결정 항목은 yaml 배열이라 손으로 써 넣을 수 있다 — 기록 명령이 남긴 원시 로그와 봉인이 맞을 때만 결정으로 센다.
        sealed, why = approval_log_state(project_root, last["entry"], kind=last["kind"])
        if sealed is False:
            check("GUARD_APPROVED", False, f"{g['id']} ({g['name']}): {why}")
            unapproved.append(g["id"])
            continue
        if sealed is None:
            check("GUARD_APPROVED", UNVERIFIED, f"{g['id']} ({g['name']}): {why} — 결정 기록을 로그로 확인하지 못했다(K-51)")
            unapproved.append(g["id"])
            continue
        if last["kind"] == "reject":
            # "아직 안 물어봤다" 와 "물어봤고 사람이 아니라고 했다" 는 다른 상태다. 후자는 재시도가 답이 아니다.
            check("GUARD_APPROVED", False,
                  f"{g['id']} ({g['name']}) BLOCKED_APPROVAL — 사람이 거부했다 "
                  f"({last['by']} · {last['at']}): {last['note']}. "
                  "승인 기록 없음과 다르다 — 같은 요청을 다시 보내는 것이 답이 아니다. "
                  "무엇이 달라졌는지 적고 사람이 새로 승인해야 한다")
            unapproved.append(g["id"])
            continue
        # 여기서 읽는 note 는 **봉인된 로그의 note 다** — `approval_log_state` 가 yaml 항목에서 로그를
        # 다시 만들어 통째로 대조했으므로, 이 자리에 온 값은 log_sha256 이 봉인한 값과 같다.
        # 그 대조가 없으면 종료 시점이 봉인되지 않은 yaml 을 읽게 되고, 승인 자리와 종료 자리가
        # **같은 값을 두 번 읽는 한 지점**이 된다. 봉인 자체는 로그와 yaml 의 일치만 보므로
        # 둘을 함께 손으로 만들면 통과한다 — 그것을 잡는 것이 아래의 설명 요구다(승인·종료 두 지점).
        try:
            parse_guard_explanation(last["note"], harness_root)
        except ValueError as exc:
            labels = " · ".join(it["label"] for it in required_explanation(harness_root))
            check("GUARD_APPROVED", False,
                  f"{g['id']} ({g['name']}): 봉인은 맞지만 승인의 note 가 설명 요구({labels})를 채우지 못했다 — {exc}")
            unapproved.append(g["id"])
            continue
        check("GUARD_APPROVED", True,
              f"{g['id']} ({g['name']}) 승인 ({last['by']} · {last['at']}, 결정 {len(decisions)}건 중 최신) "
              "— 원시 로그와 일치하고 설명 요구를 채웠다")
    if plan:
        _check_plan_committed(check, project_root, spec, plan, unit_id)
        if unapproved:
            _skip_rerun(check, plan,
                        "승인되지 않은 실행 가드가 있어 재실행하지 않았다 — 승인 없이 실행하지 않는다(K-66): "
                        + ", ".join(unapproved))
        else:
            _check_rerun(check, project_root, unit_id, plan, cmds, rerun, rerun_timeout)
    check("AC_ALL_CHECKED", not UNCHECKED_RE.search(body), f"미체크 {len(UNCHECKED_RE.findall(body))}개")
    _check_ac_text(check, project_root, spec, body, unit_id)
    for w in approval_chain_warnings(project_root, unit_id):
        # 차단이 아니라 경고다 — 옛 방식의 재승인도 같은 모양이고, 승인 사건을 기계가 확인할 형태는 사용자 결정이다(체크리스트 45).
        check("APPROVAL_CHAIN", False, w, level="warning")
    # 미완료는 spec 하나가 아니라 **문서 패키지 전체**를 본다. brief 를 아무 집행도 읽지 않던 동안
    # 라우터가 필수라고 판정한 절(조사 계획의 첫 마일스톤·UI 상태표·실험 설계)이 그리로 가
    # 빈 채로 승인되고 빈 채로 닫혔다(2026-09-01 실측).
    from .blocks import unit_docs
    loops = [(pp.name, pp.read_text(encoding="utf-8").count("NEEDS_INPUT")) for _n, pp in unit_docs(udir)]
    loops = [(n, c) for n, c in loops if c]
    check("NO_OPEN_LOOP", not loops, " · ".join(f"{n} NEEDS_INPUT {c}곳" for n, c in loops))
    check("HAS_CHANGE", bool(ev.get("changed_files")), f"changed_files {ev.get('changed_files')}" if ev.get("changed_files") else "changed_files 가 비어 있다 — 아무것도 바뀌지 않았다면 done 이 아니다")
    spec_sha = sha256_file(spec)
    spec_same = (ev.get("spec_ref") or {}).get("sha256") == spec_sha
    check("SPEC_UNCHANGED_SINCE_EVIDENCE", spec_same, "" if spec_same else "spec.md 가 evidence 이후 바뀜(AC 체크 등). 확인만.", level="warning")
    if out["reviewer"] != "none":
        _check_review(check, udir, fm.get("id") or unit_id, harness_root, project_root,
                      product=_product_of(ev))
    return _finish(checks, fm, body, spec, runs, dry_run, project_root, ev)


def _inside(project_root, raw):
    """봉투가 지목한 경로를 저장소 안의 경로로 푼다. 저장소 밖이면 None — 앵커가 될 수 없다."""
    p = Path(raw)
    p = p if p.is_absolute() else Path(project_root) / p
    try:
        p.resolve().relative_to(Path(project_root).resolve())
    except ValueError:
        return None
    return p


def _task_anchor(project_root, unit_id, env, harness_root):
    """판정이 가리키는 것이 **하네스가 만든 그 작업 계약**인지 본다.

    해시 대조는 앵커가 아니다 — 봉투가 주장하는 해시도, 대조할 파일도 둘 다 봉투 작성자가 정하기 때문이다.
    규약에 맞는 자리에 계약처럼 생긴 JSON 을 손으로 만들어 두면 해시는 언제나 맞출 수 있다.
    **앵커는 재계산이다**: 커밋된 승인 원본에서 계약을 다시 계산해 바이트로 대조한다. 위조하려면 올바른
    계약을 만들어야 하고, 그것은 이미 올바른 계약이다 — 여기서 재귀가 끝난다(K-51·D-a).

    재계산이 요구하는 것: 계약의 `base_sha` 커밋에 그 작업 단위의 `spec.md` 가 **승인 상태로 커밋돼** 있어야 하고,
    지금의 정책표·역할 계약·스키마(`harness_root`)가 계약을 만들 때와 같아야 한다. 그 중 하나라도 다르면
    같은 바이트가 나오지 않으므로 이 검사는 실패한다 — 계약을 다시 만들어야 한다는 뜻이다.

    돌려주는 계약은 다음 검사(base_sha)가 쓴다. 파일을 그 봉투의 것으로 **식별**했을 때만 돌려준다:
    재계산만 어긋난 경우에는 식별은 됐으므로 계약을 돌려주되 이 검사는 실패다."""
    from .envelope import TASK_SCHEMA, build_envelope, envelope_text  # 순환 import 를 피해 여기서 부른다
    harness_root = Path(harness_root or HARNESS_ROOT)
    ref = env.get("task_envelope_ref") or {}
    raw = ref.get("path") or ""
    path = _inside(project_root, raw)
    if path is None:
        return None, f"task_envelope_ref.path 가 저장소 밖이다 ({raw})"
    place = task_ref_error(unit_id, raw)
    if place is not None:
        return None, f"task_envelope_ref.path 가 {place} ({raw})"
    if not path.is_file():
        return None, f"task_envelope_ref.path 가 실재하지 않는다 ({raw}) — 계약은 손으로 쓰지 않고 계약 생성 명령이 만든다"
    data = path.read_bytes()
    got = sha256_bytes(data)
    if got != ref.get("sha256"):
        return None, (f"task_envelope_ref.sha256 가 {raw} 의 실제 해시와 다르다 "
                      f"({str(ref.get('sha256'))[:12]} vs {got[:12]})")
    try:
        task = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        return None, f"{raw} 를 JSON 으로 읽을 수 없다 ({e})"
    if not isinstance(task, dict):
        return None, f"{raw} 가 JSON 객체가 아니다 — 작업 계약이 아니다"
    schema_errs = validate_schema(task, load_json(harness_root / TASK_SCHEMA))
    if schema_errs:
        return None, (f"{raw} 가 {TASK_SCHEMA} 에 맞지 않는다 ({'; '.join(schema_errs[:2])}) — "
                      f"계약 생성 명령이 만든 계약이 아니다")
    if task.get("unit_id") != unit_id:
        return None, f"{raw} 는 다른 작업 단위의 계약이다 (unit_id={task.get('unit_id')})"
    if task.get("role") != env.get("role"):
        return None, f"{raw} 의 role 이 {task.get('role')!r} 다 — 이 판정의 역할({env.get('role')!r})이 아니다"
    try:
        rebuilt = build_envelope(unit_id, task["role"], project_root=project_root,
                                 harness_root=harness_root, base_sha=task["base_sha"], allow_superseded=True)
    except Exception as e:
        return task, (f"{raw} 를 커밋된 원본에서 다시 계산할 수 없다 ({e}) — "
                      f"계약은 손으로 쓰지 않고 계약 생성 명령이 만든다")
    if envelope_text(rebuilt).encode("utf-8") != data:
        diff = sorted(k for k in set(rebuilt) | set(task) if rebuilt.get(k) != task.get(k))
        why = f"다른 필드 {diff}" if diff else "내용은 같은데 직렬화가 다르다(들여쓰기·개행)"
        return task, (f"{raw} 가 지금 다시 계산한 계약과 바이트로 다르다 — {why}. "
                      f"계약은 승인된 spec.md 를 커밋한 리비전에서 계약 생성 명령이 만든다(D-a)")
    return task, None


def _base_sha_anchor(project_root, task):
    """계약의 base_sha 가 지금 보고 있는 이력 안의 커밋인지 본다.

    evidence 의 신선도 검사와 같은 이유다 — 이 이력에 없는 리비전에서 낸 판정은 이 리비전의 검토가 아니다."""
    sha = task.get("base_sha") or ""
    if not sha:
        return "작업 계약에 base_sha 가 없다 — 어느 리비전의 검토인지 말할 수 없다"
    proc = subprocess.run(["git", "rev-parse", "--verify", f"{sha}^{{commit}}"],
                          cwd=str(project_root), capture_output=True, text=True)
    if proc.returncode != 0:
        return f"작업 계약의 base_sha {sha[:12]} 는 이 저장소의 커밋이 아니다"
    anc = subprocess.run(["git", "merge-base", "--is-ancestor", proc.stdout.strip(), "HEAD"],
                         cwd=str(project_root), capture_output=True, text=True)
    if anc.returncode != 0:
        return f"작업 계약의 base_sha {sha[:12]} 가 현재 HEAD 의 이력에 없다 — 다른 리비전에서 낸 판정이다"
    return None


def _evidence_ref(env):
    """봉투가 지목한 증거 경로. 비어 있으면 None — 대조할 앵커가 없다는 뜻이다(통과가 아니다)."""
    raw = env.get("evidence_ref")
    return raw.strip() if isinstance(raw, str) and raw.strip() else None


def _claimed_checks_vs_evidence(project_root, path, env):
    """봉투가 **주장한 검사**가 그 증거에 실제로 기록돼 있는지 본다. 어긋나면 이유, 맞으면 None(4차 리뷰 구멍 B).

    앵커가 '증거 파일이 실재하는가' 에서 멈추면, 진짜 증거를 가리키면서 실행된 적 없는 명령을 적을 수 있다 —
    `pytest -q tests/` exit 0 을 손으로 타이핑해도 아무도 반박하지 않았다. 파일이 진짜인지만 보고
    **봉투의 주장이 그 파일과 맞는지**는 보지 않았기 때문이다.

    대조 키는 명령 문자열이다. id 는 기록하는 쪽이 붙이는 이름이라 달라질 수 있지만, 무엇을 실행했다고
    주장하는지는 명령이 말한다. 같은 명령을 여러 번 실행했으면 그 중 하나와 종료 코드가 맞으면 된다.
    봉투가 증거보다 적게 주장하는 것은 막지 않는다 — 이 검사가 막는 것은 **없는 것을 주장하는 쪽**이다."""
    claims = env.get("checks") or []
    if not claims:
        return None                      # 주장한 검사가 없다 — 증거와 어긋날 것도 없다
    try:
        rec = load_yaml(path)
    except Exception as e:
        return f"evidence_ref 를 증거 기록으로 읽을 수 없다 ({e}) — 주장한 검사를 대조할 수 없다"
    if not isinstance(rec, dict):
        return "evidence_ref 가 증거 기록(YAML 매핑)이 아니다 — 주장한 검사를 대조할 수 없다"
    recorded = {}
    for c in rec.get("commands") or []:
        if isinstance(c, dict) and isinstance(c.get("command"), str):
            recorded.setdefault(c["command"], []).append(c)
    bad = []
    for c in claims:
        cmd, code = (c or {}).get("command"), (c or {}).get("exit_code")
        hits = recorded.get(cmd) or []
        if not hits:
            bad.append(f"{(c or {}).get('id')}: {cmd!r} 는 증거에 실행 기록이 없다")
            continue
        codes = [h.get("exit_code") for h in hits]
        if code not in codes:
            bad.append(f"{(c or {}).get('id')}: {cmd!r} 의 종료 코드가 증거와 다르다 "
                       f"(봉투 {code} vs 증거 {codes})")
            continue
        # 원시 로그가 그 체크아웃에 남아 있으면 거기까지 본다. **없는 것은 어긴 것이 아니다** —
        # .harness 는 커밋되지 않으므로 결과를 모은 체크아웃에는 로그가 없을 수 있다.
        # 로그가 있는데 어긋나는 경우만 잡는다: 증거 파일이 손으로 고쳐졌다는 뜻이다.
        for h in hits:
            if h.get("exit_code") != code:
                continue
            state, why = command_log_state(project_root, h)
            if state is False:
                bad.append(f"{(c or {}).get('id')}: 증거 기록이 원시 로그와 어긋난다 — {why}")
            break
    if bad:
        return ("봉투가 주장한 검사가 evidence_ref 의 기록과 맞지 않는다 — " + "; ".join(bad)
                + ". 실행하지 않은 검사를 주장할 수 없다(K-51)")
    return None


def _evidence_anchor(project_root, udir, unit_id, env):
    """판정이 지목한 증거가 이 작업 단위의 **증거 산출물**로 실재하고, **봉투의 주장이 그 증거와 맞는지** 본다
    (K-51·K-62).

    실재하는 아무 파일이나 인정하면 검토자가 자기 입력인 spec.md 를 '읽은 증거' 로 지목해도 통과한다.
    실재만 확인하고 멈추면 진짜 증거를 가리키면서 실행된 적 없는 검사를 주장해도 통과한다 —
    앵커는 파일이 진짜인지와 **주장이 그 파일과 맞는지** 둘 다여야 한다.
    자리 규약은 동등성 판정과 같은 함수(`parity.evidence_ref_error`)에서 온다 — 같은 필드를 두 검사기가
    다르게 보면 느슨한 쪽이 done 을 만든다(K-63). 이 함수를 종료 검사·`romeo envelope check`·
    동등성 판정이 모두 지나간다.

    비어 있는 경우는 여기서 보지 않는다 — 부르는 쪽이 '검사 불가' 로 인쇄하고,
    PASS 를 주장한 봉투라면 역할 계약 검사가 EVIDENCE_MISSING 으로 잡는다."""
    raw = _evidence_ref(env)
    if raw is None:
        return None
    path = _inside(project_root, raw)
    if path is None:
        return f"evidence_ref 가 저장소 밖이다 ({raw})"
    place = evidence_ref_error(unit_id, raw)
    if place is not None:
        return f"evidence_ref 가 {place} ({raw})"
    if not path.is_file():
        return f"evidence_ref 가 실재하지 않는다 ({raw}) — 읽은 증거를 지목하지 못하면 통과가 아니다"
    try:
        path.resolve().relative_to(udir.resolve())
    except ValueError:
        return f"evidence_ref 가 이 작업 단위 밖을 가리킨다 ({raw}) — 등록되지 않은 산출물은 인정하지 않는다"
    return _claimed_checks_vs_evidence(project_root, path, env)


def envelope_checks(env, unit_id, role, project_root, udir, roles, schema, side="review",
                    harness_root=None):
    """결과 계약 **하나**를 검사해 `(검사 id, 상태, 이유)` 목록을 돌려준다. 상태는 True·False·UNVERIFIED 다.

    검사는 다섯 가지다 — 스키마 유효, 작업 단위 id 대조, 역할 대조(`role` 이 None 이면 생략),
    가리킨 작업 계약의 재계산 대조·리비전·증거의 자리와 실재, 역할 계약이 허용한 능력 범위.
    close 의 검토 판정과 `romeo envelope check` 가 이 함수 하나만 쓴다 —
    같은 봉투를 두 검사기가 다르게 보면 느슨한 쪽이 done 을 만든다(K-63).

    앞 검사가 성립하지 않으면 뒤 검사는 통과가 아니라 UNVERIFIED 다: 대조할 것이 없었다는 사실을
    PASS 로 인쇄하지 않는다(K-51)."""
    if not isinstance(env, dict):
        return [("ENVELOPE_VALID", False, "결과 계약이 JSON 객체가 아니다")] + [
            (cid, UNVERIFIED, UNREADABLE) for cid in ENVELOPE_CHECKS[1:]]
    why = None
    errs = validate_schema(env, schema)
    if errs:
        why = "; ".join(errs[:2])
    elif env.get("unit_id") != unit_id:
        why = f"다른 작업 단위의 결과다 (unit_id={env.get('unit_id')})"
    elif role is not None and env.get("role") != role:
        why = f"role 이 {role!r} 가 아니다 ({env.get('role')!r})"
    if why is not None:
        return [("ENVELOPE_VALID", False, why)] + [
            (cid, UNVERIFIED, "봉투가 유효하지 않아 대조가 성립하지 않는다") for cid in ENVELOPE_CHECKS[1:]]

    rows = [("ENVELOPE_VALID", True, "")]
    task, task_why = _task_anchor(project_root, unit_id, env, harness_root)
    rows.append(("TASK_ANCHORED", task_why is None, task_why or ""))
    if task is None:
        rows.append(("BASE_SHA", UNVERIFIED,
                     "가리킨 작업 계약을 읽지 못해 base_sha 를 대조할 수 없다 — TASK_ANCHORED 를 먼저 본다"))
    else:
        base_why = _base_sha_anchor(project_root, task)
        rows.append(("BASE_SHA", base_why is None, base_why or ""))
    if _evidence_ref(env) is None:
        rows.append(("EVIDENCE_ANCHORED", UNVERIFIED, "봉투가 evidence_ref 를 비워 두어 대조할 증거가 없다"))
    else:
        ev_why = _evidence_anchor(project_root, udir, unit_id, env)
        rows.append(("EVIDENCE_ANCHORED", ev_why is None, ev_why or ""))
    defects = [msg for _code, msg in _envelope_defects(side, env.get("role"), env, roles)]
    if defects:
        rows.append(("ROLE_CONTRACT", False, "; ".join(defects)))
    elif roles.get(env.get("role")) is None:
        rows.append(("ROLE_CONTRACT", UNVERIFIED,
                     f"역할 계약({env.get('role')!r})을 읽을 수 없어 허용된 능력 범위를 대조할 수 없다"))
    else:
        rows.append(("ROLE_CONTRACT", True, ""))
    return rows


def _check_review(check, udir, unit_id, harness_root, project_root, product=None):
    """검토자가 낸 게이트 판정을 읽어 완료 판정에 연결한다.

    디렉터리가 비어 있지 않다는 것은 검토가 아니다 — 결과 계약을 스키마로 검증하고 `gate_verdict` 를 읽는다.
    **현재 산출물에 대한** 판정 중 PASS 가 아닌 것이 하나라도 남아 있으면 close 는 done 을 선언하지 않는다(D-c).
    판정을 읽을 수 없는 형식이면 통과가 아니라 거부다 — 모르는 것을 통과로 세지 않는다(K-51).

    검토자의 판정은 자기가 본 산출물의 함수다(D-73) — 산출물은 봉투가 지목한 증거의 `head_sha`·`dirty_tree_hash` 로 식별한다.
    `product` 는 지금 닫으려는 산출물(검사 기록 run 의 것)이고, 다른 산출물을 본 판정은 PASS 든 FAIL 이든 이 close 의 대상이
    아니다 — 낡은 PASS 로 새 산출물이 닫히지 않고, 낡은 FAIL 이 새 산출물을 막지 않는다(체크리스트 41). 그런 봉투는 지우지
    않고 `REVIEW_SUPERSEDED` 로 인쇄한다(동등성 게이트의 관측 표본이다). 산출물을 식별하지 못하는 봉투는 미검증이다 — PASS 로도
    지나간 것으로도 세지 않는다. 검사만 다시 기록해도 산출물이 같으면 같은 판정 대상이다. 앵커 검사 5개는 산출물과 무관하게 모든 봉투에 걸린다.
    현재 산출물의 봉투는 그 run 의 증거에 **기록된 그대로**여야 한다(`romeo review record` 가 남긴 sha256 봉인) — 판정 문자열은
    다른 어떤 앵커에도 묶이지 않는다.

    스키마를 통과했다는 것도 검토가 아니다. 봉투는 손으로 쓸 수 있으므로, 그 안의 주장을 **실재하는 것**에 묶는다 —
    가리킨 작업 계약이 실재하고 해시가 맞는가, 그 계약의 base_sha 가 이 이력 안인가, 가리킨 증거가 실재하는가,
    실은 checks 가 그 역할의 계약이 허용한 능력 안인가. 봉투 하나를 보는 규칙은 `envelope_checks` 한 곳에만 있고
    역할 능력 규칙은 동등성 판정과 같은 함수를 쓴다 — 같은 봉투를 두 검사기가 다르게 보면
    느슨한 쪽이 done 을 만든다(K-63).

    여러 봉투의 상태를 합칠 때 FAIL 이 UNVERIFIED 를 이기고 UNVERIFIED 가 PASS 를 이긴다 —
    한 봉투도 대조하지 못한 검사를 PASS 로 인쇄하지 않는다(K-51)."""
    review_dir = udir / "review"
    files = sorted(review_dir.glob("*.json")) if review_dir.is_dir() else []
    if not check("HAS_REVIEW", bool(files),
                 "" if files else "검토자가 필요한 패키지인데 review/ 에 결과 계약(*.json)이 없다"):
        return
    schema = load_json(Path(harness_root) / RESULT_SCHEMA)
    roles = load_role_contracts(harness_root)
    rows = {cid: [] for cid in ENVELOPE_CHECKS}
    verdicts = []
    for p in files:
        try:
            env = load_json(p)
        except Exception as e:
            rows["ENVELOPE_VALID"].append((False, f"{p.name}: JSON 을 읽을 수 없다 ({e})"))
            for cid in ENVELOPE_CHECKS[1:]:
                rows[cid].append((UNVERIFIED, f"{p.name}: {UNREADABLE}"))
            continue
        got = envelope_checks(env, unit_id, "reviewer", project_root, udir, roles, schema,
                              harness_root=harness_root)
        for cid, state, why in got:
            rows[cid].append((state, f"{p.name}: {why}" if why else ""))
        if got[0][1] is True:
            verdicts.append((p.name, env))
    for cid in ENVELOPE_CHECKS:
        states = [s for s, _ in rows[cid]]
        detail = "; ".join(d for s, d in rows[cid] if d and s is not True)
        # FAIL > UNVERIFIED > PASS. 한 봉투도 대조하지 못한 검사를 다른 봉투의 PASS 로 덮지 않는다(K-51).
        check("REVIEW_" + cid,
              False if False in states else (UNVERIFIED if UNVERIFIED in states else True), detail)

    current, stale, unknown = [], [], []
    now_key = _current_approval_key(udir)
    for n, e in verdicts:
        seen, own_rec, why = _reviewed_product(project_root, udir, unit_id, e)
        if seen is None:
            head = _legacy_head(project_root, udir, unit_id, e)
            if head is not None and product is not None and head != product[0]:
                # 봉인 이전 형식의 봉투 — 판정이 본 산출물을 증명할 수 없지만, 그 증거의 head_sha 가 지금 HEAD 가 아니므로
                # 현재 산출물에 대한 판정일 수 없다(산출물 식별에는 head 가 들어 있다). 낡은 것으로 분류하되 그 근거가
                # 미봉인 값임을 인쇄한다. 지금 HEAD 를 가리키는 미봉인 봉투는 그대로 미검증이다(위조 방향을 막는다).
                stale.append((n, e, f"봉인 이전 형식의 기록이라 산출물을 증명하지 못했지만 증거의 head_sha {head[:7]} 가 지금 HEAD 가 아니다 — {why}"))
                continue
            unknown.append((n, e, why))
            continue
        approval = _envelope_approval_key(project_root, unit_id, e)
        reasons = []
        if now_key is not None and approval is not None and approval != now_key:
            reasons.append(f"재승인 전 승인(approved_at {approval[0]})으로 낸 판정")
        if product is not None and seen != product:
            reasons.append(f"다른 산출물({_product_text(seen)})을 본 판정")
        if reasons:
            stale.append((n, e, " · ".join(reasons)))
            continue
        recorded, why = review_record_state(project_root, own_rec, Path(udir) / "review" / n, product=seen)
        if recorded is not True:
            # 판정 문자열 자체는 어떤 앵커에도 묶이지 않는다 — 기록 명령이 남긴 sha256 봉인이 유일한 결박이다.
            unknown.append((n, e, why or "봉투 기록을 대조할 수 없다"))
            continue
        current.append((n, e))
    if stale:
        check("REVIEW_SUPERSEDED", False,
              "; ".join(f"{n}: {e['gate_verdict']}{_findings_gist(e)} — {why}이라 이 close 의 대상이 아니다"
                        for n, e, why in stale)
              + f". 현재 산출물은 {_product_text(product) if product else '?'} 이다"
              f"(검사 기록 run 의 head_sha+dirty_tree_hash, D-73)",
              level="warning")
    # FAIL 사유의 뒷겹. 결과 계약 스키마는 `fail_reasons` 의 **값**만 본다 — 그 필드가 생기기 전에 기록된 판정에도
    # 같은 스키마가 걸리므로 조건부 필수를 걸 수 없다(fixtures/parity 의 관측 케이스가 옛 봉투를 읽는다).
    # 그래서 '사유를 실제로 담았는가' 는 여기서 **지금 닫으려는 산출물의 봉투에 대해서만** 요구한다.
    # 다른 산출물·재승인 전 승인의 봉투(REVIEW_SUPERSEDED)와 PASS·BLOCKED 는 대상이 아니다 —
    # 낡은 기록을 소급해 막으면 이 검사가 하는 말이 '옛 판정이 옛 형식이다' 로 바뀐다.
    no_reasons = [n for n, e in current
                  if e.get("gate_verdict") == "FAIL" and not (e.get("fail_reasons") or [])]
    check("REVIEW_FAIL_REASONS", not no_reasons,
          "; ".join(f"{n}: gate_verdict FAIL 인데 fail_reasons 가 비었다 — "
                    f"무엇이 게이트를 내렸는지 닫힌 목록의 코드로 적는다"
                    f"(core/workflows/review/SKILL.md 「무엇이 FAIL 사유인가」)" for n in no_reasons))
    bad = [(n, e) for n, e in current if e.get("gate_verdict") != "PASS"]
    passes = [n for n, e in current if e.get("gate_verdict") == "PASS"]
    if not verdicts:
        check("REVIEW_VERDICT", False, "review/ 에서 읽을 수 있는 검토자 판정이 없다 — 통과로 세지 않는다")
    elif bad:
        check("REVIEW_VERDICT", False,
              "; ".join(f"{n}: {e['gate_verdict']} (blocked_reason={e.get('blocked_reason')}, "
                        f"findings {len(e.get('findings') or [])}건)" for n, e in bad))
    elif unknown:
        # 어느 산출물을 본 판정인지 하네스가 확인하지 못했다 — PASS 로 세지 않고, 지나간 것으로도 접지 않는다(K-51).
        check("REVIEW_VERDICT", UNVERIFIED,
              "판정이 본 산출물을 확인할 수 없는 봉투가 있다 — " + "; ".join(f"{n}: {why}" for n, _e, why in unknown))
    elif not current:
        check("REVIEW_VERDICT", UNVERIFIED,
              f"현재 산출물({_product_text(product) if product else '?'})에 대한 검토가 아직 없다 — 낡은 판정 {len(stale)}건은 "
              f"다른 산출물·다른 승인의 것이다. 이 산출물을 검토받는다")
    else:
        check("REVIEW_VERDICT", True, "; ".join(f"{n}: PASS" for n in passes))
        if len(passes) < REVIEW_PASS_SAMPLES:
            # D-75 (b) 확정(2026-08-29): close 는 현재 산출물의 PASS 1건으로 닫는다. 표본 2건은 참값을 만들지 않고
            # 같은 산출물 재검토로 PASS 를 기다리는 룰렛만 연다 — 그 한계는 경고로 드러내되 막지 않는다(D-76 도 같은 논리).
            # 바뀐 산출물만 새 검토 1건을 받는다.
            check("REVIEW_SAMPLE", False,
                  f"현재 산출물에 PASS {len(passes)}건 — 같은 산출물에서도 검토 판정은 흔들린다(D-74 관측). "
                  f"D-75 (b) 확정: 1건으로 닫는다. 표본 {REVIEW_PASS_SAMPLES}건은 요구하지 않으며, "
                  f"같은 산출물을 다시 검토해 PASS 를 기다리지 않는다", level="warning")


# D-74 가 게이트에 요구했던 표본 수. close 는 D-75 (b) 로 1건이면 닫고, 이 값은 경고 문구에만 쓴다(D-76 과 같은 논리).
REVIEW_PASS_SAMPLES = 2
# 검토자를 띄운 쪽이 검토 전후에 남기는 방어 검사의 라벨(RUNBOOK §4). 이 두 기록이 검토 시점의 산출물이다.
DEFENSIVE_LABELS = ("review-tree-before", "review-tree-after")


def _run_of_envelope(env):
    """봉투가 가리킨 작업 계약 경로 `docs/work/<id>/task/<run>-<role>.json` 의 `<run>`. 규약 밖이면 None."""
    raw = ((env.get("task_envelope_ref") or {}).get("path") or "").replace("\\", "/")
    name = raw.rsplit("/", 1)[-1]
    role = env.get("role") or ""
    suffix = f"-{role}.json"
    if not name.endswith(suffix) or len(name) <= len(suffix):
        return None
    return name[:-len(suffix)]


def _reviewed_product(project_root, udir, unit_id, env):
    """검토자가 실제로 본 산출물 — **검토 run 자신의 증거**에서 읽는다. (식별자, 못 읽은 이유)

    `evidence_ref` 는 봉투 작성자가 고르는 포인터라 판정을 다른 산출물로 옮기는 데 쓸 수 있다(문자열 하나로 FAIL 을 낡은 것으로,
    옛 PASS 를 현재 것으로 만든다 — 설계 검토가 재현했다). 검토 시점의 산출물은 검토자를 띄운 쪽이 그 run 의 증거에
    방어 검사로 기록한다(RUNBOOK §4·§6.6: `evidence/<run>.yaml` 의 review-tree-before/after). 그래서 산출물 식별은
    그 증거에서 읽고, `evidence_ref` 의 산출물은 그것과 **같아야** 한다 — 다르면 그 봉투는 어느 산출물을 본 판정인지 말할 수 없다.
    원시 로그가 그 체크아웃에 있으면 마지막 명령의 봉인(head/tree 줄)까지 대조한다."""
    run = _run_of_envelope(env)
    if run is None:
        return None, None, "작업 계약 경로가 <run>-<role>.json 규약이 아니라 검토 run 의 증거를 찾을 수 없다"
    own_rel = f"docs/work/{unit_id}/evidence/{run}.yaml"
    own_path = Path(udir) / "evidence" / f"{run}.yaml"
    if not own_path.is_file():
        return None, None, (f"검토 run {run} 의 증거({own_rel})가 없다 — 검토 시점의 산출물을 하네스가 기록하지 않았다"
                            f"(RUNBOOK §4 방어 검사를 그 run 에 남긴다)")
    try:
        own_rec = load_yaml(own_path)
    except Exception as e:
        return None, None, f"검토 run {run} 의 증거를 읽을 수 없다 ({e})"
    if not isinstance(own_rec, dict):
        return None, None, f"검토 run {run} 의 증거가 증거 기록(YAML 매핑)이 아니다"
    # 검토 시점의 산출물은 방어 검사(review-tree-before/after)가 기록한다 — 그 두 기록이 실재하고 원시 로그와 맞아야
    # '검토 run 의 증거' 다. 계약 파일을 다른 run 이름으로 복사해 아무 증거나 자기 것으로 삼는 길을 여기서 막는다.
    cmds = [c for c in (own_rec.get("commands") or []) if isinstance(c, dict)]
    guards = {label: [c for c in cmds if c.get("id") == label] for label in DEFENSIVE_LABELS}
    missing = [label for label, recs in guards.items() if not recs]
    if missing:
        return None, None, (f"검토 run {run} 의 증거에 방어 검사 {missing} 기록이 없다 — 검토자를 띄운 쪽이 그 run 에 "
                            f"review-tree-before/after 를 남겨야 검토 시점의 산출물이 기록된다(RUNBOOK §4)")
    products = {}
    for label, recs in guards.items():
        state, why = command_log_state(project_root, recs[-1])
        if state is not True:
            # None(로그 없음)도 통과가 아니다 — 검사 기록 면의 EVIDENCE_LOG 와 같은 기준이다(K-63).
            return None, None, f"검토 run {run} 의 {label} 기록을 원시 로그로 확인하지 못했다 — {why}"
        products[label] = _product_of(recs[-1])
        if products[label] is None:
            return None, None, (f"검토 run {run} 의 {label} 기록에 산출물 식별이 없다 — 명령별 봉인이 없던 시절의 기록이라 "
                                f"검토 시점의 산출물을 확인할 수 없다")
    # 검토 시점의 산출물은 **방어 검사 기록**의 것이다 — run 최상위나 마지막 명령이 아니다. 최상위·마지막 명령은 그 run 에 나중에
    # 명령을 하나 더 기록하는 것으로 '지금' 으로 바뀐다(옛 run 에 새 봉투를 기록하면 옛 판정이 현재 산출물로 옮겨지던 자리).
    before, after = products["review-tree-before"], products["review-tree-after"]
    if before != after:
        return None, None, (f"검토 run {run} 의 방어 검사가 무효다 — 검토 전({_product_text(before)})과 후({_product_text(after)})의 "
                            f"산출물이 다르다. 검토 중 작업 트리가 바뀌었다(RUNBOOK §4)")
    own = after
    ref = _evidence_ref(env)
    if ref is None:
        return None, None, "봉투가 evidence_ref 를 비워 두어 읽은 산출물을 지목하지 않았다"
    seen, err = _evidence_product(Path(project_root), ref)
    if seen is None:
        return None, None, f"evidence_ref 의 산출물을 읽을 수 없다 — {err}"
    if seen != own:
        return None, None, (f"evidence_ref 가 지목한 산출물({_product_text(seen)})이 검토 run {run} 이 기록한 산출물"
                            f"({_product_text(own)})과 다르다 — 판정이 본 것과 다른 증거를 가리킨다")
    return own, own_rec, None


def _legacy_head(project_root, udir, unit_id, env):
    """봉인 이전 형식(방어 검사 기록에 명령별 head/tree 가 없는) 검토 run 의 봉투가 지목한 증거의 **미봉인** head_sha. 아니면 None.

    봉인 형식의 기록(명령별 값이 있는데 로그가 없거나 어긋나는 경우)은 여기 오지 않는다 — 그것은 미검증으로 남아 막는다.
    옛 형식이라는 판정은 방어 검사 기록에 `head_sha` 키가 하나도 없다는 사실로 한다."""
    run = _run_of_envelope(env)
    if run is None:
        return None
    own_path = Path(udir) / "evidence" / f"{run}.yaml"
    if not own_path.is_file():
        return None
    try:
        own = load_yaml(own_path)
    except Exception:
        return None
    cmds = [c for c in ((own or {}).get("commands") or []) if isinstance(c, dict)]
    defensive = [c for c in cmds if c.get("id") in DEFENSIVE_LABELS]
    if not defensive or any(isinstance(c.get("head_sha"), str) and c.get("head_sha") for c in defensive):
        return None
    # 기록만 지워 옛 형식으로 위장한 경우는 로그가 잡는다(로그에 봉인 줄이 남아 있다) — 그것은 옛 형식이 아니라 위반이다.
    for c in defensive:
        state, _why = command_log_state(project_root, c)
        if state is False:
            return None
    ref = _evidence_ref(env)
    if ref is None:
        return None
    seen, _err = _evidence_product(Path(project_root), ref)
    return seen[0] if seen else None


def _current_approval_key(udir):
    try:
        fm, _ = frontmatter.read(Path(udir) / "spec.md")
        return approval_key(fm) if fm.get("approved_at") else None
    except Exception:
        return None


def _envelope_approval_key(project_root, unit_id, env):
    """봉투가 가리킨 작업 계약의 base_sha 커밋이 담은 승인. 재승인 뒤에는 이전 승인으로 낸 판정을 가려내는 데 쓴다."""
    raw = (env.get("task_envelope_ref") or {}).get("path") or ""
    path = _inside(project_root, raw)
    if path is None or not path.is_file():
        return None
    try:
        sha = (json.loads(path.read_text(encoding="utf-8")) or {}).get("base_sha")
        return approval_key_at(project_root, sha, unit_id) if sha else None
    except Exception:
        return None


def _findings_gist(env):
    findings = env.get("findings") or []
    if not findings:
        return ""
    first = str((findings[0] or {}).get("summary", ""))[:60]
    return f"(findings {len(findings)}건 — 첫째: {first})"


def _finish(checks, fm, body, spec, runs, dry_run, project_root, ev):
    """PASS 는 '어긴 것이 없다' 가 아니라 '전부 대조했고 어긴 것이 없다' 다.
    성립하지 않은 검사(UNVERIFIED)가 하나라도 있으면 done 을 선언하지 않는다 — 미검증은 완료가 아니다(K-51).
    판정은 **검사 기록** run(`ev`)에 적는다 — 마지막 파일이 아니라(체크리스트 41). evidence 링크는 모든 run 을 남긴다:
    방어 검사 run 도 이 단위의 증거다."""
    failed = [c for c in checks if c["level"] == "error" and not c["ok"]]
    unverified = [c for c in checks if c["level"] == UNVERIFIED]
    verdict = "PASS" if not failed and not unverified else "FAIL"
    result = {"unit_id": fm.get("id"), "verdict": verdict, "checks": checks, "dry_run": dry_run, "updated": []}
    if verdict == "PASS" and not dry_run and ev is not None:
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
            block = (["", f"close PASS · {fm['closed_at']} · HEAD {str(ev.get('head_sha', ''))[:12]} · 검사 기록 {_run_name(ev)}", ""]
                     + [f"- [{p}]({p}) — exit codes {[c['exit_code'] for c in r.get('commands', [])]}"
                        + (" (검사 기록)" if r is ev else "") for p, r in zip(ev_links, runs)] + [""])
            lines[i + 1:j] = block
            body = "\n".join(lines)
        except StopIteration:
            pass
        frontmatter.write(spec, fm, body)
        result["updated"].append(str(spec))
        path = ev.pop("_path")
        ev["verdict"] = "PASS"
        ev["close"] = {"at": fm["closed_at"], "checks": [{"id": c["id"], "ok": c["ok"], "level": c["level"], "detail": c["detail"]} for c in checks]}
        Path(path).write_text(dump_yaml(ev), encoding="utf-8")
        result["updated"].append(path)
    return result


def mark_of(c):
    """검사 한 줄의 인쇄 토큰. 검사가 성립하지 않은 줄은 PASS 도 FAIL 도 아닌 UNVERIFIED 로 인쇄한다(K-51)."""
    if c["level"] == UNVERIFIED:
        return "UNVERIFIED"
    return "PASS" if c["ok"] else ("WARN" if c["level"] == "warning" else "FAIL")


def format_close(result):
    lines = [f"romeo close {result['unit_id']} → {result['verdict']}" + (" (dry-run)" if result["dry_run"] else "")]
    for c in result["checks"]:
        lines.append(f"  [{mark_of(c)}] {c['id']}" + (f" — {c['detail']}" if c["detail"] else ""))
    if result["verdict"] == "FAIL" and not any(c["level"] == "error" and not c["ok"] for c in result["checks"]):
        # 어긴 줄이 하나도 없는데 FAIL 이면 이유는 '대조하지 못했다' 뿐이다. 그 사실을 말해 준다.
        lines.append("  어긴 검사는 없으나 성립하지 않은 검사가 있다 — 미검증은 완료가 아니다(K-51). "
                     "위 UNVERIFIED 줄을 해소한 뒤 다시 실행한다.")
    for u in result["updated"]:
        lines.append(f"  updated: {u}")
    return "\n".join(lines)
