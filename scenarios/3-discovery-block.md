# 시나리오 3 — 조사 없이 구현으로 넘어가는 것을 막는다

해법 자체가 미정인 요청(`mode: discovery`)이 조사 결과 없이 구현 승인으로 넘어가는 것을 막는다.
같은 자리에서 T2 이니셔티브가 마일스톤 계획 없이 열리는 것도 막는다.

이 시나리오가 필요한 이유는 **차단이 계산만 되고 아무것도 막지 않던 상태**가 있었기 때문이다.
라우터는 `blocks: [spec-ready, discovery-result]` 를 계산해 분류 카드에 인쇄까지 했지만,
`romeo approve` 도 `romeo close` 도 그 값을 한 번도 읽지 않았다(2026-09-01 실측).
차단은 표시가 아니라 **집행**이어야 한다.

그 집행을 붙인 뒤에도 두 번째 결함이 남아 있었다. 차단이 전부 `enforced_at: [approve, close]` 로
일괄 배치돼, `discovery-result` 가 "구현 위임을 막는다" 면서 실제로는 **승인**을 막았다 —
조사 단위의 일이 곧 조사인데 조사 결과를 먼저 요구하니 조사를 시작할 창구가 없었다.
충족 조건도 `inputs:` 가 비었는지만 봐서 `"ㅁㄴㅇㄹ"` 로 통과했고, 조사 계획이 사는 `brief.md` 는
승인도 종료도 한 글자도 읽지 않았다. 이 런북은 그 세 자리를 고친 뒤의 판정을 고정한다.

## 집행 지점

| 차단 | `enforced_at` (막기 시작하는 사건) | `reads` (정본 입력) |
| --- | --- | --- |
| `spec-ready` | `approve` | `spec` |
| `milestone-plan` | `approve` | `charter` |
| `discovery-result` | `dispatch` — 작업 계약을 쓰는 자리 | `brief\|charter` |
| `risk-plan-ready` | `approve` | `spec` |

막기 시작하는 사건은 차단마다 **하나**다. 종료는 그와 별개로 걸린 차단을 **전부** 다시 보는
backstop 이다 — 승인이나 위임 뒤에 조건이 무너지는 것을 잡을 자리가 그것 하나뿐이기 때문이다.
되돌리기 어려운 **실행**의 승인은 차단이 아니라 `guards` 가 소유한다.

## 전제

- fixture `fixtures/requests/fx-discord-computer-use-automation.yaml` — 실제 요청에서 온 discovery 분류다.
  사람이 `mode: experiment` → `discovery` 로 교정한 기록이 그 파일의 `human_correction` 에 있고,
  교정 사유가 바로 "되는지 확인하기 전에 구현이 나가지 않도록 dispatch 를 차단해야 한다" 였다.
- fixture `fixtures/requests/fx-s16-edu-webapp-new.yaml` — 새 프로젝트 T2 분류다.
- 정책표의 차단 카탈로그(`core/policy/packages.yaml` 의 `blocks:`)와 집행 매핑(`romeo/blocks.py` 의 `BLOCK_CHECKS`).

## 단계

1. discovery fixture 의 분류를 라우터에 넣는다 — `bin/romeo route --json` 또는 `romeo.policy.route()`.
2. 그 라우팅으로 문서 패키지를 만든다 — `brief.md` + `spec.md`, 「조사·가설·검증 계획」 절이 붙는다.
3. spec 의 확인란·검증 계획과 brief 를 채우고 `romeo approve` 를 한다. **조사 산출물은 아직 붙이지 않았다.**
   이어서 `romeo envelope build` 로 구현자 계약을 만들어 본다.
4. 조사 산출물을 **brief 의** frontmatter `inputs:` 에 링크로 붙이고 계약을 다시 만든다.
   중간에 세 가지 그럴듯한 거짓 값을 넣어 본다 — 경로가 아닌 문자열 · 없는 경로 · spec 에 붙인 링크.
5. T2 fixture 의 분류로 문서 패키지를 만든다 — `charter.md` + `brief.md` + `spec.md`.
6. charter 의 「마일스톤 계획」이 `NEEDS_INPUT` 인 채로 승인을 시도한다.
7. 마일스톤 계획을 채우고 다시 승인한다.
8. 승인된 단위를 구현·증거까지 진행해 `romeo close` 를 돌린다.
9. 이미 `done` 인 단위에서 차단 조건을 무너뜨리고 `romeo close` 를 다시 돌린다.

## 기대 판단

| 단계 | 하네스가 내야 하는 판정 | 근거 |
| --- | --- | --- |
| 1 | `blocks` 가 `[spec-ready, discovery-result]` 다. `parts` 에 `bmad-cis` 가 추천되고 `status` 는 부착이 아니라 **채택 결정**(`accepted`)을 말한다 — 부착되지 않았으므로 `PART_PENDING_GATE` 경고가 함께 뜬다 | overlay `mode.discovery` · K-63 |
| 1 | 추천 부품의 `output_binding` 이 `inputs-link` 다 — 산출물은 복사가 아니라 링크다 | K-62 |
| 2 | `brief.md` 에 「조사·가설·검증 계획」 절이 생긴다(T1 은 brief 가 있으므로 charter fallback 을 쓰지 않는다) | section `discovery-plan` |
| 3 | **승인은 된다** (`status: active`). 조사를 시작할 창구를 막지 않는다 | `enforced_at: [dispatch]` |
| 3 | **계약 생성 거부.** 메시지에 `discovery-result` 와 "inputs: 가 비어 있다" 가 나오고 `task/` 가 만들어지지 않는다 | 차단 `discovery-result` |
| 4 | 경로가 아닌 문자열 · 없는 경로 · spec 에 붙인 링크 **셋 다 거부된다.** 실재하는 brief 링크에서만 계약이 만들어지고, 그때 `attempts.yaml` 에 회차가 남는다 | 충족은 문장이 참인가 · Q-27 |
| 4 | brief 가 `NEEDS_INPUT` 인 채면 링크가 실재해도 계약이 만들어지지 않는다 | 미완료 검사가 패키지 전체를 본다 |
| 5 | `charter.md` 가 `NOT_AVAILABLE_YET` 없이 생성되고 「마일스톤 계획」 절을 갖는다 | 문서 `charter` |
| 6 | **승인 거부.** 메시지에 `milestone-plan` 이 나온다 | 차단 `milestone-plan` |
| 7 | 승인된다 | — |
| 8 | 걸린 차단마다 `BLOCK_SATISFIED` 검사가 인쇄된다 — 위임에서 막는 차단도 포함이다(backstop) | AC-4 |
| 8 | 닫기 전에 조사 링크를 지우면 `BLOCK_SATISFIED` 가 실패한다 | 종료는 backstop 이다 |
| 9 | 판정은 `FAIL`·`NOT_ALREADY_DONE` 그대로이고 `BLOCK_SATISFIED` 는 나오지 않는다. 문서도 바뀌지 않는다 | 차단은 소급하지 않는다 |

**막는 것이 판정이다.** 3(계약 생성)·4(거짓 값 셋)·6 단계가 통과하면 이 시나리오는 실패다 —
통과만 보이는 런북은 빈 검사와 같다. 반례는 **빈 값이 아니라 그럴듯한 거짓 값**이어야 한다:
빈 값은 고치기 전에도 막혔고, 통과한 것은 있는 척하는 값이었다.

## 산출물

- 이 런북과 `scenarios/README.md`.
- 자동 실행이 만드는 작업 단위 문서는 전부 임시 저장소 안에서 만들어지고 사라진다 —
  시나리오가 이 저장소의 `docs/work/` 를 오염시키지 않는다.

## 증거

`tests/test_scenario_3.py` 가 위 9단계를 그대로 실행한다. 단계 번호는 테스트 메서드 이름에 들어 있다.
실행: `python3 -m unittest tests.test_scenario_3`
