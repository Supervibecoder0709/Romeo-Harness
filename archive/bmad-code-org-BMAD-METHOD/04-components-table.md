# 구성요소 표

**읽는 법:** “확인됨”은 고정 SHA의 원문 파일을 직접 읽은 사실이다. “경로 미선언”은 원문 SKILL에서 정적 파일명을 선언하지 않았다는 뜻이며, 임의의 `_bmad-output` 경로를 채워 넣지 않았다. `기본`은 사람이 묻고 menu/checkpoint에서 멈추는 흐름, `자동 가능`은 명시적인 headless/non-interactive mode가 있는 경우다. 원문 위치는 설치 후 경로가 아니라 **본체 source 내 file location**이다.

## 모듈·설치 구성요소

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태 변화 | 실행 방식 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `core` | built-in module | 전 module 공용 utility/skill | installer module selection; core config | 기본 `output_folder={project-root}/_bmad-output` | installer config | `src/core-skills/module.yaml` | 확인됨 [E06] |
| `bmm` | built-in module | 분석→계획→solutioning→구현 agile suite | installer module selection; core config | 기본 `planning_artifacts=_bmad-output/planning-artifacts`, `implementation_artifacts=_bmad-output/implementation-artifacts`, `project_knowledge=docs` | installer config | `src/bmm-skills/module.yaml` | 확인됨 [E06] |
| installer | Node CLI | module copy, config, IDE wiring | `install --directory --modules --tools --yes/...` | `_bmad/`, manifest/config, IDE skill dirs | interactive 또는 `--yes` | `tools/installer/{bmad-cli.js,commands/install.js,core/install-paths.js}` | 확인됨 [E03][E04] |
| install manifest | state/probe | installed modules·IDE·version source 기록 | installation result | `_bmad/_config/manifest.yaml` | automatic during install | `tools/installer/core/manifest.js` | 확인됨 [E05] |
| `codex` platform | IDE configuration | Codex가 읽을 skill directory 지정 | `--tools codex` | project `.agents/skills/<id>/SKILL.md`; global `~/.codex/skills` | automatic during install | `tools/installer/ide/platform-codes.yaml` | 확인됨; runtime execution 미확인 [E09][E10] |

## Core: 13개 SKILL

| 구성요소 | 종류 | 역할·입력 | 출력/상태 변화 | 실행 방식 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| `bmad-advanced-elicitation` | task | 기존 문서와 더 깊이 살필 section/method | 사용자가 승인할 때만 대상 문서 변경; fixed output 미선언 | 기본 대화형 | `src/core-skills/bmad-advanced-elicitation/SKILL.md` | 확인됨 [E14] |
| `bmad-brainstorming` | workflow | 주제·목표·입력 자료 | `{output_folder}/brainstorming/brainstorm-{topic_slug}-{date}/`의 session log/최종 artifact | 기본 대화형, headless 지시 존재 | `src/core-skills/bmad-brainstorming/{SKILL.md,customize.toml}` | 확인됨 [E14] |
| `bmad-customize` | task | 변경할 skill/agent/workflow와 persistent instruction | `{project-root}/_bmad/custom/*.toml` override 및 merge verification | 대화형 | `src/core-skills/bmad-customize/SKILL.md` | 확인됨 [E14] |
| `bmad-editorial-review-prose` | review task | 대상 문서 path | 대상 문서 곁의 3-column suggested-fix report; fixed filename 미선언 | 입력 기반 | `src/core-skills/bmad-editorial-review-prose/SKILL.md`; `src/core-skills/module-help.csv` | 확인됨 [E06][E14] |
| `bmad-editorial-review-structure` | review task | 구조 개선이 필요한 문서 path | 대상 문서 곁의 structure report; fixed filename 미선언 | 입력 기반 | `src/core-skills/bmad-editorial-review-structure/SKILL.md`; `module-help.csv` | 확인됨 [E06][E14] |
| `bmad-forge-idea` | workflow | idea, constraints, evidence | `{output_folder}/forge/...`; 매 run `forge-report.html`, hardened일 때 `forged-idea.md` | 기본 대화형 | `src/core-skills/bmad-forge-idea/{SKILL.md,customize.toml}` | 확인됨 [E06][E14] |
| `bmad-help` | router/help | 사용자의 “다음에 무엇을?” 질문 | inline routing answer; fixed disk output 없음 | 대화형 | `src/core-skills/bmad-help/SKILL.md` | 확인됨 [E06][E14] |
| `bmad-index-docs` | task | docs directory/root | inline directory index; fixed disk output 없음 | 입력 기반 | `src/core-skills/bmad-index-docs/SKILL.md` | 확인됨 [E14] |
| `bmad-party-mode` | orchestration workflow | topic, installed/named agents, optional mode | discussion 및 `{output_folder}/party-mode` 아래 memory/document 가능 | 기본 대화형; `--non-interactive`만 자동 close | `src/core-skills/bmad-party-mode/{SKILL.md,customize.toml}` | 확인됨 [E14] |
| `bmad-review-adversarial-general` | review task | diff/file/function content | inline finding JSON; fixed disk output 없음 | 입력 기반 | `src/core-skills/bmad-review-adversarial-general/SKILL.md` | 확인됨 [E14] |
| `bmad-review-edge-case-hunter` | review task | diff/file/function content | inline finding JSON array; fixed disk output 없음 | 입력 기반 | `src/core-skills/bmad-review-edge-case-hunter/SKILL.md` | 확인됨 [E14] |
| `bmad-shard-doc` | filesystem task | source `.md`, destination folder, original 처리 선택 | sharded folder/index; user choice에 따라 original delete/move/keep | 대화형·파괴적 choice 존재 | `src/core-skills/bmad-shard-doc/SKILL.md` | 확인됨 [E14] |
| `bmad-spec` | workflow | intent source(brief/PRD/transcript 등), slug | `{output_folder}/specs/spec-{slug}/{SPEC.md,companions,.memlog.md}` | interactive 또는 explicit/programmatic headless | `src/core-skills/bmad-spec/{SKILL.md,customize.toml}` | 확인됨 [E14] |

## BMM persona agent: 6개 SKILL

| 구성요소 | 종류 | 역할·입력 | 출력/상태 변화 | 실행 방식 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| `bmad-agent-analyst` (Mary) | agent | 분석 intent 또는 menu choice | persona session; 선택된 analysis skill로 dispatch | 대화형 | `src/bmm-skills/1-analysis/bmad-agent-analyst/{SKILL.md,customize.toml}` | 확인됨 [E07][E15] |
| `bmad-agent-tech-writer` (Paige) | agent | 문서 intent 또는 menu choice | persona session; document/diagram/validation task dispatch | 대화형 | `src/bmm-skills/1-analysis/bmad-agent-tech-writer/{SKILL.md,customize.toml}` | 확인됨 [E07][E15] |
| `bmad-agent-pm` (John) | agent | PM intent 또는 menu choice | persona session; PRD/epics/readiness/change dispatch | 대화형 | `src/bmm-skills/2-plan-workflows/bmad-agent-pm/{SKILL.md,customize.toml}` | 확인됨 [E07][E15] |
| `bmad-agent-ux-designer` (Sally) | agent | UX intent | persona session; UX workflow dispatch | 대화형 | `src/bmm-skills/2-plan-workflows/bmad-agent-ux-designer/{SKILL.md,customize.toml}` | 확인됨 [E07][E15] |
| `bmad-agent-architect` (Winston) | agent | architecture/readiness intent | persona session; architecture/readiness dispatch | 대화형 | `src/bmm-skills/3-solutioning/bmad-agent-architect/{SKILL.md,customize.toml}` | 확인됨 [E07][E15] |
| `bmad-agent-dev` (Amelia) | agent | implementation intent | persona session; story/dev/review/QA/sprint dispatch | 대화형 | `src/bmm-skills/4-implementation/bmad-agent-dev/{SKILL.md,customize.toml}` | 확인됨 [E07][E15] |

## BMM workflow/task: Analysis 6개

| 구성요소 | 종류 | 역할·입력 | 출력/상태 변화 | 실행 방식 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| `bmad-document-project` | workflow | existing/brownfield project | `{project_knowledge}/project-scan-report.json` state와 project documentation; default `project_knowledge=docs`라 `_bmad-output` 고정 아님 | step menu 대화형 | `src/bmm-skills/1-analysis/bmad-document-project/{SKILL.md,instructions.md}` | 확인됨 [E06][E08] |
| `bmad-prfaq` | workflow | customer, problem, stakes, solution; optional research/context | `{planning_artifacts}/prfaq-{project_name}.md`와 PRD distillate | 기본 coaching; `--headless/-H`는 first draft 자동 | `src/bmm-skills/1-analysis/bmad-prfaq/SKILL.md` | 확인됨 [E07][E08] |
| `bmad-product-brief` | workflow | product intent, source materials, create/update/validate intent | `{planning_artifacts}/briefs/brief-{project_name}-{date}/{brief.md,addendum.md,.memlog.md}` | interactive 또는 headless | `src/bmm-skills/1-analysis/bmad-product-brief/{SKILL.md,customize.toml}` | 확인됨 [E08][E11] |
| `bmad-domain-research` | workflow | domain topic/context | `{planning_artifacts}/research/domain-{slug}-research-{date}.md` | 대화형 step workflow | `src/bmm-skills/1-analysis/research/bmad-domain-research/SKILL.md` | 확인됨 [E08] |
| `bmad-market-research` | workflow | market topic/context | `{planning_artifacts}/research/market-{slug}-research-{date}.md` | 대화형 step workflow | `src/bmm-skills/1-analysis/research/bmad-market-research/SKILL.md` | 확인됨 [E08] |
| `bmad-technical-research` | workflow | technical topic/context | `{planning_artifacts}/research/technical-{slug}-research-{date}.md` | 대화형 step workflow | `src/bmm-skills/1-analysis/research/bmad-technical-research/SKILL.md` | 확인됨 [E08] |

## BMM workflow/task: Planning 5개

| 구성요소 | 종류 | 역할·입력 | 출력/상태 변화 | 실행 방식 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| `bmad-create-prd` | deprecated forwarder | create intent | 독자 output 없음; `bmad-prd` create로 전달 | 전달 후 target mode | `src/bmm-skills/2-plan-workflows/bmad-create-prd/SKILL.md` | 확인됨 [E11] |
| `bmad-edit-prd` | deprecated forwarder | update intent + existing PRD | 독자 output 없음; `bmad-prd` update로 전달 | 전달 후 target mode | `src/bmm-skills/2-plan-workflows/bmad-edit-prd/SKILL.md` | 확인됨 [E11] |
| `bmad-validate-prd` | deprecated forwarder | validate intent + existing PRD | 독자 output 없음; `bmad-prd` validate로 전달 | 전달 후 target mode | `src/bmm-skills/2-plan-workflows/bmad-validate-prd/SKILL.md` | 확인됨 [E11] |
| `bmad-prd` | workflow | product sources + create/update/validate intent | `{planning_artifacts}/prds/prd-{project_name}-{date}/{prd.md,addendum.md,.memlog.md,review-*.md}`; validate report | interactive 또는 headless | `src/bmm-skills/2-plan-workflows/bmad-prd/{SKILL.md,customize.toml}` | 확인됨 [E11] |
| `bmad-ux` | workflow | product/UX sources + create/update/validate intent | `{planning_artifacts}/ux-designs/ux-{project_name}-{date}/{DESIGN.md,EXPERIENCE.md,.memlog.md}` | interactive 또는 headless | `src/bmm-skills/2-plan-workflows/bmad-ux/{SKILL.md,customize.toml}` | 확인됨 [E11] |

## BMM workflow/task: Solutioning 5개

| 구성요소 | 종류 | 역할·입력 | 출력/상태 변화 | 실행 방식 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| `bmad-create-architecture` | deprecated forwarder | create intent | 독자 output 없음; `bmad-architecture` create로 전달 | 전달 후 target mode | `src/bmm-skills/3-solutioning/bmad-create-architecture/SKILL.md` | 확인됨 [E12] |
| `bmad-architecture` | workflow | PRD/spec/UX/codebase; create/update/validate intent | `{planning_artifacts}/architecture/architecture-{project_name}-{date}/{ARCHITECTURE-SPINE.md,.memlog.md}` + 선택 human artifact | coaching 기본 또는 headless | `src/bmm-skills/3-solutioning/bmad-architecture/{SKILL.md,customize.toml}` | 확인됨 [E11][E12] |
| `bmad-create-epics-and-stories` | workflow | PRD, architecture, optional UX | `{planning_artifacts}/epics.md` | step menu 대화형 | `src/bmm-skills/3-solutioning/bmad-create-epics-and-stories/{SKILL.md,steps/step-01-validate-prerequisites.md}` | 확인됨 [E12] |
| `bmad-check-implementation-readiness` | gate workflow | PRD, UX, architecture, epics/stories | `{planning_artifacts}/implementation-readiness-report-{date}.md`, readiness decision | step menu 대화형 | `src/bmm-skills/3-solutioning/bmad-check-implementation-readiness/{SKILL.md,steps/step-01-document-discovery.md}` | 확인됨 [E12] |
| `bmad-generate-project-context` | workflow | codebase/architecture context | `{output_folder}/project-context.md` | workflow; default interaction not separately declared | `src/bmm-skills/3-solutioning/bmad-generate-project-context/SKILL.md` | 확인됨 [E12] |

## BMM workflow/task: Implementation 11개

| 구성요소 | 종류 | 역할·입력 | 출력/상태 변화 | 실행 방식 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| `bmad-checkpoint-preview` | human-review workflow | change/commit/branch/PR context | inline guided review trail; file output path 미선언 | 대화형 human-in-loop | `src/bmm-skills/4-implementation/bmad-checkpoint-preview/{SKILL.md,generate-trail.md}` | 확인됨 [E13] |
| `bmad-code-review` | review workflow | code change, story/sprint context | story `Review Findings`, `sprint-status.yaml` update; `{implementation_artifacts}/deferred-work.md` 가능 | checkpoints; subagent 가능 | `src/bmm-skills/4-implementation/bmad-code-review/{SKILL.md,steps/step-04-present.md}` | 확인됨 [E13] |
| `bmad-correct-course` | change workflow | change signal + PRD/epic/arch/UX/spec | `{planning_artifacts}/sprint-change-proposal-{date}.md`, related plan updates | 대화형 mode choice | `src/bmm-skills/4-implementation/bmad-correct-course/SKILL.md` | 확인됨 [E13] |
| `bmad-create-story` | workflow | next/specified story + epics/PRD/architecture/UX | `{implementation_artifacts}/{story_key}.md`, `sprint-status.yaml` update | 대화형 | `src/bmm-skills/4-implementation/bmad-create-story/SKILL.md` | 확인됨 [E13] |
| `bmad-dev-auto` | unattended workflow | small intent/spec; baseline revision | existing spec updated with auto result; missing spec이면 `{implementation_artifacts}/bmad-dev-auto-result-{slug-or-timestamp}.md`; code changes/review | 자동 iteration (no human interaction review step) | `src/bmm-skills/4-implementation/bmad-dev-auto/{SKILL.md,step-04-review.md}` | 확인됨 [E13] |
| `bmad-dev-story` | implementation workflow | prepared story + codebase | code/tests, story update, `sprint-status.yaml` to review | 대화형; ambiguity면 ask/halt | `src/bmm-skills/4-implementation/bmad-dev-story/SKILL.md` | 확인됨 [E13] |
| `bmad-qa-generate-e2e-tests` | test-generation workflow | source dir + what to test | test suite + `{implementation_artifacts}/tests/test-summary.md` | 대화형 framework/test scope confirmation | `src/bmm-skills/4-implementation/bmad-qa-generate-e2e-tests/SKILL.md` | 확인됨 [E13] |
| `bmad-quick-dev` | short-flow workflow | small, understood intent | spec + implementation at `{implementation_artifacts}`; exact spec run filename not declared in root SKILL | staged workflow; present step may commit locally if VCS dirty, never auto-push | `src/bmm-skills/4-implementation/bmad-quick-dev/{SKILL.md,step-05-present.md}` | 확인됨 [E07][E13] |
| `bmad-retrospective` | workflow | completed epic, sprint status, prior artifacts | `{implementation_artifacts}/epic-{epic_number}-retro-{date}.md`; sprint status retrospective mark | interactive party-style facilitation | `src/bmm-skills/4-implementation/bmad-retrospective/SKILL.md` | 확인됨 [E13] |
| `bmad-sprint-planning` | workflow | all epics/stories | `{implementation_artifacts}/sprint-status.yaml` | workflow, human-facing but no headless contract found | `src/bmm-skills/4-implementation/bmad-sprint-planning/SKILL.md` | 확인됨 [E13] |
| `bmad-sprint-status` | status workflow | `{implementation_artifacts}/sprint-status.yaml`, optional mode | inline summary/recommendation; data/validate modes available, no new fixed artifact | default interactive; `data`/`validate` mode branch | `src/bmm-skills/4-implementation/bmad-sprint-status/SKILL.md` | 확인됨 [E13] |

## G-M3 discovery/T2 추천 후보

**추천(추론):** router의 discovery/T2에는 먼저 `bmad-product-brief`(아이디어는 있으나 PM discovery가 필요한 경우)와 `bmad-prfaq`(고객 문제·stakes·solution을 강하게 검증하려는 경우)를 제시하고, evidence가 부족할 때 domain/market/technical research를 추가하는 순서가 가장 맞다. 빠른 발산은 `bmad-brainstorming`, 반증 압박은 `bmad-forge-idea`가 보조다. 이 선택은 BMM workflow map과 각 output contract에서 추론한 것이며, 자동 실행 추천이 아니다. [E07][E08][E14]
