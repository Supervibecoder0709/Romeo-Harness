---
name: stories
description: component, story, style, CSS, theme, color, design token 등 UI가 보이는 방식을 바꾸는 모든 항목을 생성·수정·삭제하기 전에 예외 없이 먼저 호출합니다. UI를 검증하기 위해 Storybook을 시작하거나 preview하는 경우, component·story·UI state를 보여주거나 browse/list하는 요청, docs·props·usage 조회에도 사용합니다.
---

사전 조건:

1. 프로젝트에 Storybook이 설치되어 있어야 합니다. 사용자가 이 skill을 명시적으로 호출하고 Storybook 설치를 승인한 경우에만 $storybook:init skill을 호출해 Storybook을 설정합니다.
2. Storybook은 최소 10.5여야 합니다(10.5가 아직 release되지 않았다면 next). 사용자가 Storybook upgrade를 명시적으로 승인한 경우에만 $storybook:upgrade skill을 호출합니다.
3. @storybook/addon-mcp가 설치되어 있는지 확인합니다. 없으면 npx storybook add @storybook/addon-mcp로 설치합니다.

sandboxed Codex environment에서는 모든 Storybook CLI 명령을 require_escalated로 실행합니다. sandbox network/port 제한은 혼란스러운 실패를 일으킬 수 있습니다(예: dev server가 bind할 여유 port를 찾지 못함).

Storybook dev server와 모든 storybook ai 명령은 Storybook이 설치된 동일 working directory에서 실행합니다. monorepo에서는 대개 packages/ui 같은 leaf package입니다.

STORYBOOK_FEATURE_AI_CLI=1 npx storybook ai --help를 실행하고 출력 전체를 읽어 UI 변경 작업, story 작성, 생성·수정·삭제하는 모든 frontend component와 story를 동기화하기 위한 **필수 순서 workflow**를 확인합니다. 이 workflow는 story 작성, story preview, 선별된 Storybook review 표시 방법을 설명합니다.

session에서 storybook ai 명령을 처음 호출하기 전에 STORYBOOK_FEATURE_AI_CLI=1 npx storybook ai <command> --help를 실행하고 전체를 읽습니다. top-level help에는 명령만 나열되고, 각 명령의 payload shape와 usage rule(언제 어떤 field를 포함하는지)은 해당 help 출력에 있습니다. 명령 이름만 보고 --json payload를 추측하지 마세요. validation error는 누락된 필수 field만 알려줄 뿐 workflow가 기대하는 선택 field까지 알려주지는 않습니다.

일부 명령에는 실행 중인 Storybook dev server가 필요합니다.

1. 이 프로젝트 Storybook을 이미 serve하는 dev server가 있으면 두 번째 server를 시작하지 말고 URL(대개 http://localhost:6006)을 probe해 재사용합니다. 없다면 프로젝트가 선호하는 package manager와 기존 package.json Storybook script(가능하면 npm run storybook)를 사용해 background에서 시작합니다. 필요한 명령 전에 URL이 응답할 때까지 기다립니다.
2. dev server는 일시적 검증 도구가 아니라 deliverable의 일부입니다. 작업 후에도 사용자가 story를 계속 browse할 수 있게 실행 상태로 두고, 검증 후 kill하지 않습니다.
3. control-in-app-browser skill을 사용할 수 있으면, 최종 답변에 넣을 Storybook review 또는 story preview URL을 그 skill으로 in-app browser에서 열어 사용자가 Codex 안에서 결과를 나란히 보게 합니다.

원문: code/lib/codex-plugin/plugins/storybook/skills/stories/SKILL.md

