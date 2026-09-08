---
id: feat-20260909-promote-integrity-kchq
type: brief
title: 승격과 무결성 — 끝난 사실을 current/ 로 올리고, 링크·ID 중복을 검사한다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: high
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
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.high.small=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-09'
updated: '2026-09-09'
---

# 승격과 무결성 — 끝난 사실을 current/ 로 올리고, 링크·ID 중복을 검사한다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

끝난 사실이 모이는 자리 `docs/current/` 를 열고, 그 자리가 낡지 않도록 코드와 대조하는
검사 `romeo integrity` 를 세운다. M4 charter 의 마일스톤 M3 이다.

## 배경과 대상

- **왜 지금:** M4 이니셔티브의 M1(재사용 검색)·M2(1-hop 재개)가 닫혔고, 셋째 마일스톤이 승격과 무결성이다. 계획 §10 #14 의 관찰 가능한 결과 넷 중 「`docs/current/` 1건」과 「깨진 링크 0」이 이 단위의 몫이다.
- **누구를 위한 것:** 다음 세션의 자신. 지금은 「무엇이 무엇을 막는가」를 알려면 매번 `romeo/*.py` 를 열어 재구성해야 한다 — 이 단위를 여는 조사에서도 그 일을 한 번 했다.
- **성공하면 무엇이 달라지나:** 집행 목록이 한 파일에 서고, 코드가 그 목록을 앞질러 가면 검사가 exit 1 로 지목한다. 목록이 조용히 낡는 경로가 닫힌다.

## 방향

- **하려는 것:** `docs/current/enforcement.md`(집행 목록) · `romeo integrity`(대조·링크·ID 중복) · `romeo close` 의 승격 후보 경고 한 줄 · CI 한 줄.
- **하지 않는 것:** 차단하지 않는다 — `romeo close` 의 종료 판정에 이 검사를 넣지 않는다(charter 「하지 않는 것」). `decisions.md` append 는 M3 의 다음 단위로 뺐다. 무결성 검사의 범위를 `docs/planning/`·`docs/decisions/` 로 넓히지 않는다(§12).
- **전달 메시지:** 승격은 복사가 아니라 저술이다. 사본을 만들지 않는 유일한 방법은 그 사본을 검사가 계속 대조하는 것이다.

## 열린 질문

- 무결성 검사의 범위를 `docs/planning/`·`docs/decisions/` 까지 넓힐지 — 이 단위는 `docs/current/` 와 `docs/work/` 의 id 만 본다.
- `feat-20260830-harness-defects-w3qu` 가 `status: active` 로 남아 있는 것 — 이 단위의 요청 밖이라 고치지 않고 `open-questions.md` 에 연다(§12).


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
