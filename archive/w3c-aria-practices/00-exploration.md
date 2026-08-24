# 00. 탐색 기록

## 결론

`w3c/aria-practices`는 서버나 SaaS 애플리케이션이 아니라 WAI-ARIA Authoring Practices Guide(APG)의 정적 HTML 가이드와 동작 가능한 UI 예제를 함께 관리하는 Node.js 기반 콘텐츠 저장소다. `content/`의 패턴 설명·예제 HTML/JS를 작성하고, Node 명령으로 정적 품질 검사·예제 회귀·참조표/coverage 산출물 정합성을 검증하며, `main`의 콘텐츠 변경은 별도 `wai-aria-practices` 레포의 배포 workflow를 호출한다. [S5]-[S18]

## 탐색 방법

1. `repos/w3c/aria-practices` API에서 기본 브랜치 `main`을 받고 `commits/main`의 SHA를 `7e4034b262bc0d25332e330d8a582aaf34113829`로 고정했다.
2. `git/trees/<SHA>?recursive=1`으로 blob 521개를 인벤토리화했다.
3. 안내 문서와 패키지 실행 계약, 대표 콘텐츠·예제, 생성·검사·회귀 테스트, CI와 외부 WAI 연동 workflow를 우선순위로 열었다.
4. README의 운영 설명을 `package.json`, 테스트 진입점, 대표 Accordion 예제, GitHub Actions 설정과 교차 확인했다. [S1]-[S19]

## 실제로 연 파일과 선정 이유

| 파일 | 선정 이유 | 확인 결과 |
| --- | --- | --- |
| `README.md` | 레포 목적, 기여·검증 안내 | APG를 관리하며 공개 URL·기여 순서·로컬 lint/test 명령을 안내한다. [S3] |
| `CONTRIBUTING.md` | 문서 기여의 법적/저작권 경계 | 실질 기여에는 W3C Working Group 참여 또는 저작권 이전이 필요하다고 명시한다. [S4] |
| `package.json`, `.husky/pre-commit` | 실제 Node 실행 계약과 커밋 전 자동화 | lint, link, 회귀, coverage, 참조표 생성 명령과 `lint-staged` 훅을 선언한다. [S5], [S6] |
| `content/apg-home.html` | 사용자가 받는 가이드의 대표 진입 콘텐츠 | 디자인 패턴·동작 예제·기본 실무 지침을 제공한다고 설명한다. [S7] |
| Accordion 패턴/예제 HTML·JS | 문서 → 실행 가능한 예제 → 상태 변화의 대표 경로 | 키보드/ARIA 요구를 문서화하고 클릭 시 `aria-expanded`와 `hidden`을 함께 바꾼다. [S8], [S9] |
| `test/index.js`, Accordion 회귀 테스트 | 실제 브라우저 테스트 진입점과 예제 계약 | Selenium/Geckodriver가 `file://` 예제를 열고 `data-test-id`와 동작·ARIA 속성을 검사한다. [S10], [S11] |
| `scripts/regression-tests.sh`, regression workflow | CI가 바뀐 예제를 선별·분할하는 방식 | 변경 범위에 따라 전체/관련 AVA 테스트를 골라 5개 matrix job으로 실행한다. [S12], [S13] |
| `scripts/{reference-tables,coverage-report}.js`, examples workflow | 파생 HTML/CSV의 생성 및 커밋 정합성 | 콘텐츠에서 역할·속성·예제를 읽어 색인/coverage를 생성하고 CI가 `git diff --exit-code`로 누락된 결과물을 막는다. [S14], [S15] |
| `scripts/link-checker.js`, link-checker workflow | 정적·외부 링크 검증과 재시도 경계 | `content/**/*.html`의 링크/리소스를 검사하고 외부 URL은 최대 3회 재시도한다. [S16], [S17] |
| `test/util/report.js`, coverage-report workflow | 예제 설명 행과 회귀 테스트의 coverage 가시화 | `data-test-id` 누락과 미검증 항목을 보고하고, workflow는 PR에 보고를 작성/갱신하도록 설정한다. [S18], [S19] |
| WAI trigger workflows | 별도 게시 시스템과의 쓰기 경계 | main 배포, PR 미리보기, branch/PR 종료 정리를 별도 레포 workflow dispatch로 요청한다. [S20]-[S22] |

## 기술 스택·실행 경로

- **확인됨:** 정적 콘텐츠는 HTML/CSS/브라우저 JavaScript이고, 저장소 도구는 Node.js의 npm scripts, ESLint, Stylelint, Prettier, cspell, HTMLHint/NU validator, AVA, Selenium WebDriver/Geckodriver다. [S5]
- **확인됨:** 재귀 트리에는 콘텐츠 HTML 130개, 패턴 정의 30개, 예제 HTML 76개, 회귀 테스트 파일 59개, GitHub Actions workflow 11개가 있다. [S2]
- **확인됨:** 이 레포의 `package.json`은 `private: true`이고, npm 패키지 배포물의 런타임 entrypoint로 사용된다는 근거는 없다. [S5]
- **추론:** 제품의 핵심 가치는 애플리케이션의 사용자 데이터를 처리하는 것이 아니라, 설명·데모·테스트·파생 지표가 서로 어긋나지 않도록 유지하는 콘텐츠 품질 파이프라인이다. 이 추론은 콘텐츠, 생성기, 회귀 검사 구조에서 나왔다. [S7]-[S19]

## 에이전트·스킬 탐색 결과

고정 Git 트리에 agent/skill 정의 경로가 없었다. 따라서 모델, 에이전트 역할, tool 권한, prompt 입력 계약을 이 레포의 기능이라고 기술하지 않는다. 실제 실행 단위는 사람이 작성하는 콘텐츠/코드, npm script, CI workflow, 그리고 별도 WAI 레포로 보내는 dispatch다. [S2], [S5], [S20]-[S22]

## 문서와 현재 파일의 불일치

README는 JavaScript 규칙의 위치를 `.eslintrc.json`이라고 설명하지만, 고정 트리에 있는 설정 파일은 `eslint.config.mjs`다. 이 아카이브는 실제 현행 실행 명령(`eslint .`)은 `package.json`을 우선 근거로 삼고, README의 이 경로는 문서상 불일치로 남긴다. [S2], [S3], [S5]

## 미확인 범위

- GitHub Actions의 최근 실제 성공/실패, Actions 로그, 보호 규칙, required check
- 별도 `wai-aria-practices` 레포가 콘텐츠를 변환하는 세부 구현과 실제 배포·PR 미리보기 결과
- 브라우저/보조기술/운영체제별의 실제 접근성 경험, 모든 76개 예제의 동작
- npm 의존성 내부, 시크릿 값, 외부 링크의 현재 가용성 및 응답 내용

근거 ID는 [06-source-evidence.md](06-source-evidence.md)에서 고정 SHA URL로 추적할 수 있다.
