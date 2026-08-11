기획 하네스를 만들기 위해 몇가지 질문이 있어. 내가 오랜시간 product manager로 일하다보니, 모든 기획에 다 동일한 포맷의 기획서가 필요하지 않다는 걸 알게됐어. 어떤 상황에서는 아주 작은 아이디어만으로 구현 가능한 계획들도 있었고, 대부분의 경우에 스펙 작성 문서는 항상 필요했지만, 큰 아이디어들은 전체 유저스토리와  validation, 전략 일치도, 목표, Acceptance criteria 등 모두 상세하게 적을 필요가 있었거든.  내가 작성하는 PRD도 그래서 매번 달라졌어. 그리고 어떤 때는 기능 단위로 prd를 쓸 때도 있고, 프로젝트 단위로 큰 PRD를 하나 마련한 다음 마일스톤에 따라서 구현 계획서를 하위에 별도로 두는 경우도 있었어.   그런데 이제 기획 하네스를 만들고나서는, 내가 요청하는 첫 사항에 대해 특정 기준을 가지고 해당 기획의 볼륨,난이도,크기 등을 분류하고, 그것에 맞는 문서 양식을 작성해서 -&gt; 또 그것에 어울리는 실행계획을 세우는 워크플로우를 실행해보려해.   1. 위 경우에 기획을 분류하는 기준을 어떻게 가져가면 좋을까? 2. 기획 분류 기준에 따라 그것을 구현하기 위한 문서 양식이 달라져야 한다는 점에 동의해? 3. 한 프로젝트에서, 기획 문서의 레이어 계층을 어떻게 구분하면 좋을까?    1. 넓은 범위에서, 기술 문서도 포함될 수 있고, 시장 방향에 대한 전략 및 마케팅 실행법    2. 그리고 유저 리서치까지 포함할 수도 있어.     3. 가능한 넓은 경우의 수를 가지고 문서 레이어를 어떻게 관리하면 좋을지 알려줘.   참고로 기획의 레벨과 무관하게 그것을 실행할 때는 반드시 기술 스펙을 작성해야 하고, 별도의 고정된 개발 방법론을 이용해 개발하는 워크플로우를 만들 거니 신경쓰지 않아도 돼.  내가 정말 궁금한 건 이렇게 나온 기획 산출물들, 기술 계획서들을 어떻게 저장하고 관리하는 게 좋을지 개념적으로 이해하고 싶은 거야.

7m 22s 동안 처리함

결론부터 말하면, 방향에 동의합니다. 다만 하네스의 중심을 **“기획 규모에 따라 PRD 템플릿을 고르는 시스템”**으로 두면 곧 한계가 옵니다.

제가 추천하는 구조는 다음입니다.

> 첫 요청 분석  
> → 무엇을 기획하는지 분류  
> → 불확실성·영향·위험·조율 난이도 평가  
> → 필요한 문서 묶음 자동 조립  
> → 기술 스펙 및 실행계획 연결  
> → 출시·검증 후 현재 문서와 기록 문서 분리

핵심은 `Small / Medium / Large`가 아니라 **작업 유형 × 기획 강도 × 위험 오버레이**입니다.

---

## 1. 기획은 어떤 기준으로 분류해야 하는가

### 먼저 “크기”가 아니라 기획 객체를 판별해야 합니다

같은 “기능 요청”처럼 보여도 실제로는 전혀 다른 종류의 기획일 수 있습니다.


| 기획 객체판별 기준기본 산출물       |                         |                                    |
| ---------------------- | ----------------------- | ---------------------------------- |
| Change                 | 기존 동작의 국소적인 변경          | Change Brief                       |
| Feature                | 하나의 사용자 문제를 종단 간 해결     | Feature PRD                        |
| Discovery / Experiment | 구현보다 학습과 의사결정이 목적       | Discovery·Experiment Brief         |
| Initiative             | 여러 기능·정책·채널이 하나의 성과를 만듦 | Initiative Charter                 |
| Product / Strategy     | 제품·시장·고객에 대한 장기 방향 결정   | Product Strategy                   |
| GTM / Operation        | 출시, 마케팅, 운영 절차, 정책 변경   | GTM·Operations Plan                |
| Platform / Migration   | 사용자 기능보다 시스템·데이터 전환이 중심 | Change Brief 또는 Initiative Charter |


예를 들어:

- “설정 화면의 버튼 문구 변경”은 `Change`
- “알림 설정 기능 추가”는 `Feature`
- “온보딩 단계를 줄이면 전환율이 오르는지 확인”은 `Experiment`
- “무료 사용자를 유료로 전환시키는 요금제 도입”은 가격·결제·권한·마케팅이 함께 움직이는 `Initiative`
- “태국 작가 시장 진출”은 `Product Strategy + Discovery + Initiative`
- “인증 시스템 교체”는 제품 기획은 얇고 기술·운영 리스크가 큰 `Platform / Migration`

이 단계에서부터 `Project PRD`라는 모호한 이름은 가능한 한 피하는 편이 좋습니다. 프로젝트가 제품 전체를 뜻하는지, 특정 Initiative를 뜻하는지, 단순한 실행 기간을 뜻하는지 사람마다 다르기 때문입니다.

---

### 그다음 기획 강도를 다섯 축으로 평가합니다


|                             |                                      |                              |
| --------------------------- | ------------------------------------ | ---------------------------- |
| 평가 축하네스가 물어야 할 질문문서에 미치는 영향 |                                      |                              |
| Scope                       | 몇 개의 사용자 여정·제품 영역·채널을 변경하는가?         | 넓으면 상위 문서와 하위 Feature 문서를 분리 |
| Uncertainty                 | 문제·고객가치·시장·해결책 중 무엇이 불명확한가?          | 높으면 PRD보다 Discovery를 먼저 수행   |
| Impact                      | 실패하거나 성공했을 때 사용자·매출·전략에 얼마나 영향을 주는가? | 목표·지표·가드레일·사후검증 강화           |
| Risk / Reversibility        | 쉽게 되돌릴 수 있는가? 법무·돈·데이터 문제가 있는가?      | 승인·감사·롤백·마이그레이션 문서 추가        |
| Coordination                | 몇 개 팀·시스템·외부 업체가 관여하는가?              | 이해관계자·의존성·마일스톤·출시조정 추가       |


여기에 두 가지 보조값을 기록하면 좋습니다.

- `evidence_confidence`: 현재 판단을 뒷받침하는 근거가 얼마나 충분한가
- `appetite`: 이 아이디어에 최대 어느 정도의 시간·비용을 투자할 의향이 있는가

`appetite`는 개발 예상 공수가 아니라 “이 문제가 이 정도 투자를 받을 가치가 있는가”라는 제품 판단입니다. Basecamp의 Shape Up도 문제·해결책뿐 아니라 투자 한도를 먼저 정해 솔루션 범위를 제한합니다. [Basecamp의 Pitch 구성](https://basecamp.com/shapeup/1.5-chapter-06?utm_source=chatgpt.com)

### 이 값들은 합산 점수로 만들지 않는 것이 중요합니다

`총점 12점이므로 Large PRD` 같은 방식은 권하지 않습니다.

축마다 역할이 다르기 때문입니다.

- 불확실성이 높다 → Discovery를 먼저 한다.
- 범위가 넓다 → Initiative와 Feature로 문서를 나눈다.
- 영향이 크다 → 전략 연결과 성과 측정을 강화한다.
- 위험이 높다 → 승인·롤백·감사 문서를 강제한다.
- 조율이 복잡하다 → 의존성과 마일스톤 문서를 추가한다.

다음 항목들은 합산 점수와 관계없이 **Hard Gate**로 처리해야 합니다.

- 결제·정산·가격
- 개인정보·보안·권한
- 법무·규제·약관
- 운영 데이터 삭제
- 데이터 마이그레이션
- 외부 공개 API
- 되돌리기 어려운 정책 변경
- 서비스 중단 가능성

버튼 문구 한 줄이라도 결제 약관에 관련되면 기획 강도가 올라가야 합니다. 반대로 코드 전체를 리팩터링하더라도 사용자 동작과 제품 정책이 그대로라면 제품 PRD는 얇아도 됩니다.

이 때문에 **제품 기획 강도와 기술 구현 강도는 반드시 별도로 분류**해야 합니다. 사용자가 정한 “모든 구현에 기술 스펙을 작성한다”는 원칙과도 잘 맞습니다.

---

## 2. 분류에 따라 문서 양식이 달라져야 하는가

동의합니다. 다만 독립된 PRD 템플릿을 계속 추가하는 방식은 추천하지 않습니다.

가장 좋은 구조는 다음입니다.

> 공통 코어 문서
>
> - 작업 유형별 기본 모듈
> - 조건에 따라 붙는 오버레이 모듈

### 모든 구현 기획에 공통으로 들어갈 최소 코어

- 배경과 문제
- 대상 사용자와 사용 상황
- 기대하는 사용자·사업 결과
- 범위와 비범위
- Acceptance Criteria 또는 의사결정 기준
- 주요 가정과 열린 질문
- 문서 오너와 상태
- 상위 목표·근거·관련 문서
- 기술 스펙 링크

그 위에 필요한 모듈만 추가합니다.


|               |                                   |
| ------------- | --------------------------------- |
| 조건추가할 모듈      |                                   |
| 문제·시장 불확실성 높음 | Discovery / Research / Validation |
| 실험이 목적        | Hypothesis / Experiment Design    |
| 핵심 지표에 영향     | Measurement / Analytics           |
| 여러 사용자 흐름 변경  | Journey / Story Map               |
| 결제·개인정보·법무    | Risk / Approval / Compliance      |
| 기존 사용자·데이터 전환 | Migration / Rollback              |
| 여러 팀·시스템 참여   | Dependency / Stakeholder          |
| 외부 출시         | GTM / Launch                      |
| 운영 절차 변경      | Support / Operations              |
| 장기간 영향을 주는 결정 | Product Decision Record / ADR     |


문제가 충분히 검증되지 않았다면 상세 PRD를 크게 작성하는 것이 아니라, Discovery 문서로 먼저 라우팅해야 합니다. GOV.UK의 서비스 개발 방식도 Discovery의 목적을 “무엇을 만들지 상세화”가 아니라 사용자·제약·문제를 파악하고 다음 단계로 진행할지 결정하는 것으로 구분합니다. [GOV.UK Discovery 가이드](https://www.gov.uk/service-manual/agile-delivery/how-the-discovery-phase-works?utm_source=chatgpt.com)

### 추천 문서 패키지


|                      |                                                      |
| -------------------- | ---------------------------------------------------- |
| 분류기본 패키지             |                                                      |
| Change               | Change Brief + Tech Spec                             |
| Feature              | Feature PRD + Tech Spec                              |
| Experiment           | Experiment Brief + Measurement Plan + 필요 시 Tech Spec |
| Initiative           | Initiative Charter + 하위 Feature PRD들 + Tech Spec들    |
| Product / Strategy   | Product Strategy + Research + Initiative Map         |
| Platform / Migration | 얇은 Product Brief + Tech Spec + Migration·Rollback    |
| GTM / Operation      | GTM·Operations Brief + 제품 변경이 있으면 관련 PRD             |


기존 방식 중 “큰 PRD 하나와 마일스톤별 구현계획”도 여전히 유효합니다. 다만 역할을 명확히 해야 합니다.

- `Initiative Charter`는 왜 하는지, 어떤 성과를 원하는지, 무엇을 하지 않는지를 소유합니다.
- `Feature PRD`는 사용자 행동, 비즈니스 규칙, 예외 상태, Acceptance Criteria를 소유합니다.
- `Milestone Plan`은 구현 순서, 의존성, 컷라인, 검증 시점을 소유합니다.
- `Tech Spec`은 구현 방식과 기술적 계약을 소유합니다.

마일스톤 계획서는 하위 PRD 내용을 복사한 또 다른 PRD가 아닙니다.

하나의 문서로 합쳐도 되는 조건은 다음과 같습니다.

- 단일 사용자 문제
- 단일 오너
- 단일 출시
- 단일 성공지표
- 하나의 의사결정으로 종료

다음 중 하나라도 나타나면 분리하는 편이 좋습니다.

- 독립적으로 배포할 수 있다.
- 오너나 승인자가 다르다.
- 대상 사용자나 성공지표가 다르다.
- 여러 마일스톤에 걸친다.
- 병렬로 개발된다.
- 별도 법무·보안·운영 검토가 필요하다.

실제로 성숙한 기술 프로젝트도 모든 변경에 동일한 절차를 적용하지 않습니다. Rust는 일반적인 변경, 주요 변경 제안, 더 무겁고 논쟁적인 RFC 절차를 구분합니다. [Rust의 Major Change Process](https://rust-lang.github.io/rfcs/2904-compiler-major-change-process.html?utm_source=chatgpt.com)

---

## 3. 한 프로젝트 안에서 문서 레이어는 어떻게 구분해야 하는가

문서 체계를 하나의 폴더 트리로만 보면 안 됩니다. 다음 세 축을 따로 봐야 합니다.


|       |                                                              |
| ----- | ------------------------------------------------------------ |
| 축구조   |                                                              |
| 범위    | Product → Initiative → Feature / Change → Task               |
| 문서 성격 | Strategy / Evidence / Product / Technical / GTM / Operations |
| 생명주기  | Discovery → Decision → Delivery → Launch → Outcome           |


전략·리서치·마케팅·기술은 단순한 부모·자식 관계가 아닙니다.

```

```

예를 들어 하나의 사용자 인사이트가 여러 Initiative를 뒷받침할 수 있고, 하나의 ADR이 여러 Feature에 영향을 줄 수 있습니다. GTM 계획은 Feature 아래가 아니라 Initiative 또는 Release와 병렬로 연결되는 경우가 많습니다.

따라서 폴더는 사람이 찾기 쉬운 기본 경로만 제공하고, 실제 관계는 `문서 ID + 메타데이터 + 링크`가 담당해야 합니다.

### 범위 계층의 추천 명칭


|                     |                                  |                         |
| ------------------- | -------------------------------- | ----------------------- |
| 범위추천 문서이 문서가 소유할 내용 |                                  |                         |
| Product             | Product Brief / Product Strategy | 시장, 고객, 가치제안, 전략, 제품 원칙 |
| Objective / Bet     | Goal / Strategic Bet             | 달성하려는 결과와 투자 기준         |
| Initiative          | Initiative Charter               | 문제, 성과, 범위, 가드레일, 하위 작업 |
| Milestone / Release | Milestone·Release Plan           | 순서, 의존성, 컷라인, 출시조건      |
| Feature             | Feature PRD                      | 사용자 동작, 요구사항, AC        |
| Change              | Change Brief                     | 국소 변경의 이유·범위·검증         |
| Task                | Issue / Ticket                   | 담당자, 일정, 실행 상태          |


`Task`는 장기 기획 문서가 아닙니다. 실행이 끝났다고 모든 Issue를 지식 문서로 승격시켜서는 안 됩니다.

---

## 4. 실제 저장은 “현재 상태”와 “변경 기록”을 분리해야 합니다

장기적으로 가장 중요한 구분입니다.

PRD를 계속 최신 제품 설명서처럼 덮어쓰면 당시 왜 그런 결정을 했는지가 사라집니다. 반대로 출시 PRD만 보존하면 현재 제품이 어떻게 동작하는지 오래된 PRD 수십 개를 뒤져야 합니다.

그래서 다음 구조를 추천합니다.

```

```

```
PROJECT_MAP.md
DECISIONS.md
INFRASTRUCTURE.md
OPERATIONS.md
TROUBLESHOOTING.md

docs/
├── _system/
│   ├── document-policy.md
│   ├── catalog.yaml
│   ├── glossary.md
│   └── templates/
│
├── current/
│   ├── strategy/
│   ├── product/
│   ├── engineering/
│   ├── go-to-market/
│   └── operations/
│
├── work/
│   └── INIT-001-example/
│       ├── README.md
│       ├── charter.md
│       ├── features/
│       ├── engineering/
│       ├── milestones/
│       ├── gtm/
│       └── validation/
│
├── evidence/
│   ├── studies/
│   ├── insights/
│   ├── market/
│   └── experiments/
│
├── decisions/
│   ├── product/
│   └── architecture/
│
├── releases/
└── archive/
```

기존에 사용하려는 루트 문서들은 긴 내용을 모두 담는 파일보다 진입점 역할로 두면 좋습니다.

- `PROJECT_MAP.md`: 전체 구조와 현재 활성 Initiative
- `DECISIONS.md`: Product Decision과 ADR 인덱스
- `INFRASTRUCTURE.md`: 현재 인프라의 요약과 상세 문서 링크
- `OPERATIONS.md`: 운영·배포·백업·장애 대응 인덱스
- `TROUBLESHOOTING.md`: 문제와 진단·해결 이력

### 각 저장 영역의 시간적 성격


|              |                          |                   |
| ------------ | ------------------------ | ----------------- |
| 영역의미변경 원칙    |                          |                   |
| `current/`   | 현재 유효한 전략·제품 동작·아키텍처·운영법 | 계속 갱신             |
| `work/`      | 특정 시점의 변경 의도와 실행 문서      | 종료 후 동결           |
| `evidence/`  | 인터뷰·데이터·시장조사·실험 근거       | 원본은 보존, 해석은 버전 관리 |
| `decisions/` | 무엇을 왜 결정했는지              | 덮어쓰지 않고 Supersede |
| `releases/`  | 실제 출시와 검증 기록             | 종료 후 보존           |
| `archive/`   | 중단·폐기·대체된 작업             | 삭제하지 않고 사유 보존     |


출시가 끝난 PRD는 당시 변경 의도를 설명하는 기록으로 동결하고, 장기적으로 참조해야 하는 내용만 `current/product/`에 반영합니다.

예를 들어:

- 신규 가격 정책 → `current/product/policies/` 또는 `current/strategy/pricing/`로 승격
- 특정 캠페인 문구 → Initiative의 GTM 기록에 보존
- 여러 기능에서 쓰는 인증 규칙 → `current/product/`와 `current/engineering/`에 반영
- 일회성 UI 배치 결정 → 굳이 Current 문서로 승격하지 않음

즉, 모든 출시 기능을 다시 현재 문서로 복제하는 것이 아니라 **다른 작업이 앞으로 다시 참조해야 하는 공통 사실만 승격**합니다.

---

## 5. 문서는 폴더보다 ID와 관계가 중요합니다

본문은 Markdown으로 작성하고, 하네스가 읽어야 하는 정보는 YAML frontmatter로 관리하는 방식이 적합합니다.

```

```

```
---
id: FEAT-014
type: feature_prd
title: 이메일 인증 개선

doc_status: approved
work_status: active

owner: product
parent: INIT-003
supports:
  - GOAL-002
informed_by:
  - INSIGHT-008
related_specs:
  - SPEC-021
target_release: REL-005

last_reviewed: 2026-08-05
supersedes:
---
```

특히 `doc_status`와 `work_status`를 분리하는 것이 중요합니다.

- PRD 문서는 승인됐지만 개발은 시작되지 않을 수 있습니다.
- 기능은 출시됐지만 성과 측정은 끝나지 않을 수 있습니다.
- 문서가 대체됐지만 실제 제품은 아직 이전 버전일 수 있습니다.

추천 상태는 다음과 같습니다.

```

```

```
문서 상태:
draft → in_review → approved → superseded / archived

작업 상태:
idea → triaged → discovery → ready → active
→ released → measured → closed
```

종결 상태도 구분해야 합니다.

- `completed`: 구현과 결과 확인 완료
- `superseded`: 새 문서나 결정이 대체
- `abandoned`: 전략·근거·비용 문제로 중단
- `archived`: 활성 관리 대상에서 제외

`Released`는 완료가 아닙니다. 실제 동작 확인과 결과 측정, 또는 측정하지 못한 이유와 후속 결정까지 기록되어야 닫을 수 있습니다.

중요한 결정은 과거 문서를 수정해 없애지 말고 새 결정으로 대체해야 합니다. AWS의 ADR 지침도 이전 결정을 `Superseded`로 표시하고 이력과 대체 관계를 보존하며, 중앙 Git 저장소나 위키에서 관리할 것을 권장합니다. [AWS ADR 관리 원칙](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/best-practices.html?utm_source=chatgpt.com)

---

## 6. 모든 것을 같은 저장소의 같은 문서 체계에 넣지는 않아야 합니다

SSOT는 “프로젝트에 문서가 딱 하나 있어야 한다”는 뜻이 아닙니다.

> 각각의 사실·결정·상태마다 기준이 되는 장소가 하나여야 한다는 뜻입니다.


|                   |                              |
| ----------------- | ---------------------------- |
| 정보기준 저장소          |                              |
| 제품 방향·현재 정책·요구사항  | Git 기반 기획 문서                 |
| 변경 제안과 결정 이유      | PRD·Decision Record·ADR      |
| 작업 담당자·일정·진행 상태   | Linear·ClickUp·GitHub Issues |
| 실제 구현 상태          | 코드와 PR                       |
| 실제 배포 상태          | 배포 플랫폼                       |
| 실제 지표 값           | 분석·데이터 시스템                   |
| 인터뷰 원본·녹취·개인정보    | 접근통제된 Drive·리서치 저장소          |
| 리서치에서 도출한 Insight | Git의 Evidence 문서             |


같은 내용을 여러 PRD에 복사하기보다 기준 문서에 링크해야 합니다. GitLab의 문서 관리 원칙도 중복된 내용을 여러 위치에 유지하지 않고 하나의 기준 문서에 연결하는 방식을 권장합니다. [GitLab 문서 구조와 SSOT 원칙](https://docs.gitlab.com/development/documentation/site_architecture/folder_structure/?utm_source=chatgpt.com)

특히 사용자 리서치 원본에는 개인정보가 들어갈 수 있으므로 Git 저장소에는 다음만 두는 편이 안전합니다.

- 연구 ID
- 연구 목적
- 요약된 Insight
- 근거 수준
- 수행 날짜
- 원본 저장 위치 링크
- 접근 권한 책임자

---

## 7. 하네스 저장소와 프로젝트 산출물도 분리해야 합니다

공통 하네스 저장소에는 다음만 들어가는 것이 좋습니다.

```

```

```
planning-harness/
├── routing-rules/
├── schemas/
├── templates/
├── overlays/
├── lifecycle-rules/
└── validators/
```

실제 프로젝트에서 생성된 기획 산출물은 각 프로젝트가 소유해야 합니다.

```

```

```
actual-project/
├── PROJECT_MAP.md
├── docs/
└── source-code/
```

하네스는 기획 문서를 생성하고 검사하지만, 프로젝트의 전략과 결정 자체를 소유하지 않습니다. 그래야 하네스 버전을 바꾸거나 Claude와 Codex를 교체해도 프로젝트 지식이 종속되지 않습니다.

단일 코드베이스 프로젝트라면 `docs/`를 코드와 같은 저장소에 두는 것을 우선 추천합니다. 제품이 여러 코드 저장소로 나뉘면:

- 중앙 Product Docs 저장소: 전략·리서치·Initiative·제품 정책
- 각 코드 저장소: 해당 코드에 가까운 Tech Spec·Architecture
- stable ID로 서로 연결

구조가 적합합니다.

---

## 8. 최종적으로 하네스가 출력해야 하는 것

하네스의 첫 결과물은 PRD 본문이 아니라 다음과 같은 `Planning Package Manifest`가 되어야 합니다.

```

```

```
classification:
  artifact_nature: change_proposal
  object: initiative

  planning_depth:
    scope: high
    uncertainty: high
    impact: high
    reversibility: medium
    coordination: high

  evidence_confidence: low
  hard_gates:
    - payment
    - legal

package:
  create_now:
    - discovery_brief
    - pricing_research
    - initiative_charter
    - validation_plan

  create_after_validation:
    - feature_prds
    - gtm_plan
    - technical_specs

  required_overlays:
    - analytics
    - legal_review
    - rollout_and_rollback

  omitted:
    - migration_plan

relations:
  parent: PRODUCT-001
  supports:
    - GOAL-003

promotion_conditions:
  - 가격 수용성 가설 검증
  - 핵심 결제 정책 확정
  - 성공지표와 중단 기준 승인
```

그다음 하네스가:

1. 기존 문서 카탈로그를 확인하고
2. 새 문서가 필요한지 기존 문서를 수정해야 하는지 판단하고
3. 필요한 문서만 생성하고
4. 상위·하위 문서를 연결하고
5. 기술 스펙과 실행계획을 연결하고
6. 출시 후 실제 결과를 검증하고
7. Current 문서 갱신과 Archive까지 수행

하도록 만드는 것이 좋습니다.

한 문장으로 정리하면 다음과 같습니다.

> 기획 하네스는 구현량에 맞춰 문서 길이를 고르는 시스템이 아니라, 의사결정의 종류·불확실성·영향·위험·조율 비용에 비례해 최소한의 충분한 문서 묶음을 만들고, 그 문서가 현재 사실인지 변경 제안인지 증거인지 실행 기록인지 구분해 보존하는 시스템이어야 합니다.

