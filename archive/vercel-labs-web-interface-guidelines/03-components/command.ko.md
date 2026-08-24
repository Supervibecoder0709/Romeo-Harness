---
description: Vercel Web Interface Guidelines 준수 여부로 UI 코드를 검토한다
argument-hint: <file-or-pattern>
---

# Web Interface Guidelines

다음 파일의 준수 여부를 검토합니다: $ARGUMENTS

파일을 읽고 아래 규칙에 대조합니다. 간결하지만 포괄적으로 출력합니다—짧음을 위해 문법은 희생해도 됩니다. 높은 signal-to-noise를 유지합니다.

## 규칙

### 접근성

- icon-only button에는 `aria-label` 필요
- form control에는 `<label>` 또는 `aria-label` 필요
- interactive element에는 keyboard handler(`onKeyDown`/`onKeyUp`) 필요
- action에는 `<button>`, navigation에는 `<a>`/`<Link>` 사용(`<div onClick>` 금지)
- image에는 `alt` 필요(장식이면 `alt=""`)
- 장식 icon에는 `aria-hidden="true"`
- async update(toast, validation)에는 `aria-live="polite"`
- ARIA보다 semantic HTML(`button`, `a`, `label`, `table`) 우선
- heading은 계층적 `<h1>`–`<h6>`; main content용 skip link 포함
- heading anchor에는 `scroll-margin-top`
- 의미 있는 media에는 필요한 caption, transcript, description
- media control은 keyboard 지원; 장식 media는 assistive tech에서 숨김

### Focus 상태

- interactive element에는 보이는 focus 필요: `focus-visible:ring-*` 또는 동등한 것
- focus 대체 없이 `outline-none` / `outline: none` 사용 금지
- `:focus`보다 `:focus-visible` 사용(click 시 focus ring 방지)
- 복합 control의 group focus에는 `:focus-within`
- sticky header/footer/overlay가 focused element를 가려서는 안 됨

### 폼

- input에는 `autocomplete`와 의미 있는 `name`
- 올바른 `type` 사용(`email`, `tel`, `url`, `number`) 및 `inputmode`
- paste 차단 금지(`onPaste` + `preventDefault`)
- label은 clickable(`htmlFor` 또는 wrapping control)
- email, code, username의 spellcheck 비활성화(`spellCheck={false}`)
- checkbox/radio: label + control이 단일 hit target 공유(dead zone 없음)
- submit button은 request가 시작될 때까지 활성; request 중 spinner
- 오류는 field 옆 inline; submit 시 첫 오류에 focus
- placeholder는 `…`로 끝내고 example pattern 표시
- password manager trigger를 피하기 위해 비인증 field에는 `autocomplete="off"`
- 저장하지 않은 변경이 있으면 탐색 전 경고(`beforeunload` 또는 router guard)

### 애니메이션

- `prefers-reduced-motion` 존중(reduced variant 제공 또는 비활성화)
- `transform`/`opacity`만 animate(compositor 친화적)
- `transition: all` 사용 금지—속성을 명시적으로 나열
- 올바른 `transform-origin` 설정
- SVG: `<g>` wrapper에 transform; `transform-box: fill-box; transform-origin: center`
- 애니메이션은 중단 가능—진행 중 사용자 input에 반응
- 다른 콘텐츠와 함께하는 5초 초과 autoplay motion에는 pause, stop, hide control
- muted 장식 loop는 `prefers-reduced-motion`에서 중단

### 타이포그래피

- `...`가 아닌 `…`
- 직선 `"`이 아닌 curly quote `“` `”`
- non-breaking space: `10&nbsp;MB`, `⌘&nbsp;K`, brand name
- loading state는 `…`로 끝남: `"Loading…"`, `"Saving…"`
- 숫자 column/comparison에는 `font-variant-numeric: tabular-nums`
- heading에는 `text-wrap: balance` 또는 `text-pretty` 사용(widow 방지)

### 콘텐츠 처리

- text container는 긴 콘텐츠 처리: `truncate`, `line-clamp-*`, 또는 `break-words`
- text truncation을 위해 flex child에는 `min-w-0`
- empty state 처리—빈 string/array에서 깨진 UI를 렌더링하지 않음
- 사용자 생성 콘텐츠: 짧은, 평균, 아주 긴 input을 예상

### 이미지

- `<img>`에는 명시적 `width`와 `height` 필요(CLS 방지)
- below-fold image: `loading="lazy"`
- above-fold critical image: `priority` 또는 `fetchpriority="high"`

### 성능

- 큰 list(50개 초과): virtualize(`virtua`, `content-visibility: auto`)
- render 중 layout read 금지(`getBoundingClientRect`, `offsetHeight`, `offsetWidth`, `scrollTop`)
- DOM read/write batch; interleaving 피함
- uncontrolled input 선호; controlled input은 keystroke당 비용이 작아야 함
- CDN/asset domain에는 `<link rel="preconnect">` 추가
- critical font: `font-display: swap`과 함께 `<link rel="preload" as="font">`
- animated GIF보다 `<video autoplay muted loop playsinline>` 선호; still 대안 제공
- 짧고 비필수적인 loop: Safari H.264 MP4 `<picture>` source, `prefers-reduced-motion` media condition, still fallback

### Navigation과 State

- URL이 state 반영—filter, tab, pagination, expanded panel은 query param에
- 링크에는 `<a>`/`<Link>` 사용(Cmd/Ctrl-click, middle-click 지원)
- 모든 stateful UI를 deep-link(`useState`를 쓰면 nuqs 또는 유사 도구로 URL sync 고려)
- 파괴적 동작에는 확인 modal 또는 undo window 필요—즉시 실행 금지

### Touch와 Interaction

- `touch-action: manipulation`(double-tap zoom delay 방지)
- `-webkit-tap-highlight-color`을 의도적으로 설정
- modal/drawer/sheet에 `overscroll-behavior: contain`
- drag 중: text selection 비활성화, drag한 element에 `inert`
- 필수적이지 않다면 drag/swipe/pinch/path gesture에는 tap/click과 keyboard 대안 필요
- `autoFocus`는 신중하게—기본 input이 하나인 desktop에만; mobile에서는 피함

### Safe Area와 Layout

- full-bleed layout에는 notch용 `env(safe-area-inset-*)`
- 원치 않는 scrollbar 방지: container에는 `overflow-x-hidden`, content overflow 수정
- layout에는 JS 측정보다 flex/grid

### Dark Mode와 Theming

- dark theme에서는 `<html>`에 `color-scheme: dark`(scrollbar, input 수정)
- `<meta name="theme-color">`은 page background와 일치
- native `<select>`: 명시적 `background-color`와 `color`(Windows dark mode)

### Locale와 i18n

- date/time: 하드코딩 format 대신 `Intl.DateTimeFormat`
- number/currency: 하드코딩 format 대신 `Intl.NumberFormat`
- 언어는 IP가 아니라 `Accept-Language` / `navigator.languages`로 감지
- brand name, code token, identifier: 번역 훼손을 막도록 `translate="no"`로 감쌈

### Hydration 안전성

- `value`가 있는 input에는 `onChange` 필요(또는 uncontrolled에는 `defaultValue`)
- date/time rendering: hydration mismatch(server vs client)를 방지
- `suppressHydrationWarning`은 정말 필요할 때만

### Hover와 Interactive 상태

- button/link에는 `hover:` 상태 필요(시각 피드백)
- interactive state는 contrast 증가: hover/active/focus가 rest보다 더 두드러짐

### 콘텐츠와 Copy

- 능동태: `"The CLI will be installed"` 대신 `"Install the CLI"`
- heading/button에는 Title Case(Chicago style)
- 개수에는 숫자: `"eight deployments"` 대신 `"8 deployments"`
- 구체적인 button label: `"Continue"` 대신 `"Save API Key"`
- 오류 메시지에는 문제뿐 아니라 해결/다음 단계 포함
- 2인칭 사용; 1인칭 피함
- 공간이 제한되면 `and`보다 `&`

### Anti-pattern(이 항목을 표시)

- 확대를 비활성화하는 `user-scalable=no` 또는 `maximum-scale=1`
- `preventDefault`가 있는 `onPaste`
- `transition: all`
- focus-visible 대체 없는 `outline-none`
- `<a>` 없이 inline `onClick` navigation
- click handler가 있는 `<div>` 또는 `<span>`(`<button>`이어야 함)
- dimension 없는 image
- virtualize하지 않은 큰 array `.map()`
- label 없는 form input
- `aria-label` 없는 icon button
- 하드코딩한 date/number format(`Intl.*` 사용)
- 명확한 근거 없는 `autoFocus`
- 압축 video가 적합한 경우 animated GIF
- tap/click·keyboard 대안 없는 gesture-only action

## 출력 형식

파일별로 묶습니다. `file:line` 형식(VS Code에서 click 가능)을 사용합니다. 간결한 finding을 씁니다.

```text
## src/Button.tsx

src/Button.tsx:42 - icon button에 aria-label 없음
src/Button.tsx:18 - input에 label 없음
src/Button.tsx:55 - animation에 prefers-reduced-motion 없음
src/Button.tsx:67 - transition: all → 속성을 나열

## src/Modal.tsx

src/Modal.tsx:12 - overscroll-behavior: contain 없음
src/Modal.tsx:34 - "..." → "…"

## src/Card.tsx

✓ pass
```

문제와 위치를 적습니다. 수정이 명확하지 않을 때를 제외하고 설명은 생략합니다. preamble은 쓰지 않습니다.
