---
id: feat-20260830-harness-tuneup-6xcq
type: brief
title: M3 진입 전 하네스 정비 — run-unit 자동화·코어 규칙 승격·문서 다이어트
unit: T1
mode: delivery
intent: write
facets: [tooling, docs, security]
gates: [privacy-security]
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
  fired_rules: ['profile:base:T1=standard', 'profile:gate.any=kept', 'profile:uncertainty.medium=kept',
    'overlay:gate.any', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-08-30'
updated: '2026-08-30'
---
# M3 진입 전 하네스 정비 — run-unit 자동화·코어 규칙 승격·문서 다이어트

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs, security · 게이트 privacy-security
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

M2 관통에서 드러난 운영 부담 8가지를 한 묶음으로 정리해 M3 진입 조건을 만든다

## 배경과 대상

- **왜 지금:** M2 가 D-76 으로 닫혔고(2026-08-29) M3 는 아직 시작하지 않았다 — 관통을 여섯 번 돈 직후라
  무엇이 불편했는지가 가장 선명한 시점이다. 그리고 이 묶음에 들어가는 규칙 하나("관통 중 하네스를 고치지 않는다")가
  스스로를 구속한다: 그 규칙이 코어에 들어간 뒤에는 다음 관통이 도는 동안 하네스를 손댈 수 없다.
  정비를 관통과 관통 **사이**에 몰아서 해야 하는 이유가 그것이다.
- **누구를 위한 것:** 이 하네스를 실행하는 사람과, 다음 세션에 이 저장소를 여는 에이전트.
  M3 는 시나리오가 3개라(discovery 차단·삭제 게이트·능력 부재) 관통 1회의 수동 비용이 그대로 곱해진다.
- **성공하면 무엇이 달라지나:** ① 관통 1회의 수동 단계가 `romeo run-unit` 한 명령으로 줄어든다
  ② 규범(하네스 동결·위협 모델·FAIL 사유)이 진행 기록이 아니라 규칙 파일에 있어 다음 세션이 진행 문서를 뒤지지 않고 따른다
  ③ 세션 시작 때 첫 번째로 읽는 문서가 113KB → 20KB 이하로 줄어든다
  ④ 관통이 끝없이 반복되지 않는다 — M2 에서 6회를 돌고 사용자 결정(D-76)으로 겨우 멈춘 패턴이 M3 의 시나리오 3개에서 되풀이되지 않는다.

## 방향

- **하려는 것:** 8항목을 한 작업 단위·한 커밋 묶음으로 처리한다 — (1) `romeo run-unit` 신설
  (2) 페이로드 검증 계획에서 하네스 자신의 테스트를 분리하는 템플릿 규칙 (3) "관통 중 하네스 동결" 을 `AGENTS.core.md` 로
  (4) 위협 모델을 `constraints.md` 의 K-56~ 로 승격 (5) `review/SKILL.md` 에 FAIL 사유 열거(Q-10 (a))
  (6) `progress.md` 다이어트 — 덜어낸 서술은 `docs/planning/archive/` 로 옮기고 링크한다 (7) §10 체크리스트 8~48 을 완료 표로 접기 (8) 관통 반복 중단 기준 — 연속 2회 실패면 3회차를 멈추고 완료 정의를 재검토하게 한다.
- **하지 않는 것:** G-M3 채택 게이트(D-52 — 별도 사용자 확정) · impl6 교체 실행(D-76 ① — 게이트 조건 아님) ·
  M3 의 기능 자체(Charter 템플릿·`capabilities.yaml`·`gate-create`) · `run-unit --spawn` 의 실제 기동 실측(다음 관통에서 관찰한다) ·
  덜어낸 문서의 내용 수정(옮기기만 하고 문장을 고치지 않는다).
- **전달 메시지:** 이 정비는 새 능력을 만드는 것이 아니라, M2 가 실측으로 드러낸 **운영 부담과 규범의 잘못된 위치**를 고치는 것이다.
  완료 판정은 기능 시연이 아니라 관찰 가능한 수치와 검사 통과다.

## 열린 질문

- 없음 — `/plan` 단계의 결정 필요 2건은 2026-08-30 사용자 확정으로 닫혔다(범위: 한 단위 / 덜어낸 문서: 아카이브 파일로 이동 / 중단 기준 상한: 2회 실패 후 3회차 차단).

## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
