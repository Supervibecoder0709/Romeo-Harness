---
id: feat-20260830-runbook-delegation-gaps-biae
type: brief
title: RUNBOOK 위임 절차 결함 6건 정비 — 관통이 드러낸 관측을 절차로 만든다
unit: T1
mode: delivery
intent: write
facets: [docs]
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
created: '2026-08-30'
updated: '2026-08-30'
---

# RUNBOOK 위임 절차 결함 6건 정비 — 관통이 드러낸 관측을 절차로 만든다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

다음 관통에서 그대로 다시 걸릴 **위임 절차 결함 6건**을 `adapters/orca/RUNBOOK.md` 에 적는다 —
지난 두 관통에서 실제로 관측한 것을 문서로 만들 뿐, 코드는 건드리지 않는다.

## 배경과 대상

- **왜 지금:** 바로 다음 작업이 `feat-20260830-harness-defects-w3qu` 의 5회차 관통이고, 여섯 건 중 셋(ⒶⒷⒸ)은 직전 관통에서 실제로 걸린 것이다. 코어 규칙 §10 은 관통이 시작된 뒤 하네스 변경을 금지하므로 고칠 수 있는 구간은 관통과 관통 **사이**인 지금뿐이다.
- **누구를 위한 것:** 다음 관통을 위임하는 쪽(사람 또는 조정 런타임). 이 문서를 읽고 명령을 그대로 옮겨 쓰는 자리다.
- **성공하면 무엇이 달라지나:** 위임하는 쪽이 여섯 가지를 **문서에서** 찾는다. 지금은 지난 세션의 대화나 `progress.md` 의 상태 블록에만 있어서, 세션이 바뀌면 같은 함정을 다시 밟는다. 실제로 ④ 는 §3.7 의 표가 잘못된 축으로 그려져 있어 두 번 밟았다.

## 방향

- **하려는 것:** 관측된 것을 관측으로 적는다. 표본이 1~2건인 항목은 규칙으로 단정하지 않고 관측으로만 남긴다(K-51). ④ 는 표의 축을 바꾸면서 옛 축을 **지운다** — 두 서술이 공존하면 어느 쪽이 맞는지 알 수 없기 때문이다.
- **하지 않는 것:** 코드·스키마·정책표·권한 상한을 바꾸지 않는다. 남아 있는 하네스 결함 ②(`expect` 가 판정에 쓰이지 않는다)·③(반복 중단 카운터)·⑤(비대화형 검토자 lifecycle 자동화)는 이 단위 밖이다 — 그것들은 코드 변경이고, 이 단위는 문서 전용으로 유지해 실패 지점을 줄인다.
- **전달 메시지:** 관통이 드러낸 것을 문서에 되먹이지 않으면 같은 관통을 다시 돈다. 이 단위는 그 되먹임 한 번이다.

## 열린 질문

- Ⓑ 의 절차 결론이 **실측에 달려 있다** — `task-update` 가 계약 지문(`--spec`) 갱신을 받는지에 따라 「그 명령을 쓴다」가 되거나 「Run 을 새로 만든다」가 된다. 구현자가 `--help` 로 확인해 정하고, 어느 쪽인지 근거와 함께 적는다.
- ⑦ 의 실제 모델 id 를 문서에 박을지 조회 방법만 적을지 — 값은 바뀌므로 조회 방법 쪽으로 기운다. 구현 시 정한다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
