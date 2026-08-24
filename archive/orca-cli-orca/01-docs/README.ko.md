<div align="center">

<img src="assets/logo.png" alt="orca" width="240">

# orca

**AI 코딩 에이전트를 위한 오케스트레이션 계층**

*팟으로 사냥하세요. 단일 Go 바이너리. 의존성 없음.*

[빠른 시작](#빠른-시작) • [작동 방식](#작동-방식) • [명령](#명령) • [에이전트 설정](#에이전트-설정) • [Symphony와 무엇이 다른가?](#symphony와-무엇이-다른가) • [TUI](#tui) • [전체 문서](DOCS.md)

</div>

---

> **orca** `/ˈɔːr.kə/` — *생물학*: 협력하는 팟으로 사냥하는 최상위 포식자. 백상아리의 유일하게 일관된 천적.

각 에이전트는 세션이 압축되는 순간 전체 실행 컨텍스트를 잃습니다. Orca는 상태를 보유합니다. 즉, 격리된 worktree, 구조화된 실행 로그, 에이전트가 읽고 구동할 수 있는 DAG를 보유하므로 reset 사이에 아무것도 사라지지 않습니다.

Orca는 실행 상태를 SQLite에 저장하고, 모든 에이전트를 자체 git worktree에 격리하며, 모든 에이전트가 구동하거나 구동될 수 있도록 MCP server를 노출하는 **Go 바이너리**입니다. MCP를 지원하는 **모든 에이전트**—Claude Code, Codex, Aider, OpenCode, Cursor, Windsurf 또는 그 외 무엇이든—와 함께 동작합니다.

```
You (CLI, TUI, or MCP client)
    ↓
Orca (single Go binary)
    ├──→ Run state    →  ~/.orca/orca.db        (SQLite + FTS5)
    ├──→ Isolation    →  .orca/runs/<id>/       (git worktrees)
    └──→ Adapters     →  Claude Code · Codex · Aider · OpenCode · Cursor
                          (via MCP stdio)
```

Node.js도 Python도 Docker도 없습니다. **바이너리 하나, SQLite 파일 하나, 이미 이해하고 있는 git worktree**입니다.

## 빠른 시작

### Homebrew (권장)

tap으로 설치하세요. 작동하는 바이너리를 얻는 가장 빠른 방법입니다.

```sh
brew install orca-cli/tap/orca
```

### 소스에서 설치

표준 Go toolchain으로 clone하고 설치합니다.

```sh
git clone https://github.com/orca-cli/orca.git && cd orca && go install ./cmd/orca
```

### 바이너리 다운로드

Linux, macOS, Windows용 사전 빌드 바이너리는 [https://github.com/orca-cli/orca/releases](https://github.com/orca-cli/orca/releases)에서 사용할 수 있습니다. 대상 플랫폼용 archive를 다운로드하고 압축을 푼 다음 `orca` binary를 `PATH`에 둡니다.

그다음 에이전트의 MCP config가 `orca mcp serve`를 가리키게 하세요. 아래 [에이전트 설정](#에이전트-설정)을 참조하세요.

## 작동 방식

#### 에이전트가 실행하고, Orca가 오케스트레이션합니다

에이전트가 코딩 작업을 하고, orca는 격리·상태 추적·리뷰 handoff를 처리합니다. 각 run은 전용 git worktree를 받으므로 병렬 에이전트가 같은 branch를 건드리지 않습니다. pod는 목표를 run의 DAG로 분해하고 의존성 순서에 맞춰 queue에 넣습니다. upstream run이 완료되면 에이전트가 작업을 가져갑니다.

```
You: orca pod create "refactor billing module"
    ↓
Orca decomposes goal → builds DAG → 3 runs queued
    ↓
Each run gets its own git worktree
    ↓
Agents work in parallel, isolated, in their own branches
    ↓
Constraints gate what reaches review
    ↓
You: orca ship run_a3f3  →  PR opens against main
```

#### Run lifecycle

모든 run은 아래 상태 machine을 따라 이동합니다. blocked run은 같은 pod의 upstream dependency를 기다립니다. failed run은 `orca retry`로 feedback과 함께 재시도할 수 있습니다.

```
queued → running → ready → shipped
            ↓        ↓
         blocked  failed → retry
```

#### 12개의 CLI 명령

| 명령 | 목적 |
|---|---|
| `orca run` | goal과 context를 사용해 단일 run 시작 |
| `orca pod create` | pod를 만들고 goal을 run DAG로 분해 |
| `orca watch` | 실행 중인 모든 run과 pod를 보여 주는 live TUI |
| `orca ls` | 상태로 filter할 수 있는 run과 pod 목록 |
| `orca review` | run의 diff, logs, tests, context 열기 |
| `orca ship` | ready 상태의 run을 pull request로 ship |
| `orca diff` | run이 만든 diff 표시 |
| `orca logs` | agent logs를 실시간으로 stream |
| `orca kill` | 활성 run을 취소하고 해당 worktree archive |
| `orca retry` | failed 또는 killed run을 feedback과 함께 재시작 |
| `orca config` | repo별 AGENTS.md, skills, policies 관리 |
| `orca mcp serve` | Orca를 MCP server(stdio)로 실행 |

flags가 포함된 전체 CLI reference는 [DOCS.md](DOCS.md)에 있습니다.

## 에이전트 설정

### Claude Code

다음을 `~/.claude/settings.json`에 추가합니다. project-scoped 설정은 대신 repo root의 `.mcp.json`을 사용하세요. Claude Code는 둘 다 확인하며 repo-level file이 우선합니다.

```json
{
  "mcpServers": {
    "orca": {
      "command": "orca",
      "args": ["mcp", "serve"]
    }
  }
}
```

### OpenCode

global 설정은 `~/.config/opencode/opencode.json`에, 단일 project로 범위를 제한하려면 repo root의 `opencode.json`에 추가합니다.

```json
{
  "mcpServers": {
    "orca": {
      "command": "orca",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Codex

`~/.codex/config.json`에 추가합니다. Codex CLI는 이 파일에서 MCP server 정의를 JSON으로 읽으므로 아래 block을 그대로 넣을 수 있습니다.

```json
{
  "mcpServers": {
    "orca": {
      "command": "orca",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Cursor

project-scoped 설정은 repo root의 `.cursor/mcp.json`에 추가합니다. 모든 repo에서 공유하는 global 설정은 `~/.cursor/mcp.json`을 사용합니다.

```json
{
  "mcpServers": {
    "orca": {
      "command": "orca",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Gemini CLI

`~/.gemini/settings.json`에 추가합니다. Gemini CLI는 시작할 때 이 파일에서 MCP servers를 가져옵니다.

```json
{
  "mcpServers": {
    "orca": {
      "command": "orca",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Windsurf

`~/.codeium/windsurf/mcp_config.json`에 추가합니다. Windsurf는 이 global config file에서 MCP servers를 불러옵니다.

```json
{
  "mcpServers": {
    "orca": {
      "command": "orca",
      "args": ["mcp", "serve"]
    }
  }
}
```

### 다른 모든 MCP 에이전트

MCP server 정의를 읽는 모든 에이전트는 같은 구조를 사용합니다. 해당 에이전트가 MCP config를 기대하는 위치에 추가하세요. `command` field는 이미 `PATH`에 있는 `orca` binary를 가리킵니다.

```json
{
  "mcpServers": {
    "orca": {
      "command": "orca",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Context loss에서도 살아남기 (권장)

context window는 압축되고, 그때 에이전트는 진행 중인 모든 run state를 잃습니다. 확실한 방법은 매 session 시작 때 살아남는 에이전트 instruction file에 directive를 넣어, 에이전트가 매번 읽고 자신이 하던 일을 다시 수립하게 하는 것입니다.

이는 선택적 best-practice note가 아닙니다. 이것이 없으면 긴 실행 pod는 context가 차는 순간 조용히 worktree를 orphan 상태로 남깁니다. 에이전트에 맞는 snippet을 추가하세요.

project의 `CLAUDE.md` 또는 `~/.claude/CLAUDE.md`에 추가합니다.

```markdown
## Orca persistence (mandatory)

On every session start: call `orca_list_runs` via MCP. Surface any active runs to me.
After every meaningful change: stage the worktree via `orca_stage` and route review through `orca_review`.
Never leave runs orphaned — kill or ship them before exiting.
```

repo의 `.orca/AGENTS.md`에 다음을 추가합니다.

```markdown
## Orca run protocol

Every task starts with `orca run` or `orca pod create` — never edit main directly.
Worktree is yours; commit to your branch only.
When done, mark the run ready and exit — orca handles ship and review.
```

이것들은 에이전트가 매 session 시작 시 따라야 하는 지시입니다. Claude Code에는 `CLAUDE.md` snippet을, OpenCode/Codex/그 외에는 `AGENTS.md`를, Cursor에는 `.cursor/rules/orca.mdc` (`alwaysApply: true` 포함)를, Windsurf에는 `.windsurfrules`를 추가하세요.

## Symphony와 무엇이 다른가?

| | **Orca** | **Symphony** |
|---|---|---|
| **라이선스** | MIT | Proprietary |
| **에이전트 종속** | 없음 — 모든 MCP agent | 제한됨 |
| **격리** | git worktrees (native) | Custom sandboxing |
| **저장소** | 단일 SQLite file + git | Proprietary backend |
| **TUI** | Bubble Tea (`orca watch`) | Web only |
| **MCP server** | Built-in (`orca mcp serve`) | 노출하지 않음 |
| **의존성** | `go install` 후 완료 | cloud 필요 |
| **비용** | 무료 (cloud tier optional) | 유료 SaaS |

**핵심 철학의 차이**: Symphony는 orchestration을 cloud 뒤에 숨깁니다. Orca는 orchestration을 terminal-native이고 agent-agnostic한 infrastructure로 다룹니다. 에이전트는 이미 LLM, context, judgment를 갖고 있습니다. Orca는 isolation, state, review handoff를 처리합니다. 그게 전부입니다.

두 도구 모두 multi-agent coordination 문제를 풉니다. 차이는 경계를 어디에 두는가입니다. Symphony는 자신의 API에 경계를 두고, orca는 local git repo에 경계를 둡니다.

## TUI

Orca TUI는 Catppuccin Mocha palette 기반의 Bubble Tea로 만들어졌습니다. 에이전트 옆 terminal에서 실행되어 keyboard를 떠나지 않고 live run과 pod state를 보여 줍니다.

[![TUI Watch](assets/tui-watch.png)](assets/tui-watch.png)

[![TUI Review](assets/tui-review.png)](assets/tui-review.png)

[![TUI Pod DAG](assets/tui-pod.png)](assets/tui-pod.png)

**섹션**

- Watch — 활성 run과 pod의 live view
- Pod View — 진행 중인 pod의 DAG visualization
- Review — 특정 run의 diff, logs, test output
- New Run — terminal을 떠나지 않는 inline goal entry

**탐색**

- `j`/`k` — 위/아래로 이동
- `r` — 선택한 run의 review 열기
- `s` — ready run ship
- `k` — 선택한 run kill
- `n` — 새 run 만들기
- `/` — runs와 pods 전체 검색
- `Esc` — 뒤로 가기
- `q` — 종료

**기능**

- 전체에 Catppuccin Mocha palette 적용
- 수동 refresh 없는 live status update
- running run의 pulse animation
- 완전한 keyboard 중심 — mouse 불필요

## Skills & AGENTS.md

`.orca/` directory는 모든 run이 로드하는 repo별 configuration을 보관합니다. agent guidelines, skill documents, validation policies, component templates가 여기에 있습니다.

```
.orca/
├── AGENTS.md         ← guidelines every run loads
├── orca.toml         ← project config
├── skills/           ← stack-specific patterns
│   ├── kotlin-spring.md
│   └── hexagonal.md
├── policies/         ← validation rules
│   └── arch-rules.yaml
└── templates/        ← new component templates
```

- `AGENTS.md` — 모든 run 시작 시 주입되는 지시입니다. 여기에 coding conventions, review gates, repo-specific rules를 정의합니다.
- `orca.toml` — default agent adapter, concurrency limits, worktree cleanup policy를 담는 project-level config입니다.
- `skills/` — agent가 관련 있을 때 로드하는 stack-specific patterns를 설명하는 Markdown files입니다(예: hexagonal architecture, Spring Boot conventions).
- `policies/` — `orca config validate`가 각 run이 ship되기 전에 검사하는 YAML rule files입니다.
- `templates/` — 새 component의 starter files입니다. `orca run`은 matching templates를 run context에 자동 주입합니다.

어떤 repo에서든 `orca config init`을 실행해 `.orca/` directory를 scaffold하세요. `orca config validate`는 run이 ship되기 전에 `AGENTS.md`와 활성 policies 전체를 검사합니다.

## 명령

전체 CLI surface입니다.

```
orca run <goal>                     Launch a single run
orca pod create <goal>              Create a pod with multiple coordinated runs
orca pod ls                         List active pods
orca watch                          Launch interactive TUI
orca ls                             List runs and pods
orca review <run-id>                Open review screen for a run
orca ship <run-id>                  Ship a ready run as a pull request
orca diff <run-id>                  Show the diff produced by a run
orca logs <run-id>                  Stream the run's agent logs
orca kill <run-id>                  Cancel an active run
orca retry <run-id>                 Relaunch a failed/killed run with feedback
orca config init                    Scaffold .orca/ in current repo
orca config validate                Check AGENTS.md and policies
orca mcp serve                      Start MCP server (stdio transport)
orca version                        Show version
```

## 라이선스

MIT — [LICENSE](LICENSE)를 참조하세요.

**[Engram](https://github.com/Gentleman-Programming/engram)과 자연스럽게 조합됩니다.** Engram은 각 에이전트에 실행과 session reset을 넘어 유지되는 검색 가능한 brain을 제공하고, orca는 격리된 worktree와 구조화된 review gate를 제공합니다. 두 도구는 MCP 위에서 깔끔하게 조합됩니다.

issue와 PR을 환영합니다. [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

---

*orca는 활발히 개발 중입니다. v1.0 전에는 interface가 달라질 수 있습니다.*
