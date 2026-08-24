---
name: oma-orchestration
description: CLI subagent를 병렬 spawn하고 MCP Memory로 조율하며 진행 상황을 모니터링하는 자동 멀티 에이전트 orchestration. orchestration, parallel execution, 자동 멀티 에이전트 workflow에 사용합니다.
---

# Orchestration - 자동 멀티 에이전트 조율

## Scheduling

### 목표

task decomposition, native/fallback dispatch, memory coordination, progress monitoring, verification, QA cross-review, retry, result collection으로 멀티 에이전트 실행을 자동 조율합니다.

### Intent signature

- 사용자가 orchestration, parallel run, 자동 멀티 에이전트 실행, end-to-end full-stack coordination을 요청합니다.
- 작업에 여러 specialist agent와 지속적인 review/remediation loop가 필요합니다.

### 사용할 때

- 복잡한 기능에 병렬로 일할 여러 specialist agent가 필요할 때
- 사용자가 agent를 직접 spawn하지 않고 자동 실행을 원할 때
- backend, frontend, mobile, QA를 아우르는 full-stack 구현일 때
- 사용자가 “자동으로 실행”, “병렬로 실행” 또는 같은 의미의 요청을 할 때

### 사용하지 않을 때

- 단순한 single-domain task: 해당 specific agent를 직접 사용합니다.
- 사용자가 단계별 manual control을 원함: `oma-coordination`을 사용합니다.
- 빠른 bug fix 또는 작은 변경입니다.

### 예상 입력

- 복잡한 feature 또는 workflow 요청
- project config, model/vendor routing, agent type, task constraint, workspace/session 필요사항
- acceptance criteria 및 verification expectation

### 예상 출력

- orchestrator session state, task board, progress file, result file, final summary
- mechanical check, automated verify, QA cross-review 뒤의 specialist agent output
- loop 실패 시 review history와 retry/remediation 상태

### 의존성

- `.agents/oma-config.yaml`, `.codex/agents/*.toml`, `.gemini/agents/*.md` 또는 fallback `oma agent:spawn`
- memory provider config, subagent prompt template, script, task template, verify script, session metric

### 제어 흐름 특성

- vendor/native dispatch 가능성, priority tier, agent 완료/실패, verification 상태, QA verdict, retry limit, clarification debt에 따라 분기합니다.
- process/agent를 spawn하고 memory/result file을 읽고 씁니다.
- persistent workflow가 완료될 때까지 종료를 막습니다.

## 구조적 흐름

### 진입

1. agent vendor routing과 runtime dispatch path를 해석합니다.
2. 요청을 priority tier task로 분해합니다.
3. task마다 설치된 `.agents/skills/oma-*/SKILL.md`의 `Intent signature`와 대조해 하나 이상의 `domain_tags`로 분류합니다. 자신 있게 맞는 domain이 없으면 parent feature tag들의 합집합을 물려받습니다.
4. task별 `exposed_skill_set`은 `domain_tags`에 든 skill들입니다. 분류 후 `|exposed_skill_set| < 2`이면 전체 설치 skill(flat exposure)로 fallback하고 task board에 `exposure_fallback: true`를 기록합니다.
5. task별 `exposed_skill_set` 및 `exposure_fallback`을 포함한 session memory와 task board를 만듭니다.

### 장면(Scenes)

1. **PREPARE:** 계획, session ID 설정, memory file 초기화.
2. **ACT:** parallelism limit 안에서 priority tier별 agent spawn.
3. **VERIFY:** self-check, `oma verify`, QA cross-review loop 실행.
4. **RECOVER:** limit가 허용되면 review history와 함께 실패 agent retry.
5. **FINALIZE:** result file 수집, summary 컴파일, progress file 정리.

### 전이

- 현재 runtime/vendor에서 native dispatch가 가능하면 그것을 씁니다.
- vendor가 다르거나 native path가 없으면 fallback spawn을 씁니다.
- verify 또는 QA가 실패하면 feedback을 implementation agent에게 돌려보냅니다.
- review loop limit을 넘으면 review history와 quality warning을 보고합니다.
- recovery failure가 필요한 skill이 좁은 `exposed_skill_set`에서 빠졌음을 보이면, 원래 좁은 set으로 retry하지 않고 task를 재분류해 확장된 set으로 re-dispatch합니다.

### 실패와 복구

- 실패 agent를 configured limit까지 retry합니다.
- review loop가 소진되면 review history와 함께 re-spawn합니다.
- clarification debt threshold를 넘으면 pause하거나 재명세를 요청합니다.

### 종료

- 성공: 모든 task가 완료되고 verify/review가 통과하며 결과가 요약됩니다.
- 부분 성공: 실패 agent, 소진된 review loop, clarification debt를 명시합니다.

## 논리 작업

| 작업 | SSL primitive | 증거 |
|---|---|---|
| config/task context 읽기 | `READ` | oma config, routing, request |
| domain tag로 task 분류 | `INFER` | task text 대 skill `Intent signature` |
| exposed skill set 계산 | `SELECT` | domain tag와 installed skill의 교집합 |
| dispatch path 선택 | `SELECT` | native 대 fallback |
| session state 쓰기 | `WRITE` | task board와 memory file |
| agent spawn | `CALL_TOOL` | native CLI 또는 `oma agent:spawn` |
| progress poll | `READ` | progress/result file |
| verification 실행 | `CALL_TOOL` | `oma verify`, test, QA |
| retry state 갱신 | `UPDATE_STATE` | loop counter와 CD metric |
| final result 보고 | `NOTIFY` | compiled summary |

### 도구와 수단

- native CLI subagent dispatch, fallback spawn script, memory tool, verify script, QA agent
- session metric, prompt template, task template

### canonical command path

```bash
oma agent:spawn <agent-type> "<task>" <session-id> -w <workspace>
oma verify <agent-type> --workspace <workspace> --json
```

native runtime dispatch가 가능하면 fallback `oma agent:spawn` 전에 이 skill에 적힌 runtime-specific native path를 우선합니다.

### resource scope

| 범위 | resource target |
|---|---|
| `LOCAL_FS` | session, task-board, progress, result, config file |
| `PROCESS` | agent CLI process 및 verify script |
| `MEMORY` | session state 및 clarification debt |
| `CODEBASE` | spawned agent가 소유한 workspace |

### 사전조건

- task가 specialist agent work로 분해 가능해야 합니다.
- runtime/vendor dispatch path 또는 fallback이 있어야 합니다.

### effect와 side effect

- agent를 spawn하고 session/progress/result artifact를 씁니다.
- specialist agent를 통해 code change를 일으킬 수 있습니다.
- iterative review와 retry를 유발할 수 있습니다.

### guardrail

1. agent를 spawn하기 전에 project configuration에서 per-agent dispatch를 orchestration합니다.
2. `target_vendor === current_runtime_vendor`이고 runtime에 검증된 native path가 있으면 native dispatch를 씁니다.
3. 그렇지 않으면 `oma agent:spawn` fallback을 씁니다.
4. configured parallelism 또는 retry limit을 넘지 않습니다.
5. session/task-board/progress/result state가 실행 내내 맞물리도록 유지합니다.
6. domain gate는 soft해야 합니다. 좁은 `exposed_skill_set`을 우선하되 confidence가 낮으면 필요한 specialist를 굶기지 않도록 flat exposure로 fallback합니다.

현재 native executor path:

- Claude Code: `.claude/agents/{agent}.md` 정의의 Agent tool. 한 message의 여러 Agent call은 병렬이며 결과는 동기적으로 돌아와 polling하지 않습니다.
- OpenCode: `subagent_type: {agent-id}`의 native `task` tool. 같은 session OpenCode 작업에 `oma agent:spawn`을 쓰면 native child task로 보이지 않으므로 쓰지 않습니다.
- Codex CLI: `.codex/agents/*.toml`을 쓰는 `codex exec "@agent ..."`.
- Gemini CLI: `.gemini/agents/*.md`를 쓰는 `gemini -p "@agent ..."`.

fallback CLI run에는 vendor-specific execution protocol이 자동으로 주입됩니다.

### 설정

| 설정 | 기본값 | 설명 |
|---|---:|---|
| MAX_PARALLEL | 3 | 동시 subagent 최대 수 |
| MAX_RETRIES | 2 | 실패 task별 retry 시도 수 |
| POLL_INTERVAL | 30s | 상태 확인 간격 |
| MAX_TURNS (impl) | 20 | backend/frontend/mobile turn limit |
| MAX_TURNS (review) | 15 | qa/debug turn limit |
| MAX_TURNS (plan) | 10 | pm turn limit |

이 값들은 orchestrating agent가 적용하는 skill-level default이며, `config/cli-config.yaml`에서 읽지 않습니다. 후자는 `results_dir`, `timeout` 같은 vendor CLI/execution setting만 가집니다.

### memory configuration

memory provider와 tool name은 repository root `.mcp.json`(Claude Code MCP server config)이 아닌 `.agents/mcp.json`에서 설정합니다.

```json
{
  "memoryConfig": {
    "provider": "file",
    "basePath": ".agents/state/memories",
    "tools": { "read": "Read", "write": "Write", "edit": "Edit" }
  }
}
```

### workflow phase

**PHASE 1 - Plan:** request 분석 → task 분해 → session ID 생성  
**PHASE 1.5 - Domain gate:** installed skill의 `Intent signature` match 교집합으로 task별 `exposed_skill_set`을 만들고, 너무 작아 flat library를 쓰면 `exposure_fallback: true` 기록  
**PHASE 2 - Setup:** memory write tool로 `orchestrator-session.md`와 `task-board.md` 생성(각 task의 `exposed_skill_set` 포함)  
**PHASE 3 - Execute:** priority tier로 spawn(MAX_PARALLEL 초과 금지); 각 subagent에는 `exposed_skill_set`만 주입  
**PHASE 4 - Monitor:** `POLL_INTERVAL`마다 poll하며 complete/fail/crash 처리  
**PHASE 4.5 - Verify:** 완료 agent마다 mechanical check. `backend`, `frontend`, `mobile`, `qa`, `debug`, `pm`에만 `oma verify` 후 모든 implementation에 QA cross-review  
**PHASE 5 - Collect:** 모든 `result-{agent}-{sessionId}.md`를 읽어 summary를 만들고 progress file 정리

prompt construction은 `resources/subagent-prompt-template.md`, memory format은 `resources/memory-schema.md`를 봅니다.

### memory file ownership

| 파일 | 소유자 | 다른 주체 |
|---|---|---|
| `orchestrator-session.md` | orchestrator | read-only |
| `task-board.md` | orchestrator | read-only |
| `progress-{agent}[-{sessionId}].md` | 해당 agent | orchestrator가 읽음 |
| `result-{agent}[-{sessionId}].md` | 해당 agent | orchestrator가 읽음 |

## Agent-to-Agent Review Loop(PHASE 4.5)

각 agent가 끝난 뒤 single-pass verification이 아니라 iterative review loop에 들어갑니다.

```
Agent completes work
    ↓
[1] Mechanical Self-Check: lint, type-check, tests, diff scope
    ↓
[2] Verify: 지원 유형이면 `oma verify {agent-type} --workspace {workspace}`
    지원하지 않는 `db`, `refactor`, `architecture`, `tf-infra`, `docs`는 SKIP을 기록하고 계속
    ↓ FAIL → feedback을 받은 agent가 수정하고 [1]로
    ↓ PASS
[3] Cross-Review: QA agent가 변경을 review
    ↓ FAIL → feedback을 받은 agent가 수정하고 [1]로
    ↓ PASS
Accept result
```

### 상세 단계

**[1] Mechanical Self-Check**(기존 “Self-Review”): implementation agent는 외부 review 전 workspace의 lint/type-check/test를 실행하고, planned file만 바뀌었는지 diff scope를 확인하며, compile/test failure를 고칩니다. 이 단계는 quality judgment를 하지 않습니다. design quality, architecture alignment, acceptance criteria 충족 여부는 [3] QA cross-review만 평가합니다. source는 self-evaluation bias를 그 이유로 듭니다.

**[2] Automated Verify:**

```bash
oma verify {agent-type} --workspace {workspace} --json
```

- `backend`, `frontend`, `mobile`, `qa`, `debug`, `pm`에만 실행합니다.
- `db`, `refactor`, `architecture`, `tf-infra`, `docs`는 automated verify가 지원되지 않음을 기록하고 mechanical check 뒤 QA cross-review로 갑니다.
- PASS(exit 0)는 cross-review로, FAIL(exit 1)는 correction context로 agent에게 전달합니다.

**[3] Cross-Review:** QA agent가 diff를 읽고 check를 실행하며 acceptance criteria를 평가합니다. `docs/CODE-REVIEW.md`가 있으면 checklist로 씁니다. QA는 PASS(선택적으로 nit) 또는 specific issue가 있는 FAIL을 내고, FAIL issue는 implementation agent 수정으로 되돌아갑니다.

### loop limit

| counter | 최대 | 초과 시 |
|---|---:|---|
| self-check + fix cycle | 3 | cross-review로 escalation |
| cross-review rejection | 2 | review history와 함께 user에게 보고 |
| total loop iteration | 5 | quality warning과 force-complete |

review feedback에는 iteration/max, reviewer, FAIL verdict, file/line을 포함한 issue, fix instruction을 넣습니다. human review는 lint error를 잡는 단계가 아니라 final approval에 둡니다.

### retry logic

retry 전에 둘 중 먼저 발생한 종료 조건을 확인합니다.

1. agent retry count가 MAX_RETRIES에 도달하면 새 cycle을 시작하지 않습니다.
2. quota cap이 있으면 `checkCap(sessionId, cap)`을 호출합니다. `exceeded === true`이면 partial result를 저장하고 quota 조기 종료를 보고하며, 다음 retry나 tier의 남은 agent를 spawn하지 않습니다.

둘 다 아니면 1차 retry에는 전체 review history를, 2차 retry에는 “다른 접근을 시도하라”와 history를 넣어 re-spawn합니다. MAX_RETRIES 뒤(cost cap 미초과)에는 2~3개 alternative hypothesis를 별도 workspace에서 병렬 spawn하고 quality score가 있으면 최고 점수를 보존하며 experiment ledger에 기록합니다. 최종 실패는 완전한 review trail과 함께 user에게 continue/abort를 묻습니다.

### clarification debt(CD)

user feedback을 `clarify`(+10), `correct`(+25), `redo`(+40)으로 기록합니다. CD ≥ 50이면 QA가 `lessons-learned.md`에 RCA를 추가하고, CD ≥ 80이면 user에게 requirements re-specification을 요청하며, `redo`가 2회 이상이면 계속하기 전 explicit allowlist confirmation을 요청합니다. session 종료 시 CD ≥ 50이면 final report에 CD summary를 넣고 QA RCA와 prevention measure update를 실행합니다.

## 참고

- Prompt template: `resources/subagent-prompt-template.md`
- Memory schema: `resources/memory-schema.md`
- Config: `config/cli-config.yaml`
- Scripts: `scripts/spawn-agent.sh`, `scripts/parallel-run.sh`, `scripts/verify.sh`
- Task templates: `templates/`
- Skill-to-agent mapping: `../_shared/core/skill-routing.md`
- Verification: `scripts/verify.sh <agent-type>`
- Session metrics: `../_shared/core/session-metrics.md`
- API contract template(SSOT): `../_shared/core/api-contracts/template.md`; generated contract는 `.agents/results/api-contracts/`(run artifact) 또는 `docs/plans/contracts/`(durable spec)에서 읽습니다.
- Context loading/difficulty/clarification/context budget/lessons learned resource도 이 skill이 참조합니다.

원문: `.agents/skills/oma-orchestration/SKILL.md` [E17]
