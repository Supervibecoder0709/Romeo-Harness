# Game Development Skill

플레이 가능한 Three.js 및 browser game을 만드는 재사용 workflow다. 이 family는 의도적으로 web-design과 분리되어 있다. gameplay architecture, simulation, combat, content contract, asset integration, performance, QA, release proof를 담당한다.

가장 좁게 맞는 skill부터 시작한다. task가 system boundary를 넘을 때만 skill을 결합한다.

## 올바른 skill 선택

| 필요 | 시작할 skill |
| --- | --- |
| 완전한 playable vertical slice 구축 | [build-isometric-arpg](build-isometric-arpg/SKILL.md) |
| 읽기 쉬운 flat-world route와 동기 있는 lighting 작성 | [author-game-levels](author-game-levels/SKILL.md) |
| camera framing, lock-on, occlusion, touch gesture 구현 | [build-game-camera-controls](build-game-camera-controls/SKILL.md) |
| enemy archetype, moveset, model convention, runtime hook 정의 | [build-threejs-enemy-systems](build-threejs-enemy-systems/SKILL.md) |
| monster joint, socket, collider, animation state, LOD rigging 및 validation | [build-game-monster-system](build-game-monster-system/SKILL.md) |
| enemy perception, intent, spacing, state transition 조정 | [tune-enemy-ai](tune-enemy-ai/SKILL.md) |
| attack timing, contact authority, defense, combat feedback 정의 | [design-action-combat](design-action-combat/SKILL.md) |
| arena, wave, objective, boss phase, reward 구성 | [design-game-encounters](design-game-encounters/SKILL.md) |
| inventory, loot, equipment, persistence 구축 | [build-game-inventory](build-game-inventory/SKILL.md) |
| imported, procedural, generated, 2D asset 선택 및 통합 | [build-hybrid-game-assets](build-hybrid-game-assets/SKILL.md) |
| Vesperfall catalog PNG와 truthful live model review route 연결 | [build-vesperfall-review-assets](build-vesperfall-review-assets/SKILL.md) |
| 읽기 쉬운 visual 또는 audio feedback 추가 | [create-game-vfx](create-game-vfx/SKILL.md) 및 [build-game-audio-feedback](build-game-audio-feedback/SKILL.md) |
| mobile에 맞는 control, HUD, quality, QA 적용 | [build-mobile-threejs-games](build-mobile-threejs-games/SKILL.md) |
| frame-time, draw-call, memory, quality 문제 진단 | [optimize-threejs-games](optimize-threejs-games/SKILL.md) |
| 실제 browser에서 전체 player journey test | [test-playable-web-games](test-playable-web-games/SKILL.md) |
| release package, deploy, verify, document | [ship-web-games](ship-web-games/SKILL.md) |

## Foundation과 world

- [build-isometric-arpg](build-isometric-arpg/SKILL.md) — 하나의 일관된 production-ready action-RPG loop를 vertical slice로 조립한다.
- [author-game-levels](author-game-levels/SKILL.md) — collision/navigation/visual layer를 분리하고 source-motivated lighting을 사용해 평평하고 읽기 쉬운 route를 작성한다.
- [build-game-camera-controls](build-game-camera-controls/SKILL.md) — 읽기 쉬운 isometric, follow, lock-on, occlusion, shake, touch-camera behavior를 만든다.
- [build-mobile-threejs-games](build-mobile-threejs-games/SKILL.md) — mobile control, safe area, responsive HUD, orientation, performance를 주 surface로 다룬다.

## Combat, enemy, encounter

- [design-action-combat](design-action-combat/SKILL.md) — startup, active, recovery, contact authority, defense, interruption, deterministic combat proof를 명세화한다.
- [build-threejs-enemy-systems](build-threejs-enemy-systems/SKILL.md) — 이식 가능한 enemy content, model/rig/collider/socket convention, moveset, runtime hook, fallback, fixture를 정의한다.
- [build-game-monster-system](build-game-monster-system/SKILL.md) — monster마다 구체적인 rig, socket, collider, state, moveset, LOD, deterministic review contract를 강제한다.
- [tune-enemy-ai](tune-enemy-ai/SKILL.md) — 공정하고 범위가 정해져 재현 가능한 perception, intent, navigation, spacing, attack decision을 만든다.
- [design-game-encounters](design-game-encounters/SKILL.md) — arena, enemy role, spawn pacing, hazard, objective, boss phase, failure recovery, reward를 구성한다.

## Player system과 feedback

- [build-game-inventory](build-game-inventory/SKILL.md) — atomic inventory, loot, equipment, drag/drop, migration, no-loss persistence flow를 만든다.
- [create-game-vfx](create-game-vfx/SKILL.md) — 읽기 쉽고 범위가 정해지며 pool을 사용하고 reduced-motion을 고려한 gameplay effect를 만든다.
- [build-game-audio-feedback](build-game-audio-feedback/SKILL.md) — player intent와 combat state를 우선순위화되고 접근 가능한 browser-safe audio cue로 연결한다.

## Asset, performance, QA, release

- [build-hybrid-game-assets](build-hybrid-game-assets/SKILL.md) — 올바른 runtime representation을 고르고 provenance, scale, socket, collision, budget을 보존한다.
- [build-vesperfall-review-assets](build-vesperfall-review-assets/SKILL.md) — transparent catalog reference와 truthful live model preview, provenance, grounding, deterministic review route를 연결한다.
- [optimize-threejs-games](optimize-threejs-games/SKILL.md) — control 또는 combat readability를 희생하지 않고 representative encounter를 측정하고 개선한다.
- [test-playable-web-games](test-playable-web-games/SKILL.md) — desktop, touch, save, retry, accessibility 전반의 deterministic state와 complete player journey를 검증한다.
- [ship-web-games](ship-web-games/SKILL.md) — 정확히 검증된 commit을 release하고 deployed game을 local readiness와 별도로 증명한다.

## 중요한 경계

- build-threejs-enemy-systems는 이식 가능한 enemy content와 runtime orchestration을 정의하고, build-game-monster-system은 개별 rig/animation conformance를 담당하며, tune-enemy-ai는 enemy가 무엇을 할지 결정한다.
- design-action-combat은 개별 combat verb와 outcome을 정의하고, design-game-encounters는 이를 pressure와 pacing으로 구성한다.
- build-hybrid-game-assets는 asset representation을 선택/통합하고, build-vesperfall-review-assets는 Vesperfall catalog와 live-preview truth를 증명하며, create-game-vfx와 build-game-audio-feedback은 gameplay state를 전달한다.
- test-playable-web-games는 player experience를 증명하고, ship-web-games는 release sequence와 production read-back을 담당한다.
