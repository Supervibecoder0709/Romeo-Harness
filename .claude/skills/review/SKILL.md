---
name: review
description: 다른 런타임이 구현한 결과를 읽기만 하며 검토해 findings 와 게이트 판정을 낸다. 라우터가 검토자를 요구하는 패키지에서 구현이 끝난 뒤 라우터가 켤 때만 쓴다 — 스스로 켜지지 않는다. 파일을 고치지 않고, 기획을 바꾸지 않으며, 승인하지 않는다.
---

<!-- 이 파일은 `romeo compile` 산출물이다. 직접 고치지 않는다 — 고칠 곳은 core/ 와 adapters/ 다. -->

# /review (Claude Code 어댑터)

절차의 원본은 `core/workflows/review/SKILL.md` 다. 이 파일은 그 절차를 Claude Code 에서 어떻게 수행하는지만 적는다.

<!-- romeo:managed start v0.1.0 source=adapters/claude/workflows/review.md sha=bc673d2f -->
1. `core/workflows/review/SKILL.md` 를 읽고 절차를 그대로 따른다. 이 파일은 그 절차의 Claude 매핑일 뿐이다.
2. 읽기 전용으로 실행한다 — Read·Grep·Glob 만 쓴다. 파일을 만들거나 고치거나 지우지 않고, 검사·빌드 같은 명령도 실행하지 않는다(역할 계약의 `capabilities` 는 읽기와 검색뿐이다).
3. 입력은 **자기 작업 루트 기준 상대 경로** `docs/work/<id>/task/<run-id>-reviewer.json` 이다 — 위임 실행이면 위임한 쪽이 그 자리에 만들어 둔 파일을 읽는다. 위임한 쪽 체크아웃의 절대 경로를 받았더라도 읽지 않고, 그 자리에 파일이 없으면 만들지 말고 `BLOCKED_CAPABILITY` 로 보고한다(쓰기 능력이 없다). 그 `base_sha` 가 같은 디렉터리의 `<run-id>-implementer.json` 의 `base_sha` 와 같아야 한다. 다르면 판정하지 않고 `BLOCKED_CAPABILITY` 로 보고한다.
4. 규율은 `.claude/skills/` 의 requesting-code-review · receiving-code-review 를 쓰되 산출물 경로는 `docs/work/<id>/` 다. 원문이 이름으로 지목하는 범용 서브에이전트를 띄우지 않고 역할 계약으로만 나간다(D-71 · `.harness/bindings.yaml` 의 `overrides.review_dispatch`). 다른 리비전이 필요하면 `orca worktree create` 로 요청하고 이 체크아웃은 건드리지 않는다.
5. findings 와 게이트 판정은 `core/schemas/result-envelope.json` 형식으로 출력한다. 파일로 남기는 것은 이 절차를 부른 쪽의 일이고, 경로는 `docs/work/<id>/review/<run-id>-reviewer.json` 이다. 봉투에 적는 경로는 전부 자기 작업 루트 기준 상대 경로다: `task_envelope_ref.path` 는 3번의 계약 경로, `evidence_ref` 는 `docs/work/<id>/evidence/<run-id>.yaml` 이다. 절대 경로를 적으면 종료 검사가 "저장소 밖" 으로 거부한다.
6. 방어 검사(검토자 실행 전후의 작업 트리 비교)는 **이 절차를 부른 쪽**이 증거 기록 명령으로 돌린다. 검토자는 명령을 실행하지 않는다 — 자기가 만든 산출물로 자기 판정의 유효성을 증명할 수 없다(`core/workflows/review/SKILL.md` 6번).
7. 게이트 판정은 `core/workflows/review/SKILL.md` 의 **「무엇이 FAIL 사유인가」** 절이 열거한 목록으로만 낸다 — 그 절에 없는 이유로 `FAIL` 을 내지 않고, 그 절이 FAIL 이라고 한 것을 경고로 낮추지 않는다. 판정이 갈렸던 자리가 여기다(Q-10 (a)). 목록은 코어에만 있고 이 파일은 그것을 복제하지 않는다 — 두 런타임이 같은 목록을 본다.
<!-- romeo:managed end -->
