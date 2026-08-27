---
name: plan-close
description: Romeo 종료 검사. docs/work/<id>/ 작업 단위의 evidence 신선도(HEAD SHA·작업 트리)·required_checks·수용 기준·open loop·링크를 검사해 통과하면 status 를 done 으로 확정한다. 사용자가 "/plan-close", "이 작업 마무리해", "완료 처리해줘", "close 해줘"라고 할 때 사용한다. 검사가 실패하면 완료라고 하지 않는다.
---

# /plan-close (Claude 어댑터)

공통 본문은 `core/workflows/plan-close/SKILL.md` 다. M2 에서 `romeo compile` 산출물로 대체된다.

<!-- romeo:managed start v0.1.0 source=core/workflows/plan-close/SKILL.md (M1 수동 배치) -->

1. `core/workflows/plan-close/SKILL.md` 를 읽는다.
2. 증거는 반드시 `bin/romeo evidence run --unit <id> --label <check-id> -- <명령>` 으로 만든다. Spec 의 `required_checks` 명령 문자열과 **정확히 같은** 명령을 실행한다.
3. 실행 가드(삭제·배포·외부 전송 등)가 걸린 단위는 사용자 승인을 AskUserQuestion 으로 받고 `bin/romeo evidence approve --unit <id> --guard <guard-id> --by <사용자>` 로 기록한다.
4. `bin/romeo close --unit <id> --dry-run` 으로 먼저 보고, 실패 항목을 고친 뒤 `bin/romeo close --unit <id>` 를 실행한다.
5. 보고 형식: 통과/실패 항목, 미검증 항목, 남은 위험, 다음 우선 작업. 실행 자체를 완료라고 말하지 않는다.

<!-- romeo:managed end -->
