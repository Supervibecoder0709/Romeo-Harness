# 동봉 보조 Skill 정의 — 한국어 해설 및 원문 위치

이 문서는 주 `ui-ux-pro-max` 이외에 CLI가 sibling으로 설치할 수 있는 6개 보조 Skill의 **정의 파일에서 확인한 activation/입력/상태변경 경계**를 한국어로 옮긴 것이다. 각 전체 원문과 reference/script 목록은 아래 원문 위치에서 확인해야 하며, 이 아카이브에서는 실행하지 않았다. [E17]

| Skill | 언제 쓰는가 | 확인된 입력·처리 | 확인된 출력/상태 변경·주의 |
|---|---|---|---|
| `banner-design` | social/ad/web hero/print banner, cover/header, campaign creative asset | 목적, platform/size, headline/subtext/CTA/logo, brand, art direction, 옵션 수를 수집하고 reference와 UI skill을 사용 | HTML/CSS banner와 `assets/banners/{campaign}/` PNG를 전제. browser research, AI image model, local server/screenshot tool 호출을 지시하므로 외부 접근·파일 쓰기는 별도 승인 대상 |
| `brand` | brand voice, visual identity, messaging, asset 관리·audit, palette/type spec | `docs/brand-guidelines.md`를 기준으로 prompt context 주입, asset validation, color extract/compare, `update` routing | `sync-brand-to-tokens.cjs`가 guideline→`assets/design-tokens.json/css`를 sync한다고 명시. brand source/token을 바꾸므로 검토 없이 실행하면 안 됨 |
| `design-system` | token architecture, component state/spec, CSS variable, Tailwind theme, slide generation | primitive→semantic→component token, token generate/validate, slide CSV 검색/HTML validation | `generate-tokens.cjs`가 CSS 생성, slide flow가 HTML 생성·image fetch를 포함한다고 명시. 산출물 경로와 external image license 확인 필요 |
| `design` | logo/icon/CIP/social photo/slide design | task별 data CSV와 Python search/generate/render script를 사용하도록 정의 | visual asset·HTML 또는 prompt형 산출물을 생성할 수 있음. 정본에는 설치된 external generator 권한/결과 품질 보장이 없음 |
| `slides` | presentation/slide, deck, pitch, report | topic/goal/audience/format을 받은 뒤 strategy/layout/copy/chart data와 slide generation을 사용 | deck HTML/image 또는 presentation asset을 만들 수 있음. published deck·brand claim은 사람이 검토해야 함 |
| `ui-styling` | shadcn, Tailwind, responsive/theme/accessibility styling | component/theme/routing reference와 `shadcn_add.py`, `tailwind_config_gen.py`를 제공 | package/component install 또는 config 생성이 들어갈 수 있음. 기존 Tailwind/shadcn config와 충돌 검토가 필요 |

## 원문에서 확인한 구체 경계

### `banner-design`

- banner만 다루며 video edit, full website design, print production은 다루지 않는다고 정의한다.
- 요구 수집 단계는 원문에서 `AskUserQuestion`을 요구하지만, 호출하는 agent 환경에 따라 이 방식이 동작하지 않을 수 있다. 이 저장소는 그 환경을 제공하지 않는다.
- Pinterest browser research, Gemini Flash/Pro image generation, `chrome-devtools` screenshot, `assets/banners/` output path를 지시한다. 이러한 경로는 network, credentials, image licence, 파일 쓰기라는 추가 권한을 포함한다.

### `brand`

```bash
node scripts/inject-brand-context.cjs
node scripts/inject-brand-context.cjs --json
node scripts/validate-asset.cjs <asset-path>
node scripts/extract-colors.cjs --palette
node scripts/sync-brand-to-tokens.cjs
```

원문은 `docs/brand-guidelines.md`를 source of truth, `assets/design-tokens.json`/`assets/design-tokens.css`를 sync 대상이라고 적는다. `sync`의 변경 범위와 실제 대상 파일은 실행 전 readback해야 한다.

### `design-system`

```text
Primitive (raw values)
       ↓
Semantic (purpose aliases)
       ↓
Component (component-specific)
```

```bash
node scripts/generate-tokens.cjs --config tokens.json -o tokens.css
node scripts/validate-tokens.cjs --dir src/
```

원문은 token generation/validation, `search-slides.py`, slide token validator, Pexels/Unsplash image fetch script를 제공한다고 적는다. 여기서 `generate`와 `fetch`는 읽기 전용 작업이 아니다.

## PM 판단

보조 Skill은 주 검색 엔진과 동일한 안전성 수준으로 묶으면 안 된다. 주 search는 정적 data를 읽는 작업이지만, banner/brand/design-system/design/slides/ui-styling은 이미지 생성·외부 research·설치·sync·config/asset 파일 생성으로 이어질 수 있다. Harness에서는 **계획/검색과 실제 asset·token·config 쓰기를 분리**하고, 생성물 path, overwrite 여부, 외부 API/저작권, 승인자를 입력 계약에 명시하는 것이 적합하다.
