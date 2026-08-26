# 빠른 시작

<p align="center"><b>English</b> · <a href="docs/i18n/QUICKSTART.pt-BR.md">Português (Brasil)</a> · <a href="docs/i18n/QUICKSTART.de.md">Deutsch</a> · <a href="docs/i18n/QUICKSTART.fr.md">Français</a> · <a href="docs/i18n/QUICKSTART.ja-JP.md">日本語</a> · <a href="docs/i18n/QUICKSTART.ko.md">한국어</a> · <a href="docs/i18n/QUICKSTART.zh-CN.md">简体中文</a> · <a href="docs/i18n/QUICKSTART.zh-TW.md">繁體中文</a> · <a href="docs/i18n/QUICKSTART.th.md">ภาษาไทย</a></p>

전체 제품을 로컬에서 실행합니다.

## 환경 요구사항

- **Node.js:** `~24` (Node 24.x). 이 저장소는 `package.json#engines`로 이를 강제합니다.
- **pnpm:** `10.33.x`. 저장소는 `packageManager`로 `pnpm@10.33.2`를 고정합니다. Corepack을 사용하면 고정된 버전이 자동 선택됩니다.
- **OS:** macOS, Linux, WSL2가 주 경로입니다. agent CLI가 WSL2에서 실행된다면 [`WSL2 setup guide`](docs/wsl-setup.md)를 사용하세요. Windows native도 지원합니다. PowerShell 설정의 흔한 문제는 [`docs/windows-troubleshooting.md`](docs/windows-troubleshooting.md)를 보세요.
- **선택 사항인 로컬 agent CLI:** OpenDesign은 Claude Code, Codex, Devin for Terminal, OpenCode, Cursor Agent, Qwen, Qoder CLI, GitHub Copilot CLI 등을 포함한 local runtime registry를 지원합니다. 현재 목록은 [`apps/daemon/src/runtimes/registry.ts`](apps/daemon/src/runtimes/registry.ts)에 있습니다. 설치된 CLI가 없다면 Settings에서 BYOK runtime을 사용하세요.

### 로컬 agent CLI와 PATH

daemon은 **`PATH`**(및 흔한 사용자 toolchain directory)를 스캔합니다. **`npm install -g`**나 Homebrew로 CLI를 설치했는데 OpenDesign이 *not installed*로 표시하면, GUI가 global npm 또는 Homebrew `bin` directory가 없는 최소 `PATH`로 시작했을 수 있습니다. 이는 전체 login shell에서 시작하지 않는 macOS 앱에서 흔합니다. daemon을 실행하는 process의 `PATH`에 실행 파일 directory가 있는지 확인한 뒤 **Settings → Execution mode**에서 **Rescan**을 사용하세요.

[`nvm`](https://github.com/nvm-sh/nvm) / [`fnm`](https://github.com/Schniz/fnm)은 필수가 아니라 편의 도구입니다. 사용한다면 pnpm 실행 전에 Node 24를 설치/선택하세요.

```bash
# nvm
nvm install 24
nvm use 24

# fnm
fnm install 24
fnm use 24
```

그다음 Corepack을 활성화하여 저장소가 pnpm을 선택하도록 합니다.

```bash
corepack enable
corepack pnpm --version   # 10.33.2가 출력되어야 함
```

## Docker 설정

Node.js나 pnpm을 로컬에 설치하지 않고도 완전히 containerized된 환경에서 OpenDesign을 실행합니다.

### 요구사항

* Docker Desktop
* Docker Compose v2

Docker가 올바르게 설치됐는지 확인합니다.

```bash
docker compose version
```

---

## OpenDesign 시작

저장소 root에서 다음을 실행합니다.

1. deploy directory로 이동하여 environment template을 복사합니다.

   ```bash
   cd deploy
   cp .env.example .env
   ```

2. 보안 token을 생성합니다.

   ```bash
   openssl rand -hex 32
   ```

3. 편집기에서 `.env`를 열고 `OD_API_TOKEN=`을 찾아 생성한 token을 붙여 넣습니다.

그런 다음 서비스를 시작합니다.

```bash
docker compose up -d
```

브라우저에서 앱을 엽니다.

```text
http://localhost:7456
```

Docker가 최신 image를 내려받는 동안 첫 시작에는 몇 초가 걸릴 수 있습니다.

---

## 자주 쓰는 Docker 명령

### 로그 보기

```bash
docker compose logs -f
```

### container 재시작

```bash
docker compose restart
```

### container 중지

```bash
docker compose down
```

### 최신 image 받기

```bash
docker compose pull
docker compose up -d
```

### 모든 로컬 앱 데이터 제거

```bash
docker compose down -v
```

---

## 환경 설정

기본 설정을 재정의하려면 `deploy/.env` 파일을 만듭니다. 제공된 예시에서 시작하세요.

```bash
cp deploy/.env.example deploy/.env
```

`deploy/.env`를 편집해 token을 설정하고 필요에 따라 다른 값을 조정합니다.

```env
# Host에 노출할 포트
OPEN_DESIGN_PORT=7456

# Container 메모리 제한
OPEN_DESIGN_MEM_LIMIT=384m

# 허용할 CORS origin
OPEN_DESIGN_ALLOWED_ORIGINS=https://yourdomain.com

# Docker image tag
OPEN_DESIGN_IMAGE=ghcr.io/nexu-io/od:latest

# daemon 보안에 필요한 API token
# 다음으로 생성: openssl rand -hex 32
OD_API_TOKEN=
```

---

## 영속 저장소

persistent daemon storage path를 문서화·변경·선택하기 전에 root `AGENTS.md`의 **Daemon data directory contract** section을 반드시 읽어야 합니다. 이 Quickstart는 해당 contract를 다시 서술하거나 storage path를 정의해서는 안 됩니다.

---

## 참고

* Docker mode는 local Node.js 또는 pnpm setup을 원하지 않는 contributor에게 적합합니다.
* container는 production daemon build를 port `7456`에서 직접 노출합니다.
* 개발 workflow와 고급 local setup은 이 Quickstart의 나머지 section을 보세요.

---

## One-shot (dev mode)

```bash
corepack enable
pnpm install
pnpm tools-dev run web # daemon + web을 foreground에서 시작
# tools-dev가 출력한 web URL 열기
```

desktop shell과 모든 managed sidecar를 background에서 시작하려면 다음을 사용합니다.

```bash
pnpm tools-dev # daemon + web + desktop을 background에서 시작
```

첫 load에서 앱은 사용 가능한 local runtime을 탐지하고 Settings에서 설정한 BYOK runtime도 제공합니다. runtime, design template, design system을 고른 뒤 prompt를 입력하고 **Send**를 누릅니다. Structured local runtime은 canonical project file을 쓰고 file/tool event를 stream하며, file workspace와 preview는 이 write로 갱신됩니다. Plain text-only와 BYOK run은 host가 parse할 complete `<artifact>` block을 대신 반환합니다. artifact storage path를 문서화하거나 변경하기 전에는 `AGENTS.md` → **Daemon data directory contract**를 반드시 읽어야 합니다.

**Design systems** catalog는 [`design-systems/`](design-systems/)의 `DESIGN.md` package에서 load됩니다. 하나를 고르면 해당 brand의 visual language가 artifact에 적용됩니다.

**Templates** catalog는 [`design-templates/`](design-templates/)에서 오며 prototype, deck, document, image, video, audio용 artifact format을 묶습니다. [`skills/`](skills/)는 agent가 작업 중 호출하는 functional capability를 위해 예약돼 있습니다. template과 design system을 조합해 선택한 visual language의 artifact를 만드세요.

## 다른 script

```bash
pnpm tools-dev                 # daemon + web + desktop을 background에서 시작
pnpm tools-dev start web       # daemon + web을 background에서 시작
pnpm tools-dev run web         # daemon + web을 foreground에서 시작(e2e/dev server)
pnpm tools-dev restart         # daemon + web + desktop 재시작
pnpm tools-dev restart --daemon-port 7457 --web-port 5175
pnpm tools-dev status          # managed runtime 점검
pnpm tools-dev logs            # daemon/web/desktop log 보기
pnpm tools-dev check           # status + 최근 log + 일반 diagnostics
pnpm tools-dev stop            # managed runtime 중지
pnpm --filter @open-design/daemon build  # `od`용 apps/daemon/dist/cli.js build
pnpm --filter @open-design/web build     # 필요할 때 web package build
pnpm typecheck                 # workspace typecheck
```

`pnpm tools-dev`가 유일한 local lifecycle entry point입니다. 제거된 legacy root alias(`pnpm dev`, `pnpm dev:all`, `pnpm daemon`, `pnpm preview`, `pnpm start`)를 사용하지 마세요.

`tools-dev`는 port, namespace, child process environment를 해석하기 전에 workspace env file을 자동 load합니다. 기본 우선순위는 `.env.development.local`, `.env.local`, `.env.development`, `.env`입니다. env file이 ambient shell export를 덮어써 project-local config가 우선합니다. load를 끄려면 `--no-env-file`, 명시적 file을 쓰려면 `--env-file <path>`를 반복 사용하세요.

local development에서는 `tools-dev`가 daemon을 먼저 시작하고 그 port를 `apps/web`에 전달합니다. `apps/web/next.config.ts`는 `/api/*`, `/artifacts/*`, `/frames/*`를 해당 daemon port로 rewrite하므로 App Router 앱은 CORS setup 없이 sibling Express process와 통신합니다.

## Media generation / agent dispatcher 점검

image, video, audio, HyperFrames skill은 daemon이 agent를 spawn할 때 주입하는 environment variable을 통해 local `od` CLI를 호출합니다.

- `OD_BIN` — `apps/daemon/dist/cli.js`의 절대 경로
- `OD_DAEMON_URL` — 실행 중인 daemon URL
- `OD_PROJECT_ID` — active project ID
- `OD_PROJECT_DIR` — active project의 file directory

media generation이 `OD_BIN: parameter not set`, `apps/daemon/dist/cli.js` 누락, 또는 `failed to reach daemon at http://127.0.0.1:0`로 실패하면 daemon CLI를 다시 build하고 managed runtime을 재시작합니다.

```bash
pnpm --filter @open-design/daemon build
pnpm tools-dev restart --daemon-port 7457 --web-port 5175
ls -la apps/daemon/dist/cli.js
curl -s http://127.0.0.1:7457/api/health
```

그다음 이전 terminal agent session을 resume하지 말고 OpenDesign 앱에서 project를 다시 여세요. daemon이 spawn한 agent에는 다음과 같은 값이 보여야 합니다.

```bash
echo "OD_BIN=$OD_BIN"
echo "OD_PROJECT_ID=$OD_PROJECT_ID"
echo "OD_PROJECT_DIR=$OD_PROJECT_DIR"
echo "OD_DAEMON_URL=$OD_DAEMON_URL"
ls -la "$OD_BIN"
```

`OD_DAEMON_URL`은 `http://127.0.0.1:7457`처럼 실제 daemon port여야 하며 `http://127.0.0.1:0`이면 안 됩니다. `:0`은 내부의 “available port 선택” launch hint일 뿐 agent session으로 유출되면 안 됩니다.

daemon-only production mode에서는 daemon이 static Next.js export를 `http://localhost:7456`에서 직접 제공하므로 reverse proxy가 없습니다.

nginx를 daemon 앞에 둔다면 SSE route를 unbuffered·uncompressed로 유지하세요. daemon이 `X-Accel-Buffering: no`를 보내도 nginx `gzip on`이 chunked SSE response를 buffer하면 80–90초 뒤 browser console에 `net::ERR_INCOMPLETE_CHUNKED_ENCODING 200 (OK)`가 나타나는 일이 흔합니다.

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:7456;

    proxy_buffering off;
    gzip off;

    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
    proxy_http_version 1.1;
    proxy_set_header Connection "";

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 두 execution mode

| Mode | Picker value | 요청 흐름 |
|---|---|---|
| **Local CLI** (daemon이 agent를 찾으면 기본값) | "Local CLI" | Frontend → daemon `/api/chat` → `spawn(<agent>, ...)` → SSE의 structured tool/file event → project file → preview. Plain-stream CLI는 text-artifact path를 대신 사용합니다. |
| **API mode** (fallback / CLI 없음) | "Anthropic API" / "OpenAI API" / "Atlas Cloud" / "Azure OpenAI" / "Google Gemini" | Frontend → daemon `/api/proxy/{provider}/stream` → provider SSE를 `delta/end/error`로 normalize → `<artifact>` parser → preview |

두 mode는 같은 file workspace와 sandboxed preview로 끝나지만 handoff contract는 다릅니다. Filesystem-capable runtime은 canonical file을 쓰며 `<artifact>` 안에 source를 echo해서는 안 됩니다. Plain/text-only와 BYOK run에는 file tool이 없으므로 canonical deliverable은 `<artifact>` 안의 complete HTML입니다. execution profile은 runtime transport에서 선택되며, local CLI는 runtime definition에 선언된 invocation shape로 composed prompt를 전달받습니다.

## Prompt composition

모든 send에서 앱은 세 layer의 system prompt를 만들어 provider에 보냅니다.

```text
BASE_SYSTEM_PROMPT   (execution-profile-specific file 또는 <artifact> handoff)
   + active design system body  (DESIGN.md — palette/type/layout)
   + active skill body          (SKILL.md — workflow 및 output rule)
```

top bar에서 skill 또는 design system을 바꾸면 다음 send가 새 stack을 사용합니다. body는 session별 in-memory cache에 있어 picker 하나당 daemon fetch는 한 번입니다.

## File map

```text
open-design/
├── apps/
│   ├── daemon/                # Node/Express — local agent를 spawn하고 API 제공
│   │   └── src/
│   │       ├── cli.ts             # `od` bin entry
│   │       ├── server.ts          # /api/* + static serving
│   │       ├── agents.ts          # runtime module의 compatibility export
│   │       ├── runtimes/
│   │       │   ├── registry.ts    # 지원 runtime registry
│   │       │   └── defs/          # runtime별 launch 및 argument definition
│   │       ├── skills.ts          # SKILL.md loader(frontmatter parser)
│   │       │   └── design-systems/ # DESIGN.md loader와 service
│   │   ├── sidecar/           # tools-dev daemon sidecar wrapper
│   │   └── tests/             # daemon package test
│   ├── web/                   # Next.js 16 App Router + React client
│   │   ├── app/               # App Router entrypoint
│   │   ├── src/               # React + TypeScript client/runtime module
│   │   │   ├── App.tsx        # mode / skill / DS picker + send orchestration
│   │   │   ├── providers/     # daemon + BYOK API transport
│   │   │   ├── prompts/       # system, discovery, directions, deck framework
│   │   │   ├── artifacts/     # text-artifact parsing + artifact manifest
│   │   │   ├── runtime/       # iframe srcdoc, markdown, export helper
│   │   │   └── state/         # localStorage + daemon-backed project state
│   │   ├── sidecar/           # tools-dev web sidecar wrapper
│   │   └── next.config.ts     # tools-dev rewrite + prod apps/web/out export config
│   └── desktop/               # Electron runtime, tools-dev가 launch/inspect
├── packages/
│   ├── contracts/             # shared web/daemon app contract
│   ├── sidecar-proto/         # OpenDesign sidecar protocol contract
│   ├── sidecar/               # generic sidecar runtime primitive
│   └── platform/              # generic process/platform primitive
├── tools/dev/                 # `pnpm tools-dev` lifecycle 및 inspect CLI
├── e2e/                       # Playwright UI + external integration/Vitest harness
├── skills/                    # mid-task에 호출되는 functional capability
├── design-templates/          # prototype, deck, doc, media의 rendering catalog
├── design-systems/            # DESIGN.md를 root로 하는 brand package
├── scripts/sync-design-systems.ts    # upstream getdesign tarball 재import
├── docs/                      # product vision + spec
├── pnpm-workspace.yaml        # apps/* + packages/* + tools/* + e2e
└── package.json               # root quality script + `od` bin
```

## 문제 해결

- **Node.js version 변경 뒤 `better-sqlite3` load 실패 / ABI mismatch** — `pnpm install`은 `postinstall`을 다시 실행하고 current Node용 native addon을 rebuild합니다. 수동 rebuild/검증은 `pnpm --filter @open-design/daemon rebuild better-sqlite3`, 이어서 `pnpm --filter @open-design/daemon exec node -e "require('better-sqlite3')"`를 사용합니다. `python3`, `make`, `g++`(또는 `clang++`) build tool이 필요합니다. `.npmrc`에서 `ignore-scripts=true`를 쓴다면 `pnpm install` 뒤 `pnpm bootstrap`을 실행하세요.
- **"no agents found on PATH"** — [`apps/daemon/src/runtimes/registry.ts`](apps/daemon/src/runtimes/registry.ts)에 등록된 local runtime 중 하나를 설치하고 daemon에서 executable이 보이게 한 뒤 **Settings → Execution mode**에서 **Rescan**하세요. 또는 Settings에서 BYOK runtime을 설정하세요.
- **Claude Code가 code 1로 종료** — OpenDesign이 `claude` 시작에는 성공했지만 non-interactive run이 response 전 실패했습니다. OpenDesign을 시작하는 동일 shell/app environment에서 다음을 확인하세요.
  ```bash
  claude --version
  claude auth status --text
  printf 'hello' | claude -p --output-format stream-json --verbose --permission-mode bypassPermissions
  ```
  smoke test가 `401`, `apiKeySource: "none"`, custom endpoint 없는 다른 auth error를 보이면 `claude`를 실행해 `/login` 후 종료하고 OpenDesign을 재시도하세요. 여러 Claude profile을 쓴다면 **Settings -> Execution mode -> Claude Code config directory**를 `~/.claude-2` 같은 profile path로 설정합니다. `ANTHROPIC_BASE_URL` 또는 proxy가 있다면 endpoint URL, proxy credential, endpoint auth environment, model access를 확인하세요. standard Claude Code auth로 재시도하려는 경우에만 custom endpoint를 제거합니다. Windows native PowerShell과 WSL은 별도 Claude 설치·credential store를 쓰므로 OpenDesign이 쓰는 동일 environment에서 다시 authenticate하고, native Windows `/login`이 복구하지 않으면 Windows Credential Manager를 확인하세요.
- **`/api/chat`에서 daemon 500** — daemon terminal의 stderr tail을 확인하세요. 보통 CLI가 argument를 거부한 경우입니다. CLI마다 argv shape가 다르므로 맞는 `apps/daemon/src/runtimes/defs/` definition을 점검하세요.
- **media generation에서 `OD_BIN` 누락 또는 daemon URL이 `:0`** — 위 media dispatcher check를 실행하세요. 이전 CLI session을 resume하지 말고 OpenDesign app에서 project를 다시 열어 daemon이 새 `OD_*` variable을 주입하게 하세요.
- **Codex가 너무 많은 plugin context를 load** — `OD_CODEX_DISABLE_PLUGINS=1 pnpm tools-dev`로 OpenDesign을 시작하면 daemon-spawned Codex process가 `--disable plugins`로 실행됩니다.
- **artifact가 render되지 않음** — 먼저 run의 handoff profile을 식별하세요. filesystem-capable local runtime이면 agent가 previewable project file을 만들고 file-write event가 daemon에 도달했는지 확인합니다. 이 runtime은 source를 `<artifact>`로 내보내면 안 됩니다. plain/text-only 또는 BYOK run이면 response에 complete `<artifact>` block 하나가 있는지 확인하세요. filesystem runtime에게 inline source로 fallback하라고 하기보다 daemon log에서 첫 failed boundary를 확인합니다.
- **macOS에서 `Authorization: Bearer <OD_API_TOKEN>` 필요** — Docker Desktop bridge networking은 daemon이 request를 non-loopback으로 보게 합니다. Docker Desktop에서 host networking을 활성화하고 `network_mode: host`를 사용하세요. [`deploy/README.md` — Docker Desktop on macOS](deploy/README.md#docker-desktop-on-macos)를 보세요.

## vision으로 다시 연결

이 Quickstart는 [`docs/`](docs/)의 spec을 실행할 수 있게 만든 seed입니다. spec은 확장 방향을 설명합니다([`docs/roadmap.md`](docs/roadmap.md) 참고). 핵심은 다음과 같습니다.

- `docs/architecture.md`는 shipped stack을 설명합니다. 앞에는 Next.js 16 App Router, 뒤에는 local daemon이 있으며, dev에서는 `apps/web/next.config.ts` rewrite로 browser가 같은 `/api` surface와 통신합니다.
- `docs/skills-protocol.md`는 현재 `SKILL.md`/`od:` frontmatter와 functional skill·rendering template의 분리를 설명합니다. parser/normalization의 source of truth는 `apps/daemon/src/skills.ts`입니다.
- `docs/agent-adapters.md`는 adapter contract를 설명합니다. runtime별 launch, argument, model, stream setting은 `apps/daemon/src/runtimes/defs/`, registration은 `apps/daemon/src/runtimes/registry.ts`에 있고 `apps/daemon/src/agents.ts`는 compatibility export surface입니다.
- `docs/modes.md`는 six New Project tab과 seven normalized registry mode(`prototype`, `deck`, `template`, `design-system`, `image`, `video`, `audio`)의 차이를 설명합니다.

> 번역 범위: 고정 SHA의 `QUICKSTART.md:1-357`을 구조 보존해 번역했다. 명령·파일 경로·식별자·URL은 원문 그대로 유지했다. 실행하거나 설정을 변경한 문서는 아니다. [S4]
