---
id: v1-scope
type: requirements
status: draft
updated: 2026-08-29
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
| V-11 | **부품 연결 최소 1세트** (개정 3) | G-M2 채택 게이트 통과 → `provenance/imports.yaml`에 `accepted` 항목 + `vendor/` 원문 + 두 런타임 discovery 프로브 + 충돌 fixture 3종(K-68) PASS. M3에서 BMAD/CIS `install` 프로브 + `/plan` 링크 |

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
  → A/B 역할 교체 재현 → 동일 artifact 스키마 · 동일 required_checks · 동일 권한 상한 · 동일 결정적 게이트 판정
     (검토자의 자유 서술 판정 일치는 게이트가 아니라 리포트의 advisory 항목 — 개정 4, D-76)
```

합격 조건은 **역할 교체 재현**이다. 이것이 안 되면 하네스가 존재할 이유가 없다.

이 경로가 통과하기 전에는 부품의 **벤더링·원칙 재작성·자체 제작**, 자기학습, 인덱스를 시작하지 않는다.
`install`·`verbatim` 연결은 코어를 바꾸지 않으므로 채택 게이트를 거쳐 v1 안에서 허용하며,
**동등성은 부품이 켜진 상태에서 증명한다** ([결정 D-58](../decisions/decision-register.md)).

**개정 4(2026-08-29, [D-76](../decisions/decision-register.md)):** 위 흐름의 '게이트 판정' 은 **결정적 요소**로 한정한다 —
결과 봉투 스키마 · 역할 계약(앵커 검사)과 권한 상한 · `required_checks` 의 명령과 종료 코드 · 구현자 면의 gate 판정. 수용 기준(AC)은 종료 검사(`close`)가 본다 — 동등성 리포트의 비교 항목이 아니다. 검토자(LLM)의 자유 서술 판정(PASS/FAIL)은
같은 산출물·같은 런타임에서도 흔들리는 것이 관측돼(D-74) **합격 조건으로 쓰지 않고** 동등성 리포트에 advisory 로 인쇄한다.
판정이 왜 흔들리는지는 [Q-10](../planning/open-questions.md)이 가진다. M2 완료(핵심 동등성 게이트)와 v1 릴리스 완료(V-0~V-11)는 같은 말이 아니다.
근거: `docs/reviews/2026-08-29-codex-m2-rootcause-review/`.

근거: S01 KEEL 리뷰 §1, S10 최종 결론, COUNCIL 구현 우선순위 5. 개정 3: 2026-08-27 사용자 재정의. 개정 4: 2026-08-29 사용자 확정(D-76).

---

## 부품 채택 확정 게이트 (개정 3)

계획 단계에서는 후보만 기록한다. **어느 파일을 어떻게 가져올지는 해당 마일스톤 진입 시 사용자가 확정한다**
([결정 D-52](../decisions/decision-register.md)). 게이트 절차는 다섯 단계다.

1. 후보표 제시 — `archive/<repo>/03-components/`·`04-components-table.md`에서 파일 단위 후보 + 채택 방식 + 켜는 조건 + 충돌 지점
2. 사용자 선택 — 제품 결정(B)이므로 자율 진행하지 않는다
3. `provenance/imports.yaml`에 `status: accepted`, `decided_at`, `source_sha` 기록
4. `vendor/` 복사(`verbatim`) 또는 설치 프로브(`install`) + 어댑터 투영
5. 부착 검증(K-68) PASS → 게이트 닫힘. 실패한 파일은 `rewrite` 강등 또는 `rejected`

| 게이트 | 시점 | 대상 부품 | 확정하는 것 |
| --- | --- | --- | --- |
| G-M2 | M2 진입 | Superpowers | `verbatim` 세트의 파일 목록, 출력 경로 override, 제외 목록 |
| G-M3 | M3 진입 | BMAD 본체 + CIS | 라우터가 추천할 스킬 목록(discovery/T2별), 산출물 링크 규약, Codex 미지원 표기 |
| G-M6 | UI 프로젝트 발생 | WIG · taste · impeccable · ui-ux-pro-max | `verbatim` 파일 목록, `DESIGN.md` 스키마, ui-ux-pro-max 라이선스 판정 |
| G-M7 | v1 통과 후 | OpenWiki | 부착 대상 프로젝트, `.openwikiignore`, 갱신 시점 |

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
| OpenWiki `install` 실험(A-07) | v1 수직 슬라이스 통과 후 → G-M7 |
| BMAD / CIS **벤더링·템플릿 재작성** | 하지 않는다 (D-55). `install` + `/plan` 링크는 v1 M3 → G-M3 |
| 디자인 **자체 제작** 4스킬 | 하지 않는다 (Q-03 → `visual-qa`만 자체). `verbatim` 채택은 UI 프로젝트 발생 시 → G-M6 |
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
2. BMAD/CIS 산출물 흡수 고도화 (2축: 계획 깊이 × 탐색 오버레이 — 라우터는 Romeo, facilitation은 BMAD)
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
