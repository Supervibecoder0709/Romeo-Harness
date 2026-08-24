# 05. PM·Harness 운영 메모

## 추천

OpenDesign을 Harness에 연결한다면, **daemon의 project/run/file state를 실행의 source of truth로 두고, UI·chat summary·CLI 출력은 그 상태를 읽는 surface로 취급하는 방식**을 추천한다. 근거는 web과 `od` CLI가 같은 daemon API를 사용하고, daemon이 project persistence·generated files·agent spawning을 소유하며, deliverable test가 “성공 문구”가 아니라 이번 run이 실제로 쓴 유효한 entry artifact를 요구하기 때문이다. [S5], [S8], [S18]

이 결정은 운영 비용과 복구 판단을 단순하게 한다. 예를 들어 UI가 새로고침되거나 CLI가 재연결돼도 run ID, event log, project file을 기준으로 상태를 재확인할 수 있다. 반대로 chat text를 ledger로 삼으면 agent가 파일을 쓰지 않은 경우나 이전 파일을 새 결과로 오인하는 경우를 구분하기 어렵다. 후반 문장은 코드·테스트 구조에서의 **추론**이며, 실제 배포 구성의 관찰 결과는 아니다. [S13], [S18]

## 확인된 입력 계약

- 최소 제품 입력은 프로젝트와 prompt이며, 선택에 따라 design system, primary skill/template, runtime, media execution, tool bundle, conversation/message/run 재개 문맥이 결합한다. [S4], [S5], [S11]
- run에 conversation과 assistant message를 연결할 때는 그 message가 해당 project의 conversation에 속하는지 확인한다. 다른 logical request와 같은 `clientRequestId`는 conflict다. 이는 사용자가 같은 요청을 두 번 눌렀을 때 임의의 새 실행을 만들지 않기 위한 contract다. [S11]
- Codex는 prompt를 stdin으로 전달하고, stored thread ID가 있을 때 `exec resume`를 사용한다. create turn의 working directory/추가 writable dirs와 resume turn의 argv는 동일하지 않으므로 runtime adapter를 범용 shell command로 대체하면 session resume을 깨뜨릴 수 있다. [S12]

## 사람 승인 지점과 권한

- 일반 agent run은 project 파일을 쓰고 external CLI/API를 사용할 수 있다. 그러나 이 아카이브가 읽은 코드 범위에는 각 product action별 사람이 승인하는 중앙 UI 정책이 확인되지 않았다. 따라서 조직 Harness가 이를 감쌀 때는 외부 전송, 공개 publish, credential 변경, destructive overwrite를 명시적 approval gate로 둬야 한다. 이는 **추천**이고, daemon이 file/credential/agent spawn을 소유한다는 사실은 확인됐다. [S8], [S14]
- artifact create는 `overwrite: false`를 전달하고 manifest가 없거나 invalid면 실패한다. 이는 새 artifact 생성의 안전 장치지만 기존 파일 수정·모든 publication 위험을 포괄하는 증명은 아니다. [S14]
- HTML/deck publish에는 일부 미완성 pitch-deck marker를 막는 guard가 있다. marker 집합은 의도적으로 짧아서 모든 품질 문제나 모든 template의 미완성 상태를 차단하지 않는다. 따라서 출시 승인은 이 guard 통과만으로 완료로 하면 안 된다. [S15]
- non-loopback deployment에서는 token/origin/SSE proxy 설정이 운영 승인 지점이다. test에는 `OD_DISABLE_API_AUTH=1` 우회도 있으므로, public 환경의 convenience flag 사용은 보안 책임자가 별도로 승인해야 한다. [S4], [S5], [S19]
- `.claude`의 `od-contribute` skill은 GitHub PR/issue 외부 쓰기를 할 수 있는 별도 흐름이며, preview 후 “Ship it”의 explicit confirmation 전에는 push하지 않도록 명시한다. 이 권한을 제품의 일반 agent run과 혼동하지 않는다. [S20]

## 실행 단위·관찰 증거·재실행

| 운영 질문 | 확인할 증거 | 판단 |
| --- | --- | --- |
| 실행이 시작됐는가 | run ID와 SSE/event log | UI loading만으로 판단하지 않는다. [S11], [S13] |
| agent가 실제 산출물을 만들었는가 | 이번 run의 file-write event와 artifact count | 이전 project file이나 assistant text는 충분하지 않다. [S18] |
| 결과가 쓸 수 있는가 | entry file read 가능, kind 일치, 이번 run이 entry를 touch | stale/mismatched/no-artifact는 invalid다. [S18] |
| 사용자가 멈췄는가 | authorized `cancel` 결과와 terminal status/event | cancel 요청 자체와 child termination/readback은 분리해 본다. [S11], [S13] |
| 재시도해도 되는가 | failure class, side effect/live artifact/cancel 여부, project snapshot | retry-policy가 있는 것은 확인했으나 전체 실행 결과는 미검증이므로 자동 재시도 범위를 배포 전 실험해야 한다. [S17] |

run service는 run별 JSONL event log와 in-memory buffer 밖의 side-effect observer를 지원한다. Harness는 `runId`, input fingerprint, agent/runtime/model, effective project/workspace scope, event log path, written file list, preview validation 결과를 한 ledger record로 묶는 것이 좋다. 이 항목 중 event/run/file 근거는 코드에 있고, ledger schema 제안은 **추천**이다. [S11], [S13], [S18]

## 모델·에이전트 역할

OpenDesign은 agent 하나를 직접 구현하기보다 runtime definition을 registry에 두고 shared engine이 실행하게 하는 구조다. Codex definition에는 `login status` auth probe, `debug models` 모델 탐색, fallback models, model/reasoning argument, Windows/WSL sandbox exception, run-scoped environment allowlist, session resume가 있다. 따라서 PM이 “Codex를 지원한다”는 한 문장만으로 BYOK/API·로컬 CLI·플랫폼별 sandbox·resume의 같은 동작을 가정하면 안 된다. [S5], [S12]

## 확장 지점과 추천

1. **추천 — 실행 계약 버전 고정:** run 시작 시 runtime definition version/commit, selected skill/template/design-system ID와 content hash를 기록한다. 선택물이 user-writable registry에서 shadow될 수 있으므로 ID만으로 재현성이 충분하지 않을 수 있다. shadow 가능성은 확인됐고, hash 기록은 추천이다. [S5]
2. **추천 — write/publish 분리:** 파일 생성은 run permission으로 허용하더라도 external publish/export/deploy는 separate approval + exact target + readback으로 분리한다. 현재 artifact guard는 일부 placeholder만 막는다. [S14], [S15]
3. **추천 — 실패 분류 대시보드:** `no_artifact`, `entry_missing`, `entry_not_touched`, `type_mismatch`, API auth/route error, runtime spawn/auth failure를 별도 metric으로 본다. “run succeeded” 한 지표는 실제 사용자 전달 가능성을 가릴 수 있다. test의 validation names는 확인됐고, dashboard는 추천이다. [S18]
4. **추천 — CI를 release 증거로 과대해석하지 않기:** CI에는 typecheck, guard, i18n, unit shards, E2E workflows가 있지만, 현재 SHA에서 실제 각 job이 통과한지는 이 아카이브 범위가 아니다. 배포 전에는 exact commit의 CI run URL과 required check status를 별도 수집한다. [S16], [S17]

## 미확인 사항

실제 auth UI, credential 저장 형식, cloud collaboration의 live authority, workflow execution logs, runtime별 재시도·rollback 전체, production deployment topology와 cost/billing은 열거나 실행하지 않았다. 따라서 이 문서는 제품 구조·설정·대표 test가 말하는 경계이지, 특정 계정에서 바로 운영 가능한 readiness 판정은 아니다.
