# Impeccable

AI 코딩 에이전트를 위한 디자인 가이드입니다. AI가 생성한 프론트엔드 디자인을 위해 1개 skill, 23개 명령, live browser iteration, 59개의 결정론적 detector rule을 제공합니다.

> **빠른 시작:** 프로젝트 root에서 `npx impeccable install`을 실행한 다음, AI 코딩 도구 안에서 `/impeccable init`을 실행하세요. 전체 문서: [impeccable.style](https://impeccable.style).

## Impeccable을 쓰는 이유

Anthropic의 [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design)은 Claude를 위한 최초의 널리 쓰인 디자인 skill이었습니다. Impeccable은 여기서 출발했습니다.

모든 모델은 같은 SaaS template으로 학습됩니다. 가이드를 건너뛰면 매 프로젝트마다 같은 몇 가지 흔적이 나옵니다. 모든 곳에 Inter, 보라색에서 파란색으로 가는 gradient, card 안의 card, 색 배경 위의 회색 텍스트, 모든 제목 위의 둥근 사각형 icon tile입니다.

Impeccable은 다음을 더합니다.

- **하나의 setup flow.** `/impeccable init`이 `PRODUCT.md`를 작성하고 `DESIGN.md`를 제안하므로, 이후 명령은 audience, brand/product lane, voice, anti-reference, color, type, component를 알 수 있습니다.
- **23개 명령.** AI와 공유하는 디자인 vocabulary입니다. `polish`, `audit`, `critique`, `distill`, `animate`, `bolder`, `quieter` 등이 있습니다.
- **59개의 결정론적 detector rule**과 LLM 전용 critique check. CLI와 browser extension은 LLM이나 API key 없이 결정론적 rule을 실행합니다.

## 포함 항목

### Skill: impeccable

skill은 한 명령으로 설치됩니다.

```bash
/impeccable <command> <target>
```

모든 새 프로젝트는 다음으로 시작하세요.

```bash
/impeccable init
```

`init`은 surface가 brand(마케팅, landing, portfolio)인지 product(app UI, dashboard, tool)인지 묻고, 이후 모든 명령이 읽을 디자인 context를 작성합니다.

### 23개 명령

모든 명령은 `/impeccable`을 통해 접근합니다.

| 명령 | 하는 일 |
|---------|--------------|
| `/impeccable craft` | visual iteration을 포함한 전체 shape-then-build flow |
| `/impeccable init` | 일회성 setup: design context 수집, PRODUCT.md와 DESIGN.md 작성, live mode 설정, 다음 단계 추천 |
| `/impeccable document` | 기존 프로젝트 코드에서 root DESIGN.md 생성 |
| `/impeccable extract` | 재사용 가능한 component와 token을 design system으로 추출 |
| `/impeccable shape` | 코드 작성 전 UX/UI 계획 |
| `/impeccable critique` | UX 디자인 review: hierarchy, clarity, emotional resonance |
| `/impeccable audit` | 기술 품질 check 실행(a11y, performance, responsive) |
| `/impeccable polish` | 최종 pass, design system 정렬, shipping 준비도 |
| `/impeccable bolder` | 밋밋한 디자인을 더 강하게 만듦 |
| `/impeccable quieter` | 지나치게 강한 디자인의 톤을 낮춤 |
| `/impeccable distill` | 본질만 남김 |
| `/impeccable harden` | error handling, i18n, text overflow, edge case |
| `/impeccable onboard` | 첫 실행 flow, empty state, activation path |
| `/impeccable animate` | 목적 있는 animation과 motion 추가 |
| `/impeccable colorize` | monochromatic UI에 전략적 color 도입 |
| `/impeccable typeset` | font 선택, hierarchy, size 수정 |
| `/impeccable layout` | layout, spacing, visual rhythm 수정 |
| `/impeccable delight` | 즐거운 순간 추가 |
| `/impeccable overdrive` | 기술적으로 특별한 effect 추가 |
| `/impeccable clarify` | 불명확한 UX copy 개선 |
| `/impeccable adapt` | 서로 다른 device에 맞춤 |
| `/impeccable optimize` | performance 개선 |
| `/impeccable live` | visual variant mode: browser에서 element 반복 수정 |

`/impeccable pin <command>`으로 독립 shortcut을 만드세요(예: `pin audit`는 `/audit`를 만듭니다).

#### 사용 예

```
/impeccable audit blog           # blog hub + post page 감사
/impeccable critique landing     # UX 디자인 review
/impeccable polish settings      # shipping 전 최종 pass
/impeccable harden checkout      # error handling + edge case 추가
```

또는 설명과 함께 `/impeccable`을 직접 사용하세요.

```
/impeccable redo this hero section
```

### Anti-pattern

skill에는 피해야 할 항목을 명시적으로 안내합니다.

- 과도하게 쓰인 font(Arial, Inter, system default)를 쓰지 마세요.
- 색 배경 위에 회색 텍스트를 쓰지 마세요.
- 순수 black/gray를 쓰지 마세요(항상 tint를 넣으세요).
- 모든 것을 card로 감싸거나 card 안에 card를 중첩하지 마세요.
- bounce/elastic easing을 쓰지 마세요(낡아 보입니다).

## 실제 동작 보기

Impeccable 명령으로 실제 프로젝트가 바뀐 before/after 사례는 [Neo Mirai case study](https://impeccable.style/cases/neo-mirai)를 방문하세요.

## 설치

### Option 1: CLI installer(권장)

프로젝트 root에서 실행하세요.

```bash
npx impeccable install
```

이 명령은 감지한 harness folder(예: `~/.claude`, `~/.codex`, `~/.grok`, project-local `.cursor`)를 보여주고, 감지 세트를 유지할지 provider를 직접 정할지 묻습니다. 이어서 현재 project 또는 global 중 설치 위치를 묻습니다. script에서 선택을 건너뛰려면 `--providers=claude,codex,cursor,grok`와 `--scope=project|global`을 사용하세요. Claude Code, Cursor, Codex, GitHub Copilot, Grok Build에서는 현재 project의 provider-native hook manifest도 설치합니다. Cursor, Claude Code, Gemini CLI, Codex CLI, Grok Build와 그 밖의 지원 도구에서 동작합니다. 이후 harness를 다시 불러오세요.

기존 설치를 새로 고치려면 다음을 실행하세요.

```bash
npx impeccable update
```

Codex 사용자는 install 또는 update 뒤 `/hooks`를 열고 prompt가 나오면 project hook을 승인해야 합니다. Codex는 hook definition별로 trust를 추적하므로 `.codex/hooks.json`을 바꾸는 update는 다시 승인이 필요할 수 있습니다. Grok Build 사용자는 `.grok/hooks/` script가 실행되기 전에 project folder trust가 필요합니다(`/hooks-trust` 또는 `--trust`로 실행).

### Option 2: Git Submodule

Impeccable을 Git으로 vendoring하고 update하려는 팀은 이 repo를 submodule로 추가하고 compiled provider build를 harness folder에 link하세요.

```bash
git submodule add https://github.com/pbakaus/impeccable .impeccable
npx impeccable link --source=.impeccable --providers=claude,cursor
git add .gitmodules .impeccable .claude .cursor
git commit -m "Add Impeccable skills"
```

프로젝트에 필요한 provider를 쓰세요. 예를 들어 `claude`, `cursor`, `gemini`, `codex`, `github`, `grok`, `opencode`, `pi`, `qoder`, `trae`, `trae-cn`, `rovo-dev`, `vibe`가 있습니다. 이 명령은 `.impeccable/dist/universal/`에서 개별 skill folder를 link하며, `--force`를 주지 않는 한 기존의 실제 skill directory는 건드리지 않습니다.

나중에 update하려면 다음을 실행하세요.

```bash
git submodule update --remote .impeccable
npx impeccable link --source=.impeccable --providers=claude,cursor
```

### Option 3: Plugin install

**Claude Code:**

```bash
/plugin marketplace add pbakaus/impeccable
```

> Claude Code 전용입니다. marketplace를 추가한 뒤 `/plugin`을 열고 목록에서 Impeccable을 설치하세요.

**Grok Build:**

```bash
grok plugin install pbakaus/impeccable#plugin --trust
```

> Grok Build 전용입니다. `#plugin` suffix는 전체 monorepo 대신 slim plugin package(skills, agents, hooks)를 설치합니다. 이어서 Grok session에서 `/impeccable init`을 실행하세요. `npx impeccable install --providers=grok`로 project-scoped 설치도 가능하며 `.grok/skills/`와 `.grok/hooks/impeccable.json`을 작성합니다.

### Option 4: Website에서 다운로드

[impeccable.style](https://impeccable.style)를 방문해 도구용 ZIP을 내려받아 project에 압축을 푸세요.

### Option 5: Repository에서 복사

**Cursor:**

```bash
cp -r dist/cursor/.cursor your-project/
```

> **참고:** Cursor skill에는 setup이 필요합니다.
>
> 1. Cursor Settings → Beta에서 Nightly channel로 전환합니다.
> 2. Cursor Settings → Rules에서 Agent Skills를 활성화합니다.
>
> [Cursor skill 더 알아보기](https://cursor.com/docs/context/skills)

**Claude Code:**

```bash
# Project-specific
cp -r dist/claude-code/.claude your-project/

# 또는 global(모든 project에 적용)
cp -r dist/claude-code/.claude/* ~/.claude/
```

**OpenCode:**

```bash
cp -r dist/opencode/.opencode your-project/
```

**Pi:**

```bash
cp -r dist/pi/.pi your-project/
```

**Gemini CLI:**

```bash
cp -r dist/gemini/.gemini your-project/
```

> **참고:** Gemini CLI skill에는 setup이 필요합니다.
>
> 1. preview version을 설치합니다: `npm i -g @google/gemini-cli@preview`
> 2. `/settings`를 실행하고 "Skills"를 활성화합니다.
> 3. `/skills list`를 실행해 설치를 확인합니다.
>
> [Gemini CLI skill 더 알아보기](https://geminicli.com/docs/cli/skills/)

**Codex CLI:**

```bash
# Project-local
cp -r dist/agents/.agents your-project/
mkdir -p your-project/.codex
cp dist/codex/.codex/hooks.json your-project/.codex/hooks.json

# 또는 skill을 user-wide로 설치합니다. design hook을 실행하려는 각 project에
# .codex/hooks.json을 복사하세요.
mkdir -p ~/.agents/skills
cp -r dist/agents/.agents/skills/* ~/.agents/skills/
```

> asset-producer subagent는 skill 자체의 `agents/` folder 안에 중첩되어 배포되며 Codex가 자동 발견합니다. 별도 `.codex/agents/` 복사본은 필요 없습니다. hook은 trusted project config 옆의 `.codex/hooks.json`에서 Codex가 발견하므로 project-local입니다.

**GitHub Copilot:**

```bash
cp -r dist/github/.github your-project/
```

**Trae:**

```bash
# Trae China (domestic version)
cp -r dist/trae/.trae-cn/skills/* ~/.trae-cn/skills/

# Trae International
cp -r dist/trae/.trae/skills/* ~/.trae/skills/
```

> **참고:** Trae에는 서로 다른 config directory를 쓰는 두 version이 있습니다.
>
> - **Trae China**: `~/.trae-cn/skills/`
> - **Trae International**: `~/.trae/skills/`
>
> 복사한 뒤 Trae IDE를 다시 시작해 skill을 활성화하세요.

**Rovo Dev:**

```bash
# Project-specific
cp -r dist/rovo-dev/.rovodev your-project/

# 또는 global(모든 project에 적용)
cp -r dist/rovo-dev/.rovodev/skills/* ~/.rovodev/skills/
```

**Qoder:**

```bash
# Project-specific
cp -r dist/qoder/.qoder your-project/

# 또는 global(모든 project에 적용)
cp -r dist/qoder/.qoder/skills/* ~/.qoder/skills/
```

**Mistral Vibe:**

```bash
# Project-specific
cp -r dist/vibe/.vibe your-project/

# 또는 global(모든 project에 적용)
cp -r dist/vibe/.vibe/skills/* ~/.vibe/skills/
```

**Grok Build:**

```bash
# Project-specific
cp -r dist/grok/.grok your-project/

# 또는 global(모든 project에 적용)
cp -r dist/grok/.grok/skills/* ~/.grok/skills/
```

> design hook도 함께 설치되도록 `npx impeccable install --providers=grok` 또는 `grok plugin install pbakaus/impeccable#plugin --trust`를 권장합니다. project hook에는 folder마다 한 번 `/hooks-trust`(또는 `--trust`)가 필요합니다.

**Google Antigravity:**

```bash
# Project-specific
cp -r dist/antigravity/.agent your-project/

# 또는 global(모든 project에 적용)
mkdir -p ~/.gemini/config/skills
cp -r dist/antigravity/.agent/skills/* ~/.gemini/config/skills/
```

## 사용법

설치한 뒤 모든 명령은 하나의 `/impeccable` skill을 통해 실행합니다.

```
/impeccable audit        # issue 찾기
/impeccable polish       # 최종 정리
/impeccable distill      # 복잡성 제거
/impeccable critique     # 전체 디자인 review
```

전체 명령 목록을 보려면 `/impeccable`만 입력하세요.

대부분의 명령은 특정 영역에 집중할 optional argument를 받습니다.

```
/impeccable audit the header
/impeccable polish the checkout form
```

어떤 명령을 자주 쓴다면 `/impeccable pin audit`로 고정해 `/audit` standalone shortcut을 만들 수 있습니다.

**참고:** Codex는 여기서 `/prompts:` 명령이 아니라 skill을 씁니다. `/skills`를 열거나 `$impeccable`을 입력하세요. repo-local 설치는 `.agents/skills/`에, user-wide 설치는 `~/.agents/skills/`에 있습니다. GitHub Copilot은 `.github/skills/`를 씁니다. 새로 설치한 skill이 나타나지 않으면 도구를 다시 시작하세요.

## `.impeccable`을 git에서 제외하기

명령을 실행하면 Impeccable은 `.impeccable/` 아래에 critique와 polish screenshot, live-mode session과 preview state, runtime cache, developer별 config 같은 작업 파일을 씁니다. 대부분은 ephemeral이라 commit하면 안 되지만, 일부는 repo에 속하는 shared project artifact입니다. 이 block을 프로젝트의 `.gitignore`에 추가하세요.

```gitignore
# impeccable-ignore-start
# Ephemeral output, runtime state, and per-dev overrides.
# Unanchored: .impeccable may sit at the repo root or under a nested
# workspace (apps/web/.impeccable/...); anchored patterns would miss it.
# Shared artifacts stay tracked: config.json, live/config.json,
# design.json, critique/*.md.
.impeccable/config.local.json
.impeccable/hook.cache.json
.impeccable/hook.pending.json
.impeccable/*.png
.impeccable/live/server.json
.impeccable/live/sessions/
.impeccable/live/previews/
.impeccable/live/annotations/
.impeccable/live/cache/
.impeccable/live/manual-edit-apply-transaction.json
.impeccable/live/manual-edit-events.jsonl
.impeccable/live/manual-edit-evidence/
.impeccable/live/pending-manual-edits.json
.impeccable/live/deferred-svelte-component-accepts.json
.impeccable/live/*.png
# impeccable-ignore-end
```

이 block은 나중에 인식하고 갱신할 수 있게 `# impeccable-ignore-start` / `# impeccable-ignore-end` marker로 감쌌습니다. pattern은 의도적으로 unanchored입니다. monorepo에서는 active project와 그 `.impeccable/` directory가 `apps/web/` 같은 nested workspace 아래에 있을 수 있고, root-anchored pattern은 이를 놓치기 때문입니다.

**다음은 추적 상태로 유지하세요**(shared project artifact이므로 `.gitignore`에 넣지 마세요).

- `.impeccable/config.json` (통합 shared config)
- `.impeccable/live/config.json` (live-mode framework wiring)
- `.impeccable/design.json` (shared design spec)
- `.impeccable/critique/*.md` (review report)

ephemeral file(screenshot, `config.local.json`)가 이 block을 추가하기 전에 commit됐다면 `.gitignore`은 자동으로 untrack하지 않습니다. local copy를 지우지 않고 추적만 멈추려면 `git rm --cached <path>`를 실행하세요.

## Design hook

Claude Code, GitHub Copilot, Codex, Cursor, Grok Build에서 `npx impeccable install`과 `npx impeccable update`는 skill payload와 함께 provider-native hook manifest를 설치합니다. hook은 직접 UI file edit 때 Impeccable design detector를 실행하고 finding을 agent flow로 보여 줍니다. Claude Code, GitHub Copilot, Codex, Grok Build는 edit 뒤 finding을 보여 주며(지원될 때 Stop에서 더 깊은 pass도 실행), Cursor는 나쁜 proposed write가 반영되기 전에 막습니다.

설치되는 hook surface는 다음과 같습니다.

- Claude Code: `.claude/settings.local.json`(gitignored, machine-local)이 `${CLAUDE_PROJECT_DIR}/.claude/skills/impeccable/scripts/hook.mjs`를 실행합니다. shared `settings.json`으로 옮긴 hook도 그 위치에서 존중됩니다.
- GitHub Copilot: `.github/hooks/impeccable.json`(committed, Copilot CLI와 cloud agent가 공유)이 `.github/skills/impeccable/scripts/hook.mjs`를 실행합니다. Copilot CLI는 파일이 repository default branch에 있고 folder가 trusted면 이를 활성화합니다.
- Cursor: `.cursor/hooks.json`이 `.cursor/skills/impeccable/scripts/hook-before-edit.mjs`를 실행합니다.
- Codex: `.codex/hooks.json`이 `.agents/skills/impeccable/scripts/hook.mjs`를 실행합니다.

installer는 관련 없는 hook entry와 setting을 보존합니다. hook manifest가 malformed면 install/update는 기본적으로 abort합니다. malformed file을 `.bak`으로 backup하고 교체하려면 `--force`로 다시 실행하세요.

interactive `install`/`update`에서 Impeccable은 hook을 설명하고 설치 여부를 제안합니다(default yes). 선택은 gitignored `.impeccable/config.local.json`에 developer별로 기억되므로 다시 묻지 않습니다. `--no-hooks`는 아무것도 기록하지 않고 그 실행에서만 건너뜁니다. hook lifecycle setting은 `.impeccable/config.json`의 `hook` key 아래에 있고, detector ignore는 `/impeccable hooks` 및 `npx impeccable detect`가 공유하는 `detector` 아래에 있습니다.

debugging을 위해 `.impeccable/config.json`의 `hook.auditLog`를 path로 설정하면 hook invocation마다 NDJSON 한 줄을 작성합니다(또는 legacy `IMPECCABLE_HOOK_LOG` env var 사용). 일반 사용에서는 설정하지 마세요.

## Build path: comp-first 또는 code-first

새 surface를 디자인할 때 Impeccable은 full-fidelity comp를 먼저 생성하고 그에 맞춰 build하거나, direction contract에 ambition을 적고 finish에서 검사하면서 곧바로 code로 build합니다. comp-first는 더 대담하고 더 오래 걸리며, code-first는 더 간결하고 빠릅니다. `/impeccable init`은 한 번 묻고 답을 `.impeccable/config.json`의 `buildPath`로 기록합니다.

```json
{ "buildPath": "comp" }
```

읽는 값은 `comp`와 `code`뿐입니다. harness에 image generation이 없으면 한 machine에서 team의 committed 값을 override할 수 있도록 gitignored `.impeccable/config.local.json`에 설정하세요. monorepo에서는 repo root에서 한 번 commit하고, 다른 값을 원하는 workspace가 자체 설정을 둡니다. image generation이 가능한 경우에만 comp할 대상이 있으므로 이 선택지가 나타납니다.

기존 설정에 이 값이 없다고 `init`을 다시 실행하거나 file을 손으로 편집할 필요는 없습니다. 기록한 값은 lock이 아니라 default입니다. 각 decision page에는 footer toggle이 있고, 이를 바꾸면 그 session에만 적용됩니다. 아직 아무 값도 기록하지 않은 project에서 바꾸면 round 뒤 한 번만 유지할지 묻고 답을 기록합니다. 기존 project의 migration path는 이것뿐입니다. default가 틀리면 toggle을 쓰고 이어지는 질문에 답하세요.

Codex에는 Impeccable이 안전하게 건너뛸 수 없는 platform step이 하나 있습니다. install 또는 update 뒤 `/hooks`를 열어 project hook을 승인하세요. 이 hook에 대한 Codex marketplace/plugin install flow는 없습니다.

전체 hook 문서: [impeccable.style/docs/hooks](https://impeccable.style/docs/hooks).

수동 copy 명령은 fallback/debug 지시입니다. 일반 경로는 다음입니다.

```bash
npx impeccable install
npx impeccable update
```

## CLI

Impeccable에는 AI harness 없이 anti-pattern을 검출하는 standalone CLI가 포함됩니다.

```bash
npx impeccable detect src/                   # directory scan
npx impeccable detect index.html             # HTML file scan
npx impeccable detect https://example.com    # URL scan(Puppeteer)
npx impeccable detect --json .               # CI-friendly JSON output
npx impeccable detect --no-config src/       # project config/context를 무시한 raw scan
npx impeccable ignores list                  # detector ignore 표시
npx impeccable ignores add-file "src/legacy/**"
npx impeccable ignores add-value overused-font Inter --reason "Brand font"
```

detector는 AI slop(side-tab border, purple gradient, bounce easing, dark glow)과 일반 디자인 품질(line length, cramped padding, small touch target, skipped heading 등)에 걸친 59개 결정론적 issue를 잡습니다.

기본적으로 `detect`는 design hook과 같은 `.impeccable/config.json` 및 `.impeccable/config.local.json` detector config를 존중합니다. 즉 `detector.ignoreRules`, `detector.ignoreFiles`, `detector.ignoreValues`, `detector.designSystem.enabled`입니다. `hook.enabled` 같은 hook lifecycle setting은 자동 hook 실행에만 영향을 줍니다.

repo config 대신 한 file을 따라다니는 waiver가 필요하면 file 안에 inline comment를 추가하세요. `<!-- impeccable-disable overused-font: exported brand doc -->` marker는 모든 comment syntax에서 동작하고 whole file에 적용됩니다(또는 `impeccable-disable-line` / `impeccable-disable-next-line`으로 한 줄). `--no-inline-ignores` 또는 `--no-config`는 이를 무시합니다.

전체 detector 문서: [impeccable.style/docs/detector](https://impeccable.style/docs/detector).

## 지원 도구

- [Cursor](https://cursor.com)
- [Claude Code](https://claude.ai/code)
- [GitHub Copilot](https://github.com/features/copilot)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- [Codex CLI](https://github.com/openai/codex)
- [Grok Build](https://x.ai/cli)
- [OpenCode](https://opencode.ai)
- [Pi](https://pi.dev)
- [Kiro](https://kiro.dev)
- [Trae](https://trae.ai)
- [Rovo Dev](https://www.atlassian.com/software/rovo)
- [Qoder](https://qoder.com)
- [Mistral Vibe](https://docs.mistral.ai/vibe/code/overview)
- [Google Antigravity](https://antigravity.google)

## Community & Ecosystem

community와 ecosystem 대화에 참여하세요.

- GitHub Discussions: bug 신고, feature 요청, newcomer 돕기.
- [npm의 Impeccable](https://www.npmjs.com/package/impeccable): CLI를 받고, release를 보고, package에 star를 남기세요.
- 새 rule의 release note, sample lint report, video highlight는 Twitter의 @pbakaus를 팔로우하세요.

## Contributing

contributor guide와 build instruction은 [DEVELOP.md](docs/DEVELOP.md)를 보세요.

## License

Apache 2.0. [LICENSE](LICENSE)를 보세요.

---

[Paul Bakaus](https://www.paulbakaus.com)가 만들었습니다.
