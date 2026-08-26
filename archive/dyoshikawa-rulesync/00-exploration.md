# 탐색 기록

## 범위와 소스 고정

분석 대상은 `dyoshikawa/rulesync`의 `main`이 가리키던 커밋 `c3acceacec5463efe14ebb1b8be5fed5fa835e65`다. 전체 clone 대신 Git tree API로 경로만 수집한 뒤 후보 파일만 raw로 읽었다. 정확한 URL·시간·제외 범위는 [_source.md](_source.md)에 있다.

## 실제로 연 파일과 선정 이유

| 구분 | 원문 파일 | 선정 이유 |
| --- | --- | --- |
| 제품 안내 | `README.md`, `docs/getting-started/quick-start.md`, `docs/guide/dry-run.md`, `docs/reference/mcp-server.md` | 사용 흐름과 안전한 검증 옵션을 확인 |
| 배포·실행 계약 | `package.json`, `src/cli/index.ts`, `src/cli/program.ts`, `src/cli/wrap-command.ts` | npm 바이너리와 모든 명령 등록·오류/JSON 출력 진입점을 확인 |
| 핵심 상태 변경 | `src/cli/commands/{init,generate,import,fetch,convert}.ts`, `src/lib/{init,generate,import,fetch}.ts` | 초기화·생성·가져오기·원격 파일 수집이 실제 파일을 어떻게 다루는지 확인 |
| 설정·구성요소 | `src/config/config-resolver.ts`, `src/types/processor-registry.ts`, `src/features/skills/skills-processor.ts`, `src/lib/shared-file-derive.ts` | 옵션 우선순위, 9개 feature, 도구별 adapter와 공유 파일 쓰기 순서를 확인 |
| MCP | `src/cli/commands/mcp.ts`, `src/mcp/{tools,generate,mcp}.ts` | 하나의 MCP 도구, stdio, 쓰기·삭제 경계를 확인 |
| 검증 | `.github/workflows/{ci,e2e-binaries}.yml`, `src/lib/generate.test.ts`, `src/cli/commands/doctor.ts` | CI가 무엇을 실행하고, 생성/설정 오류를 어떻게 검출하는지 확인 |
| 레포 내부 운영 자산 | `rulesync.jsonc`, `.rulesync/{permissions.jsonc,hooks.json}`, `.rulesync/subagents/*.md`, `.rulesync/skills/agent-team/SKILL.md`, `skills/rulesync/SKILL.md` | 이 저장소가 Rulesync를 자기 자신에 적용하는 방식과 agent/skill 계약을 확인 |

## 확인된 진입점과 기술 스택

**확인된 사실.** npm 패키지의 `rulesync` 실행 파일은 `dist/cli/index.js`이고, 개발 시에는 `tsx src/cli/index.ts`를 쓴다. `src/cli/index.ts`는 `createProgram().parse()`로 시작하고, `program.ts`는 Commander 명령을 각 handler에 연결한다. TypeScript ESM, Node.js 22 이상, pnpm 10 이상이며, build는 `tsdown`, unit test는 Vitest, 문서는 VitePress다. [S1] [S2] [S3]

**확인된 핵심 흐름.** `init`은 `.rulesync/`와 샘플 source·`rulesync.jsonc`를 만든다. `generate`는 source를 feature별 processor로 변환해 선택한 AI 도구의 파일을 쓰고, `import`는 한 도구의 기존 파일을 Rulesync 형식으로 가져오며, `convert`는 `.rulesync`를 중간 파일로 쓰지 않고 메모리에서 도구 간 변환한다. [S4] [S5] [S6] [S7]

**확인된 외부 경계.** `fetch`/`release-notes`는 GitHub API 및 토큰을 사용할 수 있고, `rulesync mcp`는 stdio MCP 서버를 띄워 작업 디렉터리의 Rulesync 파일을 읽고·쓰고·삭제하며 generation/import/convert도 실행한다. 이 경계는 "문서 생성기" 수준보다 강한 로컬 파일 변경 권한이다. [S8] [S9] [S10]

## 미확인 범위

- 패키지를 실제 설치하거나 명령·테스트·workflow를 실행하지 않았다. 그러므로 현재 커밋의 CI 통과, 플랫폼 바이너리 동작, npm 배포본과 고정 SHA의 일치는 **미확인**이다.
- 도구 target은 다수이며, 모든 target/feature 조합 및 42개 공식 스킬을 전수 열람하지 않았다. 대표 코드와 트리 인벤토리만 근거로 하므로 도구별 세부 파일 경로·스킬별 권한은 **미확인**이다.
- README의 "20+" 지원, npm badge, 외부 서비스·문서 링크의 현재 상태는 코드 실행으로 재검증하지 않았다.
