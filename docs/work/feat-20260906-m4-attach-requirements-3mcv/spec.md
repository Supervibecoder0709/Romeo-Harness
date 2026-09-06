---
id: feat-20260906-m4-attach-requirements-3mcv
type: spec
title: M1~M3 이 낸 구멍을 M5 attach 요구사항 목록으로 정리한다
unit: T1
mode: delivery
intent: write
facets: [docs, tooling]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
status: active
approved_at: '2026-09-06T21:59:12+09:00'
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
created: '2026-09-06'
updated: '2026-09-06'
---

# M1~M3 이 낸 구멍을 M5 attach 요구사항 목록으로 정리한다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 docs, tooling · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260906-m4-attach-requirements-3mcv --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 하네스를 남의 저장소에 손으로 붙여 본 세 번의 관통(M1 부착 · M2 라우터 · M3 close)이
  남긴 관측 16건을, 다음 이니셔티브가 그대로 집어 쓸 수 있는 **요구사항 목록 한 장**으로 모은다.
  각 항목이 어느 관통의 어느 실측에서 나왔는지 가리키게 하고, 그 가리킴이 낡으면 드러나게 하는 검사 1건을 붙인다.
- **왜 지금:** 관측이 지금은 `open-questions.md` 68건 안에 흩어져 있고, 「이건 다음에 `attach` 명령이 답할 것」
  이라는 판단이 각 항목 본문의 문장으로만 남아 있다. 다음 이니셔티브를 여는 사람이 그 68건을 다시 읽어
  같은 판단을 처음부터 해야 한다. 이 정리가 부모 이니셔티브의 마지막 조각이라, 이것이 끝나면 그 이니셔티브가 닫힌다.
- **기대 결과:** `docs/requirements/attach-requirements.md` 한 장에 요구사항이 서고, 세 관통이 낸 Q-53~Q-68
  **16건 전부**가 그 문서의 「올린 것」이나 「뺀 것」 어느 한쪽에 이유와 함께 나타난다. 목록에서 무언가가 빠지거나
  출처가 없는 것을 가리키면 `python3 -m unittest` 가 실패한다 — 문서가 조용히 낡지 않는다.
- **수용 기준:**
  - [ ] AC-1 `docs/requirements/attach-requirements.md` 가 서고, **`open-questions.md` 에서 M1~M3 세 단위를
        출처로 가진 Q 전부**(2026-09-06 실측 Q-53~Q-68 16건)가 「올린 것」 표 또는 「뺀 것」 표
        어느 한쪽에 정확히 한 번 나타난다 — 개수가 아니라 그 집합이 판정 기준이다
  - [ ] AC-2 「올린 것」의 각 행이 출처로 **Q id · 작업 단위 id · 마일스톤 번호(M1|M2|M3)** 셋을 적고,
        그 Q id 가 `docs/planning/open-questions.md` 에 실재하며 그 단위 id 가 `docs/work/` 에 실재한다
  - [ ] AC-3 「뺀 것」의 각 행에 **왜 attach 요구사항이 아닌지**가 한 줄로 적히고,
        그 판정이 아래 「올림·뺌의 기준」을 따른다
  - [ ] AC-4 대조 검사가 세 가상 상태에서 **실패한다** — ① 없는 Q id 를 출처로 주입 ② 없는 단위 id 를 출처로 주입
        ③ M1~M3 출처 Q 하나를 두 표에서 모두 제거. 그 세 상태를 검사 안에서 매번 재확인한다
  - [ ] AC-5 `docs/planning/progress.md` 「지금 상태」에 부모 이니셔티브
        `init-20260904-attach-payload-manual-rreq` 의 **M4 완료 = 이니셔티브 종료**가 반영된다
- **위험과 되돌리기:** 문서 2건·검사 1건을 더하고 `progress.md` 를 고칠 뿐이다. 코드·운영 상태·외부 상태·비용에 닿지 않는다.
  되돌리기는 `git revert <구현 커밋>` 1회. 가장 큰 위험은 **목록이 실제 구멍을 좁게 잡아 다음 이니셔티브가 같은 벽에 다시 부딪히는 것**이고,
  AC-1 의 16건 전수와 AC-3 의 제외 사유가 그것을 막는다 — 뺀 것도 이유와 함께 남으므로 판단이 사후에 검증된다.
- **결정 필요:** 없음 (2026-09-06 사용자 확정 — 구멍의 범위는 「attach 가 답해야 하는 것 전부」, 출처 역추적은 「검사로 집행」)


## 올림·뺌의 기준

Q 하나를 「올린 것」에 넣을지 「뺀 것」에 넣을지는 **그 Q 를 해소하는 변경이 무엇의 형태를 정하는가**로 가른다.
개수가 아니라 이 기준이 목록의 경계다 — 기준 없이 나누면 구현자가 임의로 가르고 검사는 그것을 잡지 못한다.

- **올린다:** 해소가 **부착 산출물의 형태**(무엇을 어디에 놓는가·무엇이 커밋되는가) 또는
  `attach`·`update --dry-run`·롤백 **명령의 동작**을 정하는 것. 즉 부착이라는 행위가 없으면 존재하지 않는 결함.
- **뺀다:** 하네스 자신의 명령(`close`·`envelope`·`validate`·`run-unit`)이나 어댑터 런북의 결함 —
  **부착과 무관하게 자기 저장소에서도 같은 모양으로 나는 것**. 이것들은 관통 사이의 정비가 가져간다.
- **경계에 걸리면 올린다.** 뺀 것은 다음 이니셔티브가 보지 않으므로, 잘못 뺀 비용이 잘못 올린 비용보다 크다.

## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `docs/requirements/attach-requirements.md` (새로 만든다) · `tests/test_attach_requirements.py` (새로 만든다) · `docs/planning/progress.md` · `docs/work/feat-20260906-m4-attach-requirements-3mcv/`
- 영향을 받는 부분: CI 의 unittest 묶음에 검사 1건이 늘어난다. 다음 `attach` 이니셔티브의 `/plan` 이 이 목록을 입력으로 읽는다
- 바꾸지 않는 것(비범위): `romeo/` 전부 (구멍을 **고치지 않는다** — 이 단위는 적기만 한다, §12) · `docs/planning/open-questions.md` (Q 항목의 본문을 다시 쓰지 않는다 — 출처로 읽기만 한다) · 부모 charter `docs/work/init-20260904-attach-payload-manual-rreq/charter.md` (그 문서는 만든 뒤 고친 적이 없고 완료 반영은 `progress.md` 가 맡아 왔다) · 대상 저장소 `My-Automated-Worker/instagram-dm-sender` (이 단위는 그 저장소를 열지 않는다)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | Q-53~Q-68 16건을 읽어 attach 요구사항으로 올릴 것과 뺄 것을 가르고 목록 문서를 세운다 | `docs/requirements/attach-requirements.md` 를 만든다. 두 표 모두 **첫 열이 Q id** 다 — 「올린 것」 표는 열 `Q · 요구사항 · 무엇이 참이어야 충족인가 · 출처 단위 · 마일스톤`, 「뺀 것」 표는 열 `Q · 왜 attach 요구사항이 아닌가`. 한 요구사항이 여러 Q 에서 나오면 요구사항 열에 같은 이름을 쓴다 — 행은 Q 단위다. 출처 단위는 `init-20260904-attach-payload-manual-rreq`(M1) · `feat-20260904-m2-router-foreign-repo-ct5h`(M2) · `feat-20260906-m3-close-foreign-repo-ik3u`(M3) 셋 중 하나 | 소비: `docs/planning/open-questions.md` 의 Q-53~Q-68 → 생산: 표 두 개와 그 열 이름 | 두 표의 Q id 집합의 합이 `open-questions.md` 에서 M1~M3 세 단위를 출처로 가진 Q 집합과 정확히 같다 (단위 2 의 검사가 판정한다) | `git rm docs/requirements/attach-requirements.md` |
| 2 | 목록이 낡거나 없는 것을 가리키면 실패하는 대조 검사를 세운다 | `tests/test_attach_requirements.py` 에 `TestAttachRequirementsProvenance` 를 만든다. ① 두 표의 Q id 합집합 == `open-questions.md` 에서 M1~M3 세 단위를 출처 열에 가진 Q 집합 ② 「올린 것」의 각 출처 Q 가 `open-questions.md` 에 실재 ③ 각 출처 단위가 `docs/work/` 에 실재 ④ 마일스톤 표기가 M1·M2·M3 중 하나 ⑤ 「뺀 것」의 각 행에 사유가 비어 있지 않다. 판별력은 AC-4 의 세 가상 상태를 테스트 안에서 문자열 치환으로 만들어 매번 재확인한다 | 소비: 단위 1 의 표 두 개와 열 이름 → 생산: 클래스 `tests.test_attach_requirements.TestAttachRequirementsProvenance` | `python3 -m unittest tests.test_attach_requirements.TestAttachRequirementsProvenance -v` 가 rc=0 이고, 단위 1 의 문서가 없는 상태에서는 실패한다 | `git rm tests/test_attach_requirements.py` |
| 3 | 부모 이니셔티브의 종료를 상태 블록에 반영한다 | `docs/planning/progress.md` 「지금 상태」에 `init-20260904-attach-payload-manual-rreq` 의 M4 완료 = 이니셔티브 종료와 다음 행동을 적는다. 30줄·2KB 예산을 지킨다 | 소비: 단위 1·2 의 결과 → 생산: 없음 (문서 끝단) | 그 블록에 `M4` 와 이니셔티브 id 가 나타나고 `bin/romeo validate` 가 rc=0 | `git checkout -- docs/planning/progress.md` |

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

**판별 검사와 회귀 방지 검사의 구분(§11).** check-1 만 **판별 검사**다 — 이 단위가 없으면 실패해야 한다
(`docs/requirements/attach-requirements.md` 도 `TestAttachRequirementsProvenance` 도 없으므로 지금 상태에서는
`AttributeError` 로 실패한다). 그 판별력은 검사 안의 세 가상 상태로 매번 재확인된다 — 없는 Q id 주입 ·
없는 단위 id 주입 · M1~M3 출처 Q 하나를 두 표에서 제거. check-2·check-3 은 **회귀 방지 검사**라
양쪽 실측의 대상이 아니다.

**Q 의 개수를 검사에 박지 않는다.** 「16건」은 2026-09-06 의 실측값이지 불변량이 아니다 —
개수를 상수로 세는 검사는 나중에 M1~M3 출처 Q 가 하나 늘면 목록을 옳게 갱신해도 깨진다.
check-1 은 개수 대신 `open-questions.md` 에서 **읽은 집합**과 목록의 집합을 대조한다(§11 「요구하는 자리와 보는 자리」).

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_attach_requirements.TestAttachRequirementsProvenance -v"
  - id: check-2
    command: "python3 -m unittest discover -s tests"
  - id: check-3
    command: "bin/romeo validate"
```

### 승인 전 양쪽 실측 (2026-09-06)

판별 검사는 **기존 상태에서 실패하고 가상 완료 상태에서 성공하는 것**을 승인 전에 양쪽으로 보인다(§11).
가상 완료 상태는 프로브 워크트리 `probe-m4-attach-req`(base `b9aac2b`)에서 만들었다.

| 검사 | 기존 상태 (`b9aac2b`) | 가상 완료 상태 (프로브) |
| --- | --- | --- |
| check-1 (판별) | **rc=1** — 모듈이 없어 `AttributeError` | rc=0 — 6/6 통과 |
| check-2 회귀 | rc=0 · 897 tests · 136.5s | rc=0 · 903 tests · 124.8s |
| check-3 회귀 | rc=0 | rc=0 |

밖에서 한 번 더 흔들었다 — 목록에서 `Q-56` 행 하나를 지우자 check-1 이 **rc=1**, 되돌리자 rc=0.

재실행 상한은 `romeo/evidence.py` 의 `RERUN_TIMEOUT` = **600초**이고 check-2 실측이 124.8초라 21% 다.

**프로브가 잡은 것:** 판별 테스트 `test_detects_unknown_source_unit` 의 첫 판본이 단위 id 를
`replace(..., 1)` 로 치환했는데, 그 첫 등장이 표가 아니라 문서 상단 산문이어서 **표는 그대로인 채 통과했다** —
즉 아무것도 판별하지 못하는 검사였다. 치환 대상을 해당 표 행으로 좁혀 고쳤다.


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
