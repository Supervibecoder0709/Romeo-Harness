---
id: feat-20260901-charter-discovery-block-a3xs
type: brief
title: Charter(T2) 템플릿과 discovery 차단 집행을 세운다 — 계산만 되던 blocks 를 종료 검사에 붙인다
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

# Charter(T2) 템플릿과 discovery 차단 집행을 세운다 — 계산만 되던 blocks 를 종료 검사에 붙인다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

라우터가 계산해 카드에 인쇄까지 하는 `blocks`(`spec-ready`·`milestone-plan`·`discovery-result`·`approval-gate`)를
승인·종료 두 지점에서 실제로 집행하고, 그 중 T2 가 요구하는 Charter 문서의 템플릿을 만든다.

## 배경과 대상

- **왜 지금:** 구현 계획 §7 M3 의 "만들 것" 중 `core/templates/charter.md` 와 `scenarios/` 런북 3 이 남아 있다.
  실측해 보니 그보다 앞선 문제가 있다 — 차단이 **계산·인쇄만 되고 아무것도 막지 않는다.**
  `romeo/policy.py` 가 `blocks` 를 계산하고 `romeo/card.py:108` 이 카드에 찍고 `romeo/fixtures.py:48` 이 fixture 와 대조하는데,
  `romeo/close.py` 는 `guards` 만 읽고 `blocks` 는 한 번도 읽지 않는다. 시나리오 3 이 요구하는 `SPEC_READY` 차단이
  문서에는 있고 실행에는 없는 상태다.
- **누구를 위한 것:** 이 하네스를 부착한 프로젝트에서 불확실성이 높은 요청(discovery)이나 새 이니셔티브(T2)를
  가져오는 사용자. 조사 없이, 마일스톤 없이 구현으로 넘어가는 것을 막는 것이 그 사용자를 위한 안전장치다.
- **성공하면 무엇이 달라지나:** 정책표에 차단을 적으면 그것이 실제로 승인을 거부한다. 새 차단을 정책표에 넣고
  집행을 잊으면 정책 로드가 실패한다 — 지금 이 결함의 재발이 구조적으로 막힌다.

## 방향

- **하려는 것:** `blocks` 카탈로그를 정책표에 신설하고, 차단 id 마다 충족 조건을 코드 한 자리(`romeo/blocks.py`)에
  두고, `romeo approve`(구현 dispatch 금지 지점)와 `romeo close`(완료 판정 지점) 둘에서 집행한다.
  T2 가 요구하는 `core/templates/charter.md` 를 만들고, `scenarios/3-discovery-block.md` 런북과
  그것을 자동 실행하는 테스트로 시나리오 3 을 고정한다.
- **하지 않는 것:** 실행 가드 집행(`gate-create` 승인 흐름 = 시나리오 9)과 능력 부재 프로브(doctor MCP·브라우저 = 시나리오 8)는
  이 단위 밖이다. 이미 `status: done` 인 13개 단위의 판정을 바꾸지 않는다. fixture 기대값을 고치지 않는다 —
  discovery·T2 fixture 3건이 이미 이 차단들을 기대값으로 갖고 있고, 그것이 이 단위의 대조 대상이다.
- **전달 메시지:** 차단은 카드에 찍히는 글자가 아니라 승인을 거부하는 힘이다.

## 열린 질문

- 없음

## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
