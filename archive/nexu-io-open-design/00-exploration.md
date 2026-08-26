# 00. 탐색 기록

## 결론

OpenDesign은 Node/pnpm 모노레포로 제공되는 local-first 디자인 제작 제품이다. Next.js 웹 UI와 Electron 패키지 셸이 로컬 Express + SQLite daemon을 공통 권위로 사용하고, daemon이 선택한 로컬 AI CLI 또는 BYOK/API 실행을 시작해 이벤트·생성 파일을 프로젝트와 미리보기에 연결한다. 이 요약은 제품 문서만이 아니라 daemon의 CLI/HTTP 소유권, Codex 실행 정의, artifact 저장 경계, run route, 대표 테스트와 CI 설정을 함께 확인한 결과다. [S3], [S5], [S6], [S10], [S11], [S12], [S18]

## 탐색 방법

1. `repos/nexu-io/open-design`에서 기본 브랜치 `main`을 받고, `commits/main`의 SHA를 `35a38abf349bfbb53e2ae0252f0f21c8571890b2`로 고정했다. [S1]
2. `git/trees/<SHA>?recursive=1`으로 blob 12,885개와 최상위 분포를 확인했다. `apps` 4,413개, `design-systems` 4,015개, `plugins` 1,815개, `skills` 357개여서 전수 독해 대신 실행 중심 후보를 선정했다. [S2]
3. 사용·운영 문서, root/app package 계약, 패키지 시작점, daemon composition·run/artifact 경계, Codex adapter, CI/E2E/보안 테스트, `.claude` contribution skill을 순서대로 열었다.
4. 문서의 “web/CLI → daemon → runtime → files/preview” 흐름을 package manifest, daemon 소유권 문서, actual route/adapter/artifact 코드와 대표 테스트로 교차 확인했다. 다만 UI를 실제로 구동하거나 모든 runtime adapter를 실행하지는 않았다. [S3], [S4], [S5], [S6], [S10]-[S18]

## 실제로 연 파일과 선정 이유

| 파일 또는 경로 | 선정 이유 | 확인 결과 |
| --- | --- | --- |
| `README.md` | 제품 범위, 지원 surface, 사용자 흐름 주장 | local-first 데스크톱, skill/design-system/plugin, artifact·export, CLI/BYOK의 제품 설명을 제공한다. [S3] |
| `QUICKSTART.md` | 설치·개발·Docker·실행 프로필·운영 트러블슈팅 | Node 24/pnpm 10.33, `tools-dev` lifecycle, local CLI/BYOK의 서로 다른 handoff 계약을 명시한다. [S4] |
| `docs/architecture.md` | 런타임 토폴로지와 데이터·보안 경계 | web/daemon/packaged/runtimes/registries와 HTTP/SSE·SQLite·preview 경계를 설명한다. [S5] |
| `package.json`, 앱별 manifest | 실제 workspace·bin·build/test 계약 | root `od` bin은 daemon CLI를 가리키고 daemon/web/desktop/packaged/e2e가 별도 package다. [S6], [S7] |
| `apps/daemon/AGENTS.md` | daemon의 실제 구성·소유권 규칙 | Express+SQLite daemon, `/api/*`, `od` CLI, project/generated file/agent spawning 소유권과 route/runtime 분리를 명시한다. [S8] |
| `apps/packaged/src/index.ts`, `apps/desktop/src/main/index.ts` | 패키지된 시작 경로 | packaged Electron 진입점이 namespace/path를 준비하고 daemon·web sidecar를 시작한 뒤 desktop runtime으로 넘긴다. [S9] |
| `apps/daemon/src/server.ts`, `routes/runs.ts`, `runtimes/runs.ts` | 실제 request/run composition, SSE/취소·관찰 경계 | server가 route registrars를 조합하고, run route는 project/conversation 권한·idempotency를 검사하며, run service는 event JSONL 경로와 side-effect 관찰자를 지원한다. [S10], [S11], [S13] |
| `runtimes/defs/codex.ts` | Codex 실행 계약 | `codex exec --json`, prompt stdin, run-scoped 환경 allowlist, platform별 sandbox policy, session resume 방식을 선언한다. [S12] |
| `artifacts/create.ts`, `publication-guard.ts` | 산출물 파일 생성·방어 경계 | manifest 검증 뒤 overwrite 없이 쓰며, 특정 HTML/deck placeholder는 publish를 차단한다. [S14], [S15] |
| CI, E2E, daemon tests | 자동 검증의 범위와 완료 증거 | typecheck/guard/i18n/샤딩 daemon test, UI E2E 설정, non-loopback token guard, deliverable validity를 확인한다. [S16]-[S19] |
| `.claude/skills/od-contribute/` | 명시적 agent/skill 정의와 권한 | 기여용 별도 skill로 Bash/Read/Write/Edit/GitHub PR·issue 흐름을 선언하며, explicit push confirmation을 요구한다. 제품 런타임 자체와는 구분해야 한다. [S20], [S21] |

## 확인된 핵심 흐름

사용자는 Web UI 또는 `od` CLI에서 프로젝트와 요청을 만든다. daemon은 프로젝트, 선택된 디자인 시스템·skill/template, runtime 정의를 해석해 로컬 CLI 또는 BYOK/API 호출을 시작하고 HTTP/SSE로 정규화된 이벤트를 보낸다. 파일 시스템 기능이 있는 runtime은 canonical project file을 쓰며, plain/BYOK는 하나의 완전한 `<artifact>` 블록을 host가 file workspace로 materialize한다. 두 경우 모두 최종 확인 대상은 chat prose가 아니라 파일 workspace와 sandboxed preview다. [S4], [S5], [S8], [S11], [S14], [S18]

## 기술 스택과 외부 경계

- Node `~24`, pnpm `10.33.2`, TypeScript 모노레포다. root는 `od` CLI를 `apps/daemon/bin/od.mjs`로 노출한다. [S6]
- `apps/web`은 Next.js 16/React 18, `apps/daemon`은 Express, SQLite(`better-sqlite3`), MCP SDK, `node-pty` 등을 의존성으로 선언한다. `apps/desktop`과 `apps/packaged`는 Electron 기반이다. [S7]
- daemon은 `/api/*`·SSE, 프로젝트·생성 파일·artifact·media·skill·design-system·plugin·MCP·connector credential·agent spawn을 소유하고 web은 daemon private source를 직접 import하지 않아야 한다. [S8]
- runtime은 설치된 CLI를 spawn하거나 BYOK/API proxy를 경유한다. Codex adapter가 사용하는 sandbox·network 허용은 해당 adapter와 플랫폼 조건에 따라 달라진다. “모든 agent가 같은 권한”이라는 전제는 틀리다. [S5], [S12]

## agent·skill 탐색 결과

`apps/daemon/src/runtimes/defs/`에는 다수의 runtime definition이 있고, 이 아카이브에서는 Codex definition만 실행 계약까지 열었다. `.claude/skills/od-contribute/SKILL.md`는 기여 생성·검증·PR/issue 열기를 위한 별도 skill로, `allowed-tools`와 사용자 확인 단계를 명시한다. 이 skill이 존재한다고 해서 일반 제품 생성 run이 GitHub에 쓰기 권한을 가진다는 뜻은 아니다. [S2], [S12], [S20], [S21]

## 미확인 범위

- `apps/web` UI의 모든 화면·상태 전이와 desktop renderer의 실제 실행
- Codex 이외 각 runtime의 최신 설치/로그인/모델·권한 동작 및 모든 외부 API 제공자
- plugin·skill·design-system의 전수 내용과 marketplace/remote registry의 현재 상태
- 실제 SQLite 데이터, 사용자의 credential, cloud collaboration/Vela 계정, 실제 deployment 설정
- CI의 최근 통과 여부, release artifact, package 설치·빌드·E2E 실행 결과

근거 ID는 [06-source-evidence.md](06-source-evidence.md)에서 고정 SHA URL로 추적할 수 있다.
