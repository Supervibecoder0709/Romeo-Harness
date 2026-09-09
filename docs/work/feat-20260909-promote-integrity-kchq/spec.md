---
id: feat-20260909-promote-integrity-kchq
type: spec
title: 승격과 무결성 — 끝난 사실을 current/ 로 올리고, 링크·ID 중복을 검사한다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: high
status: done
approved_at: '2026-09-09T01:44:00+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-09-09T09:38:25+09:00'
parent: init-20260904-m4-doc-reuse-metrics-wr9m
inputs: [../init-20260904-m4-doc-reuse-metrics-wr9m/charter.md, inputs/ac-rebuttal-20260909-2.md, inputs/ac-rebuttal-20260909.md,
  inputs/probe-20260909.md]
evidence: [evidence/run_4bcfc5770ac3.yaml, evidence/run_98070e608181.yaml, evidence/run_748ddeba9896.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.high.small=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-09'
updated: '2026-09-09'
approval_history:
- {approved_at: '2026-09-09T00:24:38+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-09T00:41:29+09:00',
  reason: '2차 반박(ac-rebuttal-20260909-2.md)이 AC-3·AC-5·AC-9 에 실질 결함을 냈다 — 위조 판별을 같은 사본의 0→1 짝으로, 거짓 양성
    배제를 종료 코드 0 으로, continue-on-error 금지를 상위 job 까지 넓혔다. AC-2·AC-4·AC-7 의 표현도 함께 조였다'}
- {approved_at: '2026-09-09T00:41:29+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-09T01:44:00+09:00',
  reason: '§10 연속 2회 실패 재검토 결론에 따라 AC-4 의 열린 포함 집합을 판별 규칙으로 닫았다 — 괄호 안 내용의 첫 공백 앞까지가 경로 후보이고 # 뒤를 잘라낸
    것이 대상 경로다. fixture 가 담을 세 표기도 명시했다. 다른 AC 와 검증 계획은 그대로다'}
---

# 승격과 무결성 — 끝난 사실을 current/ 로 올리고, 링크·ID 중복을 검사한다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260909-promote-integrity-kchq --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 끝난 사실이 모이는 자리 `docs/current/` 를 열고, 그 자리가 낡지 않도록 코드·정책표와 대조하는 검사 `bin/romeo integrity` 를 세운다. 첫 승격 문서는 「지금 이 저장소가 집행하는 판정 목록」이다.
- **왜 지금:** M4 charter 의 M1(재사용 검색)·M2(1-hop 재개)가 닫혔고 셋째 마일스톤이 승격과 무결성이다. charter 가 이 마일스톤에 미정으로 남긴 「승격 대상 판정 규칙」을 여기서 정한다 — 사용자 확정: **코드·정책표가 집행하는 판정 목록을 올리고, 검사가 그 목록과 코드를 대조한다**.
- **기대 결과:** `docs/current/enforcement.md` 한 장을 읽으면 이 저장소가 지금 무엇을 막고 무엇을 경고하는지 알 수 있다. 코드가 그 목록을 앞질러 가거나 목록이 코드에 없는 것을 적으면 `bin/romeo integrity` 의 종료 코드가 1 이 되고 어긋난 id 를 인쇄한다.
- **수용 기준:**
  - [x] AC-1 `docs/current/enforcement.md` 가 있고, 표의 각 행이 **리터럴로 등록되는** 판정 id 하나와 그 판정의 수준(`error` 또는 `warning`)과 출처 파일 경로를 담는다. 표의 행 수는 0 이 아니다. 리터럴 연결로 만들어지는 판정(`romeo/close.py` 의 `check("REVIEW_" + cid, …)`)은 표가 아니라 「파생 판정」 절에 규칙 한 줄로 적고, 대조 대상이 아님을 그 자리에 밝힌다.
  - [x] AC-2 `bin/romeo integrity` 는 두 집합의 `(id, 수준)` 쌍을 대조한다 — **(가)** `docs/current/enforcement.md` 표에서 읽은 것, **(나)** `romeo/close.py` 의 `check("<id>"` 리터럴 호출과 `ENVELOPE_CHECKS` 튜플·`romeo/validate.py` 가 `errors`/`warnings` 에 넣는 리터럴 접두·`core/policy/packages.yaml` 의 `blocks:` 키에서 뽑은 것. 뽑는 규칙은 하나다 — 그 호출이나 `append` 의 문자열 인자가 **고정 텍스트로 시작**하면 그 선두의 첫 공백 앞까지를 id 로 본다(f-string 의 고정 선두를 포함한다). 문자열이 변수나 연결 표현으로 **시작**하면 (나)에 넣지 않는다. 주석 줄도 넣지 않는다. 두 집합이 다르면 종료 코드가 1 이고, 한쪽에만 있는 쌍을 어느 쪽인지와 함께 표준 출력에 인쇄한다.
  - [x] AC-3 AC-2 의 판별을 세 위조 상태에서 실측한다. 각 위조는 **다른 위반이 없어 `bin/romeo integrity` 가 종료 코드 0 을 내는 사본**에서 만들고, 같은 사본에서 위조 전 0 과 위조 후 1 을 이어 관측한다 — 종료 코드의 차이가 그 위조에서 나온 것임을 이 짝이 보인다. 세 상태는 ① `romeo/close.py` 에 기존 호출과 같은 형태의 유효한 `check("<코드에 없던 id>", True)` 한 줄을 더한 것 ② `enforcement.md` 표에서 한 행을 지운 것 ③ `enforcement.md` 의 한 id 를 코드에 없는 이름으로 바꾼 것이다. 세 상태에서 위조한 id 가 출력에 인쇄된다.
  - [x] AC-4 `bin/romeo integrity` 는 `docs/current/` 아래 `.md` 문서의 인라인 링크(대괄호로 텍스트, 이어지는 괄호로 대상을 적는 표기)에서 **괄호 안 내용의 첫 공백 앞까지**를 경로 후보로 잡고, 그 후보에서 `#` 뒤를 잘라낸 것을 대상 경로로 본다. 대상 경로가 `http://`·`https://`·`mailto:` 로 시작하거나 빈 문자열이면 검사하지 않고, 그 밖의 대상 경로가 그 문서의 위치를 기준으로 존재하지 않으면 종료 코드가 1 이고 그 링크를 인쇄한다. fixture 는 괄호 안이 경로뿐인 표기·경로 뒤에 공백과 따옴표 제목이 붙은 표기·경로 뒤에 공백만 붙은 표기를 함께 담는다. 참조형 링크(괄호 대신 두 번째 대괄호로 라벨을 적고 경로를 다른 줄에 정의하는 표기)는 이 검사의 대상이 아니다 — `docs/current/` 에서 쓰지 않는 표기다.
  - [x] AC-5 `bin/romeo integrity` 는 `docs/work/` 아래 각 폴더의 `spec.md` frontmatter `id` 를 모아(`spec.md` 가 없는 폴더는 건너뛴다) 같은 값이 둘 이상이면 종료 코드가 1 이고 그 값과 폴더 이름들을 인쇄한다. 탐색 범위는 `docs/work/` **바로 아래** 폴더다. 두 fixture 로 양방향을 실측한다 — 폴더 이름이 서로 다르고 frontmatter `id` 만 같은 fixture 에서 종료 코드가 1 이고 그 id 가 인쇄되며, `id` 는 서로 다르고 `title` 만 같은 fixture 에서 종료 코드가 0 이다.
  - [x] AC-6 `bin/romeo integrity` 를 인자 없이 이 저장소 루트에서 실행하면 종료 코드가 0 이고, 검사한 루트의 경로와 대조한 id 개수를 인쇄한다. 인쇄된 루트가 그 실행의 작업 디렉터리다.
  - [x] AC-7 `romeo/close.py` 에서 `check("` 로 등록되는 id 집합이 승인 커밋 시점의 같은 파일과 현재 파일에서 같다 — 승인 커밋은 `bin/romeo envelope build` 가 이력에서 찾는 것과 같은 커밋이다 — 이 단위는 종료 판정을 더하지도 빼지도 않는다.
  - [x] AC-8 (가)와 (나)가 다른 상태에서 `bin/romeo close` 의 출력에 「승격 후보」로 시작하는 줄이 있고, 두 집합이 같은 상태에서는 그 줄이 없다.
  - [x] AC-9 `.github/workflows/harness.yml` 이 `bin/romeo integrity` 를 실행하는 단계를 담고, 그 단계와 그 단계를 담은 job 에 `continue-on-error` 가 없고, 그 단계의 `run` 에 `|| true` 가 없다.
- **위험과 되돌리기:** 가장 큰 위험은 목록이 검사를 통과하려고 코드를 따라 적는 사본이 되는 것 — AC-3 ①이 그 반대 방향(코드가 앞서 나감)을 막고, ③이 그럴듯한 거짓 이름을 막는다. 되돌리기는 `git revert <구현 커밋>` 한 번이다. `docs/current/` 는 새로 저술한 문서라 지워도 원본 소실이 없고, `bin/romeo integrity` 는 다른 명령이 호출하지 않는 독립 명령이라 제거해도 기존 경로가 깨지지 않는다.
- **결정 필요:** 없음 — 승격 판정 규칙과 `decisions.md` append 제외는 `/plan` 확정 단계에서 사용자가 정했다.


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/integrity.py` (새 모듈 — 대조·링크·id 중복) · `romeo/cli.py` (하위 명령 등록) · `romeo/close.py` (승격 후보 인쇄 한 줄) · `docs/current/enforcement.md` (첫 승격 문서 — 표 49행과 「파생 판정」 절) · `tests/test_integrity.py` · `fixtures/integrity/` (깨진 링크·중복 id) · `.github/workflows/harness.yml` · `docs/planning/open-questions.md` (범위 밖 발견 등록)
- 영향을 받는 부분: `bin/romeo` 의 하위 명령 목록이 하나 늘어난다. CI 단계가 하나 늘어난다. `romeo close` 의 출력에 줄이 하나 늘어나되 종료 판정은 그대로다.
- 바꾸지 않는 것(비범위): `romeo/validate.py` 의 기존 `BROKEN_LINK` 검사 (`docs/work/` 패키지 문서를 계속 그대로 본다) · `core/policy/*.yaml` 의 판정 어휘 · `docs/planning/`·`docs/decisions/` 의 링크 (이 검사의 대상이 아니다) · `decisions.md` append 도구

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 코드·정책표에서 판정 id 를 뽑는다 | `romeo/integrity.py` 에 `derive_ids()` — `romeo/close.py` 의 `check("<id>"` 와 `ENVELOPE_CHECKS`, `romeo/validate.py` 의 오류·경고 접두, `core/policy/packages.yaml` 의 `blocks:` 키를 읽어 `{id: 출처}` 를 낸다 | 소비: 없음 → 생산: `derive_ids() -> dict[str, str]` | `python3 -c "from romeo.integrity import derive_ids; d=derive_ids(); print(len(d)); assert 'BROKEN_LINK' in d and 'FRESH_TREE' in d and 'spec-ready' in d"` 가 exit 0 | `git revert` |
| 2 | 목록 문서를 읽는다 | `romeo/integrity.py` 에 `document_ids(path)` — `docs/current/enforcement.md` 표의 첫 열에서 백틱으로 감싼 id 를 뽑는다 | 소비: 없음 → 생산: `document_ids(Path) -> dict[str, str]` | `python3 -c "from romeo.integrity import document_ids; from pathlib import Path; print(len(document_ids(Path('docs/current/enforcement.md'))))"` 가 0 이 아닌 수를 인쇄 | `git revert` |
| 3 | 첫 승격 문서를 저술한다 | `docs/current/enforcement.md` — 판정 id·무엇을 보는가·막는가 경고인가·출처 파일을 표로. 단위 1 이 뽑은 집합과 같은 집합을 담는다 | 소비: `derive_ids()` → 생산: `docs/current/enforcement.md` | 단위 4 의 `bin/romeo integrity` 가 exit 0 | 파일 삭제 |
| 4 | 세 검사를 한 명령으로 묶는다 | `romeo/integrity.py` 의 `main()` — 대조(단위 1·2) · `docs/current/` 상대 링크 · `docs/work/` frontmatter id 중복. 위반을 인쇄하고 위반 수가 0 이 아니면 exit 1. `romeo/cli.py` 에 `integrity` 등록 | 소비: `derive_ids`·`document_ids` → 생산: `bin/romeo integrity` | `bin/romeo integrity` 가 exit 0 (AC-6) | `git revert` |
| 5 | 판별력을 fixture 와 위조로 고정한다 | `tests/test_integrity.py` — AC-3 의 세 위조 상태를 임시 사본에서 만들어 exit≠0 을 확인, `fixtures/integrity/broken-link/`·`duplicate-id/` 로 AC-4·AC-5 를 확인 | 소비: `bin/romeo integrity` → 생산: 검사 5건 | `python3 -m unittest tests.test_integrity -v` 가 exit 0 | `git revert` |
| 6 | 종료 검사가 승격 후보를 인쇄하되 판정하지 않는다 | `romeo/close.py` — 판정 뒤에 `derive_ids()` 와 `document_ids()` 차이가 있으면 「승격 후보」 한 줄을 인쇄한다. `check(` 를 부르지 않는다 | 소비: `romeo.integrity` → 생산: close 출력 한 줄 | AC-7 의 id 집합 비교 명령이 exit 0 | `git revert` |
| 7 | CI 가 이 검사를 돌린다 | `.github/workflows/harness.yml` 에 `bin/romeo integrity` 단계 추가 | 소비: `bin/romeo integrity` → 생산: CI 단계 | `grep -q 'romeo integrity' .github/workflows/harness.yml` 가 exit 0 | `git revert` |

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

**판별 검사와 회귀 방지 검사의 구분(§11).** check-1·check-2·check-3 은 **판별 검사**다 — 이 단위가 없으면 실패한다.
check-4·check-5·check-6 은 **회귀 방지 검사**로, 두 상태에서 모두 통과가 예상되므로 승인 전 양쪽 실측의 대상이 아니다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_integrity -v"
  - id: check-2
    command: "bin/romeo integrity"
  - id: check-3
    command: "grep -q 'romeo integrity' .github/workflows/harness.yml"
  - id: check-4
    command: "python3 -m unittest discover -s tests"
  - id: check-5
    command: "bin/romeo validate"
  - id: check-6
    command: "bin/romeo compile --check"
```


## 증거

close PASS · 2026-09-09T09:38:25+09:00 · HEAD 178e03970e32 · 검사 기록 run_748ddeba9896

- [evidence/run_4bcfc5770ac3.yaml](evidence/run_4bcfc5770ac3.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_98070e608181.yaml](evidence/run_98070e608181.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_748ddeba9896.yaml](evidence/run_748ddeba9896.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
