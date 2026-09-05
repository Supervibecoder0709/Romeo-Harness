---
id: feat-20260906-m3-close-foreign-repo-ik3u
type: brief
title: 관통을 끝낸다 — 남의 저장소의 단위를 구현·검토·close 한다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs, security]
gates: [privacy-security]
profile: deep
blast_radius: medium
uncertainty: high
status: draft
approved_at: null
approved_by: null
base_sha: null
closed_at: null
parent: init-20260904-attach-payload-manual-rreq
inputs: [../init-20260904-attach-payload-manual-rreq/charter.md, ../feat-20260904-m2-router-foreign-repo-ct5h/spec.md]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:gate.any=kept', 'profile:uncertainty.high->deep',
    'overlay:gate.any', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-06'
updated: '2026-09-06'
---

# 관통을 끝낸다 — 남의 저장소의 단위를 구현·검토·close 한다

> 깊이 **Deep** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs, security · 게이트 privacy-security
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

부착한 남의 저장소에서 **구현·검토·close 까지** 한 바퀴를 돌려, 하네스가 처음으로 자기 도구·문서가
아닌 영역의 일을 **판정**하게 한다. charter `init-20260904-attach-payload-manual-rreq` 의 M3 다.

## 배경과 대상

- **왜 지금:** M1 이 부착을, M2 가 분류를 참으로 만들었지만 **판정은 아직 아무것도 참이 아니다**. 하네스는 지금까지 자기 자신만 시험했고(작업 단위 25건 중 남의 저장소를 판정한 것 0건), 그것이 이 이니셔티브를 연 이유다. M2 까지에서 멈추면 charter 가 「M3 없이는 해소되지 않는다」고 적어 둔 것이 그대로 남는다.
- **누구를 위한 것:** ① 대상 저장소(`instagram-dm-sender`)에서 일하는 에이전트 — 지금 그 저장소의 `CLAUDE.md` 는 다섯 지점에서 서로 다른 것을 지시하고, 어느 쪽을 따라도 다른 쪽을 어긴다. ② M5 `attach` 를 만들 다음 이니셔티브 — 이 관통이 막힌 자리가 그 명령의 요구사항이 된다.
- **성공하면 무엇이 달라지나:** 「하네스가 하네스만 시험한다」가 끝난다. 그리고 남의 저장소에서 close 를 돌리는 절차가 런북 하나에 적혀, 두 번째 저장소에 붙일 때 처음부터 다시 알아내지 않는다.

## 방향

- **하려는 것:** 대상 저장소의 승인된 단위 `feat-20260904-claude-md-rule-conflicts-bbn8` 을 구현하고(마커 밖에 「규칙 충돌 해소」 절), 반대 런타임 검토를 받고, `status: done` 으로 닫는다. 그 절차를 `scenarios/12-close-foreign-repo.md` 에 고정하고 완료를 **대상 저장소의 상태로** 판정하는 검사를 세운다.
- **하지 않는 것:** close 가 남의 루트에서 무엇을 더 요구하든 **`romeo/` 를 고치지 않는다** — 열어 두고 M5 에 넘긴다(§12). 두 번째 저장소에 붙이지 않는다. 대상 저장소의 BMad 를 제거하거나 Romeo 에 종속시키지 않는다. 대상 저장소에 **push 하지 않는다**. 부착분을 커밋하지 않는다.
- **전달 메시지:** 「부착했다」·「분류했다」·「판정했다」는 서로 다른 세 주장이고, 지금 참인 것은 앞의 둘뿐이다. 이 단위가 세 번째를 참으로 만든다 — 그리고 그 과정에서 막힌 자리가 이 관통의 진짜 산출물이다.

## 열린 질문

- close 가 남의 루트에서 **추가로 무엇을 요구하는지** 끝까지 모른다. 승인 시점 실측은 `HAS_EVIDENCE` 하나이고 그 뒤(`CHECK_PLAN_COMMITTED`·`TASK_ANCHORED`·`ROLE_CONTRACT`·`GUARD_APPROVED`)는 돌려 봐야 안다 — 그래서 AC-5 는 목록의 **개수**를 요구하지 않는다.
- 대상 저장소를 작업 공간으로 삼는 실행을 **어떻게 띄우는지**가 M2 에서 세 시도 중 둘이 막혔다(Orca 미등록·외부 워크트리). 이번에도 같은 경로(대상 디렉터리에서 비대화형 실행 + `--allowedTools`)를 쓴다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
