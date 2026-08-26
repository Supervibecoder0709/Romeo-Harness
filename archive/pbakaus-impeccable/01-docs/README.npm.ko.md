# Impeccable CLI

command line에서 UI anti-pattern과 디자인 품질 issue를 검출합니다. AI가 생성한 UI의 흔적, accessibility violation, 일반 디자인 품질 문제를 포함한 59개 결정론적 rule로 HTML, CSS, JSX, TSX, Vue, Svelte file을 scan합니다.

## 빠른 시작

```bash
# AI harness(Claude, Cursor, Gemini 등)에 skill 설치
npx impeccable skills install

# 특정 scope를 위한 non-interactive install
npx impeccable skills install -y --providers=claude,codex --scope=project

# AI harness 안에서 처음 실행할 명령
/impeccable init

# skill을 최신 version으로 update
npx impeccable skills update

# hook manifest 없이 skill 설치 또는 update
npx impeccable skills install --no-hooks

# Git submodule checkout에서 skill link
npx impeccable skills link --source=.impeccable --providers=claude,cursor

# 사용 가능한 모든 명령 표시
npx impeccable skills help

# file 또는 directory에서 anti-pattern scan
npx impeccable detect src/

# live URL scan(Puppeteer 필요)
npx impeccable detect https://example.com

# CI/tooling용 JSON output
npx impeccable detect --json src/

# deprecated compatibility flag, 그래도 full scan 실행
npx impeccable detect --fast src/
```

## 검출 항목

**AI Slop 흔적**: "AI가 만들었다"고 보이는 pattern입니다.

- side-tab accent border, heading의 gradient text
- purple/violet gradient와 dark 위 cyan palette
- glow accent가 있는 dark mode, border + border-radius 충돌

**Typography issue**: 과도하게 쓰인 font(Inter, Roboto), 평평한 type hierarchy, 하나뿐인 font family

**Color & Contrast**: WCAG AA violation, 색 배경 위 회색 text, 순수 black/white

**Layout & Composition**: 중첩 card, 단조로운 spacing, 모든 것의 가운데 정렬 layout

**Motion**: bounce/elastic easing, layout property transition

**Quality**: 너무 작은 body text, 답답한 padding, 긴 line length, 작은 touch target

전체 59개 결정론적 detector rule입니다. 전체 catalog는 [impeccable.style/slop](https://impeccable.style/slop)에서 보세요.

## Exit Code

- `0`: issue를 찾지 못함
- `2`: anti-pattern 감지

## Option

```
impeccable detect [options] [file-or-dir-or-url...]

  --fast    Regex-only mode(jsdom 생략, 더 빠르지만 덜 정확함)
  --json    finding을 JSON으로 출력
  --help    help 표시
```

## 요구 사항

- Node.js 22.18+
- `jsdom`(dependency에 포함, HTML scan에 사용)
- `puppeteer`(선택 사항, URL scan에만 필요)

## Impeccable의 일부

이 CLI는 AI-powered development tool용 cross-provider design skill pack인 [Impeccable](https://impeccable.style)의 일부입니다. 전체 suite에는 Claude, Cursor, GitHub Copilot, Gemini, Codex 등에서 쓰는 23개 명령이 포함됩니다.

## License

[Apache 2.0](https://github.com/pbakaus/impeccable/blob/main/LICENSE)
