# 소스 고정 기록

- Origin URL: https://github.com/nexu-io/open-design
- Ref: `main` (GitHub API가 반환한 기본 브랜치)
- Commit SHA: `35a38abf349bfbb53e2ae0252f0f21c8571890b2`
- Analysis timestamp: 2026-08-24 03:50:33 KST (+0900)

## 재현 방법과 접근 범위

이 아카이브는 GitHub REST API로 `default_branch`를 확인하고 `commits/main`이 돌려 준 위 SHA로 내용을 고정한 뒤 작성했다. 고정 SHA의 재귀 Git 트리에서 blob 12,885개를 인벤토리화하고, 아래 후보 파일만 같은 SHA의 Contents API raw 응답으로 읽었다. 대상 저장소에는 읽기 요청만 했으며 clone, push, 이슈·PR 작성, 설정 변경, 시크릿 조회, 배포를 하지 않았다. [S1], [S2]

분석한 경로는 `README.md`, `QUICKSTART.md`, `docs/architecture.md`, 최상위·앱별 `package.json`, `apps/AGENTS.md`, `apps/daemon/AGENTS.md`, `apps/daemon/src/agent-protocol/README.md`, 패키지·daemon·런타임·artifact·run route의 핵심 코드, CI/E2E/daemon 테스트, 그리고 `.claude/skills/od-contribute/` 정의다. 각 파일·줄 범위와 고정 URL은 [06-source-evidence.md](06-source-evidence.md)에 있다.

## 접근 한계와 제외

- 12,885개 파일의 대형 모노레포이므로 `apps/` 전체 구현, 357개 skill 파일, 1,815개 plugin 파일, 4,015개 design-system 파일을 전부 열지 않았다. 대신 실제 패키징 시작점, daemon composition/route, Codex runtime 정의, artifact 저장 경계, CI 및 대표 테스트를 우선 확인했다. [S2]
- `README.md`의 제품·호환성 주장은 `QUICKSTART.md`, `docs/architecture.md`, 패키지 계약과 선택한 코드 경로로 교차 확인한 범위만 사실로 서술했다. 모든 지원 CLI 또는 모든 UI 기능을 실행해 확인한 것은 아니다. [S3], [S4], [S5], [S6]
- 원격 저장소를 clone하거나 의존성을 설치하지 않았으므로 `pnpm` 테스트, Electron/컨테이너 실행, 실제 GitHub Actions 실행 결과, 외부 CLI 로그인·모델·네트워크 제공자, 릴리스 자산은 **미검증**이다. CI와 테스트 파일은 “무엇을 설정·검증하도록 작성됐는지”만 확인했다. [S16], [S17], [S18]
- 이 작업은 의도적으로 GitHub issues/PR, 사용자 토큰·secret, 실제 설정값을 읽지 않았다. 공개 코드에 나타난 환경변수·인증 경계는 구현·테스트의 계약일 뿐, 어느 설치의 실제 값이나 안전성을 증명하지 않는다. [S19]
