---
id: feat-20260831-park-defects-actm
type: brief
title: park 된 하네스 결함 4건 정비 — 계약 경로 잘림·안내문 토큰·디렉터리 크래시·유령 시도
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
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
created: '2026-08-31'
updated: '2026-08-31'
---

# park 된 하네스 결함 4건 정비 — 계약 경로 잘림·안내문 토큰·디렉터리 크래시·유령 시도

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

관통과 관통 사이에만 열리는 정비 창에서, 지난 관통을 실제로 막았거나 손작업을 강요한 하네스 결함 넷을 고치고 park 다섯 건을 닫는다.

## 배경과 대상

- **왜 지금:** 코어 규칙 §10 이 관통 중 하네스 수정을 금지한다. 직전 단위가 close 를 통과해 진행 중인 관통이 없는 지금이 유일하게 열린 구간이고, 다음 단위를 열면 그것이 끝날 때까지 다시 잠긴다. 그 사이 네 결함은 다음 관통에서 같은 자리에 다시 걸린다.
- **누구를 위한 것:** 이 하네스로 관통을 도는 사람과, 위임을 받아 구현·검토하는 두 런타임. 제품 사용자에게 보이는 변화는 없다.
- **성공하면 무엇이 달라지나:** 승인된 변경 범위를 여러 줄로 적어도 계약이 전부 읽고, 템플릿 안내문을 지우는 것을 잊어도 종료 검사가 막지 않고, `validate` 에 폴더를 줘도 트레이스백이 나오지 않고, 반복 중단을 풀 때 시도 기록에 유령이 생기지 않는다.

## 방향

- **하려는 것:** 네 결함의 **근본**을 고친다 — 우회 방법을 문서에 더 적는 것이 아니라, 우회가 필요 없게 만든다. 고친 자리마다 그 결함을 재현하는 회귀 테스트를 붙인다.
- **하지 않는 것:** 나머지 park(Q-12~Q-17·Q-19·Q-23·Q-24)은 건드리지 않는다. 4회 연속 실패로 멈춘 `feat-20260830-harness-defects-w3qu` 도 재개하지 않는다 — 그 단위의 실패 원인은 완료 정의 쪽이었고, 재검토 없이 다시 열면 반복 중단 브레이크가 그대로 다시 걸린다. 코어 규칙과 CI 워크플로도 비범위다.
- **전달 메시지:** park 이라고 다 같은 park 이 아니다. 다섯 건 중 하나(Q-21)는 **서술된 결함이 이미 존재하지 않았다** — 고칠 코드가 없어 문서 정정으로 닫는다. 열린 질문도 실측으로 다시 확인해야 한다는 것이 이번에 드러난 것이다.

## 열린 질문

- 없음


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
