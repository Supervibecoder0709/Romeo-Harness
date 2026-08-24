# PM Harness 운영 노트

## 결론과 추천

**추천:** Rulesync를 도입한다면 `project scope` + source를 Git으로 관리 + `doctor → dry-run → 사람 diff 승인 → generate → check`의 5단계 gate를 기본 Harness로 쓰는 것이 가장 적합하다. 이 도구는 여러 AI agent의 지시문을 한 곳에서 관리하는 이점이 있지만, `generate --delete`, MCP의 `put/delete/run`, PR 병합 agent처럼 실제 파일·원격 상태를 바꾸는 권한도 포함하므로, "규칙 편집"과 "도구별 파일 반영"을 하나의 자동 승인으로 묶으면 운영·보안 비용이 급격히 커진다. [S5] [S9] [S18]

**이 추천이 달라지는 조건:** 개인 전역 설정을 의도적으로 통합해야 하고 전용 테스트 환경이 있다면 `--global`을 별도 change request로 운영할 수 있다. 다만 global은 home directory가 output root가 되므로, 일반 프로젝트 변화보다 영향 범위와 복구 난도가 커진다. [S14]

## 입력 계약

1. source of truth는 `.rulesync/`와 `rulesync.jsonc`다. `rulesync.local.jsonc`가 있으면 같은 key에서 우선하므로, 운영 규칙과 개인 로컬 override를 분리해 누가 무엇을 바꿨는지 기록해야 한다. [S14]
2. `targets`를 object 형식으로 써 target별 feature를 지정할 때는 별도 `features`를 같이 쓰면 안 된다. base/local file을 합친 뒤에도 이 규칙이 검사된다. [S14]
3. `inputRoot`는 source 위치를 output과 분리한다. config의 `global: true`와 결합하면 예상 밖의 home directory 변경이 될 수 있어, resolver는 CLI `--global`을 명시하지 않은 경우 config의 global을 버리고 warning을 낸다. [S14]

## 권한과 사람 승인 지점

| 단계 | 허용할 자동화 | 사람이 승인해야 할 지점 | 완료 증거 |
| --- | --- | --- | --- |
| 진단 | `rulesync doctor --strict` | 없음(읽기 전용) | diagnostics와 종료 코드 |
| 계획 | `rulesync generate --dry-run` | target/features/output root, 삭제 예정 diff | dry-run 출력과 대상 파일 목록 |
| 반영 | `rulesync generate` | `--delete`, `--global`, 여러 output root, plugin root | 생성 요약 + Git diff/readback |
| CI gate | `rulesync generate --check` | 없음(검증) | code 0; 차이가 있으면 code 1 |
| MCP | `list/get` | 모든 `put/delete`, `generate/import/convert run` | 호출 인자, 반환 JSON, 파일 readback |
| GitHub agent | 리뷰/요약 | commit/push/PR 생성, `--admin --squash` merge | PR URL, commit SHA, merge 상태 |

이 표의 approval gate는 source code가 제공하는 자동 승인 기능이 아니라, 파일 시스템 권한을 가진 CLI/MCP를 안전하게 운영하기 위한 **추천**이다. 특히 repo 내부 설정의 `delete: true`는 현재 source에 없는 managed 결과물을 제거할 수 있으므로 기본으로 무인 실행하지 않는 편이 안전하다. [S5] [S21]

## 모델·에이전트 역할

**확인된 사실:** Rulesync의 runtime은 특정 LLM 모델을 호출하지 않는다. 이 레포의 `.rulesync/subagents`는 target `*`에 배포될 agent instruction이고, `agent-team`은 `claudecode`용 역할 분리 스킬이다. [S18] [S20]

**운영 판단:** `code-reviewer`와 `security-reviewer`를 변경 writer가 아닌 review-only 역할로 고정하고, `pr-handler`/`pr-merger`에는 최소한의 GitHub 권한과 명시 승인 token만 준다. 정의상 `pr-merger`는 admin squash merge를 지시하므로, PM Harness에서 가장 높은 위험 작업이다. [S18]

## 재실행·복구

- **재실행 가능:** default generate는 변한 파일만 쓰며, zero writes는 성공 no-op이다. `--check`는 drift 검출에 쓸 수 있다. [S5]
- **안전한 복구:** 반영 전 dry-run 결과와 Git diff를 보관하고, 반영 뒤 target 파일을 readback한다. `--delete`를 쓰기 전에는 삭제 대상 목록을 승인 artifact에 넣고, Git으로 추적되는 생성 파일은 commit 전 diff에서 검토한다. 이는 **추천**이며, Rulesync가 자동 backup/rollback을 제공한다는 근거는 확인하지 못했다.
- **watch 유의:** watcher는 config 경로/inputRoot 변화 뒤 자동으로 watch 대상 집합을 다시 만들지 않으므로 재시작이 필요하다. [S5]

## 확장 지점과 검증 한계

- `PROCESSOR_REGISTRY`가 feature 추가의 중심 지점이며, tool-specific factory가 형식 변환을 맡는다. 새로운 target은 processor/factory·지원표·테스트를 함께 바꾸는 개발 작업으로 취급해야 한다. [S13] [S15]
- CI는 `pnpm cicheck`, build, 빌드 뒤 git clean, dist artifact 존재를 확인하며, 별도 workflow는 Linux/macOS/Windows binary E2E를 정의한다. 그러나 이 아카이브는 workflow run 성공을 보지 않았으므로 CI 통과 상태는 **미확인**이다. [S22] [S23]
- MCP 단일 tool 설계는 tool-definition token을 줄이지만, feature/operation 하나에 쓰기와 삭제가 같이 들어간다. Harness에서는 operation allowlist와 호출 로그가 필요하다는 점은 **추천**이다. [S9]
