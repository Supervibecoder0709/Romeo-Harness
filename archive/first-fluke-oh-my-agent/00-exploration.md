# 탐색 기록

## 고정한 범위

**확인된 사실.** 저장소 기본 브랜치는 `main`이고, 분석 기준 커밋은 `7a2b46ebe670b14be628210ea45fd3ccc24ab5ee`이다. 루트 workspace는 `cli`와 `web` 두 workspace를 선언하고, 루트 테스트·타입체크 명령은 실제로 `cli` 및 `web`의 명령을 호출한다. [E01][E02]

**확인된 사실.** GitHub tree API는 3,863개 항목을 `truncated: false`로 반환했다. 따라서 전체를 내려받거나 clone하지 않고, 실행 중심성과 외부 변경 권한을 기준으로 다음 후보만 열었다.

| 선정 묶음 | 실제로 연 파일 | 선정 이유 |
|---|---|---|
| 사용자 설명 | `README.md`, `docs/README.ko.md`, `action/README.md` | 목적, 설치 진입점, 지원 런타임 및 update Action의 권한 설명을 제공 |
| CLI 진입점·패키징 | `package.json`, `cli/package.json`, `cli/cli.ts` | 실제 바이너리·명령 등록·검증/대시보드 진입점을 확인 |
| 설치·런타임 투영 | `cli/commands/install/run.ts`, `cli/platform/agent-composer.ts`, `cli/platform/hooks-composer.ts`, `.agents/hooks/variants/{claude,codex}.json` | `.agents/` SSOT를 프로젝트/벤더별 파일로 쓰는 변경 경계와 hook 연결을 확인 |
| 검증·상태 | `.agents/hooks/core/persistent-mode.ts`, `cli/state/{artifact-verifier,decision-verifier,events}.ts`, `_shared/runtime/event-spec.md` | 완료를 말이 아닌 테스트/산출물/이벤트로 판정하는 핵심을 확인 |
| harness | `cli/commands/harness/{command,run,runner,overlay,provenance,records,scoring,types}.ts`, `run.test.ts` | 후보 overlay를 baseline과 비교하고 재현/차단하는 실행 계약을 확인 |
| 역할 정의 | `.agents/agents/{pm-planner,qa-reviewer,architecture-reviewer}.md`, `.agents/skills/oma-orchestration/SKILL.md` | PM·QA·아키텍처 역할의 입력/산출물/비수정 경계와 오케스트레이션 계약을 확인 |
| CI·배포 자동화 | `.github/workflows/test.yml`, `action/action.yml` | CI가 무엇을 보장하는지, Action이 어떤 쓰기 권한을 요구하는지 확인 |

## 기술 스택과 실제 진입점

- **실행 프로그램:** `oh-my-agent`와 `oma`는 모두 `cli/bin/cli.js`를 가리키며, 빌드는 Bun으로 `cli.ts`를 bundle한다. [E02]
- **명령 등록:** `cli/cli.ts`가 install을 먼저 등록하고, 일반 실행에서는 state·hook·agent·verify·harness 등을 동적으로 등록한다. `oma hook`은 사용자 프롬프트마다 실행될 수 있어 full command tree를 우회하는 fast path다. [E03]
- **상태 저장:** 세션별 append-only JSONL은 `.agents/state/sessions/{sid}/events.jsonl`이고, index/meta는 별도 JSON으로 원자적으로 쓴다. [E10][E12]
- **테스트:** Vitest가 CLI 테스트를 실행한다. CI는 3개 OS에서 lint/boundary/typecheck/build, Linux/macOS에서 full test, Windows에서 선별된 win32 path test와 설치 스모크를 선언한다. [E02][E20]

## 확인된 핵심 흐름

1. 사용자가 `oma install`을 실행하면 install root를 정하고, interactive global install은 Home 및 vendor 설정 변경 범위를 알린 뒤 동의를 받는다. 이후 SSOT·hooks·agents·workflows·rules·config와 선택된 skills를 설치하고 vendor adaptation/link를 수행한다. [E04]
2. vendor hook은 prompt/도구/stop 이벤트를 `keyword-detector`, `state-boundary`, `skill-injector`, `scm-guard`, `test-filter`, `refactor-guard`, `persistent-mode`에 연결한다. Codex variant도 같은 범주의 이벤트를 명시한다. [E05]
3. persistent workflow의 Stop 이벤트에서는 state file 및 예산을 읽고, `typecheck`·`test`·`lint`만 allowlist로 실행한다. 통과·실패는 event log에 기록되며, 게이트 실패는 최대 5회 강화 후 탈출 가능하다. [E06]
4. `oma harness eval`은 baseline과 별도 candidate overlay를 비교한다. live 실행은 비용 확인을 기본으로 하며, task마다 fresh temporary workspace 두 개를 만들고 protected harness가 변경되면 실패로 본다. 녹화는 suite/baseline/candidate hash가 일치해야 replay된다. [E07][E08][E09]

## 미확인 범위

- 실제 `oma install`, `oma update`, agent spawn, vendor native dispatch, Stop hook 호출, harness live run 및 GitHub Action 실행 결과는 관찰하지 않았다.
- “지원 런타임 전부에서 동일하게 동작”은 README의 제품 주장이고, 이 아카이브는 Claude/Codex variant와 composer 코드만 열어 일부 구현 근거를 확인했다. 다른 벤더별 실제 동작은 미확인이다.
- CI workflow는 열었지만, 이 fixed SHA에는 `test.yml` 실행 기록이 없었다. 따라서 코드 테스트가 이 SHA에서 통과했다고 결론 내리지 않는다. [E21]
