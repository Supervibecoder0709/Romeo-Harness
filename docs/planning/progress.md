---
id: progress
type: planning
status: active
updated: 2026-09-01
authority: derived
---

# 구현 진행 상태

[구현 계획](implementation-plan.md) §10 체크리스트 기준. 완료 판정은 관찰 가능한 결과로만 한다(K-51).
정지선·결정은 [decision-register](../decisions/decision-register.md) "구현 착수 결정"(D-59~D-71).

`계획 §10` 열은 이 표의 행이 계획 §10 의 어느 번호에 대응하는지다. 두 표의 번호가 어긋나
계획의 확인 기준이 조용히 사라지는 것을 막는다(1차 리뷰 F16). `—` 는 계획 §10 에 번호가 없는 항목이다.

독립 리뷰 findings 원문은 `docs/reviews/` 에 라운드별로 보관한다 —
[1차(F01~F31)](../reviews/2026-08-28-m2-round1-review/README.md) · [2차(G01~G13)](../reviews/2026-08-28-m2-round2-review/README.md).

## 지금 상태 (기준 `fd7c7b9` · 2026-09-01)

> 이 블록은 손으로 갱신한다. 위 SHA 는 **이 요약이 서술하는 상태의 기준 커밋**이지 블록을 쓴 커밋이 아니다.
> `git log --oneline fd7c7b9..HEAD` 에 커밋이 있으면 그 커밋들이 아래 항목을 바꿨는지 먼저 본다 —
> 바꿨다면 블록을 믿지 말고 CI 최신 실행과 검사 재실행으로 실측하고, 이 블록을 갱신한다.

- **마일스톤:** M2 완료(2026-08-29 · D-76). **M3 진행 중** — G-M3 §6.1 1~5단계는 `a9e7af1` 로 닫혔다.
  그 뒤 **관통과 관통 사이의 하네스 정비 1회를 마쳤다** — `feat-20260831-park-defects-actm` 이 **5회차(`run_e3a4af18582c`)에서 close 를 통과**했고(`status: done`),
  통합 커밋은 `fd7c7b9` 다. 남은 M3 는 charter(T2)·MCP/브라우저 프로브·gate·시나리오 3·8·9 다.
- **park 된 결함 5건이 닫혔다.** 넷은 승인된 범위였고 하나는 이 단위가 스스로 드러낸 것이다.
  | # | 무엇이 막고 있었나 | 고친 자리 | 회귀 테스트 |
  | --- | --- | --- | --- |
  | Q-18 | 작업 계약이 「바뀌는 파일·모듈」 선언을 **일부만 읽고 아무 말도 하지 않았다** — `bmad-attach-probe` 1회차를 통째로 실패시켰다(9개 중 2개만 실림) | `romeo/envelope.py` `change_scope_paths` — 다음 목록 항목·다음 제목·빈 줄까지 이어 읽는다 | `TestChangeScopeMultiline` |
  | Q-20 | spec 템플릿의 「빈칸 금지」 안내가 종료 검사의 미완료 토큰을 글자 그대로 담아 **자기 검사에 걸렸다** | `core/templates/tech-spec.md` — 안내는 남기고 토큰만 뺐다 | `TestTemplateBlankGuidanceToken` |
  | Q-22 | `romeo validate` 에 폴더를 주면 **파이썬 트레이스백**이 올라왔다 | `romeo/validate.py`·`romeo/cli.py` | `TestValidateDirectoryTarget` |
  | Q-25 | 반복 중단을 푸는 유일한 창구가 **시도까지 함께 시작**해 유령 기록과 이중 base_sha 를 만들었다 | `romeo/run_unit.py`·`romeo/cli.py` — 기록 전용 경로. 브레이크를 우회하지는 않는다 | `TestReviewOnlyRecord` |
  | (신규) | 원시 로그 앵커가 **첫 물리 줄 하나만** 기록된 명령 전체와 비교해, 개행을 담은 명령은 **어떤 구현으로도** `EVIDENCE_ANCHORED` 를 통과할 수 없었다 | `romeo/evidence.py` `log_command_header()` — `$ ` 뒤부터 첫 `--- stdout ---` 표지 앞까지. 로그 기록 형식은 바이트 그대로 | `TestMultilineCommandAnchor` |
  Q-21 은 **고칠 것이 없었다** — park 이 요구하던 CI 스텝이 이미 `4e47693`(2026-08-28)에 있었다. 문서 정정으로 닫고, 그 park 이 함께 지적한
  「옵션 없는 `bin/romeo doctor` 는 항상 exit 0 인 빈 검사」 사실은 남겼다.
- **위조 탐지는 약해지지 않았다.** 앵커 수정이 대조를 느슨하게 만들 수 있는 자리였다. 헤더를 읽지 못하면 **건너뛰지 않고 미검증**을 돌려주도록 해
  표지를 지우고 봉인을 다시 맞추는 우회를 막았다 — 그 우회는 **수정 전 코드에도 있었고**(`f2-prefix-bypass` 라벨이 옛 코드를 격리 로드해 재현했다),
  봉인까지 다시 맞춘 위조 4종이 전부 거부되는 것을 `check-15` 가 고정한다.
- **다섯 회차가 결함을 하나씩 드러내고 닫았다.** 게이트가 오탐을 낸 회차는 **없다**.
  | 회차 | 막은 것 | 성격 | 처리 |
  | --- | --- | --- | --- |
  | 1 | check-1·check-2 가 라벨의 한 글자를 틀리게 적어 **통과 불가능** | 검증 계획 | 재승인 `deae0aa` |
  | 2 | `evidence.py` 의 첫 줄 대조 — 개행 담은 check-9 이 통과 불가능 | 하네스 | 범위에 넣어 재승인 `448c9f8` |
  | 3 | 재검토 기록을 커밋하지 않고 위임해 자식 워크트리가 **브레이크를 못 풀었다** | 절차(런북 누락) | `8284f89` 로 커밋 후 재기동. 판정 없이 중단됐으므로 `started` 로 남겼다 |
  | 4 | check-16 이 `sorted(glob)` 의 **마지막 하나만** 대조 — 증거 파일이 둘이 되면 옛 run 을 검사 | 검증 계획 | 「모든 `check-9` 기록 대조」로 교체해 재승인 `120aa96` |
  | 5 | — | — | **pass** · 연속 실패 0 으로 리셋 |
- **5회차가 통과한 근거.** required_checks **16/16 exit 0** · AC-6 단독 실행 2건 exit 0 · 원시 로그 대조 **22건** · 재실행 대조 **16/16** ·
  봉투 앵커 **양쪽 5/5** · 방어 검사 **유효**(before/after `log_sha256` 동일 `1b7a3364afac`) · 검토자(codex `gpt-5.6-sol`, read-only) **PASS · findings 0**.
  유일한 WARN 은 `REVIEW_SAMPLE` 이고 **D-75 (b) 가 이미 1건으로 닫기로 확정한 것**이다.
  산출물 트리 `3a5ba01c58ff` 는 4회차와 **바이트로 같다** — 5회차는 코드를 새로 만들지 않고 검증 계획만 교체했다.
- **정비 중에 새로 드러난 것 셋 — 다음 정비 후보다.** 전부 코디네이터 쪽 절차 결함이고 park 으로 열지 않았다(이 단위 범위 밖).
  ① RUNBOOK §3.1 의 커밋 목록에 **재검토 기록(`attempts.yaml`)이 없다** — 없으면 자식 워크트리가 브레이크를 못 푼다(3회차가 겪었다).
  ② 한 관통에서 **재작업을 새 위임으로 붙이면 새 run 이 필요하다**(`_stamp_ids` 가 거부). 런북에 그 분기가 없다.
  ③ `orca orchestration run-create` 가 **코디네이터 터미널을 최신 run 에 재바인딩**해 옛 run 의 메시지를 못 읽는다(`consumer_fenced`) — 답장 도달을 확인할 수 없다.
- **기존 park 은 `Q-12`~`Q-17`·`Q-19`·`Q-23`·`Q-24` 그대로다.**
- **CI:** `8d5af4f` 까지 푸시돼 있고 그 시점 실행 success. **`40b074b`~`fd7c7b9` 는 아직 로컬에만 있다** — 푸시는 별도 승인 대상이다(K-66).
- **워크트리 5개 — 이번 세션에 6개를 지웠다.** `mvp_planning` · `impl-`·`impl2-`·`impl4-`·`impl5-feat-20260831-park-defects-actm` 과 원본 체크아웃(`main`).
  bmad 계열 6개와 `impl3-park-defects` 를 정리했고(928MB → 330MB), 소실 위험이 있던 3건은 태그로 보존했다
  (`preserve/bmad-install-observe-a3bm-run1`~`run3`). **`orca worktree rm` 은 브랜치도 지운다** — 지우기 전에 커밋이 다른 ref 로 도달 가능한지 본다.
  `impl-`·`impl2-park-defects` 는 미커밋 산출물이 남아 있다.
- **문서 지연:** 「미검증·남은 위험」은 맨 위 소절(M2 close 이후)만 최신이다.


## 마일스톤

| 마일스톤 | 상태 | 근거 |
| --- | --- | --- |
| M0 정책표·fixture·분류 카드 | **완료** | [원문](archive/milestones.md) |
| M1 T0 최소 관통 (Claude 단독, 현재 작업 공간) | **완료** | [원문](archive/milestones.md) |
| M2 어댑터·역할·Orca 위임·T1 교차 관통 | **완료 (2026-08-29 · D-76)** | [원문](archive/milestones.md) |
| M3 기획 깊이 확장 (T2·discovery·gate·doctor) | **진행 중** — G-M3 는 §6.1 **1~5단계 전부 닫힘**(D-77 + `feat-20260831-bmad-attach-probe-tgnb` + `feat-20260831-bmad-install-observe-a3bm`). **5단계 결론은 「공존한다」**. 그 뒤 **관통 사이의 하네스 정비 1회**를 마쳤다 — `feat-20260831-park-defects-actm` 이 park 된 결함 5건을 닫고 5회차(`run_e3a4af18582c`)에서 close 를 통과했다(required_checks 16/16 · 재실행 대조 16/16 · 앵커 양쪽 5/5 · 검토자 PASS · findings 0). M3 의 나머지(charter·MCP/브라우저 프로브·gate·시나리오 3·8·9)는 미착수 | D-77, `docs/work/feat-20260831-bmad-install-observe-a3bm/`(status done) 통합 `a9e7af1`, `docs/work/feat-20260831-park-defects-actm/`(status done) 통합 `fd7c7b9` |
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
