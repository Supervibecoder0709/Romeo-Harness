---
id: feat-20260911-attach-by-reference-and-index-amj9
type: brief
title: 부착을 참조로 바꾸고, 투영되는 인덱스를 대상에 실재하는 것으로 좁힌다
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
parent: init-20260911-m5-attach-update-rollback-sauc
inputs: [inputs/ac-rebuttal-20260911.md, inputs/ac-rebuttal-20260911-round2.md]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-11'
updated: '2026-09-11'
---

# 부착을 참조로 바꾸고, 투영되는 인덱스를 대상에 실재하는 것으로 좁힌다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

하네스가 **읽는 곳**과 **쓰는 곳**을 나눈다 — 대상에는 산출물만 놓이고, 그 산출물은 그 저장소에 실재하는 것만 가리킨다.

## 배경과 대상

- **왜 지금:** M1 이 「붙었는지 보는 눈」을 바로 달았다. 다음은 **무엇을 놓을지**인데, 지금은 대상 **안에서**
  소스를 읽는 구조라 소스 트리 여섯을 손으로 복사해야 부착이 성립한다. 그 사본은 하네스가 갱신되면 낡고,
  계획이 「override 가 코어를 복제하면 드리프트」라고 경고한 것이 그것이다. 붙이는 명령(`romeo attach`)을
  만들기 전에 **무엇을 놓을지**가 정해져야 한다 — 아니면 그 목록이 명령 코드에 굳는다.
- **누구를 위한 것:** 하네스를 자기 프로젝트에 붙이는 사람, 그리고 **부착된 저장소에서 도는 에이전트**다.
  후자는 지금 그 저장소에 없는 파일 5종을 세션 시작에 읽으라는 지시를 받는다(Q-60 실측).
- **성공하면 무엇이 달라지나:** 대상에 놓이는 것이 14개에서 8개로 줄고 소스 사본이 사라진다.
  주입된 지침이 거짓을 말하지 않는다. 충돌 검사가 대상에서도 **실제로 돈다** — 지금은 0종 실행으로 통과한다.

## 방향

- **하려는 것:** 읽는 경로에 `harness_root` 를 도입해 `compile` 과 `doctor` 의 충돌 검사가 하네스의 것을 읽고
  **대상을 검사**하게 한다. 그리고 `PROJECT.core.md` 의 절마다 투영 범위 표식을 두고 컴파일이 그것을 **읽어** 가른다.
- **하지 않는 것:** `romeo attach` 명령을 만들지 않는다(M2 의 다음 단위). 이미 복제해 둔 사본을 **지우지 않는다** —
  지우는 것은 Charter M3 의 `rollback` 이고 삭제는 승인 대상이다(K-66). `AGENTS.core.md` 의 행동 규범은
  **가르지 않는다** — 전부 모든 저장소에 간다.
- **전달 메시지:** 「부착은 사본을 두는 일이 아니라 산출물을 놓는 일이다. 낡을 사본이 없으면 드리프트도 없다.」

## 열린 질문

- 계획 §3.1 이 이 전환을 금지한다고 Q-54 가 적었으나 **전문에는 그 문장이 없다**(`implementation-plan.md:186-201`).
  금지 대상은 「override 가 코어를 복제하는 것」이다(:174·:198). 따라서 §3.1 개정도 D-xx 도 필요하지 않고,
  Q-54 의 그 서술은 이 단위가 해소할 때 함께 고친다.
- 대상의 `.harness/bindings.yaml` 도 참조로 돌린다. 프로젝트별로 달라질 여지는
  `.harness/romeo.project.yaml` 이 가져간다는 가정이고, 틀리면 그 하나만 예외로 되돌린다 — 미검증이다.

## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
