---
id: feat-20260830-reviewer-fail-reasons-938r
type: brief
title: 검토자 FAIL 사유를 닫힌 목록으로 만들고 결과 봉투로 강제한다 — 하네스가 허용하는 상태를 검토자가 FAIL 로 보는 충돌 해소
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
created: '2026-08-30'
updated: '2026-08-30'
---

# 검토자 FAIL 사유를 닫힌 목록으로 만들고 결과 봉투로 강제한다 — 하네스가 허용하는 상태를 검토자가 FAIL 로 보는 충돌 해소

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

검토자가 게이트를 내릴 수 있는 사유를 닫힌 목록으로 만들고, 결과 봉투 스키마가 그 코드를 요구하게 한다 —
지금은 목록 밖 사유로도 FAIL 이 나고, 그중 하나가 절차를 따르면 반드시 생기는 상태여서 어떤 작업 단위도 닫히지 않는다.

## 배경과 대상

- **왜 지금:** 같은 작업 단위에서 관통이 4회 연속 실패했고, 마지막 실패는 산출물이 아니라 **하네스의 절차적 모순**이었다.
  구현자는 절차대로 확인란 체크박스를 채워야 하는데(implement 절차 7), 채우는 순간 작업 트리 spec.md 의 지문이
  작업 계약의 것과 달라지고, 검토자가 그 차이를 FAIL 로 봤다. 표본 2건이 같은 사유로 FAIL 해 흔들림이 아님이 확인됐고,
  같은 시점 `close --dry-run` 은 나머지를 전부 PASS 로 냈다. 이것이 닫히지 않으면 다음 관통도 같은 자리에서 멈춘다.
- **누구를 위한 것:** 이 하네스로 작업을 위임하고 완료를 판정하는 사람과, 그 판정을 내는 검토자 런타임.
  검토자는 지금 "무엇이 FAIL 인가" 를 목록으로 받지만 그 목록이 자기를 구속하지 않는다는 것도 함께 받는다.
- **성공하면 무엇이 달라지나:** 판정의 근거가 자유 서술에서 **열거된 코드**로 바뀐다. 검토자가 목록 밖 사유로 게이트를
  내리면 결과 봉투가 스키마에서 걸리므로, 판정의 흔들림이 사람의 성실성이 아니라 계약으로 막힌다.
  열린 단위 `feat-20260830-harness-defects-w3qu` 를 새 base 로 재개할 수 있게 된다.

## 방향

- **하려는 것:** ① FAIL 사유 8개에 코드를 붙이고 "목록에 없는 사유로 FAIL 을 내지 않는다" 를 명시한다.
  ② 결과 봉투 스키마에 `fail_reasons` 를 더해 `FAIL` 일 때 요구한다. ③ 확인란 체크로 인한 지문 차이가
  정상임을 문서에 적는다. ④ 검토자 프롬프트와 기존 판정 표본을 새 계약에 맞춘다.
- **하지 않는 것:** FAIL 사유 목록 자체를 늘리거나 줄이지 않는다 — 이번은 목록을 **닫는** 작업이다.
  `romeo/close.py` 의 판정 로직도 건드리지 않는다(이미 올바르게 동작한다).
  증거의 `spec_ref` 를 승인 커밋 기준으로 바꾸는 방향은 택하지 않는다 — 그러면
  `SPEC_UNCHANGED_SINCE_EVIDENCE` 가 자기 자신을 비교하게 되어 검사 하나가 죽는다.
  결함 ②(`expect` 가 판정에 쓰이지 않는다)와 ③(반복 중단 카운터)은 별도 단위다.
- **전달 메시지:** 판정 기준을 문서로만 적으면 다음 검토자가 또 다른 목록 밖 사유를 낸다 — 4회 관통이 그 증거다.
  기준은 기계가 확인하는 계약으로 내보낸다. 이 저장소가 권한 상한을 지침 문구가 아니라 설정으로 강제하는 것과 같은 이유다.

## 열린 질문

- `fail_reasons` 를 스키마에서 FAIL 일 때 필수로 조일지, 선택 필드로 두고 종료 검사가 잡을지 — 구현 시 확인한다.
  전자면 `fixtures/parity` 표본 갱신이 함께 필요하다.
- 검토자가 코드를 적더라도 그 코드와 findings 본문이 어긋나는 경우는 기계가 잡지 못한다. 이번 범위 밖으로 둔다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
