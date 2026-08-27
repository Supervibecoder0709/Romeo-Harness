---
id: progress
type: planning
status: active
updated: 2026-08-27
authority: derived
---

# 구현 진행 상태

[구현 계획](implementation-plan.md) §10 체크리스트 기준. 완료 판정은 관찰 가능한 결과로만 한다(K-51).
정지선·결정은 [decision-register](../decisions/decision-register.md) "구현 착수 결정"(D-59~D-66).

## 마일스톤

| 마일스톤 | 상태 | 관찰 가능한 결과 | 커밋 |
| --- | --- | --- | --- |
| M0 정책표·fixture·분류 카드 | **완료** (shadow 검토 1건 대기) | `bin/romeo route --fixtures fixtures/requests --report` → 33/33 일치(100%), gate 누락 의심 0 · `python3 -m unittest discover -s tests` → 23 PASS · 카드 5건 ≤ 29줄 | `73501f8` |
| M1 T0 최소 관통 (Claude 단독, 현재 작업 공간) | **완료** | `docs/work/chg-20260827-gitignore-harness-runs-mj9p/` · `docs/work/chg-20260827-rg-fallback-validate-245m/` 각각 `spec.md`(status done) + `evidence/run-m1.yaml`(head_sha·dirty_tree_hash·commands 3건 exit 0) · `romeo close` PASS 2건 | `2260605`~`48f7298` |
| M2 어댑터·역할·Orca 위임·T1 교차 관통 | 미착수 | 진입 조건: **G-M2 채택 게이트**(Superpowers 후보표 → 사용자 확정), LICENSE 교체(D-41), 역할 바인딩 승인 | — |
| M3 ~ M7 | 미착수 | — | — |

## §10 체크리스트

| # | 항목 | 상태 | 근거 |
| --- | --- | --- | --- |
| 1 | §9.2 결정 1~5 확정 | 완료 | D-41·D-43·D-59·D-60·D-61 accepted (`50a6026`) |
| 2 | fixture 15~20건 (사용자 3개월 요청 포함) | 완료 (33건) | `fixtures/requests/` — 세션 로그 24 · 대화 압축본 5 · 저장소 4. `bin/romeo fixtures check` PASS |
| 3 | 정책표 3종 + 스키마 + Tech Spec 템플릿 + `/plan` SKILL | 완료 | `core/policy/*.yaml`, `core/schemas/*.json`, `core/templates/tech-spec.md`, `core/workflows/plan/SKILL.md`. 리포트 100% / gate 누락 0 |
| 4 | `romeo validate`·`new`·ID + unittest | 완료 | 23 PASS. 같은 날 같은 slug 300건 생성 시 충돌 없음(`tests/test_ids_schema_frontmatter.py`) |
| 5 | `/plan --dry-run` 5건 shadow | **부분** — 카드 생성 완료, 사람 검토 대기 | `fixtures/shadow/2026-08-27-cards.md`. 사용자 결정: 다음 세션에 검토. `human_correction` 은 아직 전부 null |
| 6 | M1: T0 2건 관통 | 완료 | 위 M1 행. M0 fixture `fx-repo-gitignore`·`fx-repo-rg-fallback` 가 같은 요청이다 |
| 7 | stale 거부·미체크 AC 거부 | 완료 (테스트 기준) | `tests/test_docs_evidence_close.py`: 커밋 이동·tracked 수정·staged·untracked 4경우 FRESH_* 거부, 미체크 AC·required_check 누락·변경 없음 거부. 실제 단위에서는 evidence 없는 close 거부 1건 관찰 |
| 8~ | M2 이후 | 미착수 | 다음 세션: G-M2 후보표부터 (D-66) |

## 세션 기록

- **2026-08-27 (M0+M1 착수 세션)** — 사용자 결정 8건 수렴 → M0 빌드 → fixture 확정(24건) → M1 T0 2건 승인·관통. Claude Code 가 `.claude/skills/plan`·`plan-close` 를 스킬로 discovery 하는 것을 세션에서 관찰(K-68 Claude 쪽). Codex discovery 는 미확인.

## 미검증·남은 위험

- shadow 카드 5건의 사람 검토가 없어 **LLM 분류 정확도는 아직 0건 측정**(A-13). 정책표 100% 는 자기 일관성이다.
- hard gate 8 중 fixture 가 있는 게이트는 privacy-security·migration·availability 3종. 나머지 5종(payment·legal·ops-data-deletion·public-api·irreversible-policy)은 실제 요청이 없어 M3 조건("게이트별 fixture ≥ 1")이 아직 미충족.
- `romeo` 는 Python 3.9 + PyYAML 로만 검증했다. CI(python 3.11)에서는 아직 실행하지 않았다.
- `.agents/skills` 투영·Codex discovery(A-11)·Orca dispatch(A-06)는 M2 에서 실측한다.
