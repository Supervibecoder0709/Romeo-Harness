# 시나리오 8 — 없는 능력을 있는 것처럼 쓰는 것을 막는다

능력이 필요한 요청에서 하네스가 **필요 능력·프로브 결과·대안을 카드에 인쇄**하고,
「능력 확인」 절에 **사실과 다른 결과를 적으면 승인을 막는다.**

이 시나리오가 필요한 이유는 요구하는 자리와 보는 자리가 어긋나 있었기 때문이다.
라우터는 `browser-automation` 요청에 「능력 확인」 절을 걸었지만 **그 절을 채울 프로브가 없었고**
(`capabilities.yaml` 에는 기획 부품의 설치 흔적 하나뿐이었다) **카드는 프로브 결과를 한 줄도 인쇄하지
않았다.** 절의 충족은 미완료 토큰 검사뿐이라, `NEEDS_INPUT` 을 아무 글자로 바꾸기만 하면 통과했다 —
그 자리에 글자가 있는지를 본 것이지 그 문장이 참인지를 본 것이 아니다(AGENTS.core §11).

**부재는 막지 않는다.** 막는 것은 거짓이다. 능력이 없다는 사실 자체로 승인을 막으면
「되는지 조사해 보자」 라는 요청이 통째로 불가능해진다(Q-28) — 그리고 그것이 이 fixture 의 원래 요청이다.

## 집행 지점

| 무엇 | 어디 | 무엇이 참이어야 하나 |
| --- | --- | --- |
| 능력 정의(`why`·`alternatives`·`honesty`) | `core/policy/capabilities.yaml` | 코어는 **흔적 경로를 모른다**(C-C6) |
| 흔적 경로 | `adapters/*/adapter.yaml` 의 `capability_markers` | 어댑터가 경로를 주지 않으면 그 런타임에서 `absent` |
| 요구 능력 계산 | overlay `facet.browser-automation` 의 `add_capabilities` | 라우팅 출력 `capabilities` 에 실린다 |
| 인쇄 | `romeo card` | 부품에 붙지 않은 능력도 결과·대안과 함께 인쇄한다 |
| 대조 | 차단 `capability-probed` · `enforced_at: [approve]` · `reads: spec` | 표가 프로브가 **실제로 낸 값**과 같다 |

요구(정책표)·정의(능력 카탈로그)·대조(차단)가 어긋나면 **정책 로드가 실패한다**
(`romeo.blocks.capability_defects`). 요구를 적고 집행을 잊는 것이 이 하네스가 반복해 온 결함의 모양이다.

## 전제

- fixture `fixtures/requests/fx-discord-computer-use-automation.yaml` — 실제 요청에서 온
  `browser-automation` 분류다. 요청 자체가 "이 능력으로 되는지 알려달라" 이므로, 부재를 막으면
  이 요청은 시작할 수 없다.
- 제안 fixture `fixtures/proposals/fx-discord-computer-use-automation.yaml` — 카드 렌더링 입력.
- 능력 카탈로그의 `automation.ui-control`·`automation.tool-server`, 그리고 두 어댑터의 `capability_markers`.
- 이 저장소에는 두 능력의 흔적 파일이 **없다**. 그래서 정직한 표는 `absent` 두 줄이다.

## 단계

1. fixture 의 분류를 라우터에 넣는다 — `bin/romeo route --json` 또는 `romeo.policy.route()`.
2. 같은 제안으로 카드를 만든다 — `bin/romeo card --proposal fixtures/proposals/fx-discord-computer-use-automation.yaml`.
3. 그 라우팅으로 문서 패키지를 만든다 — `brief.md` + `spec.md`, spec 에 「능력 확인」 절이 붙는다.
4. 표를 **그럴듯한 거짓 값**으로 채우고 `romeo approve` 를 시도한다. 넷을 각각 따로 시도한다.
   ① `absent` 인 능력을 `present` 라고 적는다.
   ② 프로브 칸에 카탈로그에 없는 id 를 적는다(형태는 그럴듯하게).
   ③ `absent` 는 사실대로 적고 **대안 칸만 비운다.**
   ④ 라우터가 요구한 능력 중 하나만 적고 하나를 뺀다.
5. 표를 사실대로(`absent` 두 줄 + 대안) 채우고 다시 승인한다.
6. 어댑터가 흔적 경로를 주지 않는 능력을 프로브한다 — 그 런타임에서 `absent` 인지 본다.
7. 임시 저장소에 흔적 파일을 만들었다 지운다. 라벨이 `present` ↔ `absent` 로 뒤바뀌는지 본다.
8. 프로브를 실행한 뒤 저장소의 파일 목록이 실행 전과 같은지 본다.

## 기대 판단

| 단계 | 하네스가 내야 하는 판정 | 근거 |
| --- | --- | --- |
| 1 | 라우팅 출력의 `capabilities` 가 `[automation.ui-control, automation.tool-server]` 이고 `blocks` 에 `capability-probed` 가 있다. 다른 facet 의 요청은 `capabilities` 가 **빈 목록**이다 | overlay `facet.browser-automation` |
| 2 | 카드에 두 능력이 **각각** 프로브 결과와 대안과 함께 나온다. 그 능력은 어느 부품에도 붙어 있지 않다 — 부품 절에만 프로브를 매달면 한 줄도 인쇄되지 않던 자리다 | AC-4 |
| 3 | spec 에 「능력 확인」 절이 생기고 표의 열이 `능력 \| 프로브 \| 결과 \| 대안` 이다 | section `capability-check` |
| 4① | **승인 거부.** 이유에 프로브가 낸 값(`absent`)과 표에 적힌 값(`present`)이 함께 나온다 | 거짓을 막는다 |
| 4② | **승인 거부.** 이유에 "능력 카탈로그에 없다" 가 나온다 | 실재하지 않는 프로브의 결과는 결과가 아니다 |
| 4③ | **승인 거부.** 이유에 "대안 칸이 비어 있다" 가 나온다 | 부재만 적고 대안을 안 적으면 구현자가 우회한다 |
| 4④ | **승인 거부.** 이유에 빠진 능력 id 가 나온다 | 요구와 표를 대조한다 |
| 5 | **승인된다** (`status: active`). `absent` 두 줄이 그대로 남는다 — 능력 부재는 승인을 막지 않는다 | Q-28 |
| 6 | 경로를 주지 않은 런타임의 라벨이 `absent` 이고, 이유가 "경로 선언 없음" 이다 | AC-2 |
| 7 | 흔적 파일이 있으면 `present`, 지우면 `absent` 로 **되돌아온다** | AC-2 |
| 8 | 파일 목록이 실행 전과 **같다.** 프로브는 읽기만 한다 — 자동 설치 금지 | AC-8 |

**막는 것이 판정이다.** 4 단계의 네 값이 하나라도 통과하면 이 시나리오는 실패다.
반례는 **빈 값이 아니라 그럴듯한 거짓 값**이어야 한다 — 빈 값(`NEEDS_INPUT`)은 고치기 전에도 막혔고,
통과한 것은 형태가 그럴듯하고 내용이 거짓인 값이었다.

## 구현자가 `BLOCKED_CAPABILITY` 로 끝내야 하는 자리

승인이 난 뒤(5 단계) 구현자가 작업 계약을 받았다고 해서 능력이 생기는 것은 아니다.
아래 자리에서 구현자는 **가능한 척 우회하지 않고** 결과 봉투의 `blocked_reason` 을
`BLOCKED_CAPABILITY` 로 적고 끝낸다(`core/workflows/implement/SKILL.md` 「실패 처리」).

- 계약의 작업이 표에서 `absent` 인 능력을 **실제로 써야만** 완료되는 경우.
  「능력 확인」 표에 대안이 적혀 있어도 그 대안이 이 계약의 범위 밖이면 마찬가지다 — 범위를 넓히는 것은
  구현자의 권한이 아니다(K-66). 승인된 범위 안에서 할 수 있는 것까지 하고, 남은 것을 그 이유로 끝낸다.
- 그 능력을 **설치·활성화하면 될 것 같은** 경우. 자동 설치는 금지다(K-66) — 흔적 파일을 만드는 것도
  설치다. 프로브가 `present` 로 바뀌는 변경을 구현자가 스스로 하지 않는다.
- 표에 적힌 라벨과 실행 중 관찰한 사실이 다른 경우. 표를 고쳐 맞추지 않는다 — 그것은 증거가 아니라
  주장을 고치는 것이다. 재승인 대상이다(D-27).

`BLOCKED_CAPABILITY` 는 실패가 아니라 **정상 경로**다. 없는 능력을 있는 것처럼 쓰고 완료를 선언하는 것이 실패다.

## 산출물

- 이 런북과 `scenarios/README.md` 의 목록 한 줄.
- 자동 실행이 만드는 작업 단위 문서는 전부 임시 저장소 안에서 만들어지고 사라진다 —
  시나리오가 이 저장소의 `docs/work/` 를 오염시키지 않는다.

## 증거

`tests/test_scenario_8.py` 가 위 8단계를 그대로 실행한다. 단계 번호는 테스트 메서드 이름의 `stepN` 에 있다.
실행: `python3 -m unittest tests.test_scenario_8`
