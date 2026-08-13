# 06. 원문 근거 목록

모든 링크는 분석을 고정한 커밋 `7c318bd1aa4b4affab29761f15a9604323fe2a3b`를 가리킨다. `파일:줄`은 GitHub REST Contents API로 해당 SHA의 내용을 읽고 줄 번호를 매긴 결과다.

| ID | 원문 위치 | 이 아카이브에서 뒷받침하는 사실 |
| --- | --- | --- |
| S1 | [레포 메타데이터 API](https://api.github.com/repos/sindresorhus/slugify), [고정 커밋 API](https://api.github.com/repos/sindresorhus/slugify/commits/7c318bd1aa4b4affab29761f15a9604323fe2a3b) | 기본 브랜치, 레포 설명·라이선스·언어, 고정 SHA와 커밋 시각 |
| S2 | [재귀 Git 트리 API](https://api.github.com/repos/sindresorhus/slugify/git/trees/7c318bd1aa4b4affab29761f15a9604323fe2a3b?recursive=1) | 13개 blob 인벤토리, agent/skill 정의 파일과 lockfile 부재 |
| S3 | [package.json:1-62](https://github.com/sindresorhus/slugify/blob/7c318bd1aa4b4affab29761f15a9604323fe2a3b/package.json#L1-L62), [readme.md:1-310](https://github.com/sindresorhus/slugify/blob/7c318bd1aa4b4affab29761f15a9604323fe2a3b/readme.md#L1-L310) | 패키지 export·Node 요구사항·의존성·테스트 명령·사용자 API 설명 |
| S4 | [index.js:1-139](https://github.com/sindresorhus/slugify/blob/7c318bd1aa4b4affab29761f15a9604323fe2a3b/index.js#L1-L139) | 실제 변환 순서, 오류, 카운터 상태와 reset |
| S5 | [overridable-replacements.js:1-7](https://github.com/sindresorhus/slugify/blob/7c318bd1aa4b4affab29761f15a9604323fe2a3b/overridable-replacements.js#L1-L7) | 내장 치환 3개 |
| S6 | [index.d.ts:1-286](https://github.com/sindresorhus/slugify/blob/7c318bd1aa4b4affab29761f15a9604323fe2a3b/index.d.ts#L1-L286) | TypeScript 옵션, 함수와 카운터 타입 계약 |
| S7 | [test.js:1-257](https://github.com/sindresorhus/slugify/blob/7c318bd1aa4b4affab29761f15a9604323fe2a3b/test.js#L1-L257) | 결과·옵션·예외·언어·카운터 회귀 사례 |
| S8 | [.github/workflows/main.yml:1-21](https://github.com/sindresorhus/slugify/blob/7c318bd1aa4b4affab29761f15a9604323fe2a3b/.github/workflows/main.yml#L1-L21) | push/PR CI와 Node 20·24 테스트 설정 |
| S9 | [.github/security.md:1-3](https://github.com/sindresorhus/slugify/blob/7c318bd1aa4b4affab29761f15a9604323fe2a3b/.github/security.md#L1-L3) | 취약점 신고 연락 경로 |
| S10 | [license:1-9](https://github.com/sindresorhus/slugify/blob/7c318bd1aa4b4affab29761f15a9604323fe2a3b/license#L1-L9) | MIT 라이선스와 보증 부인 |

## 근거 해석 규칙

- **확인됨**: 위 고정 SHA의 코드·설정·타입·테스트·정책 원문에 직접 있다.
- **추론**: 코드 구조에서 합리적으로 도출했지만, 외부 시스템의 실제 운영까지 증명하지 않는다. 문서에서 `추론`으로 표시했다.
- **미검증**: GitHub Actions 실행 결과, npm 배포물, 외부 의존성 내부 구현처럼 이 절차에서 열거나 실행하지 않은 내용이다.

API와 파일 URL은 읽기 전용 근거 링크다. 이 아카이브 작성 중 GitHub 저장소의 코드, 설정, 이슈, PR, 릴리스를 변경하지 않았다.
