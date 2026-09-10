---
id: feat-20260909-metrics-four-counters-dyz2
type: brief
title: 지표 — `romeo metrics` 가 네 카운터를 집계하고 각 숫자의 원본을 함께 인쇄한다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs, data]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
status: draft
approved_at: null
approved_by: null
base_sha: null
closed_at: null
parent: init-20260904-m4-doc-reuse-metrics-wr9m
inputs: [../init-20260904-m4-doc-reuse-metrics-wr9m/charter.md]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-09'
updated: '2026-09-09'
---

# 지표 — `romeo metrics` 가 네 카운터를 집계하고 각 숫자의 원본을 함께 인쇄한다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs, data · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

하네스가 자기 지표 4개를 처음으로 스스로 센다 — 세 개는 숫자가 서고, 원본이 없다고 실측된 하나는 「미집계」로 선다.

## 배경과 대상

- **왜 지금:** M4 이니셔티브의 네 마일스톤 중 마지막이다. 앞의 셋(재사용 검색 · 1-hop 재개 · 승격과 무결성)이 이미 닫혔고, 그것들이 만든 문서가 이 집계의 입력이다. 계획 §10 #14 의 관찰 결과 네 가지 중 마지막 하나가 이것으로 닫히면 다음 단계(§10 #15 shadow 20건 · v1 릴리스 게이트)로 넘어간다.
- **누구를 위한 것:** 이 하네스를 운영하는 사람. 지금까지 「분류가 얼마나 맞는가」·「게이트를 얼마나 놓치는가」는 사람이 문서를 훑어야만 알 수 있었다.
- **성공하면 무엇이 달라지나:** 명령 하나로 네 숫자와 그 숫자를 만든 파일 목록이 나온다. v1 릴리스 게이트가 추측이 아니라 숫자를 읽고 판정할 수 있게 되는 첫 조각이다.

## 방향

- **하려는 것:** 저장소를 읽어 네 지표를 집계하는 `romeo metrics` 하위 명령 하나와 그 판별 검사. 각 숫자 옆에 원본 파일 경로를 함께 인쇄한다(K-63).
- **하지 않는 것:** 지표가 나쁘다는 이유로 무엇도 차단하지 않는다 — charter 가 「드러내는 데까지」로 범위를 못박았다. 원본이 없는 지표를 집계 가능하게 만드는 기록 경로도 새로 만들지 않는다(§12) — 그 결함은 열어 둔다.
- **전달 메시지:** 셀 수 없는 것을 0 이라고 말하지 않는다. 「미집계」와 「0%」는 다른 사실이다(K-68).

## 열린 질문

- 없음


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
