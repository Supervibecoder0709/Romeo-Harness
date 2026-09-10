---
id: feat-20260909-metrics-four-counters-dyz2
type: spec
title: 지표 — `romeo metrics` 가 네 카운터를 집계하고 각 숫자의 원본을 함께 인쇄한다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs, data]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
status: done
approved_at: '2026-09-10T10:32:41+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-09-10T15:22:11+09:00'
parent: init-20260904-m4-doc-reuse-metrics-wr9m
inputs: [../init-20260904-m4-doc-reuse-metrics-wr9m/charter.md, inputs/probe-20260909.md, inputs/ac-rebuttal-20260909.md,
  inputs/ac-rebuttal-20260909-2.md]
evidence: [evidence/run_cf5998614e4c.yaml, evidence/run_85a3e6bebe47.yaml, evidence/run_f93b869a890d.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-09'
updated: '2026-09-10'
---

# 지표 — `romeo metrics` 가 네 카운터를 집계하고 각 숫자의 원본을 함께 인쇄한다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs, data · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260909-metrics-four-counters-dyz2 --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** `romeo metrics` 하위 명령을 새로 만들어, 이 저장소 자신을 읽어 하네스 지표 4개(분류 수정률·gate 누락·T0 처리 시간·재분류율)를 표로 인쇄한다. 각 지표 옆에 **그 숫자를 만든 원본**을 함께 인쇄하고(K-63) — 파일 경로와 그 파일에서 읽은 자리, 그리고 읽은 파일 수까지 — 원본이 없다고 확인된 지표는 숫자 대신 「미집계」와 사유를 쓴다(K-68).
- **왜 지금:** M4 이니셔티브(`init-20260904-m4-doc-reuse-metrics-wr9m`)의 **마지막 마일스톤**이다. 앞의 셋 — 재사용 검색·1-hop 재개·승격과 무결성 — 이 만든 문서가 이 집계의 입력이고, 계획 §10 #14 의 관찰 결과 네 가지 중 마지막 하나(「`romeo metrics` 가 표를 출력」)가 이것으로 닫힌다. 그다음 단계인 §10 #15(shadow 20건 + v1 릴리스 게이트 판정)가 읽을 숫자가 여기서 처음 생긴다.
- **기대 결과:** `bin/romeo metrics` 를 치면 네 줄짜리 표가 선다. 세 지표는 숫자가 서고, **재분류율만 「미집계」로 선다** — 재분류 사건을 기록해야 할 자리(`routing.history`)가 문서 38건에서 전부 비어 있고 거기에 값을 넣는 코드 경로가 저장소에 없다는 것을 이 계획 단계에서 실측했기 때문이다. 그 자리에 `0%` 를 인쇄하면 「재분류가 한 번도 없었다」와 「일어나도 기록되지 않는다」를 구별하지 못한 채 전자를 주장하게 된다. 각 숫자 아래에는 그 숫자를 만든 파일 경로와 읽은 자리가 인쇄되므로, 숫자를 믿는 대신 직접 열어 다시 셀 수 있다.
- **수용 기준:**
  - [x] AC-1 ① `bin/romeo metrics` 가 종료 코드 0 으로 끝나고, 출력한 **지표 행의 집합이 지표 정의 정본(`romeo/metrics.py`)에 등록된 지표의 집합과 같다** — 등록된 것이 빠져도, 등록되지 않은 행이 끼어도 어긋난다. 검사는 이름·개수를 스스로 적지 않고 정본을 import 해 대조한다. ② 그리고 **그 정본에는 상위 charter 가 이름 붙인 네 지표**(분류 수정률·gate 누락·T0 처리 시간·재분류율)가 모두 등록되어 있다. ① 만 두면 정본과 출력을 **함께** 고쳐 요청과 다른 지표를 세는 산출물이 통과하므로, ② 가 요청 자체를 붙든다.
  - [x] AC-2 각 지표 행마다 **그 숫자를 만든 원본**이 인쇄된다 — 관측 사건이 1건 이상이면 **파일 경로와 그 파일에서 읽은 자리**(필드·키 이름)를, 0건이면 **읽은 범위**(찾은 자리와 읽은 파일 수)를 인쇄하고, 어느 쪽에도 빈 칸이 남지 않는다. 인쇄된 경로는 그 실행이 읽은 트리에 실재한다. 그리고 **인쇄된 「읽은 파일 수」가 그 트리에서 그 지표의 대상 범위에 실재하는 파일 수와 같다** — 대상의 일부만 읽고 그 일부의 출처를 정확히 인쇄하는 산출물은 이 기준에서 실패한다. 경로만으로는 부족하다: 「T0 처리 시간 70초」는 그 파일의 **어느 두 시각**을 뺀 것인지 알아야 손으로 다시 셀 수 있다.
  - [x] AC-3 정본이 「사건 없이 값을 주장하지 않는다」고 표시한 지표는, 관측 사건이 0 이면 값 자리에 숫자 대신 `미집계` 와 사유를 인쇄하고, **사건이 1건 이상 있는 입력에서는 숫자를 인쇄한다** — 두 경우를 각각 실행해 보인다. **재분류율은 그 표시 대상이다** — 표시 대상에서 빼면 빈 기록에서 `0%` 가 서고, 그것이 이 지표를 두는 이유를 지운다. **관측 사건은 그 값을 계산하는 데 필요한 자리가 다 채워진 기록만 센다** — 자리가 비어 있는 기록은 사건이 아니다. 그리고 **사유는 관측한 것만 말한다**: 「사건 0건」·「읽은 자리와 읽은 파일 수」는 관측이지만 「그런 일이 일어난 적 없다」는 관측이 아니므로 사유에 쓰지 않는다.
  - [x] AC-4 검사는 **값이 미리 정해진 작은 합성 입력 트리**를 스스로 만들어 거기에 명령을 돌린다. ① 그 트리에서 숫자로 인쇄된 지표마다, 인쇄된 값이 **그 트리에 대해 손으로 적어 둔 정답과 같다**(단위 포함). 정답은 계산식이 아니라 **숫자로** 적는다 — 집계 코드의 식을 검사에 옮겨 적으면 같은 오류가 양쪽에 생겨 대조가 아무것도 걸러내지 못한다. ② 그 트리의 원본을 바꾸면 값이 **두 번째로 적어 둔 정답**으로 바뀐다. 저장소 트리에 맞춘 상수를 넣거나 원본 한 건만 보정하는 산출물은 합성 트리에서 ① 이 어긋난다.
  - [x] AC-5 이 명령은 **지표의 값을 이유로 실패하지도 멈추지도 않는다** — AC-3·AC-4 가 만든 입력들(미집계가 있는 트리 · 숫자만 있는 트리 · gate 누락 0건인 트리 · gate 누락 1건 이상인 트리)과 이 저장소 트리에서, **표준 입력이 닫힌 비대화형 실행**이 사람의 입력을 기다리지 않고 종료 코드 0 으로 끝난다. 그 입력들 밖까지 주장하지 않는다 — charter 가 이 이니셔티브를 「드러내는 데까지」로 못박았으므로 나쁜 숫자로 절차를 막는 것은 이 명령의 일이 아니고, 그것을 확인한 범위는 여기 열거한 다섯 입력이다.
- **위험과 되돌리기:** 이 명령은 저장소 안 파일을 **읽기만** 한다 — 어떤 문서도 고치지 않고, 어떤 절차도 차단하지 않으며, 외부 상태·비용·운영 데이터를 건드리지 않는다. 잘못되면 `git revert <구현 커밋>` 하나로 되돌아가고 남는 것이 없다(새 파일 2개 + 기존 파일 2곳의 짧은 추가). 가장 큰 위험은 **숫자가 그럴듯한데 틀린 것**이다 — 원본과 무관하게 계산되거나 하드코딩된 값이 표에 서면 그다음 §10 #15 판정이 그것을 읽는다. AC-4 가 **검사 스스로 만든 작은 합성 트리**에서 손으로 적어 둔 정답과 대조하도록 요구해 그 경우를 막는다 — 저장소에 맞춘 상수도, 단위가 틀린 계산도 그 트리에서 어긋난다.
- **결정 필요:** 없음 — 재분류율을 「미집계」로 인쇄하는 것은 상위 charter 가 이미 정했다(「원본 데이터 부재가 확인되면 그 지표는 미집계로 정직하게 인쇄한다」, K-68).


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/metrics.py` (신규 — 지표 정의 정본과 집계) · `romeo/cli.py` (하위 명령 등록) · `tests/test_metrics.py` (신규 — 판별 검사) · `.github/workflows/harness.yml` (스모크 스텝 1개) · `docs/planning/open-questions.md` (범위 밖 발견 등록) · `docs/work/feat-20260909-metrics-four-counters-dyz2/`
- 영향을 받는 부분: `romeo/fixtures.py` 의 `run_report` 를 **불러 쓴다**(고치지 않는다 — gate 누락은 이미 그것이 계산한다). 읽기 대상은 `fixtures/requests/` 의 fixture 와 `docs/work/` 각 단위의 `spec.md` frontmatter 다.
- 바꾸지 않는 것(비범위): `routing.history` 에 값을 넣는 기록 경로를 **만들지 않는다** — 재분류율을 집계 가능하게 만드는 것은 이 요청이 아니고, 그 결함은 `docs/planning/open-questions.md` 에 열어 둔다(§12). 어떤 문서의 내용도 고치지 않는다(K-61). 지표 값으로 무엇도 차단하지 않는다(charter 의 비범위). `core/policy/` 와 `core/workflows/` 를 건드리지 않는다. `romeo/fixtures.py` 의 계산을 고치지 않는다.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 지표 정의 정본과 집계 함수를 한 자리에 둔다 | `romeo/metrics.py` 신규 — 지표 4개를 `id`·인쇄 이름·읽는 자리·관측 사건 규칙·「사건 없이 값을 주장하지 않는다」 표시로 적은 정본과, 그것을 돌아 값·사건 파일 목록을 내는 집계 함수 | 소비: `romeo.fixtures.run_report` → 생산: 지표 정본 상수 · 집계 함수 · 표 렌더 함수 | `python3 -c "from romeo.metrics import *"` 가 exit 0 이고, 정본을 돌아 지표 4개의 값과 사건 파일 목록이 나온다 | 파일 삭제 |
| 2 | 그 집계를 명령으로 노출한다 | `romeo/cli.py` 에 `metrics` 하위 명령 등록 (`--root` 로 대상 트리를 받아 다른 트리에도 돌릴 수 있게 한다 — AC-3·AC-4 의 「다른 입력」이 이것으로 만들어진다) | 소비: 1단계의 집계·렌더 함수 → 생산: `bin/romeo metrics` | `bin/romeo metrics` 가 exit 0 으로 네 행짜리 표를 인쇄한다 | 등록 줄 제거 |
| 3 | 판별 검사를 붙인다 | `tests/test_metrics.py` 신규 — AC-1~5 를 **정본을 import 해** 대조하고(이름·행 수를 검사에 옮겨 적지 않는다), charter 의 네 지표가 정본에 있는지 확인한다 · **값이 미리 정해진 작은 합성 트리**를 만들어 정답(계산식이 아니라 숫자)과 대조하고, 사건 0/사건 1 · gate 누락 0/1 두 입력에서 미집계와 숫자·종료 코드 양쪽을 실행으로 본다 | 소비: 1단계의 정본·집계 함수 → 생산: 없음 | `python3 -m unittest tests.test_metrics -v` 가 exit 0 | 파일 삭제 |
| 4 | CI 가 이 명령을 실제로 돌린다 | `.github/workflows/harness.yml` 에 `bin/romeo metrics` 스텝 1개 | 소비: 2단계의 명령 → 생산: 없음 | `grep -q 'romeo metrics' .github/workflows/harness.yml` 가 exit 0 | 스텝 제거 |
| 5 | 범위 밖 발견을 닫지 않고 연다 | `docs/planning/open-questions.md` 에 「재분류 사건의 기록 경로가 없다 — 절차(`core/workflows/plan/SKILL.md` 의 「재분류」)는 `routing.history` append 를 요구하는데 그것을 쓰는 코드가 없다」를 새 Q 로 등록 | 소비: 없음 → 생산: Q 번호 | `grep -q 'routing.history' docs/planning/open-questions.md` 가 exit 0 | 항목 제거 |

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

**어느 것이 판별 검사인가.** check-1·2·3 은 **판별 검사**다 — 이 단위가 없으면 실패해야 하고, 승인 전에 기존 상태와 가상 완료 상태 양쪽에서 돌려 보인다(§11). check-4·5·6·7 은 **회귀 방지 검사**로, 양쪽에서 통과하는 것이 정의이므로 양쪽 실측의 대상이 아니다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_metrics -v"
  - id: check-2
    command: "bin/romeo metrics < /dev/null"
  - id: check-3
    command: "grep -q 'romeo metrics' .github/workflows/harness.yml"
  - id: check-4
    command: "python3 -m unittest discover -s tests"
  - id: check-5
    command: "bin/romeo validate"
  - id: check-6
    command: "bin/romeo compile --check"
  - id: check-7
    command: "bin/romeo integrity"
```


## 증거

close PASS · 2026-09-10T15:22:11+09:00 · HEAD b70568f17ca0 · 검사 기록 run_f93b869a890d

- [evidence/run_cf5998614e4c.yaml](evidence/run_cf5998614e4c.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_85a3e6bebe47.yaml](evidence/run_85a3e6bebe47.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_f93b869a890d.yaml](evidence/run_f93b869a890d.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
