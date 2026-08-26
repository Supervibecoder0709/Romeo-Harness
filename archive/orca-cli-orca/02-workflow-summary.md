# 워크플로우 요약

## 현재 실제로 동작 경로가 확인된 범위

### 무엇을 하는가

현재 바이너리는 Cobra 기반 `orca` 명령의 골격을 실행하며, 확인된 하위 명령은 빌드 시 주입된 버전 정보를 출력하는 `orca version`뿐이다. 멀티 에이전트 실행 자체는 이 커밋에서 연결되어 있지 않다.[E04][E05]

### 입력

- 셸 인자. 확인된 유효 하위 명령은 `version`이다.
- 릴리스 빌드일 때 GoReleaser가 `Version`, `Commit`, `Date` 값을 linker flag로 주입한다.[E05][E17]

### 처리 단계

1. `cmd/orca/main.go`가 `cli.Execute()`를 호출한다.[E04]
2. `rootCmd.Execute()`가 Cobra 인자를 해석한다. Cobra가 오류를 반환하면 프로그램은 exit code 1로 종료한다.[E05]
3. `versionCmd`가 stdout에 `orca <version> (commit: <commit>, built: <date>)`를 출력한다.[E05]

### 출력/상태

- 관찰 가능한 출력은 표준 출력의 버전 한 줄이며, 상태 DB·worktree·원격 API는 이 경로에서 변경하지 않는다.[E05]
- GoReleaser 설정상 release build는 Linux/macOS × amd64/arm64용 `orca` binary와 checksum을 만들도록 되어 있다. Windows archive override는 있으나 build `goos` 목록에 Windows가 없어 Windows binary 생성은 이 설정만으로 확인되지 않는다.[E17]

### 실패·재시도

- CLI 진입점은 Cobra 오류를 exit code 1로 전달한다.[E05]
- 현재 `version` 경로의 재시도 정책은 없다. README에 적힌 `orca retry`는 root command에 등록된 구현으로 확인되지 않는다.[E03][E05]

### 관찰 증거

- 로컬에서 바이너리를 실제 실행하지는 않았다. 소스상 최종 출력 호출은 `internal/cli/version.go` 20–21행이고, CI는 `go vet`, lint, `go test -race`를 정의한다.[E05][E18]

## 구현되었지만 아직 하나의 제품 흐름으로 연결되지 않은 기반 요소

아래는 README의 기능을 “현재 제공”으로 해석해서는 안 되는 이유이자, 향후 runner가 연결할 수 있는 경계다.

### 상태 전이

**입력:** `state.Apply(from, event)`에 상태와 이벤트를 전달한다.  
**처리:** 전이표가 legal pair만 목표 상태로 바꾸고 나머지는 `ErrIllegalTransition`을 반환한다.  
**출력/상태:** 순수 함수의 반환값일 뿐 DB·worktree·agent process에 부수 효과가 없다. `pending`은 코드에 있지만 README lifecycle 그림에는 없다.[E09][E10][E15]

### SQLite 저장소

**입력:** 파일 경로 또는 `:memory:`와 `Run` 객체/필터/상태.  
**처리:** SQLite를 열고 WAL, foreign keys, migration을 적용한다. run 생성·조회·목록·상태 업데이트는 구현되어 있다.  
**출력/상태:** DB table에는 pods, runs, DAG dependency, context files, constraints, logs, immutable events와 FTS5 index가 정의되어 있다.[E11][E12]

**중요한 한계:** `UpdateStatus`는 `state.Apply`를 부르지 않고 전달받은 문자열을 바로 저장하며, 현재 DB schema에도 status CHECK 제약이 없다. 따라서 runner가 연결되기 전에는 lifecycle 보호 장치가 아니라 데이터 접근 API일 뿐이다.[E10][E12]

### git worktree 격리

**입력:** primary repo root, run ID, base branch.  
**처리:** `git rev-parse`로 root를 정규화하고, 비어 있지 않은 base branch를 확인한 다음 `.orca/runs/<runID>`에 `orca/<runID>` branch worktree를 만든다. archive는 directory를 `_shipped` 또는 `_killed` 아래로 옮기고 `git worktree prune`을 best-effort로 수행한다.[E13]

**출력/상태:** 파일 시스템과 git worktree registry가 바뀐다. 이 조작은 테스트에서 생성·보관·registry 제거까지 확인하지만, current CLI가 호출하지는 않는다.[E13][E16]

### 어댑터 포트

**입력:** run ID, worktree absolute path, prompt, context files를 담은 `LaunchRequest`; adapter-specific config.  
**처리:** interface는 환경 검증과 launch를 요구하고 registry가 이름별 factory를 동시성 안전하게 보관한다.  
**출력/상태:** `Handle`(PID/session ID) 또는 에러를 반환한다. 구체 adapter, credential 처리, process wait, 결과를 상태/DB에 반영하는 호출 경로는 없다.[E07][E08][E14]

## README가 그리는 목표 워크플로우 — 현재 미구현

README는 goal → pod DAG → isolated worktrees → constraints → review/ship 및 MCP server 흐름을 설명한다.[E03] 그러나 이를 실행하는 command, runner, pod manager, constraint engine, MCP server, PR publisher의 코드가 이 SHA에는 없다.[E05][E20] 따라서 아래 흐름은 **제품 의도**로만 기록하며, 운영 설계나 도입 검증의 완료 증거로 쓰면 안 된다.

```text
문서상 의도: goal → pod/run 생성 → adapter 실행 → constraints → ready → 사람 review/ship
코드상 확인: version CLI | 상태 전이 함수 | SQLite 기반 API 일부 | worktree helper
연결 경로: 확인되지 않음
```
