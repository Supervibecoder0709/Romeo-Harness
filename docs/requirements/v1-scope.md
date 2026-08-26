---
id: v1-scope
type: requirements
status: draft
updated: 2026-08-27
authority: canonical
---

# v1 범위

기준: [COUNCIL](../council/03-codex-gpt5.6-debate-and-final-synthesis.md) "구현 우선순위" 0–6
+ 현재 저장소의 실제 구현 상태(S23, 저장소 실물).

---

## 이미 구현되어 있는 것

| 항목 | 상태 | 근거 |
| --- | --- | --- |
| `/repo` + `$repo-archive` (Claude 코디네이터 → Codex 작업자) | 동작 | `.claude/commands/repo.md`, `skills/repo-archive/SKILL.md` |
| 고정 SHA 기반 한국어 아카이브 스키마 7종 | 아카이브 18개 · 문서 202개 | `archive/README.md` |
| `scripts/validate-repo-archive.sh` 스키마 검증 | 통과 | S23 |
| 아카이브 인덱스 자동 생성 + CI 최신성 검사 | 동작 | `scripts/generate-archive-index.py`, `.github/workflows/archive-index.yml` |

> 이것은 **아카이브 형식 검증**이 통과했다는 뜻이지 기획 하네스(`/plan`, `/plan-close`)가
> 구현됐다는 뜻이 아니다. (S23 명시)

---

## v1에 반드시 들어가는 것

| # | 항목 | 완료 기준 |
| --- | --- | --- |
| V-0 | **실제 요청 픽스처 15~20건 수집** | 각 fixture에 입력 요청·기대 planning unit·기대 gate·기대 문서 패키지·허용 가능한 대안·사람의 수정 결과를 기록 |
| V-1 | `SKILL.md` v1 | tier 정의, 2질문 rubric(blast radius / 불확실성), hard gate 8, 정책 충돌 우선순위, 상태·frontmatter·명명 규약, few-shot 자리 |
| V-2 | 템플릿 3개 | Tech Spec(Planning Capsule 섹션 포함), T1 Compact Brief, T2 Charter. 각 길이 캡 명기 |
| V-3 | `/plan` | 재사용 검색 → 분류 제안 → gate 체크리스트 인쇄 → 사람 1클릭 확정 → 필요한 문서만 생성. 재실행 = 재분류 |
| V-4 | `/plan-close` + 검증 스크립트 | 스키마·링크·미체크박스·예산·open-loop 검사 → 상태 확정 + `current/` 갱신 |
| V-5 | 최소 어댑터 | 공통 정의 → `CLAUDE.md`(@AGENTS.md import) / `AGENTS.md`, `.claude/agents` ↔ `.codex/agents`, `.claude/skills` ↔ `.agents/skills`. managed marker + source hash |
| V-6 | 역할 2개 | `implementer`(writer, worktree당 1명) / `reviewer`(read-only) |
| V-7 | Evidence 계약 | [능력 지도 C-E1](capability-map.md) 최소 필드 |
| V-8 | 프로젝트 부착 상태 파일 | 하네스 버전과 활성 기능만. 인증정보 없음 (S12) |
| V-9 | **수직 슬라이스 1건 관통** | 아래 참조 |
| V-10 | shadow mode 20건 운영 | 분류를 전수 사람 확인. 오분류는 fixture + rubric 예시로 축적 |

---

## 증명해야 할 최소 흐름

v1의 유일한 합격 기준이다.

```text
실제 T1 요청 1건
  → LLM: 사실·가정·미확인·분류 후보 추출
  → 승인 메시지에 2질문(blast radius / 불확실성) + hard gate 8 체크리스트 인쇄
  → 사람 1클릭 확정
  → 정책 테이블이 문서 패키지·차단 상태 계산
  → Compact Brief + Tech Spec 생성 (frontmatter에 policy_version·fired_rules)
  → Orca dispatch → 런타임 A가 implementer (worktree 1 writer)
  → 런타임 B가 read-only reviewer
  → 현재 HEAD SHA에 묶인 commands·exit_codes·artifact_hash 증거
  → /plan-close 검증 통과 → status 확정 + current 갱신
  → A/B 역할 교체 재현 → 동일 artifact 스키마·게이트 판정
```

합격 조건은 **역할 교체 재현**이다. 이것이 안 되면 하네스가 존재할 이유가 없다.
이 경로가 통과하기 전에는 BMAD·CIS·디자인·자기학습·OpenWiki·인덱스를 시작하지 않는다.

근거: S01 KEEL 리뷰 §1, S10 최종 결론, COUNCIL 구현 우선순위 5.

---

## v1에서 명시적으로 짓지 않는 것

트리거가 오기 전에는 만들지 않는다. 트리거를 미리 이름 붙여 두는 것이 이 표의 목적이다.

| 항목 | 도입 트리거 |
| --- | --- |
| 인덱스 / catalog / SQLite | 문서 약 100개 이상 또는 저장소 횡단 조회 반복 |
| 큐 / DB / 샤딩 | 동시 요청자 2명 이상 |
| hook 파이프라인 | (사실상 기각 — 핵심 상태 전이는 hook에 의존하지 않는다) |
| 물리 archive 폴더 | (기각 — archive는 상태이지 폴더가 아니다) |
| 범용 outcome gate | 측정 가능한 제품 가설이 실제로 등장할 때 |
| 자동 모델 라우팅 | fixture 축적 + T0 저위험 한정 |
| OpenWiki 연동 | v1 수직 슬라이스 통과 후 |
| BMAD / CIS 기획 자산 통합 | v1 수직 슬라이스 통과 후 |
| 디자인 트랙 4스킬 | UI 산출물이 실제로 필요한 프로젝트가 생길 때 |
| 자기학습 승격 루프 | 실패 fixture가 축적된 뒤 (가장 마지막) |

---

## 모델 라우팅에 대한 v1 입장

자동 라우팅은 구현하지 않는다. 대신 **전제조건만** 넣는다.

1. 역할이 모델이 아니라 capability를 선언한다 (`deep-reasoning` / `fast-read` / `precise-implementation`).
2. 역할이 처음 등록될 때 런타임·모델·reasoning effort·권한·툴 프로필 추천안을 보고하고 승인받아 고정한다.
3. task별 명시적 override가 중앙 기본값보다 항상 우선한다.
4. 검증되지 않은 provider model ID는 넣지 않는다. ([제약 K-12](constraints.md))

근거: S01 인용 대화("공통 워크플로우 + 명시적 선택 = 가장 좋은 출발점,
공통 워크플로우 + 제한적 자동 선택 = 최종적으로 도달할 구조"), S01 KEEL 리뷰 §7.

---

## v2 이후 권장 순서

1. Orca 개발 실행 루프 정교화 (Delivery Map / Executable Plan 분리)
2. BMAD 기반 기획 라우터 (2축: 계획 깊이 × 탐색 오버레이)
3. 검증·drift·CI 강화, 하네스 지표 8종 계측
4. 전문 역할 확장 — architect·debugger·QA → security·SRE → design 4종 → backend/frontend/DB → researcher·doc-auditor
5. OpenWiki 파생 계층 + converge 검사
6. MCP registry 공통 스키마
7. 자기학습 + upstream update PR

근거: S01 KEEL 리뷰 §7 권장 추가 순서, COUNCIL 구현 우선순위 6.

---

## 워크플로우 호출 규칙

기획·디자인·개발은 **독립 호출이 기본**이고, 강제되는 선행조건은 하나뿐이다.

- 강제: **구현 착수는 승인된 Tech Spec을 요구한다.** (S12 상태2 `SPEC_READY`)
- 비강제: 기획 → 디자인 → 개발 순서. T0는 기획 파일이 0개이고, 탐색 워크플로우는
  `phase=anytime, required=false`이며, 디자인은 UI 산출물이 있을 때만 붙는 조건부 트랙이다.

"모든 작업에 brainstorming 강제"를 제외한 이유가 정확히 이것이다.
([결정 D-33](../decisions/decision-register.md), S02 분석 3, S03)
