---
id: feat-20260830-harness-defects-w3qu
type: brief
title: 3차 관통이 드러낸 하네스 결함 5건 정비
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
created: '2026-08-30'
updated: '2026-08-30'
---

# 3차 관통이 드러낸 하네스 결함 5건 정비

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

3차 관통(`feat-20260830-harness-tuneup-6xcq`)을 돌리는 동안 하네스가 스스로 드러낸 결함 5건을,
같은 실패가 M3 관통에서 되풀이되기 전에 고친다. 다섯 건 모두 **위임을 중단시켰거나 승인을 다시 돌게 만든 것**이다.

## 배경과 대상

- **왜 지금:** 코어 규칙 §10 은 관통이 시작된 뒤에는 하네스를 고치지 못하게 한다 — 도중에 하네스가 바뀌면 그 판정이 무엇이 만든 것인지 말할 수 없기 때문이다. 그래서 정비는 관통과 관통 **사이**에만 가능하고, M2 가 닫히고 M3 가 아직 시작되지 않은 지금이 그 구간이다.
- **누구를 위한 것:** 다음 관통에서 계약을 만들고 위임을 띄우는 사람과, 그 계약을 받아 구현하는 워커. 다섯 결함은 전부 그 두 자리에서 걸렸다.
- **성공하면 무엇이 달라지나:** ④ 때문에 1차 위임이 통째로 폐기되고 ①② 때문에 승인이 두 번 더 돈 일이 M3 에서는 일어나지 않는다. 구현자가 쓰기 상한을 손으로 기억하는 대신 명령에 물어본다.

## 방향

- **하려는 것:** 다섯 자리에 **사유를 붙이거나 제약을 인쇄한다** — 죽는 자리에는 왜 죽었는지를, 형식이 정해진 줄에는 그 형식을, 개수가 박힌 프롬프트에는 개수 대신 출처를, 기억에 의존하던 목록에는 그것을 답하는 명령을, 한쪽만 적힌 실패 조건에는 반대쪽 관측을.
- **하지 않는 것:** 계약 스키마·코어 규칙·권한 상한·정책표를 바꾸지 않는다. 검증 계획 YAML 의 문법을 관대하게 만들지 않는다 — ① 은 콜론을 허용하는 것이 아니라 콜론이 무엇을 깨뜨렸는지 말하는 것이다. M3 의 내용(Charter·discovery·gate·doctor)에는 손대지 않는다.
- **전달 메시지:** 이 다섯은 새 기능이 아니라 **이미 한 번씩 사람을 멈춰 세운 자리**다. 고치는 기준은 '더 똑똑해지는 것' 이 아니라 '같은 자리에서 다시 멈추지 않는 것' 이다.

## 열린 질문

- 없음


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
