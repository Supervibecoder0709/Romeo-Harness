---
id: feat-20260913-seal-fill-scope-alignment-5sek
type: spec
title: 요구하는 자리에서 본다 — 봉인·채움·검사 범위의 세 자리
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
status: active
approved_at: '2026-09-13T01:49:18+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: [inputs/ac-rebuttal-20260913.md, inputs/probe-20260913.md]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-13'
updated: '2026-09-13'
---

# 요구하는 자리에서 본다 — 봉인·채움·검사 범위의 세 자리

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260913-seal-fill-scope-alignment-5sek --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 관통 절차의 세 자리에서 요구를 적은 문서와 그것을 보는 코드가 어긋난 것을 맞춘다 —
  검토 봉인(Q-103) · 검토자 브리프 채움(Q-104) · 충돌 fixture 의 검사 범위(Q-105 ①).
- **왜 지금:** 직전 관통이 4회차로 닫혔고 그 중 하나는 산출물이 아니라 절차 때문이었다. Q-103 은 M5 M1 관통에서
  회차 하나와 재승인 한 번을 실제로 태웠다 — 봉인된 run 에는 더 쓸 수 없어서(Q-101) 되돌릴 방법이 재승인뿐이었다.
  다음 관통(M5 M2 둘째 단위)은 게이트·가드가 붙는 무거운 관통이라 회차 하나의 비용이 지금보다 크다.
- **기대 결과:** 세 실수가 **일어난 자리에서** 드러난다 — 방어 검사를 빠뜨린 검토는 close 가 아니라 봉인 시점에 경고를 받고,
  검토자 브리프의 `base_sha` 는 손으로 옮겨 적을 값이 아니라 계약 파일에서 읽는 값이 되며,
  충돌 fixture 는 자기가 어느 저장소를 검사하는지 스스로 말한다.
- **수용 기준:**
  - [x] AC-1 검토 run 의 증거에 종료 검사가 판정에 쓰는 방어 검사 기록이 빠져 있으면, `romeo review record` 가
        **빠진 라벨을 모두** 이름으로 말하는 경고를 인쇄한다. 봉인은 그대로 이뤄지고, 그 명령의 종료 코드는
        같은 봉투를 방어 검사가 전부 있는 run 에 기록했을 때와 같다.
  - [x] AC-2 종료 검사가 판정에 쓰는 방어 검사 라벨 목록의 **정의가 저장소에 하나뿐**이고, AC-1 의 경고는 그 정의를 읽는다 —
        그 한 자리의 라벨 이름을 바꾸면 경고가 말하는 이름도 함께 바뀐다.
  - [x] AC-3 `fill_brief.py` 는 검토자 계약 파일의 **경로**를 받고, 채워진 브리프의 `base_sha` 는 그 JSON 의 값이며
        계약 sha256 은 **그 파일의 바이트에서 계산한** 값이다 — 계약 파일의 `base_sha` 를 바꾸면 브리프의 `base_sha` 가 바뀌고,
        그 파일의 내용을 바꾸면 브리프의 sha256 이 바뀐다. 그 두 값을 따로 넘기는 인자는 이 스크립트에 없다.
  - [x] AC-4 없어진 인자 이름을 넘기는 호출은 **어디서 오든** `fill_brief.py` 가 0 이 아닌 종료 코드로 거부한다 —
        그래서 문자열 검색에서 빠지는 간접 호출도 실행 시점에 드러난다. 그리고 이 저장소에서 그 스크립트를 **지시하는**
        자리 — 실행 명령(런북 §3.7 · `romeo/run_unit.py`)과 그 명령을 설명하는 산문 — 에 없어진 인자 이름이 남아 있지 않다.
  - [x] AC-5 충돌 fixture 는 자기 검사 대상 저장소를 **허용된 값으로** 선언하고, `check_conflicts` 는
        **그 선언이 정한 루트**를 그 fixture 의 검사에 넘긴다. 선언이 없거나 허용 목록 밖의 값인 fixture 가 있으면
        `doctor` 가 그 fixture 의 id 를 말하며 문제를 낸다.
  - [x] AC-6 c7 은 하네스를 선언하므로 대상 루트에 `core/` 가 **있든 없든** 하네스의 코어를 검사한다 —
        하네스 코어에만 금지 패턴을 심으면 c7 의 findings 가 **그 파일의 경로**를 가리키고,
        대상 코어에만 심으면 c7 의 findings 가 나오지 않는다.
- **위험과 되돌리기:** ① AC-1 의 경고를 차단으로 잘못 만들면 이 명령이 없던 시절의 봉투를 되살릴 길이 막힌다 — 그래서 종료 코드를 바꾸지 않는 것을 AC-1 이 직접 요구한다(K-31). ② `fill_brief.py` 의 인자를 바꾸면 그것을 부르는 자리가 함께 바뀌어야 하고, 하나라도 놓치면 다음 관통의 검토자 기동이 그 자리에서 멈춘다 — 그래서 AC-4 가 **스크립트 쪽에서** 거부하게 해 검색에 의존하지 않는다. 되돌리기: 세 변경 다 이 저장소 안의 로컬 커밋이라 `git revert <통합 커밋>` 하나로 끝나고, 외부 저장소·운영 데이터·권한 경계를 건드리지 않는다.
- **결정 필요:** 없음 — Q-105 ②(심링크 경계)를 범위에서 빼는 것은 2026-09-13 확정했다(카드의 `needs_decision`).

## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/evidence.py` (봉인 전 경고) · `romeo/cli.py` (경고 출력 자리) · `romeo/close.py` (방어 검사 라벨 목록을 공용으로) ·
  `romeo/doctor.py` (fixture 선언을 읽어 검사 루트를 고른다) · `romeo/run_unit.py` (검토자 브리프 명령 문자열) ·
  `adapters/orca/prompts/fill_brief.py` (계약 파일에서 읽는다) · `adapters/orca/RUNBOOK.md` (§3.7 호출 자리) ·
  `fixtures/conflicts/` (검사 대상 저장소 선언) · `tests/` (판별 검사) ·
  `docs/work/feat-20260913-seal-fill-scope-alignment-5sek/` (이 단위의 산출물) ·
  `docs/planning/open-questions.md` (Q-103·Q-104·Q-105 의 상태)
- 영향을 받는 부분: 다음 관통의 검토자 위임 절차 — 브리프를 채우는 명령과 봉인하는 명령이 둘 다 바뀐다. 종료 검사(`romeo close`)의 `REVIEW_VERDICT` **판정 기준은 바뀌지 않는다** — 같은 것을 더 이른 자리에서 한 번 더 볼 뿐이다.
- 바꾸지 않는 것(비범위): Q-105 ②(`_read_source_tree` 의 심링크 경계 — 지금 발동하지 않아 Q-105 에 열어 둔다) · M5 M2 둘째 단위의 내용(`romeo attach` · Q-58 · Q-59 · Q-106) · `docs/planning/progress.md`(통합 뒤 별도 커밋) · `review record` 를 차단으로 바꾸는 것 · 종료 검사의 판정 기준.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 봉인 시점에 방어 검사 부재를 말한다 (Q-103) | 종료 검사가 쓰는 방어 검사 라벨 목록을 두 자리가 함께 쓸 수 있는 곳에 두고, 검토 봉투를 기록하는 경로가 봉인 **전에** 그 run 의 증거에서 각 라벨의 기록을 찾는다. 빠진 것이 있으면 그 이름을 말하는 경고를 표준 오류에 인쇄하고 봉인은 그대로 진행한다 | 소비: 없음 → 생산: 방어 검사 라벨 목록의 단일 출처, 경고 코드 이름 | `tests/test_review_seal_warning.py` 의 두 테스트 — 라벨이 빠진 run 에서 경고가 나고 봉인은 되는 것, 목록을 바꾸면 경고가 말하는 이름도 바뀌는 것 | `git revert` |
| 2 | 옮겨 적을 값을 없앤다 (Q-104) | `fill_brief.py` 가 검토자 계약 파일 경로를 인자로 받아 `base_sha` 를 그 JSON 에서 읽고 sha256 을 그 파일에서 계산한다. `--base-sha`·`--task-sha256` 인자를 없앤다. 그것을 부르는 두 자리 — `adapters/orca/RUNBOOK.md` §3.7 과 `romeo/run_unit.py` 의 명령 문자열 — 와 그 명령을 설명하는 산문(§3.4 의 세 곳·`run_unit.py` 의 두 주석)을 같은 인터페이스로 맞추고, 옛 인자를 단언하던 `tests/test_run_unit.py` 2건과 `TestFillBrief.ARGS` 를 옮긴다 | 소비: 없음 → 생산: `fill_brief.py` 의 새 인자 이름 | `tests/test_reviewer_brief.py` — 계약의 `base_sha` 를 바꾸면 브리프의 값이 따라 바뀌는 것, 부르는 자리 전부가 새 인터페이스인 것 | `git revert` |
| 3 | fixture 가 검사 대상 저장소를 말한다 (Q-105 ①) | 충돌 fixture 에 검사 대상 저장소를 선언하는 필드를 더하고(7개 전부), `check_conflicts` 가 그 선언을 읽어 각 checker 에 넘길 검사 루트를 고른다. 선언이 없는 fixture 는 그 id 를 말하며 문제로 낸다. `_check_c7` 이 그 루트를 쓴다 | 소비: 없음 → 생산: fixture 의 선언 필드 이름과 허용 값 | `tests/test_doctor.py` `TestConflictFixtures` — 선언을 지운 fixture 가 문제가 되는 것, 코어 없는 대상에서도 c7 이 하네스 코어를 검사하는 것 | `git revert` |

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

**판별 검사와 회귀 방지 검사를 구분한다(§11).** check-1 ~ check-6 은 **판별 검사**다 — 이 단위의 변경이 없으면 실패해야 하고, 승인 전에 현재 상태(실패)와 가상 완료 상태(성공) 양쪽에서 실행해 보인다. check-7 ~ check-10 은 **회귀 방지 검사**이고 양쪽 상태에서 통과가 예상되므로 그 양쪽 실측의 대상이 아니다.

**check-7 의 실측 시간은 410초**(2026-09-13 · 1093 tests · OK)이고 재실행 상한은 검사 한 건당 600초다(`romeo/evidence.py` 의 `RERUN_TIMEOUT`) — 상한의 68% 라 close 의 근접 경고(80%) 아래다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_review_seal_warning.TestReviewSealWarning.test_a_run_missing_the_defensive_records_warns_and_still_seals -v"
  - id: check-2
    command: "python3 -m unittest tests.test_review_seal_warning.TestReviewSealWarning.test_the_warning_reads_the_label_list_close_judges_with -v"
  - id: check-3
    command: "python3 -m unittest tests.test_reviewer_brief.TestFillBrief.test_base_sha_and_hash_are_derived_from_the_contract_file -v"
  - id: check-4
    command: "python3 -m unittest tests.test_reviewer_brief.TestFillBrief.test_removed_arguments_are_refused_and_both_call_sites_match -v"
  - id: check-5
    command: "python3 -m unittest tests.test_doctor.TestConflictFixtures.test_a_fixture_with_no_or_invalid_scope_declaration_is_a_problem -v"
  - id: check-6
    command: "python3 -m unittest tests.test_doctor.TestConflictFixtures.test_c7_checks_the_harness_core_regardless_of_the_target -v"
  - id: check-7
    command: "python3 -m unittest discover -s tests -q"
  - id: check-8
    command: "bin/romeo validate"
  - id: check-9
    command: "bin/romeo compile --check"
  - id: check-10
    command: "bin/romeo doctor --strict --scope repository"
```

## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
