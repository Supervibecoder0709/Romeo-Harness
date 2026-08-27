1. `core/workflows/plan/SKILL.md` 를 읽고 절차를 그대로 따른다. 이 파일은 그 절차의 Codex 매핑일 뿐이다.
2. 제안은 `core/schemas/proposal.json` 형식의 YAML 로 `.harness/runs/plan/<slug>.proposal.yaml` 에 쓴다(git 제외).
3. 카드는 `bin/romeo card --proposal <파일>` 로 만든다.
4. **사람 확정**은 카드를 그대로 출력하고 한 번의 질문으로 받는다 — "제안대로 확정 / 단위 변경 / 깊이 변경 / 게이트 수정" 중 무엇인지 묻고, 답이 올 때까지 문서를 만들지 않는다. 사용자가 고치면 fixture 의 `human_correction` 에 기록한다.
5. `bin/romeo new --proposal <파일> --title ... --slug ...` 로 문서를 만들고 `NEEDS_INPUT` 을 채운다. `bin/romeo validate` 가 PASS 여야 한다.
6. 승인 요청은 **확인란만** 출력하고 사용자의 명시적 승인을 기다린다. 승인되면 `bin/romeo approve <id> --by <사용자>`.
7. `unit: none` 이면 문서를 만들지 않고 답변으로 끝낸다. 비코드 프로젝트면 `OUT_OF_SCOPE_NON_CODE` 를 그대로 보고한다.
