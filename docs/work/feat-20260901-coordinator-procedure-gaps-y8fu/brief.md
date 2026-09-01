---
id: feat-20260901-coordinator-procedure-gaps-y8fu
type: brief
title: 코디네이터 위임 절차 결함 3건 정비 — 재검토 커밋·재작업 재위임·Run 바인딩
unit: T1
mode: delivery
intent: write
facets: [docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: low
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
  fired_rules: ['profile:base:T1=standard', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-01'
updated: '2026-09-01'
---

# 코디네이터 위임 절차 결함 3건 정비 — 재검토 커밋·재작업 재위임·Run 바인딩

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

관통과 관통 사이의 하네스 정비 2회 — 직전 정비(`feat-20260831-park-defects-actm`)가 돌면서 드러났지만
그 단위 범위 밖이었던 **위임 절차 결함 3건**을 닫는다.

## 배경과 대상

- **왜 지금:** 코어 규칙 §10 이 관통 시작 뒤 하네스·절차 변경을 금지한다. 지금은 진행 중인 관통이 없고,
  다음 작업(M3 — charter·capabilities·gate·시나리오)은 위임으로 돈다. 그 관통을 시작하면 동결이 걸려
  이 세 가지를 다음 관통이 끝날 때까지 못 고친다. **정비는 관통과 관통 사이에만 가능하다.**
- **누구를 위한 것:** 다음 관통에서 코디네이터를 맡는 사람. 구현자·검토자 워커가 아니라 **위임하는 쪽**이
  밟는 절차의 결함이다 — 셋 다 워커에게는 원인이 보이지 않는 형태로 나타난다(브레이크가 안 풀리고,
  계약 생성이 거부되고, 명령이 종료 코드 0 으로 조용히 무시된다).
- **성공하면 무엇이 달라지나:** 세 가지를 **절차를 순서대로 밟다가** 만난다. 지금은 ① 은 어디에도 없고,
  ② 는 어디에도 없으며, ③ 은 1,164줄 문서의 맨 뒤 관측 표에만 있다 — 절차를 밟는 사람은 그것을 만나지 못한다.

## 방향

- **하려는 것:** 세 결함을 `adapters/orca/RUNBOOK.md` 의 **실행 순서 절**에 반영하고, ① 의 확인이 두 경우를
  실제로 가른다는 것을 반례 테스트로 고정하며, ③ 의 되돌리는 방법이 작동하는지 실행으로 관측한다.
- **하지 않는 것:** 하네스 코드의 동작을 바꾸지 않는다 — `_stamp_ids` 의 거부도, `repeat_gate` 의 브레이크도
  그대로 둔다. 둘 다 **의도된 방어**이고 이 단위가 고치는 것은 그 방어에 걸리지 않는 절차다.
  Orca CLI 자체도 바꾸지 않는다(우리 저장소 밖이다). M3 의 어떤 항목도 이 단위에 넣지 않는다.
- **전달 메시지:** 관통이 드러낸 것을 관통 사이에 절차로 만든다. 세 결함 모두 "다음에 기억하자" 로는
  닫히지 않는 것들이다 — ① 은 이미 두 번 같은 방식으로 걸렸다.

## 열린 질문

- ③ 의 전환이 되는 것과, 전환 뒤 옛 Run 의 메시지를 읽을 수 있는 것은 **별개**다. 2026-08-29 관측은 전자만 말한다.
  후자가 안 되면 그 사실 자체를 절차에 적고(대기 중에는 Run 을 새로 만들지 않는다), 남는 제약은 열린 질문으로 연다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
