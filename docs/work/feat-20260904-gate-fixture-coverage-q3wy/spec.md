---
id: feat-20260904-gate-fixture-coverage-q3wy
type: spec
title: hard gate 8 커버리지를 fixture 와 검사로 채운다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
status: done
approved_at: '2026-09-04T05:53:23+09:00'
approved_by: julliettelee
base_sha: null
closed_at: '2026-09-04T06:10:28+09:00'
parent: null
inputs: []
evidence: [evidence/run_dd07b98f3f83.yaml, evidence/run_60db3d61480b.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-04'
updated: '2026-09-04'
approval_history:
- {approved_at: '2026-09-04T02:01:26+09:00', approved_by: julliettelee, superseded_at: '2026-09-04T05:53:23+09:00',
  reason: AC-2 가 사후 관측이 불가능한 시간 순서(route 보다 먼저 적었다)를 요구해 1회차 검토자가 AC_UNMET 을 냈다. 자기참조를 끊는 자리를 시간 순서에서
    사람의 확인(human_correction)으로 옮긴다. 5건의 분류·expected 는 2026-09-04 사용자가 확정했다.}
---

# hard gate 8 커버리지를 fixture 와 검사로 채운다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260904-gate-fixture-coverage-q3wy --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** hard gate 8 중 fixture 가 0건인 5개(payment·legal·ops-data-deletion·public-api·irreversible-policy)에 요청 fixture 를 1건씩 추가하고, 「8개 각각 ≥ 1」과 「fixture 의 게이트 id 가 정책표 안의 id 인가」를 정책표에서 읽어 대조하는 검사를 붙인다.
- **왜 지금:** 계획 §10 #13 의 M3 종료 조건은 두 개인데 「시나리오 3·8·9 런북 PASS」만 충족됐고 나머지 절반이 남았다. 지금 8개 중 3개(privacy-security 5 · migration 2 · availability 1)만 fixture 가 있다. 게이트 발동 경로가 fixture 로 고정돼 있지 않으면 다음 T2 관통이 그 경로를 타면서 분류 기준을 즉석에서 만들게 되고, 그것은 §10 동결 위반이다.
- **기대 결과:** `bin/romeo route --fixtures fixtures/requests --report` 가 38건 전부 일치로 exit 0 이고, 게이트 커버리지 검사가 8개 전부 ≥ 1 을 확인한다. 계획 §10 #13 이 닫힌다.
- **추가할 fixture 5건 (요청 원문과 출처):** 사용자가 승인과 함께 이 분류를 확정한다. 확정 사실은 각 fixture 의 `human_correction` 에 기록한다.

  | # | 게이트 | 요청 | 출처 |
  | --- | --- | --- | --- |
  | 1 | payment | 「lifetime 결제자랑 subscribe 결제자 숫자도 사인업이랑 대화 2회 이후 스키마 사이에 추가해줄 수 있어? 환불이나 구독 취소는 고려 안 해도 돼」 | **실제** — 닥터테일 데이터 분석 세션 `f95922ee` (2026-07-07) |
  | 2 | legal | 랜딩 이메일 수집 폼에 개인정보 수집·이용 동의 문안과 체크박스를 넣고, 동의 없이는 제출되지 않게 한다 | **authored** — ordi 랜딩 세션 `20a7db24` 에 「동의 문안 건만 요청한대로 반영」이 있으나 그 요청 **원문이 로그에 없다**. 맥락만 실제이고 문장은 새로 썼다 |
  | 3 | ops-data-deletion | 테스트로 만든 계정·주문 데이터를 운영 DB 에서 지운다 | **authored** — 로그에 운영 데이터 삭제 요청이 없다. 삭제 요청 8건은 전부 워크트리·코드·문서 삭제였다 |
  | 4 | public-api | KPI 대시보드 집계를 외부에서 조회할 공개 API 엔드포인트를 연다 | **authored** — 로그에 공개 API 요청이 없다 |
  | 5 | irreversible-policy | 무료 플랜의 대화 기록 보존 기간을 30일에서 7일로 줄인다 | **authored** — 로그에 정책 기본값 변경 요청이 없다 |

  실제 로그 우선 탐색은 68개 프로젝트의 세션 로그(597MB)를 2회 훑어 수행했다. 5개 게이트 중 실제 요청이 **1건**뿐인 이유는 사용자의 프로젝트가 아직 운영 데이터·법무·공개 API 단계에 이르지 않았기 때문이다. authored 4건은 「라우터가 실제 사용에서 맞는가」를 증명하지 않는다 — `source.kind: authored` 가 그 한계를 파일에 남긴다.
- **수용 기준:**
  - [x] AC-1 `fixtures/requests/` 의 `classification.gates` 를 집계하면 `core/policy/classification.yaml` 의 `hard_gates[].id` 8개 각각에 대해 fixture 가 1건 이상이다.
  - [x] AC-2 추가한 5건의 `expected` 는 `notes/hand-derived-expected.md` 에 **항목별 근거**(어느 정책 규칙이 그 값을 내는가)와 함께 적혀 있고, `bin/romeo route --classification` 출력과의 항목별 대조표와 어긋난 항목 보고가 같은 파일에 있다. 그리고 **사용자가 그 표를 확인한 사실이 각 fixture 의 `human_correction` 에 기록된다**(`reviewed_by: user` · `verdict` · 확인 날짜). 그 뒤 `bin/romeo route --fixtures fixtures/requests --report` 가 38건 전부 일치로 exit 0 이다.

    (**1회차 재승인 사유 · D-80 경로.** 이 AC 는 처음에 「route 실행 **전에** 손으로 적었다」는 시간 순서를 요구했고 1회차 검토자가 `AC_UNMET` 을 냈다 — 그 순서는 사전에 봉인하지 않으면 사후 관측이 불가능한데 AC 가 봉인을 지시하지 않았다. 원인이 산출물이 아니라 완료 정의였다. 자기참조를 실제로 끊는 자리는 시간 순서가 아니라 **사람의 확인**이다 — 근거 열이 있는 표는 route 출력의 단순 복사와 이미 구별되고, 남은 것은 그 값이 옳은지를 사람이 판정하는 것이다. 기존 fixture 33건의 `human_correction` 이 그 자리다. `route --fixtures … --report` 는 **회귀 방지 검사**로 남는다 — expected 를 route 출력으로 채우면 그것으로 채점해도 항상 통과한다.)
  - [x] AC-3 새 검사는 게이트 id 를 **정책표에서 읽는다** — 정책표의 게이트 id 하나를 개명한 가상 상태에서 커버리지 검사가 실패한다(id 를 하드코딩한 검사는 이 상태에서 통과해 버린다).
  - [x] AC-4 새 검사는 fixture 의 `gates` 값이 정책표 id 집합 밖이면 실패한다 — 정책표에 없는 게이트 id 를 fixture 하나에 넣은 가상 상태에서 id 유효성 검사가 실패한다. (AC-3 과 다른 상태를 본다: AC-3 은 정책표를 바꾸고 fixture 를 그대로 두며, AC-4 는 fixture 를 바꾸고 정책표를 그대로 둔다.)
  - [x] AC-5 새 검사는 **판별 검사**다 — fixture 5건을 뺀 가상 상태(= 이 단위 이전 상태)에서 커버리지 검사가 실패하고, 5건이 있는 상태에서 통과한다. 양쪽을 실행으로 보인다. 더해서 **게이트 id 를 하드코딩한 구현**을 개명된 정책표로 돌리면 통과해 버리는 것을 반례로 보인다 — 빈 값이 아니라 그럴듯한 거짓 구현에서 갈리는 것을 확인한다(§11).
  - [x] AC-6 추가한 5건 각각의 `source.kind` 가 실제 출처(`session-log`)인지 `authored` 인지 파일에 적혀 있고, `authored` 인 4건은 `source.ref` 에 그 근거가 적혀 있다.
- **위험과 되돌리기:** 파일 추가와 새 테스트 1개뿐이라 `git revert <통합 SHA>` 로 전부 되돌아간다. 실제 위험은 다른 데 있다 — authored fixture 의 `expected` 는 내가 정책표를 보고 계산한 값이므로, 그것을 정책표로 채점하면 자기참조다. 그래서 **분류(`classification`)를 사용자가 승인 시점에 확정**하고 `human_correction` 에 기록한다. 승인 없이 채워 넣지 않는다.
- **결정 필요:** 없음 (fixture 출처 방침과 검사 범위는 2026-09-04 분류 확정 때 사용자가 정했다).

## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `fixtures/requests/` · `tests/test_gate_coverage.py` · `docs/work/feat-20260904-gate-fixture-coverage-q3wy/`
- 영향을 받는 부분: `bin/romeo route --fixtures` 의 대조 대상이 33건에서 38건으로 늘어난다. CI 의 `unittest discover` 가 새 검사를 함께 돈다.
- 바꾸지 않는 것(비범위): `core/policy/classification.yaml`(게이트 정의·facet 어휘를 건드리지 않는다 — 건드리면 재분류 대상이다) · 기존 fixture 33건 · `romeo/` 의 라우팅 코드 · `tests/test_policy.py`

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 확인란 표의 5건을 fixture 파일로 만든다. `expected` 는 요청 내용에서 **먼저 손으로 적고** `bin/romeo route --classification` 출력과 대조한다 — route 출력을 그대로 붙여 넣지 않는다(자기참조) | `fixtures/requests/fx-payment-metric-schema.yaml` · `fx-landing-consent-copy.yaml` · `fx-ops-test-data-purge.yaml` · `fx-public-kpi-endpoint.yaml` · `fx-free-plan-retention-cut.yaml` 신규 5건. 각 파일은 `core/schemas/fixture.json` 을 만족하고 `human_correction` 에 2026-09-04 사용자 확정을 기록한다 | 소비: 없음 → 생산: fixture 5건의 `id` 와 `classification.gates` | `bin/romeo route --fixtures fixtures/requests --report` 가 38건 전부 일치로 exit 0 이고, 손으로 적은 `expected` 와 route 출력이 어긋난 항목이 결과에 보고돼 있다 | 추가한 5개 파일 삭제 |
| 2 | 게이트 커버리지와 게이트 id 유효성을 정책표에서 읽어 대조하는 검사를 붙인다. 판별력(AC-3·AC-4·AC-5)을 검사 안에서 매번 재확인한다 | `tests/test_gate_coverage.py` 신규. `classification.yaml` 의 `hard_gates[].id` 를 읽어 ① 각 id 마다 fixture ≥ 1 ② 모든 fixture 의 `gates` ⊆ 그 id 집합 을 본다. 판별 실측 3건은 `tests/test_policy.py` 의 `TestFixtureReportExit` 와 같은 방식으로 임시 디렉터리 사본을 조작해 넣는다 | 소비: 1번이 만든 fixture 5건 → 생산: 없음 | `python3 -m unittest tests.test_gate_coverage -v` exit 0 | `tests/test_gate_coverage.py` 삭제 |

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

**판별 검사와 회귀 방지 검사의 구분(§11).** check-1 만 **판별 검사**다 — 이 단위가 없으면 실패해야 한다.
그 판별력은 검사 안의 네 가상 상태로 매번 재확인된다: fixture 5건 제거(커버리지 실패) · 정책표 게이트 id 개명(커버리지 실패) ·
fixture 에 없는 id 주입(id 유효성 실패) · **게이트 id 를 하드코딩한 구현 × 개명된 정책표**(그 구현은 통과해 버린다 — 이것이
「정책표에서 읽는가」를 가르는 반례다). check-2·check-3·check-4·check-5 는 **회귀 방지 검사**이고 양쪽 실측의 대상이 아니다 —
check-2 는 expected 를 route 출력으로 채우면 자기참조가 되므로 판별 검사로 세지 않는다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_gate_coverage -v"
  - id: check-2
    command: "bin/romeo route --fixtures fixtures/requests --report"
  - id: check-3
    command: "python3 -m unittest discover -s tests"
  - id: check-4
    command: "bin/romeo validate"
  - id: check-5
    command: "bin/romeo compile --check"
```


## 증거

close PASS · 2026-09-04T06:10:28+09:00 · HEAD 528c7f1bf01b · 검사 기록 run_60db3d61480b

- [evidence/run_dd07b98f3f83.yaml](evidence/run_dd07b98f3f83.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_60db3d61480b.yaml](evidence/run_60db3d61480b.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
