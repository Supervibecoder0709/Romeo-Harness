---
id: feat-20260904-gate-fixture-coverage-q3wy
type: brief
title: hard gate 8 커버리지를 fixture 와 검사로 채운다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
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
created: '2026-09-04'
updated: '2026-09-04'
---

# hard gate 8 커버리지를 fixture 와 검사로 채운다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

hard gate 8 중 fixture 가 없는 5개(payment·legal·ops-data-deletion·public-api·irreversible-policy)에 요청 fixture 를 각각 1건 이상 추가하

## 배경과 대상

- **왜 지금:** 계획 §10 #13 의 M3 종료 조건 두 개 중 「시나리오 3·8·9 런북 PASS」는 `344fc7e`·`50d3901`·`16c0751` 로 충족됐고, 나머지 「hard gate 8 각 fixture ≥ 1」이 남았다. 실측하면 8개 중 3개만 fixture 가 있다.
- **누구를 위한 것:** 라우터를 만드는 이 저장소 자신. fixture 는 「사람이 확정한 분류」와 「정책표가 낸 출력」을 대조하는 유일한 자리다.
- **성공하면 무엇이 달라지나:** 8개 게이트 전부가 적어도 한 번은 실제 대조를 거친다. 게이트 id 를 바꾸거나 fixture 를 지우면 검사가 즉시 빨간불이 된다 — 지금은 아무도 보지 않는다.

## 방향

- **하려는 것:** fixture 5건 추가 + 커버리지·id 유효성 검사 1건. 게이트 id 는 정책표에서 읽어 대조한다.
- **하지 않는 것:** 정책표(`classification.yaml`)의 게이트 정의·facet 어휘 수정, 기존 fixture 33건 수정, 라우팅 코드 수정. T2 관통은 이 단위가 아니다.
- **전달 메시지:** 8개 게이트 중 5개는 사용자의 실제 요청 로그에 없다. 그 5개 중 4건은 `source.kind: authored` 로 새로 쓰며, 그 사실을 파일에 남긴다 — authored fixture 는 M3 종료 조건을 닫지만 「라우터가 실제 사용에서 맞는가」를 증명하지는 않는다.

## 열린 질문

- 없음



## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
