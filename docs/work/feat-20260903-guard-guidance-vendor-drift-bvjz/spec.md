---
id: feat-20260903-guard-guidance-vendor-drift-bvjz
type: spec
title: 안내하는 자리가 요구하는 자리를 따라간다 — 가드 --note 안내 3곳·코어에 남은 집행 수단
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: low
status: active
approved_at: '2026-09-03T10:08:41+09:00'
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
created: '2026-09-03'
updated: '2026-09-03'
---

# 안내하는 자리가 요구하는 자리를 따라간다 — 가드 --note 안내 3곳·코어에 남은 집행 수단

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260903-guard-guidance-vendor-drift-bvjz --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 가드 승인 명령을 **안내하는** 절차 문서 3곳을 요구와 같은 형식으로 맞추고, `core/policy/execution-guards.yaml` 에 남은 집행 수단 사본(`enforcement:` 블록)을 걷어낸다. 두 어긋남을 각각 겨누는 검사를 같은 커밋에 넣는다.
- **왜 지금:** 절차 문서를 **지시대로 따르면 `exit 2` 로 막힌다** — 규칙을 지킨 실행이 막히고 지시를 무시한 실행만 통과한다. M3 의 남은 조각인 실제 T2 관통이 시작되면 §10 동결 때문에 그 안에서 이 안내를 고칠 수 없으므로 관통 **전에** 닫는다.
- **기대 결과:** 안내하는 자리와 요구하는 자리가 같은 형식을 말하고, 코어 정책 파일에 집행 수단이 남지 않는다. 그 일치가 검사로 유지되어 라벨이 바뀌면 검사가 먼저 깨진다.
- **수용 기준:**
  - [ ] AC-1 안내 3곳(`core/workflows/implement/SKILL.md` · `adapters/{claude,codex}/workflows/implement.md`)의 명령 예시가 `--note` 인자를 담는다. 지금은 셋 중 둘이 그 인자를 아예 빼고 안내한다.
  - [ ] AC-2 그 `--note` 값이 설명 라벨을 **일부만** 나열하지 않는다 — 라벨이 하나라도 나타나면 `required_explanation` 의 네 개가 전부 나타난다. 지금 `SKILL.md:57` 은 넷 중 둘만 적는다.
  - [ ] AC-3 그 검사가 라벨을 `core/policy/execution-guards.yaml` **에서 읽는다** — 검사 코드에 라벨 글자를 복사하지 않는다. 정책의 라벨을 바꾸면 검사가 그 즉시 새 라벨로 대조한다(§11).
  - [ ] AC-4 그 검사의 반례가 **그럴듯한 거짓 값**이다 — 빈 `--note` 가 아니라 네 항목 중 셋만 적은 안내가 실패하는 것을 보인다(§11).
  - [ ] AC-5 `core/policy/execution-guards.yaml` 에 최상위 `enforcement:` 키가 없고 그 파일 어디에도 런타임·도구 이름(claude·codex·orca·anthropic·openai·gemini)이 없다(C-C6). 걷어낸 값의 정본이 `.harness/bindings.yaml` 의 `permission_ceiling`·`roles[].enforcement` 임을 그 자리에 한 줄로 남긴다.
  - [ ] AC-6 그 삭제가 무엇도 깨뜨리지 않았음을 보인다 — 그 블록을 읽는 코드가 저장소에 없다는 실측을 증거로 남긴다(`romeo/policy.py` 는 `guards` 키만 읽는다).
  - [ ] AC-7 AC-1·AC-2·AC-5 를 겨누는 검사가 **고치기 전 트리에서 실패**하고 고친 뒤 통과하는 것을 양쪽으로 보인다(§11). 회귀 검사는 이 실측 대상이 아니며 검증 계획의 종류 표가 어느 쪽인지 적는다.
  - [ ] AC-8 `bin/romeo compile --check` 가 통과한다 — 어댑터 원문을 고치면 두 런타임의 지침 산출물이 함께 움직여야 한다. 한쪽만 바뀐 상태로 닫히지 않는다.
  - [ ] AC-9 `docs/planning/open-questions.md` 의 Q-44·Q-45 가 닫힌 것으로 갱신되고, 이 단위가 범위 밖으로 남긴 것(코어 나머지 6파일의 런타임 이름)이 새 항목으로 열린다(§12).
- **위험과 되돌리기:** 판정을 바꾸지 않는다 — 지금 막히는 것(빈 `--note`)은 그대로 막히고 안내가 요구를 따라올 뿐이다. 되돌리기는 커밋 되돌림 하나(`git revert <통합 커밋>`)이고, 지우는 `enforcement:` 블록은 읽는 코드가 없음을 AC-6 이 실측으로 보인다. 운영 데이터·외부 상태는 건드리지 않는다.
- **결정 필요:** 없음


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `core/workflows/implement/SKILL.md` (6번 가드 절) · `adapters/claude/workflows/implement.md` (5번) · `adapters/codex/workflows/implement.md` (5번) · `core/policy/execution-guards.yaml` (enforcement 블록 제거와 정본 포인터) · `tests/test_guard_guidance_alignment.py` (새 검사) · `.claude/skills/implement/SKILL.md` · `.agents/skills/implement/SKILL.md` (컴파일 산출물) · `docs/planning/open-questions.md` · `docs/work/feat-20260903-guard-guidance-vendor-drift-bvjz/`
- 영향을 받는 부분: 가드가 걸린 작업 단위의 구현자 실행 경로. 판정 기준은 그대로이고 안내 문구와 검사만 바뀐다. 이미 done 인 단위에는 소급하지 않는다.
- 바꾸지 않는 것(비범위): 집행 코드 (요구는 이미 옳게 집행된다) · CLI 의 도움말 (이미 네 항목 예시를 인쇄한다) · 런북 (§8.1·§8.2 는 이미 새 형식이다) · 정책 파일의 `required_explanation`·`approval`·`guards` (요구 자체는 옳다) · 코어 나머지 6파일의 런타임 이름 (정당한 언급과 위반을 구분하는 기준이 없다 — 새 질문으로 연다) · `TestVendorNeutral` 의 대상 목록 (확대는 같은 문제를 연다)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 안내가 요구를 따라오는지 보는 검사를 세운다 | `tests/test_guard_guidance_alignment.py` 신설. `core/policy/execution-guards.yaml` 의 `required_explanation` 라벨을 읽어, 대상 3파일에서 `evidence approve`·`evidence reject` 가 나오는 명령 예시 줄을 뽑아 (a) `--note` 인자를 담는지 (b) 그 값에 라벨이 하나라도 있으면 넷 다 있는지 본다. 반례 둘을 임시 파일로 만들어 실패를 보인다 — 라벨 셋만 적은 안내, `--note` 를 뺀 안내 | 소비: 없음 → 생산: `tests/test_guard_guidance_alignment.py` (라벨 로더 · 대상 파일 목록 상수) | `python3 -m unittest tests.test_guard_guidance_alignment -v` 가 **현재 트리에서 실패**한다 (단위 2 전) | `git revert` |
| 2 | 안내 3곳을 요구와 같은 형식으로 맞춘다 | `core/workflows/implement/SKILL.md` 6번의 `--note "<영향 범위·복구 방법>"` 를 네 라벨 전부를 담은 형식으로 고친다. `adapters/{claude,codex}/workflows/implement.md` 5번의 명령에 `--note` 인자를 더한다 (어댑터는 매핑 파일이므로 라벨 나열 대신 코어 절차의 형식을 가리켜도 되고, 그때는 AC-2 에 걸리지 않는다) | 소비: 단위 1 의 검사 → 생산: 세 문서의 새 명령 예시 | 단위 1 의 검사가 통과한다 | `git revert` |
| 3 | 코어 정책에서 집행 수단 사본을 걷어낸다 | `core/policy/execution-guards.yaml` 의 최상위 `enforcement:` 블록(86~95행)을 지우고, 그 자리에 정본이 `.harness/bindings.yaml` 의 `permission_ceiling`·`roles[].enforcement` 임을 한 줄 주석으로 남긴다. 지우기 전에 그 블록을 읽는 코드가 없음을 실측해 증거로 남긴다 | 소비: 없음 → 생산: 런타임 이름 없는 `execution-guards.yaml` | `! grep -qiE '(claude\|codex\|orca\|anthropic\|openai\|gemini)' core/policy/execution-guards.yaml` 가 exit 0 이고 `python3 -m unittest discover -s tests` 가 통과한다 | `git revert` |
| 4 | 두 런타임의 지침이 함께 움직인 것을 확인한다 | `bin/romeo compile` 로 `.claude/skills/implement/SKILL.md` · `.agents/skills/implement/SKILL.md` 를 재생성한다 (managed block 의 source sha 가 바뀐다) | 소비: 단위 2 의 어댑터 변경 → 생산: 갱신된 컴파일 산출물 2개 | `bin/romeo compile --check` 가 exit 0 | `git revert` |
| 5 | 열린 질문 장부를 실제 상태에 맞춘다 | `docs/planning/open-questions.md` 의 Q-44·Q-45 를 닫힌 것으로 갱신하고, 이 단위가 §12 로 남긴 「코어 나머지 6파일의 런타임 이름 — 정당한 언급과 위반을 구분하는 기준이 없다」를 새 항목으로 연다 | 소비: 단위 2·3 의 결과 → 생산: 갱신된 장부 | `bin/romeo validate` 가 exit 0 이고 새 항목의 번호가 기존과 겹치지 않는다 | `git revert` |

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

**판별 검사와 회귀 검사를 구분해 적는다**(§11). 판별 검사는 이 단위가 없으면 실패해야 하는 검사이고,
승인 전에 **현재 트리에서 실패하는 것**을 프로브로 확인했다. 회귀 검사는 양쪽에서 통과가 예상되므로
양쪽 실측의 대상이 아니다 — 현재 트리에서 통과하는 것만 확인했다.

| id | 종류 | 승인 전 프로브 (현재 트리 · 2026-09-03) |
| --- | --- | --- |
| check-1 | 판별 | 실행 불가 — 이 검사 모듈 자체가 단위 1 의 산출물이다(D-27). AC-8 이 base 트리 재현으로 대신한다 |
| check-2 | 판별 | exit 1 (`core/policy/execution-guards.yaml` 88·94행에 `claude:`·`codex:` 가 있다) |
| check-3 | 판별 | exit 1 (`adapters/claude/workflows/implement.md` 에 `--note` 가 없다) |
| check-4 | 판별 | exit 1 (`adapters/codex/workflows/implement.md` 에 `--note` 가 없다) |
| check-5~9 | 회귀 | 전부 exit 0 — `discover`·`validate`·`compile --check`·`doctor --strict`·`fixtures check` 실측 |

check-3·4 는 check-1 의 부분집합이지만 따로 둔다 — check-1 이 대상 목록을 좁히면 그 사실이 여기서 드러난다(§11).

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_guard_guidance_alignment -v"
  - id: check-2
    command: "! grep -qiE '(claude|codex|orca|anthropic|openai|gemini)' core/policy/execution-guards.yaml"
  - id: check-3
    command: "grep -q -- '--note' adapters/claude/workflows/implement.md"
  - id: check-4
    command: "grep -q -- '--note' adapters/codex/workflows/implement.md"
  - id: check-5
    command: "python3 -m unittest discover -s tests"
  - id: check-6
    command: "bin/romeo validate"
  - id: check-7
    command: "bin/romeo compile --check"
  - id: check-8
    command: "bin/romeo doctor --strict --scope repository"
  - id: check-9
    command: "bin/romeo fixtures check"
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
