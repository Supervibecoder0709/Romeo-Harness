# 1차 리뷰 findings (워크플로 wf_3bd93c90-559)

blocker 6 · important 15 · minor 10

## F01 [blocker] (요구대비-누락)
**대상:** `.harness/romeo.project.yaml`

**요약:** 이번 라운드에 만든 `.harness/romeo.project.yaml` 의 `modules.superpowers: active` 가 라우터에 도달하지 않는다. 그 결과 모든 T1/T2 라우팅이 여전히 `superpowers: pending_gate` + `PART_PENDING_GATE` 를 내고, `core/workflows/implement/SKILL.md` 3절이 "채택 게이트를 통과하지 않은 부품은 PART_PENDING_GATE 로 표시하고 쓰지 않는다" 고 지시하므로, 실제 구현 절차가 superpowers 규율 세트를 끄게 된다 — M2 다음 조건 "superpowers 규율 세트가 켜진 상태에서 parity PASS(D-58)" 와 정면으로 어긋난다.

**증거:**

`romeo/policy.py:121` `def route(classification, policy=None, project_state=None)` · `:238` `modules = (project_state or {}).get("modules") or {}` · `:242` `status = "active" if modules.get(pid) == "active" else meta.get("status", "pending_gate")`.
`grep -rn "project_state|romeo.project.yaml" romeo/ tests/ .github/` → 히트 2건, 둘 다 `romeo/policy.py` 안(정의와 사용). **호출자 0건** — `.harness/romeo.project.yaml` 을 읽는 코드가 저장소에 없다.
실측:
```
$ python3 -c "...route({'intent':'write','unit':'T1','mode':'delivery','facets':[],'gates':[],'uncertainty':'low','blast_radius':'small'}, pol)"
"parts": [{"id":"superpowers","gate":"G-M2","status":"pending_gate",...}]
"warnings": [{"id":"PART_PENDING_GATE",...,"detail":["superpowers"]}]
$ ...같은 호출에 project_state={'modules':{'superpowers':'active'}} 를 넘기면
with project_state: [{"id":"superpowers",...,"status":"active",...}]
```
`$ ./bin/romeo route --fixtures fixtures/requests --report` (exit 0) → `경고 빈도: PART_PENDING_GATE×20`.
`core/policy/packages.yaml:171` `status: pending_gate` (superpowers). G-M2 는 D-67 로 닫혔고 vendor 15파일 복사·양 런타임 discovery 관찰까지 끝났는데도 라우터는 여전히 미통과로 본다.
`.harness/romeo.project.yaml:20-21` 이 스스로 "값이 부품 레지스트리(core/policy/packages.yaml)의 status 를 덮는다" 고 선언하지만 그 동작이 구현돼 있지 않다.

**제안된 수정:** `romeo/util.py` 또는 `romeo/policy.py` 에 `load_project_state(root)` 를 추가해 `.harness/romeo.project.yaml` 을 읽고, `romeo/cli.py` 의 `cmd_route`·`cmd_card`·`cmd_new`(문서 생성 경로)와 `romeo/docs.py`·`romeo/close.py` 의 `route(...)` 호출에 `project_state=` 를 넘긴다. 파일이 없으면 지금과 같은 pending_gate 동작을 유지한다(정직한 기본값). 회귀 테스트 2건: (a) 파일이 있으면 T1 라우팅의 `parts[0].status == "active"` 이고 `PART_PENDING_GATE` 경고가 사라진다, (b) 파일이 없으면 pending_gate 로 되돌아간다. `fixtures/requests` 리포트의 기대값은 warnings 를 비교하지 않으므로 33/33 일치는 유지된다(실측 확인 필요).

## F02 [blocker] (실행가능성)
**대상:** `adapters/orca/RUNBOOK.md`

**요약:** 위임된 워커 안에서는 승인이 절대 보이지 않는다 — `romeo approve` 가 base_sha 를 '승인 직전 HEAD' 로 박고 승인 표시는 작업 트리에만 쓰기 때문에, RUNBOOK §3.3 이 지시한 `--base-branch <base_sha 의 ref>` 자식 워크트리에는 `status: draft` 만 존재한다. implement/SKILL.md 1번이 그 안에서 항상 BLOCKED_APPROVAL 로 끝난다.

**증거:**

romeo/docs.py:105-110 `approve_unit` 은 `fm["base_sha"] = head_sha(project_root)` 로 **승인 직전 HEAD** 를 기록한 뒤 `fm["status"]="active"`·`approved_at` 을 spec.md 파일에만 쓴다(커밋하지 않는다).

격리 재현(scratchpad 사본, 저장소 무변경):
```
$ BASE(HEAD) = b6995cf944181cfaca53b6de0dc8b642e80d7d49
$ base_sha 시점 spec status = status: draft
$ ./bin/romeo approve chg-20260827-rg-fallback-validate-245m --by julliette --root $S2
approved ... base_sha=b6995cf944181cfaca53b6de0dc8b642e80d7d49   (EXIT=0)
기록된 base_sha            = base_sha: b6995cf944181cfaca53b6de0dc8b642e80d7d49
작업 트리 spec status      = status: active
base_sha 체크아웃의 status  = status: draft
base_sha 체크아웃 approved_at = ''            ← 없음
git status --porcelain     =  M docs/work/chg-20260827-rg-fallback-validate-245m/spec.md
```
작업 단위가 아직 커밋조차 안 된 흔한 경우는 더 일찍 터진다:
```
$ ./bin/romeo evidence checks --unit chg-20260827-rg-fallback-validate-245m --root $S/emptyroot
ERROR 작업 단위 디렉터리가 없다: .../docs/work/chg-20260827-rg-fallback-validate-245m
EXIT=1
```
빠져나갈 길이 없다. 승인 커밋을 브랜치에 올린 뒤 워크트리를 만들면 `head != base_sha` 가 되어 RUNBOOK:23("`head` 값이 작업 계약의 `base_sha` 와 같아야 한다")과 §6("같은 `base_sha`")이 깨지고, base_sha 그대로 만들면 승인이 없다. RUNBOOK 어디에도 "승인된 spec 을 먼저 커밋한다"는 단계가 없다(grep 결과 §3.2 는 SKILL.md 의 미커밋 문제만 절대경로로 우회한다).

**제안된 수정:** 둘 중 하나를 정본으로 고른다. (a) `romeo approve` 가 base_sha 를 '승인 커밋 이후 HEAD' 로 기록하도록 바꾸고 RUNBOOK §3 앞에 "승인된 spec.md 를 커밋한 뒤 그 SHA 를 base_sha 로 쓴다"를 명시 — 이 경우 romeo/docs.py:107 이 approve 뒤 커밋을 요구하는 2단계가 된다. (b) 워커에 넘기는 것을 작업 계약(TaskEnvelope)으로 한정하고 워커가 spec.md 를 다시 읽지 않게 한다 — implement/SKILL.md 1번의 '승인 확인'을 위임 계층(§3.2 이전)으로 옮기고, 워커 안에서는 계약의 `spec_ref.sha256` 대조만 시킨다. 어느 쪽이든 RUNBOOK §1·§3.3·§6 의 base_sha 문장을 함께 고쳐야 한다.

## F03 [blocker] (실행가능성)
**대상:** `core/workflows/implement/SKILL.md`

**요약:** 3번 '규율 부품' 절 전체가 실행 불가다. 라우터가 `superpowers` 를 항상 `pending_gate` 로 돌려주므로(CLI 가 `.harness/romeo.project.yaml` 을 읽지 않는다) 같은 절 마지막 줄의 금지 규칙에 걸려 sp-* 5종이 100% 켜지지 않는다.

**증거:**

`romeo/cli.py` 의 route 호출 3곳(25·44·63·75행)이 전부 `route(cls)` — `project_state` 를 넘기지 않는다:
```
$ grep -n "route(" romeo/cli.py
44:        out = route(cls)
63:    out = route(prop["candidate"])
75:    out = route(cls)
```
`romeo/policy.py:121` 은 `def route(classification, policy=None, project_state=None)`, `:238` 은 `modules = (project_state or {}).get("modules") or {}`. 따라서 항상 `core/policy/packages.yaml:171` 의 `status: pending_gate` 가 남는다:
```
CLI 경로            parts = [... {'id':'superpowers','gate':'G-M2','status':'pending_gate', ...}]  warnings = ['PART_PENDING_GATE']
project_state 전달   parts = [... {'id':'superpowers','gate':'G-M2','status':'active', ...}]      warnings = ['PART_PENDING_GATE']
```
(fixtures/requests/fx-ab-tracking-plan-dashboard.yaml 로 실행)
전체 라우팅에서도 같다 — `./bin/romeo route --fixtures fixtures/requests --report` 의 경고 빈도에 `PART_PENDING_GATE×20`(write intent 20건 전부).
implement/SKILL.md:27 은 "라우터 출력 `parts` 에 실린 것만 켠다", :35 는 "채택 게이트를 통과하지 않은 부품은 `PART_PENDING_GATE` 로 표시하고 쓰지 않는다" 다. 두 문장을 함께 적용하면 :29-34 의 `sp-test-driven-development`·`sp-systematic-debugging`·`sp-verification-before-completion`·`sp-using-git-worktrees`·`sp-finishing-a-development-branch` 는 어떤 작업 단위에서도 켜지지 않는다. provenance/imports.yaml 은 이 5종을 `status: accepted` · `gate: G-M2` · `decided_at: 2026-08-27` 로, `.harness/romeo.project.yaml:24` 는 `superpowers: active` 로 선언하고 있어 세 곳이 서로 모순된다. review/SKILL.md:18 의 `sp-requesting-code-review`·`sp-receiving-code-review` 도 같은 `superpowers` 부품이다.

**제안된 수정:** 부품 부착 상태의 주인을 하나로 정한다(K-63). 추천은 `romeo/cli.py` 의 route 호출 3곳이 `.harness/romeo.project.yaml` 을 읽어 `project_state=` 로 넘기게 하는 것이다 — `romeo/policy.py:238` 이 이미 그 값을 받도록 만들어져 있고 파일도 이미 존재하므로 배선만 없다. 그렇게 하면 `superpowers` 가 `active` 로 나와 PART_PENDING_GATE 경고에서도 빠진다. 배선을 M5 로 미룰 거라면 `core/policy/packages.yaml:171` 의 `status` 를 `active` 로 올려 G-M2 결정을 반영하고, 그 전까지는 implement/SKILL.md:35 가 어떤 결과를 낳는지(규율 부품 0종) 문서에 명시해야 한다.

## F04 [blocker] (실행가능성)
**대상:** `core/workflows/implement/SKILL.md`

**요약:** 6번의 `romeo evidence approve` 는 문서가 지시한 순서(6번 승인 → 7번 증거)로는 실행이 불가능하다. evidence run 이 먼저 있어야만 승인이 기록되는데, 같은 절이 '승인 전 상태 변경 0건' 을 요구한다.

**증거:**

romeo/evidence.py:122-128 `add_approval` 은 기존 evidence run 파일이 없으면 예외를 던진다.
격리 재현(scratchpad 사본):
```
$ ./bin/romeo evidence approve --unit chg-20260827-rg-fallback-validate-245m --guard deletion --by julliette --note "영향 범위/복구" --root $S
ERROR 승인을 기록할 evidence run 이 없다 — 먼저 romeo evidence run 을 실행한다
EXIT=1
```
순서를 뒤집으면 통과한다:
```
$ ./bin/romeo evidence run --unit chg-... --root $S -- true      → EXIT=0
$ ./bin/romeo evidence approve --unit chg-... --guard deletion --by julliette --root $S
approval recorded → .../evidence/run-20260828.yaml               → EXIT=0
```
implement/SKILL.md:40-42 는 가드 승인(6번)을 증거(7번)보다 앞에 두고 "승인 전 상태 변경 0건이다" 라고 못박는다. adapters/orca/RUNBOOK.md:219-224 §8 과 core/policy/execution-guards.yaml:19 도 같은 문장이다. 작업 단위의 첫 행동이 가드 대상이면(예: `deletion`·`workspace-deletion` 가드가 붙은 T1) 승인 기록 자체가 불가능하고, romeo/close.py:73-74 의 `GUARD_APPROVED` 는 그 승인이 없으면 FAIL 이므로 종료 검사까지 막힌다.

**제안된 수정:** `romeo/evidence.py` 의 `add_approval` 이 evidence run 이 없을 때 새 run 레코드를 만들도록 바꾸는 것을 권한다 — `run_command` 가 쓰는 초기 dict 를 별도 함수로 뽑아 `add_approval` 도 호출하면 되고, `commands: []` 인 승인 전용 레코드가 남아 '승인 시점에 명령 0건' 이 오히려 증거로 남는다. 코드를 못 고치면 implement/SKILL.md 6번과 RUNBOOK §8 에 "승인 기록 전에 `romeo evidence run --unit <id> --label approval-context -- <읽기 전용 확인 명령>` 을 먼저 돌린다" 를 명시해야 한다(지금은 어디에도 없다).

## F05 [blocker] (요구대비-누락)
**대상:** `romeo/parity.py`

**요약:** `bin/romeo fixtures parity --report` 가 손으로 쓴(`source.kind: authored`) 케이스 5건만으로 "핵심 동등성 게이트: PASS" 를 인쇄하고 exit 0 으로 끝난다. 관측(observed) 케이스를 요구하는 검사가 없어, 실제 교차 실행이 한 번도 없는 상태에서 계획 §10 #11 의 완료 확인 기준이 충족된 것처럼 보인다 — K-51(증거는 손으로 쓰지 않고 증거 기록 명령으로만 만든다)이 막으려는 바로 그 형태다.

**증거:**

```
$ ./bin/romeo fixtures parity --report
parity 리포트 · 6건(실행 5 · 미실행 1) · 판정 PASS · 동일 3 · 불일치 2(전부 기대함)
...
핵심 동등성 게이트: PASS
exit=0
```
실행으로 계상된 5건의 출처는 전부 사람이 쓴 것이다:
```
$ grep -n "kind:" fixtures/parity/*.yaml
pr-blocked-capability.yaml:44:  kind: authored
pr-checks-drift.yaml:48:  kind: authored
pr-license-field-t1.yaml:84:  kind: authored
pr-t0-implementer-only.yaml:46:  kind: authored
pr-verdict-drift.yaml:47:  kind: authored
pr-license-field-t1-observed.yaml:21:  kind: planned   ← 유일하게 status: pending
```
`romeo/parity.py:174` `"verdict": "PASS" if executed and matched == len(executed) else "FAIL"` — `source.kind` 를 보지 않는다. `romeo/parity.py:24` `REQUIRED_KEYS` 에 `source` 는 있으나 `check_parity_cases` 는 `kind` 값을 검증하지 않는다(`grep -n "kind" romeo/parity.py` → 히트 0건).
미실행을 통과로 세지 않는 장치(`status: pending`)는 잘 만들어져 있으나, "authored 만으로는 게이트를 통과할 수 없다" 는 장치는 없다.

**제안된 수정:** `check_parity_cases` 에 `source.kind ∈ {observed, authored, planned}` enum 검사를 넣고, `run_parity` 의 verdict 계산을 두 층으로 나눈다 — `checker_verdict`(지금 로직, 검사기 자기 검증)와 `gate_verdict`(= `PASS` 만 `observed` 케이스가 1건 이상 있고 그것들이 전부 일치할 때, 아니면 `미판정`). `format_parity` 의 마지막 줄을 `핵심 동등성 게이트: 미판정 — 관측 케이스 0건(authored 5건은 검사기 검증용)` 으로 바꾸고 CLI 종료 코드는 미판정일 때 1 로 둔다. 회귀 테스트: authored 만 있는 디렉터리는 게이트를 통과하지 못한다.

## F06 [blocker] (규율-위반)
**대상:** `core/schemas/result-envelope.json:78-126 · romeo/parity.py:139-155,174`

**요약:** 핵심 동등성 게이트가 '검사 0건 · 증거 0건'의 PASS 쌍을 통과시킨다 — 실행하지 않은 것을 완료로 인정한다(K-51 · AGENTS.core §4).

**증거:**

result-envelope.json 은 gate_verdict(:78-85), blocked_reason(:86-97), evidence_ref(:121-126)를 서로 무관하게 선언하고 조건 제약이 없다. 실제 검증:

$ python3 -c "...validate({'gate_verdict':'PASS','checks':[],'blocked_reason':None,'evidence_ref':None,...}, result-envelope)"
PASS+evidence_ref=null+checks=[] errors: []

이 상태의 봉투 2개를 케이스로 만들어 게이트를 돌리면:
$ ./bin/romeo fixtures parity /…/scratchpad/parityhole
parity 리포트 · 1건 · 판정 PASS · 동일 1 · 불일치 0
| pr-empty-pass | … | ✓ | 스키마 유효·required_checks 동일·gate 판정 동일 |
핵심 동등성 게이트: PASS
exit=0

compare_case 는 checks 리스트가 양쪽 다 빈 리스트면 '동일'로, gate_verdict 가 양쪽 PASS 면 '동일'로 판정하고(parity.py:141-148) evidence_ref 를 전혀 보지 않는다. core/workflows/implement/SKILL.md:46-47 이 '명령을 하나도 실행하기 전에 차단된 경우에만 evidence_ref 가 비어 있을 수 있고, 그때는 blocked_reason 이 반드시 채워져 있다'고 선언한 규칙을 스키마도 검사기도 강제하지 않는다.

**제안된 수정:** 두 겹으로 막는다. (1) result-envelope.json 에 gate_verdict=PASS 이면 evidence_ref 가 문자열이고 checks 가 minItems:1 이어야 한다는 제약을 넣는다 — romeo/schema.py 는 if/then 을 지원하지 않으므로(:1-2 docstring) anyOf 로 표현하고(anyOf 는 :68-73 에서 지원됨), 'PASS 이면 evidence_ref:{type:string,minLength:1}' / 'PASS 가 아니면 제약 없음' 두 분기를 쓴다. (2) parity.py 의 compare_case 에 SCHEMA_INVALID 와 같은 층위로 EVIDENCE_MISSING 판정 코드를 추가해, PASS 인데 evidence_ref 가 비었거나 checks 가 빈 봉투는 양면이 똑같아도 불일치가 아니라 '판정 불가'로 떨어뜨린다.

## F07 [important] (규율-위반)
**대상:** `.harness/romeo.project.yaml:19-26 · core/workflows/implement/SKILL.md:27,35`

**요약:** romeo.project.yaml 을 로드하는 코드가 없어 modules.superpowers: active 가 무효다. 라우터는 계속 PART_PENDING_GATE 를 내므로 새 implement 절차는 자기가 지목한 부품을 하나도 켤 수 없다.

**증거:**

$ grep -rn "romeo.project" romeo/ bin/ tests/ adapters/ .github/
(출력 없음 — 소비자 0)

romeo/policy.py:121 route(classification, policy=None, project_state=None) 와 :238 modules = (project_state or {}).get("modules") 로 덮어쓰기 경로 자체는 있으나 project_state 를 넘기는 호출자가 없다. 실측:

$ python3 -c "from romeo.policy import load_policy,route; out=route({...T1 delivery write...}, load_policy()); print(out['parts'], out['warnings'])"
parts= [{'id':'superpowers','gate':'G-M2','status':'pending_gate',...}]
warnings= [{'id':'PART_PENDING_GATE', 'detail':['superpowers']}]

core/policy/packages.yaml:166 은 '실제 부착 상태는 .harness/romeo.project.yaml이 덮어쓴다'고 단언하지만 :171 status 는 여전히 pending_gate 다. 그런데 core/workflows/implement/SKILL.md:35 는 '채택 게이트를 통과하지 않은 부품은 PART_PENDING_GATE 로 표시하고 쓰지 않는다'이므로, 같은 파일 :29-34 가 지목한 sp-test-driven-development·sp-systematic-debugging·sp-verification-before-completion·sp-using-git-worktrees·sp-finishing-a-development-branch 는 현재 배선에서 전부 사용 금지 상태다. G-M2 는 D-67 로 이미 닫혔는데(romeo.project.yaml:22) 그 사실이 라우터에 도달하지 않는다.

**제안된 수정:** romeo/policy.py 의 load_policy 옆에 load_project_state(root) 를 만들어 .harness/romeo.project.yaml 을 읽고, route 를 부르는 지점(romeo/cli.py 의 cmd_route·cmd_new, romeo/close.py:68)에서 project_state 로 넘긴다. 파일이 없으면 지금과 같은 pending_gate 동작을 유지한다. 배선 후 ./bin/romeo route --fixtures fixtures/requests --report 의 PART_PENDING_GATE 경고 수가 줄어드는 것으로 검증한다(현재 ×20).

## F08 [important] (요구대비-누락)
**대상:** `.github/workflows/harness.yml`

**요약:** 핵심 동등성 게이트 명령 `bin/romeo fixtures parity` 가 CI 에 없다. 다른 romeo 게이트 명령(route·fixtures check·validate·compile --check·vendor check·notices --check·doctor --strict)은 전부 스텝으로 있는데, 계획 §10 #11 이 지목한 게이트 명령만 빠져 있어 `fixtures/parity/*.yaml` 의 구조 오류나 판정 회귀가 CI 에서 걸리지 않는다.

**증거:**

`.github/workflows/harness.yml` 의 steps 실측: `unittest` → `정책표 fixture 리포트` → `fixture 스키마 검사`(`bin/romeo fixtures check`) → `작업 문서 검증` → `어댑터 컴파일 대조` → `vendor 대조 · provenance id` → `THIRD_PARTY_NOTICES 신선도` → `부착 검증 · 충돌 fixture`. **`fixtures parity` 스텝 없음.**
`romeo/cli.py:117-125` 의 `PARITY_INVALID` 경로(구조 오류 시 exit 1)와 `:126` 의 게이트 exit 1 경로는 `python3 -m unittest discover` 로는 실행되지 않는다 — `tests/test_parity.py` 는 임시 디렉터리와 메모리 케이스로 CLI 를 부르고, 저장소 케이스에 대해서는 `check_parity_cases` 만 돌린다(`tests/test_parity.py:1-13` 계약 1번).

**제안된 수정:** `fixture 스키마 검사` 스텝 바로 뒤에 추가한다:
```yaml
      - name: 동등성 판정 (핵심 동등성 게이트)
        run: bin/romeo fixtures parity --report
```
위 blocker 2번(게이트를 관측 케이스에 묶기)을 먼저 반영한 뒤에 붙여야 한다 — 지금 그대로 붙이면 손으로 쓴 케이스가 CI 에서 매번 PASS 를 찍는다.

## F09 [important] (요구대비-누락)
**대상:** `.harness/bindings.yaml`

**요약:** 역할 교체 실행에서 검토자가 되는 런타임의 read-only 강제 수단이 정본(bindings.yaml)에 선언돼 있지 않다. `enforcement` 는 `roles.reviewer`(codex)에만 있고 `parity_swap.reviewer: claude` 에는 대응 선언이 없어, 컴파일 산출물(CLAUDE.md·AGENTS.md 역할표)에도 교체 실행의 강제 수단이 인쇄되지 않는다. 계획 §7 M2 는 "Claude 는 `--allowedTools`(Read·Grep·Glob·읽기 전용 Bash)로 실행" 을 명시적으로 요구한다(계획 :506).

**증거:**

`.harness/bindings.yaml:18-24` — `roles.reviewer` 에만 `enforcement: "codex -s read-only"` 와 `defensive_check` 가 있다. 바로 아래 `parity_swap: {implementer: codex, reviewer: claude}` 에는 `enforcement` 키가 없다.
컴파일 산출물(`CLAUDE.md` managed block 역할표) 실측:
```
| `implementer` | claude | 예 | 작업 공간 쓰기 허용 |
| `reviewer` | codex | **아니오** | codex -s read-only |
역할 교체 재실행: implementer=codex · reviewer=claude. 같은 판정이 나와야 동등성 게이트를 통과한다.
```
→ 교체 실행의 "어떻게 강제하나" 칸이 없다.
`adapters/orca/RUNBOOK.md:156-160` 은 `--tools "Read,Grep,Glob" --disallowedTools "Edit Write Bash"` 를 제시하되 계획이 지목한 `--allowedTools` 와 다르고, 같은 문단에서 "어느 플래그가 실제로 쓰기를 막는지는 실행해서 확인하지 않았다" 고 미검증으로 남긴다(`RUNBOOK.md:266`). 즉 강제 수단이 정본에도 없고 검증도 없다.

**제안된 수정:** `.harness/bindings.yaml` 의 `parity_swap` 를 값 두 개짜리 맵에서 역할별 블록으로 승격해 `parity_swap.reviewer: {runtime: claude, write: false, enforcement: "claude -p --allowedTools \"Read,Grep,Glob\"", defensive_check: ...}` 를 넣고, `romeo/compile.py:_render_instructions` 의 역할표에 교체 실행 행을 추가한다. 어느 플래그가 실제로 쓰기를 막는지 1회 프로브로 확인한 뒤 그 값을 쓰고, 확인 전에는 `enforcement: UNVERIFIED` 로 정직하게 표시한다.

## F10 [important] (요구대비-누락)
**대상:** `.harness/observations.yaml`

**요약:** 이번 라운드에 스킬이 9개→11개(claude)·10개→12개(codex)로 늘었는데 관찰 기록은 갱신되지 않았고, `romeo doctor` 는 관찰 텍스트의 존재 여부만 보고 "런타임 로드 관찰됨" 을 인쇄한다. 결과적으로 새 스킬 `implement`·`review` 는 어느 런타임에서도 로드가 관찰되지 않았는데 doctor 는 관찰된 것처럼 보고한다 — 계획 §10 #9 의 확인 기준 "doctor 에서 양쪽 discovery 확인" 이 새 스킬에 대해 충족되지 않았다.

**증거:**

```
$ ./bin/romeo doctor
## 스킬 파일 ...
  claude  11개 · .claude/skills · 런타임 로드 관찰됨 (2026-08-28 · ... 채택 7종 ... + plan · plan-close 가 모두 나타났다.)
  codex   12개 · .agents/skills · 런타임 로드 관찰됨 (2026-08-28 · ... .agents/skills/ 의 10개가 전부 나타났다 — finishing-a-development-branch · plan · plan-close · receiving-code-review · repo-archive · requesting-code-review · systematic-debugging · test-driven-development · using-git-worktrees · verification-before-completion. romeo doctor 가 센 목록과 이름까지 일치한다.)
```
관찰문이 열거한 이름에 `implement`·`review` 가 없고, "romeo doctor 가 센 목록과 이름까지 일치한다" 는 문장은 이제 사실이 아니다(센 값은 12, 열거는 10).
`romeo/doctor.py:229-232`: `seen = observed.get(s["runtime"])` → `mark = "관찰됨" if seen else "**미관찰**"` — 이름 대조도 개수 대조도 없다.
`.harness/observations.yaml:6` `updated: 2026-08-28` 이지만 내용은 컴파일 이전 상태다.

**제안된 수정:** `.harness/observations.yaml` 의 `runtime_load` 를 문자열에서 `{observed_at, skills: [이름 목록], note}` 구조로 바꾸고, `probe_skill_files` 가 센 이름 집합과 `skills:` 를 대조해 차집합이 있으면 `부분 관찰 (implement·review 미관찰)` 로 인쇄한다. 그 뒤 두 런타임 세션에서 새 스킬 2종이 목록에 뜨는지 실제로 관찰해 기록을 갱신한다. 관찰 전까지는 doctor 가 "관찰됨" 이라고 말하지 않아야 한다.

## F11 [important] (요구대비-누락)
**대상:** `adapters/codex/adapter.yaml`

**요약:** 역할 계약이 어느 런타임에도 투영되지 않는다. `core/roles/{implementer,reviewer}.yaml` 을 읽는 코드가 테스트 말고는 없고, 계획 §5.1(codex 어댑터 [M2] 산출물)과 §5.2 가 명시한 `.codex/agents/*.toml` 과 `.claude/agents/{implementer,reviewer}.md` 가 만들어지지 않았다. 런타임은 역할의 capabilities·allowed_paths·forbidden 을 보지 못하고, 컴파일 산출물에는 `.harness/bindings.yaml` 에서 뽑은 4칸 표만 인쇄된다.

**증거:**

```
$ grep -rn "core/roles|roles/implementer|roles/reviewer" --exclude-dir=.git . | grep -v docs/planning
tests/test_roles_envelopes.py:1,23,24,131
```
→ 소비자는 자기 테스트뿐. `romeo/compile.py` 는 `.harness/bindings.yaml` 만 읽는다(`grep -n "roles|bindings" romeo/compile.py` → `:126,136,140,145,259,269`).
```
$ ls .codex
ls: .codex: No such file or directory
$ ls .claude/agents
repo-archive-coordinator.md      ← implementer.md·reviewer.md 없음
$ cat .harness/compiled.yaml   # 산출물 26개 — agents 관련 0건
```
계획 `:506` 만들 것: "`adapters/claude`·`adapters/codex`(`romeo compile`: `AGENTS.md`·`CLAUDE.md`·`.claude/*`·`.agents/skills/*`·**`.codex/agents/*.toml`**, managed marker + source hash)". 계획 §5.1 codex 행: "`.agents/skills`, `.codex/agents/*.toml`, `AGENTS.md`, NDJSON 파서 [M2]". 폐기 목록(decision-register.md:145)에 폐기된 것은 `.codex/skills` 심링크와 `.codex/prompts` 이지 `.codex/agents/*.toml` 이 아니다 — 이 항목을 취소한 결정 기록이 없다.

**제안된 수정:** 둘 중 하나를 명시적으로 한다. (a) `adapters/{claude,codex}/adapter.yaml` 에 `agents_dir`(`.claude/agents` / `.codex/agents`)와 역할별 매핑 템플릿을 추가하고 `romeo/compile.py` 가 `core/roles/*.yaml` 을 입력으로 읽어 두 런타임 형식으로 투영한다(`compiled.yaml` 에 등록, `compile --check` 대상). (b) `.codex/agents/*.toml` 을 하지 않기로 결정했다면 `docs/decisions/decision-register.md` 에 근거와 함께 폐기 항목으로 기록하고 계획 §5.1·§5.2·§7 M2 를 정정한다. 어느 쪽이든 지금처럼 계획에만 있고 저장소에도 결정 기록에도 없는 상태로 두지 않는다.

## F12 [important] (요구대비-누락)
**대상:** `adapters/orca/RUNBOOK.md`

**요약:** RUNBOOK §5 가 "`run_id`·`task_id`·`dispatch_id` 세 필드의 값은 `bin/romeo evidence run` 이 만든 evidence yaml 에 들어간다" 고 단언하지만, `task_id`·`dispatch_id` 는 항상 `null` 로만 기록되고 값을 넣을 수 있는 명령·플래그가 없다. 계획 §3.5 상태 계약("하네스는 evidence 에 run_id·task_id·dispatch_id 만 기록")의 배관이 비어 있다.

**증거:**

`adapters/orca/RUNBOOK.md:175-176`: "이 세 필드는 `romeo/evidence.py` 의 기록 구조에 이미 있다. 값은 `bin/romeo evidence run` 이 만든 `docs/work/<id>/evidence/<run>.yaml` 에 들어가고 ..."
`romeo/evidence.py:87`: `"repo_id": repo_id(project_root), "run_id": run_name, "task_id": None, "dispatch_id": None,` — 이후 어떤 코드도 이 둘을 갱신하지 않는다(`grep -rn "task_id|dispatch_id" romeo/` → `evidence.py:87` 과 `:126`(run_id 필터)뿐).
```
$ ./bin/romeo evidence run --help
optional arguments: -h --unit --run --label --root      ← --task-id / --dispatch-id 없음
$ grep -n "run_id|task_id|dispatch_id" docs/work/chg-20260827-rg-fallback-validate-245m/evidence/run-m1.yaml
4:run_id: run-m1
5:task_id: null
6:dispatch_id: null
```
또한 `run_id` 는 오케스트레이터 Run id(`run_7865ac0ae3e3` 형식)가 아니라 로컬 실행 이름(`run-m1`)이라 RUNBOOK §3.1 이 보관하라고 한 값과 같은 것이 아니다.

**제안된 수정:** `evidence run`·`evidence checks` 에 `--task-id`·`--dispatch-id`·`--orchestrator-run-id` 를 추가하고(모두 선택), 기존 레코드에 병합한다. `run_id`(로컬 실행 이름)와 오케스트레이터 Run id 를 같은 키에 섞지 말고 필드를 분리한다. 그 전까지는 RUNBOOK §5 의 문장을 "필드 자리는 있으나 값을 넣는 경로가 아직 없다(M2 미구현)" 로 정정해야 K-51 에 맞다.

## F13 [important] (실행가능성)
**대상:** `adapters/orca/RUNBOOK.md`

**요약:** §5 가 evidence 에 남기라고 지시한 `task_id`·`dispatch_id` 를 넣을 수단이 없다. CLI 에 해당 플래그가 없고 romeo/evidence.py 가 두 필드를 `None` 으로 하드코딩한다. `run_id` 도 orca Run id 가 아니라 날짜 문자열이 들어간다.

**증거:**

RUNBOOK:173-176 — "`run_id` · `task_id` · `dispatch_id` 세 개만 남긴다 … 값은 `bin/romeo evidence run` 이 만든 `docs/work/<id>/evidence/<run>.yaml` 에 들어가고".
실제 CLI:
```
$ ./bin/romeo evidence run --help
  --unit UNIT   --run RUN   --label LABEL   --root ROOT      ← task/dispatch 플래그 없음
$ ./bin/romeo evidence checks --help
  --unit UNIT   --run RUN   --root ROOT
```
실제 구현 romeo/evidence.py:87:
```
"repo_id": repo_id(project_root), "run_id": run_name, "task_id": None, "dispatch_id": None,
```
실제 산출물(scratchpad 재현):
```
run_id: run-20260828
task_id: null
dispatch_id: null
```
`run_name` 기본값은 romeo/evidence.py:78 의 `time.strftime("run-%Y%m%d")` 다. RUNBOOK §3.1 이 정의한 Run id 는 `run_7865ac0ae3e3` 형식이고, RUNBOOK §2 표의 워커 명령 `bin/romeo evidence checks --unit <id>` 에는 `--run` 이 없으므로 두 이름 공간이 절대 만나지 않는다. 그 결과 §3.6 의 `docs/work/<id>/result/<run>-implementer.json` 과 §5 의 `docs/work/<id>/evidence/<run>.yaml` 의 `<run>` 이 서로 다른 값이 된다.

**제안된 수정:** `romeo evidence run`/`checks` 에 `--task`·`--dispatch` 플래그를 더해 romeo/evidence.py:87 의 두 필드를 채우게 하고, RUNBOOK §2 표의 워커 명령을 `bin/romeo evidence checks --unit <id> --run <orca run id> --task <task-id> --dispatch <dispatch-id>` 로 고친다. 플래그 추가를 M3 로 미룬다면 RUNBOOK §5 를 "`run_id` 만 `--run` 으로 남길 수 있고 `task_id`·`dispatch_id` 는 기록 수단이 아직 없다" 로 바꾸고 §11 미검증 목록에 올려야 한다.

## F14 [important] (실행가능성)
**대상:** `adapters/orca/RUNBOOK.md`

**요약:** §4 의 방어 검사 블록(164-169행)을 그대로 붙여 넣으면 실패한다. `$D=.harness/runs/<id>/<run>` 는 `romeo evidence run` 만이 만드는 디렉터리인데, 이 블록은 검토자 기동 '직전' 에 돌리라고 되어 있어 그 시점에 존재하지 않는다.

**증거:**

RUNBOOK:164-168 블록을 문자 그대로 실행:
```
$ D=.harness/runs/chg-20260827-rg-fallback-validate-245m/run_7865ac0ae3e3
$ git -C $S status --porcelain > $D/review-tree-before.txt
(eval):6: no such file or directory: .harness/runs/chg-.../run_7865ac0ae3e3/review-tree-before.txt
EXIT=1
```
디렉터리를 만드는 유일한 코드는 romeo/evidence.py:96-97 의 `log_dir = project_root / ".harness" / "runs" / unit_id / run_name; log_dir.mkdir(parents=True, exist_ok=True)` 이고, 이건 `romeo evidence run` 안에서만 돈다. scratchpad 실측에서도 `evidence run` 을 돌린 뒤에야 `.harness/runs/<id>/run-20260828/01-cmd-1.log` 가 생겼다. RUNBOOK:166 주석은 "검토자 기동 직전" 이므로 워커가 아직 아무 evidence 도 남기지 않은 시점이다. 같은 블록의 `<run>` 값 역시 위 finding 과 같은 이름 공간 충돌을 갖는다.

**제안된 수정:** 블록 첫 줄에 `mkdir -p "$D"` 를 넣는다. `.harness/runs/` 는 .gitignore:2 로 제외돼 있으니 부작용이 없다. 그리고 `<run>` 이 orca Run id 인지 romeo run 이름인지 한 값으로 고정해 §3.6·§4·§5 에서 같은 이름을 쓰게 한다.

## F15 [important] (요구대비-누락)
**대상:** `core/schemas/task-envelope.json`

**요약:** 작업 계약(TaskEnvelope)을 만들거나 검증하는 코드가 저장소에 하나도 없다. `core/workflows/implement/SKILL.md` 의 역할 분담 표는 "계약 | 하네스 | 승인된 Tech Spec 과 라우터 출력에서 작업 계약을 계산한다. 같은 입력이면 같은 계약" 이라고 선언하지만, 실제 유일한 생성 경로는 에이전트가 JSON 을 손으로 써서 git 제외 디렉터리에 두는 것이다 — 결정성도 검증도 성립하지 않는다.

**증거:**

```
$ grep -rn "task-envelope|result-envelope|task_envelope|result_envelope" romeo/ bin/ .github/
romeo/parity.py:19:SCHEMA_PATH = "core/schemas/result-envelope.json"
```
작업 계약 스키마의 소비자는 **0건**(테스트 `tests/test_roles_envelopes.py` 제외). `./bin/romeo --help` 의 서브커맨드에도 계약 생성 명령이 없다(`romeo/cli.py:1` 목록: route · card · new · validate · fixtures · approve · evidence · close · id · compile · doctor · vendor · notices).
`core/workflows/implement/SKILL.md` 역할 분담 표 1행: "| 계약 | 하네스 | ... 같은 입력이면 같은 계약 |", 절차 2번: "`core/schemas/task-envelope.json` 형식으로 만든다" — 만드는 주체가 명시돼 있지 않다.
`adapters/claude/workflows/implement.md:3` 은 `.harness/runs/<id>/<run>/task-implementer.json` 에 쓰라고 지시하는데, `.gitignore:2` 가 `.harness/runs/` 를 제외하고 `romeo/evidence.py:18` 의 `exclusions()` 가 `.harness` 를 `dirty_tree_hash`·`changed_files` 에서도 제외한다 — 계약 파일이 바뀌어도 종료 검사가 알아채지 못한다.

**제안된 수정:** `romeo/envelope.py` + `bin/romeo envelope build --unit <id> --role implementer|reviewer` 를 추가해 승인된 `spec.md`(`spec_ref`·`base_sha`)와 `route()` 출력(`guards`·`isolation`→`workspace`)에서 계약을 계산하고 `core/schemas/task-envelope.json` 으로 자체 검증한 뒤 파일로 쓴다. 출력 경로는 git 제외가 아닌 `docs/work/<id>/task/<run>-<role>.json` 으로 옮겨 K-62 등록 대상이 되게 한다. 두 역할에 같은 입력이면 바이트 동일한 계약이 나오는지 테스트한다.

## F16 [important] (요구대비-누락)
**대상:** `docs/planning/progress.md`

**요약:** 계획 §10 #8 의 세 확인 기준 중 "reviewer 쓰기 시도 거부 로그" 를 만족하는 산출물이 저장소에 없다. 이것은 이번 라운드에서 제외한 실제 T1 관통·Orca 위임과 무관한 단독 프로브(`codex exec -s read-only` 로 쓰기를 시도해 거부를 관찰)인데도 기록이 없고, progress.md 의 체크리스트 번호가 계획 §10 과 어긋나 이 기준이 어느 행에도 매핑되지 않은 채 사라져 있다.

**증거:**

계획 `docs/planning/implementation-plan.md:640`: `| 8 | 역할 2(reviewer 런타임 read-only) + 바인딩 승인 + envelope 스키마 | .harness/bindings.yaml 승인 기록, 스키마 테스트 PASS, reviewer 쓰기 시도 거부 로그 |`
```
$ grep -rn "review-tree|쓰기 시도" --include='*.md' --include='*.yaml' . (vendor/·archive/ 제외)
docs/planning/implementation-plan.md:298,640   ← 계획 원문뿐
adapters/orca/RUNBOOK.md:166,167,168           ← 앞으로 할 방법의 서술뿐
```
실제 거부 관찰 기록 0건. `.harness/observations.yaml` 에도 항목 없음. `adapters/orca/RUNBOOK.md:265` 이 "검토자 read-only 강제의 실제 효력 ... 실행해 보지 않았다" 로 미검증 선언.
번호 어긋남: progress.md 의 `#8` 은 "G-M2 채택 게이트"(계획 §10 의 `#8b`), `#9` 는 "LICENSE Apache-2.0 교체"(계획 §10 에는 없는 항목)다. 계획 §10 `#8` 자체에 대응하는 행이 progress.md 에 없고 `19~ 역할 실행·envelope·Orca 위임·parity (미착수)` 에 묶여 버렸다.

**제안된 수정:** 단독 프로브를 1회 실행해 증거를 남긴다 — 임시 파일 쓰기를 지시하는 최소 프롬프트를 `codex exec -s read-only -C <repo>` 로 돌리고 종료 코드·거부 메시지·전후 `git status --porcelain` diff 를 `.harness/runs/` 에 저장한 뒤 `.harness/observations.yaml` 에 `reviewer_write_refusal` 항목으로 기록한다(교체 실행 쪽 claude 플래그도 같이). 동시에 progress.md 의 체크리스트 번호를 계획 §10 번호(#8·#8b·#9…)에 맞춰 재정렬해 누락 행이 눈에 보이게 한다.

## F17 [important] (규율-위반)
**대상:** `adapters/codex/adapter.yaml:7 · adapters/orca/RUNBOOK.md:27-38,269-270`

**요약:** K-66 권한 상한이 한쪽 런타임에만 컴파일된다. 역할 교체 실행에서 구현자가 되는 쪽에는 승인 게이트도 샌드박스 매핑도 없다.

**증거:**

adapters/codex/adapter.yaml:7 `settings_file: null` — codex 쪽에는 settings_ask/settings_deny 를 투영할 대상 파일 자체가 없다. 반면 adapters/claude/adapter.yaml 은 settings_ask 12건(git push·gh pr merge·git worktree remove·git branch -D·gh api·gh pr comment·gh pr review·git reset --hard 등)과 settings_deny 5건을 .claude/settings.json 으로 내보낸다.

.harness/bindings.yaml:26 `parity_swap: {implementer: codex, reviewer: claude}` 이므로 교체 실행에서 쓰기 권한을 가진 쪽이 codex 가 된다.

RUNBOOK.md:27-38 의 계약→플래그 매핑 표에는 `allowed_paths: []` (검토자) → `codex exec -s read-only` 한 줄만 있고 구현자 쪽 샌드박스·승인 정책 매핑이 없다. core/policy/execution-guards.yaml:77-79 도 codex 에 대해 reviewer_sandbox: read-only 와 approval_policy: on-request 만 선언한다.

RUNBOOK.md:269-270 은 미검증 항목으로 '검토자 read-only 강제의 실제 효력'과 '역할 교체 실행에서 검토자가 되는 런타임의 강제 수단'만 남겼고, 구현자 쪽 비대칭은 적지 않았다. 결과적으로 동등성 게이트는 '권한 상한이 서로 다른 두 실행'을 비교하면서 같은 판정이 나오면 동등하다고 선언하게 된다.

**제안된 수정:** 두 가지를 같이 한다. (1) .harness/bindings.yaml 의 roles.implementer 에 reviewer 와 대칭인 enforcement 키를 넣고(예: 승인 대상 명령 목록 + 런타임별 표현), adapters/codex 쪽에 그것을 실제 파일로 내보낼 대상을 정한다 — codex 는 settings.json 이 없으므로 worker-start 시 `codex exec -s workspace-write --approval-policy on-request` 형태를 RUNBOOK 매핑 표에 명시하는 것이 최소안이다. (2) RUNBOOK §11 미검증 목록에 '구현자 쪽 권한 상한이 런타임마다 다르다'를 추가해, 지금 그 비대칭 위에서 동등성 판정이 돌고 있다는 사실을 문서에 남긴다.

## F18 [important] (규율-위반)
**대상:** `adapters/orca/RUNBOOK.md:162-171`

**요약:** 판정의 유효/무효를 가르는 방어 검사 산출물을 증거 기록 명령이 아니라 셸 리다이렉션으로 손수 만든다 — AGENTS.core §4 '증거는 손으로 쓰지 않고 증거 기록 명령으로만 만든다'(K-51) 위반이고, 산출물이 gitignore 된 경로에 남아 등록되지 않는다(K-62).

**증거:**

RUNBOOK.md:164-169
  D=.harness/runs/<id>/<run>            # git 제외 경로다(K-24)
  git -C <검토 대상 워크트리> status --porcelain > $D/review-tree-before.txt
  git -C <검토 대상 워크트리> status --porcelain > $D/review-tree-after.txt
  diff $D/review-tree-before.txt $D/review-tree-after.txt

:171 '성공 신호: diff 종료 코드 0(출력 없음). 다르면 그 판정은 무효다.' — 즉 이 파일 두 개가 리뷰 판정의 유효성을 결정하는 증거다. 그런데 `bin/romeo evidence run --unit <id> -- <명령>` 을 거치지 않으므로 docs/work/<id>/evidence/<run>.yaml 에 명령·종료코드·head_sha 가 기록되지 않는다.

$ cat .gitignore
.harness/runs/
.harness/cache/

따라서 산출물은 작업 단위 폴더 밖 + git 추적 밖 + frontmatter evidence: 미등록 세 조건을 동시에 만족한다. core/principles/AGENTS.core.md:50 '등록되지 않은 산출물은 종료 검사가 인정하지 않는다'. 같은 문제가 adapters/claude/workflows/review.md:6 과 adapters/codex/workflows/review.md:6 ('실행 전후 git status --porcelain 출력이 같아야 한다')에도 그대로 투영돼 있다.

**제안된 수정:** RUNBOOK §4 의 두 줄을 `bin/romeo evidence run --unit <id> --label review-tree-before -- git -C <워크트리> status --porcelain` / `--label review-tree-after` 로 바꾼다. 그러면 두 실행이 evidence 에 명령·exit code·head_sha 와 함께 남고 종료 검사가 인정하는 산출물이 된다. diff 비교는 evidence 에 기록된 두 실행의 stdout 을 대조하는 형태로 다시 쓴다. adapters/{claude,codex}/workflows/review.md:6 도 같은 문구로 맞춘다(어댑터 원본을 고친 뒤 ./bin/romeo compile && ./bin/romeo compile --check 재실행 필요).

## F19 [important] (규율-위반)
**대상:** `fixtures/parity/pr-license-field-t1.yaml:37-45,72-80 · core/roles/reviewer.yaml:12,15-19`

**요약:** 정본 parity 케이스가 검토자에게 '셸 명령 3건을 exit 0 으로 실행했다'고 기록한다 — 검토자 역할 계약에 run-command 능력이 없고, 그 checks 를 뒷받침하는 evidence_ref 는 null 이다.

**증거:**

core/roles/reviewer.yaml:12 `capabilities: [read, search]` — run-command 없음. :15-19 `allowed_paths.scope: none` / '어떤 경로에도 쓰지 않는다'. outputs.evidence: none.

fixtures/parity/pr-license-field-t1.yaml:37-45 (baseline.reviewer):
  checks:
    - {id: check-1, command: bash scripts/validate-repo-archive.sh …, exit_code: 0}
    - {id: check-2, command: python3 scripts/generate-archive-index.py --check, exit_code: 0}
    - {id: check-3, command: python3 -m unittest tests.test_provenance, exit_code: 0}
  gate_verdict: PASS
  evidence_ref: null
:72-80 (swapped.reviewer) 도 동일.

romeo/parity.py:139-144 는 이 checks 를 역할별로 짝지어 비교하므로, 게이트가 '검토자가 required_checks 를 실행한다'를 정상 상태로 굳힌다. 반면 core/workflows/review/SKILL.md:20 은 검토자에게 'required_checks 가 그 주장을 실제로 검사하는가'를 읽고 판단하라고만 하고 실행하라고 하지 않으며, adapters/orca/RUNBOOK.md:255 는 위임 계층이 대신 실행하는 것도 금지한다. 즉 이 3건을 실행한 주체가 계약상 존재하지 않는다.

**제안된 수정:** 두 파일 중 하나를 정한다. 권고는 케이스 쪽 수정이다 — pr-license-field-t1.yaml 의 reviewer 봉투에서 checks 를 [] 로 비우고(검토자는 검사를 실행하지 않는다), 대신 findings 와 gate_verdict 만 남긴다. 그러면 parity.py:141 의 _check_key 비교가 양면 모두 [] 로 일치하고 역할 계약과 모순이 사라진다. 검토자가 정말 검사를 재실행해야 한다면 reviewer.yaml:12 에 run-command 를 추가하고 review/SKILL.md 에 실행 단계를 명시해야 하며, 그때는 read-only 강제(codex -s read-only)와의 양립 가능성을 먼저 실측해야 한다.

## F20 [important] (규율-위반)
**대상:** `romeo/close.py:69-71 · core/workflows/review/SKILL.md:26-27`

**요약:** 검토자가 낸 gate_verdict 가 완료 판정에 전혀 연결되지 않는다. review/ 디렉터리가 비어 있지 않기만 하면 FAIL 판정이 들어 있어도 close 는 PASS 다.

**증거:**

romeo/close.py:69-71
  if out["reviewer"] != "none":
      review_dir = udir / "review"
      check("HAS_REVIEW", review_dir.is_dir() and any(review_dir.iterdir()), "검토자가 필요한 패키지인데 review/ 가 비어 있다(M2)")

디렉터리 존재와 비어있지 않음만 본다. 파일을 core/schemas/result-envelope.json 으로 검증하지도, gate_verdict 값을 읽지도 않는다. 반면 core/workflows/review/SKILL.md:26-27 은 'PASS · FAIL · BLOCKED 중 하나를 낸다. 종료 조건은 증거다 — 수용 기준마다 그것을 뒷받침하는 증거를 지목할 수 있을 때만 PASS 다' 라고 판정을 만들게 하고, adapters/orca/RUNBOOK.md:118-120 이 그 결과를 docs/work/<id>/review/<run>-reviewer.json 에 두게 한다. 만들어진 판정을 읽는 소비자가 없다.

$ grep -rn "gate_verdict" romeo/
romeo/parity.py:145,147,148,151  ← 동등성 비교에만 쓰인다. close.py 에는 없다.

결과적으로 '검토자 FAIL' 과 '빈 텍스트 파일 한 개'가 종료 검사에서 구별되지 않는다(K-51 · K-63 상태 소유권).

**제안된 수정:** close.py 의 HAS_REVIEW 를 둘로 나눈다. REVIEW_VALID — review/ 안의 *.json 을 result-envelope.json 으로 검증하고 실패하면 error. REVIEW_VERDICT — 가장 최근 리뷰 봉투의 gate_verdict 가 PASS 가 아니면 error 로 떨어뜨리고 detail 에 blocked_reason 과 findings 개수를 인쇄한다. 검증 명령은 romeo/schema.py 의 validate 를 그대로 재사용하면 되고, tests/test_close.py 에 FAIL 봉투를 넣은 케이스를 추가해 close 가 FAIL 로 떨어지는지 확인한다.

## F21 [important] (규율-위반)
**대상:** `romeo/parity.py:164-203 · fixtures/parity/*.yaml`

**요약:** '핵심 동등성 게이트: PASS' 가 전부 손으로 작성한 합성 데이터(source.kind: authored)에서 계산되는데, 리포트가 그 사실을 인쇄하지 않는다 — 관측 0건인 상태가 통과로 보인다(K-51).

**증거:**

check_parity_cases 는 source 를 필수 키로 요구하지만(parity.py:24 REQUIRED_KEYS) 값을 읽는 곳이 없다:

$ grep -n "source" romeo/parity.py
24:REQUIRED_KEYS = ("id", "title", "unit_id", "expect", "baseline", "swapped", "source")
(다른 참조 없음)

$ grep -rn "kind:" fixtures/parity/
pr-license-field-t1.yaml:84:  kind: authored
pr-blocked-capability.yaml:44:  kind: authored
pr-t0-implementer-only.yaml:46:  kind: authored
pr-checks-drift.yaml:48:  kind: authored
pr-verdict-drift.yaml:47:  kind: authored
pr-license-field-t1-observed.yaml:21:  kind: planned   ← 유일한 관측 자리표이고 status: pending

$ ./bin/romeo fixtures parity --report
parity 리포트 · 6건(실행 5 · 미실행 1) · 판정 PASS · 동일 3 · 불일치 2(전부 기대함)
핵심 동등성 게이트: PASS

실행으로 계상된 5건이 100% authored 다. format_parity(:181-203)는 미실행 건수는 분리해 인쇄하지만 authored/observed 는 구분하지 않아, 이 한 줄만 보는 사람에게는 '역할을 바꿔도 같은 판정이 났다'는 관측이 있는 것처럼 읽힌다. 실제로는 검사기가 옳게 판정한다는 증거일 뿐이다(G4 보고도 같은 취지로 미검증에 적었다).

**제안된 수정:** format_parity 의 첫 줄과 마지막 줄에 source.kind 집계를 넣는다: '핵심 동등성 게이트: PASS (관측 0 · 작성 5)' 처럼. 그리고 run_parity 의 verdict 계산에 observed 건수 0이면 verdict 를 PASS 로 두지 않는 조건(또는 별도 필드 observed_verdict)을 넣어, 실제 교차 실행이 pr-license-field-t1-observed.yaml 을 채우기 전에는 마일스톤 완료로 읽히지 않게 한다. tests/test_parity.py 에 'authored 만으로는 observed 게이트가 PASS 가 아니다' 케이스를 추가한다.

## F22 [minor] (규율-위반)
**대상:** `.agents/skills/implement/SKILL.md:3 · .agents/skills/review/SKILL.md:3 · adapters/codex/adapter.yaml:14-21`

**요약:** 두 런타임의 K-60 문구가 다르다. codex 쪽 산출물 description 에만 '라우터가 켤 때만 쓴다 — 스스로 켜지지 않는다'가 빠졌다.

**증거:**

$ head -3 .claude/skills/implement/SKILL.md
description: … 실제로 구현할 때 라우터가 켤 때만 쓴다 — 스스로 켜지지 않는다. …

$ head -3 .agents/skills/implement/SKILL.md
description: … 실제로 구현할 때 라우터가 켠다. …

$ head -3 .agents/skills/review/SKILL.md
description: … 구현이 끝난 뒤 켠다. …

원인은 adapters/codex/adapter.yaml:15 '# description 은 적지 않는다 — 코어 frontmatter 값을 그대로 쓴다' 이고, 코어 값(core/workflows/implement/SKILL.md:3, review/SKILL.md:3)에는 그 절이 없다. description 은 런타임이 스킬을 언제 띄울지 판단하는 문구이므로, 자동 활성화를 막는 문장이 한쪽에만 있으면 K-60 의 방어가 런타임마다 다르다. `when: 승인 뒤 라우터가 켤 때만` 은 지침 파일의 절차 표에만 인쇄되고 스킬 frontmatter 에는 들어가지 않는다.

**제안된 수정:** 코어 쪽을 강화하는 것이 낫다 — core/workflows/{implement,review}/SKILL.md 의 frontmatter description 을 '라우터가 켤 때만 쓴다 — 스스로 켜지지 않는다'로 바꾸면 codex 는 그대로 상속하고 claude 는 이미 같은 문구다. 그 뒤 adapters/claude/adapter.yaml 의 중복 description 을 지워 한 곳에서만 관리한다. 고친 뒤 ./bin/romeo compile && ./bin/romeo compile --check 로 양쪽 산출물이 같은 문구가 되는지 확인한다.

## F23 [minor] (규율-위반)
**대상:** `.harness/bindings.yaml:21 · core/roles/reviewer.yaml:15-19`

**요약:** 컴파일이 실제로 읽는 bindings.yaml 의 reviewer scope 문구가 새 역할 계약과 정면으로 모순된다 — 한쪽은 '리뷰 보고서 작성', 다른 쪽은 '어떤 경로에도 쓰지 않는다'.

**증거:**

.harness/bindings.yaml:21
    scope: 읽기·검색·리뷰 보고서 작성(작업 공간 밖)

core/roles/reviewer.yaml:15-19
  allowed_paths:
    scope: none
    note: 어떤 경로에도 쓰지 않는다. 결과는 결과 계약으로만 나간다.
      검토자를 띄운 쪽이 그 결과를 docs/work/{unit_id}/review/ 에 기록한다 —
      검토자 자신이 쓰는 것이 아니다(K-66 · 종료 검사의 리뷰 요구).

bindings.yaml:19 `enforcement: "codex -s read-only"` 와 adapters/codex/workflows/review.md:2 '샌드박스가 쓰기를 막는다' 도 reviewer.yaml 쪽 해석과만 양립한다. bindings.yaml 은 romeo compile 의 입력(:1)이므로 모순된 문구가 지침 파일 방향으로 흘러갈 수 있는 쪽이다. G1·G3 두 구현 에이전트가 모두 배정 밖이라 보고만 하고 넘긴 항목이다.

**제안된 수정:** .harness/bindings.yaml:21 을 `scope: 읽기·검색·판정(파일 쓰기 없음)` 으로 고친다. 사실 관계를 바꾸는 것이 아니라 이미 enforcement 와 reviewer.yaml 이 정한 것을 문구에 맞추는 것이므로 되돌리기 쉽다. 고친 뒤 ./bin/romeo compile && ./bin/romeo compile --check 를 돌려 지침 파일 managed block 이 갱신되는지 확인한다.

## F24 [minor] (요구대비-누락)
**대상:** `.harness/bindings.yaml`

**요약:** `roles.reviewer.scope` 문구가 이번 라운드에 만든 `core/roles/reviewer.yaml`·`adapters/orca/RUNBOOK.md` 의 해석과 모순된다. bindings 는 검토자가 "리뷰 보고서 작성" 을 한다고 읽히지만, 역할 계약과 런북은 검토자가 어떤 경로에도 쓰지 않고 띄운 쪽이 기록한다고 못박는다. 이 문구는 컴파일되어 두 지침 파일에 그대로 들어간다.

**증거:**

`.harness/bindings.yaml:21`: `scope: 읽기·검색·리뷰 보고서 작성(작업 공간 밖)`
`core/roles/reviewer.yaml` allowed_paths: `scope: none` · `note: 어떤 경로에도 쓰지 않는다. ... 검토자를 띄운 쪽이 그 결과를 docs/work/{unit_id}/review/ 에 기록한다 — 검토자 자신이 쓰는 것이 아니다`
`core/workflows/review/SKILL.md` 7절: "이 절차는 결과 계약을 출력할 뿐이고, 그것을 `docs/work/<id>/review/` 에 파일로 남기는 것은 검토자를 띄운 쪽의 책임이다"
`adapters/orca/RUNBOOK.md:119`: "**검토자는 자기 결과를 스스로 쓰지 않는다.**"
`.harness/bindings.yaml:20` 의 `enforcement: "codex -s read-only"` 는 물리적으로 쓰기를 막으므로 bindings 문구대로면 계약 자체가 실행 불가능하다.

**제안된 수정:** `.harness/bindings.yaml:21` 을 `scope: 읽기·검색·판정(파일 쓰기 없음 — 결과 기록은 띄운 쪽)` 으로 고치고 `./bin/romeo compile && ./bin/romeo compile --check` 를 다시 돌린다. 문구 변경이라 되돌리기 쉽지만 지침 파일 두 개에 투영되므로 사람의 확인을 받고 진행한다.

## F25 [minor] (실행가능성)
**대상:** `core/policy/execution-guards.yaml`

**요약:** 81행의 gate-create 예시가 CLI 계약과 다른 인자 형식을 쓴다 — `--options approve,reject` 인데 도움말은 `<json_array>` 를 요구한다. RUNBOOK §8 은 올바른 JSON 배열 형식을 쓰고 있어 정본 두 곳이 어긋난다.

**증거:**

```
$ orca orchestration gate-create --help
Usage: orca orchestration gate-create --task <task_id> --question <text> [--options <json_array>] ...
```
core/policy/execution-guards.yaml:81:
```
    gate: "orca orchestration gate-create --question <설명> --options approve,reject"
```
adapters/orca/RUNBOOK.md:229 (같은 명령, 다른 형식):
```
orca orchestration gate-create --task <task-id> --question "<설명>" --options '["approve","reject"]' --json
```
execution-guards.yaml 쪽은 필수 인자 `--task` 도 빠져 있다. 상태를 바꾸는 명령이라 실제 실행으로 실패를 증명하지는 않았다(도움말 계약 대조까지만).

**제안된 수정:** core/policy/execution-guards.yaml:81 을 RUNBOOK §8 과 같은 형식(`--task <task_id>` 포함, `--options '["approve","reject"]'`)으로 맞춘다. 다만 이 줄은 `claude`·`codex`·`orca` 를 그대로 담고 있어 C-C6(코어에 도구명 금지)에도 걸린다 — 형식만 고치기보다 `enforcement:` 블록 전체를 `.harness/bindings.yaml` 이나 `adapters/` 로 옮기는 편이 낫다.

## F26 [minor] (실행가능성)
**대상:** `core/workflows/implement/SKILL.md`

**요약:** 2번이 `workspace` 를 '라우터의 격리 값' 이라고만 하는데 라우터는 `none` 도 낸다. `none` 은 task-envelope 의 `workspace` enum 에 없어 스키마 검증에 실패한다(현재 정책상 도달 불가하지만 문서에 그 전제가 없다).

**증거:**

```
$ grep -rn "isolation" core/policy/packages.yaml
94:    isolation: none      (base.none)
100:    isolation: current   (base.T0)
106/111: isolation: worktree (base.T1/T2)
```
33개 fixture 라우팅 실측: `isolation='none'` 5건(fx-payment-record-lookup·fx-posthog-structure-report·fx-s15-interview-prep-lightweight·fx-s24-commerce-ops-agent-md·fx-survey-targeting-answer).
implement/SKILL.md:26 이 지시한 매핑을 그대로 적용하면 romeo 자체 검증기가 거부한다:
```
fixture=fx-s15-interview-prep-lightweight  unit=T0 isolation='none'
  workspace = 'none'
  validate errors = ["$.workspace: 'none' 는 허용값 ['current', 'worktree'] 에 없음"]
```
다만 romeo/policy.py:179 이 `isolation = base["isolation"] if package else "none"` 이라 `isolation=='none'` 은 항상 `package==[]` 와 동치이고, 그때는 spec.md 가 없어 implement 1번이 먼저 `BLOCKED_DOCS` 로 끝난다 — 그래서 지금은 도달 불가다. 이 안전장치는 문서 어디에도 적혀 있지 않다.

**제안된 수정:** implement/SKILL.md 2번의 `workspace` 문장을 "라우터의 격리 값(`current`·`worktree`)이다. 격리가 `none` 이면 패키지가 비어 있다는 뜻이므로 작업 계약을 만들지 않고 1번의 `BLOCKED_DOCS` 로 끝낸다" 로 한 줄 보강한다. 스키마는 그대로 두는 편이 낫다 — `none` 을 enum 에 넣으면 '실행할 것이 없는 계약' 이 유효해진다.

## F27 [minor] (실행가능성)
**대상:** `provenance/imports.yaml`

**요약:** 215·219행의 `applied_by` 가 "adapters/orca/RUNBOOK.md 는 아직 없다" 라고 단언하는데 그 파일이 이번 라운드에 생겼다. 168행의 "실행 강제 미구현" 도 RUNBOOK §4 가 강제 명령형을 제공하면서 낡았다.

**증거:**

```
$ grep -n "RUNBOOK\|실행 강제" provenance/imports.yaml
168:        applied_by: "CLAUDE.md·AGENTS.md managed block (인쇄). 실행 강제 미구현"
215:        applied_by: "CLAUDE.md·AGENTS.md managed block (인쇄). adapters/orca/RUNBOOK.md 는 아직 없다"
219:        applied_by: "CLAUDE.md·AGENTS.md managed block (인쇄). adapters/orca/RUNBOOK.md 는 아직 없다"
$ ls -l adapters/orca/RUNBOOK.md
-rw-r--r--@ 1 julliettelee staff 19087 Aug 28 10:08 adapters/orca/RUNBOOK.md
```
`./bin/romeo vendor check`(exit 0)·`./bin/romeo notices --check`(exit 0) 는 `applied_by` 문자열을 검증하지 않으므로 모든 검사가 PASS 인 채로 이 드리프트가 남는다. 부수 확인: RUNBOOK·implement·review 가 인용한 sp-* id 7종(`sp-test-driven-development`·`sp-systematic-debugging`·`sp-verification-before-completion`·`sp-using-git-worktrees`·`sp-finishing-a-development-branch`·`sp-requesting-code-review`·`sp-receiving-code-review`)은 모두 imports.yaml 에 `status: accepted` 로 실재한다 — 없는 id 0건.

**제안된 수정:** 215·219행을 `"CLAUDE.md·AGENTS.md managed block (인쇄) + adapters/orca/RUNBOOK.md §3·§10 (위임 명령형)"`, 168행을 `"... + adapters/orca/RUNBOOK.md §4 (codex -s read-only 명령형)"` 로 갱신한다. 재발을 막으려면 `applied_by` 가 가리키는 경로가 실재하는지 검사하는 단언을 tests/test_provenance.py 에 붙인다.

## F28 [minor] (요구대비-누락)
**대상:** `romeo/close.py`

**요약:** 종료 검사가 결과 계약을 전혀 검증하지 않는다. `HAS_REVIEW` 는 `docs/work/<id>/review/` 가 비어 있지 않은지만 보고, 구현자 결과 계약이 놓이는 `docs/work/<id>/result/` 는 아예 보지 않는다. 계획 §7 M2 관찰 가능한 결과가 요구하는 "ResultEnvelope 2개" 를 close 가 확인하지 못한다.

**증거:**

`romeo/close.py:71`: `check("HAS_REVIEW", review_dir.is_dir() and any(review_dir.iterdir()), "검토자가 필요한 패키지인데 review/ 가 비어 있다(M2)")` — 파일 내용·스키마·역할·`base_sha` 를 보지 않으므로 빈 텍스트 파일 하나로도 통과한다.
`grep -rn "/result/" romeo/` → 히트 0건. `result/` 를 만들거나 읽는 코드가 없다(경로는 `adapters/{claude,codex}/workflows/implement.md:7` 과 `adapters/orca/RUNBOOK.md:117` 에만 문자열로 존재).
`grep -rn "result-envelope" romeo/` → `romeo/parity.py:19` 하나뿐 — close 는 스키마를 불러오지도 않는다.

**제안된 수정:** `close_unit` 에 `RESULT_ENVELOPE_VALID` 검사를 추가한다: `docs/work/<id>/result/*.json` 과 `review/*.json` 을 `core/schemas/result-envelope.json` 으로 검증하고, `unit_id` 일치·`role` 일치·`evidence_ref` 가 실제 evidence 파일을 가리키는지 확인한다. 검토자가 필요한 패키지에서는 `review/` 에 유효한 `role: reviewer` 계약이 1건 이상 있어야 PASS 로 한다.

## F29 [minor] (요구대비-누락)
**대상:** `tests/test_doc_commands.py`

**요약:** 이번 라운드에 추가한 `adapters/orca/RUNBOOK.md` 가 "문서에 적힌 romeo 명령이 실제 CLI 와 맞는가" 회귀 가드(F-05 대응)의 검사 범위 밖이다. RUNBOOK 은 `bin/romeo evidence approve`·`evidence checks` 를 절차로 지시하는 실행 문서인데, 다른 어댑터 문서와 달리 파서 대조를 받지 않는다.

**증거:**

`tests/test_doc_commands.py:17-21`:
```python
DOC_GLOBS = ["core/workflows/*/SKILL.md", "adapters/*/workflows/*.md", "core/templates/*.md"]
```
실측 커버 목록(18개)에 `adapters/orca/RUNBOOK.md` 없음:
```
$ python3 -c "from tests.test_doc_commands import doc_files; [print(f) for f in doc_files()]"
... core/workflows/{implement,plan,plan-close,review}/SKILL.md · adapters/{claude,codex}/workflows/*.md · core/templates/*.md · .claude|.agents/skills/{plan,plan-close}/SKILL.md
```
같은 파일이 실제로 CLI 와 어긋나는 주장을 담고 있다(위 `RUNBOOK.md:175-176` 의 task_id·dispatch_id 건) — 이 가드가 있었다면 문자열 검사 수준에서는 못 잡았겠지만, 명령·플래그 오타 계열은 걸린다.
덧붙여 `RUNTIME_SKILL_GLOBS` 도 `plan`·`plan-close` 만 열거해 새로 투영된 `.claude/skills/{implement,review}/SKILL.md`·`.agents/skills/{implement,review}/SKILL.md` 를 보지 않는다(코어 원본은 검사되므로 실질 위험은 낮다).

**제안된 수정:** `DOC_GLOBS` 에 `adapters/*/RUNBOOK.md` 를 추가하고, `RUNTIME_SKILL_GLOBS` 를 `.claude/skills/*/SKILL.md`·`.agents/skills/*/SKILL.md` 중 하네스 소유 스킬(plan·plan-close·implement·review) 4종으로 넓힌다. vendor 투영본은 romeo 명령을 쓰지 않으므로 이름 목록으로 한정한다.

## F30 [minor] (요구대비-누락)
**대상:** `tests/test_roles_envelopes.py`

**요약:** C-C6(코어에 런타임명·도구명 금지) 회귀 테스트가 이번 라운드에 새로 만든 코어 산출물 6개 중 3개만 검사한다. `core/workflows/implement/SKILL.md`·`core/workflows/review/SKILL.md`·`core/templates/compact-brief.md` 는 지금 깨끗하지만 이 규칙을 지키는 테스트가 저장소에 없어, 다음 편집에서 도구명이 들어가도 CI 가 잡지 못한다.

**증거:**

`tests/test_roles_envelopes.py:131-137`:
```python
targets = sorted((REPO / "core/roles").glob("*.yaml")) + \
    sorted((REPO / "core/schemas").glob("*envelope*.json"))
self.assertEqual(len(targets), 4, ...)
```
→ 검사 대상 4개 고정. `grep -rn "C-C6|중립" tests/*.py` → `test_roles_envelopes.py` 밖에 없다.
현재 상태는 통과: `grep -niE "claude|codex|orca|gpt|opus|sonnet|anthropic|openai" core/workflows/implement/SKILL.md core/workflows/review/SKILL.md core/templates/compact-brief.md` → exit 1(매치 0건). 즉 지금 고칠 것은 없고 회귀 가드만 없다.

**제안된 수정:** `TestVendorNeutral` 의 대상을 글롭으로 넓힌다 — `core/roles/*.yaml` + `core/schemas/*.json` + `core/workflows/*/SKILL.md` + `core/templates/**/*.md`. `core/workflows/plan/SKILL.md:4`(`provenance: [anthropics-skills-skill-format]`)와 `:9`·`core/principles/AGENTS.core.md:10` 의 자기 참조 문장, `core/policy/execution-guards.yaml` 의 enforcement 블록은 기존 예외이므로 예외 목록을 파일별로 명시하고 그 예외마다 근거 한 줄을 단다 — 예외를 늘리지 않는 것이 이 테스트의 목적이다.

## F31 [minor] (규율-위반)
**대상:** `core/roles/implementer.yaml:14-22 · core/roles/reviewer.yaml:12-19`

**요약:** 역할 계약 파일을 읽는 코드가 없다. capabilities·allowed_paths·forbidden 은 어디서도 강제·대조되지 않는 선언이고, implementer.yaml:22 의 K-66 주장을 검사하는 것이 없다.

**증거:**

$ grep -rn "core/roles" romeo/ bin/ adapters/ .harness/ core/ .github/
(출력 없음 — tests/test_roles_envelopes.py 만 이 파일들을 연다)

implementer.yaml:22 `note: 작업 계약의 allowed_paths 는 이 범위를 넘을 수 없다(K-66). 저장소 밖 경로는 허용하지 않는다.` — task-envelope.json:58-64 의 allowed_paths 를 이 범위와 대조하는 코드가 없고, core/schemas/task-envelope.json 자체도 romeo/ 아래 어디서도 로드되지 않는다:

$ grep -rn "task-envelope" romeo/ bin/
(출력 없음)

romeo/compile.py 도 core/roles 를 투영하지 않아 두 런타임 지침 파일에 역할 계약 본문이 들어가지 않는다. K-68 '파일·설정 존재만으로 완료라 하지 않는다'.

**제안된 수정:** 최소안은 대조 테스트 한 건이다 — tests/test_roles_envelopes.py 에 '작업 계약 표본의 allowed_paths 가 implementer.yaml 의 allowed_paths.must_include 를 포함하고 scope 를 벗어나지 않는다'를 단언하는 케이스를 넣는다. 그 다음 단계로 romeo/ 에 verify_task_envelope(env, role_contract) 를 만들어 작업 계약 생성 시점에 검사하고, 위반이면 BLOCKED_CAPABILITY 로 떨어뜨린다. 지금처럼 강제 수단이 없다면 두 yaml 상단 주석에 '이 파일은 아직 어떤 코드도 강제하지 않는다(M2 선언 단계)'를 명시해 미검증임을 드러낸다.
