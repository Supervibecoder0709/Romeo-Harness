---
id: feat-20260909-promotion-check-coverage-ggkm
type: spec
title: 승격 문서를 보는 자리를 넓힌다 — CI 트리거와 대조 등록부
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
status: active
approved_at: '2026-09-09T12:58:47+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: [inputs/ac-rebuttal-20260909.md, inputs/ac-rebuttal-20260909-2.md]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-09'
updated: '2026-09-09'
---

# 승격 문서를 보는 자리를 넓힌다 — CI 트리거와 대조 등록부

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260909-promotion-check-coverage-ggkm --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 승격 문서(`docs/current/`)를 보는 자리 두 곳을 넓힌다. ① CI 가 도는 **사건**이 CI 가 읽는 **파일**을 덮게 하고, 그 덮음을 검사 코드에서 뽑아 대조한다(Q-90). ② 대조하는 승격 문서 목록을 하드코딩된 상수 하나에서 등록부로 바꾸고, 등록되지 않은 승격 문서를 지목한다(Q-91).
- **왜 지금:** 두 결함 다 바로 앞 단위(`feat-20260909-promote-integrity-kchq`)가 새 검사를 세우면서 §12 로 남긴 것이고, **그 새 검사 자신의 사각**이다. `.github/workflows/harness.yml` 의 `paths:` 에 `docs/` 로 시작하는 항목이 하나도 없어, 문서만 바뀐 커밋에서는 `bin/romeo integrity` 도 `bin/romeo validate` 도 돌지 않는다 — 표에서 한 행을 지운 커밋이 초록불로 지나간다. 그리고 대조 대상 승격 문서는 문자열 상수 하나로 고정돼 있어, 예정된 두 번째 승격 문서(`decisions.md`)가 들어오면 링크만 검사받고 내용은 아무도 대조하지 않는다. 다음 마일스톤(M4 지표)이 이 사각 위에서 돌기 전에 메운다.
- **기대 결과:** `docs/current/enforcement.md` 에서 한 행을 지운 커밋이 CI 를 빨간불로 만든다. `docs/current/` 에 대조원이 없는 새 문서를 두면 `bin/romeo integrity` 가 그 경로를 지목하고 종료 코드 1 을 낸다. 그리고 검사 코드가 읽는 자리가 늘어나면 `paths:` 를 함께 넓히지 않는 한 CI 가 실패한다 — 이 사각이 다시 열리지 않는다.
- **수용 기준:**
  - [ ] AC-1 `romeo/validate.py` 와 `romeo/integrity.py` 가 각각 자기가 읽는 저장소 하위 루트를 `READ_ROOTS` 상수로 선언하고, 그 상수가 **사본이 아니라 실제 출처**다. 판별 규칙 둘을 모두 만족한다 — ① 두 모듈의 소스에 `docs` 로 시작하는 문자열 리터럴이 나타나는 자리는 루트 상수의 정의뿐이고, 경로 조립(`/ "docs"`)과 다른 모듈에 경로 결정을 넘기는 호출이 0건이다. ② 루트 상수를 검사 안에서 다른 값으로 바꿔치면 `validate.find_docs` 와 `integrity.broken_links` 가 그 새 값 아래를 보고 원래 값 아래를 보지 않는다.
  - [ ] AC-2 `tests/test_ci_trigger_coverage.py` 가 두 모듈의 `READ_ROOTS` 합집합의 각 루트에 대해 `.github/workflows/harness.yml` 의 `on.push.paths` 와 `on.pull_request.paths` **양쪽 각각**에서 그 루트를 덮는 패턴을 찾고, 덮이지 않은 `(루트, 이벤트)` 쌍을 그 쌍의 형태로 보고한다 — 보고 형태는 `(루트, 이벤트)` 튜플의 목록이다. 한 쌍이라도 나오면 실패한다. 판별 규칙 셋 — ① 「덮는다」는 패턴에서 끝의 `/**` 를 떼어낸 문자열이 그 루트와 같거나 그 루트의 조상 디렉터리 경로일 때만 참이다. ② `/**` 로 끝나지 않는 패턴은 덮지 않는다. ③ 두 목록 중 하나라도 `!` 로 시작하는 항목을 담으면 그것만으로 실패한다 — 제외 패턴은 순서에 따라 앞의 포함을 무효로 만들 수 있어, 이 워크플로에서는 쓰지 않기로 한다.
  - [ ] AC-3 AC-2 의 판정을 **이벤트마다 따로** 짝으로 보인다. 세 입력은 AC-2 가 정의한 **같은 판정 함수 하나**를 거치며, 세 호출의 차이는 인자로 넘긴 워크플로 사전뿐이다 — 사본별 기대값을 따로 적은 전용 경로를 두지 않는다. 지금 워크플로에서 `docs/` 로 시작하는 패턴을 `push` 에서만 제거한 사본을 넣으면 보고된 쌍의 이벤트가 `push` 뿐이고, `pull_request` 에서만 제거한 사본을 넣으면 `pull_request` 뿐이며, 지금 워크플로 자체를 넣으면 0쌍이다. 세 입력은 지금 파일에서 파생한 사본이며 승인 커밋이나 git 이력을 참조하지 않는다(Q-92 가 지적한 「새 파일은 이전 상태를 이력에서 꺼낼 수 없다」를 피한다).
  - [ ] AC-4 `.github/workflows/harness.yml` 이 문서 변경에서 실제로 검사를 돌릴 수 있는 상태다 — ① `on.push.paths` 와 `on.pull_request.paths` 가 각각 `docs/current/**` 와 `docs/work/**` 를 담는다. ② 두 목록 어느 쪽에도 `!` 로 시작하는 항목이 없다. ③ 두 이벤트 어느 쪽에도 `branches`·`branches-ignore` 항목이 없다. ④ 그 워크플로의 job 이 `bin/romeo integrity` 와 `bin/romeo validate` 를 스텝의 `run` 으로 담고, 그 두 스텝과 그것을 담은 job 어느 쪽에도 `if:` 가 없다. 넷 중 하나라도 어긋나면 실패한다 — 경로 필터만 넓히고 실행 경로가 막혀 있으면 이 단위는 아무것도 바꾸지 않은 것이다.
  - [ ] AC-5 `romeo/integrity.py` 가 대조 대상을 `{승격 문서 경로: 그 문서와 대조할 파생 함수}` 매핑으로 갖고, 그 매핑은 **소스에 리터럴로 적힌 키만** 갖는다 — 디렉터리를 훑어 키를 채우지 않는다. 판별 규칙 둘 — ① 임시 루트의 `docs/current/` 에 파일을 더하거나 지워도 `integrity` 모듈의 매핑 키 집합이 그대로다. ② 그 매핑의 **값이 실제 대조 경로에서 호출된다** — 검사 안에서 어떤 키의 값을 대조를 반드시 어긋나게 하는 함수로 바꿔치면 그 문서에 대해 `PROMOTION_DRIFT` 가 나오고 종료 코드가 1 이 된다. 그리고 `docs/current/` 아래 `.md` 중 그 매핑의 키가 아닌 파일이 있으면 `bin/romeo integrity` 가 그 경로를 담은 `UNCHECKED_PROMOTION` 줄을 인쇄하고 종료 코드 1 을 낸다.
  - [ ] AC-6 지목 여부가 파일 이름이 아니라 **매핑 키에 드는가**로만 갈린다. 임시 루트에 지금의 `docs/current/enforcement.md` 를 두고, 매핑에 없는 `.md` 를 두 이름으로 각각 더할 때마다 그 경로를 담은 줄과 종료 코드 1 이 나오고, 지우면 같은 루트에서 종료 코드 0 이 나온다. 두 이름 중 하나는 예정된 `decisions.md` 이고, 다른 하나는 **실행할 때마다 달라지는 이름**이다(검사가 실행 시점에 만든다) — 특정 이름을 특별 취급한 구현은 그 쪽에서 걸린다.
  - [ ] AC-7 이 저장소에서 `bin/romeo integrity` 의 종료 코드가 0 이고, 그 0 이 새 검사를 **건너뛴 결과가 아님이 같은 실행의 출력에 드러난다** — `bin/romeo integrity` 가 등록 검사가 실제로 센 값을 한 줄로 인쇄하고(등록된 승격 문서 수와 미등록 수), 이 저장소에서 그 줄이 등록 1건·미등록 0건을 말한다. 다른 루트의 실패가 아니라 이 실행 자신의 출력이 근거다.
  - [ ] AC-8 `docs/current/enforcement.md` 의 「범위」 절에서 integrity 자신이 인쇄하는 이름을 세는 목록에 `UNCHECKED_PROMOTION` 이 **정확히 한 번** 나오고, 그 목록이 세는 이름은 넷이다.
  - [ ] AC-9 `docs/current/enforcement.md` 에 「이 문서를 검사하는 것과 하지 않는 것」 절이 생겨, 승격 문서가 frontmatter 를 두지 않는다는 것 · 문서 검증(`romeo validate`)의 대상이 아니라는 것 · 그 이유(문서 검증의 필수 절과 길이 예산은 라우팅 분류에서 계산되는데 승격 문서에는 분류가 없다) · 대신 무엇이 이 문서를 보는가(`bin/romeo integrity` 의 대조·링크·등록 검사)를 적는다. 그 절이 말하는 frontmatter 부재는 참이다 — `docs/current/enforcement.md` 의 첫 줄이 `---` 가 아니다.
  - [ ] AC-10 AC-9 의 「대상이 아니다」가 참이다 — 저장소 루트에서 `romeo.validate.find_docs('.')` 를 호출하고 그 결과의 각 경로를 저장소 루트 기준 상대경로 문자열로 만들었을 때, `docs/current/` 로 시작하는 것이 0건이다.
- **위험과 되돌리기:** 이 변경은 이 저장소 안에서 끝난다 — 외부 반영·비용·권한 변화가 없다. 되돌리기는 `git revert <커밋>` 한 번이다. 실질 위험은 둘 — ① `paths:` 를 넓혀 문서만 바꾼 커밋에서도 CI 한 벌(약 2분)이 돈다. 의도한 비용이다. ② 새 `UNCHECKED_PROMOTION` 이 거짓 양성을 내면 무관한 커밋이 막힌다. AC-7 이 그것을 지금 저장소에서 실측으로 배제한다. 개별 되돌리기는 `paths:` 두 줄 삭제와 `integrity.py` 의 새 검사 호출 한 줄 삭제다.
- **결정 필요:** 없음 — 확정 단계에서 둘 다 골랐다. Q-90 은 「검사 코드에서 읽는 루트를 뽑아 `paths:` 와 대조」, Q-91 은 「등록되지 않은 승격 문서를 지목」이다. 미완 표지 토큰(문서 검증이 open loop 로 세는 그 낱말) 잔존 검사는 넣지 않기로 했다 — 지금 승격 문서 본문에 그 낱말이 판정 **설명**으로 3곳 있어 도입 즉시 거짓 양성 3건이다.

## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `.github/workflows/harness.yml` · `romeo/integrity.py` · `romeo/validate.py` · `tests/test_ci_trigger_coverage.py` · `tests/test_promotion_registry.py` · `tests/test_integrity.py` · `docs/current/enforcement.md` · `docs/work/feat-20260909-promotion-check-coverage-ggkm/`
- 영향을 받는 부분: CI 가 도는 사건 집합이 넓어진다(문서만 바뀐 커밋도 검사 한 벌을 돈다). `bin/romeo integrity` 의 종료 코드에 판정이 하나 는다 — 그 명령은 CI 스텝이자 `romeo close` 가 참고하는 자리다.
- 바꾸지 않는 것(비범위): `romeo/close.py` 의 판정 목록 · `core/policy/` 의 정책표 · `core/schemas/` 의 문서 스키마 · `docs/current/enforcement.md` 의 「집행하는 판정」 표 본체(새 이름은 「범위」 절에 들어간다) · Q-92(회차 판정 커밋에 미추적 파일) · Q-93(부착 저장소에 승격 규약을 적용할지)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 두 모듈이 자기가 읽는 루트를 선언하고 그것만 쓴다 (AC-1) | `romeo/validate.py` 에 `WORK_ROOT`·`READ_ROOTS` 를 두고 `find_docs` 가 쓴다. `romeo/integrity.py` 에 `CURRENT_ROOT`·`WORK_ROOT`·`READ_ROOTS` 를 두고 `broken_links`·`duplicate_unit_ids` 와 승격 문서 경로가 쓴다 | 소비: 없음 → 생산: `validate.READ_ROOTS` · `integrity.READ_ROOTS` · `integrity.CURRENT_ROOT` | `python3 -c` 로 두 상수를 인쇄하고, 두 모듈에서 루트 상수 정의 밖의 `docs` 리터럴을 센 뒤, 상수를 바꿔치면 두 함수가 새 루트를 보는지 확인한다 | `git checkout -- romeo/validate.py romeo/integrity.py` |
| 2 | CI 트리거가 그 루트를 덮는지 대조한다 (AC-2·AC-3) | `tests/test_ci_trigger_coverage.py` 를 새로 만든다 — 덮음 판정을 **파싱된 워크플로 사전을 받는 함수**로 두어 지금 파일에도 사본에도 같은 판정을 적용할 수 있게 한다 | 소비: `validate.READ_ROOTS` · `integrity.READ_ROOTS` → 생산: `covers(pattern, root)` · `uncovered(on_mapping, roots)` | `python3 -m unittest tests.test_ci_trigger_coverage -v` — 그 안에 `push` 에서만 · `pull_request` 에서만 `docs/` 패턴을 뺀 두 사본으로 각 이벤트의 실패를 보이는 케이스가 있다 | `rm tests/test_ci_trigger_coverage.py` |
| 3 | 트리거를 실제로 넓힌다 (AC-4) | `.github/workflows/harness.yml` 의 `on.push.paths` 와 `on.pull_request.paths` 에 `docs/current/**`·`docs/work/**` 를 각각 더한다. `branches` 부재·`if:` 부재·두 스텝 실재는 지금 상태를 유지하는 것이고, 2 의 검사가 그것을 함께 판정한다 | 소비: 2 의 `uncovered` → 생산: 없음 | `python3 -c` 로 두 목록을 읽어 네 항목을 확인하고, 2 의 검사가 통과한다 | `git checkout -- .github/workflows/harness.yml` |
| 4 | 대조 대상을 등록부로 바꾸고 미등록 문서를 지목한다 (AC-5·AC-7) | `romeo/integrity.py` 의 `DOC_PATH` 상수를 `{경로: 파생 함수}` 매핑으로 바꾸고 `compare()` 가 매핑을 돈다. `unregistered_promotions()` 를 더해 `run()` 의 위반 목록에 넣고, `run()` 이 「등록 N건 · 미등록 M건」 한 줄을 인쇄하게 한다 | 소비: 1 의 `CURRENT_ROOT` → 생산: `integrity.PROMOTED` · `integrity.unregistered_promotions` | `bin/romeo integrity` 가 종료 코드 0 이고, 대조 건수가 이전과 같으며, 「등록 1건 · 미등록 0건」 을 인쇄한다 | `git checkout -- romeo/integrity.py` |
| 5 | 그 판정의 판별을 짝으로 보인다 (AC-5·AC-6·AC-7) | `tests/test_promotion_registry.py` 를 **새 모듈로** 만든다(기존 `tests/test_integrity.py` 에 더하면 그 모듈 명령이 이 단위 없이도 통과해 빈 검사가 된다 — 승인 전 프로브에서 실측했다). 임시 루트 케이스를 담는다 — 미등록 `.md` 를 두 이름(그중 하나는 `decisions.md`)으로 각각 두면 그 경로 줄과 종료 코드 1, 지우면 종료 코드 0. 매핑 키 집합이 그 파일 조작에 흔들리지 않는 것도 같은 자리에서 본다 | 소비: 4 의 `PROMOTED` → 생산: 없음 | `python3 -m unittest tests.test_promotion_registry -v` | `rm tests/test_promotion_registry.py` |
| 6 | 새 이름과 자리 결정을 승격 문서에 적는다 (AC-8·AC-9·AC-10) | `docs/current/enforcement.md` 의 「범위」 절 integrity 자기 판정 목록에 `UNCHECKED_PROMOTION` 을 더하고, 「이 문서를 검사하는 것과 하지 않는 것」 절을 새로 세워 frontmatter 부재·문서 검증 대상 아님·그 이유·대신 무엇이 이 문서를 보는가를 적는다 | 소비: 4 의 판정 이름 → 생산: 없음 | `grep` 으로 두 자리를 확인하고, `validate.find_docs('.')` 결과에 `docs/current/` 가 0건임을 인쇄한다 | `git checkout -- docs/current/enforcement.md` |

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

`check-1`·`check-2`·`check-4`·`check-5` 는 **판별 검사**다 — 이 단위가 없으면 실패해야 한다.
`check-3`·`check-6`·`check-7`·`check-8` 은 **회귀 방지 검사**로, 이 단위 전후 양쪽에서 통과하는 것이 정상이다(AGENTS.core §11).
`check-8` 이 회귀 쪽인 것은 승인 전 실측으로 확인했다 — AC-10(문서 검증 대상에 `docs/current/` 가 0건)은 지금도 참이다.
AC-9(문서에 그 절이 생긴다)를 판별하는 것은 `check-5` 다.

`check-1` 이 담는 테스트는 AC-1(루트 상수가 사본이 아님 — 리터럴 0건과 바꿔치기 둘 다) · AC-2(덮음 판정 규칙 셋) · AC-3(이벤트마다 따로 낸 세 사본의 짝) · AC-4(네 항목 실재와 제외 패턴 부재) 넷이다.
`check-2` 가 담는 테스트는 AC-5(리터럴 등록부 · 값이 실제 호출됨) · AC-6(고정 이름과 실행마다 달라지는 이름으로 낸 1 → 0 짝) 둘이다.
`check-3` 이 AC-7 을 본다 — 종료 코드 0 과 함께 등록 검사가 센 값을 인쇄한다. `check-9` 가 그 줄이 등록 1건·미등록 0건임을 판정한다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_ci_trigger_coverage -v"
  - id: check-2
    command: "python3 -m unittest tests.test_promotion_registry -v"
  - id: check-3
    command: "bin/romeo integrity"
  - id: check-4
    command: "grep -q 'UNCHECKED_PROMOTION' docs/current/enforcement.md"
  - id: check-5
    command: "grep -q '이 문서를 검사하는 것과 하지 않는 것' docs/current/enforcement.md"
  - id: check-6
    command: "bin/romeo validate"
  - id: check-7
    command: "python3 -m unittest discover -s tests"
  - id: check-9
    command: "bin/romeo integrity | grep -q '등록 1건 · 미등록 0건'"
  - id: check-8
    command: "python3 -c \"import romeo.validate as v; hits=[str(q) for q in v.find_docs('.') if str(q).startswith('docs/current')]; assert not hits, hits; print('validate 대상에 docs/current 0건')\""
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
