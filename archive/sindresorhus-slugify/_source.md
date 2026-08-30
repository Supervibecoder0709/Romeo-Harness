# 소스 고정 기록

- Origin URL: https://github.com/sindresorhus/slugify
- Ref: `main` (GitHub API가 반환한 현재 기본 브랜치)
- Commit SHA: `7c318bd1aa4b4affab29761f15a9604323fe2a3b`
- License: MIT
- Analysis timestamp: 2026-08-13 08:51:12 KST (+0900)

## 재현 방법과 접근 범위

이 아카이브는 GitHub REST API로 먼저 `default_branch`를 확인한 뒤, 해당 브랜치를 위 40자리 SHA로 고정하여 만들었다. 그 SHA의 재귀 Git 트리에서 blob 13개를 인벤토리화하고, 선택한 파일만 같은 SHA로 읽었다. GitHub에는 읽기 요청만 했으며 clone, push, 이슈·PR 작성, 설정 변경, 시크릿 조회, 배포를 수행하지 않았다.

고정 커밋의 커밋 메시지는 `3.0.0`이고 커밋 시각은 2025-09-11T12:11:41Z이다. 레포 메타데이터상 기본 브랜치는 `main`, 주 언어는 JavaScript, 라이선스는 MIT다. 이는 분석 당시 API 응답이며, 이후 `main`이 이동해도 이 문서의 근거는 위 SHA를 가리킨다. [S1], [S2]

## 확인한 범위

열어 확인한 파일은 `readme.md`, `package.json`, `index.js`, `overridable-replacements.js`, `index.d.ts`, `test.js`, `.github/workflows/main.yml`, `.github/security.md`, `license`다. 각 근거의 고정 URL과 줄 범위는 [06-source-evidence.md](06-source-evidence.md)에 있다.

## 제외·한계

- `.editorconfig`, `.gitattributes`, `.gitignore`, `.npmrc`는 동작 경로·공개 API·CI 실행 계약을 추가로 설명하지 않는 소규모 메타데이터여서 내용 분석 후보에서 제외했다. Git 트리에는 잠금 파일, Docker/Compose, `AGENTS.md`, `CLAUDE.md`, `.claude/agents/**`, `.claude/skills/**`, `.agents/skills/**`가 없다. [S2]
- 원격 저장소를 clone하지 않는 절차를 지켰으므로 이 작업에서 `npm install`이나 `npm test`를 실제 실행하지 않았다. 따라서 CI 워크플로 파일이 무엇을 **설정했는지**는 확인했지만, 특정 실행의 통과 여부나 외부 의존성 설치 재현성은 미검증이다. [S8]
- `@sindresorhus/transliterate`와 `escape-string-regexp`의 내부 구현, npm 배포본, 보안 권고·릴리스·이슈/PR 이력은 이 아카이브 범위에서 열지 않았다. 이 라이브러리가 의존성에 기대는 세부 언어 변환 결과는 이 저장소의 테스트와 선언으로 확인 가능한 범위만 서술한다. [S3], [S6]
