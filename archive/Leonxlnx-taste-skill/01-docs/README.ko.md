# Taste Skill - 사용 안내 한국어 번역 (운영 관련 발췌)

> 번역 범위: 원본 README의 제품 소개, 설치, 스킬 선택, 설정, 연구/FAQ/라이선스 구간이다. 스폰서 표와 이미지 마크업은 사용·운영 계약이 아니므로 번역 대상에서 제외했다. 원문 전체 위치는 [E02][E03][E04]다.

## Taste Skill

AI 에이전트가 만든 인터페이스를 위한 휴대 가능한 **Agent Skills**다. 보일러플레이트처럼 보이는 UI 대신 더 나은 레이아웃, 타이포그래피, 모션, 간격을 목표로 한다. 이 저장소에는 참조 보드(웹, 모바일, 브랜드 키트)를 만드는 **이미지 생성 스킬**도 포함한다. ChatGPT Images 같은 생성기와 함께 사용한 뒤, 생성된 프레임을 Codex, Cursor, Claude Code에 전달해 구현할 수 있다.

## 설치

[`npx skills add`](https://github.com/vercel-labs/agent-skills) CLI는 이 저장소의 `skills/` 폴더를 스캔하므로 코드형과 이미지 생성형 스킬 모두 같은 방식으로 설치한다고 원문은 안내한다.

```bash
npx skills add https://github.com/Leonxlnx/taste-skill
```

폴더명이 아니라 SKILL frontmatter의 `name:` 값인 **설치 이름**으로 스킬 하나만 설치할 수도 있다.

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
```

어떤 `SKILL.md`든 프로젝트에 복사하거나 ChatGPT / Codex 대화에 붙여 넣을 수도 있다고 안내한다. 이 저장소는 외부 CLI 구현을 포함하지 않으므로 위 설치 명령의 실제 현재 동작은 이 아카이브에서 검증하지 않았다.

### 이전 버전에서 업데이트

기본 `taste-skill`(설치 이름 `design-taste-frontend`)은 현재 **v2 (experimental)**다. 이미 v1을 설치했다면 같은 명령을 다시 실행해 업그레이드하라고 안내한다.

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
```

정확히 v1의 동작에 의존한다면 다음 설치 이름으로 고정한다.

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend-v1"
```

설치 이름은 바뀌지 않았으며 최신 `SKILL.md`가 기존 파일을 대체한다는 설명이지만, 실제 업데이트 충돌·되돌리기는 외부 CLI 범위라 미검증이다.

## 스킬

각 스킬은 하나의 일을 하므로 한 번에 모두 쓸 필요는 없다. **구현 스킬**은 코드를 산출하고, **이미지 생성 스킬**은 참조 이미지만 산출한다.

| 폴더 | 설치 이름 | 한국어 설명 |
| --- | --- | --- |
| `taste-skill` | `design-taste-frontend` | v2 experimental 기본값. brief를 읽어 디자인 언어를 추론하고 VARIANCE / MOTION / DENSITY 다이얼을 조정한다. |
| `taste-skill-v1` | `design-taste-frontend-v1` | 정확한 하위 호환성이 필요할 때만 쓰는 기존 v1. |
| `gpt-tasteskill` | `gpt-taste` | GPT/Codex용으로 더 강한 레이아웃 다양성과 GSAP 방향을 둔 변형. |
| `image-to-code-skill` | `image-to-code` | 사이트 참조 이미지를 생성하고 분석한 뒤 프런트엔드를 맞추어 구현하는 파이프라인. |
| `redesign-skill` | `redesign-existing-projects` | 기존 프로젝트 UI를 먼저 감사한 뒤 개선한다. |
| `soft-skill` | `high-end-visual-design` | 차분한 대비, 여백, 프리미엄 폰트, 스프링 모션을 쓰는 부드러운 고급 UI. |
| `output-skill` | `full-output-enforcement` | 모델이 일부만 출력하거나 placeholder로 생략하는 것을 막는 지시. |
| `minimalist-skill` | `minimalist-ui` | 편집 디자인형 제품 UI, 절제된 팔레트, 선명한 구조. |
| `brutalist-skill` | `industrial-brutalist-ui` | 스위스 타이포그래피, 강한 대비, 실험적 레이아웃의 기계적 언어. |
| `stitch-skill` | `stitch-design-taste` | Google Stitch 호환 `DESIGN.md` 규칙 생성. |
| `imagegen-frontend-web` | `imagegen-frontend-web` | 웹페이지 섹션별 참조 이미지만 생성한다. |
| `imagegen-frontend-mobile` | `imagegen-frontend-mobile` | 모바일 화면·흐름 참조 이미지만 생성한다. |
| `brandkit` | `brandkit` | 로고 방향, 팔레트, 타이포그래피, 아이덴티티 적용을 담은 브랜드 키트 보드 이미지만 생성한다. |

### 어떤 것을 써야 하나?

- 가장 안전한 일반 기본값은 `taste-skill`이다. 단, v2 experimental임을 고려한다.
- 기존 v1 동작을 고정해야 하면 `taste-skill-v1`을 쓴다.
- GPT/Codex 중심의 엄격한 규칙은 `gpt-taste`를 쓴다.
- 이미지 → 분석 → 코드 흐름이면 `image-to-code-skill`, 기존 코드베이스 개선이면 `redesign-skill`을 쓴다.
- 이미지가 최종 산출물이라면 웹은 `imagegen-frontend-web`, 모바일은 `imagegen-frontend-mobile`, 아이덴티티 보드는 `brandkit`을 쓴 뒤 구현 에이전트에게 전달한다.

## Settings (`taste-skill`만)

파일 위쪽의 1-10 숫자는 다음 다이얼이다.

- **DESIGN_VARIANCE**: 레이아웃 실험 수준. 낮으면 가운데 정렬·정돈, 높으면 비대칭·현대적이다.
- **MOTION_INTENSITY**: 애니메이션 깊이. 낮으면 hover, 높으면 scroll/magnetic 같은 상호작용이다.
- **VISUAL_DENSITY**: 뷰포트당 정보량. 낮으면 여유롭고, 높으면 밀도 높은 대시보드에 가깝다.

## Research / FAQ / License

스킬을 만든 배경 글은 `research/`에 있고, README는 주요 코딩 에이전트와 프레임워크에 구애받지 않는다고 설명한다. 이 주장은 호환성 시험 결과가 아니라 README의 주장이다. 라이선스 표기는 MIT이며 저작권 표기는 2026 Leonxlnx다.
