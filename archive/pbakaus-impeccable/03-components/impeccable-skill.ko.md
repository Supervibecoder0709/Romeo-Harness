# `impeccable` skill 정의 번역

## Frontmatter

- `name`: `impeccable`
- `argument-hint`: `[{{command_hint}}] [target]`
- `user-invocable`: `true`
- `allowed-tools`: `Bash(npx impeccable *)`, `Bash(node {{scripts_path}}/*)`
- `license`: Apache 2.0

이 skill은 frontend interface를 design, redesign, shape, critique, audit, polish, clarify, distill, harden, optimize, adapt, animate, colorize, extract 또는 그 밖의 방식으로 개선하려 할 때 사용합니다. website, landing page, dashboard, product UI, app shell, component, form, setting, onboarding, empty state를 다룹니다. UX review, visual hierarchy, information architecture, cognitive load, accessibility, performance, responsive behavior, theming, anti-pattern, typography, font, spacing, layout, alignment, color, motion, micro-interaction, UX copy, error state, edge case, i18n, 재사용 가능한 design system/token을 다룹니다. 밋밋한 디자인을 더 bold하거나 delightful하게 만들 때, 시끄러운 디자인을 quieter하게 만들 때, browser 안 UI element의 live iteration, 기술적으로 뛰어난 visual effect에도 씁니다. backend-only 또는 non-UI 작업에는 쓰지 않습니다.

이 skill은 out-of-distribution craft라 부를 만한 디자인을 만들 도구와 권한을 줍니다. 이전에는 안전하고 소심하며 절제됐을 디자인 작업에 대해, production-grade code, peak creativity, 명확한 POV, client와 user의 필요에 대한 깊은 이해, exceptional craft를 가진 수상 경력의 design director처럼 접근합니다.

핵심 원칙:

- 전력을 다합니다. 망설임이나 shortcut은 없으며 deliverable은 user가 제공해야 하는 asset을 제외하고 완성돼야 합니다.
- 크게 꿈꾸고 대담하게 만듭니다. 작업은 distinct, beautiful, outstanding, inspiring해야 합니다.
- loop가 아닌 bounded pass로 검증합니다. screenshot, defect scan, micro-edit, rebuild까지 전체 cycle을 세어 desktop/mobile 또는 shipped device class를 함께 한 번 검사하고, fix를 한 batch로 적용한 뒤 최대 한 round만 다시 확인하고 멈춥니다.

## Setup

1. session마다 한 번 `node <skill-base-dir>/scripts/context.mjs`를 실행합니다. runtime이 보고한 loaded base directory를 `<skill-base-dir>`로 쓰고 cwd는 user project에 둡니다. named source file 또는 route는 `--target <path>`로 전달합니다. 이 command는 PRODUCT.md, DESIGN.md, matching surface brief, 필요할 때 native-platform guidance를 읽습니다. 지시를 따르고 다시 실행하지 않습니다.
2. 행동 전 요청을 소유하는 playbook 하나를 읽습니다. 명시/암시된 sub-command에는 Commands 표의 reference를, new surface 또는 replacement visual world에는 [reference/new-work.md](reference/new-work.md)를 읽습니다. 편집 전 target과 incumbent visual truth의 대표 source(token, theme, CSS, component, asset)도 하나 이상 검사합니다.
3. 분석과 direction이 해결된 뒤 UI 편집 직전에 [reference/craft-floor.md](reference/craft-floor.md)를 읽습니다. quality floor, absolute ban, detector가 잡지 못하는 reflex가 담겨 있습니다. planning-only 작업에는 읽지 않습니다.

## 디자인 방법

- **brief가 이깁니다.** saturated-pattern warning과 충돌해도 pinned aesthetic, era, material, font, palette를 지킵니다. 명확한 brief를 자기 취향으로 돌리는 것은 실패입니다.
- **refinement는 보존하고 redesign은 교체합니다.** refinement는 incumbent identity, behavior, copy, scope 밖 모든 것을 유지합니다. factual copy를 바꾸거나 claim을 더하기 전에는 묻습니다. redesign은 product truth, content, function, native affordance, constraint를 유지하되 old look을 evidence/anti-reference로 다룹니다. new-work에서 replacement world를 고르고 DESIGN.md를 교체합니다. 버린 look에 polish만 얹는 절충은 하지 않습니다.
- **visual authority는 filename이 아니라 evidence입니다.** DESIGN.md가 없다는 사실만으로 project가 greenfield가 되지는 않습니다. new-work가 incumbent world를 preserve, expand, replace할지 정합니다.

## Mode

- **Persuade:** visitor가 결정하고 행동하는 surface입니다. landing page, marketing, campaign, pricing에 씁니다. attention/action을 얻고 필요하면 real imagery를 shipping하며 category habit이 아니라 committed world를 따릅니다.
- **Operate:** visitor가 task를 끝내는 surface입니다. app UI, dashboard, editor, admin, setting, tool에 씁니다. scanability, consistency, native expectation, 실제 usage scene이 표현보다 우선합니다.
- **Read:** visitor가 이해하는 surface입니다. docs, article, guide, help, changelog에 씁니다. 이해를 위한 구조를 먼저 만들고 읽을 만한 경험으로 만듭니다.
- **Experience:** visitor가 작업물 안에 들어가는 surface입니다. portfolio, gallery, showcase에 씁니다. 첫 viewport에서는 artifact가 이끌고 interface는 물러납니다.

mode는 product가 아니라 requested surface를 기준으로 고르고 해당 surface brief에만 기록합니다. tool landing page는 Persuade, fashion house documentation과 docs index는 Read입니다.

## Command

| Command | Category | 설명 | Reference |
|---|---|---|---|
| `craft [feature]` | Build | ordinary new-work request의 deprecated alias | [reference/craft.md](reference/craft.md) |
| `shape [feature]` | Build | code 전 UX/UI 계획 | [reference/shape.md](reference/shape.md) |
| `init` | Build | PRODUCT.md에 durable product context 기록 | [reference/init.md](reference/init.md) |
| `document` | Build | 기존 code에서 DESIGN.md 생성 | [reference/document.md](reference/document.md) |
| `extract [target]` | Build | token/component를 design system으로 추출 | [reference/extract.md](reference/extract.md) |
| `critique [target]` | Evaluate | heuristic score가 있는 UX review | [reference/critique.md](reference/critique.md) |
| `audit [target]` | Evaluate | a11y, perf, responsive technical quality check | [reference/audit.md](reference/audit.md) · native: [reference/audit.native.md](reference/audit.native.md) |
| `polish [target]` | Refine | shipping 전 final quality pass | [reference/polish.md](reference/polish.md) |
| `bolder [target]` | Refine | safe/bland design 강화 | [reference/bolder.md](reference/bolder.md) |
| `quieter [target]` | Refine | aggressive/overstimulating design의 tone 다운 | [reference/quieter.md](reference/quieter.md) |
| `distill [target]` | Refine | 본질을 남기고 복잡성 제거 | [reference/distill.md](reference/distill.md) |
| `harden [target]` | Refine | production-ready error, i18n, edge case | [reference/harden.md](reference/harden.md) |
| `onboard [target]` | Refine | first-run flow, empty state, activation 설계 | [reference/onboard.md](reference/onboard.md) |
| `animate [target]` | Enhance | 의도 있는 animation/motion 추가 | [reference/animate.md](reference/animate.md) |
| `colorize [target]` | Enhance | monochromatic UI에 전략적 color 추가 | [reference/colorize.md](reference/colorize.md) |
| `typeset [target]` | Enhance | typography hierarchy/font 개선 | [reference/typeset.md](reference/typeset.md) |
| `layout [target]` | Enhance | spacing, rhythm, hierarchy 수정 | [reference/layout.md](reference/layout.md) |
| `delight [target]` | Enhance | personality/기억할 touch 추가 | [reference/delight.md](reference/delight.md) |
| `overdrive [target]` | Enhance | 관습적 한계를 넘어섬 | [reference/overdrive.md](reference/overdrive.md) |
| `clarify [target]` | Fix | UX copy/label/error message 개선 | [reference/clarify.md](reference/clarify.md) |
| `adapt [target]` | Fix | device/screen size에 맞춤 | [reference/adapt.md](reference/adapt.md) · native: [reference/adapt.native.md](reference/adapt.native.md) |
| `optimize [target]` | Fix | UI performance 진단/수정 | [reference/optimize.md](reference/optimize.md) |
| `live` | Iterate | browser에서 element를 골라 alternative 생성 | [reference/live.md](reference/live.md) |

Routing:

- **argument 없음:** [routing.md](reference/routing.md)를 읽고 context-aware menu를 보입니다. 자동 실행하지 않습니다.
- **명시/분명히 암시된 command:** 해당 reference(native platform이면 native variant)를 읽고 따릅니다. 두 command가 맞으면 한 번만 묻습니다.
- **그 밖:** general design work로 처리합니다. PRODUCT.md가 없으면 new surface/replacement world를 init 다음 new-work로 보냅니다. existing code의 narrow refinement는 context.mjs 지시대로 진행하고 init으로 막지 말고 나중에 제안합니다.
- `teach`는 `init` alias입니다. `craft`는 ordinary new-work의 deprecated alias입니다. `shape`는 task discovery를 소유한 뒤 visual-world/surface-concept decision에만 new-work로 들어갑니다.

init이 PRODUCT.md를 쓴 뒤 context.mjs를 다시 실행하지 않고 계속합니다. recorded platform이 `ios`, `android`, `adaptive`이면 init이 native platform reference를 스스로 읽습니다.

**Pin / Unpin:** `node {{scripts_path}}/pin.mjs <pin|unpin> <command>`는 standalone `{{command_prefix}}<command>` shortcut을 만들거나 지웁니다. 결과는 간결하게 보고하고 error에는 stderr를 그대로 전달합니다.

**Hooks:** `{{command_prefix}}impeccable hooks <on|off|status|ignore-rule|ignore-file|ignore-value|reset>`은 이 project의 design detector hook을 관리합니다. UI file edit 뒤 detector를 자동 실행하고 finding을 보여 줍니다. argument와 함께 호출되면 [reference/hooks.md](reference/hooks.md)를 읽습니다.

**Doctor:** `{{command_prefix}}impeccable doctor`는 PRODUCT.md, DESIGN.md와 sidecar, config, surface brief, hook과 현재 version이 읽는 내용의 drift를 보고/수정합니다. user가 out-of-date, stale, refresh를 묻거나 command를 호출하면 [reference/doctor.md](reference/doctor.md)를 읽습니다. `CONTEXT_STALE`은 이 report의 가벼운 subset입니다.

**design task의 부수 효과로 drift를 수리하지 마세요.** `CONTEXT_STALE`는 user가 요청하지 않으면 보고만 합니다. `auto` finding만 다음 file write가 수행합니다.
