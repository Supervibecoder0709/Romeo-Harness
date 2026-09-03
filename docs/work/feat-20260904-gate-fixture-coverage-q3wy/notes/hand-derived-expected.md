# 손으로 먼저 적은 expected (AC-2 앞단)

`bin/romeo route --classification` 을 돌리기 **전에** 정책표(`core/policy/classification.yaml` ·
`core/policy/packages.yaml` · `core/policy/execution-guards.yaml`)를 읽고 손으로 계산한 값이다.
route 출력과의 대조 결과는 이 파일 맨 아래 「대조」 절에 적는다. 어긋난 항목은 조용히 맞추지 않고 결과에 보고한다.

## 1. fx-payment-metric-schema (gate: payment)

분류: unit=T0 · mode=delivery · intent=write · facets=[payment, analytics, data] · gates=[payment] ·
blast_radius=small · uncertainty=low

| 항목 | 손으로 적은 값 | 근거 |
| --- | --- | --- |
| profile | standard | base T0=quick → escalation `gate.any`(gates any) min standard |
| package | [spec] | base T0 |
| reviewer | opposite-runtime-readonly | base T0=none → overlay `gate.any` set_reviewer (blast.small.no-reviewer 는 unit T1 전용) |
| isolation | current | base T0 |
| blocks | [spec-ready, risk-plan-ready] | base T0 + overlay `gate.any` add_blocks |
| sections | [risk-backup-recovery] | overlay `gate.any` |
| guards | [payment-charge] | triggers {facets:[payment,ai-cost], intent:[write,deploy,mixed]} |
| parts | [superpowers] | overlay `profile.standard-or-deeper` |
| gate 힌트 | payment 만 힌트, 체크됨 → GATE_HINT_UNCHECKED 없음 | hint_facets payment × intent write |

## 2. fx-landing-consent-copy (gate: legal)

분류: unit=T1 · mode=delivery · intent=write · facets=[legal, privacy, ui, copy] ·
gates=[legal, privacy-security] · blast_radius=small · uncertainty=low

| 항목 | 손으로 적은 값 | 근거 |
| --- | --- | --- |
| profile | standard | base T1=standard, `gate.any` min standard = kept |
| package | [brief, spec] | base T1 |
| reviewer | opposite-runtime-readonly | base T1 + `gate.any`. `blast.small.no-reviewer` 는 `gates: none` 조건이라 발동 안 함 |
| isolation | worktree | base T1 |
| blocks | [spec-ready, risk-plan-ready] | base T1 + `gate.any` |
| sections | [risk-backup-recovery, ui-state-table] | `gate.any` + `facet.ui` |
| guards | [] | intent=write · facets 에 payment/ai-cost/ops-data/migration 없음 · actions 없음 |
| parts | [design-ui, superpowers] | `facet.ui` + `profile.standard-or-deeper` |
| gate 힌트 | legal(write) · privacy-security(any) 둘 다 힌트, 둘 다 체크됨 | |

## 3. fx-ops-test-data-purge (gate: ops-data-deletion)

분류: unit=T1 · mode=delivery · intent=delete · facets=[ops-data] · gates=[ops-data-deletion] ·
blast_radius=large · uncertainty=medium

| 항목 | 손으로 적은 값 | 근거 |
| --- | --- | --- |
| profile | deep | base T1=standard → `gate.ops-boundary`(gates_any ops-data-deletion × blast large) min deep |
| package | [brief, spec] | base T1 |
| reviewer | opposite-runtime-readonly | base T1 + `gate.any` |
| isolation | worktree | base T1 |
| blocks | [spec-ready, risk-plan-ready] | base T1 + `gate.any` |
| sections | [risk-backup-recovery, environment-plan] | `gate.any` + `gate.ops-boundary`(packages) |
| guards | [deletion, ops-data-change] | deletion{intent delete} · ops-data-change{facets ops-data × intent delete} |
| parts | [superpowers] | `profile.standard-or-deeper`(intent delete 포함) |
| warnings | WORKTREE_ISOLATES_CODE_ONLY | `gate.ops-boundary` add_warnings |

## 4. fx-public-kpi-endpoint (gate: public-api)

분류: unit=T1 · mode=delivery · intent=write · facets=[public-api, analytics] · actions=[expose] ·
gates=[public-api] · blast_radius=medium · uncertainty=low

| 항목 | 손으로 적은 값 | 근거 |
| --- | --- | --- |
| profile | standard | base T1=standard, `gate.any` kept. blast medium 이라 `blast.large` 미발동 |
| package | [brief, spec] | base T1 |
| reviewer | opposite-runtime-readonly | base T1 + `gate.any` |
| isolation | worktree | base T1 |
| blocks | [spec-ready, risk-plan-ready] | base T1 + `gate.any` |
| sections | [risk-backup-recovery] | `gate.any` |
| guards | [public-exposure] | triggers {actions:[publish, share, expose]} |
| parts | [superpowers] | `profile.standard-or-deeper` |

## 5. fx-free-plan-retention-cut (gate: irreversible-policy)

분류: unit=T1 · mode=delivery · intent=write · facets=[policy] · gates=[irreversible-policy] ·
blast_radius=large · uncertainty=low

| 항목 | 손으로 적은 값 | 근거 |
| --- | --- | --- |
| profile | deep | base T1=standard → `blast.large`(blast large × unit T1) min deep |
| package | [brief, spec] | base T1 |
| reviewer | opposite-runtime-readonly | base T1 + `gate.any` |
| isolation | worktree | base T1 |
| blocks | [spec-ready, risk-plan-ready] | base T1 + `gate.any` |
| sections | [risk-backup-recovery] | `gate.any`. `gate.ops-boundary` 는 gates_any 에 irreversible-policy 가 없어 미발동 |
| guards | [] | intent=write · facets=[policy] 는 어떤 guard trigger 에도 없음 · actions 없음 |
| parts | [superpowers] | `profile.standard-or-deeper` |

## 대조

`bin/romeo route --classification <분류> --json` 을 5건 각각에 돌려 위 표와 대조했다.

**어긋난 항목 0건.** profile · package · reviewer · isolation · blocks · sections · guards · parts · warnings ·
gate_hints 전부 손으로 적은 값과 같았다. route 출력을 보고 `expected` 를 고친 항목은 없다 —
fixture 5건의 `expected` 는 위 표를 그대로 옮긴 것이다.

route 가 낸 `fired_rules` 로 근거를 다시 확인했다.

| fixture | fired_rules |
| --- | --- |
| 1 | `profile:base:T0=quick` · `profile:gate.any->standard` · `overlay:gate.any` · `overlay:profile.standard-or-deeper` · `guard:payment-charge` |
| 2 | `profile:base:T1=standard` · `profile:gate.any=kept` · `overlay:gate.any` · `overlay:facet.ui` · `overlay:profile.standard-or-deeper` · `warn:PART_PENDING_GATE` |
| 3 | `profile:base:T1=standard` · `profile:gate.ops-boundary->deep` · `overlay:gate.any` · `overlay:gate.ops-boundary` · `warn:WORKTREE_ISOLATES_CODE_ONLY` · `guard:ops-data-change` · `guard:deletion` |
| 4 | `profile:base:T1=standard` · `overlay:gate.any` · `overlay:profile.standard-or-deeper` · `guard:public-exposure` |
| 5 | `profile:base:T1=standard` · `profile:blast.large->deep` · `overlay:gate.any` · `overlay:profile.standard-or-deeper` |

## 양쪽 실측 (AC-5)

check-1 이 판별 검사인지, check-2 가 회귀 방지 검사인지를 두 상태에서 실행해 확인했다.
「이전 상태」 는 이 단위가 추가한 fixture 5건을 치운 상태다(작업 트리에서 실제로 치웠다가 되돌렸다).

| 검사 | 이전 상태 (fixture 33건) | 지금 상태 (38건) | 판정 |
| --- | --- | --- | --- |
| check-1 `python3 -m unittest tests.test_gate_coverage` | **exit 1** (failures=5, errors=1) | exit 0 | 판별 검사 — 이 단위가 없으면 실패한다 |
| check-2 `bin/romeo route --fixtures fixtures/requests --report` | exit 0 (33/33 일치) | exit 0 (38/38 일치) | 회귀 방지 검사 — 양쪽에서 통과하는 것이 정의다 |

「그럴듯한 거짓 구현」 반례는 검사 안에 있다 —
`TestGateCoverageDiscriminates.test_a_hardcoded_implementation_passes_the_renamed_policy_table` 이
개명된 정책표 하나를 두 구현에 돌려, 정책표를 읽는 구현은 실패하고 id 를 하드코딩한 구현은 통과하는 것을 매 실행마다 보인다.

## 사용자 확인 (재승인된 AC-2)

2026-09-04, 사용자가 위 5건의 `classification` 과 항목별 `expected` 대조표를 확인하고 확정했다(어긋난 항목 0건).
그 확인 사실은 fixture 5건 각각의 `human_correction` 에 기록돼 있다 —
`reviewed_at: '2026-09-04'` · `reviewed_by: user` · `round: gate-coverage` · `verdict: confirmed` · `changes: []`.

자기참조를 끊는 자리는 「route 보다 먼저 적었다」는 시간 순서가 아니라 이 사람의 확인이다(재승인 사유 참조).
`bin/romeo route --fixtures fixtures/requests --report` 는 회귀 방지 검사로 남는다.
