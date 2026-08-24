---
name: init
description: Storybook이 아직 설정되지 않은 프로젝트에 Storybook을 추가할 때 사용합니다.
---

1. 프로젝트 root directory 안에서 npm create storybook@latest를 실행해 최신 Storybook을 설치합니다. 적절한 경우 pnpm create storybook@latest 또는 yarn create storybook 같은 일치하는 package-manager 명령을 사용합니다.
2. 초기화가 성공한 뒤 npx storybook add @storybook/addon-mcp를 실행합니다.
3. .storybook/preview.ts file 같은 프로젝트별 Storybook 설정을 사용자가 준비하도록 돕기 위해 $storybook:setup skill을 호출합니다.

원문: code/lib/codex-plugin/plugins/storybook/skills/init/SKILL.md

