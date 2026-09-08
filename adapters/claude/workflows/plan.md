1. `core/workflows/plan/SKILL.md` 를 읽고 절차를 그대로 따른다. 이 파일은 그 절차의 Claude 매핑일 뿐이다.
2. 제안은 `core/schemas/proposal.json` 형식의 YAML 로 `.harness/runs/plan/<slug>.proposal.yaml` 에 쓴다(git 제외).
3. 카드는 `bin/romeo card --proposal <파일>` 로 만든다.
4. **사람 확정**은 AskUserQuestion 한 번으로 받는다 — 첫 옵션 "제안대로 확정(추천)", 나머지는 "단위 변경", "깊이 변경", "게이트 수정". 사용자가 고치면 fixture 의 `human_correction` 에 기록한다.
5. `bin/romeo new --proposal <파일> --title ... --slug ...` 로 문서를 만들고 `NEEDS_INPUT` 을 채운다. `bin/romeo validate` 가 PASS 여야 한다.
6. **반박 읽기(절차 8)** 는 검토자 런타임의 읽기 전용 비대화형 실행으로 한다 — 기본 실행에서 이 런타임은 구현자이므로 검토자는 상대 런타임이다. 명령의 읽기 전용 강제는 `.harness/bindings.yaml` 의 검토자 `enforcement` 를 그대로 쓰고, 출력은 파일로 받아 `inputs/` 에 둔다:
   `codex exec -s read-only -C <저장소 루트> -o docs/work/<id>/inputs/ac-rebuttal-<YYYYMMDD>.md - < <(cat adapters/orca/prompts/ac-rebuttal-brief.md; sed -n '/^## 확인란/,/^## 변경 범위/p' docs/work/<id>/spec.md)`
   브리프의 `<id>` 를 실제 단위 id 로 바꾼다. 실행 전후 `git status --porcelain` 이 같은지 방어 검사한다.
7. 승인 요청은 **확인란만** 보여주고 AskUserQuestion 으로 받는다. 승인되면 `bin/romeo approve <id> --by <사용자>`.
8. `unit: none` 이면 문서를 만들지 않고 답변으로 끝낸다. 비코드 프로젝트면 `OUT_OF_SCOPE_NON_CODE` 를 그대로 보고한다.
