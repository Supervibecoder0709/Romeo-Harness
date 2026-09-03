---
id: init-20260904-m4-doc-reuse-metrics-wr9m
type: brief
title: M4 — 문서 재사용·승격·지표
unit: T2
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: deep
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
  fired_rules: ['profile:base:T2=deep', 'profile:uncertainty.medium=kept', 'overlay:unit.t2.parts', 'overlay:profile.standard-or-deeper',
    'warn:PART_PENDING_GATE']
  history: []
created: '2026-09-04'
updated: '2026-09-04'
---

# M4 — 문서 재사용·승격·지표

> 깊이 **Deep** · 단위 T2 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

M4 — 문서를 두 번 만들지 않고, 끝난 사실을 current 로 올리고, 하네스가 자기 지표를 집계한다

## 배경과 대상

- **왜 지금:** 작업 단위가 23건이다. 절차는 새 단위를 열기 전 재사용 검색을 요구하는데 그 검색을 하는 것도, 했는지 보는 것도 사람의 기억뿐이다. M4 의 나머지 세 조각도 모두 「이미 무엇이 있는가」에서 출발한다.
- **누구를 위한 것:** 이 하네스로 작업을 여는 사람과, 그 사람을 대신해 `/plan` 을 도는 실행 런타임. 둘 다 지금은 23개 폴더를 눈으로 훑어야 한다.
- **성공하면 무엇이 달라지나:** 제안 카드가 확정을 받기 **전에** 겹치는 단위를 스스로 내민다. 사람은 재개·재분류·새 단위 중 하나를 고르면 된다.

## 방향

- **하려는 것:** 첫 마일스톤은 검색 하나다 — `romeo find` 와, 그 결과를 제안과 무관하게 인쇄하는 카드. 나머지 마일스톤은 Charter 의 계획표에 있다.
- **하지 않는 것:** 중복을 **차단**하지 않는다. 겹치는 단위가 있어도 새로 여는 것이 옳은 경우(재분류·후속 작업)가 있어, 차단은 정상 경로를 막고 사람의 판단을 지운다. 카드는 드러내고 사람이 정한다.
- **전달 메시지:** 「이미 이것들이 있습니다 — 재개할까요, 새로 열까요?」

## 열린 질문

- `docs/current/` 승격 규칙(무엇이 승격 대상인가)은 이 마일스톤에서 정하지 않는다 — Charter M3 의 몫이다.
- 지표 4개의 원본 데이터가 evidence·fixture 에 전부 있는지는 미확인이다 — Charter M4 진입 전에 확인한다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
