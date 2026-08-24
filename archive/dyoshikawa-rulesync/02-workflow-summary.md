# 워크플로우 요약

## 무엇을 하는가

**확인된 사실:** Rulesync는 프로젝트의 통합 source인 `.rulesync/`를 여러 AI 코딩 도구가 읽는 규칙·명령·MCP·서브에이전트·스킬·hook·권한·check 형식으로 변환하는 Node.js CLI다. processor registry에는 이 9개 feature가 명시되어 있다. [S13]

## 입력

1. `.rulesync/` 아래의 source 파일·디렉터리와 `rulesync.jsonc`/`rulesync.local.jsonc`.
2. CLI 옵션(예: `--targets`, `--features`, `--output-roots`, `--global`, `--dry-run`, `--check`, `--delete`).
3. 선택적으로 기존 AI 도구 설정(`import`) 또는 원격 Git 저장소 source(`fetch`).

**설정 우선순위(확인됨):** CLI 옵션 > `rulesync.local.jsonc` > `rulesync.jsonc` > 내장 기본값이다. 기본 target은 `agentsmd`, 기본 feature는 `rules`이다. [S14]

## 처리 단계

1. **초기화:** `rulesync init`은 이미 있는 파일을 덮어쓰지 않고 config 및 rule/MCP/subagent/skill/hooks/permissions 샘플을 만든다. [S4]
2. **설정 해석:** resolver가 JSONC를 읽고 schema·경로·`targets` 객체형과 `features`의 상호 배타성을 확인한 뒤, source root와 output root를 확정한다. `inputRoot`가 설정되면 config 파일의 `global: true`를 기본적으로 무시하고 경고한다. [S14]
3. **생성:** `.rulesync` 존재를 확인하고 9개 feature processor에 source를 전달한다. 각 processor가 선택 target·scope에 맞는 AI 도구 파일/디렉터리로 바꾸고 쓴다. feature가 동일한 설정 파일을 함께 수정하면 의존 그래프를 위상 정렬해 순서를 고정하고, 순서가 없거나 cycle이면 오류로 중단한다. [S5] [S15]
4. **대체 입력 흐름:** `import`는 정확히 하나의 tool을 선택해 기존 설정을 Rulesync source로 쓴다. `convert`는 source tool -> 메모리 내 Rulesync 표현 -> destination tool로 변환하여 `.rulesync/` 중간 파일은 만들지 않는다. `fetch`는 Git source를 임시 영역에 받아 Rulesync 형식으로 변환한다. [S6] [S7] [S8]
5. **MCP 흐름:** `rulesync mcp`는 stdio 서버에 단 하나의 `rulesyncTool`을 등록한다. 이 도구는 feature와 operation에 따라 Rulesync source의 list/get/put/delete 또는 generate/import/convert run을 실행한다. [S9] [S10]

## 출력과 상태 변화

- 기본 generate는 선택한 output roots의 도구별 구성 파일을 쓰며, 실제 바뀐 파일 수·경로·`hasDiff`를 결과로 만든다. 변경이 없으면 성공 no-op이다. [S5]
- `--delete`가 참이면 현재 source가 더 이상 만들지 않는 managed 파일/디렉터리를 orphan으로 판단해 제거한다. 따라서 source/target 선택 오류가 파일 삭제로 이어질 수 있다. [S15]
- `--dry-run`은 쓰지 않고 예정 변경을 출력한다. `--check`는 차이가 있으면 code 1로 실패시켜 CI gate가 될 수 있다. [S5] [S12]
- MCP의 `put`과 `delete`, `generate`/`import`/`convert` run은 현재 작업 디렉터리의 파일을 바꿀 수 있다. MCP 서버는 호출자에게 별도의 승인 체계를 코드상 강제하지 않는다. [S9] [S10]

## 실패·재시도

- source 디렉터리가 없으면 generate는 `rulesync init`을 안내하며 실패한다. 지원하지 않는 target/feature 조합은 일부 경우 경고하고 skip한다. [S5] [S15]
- 설정 진단은 `rulesync doctor`가 read-only로 parse/unknown key/target/feature/병합 오류/inputRoot 등을 수집한다. error(또는 `--strict`의 warning)가 있으면 code 1이다. [S16]
- watch 모드는 `--check`, `--dry-run`, `--json`과 결합할 수 없고, 변경 이벤트에서 실패해도 watcher는 다음 변경을 기다린다. 설정 위치·inputRoot를 바꿨다면 watcher를 재시작해야 한다. [S5]
- 이 아카이브는 retry 백오프·원격 fetch 실패 시 자동 재시도 정책을 확인하지 못했다. **미확인**이다.

## 관찰 증거

권장 관찰 순서는 `rulesync doctor --strict` → `rulesync generate --dry-run` → 생성 대상 파일의 diff 검토 → `rulesync generate --check`다. `--check` 성공과 생성된 파일의 실제 readback을 함께 남겨야 "설정은 되었지만 원하는 파일이 안 바뀐" 상황을 줄일 수 있다. 이 순서는 코드상 명시된 `doctor`의 read-only 성격과 generate의 check/dry-run 계약에서 도출한 **추천**이다. [S5] [S16]
