---
id: feat-20260901-task-copy-brief-count-erc6
type: spec
title: 관통이 매번 손대는 두 자리를 없앤다 — task/ 사본 병합 충돌·브리프 검사 개수 하드코딩
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: done
approved_at: '2026-09-01T14:03:00+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-09-01T14:21:47+09:00'
parent: null
inputs: []
evidence: [evidence/run_e909a3e53aea.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-01'
updated: '2026-09-01'
---

# 관통이 매번 손대는 두 자리를 없앤다 — task/ 사본 병합 충돌·브리프 검사 개수 하드코딩

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260901-task-copy-brief-count-erc6 --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 관통이 매번 사람 손을 부르던 두 자리를 없앤다. ① 위임할 때마다 만들어지는 **작업 계약 사본**(`docs/work/<id>/task/<run>-<role>.json`)이 커밋에 딸려 들어가 통합할 때 `git merge --ff-only` 가 거부되던 것 — 계약을 git 추적 대상에서 뺀다. ② 구현자에게 보내는 절차 문서가 **검사 개수를 문장에 박아 두고 있던 것**(「`required_checks` 6건은…」) — 개수를 지운다.
- **왜 지금:** 둘 다 **다음 관통에서 또 걸린다.** ①은 직전 관통에서 실제로 걸려 재승인 커밋을 `amend` 로 다시 만들었고(`f53d096` → `82a8191`), ②는 이번 검사가 15건이라 `sed` 로 문장을 고쳐 넘겼다. 코어 규칙 §10 은 관통 **중에는** 하네스를 못 고치게 하므로, 고칠 수 있는 구간은 관통과 관통 사이인 지금뿐이다. M3 는 앞으로 관통을 더 돈다.
- **기대 결과:** 위임한 쪽과 워커 쪽이 같은 경로에 계약을 각각 만들어도 통합이 `--ff-only` 로 그대로 지나간다. 구현자 절차 문서를 검사 개수 때문에 고칠 일이 없어진다.
- **수용 기준:**
  - [x] AC-1 **새로 만들어지는 작업 계약은 git 추적 대상이 아니다** — 임의 작업 단위의 `docs/work/<id>/task/<run>-<role>.json` 을 `git check-ignore` 가 제외로 판정하고, 이 단위 폴더에 **실재하는** 계약이 `git status` 의 untracked 목록(`??`)에 나오지 않는다.
  - [x] AC-2 **그런데도 종료 검사는 성립한다** — 계약 파일이 추적되지 않는 상태에서도 `romeo close` 의 작업 계약 앵커가 통과한다는 것이 반례 테스트로 고정된다. (앵커는 커밋 조회가 아니라 **승인 원본에서의 재계산**이다 — `romeo/close.py` 의 `_task_anchor`)
  - [x] AC-3 **이미 커밋된 계약은 추적에서 빠지지 않는다** — 과거 단위의 계약 파일이 여전히 `git ls-files` 에 있다. 이력을 다시 쓰지 않는다.
  - [x] AC-4 `adapters/orca/prompts/implementer-brief.md` 에 **검사 개수를 고정한 표현이 없고**, 계약의 `required_checks` 를 가리키는 문장은 남아 있다 — 개수는 계약이 정하고 절차 문서는 그것을 가리키기만 한다.
  - [x] AC-5 `adapters/orca/RUNBOOK.md` §3.3 이 **이 사본을 커밋하지 않는다는 것과 그 이유**(계약은 승인 원본에서 재계산되는 파생물이다)를 적고, `docs/planning/open-questions.md` 의 `Q-14` 가 해소로 갱신된다.
  - [x] AC-6 기존 검사가 회귀하지 않는다 — unittest 전체와 `compile --check` · `validate` · `doctor --strict --scope repository` · `fixtures check` · `fixtures parity --report` 가 모두 종료 코드 0.
- **위험과 되돌리기:** 위험은 **AC-2 의 전제가 틀리는 것** 하나다 — 계약을 커밋에서 빼는 것이 종료 검사를 망가뜨리면 완료 판정이 서지 않는다. 그래서 승인 전에 실측했다: `romeo/close.py` 의 `_task_anchor` 는 계약 파일을 **작업 트리에서** 읽고(`is_file()`·`read_bytes()`), 진짜 앵커는 `base_sha` 커밋의 승인된 `spec.md` 로 계약을 **다시 만들어 바이트 대조**하는 것이다 — 계약이 이력에 있을 필요가 없다. 2026-09-01 프로브로 규칙을 임시로 넣어 ①새 계약이 untracked 목록에서 사라지고 ②`check-ignore` 가 제외로 판정하며 ③이미 커밋된 계약은 그대로 추적되는 것을 확인하고 되돌렸다. **이번 관통 자체는 여전히 ①을 밟는다** — 규칙은 구현자가 넣으므로 이 단위의 승인·재승인 커밋에는 아직 없다. 그때는 알려진 우회(위임한 쪽 사본을 `git add` 하지 않는다)를 쓴다. 전부 이 저장소 안의 로컬 변경이고 외부 상태를 바꾸지 않으므로 되돌리기는 `git revert <커밋>` 한 번이다. 워크트리에서 작업하므로 통합 전에는 브랜치가 그대로 남는다.
- **결정 필요:** 없음 — 강제 수단 후보 셋(승인 커밋 범위 제한 · `.gitignore` · 커밋 전 확인 검사) 중 `.gitignore` 로 확정했다. 근거는 위 「위험과 되돌리기」의 실측이다.


## 변경 범위

- 바뀌는 파일·모듈: `.gitignore` · `adapters/orca/prompts/implementer-brief.md` · `adapters/orca/RUNBOOK.md` · `docs/planning/open-questions.md` · `tests/test_task_artifact_policy.py` · `docs/work/feat-20260901-task-copy-brief-count-erc6/`
- 영향을 받는 부분: 다음 관통부터의 **통합 절차**(`git merge --ff-only` 가 계약 사본 때문에 거부되지 않는다)와 **위임 절차**(구현자 절차 문서를 `sed` 로 개수까지 고칠 필요가 없어진다). 종료 검사(`romeo/close.py`)는 코드를 바꾸지 않지만, 계약이 추적되지 않는 상태에서도 통과한다는 것이 이제 테스트로 고정된다.
- 바꾸지 않는 것(비범위): **이미 커밋된 계약 파일**(`git rm --cached` 를 하지 않는다 — 이력을 다시 쓰는 것은 되돌리기 어렵고 AC-3 가 그것을 금지한다) · `romeo/close.py`·`romeo/envelope.py` 의 판정 로직 · 코어 규칙(`core/principles/`) · 다른 park 결함(`Q-15`·`Q-16`·`Q-17`·`Q-19`·`Q-23`·`Q-24`·`Q-26`) · `w3qu` 단위의 나머지 4건.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 작업 계약을 git 추적 대상에서 뺀다 | `.gitignore` 에 `docs/work/*/task/` 규칙과 **이유 주석**(계약은 승인 원본에서 재계산되는 파생물이고, 위임한 쪽과 워커 쪽이 같은 경로에 각각 만들어 `--ff-only` 를 막는다)을 더한다. 이미 커밋된 계약은 건드리지 않는다 — `git rm --cached` 를 쓰지 않는다 | 소비: 없음 → 생산: `.gitignore` 의 `docs/work/*/task/` 규칙 | `git check-ignore -q` 가 이 단위와 임의 단위의 계약 경로를 둘 다 제외로 판정하고(check-1·check-2), 실재하는 계약이 `git ls-files` 에도 `git status` 에도 나오지 않는다(check-3), 이미 커밋된 계약은 그대로 추적된다(check-4) | `git revert` |
| 2 | 그 규칙이 종료 검사를 망가뜨리지 않는다는 것을 반례로 고정한다 | `tests/test_task_artifact_policy.py` 에 `TestTaskEnvelopeNotTracked` 를 만든다 — ① 계약 파일이 **추적되지 않는 상태**에서 `romeo/close.py` 의 작업 계약 앵커(`_task_anchor`)가 통과한다 ② 계약 파일이 **작업 트리에 없으면** 그 앵커가 실패한다(제외가 파일까지 없애도 된다는 뜻이 아니다) ③ 규칙이 `docs/work/<임의>/task/` 를 제외하고 `docs/work/<임의>/evidence/`·`result/`·`review/` 는 제외하지 않는다 | 소비: 1 의 규칙 → 생산: `TestTaskEnvelopeNotTracked` | `python3 -m unittest tests.test_task_artifact_policy` 가 종료 코드 0(check-7) | `git revert` |
| 3 | 구현자 절차 문서에서 검사 개수를 지운다 | `adapters/orca/prompts/implementer-brief.md:12` 의 「`required_checks` 6건은 문자열 그대로 실행한다」에서 **개수를 빼고**, 개수는 계약이 정한다는 표현으로 바꾼다. `required_checks` 를 가리키는 문장 자체는 남긴다 | 소비: 없음 → 생산: 그 파일의 12행 문구 | 그 파일에 `<숫자>건` 형태가 남아 있지 않고(check-5) `required_checks` 문장은 남아 있다(check-6) | `git revert` |
| 4 | 그 문구가 다시 개수를 갖지 않게 고정한다 | 같은 테스트 파일에 `TestImplementerBriefNoCheckCount` 를 만든다 — 브리프 본문에 `<숫자>건` 형태가 없고 `required_checks` 를 가리키는 문장은 있다는 것을 반례로 박는다 | 소비: 3 → 생산: `TestImplementerBriefNoCheckCount` | check-7 에 포함 | `git revert` |
| 5 | 절차 문서를 이 결론에 맞춘다 | `adapters/orca/RUNBOOK.md` §3.3 에 **위임한 쪽 사본을 커밋하지 않는다**는 것과 그 이유(계약은 파생물이라 `.gitignore` 가 제외한다 · 커밋하면 워커 쪽 사본과 같은 경로에서 만나 `--ff-only` 가 거부된다)를 적는다. 같은 테스트 파일의 `TestRunbookTaskCopyNotCommitted` 가 §3.3 절 본문에 그 두 가지가 있는지 본다 | 소비: 1 → 생산: RUNBOOK §3.3 문단 · `TestRunbookTaskCopyNotCommitted` | check-7 에 포함 | `git revert` |
| 6 | park 을 닫는다 | `docs/planning/open-questions.md` 의 `Q-14` 행을 다른 해소 항목과 같은 형식(원문 취소선 + **해소(2026-09-01, 이 단위)**)으로 갱신하고, 무엇으로 닫았는지와 **닫지 않은 것**(이미 커밋된 67개는 그대로 둔다)을 적는다 | 소비: 1 → 생산: `Q-14` 행 | `Q-14` 행에 「해소」가 있다(check-8) | `git revert` |

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

```yaml
required_checks:
  - id: check-1
    command: "git check-ignore -q docs/work/feat-20260901-task-copy-brief-count-erc6/task/run_probe-implementer.json"
  - id: check-2
    command: "git check-ignore -q docs/work/feat-00000000-any-unit-zzzz/task/run_x-reviewer.json"
  - id: check-3
    command: 'test -n "$(ls docs/work/feat-20260901-task-copy-brief-count-erc6/task 2>/dev/null)" && test -z "$(git ls-files docs/work/feat-20260901-task-copy-brief-count-erc6/task/)" && test -z "$(git status --porcelain --untracked-files=all docs/work/feat-20260901-task-copy-brief-count-erc6/task/)"'
  - id: check-4
    command: "git ls-files --error-unmatch docs/work/feat-20260829-license-field-46an/task/run_31e175742892-implementer.json"
  - id: check-5
    command: "! grep -qE '[0-9]+건' adapters/orca/prompts/implementer-brief.md"
  - id: check-6
    command: "grep -q 'required_checks' adapters/orca/prompts/implementer-brief.md"
  - id: check-7
    command: "python3 -m unittest tests.test_task_artifact_policy"
  - id: check-8
    command: "grep '^| Q-14 |' docs/planning/open-questions.md | grep -q 해소"
  - id: check-9
    command: "python3 -m unittest discover -s tests"
  - id: check-10
    command: "bin/romeo compile --check"
  - id: check-11
    command: "bin/romeo validate"
  - id: check-12
    command: "bin/romeo doctor --strict --scope repository"
  - id: check-13
    command: "bin/romeo fixtures check"
  - id: check-14
    command: "bin/romeo fixtures parity --report"
```


## 증거

close PASS · 2026-09-01T14:21:47+09:00 · HEAD dc7b16108ebb · 검사 기록 run_e909a3e53aea

- [evidence/run_e909a3e53aea.yaml](evidence/run_e909a3e53aea.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
