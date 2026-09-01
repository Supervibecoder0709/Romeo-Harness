# 시나리오 3 — 조사 없이 구현으로 넘어가는 것을 막는다

해법 자체가 미정인 요청(`mode: discovery`)이 조사 결과 없이 구현 승인으로 넘어가는 것을 막는다.
같은 자리에서 T2 이니셔티브가 마일스톤 계획 없이 열리는 것도 막는다.

이 시나리오가 필요한 이유는 **차단이 계산만 되고 아무것도 막지 않던 상태**가 있었기 때문이다.
라우터는 `blocks: [spec-ready, discovery-result]` 를 계산해 분류 카드에 인쇄까지 했지만,
`romeo approve` 도 `romeo close` 도 그 값을 한 번도 읽지 않았다(2026-09-01 실측).
차단은 표시가 아니라 **집행**이어야 한다.

## 전제

- fixture `fixtures/requests/fx-discord-computer-use-automation.yaml` — 실제 요청에서 온 discovery 분류다.
  사람이 `mode: experiment` → `discovery` 로 교정한 기록이 그 파일의 `human_correction` 에 있고,
  교정 사유가 바로 "되는지 확인하기 전에 구현이 나가지 않도록 dispatch 를 차단해야 한다" 였다.
- fixture `fixtures/requests/fx-s16-edu-webapp-new.yaml` — 새 프로젝트 T2 분류다.
- 정책표의 차단 카탈로그(`core/policy/packages.yaml` 의 `blocks:`)와 집행 매핑(`romeo/blocks.py` 의 `BLOCK_CHECKS`).

## 단계

1. discovery fixture 의 분류를 라우터에 넣는다 — `bin/romeo route --json` 또는 `romeo.policy.route()`.
2. 그 라우팅으로 문서 패키지를 만든다 — `brief.md` + `spec.md`, 「조사·가설·검증 계획」 절이 붙는다.
3. spec 의 확인란·검증 계획을 채우고 `romeo approve` 를 시도한다. **조사 산출물은 아직 붙이지 않았다.**
4. 조사 산출물을 frontmatter 의 `inputs:` 에 링크로 붙이고 다시 승인한다.
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
| 3 | **승인 거부.** 메시지에 `discovery-result` 와 "inputs: 가 비어 있다" 가 나온다 | 차단 `discovery-result` |
| 4 | 승인된다 (`status: active`, `approved_at` 기록) | — |
| 5 | `charter.md` 가 `NOT_AVAILABLE_YET` 없이 생성되고 「마일스톤 계획」 절을 갖는다 | 문서 `charter` |
| 6 | **승인 거부.** 메시지에 `milestone-plan` 이 나온다 | 차단 `milestone-plan` |
| 7 | 승인된다 | — |
| 8 | 걸린 차단마다 `BLOCK_SATISFIED` 검사가 인쇄된다 | AC-4 |
| 9 | 판정은 `FAIL`·`NOT_ALREADY_DONE` 그대로이고 `BLOCK_SATISFIED` 는 나오지 않는다. 문서도 바뀌지 않는다 | 차단은 소급하지 않는다 |

**막는 것이 판정이다.** 3·6 단계가 통과하면 이 시나리오는 실패다 — 통과만 보이는 런북은 빈 검사와 같다.

## 산출물

- 이 런북과 `scenarios/README.md`.
- 자동 실행이 만드는 작업 단위 문서는 전부 임시 저장소 안에서 만들어지고 사라진다 —
  시나리오가 이 저장소의 `docs/work/` 를 오염시키지 않는다.

## 증거

`tests/test_scenario_3.py` 가 위 9단계를 그대로 실행한다. 단계 번호는 테스트 메서드 이름에 들어 있다.
실행: `python3 -m unittest tests.test_scenario_3`
