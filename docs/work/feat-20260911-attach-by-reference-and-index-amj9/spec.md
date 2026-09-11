---
id: feat-20260911-attach-by-reference-and-index-amj9
type: spec
title: 부착을 참조로 바꾸고, 투영되는 인덱스를 대상에 실재하는 것으로 좁힌다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: active
approved_at: '2026-09-11T11:29:03+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: init-20260911-m5-attach-update-rollback-sauc
inputs: [inputs/ac-rebuttal-20260911.md, inputs/ac-rebuttal-20260911-round2.md]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-11'
updated: '2026-09-11'
approval_history:
- {approved_at: '2026-09-11T11:16:35+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-11T11:25:42+09:00',
  reason: '구현이 AC 결함 3건을 드러냈다 — AC-6·AC-7 은 달성 불가능한 낱말이었고(표 구분선과 행동 규범의 코어 경로 인용이 항상 투영된다), AC-8 이 고른
    c4-dangerous-instruction 은 override 로 덮이는 종류라 대상에 심어도 통과한다. 세 문장을 달성 가능하고 판별력 있는 형태로 고쳤다. 검증 계획(required_checks
    6건)은 바꾸지 않았다'}
- {approved_at: '2026-09-11T11:25:42+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-11T11:29:03+09:00',
  reason: 'AC-6·AC-7·AC-8 을 실제로 교체한다. 앞선 재승인 두 건(5ea8c87·244c530)은 치환이 조용히 실패해 spec 본문이 바뀌지 않은 채 approved_at
    만 갱신됐다 — 그 두 커밋 메시지가 주장한 수정은 이 커밋에서 이루어진다. AC-6 은 서식 줄을 비교 대상에서 빼는 규칙(실측 38/38), AC-7 은 Q-60 이 실측한
    5종, AC-8 은 대상 산출물만으로 판정하는 c2-no-auto-trigger 로 바꿨다'}
---

# 부착을 참조로 바꾸고, 투영되는 인덱스를 대상에 실재하는 것으로 좁힌다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260911-attach-by-reference-and-index-amj9 --by <승인자>` 로 기록한다.
> Charter M2 의 첫 단위다 — 부모는 `init-20260911-m5-attach-update-rollback-sauc`.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 하네스 명령이 **읽는 곳**(하네스 저장소)과 **쓰는 곳**(부착 대상)을 분리한다. 그러면 대상에 소스 트리 여섯을 복제하지 않는다. 그리고 대상에 투영되는 지침에서 **그 저장소에 없는 것을 가리키는 절**을 뺀다.
- **왜 지금:** 지금은 `compile --root <대상>` 이 대상 **안에서** `core/`·`adapters/`·`vendor/`·`provenance/`·`skills/`·`.harness/bindings.yaml` 을 읽으므로, 그 여섯을 손으로 복사해야만 부착이 성립한다. 사본은 하네스가 갱신되면 낡고, 계획이 경고한 드리프트가 그것이다. 같은 모양이 `doctor` 의 충돌 fixture 에도 있다 — 대상의 `fixtures/` 를 읽으므로 **부착 대상에서는 0종 실행으로 통과한다**(Q-53 과 같은 「부재가 일치로 읽히는」 자리). 그리고 대상 `CLAUDE.md` 는 그 저장소에 **없는 파일 5종**을 세션 시작에 읽으라고 지시한다(Q-60 · 2026-09-04 실측).
- **기대 결과:** 부착 대상에 놓이는 것이 14개에서 **8개**(컴파일·고지 산출물)로 줄고, 소스 트리 사본이 사라진다. 대상 지침은 그 저장소에 실재하는 것만 가리킨다. 충돌 fixture 는 하네스의 것을 읽어 **대상을 검사한다** — 0종으로 통과하지 않는다.
- **수용 기준:** 아래 낱말은 이 뜻이다. 「**사본**」 = 빈 디렉터리에 `bin/romeo compile --root` 와 `bin/romeo notices --root` 만 걸어 만든 부착본(소스 트리를 손으로 복사하지 않는다). 「**판정 명령**」 = `bin/romeo doctor --strict --scope repository --root <사본>`. 「**절**」 = `PROJECT.core.md` 본문에서 `## ` 로 시작하는 줄부터 다음 `## ` 줄 앞까지, 그리고 첫 `## ` 앞의 앞머리. 모든 명령은 하네스 저장소 안에서 실행한다.
  - [ ] AC-1 빈 디렉터리에 `bin/romeo compile --root <그 디렉터리>` 와 `bin/romeo notices --root <그 디렉터리>` 를 걸면 각 종료 코드가 0 이고, **실행이 끝난 뒤 그 루트의 파일 집합**이 `.harness/compiled.yaml` 의 `outputs` + `.harness/compiled.yaml` + `THIRD_PARTY_NOTICES.md` 와 정확히 같다 — 그 밖의 파일이 하나도 남지 않으므로 소스 사본도 남지 않는다.
  - [ ] AC-2 사본에서 판정 명령의 종료 코드가 0 이고, 같은 사본에서 `outputs` 가 담은 파일 하나를 지우면 종료 코드가 0 이 아니며 출력이 그 경로를 담는다 — 하네스 저장소는 그대로이므로 그 실패는 `--root` 가 사본을 본 결과다.
  - [ ] AC-3 `romeo.attach.required_paths()` 의 항목 집합이 AC-1 의 파일 집합을 **디렉터리 단위로 덮는 것과 정확히 같다** — 한쪽에만 있는 항목이 없다. 그러므로 소스 트리 여섯도, 산출물이 아닌 항목도, 빠진 산출물도 없다.
  - [ ] AC-4 하네스 저장소 자신을 대상으로 한 `bin/romeo compile --check` 와 `bin/romeo doctor --strict --scope repository`(`--root` 없이)의 종료 코드가 각각 0 이고, `python3 -m unittest discover -s tests` 의 종료 코드가 0 이다.
  - [ ] AC-5 `PROJECT.core.md` 의 절에서 ① 표식을 지우거나 ② `all`·`harness-only` 가 아닌 값을 넣거나 ③ 한 절에 표식을 두 줄 넣으면, 세 경우 각각 `bin/romeo compile` 의 종료 코드가 0 이 아니고 출력이 그 절의 제목(앞머리면 `앞머리`)을 담는다.
  - [ ] AC-6 `romeo:scope harness-only` 절들의 **고유 내용 줄**이 사본의 `CLAUDE.md`·`AGENTS.md` managed block 에 한 줄도 없고, 하네스 저장소 자신의 두 지침 파일에는 빠짐없이 있다. 「고유 내용 줄」은 그 절들의 줄에서 빈 줄·수평선(`---`)·표 구분선(`|` 와 `-`·`:`·공백만으로 된 줄)을 빼고, `romeo:scope all` 절과 `AGENTS.core.md` 에 같은 줄이 있는 것도 뺀 나머지다 — 서식 줄은 어느 소스에도 없으면서 렌더러가 만드는 표에 늘 나타나므로 판별에 쓸 수 없다(2026-09-11 실측: 그렇게 남는 줄 38개가 하네스 자신 블록에 38/38 있다).
  - [ ] AC-7 Q-60 이 실측한 5종(`docs/planning/progress.md`·`docs/decisions/decision-register.md`·`docs/planning/open-questions.md`·`docs/requirements/`·`docs/reviews/`)이 사본의 `CLAUDE.md`·`AGENTS.md` managed block 에 하나도 나타나지 않고, 하네스 저장소 자신의 두 지침 파일에는 다섯이 다 나타난다.
  - [ ] AC-8 사본에 `fixtures/` 가 없어도 `doctor` 의 충돌 검사 실행 수가 하네스의 `fixtures/conflicts/*.yaml` 개수와 같고, 사본에 `.claude/hooks.json` 을 놓으면(`c2-no-auto-trigger` 가 대상의 산출물만으로 판정하는 종류다) 판정 명령의 종료 코드가 0 이 아니며 출력이 **`c2-no-auto-trigger`** 를 담는다.
- **위험과 되돌리기:** 실제 프로젝트 저장소에는 쓰지 않는다 — 검증이 쓰는 것은 임시 디렉터리 사본뿐이다. 이미 소스 트리를 복제해 둔 저장소가 있으면 그 사본은 **남는다**(지우는 것은 Charter M3 의 `rollback` 이다). 되돌리려면 통합 커밋 하나를 `git revert` 하고 `bin/romeo compile` 로 산출물을 재생성한다.
- **결정 필요:** 없음. 계획 §3.1 은 이 전환을 금지하지 않는다 — 전문에 「코어 규칙을 복제하지 않는다」는 문장이 없고, 금지 대상은 「override 가 코어를 복제하는 것」이다(`implementation-plan.md:174·198`). 개정도 D-xx 도 필요하지 않다.

## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/compile.py` (읽는 곳을 하네스 저장소로 분리 · 절 표식을 읽어 투영 범위를 가른다) · `romeo/doctor.py` (충돌 fixture 를 하네스에서 읽어 대상을 검사) · `core/principles/PROJECT.core.md` (절마다 투영 범위 표식) · `scenarios/10-attach-payload.md` (「놓는 것」에서 소스 트리 여섯을 빼고 부착 순서를 고친다) · `tests/test_attach_runbook.py` (`SOURCE_TREE`·`attach()` 가 더 이상 복사하지 않는다) · `tests/test_attach_manifest.py` (기대 목록이 8개로 바뀐다) · `tests/test_attach_reference.py` (새 파일) · `.harness/compiled.yaml` (재생성 산출물) · `docs/work/feat-20260911-attach-by-reference-and-index-amj9/`
- 영향을 받는 부분: 이미 소스 트리를 복제한 부착 저장소 (그 사본은 남고 더 이상 요구되지 않는다) · `bin/romeo doctor --root <대상>` 의 충돌 검사 실행 수 · CI 의 compile·doctor 단계
- 바꾸지 않는 것(비범위): `romeo attach` 하위 명령과 preflight·파일별 승인·원자적 적용 (M2 의 다음 단위) · 대상의 실행 권한(Q-58)과 환경 등록(Q-59) · `update --dry-run`·`rollback` (Charter M3) · `AGENTS.core.md` 의 행동 규범 (전부 모든 저장소에 간다 — 가르지 않는다) · 이미 복제된 사본을 지우는 일

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 읽는 곳과 쓰는 곳을 분리한다 | `romeo/compile.py` 의 `plan_outputs(root, harness_root=None)` — 소스(`core/`·`adapters/`·`vendor/`·`provenance/`·`skills/`·`.harness/bindings.yaml`)는 `harness_root` 에서 읽고 산출물 경로만 `root` 아래로 만든다. `harness_root` 를 생략하면 `HARNESS_ROOT` 다. `check_compiled`·`compile_all` 도 같은 인자를 넘긴다 | 소비: 없음 → 생산: `plan_outputs(root, harness_root)` · 같은 서명의 `check_compiled`·`compile_all` | 소스 트리를 하나도 복사하지 않은 tmpdir 에 `compile --root` 를 걸어 산출물이 놓이는 것과, 하네스 자신의 `compile --check` 가 그대로 통과하는 것을 확인 (AC-1·AC-4) | 인자를 지우고 `root` 로 되돌린다 |
| 2 | 인덱스를 저장소별로 가른다 | `core/principles/PROJECT.core.md` 의 각 절(앞머리 포함) 앞에 `<!-- romeo:scope all -->` 또는 `<!-- romeo:scope harness-only -->` 를 적는다. `## 충돌 해소 순서` 만 `all` 이고 나머지는 `harness-only` 다 — 나머지 세 절은 전부 하네스 저장소의 경로를 가리킨다 | 소비: 없음 → 생산: `PROJECT.core.md` 의 절별 `romeo:scope` 표식 | `grep -c 'romeo:scope'` 가 절 개수와 같은 것을 확인 | 표식 줄을 지운다 |
| 3 | 표식을 **읽어** 투영 범위를 정한다 | `romeo/compile.py` 의 `_render_instructions` 가 그 표식을 읽어, `root` 가 `harness_root` 와 **다를 때**(= 부착) `all` 인 절만 넣는다. 표식이 없는 절을 만나면 `CompileError` 로 그 절의 제목을 말하며 멈춘다 — 표식을 잊은 절이 조용히 새지 않는다 | 소비: 2의 `romeo:scope` 표식 (**코드에 절 이름을 복사하지 않고 매번 읽는다**) → 생산: 부착 대상용 managed block | 표식 하나를 지우면 `compile` 이 그 제목을 말하며 실패하고, 사본 블록에 `harness-only` 절 제목이 없는 것을 확인 (AC-5·AC-6) | 조건을 지워 전부 투영한다 |
| 4 | Q-60 이 실측한 5종이 대상에 가지 않게 한다 | `tests/test_attach_reference.py` 가 사본의 managed block 에서 그 다섯 경로를 찾는다. 하나라도 있으면 인쇄하며 실패하고, 하네스 자신의 블록에는 다섯이 다 있어야 한다 | 소비: 3의 부착 대상용 블록 → 생산: Q-60 5종 부재 검사 | 사본과 하네스 자신 양쪽에 걸어 결과가 갈리는 것을 확인 (AC-7) | 검사를 지운다 |
| 5 | 충돌 fixture 를 하네스에서 읽어 대상을 검사한다 | `romeo/doctor.py` 의 `check_conflicts(root, harness_root=None)` — fixture 파일은 `harness_root/fixtures/conflicts/` 에서 읽고 검사 대상은 `root` 로 넘긴다. 실행 수가 0 이면 그 사실을 finding 으로 낸다. finding 에는 그것을 낸 **fixture 의 id** 가 실린다(이미 그렇다 — 그 자리가 AC-8 의 연결을 만든다) | 소비: 1의 `harness_root` 개념 → 생산: `check_conflicts(root, harness_root)` · 실행 수 0 의 finding | fixture 가 없는 사본에서 실행 수가 1 이상인 것과, 사본에 충돌을 심으면 종료 코드가 0 이 아닌 것을 확인 (AC-8) | 인자를 되돌린다 |
| 6 | 부착 정본에서 소스 트리를 뺀다 | `scenarios/10-attach-payload.md` 의 「놓는 것」에서 소스 트리 여섯 줄을 빼고, 「앞의 여섯은 손으로 복사하는 하네스 소스 트리다」 문단과 부착 순서를 고친다. `tests/test_attach_runbook.py` 의 `SOURCE_TREE` 와 `attach()` 도 복사를 그만둔다 | 소비: 1의 `plan_outputs(root, harness_root)` → 생산: 8개로 줄어든 `required_paths()` 결과 | `required_paths()` 에 여섯 중 어느 것도 없는 것과, 기존 두 테스트가 그대로 통과하는 것을 확인 (AC-3 · 회귀) | 문서와 목록을 되돌린다 |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 이 단위는 하네스 저장소 **자신**을 대상으로 하므로
`python3 -m unittest` 와 `bin/romeo` 의 자기 검사가 정당하다 — 그때는 그것이 이 단위의 산출물이기 때문이다.
(페이로드 작업 단위라면 그 둘을 넣지 않는다. 하네스가 깨진 동안 멀쩡한 산출물이 닫히지 못하고,
두 판정을 한 검사에 묶으면 어느 쪽이 깨졌는지 구분되지 않는다 — `feat-20260829-license-field-46an` 의 check-5 가 그 형태였다.)

**종료 코드 자체가 조건이다.** 검사에 적는 것은 `id` 와 `command` 둘뿐이고, 그 명령의 종료 코드 0 이 통과다.
기대를 문장으로 따로 적는 자리는 두지 않는다 — 사람은 그것을 조건으로 쓰는데 기계는 판정에 쓰지 않으므로,
그 검사는 무엇을 확인하는지 적혀 있는 채로 아무것도 확인하지 않는 **빈 검사**가 된다(2026-08-31 실측으로 제거).
확인하고 싶은 조건이 있으면 그 조건을 **명령으로** 쓴다. 옵션이 판정을 만드는 명령은 그 옵션까지 적는다 —
`bin/romeo doctor` 는 옵션 없이 쓰면 항상 exit 0 이라 빈 검사이고, 부착 검증(K-68)을 실제로 판정하게 하려면
`--strict --scope repository` 로 쓴다(Q-21). 그래서 `|| true` 를 붙이지 않는다 — 종료 코드를 항상 0 으로 만들어
위반을 통과시킨다. 부정 조건은 `!` 로 쓴다: `! grep -q '<있으면 안 되는 것>' <파일>`.

**어느 검사가 판별 검사인가**(§11 — 판별 검사만 승인 전에 양쪽 상태에서 실측한다):
check-1 은 **판별 검사**다(이 단위가 없으면 실패해야 한다). check-2~check-6 은 **회귀 방지 검사**이므로 양쪽 실측의 대상이 아니다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_attach_reference -v"
  - id: check-2
    command: "bin/romeo doctor --strict --scope repository"
  - id: check-3
    command: "python3 -m unittest tests.test_attach_runbook tests.test_attach_manifest -v"
  - id: check-4
    command: "python3 -m unittest discover -s tests"
  - id: check-5
    command: "bin/romeo compile --check"
  - id: check-6
    command: "bin/romeo validate docs/work/feat-20260911-attach-by-reference-and-index-amj9"
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
