# Superpowers 테스트하기

> 원문: [`docs/testing.md`](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/docs/testing.md) — 고정 SHA `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`의 한국어 번역.

Superpowers에는 서로 다른 두 종류의 test가 있고 각각 별도 directory에 있다.

- **`tests/`** — plugin의 non-LLM code가 동작하는가? brainstorm-server JS, OpenCode plugin loading, codex-plugin sync, analysis utility를 위한 Bash + node + python integration test다.
- **`evals/`** — 실제 LLM session에서 agent가 올바르게 행동하는가? Claude Code / Codex / Gemini CLI의 실제 tmux session을 Python harness가 구동하고 LLM actor와 verifier가 skill compliance를 판단한다.

## Plugin test

`tests/`에 있다. 현재는 다음과 같다.

- `tests/brainstorm-server/` — brainstorm server JS code의 node test suite.
- `tests/opencode/` — OpenCode plugin loading, bootstrap caching, tool registration의 bash test.
- `tests/codex-plugin-sync/` — bash sync verification.
- `tests/kimi/` — Kimi plugin manifest wiring의 bash/Python check.
- `tests/claude-code/test-helpers.sh`, `analyze-token-usage.py` — 남은 bash test가 사용하는 utility.
- `tests/claude-code/test-subagent-driven-development.sh` — agent가 SDD를 설명할 수 있는지 보는 test. drill counterpart는 없고 behavior가 아닌 description-recall을 test한다.
- `tests/claude-code/test-subagent-driven-development-integration.sh` — token analysis가 있는 확장 SDD integration. drill이 YAGNI subset을 다루고, bash는 commit count, Claude Code task tracking, token telemetry assertion을 추가한다.
- `tests/claude-code/test-worktree-native-preference.sh` — worktree skill의 RED-GREEN-REFACTOR validation. drill이 PRESSURE phase를 다루고 bash가 RED/GREEN baseline도 다룬다.
- `tests/explicit-skill-requests/` — drill이 다루지 않는 Haiku-specific, multi-turn, skill-name-prompted test.

Plugin test는 해당 directory의 `run-*.sh` 또는 `npm test`로 실행한다.

## Skill behavior eval

`evals/`에 있다. harness는 Drill이며 scenario는 `evals/scenarios/*.yaml`에 있다. setup은 `evals/README.md`를 본다. 빠른 시작 예시는 다음과 같다.

```bash
cd evals
uv sync --extra dev
export ANTHROPIC_API_KEY=sk-...
uv run drill run triggering-test-driven-development -b claude
```

Drill scenario는 느리고(각각 3~30분 이상), 실제 LLM session을 실행한다. 현재 CI에는 포함되지 않으며, 자연스러운 후속 작업은 PR의 fast subset, nightly 및 on-demand full sweep으로 구성된 tiered model이다.
