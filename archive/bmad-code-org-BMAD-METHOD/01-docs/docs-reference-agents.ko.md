---
title: Agents
description: BMM 기본 agent의 skill ID, menu trigger, 주요 workflow
sidebar:
  order: 2
---

## 기본 Agents

이 페이지는 BMad Method와 함께 설치되는 기본 BMM(Agile suite) agent와 해당 skill ID, menu trigger, 주요 workflow를 나열합니다. 각 agent는 skill로 호출됩니다.

## 참고

- 각 agent는 installer가 생성하는 skill로 제공됩니다. agent를 호출할 때 skill ID(예: `bmad-agent-dev`)를 사용합니다.
- Trigger는 각 agent menu에 표시되는 짧은 menu code(예: `PRD`)와 fuzzy match입니다.
- QA test generation은 Developer agent에서 쓸 수 있는 `bmad-qa-generate-e2e-tests` workflow skill이 담당합니다. 전체 Test Architect(TEA)는 별도 module에 있습니다.

| Agent | Skill ID | Triggers | 주요 workflows |
| --- | --- | --- | --- |
| Analyst (Mary) | `bmad-agent-analyst` | `BP`, `MR`, `DR`, `TR`, `CB`, `WB`, `DP` | Brainstorm, Market Research, Domain Research, Technical Research, Create Brief, PRFAQ Challenge, Document Project |
| Product Manager (John) | `bmad-agent-pm` | `PRD`, `CE`, `IR`, `CC` | Create/Update/Validate PRD, Create Epics and Stories, Implementation Readiness, Correct Course |
| Architect (Winston) | `bmad-agent-architect` | `CA`, `IR` | Create Architecture, Implementation Readiness |
| Developer (Amelia) | `bmad-agent-dev` | `DS`, `QD`, `QA`, `CR`, `SP`, `CS`, `ER` | Dev Story, Quick Dev, QA Test Generation, Code Review, Sprint Planning, Create Story, Epic Retrospective |
| UX Designer (Sally) | `bmad-agent-ux-designer` | `CU` | Create UX Design |
| Technical Writer (Paige) | `bmad-agent-tech-writer` | `DP`, `WD`, `MG`, `VD`, `EC` | Document Project, Write Document, Mermaid Generate, Validate Doc, Explain Concept |

## Trigger 유형

Agent menu trigger는 두 가지 호출 유형을 사용합니다. 어떤 유형인지 알면 적절한 입력을 제공할 수 있습니다.

### Workflow trigger(인자 불필요)

대부분의 trigger는 구조화된 workflow file을 불러옵니다. Trigger code를 입력하면 agent가 workflow를 시작하고 각 단계에서 필요한 입력을 묻습니다.

예: `PRD`(PRD create, update 또는 validate), `DS`(Dev Story), `CA`(Create Architecture), `QD`(Quick Dev)

### 대화형 trigger(인자 필요)

일부 trigger는 구조화된 workflow 대신 자유 형식 대화를 시작합니다. Trigger code와 함께 필요한 내용을 설명해야 합니다.

| Agent | Trigger | 제공할 내용 |
| --- | --- | --- |
| Technical Writer (Paige) | `WD` | 작성할 문서 설명 |
| Technical Writer (Paige) | `MG` | diagram 설명과 유형(sequence, flowchart 등) |
| Technical Writer (Paige) | `VD` | validate할 문서와 집중할 영역 |
| Technical Writer (Paige) | `EC` | 설명할 concept 이름 |

**예시:**

```text
WD Write a deployment guide for our Docker setup
MG Create a sequence diagram showing the auth flow
EC Explain how the module system works
```
