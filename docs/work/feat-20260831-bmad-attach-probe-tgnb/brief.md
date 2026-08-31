---
id: feat-20260831-bmad-attach-probe-tgnb
type: brief
title: G-M3 부착 — discovery.bmad 프로브와 /plan 추천·inputs 링크 요구
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
created: '2026-08-31'
updated: '2026-08-31'
---

# G-M3 부착 — discovery.bmad 프로브와 /plan 추천·inputs 링크 요구

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

D-77 이 고른 BMAD·CIS 스킬 11종을 라우터에 연결한다 — discovery/T2 요청의 분류 카드가 그 11종을 추천하고,
산출물을 복사 대신 `inputs:` 링크로 요구하며, `romeo doctor` 가 설치 여부를 정직하게 인쇄한다.

## 배경과 대상

- **왜 지금:** G-M3 의 1·2·3단계는 D-77 로 닫혔고 남은 것은 §6.1 의 4(부착)·5(검증)뿐이다.
  결정이 정책표에 연결되지 않으면 카드는 여전히 아무것도 추천하지 않는다 — 결정은 문서 안에만 남는다.
- **누구를 위한 것:** 이 하네스로 새 요청을 여는 사람. 특히 `mode=discovery` 나 T2 처럼
  "무엇을 만들지 아직 모르는" 상태로 들어오는 요청이 대상이다.
- **성공하면 무엇이 달라지나:** `core/templates/sections/discovery-plan.md` 의 「조사 방법·기간」 의 빈칸이
  빈칸인 채로 남지 않는다. 라우터가 그 칸을 채울 도구 11종을 이름으로 제시하고, 그 산출물을 붙이는 방법까지 지정한다.

## 방향

- **하려는 것:** 능력 프로브 정책표를 만들고(`capabilities.yaml`), doctor 가 그것을 실행하게 하고,
  `parts.bmad-cis` 를 G-M3 확정 상태로 올려 카드에 추천과 `inputs:` 요구를 인쇄하고, 충돌을 fixture 로 고정한다.
- **하지 않는 것:** BMAD 를 실제로 설치하지 않는다. `.agents/skills/**` 를 건드리지 않는다.
  BMAD 템플릿을 다시 쓰지 않고 벤더링하지 않는다. deferred 5종의 보류 판정을 뒤집지 않는다.
  `capabilities.yaml` 의 MCP·브라우저 프로브는 M3 의 다른 조각이므로 여기서 만들지 않는다.
- **전달 메시지:** 부품은 라우터가 켤 때만 쓴다(K-60). 이 단위가 하는 일은 부품을 켜는 것이 아니라
  **언제 무엇을 추천할지의 규칙**을 정책표에 적는 것이다. 추천은 실행이 아니고, 설치 흔적은 실행 증거가 아니다.

## 열린 질문

- BMAD installer 가 `.agents/skills/` 의 romeo 스킬 12개를 지우거나 덮어쓰는지는 설치해 봐야 안다.
  이 단위는 설치하지 않으므로 답이 나오지 않는다 — 다음 단위(실제 설치 + K-68 관측)로 넘긴다.
- CIS agent 없이 workflow SKILL 을 직접 호출하는 경로, Codex 런타임에서의 `bmad-*` discovery 도 같은 이유로 미관측이다.

## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
