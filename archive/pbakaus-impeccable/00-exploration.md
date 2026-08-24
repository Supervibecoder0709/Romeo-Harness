# 탐색 기록

## 범위와 선정 기준

고정 SHA의 recursive tree를 먼저 확인했다. 이 레포는 하나의 디자인 skill 원본을 여러 AI coding harness 형식으로 변환하고, 별도의 CLI·detector·browser extension·웹 사이트·테스트 fixture를 함께 가진 JavaScript/Bun 프로젝트다. `package.json`은 Node 22.18+ ESM 패키지이며 CLI 진입점은 `cli/bin/cli.js`다. [E2]

3,268개 blob 중 아래 후보를 실제로 열었다. 중요도는 파일명이나 줄 수가 아니라, 사용자 입력을 받는 지점, 파일/프로세스/브라우저/API 경계, 생성물의 진실 원천, 그리고 검증·배포 계약의 영향으로 판단했다.

| 후보 | 선정 이유 | 확인 결과 |
| --- | --- | --- |
| `README.md`, `README.npm.md` | 설치·사용·상태파일·hook·CLI에 대한 이용자 계약 | README의 설치 설명과 CLI 공개 명령을 코드와 교차 확인했다. [E1] [E2] [E3] |
| `AGENTS.md`, `CLAUDE.md` | 원본/생성물 경계, build/test/release 운영 계약 | `skill/`이 원본이고 root harness 폴더는 생성물이라는 정책을 확인했다. [E5] [E6] |
| `skill/SKILL.src.md`와 `skill/agents/*.md` | user-invocable skill과 4개 하위 agent의 입력·출력 계약 | 23개 sub-command router 및 agent 역할/권한/반환 형식을 확인했다. [E7] [E8] |
| `cli/bin/cli.js`, `cli/bin/commands/skills.mjs` | 설치·갱신·detect의 실제 CLI 라우팅 | CLI의 허용 명령과 `init`이 shell 명령이 아니라 harness chat 명령임을 확인했다. [E2] |
| `skill/scripts/live.mjs`, `hook.mjs`, `detect.mjs`, `lib/impeccable-paths.mjs` | live browser, hook, detector, 프로젝트 상태 경계 | live가 config/context를 gate하고 server/injection/poll 준비 JSON을 출력하며, hook은 turn을 깨지 않도록 0으로 종료하도록 설계됨을 확인했다. [E9] [E10] [E11] |
| `scripts/build.js`, `scripts/run-tests.mjs`, `scripts/test-suites.mjs`, `.github/workflows/*.yml`, `scripts/release.mjs` | 원본→공급자 변환, 검증, CI, release 경계 | build·CI·생성물 drift 검증·release preflight를 교차 확인했다. [E4] [E12] [E13] [E14] |
| `tests/live-e2e.test.mjs`, `tests/plugin-e2e.test.mjs`, `tests/skill-behavior/scenarios.test.mjs`, `tests/hook.test.mjs` | 존재하는 회귀·E2E coverage의 범주 확인 | 테스트 파일과 `test-suites`의 suite 등록은 확인했으나 개별 테스트 전문과 실행 결과는 미확인이다. [E13] [E15] |

## 확인된 진입점과 핵심 흐름

1. **배포/설치 경로**: npm binary `impeccable`은 `cli/bin/cli.js`를 시작하고, `install`·`link`·`update`·`check`를 skills 명령 구현으로 보낸다. 제공자별 skill/hook 설치는 CLI 쪽의 파일 쓰기 경계다. [E2]
2. **harness 대화 경로**: 사용자는 `/impeccable <command> [target]`을 입력한다. source skill은 session마다 context를 한 번 읽고, 의도에 맞는 reference playbook 하나를 골라 UI 작업 전에 incumbent visual truth를 확인하도록 지시한다. [E7]
3. **검출 경로**: `npx impeccable detect`는 detector engine을 동적 import한다. 설치된 hook은 UI 파일 edit 뒤 즉시 검출하고 Stop 때 해당 세션의 touched UI file을 더 깊게 검사하되, clean/오류에도 turn을 중단하지 않도록 exit 0 계약을 둔다. [E2] [E10] [E11]
4. **live 경로**: `live.mjs`는 app 선택, `PRODUCT.md`/`DESIGN.md`, live config를 먼저 확인한 뒤 helper server를 재사용 또는 기동하고 브라우저 스크립트를 injection한다. 이후 agent가 poll loop로 들어갈 수 있는 JSON을 낸다. [E9]
5. **개발/릴리스 경로**: `skill/` 원본을 transformer로 각 provider 산출물과 ZIP으로 만들며, CI는 Node 22.18.0·24에서 core test와 변경 범위별 suites/build를 실행하고 tracked generated output drift를 검사한다. 별도 sync workflow는 main에서 생성물 drift가 있으면 최대 5회 재build/push를 시도한다. [E4] [E5] [E12] [E14]

## 기술 스택과 외부 경계

- **확인됨**: Node ESM, Bun, Playwright, optional Puppeteer, CSS/HTML parser 계열 의존성을 사용한다. [E2]
- **확인됨**: 파일 시스템 경계는 대상 프로젝트의 `PRODUCT.md`, `DESIGN.md`, `.impeccable/`과 설치할 harness 폴더다. live server 정보는 `.impeccable/live/server.json`에 저장한다. [E9] [E11]
- **확인됨**: URL detector는 Puppeteer가 필요한 선택 경로이고, 일부 CI는 provider API key가 없으면 skip한다. secret 값·원격 모델 응답은 열지 않았다. [E1] [E12]
- **미확인**: 웹사이트 backend, extension의 실제 Chrome API 권한, npm registry의 현재 published version, GitHub Actions의 최근 성공/실패 결과, private eval repository의 평가 결과.

## 문서-코드 교차 확인 메모

- README는 `npx impeccable install` 뒤 harness에서 `/impeccable init`을 실행하라고 안내한다. CLI 코드도 terminal에서 `init`을 실행하면 agent chat에서 실행하라고 명시적으로 오류를 낸다. 이 부분은 일치한다. [E1] [E2]
- README는 Codex skill이 `.agents/skills/`에 있고 hook은 `.codex/hooks.json`에 있다고 설명한다. build 주석과 installer provider hook mapping도 같은 분리를 명시한다. [E1] [E4]
- README의 “59 deterministic rules” 숫자는 build가 detector registry의 unique id 수로 계산하고 user-facing count를 검사하는 계약을 가진다. 이 아카이브는 registry 전체를 세거나 build를 실행하지 않았으므로, 숫자 자체의 실행 검증이 아니라 고정 SHA의 문서·build 주장으로 기록한다. [E1] [E4]
