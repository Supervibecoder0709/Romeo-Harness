---
id: decision-register
type: decision_register
status: draft
updated: 2026-08-27
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
| D-54 | Superpowers는 개발 규율 스킬 세트를 `verbatim` 후보로 둔다. `brainstorming`·`using-superpowers`·bootstrap hook·visual companion 제외(D-33 유지). 본문에 도구명이 없음을 고정 SHA `b36e082` 원문으로 확인했으므로 C-C6 위반이 아니다 | accepted (후보 — 파일 확정은 G-M2) | 원문 확인, S03 "거의 그대로 재사용", MIT | D-33을 보완 |
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
