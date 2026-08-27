---
id: harness-brief
type: product_brief
status: draft
updated: 2026-08-27
authority: canonical
---

# Romeo 하네스 — 제품 브리프

## 한 문장

Romeo는 사용자가 직접 써보고 검증한 하네스들(BMAD/CIS = 기획, Superpowers = 개발 규율,
OpenWiki = 기술 문서 파생, 디자인 스킬 세트 = UI·랜딩, Orca = 실행)을 **부품으로 그대로 두고**,
그 앞에 서서 요청을 이해해 "어떤 부품을 어떤 깊이로 어떤 순서로 쓸지"를 정하고,
부품 사이의 산출물·상태·증거를 하나의 문서 체계로 이어 주며, Claude Code와 Codex 어느 쪽에서
실행해도 같은 판정이 나오게 하는 **개인용 라우터(요청 운영 체계)**다.
에이전트·스킬 카탈로그가 아니고, 부품을 다시 만드는 프로젝트도 아니다.

> 2026-08-27 사용자 재정의: "내가 잘 썼던 하네스들을 **조립**해서 **나만의 라우터 체계**로 구축하고 싶다."
> 이 문장은 S01(2026-08-04) 계획의 책임표 — BMAD·Superpowers·OMA·Orca는 각자 담당, **자체 하네스는
> 라우팅·문서 상태·SSOT·모델 정책·도구 레지스트리·자기개선** — 와 같은 내용이다.
> ([결정 D-50](../decisions/decision-register.md), [개정 3 기록](../reviews/2026-08-27-assembly-redefinition/summary.md))

## 만드는 것과 만들지 않는 것

| Romeo가 만든다 (라우터 + 접착 + 동등성) | Romeo가 만들지 않는다 (조립하는 부품) |
| --- | --- |
| `/plan` 라우터: 요청 이해 → unit·mode·facet·profile → **어떤 부품을 켤지** 결정 | 기획 facilitation (BMAD 본체·CIS) |
| 접착: 문서 ID·frontmatter·상태·`docs/work/`·evidence·`/plan-close` | 개발 규율 스킬 (Superpowers TDD·디버깅·검증·리뷰) |
| 동등성: 공통 스키마·역할 계약·어댑터·parity fixture | 기술 문서 파생 (OpenWiki) |
| 조립 규약: 채택 방식·채택 게이트·통합 규약·provenance | 디자인 규칙·감사 스킬 (WIG·taste·impeccable·ui-ux-pro-max) |
| 부착·업데이트·doctor | 실행·worktree·dispatch (Orca) |

## 해결하려는 문제

1. 모든 요청에 같은 포맷의 기획서가 필요하지 않은데, 기존 도구는 하나의 고정 절차를 강요한다.
   ([PHD](../planning-harness-discussion.md) 도입부, S09 사용자 원문)
2. 기획 의도 → 구현 → 검증 사이에서 근거가 끊긴다. "만들었다"가 "검증했다"로 오인된다. (S01, S07/S08)
3. Claude와 Codex의 규칙을 따로 관리하면 드리프트가 생겨 결과를 공정하게 비교할 수 없다. (S01 참조 대화)
4. 코드가 변하면 기술 문서가 낡는데, 사용자는 기술 문서를 직접 관리하고 싶어하지 않는다. (S12)
5. 위험 작업(결제·개인정보·마이그레이션·삭제·배포)이 절차 없이 통과할 수 있다. (PHD §1 Hard Gate)

## 사용자와 사용 맥락

- 1인 운영. PM 출신이며 개발 암묵지를 상당 부분 공유한다. (S14 사용자 원문)
- 미래의 주 소비자는 사람이 아니라 **다음 LLM 세션**이다.
  ([COUNCIL](../council/03-codex-gpt5.6-debate-and-final-synthesis.md) "전원이 틀릴 수 있는 지점")
- 실행 환경은 Orca + Claude Code CLI + Codex CLI로 고정한다. (S01)
- 운영 방식은 "나는 기획·명세, 코드는 에이전트"다. (S12 "코드 쪽은 최대한 건드리지 않고") S14의
  "개발자와 같은 암묵지"와 모순되지 않는다 — X-02는 설명 톤의 문제이지 설계 요구가 아니다.
- 부품 실사용 흔적(2026-08-27 로컬 확인): BMAD v6.0.4(`~/readly-sologis`, 2026-03) ·
  v6.10.0 + CIS v0.2.1(`~/bmad-ordi`, 2026-07) · UI UX Pro Max v2.2.3(`~/readly-sologis`).
  Superpowers·OpenWiki·impeccable·taste 는 로컬 흔적은 없지만 사용자가 다른 환경에서 실사용했고 좋았다고 확인했다(2026-08-27, D-64).
  BMAD 기획 흐름의 PRD 양식은 "고정돼 있어 다양한 상황에 부적합", CIS 가 기획 구체화에 가장 유용했다.

## 성공의 정의 (v1)

실제 T1 요청 1건이 다음을 관통하고, **구현/리뷰 런타임을 서로 바꿔도 같은 artifact 스키마와
게이트 판정**이 나온다.

```text
분류 확인 → Brief → Tech Spec → 한 런타임 구현
→ 반대 런타임 read-only 리뷰 → 현재 HEAD SHA에 묶인 증거 → close
```

근거: S01 KEEL 리뷰 §1, S10 최종 결론, COUNCIL 구현 우선순위 5.

동등성은 **부품이 붙은 상태에서** 증명한다 — 구현 단계에서 Superpowers 규율 세트가, 기획 단계에서
BMAD/CIS 링크가 실제로 켜진 채로 위 흐름이 통과해야 실제 사용 조건을 반영한 증명이다.
([결정 D-58](../decisions/decision-register.md))

## 비목표 (v1)

- 완성형 하네스 운영체제, 20여 개 역할, 8계층 문서 (S01 KEEL 리뷰: "연기")
- 중앙 DB·큐·샤딩·인덱스 (COUNCIL Consensus 7 — 전원 기각)
- 자체 DAG·relay·worktree 폴백 (Orca와 이중 스케줄러가 됨 — S04 리뷰 #5)
- 범용 outcome gate, 자동 모델 라우팅, 자기학습 자동 반영
- 부품의 자체 제작·벤더링·원칙 재작성을 기본값으로 삼는 것 (D-50 — `rewrite`는 통합 규약을 못 지킬 때의 강등 경로)

## 부품 조립표: 누가 어떤 진실을 소유하고, 어떻게 가져오는가

채택 방식은 [결정 D-51](../decisions/decision-register.md)의 5단계(`install` 설치·연결 / `verbatim` 고정 SHA 원문 /
`rewrite` 원칙 재작성 / `principle` 참고 / `excluded`)다. "후보"는 계획 단계의 기록이며, 파일 단위 확정은
해당 마일스톤 진입 시 **채택 확정 게이트**에서 사용자가 한다 (D-52). 부품이 충돌 없이 하나의 시스템이 되는
조건은 [통합 규약 K-60~K-69](../requirements/constraints.md)다 (D-53).

| 진실 | 소유자(부품) | 채택 방식(후보) | 라우터가 켜는 조건 | 확정 게이트 |
| --- | --- | --- | --- | --- |
| 제품 의도·요구사항·승인·문서 상태 | **Romeo** (라우터·접착) | 자체 | 항상 | — |
| 실행 상태(worktree·dispatch·재시도·게이트 대기) | **Orca** | `install` (이미 사용 중) | 위임이 필요한 T1 이상 | — |
| 발산·문제 정의·전략·스토리 facilitation | **BMAD 본체 + CIS** (프로젝트별 설치, v6.10.0 / CIS v0.2.1 고정) | `install` + `/plan` 링크 | `mode=discovery` 또는 T2 | G-M3 |
| 구현 규율(TDD·디버깅·검증·리뷰·worktree·통합) | **Superpowers** 규율 스킬 세트 (`brainstorming`·`using-superpowers` 제외) | `verbatim` (고정 SHA `b36e082`) | `profile ≥ standard` 구현·리뷰 단계 | G-M2 |
| 현재 실제 동작 | 코드와 테스트 | — | — | — |
| 현재 구현의 기술 설명 | **OpenWiki** (파생 계층, 기획을 소유하지 않음) | `install` | 기준 브랜치 반영 후 1건씩 | G-M7 (v2) |
| UI·랜딩 규칙·감사 | **WIG · taste-skill · impeccable · ui-ux-pro-max**(라이선스 확인 후) | `verbatim` 파일 + `visual-qa`만 자체 | `facet=ui` / `brand` | G-M6 |
| 최종 승인 | 사람 | — | — | — |

근거: S12 최종 판단, COUNCIL Recommendation, 2026-08-27 사용자 재정의, `~/readly-sologis`·`~/bmad-ordi` 실사용 흔적.

## 관련 문서

- [개정 3 기록 — 부품 조립 재정의·통합 규약](../reviews/2026-08-27-assembly-redefinition/summary.md)
- [능력 지도](../requirements/capability-map.md)
- [제약](../requirements/constraints.md)
- [v1 범위](../requirements/v1-scope.md)
- [결정 등록부](../decisions/decision-register.md)
- [열린 질문](../planning/open-questions.md)
- [대화 커버리지](../traceability/conversation-coverage.md)
