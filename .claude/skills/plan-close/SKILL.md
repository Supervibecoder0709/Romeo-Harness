---
name: plan-close
description: Romeo 종료 검사. docs/work/<id>/ 작업 단위의 evidence 신선도(HEAD SHA·작업 트리)·required_checks·수용 기준· open loop·링크를 검사해 통과하면 status 를 done 으로 확정한다. 사용자가 "/plan-close", "이 작업 마무리해", "완료 처리해줘", "close 해줘"라고 할 때 사용한다. 검사가 실패하면 완료라고 하지 않는다.
---

<!-- 이 파일은 `romeo compile` 산출물이다. 직접 고치지 않는다 — 고칠 곳은 core/ 와 adapters/ 다. -->

# /plan-close (Claude Code 어댑터)

절차의 원본은 `core/workflows/plan-close/SKILL.md` 다. 이 파일은 그 절차를 Claude Code 에서 어떻게 수행하는지만 적는다.

<!-- romeo:managed start v0.1.0 source=adapters/claude/workflows/plan-close.md sha=96d88f71 -->
1. `core/workflows/plan-close/SKILL.md` 를 읽고 절차를 그대로 따른다.
2. 증거가 없으면 시작하지 않는다. `bin/romeo evidence run --unit <id> -- <명령>` 또는 `bin/romeo evidence checks --unit <id>` 로 만든다. 손으로 쓰지 않는다.
3. 검사는 `bin/romeo close <id>` 가 한다. 실패 코드(FRESH_*·NO_EVIDENCE·UNCHECKED_AC·MISSING_CHECK)를 그대로 사용자에게 보고한다.
4. 실패를 우회하지 않는다. "거의 됐다"는 완료가 아니다 — 실패한 검사 이름과 출력을 그대로 보여주고 다음 행동을 제안한다.
5. 통과하면 `status: done` 과 `closed_at` 이 기록된다. 결과 보고에는 실행한 명령과 종료 코드를 포함한다.
<!-- romeo:managed end -->
