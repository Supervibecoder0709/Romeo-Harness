1. `core/workflows/plan-close/SKILL.md` 를 읽고 절차를 그대로 따른다.
2. 증거가 없으면 시작하지 않는다. `bin/romeo evidence run --unit <id> -- <명령>` 또는 `bin/romeo evidence checks --unit <id>` 로 만든다. 손으로 쓰지 않는다.
3. 검사는 `bin/romeo close <id>` 가 한다. 실패 코드(FRESH_*·NO_EVIDENCE·UNCHECKED_AC·MISSING_CHECK)를 그대로 사용자에게 보고한다.
4. 실패를 우회하지 않는다. 실패한 검사 이름과 출력을 그대로 보여주고 다음 행동을 제안한다.
5. 통과하면 `status: done` 과 `closed_at` 이 기록된다. 결과 보고에는 실행한 명령과 종료 코드를 포함한다.
