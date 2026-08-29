---
id: feat-20260829-m2-root-cause-review-20260829-44hm
type: brief
title: M2 마일스톤 지연 근본 원인 리뷰
unit: T1
mode: discovery
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
inputs:
  - docs/planning/progress.md
  - docs/planning/implementation-plan.md
  - docs/decisions/decision-register.md
  - adapters/orca/RUNBOOK.md
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:mode.discovery->deep', 'profile:uncertainty.high=kept',
    'overlay:mode.discovery', 'overlay:profile.standard-or-deeper', 'warn:PART_PENDING_GATE']
  history: []
created: '2026-08-29'
updated: '2026-08-29'
---

# M2 마일스톤 지연 근본 원인 리뷰

> 깊이 **Deep** · 단위 T1 · 모드 discovery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

M2가 왜 아직 닫히지 않았는지, 처음 설계가 어떤 사용자 가치를 검증하려 했고 실행 과정에서 무엇이 그 검증을 늘렸는지를 증거로 추적해, 다음 작업을 줄일 수 있는 리뷰 보고서로 남긴다.

## 배경과 대상

- **왜 지금:** 현재 상태 문서는 교체 실행·복수 검토 표본·실제 `close`가 남았다고 기록한다. 현재 CI 성공은 이 세 항목의 실행 증거가 아니므로, 같은 관통을 반복하기 전에 지연 원인을 분리해야 한다.
- **누구를 위한 것:** M2를 계속 관통할지, 종료 기준 또는 실행 순서를 바꿀지 결정하는 비개발자 프로젝트 책임자와 다음 작업자.
- **성공하면 무엇이 달라지나:** "무엇이 아직 안 됐는지"와 "왜 같은 종류의 작업이 반복됐는지"가 분리된다. 다음 작업은 원인별 최소 검증 1개와 중단 조건을 갖게 된다.

## 방향

- **하려는 것:** 기본 기획서의 M2 약속, 구현 계획의 종료 조건, 상태 문서의 실제 진행, RUNBOOK의 실행 순서, 기존 evidence/result/review를 같은 SHA 기준으로 대조한다. 보고서는 각 원인을 유저스토리·사실·추론·미확인·권고·확인 방법으로 설명한다.
- **하지 않는 것:** 코어 코드·정책·테스트·기존 기획 문서·M2 상태를 수정하거나, push·배포·worktree 삭제를 하지 않는다. 발견된 결함은 고치지 않고 별도 후속 단위 후보로만 적는다.
- **전달 메시지:** M2는 "CI가 초록"이라서 끝나는 일이 아니라, 같은 산출물에서 역할 교체·복수 표본·실제 종료 검사가 각각 무엇을 증명하는지 확인해야 끝난다. 다만 각 검사가 그 의사결정에 실제로 필요한지도 다시 검토한다.

## 열린 질문

- 교체 실행과 표본 보강, 실제 `close`가 여전히 미완료인지 현재 작업트리와 기록에서 다시 확인해야 한다.
- 기존의 설계 보완(동일 산출물 전제·복수 표본·앵커 강화)이 실제 결함을 차단했는지, 혹은 종료 비용만 늘렸는지 구분해야 한다.
- 보고서의 권고가 기획 변경을 요구하면, 그 변경은 이 리뷰에서 반영하지 않고 새 승인 단위로 분리해야 한다.

## 조사·가설·검증 계획

구현 dispatch 는 조사 결과가 기록되기 전에는 차단된다(discovery-result).

- **핵심 가설:** 지연의 주원인은 한 가지 테스트 실패가 아니라, (1) 완료 증거를 만드는 실행이 남아 있는 상태, (2) 관측 중 새 결함을 발견하면 종료 기준과 관측 설계가 함께 바뀌는 구조, (3) 상태 문서·CI·worktree가 서로 다른 SHA를 가리킬 수 있는 추적 부담의 결합이다. 이는 조사 전 가설이며 사실로 단정하지 않는다.
- **조사 방법·기간:** Codex `gpt-5.6-sol`/`max`가 별도 worktree에서 읽기·검색 위주로 계획 문서, 결정 기록, RUNBOOK, M2 work unit의 evidence/result/review를 대조한다. 명령 결과는 보고서의 관찰값으로만 쓰고, 검토자는 반대 런타임의 읽기 전용 검토로 근거 링크를 확인한다.
- **첫 마일스톤(spike):** "계획된 M2 종료 조건 → 실제 실행/증거 → 남은 조건"을 한 장의 추적표로 만들고, 각 빈칸이 문서 지연인지 실행 미완료인지 구분한다.
- **진행/중단 판단 기준:** 모든 최우선 원인이 현재 파일·SHA·명령 기록으로 추적되면 보고서를 완성한다. 핵심 증거가 없거나 서로 다른 SHA라서 비교할 수 없으면 원인을 확정하지 않고 `미확인`으로 남긴다. 코드 수정 필요성이 확인되면 그 자리에서 중단하고 새 단위를 제안한다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
