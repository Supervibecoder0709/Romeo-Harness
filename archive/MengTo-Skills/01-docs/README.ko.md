# 에이전트 스킬

Codex, Claude, Cursor 및 기타 AI 코딩 에이전트를 사용하는 디자이너와 빌더를 위한, 풍부한 사용자 인터페이스, 플레이 가능한 게임, 프런트엔드 시스템, 에이전트 루프, 자동화, 재사용 가능한 워크플로우를 만드는 agent skill 엄선 모음이다.

![Aura Build super prompt workflow](assets/aura-build-superprompt.gif)

이 skill을 Codex, Claude Design, [Aura Build](https://aura.build), Lovable 및 나머지 agent stack과 함께 사용해 reference를 prompt로 바꾸고, 상세한 landing page를 생성하고, 플레이 가능한 Three.js system을 만들고, 재사용 가능한 implementation workflow를 구축한다.

대표 web-design workflow부터 시작한다.

1. **[Video to Super Prompt](agent-skills/codex/video-to-superprompt/SKILL.md)**
   design, landing page, animation의 screen recording을 Fable 5가 one-shot HTML에 사용할 수 있는 매우 상세한 prompt로 바꾼다.
2. **[HTML to Interaction Prompts](agent-skills/codex/html-to-interaction-prompts/SKILL.md)**
   Aura Build page 같은 기존 HTML page를 한 section, 한 animation, 한 button, 한 hover state, 한 WebGL effect에 쓸 수 있는 재사용 prompt로 바꾼다.
3. **[Stitched Full Page Capture](agent-skills/codex/stitched-full-page-capture/SKILL.md)**
   hero만이 아니라 전체 landing page를 capture해 agent에게 structure, pacing, visual hierarchy의 full-page reference를 제공한다.
4. **[Daily UI Inspiration](agent-skills/codex/daily-ui-inspiration-capture/SKILL.md)**
   browsing, capture, reference study, prompt generation을 결합해 강한 landing page를 상세 prompt pack으로 바꾸는 유용한 agent loop를 만든다.

이는 이식 가능한 agent skill folder다. 간결한 SKILL.md playbook에 선택적으로 references, articles, scripts, assets를 붙인다. 좋은 prompt, workflow, style system, capture recipe, debugging habit을 agent가 load하고 따를 수 있는 versioned file로 바꾸는 것이 목표다.

기본적으로 이식 가능하다. 사용자가 local agent instruction을 통해 project-specific context를 주지 않는 한 각 skill은 어떤 사용자, repo, workspace에서도 작동해야 한다.

[실행 가능한 모든 demo와 recreation prompt](DEMOS.md)를 둘러본다.

다음이 필요할 때 이 skill을 사용한다.

- 반복 가능한 design direction
- 재사용 가능한 game architecture와 gameplay QA
- 절차적인 implementation 단계
- copy/paste snippet
- 흔한 함정과 guardrail
- 일회성 chat answer 대신 재사용 가능한 workflow

---

## 에이전트 지원

형식은 의도적으로 plain Markdown 및 folder 기반이다.

- **Codex**: 행동 전에 관련 SKILL.md를 load한다. repo behavior는 AGENTS.md에 두며, 이 repo의 browser 작업은 Codex browser를 사용해야 한다.
- **Claude Code**: CLAUDE.md에서 관련 skill을 참조하거나 Claude skills setup으로 복사하거나 SKILL.md를 working context로 직접 연다.
- **Cursor**: Cursor rules나 chat context에서 특정 skill folder를 가리킨다. 재사용 snippet, constraint, default를 쉽게 붙여 넣을 수 있게 유지한다.
- **기타 에이전트**: 같은 계약을 사용한다. 가장 좁게 맞는 skill부터 읽고 그 단계와 연결 reference를 따른다.

---

## 철학

### 1) Prompt는 asset이다

한 번 좋았다면 재사용 가능해야 한다.

- prompt를 file로 저장한다.
- version을 관리한다.
- library와 stylecard를 만든다.

### 2) Spec이 감보다 낫다

일관된 output으로 가는 가장 빠른 길은 다음이다.

- 명확한 constraint
- 명확한 hierarchy
- 한 번에 1~2개만 바꾸는 iteration

### 3) Paragraph보다 reference가 낫다

screenshot과 example은 다음을 담는다.

- font, spacing, color
- layout rhythm
- icon style

### 4) Skill은 표준작업절차다

좋은 skill은 agent에게 언제 사용해야 하는지, 무엇을 먼저 해야 하는지, 어떤 default를 적용할지, 어떤 실수를 피해야 하는지를 정확히 알려 준다.

---

## Repo 구조

~~~txt
agent-skills/
  codex/
    audit-verify-explain-grade-5/
      SKILL.md
    build-daily-inspiration-sites/
      SKILL.md
    daily-ui-inspiration-capture/
      SKILL.md
  game-development/
    README.md
    build-isometric-arpg/
      SKILL.md
    author-game-levels/
      SKILL.md
    design-action-combat/
      SKILL.md
    build-threejs-enemy-systems/
      SKILL.md
    build-game-monster-system/
      SKILL.md
    build-vesperfall-review-assets/
      SKILL.md
    test-playable-web-games/
      SKILL.md
  media/
    aura-asset-images/
      SKILL.md
    unsplash-asset-images/
      SKILL.md
  ui/
    design-first-ui-prompting/
      SKILL.md
      ARTICLE.md
      REFERENCES.md
  web-design/
    add-shader-cursor-trail/
      SKILL.md
    build-awwwards-quality-sites/
      SKILL.md
    pricing-page/
      SKILL.md
      REFERENCES.md
    landing-page/
      SKILL.md
      REFERENCES.md
    gsap/
      SKILL.md
      REFERENCES.md
    threejs/
      SKILL.md
      REFERENCES.md
    tailwindcss/
      SKILL.md
      REFERENCES.md
    matterjs/
      SKILL.md
    globe-gl/
      SKILL.md
    css-border-gradient/
      SKILL.md
    progressive-blur/
      SKILL.md
    animation-on-scroll/
      SKILL.md
    css-alpha-masking/
      SKILL.md
    vantajs/
      SKILL.md
      REFERENCES.md
    cobejs/
      SKILL.md
      REFERENCES.md
    unicorn-studio/
      SKILL.md
      REFERENCES.md
~~~

Folder 계약:

~~~txt
agent-skills/<category>/<skill-name>/
  SKILL.md            # 필수: frontmatter + workflow
  REFERENCES.md       # 선택: link만
  ARTICLE.md          # 선택: 긴 설명
  assets/             # 선택: 이미지, template, example
  scripts/            # 선택: helper script
  demo/               # 선택: visual 또는 interaction proof
    index.html         # 독립형 HTML, CSS, JavaScript
    PROMPT.md          # 정확한 recreation 및 remix prompt
    assets/            # 필요한 경우 local demo asset
~~~

관례:

- SKILL.md는 agent가 load하여 따르는 skill이다.
- REFERENCES.md는 link만 담는다. SKILL.md를 가볍게 유지한다.
- visual 및 interaction skill은 이식 가능한 demo/index.html과 demo/PROMPT.md를 포함할 수 있다.
- workflow skill은 proof를 실질적으로 개선할 때 가상의 demo/input.md 및 demo/expected-output.md handoff를 포함할 수 있다.
- skill은 백과사전식이 아니라 절차적이어야 한다. 단계, pattern, guardrail을 쓴다.
- 모호한 표현보다 Use when 같은 명시적 trigger를 선호한다.
- duration, spacing, hierarchy, command, acceptance check에 default를 둔다.

---

## 현재 라이브러리

이 snapshot에는 다섯 category에 걸쳐 **123개 skill**이 포함돼 있다.

source of truth에는 다음을 사용한다.

~~~bash
find agent-skills -name SKILL.md | sort
~~~

### Codex workflow (19)

반복 가능한 Codex 작업을 위한 operational skill:

- article-prompts-to-skills - article과 prompt pack을 focused, validated skill package로 바꾼다.
- audit-reference-originality - website를 reference와 비교하고 originality risk를 식별한다.
- audit-verify-explain-grade-5 - 작업을 audit하고 claim을 verify하며 결과를 쉽게 설명한다.
- browser-video-recording - scripted UI scene에서 다듬어진 browser screen-recording video를 render한다.
- build-daily-inspiration-sites - capture한 reference 다섯 개를 original Sites build 다섯 개로 바꾼다.
- daily-ui-inspiration-capture - screenshot, motion, prompt가 포함된 recurring UI inspiration bundle을 만든다.
- elevenlabs-tts - local profile에서 재사용 가능한 ElevenLabs voiceover를 생성한다.
- generate-reference-inspired-brand-worlds - reference grammar를 original brand-world direction으로 바꾼다.
- html-to-interaction-prompts - HTML page를 screenshot-backed interaction prompt article로 바꾼다.
- optimize-web-animations - animation, canvas, WebGL performance cost를 profile하고 줄인다.
- performance-profiling - Instruments, diagnostics, MetricKit을 사용하는 Apple platform profiling.
- stitched-full-page-capture - lazy, animated, WebGL page를 위한 신뢰할 수 있는 full-page screenshot.
- video-to-superprompt - reference video를 상세 recreation prompt로 분석한다.
- web-technique-to-skill - 이미 만든 effect를 재사용 가능한 web-design skill로 바꾼다.
- write-like-meng-on-x - authored voice corpus를 기준으로 간결한 X draft를 보정한다.
- x-bookmark-quote-posts - 최근 X bookmark를 source-backed quote-post draft로 바꾼다.

### Media (2)

이미지 sourcing skill:

- aura-asset-images - stock 스타일의 design/marketing image에 Aura Assets를 사용한다.
- unsplash-asset-images - use case, crop, ratio에 맞는 고품질 Unsplash asset을 고른다.

### UI (1)

#### design-first-ui-prompting

Design-first UI prompting system:

- prompt template: goal → format → layout → type → color → constraint
- reroll보다 variant를 쓰는 workflow
- negative prompt와 guardrail
- 2-pass typography workflow: layout 생성 후 Figma에서 typeset

파일:

- agent-skills/ui/design-first-ui-prompting/SKILL.md
- agent-skills/ui/design-first-ui-prompting/ARTICLE.md

### Game development (20)

플레이 가능한 Three.js 및 browser-game workflow. skill selection table과 system boundary는 [game-development guide](agent-skills/game-development/README.md)를 본다.

Foundation과 world:

- build-isometric-arpg, author-game-levels, build-game-camera-controls, build-mobile-threejs-games

Combat, enemy, encounter:

- design-action-combat, build-threejs-enemy-systems, build-game-monster-system, tune-enemy-ai, design-game-encounters

Player system과 feedback:

- build-game-inventory, create-game-vfx, build-game-audio-feedback

Asset, performance, QA, release:

- build-hybrid-game-assets, build-vesperfall-review-assets, optimize-threejs-games, test-playable-web-games, ship-web-games

### Web design (81)

Conversion과 implementation:

- build-awwwards-quality-sites, landing-page, pricing-page, tailwindcss, animation-systems, webgl-landing-steering

Motion과 scroll:

- animation-on-scroll, cinematic-gsap-lenis-motion-system, cinematic-scroll-storytelling, gsap, gsap-scrolltrigger-storytelling, marquee-loop, masked-reveal, staggered-word-reveal

WebGL, canvas, 3D:

- add-shader-cursor-trail, background-grid-webgl, cobejs, globe-gl, globe-particles, matterjs, threejs, threejs-landscape, threejs-towers, threejs-weather, unicorn-studio, vantajs, webgl-3d-object, webgl-laser

CSS treatment와 detail:

- beautiful-shadows, company-logos, container-lines, corner-diagonals, corner-lasers, css-alpha-masking, css-border-gradient, gooey-blob-system, number-details, progressive-blur, solar-duotone-bold

Layout system:

- agency-grid-layout-minimal, book-serif-index, editorial-tech, framed-grid-layout, image-first-grid-layout, nested-container-frames, split-layout-technical, technical-wireframe-info-layout

Visual style과 page mood:

- atmosphere-background, blue-cloudy-clean-modern, blue-laser-clean-glass-layout, bright-green-tech-system-webgl, clean-minimal-beige-light-mode, dark-blue-contrasting-clean, dark-glass-clean-layout, dither-background, dither-laser-dark-mode, framed-tech-dark-border-gradient, funky-purple-container-tech, glass-dark-mode-clock, glass-dark-ui, high-contrast-skeuomorphic-clean, light-mode-paper-technical, mesh-gradient-dark-blue-clean, nested-container-clean-agency, orange-clean-paper-saas, skeuomorphic-ui, tech-green-dark-mode-modern

추가 interaction, narrative, product system:

- ambient-section-particles, beam-glow-states, documentary-brutalist-agency, editorial-portfolio-chapters, editorial-service-booking, falling-leaves, liquid-metal-border, operational-enterprise-ai, pointer-trail-emitter, product-proof-saas, reveal-hover-effect, scroll-progress-timeline, scroll-scrubbed-visual-sequence, scroll-scrubbed-word-reveal, scroll-world-storytelling, shaders-cursor-ripples, thinking-orbs

---

## 새 skill 추가 방법 (workflow)

1) Folder를 만든다.

~~~text
agent-skills/<category>/<skill-name>/
~~~

2) SKILL.md를 추가한다.

- frontmatter: name, description
- 내용: 언제 사용하는지, workflow, pitfall, recipe, 무엇을 물어볼지

3) visual 또는 interaction proof가 유용하면 portable demo를 추가한다.

- inline CSS와 JavaScript가 있는 demo/index.html
- minimal, recreation, remix prompt가 있는 demo/PROMPT.md
- demo/assets/ 아래의 local file

4) 선택적으로 REFERENCES.md를 추가한다.

- doc link만

5) skill contract를 test한다.

- 명확한 trigger
- 구체적 workflow
- 재사용 가능한 snippet 또는 command
- pitfall 및 acceptance check
- secret나 private client info 없음

6) Commit한다.

- skill별 작은 commit
- 보통 Add skill-name skill 또는 Update skill-name skill 같은 명확한 message

---

## 작성 스타일

- Meng To처럼 쓴다: 훑기 쉽고, 실용적이며, 자신감 있게.
- constraint와 default를 선호한다.
- 군더더기를 피한다.
- 긴 설명은 SKILL.md가 아니라 ARTICLE.md에 둔다.
- reference는 workflow가 아니라 REFERENCES.md에 둔다.

---

## 유지보수 아이디어

- library가 커지면서 category README를 최신으로 유지한다.
- 선호 setup이 안정되면 Codex, Claude Code, Cursor 설치 note를 추가한다.
- required frontmatter의 가벼운 validation을 추가한다.
- imported skill을 이식 가능하게 유지한다: secret, private path, 숨은 account assumption을 두지 않는다.

---

## 저장소

GitHub: https://github.com/MengTo/Skills

Update push:

~~~bash
cd /Users/mengto/clawd/@MengTo/Skills
git push origin main
~~~

---

## License

MIT License. [LICENSE](LICENSE)를 본다.
