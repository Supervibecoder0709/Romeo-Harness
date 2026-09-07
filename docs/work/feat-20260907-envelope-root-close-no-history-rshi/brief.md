---
id: feat-20260907-envelope-root-close-no-history-rshi
type: brief
title: 위치 인자가 루트를 따르고, 이력 없는 루트에서도 종료 검사가 판정을 낸다
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
created: '2026-09-07'
updated: '2026-09-07'
---

# 위치 인자가 루트를 따르고, 이력 없는 루트에서도 종료 검사가 판정을 낸다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

envelope check 의 상대 경로를 루트 기준으로 풀고, 이력 없는 루트에서 close 가 예외 대신 판정을 인쇄한다

## 배경과 대상

- **왜 지금:** D-81 이 정한 순서의 ①이다 — 이 정비 뒤에 ②(판정 리비전 분리)가 오고, ②는 `--root` 로 옛 리비전 하네스가 현재
  트리를 판정하게 하는 것이라 `--root` 를 따르지 않는 자리(Q-66)와 이력 없는 루트에서 죽는 자리(Q-67)가 먼저 닫혀야 한다.
  둘 다 M5 attach 요구사항 9건 중 2건이기도 하다. 관통 도중에는 하네스를 고칠 수 없으므로(§10 동결) 관통 사이인 지금 닫는다.
- **누구를 위한 것:** 남의 루트를 `--root` 로 다루는 사람 — 관통을 위임하고 결과를 회수하는 코디네이터(RUNBOOK §3.8),
  하네스를 부착한 프로젝트에서 `close` 를 부르는 사람(M5), 그리고 ②에서 옛 리비전 하네스를 돌릴 절차.
- **성공하면 무엇이 달라지나:** `--root` 를 준 실행에서 위치 인자가 그 루트 기준으로 해석되고, 못 찾으면 어느 경로에서
  찾았는지가 인쇄된다. 이력 없는 루트에서 `close` 는 죽지 않고 검사 목록과 종료 코드를 낸다 — `FRESH_HEAD` 미검증 한 건으로,
  완료가 선언되는 일은 없다. 이력 있는 루트의 판정은 바뀌지 않는다.

## 방향

- **하려는 것:** `romeo/envelope.py` 의 `check_result_envelope` 가 상대 경로를 `project_root` 기준으로 풀게 하고,
  `romeo/close.py` 가 `head_sha` 실패를 `FRESH_HEAD` 미검증 한 건으로 바꿔 거기서 판정을 끝내게 한다. 각 규칙이 사는
  문서(RUNBOOK §3.0 · plan-close 절차 · `--help`)를 같은 변경에서 함께 고친다(§11).
- **하지 않는 것:** `review record <source>` 의 경로 해석은 손대지 않는다 — 그 파일은 설계상 루트 밖에 둔다(RUNBOOK §3.7).
  이력 없는 루트에서 뒤 검사를 억지로 이어 돌리지 않는다 — 검사 기록 선택·재실행·검토 판정은 전부 head·tree 에 앵커되므로
  이력 없이는 성립하지 않는다. `is_repo` 로 미리 가르지 않는다 — 커밋 없는 저장소가 그 틈으로 빠진다. Q-64·Q-69·Q-70 도
  이 단위에서 고치지 않는다(§12).
- **전달 메시지:** `--root` 가 정하는 것과 위치 인자가 해석되는 기준은 같아야 한다. 그리고 판정 명령은 어떤 루트에서든
  판정으로 끝난다 — 검사가 성립하지 않으면 그것을 미검증으로 **인쇄**하는 것이 이 하네스의 규칙이지(K-51), 예외로 죽는 것이 아니다.

## 열린 질문

- 없음


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
