---
id: decision-register
type: decision_register
status: draft
updated: 2026-08-29
authority: canonical
---

# 결정 등록부

`accepted` 확정 · `superseded` 대체됨 · `open` 미확정 · `conflict` 충돌.

대체된 결정은 지우지 않고 남긴다. 과거 문서를 수정해 없애는 대신 새 결정으로 대체한다. (PHD §5)

인용 키는 [대화 커버리지](../traceability/conversation-coverage.md)를 따른다.

---

## 아키텍처

| ID | 결정 | 상태 | 근거 | 대체 관계 |
| --- | --- | --- | --- | --- |
| D-01 | 하네스는 에이전트 모음이 아니라 요청 분류·절차 선택 **운영 체계**다 | accepted | S23, COUNCIL, S01 | — |
| D-02 | 최종 아키텍처는 **Thin Policy-Compiled Planning Spine** | accepted | COUNCIL Recommendation (cross-vendor 독립 수렴) | D-02a를 대체 |
| D-02a | Policy-Compiled Planning **Graph** (Graph Store·큐·샤딩·Postgres) | superseded | S09 → S10 자기반박, COUNCIL 전원 기각 | D-02로 대체됨 |
| D-03 | planning unit 3개(T0/T1/T2) + mode + facet. Project는 실행 컨테이너, Strategy는 `current/` 상시 문서 | accepted | COUNCIL Consensus 1 | PHD §1 7객체 분류표를 대체 |
| D-04 | T0는 기획 파일 0개. Tech Spec 안 Planning Capsule | accepted | COUNCIL Consensus 2 | "Change Brief + Tech Spec 항상 2파일"을 대체 |
| D-05 | 독립 Manifest 파일 폐기. frontmatter가 분류 기록 겸 재개 체크포인트 | accepted | COUNCIL Consensus 3 | PHD §8 `Planning Package Manifest`를 대체 |
| D-06 | LLM 제안 / 사람 확정 / 규칙 강제 3분할. 의미적 사실의 확정은 결정론이 아니다 | accepted | COUNCIL Consensus 4 | "결정론 엔진이 planning unit 확정"을 대체 |
| D-07 | 합산 점수 금지 + hard gate 8 + 충돌 우선순위 | accepted | COUNCIL Consensus 5 | 합산 점수 T1/T2/T3를 대체 |
| D-08 | ID는 `type-YYYYMMDD-slug-entropy` | accepted | COUNCIL Consensus 6 | 순번 ID(`SPEC-0012`, `FEAT-014`)를 대체 |
| D-09 | 경로 불변. archive는 폴더가 아니라 상태. `current/`는 별도 저술 | accepted | COUNCIL "새로 닫힌 쟁점" | `current/work/archive` 물리 이동을 대체 |
| D-10 | v1 인프라 제로 | accepted | COUNCIL Consensus 7 | SQLite 인덱스·10x/100x 설계를 대체 |
| D-11 | 재분류는 정상 경로 | accepted | COUNCIL Consensus 8 | — |
| D-12 | 벤더 중립 = 같은 schema·AC·게이트·evidence. adapter가 TaskEnvelope/ResultEnvelope로 흡수 | accepted | COUNCIL Consensus 9, S10 §5 | "심볼릭 링크면 변환 버그 0"을 대체 |
| D-13 | fixture 15~20건 수집이 아키텍처 확정보다 우선. 초기 20건 shadow mode | accepted | COUNCIL Consensus 10 | — |
| D-14 | 커맨드 2개: `/plan`, `/plan-close` | accepted | COUNCIL "남은 이견 2" (권고 유지) | — |
| D-15 | 상태 모델 v1은 단일 5상태. 검증 상태는 evidence 파이프라인이 생기면 분리 추가 | accepted | COUNCIL "남은 이견 1" | 직교 3세트 동시 도입을 보류 |
| D-16 | 핵심 상태 전이를 hook에 의존하지 않는다 | accepted | COUNCIL "남은 이견 3", S10 §9 | S01 plan의 SessionStart/PostToolUse/Stop 강제를 대체 |

> D-09는 COUNCIL이 **"5.6 단독 제안이며 로컬 멤버가 반박 기회를 갖지 못했다"**고 명시했다.
> 채택하되 [열린 질문 A-04](../planning/open-questions.md)로 계속 관찰한다.

---

## 경계

| ID | 결정 | 상태 | 근거 |
| --- | --- | --- | --- |
| D-20 | Orca가 실행 상태의 유일한 권위자. 자체 relay·DAG·worktree 폴백 제외 | accepted | S01 KEEL 리뷰, S04 리뷰 #5 |
| D-21 | 하네스 저장소와 프로젝트 산출물 분리. 프로젝트의 전략·결정은 프로젝트가 소유 | accepted | PHD §7 |
| D-22 | 공용 실행환경 계층(머신당 1회)과 프로젝트 계층(저장소당 1회) 분리. `Harness Setup` / `Harness Attach` | accepted | S12 최종 추천 |
| D-23 | OpenWiki는 기획 하네스를 대체할 수 없다. 포크하지 않고 구현 지식 파생 계층으로만 채택 | accepted | S12 최종 판단 |
| D-24 | 파생 문서 갱신은 기준 브랜치 반영 후 1건씩 순차. 기능 워크트리에서는 읽기만 | accepted | S12 |
| D-25 | 승인된 명세는 이미 설계 승인 완료로 취급. 구현 방법론이 제품 기획을 다시 만들지 않는다 | accepted | S12 |
| D-26 | 완료는 코드 검증 + 파생 문서 동기화 둘 다. 문서만 실패하면 `BLOCKED_DOCS` | accepted | S12 상태 11 |
| D-27 | 구현 착수만 승인된 Tech Spec을 선행조건으로 강제한다. 기획·디자인·개발 워크플로우는 그 외에는 독립 호출한다 | accepted | S12 상태2, S02 분석 3, S03 |

---

## 참조 자산

| ID | 결정 | 상태 | 근거 |
| --- | --- | --- | --- |
| D-30 | 전체 포크 금지. 버전 고정 + 선별 채택 + 출처·라이선스 추적 | accepted | S01 plan, S13 |
| D-31 | BMAD는 **기획 자산만** 선별 벤더링하고 안정판 `v6.10.0`에 고정한다. `main` 구조와 혼용 금지 | superseded | S02 분석 1 — **D-55로 대체됨**(벤더링하지 않고 `install`+링크). 버전 고정·`main` 혼용 금지는 유지 |
| D-32 | CIS는 계획 깊이가 아니라 **불확실성 축**이다 (`phase=anytime, required=false`) | accepted | S02 분석 3 |
| D-33 | Superpowers는 승인 이후 개발 규율만 채택. `brainstorming` 강제와 자체 spec 경로 제외 | accepted | S03 |
| D-34 | OMA는 런타임을 설치하지 않고 `.agents` SSOT + adapter compiler 패턴만 재구현 | accepted | S01 plan, S04 |
| D-35 | OMC(oh-my-claudecode)는 Claude 중심이라 공통 베이스에서 제외 | accepted | S04 식별 결론 |
| D-36 | 참조 저장소는 `/repo`로 고정 SHA 한국어 아카이브를 만든 뒤 판정한다 | accepted (구현됨) | `archive/`, S23 |
| D-37 | 디자인은 `DESIGN.md`를 계약으로, 생성 규칙 1개 + 감사 규칙 2개만 채택. taste-skill은 랜딩·브랜드 한정 | accepted (권고) | S13 최종 |
| D-38 | 문서 본문은 한국어, 경로·ID·키·상태값은 영어 | accepted | S01 plan §2 |

---

## 부품 조립 (개정 3, 2026-08-27)

사용자 재정의 "잘 썼던 하네스들을 조립해서 나만의 라우터 체계로"에서 나왔다.
근거 기록: [개정 3 요약](../reviews/2026-08-27-assembly-redefinition/summary.md).

| ID | 결정 | 상태 | 근거 | 대체 관계 |
| --- | --- | --- | --- | --- |
| D-50 | Romeo는 **라우터 + 접착(문서·상태·증거) + 양 런타임 동등성**을 만들고, 기획 facilitation·개발 규율·기술 문서 파생·디자인 규칙·실행은 사용자가 검증한 외부 부품을 **조립**한다. 부품의 자체 제작·원칙 재작성은 기본값이 아니라 강등 경로다 | accepted | S01 사용자 원문("딱 기획 범위까지만 카피"), S12("한 패키지 모듈"), 2026-08-27 사용자 재정의 | 정규화 원칙 2의 "능력 후보 강등"을 라우터·접착에만 한정 |
| D-51 | 채택 방식은 5단계로 명시한다: `install`(설치·연결, 코드 미복사) / `verbatim`(고정 SHA 원문 복사, 수정 0) / `rewrite`(원칙 재작성) / `principle`(참고) / `excluded`. `provenance/imports.yaml`의 `adoption` 값이다 | accepted | 2026-08-27 분석 | 계획 §6의 "전체 도입/일부 재작성/원칙만 참고/제외"를 대체 |
| D-52 | **채택 확정 게이트.** 계획 단계에서는 후보만 기록한다. 어느 파일을 어떻게 가져올지는 해당 마일스톤 진입 시(G-M2 Superpowers, G-M3 BMAD/CIS, G-M6 디자인, G-M7 OpenWiki) 후보표를 제시하고 사용자가 확정한다. 제품 결정(B)이므로 자율 진행하지 않는다 | accepted | 2026-08-27 사용자 요청("해당 구현 단계가 됐을 때 나한테 다시 물어서 구체화") | — |
| D-53 | 부품 부착 완료 조건은 **통합 규약 K-60~K-69** 준수 + 충돌 fixture 3종 PASS + 양 런타임 discovery 프로브다. 규약을 어기는 부품은 `rewrite`로 강등하거나 제외한다 | accepted | 2026-08-27 사용자 요청("충돌하지 않고 하나의 시스템에 녹아드는 것이 가장 중요") | — |
| D-54 | Superpowers는 개발 규율 스킬 세트를 `verbatim` 후보로 둔다. `brainstorming`·`using-superpowers`·bootstrap hook·visual companion 제외(D-33 유지). 본문에 도구명이 없음을 고정 SHA `b36e082` 원문으로 확인했으므로 C-C6 위반이 아니다 | accepted (파일은 D-67에서 확정) | 원문 확인, S03 "거의 그대로 재사용", MIT | D-33을 보완. **도구명 0건 근거는 D-71이 정정**, 파일 목록은 D-67이 확정 |
| D-55 | BMAD 본체·CIS는 벤더링하지 않고 **프로젝트별 `install` + `/plan` 링크**로 조립한다. discovery·T2 판정 시 라우터가 해당 BMAD 스킬을 추천하고 산출물을 입력 링크로 흡수한다. v6.10.0 / CIS v0.2.1 고정은 유지. 사람 대화형이라 parity 비대상이며 Codex 미지원 시 정직 표기 | accepted (후보 — G-M3) | S01 사용자 원문, `~/bmad-ordi`·`~/readly-sologis` 실사용, D-32 | D-31을 대체 |
| D-56 | OpenWiki는 `install`이다(D-23 그대로). 계획 §6의 "원칙만 참고" 라벨은 오기 → "도구 설치·연결, 코드 미복사"로 정정 | accepted | S12 | D-23 표기 정정 |
| D-57 | ui-ux-pro-max는 "제외(보류)"가 아니라 **라이선스 확인 트랙**이다. `cli/`를 제외한 skill/data를 루트 MIT 범위로 채택할 수 있는지 확인한 뒤 G-M6에서 판정한다 | accepted | `~/readly-sologis` 실사용(v2.2.3), K-42 | 계획 §6 "제외(보류)"를 대체 |
| D-58 | `install`·`verbatim`은 코어를 바꾸지 않으므로 채택 게이트 통과를 조건으로 **v1 안에서 허용**한다. `rewrite`·자체 제작·벤더링만 "슬라이스 통과 후"에 둔다. 동등성 게이트는 **부품이 켜진 상태에서** 판정한다 | accepted | 2026-08-27 | v1-scope "이 경로가 통과하기 전에는 BMAD·CIS·디자인·OpenWiki를 시작하지 않는다"를 완화 |

---

## 미확정 / 충돌

이 항목들은 사용자 승인이나 추가 검증 없이 진행하지 않는다.

| ID | 항목 | 상태 | 비고 |
| --- | --- | --- | --- |
| D-40 | GitHub Spec Kit 채택 여부 | **accepted → 비채택, `converge` 개념만 v2 재검토** (2026-08-27 확인) | S12 추천 vs 정본 추천 — 자체 정책표가 이미 더 구체적 |
| D-41 | 저장소 라이선스 | **accepted → Apache-2.0** (2026-08-27) | 아래 "구현 착수 결정" D-41 참조. 파일 교체는 M2 첫 외부 자산 복사 시 |
| D-42 | 하네스 명칭 | open | KEEL(2026-08-04 초안) vs Romeo(현재 저장소) |
| D-43 | 하네스 적용 대상이 코드 프로젝트 전용인지 | **accepted → v1 코드 전용** (2026-08-27) | 비코드 요청은 라우터가 `OUT_OF_SCOPE_NON_CODE` 로 정직 보고. 경량 부착은 v1.1 이후 |
| D-44 | 모델 라우팅 정책 | open | S01은 "역할별 첫 등록 시 승인 후 고정", COUNCIL은 미다룸 |
| D-45 | ECC / claude-multi-agent-architecture 채택 여부 | open | 비교 조사만 되고 채택 결정 미기록 (S13) |

---

## 구현 착수 결정 (2026-08-27, M0 진입 — 계획 §9.2 항목 1~8의 답)

사용자에게 물은 것(제품·안전 결정)과 자율로 정한 것(기술 결정)을 구분해 적는다. 근거 세션: 2026-08-27 M0 착수 대화.

| ID | 결정 | 상태 | 누가 | 근거·비고 |
| --- | --- | --- | --- | --- |
| D-41 | 저장소 라이선스를 **Apache-2.0** 으로 전환한다. 현재 GPL-3.0 은 2026-08-05 초기 커밋에 템플릿으로 들어온 것. `LICENSE` 교체와 `THIRD_PARTY_NOTICES.md` 는 M2 의 첫 외부 자산 복사 직전에 함께 처리한다 | accepted | 사용자 | 계획 §9.2 #1, X-05 |
| D-43 | v1 은 **코드 프로젝트 전용**. 비코드 프로젝트 요청은 `project_kind: non-code` 로 받아 `OUT_OF_SCOPE_NON_CODE` 경고 + 문서 0개로 정직하게 보고한다. 비코드 fixture 2건(S15·S24)은 이 판정이 기대값 | accepted | 사용자 | 계획 §9.2 #5, A-10 |
| D-59 | **깊이 라벨** `profile: quick / standard / deep` 은 정책표의 **출력**이고 unit(T0/T1/T2)은 승인 단위로 유지한다. 카드는 깊이와 그 이유를 먼저, 단위·모드·영역은 한 줄로 보여준다. 규칙은 unit 기본값에서 올리기만 한다 | accepted | 자율(기술) | 계획 §2.4 B1, `core/policy/classification.yaml` profile 절 |
| D-60 | **승인 방식**: 사용자는 Tech Spec 의 `## 확인란`(무엇을·왜·기대 결과·수용 기준·위험과 되돌리기)만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence 가 책임진다. `romeo approve` 는 확인란에 `NEEDS_INPUT` 이 남아 있으면 거부한다. persona(비개발자 PM)를 확정하고 X-02 를 해소한다 | accepted | 사용자 | 계획 §9.2 #2, `~/.codex/AGENTS.md`, 메모리 decision-authority-split |
| D-61 | **상태 계약 구현**: `status` 5값 + `approved_at`·`approved_by`·`base_sha` 사실 필드 + 검증 상태는 저장하지 않고 `romeo close` 가 HEAD SHA·`dirty_tree_hash` 로 계산(D-15 보완). 신선도 계산에서 `.harness/` 와 `docs/work/<unit>/` 는 제외한다 — 기록 행위 자체가 트리를 바꾸기 때문. 대신 evidence 가 spec 해시를 기록해 이후 변경을 경고한다 | accepted | 자율(기술) | 계획 §3.5, F-04, `romeo/evidence.py`·`close.py`, 테스트 4경우 |
| D-62 | **`unit: none`**: 저장소 산출물을 만들지 않는 질문·조사·설명은 기획 단위가 없다 — 문서 0, 카드만 기록. T0/T1/T2 3-tier 는 유지하고 none 은 "단위 없음" 판정이다. 게이트 영역을 읽기만 해도 카드에 주의를 인쇄한다(`UNIT_NONE_WITH_GATE`) | accepted | 자율(기술) | fixture 3건(결제 조회·posthog 보고·설문 답변)이 근거. C-B1 템플릿 폭발 금지 |
| D-63 | **fixture 원천**: 로컬 세션 로그(`~/.claude/projects`, `~/.codex/history.jsonl`, 최근 90일)를 읽기 전용으로 스캔해 사용자가 보낸 메시지 문장만 추출하고 시크릿·URL·이메일·전화번호를 마스킹한 뒤 사용자가 후보를 확정한다(24건 채택). 원본 로그는 수정하지 않는다. 커밋 전 사용자 검토 | accepted | 사용자 | 계획 §9.2 #6, V-0, K-23 |
| D-64 | **부품 선호(Q-07 답)**: CIS 4종이 기획 구체화에 가장 유용 → G-M3 후보표 최우선. BMAD 기획 흐름(PRD 양식)은 "양식이 고정돼 다양한 상황에 부적합" → 후순위. Superpowers·OpenWiki·impeccable·taste·ui-ux-pro-max 는 다른 환경에서 실사용했고 좋았음(메모리의 "사용 흔적 없음" 정정). 사용자가 상상하는 흐름: **CIS(구체화) → Romeo 문서(작업 status 에 따라 자동 갱신) → Superpowers(개발) → OpenWiki(ADR·제품 문서 자동 관리)**; 디자인은 **구현 문서 기반 디자인 시스템 문서 자동 갱신 + 랜딩 같은 창의 작업 시 별도 스킬 로드** | accepted | 사용자 | 2026-08-27 자유 답변. G-M2·G-M3·G-M6·G-M7 후보표 우선순위에 반영 |
| D-65 | **첫 부품**: Superpowers 를 계획대로 G-M2 에서 시험 도입한다(세트 단위라 제거 쉬움, K-69) | accepted | 사용자 | 계획 §7 M2 |
| D-66 | **이번 세션 정지선**: M0+M1 까지. M2 는 G-M2 채택 게이트·라이선스 파일 교체·역할 바인딩 승인이 필요해 사용자가 있는 세션에서 시작한다 | accepted | 사용자 | 계획 §7 |
| D-67 | **G-M2 채택 확정(게이트 닫힘)**: obra/superpowers `b36e082` 중 **규율 코어 7종 14파일만** `verbatim` 채택 — `test-driven-development`·`systematic-debugging`·`verification-before-completion`·`requesting-code-review`(+`code-reviewer.md`)·`receiving-code-review`·`using-git-worktrees`·`finishing-a-development-branch`. `writing-plans`·`executing-plans`·`subagent-driven-development`·`dispatching-parallel-agents` 4종은 **deferred**(rejected 아님, M3 재검토), `brainstorming`·`using-superpowers`·`writing-skills`·visual companion 은 **rejected**. 채택 7종은 나가는 참조가 세트 안에서 닫혀 깨진 링크 0(실측). 6·7번은 override 조건부 — `using-git-worktrees` 는 네이티브 도구 지목을 `orca worktree create` 로, `finishing-a-development-branch` 의 merge/push/worktree 삭제는 `.claude/settings.json` deny 로 덮는다 | accepted | 사용자 | `provenance/imports.yaml`(15항목), 계획 §6·§6.1. D-54·D-65를 구체화 |
| D-68 | **역할 바인딩 확정**: `implementer=claude`, `reviewer=codex`(모델은 계정 기본값, K-12). reviewer 는 런타임 read-only 로 강제하고(`codex -s read-only`) `git status` 비교는 방어 검사로만 둔다. 역할 교체 재실행(implementer=codex·reviewer=claude)으로 parity 를 판정한다 | accepted | 사용자 | 계획 §7 M2 선행 조건, `.harness/bindings.yaml` |
| D-69 | **`writing-plans` 미채택 보상**: 스킬 전체를 들이면 계획 원본이 2개가 되므로(K-61) 채택하지 않되, 원문 `Task Structure` 의 두 규율만 Romeo Tech Spec 에 흡수한다 — **인터페이스 열**(소비 → 생산 시그니처 계약)과 **빈칸 금지 규칙**(`TBD`·"적절한 에러 처리 추가" 류를 `NEEDS_INPUT` 과 동일 취급). 재작성이며 원문 복사가 아니다 | accepted | 사용자 | `core/templates/tech-spec.md`, `provenance/imports.yaml#sp-writing-plans-absorbed` |
| D-70 | **OpenWiki 시점 유지(G-M7)**: 코드→문서 자동 생성은 OpenWiki 가 맡고 M2 에서는 붙이지 않는다. 선행 조건을 추가한다 — OpenWiki 는 `openwiki/` 외에 루트 `AGENTS.md`·`CLAUDE.md` 블록과 `.github/workflows/openwiki-update.yml` 을 건드리는데, 같은 두 파일을 M2 어댑터가 managed block 으로 컴파일한다. **어댑터 마커 규약이 서고 K-68 검증을 통과한 뒤에만** G-M7 을 연다. 문서 3층 분리: 작업 문서=Romeo(`docs/work/<id>/`), 기획=CIS+Romeo, 코드 파생=OpenWiki(D-23 기획 미소유) | accepted | 사용자 | D-64 흐름 유지, `archive/langchain-ai-openwiki/02-workflow-summary.md` §1 |
| D-71 | **사실 정정**: 계획 §6 표의 "고정 SHA `b36e082` 원문에서 본문 도구명 0건 확인"은 **오류다**. 실측 결과 6개 스킬에 도구명·런타임명이 있다 — `requesting-code-review:34`(`general-purpose`), `using-git-worktrees:53,164`(`EnterWorktree`·`WorktreeCreate`), `executing-plans:14`(Claude Code·Codex CLI·Codex App·Copilot CLI·Gemini CLI), `writing-plans:159,165`·`subagent-driven-development:6,506`·`dispatching-parallel-agents:71~73`(`Subagent`·`general-purpose`). C-C6 는 `core/` 에 적용되고 `vendor/` 는 원문 보존이므로 위반은 아니지만, **어댑터 투영 시 이름 치환이 필요**하다는 뜻이다. 채택 7종 중 해당하는 2건은 D-67 의 override 로 처리한다 | accepted | 자율(사실 확인) | 2026-08-27 고정 SHA 원문 grep. D-54 의 근거 일부를 정정 |
| D-72 | **K-60 재정의(진입점 단일 → 기획 진입점 단일)**: 개발 규율 부품(TDD·디버깅·완료 검증·코드리뷰)이 구현 중 런타임에 직접 노출되고 스스로 선택되는 것을 **허용한다** — 그것이 규율을 채택한 이유다. 금지 대상은 부품이 라우터를 대체하는 경로다(자체 bootstrap·세션 시작 주입·"항상 나를 먼저" 규칙·기획 문서 생성·승인 창구 이중화). K-64 의 `superpowers:*` 접두사 요구는 `verbatim`(수정 0)과 양립할 수 없으므로 **논리 id(`sp-*`)는 imports.yaml 이, 런타임 이름은 원문이** 갖는 것으로 정리한다. 이름 충돌은 fixture c3 가 검출한다 | accepted | 사용자 | Codex 독립 리뷰 F-03 이 제기. 2026-08-28 사용자 확정 |
| D-73 | **동등성 게이트의 검토자 면에 산출물 동일성 전제를 넣는다.** 구현자 면(계약·checks·판정)은 지금처럼 비교한다 — 두 구현자가 다른 바이트를 만드는 것은 정상이다. 검토자의 판정은 자기가 본 산출물의 함수이므로 **두 면의 산출물(`head_sha`+`dirty_tree_hash`, 봉투가 지목한 증거에서 읽는다)이 같을 때만** 비교하고, 다르면 `PRODUCT_DIFFERS` 로 분리해 **게이트 판정에서 빼되 '비교 불가' 로 정직하게 인쇄한다.** 관측 케이스의 `expect` 는 고치지 않는다(D-b 유지). 비교할 면이 하나도 남지 않으면 게이트는 미판정이다. 합성 케이스는 면마다 `product:` 를 선언하고 `expect_incomparable:` 로 검사기가 비교 불가를 잡는지 검증한다 — 관측 케이스는 둘 다 인라인으로 선언할 수 없다(구조 오류). **결과:** 2026-08-29 관측 케이스는 구현자 면으로 PASS, 검토자 면은 비교 불가 — 검토자 동등성은 같은 산출물을 두 검토자에게 보인 관측(RUNBOOK §6.6, 미실행)이 있어야 판정된다 | accepted | 사용자 | progress §10 체크리스트 30 이 제기한 세 선택지(정의 수정·구현자 면으로 축소·산출물 동일성 전제) 중 사용자가 셋째를 확정, 2026-08-29. `romeo/parity.py` · `fixtures/parity/pr-product-differs.yaml`·`pr-reviewer-drift.yaml` |
| D-74 | **동등성 게이트의 검토자 면에 재현성 요구를 넣는다.** 판정 역할(역할 계약에 `workspace-write` 가 없는 역할)의 면은 **각 면 2건 이상의 표본**(`results.<역할>.files`)을 요구하고, 그 표본들이 **자기 안에서 일관할 때만** 비교한다. 표본이 모자라면 `VERDICT_UNSAMPLED`, 표본끼리 갈리면 `VERDICT_UNSTABLE` 로 분리해 **게이트 판정에서 빼되 '비교 불가' 로 인쇄한다** — D-73 의 `PRODUCT_DIFFERS` 와 같은 형태다. 진단 순서는 산출물 전제(D-73)가 먼저다 — 산출물이 다르면 표본을 늘려도 비교할 수 없다. 구현자 면에는 이 요구가 없다: 그 면이 묻는 것은 재현성이 아니라 같은 계약에서 같은 검사를 돌려 같은 결론을 냈는가이고, 두 구현자가 다른 바이트를 만드는 것은 정상이다. 관측 케이스의 `expect` 는 고치지 않는다(D-b 유지) — 케이스가 담는 표본을 늘릴 뿐이다. **근거가 된 관측:** 산출물을 고정한 채(계약 sha256 `f79f4bc1…` 네 개 `cmp` identical · 방어 검사 `log_sha256` 열 스냅샷 전부 `2bc7dad48f31…`) codex 검토자 3회 = `PASS`(0) · `FAIL`(1) · `FAIL`(4), claude 검토자 2회 = `FAIL`(6) · `PASS`(8). **두 런타임 다 자기 안에서 흔들린다** — 각 면 1건씩을 비교해 얻은 `VERDICT_DIFFERS` 는 런타임 차이의 증거가 아니다. **결과:** 관측 케이스 `pr-license-field-t1-reviewer-observed` 가 다섯 봉투를 모두 담고 `VERDICT_UNSTABLE` 로 빠진다. 게이트는 `pr-license-field-t1-observed` 의 구현자 면으로 서서 `PASS`(EXIT=0)이고, 뺀 면 2개를 인쇄한다 | accepted | 사용자 | Q-09 의 세 선택지(재현성 요구·검토자 면 영구 제외·현상 유지) 중 사용자가 첫째를 확정, 2026-08-29. `romeo/parity.py` · `fixtures/parity/pr-reviewer-unstable.yaml`·`pr-reviewer-unsampled.yaml` · `.harness/observations.yaml` 의 `reviewer_verdict_reproducibility` |
| D-75 | **종료 검사의 검토 판정은 '현재 산출물에 대한, 지금의 승인으로 낸' 판정만 센다(D-73 의 close 적용).** 검토자의 판정은 자기가 본 산출물의 함수이므로(D-73), close 는 각 검토 봉투가 본 산출물을 **검토 run 자신의 증거**(검토자를 띄운 쪽이 그 run 에 남긴 방어 검사의 `head_sha`+`dirty_tree_hash`)에서 읽고, 봉투의 `evidence_ref` 가 가리킨 산출물이 그것과 같을 때만 판정으로 인정한다(다르면 미검증 — 포인터 문자열 하나로 판정을 옮기는 위조를 설계 검토가 재현했다). 지금 닫는 산출물(검사 기록 run 의 것)과 같고 계약의 `base_sha` 가 담은 승인이 지금의 승인과 같은 판정만 `REVIEW_VERDICT` 에 세고, 다른 산출물·재승인 전 승인의 판정은 PASS 든 FAIL 이든 `REVIEW_SUPERSEDED`(WARN) 로 인쇄하되 **지우지 않는다**(동등성 관측의 표본이다). 종전 D-c('PASS 아닌 판정이 하나라도 남아 있으면 거부')는 낡은 FAIL 봉투를 삭제해야만 close 가 서게 만들었고 그 봉투들은 지울 수 없다 — 이 결정은 D-c 를 '현재 산출물·현재 승인' 으로 좁힌 것이다. D-61 의 `base_sha` 사실 필드도 함께 정정한다: approve 는 base_sha 를 적지 않고 승인 커밋은 이력에서 찾는다(체크리스트 38). **사용자 확정이 필요한 잔여 결정 — 검토 표본 수.** 이 결정만으로는 '검토 룰렛' 이 열린다: 산출물을 사소하게 바꿔 새 run 을 만들고 PASS 가 나올 때까지 검토를 반복할 수 있다(같은 산출물에서 판정이 PASS 2/FAIL 3 으로 갈린 D-74 관측 기준 기대 2~3회). 선택지: (a) **당시 추천 — 채택 안 함(2026-08-29, (b) 확정)** — D-74 를 close 에도 적용해 현재 산출물에 PASS 2건 이상·비-PASS 0건을 요구한다(§6.6 이 이미 런타임당 2건을 만들므로 M2 흐름에서는 추가 비용이 없고, 한 번의 판정은 그 실행의 판정이라는 D-74 의 논리와 같다; 일반 T1 에서는 검토 비용 2배) · (b) 1건으로 두되 `REVIEW_SAMPLE` WARN 과 `REVIEW_SUPERSEDED` 의 findings 요약으로 사람이 보게 한다(지금 구현된 상태) · (c) 낡은 비-PASS 가 있으면 사람이 `--accept-superseded` 로 명시적으로 넘긴다. 구현은 (b) 로 두고 상수 `REVIEW_PASS_SAMPLES=2` 는 경고에만 쓴다. **알려진 경계:** 검토자 면에는 재실행 대조 같은 종점이 없다 — 판정 문자열(`gate_verdict`)은 `romeo review record` 가 검토 run 의 증거에 남기는 sha256 봉인으로만 묶이고, 봉투·증거·원시 로그·해시를 전부 앞뒤 맞게 고치면 뚫린다(로컬 파일의 한계 — progress 「막지 못하는 것」). (a) 의 표본 2건도 그 위조 비용을 2배로 올릴 뿐이다 | **accepted — (b)** 2026-08-29 사용자 확정: 현재 산출물 PASS 1건 + `REVIEW_SAMPLE` WARN 으로 닫는다. 표본 2건은 요구하지 않고, 같은 산출물을 다시 검토해 PASS 를 기다리지 않는다(바뀐 산출물만 새 검토 1건). 근거: 표본을 늘려도 참값이 생기지 않는다(D-74)·D-76 | 하네스(2026-08-29 세션) → 사용자 | 체크리스트 41 의 설계 반박 검토(위조 저항·D-73/D-74 정합·운영 세 렌즈)가 잡은 finding 을 반영. `romeo/close.py` `_check_review`·`_reviewed_product` · `tests/test_docs_evidence_close.py` TestCloseReviewVerdict 의 산출물 시나리오 8건 · impl3 워크트리 실측(낡은 봉투 6건 분리, 현재 산출물 FAIL 4건) |
| D-76 | **M2 완료 정의 개정 — 동등성 게이트는 결정적 요소만 센다. 검토자의 자유 서술 판정은 advisory 다.** 역할 교체 재현의 '동일 게이트 판정'(v1-scope 최소 흐름)은 **결과 봉투 스키마 · 역할 계약(앵커 검사)과 권한 상한 · `required_checks` 의 명령·종료 코드 · 구현자 면의 gate 판정** 으로 한정한다(수용 기준 AC 는 종료 검사 `close` 가 본다 — 동등성 리포트의 항목이 아니다). 판정 역할(검토자)의 면은 스키마·계약·checks 로만 비교하고, 판정과 그 전제(산출물 동일·표본 수·면 내부 일관성)는 리포트에 `advisory` 로 인쇄한다 — 세지 않되 숨기지 않는다(K-51). D-73·D-74 의 결박은 `romeo fixtures parity --judge-verdict strict` 프로파일로 보존한다(Q-10 판정 흔들림 실험용). **함께 확정:** ① impl6 전체 교체 실행은 M2 게이트 조건이 아니다 — 관측 케이스(`pr-license-field-t1-observed`)가 이미 교체 실행의 구현자 면(codex)을 담고 있다. 원하면 1회 선택 실행이며 실패해도 M2 를 막지 않는다 ② close 까지 하네스 코드(`romeo/`·`core/`·`adapters/`)를 동결한다 — 이 결정의 구현(parity 판정 축소)이 마지막 하네스 변경이다 ③ M2 완료와 v1 릴리스 완료를 분리한다(T2 Charter·shadow 20건·attach 는 v1 잔여) ④ 같은 산출물을 다시 검토해 PASS 를 기다리지 않는다 — 바뀐 산출물만 새 검토 1건을 받는다(D-75 (b) 와 같은 논리). **근거가 된 관측:** 같은 산출물·같은 런타임에서도 판정이 흔들렸고(D-74: codex PASS/FAIL/FAIL · claude FAIL/PASS), 그 뒤 게이트 기계가 12시간에 세 번 바뀌며(D-73→D-74→D-75) 검토 실행·봉인이 증식했다. 네 검토 실행이 전부 FAIL 인 산출물로 게이트가 '같음 → PASS' 를 낸 것이 결정적이었다 — 그 게이트는 품질이 아니라 같음을 잰다 | accepted | 사용자(2026-08-29) | 근본 원인 재검토 `docs/reviews/2026-08-29-codex-m2-rootcause-review/README.md` §3 결정 1·3 · `romeo/parity.py` `judge_mode`(`_advisory_face`) · `fixtures/parity/*` `expect_advisory` · `tests/test_parity.py` TestAdvisoryVerdict(419 OK) · `bin/romeo fixtures parity --report` EXIT 0 + 'advisory 면 7' |

---

## 폐기된 아이디어

채택 여부를 다시 논의하지 않기 위해 남긴다. 되살리려면 새 결정이 필요하다.

| 아이디어 | 폐기 사유 | 근거 |
| --- | --- | --- |
| relay v2 (heartbeat·5초 폴링·role swap) | Orca와 책임 중복. 실제 유실이 관찰될 때만 재검토 | S01 KEEL 리뷰, S04 리뷰 #7 |
| 자체 DAG·worktree 폴백 | 두 상태 머신이 충돌 | S04 리뷰 #5 |
| "Codex에는 서브에이전트가 없다" | 사실 오류 | S03 리뷰 #1, S04 리뷰 #1 |
| `.codex/skills` 심링크, `.codex/prompts` workflow | 네이티브 경로가 아니거나 deprecated | S04 리뷰 #2 |
| "심볼릭 링크면 변환 버그 0" | 발견 규칙·trust·상대경로·Windows 차이가 남음 | S03 리뷰 #4 |
| 합산 점수 기반 T1/T2/T3 | 작은 모호한 작업을 과잉 기획 | S02 리뷰 4 |
| Graph Store·큐 워커·샤딩·2단계 커밋 | 전원 기각. 첫 병목이 처리량이 아님 | COUNCIL |
| `P3 Strategy` 프로필 | Strategy는 planning depth가 아니라 상시 문서 | COUNCIL §2 |
| MVP 단계의 SQLite 인덱스 | 자진 철회 | COUNCIL |
| 독립 Manifest 문서 | frontmatter로 충분 | COUNCIL Consensus 3 |
| 물리적 archive 폴더 이동 | 링크가 깨지고 병렬 브랜치 충돌 증가 | COUNCIL |
| 범용 outcome gate | 내부 리팩터링에서 인위적 지표를 만들게 됨 | COUNCIL |
| `binds.code` 변경만으로 문서 자동 `drifted` 강등 | 경로 변경이 의미 변경을 뜻하지 않음. 경고까지만 | S01 KEEL 리뷰, S04 리뷰 #8 |
| 참고 저장소를 "능력 후보"로만 취급하고 원칙 재작성을 기본값으로 삼기 | 실사용 검증된 흐름을 탈락시키고 사용자 요구("카피하고 싶다", "한 패키지")를 강등함. 재작성은 통합 규약을 못 지킬 때의 강등 경로로만 | 2026-08-27 사용자 재정의, D-50·D-51 |
| 계획 단계에서 채택 파일 목록을 확정하기 | 제품 결정을 구현 세션이 즉흥 판단하게 됨. 마일스톤 진입 시 게이트에서 사용자가 확정 | D-52 |
