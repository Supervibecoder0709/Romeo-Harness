# 소스 고정 기록

- Origin URL: https://github.com/orca-cli/orca

- Ref: main

- Commit SHA: `5beeefcb57555962bb93facc54b5f82484731802`

- License: MIT

- Analysis timestamp: 2026-08-23T18:44:16Z (2026-08-24 03:44:16 KST)

## 수집 방법과 범위

- GitHub REST API로 `default_branch`와 고정 커밋 SHA를 확인한 뒤, 해당 SHA의 recursive tree와 필요한 원문 파일만 읽었다. clone, issue/PR 작성, 설정 변경, secret 조회, 배포는 하지 않았다.
- 고정 tree에는 blob 39개가 있다. 이 아카이브는 그중 실행 경로·상태/저장소/워크트리 코드, 단위 테스트, CI·릴리스 설정, 사용자 문서에 해당하는 파일을 열어 작성했다. 근거 링크와 줄 범위는 [06-source-evidence.md](06-source-evidence.md)에 있다.

## 접근 한계와 확인된 공백

- README가 링크하는 `DOCS.md`, `CONTRIBUTING.md`와 `assets/logo.png`, `assets/tui-watch.png`, `assets/tui-review.png`, `assets/tui-pod.png`는 이 SHA의 tree에 없고 Contents API 조회도 404였다. 따라서 그 링크·화면은 이 커밋을 근거로 검증할 수 없다.
- `internal/config`, `constraint`, `mcp`, `pod`, `runner`, `tui`에는 각 패키지의 `doc.go`만 있고 구현 파일은 없다. README의 해당 기능 설명은 현재 실행 기능의 증거가 아니라 의도/계획 문서로 구분했다.
- `go.sum`은 잠긴 간접 의존성 목록이라 동작 분석 후보에서 제외했다. `LICENSE`와 `.gitignore`는 각각 라이선스/로컬 산출물 제외 규칙이며, 핵심 실행 경로를 증명하지 않아 번역·구성요소 분석의 중심에서는 제외했다.
