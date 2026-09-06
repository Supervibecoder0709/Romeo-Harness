---
id: feat-20260906-m4-attach-requirements-3mcv
type: brief
title: M1~M3 이 낸 구멍을 M5 attach 요구사항 목록으로 정리한다
unit: T1
mode: delivery
intent: write
facets: [docs, tooling]
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
created: '2026-09-06'
updated: '2026-09-06'
---

# M1~M3 이 낸 구멍을 M5 attach 요구사항 목록으로 정리한다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 docs, tooling · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

부모 이니셔티브 `init-20260904-attach-payload-manual-rreq` 의 마지막 마일스톤 M4 —
세 관통(M1 부착 · M2 라우터 · M3 close)이 낸 관측 Q-53~Q-68 **16건**을
`attach` 명령이 답해야 할 요구사항 목록 한 장으로 모으고, 출처 가리킴을 검사로 고정한다.

## 배경과 대상

- **왜 지금:** 세 관통이 전부 닫혔고 남은 것이 이 정리뿐이다. 관측은 지금 `open-questions.md` 68건 안에
  흩어져 있고, 「이건 `attach` 가 답할 것」이라는 판단이 각 항목 본문의 산문으로만 존재한다 —
  본문에 `M5` 를 쓴 것은 6건뿐인데 세 단위를 출처로 가진 것은 16건이다. 그 차이가 다음 이니셔티브를 여는 사람에게 그대로 넘어간다.
- **누구를 위한 것:** `attach`·`update --dry-run`·롤백 명령을 세우는 다음 이니셔티브의 `/plan`.
  그 사람이 68건을 다시 읽어 같은 판단을 반복하지 않게 하는 것이 목적이다.
- **성공하면 무엇이 달라지나:** 다음 이니셔티브가 **요구사항 목록에서 시작한다**. 그리고 그 목록이 낡으면
  — 새 관측이 목록에 안 올라가거나 출처가 없는 것을 가리키면 — CI 가 실패로 드러낸다.
  지금은 문서가 낡아도 아무 일도 일어나지 않는다.

## 방향

- **하려는 것:** 요구사항 목록 문서 1장(올린 것 · 뺀 것 두 표) + 출처 대조 검사 1건 + 부모 이니셔티브 종료를 상태 블록에 반영.
- **하지 않는 것:** 구멍을 **고치지 않는다** — `romeo/` 를 한 줄도 건드리지 않는다(§12).
  `attach` 명령을 만들지 않는다(charter 비범위). Q 항목 본문을 다시 쓰지 않는다 — 출처로 읽기만 한다.
  대상 저장소 `My-Automated-Worker/instagram-dm-sender` 를 다시 열지 않는다.
- **전달 메시지:** 「하네스를 남의 저장소에 손으로 붙여 보니 이 16가지가 걸렸고, 그중 이것들이 `attach` 가 답해야 할 것이다.
  뺀 것도 왜 뺐는지 남겼다.」

## 열린 질문

- 없음 (구멍의 범위와 출처 집행 방식은 2026-09-06 사용자 확정)


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
