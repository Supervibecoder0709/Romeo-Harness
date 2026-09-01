---
id: feat-20260901-task-copy-brief-count-erc6
type: brief
title: 관통이 매번 손대는 두 자리를 없앤다 — task/ 사본 병합 충돌·브리프 검사 개수 하드코딩
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

# 관통이 매번 손대는 두 자리를 없앤다 — task/ 사본 병합 충돌·브리프 검사 개수 하드코딩

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

관통 한 번을 돌 때마다 사람이 손으로 메우던 두 자리를 없앤다 — 작업 계약 사본이 통합(`git merge --ff-only`)을 막던 것과, 구현자 절차 문서가 검사 **개수**를 문장에 박아 두어 관통마다 `sed` 로 고쳐야 했던 것.

## 배경과 대상

- **왜 지금:** 코어 규칙 §10 이 관통 **중에는** 하네스를 못 고치게 한다. 지금은 정비 구간이고(정비 2회를 마쳤다), M3 는 앞으로 관통을 더 돈다. 두 결함 모두 **다음 관통에서 또 걸리는 것**이 직전 관통에서 실측됐다 — ①은 재승인 커밋을 `amend` 로 다시 만들게 했고(`f53d096` → `82a8191`), ②는 검사가 15건이라 문장을 손으로 고쳐 넘겼다.
- **누구를 위한 것:** 이 하네스로 관통을 돌리는 사람(코디네이터)과, 위임을 받아 구현하는 워커. 둘 다 지금은 **절차가 아니라 우회를 기억해야** 한다.
- **성공하면 무엇이 달라지나:** 통합이 `--ff-only` 로 그대로 지나가고, 구현자 절차 문서를 검사 개수 때문에 고칠 일이 없어진다. 기억해야 할 우회가 두 개 줄어든다.

## 방향

- **하려는 것:** 작업 계약(`docs/work/<id>/task/<run>-<role>.json`)을 git 추적 대상에서 빼고, 그래도 종료 검사가 성립한다는 것을 반례 테스트로 고정한다. 구현자 절차 문서에서 검사 개수를 지운다. 그 결론을 RUNBOOK §3.3 과 `Q-14` 에 적는다.
- **하지 않는 것:** 이미 커밋된 계약 67개를 이력에서 빼지 않는다(`git rm --cached` 를 쓰지 않는다 — 이력을 다시 쓰는 것은 되돌리기 어렵다). 종료 검사·계약 생성의 판정 로직을 바꾸지 않는다. 다른 park 결함(`Q-15`~`Q-17`·`Q-19`·`Q-23`·`Q-24`·`Q-26`)과 `w3qu` 의 나머지 4건은 이번 범위가 아니다.
- **전달 메시지:** **작업 계약은 산출물이 아니라 파생물이다.** 승인된 원본(`base_sha` 커밋의 `spec.md`)과 그때의 하네스 리비전이 있으면 바이트까지 같게 다시 만들어진다 — 그래서 이력에 둘 필요가 없고, 두는 순간 같은 경로를 양쪽이 각각 커밋해 통합을 막는다.

## 열린 질문

- 없음 — 강제 수단 후보 셋 중 `.gitignore` 를 실측(2026-09-01 프로브)으로 확정했다. 근거는 `spec.md` 확인란의 「위험과 되돌리기」에 있다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
