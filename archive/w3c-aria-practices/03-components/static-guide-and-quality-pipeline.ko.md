# 정적 가이드와 품질 파이프라인 구성요소

## 1. 정적 APG 콘텐츠

`content/apg-home.html`은 ARIA 의미 체계로 접근 가능한 웹 경험을 만들기 위한 패턴·동작 예제·기초 지침을 제공한다고 설명한다. 이 레포는 데이터를 받아 사용자별 결과를 만드는 서버가 아니라, 브라우저가 읽을 HTML/CSS/JavaScript와 문서 계약을 관리한다. [S7]

## 2. 패턴 문서와 실행형 예제

각 패턴 문서는 키보드 상호작용과 역할·상태·속성의 기대값을 설명하고, 예제는 그것을 실행 가능하게 만든다. 대표 Accordion에서 클릭 handler는 버튼의 `aria-expanded`와 대응 panel의 `hidden`을 같이 변경한다. 즉 문서상의 접근성 약속이 실제 DOM 동작으로 이어지는 구조다. [S8], [S9]

## 3. 회귀 테스트와 coverage 보고

공통 `ariaTest` helper는 각 로컬 예제의 `data-test-id`가 문서에 있는지 확인한 뒤 Selenium/Firefox에서 동작을 검증한다. `test/util/report.js`는 예제 문서 표의 test ID와 test 파일의 선언을 비교해 누락된 회귀 테스트·문서 행을 보고한다. 이 테스트는 실제 보조기술의 사용자 경험까지 검증한다는 근거는 아니다. [S10], [S11], [S18]

## 4. 파생물 생성과 정합성 검사

reference table·coverage generator는 예제와 지침에서 역할·ARIA 속성을 읽어 인덱스/보고 산출물을 만든다. GitHub Actions는 생성 후 working tree에 diff가 없는지 검사하므로, 생성 결과를 소스에 반영하지 않은 변경을 잡는 역할을 한다. [S14], [S15]

## 5. 외부 WAI 게시 연동

이 레포의 main 콘텐츠 변경은 별도 `wai-aria-practices` 레포의 `deploy.yml` workflow dispatch를 요청한다. PR 미리보기와 branch/PR 종료 정리도 같은 외부 레포의 workflow를 호출하도록 설정되어 있다. 외부 workflow의 구현·권한·성공 여부·실제 공개 결과는 이 레포만 읽은 범위에서는 미검증이다. [S20]-[S22]
