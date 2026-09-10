---
id: feat-20260910-sealed-run-worker-settle-37qi
type: spec
title: 봉인된 run 에는 더 쓰지 않는다 — 살아남은 워커의 증거 오염을 절차와 기록 두 자리에서 막는다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
status: done
approved_at: '2026-09-10T19:49:39+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-09-10T20:31:12+09:00'
parent: null
inputs: [inputs/ac-rebuttal-20260910.md, inputs/ac-rebuttal-20260910-2.md]
evidence: [evidence/run_3bc199b43f95.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-10'
updated: '2026-09-10'
---

# 봉인된 run 에는 더 쓰지 않는다 — 살아남은 워커의 증거 오염을 절차와 기록 두 자리에서 막는다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260910-sealed-run-worker-settle-37qi --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** Q-101 정비 — 검토 봉투가 기록된(봉인된) run 에 살아남은 워커가 검사를 다시 쓰면 그 run 의 증거가 두 산출물에 걸쳐 판정이 서지 않고 되돌릴 수도 없다. 세 자리를 고친다. ① 재작업 위임 절차(RUNBOOK §3.4.2)의 첫 단계로 앞 dispatch 가 settle 됐는지 **관측**한다 ② `worker-stop` 이 거부할 수 있다는 것과 그 뒤의 복구 경로를 §7 에 적는다 ③ `evidence run`·`evidence checks`·`review record` 가 봉인된 run 에 쓰려 하면 **아무것도 쓰지 않고 실행하지도 않은 채** 거부한다.
- **왜 지금:** 바로 앞 관통(`feat-20260909-metrics-four-counters-dyz2`)의 2회차가 이 결함으로 탔다 — 검토자 PASS 봉투를 `review-spoiled/` 로 옮기고 3회차를 다시 돌려야 close 가 섰다. 절차의 어느 자리도 앞 회차의 워커가 죽었는지 묻지 않고, 기록 코드는 봉인 뒤에도 무조건 append 한다(`romeo/evidence.py` 의 `run_command`). close 는 검토 시점의 산출물을 방어 검사에서 읽지만 봉투가 지목한 증거의 산출물은 **마지막 명령**에서 읽으므로, 봉인 뒤 한 줄이 더 붙으면 둘이 갈려 `REVIEW_VERDICT` 가 미검증이 된다. 다음 관통(D-81 ④)도 재작업 위임을 밟는다.
- **기대 결과:** 봉인된 run 에 증거를 더 쓰려는 명령은 exit 1 로 끝나고 그 run 의 증거·로그·봉투는 바이트 하나 바뀌지 않는다 — 살아남은 워커가 있어도 봉인된 판정은 그대로다. 봉인되지 않은 run 과 같은 단위의 새 run 에는 지금처럼 쓴다. 재작업 위임 절차가 앞 dispatch 의 settle 을 관측으로 먼저 확인하고, 거부된 `worker-stop` 뒤의 길이 §7 에 있다.
- **수용 기준:**
  - [x] AC-1 `romeo/evidence.py` 에 봉인 판정 하나를 둔다 — run 기록의 `commands` 에 `REVIEW_RECORD_LABEL` 라벨의 기록이 있으면(1개 이상) 그 run 은 봉인이다. `run_command` 은 그 판정을 **두 번** 본다 — ① 명령을 실행하기 전 ② 명령이 끝나고 기록을 쓰기 직전에 **디스크에서 기록을 다시 읽어**. `record_review_envelope` 은 봉투 파일을 쓰기 전에 본다. 그 세 자리 중 하나에서 봉인이면 `ValueError` 로 끝나고, **그 호출이 만드는 쓰기 셋** — `evidence/<run>.yaml` 갱신 · 그 명령의 로그 파일 · `review/<run>-reviewer.json` — 을 하나도 하지 않는다(넘긴 명령의 부수 효과와 안쪽 호출의 쓰기는 이 집합에 없다 — ④ 가 그 경우다). 판별 상태 넷 — 각각 호출 전후로 (a) `evidence/<run>.yaml` 의 바이트 (b) `.harness/runs/<id>/<run>/` 의 파일 이름·sha256 목록 (c) `review/<run>-reviewer.json` 의 바이트를 대조한다: ① 봉인된 run 에 `run_command` — (a)(b) 같고 넘긴 명령은 실행되지 않는다(파일 하나를 만드는 명령을 넘겨 그 파일이 없는 것으로 본다) ② 봉인된 run 에 `run_required_checks` — ① 과 같고 첫 검사에서 멈춘다 ③ 봉인된 run 에 `record_review_envelope` 재기록(판정이 다른 봉투 JSON) — (a)(b)(c) 같다 ④ **실행 도중 봉인** — 봉인되지 않은 run 에 넘긴 명령 자체가 그 run 을 봉인하면(명령 안에서 `review record` 를 부른다) 그 명령은 실행되지만 결과는 기록되지 않는다: 호출은 `ValueError` 로 끝나고, (a) 의 `commands` 는 안쪽 봉인이 남긴 봉인 라벨 기록 1건이 마지막이며 바깥 명령의 기록이 없고, (b) 에 바깥 명령의 로그 파일이 없다. 거부 메시지는 그 run id 와 「새 run」 낱말을 담는다.
  - [x] AC-2 봉인 판정의 여집합 — 봉인 라벨 기록이 **없는** run — 에는 기록이 된다. 「정상 기록」의 관측 기준: `run_command` 은 `commands` 길이가 1 늘고 마지막 항목의 `id` 가 넘긴 라벨이며 그 항목의 `exit_code` 가 넘긴 명령의 실제 종료 코드(0 과 1 을 각각 넘겨 본다)이고 최상위 `head_sha` 가 그 항목의 값이며 `command_log_state` 가 그 항목에 `True` 를 돌려준다(로그 파일이 있고 `log_sha256`·봉인 줄과 맞는다); `record_review_envelope` 은 `review/<run>-reviewer.json` 이 넘긴 JSON 과 같은 내용이고 `commands` 마지막 항목의 `id` 가 봉인 라벨이다. 판별 상태 넷: ① `commands` 가 빈 새 run ② 일반 명령(`check-1` 같은 라벨)만 있는 run ③ `review-tree-before`·`review-tree-after` 만 있는 run ④ 같은 단위의 다른 run 이 봉인된 **뒤에** 만든 새 run. 넷 다 `run_command` 이 정상 기록되고, ③·④ 는 `record_review_envelope` 도 정상 기록된다(③ 이 정상 검토 순서다).
  - [x] AC-3 봉인 표지는 `REVIEW_RECORD_LABEL` 에서 읽고 라벨 **동일성**(문자열이 같다)으로 판정한다. 판별 셋 — ① `tests/test_sealed_run_refusal.py` 가 그 상수를 `unittest.mock.patch("romeo.evidence.REVIEW_RECORD_LABEL", …)` 로 **원래 값과 서로 부분 문자열이 아닌** 값으로 바꿔친 채 `run_command` 을 부르면, 원래 라벨의 기록만 있는 run 은 거부되지 **않고** 바꿔친 라벨의 기록이 있는 run 은 거부된다 ② 바꿔치지 않은 상태에서 원래 라벨의 **진부분 문자열**(예: 앞 여섯 글자)을 라벨로 가진 기록만 있는 run 과 원래 라벨을 **포함하는 더 긴** 라벨의 기록만 있는 run 은 둘 다 거부되지 않는다(부분 문자열 비교를 막는다) ③ 그 검사 파일의 소스에 문자열 리터럴 `review-record` 가 0건이다 — 라벨은 import 로만 가져오고, ② 의 라벨도 상수에서 잘라 만든다.
  - [x] AC-4 명령줄 세 경로도 같다 — 봉인된 run 에 대해 `bin/romeo evidence run --unit <id> --run <run> -- <파일 하나를 만드는 명령>` · `bin/romeo evidence checks --unit <id> --run <run>`(그 spec 의 `required_checks` 가 파일 하나를 만드는 명령이다) · `bin/romeo review record --unit <id> --run <run> <판정이 다른 봉투 JSON>` 이 각각 exit 1 로 끝나고 stderr 가 그 run id 와 「새 run」 낱말(AC-1 의 거부 메시지)을 담으며, 실행 전후로 AC-1 의 (a)(b)(c) 가 같고 그 파일이 생기지 않는다. 여집합 — 같은 단위의 봉인되지 않은 run 에 같은 세 명령을 부르면 각각 exit 0 으로 끝나고 그 파일이 생기며 `commands` 가 늘어난다(봉인과 무관한 공통 오류로 exit 1 이 나는 구현을 여기서 가른다).
  - [x] AC-5 RUNBOOK §3.4.2 「밟을 순서」 의 첫 단계가 앞 dispatch 의 settle 관측이고 세 갈래 (가)(나)(다) 를 적는다 — (가) `orca orchestration worker-show --dispatch <옛 dispatch-id> --json` 의 `.result.dispatch.status` 가 `failed`·`completed` 중 하나이고 `.result.observation.status` 가 `exited` 이면 settle 이다: 다음 단계로 간다 (나) 아니면 `worker-stop` 을 밟고, **수락됐어도** 같은 `worker-show` 를 다시 돌려 (가) 가 성립할 때만 다음 단계로 간다 (다) `worker-stop` 이 거부되면 §7 의 그 행으로 가고, 그 행의 마지막 확인이 (가) 와 같다. 그리고 같은 절의 「(1) 증거가 거부한다」 문단에 두 번째 방어를 적는다 — 봉인 라벨(`review-record`) 기록이 있는 run 에는 `evidence run`·`evidence checks`·`review record` 셋이 기록을 더하지 않는다. 판별 규칙: §3.4.2 절(다음 `### ` 헤더 전까지) 안에서 `worker-show --dispatch` 의 첫 줄이 `task-update` 의 첫 줄보다 앞이고, 그 절에 `worker-show` 가 2회 이상 나타나며, 봉인 라벨이 백틱으로 나타난다.
  - [x] AC-6 RUNBOOK §7 「남은 상태」 표에 `worker-stop` 이 거부하는 행이 **정확히 하나** 있다 — 첫 칸이 거부 메시지 `Dispatch ... is not stopping` 을 담고, 같은 행이 순서 셋을 이 순서로 담으며 ①과 ② 사이에 다른 단계를 두지 않는다: ① `worker-show` 로 `.result.terminalResource.ownerDispatchId` 가 그 dispatch id 와 같고 `.result.observation.exactWorker` 가 `true` 임을 확인 ② 그 직후 `orca terminal close --terminal <.result.worker.agent_terminal_handle>` ③ `worker-show` 로 AC-5 (가) 의 두 조건(`.result.dispatch.status` 가 `failed`·`completed` 중 하나 · `.result.observation.status` 가 `exited`)을 확인 — 이것이 settle 이고, AC-5 (다) 의 마지막 확인과 같은 것이다. 「그 직후」는 문서상 인접 — 같은 행 안에서 ① 과 ② 사이에 다른 단계가 없다는 뜻이다. 그 행은 ② 가 거부된 워커를 실제로 죽이는지 **미관측**이라고 적고 그 근거를 적는다 — 이 저장소의 `.harness/observations.yaml` 과 RUNBOOK §11.1 에 `terminal close` 를 실행한 관측 기록이 없고, 거부된 워커의 종료로 관측된 것은 `exitCause.kind operator_close`(사람이 닫은 것) 1건(`ctx_396c4aad204d`)이다. §11.2 에 `orca terminal close --terminal` 을 담은 항목이 있다. 판별 규칙: 표에서 `is not stopping` 을 담은 행이 1개이고, 그 행에 `orca terminal close --terminal`·`ownerDispatchId`·`exactWorker`·`dispatch.status`·`observation.status`·「미관측」이 있으며, §11.2 절 안에 `orca terminal close --terminal` 이 나타나고, `.harness/observations.yaml` 과 §11.1 절 안에는 `terminal close` 가 나타나지 않는다(미관측 근거를 검사가 같이 본다).
  - [x] AC-7 `core/workflows/implement/SKILL.md` 의 7번 항목(「7. **증거.**」 로 시작해 「8.」 항목 전까지) 안에 봉인 라벨을 **백틱으로** 담은 문장이 있고, **그 문장**이 「거부」 와 「새 run」 낱말을 함께 담는다 — 뜻은 「검토 봉투가 기록된 run 에는 더 쓰지 않는다: 증거 기록 명령이 거부하고, 다시 검토받으려면 새 run 이다」. 그리고 7번 항목 안에서 봉인 라벨을 담은 문장은 **그 문장뿐**이거나, 더 있다면 각각이 「거부」 또는 「새 run」 을 담는다 — 라벨을 지우거나 같은 run 에 다시 쓰라는 안내가 같은 항목에 실리는 것을 막는다. 판별 규칙: 검사가 `REVIEW_RECORD_LABEL` 을 import 로 읽어 7번 항목의 텍스트를 문장(마침표 단위)으로 나눈 뒤 ① 백틱 라벨·「거부」·「새 run」 셋을 다 담는 문장이 1개 이상이고 ② 백틱 라벨을 담으면서 「거부」도 「새 run」도 담지 않는 문장이 0개인지 본다 — 검사 소스에 리터럴 0건.
- **위험과 되돌리기:** 이 변경은 이 저장소 안에서 끝난다 — 외부 반영·비용·권한 변화가 없다. 되돌리기는 `git revert <커밋>` 한 번이다. 실질 위험은 하나 — **거부가 정당한 경로를 막는 것.** `review record` 자체가 자기 라벨에 걸리면 어떤 검토도 봉인되지 않고, 방어 검사 뒤의 정상 기록이 막히면 그 뒤의 관통이 close 에서 멈춘다. AC-2 가 그것을 직접 겨눈다(봉인 기록이 없는 run 네 상태에는 쓴다). 개별 되돌리기는 `evidence.py` 의 판정 호출 두 줄이다.
- **결정 필요:** 없음 — 거부 범위(봉인된 run 에는 재기록 포함 어떤 명령도 더하지 않는다)와 복구 경로(`terminal close`)는 확정 단계에서 사용자가 골랐다.


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/evidence.py` · `adapters/orca/RUNBOOK.md` · `core/workflows/implement/SKILL.md` · `tests/test_sealed_run_refusal.py` · `tests/test_runbook_worker_settle.py` · `docs/work/feat-20260910-sealed-run-worker-settle-37qi/`
- 영향을 받는 부분: 다음 관통부터 봉인된 run 에 `evidence run`·`evidence checks`·`review record` 를 부르면 exit 1 이다 — 재검토·재작업은 새 run 으로만 간다(이미 §3.4.2·§6.6 이 그렇게 적고 있다). 재작업 위임의 첫 단계가 하나 늘어난다.
- 바꾸지 않는 것(비범위): `romeo/close.py` 의 판정 로직(오염을 읽는 자리에서 거르지 않고 쓰는 자리에서 막는다) · 가드 결정 기록(`_add_decision` — 명령 배열이 아니고 산출물 식별에 들어가지 않는다) · 거부 우회 플래그(두지 않는다 · K-51) · `orca terminal close` 가 거부된 워커를 실제로 죽이는지의 관측(이 단위는 「미관측」으로 적는다) · 컴파일 산출물 `.claude/skills/implement/SKILL.md`·`.agents/skills/implement/SKILL.md`(원본을 가리키기만 하고 본문을 담지 않으므로 다시 만들지 않는다) · Q-100(재분류 기록 경로) · `docs/planning/open-questions.md` 의 Q-101 해소 표기(통합 뒤 progress 커밋이 한다)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 봉인된 run 에 쓰기를 거부한다 (AC-1·AC-2·AC-3·AC-4) | `romeo/evidence.py` 에 `sealing_record(rec)` 를 둔다 — `commands` 에서 `REVIEW_RECORD_LABEL` 라벨의 기록을 찾아 그 기록(없으면 None)을 돌려준다. `run_command` 은 `_open_record` 직후·`_stamp_ids` 전에 한 번, 그리고 `subprocess.run` 이 끝난 뒤 기록을 쓰기 직전에 디스크에서 다시 읽어 한 번 더, `record_review_envelope` 은 봉투 파일을 쓰기 전에 각각 그것을 보고 봉인이면 run id 와 「새 run」 안내를 담은 `ValueError` 를 낸다. 상수는 함수 정의보다 아래(551)에 있지만 호출 시점에 읽으므로 옮기지 않는다 | 소비: `REVIEW_RECORD_LABEL` · `_open_record` → 생산: `sealing_record(rec) -> dict \| None` | `tests/test_sealed_run_refusal.py` 를 **새 모듈로** 만든다(기존 `tests/test_docs_evidence_close.py` 에 더하면 그 모듈 명령이 이 단위 없이도 통과해 빈 검사가 된다). 임시 git 저장소에 단위를 만들고 방어 검사 둘 + `record_review_envelope` 으로 봉인한 뒤 AC-1 의 네 상태·AC-2 의 여집합 넷·AC-3 의 동일성 셋·AC-4 의 CLI 셋과 그 여집합을 확인한다. 상수 바꿔치기는 `unittest.mock.patch("romeo.evidence.REVIEW_RECORD_LABEL", ...)` 로 한다 | `git checkout -- romeo/evidence.py` · `rm tests/test_sealed_run_refusal.py` |
| 2 | 재작업 위임이 앞 워커의 죽음을 관측한다 (AC-5·AC-6) | `adapters/orca/RUNBOOK.md` §3.4.2 「밟을 순서」 코드 블록 앞에 0번 단계(`worker-show` 관측 · 두 필드의 판정 기준 · 살아 있으면 `worker-stop` 뒤 재관측 · 거부되면 §7)를 넣고, 「(1) 증거가 거부한다」 문단에 봉인된 run 의 거부를 한 문장 더한다. §7 표에 `worker-stop` 거부 행(소유 확인 필드 둘 · 직후 `terminal close` · `exited` 재확인 · 미관측 표시)을 넣고, §11.2 에 「`terminal close` 가 거부된 워커를 죽이는지」 항목을 더한다 | 소비: 1 의 거부 메시지 형태 → 생산: 없음 | 3 의 검사가 통과한다. 사람이 §3.4.2 를 위에서 아래로 읽어 관측 → 닫기 → 기록 → 새 Run 순서가 되는지 본다 | `git checkout -- adapters/orca/RUNBOOK.md` |
| 3 | 코어 절차가 요구를 적는다 (AC-7) | `core/workflows/implement/SKILL.md` 7번 「한 run 은 한 위임에 속하므로 …」 뒤에 「검토 봉투가 기록된(`review-record`) run 에는 더 쓰지 않는다 — 증거 기록 명령이 거부하고, 다시 검토받으려면 새 run 이다」 를 적는다. 컴파일 산출물은 원본을 가리키기만 하므로 다시 만들지 않는다 | 소비: 1 의 라벨 → 생산: 없음 | 4 의 검사가 통과한다 | `git checkout -- core/workflows/implement/SKILL.md` |
| 4 | 절차 문서의 요구를 코드에서 읽어 고정한다 (AC-5·AC-6·AC-7 의 판별 규칙) | `tests/test_runbook_worker_settle.py` 를 **새 모듈로** 만든다 — §3.4.2 절 안의 순서(`worker-show --dispatch` 첫 줄 < `task-update` 첫 줄)·`worker-show` 2회 이상·봉인 라벨의 백틱 존재, §7 표의 거부 행 1개와 그 행의 복구 명령·소유 확인 필드·미관측, §11.2 의 `orca terminal close --terminal`, 코어 7번 항목 안에서 백틱 라벨·「거부」·「새 run」 을 한 문장에 담은 문장의 존재와 라벨만 담은 문장의 부재, `.harness/observations.yaml`·§11.1 에 `terminal close` 부재. 라벨은 `romeo.evidence.REVIEW_RECORD_LABEL` 을 import 해 쓴다 — 선례 `tests/test_runbook_procedure.py` 의 `TestRunbookProcedureAnchors` 와 `tests/test_review_guidance_alignment.py` 의 import 규칙 | 소비: `REVIEW_RECORD_LABEL` · RUNBOOK 절 헤더 → 생산: 없음 | `python3 -m unittest tests.test_runbook_worker_settle -v` — 이 단위 전 상태에서는 모듈이 없어 exit 1 이고, 2·3 을 되돌리면 각 검사가 그 자리를 지목하며 실패한다 | `rm tests/test_runbook_worker_settle.py` |

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

`check-1`·`check-2` 는 **판별 검사**다 — 이 단위가 없으면 실패해야 한다(승인 전에 둘 다 exit 1 을 실측했다 · 모듈이 없다).
`check-3`·`check-4`·`check-5` 는 **회귀 방지 검사**로, 이 단위 전후 양쪽에서 통과하는 것이 정상이다(AGENTS.core §11).
`check-1` 이 담는 것은 AC-1~AC-4 이고, `check-2` 가 담는 것은 AC-5·AC-6·AC-7 의 판별 규칙이다 — 둘 다 **새 모듈**이다. 기존 모듈에 케이스를 더하면 그 모듈 명령이 이 단위 없이도 통과해 빈 검사가 된다.
`bin/romeo compile --check` 는 넣지 않는다 — 이 단위가 고치는 세 문서(RUNBOOK · 코어 implement 절차) 중 어느 것도 컴파일 산출물에 포함되지 않는다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_sealed_run_refusal -v"
  - id: check-2
    command: "python3 -m unittest tests.test_runbook_worker_settle -v"
  - id: check-3
    command: "bin/romeo validate"
  - id: check-4
    command: "bin/romeo integrity"
  - id: check-5
    command: "python3 -m unittest discover -s tests"
```


## 증거

close PASS · 2026-09-10T20:31:12+09:00 · HEAD 96ffc94b45a3 · 검사 기록 run_3bc199b43f95

- [evidence/run_3bc199b43f95.yaml](evidence/run_3bc199b43f95.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
