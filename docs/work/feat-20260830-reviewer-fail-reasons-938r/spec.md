---
id: feat-20260830-reviewer-fail-reasons-938r
type: spec
title: 검토자 FAIL 사유를 닫힌 목록으로 만들고 결과 봉투로 강제한다 — 하네스가 허용하는 상태를 검토자가 FAIL 로 보는 충돌 해소
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: done
approved_at: '2026-08-30T22:30:22+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-08-30T22:51:13+09:00'
parent: null
inputs: []
evidence: [evidence/run_c62036661689.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-08-30'
updated: '2026-08-30'
approval_history:
- {approved_at: '2026-08-30T21:56:08+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-08-30T22:30:22+09:00',
  reason: '1회차 관통이 spec 의 위험 (2) 판단 오류를 드러냈다 — fixtures/parity 관측 케이스 2건이 이미 done 인 단위의 옛 FAIL 봉투 8건을
    직접 읽으므로 fail_reasons 를 조건부 필수로 조이면 check-5 와 test_parity 가 실패한다. AC-2 를 두 겹(스키마는 값만·close 가 존재를)으로
    나누고, 변경 범위에 romeo/close.py 를 더하고, 검증 계획을 9건에서 10건으로 늘렸다(check-7 은 스키마 앞겹·check-10 은 close 뒷겹). 과거
    판정 기록은 소급 수정하지 않는다'}
---

# 검토자 FAIL 사유를 닫힌 목록으로 만들고 결과 봉투로 강제한다 — 하네스가 허용하는 상태를 검토자가 FAIL 로 보는 충돌 해소

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260830-reviewer-fail-reasons-938r --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 검토자가 게이트를 내릴 수 있는 사유를 **닫힌 목록**으로 만든다. 지금 `review/SKILL.md` 는 FAIL 사유 8개를
  "정본" 이라고 선언하지만 "이 목록에 없으면 FAIL 이 아니다" 를 말하지 않아, 검토자가 목록 밖 사유로 게이트를 내릴 수 있다.
  각 사유에 코드를 붙이고, 결과 봉투 스키마가 `gate_verdict` 가 `FAIL` 일 때 그 코드를 요구하게 한다 — 목록 밖 사유는 기계가 걸러낸다.
  함께, 4회차 관통을 멈춰 세운 그 사유(구현자가 확인란 체크박스를 채워 spec.md 지문이 작업 계약의 것과 달라진 것)가
  **정상이라는 것**을 문서에 명시한다.
- **왜 지금:** 이것이 닫히지 않으면 **어떤 작업 단위도 close 되지 않는다.** 구현자는 절차대로 확인란을 체크해야 하는데,
  체크하는 순간 지문이 갈라지고 검토자가 그것을 FAIL 로 본다. 4회차 표본 2건이 같은 사유로 FAIL 했고(흔들림이 아니다),
  같은 시점 `close --dry-run` 은 나머지 검사를 전부 PASS 로 냈다 — 하네스와 검토자의 판정이 갈린 것이다.
  열린 단위 `feat-20260830-harness-defects-w3qu` 의 구현 9개 파일이 미커밋으로 대기 중이고, 그 단위는 이 수정 뒤 새 base 로 재개한다.
  §10 상 지금은 관통과 관통 사이라 하네스를 고칠 수 있는 구간이다.
- **기대 결과:** 검토자가 목록 밖 사유로 `FAIL` 을 내면 결과 봉투가 스키마 검증에서 걸린다.
  확인란 체크로 인한 지문 차이를 FAIL 로 보는 판정이 재현되지 않고, `w3qu` 를 새 base 로 재개할 수 있게 된다.
  검토자가 목록 밖의 진짜 문제를 발견하면 `findings` 로 적고 판정은 `PASS` 로 낸다 — 사유를 목록에 더할지는 사람이 정한다(K-61).
- **수용 기준:**
  - [x] AC-1 `core/workflows/review/SKILL.md` 의 FAIL 사유 8개에 각각 코드가 붙어 있고, "이 목록에 없는 사유로 `gate_verdict` 를 `FAIL` 로 내지 않는다" 는 취지의 닫힌 목록 선언이 있으며, 그 코드 집합이 `core/schemas/result-envelope.json` 의 `fail_reasons` 열거값과 **정확히 같다**(한쪽에만 있는 코드가 없다).
  - [x] AC-2 FAIL 사유가 두 겹으로 강제된다 — ① 결과 봉투 스키마는 `fail_reasons` 에 목록 밖 코드가 들어 있으면 **거부하고**, 유효한 코드만 담으면 통과하며, 그 필드가 아예 없는 봉투(스키마를 조이기 전에 기록된 옛 판정 포함)는 그대로 통과한다. ② `bin/romeo close` 는 **지금 닫으려는 산출물에 대한** 검토자 봉투가 `gate_verdict` 가 `FAIL` 인데 `fail_reasons` 가 없거나 비어 있으면 완료를 선언하지 않는다.
  - [x] AC-3 4회차를 멈춰 세운 사유가 FAIL 사유가 아님이 `core/workflows/review/SKILL.md` 에 적혀 있다 — 작업 계약과 증거의 `spec_ref.sha256` 이 확인란 체크 때문에 달라지는 것은 판정을 바꾸지 않는다는 조항이 있고, 그 근거로 `AC_TEXT_UNCHANGED`(체크 표시를 뺀 비교)와 `SPEC_UNCHANGED_SINCE_EVIDENCE`(경고 수준)를 지목한다.
  - [x] AC-4 검토자 프롬프트 `adapters/orca/prompts/reviewer-brief.md` 의 출력 예시에 `fail_reasons` 가 있고, 유효한 코드 목록이 프롬프트 본문에 인쇄된다 — 검토자가 계약을 보기 위해 다른 파일을 열지 않아도 된다.
  - [x] AC-5 회귀가 없다 — `python3 -m unittest discover -s tests -t . -v` · `bin/romeo compile --check` · `bin/romeo validate` · `bin/romeo doctor` · `bin/romeo fixtures parity --report` 가 모두 종료 코드 0 이다.
- **위험과 되돌리기:** ① 스키마를 조이면 **정당한 FAIL 도 코드가 없으면 못 낸다** — 그 경로(findings 로 적고 PASS, 사유 추가는 사람이 결정)를 `review/SKILL.md` 에 함께 적어 막다른 길을 만들지 않는다. ② **이 spec 의 1차 판단이 틀렸다(1회차 관통에서 드러났다).** `feat-20260829-license-field-46an` 의 옛 FAIL 봉투는 재검증 경로 밖이 아니다 — `fixtures/parity` 의 관측 케이스 2건(`pr-license-field-t1-observed`·`pr-license-field-t1-reviewer-observed`)이 그 봉투 8건을 직접 읽어 결과 봉투 스키마로 검증한다. 그래서 `fail_reasons` 를 조건부 **필수**로 조이면 `check-5` 와 `tests.test_parity` 가 실패한다. AC-2 를 두 겹(스키마는 값만·close 가 존재를)으로 나눈 것이 그 대응이고, 과거 판정 기록은 소급 수정하지 않는다. 특히 `run_b5cdadaffcdc-reviewer.json` 은 이번에 "FAIL 사유가 아니다" 라고 선언하는 바로 그 사유(`spec_ref.sha256` 불일치)로 FAIL 했으므로 붙일 코드가 애초에 없다. ③ `fixtures/parity` 6건은 갱신 대상이라 잘못 고치면 동등성 게이트가 깨진다 — check-5 가 잡는다. **되돌리기:** 전부 저장소 안 로컬 변경이다. `git revert <커밋>`, 미커밋이면 `git checkout -- <파일>`. 컴파일 산출물은 `bin/romeo compile` 재실행으로 복구한다.
- **결정 필요:** 없음 (수정 강도와 검증 방식은 2026-08-30 사용자 확정 — 문서 + 봉투 스키마 강제, 평소대로 관통)


## 변경 범위

- 바뀌는 파일·모듈: `core/workflows/review/SKILL.md` · `core/schemas/result-envelope.json` · `romeo/close.py` · `adapters/orca/prompts/reviewer-brief.md` · `fixtures/parity/` · `tests/` · `docs/work/feat-20260830-reviewer-fail-reasons-938r/` · `CLAUDE.md` · `AGENTS.md` · `.claude/` · `.agents/` · `.harness/compiled.yaml`
- 영향을 받는 부분: 앞으로의 모든 검토자 판정(`bin/romeo review record` 로 들어오는 봉투) · `bin/romeo close` 의 `REVIEW_VERDICT`·앵커 검사 · `bin/romeo fixtures parity` 의 표본. 관측 케이스 `pr-license-field-t1-observed`·`pr-license-field-t1-reviewer-observed` 는 이미 close 된 단위의 옛 봉투를 읽으므로, 스키마를 조이는 방식이 그 표본의 통과 여부를 정한다. `core/workflows/review/SKILL.md` 를 고치면 `bin/romeo compile` 이 `.claude/skills/` 와 `.agents/skills/` 의 사본과 `.harness/compiled.yaml` 을 갱신하므로 상한에 포함한다(직전 단위에서 이것을 빠뜨려 위임이 폐기됐다).
- 바꾸지 않는 것(비범위): FAIL 사유 **8개 목록 자체**(이번 정비는 목록을 닫고 코드를 붙이는 것이지 사유를 더하거나 빼는 것이 아니다) · `romeo/close.py` 의 **기존** 판정 로직(`AC_TEXT_UNCHANGED`·`SPEC_UNCHANGED_SINCE_EVIDENCE` 는 이미 올바르게 동작하므로 손대지 않는다 — 이번에 더하는 것은 FAIL 사유 검사 하나뿐이다) · **이미 `done` 인 단위의 판정 기록**(`docs/work/feat-20260829-license-field-46an/` 의 옛 봉투에 사유를 소급해 채우지 않는다) · `romeo/evidence.py` 의 `_spec_ref`(작업 트리 기준을 유지한다 — 승인 커밋 기준으로 바꾸면 `SPEC_UNCHANGED_SINCE_EVIDENCE` 가 자기 자신을 비교하게 되어 검사가 죽는다) · `core/schemas/task-envelope.json` · 코어 규칙(`core/principles/`) · 권한 상한(`.harness/bindings.yaml`) · 정책표(`core/policy/`) · 열린 단위 `feat-20260830-harness-defects-w3qu` 의 산출물 · `docs/planning/progress.md`(통합 뒤 별도로 갱신한다)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | FAIL 사유 8개에 코드를 붙이고 목록을 닫는다 | `core/workflows/review/SKILL.md` 의 "무엇이 FAIL 사유인가" 절 — 각 항목 제목에 코드를 붙이고, 목록 끝에 "이 목록에 없는 사유로 FAIL 을 내지 않는다. 목록 밖의 우려는 findings 로 적고 판정은 PASS 로 낸다" 를 더한다 | 소비: 없음 → 생산: 코드 8개 `AC_UNMET` · `UNAPPROVED_ACTION` · `OUT_OF_SCOPE_WRITE` · `CHECK_PLAN_CHANGED` · `EVIDENCE_NOT_RECORDED` · `CHECK_NOT_RERUNNABLE` · `ROLE_CONTRACT_VIOLATION` · `FAILED_CHECK_CLAIMED_PASS` (순서는 지금 목록 1~8 과 같다) | check-6 | `git checkout -- core/workflows/review/SKILL.md` |
| 2 | 스키마가 목록 밖 코드를 거부한다 | `core/schemas/result-envelope.json` 에 `fail_reasons` 를 더한다 — 1의 코드 8개를 `enum` 으로 갖는 **선택** 배열(`uniqueItems`)이다. **`gate_verdict` 로 조건부 필수를 걸지 않는다** — 그 필드가 없는 옛 판정 기록이 `fixtures/parity` 관측 케이스에 읽히기 때문이다(위험 ②). 기존 `anyOf` 세 갈래가 전부 `additionalProperties` 를 닫고 있으므로 세 갈래 모두에 키를 더한다 | 소비: 1의 코드 8개 → 생산: `fail_reasons` 필드 | check-7 | `git checkout -- core/schemas/result-envelope.json` |
| 3 | 종료 검사가 사유 없는 FAIL 을 막는다 | `romeo/close.py` 의 `_check_review` 에 검사를 더한다 — **지금 닫으려는 산출물에 대한** 검토자 봉투가 `gate_verdict` 가 `FAIL` 인데 `fail_reasons` 가 없거나 비면 그 검사를 실패로 낸다. 다른 산출물의 봉투(`REVIEW_SUPERSEDED`)와 `PASS`·`BLOCKED` 는 대상이 아니다 | 소비: 2의 필드 이름 → 생산: 검사 id 1개 | check-10 | `git checkout -- romeo/close.py` |
| 4 | 확인란 체크로 인한 지문 차이가 FAIL 이 아님을 명시한다 | `core/workflows/review/SKILL.md` 의 "판정을 바꾸지 않는 것" 절에 조항을 더한다 — 작업 계약의 `spec_ref.sha256` 은 승인 커밋 시점(`romeo/envelope.py`), 증거의 것은 작업 트리 시점(`romeo/evidence.py`)이라 구현자가 확인란을 체크하면 갈라지는 것이 정상이고, 하네스는 `AC_TEXT_UNCHANGED`(체크 표시를 뺀 비교)와 `SPEC_UNCHANGED_SINCE_EVIDENCE`(경고 수준)로 이를 허용한다 | 소비: 없음 → 생산: 조항 1건 | check-8 | `git checkout -- core/workflows/review/SKILL.md` |
| 5 | 검토자 프롬프트에 새 계약을 반영한다 | `adapters/orca/prompts/reviewer-brief.md` 의 출력 예시 JSON 에 `fail_reasons` 를 더하고, 그 아래 설명에 코드 8개를 인쇄한다 | 소비: 1의 코드 8개 · 2의 필드 이름 → 생산: 갱신된 프롬프트 | check-9 | `git checkout -- adapters/orca/prompts/reviewer-brief.md` |
| 6 | 앞으로의 판정 표본에 사유를 담는다 | `fixtures/parity/` 중 **FAIL verdict 를 담고 이 저장소가 소유한** 표본에 그 FAIL 에 맞는 코드를 채운다. BLOCKED 는 대상이 아니고, 이미 `done` 인 단위의 봉투를 읽는 관측 케이스 2건(`pr-license-field-t1-observed`·`pr-license-field-t1-reviewer-observed`)과 그 봉투 자체는 **손대지 않는다** | 소비: 2의 필드 이름 → 생산: 없음 | check-5 · check-1 | `git checkout -- fixtures/parity/` |
| 7 | 컴파일 산출물을 동기화한다 | `bin/romeo compile` 을 실행해 `.claude/` · `.agents/` · `.harness/compiled.yaml` 의 사본을 1·4의 변경에 맞춘다 | 소비: 1 · 4 → 생산: 갱신된 컴파일 산출물 | check-2 | `bin/romeo compile` 재실행 |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 페이로드(하네스를 부착한 프로젝트) 작업 단위의 `required_checks` 에
**하네스 자신의 테스트**를 넣지 않는다 — `python3 -m unittest discover -s tests`(하네스 저장소의 테스트),
`bin/romeo` 의 자기 검사(`compile --check` · `validate` · `doctor` · `fixtures …`)가 그것이다.
넣으면 하네스가 깨진 동안 그 페이로드 단위가 닫히지 못한다. 그 단위의 산출물은 멀쩡한데 완료가 서지 않는 것이고,
그때 고쳐야 할 것은 그 단위가 아니라 하네스다 — 두 판정을 한 검사에 묶으면 어느 쪽이 깨졌는지 구분되지 않는다
(근거: `feat-20260829-license-field-46an` 의 check-5 가 이 형태였다).
하네스 저장소 **자신**을 대상으로 하는 작업 단위에서는 그 검사들이 정당하다 — 그때는 그것이 이 단위의 산출물이기 때문이다.

**check-6~10 은 각각 하나의 AC(또는 그 한 겹)를 검사한다.** 검사가 무엇을 주장하는지 `expect` 로 적지만, 판정은 **종료 코드로만** 난다 —
`expect` 문구는 사람이 읽는 자리이고 기계는 보지 않는다(직전 관통의 결함 ②). 그러므로 각 검사는 명령 자체가 조건이 되도록
단위 테스트로 만들고, 그 테스트는 **거부 케이스를 함께 담는다** — 통과만 확인하는 검사는 구현 전에도 통과해서 빈 검사가 된다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest discover -s tests -t . -v"
    expect: exit 0
  - id: check-2
    command: "bin/romeo compile --check"
    expect: exit 0
  - id: check-3
    command: "bin/romeo validate"
    expect: exit 0
  - id: check-4
    command: "bin/romeo doctor"
    expect: exit 0
  - id: check-5
    command: "bin/romeo fixtures parity --report"
    expect: exit 0
  - id: check-6
    command: "python3 -m unittest tests.test_roles_envelopes.TestFailReasonsAreAClosedList -v"
    expect: exit 0 — AC-1. SKILL.md 에서 뽑은 코드 집합과 스키마 enum 이 정확히 같은지, 닫힌 목록 선언이 있는지 검사한다
  - id: check-7
    command: "python3 -m unittest tests.test_roles_envelopes.TestSchemaRejectsUnknownFailReasons -v"
    expect: exit 0 — AC-2 앞겹. 목록 밖 코드는 스키마가 거부하고 유효한 코드는 통과하며 필드가 없는 옛 봉투도 통과하는지 검사한다
  - id: check-8
    command: "python3 -m unittest tests.test_roles_envelopes.TestSpecHashDifferenceIsNotAFailReason -v"
    expect: exit 0 — AC-3. spec_ref 지문 차이 조항이 SKILL.md 에 있고 두 근거 검사 이름을 지목하는지 검사한다
  - id: check-9
    command: "python3 -m unittest tests.test_reviewer_brief.TestBriefCarriesFailReasons -v"
    expect: exit 0 — AC-4. 검토자 프롬프트의 출력 예시와 본문이 코드 8개를 담는지 검사한다
  - id: check-10
    command: "python3 -m unittest tests.test_docs_evidence_close.TestCloseRequiresFailReasonsOnFail -v"
    expect: exit 0 — AC-2 뒷겹. 현재 산출물의 FAIL 봉투에 사유가 없으면 close 가 완료를 선언하지 않는지 검사한다
```


## 증거

close PASS · 2026-08-30T22:51:13+09:00 · HEAD 6065efd37c68 · 검사 기록 run_c62036661689

- [evidence/run_c62036661689.yaml](evidence/run_c62036661689.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
