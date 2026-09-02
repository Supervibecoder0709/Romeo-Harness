---
id: feat-20260902-scope-grammar-procedure-drift-z5mv
type: spec
title: 승인 산문이 쓰기 권한이 되지 않게 하고, 절차와 도구의 어긋남을 닫는다 — 시나리오 8 관통이 낸 결함 Q-36~Q-42
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: active
approved_at: '2026-09-02T14:47:31+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-02'
updated: '2026-09-02'
---

# 승인 산문이 쓰기 권한이 되지 않게 하고, 절차와 도구의 어긋남을 닫는다 — 시나리오 8 관통이 낸 결함 Q-36~Q-42

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260902-scope-grammar-procedure-drift-z5mv --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 직전 관통(시나리오 8)이 낸 하네스 결함 7건을 닫는다. ① 승인 문장의 **설명 산문이 쓰기 권한이 되는 것**을 막는다 — 「변경 범위」에서 괄호 안의 설명과 경로 모양이 아닌 토큰(함수명·플래그)은 쓰기 상한(`allowed_paths`)에 넣지 않고, 그 문법을 spec 을 쓰는 사람이 읽는 템플릿에 적는다(Q-36). ② fixture 대조 명령이 **불일치 1건이면 실패**하게 한다 — 지금은 30/33 이 맞아도 exit 0 이라 CI 스텝이 아무것도 판정하지 않는다(Q-37). ③ 위임 절차 원본(RUNBOOK)과 도구(`run-unit`)의 어긋남 5건을 맞춘다 — 첫 관통에서 항상 실패하던 확인 4 를 `started` 기록은 무시하고 **판정·재검토만** 대조하는 명령으로 바꾸고(Q-39), `run-unit` 이 없는 Run 을 가리키거나 절차 항목을 빠뜨린 위임 명령을 인쇄하던 것을 정본 절차 파일에서 채우게 하고(Q-40), 재승인 때 Run 을 무조건 새로 만들라던 규칙을 **해시를 `--spec` 에 넣은 경우로 한정**하며(Q-41), 재승인해도 갱신되지 않던 회차 기록의 `base_sha` 를 갱신한다(Q-42). ④ 「범위를 다 알 수 없는 작업에서 재승인이 필수 경로가 되는가」(Q-38)는 **재승인이 정상 경로**라는 결정(D-80)으로 닫고, 그 비용은 Q-41 로 낮춘다.
- **왜 지금:** 코어 규칙 §10 은 관통 **중에는** 하네스를 못 고치게 하므로 고칠 수 있는 구간은 관통과 관통 사이인 지금뿐이고, M3 는 앞으로 관통을 더 돈다(시나리오 9 · 실제 T2 관통). Q-36 은 **권한 상한 계열**이다 — 이번엔 함수명 `cmd_card` 가 실려 판정에 영향이 없었지만, 승인하지 않은 경로가 상한에 조용히 들어가는 구멍이 열려 있다(K-66). Q-37 은 CI 가 초록인데 fixture 가 틀릴 수 있는 상태다. Q-39·Q-40 은 직전 관통에서 `started` 유령 회차 2건과 확인 4 의 반복 실패를 실제로 만들었다.
- **기대 결과:** 승인 문장의 설명을 아무렇게 써도 쓰기 상한은 승인한 경로만 담는다. fixture 가 하나라도 틀리면 로컬 명령도 CI 도 빨간불이다. `run-unit` 이 인쇄한 명령을 그대로 실행해도 RUNBOOK 과 어긋나지 않고, 첫 관통의 확인 4 가 통과하며, 재승인이 관통을 처음부터 다시 돌리게 하지 않는다.
- **수용 기준:**
  - [ ] AC-1 **설명 산문이 쓰기 상한에 들어가지 않는다** — 시나리오 8 spec 의 실제 「변경 범위」 문장에서 `cmd_card` 가 상한에 나오지 않고 `romeo/cli.py` 는 나온다. 괄호 안에 경로 모양의 백틱이 있어도 상한에 들어가지 않는다(넓어지는 방향의 반례). `/` 도 `.` 도 없거나 공백이 든 백틱 토큰은 상한에 들어가지 않는다. 괄호가 줄을 넘겨도 다음 줄의 항목은 살아 있다. 조각의 **첫 백틱만** 경로다 — 뒤따르는 백틱은 괄호 밖이어도 상한이 아니다. 괄호 제거는 백틱 **밖** 구간에만 적용한다 — `app/(g)/page.tsx` 같은 경로 안의 괄호는 지우지 않는다.
  - [ ] AC-2 **기존 승인의 상한은 그대로다** — 저장소에 커밋된 구현자 계약 30건 전부에서, 그 계약의 `base_sha` 커밋의 spec 을 새 규칙으로 읽은 결과가 **이 단위 직전 하네스(`d9a3b12`)의 규칙**으로 읽은 결과와 순서까지 같다. 기록된 `allowed_paths` 와의 대조는 이력상 3건(`feat-20260829-license-field-46an` 의 `run_31e175742892`·`run_b5cdadaffcdc` — 상한이 `.` 이던 시절 · `feat-20260831-bmad-attach-probe-tgnb` 의 `run_d7edd4884a83` — Q-18 이전 파서가 만든 계약)을 이름으로 제외한 27건이 **목록으로**(순서 포함) 같다. `cmd_card` 는 커밋된 계약이 아니라 시나리오 8 spec 의 재계산에서만 빠진다(AC-1 — 그 단위의 계약은 `.gitignore` 로 커밋되지 않았다). 동등성 관측 케이스의 계약 재계산(`fixtures parity`)이 그대로 통과한다.
  - [ ] AC-3 **문법이 spec 을 쓰는 사람이 읽는 자리에 있다** — Tech Spec 템플릿의 「변경 범위」 절이 경로는 백틱으로, 설명은 괄호 안에, `/`·`.` 이 없는 토큰은 경로로 읽지 않는다는 것과 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다는 것을 적고 있다. 계약을 만들 때 경로로 읽지 않은 백틱 토큰이 있으면 그 목록을 인쇄한다(계약 JSON 자체는 바뀌지 않는다).
  - [ ] AC-4 **fixture 불일치 1건이면 exit 1** — 번들 fixture 33건 중 1건의 기대 profile 만 다른 유효한 값으로 바꾼 디렉터리(97% 일치)에서 `route --fixtures <디렉터리> --report` 가 exit 1 이고, 원본 그대로에서는 exit 0, 빈 디렉터리(0/0)는 exit 1 이다. `gate 누락 의심` 이 1건이면 일치가 33/33 이어도 exit 1 이다. 같은 리포트를 내는 `fixtures report` 도 같은 규칙이다 — 두 명령이 다른 판정을 내지 않는다. CI 의 그 스텝은 명령을 바꾸지 않고도 이 판정을 받는다(`|| true` 도 `continue-on-error` 도 없다).
  - [ ] AC-5 **`run-unit` 이 인쇄하는 위임 명령이 RUNBOOK 과 같다** — 인쇄에 `run-create` 가 없고 `--run` 으로 받은 Run 이 이미 있는지 보는 명령(`run-show --id`)이 첫 명령이다. 구현자 `task-create` 의 `--spec` 은 정본 절차 파일(`adapters/orca/prompts/implementer-brief.md` 를 채운 `.harness/runs/<id>/<run>/implementer-spec.md`)을 읽고, 그 정본에 §3.4 의 항목 5개(결과 계약 형식 · 체크박스는 구현자가 채운다 · 계약이 없으면 스스로 만든다 · `--task-id`·`--dispatch-id` 플래그 · dispatch-id 는 기동 뒤 전달)가 들어 있다. 검토자 `task-create` 의 `--spec` 에는 해시(64자리 16진수)가 없다. 검토자 절차 파일을 채우는 명령이 1단계가 만든 검토자 계약의 sha256 을 실어 인쇄된다. RUNBOOK §3.4 의 bash 블록이 자리표시자 대신 그 형태(구현자 `--spec "$(cat .harness/runs/<id>/<run-id>/implementer-spec.md)"` · 검토자 `--spec` 의 경로·절차 문장)를 적고, 테스트가 그 블록에서 명령을 뽑아 `run-unit` 의 인쇄와 문자열로 대조한다 — 요구하는 자리와 만드는 자리가 하나다.
  - [ ] AC-6 **§3.1 확인 4 가 첫 관통에서 통과한다** — 새 명령 `run-unit check --unit <id> --base-sha <sha>` 는 커밋과 작업 트리의 `attempts.yaml` 을 **판정 난 시도(pass·fail)와 재검토(reviews)** 로만 대조한다. 양쪽 다 없음 → 0, 작업 트리에만 `started` → 0, 작업 트리에만 `fail` 이나 재검토 → 1, 커밋의 `fail` 이 작업 트리에서 `pass` 로 바뀜 → 1, 같음 → 0. RUNBOOK §3.1 확인 4 의 bash 블록이 그 명령이고, 지시된 해법은 「판정·재검토가 커밋 밖이면 그것을 커밋한다 — `started` 는 커밋하지 않아도 된다」 다. §3.4.2 의 「확인 4 를 되살린다」 문단도 그 기준으로 고쳐져 있다. 대조는 **양방향**이다 — 커밋에는 있는 판정·재검토가 작업 트리에 없으면 → 1. §3.4.2 문단이 `run-unit check` 와 `started` 를 말하고 옛 `diff` 지시를 담지 않는다는 것이 앵커 테스트로 고정된다.
  - [ ] AC-7 **재승인이 Run 재생성을 무조건 요구하지 않는다** — RUNBOOK §3.4 가 「`--spec` 에는 해시를 넣지 않는다 — 경로와 절차만. 해시는 §3.7 의 채움 스크립트가 그 자리에서 계산해 절차 파일에 적는다」 를 규칙으로 적고, §3.4.1 이 Run 재생성을 **`--spec` 에 낡은 해시가 들어간 경우**로 한정하며 해시 없이 경로만 넣었으면 Run·Task 를 유지하고 봉투(§3.3·§3.5.1)와 절차 파일(§3.7)만 새 base 로 다시 만든다고 적는다(2026-09-02 5회차 관측). 옛 절차는 해시가 들어간 경우의 절차로 남는다.
  - [ ] AC-8 **회차 기록의 `base_sha` 가 재승인을 따라간다** — 승인 커밋 A 에서 만든 run 의 계약을 재승인 커밋 B 에서 같은 run 으로 다시 만들면 `attempts.yaml` 의 그 회차 `base_sha` 는 B 가 되고 A 는 `base_sha_history` 에 남으며 회차 수는 늘지 않는다. 같은 base 로 다시 만들면 아무것도 바뀌지 않는다.
  - [ ] AC-9 **Q-38 이 결정으로 닫히고 7행이 해소된다** — `docs/decisions/decision-register.md` 에 D-80(재승인은 정상 경로 — (a) 파생 범위 선언은 승인 문장이 아닌 것을 상한에 넣는 방향이라 K-66 과 어긋나고 (c) 경량 승인 창구는 승인 창구를 둘로 만들어 D-60 과 어긋난다 · 비용은 Q-41 과 시딩으로 낮춘다)이 있고, `docs/planning/open-questions.md` 의 Q-36~Q-42 7행이 다른 해소 항목과 같은 형식(원문 취소선 + **해소(2026-09-02, 이 단위)**)으로 갱신돼 있다.
  - [ ] AC-10 기존 검사가 회귀하지 않는다 — unittest 전체와 `compile --check` · `validate` · `doctor --strict --scope repository` · `fixtures check` · `fixtures parity --report` · `route --fixtures fixtures/requests --report` 가 모두 종료 코드 0.
- **위험과 되돌리기:** 위험은 셋이다. **(1) 파서를 바꾸면 이미 승인된 단위의 계약이 다르게 재계산될 수 있다** — 종료 검사와 동등성 관측 케이스가 계약을 승인 원본에서 다시 계산해 바이트로 대조하기 때문이다. 그래서 승인 전에 실측했다: 2026-09-02 프로브(저장소 무변경)에서 새 규칙을 `docs/work` 의 spec 16개에 적용하니 15개는 현재 파서와 바이트 동일했고 시나리오 8 만 `cmd_card` 하나가 빠졌다. 동등성 관측 케이스가 재계산하는 `feat-20260829-license-field-46an` 도 동일하다. AC-2 가 이것을 커밋된 계약 전부에 대해 테스트로 고정한다. **이 단위 자신의 「변경 범위」도 그 위험에 걸린다** — 구현자가 파서를 바꾼 워크트리에서 도는 종료 검사가 새 파서로 이 단위의 계약을 재계산하므로, 아래 「변경 범위」는 괄호·설명 백틱 없이 경로만 나열했고 승인 전에 두 파서로 대조해 같은 목록임을 확인했다. **(2) fixture 대조를 엄격하게 하면 fixture 가 하나라도 어긋난 순간 CI 가 빨간불이 된다** — 그것이 목적이다. 지금은 33/33 이 맞는다. **(3) RUNBOOK 의 절을 고치면 그 절을 앵커로 잡은 기존 테스트가 걸릴 수 있다**(§3.1 의 `attempts.yaml` bash 블록은 정확히 1개여야 하고, `git ls-tree` 목록은 8행이어야 한다) — 구현자가 그 테스트를 함께 고치고 전체 unittest 로 확인한다. **(4) 전체 unittest(check-11)가 208~218초로 종료 검사의 재실행 상한(기본 300초)에 90초 미만으로 붙어 있다** — 상한을 넘기면 그 검사가 미검증이 되어 close 가 PASS 를 선언하지 못한다(검사 내용이 아니라 머신 부하가 결론을 바꾸는 자리). 이 단위는 그 상한을 바꾸지 않고(`romeo/close.py`·`romeo/evidence.py` 비범위), 종료 검사를 `close --rerun-timeout 900` 으로 돌린다. 전부 이 저장소 안의 로컬 변경이고 외부 상태를 바꾸지 않으므로 되돌리기는 `git revert <커밋>` 한 번이다. 워크트리에서 작업하므로 통합 전에는 브랜치가 그대로 남는다.
- **결정 필요:** 없음 — 두 결정(Q-38 → (b) 재승인은 정상 경로 · Q-37 → `--report` 기본값을 엄격으로)은 제안 카드의 추천안으로 확정했다. 이 승인 자체도 사용자의 2026-09-02 지시(「다음 작업을 이어서 진행하고, 승인이 필요한 일은 모두 추천사항으로 처리해」)에 따라 추천안으로 기록한다.


## 변경 범위

- 바뀌는 파일·모듈: `romeo/envelope.py` · `romeo/cli.py` · `romeo/run_unit.py` · `core/templates/tech-spec.md` · `adapters/orca/RUNBOOK.md` · `.github/workflows/harness.yml` · `tests/test_envelope.py` · `tests/test_policy.py` · `tests/test_run_unit.py` · `tests/test_runbook_procedure.py` · `docs/planning/open-questions.md` · `docs/decisions/decision-register.md` · `docs/work/feat-20260902-scope-grammar-procedure-drift-z5mv/`
- 영향을 받는 부분: 앞으로 만들어지는 모든 작업 계약의 `allowed_paths` 계산(Q-36) · CI 의 fixture 스텝과 로컬 `route --fixtures --report` 의 종료 코드(Q-37) · 다음 관통의 위임 절차 — §3.1 확인 4·§3.4·§3.4.1·§3.4.2 와 `run-unit` 의 인쇄(Q-39~Q-42). 이미 닫힌 단위의 계약 재계산은 AC-2 가 그대로임을 고정한다.
- 바꾸지 않는 것(비범위): `romeo/evidence.py`(`_stamp_ids`·`_change_base` — 한 run 은 한 위임이라는 방어는 그대로다) · `romeo/close.py` 의 판정 로직 · 코어 규칙(`core/principles/`) · `adapters/orca/prompts/implementer-brief.md`·`reviewer-brief.md` 의 문안(정본을 그대로 쓴다) · Orca CLI 자체의 동작 · 다른 park(Q-12·13·15·16·17·19·23·24·26·32·33·34·35) · `run-unit --spawn` 의 실제 실행 경로(자리표시자에서 멈추는 지금 동작 그대로 — 이 단위는 **인쇄**를 고친다) · 시나리오 9(gate 집행)·실제 T2 관통.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 설명 산문을 쓰기 상한에서 뺀다(Q-36) | `romeo/envelope.py` 의 `change_scope_paths` 를 고친다. 선언된 줄들을 이어 붙인 뒤 **괄호 `(…)`·`（…）` 안을 줄 경계를 보존한 채 공백으로 바꾸고**(중첩은 반복 제거), 다시 줄마다 `·` 로 나눠 각 조각의 첫 백틱을 읽는 것은 그대로다. 읽은 토큰이 **경로 모양이 아니면**(공백을 포함하거나 `/` 도 `.` 도 없으면) 상한에 넣지 않고 「경로로 읽지 않은 토큰」 으로 모은다. 앞의 `./` 는 벗긴다. 저장소 밖(`/`·`~`·`..`)을 버리는 규칙은 그대로다. **괄호 제거는 백틱 밖 구간에만** 적용한다(백틱 토큰을 먼저 뽑고 그 사이 텍스트에서만 지운다) — 경로 안의 괄호는 살아야 한다. 새 함수 `change_scope_report(body)` 가 `{"paths": [...], "ignored": [...]}` 를 돌려주고 `change_scope_paths(body)` 는 그 `paths` 다. `write_envelope` 의 반환에 `scope_ignored` 를 싣고, `romeo/cli.py` 의 `cmd_envelope` 가 비어 있지 않을 때만 `  경로로 읽지 않은 백틱 N개: …` 한 줄을 더 인쇄한다(`--json` 이면 표준 오류로 — 표준 출력은 계약 JSON 이다). 역할과 무관하게 계산한다. **계약 JSON 의 필드는 바꾸지 않는다** — 앵커 재계산과 호환돼야 한다 | 소비: 없음 → 생산: `change_scope_report(body) -> dict(paths, ignored)` · `write_envelope()[...]["scope_ignored"]` | `tests/test_envelope.py` 의 `TestChangeScopeGrammar`: ① 시나리오 8 spec(`docs/work/feat-20260901-scenario-8-capability-probe-s7ny/spec.md`, 저장소의 실제 파일)의 본문에서 `cmd_card`·`--root`·`cmd_route --card` 가 나오지 않고 `romeo/cli.py`·`scenarios/8-capability-absent.md` 는 나온다 ② `` `a/x.py`(설명 · `b/y.py` 는 그대로) `` 에서 `b/y.py` 가 나오지 않는다 ③ 괄호가 줄을 넘긴 `` `a/x.py`(설명 ·\n  다음 줄 · 계속) · `b/y.py` `` 에서 `b/y.py` 가 나온다 ④ `` `cmd_card` · `--root` · `a b/c.py` `` 는 전부 ignored 에 들어가고 paths 는 빈다 ⑤ `./LICENSE` → `LICENSE` ⑥ 기존 `TestChangeScopeMultiline` 10건이 그대로 통과 ⑦ `` `a/x.py` 는 `b/y.py` 를 부른다 · `c/z.py` `` → paths 는 `a/x.py`·`c/z.py` 이고 `b/y.py` 는 paths 에 없다(조각의 첫 백틱만) ⑧ `·` 없이 줄바꿈으로만 나눈 선언에서 닫는 괄호와 같은 줄에 다음 항목이 오는 `` `a/x.py`(설명\n  계속) `b/y.py` `` → 둘 다 나온다(줄 경계를 지우는 구현은 여기서 하나만 낸다) ⑨ `app/(g)/page.tsx` 는 상한에 남는다. 시나리오 8 의 문장은 테스트 상수로도 박아 둔다(저장소 파일이 나중에 고쳐져도 부정 단언이 빈 검사가 되지 않게). `TestChangeScopeRegressionOnRecordedContracts`: `git ls-files 'docs/work/*/task/*-implementer.json'` 의 계약 30건 전부에 대해 `git show <base_sha>:<spec 경로>` 의 본문을 새 규칙으로 읽은 결과가 `d9a3b12` 규칙(테스트 안에 참조 구현으로 고정)으로 읽은 결과와 **목록으로 같고**, 이력상 3건(AC-2 에 이름 명시)을 제외한 27건은 `[must_include] + new` 가 기록된 `allowed_paths` 와 목록으로 같다(check-1) | `git revert` |
| 2 | 문법을 spec 을 쓰는 사람이 읽는 자리에 적는다(Q-36) | `core/templates/tech-spec.md` 의 「변경 범위」 절 제목 아래, 목록 **앞**에 안내 문단을 넣는다: 경로는 백틱으로 · 항목은 `·` 나 줄바꿈 목록으로 · 설명은 괄호 안에(괄호 안의 백틱은 경로로 읽지 않는다) · `/` 도 `.` 도 없는 토큰(함수명·플래그)은 경로로 읽지 않는다 · 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다 · 그 규칙의 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다. 문단에 라벨 문자열(「바뀌는 파일·모듈」 뒤에 콜론이 붙은 형태)을 그대로 쓰지 않는다 — 파서가 그 줄을 선언으로 읽는다 | 소비: 1 → 생산: 템플릿 문단 | `grep -q '경로로 읽지 않' core/templates/tech-spec.md`(check-2) · `TestChangeScopeGrammar.test_the_template_states_the_grammar` 가 그 다섯 요소를 본다(check-1) | `git revert` |
| 3 | fixture 불일치 1건이면 실패한다(Q-37) | `romeo/cli.py` `cmd_route` 의 fixture 분기 **와** `cmd_fixtures` 의 `report` 분기 둘 다: 종료 코드를 `0 if rep["total"] and rep["matched"] == rep["total"] and rep["gate_misses"] == 0 else 1` 로 바꾼다(90% 임계값 제거 — 그것은 M0 진입 기준이었다 · `total` 가드는 빈 디렉터리 0/0 을 통과로 접지 않기 위한 것이다, K-51). `--report` 도움말에 「불일치나 gate 누락 의심이 1건이면 exit 1」 을 적는다. `.github/workflows/harness.yml` 의 그 스텝 이름을 「정책표 fixture 대조 — 불일치 1건이면 실패(Q-37)」 로 바꾸고 명령은 그대로 둔다 | 소비: 없음 → 생산: `cmd_route` 종료 코드 규칙 | `tests/test_policy.py` 의 `TestFixtureReportExit`: ① 임시 디렉터리에 `fixtures/requests` 33건을 복사하고 1건의 `expected.profile` 을 실제와 다른 **유효한** profile 값으로 바꾼 뒤 CLI `route --fixtures <디렉터리> --report` → exit 1 ② 원본 디렉터리 → exit 0 ③ 빈 임시 디렉터리 → exit 1 ④ `run_report` 를 패치해 matched == total·gate_misses == 1 인 리포트를 돌려주게 한 뒤 → exit 1 ⑤ 같은 디렉터리에서 `fixtures report` 와 `route --fixtures … --report` 의 종료 코드가 같다(일치 디렉터리·불일치 디렉터리 둘 다) ⑥ `TestFixtures.test_bundled_fixtures_pass_threshold` 의 `>= 0.9` 를 `matched == total` 로 조인다. `test_ci_step_takes_the_verdict_as_is`: `.github/workflows/harness.yml` 에 `bin/romeo route --fixtures fixtures/requests --report` 로 끝나는 run 줄이 있고 그 스텝 블록과 job 에 `|| true`·`continue-on-error` 가 없다(check-3) · `bin/romeo route --fixtures fixtures/requests --report` exit 0(check-4) | `git revert` |
| 4 | `run-unit` 의 위임 명령을 RUNBOOK 에 맞춘다(Q-40·Q-41) | `romeo/run_unit.py` `delegation_commands` 를 고친다 — 하네스 루트와 1단계가 만든 검토자 계약의 sha256 을 인자로 받는다. ① 첫 명령 `run-create` 를 `orca orchestration run-show --id <run> --json` 으로 바꾼다(주석: `--run` 은 §3.2 에서 이미 만든 Run id 다 — 없으면 여기서 exit≠0 으로 멈춘다) ② 구현자 절차 파일을 정본에서 채우는 명령을 더한다: `mkdir -p .harness/runs/<id>/<run> && awk 'f;/^---$/{f=1}' <하네스루트>/adapters/orca/prompts/implementer-brief.md \| sed "s/<id>/…/g; s/<run-id>/…/g; s/<base-sha>/…/g" > .harness/runs/<id>/<run>/implementer-spec.md` ③ 구현자 `task-create` 의 `--spec` 을 `"$(cat .harness/runs/<id>/<run>/implementer-spec.md)"` 로 ④ 검토자 `task-create` 의 `--spec` 은 경로와 절차만: 계약 `docs/work/<id>/task/<run>-reviewer.json` · 판정 `docs/work/<id>/review/<run>-reviewer.json` · 절차 `core/workflows/review/SKILL.md` · 「절차 파일은 §3.7 이 채워 argv 로 넘긴다 — 해시는 거기서 계산한다」 · 읽기 전용. **해시를 넣지 않는다** ⑤ `reviewer-spawn` 앞에 절차 파일 채움 명령을 더한다: `python3 <하네스루트>/adapters/orca/prompts/fill_brief.py --unit <id> --run <run> --base-sha <base> --task-sha256 <검토자 계약 sha256> --runtime codex --mode base --out <W>/.harness/runs/<id>/<run>/reviewer-brief.md`(W 는 자리표시자로 남긴다). `run_unit()` 이 1단계 `built` 에서 검토자 sha256 을 꺼내 넘긴다. **RUNBOOK §3.4 의 bash 블록도 같은 형태로 구체화한다** — 구현자 `--spec "$(cat .harness/runs/<id>/<run-id>/implementer-spec.md)"` · 검토자 `--spec` 의 경로·절차 문장(자리표시자 `<작업 계약 경로와 실행 조건>` 을 없앤다) | 소비: `_stage_contract` 의 `built[*]["sha256"]` → 생산: `delegation_commands(unit_id, run, base_sha, workspace, harness_root, reviewer_sha256)` | `tests/test_run_unit.py` 의 `TestDelegationCommandsMatchRunbook`: ① 인쇄된 명령 문자열 어디에도 `run-create` 가 없고 첫 명령이 `run-show --id <run>` 이다 ② 구현자 task-create 의 `--spec` 이 `.harness/runs/<id>/<run>/implementer-spec.md` 를 읽고, `adapters/orca/prompts/implementer-brief.md` 에 다섯 문구가 있다: `core/schemas/result-envelope.json` · 「네가 채운다」 · 「아직 없으면」 과 `envelope build` · `--task-id <task-id> --dispatch-id <dispatch-id>` · 「받기 전에는」 ③ 검토자 task-create 명령에 `[0-9a-f]{64}` 가 없다 ④ fill_brief 명령에 1단계 검토자 계약의 sha256 이 그대로 실려 있다 ⑤ 기존 `test_delegation_commands_are_printed_not_executed` 유지 ⑥ `tests/test_runbook_procedure.py` 의 `TestDelegationBlockMatchesRunUnit`: §3.4 bash 블록에서 두 `task-create` 명령을 뽑아 자리표시자(`<id>`·`<run-id>`·`<implementer-task-id>`)를 치환한 것이 `delegation_commands` 가 인쇄하는 두 명령과 문자열로 같다(check-5·check-6) | `git revert` |
| 5 | §3.1 확인 4 를 판정·재검토 대조로 좁힌다(Q-39) | `romeo/run_unit.py` 에 `attempts_drift(project_root, unit_id, base_sha)` 를 만든다 — `git show <sha>:docs/work/<id>/attempts.yaml`(없으면 빈 기록)과 작업 트리의 파일을 읽어 **`result` 가 pass·fail 인 시도**(n·run·result 로 식별)와 **reviews**(after_attempt·conclusion·by)만 비교하고 차이 목록을 돌려준다. `started` 는 비교하지 않는다. CLI `run-unit check --unit <id> --base-sha <sha> [--root]` 를 더한다(`action` 선택지에 `check`) — 차이 없으면 exit 0 과 `→ 일치 (판정 N건 · 재검토 M건 · started 는 대조하지 않는다)`, 있으면 exit 1 과 차이 줄. `adapters/orca/RUNBOOK.md` §3.1 확인 4 를 고친다: bash 블록을 그 명령 하나로 바꾸고(§3.1 에 `attempts.yaml` 을 담은 bash 블록은 **정확히 1개**여야 한다 — 기존 테스트의 전제), 왜 옛 diff 가 첫 관통에서 항상 실패했는지(계약 생성이 `started` 를 남긴다)와 새 해법(「판정·재검토가 커밋 밖이면 그것을 커밋한다 — `started` 는 커밋하지 않아도 된다」)을 적는다. §3.4.2 의 「2번이 §3.1 확인 4 를 되살린다」 문단을 같은 기준으로 고친다 | 소비: 없음 → 생산: `attempts_drift(...) -> list[str]` · CLI `run-unit check` | `tests/test_run_unit.py` 의 `TestAttemptsDrift`(임시 저장소): 양쪽 없음 → 0 · 작업 트리에만 started → 0 · 작업 트리에만 fail → 1 · 작업 트리에만 review → 1 · 커밋의 fail 이 작업 트리에서 pass → 1 · **커밋에만 있는 판정 / 커밋에만 있는 재검토(작업 트리 파일 삭제 또는 비움) → 1** · 없는 SHA → 1(ERROR) · 같음 → 0(check-5). `tests/test_runbook_procedure.py::TestAttemptsCommittedCheck` 를 새 기준으로 개정 — 명령을 RUNBOOK 에서 뽑아 `bin/romeo` 를 이 저장소의 절대 경로로 바꾸고 `--root <임시 저장소>` 를 붙여 실행하며, 「작업 트리에만 started」 케이스가 **통과**하는 것과 「커밋에만 있는 판정」 이 거부되는 것을 새 케이스로 추가 · `TestRunbookProcedureAnchors` 에 §3.4.2 절 본문이 `run-unit check` 와 `started` 를 담고 `diff <(git show` 를 담지 않는다는 앵커 추가(check-6) · 이 단위 자신에게 실행: `bin/romeo run-unit check --unit feat-20260902-scope-grammar-procedure-drift-z5mv --base-sha HEAD` exit 0(check-7 — 워커 워크트리에는 이 run 의 `started` 만 작업 트리에 있다) | `git revert` |
| 6 | 재승인 규칙을 조건부로 만든다(Q-41) | `adapters/orca/RUNBOOK.md` §3.4 에 규칙 문단을 넣는다: 「`--spec` 에는 해시를 넣지 않는다 — 경로와 절차만. 해시는 §3.7 의 `fill_brief.py --task-sha256` 이 그 자리에서 계산해 절차 파일 P 에 적는다」. §3.4.1 을 고친다: Run 재생성은 **`--spec` 에 낡은 해시가 들어간 경우에만** 밟는다. 해시 없이 경로만 넣었다면 Run·Task 를 유지하고 §3.3·§3.5.1 의 봉투와 §3.7 의 P 만 새 `<base-sha>` 로 다시 만든다 — 2026-09-02 시나리오 8 5회차가 그 형태였다(Run 유지 · 봉투 재생성 · close PASS). 옛 절차(Run 재생성)는 해시가 들어간 경우의 절차로 남긴다. 「검토자 `--spec` 은 손으로 쓰지 않는다 — … P 파일과 같은 내용이다」 문장은 새 규칙에 맞게 고친다(해시가 든 P 를 `--spec` 에 넣는 것이 바로 §3.4.1 의 원인이었다) | 소비: 4 → 생산: RUNBOOK §3.4·§3.4.1 문단 | `tests/test_runbook_procedure.py` 의 `TestReapprovalRuleIsConditional`: §3.4 절 본문에 「해시」 와 「넣지 않는다」 가 같은 문단에 있다 · §3.4.1 절 본문에 「경우에만」(또는 「한정」)과 `2026-09-02` 가 있다 · §3.4.1 에 「무조건」 이 규칙으로 남아 있지 않다(check-6) | `git revert` |
| 7 | 회차 기록의 `base_sha` 가 재승인을 따라간다(Q-42) | `romeo/envelope.py` `record_start`: 같은 run 의 기록이 있고 `base_sha` 가 다르면 새 값으로 갱신하고 이전 값을 `base_sha_history`(목록, 없으면 만든다)에 덧붙인 뒤 저장한다. 같으면 아무것도 쓰지 않는다. 회차 항목을 새로 만들지 않는다 | 소비: 없음 → 생산: attempts 항목의 `base_sha_history` | `tests/test_run_unit.py` 의 `TestAttemptBaseShaFollowsReapproval`(`_UnitRepo` 위에서 `approve_unit(..., reapprove=True, reason=...)` 뒤 커밋): run_a 를 A 에서 만들고 B 에서 다시 만들면 `attempts[0].base_sha == B`, `base_sha_history == [A]`, `len(attempts) == 1` · 같은 base 로 두 번 만들면 `base_sha_history` 가 생기지 않는다(check-5) | `git revert` |
| 8 | Q-38 을 결정으로 닫고 7행을 해소한다 | `docs/decisions/decision-register.md` 「구현 착수 결정」 표에 D-80 행을 더한다 — 재승인은 정상 경로다(Q-38 (b)); (a) 파생 범위 선언은 승인 문장이 아닌 것을 상한에 넣는 방향이라 K-66 과 어긋나고 (c) 경량 승인 창구는 승인 창구를 둘로 만들어 D-60 과 어긋난다; 비용은 Q-41(해시 없는 `--spec` 이면 Run 유지)과 시딩(직전 회차 워크트리를 읽기 참조로)으로 낮춘다; 상태 accepted · 누가 「자율(기술) — 사용자 위임 2026-09-02」. `docs/planning/open-questions.md` 의 Q-36~Q-42 7행을 다른 해소 항목과 같은 형식(원문 취소선 + **해소(2026-09-02, `feat-20260902-scope-grammar-procedure-drift-z5mv`)** + 무엇으로 닫았나)으로 갱신한다. Q-38 행은 D-80 을 가리킨다 | 소비: 1~7 → 생산: D-80 행 · Q-36~Q-42 해소 행 | 7행 모두에 「해소」 가 있다(check-8) · `grep -q '^| D-80 |' docs/decisions/decision-register.md`(check-9) | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 페이로드(하네스를 부착한 프로젝트) 작업 단위의 `required_checks` 에
**하네스 자신의 테스트**를 넣지 않는다 — `python3 -m unittest discover -s tests`(하네스 저장소의 테스트),
`bin/romeo` 의 자기 검사(`compile --check` · `validate` · `doctor` · `fixtures …`)가 그것이다.
넣으면 하네스가 깨진 동안 그 페이로드 단위가 닫히지 못한다. 그 단위의 산출물은 멀쩡한데 완료가 서지 않는 것이고,
그때 고쳐야 할 것은 그 단위가 아니라 하네스다 — 두 판정을 한 검사에 묶으면 어느 쪽이 깨졌는지 구분되지 않는다
(근거: `feat-20260829-license-field-46an` 의 check-5 가 이 형태였다).
하네스 저장소 **자신**을 대상으로 하는 작업 단위에서는 그 검사들이 정당하다 — 그때는 그것이 이 단위의 산출물이기 때문이다.
**이 단위는 하네스 자신을 고치므로 그 검사들이 정당하다.**

**종료 코드 자체가 조건이다.** 검사에 적는 것은 `id` 와 `command` 둘뿐이고, 그 명령의 종료 코드 0 이 통과다.
기대를 문장으로 따로 적는 자리는 두지 않는다 — 사람은 그것을 조건으로 쓰는데 기계는 판정에 쓰지 않으므로,
그 검사는 무엇을 확인하는지 적혀 있는 채로 아무것도 확인하지 않는 **빈 검사**가 된다(2026-08-31 실측으로 제거).
확인하고 싶은 조건이 있으면 그 조건을 **명령으로** 쓴다.
같은 이유로 옵션이 판정을 만드는 명령은 그 옵션까지 적는다 — 예: `bin/romeo doctor` 는 옵션 없이 쓰면 항상 exit 0 이라 빈 검사이고,
부착 검증(K-68)을 실제로 판정하게 하려면 `bin/romeo doctor --strict --scope repository` 로 쓴다(Q-21).

그래서 `|| true` 를 붙이지 않는다 — 종료 코드를 항상 0 으로 만들어 위반을 통과시킨다.
부정 조건은 `!` 로 쓴다: `! grep -q '<있으면 안 되는 것>' <파일>`.

**양쪽으로 보였다(AGENTS.core §11).** 승인 전에 이 검사들을 **기존 상태**(이 단위 직전 하네스 `d9a3b12`, 이 단위의 테스트 없음)와 **가상 완료 상태**(프로브 워크트리)에서 전부 실행해 종료 코드 표를 brief 의 「승인 전 양쪽 실측」 에 남겼다. 검사는 두 성격이다 — **양쪽 판별 검사**(check-1·2·5·6·7·8·9·10: 기존 상태에서 실패하고 가상 완료 상태에서 0)와 **회귀 방지 검사**(check-3·4·11~16: 양쪽 0 — 이 단위가 기존 것을 깨지 않았다는 것만 말한다). unittest 검사는 **새 테스트 클래스 이름을 박아** 기존 상태에서 실패하게 했다 — 모듈 이름만 적으면 새 클래스를 빠뜨린 구현도 통과한다. 새 테스트 자체의 양쪽 실측은 프로브에서 **옛 코드 위에 새 테스트를 먼저 돌려** 40건이 실패(FAIL 24 · ERROR 16)한 것으로 보였고, 옛 코드에서도 통과하는 8건은 대조군·회귀 고정용이다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_envelope.TestChangeScopeGrammar tests.test_envelope.TestChangeScopeRegressionOnRecordedContracts"
  - id: check-2
    command: "grep -q '경로로 읽지 않' core/templates/tech-spec.md"
  - id: check-3
    command: "grep -qE 'bin/romeo route --fixtures fixtures/requests --report$' .github/workflows/harness.yml && ! grep -q 'continue-on-error' .github/workflows/harness.yml"
  - id: check-4
    command: "bin/romeo route --fixtures fixtures/requests --report"
  - id: check-5
    command: "python3 -m unittest tests.test_run_unit.TestDelegationCommandsMatchRunbook tests.test_run_unit.TestAttemptsDrift tests.test_run_unit.TestAttemptBaseShaFollowsReapproval"
  - id: check-6
    command: "python3 -m unittest tests.test_runbook_procedure.TestReapprovalRuleIsConditional tests.test_runbook_procedure.TestAttemptsCommittedCheck tests.test_runbook_procedure.TestDelegationBlockMatchesRunUnit"
  - id: check-7
    command: "bin/romeo run-unit check --unit feat-20260902-scope-grammar-procedure-drift-z5mv --base-sha HEAD"
  - id: check-8
    command: "test \"$(grep -E '^\\| Q-(3[6-9]|4[0-2]) \\|' docs/planning/open-questions.md | grep -c '해소(2026-09-02')\" -eq 7"
  - id: check-9
    command: "grep -q '^| D-80 |' docs/decisions/decision-register.md"
  - id: check-10
    command: "python3 -m unittest tests.test_policy.TestFixtureReportExit"
  - id: check-11
    command: "python3 -m unittest discover -s tests"
  - id: check-12
    command: "bin/romeo compile --check"
  - id: check-13
    command: "bin/romeo validate"
  - id: check-14
    command: "bin/romeo doctor --strict --scope repository"
  - id: check-15
    command: "bin/romeo fixtures check"
  - id: check-16
    command: "bin/romeo fixtures parity --report"
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
