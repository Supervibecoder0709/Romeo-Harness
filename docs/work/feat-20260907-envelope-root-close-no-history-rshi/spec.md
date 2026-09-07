---
id: feat-20260907-envelope-root-close-no-history-rshi
type: spec
title: 위치 인자가 루트를 따르고, 이력 없는 루트에서도 종료 검사가 판정을 낸다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: low
status: active
approved_at: '2026-09-07T14:29:31+09:00'
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
created: '2026-09-07'
updated: '2026-09-07'
approval_history:
- {approved_at: '2026-09-07T14:05:05+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-07T14:29:31+09:00',
  reason: '1회차 검토자 FAIL findings 1건 — AC-2 의 「인쇄와 --json 의 path 도 그 해석된 경로다」가 없는 파일 문단 안에 있어, 없는 파일은 JSON
    출력 전에 오류 문장으로 끝나는 기존 경로라 검토 시점에 참일 수 없었다. 그 문장을 찾은 파일로 좁히고 없는 파일은 JSON 을 내지 않는다고 명시한다. 산출물은 문제없다 —
    AC-1·3~8 은 검토자가 확인했다'}
---

# 위치 인자가 루트를 따르고, 이력 없는 루트에서도 종료 검사가 판정을 낸다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260907-envelope-root-close-no-history-rshi --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 두 자리를 고친다. ① `romeo envelope check` 에 **상대 경로**를 주면 지금은 명령을 친 자리(cwd)에서
  찾아 `--root` 로 가리킨 루트의 파일을 못 찾는다 — 앞으로는 `--root`(없으면 발견한 루트) 기준으로 찾는다.
  ② git 이력이 없는 루트(저장소가 아니거나 커밋이 없는 저장소)에서 `romeo close` 는 지금 스택 트레이스로
  죽고 검사 목록도 종료 코드도 없다 — 앞으로는 「이력이 없어 신선도를 판정할 수 없다」를 **미검증 검사 한 건**으로
  인쇄하고 종료 코드 1 로 끝난다. 각 규칙이 사는 문서(RUNBOOK §3.0 · plan-close 절차)를 같은 변경에서 함께 고친다.
- **왜 지금:** 둘 다 2026-09-06 M3 관통이 남의 루트를 다루다 실측하고 §12 로 남긴 결함이고(Q-66·Q-67),
  D-81 이 정한 순서의 ①이다 — 이 정비가 끝나야 ②(판정 리비전 분리)가 `--root` 로 옛 리비전 하네스를 돌릴 수 있다.
  M5 attach 요구사항 9건 중 2건이기도 하다. 관통 도중에는 하네스를 고칠 수 없으므로(§10 동결) 관통 사이인 지금 닫는다.
- **기대 결과:** `--root` 를 준 실행에서 위치 인자가 그 루트 기준으로 해석되고, 못 찾으면 **어느 경로에서 찾았는지**가
  문장에 인쇄된다. 이력 없는 루트에서 `close` 는 죽지 않고 검사 목록(앞 검사는 그대로, `FRESH_HEAD` 미검증)과
  종료 코드를 낸다 — 완료(done)가 선언되는 일은 없다. 이력이 있는 루트의 판정은 한 줄도 바뀌지 않는다.
- **수용 기준:**
  - [ ] AC-1 `envelope check` 에 상대 경로를 주면 `--root` 기준으로 찾는다 — 명령을 친 자리가 **다른 저장소**여도
        `--root` 아래의 봉투를 검사해 통과한다. 절대 경로는 지금과 같다.
  - [ ] AC-2 상대 경로의 파일이 없으면 종료 코드 1 과 「결과 계약 파일이 없다」 문장에 **해석된 절대 경로**가 들어가
        어느 루트에서 찾았는지 보인다 — JSON 은 내지 않는다(없는 파일은 이 단위 이전부터 오류 문장과 종료 코드 1 로 끝나는
        기존 경로이고, 그것을 바꾸지 않는다). **찾은** 파일에 대해서는 인쇄와 `--json` 의 `path` 가 그 해석된 경로다.
        스택 트레이스가 아니다.
  - [ ] AC-3 규칙이 사는 자리 둘이 새 규칙을 말한다 — `adapters/orca/RUNBOOK.md` §3.0 에서 `envelope check` 의
        위치 인자를 「셸이 자기 cwd 로 푸는 경로」 목록에 넣은 문장이 사라지고 「상대 경로면 `--root` 기준으로 푼다」가
        적히며, `envelope check --help` 의 `paths` 설명이 같은 규칙을 말한다. 이 문서가 지시하는 명령(`$W/…` 절대 경로)은
        한 글자도 바뀌지 않는다.
  - [ ] AC-4 git 이력이 없는 루트 — 저장소가 아닌 폴더와, `git init` 만 하고 커밋이 없는 저장소 둘 다 — 에서
        `romeo close --unit <id> --root <그 루트>` 는 `FRESH_HEAD` 를 **미검증**으로 인쇄하고 종료 코드 1 로 끝난다.
        그 앞 검사(`FRONTMATTER_VALID`·`APPROVED`·`HAS_EVIDENCE`)는 지금처럼 인쇄되고, 그 문장에
        「git 이력이 없어 신선도를 판정할 수 없다」가 들어가며, 출력에 스택 트레이스가 없다. `--dry-run` 도 같다.
  - [ ] AC-5 그 미검증 뒤의 검사(검사 기록 선택·재실행·검토 판정)는 시도하지 않는다 — 이력 없이는 대조할 현재 값이
        없다. 그 루트에서 `status: done` 이 쓰이는 일은 없다.
  - [ ] AC-6 규칙이 사는 자리(`core/workflows/plan-close/SKILL.md` 의 신선도 검사 문단)가 그 예외를 말한다 —
        「git 이력이 없」는 루트에서는 `FRESH_HEAD` 를 미검증으로 인쇄하고 뒤 검사를 시도하지 않는다는 것.
  - [ ] AC-7 이력이 있는 루트의 판정은 바뀌지 않는다 — 기존 검사를 하나도 고치지 않고 전부 통과하며(삭제 0줄),
        `envelope check` 의 기존 검사도 전부 통과한다. 늘어난 검사는 이 단위가 더한 것뿐이다.
  - [ ] AC-8 `docs/planning/open-questions.md` 의 Q-66·Q-67 행이 해소 표기되고(두 행의 근거 열에 있는 출처 단위 id 는
        남긴다), 이번 작업이 발견했으나 고치지 않은 결함이 새 행으로 열린다.
- **위험과 되돌리기:** 종료 검사의 차단 범위를 **줄이지 않는다** — 예외로 죽던 자리가 미검증(완료 아님)으로 인쇄될 뿐이고,
  못 찾던 파일을 찾을 뿐이다. 바뀌는 동작은 하나다: 명령을 친 자리가 루트의 **하위 폴더**일 때 그 자리 기준으로 적은
  상대 경로는 이제 못 찾는다 — 그런 호출을 지시하는 문서·검사는 없고(전부 `$W/…` 절대 경로), 못 찾으면 해석된 경로가
  문장에 인쇄된다. 되돌리기는 `git revert <이 단위의 통합 커밋>` — 외부 상태를 바꾸지 않는다.
- **결정 필요:** 없음.


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/envelope.py` · `romeo/close.py` · `romeo/cli.py` · `tests/test_envelope.py` · `tests/test_docs_evidence_close.py` · `adapters/orca/RUNBOOK.md` · `core/workflows/plan-close/SKILL.md` · `docs/planning/open-questions.md` · `docs/planning/progress.md` · `docs/work/feat-20260907-envelope-root-close-no-history-rshi/` · `.claude/skills/plan-close/SKILL.md` · `.agents/skills/plan-close/SKILL.md` · `.harness/compiled.yaml` (뒤 셋은 컴파일 산출물 보험 — 코어 본문만 고치면 재생성이 필요 없다는 것을 직전 정비가 확인했으나, 필요해질 경우를 위해 상한에 둔다)
- 영향을 받는 부분: `romeo envelope check` 의 위치 인자 해석과 「파일이 없다」 문장 · `romeo close` 가 이력 없는 루트를 만났을 때의 종료 경로. `run-unit` 은 절대 경로로 부르므로 영향이 없다.
- 바꾸지 않는 것(비범위): `romeo review record <source>` 의 경로 해석(그 파일은 설계상 루트 밖에 둔다 — RUNBOOK §3.7 `-o <워크트리 밖 파일>`) · `romeo/gitinfo.py`(`head_sha`·`is_repo` 는 그대로) · `romeo/evidence.py`·`romeo/run_unit.py` · `_finish` 의 판정 규칙 · 이력이 **있는** 루트에서의 어떤 판정 · `docs/requirements/attach-requirements.md`(「올린 것」 목록은 M5 의 입력이고 D-81 이 이미 이 정비를 그 앞에 두었다) · 다른 열린 질문(Q-64·Q-69·Q-70·Q-71~Q-81)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope check` 의 상대 위치 인자를 루트 기준으로 푼다(Q-66) | `romeo/envelope.py` 의 `check_result_envelope` 에서 `project_root` 를 resolve 한 **뒤** `path = Path(path)` 가 절대 경로가 아니면 `project_root / path` 로 바꾼다. `FileNotFoundError` 문장과 결과의 `path` 는 그 해석된 경로로 낸다. `romeo/cli.py` 의 `envelope check` 파서에서 `paths` 의 help 를 「상대 경로는 `--root`(없으면 발견한 루트) 기준으로 푼다」로 바꾼다. `run_unit._stage_collect` 는 절대 경로를 넘기므로 손대지 않는다 | 소비: 없음 → 생산: `check_result_envelope(...)["path"]` 가 해석된 절대 경로 문자열 | check-1·check-2·check-10 | `git revert` |
| 2 | 이력 없는 루트에서 `close` 가 예외 대신 판정을 낸다(Q-67) | `romeo/close.py` 의 `close_unit` 에서 `cur_head = head_sha(project_root)` 를 `try` 로 감싸 `subprocess.CalledProcessError` 면 `check("FRESH_HEAD", UNVERIFIED, "이 루트에는 git 이력이 없어 신선도를 판정할 수 없다 — <git 의 stderr 한 줄>")` 를 남기고 `HAS_EVIDENCE` 와 같은 모양으로 `return _finish(checks, fm, body, spec, runs, dry_run, project_root, None)` 한다. `subprocess` import 가 없으면 더한다. `is_repo` 로 미리 가르지 않는다 — 커밋 없는 저장소는 `is_repo` 가 참이면서 `head_sha` 가 실패하므로, 실패 자체를 잡아야 두 경우가 한 문장으로 모인다 | 소비: 없음 → 생산: 검사 행 `{"id": "FRESH_HEAD", "level": "unverified"}` 와 그 뒤 검사 없음 | check-3·check-4 | `git revert` |
| 3 | 규칙이 사는 문서 둘이 같은 변경에서 참이 된다(§11) | `adapters/orca/RUNBOOK.md` §3.0 「셸에 넣는 값은 이 규약이 아니다」 문단: `bin/romeo envelope check` 의 위치 인자를 cwd 목록에서 빼고 한 문장을 더한다 — 「`envelope check` 의 위치 인자는 절대 경로면 그대로, 상대 경로면 `--root` 기준으로 푼다 — 봉투에 적히는 값은 아니다. 이 문서는 그 자리에 `$W` 절대 경로를 쓴다」. `-C`·`-o`·`$(cat …)` 는 여전히 cwd 로 푸는 값이므로 그 문장은 남긴다. `core/workflows/plan-close/SKILL.md` 절차 2 의 `FRESH_HEAD`/`FRESH_TREE` 항목 뒤에 「루트에 git 이력이 없으면(`git rev-parse HEAD` 실패) `FRESH_HEAD` 를 미검증으로 인쇄하고 그 뒤 검사는 시도하지 않는다 — 대조할 현재 값이 없다. 스택 트레이스가 아니라 검사 목록과 종료 코드로 끝난다」를 넣는다. 도구명·모델명을 쓰지 않는다(C-C6). frontmatter 의 `description:` 은 건드리지 않는다 | 소비: 1·2 가 만든 규칙 → 생산: 없음 | check-5·check-6·check-7 | `git revert` |
| 4 | 판별 검사와 회귀 방지 검사를 더한다 | `tests/test_envelope.py` 의 `TestResultEnvelopeCheck` 에 검사 2건(상대 경로가 루트 기준으로 풀려 통과 · 없는 상대 경로의 문장에 해석된 절대 경로) — 기존 헬퍼 `_check` 를 그대로 쓰고 첫 인자에 `docs/work/<unit>/result/…` 상대 문자열을 준다(테스트 프로세스의 cwd 는 이 저장소라 그 자체가 「그럴듯한 거짓 값」이다). `tests/test_docs_evidence_close.py` 에 새 클래스 `TestCloseWithoutGitHistory` — `TestVerticalSlice` 와 같은 순서로 저장소·단위·승인·구현 커밋·증거 1건을 만든 뒤 `docs/` 를 `git` 없는 임시 폴더로 복사하고, 그 폴더가 어느 저장소 안도 아님을 `git rev-parse --is-inside-work-tree` 실패로 먼저 확인한다(안이면 `GIT_CEILING_DIRECTORIES` 로 상위 탐색을 막는다). 검사 3건: 저장소 아닌 루트 · `git init` 만 한 루트 · 이력 있는 루트의 회귀. 단언은 판정 문자열이 아니라 검사 id·`level`·종료 코드·「Traceback 부재」로 한다. **기존 검사는 한 줄도 고치지 않는다** | 소비: 1·2 → 생산: 검사 5건 | check-1~check-4·check-8 | 해당 검사만 되돌린다 |
| 5 | 이번 작업이 발견했으나 고치지 않은 것을 연다 | `docs/planning/open-questions.md` 의 Q-66·Q-67 행을 해소 표기(취소선 + 「해소(2026-09-07, <이 단위 id>)」 + **닫지 않은 것**)로 바꾸고, 발견한 결함을 새 행(Q-82~)으로 더한다. 두 행 근거 열의 `feat-20260906-m3-close-foreign-repo-ik3u` 문자열은 **지우지 않는다**(`tests/test_attach_requirements.py` 가 그 문자열로 출처 집합을 만든다). `docs/planning/progress.md` 「지금 상태」 블록의 활성 단위·다음 행동 줄을 갱신한다(예산 30줄·2KB) | 소비: 없음 → 생산: 없음 | check-9 | `git revert` |

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

**판별 검사와 회귀 방지 검사의 구분** — §11 은 「어느 쪽인지는 검증 계획에 적는다, 적지 않으면 전부 판별 검사로 본다」고 한다.
**판별 검사는 check-1~check-6·check-10 일곱이고**, 승인 전에 기존 상태·가상 완료 상태 양쪽에서 실행해 각각 실패·통과를 보였다.
check-7~check-9 는 **회귀 방지 검사**이므로 양쪽 실측 대상이 아니다 — 양쪽에서 통과하는 것이 그 검사의 정의다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_envelope.TestResultEnvelopeCheck.test_a_relative_path_is_resolved_against_the_root"
  - id: check-2
    command: "python3 -m unittest tests.test_envelope.TestResultEnvelopeCheck.test_a_missing_relative_path_names_the_root_it_looked_in"
  - id: check-3
    command: "python3 -m unittest tests.test_docs_evidence_close.TestCloseWithoutGitHistory.test_a_root_without_a_repository_prints_fresh_head_unverified_instead_of_a_traceback"
  - id: check-4
    command: "python3 -m unittest tests.test_docs_evidence_close.TestCloseWithoutGitHistory.test_a_repository_without_commits_is_reported_the_same_way"
  - id: check-5
    command: "grep -q 'git 이력이 없' core/workflows/plan-close/SKILL.md"
  - id: check-6
    command: "grep -q '상대 경로면' adapters/orca/RUNBOOK.md && ! grep -q 'envelope check` 의 위치 인자, `orca terminal create' adapters/orca/RUNBOOK.md"
  - id: check-7
    command: "bin/romeo compile --check"
  - id: check-8
    command: "python3 -m unittest discover -s tests -q"
  - id: check-9
    command: "python3 -m unittest tests.test_attach_requirements tests.test_enforce_points"
  - id: check-10
    command: "bin/romeo envelope check --help | grep -q '루트 기준'"
```

**각 검사가 무엇을 보는가**

| id | 종류 | 무엇이 참이어야 통과인가 | 반례(그럴듯한 거짓 값) |
| --- | --- | --- | --- |
| check-1 | **판별** | 명령을 친 자리(테스트 프로세스의 cwd = 이 저장소)가 `--root` 와 다른 저장소일 때, `docs/work/<unit>/result/<run>-implementer.json` 상대 문자열이 `--root` 아래에서 풀려 다섯 검사 전부 PASS · 종료 코드 0 | cwd 도 `docs/work/` 를 가진 저장소다 — 빈 값이 아니라 「다른 루트의 같은 모양」이고, 지금 코드는 거기서 찾다 못 찾아 종료 코드 1 을 낸다 |
| check-2 | **판별** | 없는 상대 경로에 대해 종료 코드 1 · 「결과 계약 파일이 없다」 문장에 `--root` 아래로 해석된 **절대 경로**가 들어간다 · Traceback 없음 | 지금 코드는 받은 문자열 그대로(상대 경로)를 인쇄해 어느 루트에서 찾았는지 말하지 않는다 |
| check-3 | **판별** | 증거가 든 단위 폴더를 git 없는 폴더로 복사한 뒤 `close --dry-run --root <그 폴더>` 가 종료 코드 1 · 검사 목록에 `FRESH_HEAD` `level: unverified` · 그 앞 검사 셋은 그대로 · 그 뒤 검사 없음 · 출력에 `Traceback` 없음 | 지금 코드는 `subprocess.CalledProcessError` 로 죽는다 — 검사 목록도 종료 코드도 없다(Q-67 원문) |
| check-4 | **판별** | 같은 폴더에 `git init` 만 한 상태(커밋 0)에서도 check-3 과 같은 판정·같은 문장 | `is_repo` 는 참인데 `head_sha` 가 실패하는 상태 — `is_repo` 로만 가른 구현은 여기서 다시 죽는다 |
| check-5 | **판별** | plan-close 절차 문서에 「git 이력이 없」는 루트의 예외가 적혀 있다 | 기존 문서에 그 문구는 0건이다(실측) |
| check-6 | **판별** | RUNBOOK §3.0 에 「상대 경로면」 규칙이 적혀 있고, `envelope check` 의 위치 인자를 cwd 목록에 넣은 옛 문장은 사라졌다 | 기존 문서는 앞 문구 0건·옛 문장 1건이다(실측) — 새 문장만 더하고 옛 문장을 남기면 두 규칙이 공존해 실패한다 |
| check-7 | 회귀 방지 | 코어 본문 변경이 컴파일 산출물과 어긋나지 않는다 | — |
| check-8 | 회귀 방지 | 기존 검사가 하나도 깨지지 않는다 | — |
| check-9 | 회귀 방지 | 문서 편집이 출처 집합 대조·집행 지점 대조를 깨지 않는다 | — |
| check-10 | **판별** | `envelope check --help` 가 「루트 기준」 규칙을 말한다 | 기존 help 는 예시 경로만 있고 해석 기준이 없다(0건 실측) |

**재실행 시간** — check-8 이 약 130초, 나머지는 각 1~5초다. `romeo close` 의 재실행 상한 600초 안이다.


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
