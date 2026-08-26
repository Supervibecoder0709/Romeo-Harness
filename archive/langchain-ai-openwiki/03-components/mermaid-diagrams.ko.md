---
name: mermaid-diagrams
description: 생성되는 wiki page에 Mermaid diagram을 넣습니다. runtime/request flow, call sequence, state machine/lifecycle, data model/entity relationship, trivial하지 않은 control flow를 문서화할 때 사용합니다. 이런 내용은 prose보다 diagram이 명확하기 때문입니다. update run이 이미 mermaid fence가 있는 page 또는 이전 run이 degrade한 text fence가 있는 page를 건드릴 때도 사용합니다.
---

# 생성된 Wiki Page의 Mermaid Diagram

diagram은 장식이 아니라 고품질 wiki generation의 일부입니다. flow, lifecycle, data model을 시각적으로 이해하기 쉬운 곳에는 가장 관련 있는 page에 fenced ```mermaid block을 넣습니다.

## Diagram type 선택

- component 간 runtime/request flow(auth flow, request lifecycle, agent tool loop)에는 `sequenceDiagram`.
- lifecycle과 state machine(job state, connection state, run phase)에는 `stateDiagram-v2`.
- data model과 entity relationship에는 `erDiagram`.
- branch control flow와 decision logic에는 `flowchart TD`.

## 규율

- 모든 diagram은 검사한 source에 근거합니다. code가 뒷받침하지 않는 participant, state, entity, relationship을 만들지 않습니다.
- high-value case를 다룹니다. page가 request/runtime flow, call sequence, lifecycle/state machine, data model을 문서화한다면 diagram을 추가합니다. repository wiki에는 전체 개요 하나만이 아니라 보통 이런 diagram이 여럿 있습니다. navigation, reference table, pure configuration page는 건너뜁니다.
- 모든 page를 꾸미기보다 강한 diagram 몇 개를 우선합니다. 필요한 page의 정확한 diagram 하나가 모든 page에 억지로 넣은 diagram보다 낫습니다.
- 각 diagram 바로 아래에 무엇을 보이는지 한 줄 caption을 둡니다.
- OpenWiki는 run 뒤 모든 Mermaid fence를 검증하고 parse하지 못한 fence는 plain text fence로 변환합니다. degrade된 diagram은 품질 failure이므로 아래 syntax rule을 따라야 합니다.

## Syntax 안전성

다음 규칙은 가장 흔한 rendering breakage를 막습니다. 확신이 없으면 label을 바꾸어 씁니다.

- node, message, edge label 안에 semicolon이나 pipe를 넣지 않습니다.
- label에 escape하지 않은 angle bracket을 넣지 않습니다. `returns Promise<User>` 대신 `returns Promise of User`를 씁니다.
- `flowchart`에서는 parenthesis, bracket, 다른 punctuation이 든 label을 double quote로 감쌉니다. 예: `A["calls foo(bar)"]`.
- `flowchart`에서는 bare word `end`를 node id로 쓰지 않고, `o` 또는 `x` 뒤에 dash로 시작하는 node id도 쓰지 않습니다(둘 다 edge-marker syntax). node 이름을 바꿉니다.
- `sequenceDiagram`에서 space/punctuation이 있는 participant name에는 alias가 필요합니다. 예: `participant AS as Auth Service`.
- Mermaid reserved word를 participant name, alias, node id로 쓰지 않습니다: `note`, `end`, `loop`, `alt`, `opt`, `par`, `and`, `else`, `activate`, `deactivate`, `class`, `state`, `click`, `link`. 예를 들어 notification participant는 `Note`(reserved `note`와 충돌)가 아니라 `Notifier`를 씁니다.
- `erDiagram`의 entity/attribute name은 하나의 identifier-like token이어야 합니다. 사람에게 보일 phrasing은 relationship label에 둡니다.
- label은 짧게 유지합니다. 설명은 diagram이 아니라 주변 prose 또는 caption으로 옮깁니다.

## Update run

- 잘못된 diagram은 보존해야 할 기존 구조가 아니라 stale claim입니다. source change가 diagram을 부정확하게 만들면 주변 prose를 고치는 edit과 같은 edit에서 diagram을 갱신합니다.
- 아직 정확한 diagram은 다시 쓰지 않습니다. 바뀌지 않은 diagram을 regenerate하면 diff noise가 생깁니다.
- page에 `openwiki: mermaid parse failed`로 시작하는 HTML comment가 앞에 붙은 text fence가 있으면, 이전 run이 degrade한 diagram입니다. comment의 parser error로 syntax를 고치고 ```mermaid fence를 복원하며 comment를 삭제합니다.
