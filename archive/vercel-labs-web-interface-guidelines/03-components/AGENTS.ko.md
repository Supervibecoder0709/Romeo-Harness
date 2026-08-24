# AGENTS.md 한국어 번역

접근 가능하고, 빠르며, 즐거운 UI를 만들기 위한 간결한 규칙입니다. 결정을 이끌기 위해 MUST/SHOULD/NEVER를 사용합니다.

## 상호작용

### 키보드

- MUST: [WAI-ARIA APG](https://www.w3.org/WAI/ARIA/apg/patterns/)에 따른 완전한 키보드 지원
- MUST: 눈에 보이고 가려지지 않는 focus ring(`:focus-visible`; 그룹은 `:focus-within`으로 묶음); sticky/fixed 요소가 focus를 절대 가리지 않음
- MUST: APG pattern에 따라 focus를 관리(trap, 이동, 반환)
- NEVER: 눈에 보이는 focus 대체 없이 `outline: none` 사용

### 대상과 입력

- MUST: hit target 24px 이상(모바일 44px 이상); 시각적 크기가 24px 미만이면 hit area 확장
- MUST: iOS 확대를 막기 위해 모바일 `<input>` font-size 16px 이상
- NEVER: 브라우저 확대 비활성화(`user-scalable=no`, `maximum-scale=1`)
- MUST: double-tap 확대를 막도록 `touch-action: manipulation`
- SHOULD: 디자인에 맞게 `-webkit-tap-highlight-color` 설정

### 폼

- MUST: hydration 안전 input(포커스/값 손실 없음)
- NEVER: `<input>`/`<textarea>`에서 paste 차단
- MUST: loading button은 spinner를 보이고 원래 label 유지
- MUST: focused input은 Enter로 제출; `<textarea>`에서는 ⌘/Ctrl+Enter로 제출
- MUST: request가 시작될 때까지 submit 활성 유지; 이후 spinner와 함께 비활성화
- MUST: 자유 텍스트를 받아들이고 이후 validate—typing 차단 금지
- MUST: 불완전한 form도 제출할 수 있게 해 validation을 드러냄
- MUST: 오류는 field 옆에 inline으로 표시; submit 시 첫 오류에 focus
- MUST: `autocomplete` + 의미 있는 `name`; 올바른 `type`과 `inputmode`
- SHOULD: email/code/username의 spellcheck 비활성화
- SHOULD: placeholder는 `…`로 끝내고 예시 pattern 표시
- MUST: 저장하지 않은 변경이 있으면 탐색 전 경고
- MUST: password manager와 2FA 호환; code paste 허용
- MUST: text expansion의 trailing space를 처리하도록 값 trim
- MUST: checkbox/radio에 dead zone 없음; label+control이 하나의 hit target 공유

### 상태와 탐색

- MUST: URL이 상태 반영(deep-link filter/tab/pagination/expanded panel)
- MUST: Back/Forward가 scroll position 복원
- MUST: 탐색에 `<a>`/`<Link>` 사용(Cmd/Ctrl/middle-click 지원)
- NEVER: 탐색에 `<div onClick>` 사용

### 피드백

- SHOULD: optimistic UI; 응답에서 조정; 실패 시 rollback 또는 Undo 제공
- MUST: 파괴적 동작 확인 또는 Undo window 제공
- MUST: toast/inline validation에 polite `aria-live` 사용
- SHOULD: 후속 입력을 여는 옵션(`Rename…`)과 loading state(`Loading…`)에는 ellipsis(`…`) 사용

### Touch와 Drag

- MUST: 넉넉한 대상, 분명한 affordance; 까다로운 상호작용 피함
- MUST: 첫 tooltip은 지연; 이후 동등한 요소는 즉시
- MUST: modal/drawer에 `overscroll-behavior: contain`
- MUST: drag 중 text selection 비활성화하고 drag한 요소에 `inert` 설정
- MUST: 필수적이지 않다면 drag/swipe/pinch/path gesture에 tap/click·키보드 대안 제공
- MUST: clickable해 보인다면 실제 clickable해야 함

### Autofocus

- SHOULD: 기본 input이 하나인 데스크톱에서는 autofocus; 모바일에서는 드물게 사용

## 애니메이션

- MUST: `prefers-reduced-motion` 존중(reduced variant 제공 또는 비활성화)
- SHOULD: CSS > Web Animations API > JS library 선호
- MUST: compositor 친화 속성(`transform`, `opacity`)만 animate
- NEVER: layout 속성(`top`, `left`, `width`, `height`) animate
- NEVER: `transition: all`—속성을 명시적으로 나열
- SHOULD: 원인/결과를 명확히 하거나 의도적인 즐거움을 더할 때만 animate
- SHOULD: 변화(크기/거리/trigger)에 맞는 easing 선택
- MUST: 애니메이션은 중단 가능하고 input 주도적; autoplay는 muted, 비필수 loop에 한정
- MUST: 다른 콘텐츠와 함께하는 5초 초과 autoplay motion에는 pause, stop, hide control 제공
- MUST: 올바른 `transform-origin`(motion은 물리적으로 시작할 위치에서 시작)
- MUST: SVG transform은 `transform-box: fill-box`인 `<g>` wrapper에 적용

## 레이아웃

- SHOULD: 시각적 정렬; 지각이 기하보다 우선할 때 ±1px 조정
- MUST: grid/baseline/edge에 의도적으로 정렬—우연한 배치 없음
- SHOULD: icon/text lockup의 균형(weight/size/spacing/color)
- MUST: 모바일, 노트북, ultra-wide 검증(ultra-wide는 50% zoom으로 시뮬레이션)
- MUST: safe area(`env(safe-area-inset-*)`) 존중
- MUST: 원치 않는 scrollbar 방지; overflow 수정
- SHOULD: layout에 JS 측정보다 flex/grid 사용

## 콘텐츠와 접근성

- SHOULD: 먼저 inline help; tooltip은 최후의 수단
- MUST: layout shift 방지를 위해 skeleton이 최종 콘텐츠를 그대로 모방
- MUST: `<title>`이 현재 맥락과 일치
- MUST: 막다른 길 없음; 항상 다음 단계/복구 제공
- MUST: empty/sparse/dense/error 상태 설계
- SHOULD: curly quote(`“ ”`); widow/orphan 피함(`text-wrap: balance`)
- MUST: 숫자 비교에는 `font-variant-numeric: tabular-nums`
- MUST: 중복된 상태 단서(색상만 사용 금지); icon에는 text label
- MUST: 시각적으로 label이 없어도 accessible name 존재
- MUST: `...`가 아닌 `…` 문자 사용
- MUST: heading에 `scroll-margin-top`; “Skip to content” link; 계층적 `<h1>`–`<h6>`
- MUST: 사용자 생성 콘텐츠에 견고(짧음/평균/매우 김)
- MUST: 로캘 인식 날짜/시간/숫자(`Intl.DateTimeFormat`, `Intl.NumberFormat`)
- SHOULD: 자동 번역으로 인한 훼손을 막기 위해 brand name, code token, identifier에 `translate="no"`
- MUST: 정확한 `aria-label`; 장식 요소에는 `aria-hidden`
- MUST: icon-only button에는 설명적인 `aria-label`
- MUST: ARIA보다 native semantic(`button`, `a`, `label`, `table`) 우선
- MUST: media에 필요한 caption/transcript/description; control은 keyboard 조작 가능; 장식 media는 assistive tech에서 숨김
- MUST: non-breaking space: `10&nbsp;MB`, `⌘&nbsp;K`, brand name

## 콘텐츠 처리

- MUST: text container가 긴 콘텐츠 처리(`truncate`, `line-clamp-*`, `break-words`)
- MUST: text truncation을 위해 flex child에 `min-w-0`
- MUST: empty state 처리—빈 string/array 때문에 UI가 깨지지 않음

## 성능

- SHOULD: iOS Low Power Mode와 macOS Safari 시험
- MUST: 신뢰성 있게 측정(runtime을 왜곡하는 extension 비활성화)
- MUST: re-render 추적·최소화(React DevTools/React Scan)
- MUST: CPU/network throttling으로 profile
- MUST: layout read/write batch; reflow/repaint 피함
- MUST: mutation(`POST`/`PATCH`/`DELETE`) 목표 500ms 미만
- SHOULD: uncontrolled input 선호; controlled input은 keystroke당 비용이 작아야 함
- MUST: 큰 list(50개 초과) virtualize
- MUST: above-fold image preload; 나머지는 lazy-load
- MUST: CLS 방지(명시적 image dimension)
- SHOULD: CDN domain에는 `<link rel="preconnect">`
- SHOULD: critical font는 `font-display: swap`과 함께 `<link rel="preload" as="font">`
- SHOULD: animated GIF보다 `<video autoplay muted loop playsinline>`; still/reduced-motion 대안 제공
- SHOULD: 짧고 비필수적인 loop에는 Safari H.264 MP4 `<picture>` source, `prefers-reduced-motion` media condition, still fallback 포함

## Dark Mode와 Theming

- MUST: dark theme에서는 `<html>`에 `color-scheme: dark`
- SHOULD: `<meta name="theme-color">`는 page background와 일치
- MUST: native `<select>`에 명시적 `background-color`와 `color`(Windows 수정)

## Hydration

- MUST: `value`가 있는 input에는 `onChange` 필요(또는 `defaultValue` 사용)
- SHOULD: hydration mismatch가 생기지 않도록 date/time rendering 보호

## 디자인

- SHOULD: layer가 있는 shadow(ambient + direct)
- SHOULD: 반투명 border + shadow로 선명한 edge
- SHOULD: nested radius: child ≤ parent; 동심
- SHOULD: hue 일관성: border/shadow/text를 background hue 쪽으로 tint
- MUST: 접근 가능한 chart(color-blind-friendly palette)
- MUST: contrast 충족—WCAG 2보다 [APCA](https://apcacontrast.com/) 선호
- MUST: `:hover`/`:active`/`:focus`에서 contrast 증가
- SHOULD: browser UI를 background와 일치
- SHOULD: 어두운 color gradient banding 피함(필요하면 background image 사용)
