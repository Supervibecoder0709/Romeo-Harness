---
id: feat-20260910-router-fewshot-conflict-guidance-k8dd
type: spec
title: 오분류 예시를 정책표에 두고 카드가 그것을 읽어 인쇄한다 — 충돌 우선순위는 안내에 적는다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
status: active
approved_at: '2026-09-10T23:01:23+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: [inputs/ac-rebuttal-20260910.md, inputs/ac-rebuttal-20260910-2.md, inputs/card-baseline.proposal.yaml,
  inputs/card-before-20260910.txt, inputs/probe-20260910.md]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-10'
updated: '2026-09-10'
---

# 오분류 예시를 정책표에 두고 카드가 그것을 읽어 인쇄한다 — 충돌 우선순위는 안내에 적는다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260910-router-fewshot-conflict-guidance-k8dd --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 분류를 틀리게 만드는 신호를 **정책표에 예시로 적고, 분류 카드가 그것을 읽어 확정 화면에 인쇄한다.** 지금 그 예시를 둘 자리가 어디에도 없다(Q-102 · V-1 부분 충족). 함께: 정책 충돌 우선순위가 정책표에는 있고 `/plan` 안내 본문에는 없어서 그 한 줄을 더한다.
- **왜 지금:** shadow 20건이 예시로 쓸 오분류를 이미 모았고 2건이 같은 유형이다 — 요청에 「계획 세워봐」·「알려줘」처럼 판단·조사 요구가 섞였는데 실행 단계만 보고 불확실성을 낮게 잡았다(fx-landing-copy-revision · fx-landing-mobile-optimization). M5 attach 로 들어가기 전 정비 1회이고, 범위가 작다.
- **기대 결과:** 제안이 불확실성을 예시와 다르게 잡으면 카드가 그 신호를 한 줄로 인쇄해 사람이 확정 전에 본다. 그 문구를 정책표에서 고치면 카드 출력이 따라 바뀐다 — 요구하는 자리와 보는 자리가 같아진다(§11). `/plan` 안내가 충돌 우선순위를 담는다.
- **수용 기준:**
  - [ ] AC-1 `core/policy/classification.yaml` 의 `two_questions.uncertainty.examples` 에 항목이 1건 이상 있고, 각 항목이 `level`·`cue`·`why`·`source` 넷을 빈 값이 아닌 채로 갖는다. `level` 은 `low`·`medium`·`high` 중 하나이고 `source` 는 fixture id 를 1건 이상 담은 목록이다. 지금 정책표에서 이 검사는 통과한다. `cue` 문구가 `source` fixture 의 교정 사유를 옳게 요약하는지는 이 검사가 판정하지 않는다 — 검토자가 그 둘을 나란히 읽는다
  - [ ] AC-2 각 예시의 `source` 항목마다 `fixtures/requests/<id>.yaml` 이 있고, 그 fixture 의 `human_correction.changes` 에 `field` 가 `classification.uncertainty` 이고 `to` 가 그 예시의 `level` 과 같은 항목이 있다 — 예시의 레벨이 그 fixture 가 기록한 교정 결과값과 같다는 뜻이다. 지금 정책표에서 이 검사는 통과한다. 어느 예시의 `level` 을 그 fixture 의 `to` 가 아닌 다른 허용값으로 바꾸면 실패한다
  - [ ] AC-3 카드는 예시의 `level` 과 `cue` 를 정책표에서 **읽어** 인쇄하고, 그 줄은 제안의 확정값이 아니라 참고 예시임이 드러나는 접두로 시작한다. 정책표 사본에서 `cue` 값만 바꾸면(`level` 은 그대로) 카드 출력의 그 줄이 바뀐 값을 담는다. 기대 문구는 그 사본에서만 오고, `tests/test_router_guidance_examples.py` 에도 그 파일이 가져오는 어떤 상수·데이터 파일에도 정책표의 실제 `cue` 문자열이 없다
  - [ ] AC-4 제안의 `candidate.uncertainty` 와 `level` 이 다른 예시는 **전부** 인쇄되고, `level` 이 같은 예시는 인쇄되지 않는다
  - [ ] AC-5 예시는 한 예시당 한 줄로 인쇄한다. 예시를 인쇄하는 카드의 개행 기준 줄 수가 `core/policy/packages.yaml` 의 `card_max_lines` 를 넘지 않고, 예시 줄 각각의 길이가 카드가 다른 줄에 이미 쓰는 접기 폭을 넘지 않는다
  - [ ] AC-6 `inputs/card-before-20260910.txt` 는 이 단위 착수 전 `inputs/card-baseline.proposal.yaml` 로 만든 카드 출력이다. 구현 뒤 같은 제안으로 만든 카드가 그 파일의 카드 줄을 **전부** 담는다 — 변경 전에 사람이 보던 줄이 지워지지 않는다. 저장소 상태·설치 상태에 따라 달라지는 줄(재사용 후보·능력 프로브·부품 설치)은 검사가 양쪽에서 같은 규칙으로 제외하고, 그 규칙을 실패 메시지에 인쇄한다
  - [ ] AC-7 `core/workflows/plan/SKILL.md` 는 **표식으로 특정한 한 줄**에 충돌 우선순위 항목을 적고, 그 줄의 항목 목록이 `classification.yaml` 의 `conflict_priority` 와 순서까지 정확히 같다. 검사는 그 줄만 읽는다 — 본문 아무 데나 나타나는 낱말을 세지 않는다. 구현 뒤 이 검사는 통과한다. 정책표를 그대로 둔 채 그 줄에서 어느 항목이든 하나를 빼면 실패한다. 정책표를 그대로 둔 채 그 줄의 서로 다른 두 항목의 순서를 바꾸어도 실패한다. `tests/test_router_guidance_examples.py` 에는 항목 이름이 인용부호나 백틱에 감싸인 채로 없다. 그 줄의 설명 문장이 우선순위 방향을 옳게 적었는지는 이 검사가 판정하지 않는다 — 검토자가 읽는다
- **위험과 되돌리기:** 위험은 카드 30줄 예산이다 — 새 줄이 다른 줄을 밀어내면 사람이 보던 것이 사라진다. AC-5(넘지 않는다)와 AC-6(밀어내지 않는다)이 그것을 판정한다. 외부 상태를 바꾸지 않고 되돌리기는 통합 커밋 `git revert` 한 번이다.
- **결정 필요:** 없음


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `core/policy/classification.yaml` · `romeo/card.py` · `core/workflows/plan/SKILL.md` · `tests/test_router_guidance_examples.py` · `docs/work/feat-20260910-router-fewshot-conflict-guidance-k8dd/`
- 영향을 받는 부분: `bin/romeo card` 와 `bin/romeo route --card` 의 출력 한 줄이 늘어난다. 분류값은 바뀌지 않는다
- 바꾸지 않는 것(비범위): 라우터의 unit·profile·게이트 계산(`romeo/policy.py`) · `fixtures/shadow/` 기록 · `docs/planning/open-questions.md` 의 Q-102 해소 표시(통합 뒤 별도 커밋) · `core/policy/packages.yaml` 의 주석에 있는 축약형 우선순위(안내 자리는 `/plan` SKILL 하나로 한정한다, §12)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 정책표에 예시 자리를 만든다 | `core/policy/classification.yaml` 의 `two_questions.uncertainty` 에 `examples` 목록과 항목 1건. `source` 는 그 판단의 근거가 된 fixture id 목록이다(shadow 2건이 같은 유형이므로 규칙 한 줄로 덮인다). 카드가 `level`·`cue` 만 인쇄하고 `why` 는 이 표를 여는 사람이 읽는 근거이며 `source` 는 검사가 대조하는 값이라는 것을 주석으로 적는다 — 아무도 읽지 않아도 되는 것은 읽지 않는다고 적는다(§11) | 소비: 없음 → 생산: `two_questions.uncertainty.examples[]` (`level`·`cue`·`why`·`source`) | `tests/test_router_guidance_examples.py` 의 스키마 검사 (AC-1) | `git revert` |
| 2 | 예시의 근거를 fixture 기록과 대조한다 | 같은 검사 파일에서 `source` 의 fixture 를 열어 `human_correction.changes` 에 `field: classification.uncertainty` 이고 `to` 가 예시 `level` 과 같은 항목이 있는지 본다. 형식만 맞고 내용이 거짓인 예시 — 고치려던 오분류를 정답으로 등록한 것 — 를 막는 자리다 | 소비: 1번의 `examples[].source`·`level` → 생산: 근거 대조 함수 | 같은 파일의 대조 검사 (AC-2) | `git revert` |
| 3 | 카드가 그 예시를 읽어 인쇄한다 | `romeo/card.py` 의 2질문 줄 **바로 아래**에 예시 줄을 더한다 — 제안 `uncertainty` 와 `level` 이 다른 예시만, 전부. 참고 예시임이 드러나는 접두를 붙이고 값은 정책표에서 읽어 문구를 코드에 적지 않는다. 자리를 앞쪽에 두는 이유는 예산 축소가 뒤에서부터 자르기 때문이다 | 소비: 1번의 `examples[]` → 생산: 카드 예시 줄 | 같은 파일의 파생·여집합·예산·보존 검사 (AC-3·4·5·6) | `git revert` |
| 4 | 충돌 우선순위를 안내에 적는다 | `core/workflows/plan/SKILL.md` 의 역할 분담 표 아래에 한 줄. 검사는 순서를 정책표에서 **읽어** 대조하고 항목 이름을 검사 파일에 적지 않는다 | 소비: `classification.yaml` 의 `conflict_priority` → 생산: SKILL 본문 한 줄 | 같은 파일의 순서 대조 검사 (AC-7) | `git revert` |

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

**어느 검사가 판별이고 어느 것이 회귀 방지인지 적는다.** 승인 전 양쪽 상태(현재·가상 완료) 실측의 대상은
**판별 검사**뿐이다 — 회귀 방지 검사는 양쪽에서 통과하는 것이 정의이므로 두 상태에서 돌려도 판별할 것이 없다(§11).

아래 구분은 승인 전 프로브의 **실측**이다 — `inputs/probe-20260910.md` 가 검사별 판정을 담는다.

- **판별** — 기존 상태에서 실패했다: `check-1` 의 AC-1·3·4·5·7 항목(13개 중 8개).
- **회귀 방지** — 양쪽에서 통과했다: `check-1` 의 AC-6(기존 줄 보존)·AC-7 의 자기 파생 검사와 `check-2`~`check-5`.
- **지금은 공전한다** — `check-1` 의 AC-2 두 항목과 AC-1 의 필드 검사는 예시가 0건이라 루프가 돌지 않아 통과했다.
  판별력은 `test_at_least_one_example` 이 만든다. 숨기지 않고 적는다 — 이 셋만 보면 검사가 무언가를
  확인한 것처럼 보이기 때문이다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_router_guidance_examples -v"
  - id: check-2
    command: "bin/romeo validate"
  - id: check-3
    command: "bin/romeo fixtures parity --report"
  - id: check-4
    command: "bin/romeo compile --check"
  - id: check-5
    command: "python3 -m unittest discover -s tests"
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
