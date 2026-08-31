---
id: progress
type: planning
status: active
updated: 2026-08-30
authority: derived
---

# 구현 진행 상태

[구현 계획](implementation-plan.md) §10 체크리스트 기준. 완료 판정은 관찰 가능한 결과로만 한다(K-51).
정지선·결정은 [decision-register](../decisions/decision-register.md) "구현 착수 결정"(D-59~D-71).

`계획 §10` 열은 이 표의 행이 계획 §10 의 어느 번호에 대응하는지다. 두 표의 번호가 어긋나
계획의 확인 기준이 조용히 사라지는 것을 막는다(1차 리뷰 F16). `—` 는 계획 §10 에 번호가 없는 항목이다.

독립 리뷰 findings 원문은 `docs/reviews/` 에 라운드별로 보관한다 —
[1차(F01~F31)](../reviews/2026-08-28-m2-round1-review/README.md) · [2차(G01~G13)](../reviews/2026-08-28-m2-round2-review/README.md).

## 지금 상태 (기준 `280bf2d` · 2026-08-31)

> 이 블록은 손으로 갱신한다. 위 SHA 는 **이 요약이 서술하는 상태의 기준 커밋**이지 블록을 쓴 커밋이 아니다.
> `git log --oneline 280bf2d..HEAD` 에 커밋이 있으면 그 커밋들이 아래 항목을 바꿨는지 먼저 본다 —
> 바꿨다면 블록을 믿지 말고 CI 최신 실행과 검사 재실행으로 실측하고, 이 블록을 갱신한다.

- **마일스톤:** M2 완료(2026-08-29 · D-76). **G-M3 채택 게이트가 닫혔다(2026-08-31 · D-77) — M3 에 진입했다.**
  **사용자 결정(2026-08-31): 앞으로 발견되는 하네스 결함은 기본이 park 다.** 고치는 것은 **차단급**
  (있으면 어떤 관통도 끝나지 않는 것)만이고, 우회 가능한 마찰은 `open-questions.md` 에 적고 지나간다.
- **이번에 닫힌 것 — G-M3 (§6.1 의 1·2·3단계).** BMAD 는 `install` 이라 파일을 가져오지 않는다.
  확정한 것은 **라우터가 discovery/T2 에서 추천할 스킬**이고, 46개(Core 13 + BMM 33) + CIS 10 을 빠짐없이 분류했다.
  **채택 11** — `bmad-product-brief`·`bmad-prfaq`·`{domain,market,technical}-research`(BMM 5) +
  `bmad-brainstorming`·`bmad-forge-idea`(core 2) + CIS workflow 4.
  **deferred 5** — `bmad-prd`·`bmad-architecture`(K-61) · brownfield 2(K-62) · `bmad-ux`(G-M6 이관).
  **excluded 40** — persona agent 12(K-60) · 구현계 13(K-63·K-66·Superpowers 중복) · core 중복 11 + forwarder 4.
- **채택과 보류를 가른 기준은 「Romeo 에 빈칸이 실재하는가」 하나다.**
  채택군이 채우는 자리는 `core/templates/sections/discovery-plan.md` 의 「조사 방법·기간: `NEEDS_INPUT`」 이다 —
  Romeo 는 조사를 **어떻게 할지 적는 칸**만 갖고 조사 자체는 하지 않는다.
  보류군은 빈칸이 아니라 **이미 찬 자리**다: `prd.md` ↔ Tech Spec `## 확인란`,
  `ARCHITECTURE-SPINE.md` ↔ decision-register + `## 변경 범위`, 모듈 간 계약 ↔ 구현 단위 표의 인터페이스 열(D-69).
  BMAD 문서가 스스로 밝히듯 `product-brief` → `prd` 는 한 줄기인데 Romeo 에서 그 줄기는 brief → 확인란이다 —
  PRD 를 끼우면 같은 요구가 세 곳에 적히고 **승인은 확인란만 읽는다**(D-27).
  `charter.md` 가 아직 없어 「Charter 가 담지 못하는 층이 있는가」 는 지금 확인할 수 없다. 그래서 채택이 아니라 보류다.
- **아카이브가 계획의 전제 둘을 뒤집었다 — 후보표를 먼저 만들었다면 둘 다 틀린 채로 확정됐다(Q-06 해소).**
  ① **Codex 는 지원된다**(A-12 전제 반증). `platform-codes.yaml` 에서 preferred, 타깃 `.agents/skills`, installer 에 setup test.
  계획 §7 M3 의 「Codex 미지원 시 정직 표기」 를 지웠다. **대신 새 충돌이 생겼다** — `.agents/skills` 는
  `romeo compile` 의 쓰기 대상이다(K-64·K-68 이 이 지점을 봐야 한다).
  ② **산출물 경로를 `_bmad-output/**` 로 하드코딩할 수 없다** — `bmm` 의 `project_knowledge` 기본값이 `docs` 다.
- **이번 작업의 증거.** 검사 6건 전부 exit 0 — `unittest`(OK) · `validate` · `vendor`(vendors=1 files=15) ·
  `notices --check` · `compile --check` · `fixtures check`(PASS 33). `THIRD_PARTY_NOTICES.md` 는 재생성했다.
  46+10 분류에 빠지거나 두 번 센 SKILL 이 없음을 산술로 실측했다.
- **미검증 — 완료로 세지 않는다.** ① CIS agent 없이 workflow SKILL 을 직접 호출하는 경로는 **원문 activation 계약으로만**
  확인했다(`workflows.ko.md` 15~17: workflow 가 스스로 `config.yaml` 해석·`persistent_facts` 로드·시작). 실행하지 않았다.
  ② Codex 도 **설치 선언을 읽었을 뿐** 그 런타임에서 실제로 discovery·실행되는 것은 보지 못했다(A-12 잔여).
  둘 다 §6.1 **5단계**(K-68 부착 검증)에서 관측한다.
- **넘긴 것 (park) — `docs/planning/open-questions.md` Q-12~Q-17, `우회 가능 — v1 이후` 표시.**
  각 행에 **우회 방법**이 함께 적혀 있다. ⑤ 검토자 lifecycle 자동화 · Ⓓ `check --wait` 는 Run 당 waiter 하나 ·
  Ⓕ `task/` 사본이 `git merge --ff-only` 를 막는다 · `w3qu` 잔여 3건.
- **직전 관통이 드러낸 RUNBOOK 결함 4건 (전부 미반영 — park):**
  Ⓖ §3.5.1 이 `attempts.yaml` 을 워크트리에 실재시키지 않는다(**브레이크를 켠 지금 이것이 가장 먼저 물 자리다**) ·
  Ⓗ §3.4.1 에 「옛 Task 를 닫기 전 워커를 먼저 정리한다」 누락 · Ⓘ `worker-start --setup` 은 새 워크트리 전용 ·
  Ⓙ `run-unit` 이 인쇄하는 reviewer-spawn 명령의 `--output-schema` 는 RUNBOOK §2 기준 HTTP 400 이다.
- **반복 중단 브레이크는 켜져 있다.** `envelope build` 가 입구에서 평가한다 — 연속 실패 2회면 `--after-review` 없이 거부된다.
  `w3qu` 는 park 이고 지금 브레이크가 그것을 막고 있다(새 카운터로 연속 실패 **4회**). 재개하려면 §10 재검토 결론 1건 +
  AC-5 제거 재승인 + `a1f543a` rebase 가 먼저다. 구현은 브랜치 `impl-feat-20260830-harness-defects-w3qu` 의 `a1f543a` 에 보존돼 있다.
- **다음 세션이 이어갈 자리 — §6.1 의 4·5단계다.**
  1. **`capabilities.yaml` 의 `discovery.bmad` 프로브** — `_bmad/_config/manifest.yaml` 존재 + 기록된 module/IDE 를 읽는다.
     존재 프로브는 **실행 증거가 아니다**(아카이브 경고). "설치 흔적 확인" 까지만 말한다.
  2. **`/plan` 분류 카드가 D-77 의 11종을 추천하고 산출물 `inputs:` 링크를 요구**하게 한다(K-62).
  3. **K-68 부착 검증** — 그때 위 미검증 2건(CIS workflow 직접 호출 · Codex discovery)을 함께 관측한다.
     `.agents/skills` 와 `romeo compile` 의 쓰기 충돌이 이 단계의 실제 위험이다.
  4. `core/templates/charter.md`(T2) 를 만들고 나면 `bmad-prd`·`bmad-architecture` 보류를 재검토할 근거가 생긴다.
- **CI:** `ee0c00a` 까지 푸시돼 있고 그 시점 실행 2건 success. **`280bf2d` 는 아직 로컬에만 있다** — 푸시는 별도 승인 대상이다(K-66).
- **낡은 워크트리:** `impl-feat-20260830-harness-defects-w3qu`(구현이 `a1f543a` 로 커밋돼 있어 워크트리를 지워도 브랜치는 남는다) ·
  `impl-feat-20260830-reviewer-fail-reasons-938r`(통합 완료) · `impl-feat-20260830-runbook-delegation-gaps-biae`(통합 완료) ·
  `impl-feat-20260831-repeat-brake-82zv`(통합 완료). 정리는 승인 대상이다(K-66).
- **문서 지연:** 「미검증·남은 위험」은 맨 위 소절(M2 close 이후)만 최신이다.

## 마일스톤

| 마일스톤 | 상태 | 근거 |
| --- | --- | --- |
| M0 정책표·fixture·분류 카드 | **완료** | [원문](archive/milestones.md) |
| M1 T0 최소 관통 (Claude 단독, 현재 작업 공간) | **완료** | [원문](archive/milestones.md) |
| M2 어댑터·역할·Orca 위임·T1 교차 관통 | **완료 (2026-08-29 · D-76)** | [원문](archive/milestones.md) |
| M3 기획 깊이 확장 (T2·discovery·gate·doctor) | **진입** — G-M3 채택 게이트 닫힘(D-77, §6.1 1·2·3단계). 남은 것은 4·5단계(`discovery.bmad` 프로브 · `/plan` 링크 · K-68 검증) | D-77, `provenance/imports.yaml` G-M3 |
| M4 ~ M7 | 미착수 | [원문](archive/milestones.md) |

## §10 체크리스트

항목명·상태·근거 링크만 남긴 완료 표다. 각 행의 근거 원문은 [archive/checklist-8-48.md](archive/checklist-8-48.md) 에 문장 그대로 있다.

| # | 계획 §10 | 항목 | 상태 | 근거 |
| --- | --- | --- | --- | --- |
| 1 | #1 | §9.2 결정 1~5 확정 | 완료 | [원문](archive/checklist-8-48.md#c1) |
| 2 | #2 | fixture 15~20건 (사용자 3개월 요청 포함) | 완료 (33건) | [원문](archive/checklist-8-48.md#c2) |
| 3 | #3 | 정책표 3종 + 스키마 + Tech Spec 템플릿 + `/plan` SKILL | 완료 | [원문](archive/checklist-8-48.md#c3) |
| 4 | #4 | `romeo validate`·`new`·ID + unittest | 완료 | [원문](archive/checklist-8-48.md#c4) |
| 5 | #5 | `/plan --dry-run` 5건 shadow | 완료 | [원문](archive/checklist-8-48.md#c5) |
| 6 | #6 | M1: T0 2건 관통 | 완료 | [원문](archive/checklist-8-48.md#c6) |
| 7 | #7 | stale 거부·미체크 AC 거부 | 완료 (테스트 기준) | [원문](archive/checklist-8-48.md#c7) |
| 8 | #8b | G-M2 채택 게이트 | 완료 | [원문](archive/checklist-8-48.md#c8) |
| 9 | — | LICENSE Apache-2.0 교체 + `THIRD_PARTY_NOTICES.md` | 완료 | [원문](archive/checklist-8-48.md#c9) |
| 10 | #8b | `vendor/obra-superpowers@b36e082/` 원문 복사(수정 0) | 완료 | [원문](archive/checklist-8-48.md#c10) |
| 11 | — | CI(python 3.11) 하네스 검사 | 완료 (그 뒤의 워크플로 변경은 **CI 에서 미실행**) | [원문](archive/checklist-8-48.md#c11) |
| 12 | #9 | 어댑터 컴파일(`romeo compile`) | 완료 | [원문](archive/checklist-8-48.md#c12) |
| 13 | — | 실행 가드 `.claude/settings.json` | 완료 | [원문](archive/checklist-8-48.md#c13) |
| 14 | #9 | `romeo doctor` 부착 검증 | 완료 | [원문](archive/checklist-8-48.md#c14) |
| 15 | #8b | 충돌 fixture 3종 (K-68) | 완료 | [원문](archive/checklist-8-48.md#c15) |
| 16 | — | Codex 독립 리뷰 반영 | 완료 | [원문](archive/checklist-8-48.md#c16) |
| 17 | — | K-60 재정의(D-72) | 완료 | [원문](archive/checklist-8-48.md#c17) |
| 18 | — | F-08 원자적 컴파일 · F-07 upstream 대조 | 완료 | [원문](archive/checklist-8-48.md#c18) |
| 19 | **#8** | 검토자 런타임 read-only **쓰기 시도 거부 로그** | 완료 | [원문](archive/checklist-8-48.md#c19) |
| 20 | #9 | 부품 부착 배선 (`.harness/romeo.project.yaml` → 라우터) | 완료 | [원문](archive/checklist-8-48.md#c20) |
| 21 | #10 선행 | 승인 → 실행 순서 · 위임 식별자 | 완료 | [원문](archive/checklist-8-48.md#c21) |
| 22 | #10 선행 | 작업 계약 생성 (`romeo envelope build`) | 완료 | [원문](archive/checklist-8-48.md#c22) |
| 23 | #10 선행 | 검토자 판정 → 완료 판정 연결 | 완료 (실물 봉투로는 **미검증**) | [원문](archive/checklist-8-48.md#c23) |
| 24 | #11 | 동등성 게이트 정직화 + CI 스텝 | 완료 (게이트는 **미판정**) | [원문](archive/checklist-8-48.md#c24) |
| 25 | #8 | 역할 계약 투영 · 권한 상한 정본 | 완료 | [원문](archive/checklist-8-48.md#c25) |
| 26 | #10 | Orca 런북으로 T1 관통 (Claude 구현 / Codex 리뷰) | **완료** | [원문](archive/checklist-8-48.md#c26) |
| 27 | #11 | 역할 교체 재현 + parity **관측** | **완료 — 게이트 판정 FAIL** | [원문](archive/checklist-8-48.md#c27) |
| 28 | — | 2차 독립 리뷰 반영 (G01~G13) | 완료 | [원문](archive/checklist-8-48.md#c28) |
| 29 | — | 관통이 찾은 결함 반영 (RUNBOOK 3건 + 코어 모순 1건) | 완료 | [원문](archive/checklist-8-48.md#c29) |
| 30 | #11 | 동등성 게이트 정의 보완 | **완료 (D-73)** | [원문](archive/checklist-8-48.md#c30) |
| 31 | — | 작업 단위 `feat-20260829-license-field-46an` 완료 | **진행 중 — 3차 관통 기준 실행 완료(close 는 검토 표본만 남았다)** | [원문](archive/checklist-8-48.md#c31) |
| 32 | — | `AGENTS.md` 서문 비대칭 해소 | **완료** | [원문](archive/checklist-8-48.md#c32) |
| 33 | #11 | 검토자 면 동등성 관측 — 검토자-only 재실행(RUNBOOK §6.6) | **완료 — 게이트 FAIL** | [원문](archive/checklist-8-48.md#c33) |
| 34 | — | 작업 계약 `allowed_paths` 상한 — spec 변경 범위로 좁힌다 | **완료 (`c237ea9`)** | [원문](archive/checklist-8-48.md#c34) |
| 35 | — | Q-08 재현성 측정 — 같은 산출물에 같은 검토자 런타임 2회 추가 | **완료 — codex 의 PASS 는 재현되지 않았다** | [원문](archive/checklist-8-48.md#c35) |
| 36 | #11 | 동등성 게이트에 재현성 요구 (D-74) | **완료 — 게이트 PASS(관측 2건 · 비교 불가 면 2)** | [원문](archive/checklist-8-48.md#c36) |
| 37 | — | 승인된 spec 을 고쳤을 때 재승인하는 경로 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c37) |
| 38 | — | `approve` 의 `base_sha` 가 승인된 내용을 담지 않는 커밋을 가리킨다 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c38) |
| 39 | — | 결과 계약 스키마에 자유 서술 자리가 없다 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c39) |
| 40 | — | 두 런타임 모두 결과 계약 스키마를 CLI 로 강제할 수 없다 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c40) |
| 41 | — | `close` 가 evidence 를 하나만 읽어 §6.6 뒤에 구조적으로 깨진다 | **완료 (2026-08-29) — D-75 의 표본 수만 사용자 확정 대기** | [원문](archive/checklist-8-48.md#c41) |
| 42 | — | 검토자 프롬프트의 「명령 실행 금지」가 런타임에 따라 읽기까지 막는다 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c42) |
| 43 | — | 잔여 결함 설계의 반박 검토(세 렌즈) 와 반영 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c43) |
| 44 | — | 원시 로그가 산출물 식별을 봉인한다 (4차 리뷰 구멍 B 의 한 겹) | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c44) |
| 45 | — | 구현 diff 의 반박 검증(세 렌즈 + finding 별 반박 에이전트) 과 반영 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c45) |
| 46 | #10·#11 | 3차 관통 — 기준 실행(구현자 claude · 검토자 codex) 완료, 교체 실행 준비 | **완료 (2026-08-29) — 48 에서 close** | [원문](archive/checklist-8-48.md#c46) |
| 47 | — | M2 근본 원인 재검토 — "왜 3일째 안 닫히나, 설계·계획이 틀렸나" | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c47) |
| 48 | #11·#12 | D-76 실행 — 완료 정의 개정 · parity 판정 축소(advisory) · **impl5 close** · 페이로드 통합 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c48) |

## 세션 기록

날짜별 서술은 [archive/session-log.md](archive/session-log.md) 로 옮겼다 — 이 문서는 상태를 담고, 이력은 거기 있다.

## 미검증·남은 위험

이 절의 항목은 **완료가 아니다.** 검사가 PASS 라는 것과 그 회로가 실제로 닫혔다는 것은 다르다(K-51).

### 2026-08-29 M2 close 이후 남은 것 (최신)

- **원격 CI 는 `144a676` 까지 초록이다**(run `33289382316`). 그 뒤 커밋은 이 CI 줄 갱신뿐이다 — CI 는 push 마다 다시 본다.
- **기본 구현자(claude)의 권한 강제는 여전히 미관측이다.** D-76 의 "권한 상한" 요소는 관측된 범위(검토자 read-only 두 런타임)로만 판정한다. 교체 구현자(codex `-s workspace-write`)의 외부 쓰기·승인 명령 차단도 부분 관측이다.
- **검토 판정이 왜 흔들리는지는 모른다(Q-10).** D-76 은 그것을 게이트에서 뺀 것이지 줄인 것이 아니다. 재료: `--judge-verdict strict` 프로파일과 같은 산출물 5실행의 봉투. 첫 손댈 자리는 `review/SKILL.md` 의 FAIL 사유 열거.
- **check-5 가 하네스 자신의 unittest 라 페이로드 close 가 하네스 리비전에 묶인다.** 이번엔 impl5(7f8ecd7)에서 닫아 문제없었지만, 다음 단위부터는 페이로드 검사와 하네스 검사를 분리하는 템플릿 규칙이 필요하다(다음 자리 3).
- **RUNBOOK 은 여전히 수동이다(1,164줄·최소 72 행동 묶음).** 이번 close 는 수동 절차 없이 `close` 한 명령으로 끝났지만, 다음 T1 의 위임·회수·모으기는 자동화 전까지 같은 비용이다.
- **impl6 교체 실행은 하지 않았다.** 현 base(7f8ecd7)에서의 교체 성공 여부는 미검증이다 — D-76 ① 에 따라 M2 게이트 조건이 아니다.
- **옛 봉투 11건은 REVIEW_SUPERSEDED WARN 으로 남아 있고 지우지 않는다**(관측 표본). `APPROVAL_CHAIN` WARN(옛 손 재승인)도 그대로다 — Q-11 미룸.
- **v1 릴리스 잔여:** T2 Charter(V-2)·shadow 20건(V-10)·attach/update(M5) — M2 완료가 이것들을 닫지 않는다.

### 위협 모델 — 무엇을 막고, 무엇을 막지 못하는가

원문은 [제약 K-56~K-59](../requirements/constraints.md)로 옮겼다 — 무엇을 막고(K-56), 무엇을 막지 못하며(K-57),
무엇에 의존하고(K-58), 재실행으로 확인할 수 없는 것을 어떻게 다루는가(K-59). 문장은 그대로다.
다음 라운드에서 "해시를 하나 더 걸면 닫힌다" 류의 제안이 나오면 K-57 을 먼저 읽는다.

### 그 이전 소절 (2026-08-29 이전)

4차 리뷰(위조 시도 2종 관통) · 게이트 정의 보완 · 잔여 결함 37~42 · 이전 라운드에서 이어지는 것은
[archive/risks-2026-08-29.md](archive/risks-2026-08-29.md) 에 있다. 각 소절은 그 날짜 기준이며,
상당수가 D-76 으로 닫혔거나 후속 단위로 넘어갔다 — 닫혔는지는 그 항목의 근거를 다시 실행해 확인한다(K-51).
