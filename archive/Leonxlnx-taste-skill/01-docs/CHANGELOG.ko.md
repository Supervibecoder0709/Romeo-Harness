# 변경 기록 한국어 번역 (v2 및 호환성 범위)

> 번역 범위: `CHANGELOG.md` 1-111행. 이후 내용은 이 아카이브의 핵심 의사결정(기본 버전·호환성)에 직접 영향을 주지 않아 열람하지 않았다. [E07]

## 변경 기록

저장소는 SemVer와 비슷한 규율을 따른다고 설명한다. 실험적 사전 릴리스는 자유롭게 반복하고, 안정 릴리스는 API를 고정한다.

### Unreleased

- `taste-skill`(설치 이름 `design-taste-frontend`)은 이제 **v2 (experimental)**다.
- 이전 v1은 `taste-skill-v1`(설치 이름 `design-taste-frontend-v1`)으로 보존된다.

### v2 (experimental) - 새 기본 `taste-skill`

v2는 기존 taste-skill을 크게 다시 쓴 버전이다. `DESIGN_VARIANCE`, `MOTION_INTENSITY`, `VISUAL_DENSITY`라는 다이얼 철학은 유지하되, 에이전트가 실제로 따를 수 있는 구조·강제 규칙·구체 구현 패턴을 추가했다고 설명한다.

이 버전은 **사전 릴리스**다. 새 기본 설치값이지만 계속 개선 중이며, 설치 이름·다이얼 이름·섹션 구조는 v2.0.0 stable에서 안정화될 예정이라고 적혀 있다.

새 항목은 brief inference, 실제 디자인 시스템과 미적 스타일의 구분, 다크 모드 프로토콜, 리디자인 모드 판별과 사전 감사, 블록 라이브러리 계약, 범위 밖 목록, 최종 사전 점검표다. 또 em dash, 섹션 번호 eyebrow, 장식용 버전 표기·스크롤 안내·가짜 제품 UI 같은 “AI tell”을 금지하고, 색·형상·CTA 대비·hero·레이아웃 반복·motion·reduced motion 규칙을 강화했다고 설명한다.

Motion 라이브러리는 `motion/react`을 권장하고 `framer-motion`은 레거시 alias로 둔다. Tailwind v4가 기본이며 v3는 기존 프로젝트가 요구할 때만 쓴다고 명시한다.

### 호환성 판단

v2는 기본값이지만 실험적이다. 기존 결과의 정확한 재현이 제품 요구사항이면 v1 설치 이름을 명시적으로 pin하는 편이 안전하다. 반대로 새 작업이고 brief inference·사전 점검·리디자인 안전장치가 필요하면 v2가 문서상 권장 경로다. 이 판단은 CHANGELOG의 설명에 근거한 운영 추천이며 실제 CLI pin/rollback은 검증하지 않았다.
