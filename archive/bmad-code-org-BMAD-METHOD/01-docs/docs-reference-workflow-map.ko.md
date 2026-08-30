---
title: "Workflow Map"
description: BMad Method workflow phase와 output의 시각적 reference
sidebar:
  order: 1
---

BMad Method(BMM)는 context engineering과 planning의 best practice를 따르기 위한 BMad Ecosystem module입니다. AI agent는 명확하고 구조화된 context에서 가장 잘 작동합니다. BMM system은 4개의 뚜렷한 phase를 거치며 context를 점진적으로 만듭니다. 각 phase와 그 안의 선택 workflow는 다음 단계를 알려 주는 document를 만들어 agent가 무엇을 왜 만들어야 하는지 알게 합니다.

그 근거와 개념은 업계에서 성공적으로 사용되어 온 agile methodology의 mental framework에서 왔습니다.

언제든 무엇을 해야 할지 확신이 없으면 `bmad-help` skill이 흐름을 유지하거나 다음 단계를 알 수 있게 돕습니다. 이 문서를 reference로 볼 수도 있지만, BMad Method를 이미 설치했다면 `bmad-help`는 완전히 interactive하고 더 빠릅니다. BMad Method를 확장하는 module이나 보완적인 non-extension module을 함께 쓴다면 `bmad-help`는 그때 사용 가능한 모든 것을 파악해 상황별 조언을 제공합니다.

마지막으로 중요한 점: 아래 모든 workflow는 선택한 tool에서 skill로 직접 실행하거나, 먼저 agent를 load한 뒤 agent menu의 항목을 사용해 실행할 수 있습니다.

<iframe src="/workflow-map-diagram.html" title="BMad Method Workflow Map Diagram" width="100%" height="100%" style="border-radius: 8px; border: 1px solid #334155; min-height: 900px;"></iframe>

<p style="font-size: 0.8rem; text-align: right; margin-top: -0.5rem; margin-bottom: 1rem;">
  <a href="/workflow-map-diagram.html" target="_blank" rel="noopener noreferrer">새 탭에서 diagram 열기 ↗</a>
</p>

## Phase 1: Analysis (선택)

Planning에 확정적으로 들어가기 전에 problem space를 탐색하고 idea를 검증합니다. [**각 tool이 하는 일과 사용할 시점 알아보기**](../explanation/analysis-phase.md).

| Workflow | 목적 | 산출물 |
| --- | --- | --- |
| `bmad-brainstorming` | brainstorming coach의 guided facilitation으로 project idea 발산 | `brainstorm.html` keepsake 및 선택적 `brainstorm-intent.md` |
| `bmad-forge-idea` | idea가 단단해지거나, 입증되거나, 낮은 비용으로 폐기될 때까지 pressure-test | 매 run `forge-report.html`; idea가 단단해질 때 `forged-idea.md` |
| `bmad-domain-research`, `bmad-market-research`, `bmad-technical-research` | market, technical, domain 가정 검증 | research findings |
| `bmad-product-brief` | strategic vision 포착 — concept가 이미 분명할 때 가장 적합 | `brief.md` + `addendum.md`, 원하는 HTML/presentation output |
| `bmad-prfaq` | Working Backwards — 고객 관점에서 product concept stress-test | `prfaq-{project}.md` |

## Phase 2: Planning

무엇을 누구를 위해 만들지 정의합니다.

| Workflow | 목적 | 산출물 |
| --- | --- | --- |
| `bmad-prd` | PRD create, update, validate — 한 skill 안의 facilitated discovery와 세 intent | Create/Update: `prd.md`, `addendum.md`, `.memlog.md`; Validate: `validation-report.html` + `.md` |
| `bmad-ux` | UX가 중요할 때 user experience 설계 — `DESIGN.md`(visual) + `EXPERIENCE.md`(behavioral) spine pair | `DESIGN.md`, `EXPERIENCE.md`, `.memlog.md` |

:::tip[한 skill의 세 intent]
`bmad-prd`는 전체 PRD lifecycle을 처리합니다. 호출할 때 intent를 밝히지 않으면 skill이 묻습니다.

- **Create** — coached discovery로 새 PRD를 처음부터 만들며 `prd.md`, `addendum.md`, `.memlog.md`를 생성합니다.
- **Update** — 기존 PRD를 change signal과 조정하고 변경 전에 conflict를 드러냅니다.
- **Validate** — configurable checklist로 PRD를 비평하고 구조화된 HTML findings report를 생성합니다.
:::

:::tip[Upstream: `bmad-product-brief`]
`bmad-product-brief`(Phase 1)는 `bmad-prd`가 Discovery 중 source-extract할 수 있는 `product-brief.md`를 만들어, 재설명을 줄이고 두 document의 정렬을 유지합니다. 두 skill은 서로를 요구하지 않으므로 무엇을 만들지 이미 알고 있다면 `bmad-prd`에서 직접 시작할 수 있습니다.
:::

## Phase 3: Solutioning

어떻게 만들지 결정하고 작업을 story로 나눕니다.

| Workflow | 목적 | 산출물 |
| --- | --- | --- |
| `bmad-architecture` | technical decision을 명시 | 기본 spine은 `ARCHITECTURE-SPINE.md`이며 원하는 output/presentation 요구로 hydrate할 수도 있음 |
| `bmad-create-epics-and-stories` | requirement를 구현 가능한 work로 분해 | story가 포함된 epic file |
| `bmad-check-implementation-readiness` | implementation 전 gate check | PASS/CONCERNS/FAIL decision |

## Phase 4: Implementation

한 번에 한 story씩 만듭니다. Phase 4에는 epic/story automation도 있으므로 계속 loop에 남을 방식, full flow 또는 quick flow를 선택할 수 있습니다.

| Workflow | 목적 | 산출물 |
| --- | --- | --- |
| `bmad-sprint-planning` | development cycle을 순서대로 진행하기 위한 tracking 초기화(project당 한 번) | `sprint-status.yaml` |
| `bmad-create-story` | implementation을 위한 다음 story 준비 | `story-[slug].md` |
| `bmad-dev-story` | story 구현 | 동작하는 code + test |
| `bmad-code-review` | implementation quality 검증 | 승인 또는 변경 요청 |
| `bmad-correct-course` | sprint 중 큰 변경 처리 | update된 plan 또는 rerouting |
| `bmad-sprint-status` | sprint 진행 및 story status 추적 | sprint status update |
| `bmad-retrospective` | epic 완료 후 review | lesson learned |

## Quick Flow (병렬 track)

작고 잘 이해한 작업이면 phase 1-3을 건너뜁니다.

| Workflow | 목적 | 산출물 |
| --- | --- | --- |
| `bmad-quick-dev` | intent 명확화, plan, implement, review, present를 하나로 묶은 quick flow | `spec-*.md` + code |
| `bmad-dev-auto` | 무인 development-loop iteration 한 번 실행 — 작은 intent를 받아 code를 냄 | `spec-*.md` + code |

`bmad-dev-auto`의 무인 development loop reference는 [Autonomous Development Loops](./dev-auto.md)를 참조하세요.

## Context Management

각 document는 다음 phase의 context가 됩니다. PRD는 architect에게 어떤 constraint가 중요한지 말하고, architecture는 dev agent에게 따를 pattern을 말합니다. Story file은 implementation에 집중되고 완전한 context를 제공합니다. 이런 구조가 없으면 agent는 일관되지 않은 결정을 내립니다.

### Project Context

:::tip[권장]
AI agent가 project의 rule과 preference를 따르도록 `project-context.md`를 만드세요. 이 file은 project의 constitution처럼 모든 workflow에서 implementation decision을 안내합니다. 이 선택 file은 Architecture Creation 마지막에 만들 수 있고, existing project에서는 현재 convention과 정렬되어야 할 중요한 내용을 포착하도록 만들 수도 있습니다.
:::

**만드는 방법:**

- **수동** — technology stack과 implementation rule을 담은 `_bmad-output/project-context.md`를 만듭니다.
- **생성** — `bmad-generate-project-context`를 실행하여 architecture 또는 codebase에서 자동 생성합니다.

[**project-context.md 더 알아보기**](../explanation/project-context.md)
