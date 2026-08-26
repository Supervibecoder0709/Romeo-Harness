# Runtime adapter와 bootstrap 구성요소

> 원문 근거: [E05](../06-source-evidence.md#e05)~[E12](../06-source-evidence.md#e12). 이 파일은 코드의 동작 설명이며 설치 성공의 증명은 아니다.

## 공통 역할

각 adapter의 목적은 두 가지다.

1. harness가 `skills/` directory를 발견하거나 등록하게 한다.
2. 첫 대화에서 `using-superpowers` 내용을 bootstrap으로 넣어 agent가 다른 skill을 먼저 선택하게 한다.

둘 중 하나가 빠지면 파일은 설치돼도 행동 workflow는 살아나지 않을 수 있다.

| Harness | 선언/진입점 | bootstrap 방식 | 코드에서 확인한 failure·중복 경계 |
|---|---|---|---|
| Codex | `.codex-plugin/plugin.json` | `skills: "./skills/"` native discovery에 의존하는 구성 | `hooks: {}`가 명시되어 있다. native discovery의 실제 성공은 이 분석에서 미검증. [E06](../06-source-evidence.md#e06) |
| Claude Code | `.claude-plugin` + `hooks/hooks.json` | `SessionStart` command가 `hooks/session-start`를 실행 | plugin root에서 `using-superpowers/SKILL.md`를 읽고 nested context JSON 출력. [E08](../06-source-evidence.md#e08) |
| Cursor | `.cursor-plugin/plugin.json` + `hooks/hooks-cursor.json` | 같은 script가 `additional_context` 형식 출력 | `CURSOR_PLUGIN_ROOT`가 있으면 Cursor 형식을 우선한다. [E08](../06-source-evidence.md#e08) |
| Copilot CLI | Claude-compatible hook path | 같은 script가 top-level `additionalContext` 형식 출력 | unknown platform도 SDK standard format으로 fallback. [E08](../06-source-evidence.md#e08) |
| OpenCode | root `package.json` → `.opencode/plugins/superpowers.js` | config hook에 skill path를 넣고 첫 user message 앞에 bootstrap을 삽입 | bootstrap file이 없으면 `null`; marker가 있으면 double injection을 skip. [E05](../06-source-evidence.md#e05) [E10](../06-source-evidence.md#e10) |
| Pi | root `package.json` → `.pi/extensions/superpowers.ts` | `resources_discover`와 `context` event; session start/compact 후 다시 inject | cached read; read error면 `null`; marker로 중복 검사. [E05](../06-source-evidence.md#e05) [E11](../06-source-evidence.md#e11) |
| Hermes | `.hermes-plugin/plugin.yaml` → `__init__.py` | 모든 stock skill을 native loader에 등록하고 first `pre_llm_call`에 context 반환 | 두 install layout에서 skills dir를 찾고 없으면 RuntimeError. [E12](../06-source-evidence.md#e12) |
| Kimi Code | `.kimi-plugin/plugin.json` | `sessionStart.skill: "using-superpowers"` | manifest 안에 harness tool mapping이 있다. [E07](../06-source-evidence.md#e07) |
| Gemini CLI | `gemini-extension.json` + `GEMINI.md` | `contextFileName`으로 `GEMINI.md`; 두 파일을 `@` include | context file이 bootstrap/mapping을 참조한다. [E07](../06-source-evidence.md#e07) |

## PM 관점의 확인 방법

**설치 직후에는 adapter 유형에 맞는 증거를 하나씩 얻어야 한다.** manifest가 보인다는 것만으로는 부족하다.

- native discovery형(Codex/Kimi): clean session transcript에서 `using-superpowers`와 관련 skill 선택이 보이는지 확인한다.
- hook형(Claude/Cursor/Copilot): hook command의 JSON output shape와 session context 주입을 확인한다. `hooks/session-start`는 소비자별 field를 하나만 내도록 작성됐다. [E08](../06-source-evidence.md#e08)
- in-process형(OpenCode/Pi/Hermes): first message/context에 marker가 한 번 들어가고, compaction 뒤 필요한 경우 재삽입되는지를 확인한다. [E10](../06-source-evidence.md#e10) [E11](../06-source-evidence.md#e11)

**추론**: 여러 harness를 동시에 지원하려면 skill 본문을 fork해 고치기보다 adapter와 tool mapping을 분리해 유지하는 편이 이 source의 구조와 맞다. 단, 어떤 harness가 어느 callback을 실제로 제공하는지는 해당 harness의 현재 공식 문서와 live test로 다시 검증해야 한다.
