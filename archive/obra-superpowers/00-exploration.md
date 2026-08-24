# 탐색 기록

## 범위와 고정점

분석 대상은 `obra/superpowers`의 기본 브랜치 `main`을 2026-08-24에 `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`로 고정한 상태다. 재귀 Git tree는 blob 195개이며, 전체 clone 없이 경로 목록부터 선별했다. [E01](06-source-evidence.md#e01) [E02](06-source-evidence.md#e02)

## 실제로 연 파일과 선정 이유

| 범주 | 연 파일 | 선정 이유 | 확인한 사실 |
|---|---|---|---|
| 제품 설명·운영 문서 | `README.md`, `AGENTS.md`, `docs/testing.md` | 사용자 흐름, 기여·승인 경계, 테스트 범위를 함께 확인 | skill 기반 방법론, 설치별 차이, 별도 eval/플러그인 테스트 구분 [E03](06-source-evidence.md#e03) [E04](06-source-evidence.md#e04) [E24](06-source-evidence.md#e24) |
| 공통 설치 계약 | `package.json`, `.codex-plugin/plugin.json`, `.kimi-plugin/plugin.json`, `gemini-extension.json` | 어떤 harness가 skill을 발견하고 bootstrap하는지 확인 | OpenCode main, Pi extension·skill 경로, Codex skills + 빈 hooks, Kimi sessionStart, Gemini context file [E05](06-source-evidence.md#e05) [E06](06-source-evidence.md#e06) [E07](06-source-evidence.md#e07) |
| hook 기반 adapter | `hooks/hooks.json`, `hooks/hooks-cursor.json`, `hooks/session-start`, `hooks/run-hook.cmd` | Claude/Cursor/Copilot의 세션 시작 주입 경로 및 플랫폼 분기를 확인 | `using-superpowers` 본문을 JSON context로 만들고 소비 플랫폼별 필드 하나만 출력 [E08](06-source-evidence.md#e08) [E09](06-source-evidence.md#e09) |
| in-process adapter | `.opencode/plugins/superpowers.js`, `.pi/extensions/superpowers.ts`, `.hermes-plugin/__init__.py` | 매니페스트가 가리키는 실제 실행 코드 | skill directory 등록, 첫 사용자 문맥에 bootstrap 삽입, 중복 방지/compaction 처리 [E10](06-source-evidence.md#e10) [E11](06-source-evidence.md#e11) [E12](06-source-evidence.md#e12) |
| workflow skill | `skills/using-superpowers/SKILL.md`, `brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development` | 입력 계약·승인·계획·하위 작업자·재시도 규칙을 확인 | 현행 방법론의 중심 흐름과 ledger/review loop 계약 [E13](06-source-evidence.md#e13)~[E17](06-source-evidence.md#e17) |
| 안전·품질 skill | `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `using-git-worktrees`, `finishing-a-development-branch` | 변경·완료·통합에서 무엇을 막는지 확인 | TDD, 근본 원인 조사, 신선한 검증, worktree 격리, merge/push/discard 승인 [E18](06-source-evidence.md#e18)~[E21](06-source-evidence.md#e21) |
| 선택적 visual companion | `skills/brainstorming/scripts/{start-server.sh,stop-server.sh,server.cjs,helper.js}` | 이 저장소의 실제 런타임 코드·파일/네트워크 경계를 확인 | 토큰 인증 HTTP/WS, local content/state, idle 종료, browser open opt-in [E25](06-source-evidence.md#e25)~[E29](06-source-evidence.md#e29) |
| 검증 | `tests/brainstorm-server/*`, `tests/hooks/test-session-start.sh`, harness별 test script | README 주장 대신 무엇을 테스트하려는지 확인 | brainstorm Node suite, hook JSON shape, 일부 harness wiring/행동 테스트 [E23](06-source-evidence.md#e23) [E30](06-source-evidence.md#e30) |

## 실제 진입점과 기술 스택

1. **대부분의 harness**: plugin manifest가 `skills/`를 노출하고, 시작 시 `using-superpowers`를 model context에 넣거나 native skill discovery에 기대는 구조다. 즉 이 프로젝트의 중심 산출물은 서버가 아니라 Markdown skill instruction 집합이다. [E05](06-source-evidence.md#e05) [E06](06-source-evidence.md#e06) [E13](06-source-evidence.md#e13)
2. **OpenCode**: root `package.json`의 `main`이 `.opencode/plugins/superpowers.js`를 가리킨다. 이 모듈은 config hook에서 skill path를 추가하고 첫 사용자 message 앞에 bootstrap을 넣는다. [E05](06-source-evidence.md#e05) [E10](06-source-evidence.md#e10)
3. **Pi/Hermes**: 각각 TypeScript/Python extension이 skill을 등록하고 첫 turn 또는 context에 bootstrap을 넣는다. [E11](06-source-evidence.md#e11) [E12](06-source-evidence.md#e12)
4. **Claude/Cursor/Copilot**: shell hook이 `using-superpowers/SKILL.md`를 읽어 platform별 JSON context shape로 출력한다. Windows에서는 polyglot wrapper가 bash를 찾는다. [E08](06-source-evidence.md#e08) [E09](06-source-evidence.md#e09)
5. **Visual companion**: Node built-in `http`, `fs`, `crypto`와 자체 WebSocket frame 구현을 사용한다. test package의 `ws`는 테스트 의존성이다. [E25](06-source-evidence.md#e25) [E23](06-source-evidence.md#e23)

## 확인된 핵심 흐름

`세션 시작/첫 문맥 → using-superpowers → 관련 skill 선택 → brainstorming의 승인 gate → (필요 시) plan → isolated worktree → TDD·구현·review → fresh verification → 사람이 merge/PR/보존을 선택`이 문서상 중심 흐름이다. 이 흐름의 실행 주체는 설치된 coding-agent harness이고, Superpowers 자체는 이를 유도하는 skill text와 adapter를 제공한다. [E03](06-source-evidence.md#e03) [E13](06-source-evidence.md#e13)~[E21](06-source-evidence.md#e21)

## 코드/문서 교차 확인 결과

- README는 Codex plugin을 통해 skills를 제공한다고 말하고, Codex manifest도 `skills: "./skills/"`와 `hooks: {}`를 선언한다. 이 SHA에서 Codex는 Claude-style `hooks/hooks.json`을 사용하도록 구성된 것이 아니라 native skill discovery를 쓰는 것으로 해석하는 편이 코드와 일치한다. [E03](06-source-evidence.md#e03) [E06](06-source-evidence.md#e06)
- README는 visual companion의 logo 요청에 version만 포함되고 프로젝트/프롬프트는 포함하지 않는다고 설명한다. 서버는 원격 brand image URL을 쓰며 telemetry disable 환경변수를 검사한다. 단, 실제 네트워크 요청 payload는 실행하지 않았으므로 README의 전체 privacy 주장은 **부분 확인**이다. [E03](06-source-evidence.md#e03) [E25](06-source-evidence.md#e25)
- 현행 SDD skill은 implementer에게 전체 plan을 다시 읽히지 않고 plan-scoped task brief file을 전달하라고 한다. 반면 한 Claude Code test에는 "직접/full task text"를 기대하는 문구가 있어, 현재 source만 보면 진화 과정에서 테스트 문구가 뒤처졌을 가능성이 있다. 이 테스트를 실행하지 않았으므로 통과/실패는 **미확인**이다. [E16](06-source-evidence.md#e16) [E30](06-source-evidence.md#e30)

## 미확인 범위

- 실제 marketplace 설치, external fork sync, 지원 harness별 session bootstrap, LLM이 skills를 자동 호출하는 행동, CI와 외부 `evals/` 결과는 실행하지 않았다.
- source tree에서 API key/secret 값을 찾거나 읽지 않았으며, local visual server의 원격 bind 운영·방화벽 설정도 평가하지 않았다.
