# 02. 워크플로 요약

## 무엇을 하는가

APG는 웹 접근성 디자인 패턴, 키보드 상호작용, ARIA 역할·상태·속성의 사용법과 동작 예제를 함께 제공하는 정적 가이드다. 소스 `content/`는 이 레포에서 작성되지만, 홈 HTML 주석과 배포 workflow에 따르면 최종 WAI 사이트 형태로의 변환·게시에는 별도 `wai-aria-practices` 레포가 관여한다. [S7], [S20]

## 입력

- 작성자 입력: `content/`의 패턴 설명 HTML, 예제 HTML/CSS/JS, 공통 스타일·스크립트, 테스트와 생성 스크립트 변경. [S2], [S7]-[S11]
- 실행 입력: `npm` 의존성, 변경 파일 범위, `COMMIT_RANGE`, CI matrix index, 테스트 대기 시간. [S5], [S12], [S13]
- 외부 연동 입력: GitHub `push`/`pull_request_target` 이벤트의 branch·SHA·PR 번호와 workflow secret 토큰. 토큰의 값은 이 분석에서 읽지 않았다. [S19]-[S22]

## 처리 단계

1. **콘텐츠와 예제 작성:** 패턴 페이지가 요구하는 키보드·ARIA 계약을 설명하고, 예제 HTML/JS가 실제 상태를 바꾼다. 대표 Accordion 예제는 click으로 `aria-expanded`와 panel의 `hidden`을 함께 갱신한다. [S8], [S9]
2. **로컬 예방 검사:** 커밋 시 Husky가 `lint-staged`를 실행한다. HTML 예제나 생성기 변경에는 Prettier/Stylelint/ESLint 자동 수정과 함께 reference table·coverage 파일을 다시 만들고 `git add`하는 설정이 있다. 즉, 작업 트리 상태가 바뀔 수 있는 개발자 도구 단계다. [S5], [S6]
3. **정적 품질 검사:** `npm test`는 lint 후 AVA 회귀를 실행한다. 별도 link checker는 `content/**/*.html`에서 링크·CSS·JS·이미지 참조를 수집하고 외부 URL을 최대 3회 재시도한다. [S5], [S16]
4. **예제 동작 회귀:** 공통 test helper가 각 로컬 예제 HTML을 `file://` URL로 열고 `data-test-id`가 있는 문서 행 및 Selenium 행위를 검사한다. regression workflow는 변경 범위에서 전체 또는 관련 test를 고르고 5개 CI job으로 분할한다. [S10]-[S13]
5. **파생물 정합성:** reference table/coverage generator가 예제와 안내 문서에서 역할·ARIA 속성을 읽어 인덱스·보고 파일을 만든다. CI는 생성 후 `git diff --exit-code`로 소스에 파생 결과가 반영되었는지를 검사한다. [S14], [S15]
6. **WAI 사이트 연동:** `main`의 해당 경로 변경은 별도 레포의 `deploy.yml` dispatch를 요청한다. PR에는 별도 레포의 `pr-create.yml`, 브랜치 삭제/PR 종료에는 `remove-branch.yml` dispatch를 요청하는 workflow가 있다. [S20]-[S22]

## 출력/상태

- 확인됨: 콘텐츠 HTML·예제 JS, 생성된 `content/index/index.html` 및 coverage 관련 산출물, lint/회귀/링크 검사 결과, CI job 로그, coverage PR 코멘트가 이 workflow의 산출물 또는 상태 변화로 설정되어 있다. [S5], [S14]-[S19]
- 확인됨: main 배포 및 PR 미리보기/정리는 이 레포 밖 `wai-aria-practices`에 workflow dispatch를 보낸다. [S20]-[S22]
- 미검증: 특정 커밋이 실제 `https://www.w3.org/wai/aria/apg/`에 게시됐는지, dispatch가 성공했는지, PR 미리보기 URL이 무엇인지는 확인하지 않았다.

## 실패·재시도

- lint·AVA·생성 정합성 검사는 명령 실패 또는 `git diff --exit-code` 실패로 CI를 실패시킬 수 있다. [S5], [S13], [S15]
- regression selector는 관련 파일이 없으면 예제 회귀를 실행하지 않고 정상 종료한다. Landmark 예제는 선택 로직/trigger에서 명시적으로 제외되어 있어 같은 보장을 받는다고 단정할 수 없다. [S12], [S13]
- link checker는 외부 HTTP 403/429/503/508과 fetch 오류에 대해 15초 기반 지수 backoff로 최대 3회 시도한 뒤 오류를 수집한다. 외부 링크 품질은 네트워크·상대 서버 상태에 의존한다. [S16]
- coverage report workflow는 생성 명령에 `|| true`를 두고 PR 코멘트로 보고한다. 따라서 코멘트가 있어도 해당 PR의 모든 회귀 검사가 통과했다는 완료 증거는 아니다. [S19]

## 관찰 증거

가장 신뢰할 수 있는 완료 증거는 (1) 변경된 콘텐츠와 생성 산출물의 diff, (2) 해당 PR/commit의 lint·regression·examples·link-checker job 결과, (3) coverage 코멘트 내용, (4) 별도 WAI 레포의 dispatch/workflow 성공 기록, (5) 최종 사이트에서 해당 고정 SHA의 콘텐츠가 읽히는지의 독립 readback이다. 이 중 이 아카이브 작성 중 실제로 관찰한 것은 소스 설정뿐이며, 실행·배포 결과는 미검증이다. [S5], [S13], [S15], [S17], [S19]-[S22]
