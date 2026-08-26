# Source evidence

모든 link는 분석을 고정한 commit SHA db12626a58d505f5551ae1d2c714c6249849212a를 가리킨다. line range는 이 아카이브의 사실을 뒷받침하는 최소 범위이며, 해석은 해당 문서에서 사실/추론으로 분리했다.

| ID | 원문 URL · line | 뒷받침하는 사실 |
| --- | --- | --- |
| E01 | [code/core/README.md L26-L38](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/README.md#L26-L38) | storybook core package의 CLI, dev server, manager, utilities, internal library 범위 |
| E02 | [AGENTS.md L7-L19](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/AGENTS.md#L7-L19) | TypeScript monorepo, code/scripts 위치, next, Node/Yarn/NX/lint/typecheck 안내 |
| E03 | [AGENTS.md L43-L79](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/AGENTS.md#L43-L79) | renderer, builder, framework의 역할과 core 영역 |
| E04 | [AGENTS.md L80-L107](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/AGENTS.md#L80-L107) | main/preview/manager, AST index, open service/toolset, agent skill 구조 |
| E05 | [dispatcher.ts L18-L92](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/bin/dispatcher.ts#L18-L92) | CLI command 분기, Node version check, package-manager remote fallback |
| E06 | [core.ts L44-L156](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/bin/core.ts#L44-L156) | 공통 option/log handling과 dev CLI option/action |
| E07 | [cli/dev.ts L37-L63](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/cli/dev.ts#L37-L63) | dev의 기본 configDir, DEVELOPMENT mode, telemetry wrapper |
| E08 | [build-dev.ts L76-L386](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/core-server/build-dev.ts#L76-L386) | port/config/preset/builder resolution, runtime record, smoke test, startup output |
| E09 | [dev-server.ts L30-L229](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/core-server/dev-server.ts#L30-L229) | middleware, manager/preview start, listening, cleanup, manifest registration |
| E10 | [core.ts L158-L231](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/bin/core.ts#L158-L231) | build/index CLI option, env mapping, success/error output |
| E11 | [build-static.ts L40-L55](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/core-server/build-static.ts#L40-L55) | outputDir empty/root guard와 recursive deletion/create |
| E12 | [build-static.ts L57-L253](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/core-server/build-static.ts#L57-L253) | preset/build, static assets, index, manifest, project metadata, telemetry |
| E13 | [skills/register.ts L23-L98](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/cli/skills/register.ts#L23-L98) | skills list/get command, target selection, config loading, output/exit handling |
| E14 | [skills/run.ts L37-L123](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/cli/skills/run.ts#L37-L123) | skill ID validation, setup probe, config load error, instruction assembly |
| E15 | [addon-mcp preset.ts L27-L117](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/addons/mcp/src/preset.ts#L27-L117) | endpoint default/option parsing, composition refs, local access, OAuth protected-resource, Bearer check |
| E16 | [tool-registry.ts L162-L318](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/addons/mcp/src/tools/tool-registry.ts#L162-L318) | dev/docs/test MCP tool definitions, availability gates, missing toolset handling |
| E17 | [mcp-handler.ts L27-L89](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/addons/mcp/src/mcp-handler.ts#L27-L89) | MCP server initialization, feature availability, instruction generation, tool registration |
| E18 | [core.ts L244-L307](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/bin/core.ts#L244-L307) | deprecated ai setup, experimental AI passthrough, tools/skills command registration |
| E19 | [cli/ai/index.ts L13-L89](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/cli/ai/index.ts#L13-L89) | ai setup deprecation, React+Vite condition, cache/telemetry/output file behavior |
| E20 | [Codex plugin manifest L1-L34](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/lib/codex-plugin/plugins/storybook/.codex-plugin/plugin.json#L1-L34) and [.mcp.json L1-L3](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/lib/codex-plugin/plugins/storybook/.mcp.json#L1-L3) | plugin metadata, skills path, MCP reference, Interactive/Write capability, empty server map |
| E21 | [init SKILL.md L1-L8](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/lib/codex-plugin/plugins/storybook/skills/init/SKILL.md#L1-L8) | Storybook/addon installation과 setup 전환 |
| E22 | [setup SKILL.md L1-L13](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/lib/codex-plugin/plugins/storybook/skills/setup/SKILL.md#L1-L13) | setup precondition, version, ai setup command |
| E23 | [stories SKILL.md L1-L25](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/lib/codex-plugin/plugins/storybook/skills/stories/SKILL.md#L1-L25) | UI 작업 선행 skill, addon install, server lifecycle, AI help/readback |
| E24 | [upgrade SKILL.md L1-L10](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/lib/codex-plugin/plugins/storybook/skills/upgrade/SKILL.md#L1-L10) | version threshold와 upgrade instruction source |
| E25 | [code/vitest.config.storybook.ts L1-L62](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/vitest.config.storybook.ts#L1-L62) | Storybook Vitest project, tags, Playwright Chromium, retry/exclusions |
| E26 | [fork-checks.yml L1-L80](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/.github/workflows/fork-checks.yml#L1-L80) | fork push에서 check/format/unit test와 Windows/Ubuntu matrix |
| E27 | [nx.yml L1-L103](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/.github/workflows/nx.yml#L1-L103) | NX Cloud license로 disabled된 automatic trigger, manual dispatch, task list |
| E28 | [CircleCI config.yml L1-L60](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/.circleci/config.yml#L1-L60) | dynamic generated config와 workflow parameter gate |
| E29 | [publish.yml L1-L260](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/.github/workflows/publish.yml#L1-L260) | release trigger, write permissions, version commit/push, publish, DX/Discord, GitHub release/merge |
| E30 | [build-index.ts L12-L45](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/code/core/src/core-server/build-index.ts#L12-L45) | story normalization, generator initialization, index JSON file write |
| E31 | [AGENTS.md L240-L272](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/AGENTS.md#L240-L272) | component story play function, unit/E2E/test-runner guidance |
| E32 | [README.md L47-L142](https://github.com/storybookjs/storybook/blob/db12626a58d505f5551ae1d2c714c6249849212a/README.md#L47-L142) | product statement, supported framework/example table, addon capabilities |

## Evidence gaps

- API metadata that established default branch next and commit SHA was read from GitHub REST endpoints, not a line-addressable repository file. The fixed SHA is recorded in _source.md.
- No local or hosted execution logs were collected. Consequently no evidence ID asserts deployment, package publication, CI pass, browser rendering, endpoint reachability, or marketplace availability.

