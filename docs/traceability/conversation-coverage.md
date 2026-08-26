---
id: conversation-coverage
type: traceability
status: draft
updated: 2026-08-27
authority: derived
---

# 대화 커버리지

원천: [`docs/source-context/project-conversations-compressed-2026-08-27/`](../source-context/project-conversations-compressed-2026-08-27/) (세션 25건)

무결성: 커밋 시점에 `shasum -a 256 -c SHA256SUMS` → 28/28 OK.

## 인용 키

| 키 | 대상 |
| --- | --- |
| `S01`~`S25` | `transcripts/NN_...md` (`INDEX.md` 번호) |
| `COUNCIL` | [`docs/council/03-codex-gpt5.6-debate-and-final-synthesis.md`](../council/03-codex-gpt5.6-debate-and-final-synthesis.md) |
| `PHD` | [`docs/planning-harness-discussion.md`](../planning-harness-discussion.md) |
| `AGENTS-P` | 모든 transcript에 반복 포함된 사용자 상시 persona 지시문 |

`S01`·`S02`·`S03`·`S04`는 같은 세션(`019fcd2e`)의 메인/서브 분기다.

---

## 1차 근거 — 하네스 요구의 출처 (11건)

| # | 날짜 | 무엇이 나왔나 | 반영 위치 | 현행성 |
| --- | --- | --- | --- | --- |
| S01 | 08-04 / 08-05 | 최초 요구 원문(기획·개발·디자인·룰·자기학습), `proposed_plan` 전문, KEEL 초안 리뷰, "처음부터 구축하는 순서", v0.1 완료 기준 | brief, capability-map 전 영역, D-20~D-38, v1-scope | **부분 유효**. 요구 원문은 유효, plan의 실행 구조 상당수는 COUNCIL이 대체 |
| S02 | 08-04 / 08-05 | BMAD `v6.10.0` vs `main` 구조 차이, CIS는 anytime·optional, `module.yaml`·`module-help.csv`·`customize.toml`·memlog 패턴, lifecycle과 implementation_state 분리 | D-31, D-32, C-B3, C-B5 | 유효 |
| S03 | 08-04 / 08-05 | Superpowers `v6.2.0` 실구조, Claude/Codex marketplace 버전 불일치(6.2 vs 5.1.3), 공통 skill + thin adapter 패턴, brainstorming 충돌, 10개 리뷰 | D-33, C-C6, C-E1~E3 | 유효 |
| S04 | 08-04 / 08-05 | OMA vs OMC 식별, `.agents` 투영 표, Codex 사실 정정 4건, Orca 이중 오케스트레이터 경고 | K-02~K-05, D-20, D-34, D-35 | 유효 |
| S05 | 08-05 | 라이선스 비교. Apache-2.0 권고 | K-43, X-05, D-41 | **실물과 불일치** |
| S09 | 08-11 | PHD 원문 전문 + Policy-Compiled Planning Graph 라운드1 | PHD, D-02a | **대체됨** (인프라 부분) |
| S10 | 08-11 | 자기반박 → **Thin Policy-Compiled Planning Spine**, unit 3개, frontmatter 체크포인트, 재분류, 정책 우선순위, 지표 8종, 두 CLI 구조화 출력 실측 | D-02~D-16, constraints 전반, v1-scope 전체 | **현행 기준** |
| S12 | 08-23 | OpenWiki 경계 판정, Spec Kit·OpenSpec·BMAD 비교, Superpowers 충돌 4종, 11단계 상태 전이, 공용 하네스 2계층(Setup/Attach) | D-22~D-27, C-F1~F4, X-08, Q-01 | 유효 |
| S13 | 08-23 | 언급된 저장소 전수 분류(기반 5 / 보조 7 / 제외), 디자인 트랙 4역할, anti-slop 저장소 목록 | D-30, D-37, C-G1~G4, Q-03 | 유효 |
| S23 | 08-26 | 현재 저장소 자체 요약. 무엇이 구현됐고 무엇이 아직인지 | v1-scope "이미 구현되어 있는 것" | **현행 기준** |
| S25 | 08-26 | 이 원천 자료를 만든 내보내기 작업 자체 | 이 문서 | 배경 |

---

## 2차 근거 — 운영 사례 (4건, 요구로 승격하지 않음)

| # | 날짜 | 성격 | 추출한 것 |
| --- | --- | --- | --- |
| S07·S08 | 08-10 | 쿠팡 계정 마이그레이션 (별도 제품 프로젝트) | GO/NO-GO 판정, fail-closed 게이트, credential-blind 증거, read-only 교차검토, "실제 브라우저는 열지 않았습니다" 정직 보고, 34개 분모 전수 종결 규칙 → C-E1·C-E4, K-50·K-51의 **실사용 증거** |
| S15 | 08-26 | 면접 준비 프로젝트 | 프로젝트별 `AGENTS.md` + `PROJECT_CONTEXT.md` 경량 부착, 대화로 규칙 추가, 원본 해시 무결성, 분석 기준일 기록, 출처별 수치 분리 → A-10, D-43 |
| S24 | 08-26 | 커머스 운영 자동화 `AGENT.md` | 확인된 컨텍스트만 사용, 승인 필요 위험 작업, 검증 기준 → D-43 |
| S14 | 08-23 | 비개발자 교육 설계 | 사용자 정체성 확정 근거 → X-02 |

---

## 하네스 범위 밖 (10건, 기록만)

| # | 날짜 | 내용 |
| --- | --- | --- |
| S06 | 08-09 | Codex `suppress_unstable_features_warning` 설정 |
| S11 | 08-22 | 상세페이지 이미지 편집 실험 (GPT Image) |
| S16~S22 | 08-26 | 초보자 교육용 단일 HTML 실습 웹앱 제작·개선 |

> 번들 77MB 중 58MB(78%)가 이 범위 밖 대화에 포함된 base64 이미지다.
> 1차 근거 11건은 합쳐도 10MB 미만이다.

---

## 커버리지 공백

| 공백 | 영향 |
| --- | --- |
| KEEL 원문 첨부(`pasted-text.txt`)가 번들에 포함되지 않았다 | 리뷰 인용으로만 복원된다. 원문 대조 불가 |
| 참조된 ChatGPT 대화 3건("워크플로우 자동화 설계", "개발 관련 스킬 추천", "OpenWiki 분석 설명")은 bounded preview만 존재한다 | 각 대화의 후반부 미확인 |
| S01·S02 등의 코드펜스 일부가 유실된 상태로 검토됐다 | COUNCIL이 명시한 한계 |
| BMAD 본체 아카이브 부재 (`archive/`에 CIS만 있음) | D-31 판정의 근거가 2026-08-04 조사에만 의존한다 → Q-06 |

---

## 정규화 원칙

이번 정규화에서 적용한 판단 기준을 남긴다.

1. **언급 횟수가 아니라 최종 생존 여부**로 중요도를 정했다. 2026-08-04 KEEL 계열과
   2026-08-11 이후 Spine 계열이 충돌할 때는 후자를 채택했다.
2. **도구 이름을 요구로 해석하지 않았다.** BMAD·Superpowers·OpenWiki·Spec Kit은 모두
   능력의 후보로 강등하고, [능력 지도](../requirements/capability-map.md)를 능력 ID 기준으로 작성했다.
3. **1차 근거만 요구로 승격**했다. 운영 사례는 증거로, 범위 밖 대화는 기록으로만 남겼다.
