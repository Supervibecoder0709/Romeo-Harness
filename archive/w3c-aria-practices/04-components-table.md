# 04. 구성요소 표

근거 상태의 **확인됨**은 고정 SHA의 파일을 직접 읽은 사실, **추론**은 파일 사이의 실행 관계를 요약한 것, **미검증**은 외부 실행 결과다. 근거 ID는 [06-source-evidence.md](06-source-evidence.md)에서 해석한다.

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태변화 | 권한·외부경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `content/apg-home.html` | 정적 콘텐츠 진입 | 패턴·예제·기초 지침으로 안내 | HTML·공유 정적 자산 | APG 홈 콘텐츠 | 브라우저, 최종 변환은 별도 WAI 레포라고 주석에 표시 | [S7] | 확인됨 |
| `content/patterns/*/*-pattern.html` | 패턴 규격 문서 | 키보드와 WAI-ARIA 사용 계약을 설명 | 작성된 HTML | 패턴 안내 페이지 | 브라우저 읽기 | [S8] | 확인됨 |
| `content/patterns/*/examples/*.{html,js,css}` | 실행형 예제 | 문서의 계약을 UI 상태 변화로 시연 | 사용자 키보드/포인터, DOM | DOM 속성·표시 상태 변화 | 브라우저 DOM; 대표 Accordion은 네트워크/저장소 I/O를 확인하지 못함 | [S9] | 확인됨(대표 예제) |
| `package.json` npm scripts | 실행 계약 | lint, link, 생성, 회귀 test의 진입점 | 로컬 파일·npm 의존성 | 검사 결과 또는 생성 파일 | 로컬 파일 시스템·JDK·브라우저 driver가 필요할 수 있음 | [S5] | 확인됨 |
| `.husky/pre-commit` + `lint-staged` | 로컬 Git 훅 | 커밋 전 형식/스타일 검사와 일부 파생물 갱신 | staged 변경 | 자동 수정, `git add`될 파생 콘텐츠 | 개발자 작업 트리를 바꿀 수 있음 | [S5], [S6] | 확인됨 |
| `test/index.js` + `test/tests/*.js` | 브라우저 회귀 테스트 | 문서화한 행과 실제 키보드/ARIA 동작 연결 | 로컬 예제 파일, `data-test-id`, Selenium | AVA pass/fail | `file://`, Geckodriver, Firefox; 실제 보조기술은 범위 밖 | [S10], [S11] | 확인됨 |
| `scripts/regression-tests.sh` | CI 테스트 선택기 | 변경 범위에 맞는 test만 또는 전체 test 실행 | Git diff, `COMMIT_RANGE` | AVA 대상 목록, exit code | Git history, CI env; Landmark 제외 | [S12] | 확인됨 |
| `scripts/reference-tables.js` | 파생물 생성기 | 예제의 역할·속성을 모아 index 참조표 생성 | 예제 HTML/JS | `content/index/index.html` 쓰기 | 로컬 파일 시스템 | [S14] | 확인됨 |
| `scripts/coverage-report.js` / `test/util/report.js` | 품질 지표 생성/보고 | 예제·안내와 회귀 test의 coverage 공백을 집계 | HTML, JS, AVA TAP 출력 | coverage HTML/CSV 또는 콘솔 보고 | 로컬 파일 시스템·Node child process | [S14], [S18] | 확인됨 |
| `scripts/link-checker.js` | 링크 검사기 | content 내 링크·리소스·anchor 검증 | 콘텐츠 HTML, 외부 URL | 오류 수, exit code | 외부 HTTP fetch; 최대 3회 재시도 | [S16] | 확인됨 |
| `.github/workflows/{regression,examples,link-checker}.yml` | CI 품질 게이트 | npm 설치·회귀·생성 diff·링크 검사 실행 | push/PR와 경로 조건 | GitHub Actions job 결과 | GitHub-hosted runner, npm cache | [S13], [S15], [S17] | 확인됨(설정) |
| `.github/workflows/coverage-report.yml` | PR 보고 자동화 | coverage 결과를 PR 코멘트로 생성/갱신 | `pull_request_target`, PR head, `GITHUB_TOKEN` | issue/PR comment 쓰기 | `issues: write`; 실제 실행/코멘트 미검증 | [S19] | 확인됨(설정) |
| WAI trigger workflows + cleanup script | 외부 배포/미리보기 연동 | 별도 WAI 레포의 deploy, PR 생성, branch 제거 workflow 호출 | main/PR/delete 이벤트, branch/SHA/PR 정보, secret | 외부 `workflow_dispatch` 요청 | `W3CGRUNTBOT_TOKEN`; 그 값·외부 결과 미검증 | [S20], [S21], [S22] | 확인됨(요청 설정), 결과 미검증 |
