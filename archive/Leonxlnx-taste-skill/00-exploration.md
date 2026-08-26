# 탐색 기록

## 탐색 범위

고정 SHA `72e299530e2eb31ed8da06181bc19f6c18a00821`의 Git 트리를 재귀 조회했다. 일반 파일은 64개였고, 중심 경로는 `README.md`, `.claude-plugin/`, `skill.sh`, `skills/*/SKILL.md`, `skills/llms.txt`, `research/`, `CHANGELOG.md`다. 이미지·로고·렌더 예시와 README 자산 처리 스크립트는 실행 계약을 늘리지 않아 제외했다.

## 실제로 연 파일

- 안내/설치: `README.md` (설치, 스킬 목록, 사용 구분), `CHANGELOG.md` (v2 experimental과 v1 호환성 설명)
- 등록 정보: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `skill.sh`, `skills/llms.txt`
- 스킬 정의: `skills/` 아래 13개 `SKILL.md`의 frontmatter, 목적, 핵심 절차·출력 규칙·체크 섹션. 가장 긴 정의는 필요한 핵심 절만 읽었다.
- 보조 문서: `skills/stitch-skill/DESIGN.md`, `research/README.md`, `research/laziness/README.md`, 연구의 참조 프롬프트 및 실험 결과 문서 각 1개.

## 확인된 구조와 진입점

**확인된 사실.** 이 커밋에는 서비스 서버, 웹 앱, 패키지 매니페스트, 테스트, CI workflow가 없다. 따라서 런타임 실행 진입점은 확인되지 않는다. 저장소가 직접 제공하는 진입점에 가장 가까운 것은 다음 두 가지다.

1. 사용자가 `npx skills add https://github.com/Leonxlnx/taste-skill` 또는 특정 frontmatter `name`으로 설치하라고 안내하는 README. 이 CLI의 실제 스캔/설치 구현은 저장소 밖이다. [E03]
2. 로컬에서 source하는 경우 스킬 이름을 경로로 echo하는 `skill.sh` 레지스트리. 이 스크립트는 스킬을 로드·실행하지 않고 경로만 반환한다. [E05]

## 기술 스택과 외부 경계

**확인된 사실.** 콘텐츠는 Markdown 지시문과 JSON 플러그인 메타데이터다. 지시문은 생성 대상에서 React/Next.js, Tailwind, Motion/GSAP, CSS 등을 권고하거나 특정 디자인 시스템을 참조하지만, 이것은 이 저장소의 런타임 의존성이 아니다. [E09][E10]

**추론.** 실제 실행자는 SKILL.md를 읽는 Codex/Cursor/Claude 같은 에이전트 또는 `npx skills` 호환 도구다. 이 저장소는 그 실행자에 프롬프트 계약을 제공하는 콘텐츠 레이어다. 이는 README의 설치 방식과 소스 트리의 부재를 함께 근거로 한 해석이다. [E03][E05][E08]

외부 경계는 (a) 설치 CLI, (b) 모델/코딩 에이전트, (c) 이미지 생성 가능 환경, (d) 스킬 지시가 권하는 라이브러리·디자인 시스템이다. 토큰, API 키, 네트워크 요청, 데이터베이스, 파일 저장의 실제 구현은 고정 트리에서 찾지 못했다.

## 확인된 핵심 흐름

1. 사용자는 일반 프런트엔드, 기존 프로젝트 리디자인, 이미지 우선 웹 구현, 웹/모바일 참조 이미지, 브랜드 보드, Stitch용 DESIGN.md 등 작업에 맞는 스킬을 선택한다. [E03][E08]
2. 에이전트는 스킬에 정의된 입력 해석·금지 패턴·산출물 수·품질 체크를 적용한다. 기본 `taste-skill` v2는 brief reading과 3개 다이얼을 먼저 요구한다. [E09][E12]
3. 코드형 스킬은 구현 코드 또는 DESIGN.md를 목표로 하고, 이미지형 스킬은 이미지/화면 세트를 목표로 한다. 다만 이 결과물은 스킬 본문이 아니라 실행 모델이 생성한다. [E03][E16][E19]
4. `image-to-code`는 이미지 생성 가능 시 참조 이미지를 먼저 만들고 분석한 다음 그 이미지에 맞추어 코드를 구현하라는 별도 2단계 계약을 둔다. [E15]

## 미확인 범위

- 각 스킬의 자동 트리거 규칙, 실제 설치 디렉터리, 충돌 처리, 업데이트/제거, 버전 호환성
- 생성 모델, 이미지 생성 도구, 권한, 비용, 보존 정책, 텔레메트리
- `DESIGN.md`의 Google Stitch 실제 수용 여부 및 Stitch MCP 연결
- README가 언급한 지원 프레임워크 전체에서의 정상 실행, 생성물의 테스트/CI/Lighthouse 결과

근거 상태는 `확인된 사실`, `추론`, `미확인`을 엄격히 구분했다. 세부 근거는 [06-source-evidence.md](06-source-evidence.md)를 본다.
