<!-- markdownlint-disable MD033 MD041 -->

<div align="center">

<img alt="OpenWiki" src="./static/openwiki-lockup.png" width="620">

### 에이전트를 위해 만들고, 사람이 탐색하는 자기 유지형 위키

[![npm version](https://img.shields.io/npm/v/openwiki.svg?style=flat&labelColor=030710&color=1A6FB5)](https://www.npmjs.com/package/openwiki)
[![downloads](https://img.shields.io/npm/dm/openwiki.svg?style=flat&labelColor=030710&color=1A6FB5)](https://www.npmjs.com/package/openwiki)
[![Node](https://img.shields.io/node/v/openwiki.svg?style=flat&labelColor=030710&color=1A6FB5)](https://nodejs.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-1A6FB5.svg?style=flat&labelColor=030710)](./LICENSE)
[![Built with Deep Agents](https://img.shields.io/badge/built%20with-DeepAgents-1A6FB5.svg?style=flat&labelColor=030710)](https://github.com/langchain-ai/deepagentsjs)

<a href="https://trendshift.io/repositories/70339?utm_source=trendshift-badge&amp;utm_medium=badge&amp;utm_campaign=badge-trendshift-70339" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/trendshift/repositories/70339/daily" alt="langchain-ai%2Fopenwiki | Trendshift" width="250" height="55"/></a>

</div>

OpenWiki는 코드베이스 또는 개인 지식을 위한 위키를 작성하고 유지하는 CLI입니다. 에이전트가 소스를 읽어 소유권이 사용자에게 있는 연결된 Markdown 위키를 종합하고, 모든 변경 시 최신 상태를 유지합니다. 이는 에이전트가 메모리로 읽도록 만들었으며, 사람이 탐색할 수 있는 대화형 visualizer도 제공합니다.

**OpenWiki가 제공하는 것:**

- [Deep Agents](https://github.com/langchain-ai/deepagentsjs) 문서화 에이전트가 생성하고 정확성을 유지하는 **에이전트 작성 문서**.
- 저장소용 `code` 위키와 개인 지식용 `personal` 위키, 두 가지 모드.
- OpenAI·Anthropic부터 Bedrock·Gemini·모든 OpenAI-compatible gateway까지, 기본 제공되는 13개 모델 provider.
- host의 모델과 repository tool을 사용하는 Codex 및 Claude Code용 **coding-agent integration**.
- 중요한 사실을 버전이 있는 source evidence로 추적하고 evidence가 바뀌면 드러내는 **Grounded Claims**.
- Custom MCP, Notion, Slack, Gmail, X, Web Search, Hacker News, LangSmith, local git repository용 기본 connector 9개.
- 모든 위키를 live 탐색 가능한 node graph로 바꾸는 **대화형 visualizer**.
- GitHub Actions, GitLab CI 또는 Bitbucket Pipelines를 통한 자동 갱신.
- 검증된 Mermaid diagram이 포함된 Open Knowledge Format([OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)) 출력.

## 🎉 새로운 기능

- **Grounded Claims:** 이제 code wiki의 중요한 사실에는 버전이 있는 source evidence가 붙습니다. 해당 evidence가 변경되거나 사라지면 OpenWiki는 어떤 proposition을 확인·재작성·폐기해야 하는지 정확히 압니다.
- **OpenWiki integrations:** Codex 또는 Claude Code 안에서 OpenWiki를 직접 실행합니다. coding agent는 인증된 model과 native repository tool을 사용하고 OpenWiki는 문서 lifecycle을 관리합니다.
- **OKF v0.2:** 모든 위키는 결정적인 generation provenance와 검증된 trust/lifecycle metadata를 갖춘 portable Open Knowledge Format bundle입니다.
- **게시 가능한 visualizer:** 대화형 graph와 Markdown reader를 GitHub Pages, MkDocs 또는 임의의 static host에 배포할 수 있는 static site로 내보냅니다.

## 빠른 시작

CLI를 설치합니다(Node.js 22 이상).

```sh
npm install -g openwiki
```

현재 repository용 위키를 생성합니다. 첫 실행에서는 provider, key, model을 고르고 `openwiki/`에 문서를 씁니다.

```sh
openwiki --init
```

`openwiki --init`을 다시 실행하면 기존에 생성한 repository wiki와 Claims를 완전히 새로 생성한 결과로 교체합니다. OpenWiki는 사용자가 작성한 `openwiki/INSTRUCTIONS.md` brief는 보존하며, generation이 실패하거나 취소되면 이전 wiki를 복원합니다.

변경 시 문서 PR을 열도록 scheduled CI job을 추가하면 최신 상태를 자동으로 유지할 수 있습니다.

- **GitHub Actions:** [`openwiki-update.yml`](./examples/openwiki-update.yml)을 `.github/workflows/openwiki-update.yml`로 복사합니다.
- **GitLab CI:** [`openwiki-update.gitlab-ci.yml`](./examples/openwiki-update.gitlab-ci.yml)을 `.gitlab-ci.yml`에 복사하거나 pipeline에서 include합니다.
- **Bitbucket Pipelines:** [`openwiki-update.bitbucket-pipelines.yml`](./examples/openwiki-update.bitbucket-pipelines.yml)을 `bitbucket-pipelines.yml`에 복사한 뒤 `openwiki-update` pipeline을 schedule합니다.

> [!NOTE]
> Windows에서는 Node.js package manager(`npm install -g openwiki` 또는 `pnpm add -g openwiki`)로 설치하세요. `bun`으로 설치하면 `better-sqlite3` native dependency를 compile하는 경로로 갈 수 있으며, 이 경우 Desktop development with C++ workload가 포함된 Visual Studio Build Tools가 필요합니다.

## Coding-agent integrations

OpenWiki는 자체 model을 실행하는 대신 기존 coding agent 안에서 실행할 수 있습니다. coding agent가 repository를 조사하고, 문서를 계획·작성하며 필요할 때 native tool과 subagent를 사용합니다. OpenWiki는 repository를 준비하고 실행을 제약하며 index, provenance, setup file, metadata를 결정적으로 완료하는 MCP lifecycle을 제공합니다.

<div align="center">
  <img alt="Codex initializes an OpenWiki for a repository." src="./static/openwiki-codex.gif" width="880">
</div>

coding agent용 integration 하나를 설치합니다.

```sh
openwiki integrations install codex
openwiki integrations install claude
```

지원 target은 **Codex**와 **Claude Code**입니다. 둘 다 기본적으로 user level에 설치되므로 설치 하나로 모든 Git repository에서 동작합니다. project path는 Git repository root로 resolve됩니다. 설치 후 coding agent를 재시작하고 repository를 연 뒤 다음처럼 요청합니다.

```text
Initialize this repository's OpenWiki from the current source and tests.
```

이미 있는 wiki는 다음처럼 요청합니다.

```text
Update this repository's OpenWiki for changes since its last successful run.
```

현재 host-driven run은 personal brain이 아니라 repository code wiki를 지원합니다. coding agent의 인증된 model session을 쓰므로 OpenWiki provider credential은 필요하지 않습니다. OpenWiki는 여전히 deterministic setup과 finalization을 소유하고, coding agent는 research, planning, factual authoring, semantic review를 소유합니다.

외부 coding-agent integration은 현재 repository source와 test만 사용합니다. LangSmith를 포함한 connector-sourced context는 아직 지원하지 않습니다.

integration은 lifecycle bookend와 Grounded Claims inspection/resolution을 노출합니다. Codex 또는 Claude는 native repository tool로 Markdown을 작성하고, OpenWiki는 사실 페이지의 evidence-backed proposition을 검증하고 저장합니다.

`openwiki integrations list`로 user-level 설치 상태를 확인하고 `openwiki integrations uninstall <host>`로 integration을 안전하게 제거합니다. repository-scoped 상태는 `list`, `install`, `uninstall`에 `--project [path]`를 추가합니다.

새 coding agent를 추가하는 contributor는 [Adding a coding-agent integration](CONTRIBUTING.md#adding-a-coding-agent-integration)을 따릅니다.

## Grounded Claims

OpenWiki는 Markdown 파일의 마지막 generation 시점만 추적하는 것이 아니라 사실 페이지 뒤의 중요한 proposition을 추적해 code wiki가 스스로 바로잡히도록 합니다. Claim은 미래의 agent가 의존하는 behavior, responsibility, architecture, data flow, invariant, failure semantic, configuration, security boundary를 포함합니다. 각 claim은 `repo://src/server.ts#L40-L82` 같은 정확한 repository evidence와, claim을 만들 때 관찰한 evidence version을 가리킵니다.

갱신 전에 OpenWiki는 그 evidence version을 확인합니다. source line이 바뀌거나 사라지면 영향받은 claim은 stale 또는 unresolved가 됩니다. 이 debt는 관련 page를 읽을 때까지 조용히 있다가, agent가 proposition을 검사하고 확인·수정·철회할 수 있습니다. Markdown은 깔끔하게 유지하고 구조화된 claim 상태는 `openwiki/.claims/`에 함께 둡니다.

Grounded Claims는 현재 repository code wiki와 repository evidence에 적용됩니다. LangSmith 전용 관찰을 포함한 connector-derived fact는 claim으로 만들지 않습니다.

## 두 가지 모드

OpenWiki는 두 모드 중 하나로 실행합니다. 인자 없는 `openwiki`, `openwiki --init`, `openwiki --update`는 기본적으로 **code** mode이며, personal brain에는 `personal` positional 또는 `--mode personal`을 추가합니다.

| Mode | 문서 대상 | 쓰는 위치 | 시작 방법 |
| --- | --- | --- | --- |
| **Code** _(기본)_ | 현재 repository | repo의 `openwiki/` | `openwiki --init` |
| **Personal** | 연결한 source | `~/.openwiki/wiki` | `openwiki personal --init` |

기본적으로 CLI는 run 뒤에도 열려 있어 후속 메시지를 보낼 수 있습니다. 최종 출력을 print하고 종료하는 one-shot run은 `-p` / `--print`를 추가합니다. `--init`, `--update`는 interactive terminal에서 성공 시 자동 종료되므로 동일한 command를 one-shot 또는 interactive로 쓸 수 있습니다.

### Local state directory

OpenWiki는 기본적으로 local credential, personal wiki, connector data, conversation history, skill을 `~/.openwiki`에 저장합니다. mounted container volume처럼 다른 writable directory를 쓰려면 OpenWiki를 시작하기 전에 `OPENWIKI_CONFIG_DIR`을 설정합니다.

```sh
OPENWIKI_CONFIG_DIR=/data/openwiki openwiki personal --init
```

이 override는 별도 state directory를 선택할 뿐 기존 `~/.openwiki` directory를 이동하거나 삭제하지 않습니다. 보존할 state는 직접 복사하고, OpenWiki가 current user만 접근하도록 permission을 제한하므로 이 변수에는 dedicated directory를 지정하세요.

## 위키 탐색

어떤 wiki든 live, side-by-side Markdown reader가 있는 대화형 node graph로 바꿉니다.

```sh
openwiki visualize
```

<div align="center">
  <img alt="The OpenWiki visualizer: an interactive node graph beside a live Markdown reader." src="./static/visualizer.gif" width="880">
</div>

이는 `./openwiki`를 local loopback address(`127.0.0.1`, 네트워크에 노출하지 않음)에서 제공하고 browser로 graph를 엽니다. server가 실행 중인 동안 wiki file edit은 자동 반영됩니다. 다른 directory에는 path를 전달하고, port 선택에는 `--port <port>`(충돌 시 증가, 기본 `4321`), browser를 열지 않으려면 `--no-open`을 사용합니다.

```sh
openwiki visualize openwiki --port 4400 --no-open
```

생성 문서 옆에 visualizer를 게시하려면 server를 시작하는 대신 static directory를 export합니다.

```sh
openwiki visualize openwiki --export docs/openwiki-visualizer
```

export에는 `index.html`, `client.js`, `client-lib.js`, `styles.css`, `graph.json`이 들어갑니다. client는 sibling graph file을 읽고 live reload를 쓰지 않으므로 GitHub Pages, MkDocs 또는 다른 static host에서 제공할 수 있습니다. `--export`는 `--port` 또는 `--no-open`과 함께 쓸 수 없습니다.

> [!NOTE]
> page는 public CDN에서 graph, Markdown, diagram library를 로드하므로 local/static viewer 모두 인터넷 연결이 필요합니다.

## Source 연결

`personal` mode에서 OpenWiki는 이미 사용하는 tool의 지식을 local wiki로 수집·종합합니다. 첫 실행 onboarding은 **Custom MCP, local git repository, Notion, Gmail, X/Twitter, Web Search, Hacker News** 설정을 제공합니다. Slack도 OAuth app과 HTTPS callback을 구성하면 쓸 수 있습니다.

ingestion run 중 deterministic connector tool은 raw data와 manifest를 `~/.openwiki/connectors/<connector>/raw/`에 쓰고, source-specific agent run이 `~/.openwiki/wiki/`의 wiki를 종합합니다. 같은 connector를 여러 번 구성할 수 있습니다(예: AI research용 Web Search 하나, NBA news용 또 하나). OpenWiki는 이를 `web-search-1`, `web-search-2`처럼 별도 instance로 저장합니다.

```sh
openwiki auth notion        # provider용 local browser OAuth flow 실행
openwiki ingest all         # 구성한 모든 source 실행
openwiki ingest web-search  # connector의 source 하나 실행
```

<details>
<summary><b>Connector 세부 사항과 OAuth</b></summary>

<br/>

- `git-repo`는 구성한 local repository path를 읽고 compact manifest를 씁니다.
- `custom-mcp`는 구성한 HTTP 또는 stdio MCP server에 연결하며 명시적으로 안전한 read-only tool만 허용합니다.
- `x`는 OAuth user-context credential로 X API를 직접 사용해 home timeline, user post, mention, bookmark, list post를 가져옵니다.
- `notion`은 hosted Notion MCP server를 target으로 하므로 token을 붙여 넣는 대신 Notion OAuth로 인증합니다.
- `google`은 OAuth user credential로 Gmail API를 직접 사용해 최근 mail을 가져옵니다.
- `slack`은 OAuth user/bot token으로 Slack Web API를 사용해 scoped conversation과 search result를 수집합니다.
- `web-search`는 LangChain을 통해 Tavily를 사용하며 `TAVILY_API_KEY`가 필요합니다.
- `hackernews`는 credential 없이 public Hacker News feed와 search API를 사용합니다.

`openwiki auth <provider>`는 local browser OAuth flow를 실행하고, 반환 token을 `~/.openwiki/.env`에 저장하며, 가능한 경우 connector config를 만들고 MCP-backed provider의 MCP tool을 discovery합니다. Slack과 Gmail은 app client credential이 이미 이 file에 있어야 합니다. Notion은 hosted MCP의 dynamic client registration을 사용하고 X는 PKCE가 있는 OAuth 2.0을 사용합니다. `openwiki auth configure <provider>`와 `openwiki auth tools <provider>`는 advanced retry command입니다.

connector secret은 env var name으로 참조하며 `~/.openwiki/.env`에 저장합니다. connector config file에는 raw secret value가 들어가지 않습니다.

**Slack OAuth tunnel.** `openwiki ngrok start`는 random HTTPS forwarding URL의 ngrok tunnel을 시작하고, ngrok의 local inspection API를 읽어 `/callback`을 붙인 뒤 `OPENWIKI_HTTPS_OAUTH_REDIRECT_URI`를 자동 저장합니다. 출력된 callback URL을 Slack에 등록하세요. fixed domain이면 `openwiki ngrok start https://<your-ngrok-domain>`을 실행합니다.

</details>

### LangSmith connector (code mode)

위 connector는 `personal` wiki를 채웁니다. **LangSmith** connector는 반대로 `code` wiki를 보강합니다. 선택한 project의 최근 LangSmith trace(tool call, outcome, latency)를 official LangSmith SDK로 가져와 repository 문서가 source가 말하는 내용뿐 아니라 code가 runtime에서 실제로 어떻게 동작하는지도 반영하도록 합니다.

`code` mode에서 `openwiki --init` 중 구성합니다. source menu에서 LangSmith를 추가하고 workspace region(US, EU 또는 APAC)과 문서화할 project를 고릅니다. OpenWiki는 workspace와 project 이름만 담고 key 자체는 절대 담지 않는 committed `openwiki/.langsmith.json`을 쓰므로, 모든 teammate와 CI run이 같은 set을 문서화합니다. API key는 environment에서 읽습니다.

```sh
OPENWIKI_LANGSMITH_API_KEY="<your-langsmith-key>"
```

local에서는 setup wizard가 이를 `~/.openwiki/.env`에 저장합니다. CI에서는 repository secret으로 설정하고 run에 export합니다.

> [!NOTE]
> LangSmith key는 workspace와 region에 묶입니다. 둘 이상의 workspace project를 문서화하려면 workspace마다 `OPENWIKI_LANGSMITH_API_KEY_2`, `OPENWIKI_LANGSMITH_API_KEY_3`처럼 각각 key가 있는 entry를 추가합니다. connector는 official US(`api.smith.langchain.com`), EU(`eu.api.smith.langchain.com`), APAC(`apac.api.smith.langchain.com`) host에만 통신합니다.

## 소유권 유지 방식

위키는 소유권이 사용자에게 있는 plain Markdown으로 repository에 남고, OpenWiki가 관리하는 grounding과 run metadata도 함께 versioning됩니다.

- **Agent가 메모리로 읽습니다.** 각 `code` run에서 OpenWiki는 repo root의 `AGENTS.md`, `CLAUDE.md`가 wiki를 가리키도록 유지합니다. 자체 `<!-- OPENWIKI:START -->…<!-- OPENWIKI:END -->` block만 다시 쓰고 나머지는 건드리지 않습니다.
- **Grounding은 wiki와 함께 남습니다.** `openwiki/.claims/`의 versioned claim sidecar는 Markdown과 함께 이동하므로 사실 페이지를 유지할 evidence를 검사·review할 수 있습니다.
- **사용자가 brief를 정합니다.** repository-specific instruction은 `openwiki/INSTRUCTIONS.md`에 둡니다. OpenWiki는 scope와 priority를 위해 읽지만 normal run에서 다시 쓰지 않는 user-authored file입니다.
- **No-op run은 문서를 흔들지 않습니다.** clean update는 model 작업을 건너뛰고 wiki content를 그대로 두며, check가 실행됐음을 기록하려 `.last-update.json`만 새로 고칩니다.
- **Local, private config.** provider choice, key, optional LangSmith tracing은 machine의 `~/.openwiki/.env`에 저장합니다.

## Open Knowledge Format (OKF v0.2)

OpenWiki는 두 mode 모두에서 [Google Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle을 출력하므로 모든 OKF-aware tool로 옮길 수 있습니다.

- 모든 concept document는 비어 있지 않은 `type`의 YAML front matter를 갖습니다. 다른 standard field는 선택 사항입니다.
- page는 마지막 body change를 `generated: {by, at}`로 기록합니다. whitespace를 포함한 body change는 stamp를 진행시키지만 front-matter-only change는 그렇지 않습니다. producer는 `openwiki/<version>`(또는 coding-agent host)로 stamp되어 provenance가 명시됩니다. 기존 page의 legacy v0.1 `timestamp` field도 허용합니다.
- repository page는 grounded Claims evidence를 `sources`로 project합니다. OpenWiki는 결정적으로 식별한 entry를 reconcile하면서 독립적으로 작성한 source는 보존합니다.
- repository page는 비어 있지 않은 complete Claims set을 능동적으로 reconcile하고, final evidence recheck를 통과하며, Claims sidecar를 persist한 뒤에만 `verified: {by: openwiki/<version>, at: ...}`를 받습니다. clean preflight만으로 verification을 만들거나 진행시키지는 않으며 human/other process event는 보존합니다.
- optional v0.2 provenance, trust, lifecycle family(`sources`, `verified`, `status`, `stale_after`)는 있으면 검증합니다.
- concept document 사이의 standard Markdown link가 관계를 표현합니다.
- `index.md`, `log.md`는 concept가 아니라 reserved document입니다. root index는 `okf_version: "0.2"`를 선언합니다.
- producer-defined extension field는 update와 migration을 지나도 보존합니다.

## Diagram

OpenWiki는 prose보다 concept를 더 명확하게 만드는 곳에 **Mermaid** diagram을 넣습니다. runtime flow에는 sequence diagram, data model에는 ER diagram, lifecycle에는 state diagram, control flow에는 flowchart를 사용합니다. diagram은 검사한 source에 근거하고, signal을 더할 때만 추가되며, `--update`에서 동기화됩니다. configuration은 필요 없습니다.

각 run 뒤 OpenWiki는 모든 `mermaid` fence를 검증합니다. validation에 실패한 diagram은 왜 그런지 설명하는 짧은 comment와 함께 plain `text` fence로 in-place 변환되므로, 깨진 block 대신 읽을 수 있는 text로 degrade합니다. 다음 `--update`는 그 comment를 찾아 diagram을 수리하므로 successive run에 걸쳐 품질을 회복합니다.

> [!TIP]
> 기본적으로 OpenWiki는 흔한 문제를 잡는 가벼운 zero-dependency check를 실행합니다. GitHub render와 정확히 일치하는 authoritative validation을 원하면 scheduled workflow처럼 OpenWiki를 실행하는 곳에 Mermaid parser를 설치하세요. 그러면 깨진 diagram이 배포되지 않습니다.
>
> ```sh
> npm install mermaid jsdom
> ```

## Model provider

onboarding 기본값은 `gpt-5.6-terra`를 쓰는 OpenAI입니다. 모든 provider에는 preset model option과 custom model ID 지원이 있으며 credential은 `~/.openwiki/.env`에 저장합니다.

| Provider | Credential |
| --- | --- |
| **OpenAI** _(기본)_ | `OPENAI_API_KEY` |
| **OpenAI (ChatGPT login)** | Browser sign-in, uses your ChatGPT plan |
| **Anthropic** | `ANTHROPIC_API_KEY` |
| **Gemini** (AI Studio) | `GEMINI_API_KEY` |
| **Gemini Enterprise** (Vertex AI) | Google ADC, keyless |
| **AWS Bedrock** | IAM credential |
| **GitHub Copilot** | GitHub CLI session |
| **OpenRouter** | `OPENROUTER_API_KEY` |
| **Nebius / Fireworks / Baseten / NVIDIA NIM** | Provider API key |
| **OpenAI-compatible** (LiteLLM, Ollama, LM Studio, gateway) | Base URL + key |

<details>
<summary><b>GitHub Copilot</b></summary>

<br/>

GitHub Copilot provider는 inference를 OpenAI-compatible Copilot API(`https://api.githubcopilot.com`)로 route하므로 team은 별도 inference key를 provision하지 않고 기존 Copilot subscription을 재사용할 수 있습니다.

1. `openwiki --init` 중 `GitHub Copilot`을 선택합니다. 활성 [GitHub CLI](https://cli.github.com) session이 있으면 OpenWiki가 감지해 재사용을 제안합니다. 없으면 credential prompt에서 <kbd>Tab</kbd>을 눌러 `gh auth login`을 실행하고 sign in합니다.
2. model(예: `gpt-5.5`)을 고릅니다.

OpenWiki는 token을 GitHub CLI 자체 credential store에 둡니다. CI 또는 다른 headless environment에서는 `COPILOT_API_KEY`에 GitHub **OAuth token**을 설정하세요. Personal Access Token은 third-party integration에서 Copilot API가 거절합니다. local config는 token 없이 둘 수 있습니다.

```env
OPENWIKI_PROVIDER="copilot"
OPENWIKI_MODEL_ID="gpt-5.5"
```

CI에서는 `COPILOT_API_KEY` repository secret을 설정하고 `OPENWIKI_PROVIDER=copilot`을 export합니다.

</details>

<details>
<summary><b>AWS Bedrock</b></summary>

<br/>

`bedrock` provider는 하나의 vendor key 대신 IAM credential을 사용해 AWS Bedrock의 foundation model을 호출합니다.

```bash
OPENWIKI_PROVIDER=bedrock
BEDROCK_AWS_ACCESS_KEY_ID=your-access-key-id
BEDROCK_AWS_SECRET_ACCESS_KEY=your-secret-access-key
BEDROCK_AWS_REGION=us-east-1
OPENWIKI_MODEL_ID=anthropic.claude-sonnet-5
```

명시적 Bedrock credential이 없으면 OpenWiki는 AWS SDK default credential provider chain(OIDC/web identity, IAM role, AWS profile, ECS/EC2)을 사용합니다. region은 `BEDROCK_AWS_REGION`, `AWS_REGION`, `AWS_DEFAULT_REGION`에서 resolve됩니다. 사용 가능한 model ID는 account와 region에서 enable한 foundation model에 따라 다르므로 preset list가 없습니다. Bedrock model ID를 직접 붙여 넣으세요.

새로운 model 중 일부는 cross-region inference profile을 통한 on-demand invocation만 허용합니다. `ValidationException: Invocation of model ID ... with on-demand throughput isn't supported`가 보이면 model ID 앞에 profile region code(예: `us.anthropic.claude-sonnet-5`)를 붙입니다. IAM policy에는 `foundation-model`, `inference-profile` resource type 모두에 대한 `bedrock:InvokeModel` / `InvokeModelWithResponseStream`도 필요합니다.

</details>

<details>
<summary><b>Gemini (AI Studio)와 Gemini Enterprise (Vertex AI)</b></summary>

<br/>

**Gemini (AI Studio)**는 하나의 API key로 Google Gemini model을 실행합니다.

```bash
OPENWIKI_PROVIDER=gemini
GEMINI_API_KEY=your-ai-studio-key
```

**Gemini Enterprise**는 Gemini Enterprise Model Garden(이전 Vertex AI)의 model, 즉 Google Gemini/Gemma, Anthropic Claude, partner/open-weight model(Llama, Mistral, DeepSeek, Qwen)을 실행합니다. 각 model ID를 올바른 API surface로 자동 route하고 API key를 사용하지 않습니다. 인증은 Google Application Default Credentials(ADC)로 합니다.

- `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`을 통한 service account key file,
- `gcloud auth application-default login`의 user credential 또는
- Google Cloud/CI에서 실행할 때 workload identity.

```bash
OPENWIKI_PROVIDER=gemini-enterprise
GOOGLE_CLOUD_PROJECT=your-gcp-project
GOOGLE_CLOUD_LOCATION=global   # 선택 사항, 기본값 global
```

`OPENWIKI_MODEL_ID`에는 어떤 Model Garden model이든 설정합니다. Gemini와 Claude는 preset으로 제공하고 partner model은 ID(예: `publishers/meta/models/llama-3.3-70b-instruct-maas`)를 붙여 넣어 연결합니다. credential에는 Vertex AI access(`roles/aiplatform.user`)가 필요하고 model은 Model Garden에서 enable되어야 합니다. `global` endpoint는 Gemini와 Claude에 가장 좋은 availability를 제공하며, data residency에는 regional endpoint를 지정하고 region-specific partner(MaaS) model에는 항상 명시합니다.

CI에서는 update job 전에 인증하고(예: [`google-github-actions/auth`](https://github.com/google-github-actions/auth)), job environment에 `OPENWIKI_PROVIDER=gemini-enterprise`, `GOOGLE_CLOUD_PROJECT`를 설정합니다.

</details>

<details>
<summary><b>OpenAI (ChatGPT login)</b></summary>

<br/>

`openai-chatgpt` provider는 metered API key 대신 ChatGPT subscription을 통해 OpenAI Codex backend를 호출하며 Plus/Pro/Team plan에 포함된 Codex usage를 사용합니다. `openai` provider와 같은 model list를 제공합니다.

```bash
OPENWIKI_PROVIDER=openai-chatgpt openwiki code --init
# 또는
OPENWIKI_PROVIDER=openai-chatgpt openwiki personal --init
```

wizard는 browser에서 `https://auth.openai.com`을 열고(headless/SSH 사용을 위해 URL도 출력), sign in 뒤 OAuth callback을 잡아 signed-in email과 plan을 보여 준 후 model selection을 계속합니다. access token, refresh token, expiry, account id, email, plan을 `~/.openwiki/.env`에 저장합니다. 이 값은 자동 관리되고 access token도 자동 refresh되므로 보통 직접 편집하지 않습니다. refresh token은 password처럼 다루세요.

</details>

<details>
<summary><b>OpenAI-compatible endpoint (LiteLLM, Ollama, LM Studio, gateway)</b></summary>

<br/>

`openai-compatible` provider는 필수 base URL을 통해 모든 OpenAI-compatible chat-completions endpoint를 target으로 합니다. model ID에는 endpoint가 노출하는 값을 설정합니다.

```bash
# Hosted gateway (예: 여러 upstream provider를 앞단에 둔 Requesty)
OPENWIKI_PROVIDER=openai-compatible
OPENAI_COMPATIBLE_API_KEY=your-gateway-key
OPENAI_COMPATIBLE_BASE_URL=https://router.requesty.ai/v1
OPENWIKI_MODEL_ID=openai/gpt-5.5
```

```bash
# `ollama serve` 및 `ollama pull llama3.2` 뒤의 Ollama
OPENWIKI_PROVIDER=openai-compatible
OPENAI_COMPATIBLE_API_KEY=ollama
OPENAI_COMPATIBLE_BASE_URL=http://localhost:11434/v1
OPENWIKI_MODEL_ID=llama3.2
```

```bash
# Developer tab에서 local server를 시작한 뒤의 LM Studio
OPENWIKI_PROVIDER=openai-compatible
OPENAI_COMPATIBLE_API_KEY=lm-studio
OPENAI_COMPATIBLE_BASE_URL=http://localhost:1234/v1
OPENWIKI_MODEL_ID=your-loaded-model-id
```

일부 local server는 API key 값을 무시하지만 client가 key를 기대하므로 OpenWiki에는 여전히 `OPENAI_COMPATIBLE_API_KEY`가 필요합니다.

**Streaming-only gateway.** 일부 gateway는 streaming transport만 제공하여 non-streaming request를 즉시 거절(`Stream must be set to true`)하거나 HTTP 200과 empty content를 반환합니다. 이는 blank wiki를 error 없이 남깁니다. OpenWiki는 내부적으로 non-streaming request를 내므로 해당 endpoint에는 streaming transport를 강제합니다.

```bash
OPENWIKI_OPENAI_COMPATIBLE_STREAMING=true
```

이 provider가 임의의 third-party endpoint를 가리키고 SSE가 proxy/load balancer를 통과한다는 보장이 없으므로 기본값은 off입니다. 이를 켜면 client는 server-reported token count 대신 estimated token count도 보고합니다.

</details>

<details>
<summary><b>대체 base URL, OpenRouter pinning, retry</b></summary>

<br/>

**대체 base URL.** key와 함께 base URL을 설정해 self-hosted 또는 proxied gateway로 provider를 route할 수 있습니다: `ANTHROPIC_BASE_URL`, `OPENAI_BASE_URL`, `BASETEN_BASE_URL`, `FIREWORKS_BASE_URL`, `NVIDIA_BASE_URL`, `COPILOT_BASE_URL`. `openai` provider는 Responses API(`/v1/responses`)로 tool call을 route하므로 이를 노출하는 gateway에 유용합니다.

```bash
OPENWIKI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key
ANTHROPIC_BASE_URL=https://your-gateway.example.com/anthropic
```

**OpenRouter provider pinning.** OpenRouter가 여러 upstream으로 model을 제공하면 provider 또는 comma-separated allowlist로 routing을 제한합니다.

```bash
OPENWIKI_PROVIDER=openrouter
OPENROUTER_API_KEY=your-key
OPENWIKI_OPENROUTER_PROVIDER_ONLY=Novita
```

**Output-token limit.** OpenWiki는 최신 Claude 4/5 model에 request당 16,384 token 기본값을 씁니다. 이전 LangChain model metadata가 최신 Claude alias를 4,096 token으로 제한할 수 있기 때문입니다. 현재 선택 model에는 provider-neutral limit을 설정할 수 있습니다.

```bash
OPENWIKI_MAX_OUTPUT_TOKENS=16384
```

OpenWiki는 이 설정을 선택한 provider의 request shape로 mapping합니다. custom model은 지원 output window를 OpenWiki가 알 수 없으므로 provider 또는 SDK 기본값을 유지합니다.

**OpenRouter output-token cap.** 기본값은 `max_tokens`를 보내지 않으므로 OpenRouter credit pre-check가 model의 전체 advertised output ceiling 기준으로 예산을 잡습니다. 낮은 credit balance에서는 모든 request가 402 error로 실패할 수 있습니다. 기존 설치는 다음 OpenRouter-specific cap을 유지할 수 있습니다.

```bash
OPENWIKI_OPENROUTER_MAX_TOKENS=8192
```

OpenRouter에서는 이 설정이 `OPENWIKI_MAX_OUTPUT_TOKENS`보다 우선합니다. cap은 hard 402 failure를 긴 wiki generation이 실제로 더 긴 output을 필요로 할 때의 possible truncation과 맞바꾸므로, 잔액이 허용하는 가장 큰 값을 권합니다.

**Retry attempt.** OpenWiki는 transient provider error에 LangChain retry handling을 사용합니다. retry count(기본값 3)는 positive integer `OPENWIKI_PROVIDER_RETRY_ATTEMPTS=3`로 override합니다.

**Bedrock stream idle timeout.** Bedrock provider에는 첫 streamed response chunk 또는 다음 chunk를 기다리는 시간을 설정하는 `OPENWIKI_STREAM_IDLE_TIMEOUT`을 사용합니다. 예: `OPENWIKI_STREAM_IDLE_TIMEOUT=300000`. 값은 millisecond이며 `0`부터 `2147483647` 사이의 integer여야 합니다. `0`이면 watchdog를 끕니다. 설정하지 않으면 `@langchain/aws` provider 기본값을 유지합니다. stalled stream이 무기한 hang하지 않도록 watchdog을 끄기보다 충분히 긴 finite timeout을 권합니다.

**Reasoning effort.** 지원 provider/model의 reasoning은 `OPENWIKI_REASONING_EFFORT`로 구성합니다. OpenAI GPT-5.6 model은 Responses API 값 `none`, `low`, `medium`, `high`, `xhigh`, `max`를 사용합니다. NVIDIA NIM의 Nemotron 3 Super는 `none`, `low`, `high`를 지원합니다. interactive chat에서는 `/effort`로 사용 가능한 값을 고르거나 `/effort default`로 provider 기본값으로 되돌립니다. provider, model, effort 조합이 유효하지 않으면 request를 보내기 전에 실패합니다.

</details>

> [!NOTE]
> 추가되었으면 하는 inference provider 또는 model이 있으면 PR을 열어 주세요.

## Path 무시

repository root에 `.openwikiignore` file을 만들어 생성 문서가 private, generated, irrelevant path를 읽거나 설명하지 않게 할 수 있습니다. 문법은 comment, blank line, `*`/`**` glob, directory rule, `!` negation을 지원합니다.

```gitignore
secrets/
*.log
!logs/keep.log
```

`.openwikiignore`에 active rule이 있으면 OpenWiki는 filesystem discovery를 filter하고 shell execute를 제한해 ignored path가 run에서 제외되게 합니다. 이는 read boundary입니다. ignored path는 문서에서 읽거나 scan하거나 재현하지 않습니다. 그러나 agent가 test, README, commit message처럼 허용된 다른 evidence에서 ignored area를 추론할 수 있으므로 어떤 topic도 절대 언급되지 않는다는 보장은 아닙니다.

## Command reference

```sh
openwiki                         # interactive chat, code mode, current repo
openwiki personal                # interactive chat, personal brain
openwiki "generate docs"         # initial request와 함께 시작
openwiki -p "what can you do?"   # one-shot으로 print하고 종료
openwiki --init                  # code docs 초기화 (personal: openwiki personal --init)
openwiki --update                # code docs 갱신 (personal: openwiki personal --update)
openwiki visualize               # interactive graph + live reader
openwiki visualize openwiki --export docs/openwiki-visualizer  # static graph + reader
openwiki auth <provider>         # connector 인증 (slack, gmail, x, notion)
openwiki ingest <source>         # connector ingestion 실행 (all 또는 connector/instance)
openwiki integrations list       # 설치된 coding-agent integration 표시
openwiki integrations install <codex|claude> [--project [path]]
openwiki integrations uninstall <codex|claude> [--project [path]]
openwiki --help                  # 전체 도움말
```

chat에서 `/api-key`는 masked prompt로 현재 provider key를 갱신하고, `/langsmith-key`는 LangSmith tracing credential을 갱신하거나 지웁니다.

## Telemetry

OpenWiki는 tool 사용 방식을 이해하고 개선하려 익명 aggregate usage data를 수집합니다. telemetry는 기본적으로 켜져 있고 끄기 쉽습니다.

random install ID(`~/.openwiki/install-id`)로 key된 단일 `openwiki_run` event에 **수집하는 것**은 command(init/update), outcome(success/failure/no-op)와 failure 시 coarse error category(메시지는 절대 수집하지 않음), 그리고 setup 시 brain mode·model provider·configured connector name입니다.

**절대 수집하지 않는 것:** file content, repository data/name, credential, prompt, model output, connector payload, error message, file path, URL, model ID, run duration, IP address. interactive chat, `auth`, `ingest`도 기록하지 않습니다. scheduled/CI run은 shared CI identifier 아래 익명 reliability data로 tag되며 install로 세지지 않습니다.

다음 environment variable 중 하나로 opt out하거나, 영구 비활성화를 위해 `~/.openwiki/.env` 첫 줄에 추가합니다.

```sh
export OPENWIKI_TELEMETRY_DISABLED=1
export DO_NOT_TRACK=1   # cross-tool standard
```

run이 무엇을 보낼지 정확히 보려면 모든 run에 `--telemetry-file=<path>`를 추가합니다.

## 기여

기여를 환영합니다. PR을 열기 전에 [CONTRIBUTING.md](./CONTRIBUTING.md)를 읽어 주세요. 의도적으로 PR 하나를 변경 하나에만 좁게 유지하며, 관련 없는 변경을 묶은 PR에는 분리 요청과 함께 close될 수 있습니다.

## License

[MIT](./LICENSE)
