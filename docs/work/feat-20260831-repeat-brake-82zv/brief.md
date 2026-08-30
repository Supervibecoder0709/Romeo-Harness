---
id: feat-20260831-repeat-brake-82zv
type: brief
title: 반복 중단 브레이크를 실제로 걸고 expect 함정을 없앤다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
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
created: '2026-08-31'
updated: '2026-08-31'
---

# 반복 중단 브레이크를 실제로 걸고 expect 함정을 없앤다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

정비 반복이 끝나 보이지 않는 원인은 결함 수가 아니라 **멈추라고 말해 줄 장치가 꺼져 있는 것**이다.
그 브레이크를 실제로 걸고, 함정 하나를 없애고, 나머지는 전부 넘긴다. **이 단위 뒤 하네스 정비를 멈춘다.**

## 배경과 대상

- **왜 지금:** 라운드마다 결함이 새로 나오는 것은 자기 자신을 실사용으로 시험하는 하네스에서 당연한 일이고, 실제로 **차단급 결함은 2 → 1 → 0 → 0 으로 줄었다**(수렴하고 있다). 문제는 다른 데 있다 — §10 이 "연속 2회 실패하면 멈춘다" 고 말하는데 그 장치가 두 군데서 샌다. 이 상태로 M3(BMAD 부품 46개)에 들어가면 훨씬 비싼 자리에서 같은 반복이 난다.
- **누구를 위한 것:** 다음 관통을 돌리는 사람. 그리고 그 사람이 "이제 그만해야 하나" 를 스스로 판단하지 않아도 되게 하는 것이 목적이다.
- **성공하면 무엇이 달라지나:** 같은 완료 정의를 향한 관통이 연속 2회 실패하면, **어느 경로로 돌리든** 3회차가 시작되지 않는다 — 사람이 재검토를 기록하기 전까지. 지금은 손으로 돌면 게이트가 아예 평가되지 않고, `run-unit` 으로 돌아도 재검토 한 번에 카운터가 0 이 된다.

## 방향

- **하려는 것:** 코드를 규칙 문장에 맞춘다 — `AGENTS.core.md` §10 의 문장은 바꾸지 않고 `run_unit.py` 를 고친다. 게이트를 **모든 관통이 반드시 지나는 자리**(`envelope build`)로 옮겨 강제한다. `expect` 는 구현하지 않고 **지운다** — 사람이 조건으로 쓰는데 기계가 안 보는 필드는 함정이고, 없애는 쪽이 싸다.
- **하지 않는 것:** 우회 가능한 마찰 6건(⑤ⒹⒻ + w3qu 잔여 3건)은 고치지 않고 `open-questions.md` 로 넘긴다. w3qu 는 **닫지도 폐기하지도 않고** park 한다 — 구현은 브랜치 `a1f543a` 에 보존돼 있다. `romeo/parity.py` 의 `expect` 는 다른 것이므로 건드리지 않는다.
- **전달 메시지:** 하네스는 완전해질 수 없다. 목표가 완전성이면 끝이 없고, 목표가 "쓸 수 있음" 이면 이미 도달했다. 남은 것은 **멈출 수 있게 만드는 것** 하나다.

## 열린 질문

- `envelope build` 가 차단됐을 때 그 자리에서 재검토를 기록할 우회 수단을 둘지, 아니면 `run-unit --after-review` 를 거치게 할지. 전자는 손으로 도는 경로를 편하게 하고, 후자는 기록 경로를 하나로 유지한다. 구현자가 실측해 정하고 이유를 결과 봉투에 남긴다.
- 이 단위 뒤 M3 진입 전에 남는 것은 **G-M3 후보표 → 사용자 확정**(D-52) 하나다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
