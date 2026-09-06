---
id: feat-20260906-m3-close-foreign-repo-ik3u
type: spec
title: 관통을 끝낸다 — 남의 저장소의 단위를 구현·검토·close 한다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs, security]
gates: [privacy-security]
profile: deep
blast_radius: medium
uncertainty: high
status: done
approved_at: '2026-09-06T12:39:25+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-09-06T14:30:27+09:00'
parent: init-20260904-attach-payload-manual-rreq
inputs: [../init-20260904-attach-payload-manual-rreq/charter.md, ../feat-20260904-m2-router-foreign-repo-ct5h/spec.md]
evidence: [evidence/run_cc685a7dfa45.yaml, evidence/run_3e1b612799e2.yaml, evidence/run_63bbd145a5ba.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:gate.any=kept', 'profile:uncertainty.high->deep',
    'overlay:gate.any', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-06'
updated: '2026-09-06'
approval_history:
- {approved_at: '2026-09-06T07:09:32+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-06T12:39:25+09:00',
  reason: '2회차 검토자 FAIL(AC_UNMET) — AC-5 가 「close 가 추가로 요구한 것을 그 요구를 인쇄한 명령과 함께 적는다」를 요구하는데, 그 close 실행들은
    코디네이터가 대상 저장소에서 라벨 없이 돌려 evidence 에 남지 않았다. 런북이 적은 것은 observations.md 의 요약 표에만 대응해 K-51 의 「증거는 손으로
    쓰지 않는다」를 어긴다. 과거 실행은 소급 기록할 수 없고 대상 단위는 이미 done 이라 같은 출력을 다시 낼 수 없다 — 원인이 산출물이 아니라 완료 정의여서 AC-5 만
    고쳤다. 기준을 기록에서 **재현**으로 옮긴다: 임시 루트에 그 요구가 미충족인 상태를 만들고 close 를 돌려 같은 검사 이름이 FAIL 로 인쇄되게 한다. required_checks
    5건과 다른 AC 는 그대로다. 사용자 확정 2026-09-06'}
---

# 관통을 끝낸다 — 남의 저장소의 단위를 구현·검토·close 한다

> 깊이 **Deep** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs, security · 게이트 privacy-security
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260906-m3-close-foreign-repo-ik3u --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** charter `init-20260904-attach-payload-manual-rreq` 의 **M3** — 대상 저장소(`My-Automated-Worker/instagram-dm-sender`)에 **이미 서 있고 이미 승인된** 단위 `feat-20260904-claude-md-rule-conflicts-bbn8` 을 구현하고, 반대 런타임 검토를 받고, `status: done` 으로 닫는다. 그 절차를 런북 `scenarios/12-close-foreign-repo.md` 하나에 고정하고, 완료를 **대상 저장소의 상태로** 판정하는 검사를 세운다.
- **왜 지금:** M2 가 참으로 만든 것은 「라우터가 남의 저장소에서 **분류**한다」 하나다. 구현·검토·close 를 남의 저장소 루트에 대해 돌린 적은 **한 번도 없다**. 그래서 하네스는 아직 자기 도구·문서가 아닌 것을 **판정**해 본 적이 없다 — 그것이 이 이니셔티브를 연 이유이고(charter 「중간에 멈춰도 되는 지점」), M3 없이는 「하네스가 하네스만 시험한다」가 해소되지 않는다.
- **기대 결과:** 대상 저장소의 그 단위가 `status: done` 이 되고 `required_checks` 9건이 전부 통과한다. 지금 그 저장소의 `CLAUDE.md` 에는 BMad·Romeo 두 규칙 블록이 서로를 모른 채 있고 다섯 지점에서 다른 것을 지시하는데, 그중 **C-3 은 승인 없이 착수할 근거로 읽힌다** — 이 관통이 그 자리를 못박는다. 그리고 close 를 남의 저장소에서 돌리는 절차가 런북 하나에 적히고, 그 절차가 **무엇을 더 요구했는지**가 종료 코드로 남는다.
- **수용 기준:**
  - [x] AC-1 런북 `scenarios/12-close-foreign-repo.md` 가 서고 다섯 절 — 「무엇이 더 필요한가」·「어디서 구현하는가」·「검토자를 어떻게 붙이는가」·「검증」·「되돌리기」 — 을 전부 담는다.
  - [x] AC-2 그 런북의 「검증」 절이 M3 의 완료 조건을 **조건 id 로** 고정하고, `tests/test_foreign_close.py` 가 그 목록을 **런북 파일에서 읽어** 자기 판정과 대조한다. 목록에서 한 항목을 빼면 검사는 그것을 조용히 건너뛰는 것이 아니라 **바뀐 목록으로 대조하고**, 판정 코드가 없는 조건 id 를 더하면 **그 자리에서 막힌다** — 검사 안에서 목록을 양쪽으로 바꿔 넣어 그 사실을 매번 재확인한다(M2 의 AC-2 와 같은 패턴 · Romeo §11).
  - [x] AC-3 그 검사가 **조건을 만족하지 않는 합성 루트에서 실패하고 만족하는 합성 루트에서 통과한다**. 반례는 빈 루트가 아니라 **그럴듯한 거짓 루트**여야 한다: ① `status: done` 까지 갔는데 증거의 종료 코드 하나가 `1` 인 것 · ② 닫혔는데 `review/` 에 검토자 봉투가 **없는** 것(자기 검토) · ③ 봉투는 있는데 판정이 `FAIL` 인 것. 빈 루트만으로 통과한 검사는 고치기 전 상태와 구별되지 않는다.
  - [x] AC-4 그 검사를 **실제 대상 저장소에 대해 돌려 통과**시킨다 — 세 조건이 전부 참인 것을 증거 `foreign-close-verdict` 로 남긴다. 그 단위의 구현·검토·close 는 **대상 저장소를 작업 공간으로 삼는 별도 실행**이 한다(charter 제약).
  - [x] AC-5 런북 「무엇이 더 필요한가」 절이, close 가 이 관통에서 **추가로 요구한 것**을 각각 **지금 다시 돌려 그 요구를 인쇄하는 명령**과 함께 적고, 그 명령을 실제로 돌린 것이 이 단위의 증거로 남는다. **과거 실행의 출력은 소급해 증거로 만들 수 없다**(K-51 — 증거는 손으로 옮겨 적지 않고 증거 기록 명령이 만든다) — 그래서 기준은 기록이 아니라 **재현**이다: 대상 단위 폴더를 임시 루트로 복사해 그 요구가 아직 충족되지 않은 상태를 만들고 `bin/romeo close --unit <대상 단위> --root <임시 루트> --dry-run` 을 돌리면 같은 검사 이름이 FAIL 로 인쇄된다. **임시 루트를 쓰는 이유는 대상 저장소가 이미 `done` 이라 그 상태를 되돌리지 않고는 같은 출력을 낼 수 없기 때문이다** — 닫힌 단위를 다시 열지 않는다. 요구한 것이 없었으면 「없었다」를 근거와 함께 적는 것이 결과다. 2회차 검토자가 이 자리를 잡았다 — 런북이 적은 요구가 `observations.md` 의 요약 표에만 대응하고 증거로 연결되지 않았다(D-80 재승인 2026-09-06).
  - [x] AC-6 이 관통이 낸 관측이 `docs/planning/open-questions.md` 에 이 단위 id 를 가리키는 Q 항목으로 **한 건 이상** 열린다. 고치지 않고 열어만 둔다(§12).
- **위험과 되돌리기:** 이 관통이 대상 저장소에서 바꾸는 것은 **`CLAUDE.md` 의 마커 밖 영역 한 절**과 그 단위 폴더뿐이다. 코드·설정·봇 동작·운영 상태·외부 상태·비용에는 닿지 않는다. 실제 위험은 하나다 — 그 절의 **C-3 판정을 뒤집어 적으면** 그 저장소에서 승인 없는 착수가 **문서로 정당화된다**. 그래서 C-3 은 이미 그 저장소의 승인에서 「Romeo §3(D-27) 우선」으로 확정돼 있고(2026-09-04), 이 단위는 그 확정을 **바꾸지 않는다**.
  되돌리기 — 대상 저장소: `git -C <대상> checkout -- CLAUDE.md` (미커밋 시) 또는 `git -C <대상> revert <커밋>` · `rm -rf <대상>/docs/work/feat-20260904-claude-md-rule-conflicts-bbn8`. Romeo-Harness: `git revert <구현 커밋>`. 부착분은 미커밋이므로 `git status --porcelain` 이 부착 직후 목록으로 돌아가는 것으로 확인한다.
- **결정 필요:** **대상 저장소에 커밋이 생긴다.** close 의 `CHECK_PLAN_COMMITTED` 와 `TASK_ANCHORED` 는 승인된 `spec.md` 가 **커밋돼** 있어야 판정하는데(`romeo/close.py:75-100`·`440-490`), 지금 대상 저장소의 `docs/work/<id>/` 는 미추적이다. 그래서 이 관통은 대상 저장소에 **로컬 커밋 1~2건**을 만든다 — `docs/work/<id>/`(승인된 spec) 과 `CLAUDE.md`(구현). **push 하지 않는다.** 부착분(`core/`·`adapters/`·`.harness/` 등)은 계속 미커밋으로 둔다 — 부착을 커밋하는 것은 이 단위의 범위가 아니다(§12). 되돌리기는 `git revert` 이고, 그 저장소의 원격 상태는 바뀌지 않는다.

## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `scenarios/12-close-foreign-repo.md` · `tests/test_foreign_close.py` · `docs/planning/open-questions.md` · `docs/work/feat-20260906-m3-close-foreign-repo-ik3u/`
- 영향을 받는 부분: 대상 저장소 `~/orca/workspaces/My-Automated-Worker/instagram-dm-sender` 의 `CLAUDE.md`(마커 밖 한 절)와 `docs/work/feat-20260904-claude-md-rule-conflicts-bbn8/` — **이 저장소 밖이라 쓰기 상한에 넣지 않는다.** 그 쓰기는 대상 저장소를 작업 공간으로 삼는 별도 실행이 하고, 이 단위는 그 결과를 **읽어** 판정하고 증거로 기록한다(M2 와 같은 분리 · 사용자 확정 2026-09-04). 그 별도 실행의 쓰기 상한은 대상 저장소의 `CLAUDE.md` 와 `docs/work/` 둘이다.
- 바꾸지 않는 것(비범위): `romeo/` 전부 — close 가 남의 루트에서 무엇을 요구하든 **이 단위에서 고치지 않는다**. 관측으로 열어 두고 M5 `attach` 에 넘긴다(§12·charter 중단 조건 ③). `scenarios/10-attach-payload.md` · `scenarios/11-router-foreign-repo.md` · `tests/test_foreign_router.py` 도 고치지 않는다 — M1·M2 는 이미 닫혔다. 대상 저장소의 **`CLAUDE.md` 마커 안**(108~381줄) · BMad 블록의 기존 문장 · `_bmad-output/` · `docs/agent-rules/` · `.claude/` 설정 · 코드 전부. 대상 저장소의 부착분을 커밋하는 것. 대상 저장소에 **push 하는 것**.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 남의 저장소에서 관통을 끝내는 절차를 다섯 절로 고정하고, 「검증」 절이 완료 조건을 조건 id 로 적는다 (AC-1·AC-2 앞부분) | `scenarios/12-close-foreign-repo.md` 신설 | 소비: `scenarios/11-router-foreign-repo.md` 의 「목록의 문법」 → 생산: 조건 id `unit-done` · `unit-checks-passed` · `unit-reviewed` 와 그 목록을 읽는 문법 | check-2 (다섯 절 전부 존재) | 파일 삭제 |
| 2 | 그 조건 id 목록을 런북에서 읽어 주어진 루트를 판정하는 검사를 만든다. 목록을 바꾸면 대조가 함께 바뀌고, 판정 코드가 없는 id 를 더하면 막힌다 (AC-2 뒷부분·AC-3) | `tests/test_foreign_close.py` 신설 | 소비: 1 의 조건 id 와 목록 문법 → 생산: `conditions()` · `check(root)` · `VERDICTS` | check-1 (합성 루트 양쪽 + 목록 조작 재확인이 전부 통과) | 파일 삭제 |
| 3 | 대상 저장소에서 별도 실행으로 그 단위를 **구현**한다 — `CLAUDE.md` 마커 밖에 「규칙 충돌 해소」 절을 쓰고 그 단위의 `required_checks` 9건을 증거로 남긴다 | 대상 저장소 `CLAUDE.md` · `docs/work/feat-20260904-claude-md-rule-conflicts-bbn8/`(이 저장소 밖 — 쓰기 상한 아님) | 소비: 1 의 「어디서 구현하는가」 절 → 생산: 그 단위의 증거 run 1건 | 그 단위의 `romeo evidence checks --root <대상>` 이 9/9 exit 0 | 대상에서 `git checkout -- CLAUDE.md` · `rm -rf docs/work/<id>/evidence` |
| 4 | 그 단위에 반대 런타임 read-only 검토자를 붙이고 `close` 로 닫는다 (AC-4) | 대상 저장소 `docs/work/feat-20260904-claude-md-rule-conflicts-bbn8/review/`·`task/`·`attempts.yaml` (이 저장소 밖) | 소비: 1 의 「검토자를 어떻게 붙이는가」 절, 3 의 증거 → 생산: 검토자 봉투 · `status: done` | 증거 `foreign-close-verdict` (2 의 검사를 실제 대상 루트에 대해 돌려 exit 0) | 대상에서 그 단위 폴더의 `review/`·`task/` 삭제 후 spec frontmatter 를 `active` 로 되돌린다 |
| 5 | close 가 **추가로 요구한 것**을 런북 「무엇이 더 필요한가」 절에 적고, 이 관통이 낸 관측을 열어 둔다 (AC-5·AC-6) | `scenarios/12-close-foreign-repo.md` (첫 절) · `docs/planning/open-questions.md` | 소비: 3·4 가 실제로 막힌 자리 → 생산: 요구 목록과 Q 항목 | check-3 (이 단위 id 를 가리키는 Q 행 ≥ 1) · 목록의 내용은 검토자가 본다 | `git revert` |

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

**판별 검사와 회귀 방지 검사(§11).** check-1·2·3 은 **판별 검사**다 — 이 단위가 없으면 실패해야 한다.
check-4·5 는 **회귀 방지 검사**라 양쪽 상태에서 통과가 예상되고, 두 상태 실측의 대상이 아니다.

AC-4 의 **실제 대상 부분**은 required_checks 가 아니라 **증거**가 판정한다 — 이 저장소 **밖**의 상태(대상 저장소)를 읽으므로,
검사에 넣으면 대상 저장소가 없는 머신(CI)에서 이 단위가 영원히 닫히지 않는다. M2 의 `foreign-router-verdict` 와 같은 자리다.
그 증거의 이름은 `foreign-close-verdict` 이고 명령은 `python3 tests/test_foreign_close.py --verdict <대상 루트>` 다.
AC-3 의 **합성 루트 양쪽**은 저장소 안에서 완결되므로 check-1 이 판정한다.

승인 전 양쪽 실측 (2026-09-06 · 프로브를 이 체크아웃에 만들고 실측 뒤 삭제 · `git status` 로 원복 확인):

| 검사 | 구현 전 | 가상 완료 | 그럴듯한 거짓 값 반례 |
| --- | --- | --- | --- |
| check-1 | exit 1 | exit 0 | 런북 「검증」 표에서 `unit-reviewed` **한 줄만** 지우면 exit 1 — 검사가 목록을 파일에서 읽고 있다는 증거다 |
| check-2 | exit 1 | exit 0 | 다섯 절 중 「## 검증」 **하나만** 「## 확인」으로 바꾸면 exit 1 |
| check-3 | exit 1 | exit 0 | Q 행은 그대로 두고 **가리키는 단위 id 만 다른 단위 것으로** 바꾸면 exit 1 — 「Q 행이 있는가」가 아니라 「이 단위를 가리키는가」를 본다 |
| check-4 | exit 0 (회귀) | — | — |
| check-5 | exit 0 · 129초 (재실행 상한 600초의 22% — 경고 임계 80% 아래) | — | — |

반례를 빈 값이 아니라 **그럴듯한 거짓 값**으로 잡은 이유는 §11 이다 — 빈 값은 고치기 전에도 막혔으므로 판별력을 증명하지 않는다.
`check(root)` 의 합성 루트 반례 셋(증거 종료 코드 1 · 검토자 봉투 없음 · 판정 FAIL)도 같은 이유로 **`status: done` 까지 간** 루트다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_foreign_close -v"
  - id: check-2
    command: "for h in '## 무엇이 더 필요한가' '## 어디서 구현하는가' '## 검토자를 어떻게 붙이는가' '## 검증' '## 되돌리기'; do grep -qF \"$h\" scenarios/12-close-foreign-repo.md || exit 1; done"
  - id: check-3
    command: "test $(grep -cE '^\\| Q-[0-9]+ \\|.*feat-20260906-m3-close-foreign-repo-ik3u' docs/planning/open-questions.md) -ge 1"
  - id: check-4
    command: "bin/romeo validate docs/work/feat-20260906-m3-close-foreign-repo-ik3u"
  - id: check-5
    command: "python3 -m unittest discover -s tests"
```

## 위험·백업·복구

hard gate 가 발동했다. 승인 전 상태 변경 0건.

- **영향 범위:** 대상 저장소에서 도는 모든 에이전트 세션의 **규칙 해석** — 특히 착수 전 승인 판정(C-3)과 부품 스킬 발동(C-1). 그 저장소의 코드·설정·봇 동작·운영 데이터·배포·외부 서비스에는 닿지 않는다. 이 저장소 쪽은 런북 1건·검사 1건·문서 2건이다.
- **사전 백업:** 별도 백업이 필요 없다 — 대상 저장소의 `CLAUDE.md` 는 git 추적 파일이고(HEAD `509e7d1`), 부착분은 미추적이라 `git status --porcelain` 만으로 무엇이 이 관통의 산출인지 갈린다. 구현 전에 그 목록을 증거로 인쇄한다.
- **복구 방법:** 대상 저장소 — `git -C <대상> checkout -- CLAUDE.md`(미커밋 시) 또는 `git -C <대상> revert <커밋>` · `rm -rf <대상>/docs/work/feat-20260904-claude-md-rule-conflicts-bbn8`. 되돌린 뒤 그 단위의 check-1~check-8 이 다시 rc=1 로 돌아오는 것으로 복구를 확인한다(지금 상태가 그것이다 — 2026-09-06 실측). 이 저장소 — `git revert <구현 커밋>`. **push 는 하지 않으므로 원격 상태는 어느 쪽도 바뀌지 않는다.**
- **확인할 내용(승인자용):** 두 가지다. ① **C-3 판정을 뒤집지 않는다** — 대상 저장소의 「규칙 충돌 해소」 절은 `Romeo §3(D-27) 우선`으로 이미 확정돼 있고(2026-09-04 그 저장소의 승인), 이 단위는 그 확정을 실행할 뿐 다시 정하지 않는다. 뒤집어 적히면 그 저장소에서 승인 없는 착수가 문서로 정당화된다. ② **대상 저장소에 로컬 커밋이 생긴다** — `docs/work/<id>/` 와 `CLAUDE.md` 두 건이고 push 하지 않는다. 부착분은 계속 미커밋으로 둔다.
- **승인 기록:** evidence.approvals 에 남긴다


## 증거

close PASS · 2026-09-06T14:30:27+09:00 · HEAD e2f71d6eb0b1 · 검사 기록 run_63bbd145a5ba

- [evidence/run_cc685a7dfa45.yaml](evidence/run_cc685a7dfa45.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_3e1b612799e2.yaml](evidence/run_3e1b612799e2.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- [evidence/run_63bbd145a5ba.yaml](evidence/run_63bbd145a5ba.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
