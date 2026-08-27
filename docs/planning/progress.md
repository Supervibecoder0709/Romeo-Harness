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
| 9 | LICENSE Apache-2.0 교체 + `THIRD_PARTY_NOTICES.md` | 완료 | `LICENSE` 202줄 Apache-2.0(Copyright 2026 Supervibecoder0709). `THIRD_PARTY_NOTICES.md` 는 `bin/romeo notices` 가 imports.yaml 에서 생성 · `--check` PASS |
| 10 | `vendor/obra-superpowers@b36e082/` 원문 복사(수정 0) | 완료 | 15파일(스킬 14 + MIT 사본). `bin/romeo vendor check` → **PASS · files=15 blob SHA 일치**. 변조 검출 테스트 5경우(수정·삭제·추가·디렉터리 없음·미등록 id) |
| 11 | CI(python 3.11) 하네스 검사 | 완료 | `.github/workflows/harness.yml` 6단계(unittest·route·fixtures·validate·vendor·notices). GitHub Actions run `33095164296` **success 13s** — 39 tests OK, vendor PASS files=15, notices 일치 |
| 12 | 어댑터 컴파일(`romeo compile`) | 완료 | `core/principles/AGENTS.core.md`·`.harness/bindings.yaml`·`adapters/{claude,codex}/` → 산출물 22개(`CLAUDE.md`·`AGENTS.md` managed block, 두 런타임 스킬 18개, `.claude/settings.json`). `compile --check` PASS. 테스트 24개(마커 밖 보존·idempotent·심링크 대체·투영본 해시·stale 4경우) |
| 13 | 실행 가드 `.claude/settings.json` | 완료 | ask 8건(git push·PR·worktree 삭제·reset --hard) · deny 5건(rm -rf /·sudo rm·force push). K-66 은 "승인 없이 실행 금지"이므로 정당한 작업은 deny 가 아니라 ask 로 뒀다 |
| 14 | `romeo doctor` 부착 검증 | 완료 | 런타임 프로브 5종(claude·codex·orca·gh·git 전부 ✓) · 스킬 파일 프로브(claude 9 · codex 10) · 부착 상태 3종 · 충돌 fixture. **런타임 로드는 PASS 로 세지 않고 `.harness/observations.yaml` 의 관찰만 인쇄한다** |
| 15 | 충돌 fixture 3종 (K-68) | 완료 | `fixtures/conflicts/` — c1 외부 계획 경로·c2 자동 트리거·c3 이름/마커 충돌. **c1 이 게이트에서 놓친 실제 충돌 1건을 잡았다** (`requesting-code-review:60` → `docs/superpowers/plans/`). `overrides.output_paths` 로 흡수 후 충돌 0 |
| 16~ | 역할 실행·envelope·Orca 위임·parity | 미착수 | 계획 §7 M2. `adapters/orca/RUNBOOK.md` 는 envelope 스키마와 함께 만든다 |

## 세션 기록

- **2026-08-28 (어댑터 세션)** — `romeo compile` 을 만들어 코어 → 두 런타임 산출물 경로를 세웠다. TDD 로 계약을 먼저 고정했고, 그 과정에서 실제 버그 2건을 잡았다 — 디렉터리 심링크에 `rmtree` 가 실패하는 문제와, `--check` 가 디렉터리 심링크를 PASS 로 통과시키던 문제. 실행 가드는 계획의 deny 대신 **ask/deny 분리**로 넣었다(K-66 은 금지가 아니라 승인 요구다). 테스트 39 → 63. **컴파일 직후 같은 세션에서 채택 7종이 전부 Claude 스킬 목록에 나타나는 것을 관찰**했다(A-11 Claude 쪽).
- **2026-08-28 (vendor 복사 세션)** — LICENSE 를 Apache-2.0 으로 교체하고 `vendor/obra-superpowers@b36e082/` 에 15파일을 원문 복사했다(blob SHA 15/15 일치). `romeo vendor`·`romeo notices` 를 추가해 수정 0 대조와 고지 생성을 자동화하고, CI 워크플로 `harness.yml` 로 강제했다. 검사기가 `core/workflows/plan/SKILL.md` 의 미등록 출처(anthropics/skills SKILL.md 형식)를 잡아내 `imports.yaml` 에 기록했다. 테스트 23 → 39. CI(python 3.11) 첫 실행 success(run `33095164296`).
- **2026-08-27 (M2 진입 · G-M2 게이트 세션)** — 후보 14종의 상호 참조를 고정 SHA 원문에서 실측해, 채택 7종의 나가는 참조가 세트 안에서 전부 닫힘을 확인했다. 오케스트레이션 4종은 Romeo 라우터·Orca 와 같은 자리를 차지해 보류(D-67). 계획 §6 의 "본문 도구명 0건" 이 사실 오류임을 발견해 정정했다(D-71 — 6개 스킬에 도구명 존재). `writing-plans` 의 두 규율을 Tech Spec 템플릿에 흡수(D-69), OpenWiki 선행 조건 추가(D-70).
- **2026-08-27 (shadow 1차 검토 세션)** — 카드 5건 사람 확정. `mode` 와 `uncertainty` 각 1건 수정 → fixture 5건에 `human_correction` 기록, 정책표 리포트 33/33 유지. M0 체크리스트 전항목 완료.
- **2026-08-27 (M0+M1 착수 세션)** — 사용자 결정 8건 수렴 → M0 빌드 → fixture 확정(24건) → M1 T0 2건 승인·관통. Claude Code 가 `.claude/skills/plan`·`plan-close` 를 스킬로 discovery 하는 것을 세션에서 관찰(K-68 Claude 쪽). Codex discovery 는 미확인.

## 미검증·남은 위험

- **A-13 첫 측정 완료(5/20건)** — 카드 단위 수정률 2/5 = 40%. unit 0/5 · hard gate 0/5 수정(둘 다 정확), mode 1건·2질문 1건 수정. 실패 지점은 정책표가 아니라 **요청 원문 → 분류축 매핑**이었고, 두 건 다 요청에 섞인 조사·판단 단계를 놓쳐 깊이를 낮게 잡은 유형이다. 표본 5건은 아직 작다 — V-10 목표 20건까지 15건 남았다.
- hard gate 8 중 fixture 가 있는 게이트는 privacy-security·migration·availability 3종. 나머지 5종(payment·legal·ops-data-deletion·public-api·irreversible-policy)은 실제 요청이 없어 M3 조건("게이트별 fixture ≥ 1")이 아직 미충족.
- ~~`romeo` 는 Python 3.9 로만 검증했다~~ → 해소. 로컬 Python 3.9 와 CI Python 3.11 양쪽에서 39 tests PASS(run `33095164296`).
- `.agents/skills` 투영·Codex discovery(A-11)·Orca dispatch(A-06)는 M2 에서 실측한다.
- **Claude discovery 확인(`.harness/observations.yaml` 에 기록), Codex 는 미확인(A-11).** 컴파일 직후 같은 세션에서 채택 7종이 **전부** 스킬 목록에 나타났다 — `test-driven-development`·`systematic-debugging`·`verification-before-completion`·`requesting-code-review`·`receiving-code-review`·`using-git-worktrees`·`finishing-a-development-branch` + Romeo 의 `plan`·`plan-close`. 보류·제외한 스킬(`brainstorming`·`subagent-driven-development` 등)은 목록에 **없다** — K-68 ②(자동 트리거 미발생)의 부분 증거다. **Codex 쪽 discovery 는 여전히 미확인**이고, 스킬이 목록에 뜨는 것과 규율이 실제로 지켜지는 것은 다르다 — 충돌 fixture 3종이 남았다.
- override 는 **5건**으로 늘었다(`output_paths` 는 충돌 fixture c1 이 찾아냈다). 컴파일이 두 지침 파일에 인쇄한다. 다만 **원문의 지시와 override 가 충돌할 때 에이전트가 실제로 override 를 따르는지는 여전히 미검증**이다 — fixture 는 "override 가 존재하는가" 를 검사할 뿐 "에이전트가 그것을 따르는가" 는 증명하지 못한다. 실제 T1 관통에서 관찰해야 한다.
