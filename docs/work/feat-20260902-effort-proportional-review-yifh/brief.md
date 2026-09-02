---
id: feat-20260902-effort-proportional-review-yifh
type: brief
title: 작업 강도를 위험에 비례시킨다 — 검토자 오버레이·범위 밖 발견·회귀 검사 실측
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: low
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
  fired_rules: ['profile:base:T1=standard', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-02'
updated: '2026-09-02'
---

# 작업 강도를 위험에 비례시킨다 — 검토자 오버레이·범위 밖 발견·회귀 검사 실측

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

사람이 매번 확정하는 `blast_radius` 를 검토자 배정에도 쓰게 해, 영향 반경이 작고 게이트가 없는 정비 작업이 큰 작업과 같은 코스를 돌지 않게 한다.

## 배경과 대상

- **왜 지금:** `docs/work/` 17건 실측 — T0 2건, T1 15건. T1 15건은 전부 영역이 `tooling`·`docs` 인 하네스 자기 정비인데 `packages.yaml` 의 `base.T1` 이 unit 만 보고 검토자·격리를 정하므로 예외 없이 반대 런타임 검토자 왕복을 받았다. `blast_radius` 는 카드에서 사람이 확정하지만 `classification.yaml` 의 escalations 가 profile 을 **올리는** 데만 쓰고, 검토자·격리를 정하는 자리에서는 읽지 않는다.
- **누구를 위한 것:** 이 저장소에서 정비 단위를 여는 사람. 판단 근거(영향 반경)를 이미 대고 있는데 그 판단이 작업량에 반영되지 않는 상태를 없앤다.
- **성공하면 무엇이 달라지나:** 같은 판단으로 두 갈래가 갈린다 — 영향 반경이 작고 게이트가 없으면 증거만으로 닫고, 게이트가 켜지거나 반경이 커지면 지금과 똑같이 검토자가 붙는다.

## 방향

- **하려는 것:** 정책표 오버레이 1행(코드 수정 없음 — `romeo/policy.py:279` 의 `set_reviewer` 와 `_match` 의 `blast_radius`·`gates: none` 이 이미 이 조건을 지원한다). 요청 범위 밖 결함을 열어 두게 하는 조항. 회귀 방지 검사를 승인 전 양쪽 실측에서 빼는 한 줄.
- **하지 않는 것:** 격리(worktree)는 그대로 둔다 — `set_isolation` 은 미구현이라 코드 수정이 필요하고, 워크트리는 검토자 왕복보다 훨씬 싸다. 새 분류 축(Risk Tier)도 만들지 않는다 — `blast_radius` 와 중복이다. `romeo/policy.py` 를 고치지 않는다.
- **전달 메시지:** 검증은 많이 하는 것이 아니라 실패 비용에 비례해야 한다. 그 비례를 만드는 입력값은 이미 카드에 있었고, 읽는 자리가 한 곳 모자랐을 뿐이다.

## 열린 질문

- 이 오버레이가 붙은 뒤 `romeo close` 가 `reviewer: none` 인 단위에서 review 산출물을 요구하지 않는지 — check-5(전체 테스트)와 이 단위 자신의 close 로 확인한다. 이 단위는 오버레이를 만들기 전에 분류됐으므로 검토자가 붙은 채로 닫힌다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
