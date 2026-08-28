---
name: implement
description: 승인된 Tech Spec 을 작업 계약으로 바꿔 구현하고 증거를 남긴다. 승인이 끝난 작업 단위를 실제로 구현할 때 라우터가 켤 때만 쓴다 — 스스로 켜지지 않는다. 기획을 다시 만들지 않고, 스스로 검토하지 않으며, 승인 없이 되돌리기 어려운 작업을 하지 않는다.
---

<!-- 이 파일은 `romeo compile` 산출물이다. 직접 고치지 않는다 — 고칠 곳은 core/ 와 adapters/ 다. -->

# /implement (Claude Code 어댑터)

절차의 원본은 `core/workflows/implement/SKILL.md` 다. 이 파일은 그 절차를 Claude Code 에서 어떻게 수행하는지만 적는다.

<!-- romeo:managed start v0.1.0 source=adapters/claude/workflows/implement.md sha=d4448e21 -->
1. `core/workflows/implement/SKILL.md` 를 읽고 절차를 그대로 따른다. 이 파일은 그 절차의 Claude 매핑일 뿐이다.
2. 승인 확인은 `docs/work/<id>/spec.md` 의 `status`·`approved_at` 으로 한다. 하나라도 없으면 구현하지 않고 `BLOCKED_APPROVAL` 로 보고하고 멈춘다.
3. 작업 계약은 손으로 쓰지 않는다. `bin/romeo envelope build --unit <id> --role implementer --base-sha <승인 커밋 SHA> --run <run-id>` 가 만들고, 결과는 **자기 작업 루트 기준 상대 경로** `docs/work/<id>/task/<run-id>-implementer.json` 이다. 위임 실행이면 그 상대 경로를 읽고, 그 자리에 아직 없으면 같은 명령으로 만든다 — 같은 입력이면 바이트까지 같은 계약이라 위임한 쪽이 만든 것과 같은 파일이다. 위임한 쪽 체크아웃의 절대 경로는 받았더라도 읽지 않고 봉투에도 적지 않는다.
4. 규율 부품은 `.claude/skills/` 의 test-driven-development · systematic-debugging · verification-before-completion · using-git-worktrees 중 라우터가 켠 것만 쓴다. 부품이 실행 순서를 정하지 않는다. 원문이 이름으로 지목하는 내장 worktree 도구는 쓰지 않고 `orca worktree create` 로 대체한다(D-71 · `.harness/bindings.yaml` 의 `overrides.worktree`).
5. 가드 승인은 AskUserQuestion 한 번으로 받고 `bin/romeo evidence approve --unit <id> --guard <가드> --by <사용자> --run <run-id>` 로 기록한다. 기록 전에는 상태를 바꾸지 않는다.
6. 검사는 `bin/romeo evidence checks --unit <id> --run <run-id>` 로 돌린다. 단건은 `bin/romeo evidence run --unit <id> --run <run-id> --label <이름> -- <명령>` 이다. 손으로 쓰지 않는다. 위임 실행이면 `--task-id`·`--dispatch-id` 도 같은 run 에 남긴다.
7. 결과 계약은 `core/schemas/result-envelope.json` 형식으로 `docs/work/<id>/result/<run-id>-implementer.json` 에 **스스로** 쓴다 — 회수해 주는 쪽이 없다. 봉투에 적는 경로는 전부 자기 작업 루트 기준 상대 경로다: `task_envelope_ref.path` 는 3번의 계약 경로, `evidence_ref` 는 `docs/work/<id>/evidence/<run-id>.yaml` 이다. 절대 경로를 적으면 종료 검사가 "저장소 밖" 으로 거부한다. `checks` 와 증거가 어긋나면 증거를 따른다.
<!-- romeo:managed end -->
