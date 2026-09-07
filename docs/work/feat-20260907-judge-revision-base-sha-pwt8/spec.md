---
id: feat-20260907-judge-revision-base-sha-pwt8
type: spec
title: 종료 검사는 base_sha 시점의 하네스가 낸다 — 규칙을 만든 단위가 자기 규칙으로 닫히지 않는다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: low
status: active
approved_at: '2026-09-07T19:07:03+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: [inputs/probe-2026-09-07.patch]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-07'
updated: '2026-09-07'
approval_history:
- {approved_at: '2026-09-07T18:26:46+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-07T19:07:03+09:00',
  reason: 1회차 검토자 FAIL findings 1건 — AC-3 의 「파일 하나가 없어도 같다」가 판정이 JUDGE_REVISION 앞에서 읽는 파일(정책표·스키마)에는 참일
    수 없었다(그 파일이 없으면 load_policy 가 먼저 ERROR 로 끝난다 — 실행 재현). 첫 문장의 「docs/ 밖」도 대조에서 뺀 .harness/ 를 포함했다. AC-3
    을 두 자리에서 좁혔다. 산출물은 문제없다 — 검토자가 13/13·원시 로그·allowed_paths 를 확인했다}
---

# 종료 검사는 base_sha 시점의 하네스가 낸다 — 규칙을 만든 단위가 자기 규칙으로 닫히지 않는다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260907-judge-revision-base-sha-pwt8 --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 종료 검사(`romeo close`)를 **승인 커밋(base_sha) 시점의 하네스**가 돌리게 한다. 지금은 구현자 워크트리의
  `bin/romeo` — 그 단위가 바꾼 하네스 — 가 자기 단위를 판정한다(RUNBOOK §3.8). 앞으로는 ① `close` 에 검사
  `JUDGE_REVISION` 이 생겨, 판정 대상이 하네스 저장소 자신이면 판정을 낸 하네스의 파일(`docs/`·`.harness/` 밖 추적 파일 전부 — 두 곳은 판정이 읽지 않는다)이
  승인 커밋의 파일과 **전부 같아야** 통과하고, 하나라도 다르거나 없으면 거부한다 — 워커 트리가 자기를 판정하면 FAIL 이다.
  ② 절차(RUNBOOK §3.8 · plan-close 절차 · 두 런타임의 plan-close 매핑)는 승인 커밋을 `git archive` 로 꺼낸 스냅샷의
  `bin/romeo close --unit <id> --root <구현 워크트리>` 로 바뀐다. 남의 저장소(트리에 하네스가 없는 루트)의 판정은 바뀌지 않는다.
- **왜 지금:** 2026-09-07 진단이 자가봉착의 뿌리를 「판정하는 하네스와 판정받는 하네스가 같은 리비전」으로 지목했고(권고 1),
  D-81 이 이것을 M5 보다 앞에 두었다 — 선행 ①(Q-66·Q-67)은 닫혔다. 실측 사례가 Q-43 이다: 검토자를 끄는 오버레이를
  추가한 단위가 그 오버레이에 걸려 검토 없이 닫혔다. 이 단위가 **자기적용의 마지막 라운드**다 — 성립하면 그다음부터
  새 규칙은 다음 단위부터 적용된다. 관통 도중에는 하네스를 고칠 수 없으므로(§10 동결) 관통 사이인 지금 닫는다.
- **기대 결과:** 승인 커밋 스냅샷의 `bin/romeo` 가 현재 트리를 `--root` 로 판정해 검사 목록과 종료 코드를 낸다(스택 트레이스
  아님) — 스냅샷 폴더는 git 저장소가 아니어도 된다. 그 출력의 `JUDGE_REVISION` 은 PASS 이고, 워커 트리 자신의 `bin/romeo`
  로 돌리면 같은 검사가 FAIL 로 인쇄되며 어느 파일이 다른지 보인다. 규칙이 사는 문서 셋이 같은 변경에서 그 규칙을 말한다.
  이 단위 자신은 D-81 대로 **옛 close**(승인 커밋 스냅샷)가 닫는다 — 그 출력에는 `JUDGE_REVISION` 줄이 없다.
- **수용 기준:**
  - [ ] AC-1 `romeo close` 가 검사 `JUDGE_REVISION` 을 인쇄한다. 판정 대상 루트의 승인 커밋(이력에서 찾은 현재 승인의 첫 커밋)
        트리에 `romeo/__init__.py` 가 있으면 자기적용이고, 그 트리의 `docs/`·`.harness/` 밖 추적 파일 전부가 판정을 낸 하네스(실행된
        `bin/romeo` 의 체크아웃)의 같은 경로에 **같은 blob 해시**로 있어야 PASS 다 — 내용만 본다(실행 비트·더해진 파일은 보지 않는다). 하나라도 다르거나 없으면 FAIL 이고, 그 문장에
        승인 커밋 앞 12자·다른 파일 수·다른 경로(최대 3개)가 들어간다. 승인 커밋 뒤에 `docs/`·`.harness/` 밖 추적 파일을 바꾼 커밋이 있는
        체크아웃이 자기를 판정하면(같은 폴더를 `--root` 로) FAIL 이다.
  - [ ] AC-2 승인 커밋을 `git archive` 로 꺼낸 스냅샷 폴더(git 저장소 아님)의 `bin/romeo close --unit <id> --root <그 트리>` 는
        `JUDGE_REVISION` PASS 이고, 나머지 검사가 전부 통과하는 단위는 그 호출 한 번으로 `status: done` 이 된다(`--dry-run` 없이 부른 실제 종료). 출력에
        `Traceback` 이 없다. `--dry-run` 도 같은 판정을 인쇄한다.
  - [ ] AC-3 스냅샷의 `docs/`·`.harness/` 밖 파일 하나만 내용이 달라도(예: `romeo/close.py` 끝에 한 줄) FAIL 이고 그 경로가 문장에
        인쇄된다. 판정이 이 검사 **앞에서 읽지 않는** 파일 하나가 없어도 같다(예: `README.md`). 판정이 이 검사 앞에서 읽는 파일
        (정책표·스키마)이 없으면 그 읽기가 먼저 오류 문장과 종료 코드 1 로 끝나는 기존 경로이고, 그것을 바꾸지 않는다 — 어느 쪽이든
        완료가 선언되는 일은 없다. 스냅샷의 `docs/`·`.harness/` 아래 파일이 달라도 판정은 바뀌지 않는다.
  - [ ] AC-4 승인 커밋 트리에 `romeo/__init__.py` 가 없는 루트(남의 저장소)에서는 `JUDGE_REVISION` 이 「자기적용이 아니다」 문장으로
        PASS 이고, 승인 커밋을 이력에서 찾지 못하면(예: 커밋하지 않은 재승인) 미검증(UNVERIFIED)이다 — 통과가 아니다. 이 검사는 검사 목록에서 `FRESH_HEAD` 미검증
        조기 종료 **뒤**·검사 기록 선택 **앞**에 온다 — 이력 없는 루트의 판정(Q-67)은 바뀌지 않는다.
  - [ ] AC-5 규칙이 사는 자리 셋이 같은 변경에서 새 규칙을 말한다 — `core/workflows/plan-close/SKILL.md` 절차 2 가 「판정하는
        하네스는 승인 커밋 시점의 것」과 `JUDGE_REVISION` 의 조건(자기적용 판별·비교 대상·`docs/`·`.harness/` 제외·거부 뜻)을 적고,
        `adapters/orca/RUNBOOK.md` §3.8 이 종료 검사를 승인 커밋 스냅샷(`git archive <base-sha>`)의 `bin/romeo` 로
        `--root "$W"` 를 주어 돌리는 명령으로 바뀌며 구현자 워크트리의 `bin/romeo` 로 `close` 를 돌리는 명령(`"$W/bin/romeo" close`)은
        사라진다. §3.1 의 「계약 입력이 바뀌었으면 `<base-sha>` 를 그 변경 뒤로 잡는다」는 「재승인한다 — 판정 하네스는 승인 커밋의
        것이다」로 바뀐다. `adapters/{claude,codex}/workflows/plan-close.md` 와 컴파일 산출물(`.claude/skills/plan-close/SKILL.md` ·
        `.agents/skills/plan-close/SKILL.md`)이 같은 문장을 담고 `bin/romeo compile --check` 가 통과한다.
  - [ ] AC-6 기존 검사(`tests/`)는 한 줄도 고치지 않고 전부 통과한다 — 늘어난 검사는 이 단위가 더한 `tests/test_judge_revision.py`
        뿐이다. `romeo close` 첫 줄 형식(`romeo close <id> → PASS|FAIL`)과 다른 검사 id·문장은 바뀌지 않는다.
  - [ ] AC-7 `docs/planning/open-questions.md` 의 Q-43 행이 해소 표기되고(근거 열의 파일 경로는 남긴다), 이번 작업이 발견했으나
        고치지 않은 결함이 새 행(Q-83~)으로 열린다. 진단 문서(`docs/reviews/2026-09-07-self-application-diagnosis/`)는 고치지 않는다.
- **위험과 되돌리기:** 종료 검사가 **더 엄격해진다** — 이 저장소의 단위는 이제 자기 트리의 `bin/romeo` 로 닫히지 않는다.
  현재 작업 공간에서 직접 구현한 단위(T0)도 `docs/`·`.harness/` 밖을 바꿨으면 승인 커밋 스냅샷이 닫아야 한다(비용: `git archive` 한 줄).
  문서만 바꾼 단위는 하네스 파일이 그대로라 지금처럼 닫힌다. 남의 저장소는 영향이 없다. 알려진 한계 둘 — ① 판정 하네스에
  **더해진** 파일은 보지 않는다(`close` 가 읽는 파일은 이름이 고정돼 있어 더해진 파일이 판정을 바꾸지 못한다). ② `close` 가 읽는
  형식(증거·봉투·frontmatter)을 바꾸는 단위는 옛 판정자가 그 형식을 모르므로 한 단위로 닫히지 않는다 — 그런 단위는 쪼갠다.
  되돌리기는 `git revert <이 단위의 통합 커밋>` — 외부 상태를 바꾸지 않는다.
- **결정 필요:** 없음.


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/close.py` · `romeo/gitinfo.py` · `tests/test_judge_revision.py` · `core/workflows/plan-close/SKILL.md` · `adapters/orca/RUNBOOK.md` · `adapters/claude/workflows/plan-close.md` · `adapters/codex/workflows/plan-close.md` · `.claude/skills/plan-close/SKILL.md` · `.agents/skills/plan-close/SKILL.md` · `.harness/compiled.yaml` · `docs/planning/open-questions.md` · `docs/planning/progress.md` · `docs/work/feat-20260907-judge-revision-base-sha-pwt8/` (뒤 컴파일 산출물 셋은 어댑터 매핑을 고치면 `romeo compile` 이 다시 만든다)
- 영향을 받는 부분: `romeo close` 의 판정 경로(모든 단위가 지난다 — 검사 한 건이 늘고 자기 판정이 거부된다) · RUNBOOK §3.8 의 종료 검사 절차와 §3.1 의 `<base-sha>` 문단 · plan-close 스킬(두 런타임)
- 바꾸지 않는 것(비범위): `romeo/envelope.py`·`romeo/evidence.py`·`romeo/run_unit.py`(`envelope check`·`evidence checks` 는 판정이 아니라 사전 검사·증거 생성이므로 구현자 워크트리의 `bin/romeo` 로 그대로 돈다 — 그것이 판정에 닿는지는 열린 질문으로 남긴다) · `core/principles/AGENTS.core.md`(§10 동결·반복 중단은 D-81 대로 유지) · `format_close` 의 첫 줄 · `attempts.yaml` 에 판정 하네스를 남기는 것(Q-02 재료 — 열린 질문으로) · `docs/reviews/…` 진단 문서 · `docs/decisions/decision-register.md`(새 결정 없음 — D-81 의 집행이다) · 다른 열린 질문(Q-23·34·35·64·69·70·71~82)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | `close` 가 판정 하네스의 리비전을 대조한다(`JUDGE_REVISION`) | `romeo/gitinfo.py` 에 `tree_blobs(cwd, rev, exclude_prefixes=())` — `git ls-tree -r -z <rev>` 를 읽어 `{path: blob_sha}`(mode 100644·100755 만, `exclude_prefixes` 로 시작하는 경로 제외) — 와 `blob_sha_of(path)` — 파일 바이트를 git 의 blob 해시(`sha1("blob <len>\0" + bytes)`)로 — 를 더한다. `romeo/close.py` 에 `_judge_revision(project_root, unit_id, harness_root)` 를 더한다: `approval_commit(project_root, unit_id)` 가 ValueError 면 `(UNVERIFIED, "승인 커밋을 이력에서 찾지 못해 판정 하네스를 대조할 수 없다 — <이유>")`; `tree_blobs(project_root, sha, exclude_prefixes=("docs/", ".harness/"))` 에(두 곳은 판정이 `harness_root` 에서 읽지 않는다 — 증거 신선도의 `exclusions` 와 같은 이유) `romeo/__init__.py` 가 없으면 `(True, "이 루트의 승인 커밋 <sha12> 트리에 하네스(romeo/__init__.py)가 없다 — 자기적용이 아니다 · 판정 하네스 <harness_root>")`; 있으면 각 경로에 대해 `harness_root/path` 가 없거나 `blob_sha_of` 가 다르면 모아서, 있으면 `(False, "판정 하네스가 승인 커밋 <sha12> 의 하네스가 아니다 — <n>개 파일이 다르거나 없다(<경로 최대 3개>) · 판정받는 리비전이 판정하고 있다. 승인 커밋의 스냅샷에서 꺼낸 romeo close 로 --root 를 주어 다시 돌린다")`, 없으면 `(True, "판정 하네스 = 승인 커밋 <sha12> 의 하네스 (<n>개 파일 대조 · <harness_root>)")`. `close_unit` 에서 `cur_head` 를 얻은 직후(`FRESH_HEAD` 미검증 조기 종료 뒤)·`select_check_record` 앞에 `check("JUDGE_REVISION", ok, detail)` 로 부른다 — FAIL 이어도 조기 종료하지 않는다. `format_close` 는 손대지 않는다 | 소비: `docs.approval_commit`(있음) → 생산: `gitinfo.tree_blobs`·`gitinfo.blob_sha_of` · 검사 행 `{"id": "JUDGE_REVISION", "ok": bool, "level": "error"\|"unverified"}` | check-1~check-6 | `git revert` |
| 2 | 규칙이 사는 문서 셋이 같은 변경에서 참이 된다(§11) | `core/workflows/plan-close/SKILL.md` 절차 2 의 첫 항목 앞에 굵은 문단 하나: 「**판정하는 하네스는 승인 커밋 시점의 것이다.** `romeo close` 는 그 단위의 승인 커밋을 스냅샷으로 꺼낸 `bin/romeo` 로 `--root <판정 대상 루트>` 를 주어 돌린다. 판정 대상의 승인 커밋 트리에 `romeo/__init__.py` 가 있으면(하네스 저장소 자신) 판정을 낸 하네스의 `docs/`·`.harness/` 밖 추적 파일 전부가 그 커밋의 것과 같아야 하고(`JUDGE_REVISION` — 두 곳은 판정이 읽지 않는다), 다르거나 없으면 거부한다 — 그 단위가 바꾼 규칙이 그 단위 자신을 판정하는 것이고, 새 규칙은 다음 단위부터 적용된다(D-81). 트리에 하네스가 없는 루트는 「자기적용이 아니다」로 통과한다. 내용(blob)만 본다 — 실행 비트와 더해진 파일은 보지 않는다, 판정이 읽는 파일은 이름이 고정돼 있다」. `adapters/orca/RUNBOOK.md` §3.8: 871행 문단의 「종료 검사(`bin/romeo close --unit <id>`)가 그 체크아웃에서 돌면서」를 「종료 검사(승인 커밋 스냅샷의 `bin/romeo close --unit <id> --root "$W"`)가 그 체크아웃을 대상으로 돌면서」로, 「**종료 검사를 실행한다.**」 문단의 「종료 검사는 **구현자 워크트리에서** 돈다」를 「종료 검사는 **승인 커밋 시점의 하네스**가 돌리고 대상은 구현자 워크트리다(`--root "$W"`) — 그 단위가 바꾼 하네스가 자기를 판정하지 않게 하기 위해서다(D-81)」로 바꾸고, 명령 블록을 `J=$(mktemp -d) && git -C "$W" archive <base-sha> \| tar -x -C "$J"` · `"$J/bin/romeo" close --unit <작업 단위 id> --root "$W" --dry-run` · `"$J/bin/romeo" close --unit <작업 단위 id> --root "$W"` · `rm -rf "$J"` 로 바꾼다(§3.1 확인 3 과 같은 모양). 플래그 문장·`--root "$W"` 를 빼면 위임한 쪽을 검사한다는 문장·성공 신호는 그대로 두되 「`[FAIL] JUDGE_REVISION` 은 스냅샷이 승인 커밋이 아니거나 `$W` 자신의 `bin/romeo` 로 돌린 것이다」 한 줄을 더한다. §3.1 의 「승인 커밋과 `<base-sha>` 사이에 계약 입력(…)이 바뀌었으면 §3.8 의 재계산 대조가 **지금 하네스**로 다시 계산하므로 `<base-sha>` 를 그 변경 뒤로 잡는다」를 「승인 커밋과 `<base-sha>` 사이에 계약 입력(…)이 바뀌었으면 **재승인한다** — §3.8 의 판정·재계산은 승인 커밋 시점의 하네스가 하므로 그 뒤의 입력으로 만든 계약은 재계산 대조에서 어긋난다」로 바꾼다. `adapters/claude/workflows/plan-close.md` 와 `adapters/codex/workflows/plan-close.md` 의 3번을 「검사는 승인 커밋 스냅샷의 `bin/romeo close --unit <id> --root <대상 루트>` 가 한다(절차 2 — 구현 워크트리 자신의 `bin/romeo` 가 아니다). 실패 코드(FRESH_*·NO_EVIDENCE·UNCHECKED_AC·MISSING_CHECK·JUDGE_REVISION)를 그대로 사용자에게 보고한다」로 바꾸고 `bin/romeo compile` 을 돌려 산출물 둘과 `.harness/compiled.yaml` 을 갱신한다. 도구명·모델명을 쓰지 않는다(C-C6). frontmatter `description:` 은 건드리지 않는다 | 소비: 1 이 만든 규칙 → 생산: 없음 | check-7·check-8·check-9·check-12 | `git revert` |
| 3 | 판별 검사를 더한다 | 새 파일 `tests/test_judge_revision.py`, 클래스 `TestJudgeRevision`. fixture: `setUpClass` 에서 임시 저장소 R 을 만들어 `git -C HARNESS_ROOT ls-files -z` 의 파일을 **작업 트리 내용**으로 복사해 커밋(이것이 「하네스 저장소 자신」이다), `TestVerticalSlice` 와 같은 순서로 T0 단위 생성·`_fill_spec(command="true")`·승인·커밋(= 승인 커밋 A)·`README.md` 끝에 한 줄 덧붙여 커밋(구현 커밋 — `docs/` 밖 추적 파일을 바꾼다)·`evidence run`(command `true`) 1건. 각 검사는 R 을 `git clone`(또는 `cp -R`)한 사본과 `git -C R archive A \| tar -x` 로 만든 스냅샷 J 를 자기 임시 폴더에 둔다. 검사 7건 — `test_the_tree_under_judgment_judging_itself_is_refused`(`close_unit(unit, project_root=R, harness_root=R, dry_run=True)` → 검사 행 `JUDGE_REVISION` ok False·level error·문장에 A 앞 12자와 `README.md`), `test_a_snapshot_of_the_approval_commit_passes_and_closes_the_unit`(`harness_root=J` → `JUDGE_REVISION` ok True·전체 verdict PASS·dry_run 아님이면 spec `status: done`), `test_a_snapshot_with_one_file_changed_is_refused_and_names_the_path`(`J/romeo/close.py` 끝에 한 줄 → FAIL·문장에 `romeo/close.py`; `J/README.md` 삭제 → FAIL·문장에 `README.md`), `test_docs_are_not_compared`(`J/docs/planning/progress.md` 와 `J/.harness/observations.yaml` 을 고쳐도 ok True), `test_a_root_without_the_harness_passes_as_not_self_applied`(`TestVerticalSlice` 형 저장소 — `romeo/` 없음 — 를 `harness_root=HARNESS_ROOT` 로 → ok True·문장에 「자기적용이 아니다」), `test_the_snapshot_cli_judges_the_tree_with_root_and_prints_a_verdict`(`subprocess` 로 `J/bin/romeo close --unit <id> --root R --dry-run` → exit 0·stdout 에 `[PASS] JUDGE_REVISION`·`Traceback` 없음; `R/bin/romeo close --unit <id> --root R --dry-run` → exit 1·`[FAIL] JUDGE_REVISION`; 그 뒤 `J/bin/romeo close --unit <id> --root R`(dry-run 없음) → exit 0·spec `status: done`), `test_an_uncommitted_approval_leaves_the_judge_unverified`(R 사본에서 `approve_unit(..., reapprove=True)` 만 하고 커밋하지 않은 뒤 스냅샷으로 판정 → `JUDGE_REVISION` ok False·level `unverified`·문장에 「승인 커밋을 이력에서 찾지 못해」). 단언은 판정 문자열 전체가 아니라 검사 id·`ok`·`level`·종료 코드·경로 문자열로 한다. **기존 검사는 한 줄도 고치지 않는다** | 소비: 1 → 생산: 검사 7건 | check-1~check-6·check-13·check-10 | 해당 검사만 되돌린다 |
| 4 | 이번 작업이 발견했으나 고치지 않은 것을 연다 | `docs/planning/open-questions.md` 의 Q-43 행을 해소 표기(취소선 + 「해소(2026-09-07, feat-20260907-judge-revision-base-sha-pwt8)」 + 무엇으로 닫혔나 — 세 후보 대신 D-81 의 판정 리비전 분리 · 근거 열의 `romeo/close.py`·`core/policy/packages.yaml` 은 남긴다)로 바꾸고, 발견한 결함을 새 행(Q-83~)으로 더한다 — 최소 둘: `envelope check`·`evidence checks` 는 구현자 워크트리의 `bin/romeo` 로 돌아 판정 하네스와 리비전이 다르다(판정에 닿는지 미확인) · 판정 하네스의 리비전이 `attempts.yaml` 회차에 남지 않는다(Q-02 계측 재료). `docs/planning/progress.md` 「지금 상태」 블록의 활성 단위·다음 행동 줄을 갱신한다(예산 30줄·2KB) | 소비: 없음 → 생산: 없음 | check-11 | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 페이로드(하네스를 부착한 프로젝트) 작업 단위의 `required_checks` 에
**하네스 자신의 테스트**를 넣지 않는다 — `python3 -m unittest discover -s tests`(하네스 저장소의 테스트),
`bin/romeo` 의 자기 검사(`compile --check` · `validate` · `doctor` · `fixtures …`)가 그것이다.
넣으면 하네스가 깨진 동안 그 페이로드 단위가 닫히지 못한다. 그 단위의 산출물은 멀쩡한데 완료가 서지 않는 것이고,
그때 고쳐야 할 것은 그 단위가 아니라 하네스다 — 두 판정을 한 검사에 묶으면 어느 쪽이 깨졌는지 구분되지 않는다
(근거: `feat-20260829-license-field-46an` 의 check-5 가 이 형태였다).
하네스 저장소 **자신**을 대상으로 하는 작업 단위에서는 그 검사들이 정당하다 — 그때는 그것이 이 단위의 산출물이기 때문이다.

**종료 코드 자체가 조건이다.** 검사에 적는 것은 `id` 와 `command` 둘뿐이고, 그 명령의 종료 코드 0 이 통과다.
기대를 문장으로 따로 적는 자리는 두지 않는다 — 사람은 그것을 조건으로 쓰는데 기계는 판정에 쓰지 않으므로,
그 검사는 무엇을 확인하는지 적혀 있는 채로 아무것도 확인하지 않는 **빈 검사**가 된다(2026-08-31 실측으로 제거).
확인하고 싶은 조건이 있으면 그 조건을 **명령으로** 쓴다.
같은 이유로 옵션이 판정을 만드는 명령은 그 옵션까지 적는다 — 예: `bin/romeo doctor` 는 옵션 없이 쓰면 항상 exit 0 이라 빈 검사이고,
부착 검증(K-68)을 실제로 판정하게 하려면 `bin/romeo doctor --strict --scope repository` 로 쓴다(Q-21).

그래서 `|| true` 를 붙이지 않는다 — 종료 코드를 항상 0 으로 만들어 위반을 통과시킨다.
부정 조건은 `!` 로 쓴다: `! grep -q '<있으면 안 되는 것>' <파일>`.

**판별 검사와 회귀 방지 검사의 구분** — §11 은 「어느 쪽인지는 검증 계획에 적는다, 적지 않으면 전부 판별 검사로 본다」고 한다.
**판별 검사는 check-1~check-8·check-12·check-13 열이고**, 승인 전에 기존 상태·가상 완료 상태 양쪽에서 실행해 각각 실패·통과를 보인다(아래 「승인 전 실측」).
check-9~check-11 은 **회귀 방지 검사**이므로 양쪽 실측 대상이 아니다 — 양쪽에서 통과하는 것이 그 검사의 정의다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_judge_revision.TestJudgeRevision.test_the_tree_under_judgment_judging_itself_is_refused"
  - id: check-2
    command: "python3 -m unittest tests.test_judge_revision.TestJudgeRevision.test_a_snapshot_of_the_approval_commit_passes_and_closes_the_unit"
  - id: check-3
    command: "python3 -m unittest tests.test_judge_revision.TestJudgeRevision.test_a_snapshot_with_one_file_changed_is_refused_and_names_the_path"
  - id: check-4
    command: "python3 -m unittest tests.test_judge_revision.TestJudgeRevision.test_docs_are_not_compared"
  - id: check-5
    command: "python3 -m unittest tests.test_judge_revision.TestJudgeRevision.test_a_root_without_the_harness_passes_as_not_self_applied"
  - id: check-6
    command: "python3 -m unittest tests.test_judge_revision.TestJudgeRevision.test_the_snapshot_cli_judges_the_tree_with_root_and_prints_a_verdict"
  - id: check-7
    command: "grep -q 'JUDGE_REVISION' core/workflows/plan-close/SKILL.md && grep -q '승인 커밋 시점' core/workflows/plan-close/SKILL.md"
  - id: check-8
    command: "grep -q 'J/bin/romeo\" close --unit <작업 단위 id> --root \"$W\"' adapters/orca/RUNBOOK.md && ! grep -q 'W/bin/romeo\" close' adapters/orca/RUNBOOK.md && ! grep -q '그 변경 뒤로 잡는다' adapters/orca/RUNBOOK.md"
  - id: check-9
    command: "bin/romeo compile --check"
  - id: check-10
    command: "python3 -m unittest discover -s tests -q"
  - id: check-11
    command: "python3 -m unittest tests.test_doc_commands tests.test_enforce_points tests.test_attach_requirements"
  - id: check-12
    command: "grep -q 'JUDGE_REVISION' adapters/claude/workflows/plan-close.md && grep -q 'JUDGE_REVISION' adapters/codex/workflows/plan-close.md && grep -q 'JUDGE_REVISION' .claude/skills/plan-close/SKILL.md && grep -q 'JUDGE_REVISION' .agents/skills/plan-close/SKILL.md"
  - id: check-13
    command: "python3 -m unittest tests.test_judge_revision.TestJudgeRevision.test_an_uncommitted_approval_leaves_the_judge_unverified"
```

**각 검사가 무엇을 보는가**

| id | 종류 | 무엇이 참이어야 통과인가 | 반례(그럴듯한 거짓 값) |
| --- | --- | --- | --- |
| check-1 | **판별** | 승인 커밋 뒤에 `README.md` 를 바꾼 저장소가 자기를 판정하면 `JUDGE_REVISION` 이 FAIL 이고 문장에 승인 커밋 앞 12자와 그 경로가 있다 | 지금 코드에는 그 검사 행이 없다 — 자기 판정이 PASS 로 닫힌다(Q-43 실측). `docs/` 만 바꾼 저장소는 통과해야 하므로 「HEAD 가 승인 커밋과 다르면 FAIL」로 구현하면 이 검사는 통과해도 check-4 가 잡는다 |
| check-2 | **판별** | `git archive` 로 꺼낸 git 아닌 폴더를 `harness_root` 로 준 판정이 `JUDGE_REVISION` PASS 이고 전체 PASS 로 단위가 done 이 된다 | 판정 루트가 git 이어야만 리비전을 알 수 있게 구현하면(`git rev-parse HEAD` 대조) 스냅샷은 미검증이 된다 |
| check-3 | **판별** | 스냅샷의 파일 하나가 다르거나 없으면 FAIL 이고 그 경로가 문장에 있다 | 「거의 같은」 스냅샷 — 한 줄만 다른 `romeo/close.py` — 이 통과하면 판정 리비전 분리는 이름뿐이다 |
| check-4 | **판별** | 스냅샷의 `docs/`·`.harness/` 아래가 달라도 판정은 그대로다 | 추적 파일 전부를 대조하면 위임한 쪽 체크아웃의 `attempts.yaml`·`task/`(승인 커밋 뒤에 생긴다)와 관통 중 갱신되는 `.harness/observations.yaml` 때문에 FAIL 이 난다 |
| check-5 | **판별** | `romeo/` 가 없는 저장소는 「자기적용이 아니다」로 PASS — 실제 체크아웃이 판정해도 그렇다 | 자기적용 판별 없이 대조하면 남의 저장소는 하네스 파일이 없어 전부 FAIL 이 된다(M3 관통·기존 close 검사 전부) |
| check-6 | **판별** | 스냅샷의 `bin/romeo` 가 `--root` 로 다른 트리를 판정해 exit 0·`[PASS] JUDGE_REVISION`·`Traceback` 없음, 자기 판정은 exit 1·`[FAIL] JUDGE_REVISION`, 스냅샷의 실제 종료 한 번으로 `status: done` | 계획 §10 #13c 의 확인 기준 그대로 — 검사 목록과 종료 코드(스택 트레이스 아님). 지금 코드는 두 호출 모두 `JUDGE_REVISION` 줄이 없다 |
| check-7 | **판별** | plan-close 절차가 판정 하네스의 리비전 규칙을 말한다 | 기존 문서에 두 문구 모두 0건이다 |
| check-8 | **판별** | RUNBOOK §3.8 이 스냅샷의 `bin/romeo` 로 닫는 명령을 갖고, 구현자 워크트리 자신의 `bin/romeo` 로 close 를 돌리는 명령과 §3.1 의 「그 변경 뒤로 잡는다」가 사라졌다 | 기존 문서는 새 명령 0건·옛 명령 있음·옛 문장 있음 — 새 명령만 더하고 옛 것을 남기면 두 절차가 공존해 실패한다 |
| check-9 | 회귀 방지 | 어댑터 매핑 변경이 컴파일 산출물과 어긋나지 않는다 | — |
| check-10 | 회귀 방지 | 기존 검사가 하나도 깨지지 않는다 — 특히 `harness_root` 를 넘기지 않는 close 검사 47건이 「자기적용 아님」으로 지나간다 | — |
| check-11 | 회귀 방지 | 문서 예시의 옵션·필수 옵션, 출처 집합 대조, 집행 지점 대조가 깨지지 않는다 | — |
| check-12 | **판별** | 두 어댑터 매핑과 두 컴파일 산출물이 `JUDGE_REVISION` 을 말한다 | 코어 문서만 고치면 런타임 스킬 파일은 옛 문장(「`bin/romeo close --unit <id>`」)을 그대로 인쇄한다 — 매 세션 두 런타임이 그것을 읽는다 |
| check-13 | **판별** | 승인 커밋을 이력에서 찾지 못하면 `JUDGE_REVISION` 은 미검증이다 | 못 찾은 것을 「자기적용 아님」이나 PASS 로 접으면 커밋하지 않은 재승인이 판정을 통과시킨다 |

**재실행 시간** — check-10 이 약 160~190초(프로브 실측 184초 · 새 검사 7건이 하네스 사본 저장소를 만든다), 나머지는 각 1~6초다. `romeo close` 의 재실행 상한 600초 안이다.

**승인 전 실측(2026-09-07)** — 판별 검사 열(check-1~8·12·13)을 두 상태에서 실행했다. 기존 상태(이 체크아웃 `52078b7`, 이 단위의 문서만 더한 트리):
**열 건 전부 exit 1**(check-1~6·13 은 검사 모듈 없음, check-7·8·12 는 문구 0건). 가상 완료 상태(프로브 워크트리
`probe-judge-revision` = `52078b7` + 구현 단위 1~3 을 이 spec 대로 적용한 미커밋 시제품): **열 건 전부 exit 0**(check-1~6·13 각 3.5~5.9초),
회귀 검사 check-9·check-11 exit 0, check-10 은 922건 OK(183.5초). 프로브에서 잡아 spec 에 반영한 것 셋 — `.harness/` 도 대조에서 뺀다
(관통 중 `observations.yaml` 이 바뀌면 거짓 FAIL) · AC-4 의 미검증 경로에 검사가 없었다(check-13) · AC-2 의 「호출 한 번으로 done」을
CLI 검사가 실제로 밟게 했다(check-6). 프로브 산출물은 승인 뒤 구현자의 출발점으로 넘긴다 — 판정 게이트는 그대로다.


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
