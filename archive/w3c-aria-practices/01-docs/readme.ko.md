# WAI-ARIA: 저작 실무 가이드

이 저장소는 WAI-ARIA Authoring Practices Guide(APG)를 관리합니다.

- 게시 위치: [w3.org/wai/aria/apg](https://www.w3.org/wai/aria/apg/)
- [ARIA Working Group](http://www.w3.org/WAI/ARIA/)의 [Authoring Practices Task Force](https://www.w3.org/WAI/ARIA/task-forces/practices/)가 개발합니다.
- 담당자: [Daniel Montalvo](https://www.w3.org/people#dmontalvo)

조율 없이 이 저장소의 커밋 권한을 제공하지 마세요.

## 작업 구성 방식

- 작업은 [마일스톤](https://github.com/w3c/aria-practices/milestones?direction=asc&sort=due_date&state=open)에서 계획·우선순위화합니다. 각 마일스톤은 w3.org에 게시되는 작업 초안 또는 릴리스에 대응합니다.
- 작업은 [프로젝트](https://github.com/w3c/aria-practices/projects)에서 주제별로 구성합니다. 각 프로젝트는 하나의 디자인 패턴 유형 또는 지침 섹션에 대응합니다.
- 작업 범위와 로드맵은 프로젝트 wiki의 [scope of work and roadmap](https://github.com/w3c/aria-practices/wiki/Scope)에 설명되어 있습니다.

## 기여하기

1. 기존 이슈에 댓글을 달거나 새 이슈를 열어, 도움을 주고 싶다는 의사와 제안하는 해결 방향을 간략히 설명합니다.
2. 편집자가 상충하는 계획이 없는지 확인하고, 필요하면 지침을 제공합니다.
3. 아래 설명에 따라 linter를 설치하고 설정했는지 확인합니다.
4. [pull request 제출](https://github.com/w3c/aria-practices/wiki/Submitting-Pull-Requests)에 관한 wiki 페이지를 읽습니다.
5. 훌륭한 작업을 하고 pull request를 제출합니다.

참고: 이슈나 [Authoring Practices Task Force 메일링 리스트](http://lists.w3.org/Archives/Public/public-aria-practices/)를 통해 자유롭게 질문하세요.

### 코드 적합성

이 저장소는 HTML, CSS, JavaScript 전반에서 정적 코드 분석을 수행하고 일관된 코드 품질을 보장하기 위해 [linting](https://en.wikipedia.org/wiki/Lint_%28software%29) 도구를 사용합니다. 각 lint 도구와 해당 코드 표준은 아래와 [code guide](https://github.com/w3c/aria-practices/wiki/Code-Guide)에 문서화되어 있습니다.

lint 오류가 포함된 pull request는 오류가 해결될 때까지 병합되지 않습니다. 더 쉽게 하려면 push하기 전에 로컬에서 도구를 설치하고 실행할 수 있습니다. 또한 CSS와 JavaScript 도구는 로컬에 설치되어 있다면 많은 문제를 자동 수정합니다. 이 도구를 설치하려면 다음을 따르세요.

1. [Node.js](https://nodejs.org/en/)와 함께 제공되는 [node package manager (npm)](https://www.npmjs.com/get-npm)이 설치되어 있는지 확인합니다.
1. 터미널에서 `aria-practices` 저장소가 있는 디렉터리를 엽니다.
1. `npm install`을 실행합니다.

HTML validator를 실행하려면 JDK 설치도 필요합니다. JDK가 아직 없다면 [Oracle에서 최신 JDK를 내려받으세요](https://www.oracle.com/technetwork/java/javase/downloads/index.html).

이 도구와 [EditorConfig](http://editorconfig.org/)를 지원하는 코드 편집기를 사용하는 것도 강력히 권장합니다.

#### HTML

HTML은 [NU HTML Validator](https://github.com/validator/validator)로 검증합니다. 향후 ARIA 기능이 아직 구현되지 않아 경고나 오류가 발생하면 [.vnurc file](.vnurc)에 추가하여 그 오류를 통과시킵니다.

로컬 실행:

```sh
npm run lint:html
```

#### CSS

CSS는 [stylelint](https://stylelint.io/)에서 [stylelint-config-standard](https://github.com/stylelint/stylelint-config-standard) 규칙 세트를 사용해 검증합니다.

**참고**: 커밋 시 staged CSS 파일에 stylelint가 실행됩니다. [--fix 플래그](https://stylelint.io/user-guide/cli/#autofixing-errors)로 자동 수정할 수 있는 오류가 있으면, 자동 수정된 변경 사항도 커밋됩니다.

로컬 실행:

```sh
npm run lint:css
```

#### JavaScript

JavaScript는 [ESLint](http://eslint.org/)로 검증하며, [자체 설정](.eslintrc.json)을 사용합니다.

**참고**: 커밋 시 staged CSS 파일에 eslint가 실행됩니다. [--fix 플래그](https://eslint.org/docs/user-guide/command-line-interface#fixing-problems)로 자동 수정할 수 있는 오류가 있으면, 자동 수정된 변경 사항도 커밋됩니다.

로컬 실행:

```sh
npm run lint:js
```

### 코드 테스트 및 수정

1. `aria-practices` 저장소가 있는 디렉터리에서 터미널 창을 엽니다.
1. 이 저장소에는 examples 디렉터리의 모든 JavaScript를 테스트하는 script가 정의되어 있습니다. 실행하려면 `npm test` 명령을 실행하세요. 참고: 이 작업은 몇 분 걸릴 수 있으며, 테스트 도중 포커스를 가져오는 여러 브라우저 창을 엽니다.
1. `npm run fix` 명령으로 많은 오류를 자동 수정할 수 있습니다.
1. fix를 실행한 뒤 다시 테스트하여 수동으로 수정할 항목을 확인합니다.

linter가 오류를 만나면 콘솔에 보고합니다. 오류 보고에는 파일 이름과 줄 번호가 포함되며, 스타일 위반이 발생한 줄의 문자 또는 위치를 알려 줍니다. 오류를 고치려면 그 위반이 지시하는 변경 사항을 충족하세요.

예를 들어 아래는 유효하지 않은 변수 이름 스타일의 오류입니다. 변수는 camelCase 규칙을 따라야 합니다.

```sh
/Users/user1/Documents/github/aria-practices/examples/slider/js/text-slider.js
  19:8  error  Identifier 'value_nodes' is not in camel case  camelcase
```

오류는 `examples/slider/js/text-slider.js`의 19번째 줄에 발생했고, 콜론 뒤 숫자 `8`이 문제 문자를 가리킵니다. 소스에서 `value_nodes`를 `valueNodes`로 바꾸면 이 오류가 사라집니다.

ESLint에 적용되는 스타일 규칙 전체 목록은 프로젝트 루트의 [.eslintrc.json](.eslintrc.json) 파일에서 확인하세요.

### 편집 문서

APG용 글을 쓰는 방법은 [APG Editorial Style Guidelines](https://github.com/w3c/aria-practices/wiki/APG-Editorial-Style-Guidelines)를 참고하세요. [ARIA specification의 ReadMe](https://github.com/w3c/aria/)에는 추가로 유용한 편집 지침이 있습니다.
