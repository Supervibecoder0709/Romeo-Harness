---
id: feat-20260903-runbook-handle-attempts-drift-w7tm
type: brief
title: 런타임이 소유한 값을 확인 기준으로 쓰지 않는다 — 핸들 확인·attempts 정본
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
created: '2026-09-03'
updated: '2026-09-03'
---

# 런타임이 소유한 값을 확인 기준으로 쓰지 않는다 — 핸들 확인·attempts 정본

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

위임 절차가 **런타임이 소유한 값(터미널 제목)** 을 확인 기준으로 쓰던 것과, 관통을 통합할 때
**회차 판정이 조용히 사라지던 것** 을 함께 닫는다 — 다음 T2 관통이 지나는 경로 위의 결함 2건이다(Q-47·Q-48).

## 배경과 대상

- **왜 지금:** 다음 관통은 charter 를 쓰는 실제 T2 관통이고, 두 결함은 그 관통이 반드시 지나는 위임 경로 위에 있다.
  §10 동결 규칙상 관통이 시작되면 하네스를 고칠 수 없으므로, 정비의 자리는 관통과 관통 사이다.
- **누구를 위한 것:** 위임 절차(RUNBOOK §3)를 손으로 밟는 코디네이터와, 관통 결과를 통합하는 사람.
- **성공하면 무엇이 달라지나:** §3.7 을 글자 그대로 밟아도 핸들 확인이 성립하고(제목이 무엇으로 바뀌어 있든),
  판정을 잃은 통합은 종료 코드로 막힌다. 지금은 둘 다 사람이 눈치채야만 넘어간다.

## 방향

- **하려는 것:** ① §3.7 의 핸들 확인 기준을 제목에서 **핸들 + 워크트리 id** 로 옮기고 그 근거(실측)를 같은 자리에 적는다.
  ② 워크트리 사본이 위임 쪽 판정을 잃었는지 보는 명령(`run-unit merge-check`)을 만들고, 통합 직전에 그것을 밟는 자리를 절차에 둔다.
- **하지 않는 것:** `run-unit check`(§3.1 확인 4)의 판정·재검토만 대조하는 규칙을 바꾸지 않는다(Q-39 의 결정).
  회차를 만드는 자리(§10)와 워크트리 안 `envelope build` 의 동작도 그대로 둔다. 통합 자체를 자동화하지 않는다 —
  이 단위가 만드는 것은 통합을 **막을 수 있는 판정**이지 통합 절차가 아니다.
- **전달 메시지:** 확인 기준으로 쓸 수 있는 값과 쓸 수 없는 값이 있다. 다른 주체가 언제든 바꿀 수 있는 값(제목)은
  기준이 될 수 없고, 그것을 기준으로 적은 절차는 「막다른 길」이라는 모양으로만 드러난다.

## 열린 질문

- 없음 (Q-47·Q-48 은 이 단위가 닫는 대상이고, 열린 채로 남기지 않는다)


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
