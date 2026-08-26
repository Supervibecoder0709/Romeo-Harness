# 탐색 기록

## 결론

Storybook은 UI 컴포넌트와 페이지를 분리된 환경에서 개발·문서화·테스트하기 위한 TypeScript 모노레포다. 고정 시점의 중심 패키지는 code/core의 storybook이며, 단일 CLI dispatcher가 dev, build, index, ai, tools, skills를 core binary로 보내고 init 및 그 밖의 CLI는 별도 패키지로 위임한다. [E01] [E05]

## 탐색 범위

- 고정 SHA의 recursive tree에서 9,459개 경로를 인벤토리했다.
- 안내·에이전트: README.md, AGENTS.md, CLAUDE.md, code/lib/codex-plugin 및 code/lib/claude-plugin의 인벤토리.
- 실행 계약: root/code/core package.json, CLI dispatcher/core, dev/build/index, static build, core server.
- 에이전트·MCP: skills CLI, tools CLI, addon-mcp preset/registry/handler, Codex plugin manifest 및 네 개 skill 정의.
- 검증·운영: Storybook Vitest project, fork GitHub Actions, Nx workflow, CircleCI setup, release workflow.

## 실제로 연 핵심 파일

| 선정 이유 | 원문 파일 |
| --- | --- |
| 제품 목적·지원 표면 | README.md, code/core/README.md |
| 저장소의 canonical agent 안내 | AGENTS.md, CLAUDE.md |
| CLI 분기와 사용자 명령 | code/core/src/bin/dispatcher.ts, code/core/src/bin/core.ts |
| 개발·정적 빌드의 실제 실행 | code/core/src/cli/dev.ts, code/core/src/cli/build.ts, code/core/src/core-server/build-dev.ts, dev-server.ts, build-static.ts |
| story index 산출 | code/core/src/core-server/build-index.ts |
| agent instruction 제공 | code/core/src/cli/skills/register.ts, run.ts |
| MCP 제공·권한·도구 등록 | code/addons/mcp/src/preset.ts, mcp-handler.ts, tools/tool-registry.ts |
| Codex plugin 계약 | code/lib/codex-plugin/plugins/storybook/.codex-plugin/plugin.json, .mcp.json, skills/*/SKILL.md |
| 테스트·CI·릴리스 | code/vitest.config.storybook.ts, .github/workflows/fork-checks.yml, nx.yml, .circleci/config.yml, publish.yml |

## 확인된 기술 구조

- 언어·패키지 관리: TypeScript 모노레포, Yarn Berry, NX와 custom yarn task runner다. 기본 브랜치는 next이며 Node 22.22.3을 명시한다. [E02]
- 핵심 분리: renderer는 UI framework를 DOM에 mount하고, builder는 Storybook을 bundle/serve하며, framework는 renderer + builder + framework config를 묶는다. [E03]
- 설정·렌더 흐름: .storybook/main.ts를 시작 시 읽고, preview/manager 설정을 각 bundle에 넣으며, story 파일은 runtime 전에 AST index 처리한다. [E04]
- 사용자-facing package: code/core의 storybook package는 CLI/dev server/manager/utility library와 ecosystem용 internal library를 포함한다고 문서화되어 있다. [E01]

## 핵심 흐름 교차 확인

1. CLI dispatcher는 dev/build/index/ai/tools/skills를 core binary로 보내고, init은 create-storybook으로, 기타 명령은 @storybook/cli로 보낸다. [E05]
2. dev는 기본 configDir을 ./.storybook로 잡아 buildDevStandalone을 호출한다. core는 main config와 preset을 두 번 로드해 builder/renderer를 결정하고, dev server는 manager/preview builder와 story index를 시작한다. [E06] [E07] [E08] [E09]
3. build는 기본 outputDir을 ./storybook-static로 잡으며, static build는 outputDir을 비운 뒤 manager, preview, static assets, index.json 및 조건부 manifest를 만든다. [E10] [E11] [E12]
4. skills CLI는 list/get만 제공하고, setup은 가벼운 project probe, 나머지는 target Storybook config load 후 instruction을 조립한다. [E13] [E14]
5. addon-mcp는 dev server에 기본 /mcp endpoint를 등록하고, toolset/feature gate에 따라 docs·dev·test 도구를 등록한다. 구성된 remote refs에는 OAuth/Bearer 인증 요구가 있을 수 있다. [E15] [E16] [E17]

## 문서와 코드의 차이

- Codex plugin의 setup skill은 npx storybook ai setup 실행을 지시한다. 그러나 core CLI는 ai setup을 deprecated로 표시하고 storybook skills get setup 사용을 권한다. 둘 다 고정 SHA에 존재하므로, 자동화 Harness는 plugin 문구만 믿고 실행하지 말고 현재 CLI help/readback을 먼저 확인해야 한다. [E18] [E19]
- AGENTS.md는 dev server의 기본 포트를 6006이라고 안내하지만, 실제 포트는 CLI option과 getServerPort 결과에 따라 정해진다. 6006은 관례적 기본이지 이 아카이브에서 검증된 실행 결과가 아니다. [E02] [E08]

## 미확인 범위

- 어떤 framework/builder/addon 조합이 이 SHA에서 실제로 정상 동작하는지.
- remote MCP composition의 실제 OAuth issuer, token issuance/rotation, remote network reachability.
- CircleCI/Nx/GitHub Actions의 최근 실행 상태·pass/fail 및 npm/GitHub Release의 실제 배포 결과.
- package published version과 source package.json 버전의 일치 여부.

