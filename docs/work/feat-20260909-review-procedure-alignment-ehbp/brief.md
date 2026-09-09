---
id: feat-20260909-review-procedure-alignment-ehbp
type: brief
title: 검토자 절차의 요구와 안내를 같은 자리에서 맞춘다 — 봉인·라벨·회차·반박
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

# 검토자 절차의 요구와 안내를 같은 자리에서 맞춘다 — 봉인·라벨·회차·반박

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

검토자 절차에서 **요구하는 자리와 보는 자리가 다른**(§11 ②) 세 자리를 맞춘다 — 종료 검사가 요구하는 봉인 명령·방어 검사 라벨을 절차 문서가 모르는 것(Q-96) · 검토자 계약이 관통 회차를 만드는 것(Q-95) · 반박 검사가 첫 파일만 읽는 것(Q-94).

## 배경과 대상

- **왜 지금:** 바로 앞 관통이 §12 로 남긴 넷 중 셋이고, **Q-96 은 그 관통에서 실제로 두 번 close 를 막았다.** 나머지 후보는 전부 관측만 됐고 아직 아무도 막지 않았다. 다음 마일스톤(M4 지표)의 단위도 검토자를 붙이므로 지금 고치지 않으면 같은 두 자리에서 또 막힌다.
- **누구를 위한 것:** 절차 문서를 읽고 검토자를 띄우는 사람과 런타임. 지금은 `adapters/orca/RUNBOOK.md` 를 따로 읽지 않으면 close 를 통과할 수 없다.
- **성공하면 무엇이 달라지나:** 절차 문서만 읽고 검토자를 띄운 실행이 통과한다. 라벨이나 명령 이름을 코드에서 바꾸면 안내가 따라오지 않은 것을 검사가 지목한다. 검토자만 다시 띄운 실행이 §10 의 회차를 늘리지 않으면서도 이력에는 남는다.

## 방향

- **하려는 것:** 요구를 코드에서 읽어(`close.DEFENSIVE_LABELS` · CLI 파서가 등록한 서브커맨드) 안내 문서 셋과 대조하는 검사를 만들고, 그 셋에 실제로 적는다. 검토자 계약이 회차 대신 `reviewer_runs:` 에 남게 한다. 반박 검사가 `inputs:` 의 모든 반박 파일을 보게 한다.
- **하지 않는 것:** `romeo/close.py` 의 판정 로직과 `DEFENSIVE_LABELS` 값을 바꾸는 것 — 요구는 그대로 두고 안내가 따라가게 한다. `adapters/orca/RUNBOOK.md` 도 고치지 않는다(이미 옳게 적혀 있다). Q-97(승격 문서 「범위」 절 대조)과 Q-83(계약·증거 생성의 판정 리비전)은 크기가 달라 열어 둔다.
- **전달 메시지:** 요구를 적고 안내를 잊으면, **지시대로 따른 실행이 막히고 지시를 따로 찾아 읽은 실행만 통과한다.** 가드 안내에서 한 번 겪은 모양(`feat-20260903-guard-guidance-vendor-drift-bvjz`)이 검토자 절차에서 되풀이됐다 — 그때 만든 대조 검사가 이 단위의 설계 선례다.

## 열린 질문

- 없음 — 자리 선택 두 건은 확정 단계에서 사용자가 골랐다. 다만 「`reviews:` 목록에 남긴다」는 그 목록이 §10 브레이크를 푸는 자리라 `reviewer_runs:` 로 나눈다(Tech Spec 확인란의 「결정 필요」에 적었다).


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
