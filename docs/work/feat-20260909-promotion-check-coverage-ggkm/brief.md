---
id: feat-20260909-promotion-check-coverage-ggkm
type: brief
title: 승격 문서를 보는 자리를 넓힌다 — CI 트리거와 대조 등록부
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
created: '2026-09-09'
updated: '2026-09-09'
---

# 승격 문서를 보는 자리를 넓힌다 — CI 트리거와 대조 등록부

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

승격 문서(`docs/current/`)를 보는 자리 두 곳을 넓힌다 — CI 가 도는 사건이 CI 가 읽는 파일을 덮게 하고(Q-90), 대조 대상 승격 문서를 상수 하나에서 등록부로 바꿔 미등록 문서를 지목한다(Q-91).

## 배경과 대상

- **왜 지금:** 바로 앞 단위(`feat-20260909-promote-integrity-kchq`)가 `docs/current/` 와 `bin/romeo integrity` 를 세우면서 §12 로 남긴 결함 둘이고, 둘 다 **그 새 검사 자신의 사각**이다. 다음 마일스톤(M4 지표)이 이 사각 위에서 돌기 전에 메운다.
- **누구를 위한 것:** 이 저장소에서 다음 작업 단위를 도는 사람과 런타임. 승격 문서를 고치는 커밋이 검사를 받고, 새 승격 문서가 대조 없이 들어오지 않는다.
- **성공하면 무엇이 달라지나:** 표에서 한 행을 지운 커밋이 CI 를 빨간불로 만든다. 대조원 없는 승격 문서를 두면 `bin/romeo integrity` 가 지목한다. 그리고 검사 코드가 읽는 자리가 늘 때 트리거를 함께 넓히지 않으면 CI 가 실패한다 — 같은 사각이 다시 열리지 않는다.

## 방향

- **하려는 것:** 두 모듈이 읽는 루트를 상수로 선언하게 하고, 그 상수를 CI 트리거와 대조하는 검사를 만든다. 대조 대상 승격 문서를 `{경로: 파생 함수}` 등록부로 바꾸고 미등록 `.md` 를 `UNCHECKED_PROMOTION` 으로 낸다. 승격 문서가 문서 검증 대상이 아니라는 결정을 그 문서에 적는다.
- **하지 않는 것:** 승격 문서에 frontmatter 를 붙이거나 문서 스키마에 새 type 을 더하는 것. 미완 표지 토큰(문서 검증이 open loop 로 세는 그 낱말) 잔존 검사 — 지금 승격 문서 본문에 그 낱말이 판정 **설명**으로 3곳 있어 도입 즉시 거짓 양성 3건이다. Q-92(회차 판정 커밋의 미추적 파일)와 Q-93(부착 저장소에 승격 규약을 적용할지)도 이 단위에서 풀지 않는다.
- **전달 메시지:** 검사가 **막는 자리**에 있어도 **보는 사건**이 좁으면 아무것도 막지 못한다. 요구하는 자리와 보는 자리를 같게 두는 것(§11)은 규칙 문서만이 아니라 CI 트리거에도 적용된다.

## 열린 질문

- 없음 — 자리 선택 두 건은 확정 단계에서 사용자가 골랐다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
