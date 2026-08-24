# 탐색 기록

## 범위와 후보 선정

고정 SHA의 Git tree를 재귀적으로 읽어 안내 문서, 실행 계약, 진입점, 핵심 상태 경계, 대표 검증 파일 순으로 좁혔다. 후보는 40개를 넘었으므로 문서 전체나 테스트 전체를 요약하지 않고, 각 핵심 경로에 최소 하나의 실행 코드와 하나의 설정 또는 테스트 근거를 남겼다.

| 후보군 | 실제로 연 파일 | 선정 이유 |
| --- | --- | --- |
| 제품·운영 문서 | `README.md`, `DEVELOPMENT.md`, `CONTRIBUTING.md`, `AGENTS.md` | 명령, 모드, 로컬 상태, 기여·통합 운영 계약을 확인 |
| 패키지·CI | `package.json`, `checks.yml`, `openwiki-update.yml`, `release.yml` | 배포 CLI, 빌드·테스트, 자동 갱신과 릴리스의 권한 경계를 확인 |
| CLI 경로 | `src/cli/cli.tsx`, `src/cli/runners.ts` | argv가 인증·수집·시각화·에이전트 실행으로 분기하는 실제 진입점을 확인 |
| 생성·복구 경로 | `src/agent/index.ts`, `src/ingestion/code-mode.ts` | init 교체/rollback, Claims, no-op, 모델·체크포인트·repo 파일 쓰기 경계를 확인 |
| 개인 지식 수집 | `src/ingestion/ingestion.ts` | connector pull → agent update의 순차 처리와 오류 상태를 확인 |
| 코딩 에이전트 통합 | `integrations/openwiki/SKILL.md`, `src/integrations/{mcp/server,core/session-manager}.ts` | Codex/Claude 호스트와 OpenWiki의 역할·4개 lifecycle 도구·완료 조건을 확인 |
| 내장 스킬 | `skills/*/SKILL.md` | Mermaid와 connector 작성의 명시된 입력·보안 규칙을 확인 |
| 대표 테스트 | `claims-run-lifecycle`, `update-noop`, `protocol` | Claims 완료 순서, no-op 조건, host lifecycle 입력 검증을 교차 확인 |

## 확인된 기술 스택과 실행 진입점

- **확인된 사실:** 패키지는 ESM TypeScript이고 Node.js `>=22`, pnpm 10.33.2를 선언한다. 배포된 `openwiki` 명령은 `dist/cli/cli.js`를 가리키며 개발 모드는 `tsx src/cli/cli.tsx`를 실행한다. UI는 React/Ink, 테스트는 Vitest, 대화 체크포인트는 SQLite 의존성을 사용한다. [E01]
- **확인된 사실:** 런타임 진입점은 argv를 `parseCommand`로 해석하고, `integrations`·`mcp`는 별도 경로로, 나머지는 환경을 로드한 뒤 auth/ngrok/cron/ingest/visualize/비대화형 run/Ink TUI로 분기한다. [E02]
- **확인된 사실:** 비대화형 code run은 repo setup, code-mode connector pull, `runOpenWikiAgent`를 하나의 telemetry 경계 안에서 순서대로 호출한다. [E03]

## 확인된 핵심 흐름

1. **코드 위키:** `openwiki --init` 또는 `--update`가 현재 Git repo를 대상으로 한다. init은 기존 생성 위키를 복구 가능한 교체 단위로 시작하고, 성공 시 commit, 실패 시 rollback을 시도한다. update는 마지막 상태와 Git 변경을 보고 조건이 맞으면 모델 호출을 건너뛴다. [E04][E05]
2. **에이전트 생성:** 런타임은 `.openwikiignore`, Claims runtime, 모델, DeepAgent graph, connector/Claims 도구, index·번역 middleware, subagent 정의, 파일 시스템 권한을 결합한다. skill과 대화 이력 가상 마운트에는 agent 쓰기를 거부한다. [E05]
3. **개인 지식 수집:** 구성된 source instance마다 deterministic connector pull(가능한 경우)을 먼저 수행하고, 성공 또는 부분 raw 결과를 바탕으로 local wiki agent update를 수행한다. 원본 pull이 파일 없이 오류면 해당 source는 `error`로 끝난다. [E06]
4. **호스트 통합:** Codex/Claude는 저장소 조사와 Markdown 작성에 native tool을 쓰며, OpenWiki MCP는 `begin → claims inspect/resolve → finish`의 결정적 준비·완료를 담당한다. 완료는 `openwiki_finish`가 `{status:"complete"}`를 반환할 때뿐이다. [E07][E08]

## 미확인 범위

- 실제 npm 패키지 설치, 실행 가능한 provider별 모델 호출, OAuth callback, connector API 호출, telemetry 전송, GitHub Actions의 최근 성공 여부는 실행하지 않아 **미확인**이다.
- 13개 provider와 README에 열거된 모든 connector의 개별 구현·권한·retry 차이는 전수 확인하지 않았다.
- `evals/`의 점수 산식과 benchmark 결과, 생성된 `openwiki/` 문서의 사실성·최신성, release workflow의 실제 publish 결과도 **미확인**이다.
