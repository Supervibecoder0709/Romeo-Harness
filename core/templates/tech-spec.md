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
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve {{id}} --by <승인자>` 로 기록한다.

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

**'바뀌는 파일·모듈' 은 한 줄이어야 하고, 각 항목의 경로는 백틱으로 감싼다.** 이 줄이 작업 계약의 `allowed_paths` 가 된다 —
계약 생성은 이 줄만 읽고 각 항목의 **첫 백틱** 을 경로로 집는다(K-66). 여러 줄로 나누어 적으면 첫 줄 뒤는 읽히지 않고,
백틱 없이 적으면 그 항목은 쓰기 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: NEEDS_INPUT
- 영향을 받는 부분: NEEDS_INPUT
- 바꾸지 않는 것(비범위): NEEDS_INPUT

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 `NEEDS_INPUT` 과 똑같이 취급한다. 승인 전에 채워야 한다. (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | NEEDS_INPUT | NEEDS_INPUT | 소비: 없음 → 생산: NEEDS_INPUT | NEEDS_INPUT | `git revert` 또는 NEEDS_INPUT |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 페이로드(하네스를 부착한 프로젝트) 작업 단위의 `required_checks` 에
**하네스 자신의 테스트**를 넣지 않는다 — `python3 -m unittest discover -s tests`(하네스 저장소의 테스트),
`bin/romeo` 의 자기 검사(`compile --check` · `validate` · `doctor` · `fixtures …`)가 그것이다.
넣으면 하네스가 깨진 동안 그 페이로드 단위가 닫히지 못한다. 그 단위의 산출물은 멀쩡한데 완료가 서지 않는 것이고,
그때 고쳐야 할 것은 그 단위가 아니라 하네스다 — 두 판정을 한 검사에 묶으면 어느 쪽이 깨졌는지 구분되지 않는다
(근거: `feat-20260829-license-field-46an` 의 check-5 가 이 형태였다).
하네스 저장소 **자신**을 대상으로 하는 작업 단위에서는 그 검사들이 정당하다 — 그때는 그것이 이 단위의 산출물이기 때문이다.

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
