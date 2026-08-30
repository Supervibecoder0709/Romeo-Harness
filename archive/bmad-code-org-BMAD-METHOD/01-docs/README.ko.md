![BMad Method](banner-bmad-method.png)

[![Version](https://img.shields.io/npm/v/bmad-method?color=blue&label=version)](https://www.npmjs.com/package/bmad-method)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D20.12.0-brightgreen)](https://nodejs.org)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.10-blue?logo=python&logoColor=white)](https://www.python.org)
[![uv](https://img.shields.io/badge/uv-package%20manager-blueviolet?logo=uv)](https://docs.astral.sh/uv/)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289da)](https://discord.gg/gk8jAdXWmj)

**Build More Architect Dreams** — BMad Method Module Ecosystem을 위한 AI 기반 애자일 개발 모듈입니다. 버그 수정부터 엔터프라이즈 시스템까지 조정되는 규모 적응형 지능을 갖춘, 포괄적인 Agile AI Driven Development 프레임워크를 지향합니다.

**100% 무료·오픈소스입니다.** paywall, gated content, gated Discord가 없습니다. 유료 커뮤니티나 강좌를 살 수 있는 사람만이 아니라 모두에게 힘을 주는 것을 믿습니다.

## BMad Method를 쓰는 이유

전통적인 AI 도구는 사용자를 대신해 생각하여 평균적인 결과를 만들 수 있습니다. BMad agent와 facilitator workflow는 AI와 협력하여 최선의 사고를 끌어내도록, 구조화된 과정을 안내하는 전문 협업자로 동작합니다.

- **AI Intelligent Help** — 다음에 무엇을 할지 안내가 필요하면 언제든 `bmad-help` skill을 호출합니다.
- **Scale-Domain-Adaptive** — project 복잡도에 맞춰 planning 깊이를 자동 조정합니다.
- **Structured Workflows** — analysis, planning, architecture, implementation 전반의 agile best practice에 기반합니다.
- **Specialized Agents** — PM, Architect, Developer, UX 등을 포함한 12명 이상의 domain expert를 제공합니다.
- **Party Mode** — 여러 agent persona를 한 session에 불러 협업·토론합니다.
- **Complete Lifecycle** — brainstorming부터 deployment까지의 lifecycle을 다룹니다.

[**docs.bmad-method.org**에서 더 알아보기](https://docs.bmad-method.org)

---

## 🚀 BMad의 다음 단계

**V6가 도착했고 이제 시작입니다!** BMad Method는 Cross Platform Agent Team과 Sub Agent 지원, Skills Architecture, BMad Builder v1, Dev Loop Automation 등을 포함해 빠르게 발전하고 있습니다.

**[📍 전체 Roadmap 보기 →](https://docs.bmad-method.org/roadmap/)**

---

## 빠른 시작

**사전 요구사항**: [Node.js](https://nodejs.org) v20.12+ · [Python](https://www.python.org) 3.10+ · [uv](https://docs.astral.sh/uv/)

```bash
npx bmad-method install
```

> 최신 prerelease build가 필요하다면 `npx bmad-method@next install`을 사용합니다. 기본 설치보다 변경 폭이 클 수 있습니다.

installer prompt를 따른 뒤, project folder에서 AI IDE(Claude Code, Cursor 등)를 엽니다.

**비대화형 설치**(CI/CD용):

```bash
npx bmad-method install --directory /path/to/project --modules bmm --tools claude-code --yes
```

어떤 module config option이든 `--set <module>.<key>=<value>`로 override할 수 있습니다(반복 가능). `--list-options [module]`을 실행하면 이 machine에서 알려진 official key(내장 module과 cache된 external official)를 볼 수 있습니다.

```bash
npx bmad-method install --yes \
  --modules bmm --tools claude-code \
  --set bmm.project_knowledge=research \
  --set bmm.user_skill_level=expert
```

[모든 설치 옵션 보기](https://docs.bmad-method.org/how-to/non-interactive-installation/)

> **무엇을 해야 할지 모르겠나요?** `bmad-help`에게 물어보세요. 정확히 다음 단계와 선택 사항을 알려 줍니다. 예: `bmad-help I just finished the architecture, what do I do next?`

## Modules

BMad Method는 specialized domain용 official module로 확장됩니다. 설치 중에도, 이후에도 사용할 수 있습니다.

| Module | 목적 |
| --- | --- |
| **[BMad Method (BMM)](https://github.com/bmad-code-org/BMAD-METHOD)** | 34개 이상의 workflow를 가진 core framework |
| **[BMad Builder (BMB)](https://github.com/bmad-code-org/bmad-builder)** | custom BMad agent와 workflow 생성 |
| **[Test Architect (TEA)](https://github.com/bmad-code-org/bmad-method-test-architecture-enterprise)** | risk-based test strategy와 automation |
| **[Game Dev Studio (BMGD)](https://github.com/bmad-code-org/bmad-module-game-dev-studio)** | game development workflow(Unity, Unreal, Godot) |
| **[Creative Intelligence Suite (CIS)](https://github.com/bmad-code-org/bmad-module-creative-intelligence-suite)** | innovation, brainstorming, design thinking |

## Web Bundles

V4에서 web bundle을 제공했고, V6에서 개선된 형태로 다시 제공합니다.

Web bundle은 선택한 BMad skill을 **Google Gemini Gems**와 **ChatGPT Custom GPTs**로 설치할 수 있게 묶습니다. brainstorming, product brief, PRD, PRFAQ, UX spec, market/industry research 같은 초기 planning은 web LLM subscription에서 하고, 다듬은 artifact를 IDE로 가져와 구현할 수 있습니다. Planning은 장기 작업에서 metered IDE token 대신 flat-rate subscription을 쓰므로 비용을 아낄 수 있습니다. 이용 가능한 가장 좋은 model을 Gemini 또는 ChatGPT에서 선택하세요.

현재 제공: brainstorming, product brief, PRFAQ, PRD, UX, market & industry research.

**[bmadcode.com/web-bundles](https://bmadcode.com/web-bundles/)에서 살펴보고 설치하세요.** bundle마다 card, Gemini/ChatGPT inline install step, one-click ZIP download를 제공합니다. 개념은 [web bundles guide](https://docs.bmad-method.org/explanation/web-bundles/)를 참조하세요.

## 문서

[BMad Method Docs Site](https://docs.bmad-method.org) — tutorial, guide, concept, reference

**빠른 링크:**

- [Getting Started Tutorial](https://docs.bmad-method.org/tutorials/getting-started/)
- [이전 버전에서 업그레이드](https://docs.bmad-method.org/how-to/upgrade-to-v6/)
- [Test Architect 문서](https://bmad-code-org.github.io/bmad-method-test-architecture-enterprise/)

## Community

- [Discord](https://discord.gg/gk8jAdXWmj) — 도움받기, 아이디어 공유, 협업
- [YouTube](https://youtube.com/@BMadCode) — tutorial, master class 등
- [X / Twitter](https://x.com/BMadCode)
- [Website](https://bmadcode.com)
- [GitHub Issues](https://github.com/bmad-code-org/BMAD-METHOD/issues) — bug report와 feature request
- [Discussions](https://github.com/bmad-code-org/BMAD-METHOD/discussions) — community 대화

## BMad 지원

BMad는 모두에게 무료이며 앞으로도 그럴 것입니다. 이 repo에 star를 남기거나, [coffee를 사 주거나](https://buymeacoffee.com/bmad), corporate sponsorship은 <contact@bmadcode.com>으로 이메일을 보내 주세요.

## 기여

기여를 환영합니다. 가이드는 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## License

MIT License — 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.

---

**BMad** 및 **BMAD-METHOD**는 BMad Code, LLC의 상표입니다. 자세한 내용은 [TRADEMARK.md](TRADEMARK.md)를 참조하세요.

[![Contributors](https://contrib.rocks/image?repo=bmad-code-org/BMAD-METHOD)](https://github.com/bmad-code-org/BMAD-METHOD/graphs/contributors)

기여자 정보는 [CONTRIBUTORS.md](CONTRIBUTORS.md)를 참조하세요.
