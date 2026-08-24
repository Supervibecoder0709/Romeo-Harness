# PM/Harness 운영 메모

## 결론과 추천

**추천: 이 저장소를 "자동 개발 시스템"으로 한 번에 도입하지 말고, 먼저 현재 harness에서 `using-superpowers → brainstorming → writing-plans → verification-before-completion` 네 가지를 작은 비위험 기능 하나에 적용한 뒤, 부트스트랩·승인 기록·fresh test evidence가 실제로 남는 것을 확인하고 SDD를 추가하세요.**

이유는 Superpowers의 핵심 가치가 코드 생성기가 아니라 **agent의 행동 순서와 검증 규율**이기 때문입니다. 설치만으로는 효과가 보장되지 않고, harness마다 bootstrap 방식도 달라서 실제 첫 세션에서 `brainstorming`이 코드 작성 전에 자동으로 선택되는지 확인해야 합니다. [E03](06-source-evidence.md#e03) [E06](06-source-evidence.md#e06) [E13](06-source-evidence.md#e13)

비용은 별도 런타임 사용료보다 planning/review subagent와 real-session eval의 토큰·시간에 주로 생깁니다. SDD도 역할에 따라 가장 낮은 충분 모델을 쓰되, 여러 turn을 쓰는 저가 모델이 총비용을 키울 수 있다고 명시합니다. 운영상으로는 ledger·brief·review package를 artifact로 남기는 장점이 있고, 보안상으로는 merge/push/PR/삭제를 사람 승인 지점으로 유지해야 합니다. [E16](06-source-evidence.md#e16) [E17](06-source-evidence.md#e17) [E21](06-source-evidence.md#e21)

## 확인된 사실

### 1) 실제 제품 경계

- Superpowers는 `skills/`의 Markdown instructions와 harness별 plugin/hook adapter다. 사용자 프로젝트의 상태를 중앙에서 기록하거나 배포하는 서비스는 이 source에서 확인되지 않는다. [E05](06-source-evidence.md#e05) [E10](06-source-evidence.md#e10)
- 그러므로 "skill 파일이 설치돼 있다"와 "현재 세션에서 skill이 자동 호출됐다"는 다른 주장이다. 전자는 manifest/file로, 후자는 실제 clean-session transcript나 behavior eval로 검증해야 한다. AGENTS는 새 harness의 최소 acceptance test로 깨끗한 세션에서 `Let's make a react todo list`를 보내 코드 전에 `brainstorming`이 자동 실행되는 transcript를 요구한다. [E04](06-source-evidence.md#e04)
- 이 고정 SHA에서 Codex manifest는 `skills: "./skills/"`와 빈 `hooks: {}`를 갖는다. 따라서 Codex에서 Claude용 session-start hook이 주입될 것이라고 가정하면 안 된다. native skill discovery가 실제로 동작하는지는 이 분석에서 미검증이다. [E06](06-source-evidence.md#e06)

### 2) 승인 지점은 기능이 아니라 운영 계약

| 시점 | source가 요구하는 사람 개입 | PM이 남겨야 할 증거 |
|---|---|---|
| 아이디어→구현 | brainstorming이 설계 제시 후 명시적 승인 대기 | 승인된 설계 메시지 또는 spec revision [E14](06-source-evidence.md#e14) |
| 새 worktree | 이미 선호가 없으면 격리 workspace 생성 동의 | 위치·branch·baseline test output [E20](06-source-evidence.md#e20) |
| plan 실행 중 | 보통 지속 실행하되 irreversible/destructive·security-sensitive·worktree 밖 side effect·완전히 추측뿐인 plan에서는 중지 | blocker 또는 ruling ledger [E16](06-source-evidence.md#e16) |
| merge/push/PR | integration option을 사람이 선택 | 선택 기록과 실제 remote/PR URL [E21](06-source-evidence.md#e21) |
| discard | permanent delete 대상 공개 후 정확히 `discard`를 입력 | 대상 branch/commits/worktree와 typed confirmation [E21](06-source-evidence.md#e21) |

### 3) 재실행·복구 단위

- SDD의 durable record는 Git commit과 plan-scoped ledger다. context compaction 뒤에는 기억보다 ledger와 `git log`를 신뢰하라고 적혀 있다. 다만 `.superpowers/sdd/...`는 git-ignored scratch라 `git clean -fdx` 후에는 commits만 남는다. 이 점은 운영 runbook에 반드시 포함해야 한다. [E16](06-source-evidence.md#e16)
- `NEEDS_CONTEXT`/`BLOCKED`는 같은 prompt를 반복할 신호가 아니라 context 추가, 모델 상향, task 분할, plan ruling 중 하나를 바꾼 뒤 재시도하라는 분기다. [E17](06-source-evidence.md#e17)
- visual companion은 별도의 선택 기능이다. `--open`은 사용자가 visual companion을 승인한 뒤에만 쓰라고 되어 있고, session key가 URL/state files에 들어갈 수 있어 session directory 접근 권한이 중요하다. [E14](06-source-evidence.md#e14) [E25](06-source-evidence.md#e25) [E27](06-source-evidence.md#e27)

## 추천 운영 설계

### 권장 단계 1 — "행동 계약"의 작은 검증

기존의 낮은 위험 기능 하나를 골라, 새 clean session에서 아래 세 가지를 관찰하세요.

1. 코드 탐색/작성 전에 `brainstorming`이 선택되고, 짧은 설계와 승인 대기가 생기는가.
2. plan에는 정확한 파일·test command·기대 결과가 있고, 구현 뒤에 fresh command output이 있는가.
3. 완료 보고가 "agent가 끝냈다"가 아니라 diff, test result, merge/PR readback을 구별하는가.

이 단계는 추가 인프라 없이 현재 harness/저장소 안에서 되돌릴 수 있고, 도입이 유효한지 가장 빨리 검증한다. [E14](06-source-evidence.md#e14) [E15](06-source-evidence.md#e15) [E19](06-source-evidence.md#e19)

### 권장 단계 2 — SDD는 계획 품질이 확보된 뒤

SDD의 강점은 한 task마다 implementer와 독립 reviewer를 분리하고 artifact file로 handoff하는 데 있다. 반대로 spec과 plan이 빈약하면 subagent 수만 늘린다. 따라서 task가 2~5분짜리 검증 단위로 분해되고, 각 task가 소비/생산 interface를 밝혔을 때 도입하는 것이 적합하다. [E15](06-source-evidence.md#e15) [E16](06-source-evidence.md#e16)

모델 배정은 "기계적인 1~2 파일 구현은 빠른/저가, integration·debugging은 표준, architecture·final review는 최고 판단력"이라는 source의 역할 기반 기준을 따르되, 실제 조직의 품질/비용 data로 보정해야 한다. 이는 **추천**이며, 특정 provider/model 이름이나 비용 효과는 이 source만으로 검증되지 않는다. [E16](06-source-evidence.md#e16)

### 권장 단계 3 — visual companion은 별도 보안 검토 후 opt-in

서버는 기본 loopback, per-session token, constant-time comparison, HttpOnly/SameSite cookie, same-origin WS 검사를 구현하고 테스트한다. 그러나 `--host 0.0.0.0`는 remote/container 환경의 선택지이며, 네트워크 접근 범위와 session state file 보호는 배포 환경에 따라 달라진다. 내부 사용에 필요할 때만 enable하고, remote bind에는 네트워크 경계·로그 보관·browser launcher를 별도 검토하세요. [E25](06-source-evidence.md#e25) [E26](06-source-evidence.md#e26) [E23](06-source-evidence.md#e23)

## 운영 대시보드에 넣을 최소 관찰 항목

| 질문 | 관찰 가능한 답 |
|---|---|
| bootstrap이 실제로 살아 있는가? | clean-session transcript에서 skill 선택과 코드 전 brainstorming |
| 어떤 상태의 작업인가? | spec 승인 / plan 작성 / task N implement / review loop / final review / integration choice |
| 검증은 신선한가? | command, timestamp, exit code, pass/fail count, 어떤 tree/commit인지 |
| 사람의 결정을 agent가 대신하지 않았는가? | merge/push/PR/discard 전 approval event와 실제 readback |
| 재개할 수 있는가? | plan-scoped ledger path, task brief/report/review package, commit SHA |
| visual state가 노출되지 않는가? | bind host, token file permission, server stopped event, session directory retention |

## 미확인 또는 조건부 사항

- 이 source tree만으로 현재 marketplace 설치 상태, native skill auto-trigger, provider별 model quality/cost, PR rejection rate 숫자, external `superpowers-evals` pass rate는 확정할 수 없다.
- source에 GitHub Actions workflow가 없다는 것은 이 SHA의 workflow path가 없다는 뜻일 뿐, maintainer가 다른 CI를 쓰지 않는다는 증명은 아니다. [E02](06-source-evidence.md#e02)
- 이 아카이브는 `tests/`를 읽었지만 test command를 실행하지 않았다. 따라서 테스트 존재는 확인됐고 **현재 green 상태는 미확인**이다. [E23](06-source-evidence.md#e23) [E24](06-source-evidence.md#e24)
