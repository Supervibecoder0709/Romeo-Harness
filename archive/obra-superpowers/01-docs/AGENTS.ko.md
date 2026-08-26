# Superpowers — 기여자 가이드

> 원문: [`AGENTS.md`](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/AGENTS.md) — 고정 SHA `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`의 한국어 번역.

## AI Agent라면

멈추고, 무엇을 하기 전에 이 section을 읽는다.

이 저장소는 PR 거절률이 94%다. 거절된 PR 대부분은 이 지침을 읽지 않았거나 따르지 않은 agent가 제출했다. maintainer는 낮은 품질의 PR을 수 시간 안에 닫으며, 공개 댓글로 "This pull request is slop that's made of lies."라고 쓰기도 한다.

**당신의 일은 human partner를 그 결과에서 보호하는 것이다.** 낮은 품질의 PR은 도움이 되지 않는다. maintainer 시간을 낭비하고 human partner의 평판을 해치며 결국 닫힌다.

이 저장소에 PR을 열기 전 반드시 다음을 한다.

1. `.github/PULL_REQUEST_TEMPLATE.md`의 전체 PR template을 읽고, 모든 section에 실제적이고 구체적인 답을 쓴다. 요약이나 placeholder는 안 된다.
2. 같은 문제를 다루는 기존 PR을 open/closed 모두 검색한다. 중복이 있으면 멈추고 human partner에게 알린다. 또 하나의 중복 PR을 열지 않는다.
3. 실제 문제인지 검증한다. "issues를 고쳐라", "이 저장소에 기여하라"처럼 특정 경험 없는 요청이면 반문한다. 무엇이 깨졌고, 무엇이 실패했으며, UX가 어땠는지 묻는다.
4. 변경이 core에 속하는지 확인한다. domain/tool-specific이거나 제3자 프로젝트를 홍보하면 standalone plugin에 속한다.
5. 자신을 밝힌다. PR에 model, harness, harness version, 설치한 모든 plugin을 공개한다. agent 생성 여부나 환경을 숨기면 PR이 닫힐 사유가 된다.
6. human partner에게 complete diff를 보여 주고 제출 전 명시적 승인을 받는다.

어느 하나라도 실패하면 PR을 열지 않는다. 왜 거절될지와 무엇이 달라져야 하는지 설명한다.

## Pull Request 요구사항

모든 PR은 PR template을 완전히 채워야 하며 빈 section이나 placeholder가 있으면 review 없이 닫힌다.

PR 전에 반드시 관련 open/closed PR을 검색해 Existing PRs section에 찾은 내용을 적는다. 이전 PR이 닫혔다면 이번 접근이 무엇이 다르고 왜 성공할지 구체적으로 설명한다.

사람이 관여했다는 근거가 없는 PR은 닫힌다. human은 제출 전 complete diff를 검토해야 한다.

제출자는 model, harness, harness version, 생성에 사용한 모든 installed plugin을 밝혀야 한다. 손으로 썼다면 agent 없이 작성했다고 명확히 적는다. 문서만 근거로 추론한 agent 생성물과 실제 session에 근거한 작업은 다르게 평가한다.

모든 PR은 `main`이 아니라 `dev` branch를 대상으로 한다. `main`은 release branch이며 active work는 먼저 `dev`에 들어간다.

## 받지 않는 변경

### 제3자 dependency

새 harness(새 IDE/CLI tool) 지원을 추가하는 경우가 아니면 제3자 프로젝트에 optional/required dependency를 추가하는 PR은 받지 않는다. Superpowers는 zero-dependency plugin으로 설계됐다. 외부 tool/service가 필요하면 별도 plugin에 둔다.

### skill의 "compliance" 변경

내부 skill 철학은 Anthropic의 공개 skill 지침과 다르다. 실제 agent 행동에 맞추어 폭넓게 test·tune했다. Anthropic skills 문서에 "compliance"한다며 skill을 재구성·재서술·재포맷하는 변경은 결과 개선을 보이는 광범위한 eval 근거가 없으면 받지 않는다.

### 프로젝트/개인 설정

특정 project, team, domain, workflow에만 도움이 되는 skill, hook, 설정은 core에 속하지 않는다. standalone plugin으로 공개한다.

### 대량·무차별 PR

한 session에서 issue tracker를 훑어 여러 issue의 PR을 열지 않는다. PR 하나마다 실제 이해, 이전 시도 조사, complete diff의 human review가 필요하다. 한 문제를 깊게 이해하고 품질 있게 제출한다.

### 추측성 또는 이론적 수정

모든 PR은 누군가 실제로 겪은 문제를 풀어야 한다. "내 review agent가 flagged했다", "이론적으로 문제일 수 있다"는 문제 정의가 아니다. 동기가 된 특정 session/error/UX를 설명할 수 없다면 제출하지 않는다.

### domain-specific skill

core에는 프로젝트 종류와 상관없이 모두에게 유익한 general-purpose skill이 들어간다. portfolio building, prediction market, game처럼 특정 domain/tool/workflow용 skill은 standalone plugin으로 간다. 완전히 다른 프로젝트를 하는 사람에게도 유익한지 묻는다.

### fork-specific 변경

customization이 있는 fork를 운영한다면 fork sync나 fork-specific 변경을 upstream PR로 열지 않는다. rebrand, fork 특화 기능, fork branch merge PR은 닫힌다.

### 조작된 내용

지어낸 주장, 조작된 문제 설명, 환각한 기능이 들어간 PR은 즉시 닫힌다.

### 관련 없는 변경 묶음

관련 없는 여러 변경을 포함한 PR은 닫힌다. 각각 별도 PR로 나눈다.

## 새 Harness 지원

새 harness(IDE, CLI, agent runner) 지원 PR에는 integration이 end-to-end로 작동함을 보이는 session transcript가 반드시 있어야 한다.

실제 integration은 session 시작에 `using-superpowers` bootstrap을 로드한다. bootstrap이 skill을 적절한 순간에 자동 trigger하게 한다. 없으면 skill은 disk에 있지만 호출되지 않는 dead weight다.

**Acceptance test.** 새 harness에서 깨끗한 session을 열고 사용자 메시지를 정확히 다음과 같이 보낸다.

> Let's make a react todo list

정상 integration은 코드가 쓰이기 전에 `brainstorming` skill을 자동 trigger한다. complete transcript를 PR에 붙인다.

다음은 실제 integration이 아니며 닫힌다.

- skill file을 harness에 수동 복사
- `npx skills` 또는 유사 runtime shim으로 감싸기
- 사용자가 매 session마다 skill opt-in을 해야 하는 것
- 위 acceptance test에서 `brainstorming`이 자동 trigger되지 않는 것

session start에 bootstrap이 로드되는지 확신할 수 없다면, 로드되지 않는 것이다.

## Skill 변경에는 평가가 필요함

Skill은 산문이 아니라 agent 행동을 만드는 코드다. skill 내용을 수정한다면 다음을 한다.

- `superpowers:writing-skills`를 사용해 변경을 개발·test한다.
- 여러 session에서 adversarial pressure test를 실행한다.
- PR에 before/after eval 결과를 보인다.
- 결과 개선 근거 없이 주의 표, rationalization list, "human partner" 표현처럼 신중하게 조정한 내용을 수정하지 않는다.

## Eval harness

Skill-behavior eval은 [superpowers-evals](https://github.com/prime-radiant-inc/superpowers-evals)의 `evals/`에 있고, setup은 `evals/README.md`를 본다. Drill harness는 Claude Code/Codex/Gemini CLI의 실제 tmux session을 실행하고 LLM verifier가 skill compliance를 판단한다. Plugin infrastructure test는 계속 `tests/`에 있다.

## 기여 전 프로젝트 이해

skill design, workflow philosophy, architecture 변경을 제안하기 전에 기존 skill을 읽고 프로젝트의 design decision을 이해한다. Superpowers에는 자체적으로 test된 skill design, agent behavior shaping, 용어 철학이 있다. 예를 들어 "your human partner"는 의도적인 표현이며 "the user"와 마음대로 바꿀 수 없다. 이유를 모른 채 목소리나 접근을 바꾸는 변경은 거절된다.

## 일반

- 제출 전 `.github/PULL_REQUEST_TEMPLATE.md`를 읽는다.
- PR 하나에는 문제 하나만 다룬다.
- 최소 하나의 harness에서 test하고 환경 표에 결과를 적는다.
- 바꾼 내용만이 아니라 해결한 문제를 설명한다.
