---
id: feat-20260830-harness-tuneup-6xcq
type: spec
title: M3 진입 전 하네스 정비 — run-unit 자동화·코어 규칙 승격·문서 다이어트
unit: T1
mode: delivery
intent: write
facets: [tooling, docs, security]
gates: [privacy-security]
profile: standard
blast_radius: medium
uncertainty: medium
status: active
approved_at: '2026-08-30T13:31:24+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:gate.any=kept', 'profile:uncertainty.medium=kept',
    'overlay:gate.any', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-08-30'
updated: '2026-08-30'
approval_history:
- {approved_at: '2026-08-30T13:13:42+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-08-30T13:17:58+09:00',
  reason: check-9 의 expect 문구에 있던 콜론이 required_checks YAML 파싱을 깨뜨려 가운데점으로 교체했다. 명령·기대 종료 코드·수용 기준·확인란은
    불변}
- {approved_at: '2026-08-30T13:17:58+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-08-30T13:20:52+09:00',
  reason: 「변경 범위」의 바뀌는 파일·모듈 을 한 줄로 통합해 쓰기 상한 파서가 읽을 수 있게 했다. 경로 16건을 명시(compile 산출물과 romeo/envelope.py·close.py
    포함). 수용 기준·확인란·검증 계획 불변}
- {approved_at: '2026-08-30T13:20:52+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-08-30T13:31:24+09:00',
  reason: 쓰기 상한 누락 2건 보완 — romeo compile 은 .claude/ 와 .agents/ 양쪽에 쓰고 .harness/compiled.yaml 에 기록하는데 셋
    중 둘이 변경 범위에 없었다. 구현자가 AC-2·AC-4 달성 불가를 보고해 확인했다. 경로 16→18건. 수용 기준·확인란·검증 계획 불변}
---
# M3 진입 전 하네스 정비 — run-unit 자동화·코어 규칙 승격·문서 다이어트

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs, security · 게이트 privacy-security
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260830-harness-tuneup-6xcq --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** M2 관통에서 드러난 운영 부담 7가지를 한 묶음으로 정리한다 — 관통 절차를 한 명령(`romeo run-unit`)으로 묶고,
  진행 기록 안에만 있던 규범 3건(하네스 동결·위협 모델·검토 FAIL 사유)을 규칙 파일로 옮기고, `progress.md` 를 113KB 에서 20KB 이하로 줄인다.
  여기에 **관통 반복 중단 기준**을 함께 넣는다 — M2 에서 관통이 6회 돌았고 그 반복을 끝낸 것은 규칙이 아니라 사용자 결정(D-76)이었다.
- **왜 지금:** M2 가 D-76 으로 닫혔고 M3 는 아직 시작하지 않았다. 이 묶음에 들어가는 규칙 하나가 "관통 중에는 하네스를 고치지 않는다" 이므로,
  그 규칙이 코어에 들어간 뒤에는 다음 관통이 도는 동안 하네스를 손댈 수 없다 — 정비는 관통과 관통 **사이**에 해야 한다.
  그리고 M3 는 시나리오가 3개라 관통 1회의 수동 비용이 그대로 곱해진다.
- **기대 결과:** ① 관통 1회를 `romeo run-unit` 한 명령으로 시작한다(기동은 여전히 사람이 승인한다)
  ② "다음 세션이 무엇을 따라야 하는가" 가 진행 문서가 아니라 규칙 파일에 있다
  ③ 세션 첫 문서가 20KB 이하가 되고, 덜어낸 서술은 `docs/planning/archive/` 에서 그대로 읽을 수 있다.
  ④ 관통이 연속 2회 실패하면 3회차 기동이 그 자리에서 멈추고, 사람이 완료 정의를 재검토할 때까지 반복이 계속되지 않는다.
- **수용 기준:**
  - [ ] AC-1 `romeo run-unit` 이 실재하고, dry-run 으로 5단계(작업 계약 생성 → 위임 명령 출력 → 결과 회수·앵커 검증 → evidence 기록 → 관측 모으기)를 순서대로 수행한다. 실제 기동(`--spawn`)의 실측은 이 단위의 범위가 아니다
  - [ ] AC-2 "관통 중에는 하네스를 고치지 않는다" 가 `core/principles/AGENTS.core.md` 에 있고, `romeo compile` 산출물인 두 런타임 지침 파일에 같은 문구로 들어 있다
  - [ ] AC-3 위협 모델(무엇을 막고 무엇을 막지 못하는가)이 `docs/requirements/constraints.md` 의 K-56 이후 번호로 있고, `progress.md` 는 원문 대신 그 링크만 갖는다. 옮기는 과정에서 문장을 고치지 않는다
  - [ ] AC-4 `core/workflows/review/SKILL.md` 가 "무엇이 FAIL 사유인가" 를 열거하고, 그것이 두 런타임의 review 스킬 산출물에 반영돼 있다 (Q-10 (a))
  - [ ] AC-5 페이로드(부착 대상) 작업 단위의 `required_checks` 에 하네스 자신의 테스트를 넣지 않는 규칙이 `core/templates/tech-spec.md` 에 있고, 그 규칙을 검사하는 테스트가 있다
  - [ ] AC-6 `docs/planning/progress.md` 가 20,480 bytes 이하이고, 덜어낸 서술은 `docs/planning/archive/` 에 있으며 문서 안의 상대 링크 중 깨진 것이 0 이다
  - [ ] AC-7 기존 검사가 전부 통과한다 — unittest · `compile --check` · `validate` · `doctor` · `fixtures parity --report`
  - [ ] AC-8 관통 반복 중단 기준이 `AGENTS.core.md` 에 규칙으로 있고, `romeo run-unit` 이 그것을 강제한다 — 같은 작업 단위에서 **연속 2회 실패**가 기록돼 있으면 3회차 기동을 exit 1 로 거부하고, `--after-review "<재검토 결론>"` 이 주어지면 그 결론을 기록하고 진행한다. 관통 성공 시 연속 카운터가 0 으로 돌아가고, base_sha 가 바뀌어도 리셋되지 않는다
- **위험과 되돌리기:** 코어 규칙과 템플릿을 바꾸므로 **이 저장소의 다음 작업이 곧바로 바뀐 규칙 아래 돈다**(하네스가 하네스를 만든다).
  잘못되면 `git revert <커밋>` 으로 되돌린다 — 한 커밋 묶음이라 되돌리기 단위가 하나다. 문서 감축분은 `archive/` 파일과 git 이력 양쪽에 남아 소실되지 않는다.
  운영 데이터·외부 저장소·배포는 건드리지 않는다.
  중단 기준은 **정당한 반복까지 막을 수 있다** — 그래서 차단이 아니라 '사람의 판단을 한 번 강제하는' 형태이고 `--after-review` 로 즉시 풀린다. 상한이 방해가 되면 규칙 한 줄과 상수 하나를 고치면 된다.
- **결정 필요:** 없음 — 2026-08-30 사용자 확정으로 둘 다 닫혔다(범위: 한 단위 7항목 / 덜어낸 문서: `docs/planning/archive/` 로 이동 후 링크).

## 변경 범위

- 바뀌는 파일·모듈: `core/principles/AGENTS.core.md` (동결 규칙과 중단 기준) · `core/workflows/review/SKILL.md` (FAIL 사유 열거) · `core/templates/tech-spec.md` (페이로드 검사 분리 규칙) · `docs/requirements/constraints.md` (위협 모델 K-56~) · `docs/planning/progress.md` (감축) · `docs/planning/archive/` (신설) · `romeo/run_unit.py` (신설) · `romeo/cli.py` (서브커맨드 등록) · `romeo/envelope.py` · `romeo/close.py` · `tests/` (신규 테스트) · `docs/work/feat-20260830-harness-tuneup-6xcq/` (계약·증거·결과·attempts.yaml) · `CLAUDE.md` · `AGENTS.md` · `.claude/` · `.agents/` · `.harness/compiled.yaml` (앞 다섯은 romeo compile 산출물이며 손으로 고치지 않는다 — compile 은 claude 쪽 .claude/ 와 codex 쪽 .agents/ 양쪽에 쓴다) · `adapters/` (compile 의 입력이자 RUNBOOK 갱신 대상)
- 영향을 받는 부분: 이 저장소의 이후 모든 작업 단위. 부착 대상 프로젝트는 아직 없다(M5 이전).
  `run-unit` 은 기존 명령(`envelope build` · `envelope check` · `evidence record` · `fixtures parity`)을 호출하는 상위 계층이며 그 명령들의 판정 로직을 바꾸지 않는다.
- 바꾸지 않는 것(비범위):
  - `fixtures/parity/` 의 관측 케이스 — 계약은 **커밋된 spec 블롭**에서 계산되므로 템플릿 변경이 기존 케이스의 계약 바이트를 바꾸지 않는다. check-5 가 그것을 회귀로 확인한다
  - `.harness/bindings.yaml` 의 권한 상한과 역할 계약 — 위협 모델을 **옮기는 것**이지 경계를 바꾸는 것이 아니다
  - G-M3 채택 게이트(D-52) · impl6 교체 실행(D-76 ①) · M3 의 기능 자체(Charter 템플릿 · `capabilities.yaml` · `gate-create`)
  - `run-unit --spawn` 의 실제 기동 경로 — 코드는 넣되 실측은 다음 관통에서 한다

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 위협 모델을 코어 제약으로 승격 | `progress.md` 의 「위협 모델 — 무엇을 막고, 무엇을 막지 못하는가」 소절을 `docs/requirements/constraints.md` 에 K-56 부터의 행으로 옮긴다. 문장은 고치지 않고 표 형식에만 맞춘다. `progress.md` 자리에는 링크 한 줄을 남긴다 | 소비: 없음 → 생산: K-56~ 번호 (단위 6 이 링크한다) | `grep -c '^| K-5[6-9]' docs/requirements/constraints.md` 가 1 이상이고 `./bin/romeo validate` exit 0 | `git revert` |
| 2 | 관통 동결 규칙 + 반복 중단 기준 | `core/principles/AGENTS.core.md` 에 절 하나를 추가한다 — **① 동결:** 관통(기준·교체 실행)이 시작된 뒤에는 하네스 코드·코어 규칙·템플릿을 바꾸지 않는다, 바꾸려면 관통을 끝내거나 중단하고 새 base 로 다시 시작한다. **② 중단:** 같은 작업 단위에서 관통이 연속 2회 실패하면 3회차를 돌기 전에 완료 정의가 달성 가능한지 재검토하고 그 결론을 기록한다. 실패 원인 분류(산출물·하네스·목표)는 **기록만 하고 차단 판정에는 쓰지 않는다** — 원인 오판이 M2 의 반복을 만들었으므로 자동 분류를 신뢰하지 않는다. `romeo compile` 로 두 지침 파일에 반영 | 소비: 없음 → 생산: 동결 규칙·중단 기준 문구 (두 런타임 지침 파일에 동일), 상한 값 2 (단위 5 가 강제한다) | `./bin/romeo compile --check` exit 0 이고 `CLAUDE.md` · `AGENTS.md` 양쪽에서 두 문구가 grep 된다 | `git revert` |
| 3 | 검토 절차에 FAIL 사유 열거 | `core/workflows/review/SKILL.md` 에 "무엇이 FAIL 사유인가" 절을 신설한다 — 어떤 findings 가 게이트 FAIL 을 만들고 어떤 것이 경고에 그치는지를 열거한다(Q-10 (a): 같은 findings 로 PASS 와 FAIL 이 갈렸던 원인 후보). `romeo compile` 로 두 런타임 스킬에 반영 | 소비: 없음 → 생산: FAIL 사유 목록 | `./bin/romeo compile --check` exit 0 이고 두 런타임의 review 스킬 산출물 양쪽에서 그 절이 grep 된다 | `git revert` |
| 4 | 페이로드 검증 계획에서 하네스 테스트 분리 | `core/templates/tech-spec.md` 의 `required_checks` 안내에 규칙을 추가한다 — 페이로드 작업 단위의 검사는 그 단위의 산출물만 대상으로 한다, 하네스 자신의 테스트를 넣지 않는다. 그 규칙을 검사하는 테스트를 `tests/` 에 넣는다 (근거: `feat-20260829-license-field-46an` 의 check-5 가 하네스 unittest 라서, 하네스가 깨진 동안 페이로드 단위가 닫히지 못했다 — 체크리스트 31) | 소비: 없음 → 생산: 템플릿 규칙 문구 + 검사 테스트 | `python3 -m unittest discover -s tests` exit 0 (새 테스트가 하네스 테스트를 넣은 페이로드 spec 예시를 잡아낸다) | `git revert` |
| 5 | `romeo run-unit` 신설 | `romeo/run_unit.py` 를 만들고 `romeo/cli.py` 에 등록한다. 5단계를 한 명령으로 엮는다 — ① `envelope build` 로 작업 계약 생성 ② 역할별 위임 명령 문자열 생성·출력 ③ 결과 계약 회수와 앵커 검증(`envelope check`) ④ `evidence record` ⑤ `fixtures parity` 관측 등록. **기동은 기본이 dry-run 이고 `--spawn` 을 명시했을 때만 실제로 띄운다**(K-66 — 기동은 비용이 드는 실행이다). RUNBOOK §3 의 수동 순서를 그대로 옮긴다. 회차마다 `docs/work/<unit_id>/attempts.yaml` 에 시도(회차·base_sha·판정·사람이 적은 실패 분류)를 append 하고, **연속 실패 2회가 기록돼 있으면 3회차 기동을 exit 1 로 거부**한다 — `--after-review "<결론>"` 이 오면 그 결론을 기록하고 진행한다(단위 2 의 규칙을 강제하는 자리) | 소비: 없음 → 생산: `romeo run-unit` 서브커맨드 | `./bin/romeo run-unit --help` exit 0 · dry-run 실행이 5단계를 순서대로 인쇄하고 계약 파일을 실제로 만든다 · `python3 -m unittest tests.test_run_unit` exit 0 (연속 실패 2회 → 3회차 거부 · `--after-review` 로 해제 · 성공 시 카운터 0 · base_sha 변경으로는 리셋되지 않음, 반례 4건) | `git revert` |
| 6 | 문서 다이어트 | `progress.md` 의 §10 체크리스트 8~48 을 항목명·상태·근거 링크만 남긴 "완료 표" 로 접고, 긴 서술은 `docs/planning/archive/` 아래 파일로 옮겨 링크한다. 「지금 상태」 블록과 마일스톤 표는 남긴다. 단위 1~5 의 결과가 반영된 **뒤에** 마지막으로 한다 | 소비: 단위 1 의 K 번호 · 단위 2·3·5 의 결과 → 생산: 20KB 이하의 `progress.md` + `archive/` 파일 | `test "$(wc -c < docs/planning/progress.md)" -le 20480` exit 0 이고 상대 링크 깨짐 0 (check-8) | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

이 단위는 **하네스 저장소 자신**이 대상이므로 하네스 테스트(check-1)가 정당한 검사다. 단위 4 가 만드는 규칙은 부착 대상 프로젝트의 페이로드 단위에 적용된다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest discover -s tests"
    expect: exit 0
  - id: check-2
    command: "./bin/romeo compile --check"
    expect: exit 0
  - id: check-3
    command: "./bin/romeo validate"
    expect: exit 0
  - id: check-4
    command: "./bin/romeo doctor"
    expect: exit 0
  - id: check-5
    command: "./bin/romeo fixtures parity --report"
    expect: exit 0 (관측 케이스의 계약 바이트가 이 정비로 바뀌지 않았음을 확인하는 회귀 검사다)
  - id: check-6
    command: "test \"$(wc -c < docs/planning/progress.md | tr -d ' ')\" -le 20480"
    expect: exit 0 (AC-6 의 수치를 대조하는 유일한 검사)
  - id: check-7
    command: "./bin/romeo run-unit --help"
    expect: exit 0 (AC-1 의 명령이 실재하는지)
  - id: check-8
    command: "cd docs/planning && miss=0; for l in $(grep -oE '\\]\\([^)#]+\\)' progress.md | sed -E 's/^\\]\\(//;s/\\)$//' | grep -v '^http'); do [ -e \"$l\" ] || { echo \"MISSING $l\"; miss=1; }; done; test $miss -eq 0"
    expect: exit 0 (다이어트 뒤 progress.md 의 상대 링크가 전부 실재하는지)
  - id: check-9
    command: "python3 -m unittest tests.test_run_unit"
    expect: exit 0 (AC-8 을 대조하는 유일한 검사 — 반례 4건 · 연속 2회 실패 뒤 3회차 거부 · --after-review 해제 · 성공 시 카운터 0 · base_sha 변경으로는 리셋되지 않음)
```

## 위험·백업·복구

hard gate 가 발동했다. 승인 전 상태 변경 0건.

- **영향 범위:** 이 저장소의 코어 규칙(`AGENTS.core.md` · `review/SKILL.md` · `tech-spec.md`) · 요구 문서 · 진행 문서 · `romeo` CLI.
  코어 규칙이 바뀌면 **이 저장소의 다음 작업이 곧바로 그 규칙 아래 돈다.** 외부 저장소·운영 데이터·배포·비용 발생은 없다.
  게이트가 발동한 이유는 위협 모델이 권한 경계의 서술이기 때문이며, 이 단위는 그것을 **옮기기만** 하고 경계 자체를 바꾸지 않는다.
- **사전 백업:** 시작 시점의 HEAD SHA 를 evidence 에 기록한다(현재 `9947c62`, 원격 `origin/Supervibecoder0709/mvp_planning` 에 동일 커밋이 있다).
  별도 백업 파일을 만들지 않는다 — git 이력과 원격이 백업이다.
- **복구 방법:** 한 커밋 묶음이므로 `git revert <커밋>` 하나로 전부 되돌아간다. 커밋 전이라면 `git checkout -- <경로>`.
  `git reset --hard` 는 승인 대상이므로 쓰지 않는다(K-66). 감축된 문서는 `docs/planning/archive/` 에 원문이 남고, 그것마저 잘못되면 `git show 9947c62:docs/planning/progress.md` 로 원본을 꺼낸다.
- **확인할 내용(승인자용):** ① 위협 모델이 K-5x 로 옮겨질 때 문장이 바뀌지 않았는지 ② `progress.md` 에서 무엇이 `archive/` 로 갔고 무엇이 남았는지
  ③ "관통 중 하네스 동결" 규칙의 문구가 이후 작업을 과도하게 묶지 않는지 (관통을 중단하고 다시 시작하는 경로가 열려 있는지)
- **승인 기록:** evidence.approvals 에 남긴다

## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
