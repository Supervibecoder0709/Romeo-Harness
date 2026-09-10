---
id: feat-20260910-router-fewshot-conflict-guidance-k8dd
type: brief
title: 오분류 예시를 정책표에 두고 카드가 그것을 읽어 인쇄한다 — 충돌 우선순위는 안내에 적는다
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
created: '2026-09-10'
updated: '2026-09-10'
---

# 오분류 예시를 정책표에 두고 카드가 그것을 읽어 인쇄한다 — 충돌 우선순위는 안내에 적는다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

분류를 틀리게 만드는 신호를 정책표에 예시로 적고, 분류 카드가 그것을 읽어 확정 화면에 인쇄한다. 지금은 그 예시를 둘 자리가 없다.

## 배경과 대상

- **왜 지금:** v1 릴리스 게이트(D-82)가 V-1 을 부분 충족으로 남겼다 — 요구한 few-shot 자리가 `core/workflows/plan/SKILL.md` 에도 `core/policy/classification.yaml` 에도 없다. 예시로 쓸 재료는 이미 모였다: shadow 20건의 사람 수정 3건 중 2건이 같은 유형이다. M5 attach 진입 전 정비 1회이고 범위가 작다.
- **누구를 위한 것:** 분류를 확정하는 사람과, 카드를 만드는 제안자다. 사람은 확정 화면에서 「이 신호가 있으면 불확실성이 medium 이다」를 읽고, 제안자는 그 문구가 정책표에 있으므로 다음 제안에서 참조할 자리를 갖는다.
- **성공하면 무엇이 달라지나:** 정책표에서 그 문구를 고치면 카드 출력이 따라 바뀐다. 지금은 정책표의 `two_questions` 전체를 카드가 한 번도 읽지 않는다 — 질문 문장과 레벨 정의가 적혀만 있고 아무도 보지 않는 값이다.

## 방향

- **하려는 것:** 예시 자리를 정책표에 만들고(항목 1건), 카드가 그것을 읽어 2질문 줄 아래에 인쇄한다 — 제안값이 예시의 레벨과 다를 때만. 함께 `/plan` 안내에 정책 충돌 우선순위 한 줄을 더한다.
- **하지 않는 것:** 라우터의 unit·profile·게이트 계산은 건드리지 않는다. 예시가 실제로 오분류를 줄이는지는 이 단위가 증명하지 않는다 — 다음 shadow 관측이 판정한다. shadow 기록과 Q-102 해소 표시도 이 단위 밖이다.
- **전달 메시지:** 요구하는 자리와 보는 자리를 같게 둔다(AGENTS.core §11). 예시를 산문으로만 적으면 아무도 읽지 않아도 드러나지 않는다.

## 열린 질문

- 없음


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
