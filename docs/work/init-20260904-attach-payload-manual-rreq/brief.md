---
id: init-20260904-attach-payload-manual-rreq
type: brief
title: 페이로드 1건 손 부착 — 하네스를 자기 저장소 밖에서 처음 돌린다
unit: T2
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: deep
blast_radius: medium
uncertainty: high
status: draft
approved_at: null
approved_by: null
base_sha: null
closed_at: null
parent: null
inputs: ['../feat-20260831-bmad-attach-probe-tgnb/spec.md']
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T2=deep', 'profile:uncertainty.high=kept', 'overlay:unit.t2.parts', 'overlay:profile.standard-or-deeper',
    'warn:PART_PENDING_GATE']
  history: []
created: '2026-09-04'
updated: '2026-09-04'
---

# 페이로드 1건 손 부착 — 하네스를 자기 저장소 밖에서 처음 돌린다

> 깊이 **Deep** · 단위 T2 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

Romeo 하네스를 실제 제품 저장소 1건에 손으로 부착하고 그 저장소의 작업 1건을 관통시켜 M5 attach 의 요구사항을 실측으로 얻는다

## 배경과 대상

- **왜 지금:** 하네스가 자기 저장소 밖에서 한 번도 돈 적이 없다. `attach` 명령(M5)을 만들기 전에 손으로 밟아야 그 명령이 실측 위에 선다.
- **누구를 위한 것:** 이 하네스를 자기 프로젝트에 붙이려는 사람. 첫 사용자는 이 저장소 자신이고, 두 번째가 `My-Automated-Worker/instagram-dm-sender` 다.
- **성공하면 무엇이 달라지나:** 「부착」이 문장이 아니라 **파일 목록과 종료 코드**로 정의된다. 그리고 그 정의를 판정하는 검사가 서서, 아무것도 부착하지 않은 저장소가 부착 검증을 통과하는 지금 상태와 갈린다.

## 방향

- **하려는 것:** 첫 마일스톤은 부착 하나다 — 런북 `scenarios/10-attach-payload.md`, 부착 판정 검사 `tests/test_attach_runbook.py`, 대상 저장소 1건에 실제 부착, 그리고 그 과정이 낸 관측을 열어 두는 것.
- **하지 않는 것:** 부착을 자동화하지 않는다(M5). 프로브가 잡은 `compile`·`doctor` 결함을 고치지 않는다(§12). 대상 저장소의 BMad 를 건드리지 않는다. 두 번째 저장소에 붙이지 않는다.
- **전달 메시지:** 손으로 밟는 것이 방법이다 — 승인 전 프로브 하나가 이미 다섯 가지를 잡았고, 그중 하나(대상의 `.claude/settings.json` `deny` 배열이 통째로 덮여 보호 규칙 두 건이 사라지는 것)는 자동화를 먼저 만들었으면 그 자동화가 조용히 저질렀을 일이다.

## 열린 질문

- 부착이 하네스 소스 트리(`core/`·`adapters/`·`vendor/`·`provenance/`)를 대상 저장소에 복제해야만 성립한다는 것이 실측으로 확인됐다. 계획 §3.1 은 「코어 규칙을 복제하지 않는다 — 복제하면 드리프트다」라고 적는다. **이 단위는 그 복제를 실행하고 결정으로 기록만 한다** — 없애는 것은 M5 의 요구사항이다(charter 중단 조건 ③).
- M3 에서 관통시킬 대상 저장소의 실제 작업이 무엇인지는 그 시점에 정한다(사용자 확정 2026-09-04).


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
