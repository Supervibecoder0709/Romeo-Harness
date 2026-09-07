---
id: feat-20260907-close-review-reapproval-reach-bjec
type: brief
title: 재승인이 닿지 않던 자리를 연다 — 산출물을 식별하지 못한 봉투도 승인 키는 읽는다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: draft
approved_at: null
approved_by: null
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-07'
updated: '2026-09-07'
---

# 재승인이 닿지 않던 자리를 연다 — 산출물을 식별하지 못한 봉투도 승인 키는 읽는다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

검토 판정을 낡은 것으로 가려내는 규칙이 **산출물을 식별한 봉투에만** 걸려 있어, 식별하지 못한 봉투는
사람이 재승인해도 걷히지 않는다. 승인 키는 산출물과 무관하게 읽을 수 있으므로 그 순서를 바꾼다.

## 배경과 대상

- **왜 지금:** 다음은 M5 attach 관통이고, 그 관통도 회차를 돌면 같은 자리를 지난다. §10 동결 규칙상
  관통 도중에는 하네스를 고칠 수 없으므로 관통 **사이**인 지금 닫는다. 2026-09-06 M3 관통에서 이 결함이
  실제로 작동해, 3회차가 PASS 를 받고 재승인까지 했는데도 닫히지 않아 봉투를 손으로 빼내야 했다.
- **누구를 위한 것:** 관통을 닫는 사람. 재승인(D-80)은 이 저장소의 정상 경로인데(M3 에서 2회, M4 에서 1회),
  그 경로가 특정 봉투에는 듣지 않는다는 것이 지금 상태다.
- **성공하면 무엇이 달라지나:** 재승인 뒤에는 이전 승인으로 낸 검토가 — 그 판정이 무엇을 봤는지 하네스가
  확인하지 못하더라도 — 완료를 막지 않는다. 봉투는 지워지지 않고 `REVIEW_SUPERSEDED` 로 인쇄된다.

## 방향

- **하려는 것:** `romeo close` 의 봉투 분류에서 승인 키 대조를 산출물 식별보다 앞에 둔다. 그 규칙이 사는
  문서(`core/workflows/plan-close/SKILL.md`)를 같은 커밋에서 함께 고친다(§11).
- **하지 않는 것:** 기록 시점(`romeo review record`)에 새 게이트를 만들지 않는다 — 반박 검증에서 그것이
  검토자의 FAIL 을 파일로도 로그로도 남기지 않아 **순 안전성을 낮추는 것**으로 실측됐다. 방어 검사 판정
  함수를 두 자리가 공유하도록 하는 리팩터도 하지 않는다(판정을 바꾸지 않으므로 §12 밖). Q-64·Q-69·Q-70 도
  이 단위에서 고치지 않는다.
- **전달 메시지:** 하나의 봉투에 대해 「무엇을 봤는가」와 「어느 승인으로 낸 판정인가」는 서로 독립인 두
  질문이고, 후자가 논리적으로 먼저다 — 완료 정의가 바뀌었으면 그 판정이 무엇을 봤든 이번 close 의 대상이 아니다.

## 열린 질문

- 없음 — 봉인 조건을 함께 걸지 여부는 실측으로 확정해 `spec.md` 의 검증 계획에 넣는다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
