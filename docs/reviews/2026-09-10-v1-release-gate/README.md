---
id: review-20260910-v1-release-gate
type: review
status: decided
updated: 2026-09-10
authority: derived
---

# v1 릴리스 게이트 판정 자료 — V-0~V-11 증거 대조 (2026-09-10)

정본은 `docs/requirements/v1-scope.md` 「v1에 반드시 들어가는 것」이고, 계획 §10 #15 가 이 판정을 요구한다.
**판정: 사용자가 2026-09-10 추천대로 확정했다 → [D-82](../../decisions/decision-register.md) · V-5 문구 개정 5 · Q-102 신설 · `v0.1.0` 로컬 태그.** 이 문서는 각 항목을 **오늘 실행한 명령·종료 코드·파일**로 대조한 표이고, 충족하지 못한 낱말을 숨기지 않는다(K-51).
기준 리비전 `effb059`(shadow 2차 커밋). 실측 명령은 모두 이 체크아웃에서 2026-09-10 에 돌렸다.

## 대조표

| # | 정본의 완료 기준 | 증거 (명령 → 결과) | 판정 제안 |
| --- | --- | --- | --- |
| V-0 | 실제 요청 fixture 15~20건 · 각 fixture 에 입력·기대 unit·기대 gate·기대 문서 패키지·허용 대안·사람의 수정 결과 | `fixtures/requests/*.yaml` 38건 · `romeo fixtures check` → `PASS 38 fixtures` exit 0 · `human_correction.verdict` 기록 20건(shadow-1 5 · gate-coverage 5 · shadow-2 10) · 38건 중 4건은 `source.kind: authored`(Q-50) | **충족** — 20건이 모든 필드를 가진다. 나머지 18건은 사람 수정 결과가 `null`(V-0 의 수 요건 밖) |
| V-1 | `SKILL.md` v1: tier 정의 · 2질문 rubric · hard gate 8 · 정책 충돌 우선순위 · 상태·frontmatter·명명 규약 · few-shot 자리 | `core/workflows/plan/SKILL.md`(71줄) + `core/policy/classification.yaml`(units 4 · two_questions · hard_gates **8** · conflict_priority · reclassification) · `core/schemas/frontmatter.json` · `romeo id` | **부분 충족** — 「정책 충돌 우선순위」는 정책표(`conflict_priority`)에 있고 SKILL 본문은 언급하지 않는다(라우터가 정책표를 읽으므로 동작은 같다). **「few-shot 자리」는 어디에도 없다** — 결정·Q 기록도 없다. shadow 20건의 수정 3건이 그 자리에 들어갈 예시다 |
| V-2 | 템플릿 3개(Tech Spec + Planning Capsule · T1 Compact Brief · T2 Charter) · 각 길이 캡 명기 | `core/templates/tech-spec.md`(Planning Capsule 절) · `compact-brief.md` · `charter.md` · 길이 캡 `packages.yaml budgets`: capsule 20 · spec 150 · brief 120 · charter 250 · `romeo validate` 가 캡을 검사(exit 0) | **충족** |
| V-3 | `/plan`: 재사용 검색 → 분류 제안 → gate 체크리스트 인쇄 → 사람 1클릭 확정 → 필요한 문서만 생성 · 재실행 = 재분류 | `romeo route --proposal … --card` 가 재사용 후보·2질문·게이트 8 체크리스트를 인쇄(오늘 shadow 카드 10장) · `romeo approve`(확정) · `romeo new`(패키지만 생성) · SKILL §「재분류」= `routing.history` append(D-09·D-11) | **충족** |
| V-4 | `/plan-close` + 검증: 스키마·링크·미체크박스·예산·open-loop → 상태 확정 + `current/` 갱신 | `romeo close`(SCHEMA·UNCHECKED·OPEN_LOOP·FRESH_HEAD·FRESH_TREE·EVIDENCE_* 코드) · `romeo validate` exit 0 · `romeo integrity` → 「등록 1건 · 미등록 0건 · 위반 0건」 exit 0 · `docs/current/enforcement.md` 승격 1건 · 실사용 close PASS 다수(최근 `feat-20260910-…-37qi` 1회차) | **충족** |
| V-5 | 최소 어댑터: 공통 정의 → `CLAUDE.md`/`AGENTS.md` · `.claude/agents ↔ .codex/agents` · `.claude/skills ↔ .agents/skills` · managed marker + source hash | `romeo compile --check` → `compile 검사 PASS` exit 0 · `CLAUDE.md`·`AGENTS.md` 1행 `<!-- romeo:managed start v0.1.0 source=… sha=… -->` · `.claude/skills/**` ↔ `.agents/skills/**` 산출(`.harness/compiled.yaml`) · `.claude/agents/{implementer,reviewer}.md` 산출 · **`.codex/agents` 는 없다** — codex 쪽 역할은 `.harness/bindings.yaml` 의 실행 플래그(`codex exec -s read-only` / `-s workspace-write`)로 강제한다(D-68) | **부분 충족** — `.codex/agents` 는 만들지 않았고 그 대신 실행 플래그가 역할을 강제한다. 정본 문구를 D-68 에 맞춰 고칠지, 파일을 만들지는 사용자 결정 |
| V-6 | 역할 2개: `implementer`(writer, worktree 당 1명) / `reviewer`(read-only) | `core/roles/implementer.yaml`·`reviewer.yaml` · `.harness/bindings.yaml` 기본·교체 4칸 · reviewer read-only 쓰기 거부 로그(§10 #19 완료) · implementer 의 `.claude/settings.json` 승인 게이트는 **미관측**(CLAUDE.md 역할 표) | **충족** — 단, implementer 쪽 강제 수단이 실제로 막는지는 미관측으로 남아 있다(완료로 세지 않음) |
| V-7 | Evidence 계약: C-E1 최소 필드(repo_id·run_id·task_id·spec_ref·base_sha·head_sha·dirty_tree_hash·commands·exit_codes·environment·started_at·finished_at·artifact_hash·reviewer·verdict) | 실물 `docs/work/feat-20260910-sealed-run-worker-settle-37qi/evidence/run_3bc199b43f95.yaml` 최상위 키 21개에 14개 필드가 그대로 있고 `exit_codes` 는 `commands[].exit_code` 로 명령마다 붙는다 · 증거는 `romeo evidence run` 만 쓴다(K-51) | **충족** |
| V-8 | 부착 상태 파일: 하네스 버전과 활성 기능만 · 인증정보 없음 | `.harness/romeo.project.yaml`: `harness_version 0.1.0` · `policy_version` · `modules` 5종 상태 · token/secret/password 문자열 0건 · `romeo doctor --strict` → 「저장소 PASS · 런타임 PASS」 exit 0 | **충족** |
| V-9 | 수직 슬라이스 1건 관통 — 실제 T1 → 카드 → 확정 → Brief+Spec → Orca dispatch → A implementer / B read-only reviewer → HEAD 증거 → close → **A/B 역할 교체 재현**(결정적 게이트: 봉투 스키마·required_checks·권한 상한·구현자 면 gate 판정 · 검토자 판정은 advisory, D-76) | §10 #26 T1 관통 완료 · #27·#33 교체 관측 · #36 게이트 PASS(관측 2건) · #48 D-76 close · 오늘 `romeo fixtures parity --report` → 「핵심 동등성 게이트: PASS — 관측 2건」 exit 0(검토자 면은 advisory 로 인쇄) · 그 뒤 M3·M4 관통 십수 건이 같은 경로로 close | **충족** (개정 4 의 정의로) |
| V-10 | shadow mode 20건 · 분류 전수 사람 확인 · 오분류는 fixture + rubric 예시로 축적 | `romeo metrics` → 분류 수정률 15.0% · 관측 20건 · gate 누락 0 · `fixtures/shadow/2026-08-27-cards.md`(5) · `2026-09-10-cards.md`(10) · gate-coverage 5 · 수정 3건은 fixture `human_correction.changes` 에 있음 · **rubric 예시로는 아직 안 옮김**(A-13: 같은 유형 3번째에 옮길지 결정) | **충족** — 「rubric 예시로 축적」의 절반(fixture)만 했다. 예시 추가는 V-1 의 few-shot 자리와 같은 결함 |
| V-11 | 부품 연결 1세트: G-M2 통과 → `provenance/imports.yaml` accepted + `vendor/` 원문 + 두 런타임 discovery 프로브 + 충돌 fixture 3종 PASS · M3 에서 BMAD/CIS install 프로브 + `/plan` 링크 | `provenance/imports.yaml` accepted 9건 · `vendor/obra-superpowers@b36e082/` · `fixtures/conflicts/c1~c7` 7종 · `romeo doctor --strict` exit 0 · G-M3 5단계 「공존한다」(`feat-20260831-bmad-install-observe-a3bm`) · 카드가 bmad-cis 추천 11종·`inputs:` 요구·프로브 결과를 인쇄(오늘 s07·s16 카드) | **충족** |

## 요약

| 판정 | 항목 |
| --- | --- |
| 충족 | V-0 · V-2 · V-3 · V-4 · V-6 · V-7 · V-8 · V-9 · V-10 · V-11 (10건) |
| 부분 충족 | **V-1**(few-shot 자리 없음 · 충돌 우선순위가 SKILL 본문에 없음) · **V-5**(`.codex/agents` 없음, 실행 플래그로 대체) |
| 남아 있는 미관측 | implementer 쪽 권한 상한(`.claude/settings.json` 승인 게이트)이 실제로 막는지 — V-6 의 강제 수단이고 완료로 세지 않는다 |

## 추천 (판정은 사용자)

**추천: 두 부분 충족을 「정본 문구 개정」으로 닫고 v1 완료를 선언한 뒤 `v0.1.0` 태그(§10 #17)로 간다.** 이유는 둘 다 동작이 아니라 낱말의 결함이라서다.

- V-5 의 `.codex/agents` 는 codex 런타임에 그런 개념이 없고 역할 강제는 실행 플래그가 이미 하고 있다(D-68 · 관측됨). 정본 문구를 「역할 바인딩은 `.harness/bindings.yaml`, 강제는 런타임별 수단」으로 고친다.
- V-1 의 few-shot 자리는 **작은 실제 결함**이다 — shadow 가 모은 수정 3건(같은 유형 2건)이 들어갈 자리가 없다. 정본을 고치지 않고 **다음 정비 단위**로 연다(Q 신설): `classification.yaml two_questions.uncertainty` 에 「요청에 계획·판단 요구가 섞이면 medium」 예시 1건 + SKILL 에 정책 충돌 우선순위 한 줄. v1 선언을 이것에 묶지 않는다 — 20건 중 unit·gate 수정 0 이라 라우터의 동작은 이미 증명됐고, 예시는 제안 정확도를 올리는 개선이다.

**추천이 달라지는 조건:** 사용자가 「few-shot 자리」를 v1 의 필수 산출물로 본다면 정비 1회(약 반나절) 뒤에 선언한다. 그 경우 이 문서의 V-1 행만 다시 실측한다.

**되돌리기:** v1 선언은 결정 기록(D-xx) 한 줄과 progress 한 줄이고 태그는 로컬 태그다. 태그 푸시 전까지 저장소 밖 상태는 바뀌지 않는다.
