# 웹 인터페이스 가이드라인

인터페이스의 성공은 수백 가지 선택의 결과입니다. 이것은 그 결정들을 모은 살아 있는, 완전하지 않은 목록입니다. 대부분의 가이드라인은 프레임워크와 무관하지만, 일부는 React/Next.js에 특화되어 있습니다. [피드백을 환영합니다](https://github.com/vercel-labs/web-interface-guidelines/tree/main).

## 상호작용

- **키보드는 어디서나 작동합니다.** 모든 흐름은 키보드로 조작할 수 있고 [WAI-ARIA Authoring Patterns](https://www.w3.org/WAI/ARIA/apg/patterns/)를 따릅니다.
- **분명한 포커스.** 포커스 가능한 모든 요소는 가려지지 않는 눈에 보이는 포커스 링을 표시합니다. 포인터 사용자에게 방해되는 포커스 링을 피하려면 `:focus`보다 `:focus-visible`을 선호합니다. 묶인 컨트롤에는 `:focus-within`을 설정합니다. sticky header, footer, banner, overlay가 포커스된 요소를 절대 가리지 않습니다.
- **포커스를 관리합니다.** [WAI-ARIA Patterns](https://www.w3.org/WAI/ARIA/apg/patterns/)에 따라 포커스 trap을 사용하고 포커스를 이동·반환합니다.
- **시각적 대상과 hit target을 맞춥니다.** 예외: 시각적 대상이 24px 미만이면 hit target을 24px 이상으로 넓힙니다. 모바일 최소 크기는 44px입니다.
- **모바일 input 크기.** 포커스 시 iOS Safari의 자동 확대/이동을 방지하려면 모바일에서 `<input>` 글꼴 크기를 16px 이상으로 합니다. 또는 `<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />`를 설정합니다.
- **확대를 존중합니다.** 브라우저 확대를 절대 비활성화하지 않습니다.
- **Hydration 안전 input.** hydration 뒤 input이 포커스나 값을 잃어서는 안 됩니다.
- **붙여넣기를 막지 않습니다.** `<input>` 또는 `<textarea>`에서 붙여넣기를 절대 비활성화하지 않습니다.
- **로딩 버튼.** 로딩 표시기를 보이고 원래 label은 유지합니다.
- **최소 로딩 상태 시간.** spinner/skeleton을 보인다면 빠른 응답에서 깜빡이지 않도록 짧은 표시 지연(~150–300 ms)과 최소 표시 시간(~300–500 ms)을 추가합니다. React의 `<Suspense>` 구성요소는 이를 자동으로 처리합니다.
- **상태로서의 URL.** 공유, 새로고침, Back/Forward 탐색이 동작하도록 상태를 URL에 보존합니다. 예: [nuqs](https://nuqs.dev).
- **낙관적 업데이트.** 성공 가능성이 높으면 UI를 즉시 업데이트하고 서버 응답에서 조정합니다. 실패 시 오류를 보이고 되돌리거나 Undo를 제공합니다.
- **추가 입력과 로딩 상태에는 말줄임표.** 후속 입력을 여는 메뉴 옵션(예: “Rename…”)과 로딩/처리 상태(예: “Loading…”, “Saving…”, “Generating…”)는 말줄임표로 끝냅니다.
- **파괴적 동작을 확인합니다.** 확인을 요구하거나 안전한 시간 창의 Undo를 제공합니다.
- **컨트롤의 double-tap 확대를 막습니다.** `touch-action: manipulation`을 설정합니다.
- **tap highlight는 디자인을 따릅니다.** `webkit-tap-highlight-color`를 설정합니다.
- **관대한 상호작용을 설계합니다.** 넉넉한 hit target, 분명한 affordance, 예측 가능한 상호작용으로 컨트롤의 까다로움을 줄입니다. 예: [prediction cones](https://x.com/JohnPhamous/status/1657083267299028992).
- **Tooltip 시간.** 한 그룹의 첫 tooltip은 지연하고, [그 뒤의 동등한 요소에는 지연을 두지 않습니다](https://x.com/emilkowalski_/status/1962500739336462340).
- **Overscroll 동작.** 예를 들어 modal/drawer에서 `overscroll-behavior: contain`을 의도적으로 설정합니다.
- **스크롤 위치를 보존합니다.** Back/Forward가 이전 스크롤 위치를 복원합니다.
- **속도를 위한 autofocus.** 기본 input이 하나인 데스크톱 화면에서는 autofocus를 사용합니다. 모바일에서는 키보드가 열리면 layout shift가 생길 수 있으므로 거의 사용하지 않습니다.
- **dead zone이 없습니다.** 컨트롤의 일부가 상호작용 가능해 보인다면 실제로 상호작용 가능해야 합니다. 사용자가 어디를 조작해야 할지 추측하게 두지 않습니다.
- **모든 것을 deep-link합니다.** filter, tab, pagination, expanded panel, `useState`를 쓰는 모든 경우입니다.
- **깔끔한 drag 상호작용.** 요소를 drag하는 동안 텍스트 선택을 비활성화하고 [`inert`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/inert)(상호작용을 막음)를 적용해 선택/hover가 동시에 일어나지 않게 합니다.
- **gesture에는 대안이 있습니다.** gesture가 필수적이지 않다면 모든 drag, swipe, pinch, path 기반 동작은 [tap/click 컨트롤과 키보드](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html)로도 작동합니다.
- **링크는 링크입니다.** 표준 브라우저 동작(Cmd/Ctrl+Click, middle-click, right-click 새 탭 열기)을 지원하도록 탐색에는 `<a>` 또는 `<Link>`를 사용합니다. 탐색용 링크를 `<button>` 또는 `<div>`로 대체하지 않습니다.
- **비동기 업데이트를 알립니다.** toast와 inline validation에 polite aria-live를 사용합니다.
- **로캘 인식 키보드 단축키.** 비 QWERTY 배열을 위해 키보드 단축키를 국제화합니다. 플랫폼별 기호를 표시합니다.

## 애니메이션

- **`prefers-reduced-motion`을 존중합니다.** reduced-motion 변형을 제공합니다.
- **구현 선호.** 가능하면 CSS를 선호하고 main thread JavaScript 기반 애니메이션을 피합니다.
  - 선호도: CSS > Web Animations API > JavaScript 라이브러리(예: [motion](https://www.npmjs.com/package/motion)).
- **Compositor 친화적.** GPU 가속 속성(`transform`, `opacity`)을 우선하고 reflow/repaint를 유발하는 속성(`width`, `height`, `top`, `left`)은 피합니다.
- **필요성 확인.** 원인과 결과를 명확히 하거나 의도적인 즐거움을 더할 때만 애니메이션을 사용합니다. 예: [the northern lights](https://x.com/JohnPhamous/status/1831380516509278561).
- **대상에 맞는 easing.** 바뀌는 것(크기, 거리, trigger)에 따라 easing을 선택합니다.
- **중단 가능.** 사용자 입력으로 애니메이션을 취소할 수 있습니다.
- **입력 주도.** muted이고 필수가 아닌 loop 외에는 autoplay를 피합니다. 다른 콘텐츠와 함께 자동 재생되는 [5초 초과](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) motion에는 pause, stop, hide 컨트롤이 있습니다.
- **올바른 transform origin.** motion이 물리적으로 시작하는 곳에 맞춰 고정합니다.
- **`transition: all`은 사용하지 않습니다.** 애니메이션하려는 속성(보통 `opacity`, `transform`)만 명시적으로 나열합니다. `all`은 layout에 영향을 주는 속성까지 의도치 않게 애니메이션하여 jank를 유발할 수 있습니다.
- **크로스 브라우저 SVG transform.** CSS transform/animation은 `<g>` wrapper에 적용하고 `transform-box: fill-box; transform-origin: center;`를 설정합니다. Safari는 역사적으로 SVG의 transform-origin에 버그가 있었고, grouping은 origin 오계산을 피합니다.

## 레이아웃

- **시각적 정렬.** 지각이 기하보다 중요할 때 [±1px를 조정합니다](https://x.com/JohnPhamous/status/1760444698857230360).
- **의도적인 정렬.** 모든 요소는 grid, baseline, edge, 시각적 중심 중 하나에 의도적으로 맞춥니다. 우연한 배치는 없습니다.
- **lockup의 대비를 균형 있게 합니다.** 텍스트와 icon이 나란히 있으면 weight, size, spacing, color를 조정해 서로 충돌하지 않게 합니다. 예를 들어 얇은 stroke icon은 medium-weight 텍스트 옆에서 더 굵은 stroke가 필요할 수 있습니다.
- **반응형 범위.** 모바일, 노트북, ultra-wide에서 검증합니다. ultra-wide는 50%로 축소해 시뮬레이션합니다.
- **safe area를 존중합니다.** [safe-area variables](https://developer.mozilla.org/en-US/docs/Web/CSS/env)로 notch와 inset을 고려합니다.
- **과도한 scrollbar가 없습니다.** 유용한 scrollbar만 렌더링합니다. 원치 않는 scrollbar를 막도록 overflow 문제를 고칩니다. macOS에서는 Windows 사용자가 보는 것을 시험하려고 [“Show scroll bars”를 “Always”로 설정합니다](https://support.apple.com/guide/mac-help/change-appearance-settings-mchlp1225/mac#:~:text=or%20status%20bars.-,Show%20scroll%20bars,-Scroll%20bars%20appear).
- **브라우저가 크기를 정하게 합니다.** JavaScript 측정보다 flex/grid/intrinsic layout을 선호합니다. CSS가 flow, wrapping, alignment를 맡게 해 layout thrash를 피합니다.

## 콘텐츠

- **먼저 inline help.** inline 설명을 선호하고 tooltip은 최후의 수단으로 사용합니다.
- **안정적인 skeleton.** layout shift를 피하도록 skeleton은 최종 콘텐츠를 정확히 따라야 합니다.
- **정확한 page title.** `<title>`은 현재 맥락을 반영합니다.
- **막다른 길이 없습니다.** 모든 화면은 다음 단계 또는 복구 경로를 제공합니다.
- **모든 상태를 설계합니다.** empty, sparse, dense, error 상태입니다.
- **타이포그래피 따옴표.** 직선 따옴표(`" "`)보다 curly quote(`“ ”`)를 선호합니다.
- **widow/orphan을 피합니다.** rag와 줄바꿈을 정돈합니다.
- **비교에는 tabular 숫자.** `font-variant-numeric: tabular-nums` 또는 [Geist Mono](https://vercel.com/font) 같은 monospace를 사용합니다.
- **중복된 상태 단서.** 색상만으로 판단하게 하지 말고 텍스트 label을 포함합니다.
- **icon에는 label이 있습니다.** 비시각 사용자에게도 같은 의미를 텍스트로 전달합니다.
- **schema를 그대로 출시하지 않습니다.** 시각적 layout이 visible label을 생략할 수는 있어도 보조기술용 accessible name/label은 존재해야 합니다.
- **말줄임표 문자를 사용합니다.** 세 마침표 `...` 대신 `…`를 사용합니다.
- **고정된 heading.** 섹션 링크 시 header에 `scroll-margin-top`을 설정합니다.
- **사용자 생성 콘텐츠에 견고합니다.** layout은 짧은, 평균, 아주 긴 콘텐츠를 처리합니다.
- **로캘 인식 형식.** 사용자의 로캘에 맞춰 날짜, 시간, 숫자, delimiter, 통화를 형식화합니다.
- **위치보다 언어 설정을 선호합니다.** 언어는 `Accept-Language` header와 `navigator.languages`로 감지합니다. 언어에 IP/GPS를 절대 의존하지 않습니다.
- **번역으로부터 원문 콘텐츠를 보호합니다.** 브라우저 자동 번역이 brand name, product name, code token, 기술 identifier를 손상시키지 않도록 `translate="no"`로 감쌉니다.
- **접근 가능한 콘텐츠.** 정확한 name(`aria-label`)을 설정하고 장식은 숨기며(`aria-hidden`), [accessibility tree](https://developer.chrome.com/blog/full-accessibility-tree)에서 검증합니다.
- **icon-only button에는 이름이 있습니다.** 설명적인 `aria-label`을 제공합니다.
- **ARIA보다 semantic을 우선합니다.** `aria-*`보다 native element(`button`, `a`, `label`, `table`)를 먼저 사용합니다.
- **heading과 skip link.** 계층적인 `<h1–h6>`와 “Skip to content” link를 둡니다.
- **접근 가능한 media.** [음성과 의미 있는 소리에 caption을 제공하고](https://www.w3.org/WAI/media/av/), audio-only에는 transcript를 제공하며 필수 시각 정보를 설명합니다. 장식 media는 보조기술에서 숨기고, media control은 키보드로 조작할 수 있게 합니다.
- **logo에서 brand resource를 찾습니다.** 빠른 접근을 위해 [nav logo를 right-click합니다](https://x.com/JohnPhamous/status/1636427186566762496).
- **붙어 있어야 하는 용어에는 non-breaking space.** unit, shortcut, name이 떨어지지 않게 non-breaking space `&nbsp;`를 씁니다: `10 MB` → `10&nbsp;MB`, `⌘ + K` → `⌘&nbsp;+&nbsp;K`, `Vercel SDK` → `Vercel&nbsp;SDK`. 공백이 전혀 없어야 하면 `&#x2060;`를 사용합니다.

## 폼

- **Enter로 제출.** text input에 포커스가 있고 그것이 유일한 control이면 Enter가 제출합니다. control이 많다면 마지막 control에 적용합니다.
- **Textarea 동작.** `<textarea>`에서는 ⌘/⌃+Enter가 제출하고 Enter는 줄바꿈을 삽입합니다.
- **모든 곳에 label.** 모든 control에는 `<label>`이 있거나 보조기술용 label과 연결되어 있습니다.
- **Label 활성화.** `<label>`을 click하면 연결된 control에 포커스합니다.
- **제출 규칙.** 제출이 시작될 때까지 submit을 활성화합니다. 이후 in-flight request 동안 비활성화하고 spinner를 보이며 idempotency key를 포함합니다.
- **입력을 막지 않습니다.** field가 숫자만 받아도 어떤 input이든 허용하고 validation feedback을 보입니다. keystroke를 완전히 막으면 사용자는 설명을 받지 못해 혼란스럽습니다.
- **미리 submit을 비활성화하지 않습니다.** 불완전한 form도 제출해 validation feedback을 보게 합니다.
- **control에 dead zone이 없습니다.** checkbox와 radio에는 dead zone이 없고 label과 control은 하나의 넉넉한 hit target을 공유합니다.
- **오류 위치.** 오류는 field 옆에 보이고 submit 시 첫 오류에 포커스합니다.
- **Autocomplete와 name.** autofill을 위해 `autocomplete`와 의미 있는 `name` 값을 설정합니다.
- **선택적으로 spellcheck.** email, code, username 등에는 비활성화합니다.
- **올바른 type과 input mode.** 더 나은 keyboard와 validation을 위해 알맞은 `type`과 `inputmode`를 씁니다.
- **Placeholder는 비어 있음을 나타냅니다.** 말줄임표로 끝냅니다.
- **Placeholder 값.** `+1 (123) 456-7890`, `sk-012345679…`처럼 example value 또는 pattern으로 설정합니다.
- **저장하지 않은 변경.** 데이터가 사라질 수 있으면 탐색 전에 경고합니다.
- **Password manager와 2FA.** 호환성을 보장하고 one-time code 붙여넣기를 허용합니다.
- **비인증 field에서 password manager를 유발하지 않습니다.** “Search” 같은 input에는 예약 name(예: password)을 피하고 `autocomplete="off"` 또는 OTP field의 `autocomplete="one-time-code"`처럼 특정 token을 사용합니다.
- **텍스트 교체와 확장.** 일부 input method는 trailing whitespace를 추가합니다. 혼란스러운 오류 메시지를 보이지 않도록 input이 값을 trim해야 합니다.
- **Windows `<select>` background.** Windows dark mode contrast bug를 피하려면 native `<select>`에 `background-color`와 `color`를 명시적으로 설정합니다.

## 성능

- **Device/browser matrix.** iOS Low Power Mode와 macOS Safari에서 시험합니다.
- **신뢰성 있게 측정합니다.** overhead를 더하거나 runtime behavior를 바꾸는 extension을 비활성화합니다.
- **re-render를 추적합니다.** re-render를 최소화하고 빠르게 만듭니다. [React DevTools](https://react.dev/learn/react-developer-tools) 또는 [React Scan](https://react-scan.com/)을 사용합니다.
- **profiling 시 throttle.** CPU와 network throttling으로 시험합니다.
- **layout 작업 최소화.** read/write를 batch하고 불필요한 reflow/repaint를 피합니다.
- **네트워크 latency budget.** `POST/PATCH/DELETE`는 500ms 미만에 완료합니다.
- **Keystroke 비용.** uncontrolled input을 선호하고 controlled loop는 keystroke당 비용이 작게 만듭니다.
- **큰 목록.** 큰 list는 [virtua](https://github.com/inokawa/virtua) 또는 [content-visibility: auto](https://web.dev/articles/content-visibility) 등으로 virtualize합니다.
- **현명하게 preload.** above-the-fold image만 preload하고 나머지는 lazy-load합니다.
- **image로 인한 CLS 방지.** 명시적인 image dimension을 설정하고 공간을 예약합니다.
- **origin에 preconnect.** DNS/TLS latency를 줄이려 asset/CDN domain에는 필요할 때 crossorigin과 함께 `<link rel="preconnect">`를 사용합니다.
- **font preload.** flash와 layout shift를 피하기 위해 critical text에 사용합니다.
- **font subset.** unicode-range로 사용하는 code point/script만 전송하고(variable axis도 필요한 것만 제한) 크기를 줄입니다.
- **비싼 작업에 main thread를 쓰지 않습니다.** 특히 오래 걸리는 task는 [Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API)로 옮겨 페이지 상호작용을 막지 않습니다.
- **animated GIF보다 video.** loop animation에는 `<video autoplay muted loop playsinline>`을 선호합니다. [현대 video는 보통 GIF보다 훨씬 작습니다](https://web.dev/articles/replace-gifs-with-videos). still 대안을 제공하고 `prefers-reduced-motion`을 존중합니다.
- **Safari의 video-as-image.** 짧고 필수가 아닌 loop에는 [`<picture>`에 H.264 MP4 source를 추가합니다](https://developer.apple.com/documentation/webkit/delivering-video-content-for-safari#Use-MP4-Video-Instead-of-Animated-GIFs). Safari는 video를 image pipeline으로 렌더링하고 다른 브라우저는 still fallback을 사용합니다. MP4 source는 `prefers-reduced-motion`으로 gate합니다. 사용자가 playback control을 필요로 하거나 animation이 필수 정보를 전달할 때는 `<video>`를 사용합니다.

## 디자인

- **겹친 shadow.** 최소 두 layer로 ambient + direct light를 모방합니다.
- **선명한 border.** border와 shadow를 결합합니다. 반투명 border가 edge 선명도를 높입니다.
- **중첩된 radius.** child radius는 parent radius 이하이고 동심이어야 곡선이 정렬됩니다.
- **hue 일관성.** neutral이 아닌 background에서는 border/shadow/text를 같은 hue 쪽으로 tint합니다.
- **접근 가능한 chart.** color-blind-friendly palette를 사용합니다.
- **최소 contrast.** 더 정확한 지각 contrast를 위해 [WCAG 2](https://webaim.org/resources/contrastchecker/)보다 [APCA](https://apcacontrast.com/)를 선호합니다.
- **상호작용은 contrast를 높입니다.** `:hover`, `:active`, `:focus`는 rest state보다 contrast가 높습니다.
- **browser UI는 background와 맞춥니다.** `<meta name="theme-color" content="#000000">`를 설정해 [browser theme color를 page background와 맞춥니다](https://x.com/JohnPhamous/status/1816160187839107342).
- **알맞은 color-scheme을 설정합니다.** dark theme에서는 scrollbar와 다른 device UI가 알맞은 contrast를 갖도록 `<html>` tag를 `color-scheme: dark`로 style합니다.
- **텍스트 anti-aliasing과 transform.** text scaling은 smoothing을 바꿀 수 있습니다. text node 대신 wrapper를 animate합니다. artifact가 지속되면 자체 layer로 올리기 위해 `translateZ(0)` 또는 `will-change: transform`을 설정합니다.
- **gradient banding을 피합니다.** css mask로 콘텐츠를 dark color로 fade하면 banding이 생길 수 있습니다. [대신 background image를 사용할 수 있습니다](https://x.com/JohnPhamous/status/1724491202148675590).

# Vercel 전용

이 선호는 Vercel의 brand와 product 선택을 반영합니다. 보편적인 가이드라인은 아닙니다.

## 카피라이팅

- **능동태.**
  - “_The CLI will be installed,_” 대신 _“Install the CLI.”_라고 씁니다.
- **heading과 button은 Title Case**를 사용합니다([Chicago](https://title.sh/)). marketing page에서는 sentence case를 사용합니다.
- **분명하고 간결하게.** 가능한 적은 단어를 씁니다.
- **`and`보다 `&`를 선호합니다.**
- **동작 지향 언어.**
  - _“You will need the CLI…”_ 대신 _“Install the CLI…”_라고 씁니다.
- **명사의 일관성.** 고유한 용어는 가능한 적게 도입합니다.
- **2인칭으로 씁니다.** 1인칭을 피합니다.
- **일관된 placeholder 사용.**
  - 문자열: `YOUR_API_TOKEN_HERE`. 숫자: `0123456789`.
- **개수에는 숫자를 사용합니다.**
  - _“eight deployments”_ 대신 _“8 deployments”_라고 씁니다.
- **일관된 통화 형식.** 같은 맥락에서는 통화를 소수점 0자리 또는 2자리 중 하나로만 표시하고 섞지 않습니다.
- **숫자와 unit을 공백으로 분리합니다.**
  - `10MB` 대신 `10 MB`라고 씁니다.
  - 예: `10&nbsp;MB`처럼 non-breaking space를 사용합니다.
- **기본적으로 긍정 언어.** 오류에서도 문제 해결을 돕고 격려하는 방식으로 메시지를 구성합니다.
  - _“Your deployment failed,”_ 대신 _“Something went wrong—try again or contact support.”_라고 씁니다.
- **오류 메시지는 출구를 안내합니다.** 무엇이 잘못됐는지만 말하지 말고 고칠 방법을 알려줍니다.
  - _“Invalid API key,”_ 대신 _“Your API key is incorrect or expired. Generate a new key in your account settings.”_라고 씁니다. copy와 button/link는 명확한 action을 교육하고 제공해야 합니다.
- **모호함을 피합니다.** label은 분명하고 구체적입니다.
  - button label _“Continue”_ 대신 _“Save API Key”_라고 씁니다.

# Agent와 통합하기

AI coding agent와 이 가이드라인을 함께 사용합니다. 생성된 모든 interface를 감사하세요.

## 검토 명령

UI code를 검토하려면 `web-design-guidelines` skill을 설치하세요.

```bash
npx skills add https://github.com/vercel-labs/agent-skills --skill web-design-guidelines
```

## AGENTS.md

agent가 생성 중 이 가이드라인을 적용하도록 프로젝트에 [AGENTS.md](https://agents.md/)를 추가하세요.

- [AGENTS.md 다운로드](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/AGENTS.md)

# Vercel에 합류하세요

우리는 이런 세부 사항에 몰입하는 사람을 채용합니다. [채용 공고를 확인하세요](https://vercel.com/careers?function=Design).

---

피드백을 주신 [Adam](https://x.com/argyleink), [Jimmy](https://x.com/wwwjim), [Jonnie](https://destroytoday.com/), [Lochie](https://x.com/lochieaxon), [Paco](https://pa.co), [Joe](https://joebell.studio/), [Austin](https://x.com/austin_malerba)에게 감사합니다.
