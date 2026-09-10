---
id: init-20260911-m5-attach-update-rollback-sauc
type: spec
title: M5 attach — 하네스를 남의 저장소에 붙이고 갱신·복원한다
unit: T2
mode: delivery
intent: mixed
facets: [tooling, docs, security]
gates: [privacy-security]
profile: deep
blast_radius: large
uncertainty: medium
status: done
approved_at: '2026-09-11T03:06:09+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: '2026-09-11T03:37:50+09:00'
parent: null
inputs: [inputs/ac-rebuttal-20260911.md, inputs/ac-rebuttal-20260911-round2.md, inputs/ac-rebuttal-20260911-ac9.md]
evidence: [evidence/run_68f8e0cf3c09.yaml, evidence/run_877628bab8bd.yaml, evidence/run_5f973032a158.yaml]
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T2=deep', 'profile:gate.any=kept', 'profile:blast.large=kept', 'profile:uncertainty.medium=kept',
    'overlay:gate.any', 'overlay:unit.t2.parts', 'overlay:profile.standard-or-deeper', 'guard:permission-escalation',
    'guard:production-deploy', 'guard:deletion', 'warn:PART_PENDING_GATE']
  history: []
created: '2026-09-11'
updated: '2026-09-11'
approval_history:
- {approved_at: '2026-09-11T02:30:20+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-11T02:31:46+09:00',
  reason: AC-9 의 실재성 기준을 판정 명령을 실행한 하네스 저장소의 로컬 이력으로 명시 — AC-9 단독 반박 반영}
- {approved_at: '2026-09-11T02:31:46+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-11T03:06:09+09:00',
  reason: '1·2회차 검토가 RUNBOOK §4 의 방어 검사(review-tree-before/after) 없이 돌아, 그 판정이 어느 산출물을 본 것인지 하네스가 확인할
    수 없다(close 의 REVIEW_VERDICT UNVERIFIED). 확인란과 검증 계획은 바꾸지 않는다 — 같은 산출물을 그 기록과 함께 다시 검토받기 위한 재승인이다'}
---

# M5 M1 — 부착을 선언한다: 매니페스트와 리비전, 그것을 읽는 doctor

> 깊이 **Deep** · 단위 T2 · 모드 delivery · 의도 mixed · 영역 tooling, docs, security · 게이트 privacy-security
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve init-20260911-m5-attach-update-rollback-sauc --by <승인자>` 로 기록한다.
> 이 Spec 은 Charter 의 **첫 마일스톤 M1** 만 담는다. M2~M4 는 각각 별도 작업 단위로 연다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** `romeo doctor --strict --scope repository` 가 **이미 있는 부착 정본**(`scenarios/10-attach-payload.md` 의 「놓는 것」 절)을 읽어 부착 여부를 판정하게 한다. 그리고 부착된 저장소에 **어느 하네스 리비전이 붙었는지**를 남긴다.
- **왜 지금:** 지금 `doctor` 는 부착 여부와 **거꾸로** 답한다 — 안 붙인 저장소는 통과(exit 0), 붙인 저장소는 실패(exit 1, 2026-09-04 실측). 부재가 일치로 읽히고(Q-53), 대상의 기존 스킬 8개가 부착 실패로 세어지기 때문이다(Q-55). **요구하는 자리와 보는 자리가 갈려 있다** — 「놓는 것」 정본을 `tests/test_attach_runbook.py` 는 읽는데 `doctor` 는 읽지 않고, 그 구멍을 시나리오 문서가 「4번을 단독으로 쓰지 않는다」는 **주의로** 메우고 있다. 주의는 집행이 아니다(§11).
- **기대 결과:** 빈 저장소에 그 명령을 걸면 **빠진 경로를 인쇄하며 실패**하고, 시나리오 10 대로 붙인 저장소에서는 **통과**한다. 시나리오 문서의 「4번을 단독으로 쓰지 않는다」 주의가 필요 없어진다. 붙인 저장소를 열면 `.harness/compiled.yaml` 의 `harness_revision` 으로 어느 리비전이 붙었는지 읽을 수 있다.
- **수용 기준:** 아래에서 「**판정 명령**」은 `bin/romeo doctor --strict --scope repository --root <해당 루트>` 이고, **하네스 저장소 안에서** 실행한다. 「**사본**」은 시나리오 10 의 「놓는 것」 절대로 만든 임시 부착 사본이다.
  - [x] AC-1 「놓는 것」이 요구하는 경로가 하나도 없는 빈 루트에서 판정 명령의 종료 코드가 0 이 아니고, 출력이 finding id `ATTACH_INCOMPLETE` 와 빠진 경로 문자열을 담는다.
  - [x] AC-2 하네스 저장소 자신에서 판정 명령의 종료 코드가 0 이다.
  - [x] AC-3 사본에서 판정 명령의 종료 코드가 0 이다.
  - [x] AC-4 사본에서 「놓는 것」이 요구하는 경로 하나를 지우면 판정 명령의 종료 코드가 0 이 아니고, 출력이 finding id `ATTACH_INCOMPLETE` 와 지워진 그 경로 문자열을 담는다.
  - [x] AC-5 `scenarios/10-attach-payload.md` 의 「놓는 것」 절에 새 경로 한 줄을 더했을 때, 그 경로가 사본에 **없으면** 판정 명령의 종료 코드가 0 이 아니고 그 경로 문자열이 출력에 나오며, 그 경로를 사본에 **놓으면** 종료 코드가 0 이다.
  - [x] AC-6 사본의 `.harness/compiled.yaml` `outputs` **밖**에 심링크 스킬을 심으면 판정 명령의 종료 코드가 0 이고, `outputs` **안**의 스킬을 같은 방식으로 심링크로 바꾸면 0 이 아니다 — 심링크 자체가 놓인 위치가 안팎의 기준이다.
  - [x] AC-7 한 번의 검사 실행이 사본에 `bin/romeo compile --root <사본>` 을 돌리고, 같은 실행 안에서 사본의 `harness_revision` 과 하네스 저장소 HEAD 를 함께 읽어 비교했을 때 두 값이 같다.
  - [x] AC-8 사본의 `harness_revision` 키가 없거나 값이 빈 문자열이면 판정 명령의 종료 코드가 0 이 아니고, 출력이 finding id `ATTACH_REVISION_MISSING` 을 담는다.
  - [x] AC-9 사본의 `harness_revision` 이 40자 hex 커밋 식별자이면서 판정 명령을 실행한 하네스 저장소의 **로컬 이력**(`git cat-file -e <값>`)에 없으면, 판정 명령의 종료 코드가 0 이 아니고 출력이 finding id `ATTACH_REVISION_UNKNOWN` 을 담는다 — 원격만 가진 커밋은 이 기준에서 「없음」이다.
- **위험과 되돌리기:** 이 마일스톤은 **실제 프로젝트 저장소에 아무것도 쓰지 않는다** — 검증이 쓰는 것은
  임시 디렉터리의 부착 사본뿐이고, `My-Automated-Worker/instagram-dm-sender` 는 Charter M4 에서만 쓴다.
  실패하면 통합 커밋 하나를 `git revert` 하고 `bin/romeo compile` 로 산출물을 재생성한다. 판정이 엄해지므로
  **지금 통과하던 것이 실패할 수 있다** — 그것이 이 단위의 목적이고, 실패가 곧 결함의 발견이다.
- **결정 필요:** 없음. 복제냐 참조냐(Q-54)는 Charter M2 가 결정한다 — M1 은 지금의 부착 방식을 사실로 받아
  매니페스트의 **형식과 검사가 서는 자리**만 세운다.

## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/attach.py` (새 파일 · 「놓는 것」 정본을 읽는 `required_paths`·`missing` — 지금 `tests/` 에 있는 것을 옮긴다) · `romeo/doctor.py` (그 함수를 읽는 검사와 스킬 검사 범위) · `romeo/compile.py` (`harness_revision` 기록) · `tests/test_attach_runbook.py` (옮긴 자리에서 import) · `tests/test_attach_manifest.py` (새 파일) · `.harness/compiled.yaml` (재생성 산출물) · `scenarios/10-attach-payload.md` (판정이 바뀌므로 기대 출력과 「단독으로 쓰지 않는다」 주의를 고친다) · `docs/work/init-20260911-m5-attach-update-rollback-sauc/`
- 영향을 받는 부분: `bin/romeo doctor` 의 종료 코드 (엄해진다) · CI 의 doctor 단계 · `docs/planning/open-questions.md` 의 Q-53·Q-55 상태 (닫는 것은 통합 뒤 별도 커밋)
- 바꾸지 않는 것(비범위): 실제 프로젝트 저장소의 어떤 파일도 바꾸지 않는다 · `romeo attach`·`update`·`rollback` 하위 명령 (M2·M3) · `plan_outputs` 가 읽는 소스 경로 (Q-54 · M2) · **「놓는 것」 목록의 내용** — 정본은 그대로 두고 읽는 자리만 늘린다 · 요구사항 원본 `docs/requirements/attach-requirements.md`

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 부착 정본을 읽는 자리를 테스트 밖으로 옮긴다 | 지금 `tests/test_attach_runbook.py` 에 있는 `required_paths(runbook)`·`check(root, paths)` 를 `romeo/attach.py` 로 옮긴다. **정본은 옮기지 않는다** — 여전히 `scenarios/10-attach-payload.md` 의 「놓는 것」 절이고, 옮기는 것은 그것을 읽는 코드다. 기존 테스트는 새 자리에서 import 한다 | 소비: `scenarios/10-attach-payload.md` 의 「놓는 것」 → 생산: `romeo.attach.required_paths` · `romeo.attach.missing(root)` | `python3 -m unittest tests.test_attach_runbook` 이 옮긴 뒤에도 통과하는 것을 확인 (회귀) | 함수를 테스트 파일로 되돌린다 |
| 2 | doctor 가 그 정본을 읽어 판정한다 | `romeo/doctor.py` 가 `romeo.attach.missing(root)` 를 불러 빠진 경로를 finding 으로 내고, `doctor()` 반환의 `attach` 에 `completeness` 키로 실어 `doctor_problem_count` 의 `repository` 합에 더한다. finding 은 빠진 경로 문자열을 담는다 | 소비: 1의 `romeo.attach.missing` (**목록을 코드에 복사하지 않고 매번 읽는다** — AC-4 가 그것을 판별한다) → 생산: finding id `ATTACH_INCOMPLETE` | 빈 tmpdir · 하네스 저장소 · 사본에 각각 걸어 종료 코드와 finding id 를 확인 (AC-1~AC-5) | 검사 호출과 합산 한 줄 revert |
| 3 | 검사 대상을 하네스가 놓은 것으로 좁힌다 | `romeo/doctor.py` 의 `probe_skill_files(root)` 가 `.harness/compiled.yaml` 의 `outputs` 를 읽어, 그 목록이 담는 경로에 놓인 스킬만 판정에 센다. **검사 종류는 하나도 없애지 않는다** — 목록 밖의 것도 같은 검사를 돌려 인쇄하되 「대상의 기존 자산」으로 구분하고 합계에서 뺀다 | 소비: `.harness/compiled.yaml` 의 `outputs` → 생산: `probe_skill_files` 의 각 항목에 `owned`(하네스가 놓음)·`foreign`(대상 기존) 구분 | 목록 밖에 심링크 스킬을 심은 tmpdir 에서 종료 코드가 0 인 것과, 목록 안의 것을 같은 방식으로 깨뜨리면 0 이 아닌 것을 확인 (AC-6) | 범위 축소 revert |
| 4 | 어느 리비전이 붙었는지 남긴다 | `romeo/compile.py` 가 `.harness/compiled.yaml` 을 쓸 때 `harness_revision` 에 **명령을 실행한 하네스 저장소**의 HEAD SHA 를 기록한다. 하네스 저장소가 git 이 아니면 그 사실을 값으로 남긴다(빈 문자열로 두지 않는다) | 소비: 없음 → 생산: `.harness/compiled.yaml` 의 `harness_revision` | `bin/romeo compile --root <tmpdir 부착본>` 뒤 같은 검사 실행이 두 값을 함께 읽어 비교 (AC-7) | 필드 제거 |
| 5 | 리비전을 요구하는 자리와 보는 자리를 같게 둔다 | 2의 `check_attach_manifest` 가 `harness_revision` 의 부재와 「하네스 저장소에 실재하지 않는 커밋」을 finding 으로 낸다 | 소비: 2의 `check_attach_manifest` · 4의 `harness_revision` → 생산: finding id `ATTACH_REVISION_MISSING`(키 부재·빈 값) · `ATTACH_REVISION_UNKNOWN`(실재하지 않는 커밋) | 키를 지운 사본·빈 값 사본·없는 SHA 사본 셋에서 각각 종료 코드와 finding id 를 확인 (AC-8·AC-9) | 검사 두 줄 revert |
| 6 | 판정이 바뀐 것을 시나리오가 따라간다 | `scenarios/10-attach-payload.md` 의 「검증」 절에서 **「4번을 단독으로 쓰지 않는다」 주의를 걷어낸다** — 그 주의는 집행이 없던 자리를 메우던 것이고, 이제 4번이 1번과 같은 정본을 읽는다. 새 종료 코드와 실패 사유를 적는다 | 소비: 2·3·5의 finding id → 생산: 시나리오 문서의 기대 출력 | 문서가 인쇄하는 명령을 그대로 실행해 적힌 종료 코드와 같은 것을 확인 | 문서 revert |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 페이로드(하네스를 부착한 프로젝트) 작업 단위의 `required_checks` 에
**하네스 자신의 테스트**를 넣지 않는다 — `python3 -m unittest discover -s tests`(하네스 저장소의 테스트),
`bin/romeo` 의 자기 검사(`compile --check` · `validate` · `doctor` · `fixtures …`)가 그것이다.
넣으면 하네스가 깨진 동안 그 페이로드 단위가 닫히지 못한다. 그 단위의 산출물은 멀쩡한데 완료가 서지 않는 것이고,
그때 고쳐야 할 것은 그 단위가 아니라 하네스다 — 두 판정을 한 검사에 묶으면 어느 쪽이 깨졌는지 구분되지 않는다
(근거: `feat-20260829-license-field-46an` 의 check-5 가 이 형태였다).
하네스 저장소 **자신**을 대상으로 하는 작업 단위에서는 그 검사들이 정당하다 — 그때는 그것이 이 단위의 산출물이기 때문이다.
**이 단위는 하네스 저장소 자신이 대상이므로 아래 검사들이 정당하다.**

**종료 코드 자체가 조건이다.** 검사에 적는 것은 `id` 와 `command` 둘뿐이고, 그 명령의 종료 코드 0 이 통과다.
기대를 문장으로 따로 적는 자리는 두지 않는다 — 사람은 그것을 조건으로 쓰는데 기계는 판정에 쓰지 않으므로,
그 검사는 무엇을 확인하는지 적혀 있는 채로 아무것도 확인하지 않는 **빈 검사**가 된다(2026-08-31 실측으로 제거).
확인하고 싶은 조건이 있으면 그 조건을 **명령으로** 쓴다.
같은 이유로 옵션이 판정을 만드는 명령은 그 옵션까지 적는다 — 예: `bin/romeo doctor` 는 옵션 없이 쓰면 항상 exit 0 이라 빈 검사이고,
부착 검증(K-68)을 실제로 판정하게 하려면 `bin/romeo doctor --strict --scope repository` 로 쓴다(Q-21).

그래서 `|| true` 를 붙이지 않는다 — 종료 코드를 항상 0 으로 만들어 위반을 통과시킨다.
부정 조건은 `!` 로 쓴다: `! grep -q '<있으면 안 되는 것>' <파일>`.

**어느 검사가 판별 검사인가**(§11 — 판별 검사만 승인 전에 양쪽 상태에서 실측한다): check-1 만 **판별 검사**다(이 단위가 없으면 실패해야 한다 — 기존 상태 exit 1 실측).
check-2~check-6 은 **회귀 방지 검사**이므로 양쪽 실측의 대상이 아니다 — 기존 상태에서 전부 exit 0 을 실측했다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_attach_manifest -v"
  - id: check-2
    command: "bin/romeo doctor --strict --scope repository"
  - id: check-3
    command: "python3 -m unittest tests.test_attach_runbook -v"
  - id: check-4
    command: "python3 -m unittest discover -s tests"
  - id: check-5
    command: "bin/romeo compile --check"
  - id: check-6
    command: "bin/romeo validate docs/work/init-20260911-m5-attach-update-rollback-sauc"
```

## 위험·백업·복구

hard gate 가 발동했다. 승인 전 상태 변경 0건.

- **영향 범위:** 하네스 저장소의 `romeo/doctor.py`·`romeo/compile.py`·새 `core/policy/attach.yaml`·새 테스트·
  `scenarios/10-attach-payload.md`·재생성되는 `.harness/compiled.yaml`. 그 밖에 쓰는 곳은 검증이 만드는
  **임시 부착 사본**뿐이다 — 실제 프로젝트 저장소는 Charter M4 에서만 쓴다. 게이트 `privacy-security` 가
  발동한 이유(부착이 대상의 실행 권한 경계를 바꾼다, Q-58)는 **Charter M2 의 몫**이다.
- **사전 백업:** 하네스 저장소의 git 이력. 작업은 격리 워크트리에서 하고 통합 전까지 `main` 은 영향받지 않는다.
- **복구 방법:** 통합 커밋 하나를 `git revert <SHA>` 한 뒤 `bin/romeo compile` 로 산출물을 재생성하고
  `bin/romeo doctor --strict --scope repository` 로 되돌아온 것을 확인한다.
- **확인할 내용(승인자용):** ① 이 단위가 대상 저장소에 아무것도 쓰지 않는다는 것 — 부착 자동화는 M2 다.
  ② `doctor` 의 판정이 **엄해진다**는 것 — CI 가 그 명령을 부르므로 통합 직후 빨간불이 될 수 있고,
  그때 고칠 것은 검사가 아니라 부착 상태다.
- **승인 기록:** evidence.approvals 에 남긴다


## 증거

close PASS · 2026-09-11T03:37:50+09:00 · HEAD f027f3818ef0 · 검사 기록 run_5f973032a158

- [evidence/run_68f8e0cf3c09.yaml](evidence/run_68f8e0cf3c09.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0]
- [evidence/run_877628bab8bd.yaml](evidence/run_877628bab8bd.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0]
- [evidence/run_5f973032a158.yaml](evidence/run_5f973032a158.yaml) — exit codes [0, 0, 0, 0, 0, 0, 0, 0, 0] (검사 기록)
