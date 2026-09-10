---
id: feat-20260910-sealed-run-worker-settle-37qi
type: brief
title: 봉인된 run 에는 더 쓰지 않는다 — 살아남은 워커의 증거 오염을 절차와 기록 두 자리에서 막는다
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

# 봉인된 run 에는 더 쓰지 않는다 — 살아남은 워커의 증거 오염을 절차와 기록 두 자리에서 막는다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

Q-101 정비 — 검토 봉투가 기록된(봉인된) run 에 살아남은 워커가 검사를 다시 쓰면 그 run 의 증거가 두 산출물에 걸쳐 판정이 서지 않고 되돌릴 수도 없다. **절차**(재작업 위임 전에 앞 워커가 죽었는지 관측 · `worker-stop` 거부 시 복구 경로)와 **기록 코드**(봉인된 run 에 대한 쓰기를 거부) 두 자리에서 막는다.

## 배경과 대상

- **왜 지금:** 바로 앞 관통(`feat-20260909-metrics-four-counters-dyz2`)의 2회차가 이 결함으로 탔다 — 검토자 PASS 까지 마친 봉투를 `review-spoiled/` 로 옮기고 3회차를 다시 돌려야 close 가 섰다. 절차의 어느 자리도 「앞 회차의 워커를 확실히 죽인다」를 요구하지 않고, `worker-stop` 이 거부할 수 있다는 것도 적혀 있지 않으며, 기록 코드는 봉인 뒤에도 무조건 append 한다. 다음 관통(D-81 ④ shadow 20건)도 재작업 위임을 밟으므로 고치지 않으면 같은 자리에서 또 회차 하나를 태운다.
- **누구를 위한 것:** 재작업을 위임하는 코디네이터(RUNBOOK §3.4.2 를 밟는 사람과 런타임)와 그 뒤 종료 검사. 지금은 코디네이터의 기억에만 의존한다.
- **성공하면 무엇이 달라지나:** 봉인된 run 에 증거를 더 쓰려는 명령은 아무것도 쓰지 않고 실행하지도 않은 채 exit 1 로 끝난다 — 살아남은 워커가 있어도 봉인된 판정은 오염되지 않는다. 재작업 위임 절차가 앞 dispatch 의 settle 을 관측으로 확인하고, 거부된 `worker-stop` 뒤의 길이 적혀 있다.

## 방향

- **하려는 것:** `romeo/evidence.py` 에 봉인 판정 하나(그 run 의 명령 기록에 `review-record` 라벨이 있는가)를 두고 `evidence run`·`evidence checks`·`review record` 세 경로가 쓰기·실행보다 먼저 그것을 보게 한다. RUNBOOK §3.4.2 의 첫 단계로 `worker-show` 관측을 넣고, §7 표에 `worker-stop` 거부 행과 `terminal close` 복구 경로를 더한다. 코어 구현 절차에 「봉인된 run 에는 더 쓰지 않는다」 한 문장을 적는다.
- **하지 않는 것:** `romeo/close.py` 의 판정 로직은 바꾸지 않는다 — 오염을 **읽는 자리**에서 걸러내는 대신 **쓰는 자리**에서 막는다. 가드 결정(`approve`·`reject`)의 기록은 대상이 아니다(명령 배열이 아니고 산출물 식별에 들어가지 않는다). 거부에 우회 플래그를 두지 않는다 — 다시 검토받으려면 새 run 이다(K-51). `orca terminal close` 가 거부된 워커를 실제로 죽이는지는 이 단위에서 관측하지 않고 「미관측」으로 적는다. Q-100(재분류 기록 경로)은 모양이 달라 열어 둔다.
- **전달 메시지:** **한 run 의 증거는 봉인 뒤에 닫힌다.** 옛 run 에 무엇을 더 쓰는 것은 — 살아남은 워커든 손이든 — 그 run 의 판정을 다른 산출물로 옮기는 일이고, 그것을 막는 자리는 판정이 아니라 기록이다(§11: 요구하는 자리와 보는 자리를 같게 둔다). 같은 모양의 방어가 이미 하나 있다 — `_stamp_ids` 의 「한 run 은 한 위임에 속한다」.

## 열린 질문

- 없음 — 거부 범위(어떤 명령도)와 복구 경로(`terminal close`)는 확정 단계에서 사용자가 골랐다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
