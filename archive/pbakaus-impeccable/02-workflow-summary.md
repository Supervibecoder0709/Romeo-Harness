# 워크플로우 요약

## 1. 설치와 skill 호출

**무엇을 하는가**

Impeccable은 backend 서비스가 아니라 AI coding harness 안에 설치되는 디자인 작업 규칙·reference·script 묶음과, 이를 설치/검출하는 CLI다. 사용자는 terminal에서 `npx impeccable install` 또는 `update`를 실행한 뒤, harness chat에서 `/impeccable init`, `/impeccable audit` 같은 명령을 쓴다. terminal의 `npx impeccable init`은 의도적으로 실패한다. [E1] [E2]

**입력**

- CLI: 설치 대상 provider, project/global scope, 선택적으로 `--providers`, `--scope`, hook 설치 여부.
- skill: sub-command와 선택 target, 작업 중인 프로젝트의 context 파일.

**처리 단계**

1. CLI가 명령을 install/link/update/check 또는 detector로 라우팅한다. [E2]
2. skill은 한 세션에 한 번 context를 읽고, 요청을 소유하는 reference playbook 하나를 고른다. 새 surface/교체 작업이면 `new-work`, 좁은 기존 UI 정제면 incumbent visual truth를 먼저 읽는다. [E7]
3. `init` 이후 기록한 `PRODUCT.md`/`DESIGN.md`와 surface brief가 후속 명령의 설계 맥락이 된다. [E1] [E7]

**출력/상태**

- provider의 skill/hook 파일, project/user harness 폴더, `PRODUCT.md`/`DESIGN.md`, `.impeccable` 작업 상태.
- Codex는 skill과 project hook의 발견 위치가 다르다: `.agents/skills/` 및 `.codex/hooks.json`. [E1] [E4]

**실패·재시도**

- CLI는 알 수 없는 bare command를 loud failure로 끝내며, `init`을 shell에서 실행한 경우 chat 명령이라는 안내와 함께 exit 1 한다. [E2]
- 잘못된 hook manifest는 기본적으로 install/update를 중단하며, README는 `--force`일 때 backup 후 교체한다고 설명한다. 실제 설치 구현의 전체 backup 동작은 이번 분석에서 미확인이다. [E1]

**관찰 증거**

- CLI help/exit code, provider 폴더에 설치된 skill 및 hook manifest, `/skills`에서 발견된 skill, `PRODUCT.md`/`DESIGN.md` 생성 여부.

## 2. 디자인 검사와 hook

**무엇을 하는가**

CLI detector는 파일·디렉터리·URL을 스캔하고, provider-native hook은 agent가 UI 파일을 수정한 뒤 같은 detector의 결과를 agent flow에 되돌린다. [E1] [E2] [E10]

**입력**

- `npx impeccable detect [file-or-dir-or-url...]`, ignore 설정, 또는 provider가 stdin으로 보내는 hook event.

**처리 단계**

1. `detect`는 detector engine을 import해 실행한다. bundled detector가 없으면 error exit 1이다. [E2] [E11]
2. hook은 `PostToolUse`이면 방금 수정한 파일을 immediate-tier로, `Stop`이면 해당 session의 touched UI file을 full rule set으로 검사한다. [E10]
3. finding이 있으면 additional context로 반환하며 audit log가 설정됐으면 NDJSON 기록을 시도한다. [E1] [E10]

**출력/상태**

- detector finding 또는 JSON output, ignore 설정, 선택적인 hook audit log.

**실패·재시도**

- hook entrypoint는 parser/실행 예외를 삼키고 항상 0으로 끝나도록 설계되어 agent turn을 막지 않는다. 따라서 “hook이 오류 없이 끝남”은 detector가 충분히 검사했거나 finding이 없었다는 증거가 아니다. [E10]

**관찰 증거**

- 명시적 `npx impeccable detect --json ...` 결과, hook additionalContext, 설정한 audit NDJSON, 수정 전후 source/화면 검사.

## 3. live browser iteration

**무엇을 하는가**

`/impeccable live`는 실제 app의 dev/preview URL 위에서 요소별 visual variant를 반복하기 위한 준비와 poll protocol을 만든다. helper server의 port는 웹 앱 URL이 아니라 `/live.js`·`/poll` 보조용이라는 점이 명시돼 있다. [E9]

**입력**

- 현재 cwd 또는 `--target`, `.impeccable/live/config.json`, `PRODUCT.md`, `DESIGN.md`, 선택적으로 surface brief.

**처리 단계**

1. monorepo에 여러 app이 있으면 선택 요구 JSON을 출력하고, agent가 사용자에게 어떤 app인지 물어야 한다. [E9]
2. `PRODUCT.md`/`DESIGN.md`가 없거나 비어 있으면 context_missing JSON과 다음 명령(`init` 또는 `document`)을 출력한다. [E9]
3. roots를 저장하고 config 검증 후 helper server를 reuse/start하고, project entry에 browser script를 inject한다. [E9]
4. resolved page files·context·drift warning·server port/token·지시문을 JSON으로 내보낸 뒤 harness-native poll loop가 이어진다. [E9]

**출력/상태**

- `.impeccable/live/config.json`, `.impeccable/live/server.json`, sessions/annotations 등의 live state; injected page entry; success/failure JSON.

**실패·재시도**

- config/context/target 선택이 부족하면 서버 기동 전에 fail-fast한다. server PID가 stale하면 정보 읽기 함수가 파일 삭제를 시도하고 새 server를 시작한다. [E9] [E11]
- 이 아카이브는 live session을 실행하지 않았으므로 실제 injection 복구, poll event의 end-to-end 성공, source apply 여부는 미확인이다.

**관찰 증거**

- live JSON의 `ok`, `projectRoot`, `pageFiles`, `liveConfigPath`, `serverPort`; browser에서 실제 dev URL; `.impeccable/live/server.json`; poll/accept receipt와 수정된 source 및 다시 캡처한 화면.

## 4. 원본 빌드·검증·release

**무엇을 하는가**

`skill/` 원본을 provider별 harness 문서·agent·hook으로 변환하고 ZIP 및 일부 browser artifact를 만든다. CI는 source build와 tracked output drift를 검사하고, sync workflow는 main의 provider output drift를 생성 commit으로 맞춘다. [E4] [E5] [E12] [E14]

**입력**

- source skill, transformers, CLI detector registry, package scripts, build 환경(Node/Bun).

**처리 단계**

1. build는 command table과 detector registry로 공개 count를 계산하고 stale user-facing claim을 검증한다. [E4]
2. CI는 Node 22.18.0·24 matrix에서 core tests를 실행하고 변경 범위별 detector/live/framework tests, build, extension build, generated output diff check를 조건부로 실행한다. [E12]
3. opt-in live E2E는 framework fixtures와 Playwright Chromium을 쓰며, 일부 provider-backed suites는 key가 없으면 skip한다. [E5] [E12] [E13]
4. release script는 clean tree·pushed HEAD·version/changelog/artifact를 확인하고, skill/extension은 build re-run 뒤 drift가 없을 때 tag/release를 생성한다. [E6]

**출력/상태**

- `dist/`, `build/`, root provider output, ZIP, CI artifact, Git tag/GitHub release(실제 release 수행 시).

**실패·재시도**

- sync workflow는 main 경쟁으로 push가 안 되면 최대 5회 최신 main에서 rebuild 후 재시도한다. [E14]
- release script의 실제 tag/push/release는 상태 변경 경계다. 이 읽기 전용 분석은 실행하지 않았고, 이 SHA가 release 가능한지 또는 release됐는지는 미확인이다.

**관찰 증거**

- `bun run build`/선택 suite exit code, CI run 결과, `git diff --exit-code` 결과, generated output commit SHA, GitHub release/tag와 업로드 artifact.
