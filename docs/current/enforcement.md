# 지금 이 저장소가 집행하는 판정 목록

> 갱신 2026-09-09 · `bin/romeo integrity` 가 이 목록과 코드를 대조한다.

이 한 장을 읽으면 **이 저장소가 지금 무엇을 막고 무엇을 경고하는지** 알 수 있다.
`docs/planning/` 이 «앞으로 무엇을 할 것인가» 라면 `docs/current/` 는 «지금 무엇이 참인가» 다 —
끝난 사실만 여기로 올라온다.

**이 목록은 손으로 쓰고 기계가 대조한다.** `bin/romeo integrity` 가 아래 표와 코드·정책표를
`(판정 id, 수준)` 쌍으로 대조해 한쪽에만 있는 것을 인쇄하고 종료 코드 1 을 낸다.
코드에서 이 문서를 **생성하지 않는** 이유는 그 반대다 — 생성한 목록은 코드의 사본이라 어긋날 수 없고,
어긋날 수 없는 것은 아무것도 알리지 않는다. 어긋남을 볼 수 있게 두는 것이 이 문서가 하는 일이다.

- **수준 `error`** — 어기면 판정이 서지 않는다. 종료 검사에서는 done 이 선언되지 않고, 문서 검증에서는 종료 코드가 1 이 되며, 차단에서는 그 사건 자체가 거부된다.
- **수준 `warning`** — 인쇄하고 넘어간다. 종료 코드를 바꾸지 않는다(K-31).

## 집행하는 판정

| 판정 id | 무엇을 보는가 | 수준 | 출처 |
| --- | --- | --- | --- |
| `capability-probed` | 「능력 확인」 표가 프로브가 실제로 낸 값과 같은가 | error | `core/policy/packages.yaml` |
| `discovery-result` | 조사 계획이 사는 문서의 inputs: 에 조사 산출물 링크가 실재하는가 | error | `core/policy/packages.yaml` |
| `milestone-plan` | charter.md 의 「마일스톤 계획」 절이 채워져 있는가 | error | `core/policy/packages.yaml` |
| `risk-plan-ready` | spec.md 의 「위험·백업·복구」 절이 채워져 있는가 | error | `core/policy/packages.yaml` |
| `spec-ready` | 확인란이 NEEDS_INPUT 없이 채워지고 수용 기준이 1건 이상인가 | error | `core/policy/packages.yaml` |
| `AC_ALL_CHECKED` | 확인란의 수용 기준 체크박스가 전부 채워졌는가 | error | `romeo/close.py` |
| `AC_TEXT_UNCHANGED` | 확인란의 문장이 승인 커밋과 같은가 (체크 표시는 다를 수 있다) | error | `romeo/close.py` |
| `APPROVAL_CHAIN` | 승인 이력이 기계가 대조할 수 있는 형태인가 | warning | `romeo/close.py` |
| `APPROVED` | status 가 active 이고 approved_at 이 있는가 | error | `romeo/close.py` |
| `BASE_SHA` | 결과 계약이 가리킨 작업 계약의 base_sha 가 이 이력의 조상인가 | error | `romeo/close.py` |
| `BLOCK_SATISFIED` | 라우터가 건 차단이 실제로 충족됐는가 | error | `romeo/close.py` |
| `CHECK_PLAN_COMMITTED` | 지금 읽는 검증 계획이 승인 커밋의 것과 같은가 | error | `romeo/close.py` |
| `DOC_WARNING` | 문서 검증이 낸 경고를 종료 검사의 자리에 옮겨 인쇄한다 | warning | `romeo/close.py` |
| `ENVELOPE_VALID` | 결과 계약이 스키마·작업 단위·역할에 맞는가 | error | `romeo/close.py` |
| `EVIDENCE_ANCHORED` | 결과 계약이 가리킨 증거가 이 작업 단위 안에 실재하는가 | error | `romeo/close.py` |
| `EVIDENCE_LOG` | 증거의 명령이 원시 로그·log_sha256 과 일치하는가 | error | `romeo/close.py` |
| `EVIDENCE_SELECTED` | 검증 계획을 전부 실행한 run 이 있는가 | error | `romeo/close.py` |
| `FRESH_HEAD` | 증거의 head_sha 가 지금 HEAD 인가 | error | `romeo/close.py` |
| `FRESH_TREE` | 증거의 작업 트리 해시가 지금 트리와 같은가 | error | `romeo/close.py` |
| `FRONTMATTER_VALID` | 문서 검증이 오류를 내지 않는가 | error | `romeo/close.py` |
| `GUARD_APPROVED` | 되돌리기 어려운 실행에 설명을 채운 승인 기록이 있는가 | error | `romeo/close.py` |
| `HAS_CHANGE` | 증거의 changed_files 가 비어 있지 않은가 | error | `romeo/close.py` |
| `HAS_EVIDENCE` | evidence/*.yaml 이 하나라도 있는가 | error | `romeo/close.py` |
| `HAS_REVIEW` | 검토자가 필요한 패키지에 review/*.json 이 있는가 | error | `romeo/close.py` |
| `JUDGE_REVISION` | 판정을 내리는 하네스 리비전이 승인 커밋의 것인가 | error | `romeo/close.py` |
| `NOT_ALREADY_DONE` | 이미 done 인 단위를 다시 닫으려 하는가 | error | `romeo/close.py` |
| `NO_OPEN_LOOP` | 문서 패키지 전체에 NEEDS_INPUT 이 남아 있지 않은가 | error | `romeo/close.py` |
| `REQUIRED_CHECK` | 검증 계획의 각 명령이 증거에 있고 종료 코드가 0 인가 | error | `romeo/close.py` |
| `REQUIRED_CHECK_RERUN` | 그 명령을 지금 다시 실행해도 같은 종료 코드인가 | error | `romeo/close.py` |
| `RERUN_NEAR_TIMEOUT` | 재실행 한 건이 상한 시간에 가까워졌는가 | warning | `romeo/close.py` |
| `REVIEW_FAIL_REASONS` | FAIL 판정이 fail_reasons 를 닫힌 목록의 코드로 담았는가 | error | `romeo/close.py` |
| `REVIEW_SAMPLE` | 현재 산출물에 대한 PASS 표본이 몇 건인가 | warning | `romeo/close.py` |
| `REVIEW_SUPERSEDED` | 다른 산출물이나 재승인 전 승인으로 낸 판정을 가려낸다 | warning | `romeo/close.py` |
| `REVIEW_VERDICT` | 지금 닫으려는 산출물에 대한 검토자 PASS 가 있는가 | error | `romeo/close.py` |
| `ROLE_CONTRACT` | 결과 계약이 주장한 것이 그 역할의 능력 범위 안인가 | error | `romeo/close.py` |
| `SPEC_UNCHANGED_SINCE_EVIDENCE` | spec.md 가 증거를 만든 뒤에 바뀌었는가 | warning | `romeo/close.py` |
| `TASK_ANCHORED` | 가리킨 작업 계약이 실재하고 다시 계산한 것과 바이트로 같은가 | error | `romeo/close.py` |
| `AC_UNIVERSAL` | 확인란의 수용 기준에 전칭 표현이 있는가 | warning | `romeo/validate.py` |
| `BROKEN_LINK` | 작업 단위 문서의 상대 링크 대상이 실재하는가 | error | `romeo/validate.py` |
| `BUDGET_EXCEEDED` | 문서 길이가 정책표의 예산을 넘었는가 | warning | `romeo/validate.py` |
| `CAPSULE_TOO_LONG` | Planning Capsule 절이 예산을 넘었는가 | warning | `romeo/validate.py` |
| `FRONTMATTER_INVALID` | frontmatter 가 스키마에 맞는가 | error | `romeo/validate.py` |
| `MISSING_SECTION` | 라우터가 요구한 절이 문서에 있는가 | error | `romeo/validate.py` |
| `OPEN_LOOP` | 문서에 NEEDS_INPUT 이 남아 있는가 | warning | `romeo/validate.py` |
| `POLICY_VERSION_CHANGED` | 문서가 기록한 정책표 판이 지금 판과 다른가 | warning | `romeo/validate.py` |
| `PROFILE_MISMATCH` | frontmatter 의 profile 이 정책표 재계산 결과와 같은가 | error | `romeo/validate.py` |
| `ROUTE_ERROR` | frontmatter 의 분류로 라우팅을 계산할 수 있는가 | error | `romeo/validate.py` |
| `STALE_BASE_SHA` | frontmatter 에 승인 커밋이 아닌 낡은 base_sha 가 남아 있는가 | warning | `romeo/validate.py` |
| `UNCHECKED_AC` | 미체크 수용 기준이 남아 있는가 | warning | `romeo/validate.py` |

## 파생 판정

리터럴 연결로 만들어지는 판정은 위 표에 없고 **대조 대상도 아니다.** 한 자리의 문자열만 봐서는
실제 id 를 알 수 없기 때문이다. 지금 있는 것은 하나다.

- `romeo/close.py` 의 `check("REVIEW_" + cid, …)` — 결과 계약 검사 다섯 가지(`ENVELOPE_VALID` ·
  `TASK_ANCHORED` · `BASE_SHA` · `EVIDENCE_ANCHORED` · `ROLE_CONTRACT`)를 검토자 봉투에 적용해
  `REVIEW_` 접두를 붙인 이름으로 등록한다. 규칙은 «`REVIEW_` + 표의 그 다섯 id» 이고,
  그 다섯은 위 표에 접두 없이 실려 있다.

## 범위

이 표가 덮는 자리는 넷이다 — `romeo/close.py` 의 `check("<id>"` 리터럴 호출과 `ENVELOPE_CHECKS` 튜플,
`romeo/validate.py` 가 `errors`/`warnings` 에 넣는 리터럴 접두, `core/policy/packages.yaml` 의 `blocks:` 키.
**그 밖의 자리에서 인쇄되는 이름은 이 표에 없다.** 지금 아는 것만 적는다.

- `romeo/docs.py` 의 승인 경고(`AC_UNREBUTTED`), `romeo/doctor.py` · `romeo/parity.py` · `romeo/provenance.py` 등이 내는 이름.
- `romeo/integrity.py` 자신이 인쇄하는 이름(`PROMOTION_DRIFT` · `BROKEN_LINK` · `DUPLICATE_UNIT_ID`).
- `core/policy/packages.yaml` 의 `warnings:` 카탈로그 — 그것은 메시지 문안이고 집행 자리가 아니다.
  거기 실린 이름 중 실제로 집행되는 것(`AC_UNIVERSAL` · `BUDGET_EXCEEDED`)은 위 표에 출처와 함께 있다.

넓히려면 `romeo/integrity.py` 의 뽑는 자리와 이 절을 **같은 커밋에서** 함께 고친다 —
요구하는 자리와 보는 자리를 같게 둔다(AGENTS.core §11).
