---
id: feat-20260902-effort-proportional-review-yifh
type: spec
title: 작업 강도를 위험에 비례시킨다 — 검토자 오버레이·범위 밖 발견·회귀 검사 실측
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: low
status: done
approved_at: '2026-09-02T16:32:53+09:00'
approved_by: justjulliette0709
base_sha: null
closed_at: '2026-09-02T16:51:53+09:00'
parent: null
inputs: []
evidence: [evidence/run_2410bcf75836.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-02'
updated: '2026-09-02'
approval_history:
- {approved_at: '2026-09-02T16:11:01+09:00', approved_by: justjulliette0709, superseded_at: '2026-09-02T16:32:53+09:00',
  reason: '오버레이 조건에 uncertainty: [low] 를 더했다 — AC-1·AC-3 문장과 구현 단위 1·2행이 바뀌었다. 1차 승인본이 방법 미정(medium) 요청까지
    잡아 실제 세션 로그 fixture 가 검토자를 잃은 것을 fixture 대조가 exit 1 로 잡았다'}
---

# 작업 강도를 위험에 비례시킨다 — 검토자 오버레이·범위 밖 발견·회귀 검사 실측

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260902-effort-proportional-review-yifh --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 작업 강도를 위험에 비례시키는 규칙 3건. (1) 영향 반경이 작고 게이트가 없는 T1 에서 검토자를 끄는 오버레이 1행, (2) 요청 범위 밖에서 발견한 결함은 고치지 말고 열어 두는 조항, (3) 회귀 방지 검사는 승인 전 양쪽 실측 대상이 아니라는 한 줄.
- **왜 지금:** 작업 단위 17건 실측에서 15건이 T1 이었고 전부 검토자 왕복을 받았다. 그 15건은 모두 영역이 `tooling`·`docs` 인 하네스 자기 정비다. 사람이 매번 확정하는 `blast_radius` 가 깊이(profile)만 올리고 검토자·격리에는 아무 영향을 못 주기 때문에, 영향 반경이 작다고 확정한 작업도 큰 작업과 같은 코스를 돈다.
- **기대 결과:** 다음 단위부터, 영향 반경이 작고 게이트가 없는 T1 정비 작업은 검토자 왕복 없이 증거로만 닫힌다. 게이트가 하나라도 켜지면 검토자는 그대로 붙는다. 정비 단위가 요청 범위 밖으로 번지는 것은 조항이 막고, 판별력이 없는 검사를 두 상태에서 돌리던 관행은 사라진다.
- **수용 기준:**
  - [x] AC-1 `unit=T1 · blast_radius=small · uncertainty=low · gates 없음 · mode=delivery · intent=write` 인 분류에서 라우터가 `reviewer: none` 을 낸다.
  - [x] AC-2 같은 분류에 hard gate 가 하나라도 켜지면 `reviewer` 가 `opposite-runtime-readonly` 로 유지된다 — 새 오버레이가 게이트가 켠 검토자를 덮어쓰지 않는다.
  - [x] AC-3 `blast_radius` 가 medium·large 이거나 `uncertainty` 가 low 가 아니거나 `unit` 이 T2 이면 검토자가 유지된다.
  - [x] AC-4 구현자 계약의 「요청 범위 밖 수정」 금지 항목과 §11 의 회귀 검사 문장이 두 런타임 지침 파일에 똑같이 실린다.
- **위험과 되돌리기:** 이 변경은 안전 장치를 **낮추는** 방향이다 — 검토자가 잡던 결함을 앞으로 증거만으로 걸러야 한다. 완화는 조건을 좁게 잡은 것이다(게이트 없음 + 영향 반경 작음 + delivery + write 를 모두 만족할 때만). 되돌리기: `core/policy/packages.yaml` 에서 `blast.small.no-reviewer` 오버레이 행을 지우고 `bin/romeo compile` 을 다시 돌린다. 이미 닫힌 단위에는 영향이 없다.
- **결정 필요:** 없음

## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `core/policy/packages.yaml` · `core/principles/AGENTS.core.md` · `core/roles/implementer.yaml` · `tests/test_policy.py` · `tests/test_roles_envelopes.py` · `CLAUDE.md` · `AGENTS.md` (뒤 둘은 `romeo compile` 산출물)
- 영향을 받는 부분: 라우터의 `reviewer` 계산(`romeo/policy.py` 의 오버레이 루프 — 코드는 고치지 않는다). 앞으로 만들어지는 작업 계약의 검토자 배정.
- 바꾸지 않는 것(비범위): `isolation`(worktree 는 그대로 붙는다) · `romeo/policy.py` 의 코드 · 기존 오버레이 · 차단 카탈로그 · 이미 닫힌 작업 단위

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 영향 반경이 작고 게이트가 없는 T1 에서 검토자를 끈다 | `core/policy/packages.yaml` 의 `overlays:` 끝에 `blast.small.no-reviewer` 행 1개 추가 (`tier: optional_overlay` · `when: {unit: [T1], blast_radius: [small], uncertainty: [low], gates: none, mode: [delivery], intent: [write]}` · `set_reviewer: none`) | 소비: 없음 → 생산: 오버레이 id `blast.small.no-reviewer` | check-1 | 그 행을 지운다 |
| 2 | 그 오버레이가 게이트가 켠 검토자를 덮어쓰지 않고, 방법이 미정인 요청을 잡지 않는 것을 고정한다 | `tests/test_policy.py` 에 `TestBlastSmallDropsReviewer` 추가 — 발동/게이트 반례/불확실성 반례/반경/T2/모드/의도 | 소비: 오버레이 id → 생산: 없음 | check-1 | 클래스를 지운다 |
| 3 | 요청 범위 밖 결함을 고치지 않고 열어 두게 한다 | `core/principles/AGENTS.core.md` 에 §12 절 추가 + `core/roles/implementer.yaml` 의 `forbidden` 에 항목 1줄 | 소비: 없음 → 생산: forbidden 항목 문구 | check-2 | 절과 항목을 지운다 |
| 4 | 회귀 방지 검사를 양쪽 실측 대상에서 뺀다 | `core/principles/AGENTS.core.md` §11 의 「반례는 빈 값이 아니라」 문단 끝에 한 문장 추가 | 소비: 없음 → 생산: 그 문장 | check-2 | 문장을 지운다 |
| 5 | 위 셋이 두 런타임 지침에 똑같이 실린 것을 고정한다 | `tests/test_roles_envelopes.py` 에 `TestOutOfScopeFindingRule` 추가 + `bin/romeo compile` 재생성 | 소비: forbidden 항목 문구·§11 문장 → 생산: 없음 | check-2 · check-3 | 클래스를 지우고 compile 을 되돌린다 |

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

**양쪽으로 보인다(AGENTS.core §11).** check-1·2 는 **판별 검사**다 — 기존 상태(이 단위 직전 `656c932`)에서 실패하고 구현 뒤 통과하는 것을 승인 전에 양쪽으로 보인다. check-1 은 새 테스트 클래스 이름을 박아 기존 상태에서 수집 자체가 실패하게 했고, 그 안의 게이트 반례(`gates: [privacy-security]` 인데 검토자가 유지되는가)가 이 단위의 **그럴듯한 거짓 값** 반례다 — `gates: none` 조건을 빠뜨린 구현은 형태가 그럴듯하지만 게이트가 켠 검토자를 꺼버리고, 그 구현에서 이 검사가 실패한다. **1차 승인본은 `uncertainty` 를 보지 않았고, 실제 세션 로그에서 온 fixture `fx-coupang-rocket-badge-automation-plan`(브라우저 자동화·외부 연동·방법 미정)이 검토자를 잃는 것을 check-4 가 exit 1 로 잡았다** — 그래서 조건에 `uncertainty: [low]` 를 더해 재승인했다. check-3~6 은 **회귀 방지 검사**이고 양쪽에서 통과가 예상되므로 판별 실측 대상이 아니다(이 단위가 §11 에 더하는 규칙이 그것이다).

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_policy.TestBlastSmallDropsReviewer"
  - id: check-2
    command: "python3 -m unittest tests.test_roles_envelopes.TestOutOfScopeFindingRule"
  - id: check-3
    command: "bin/romeo compile --check"
  - id: check-4
    command: "bin/romeo route --fixtures fixtures/requests --report"
  - id: check-5
    command: "python3 -m unittest discover -s tests"
  - id: check-6
    command: "bin/romeo validate"
```


## 증거

close PASS · 2026-09-02T16:51:53+09:00 · HEAD 9dda8e9c7d88 · 검사 기록 run_2410bcf75836

- [evidence/run_2410bcf75836.yaml](evidence/run_2410bcf75836.yaml) — exit codes [0, 0, 0, 0, 0, 0] (검사 기록)
