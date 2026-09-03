---
id: init-20260904-m4-doc-reuse-metrics-wr9m
type: spec
title: M4 — 문서 재사용·승격·지표
unit: T2
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: deep
blast_radius: medium
uncertainty: medium
status: active
approved_at: '2026-09-04T07:13:40+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T2=deep', 'profile:uncertainty.medium=kept', 'overlay:unit.t2.parts', 'overlay:profile.standard-or-deeper',
    'warn:PART_PENDING_GATE']
  history: []
created: '2026-09-04'
updated: '2026-09-04'
---

# M4 — 문서 재사용·승격·지표

> 깊이 **Deep** · 단위 T2 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve init-20260904-m4-doc-reuse-metrics-wr9m --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** M4 — 문서를 두 번 만들지 않고, 끝난 사실을 current 로 올리고, 하네스가 자기 지표를 집계한다
- **왜 지금:** `/plan` 절차 1단계가 「재사용 검색」을 요구하지만 그것을 수행하는 명령도, 수행했는지 보는 자리도 없다 — 요구만 있고 집행이 없는 §11 의 모양이다. 작업 단위가 23건까지 쌓여 사람이 눈으로 훑는 방식은 이미 한계다. 이 이니셔티브(M4)의 나머지 세 조각(`context`·`current/` 승격·`metrics`)은 모두 「무엇이 이미 있는가」를 아는 것에서 출발하므로 이것이 첫 마일스톤이다.
- **기대 결과:** 제안 카드가 사람이 적어 넣지 않아도 **스스로 찾은** 중복 후보 단위를 인쇄한다. 같은 일을 두 번 여는 것을 막는 것이 아니라 **보이게** 한다 — 재개할지, 재분류할지, 새로 열지는 사람이 정한다(K-61).
- **수용 기준:**
  - [ ] AC-1 `romeo find <핵심어…>` 가 `docs/work/` 의 기존 작업 단위 중 id·제목·slug 가 핵심어와 겹치는 것을 unit id 로 출력한다. 겹치는 것이 없으면 빈 결과와 종료 코드 0 이다(없음은 오류가 아니다).
  - [ ] AC-2 제안의 `reuse_hits` 가 **비어 있어도** 카드가 스스로 검색한 후보를 인쇄한다 — 기존 단위와 겹치는 제안이면 카드 본문에 그 단위의 id 가 글자 그대로 나타난다. (「재사용 후보 줄이 있다」가 아니라 「그 줄에 그 id 가 있다」가 충족 조건이다.)
  - [ ] AC-3 카드가 30줄 예산을 넘어 축소될 때에도 그 재사용 후보 줄은 남는다 — 축소로 사라지면 이 요구는 인쇄만 되고 아무것도 드러내지 못한다.
  - [ ] AC-4 겹치지 않는 제안에서는 그 줄에 어떤 unit id 도 나타나지 않는다 (거짓 양성 0). — **이 항목만 회귀 방지다**: 구현 전에도 참이므로(카드가 아무것도 인쇄하지 않으니) 판별력이 없다. 승인 전 프로브에서 실측했다.
  - [ ] AC-5 `core/workflows/plan/SKILL.md` 1단계가 이 명령을 절차로 지정하고, 검사가 **`## 절차` 아래 1단계 본문만** 읽어 거기 적힌 `romeo <하위명령>` 이름을 뽑은 뒤, **그 이름으로 실제 검색을 돌려 기존 단위가 나오는 것까지** 확인한다. 이름이 CLI 에 있는지만 보면 부족하다. — 승인 전 프로브 실측: 문서 앞부분을 함께 읽으면 역할 분담 표의 `romeo route` 가 잡혀 **이 단위 없이도 통과**했고, 이름만 대조하는 판정도 같은 이유로 통과했다.
- **위험과 되돌리기:** 카드 렌더링을 건드리므로 기존 카드 출력의 줄 구성이 바뀐다(내용 손실이 아니라 한 줄 추가·축소 규칙 1건 변경). 운영 상태·외부 상태를 건드리지 않는다. 되돌리기는 `git revert <구현 커밋>` — 신규 파일 2개가 사라지고 수정 파일 3개가 이전 내용으로 돌아간다.
- **결정 필요:** 없음


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/find.py`(신규) · `romeo/cli.py` · `romeo/card.py` · `tests/test_find_reuse.py`(신규) · `core/workflows/plan/SKILL.md` · `docs/work/init-20260904-m4-doc-reuse-metrics-wr9m/`
- 영향을 받는 부분: `/plan` 절차 1단계(재사용 검색)와 제안 카드의 30줄 예산 축소 규칙. 어댑터 산출물은 코어 SKILL 의 `description` 만 반영하므로 본문 변경으로는 바뀌지 않는다.
- 바꾸지 않는 것(비범위): 정책표 `core/policy/**` · 템플릿 `core/templates/**` · 다른 작업 단위 · 어댑터 산출물(`.claude/**`·`AGENTS.md`) · 이 이니셔티브의 나머지 마일스톤(`romeo context` · `docs/current/` 승격 · `romeo metrics`) · 카드의 사실·가정·미확인 목록이 예산 축소로 사라지는 것(별개 결함 — `open-questions.md` 에 연다)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | `romeo find` 가 기존 단위를 찾는다 | `romeo/find.py` 신규 · `romeo/cli.py` 에 하위 명령 등록 | 소비: 없음 → 생산: `romeo.find.search_units(project_root, terms) -> list[dict]`(키 `id`·`title`·`path`·`score`) · CLI `romeo find <핵심어…> [--json]` | `bin/romeo find gate-fixture-coverage --json` 출력에 `feat-20260904-gate-fixture-coverage-q3wy` 가 있다 | `romeo/find.py` 삭제 + `cli.py` 등록 되돌리기 |
| 2 | 카드가 제안과 무관하게 스스로 찾은 후보를 인쇄하고, 그 줄이 예산 축소에서 살아남는다 | `romeo/card.py` 의 `render_card` — 후보 조회와 축소 제외 | 소비: `romeo.find.search_units` → 생산: 카드의 「재사용 후보」 줄 | `python3 -m unittest tests.test_find_reuse -v` 의 겹침·비겹침·예산초과 세 경우 | `git revert` |
| 3 | 절차가 그 명령을 지정하고, 지정과 실제가 어긋나면 검사가 실패한다 | `core/workflows/plan/SKILL.md` 1단계 · `tests/test_find_reuse.py` 의 대조 검사 | 소비: `core/workflows/plan/SKILL.md` 본문 · CLI 하위 명령 목록 → 생산: 없음 | `python3 -m unittest tests.test_find_reuse -v` | `git revert` |

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

**판별 검사와 회귀 방지 검사를 구분해 적는다(§11).** 판별 검사는 이 단위가 없으면 실패해야 하는 것이고,
회귀 방지 검사는 양쪽 상태에서 통과하는 것이 정의이므로 양쪽 실측의 대상이 아니다.

- **판별:** check-1(단, 그중 AC-4 케이스는 회귀 방지다 — 아래) · check-2
- **회귀 방지:** check-3 · check-4 · check-5, 그리고 check-1 안의 AC-4 케이스

**승인 전 프로브 실측(2026-09-04, 워크트리 `probe-m4-find`, base `ee1d2ee`).**
기존 상태에서 판별 검사 5건 전부 실패했고, 최소 구현을 넣은 가상 완료 상태에서 6/6 통과했다.
check-2·check-4·check-5 는 가상 완료 상태에서 종료 코드 0, check-3 은 839건 통과에 249초
(재실행 상한 600초의 42% — 경고 임계 80% 아래)였다. 그 프로브가 AC-5 의 결함 하나를 잡아 위 문구를 고쳤다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_find_reuse -v"
  - id: check-2
    command: "bin/romeo find gate-fixture-coverage --json | grep -q 'feat-20260904-gate-fixture-coverage-q3wy'"
  - id: check-3
    command: "python3 -m unittest discover -s tests"
  - id: check-4
    command: "bin/romeo validate"
  - id: check-5
    command: "bin/romeo compile --check"
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
