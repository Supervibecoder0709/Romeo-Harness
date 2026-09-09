---
id: feat-20260909-review-procedure-alignment-ehbp
type: spec
title: 검토자 절차의 요구와 안내를 같은 자리에서 맞춘다 — 봉인·라벨·회차·반박
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
status: active
approved_at: '2026-09-09T18:16:32+09:00'
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

# 검토자 절차의 요구와 안내를 같은 자리에서 맞춘다 — 봉인·라벨·회차·반박

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260909-review-procedure-alignment-ehbp --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 검토자 절차에서 **요구하는 자리와 보는 자리가 다른**(§11 ②) 세 자리를 맞춘다. ① 종료 검사가 요구하는 봉인 명령과 방어 검사 라벨을 절차 문서가 모르는 것(Q-96) ② 검토자 계약이 관통 회차를 하나 더 만드는 것(Q-95) ③ 반박 검사가 `inputs:` 의 첫 파일만 읽는 것(Q-94).
- **왜 지금:** 바로 앞 관통이 §12 로 남긴 셋이고, **Q-96 은 그 관통에서 실제로 두 번 close 를 막았다.** 절차 문서(`core/workflows/review/SKILL.md` 7번과 두 어댑터의 5·6번)는 「봉투를 파일로 남기는 것은 부른 쪽의 일」·「방어 검사는 부른 쪽이 증거 기록 명령으로 돌린다」 까지만 적는다 — 봉인을 만드는 것이 `romeo review record` 라는 것도, 라벨이 정확히 `review-tree-before`/`review-tree-after` 여야 한다는 것도 `adapters/orca/RUNBOOK.md` 에만 있다. **지시대로 따른 실행이 미검증으로 막히고, RUNBOOK 을 따로 읽은 실행만 통과한다.** 다음 마일스톤(M4 지표)의 단위도 검토자를 붙이므로 고치지 않으면 같은 두 자리에서 또 막힌다.
- **기대 결과:** 절차 문서만 읽고 검토자를 띄운 실행이 close 를 통과한다. 라벨이나 명령 이름을 코드에서 바꾸면 안내가 따라오지 않은 것을 검사가 지목한다. 검토자만 다시 띄운 실행이 관통 회차를 늘리지 않고, 그 사실은 이력에 남는다. 반박을 두 번 돌려 AC 를 쪼개도 새 AC 가 미반박으로 남지 않는다.
- **수용 기준:**
  - [ ] AC-1 요구의 정본은 코드에 하나씩 있다 — 방어 검사 라벨은 `romeo.close.DEFENSIVE_LABELS`(이미 있다), 봉인 명령은 `romeo/close.py` 에 새로 두는 `SEAL_COMMAND` 튜플이다. 종료 검사가 요구하는 것이므로 요구가 사는 자리에 함께 둔다. `tests/test_review_guidance_alignment.py` 는 그 둘을 **import 로만** 가져오고(두 정본을 참조하는 자리가 그 import 뿐이다), **자기 안에 그 값을 조각으로도 적지 않는다** — 판별 규칙: 그 검사 파일의 소스에서 `review-tree` · `review record` · `record` · `"review"` 중 어느 것도 문자열 리터럴로 나타나지 않는다(이름을 두 조각으로 나눠 고정하는 것도 중복이다).
  - [ ] AC-2 그 검사가 `SEAL_COMMAND` 가 **CLI 파서에 실제로 등록돼 있는지** 먼저 확인하고(등록이 없으면 그 자체로 실패 — 정본이 실재하지 않는 이름을 가리키는 것이다), 그다음 안내 문서 셋(`core/workflows/review/SKILL.md` · `adapters/claude/workflows/review.md` · `adapters/codex/workflows/review.md`) 각각이 ① 방어 검사 라벨 둘과 ② 봉인 명령을 **백틱으로 감싼 채** 담는지 본다. 백틱 안만 세는 것은 산문 언급과 실행 지시를 가르기 위해서다. 한 문서에서 하나라도 빠지면 그 `(문서, 빠진 것)` 쌍을 튜플 목록으로 보고하며 실패한다. 등록 확인이 실패할 때는 그 사실과 `SEAL_COMMAND` 값을 보고하며 실패한다 — 안내 대조로 넘어가지 않는다.
  - [ ] AC-3 AC-2 의 판정을 **구현이 끝난 뒤의 안내 문서**를 기준으로 네 짝으로 보인다. ① 그 문서 하나에서 라벨 한 줄을 지운 사본을 판정에 넣으면 그 문서의 쌍이 나오고, 지금 문서를 넣으면 0쌍이다. ② `DEFENSIVE_LABELS` 를 **안내 문서 셋 어디에도 나타나지 않는 값**으로 바꿔치면 문서 셋 전부가 쌍을 낸다 — 검사가 코드를 읽는다는 것이 여기서 드러난다(안내에 복사한 사본이면 바꿔쳐도 통과한다). ③ `SEAL_COMMAND` 를 CLI 파서에 없는 이름으로 바꿔치면 AC-2 의 등록 확인에서 실패한다. ④ `SEAL_COMMAND` 를 **파서에 등록은 돼 있지만 안내 문서 셋 어디에도 없는** 다른 명령으로 바꿔치면 등록 확인은 지나고 문서 셋 전부가 쌍을 낸다 — 명령 이름의 문서 대조가 실제로 도는 것이 여기서 드러난다.
  - [ ] AC-4 안내 문서 셋이 실제로 담는 것 넷 — ① 봉투는 `bin/romeo review record` 로 기록해야 종료 검사가 판정으로 센다는 것 ② 방어 검사를 `review-tree-before`/`review-tree-after` 라는 이름으로 검토 **전**과 **후**에 남긴다는 것 ③ 그 셋(방어 검사 둘과 봉투 기록)이 **같은 run** 에 들어가야 한다는 것 ④ 봉투를 손으로 복사하면 봉인이 서지 않는다는 것. 코어 절차에도 적는다 — `bin/romeo` 는 이 하네스 자신의 명령이고 C-C6 이 금지하는 것은 벤더 도구명·모델명이다(코어의 implement 절차가 이미 `romeo evidence run` 을 적는다).
  - [ ] AC-5 `romeo/envelope.py` 의 회차 기록이 **역할을 본다** — `role` 이 `reviewer` 이고 그 run 에 회차가 아직 없으면 회차를 열지 않는다. 그리고 그때 `attempts` 목록의 기존 항목이 **바이트로 그대로 남는다**(시작 시각·`base_sha`·`result` 중 어느 것도 바뀌지 않는다). 판별 상태 넷에서 확인한다 — ① `attempts.yaml` 파일이 아직 없는 상태 ② 다른 run 의 회차가 이미 하나 있는 상태 ③ 같은 run 의 회차가 이미 있는 상태(그때는 기존 회차를 그대로 돌려준다) ④ **여집합** — 같은 상태에서 `role` 이 `implementer` 이면 회차가 **열린다**. 「그대로 남는다」는 저장 전후의 `attempts.yaml` **바이트를 비교해** 확인한다(필드를 골라 비교하면 비교하지 않은 필드가 바뀌어도 통과한다).
  - [ ] AC-6 회차를 열지 않은 검토자 계약은 `attempts.yaml` 의 **`reviewer_runs:`** 목록에 그 run 과 시각을 남긴다. 그 목록은 **덮어쓰지 않는 이력**이다 — 서로 다른 두 run 으로 검토자 계약을 만들면 항목이 둘이 되고, 같은 run 으로 다시 만들면 항목이 늘지 않으면서 기존 항목의 시각도 바뀌지 않는다. 그리고 그 자리는 `reviews:` 와 **다른 목록**이다 — `reviews:` 는 §10 의 사람 재검토 기록이고 `romeo/run_unit.py` 의 `gate()` 가 그것으로 연속 실패 차단을 푼다. 판별 규칙 둘 — ① 연속 2회 실패로 `gate()` 가 **거부하는** 상태에서 검토자 계약을 두 번 만들어도 `gate()` 의 반환값 세 요소가 그대로다. ② 연속 2회 실패에 **사람 재검토가 있어 `gate()` 가 허용하는** 상태에서도 검토자 계약을 만든 뒤 반환값 세 요소가 그대로다 — `reviews:` 목록이 보존된다는 것이 이 두 번째에서만 드러난다(첫 번째는 그 목록이 비어 있어 지워져도 결과가 같다).
  - [ ] AC-7 `romeo/docs.py` 의 반박 검사가 `inputs:` 목록의 각 항목 **문자열이 정책표의 `rebuttal_prefix` 로 시작하는** 파일 전부를 읽고, 각 파일에서 `rebuttal_heading` 으로 시작하는 줄의 **AC 번호**를 모아 합집합으로 본다. `inputs:` 에 없는 파일은 같은 접두로 디렉터리에 있어도 읽지 않는다.
  - [ ] AC-8 AC-7 의 판별을 짝으로 보인다. AC 두 개짜리 확인란에서 — ① 1차 파일이 AC-1 만, 2차 파일이 AC-2 만 반박하고 둘 다 `inputs:` 에 있으면 그 함수가 내는 `AC_UNREBUTTED` 경고가 0건이다. ② 2차 파일을 `inputs:` 에서 빼면 `AC_UNREBUTTED AC-2` 가 나온다. ③ 2차 파일을 `inputs:` 에서 뺀 채 **그 경로를 디렉터리로 두면** 여전히 `AC_UNREBUTTED AC-2` 가 나오고 예외가 오르지 않는다 — 그 경로를 읽으려는 구현은 거기서 실패하므로, 통과 자체가 「읽지 않았다」의 관측이다(반환값만으로는 「읽고 결과를 버리는」 구현과 구별되지 않는다). ②는 그 경로를 디렉터리로 두지 않은 상태이고 ③과 다른 상태다. 세 경우 모두 그 함수의 반환값이 **정확히 기대한 줄만** 담는다 — ①은 0건, ②·③은 `AC_UNREBUTTED AC-2` 한 건이고 `AC_UNREBUTTED AC-1` 은 어느 경우에도 없다.
  - [ ] AC-9 `bin/romeo compile --check` 가 통과한다 — 어댑터 원본을 고쳤으므로 `.claude/skills/` 와 `.agents/skills/` 의 managed block 이 함께 갱신돼 있다.
- **위험과 되돌리기:** 이 변경은 이 저장소 안에서 끝난다 — 외부 반영·비용·권한 변화가 없다. 되돌리기는 `git revert <커밋>` 한 번이다. 실질 위험은 하나 — **회차 기록 규칙은 §10 브레이크의 입력이다.** 잘못 고치면 연속 실패 차단이 풀리거나 엉뚱하게 걸린다. AC-6 이 그것을 직접 겨눈다(검토자 계약을 만들어도 `gate()` 판정이 바뀌지 않는다). 개별 되돌리기는 `envelope.py` 의 조건 한 줄이다.
- **결정 필요:** 없음 — 확정 단계에서 둘 다 골랐다. 다만 **확정하신 「`reviews:` 목록에 남긴다」를 글자 그대로 하지 않는다.** 그 목록은 `gate()` 가 읽어 §10 연속 실패 차단을 푸는 자리라, 검토자 재실행을 섞으면 **사람 재검토 없이 3회차가 돈다** — 안전 장치가 낮아진다. 의도(검토만 다시 돌린 사실을 이력에 남긴다)는 그대로 두고 자리만 `reviewer_runs:` 라는 **별도 목록**으로 나눈다. 되돌리기는 목록 이름 하나다.

## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/close.py` · `core/workflows/review/SKILL.md` · `adapters/claude/workflows/review.md` · `adapters/codex/workflows/review.md` · `romeo/envelope.py` · `romeo/run_unit.py` · `romeo/docs.py` · `tests/test_review_guidance_alignment.py` · `tests/test_reviewer_attempt_isolation.py` · `tests/test_ac_rebuttal_multi.py` · `tests/test_envelope.py` · `tests/test_ac_rebuttal.py` · `.claude/skills/review/SKILL.md` · `.agents/skills/review/SKILL.md` · `docs/work/feat-20260909-review-procedure-alignment-ehbp/`
- 영향을 받는 부분: 다음 단위부터 검토자 계약이 회차를 열지 않는다 — `attempts.yaml` 을 읽는 자리(`gate` · `merge-check` · `compare-attempts`)가 새 목록을 만난다. 반박 경고의 대상이 넓어져 지금 경고가 뜨던 단위가 조용해질 수 있다.
- 바꾸지 않는 것(비범위): `romeo/close.py` 의 `DEFENSIVE_LABELS` **값**과 종료 검사 로직(새 상수 `SEAL_COMMAND` 를 더하는 것은 범위 안이다 — 요구가 사는 자리에 요구를 하나 더 두는 것이고 판정은 바뀌지 않는다) · `adapters/orca/RUNBOOK.md`(이미 옳게 적혀 있다 — 안내가 그것을 따라가는 것이 이 단위다) · `core/policy/packages.yaml` 의 `ac_lint` 설정값 · Q-97(승격 문서 「범위」 절 대조) · Q-83(계약·증거 생성의 판정 리비전)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 요구를 코드에서 읽어 안내와 대조한다 (AC-1·AC-2·AC-3) | `romeo/close.py` 에 `SEAL_COMMAND` 를 두고, `tests/test_review_guidance_alignment.py` 를 새로 만든다 — 두 정본을 import 로만 가져와 대조하고, 판정을 안내 파일 목록·라벨·명령을 인자로 받는 함수로 뺀다(사본마다 기대값을 따로 적는 경로를 두지 않는다) | 소비: `romeo.close.DEFENSIVE_LABELS`·`romeo.close.SEAL_COMMAND`·`romeo.cli.build_parser` → 생산: `missing(paths, labels, command)` · `registered(parser, command)` | `python3 -m unittest tests.test_review_guidance_alignment -v` — 라벨을 지운 사본과 상수를 바꿔친 두 짝이 그 안에 있다 | `rm tests/test_review_guidance_alignment.py` |
| 2 | 안내 문서 셋에 실제로 적는다 (AC-4) | `core/workflows/review/SKILL.md` 7번과 두 어댑터 `review.md` 5·6번에 봉인 명령과 방어 검사 라벨·시점을 적는다 | 소비: 1 의 대조 규칙 → 생산: 없음 | 1 의 검사가 통과한다 | `git checkout -- core/workflows/review/SKILL.md adapters/` |
| 3 | 어댑터 산출물을 다시 만든다 (AC-9) | `bin/romeo compile` 로 `.claude/skills/review/SKILL.md` 와 `.agents/skills/review/SKILL.md` 의 managed block 을 갱신한다 | 소비: 2 의 원본 → 생산: 없음 | `bin/romeo compile --check` 가 exit 0 | `git checkout -- .claude/ .agents/` |
| 4 | 검토자 계약이 회차를 열지 않는다 (AC-5·AC-6) | `romeo/envelope.py` 의 `record_start` 가 `role` 을 받아 `reviewer` 이고 그 run 에 회차가 없으면 회차 대신 `reviewer_runs:` 에 남긴다. `romeo/run_unit.py` 에 그 목록을 읽고 쓰는 자리를 더한다 — `gate()` 가 읽는 `reviews:` 와 섞지 않는다 | 소비: `build_envelope` 의 `role` → 생산: `attempts.yaml` 의 `reviewer_runs:` | `tests/test_reviewer_attempt_isolation.py` 를 **새 모듈로** 만든다(기존 `tests/test_envelope.py` 에 더하면 그 모듈 명령이 이 단위 없이도 통과해 빈 검사가 된다 — 앞 단위에서 실측했다). 검토자만 만들면 `attempts` 0건, 연속 2회 실패 상태에서 검토자 계약을 만들어도 `gate()` 판정이 그대로 | `git checkout -- romeo/envelope.py romeo/run_unit.py` · `rm tests/test_reviewer_attempt_isolation.py` |
| 5 | 반박 검사가 목록 전체를 본다 (AC-7·AC-8) | `romeo/docs.py` 의 반박 파일 선택을 `next(...)` 에서 목록 순회로 바꾸고 각 파일의 `### AC-` 절을 합집합으로 모은다 | 소비: 없음 → 생산: 없음 | `tests/test_ac_rebuttal_multi.py` 를 **새 모듈로** 만든다(같은 이유). 두 파일이 AC 를 나눠 반박하면 경고 0건, 둘째를 `inputs:` 에서 빼면 그 AC 가 경고에 나온다 | `git checkout -- romeo/docs.py` · `rm tests/test_ac_rebuttal_multi.py` |

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

`check-1`·`check-2`·`check-3` 은 **판별 검사**다 — 이 단위가 없으면 실패해야 한다(승인 전에 셋 다 exit 1 을 실측했다).
`check-4`·`check-5`·`check-6`·`check-7` 은 **회귀 방지 검사**로, 이 단위 전후 양쪽에서 통과하는 것이 정상이다(AGENTS.core §11).
`check-4`(`compile --check`)가 회귀 쪽인 것은 승인 전 실측으로 확인했다 — 지금도 exit 0 이다. 그것이 막는 것은 **어댑터 원본을 고치고 컴파일을 잊는 것**이지 이 단위의 존재가 아니다.

`check-1` 이 담는 테스트는 AC-1(검사 안에 리터럴 0건) · AC-2(대조 규칙) · AC-3(라벨을 지운 사본과 상수를 바꿔친 두 짝) 셋이다.
`check-2` 는 AC-5·AC-6 을, `check-3` 은 AC-7·AC-8 을 담는다 — 둘 다 **새 모듈**이다. 기존 모듈에 케이스를 더하면 그 모듈 명령이 이 단위 없이도 통과해 빈 검사가 된다(앞 단위의 승인 전 프로브가 그 함정을 실측했다). `check-4` 는 AC-9 다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_review_guidance_alignment -v"
  - id: check-2
    command: "python3 -m unittest tests.test_reviewer_attempt_isolation -v"
  - id: check-3
    command: "python3 -m unittest tests.test_ac_rebuttal_multi -v"
  - id: check-4
    command: "bin/romeo compile --check"
  - id: check-5
    command: "bin/romeo validate"
  - id: check-6
    command: "bin/romeo integrity"
  - id: check-7
    command: "python3 -m unittest discover -s tests"
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
