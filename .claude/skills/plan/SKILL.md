---
name: plan
description: Romeo 라우터. 새 요청을 받으면 사실·가정·미확인·분류 후보를 제안 카드로 정리하고, 사용자가 1클릭으로 확정하면 정책표로 문서 패키지를 계산해 docs/work/<id>/ 에 필요한 문서만 만든다. 사용자가 "/plan", "이 요청 분류해줘", "계획 잡아줘", "어떻게 진행할지 정해줘"라고 하거나 새 작업 요청을 가져올 때 사용한다. 구현은 하지 않는다.
---

# /plan (Claude 어댑터)

공통 본문은 `core/workflows/plan/SKILL.md` 다. 이 파일은 Claude Code 에서의 매핑만 적는다. M2 에서 `romeo compile` 산출물로 대체된다.

<!-- romeo:managed start v0.1.0 source=core/workflows/plan/SKILL.md (M1 수동 배치) -->

1. `core/workflows/plan/SKILL.md` 를 읽고 절차를 그대로 따른다.
2. 제안은 `core/schemas/proposal.json` 형식의 YAML 로 `.harness/runs/plan/<slug>.proposal.yaml` 에 쓴다(git 제외).
3. 카드는 `bin/romeo card --proposal <파일>` 로 만든다.
4. **사람 확정**은 AskUserQuestion 한 번으로 받는다 — 첫 옵션 "제안대로 확정(추천)", 나머지는 "단위 변경", "깊이 변경", "게이트 수정". 사용자가 고치면 fixture 의 `human_correction` 에 기록한다.
5. `bin/romeo new --proposal <파일> --title ... --slug ...` 로 문서를 만들고 `NEEDS_INPUT` 을 채운다. `bin/romeo validate` 가 PASS 여야 한다.
6. 승인 요청은 **확인란만** 보여주고 AskUserQuestion 으로 받는다. 승인되면 `bin/romeo approve <id> --by <사용자>`.
7. `unit: none` 이면 문서를 만들지 않고 답변으로 끝낸다. 비코드 프로젝트면 `OUT_OF_SCOPE_NON_CODE` 를 그대로 보고한다.

<!-- romeo:managed end -->
