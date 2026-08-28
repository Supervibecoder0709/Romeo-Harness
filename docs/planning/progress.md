---
id: progress
type: planning
status: active
updated: 2026-08-29
authority: derived
---

# 구현 진행 상태

[구현 계획](implementation-plan.md) §10 체크리스트 기준. 완료 판정은 관찰 가능한 결과로만 한다(K-51).
정지선·결정은 [decision-register](../decisions/decision-register.md) "구현 착수 결정"(D-59~D-71).

`계획 §10` 열은 이 표의 행이 계획 §10 의 어느 번호에 대응하는지다. 두 표의 번호가 어긋나
계획의 확인 기준이 조용히 사라지는 것을 막는다(1차 리뷰 F16). `—` 는 계획 §10 에 번호가 없는 항목이다.

독립 리뷰 findings 원문은 `docs/reviews/` 에 라운드별로 보관한다 —
[1차(F01~F31)](../reviews/2026-08-28-m2-round1-review/README.md) · [2차(G01~G13)](../reviews/2026-08-28-m2-round2-review/README.md).

## 지금 상태 (기준 `8956371` · 2026-08-29)

> 이 블록은 손으로 갱신한다. 위 SHA 는 **이 요약이 서술하는 상태의 기준 커밋**이지 블록을 쓴 커밋이 아니다.
> `git log --oneline 8956371..HEAD` 가 비어 있지 않으면 그 커밋들이 아래 항목을 바꿨는지 먼저 본다 —
> 바꿨다면 블록을 믿지 말고 `gh run list --limit 1` 과 검사 재실행으로 실측하고, 이 블록을 갱신한다.

- **마일스톤:** M2 진행 중 — 교차 관통 완료, 동등성 게이트 **구현자 면 PASS · 검토자 면 비교 불가**(D-73). M3~M7 미착수.
- **CI:** 마지막 실행은 ❌ (run `33204229155`, `8749bb5` 기준 — 원인은 옛 게이트 정의). `8956371` 은 **아직 push 하지 않아
  CI 가 돌지 않았다** — 로컬에서 게이트 스텝 본문을 그대로 실행해 EXIT=0 과 `::warning::` 1줄(뺀 면 1)을 확인했다.
  push 는 승인 대상(K-66)이다.
- **로컬 검사 (2026-08-29, `8956371`):** unittest **340 OK** · `fixtures parity --report` **EXIT=0**(게이트 PASS · 검사기 PASS ·
  비교 불가 면 1) · `compile --check`·`notices --check`·`vendor check`·`doctor`·`validate` 전부 EXIT=0.
- **다음 작업 3건** (§10 체크리스트 31·32 + 새 항목):
  1. **작업 단위 `feat-20260829-license-field-46an` 완료** — spec 의 AC-1 은 값 대조를 요구하는데
     `check-2` 는 개수만 센다. 검증 계획 변경은 재승인 대상(D-27) → 재승인 후 재관통.
  2. **`AGENTS.md` 서문 비대칭 해소** — 문서 인덱스·충돌 해소 순서를 Claude 쪽만 본다(체크리스트 32).
  3. **검토자 면 동등성 관측** — 기준 실행의 산출물을 고정한 채 검토자만 교체 바인딩으로 재실행(RUNBOOK §6.6, 미실행).
     지금 PASS 는 구현자 면 위에만 서 있다.
- **문서 지연:** 「미검증·남은 위험」의 「4차 리뷰」 이하 소절은 2026-08-28 기준이다.
  8/29 관통 이후 사실이 아닌 항목이 있다(예: "게이트는 미판정", "CI 새 스텝은 한 번도 돌지 않았다"). 맨 위 소절(D-73 이후)만 최신이다.

## 마일스톤

| 마일스톤 | 상태 | 관찰 가능한 결과 | 커밋 |
| --- | --- | --- | --- |
| M0 정책표·fixture·분류 카드 | **완료** | `bin/romeo route --fixtures fixtures/requests --report` → 33/33 일치(100%), gate 누락 의심 0 · `python3 -m unittest discover -s tests` → 23 PASS · 카드 5건 ≤ 29줄 · shadow 1차 5건 사람 확정(수정 2건 반영 후 100% 유지) | `73501f8` |
| M1 T0 최소 관통 (Claude 단독, 현재 작업 공간) | **완료** | `docs/work/chg-20260827-gitignore-harness-runs-mj9p/` · `docs/work/chg-20260827-rg-fallback-validate-245m/` 각각 `spec.md`(status done) + `evidence/run-m1.yaml`(head_sha·dirty_tree_hash·commands 3건 exit 0) · `romeo close` PASS 2건 | `2260605`~`48f7298` |
| M2 어댑터·역할·Orca 위임·T1 교차 관통 | **진행 중 — 관통 완료, 게이트 구현자 면 PASS · 검토자 면 비교 불가(D-73)** | 진입 조건 3건 완료(**G-M2** D-67 · **역할 바인딩** D-68 · **LICENSE** D-41). 기반과 실행 배관이 서고 2·3차 리뷰가 그 배관의 판정을 실재에 묶은 뒤, **2026-08-29 에 RUNBOOK §3 을 실제로 두 번 관통했다** — 기준(구현자 claude · 검토자 codex)과 역할 교체(구현자 codex · 검토자 claude). 결과 계약 4개가 모두 앵커 검사를 통과했고 관측 케이스 1건이 등록돼 **`핵심 동등성 게이트: FAIL — 관측 1건으로 판정했다`(EXIT=1)** 가 나왔다 — 미판정에서 **판정으로** 바뀐 것이 이 마일스톤의 성과다. 구현자 면은 일치했고(`PASS`/`PASS` · checks 5건 동일 · 계약 바이트 동일), 검토자 면이 갈렸다(`PASS`≠`FAIL`). **그 차이의 원인은 런타임 능력이 아니라 검토 대상이 실제로 달랐던 것**이다 — codex 구현자가 `archive/README.md` 표 구분선을 5셀로 만들었고(헤더는 6열) claude 검토자가 그것을 잡았다. baseline 산출물에는 그 버그가 없어 codex 검토자의 `PASS` 도 옳다. 관통 중 RUNBOOK 결함 3건과 **코어 설계 모순 1건**을 찾아 반영했다(체크리스트 29). **2026-08-29 사용자 결정(D-73)으로 게이트 정의를 보완했다** — 검토자 면은 두 면의 산출물이 같을 때만 비교하고, 다르면 `PRODUCT_DIFFERS` 로 판정에서 빼되 '비교 불가' 로 인쇄한다. 같은 관측이 이제 `핵심 동등성 게이트: PASS — 관측 1건으로 판정했다` + `비교 불가 — 관측 케이스의 1개 면을 판정에서 뺐다` (EXIT=0) 다(체크리스트 30). **검토자 동등성은 아직 관측되지 않았다** — 같은 산출물을 두 검토자에게 보인 관측(RUNBOOK §6.6)이 필요하다. 남은 것은 작업 단위 자체의 완료다(체크리스트 31) | — |
| M3 ~ M7 | 미착수 | — | — |

## §10 체크리스트

| # | 계획 §10 | 항목 | 상태 | 근거 |
| --- | --- | --- | --- | --- |
| 1 | #1 | §9.2 결정 1~5 확정 | 완료 | D-41·D-43·D-59·D-60·D-61 accepted (`50a6026`) |
| 2 | #2 | fixture 15~20건 (사용자 3개월 요청 포함) | 완료 (33건) | `fixtures/requests/` — 세션 로그 24 · 대화 압축본 5 · 저장소 4. `bin/romeo fixtures check` PASS |
| 3 | #3 | 정책표 3종 + 스키마 + Tech Spec 템플릿 + `/plan` SKILL | 완료 | `core/policy/*.yaml`, `core/schemas/*.json`, `core/templates/tech-spec.md`, `core/workflows/plan/SKILL.md`. 리포트 100% / gate 누락 0 |
| 4 | #4 | `romeo validate`·`new`·ID + unittest | 완료 | 23 PASS. 같은 날 같은 slug 300건 생성 시 충돌 없음(`tests/test_ids_schema_frontmatter.py`) |
| 5 | #5 | `/plan --dry-run` 5건 shadow | 완료 | `fixtures/shadow/2026-08-27-cards.md` 1차 검토 결과표. 5건 모두 `human_correction` 기록(confirmed 3 · corrected 2). 수정률 2/5 = 40%, unit·gate 수정 0/5 |
| 6 | #6 | M1: T0 2건 관통 | 완료 | 위 M1 행. M0 fixture `fx-repo-gitignore`·`fx-repo-rg-fallback` 가 같은 요청이다 |
| 7 | #7 | stale 거부·미체크 AC 거부 | 완료 (테스트 기준) | `tests/test_docs_evidence_close.py`: 커밋 이동·tracked 수정·staged·untracked 4경우 FRESH_* 거부, 미체크 AC·required_check 누락·변경 없음 거부. 실제 단위에서는 evidence 없는 close 거부 1건 관찰 |
| 8 | #8b | G-M2 채택 게이트 | 완료 | 고정 SHA `b36e082` 원문 14개 스킬을 받아 상호 참조 실측 → 후보표 제시 → 사용자 확정. `provenance/imports.yaml` 15항목(accepted 8 · deferred 4 · rejected 3), D-67~D-71 |
| 9 | — | LICENSE Apache-2.0 교체 + `THIRD_PARTY_NOTICES.md` | 완료 | `LICENSE` 202줄 Apache-2.0(Copyright 2026 Supervibecoder0709). `THIRD_PARTY_NOTICES.md` 는 `bin/romeo notices` 가 imports.yaml 에서 생성 · `--check` PASS. (D-41 — 계획 §10 에는 번호가 없다) |
| 10 | #8b | `vendor/obra-superpowers@b36e082/` 원문 복사(수정 0) | 완료 | 15파일(스킬 14 + MIT 사본). `bin/romeo vendor check` → **PASS · files=15 blob SHA 일치**. 변조 검출 테스트 5경우(수정·삭제·추가·디렉터리 없음·미등록 id) |
| 11 | — | CI(python 3.11) 하네스 검사 | 완료 (그 뒤의 워크플로 변경은 **CI 에서 미실행**) | `.github/workflows/harness.yml`. GitHub Actions run `33095164296` **success 13s** — 39 tests OK, vendor PASS files=15, notices 일치. (계획 §7 요구 · §10 에는 번호가 없다) **2026-08-29 에 새 스텝이 GitHub Actions 에서 처음 돌았다**(run `33198506693`, `dc9e1e3`) — 그리고 **실패했다**. 실패한 곳은 게이트 스텝이 아니라 `unittest` 였고, 원인은 `actions/checkout@v4` 의 기본값이 **얕은 클론**(`fetch-depth: 1`)이라는 것이다. 관측 parity 케이스의 앵커 검사는 작업 계약을 `base_sha` 커밋의 spec 에서 **다시 계산해** 대조하는데(`TASK_ANCHORED`) 그 커밋이 체크아웃에 없어 봉투 4개가 전부 `base_sha 로 쓸 커밋을 찾을 수 없다` 로 `PARITY_INVALID` 가 됐다. 로컬에서는 전체 이력이 있어 통과했으므로 **CI 에서만 드러나는 종류**다. `--depth 1` 클론으로 재현해 확인하고 `fetch-depth: 0` 을 넣었다(전체 이력 클론 재검증: 구조 오류 0 · `gate_verdict FAIL` · `observed 1` · `checker PASS`). 관측 케이스를 저장소에 두는 순간 CI 가 그 커밋 이력을 필요로 한다는 것이 이 실행의 발견이다 |
| 12 | #9 | 어댑터 컴파일(`romeo compile`) | 완료 | `core/principles/AGENTS.core.md`·`.harness/bindings.yaml`·`adapters/{claude,codex}/` → 산출물(`CLAUDE.md`·`AGENTS.md` managed block, 두 런타임 스킬, `.claude/settings.json`). `compile --check` PASS. 테스트(마커 밖 보존·idempotent·심링크 대체·투영본 해시·stale 4경우) |
| 13 | — | 실행 가드 `.claude/settings.json` | 완료 | ask 8건(git push·PR·worktree 삭제·reset --hard) · deny 5건(rm -rf /·sudo rm·force push). K-66 은 "승인 없이 실행 금지"이므로 정당한 작업은 deny 가 아니라 ask 로 뒀다. 25행에서 정본을 `.harness/bindings.yaml` 로 올렸다. **파일이 있다는 것뿐이다 — 이 프롬프트가 실제로 뜨는 것은 관찰하지 않았다**(K-68) |
| 14 | #9 | `romeo doctor` 부착 검증 | 완료 | 런타임 프로브 5종(claude·codex·orca·gh·git 전부 ✓) · 스킬 파일 프로브 · 부착 상태 3종 · 충돌 fixture. **런타임 로드는 PASS 로 세지 않고 `.harness/observations.yaml` 의 관찰만 인쇄한다.** 3차 라운드에 관찰 기록을 `{observed_at, skills:[…], note}` 로 구조화하고 **실제 스킬 이름과 대조**하게 고쳤다(2차 리뷰 G09) — `./bin/romeo doctor` 는 이제 `codex 12개 · 런타임 로드 **부분 관찰** 10/12개 · 미관찰 implement · review` 를 인쇄한다(EXIT=0). 개수가 같고 이름만 달라도 잡힌다 |
| 15 | #8b | 충돌 fixture 3종 (K-68) | 완료 | `fixtures/conflicts/` — c1 외부 계획 경로·c2 자동 트리거·c3 이름/마커 충돌. **c1 이 게이트에서 놓친 실제 충돌 1건을 잡았다** (`requesting-code-review:60` → `docs/superpowers/plans/`). `overrides.output_paths` 로 흡수 후 충돌 0 |
| 16 | — | Codex 독립 리뷰 반영 | 완료 | `docs/reviews/2026-08-28-codex-m2-review/` — gpt-5.6-sol(effort max)이 반례를 실행해 Important 9 · Minor 1 보고. 8건 수정(F-01·02·04·05·06·07·09·10), fixture c4 추가, 테스트 80→95 |
| 17 | — | K-60 재정의(D-72) | 완료 | 리뷰 F-03 → 사용자 확정. 개발 규율 부품의 런타임 직접 노출을 허용하고, 금지 대상을 "라우터 대체 경로"로 좁혔다. K-64 는 논리 id(`sp-*`)와 런타임 이름(원문)을 분리 |
| 18 | — | F-08 원자적 컴파일 · F-07 upstream 대조 | 완료 | **Codex(codex-m2-review 워크트리)가 구현**. staging + `os.replace` + 예외 시 역순 롤백, settings 기대값의 순환 의존 제거, `romeo vendor verify-upstream` 신설. 테스트 95 → 107. 사람 검증: 위조(파일+manifest 동시) 시 `UPSTREAM_BLOB_MISMATCH` exit 1 · 깨진 소스 주입 시 산출물 지문 무변경 |
| 19 | **#8** | 검토자 런타임 read-only **쓰기 시도 거부 로그** | 완료 | 프로브 7건. `codex exec -s read-only` 를 임시 디렉터리와 이 저장소 두 곳에서 실행 → **생성된 파일 0건**, 로그에 `patch rejected: writing is blocked by read-only sandbox`. 교체 실행 쪽 `claude -p --tools "Read" "Grep" "Glob" --allowedTools ... --strict-mcp-config` → 사용 가능한 도구가 **`Read`·`Grep`·`Glob` 3개로 관찰**, 파일 0건. 원문 로그 [`docs/reviews/2026-08-28-m2-round1-review/`](../reviews/2026-08-28-m2-round1-review/PROBE_READONLY.md), 색인 `.harness/observations.yaml` 의 `reviewer_write_refusal`. **거부된 실행 5건이 전부 종료 코드 0 이다 — 차단 여부를 exit code 로 판정하면 안 된다.** 이 7건은 전부 **단독 프로브**였다. **2026-08-29 관통에서 §3 기동 경로의 관찰이 생겼다** — §3.7 로 띄운 검토자가 도는 동안 §4 의 방어 검사가 두 실행 모두 `유효` 를 냈다(baseline `2bc7dad48f31` · swapped `8262a4b8ad4f` — `review-tree-before` 와 `after` 의 `log_sha256` 동일). §4 표의 검토자 두 행이 `예 / 예` 로 바뀌었다. **다만 이것은 사후 확인이지 강제 그 자체가 아니다** — 쓰기를 시도했다가 막힌 것을 본 것은 단독 프로브 쪽이다. 그리고 같은 관통이 그 강제의 **한계**를 드러냈다: `-s read-only` 는 모델이 만든 셸 명령의 **쓰기**만 막고 명령 실행 자체는 막지 않는다(프로브: `shasum` 이 read-only 아래에서 `succeeded in 0ms` 로 정확한 해시를 냈다). 역할 계약의 '명령을 실행하지 않는다' 는 그 수단으로 강제되지 않고 지침으로만 존재한다 |
| 20 | #9 | 부품 부착 배선 (`.harness/romeo.project.yaml` → 라우터) | 완료 | `bin/romeo route --classification <T1> --root <이 저장소> --json` → `parts[superpowers].status = active` · `warnings []`. 부착 파일이 없는 루트에서는 `pending_gate` · `PART_PENDING_GATE` 로 되돌아간다. `python3 -m unittest tests.test_policy` PASS. fixture 리포트는 정책표 자체의 회귀 테스트라 의도적으로 배선하지 않았다(33/33 유지) |
| 21 | #10 선행 | 승인 → 실행 순서 · 위임 식별자 | 완료 | `evidence approve` 가 evidence run 없이도 **승인 전용 레코드**를 만든다(`commands: []` 가 "승인 시점 명령 0건" 의 증거가 된다). `evidence run`·`checks`·`approve` 에 `--task-id`·`--dispatch-id` 추가 — run 당 1회만 기록하고 다른 값이 오면 exit 1 로 거부. `--run` 을 오케스트레이터 Run id 로 쓰면 `evidence/`·`result/`·`task/` 의 `<run>` 이 한 값이 된다 |
| 22 | #10 선행 | 작업 계약 생성 (`romeo envelope build`) | 완료 | `bin/romeo envelope build --unit <id> --role implementer --base-sha <SHA>` → `docs/work/<id>/task/<role>.json`(git 추적 경로 · K-62). 계약은 **커밋된 spec 블롭에서만** 계산해 작업 트리를 고쳐도 바뀌지 않는다. 같은 입력 재실행 → `cmp` identical. 승인 전·커밋 전에는 exit 1 로 막고 쓸 SHA 를 알려준다(D-a). 3차 라운드 정정: 두 런타임 지침이 **계약을 손으로 쓰라**고 지시하고(G01) **생산자가 0건인 경로**를 입력으로 지목하고 있었다(G02) — 둘 다 `envelope build` 와 `docs/work/<id>/task/<run-id>-<role>.json` 으로 고쳤고 `compile --check` PASS |
| 23 | #10 선행 | 검토자 판정 → 완료 판정 연결 | 완료 (실물 봉투로는 **미검증**) | `romeo/close.py` 에 `HAS_REVIEW`·`REVIEW_ENVELOPE_VALID`·`REVIEW_VERDICT`. `gate_verdict: FAIL` 봉투·깨진 JSON·`unit_id` 불일치·`role != reviewer` 는 전부 close FAIL. **PASS 가 아닌 판정이 하나라도 남아 있으면 거부**한다(D-c). 2차 리뷰 G05 가 **손으로 쓴 PASS 봉투 하나로 close 가 통과**하는 것을 반례로 보였다(가리키는 계약도 증거 파일도 없음 · `close verdict = PASS · EXIT=0`). 3차 라운드에 앵커 검사 4개 추가 — `REVIEW_TASK_ANCHORED`(계약 실재 + sha256 일치 + 같은 unit·role) · `REVIEW_BASE_SHA`(현재 이력의 조상) · `REVIEW_EVIDENCE_ANCHORED`(증거 실재 + 이 단위 안, K-62) · `REVIEW_ROLE_CONTRACT`(`romeo/parity.py` 의 규칙 재사용). 같은 반례가 이제 `FAIL` 이고 `python3 -m unittest tests.test_docs_evidence_close` → **29 OK**. 다만 **실물 검토자 봉투로 돌려 본 적은 없다** — 저장소에 `review/` 산출물이 0건이라 격리 저장소 반례로만 검증했다 |
| 24 | #11 | 동등성 게이트 정직화 + CI 스텝 | 완료 (게이트는 **미판정**) | `source.kind ∈ {observed, authored, planned}` enum 강제, 판정을 `checker_verdict`(검사기 자기 검증)와 `gate_verdict`(관측 케이스로만 계산) 2층으로 분리. `EVIDENCE_MISSING`·`ROLE_CONTRACT_VIOLATION` 판정 불가 코드 추가. `./bin/romeo fixtures parity --report` → `핵심 동등성 게이트: 미판정 — 관측 케이스 0건` **EXIT=1**. 2차 리뷰가 이 게이트에서 **자기 신고 3건**을 잡았고 3차 라운드에 전부 실재에 묶었다 — ① `source.kind` 를 `observed` 로 한 줄만 고치면 게이트가 열리던 것을(G10) `source.ref`·`unit_id`·`evidence_ref` 실재 검사로 막았다(조작 케이스 재현: 수정 전 `게이트 PASS · EXIT=0` → 수정 후 `PARITY_INVALID · EXIT=1`), ② `checker_verdict` 를 합성 케이스만으로 계산하고 합성 0건이면 `해당 없음` 으로 인쇄한다(G12), ③ CI 스텝의 `\|\| echo` 를 걷어내고 `--json` 판정을 읽게 했다(G06) — 스텝 4상태 실측에서 **관측 불일치·위조 observed 가 EXIT=1**, 미판정만 경고로 넘어간다. 종료 코드 규약은 그대로다(PASS=0 · 그 외 1) |
| 25 | #8 | 역할 계약 투영 · 권한 상한 정본 | 완료 | `.claude/agents/{implementer,reviewer}.md` 생성(**강제 수단은 기동 플래그다** — 에이전트 파일의 `tools: Read, Grep, Glob` frontmatter 가 서브에이전트 실행에서 쓰기를 막는지는 **미관측**이다. 프로브 7건은 전부 CLI 기동 플래그를 시험했고, `.claude/agents/reviewer.md` 의 managed block 도 강제 수단으로 3플래그를 적는다) · `AGENTS.md` 에 `## 역할 계약` 절 · 두 지침 파일에 4행 역할 표(기본 2 + 교체 2, `강제 관측` 칸 포함)와 `## 권한 상한 (K-66)`. 정본은 `.harness/bindings.yaml` 의 `permission_ceiling`(approval_required 12 · never 4). `./bin/romeo compile --check` PASS. **codex 의 저장소 커밋형 에이전트 정의 형식은 미확인이라 `.codex/agents/*.toml` 을 만들지 않았다** |
| 26 | #10 | Orca 런북으로 T1 관통 (Claude 구현 / Codex 리뷰) | **완료** | Run `run_31e175742892` · Task 2건(deps 로 검토자 `pending`) · 자식 워크트리 `impl-feat-20260829-license-field-46an`(head == base_sha) · 구현자 dispatch `ctx_fb22954680e4` · evidence `run_31e175742892.yaml`(위임 식별자 3종 기록 · required_checks 5건 exit 0) · 검토자 판정 `review/run_31e175742892-reviewer.json` · `envelope check` 두 봉투 앵커 5개 전부 PASS · close 는 **`AC_ALL_CHECKED` 하나로만 FAIL**(구현자가 체크박스를 채우지 않았다) — 나머지 검사는 전부 PASS 였고 그중 `REQUIRED_CHECK_RERUN` 5건 · `EVIDENCE_LOG` 14건 · `CHECK_PLAN_COMMITTED` · `REVIEW_*` 앵커 4개가 **실물 봉투로 처음** 작동했다(체크리스트 23 의 미검증 해소) |
| 27 | #11 | 역할 교체 재현 + parity **관측** | **완료 — 게이트 판정 FAIL** | Run `run_b5cdadaffcdc` · 같은 `base_sha` · 새 워크트리 `impl2-…` · 구현자 codex(`codex -s workspace-write -a never` TUI) · 검토자 claude(3플래그). 작업 계약은 `--run` 만 다르고 **내용은 바이트까지 같다**(`cmp` identical — §6 2번의 전제 확인). `fixtures/parity/pr-license-field-t1-observed.yaml` 을 `status: executed` · `source.kind: observed` 로 채우고 봉투 4개를 파일로 지목했다(인라인 금지, D-b). `./bin/romeo fixtures parity --report` → **`핵심 동등성 게이트: FAIL — 관측 1건으로 판정했다` · `VERDICT_DIFFERS reviewer PASS≠FAIL` · EXIT=1**. 검사기 자기 검증은 PASS(합성 5건). **게이트가 미판정을 벗어나 실제 판정을 낸 첫 실행이다** |
| 28 | — | 2차 독립 리뷰 반영 (G01~G13) | 완료 | [`docs/reviews/2026-08-28-m2-round2-review/`](../reviews/2026-08-28-m2-round2-review/README.md) — 1차 반영분을 그대로 다시 리뷰에 넣어 blocker 5 · important 5 · minor 3. 13건 전부 반영하고 **수정 전에 통과하던 반례**를 회귀 테스트로 붙였다(close 11 · parity 15 · doctor 6). 각 담당의 실행 결과: `tests.test_docs_evidence_close` 29 OK · `tests.test_parity` + `tests.test_doctor` 94 OK · `tests.test_compile` 46 OK · `compile --check` PASS. 이 문서를 쓰며 직접 재확인한 것은 `./bin/romeo fixtures parity --report`(미판정 · EXIT=1)와 `./bin/romeo doctor`(codex 부분 관찰 10/12 · EXIT=0) 둘이다. findings 제안과 다르게 판단한 4건은 대조표의 "반영하지 않은 것" 에 근거와 함께 있다 |
| 29 | — | 관통이 찾은 결함 반영 (RUNBOOK 3건 + 코어 모순 1건) | 완료 | **① `--output-schema` 매핑이 실행 불가** — `core/schemas/result-envelope.json` 의 `anyOf` 가 `"schema": {}` 같은 빈 하위 스키마를 써서 codex 가 HTTP 400 으로 거부한다(`schema must have a 'type' key`). JSON Schema 로는 유효해 **검사기로는 잡히지 않고 그 CLI 를 호출해야만** 드러난다. §2 표를 "넘기지 않는다"로 고치고 형식 검증을 `envelope check` 로 일원화했다. **② §3.7 의 2단계 경로가 비대화형 실행에는 성립하지 않는다** — `codex exec` 는 `state: failed · stage: dispatch_input · last_failure: agent_prompt_stalled`, TUI(`codex -s read-only`)는 `state: ready · stage: input_accepted`. 원인은 `worker-start --terminal` 이 주입하는 task spec 을 비대화형 실행이 받을 자리가 없다는 것이고, 실제로 주입된 텍스트가 셸에 들어가 `zsh: parse error` 를 냈다. **③ §3.4 의 `--spec` 이 비대화형 검토자에게 도달하지 않는다** — DB 에만 남고 프롬프트로 가지 않아 절차 문서 지시가 워커에 닿지 않았다. **④ 코어 설계 모순** — 결과 계약 스키마는 검토자에게 `task_envelope_ref.sha256` 을 요구하는데 `core/roles/reviewer.yaml` 의 능력(`read`·`search`)에는 해시 계산 수단이 없다. 계약을 지킨 claude 검토자는 `BLOCKED_CAPABILITY` 를 냈고 그 봉투는 `TASK_ANCHORED` 에서 거부됐다. **위임한 쪽이 해시를 계산해 프롬프트에 제공**하는 방식으로 해결했다(사용자 확정) — 역할 계약도 앵커 검사도 약화되지 않는다. 네 건 모두 `adapters/orca/RUNBOOK.md` §2·§3.7·§3.8·§4·§11 에 반영했다 |
| 30 | #11 | 동등성 게이트 정의 보완 | **완료 (D-73)** | 문제는 게이트가 "런타임이 동등하지 않다" 와 "산출물이 달라서 판정이 갈렸다" 를 구분하지 못한 것이었다 — 이번 관통이 그 경우였다(codex 구현자가 `archive/README.md` 표 구분선을 5셀로 만들었고 claude 검토자가 잡았다; baseline 산출물에는 그 버그가 없어 codex 검토자의 `PASS` 도 옳다). **사용자 결정(2026-08-29): 검토자 면에 산출물 동일성을 전제로 넣는다.** `romeo/parity.py` — 판정 역할(역할 계약에 `workspace-write` 가 없는 역할)의 면은 두 면의 산출물(`head_sha`+`dirty_tree_hash`, **봉투가 지목한 증거에서 읽는다**)이 같을 때만 비교하고, 다르면 `PRODUCT_DIFFERS` 로 분리해 판정에서 빼되 `비교 불가` 로 인쇄한다. 구현자 면은 그대로다. 관측 케이스의 `expect` 는 손대지 않았다(D-b). 관측 케이스에 `product:`·`expect_incomparable:` 을 인라인으로 적으면 구조 오류, 증거에 산출물 식별이 없어도 구조 오류, 비교할 면이 하나도 없으면 미판정. 실측: `./bin/romeo fixtures parity --report` → `pr-license-field-t1-observed … ✓ 부분 … PRODUCT_DIFFERS reviewer 산출물 6e52900+7b035490df84≠6e52900+6516ae0e27d0 — 비교 불가` · `핵심 동등성 게이트: PASS — 관측 1건으로 판정했다` · `비교 불가 — 관측 케이스의 1개 면을 판정에서 뺐다(D-73) … 이 판정은 비교한 면으로만 섰다` · **EXIT=0**. 합성 케이스 2건 추가(`pr-product-differs` 산출물 다름→비교 불가 · `pr-reviewer-drift` 같은 산출물인데 갈림→`VERDICT_DIFFERS`, 전제가 핑계가 되지 않는지). `tests.test_parity` 83 → **108 OK**(관측 경로 반례는 증거 기록 명령으로 트리를 실제로 갈라 만들었다), 전체 340 OK. CI 스텝 본문 로컬 실행 EXIT=0 + `::warning::` 1줄(뺀 면 수). RUNBOOK §6·§6.6·§11.2 반영 |
| 31 | — | 작업 단위 `feat-20260829-license-field-46an` 완료 | **미착수** | 두 실행 모두 close 가 **정확히 하나의 실재하는 이유로** FAIL 한다 — baseline 은 `AC_ALL_CHECKED`(claude 구현자가 체크박스 미기입), swapped 는 `REVIEW_VERDICT`(claude 검토자가 잡은 README 표 버그 + `spec_ref.sha256` 불일치). 그리고 검토자가 baseline 1차에서 잡은 **spec 자체의 결함**이 남아 있다: AC-1 은 "18개 값이 계획 §1.3 표와 일치" 를 요구하는데 `check-2` 는 **개수만** 센다 — 어떤 required_check 도 값을 대조하지 않는다. 검증 계획 변경은 승인 대상이므로(D-27) 재승인 뒤 다시 관통해야 한다 |
| 32 | — | `AGENTS.md` 서문 비대칭 해소 | **미착수** | `CLAUDE.md` 는 마커 밖에 프로젝트 정체성·충돌 해소 순서·문서 인덱스를 두는데 `AGENTS.md` 는 managed block 으로 바로 시작한다 — **같은 안내를 Codex 세션은 보지 못한다.** 코어 규칙("공통 규칙을 특정 실행기에 종속시키지 않는다")과 어긋나고 동등성의 전제도 약해진다. 지금 고치지 않는 이유는 순서다 — Codex 런타임의 지침이 바뀌면 그 조건 위에서 관측한 `fixtures/parity/pr-license-field-t1-observed.yaml` 의 의미가 흐려진다. 체크리스트 30 을 정리한 뒤 같이 처리한다. 후보 방식 2가지: (a) 두 파일의 마커 밖에 같은 서문을 손으로 유지 — 어긋나도 검사하는 게이트가 없다, (b) 인덱스를 `core/` 아래 한 파일에 두고 compile 이 두 지침 파일에 함께 투영 — 원본이 하나가 되지만 컴파일 대상이 는다 |

## 세션 기록

- **2026-08-29 (게이트 정의 보완 — D-73)** — 8/29 관통이 남긴 `핵심 동등성 게이트: FAIL` 은 검사기의 버그도 런타임의 차이도 아니었다. 두 구현자가 **다른 산출물**을 만들었고 두 검토자는 각자 본 것을 옳게 판정했는데, 게이트가 검토자 판정을 산출물과 떼어 놓고 비교하고 있었다. 사용자가 세 선택지 중 **"검토자 면에 산출물 동일성을 전제로 넣는다"** 를 확정했다(D-73). 구현의 기준은 3차 라운드와 같다 — *빼는 근거도 실재에 묶는다.* 산출물 식별은 케이스 파일이 아니라 봉투가 지목한 증거의 `head_sha`·`dirty_tree_hash` 에서 읽고, 관측 케이스에 그것을 손으로 적는 길은 구조 오류로 막았다. 뺐다는 사실은 표(`✓ 부분`)·게이트 줄 다음 문장·JSON(`observed_incomparable_faces`)·CI `::warning::` 네 곳에 인쇄된다. **다음 세션이 기억할 것:** 이 PASS 는 구현자 면 위에만 서 있다. 검토자 동등성을 말하려면 **같은 산출물을 두 검토자에게** 보이는 관측(RUNBOOK §6.6)이 따로 있어야 하고, 그 절차는 아직 한 번도 실행되지 않았다.
- **2026-08-28 (2차 리뷰 + 3차 반영 — 1차 반영분을 다시 리뷰에 넣었다)** — 1차 리뷰를 반영한 결과물을 그대로 다시 독립 리뷰에 넣어 **blocker 5 · important 5 · minor 3**([findings 전문](../reviews/2026-08-28-m2-round2-review/REVIEW_FINDINGS.md) · [반영 대조표](../reviews/2026-08-28-m2-round2-review/README.md))을 받았다. 대상 파일은 제각각인데 결함의 형태가 하나였다 — **판정이 검사되지 않는 자기 신고 위에 서 있었다.** 손으로 쓴 PASS 봉투 하나가 close 를 통과했고(가리키는 계약도 증거 파일도 존재하지 않았다, G05), `source.kind` 를 `authored` → `observed` 로 고친 **한 단어**가 동등성 게이트를 열었으며(G10), 관찰 텍스트가 **존재한다는 것**만으로 doctor 가 12개 전부에 "런타임 로드 관찰됨" 을 인쇄했고(G09), 어댑터 지침이 지목한 계약 경로에는 파일을 쓰는 코드가 **0건**이었으며(G02), 승인 커밋에는 워커가 실행할 하네스가 들어 있지 않았고(G03), CI 게이트 스텝은 `|| echo` 로 끝나 **어떤 판정이 나와도 초록불**이었다(G06). 1차 라운드에서 배운 것이 "파일이 있다 = 됐다 로 읽지 마라" 였다면, 2차가 잡은 것은 그 한 층 아래다 — **검사를 붙였는데 그 검사가 자기 신고 문자열을 읽고 있었다.** 3차 반영의 기준은 그래서 하나였다: *모든 판정을 실재하는 것에 묶는다.* 문자열이 아니라 파일의 실재·sha256 일치·이름 대조·기계 판독 출력으로 판정하게 고쳤고, 각 수정에는 **수정 전에 통과하던 반례**를 회귀 테스트로 붙였다(close 반례 11 · parity 반례 15 · doctor 반례 6). 그 결과 게이트는 더 자주 빨간불이 된다 — 관측 불일치와 위조 observed 가 CI 를 실패시키고, `fixtures parity` 는 여전히 EXIT=1(미판정)이다. **다음 세션이 기억할 것:** 새 검사를 붙였으면 "이 검사를 통과시키는 가장 싼 방법이 무엇인가" 를 먼저 묻고, 그 답이 *손으로 문자열 하나 쓰기* 라면 그것은 검사가 아니다. 그리고 이 라운드가 만든 것은 강제이지 **관측이 아니다** — 실제 T1 관통·역할 교체·위임 기동 경로는 여전히 한 번도 실행되지 않았다.
- **2026-08-28 (M2 실행 검증 배치 + 1차 리뷰 반영)** — 역할 실행·작업 계약·Orca 위임·동등성 게이트를 병렬로 만들고, 만든 직후 독립 리뷰를 받아 **blocker 6 · important 15 · minor 10**([findings 전문](../reviews/2026-08-28-m2-round1-review/REVIEW_FINDINGS.md))을 반영했다. 리뷰가 잡은 것 중 가장 큰 것 셋은 **모두 "검사가 PASS 인데 실제로는 닫히지 않은 회로"** 였다 — ① `.harness/romeo.project.yaml` 을 읽는 코드가 없어 라우터가 부품을 계속 `pending_gate` 로 돌려주고 있었고(F01·F03·F07), ② `핵심 동등성 게이트: PASS` 가 **손으로 쓴 합성 케이스 5건**만으로 계산되고 있었으며(F05·F21), ③ 검토자가 낸 `gate_verdict: FAIL` 이 완료 판정에 전혀 연결되지 않아 빈 파일 한 개와 구별되지 않았다(F20). 셋 다 "파일이 있다 = 됐다" 로 읽히던 자리다(K-51·K-68). 이번 라운드에 게이트를 정직하게 만든 결과 `fixtures parity` 는 이제 **exit 1(미판정)** 이다 — 통과가 아니라 판정 불가가 정확한 상태이기 때문이다. 같은 라운드에서 계획 §10 #8 의 마지막 확인 기준인 **검토자 쓰기 시도 거부**를 처음으로 실행해 관찰했다(체크리스트 19). 여전히 미검증인 것은 **실제 T1 관통·Orca 위임**과 **역할 교체 관측**, 그리고 **새 스킬 2종의 한쪽 런타임 로드**다.
- **2026-08-28 (리뷰 잔여 구현 — Codex 위임)** — F-08·F-07 을 리뷰어였던 Codex 세션에 그대로 맡겼다. 지적한 사람이 고치게 하니 맥락 전달 비용이 없었다. 결과를 맹목 수용하지 않고 반례 3종을 직접 재현해 확인했다 — 위조 탐지·settings 오탐 없음·실패 시 쓰기 0건. 기존 95개 테스트는 한 줄도 고쳐지지 않았다.
- **2026-08-28 (doctor·충돌 fixture·독립 리뷰 세션)** — `romeo doctor` 와 충돌 fixture 를 만들었고, c1 이 게이트에서 놓친 K-62 충돌을 즉시 잡았다. 별도 워크트리에서 Codex(gpt-5.6-sol, effort max)에게 독립 리뷰를 맡겨 Important 9건을 받았고, 검증 후 8건을 고쳤다 — 그중 F-05(문서의 명령이 실제로 실행 불가)는 모든 검사가 PASS 인데도 수직 흐름이 닫히지 않던 상태였다. 같은 세션에서 Codex 의 스킬 목록을 받아 A-11 을 해소했다.
- **2026-08-28 (어댑터 세션)** — `romeo compile` 을 만들어 코어 → 두 런타임 산출물 경로를 세웠다. TDD 로 계약을 먼저 고정했고, 그 과정에서 실제 버그 2건을 잡았다 — 디렉터리 심링크에 `rmtree` 가 실패하는 문제와, `--check` 가 디렉터리 심링크를 PASS 로 통과시키던 문제. 실행 가드는 계획의 deny 대신 **ask/deny 분리**로 넣었다(K-66 은 금지가 아니라 승인 요구다). 테스트 39 → 63. **컴파일 직후 같은 세션에서 채택 7종이 전부 Claude 스킬 목록에 나타나는 것을 관찰**했다(A-11 Claude 쪽).
- **2026-08-28 (vendor 복사 세션)** — LICENSE 를 Apache-2.0 으로 교체하고 `vendor/obra-superpowers@b36e082/` 에 15파일(스킬 7종 14파일 + MIT 사본)을 원문 복사했다(blob SHA 15/15 일치). `romeo vendor`·`romeo notices` 를 추가해 수정 0 대조와 고지 생성을 자동화하고, CI 워크플로 `harness.yml` 로 강제했다. 검사기가 `core/workflows/plan/SKILL.md` 의 미등록 출처(anthropics/skills SKILL.md 형식)를 잡아내 `imports.yaml` 에 기록했다. 테스트 23 → 39. CI(python 3.11) 첫 실행 success(run `33095164296`).
- **2026-08-27 (M2 진입 · G-M2 게이트 세션)** — 후보 14종의 상호 참조를 고정 SHA 원문에서 실측해, 채택 7종의 나가는 참조가 세트 안에서 전부 닫힘을 확인했다. 오케스트레이션 4종은 Romeo 라우터·Orca 와 같은 자리를 차지해 보류(D-67). 계획 §6 의 "본문 도구명 0건" 이 사실 오류임을 발견해 정정했다(D-71 — 6개 스킬에 도구명 존재). `writing-plans` 의 두 규율을 Tech Spec 템플릿에 흡수(D-69), OpenWiki 선행 조건 추가(D-70).
- **2026-08-27 (shadow 1차 검토 세션)** — 카드 5건 사람 확정. `mode` 와 `uncertainty` 각 1건 수정 → fixture 5건에 `human_correction` 기록, 정책표 리포트 33/33 유지. M0 체크리스트 전항목 완료.
- **2026-08-27 (M0+M1 착수 세션)** — 사용자 결정 8건 수렴 → M0 빌드 → fixture 확정(24건) → M1 T0 2건 승인·관통. Claude Code 가 `.claude/skills/plan`·`plan-close` 를 스킬로 discovery 하는 것을 세션에서 관찰(K-68 Claude 쪽). Codex discovery 는 미확인.

## 미검증·남은 위험

이 절의 항목은 **완료가 아니다.** 검사가 PASS 라는 것과 그 회로가 실제로 닫혔다는 것은 다르다(K-51).

### 2026-08-29 게이트 정의 보완(D-73) 이후 남은 것

- **검토자 면의 동등성은 미관측이다.** 게이트 PASS 는 구현자 면(계약 바이트 동일 · checks 5건 동일 · `PASS`/`PASS`)으로만 섰고,
  검토자 면은 `PRODUCT_DIFFERS` 로 판정에서 뺐다. 검토자 동등성을 관측하려면 기준 실행의 산출물을 고정한 채 **검토자만** 교체
  바인딩으로 다시 띄워야 한다(RUNBOOK §6.6). 그 절차는 명령형만 적혀 있고 실행된 적이 없다.
- **산출물 식별의 앵커는 증거 YAML 뿐이다 — 증거 자체의 위조는 이 게이트가 잡지 못한다.** 검사기는 검토자 봉투가 지목한 증거의
  `head_sha`·`dirty_tree_hash` 를 읽을 뿐, 그 값이 실제 트리와 맞는지는 그 실행이 벌어진 체크아웃의 `romeo close`(`FRESH_TREE`)만 대조한다.
  모아 온 체크아웃에서 evidence 의 `dirty_tree_hash` 를 손으로 바꿔 두 면을 **다르게** 만들면 갈린 검토자 면이 '비교 불가' 로 빠진다 —
  4차 리뷰 구멍 B("증거 파일 자체에는 앵커가 없다")와 같은 자리이고, 이 변경이 그 구멍을 넓히지는 않지만 좁히지도 않는다.
- **검토자가 다른 run 의 증거를 지목해도 대조하지 않는다.** 봉투의 `task_envelope_ref` 경로와 `evidence_ref` 경로가 같은 `<run-id>` 인지
  검사기는 보지 않는다(RUNBOOK §3.0 의 규약이지 앵커가 아니다). 두 검토자가 같은 증거를 지목하면 산출물이 같다고 읽는다 —
  그 경우 검토자 면은 **비교되므로** 게이트를 열 수는 없고(갈리면 FAIL), 빠지지도 않는다.

### 4차 리뷰 — 위조 시도 2종이 **뚫렸다** (가장 급한 것)

4차 라운드에서 위조 시도 6종 중 **4종은 막혔고 2종은 게이트를 열었다.** 막힌 것: 손으로 쓴 4필드 계약,
스키마를 전부 채운 계약, 승인 이전 커밋을 가리킨 계약, 직렬화만 다른 계약, 판정 대상 문서를 증거로 지목.
재계산 대조(커밋된 원본 → 바이트)가 각각 다른 문구로 잡아낸다. 그러나 **위조가 한 겹 옆으로 옮겨갔다.**

- **동등성 게이트가 교차 실행 0회로 열린다.** 결과 계약(`docs/work/<id>/result/<run>-implementer.json`)을
  **손으로 타이핑**하되 `romeo envelope build` 가 만든 진짜 작업 계약과 `romeo evidence run` 이 만든 진짜 증거를
  가리키게 하면, `envelope_checks` 다섯 검사가 전부 `[PASS]` 이고 `fixtures parity` 가
  「핵심 동등성 게이트: PASS — 관측 1건으로 판정했다」 **EXIT=0** 을 낸다. 합성 1건만 곁들이면 J08 도 통과한다.
  그 봉투에 **실행된 적 없는 검사**(`pytest -q tests/`·`npm run build`, exit_code 0)를 적어도 아무도 반박하지 않는다.
  원인: `romeo/parity.py` 의 `_resolve_face` 가 태우는 다섯 검사에 **「봉투의 `checks` 가 `evidence_ref` 가 가리킨
  증거의 `commands` 와 같은가」가 없다.** 앵커는 *파일이 진짜인지*만 보고 *봉투의 주장이 그 파일과 맞는지*는 보지 않는다.
  (같은 이유로 진짜 계약을 다른 이름으로 복사해 가리켜도 PASS 다 — 앵커가 파일명이 아니라 바이트에 묶여 있다.)
- **증거 파일 자체에는 앵커가 없다.** 1~4차의 재귀는 「계약 → 봉투 → 케이스」 축만 따라갔는데, close 의 완료 판정은
  그 축이 아니라 evidence YAML 을 직접 읽는다(`romeo/close.py` 의 `cmds = {c["command"]: c for c in ev["commands"]}`).
  `required_checks` 의 명령이 `false`(exit 1)인 단위에서 evidence YAML 의 `exit_code: 1` 을 손으로 `0` 으로 고치자
  close 가 **전 항목 PASS · EXIT=0** 으로 뒤집혔다. 원시 로그(`.harness/runs/<id>/<run>/*.log`)에는 종료 코드가
  기록되지 않고, `romeo/evidence.py` 가 쓰는 `log_sha256` 을 **읽는 코드는 저장소에 하나도 없다**(grep 확인).
  작업 계약에 걸린 재계산 대조에 대응하는 것이 증거 쪽에는 없다.

**이것이 T1 순서에 걸린다.** T1 의 목적은 믿을 수 있는 첫 관측 케이스를 만드는 것인데, 지금은 손으로 타이핑한
봉투가 똑같은 PASS 를 낸다 — 그래서 지금 T1 을 돌려 얻는 PASS 는 교차 실행을 증명하지 못한다.

- **RUNBOOK §3 에 끊긴 자리 3건 — 단계는 채웠고, 실행은 여전히 미관측이다.** 무엇이 끊겨 있었나:
  (a) §3.4 가 `--spec` 에 넣으라는 `--dispatch-id` 는 §3.5 의 반환값이라 그 시점에 존재하지 않고, 돌고 있는 워커에게
  전달하는 단계가 없었다(검사하는 게이트도 없어 조용히 빴다).
  (b) §6 의 "결과 계약 4개를 짝지어 비교한다" 를 실행할 수 없었다 — 4개는 서로 다른 두 자식 워크트리에 있고
  §3.9 가 워커를 해제하는데, 한 체크아웃으로 모으는 단계도 관측 케이스 YAML 을 등록하는 단계도 없었다.
  **게이트가 계속 '미판정' 인 구조적 이유가 여기였다.** (c) §3.8 은 close 가 "그 체크아웃에서 돈다" 고 전제하지만
  §3 어디에도 close 를 실행하는 명령 블록·성공 신호·`--root` 지정이 없었다.
  → 채운 것: (a) §3.4 가 "이 시점에 아는 식별자는 `<run-id>`·`<task-id>` 둘뿐" 을 명시하고, 새 **§3.5.2** 가
  `orca orchestration send --to dispatch:<id>` 로 전달하며(워커 쪽 자가 조회는 `dispatch-show --task`),
  §3.8 의 **식별자 검사**가 증거의 `task_id`·`dispatch_id` 를 대조해 게이트가 된다.
  (b) **§6.3 모으기 → §6.4 등록 → §6.5 판정** — 결과 계약·증거를 `fixtures/parity/` 가 있는 체크아웃으로 모으고,
  작업 계약은 복사하지 않고 거기서 다시 만들고, `envelope check` 로 앵커 4개를 먼저 확인한 뒤
  자리표 케이스를 `status: executed`·`source.kind: observed` 로 채운다.
  (c) §3.8 에 `close --unit <id> --root "$W"` 블록·성공 신호·재실행 대조 조건 3개, §3.9 에 순서(해제 전에 close).
  **채운 것은 실행 가능한 단계와 성공 신호이지 관측이 아니다** — 세 자리 모두 `--help` 와 저장소 코드로만 대조했고
  상태를 바꾸는 명령은 실행하지 않았다(RUNBOOK §11 에 미검증으로 기록).

### 위협 모델 — 무엇을 막고, 무엇을 막지 못하는가 (다음 세션이 방향을 잘못 잡지 않게)

4차 라운드의 결론은 "해시 사슬이 한 겹 부족했다" 가 아니다. **이 하네스가 무엇을 막는 물건인지** 를 여기 적어 둔다.
이 절이 없으면 다음 세션은 뚫린 자리마다 해시를 하나씩 더 거는 방향으로 간다 — 그 방향에는 종점이 없다.

**막는 것 — 부주의·표류·게으른 조작.** 세 가지다.
① 실행하지 않은 것을 완료로 기록하는 것(증거 없이 done, 손으로 쓴 검사 결과),
② 기록이 실행과 어긋나는 것(다른 리비전의 증거, 다른 위임의 식별자, 낡은 계약),
③ 주장이 산출물과 맞지 않는 것(가리킨 계약이 재계산과 다름, 지목한 증거가 그 작업 단위 밖, 통과 주장인데 실행 0건).
셋 다 **한 곳만 고쳐서는 통과하지 못하게** 만드는 방식으로 막는다 — 봉투와 계약과 증거와 커밋이 서로를 가리키므로,
한 군데를 고치면 다른 곳이 어긋난다. 이것이 4차 라운드에서 위조 시도 6종 중 4종이 막힌 이유다.

**막지 못하는 것 — 일관된 로컬 위조.** 그 기계를 쓰는 사람은 증거 YAML 을 고치고, 원시 로그를 고치고,
해시를 다시 계산하고, 봉투를 그에 맞게 다시 쓸 수 있다. **로컬 파일은 로컬 행위자에게서 지킬 수 없다.**
이것은 고쳐야 할 결함이 아니라 **경계**다. 해시를 한 겹 더 거는 것은 위조 비용을 올릴 뿐 이 경계를 옮기지 못한다 —
새 해시도 같은 사람이 다시 계산할 수 있는 로컬 파일이기 때문이다. 4차에서 뚫린 2종이 정확히 이 경계 안에 있다:
손으로 타이핑한 결과 계약, 손으로 고친 `exit_code`. 사슬을 길게 만드는 대응은 같은 자리에서 다시 뚫린다.

**그래서 무엇에 의존하는가 — 둘뿐이다.**
① **재실행 대조.** 기록은 고칠 수 있어도 명령을 다시 돌린 결과는 고칠 수 없다. 완료 판정의 종점은 여기다 —
   하네스 자신의 규칙이 이미 그렇게 적혀 있다(`core/principles/AGENTS.core.md` §4: 주장에 맞는 명령을 **새로 실행하고**
   그 출력·종료 코드를 기록한다). 4차 라운드 이전의 close 는 그것을 하지 않고 기록을 읽기만 했다.
   이번 라운드에 `REQUIRED_CHECK_RERUN`(재실행 대조) · `CHECK_PLAN_COMMITTED`(계획이 커밋된 것과 같은가) ·
   `EVIDENCE_LOG`(기록이 원시 로그·`log_sha256` 과 맞는가)가 붙었다. **붙었다는 것과 위임 실행에서 닫혔다는 것은 다르다** —
   자식 워크트리에서 close 를 돌려 본 적은 아직 없다(RUNBOOK §11).
② **두 런타임이 서로의 산출물을 검토하는 구조.** 한 실행이 자기 산출물로 자기를 증명하지 못하게 하는 장치다.
   동등성 게이트는 "같은 판정이 났는가" 를 보고, 종료 검사는 "그 판정이 실재를 가리키는가" 를 본다 —
   둘은 서로를 대신하지 않는다. **같은 거짓을 두 번 적으면 양면이 같아지므로, 동등성만으로는 참이 되지 않는다.**

**재실행으로 확인할 수 없는 것은 막지 말고 드러낸다.** 부작용이 있어 두 번 돌릴 수 없는 명령, 돌릴 때마다 결과가
달라지는 명령, 상한 시간 안에 끝나지 않는 명령은 재실행 대조가 성립하지 않는다. 그런 검사는 검증 계획에서
`rerun: false` 와 이유로 선언하고, 종료 검사는 그것을 `재실행으로 확인되지 않았다 (rerun: false — <이유>)` 로
**미검증** 인쇄한다. 통과로 세지 않으므로 완료는 서지 않는다. 이것이 실행을 금지하는 것보다도, 기록을 믿는 것보다도 낫다 —
미검증은 완료가 아니지만 거짓도 아니다(K-51).

**이 절이 금지하는 방향.** 다음 라운드에서 "해시를 하나 더 걸면 닫힌다"·"봉투에 서명을 붙이면 된다"·
"로그를 append-only 로 만들면 된다" 는 제안이 나오면, 그 제안이 **로컬 행위자를 위협 모델에 넣고 있는지** 먼저 묻는다.
넣고 있다면 그 제안은 로컬 파일로 로컬 행위자를 막으려는 것이므로 성립하지 않는다.
넣고 있지 않다면(부주의·표류를 막으려는 것이면) 유효할 수 있다 — 그때는 무엇을 막는지 이 절의 세 항목으로 말한다.

### 이번 라운드에 남은 것 (1~3차 리뷰 반영 후)

- **실제 T1 관통과 Orca 위임은 한 번도 실행하지 않았다.** 이번 라운드에 만든 것은 **배관**이고, 2·3차 라운드에 한 것은 그 배관의 **판정을 실재에 묶은 것**이다 — 둘 다 관통이 아니다. 작업 계약 생성·위임 식별자·검토자 판정 연결은 CLI 와 단위 테스트 수준에서만 확인했다. worktree 격리, 두 런타임 교차 실행, Run·Task·dispatch 의 실제 발급은 관찰되지 않았다(체크리스트 26).
- **위임 명령의 반환 JSON 구조는 미확인이다 — 첫 실행에서 확인해야 한다.** `run-create`·`task-create`·`worker-start`·`check --wait`·`worker-release`·`terminal create` 의 필드 이름은 각 명령의 `--help` 와 Notes 에서만 읽었다. 상태를 바꾸는 명령이라 실행하지 않았다. 특히 **`terminal create --json` 의 어느 필드가 터미널 핸들인지 모른다** — RUNBOOK §3.7 (1) 에 확인 절차 (a)(b)(c) 를 적어 두었고, 확인 전에는 (2) 로 넘어가지 않는다. 실측한 JSON 은 `orca status --json`·`orca worktree current --json`·`orca orchestration run-current --json` 셋뿐이다.
- **핵심 동등성 게이트는 미판정이다 — 관측 케이스 0건.** `./bin/romeo fixtures parity --report` 는 EXIT=1 이고 마지막 줄이 `핵심 동등성 게이트: 미판정` 이다. 합성 5건은 검사기가 옳게 판정한다는 증거일 뿐 역할을 바꿔도 같은 판정이 난다는 증거가 아니다(D-b). 3차 라운드에 `observed` 선언의 실재 검사를 붙였지만 **그것은 "관측이라고 선언하면 관측물이 있어야 한다" 를 강제한 것이지 관측을 만든 것이 아니다.** **계획 §10 #11 의 확인 기준(`romeo fixtures parity --report` "동일")은 지금 충족되지 않으며, 계획 문서가 이 변경을 아직 반영하지 않았다.**
- **새 스킬 `implement`·`review` 는 검토자 런타임에서 로드가 관찰된 적이 없다.** Claude 쪽은 이 저장소를 작업 공간으로 띄운 세션의 스킬 목록에서 11개 이름을 전부 확인했다. **Codex 쪽은 10개 시점의 관찰만 있고 새 2종은 미관찰이다**(`.harness/observations.yaml`). 3차 라운드에 doctor 가 관찰 기록의 `skills:` 와 실제 이름을 대조하게 고쳐 이제 `부분 관찰 10/12개 · 미관찰 implement · review` 로 인쇄한다(2차 리뷰 G09) — **인쇄가 정직해졌을 뿐 관찰이 생긴 것은 아니다.** 관찰하면 `.harness/observations.yaml` 의 `runtime_load.codex.skills` 에 두 이름을 넣는 것으로 끝나고, 그때 기대값을 갱신하라고 테스트가 알려준다.
- **검토자 판정 → 완료 판정 연결은 실물 봉투로 검증되지 않았다.** 3차 라운드의 앵커 검사 4개는 격리 저장소 반례로만 확인했다 — 저장소에 실물 `review/` 봉투가 0건이라 실제 작업 단위로 `bin/romeo close` 를 돌려 보지 못했다. 또 `docs/work/<id>/result/` 의 **구현자 결과 계약은 여전히 아무도 검증하지 않는다**(그 경로에 파일을 쓰는 코드가 저장소에 없어 차단 검사로 넣지 않았다).
- **CI 워크플로의 새 스텝은 GitHub Actions 에서 한 번도 돌지 않았다.** 3차 라운드의 4상태 실측(미판정·관측 일치·관측 불일치·위조 observed)은 YAML 에서 `run:` 을 추출해 로컬에서 돌린 것이다. `$RUNNER_TEMP` 분기, 러너의 python 3.11, 스텝 순서는 실제 실행으로 확인해야 한다.
- **검토자 방어 검사(`git status --porcelain` 실행 전후 동일)는 아직 유효하게 관찰되지 않았다.** 프로브 중 같은 작업 트리를 다른 에이전트와 관찰자 자신이 편집하고 있어 diff 가 1줄 늘었다 — 검토자가 만든 변경이 아니다. 이 검사는 **트리를 아무도 건드리지 않는 조건**에서만 판정에 쓸 수 있다.
- **구현자 역할의 승인 프롬프트가 실제로 뜨는지 관찰되지 않았다.** 구현자 쪽 권한 상한은 두 런타임이 비대칭이고 어느 쪽도 실행으로 관찰되지 않았다 — Claude 쪽 `.claude/settings.json` 의 ask/deny 프롬프트가 실제로 뜨는지 미관측이고(설정 파일이 존재하는 것은 강제가 작동한다는 증거가 아니다, K-68), Codex 쪽 비대화형 실행에는 승인 정책 플래그 자체가 없어 승인 게이트를 하네스가 소유한다. RUNBOOK §4 표의 구현자 두 행은 `단독 프로브`·`§3 기동 경로` 두 칸이 모두 **아니오**다. 동등성 판정은 지금 이 비대칭 위에서 돈다.
- **검토자 강제 수단으로 에이전트 파일 frontmatter 가 작동하는지는 미관측이다**(2차 리뷰 G11). `.claude/agents/reviewer.md` 의 `tools: Read, Grep, Glob` 이 서브에이전트 실행에서 실제로 쓰기를 막는지 시험한 적이 없다 — 관찰된 것은 전부 **기동 플래그**(`codex exec -s read-only` · `claude -p` 3플래그)이고, `.harness/bindings.yaml` 과 컴파일 산출물도 강제 수단으로 그 플래그를 적는다. 두 메커니즘을 하나로 합쳐 읽지 않는다.
- **codex 의 저장소 커밋형 에이전트 정의 형식은 미확인이다.** 설치 실행 파일(0.147.0)에 `.codex/agents` 문자열이 0건이라 `.codex/agents/*.toml` 을 만들지 않았다. 계획 §5.1·§5.2 는 이 산출물을 여전히 요구하고 있고, 하지 않기로 한 근거가 `decision-register.md` 에 아직 기록되지 않았다.
- **`adapters/orca/RUNBOOK.md` 는 어떤 게이트도 검사하지 않는다.** 3차 라운드에 CLI 변경(`--task-id`·`--dispatch-id`·`--run` = Run id·D-a 의 `--base-sha`)과 2차 리뷰 G02·G03·G04·G07 을 반영했지만, 이 문서는 컴파일 대상이 아니어서(`adapters/orca/` 에 `adapter.yaml` 이 없다) **문서의 명령형이 실제 CLI 와 맞는지 확인하는 검사가 없다.** G02 가 통과했던 이유와 같은 구조다 — 다시 어긋나도 `compile --check` 는 PASS 를 낸다. 재발 방지 후보는 "어댑터 문서가 지목한 계약 경로 = `romeo/envelope.py` 가 쓰는 경로" 단언을 `tests/test_doc_commands.py` 에 붙이는 것이다(미구현).
- **`romeo/fixtures.py`·`romeo/validate.py` 의 `route()` 호출 2곳은 부착 상태를 읽지 않는다.** 의도한 것이다(fixture 리포트는 정책표의 회귀 테스트라 로컬 부착 파일에 흔들리면 안 된다). 다만 "라우터 출력" 이 호출 지점마다 다르다는 사실은 문서에 없다.

### 이전 라운드에서 이어지는 것

- **A-13 첫 측정 완료(5/20건)** — 카드 단위 수정률 2/5 = 40%. unit 0/5 · hard gate 0/5 수정(둘 다 정확), mode 1건·2질문 1건 수정. 실패 지점은 정책표가 아니라 **요청 원문 → 분류축 매핑**이었고, 두 건 다 요청에 섞인 조사·판단 단계를 놓쳐 깊이를 낮게 잡은 유형이다. 표본 5건은 아직 작다 — V-10 목표 20건까지 15건 남았다.
- hard gate 8 중 fixture 가 있는 게이트는 privacy-security·migration·availability 3종. 나머지 5종(payment·legal·ops-data-deletion·public-api·irreversible-policy)은 실제 요청이 없어 M3 조건("게이트별 fixture ≥ 1")이 아직 미충족.
- ~~`romeo` 는 Python 3.9 로만 검증했다~~ → 해소. 로컬 Python 3.9 와 CI Python 3.11 양쪽에서 39 tests PASS(run `33095164296`).
- ~~`.agents/skills` 투영·Codex discovery(A-11)~~ → 해소(아래). **Orca dispatch(A-06)는 여전히 미실측**이다.
- **A-11 부분 해소 — 두 런타임 모두 discovery 확인, 단 새 스킬 2종은 예외.** Claude 는 컴파일 직후 같은 세션에서, Codex 는 별도 워크트리의 독립 세션에서 스킬 목록이 관찰됐고 `romeo doctor` 가 센 목록과 이름이 일치했다. 보류·제외한 스킬은 어느 쪽에도 나타나지 않았다(K-68 ② 부분 증거). 증거는 `.harness/observations.yaml` 과 `docs/reviews/2026-08-28-codex-m2-review/SKILLS_SEEN.md`. **남은 것은 "목록에 뜬다" 가 아니라 "규율이 실제로 지켜지는가" 다.**
- override 는 **8건**이다(`output_paths` 는 fixture c1 이, `reviewer_workspace`·`external_writes`·`destructive_tdd` 는 Codex 리뷰가 찾아냈다). **원문의 지시와 override 가 충돌할 때 에이전트가 실제로 override 를 따르는지는 여전히 미검증**이다 — fixture 는 "override 가 존재하는가" 만 검사한다. 실제 T1 관통에서 관찰해야 한다.
- **crash recovery 미검증** — 개별 파일 교체는 원자적이고 예외 시 롤백하지만, 프로세스 강제 종료·전원 손실처럼 롤백 코드 자체가 실행되지 않는 경우는 미검증이다. 여러 파일 전체를 하나의 OS 트랜잭션으로 만들지는 않았다. `verify-upstream` 의 rate limit·네트워크 단절 분기는 고정 실패 주입으로만 검증했고 실제로 발생시키지는 않았다.
