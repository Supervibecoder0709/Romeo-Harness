---
id: progress
type: planning
status: active
updated: 2026-08-27
authority: derived
---

# 구현 진행 상태

[구현 계획](implementation-plan.md) §10 체크리스트 기준. 완료 판정은 관찰 가능한 결과로만 한다(K-51).
정지선·결정은 [decision-register](../decisions/decision-register.md) "구현 착수 결정"(D-59~D-71).

## 마일스톤

| 마일스톤 | 상태 | 관찰 가능한 결과 | 커밋 |
| --- | --- | --- | --- |
| M0 정책표·fixture·분류 카드 | **완료** | `bin/romeo route --fixtures fixtures/requests --report` → 33/33 일치(100%), gate 누락 의심 0 · `python3 -m unittest discover -s tests` → 23 PASS · 카드 5건 ≤ 29줄 · shadow 1차 5건 사람 확정(수정 2건 반영 후 100% 유지) | `73501f8` |
| M1 T0 최소 관통 (Claude 단독, 현재 작업 공간) | **완료** | `docs/work/chg-20260827-gitignore-harness-runs-mj9p/` · `docs/work/chg-20260827-rg-fallback-validate-245m/` 각각 `spec.md`(status done) + `evidence/run-m1.yaml`(head_sha·dirty_tree_hash·commands 3건 exit 0) · `romeo close` PASS 2건 | `2260605`~`48f7298` |
| M2 어댑터·역할·Orca 위임·T1 교차 관통 | **진행 중** | 진입 조건 3건 중 2건 완료 — **G-M2 게이트 닫힘**(D-67: 7종 14파일 accepted · 4종 deferred · 3종 rejected, `provenance/imports.yaml`), **역할 바인딩 확정**(D-68: implementer=claude · reviewer=codex). 남은 것: LICENSE Apache-2.0 교체(D-41, 첫 `vendor/` 복사 직전) | — |
| M3 ~ M7 | 미착수 | — | — |

## §10 체크리스트

| # | 항목 | 상태 | 근거 |
| --- | --- | --- | --- |
| 1 | §9.2 결정 1~5 확정 | 완료 | D-41·D-43·D-59·D-60·D-61 accepted (`50a6026`) |
| 2 | fixture 15~20건 (사용자 3개월 요청 포함) | 완료 (33건) | `fixtures/requests/` — 세션 로그 24 · 대화 압축본 5 · 저장소 4. `bin/romeo fixtures check` PASS |
| 3 | 정책표 3종 + 스키마 + Tech Spec 템플릿 + `/plan` SKILL | 완료 | `core/policy/*.yaml`, `core/schemas/*.json`, `core/templates/tech-spec.md`, `core/workflows/plan/SKILL.md`. 리포트 100% / gate 누락 0 |
| 4 | `romeo validate`·`new`·ID + unittest | 완료 | 23 PASS. 같은 날 같은 slug 300건 생성 시 충돌 없음(`tests/test_ids_schema_frontmatter.py`) |
| 5 | `/plan --dry-run` 5건 shadow | 완료 | `fixtures/shadow/2026-08-27-cards.md` 1차 검토 결과표. 5건 모두 `human_correction` 기록(confirmed 3 · corrected 2). 수정률 2/5 = 40%, unit·gate 수정 0/5 |
| 6 | M1: T0 2건 관통 | 완료 | 위 M1 행. M0 fixture `fx-repo-gitignore`·`fx-repo-rg-fallback` 가 같은 요청이다 |
| 7 | stale 거부·미체크 AC 거부 | 완료 (테스트 기준) | `tests/test_docs_evidence_close.py`: 커밋 이동·tracked 수정·staged·untracked 4경우 FRESH_* 거부, 미체크 AC·required_check 누락·변경 없음 거부. 실제 단위에서는 evidence 없는 close 거부 1건 관찰 |
| 8 | G-M2 채택 게이트 | 완료 | 고정 SHA `b36e082` 원문 14개 스킬을 받아 상호 참조 실측 → 후보표 제시 → 사용자 확정. `provenance/imports.yaml` 15항목(accepted 8 · deferred 4 · rejected 3), D-67~D-71 |
| 9 | LICENSE Apache-2.0 교체 + `THIRD_PARTY_NOTICES.md` | 미착수 | D-41. 첫 `vendor/` 복사와 같은 커밋 |
| 10 | `vendor/obra-superpowers@b36e082/` 원문 복사(14파일, 수정 0) | 미착수 | 해시 대조로 수정 0 검증 |
| 11~ | 어댑터·역할·envelope·parity | 미착수 | 계획 §7 M2 |

## 세션 기록

- **2026-08-27 (M2 진입 · G-M2 게이트 세션)** — 후보 14종의 상호 참조를 고정 SHA 원문에서 실측해, 채택 7종의 나가는 참조가 세트 안에서 전부 닫힘을 확인했다. 오케스트레이션 4종은 Romeo 라우터·Orca 와 같은 자리를 차지해 보류(D-67). 계획 §6 의 "본문 도구명 0건" 이 사실 오류임을 발견해 정정했다(D-71 — 6개 스킬에 도구명 존재). `writing-plans` 의 두 규율을 Tech Spec 템플릿에 흡수(D-69), OpenWiki 선행 조건 추가(D-70).
- **2026-08-27 (shadow 1차 검토 세션)** — 카드 5건 사람 확정. `mode` 와 `uncertainty` 각 1건 수정 → fixture 5건에 `human_correction` 기록, 정책표 리포트 33/33 유지. M0 체크리스트 전항목 완료.
- **2026-08-27 (M0+M1 착수 세션)** — 사용자 결정 8건 수렴 → M0 빌드 → fixture 확정(24건) → M1 T0 2건 승인·관통. Claude Code 가 `.claude/skills/plan`·`plan-close` 를 스킬로 discovery 하는 것을 세션에서 관찰(K-68 Claude 쪽). Codex discovery 는 미확인.

## 미검증·남은 위험

- **A-13 첫 측정 완료(5/20건)** — 카드 단위 수정률 2/5 = 40%. unit 0/5 · hard gate 0/5 수정(둘 다 정확), mode 1건·2질문 1건 수정. 실패 지점은 정책표가 아니라 **요청 원문 → 분류축 매핑**이었고, 두 건 다 요청에 섞인 조사·판단 단계를 놓쳐 깊이를 낮게 잡은 유형이다. 표본 5건은 아직 작다 — V-10 목표 20건까지 15건 남았다.
- hard gate 8 중 fixture 가 있는 게이트는 privacy-security·migration·availability 3종. 나머지 5종(payment·legal·ops-data-deletion·public-api·irreversible-policy)은 실제 요청이 없어 M3 조건("게이트별 fixture ≥ 1")이 아직 미충족.
- `romeo` 는 Python 3.9 + PyYAML 로만 검증했다. CI(python 3.11)에서는 아직 실행하지 않았다.
- `.agents/skills` 투영·Codex discovery(A-11)·Orca dispatch(A-06)는 M2 에서 실측한다.
- **G-M2 채택분은 아직 파일로 존재하지 않는다.** 게이트 결정만 기록됐고 `vendor/` 복사·어댑터 투영·discovery 프로브(K-68)는 미실행이다. 채택 7종이 두 런타임에서 실제로 discovery 되는지는 **미검증**이며, 실패한 스킬은 `rewrite` 로 강등한다(D-53).
- override 3건(`orca worktree create` 치환 · deny 목록 · reviewer 바인딩 치환)은 문서에만 있고 `.harness/bindings.yaml`·`.claude/settings.json` 이 아직 없다. verbatim 원문은 수정하지 않으므로, override 가 실제로 작동하는지는 충돌 fixture 로만 확인할 수 있다.
