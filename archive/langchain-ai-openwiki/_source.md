# Source fixation

- Origin URL: https://github.com/langchain-ai/openwiki
- Ref: main
- Commit SHA: `a525ed88fe1f189d08e0f0acf12f42caec2b600e`
- License: MIT
- Analysis timestamp: 2026-08-23T18:48:37Z

## 접근과 재현 범위

- GitHub REST API로 `main`의 기본 브랜치와 커밋 SHA를 확인한 뒤, 해당 SHA의 재귀 트리와 선택한 파일만 읽었다. 트리 응답은 `truncated=false`였다.
- 대상 저장소는 clone하거나 실행하지 않았고, issue/PR/설정/secret/배포에 쓰기 요청을 하지 않았다. 따라서 이 아카이브의 동작 설명은 **고정 SHA의 정적 코드·설정·테스트 근거**이며, 실제 설치·모델 호출·OAuth·CI 실행 결과는 포함하지 않는다.
- `gh` 읽기 인증은 확인했지만 토큰 값·환경 변수 값·저장소 secret은 조회하지 않았다.

## 제외 또는 제한한 후보

- `pnpm-lock.yaml`, `static/`, `.changeset/`는 실행 경로 판별에 직접 필요하지 않아 내용 검토에서 제외했다.
- 이미 생성된 `openwiki/` Markdown과 `openwiki/.claims/` JSON은 이 저장소가 자기 자신에 대해 생성한 결과물이다. `AGENTS.md`가 가리키는 방식만 확인했고, 결과물의 서술을 실행 동작의 독립 근거로 사용하지 않았다.
- `evals/ledger/**`, `evals/deepswe/**`, 개별 connector 구현, 전체 테스트군은 규모가 커서 전수 열람하지 않았다. 이 아카이브에는 대표 수명주기·no-op·통합 프로토콜 테스트만 반영했다.
- `src/agent/index.ts`(74KB), `src/cli/commands.ts`(34KB) 등 큰 파일은 실행 진입·생성·스트리밍·완료 처리와 직접 연결된 구간만 읽었다. 열지 않은 함수의 세부 동작은 미확인으로 남긴다.

## 읽은 원문

README.md, AGENTS.md, DEVELOPMENT.md, CONTRIBUTING.md, package.json, `.github/workflows/{checks,openwiki-update,release}.yml`, `integrations/openwiki/SKILL.md`, `skills/{mermaid-diagrams,write-connector}/SKILL.md`, `src/{cli/cli.tsx,cli/runners.ts,agent/index.ts,ingestion/ingestion.ts,ingestion/code-mode.ts,integrations/mcp/server.ts,integrations/core/session-manager.ts}`, 그리고 `test/{agent/claims-run-lifecycle,agent/update-noop,integrations/protocol}.test.ts`.

근거 ID와 정확한 원문 URL·줄 범위는 [06-source-evidence.md](06-source-evidence.md)에 있다.
