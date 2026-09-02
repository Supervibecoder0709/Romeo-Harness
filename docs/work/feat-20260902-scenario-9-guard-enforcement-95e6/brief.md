---
id: feat-20260902-scenario-9-guard-enforcement-95e6
type: brief
title: 승인 없이는 되돌리기 어려운 것을 실행하지 않는다 — 가드 설명 요구·거부 경로·시나리오 9
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
created: '2026-09-02'
updated: '2026-09-02'
---

# 승인 없이는 되돌리기 어려운 것을 실행하지 않는다 — 가드 설명 요구·거부 경로·시나리오 9

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

시나리오 9 — 실행 가드 집행. 되돌리기 어려운 요청("아카이브 1개 삭제")에서 가드가 발동해
**설명 넷을 받아야만** 승인으로 세고, 사람이 거부하면 그 사실이 봉인된 기록으로 남아
종료 검사가 `BLOCKED_APPROVAL` 로 판정한다. 시나리오 3·8 과 같은 형식의 런북과 재현 테스트로 고정한다.


## 배경과 대상

- **왜 지금:** M3 종료 조건(계획 §10 #13)은 시나리오 3·8·9 런북 PASS 이고 9 만 남았다. 그리고
  관통 사이 정비 구간인 지금이 하네스를 고칠 수 있는 유일한 구간이다(AGENTS.core §10 동결).
  가드의 계산·인쇄·계약 전달·종료 집행은 이미 서지만, 요구를 적고 집행을 잊은 자리가 둘 남아 있다 —
  `required_explanation` 4항목은 저장소 전체 grep 1건 = 정의 자리뿐이고, 사람이 거부한 것을
  기록할 자리가 아예 없다.
- **누구를 위한 것:** 되돌리기 어려운 실행을 승인해야 하는 사람. 지금은 승인 버튼만 있고
  "무엇을 보고 판단해야 하는가" 를 요구하는 자리가 없어, 판단 없이 눌린 승인과 판단한 승인이
  기록에서 구별되지 않는다.
- **성공하면 무엇이 달라지나:** 가드가 걸린 실행의 승인 기록에는 영향 범위·사전 백업·복구 방법·
  확인할 내용이 반드시 남는다. 거부는 흔적 없이 사라지지 않고, 종료 검사가 "아직 안 물어봤다"와
  "물어봤고 사람이 아니라고 했다"를 다르게 말한다 — 후자는 재시도가 답이 아니기 때문이다.

## 방향

- **하려는 것:** ① 설명 요구를 정책표에서 기계가 읽을 수 있는 구조로 만들고, 승인 기록 시점과
  종료 검사 두 지점에서 대조한다. ② 거부를 승인과 같은 방식으로 봉인해 기록하는 창구를 만들고,
  종료 검사가 그 결정을 판정에 쓴다. ③ `gate-create` 를 코어에서 걷어내 어댑터가 소유하게 한다(C-C6).
  ④ 런북 `scenarios/9-guard-approval.md` 와 재현 테스트로 고정한다 — 반례를 단계로 담는다.
- **하지 않는 것:** 가드의 **발동 조건**(어떤 요청에 어떤 가드가 붙는지)은 그대로다 · 실제 삭제·배포·
  외부 상태 변경은 하지 않는다(이 시나리오는 gate 거부로 끝나는 것이 정의다) · `enforcement:` 블록의
  `claude`·`codex` 키에 남은 벤더명은 같은 모양의 문제지만 이 요청은 `gate-create` 만 겨눈다 —
  발견으로 열어 둔다(§12) · 이미 닫힌 단위에 소급하지 않는다 · 실제 T2 관통과 다른 park.
- **전달 메시지:** 승인은 버튼이 아니라 **설명**이다. 설명 없이 눌린 승인은 승인으로 세지 않고,
  사람이 아니라고 한 것은 기록으로 남아 다음 시도가 같은 것을 반복하지 않게 한다.

## 열린 질문

- 없음


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
