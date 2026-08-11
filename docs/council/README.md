# AI 카운슬 토론 기록

기획 하네스 설계(`docs/planning-harness-discussion.md`)를 검토한 AI 카운슬(claude-council)
토론 산출물 모음. 검토 대상 원문은 [`../planning-harness-discussion.md`](../planning-harness-discussion.md).

## 파일 목록 (권장 읽는 순서)

1. **[`01-codex-gpt5.3-debate.md`](./01-codex-gpt5.3-debate.md)**
   codex(gpt-5.3-codex-spark) 2라운드 debate. 초기 실행이며 비교용으로 보존한다.
   여기서 제안된 PGO 인프라(Graph Store·큐·샤딩)는 이후 전원 기각됨.

2. **[`02-local-council-debate.md`](./02-local-council-debate.md)**
   Claude 서브에이전트 3역할(Scalability Architect / Maintainability Advocate /
   Simplicity Champion)의 독립 제안(Round 1) + 상호 비판(Round 2). 세 멤버가 모두
   같은 모델이므로 멤버 간 합의는 독립 검증이 아니라 공유 프라이어임에 주의.

3. **[`03-codex-gpt5.6-debate-and-final-synthesis.md`](./03-codex-gpt5.6-debate-and-final-synthesis.md)**
   codex(gpt-5.6-sol) 재실행 debate + **최종 synthesis**. 결론만 볼 사람은 이 파일의
   Synthesis 섹션부터 읽으면 됨.

## 최종 권장 아키텍처

**Thin Policy-Compiled Planning Spine** — codex 5.6과 로컬 카운슬이 서로 못 본 채
독립 수렴한 결론.
