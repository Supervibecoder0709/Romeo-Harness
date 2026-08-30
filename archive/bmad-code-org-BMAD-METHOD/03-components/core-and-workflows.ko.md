# Core 및 BMM workflow/task 구성요소

## Core (13개)

`core`는 모든 설치에 자동 포함되는 shared utilities module이다. `output_folder` 기본값은 `_bmad-output`이지만, 각 skill이 이를 쓰는 방식은 다르다. `bmad-help`처럼 파일을 남기지 않는 skill과 `bmad-spec`처럼 완전한 workspace를 만드는 skill을 구분해야 한다. [E06][E14]

- 대화·발산: `bmad-brainstorming`, `bmad-forge-idea`, `bmad-party-mode`, `bmad-advanced-elicitation`
- context·구조화: `bmad-help`, `bmad-index-docs`, `bmad-spec`, `bmad-customize`, `bmad-shard-doc`
- review: `bmad-editorial-review-prose`, `bmad-editorial-review-structure`, `bmad-review-adversarial-general`, `bmad-review-edge-case-hunter`

## BMM workflow/task (27개)

`bmm`의 module manifest는 4개의 lifecycle phase와 기본 artifact root를 정의한다. 27개 중 legacy forwarding skill 4개(`bmad-create-prd`, `bmad-edit-prd`, `bmad-validate-prd`, `bmad-create-architecture`)는 “deprecated → 새 unified skill로 전달”만 하고 독자 산출물을 만들지 않는다. router는 이 4개를 새 호출 대상으로 추천하지 않는 편이 맞다. [E06][E11][E12]

| phase | 실질 workflow/task |
| --- | --- |
| 1 Analysis | document project, PRFAQ, product brief, domain/market/technical research |
| 2 Planning | PRD(create/update/validate), UX(create/update/validate) |
| 3 Solutioning | architecture(create/update/validate), epics & stories, implementation readiness, project context |
| 4 Implementation | checkpoint, code review, correct course, create/dev story, dev auto, QA E2E, quick dev, retrospective, sprint planning/status |

각 항목의 입력·출력·대화성·정확한 원문 `SKILL.md` 경로는 [04-components-table.md](../04-components-table.md)에 파일 단위로 기록했다.
