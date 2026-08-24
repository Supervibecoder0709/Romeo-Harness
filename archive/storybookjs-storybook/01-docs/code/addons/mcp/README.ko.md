# Storybook MCP Addon

MCP 기반 UI 개발 워크플로를 위한 Storybook addon입니다.

<div align="center">
	<img src="./addon-mcp-claude-code-showcase.gif" alt="Storybook MCP Addon Demo" />
</div>

설치 안내, 사용 예, API 등은 [문서](https://storybook.js.org/docs/next/ai/mcp/overview/?ref=readme)를 참조하세요.

## 설정

기본적으로 addon은 MCP server를 /mcp에 노출합니다. .storybook/main.ts에서 다른 literal endpoint path를 설정할 수 있습니다.

~~~ts
export default {
	addons: [
		{
			name: '@storybook/addon-mcp',
			options: {
				endpoint: '/custom-mcp',
			},
		},
	],
};
~~~

endpoint는 /custom-mcp 또는 /tools/mcp 같은 URL pathname이어야 합니다.

Storybook에 대해 더 알아보려면 [storybook.js.org](https://storybook.js.org/?ref=readme)를 방문하세요.

원문: code/addons/mcp/README.md (고정 SHA db12626a58d505f5551ae1d2c714c6249849212a)

