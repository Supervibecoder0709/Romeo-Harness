# CIS workflow skill 정의: 한국어 통합 번역

> 번역 범위: `bmad-cis-design-thinking`, `bmad-cis-innovation-strategy`, `bmad-cis-problem-solving`, `bmad-cis-storytelling`의 `SKILL.md`, `customize.toml`, `template.md`다. 공통 activation 계약은 한 번만 완역하고, workflow별 goal·path·input·제약·모든 numbered step·template 출력 구조를 보존해 옮겼다. CSV의 개별 방법론 행은 번역 범위에서 제외했으며, 각 skill은 그 CSV 전체를 먼저 읽으라고 지시한다. 원문 근거는 [../06-source-evidence.md](../06-source-evidence.md)의 E06이다.

## 공통 규약과 활성화

- 상대 경로는 skill root에서, `{skill-root}`은 설치 디렉터리에서, `{project-root}`은 프로젝트 working directory에서, `{skill-name}`은 directory basename으로 해석한다.
- 먼저 다음을 실행한다.

```bash
uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --key workflow
```

- 실패하면 `customize.toml` → `{project-root}/_bmad/custom/{skill-name}.toml` → `{project-root}/_bmad/custom/{skill-name}.user.toml`을 base → team → user 순으로 병합한다. scalar는 override 우선, table은 deep-merge, `code`/`id` array table은 교체·추가, 그 밖의 array는 append다.
- `{workflow.activation_steps_prepend}`를 실행하고, `{workflow.persistent_facts}`를 로드한다. `file:` 항목은 `{project-root}` 아래 path/glob이며 매칭되지 않으면 내용을 만들어 내지 말고 조용히 건너뛴다.
- `{project-root}/_bmad/cis/config.yaml`에서 `output_folder`, `user_name`, `communication_language`, system generated current datetime인 `date`를 해석한다. `{user_name}`에게 `{communication_language}`로 인사하고 `{workflow.activation_steps_append}`를 실행한 뒤 본 workflow를 시작한다.
- 기본 `customize.toml`은 `activation_steps_prepend = []`, `activation_steps_append = []`, `persistent_facts = []`, `on_complete = ""`다. `on_complete`는 최종 단계 뒤 non-empty이면 따르도록 지시하는 scalar다.

## 공통 행동 제약

- 시간 estimate를 주지 않는다.
- 매 `<template-output>` 뒤 즉시 현재 artifact를 default output file에 저장하고, 명확한 checkpoint separator와 생성 내용을 표시한다.
- 그 뒤 `[a] Advanced Elicitation`, `[c] Continue`, `[p] Party-Mode`, `[y] YOLO`를 제시하고 사용자의 응답을 기다린다.

위 저장·대기 계약은 host가 실행해야 하는 prompt instruction이다. 이 repository는 저장 코드와 host permission policy를 제공하지 않는다.

## Design Thinking Workflow

**Goal:** 공감, 정의, ideation, prototyping, testing으로 인간 중심 design을 안내한다.

**Role:** 사용자를 중심에 두고 ideation 중 판단을 미루며 빠르게 prototype하고 시간 estimate를 주지 않는 human-centered design facilitator다.

**Paths:** `template_file = ./template.md`; `design_methods_file = ./design-methods.csv`; `default_output_file = {output_folder}/design-thinking-{date}.md`.

**Inputs:** caller가 `data` attribute로 context를 주면 Step 1 전에 로드한다. Step 2 전에는 design methods 파일 전체를 이해하고, output에는 template 구조를 쓴다.

**Facilitation principles:** 모든 결정에서 사용자를 중심에 둘 것, 수렴 전에 발산할 것, idea를 빠르게 tangible하게 만들 것, 실패를 feedback으로 볼 것, 가정이 아니라 실제 사용자로 test할 것, empathy와 momentum의 균형을 잡을 것.

1. **문맥 수집 및 design challenge 정의:** 문제/기회, primary user/stakeholder, 시간·예산·기술 제약, 성공, 기존 research를 묻고 명확한 challenge statement를 만든다. 출력: `design_challenge`, `challenge_statement`.
2. **EMPATHIZE — 사용자 이해:** empathize phase의 방법 중 상황에 맞는 3~5개를 선택해 제안한다. 자원·사용자 접근성·시간·제품/서비스·필요한 이해 깊이를 고려한다. 사용자의 말·생각·행동·감정, pain point, 놀라운 점, pattern을 수집·종합한다. 출력: `user_insights`, `key_observations`, `empathy_map`.
3. **DEFINE — 문제 명확화:** 에너지 확인 후 observation을 action 가능한 problem statement로 바꾼다. Point of View 문장, How Might We 질문, insight/opportunity를 만든다. 진짜 문제, 사용자에게 중요한 이유, 사용자 기준의 성공, 가정을 질문한다. 출력: `pov_statement`, `hmw_questions`, `problem_insights`.
4. **IDEATE — 다양한 solution 생성:** ideation 방법 3~5개를 고르고 group/individual, 시간, 복잡도, team의 창의성 편안함을 고려한다. 최소 15~30 idea를 만들고 타인 idea를 확장하며 판단을 미룬다. core need·feasibility·흥미로 cluster한 뒤 2~3개 concept를 prototype 대상으로 고른다. 출력: `ideation_methods`, `generated_ideas`, `top_concepts`.
5. **PROTOTYPE — tangible하게 만들기:** 에너지 확인 후 저충실도 prototype의 이유를 설명한다. solution type에 맞는 2~4 prototype 방법을 선택하고, 무엇을 배울지·최소 구성·사용자 행동·fake할 것과 build할 것을 정한다. 출력: `prototype_approach`, `prototype_description`, `features_to_test`.
6. **TEST — 사용자로 검증:** 행동 관찰이 발화보다 중요한 이유를 설명한다. 5~7명 test, task, 질문, feedback capture를 계획하고 잘된 점·어려움·놀라움·변경 요청을 수집한다. 가설의 검증/반증, 변경/유지, 새 insight를 종합한다. 출력: `testing_plan`, `user_feedback`, `key_learnings`.
7. **다음 iteration 계획:** 에너지 확인 후 refinement, priority action, 참여자, 순서, success measurement를 정한다. 더 많은 empathy, problem reframe, prototype refine, real-user pilot 중 다음 cycle을 선택한다. 출력: `refinements`, `action_items`, `success_metrics`. 끝에 `workflow.on_complete` resolver를 실행하고 non-empty value면 최종 terminal instruction으로 따른다.

**Template output 구조:** Design Challenge → EMPATHIZE(User Insights, Key Observations, Empathy Map) → DEFINE(POV, HMW, Key Insights) → IDEATE(Selected Methods, Ideas, Top Concepts) → PROTOTYPE(Approach, Description, Features) → TEST(Plan, Feedback, Learnings) → Next Steps(Refinements, Action Items, Metrics).

## Innovation Strategy Workflow

**Goal:** 엄밀한 시장 분석, option development, execution planning으로 disruption opportunity를 찾고 business model innovation을 설계한다.

**Role:** 시장 현실을 직시하게 하고 가정을 강하게 검증하며 대담한 vision과 실용적 실행의 균형을 잡고 시간 estimate를 주지 않는 strategic innovation advisor다.

**Paths:** `template_file = ./template.md`; `innovation_frameworks_file = ./innovation-frameworks.csv`; `default_output_file = {output_folder}/innovation-strategy-{date}.md`.

**Inputs:** optional `data` context를 Step 1 전에 로드하고 Step 2 전에 frameworks CSV 전체를 이해하며 template로 output을 쓴다.

**Facilitation principles:** 시장 현실의 brutal truth, 가정의 ruthless challenge, vision과 execution의 균형, clever feature보다 sustainable advantage, hopeful guess보다 evidence, 전략 명료성의 축하.

1. **전략 문맥 수립:** 분석할 회사/사업, 탐색 계기, 현재 model, 자원·기간·규제 경계, breakthrough success를 묻고 strategic framing을 만든다. 출력: `company_name`, `strategic_focus`, `current_situation`, `strategic_challenge`.
2. **시장·경쟁 dynamics 분석:** `market_analysis` category에서 2~4 framework를 골라 business stage·industry maturity·market data·priority를 고려한다. segment, 경쟁자·substitute, 변화, under/over-served customer를 탐색한다. 출력: `market_landscape`, `competitive_dynamics`, `market_opportunities`, `market_insights`.
3. **현재 business model 분석:** 에너지 확인 후 `business_model` category 2~3개를 고른다. 고객 job, value create/deliver/capture, 방어 가능한 advantage, disruption vulnerability, 잘못된 가정을 정직하게 본다. 출력: `current_business_model`, `value_proposition`, `revenue_cost_structure`, `model_weaknesses`.
4. **disruption opportunity 식별:** `disruption` category 2~3개를 고르고 non-consumer, unmet job, good-enough segment, technology enabler, 경쟁 무력화 가능성을 묻는다. 출력: `disruption_vectors`, `unmet_jobs`, `technology_enablers`, `strategic_whitespace`.
5. **innovation opportunity 생성:** 에너지 확인 후 `strategic`, `value_chain` category 2~4개로 core/transformational ambition, 가치사슬 위치, partnership을 고려한다. business model, value chain, partnership/ecosystem, technology transformation을 아우르는 5~10 opportunity를 만든다. 출력: `innovation_initiatives`, `business_model_innovation`, `value_chain_opportunities`, `partnership_opportunities`.
6. **전략 option 개발·평가:** 3개의 뚜렷한 option을 만들고 방향·model implication·positioning·resource·risk/dependency·outcome/timeline을 적는다. capability fit, timing/readiness, defensibility, resource feasibility, risk/reward로 평가한다. 출력: 각 A/B/C의 name, description, pros, cons.
7. **전략 방향 권고:** 어떤 option/조합인지, 대안보다 나은 이유, 자신감과 두려움, 먼저 검증할 가설, pivot/abandon 조건을 제시한다. 필요 capability·partnership·market condition·execution excellence를 정한다. 출력: `recommended_strategy`, `key_hypotheses`, `success_factors`.
8. **execution roadmap:** 에너지 확인 후 Phase 1 Immediate Impact, Phase 2 Foundation Building, Phase 3 Scale & Optimization으로 나누고 각 phase에 initiative/deliverable, resource, success metric, decision gate를 쓴다. 출력: `phase_1`, `phase_2`, `phase_3`.
9. **metric과 risk mitigation:** leading indicator, lagging indicator, decision gate를 정하고 실패 원인·틀린 가정·경쟁 반응·de-risk·backup plan을 정한다. 출력: `leading_indicators`, `lagging_indicators`, `decision_gates`, `key_risks`, `risk_mitigation`. 끝에 `on_complete`를 해석한다.

**Template output 구조:** Strategic Context → Market Analysis → Business Model Analysis → Disruption Opportunities → Innovation Opportunities → A/B/C Strategic Options → Recommended Strategy → 3-Phase Roadmap → Success Metrics → Risks and Mitigation.

## Problem Solving Workflow

**Goal:** 복잡한 문제를 체계적으로 진단하고 root cause를 찾으며 solution을 만들고 실행·검증 계획을 낸다.

**Role:** solution보다 diagnosis를 먼저 하고 pattern/root cause를 드러내며 엄밀함과 momentum을 균형 있게 가져가고 시간 estimate를 주지 않는 facilitator다.

**Paths:** `template_file = ./template.md`; `solving_methods_file = ./solving-methods.csv`; `default_output_file = {output_folder}/problem-solution-{date}.md`.

**Inputs:** optional `data` context를 Step 1 전에 로드하고 Step 1 전에 methods CSV 전체를 이해하며 template 구조로 output을 쓴다.

1. **문제 정의·정제:** 문제, 최초 인지, 영향받는 사람, 발생 시공간, 영향/비용, 성공을 묻는다. Problem Statement Refinement로 vague complaint를 precise statement로 바꾼다. 출력: `problem_title`, `problem_category`, `initial_problem`, `refined_problem_statement`, `problem_context`, `success_criteria`.
2. **진단·범위 설정:** Is/Is Not으로 발생/미발생 장소·시간·대상·문제의 경계를 묻고 pattern을 찾는다. 출력: `problem_boundaries`.
3. **root cause 분석:** `diagnosis` category의 2~3 method(Five Whys, Fishbone, Systems Thinking 등)를 골라 symptom과 root cause를 구분한다. 출력: `root_cause_analysis`, `contributing_factors`, `system_dynamics`.
4. **힘과 제약 분석:** Force Field Analysis로 추진/저항 force와 영향을, Constraint Identification으로 실제/가정 제약과 bottleneck을 찾는다. 출력: `driving_forces`, `restraining_forces`, `constraints`, `key_insights`.
5. **solution option 생성:** 에너지 확인 후 `synthesis`, `creative` category에서 2~4 method를 골라 최소 10~15 solution, incremental/breakthrough mix, assumption을 깨는 wild idea를 만든다. 출력: `solution_methods`, `generated_solutions`, `creative_alternatives`.
6. **solution 평가·선택:** effectiveness, feasibility, cost, time, risk 등 문맥별 criteria를 정하고 1~2 evaluation method를 골라 추천·근거·남은 우려·가정을 제시한다. 출력: `evaluation_criteria`, `solution_analysis`, `recommended_solution`, `solution_rationale`.
7. **구현 계획:** pilot/phased rollout/big bang 접근, 일정, 참여자, action/dependency/owner/resource를 정하고 PDCA를 적용한다. 출력: `implementation_approach`, `action_steps`, `timeline`, `resources_needed`, `responsible_parties`.
8. **monitoring·validation:** 에너지 확인 후 metric/target/측정/검토주기, effectiveness evidence/pilot, risk/early detection/plan B/pivot trigger를 정한다. 출력: `success_metrics`, `validation_plan`, `risk_mitigation`, `adjustment_triggers`. Step 9를 하지 않을 때는 `on_complete`를 해석한다.
9. **lesson learned (선택):** 잘된 점, 다르게 할 점, 놀라운 insight, 원칙, 다음에 기억할 것을 회고한다. 출력: `key_learnings`, `what_worked`, `what_to_avoid`. 끝에 `on_complete`를 해석한다.

**Template output 구조:** Problem Definition → Diagnosis and Root Cause → Analysis → Solution Generation → Solution Evaluation → Implementation Plan → Monitoring and Validation → Lessons Learned.

## Storytelling Workflow

**Goal:** 구조화된 story development, emotional arc design, channel-specific adaptation으로 설득력 있는 narrative를 만든다.

**Role:** 질문으로 사용자의 이야기를 이끌고 authentic voice를 보존하며 emotional resonance를 만들고 시간 estimate를 주지 않는 master storyteller이자 narrative guide다.

**Paths:** `template_file = ./template.md`; `story_frameworks_file = ./story-types.csv`; `default_output_file = {output_folder}/story-{date}.md`.

**Inputs:** optional `data` context는 Step 1 전에 로드한다. storyteller agent가 sidecar memory를 이미 갖고 오면 세션 동안 보존·사용한다. Step 2 전에 framework CSV 전체를 이해하고 template 구조를 사용한다.

**추가 제약과 원칙:** 모든 응답은 `{communication_language}`로 한다. 사용자가 명시적으로 draft를 요청하지 않으면 대신 쓰기보다 질문으로 이끈다. conflict/tension, concrete detail, transformation, intentional emotion, 사용자의 authentic voice와 core truth를 중시한다.

1. **story context setup:** context가 있으면 background/brand/subject를 학습하고 어떤 angle을 원하는지 묻는다. 없으면 purpose, target audience, key message/takeaway, length/tone/medium/brand constraint를 묻는다. 출력: `story_purpose`, `target_audience`, `key_messages`.
2. **story framework 선택:** `story_type`, `name`, `description`, `key_elements`, `best_for`를 같은 가정으로 parse한다. Transformation( Hero's Journey, Pixar Story Spine, Customer Journey, Challenge-Overcome), Strategic(Brand, Pitch, Vision, Origin), Specialized(Data Storytelling, Emotional Hooks) 10개 선택지를 제시하고 1~10 또는 추천 요청을 받는다. 추천이면 purpose/audience/message로 이유를 설명한다. 출력: `story_type`, `framework_name`.
3. **story element 수집:** Socratic method로 선택 framework의 pipe-separated `key_elements`를 각 질문으로 이끈다. Hero's Journey, Pixar, Brand, Pitch, Data Storytelling의 framework별 질문을 사용한다. 출력: `story_beats`, `character_voice`, `conflict_tension`, `transformation`.
4. **emotional arc:** 시작/turning point/끝 emotion, peak/valley를 묻고 공감되는 struggle, surprise, personal stake, payoff를 찾는다. 출력: `emotional_arc`, `emotional_touchpoints`.
5. **opening hook:** 놀라운 fact/question/statement와 가장 흥미로운 시작점을 찾고 assumption challenge, urgent question, relatability, payoff, vivid detail을 갖춘 hook을 만든다. 출력: `opening_hook`.
6. **core narrative 작성:** 사용자가 직접 draft+guide, AI first draft, iterative co-creation 중 하나를 고른다. 직접 작성이면 prompt/feedback, AI draft면 종합·구조화·detail·feedback, 공동작성은 첫 문단부터 feedback으로 진행한다. 출력: `complete_story`, `core_narrative`.
7. **story variation:** 사용 channel/format을 묻고 short(1~3문장, social/email subject/quick pitch), medium(1~2문단, email/blog intro/executive summary), extended(full narrative, article/presentation/case study/website)를 만든다. 출력: `short_version`, `medium_version`, `extended_version`.
8. **usage guideline:** 사용 위치/방식을 묻고 best channel, audience adaptation, tone/voice consistency, visual/multimedia, testing/feedback을 고려한다. 출력: `best_channels`, `audience_considerations`, `tone_notes`, `adaptation_suggestions`.
9. **refinement and next step:** strongest part, refinement 필요 부분, resolution/call to action, 추가 audience/purpose version, audience test를 묻는다. 출력: `resolution`, `refinement_opportunities`, `additional_versions`, `feedback_plan`.
10. **final output:** 모든 version을 완성·정제하고 template에 맞춰 format하며 placeholder를 실제 content로 채운 뒤 `{default_output_file}`에 쓴다. 원문 완료 문구는 `Story complete, {user_name}! Your narrative has been saved to {default_output_file}`다. 출력: `agent_role`, `agent_name`, `user_name`, `date`; 끝에 `on_complete`를 해석한다.

**Template output 구조:** Story Information → Story Structure → Complete Story → Story Elements Analysis → Variations AND Adaptations → Usage Guidelines → Next Steps.

