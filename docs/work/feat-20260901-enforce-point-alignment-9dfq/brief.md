---
id: feat-20260901-enforce-point-alignment-9dfq
type: brief
title: 요구하는 자리와 보는 자리를 같게 둔다 — 집행 지점 어휘·차단 충족 조건·절 로드 대조
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
created: '2026-09-01'
updated: '2026-09-01'
---

# 요구하는 자리와 보는 자리를 같게 둔다 — 집행 지점 어휘·차단 충족 조건·절 로드 대조

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

차단이 무엇을 언제 어느 문서로 보는지를 선언하게 하고, 라우터가 요구한 절을 아무도 읽지 않는 상태를 로드 시점에 막는다

## 배경과 대상

- **왜 지금:** 2026-09-01 Codex 아키텍처 검토와 그 교차 대조가 실측으로 확정했다 — 바로 앞 단위
  (`feat-20260901-charter-discovery-block-a3xs`)가 세운 차단 4개가 **여전히 아무것도 막지 못한다.**
  `inputs: ["ㅁㄴㅇㄹ"]` 로 승인이 통과하고, 조사 단위는 조사 결과를 먼저 요구받아 조사를 시작할 수 없으며,
  라우터가 필수라고 판정한 절이 `brief.md` 에 있으면 승인·종료·CI 셋 다 그것을 읽지 않는다.
  M3 시나리오 3 의 수용 기준이 지금 이 상태로 서 있으므로 정비가 아니라 M3 본체 재작업이다.
- **누구를 위한 것:** 이 하네스를 쓰는 다음 작업 단위 전부. 특히 조사(discovery)와 T2 이니셔티브 —
  지금 그 두 경로가 가장 헐겁다.
- **성공하면 무엇이 달라지나:** 차단이 **무엇을 · 언제 · 어느 문서로** 보는지를 스스로 선언하고,
  선언과 집행이 어긋나면 정책이 로드되지 않는다. 라우터가 요구했는데 아무도 읽지 않는 절이 생길 수 없다.

## 방향

- **하려는 것:** ① 집행 지점 어휘에 `dispatch`(구현 위임 직전)를 더하고 차단마다 주 사건 하나를 선언한다.
  ② 차단마다 정본 입력 문서(`reads:`)를 선언하고, 충족을 '그 자리에 글자가 있는가' 에서 '그 문장이 참인가' 로 바꾼다.
  ③ 미완료 검사를 spec 하나가 아니라 **그 단위의 문서 패키지 전체**에 건다. ④ 정책표의 절마다 누가 그것을 집행하는지
  선언하게 하고 로드 시점에 대조한다. ⑤ `approval-gate` 를 실제 의미로 개명하고 실행 승인은 `guards` 소유임을 명시한다.
  ⑥ 같은 훅에서 Q-27 을 닫는다.
- **하지 않는 것:** 새 `execute` 집행 지점을 만들지 않는다 — `core/policy/execution-guards.yaml` 의 `guards` 가
  이미 실행 시점 승인을 소유하고, 승인 기록을 원시 로그로 봉인한다. 두 이름으로 같은 일을 하지 않는다.
  이미 `done` 인 단위에 소급하지 않는다. `docs/source-context/` 와 옛 리뷰 라운드의 `approval-gate` 표기는 건드리지 않는다 —
  그것들은 그때의 기록이다.
- **전달 메시지:** 요구를 적는 자리와 그것이 충족됐는지 보는 자리를 같게 둔다. 어긋나면 돌지 않는다.

## 열린 질문

- `dispatch` 집행 훅을 `romeo/envelope.py` 의 계약 생성에 거는 것이 모든 경로를 덮는가.
  Q-27 은 "계약 생성은 어느 경로로 돌리든 반드시 지나는 첫 동작" 이라고 적지만 실측하지 않았다 —
  구현 단위 1 이 이것을 먼저 확인한다.
- 차단 id 개명(`approval-gate` → `risk-plan-ready`)이 요청 fixture 5건의 기대값을 바꾼다.
  양성 증명에서 일괄 치환만으로 `tests.test_policy` 21건이 통과했으나 치환이 의미상 옳은지는 검토자가 본다.
- **`spec_max_lines: 150` 이 템플릿보다 작다.** 빈 T1 spec 이 이미 108줄이라 내용에 쓸 자리가 42줄뿐이고,
  최근 단위는 전부 144~155줄이다. 이 spec 도 178줄이라 `BUDGET_EXCEEDED` 경고가 뜬다 —
  경고이지 차단이 아니어서 승인·종료를 막지는 않는다. 템플릿은 2026-09-01 park 정비(Q-20·Q-21)로
  커졌는데 예산은 그대로다. **요구를 적는 자리와 그것을 재는 자리가 다른** 같은 생성기의 또 한 사례다.
  이 단위 밖이므로 고치지 않고 park 한다 — 다음 T0 정비 단위의 후보다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
