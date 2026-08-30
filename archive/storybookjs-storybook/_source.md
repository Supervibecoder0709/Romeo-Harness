# Source fixation

- Origin URL: https://github.com/storybookjs/storybook
- Ref: next
- Commit SHA: `db12626a58d505f5551ae1d2c714c6249849212a`
- License: MIT
- Analysis timestamp: 2026-08-24T03:51:27+0900

## 범위와 접근 방식

- GitHub REST API와 고정 커밋의 raw 파일만 읽었다. clone, 이슈·PR 작성, 릴리스·배포, 설정 변경, secret 조회는 하지 않았다.
- 기본 브랜치는 GitHub API에서 확인한 next이고, 이 문서의 모든 파일 근거 URL은 위 SHA를 사용한다.
- 9,459개 경로의 대형 TypeScript 모노레포이므로 전체 파일을 내려받지 않았다. CLI 진입점, core server, MCP addon, Codex plugin, 테스트 설정, CI와 릴리스 워크플로를 우선 열었다.
- 참고한 GitHub workflow 안에는 secret 이름이 나타나지만 값은 조회하지 않았다.

## 접근 한계

- 로컬 설치, 컴파일, 테스트, 실제 dev server 기동, npm 배포물, CI 실행 결과, 외부 MCP endpoint의 현재 응답은 검증하지 않았다.
- 정적 분석이므로 특정 앱의 .storybook 설정, framework/builder 선택, addon 조합에 따라 달라지는 실제 동작은 확인하지 않았다.
- GitHub API가 제공한 현재 next HEAD만 고정했다. 이후 브랜치 이동이나 릴리스 상태는 이 아카이브의 범위 밖이다.

## 제외한 후보와 이유

- yarn lockfile, 생성된 sandbox, 빌드 산출물, 이미지/동영상, vendor성 파일은 실행 계약을 직접 설명하지 않아 제외했다.
- docs/_snippets 이하의 대량 예제와 모든 framework/renderer 구현은 대표 흐름을 중복하므로 제외했다. 지원 범위는 README와 package/config 근거로만 기록했다.
- 전체 단위·E2E 테스트는 실행하지 않고, CLI skill·tool 계약과 Storybook Vitest 설정을 확인하는 대표 테스트/설정만 읽었다.

자세한 파일별 근거는 06-source-evidence.md를 참조한다.
