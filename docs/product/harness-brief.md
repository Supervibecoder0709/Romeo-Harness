---
id: harness-brief
type: product_brief
status: draft
updated: 2026-08-27
authority: canonical
---

# Romeo 하네스 — 제품 브리프

## 한 문장

Romeo는 PM의 자연어 요청을, 위험도와 규모에 맞는 최소 기획 문서·실행 계약·검증 증거로
바꿔 Claude Code와 Codex가 같은 의미로 수행하게 만드는 **요청 운영 체계**다.
에이전트·스킬 카탈로그가 아니다.

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

## 성공의 정의 (v1)

실제 T1 요청 1건이 다음을 관통하고, **구현/리뷰 런타임을 서로 바꿔도 같은 artifact 스키마와
게이트 판정**이 나온다.

```text
분류 확인 → Brief → Tech Spec → 한 런타임 구현
→ 반대 런타임 read-only 리뷰 → 현재 HEAD SHA에 묶인 증거 → close
```

근거: S01 KEEL 리뷰 §1, S10 최종 결론, COUNCIL 구현 우선순위 5.

## 비목표 (v1)

- 완성형 하네스 운영체제, 20여 개 역할, 8계층 문서 (S01 KEEL 리뷰: "연기")
- 중앙 DB·큐·샤딩·인덱스 (COUNCIL Consensus 7 — 전원 기각)
- 자체 DAG·relay·worktree 폴백 (Orca와 이중 스케줄러가 됨 — S04 리뷰 #5)
- 범용 outcome gate, 자동 모델 라우팅, 자기학습 자동 반영

## 경계: 누가 어떤 진실을 소유하는가

| 진실 | 소유자 |
| --- | --- |
| 제품 의도·요구사항·승인 | Romeo (기획 하네스) |
| 실행 상태(worktree·dispatch·재시도·게이트 대기) | Orca |
| 현재 실제 동작 | 코드와 테스트 |
| 현재 구현의 기술 설명 | OpenWiki (선택 부품, 파생 계층) |
| 구현 규율(TDD·디버깅·리뷰) | Superpowers에서 차용한 규칙 |
| 최종 승인 | 사람 |

근거: S12 최종 판단, COUNCIL Recommendation.

## 관련 문서

- [능력 지도](../requirements/capability-map.md)
- [제약](../requirements/constraints.md)
- [v1 범위](../requirements/v1-scope.md)
- [결정 등록부](../decisions/decision-register.md)
- [열린 질문](../planning/open-questions.md)
- [대화 커버리지](../traceability/conversation-coverage.md)
