# Storybook Codex Plugin

Storybook의 Codex plugin을 사용하면 agent를 여러분의 Storybook에 연결할 수 있습니다. 그러면 agent는 plugin의 skill과 tool을 사용해 UI를 생성하고, test를 실행하고, Storybook에서 작업을 preview할 수 있습니다. agent는 관련 story를 ADE preview에서 자동으로 열 수 있으므로 컴포넌트와 코드를 검사할 수 있습니다.

## 요구 사항

- Storybook 10.5 이상
- [Codex](https://openai.com/codex/)

## 설치

> [!NOTE]
> 이 plugin은 [experimental](https://storybook.js.org/docs/releases/features#experimental)이므로 아직 Codex marketplace에 추가되지 않았습니다. 아래 안내에 따라 Storybook marketplace를 Codex에 추가한 뒤 그곳에서 plugin을 설치합니다.

1. 다음 명령으로 Storybook marketplace를 Codex에 추가합니다.

~~~bash
codex plugin marketplace add storybookjs/storybook
~~~

2. 이어서 plugin을 설치합니다.

~~~bash
codex plugin add storybook@storybook
~~~

3. plugin을 사용할 수 있는지 확인합니다.

~~~bash
codex plugin list --marketplace storybook
~~~

이제 준비되었습니다!

### plugin 업데이트

plugin이 공식 marketplace에서 제공되기 전까지는 plugin을 제거한 뒤 설치 안내를 다시 수행하여 업데이트할 수 있습니다.

plugin을 제거하려면 다음을 수행합니다.

1. 다음 명령으로 Codex에서 plugin을 제거합니다.

~~~bash
codex plugin remove storybook@storybook
~~~

2. 이어서 Storybook marketplace를 제거합니다.

~~~bash
codex plugin marketplace remove storybook
~~~

3. 위 [설치 안내](#설치)를 따라 marketplace와 plugin을 다시 추가합니다.

## 사용

이 plugin에는 agent가 사용할 수 있는 [skills](#skills)와 [tools](#tools)를 언제 어떻게 사용할지 이해하도록 돕는 안내가 포함됩니다. agent가 UI 작업을 수행할 때 plugin을 사용해 story를 생성하고, test를 실행하고, Storybook에서 작업을 preview할 수 있습니다. 특정 작업을 수행하게 하려면 prompt에서 plugin skill을 명시적으로 호출할 수도 있습니다(예: /upgrade).

agent는 여러분이 작업을 검토할 수 있도록 관련 story 또는 [agentic review summary](https://storybook.js.org/docs/10.5/ai/agentic-review)를 ADE preview에서 자동으로 엽니다.

## Skills

Storybook plugin을 설치한 agent가 사용할 수 있는 skill입니다. prompt에서 참조할 수 있고(예: /upgrade), agent가 작업 중 간접적으로 사용할 수도 있습니다.

### init

프로젝트에 Storybook을 초기화합니다(즉, [npm create storybook@latest](https://storybook.js.org/docs/get-started/install)를 실행). [@storybook/addon-mcp](../../addons/mcp)를 설치한 뒤 [setup](#setup) skill을 실행합니다.

### setup

agentic workflow를 위해 Storybook을 설정하고, 프로젝트가 컴포넌트를 올바르게 render하도록 자동 설정하며, 여러 컴포넌트 유형의 story file을 작성합니다. 자세한 내용은 [agentic setup docs](https://storybook.js.org/docs/ai/agentic-setup)를 참조하세요.

### stories

모든 UI 작업에 story를 사용하도록 agent에 지시합니다.

### upgrade

Storybook을 최신 버전으로 upgrade합니다. 프로젝트에서 [npx storybook upgrade](https://storybook.js.org/docs/releases/upgrading)를 실행하는 것과 같습니다.

## Tools

plugin을 설치한 agent는 [Storybook MCP server의 모든 tool](https://storybook.js.org/docs/ai/mcp/overview#toolsets)을 사용할 수 있습니다.

원문: code/lib/codex-plugin/README.md (고정 SHA db12626a58d505f5551ae1d2c714c6249849212a)

