
## Round 1: Initial Responses


---
## 🔳 Codex (scalability) - gpt-5.3-codex-spark
결론부터 말하면, **최적은 “Rule-First + LLM Compose” 하이브리드 아키텍처**입니다.  
핵심은 `작은 PRD 하나`가 아니라, **요청 객체(Object) + 리스크/불확실성/조율 축 + 하드 게이트**로 문서 패키지를 결정하고, 실행까지 연결되는 **상태 기반 오케스트레이터**를 만드는 것입니다.

---

## 1) 확정적으로 반영된 사실 / 가정 / 권고

확인된 사실  
- 당신의 기존 설계는 방향이 맞습니다. 고정 PRD보다 **작업 유형 + 불확실성 + 위험 + 영향 + 조율 복잡도**로 나누는 접근이 타당합니다.  
- `current / work / evidence / decisions / releases / archive`처럼 **시간축 분리**는 장기 운영에서 아주 중요합니다.

전제  
- 문서는 Git/Markdown 기반으로 관리하지만, API·워크플로우 연동은 LLM 에이전트(Claude/Codex)로 자동화할 수 있다고 가정합니다.  
- 프로젝트 수가 늘어도 사람/팀 의사결정 책임은 남고, 실행 자동화는 보조 수단이어야 한다고 가정합니다.

권고  
- 지금 필요한 것은 “문서 템플릿 추가”가 아니라 **문서 생성의 규칙 엔진 + 실행 상태/의존성 그래프 + 검증 게이트**입니다.  
- GPT 제안은 좋은 뼈대를 줬고, 이를 운영 가능한 시스템으로 만들려면 다음 4가지를 강화해야 합니다:  
  1) 스키마 기반 매니페스트, 2) 결정 규칙의 기계 판별, 3) 링크 그래프 검증, 4) 토큰/문서 생성 상한 제어.

---

## 2) 권장 아키텍처: Planning Unit + Document Graph Orchestrator (PGO)

### 아키텍처 한 줄
`요청 입력 -> 분류 엔진(Classifier) -> 패키지 매니페스트 생성 -> 문서 생성/재사용 결정 -> 실행계획 생성 -> 출시/측정 후 Work 상태 갱신/아카이빙`

### 핵심 컴포넌트
1. `Request Intake`  
   - 요청 스키마 정규화(요구사항, 대상 채널, 범위, 제약, 기존 연결 ID)
2. `Rule Engine`  
   - 객체 유형(Feature/Initiative/Experiment/Project/Platform) 판별  
   - hard gate 판단(결제, 법무, 보안, 마이그레이션, 외부 API 등)
3. `Manifest Composer (LLM+템플릿)`  
   - 공통 코어 + 오버레이 조합으로 “필요 문서 세트” 산출
4. `Execution Planner`  
   - Milestone / Dependency / Rollout 조건 / 실패 후 롤백 조건까지 출력
5. `Graph Store`  
   - 문서 간 관계를 SSOT로 보관 (id, parent, child, supersedes, implements, blocks)
6. `Policy Validator`  
   - 링크 정합성, 상태 전이, 중복/재사용 가능성, missing required docs 검증
7. `Ops Adapter`  
   - Git, 이슈트래커, 분석시스템으로 동기화

---

## 3) 왜 기존 제안에서 고쳐야 할 부분이 있는가 (비판 포인트)

- 장점:  
  - 작업 유형 + hard gate 개념, current/work/evidence 분리, ADR/상태 분리, 현재 기획과 변경 제안 분리 원칙은 매우 적절합니다.
- 보완 필요:  
  - “어떤 조건에서 어떤 문서를 무조건 생성/생략”이 규칙으로 완결되지 않아 자동 실행성이 낮습니다.
  - feature/initiative/project 구분이 설명되어 있으나, **관계 그래프(edge type)와 상태 전이**가 덜 명확해 중복/누락 위험이 큽니다.
  - 10x 규모에서는 템플릿 조합 폭발을 막을 **문서 예산/토큰 예산 정책**이 필요합니다.
  - LLM 출력 품질 관리(스키마 검증, ID 제어, 링크 무결성)가 빠져 있어 오탐/환각 리스크가 큽니다.
  - “하네스만 저장소 분리”는 맞지만, 프로젝트별 결정/근거를 프로젝트로 안정적으로 링크하는 **stable ID 계약**이 핵심인데 제안이 상대적으로 약합니다.

---

## 4) 질문 항목별 검증

### A) 고정 PRD 포맷 대신 동적 깊이 결정
동의합니다.  
다만 구현에서는 다음만 지켜야 합니다.

- 문서 템플릿을 무한히 늘리지 말고 **Core + Overlay**로 유지.
- “점수 합산 후 임계치” 금지, 대신 **독립 축 + hard gate + 필수 모듈 목록** 기반 규칙 사용.
- 예: `uncertainty=high`이면 `feature_prd`를 강행하지 말고 `discovery` 우선.

예시 규칙(개념):

```python
if hard_gate.payment or hard_gate.legal: add_overlay("risk_compliance")
if scope > 2 or channels > 1: add_doc("journey_map")
if uncertainty in ["high","very_high"] and evidence_confidence < 0.6: add_doc("discovery_brief") and block("implementation-ready")
if impact in ["high","critical"]: add_doc("measurement_plan","rollback_plan")
```

### B) feature / initiative / project 분리
당장 실무에서 가장 안정적인 구분은:

- `Initiative`(전략적 베팅, 다수 기능/채널 영향)  
- `Feature/Change`(단일 사용자 문제 해결 단위)  
- `Project`(기술/운영 제약이 큰 Delivery Container, 일정·자원 집계용)  
- `Task`(실행 티켓)

이때 `Project`는 제품 의사결정 단위가 아니라 **조정/예산/일정의 전달 단위**로만 쓰는 게 중요합니다.

### C) 분류→생성→validation→실행계획 워크플로우
권장 파이프라인(상태 전이):

1) `idea`  
2) `triaged`  
3) `discovery` (필요시)  
4) `ready_to_plan`  
5) `approved`  
6) `active`  
7) `released`  
8) `measured`  
9) `closed / superseded / archived`

핵심 연결점:
- 각 단계에서 `Policy Validator`가 통과되지 않으면 다음 단계로 못 감.
- `released`는 끝이 아님. `measured` 또는 `blocked_measurement`가 되어야 닫힘.

### D) deterministic rule vs LLM
**Deterministic에 두어야 함**  
- 분류 객체 타입(대부분 라벨 기반 분류)  
- hard gate/필수 오버레이  
- 문서 패키지 조합(규칙표)  
- 상태 전이 및 링크 제약  
- 승인 필요/검토 필요 조건

**LLM이 맡아야 함**  
- 요구사항 요약(한국어)  
- AC/가설/측정 지표 초안  
- 리스크 서술, 의사결정 로그 정리  
- 기술 스펙 초안(인력, 코드베이스 문맥 포함)

**제약 조건**: LLM 출력은 스키마 검증 후 반영, 무증거 생성 금지.

예시 출력 형식:

```yaml
id: INIT-014
type: initiative
doc_status: approved
work_status: ready
required_modules:
  - core
  - validation
  - measurement
  - risk_compliance
requires_llm:
  - user_story
  - hypotheses
  - implementation_notes
hard_gates:
  - payment
  - legal
```

### E) SSOT와 dependency 관리
핵심은 문서 갯수보다 **관계**입니다.

최소 관계 스키마:
- `id`, `type`, `version`, `doc_status`, `work_status`
- `parent`, `children[]`, `supersedes[]`, `replaces[]`
- `supports[]` (Goal/Bet)
- `implements[]` (Feature 구현)
- `blocks[]` (의존성)

SSOT 규칙:
- 전략/정책 기준: `product strategy` 단일 위치
- 아키텍처 결정: ADR 단일 위치
- 실행 작업: 이슈 트래커 단일 위치(복사하지 않음, 링크만)
- 실제 성과: 분석시스템 단일 위치(숫자만 신뢰)

문서에 원문 인용 대신 링크/ID 중심으로 중복을 줄입니다.

### F) 과도한 문서화/토큰 낭비 방지
- 문서 깊이를 `D0~D3`로 강제:
  - D0: Core only (매우 작음)
  - D1: Core + 1~2 overlay
  - D2: Core + 필요한 overlay
  - D3: Core + 다중 overlay + 실행/리스크 패키지
- `max_tokens_by_stage` 정책 적용(예: discovery brief 1,500~2,000 토큰).
- 유사 요청 캐시: 유사한 요청은 재생성 대신 재활용/업데이트 제안.
- 기존 문서 재사용 우선(수정 vs 신규 생성 결정 규칙).

---

## 5) 확장성(10x/100x) 관점 설계

수백~수천 문서/일 처리할 때 병목은 LLM API 호출과 검증 I/O입니다.

- **수평 확장**
  - 분류/검증/생성 워커를 분리해 큐 기반 비동기 처리
  - 입력이 많을 때 워커 숫자 증가
- **샤딩**
  - 프로젝트/워크스페이스 단위로 메타데이터 파티션
  - 최근성 높은 active work는 별도 샤드로 분리 운영
- **캐싱**
  - 템플릿/룰/최근 분류 결과 캐시
  - 동일 범주의 작은 변경은 “템플릿 렌더 캐시” 재사용
- **비동기 처리**
  - 즉시 결과(D0) 반환 후, 고비용 문서(리서치/기술 요약)는 백그라운드 생성
- **정합성**
  - 최종 반영은 2단계(초안+확정)로, 임시 저장 후 검증 통과시 커밋
- **병목 방어**
  - 문서 빌드 타임아웃, 재시도 정책, idempotency key(중복 처리 방지)

---

## 6) Claude Code/Codex로 구현 가능성

가능합니다. 초기 구현은 Git 저장소 기반으로 시작하고, 필요하면 분리형 DB로 진화시키는 게 현실적입니다.

- 시작 단계:  
  - `planning-harness` 레포: 정책, 템플릿, 규칙, 검증기  
  - 각 프로젝트: `current/work/evidence/decisions/release` 디렉터리 + 문서 카탈로그
  - Codex가 `manifest`를 계산해 파일 뿌리기
- 성숙 단계:  
  - 중앙 Graph Store(Postgres/Neo4j) + Git mirror  
  - Webhook/CI로 자동 상태 갱신  
  - 분석시스템과 연동해 measured 폐기 조건 트리거

---

## 7) 마지막 정리 (권장안 근거)

당장 채택할 한 가지는 “**Rule-First Planning Graph Orchestrator**”입니다.

이 방식이 맞는 이유:
- 규칙은 추적 가능하고 자동화 가능하므로 확장성·일관성이 올라갑니다.
- LLM은 문장 생산과 창의적 요약에만 쓰고, 판단은 규칙으로 고정해 운영 실패를 줄입니다.
- 문서 생성을 “요청 규모”가 아니라 **결정 위험과 실행 영향도**로 제어해 과도 문서화를 막습니다.
- 출시 이후의 측정/폐기/대체까지 한 흐름으로 다루어 제품 지식 손실을 줄입니다.

---

원하면 다음 답변에서 이 권장안 기반으로 바로 쓸 수 있는 **실제 정책 YAML 스키마 + rule DSL + 매니페스트 예시 + 검증체커(예시 규칙 25개)**를 바로 정리해줄게.


## Round 2: Rebuttals


---
## 🔳 Codex REBUTTAL - gpt-5.3-codex-spark
결론부터: **[CODEX'S RESPONSE]를 채택하는 게 맞고, 첨부 대화의 제안(원문)에서 좋은 아이디어를 흡수해 규칙 정합성·거버넌스만 보강하면 바로 운영 가능한 형태**입니다.

## 1) 각 접근의 강점

### 원문 제안 (첨부 대화의 GPT 설계)
- 장점: 기획을 `Change/Feature/Experiment/Initiative/Strategy`로 분리해 **문서의 형식을 “요청 크기”가 아니라 **기획 객체 성격**에 맞춰 나눈 점이 정확함.
- 장점: `Scope/Uncertainty/Impact/Risk/Coordination` 축과 hard gate(결제·법무·보안·마이그레이션)를 통해 **구조적 확장성**을 제시함.
- 장점: `current/work/evidence/decisions/releases/archive` 분리로 **현재 상태 vs 이력**을 구분한 점은 장기 운영에서 핵심.
- 장점: 문서 ID·메타데이터 중심 운영으로 **폴더 트리 의존을 줄이려는 방향**이 맞음.

### [CODEX'S RESPONSE]
- 장점: `Rule-First + LLM Compose`로 판단의 4대 요소(분류/패키징/생성/검증/실행)를 **실행 엔진 관점**으로 정리한 점이 강함.
- 장점: `Graph Store` + 상태기반 오케스트레이터 + validator를 제시해 **자동화 가능한 아키텍처**로 구체화함.
- 장점: deterministic rule과 LLM 책임 영역을 분리해 **운영 리스크(오탐/허위 생성)**를 줄이려 한 점이 실무에 유리.
- 장점: 토큰/문서 비용 통제(D0~D3, 생성 상한) 개념을 넣어 **과도 문서화 방지 의도**가 분명함.

## 2) 약점/블라인드 스팟

### 원문 제안의 약점
- 규칙이 개념 수준이라 **자동 판별 가능한 정책으로 완결되지 않음**(예: 어느 조건에서 무조건 Discovery로 간주할지 불명확).
- `Feature/Initiative/Project` 관계가 풍부하지만, **유효성 제약(중복/순환 링크/우선순위)**이 없음.
- 문서 수와 토큰 관리에 대한 수치 규칙이 약해 운영 시 문서 폭발 가능성 큼.
- LLM이 생성한 콘텐츠의 스키마 검증, ID 일관성, idempotency가 빠져 있음.

### [CODEX'S RESPONSE]의 약점
- `Project` 개념이 남아 있어 현실적으로는 **Initiative/Release/Work Stream와 경계가 모호**해질 수 있음.
- Graph Store 언급은 좋지만, 실제로 필요한 최소 계약(필수 필드, edge 타입, 충돌 규칙)이 더 구체적이어야 함.
- hard gate를 제시했지만, gate 통과 실패 시 **자동 Escalation 정책**(누가 언제 개입하는지) 정의가 약함.
- 초기 운영 비용이 큰 편이므로, **도입 순서(최소 구현 MVP)**가 별도로 제시되면 좋음.
- 보안·권한·PII 관리(예: 리서치 원본 링크, 접근권한 정책)를 실행 단계에서 분명히 고정하지 않음.

## 3) 서로 놓친 부분

- 원문은 정책·개념은 풍부하지만 **자동 실행 규칙**이 약함.
- [CODEX'S RESPONSE]는 규칙 엔진은 강하지만, 실제 운영에서 필요한 **요청 intake 품질(누락/애매함) 처리**가 약함.
- 두 접근 모두 공통적으로 부족한 점:
  - `문서 필요 여부`와 `기존 문서 재사용`에 대한 결정 규칙이 체계화되지 않음.
  - "동일한 변경 제안이 기존 작업과 충돌/중복될 때"의 처리 정책(merging/분기) 부재.
  - 실패 실험/중단 결정의 `post-mortem` 필수 메타데이터가 약함.
  - 오너십과 승인권한 모델(RACI) 미정의.

## 4) 원본 권고 수정안 (실행 가능한 형태로 보강)

당장 적용하려면 기존 제안의 핵심은 유지하되, 다음 7가지로 정제하세요.

1. `Rule-First Planning Graph`를 유지하되, 규칙 DSL을 추가한다.  
2. `Project`를 의사결정 단위에서 빼고 `Initiative/Feature/Change` 중심으로 정리한다.  
3. 요청 품질을 `confidence score`로 관리하고, 낮으면 LLM 보정 대신 인간 승인 경로로 강제한다.  
4. 문서 패키지 결정 전에 “재사용 검색”을 먼저 수행한다(동일 목표, 동일 사용자군, 동일 성공지표면 신규 생성보다 supersede/update).  
5. Graph 제약을 최소화한다: `parent/type/owner/version/supersedes/blocks/dependency`만 필수로 강제.  
6. 문서 생성량 제한을 수치로 고정한다(`max_depth`, `max_tokens`, `max_docs_per_cycle`, `max_overlays`).  
7. `release -> measured -> closed` 전환 조건을 metric + 이유 기반 로그로 강제한다.

예시 보강 규칙 스케치:

```yaml
manifest_rules:
  gates:
    required:
      payment: [legal_review, rollback_plan]
      legal: [compliance_notes, owner_approval]
  package:
    default:
      - core
    add_overlay:
      uncertainty_high: [discovery, decision_log]
      impact_high: [measurement, guardrails]
      coordination_high: [dependency_map, milestone]
      channels_multi: [journey_map]
      repeated_feature_like: [reuse_candidate]
  stop:
    if uncertainty_high && evidence_confidence < 0.65:
      - block: implementation_ready
      - require: experiment_or_research_plan
  budget:
    max_depth: 3
    max_tokens_total: 5000
    max_overlays: 4
```

최종적으로는 `[CODEX'S RESPONSE]`의 구조를 채택하되, 위 보강 규칙을 붙이면 **분류 정확도, 비용 효율성, 추적 가능성, 유지보수성**을 동시에 맞출 수 있습니다.



---
## Synthesis

*(이 synthesis는 하이브리드 런을 종합한다: 위의 Codex(gpt-5.3-codex-spark) debate + 병행 실행된 로컬 Claude 카운슬 3역할 × 2라운드(`02-local-council-debate.md`). 로컬 3인은 같은 모델이므로 로컬 간 합의는 공유 프라이어일 수 있고, Codex와 로컬의 독립 수렴만이 cross-vendor 신호다.)*

### Consensus

- GPT 원안의 뼈대(작업 유형×위험 기반 동적 문서, hard gate, current/work 분리, 합산 점수 금지)는 4자 전원 지지; 규모(7유형·5축·13필드·이중 상태머신 ≈80개념)는 전원이 1인+LLM 운영에 과잉으로 판정.
- Planning unit은 3-tier(Change/Feature/Initiative)로 축소 — Codex도 Round 2에서 Project를 의사결정 단위에서 제외. 나머지 유형은 라벨·선택 섹션·current/ 상시 문서.
- Rule-First + LLM Compose 원칙: LLM은 제안(분류·gate 탐지·내용), 규칙은 강제(gate→섹션 매핑, 상태 전이, 길이 예산).
- 순차 ID 금지(`type-YYYYMMDD-slug`로), frontmatter 최소주의("기계적 소비자 없는 필드 금지"), 벤더 중립 코어(markdown+템플릿+스크립트), 수용 기준 "Change 한 건 5분".

### Divergence

- **해결됨**: 독립 Manifest 파일 폐기(기록은 문서 frontmatter ~6줄로 존속, 승인은 파일 쓰기 전 1클릭); 5축→2질문(blast radius, 불확실성)+gate; T0 무문서(흔적은 커밋 메시지/decisions); 상태 5개(draft/active/done/dropped/superseded); 재분류 = 기존 유닛 위 /plan 재실행; Codex의 인프라(Graph Store·큐·샤딩·2PC·Ops Adapter)는 만장일치 기각 — 수치 캡과 재사용 검색만 흡수.
- **남음**: 파생 catalog 도입 시점(v1 없음 + 명명된 트리거로 수렴 중), 훅 파이프라인·독립 /plan-validate(2:1 기각 우세), 픽스처 러너 vs rubric few-shot(데이터 축적은 합의), 커맨드 2 vs 4, 링크 표기(slug-ID 2표 vs 상대 경로+tombstone 1표).

### Recommendation

**"얇은 결정론적 척추(Thin Deterministic Spine)"** 채택: T0(파일 0)/T1(1파일 brief+선택 섹션)/T2(charter+자식 brief) 3-tier; 분류는 2질문+gate 8 체크리스트를 승인 메시지에 인쇄 후 1클릭 확정, gate 시 최소 T1+risk/rollback 강제, 불확실하면 첫 마일스톤=spike; frontmatter 6줄(status/tier/parent/created/gates/harness_version)이 분류 기록 겸 체크포인트; 폴더명 `type-YYYYMMDD-slug`; current/+work/+decisions.md; 커맨드는 /plan(재사용 검색→분류→승인→생성, 재실행=재분류)과 /plan-close(검증 스크립트→동결→승격) 2개; 벤더 중립 코어(SKILL.md+템플릿 3+close 스크립트)에 Claude/Codex 얇은 어댑터. 파생 catalog·픽스처 러너·훅·DB·큐는 명명된 트리거(grep 체감 저하, 문서 100+, 동시 요청자>1) 전까지 짓지 않는다.

구현 우선순위: (1) SKILL.md v1 → (2) 템플릿 3개 → (3) /plan → (4) /plan-close+검증 스크립트 → (5) 운영 루프(오분류→rubric 예시) → (6) 조건부: 다중 프로젝트 pin/override/catalog.

전체 토론 전문(로컬 R1/R2 포함): `02-local-council-debate.md`
