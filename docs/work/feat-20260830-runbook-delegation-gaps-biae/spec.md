---
id: feat-20260830-runbook-delegation-gaps-biae
type: spec
title: RUNBOOK 위임 절차 결함 6건 정비 — 관통이 드러낸 관측을 절차로 만든다
unit: T1
mode: delivery
intent: write
facets: [docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: done
approved_at: '2026-08-30T23:24:44+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-08-30T23:45:52+09:00'
parent: null
inputs: []
evidence: [evidence/run_583f325f5c94.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-08-30'
updated: '2026-08-30'
---

# RUNBOOK 위임 절차 결함 6건 정비 — 관통이 드러낸 관측을 절차로 만든다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260830-runbook-delegation-gaps-biae --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 지난 두 관통이 드러낸 **위임 절차 결함 6건**을 `adapters/orca/RUNBOOK.md` 에 반영한다. 바뀌는 파일은 그 문서 하나다 — 코드·스키마·정책표를 건드리지 않는다. Ⓐ 워커가 낸 **질문에 답하는 경로**를 적는다(지금은 받는 방법만 있고 답하는 방법이 없다). Ⓑ **관통 도중 재승인했을 때** 이미 만들어 둔 위임 작업의 계약 지문을 어떻게 맞추는지 적는다. Ⓒ `tui-idle` 은 **완료 신호가 아니다**를 적고 완료를 읽는 자리를 알려준다. ④ 검토자 기동 실패를 가르는 실제 변수가 '대화형이냐'가 아니라 **'프롬프트를 명령줄에 넣었느냐'** 임을 표로 다시 그린다. ⑥ 검토자 실행 명령에 `< /dev/null` 을 붙여 입력을 기다리다 멈추지 않게 한다. ⑦ **논리 역할 이름은 모델 id 가 아니다**를 적는다.
- **왜 지금:** 여섯 건 모두 **다음 위임에서 그대로 다시 걸리는 것**이고, 바로 다음 작업이 `feat-20260830-harness-defects-w3qu` 의 5회차 관통이다. ⒶⒷⒸ 는 직전 관통에서 실제로 걸렸다 — Ⓐ 는 답이 도달했는데도 구현자가 900초 무응답으로 판단해 escalation 을 냈고, Ⓑ 는 검토자가 낡은 해시와 새 해시를 둘 다 받았으며(이번엔 운으로 넘어갔다), Ⓒ 는 완료 판정에 오탐을 냈다. 코어 규칙 §10 은 관통 중 하네스 변경을 금지하므로, 고칠 수 있는 구간은 관통과 관통 **사이**인 지금뿐이다.
- **기대 결과:** 다음 관통을 도는 사람이 이 여섯 가지를 문서에서 찾을 수 있다 — 기억이나 지난 세션의 대화에 의존하지 않는다. 그리고 `w3qu` 의 AC-5 가 요구한 관측이 ④ 의 새 서술 **안으로 흡수**되어, §3.7 에 원인을 서로 다르게 지목하는 두 문단이 남지 않는다.
- **수용 기준:**
  - [x] AC-1 (Ⓐ) RUNBOOK 에 워커의 질문에 **답하는** 명령형이 있다 — `--to run:<run-id> --thread-id` 형태를 쓰고, `--to dispatch:<id>` 로 보낸 답이 ask 스레드를 풀지 못했다는 관측이 함께 적혀 있다.
  - [x] AC-2 (Ⓑ) `### 3.4.1` 소절이 신설되어, 관통 도중 재승인하면 무엇이 어긋나는지(검토자가 **낡은 해시**를 받는다)와 그때 밟을 절차가 적혀 있다.
  - [x] AC-3 (Ⓒ) `tui-idle` 이 **완료 신호가 아니다**라는 것과, 완료를 실제로 읽은 자리(`task_complete.last_agent_message`)가 적혀 있다.
  - [x] AC-4 (④) §3.7 의 실측 표가 **`프롬프트가 argv 에 있는가`** 를 축으로 다시 그려져 있고, 옛 표의 '대화형 여부' 축(`에 넣은 것 |` 헤더)은 남아 있지 않다.
  - [x] AC-5 (이관분) 그 새 서술 안에 `tui-idle` 을 **기다린 뒤에 채택해도** `agent_prompt_stalled` 로 실패했다는 관측이 보존되어 있다 — `w3qu` 의 AC-5 가 요구한 것이 이 단위에서 충족된다.
  - [x] AC-6 (⑥) §4 의 검토자 실행 명령 블록 안에 `< /dev/null` 이 있다.
  - [x] AC-7 (⑦) **논리 역할 이름**이 **모델 id 가 아니다**라는 것과, 실제 id 를 아는 방법이 적혀 있다.
  - [x] AC-8 기존 검사가 회귀하지 않는다 — `python3 -m unittest discover -s tests` · `bin/romeo validate` · `compile --check` · `doctor` · `fixtures parity --report` 가 모두 종료 코드 0.
- **위험과 되돌리기:** 바뀌는 것은 문서 한 개뿐이고 실행되는 코드가 아니다. 잘못 써도 명령이 깨지지 않고 **다음 사람이 잘못된 절차를 따르는** 형태로만 해를 끼친다 — 그래서 AC-4 가 옛 서술의 **제거**까지 요구한다(두 서술이 공존하면 어느 쪽이 맞는지 알 수 없다). 되돌리기는 `git revert <커밋>` 한 번이고, 저장소 밖 상태를 바꾸지 않는다. 워크트리에서 작업하므로 통합 전에는 그 브랜치가 그대로 남는다. **되돌리면 안 되는 부작용은 없다.**
- **결정 필요:** 없음 — 2026-08-30 확정. (a) `w3qu` 의 AC-5 를 이 단위로 이관한다. (b) 이 단위를 `w3qu` 5회차보다 **먼저** 돌린다.


## 변경 범위

- 바뀌는 파일·모듈: `adapters/orca/RUNBOOK.md` · `docs/work/feat-20260830-runbook-delegation-gaps-biae/`
- 영향을 받는 부분: 다음 위임을 수행하는 사람·런타임이 읽는 절차. 실행되는 코드는 없다 — `romeo compile` 은 `core/principles/` 와 `adapters/{claude,codex}/` 를 읽고 `adapters/orca/RUNBOOK.md` 는 읽지 않으므로 컴파일 산출물도 바뀌지 않는다(AC-8 의 `compile --check` 가 그것을 확인한다).
- 바꾸지 않는 것(비범위): `romeo/` 아래 코드 전부 · 스키마(`core/schemas/`) · 코어 규칙(`core/principles/`) · 정책표(`core/policy/`) · 권한 상한(`.harness/bindings.yaml`·`.claude/settings.json`) · `fixtures/` · `docs/work/feat-20260830-harness-defects-w3qu/`(그 단위의 재승인은 이 단위가 close 된 **뒤** 별도로 한다) · `docs/planning/progress.md`(통합 뒤 별도로 갱신한다)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

각 행의 **확인 방법** 열에 적힌 문자열은 검증 계획의 `grep` 이 문자 그대로 찾는 값이다. 그 문자열을 그대로 쓴다 —
바꿔 쓰면 검사가 실패한다. 문장 전체를 지정하지는 않으므로 앞뒤 서술은 구현자가 쓴다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | Ⓐ 워커의 질문에 답하는 경로가 문서에 있다 | §3.5.2 뒤(또는 §3.6 안)에 「워커가 낸 질문에 답한다」 문단을 새로 쓴다. 실효 경로는 `orca orchestration send --to run:<run-id> --thread-id <질문 msg id>` 이고, `--to dispatch:<id>` 로 보낸 답은 ask 스레드 타임아웃을 풀지 못했으며 `check --run --peek` 수신함에도 보이지 않았다는 관측을 함께 적는다. 표본 1건이므로 규칙으로 단정하지 않고 관측으로 적는다 | 소비: 없음 → 생산: RUNBOOK 문단 1개 | `--to run:<run-id> --thread-id` 와 `ask 스레드` 두 문자열이 문서에 있다 | `git revert` |
| 2 | Ⓑ 관통 도중 재승인했을 때 밟을 절차가 문서에 있다 | §3.4 바로 뒤에 `### 3.4.1` 소절을 신설한다. 담을 것 — (a) 재승인하면 `envelope build` 가 새 계약을 내므로 §3.4 가 이미 넘긴 `--spec` 의 지문이 낡는다, (b) 직전 관통에서 검토자가 **낡은 해시**와 새 해시를 둘 다 받았다는 관측, (c) 밟을 절차. **(c) 는 구현자가 `orca orchestration task-update --help` 로 `--spec` 갱신이 가능한지 실측해 정한다** — 가능하면 그 명령을, 불가능하면 「Run 을 새로 만든다」를 정본으로 적고 어느 쪽인지 실측 근거를 함께 남긴다 | 소비: 없음 → 생산: RUNBOOK `### 3.4.1` 소절 | `^### 3\.4\.1 ` 로 시작하는 줄이 있고 `낡은 해시` 문자열이 문서에 있다 | `git revert` |
| 3 | Ⓒ `tui-idle` 을 완료 신호로 쓰면 안 된다는 것이 문서에 있다 | §3.7 의 `terminal wait --for tui-idle` 문단(현재 481행 부근)에 이어, 그 신호가 **완료 신호가 아니다**라는 것을 적는다 — 작업 시작 직후에도 `satisfied: true` 가 나왔다. 채택 전 대기에 쓰면 주입이 경쟁하고 완료 판정에 쓰면 오탐이 난다. 완료를 실제로 읽은 자리는 codex 세션 로그(`~/.codex/sessions/<날짜>/rollout-*.jsonl` 의 `task_complete.last_agent_message`)였다는 것을 함께 적는다 | 소비: 없음 → 생산: RUNBOOK 문단 1개 | `완료 신호가 아니다` 와 `task_complete.last_agent_message` 두 문자열이 문서에 있다 | `git revert` |
| 4 | ④ §3.7 실측 표의 축이 실제 변수와 맞는다 | §3.7 의 실측 표(현재 405~408행)를 **`프롬프트가 argv 에 있는가`** 를 축으로 다시 그린다. 옛 두 행이 관측한 것은 유지하되(비대화형 `codex exec …` 실패 · TUI `codex -s read-only` 성공), 새 관측 한 행을 더한다 — **TUI 로 띄워도 프롬프트를 `--command` 의 argv 에 넣으면 같은 실패가 났다.** 옛 표의 헤더(`에 넣은 것 |` 를 포함하는 줄)는 남기지 않는다. 바로 아래 410~414행의 설명("프롬프트를 argv 로 이미 받고 입력을 더 받지 않으므로 주입이 갈 곳이 없다")과 표가 같은 원인을 가리키게 만든다 | 소비: 없음 → 생산: RUNBOOK §3.7 의 표 | `프롬프트가 argv 에 있는가` 가 문서에 있고, `에 넣은 것 \|` 는 문서에 **없다** | `git revert` |
| 5 | AC-5 이관분 — 늦은 채택 관측이 새 서술 안에 보존된다 | 4행이 만든 새 서술 안에, `tui-idle` 을 **기다린 뒤에 채택해도** `agent_prompt_stalled` 로 실패했다는 관측을 넣는다. 원본은 브랜치 `impl-feat-20260830-harness-defects-w3qu` 의 커밋 `a1f543a` 가 RUNBOOK 483행 뒤에 넣은 10줄이다 — 그 문단은 원인을 '채택 시점' 으로 지목하는데, 이번 서술은 원인을 '프롬프트 위치' 로 바꾸고 '기다려도 실패했다' 는 **관측만** 가져온다. 두 실패가 같은 증상(`agent_prompt_stalled`)을 낸다는 것도 유지한다 | 소비: 4행의 새 표·서술 → 생산: 그 서술 안의 관측 문단 | `기다린 뒤에 채택해도` 와 `agent_prompt_stalled` 두 문자열이 문서에 있다 | `git revert` |
| 6 | ⑥ 검토자 실행 명령이 stdin 을 기다리지 않는다 | §4 의 `codex exec -s read-only -C …` 명령 블록(현재 770행 부근) 마지막 줄에 `< /dev/null` 을 붙이고, argv 로 프롬프트를 받고도 stdin 을 기다려 멈춘 관측을 한 줄로 적는다 | 소비: 없음 → 생산: RUNBOOK §4 의 명령 블록 | `codex exec -s read-only -C` 로 시작하는 줄부터 8줄 안에 `< /dev/null` 이 있다 | `git revert` |
| 7 | ⑦ 논리 역할 이름과 모델 id 가 구분된다 | §2(`--model` 을 넘기지 않는다는 문단, 현재 58행) 또는 §11.1 에, **논리 역할 이름**(예: 검토 역할을 부르는 이름)은 **모델 id 가 아니다**라는 것을 적는다. 그 이름을 `--model` 값으로 넘기면 HTTP 400 이고, 실제 id 는 접두사가 붙은 다른 문자열이다. 값 자체는 바뀔 수 있으므로 **실제 id 를 조회하는 방법**을 적는다 — 값을 문서에 박으면 낡는다. 직전 관통의 검토자가 실제로 돈 모델은 계정 기본값이었다는 관측을 함께 남긴다 | 소비: 없음 → 생산: RUNBOOK 문단 1개 | `논리 역할 이름` 과 `모델 id 가 아니다` 두 문자열이 문서에 있다 | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

이 단위는 **하네스 저장소 자신**이 대상이므로 하네스 검사(check-8~12)가 정당한 검사다.
check-1~7 은 이 단위가 만든 것을 직접 겨눈다 — 순서대로 구현 단위 1~7행이다.

**모든 검사는 종료 코드 자체가 조건이다.** `|| true` 를 쓰지 않고, 부정 조건은 `!` 로 쓴다 —
2회차 관통에서 `|| true` 가 종료 코드를 항상 0 으로 만들어 위반을 통과시킨 적이 있다.
check-1~7 은 **구현 전 상태에서 전부 종료 코드 1** 인 것을 2026-08-30 에 실측했고,
check-8~12 는 같은 시점에 전부 종료 코드 0 이었다.

```yaml
required_checks:
  - id: check-1
    command: "grep -qF -- '--to run:<run-id> --thread-id' adapters/orca/RUNBOOK.md && grep -qF 'ask 스레드' adapters/orca/RUNBOOK.md"
    expect: exit 0
  - id: check-2
    command: "grep -qE '^### 3\\.4\\.1 ' adapters/orca/RUNBOOK.md && grep -qF '낡은 해시' adapters/orca/RUNBOOK.md"
    expect: exit 0
  - id: check-3
    command: "grep -qF '완료 신호가 아니다' adapters/orca/RUNBOOK.md && grep -qF 'task_complete.last_agent_message' adapters/orca/RUNBOOK.md"
    expect: exit 0
  - id: check-4
    command: "grep -qF '프롬프트가 argv 에 있는가' adapters/orca/RUNBOOK.md && ! grep -qF '에 넣은 것 |' adapters/orca/RUNBOOK.md"
    expect: exit 0
  - id: check-5
    command: "grep -qF '기다린 뒤에 채택해도' adapters/orca/RUNBOOK.md && grep -qF 'agent_prompt_stalled' adapters/orca/RUNBOOK.md"
    expect: exit 0
  - id: check-6
    command: "grep -A8 -F 'codex exec -s read-only -C' adapters/orca/RUNBOOK.md | grep -qF '< /dev/null'"
    expect: exit 0
  - id: check-7
    command: "grep -qF '논리 역할 이름' adapters/orca/RUNBOOK.md && grep -qF '모델 id 가 아니다' adapters/orca/RUNBOOK.md"
    expect: exit 0
  - id: check-8
    command: "python3 -m unittest discover -s tests"
    expect: exit 0
  - id: check-9
    command: "bin/romeo validate"
    expect: exit 0
  - id: check-10
    command: "bin/romeo compile --check"
    expect: exit 0
  - id: check-11
    command: "bin/romeo doctor"
    expect: exit 0
  - id: check-12
    command: "bin/romeo fixtures parity --report"
    expect: exit 0
```


## 증거

close PASS · 2026-08-30T23:45:52+09:00 · HEAD b760144dad0d · 검사 기록 run_583f325f5c94

- [evidence/run_583f325f5c94.yaml](evidence/run_583f325f5c94.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
