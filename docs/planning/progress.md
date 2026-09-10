---
id: progress
type: planning
status: active
updated: 2026-09-11
authority: derived
---

# 구현 진행 상태

[구현 계획](implementation-plan.md) §10 체크리스트 기준. 완료 판정은 관찰 가능한 결과로만 한다(K-51).
정지선·결정은 [decision-register](../decisions/decision-register.md) "구현 착수 결정"(D-59~D-71).

`계획 §10` 열은 이 표의 행이 계획 §10 의 어느 번호에 대응하는지다. 두 표의 번호가 어긋나
계획의 확인 기준이 조용히 사라지는 것을 막는다(1차 리뷰 F16). `—` 는 계획 §10 에 번호가 없는 항목이다.

독립 리뷰 findings 원문은 `docs/reviews/` 에 라운드별로 보관한다 —
[1차(F01~F31)](../reviews/2026-08-28-m2-round1-review/README.md) · [2차(G01~G13)](../reviews/2026-08-28-m2-round2-review/README.md).

## 지금 상태 (기준 `5d5c5f5` · 2026-09-11)

> **예산 30줄·2KB.** 회차 서사와 결함 표는 작업 단위(`docs/work/<id>/`)와 `attempts.yaml` 이 소유한다 —
> 여기 옮겨 적지 않는다(K-63). 아래가 낡았는지는 `git log --oneline <아래 SHA>..HEAD` 로 본다.

- **마일스톤:** M2·M3·M4 완료 · v1 완료 선언(D-82 · `v0.1.0`). **v1.1 의 첫 이니셔티브 M5 `attach` 착수 — Charter 4마일스톤 중 M1 완료(2026-09-11 · 통합 `5d5c5f5`).**
- **활성 작업 단위:** `init-20260911-m5-attach-update-rollback-sauc`(M5 · T2 · **M1 done**, M2~M4 미착수). 요구사항 원본의 「올린 것」 9건 중 Q-66·Q-67 은 #13c 가 이미 닫았고, 이번에 **Q-53·Q-55 를 닫고 Q-54 의 M1 몫**을 닫았다. 남은 입력은 Q-54 후반·Q-58·Q-59·Q-60·Q-65.
- **M1 이 닫은 것 — 주의문이 메우던 자리에 집행을 두었다.** 「무엇이 있어야 부착인가」의 정본은 이미 `scenarios/10-attach-payload.md` 의 「놓는 것」 절이었고 그것을 읽는 검사도 있었다. 없던 것은 **`doctor` 가 그 정본을 읽는 것**뿐이었고, 그 구멍을 문서의 「4번을 단독으로 쓰지 않는다」는 주의가 메우고 있었다. 새 매니페스트를 만들지 않고 정본을 읽는 코드를 `romeo/attach.py` 로 꺼내 두 자리가 같은 문서를 읽게 했다 — 목록을 하나 더 만들면 어느 쪽이 요구인지 말할 수 없다.
- **회차 3 · 재승인 1.** 1회차 검토자 FAIL(findings 1) — AC-9 의 「40자 hex」에 대문자가 들 수 있는데 `_HEX40` 이 소문자만 받아 그럴듯한 거짓 값에서 실재성 검사를 건너뛰었다. 2회차에서 고쳐 검토자 PASS 였으나, **1·2회차 모두 RUNBOOK §4 의 `review-tree-before/after` 없이 돌아** close 가 그 판정이 어느 산출물을 본 것인지 확인하지 못했다(`REVIEW_VERDICT UNVERIFIED`). 봉인된 run 에는 더 쓸 수 없어(Q-101) **재승인 뒤 같은 산출물을 시딩해 3회차**에서 그 기록과 함께 다시 검토받았다 — 검토자 PASS · findings 0 · 방어 검사 유효.
- **승인 전 검증:** AC 반박 3회(6·8·1건)로 AC 가 6→9개. 2차의 「문서가 달라지면 무조건 실패하는 구현도 충족한다」가 AC-5 를 **양방향**으로 바꿨고, 「안팎이 서로 다른 오류 종류라 범위 제한과 검사 제거가 구별되지 않는다」가 AC-6 을 심링크로 통일했다. 검사 6종을 승인 전 실측(판별 1 exit 1 · 회귀 5 exit 0).
- **다음 행동:** M5 **M2**(`romeo attach` — preflight · 파일별 승인 · 원자적 적용 · **Q-54 복제/참조 결정** · Q-58·Q-59·Q-60). 그 결정이 계획 §3.1 개정을 요구하면 D-xx 로 올린다.
- **blocker:** 없음. **미푸시** — 통합 `5d5c5f5` 와 이 갱신 커밋.
- **최신 CI:** `9ed5ba8` success(2026-09-10). 이번 통합은 아직 푸시 전이라 CI 가 돌지 않았다.
- **열린 park:** Q-12·13·15~17·19·23·24·26·32~35·46·49~52·54(부분)·56~61·62~65·69~70·71~77·78~82·83~89·92·93·97·98·99·100·**103·104**(`open-questions.md`). **Q-53·Q-55 해소.**
- **이 관통이 §12 로 남긴 것:** Q-103(`review record` 가 §4 방어 검사 없이도 봉인해 준다 — 요구하는 자리와 보는 자리가 회차 하나만큼 떨어져 있다) · Q-104(`fill_brief.py` 가 `--base-sha` 의 실재성을 보지 않아 지어낸 hex 가 브리프에 인쇄된다).
- **다음 정비 후보:** Q-103·Q-104 → Q-83 → Q-64 → Q-69·Q-70·Q-99 → Q-82 → Q-88. Q-89(1회차 통과율)는 이번이 **3회차** close 라 1회차 PASS 가 아니다.
- **진단 (2026-09-07):** 자가봉착의 뿌리는 **판정하는 하네스와 판정받는 하네스가 같은 리비전**이라는 것(`docs/reviews/2026-09-07-self-application-diagnosis/`). 권고 1·2·3 은 집행됐고 D-81·Q-02 로 이어졌다. **이번 close 는 승인 커밋 스냅샷의 하네스가 냈다(JUDGE_REVISION).**
## 마일스톤

| 마일스톤 | 상태 | 근거 |
| --- | --- | --- |
| M0 정책표·fixture·분류 카드 | **완료** | [원문](archive/milestones.md) |
| M1 T0 최소 관통 (Claude 단독, 현재 작업 공간) | **완료** | [원문](archive/milestones.md) |
| M2 어댑터·역할·Orca 위임·T1 교차 관통 | **완료 (2026-08-29 · D-76)** | [원문](archive/milestones.md) |
| M3 기획 깊이 확장 (T2·discovery·gate·doctor) | **완료 (2026-09-04)** — 마지막 조각인 charter 를 쓰는 실제 T2 관통이 `init-20260904-m4-doc-reuse-metrics-wr9m`(1회차 close PASS · 5/5 · 재실행 5/5 · 검토자 PASS findings 0 · 통합 `ec4f97c`)로 닫혔다. 그 관통이 M4 이니셔티브를 열고 첫 마일스톤(재사용 검색)까지 닫았다. 이하는 그 이전 경과다 — G-M3 는 §6.1 **1~5단계 전부 닫힘**(D-77 + `feat-20260831-bmad-attach-probe-tgnb` + `feat-20260831-bmad-install-observe-a3bm`). **5단계 결론은 「공존한다」**. 그 뒤 **관통 사이의 하네스 정비 3회**를 마쳤다 — 1회는 `feat-20260831-park-defects-actm`(park 결함 5건 · 5회차 `run_e3a4af18582c` close · 16/16), 2회는 `feat-20260901-coordinator-procedure-gaps-y8fu`(코디네이터 위임 절차 결함 3건 · 2회차 `run_fc79c4267d1c` close · required_checks 15/15 · 재실행 15/15 · 앵커 양쪽 5/5 · 검토자 PASS findings 0), 3회는 `feat-20260901-task-copy-brief-count-erc6`(`task/` 사본 병합 충돌 · 브리프 검사 개수 하드코딩 · **1회차** `run_e909a3e53aea` close · required_checks 14/14 · 재실행 14/14 · 앵커 양쪽 5/5 · 검토자 PASS findings 0). 그 뒤 **M3 본체로 돌아와 시나리오 3 을 세웠다** — `feat-20260901-charter-discovery-block-a3xs`(계산만 되던 `blocks` 를 승인·종료 두 지점에서 집행 · `core/templates/charter.md`(T2) · `scenarios/` 런북 · **관통 1회차** `run_d947edf2d24a` close PASS · required_checks 17/17 · 재실행 17/17 · 앵커 양쪽 5/5 · 검토자 PASS findings 0). 그 뒤 **시나리오 8 을 세웠다** — `feat-20260901-scenario-8-capability-probe-s7ny`(능력 프로브를 코어에 정의하고 흔적 경로는 어댑터가 소유 · 카드가 부재와 대안을 인쇄 · 차단 `capability-probed` 가 **거짓만 막고 부재는 막지 않는다** · `scenarios/8-capability-absent.md` · **관통 5회차** `run_d7092f3d25c5` close PASS · required_checks 10/10 · 재실행 10/10 · 검토자 PASS · **§10 브레이크 1회 작동**(3회차 goal · 4회차 outputs → 사람 재검토 뒤 5회차) · 재승인 3회 · 그 관통이 낸 결함은 Q-36~Q-42). 그 뒤 **관통 사이 정비 4회차** — `feat-20260902-scope-grammar-procedure-drift-z5mv`(시나리오 8 관통이 낸 결함 Q-36~Q-42 · 승인 산문이 쓰기 권한이 되던 구멍·CI 빈 검사·RUNBOOK/run-unit 어긋남 5건 · Q-38 은 D-80 · **관통 1회차** `run_0b4ed250c691` close PASS · required_checks 16/16 · 재실행 16/16 · 검토자 PASS findings 0 · 승인 전 프로브 양쪽 실측 + 세 렌즈 반박 검증). 그 뒤 **시나리오 9 를 세워 M3 의 런북 조건을 닫았다** — `feat-20260902-scenario-9-guard-enforcement-95e6`(가드 설명 요구 4항목을 `execution-guards.yaml` 단일 출처에서 승인·종료 두 지점이 읽는다 · 거부 경로 `evidence reject` 와 `BLOCKED_APPROVAL` 종결 판정 · `gate-create` 를 코어에서 걷어내 어댑터가 소유(C-C6) · `scenarios/9-guard-approval.md` · **관통 3회차** `run_108f96346abc` close PASS · required_checks 12/12 · 재실행 12/12 · 검토자 PASS · **§10 브레이크 1회 작동**(1회차 `approval_log_state` 가 로그의 note·seq 를 대조하지 않아 두 지점이 같은 yaml 을 두 번 읽었다 · 2회차 AC-10 의 base 재현을 손으로 적어 봉인 누락 → 사람 재검토 「달성 가능」 뒤 3회차) · 그 관통이 낸 결함은 Q-44·Q-45). **계획 §10 #13 의 「시나리오 3·8·9 런북 PASS」 는 충족됐다**. 그 뒤 **관통 사이 정비 5회차** — `feat-20260903-guard-guidance-vendor-drift-bvjz`(시나리오 9 관통이 §12 로 남긴 Q-44·Q-45 · 가드 `--note` 네 항목을 안내 3곳이 몰라 지시대로 따르면 exit 2 로 막히던 것 · 코어 정책에 남은 집행 수단 사본 제거(C-C6) · 라벨을 정책표에서 **읽어** 대조하는 검사(라벨 1개만 개명해도 검사가 즉시 실패하는 것을 실측) · **관통 2회차** `run_52462dd28eae` close PASS · required_checks 9/9 · 재실행 9/9 · 검토자 PASS findings 0 · **1회차는 검토자 FAIL** — AC-3 이 요구한 「라벨을 바꾸면 새 라벨로 대조한다」가 실제로는 「대조를 그만둔다」였고, 그 원인은 spec 의 AC-2 가 둔 「라벨이 하나라도 나타나면」 조건이었다 · 그 관통이 낸 결함은 Q-47·Q-48). 그 뒤 **관통 사이 정비 6회차** — `feat-20260903-runbook-handle-attempts-drift-w7tm`(정비 5회차가 §12 로 남긴 Q-47·Q-48 · §3.7 의 핸들 확인이 「같은 제목」을 기준으로 삼아 TUI 가 제목을 덮어쓰면 막다른 길이던 것을 `.result.terminal.worktreeId`+`worktreePath`+핸들 대조로 옮겼다 · 통합할 때 워크트리 사본이 위임 쪽 판정을 `started` 로 덮던 것을 막는 `run-unit merge-check` 와 RUNBOOK 새 절 §3.10 · **관통 2회차** `run_cc106a316c68` close PASS · required_checks 9/9 · 재실행 9/9 · 검토자 PASS findings 0 · **1회차는 검토자 FAIL** — AC-4 가 AC-3 과 같은 상태를 반대로 판정했고 원인이 산출물이 아니라 완료 정의여서 AC-4 만 고쳐 재승인했다(D-80) · **그 검사의 첫 실사용이 자기 통합이었다** — merge-check 가 exit 1 로 「회차 2 · pass 가 사라진다」를 지목해 막았고 정본을 반영한 뒤 exit 0 · §3.7 의 제목 덮어쓰기도 이 관통에서 재현됐다). 그 뒤 **hard gate 8 커버리지를 채워 §10 #13 의 나머지 절반을 닫았다** — `feat-20260904-gate-fixture-coverage-q3wy`(fixture 0건이던 5개 게이트 payment·legal·ops-data-deletion·public-api·irreversible-policy 에 요청 fixture 를 1건씩 더해 **8/8** · 게이트 id 를 `classification.yaml` 에서 **읽어** 커버리지와 id 유효성을 대조하는 `tests/test_gate_coverage.py` · 판별력을 검사 안에서 매번 재확인한다(fixture 제거·정책표 id 개명·없는 id 주입 · **id 를 하드코딩한 구현은 개명된 정책표에서 통과해 버린다**는 반례) · **관통 2회차** `run_60db3d61480b` close PASS · required_checks 5/5 · 재실행 5/5 · 검토자 PASS findings 0 · **1회차는 검토자 FAIL** — AC-2 가 「route 실행 전에 손으로 적었다」는 사후 관측 불가능한 시간 순서를 요구했고, 원인이 산출물이 아니라 완료 정의여서 AC-2 만 고쳐 재승인했다(D-80). 자기참조를 끊는 자리를 시간 순서에서 **사람의 확인**(`human_correction`)으로 옮겼다 · **merge-check 가 두 번째 실사용에서도 exit 1 로 막았다** — 회차 2 pass 가 사라지는 것을 지목 · 68개 프로젝트 세션 로그(597MB)를 훑어 실제 요청은 payment 1건뿐이라 **나머지 4건은 `source.kind: authored`** — 그 한계는 Q-50 · 그 관통이 §12 로 남긴 관측은 Q-49). **M3 의 나머지는 charter 를 쓰는 실제 T2 관통 하나다** | D-77, `docs/work/feat-20260831-bmad-install-observe-a3bm/`(status done) 통합 `a9e7af1`, `docs/work/feat-20260831-park-defects-actm/`(status done) 통합 `fd7c7b9`, `docs/work/feat-20260901-coordinator-procedure-gaps-y8fu/`(status done) 통합 `c945686`, `docs/work/feat-20260901-task-copy-brief-count-erc6/`(status done) 통합 `045ea08`, `docs/work/feat-20260901-charter-discovery-block-a3xs/`(status done) 통합 `344fc7e`, `docs/work/feat-20260901-scenario-8-capability-probe-s7ny/`(status done) 통합 `50d3901`, `docs/work/feat-20260902-scope-grammar-procedure-drift-z5mv/`(status done) 통합 `3efc026`, `docs/work/feat-20260902-scenario-9-guard-enforcement-95e6/`(status done) 통합 `16c0751`, `docs/work/feat-20260903-guard-guidance-vendor-drift-bvjz/`(status done) 통합 `0b3a263`, `docs/work/feat-20260903-runbook-handle-attempts-drift-w7tm/`(status done) 통합 `2f7c318`, `docs/work/feat-20260904-gate-fixture-coverage-q3wy/`(status done) 통합 `8eee897` |
| M4 문서 재사용·승격·지표 (`init-20260904-m4-doc-reuse-metrics-wr9m`) | **완료 (2026-09-10)** — charter 의 네 마일스톤이 전부 섰다. M1 재사용 검색 `romeo find`(통합 `ec4f97c`) · M2 1-hop 재개 `romeo context`(`feat-20260907-context-one-hop-resume-w5jq` · 통합 `7f77699`) · M3 승격과 무결성 `docs/current/` + `romeo integrity`(`feat-20260909-promote-integrity-kchq` 와 `feat-20260909-promotion-check-coverage-ggkm` · 통합 `177b67d`) · **M4 지표 `romeo metrics`**(`feat-20260909-metrics-four-counters-dyz2` · 3회차 close PASS · 통합 `281b8c8`). 계획 §10 #14 의 관찰 결과 네 가지 — 중복 요청에 기존 unit id 제시 · `docs/current/` 승격 1건 이상 · `romeo metrics` 표 출력 · 깨진 링크 0 — 이 전부 명령의 종료 코드로 선다 | `docs/work/init-20260904-m4-doc-reuse-metrics-wr9m/`(status done) |
| M5 attach (v1.1 · `init-20260911-m5-attach-update-rollback-sauc`) | **진행 중 (2026-09-11 착수)** — Charter 4마일스톤 중 **M1 「부착 정본을 doctor 가 읽는다」 완료**(3회차 close PASS 40건 · 검토자 PASS findings 0 · 통합 `5d5c5f5`). Q-53·Q-55 해소 · Q-54 의 M1 몫 해소. M2(`attach` · Q-54 결정 · Q-58·Q-59·Q-60) · M3(`update --dry-run`·`rollback` · Q-65) · M4(실제 프로젝트 1건 관통 — §10 #16 의 완료 확인 기준) 미착수 | `docs/work/init-20260911-m5-attach-update-rollback-sauc/`(charter) |
| M6 ~ M7 | 미착수 | [원문](archive/milestones.md) |

## §10 체크리스트

항목명·상태·근거 링크만 남긴 완료 표다. 각 행의 근거 원문은 [archive/checklist-8-48.md](archive/checklist-8-48.md) 에 문장 그대로 있다.

| # | 계획 §10 | 항목 | 상태 | 근거 |
| --- | --- | --- | --- | --- |
| 1 | #1 | §9.2 결정 1~5 확정 | 완료 | [원문](archive/checklist-8-48.md#c1) |
| 2 | #2 | fixture 15~20건 (사용자 3개월 요청 포함) | 완료 (33건) | [원문](archive/checklist-8-48.md#c2) |
| 3 | #3 | 정책표 3종 + 스키마 + Tech Spec 템플릿 + `/plan` SKILL | 완료 | [원문](archive/checklist-8-48.md#c3) |
| 4 | #4 | `romeo validate`·`new`·ID + unittest | 완료 | [원문](archive/checklist-8-48.md#c4) |
| 5 | #5 | `/plan --dry-run` 5건 shadow | 완료 — **shadow 2차 10건으로 V-10 20/20 도달(2026-09-10)**, `fixtures/shadow/2026-09-10-cards.md` | [원문](archive/checklist-8-48.md#c5) |
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
| 49 | **#15** | shadow 20건 + **v1 릴리스 게이트 판정** | **완료 (2026-09-10 · D-82)** — 충족 10 · 부분 2(V-1 few-shot 자리 → **Q-102 로 해소 · 통합 `b2307dc`** · V-5 문구 개정 5) · 분류 수정률 15.0%(20건) · gate 누락 0 | [대조표](../reviews/2026-09-10-v1-release-gate/README.md) · `fixtures/shadow/2026-09-10-cards.md` |
| 50 | #17 | 하네스 `v0.1.0` 태그 | **완료 (로컬 태그 2026-09-10)** — 태그 푸시는 별도 승인 · provenance CI 는 `effb059` success | `git tag -l v0.1.0` |

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
