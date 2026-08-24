# 워크플로우 요약

아래는 고정 SHA에서 코드와 설정으로 확인한 동작이다. 실제 모델·OAuth·CI를 실행한 결과가 아니다.

## 1. 저장소 코드 위키 생성·갱신

### 무엇을 하는가

현재 저장소를 읽어 `openwiki/` 아래의 Markdown 위키와 Claims sidecar·run metadata를 관리한다. 코드 모드의 기본 출력은 저장소의 `openwiki/`이며, `--init`은 새 생성, `--update`는 증분 갱신을 목표로 한다. [E09]

### 입력

- CLI 인자: `--init`, `--update`, `--print`, 모델·언어 등 파싱된 command.
- 현재 작업 디렉터리와 그 Git 상태, 기존 `openwiki/.last-update.json`, 선택적 `.openwikiignore`.
- 로컬 구성 디렉터리의 provider 설정·credential. 자격증명 값 자체는 본 분석에서 열지 않았다. [E02][E04]

### 처리 단계

1. CLI가 command를 파싱하고 런타임 환경을 로드한다. 비대화형 run은 code-mode repo setup과 code connector pull을 선행한다. [E02][E03]
2. agent run은 bundled skill 동기화와 `.openwikiignore` 읽기를 수행하고 Claims runtime을 준비한다. [E04]
3. `update`는 Git 변경·이전 상태를 검사한다. 변경이 없으면 agent stream을 열지 않고 Claims finalize 및 `.last-update.json` 새로고침을 시도한다. [E04][E10]
4. `init`은 이전 위키를 복구 가능하게 치환한 후 모델·DeepAgent graph를 만들고, connector/Claims tool과 deterministic middleware를 붙여 stream을 소비한다. [E04][E05]
5. 정상 완료 시 임시 파일 정리 → Claims finalize → complete metadata 저장 → init replacement commit 순서로 마무리한다. [E05]

### 출력·상태 변화

- 생성/수정 가능한 영역: repo `openwiki/`, 그 안의 `.claims/`·`.last-update.json`, 그리고 code setup이 관리하는 root `AGENTS.md`/`CLAUDE.md` block. init은 없는 경우 `.github/workflows/openwiki-update.yml`도 만든다. [E09][E11]
- 대화형 chat의 SQLite checkpoint와 conversation history는 `~/.openwiki` 영역을 사용한다. agent tool은 `/skills/**`와 `/conversation_history/**`에 직접 write할 수 없다. [E05]
- no-op은 모델 작업 없이 skipped 결과를 내고, freshness metadata만 best-effort로 갱신할 수 있다. [E04]

### 실패·재시도

- init agent 실패 시 replacement rollback을 시도한다. rollback 자체도 실패하면 이전 위키가 완전히 복구되지 않았을 수 있다는 aggregate error를 낸다. [E04]
- stream 중 실패한 경우 partial wiki가 다음 update에서 no-op으로 오인되지 않도록 `interrupted` metadata 저장을 시도하고 원 오류를 다시 던진다. [E05]
- provider retry count는 모델 생성 시 `maxRetries`로 전달된다. 이 값의 실제 provider별 효과는 이 아카이브에서 실행 검증하지 않았다. [E12]

### 관찰 가능한 완료 증거

- CLI exit code 0만으로는 내용 정확성을 보장하지 않는다. 코드상 완료는 agent core가 반환한 뒤 Claims finalize와 metadata persistence가 성공한 경로, 또는 host 통합에서는 `openwiki_finish`의 `status: "complete"`다. [E05][E08]
- 운영 확인에는 생성된 `openwiki/` diff, `.last-update.json`의 status/timestamp, Claims sidecar, CLI stderr/stdout, 예정 CI라면 생성된 PR을 함께 읽어야 한다. 마지막 두 항목은 권장 관찰 항목이며 이 작업에서는 실제로 읽지 않았다.

## 2. 개인 지식 수집

### 무엇을 하는가 → 입력

`openwiki ingest <source|all>`은 onboarding 설정의 연결된 source instance를 대상으로 개인 위키를 갱신한다. 입력은 target, scheduled-only 여부, 모델 ID, source 설정 및 로컬 환경이다. [E06]

### 처리 단계 → 출력/상태

각 source를 순차로 처리한다. deterministic connector는 먼저 raw 파일을 수집하고, raw 결과·사용자 목표·source 지침을 agent 메시지에 넣어 local wiki update를 수행한다. 결과별 상태는 `agent-updated`, `error`, `skipped`이며 raw file 목록을 함께 갖는다. [E06]

### 실패·재시도 → 관찰 증거

deterministic pull이 raw file 없이 error이면 agent run 없이 해당 source를 `error`로 반환한다. 그 밖의 예외도 source별 `error` 결과로 바꾸며, 이 함수가 자동 재시도하는지는 확인되지 않았다. CLI는 각 source의 status와 raw file 수를 출력하고 하나라도 error면 exit code 1을 설정한다. [E03][E06]

## 3. Codex/Claude 호스트 통합

### 무엇을 하는가 → 입력

호스트 coding agent가 native repo tool로 조사·기획·Markdown 저작을 수행하되, OpenWiki는 MCP lifecycle로 저장소 root·run ID·Claims·finalization을 통제한다. `openwiki_begin` 입력은 절대 Git root와 `init|update` mode이며, 이후 도구는 동일 run ID를 요구한다. [E07][E08]

### 처리 단계 → 출력/상태

`begin`은 root를 canonicalize하고 setup, ignore, Claims, snapshot, docs-only backend를 준비하며, 진행 중 상태를 `interrupted` metadata로 기록한다. host는 `inspect_claims`/`resolve_claims`를 거쳐 페이지를 저작하고, `finish`가 index·Claims·metadata·init commit을 deterministic하게 완료한다. [E08]

### 실패·재시도 → 관찰 증거

finish의 pre-commit 단계 실패 시 active session을 유지하여 finish 재시도를 허용한다. 새 begin은 버려진 run을 supersede할 수 있고, MCP adapter는 알려진 domain error만 안전한 메시지로 돌려주며 알 수 없는 예외 내용은 숨긴다. 완료 증거는 `openwiki_finish`의 `{status:"complete"}`와 그 뒤 저장된 결과물이다. [E08][E13]
