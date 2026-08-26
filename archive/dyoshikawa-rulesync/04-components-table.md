# 구성요소 표

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `src/cli/index.ts` + `program.ts` | CLI 진입점 | `rulesync` 명령을 Commander handler에 연결 | argv, 현재 작업 디렉터리 | 각 command 실행·종료 코드 | 로컬 process/stdio | `src/cli/index.ts:1-13`, `src/cli/program.ts:40-401` | 확인됨 [S2] |
| ConfigResolver | 설정 해석 | config 우선순위·schema·root를 확정 | CLI, `rulesync.jsonc`, `rulesync.local.jsonc`, defaults | 불변 Config 또는 validation error | 로컬 파일 시스템; path validation | `src/config/config-resolver.ts:54-91, 228-402` | 확인됨 [S14] |
| processor registry | adapter 등록부 | 9개 feature와 각 processor/factory를 결속 | feature/target 선택 | feature별 도구 형식 변환 경로 | 로컬 파일 시스템 | `src/types/processor-registry.ts:66-132` | 확인됨 [S13] |
| Generate | 핵심 쓰기 오케스트레이터 | source를 target 도구 파일로 생성·동기화 | Config, `.rulesync/`, logger | 생성/삭제 수·경로·`hasDiff` | output root에 쓰기·`--delete` 시 orphan 삭제 | `src/cli/commands/generate.ts:105-221`, `src/lib/generate.ts:69-168, 524-600` | 확인됨 [S5] |
| shared-file order | 데이터 손실 방지 guard | 공유 설정 파일의 feature 쓰기 순서를 강제 | processor registry·settable paths | 순서 보장 또는 unknown/cycle/unordered writer error | 로컬 shared config 파일 | `src/lib/generate.ts:224-379`, `src/lib/shared-file-derive.ts:18-41, 142-220` | 확인됨 [S15] |
| Import | 역변환 | 한 도구의 기존 설정을 Rulesync source로 변환 | 하나의 target·도구 파일 | `.rulesync` 파일/디렉터리 생성 | 로컬 파일 읽기·쓰기; plugin root safety check | `src/cli/commands/import.ts:17-79`, `src/lib/import.ts:79-155` | 확인됨 [S6] |
| Convert | 메모리 내 변환 | source tool을 destination tool로 직접 변환 | `--from`, `--to`, features | 목적 도구 파일; `.rulesync` 중간 파일은 미작성 | 로컬 파일 읽기·쓰기; same tool 거부 | `src/cli/commands/convert.ts:30-117` | 확인됨 [S7] |
| Fetch | 원격 source 수집 | Git source를 받아 Rulesync 형식으로 변환 | owner/repo, ref, path, token 등 | 임시 다운로드 후 Rulesync output 작성·요약 | GitHub/GitLab API, token, 로컬 temp/output | `src/cli/commands/fetch.ts:12-66`, `src/lib/fetch.ts:751-798` | 확인됨 [S8] |
| `rulesyncTool` | MCP 단일 도구 | feature/operation으로 source CRUD와 run을 다중화 | MCP args, CWD | source read/write/delete 또는 generate/import/convert | stdio MCP → 현재 CWD의 로컬 파일 쓰기·삭제 | `src/cli/commands/mcp.ts:9-26`, `src/mcp/tools.ts:36-100, 404-456` | 확인됨 [S9] |
| `doctor` | read-only 진단 | config 오류·warning/info를 수집 | config 파일, `--strict` | diagnostics/JSON, code 0 또는 1 | 로컬 파일 읽기만 | `src/cli/commands/doctor.ts:687-780` | 확인됨 [S16] |
| 서브에이전트 5개 | agent 정의 | 코드 리뷰, diff 분석, PR 생성·병합, 보안 리뷰 지시 | agent prompt, repo/PR 상태 | 원문 지시상 review/diff 또는 PR write 가능 | git fetch; `pr-handler` push/PR; `pr-merger` admin squash merge | `.rulesync/subagents/*.md` | 확인됨 [S18] |
| `agent-team` | Claude Code skill | implementer/reviewer 반복 운영 | TASK, reviewer findings | Converged/Capped 보고 | agent 위임; 정의상 직접 commit/PR 금지 | `.rulesync/skills/agent-team/SKILL.md:1-105` | 확인됨 [S20] |
| `rulesync` skill | 배포용 skill | Rulesync의 표준 작업 순서와 docs 사용법 제공 | 사용자 작업/CLI | 명령 실행 안내 | 실행 자체의 승인 정책은 정의하지 않음 | `skills/rulesync/SKILL.md:1-69` | 확인됨 [S19] |
| 나머지 공식 skills 40개 | skill assets | tree에 존재만 확인 | 미열람 | 미확인 | 미확인 | `.rulesync/skills/*/SKILL.md` | **미확인** [S17] |
