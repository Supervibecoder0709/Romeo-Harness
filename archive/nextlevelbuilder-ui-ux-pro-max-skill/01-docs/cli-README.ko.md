# ui-ux-pro-max-cli — 한국어 번역

원문: [`cli/README.md`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/cli/README.md). 코드 블록·명령·식별자는 유지했다.

AI coding assistant에 UI/UX Pro Max skill을 설치하는 CLI입니다.

## 설치

```bash
npm install -g ui-ux-pro-max-cli
```

## 사용

```bash
# 특정 AI assistant에 설치
uipro init --ai claude      # Claude Code
uipro init --ai cursor      # Cursor
uipro init --ai windsurf    # Windsurf
uipro init --ai antigravity # Antigravity
uipro init --ai copilot     # GitHub Copilot
uipro init --ai kiro        # Kiro
uipro init --ai codex       # Codex (Skills)
uipro init --ai roocode     # Roo Code
uipro init --ai qoder       # Qoder
uipro init --ai gemini      # Gemini CLI
uipro init --ai trae        # Trae
uipro init --ai opencode    # OpenCode
uipro init --ai universal   # Universal / Agent Standard (.agents/skills/)
uipro init --ai all         # 모든 assistant

# 옵션
uipro init --offline        # 호환성 flag; 번들 템플릿 설치
uipro init --force          # 기존 파일 덮어쓰기
uipro init --global         # 홈 디렉터리(~/)에 전역 설치

# 기타 명령
uipro versions              # 사용 가능한 버전 목록
uipro update                # 전역 CLI를 최신 릴리스로 갱신
uipro update --global       # 이 CLI 패키지로 전역 설치 skill 파일 새로고침
```

## GitHub 인증

GitHub 미인증 API는 IP당 시간당 60회 요청을 허용합니다. rate limit에 걸리면 GitHub Personal Access Token(PAT)을 제공해 시간당 5,000회로 올릴 수 있습니다.

**옵션 (우선순위 순):**

```bash
# 1. flag로 직접 전달 (일회성)
uipro init --token ghp_yourtoken
uipro versions --token ghp_yourtoken
uipro update --token ghp_yourtoken

# 2. 프로젝트 범위 환경 변수 설정 (권장)
export UI_PRO_MAX_GITHUB_TOKEN=ghp_yourtoken
uipro init

# 3. UI_PRO_MAX_GITHUB_TOKEN이 없으면 GITHUB_TOKEN도 읽음
export GITHUB_TOKEN=ghp_yourtoken
uipro init
```

토큰 생성: <https://github.com/settings/tokens>에서 **Generate new token (classic)**을 누르고 **no scopes**를 고릅니다. public repo 접근에는 권한이 필요 없습니다. 토큰을 복사해 환경 secret에 보관하고 source file에 하드코딩하지 마세요.

> **경고:** `GITHUB_TOKEN`은 GitHub Actions에서 넓은 repository 권한과 함께 자동 주입될 수 있습니다. CI에서 workflow credential이 release download 요청에 실수로 붙지 않도록 `UI_PRO_MAX_GITHUB_TOKEN`을 우선 사용하세요.

## 작동 방식

`uipro init`은 설치된 CLI package에 bundle된 template으로 assistant별 파일을 생성합니다. 더 새로운 template/data를 원하면 package를 먼저 update한 뒤 다시 생성합니다.

```bash
uipro update                   # 전역 CLI를 최신 릴리스로 갱신
uipro init --ai codex --force  # 새 package에서 skill 파일 다시 생성
```

`uipro update`는 `npm install -g ui-ux-pro-max-cli@latest`를 실행합니다(원문 설명상 Windows에서는 `npm`이 `.cmd`이므로 shell을 사용합니다). 원하면 이 명령을 수동으로 실행할 수 있습니다. CLI가 이미 최신이면 `uipro update`는 설치된 skill 파일만 새로고침합니다.

## 개발

```bash
# 의존성 설치
bun install

# 로컬 실행
bun run src/index.ts --help

# Build
bun run build

# source skill에서 번들 CLI asset 동기화
npm run sync:assets

# publish 전 bundle asset 최신 여부 검증
npm run check:assets

# 로컬 테스트를 위한 link
bun link
```

## 라이선스

CC-BY-NC-4.0
