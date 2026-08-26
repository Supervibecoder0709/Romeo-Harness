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
| D-31 | BMAD는 **기획 자산만** 선별 벤더링하고 안정판 `v6.10.0`에 고정한다. `main` 구조와 혼용 금지 | accepted | S02 분석 1 |
| D-32 | CIS는 계획 깊이가 아니라 **불확실성 축**이다 (`phase=anytime, required=false`) | accepted | S02 분석 3 |
| D-33 | Superpowers는 승인 이후 개발 규율만 채택. `brainstorming` 강제와 자체 spec 경로 제외 | accepted | S03 |
| D-34 | OMA는 런타임을 설치하지 않고 `.agents` SSOT + adapter compiler 패턴만 재구현 | accepted | S01 plan, S04 |
| D-35 | OMC(oh-my-claudecode)는 Claude 중심이라 공통 베이스에서 제외 | accepted | S04 식별 결론 |
| D-36 | 참조 저장소는 `/repo`로 고정 SHA 한국어 아카이브를 만든 뒤 판정한다 | accepted (구현됨) | `archive/`, S23 |
| D-37 | 디자인은 `DESIGN.md`를 계약으로, 생성 규칙 1개 + 감사 규칙 2개만 채택. taste-skill은 랜딩·브랜드 한정 | accepted (권고) | S13 최종 |
| D-38 | 문서 본문은 한국어, 경로·ID·키·상태값은 영어 | accepted | S01 plan §2 |

---

## 미확정 / 충돌

이 항목들은 사용자 승인이나 추가 검증 없이 진행하지 않는다.

| ID | 항목 | 상태 | 비고 |
| --- | --- | --- | --- |
| D-40 | GitHub Spec Kit 채택 여부 | open | S12에서 "기획 하네스에 가장 가까운 1순위"로 추천됐으나 이후 council·저장소에 반영 없음. `archive/`에도 없음 |
| D-41 | 저장소 라이선스 | conflict | S05 권고 Apache-2.0 vs 실물 GPL-3.0 |
| D-42 | 하네스 명칭 | open | KEEL(2026-08-04 초안) vs Romeo(현재 저장소) |
| D-43 | 하네스 적용 대상이 코드 프로젝트 전용인지 | open | S15(면접 준비)·S24(커머스 운영)에서 경량 적용 사례 존재 |
| D-44 | 모델 라우팅 정책 | open | S01은 "역할별 첫 등록 시 승인 후 고정", COUNCIL은 미다룸 |
| D-45 | ECC / claude-multi-agent-architecture 채택 여부 | open | 비교 조사만 되고 채택 결정 미기록 (S13) |

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
