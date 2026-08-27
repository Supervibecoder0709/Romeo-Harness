---
id: constraints
type: requirements
status: draft
updated: 2026-08-27
authority: canonical
---

# 제약

여기 있는 항목은 선호가 아니라 **위반하면 설계가 깨지는 조건**이다.
"확인된 사실"은 원천 대화에서 공식 문서나 실물로 교차 확인된 것이고,
그렇지 않은 것은 [열린 질문](../planning/open-questions.md)의 가정으로 옮겨 두었다.

---

## 1. 런타임 제약 (확인된 사실)

| ID | 제약 | 근거 | 위반 시 |
| --- | --- | --- | --- |
| K-01 | 지원 런타임은 Claude Code CLI와 Codex CLI 둘뿐이다 | `README.md`, S01 | 범위 폭발 |
| K-02 | Codex는 subagent와 `.codex/agents/*.toml`을 지원한다. 과거의 "Codex에는 서브에이전트가 없다"는 전제는 **사실 오류**다 | S03 리뷰 #1, S04 리뷰 #1 | 불필요한 폴백·릴레이 계층 |
| K-03 | Codex 프로젝트 skill의 네이티브 위치는 `.agents/skills`다. `.codex/skills` 심링크는 불필요하다 | S04 리뷰 #2 | 스킬 발견 실패 |
| K-04 | Codex custom prompts는 deprecated이며 사용자 홈 전용이다. 프로젝트 workflow는 skill로 배포한다 | S01 KEEL 리뷰, S04 리뷰 #2 | 프로젝트 공유 실패 |
| K-05 | Codex `--json`은 최종 결과 하나가 아니라 NDJSON 이벤트 스트림이다 | S10 §5 | 결과 파싱 실패 |
| K-06 | Claude의 agent hook은 실험적이다. **핵심 상태 전이를 hook에 의존하지 않는다** | S10 §9, COUNCIL "남은 이견 3" | 상태 유실 |
| K-07 | Claude는 `CLAUDE.md`에서 `@AGENTS.md`를 import하는 방식이 심볼릭 링크보다 이식성이 좋다 | S01 KEEL 리뷰 | 새 worktree에서 깨짐 |
| K-08 | 프로젝트 trust와 개별 command-hook hash 승인은 별개다 | S04 리뷰 #3 | 훅 미실행 |

> K-02~K-05는 2026-08-05 기준 공식 문서로 확인된 내용이다. 두 CLI는 빠르게 바뀌므로
> 어댑터를 구현할 때 `doctor` 단계에서 capability probe로 재확인한다. (S02 리뷰 2)

---

## 2. Orca 경계

| ID | 제약 | 근거 |
| --- | --- | --- |
| K-10 | Orca가 Run·Task·Dispatch·worktree·메시지·DAG·결정 게이트·재시도를 소유한다. 하네스는 두 번째 스케줄러가 되지 않는다 | S01 plan, S04 리뷰 #5 |
| K-11 | 독립 작업자 간 파일은 자동 공유되지 않는다. 단계형 실행은 같은 워크트리이거나 명시적 전달이 필요하다 | `skills/repo-archive/SKILL.md` |
| K-12 | 검증되지 않은 provider model ID를 추정해 넣지 않는다. Orca는 사람이 읽는 별칭이 아니라 계정별 opaque ID를 요구한다 | `.claude/commands/repo.md` 7단계 |
| K-13 | 공개 `orca-cli/orca` 저장소는 골격만 있고 실제 사용 중인 Orca 제품과 다르다. 이 저장소를 기반으로 삼지 않는다 | `archive/orca-cli-orca`, S13 |

---

## 3. 저장·데이터 제약

| ID | 제약 | 근거 |
| --- | --- | --- |
| K-20 | v1 인프라 제로. catalog·SQLite·큐·Postgres·샤딩 없이 `rg` + 구조 검증 스크립트로 시작한다 | COUNCIL Consensus 7 |
| K-21 | 도입 트리거를 미리 명명한다. 문서 약 100개 이상 또는 저장소 횡단 조회 반복 → 인덱스. 동시 요청자 2명 이상 → 큐·DB | COUNCIL "짓지 않는 것" |
| K-22 | 순차 ID 금지. 병렬 worktree에서 충돌한다 | S01 KEEL 리뷰, COUNCIL Consensus 6 |
| K-23 | PII·인터뷰 원본·계약서·크리덴셜은 Git에 두지 않는다. 접근통제된 위치 링크, 요약, 근거 수준, 연구 ID만 남긴다 | PHD §6, COUNCIL |
| K-24 | 원시 대화·로그·임시 상태는 `.harness/runs/<run-id>/`에 두고 Git에서 제외한다 | S01 plan §4 |
| K-25 | 생성된 `.claude/`·`.codex/` 파일은 커밋한다. 새 worktree와 새 clone이 별도 설치 없이 동작해야 한다. 로컬 trust와 credential만 제외한다 | S01 KEEL 리뷰 |

---

## 4. 비용·컨텍스트 제약

| ID | 제약 | 근거 |
| --- | --- | --- |
| K-30 | 첫 병목은 처리량이 아니라 **운영자 주의력·문서 부패·컨텍스트 비용**이다 | COUNCIL "5.3 대비 달라진 것" |
| K-31 | 상위 문서 전체가 아니라 관련 노드 1-hop만 로드한다. 기준 문서에 있는 내용은 복사하지 않고 링크한다 | S10 §7 |
| K-32 | 저위험 작업은 classifier 1회 + writer 1회로 제한한다. 전문 reviewer는 hard gate나 overlay가 발동할 때만 추가한다 | S10 §7 |
| K-33 | 미확인 내용은 장문의 추측 대신 `UNKNOWN` 또는 `NEEDS_VALIDATION`으로 남긴다 | S10 §7 |

---

## 5. 라이선스·출처 제약

| ID | 제약 | 근거 |
| --- | --- | --- |
| K-40 | 참조 저장소를 통째로 포크하지 않는다. 버전 고정 + 선별 채택 | S01 plan, S13 최종 |
| K-41 | 복사한 자산은 원 라이선스 고지와 `THIRD_PARTY_NOTICES.md`를 유지하고, 공식 프로젝트로 오인시키지 않는다 | S01 plan §4, S02 리뷰 1 |
| K-42 | 라이선스 표기가 불명확한 저장소는 코드 포함을 보류한다 | S13 |
| K-43 | 현재 저장소 라이선스는 **GPL-3.0**(`LICENSE` 실물)이다. 2026-08-05 권고는 Apache-2.0이었다 | `LICENSE`, S05 |

> K-43은 미해결 충돌이다. [열린 질문 X-05](../planning/open-questions.md)와
> [결정 D-41](../decisions/decision-register.md)을 참조한다.

---

## 6. 운영 안전 제약

사용자의 상시 persona 지시문과 프로젝트 `CLAUDE.md`에서 온 것이며, 모든 워크플로우에 적용된다.

| ID | 제약 | 근거 |
| --- | --- | --- |
| K-50 | 비용 결제·권한 확대·공개 전환·삭제·소유권 이전·운영 데이터 변경은 영향 범위와 복구 방법을 먼저 설명하고 명시적 승인을 받는다 | AGENTS-P |
| K-51 | 실행 자체를 완료로 간주하지 않는다. 관찰 가능한 기준으로 검증하고 확인하지 못한 항목은 미검증으로 표기한다 | AGENTS-P, S07/S08 |
| K-52 | 확인된 사실 / 현재 가정 / 추천을 구분한다 | AGENTS-P |
| K-53 | 계획만 요청받았다면 파일을 수정하지 않는다 | `CLAUDE.md` |
| K-54 | 존재하지 않는 기능이나 도구를 가정하지 않는다 | `CLAUDE.md` |
| K-55 | 정보와 지시가 충돌하면 현재 사용자의 명시적 요청 → 승인된 현재 문서와 결정 → 프로젝트 인덱스 → 과거 대화·조사 자료 → 참고 저장소 → 일반 권고 순으로 따르고, 충돌을 임의 해석하지 않고 차이와 추천안을 알린다 | `CLAUDE.md` |

---

## 7. 부품 통합 규약 (Integration Contract)

2026-08-27 사용자 요구 "각 레포 추출물들이 충돌하지 않고 하나의 시스템에 잘 녹아드는 것"이 이 기획의 최우선 조건이다.
부품이 무엇이든(BMAD/CIS·Superpowers·OpenWiki·디자인 스킬·Orca) 부착 시 아래 열 가지를 지켜야 하며,
지킬 수 없는 부품은 `rewrite`로 강등하거나 제외한다 ([결정 D-53](../decisions/decision-register.md)).
근거는 [개정 3 기록](../reviews/2026-08-27-assembly-redefinition/summary.md)과 각 `archive/*/05-pm-harness-notes.md`다.

| ID | 규약 | 위반 시 | 근거 |
| --- | --- | --- | --- |
| K-60 | **기획 진입점 단일.** 새 요청의 *분류와 문서화*는 `/plan`(라우터)로만 들어온다. **개발 규율 부품**(TDD·디버깅·완료 검증·코드리뷰)은 구현 중 런타임이 스스로 골라 써도 된다 — 그것이 규율의 목적이다. 금지되는 것은 부품이 **라우터를 대체**하는 것이다: 자체 bootstrap, 세션 시작 주입, "모든 대화에서 나를 먼저 써라" 규칙, 기획 문서 생성, 승인 창구 이중화. (D-72 로 재정의 — 원래 문구는 부품 스킬이 런타임에 노출되는 것 자체를 금지하는 것처럼 읽혔다) | 이중 기획, 주의력 소모(K-30), 승인 우회 | superpowers `using-superpowers` "1% 규칙", `brainstorming`, BMAD 자동 인사, ui-ux-pro-max 키워드 활성화 |
| K-61 | **기획 원본 단일.** 승인된 Brief/Spec이 유일한 제품 요구 원본이다. 부품은 기획을 재생성하지 않고 누락·모순 시에만 질문한다(D-25). BMAD 산출물은 입력 링크로, superpowers `brainstorming`은 제외 | 문서 두 벌, 최종본 모호 | S12 충돌 1, S03 |
| K-62 | **산출물 흡수.** 부품 산출물은 `docs/work/<id>/`에 생성하거나 frontmatter `inputs:`/`evidence:` 링크로 등록되어야 `/plan-close`가 인정한다. 부품 기본 경로(`docs/superpowers/**`, `_bmad-output/**`, `.superpowers/**`)는 설정으로 override하거나 링크로만 참조한다 | 고아 산출물, 경로 불변(D-09) 위반 | superpowers "사용자 선호 우선", BMAD `output_folder` |
| K-63 | **상태 소유권.** 문서 상태·승인은 Romeo, 실행 상태는 Orca, 기술 문서 신선도는 OpenWiki. 부품 내부 상태(BMAD `stepsCompleted`, SDD ledger)는 참고 정보이며 완료 판정에 쓰지 않는다 | 진실이 세 곳 | D-20, D-23, K-10 |
| K-64 | **네임스페이스.** 부품 스킬은 **원본 이름을 유지**한다 — 논리 id 는 `provenance/imports.yaml` 의 `sp-*` 이고, 런타임 이름은 원문 그대로다(`verbatim` 이라 frontmatter 를 고칠 수 없다). 이름 충돌은 `doctor` 의 충돌 fixture c3 가 검출한다. Romeo 자체는 `romeo:*`를 쓴다. `AGENTS.md` managed block 마커에 소유자(`romeo:managed`, `openwiki:managed`)를 넣는다. 이름·마커 충돌은 `doctor`가 검출한다 | 스킬 오호출, 마커 덮어쓰기 | §6 충돌 5 |
| K-65 | **트리거 소유권.** 부품의 hook을 `.claude/settings.json`·`.codex/hooks.json`에 등록하지 않는다(K-06 확장). 호출 순서는 Romeo 워크플로우 본문이 정한다 | hook 의존, 상태 유실 | K-06, impeccable "hook exit 0은 증거 아님" |
| K-66 | **권한 상한.** 부품은 Romeo 역할 계약(implementer write / reviewer read-only)의 권한을 넘지 못한다. 부품이 유도하는 외부 쓰기(publish·push·PR·deploy·이미지 생성 비용)는 execution guard 대상이다 | 승인 우회 | K-50, MengTo publish guard, taste 이미지 비용 |
| K-67 | **버전 고정·출처.** 모든 부품은 SHA 또는 릴리스 태그로 고정하고 `provenance/imports.yaml`에 기록한다. 업데이트는 `/repo` 재아카이브 → diff 검토 → 채택 게이트 재통과 순이다 | 조용한 드리프트 | K-40~K-42, C-H4 |
| K-68 | **부착 검증.** 부착 완료 = `doctor` 프로브(존재·버전·양 런타임 discovery) + 충돌 fixture 3종 PASS — ① 이중 기획 미발생(T0 요청에 `/plan`만 뜸) ② 자동 트리거 미발생(부품 스킬은 라우터가 켤 때만) ③ 산출물 경로·마커 충돌 0. 파일·설정 존재만으로 완료라 하지 않는다 | "설치됐다 ≠ 동작한다" | K-51, archive `05` 노트 전부 |
| K-69 | **분리 가능.** 부품을 제거해도 Romeo 코어·문서·evidence가 깨지지 않아야 한다. 부품 세트 내부 상호참조(`superpowers:*` 간 호출)는 세트 단위로 채택한다 | 부품 종속, dangling reference | superpowers 원문 상호참조 확인 |
