---
id: feat-20260901-scenario-8-capability-probe-s7ny
type: spec
title: 없는 능력을 있는 것처럼 쓰는 것을 막는다 — 능력 프로브·부재 카드·시나리오 8
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: done
approved_at: '2026-09-02T00:08:52+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-09-02T00:45:28+09:00'
parent: null
inputs: []
evidence: [evidence/run_7c32a145569d.yaml, evidence/run_de465802c277.yaml, evidence/run_d7092f3d25c5.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-01'
updated: '2026-09-02'
approval_history:
- {approved_at: '2026-09-01T21:42:52+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-01T22:28:19+09:00',
  reason: '변경 범위가 산문이라 allowed_paths 가 담지 못한 파일 8개를 백틱 경로로 명시한다 — 새 차단 capability-probed 를 추가하면 차단 목록을
    하드코딩한 기존 검사 25건과 fixture 기대값 3건이 따라와야 하고, 차단 판정에 라우터 컨텍스트를 넘기려면 docs.py·close.py 의 호출부 배선이 필요하다. 함께
    check-3 을 고친다: 종전 명령은 fixture 불일치 3건에도 exit 0 이라 아무것도 판정하지 않는 빈 검사였다(실측). 새 명령은 불일치 행이 있으면 실패한다 —
    구현 전 트리 exit 0, 현재 구현 트리 exit 1 로 양쪽을 확인했다.'}
- {approved_at: '2026-09-01T22:28:19+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-01T23:00:08+09:00',
  reason: 'AC-10 이 달성 불가능했다 — 이 단위의 산출물인 tests/test_scenario_8.py 에 대해 ''고친 뒤 성공하는 것을 승인 전에 보인다'' 를 요구했는데,
    그러려면 승인 전에 구현해야 하고 그것은 D-27 위반이다. 검토자가 3회차에서 AC_UNMET 으로 잡았다(ac10-before-state 가 승인 22:28:19 뒤인 22:46:05
    에 돌았다 — 사실관계는 정확하다). 문장을 실행 가능한 것으로 고친다: 고치기 전 실패는 base 리비전 트리에 그 테스트만 얹어 재현해 증거로 남기고, 고친 뒤 성공은 check-1
    이 보인다. §11 이 요구하는 양쪽 보이기의 목적(빈 검사·통과 불가능한 검사를 승인하지 않는다)은 그대로 지킨다. 구현본과 증거는 바꾸지 않는다.'}
- {approved_at: '2026-09-01T23:00:08+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-02T00:08:52+09:00',
  reason: '4회차 검토자 finding ② 의 수정 자리가 romeo/cli.py 인데 승인된 「변경 범위」에 없어 allowed_paths 밖이었다(K-66). 카드가 프로브할
    저장소는 --root 가 정하는데 cmd_card 와 cmd_route --card 두 자리 모두 render_card 에 root 를 넘기지 않는다 — 검토자는 cmd_card
    만 지목했고 구현자가 실측으로 두 자리를 찾았다. 변경 범위에 그 파일과 두 호출부를 명시한다. AC 문장은 바꾸지 않는다 — 요구를 좁히는 것이 아니라 승인된 쓰기 상한이 결함
    위치를 담지 못한 것이고, 이는 approval_history 첫 항목과 같은 사유(백틱 경로 누락)의 두 번째 발생이다.'}
---

# 없는 능력을 있는 것처럼 쓰는 것을 막는다 — 능력 프로브·부재 카드·시나리오 8

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260901-scenario-8-capability-probe-s7ny --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 없는 능력을 요구하는 요청에서 하네스가 필요 능력·프로브 결과·대안을 카드에 인쇄하고,
  「능력 확인」 절에 사실과 다른 결과를 적으면 승인을 막는다. 시나리오 8 런북과 재현 테스트로 고정한다.
- **왜 지금:** M3 종료 조건(계획 §10 #13)은 시나리오 3·8·9 런북 PASS 이고 3 은 섰다. 지금 라우터는
  `browser-automation` 요청에 「능력 확인」 절을 걸지만 **그 절을 채울 프로브가 없고**(`capabilities.yaml` 에
  `discovery.bmad` 뿐) **카드는 프로브 결과를 인쇄하지 않는다**. 절의 충족은 미완료 토큰 검사뿐이라
  그럴듯한 거짓 값이 통과한다 — 요구하는 자리와 보는 자리가 어긋난 §11 의 재발이다.
- **기대 결과:** 없는 능력은 카드에 「없음」으로 인쇄되고 대안이 함께 나온다. 있다고 적은 거짓은
  승인 자리에서 막힌다. **없다는 사실 자체는 막지 않는다** — 막으면 「되는지 조사해 보자」 가 불가능해진다(Q-28).
- **수용 기준:**
  - [x] AC-1 `core/policy/capabilities.yaml` 에 브라우저·데스크톱 자동화 능력과 외부 도구 서버 능력이
        정의되고 각각 `why`·`alternatives`·`honesty` 를 갖는다. 코어에 도구명·모델명은 없다(C-C6).
  - [x] AC-2 그 능력의 흔적 경로는 어댑터가 소유한다(`adapters/*/adapter.yaml`). 어댑터가 경로를 주지
        않으면 그 런타임에서 `absent` 다 — 코어가 경로를 알지 않는다.
  - [x] AC-3 라우터가 `browser-automation` facet 요청에 필요 능력 목록을 계산해 출력한다.
  - [x] AC-4 카드가 그 능력의 프로브 결과와 대안을 인쇄한다 — 부품에 붙지 않은 능력도 인쇄한다.
        (지금은 한 줄도 인쇄하지 않는다.)
  - [x] AC-5 새 차단 `capability-probed` 가 카탈로그와 `BLOCK_CHECKS` 양쪽에 있고 `enforced_at` 은
        `approve` 하나다. 「능력 확인」 절의 `enforcement` 가 그 차단을 가리킨다.
  - [x] AC-6 그럴듯한 거짓 값 넷이 **전부 승인에서 막힌다**: ① `absent` 를 `present` 로 적음
        ② 카탈로그에 없는 프로브 id ③ `absent` 인데 대안 칸이 빔 ④ 라우터가 요구한 능력이 표에 없음.
  - [x] AC-7 `absent` 를 사실대로 적고 대안을 쓰면 **승인된다**. 능력 부재는 승인을 막지 않는다.
  - [x] AC-8 프로브는 파일을 읽기만 한다 — 실행 뒤에도 흔적 파일이 생기지 않는다(자동 설치 금지).
  - [x] AC-9 런북 `scenarios/8-capability-absent.md` 가 `scenarios/README.md` 목록에 등재되고,
        구현자가 `BLOCKED_CAPABILITY` 로 끝내야 하는 자리를 명시한다. 통과만 보이지 않는다 — 반례를 담는다.
  - [x] AC-10 `tests/test_scenario_8.py` 가 런북의 단계를 그대로 실행하고, **고치기 전 상태에서 실패하는
        것**을 증거로 남긴다 — base 리비전 트리에 이 테스트만 얹어 재현한다. 고친 뒤 성공은 check-1 이
        보인다. 두 기록이 §11 의 양쪽이다 — 통과만 보인 검사는 빈 검사이고, 실패만 보인 검사는 통과
        불가능한 검사다. **이 단위의 산출물인 검사를 승인 전에 실행할 수는 없다**(D-27).
- **위험과 되돌리기:** 저장소 안의 문서·정책표·코드만 바뀐다. 외부 상태를 바꾸지 않는다.
  되돌리기: 통합 커밋을 `git revert` 한다. 정책표 로드가 깨지면 `bin/romeo route` 가 즉시 실패하므로
  같은 커밋 안에서 드러난다(`catalog_defects`·`section_defects` 가 로드 시점에 대조한다).
- **결정 필요:** 없음 — 차단 경계(거짓만 막고 부재는 막지 않는다)는 2026-09-01 사용자 확정.


## 변경 범위

- 바뀌는 파일·모듈: `core/policy/capabilities.yaml` · `core/policy/packages.yaml`(절 enforcement ·
  overlay · 차단 카탈로그) · `core/templates/sections/capability-check.md` · `adapters/*/adapter.yaml` ·
  `romeo/doctor.py`(프로브) · `romeo/policy.py`(능력 계산) · `romeo/card.py`(인쇄) ·
  `romeo/blocks.py`(집행) · `romeo/docs.py`(차단에 라우터 컨텍스트를 넘기는 배선) ·
  `romeo/close.py`(같은 배선의 종료 검사 쪽 호출부) · `romeo/cli.py`(카드 렌더러에 `--root` 를
  넘기는 호출부 — `cmd_card` 와 `cmd_route --card` 두 자리) · `scenarios/8-capability-absent.md` ·
  `scenarios/README.md` · `tests/test_scenario_8.py` · 새 차단이 추가되면 따라와야 하는 기존 검사와 fixture:
  `tests/test_scenario_3.py` · `tests/test_enforce_points.py` · `tests/test_blocks_enforcement.py` ·
  `fixtures/requests/fx-discord-computer-use-automation.yaml` ·
  `fixtures/requests/fx-s07-coupang-migration-initiative.yaml` ·
  `fixtures/requests/fx-account-migration-continue.yaml`.
- 영향을 받는 부분: `browser-automation` facet 이 붙는 요청의 카드·spec·승인 판정. 다른 facet 은
  능력 목록이 비므로 차단이 걸리지 않는다.
- 바꾸지 않는 것(비범위): 구현자·검토자 결과 봉투의 스키마(`BLOCKED_CAPABILITY` 는 이미 있다) ·
  `romeo close` 의 검토 판정 처리 · 시나리오 9(gate 집행) · 능력의 자동 설치 · `discovery.bmad` 프로브.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 능력을 코어에 정의하고 흔적 경로는 어댑터가 갖는다 | `capabilities.yaml` 에 능력 2종(+`why`·`alternatives`·`honesty`) · `adapters/*/adapter.yaml` 에 `capability_markers` | 소비: 없음 → 생산: 능력 id `automation.*` · 어댑터 키 `capability_markers` | `bin/romeo doctor --strict --scope repository` 가 그 능력을 인쇄하고 exit 0 · 코어에 도구명 없음 | `git revert` |
| 2 | 프로브가 어댑터 marker 를 읽는다 | `romeo/doctor.py` 의 `probe_capabilities` 가 어댑터별 marker 를 본다. 라벨은 `present`·`absent` 뿐 | 소비: 1 의 어댑터 키 → 생산: 프로브 결과 dict(`id`·`label`·`detail`·`alternatives`) | 임시 저장소에서 marker 를 만들었다 지웠을 때 라벨이 뒤바뀐다 · 프로브 실행 뒤 marker 가 생기지 않는다 | `git revert` |
| 3 | 라우터가 요구 능력을 계산한다 | `packages.yaml` overlay `facet.browser-automation` 에 능력 목록 추가 · `romeo/policy.py` 가 출력에 싣는다 | 소비: 2 의 능력 id → 생산: 라우팅 출력 키 | `fx-discord-computer-use-automation` 라우팅이 그 능력을 낸다 · 다른 fixture 는 비어 있다 | `git revert` |
| 4 | 카드가 프로브 결과·대안을 인쇄한다 | `romeo/card.py` — 부품에 붙지 않은 능력도 인쇄 | 소비: 3 의 라우팅 출력 → 생산: 카드의 「능력」 줄 | `bin/romeo card` 출력에 그 능력과 결과·대안이 나온다(지금은 없다) | `git revert` |
| 5 | 거짓 기재를 승인에서 막는다 | 차단 `capability-probed` 를 카탈로그·`BLOCK_CHECKS` 양쪽에 · 「능력 확인」 절 `enforcement` 를 그 차단으로 · 템플릿 표 열 정비 | 소비: 3·4 → 생산: 차단 id `capability-probed` | 거짓 값 넷이 전부 승인 거부 · 사실대로 적으면 승인 통과 | `git revert` |
| 6 | 런북과 재현 테스트 | `scenarios/8-capability-absent.md` · `scenarios/README.md` 목록 · `tests/test_scenario_8.py` | 소비: 1~5 → 생산: 없음 | `python3 -m unittest tests.test_scenario_8` exit 0 · 5 이전 리비전에서는 실패한다 | `git revert` |

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

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_scenario_8 -v"
  - id: check-2
    command: "python3 -m unittest discover -s tests"
  - id: check-3
    command: "! bin/romeo route --fixtures fixtures/requests --report | grep -q '✗'"
  - id: check-4
    command: "bin/romeo fixtures check"
  - id: check-5
    command: "bin/romeo validate"
  - id: check-6
    command: "bin/romeo compile --check"
  - id: check-7
    command: "bin/romeo doctor --strict --scope repository"
  - id: check-8
    command: "grep -q capability_markers adapters/claude/adapter.yaml && grep -q capability_markers adapters/codex/adapter.yaml"
  - id: check-9
    command: "bin/romeo card --proposal fixtures/proposals/fx-discord-computer-use-automation.yaml | grep -q '능력:'"
  - id: check-10
    command: "grep -q '8-capability-absent.md' scenarios/README.md"
```


## 증거

close PASS · 2026-09-02T00:45:28+09:00 · HEAD 01ec50d1f27d · 검사 기록 run_d7092f3d25c5

- [evidence/run_7c32a145569d.yaml](evidence/run_7c32a145569d.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_de465802c277.yaml](evidence/run_de465802c277.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_d7092f3d25c5.yaml](evidence/run_d7092f3d25c5.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
