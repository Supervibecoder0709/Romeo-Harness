# PM Harness 관점 메모

## 권장 판단

**현재는 이 레포를 운영용 Harness로 연결하거나 agent에게 MCP 설정을 배포하지 않는 것이 맞다.** README는 완성형 오케스트레이터처럼 보이지만, 고정 SHA의 실제 실행물은 `orca version`뿐이고 나머지는 연결되지 않은 기반 코드 또는 설명 주석이다.[E03][E05][E20]

이 판단은 “Go 코드가 부족해 보인다”는 인상이 아니라, 실제 사용자 입력 → run/pod 생성 → agent 실행 → 제약 확인 → review/ship으로 이어지는 호출 경로가 없다는 코드 근거에 따른 것이다. 잘못 도입하면 팀은 MCP config를 바꿨지만 server subcommand가 없어 agent가 실패하고, run/audit/worktree가 기록될 것이라는 운영 기대만 생기는 상태가 된다.[E03][E05][E20]

## 확인된 사실

- **입력 계약:** 현재 CLI에서 확인된 계약은 `orca version`과 build-time version fields다. run goal, pod DAG, config file, MCP tool schema의 parsing/validation은 없다.[E05][E20]
- **모델/agent 역할:** `Adapter` interface는 prompt·context file·worktree를 받아 launch할 수 있게 설계되었지만 concrete adapter와 credential handling은 없다. 지원 agent 목록은 README 주장일 뿐이다.[E03][E07][E08]
- **실행 단위:** DB schema상 pod/run/dependency 모델을 계획했고, worktree helper는 run ID마다 branch/worktree를 만들 수 있다. 하지만 pod 생성·scheduler·dependency resolution·concurrency limit 실행 코드는 없다.[E12][E13][E20]
- **증거·로그:** schema는 logs/events/FTS5를 설계했으나 이를 기록·조회하는 상위 서비스와 CLI는 없다. DB file 위치도 README가 말하는 `~/.orca/orca.db`로 여는 코드가 이 SHA에는 없다.[E03][E11][E12]
- **재시도·복구:** state table의 `failed/blocked → running` retry와 worktree archive helper는 각각 존재한다. 그러나 실제 retry command와 state/DB/worktree를 일관되게 갱신하는 orchestrator는 없다.[E03][E10][E13]

## 사람 승인 지점

실제로 구현될 때에도 아래는 agent가 자동 확정하면 안 되는 외부 경계다. 현재는 해당 기능 자체가 없으므로 이 목록은 **운영 추천**이지 구현된 safeguard가 아니다.

| 지점 | 왜 사람 승인인가 | 현재 코드 증거 |
| --- | --- | --- |
| GitHub PR/merge·release | 외부 repository를 바꾸고 되돌리기 비용이 큼 | README는 ship/PR을 주장하지만 구현 없음; release workflow만 tag에 `contents: write` 권한을 선언 [E03][E19] |
| worktree archive/cleanup | 로컬 작업 디렉터리가 이동되므로 복구 위치를 명확히 해야 함 | `Archive`는 directory 이동 후 prune; shipped/killed kind 값 검증은 코드상 없음 [E13] |
| agent 실행과 credentials | prompt/context가 외부 agent process로 넘어갈 수 있음 | Adapter interface만 있고 concrete provider/credential flow 미확인 [E07] |
| constraint 통과 판정 | ready/ship gate가 제품 품질과 직접 연결됨 | state rule은 있지만 constraint evaluator/runner가 없음 [E10][E20] |

## 재실행·복구에 쓸 수 있는 기반

- schema migration은 embedded SQL을 순서대로 적용하고 반복 open을 고려해 idempotent하게 작성됐다. Store test도 같은 DB를 두 번 여는 경우와 FTS trigger를 확인한다.[E11][E12][E16]
- worktree test는 생성, 빈 base branch 오류, shipped archive와 git registry 제거를 확인한다. 다만 killed archive, rename/prune 실패 복구, concurrent worktree 생성은 이 테스트에서 확인되지 않는다.[E13][E16]
- state test는 legal transition 전체와 각 source 상태의 일부 illegal case를 확인한다. event를 실제 agent 결과·constraint 결과와 연결하는 end-to-end test는 없다.[E15]

## 다음 단계 추천 — 구현 전 검증 게이트

1. **우선순위 1: 수직 슬라이스 하나를 구현하고 검증한다.** `orca run <goal>`이 input validation → run DB record → worktree 생성 → mock adapter launch → event/log record → 상태 전이까지 한 번 연결되어야 한다. 이 한 줄의 실제 readback (DB row, worktree path, log/event)이 있어야 Harness라고 부를 수 있다.
2. **우선순위 2: 외부 write를 명시적 승인 뒤에만 둔다.** `ship`/release/cleanup은 exact target, diff/test evidence, rollback 경로를 보여 준 후 실행하고 결과를 다시 읽어야 한다. release workflow의 `contents: write` 권한도 최소화·검토 대상이다.[E19]
3. **우선순위 3: provider adapter와 MCP를 별도 acceptance test로 검증한다.** credential를 로그/DB/prompt에 저장하지 않고, agent binary 존재·MCP tool schema·timeout/cancel·worktree ownership을 실제 test fixture에서 확인한다. 현재 repository만으로는 이를 검증할 근거가 없다.[E07][E20]

추천이 달라지는 조건은 단 하나다. 고정 SHA 이후의 커밋에서 실제 CLI subcommand, runner, concrete adapter, MCP/constraint implementation 및 end-to-end tests가 추가되면, 그 **새 SHA를 다시 고정**해 위 판단을 재검토해야 한다. 브랜치 이름이나 README만 바뀐 것은 충분한 근거가 아니다.
