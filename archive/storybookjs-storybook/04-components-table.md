# 구성요소 표

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태 변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| storybook dispatcher | CLI 진입점 | 명령을 core, create-storybook, @storybook/cli로 분기 | argv, Node version, 설치 package | child process 또는 core import | package manager를 통한 remote package 실행 가능 | code/core/src/bin/dispatcher.ts | 확인됨 [E05] |
| core CLI | CLI | dev/build/index/ai/tools/skills command와 공통 log/telemetry option 등록 | CLI options, env | dev server, static build, JSON index, markdown/tool output | log file 및 option이 가리키는 local FS | code/core/src/bin/core.ts | 확인됨 [E06] [E10] [E18] |
| development bootstrap | server bootstrap | main config/preset/builder를 resolve하고 dev server를 준비 | .storybook config, port/host, environment | address, runtime record, builder 시작 | local port, cache, browser open, telemetry | code/core/src/cli/dev.ts; core-server/build-dev.ts | 확인됨 [E07] [E08] |
| development server | HTTP server | manager/preview, story index, middleware, change detection을 구동 | resolved Options, builder, server | listen한 UI, index route, 선택적 manifest | host validation, access control, local HTTP/WebSocket | code/core/src/core-server/dev-server.ts | 확인됨 [E09] |
| static build | build pipeline | 정적 Storybook site와 index/manifest를 생성 | configDir, outputDir, preset/builder | outputDir files, exit code | outputDir recursive deletion·local FS write·telemetry | code/core/src/core-server/build-static.ts | 확인됨 [E11] [E12] |
| story index | indexing service | story config을 normalize하고 index JSON 생성 | config, indexer, story files | in-memory index 또는 output file | source file read, output file write | code/core/src/core-server/build-index.ts | 확인됨 [E30] |
| skills CLI | agent instruction service | list/get으로 project-specific Markdown instruction 제공 | skill id, cwd/configDir | stdout/stderr Markdown, exit code | target config read, optional telemetry | code/core/src/cli/skills/register.ts; run.ts | 확인됨 [E13] [E14] |
| tools/AI passthrough | agent command surface | registered toolset을 local 실행하거나 일부 runtime command를 MCP로 전달 | tool id/args, cwd/configDir/port | Markdown/JSON response, error outcome | local tool handler; 실행 중 dev server/MCP로 proxy 가능 | code/core/src/bin/core.ts; cli/tools/run.ts; cli/ai/mcp/register.ts | 확인됨 [E16] [E18] |
| addon-mcp | Storybook addon | /mcp handler와 docs/dev/test MCP toolset을 dev server에 붙임 | addon options, preset, HTTP request, feature gate | MCP response, browser landing page, tool metadata | local HTTP endpoint; composition remote ref fetch; Bearer/OAuth requirement 가능 | code/addons/mcp/src/preset.ts; mcp-handler.ts; tools/tool-registry.ts | 확인됨 [E15] [E16] [E17] |
| Codex plugin | agent plugin package | Storybook 작업용 skill bundle와 plugin metadata 제공 | Codex prompt, installed plugin | init/setup/stories/upgrade instruction | skill에 따른 package install, config/file write, dev server, upgrade | code/lib/codex-plugin/plugins/storybook | 확인됨 [E20] [E21] [E22] [E23] [E24] |
| Storybook Vitest project | browser test config | story에 tag vitest를 대상으로 Chromium browser test 실행 | story files, configDir, CI env | test result/retry | Playwright Chromium dependency, local browser | code/vitest.config.storybook.ts | 확인됨 [E25] |
| fork checks | GitHub Actions | fork push에서 type check/format/unit test 수행 | fork push | GitHub Actions job status | checkout·dependency install·Playwright browser install | .github/workflows/fork-checks.yml | 확인됨 [E26] |
| Nx workflow | GitHub Actions | NX Cloud 기반 광범위 task run 정의 | workflow_dispatch와 job condition | task status, Nx Cloud status | secret token, GitHub commit status write | .github/workflows/nx.yml | 확인됨; 자동 trigger 비활성 [E27] |
| release workflow | GitHub Actions | release branch에서 version/publish/release/merge bookkeeping | release branch push 또는 manual input | npm publish, GitHub release/merge, DX registration | write permissions, secrets, remote HTTP, Discord webhook | .github/workflows/publish.yml | 확인됨 [E29] |

## 주의

- 표의 확인됨은 source code/configuration을 읽어 역할을 확인했다는 뜻이다. 어느 project에서 기능이 활성화되어 있거나 실제로 성공했다는 뜻은 아니다.
- 명령·addon이 상태를 바꾸는 권한을 가질 수 있는 경우에도 이 아카이브는 어떤 명령도 실행하지 않았다.

