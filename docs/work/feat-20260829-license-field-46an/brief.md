---
id: feat-20260829-license-field-46an
type: brief
title: 아카이브 스키마에 라이선스 필드 추가
unit: T1
mode: delivery
intent: write
facets: [docs, tooling]
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
created: '2026-08-29'
updated: '2026-08-29'
---

# 아카이브 스키마에 라이선스 필드 추가

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 docs, tooling · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

_source.md License 줄 · 검증 스크립트 검사 · 인덱스 열 · 기존 18개 backfill

## 배경과 대상

- **왜 지금:** 아카이브 18개는 참고 저장소에서 무엇을 가져올지 판단하는 근거인데, 정작 "가져와도 되는가"를 정하는 라이선스가 스키마에 없다. 지금은 3개만 본문 어딘가에 언급하고 헤더 필드로는 0개라, 부품을 채택할 때마다 GitHub API를 다시 조회해야 한다. 값 자체는 계획 §1.3에서 이미 API와 고정 SHA 실물을 대조해 확인해 두었으므로, 남은 일은 그것을 스키마에 고정하는 것이다.
- **누구를 위한 것:** 다음 채택 게이트(G-M3·G-M6·G-M7)에서 부품을 고르는 사람과, 그 판단 근거를 읽는 다음 세션.
- **성공하면 무엇이 달라지나:** 아카이브 하나만 열어도 재사용 가능 여부를 알 수 있고, 라이선스가 빠진 새 아카이브는 검증 단계에서 걸린다 — 사람이 기억해서 챙기는 항목이 하나 줄어든다.

## 방향

- **하려는 것:** 라이선스를 `_source.md` 헤더의 1급 필드로 만들고, 그것을 검증 스크립트와 인덱스 생성기 양쪽이 알게 한다. 기존 18개는 backfill로 한 번에 맞춘다.
- **하지 않는 것:** 라이선스 값을 새로 조사하지 않는다 — 계획 §1.3 표가 근거이고 그 표를 다시 만들지 않는다(K-61). vendor 채택물의 라이선스 고지(`THIRD_PARTY_NOTICES.md`)는 건드리지 않는다. 그쪽은 `provenance/imports.yaml` 이 원본인 별개 계층이다. 아카이브 본문과 CI 워크플로 파일도 범위 밖이다.
- **전달 메시지:** 아카이브는 "무엇을 하는 저장소인가" 뿐 아니라 "가져다 써도 되는가" 까지 답해야 한다.

## 열린 질문

- 없음 — 라이선스 값의 근거(계획 §1.3)와 표기 규칙(API 값과 실물이 다르면 실물)이 Tech Spec 구현 단위 1번에 고정돼 있다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
