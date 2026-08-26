# 구성요소 표

`근거 상태`의 **사실**은 고정 SHA의 원문을 직접 읽은 내용, **해석**은 여러 사실을 연결한 결론, **미확인**은 실행하지 않은 동작이다.

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
|---|---|---|---|---|---|---|---|
| `skills/` | instruction library | 14개 workflow skill의 본문 제공 | agent request/context | agent가 따를 절차 | 자체 강제 엔진 아님 | [E02](06-source-evidence.md#e02), [E13](06-source-evidence.md#e13) | 사실 |
| `using-superpowers` | bootstrap skill | action 전 관련 skill을 탐색·호출하도록 규정 | 모든 대화 시작 | 후속 skill 선택 | harness의 skill loader 필요 | [E13](06-source-evidence.md#e13) | 사실 |
| `brainstorming` | process skill | spike/bounded/architectural 분류와 승인 gate | 아이디어·변경 요청 | 승인된 설계, spec 또는 조사 추천 | 구현 전 사람 승인 요구 | [E14](06-source-evidence.md#e14) | 사실 |
| `writing-plans` | process skill | spec을 실행 가능한 task plan으로 분해 | spec/requirements | `docs/superpowers/plans/...` plan | 코드 변경 전 문서 산출물 | [E15](06-source-evidence.md#e15) | 사실 |
| `executing-plans` | process skill | 별도 session의 inline plan execution | written plan | task progress, verification, finish skill 호출 | blocker/불명확 시 사람에게 질문 | [E15](06-source-evidence.md#e15) | 사실 |
| `subagent-driven-development` | orchestration skill | fresh implementer·reviewer를 task 단위로 조정 | plan, spec, worktree, task brief | ledger, briefs, reports, review packages, commits | merge/push/publish 등 worktree 밖 side effect에서 중지 | [E16](06-source-evidence.md#e16), [E17](06-source-evidence.md#e17) | 사실 |
| `test-driven-development` | quality skill | RED→GREEN→REFACTOR | feature/bugfix behavior | failing test, minimal implementation, green test | production code 전 failing test 요구 | [E18](06-source-evidence.md#e18) | 사실 |
| `systematic-debugging` | quality skill | 근본 원인→가설→최소 시험→수정 | bug/test/build symptom | root-cause evidence와 fix test | 3회 실패 뒤 architecture discussion | [E18](06-source-evidence.md#e18) | 사실 |
| `verification-before-completion` | completion gate | 성공 주장 전 fresh command/output 검증 | completion claim | evidence-backed status | commit/PR/delegation도 gate 대상 | [E19](06-source-evidence.md#e19) | 사실 |
| `using-git-worktrees` | isolation skill | native worktree 우선, fallback과 baseline test | repository/worktree state | isolated workspace 또는 in-place decision | 새 worktree 전 동의, `git check-ignore` 확인 | [E20](06-source-evidence.md#e20) | 사실 |
| `requesting-code-review` | review skill | task·feature·merge 전 reviewer dispatch | diff, requirements, base/head SHA | severity별 findings | reviewer에게 session history 대신 제한된 context 제공 | [E20](06-source-evidence.md#e20) | 사실 |
| `finishing-a-development-branch` | integration skill | test 후 merge/PR/keep menu·cleanup | passing working tree, base branch | local merge, pushed branch/PR, or preserved worktree | merge/push/PR은 인간 선택; discard는 literal `discard` 확인 | [E21](06-source-evidence.md#e21) | 사실 |
| `.codex-plugin/plugin.json` | Codex manifest | Codex에 skills directory 제공 | Codex plugin install | skill discovery 설정 | `hooks: {}`; Claude hook 자동 탐색을 막으려는 설정으로 보임 | [E06](06-source-evidence.md#e06) | 사실 + 해석 |
| `hooks/session-start` | shell bootstrap | `using-superpowers`를 JSON context로 inject | SessionStart, platform env vars | Claude/Cursor/Copilot 형식의 context JSON | local plugin file read, stdout JSON | [E08](06-source-evidence.md#e08) | 사실 |
| `.opencode/plugins/superpowers.js` | OpenCode adapter | skill path 등록 및 first-user message bootstrap | OpenCode config/message hook | modified in-memory config/messages | local `SKILL.md` read; no manual symlink/config file write | [E10](06-source-evidence.md#e10) | 사실 |
| `.pi/extensions/superpowers.ts` | Pi adapter | skill path registration, session/compaction-aware injection | Pi events | injected user message | local file read; native/optional tool mapping | [E11](06-source-evidence.md#e11) | 사실 |
| `.hermes-plugin/__init__.py` | Hermes adapter | stock skill 등록 및 first-turn context injection | Hermes plugin hooks | `ctx.register_skill`, `pre_llm_call` context | local path read; loud error if skills absent | [E12](06-source-evidence.md#e12) | 사실 |
| `.kimi-plugin/plugin.json`, `GEMINI.md` | Kimi/Gemini adapters | session skill 또는 instructions-file bootstrap | manifest/context file | native skill/tool mapping | harness-specific | [E07](06-source-evidence.md#e07) | 사실 |
| brainstorm server | optional local runtime | browser visual Q&A를 serve·watch·event capture | HTML content files, authenticated HTTP/WS | browser page, reload broadcast, `state/events` | local filesystem, localhost/optional remote bind, browser launcher | [E25](06-source-evidence.md#e25)~[E28](06-source-evidence.md#e28) | 사실 |
| tests | verification assets | adapter/server/selected skill behaviors를 확인하려는 suite | Node/Bash/Python/harness sessions | pass/fail exit code | 일부 real LLM/CLI와 temp project 필요 | [E23](06-source-evidence.md#e23), [E24](06-source-evidence.md#e24), [E30](06-source-evidence.md#e30) | 사실; 이 분석에서 실행은 미확인 |
| `scripts/sync-to-codex-plugin.sh` | distribution script | external Codex plugin fork에 sync/PR하는 경로 | local checkout, git/gh/rsync | commit, push, PR 가능 | 명백한 external write; 이 아카이브에서는 미실행 | [E22](06-source-evidence.md#e22) | 사실; 실제 결과 미확인 |
