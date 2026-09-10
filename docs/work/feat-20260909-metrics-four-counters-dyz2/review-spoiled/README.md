# 손상된 검토 봉투 — 지우지 않고 여기 보관한다

`run_85a3e6bebe47-reviewer.json` (2회차 검토자 · **PASS · findings 0**)

## 왜 `review/` 밖에 있나

이 봉투 자체에는 결함이 없다. 그것이 **가리키는 증거**(`evidence/run_85a3e6bebe47.yaml`)가
검토가 봉인된 **뒤에** 오염됐다.

2회차 워커의 dispatch(`ctx_396c4aad204d`)가 `worker-stop` 에 응하지 않은 채 살아 있었고,
위임한 쪽이 워크트리를 `7e180a2` → `926d65a` 로 ff 한 뒤에 그 워커가 같은 run 에
`check-1`·`check-2`·`check-3` 을 다시 기록했다. 그래서 그 run 의 증거가 두 head 에 걸친다:

| 자리 | head |
| --- | --- |
| `review-tree-before` · `review-tree-after` · `review-record` | `7e180a2ed0b4` |
| run 레벨(마지막 명령의 값) | `926d65aade2d` |

`romeo close` 는 검토 봉투가 본 산출물을 **검토 run 의 자기-증거**에서 읽는데(체크리스트 45),
그 둘이 어긋나므로 「판정이 본 산출물을 확인할 수 없다」로 `REVIEW_VERDICT` 를 UNVERIFIED 로 둔다.
`unknown` 이 하나라도 있으면 현재 산출물의 PASS 가 있어도 판정이 서지 않는다(`romeo/close.py` 의 REVIEW_VERDICT 분기).

## 무엇도 숨기지 않는다

- 이 판정은 **PASS** 다 — FAIL 을 감추려고 옮긴 것이 아니다.
- 이 검토자가 본 트리는 `17266bb65236` 이고, **3회차가 close 한 트리와 같은 값**이다.
- 3회차 검토자(`review/run_f93b869a890d-reviewer.json`)도 같은 트리에 **PASS · findings 0** 을 냈다.
- 1회차 판정(`review/run_cf5998614e4c-reviewer.json` · FAIL findings 2)은 `review/` 에 그대로 있고,
  close 가 `REVIEW_SUPERSEDED` 로 「다른 산출물을 본 판정」이라고 인쇄한다.

## 드러난 하네스 결함

**settle 된 회차의 워커가 살아 있으면 봉인된 run 의 증거를 오염시킬 수 있고, 그 오염은 되돌릴 수 없다.**
`worker-stop` 이 `Dispatch ... is not stopping` 으로 거부했고, 절차의 어느 자리도 그 뒤의 쓰기를 막지 않는다.
`docs/planning/open-questions.md` 에 연다 — 이 단위가 고칠 문제가 아니다(§12).
