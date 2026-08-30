---
id: feat-20260830-harness-defects-w3qu
type: spec
title: 3차 관통이 드러낸 하네스 결함 5건 정비
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: low
status: active
approved_at: '2026-08-30T14:29:56+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-08-30'
updated: '2026-08-30'
---

# 3차 관통이 드러낸 하네스 결함 5건 정비

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260830-harness-defects-w3qu --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 3차 관통이 드러낸 하네스 결함 5건을 M3 진입 전에 고친다 — ① 계약 생성이 파이썬 traceback 으로 죽는 자리에 사유를 붙이고, ② 쓰기 상한을 정하는 줄의 형식 제약을 템플릿에 인쇄하고, ③ 위임 프롬프트의 검사 개수 하드코딩을 지우고, ④ `romeo compile` 이 쓰는 대상을 명령으로 물어볼 수 있게 하고, ⑤ 검토자 기동의 '늦은 채택도 실패한다' 는 관측을 RUNBOOK 에 적는다.
- **왜 지금:** 다섯 건 모두 **다음 위임에서 다시 걸리는 것**이고, M3 는 또 관통을 돈다. ④ 는 이번 관통에서 1차 위임을 통째로 폐기시켰고, ①② 는 승인·재승인을 두 번 더 돌게 만들었다. 코어 규칙 §10 은 관통 중에 하네스를 못 고치게 하므로, 고칠 수 있는 구간은 관통과 관통 **사이**인 지금뿐이다.
- **기대 결과:** M3 관통의 위임이 이 다섯 가지 이유로는 중단되지 않는다. 구현자가 「변경 범위」를 쓸 때 컴파일 산출물을 손으로 기억하지 않고 `bin/romeo compile --list-outputs` 로 물어본다.
- **수용 기준:**
  - [ ] AC-1 `expect` 문구에 콜론이 든 spec 으로 `bin/romeo envelope build` 를 돌리면 파이썬 traceback 이 아니라 **어느 검사의 어느 줄이 검증 계획 YAML 을 깨뜨렸는지 지목하는 한국어 오류**가 나오고 종료 코드가 0 이 아니다.
  - [ ] AC-2 `core/templates/tech-spec.md` 의 「변경 범위」에 '바뀌는 파일·모듈 은 **한 줄**이어야 하고 각 항목의 경로를 백틱으로 감싸야 한다' 는 제약과 그 이유가 인쇄되어 있고, `bin/romeo new` 로 새로 만든 spec 에 그 문구가 그대로 나타난다.
  - [ ] AC-3 `adapters/orca/prompts/implementer-brief.md` 에 검사 개수를 고정한 표현이 남아 있지 않다 — 개수는 계약이 정하고 프롬프트는 그것을 가리키기만 한다.
  - [ ] AC-4 `bin/romeo compile --list-outputs` 가 컴파일이 실제로 쓰는 경로를 전부 인쇄한다 — 어댑터별 지침 파일과 스킬 디렉터리에 더해 `.agents/` 와 `.harness/compiled.yaml` 이 빠짐없이 들어 있다.
  - [ ] AC-5 `adapters/orca/RUNBOOK.md` §3.7 에 '너무 늦게 채택해도 `agent_prompt_stalled` 로 실패한다' 는 관측과, 그때 쓴 우회(비대화형 기동 + 결과 파일 회수)가 적혀 있다.
  - [ ] AC-6 기존 검사가 회귀하지 않는다 — unittest 전체와 `compile --check`·`validate`·`doctor`·`fixtures parity --report` 가 모두 종료 코드 0.
- **위험과 되돌리기:** ①④ 는 `romeo/` 아래 코드를 건드리고, 그 중 ① 은 **모든 위임의 입구**(계약 생성)에 있다 — 잘못 고치면 `envelope build` 자체가 막힌다. 그래서 AC-6 이 기존 9건 재실행을 요구한다. 전부 이 저장소 안의 로컬 변경이고 외부 상태를 바꾸지 않으므로, 되돌리기는 `git revert <커밋>` 한 번이다. 워크트리에서 작업하므로 통합 전에는 이 브랜치가 그대로 남는다.
- **결정 필요:** 없음


## 변경 범위

- 바뀌는 파일·모듈: `romeo/close.py` · `romeo/compile.py` · `romeo/cli.py` · `core/templates/tech-spec.md` · `adapters/orca/prompts/implementer-brief.md` · `adapters/orca/RUNBOOK.md` · `tests/` · `docs/work/feat-20260830-harness-defects-w3qu/` · `CLAUDE.md` · `AGENTS.md` · `.claude/` · `.agents/` · `.harness/compiled.yaml`
- 영향을 받는 부분: `bin/romeo envelope build`(①의 오류 경로) · `bin/romeo new` 가 만드는 모든 새 spec(②) · 다음 위임의 구현자 프롬프트(③) · `bin/romeo compile` 의 CLI 표면(④, 읽기 전용 옵션 추가). 컴파일 산출물 5종은 `core/templates/tech-spec.md` 변경과 무관하지만, 상한에서 빠뜨려 위임이 폐기된 것이 결함 ④ 였으므로 이번에는 범위에 포함한다.
- 바꾸지 않는 것(비범위): 계약 스키마(`core/schemas/task-envelope.json`·`result-envelope.json`) · 코어 규칙(`core/principles/AGENTS.core.md`) · 권한 상한(`.harness/bindings.yaml`·`.claude/settings.json`) · 정책표(`core/policy/*.yaml`) · 검증 계획 YAML 의 **문법**(①은 오류를 알려줄 뿐 콜론을 허용하지 않는다) · `docs/planning/progress.md`(통합 뒤 별도로 갱신한다)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | ① 검증 계획 YAML 이 깨졌을 때 사유를 말한다 | `romeo/close.py` 의 `required_checks()` 가 `yaml.safe_load` 를 부르는 자리에서 파서 오류를 잡아, 어느 줄·어느 열이 깨졌고 그 원인이 따옴표 없는 콜론일 수 있다는 것을 한국어로 지목하는 오류로 바꾼다. 오류에 명령 문자열 전체를 싣지 않는다 | 소비: 없음 → 생산: `required_checks()` 가 파서 실패에 대해 내는 예외 형태 | `tests/` 에 콜론이 든 `expect` 를 가진 검증 계획 본문으로 `required_checks()` 와 `envelope build` 를 부르는 회귀 테스트를 추가하고, traceback 이 아니라 지목 오류가 나오는 것과 종료 코드가 0 이 아닌 것을 확인한다 | `git revert` |
| 2 | ② 쓰기 상한을 정하는 줄의 형식 제약을 템플릿이 말한다 | `core/templates/tech-spec.md` 의 「변경 범위」에 '바뀌는 파일·모듈 은 한 줄이어야 하고 각 항목의 경로는 백틱으로 감싼다. 이 줄이 작업 계약의 `allowed_paths` 가 된다' 는 제약과 이유를 인쇄한다 | 소비: 1행 없음 → 생산: 템플릿 문구 | `bin/romeo new` 로 임시 단위를 만들어 그 문구가 들어 있는 것을 확인하고 임시 단위를 지운다 | `git revert` |
| 3 | ③ 위임 프롬프트에서 검사 개수를 지운다 | `adapters/orca/prompts/implementer-brief.md` 의 '`required_checks` 6건' 에서 개수를 빼고, 개수는 계약이 정한다는 표현으로 바꾼다 | 소비: 없음 → 생산: 프롬프트 문구 | 그 파일에 검사 개수를 고정한 표현이 남아 있지 않은 것을 `grep` 으로 확인한다 | `git revert` |
| 4 | ④ 컴파일이 쓰는 대상을 명령이 답한다 | `romeo/compile.py` 가 이미 계산하는 쓰기 대상 목록을 인쇄만 하는 `--list-outputs` 옵션을 `romeo/cli.py` 의 `compile` 에 붙인다. 파일을 쓰지 않는 읽기 전용 경로이며, 목록은 어댑터 지침 파일·스킬 디렉터리·`.agents/`·`.harness/compiled.yaml` 을 모두 포함한다. `romeo/compile.py` 첫머리 docstring 의 산출물 목록도 실제와 맞춘다 | 소비: 없음 → 생산: `bin/romeo compile --list-outputs` 의 출력 형식 | 그 명령의 출력에 `.agents/` 와 `.harness/compiled.yaml` 이 들어 있고, 실행 전후로 작업 트리가 변하지 않는 것을 확인한다 | `git revert` |
| 5 | ⑤ 검토자 기동의 늦은 채택 실패를 RUNBOOK 이 말한다 | `adapters/orca/RUNBOOK.md` §3.7 에 `tui-idle` 을 기다린 뒤에 채택해도 `agent_prompt_stalled` 로 실패한 관측 1건과, 그때 쓴 우회(비대화형으로 띄우고 결과 파일을 회수)를 적는다. 재현 조건은 표본 1건이라 단정하지 않고 관측으로만 적는다 | 소비: 없음 → 생산: RUNBOOK 문단 | §3.7 에 그 문단이 있고, 기존의 '너무 일찍 채택하면 경쟁한다' 서술과 모순되지 않는 것을 읽어 확인한다 | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

이 단위는 **하네스 저장소 자신**이 대상이므로 하네스 검사(check-1~5)가 정당한 검사다.
check-6~9 는 이 단위가 만든 것을 직접 겨눈다 — 순서대로 결함 ④·③·②·⑤ 다. 결함 ① 은 코드 변경이므로 check-1 의 회귀 테스트가 겨눈다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest discover -s tests -t . -v"
    expect: exit 0
  - id: check-2
    command: "bin/romeo compile --check"
    expect: exit 0
  - id: check-3
    command: "bin/romeo validate"
    expect: exit 0
  - id: check-4
    command: "bin/romeo doctor"
    expect: exit 0
  - id: check-5
    command: "bin/romeo fixtures parity --report"
    expect: exit 0
  - id: check-6
    command: "bin/romeo compile --list-outputs"
    expect: exit 0 이고 출력에 .agents/ 와 .harness/compiled.yaml 이 모두 있다
  - id: check-7
    command: "grep -c '6건' adapters/orca/prompts/implementer-brief.md || true"
    expect: 출력이 0 이다 (검사 개수를 고정한 표현이 남아 있지 않다)
  - id: check-8
    command: "grep -n '한 줄' core/templates/tech-spec.md"
    expect: exit 0 이고 변경 범위 절의 형식 제약을 인쇄한 줄이 나온다
  - id: check-9
    command: "grep -n 'agent_prompt_stalled' adapters/orca/RUNBOOK.md"
    expect: exit 0 이고 늦은 채택 실패를 적은 줄이 함께 나온다
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
