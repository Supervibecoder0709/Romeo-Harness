# 핵심 구성요소

## 먼저 알아둘 점

이 고정 커밋에는 `.agents/skills/`, `.claude/agents/`, `.claude/skills/`, `AGENTS.md`, `CLAUDE.md`, `SKILL.md`가 없다.[E02] 따라서 번역할 agent/skill 정의 파일은 없으며, 여기서는 코드로 실제 존재하는 핵심 구성요소만 설명한다.

## CLI shell

`cmd/orca/main.go`는 `cli.Execute()`만 호출한다. `internal/cli/root.go`는 Cobra의 root command를 만들고 오류를 exit code 1로 바꾼다. `version.go`만 `rootCmd.AddCommand`를 호출하므로, 이 SHA에서 확정 가능한 CLI 기능은 version 출력이다.[E04][E05]

## Adapter port와 registry

`adapter.Adapter`는 agent 이름, capability, 실행 전 환경 검증, 실행 시작을 요구한다. `LaunchRequest`에는 run ID, 절대 worktree path, prompt, context file 목록이 들어가며, `Handle`은 PID와 session ID를 담는다.[E07]

`Registry`는 이름과 factory를 매핑해 중복 등록과 존재하지 않는 adapter를 오류로 처리한다. 이는 여러 agent provider를 붙일 수 있게 만든 경계이지만, 실제 Claude/Codex/Aider 실행 구현이나 등록 코드는 없다.[E08][E14]

## State machine

`state`는 `queued`, `pending`, `running`, `blocked`, `ready`, `failed`, `shipped`, `killed`와 이벤트를 정의한다. `Apply`는 legal pair만 허용하는 부수 효과 없는 함수이고, legal/illegal/unknown 상태 테스트가 있다.[E09][E10][E15]

이 구성요소는 “어떤 상태가 다음으로 갈 수 있는가”만 답한다. 누가 event를 발생시키는지, 제약을 어떻게 실행하는지, DB에 언제 기록하는지는 `runner` 구현이 없어서 확인할 수 없다.

## SQLite Store와 schema

`store.Open`은 pure-Go SQLite driver로 DB를 열고 foreign keys, busy timeout, file DB의 WAL, embedded migration을 적용한다. single writer connection을 설정한다.[E11]

초기 schema는 pods/runs/dependencies/context files/constraints/logs/events와 FTS5 index 및 insert trigger를 정의한다. 구현된 public CRUD는 현재 runs의 create/get/list/update와 short-ref resolve 일부다. pods/logs/events/dependency의 public CRUD API는 이 tree에서 확인되지 않는다.[E12]

## Worktree manager

`CreateForRun`은 primary repo root를 `git rev-parse`로 정규화하고 `.orca/runs/<runID>`에 `orca/<runID>` branch를 만든다. base branch가 empty면 명시 오류를 반환한다. `Archive`는 worktree directory를 옮긴 뒤 stale registry를 prune하며, prune 실패는 보존 후 non-fatal로 다룬다.[E13]

이 함수들은 로컬 git와 파일 시스템을 실제 변경할 수 있다. 하지만 상위 CLI/runner가 이 함수에 연결된 증거는 없다.

## 계획만 있는 package

`config`, `constraint`, `mcp`, `pod`, `runner`, `tui`는 패키지 역할을 설명하는 `doc.go`만 있다. 예를 들어 MCP server, constraint evaluation, pod lifecycle, TUI를 README가 설명하지만 해당 구현 파일은 없으므로 기능·권한·실패 처리·테스트는 **미확인**이다.[E20]
