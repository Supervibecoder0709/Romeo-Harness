---
id: feat-20260902-scenario-9-guard-enforcement-95e6
type: spec
title: 승인 없이는 되돌리기 어려운 것을 실행하지 않는다 — 가드 설명 요구·거부 경로·시나리오 9
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: done
approved_at: '2026-09-02T18:26:52+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-09-03T09:08:28+09:00'
parent: null
inputs: []
evidence: [evidence/run_4f365ab79976.yaml, evidence/run_f22c7f8cae97.yaml, evidence/run_108f96346abc.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-02'
updated: '2026-09-03'
---

# 승인 없이는 되돌리기 어려운 것을 실행하지 않는다 — 가드 설명 요구·거부 경로·시나리오 9

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260902-scenario-9-guard-enforcement-95e6 --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 되돌리기 어려운 행동(삭제·배포·결제 등)의 승인이 **설명 없이는 성립하지 않게** 하고,
  사람이 **거부한 사실을 기록할 자리**를 만든다. 시나리오 9 런북과 재현 테스트로 고정한다.
- **왜 지금:** M3 종료 조건(계획 §10 #13)은 시나리오 3·8·9 런북 PASS 이고 9 만 남았다. 가드의
  **계산·인쇄·계약 전달·종료 집행은 이미 선다**(실측: 삭제 fixture 에서 `guards=[deletion]`,
  `close.py:352-368` 이 승인 없으면 FAIL, `371-374` 가 미승인 가드에서 재실행을 건너뛴다).
  비어 있는 것은 두 자리다. ① `execution-guards.yaml` 의 `required_explanation` 4항목은
  **저장소 전체 grep 1건 = 그 정의 자리뿐**이다 — 읽는 코드도 검사도 없고 `--note` 는 비어도 되므로
  **빈 승인이 지금 통과한다**(요구를 적고 집행을 잊은 §11 의 재발). ② 사람이 **거부한 것을 기록할
  자리가 없다** — 계획 §7 이 요구한 "거부 시 `BLOCKED_APPROVAL` evidence" 를 만들 수단이 없어,
  그 값은 스키마 enum 과 문서에만 존재한다.
- **기대 결과:** 가드가 걸린 실행은 **영향 범위·사전 백업·복구 방법·확인할 내용 네 가지를 적어야만**
  승인으로 센다. 사람이 거부하면 그 사실이 봉인된 기록으로 남고, 종료 검사는 "아직 안 물어봤다"와
  "물어봤고 사람이 아니라고 했다"를 **다른 판정으로** 말한다. 후자는 재시도가 답이 아니다.
- **수용 기준:**
  - [x] AC-1 `core/policy/execution-guards.yaml` 의 `required_explanation` 이 파싱 가능한 구조
        (`key`·`label`·`why`)가 되고, **그 목록이 설명 요구의 단일 출처다** — 라벨을 코드에 복사하지 않는다.
  - [x] AC-2 `bin/romeo evidence approve` 가 `--note` 를 그 라벨로 대조한다. 네 항목 중 하나라도
        없거나 값이 자리표시자(`TBD`·미완료 토큰·`해당 없음` 등 — 목록은 구현이 정한다)뿐이면 **승인 기록을 만들지 않고
        비0 으로 끝난다**. 승인이 기록되지 않았으므로 상태는 승인 전 그대로다.
  - [x] AC-3 `romeo close` 가 봉인된 승인 로그의 note 를 **다시** 대조한다 — 승인·종료 두 지점이다.
        봉인은 로그와 yaml 의 일치만 보므로 둘을 함께 손으로 만들면 지금은 통과한다.
  - [x] AC-4 `bin/romeo evidence reject --unit --guard --by --note` 가 거부 사건을 기록하고,
        승인과 **같은 방식으로 봉인한다**(원시 로그 + sha256 + head/tree). 설명 4항목은 거부에도 요구한다 —
        무엇을 왜 거부했는지가 남아야 재요청이 같은 것을 반복하지 않는다.
  - [x] AC-5 `romeo close` 는 한 가드의 **가장 최근 결정**을 따른다. 마지막이 거부면 `GUARD_APPROVED`
        FAIL 이되 이유가 "승인 기록 없음"과 다르다 — `BLOCKED_APPROVAL` 로 종결됐음을 인쇄한다.
        거부 뒤 사람이 다시 승인하면 승인이 이긴다(사람이 다시 판단한 것이다).
  - [x] AC-6 그럴듯한 거짓 값이 **전부 막힌다**: ① note 없이 승인 ② 4항목 중 3개만 ③ 라벨은 넷 다
        있는데 값이 자리표시자 ④ 승인 로그와 yaml 을 함께 손으로 만들어 봉인을 맞춤(AC-3 이 잡는다)
        ⑤ 거부된 가드를 그대로 두고 close.
  - [x] AC-7 **사실대로 넷을 적으면 승인된다.** 설명 요구가 가드를 통과 불가능하게 만들지 않는다 —
        "사전 백업: 없음" 도 이유가 붙으면 유효한 답이다. 막는 것은 빈 승인이지 정직한 답이 아니다.
  - [x] AC-8 `gate-create` 는 **코어에 나타나지 않는다**(C-C6). 코어는 결정 기록의 형식만 정의하고,
        실제 게이트 호출과 gate id·응답·시각을 기록하는 절차는 `adapters/orca/RUNBOOK.md` 가 소유한다.
  - [x] AC-9 런북 `scenarios/9-guard-approval.md` 가 `scenarios/README.md` 목록에 등재되고, 통과만
        보이지 않는다 — AC-6 의 반례를 단계로 담고 구현자가 `BLOCKED_APPROVAL` 로 끝내야 하는 자리를 명시한다.
  - [x] AC-10 `tests/test_scenario_9.py` 가 런북의 단계를 그대로 실행하고, **고치기 전 상태에서 실패하는
        것**을 증거로 남긴다 — base 리비전 트리에 이 테스트만 얹어 재현한다. 고친 뒤 성공은 check-1 이
        보인다. **이 단위의 산출물인 검사를 승인 전에 실행할 수는 없다**(D-27) — 그래서 승인 전에는
        판별 검사 후보 5개가 현재 트리에서 실패하는 것을 프로브로 확인했다(P1 `required_explanation`
        미사용 exit 1 · P2 `evidence reject` 부재 exit 2 · P3 README 미등재 exit 1 · P4 테스트 모듈 부재
        exit 1 · P5 close 미대조 exit 1). 회귀 검사(fixture 리포트)는 양쪽에서 통과가 예상되므로
        §11 의 양쪽 실측 대상이 아니다.
- **위험과 되돌리기:** 저장소 안의 정책표·코드·문서·테스트만 바뀐다. **실제 삭제나 외부 상태 변경은
  하지 않는다** — 이 시나리오는 gate 거부로 끝나는 것이 정의다. 판정이 엄격해지므로 **앞으로의**
  가드 승인은 설명 넷을 요구받는다. 이미 `done` 인 단위에는 소급하지 않는다(close 는 `status: done` 을
  건너뛴다). 되돌리기: 통합 커밋을 `git revert` 한다. 정책표 구조를 바꾸므로 잘못되면
  `bin/romeo route` 가 로드 시점에 즉시 실패해 같은 커밋 안에서 드러난다.
- **결정 필요:** 없음 — 2026-09-02 사용자 확정: ① 설명 4항목을 보는 자리는 **승인 기록의 note**
  ② `gate-create` 는 코어가 형식만, 어댑터가 흔적 경로.


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `core/policy/execution-guards.yaml` · `romeo/evidence.py` · `romeo/close.py` · `romeo/cli.py` · `adapters/orca/RUNBOOK.md` · `scenarios/9-guard-approval.md` · `scenarios/README.md` · `tests/test_scenario_9.py` · `tests/test_docs_evidence_close.py` · `docs/planning/open-questions.md` · `docs/work/feat-20260902-scenario-9-guard-enforcement-95e6/`
- 영향을 받는 부분: 앞으로 기록되는 모든 가드 승인(설명 넷을 요구받는다) · `romeo close` 의 `GUARD_APPROVED` 판정과 그 뒤의 재실행 건너뛰기 · 가드가 걸린 단위의 위임 절차(§8 승인 기록 자리) · evidence 레코드의 키 하나 추가(거부 기록). 이미 `status: done` 인 단위는 close 가 건너뛰므로 소급되지 않는다.
- 바꾸지 않는 것(비범위): 가드의 **발동 조건**(`triggers` — 어떤 요청에 어떤 가드가 붙는지는 그대로다) · `romeo/policy.py` 의 가드 계산 · `romeo/card.py` 의 가드 인쇄 · `romeo/envelope.py` 의 계약 `guards` 필드 · `core/policy/execution-guards.yaml` 의 `enforcement:` 블록 중 `claude`·`codex` 키(코어에 벤더명이 남아 있는 같은 모양의 문제지만 이 요청은 `gate-create` 만 겨눈다 — 발견으로 열어 둔다, §12) · `romeo approve`(문서 승인)의 확인란 검사 · 차단(`blocks`) 판정 · 실제 삭제·배포·외부 상태 변경 · 다른 park(Q-12·13·15·16·17·19·23·24·26·32·33·34·35·43) · 실제 T2 관통

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 설명 요구를 기계가 읽을 수 있게 한다 | `core/policy/execution-guards.yaml` 의 `required_explanation` 을 문장 4줄에서 `{key, label, why}` 4항목으로 바꾼다. 값은 지금 문장을 쪼갠 것이고 요구 자체는 바뀌지 않는다 | 소비: 없음 → 생산: `required_explanation[].key`·`.label` (2·3 이 쓴다) | `python3 -c "import yaml;d=yaml.safe_load(open('core/policy/execution-guards.yaml'));assert [x['key'] for x in d['required_explanation']]"` 가 exit 0 | `git revert` |
| 2 | 설명 없는 승인이 기록되지 않게 한다 | `romeo/evidence.py` 에 note 파서를 넣는다 — 정책표의 `label` 로 항목을 찾고, 없거나 값이 자리표시자뿐이면 `ValueError`. `add_approval` 이 기록 **전에** 부른다(반쪽 기록을 남기지 않는다). `romeo/cli.py` 는 그 오류를 비0 종료로 인쇄한다 | 소비: 1 의 `label` → 생산: `parse_guard_explanation(note)` · `EXPLANATION_PLACEHOLDERS` (3·4 가 쓴다) | check-8 이 `required_explanation` 이 `evidence.py` 에서 읽히는 것을 본다. 반례는 check-1 | `git revert` |
| 3 | 승인 자리에서 통과한 거짓을 종료 자리에서 다시 본다 | `romeo/close.py` 의 `GUARD_APPROVED` 가 봉인된 로그의 note 를 2 의 파서로 다시 대조한다. 승인·종료 두 지점이다 — 봉인은 로그와 yaml 의 일치만 보므로 둘을 함께 손으로 만들면 지금은 통과한다 | 소비: 2 의 파서 → 생산: 없음 | check-8 이 `close.py` 쪽도 본다. 반례는 check-1 | `git revert` |
| 4 | 거부를 기록할 자리를 만든다 | `romeo/evidence.py` 에 `add_rejection` — 승인과 같은 봉인(원시 로그·sha256·head/tree)에 `reject-NN-<guard>.log`, 레코드 키는 `rejections[]`. 승인 배열에 섞지 않는다(기존 close 가 `approvals` 의 **존재**를 승인으로 세므로 섞으면 거부가 승인으로 읽힌다). `romeo/cli.py` 에 `evidence reject` 서브커맨드 | 소비: 2 의 파서(거부에도 설명 넷을 요구) → 생산: `rejections[]` · `bin/romeo evidence reject` (5 가 쓴다) | check-9 가 서브커맨드 존재를 본다 | `git revert` |
| 5 | 종료 검사가 "안 물어봤다"와 "거부됐다"를 다르게 말한다 | `romeo/close.py` 가 한 가드의 `approvals`·`rejections` 를 시각순으로 병합해 **마지막 결정**을 따른다. 거부면 `GUARD_APPROVED` FAIL 의 이유에 `BLOCKED_APPROVAL` 과 거부자·시각·사유를 인쇄한다. 거부 뒤 승인이 오면 승인이 이긴다 | 소비: 4 의 `rejections[]` → 생산: 없음 | 반례는 check-1(AC-6 ⑤) | `git revert` |
| 6 | `gate-create` 를 코어에서 어댑터로 옮긴다 | `core/policy/execution-guards.yaml` 의 `approval.mechanism.M3` 과 `enforcement.orca` 에서 그 명령을 지우고, 코어에는 "가드 결정은 승인·거부 기록으로 남는다"는 형식만 남긴다. 실제 게이트 호출과 `bin/romeo evidence approve`/`reject` 로 잇는 절차는 `adapters/orca/RUNBOOK.md` §8 에 쓴다 — 그 파일은 이미 `gate-create` 를 안내한다(1381행) | 소비: 4 의 명령 → 생산: 없음 | check-11 이 코어에 없음을, check-12 가 런북이 거부 명령을 안내함을 본다 | `git revert` |
| 7 | 런북과 재현 테스트로 고정한다 | `scenarios/9-guard-approval.md` (전제·단계·기대 판단·산출물·증거 5절, 반례를 단계로 담는다) · `scenarios/README.md` 목록에 9 행 · `tests/test_scenario_9.py` 가 그 단계를 그대로 실행한다. `tests/test_docs_evidence_close.py` 의 승인 기록 테스트 4곳이 새 note 형식을 쓰도록 고친다 | 소비: 2~6 전부 → 생산: 없음 | check-1·check-2·check-10 | `git revert` |

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

**판별 검사와 회귀 검사를 구분해 적는다**(§11). 판별 검사는 이 단위가 없으면 실패해야 하는 검사이고,
승인 전에 **현재 트리에서 실패하는 것**을 프로브로 확인했다. 회귀 검사는 양쪽에서 통과가 예상되므로
양쪽 실측의 대상이 아니다 — 현재 트리에서 통과하는 것만 확인했다.

| id | 종류 | 승인 전 프로브 (현재 트리) |
| --- | --- | --- |
| check-1 | 판별 | 실행 불가 — 이 단위의 산출물이다(D-27). AC-10 이 base 트리 재현으로 대신한다 |
| check-8 | 판별 | exit 1 (`required_explanation` 이 `evidence.py` 에서 읽히지 않는다) |
| check-9 | 판별 | exit 2 (`evidence reject` 서브커맨드가 없다) |
| check-10 | 판별 | exit 1 (README 에 9 가 등재되지 않았다) |
| check-11 | 판별 | exit 1 (코어에 `gate-create` 가 있다 — `execution-guards.yaml` 18·81행) |
| check-12 | 판별 | exit 1 (런북이 거부 명령을 안내하지 않는다) |
| check-2~7 | 회귀 | 전부 exit 0 — `validate`·`compile --check`·`doctor --strict`·`fixtures check` 실측 |

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_scenario_9 -v"
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
    command: "grep -q required_explanation romeo/evidence.py && grep -q required_explanation romeo/close.py"
  - id: check-9
    command: "bin/romeo evidence reject --help > /dev/null"
  - id: check-10
    command: "grep -q '9-guard-approval.md' scenarios/README.md"
  - id: check-11
    command: "! grep -rq 'gate-create' core/"
  - id: check-12
    command: "grep -q 'romeo evidence reject' adapters/orca/RUNBOOK.md"
```


## 증거

close PASS · 2026-09-03T09:08:28+09:00 · HEAD 5d4e00db5e97 · 검사 기록 run_108f96346abc

- [evidence/run_4f365ab79976.yaml](evidence/run_4f365ab79976.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_f22c7f8cae97.yaml](evidence/run_f22c7f8cae97.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_108f96346abc.yaml](evidence/run_108f96346abc.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
