---
id: init-20260904-attach-payload-manual-rreq
type: spec
title: 페이로드 1건 손 부착 — 하네스를 자기 저장소 밖에서 처음 돌린다
unit: T2
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: deep
blast_radius: medium
uncertainty: high
status: done
approved_at: '2026-09-04T17:29:01+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-09-04T18:12:29+09:00'
parent: null
inputs: [../feat-20260831-bmad-attach-probe-tgnb/spec.md]
evidence: [evidence/run_1b6546d3394e.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T2=deep', 'profile:uncertainty.high=kept', 'overlay:unit.t2.parts', 'overlay:profile.standard-or-deeper',
    'warn:PART_PENDING_GATE']
  history: []
created: '2026-09-04'
updated: '2026-09-04'
---

# 페이로드 1건 손 부착 — 하네스를 자기 저장소 밖에서 처음 돌린다

> 깊이 **Deep** · 단위 T2 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve init-20260904-attach-payload-manual-rreq --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** Romeo 하네스를 실제 제품 저장소 1건에 손으로 부착하고 그 저장소의 작업 1건을 관통시켜 M5 attach 의 요구사항을 실측으로 얻는다
- **왜 지금:** 작업 단위 24건이 전부 하네스 자신을 겨눈 `tooling`·`docs` 라, 하네스는 자기 저장소 밖에서 한 번도 돈 적이 없다. `attach` 명령(M5)을 만들기 전에 손으로 한 번 밟아야 그 명령이 상상한 절차가 아니라 실측 위에 선다. **승인 전 프로브가 이미 다섯 가지를 잡았고**(그중 하나는 대상 저장소의 보안 규칙을 지운다), 그것들은 손으로 밟지 않았으면 M5 를 다 만든 뒤에야 드러났을 것들이다.
- **기대 결과:** 대상 저장소(`My-Automated-Worker/instagram-dm-sender`)에 하네스가 부착돼 그 저장소에서 라우터가 돌 수 있다. 부착이 **무엇을 놓고 무엇을 덮고 무엇을 되살려야 하는지**가 런북 하나에 적힌다. 그리고 부착 여부를 **부재를 통과로 읽지 않고** 판정하는 검사가 선다 — 지금 `doctor` 는 아무것도 부착하지 않은 빈 저장소도 통과시킨다.
- **수용 기준:**
  - [x] AC-1 런북 `scenarios/10-attach-payload.md` 가 서고 다섯 절 — 「부착 전 확인」·「놓는 것」·「덮는 것과 보존」·「검증」·「되돌리기」 — 을 전부 담는다.
  - [x] AC-2 부착 판정 검사가 런북의 「놓는 것」 목록을 **파일에서 읽어** 대조한다. 목록에서 한 항목을 빼면 검사는 그 항목을 조용히 건너뛰는 것이 아니라 **바뀐 목록으로 대조한다** — 검사 안에서 목록을 바꿔 넣어 그 사실을 매번 재확인한다.
  - [x] AC-3 그 검사가 **부착되지 않은 경로에서 실패하고 부착된 경로에서 통과한다** — 두 경로를 검사 안에서 각각 만들어 양쪽을 판정한다.
  - [x] AC-4 부착이 대상의 `.claude/settings.json` 에서 **지운 항목이 런북 「덮는 것과 보존」 절에 실제 값으로 적힌다** — 최소한 `Write(~/.coupang-auto/**)`. **복원하지 않는다**: 사용자가 「기존 프로젝트 규칙은 다 무시하고 부착을 우선한다」로 확정했다(2026-09-04). 기록만 남기는 이유는 그것이 M5 `attach` 가 반드시 다뤄야 할 실측이기 때문이다.
  - [x] AC-5 대상 저장소 `CLAUDE.md` 의 부착 전 106줄이 managed block **밖에** 그대로 남는다 — 부착 전 파일과 부착 후 marker 앞부분을 대조해 판정한다 (증거 `attach-target-claude-md`). **회귀 방지 검사다** — 프로브에서 이미 참이었고, 부착이 그것을 깨지 않는지만 본다.
  - [x] AC-6 이 부착이 낸 관측이 `docs/planning/open-questions.md` 에 Q 항목으로 열린다 — 최소한 「`doctor` 가 부재를 통과로 읽는다」와 「부착이 하네스 소스 트리를 복제한다」 두 건. 고치지 않고 열어만 둔다(§12).
- **위험과 되돌리기:** 부착은 대상 저장소의 `.claude/settings.json` 의 `deny` 배열을 통째로 덮어 그 저장소가 갖고 있던 보호 규칙 두 건(`~/.coupang-auto` 쓰기 금지)을 **지운다**. JSON 이라 managed marker 를 넣을 수 없어 병합이 아니라 대체다. **사용자가 그 저장소를 지금 쓰지 않으므로 복원하지 않고 부착을 우선하기로 확정했다(2026-09-04)** — 그래서 이것은 이 단위에서 **감수하는 결과**이고, 위험으로 남는 것은 「그 사실이 기록되지 않는 것」뿐이다(AC-4 가 그것을 막는다). 부착은 **대상이 `git status` clean 인 것을 먼저 확인한다** — 그러면 부착분이 `git status` 만으로 갈리고 아래 두 명령이 완전한 복구가 된다.
  되돌리기 — 대상 저장소: `git checkout -- .claude/settings.json CLAUDE.md && git clean -fd .agents .claude/agents .claude/skills .harness adapters core provenance vendor skills/repo-archive AGENTS.md THIRD_PARTY_NOTICES.md` (부착 전 clean 이었으므로 이 두 명령이 부착 전 상태로 되돌린다). Romeo-Harness: `git revert <구현 커밋>`. 운영 상태·외부 상태·비용은 건드리지 않는다.
- **결정 필요:** 없음 — 대상 저장소 쓰기는 그 저장소를 작업 공간으로 삼는 별도 실행에서 한다(사용자 확정 2026-09-04). 이 단위의 `allowed_paths` 는 이 저장소 안에 머문다.


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `scenarios/10-attach-payload.md` · `tests/test_attach_runbook.py` · `docs/planning/open-questions.md` · `docs/work/init-20260904-attach-payload-manual-rreq/`
- 영향을 받는 부분: 대상 저장소 `~/orca/workspaces/My-Automated-Worker/instagram-dm-sender` — **이 저장소 밖이라 쓰기 상한에 넣지 않는다.** 그 저장소의 부착은 그것을 작업 공간으로 삼는 별도 실행이 하고, 이 단위는 그 결과를 **읽어** 판정하고 증거로 기록한다(사용자 확정 2026-09-04).
- 바꾸지 않는 것(비범위): `romeo/compile.py` 와 `romeo/doctor.py` — 프로브가 잡은 결함(부재를 통과로 읽는 것, 소스 트리 복제를 요구하는 것)은 **고치지 않고 열어 둔다**(§12·charter 중단 조건 ③). 대상 저장소의 BMad 도 건드리지 않는다. `attach` 명령을 만들지 않는다(M5).

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 부착이 무엇을 놓고 무엇을 덮는지 런북에 적는다 — 승인 전 프로브가 실측한 것을 그대로 | `scenarios/10-attach-payload.md` 신설. 다섯 절과, 「놓는 것」 절 안에 백틱 경로 목록(프로브 실측: `core/`·`adapters/`·`vendor/`·`provenance/`·`skills/repo-archive/`·`.harness/bindings.yaml` 과 compile 산출물) | 소비: 없음 → 생산: 런북 경로 `scenarios/10-attach-payload.md`, 「## 놓는 것」 절의 백틱 경로 목록 형식 | 다섯 절 제목이 전부 있는지 검사(check-2)가 exit 0 | 파일 삭제 |
| 2 | 부착 여부를 부재를 통과로 읽지 않고 판정하는 검사 | `tests/test_attach_runbook.py` 신설. 런북의 「## 놓는 것」 절에서 백틱 경로를 **읽어** 주어진 루트와 대조한다. 검사 안에서 ① 빈 임시 저장소(부착 안 됨) ② 이 저장소(부착됨) 두 루트를 각각 판정하고, ③ 목록을 바꿔 넣어 바뀐 목록으로 대조하는지 재확인한다 | 소비: 런북 경로와 「## 놓는 것」 절 형식 → 생산: `attach_runbook.required_paths(runbook_path)` 와 `attach_runbook.check(root, paths)` | check-1 이 exit 0 | 파일 삭제 |
| 3 | 대상 저장소에 실제로 부착하고 덮인 보호 규칙을 되살린다 | **이 저장소 밖 — 별도 실행.** 대상이 clean 인지 확인 → 런북대로 놓기 → `compile`·`notices` → `.claude/settings.json` 에서 **지워진 항목을 런북에 받아 적는다**(복원하지 않는다) | 소비: 런북의 「놓는 것」·「덮는 것과 보존」 → 생산: 부착된 대상 저장소 | 이 저장소에서 검사를 대상 루트로 실행해 exit 0 + AC-4·AC-5 판정 명령이 exit 0 (증거 3건) | 위 「위험과 되돌리기」의 두 명령 |
| 4 | 부착이 낸 관측을 열어 둔다 | `docs/planning/open-questions.md` 에 Q 항목 추가 — 최소 2건(doctor 가 부재를 통과로 읽는다 · 부착이 하네스 소스 트리를 복제한다) | 소비: 단위 3 이 실제로 겪은 것 → 생산: Q 번호 | check-3 이 exit 0 | 문서 revert |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**판별 검사와 회귀 방지 검사** — check-1·2·3 은 **판별 검사**다(이 단위가 없으면 실패해야 한다).
check-4·5 는 **회귀 방지 검사**이므로 양쪽 상태에서 통과가 예상되고, 두 상태 실측의 대상이 아니다(§11).

승인 전 양쪽 실측 (2026-09-04):

| 검사 | 구현 전 | 가상 완료 | 그럴듯한 거짓 값 반례 |
| --- | --- | --- | --- |
| check-1 | exit 1 | exit 0 | — |
| check-2 | exit 1 | exit 0 | 다섯 절 중 「## 검증」 하나만 지우면 **exit 1** |
| check-3 | exit 1 | exit 0 | 단위 id 를 담은 Q 행이 **1건뿐이면 exit 1** |
| check-6 | exit 1 | exit 0 | — (AC-4 가 요구하는 실제 값이 런북에 없으면 막는다) |
| check-4 | exit 0 (회귀) | — | — |
| check-5 | exit 0 · **237초** (상한 600초의 40% — 경고 임계 80% 아래) | — | — |

check-3 의 첫 초안은 `doctor` 라는 낱말을 찾는 grep 이었고, 그 낱말을 담은 Q 행이 **이미 1건 있어 구현 전에도 통과**했다 — 빈 검사였다. 단위 id 를 가리키게 바꿔 판별력을 얻었다.

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
    command: "python3 -m unittest tests.test_attach_runbook -v"
  - id: check-2
    command: "for h in '## 부착 전 확인' '## 놓는 것' '## 덮는 것과 보존' '## 검증' '## 되돌리기'; do grep -qF \"$h\" scenarios/10-attach-payload.md || exit 1; done"
  - id: check-3
    command: "test $(grep -cE '^\\| Q-[0-9]+ \\|.*init-20260904-attach-payload-manual-rreq' docs/planning/open-questions.md) -ge 2"
  - id: check-4
    command: "bin/romeo validate docs/work/init-20260904-attach-payload-manual-rreq"
  - id: check-5
    command: "python3 -m unittest discover -s tests"
  - id: check-6
    command: "grep -qF 'Write(~/.coupang-auto/**)' scenarios/10-attach-payload.md"
```


## 증거

close PASS · 2026-09-04T18:12:29+09:00 · HEAD 9af85f36015c · 검사 기록 run_1b6546d3394e

- [evidence/run_1b6546d3394e.yaml](evidence/run_1b6546d3394e.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
