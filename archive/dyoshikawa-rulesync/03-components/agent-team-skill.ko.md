---
name: agent-team
description: >-
  Implementer와 Reviewer 서브에이전트의 Agent Team을 구성해 주어진 작업을 처리하고,
  Reviewer가 high 이상 0건 및 mid 3건 이하를 보고할 때까지 구현과 검토를 반복한다.
targets:
  - claudecode
---

# Agent Team

TASK = 사용자 요청

TASK가 제공되지 않으면 사용자에게 작업 설명을 요청하고 중단한다.

Implementer Agent와 Reviewer Agent로 구성된 Agent Team을 조정한다. 종료 조건이 충족될 때까지 구현/검토 loop를 반복한다.

## 0. 종료 조건

한 번의 검토 라운드에서 다음 둘을 모두 만족하면 loop를 종료한다.

- severity `high` 또는 `critical` finding **0**건.
- severity `mid` finding **3건 이하**.

severity `low` finding은 종료 조건에 영향을 주지 않는다.

최대 **10회 반복**이라는 강제 안전 상한을 둔다. 상한까지도 종료 조건을 만족하지 않으면 loop를 멈추고 남은 finding을 사용자에게 보고해 수동 결정을 받는다.

## 1. 반복 loop

종료 조건을 만족할 때까지 다음 단계를 반복한다.

### 1-1. 구현 단계

Agent 도구를 통해 Implementer Agent에게 위임한다.

- `subagent_type`: `general-purpose`
- 역할 지정: "You are the Implementer Agent on an Agent Team."
- 전달 입력:
  - 원래 TASK.
  - 이전 라운드의 모든 Reviewer finding(있다면), severity별 그룹화.
- prompt에 포함할 지시:
  - 현재 저장소에서 TASK를 end-to-end로 구현한다.
  - 이전 Reviewer finding을 모두 처리한다. 각 finding을 수정하거나, 의도적으로 거부하면 이유를 기록한다.
  - 설명만 하지 말고 파일을 직접 수정한다.
  - `pnpm cicheck`(또는 적절할 때 더 좁은 `pnpm cicheck:code` / `cicheck:content`)을 실행하고 실패를 고친 뒤 반환한다.
  - 변경의 간결한 요약, 수정 파일 목록, 이전 finding 처리 방법, check 결과를 보고한다.

### 1-2. 검토 단계

Agent 도구를 통해 Reviewer Agent에게 위임한다.

- `subagent_type`: `code-reviewer`
- 역할 지정: "You are the Reviewer Agent on an Agent Team."
- 전달 입력:
  - 원래 TASK.
  - 이번 라운드 Implementer의 요약과 수정 파일 목록.
- prompt에 포함할 지시:
  - 정확성, 설계 품질, 테스트, 프로젝트 규약 준수(`CLAUDE.md`, `docs/**/*.md`, `.claude/rules/feature-change-guidelines.md`)를 검토한다.
  - 보안 우려도 검토한다.
  - finding 목록을 만든다. 각 finding은 순번, `low`/`mid`/`high`/`critical` severity, 파일 경로·줄 번호, 문제 설명과 추천 수정을 포함한다.
  - 보고서 끝에 severity별 개수를 담은 **Severity Summary**를 넣어 종료 조건을 기계적으로 평가할 수 있게 한다.

### 1-3. 종료 조건 평가

Reviewer의 Severity Summary를 해석한다.

- `high + critical == 0` **그리고** `mid <= 3`이면 loop를 종료한다.
- 그렇지 않으면 finding을 다음 구현 단계로 전달하고 계속한다.

반복 사이에 `Iteration N complete — high/critical: X, mid: Y, low: Z` 같은 짧은 상태 줄을 사용자에게 출력한다.

## 2. 최종 보고

loop가 종료되면 사용자에게 다음을 보고한다.

- **Outcome**: `Converged`(종료 조건 만족) 또는 `Capped`(반복 상한 도달).
- **Iterations**: 실행한 라운드 수.
- **Remaining findings**: 최종 Severity Summary, 그리고 남은 `mid`/`low` finding 전문(상한 때문에 남은 `high`/`critical`도 포함).
- **Changes**: 구현한 내용과 수정 파일의 짧은 요약.
- **Next steps**: 사용자 제안(예: `commit-push-pr` 스킬로 commit/PR 만들기).

이 스킬이 자동으로 commit하거나 PR을 열지 않는다. 그 결정은 사용자에게 남긴다.

> 번역 원문: `.rulesync/skills/agent-team/SKILL.md` at `c3acceacec5463efe14ebb1b8be5fed5fa835e65`. [S20]
