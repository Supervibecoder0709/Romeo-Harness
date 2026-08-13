# 00. 탐색 기록

## 결론

`@sindresorhus/slugify`는 문자열을 URL·파일명·식별자에 쓸 수 있는 slug로 동기 변환하는 작은 ESM 라이브러리다. 실행 경로는 패키지 export → `index.js`의 `slugify` 또는 `slugifyWithCounter` 한 파일로 집중되어 있고, 테스트와 CI도 단일 Node.js 패키지 흐름을 검증한다. [S3], [S4], [S6], [S8]

## 탐색 방법

1. `repos/sindresorhus/slugify` API에서 기본 브랜치 `main`을 받고, `commits/main`의 SHA를 `7c318bd1aa4b4affab29761f15a9604323fe2a3b`로 고정했다.
2. `git/trees/<SHA>?recursive=1`으로 모든 blob 13개를 확인했다.
3. 안내 문서, 패키지 실행 계약, 실제 진입점, 변환 보조 데이터, 타입 계약, 테스트, CI, 보안 연락 경로를 우선순위에 따라 열었다.
4. README의 API 설명을 `index.js` 및 `test.js`와 교차 확인했다. 문서에만 있거나 실행 근거가 없는 기능으로 확대 해석하지 않았다.

## 실제로 연 파일과 선정 이유

| 파일 | 선정 이유 | 확인 결과 |
| --- | --- | --- |
| `readme.md` | 설치·공개 API·사용 예시의 공식 안내 | 기본 함수, 옵션, 카운터 API를 설명한다. [S3] |
| `package.json` | npm 패키지의 실제 export, Node 버전, 테스트 명령 | ESM이며 기본 export는 `index.js`, 타입은 `index.d.ts`, Node `>=20`, 테스트 명령은 `xo && ava`다. [S3] |
| `index.js` | 실제 변환과 상태 처리의 진입점 | 입력 검증, 옵션 병합, 변환 순서, 오류, 카운터 상태가 있다. [S4] |
| `overridable-replacements.js` | 기본 치환값의 출처 | `&`, `🦄`, `♥` 기본 치환을 제공한다. [S5] |
| `index.d.ts` | TypeScript 소비자의 입력·출력 계약 | `Options`, 기본 함수, 카운터의 `reset` 타입을 선언한다. [S6] |
| `test.js` | 실제로 기대하는 결과·예외 경계 | 문자 변환, 옵션, 카운터, 예외를 AVA로 검증한다. [S7] |
| `.github/workflows/main.yml` | 자동 검증의 환경·명령 | push/PR에서 Node 20·24에 `npm install`, `npm test`를 실행한다. [S8] |
| `.github/security.md` | 보안 보고 경로 | Tidelift 보안 연락처로 신고하도록 안내한다. [S9] |
| `license` | 배포·재사용 경계 | MIT 라이선스다. [S10] |

## 확인된 핵심 흐름

호출자는 패키지를 ESM으로 import한 다음 문자열과 선택 옵션을 전달한다. 기본 함수는 타입 확인, 기본값 결합, (기본적으로) 외부 전사 모듈을 이용한 문자 변환, camelCase 분리, 소문자화, 허용되지 않는 문자의 구분자 치환·정리를 거쳐 문자열을 반환한다. 카운터 팩토리는 이 기본 함수를 호출한 결과를 클로저의 `Map`에 기록하고 같은 slug가 다시 나오면 숫자 접미사를 붙인다. [S3], [S4]

## 기술 스택·경계

- JavaScript ESM 패키지이며 Node.js `>=20`을 요구한다. [S3]
- 런타임 외부 의존성은 `@sindresorhus/transliterate`, `escape-string-regexp` 두 개다. [S3], [S4]
- 테스트 프레임워크는 AVA, 정적 스타일 검사는 XO다. [S3], [S7]
- 코드에서 파일·네트워크·DB·환경변수를 읽거나 쓰는 경로는 확인하지 못했다. 이는 `index.js`의 import와 함수 본문을 본 범위의 사실이며, 의존성 내부의 I/O까지 부재하다고 증명한 것은 아니다. [S4]

## 에이전트·스킬 탐색 결과

고정 Git 트리에 `AGENTS.md`, `CLAUDE.md`, `.claude/agents/**`, `.claude/skills/**`, `.agents/skills/**`, `SKILL.md`가 없었다. 따라서 LLM 에이전트, 프롬프트, 도구 권한, 사람 승인 단계가 구현되어 있다는 근거는 없으며, 이 레포의 실행 단위는 일반 JavaScript 라이브러리 호출이다. [S2]

## 미확인 범위

- 특정 npm 게시물과 GitHub Actions의 실제 최근 실행 결과
- 의존성 내부의 전사 표·성능·보안 특성
- 이 패키지를 사용하는 외부 애플리케이션의 영속성, 충돌 처리, 승인 절차
- README 예시 외의 브라우저·번들러 호환성

근거 ID는 [06-source-evidence.md](06-source-evidence.md)에서 고정 SHA URL로 추적할 수 있다.
