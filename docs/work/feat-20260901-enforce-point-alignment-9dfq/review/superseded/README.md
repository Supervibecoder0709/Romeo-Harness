# 지난 회차의 검토 판정 — 지우지 않고 옮겨 둔다

여기 있는 봉투는 **1~3회차의 FAIL 판정**이다. 그 회차들은 `../../attempts.yaml` 에 `result: fail` 로
이미 기록됐고, 각 findings 를 무엇으로 고쳤는지도 거기 남아 있다.

**왜 `review/` 밖으로 옮겼나.** 종료 검사는 `review/*.json` 을 **지금 산출물에 대한 판정**으로 읽는다.
그런데 이 세 봉투는 판정 시점의 산출물을 증명하지 못한다 — 검토자를 띄운 쪽(코디네이터)이 그 run 들에
RUNBOOK §4 의 방어 검사 **두 개 중 `review-tree-before` 만** 남기고 `review-tree-after` 를 빠뜨렸기 때문이다.
그래서 `_reviewed_product` 가 산출물을 식별하지 못하고, 봉인 형식이라 옛 형식 우회로도 가지 않아
`REVIEW_VERDICT` 가 영구히 `UNVERIFIED` 가 된다 — **판정이 FAIL 이든 무엇이든 다음 close 를 막는다.**

지금 와서 `review-tree-after` 를 기록하면 **오늘의 트리**가 그때의 판정에 붙는다. 그것은 위조다(K-51).
없는 앵커를 만들지 않고, 이 봉투들이 무엇인지 적어 옮긴다.

**지우지 않는 이유.** 검토 판정은 동등성 게이트의 관측 표본이고(D-75), 이 세 건은 검토자가 실제 결함
8건을 잡은 기록이다. 판정 자체가 이 단위의 이력이다.

| 봉투 | 회차 | 판정 | 무엇을 잡았나 |
| --- | ---: | --- | --- |
| `run_9dfq01-reviewer.json` | 1 | FAIL · findings 5 | AC-9 가 기계가 셀 수 없는 spike 판정을 약속 · `mailto:` 구멍 · `allowed_paths` 밖 변경 6건 · check-9 이 문자열 존재만 검사 · 증거 `base_sha` 가 계약과 어긋남 |
| `run_9dfq02-reviewer.json` | 2 | FAIL · findings 2 | Q-29 해소문이 코드와 반대 · check-9 이 취소선 존재만 봐서 그것을 통과시킴 |
| `run_9dfq03-reviewer.json` | 3 | FAIL · findings 1 | 앵커만 있는 링크(`#section`)가 작업 단위 폴더 자신을 가리켜 조사 결과로 셈 |

4회차 판정(`../run_9dfq04-reviewer.json`)이 이 close 의 대상이고, 그 run 은 `review-tree-before`·`after` 를
모두 남겼다.

이 결함 자체는 `docs/planning/open-questions.md` 의 Q-35 로 열려 있다.
