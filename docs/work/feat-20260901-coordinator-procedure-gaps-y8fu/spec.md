---
id: feat-20260901-coordinator-procedure-gaps-y8fu
type: spec
title: 코디네이터 위임 절차 결함 3건 정비 — 재검토 커밋·재작업 재위임·Run 바인딩
unit: T1
mode: delivery
intent: write
facets: [docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: low
status: active
approved_at: '2026-09-01T12:02:17+09:00'
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
created: '2026-09-01'
updated: '2026-09-01'
approval_history:
- {approved_at: '2026-09-01T10:19:36+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-01T12:02:17+09:00',
  reason: '1회차 검토자 findings 2건을 반영한다 — AC-5 에 관측을 실행에 묶으라는 요구를 더하고, check-8 을 세 결과 키(a_switch_back·b_read_after_switch·c_rejection_shape)
    대조로 강화하며, probe 실행이 evidence 에 stdout_tail·log_sha256 으로 봉인됐는지 보는 check-15 를 더한다(14→15건). 산출물 범위와
    나머지 AC 는 그대로다.'}
---

# 코디네이터 위임 절차 결함 3건 정비 — 재검토 커밋·재작업 재위임·Run 바인딩

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260901-coordinator-procedure-gaps-y8fu --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 직전 정비(`feat-20260831-park-defects-actm`)가 돌면서 드러났으나 그 단위 범위 밖이었던 **위임 절차 결함 3건**을 닫는다. ① 재검토 기록을 커밋했는지 확인하는 자리가 위임 전 점검에 없다 — 없으면 자식 워크트리 안의 워커가 반복 중단 브레이크를 못 푼다. ② 승인은 그대로인 채 **구현만 다시 붙이는** 경우에 무엇을 해야 하는지가 절차 어디에도 없다. ③ Run 을 새로 만들면 코디네이터 터미널이 그쪽으로 옮겨 붙어 옛 Run 에 대한 명령이 조용히 거부되는데, 되돌리는 방법이 절차가 아니라 문서 맨 뒤 관측 표에만 있다.
- **왜 지금:** 셋 다 **다음 관통을 위임으로 돌리는 순간 그대로 다시 걸리는 것**이고, ① 은 직전 관통에서 실제로 두 번 걸려 3회차를 판정 없이 중단시켰다. 코어 규칙 §10 은 관통이 시작된 뒤 하네스·절차 변경을 금지하므로, 고칠 수 있는 구간은 관통과 관통 **사이**인 지금뿐이다. 다음 작업은 M3(charter·capabilities·gate·시나리오)이고 그것은 위임으로 돈다.
- **기대 결과:** 다음 관통을 도는 사람이 세 가지를 **절차를 순서대로 밟다가** 만난다 — 기억이나 지난 세션의 대화, 문서 맨 뒤 관측 표를 따로 뒤지는 것에 의존하지 않는다. ③ 은 되돌리는 방법이 실제로 작동하는 것을 실행으로 본 뒤에 적는다.
- **수용 기준:**
  - [ ] AC-1 위임 전 점검에 **재검토 기록이 커밋 안에 있는지 확인하는 자리**가 있고, 그 확인이 실행 가능한 명령이다.
  - [ ] AC-2 그 확인이 두 경우를 **가른다** — 시도 기록이 아직 없는 단위는 통과시키고, 작업 트리에만 있고 커밋 밖에 있는 재검토는 거부한다. 반례로 고정한다.
  - [ ] AC-3 실행 순서 절에 **승인은 그대로인 채 재작업만 새 위임으로 붙이는 분기**가 있고, 새 Run 이 필요한 이유(한 run 은 한 위임이라는 증거 쪽 방어)와 밟을 순서가 함께 적혀 있다.
  - [ ] AC-4 실행 순서 절에 **Run 바인딩 전환**이 있다 — Run 을 둘 이상 만들었을 때 옛 Run 으로 되돌아가는 명령과, 지금 어디에 붙어 있는지 확인하는 명령.
  - [ ] AC-5 AC-4 의 전환을 **실행으로 관측**해 그 결과를 관측 기록에 남긴다. 되는 것과 안 되는 것을 구분해 적고, **그 관측이 어느 실행에서 나왔는지 증거에 묶는다** — 관측 파일과 원시 로그가 모두 증거의 제외 경로라, 파일만으로는 그것이 그 실행에서 나왔다고 말할 수 없다(1회차 검토자 findings 2).
  - [ ] AC-6 세 결함이 「지금 상태」 블록의 임시 메모에서 벗어나 **이 단위의 산출물로 추적된다** — 상태 블록과 열린 질문 원장이 서로 어긋나지 않는다.
- **위험과 되돌리기:** 바뀌는 것은 이 저장소 안의 문서와 테스트뿐이고 외부 상태를 바꾸지 않는다. 잘못되면 `git revert <커밋>` 한 번으로 돌아간다. AC-5 만 저장소 밖 상태를 하나 만든다 — Orca Run 이다. Run 은 이름공간이자 인박스일 뿐 배치를 하지 않으므로 비용·부작용이 없고, 만들어진 Run 은 이 단위의 관측 증거로 남긴다(지우지 않는다).
- **결정 필요:** 없음 — 세 가지를 승인 전에 확정했다. ① 은 문서와 반례 테스트로 닫고 `envelope build` 의 동작은 바꾸지 않는다. ③ 은 실행으로 확인한 뒤에 적는다. 셋을 열린 질문 원장에 park 으로 먼저 열지 않는다(지금 고치고 있으므로).

## 변경 범위

- 바뀌는 파일·모듈:
  - `adapters/orca/RUNBOOK.md`
  - `tests/test_runbook_procedure.py`
  - `.harness/observations.yaml`
  - `docs/planning/progress.md`
  - `docs/planning/open-questions.md`
  - `docs/work/feat-20260901-coordinator-procedure-gaps-y8fu/`
- 영향을 받는 부분: 다음 관통의 위임 절차 전체. RUNBOOK 은 모든 위임의 절차 원본이라 잘못 쓰면 다음 관통이 서지 않거나 조용히 어긋난다.
- 바꾸지 않는 것(비범위):
  - `romeo/evidence.py` 의 `_stamp_ids` — 한 run 에 두 위임을 거부하는 것은 증거의 출처를 지키는 **의도된 방어**다. 고치면 한 run 에 두 위임이 섞인다.
  - `romeo/envelope.py` 의 `repeat_gate` 와 `romeo/run_unit.py` 의 `gate()` — 브레이크 판정 자체는 그대로 둔다. 이 단위가 고치는 것은 **브레이크를 푼 기록이 워커에게 도달하는 경로**지 브레이크가 아니다.
  - RUNBOOK §11.1 의 2026-08-29 관측 행 — 실행 순서 절로 **옮겨 적을** 뿐 지우지 않는다. 그 표는 언제 무엇을 봤는지의 기록이다.
  - Orca CLI 자체의 동작 — 우리 저장소 밖이다.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | §3.1 의 위임 전 확인에 재검토 기록 대조를 넣는다 | `adapters/orca/RUNBOOK.md` §3.1 — 지금의 확인 2(`git ls-tree` 8행)는 **항상 있어야 하는 파일**을 세는 것이라 `attempts.yaml` 을 그 목록에 넣을 수 없다(첫 관통에는 그 파일이 없어 8행 판정이 깨진다). 그래서 확인을 하나 더 만든다 — 커밋 안의 `attempts.yaml` 과 작업 트리의 것을 대조해 **다르면 거부**한다. 양쪽 다 없으면 통과한다 | 소비: 없음 → 생산: §3.1 의 새 확인 번호와 그 명령 문자열 | `awk` 로 §3.1 절만 잘라 `attempts.yaml` 과 `git` 명령이 그 안에 있는지 본다 (check-1·check-2) | `git revert` |
| 2 | 그 확인이 두 경우를 실제로 가른다는 것을 반례로 고정한다 | `tests/test_runbook_procedure.py` 신규 — 임시 git 저장소를 만들어 (a) `attempts.yaml` 이 아예 없는 단위 (b) 커밋된 것과 작업 트리의 것이 다른 단위 두 경우에 §3.1 의 명령이 각각 exit 0 · exit≠0 을 내는지 본다. 명령 문자열은 **RUNBOOK 에서 뽑아** 쓴다 — 문서와 테스트가 따로 놀지 않게 한다 | 소비: 1 이 만든 §3.1 명령 문자열 → 생산: `tests/test_runbook_procedure.py` | `python3 -m unittest tests.test_runbook_procedure` (check-3) | 테스트 파일 삭제 |
| 3 | 재작업을 새 위임으로 붙이는 분기를 실행 순서에 넣는다 | `adapters/orca/RUNBOOK.md` §3 안 — §3.4.1(재승인) 옆에 **승인은 그대로인 채 구현만 다시 붙이는** 경우를 적는다. `romeo/evidence.py` 의 `_stamp_ids` 가 한 run 에 두 위임을 거부한다는 사실, 그래서 새 Run 이 필요하다는 것, 옛 Task 를 닫는 것까지 순서로 적는다 | 소비: 없음 → 생산: §3 안의 새 절 번호 | §3 안에 제목이 `재작업` 을 담은 `### 3.x` 절이 있고, **그 절 본문 안에** `_stamp_ids` 와 `run-create` 가 있는지 본다 (check-4·check-5). `_stamp_ids` 는 §3.8 회수 절에 이미 나오므로 파일 전체 검색은 빈 검사다 | `git revert` |
| 4 | Run 바인딩 전환을 실행 순서에 넣는다 | `adapters/orca/RUNBOOK.md` §3.2 — Run 을 만들면 코디네이터 터미널이 그 Run 에 붙고, 둘 이상 만들면 뒤엣것이 이긴다는 것. 되돌리는 명령(`run-use --id`, `--run` 이 아니다)과 지금 어디에 붙어 있는지 보는 명령(`run-current --json`), 거부가 종료 코드 0 에 `.ok == false` 로 온다는 것을 적는다 | 소비: 없음 → 생산: §3.2 의 전환 문단 | `awk` 로 §3 전체를 잘라 `run-use --id`·`run-current` 가 그 안에 있는지 본다 (check-6·check-7) | `git revert` |
| 5 | 전환이 실제로 작동하는지 실행으로 보고, 그 실행을 증거에 봉인한다 | `.harness/observations.yaml` 의 `coordinator_run_rebinding` — Run 두 개를 만들어 옛 Run 으로 되돌아간 뒤 그 Run 의 상태를 읽을 수 있는지 실행한다. 결과는 `a_switch_back`·`b_read_after_switch`·`c_rejection_shape` 세 자리에 각각 `result` 를 담아 적는다. **probe 를 `bin/romeo evidence run --label run-rebinding-probe -- …` 로 돌린다** — 관측 파일도 원시 로그도 `romeo/evidence.py` 의 `exclusions()` 제외 경로라, 증거 명령을 거치지 않으면 stdout 이 어디에도 봉인되지 않는다(Q-23 과 같은 계열). 1회차는 이 자리에서 FAIL 했다 | 소비: 4 가 적은 명령 → 생산: `observations.yaml` 의 세 결과 키 + evidence 의 `run-rebinding-probe` 기록 | 세 결과 키에 `result` 가 있고(check-8), evidence 에 그 라벨의 기록이 있으며 `stdout_tail` 과 `log_sha256` 이 비어 있지 않은지 본다(check-15) | 키 삭제 |
| 6 | 세 결함을 상태 블록의 메모에서 원장으로 옮긴다 | `docs/planning/progress.md` — 「지금 상태」의 "정비 중에 새로 드러난 것 셋" 을 이 단위 id 로 대체한다. `docs/planning/open-questions.md` — ③ 이 실측으로도 닫히지 않는 부분이 남으면 그때만 새 Q 로 연다(닫히면 열지 않는다) | 소비: 5 의 관측 결과 → 생산: 갱신된 두 문서 | `progress.md` 가 이 단위 id 를 담고, 옛 메모 문구가 사라졌는지 본다 (check-9·check-10) | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 페이로드(하네스를 부착한 프로젝트) 작업 단위의 `required_checks` 에
**하네스 자신의 테스트**를 넣지 않는다 — `python3 -m unittest discover -s tests`(하네스 저장소의 테스트),
`bin/romeo` 의 자기 검사(`compile --check` · `validate` · `doctor` · `fixtures …`)가 그것이다.
넣으면 하네스가 깨진 동안 그 페이로드 단위가 닫히지 못한다. 그 단위의 산출물은 멀쩡한데 완료가 서지 않는 것이고,
그때 고쳐야 할 것은 그 단위가 아니라 하네스다 — 두 판정을 한 검사에 묶으면 어느 쪽이 깨졌는지 구분되지 않는다
(근거: `feat-20260829-license-field-46an` 의 check-5 가 이 형태였다).
하네스 저장소 **자신**을 대상으로 하는 작업 단위에서는 그 검사들이 정당하다 — 그때는 그것이 이 단위의 산출물이기 때문이다.
**이 단위가 그 경우다** — 대상이 이 저장소의 절차 문서와 그 반례 테스트다.

**종료 코드 자체가 조건이다.** 검사에 적는 것은 `id` 와 `command` 둘뿐이고, 그 명령의 종료 코드 0 이 통과다.
기대를 문장으로 따로 적는 자리는 두지 않는다 — 사람은 그것을 조건으로 쓰는데 기계는 판정에 쓰지 않으므로,
그 검사는 무엇을 확인하는지 적혀 있는 채로 아무것도 확인하지 않는 **빈 검사**가 된다(2026-08-31 실측으로 제거).
확인하고 싶은 조건이 있으면 그 조건을 **명령으로** 쓴다.
같은 이유로 옵션이 판정을 만드는 명령은 그 옵션까지 적는다 — 예: `bin/romeo doctor` 는 옵션 없이 쓰면 항상 exit 0 이라 빈 검사이고,
부착 검증(K-68)을 실제로 판정하게 하려면 `bin/romeo doctor --strict --scope repository` 로 쓴다(Q-21).

그래서 `|| true` 를 붙이지 않는다 — 종료 코드를 항상 0 으로 만들어 위반을 통과시킨다.
부정 조건은 `!` 로 쓴다: `! grep -q '<있으면 안 되는 것>' <파일>`.

**절 안을 본다.** 아래 문서 검사는 파일 전체가 아니라 `awk` 로 자른 **그 절 안**을 본다. 파일 어딘가에 그 문자열이
있다는 것은 절차를 밟는 사람이 그 자리에서 만난다는 뜻이 아니다 — ③ 이 정확히 그 형태의 결함이었다(§11.1 에는 있고 §3 에는 없었다).

```yaml
required_checks:
  - id: check-1
    command: "awk '/^### 3\\.1 /,/^### 3\\.2 /' adapters/orca/RUNBOOK.md | grep -q 'attempts\\.yaml'"
  - id: check-2
    command: "awk '/^### 3\\.1 /,/^### 3\\.2 /' adapters/orca/RUNBOOK.md | grep -qE 'git (show|diff|ls-tree)[^|]*attempts\\.yaml'"
  - id: check-3
    command: "python3 -m unittest tests.test_runbook_procedure -v"
  - id: check-4
    command: "awk '/^## 3\\. 실행 순서/,/^## 4\\./' adapters/orca/RUNBOOK.md | grep -qE '^### 3\\.[0-9.]+ .*재작업'"
  - id: check-5
    command: "python3 -c \"import re,sys; t=open('adapters/orca/RUNBOOK.md').read(); m=re.search(r'^### 3\\.[0-9.]+ [^\\n]*재작업[^\\n]*\\n(.*?)(?=^#{2,3} )', t, re.S|re.M); b=m.group(1) if m else ''; sys.exit(0 if '_stamp_ids' in b and 'run-create' in b else 1)\""
  - id: check-6
    command: "awk '/^## 3\\. 실행 순서/,/^## 4\\./' adapters/orca/RUNBOOK.md | grep -q 'run-use --id'"
  - id: check-7
    command: "awk '/^## 3\\. 실행 순서/,/^## 4\\./' adapters/orca/RUNBOOK.md | grep -q 'run-current'"
  - id: check-8
    command: "python3 -c \"import yaml,sys; k=(yaml.safe_load(open('.harness/observations.yaml')) or {}).get('coordinator_run_rebinding') or {}; need=('a_switch_back','b_read_after_switch','c_rejection_shape'); sys.exit(0 if all(isinstance(k.get(n),dict) and any(str(k[n].get(f,'')).strip() for f in ('result','exit_code')) for n in need) else 1)\""
  - id: check-15
    command: "python3 -c \"import glob,yaml,sys; hits=[c for f in glob.glob('docs/work/feat-20260901-coordinator-procedure-gaps-y8fu/evidence/*.yaml') for c in (yaml.safe_load(open(f)) or {}).get('commands',[]) if str(c.get('id','')).startswith('run-rebinding-probe')]; sys.exit(0 if hits and all(str(c.get('stdout_tail','')).strip() and c.get('log_sha256') for c in hits) else 1)\""
  - id: check-9
    command: "grep -q 'feat-20260901-coordinator-procedure-gaps-y8fu' docs/planning/progress.md"
  - id: check-10
    command: "! grep -q '다음 정비 후보다' docs/planning/progress.md"
  - id: check-11
    command: "python3 -m unittest discover -s tests"
  - id: check-12
    command: "bin/romeo validate"
  - id: check-13
    command: "bin/romeo doctor --strict --scope repository"
  - id: check-14
    command: "bin/romeo compile --check"
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
