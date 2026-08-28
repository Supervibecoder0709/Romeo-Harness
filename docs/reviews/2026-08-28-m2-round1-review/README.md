# 2026-08-28 M2 실행 검증 1차 리뷰

M2 실행 검증 배치(역할 실행·작업 계약·Orca 위임·동등성 게이트)를 만든 뒤 받은 **1차 독립 리뷰**와,
그 리뷰가 "저장소에 산출물이 0건" 이라고 지적한 항목을 실제로 관찰해 만든 증거를 함께 둔다.

| 파일 | 내용 |
| --- | --- |
| `REVIEW_FINDINGS.md` | 1차 리뷰 findings 전문(F01~F31 · blocker 6 · important 15 · minor 10). 각 항목에 재현 명령이 들어 있다 |
| `PROBE_READONLY.md` | 검토자 읽기 전용 강제 프로브 7건의 명령·종료 코드·거부 근거. 계획 §10 #8 의 "reviewer 쓰기 시도 거부 로그" |
| `logs/` | 위 프로브의 원문 stdout·stderr 와 방어 검사용 `git status --porcelain` 전후 파일 |

관찰 결과는 `.harness/observations.yaml` 의 `reviewer_write_refusal` 에도 등록했다 —
이 디렉터리는 원문 보관이고, 그 파일이 하네스가 읽는 색인이다.

이 리뷰의 **반영분을 다시 독립 리뷰에 넣은** 결과는 [`../2026-08-28-m2-round2-review/`](../2026-08-28-m2-round2-review/README.md) 에 있다.
2차 리뷰는 1차 반영이 만든 새 결함을 잡았다 — 판정이 검사되지 않는 자기 신고 위에 서 있던 자리들이다.
`PROBE_READONLY.md` 의 프로브 7건은 **단독 프로브**이지 위임 기동 경로(`adapters/orca/RUNBOOK.md` §3.7)에 대한 관찰이 아니라는 것도
그 리뷰가 잡았다(G04).
