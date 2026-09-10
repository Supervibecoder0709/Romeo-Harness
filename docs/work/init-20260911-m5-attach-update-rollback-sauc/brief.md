---
id: init-20260911-m5-attach-update-rollback-sauc
type: brief
title: M5 attach — 하네스를 남의 저장소에 붙이고 갱신·복원한다
unit: T2
mode: delivery
intent: mixed
facets: [tooling, docs, security]
gates: [privacy-security]
profile: deep
blast_radius: large
uncertainty: medium
status: draft
approved_at: null
approved_by: null
base_sha: null
closed_at: null
parent: null
inputs: [inputs/ac-rebuttal-20260911.md, inputs/ac-rebuttal-20260911-round2.md, inputs/ac-rebuttal-20260911-ac9.md]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T2=deep', 'profile:gate.any=kept', 'profile:blast.large=kept', 'profile:uncertainty.medium=kept',
    'overlay:gate.any', 'overlay:unit.t2.parts', 'overlay:profile.standard-or-deeper', 'guard:permission-escalation',
    'guard:production-deploy', 'guard:deletion', 'warn:PART_PENDING_GATE']
  history: []
created: '2026-09-11'
updated: '2026-09-11'
---

# M5 attach — 하네스를 남의 저장소에 붙이고 갱신·복원한다

> 깊이 **Deep** · 단위 T2 · 모드 delivery · 의도 mixed · 영역 tooling, docs, security · 게이트 privacy-security
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

M5 — 하네스가 자기 저장소 밖에서 산다. 한 명령으로 붙고, 붙은 뒤 실제로 돌고, 갱신을 보고, 되돌릴 수 있다.

## 배경과 대상

- **왜 지금:** v1 이 닫혔다(D-82). v1 이 세운 것은 「하네스가 자기를 판정한다」까지이고, 남의 저장소에서 도는지는
  **손으로 세 번 밟아 보기만 했다**(`init-20260904-attach-payload-manual-rreq` M1 부착 · M2 라우터 · M3 close).
  그 세 관통이 낸 결함 중 부착 고유의 것 9건을 `docs/requirements/attach-requirements.md` 가 요구사항으로 정리했고,
  #13c 정비가 그중 2건(Q-66·Q-67)을 이미 닫았다. **남은 7건이 이 이니셔티브의 입력이다.**
- **누구를 위한 것:** 하네스를 자기 프로젝트에 붙이려는 사람. 지금 그 사람이 해야 하는 일은
  `scenarios/10-attach-payload.md` 를 읽고 여섯 디렉터리를 손으로 복사한 뒤 `compile --root` 를 부르는 것이고,
  붙었는지 확인하는 `doctor` 는 **거꾸로 답한다** — 안 붙인 저장소에 초록, 붙인 저장소에 빨강.
- **성공하면 무엇이 달라지나:** 부착이 명령 하나가 되고, 그 명령이 놓은 것과 대상이 원래 갖고 있던 것이 구분된다.
  하네스가 갱신되면 드리프트가 인쇄되고, 마음에 들지 않으면 되돌린다.

## 방향

- **하려는 것:** 첫 마일스톤은 **자리를 잇는 일**이다 — 「무엇이 있어야 부착인가」의 정본은 이미 있고
  (`scenarios/10-attach-payload.md` 의 「놓는 것」), 그것을 읽는 검사도 이미 있다(`tests/test_attach_runbook.py`).
  없는 것은 `doctor` 가 그 정본을 읽는 것뿐이다. 나머지 마일스톤(`attach` · `update --dry-run` ·
  `rollback` · 실제 프로젝트 관통)은 Charter 의 계획표에 있다.
- **하지 않는 것:** 첫 마일스톤에서 **부착을 자동화하지 않고, 「놓는 것」 목록의 내용도 바꾸지 않는다.**
  새 매니페스트 파일을 만들면 정본이 둘이 된다 — 같은 사실을 두 자리에 적지 않는다(§11).
  M1 이 고치는 것은 「붙었는지 보는 눈」이 정본을 안 보고 있다는 것뿐이다.
- **전달 메시지:** 「요구는 이미 적혀 있다. `doctor` 가 그것을 읽게 하면 주의문 없이도 정직하게 답한다.」

## 열린 질문

- **복제냐 참조냐(Q-54)는 M1 에서 정하지 않는다** — Charter M2 의 몫이다. M1 은 지금의 부착 방식(여섯 디렉터리 복제)을
  **사실로 받아** 매니페스트의 형식과 검사가 서는 자리를 세운다. M2 의 결정이 바꾸는 것은 매니페스트의 **내용**이다.
- 대상 저장소 `My-Automated-Worker/instagram-dm-sender` 가 여전히 접근 가능하고 부착 전 커밋이 깨끗한지는 **미확인**이다 —
  Charter M4(실제 프로젝트 관통) 진입 전에 확인한다. M1~M3 는 샌드박스로 충분하다.

## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
