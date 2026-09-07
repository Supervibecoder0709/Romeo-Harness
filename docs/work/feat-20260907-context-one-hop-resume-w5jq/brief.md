---
id: feat-20260907-context-one-hop-resume-w5jq
type: brief
title: 1-hop 재개 — `romeo context <id>` 가 다음 세션이 읽을 파일 목록을 낸다
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
parent: init-20260904-m4-doc-reuse-metrics-wr9m
inputs: [../init-20260904-m4-doc-reuse-metrics-wr9m/charter.md, inputs/probe-2026-09-07.patch]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-07'
updated: '2026-09-07'
---

# 1-hop 재개 — `romeo context <id>` 가 다음 세션이 읽을 파일 목록을 낸다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

`romeo context <id>` 가 단위 하나의 1-hop 파일 목록(정본·상위·입력·회차·계약·증거·결과·검토)을 역할과 사실과 함께 내고, `/plan` 이 재개할 때 그 목록만 읽는다

## 배경과 대상

- **왜 지금:** M4 이니셔티브의 첫 마일스톤(재사용 검색 `romeo find`)이 닫혔고 charter 의 다음 칸이 이것이다 — 관문은 「M1 의 검색이
  그 id 를 먼저 찾아 준다」. `/plan` 절차 1단계는 겹치는 단위가 있으면 「재개」를 제안하라고 요구하지만 **재개하는 세션이 무엇을 읽어야 하는지는
  어디에도 없다** — 요구만 있고 집행이 없는 모양(§11)이고, 31개 단위·회차·검토 봉투가 쌓인 지금 폴더를 눈으로 훑는 방식은 어느 증거가
  검사 기록이고 어느 회차가 어떻게 끝났는지 말해 주지 않는다. D-81 ② 뒤 첫 단위라 종료 검사는 승인 커밋 스냅샷이 낸다 — 새 규칙이 처음으로 남을 판정한다.
- **누구를 위한 것:** 끊긴 작업을 이어받는 다음 세션(사람이든 실행 런타임이든)과, 그 세션에 무엇을 읽으라고 말해야 하는 코디네이터.
  이 관통에서는 검토자 세션이 그 「다음 세션」이다 — 목록만 받고 판정을 낸다.
- **성공하면 무엇이 달라지나:** 단위 id 하나로 한 줄을 치면 재개에 필요한 파일이 역할·사실과 함께 나온다. 상위 charter 와 입력은 1-hop 으로 따라가고,
  그 너머는 목록의 파일이 가리킬 때만 연다(K-31). 깨진 참조는 `[없음]` 으로 보이고, 없는 id 만 오류다.

## 방향

- **하려는 것:** `romeo/context.py` 의 `unit_context` 와 하위 명령 `romeo context <id> [--root] [--json]`. 목록은 단위 폴더 안의 파일 전부와
  frontmatter 의 `parent`(charter, 없으면 spec)·`inputs`(각 경로)까지다. 파일마다 역할 한 낱말과 파일에 적힌 사실(회차 결과·gate_verdict·findings 수·
  등록 여부·base_sha)만 붙인다. `/plan` 절차 1단계에 「재개할 때는 이 목록을 읽는 범위로 삼는다」 한 문단을 더하고, 검사가 그 본문의 이름으로
  실제 실행해 대조한다(M1 AC-5 패턴). 판별 검사 7건.
- **하지 않는 것:** 다음 행동을 추천하지 않는다 — 그것은 사람과 라우터의 몫이다(K-61). 깨진 참조를 막지 않는다(경고까지만 · charter 의 위험).
  부모의 부모·입력 단위의 다른 파일·계획·결정 문서는 넣지 않는다 — 저장소 수준 진입점(progress 블록·git log·CI)은 따로 있다.
  구현자·검토자 브리프 정본이 이 목록을 **생성해 쓰게** 하는 것은 요구하는 자리를 하나 더 만드는 일이라 다음 단위로 미룬다(열린 질문으로 남긴다).
  `romeo find`·카드·close·증거·봉투·세션 시작 표는 건드리지 않는다.
- **전달 메시지:** 「이 단위를 이어받으려면 이것들을 읽으세요 — 그 밖은 여기 적힌 파일이 가리킬 때만.」

## 열린 질문

- 「그 목록에 없는 파일을 읽지 않아도 재개가 된다」는 검사기가 판정할 수 없다 — 이 단위는 검토자 세션 1회로 재고 그 관찰을 검토 봉투 `notes` 에 남긴다.
  목록이 부족해 검토자가 다른 파일을 열어야 했다면 그것이 목록의 결함이고, 다음 단위의 입력이다.
- 작업 계약(`task/`)은 git 에 없다(`.gitignore`) — 새 체크아웃의 목록에는 계약이 없고 워커 트리에만 있다. 목록은 있는 것만 말한다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
