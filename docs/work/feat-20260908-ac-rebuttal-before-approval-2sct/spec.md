---
id: feat-20260908-ac-rebuttal-before-approval-2sct
type: spec
title: 승인 전 반대 독자 — 확인란의 수용 기준을 다른 런타임이 반박하고, 전칭 표현은 검사기가 경고한다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
status: draft
approved_at: null
approved_by: null
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-08'
updated: '2026-09-08'
---

# 승인 전 반대 독자 — 확인란의 수용 기준을 다른 런타임이 반박하고, 전칭 표현은 검사기가 경고한다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260908-ac-rebuttal-before-approval-2sct --by <승인자>` 로 기록한다.
> **착수 시점:** `feat-20260907-context-one-hop-resume-w5jq` 관통이 닫힌 뒤(§10 동결). 정비 후보 순서에서 **가장 앞**이다(사용자 지시 2026-09-08).

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 승인 요청 **앞에** 확인란의 수용 기준(AC)을 읽는 반대 독자를 둔다. ① `/plan` 절차에 「반박 읽기」 단계가 생긴다 — 구현하지 않는
  다른 런타임의 읽기 전용 실행에 확인란만 넘겨 AC 마다 「반례·검토 시점·표현」 세 줄을 받고, 그 결과를 `docs/work/<id>/inputs/ac-rebuttal-<날짜>.md` 에
  등록한다(판정이 아니라 입력이다 — 사람이 읽고 문장을 고친다). ② `romeo validate` 가 확인란 AC 줄의 전칭 표현(정책표 목록: 「어떤 …이든」「전부」「모든」「하나라도」「항상」 등)을
  `AC_UNIVERSAL` 로 경고한다. ③ `romeo approve` 가 반박 기록이 없거나 AC 를 덮지 못하면 `AC_UNREBUTTED` 로 경고한다. 둘 다 **경고까지만**이다 — 승인을 막지 않는다(K-31).
- **왜 지금:** 최근 15개 단위 중 1회차에 닫힌 것은 3개다. 1회차 FAIL 의 과반은 산출물이 아니라 **AC 문장의 결함**(과잉 명세·검토 시점에 참일 수 없는 명제·
  반대 판정·전칭 문장 — 6번째가 w5jq AC-5 로 2회 연속)이었고, 전부 D-80 재승인이나 재작업으로만 닫혔다. 그 문장을 반대 입장에서 처음 읽는 사람이 **검토자**인데
  그 자리는 구현 뒤라, 회차 하나(25~40분)가 매번 그 대가로 나간다. 승인 전 프로브는 검사의 판별력만 실측하고 문장은 실측하지 않는다.
  1회차에 닫힌 단위 중 하나(z5mv)는 승인 전 「세 렌즈 반박」을 손으로 했다 — 효과는 봤지만 절차도 기록 자리도 없어 재현되지 않았다.
- **기대 결과:** 승인 요청 직전에 반박 파일 하나가 단위 폴더에 서고, 거기 적힌 반례로 고친 AC 가 「반영」 절에 남는다. 문장을 쓰는 순간 `romeo validate` 가
  전칭 표현을 경고로 보여 주고, `romeo approve` 는 반박이 빠진 AC 를 이름으로 보여 준다. 1회차 통과율이 오르는지는 이 단위가 아니라 그 뒤 10개 단위의 관측이 말한다.
- **수용 기준:**
  - [ ] AC-1 `romeo validate` 가 확인란의 AC 항목(`- [ ] AC-n`/`- [x] AC-n` 으로 시작하는 항목의 이어지는 줄까지)에서 정책표 `core/policy/packages.yaml` 의
        `ac_lint.universal_patterns` 에 적힌 패턴을 찾으면 경고 `AC_UNIVERSAL AC-n «맞은 패턴»` 을 인쇄하고 종료 코드는 그대로다(경고는 오류가 아니다).
        패턴은 정책표에서 **읽는다** — 검사가 패턴 하나를 정책표에서 지우면 그 경고가 사라지는 것을 확인한다. 검사에 쓴 닫힌 집합 문장 2개(「A·B·C 세 파일」「AC-1~7」)에는 경고가 없다.
  - [ ] AC-2 `romeo approve` 가 spec frontmatter `inputs:` 에서 단위 폴더 기준 `inputs/ac-rebuttal-*.md` 를 찾아, 파일이 없으면 경고 `AC_UNREBUTTED` 뒤에 확인란의 AC id 목록을
        그대로, 있으면 그 파일에 `### AC-n` 절이 없는 AC id 만 인쇄한다. 승인은 기록된다(`status: active`·`approved_at`) — 경고까지만이다. 파일이 있고 확인란의 AC 마다 절이 있으면
        그 경고는 인쇄되지 않는다.
  - [ ] AC-3 `core/workflows/plan/SKILL.md` 절차에 「반박 읽기」 단계가 「내용 채우기」 뒤·「승인 요청」 앞에 있고, 그 본문이 기록 경로 규약(`inputs/ac-rebuttal-<YYYYMMDD>.md`)과
        세 항목(반례·검토 시점·표현)과 「판정이 아니라 입력」을 말한다. 검사가 **그 단계 본문만** 읽어 경로 접두 `inputs/ac-rebuttal-` 을 뽑고 `romeo approve` 가 찾는 접두와
        같은 문자열인지 본다 — 요구하는 자리와 보는 자리가 한 문자열이다(§11).
  - [ ] AC-4 반박 브리프 정본 `adapters/orca/prompts/ac-rebuttal-brief.md` 가 있고 자리표시자는 `<id>` 하나다. 두 런타임 매핑 `adapters/claude/workflows/plan.md`·`adapters/codex/workflows/plan.md` 에
        반박 실행 한 줄이 있다 — 읽기 전용 강제 수단은 `.harness/bindings.yaml` 의 검토자 enforcement 값을 옮겨 적고 출력은 `-o`/파일로 받아 `inputs/` 에 둔다.
        compile 산출물(`.claude/skills/plan/SKILL.md`·`.agents/skills/plan/SKILL.md`)이 같은 줄을 담고 `bin/romeo compile --check` 가 통과한다. `core/` 파일에는 도구명·모델명이 없다(C-C6).
  - [ ] AC-5 두 경고 코드 `AC_UNIVERSAL`·`AC_UNREBUTTED` 가 `core/policy/packages.yaml` `warnings:` 카탈로그에 한 줄 설명과 함께 있고, 검사가 카탈로그에서 코드를 **읽어**
        validate·approve 출력의 코드 문자열과 대조한다.
  - [ ] AC-6 기존 검사 파일은 바뀌지 않고 `python3 -m unittest discover -s tests` 가 종료 코드 0 이다. 기존 spec 2건 — `feat-20260907-context-one-hop-resume-w5jq`(AC-5)·
        `feat-20260907-judge-revision-base-sha-pwt8`(AC-3) — 에서 `AC_UNIVERSAL` 이 실제로 인쇄되고 그 `validate` 의 종료 코드는 0 이다.
  - [ ] AC-7 이 단위 자신이 절차의 첫 실사용이다 — 승인 전에 코디네이터가 구현 단위 4 의 브리프 문안으로 반박을 한 번 돌려 `inputs/ac-rebuttal-<날짜>.md` 를 등록했고,
        그 반박으로 고친 AC 가 있으면 그 파일 끝 「반영」 절에 AC 번호와 무엇을 고쳤는지가 있다(없으면 「반영: 없음」).
  - [ ] AC-8 `docs/planning/open-questions.md` 의 Q-87(1회차 통과율·반대 독자 부재)이 해소 표기되고, 이번 작업이 발견했으나 고치지 않은 것이 새 행으로 열린다.
        `docs/planning/progress.md` 「지금 상태」가 이 단위를 활성 단위로 가리킨다.
- **위험과 되돌리기:** 경고 두 개와 절차 단계 하나, 브리프 파일 하나가 늘어난다 — 차단·판정 자리(close·envelope·evidence)는 바뀌지 않는다. 기존 단위의 `validate` 출력에
  경고가 더 붙을 수 있다(오류 아님). 거짓 양성이 나면 정책표 패턴 목록만 고친다 — 경고라 정상 경로를 막지 않는다(charter M4 위험 「드러내기가 차단으로 자라는 것」).
  되돌리기는 `git revert <통합 커밋>`. 알려진 한계: ① 반박은 문장을 읽을 뿐 구현을 보지 않는다 — 산출물 결함(3mcv·w5jq 2회차)은 그대로 검토자의 몫이다 ·
  ② 경고를 차단으로 올리는 것은 10건 관측 뒤의 별도 결정이다 · ③ 반박 실행의 비용(약 5분 가정)은 착수 시 실측한다.
- **결정 필요:** 없음 — 착수 순서(정비 후보 맨 앞)와 「경고까지만」은 사용자가 2026-09-08 에 정했다.


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `core/policy/packages.yaml` · `romeo/validate.py` · `romeo/docs.py` · `romeo/cli.py` · `core/workflows/plan/SKILL.md` · `adapters/orca/prompts/ac-rebuttal-brief.md`(신규) · `adapters/claude/workflows/plan.md` · `adapters/codex/workflows/plan.md` · `.claude/skills/plan/SKILL.md` · `.agents/skills/plan/SKILL.md` · `.harness/compiled.yaml` · `tests/test_ac_rebuttal.py`(신규) · `docs/planning/open-questions.md` · `docs/planning/progress.md` · `docs/work/feat-20260908-ac-rebuttal-before-approval-2sct/` (뒤 컴파일 산출물 셋은 어댑터 매핑을 고치면 `romeo compile` 이 다시 만든다)
- 영향을 받는 부분: `/plan` 절차의 승인 직전 단계(단계 번호가 하나 밀린다 — 승인 요청은 9) · `romeo validate` 의 경고 출력(모든 단위 문서) · `romeo approve` 의 출력 · 정책표 `packages.yaml` 의 스키마(새 키 `ac_lint`)
- 바꾸지 않는 것(비범위): `romeo/close.py`·`romeo/envelope.py`·`romeo/evidence.py`·`romeo/run_unit.py`(판정·계약·증거) · 승인 차단 `blocks`(경고를 차단으로 올리지 않는다) · 검토자 절차·브리프(`core/workflows/review/`·`adapters/orca/prompts/reviewer-brief.md`) · 승인 전 프로브 절차(검사의 양쪽 실측은 그대로) · `core/principles/AGENTS.core.md` · 다른 열린 질문(Q-64·69·70·82~86)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 요구가 정책표에 산다 | `core/policy/packages.yaml` 에 `ac_lint:` 절 — `universal_patterns:` 정규식 목록(초기값: `어떤 .{1,12}이든` · `어느 .{1,12}(이)?든` · `전부` · `모든` · `하나라도` · `하나(가\|만) .{1,20}도` · `항상` · `언제나` · `어떤 경우에도`)과 `rebuttal_prefix: inputs/ac-rebuttal-` · `rebuttal_heading: "### AC-"`. `warnings:` 카탈로그에 `AC_UNIVERSAL`(「확인란의 수용 기준에 전칭 표현이 있다 — 반례가 무한하다. 닫힌 집합을 열거하거나 파일 단위 격리처럼 달성 가능한 형태로 고친다」)·`AC_UNREBUTTED`(「승인 전 반박 기록이 없거나 이 AC 를 덮지 못한다 — 반박 읽기 단계를 밟는다」) | 소비: 없음 → 생산: `load_policy()["packages"]["ac_lint"]` 의 `universal_patterns: list[str]`·`rebuttal_prefix: str`·`rebuttal_heading: str` · `warnings` 의 두 코드 | check-1 · check-7 | `git revert` |
| 2 | 문장을 쓰는 순간 전칭 표현이 보인다 | `romeo/validate.py` — `ac_items(body) -> list[tuple[str, str]]`(확인란 절에서 `- [ ] AC-n`/`- [x] AC-n` 으로 시작하는 항목과, 다음 `- [` 항목이나 절 끝 전까지의 이어지는 줄을 합친 문장) 을 더하고, `validate_doc` 이 `ac_items` 마다 정책표 패턴을 `re.search` 해 맞으면 `warnings.append(f"AC_UNIVERSAL {ac} «{matched}»")`. 확인란 절이 없으면 아무것도 하지 않는다. 종료 코드·errors 는 손대지 않는다 | 소비: 1 의 `ac_lint.universal_patterns` → 생산: `romeo.validate.ac_items(body)`(3 이 재사용) · 경고 문자열 `AC_UNIVERSAL AC-n «패턴»` | check-1 · check-4 · check-5 | `git revert` |
| 3 | 승인 시점에 반박 누락이 보인다 | `romeo/docs.py` — `rebuttal_warnings(udir, fm, body, policy) -> list[str]`: `fm["inputs"]` 중 `rebuttal_prefix` 로 시작하는 항목을 단위 폴더 기준으로 풀어 첫 파일을 읽고, `rebuttal_heading` 으로 `### AC-n` 절을 모아 `ac_items(body)` 의 id 와 대조 — 파일 없음이면 `["AC_UNREBUTTED " + ", ".join(ids)]`, 절이 없는 id 가 있으면 그 id 만, 전부 있으면 `[]`. `approve_unit` 은 승인을 기록한 뒤 이 목록을 반환값에 싣지 않고 `cmd_approve`(`romeo/cli.py`)가 같은 함수를 불러 `WARN <문장>` 으로 인쇄한다 — 경고는 종료 코드를 바꾸지 않는다 | 소비: 1 의 `rebuttal_prefix`·`rebuttal_heading` · 2 의 `ac_items` → 생산: `romeo.docs.rebuttal_warnings(...)` · approve 출력의 `WARN AC_UNREBUTTED …` 줄 | check-2 · check-3 | `git revert` |
| 4 | 절차·브리프·매핑이 같은 변경에서 그 규칙을 말한다(§11) | `core/workflows/plan/SKILL.md` 절차 7 뒤에 새 8 「**반박 읽기.** 승인을 요청하기 전에 확인란의 수용 기준을 **구현하지 않는 다른 런타임의 읽기 전용 실행**에 넘겨 AC 마다 세 줄을 받는다 — 「반례:」(그럴듯한 거짓 값 하나 · 없으면 「없음」과 이유) · 「검토 시점:」(구현이 끝난 검토 시점에 참일 수 있는 명제인가 — 사후 관측 불가·시간 순서·다른 경우의 부수 문장이면 지적) · 「표현:」(전칭 표현·열거되지 않은 집합·한 문장에 두 경우가 있으면 지적). 결과는 `docs/work/<id>/inputs/ac-rebuttal-<YYYYMMDD>.md` 에 두고 frontmatter `inputs:` 로 등록한다(K-62). 반박은 판정이 아니라 입력이다 — 읽고 문장을 고친 뒤 승인을 요청하고, 고친 AC 는 그 파일 끝 「반영」 절에 적는다. `romeo approve` 는 이 파일이 없거나 절이 없는 AC 가 있으면 `AC_UNREBUTTED` 로 경고한다(막지 않는다 — K-31). `romeo validate` 의 `AC_UNIVERSAL` 은 같은 것을 문장을 쓰는 시점에 먼저 보여 준다」, 옛 8(승인 요청)은 9 로. `adapters/orca/prompts/ac-rebuttal-brief.md` 신규 — 「너는 작업 단위 `<id>` 의 **반대 독자**다. 아래 확인란만 읽는다 — 저장소를 읽거나 검색해도 되지만 아무것도 쓰지 않고 검사·빌드를 실행하지 않는다. 판정을 내지 않는다」 + AC 마다 `### AC-n` / 반례 / 검토 시점 / 표현 형식 + 「마지막에 `## 요약` 으로 고쳐야 할 AC 를 나열한다. 문장을 대신 써 주지 않는다」 + 구분선 뒤에 확인란이 이어진다는 문장. `adapters/claude/workflows/plan.md`·`adapters/codex/workflows/plan.md` 에 한 줄 — 「반박 읽기(절차 8)는 검토자 런타임의 읽기 전용 비대화형 실행으로 한다: `<bindings 의 reviewer enforcement 형태> -o docs/work/<id>/inputs/ac-rebuttal-<날짜>.md "$(cat adapters/orca/prompts/ac-rebuttal-brief.md; sed -n '/^## 확인란/,/^## 변경 범위/p' docs/work/<id>/spec.md)"` — 자기 런타임이 검토자면 상대 런타임으로」(도구명은 어댑터에만). `bin/romeo compile` 로 산출물 둘·`.harness/compiled.yaml` 갱신 | 소비: 1·3 의 접두 문자열 → 생산: 없음 | check-3 · check-6 · check-9 · check-11 | `git revert` |
| 5 | 판별 검사를 더한다 | 새 파일 `tests/test_ac_rebuttal.py` — `TestUniversalLint`(임시 spec 으로 전칭 문장 3개 → 각 `AC_UNIVERSAL AC-n` 경고 · 닫힌 집합 문장 2개 → 경고 없음 · 임시 하네스 사본의 정책표에서 패턴 하나를 지우면 그 경고가 사라진다 · errors 없음·exit 0), `TestApproveWarnsUnrebutted`(임시 저장소 T0 단위 — `TestVerticalSlice` 형 — 에 확인란 AC 3개: 반박 파일 없음 → `WARN AC_UNREBUTTED AC-1, AC-2, AC-3` 이고 status active · 절 2개만 있는 파일을 `inputs:` 로 등록 → `AC-3` 만 · 3개 전부 → 경고 없음 · `--json` 아님), `TestProcedureAndAdapters`(절차 본문에서 「반박 읽기」 단계를 찾아 그 단계 본문만에서 접두를 뽑아 정책표 `rebuttal_prefix` 와 같다 · 단계가 「승인 요청」 앞에 있다 · 브리프 파일의 자리표시자가 `<id>` 뿐 · 두 매핑과 두 산출물에 `ac-rebuttal` · 카탈로그의 두 코드가 validate/approve 출력 코드와 같다 · `core/` 아래 새 문장에 도구명 없음). 기존 검사는 한 줄도 고치지 않는다 | 소비: 1~4 → 생산: 검사 3 클래스 | check-1~3 · check-10 | 해당 검사만 되돌린다 |
| 6 | 이 단위가 첫 실사용이고 기록이 갱신된다 | 승인 전(코디네이터): 구현 단위 4 의 브리프 문안 + 이 spec 의 확인란을 검토자 런타임 읽기 전용 실행에 넘겨 `inputs/ac-rebuttal-<날짜>.md` 를 만들고 frontmatter `inputs:` 에 등록, 고친 AC 를 「반영」 절에. 구현자: `docs/planning/open-questions.md` Q-87 행 해소 표기(취소선 + 「해소(날짜, 이 단위 id)」 + 무엇으로 닫혔나) · 발견했으나 고치지 않은 것을 새 행으로 · `docs/planning/progress.md` 「지금 상태」 활성 단위·다음 행동 줄 갱신(예산 30줄·2KB) | 소비: 4 의 브리프 → 생산: `inputs/ac-rebuttal-<날짜>.md` | check-8 · 검토자 읽기(AC-7·AC-8) | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 하네스 저장소 **자신**을 대상으로 하는 작업 단위이므로 하네스 자신의 검사(`unittest discover`·`compile --check`·`validate`)가 정당하다.

**종료 코드 자체가 조건이다.** 검사에 적는 것은 `id` 와 `command` 둘뿐이고, 그 명령의 종료 코드 0 이 통과다. 확인하고 싶은 조건은 **명령으로** 쓴다. `|| true` 를 붙이지 않는다. 부정 조건은 `!` 로 쓴다.

**판별 검사와 회귀 방지 검사의 구분(§11).** **판별 검사는 check-1~check-4·check-6~check-8 이고**, 착수 시 승인 전에 기존 상태·가상 완료 상태 양쪽에서 실행해 각각 실패·통과를 보인다.
check-5·check-9~check-11 은 **회귀 방지 검사**다 — 양쪽에서 통과하는 것이 정의다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_ac_rebuttal.TestUniversalLint"
  - id: check-2
    command: "python3 -m unittest tests.test_ac_rebuttal.TestApproveWarnsUnrebutted"
  - id: check-3
    command: "python3 -m unittest tests.test_ac_rebuttal.TestProcedureAndAdapters"
  - id: check-4
    command: "bin/romeo validate docs/work/feat-20260907-context-one-hop-resume-w5jq | grep -q 'AC_UNIVERSAL AC-5'"
  - id: check-5
    command: "bin/romeo validate docs/work/feat-20260907-context-one-hop-resume-w5jq"
  - id: check-6
    command: "grep -q 'inputs/ac-rebuttal-' core/workflows/plan/SKILL.md && grep -q 'ac-rebuttal' adapters/claude/workflows/plan.md && grep -q 'ac-rebuttal' adapters/codex/workflows/plan.md && grep -q 'ac-rebuttal' .claude/skills/plan/SKILL.md && grep -q 'ac-rebuttal' .agents/skills/plan/SKILL.md"
  - id: check-7
    command: "grep -q 'AC_UNIVERSAL' core/policy/packages.yaml && grep -q 'AC_UNREBUTTED' core/policy/packages.yaml && grep -q 'universal_patterns' core/policy/packages.yaml"
  - id: check-8
    command: "ls docs/work/feat-20260908-ac-rebuttal-before-approval-2sct/inputs/ac-rebuttal-*.md && grep -q '^### AC-1' docs/work/feat-20260908-ac-rebuttal-before-approval-2sct/inputs/ac-rebuttal-*.md"
  - id: check-9
    command: "bin/romeo compile --check"
  - id: check-10
    command: "python3 -m unittest discover -s tests -q"
  - id: check-11
    command: "python3 -m unittest tests.test_doc_commands tests.test_find_reuse tests.test_context_resume"
```

**각 검사가 무엇을 보는가**

| id | 종류 | 무엇이 참이어야 통과인가 | 반례(그럴듯한 거짓 값) |
| --- | --- | --- | --- |
| check-1 | **판별** | 전칭 문장 3개가 각각 경고되고, 닫힌 집합 문장은 경고되지 않으며, 정책표에서 패턴을 지우면 경고가 따라 사라진다 | 패턴을 코드에 하드코딩한 구현 — 정책표를 고쳐도 경고가 그대로다(요구하는 자리와 보는 자리가 다르다) |
| check-2 | **판별** | 반박 파일 없음·부분·전부 세 경우의 경고가 각각 「전체 목록」「빠진 id」「없음」이고 승인은 세 경우 모두 기록된다 | 파일 존재만 보고 절을 대조하지 않는 구현 — 빈 파일이 통과한다. 또는 경고를 오류로 올려 승인을 막는 구현 |
| check-3 | **판별** | 절차 단계 본문의 접두·정책표의 접두·approve 가 찾는 접두가 한 문자열이고, 브리프·매핑·산출물·카탈로그가 같은 변경에 있다 | 절차에는 `inputs/rebuttal-` 로 적고 approve 는 `inputs/ac-rebuttal-` 를 찾는 구현 — 지시대로 쓴 사람이 경고를 받는다 |
| check-4 | **판별** | w5jq 의 AC-5(「파일 하나가 깨져도」)가 실제 문서에서 경고된다 | 합성 문장만 잡고 실제 문서의 줄바꿈이 있는 항목(이어지는 줄)은 못 잡는 구현 |
| check-5 | 회귀 방지 | 경고가 붙어도 `validate` 는 exit 0 이다 | — |
| check-6 | **판별** | 절차·매핑 2·산출물 2 가 반박 규약을 말한다 | 코어만 고치고 컴파일하지 않은 상태 |
| check-7 | **판별** | 정책표에 패턴 목록과 두 경고 코드가 있다 | 카탈로그 없이 코드에서만 문자열을 만드는 구현 |
| check-8 | **판별** | 이 단위 자신의 반박 파일이 등록돼 있고 AC-1 절이 있다 | 절차를 만들면서 자기 단위에는 적용하지 않은 상태 |
| check-9 | 회귀 방지 | 어댑터 매핑 변경이 산출물과 어긋나지 않는다 | — |
| check-10 | 회귀 방지 | 기존 검사가 하나도 깨지지 않는다(단계 번호 변경 포함) | — |
| check-11 | 회귀 방지 | 절차 1단계 검사(M1·M2)와 문서 예시 대조가 단계 삽입 뒤에도 통과한다 | — |

**재실행 시간** — check-10 약 170초(929건 + 새 검사), 나머지 각 1~5초. `romeo close` 의 재실행 상한 600초 안이다.

**승인 전 실측** — 착수 시 한다. 기존 상태에서 판별 검사 7건(check-1~4·6~8)이 exit 1 이어야 하고(검사 모듈 없음·경고 없음·규약 문구 없음·반박 파일 없음),
가상 완료 상태에서 7건 전부 exit 0 이어야 한다. 그 실측 결과와 프로브 워크트리 이름·base 를 이 문단에 적은 뒤 승인을 요청한다. 시제품은 `inputs/probe-<날짜>.patch` 로 넘긴다.


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
