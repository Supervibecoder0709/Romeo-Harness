---
id: feat-20260913-seal-fill-scope-alignment-5sek
type: brief
title: 요구하는 자리에서 본다 — 봉인·채움·검사 범위의 세 자리
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
inputs: [inputs/ac-rebuttal-20260913.md, inputs/probe-20260913.md]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-13'
updated: '2026-09-13'
---

# 요구하는 자리에서 본다 — 봉인·채움·검사 범위의 세 자리

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

관통 절차의 세 자리에서 **요구를 적은 문서와 그것을 보는 코드가 어긋나** 있다 — 봉인(Q-103)·채움(Q-104)·검사 범위(Q-105 ①).
셋을 각자의 요구 자리에서 보게 만든다.

## 배경과 대상

- **왜 지금:** M5 M2 첫 단위가 **4회차**로 닫혔고(통합 `fa1b73e`), 그 회차 중 하나는 산출물이 아니라 **절차** 때문이었다.
  Q-103 은 2026-09-11 M5 M1 관통에서 회차 하나와 재승인 한 번을 실제로 태웠다 — 방어 검사 없이 돌린 검토를
  `review record` 가 두 번 다 `exit 0` 으로 봉인했고, 그것이 틀렸다는 것은 close 에 가서야 `REVIEW_VERDICT UNVERIFIED` 로 드러났으며,
  봉인된 run 에는 더 쓸 수 없다(Q-101). 다음 관통(M5 M2 둘째 단위 — `romeo attach`)은 Q-58 이 대상 저장소의 실행 권한을 넓히는 일이라
  게이트와 가드가 붙는 무거운 관통이다. 회차 하나의 비용이 지금보다 크므로 **그 전에** 닫는다(AGENTS.core §10: 정비는 관통 사이에).
- **누구를 위한 것:** 이 하네스로 다음 관통을 도는 실행 — 구현자·검토자·위임하는 사람.
- **성공하면 무엇이 달라지나:** 세 실수가 **일어난 자리에서** 드러난다. 방어 검사를 빠뜨린 검토는 봉인 시점에 경고를 받고(회차 하나를 아낀다),
  검토자 브리프의 `base_sha` 는 옮겨 적을 값이 아니라 계약 파일에서 읽는 값이 되며, 충돌 fixture 는 자기가 어느 저장소를 검사하는지 스스로 말한다.

## 방향

- **하려는 것:** 세 자리를 각자의 요구 자리에서 보게 한다. ① `review record` 가 봉인 전에 close 와 **같은** 방어 검사 목록을 보고
  없으면 경고한다(막지 않는다 — K-31). ② `fill_brief.py` 가 검토자 계약 파일 하나를 받아 `base_sha` 와 계약 sha256 을 거기서 읽는다 —
  옮겨 적는 인자를 없앤다. ③ 충돌 fixture 가 검사 대상 저장소(하네스인가 부착 대상인가)를 선언하고 `check_conflicts` 가 그 선언을 읽는다 —
  선언이 없는 fixture 가 있으면 멈춘다.
- **하지 않는 것:** Q-105 ②(심링크 경계)는 **범위 밖**이다 — 지금 그런 링크가 없어 발동하지 않고, §12 는 요청을 푸는 가장 작은 합리적 변경을 고르라고 한다.
  Q-105 에 열린 채로 남긴다. M5 M2 둘째 단위의 내용(`romeo attach`·Q-58·Q-59·Q-106)도 손대지 않는다.
  `review record` 를 **차단**으로 바꾸지 않는다 — 막으면 이 명령이 없던 시절의 봉투나 손으로 쓴 봉투를 되살릴 길이 사라진다.
- **전달 메시지:** 세 결함은 전부 §11 의 같은 모양이다 — 요구는 문서에 인쇄됐고 그것을 보는 코드는 다른 것을 보거나 아무것도 보지 않았다.
  고치는 방향도 하나다: **요구가 사는 자리를 검사가 읽게 한다.**

## 열린 질문

- `_check_c7` 을 하네스 쪽으로 옮기면 c7 은 「대상을 검사하는 fixture」가 아니라 「하네스 자기검사 fixture」가 된다.
  그러면 `check_conflicts` 의 실행 수가 세는 것이 무엇인지 정해야 한다 — 이 단위가 fixture 의 선언 필드로 답한다(Tech Spec 구현 단위 3).

## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
