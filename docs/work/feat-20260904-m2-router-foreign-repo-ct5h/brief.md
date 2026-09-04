---
id: feat-20260904-m2-router-foreign-repo-ct5h
type: brief
title: 라우터가 남의 저장소에서 돈다 — 대상 저장소의 실제 요청 1건을 승인까지
unit: T1
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
parent: init-20260904-attach-payload-manual-rreq
inputs: [../init-20260904-attach-payload-manual-rreq/charter.md, observations.md]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.high->deep', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-04'
updated: '2026-09-04'
---

# 라우터가 남의 저장소에서 돈다 — 대상 저장소의 실제 요청 1건을 승인까지

> 깊이 **Deep** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

부착된 남의 저장소에서 Romeo 라우터를 실제로 돌려, 그 저장소의 실제 요청 1건을 사람 승인까지 세운다. 하네스가 처음으로 `tooling`·`docs` 가 아닌 영역의 일을 분류한다.

## 배경과 대상

- **왜 지금:** M1 이 부착을 파일 목록과 종료 코드로 고정했지만, 그 부착 위에서 **라우터가 실제로 돈 적은 없다**. 부착이 성립했다는 것과 라우터가 그 저장소에서 일한다는 것은 다른 주장이다 — 지금 참인 것은 앞의 것뿐이다.
- **누구를 위한 것:** M5 `attach` 를 만들 사람. 그 명령이 자동화할 절차의 두 번째 조각(부착 다음에 오는 것)이 여기서 손으로 밟힌다.
- **성공하면 무엇이 달라지나:** 「하네스가 하네스만 시험한다」가 반쯤 풀린다. 대상 저장소에 `security` 영역의 작업 단위가 서고, 한 `CLAUDE.md` 안의 BMad·Romeo 두 라우팅 규칙이 실제로 만나는 자리가 상상이 아니라 인용으로 적힌다.

## 방향

- **하려는 것:** 대상 저장소에서 라우터를 돌리는 절차를 런북으로 고정하고, 그 절차대로 **그 시점에 사용자가 확정한 요청 1건**을 분류·승인까지 세운다. 승인 시점의 후보는 GitHub issue 14번이었으나 실행이 그것을 이미 구현된 상태로 실측해 대상을 바꿨다(spec 「결정 필요」). 그 결과를 종료 코드로 판정하는 검사를 만든다.
- **하지 않는 것:** 관통 대상으로 고른 요청 자체를 **구현하지 않는다** — M2 는 승인까지이고 구현·close 는 M3 다. `attach` 명령을 만들지 않는다(M5). 라우터가 남의 저장소에서 돌 때 걸린 것을 그 김에 고치지 않는다(§12) — 열어만 둔다. 대상 저장소의 BMad 를 제거하거나 Romeo 에 종속시키지 않는다.
- **전달 메시지:** 부착은 파일을 놓는 일이었고, 이것은 그 파일들이 실제로 일하는지 보는 일이다. 둘 중 뒤의 것만이 「하네스가 남의 저장소에서 돈다」를 참으로 만든다.

## 열린 질문

- 대상 저장소에는 `bin/`·`romeo/` 가 없다(런북 10 이 「놓지 않는다」로 확정 · Q-54). 그 저장소에서 라우터를 돌리는 별도 실행이 명령을 어디서 부르는가 — 이 관통이 그 답을 실측으로 만든다.
- 두 라우팅 규칙이 같은 상황을 서로 다르게 지시하는 구절이 실제로 있는가. 없다는 관측도 결과다(K-51).


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
