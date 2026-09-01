---
id: feat-20260901-scenario-8-capability-probe-s7ny
type: brief
title: 없는 능력을 있는 것처럼 쓰는 것을 막는다 — 능력 프로브·부재 카드·시나리오 8
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
created: '2026-09-01'
updated: '2026-09-01'
---

# 없는 능력을 있는 것처럼 쓰는 것을 막는다 — 능력 프로브·부재 카드·시나리오 8

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

없는 능력을 요구하는 요청에서, 하네스가 필요 능력과 프로브 결과를 카드에 인쇄하고
「능력 확인」 절에 사실과 다른 결과를 적으면 승인을 막는다. 시나리오 8 런북과 재현 테스트로 고정한다.

## 배경과 대상

- **왜 지금:** M3 종료 조건(계획 §10 #13)은 시나리오 3·8·9 런북 PASS 다. 3 은 `344fc7e`·`9dfq` 로 섰고
  다음이 8 이다. 지금 라우터는 `browser-automation` 요청에 「능력 확인」 절과 `CAPABILITY_CHECK_REQUIRED`
  경고를 걸지만, **그 절을 채울 프로브가 하나도 없고**(`capabilities.yaml` 에 `discovery.bmad` 뿐)
  **카드는 프로브 결과를 한 줄도 인쇄하지 않는다**(`card.py:_parts_detail` 이 부품에 붙은 것만 본다).
  절의 충족은 `open-loop` 뿐이라 미완료 자리표시자만 지우면 그럴듯한 거짓 값이 통과한다.
- **누구를 위한 것:** 없는 도구를 쓰는 계획을 승인받게 되는 사람. 지금은 하네스가 그것을 말해 주지 않는다.
- **성공하면 무엇이 달라지나:** 능력이 없다는 것이 카드에 인쇄되고, 있다고 적은 거짓이 승인 자리에서 막힌다.
  **없다는 사실 자체는 막지 않는다** — 막으면 「되는지 조사해 보자」 는 요청이 불가능해진다(Q-28 의 순환).

## 방향

- **하려는 것:** 능력 프로브를 코어에 정의하고 그 흔적 경로는 어댑터가 소유한다(C-C6). 라우터가 요구한
  능력의 프로브 결과·대안을 카드가 인쇄하고, 「능력 확인」 절의 기재가 프로브와 다르면 승인에서 막는다.
- **하지 않는 것:** 능력을 자동으로 설치하지 않는다. 능력이 없다는 이유로 승인·위임을 막지 않는다.
  프로브가 「그 도구가 동작한다」 고 말하게 하지 않는다 — 답하는 것은 설치 흔적뿐이다(A-11).
- **전달 메시지:** 프로브는 있음/없음만 말한다. 없는 것을 있다고 적는 순간 하네스가 막는다.

## 열린 질문

- 없음


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
