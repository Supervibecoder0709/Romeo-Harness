---
id: feat-20260831-repeat-brake-82zv
type: spec
title: 반복 중단 브레이크를 실제로 걸고 expect 함정을 없앤다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: low
status: active
approved_at: '2026-08-31T00:37:20+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-08-31'
updated: '2026-08-31'
approval_history:
- {approved_at: '2026-08-31T00:11:32+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-08-31T00:37:20+09:00',
  reason: '1차 관통이 spec 의 전제를 실측으로 반증했다 — expect 를 코드·스키마에서 지우면 옛 작업 계약 35개의 바이트 재계산(close.py:447 TASK_ANCHORED)이
    깨진다. 막는 것은 스키마 검증이 아니라 재계산이라 additionalProperties 를 풀어도 실패했다. 사용자 확정(옵션 C): 템플릿에서만 지운다 — envelope.py
    는 expect 가 있을 때만 복사하므로 옛 봉투는 그대로 나오고 새 spec 에는 안 생긴다. AC-6 을 ''코드 두 파일이 base 와 바이트가 같다'' 로 바꾸고 AC-7(테스트
    앵커)을 더했으며 check-15 를 신설했다. 브레이크(③·Ⓔ)는 무변경'}
---

# 반복 중단 브레이크를 실제로 걸고 expect 함정을 없앤다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260831-repeat-brake-82zv --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 반복을 멈추라고 말해 줄 **브레이크를 실제로 걸고**, 사람이 조건으로 쓰지만 기계가 보지 않는 **함정 하나를 없앤다.** 셋뿐이다. ③ 연속 실패 카운터가 **재검토로 리셋되지 않게** 한다 — 재검토는 그 시점까지를 한 번 통과시키는 것이지 카운터를 0 으로 만드는 것이 아니다. Ⓔ 중단 게이트를 **`envelope build` 에 건다** — 지금 게이트는 `run-unit` 안에만 있어서, 절차를 손으로 밟으면 한 번도 평가되지 않는다. ② `required_checks` 의 `expect` 필드를 **지운다** — 구현하는 것보다 없애는 것이 싸고 함정이 사라진다. 그리고 남은 마찰 6건을 `open-questions.md` 로 **넘긴다.**
- **왜 지금:** 정비 반복이 끝나 보이지 않는 원인은 결함 수가 아니라 **멈추라고 말해 줄 장치가 꺼져 있는 것**이다. 실측 두 가지가 그것을 보여준다 — (a) 실패 1·2 → 재검토 → 실패 3 이면 카운터가 1 로 돌아가 **4회차가 재검토 없이 돈다**(`run_unit.py:78`), (b) 게이트를 부르는 곳이 `run_unit()` 하나뿐이라 **RUNBOOK §3 을 손으로 관통하면 게이트가 평가되지 않는다** — 직전 관통이 실제로 그랬다. 이 상태로 M3(BMAD 부품 46개)에 들어가면 같은 반복이 훨씬 비싼 자리에서 난다.
- **기대 결과:** 같은 완료 정의를 향한 관통이 **연속 2회 실패하면, 어느 경로로 돌리든 3회차가 시작되지 않는다** — 사람이 재검토를 기록하기 전까지. 그리고 앞으로 누구도 `expect:` 에 조건을 써 놓고 기계가 볼 것이라 믿지 않는다. 이 단위 뒤에는 하네스 정비를 멈추고 M3 로 넘어간다.
- **수용 기준:**
  - [ ] AC-1 (③) 실패 2회 뒤 재검토가 기록돼 있어도, 그 다음 실패가 하나 더 쌓이면 **다시 차단된다** — 재검토는 카운터를 0 으로 만들지 않는다. `tests/test_run_unit.py` 의 회귀 테스트가 이것을 실행으로 보인다.
  - [ ] AC-2 (③) **성공은 여전히 카운터를 0 으로 되돌린다** — 실패 2회 뒤 성공하면 그 다음 실패 1회로는 차단되지 않는다. 같은 파일의 회귀 테스트가 보인다.
  - [ ] AC-3 (Ⓔ) 중단 조건에 걸린 단위에서 `bin/romeo envelope build` 가 **종료 코드 0 이 아니고**, 무엇이 왜 막혔는지와 어떻게 푸는지를 한국어로 말한다. 회귀 테스트가 보인다.
  - [ ] AC-4 (Ⓔ) 중단 조건에 걸리지 않은 단위(시도 기록이 아예 없는 경우 포함)에서는 `envelope build` 가 **그대로 동작한다** — 이 단위 자신의 관통이 그 증거이고, 회귀 테스트도 보인다.
  - [ ] AC-5 (②) `core/templates/tech-spec.md` 에 `expect:` 가 남아 있지 않고, 대신 **종료 코드 자체가 조건**이라는 문장과 그 이유가 인쇄되어 있다.
  - [ ] AC-6 (②) `core/schemas/task-envelope.json` 의 `expect` 속성은 **남아 있고**, 그 설명에 **`판정에 쓰이지 않는다`** 가 적혀 있다. 그리고 `romeo/envelope.py`·`romeo/close.py` 는 `base_sha` 와 **바이트가 같다** — 코드에서 `expect` 를 없애면 옛 작업 계약 35개의 바이트 재계산이 깨진다(아래 위험 절). (`romeo/parity.py` 의 `expect` 는 **다른 것**이므로 건드리지 않는다.)
  - [ ] AC-7 (②) `tests/test_docs_evidence_close.py` 가 템플릿의 `expect` 줄을 편집 앵커로 쓰지 않는다 — 템플릿에서 그 줄이 사라져도 그 파일의 테스트가 전부 통과한다.
  - [ ] AC-8 (park) `docs/planning/open-questions.md` 에 넘기는 항목이 **`우회 가능 — v1 이후`** 표시와 함께 등록돼 있다 — ⑤(검토자 lifecycle 자동화) · Ⓓ(waiter 하나) · Ⓕ(task 사본이 merge 막음) · w3qu 잔여 3건(템플릿 한 줄 · 프롬프트 하드코딩 · `compile --list-outputs`).
  - [ ] AC-9 (Ⓔ) `adapters/orca/RUNBOOK.md` 가 **중단 게이트**가 어디서 걸리는지 말한다 — 손으로 관통해도 §3.3 에서 막힌다는 것.
  - [ ] AC-10 기존 검사가 회귀하지 않는다 — `python3 -m unittest discover -s tests` · `bin/romeo validate` · `compile --check` · `doctor` · `fixtures parity --report` 가 모두 종료 코드 0.
- **위험과 되돌리기:** **`envelope build` 는 모든 관통의 입구다** — 잘못 걸면 어떤 관통도 시작하지 못한다. 그래서 AC-4 가 "안 걸린 경우엔 그대로 동작한다" 를 따로 요구하고, 이 단위 자신의 관통이 그 살아 있는 증거가 된다(이 단위가 돌았다는 것이 곧 입구가 막히지 않았다는 뜻이다). **`expect` 는 코드·스키마에서 지우지 않는다 — 1차 관통이 그 이유를 실측으로 드러냈다.** 옛 작업 계약 **35개**가 `expect` 를 담고 있고, `romeo/close.py:447` 의 `TASK_ANCHORED` 는 그 봉투를 **지금 코드로 다시 만들어 바이트로 대조**한다(스키마 검증이 아니다 — `additionalProperties` 를 풀어도 그대로 실패했다). `romeo/envelope.py` 가 `expect` 를 안 만드는 순간 옛 단위 6개의 앵커가 전부 어긋난다. 그래서 **템플릿에서만** 지운다 — `envelope.py` 는 `expect` 가 **있을 때만** 복사하므로 옛 spec 의 봉투는 재계산해도 그대로 나오고 새 spec 에는 애초에 생기지 않는다. 함정이 무는 자리는 사람이 새 spec 을 쓸 때이고 거기가 정확히 막힌다. AC-6 이 코드 두 파일의 무변경을, AC-10 의 `fixtures parity --report` 가 그 전제를 지킨다. 전부 이 저장소 안의 로컬 변경이고 외부 상태를 바꾸지 않으므로 되돌리기는 `git revert <커밋>` 한 번이다.
- **결정 필요:** 없음 — 2026-08-31 사용자 확정. 브레이크(③·Ⓔ)와 `expect` 삭제(②)만 고치고 **나머지 우회 가능한 것은 전부 넘긴다.** 이 단위 뒤 하네스 정비를 멈추고 M3 로 간다.


## 변경 범위

- 바뀌는 파일·모듈: `romeo/run_unit.py` · `romeo/envelope.py` · `romeo/close.py` · `core/schemas/task-envelope.json` · `core/templates/tech-spec.md` · `adapters/orca/RUNBOOK.md` · `docs/planning/open-questions.md` · `tests/test_run_unit.py` · `tests/test_docs_evidence_close.py` · `docs/work/feat-20260831-repeat-brake-82zv/`
- 영향을 받는 부분: **다음 모든 관통의 입구**(`envelope build` 가 중단 게이트를 평가한다) · `bin/romeo new` 가 만드는 모든 새 spec(템플릿에서 `expect` 가 빠진다) · `run-unit` 의 차단 판정 · 이미 `expect:` 를 가진 기존 spec 은 그대로 둔다(과거 기록을 소급 수정하지 않는다 — 여분의 YAML 키로 남고 파싱을 깨지 않는다).
- 바꾸지 않는 것(비범위): `romeo/parity.py` 의 `expect`(**다른 것** — fixture 의 기대 판정 same/differ) · 코어 규칙 문장(`core/principles/AGENTS.core.md` §10 — 코드를 문장에 맞추는 것이지 그 반대가 아니다) · 권한 상한(`.harness/bindings.yaml`·`.claude/settings.json`) · 정책표(`core/policy/*.yaml`) · `fixtures/` · `docs/work/feat-20260830-harness-defects-w3qu/`(park 한다 — 닫지도 폐기하지도 않는다) · `docs/planning/progress.md`(통합 뒤 별도로 갱신한다)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**확인 방법** 열의 따옴표 안 문자열은 검증 계획의 `grep` 이 문자 그대로 찾는 값이다. 그대로 쓴다.
테스트 이름도 검증 계획이 그대로 부르므로 **클래스·메서드 이름을 그대로** 쓴다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | ③ 재검토가 카운터를 리셋하지 않는다 | `romeo/run_unit.py` 의 `consecutive_failures()` 에서 `floor = _reviewed_through(data)` 를 없애 **마지막 `pass` 이후의 연속 실패를 전부** 세게 한다. 재검토의 역할은 `gate()` 로 옮긴다 — 연속 실패가 한도 이상이어도 **마지막 재검토가 마지막 시도를 덮으면**(`_reviewed_through(data) >= len(attempts)`) 통과시킨다. `_reviewed_through` 는 그 판정에 계속 쓰인다 | 소비: 없음 → 생산: `consecutive_failures()`·`gate()` 의 반환 의미 | `tests/test_run_unit.py` 에 `RepeatGate.test_review_does_not_reset_counter` 를 추가한다 — 실패 2 + 재검토(after_attempt 2) + 실패 1 인 attempts 로 `gate()` 가 **차단**을 내는 것을 확인한다 | `git revert` |
| 2 | ③ 성공은 여전히 리셋한다 | 1행과 같은 함수. `pass` 를 만나면 세기를 멈추는 기존 동작을 유지한다 | 소비: 1행의 함수 → 생산: 같은 함수의 성공 경로 | `RepeatGate.test_pass_resets_counter` — 실패 2 + 성공 1 + 실패 1 인 attempts 로 `gate()` 가 **통과**를 내는 것을 확인한다 | `git revert` |
| 3 | Ⓔ 중단 게이트가 모든 관통의 입구에서 걸린다 | `romeo/envelope.py` 의 계약 생성 경로에서 그 단위의 `attempts.yaml` 을 읽어 `gate()` 를 평가하고, 차단이면 **계약을 만들지 않고** 종료 코드 0 이 아닌 오류로 끝낸다. 오류 문구는 연속 실패 수와 「재검토 결론을 기록해야 한다」와 그 방법을 한국어로 말한다. 우회 수단을 둘지는 구현자가 `run-unit --after-review` 경로와 견주어 정하고, 정한 이유를 결과 봉투 `notes` 에 적는다 | 소비: 1행의 `gate()` → 생산: `envelope build` 의 차단 경로 | `RepeatGate.test_envelope_build_refuses_when_blocked` — 차단 상태 attempts 를 가진 임시 단위에서 계약 생성이 **0 이 아닌 종료 코드**로 끝나고 계약 파일이 생기지 않는 것을 확인한다 | `git revert` |
| 4 | Ⓔ 안 걸린 경우엔 그대로 동작한다 | 3행과 같은 자리. `attempts.yaml` 이 **없으면** 실패 0 으로 보아 통과시킨다 — 지금 대부분의 단위가 그 상태다 | 소비: 3행 → 생산: 같은 경로의 통과 분기 | `RepeatGate.test_envelope_build_allows_when_not_blocked` — 시도 기록이 없는 단위와 마지막이 `pass` 인 단위 **둘 다** 계약이 정상 생성되는 것을 확인한다 | `git revert` |
| 5 | ② 템플릿이 함정을 더 만들지 않는다 | `core/templates/tech-spec.md` 의 검증 계획 예시에서 `expect:` 줄을 지우고, 그 자리에 **「종료 코드 자체가 조건」**이라는 문장과 이유(사람이 조건으로 쓴 문장을 기계가 읽지 않으면 그 검사는 빈 검사가 된다)를 인쇄한다. `\|\| true` 를 쓰지 말고 부정은 `!` 로 쓰라는 한 줄도 함께 넣는다 | 소비: 없음 → 생산: 템플릿 문구 | 템플릿에 `expect:` 가 **없고** `종료 코드 자체가 조건` 이 **있다** | `git revert` |
| 6 | ② 필드를 코드·스키마에서 없앤다 | `core/schemas/task-envelope.json` 의 `expect` 속성, `romeo/envelope.py:189-190` 의 복사, `romeo/close.py:64` 의 대조 튜플에서 `expect` 를 뺀다. 세 줄이 전부다(grep 실측, 오탐 0). **`romeo/parity.py` 는 건드리지 않는다** — 그쪽 `expect` 는 fixture 의 기대 판정이다. 이미 `expect:` 를 가진 기존 spec 은 고치지 않는다 | 소비: 없음 → 생산: 계약 JSON 의 필드 구성 | `core/schemas/task-envelope.json` 에 `"expect"` 가 없고, `romeo/envelope.py`·`romeo/close.py` 에 `expect` 가 없다 | `git revert` |
| 7 | park — 넘기는 것이 기록으로 남는다 | `docs/planning/open-questions.md` 의 Q 절에 6건을 등록한다(Q-12 부터). 각 행에 **`우회 가능 — v1 이후`** 를 적고 우회 방법과 근거 위치를 함께 남긴다: ⑤ 검토자 lifecycle 자동화 · Ⓓ `check --wait` 는 Run 당 waiter 하나 · Ⓕ `task/` 사본이 `git merge --ff-only` 를 막는다 · w3qu 잔여 3건(템플릿 한 줄 · 프롬프트 하드코딩 · `compile --list-outputs`). w3qu 는 **닫지도 폐기하지도 않고** `status: active` 로 park 하며 구현이 브랜치 `a1f543a` 에 보존돼 있다는 것을 적는다 | 소비: 없음 → 생산: open-questions 의 Q 행들 | `우회 가능 — v1 이후` 가 문서에 있다 | `git revert` |
| 8 | Ⓔ 게이트가 어디서 걸리는지 문서가 말한다 | `adapters/orca/RUNBOOK.md` §3.3 에 **중단 게이트**가 그 자리에서 평가된다는 것과, 차단되면 무엇을 해야 하는지를 적는다. 손으로 관통해도 이 자리를 반드시 지난다는 것이 요점이다 | 소비: 3행 → 생산: RUNBOOK 문단 | `중단 게이트` 가 문서에 있다 | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

이 단위는 **하네스 저장소 자신**이 대상이므로 하네스 검사(check-10~14)가 정당한 검사다.
check-1~9 와 check-15 는 이 단위가 만든 것을 직접 겨눈다. check-15 는 **코드 두 파일이 base 와 바이트가 같다**를 종료 코드로 본다 — 1차 관통이 그 두 파일을 고쳐 옛 봉투 35개를 깨뜨렸기 때문이다.

**모든 검사는 종료 코드 자체가 조건이다.** `|| true` 를 쓰지 않고, 부정 조건은 `!` 로 쓴다.
check-5~9 는 **구현 전 상태에서 전부 종료 코드 1** 인 것을 2026-08-31 에 실측했고, check-10~14 는 같은 시점에 전부 0 이었다.
check-1~4 는 아직 없는 테스트를 부르므로 구현 전에는 당연히 실패한다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_run_unit.RepeatGate.test_review_does_not_reset_counter"
  - id: check-2
    command: "python3 -m unittest tests.test_run_unit.RepeatGate.test_pass_resets_counter"
  - id: check-3
    command: "python3 -m unittest tests.test_run_unit.RepeatGate.test_envelope_build_refuses_when_blocked"
  - id: check-4
    command: "python3 -m unittest tests.test_run_unit.RepeatGate.test_envelope_build_allows_when_not_blocked"
  - id: check-5
    command: "! grep -qF 'expect:' core/templates/tech-spec.md"
  - id: check-6
    command: "grep -qF '종료 코드 자체가 조건' core/templates/tech-spec.md"
  - id: check-7
    command: "grep -qF '판정에 쓰이지 않는다' core/schemas/task-envelope.json"
  - id: check-15
    command: "git diff --quiet HEAD -- romeo/envelope.py romeo/close.py"
  - id: check-8
    command: "grep -qF '우회 가능 — v1 이후' docs/planning/open-questions.md"
  - id: check-9
    command: "grep -qF '중단 게이트' adapters/orca/RUNBOOK.md"
  - id: check-10
    command: "python3 -m unittest discover -s tests"
  - id: check-11
    command: "bin/romeo validate"
  - id: check-12
    command: "bin/romeo compile --check"
  - id: check-13
    command: "bin/romeo doctor"
  - id: check-14
    command: "bin/romeo fixtures parity --report"
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
