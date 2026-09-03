---
id: feat-20260903-runbook-handle-attempts-drift-w7tm
type: spec
title: 런타임이 소유한 값을 확인 기준으로 쓰지 않는다 — 핸들 확인·attempts 정본
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: active
approved_at: '2026-09-04T00:33:17+09:00'
approved_by: justjulliette0709
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-03'
updated: '2026-09-04'
approval_history:
- {approved_at: '2026-09-04T00:06:33+09:00', approved_by: justjulliette0709, superseded_at: '2026-09-04T00:33:17+09:00',
  reason: AC-4 가 AC-3 과 같은 상태를 반대로 판정했다 — 1회차 검토자 FAIL 의 원인. AC-4 의 정상 모양을 「판정은 양쪽에 다 있고 워크트리에만 다음 회차
    started 가 붙은 상태」로 고쳤다}
---

# 런타임이 소유한 값을 확인 기준으로 쓰지 않는다 — 핸들 확인·attempts 정본

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260903-runbook-handle-attempts-drift-w7tm --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 직전 관통(정비 5회차)이 §12 로 남긴 결함 2건을 닫는다. ① **위임 절차가 런타임이 소유한 값을 확인 기준으로 쓰던 것**을 고친다 — RUNBOOK §3.7 (1) 은 터미널 핸들이 맞는지를 「같은 `--title`」로 확인하라고 하는데, codex TUI 가 기동 직후 제목을 자기 것으로 덮어써서(2026-09-03 실측) 그 확인이 실패하고, 실패했을 때 가라는 (c) `terminal list` 의 「같은 제목의 행」도 없다 — 문서대로 밟으면 막다른 길이다. 확인 기준을 **핸들 + 워크트리 id** 로 바꾼다(그것이 실제로 성립한 확인이다). ② **관통 결과를 통합할 때 회차 판정이 조용히 사라지던 것**을 막는다 — 워커 워크트리 안의 `attempts.yaml` 에는 그 회차가 `started` 로만 남고, 판정(`pass`/`fail`)은 위임한 쪽 체크아웃에만 쓰인다. 워크트리 것을 그대로 통합하면 판정이 `started` 로 덮이고, 지금 어느 검사도 그것을 보지 않는다(`run-unit check` 는 `started` 를 대조하지 않는다 — Q-39 가 그렇게 정했다). 통합 직전에 **판정 손실을 실제로 막는 명령**을 만들고, 위임 절차에 그것을 밟는 자리를 둔다.
- **왜 지금:** 다음 관통은 charter 를 쓰는 실제 T2 관통이고, 두 결함은 **그 관통이 반드시 지나는 위임 경로 위**에 있다(§3.7 검토자 기동 · 통합). §10 동결 규칙상 관통이 시작되면 하네스를 고칠 수 없으므로, 이 상태로 들어가면 §3.7 에서 막다른 길을 손으로 우회하고 통합에서 판정을 손으로 복사하게 된다 — 그렇게 나온 판정은 무엇이 만든 것인지 말하기 어렵다. 정비의 자리는 관통과 관통 사이다.
- **기대 결과:** 코디네이터가 RUNBOOK §3.7 을 **글자 그대로 밟아도** 핸들 확인이 성립한다 — 제목이 무엇으로 바뀌어 있든 상관없다. 그리고 워커 워크트리의 회차 기록이 위임 쪽 판정을 하나라도 잃은 채로 통합되려 하면, 통합 전에 종료 코드가 0 이 아닌 명령이 그것을 막는다. 판정을 잃지 않은 정상 통합(워크트리에 `started` 만 더 있는 경우)은 그대로 통과한다.
- **수용 기준:**
  - [ ] AC-1 RUNBOOK §3.7 (1) 의 핸들 확인 절차 (b)·(c) 가 **제목을 확인 기준으로 쓰지 않는다.** (b) 는 `terminal show` 가 돌려준 워크트리 id 가 방금 지정한 워크트리와 같은지를 보고, (c) 는 `terminal list --worktree` 결과에서 **핸들** 로 행을 찾는다.
  - [ ] AC-2 그 자리에 **왜 제목이 기준이 될 수 없는지**가 2026-09-03 실측(codex TUI 가 `review-<id>-<run>` 제목을 `⠹ impl-<id>…` 로, 구현자 터미널 제목을 `✳ <id> 구현` 으로 덮어썼다)과 함께 적혀 있다. 근거 없이 기준만 바꾸면 다음 사람이 제목으로 되돌린다.
  - [ ] AC-3 워크트리 사본의 `attempts.yaml` 이 이 체크아웃의 판정(`pass`/`fail`)을 **하나라도 잃은** 상태에서, `bin/romeo run-unit merge-check --unit <id> --worktree <경로>` 가 **종료 코드 0 이 아니고** 어느 회차의 어느 판정이 사라지는지를 인쇄한다.
  - [ ] AC-4 워크트리 사본이 **이 체크아웃의 판정을 전부 담은 채** `started` 가 하나 더 있는 상태 — 판정 난 회차는 양쪽에 같이 있고 워크트리에만 다음 회차의 `started` 가 붙은 모양 — 에서 같은 명령이 **종료 코드 0** 이다. 정상 통합을 막는 검사는 통합을 막을 뿐 아무것도 지키지 못한다. (1회차 검토자 FAIL 의 원인이 이 항목이었다 — 옛 문장은 「이 체크아웃에서는 판정까지, 워크트리에서는 `started` 까지」 를 정상이라 불렀는데 그것은 AC-3 이 막으라고 한 **판정 손실 그 자체**였다. 두 항목이 같은 상태를 반대로 판정했고, 무엇이 정상인지를 정하는 것은 Q-48 이 막으려던 사고다: 워크트리 것을 통합해 판정이 `started` 로 덮이는 것.)
  - [ ] AC-5 RUNBOOK 의 위임 절차에 **`attempts.yaml` 의 정본이 위임한 쪽**이라는 것과 통합 직전에 `run-unit merge-check` 를 밟는 자리가 있다. 요구를 적는 자리와 그것을 보는 자리를 같은 커밋에 둔다(§11).
  - [ ] AC-6 `docs/planning/open-questions.md` 의 Q-47·Q-48 이 닫히고, 무엇으로 닫혔는지가 적혀 있다.
- **위험과 되돌리기:** 문서와 하네스 코드만 바꾼다. 외부 상태·운영 데이터를 건드리지 않고 되돌리기는 `git revert <통합 커밋>` 이다. 실질적 위험은 하나 — AC-3 의 새 명령이 **정상 통합까지 막는 것**(거짓 양성)이다. 그러면 다음 관통의 통합이 서지 않는다. AC-4 가 그것을 겨누고, 검증 계획의 check-1(테스트)이 그 상태에서 종료 코드 0 을 실측한다. 그래도 막히면 그 명령을 밟는 RUNBOOK 문단만 되돌리면 통합은 즉시 가능하다(명령은 통합 자체를 수행하지 않고 판정만 낸다).
- **결정 필요:** 없음

## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `adapters/orca/RUNBOOK.md` (§3.7 의 핸들 확인 절차 · 통합 직전의 정본 규칙) · `romeo/run_unit.py` (워크트리 사본과 이 체크아웃의 판정을 대조하는 함수) · `romeo/cli.py` (그 함수를 부르는 명령 배선) · `tests/test_attempts_integration_check.py` (새 테스트) · `docs/planning/open-questions.md` (Q-47·Q-48 닫기) · `docs/work/feat-20260903-runbook-handle-attempts-drift-w7tm/` (이 단위의 산출물)
- 영향을 받는 부분: 다음 관통의 위임 절차 전체 — §3.7 을 밟는 코디네이터와, 통합 직전에 새 명령을 밟는 사람. `run-unit check`(§3.1 확인 4)의 동작은 바꾸지 않는다.
- 바꾸지 않는 것(비범위): `compare_attempts` 의 판정·재검토만 대조하는 규칙(Q-39 의 결정) · `record_start` 가 회차를 만드는 자리(§10 「나는 자리에서 만든다」) · `envelope build` 가 워크트리 안에서 회차를 남기는 동작 · §3.7 의 기동 형태(TUI vs 비대화형) 결정 · 통합 자체를 자동화하는 것.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 판정 손실을 보는 대조 함수를 만든다 (AC-3·AC-4) | `romeo/run_unit.py` 에 워크트리 사본의 `attempts.yaml` 과 이 체크아웃의 것을 **판정으로만** 대조하는 함수를 더한다. 이 체크아웃에 있는 판정 중 워크트리 사본에 없는 것이 하나라도 있으면 차이로 낸다. 워크트리에만 있는 `started` 는 차이가 아니다 — 관통에서 언제나 나는 모양이다. `compare_attempts` 는 손대지 않는다 | 소비: 없음 → 생산: 대조 함수 1개(판정 차이 목록·워크트리 경로·이 체크아웃의 판정 수를 돌려준다) | `python3 -m unittest tests.test_attempts_integration_check -v` 가 판정 손실 케이스에서 차이 ≥ 1, `started` 만 더 있는 케이스에서 차이 0 | `git revert` 또는 그 함수와 테스트를 지운다 |
| 2 | 그 함수를 명령으로 낸다 (AC-3·AC-4) | `romeo/cli.py` 에 1번 함수를 부르는 명령을 배선한다. 워크트리 경로를 인자로 받고, 차이가 있으면 **종료 코드 0 이 아니고** 어느 회차의 어느 판정이 사라지는지를 인쇄한다. 차이가 없으면 종료 코드 0 | 소비: 1번의 대조 함수 → 생산: `bin/romeo run-unit merge-check --unit <id> --worktree <워크트리 절대경로>` (기존 `run-unit` 의 action 목록에 `merge-check` 를 더한다 — `start`·`record`·`review`·`check` 옆이다) | 판정을 지운 임시 워크트리 사본에 대해 종료 코드 ≠ 0, `started` 만 더 있는 사본에 대해 종료 코드 0 — 둘 다 실행으로 본다 | `git revert` 또는 그 배선을 지운다 |
| 3 | §3.7 의 확인 기준을 제목에서 걷어낸다 (AC-1·AC-2) | `adapters/orca/RUNBOOK.md` §3.7 (1) 의 확인 절차 (b)·(c) 를 고친다. (b) 는 `terminal show` 의 워크트리 id 를 방금 지정한 워크트리와 대조하고, (c) 는 `terminal list --worktree` 결과에서 핸들로 행을 찾는다. 왜 제목이 기준이 될 수 없는지를 2026-09-03 실측과 함께 그 자리에 적는다 | 소비: 없음 → 생산: 없음 | `! grep -n '같은 제목' adapters/orca/RUNBOOK.md` 가 종료 코드 0 이고, `terminal show` 문단이 워크트리 id 를 대조한다 | `git revert` |
| 4 | 통합 직전의 정본 규칙과 명령을 절차에 둔다 (AC-5) | `adapters/orca/RUNBOOK.md` 의 위임 절차에 **`attempts.yaml` 의 정본은 위임한 쪽**이라는 것과, 통합 직전에 2번 명령을 밟는 자리를 더한다. 차이가 나면 무엇을 하는지(위임 쪽 판정을 정본으로 남긴다)까지 적는다 | 소비: 2번의 명령 이름 → 생산: 없음 | RUNBOOK 에 2번 명령의 이름이 나타나고, 그 문단이 정본을 명시한다 | `git revert` |
| 5 | 열린 관측을 닫는다 (AC-6) | `docs/planning/open-questions.md` 의 Q-47·Q-48 을 닫고 무엇으로 닫혔는지 적는다 | 소비: 1~4번의 결과 → 생산: 없음 | Q-47·Q-48 행이 닫힘으로 표시된다 | `git revert` |

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

**판별 검사와 회귀 방지 검사를 구분해 적는다**(§11). 아래 check-1~check-4 는 **판별 검사** — 이 단위가 없으면 실패해야 하고,
승인 전에 기존 상태(실패)와 가상 완료 상태(성공) 양쪽에서 실측한다. check-5~check-9 는 **회귀 방지 검사** — 양쪽에서 통과하는 것이
그 검사의 정의이므로 양쪽 실측의 대상이 아니다.

**문서 검사 3건(check-2·3·4)의 한계를 적어 둔다.** 이 셋은 문서에 그 문자열이 있는지/없는지만 본다 — 「그 문단이 실제로 워크트리 id 를 대조하는 절차인가」는 기계가 판정할 수 없다. 그 판정은 **검토자가 읽어서** AC-1·AC-2·AC-5 로 낸다. 이 셋을 통과했다는 것은 「제목 기준이 남아 있지 않고, 워크트리 id 와 새 명령이 그 문서에 등장한다」까지다. 적어 두지 않으면 다음 사람이 이 검사를 절차 정합성의 증거로 읽는다(§11).

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_attempts_integration_check -v"
  - id: check-2
    command: "! grep -q '같은 제목' adapters/orca/RUNBOOK.md"
  - id: check-3
    command: "grep -q 'result.terminal.worktreeId' adapters/orca/RUNBOOK.md"
  - id: check-4
    command: "grep -q 'run-unit merge-check' adapters/orca/RUNBOOK.md"
  - id: check-5
    command: "python3 -m unittest discover -s tests"
  - id: check-6
    command: "bin/romeo validate"
  - id: check-7
    command: "bin/romeo compile --check"
  - id: check-8
    command: "bin/romeo doctor --strict --scope repository"
  - id: check-9
    command: "bin/romeo fixtures check"
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
