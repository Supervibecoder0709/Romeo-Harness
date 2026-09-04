---
id: feat-20260904-m2-router-foreign-repo-ct5h
type: spec
title: 라우터가 남의 저장소에서 돈다 — 대상 저장소의 실제 요청 1건을 승인까지
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: deep
blast_radius: medium
uncertainty: high
status: done
approved_at: '2026-09-05T01:19:19+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-09-05T01:57:26+09:00'
parent: init-20260904-attach-payload-manual-rreq
inputs: [../init-20260904-attach-payload-manual-rreq/charter.md, observations.md]
evidence: [evidence/run_2d9f8a17e34d.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.high->deep', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-04'
updated: '2026-09-05'
approval_history:
- {approved_at: '2026-09-04T22:46:10+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-05T00:07:30+09:00',
  reason: '검토자 FAIL AC_UNMET — 확인란이 GitHub issue 14번을 관통 대상으로 고정했으나, 그 이슈의 산출물 4종이 이미 실재하는 것을 실행이 실측해
    사용자가 CLAUDE.md 라우팅 충돌 해소로 대상을 바꿔 확정했다(2026-09-04). 원인이 산출물이 아니라 완료 정의여서 확인란과 AC-4 만 고쳤다 — 산출물은 그대로다'}
- {approved_at: '2026-09-05T00:07:30+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-05T01:19:19+09:00',
  reason: '2회차 검토자 FAIL AC_UNMET — 런북 인용(CLAUDE.md:76)을 증거 명령의 sed 범위(65,67p;72p)가 인쇄하지 않았다. 원인이 숫자 오기가
    아니라 요구하는 자리와 보는 자리가 각각 하드코딩된 구조(§11)여서, 범위를 맞추는 대신 AC-5 를 AC-2 와 같은 「런북에서 읽어 대조」 패턴으로 다시 썼다(사용자 확정
    2026-09-05)'}
---

# 라우터가 남의 저장소에서 돈다 — 대상 저장소의 실제 요청 1건을 승인까지

> 깊이 **Deep** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260904-m2-router-foreign-repo-ct5h --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 부착된 대상 저장소(`My-Automated-Worker/instagram-dm-sender`)에서 Romeo 라우터를 실제로 돌려, 그 저장소의 실제 요청 1건을 분류하고 사람 승인까지 세운다. **어느 요청인지는 실행 중에 정해진다** — 승인 시점에 고른 후보(GitHub issue 14번)가 이미 구현돼 있으면 다른 요청으로 바꾸고, 그 사실을 실측으로 적는다(아래 「결정 필요」). charter `init-20260904-attach-payload-manual-rreq` 의 M2 다.
- **왜 지금:** M1 이 부착을 파일 목록과 종료 코드로 고정했지만 **그 부착 위에서 라우터가 돈 적은 없다**. 부착이 성립했다는 것과 라우터가 그 저장소에서 일한다는 것은 다른 주장이고, 지금 참인 것은 앞의 것뿐이다. 그리고 대상 저장소에 `bin/`·`romeo/` 가 없다는 것은 이미 런북에 적혀 있다(Q-54) — 그것이 실제로 무엇을 막는지는 돌려 봐야 안다.
- **기대 결과:** 대상 저장소에 `docs/work/<id>/` 가 서고 `status: active` 로 승인되며, 그 단위의 `facets` 에 `tooling`·`docs` 아닌 값이 하나 이상 있다 — 하네스가 처음으로 자기 도구·문서가 아닌 영역(`security`)의 일을 분류한다. 라우터를 남의 저장소에서 돌리는 절차가 런북 하나에 적히고, 그 세 조건을 **문서에서 읽어** 판정하는 검사가 선다. 한 `CLAUDE.md` 안의 BMad·Romeo 두 라우팅 규칙이 만나는 자리가 실제 인용으로 기록된다 — **충돌이 없다는 관측도 결과다**(K-51).
- **수용 기준:**
  - [x] AC-1 런북 `scenarios/11-router-foreign-repo.md` 가 서고 다섯 절 — 「어디서 실행하는가」·「무엇이 대상 저장소에 서는가」·「두 라우팅 규칙이 만나는 자리」·「검증」·「되돌리기」 — 을 전부 담는다.
  - [x] AC-2 그 런북의 「검증」 절이 M2 의 완료 조건을 **조건 id 로** 고정하고, `tests/test_foreign_router.py` 가 그 조건 id 목록을 **런북 파일에서 읽어** 자기 판정과 대조한다. 목록에서 한 항목을 빼면 검사는 그것을 조용히 건너뛰는 것이 아니라 **바뀐 목록으로 대조하고**, 판정 코드가 없는 조건 id 를 더하면 **그 자리에서 막힌다** — 검사 안에서 목록을 양쪽으로 바꿔 넣어 그 사실을 매번 재확인한다.
  - [x] AC-3 그 검사가 **조건을 만족하지 않는 합성 루트에서 실패하고 만족하는 합성 루트에서 통과한다** — 두 루트를 검사 안에서 각각 만들어 양쪽을 판정한다. 반례는 빈 루트가 아니라 **그럴듯한 거짓 루트**여야 한다: ① `docs/work/<id>/spec.md` 는 서 있는데 `status: draft` 인 것 · ② 승인까지 됐는데 `facets` 가 `[tooling, docs]` 뿐인 것. 빈 루트만으로 통과한 검사는 고치기 전 상태와 구별되지 않는다(§11).
  - [x] AC-4 그 검사를 **실제 대상 저장소에 대해 돌려 통과**시킨다 — 세 조건이 전부 참인 것을 증거 `foreign-router-verdict` 로 남긴다. 대상 저장소의 단위 승인은 이 저장소의 승인과 별개로 **사람이 한 번 더** 한다(D-27).
  - [x] AC-5 런북 「두 라우팅 규칙이 만나는 자리」 절의 인용이 **각 줄마다 출처 줄 번호를 달고**, `tests/test_foreign_router.py` 가 그 목록을 **런북에서 읽어** 대상 `CLAUDE.md` 의 같은 줄과 **글자로 대조한다**. 인용을 더하거나 옮기면 대조 대상도 함께 바뀌고, 인용 텍스트가 실제 줄과 다르면 **그 자리에서 실패한다** — AC-2 와 같은 패턴이다. 대상 파일이 없는 환경(CI)에서는 **합성 fixture 로 일치·불일치 양쪽을 판정한다**. 실제 대상 저장소에 대해 그 대조를 돌린 것이 증거 `foreign-router-claude-md` 이고, 그 증거는 두 블록의 경계(줄 범위)와 **같은 상황을 서로 다르게 지시하는 구절이 있는지 없는지**도 함께 인쇄한다. **없으면 「없다」를 근거와 함께 적는 것이 결과다**(K-51). 2회차 검토자가 이 자리를 잡았다 — 런북이 `CLAUDE.md:76` 을 인용하는데 증거 명령의 `sed -n '65,67p;72p'` 가 그 줄을 인쇄하지 않았다. 원인은 숫자 오기가 아니라 **요구하는 자리와 보는 자리가 서로를 모른 채 각각 하드코딩된 것**이라(§11), 범위를 맞추는 대신 대조를 기계에 옮긴다(사용자 확정 2026-09-05).
  - [x] AC-6 이 관통이 낸 관측이 `docs/planning/open-questions.md` 에 이 단위 id 를 가리키는 Q 항목으로 **한 건 이상** 열린다. 고치지 않고 열어만 둔다(§12).
- **위험과 되돌리기:** 이 관통은 대상 저장소에 **문서만** 만든다 — `docs/work/<id>/` 하나이고 그 저장소의 코드·설정·운영 상태를 건드리지 않는다. 대상 저장소는 지금 부착분이 미커밋인 상태라 새 폴더도 미추적으로 남고, `git status` 만으로 갈린다. 실제 위험은 하나다 — 라우터가 그 저장소에서 돌면서 **BMad 산출물 경로(`_bmad-output/`)나 기존 문서를 건드리는 것**. 그래서 별도 실행의 쓰기 상한은 그 저장소의 `docs/work/` 하나로 둔다.
  되돌리기 — 대상 저장소: `rm -rf ~/orca/workspaces/My-Automated-Worker/instagram-dm-sender/docs/work/<id>` (미추적이므로 `git status --porcelain` 이 부착 전 목록으로 돌아가는 것으로 확인한다). Romeo-Harness: `git revert <구현 커밋>`. 운영 상태·외부 상태·비용은 이 단위가 건드리지 않는다.
- **결정 필요:** **관통 대상은 실행 중에 한 번 더 사용자에게 간다.** 승인 시점의 후보는 GitHub issue 14번이었으나, 실행이 그 이슈의 산출물 4종이 **전부 이미 실재**하는 것을 실측했고(정책 문서·`scripts/scan-secrets.sh` 16,793B·`skills/secrets-policy/` + 심볼릭 링크·BMad override 2개 · 대체 후보 #36·#15·#51·#52 도 같은 상태), 사용자가 **대상 저장소 `CLAUDE.md` 의 BMad·Romeo 라우팅 충돌 해소**로 바꿔 확정했다(2026-09-04). charter 의 가정 「대상 저장소에 관통시킬 실제 작업이 있다」가 틀렸다는 것이 이 단위의 실측 중 하나다. 대상 저장소 쓰기는 그 저장소를 작업 공간으로 삼는 별도 실행이 한다(charter 제약 · 사용자 확정 2026-09-04). 다만 **대상 저장소 단위의 승인은 구현 도중 사용자에게 한 번 더 간다** — 그 단위의 확인란을 읽고 승인하는 것은 사람의 몫이다(D-27).


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `scenarios/11-router-foreign-repo.md` · `tests/test_foreign_router.py` · `docs/planning/open-questions.md` · `docs/work/feat-20260904-m2-router-foreign-repo-ct5h/`
- 영향을 받는 부분: 대상 저장소 `~/orca/workspaces/My-Automated-Worker/instagram-dm-sender` — **이 저장소 밖이라 쓰기 상한에 넣지 않는다.** 그 저장소에 작업 단위를 세우는 것은 그것을 작업 공간으로 삼는 별도 실행이 하고, 이 단위는 그 결과를 **읽어** 판정하고 증거로 기록한다(사용자 확정 2026-09-04). 그 별도 실행의 쓰기 상한은 대상 저장소의 `docs/work/` 하나다.
- 바꾸지 않는 것(비범위): `romeo/` 전부 — 대상 저장소에 `bin/`·`romeo/` 가 없다는 것(Q-54)을 **이 단위에서 고치지 않는다**. 그것을 푸는 것이 M5 `attach` 다(§12·charter 중단 조건 ③). `scenarios/10-attach-payload.md` 도 고치지 않는다 — 부착은 이미 닫혔다. 관통 대상으로 고른 요청 자체를 **구현하지 않는다**(M3). 대상 저장소의 BMad·`_bmad-output/`·기존 문서·`.claude/settings.json` 을 건드리지 않는다.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 라우터를 남의 저장소에서 돌리는 절차를 다섯 절로 고정하고, 「검증」 절이 완료 조건을 조건 id 로 적는다 | `scenarios/11-router-foreign-repo.md` 신설 | 소비: `scenarios/10-attach-payload.md` 의 「놓는 것」 목록 문법 → 생산: 조건 id `unit-exists` · `unit-active` · `unit-foreign-facet` 와 그 목록을 읽는 문법 | check-2 (다섯 절 전부 존재) | 파일 삭제 |
| 2 | 그 조건 id 목록을 런북에서 읽어 주어진 루트를 판정하는 검사를 만든다. 목록을 바꾸면 대조가 함께 바뀌고, 판정 코드가 없는 id 를 더하면 막힌다 | `tests/test_foreign_router.py` 신설 | 소비: 1 의 조건 id 와 목록 문법 → 생산: `conditions()` · `check(root)` | check-1 (합성 루트 양쪽 + 목록 조작 재확인이 전부 통과) | 파일 삭제 |
| 3 | 대상 저장소에서 별도 실행으로 라우터를 돌려 **그 시점에 사용자가 확정한 요청 1건**을 분류하고 사람 승인까지 세운다 | 대상 저장소 `docs/work/<id>/` (이 저장소 밖 — 쓰기 상한 아님) | 소비: 1 의 「어디서 실행하는가」 절 → 생산: 대상 저장소의 승인된 작업 단위 1건 | 증거 `foreign-router-verdict` (2 의 검사를 실제 대상 루트에 대해 돌려 exit 0) | 대상 저장소에서 `rm -rf docs/work/<id>` — 미추적이라 `git status` 가 부착 전 목록으로 돌아간다 |
| 4 | 두 라우팅 규칙이 만나는 자리를 실제 인용으로 런북에 적고, 이 관통이 낸 관측을 열어 둔다 | `scenarios/11-router-foreign-repo.md` (「두 라우팅 규칙이 만나는 자리」 절) · `docs/planning/open-questions.md` | 소비: 증거 `foreign-router-claude-md` → 생산: 인용 2건 이상과 Q 항목 | check-3 (이 단위 id 를 가리키는 Q 행 ≥ 1) · 인용 자체는 검토자와 증거가 본다 | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**판별 검사와 회귀 방지 검사** — check-1·2·3 은 **판별 검사**다(이 단위가 없으면 실패해야 한다).
check-4·5 는 **회귀 방지 검사**이므로 양쪽 상태에서 통과가 예상되고, 두 상태 실측의 대상이 아니다(§11).

AC-5 의 **합성 fixture 대조**(인용 목록을 런북에서 읽어 일치·불일치 양쪽을 판정하는 부분)는 저장소 안에서 완결되므로 check-1 이 판정한다.
그러나 AC-4 와 AC-5 의 **실제 대상 부분**은 required_checks 가 아니라 **증거**가 판정한다 — 이 저장소 **밖**의 상태(대상 저장소)를 읽으므로,
검사에 넣으면 대상 저장소가 없는 머신(CI)에서 이 단위가 영원히 닫히지 않는다. 그 두 증거는 아래 이름으로 남긴다:
`foreign-router-verdict`(check 의 판정 함수를 실제 대상 루트에 대해 돌린 결과) · `foreign-router-claude-md`(두 라우팅 규칙의 위치와 인용).

승인 전 양쪽 실측 (2026-09-04 · 프로브를 이 체크아웃에 만들고 실측 뒤 삭제 · `git status` 로 원복 확인):

| 검사 | 구현 전 | 가상 완료 | 그럴듯한 거짓 값 반례 |
| --- | --- | --- | --- |
| check-1 | exit 1 | exit 0 | 런북 「검증」 표에서 `unit-foreign-facet` **한 줄만** 지우면 exit 1 — 검사가 목록을 파일에서 읽고 있다는 증거다 |
| check-2 | exit 1 | exit 0 | 다섯 절 중 「## 검증」 **하나만** 「## 확인」으로 바꾸면 exit 1 |
| check-3 | exit 1 | exit 0 | Q 행은 그대로 두고 **단위 id 만 다른 단위 것으로** 바꾸면 exit 1 — 「Q 행이 있는가」가 아니라 「이 단위를 가리키는가」를 본다 |
| check-4 | exit 0 (회귀) | — | — |
| check-5 | exit 0 · **269초** (재실행 상한 600초의 45% — 경고 임계 80% 아래) | — | — |

반례를 빈 값이 아니라 **그럴듯한 거짓 값**으로 잡은 이유는 §11 이다 — 빈 값은 고치기 전에도 막혔으므로 판별력을 증명하지 않는다.
`check(root)` 의 합성 루트 반례 둘(`status: draft` · `facets: [tooling, docs]`)도 같은 이유로 **폴더는 서 있는** 루트다.

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
    command: "python3 -m unittest tests.test_foreign_router -v"
  - id: check-2
    command: "for h in '## 어디서 실행하는가' '## 무엇이 대상 저장소에 서는가' '## 두 라우팅 규칙이 만나는 자리' '## 검증' '## 되돌리기'; do grep -qF \"$h\" scenarios/11-router-foreign-repo.md || exit 1; done"
  - id: check-3
    command: "test $(grep -cE '^\\| Q-[0-9]+ \\|.*feat-20260904-m2-router-foreign-repo-ct5h' docs/planning/open-questions.md) -ge 1"
  - id: check-4
    command: "bin/romeo validate docs/work/feat-20260904-m2-router-foreign-repo-ct5h"
  - id: check-5
    command: "python3 -m unittest discover -s tests"
```


## 증거

close PASS · 2026-09-05T01:57:26+09:00 · HEAD 7d94b0f7055f · 검사 기록 run_2d9f8a17e34d

- [evidence/run_2d9f8a17e34d.yaml](evidence/run_2d9f8a17e34d.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
