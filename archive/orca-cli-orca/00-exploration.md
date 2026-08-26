# 탐색 기록

## 결론 요약

**확인된 사실:** 고정 커밋 `5beeefcb57555962bb93facc54b5f82484731802`는 완성된 멀티 에이전트 오케스트레이터가 아니라, 그 기반이 될 상태 전이·SQLite·git worktree·어댑터 포트를 만든 **초기 skeleton**이다. 실제 바이너리 진입점은 Cobra root command를 실행하고, 등록된 하위 명령은 `version` 하나뿐이다. README의 `run`, `pod`, `mcp`, `watch`, `ship` 등은 현재 tree의 구현으로는 실행 경로가 확인되지 않았다.[E04][E05]

## 탐색 범위

- GitHub API에서 `main`과 그 커밋 SHA를 고정했고, recursive tree의 blob 39개를 목록화했다.[E01][E02]
- tree에 `README.md`, Go module/진입점, `internal/*` 코드와 테스트, GitHub Actions, GoReleaser 설정이 있어 이 파일들을 후보로 선정했다.
- 후보 수가 40개 미만이지만, 문서 주장만으로 결론 내리지 않도록 각 핵심 흐름마다 최소 한 개의 실행 코드와 한 개의 테스트 또는 설정을 대조했다.

## 실제로 연 파일과 선정 이유

| 분류 | 연 파일 | 선정 이유 | 확인 결과 |
| --- | --- | --- | --- |
| 사용자 문서 | `README.md` | 사용법·명령·MCP·TUI·운영 주장의 원문 | 번역은 `01-docs/README.ko.md`; 코드와 불일치 다수 확인 [E03] |
| 빌드 계약 | `go.mod`, `.goreleaser.yaml` | 언어·직접 의존성·배포 바이너리 및 지원 OS/아키텍처 | Go 1.25, Cobra/SQLite 등 직접 의존성, `./cmd/orca` 빌드 [E06][E17] |
| 실행 진입점 | `cmd/orca/main.go`, `internal/cli/root.go`, `internal/cli/version.go` | 실제 CLI가 어디서 시작하고 어떤 명령을 등록하는지 | `main → cli.Execute → rootCmd`, 현재는 `version`만 등록 [E04][E05] |
| 에이전트 경계 | `internal/adapter/adapter.go`, `registry.go`, `registry_test.go` | 어댑터 입력 계약·등록·실구현 존재 여부 | 포트/레지스트리만 존재, 구체 어댑터·호출자는 없음 [E07][E08][E14] |
| 상태 흐름 | `internal/state/state.go`, `transition.go`, `state_test.go` | lifecycle 규칙과 검증 범위 | 순수 전이표는 구현·테스트됨; runner 연결은 없음 [E09][E10][E15] |
| 저장소 | `internal/store/*.go`, `migrations/0001_init.sql`, 관련 테스트 | 상태·로그·DAG의 영속 스키마와 구현 범위 | SQLite 연결/마이그레이션/run CRUD 일부 구현; pod 등 CRUD 없음 [E11][E12][E16] |
| 격리 경계 | `internal/worktree/worktree.go`, 테스트 fixture 및 test | worktree 생성·보존·정리의 실제 효과 | `.orca/runs/<id>` 생성 및 shipped/killed 위치로 이동은 구현·테스트됨 [E13][E16] |
| 품질/배포 | `.github/workflows/ci.yml`, `release.yml`, `.golangci.yml` | CI가 실제 보장하는 범위와 release 권한 | vet/lint/race test, 태그 release는 `contents: write` 권한 [E18][E19] |
| 계획 패키지 | `internal/{config,constraint,mcp,pod,runner,tui}/doc.go` | README 기능별 구현 유무 교차 확인 | 설명 주석만 존재; 구현·테스트·CLI wiring 없음 [E20] |

## 확인된 기술 스택과 실행 경로

- Go 1.25 module이며 Cobra로 CLI를 만들고 `modernc.org/sqlite`로 CGO 없이 SQLite를 연다.[E05][E06][E11]
- 실제 현행 경로: 셸의 `orca version` → `cmd/orca/main.go` → `cli.Execute()` → Cobra `rootCmd` → `versionCmd` 출력이다. 오류가 나면 프로세스는 exit code 1로 끝난다.[E04][E05]
- 구현되어 있지만 아직 CLI/runner가 호출하지 않는 재사용 가능 요소는 (1) `Adapter` 포트와 동시성 안전 registry, (2) 순수 상태 전이표, (3) SQLite migration과 runs CRUD 일부, (4) git worktree 생성/보관이다.[E07]-[E13]

## 문서 주장과 코드의 불일치

| README 주장 | 고정 SHA에서의 코드 확인 | 판정 |
| --- | --- | --- |
| 12개 CLI 명령과 MCP server | root command에는 `version`만 `AddCommand`; MCP package는 `doc.go`만 존재 | 미구현/미검증 [E03][E05][E20] |
| Claude/Codex/Aider 등 어댑터 | 인터페이스와 factory registry만 있고 concrete adapter package/등록 호출이 없음 | 미구현/미검증 [E03][E07][E08] |
| Bubble Tea TUI | `go.mod`에 Bubble Tea가 없고 TUI package는 `doc.go`만 존재; README 이미지 asset도 없음 | 미구현/미검증 [E03][E06][E20][E21] |
| config init/validate와 `.orca` 정책 | config/constraint package가 설명 주석뿐이고 CLI wiring 없음 | 미구현/미검증 [E03][E20] |
| “Zero dependencies” | Node/Python/Docker 런타임은 쓰지 않는다는 설명은 문서에 있으나, 빌드에는 Cobra·SQLite·UUID·testify 직접 의존성이 명시됨 | 외부 런타임 의존성이라는 뜻일 수 있으나, 코드 의존성 0이라는 뜻으로는 부정확 [E03][E06] |

## 미확인 범위

- 이 SHA에는 `DOCS.md`, `CONTRIBUTING.md`, README의 이미지 asset이 없어서 문서 링크와 TUI 화면을 확인하지 못했다.[E21]
- 원격 GitHub repository의 Actions 실행 이력, release artifact, Homebrew tap, 실제 MCP 클라이언트 설정 호환성은 읽지 않았다. 이 아카이브는 고정 커밋의 소스만 다룬다.
- 소스를 clone하지 않았으므로 이 워커가 `go test`나 바이너리 실행을 수행한 결과는 없다. CI 정의와 repository 내 테스트 코드를 읽은 증거만 있다.[E18]
