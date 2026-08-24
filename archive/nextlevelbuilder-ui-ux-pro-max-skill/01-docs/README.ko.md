# UI UX Pro Max — 사용자·운영 섹션 한국어 번역

> 번역 범위: 고정 SHA의 `README.md` 중 설치, 전제조건, 사용, 고급 명령, 지속 저장, 정본/검증/refresh, 문제 해결 섹션이다. 배지·예시 이미지·Star History·호환 agent의 잔여 나열은 운영 판단에 직접 필요하지 않아 이 번역본에서는 제외했다. 원문 위치는 [E02](../06-source-evidence.md)이다.

## 설치

### Claude Marketplace 사용 (Claude Code)

Claude Code에서 다음 두 명령으로 직접 설치합니다.

```
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

### CLI 사용 (권장)

```bash
# CLI를 전역 설치
npm install -g ui-ux-pro-max-cli

# 프로젝트로 이동
cd /path/to/your/project

# AI assistant용으로 설치
uipro init --ai claude      # Claude Code
uipro init --ai cursor      # Cursor
uipro init --ai windsurf    # Windsurf
uipro init --ai antigravity # Antigravity
uipro init --ai copilot     # GitHub Copilot
uipro init --ai kiro        # Kiro
uipro init --ai codex       # Codex CLI
uipro init --ai qoder       # Qoder
uipro init --ai roocode     # Roo Code
uipro init --ai gemini      # Gemini CLI
uipro init --ai trae        # Trae
uipro init --ai opencode    # OpenCode
uipro init --ai continue    # Continue
uipro init --ai codebuddy   # CodeBuddy
uipro init --ai droid       # Droid (Factory)
uipro init --ai kilocode    # KiloCode
uipro init --ai warp        # Warp
uipro init --ai augment     # Augment
uipro init --ai codewhale   # CodeWhale
uipro init --ai universal   # Universal / Agent Standard (.agents/skills/)
uipro init --ai all         # 모든 assistant
```

npm 패키지 이름은 `ui-ux-pro-max-cli`이고, 설치되는 명령은 계속 `uipro`입니다. 이전 `uipro-cli` 릴리스는 최신 asset에 사용하면 안 됩니다.

### 전역 설치 (모든 프로젝트에서 사용)

```bash
uipro init --ai claude --global    # ~/.claude/skills/에 설치
uipro init --ai cursor --global    # ~/.cursor/skills/에 설치
uipro init --ai universal --global # ~/.agents/skills/에 설치
```

### 기타 CLI 명령

```bash
uipro versions              # 사용 가능한 버전 목록
uipro update                # 설치된 CLI 패키지에서 skill 파일 새로고침
uipro update --global       # 전역 skill 파일 새로고침
uipro init --offline        # 호환성 flag; 번들 템플릿 설치
uipro uninstall             # skill 제거(플랫폼 자동 감지)
uipro uninstall --ai claude # 지정 플랫폼 제거
uipro uninstall --global    # 전역 설치에서 제거
```

## 전제조건

검색 스크립트에는 Python 3.x가 필요합니다(표준 라이브러리만 사용하며 스크립트가 아무것도 설치하거나 네트워크 호출을 하지 않습니다).

```bash
python3 --version
```

Python이 없다면 [python.org](https://www.python.org/downloads/) 또는 운영체제 패키지 관리자(Homebrew, apt, winget)로 사용자가 직접 설치합니다. 이 설치 단계는 **사람 사용자**를 위한 것입니다. 이 skill을 쓰는 AI agent는 사용자 기기에 소프트웨어를 설치하지 말고 요청해야 합니다.

## 사용

### Skill 모드 (자동 활성화)

지원: Claude Code, Cursor, Windsurf, Antigravity, Codex CLI, Continue, Gemini CLI, OpenCode, Qoder, CodeBuddy, Droid (Factory), KiloCode, Warp, Augment, CodeWhale.

UI/UX 작업을 요청하면 skill이 자동으로 활성화됩니다. 자연스럽게 대화하면 됩니다.

```
Build a landing page for my SaaS product
```

> **Trae:** 먼저 **SOLO** 모드로 전환합니다. UI/UX 요청에 skill이 활성화됩니다.

### Workflow 모드 (Slash Command)

지원: Kiro, GitHub Copilot, Roo Code, KiloCode.

```text
/ui-ux-pro-max Build a landing page for my SaaS product
```

### 작동 방식

1. **요청:** build, design, create, implement, review, fix, improve 등 UI/UX 작업을 요청합니다.
2. **설계 시스템 생성:** AI가 추론 엔진을 사용해 완전한 설계 시스템을 자동 생성합니다.
3. **스마트 추천:** 제품 유형과 요구사항으로 가장 적합한 style, color, typography를 찾습니다.
4. **코드 생성:** 적절한 색, 폰트, spacing, best practice로 UI를 구현합니다.
5. **납품 전 검사:** 흔한 UI/UX anti-pattern에 대해 검증합니다.

### 지원 stack

| 구분 | Stack |
|---|---|
| Web (HTML) | HTML + Tailwind (기본) |
| React Ecosystem | React, Next.js, shadcn/ui |
| Vue Ecosystem | Vue, Nuxt.js, Nuxt UI |
| Angular | Angular |
| PHP | Laravel (Blade, Livewire, Inertia.js) |
| Other Web | Svelte, Astro, Three.js |
| Desktop | JavaFX, WPF, WinUI 3, Avalonia, Uno Platform, UWP |
| iOS | SwiftUI |
| Android | Jetpack Compose |
| Cross-Platform | React Native, Flutter |

선호 stack을 prompt에 언급하거나 HTML + Tailwind 기본값을 사용합니다.

## Design System 명령 (고급)

Continue으로 설치했다면 아래 `.claude/skills/`를 `.continue/skills/`로 바꿉니다. Droid (Factory)는 `.factory/skills/`를 사용합니다.

```bash
# ASCII 출력으로 design system 생성
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness" --design-system -p "Serenity Spa"

# Markdown 출력으로 생성
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "fintech banking" --design-system -f markdown

# 도메인별 검색
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "glassmorphism" --domain style
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "elegant serif" --domain typography
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "dashboard" --domain chart
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "error summary validation" --domain ux

# Stack별 지침
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "form validation" --stack react
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "responsive layout" --stack html-tailwind
```

Web stack 검색은 version-aware입니다. 이전 major를 명시하지 않은 질의는 현재 active 지침을 반환합니다. `Svelte 4`, `Next.js 15`처럼 legacy를 명시하면 curated legacy 행만 `Status`, `Applies To`와 함께 반환합니다. 해당 legacy 지침이 없으면 서로 다른 framework generation을 섞는 대신 0건을 반환합니다.

## Design System 저장 (Master + Overrides 패턴)

세션을 넘어서 계층적으로 검색할 수 있도록 설계 시스템을 파일에 저장합니다.

```bash
# README 원문의 예시
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "SaaS dashboard" --design-system --persist -p "MyApp"

# 페이지별 override 파일도 생성
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "SaaS dashboard" --design-system --persist -p "MyApp" --page "dashboard"
```

이 명령은 다음 `design-system/` 구조를 만듭니다.

```text
design-system/
├── MASTER.md           # Global Source of Truth (colors, typography, spacing, components)
└── pages/
    └── dashboard.md    # Page-specific overrides (Master와 다른 부분만)
```

특정 페이지를 만들 때 먼저 `design-system/pages/checkout.md`가 있는지 확인합니다. 있으면 그 규칙이 Master를 **override**하고, 없으면 `design-system/MASTER.md`만 사용합니다.

> 운영 보정: 이 README 예시는 `--output-dir`를 생략하지만, 실제 주 skill은 실행 cwd에 쓰는 일을 막기 위해 project root를 가리키는 `--output-dir "<project-root>"`를 항상 전달하라고 지시합니다. 운영에는 그 지침을 사용해야 합니다. [E04]

## 정본·동기화·catalog refresh

플랫폼별 파일은 template-based generation system으로 CLI가 동적으로 만듭니다. 사용자 설치에는 항상 CLI를 사용합니다.

```bash
npm install -g ui-ux-pro-max-cli
uipro init --ai <platform>
```

기여자는 `src/ui-ux-pro-max/`에서 data, Python scripts, templates를 변경하고 다음으로 CLI/Claude asset을 동기화·검증합니다.

```bash
cd cli
npm run sync:assets
npm run check:assets
npm run verify:data
npm run typecheck
```

README는 catalog summary에 승인 Google Fonts 1,934개, review exclusion 8개, curated icon guidance 105행, upstream Phosphor manifest 1,512 icons라고 적습니다. 일상 개발/PR CI의 full offline gate는 다음과 같습니다.

```bash
npm --prefix cli run verify:data
# 또는 generated catalog summary만 점검
npm --prefix cli run validate:catalog-summary
```

live upstream refresh는 `refresh-catalogs.yml`에서 월요일 03:17 UTC에 또는 수동으로 실행되도록 분리돼 있습니다. `GOOGLE_FONTS_API_KEY` GitHub Actions secret을 설정한 뒤 실행하고 review artifact를 다운로드합니다.

```bash
gh workflow run refresh-catalogs.yml
run_id="$(gh run list --workflow refresh-catalogs.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
gh run watch "$run_id"
gh run download "$run_id" --name "catalog-refresh-review-$run_id"
```

원문은 이 workflow가 Google Fonts API와 pinned Phosphor package를 읽어 candidate와 unified diff artifact를 만들며, repository에는 read-only permission만 가지고 commit/push/PR/merge하지 않는다고 설명합니다. candidate는 change report, exclusions, licenses, relevance metrics, offline gate를 검토한 후 사람이 `src/ui-ux-pro-max/data/`로 승격해야 합니다.

## 문제 해결

### `uipro`가 `uninstall` 또는 `update`를 모른다고 할 때

설치된 `ui-ux-pro-max-cli`가 오래된 것입니다.

```bash
npm install -g ui-ux-pro-max-cli@latest
uipro uninstall
```

### `uipro uninstall`이 설치된 AI skill directory를 찾지 못할 때

원래 설치했던 project root에서 실행하거나 global install에서 제거합니다.

```bash
cd /path/to/your/project
uipro uninstall

uipro uninstall --global
```

### `npm install -g` 권한 오류

Node version manager를 쓰거나 global install 없이 다음을 사용합니다.

```bash
npx ui-ux-pro-max-cli init --ai claude
```

### Python이 없거나 출력이 잘릴 때

Python 3.x는 사람이 직접 설치합니다. 사람이 읽는 출력은 긴 field를 300자로 자를 수 있으므로 전체 데이터에는 `--json`을 사용합니다.

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "SaaS" --domain style --json
```

원문 라이선스는 [MIT License](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/LICENSE)입니다.
