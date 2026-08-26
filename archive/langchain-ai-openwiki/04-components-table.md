# 구성요소 표

`근거 상태`의 **확인됨**은 고정 SHA 원문을 열어 확인했다는 뜻이며, 실제 운영 성공을 뜻하지 않는다.

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태 변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `openwiki` CLI | Node CLI | argv를 표준 run·integration·MCP로 분기 | `process.argv`, TTY, cwd | stderr/stdout 또는 Ink TUI | 로컬 env 및 프로세스 | `src/cli/cli.tsx` | 확인됨 [E02] |
| standard runners | 실행 orchestration | code setup·connector pull·agent run·telemetry를 연결 | parsed run command | exit code, 출력 event | repo·`~/.openwiki`·provider로 이어짐 | `src/cli/runners.ts` | 확인됨 [E03] |
| OpenWiki agent | DeepAgents graph | 위키를 생성/갱신하고 stream을 종료 처리 | command, cwd, 모델, ignore, Claims | wiki 파일·Claims·metadata | 모델 provider, local FS | `src/agent/index.ts` | 확인됨 [E04][E05] |
| Claims runtime | 증거 상태 | page claim과 evidence를 준비·finalize | repo source, wiki page, Claims operation | `.claims` sidecar와 verified 관계 | repository evidence | `src/agent/index.ts`, `session-manager.ts` | 확인됨 [E04][E08] |
| code setup | repo mutation boundary | managed agent block과 최초 schedule workflow를 준비 | repo root, init/update flag | `AGENTS.md`, `CLAUDE.md`, 선택적 workflow | target repository 파일 시스템 | `src/ingestion/code-mode.ts` | 확인됨 [E09][E11] |
| personal ingestion | source pipeline | connector raw pull 뒤 local wiki update | source instance/config, target | source별 status·raw files·wiki 갱신 | external connector 및 `~/.openwiki` | `src/ingestion/ingestion.ts` | 확인됨 [E06] |
| OpenWiki MCP | protocol adapter | lifecycle 4개 도구를 MCP에 등록 | validated tool input | structured success / bounded error | stdio MCP host boundary | `src/integrations/mcp/server.ts` | 확인됨 [E13] |
| Host session manager | stateful lifecycle | begin/inspect/resolve/finish와 run exclusivity | root, mode, runId, Claims ops | complete metadata, final artifacts | host-native repo writing과 OpenWiki finalization | `src/integrations/core/session-manager.ts` | 확인됨 [E08] |
| `openwiki` host skill | skill definition | host 조사·저작과 lifecycle 도구의 역할을 규정 | repository documentation request | 완료된 wiki 또는 interrupted run | host native tools + MCP | `integrations/openwiki/SKILL.md` | 확인됨 [E07] |
| Mermaid skill | skill definition | 근거 기반 Mermaid 작성·수정 규칙 | 위키 페이지/실행 흐름 | Mermaid fence 또는 읽을 수 있는 text fallback | generated Markdown | `skills/mermaid-diagrams/SKILL.md` | 확인됨 [E14] |
| connector authoring skill | skill definition | 내장 connector의 설계·보안 계약 | 새 source connector 요청 | TypeScript source/test 변경 지침 | API, `~/.openwiki`, MCP | `skills/write-connector/SKILL.md` | 확인됨 [E15] |
| scheduled update workflow | GitHub Actions | daily/manual docs update 후 PR 생성 | Actions schedule/dispatch, provider secret | `openwiki/update` branch PR | repo write, PR write, provider API | `.github/workflows/openwiki-update.yml` | 확인됨 [E16] |
| checks workflow | GitHub Actions | formatting/lint/build/test/audit gate | push/PR | job pass/fail, SARIF | GitHub Actions·security events | `.github/workflows/checks.yml` | 확인됨 [E17] |
| release workflow | GitHub Actions | changeset version PR 또는 npm publish | main push, opt-in fork variable | tag/PR/npm release 가능 | contents/PR/id-token write | `.github/workflows/release.yml` | 확인됨 [E18] |
