---
id: "{{id}}"
type: brief
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
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

{{one_line}}

## 배경과 대상

- **왜 지금:** NEEDS_INPUT
- **누구를 위한 것:** NEEDS_INPUT
- **성공하면 무엇이 달라지나:** NEEDS_INPUT

## 방향

- **하려는 것:** NEEDS_INPUT
- **하지 않는 것:** NEEDS_INPUT
- **전달 메시지:** NEEDS_INPUT

## 열린 질문

- 없음

{{extra_sections}}
## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
