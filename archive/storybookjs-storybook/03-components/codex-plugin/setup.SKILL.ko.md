---
name: setup
description: Storybook이 이미 설치되어 있고 사용자가 실제 component를 위한 동작하는 preview file과 story를 원할 때 이 skill을 사용합니다.
---

사전 조건:

1. Storybook이 존재하는지 확인합니다(package.json, .storybook/). 없다면 $storybook:init으로 전환합니다.
2. Storybook은 최소 10.5여야 합니다(10.5가 아직 release되지 않았다면 next). 더 오래되었거나 먼저 upgrade/repair가 필요하면 $storybook:upgrade로 전환합니다.

프로젝트 root에서(또는 monorepo에서는 Storybook package에서) npx storybook ai setup을 실행합니다.

**출력된 Markdown을 정확히 따르세요.** 자체 계획으로 대체하지 마세요.

원문: code/lib/codex-plugin/plugins/storybook/skills/setup/SKILL.md

