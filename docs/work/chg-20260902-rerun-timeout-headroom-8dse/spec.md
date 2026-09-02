---
id: chg-20260902-rerun-timeout-headroom-8dse
type: spec
title: 재실행 상한이 조용히 관통을 막지 않게 한다 — 600초 + 80% 경고
unit: T0
mode: delivery
intent: write
facets: [tooling]
gates: []
profile: quick
blast_radius: small
uncertainty: low
status: done
approved_at: '2026-09-02T17:51:27+09:00'
approved_by: justjulliette0709
base_sha: null
closed_at: '2026-09-02T18:05:40+09:00'
parent: null
inputs: []
evidence: [evidence/run_1c4ef2f5c6de.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T0=quick']
  history: []
created: '2026-09-02'
updated: '2026-09-02'
---

# 재실행 상한이 조용히 관통을 막지 않게 한다 — 600초 + 80% 경고

> 깊이 **Quick** · 단위 T0 · 모드 delivery · 의도 write · 영역 tooling · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve chg-20260902-rerun-timeout-headroom-8dse --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 재실행 대조 상한을 300초에서 600초로 올리고, 재실행 한 건이 상한의 80% 를 넘으면 `close` 가 경고를 인쇄한다.
- **왜 지금:** 전체 unittest 가 258초인데 상한이 300초다(2026-09-02 실측). 상한은 재실행 **한 건**에 걸리고, 하네스 자기 단위는 그 한 건에 전체 테스트를 넣는다 — 넘는 순간 그 검사가 미검증이 되고 `close` 가 done 을 선언하지 않는다. 즉 **모든 관통의 완료가 막힌다.** 테스트는 앞으로도 늘어난다.
- **기대 결과:** 지금 258/600 = 43% 라 조용하다. 480초를 넘는 순간 경고가 떠서 "다음에 막힌다" 가 막히기 전에 보인다. 그때가 느린 테스트(현재 `test_docs_evidence_close` 104초)를 손볼 시점이고, 그것은 별도 단위로 연다 — 이 단위는 고치지 않는다(§12).
- **수용 기준:**
  - [x] AC-1 `RERUN_TIMEOUT` 의 값이 600 이고, 그 값이 단일 출처로 남아 `--rerun-timeout` 기본값과 도움말 문구에 그대로 실린다.
  - [x] AC-2 재실행 한 건이 상한의 80% 이상을 쓰면 `close` 가 `RERUN_NEAR_TIMEOUT` 을 **경고로** 인쇄한다 — 판정을 바꾸지 않는다(PASS 는 PASS 로 남는다).
  - [x] AC-3 80% 미만인 재실행에서는 그 경고가 인쇄되지 않는다 — 늘 뜨는 경고는 아무것도 알리지 않는다.
- **위험과 되돌리기:** 상한을 올리면 정말로 매달린 명령을 더 오래 기다린다(최대 5분 추가). 그것은 `close` 한 번의 대기이고 상태를 바꾸지 않는다. 되돌리기: `romeo/evidence.py` 의 `RERUN_TIMEOUT` 을 300 으로 되돌리고 `close.py` 의 경고 블록을 지운다.
- **결정 필요:** 없음

## Planning Capsule

T0는 기획 파일이 없다. 이 절(≤ 20줄)이 기획을 대신한다.

- **문제:** 재실행 대조 상한(300초)이 전체 테스트 시간(258초)에 붙었다. 넘으면 그 검사가 미검증이 되어 완료가 서지 않는데, 넘기 전까지는 아무 신호가 없다.
- **대상·상황:** 이 저장소의 모든 작업 단위. 하네스 자기 단위는 `required_checks` 에 전체 테스트를 한 건으로 넣는 것이 정당하다 — 그때는 그것이 그 단위의 산출물이기 때문이다.
- **기대 결과:** 상한에 여유가 생기고, 여유가 줄어드는 것이 막히기 전에 보인다.
- **범위 / 비범위:** 상수 값과 경고 하나. 느린 테스트를 빠르게 만드는 것은 **비범위** — 원인(테스트마다 임시 저장소를 세우는 구조)이 이 요청 밖이다(§12).
- **가정:** 경과 시간은 `_check_rerun` 에서 재면 되고 `replay` 의 반환 형태를 바꾸지 않는다.
- **열린 질문:** 없음


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/evidence.py` · `romeo/close.py` · `tests/test_docs_evidence_close.py`
- 영향을 받는 부분: `bin/romeo close` 의 재실행 대조 출력. `--rerun-timeout` 의 기본값과 도움말 문구(`romeo/cli.py` 가 상수를 f-string 으로 읽으므로 그 파일은 고치지 않는다).
- 바꾸지 않는 것(비범위): `replay` 의 반환 형태 · 재실행 판정(PASS/FAIL/UNVERIFIED) · 느린 테스트 자체 · 다른 상한

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 상한에 여유를 준다 | `romeo/evidence.py` 의 `RERUN_TIMEOUT` 을 300 → 600 | 소비: 없음 → 생산: 상수 600 | check-1 | 300 으로 되돌린다 |
| 2 | 여유가 줄어드는 것을 막히기 전에 드러낸다 | `romeo/close.py` 의 `_check_rerun` 이 각 재실행의 경과 시간을 재고, 상한의 80% 이상이면 `RERUN_NEAR_TIMEOUT` 을 `level="warning"` 으로 인쇄 | 소비: 상한 값 → 생산: 경고 id `RERUN_NEAR_TIMEOUT` | check-2 | 그 블록을 지운다 |
| 3 | 늘 뜨는 경고가 되지 않게 고정한다 | `tests/test_docs_evidence_close.py` 에 `TestRerunNearTimeout` 추가 — 80% 이상에서 뜨고 미만에서 안 뜨는 두 경우, 판정이 PASS 로 남는 것 | 소비: 경고 id → 생산: 없음 | check-2 | 클래스를 지운다 |

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

**양쪽으로 보인다(AGENTS.core §11).** check-1·2 는 **판별 검사**다 — 기존 상태(`2b0d876`)에서 실패하고 구현 뒤 통과하는 것을 승인 전에 양쪽으로 보인다. check-2 의 **그럴듯한 거짓 값** 반례는 `test_warning_absent_below_threshold` 다: 경과 시간을 재지 않고 **늘** 경고를 인쇄하는 구현은 형태가 그럴듯하지만 그 검사에서 실패한다. check-3~5 는 **회귀 방지 검사**이고 양쪽에서 통과가 예상되므로 판별 실측 대상이 아니다(§11).

```yaml
required_checks:
  - id: check-1
    command: "python3 -c \"from romeo.evidence import RERUN_TIMEOUT; assert RERUN_TIMEOUT == 600, RERUN_TIMEOUT\" && bin/romeo close --help | grep -q '기본 600'"
  - id: check-2
    command: "python3 -m unittest tests.test_docs_evidence_close.TestRerunNearTimeout"
  - id: check-3
    command: "python3 -m unittest discover -s tests"
  - id: check-4
    command: "bin/romeo validate"
  - id: check-5
    command: "bin/romeo compile --check"
```


## 증거

close PASS · 2026-09-02T18:05:40+09:00 · HEAD dd8980da3eb6 · 검사 기록 run_1c4ef2f5c6de

- [evidence/run_1c4ef2f5c6de.yaml](evidence/run_1c4ef2f5c6de.yaml) — exit codes [0, 0, 0, 0, 0] (검사 기록)
