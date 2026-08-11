
## Round 1: Initial Responses


---
## 🔳 Codex (scalability) - gpt-5.6-sol
## 결론

권장 아키텍처는 **Policy-Compiled Planning Graph**, 즉 “정책으로 컴파일되는 기획 그래프”입니다.

> LLM이 요청의 의미·가정·불확실성을 구조화  
> → 버전 관리되는 결정론적 정책 엔진이 planning unit·문서 패키지·게이트 확정  
> → LLM이 허용된 문서만 작성  
> → 검증을 통과한 기술 스펙에서 실행계획 생성  
> → Claude Code/Codex 어댑터가 동일한 계약으로 실행  
> → 코드·테스트·출시·성과 증거를 다시 문서 그래프에 연결

첨부 제안은 방향은 상당히 좋습니다. 특히 고정 PRD를 버리고 모듈식 문서 패키지, hard gate, 현재 문서와 변경 기록의 분리, manifest-first 접근을 제안한 점은 유지해야 합니다.

하지만 그대로 구현하면 세 가지 문제가 생깁니다.

1. `Feature / Initiative` 같은 계층과 `Discovery / Migration / GTM` 같은 작업 성격이 하나의 분류 축에 섞여 있습니다.
2. “어떤 입력이면 어떤 문서를 만드는가”를 확정하는 실행 가능한 정책이 없습니다.
3. 분류·제품 검증·문서 검증·구현 검증·성과 검증이 명확히 분리되지 않았습니다.

따라서 이 문서를 구현 명세로 사용하기보다, 아래 구조로 한 번 더 정규화하는 것을 권장합니다.

---

## 1. 하나의 고정 PRD 대신 문서 깊이를 동적으로 결정하는 방식

동의합니다. 다만 “Small이면 짧은 PRD, Large이면 긴 PRD”가 아니라 **최소 충분 문서 패키지**를 조립해야 합니다.

권장 기본 프로필은 네 개면 충분합니다.

| 프로필 | 적용 기준 | 생성물 |
|---|---|---|
| `P0 Capsule` | 기존 동작의 작고 가역적인 변경, 문제·해법이 확실함 | 별도 PRD 없이 필수 Tech Spec 안에 문제·범위·AC·위험을 포함 |
| `P1 Feature` | 하나의 사용자 역량, 독립 검증·출시 가능 | Compact Feature Brief + Tech Spec |
| `P2 Initiative` | 하나의 성과를 위해 여러 Feature·팀·릴리스가 필요 | Initiative Charter + Validation Plan + 하위 Feature/Spec |
| `P3 Strategy` | 시장·제품 방향이나 장기 투자 판단 | Strategy Decision + Research + Initiative Map |

그 위에 다음 오버레이를 조건부로 붙입니다.

- `discovery`
- `experiment/measurement`
- `security/privacy/legal/payment`
- `migration/rollback`
- `capacity/scalability`
- `operations/support`
- `GTM/launch`

중요한 원칙은 **오버레이가 있다고 무조건 별도 파일을 만들지 않는 것**입니다. 기본적으로 기존 문서의 섹션으로 넣고, 다음 조건에서만 독립 문서로 분리합니다.

- 오너나 승인자가 다름
- 생명주기가 다름
- 여러 기획에서 재사용됨
- 독립적인 검토·감사 기록이 필요함
- 내용이 커서 상위 문서를 압도함

첨부 제안의 공통 코어+오버레이 방향은 맞습니다. [문서의 관련 제안](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:100) 다만 `Change Brief + Tech Spec`을 항상 두 파일로 만드는 방식은 작은 변경에서 문서와 토큰만 늘릴 가능성이 큽니다.

---

## 2. Feature / Initiative / Project 구분

가장 중요한 수정점입니다. 첨부 문서는 `Change, Feature, Discovery, Initiative, GTM, Migration`을 하나의 객체 분류처럼 나열합니다. [현재 분류표](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:27) 하지만 이들은 같은 축이 아닙니다.

권장 모델은 다음과 같습니다.

### 계획 계층

- `Product / Goal`: 장기간 유지되는 제품 방향과 성과 목표
- `Initiative / Bet`: 하나의 측정 가능한 성과를 얻기 위한 투자 단위
- `Feature`: 독립적으로 시연·검증·출시할 수 있는 하나의 사용자 역량
- `Change`: 기존 역량의 국소 변경
- `Task`: 구현을 위한 작업 단위

### 별도 축

- `Project`: 일정·예산·팀을 묶는 실행 컨테이너이지 PRD 종류가 아님
- `Discovery / Experiment`: 학습 방식 또는 생명주기
- `Migration / Platform / GTM / Operations`: 작업 성격 또는 오버레이
- `Release / Milestone`: 구현 순서와 배포 경계

실전 판별 규칙은 단순하게 가져갈 수 있습니다.

- 하나의 사용자 역량이고 하나의 AC 집합으로 승인할 수 있다 → `Feature`
- 독립 출시 가능한 하위 결과물이 둘 이상이거나, 오너·지표·릴리스가 나뉜다 → `Initiative`
- 기존 역량의 계약을 국소 변경하며 새로운 장기 역량을 만들지 않는다 → `Change`
- 기간과 인력만 묶고 별도 제품 성과를 소유하지 않는다 → `Project`
- Initiative에 실제로 하나의 Feature밖에 없다 → Feature로 축소
- Feature가 독립 승인·출시 가능한 여러 단위로 갈라진다 → Initiative로 승격

이렇게 해야 “결제 시스템 마이그레이션”을 `Initiative + migration + payment + rollback`처럼 다중 축으로 정확히 표현할 수 있습니다.

---

## 3. 권장 전체 워크플로우

```text
Intake
  ↓
LLM Normalizer
  ├─ 확인된 사실
  ├─ 가정
  ├─ 미확인 사항
  └─ 분류 후보와 근거
  ↓
Deterministic Policy Compiler
  ├─ planning unit
  ├─ planning profile
  ├─ overlays
  ├─ hard gates
  ├─ 문서 예산
  └─ 다음 상태
  ↓
Planning Package Manifest
  ↓
필요한 문서만 생성
  ↓
Schema·관계·내용 검증
  ↓
제품 검증이 필요한가?
  ├─ Yes → Discovery/Experiment → 증거 확인 → 승인
  └─ No
  ↓
Tech Spec 승인
  ↓
Executable Plan Compiler
  ↓
Claude/Codex 실행
  ↓
코드·테스트·SHA·배포·성과 Evidence
  ↓
Current SSOT 갱신 또는 종료
```

여기서 “실행계획”을 둘로 구분해야 합니다.

- `Delivery Map`: Initiative 단계에서 만드는 마일스톤·의존성·릴리스 윤곽
- `Executable Plan`: 승인된 Tech Spec에서 파생되는 구현 task DAG

상세 구현계획을 Tech Spec 이전에 생성하면 설계가 바뀔 때마다 계획을 다시 써야 합니다. 따라서 **개략 실행지도는 일찍, 실제 작업계획은 Tech Spec 승인 후** 생성해야 합니다.

또한 `validation`도 하나의 단계가 아닙니다.

- Intake validation: 분류 입력과 근거가 충분한가
- Product validation: 문제·가치·가설의 근거가 있는가
- Document validation: 필수 섹션과 관계가 유효한가
- Implementation validation: AC와 테스트를 충족했는가
- Outcome validation: 출시 후 목표 결과가 발생했는가

첨부안의 `create_after_validation`은 어느 validation인지 정의되지 않아 자동화할 때 모호해집니다. [현재 Manifest 예시](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:473)

---

## 4. Deterministic rule과 LLM의 책임 경계

### LLM에 맡길 판단

- 자연어 요청에서 문제·대상 사용자·목표·제약 추출
- 확인된 사실, 가정, 미확인 사항 분리
- 기존 문서와의 의미적 연관 후보 탐색
- Feature/Initiative 분해안 제안
- AC·가설·위험·의존성 초안 작성
- 서로 충돌하는 요구사항 후보 발견
- 분류 근거와 대안 설명

### 결정론적 엔진에 맡길 판단

- JSON Schema 검증
- Tech Spec 필수 규칙
- Hard gate 발동
- 문서 패키지 선택
- 허용된 상태 전이
- ID 고유성, 링크 무결성, DAG 순환 검사
- 승인되지 않은 상태에서 실행 금지
- 정책·템플릿 버전 기록
- 실행 증거의 SHA·종료코드·artifact hash 검증
- 문서 수·토큰 예산 상한
- 병렬 writer 충돌 방지

### 사람에게 남겨야 하는 판단

- 목표와 투자 한도
- 문제를 실제로 풀 가치가 있는지
- Feature와 Initiative 경계가 애매한 경우
- 결제·법무·개인정보·삭제·마이그레이션 승인
- Discovery에서 Delivery로 넘어갈지
- 출시·중단·롤백 결정

전역 합산 점수는 추천하지 않지만, 첨부안처럼 “점수화하지 말자”에서 끝나서도 안 됩니다. [현재 설명](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:71) 축별 `low/medium/high`와 hard flag를 입력으로 받는 결정표가 필요합니다.

```yaml
rules:
  - id: uncertainty-requires-discovery
    when:
      any:
        - problem_uncertainty: high
        - evidence_confidence: low
    require: [discovery_brief, validation_plan]
    block_transition: spec_ready

  - id: implementation-requires-spec
    when:
      implementation_intended: true
    require: [tech_spec]

  - id: scale-overlay
    when:
      any:
        - expected_growth: ">=10x"
        - hot_path_changed: true
        - stateful_multi_tenant_data: true
    require_overlay: capacity
```

LLM은 위 규칙을 제안하거나 입력값을 추정할 수 있지만, 최종 발동 여부는 정책 엔진이 결정해야 합니다.

---

## 5. Manifest에 추가해야 할 것

기존 Planning Package Manifest는 좋은 출발점입니다. 다만 운영하려면 다음이 더 필요합니다.

```yaml
schema_version: 1
policy_version: 0.1.0
template_version: 0.1.0

case:
  id: 01K...
  unit: feature
  modes: [delivery]
  facets: [migration, payment]

assessment:
  scope: medium
  uncertainty:
    problem: low
    solution: medium
    technical: high
  evidence_confidence: medium
  hard_gates: [payment]
  capacity:
    expected_growth: 10x
    hot_path_changed: true

route:
  profile: P1
  overlays: [payment, migration, capacity]
  documents: [feature_brief, tech_spec]
  blocked_by: [payment_policy_approval]

decision_trace:
  fired_rules:
    - implementation-requires-spec
    - payment-hard-gate
    - scale-overlay

provenance:
  input_hash: sha256:...
  catalog_revision: git:...
  assumptions: [...]
  unknowns: [...]

override:
  actor:
  reason:
  approved_at:
```

`decision_trace`가 있어야 “왜 이 문서가 생성됐는가”를 재현할 수 있고, `policy_version`이 있어야 하네스 업데이트 후 과거 결과를 해석할 수 있습니다.

---

## 6. SSOT와 dependency 관리

첨부안의 “폴더보다 ID와 관계가 중요하다”는 판단은 맞습니다. [SSOT 제안](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:322) 다만 다음은 수정해야 합니다.

### 권장 저장 원칙

- 각 문서 frontmatter가 관계의 원본
- 역참조와 카탈로그는 자동 생성
- `catalog.yaml`은 사람이 수정하는 SSOT가 아니라 generated index
- 순차 ID `FEAT-014` 대신 ULID 또는 날짜+slug+entropy 사용
- 문서는 상태가 바뀌어도 경로를 옮기지 않음
- `archive/`는 물리적 이동 폴더보다 metadata 기반 view로 구현
- 실행 시 문서 ID만 참조하지 말고 Git SHA와 content hash까지 고정
- 양방향 링크를 모두 수동 저장하지 말고 한쪽 관계에서 역링크 생성

첨부안의 `current/work/archive` 구분은 개념적으로 좋지만 [현재 폴더 구조](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:242), 문서를 상태마다 이동하면 링크가 깨지고 병렬 브랜치 충돌이 늘어납니다. 안정된 경로와 metadata 상태를 유지하고 `current`, `archive` 목록을 생성하는 방식이 낫습니다.

MVP에서는 Git+Markdown/YAML을 SSOT로 두고, `.romeo/index.sqlite`를 재생성 가능한 로컬 검색 캐시로 두십시오. 중앙 데이터베이스는 아직 필요 없습니다.

---

## 7. 과도한 문서화와 토큰 낭비 방지

다음 규칙을 정책으로 강제하는 것이 좋습니다.

- P0는 별도 PRD를 만들지 않고 Tech Spec에 planning capsule 포함
- 문서당 섹션 예산과 전체 package 예산 설정
- 이미 기준 문서에 있는 내용은 링크만 하고 복사 금지
- 상위 문서 전체가 아니라 관련 노드 1-hop만 컨텍스트에 로드
- 각 문서에 짧은 machine summary와 content hash 저장
- 입력+catalog snapshot+policy version이 같으면 분류 결과 캐시
- Low-risk 작업은 classifier 1회+writer 1회로 제한
- 전문 reviewer는 hard gate 또는 overlay가 발동할 때만 추가
- PRD·Tech Spec·실행계획 전체를 매 단계마다 재전송하지 않고 필요한 필드만 task envelope로 전달
- 미확인 내용은 장문의 추측 대신 `UNKNOWN` 또는 `NEEDS_VALIDATION`으로 남김

첨부안은 “필요한 문서만 생성한다”고 말하지만 [워크플로우 설명](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:521), 무엇을 생략해야 하는지와 문서 예산이 없습니다. 이 부분은 정책으로 명문화해야 실제 비용이 통제됩니다.

---

## 8. 10배·100배 확장 시 구조

### 초기/MVP

- Git: 문서와 정책 SSOT
- SQLite: 재생성 가능한 로컬 인덱스
- 동기식 CLI 실행
- ULID 기반 ID
- case당 한 writer
- content-hash 캐시

### 10배 성장

- LLM 작업을 비동기 job queue로 분리
- idempotency key로 중복 생성 방지
- 프로젝트별 동시 실행 제한
- 변경된 문서만 증분 인덱싱
- 저비용 모델은 추출·초안, 고성능 모델은 고위험 분류·리뷰에만 사용

### 100배 성장

- 문서 본문은 계속 Git 또는 object storage에 유지
- Postgres에는 문서 metadata·관계·job·lock만 저장
- tenant/repository 기준 파티셔닝
- 자주 조회되는 그래프·요약 캐시
- 교차 저장소 링크 검증과 stale detection을 비동기화
- 조직 단위 정책 상속과 프로젝트별 override 감사 기록

DB sharding은 처음부터 필요하지 않습니다. 수백 프로젝트와 수십만 metadata row 정도는 일반적인 Postgres로 충분합니다. 실제 tenant isolation이나 쓰기 처리량 한계가 확인된 뒤에만 파티셔닝·샤딩을 고려하는 편이 운영비와 이전 가능성 면에서 낫습니다.

---

## 9. Claude Code/Codex로 실제 구현 가능한가

가능합니다. 다만 **에이전트 프롬프트가 워크플로우를 통제하게 만들면 안 됩니다.** Romeo CLI가 상태 머신과 정책 권위를 가져야 합니다.

양쪽 모두 비대화식 실행과 JSON Schema 기반 결과를 지원합니다.

- Codex는 `codex exec --output-schema ... --json` 형태의 자동화가 가능합니다. [OpenAI Codex 공식 문서](https://learn.chatgpt.com/docs/developer-commands#codex-exec)
- Claude Code는 `claude -p --output-format json --json-schema ...` 형태의 구조화 출력을 지원합니다. [Claude Code 공식 문서](https://code.claude.com/docs/en/headless)
- 양쪽 모두 hook·subagent 기능이 있지만 기능과 안정성이 완전히 같지는 않습니다. 특히 Claude의 agent hook은 현재 실험적이므로 핵심 상태 전이를 hook에 의존하지 않는 것이 안전합니다. [Claude Code hook 가이드](https://code.claude.com/docs/en/hooks-guide), [Codex 설정 문서](https://learn.chatgpt.com/docs/config-file/config-reference#configtoml)

권장 구현 경계는 다음과 같습니다.

```text
Romeo Core
├── schemas/          # 공통 입력·출력 계약
├── policies/         # 결정론적 routing/state rules
├── templates/        # 문서 모듈
├── compiler/         # manifest와 실행계획 생성
├── validators/       # schema, graph, gate, evidence
├── adapters/
│   ├── claude-code/
│   └── codex/
└── fixtures/         # 양 런타임 semantic parity 테스트
```

Claude와 Codex의 “동일한 워크플로우”는 같은 프롬프트 파일을 쓴다는 뜻이 아닙니다. 동일한 schema, AC, 권한, 상태 전이, 완료 게이트, evidence 계약을 통과한다는 뜻이어야 합니다.

---

## 10. 첨부 GPT 제안의 최종 평가

유지할 부분:

- 고정 PRD 포맷 거부
- 제품 기획 강도와 기술 구현 강도 분리
- hard gate
- 공통 코어+오버레이
- Initiative Charter와 Feature PRD 역할 분리
- 현재 사실과 변경 기록 분리
- 문서 상태와 작업 상태 분리
- manifest-first
- 하네스와 프로젝트 산출물 분리

수정이 필요한 부분:

- planning unit, work mode, domain을 별도 축으로 분리
- `Project PRD` 대신 Project를 실행 컨테이너로 정의
- 규칙 테이블과 상태 머신 추가
- validation을 다섯 종류로 분리
- micro change는 별도 Change Brief를 생략 가능하게 함
- 수동 catalog와 순차 ID 제거
- 물리적 archive 이동 대신 metadata view 사용
- policy/schema/template 버전과 decision trace 추가
- 실행계획을 Tech Spec 승인 뒤에 컴파일
- Claude/Codex 내부 기능이 아니라 Romeo CLI를 제어 평면으로 사용

가장 적합한 첫 구현 범위는 `P0/P1 → 필수 Tech Spec → Codex/Claude 구조화 출력 → deterministic validator → current-SHA evidence` 한 개의 수직 슬라이스입니다. Initiative, Discovery, 중앙 DB, 다중 전문 리뷰는 이 슬라이스가 실제로 양 런타임에서 같은 의미로 통과한 뒤 확장하는 것이 안전합니다.

현재 저장소는 README와 논의 문서 중심의 초기 상태이므로, 위 평가는 구현 테스트 완료가 아니라 **구현 가능한 아키텍처 검토 결과**입니다.


## Round 2: Rebuttals


---
## 🔳 Codex REBUTTAL - gpt-5.6-sol
## 결론

제 round‑1 답변을 그대로 채택하지는 않겠습니다. 핵심 원리는 맞지만, 현재 Romeo처럼 README와 논의 문서만 있는 초기 저장소에는 다소 무겁습니다.

수정 권고안은 **Thin Policy-Compiled Planning Spine**, 즉 “얇은 정책 컴파일형 기획 척추”입니다.

> LLM이 의미를 해석하고 분류를 제안  
> → 사람 또는 근거가 분류·위험 신호를 확정  
> → 결정론적 규칙이 문서 패키지와 게이트를 계산  
> → 승인된 기획 문서와 Tech Spec에서 실행계획 생성  
> → Claude/Codex는 동일한 계약을 서로 다른 방식으로 수행  
> → 코드·테스트·현재 Git SHA를 증거로 종료

`Graph`는 유용한 데이터 모델이지만, 아직 별도 시스템이나 아키텍처의 중심으로 만들 필요는 없습니다.

참고로 제공된 프롬프트에는 round‑1 답변이 `CODEX'S RESPONSE` 하나만 명시되어 있습니다. 아래의 “각 접근”은 첨부 GPT 원안과 Codex 답변을 비교한 것입니다.

## 1. 각 접근의 강점

| 접근 | 가장 강한 부분 |
|---|---|
| 첨부 GPT 원안 | PM 관점의 문서 체계, 시간축, SSOT를 잘 설명 |
| Codex round‑1 | 그 개념을 실제 하네스 계약과 규칙으로 바꿈 |

### 첨부 GPT 원안

가장 가치 있는 부분은 다음입니다.

- 단순한 `Small / Medium / Large`가 아니라 작업 종류·불확실성·영향·위험·조율 비용으로 문서 깊이를 결정합니다. 이는 동적 문서화의 올바른 출발점입니다.
- 합산 점수 대신 축별 결과가 서로 다른 행동을 유발하도록 설계했습니다. 예를 들어 불확실성은 Discovery를, 위험은 승인·롤백을 추가합니다. [관련 부분](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:51)
- 공통 코어와 조건부 오버레이를 조립하는 방식은 템플릿 폭발을 피할 수 있습니다. [관련 부분](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:100)
- `current`와 `work`를 분리해 “현재 제품의 사실”과 “당시 변경 의도”를 동시에 보존한다는 설명이 매우 좋습니다. [관련 부분](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:230)
- 사실·결정·실행 상태별로 SSOT가 다르다는 설명도 정확합니다. 코드 상태, 배포 상태, 제품 정책, 실제 지표를 하나의 문서가 모두 소유해서는 안 됩니다. [관련 부분](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:388)
- PRD부터 쓰지 않고 먼저 `Planning Package Manifest`를 만든다는 발상은 자동화 가능한 좋은 경계입니다. [관련 부분](/Users/julliettelee/orca/Romeo-Harness/docs/planning-harness-discussion.md:465)

즉, 원안은 “어떤 지식을 어떤 시간적 성격으로 보존할 것인가”를 가장 잘 설명합니다.

### Codex round‑1

Codex 답변은 원안의 개념을 실행 가능한 구조에 가깝게 만들었습니다.

- `planning unit`, `mode`, `facet/overlay`를 분리해 원안의 혼합된 분류 체계를 바로잡았습니다.
- `Project`를 제품 의사결정 단위가 아닌 일정·인력·예산의 실행 컨테이너로 정의했습니다.
- LLM과 결정론적 엔진의 책임을 분리했습니다.
- Product/Document/Implementation/Outcome validation을 구별했습니다.
- Tech Spec 전에 만드는 `Delivery Map`과 승인 후 만드는 `Executable Plan`을 구분했습니다.
- `policy_version`, `decision_trace`, 입력 및 카탈로그 revision을 남겨 결과를 재현할 수 있게 했습니다.
- Claude와 Codex의 동일성을 “같은 프롬프트”가 아니라 schema·AC·권한·증거·완료 게이트의 의미적 동등성으로 정의했습니다.

이 접근은 실제 하네스를 구현하려면 필요한 통제 구조를 잘 짚었습니다.

## 2. 약점과 블라인드 스팟

### 첨부 GPT 원안의 약점

첫째, 서로 다른 개념이 하나의 분류표에 섞여 있습니다.

- `Feature`, `Initiative`는 범위 단위입니다.
- `Discovery`, `Experiment`는 학습 방식입니다.
- `Migration`, `GTM`, `Operations`는 작업 성격입니다.
- `Strategy`는 장기간 유지되는 방향 문서입니다.

이를 하나의 `object type`으로 두면 조합 규칙이 급격히 늘어납니다.

둘째, 설명은 풍부하지만 실행 규칙이 없습니다. 예를 들어 `uncertainty=high`의 정의, 규칙 충돌 시 우선순위, 어떤 상태에서 실행이 차단되는지가 명확하지 않습니다.

셋째, 1인+LLM 하네스에는 개념 수가 너무 많습니다. 7개 객체, 5개 평가축, 10여 개 오버레이, 다수의 저장 영역과 이중 상태 모델을 모두 처음부터 운영하면 메타데이터가 실제보다 먼저 부패할 수 있습니다.

넷째, 수동 `catalog.yaml`, 순차 ID, 물리적 archive 이동은 병렬 작업과 문서 이동에 취약합니다.

다섯째, 최초 분류가 틀렸거나 작업 중 범위가 커졌을 때의 `reclassify` 경로가 없습니다.

### Codex round‑1의 약점

가장 큰 문제는 원안의 과설계를 비판하면서 일부를 다시 다른 이름으로 도입했다는 점입니다.

1. `P3 Strategy`는 내부적으로 모순됩니다. Strategy는 planning depth profile이 아니라 장기 컨텍스트 또는 결정 문서입니다. 제가 비판한 “서로 다른 축의 혼합”을 프로필에서 다시 만들었습니다.

2. “결정론적 엔진이 planning unit을 확정한다”는 표현은 지나쳤습니다. 자연어 요청이 결제·개인정보·마이그레이션에 해당하는지, 하나의 Feature인지 판단하는 것은 결정론적이지 않습니다.

정확한 경계는 다음입니다.

- LLM: 위험 및 분류 후보를 제안
- 사람 또는 명시적 입력: 의미적 사실을 확정
- 규칙 엔진: 확정된 값의 결과를 강제

예를 들어 `payment=true`를 확정한 뒤 “결제 승인과 롤백 섹션이 필수”로 만드는 것은 결정론적입니다. 자연어만 보고 `payment=true`라고 확정하는 것은 아닙니다.

3. SQLite 인덱스, 10배·100배 큐와 Postgres 설계는 지금 단계에 너무 이릅니다. 이 하네스의 첫 병목은 요청 처리량이 아니라 운영자의 주의력, 문서 부패, 컨텍스트 비용입니다.

4. 실행계획이 Tech Spec에서만 파생된다는 설명도 불충분합니다. 실제 실행계획은 다음을 함께 입력받아야 합니다.

- 승인된 제품 기획
- Tech Spec
- 현재 코드와 Git SHA
- 마이그레이션·운영·출시 제약
- 이미 진행 중인 작업과 소유 경로

5. 독립 Manifest와 문서 frontmatter가 중복 SSOT가 될 위험을 충분히 다루지 않았습니다.

6. 분류 오류의 교정 루프, 규칙 충돌 처리, schema migration, override 만료 정책이 빠졌습니다.

7. `expected_growth >= 10x` 같은 예시는 객관적으로 보이지만 실제로는 프로젝트 문맥이 없는 임의 임계값입니다. 이런 값은 전역 규칙보다 프로젝트별 설정이어야 합니다.

8. `Outcome validation`을 모든 작업의 필수 종료 단계처럼 다루면 내부 리팩터링이나 장애 예방 변경에서 인위적인 지표를 만들게 됩니다. 측정 가능한 제품 가설에만 outcome gate를 요구해야 합니다.

## 3. 두 답변이 공통으로 놓친 부분

### 재분류가 정상 경로여야 합니다

작은 변경으로 시작했다가 데이터 이전이나 정책 변경이 발견되는 것은 예외가 아닙니다.

```text
T0 Change
  → 영향 범위 확대 발견
  → T1 Feature로 재분류
  → 독립 출시 단위가 여러 개로 분리
  → T2 Initiative로 승격
```

기존 기록은 삭제하지 않고 새 분류와 변경 이유를 남겨야 합니다.

### 규칙의 정확도를 검증할 평가 세트가 필요합니다

아키텍처보다 먼저 실제 요청 예시 15~20개를 모아야 합니다.

각 fixture에는 다음을 기록합니다.

- 입력 요청
- 기대 planning unit
- 기대 gate
- 기대 문서 패키지
- 허용 가능한 대안
- 사람의 수정 결과

모델이나 정책을 바꿀 때 Claude와 Codex가 동일한 의미 결과를 내는지 이 fixture로 확인해야 합니다.

### 정책 충돌의 우선순위가 필요합니다

권장 순서는 다음입니다.

```text
Hard gate
→ 실행 차단 조건
→ planning unit
→ 필수 overlay
→ 선택 overlay
→ 문서·토큰 예산
```

필수 gate가 문서 예산을 초과하면 gate를 생략하는 것이 아니라 예산 초과 경고를 내야 합니다.

### 하네스 자체의 성공 기준이 없습니다

최소한 다음은 측정해야 합니다.

- 사람이 분류를 수정한 비율
- 누락된 hard gate 수
- T0 처리 시간
- 생성 문서 중 실제로 다시 읽힌 비율
- 중복 문서 발생률
- stale/broken dependency 수
- 요청당 모델 호출과 토큰 사용량
- 실행 중 재분류된 비율

### 민감한 근거의 저장 경계가 더 구체적이어야 합니다

사용자 인터뷰, 계약, 개인정보, 인증정보 원문은 Git에 들어가지 않아야 합니다. Git에는 접근통제된 원본 위치, 요약, 근거 수준, 문서 ID만 남기는 것이 안전합니다.

## 4. 수정한 최종 권장 아키텍처

### Planning unit은 세 개만 둡니다

| 단위 | 판단 기준 | 기획 산출물 |
|---|---|---|
| `T0 Change` | 기존 계약의 국소적이고 가역적인 변경 | 별도 PRD 없이 필수 Tech Spec 안에 Planning Capsule |
| `T1 Feature` | 독립적으로 승인·시연·검증 가능한 사용자 역량 | Compact Feature Brief + Tech Spec |
| `T2 Initiative` | 독립 결과물·릴리스·지표가 둘 이상 | Initiative Charter + 하위 Brief/Spec |

별도 축은 다음처럼 둡니다.

- `mode`: `discovery | delivery | experiment`
- `facets`: `payment`, `privacy`, `security`, `migration`, `operations`, `gtm` 등
- `project`: 일정·인력·예산의 실행 컨테이너
- `strategy`: `current/`에 존재하는 장기 방향 문서

### 워크플로우

```text
Intake
  ↓
LLM: 사실·가정·미확인 사항 및 분류 후보 추출
  ↓
사람: planning unit·불확실성·hard gate 확인
  ↓
정책 테이블: 필수 문서·섹션·차단 상태 계산
  ↓
Brief 또는 Charter 작성
  ↓
제품 근거 및 문서 구조 검증
  ↓
Tech Spec 작성·승인
  ↓
기획 + Spec + 현재 repo SHA에서 실행계획 생성
  ↓
Claude/Codex 실행
  ↓
테스트·종료코드·artifact·Git SHA 검증
  ↓
Current 승격 / Work 동결 / 재분류 / 중단
```

초기 20건 정도는 분류 후 항상 사람이 확인하는 shadow mode를 권합니다. 충분한 fixture가 쌓인 뒤 명백한 T0만 자동 확정할 수 있습니다.

### Manifest는 별도 인간 문서로 만들지 않습니다

T1/T2의 루트 문서 frontmatter를 재개 가능한 분류 체크포인트로 사용합니다. T0는 Tech Spec frontmatter에 포함합니다.

```yaml
---
id: feat-20260812-email-auth-a7k2
unit: feature
mode: delivery
facets: [migration]
gates: [data_migration]
status: active
parent: init-20260810-auth-modernization-p3m8

routing:
  policy_version: 0.1.0
  fired_rules:
    - implementation-requires-spec
    - migration-requires-rollback
---
```

기계가 읽지 않는 필드는 추가하지 않는 것이 원칙입니다.

상태는 서로 합치지 않되 작게 유지합니다.

- 문서: `draft | approved | superseded`
- 실행: `planned | active | done | dropped`
- 검증: `unverified | verified | stale`

### SSOT

- 문서 frontmatter와 본문: 제품 의도·결정·관계의 원본
- Git: 변경 이력
- 코드·테스트: 현재 구현 동작
- 배포 시스템: 실제 배포 상태
- 분석 시스템: 실제 지표
- 이슈 시스템: 담당자와 일정

v1에서는 SQLite나 별도 catalog 없이 `rg`와 구조 검증 스크립트로 충분합니다. 문서가 약 100개를 넘거나 저장소 횡단 관계 조회가 반복될 때 frontmatter에서 재생성되는 인덱스를 추가하면 됩니다.

## 5. Claude Code/Codex 구현 가능성 판단

구현 가능합니다. 이 부분에 대한 round‑1의 결론은 유지합니다.

현재 환경에서도 `codex-cli 0.147.0`은 `--output-schema`, `--json`, `--output-last-message`를 제공하고, Claude Code `2.1.227`은 `--print`, `--output-format`, `--json-schema`, `--bare`를 제공합니다.

다만 어댑터는 출력 차이를 흡수해야 합니다.

- Codex의 `--json`은 최종 결과 하나가 아니라 NDJSON 이벤트 스트림입니다. 최종 구조화 결과는 `--output-schema`와 별도 final-output capture를 함께 다루어야 합니다. [공식 OpenAI Codex CLI 문서](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- Claude는 `--output-format json --json-schema` 결과를 `structured_output`에 제공합니다. [Claude Code 공식 문서](https://code.claude.com/docs/en/headless)

따라서 두 CLI의 raw JSON 형식을 같게 만들려 하지 말고, Romeo adapter가 공통 `TaskEnvelope`와 `ResultEnvelope`로 변환해야 합니다.

## 최종 수정 결론

제 원래 권고에서 유지할 것은 다음입니다.

- Policy compiler
- unit/mode/facet 분리
- hard gate
- validation 종류 분리
- runtime-neutral schema
- 현재 SHA 기반 evidence
- 양 런타임 semantic parity fixture

삭제하거나 늦출 것은 다음입니다.

- `P3 Strategy`
- MVP의 SQLite
- 초기 generated catalog
- 10배·100배용 queue/Postgres 설계
- 별도 Manifest 문서
- 아직 소비자가 없는 메타데이터
- 범용적 outcome gate

그리고 반드시 추가할 것은 다음입니다.

- 사람의 분류 확인 지점
- 재분류 경로
- 정책 충돌 우선순위
- 실제 요청 기반 fixture
- shadow-mode 운영
- 하네스 비용·정확도·사용성 지표

현재 최선의 첫 수직 슬라이스는 다음 하나입니다.

> 실제 T1 요청 1건 → 분류 확인 → Feature Brief → Tech Spec → Claude 또는 Codex 구현 → 반대 런타임 검토 → 현재 SHA 검증 → evidence → close

이 한 경로가 두 런타임에서 동일한 의미로 끝나기 전에는 Initiative 자동 분해, 중앙 인덱스, 다중 reviewer, 데이터베이스를 추가하지 않는 것이 가장 안전합니다. 현재 저장소가 아직 [README와 논의 문서 중심](/Users/julliettelee/orca/Romeo-Harness/README.md:1)이므로, 이는 구현 완료 평가가 아니라 검증 가능한 MVP 아키텍처 권고입니다.



---
## Synthesis

*(하이브리드 카운슬 v2. 1차 codex 실행은 gpt-5.3-codex-spark였고(`01-codex-gpt5.3-debate.md`에 보존) 사용자 요청으로 `gpt-5.6-sol`로 재실행한 것이 이 파일이다 — "ultrafast"는 모델 ID가 아니라 서빙 티어로 확인되어 모델만 상향했다. 이 synthesis는 5.6 debate + 로컬 Claude 카운슬 3역할×2라운드(`02-local-council-debate.md`)를 종합한다. 로컬 3인은 같은 모델이므로 로컬 간 합의는 공유 프라이어일 수 있다; Codex와 로컬의 독립 수렴만이 cross-vendor 신호다.)*

### 핵심 사건: cross-vendor 독립 수렴

codex 5.6은 Round 2 자기반박에서 Round 1의 "Policy-Compiled Planning Graph"를 스스로 "**Thin Policy-Compiled Planning Spine**"으로 축소했다. 로컬 카운슬이 서로 비판하며 도달한 최종 합의는 "**얇은 결정론적 척추(Thin Deterministic Spine)**"다. 두 결론은 서로를 전혀 못 본 상태에서 구조·명명까지 수렴했다 — 이번 카운슬 전체에서 가장 강한 신호이며, 권장 아키텍처는 이 둘의 합집합이다.

### Consensus (5.6 재실행 후 cross-vendor 확정)

1. **3-tier planning unit + 축 분리**: T0 Change / T1 Feature / T2 Initiative. Discovery·Experiment는 `mode`, 결제·마이그레이션·GTM 등은 `facet/overlay`, Strategy는 current/의 상시 문서, Project는 일정·예산의 실행 컨테이너(기획 단위 아님).
2. **T0는 별도 기획 문서 없음** — 5.6의 더 날카로운 답: 어차피 필수인 Tech Spec 안에 "Planning Capsule"(문제·범위·AC·위험 몇 줄)로 포함. 스펙조차 없는 잡변경은 커밋 메시지/decisions 한 줄(로컬 안)과 양립.
3. **독립 Manifest 파일 폐기, frontmatter가 분류 기록+재개 체크포인트** — 5.6도 동일 결론 도달 + `policy_version`/`fired_rules` 트레이스 추가로 "왜 이 문서가 생성됐는가"를 재현 가능하게.
4. **LLM 제안 / 인간 확정 / 규칙 강제 3분할** — 5.6의 정밀화: 의미적 사실(payment=true)의 *확정*은 결정론이 아니라 인간·명시 입력의 몫이고, 규칙 엔진은 확정된 값의 *귀결*만 강제한다.
5. **합산 점수 금지 + hard gate + 정책 충돌 우선순위**: gate > 실행 차단 > unit > 필수 overlay > 선택 overlay > 문서·토큰 예산. 필수 gate가 예산을 초과하면 gate 생략이 아니라 예산 초과 경고.
6. **순차 ID 금지 → `type-YYYYMMDD-slug(-entropy)`** (예: feat-20260812-email-auth-a7k2) — entropy 접미로 같은 날 같은 슬러그 병렬 생성(race 워크트리) 충돌까지 차단.
7. **v1 인프라 제로**: catalog/SQLite/큐/Postgres/샤딩 없음, rg+구조 검증 스크립트로 시작. 도입 트리거: 문서 ~100+ 또는 저장소 횡단 조회 반복.
8. **재분류는 정상 경로** (T0→T1→T2 승격, 기록 보존 + 새 분류·이유 기록).
9. **벤더 중립의 정의**: 같은 프롬프트가 아니라 같은 schema·AC·게이트·evidence 계약. 어댑터가 두 CLI의 출력 차이를 TaskEnvelope/ResultEnvelope로 흡수.
10. **픽스처 조기 수집**: 실제 요청 15~20건을 아키텍처보다 먼저 모으고(5.6), 초기 20건은 shadow mode(분류 전수 인간 확인) 운영. 픽스처 진영(5.6+Maintainability+Scalability)이 cross-vendor 다수가 됨 — Simplicity의 "rubric few-shot만" 입장은 소수로.

### 5.3 대비 달라진 것

- 5.3의 PGO(Graph Store·큐 워커·샤딩·2단계 커밋·Ops Adapter)는 로컬 3인이 만장일치 기각했던 부분인데, **5.6은 그 기각 논리를 독립적으로 재생산**했다(Round 1에서 이미 "중앙 DB 불요", Round 2에서 SQLite 캐시마저 자진 철회, "첫 병목은 처리량이 아니라 운영자 주의력·문서 부패·컨텍스트 비용"). 인프라 이견이 소멸했다.
- 5.6의 신규 기여(로컬 토론에 없던 것): 경로 불변 저장(아래), Delivery Map/Executable Plan 분리(상세 실행계획은 Tech Spec 승인 *후* 컴파일 — 설계 변경 시 계획 재작성 방지), validation 5종 분리(intake/product/document/implementation/outcome)와 outcome gate는 측정 가능한 제품 가설에만 적용, 하네스 자체 성공 지표 8종(분류 수정률·gate 누락 수·T0 처리 시간·문서 재독률·중복률·토큰/요청·재분류율), 민감 근거(PII) Git 격리 재확인.

### 새로 닫힌 쟁점: 파일 이동

로컬 합의는 close 시 물리 동결·이동이었고 그래서 링크 표기(slug-ID vs 상대경로+재작성) 이견이 남아 있었다. 5.6의 반례: **"문서는 상태가 바뀌어도 경로를 옮기지 않는다; archive는 폴더가 아니라 metadata 기반 view"**. 이를 채택하면 링크 이견이 통째로 소멸한다 — 파일이 안 움직이면 어떤 링크도 안 깨지고, 재작성 스크립트도 tombstone도 ID resolver도 불필요. 종합 권고: 유닛 폴더는 생성 위치에 영구 고정(생명주기는 status frontmatter), current/는 별도로 *저술*되는 살아있는 사실 문서(승격 = work 파일 이동이 아니라 current 문서 갱신 — GPT 원안·로컬 정의와 이미 일치), archive/ 폴더는 만들지 않는다. 단 이 항목은 로컬 멤버들이 반박 기회를 갖지 못한 5.6 단독 제안임을 명시해 둔다.

### 남은 이견

1. **상태 모델**: 로컬 단일 5상태(draft/active/done/dropped/superseded) vs 5.6 직교 3세트(문서 draft/approved/superseded · 실행 planned/active/done/dropped · 검증 unverified/verified/stale). v1 권고: 단일 5상태로 시작하고, evidence 파이프라인이 실제로 생기면 검증 상태만 분리 추가.
2. **커맨드 수 2 vs 4**: 5.6은 단계 흐름만 기술하고 미판정. 권고 유지: /plan + /plan-close 2개(재분류는 /plan 재실행).
3. **훅 파이프라인**: 로컬 2:1 기각 우세에 5.6도 "핵심 상태 전이를 hook에 의존하지 말라"(Claude hook은 실험적)로 가세 — 사실상 기각.

### Recommendation (최종 권장 아키텍처 — 하나)

**Thin Policy-Compiled Planning Spine** (로컬 "얇은 결정론적 척추" ∪ 5.6 수정안):

- **유닛**: T0 Change(기획 파일 0 — Tech Spec 내 Planning Capsule, 스펙 없는 잡변경은 커밋 메시지) / T1 Feature(Compact Brief 1파일 + Tech Spec) / T2 Initiative(Charter + 자식 Brief들, 마일스톤·Delivery Map은 Charter 섹션). mode(discovery/delivery/experiment)와 facet(payment/privacy/migration/gtm/…)은 별도 축.
- **분류**: LLM이 사실·가정·미확인·분류 후보 추출 → 2질문(blast radius/불확실성)+gate 체크리스트 yes/no를 승인 메시지에 인쇄 → 인간 1클릭 확정 → 정책 테이블이 문서 패키지·차단 상태 계산. gate 시 최소 T1+risk/rollback 강제, 불확실하면 mode=discovery(첫 마일스톤=spike). 초기 20건 shadow mode, 오분류는 픽스처+rubric 예시로 축적.
- **기록**: frontmatter ~7줄(id/unit/mode/facets/gates/status/parent + routing.policy_version·fired_rules)이 분류 기록 겸 재개 체크포인트. 독립 manifest 없음.
- **저장**: 경로 불변(이동 없음). current/(살아있는 사실, 별도 저술) + work/(유닛 폴더, 영구 고정, status로 생명주기) + decisions.md(append-only). archive는 상태이지 폴더가 아님.
- **실행계획**: Delivery Map(Charter 단계, 개략) → Tech Spec 승인 후 Executable Plan(현재 repo SHA + 제약 입력으로 컴파일) → 실행 → 테스트·종료코드·SHA evidence로 close.
- **커맨드 2개**: /plan(재사용 검색→분류→확정→생성; 재실행=재분류) + /plan-close(검증 스크립트: 스키마·링크·미체크 박스·예산 → 상태 확정·current 갱신).
- **배포**: 벤더 중립 코어(SKILL.md 1페이지+템플릿 3+검증 스크립트 1+정책 테이블) + Claude/Codex 얇은 어댑터(공통 TaskEnvelope/ResultEnvelope). 프로젝트별 override 파일 1개. harness/policy version 명기.
- **짓지 않는 것(명명된 트리거 전까지)**: 인덱스/catalog(문서 100+·횡단 조회), 큐/DB(동시 요청자>1), 훅 파이프라인, 물리 archive, 범용 outcome gate.

### 구현 우선순위

0. **실제 요청 픽스처 15~20건 수집** — 아키텍처 확정보다 먼저(5.6: "규칙의 정확도를 검증할 평가 세트가 아키텍처보다 우선").
1. **SKILL.md v1** — tier 정의, 2질문 rubric, gate 8, 정책 충돌 우선순위, 상태·frontmatter·명명 규약, few-shot 자리.
2. **템플릿 3개** — Tech Spec(Planning Capsule 섹션 포함), T1 Brief(선택 섹션), T2 Charter. 길이 캡 명기.
3. **/plan** — 재사용 검색→분류→gate 인쇄→인간 확정→생성. shadow mode로 20건.
4. **/plan-close + 검증 스크립트** — 스키마·링크·미체크박스·예산·open-loop.
5. **수직 슬라이스 1건 관통** — 실제 T1 요청 1건: 분류 확인→Brief→Tech Spec→한 런타임 구현→반대 런타임 검토→SHA evidence→close. 이 경로가 양 런타임에서 같은 의미로 통과하기 전에 확장 금지.
6. **운영 루프** — 지표 관찰(분류 수정률·gate 누락·T0 시간·재독률), 트리거 도달 시 인덱스 등 도입.

### 전원이 같은 이유로 틀릴 수 있는 지점

- 4자 모두 "가볍게"로 수렴 — 축소 편향이 공유 프라이어일 수 있다. 결제·법무가 걸린 대형 Initiative가 실제로 곧 온다면 T2가 얇을 수 있다(그때는 "확장은 싸다" 비대칭에 기대 섹션·폴더를 추가).
- 검토 원문의 코드펜스 7곳(다이어그램)이 유실된 상태로 검토됐다.
- 전원이 "미래 LLM 세션이 주 소비자"를 전제 — 사람 협업자가 생기면 무문서 T0·대화 내 승인은 재검토 대상.
