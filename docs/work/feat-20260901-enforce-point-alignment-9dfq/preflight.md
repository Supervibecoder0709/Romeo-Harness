# 승인 전 검사 가능성 증명 (preflight)

`spec.md` 의 `required_checks` 12건을 **승인 전에** 두 방향으로 실제 실행한 기록이다.
새 검사는 기존 상태에서 실패하고 가상 완료 상태에서는 성공해야 한다. 한쪽만 보인 검사는
승인 대상이 아니다 — 통과만 보이면 빈 검사이고, 실패만 보이면 통과 불가능한 검사다.

- 실행일: 2026-09-01
- 음성 증명 대상 트리: `29fdb6b` + 이 작업 단위의 미커밋 문서
- 양성 증명 대상 트리: `git archive HEAD` 사본에 **기계적 스텁**만 얹은 것
  (`ENFORCE_POINTS` 3원소 · `approval-gate`→`risk-plan-ready` 일괄 치환 ·
  차단 4개의 `enforced_at` 단일화와 `reads` 추가 · 절 12개에 `enforcement` 추가 ·
  `tests/test_enforce_points.py` 빈 클래스 5개(23케이스) · 규칙·결정·질문·런북 한 줄 스텁)
  — 스텁은 **구현이 아니다.** 검사가 도달 가능한 상태를 지목하는지만 본다. 실행 뒤 폐기했다.

## 판정

| 검사 | 현재 트리 | 가상 완료 | 판정 |
| --- | ---: | ---: | --- |
| check-1 | exit 1 | exit 0 | 성립 |
| check-2 | exit 1 | exit 0 | 성립 |
| check-3 | exit 1 | exit 0 | 성립 |
| check-4 | exit 1 | exit 0 | 성립 |
| check-5 | exit 1 | exit 0 | 성립 |
| check-6 | exit 1 | exit 0 | 성립 |
| check-7 | exit 1 | exit 0 | 성립 |
| check-8 | exit 1 | exit 0 | 성립 |
| check-9 | exit 1 | exit 0 | 성립 |
| check-10 | exit 1 | exit 0 | 성립 |
| check-11 (grep 부분) | exit 1 | exit 0 | 성립 |
| check-12 | **exit 0** | **exit 1** | 회귀 가드 — 아래 참조 |

check-11 의 뒤쪽 `python3 -m unittest discover -s tests` 는 전체 스위트(약 100초)라 이 표에서는
앞쪽 grep 두 개만 판정했다. 전체 스위트는 아래 「양성 증명이 드러낸 것」 에 별도로 적는다.

## 이 증명이 실제로 잡은 것 2건

### ① 빈 검사 하나를 승인 전에 걷어냈다

첫 초안의 check-11 은 `grep -q 'dispatch' scenarios/3-discovery-block.md` 였다.
**현재 트리에서 exit 0 이었다** — 그 낱말이 런북 본문에 이미 있었기 때문이다
(「구현 dispatch 를 차단한다」). 무엇을 확인하는지 적혀 있는 채로 아무것도 확인하지 않는
검사였다(Q-21 과 같은 모양). 앵커를 `enforced_at`(런북, 현재 0회)과 `dispatch`(시나리오 테스트
소스, 현재 0회)로 바꿔 음성 증명이 서게 했다.

### ② 설계 결함 하나를 AC 로 끌어올렸다

「차단마다 막는 사건을 **하나만** 선언한다」 를 기계적으로 적용했더니 가상 완료 상태에서
`tests/test_blocks_enforcement.py::TestCloseReportsBlockSatisfied` 3건이 깨졌다 —
`close` 가 차단을 **보고하는** 자리까지 함께 사라진 것이다. 그것은 바로 앞 단위(a3xs)의 AC-4 이고,
승인 뒤 조건이 무너지는 것을 잡는 유일한 자리다.

**막는 사건은 하나, 보고는 종료에서도** 로 설계를 갈라 AC-1 에 명시하고, 그 계약을 붙드는
check-12 를 회귀 가드로 추가했다. check-12 가 현재 트리에서 통과하고 기계적 스텁에서
실패하는 것이 그 계약이 실재한다는 증거다 — 이 표에서 유일하게 방향이 반대인 행인 이유다.

## 양성 증명이 드러낸 것 — 실제 작업량

기계적 스텁 상태에서 모듈별 전체 스위트를 돌린 결과다. 옛 집행 지점을 단언하는 테스트가
정확히 **12건**이고, 나머지는 그대로 통과한다.

| 모듈 | 결과 |
| --- | --- |
| `tests.test_policy` | 21건 OK — 개명·`reads`·`enforcement` 키가 정책 로드를 깨지 않는다 |
| `tests.test_docs_evidence_close` | 105건 OK |
| `tests.test_run_unit` | 34건 OK |
| `tests.test_blocks_enforcement` | 30건 중 **10건 실패** |
| `tests.test_scenario_3` | 11건 중 **2건 실패** |

다시 써야 하는 12건:

```
TestApproveRejectsUnsatisfied.test_message_names_every_unmet_block_at_once
TestBlockCatalog.test_catalog_exists_with_the_four_blocks
TestBlockCatalog.test_every_used_block_is_in_catalog_and_in_enforcement
TestCatalogMappingMismatch.test_unknown_enforcement_point_fails_the_load
TestCloseReportsBlockSatisfied.test_close_fails_when_a_block_breaks_after_approval
TestCloseReportsBlockSatisfied.test_every_block_on_the_unit_gets_a_row
TestCloseReportsBlockSatisfied.test_t0_close_reports_spec_ready_and_passes
TestDiscoveryResultNeedsInputs.test_blank_entries_do_not_count_as_inputs
TestDiscoveryResultNeedsInputs.test_empty_inputs_blocks_approval
TestNoRetroactiveEffect.test_open_unit_still_gets_block_rows
TestScenario3.test_step3_approval_is_refused_without_research_inputs
TestScenario3.test_step8_close_reports_one_block_satisfied_row_per_block
```

이 12건이 구현 단위 8 의 범위다. 승인 전에 이름까지 확정했으므로 구현자가 "얼마나 깨질지"
를 추정하지 않는다.

## 이 증명이 말하지 않는 것

- 스텁은 구현이 아니다. 검사가 **도달 가능한 상태를 지목하는지**만 증명했다.
  같은 검사가 통과하면서 의도한 동작이 없을 가능성은 이 표가 배제하지 않는다 —
  그것은 AC-9(그럴듯한 거짓 값 반례)와 검토자가 본다.
- `dispatch` 훅을 어디에 걸지는 아직 미확인이다. 구현 단위 1 이 세 경로에서 실측한다.
- 요청 fixture 5건은 일괄 치환으로 통과했다. 치환이 의미상 옳은지는 검토자가 본다.
