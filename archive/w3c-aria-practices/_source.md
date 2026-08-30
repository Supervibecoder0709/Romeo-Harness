# 소스 고정 기록

- Origin URL: https://github.com/w3c/aria-practices
- Ref: `main` (GitHub REST API가 반환한 기본 브랜치)
- Commit SHA: `7e4034b262bc0d25332e330d8a582aaf34113829`
- License: W3C Software and Document License
- Analysis timestamp: 2026-08-24 03:49:22 KST (+0900)

## 재현 방법과 접근 범위

GitHub REST API에서 기본 브랜치 `main`을 확인한 다음, `commits/main`이 가리킨 40자리 SHA를 고정했다. 그 SHA의 재귀 Git 트리(521개 blob)를 인벤토리화하고, 안내 문서, `package.json`, 대표 콘텐츠·예제, 생성·검사 스크립트, 테스트, GitHub Actions 워크플로만 같은 SHA로 읽었다. GitHub에는 읽기 요청만 했으며 clone, push, 이슈·PR 작성, 설정 변경, 시크릿 조회, 배포를 수행하지 않았다. [S1], [S2]

고정 커밋은 2026-07-22T15:58:28Z에 작성된 landmark 예제 문장 수정 커밋이다. 레포 메타데이터의 기본 브랜치는 `main`, 설명은 “WAI-ARIA Authoring Practices Guide (APG)”이며, API가 반환한 라이선스 식별자는 `NOASSERTION`이다. 이는 분석 당시의 메타데이터이며, 이후 `main`이 이동해도 이 아카이브의 파일 근거는 위 SHA를 가리킨다. [S1]

## 확인한 범위

`README.md`, `CONTRIBUTING.md`, `package.json`, `content/apg-home.html`, Accordion 패턴·예제 HTML/JS, `test/index.js`, Accordion 회귀 테스트, `scripts/{regression-tests,link-checker,coverage-report,reference-tables}.js`, `test/util/report.js`, `.husky/pre-commit`, 그리고 회귀·생성·링크·배포·PR 미리보기·정리·coverage GitHub Actions 워크플로를 열었다. 각 고정 URL과 줄 범위는 [06-source-evidence.md](06-source-evidence.md)에 있다.

## 제외·한계

- 521개 blob 중 이미지, lockfile, 30개 패턴 전체, 76개 예제 HTML 전체, 59개 회귀 테스트 전체, CSS·공용 브라우저 JS 전체는 대표 실행 경로의 근거를 추가하지 않아 전문 분석에서 제외했다. 파일 수는 재귀 트리 기준이다. [S2]
- 고정 트리에 `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, `.claude/agents/**`, `.claude/skills/**`, `.agents/skills/**`는 없다. 따라서 AI agent/skill, 모델 선택, 프롬프트, agent 도구 권한은 이 레포에서 확인되지 않는다. [S2]
- 대상 레포를 clone하지 않는 안전 경계를 지켰으므로 `npm ci`, `npm test`, 생성 스크립트, 링크 검사, GitHub Actions를 실제 실행하지 않았다. 워크플로가 **설정한 동작**은 확인했지만, 현재 통과 상태·외부 사이트 반영·제3자 링크의 실제 응답은 미검증이다. [S5], [S12]-[S19]
- `wai-aria-practices`라는 별도 레포와 GitHub Actions 시크릿 값, 배포 결과 URL의 고정 SHA 반영 여부는 열지 않았다. 이 레포의 workflow dispatch 설정까지만 확인했다. [S16]-[S18]

근거 ID는 [06-source-evidence.md](06-source-evidence.md)에서 해석한다.
