---
id: feat-20260829-m2-root-cause-review-20260829-44hm
type: spec
title: M2 마일스톤 지연 근본 원인 리뷰
unit: T1
mode: discovery
intent: write
facets: [tooling, docs]
gates: []
profile: deep
blast_radius: medium
uncertainty: high
status: active
approved_at: '2026-08-29T18:38:07+09:00'
approved_by: julliettelee
base_sha: null
closed_at: null
parent: null
inputs: [docs/planning/progress.md, docs/planning/implementation-plan.md, docs/decisions/decision-register.md,
  docs/planning/open-questions.md, adapters/orca/RUNBOOK.md, docs/work/feat-20260829-license-field-46an/spec.md]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:mode.discovery->deep', 'profile:uncertainty.high=kept',
    'overlay:mode.discovery', 'overlay:profile.standard-or-deeper', 'warn:PART_PENDING_GATE']
  history: []
created: '2026-08-29'
updated: '2026-08-29'
approval_history:
- {approved_at: '2026-08-29T18:23:27+09:00', approved_by: julliettelee, superseded_at: '2026-08-29T18:38:07+09:00',
  reason: 승인된 산출물 경로를 계약 파서가 읽는 백틱 경로 두 개로 정정해 docs/reviews 보고서 쓰기 범위를 명시함}
---

# M2 마일스톤 지연 근본 원인 리뷰

> 깊이 **Deep** · 단위 T1 · 모드 discovery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260829-m2-root-cause-review-20260829-44hm --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** M2의 기본 기획·구현 계획·결정·RUNBOOK·실행 evidence를 현재 SHA 기준으로 대조하고, 비개발자가 읽을 수 있는 유저스토리 중심의 근본 원인 리뷰를 `docs/reviews/2026-08-29-m2-root-cause-review/REVIEW_FINDINGS.md`에 저장한다.
- **왜 지금:** 상태 문서가 교체 실행, 복수 검토 표본, 실제 `close`를 남은 일로 적고 있다. CI의 과거 성공은 이 종료 항목의 현재 실행 증거가 아니므로, 추가 관통 전에 원인과 필요성을 검증해야 한다.
- **기대 결과:** 사용자는 각 남은 단계가 해결하는 위험, 그 단계가 M2를 오래 끈 원인인지 여부, 바로 다음에 할 가장 작은 검증을 한 문서에서 판단할 수 있다.
- **수용 기준:**
  - [x] AC-1 보고서가 지정 경로에 있으며, "사용자 스토리 → 현재 관찰 → 근본 원인 → 권고 → 다음 확인" 구조로 M2의 핵심 병목을 설명한다.
  - [x] AC-2 각 최우선 원인은 현재 파일·SHA·명령 기록 또는 기존 evidence/result/review의 정확한 위치로 추적되고, 사실·추론·미확인을 혼합하지 않는다.
  - [x] AC-3 보고서가 M2의 원래 종료 조건과 실제 남은 실행을 대조해, 불필요·중복·순서가 잘못된 단계 후보를 근거와 함께 제시한다.
  - [x] AC-4 보고서가 코드·정책을 수정하지 않고, 권고마다 후속 승인 필요 여부와 검증 가능한 중단/완료 기준을 적는다.
  - [ ] AC-5 반대 런타임의 읽기 전용 검토가 보고서의 핵심 근거 링크와 결론 과장을 확인하고, 결과 봉투가 작업 단위의 `review/`에 기록된다.
- **위험과 되돌리기:** 보고서가 오래된 SHA를 사실처럼 쓸 위험이 있다. 각 관찰에 SHA/시각/근거를 적고, 확인할 수 없는 것은 `미확인`으로 남긴다. 기존 코드·정책·문서는 덮어쓰지 않는다. 보고서의 오류는 근거를 재확인한 뒤 해당 새 파일만 수정하며, 새 파일 삭제는 사용자 승인 없이 하지 않는다.
- **결정 필요:** 없음


## 변경 범위

- 바뀌는 파일·모듈: `docs/work/feat-20260829-m2-root-cause-review-20260829-44hm/` · `docs/reviews/2026-08-29-m2-root-cause-review/`
- 영향을 받는 부분: M2 종료·재관통·후속 M3 착수의 의사결정. 제품 코드나 외부 운영 상태에는 영향이 없다.
- 바꾸지 않는 것(비범위): `core/`, `romeo/`, `adapters/`, `fixtures/`, `tests/`, 기존 `docs/planning/`·`docs/decisions/`·`docs/work/feat-20260829-license-field-46an/` 파일, git history, 원격 저장소와 기존 worktree.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 미확인 빈칸과 똑같이 취급한다. 승인 전에 채워야 한다. (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | M2 완료 주장과 실제 증거의 기준선을 고정한다 | 현재 review worktree의 HEAD·상태와 progress/plan/RUNBOOK/M2 unit의 관련 SHA·명령 기록을 추적표로 정리한다 | 소비: 현재 M2 문서·기존 evidence → 생산: 출처별 관찰표 | 모든 최우선 주장에 파일/줄 또는 SHA/명령을 연결하고, 서로 다른 SHA는 비교 불가로 표시한다 | 새 보고서 초안을 수정한다. 기존 파일은 되돌리거나 삭제하지 않는다 |
| 2 | 지연 원인을 사용자 관점으로 설명한다 | 원래 M2 사용자 가치·종료 조건과 실제 재관통 순서를 대조해, 병목·불필요 단계·설계 결함 후보를 우선순위화한다 | 소비: 관찰표 → 생산: 유저스토리별 원인·영향·권고 | 원인마다 사실/추론/미확인, 왜 지금, 최소 다음 검증, 중단 조건이 있다 | 근거 없는 원인을 미확인으로 내리고 보고서를 수정한다 |
| 3 | 독립 검토 가능한 보고서를 저장한다 | 지정 `docs/reviews/` 파일을 작성하고 반대 런타임에 핵심 근거·결론 과장 여부를 읽기 전용으로 검토하게 한다 | 소비: 원인 초안 → 생산: REVIEW_FINDINGS.md + review 결과 봉투 | 아래 required_checks와 읽기 전용 review 결과가 AC-1~AC-5를 뒷받침한다 | 새 보고서 또는 review 봉투의 오류를 해당 파일에서 정정하고 다시 검토한다 |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

```yaml
required_checks:
  - id: check-1
    command: "test -f docs/reviews/2026-08-29-m2-root-cause-review/REVIEW_FINDINGS.md && rg -n '^## (사용자 스토리|현재 관찰|근본 원인|권고|다음 확인)' docs/reviews/2026-08-29-m2-root-cause-review/REVIEW_FINDINGS.md"
    expect: exit 0
  - id: check-2
    command: "rg -n '사실|추론|미확인|SHA|근거' docs/reviews/2026-08-29-m2-root-cause-review/REVIEW_FINDINGS.md"
    expect: exit 0
  - id: check-3
    command: "git diff --check && bin/romeo validate"
    expect: exit 0
  - id: check-4
    command: "git diff --name-only HEAD -- core romeo adapters fixtures tests docs/planning docs/decisions docs/work/feat-20260829-license-field-46an | test ! -s /dev/stdin"
    expect: exit 0
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
