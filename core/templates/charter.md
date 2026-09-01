---
id: "{{id}}"
type: charter
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
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다 —
> 다만 「마일스톤 계획」이 비어 있으면 차단 `milestone-plan` 이 승인과 종료를 막는다.

## 왜 이 이니셔티브인가

{{one_line}}

- **지금 없는 것:** NEEDS_INPUT
- **생기면 무엇이 달라지나:** NEEDS_INPUT
- **성공을 무엇으로 아는가:** NEEDS_INPUT

## 범위·비범위

- **이 이니셔티브가 하는 것:** NEEDS_INPUT
- **하지 않는 것:** NEEDS_INPUT
- **다른 이니셔티브에 넘기는 것:** NEEDS_INPUT

## 마일스톤 계획

T2 는 한 번에 끝나지 않는다. **마일스톤마다 무엇이 서면 다음으로 넘어가는지**를 여기 적는다 —
이 절이 비어 있으면 차단 `milestone-plan` 이 승인을 거부한다. 각 마일스톤은 그 자체로 되돌릴 수 있어야 한다.

| # | 마일스톤 | 끝났다고 말할 조건 | 다음으로 넘어가는 관문 | 되돌리기 |
| --- | --- | --- | --- | --- |
| M1 | NEEDS_INPUT | NEEDS_INPUT | NEEDS_INPUT | NEEDS_INPUT |

- **첫 마일스톤을 먼저 하는 이유:** NEEDS_INPUT
- **중간에 멈춰도 되는 지점:** NEEDS_INPUT

## 제약·전제

- **바꿀 수 없는 것(기술·조직·일정):** NEEDS_INPUT
- **지금 참으로 가정하는 것:** NEEDS_INPUT
- **그 가정이 틀리면 무엇이 무너지나:** NEEDS_INPUT

## 위험·중단 조건

- **가장 큰 위험:** NEEDS_INPUT
- **중단 조건(무엇을 보면 멈추는가):** NEEDS_INPUT
- **되돌리기:** NEEDS_INPUT

{{extra_sections}}
## 연결

Tech Spec 은 같은 폴더의 `spec.md`, Compact Brief 는 `brief.md` 다.
수용 기준·검증 계획·증거는 Tech Spec 이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
