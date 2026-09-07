---
id: feat-20260907-close-review-reapproval-reach-bjec
type: spec
title: 재승인이 닿지 않던 자리를 연다 — 산출물을 식별하지 못한 봉투도 승인 키는 읽는다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: active
approved_at: '2026-09-07T10:08:21+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-07'
updated: '2026-09-07'
approval_history:
- {approved_at: '2026-09-07T09:45:47+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-07T10:08:21+09:00',
  reason: AC-1 이 실물 봉투의 계약·원시 로그를 요구했는데 둘 다 .gitignore 대상이라 그 run 을 돌린 워크트리 밖에서는 존재하지 않는다 — 어느 구현으로도 만족시킬
    수 없는 환경 의존 기준이었다. 봉투 바이트를 픽스처에 넣는 형태로 바꾸고 check-10 을 더한다}
---

# 재승인이 닿지 않던 자리를 연다 — 산출물을 식별하지 못한 봉투도 승인 키는 읽는다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260907-close-review-reapproval-reach-bjec --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 종료 검사가 검토 판정을 낡은 것으로 가려내는 규칙을 **산출물을 식별하지 못한 봉투에도** 적용한다.
  지금은 그 봉투가 먼저 「미검증」으로 걸려 재승인을 보는 자리에 닿지 못한다. 낡은 것으로 분류하려면
  그 봉투가 기록된 그대로여야 한다는 조건을 함께 건다.
- **왜 지금:** 2026-09-06 관통에서 이 결함이 실제로 작동했다 — 3회차가 검토 PASS 를 받고 재승인까지 했는데도
  닫히지 않아 봉투를 손으로 빼내야 했다. 다음은 M5 attach 관통이고 그 관통도 회차를 돌면 같은 자리를 지난다.
  관통 도중에는 하네스를 고칠 수 없으므로(§10 동결) 관통 사이인 지금 닫는다.
- **기대 결과:** 사람이 재승인한 뒤에는 이전 승인으로 낸 검토가 완료를 막지 않는다. 그 봉투는 지워지지 않고
  경고로 인쇄된다. **지금 승인의 검토는 그대로 막는다** — 차단을 걷는 것은 사람의 재승인뿐이다.
- **수용 기준:**
  - [ ] AC-1 재승인 전 승인으로 **정식 기록된** 검토 봉투는, 방어 검사가 깨져 어느 산출물을 봤는지 확인할 수
        없더라도 `REVIEW_SUPERSEDED`(경고)로 인쇄되고 완료를 막지 않는다. 합성 픽스처와, 2026-09-06 관통이
        실제로 낸 봉투의 **바이트 그대로**를 픽스처에 넣은 검사 양쪽으로 보인다 — 그 봉투의 작업 계약과
        원시 로그는 그 run 을 돌린 워크트리에만 있고 둘 다 커밋되지 않으므로(`.gitignore`), 주변 환경은
        픽스처가 만든다. 실물 판정 문자열·`findings`·포인터가 이 분류를 지나는 것이 이 기준이 보는 것이다.
  - [ ] AC-2 그 봉투 파일은 지워지지 않고 `review/` 에 그대로 남으며, 인쇄에 판정·findings 건수·「재승인 전 승인」
        문구가 들어간다.
  - [ ] AC-3 **지금 승인**의 봉투는 산출물을 확인할 수 없으면 그대로 완료를 막는다.
  - [ ] AC-4 재승인만으로는 닫히지 않는다 — 지금 산출물에 대한 검토가 하나도 없으면 여전히 미검증이다.
  - [ ] AC-5 현재 승인으로 정식 기록된 판정에서 **계약 포인터 한 필드만** 옛 계약으로 바꾼 봉투는 낡은 것으로
        분류되지 않는다. 그 편집은 지금 코드에서는 막히는데 이 변경만 넣으면 통과하므로, 봉인 조건이 그것을 되막는다.
  - [ ] AC-6 기록이 없거나(손으로 쓴 봉투) 원시 로그를 대조하지 못한 재승인 전 봉투는 낡은 것으로 분류되지 않고,
        차단 사유에 봉인 대조 결과가 덧붙어 **재승인이 왜 듣지 않았는지**가 인쇄된다.
  - [ ] AC-7 기존 검사를 하나도 고치지 않고 전부 통과한다(수정 전 904건 → 추가 후 909건).
  - [ ] AC-8 요구가 사는 문서와 집행이 **같은 커밋**에 있다 — 종료 검사 절차 문서에 이 예외가 인쇄된다.
  - [ ] AC-9 이번 조사가 발견했으나 고치지 않은 결함이 `docs/planning/open-questions.md` 에 열린다.
- **위험과 되돌리기:** 이 변경은 종료 검사가 **막는 범위를 줄인다** — 재승인 뒤에는 이전 승인의 깨진 검토가
  완료를 막지 않는다. 완화 폭은 좁다: 낡은 것으로 분류된 판정은 통과로 세지 않고, 봉투는 지워지지 않으며,
  재승인은 사람만 할 수 있는 행위다. 되돌리기는 `git revert <이 단위의 통합 커밋>` — 외부 상태를 바꾸지 않는다.
- **결정 필요:** 없음 — 봉인 조건을 함께 건다(`is True`). 실측으로 확정했다.


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/close.py` · `tests/test_docs_evidence_close.py` · `core/workflows/plan-close/SKILL.md` · `docs/planning/open-questions.md` · `docs/planning/progress.md` · `docs/work/feat-20260907-close-review-reapproval-reach-bjec/` · `.claude/skills/plan-close/SKILL.md` · `.agents/skills/plan-close/SKILL.md` · `.harness/compiled.yaml` (뒤 셋은 컴파일 산출물 보험 — 코어 본문만 고치면 재생성이 필요 없음을 확인했으나 재생성이 필요해질 경우를 위해 상한에 둔다)
- 영향을 받는 부분: `romeo close` 의 검토 판정 인쇄(`REVIEW_VERDICT`·`REVIEW_SUPERSEDED`). 다른 검사·다른 명령의 판정은 바뀌지 않는다.
- 바꾸지 않는 것(비범위): `romeo/evidence.py`(`record_review_envelope`·`review_record_state`) · `_check_review` 의 기존 낡음 분기(산출물이 식별되는 봉투 경로) · `_reviewed_product` 의 산출물 식별 규칙 · `_legacy_head` 의 옛 형식 판정 · `adapters/orca/RUNBOOK.md` · 다른 열린 질문(Q-64·Q-69·Q-70)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 재승인 전 승인의 봉투를 산출물 식별 실패보다 먼저 낡은 것으로 분류하되, 기록된 그대로인 봉투만 그렇게 한다 | `romeo/close.py` 의 `_check_review` 안 봉투 분류 루프에서 `unknown.append((n, e, why))` **바로 앞**에 분기를 넣는다. `_envelope_approval_key` 로 봉투 계약의 `base_sha` 가 담은 승인을 읽어 현재 승인과 다르면, 그 검토 run 의 증거를 **산출물 식별과 무관하게 따로 로드**해 `review_record_state(..., product=None)` 가 `is True` 일 때만 `stale` 로 보낸다. `True` 가 아니면 기존대로 `unknown` 으로 떨어뜨리되 `why` 에 봉인 대조 결과를 덧붙인다. import 추가 없음 — 쓰는 이름이 전부 그 모듈에 이미 있다 | 소비: 없음 → 생산: `stale` 항목의 사유 문자열(`산출물을 확인하지 못했지만(…) 재승인 전 승인(approved_at …)으로 낸 판정`)과 `unknown` 사유의 `· 봉인 대조: …` 접미 | check-1·check-2·check-3·check-4·check-5 | `git revert` |
| 2 | 그 규칙이 사는 문서가 같은 커밋에서 참이 된다 | `core/workflows/plan-close/SKILL.md` 의 종료 검사 검토 절에서 「산출물을 확인할 수 없는 봉투가 있으면 미검증」 문장 뒤에 예외 세 문장을 넣는다 — ① 계약이 담은 승인이 지금 승인과 다르고 봉투가 기록된 그대로면 `REVIEW_SUPERSEDED` 로 인쇄한다 ② 승인 키는 산출물과 무관하게 읽는다 ③ 지금 승인의 봉투는 산출물을 확인할 수 없으면 그대로 미검증이다. 도구명·모델명을 쓰지 않는다(C-C6). frontmatter 의 `description:` 은 건드리지 않는다 | 소비: 1번이 만든 인쇄 규칙 → 생산: 없음 | check-6·check-7 | `git revert` |
| 3 | 판별 검사와 회귀 방지 검사를 `tests/test_docs_evidence_close.py` 에 더한다 | `TestCloseReviewVerdict` 에 검사 5건을 추가한다. 기존 헬퍼(`setUp`·`_defensive`·`_envelope`·`_write_review`)를 그대로 쓰고 **기존 검사는 한 줄도 고치지 않는다**. 단언은 판정 문자열이 아니라 검사 id·`level`·분류로 한다 | 소비: 1번의 분기 → 생산: 검사 5건 | check-1~check-5·check-8 | 해당 검사만 되돌린다 |
| 4 | 이번 조사가 발견했으나 고치지 않은 것을 연다 | `docs/planning/open-questions.md` 의 Q-68 행을 해소 표기(취소선 + 「해소(2026-09-07, <이 단위 id>)」 + **닫지 않은 것**)로 바꾸고, 새 질문 7건을 추가한다. Q-68 행 마지막 근거 열의 `feat-20260906-m3-close-foreign-repo-ik3u` 문자열은 **지우지 않는다**(다른 검사가 그 문자열로 출처 집합을 만든다). 새 행의 어느 칸에도 M1~M3 관통 단위 id 3개를 쓰지 않는다. `docs/planning/progress.md` 의 「지금 상태」 블록을 갱신한다 | 소비: 없음 → 생산: 없음 | check-9 | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 페이로드(하네스를 부착한 프로젝트) 작업 단위의 `required_checks` 에
**하네스 자신의 테스트**를 넣지 않는다 — `python3 -m unittest discover -s tests`(하네스 저장소의 테스트),
`bin/romeo` 의 자기 검사(`compile --check` · `validate` · `doctor` · `fixtures …`)가 그것이다.
넣으면 하네스가 깨진 동안 그 페이로드 단위가 닫히지 못한다. 그 단위의 산출물은 멀쩡한데 완료가 서지 않는 것이고,
그때 고쳐야 할 것은 그 단위가 아니라 하네스다 — 두 판정을 한 검사에 묶으면 어느 쪽이 깨졌는지 구분되지 않는다
(근거: `feat-20260829-license-field-46an` 의 check-5 가 이 형태였다).
하네스 저장소 **자신**을 대상으로 하는 작업 단위에서는 그 검사들이 정당하다 — 그때는 그것이 이 단위의 산출물이기 때문이다.

**종료 코드 자체가 조건이다.** 검사에 적는 것은 `id` 와 `command` 둘뿐이고, 그 명령의 종료 코드 0 이 통과다.
기대를 문장으로 따로 적는 자리는 두지 않는다 — 사람은 그것을 조건으로 쓰는데 기계는 판정에 쓰지 않으므로,
그 검사는 무엇을 확인하는지 적혀 있는 채로 아무것도 확인하지 않는 **빈 검사**가 된다(2026-08-31 실측으로 제거).
확인하고 싶은 조건이 있으면 그 조건을 **명령으로** 쓴다.
같은 이유로 옵션이 판정을 만드는 명령은 그 옵션까지 적는다 — 예: `bin/romeo doctor` 는 옵션 없이 쓰면 항상 exit 0 이라 빈 검사이고,
부착 검증(K-68)을 실제로 판정하게 하려면 `bin/romeo doctor --strict --scope repository` 로 쓴다(Q-21).

그래서 `|| true` 를 붙이지 않는다 — 종료 코드를 항상 0 으로 만들어 위반을 통과시킨다.
부정 조건은 `!` 로 쓴다: `! grep -q '<있으면 안 되는 것>' <파일>`.

**판별 검사와 회귀 방지 검사의 구분** — §11 은 「어느 쪽인지는 검증 계획에 적는다, 적지 않으면 전부 판별 검사로 본다」고 한다.
**판별 검사는 check-1·check-2·check-10 셋뿐**이고 승인 전에 기존 상태·가상 완료 상태 양쪽에서 실행해 각각 실패·통과를 보였다.
check-3~check-9 는 **회귀 방지 검사**이므로 양쪽 실측 대상이 아니다 — 양쪽에서 통과하는 것이 그 검사의 정의다.
다만 check-4·check-5 가 빈 검사가 아니라는 증거는 따로 있다: 봉인 조건을 뺀 중간 상태에서 **실패한다**(실측).

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_docs_evidence_close.TestCloseReviewVerdict.test_a_recorded_verdict_under_a_superseded_approval_is_superseded_even_when_its_product_is_unreadable"
  - id: check-2
    command: "python3 -m unittest tests.test_docs_evidence_close.TestCloseReviewVerdict.test_a_reapproval_alone_does_not_close_a_unit_whose_only_verdict_is_unidentifiable"
  - id: check-3
    command: "python3 -m unittest tests.test_docs_evidence_close.TestCloseReviewVerdict.test_an_unidentifiable_verdict_of_the_current_approval_still_blocks"
  - id: check-4
    command: "python3 -m unittest tests.test_docs_evidence_close.TestCloseReviewVerdict.test_retargeting_the_task_ref_cannot_make_a_current_fail_look_superseded"
  - id: check-5
    command: "python3 -m unittest tests.test_docs_evidence_close.TestCloseReviewVerdict.test_an_unrecorded_verdict_under_a_superseded_approval_stays_unverified"
  - id: check-6
    command: "grep -q 'REVIEW_SUPERSEDED' core/workflows/plan-close/SKILL.md"
  - id: check-7
    command: "bin/romeo compile --check"
  - id: check-8
    command: "python3 -m unittest discover -s tests -q"
  - id: check-9
    command: "python3 -m unittest tests.test_attach_requirements tests.test_enforce_points"
  - id: check-10
    command: "python3 -m unittest tests.test_docs_evidence_close.TestCloseReviewVerdict.test_the_real_2026_09_06_envelope_is_superseded_after_a_reapproval"
```

**각 검사가 무엇을 보는가**

| id | 종류 | 무엇이 참이어야 통과인가 | 반례(그럴듯한 거짓 값) |
| --- | --- | --- | --- |
| check-1 | **판별** | 방어 검사가 무효(검토 전후 산출물이 다름)라 산출물을 식별하지 못하지만 정식 기록된 **재승인 전** FAIL 봉투가, 지금 산출물에 유효한 PASS 가 있을 때 `REVIEW_SUPERSEDED`(warning)로 인쇄되고 close verdict 가 PASS 이며 미검증 0건이다 | 두 방어 라벨이 **다 있고** 각각 원시 로그 봉인이 맞고 명령별 산출물 식별도 있는데, 그 사이에 커밋이 들어가 값만 다르다 — 빈 값이 아니라 2026-09-06 관통이 실제로 낸 모양이다 |
| check-2 | **판별** | 재승인만으로는 닫히지 않는다 — 지금 산출물에 대한 판정이 하나도 없으면 `REVIEW_VERDICT` 가 미검증이고 사유가 「검토가 아직 없다」로 바뀐다 | check-1 과 같은 거짓 값에, 그 봉투의 판정이 **PASS** 이고 재승인 뒤 새 검토를 하지 않은 상태 — 「재승인 전 PASS 가 현재 판정으로 새는가」를 묻는다 |
| check-3 | 회귀 방지 | **지금 승인**의 미식별 봉투는 그대로 `REVIEW_VERDICT` 를 미검증으로 만들어 막는다 | — (양쪽 통과) |
| check-4 | 회귀 방지 | 현재 승인으로 정식 기록된 정직한 FAIL 에서 **계약 포인터 한 필드만** 옛 계약으로 바꾼 봉투가 낡은 것으로 분류되지 않는다 | — (양쪽 통과. 봉인 조건을 뺀 중간 상태에서는 **실패한다** — 그것이 이 검사가 비어 있지 않다는 증거다) |
| check-5 | 회귀 방지 | 기록이 없는(손으로 쓴) 재승인 전 봉투는 봉인이 서지 않아 낡은 것으로 분류되지 않는다(K-51) | — (양쪽 통과. 봉인 조건을 `is not False` 로 느슨하게 잡은 중간 상태에서 **실패한다**) |
| check-6 | 회귀 방지 | 요구가 사는 문서에 이 예외가 인쇄돼 있다 | — |
| check-7 | 회귀 방지 | 코어 본문 변경이 컴파일 산출물과 어긋나지 않는다 | — |
| check-8 | 회귀 방지 | 기존 검사가 하나도 깨지지 않는다(904 → 909) | — |
| check-9 | 회귀 방지 | 문서 편집이 출처 집합 대조·해소 표기 대조를 깨지 않는다 | — |
| check-10 | **판별** | 2026-09-06 관통이 낸 봉투의 **바이트 그대로**(판정·`findings`·포인터)가 픽스처가 세운 환경에서 `REVIEW_SUPERSEDED` 로 분류된다 | 합성한 이상적 봉투가 아니라 실제로 그 사고를 낸 봉투다 — 그 봉투의 계약·증거·원시 로그는 커밋되지 않으므로 픽스처가 만들고, 봉투 본문만 실물을 쓴다 |

**재실행 시간** — check-8 이 약 130초, 나머지는 각 1~4초다. `romeo close` 의 재실행 상한 600초 안이다.


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
