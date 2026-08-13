# 04. 구성요소 표

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 패키지 공개 계약 | npm ESM 패키지 | 기본 함수·타입을 소비자에게 노출 | package import | 기본 `index.js`, 타입 `index.d.ts` | Node.js `>=20`; 런타임 의존성 2개 | `package.json:13-28,49-55` [S3] | 확인됨 |
| `slugify` | 동기 함수 | 문자열을 slug로 변환 | `string`, 선택 `options` | 문자열 또는 입력/옵션 오류 | 전사·정규식 이스케이프 외부 의존성 호출; 이 파일에서 I/O 없음 | `index.js:46-110` [S4] | 확인됨 |
| `buildPatternSlug` | 내부 검증·정규식 생성기 | 허용 문자 집합을 만들고 충돌 옵션을 차단 | 결합된 options | 정규식 또는 `Error` | `escape-string-regexp` 사용 | `index.js:23-44` [S4] | 확인됨 |
| `decamelize`·구분자 정리 | 내부 변환 보조 | 단어 경계를 넣고 연속/가장자리 구분자를 정리 | 문자열, 구분자 | 정리된 문자열 | 로컬 정규식 처리 | `index.js:5-21,80-99` [S4] | 확인됨 |
| 기본 치환 목록 | 정적 데이터 | 전사 전 기본 기호 치환 제공 | 없음 | 3개 key/value 쌍 | `slugify`가 import | `overridable-replacements.js:1-7` [S5] | 확인됨 |
| `slugifyWithCounter` | 상태 있는 함수 팩토리 | 같은 slug에 번호를 붙임 | 이후 반환 함수에 `string`, `options` | 문자열; 인스턴스 로컬 `Map`; `reset()` | 외부 I/O 없음; 재호출 결과가 상태에 의존 | `index.js:112-139`, `index.d.ts:220-286` [S4], [S6] | 확인됨 |
| `@sindresorhus/transliterate` | 외부 런타임 의존성 | Unicode 전사와 locale·치환 옵션 처리 | 문자열, custom replacements, locale | 변환 문자열 | npm 의존성 경계; 내부 구현 미열람 | `package.json:49-52`; `index.js:1-3,66-78` [S3], [S4] | 연결만 확인 |
| 타입 선언 | TypeScript 계약 | 옵션·반환값·카운터 reset 형식 제시 | TypeScript 소비자 | 컴파일 시 타입 정보 | 런타임 동작을 직접 실행하지 않음 | `index.d.ts:1-194,196-286` [S6] | 확인됨 |
| 테스트 | AVA 테스트 모음 | 변환 결과와 오류 경계 검증 | 구현을 직접 import | assertion 성공/실패 | 로컬 테스트 실행; 이 아카이브에서 실제 실행 미수행 | `test.js:1-257` [S7] | 설정·사례 확인, 실행 미검증 |
| CI | GitHub Actions workflow | push/PR에서 설치·테스트 자동화 | GitHub 이벤트 | Node 20·24 각각 `npm install`, `npm test` | GitHub Actions runner·npm 레지스트리 | `.github/workflows/main.yml:1-21` [S8] | 설정 확인, 최근 결과 미확인 |
| 보안 보고 경로 | 정책 문서 | 취약점 연락 방식 안내 | 보안 제보 | Tidelift로 조정 요청 | 외부 Tidelift 연락처 | `.github/security.md:1-3` [S9] | 확인됨 |
| 에이전트·스킬 정의 | 해당 없음 | 고정 트리에서 정의 파일 미발견 | 해당 없음 | 해당 없음 | LLM·도구 권한·승인 단계 없음이 아니라, **이 레포에 정의 근거가 없음** | 재귀 Git 트리 전체 [S2] | 부재 확인 |

`원문 위치`은 모두 고정 SHA에서 읽은 파일·줄 범위다. 자세한 URL은 [06-source-evidence.md](06-source-evidence.md)에 있다.
