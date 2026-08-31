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

## 지금 상태 (기준 `91ac38b` · 2026-08-31)

> 이 블록은 손으로 갱신한다. 위 SHA 는 **이 요약이 서술하는 상태의 기준 커밋**이지 블록을 쓴 커밋이 아니다.
> `git log --oneline 91ac38b..HEAD` 에 커밋이 있으면 그 커밋들이 아래 항목을 바꿨는지 먼저 본다 —
> 바꿨다면 블록을 믿지 말고 CI 최신 실행과 검사 재실행으로 실측하고, 이 블록을 갱신한다.

- **마일스톤:** M2 완료(2026-08-29 · D-76). **M3 진행 중.** G-M3 는 §6.1 의 1~4단계가 닫혔고
  **5단계는 관측이 끝났으나 작업 단위가 아직 닫히지 않았다.** `feat-20260831-bmad-install-observe-a3bm` 은
  **관통 3회 전부 fail** 이다 — 다만 실패한 것은 매번 **하네스와 검증 계획**이었고 관측 자체는 세 번 다 성공했다.
- **답은 나왔다 — BMAD 는 이 하네스와 공존한다.** 세 번의 관통이 같은 결론을 냈고 그 근거는 실행 출력이다.
  BMAD `6.11.0`(core·bmm) + CIS `v0.3.2` 를 버리는 워크트리에 설치했을 때 **romeo 스킬 38파일이 sha256 38/38 무손상**이었고,
  **두 런타임이 `bmad-*` 59종을 romeo 스킬과 함께 로드**했다(codex 98개 중 romeo 12/12 · claude 150개 중 11/11 · MISSING 없음).
  D-77 이 아카이브만 보고 고른 **추천 11종이 두 디렉터리에 전부 실재**했고, agent 없이 `bmad-cis-storytelling` 을 직접 부르자
  두 런타임 다 첫 단계를 시작했다(A-12 잔여 2건 관측됨). 설치기는 `--directory` 안에만 썼다 —
  아카이브 [E09] 가 걱정한 **전역 `~/.codex/skills` 쓰기는 관측되지 않았다.** 프로브의 `present` 분기가 실제 설치본에서 처음 확인됐다.
- **예상 밖 발견 셋.** ① **`--tools` 는 더하기가 아니라 교체다** — claude-code 로 다시 깔면 `.agents/skills` 의 `bmad-*` 가 제거된다.
  두 런타임에 동시에 두려면 `--tools codex,claude-code` 를 준다. ② 기존 설치본에 `--yes` 만 주면 **quick-update 로 빠져 `--tools` 를 읽지 않는다**
  (exit 0 인데 반영 안 됨) — `--action update` 가 필요하다. ③ **codex 런타임을 띄우는 것 자체가 전역 `~/.codex/skills/.system/` 을 다시 쓴다.**
  설치기가 한 일이 아니다.
- **이번 세션이 잡은 것 — 하네스 결함 3건과 검증 계획 결함 2건. 전부 관통이 드러냈다.**
  | 무엇 | 성격 | 처리 |
  | --- | --- | --- |
  | 테스트 4건이 「이 저장소에 BMAD 미설치」를 단언 — 로드맵이 성공하면 깨지는 테스트 | 하네스 | 고침 `c7c1b53` |
  | `bin/romeo doctor` 가 `--strict` 없이는 항상 exit 0 — **빈 검사**였다 | 검증 계획 | 고침 `54dd04d` |
  | check-8 이 codex 소유 `.system/` 을 비교해 **통과 불가능**했다 | 검증 계획 | 고침 `54dd04d` |
  | 시크릿 패턴이 파일명 `skills-before` 를 토큰으로 오탐 → close 의 명령 대조가 깨짐 | 하네스 | 고침 `07c3bdf` + 회귀 테스트 |
  | 충돌 fixture 위반을 CI 가 전혀 잡지 않는다 | 하네스 | park `Q-21` |
- **3회차는 기계적으로 거의 다 닿았다.** 구현자 `required_checks` **12/12 exit 0**, `close` 의 **기록·재실행 대조 12/12 PASS**,
  봉투 앵커 **양쪽 5/5**, 방어 검사 **유효**(before/after `log_sha256` 동일 `1b0f9cab081e`). `close` 의 유일한 FAIL 은 `REVIEW_VERDICT` 였다.
- **검토자(codex read-only)가 FAIL 을 냈고 findings 3건은 전부 정당하다 — 반박하지 않았다.**
  ① `UNAPPROVED_ACTION` — 확인란이 설치를 「한 번에 하나씩」 으로 못박았는데 `--tools` 가 교체라 **AC-5 를 달성할 유일한 방법이 결합 설치**였다.
  확인란이 자기 수용 기준을 금지한 것이므로 **spec 결함**이다(park `Q-24`).
  ② ③ **증거 결속** — `docs/work/<id>/` 는 `dirty_tree_hash`·`changed_files`·`artifact_hash` 에서 제외되는데(`romeo/evidence.py:37`)
  baseline 파일을 그 안에 리다이렉트로 만들어 내용이 원시 로그에 남지 않았다(baseline 3건의 `stdout_tail` 이 전부 빈 문자열, 실측).
  「설치 직전 상태」라는 주장에 앵커가 없다(park `Q-23`).
- **반복 중단 브레이크가 두 번 걸렸고 두 번 다 제 역할을 했다.** 2회 연속 실패 뒤 사람이 「완료 정의는 달성 가능하다」를
  `attempts.yaml` 의 `reviews` 에 기록하고서야 3회차가 돌았다. 지금은 **연속 3회** 상태다 — 4회차는 다시 재검토 기록이 있어야 돈다.
  배운 것 하나: **재검토 기록도 커밋해야 워크트리가 본다**(D-a). 커밋 전 기동은 워크트리 안 `envelope build` 가 브레이크로 거부했다.
- **다음 세션이 이어갈 자리 — 4회차 전에 spec 두 곳을 고쳐 재승인한다.**
  1. 확인란의 설치 순서 문장. 방법(「한 번에 하나씩」)을 확인란에서 빼고 구현 단위 표로 옮긴다 — 확인란에는 결과와 이유만 둔다(`Q-24`).
  2. baseline 을 `> 파일` 대신 `tee 파일` 로 만들어 내용을 원시 로그에 봉인한다(`Q-23`). 그 뒤 `--after-review` 로 브레이크를 풀고 4회차를 돈다.
  3. 그 다음이 `core/templates/charter.md`(T2)와 M3 의 나머지(MCP·브라우저 3모드 프로브, packages.yaml 의 T2·gate 행, `gate-create` 승인 흐름, 시나리오 3·8·9).
- **park 이 4건 늘었다 — `Q-21`~`Q-24`.** Q-21 충돌 fixture 를 CI 가 안 잡는다 · Q-22 `romeo validate <디렉터리>` 가 죽는다 ·
  Q-23 작업 단위 폴더 안 산출물이 증거에 앵커되지 않는다 · Q-24 확인란이 자기 수용 기준을 금지할 수 있다. 기존 park 은 Q-12~Q-20 그대로다.
- **CI:** `8d5af4f` 까지 푸시돼 있고 그 시점 실행 success. **`40b074b`~`91ac38b`(및 이후)는 아직 로컬에만 있다** — 푸시는 별도 승인 대상이다(K-66).
- **워크트리 9개 — 이번 세션에 3개 늘었다.** 기존 6개(`impl-…-w3qu` · `…-938r` · `…-biae` · `…-82zv` · `impl-…-tgnb` · `impl2-…-tgnb`)에
  **`impl-feat-20260831-bmad-install-observe-a3bm`(1회차 `9d4669f`)** · **`impl2-…`(2회차 `bdaf240`)** · **`impl3-…`(3회차 `e36a3bc`)** 가 더해졌다.
  세 개 다 커밋돼 있어 지워도 브랜치는 남는다. 정리는 승인 대상이다(K-66).
- **문서 지연:** 「미검증·남은 위험」은 맨 위 소절(M2 close 이후)만 최신이다.


## 마일스톤

| 마일스톤 | 상태 | 근거 |
| --- | --- | --- |
| M0 정책표·fixture·분류 카드 | **완료** | [원문](archive/milestones.md) |
| M1 T0 최소 관통 (Claude 단독, 현재 작업 공간) | **완료** | [원문](archive/milestones.md) |
| M2 어댑터·역할·Orca 위임·T1 교차 관통 | **완료 (2026-08-29 · D-76)** | [원문](archive/milestones.md) |
| M3 기획 깊이 확장 (T2·discovery·gate·doctor) | **진행 중** — G-M3 는 §6.1 **1~4단계 닫힘**(D-77 + `feat-20260831-bmad-attach-probe-tgnb`). **5단계는 관측이 끝났고 결론은 「공존한다」다** — 설치 3회 재현, romeo 스킬 38/38 무손상, 두 런타임이 `bmad-*` 59종을 함께 로드, 추천 11종 실재, agent 없이 workflow 시작. 그러나 **작업 단위는 아직 닫히지 않았다** — 관통 3회 전부 fail 이고 실패한 것은 매번 하네스·검증 계획이었다. 4회차 전에 spec 두 곳(확인란의 설치 순서 · baseline 봉인)을 고쳐 재승인한다. M3 의 나머지(charter·MCP/브라우저 프로브·gate·시나리오 3·8·9)는 미착수 | D-77, `docs/work/feat-20260831-bmad-install-observe-a3bm/attempts.yaml`, 브랜치 `impl3-…`(`e36a3bc`) |
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
