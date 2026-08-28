"""/plan-close 검사기. 결정적 차단 검사만 실패로 처리하고, 휴리스틱은 경고로 남긴다(C-E3). 검증 상태는 저장하지 않고 여기서 계산한다."""
import json
import re
import subprocess
from pathlib import Path

import yaml

from . import HARNESS_ROOT, frontmatter
from .docs import find_unit_dir
from .evidence import (RERUN_TIMEOUT, command_log_state, dirty_tree_hash_excluding, exclusions,
                       list_runs, replay)
from .gitinfo import head_sha
from .parity import _envelope_defects, evidence_ref_error, load_role_contracts, task_ref_error
from .policy import classification_from_frontmatter, load_policy, load_project_state, route
from .schema import validate as validate_schema
from .util import dump_yaml, load_json, load_yaml, now_iso, rel, sha256_bytes, sha256_file, today
from .validate import UNCHECKED_RE, validate_doc

CHECKS_BLOCK_RE = re.compile(r"```yaml\s*\n(required_checks:.*?)\n```", re.S)
RESULT_SCHEMA = "core/schemas/result-envelope.json"

# 검사가 성립하지 않았다는 상태. 어긴 것(FAIL)과 구분해 인쇄하되 **통과로 세지 않는다** —
# 대조하지 못했다는 사실을 PASS 로 인쇄하지 않고, 하나라도 남아 있으면 done 을 선언하지 않는다(K-51).
UNVERIFIED = "unverified"

# 결과 계약 하나에 적용하는 검사와 그 순서. close 와 `romeo envelope check` 가 같은 목록을 쓴다.
ENVELOPE_CHECKS = ("ENVELOPE_VALID", "TASK_ANCHORED", "BASE_SHA", "EVIDENCE_ANCHORED", "ROLE_CONTRACT")
UNREADABLE = "봉투를 읽을 수 없어 대조가 성립하지 않는다"


def required_checks(body):
    m = CHECKS_BLOCK_RE.search(body)
    if not m:
        return []
    data = yaml.safe_load(m.group(1)) or {}
    return data.get("required_checks") or []


def _plan_key(plan):
    """검증 계획을 대조용 형태로 줄인다 — 무엇을 어떤 기대로 실행하기로 했는가."""
    return [(str((rc or {}).get("id")), str((rc or {}).get("command")), str((rc or {}).get("expect")))
            for rc in plan]


def _check_plan_committed(check, project_root, spec, plan):
    """지금 읽고 있는 검증 계획이 **커밋된 계획**과 같은지 본다.

    재실행 대조를 붙이자 위조가 한 겹 옆으로 갔다: 실패하는 검사(`false`)를 지우고 `true` 로 바꾼 뒤
    그것을 진짜로 실행하면 기록도 로그도 재실행도 전부 맞는다. 고쳐진 것은 증거가 아니라 **주장 자체**다.
    `docs/work/<unit>/` 는 신선도 계산에서 제외돼 있어(기록 행위가 트리를 바꾸므로) 이 편집은 어디에도 걸리지 않았다.

    그래서 계획만은 커밋된 것과 대조한다 — 커밋되지 않은 계획은 어느 이력에도 없고 되짚을 수 없다.
    **이것은 절반의 앵커다**: 계획을 고치고 커밋한 경우는 여전히 통과한다. 계획이 *승인 시점의* 계획인지까지
    묶으려면 승인 기록이 그때의 계획을 남겨야 하고, 그것은 승인을 기록하는 쪽의 일이다."""
    relpath = rel(spec, project_root)
    proc = subprocess.run(["git", "show", f"HEAD:{relpath}"], cwd=str(project_root), capture_output=True)
    if proc.returncode != 0:
        check("CHECK_PLAN_COMMITTED", UNVERIFIED,
              f"HEAD 에 {relpath} 가 없다 — 커밋되지 않은 검증 계획은 대조할 원본이 없다. "
              f"승인된 spec.md 를 커밋한 뒤 다시 실행한다(D-a)")
        return
    _fm, committed_body = frontmatter.split(proc.stdout.decode("utf-8", "replace"))
    try:
        committed = required_checks(committed_body)
    except Exception as e:
        check("CHECK_PLAN_COMMITTED", UNVERIFIED, f"HEAD 의 {relpath} 에서 검증 계획을 읽을 수 없다 ({e})")
        return
    if _plan_key(committed) != _plan_key(plan):
        check("CHECK_PLAN_COMMITTED", False,
              f"검증 계획이 HEAD 에 커밋된 것과 다르다 — 커밋 {_plan_key(committed)} vs 지금 {_plan_key(plan)}. "
              f"실행할 검사를 바꾸는 것은 증거가 아니라 주장을 바꾸는 것이다: 승인을 다시 받고 커밋한다")
        return
    check("CHECK_PLAN_COMMITTED", True, f"검사 {len(plan)}건이 HEAD 의 spec.md 와 같다")


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
    detail = "; ".join(details)
    if False in states:
        check("EVIDENCE_LOG", False, detail)
    elif None in states:
        check("EVIDENCE_LOG", UNVERIFIED, detail)
    else:
        check("EVIDENCE_LOG", True, f"{len(cmds)}건이 원시 로그·log_sha256 과 일치")


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
        code, why = replay(project_root, cmd, timeout=timeout)
        ran = True
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
        return _finish(checks, fm, body, spec, runs, dry_run, project_root)
    ev = runs[-1]
    cur_head = head_sha(project_root)
    cur_dirty = dirty_tree_hash_excluding(project_root, exclusions(unit_id))
    check("FRESH_HEAD", ev.get("head_sha") == cur_head, f"evidence {str(ev.get('head_sha'))[:12]} vs 현재 {cur_head[:12]}")
    check("FRESH_TREE", ev.get("dirty_tree_hash") == cur_dirty, f"evidence {str(ev.get('dirty_tree_hash'))[:12]} vs 현재 {cur_dirty[:12]} (tracked 수정·staged·untracked 포함)")
    cmds = {c["command"]: c for c in ev.get("commands", [])}
    plan = required_checks(body)
    if not plan:
        # 실행 대조의 앵커(검증 계획)가 없다. 검사할 것이 0건인 것을 조용히 지나가지 않는다 — 인쇄한다(K-51).
        check("REQUIRED_CHECK", UNVERIFIED,
              "spec.md 의 검증 계획에 required_checks 가 없다 — evidence 와 대조할 검사가 하나도 없다")
    for rc in plan:
        cmd = rc.get("command", "")
        rec = cmds.get(cmd)
        if rec is None:
            check("REQUIRED_CHECK", False, f"{rc.get('id')}: evidence 에 명령 없음 — {cmd}")
        else:
            check("REQUIRED_CHECK", rec["exit_code"] == 0, f"{rc.get('id')}: exit {rec['exit_code']} — {cmd}")
    _check_evidence_logs(check, project_root, ev)
    # 라우팅과 가드 승인은 **재실행보다 먼저** 판정한다. 재실행은 spec.md 의 셸 명령을 실제로 돌리므로,
    # 승인되지 않은 가드가 걸린 단위에서 그것을 먼저 돌리면 K-66(승인 없이 실행하지 않는다)을 어긴다.
    # dry-run 도 마찬가지다 — 읽기만 한다고 알려진 명령이 부작용을 내면 안 된다.
    out = route(classification_from_frontmatter(fm), pol, project_state=load_project_state(project_root))
    unapproved = []
    for g in out["guards"]:
        approved = any(a.get("guard") == g["id"] for r in runs for a in r.get("approvals", []))
        check("GUARD_APPROVED", approved, f"{g['id']} ({g['name']}) 승인 기록 없음")
        if not approved:
            unapproved.append(g["id"])
    if plan:
        _check_plan_committed(check, project_root, spec, plan)
        if unapproved:
            _skip_rerun(check, plan,
                        "승인되지 않은 실행 가드가 있어 재실행하지 않았다 — 승인 없이 실행하지 않는다(K-66): "
                        + ", ".join(unapproved))
        else:
            _check_rerun(check, project_root, unit_id, plan, cmds, rerun, rerun_timeout)
    check("AC_ALL_CHECKED", not UNCHECKED_RE.search(body), f"미체크 {len(UNCHECKED_RE.findall(body))}개")
    check("NO_OPEN_LOOP", "NEEDS_INPUT" not in body, f"NEEDS_INPUT {body.count('NEEDS_INPUT')}곳")
    check("HAS_CHANGE", bool(ev.get("changed_files")), f"changed_files {ev.get('changed_files')}" if ev.get("changed_files") else "changed_files 가 비어 있다 — 아무것도 바뀌지 않았다면 done 이 아니다")
    spec_sha = sha256_file(spec)
    spec_same = (ev.get("spec_ref") or {}).get("sha256") == spec_sha
    check("SPEC_UNCHANGED_SINCE_EVIDENCE", spec_same, "" if spec_same else "spec.md 가 evidence 이후 바뀜(AC 체크 등). 확인만.", level="warning")
    if out["reviewer"] != "none":
        _check_review(check, udir, fm.get("id") or unit_id, harness_root, project_root)
    return _finish(checks, fm, body, spec, runs, dry_run, project_root)


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
                                 harness_root=harness_root, base_sha=task["base_sha"])
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


def _check_review(check, udir, unit_id, harness_root, project_root):
    """검토자가 낸 게이트 판정을 읽어 완료 판정에 연결한다.

    디렉터리가 비어 있지 않다는 것은 검토가 아니다 — 결과 계약을 스키마로 검증하고 `gate_verdict` 를 읽는다.
    PASS 가 아닌 판정이 하나라도 남아 있으면 close 는 done 을 선언하지 않는다(D-c).
    판정을 읽을 수 없는 형식이면 통과가 아니라 거부다 — 모르는 것을 통과로 세지 않는다(K-51).

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

    bad = [(n, e) for n, e in verdicts if e.get("gate_verdict") != "PASS"]
    if not verdicts:
        detail = "review/ 에서 읽을 수 있는 검토자 판정이 없다 — 통과로 세지 않는다"
    elif bad:
        detail = "; ".join(f"{n}: {e['gate_verdict']} (blocked_reason={e.get('blocked_reason')}, "
                           f"findings {len(e.get('findings') or [])}건)" for n, e in bad)
    else:
        detail = "; ".join(f"{n}: PASS" for n, _ in verdicts)
    check("REVIEW_VERDICT", bool(verdicts) and not bad, detail)


def _finish(checks, fm, body, spec, runs, dry_run, project_root):
    """PASS 는 '어긴 것이 없다' 가 아니라 '전부 대조했고 어긴 것이 없다' 다.
    성립하지 않은 검사(UNVERIFIED)가 하나라도 있으면 done 을 선언하지 않는다 — 미검증은 완료가 아니다(K-51)."""
    failed = [c for c in checks if c["level"] == "error" and not c["ok"]]
    unverified = [c for c in checks if c["level"] == UNVERIFIED]
    verdict = "PASS" if not failed and not unverified else "FAIL"
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
        last["close"] = {"at": fm["closed_at"], "checks": [{"id": c["id"], "ok": c["ok"], "level": c["level"], "detail": c["detail"]} for c in checks]}
        Path(path).write_text(dump_yaml(last), encoding="utf-8")
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
