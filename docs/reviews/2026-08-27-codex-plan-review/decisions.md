---
id: codex-plan-review-decisions-20260827
type: decision_register
status: active
updated: 2026-08-27
authority: canonical
---

# Codex 리뷰 검증·채택 기록 (2026-08-27)

## 리뷰 실행 사실

| 항목 | 값 |
| --- | --- |
| 리뷰어 | Codex CLI 0.147.0 · 모델 `gpt-5.6-sol`(카탈로그 priority 1) · 서비스 티어 `priority`(= "Fast", 1.5x) · reasoning `xhigh`(사용자 기본값) |
| 실행 방식 | Orca 감독 dispatch — Run `run_7865ac0ae3e3`, Task `task_115be41e66b4`, Dispatch `ctx_37fd55847fb5`, 터미널 `term_a4e5b652…` |
| worktree | `~/orca/workspaces/Romeo-Harness/codex-plan-review` (브랜치 `Supervibecoder0709/codex-plan-review`, base `Supervibecoder0709/mvp_planning` @ `324d63e`) — 정본 문서와 `CLAUDE.md`가 이 브랜치에만 있어 현재 브랜치를 base로 사용 |
| 입력 | [request.md](request.md) — `CLAUDE.md` 선독 지시 + 사용자 리뷰 프롬프트 원문 + 계획·요청 원문·브리프의 절대 경로 |
| 출력 | [review.md](review.md), [review.html](review.html) (리뷰어 worktree에서 복사, 내용 동일) |
| 소요 | dispatch 02:46:16Z → review.md 02:52Z, review.html 02:55Z (약 9분) |
| 리뷰어 측 변경 | `docs/reviews/…` 신규 2파일(untracked)뿐. tracked 파일·stash·HEAD 변경 없음 (`git status` 확인) |
| 우회한 문제 | Codex 시작 시 업데이트 프롬프트(0.147.0 → 0.149.1)로 입력이 차단됨. 업데이트는 실행하지 않고 공식 설정 키 `check_for_update_on_startup=false`를 이 실행에만 `-c`로 전달해 재기동 |

**Codex 판정:** 주요 수정 후 구현 가능 — BLOCKER 0 · MAJOR 5 · MINOR 3.

## 발견 사항별 검증과 판정

| ID | 등급 | Codex 주장 | 내가 확인한 근거 | 판정 | 반영 위치 |
| --- | --- | --- | --- | --- | --- |
| F-01 | MAJOR | M2를 "v1 유일 합격 기준"으로 부르면서 정본 v1 필수(V-2 Charter, V-8 부착 상태, V-10 shadow 20)는 M3~M5에 둬 완료 기준이 문서 안에서 충돌 | `v1-scope.md`는 "증명해야 할 최소 흐름 = 유일한 합격 기준"과 "v1에 반드시 들어가는 것 V-0~V-10"을 **둘 다** 둔다. 계획 §0·§4.1·§4.2·M2·§10이 서로 다른 완료 표현을 썼음 — 사실 | **채택** | 게이트를 둘로 분리: M2 = 핵심 동등성 게이트, v1 릴리스 게이트 = V-0~V-10(M4 끝). 최소 부착 상태 파일(V-8)은 M2로 당김. §0·§3.5·§4.1·§4.2·M2·M4·M5·§10 수정 |
| F-02 | MAJOR | M2 페이로드를 `migration` facet으로 분류했는데 gate 집행은 M3라 게이트 대상 작업을 게이트 없이 실행 | 계획 §4.1에 "facet [migration(내부 데이터)]"라고 적은 것은 사실. 다만 18개 `_source.md` 소급은 저장소 내부 문서 스키마 변경으로 정본 hard gate "데이터 마이그레이션"(운영 데이터)에 해당하지 않음 | **부분 채택** — "backfill = hard gate"라는 해석은 기각, 라벨의 모호함은 인정 | M2 페이로드를 "게이트 없는 T1"으로 명시하고 facet 라벨 제거. 게이트 발동 경로 검증은 M3 유지. 실행 가드 집행 규칙(대상·영향·백업·복구 없이는 gate 생성 불가)을 M3에 명문화 |
| F-03 | MAJOR | reviewer read-only가 런타임 강제 없이 `git status` 사후 비교에 의존 | `codex exec --help`: `-s read-only \| workspace-write \| danger-full-access` 실존. `claude --help`: `--allowedTools`·`--disallowedTools`·`--tools`·`--permission-mode` 실존. 계획 M2·§9.1이 사후 비교만 명시한 것도 사실 | **채택** | reviewer 역할 계약에 런타임 강제(Codex `-s read-only`, Claude 읽기 도구 허용 목록) 추가, `git status` 비교는 방어 검사로 강등. §4.1·§4.2·M2·§10 #8, 브리프 안전 브레이크·단계 7 |
| F-04 | MAJOR | evidence의 stale 판정이 HEAD 중심이라 작업 트리 변화를 못 묶음 | 정본 C-E2 "HEAD **또는 작업 트리**가 바뀌면 stale". 계획 §3.2에는 dirty hash가 있으나 M1 검증은 "HEAD 한 커밋 올린 뒤"만 — 사실 | **채택** | §3.5 상태 계약에 `dirty_tree_hash` 정의(tracked 수정+staged+untracked, ignored 제외, 경로·내용 해시 정렬 후 sha256)와 stale 테스트 4경우(commit/tracked/staged/untracked) 추가. M1 검증·§10 #7 수정 |
| F-05 | MAJOR | attach/update 복구가 "git 추적 → checkout"만 가정, dirty 대상·untracked·부분 실패·원자성 미정의 | 계획 M5 원문 확인 — 사실. 요청 원문도 "변경 내용과 충돌을 보여준 뒤 동기화, 전후 차이 검증, 되돌리기"를 요구 | **채택** | M5에 preflight, dry-run 기본, 충돌 파일별 승인, staging 후 원자적 교체, 성공 시에만 상태 파일 갱신, untracked 생성물 포함 백업 복원 추가. M5를 v1.1(릴리스 게이트 이후)로 표기 |
| F-06 | MINOR | M0가 수평 산출물(정책 3·스키마·템플릿 2·CLI 4·tests·provenance·NOTICE)을 먼저 만들어 "폴더 생성 = 진척" 위험 | 계획 M0 원문 확인 — 사실. provenance/NOTICE는 M0에서 채택 자산이 0건이라 빈 골격 | **채택** | provenance/NOTICE·compact-brief를 첫 소비 단계(M2)로 이동, M0는 단독 완료를 선언하지 않고 같은 fixture로 M1까지 이어져야 수직 슬라이스 1이 닫힘. §5 트리·M0·§10 #3·프롬프트 초안 수정 |
| F-07 | MINOR | M0 본문은 결정 2개만 필요하다는데 최종 프롬프트·브리프는 5개를 모두 전제 | 계획 M0 선행조건 vs §10 프롬프트 "전제" 대조 — 사실 | **채택** | M0 차단 결정은 profile 라벨·상태 모델 2개로 제한. 라이선스는 M2 첫 외부 자산 복사 전, 비코드 범위는 첫 비코드 부착 전 게이트. 미정은 `NEEDS_DECISION` 기록. §9.2·프롬프트·브리프 결정 절 수정 |
| F-08 | MINOR | `rg` 경로가 이미 바뀌어(`…/codex-path/rg`) 첫 T0의 근거가 낡음 | 재프로브: Claude 셸 `command -v rg` = `/Applications/ChatGPT.app/Contents/Resources/rg`(계획대로), Codex 셸 = Codex 패키지 `codex-path/rg`, homebrew ripgrep 미설치, CI는 검증 스크립트를 실행하지 않음. 즉 "경로가 바뀐 것"이 아니라 **셸마다 다른 앱 번들 rg**를 쓰는 것 | **부분 채택** — "관찰이 낡았다"는 기각, "고정 페이로드로 두지 말고 프로브 후 결정"은 채택 | M1 페이로드를 `.gitignore` + "재프로브 후 결정하는 두 번째 T0"로 변경. 안전 브레이크 문구를 "앱 번들 의존(두 셸 모두)"로 정정 |

기각한 해석 2건(F-02의 hard gate 해당 여부, F-08의 "낡은 관찰")은 근거를 위 표에 남겼고, 수정안 자체는 둘 다 반영했다.

## 구현 순서 검사에 대한 답

Codex의 이동 제안은 전부 위 채택 항목으로 흡수됐다: 실행 가드·read-only·dirty hash를 M2 앞/안으로, 릴리스 게이트를 M4 끝으로, provenance/NOTICE를 M2로, 상태 계약을 §3.5 한 절로, `rg` 폴백을 프로브 후보로, 최소 부착 상태 파일만 v1에 남기고 full attach/update는 v1.1로.

## 바꾸지 않은 것

Thin Policy-Compiled Planning Spine, unit/mode/facet 분리, LLM 제안·사람 확정·규칙 강제 3분할, Romeo/Orca 소유권 경계, "같은 계약·판정"으로 정의한 parity, 역할 2개와 트리거 뒤 확장 — Codex도 "변경하지 않아도 됨"으로 분류했고 정본 결정과 일치한다.

## 남은 미검증

- 리뷰어 HTML(`review.html`)의 브라우저 렌더링은 리뷰어가 file URL 정책으로 확인하지 못했다고 보고했다. 이 세션에서 로컬 서버 + Playwright(1200px)로 확인했다: 판정 카드·등급 배지 14개·요구사항 표·순서 검사 다이어그램이 렌더링되고 가로 스크롤 없음, 콘솔 오류는 로컬 서버의 favicon 404뿐 — **검증 완료**.
- 리뷰어 worktree(`codex-plan-review`)와 브랜치는 삭제하지 않았다. 필요 없으면 사용자가 정리한다(삭제는 되돌리기 어려운 작업이라 승인 대상).
