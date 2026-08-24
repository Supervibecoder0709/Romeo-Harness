# 구성요소 표

근거 상태에서 “확인됨”은 고정 SHA의 실행 코드 또는 설정을 열어 본 항목, “부분 확인”은 인터페이스/스키마/문서 주석만 존재하는 항목, “미확인”은 해당 구현 경로가 없는 항목이다.

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cmd/orca` | CLI 진입점 | `cli.Execute` 호출 | 셸 인자 | Cobra 실행으로 위임 | 로컬 process | `cmd/orca/main.go:6-8` | 확인됨 [E04] |
| `cli.rootCmd` | CLI shell | root command와 오류 exit | 셸 인자 | 오류 시 exit 1 | 로컬 process | `internal/cli/root.go:9-20` | 확인됨 [E05] |
| `cli.versionCmd` | CLI command | version/commit/date 출력 | `orca version` | stdout 한 줄 | 로컬 stdout | `internal/cli/version.go:9-26` | 확인됨 [E05] |
| `adapter.Adapter` | port/interface | agent validate/launch 계약 | config, context, launch request | handle 또는 error | 장래 agent binary/credentials 경계이나 현 구현 없음 | `internal/adapter/adapter.go:15-97` | 부분 확인 [E07] |
| `adapter.Registry` | in-memory registry | adapter factory register/get | name, factory, config | Adapter 또는 duplicate/not-found error | process memory | `internal/adapter/registry.go:19-69` | 확인됨 [E08] |
| `state.Apply` | domain rule | 허용 lifecycle 전이 판정 | from status, event | next status 또는 illegal-transition error | 외부 I/O 없음 | `internal/state/transition.go:9-55` | 확인됨·단위 테스트 [E10][E15] |
| `store.Store` | persistence adapter | DB 열기/migrate/runs CRUD 일부 | DB path, Run/filter/status | SQLite data 변경/조회 | 로컬 DB file | `internal/store/{store,migrate,runs,ids}.go` | 확인됨·부분 테스트 [E11][E16] |
| initial schema | DB schema | pod/run/DAG/log/audit/FTS 구조 정의 | embedded SQL | table/index/trigger 생성 | 로컬 SQLite | `internal/store/migrations/0001_init.sql:13-120` | 확인됨 [E12] |
| `worktree.CreateForRun` / `Archive` | local isolation | run별 git worktree 생성·보관 | repo root, run ID, branch/kind | git branch/worktree와 filesystem 변경 | local git, filesystem | `internal/worktree/worktree.go:49-135` | 확인됨·단위 테스트 [E13][E16] |
| CI | quality gate | vet/lint/race test, coverage artifact | push/PR | Actions run/artifact | GitHub Actions | `.github/workflows/ci.yml:3-56` | 설정 확인됨 [E18] |
| release workflow | release automation | tag build/release | `v*` tag | GitHub release write 가능 | GitHub token, release action | `.github/workflows/release.yml:3-35` | 설정 확인됨; 실행 이력 미확인 [E19] |
| config/constraint/mcp/pod/runner/tui | planned package | 각 기능의 목표 역할 설명 | 미구현 | 미구현 | 권한/외부 API/실패 처리 미확인 | `internal/*/doc.go` | 미구현/미확인 [E20] |
| agent/skill definitions | agent/skill config | 없음 | 없음 | 없음 | 없음 | fixed tree 전체 | 정의 파일 없음 [E02] |
