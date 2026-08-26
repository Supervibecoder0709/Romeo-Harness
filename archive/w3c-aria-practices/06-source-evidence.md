# 06. 원문 근거 목록

모든 파일 링크는 분석을 고정한 커밋 `7e4034b262bc0d25332e330d8a582aaf34113829`를 가리킨다. `파일:줄`은 GitHub REST Contents API로 같은 SHA의 파일을 읽고 줄 번호를 매긴 결과다.

| ID | 원문 위치 | 이 아카이브에서 뒷받침하는 사실 |
| --- | --- | --- |
| S1 | [레포 메타데이터 API](https://api.github.com/repos/w3c/aria-practices), [고정 커밋 API](https://api.github.com/repos/w3c/aria-practices/commits/7e4034b262bc0d25332e330d8a582aaf34113829) | 기본 브랜치, 설명·라이선스 API 값, 고정 SHA, 커밋 시각과 메시지 |
| S2 | [재귀 Git 트리 API](https://api.github.com/repos/w3c/aria-practices/git/trees/7e4034b262bc0d25332e330d8a582aaf34113829?recursive=1) | 521 blob 인벤토리, 콘텐츠/예제/test/workflow 수, agent/skill 정의 파일 부재 |
| S3 | [README.md:1-108](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/README.md#L1-L108) | APG 목적·공개 URL·기여 흐름·lint/test 안내·문서상의 `.eslintrc.json` 경로 |
| S4 | [CONTRIBUTING.md:1-21](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/CONTRIBUTING.md#L1-L21) | 기여의 W3C 라이선스·저작권·공동 기여자 표기 규칙 |
| S5 | [package.json:1-95](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/package.json#L1-L95) | npm scripts, 개발 의존성, lint-staged, private 패키지 설정 |
| S6 | [.husky/pre-commit:1](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/.husky/pre-commit#L1), [package.json:64-83](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/package.json#L64-L83) | pre-commit에서 lint-staged 실행, 자동 수정·파생물 생성·git add 설정 |
| S7 | [content/apg-home.html:1-102](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/content/apg-home.html#L1-L102) | APG 홈의 목적·패턴/예제/기초 실무 안내, 별도 WAI 레포가 최종 변환한다는 주석 |
| S8 | [content/patterns/accordion/accordion-pattern.html:18-89](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/content/patterns/accordion/accordion-pattern.html#L18-L89) | Accordion의 키보드, button/heading/region·ARIA 계약 |
| S9 | [Accordion 예제 HTML:40-50](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/content/patterns/accordion/examples/accordion.html#L40-L50), [예제 JS:10-60](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/content/patterns/accordion/examples/js/accordion.js#L10-L60), [예제 설명 표:154-247](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/content/patterns/accordion/examples/accordion.html#L154-L247) | `aria-expanded`/`hidden` DOM 갱신과 data-test-id로 문서 계약을 표시하는 대표 예제 |
| S10 | [test/index.js:1-110](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/test/index.js#L1-L110) | AVA·Selenium·Geckodriver 초기화, `file://` 예제 접근, data-test-id 존재 검사 |
| S11 | [test/tests/accordion_accordion.js:1-216](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/test/tests/accordion_accordion.js#L1-L216) | Accordion의 DOM 구조, ARIA 속성, Enter/Space 동작 회귀 사례 |
| S12 | [scripts/regression-tests.sh:1-56](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/scripts/regression-tests.sh#L1-L56) | 변경 범위 기반 test 선택, 전체 실행 조건, landmark 제외, 대상 없음 시 정상 종료 |
| S13 | [.github/workflows/regression.yml:1-59](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/.github/workflows/regression.yml#L1-L59) | PR/push trigger 경로, landmark 제외, 5개 matrix, npm ci와 regression script 실행 |
| S14 | [scripts/reference-tables.js:1-23](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/scripts/reference-tables.js#L1-L23), [reference-tables.js:197-278](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/scripts/reference-tables.js#L197-L278), [coverage-report.js:450-564](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/scripts/coverage-report.js#L450-L564) | 예제 HTML/JS를 읽어 역할·속성 인덱스를 만들고 coverage 데이터를 집계하는 생성기 |
| S15 | [.github/workflows/examples.yml:1-62](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/.github/workflows/examples.yml#L1-L62) | reference table·coverage 생성 후 git diff 정합성을 검사하는 CI |
| S16 | [scripts/link-checker.js:1-235](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/scripts/link-checker.js#L1-L235) | content 링크/리소스 검사, 외부 fetch, 상태별 재시도와 backoff |
| S17 | [.github/workflows/link-checker.yml:1-28](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/.github/workflows/link-checker.yml#L1-L28) | main push/PR에서 npm ci와 link checker 실행 |
| S18 | [test/util/report.js:1-217](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/test/util/report.js#L1-L217), [report.js:283-324](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/test/util/report.js#L283-L324) | data-test-id/문서 행과 regression test의 coverage 공백 및 파일명 규칙 보고 |
| S19 | [.github/workflows/coverage-report.yml:1-69](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/.github/workflows/coverage-report.yml#L1-L69) | pull_request_target, issues: write, PR head checkout, `|| true`, PR 코멘트 작성/갱신 설정 |
| S20 | [.github/workflows/wai-trigger-deploy.yml:1-29](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/.github/workflows/wai-trigger-deploy.yml#L1-L29) | main의 common/content/README 변경 시 별도 WAI 레포 `deploy.yml` dispatch |
| S21 | [.github/workflows/wai-trigger-pr.yml:1-48](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/.github/workflows/wai-trigger-pr.yml#L1-L48) | PR head·fork 정보로 별도 WAI 레포 `pr-create.yml` dispatch |
| S22 | [.github/workflows/wai-trigger-cleanup.yml:1-56](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/.github/workflows/wai-trigger-cleanup.yml#L1-L56), [scripts/wai-trigger-cleanup.js:1-34](https://github.com/w3c/aria-practices/blob/7e4034b262bc0d25332e330d8a582aaf34113829/scripts/wai-trigger-cleanup.js#L1-L34) | branch delete/PR close 시 외부 WAI branch 존재 확인 및 `remove-branch.yml` dispatch |

## 근거 해석 규칙

- **확인됨**: 위 고정 SHA의 코드·설정·테스트·workflow 원문에 직접 있다.
- **추론**: 파일 구조와 호출 관계에서 도출했지만, 외부 시스템의 실제 실행까지 증명하지 않는다.
- **미검증**: GitHub Actions 최근 결과, 외부 WAI 레포, 시크릿, 공개 사이트 반영, 실제 접근성 품질처럼 이 절차에서 실행·열람하지 않은 내용이다.

이 아카이브 작성 중 대상 GitHub 레포의 코드, 설정, 이슈, PR, 시크릿, 배포를 변경하지 않았다.
