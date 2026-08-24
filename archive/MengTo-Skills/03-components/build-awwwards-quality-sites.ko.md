원문: agent-skills/web-design/build-awwwards-quality-sites/SKILL.md  
고정 근거: [E11]

---
name: build-awwwards-quality-sites
description: original reference-inspired imagery, standout hero, GSAP choreography, 하나의 smooth-scroll engine, 선택적 Three.js shader, 정직한 icon/logo sourcing, photo avatar, accessibility, performance safeguard로 독특하고 motion-rich한 marketing, editorial, portfolio, landing website를 art-direct하고 구현한다. Awwwards-quality, premium, cinematic, interactive, high-concept, motion-led website 또는 이 visual/motion system을 명시적으로 요청할 때 사용한다.
---

# Awwwards-Quality Site 구축

visual idea, media, typography, motion이 같은 이야기를 하는 응집력 있고 기억할 만한 site를 만든다. Awwwards quality는 award나 recognition claim이 아니라 acceptance bar로 취급한다.

## 1. Art direction 설정

- 구현 전에 사용자의 reference evidence를 완전히 검사한다. hierarchy, pacing, contrast, image treatment, motion principle 같은 high-level trait만 추출한다.
- 실질적으로 새로운 identity, layout, copy system, imagery, interaction language를 만든다. reference asset, screenshot, source code, identity, copy를 reuse, trace, closely reproduce하지 않는다.
- 사용자가 요청했거나 관련성이 있고 사용할 수 있을 때만 Aura.build top asset imagery를 쓴다. asset library가 아니라 high-level inspiration으로 취급한다.
- 호환되는 설치된 web-design skill을 최소 하나 선택하고 이름을 쓴다. 가장 작은 관련 집합을 따르며 관련 없는 aesthetic system을 결합하지 않는다.
- coding 전에 compact direction을 작성한다: visual thesis, hero focal asset, type hierarchy, color system, section sequence, motion narrative, 선택한 smooth-scroll engine, Three.js 결정, asset provenance plan.

## 2. 정직한 asset system 구축

- concept를 실질적으로 개선할 때 original hero/project imagery를 생성한다. 더 강하면 적절히 licensed된 media를 사용하고 provenance를 site source에 보관한다.
- model-authored SVG, CSS, canvas path로 illustration을 그리지 않는다. illustrative element에는 original generated 또는 적절히 licensed된 transparent PNG cutout을 사용한다. 간단한 authored brand mark, interface icon, data graphic, 정당한 Three.js shader canvas는 허용된다.
- 모든 avatar에는 photograph를 쓴다. 제공되었거나 적절히 licensed된 photo를 선호하며, initials, illustrated head, faceless silhouette, 실제 customer/staff/endorser로 제시되는 generated people을 출고하지 않는다.
- interface symbol에는 Iconify의 Solar icon을 사용한다. truthful context의 합법적인 real-company mark에는 Iconify SVG Logo만 쓴다. Logo Ipsum은 명시적으로 공개한 fictional brand specimen에만 쓰고 customer proof에는 쓰지 않는다. 정직한 proof가 없으면 logo wall을 생략한다.
- 의도적인 aspect ratio, crop behavior, alt text, loading behavior, missing-media fallback을 제공한다. generic stock imagery, copied mockup, watermark, narrative 역할이 없는 decorative media를 피한다.

## 3. Hero 구성

- 첫 viewport를 site에서 가장 강하게 authored한 순간으로 만든다. 명확한 message와 CTA에 original imagery, video, pointer-responsive interaction, 정당한 Three.js scene을 결합한다.
- hero를 위해 composed GSAP intro sequence를 만든다. animation이 끝나기 전에도 navigation, primary message, CTA가 읽히고 사용 가능해야 한다.
- pointer effect를 부가적으로 만든다. touch, keyboard, coarse pointer, window blur, visibility change를 지원하고 interface가 불완전한 state로 남지 않게 한다.
- JavaScript, media playback, WebGL, motion을 쓸 수 없어도 완전한 static first frame을 설계한다.

## 4. Motion system 구축

- GSAP를 primary animation system으로 사용한다.
- Lenis와 Locomotive Scroll을 평가하고 site의 유일한 smooth-scroll engine 하나만 선택한다. 둘 다 설치/initialize하지 않는다. 선택한 engine을 GSAP ScrollTrigger에 올바르게 연결하고 media/font 변경 뒤 측정을 refresh하며 cleanup 중 destroy한다.
- prefers-reduced-motion: reduce에서 smooth scrolling과 scrubbed timeline을 bypass한다. animation을 단순히 짧게 하지 말고 final state를 즉시 render한다.
- page를 section별로 choreograph한다. 주요 heading을 절제된 stagger로 word-by-word reveal한 뒤 supporting copy와 media를 sequence한다.
- stagger text의 분리되지 않은 accessible name을 보존한다. decorative split word는 assistive technology에서 숨기며 link나 의미 있는 inline markup을 split하지 않고 JavaScript 없이도 unsplit content가 보이게 한다.
- 간단한 hover, focus, tap state에는 CSS를 사용한다. 정당한 scrubbed/pinned sequence에만 ScrollTrigger를 쓰고 같은 property를 여러 system이 제어하지 않게 한다.

## 5. 목적이 있을 때만 Three.js 추가

- spatial depth, texture transition, displacement, pointer response가 art direction을 실질적으로 지지할 때 Three.js와 custom WebGL shader를 사용한다. 장식적 background noise로 shader를 넣지 않는다.
- canvas는 하나의 분명한 책임을 갖고 semantic content와 control보다 아래에 둔다.
- device pixel ratio를 제한하고 offscreen/document hidden에서 rendering을 멈추며 pointer input을 throttle하고 frame별 allocation을 피한다.
- static poster를 제공하고 reduced motion 또는 WebGL failure에서는 canvas를 완전히 대체한다.
- animation frame, observer, event listener, render target, texture, geometry, material, renderer를 dispose한다. content를 망가뜨리지 않고 context loss를 처리한다.

## 6. Quality bar 충족

- hero-only concept가 아니라 complete semantic page를 만든다. responsive navigation, 일관된 section progression, 구체적 conversion content, final CTA, footer, 해당 시 robust form/control state, 보이는 keyboard focus를 넣는다.
- 분명한 art-directed idea, 기억할 첫 viewport, 절제된 typography/spacing, 의도적인 image crop, authored transition, 다듬어진 hover/focus/active/loading/disabled/error/touch/reduced-motion behavior를 요구한다.
- responsive media, below-the-fold lazy loading, bounded transform, 제한된 blur, capped canvas work, 지속적으로 animation하는 offscreen content 부재로 performance를 보존한다.
- generic gradient blob, 장식적 bento grid, 모든 곳의 glass, stock component layout, fake testimonial, invented partnership, logo-wall theater, narrative 역할 없는 motion을 거절한다.
- 사용자가 검증 가능한 evidence를 제공하지 않는 한 결과를 award-winning 또는 Awwwards-recognized라고 설명하지 않는다.

## 7. Handoff 전 validate

- production build를 실행하고 모든 failure를 고친다.
- browser validation이 요청됐거나 blocker를 해결하는 데 필요하면 desktop/mobile size에서 page를 확인한다.
- keyboard navigation, visible focus, touch behavior, JavaScript 없이 content, static media fallback, prefers-reduced-motion behavior를 verify한다.
- smooth-scroll engine이 하나만 설치/initialize됐고 ScrollTrigger integration이 정확하며 animation/WebGL resource가 모두 cleanup되는지 확인한다.
- rendered content와 source에서 placeholder, copied reference identity, unsupported claim, misleading logo, uncredited media, inaccessible split text를 search한다.
- 선택한 web-design skill, asset source, motion stack, Three.js 결정, 수행한 validation, 남은 limitation을 보고한다.
