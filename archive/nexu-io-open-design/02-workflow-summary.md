# 02. 동작 워크플로 요약

## 무엇을 하는가

OpenDesign은 코딩 agent를 디자인 실행 엔진으로 사용해 prototype, deck, image, document, video 같은 산출물을 프로젝트 안에서 만들고 미리보는 로컬 우선 제품이다. 제품의 신뢰할 수 있는 상태는 단순한 대화 응답이 아니라 daemon이 소유하는 프로젝트·대화·파일 및 미리보기 가능한 deliverable이다. [S3], [S5], [S8], [S18]

## 입력

- 사용자는 Web UI 또는 `od` CLI에서 프로젝트/대화를 선택하고 요청을 보낸다. 두 surface는 같은 daemon HTTP API를 호출하도록 설계돼 있다. [S5], [S8]
- 요청에는 프로젝트, prompt, 선택한 design system, primary skill 또는 design template, runtime과 실행 metadata가 결합될 수 있다. local runtime이 없으면 BYOK/API mode를 구성할 수 있다. [S4], [S5]
- Docker 또는 public/non-loopback 배포는 포트만 정하면 되는 구성이 아니다. `OD_API_TOKEN`, 허용 origin, reverse proxy의 SSE 설정이 별도 보안·운영 입력이다. [S4], [S5], [S19]

## 처리 단계

1. **프로젝트·요청 경계 검사**: run/chat route는 project와 conversation의 소유 관계, assistant message의 conversation 연결, plugin snapshot의 프로젝트 연결 등을 확인한다. 같은 `clientRequestId`가 다른 논리 요청을 뜻하면 `IDEMPOTENCY_CONFLICT`로 거부한다. [S11]
2. **실행 프로필 해석**: daemon은 project, design system, skill/template, runtime definition을 바탕으로 filesystem 또는 text-artifact handoff를 정한다. Web UI와 CLI는 daemon의 별도 business logic 복제본이 아니다. [S4], [S5], [S8]
3. **agent 실행**: local CLI mode는 daemon이 child process를 시작하고 SSE로 structured tool/file event를 보낸다. Codex의 경우 JSON stream, stdin prompt, `OD_*` run-scoped 환경 allowlist와 OS별 sandbox 결정이 runtime definition에 있다. [S4], [S12]
4. **산출물 물질화**: filesystem-capable runtime은 project workspace의 canonical file을 쓴다. plain-stream/BYOK는 하나의 complete `<artifact>` block을 host가 parse·materialize한다. artifact 생성 API는 manifest를 검증하고 `overwrite: false`로 file writer를 호출한다. [S4], [S5], [S14]
5. **미리보기·상태**: file workspace의 previewable file은 sandboxed iframe으로 렌더된다. chat·파일·preview가 한 UI에 보이지만 browser state는 프로젝트 DB의 대체물이 아니라 UI state 용도다. [S5]

## 출력/상태

- 확인된 daemon 소유 상태: project/conversation persistence, generated files·artifact, runtime event/상태, 그리고 local data root에서 파생되는 SQLite/registry/automation 등이다. [S5], [S8]
- run service는 선택적으로 run별 `events.jsonl`을 남기고, 외부 agent가 맹목적으로 polling하지 않고 진행 상태를 관찰할 수 있게 path를 status에 노출하도록 구현돼 있다. event ring-buffer가 잘려도 side effect observer가 누적하도록 설계돼 있다. [S13]
- 사용자가 기대하는 최종 결과는 실행 완료 문구가 아니라 (a) 해당 run이 쓴 previewable project file 또는 (b) 완전한 text artifact가 materialize된 뒤, entry file/종류가 프로젝트와 맞는 것이다. 이 기준은 대표 테스트가 stale entry, 무관한 파일, type mismatch, artifact 부재를 모두 거부하는 것으로 확인된다. [S18]

## 실패·취소·재시도

- 사용자는 `POST /api/runs/:id/cancel`을 통해 write capability가 승인된 project run을 취소할 수 있다. 없는 run은 404, run ID 누락은 400이다. [S11]
- Codex는 Windows/WSL 또는 `OD_CODEX_SANDBOX=danger-full-access`에서 danger-full-access를 선택하고, 그 외에는 workspace-write + network access를 구성한다. 이는 해당 adapter의 호환성 정책이지 전역적인 보안 승인 UI는 아니다. [S12]
- 공개 bind는 token 없이 시작하지 못하도록 한 테스트가 있으며, token이 설정된 non-loopback `/api/*` 호출에는 bearer가 필요하다. 다만 `OD_DISABLE_API_AUTH=1`은 test로 확인된 명시적 우회 설정이므로 production에서 편의상 활성화하면 경계가 약화된다. [S19]
- 자동 재시도의 전체 production 구현을 전수 분석하지 않았다. 대표 retry-policy 테스트가 rate limit 등 일부 failure class, cancel·side effect·live artifact가 있을 때 retry 억제를 검증하도록 작성된 것은 확인했지만, 현재 실행 환경에서 이 정책이 통과했다는 것은 미검증이다. [S17]

## 관찰 가능한 완료 증거

1. run의 terminal status만 보지 말고, run event와 해당 project의 실제 file write를 함께 본다. [S13], [S18]
2. entry file이 존재·읽기 가능하고 해당 project kind와 artifact kind가 맞으며, 이번 run이 실제로 touch한 결과인지 확인한다. 기존 파일 하나가 남아 있다는 사실만으로 성공으로 승격하지 않는다. [S18]
3. preview는 sandboxed iframe의 렌더 결과로 별도 확인한다. CI/E2E 파일은 UI와 daemon을 검증하도록 구성돼 있으나, 이 읽기 전용 아카이브에서는 실행하지 않았다. [S5], [S16], [S17]
