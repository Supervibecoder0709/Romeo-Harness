---
id: feat-20260901-enforce-point-alignment-9dfq
type: spec
title: 요구하는 자리와 보는 자리를 같게 둔다 — 집행 지점 어휘·차단 충족 조건·절 로드 대조
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: done
approved_at: '2026-09-01T18:58:11+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-09-01T19:24:38+09:00'
parent: null
inputs: []
evidence: [evidence/run_9dfq01.yaml, evidence/run_9dfq02.yaml, evidence/run_9dfq03.yaml, evidence/run_9dfq04.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-01'
updated: '2026-09-01'
approval_history:
- {approved_at: '2026-09-01T17:58:17+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-01T18:31:03+09:00',
  reason: '1회차 검토자 findings 반영 — AC-3 에 mailto 명시, AC-8 을 이름 존재에서 상태 검사로, AC-9 에서 기계가 셀 수 없는 spike 판정을
    빼고 경계를 명시, 변경 범위에 AGENTS.md·CLAUDE.md·fixtures/shadow·tests/test_run_unit.py 추가, check-9 강화'}
- {approved_at: '2026-09-01T18:31:03+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-01T18:58:11+09:00',
  reason: 2회차 검토자 findings 반영 — Q-29 해소문이 mailto 를 통과시킨다고 적어 AC-3·코드와 반대였다(수정). check-9 을 취소선 존재 검사에서
    「해소문의 주장 ↔ 코드 동작」 대조로 바꿨다(TestClosureMatchesCode)}
---

# 요구하는 자리와 보는 자리를 같게 둔다 — 집행 지점 어휘·차단 충족 조건·절 로드 대조

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260901-enforce-point-alignment-9dfq --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 차단이 무엇을 언제 어느 문서로 보는지를 선언하게 하고, 라우터가 요구한 절을 아무도 읽지 않는 상태를 로드 시점에 막는다
- **왜 지금:** 바로 앞 단위(`feat-20260901-charter-discovery-block-a3xs`)가 "계산만 되던 차단을 집행한다" 로 닫혔는데,
  그 차단 4개가 **여전히 아무것도 막지 못한다.** 2026-09-01 실측: `inputs: ["ㅁㄴㅇㄹ"]` 로 승인이 통과하고,
  존재하지 않는 경로도 통과하며, 조사 단위는 조사 결과를 **먼저** 요구받아 조사를 시작할 창구가 없고,
  라우터가 필수라고 판정한 절이 `brief.md` 에 들어가면 승인·종료·CI **셋 다** 그것을 읽지 않는다.
  M3 시나리오 3 의 수용 기준이 이 상태로 서 있으므로 정비가 아니라 M3 본체 재작업이다.
- **기대 결과:** 차단이 **무엇을 · 언제 · 어느 문서로** 보는지를 스스로 선언하고, 선언과 집행이 어긋나면
  정책이 로드되지 않는다. 조사 단위는 조사 결과 없이 **승인은 되고 구현 위임에서 막힌다**. 링크가 가리키는 경로가
  실재할 때만 조사 결과로 센다. 라우터가 요구했는데 아무도 읽지 않는 절이 생길 수 없다.
  손으로 절차를 밟은 관통도 회차가 남아 반복 중단이 그 경로에서도 센다.
- **수용 기준:**
  - [x] AC-1 집행 지점에 `dispatch`(구현 위임 직전)가 생기고, 차단마다 **막는 사건 하나**와 **정본 입력 문서(`reads:`)** 를
        선언한다. 일괄 배치나 `reads` 누락은 정책 로드를 실패시킨다. 막는 사건은 하나지만 **보고는 종료에서도 남는다** —
        `close` 는 걸린 차단 전부를 계속 인쇄한다(a3xs AC-4).
  - [x] AC-2 `discovery-result` 가 `dispatch` 에서 걸린다 — 조사 결과 없이도 **승인은 되고**, 그 상태로 작업 계약을 만들면 막힌다.
  - [x] AC-3 `discovery-result` 는 `brief.md`(없으면 `charter.md`)의 `inputs:` 를 읽고 **경로가 실재할 때만** 충족한다 —
        없는 경로 · 경로가 아닌 문자열 · `mailto:` 는 막힌다. 확인할 수 없는 것은 `http(s)://` 하나뿐이고
        그때는 이유에 「확인하지 않는다」를 적는다.
  - [x] AC-4 `approval-gate` 가 `risk-plan-ready` 로 바뀌고 카탈로그가 "되돌리기 어려운 실행의 승인은 `guards` 소유" 를
        명시한다. 옛 id 는 정책표·코드·테스트·fixture 어디에도 남지 않는다.
  - [x] AC-5 미완료 검사가 **문서 패키지 전체**(brief·charter 포함)를 `close` 와 `dispatch` 양쪽에서 본다 —
        brief 의 「첫 마일스톤(spike)」가 빈 채로는 계약이 만들어지지 않는다.
  - [x] AC-6 절마다 **누가 집행하는지**(`enforcement:`)를 선언한다. 선언이 없거나 그 집행이 절의 문서를 실제로
        읽지 않으면 **정책이 로드되지 않는다.**
  - [x] AC-7 손으로 위임 절차를 밟은 관통도 `attempts.yaml` 에 회차가 남는다 — 반복 중단이 그 경로에서도 센다(Q-27).
  - [x] AC-8 `AGENTS.core.md` §11 신설·§10 개정, `decision-register` D-78·D-79(`accepted`),
        `open-questions` Q-27~Q-31 **닫힘 표시까지**. 이름이 있는지가 아니라 **그 상태인지**를 검사한다.
  - [x] AC-9 반례가 **빈 값이 아니라 그럴듯한 거짓 값**으로 고정된다 — 없는 경로 · 경로가 아닌 문자열 ·
        `mailto:` 링크 · `reads` 없는 차단 · `enforcement` 없는 절 · 절의 문서를 읽지 않는 차단 선언.
        빈 값만 막는 반례는 지금 상태와 구별되지 않는다. **첫 마일스톤이 spike 인가는 여기서 세지 않는다** —
        의미 판단이라 기계가 판별할 수 없다(1회차 검토자가 이 어긋남을 잡았다). 기계는 그 칸이 채워졌는지까지 보고,
        spike 여부는 검토자가 본다 — 그 경계를 테스트가 명시적으로 고정한다.
  - [x] AC-10 기존 테스트가 그대로 통과하고, 시나리오 3 런북 9단계가 새 집행 지점에 맞게 다시 쓰인다.
- **위험과 되돌리기:** `dispatch` 훅을 계약 생성에 걸므로 잘못 걸면 **어떤 단위도 위임할 수 없게 된다 — 이 단위 자신 포함.**
  그래서 구현 단위 1 이 훅 자리를 세 경로에서 실측한 뒤에야 나머지가 붙는다. 둘째 위험은 조용한 약화다 —
  차단이 헐거워져도 아무 오류가 나지 않으므로 AC-9 가 그럴듯한 거짓 값 반례를 요구한다. 개명은 fixture 5건의 기대값을
  바꾸지만 **과거 작업 계약 중 차단 id 를 담은 것은 0건**이라(실측) 앵커는 깨지지 않는다.
  전부 저장소 안 파일이고 외부 상태를 바꾸지 않는다 — 되돌리기는 `git revert <통합 커밋>` 이다.
- **결정 필요:** 없음


## 변경 범위

- 바뀌는 파일·모듈:
  - `romeo/blocks.py`
  - `romeo/policy.py`
  - `romeo/envelope.py`
  - `romeo/close.py`
  - `romeo/run_unit.py`
  - `core/policy/packages.yaml`
  - `core/principles/AGENTS.core.md`
  - `tests/test_enforce_points.py`
  - `tests/test_blocks_enforcement.py`
  - `tests/test_policy.py`
  - `tests/test_scenario_3.py`
  - `fixtures/requests/fx-vps-redeploy.yaml`
  - `fixtures/requests/fx-account-migration-continue.yaml`
  - `fixtures/requests/fx-pr-review-remaining-fixes.yaml`
  - `fixtures/requests/fx-resolve-review-issues-parallel.yaml`
  - `fixtures/requests/fx-s07-coupang-migration-initiative.yaml`
  - `scenarios/3-discovery-block.md`
  - `docs/decisions/decision-register.md`
  - `docs/planning/open-questions.md`
  - `AGENTS.md`
  - `CLAUDE.md`
  - `fixtures/shadow/2026-08-27-cards.md`
  - `tests/test_run_unit.py`
- 영향을 받는 부분: `romeo route` 의 출력(차단 id)이 바뀌므로 분류 카드의 표기가 달라진다. `AGENTS.md`·`CLAUDE.md` 는 `romeo compile` 이 코어에서 다시 만든다 — 손으로 고치지 않는다. `docs/work/` 의 이미 `done` 인 단위는 소급 대상이 아니다(차단은 소급하지 않는다 — a3xs AC-8).
- 바꾸지 않는 것(비범위): 새 `execute` 집행 지점을 만들지 않는다 — `core/policy/execution-guards.yaml` 의 `guards` 가 이미 실행 시점 승인을 소유하고 승인 기록을 원시 로그로 봉인한다(`close` 의 `GUARD_APPROVED`). 같은 일을 두 이름으로 하지 않는다. `docs/source-context/` 와 옛 리뷰 라운드 문서의 `approval-gate` 표기는 그때의 기록이므로 건드리지 않는다. 이미 `done` 인 단위의 문서·증거를 다시 쓰지 않는다. Q-19(`run-unit --spawn` 의 run id 인계)는 이 단위 밖이다.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | `dispatch` 훅 자리를 실측으로 확정한다 — 계약 생성이 정말 모든 위임 경로가 지나는 첫 동작인가 | 코드 변경 없음. `envelope build` 를 세 경로(`run-unit start` · 손 §3.4 · 테스트)에서 돌려 관측을 evidence 에 남긴다 | 소비: 없음 → 생산: 훅 자리 판정(`romeo/envelope.py` 의 함수명) | 세 경로 모두 그 함수를 지나는 것이 로그에 남는다. 지나지 않는 경로가 있으면 그 경로도 훅에 넣고 표에 한 행을 더한다 | 되돌릴 것 없음(관측만) |
| 2 | 집행 지점 어휘를 확장하고 차단이 스스로 선언하게 한다 | `romeo/blocks.py` 의 `ENFORCE_POINTS`·`catalog_defects()`, `core/policy/packages.yaml` 의 `blocks:` | 소비: 1의 훅 자리 → 생산: `ENFORCE_POINTS`(3원소) · `blocks.<id>.reads` 키 | check-1 · check-2 | `git revert` |
| 3 | `discovery-result` 를 `dispatch` 로 옮기고 Brief/Charter 의 실재 경로만 센다 | `romeo/blocks.py` 의 `_discovery_result`, 카탈로그의 해당 항목 | 소비: 2의 `reads` 키 → 생산: `_discovery_result(unit_dir, fm, body)` 가 unit_dir 에서 brief/charter 를 읽는다 | check-3 | `git revert` |
| 4 | `approval-gate` 를 `risk-plan-ready` 로 개명하고 실행 승인 소유를 명시한다 | 카탈로그 · `BLOCK_CHECKS` · fixture 5건 · 테스트 | 소비: 2의 카탈로그 형식 → 생산: 차단 id `risk-plan-ready` | check-4 · check-5 | `git revert` |
| 5 | 미완료 검사를 문서 패키지 전체로 넓히고 `dispatch` 에서도 본다 | `romeo/close.py` · `romeo/envelope.py` | 소비: 1의 훅 자리 → 생산: 패키지 문서 목록을 읽는 헬퍼 | check-6 | `git revert` |
| 6 | 절마다 집행 선언을 요구하고 로드 시점에 대조한다 | `core/policy/packages.yaml` 의 `sections:` · `romeo/policy.py` | 소비: 2의 `reads` 키 · 5의 패키지 헬퍼 → 생산: `sections.<id>.enforcement` 키 | check-7 | `git revert` |
| 7 | 손 관통도 회차가 남게 한다 (Q-27) | `romeo/envelope.py` · `romeo/run_unit.py` 의 `record_result` | 소비: 1의 훅 자리 → 생산: 계약 생성이 남기는 기동 기록 | check-8 | `git revert` |
| 8 | 옛 집행 지점을 단언하는 기존 테스트 12건을 새 계약으로 다시 쓴다 | `tests/test_blocks_enforcement.py` 10건(`TestApproveRejectsUnsatisfied` 1 · `TestBlockCatalog` 2 · `TestCatalogMappingMismatch` 1 · `TestCloseReportsBlockSatisfied` 3 · `TestDiscoveryResultNeedsInputs` 2 · `TestNoRetroactiveEffect` 1) · `tests/test_scenario_3.py` 2건(`test_step3` · `test_step8`) | 소비: 2~7의 새 계약 → 생산: 갱신된 회귀 계약 | check-11 · check-12 | `git revert` |
| 9 | 규칙·결정·열린 질문·시나리오 런북을 갱신한다 | `core/principles/AGENTS.core.md` · `docs/decisions/decision-register.md` · `docs/planning/open-questions.md` · `scenarios/3-discovery-block.md` | 소비: 2~8의 결과 → 생산: §11 본문 · D-78 · D-79 | check-9 · check-11 | `git revert` |

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

**check-1~check-11 은 지금 상태에서 실패하고 가상 완료 상태에서 통과한다. check-12 는 방향이 반대인 회귀 가드다.**
승인 전에 두 방향 모두 실제로 돌렸고 판정표·발견 2건·다시 써야 할 테스트 12건의 이름은 같은 폴더의 `preflight.md` 에 있다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -c \"from romeo.blocks import ENFORCE_POINTS as P; assert 'dispatch' in P, P\""
  - id: check-2
    command: "python3 -c \"import yaml; b=yaml.safe_load(open('core/policy/packages.yaml'))['blocks']; [ (_ for _ in ()).throw(AssertionError(k)) for k,v in b.items() if len(v.get('enforced_at') or [])!=1 or not v.get('reads') ]\""
  - id: check-3
    command: "python3 -m unittest tests.test_enforce_points.TestDispatchPoint tests.test_enforce_points.TestDiscoveryResultReadsRealPath"
  - id: check-4
    command: "! grep -rn 'approval-gate' core/ romeo/ tests/ fixtures/"
  - id: check-5
    command: "python3 -c \"import yaml; from romeo.blocks import BLOCK_CHECKS; b=yaml.safe_load(open('core/policy/packages.yaml'))['blocks']; assert 'risk-plan-ready' in b and 'risk-plan-ready' in BLOCK_CHECKS; assert 'guards' in (b['risk-plan-ready'].get('note') or '')\""
  - id: check-6
    command: "python3 -m unittest tests.test_enforce_points.TestOpenLoopCoversPackage"
  - id: check-7
    command: "python3 -c \"import yaml; s=yaml.safe_load(open('core/policy/packages.yaml'))['sections']; [ (_ for _ in ()).throw(AssertionError(k)) for k,v in s.items() if not v.get('enforcement') ]\" && python3 -m unittest tests.test_enforce_points.TestSectionEnforcementReconciliation"
  - id: check-8
    command: "python3 -m unittest tests.test_enforce_points.TestHandRunRecordsAttempt"
  - id: check-9
    command: "python3 -c \"import pathlib; a=pathlib.Path('core/principles/AGENTS.core.md').read_text(); assert '## 11. 요구하는 자리와 보는 자리를 같게 둔다' in a; assert '회차는 세는 자리가 아니라 나는 자리에서 만든다' in a; d=[l for l in pathlib.Path('docs/decisions/decision-register.md').read_text().split(chr(10)) if l.startswith(('| D-78 |','| D-79 |'))]; assert len(d)==2 and all('| accepted |' in l for l in d), d\" && python3 -m unittest tests.test_enforce_points.TestClosureMatchesCode"
  - id: check-10
    command: "python3 -c \"import unittest; n=unittest.defaultTestLoader.loadTestsFromName('tests.test_enforce_points').countTestCases(); assert n>=20, n\" && python3 -c \"import pathlib; t=pathlib.Path('tests/test_enforce_points.py').read_text(); [ (_ for _ in ()).throw(AssertionError(p)) for p in ('ㅁㄴㅇㄹ','docs/research/없는파일.md','spike 없이') if p not in t ]\""
  - id: check-11
    command: "grep -q 'enforced_at' scenarios/3-discovery-block.md && grep -q 'dispatch' tests/test_scenario_3.py && python3 -m unittest discover -s tests"
  - id: check-12
    command: "python3 -m unittest tests.test_blocks_enforcement.TestCloseReportsBlockSatisfied"
```


## 증거

close PASS · 2026-09-01T19:24:38+09:00 · HEAD a7b35e5b0ae6 · 검사 기록 run_9dfq04

- [evidence/run_9dfq01.yaml](evidence/run_9dfq01.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_9dfq02.yaml](evidence/run_9dfq02.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_9dfq03.yaml](evidence/run_9dfq03.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_9dfq04.yaml](evidence/run_9dfq04.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
