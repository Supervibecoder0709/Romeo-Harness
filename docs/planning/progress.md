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

## 지금 상태 (기준 `ae7b67a` · 2026-08-30 밤)

> 이 블록은 손으로 갱신한다. 위 SHA 는 **이 요약이 서술하는 상태의 기준 커밋**이지 블록을 쓴 커밋이 아니다.
> `git log --oneline ae7b67a..HEAD` 에 커밋이 있으면 그 커밋들이 아래 항목을 바꿨는지 먼저 본다 —
> 바꿨다면 블록을 믿지 말고 CI 최신 실행과 검사 재실행으로 실측하고, 이 블록을 갱신한다.

- **마일스톤:** **M2 완료(2026-08-29 · D-76) · M3 진입 전 2차 정비는 관통 4회 전부 FAIL 로 중단(2026-08-30 밤).**
  단위 `feat-20260830-harness-defects-w3qu` 는 **`status: active` 로 열려 있다** — close 하지 않았다.
- **G-M3 선행 Q-06 은 해소됐다.** BMAD 본체 `v6.10.0`(`081e64ee5aab…`)을 아카이브했다(`460f992`) —
  `archive/bmad-code-org-BMAD-METHOD/`, Core 13 + BMM 33 = **46개 SKILL** 을 파일 경로·산출물 경로·대화형 여부까지 표로.
  검사 3건 실측: `validate-repo-archive.sh` PASS · 인덱스 19개 · `check-archive-licenses.py` PASS(계획 §1.3 표를 19행으로 늘렸다).
  **G-M3 후보표는 아직 만들지 않았다** — 재료는 갖춰졌고 사용자 확정만 남았다(D-52).
- **BMAD 가 계획의 두 전제를 뒤집었다:** ① **Codex 를 지원한다**(`platform-codes.yaml` 에서 preferred, 프로젝트 타깃 `.agents/skills`) —
  계획 §7 M3 의 "Codex 미지원 시 정직 표기" 는 이 SHA 에서 틀리다. 다만 agent team(party-mode)은 Claude Code 전용이다.
  ② **산출물 경로를 `_bmad-output/**` 로 고정하면 안 된다** — `project_knowledge` 기본값이 `docs` 라 `bmad-document-project` 는 `docs/**` 에 쓴다(K-62).
  그리고 `.agents/skills` 가 `romeo compile` 의 쓰기 대상과 **겹친다**(K-64·K-68 에서 다뤄야 할 실제 충돌 지점).
- **정비 단위는 왜 안 닫혔나 — 4회 관통, 4회 FAIL. 실패 원인이 매번 달랐다.**

  | 회차 | run | 검토자 지적 | 실질 원인 |
  | --- | --- | --- | --- |
  | 1 | `run_f4f810c1baa6` | findings 5건 (확인란 무단 변경 · `list_outputs` pruned 누락 · check-6·8·9 가 AC 를 검사 안 함 · 검사 id 정규식 오인) | 검증 계획(목표) |
  | 2 | `run_2b_harness_defects` | check-7 의 `\|\| true` 가 종료 코드를 항상 0 으로 만든다 | 검증 계획(목표) |
  | 3 | `run_3c_harness_defects` | `.compile-*` staging 이 목록에 없다 | AC-4 가 문자 그대로는 달성 불가(목표) |
  | 4 | `run_4d_harness_defects` | evidence 의 `spec_ref.sha256` 이 계약과 다르다 | **하네스의 절차적 모순** |

  1~3 은 전부 반영해 고쳤다(재승인 3회 — `99e9031`·`5aa0c68`·`ae7b67a`). **확인란을 바꾼 것은 마지막 한 번뿐**이다(AC-4 한정).
- **4회차 FAIL 은 흔들림이 아니라 체계적이다 — 표본 2건이 같은 사유로 FAIL 했다**(`run_4d_harness_defects` · `run_4d_review2`, §6.6 재실행 · 계약 `cmp` identical · 방어 검사 둘 다 유효).
  `close --dry-run` 은 `AC_ALL_CHECKED`·`AC_TEXT_UNCHANGED`·`SPEC_UNCHANGED_SINCE_EVIDENCE` 를 **전부 PASS** 로 내고 `REVIEW_VERDICT` 만 FAIL 이다.
  모순의 형태: **① `AC_ALL_CHECKED` 가 체크를 요구 → ② 체크하면 spec 해시가 바뀜(`d848729d`→`6796bef2`) → ③ evidence 는 그 시점 spec 을,
  계약은 승인 커밋 spec 을 가리킴 → ④ 검토자가 둘의 일치를 요구 → 절차를 따르면 어떤 단위도 닫히지 않는다.**
  하네스 자신은 이를 허용한다(`AC_TEXT_UNCHANGED` 가 "체크 표시 제외" 로 비교하는 것이 그 증거). **검토자만 이 규칙을 모른다** — Q-10 (a) 가 실증됐다.
- **구현은 완성돼 있다(미커밋).** 워크트리 `impl-feat-20260830-harness-defects-w3qu` 에 9개 파일 —
  검사 9건 exit 0 · unittest **455** · 봉투 앵커 5/5 양쪽 · 음성 대조 4건(check-6·8·9 와 새 check-7 이 구현 전에는 실패하는 것을 실측).
  결함 5건(파서 사유·템플릿 제약·프롬프트 하드코딩·`compile --list-outputs` 29개+패턴·RUNBOOK 늦은 채택 관측)은 전부 반영됐다.
- **이 관통이 새로 드러낸 하네스 결함 7건 (미반영 — 다음 정비 후보, 우선순위 순):**
  ① **검토자 기준이 하네스 규칙과 충돌한다** — AC 체크로 인한 spec 해시 차이를 FAIL 로 본다. 고칠 자리는 `core/workflows/review/SKILL.md` 의 FAIL 사유 열거이거나 evidence 의 `spec_ref` 기록 방식(작업 트리 → `base_sha` 시점). **이것부터다.**
  ② **`expect` 가 판정에 쓰이지 않는다** — `required_checks` 는 exit code 만 대조한다. 사람은 `expect` 를 조건으로 읽고 쓰지만 기계는 보지 않는다. 1·2회차 실패의 공통 원인이고, 검사 4개가 빈 검사였다.
  ③ **반복 중단 카운터가 재검토로 리셋된다** — `romeo/run_unit.py:73` 은 "마지막 재검토 이후" 만 세는데, `AGENTS.core.md` §10 은 리셋 사유를 **성공으로만** 한정한다. 문서와 코드가 어긋나고, 재검토를 반복하면 중단선이 영원히 안 걸린다.
  ④ **검토자에게 lifecycle 이 없다** — `worker-start` 에 샌드박스 전달 경로가 없어(`--help` 실측: `--agent`·`--model`·`--effort` 뿐) `-s read-only` 를 걸려면 비대화형 `-o` 경로뿐이고, 그 경로엔 `worker_done`·heartbeat·`ask` 가 없다. 완전 해결은 Orca 쪽 기능이거나 `agent_prompt_stalled` 원인 규명에 달렸다.
  ⑤ **비대화형 검토자 경로에 Task 정리·완료 신호가 강제되지 않는다** — RUNBOOK §3.7 이 "사람이 `task-update` 로 정리해야 한다" 고만 적어 두 세션 연속 빠뜨렸다. 회수·정리·완료신호를 명령 하나로 묶어야 한다.
  ⑥ **`codex exec` 가 argv 프롬프트를 받고도 stdin 을 기다린다** — 배경 실행에서 무한 대기(2026-08-30 실측: 4시간 51분, CPU 0.07초). RUNBOOK §4 의 명령형에 `< /dev/null` 이 없다.
  ⑦ **논리 역할 이름과 provider 모델 id 가 구분되지 않는다** — `sol` 은 400(`ChatGPT 계정에서 지원되지 않음`), 실제 id 는 `gpt-5.6-sol`. 문서에 매핑이 없다.
- **다음 세션이 이어갈 자리 (순서대로):**
  1. **결함 ①을 고친다** — 이것이 닫히지 않으면 어떤 작업 단위도 close 되지 않는다. 관통 밖에서 한다(§10).
  2. 그 수정을 포함해 **새 base 로 정비 단위를 재개** — 구현은 워크트리에 그대로 있으므로 재사용한다.
  3. **G-M3 후보표 → 사용자 확정**(D-52). 재료는 `archive/bmad-code-org-BMAD-METHOD/04-components-table.md`·`05-pm-harness-notes.md` 에 있다.
- **CI:** 오늘 푸시하지 않았다 — `460f992`·`99e9031`·`5aa0c68`·`ae7b67a` 는 로컬에만 있다. 푸시는 별도 승인 대상이다(K-66).
- **낡은 워크트리:** 기존 목록에 더해 **`bmad-archive`**(아카이브 원본 · 회수 완료) · **`impl-feat-20260830-harness-defects-w3qu`**
  (**구현 9개 파일이 미커밋으로 살아 있다 — 지우면 오늘 만든 것이 사라진다**). 정리는 승인 대상이다(K-66).
- **문서 지연:** 「미검증·남은 위험」은 맨 위 소절(M2 close 이후)만 최신이다.

## 마일스톤

| 마일스톤 | 상태 | 근거 |
| --- | --- | --- |
| M0 정책표·fixture·분류 카드 | **완료** | [원문](archive/milestones.md) |
| M1 T0 최소 관통 (Claude 단독, 현재 작업 공간) | **완료** | [원문](archive/milestones.md) |
| M2 어댑터·역할·Orca 위임·T1 교차 관통 | **완료 (2026-08-29 · D-76)** | [원문](archive/milestones.md) |
| M3 ~ M7 | 미착수 | [원문](archive/milestones.md) |

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
