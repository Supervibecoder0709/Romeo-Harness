# 원문 근거 색인

모든 URL은 분석을 고정한 `a525ed88fe1f189d08e0f0acf12f42caec2b600e` commit을 가리킨다. 줄 범위는 GitHub 원문에서 읽은 범위다.

| ID | 파일·줄 | 원문 URL | 뒷받침하는 사실 |
| --- | --- | --- | --- |
| E01 | `package.json:2-12,37-59,61-86,119-125` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/package.json#L2-L125 | CLI bin, Node/pnpm, scripts, 핵심 runtime 의존성 |
| E02 | `src/cli/cli.tsx:39-115` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/src/cli/cli.tsx#L39-L115 | argv parsing, env load, command 분기, TUI/print 경로 |
| E03 | `src/cli/runners.ts:150-182,260-336` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/src/cli/runners.ts#L150-L336 | ingest summary/exit code, code setup·connector·agent·telemetry 실행 순서 |
| E04 | `src/agent/index.ts:161-346` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/src/agent/index.ts#L161-L346 | env/skill/ignore/Claims, no-op, init replacement commit/rollback |
| E05 | `src/agent/index.ts:533-635,637-889,954-1005,1110-1143` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/src/agent/index.ts#L533-L1143 | DeepAgent graph, virtual mount write denial, stream 실패 처리, finalize, checkpoint |
| E06 | `src/ingestion/ingestion.ts:65-220,270-346` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/src/ingestion/ingestion.ts#L65-L346 | source instance 순차 처리, deterministic pull, result status, untrusted data 지침 |
| E07 | `integrations/openwiki/SKILL.md:6-55` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/integrations/openwiki/SKILL.md#L6-L55 | host skill의 요구 순서와 금지 규칙 |
| E08 | `src/integrations/core/session-manager.ts:297-465,477-583` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/src/integrations/core/session-manager.ts#L297-L583 | begin/finish session, interrupted/complete 상태, Claims 도구, run exclusivity |
| E09 | `README.md:40-60,111-130,210-218` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/README.md#L40-L218 | quickstart, code/personal mode, local state, owned wiki 설명 |
| E10 | `test/agent/update-noop.test.ts:56-196,199-247` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/test/agent/update-noop.test.ts#L56-L247 | no-op/변경/ignore/interrupted 조건의 테스트 |
| E11 | `src/ingestion/code-mode.ts:18-96,191-256` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/src/ingestion/code-mode.ts#L18-L256 | 최초 workflow 생성, managed AGENTS/CLAUDE marker 처리 |
| E12 | `src/agent/index.ts:1309-1352` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/src/agent/index.ts#L1309-L1352 | provider retry와 output limit을 model constructor에 전달 |
| E13 | `src/integrations/mcp/server.ts:10-99` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/src/integrations/mcp/server.ts#L10-L99 | MCP instructions, tool registration, bounded error handling |
| E14 | `skills/mermaid-diagrams/SKILL.md:6-44` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/skills/mermaid-diagrams/SKILL.md#L6-L44 | Mermaid 사용·근거·문법·update 규칙 |
| E15 | `skills/write-connector/SKILL.md:6-56` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/skills/write-connector/SKILL.md#L6-L56 | connector 설계·secret·ingestion 지침 |
| E16 | `.github/workflows/openwiki-update.yml:1-90` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/.github/workflows/openwiki-update.yml#L1-L90 | scheduled/manual docs update, secrets, workflow restore, PR write |
| E17 | `.github/workflows/checks.yml:1-185` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/.github/workflows/checks.yml#L1-L185 | format/lint/build/smoke/test/windows/audit CI gates |
| E18 | `.github/workflows/release.yml:1-72` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/.github/workflows/release.yml#L1-L72 | release opt-in, privileged permissions, changeset/NPM OIDC publishing |
| E19 | `test/integrations/protocol.test.ts:42-165` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/test/integrations/protocol.test.ts#L42-L165 | strict lifecycle schema와 4개 MCP tool test |
| E20 | `README.md:122-130,246-280,336-349,476-491` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/README.md#L122-L491 | config dir, provider/ChatGPT OAuth, telemetry 설명 |
| E21 | `test/agent/claims-run-lifecycle.test.ts:152-184,245-260` | https://github.com/langchain-ai/openwiki/blob/a525ed88fe1f189d08e0f0acf12f42caec2b600e/test/agent/claims-run-lifecycle.test.ts#L152-L260 | Claim resolve 후 page write와 lifecycle finalization을 검증하는 test harness |
