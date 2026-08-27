---
id: "{{id}}"
type: spec
title: "{{title}}"
unit: {{unit}}
mode: {{mode}}
intent: {{intent}}
facets: {{facets}}
gates: {{gates}}
profile: {{profile}}
blast_radius: {{blast_radius}}
uncertainty: {{uncertainty}}
status: draft
approved_at: null
approved_by: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: "{{policy_version}}"
  fired_rules: {{fired_rules}}
  history: []
created: "{{today}}"
updated: "{{today}}"
---

# {{title}}

> 깊이 **{{profile_label}}** · 단위 {{unit}} · 모드 {{mode}} · 의도 {{intent}} · 영역 {{facets_text}} · 게이트 {{gates_text}}
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve {{id}}` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** {{one_line}}
- **왜 지금:** NEEDS_INPUT
- **기대 결과:** NEEDS_INPUT
- **수용 기준:**
  - [ ] AC-1 NEEDS_INPUT
- **위험과 되돌리기:** NEEDS_INPUT (실패 시 복구 명령·절차)
- **결정 필요:** 없음

{{capsule_section}}
## 변경 범위

- 바뀌는 파일·모듈: NEEDS_INPUT
- 영향을 받는 부분: NEEDS_INPUT
- 바꾸지 않는 것(비범위): NEEDS_INPUT

## 구현 단위

| # | 목표 | 변경 | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- |
| 1 | NEEDS_INPUT | NEEDS_INPUT | NEEDS_INPUT | `git revert` 또는 NEEDS_INPUT |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

```yaml
required_checks:
  - id: check-1
    command: "NEEDS_INPUT"
    expect: exit 0
```

{{extra_sections}}
## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
