# 워크플로우 요약

## 무엇을 하는가

**확인된 사실.** oh-my-agent는 하나의 `.agents/` 디렉터리를 공통 정의로 두고, 여러 AI coding runtime에 agent·skill·workflow·hook을 연결하는 CLI 기반 하네스다. 핵심 차별점은 에이전트의 완료 문장을 신뢰하는 대신, 테스트 게이트·필수 산출물·독립 리뷰·append-only 이벤트로 완료 주장을 반증 가능하게 만들려는 구조다. [E03][E06][E11][E13]

## 입력

| 입력 | 용도 | 유효성/경계 |
|---|---|---|
| 사용자 요청, slash command 또는 keyword | 적절한 workflow/agent를 고르고 task를 시작 | 실제 keyword routing의 전체 corpus는 미열람; hook 연결만 확인 [E05] |
| `.agents/oma-config.yaml` | 언어, telemetry, 모델 routing, quota, SCM 등 프로젝트 정책 | user-owned로 취급되는 파일이며 업데이트 보존 정책이 문서화됨 [E18] |
| workflow state 및 session id | persistent workflow와 event trail을 현재 실행에 묶음 | unknown session id는 다른 세션을 막지 않도록 stop 차단을 피함 [E06] |
| harness suite YAML + candidate overlay | baseline 대 candidate 비교 태스크, 기대 check, 후보 정의 | candidate는 project root 내부·별도 경로여야 하며 symlink/실행제어 변경을 거부 [E07][E08] |

## 처리 단계

### 1. 설치와 런타임 연결

`oma install`은 install lock을 얻고, global install인 경우 `~/.agents/` 및 `~/.claude/`, `~/.codex/` 등 vendor 설정 변경 범위를 interactive prompt로 고지한다. 설치는 shared/hook/agent/workflow/rule/config/선택 skill을 설치한 뒤, vendor adaptation과 symlink를 만든다. `.agents/`가 정의의 원본(SSOT)이고 vendor별 파일은 이를 소비하는 형태다. [E04][E05]

### 2. 요청 수신과 역할 분해

일반 CLI는 install 뒤 agent, hook, state, verify, harness 등 명령 모듈을 동적 등록한다. 오케스트레이션 skill은 요청을 priority tier task로 나누고, skill intent signature로 task별 노출 skill 집합을 좁힌 뒤, 설정에 따라 native 또는 fallback dispatch를 고르도록 정의한다. [E03][E17]

### 3. 실행 중 상태·증거 기록

세션 이벤트는 JSON 한 줄씩 append되며, event 종류에는 phase, gate pass/fail, blocker, decision made/missing, session ended가 있다. event reader는 raw file order가 아니라 `(ts, eventId)`로 상태를 재구성해야 한다. 중요한 결정은 `subject`, 실제 `decision`, 실제 `rationale`을 지녀야 하며, boilerplate 기록은 충분한 증거가 아니라는 계약도 명시되어 있다. [E10][E13]

### 4. 종료 게이트와 산출물 검증

persistent workflow가 끝나려 할 때 Stop hook은 workflow state와 wall-clock budget을 확인한다. completion gate는 agent-writable 문자열을 쉘로 실행하지 않으며 `typecheck`, `test`, `lint` 중 package script가 존재하는 것만 argv 배열로 실행한다. 통과하면 state를 해제하고 `gate.passed`를 기록하며, 실패·timeout은 최대 5회 재강제하되 영구 차단을 피한다. [E06]

`ralph` EXEC 검증은 ultrawork phase 기록, plan JSON, 별도 QA result, 별도 refactor/debug result를 검색한다. 누락하면 structured failed verdict와 remediation을 만들고 active session에 `gate.failed`를 append한다. [E11]

### 5. harness 평가(스킬/정의 변경의 효과 측정)

`oma harness eval`은 candidate가 baseline `.agents` tree와 분리됐는지 먼저 검증한다. live 모드는 task 수의 두 배 dispatch, vendor/model route, temporary checkout, timeout을 보여주고 `--yes` 없이는 사용자 확인을 요구한다. 각 task는 baseline/candidate fresh temporary workspace에서 실행되고, dispatch 중 protected harness definitions가 변하면 실패다. [E07][E08]

candidate가 baseline보다 나아졌는지는 weighted pass score로 계산한다. 최소 5개 paired task가 있어야 coverage가 충분하며, regression 또는 음수 lift는 fail, 5% 이상 lift는 pass, 그 사이는 warn이다. 기록 replay는 suite·baseline·candidate hash가 모두 같아야 하므로 바뀐 입력을 오래된 결과로 재사용하지 않는다. [E07][E09]

## 출력/상태

- 설치 결과: `.agents/` SSOT, vendor adaptation/settings/hook wrapper/symlink, user config patch. 어느 vendor를 선택했는지에 따라 외부 runtime 설정도 바뀔 수 있다. [E04][E05]
- 실행 결과: agent별 `.agents/results/result-{agent}[-{sessionId}].md`, plan JSON, session/task board/progress artifacts라는 계약이 역할·skill에 있다. [E14][E15][E17]
- 감사 결과: `.agents/state/sessions/{sid}/events.jsonl`, index/meta, 그리고 선택 시 memory provider 관찰/기억 경로. 이벤트 append 실패는 stderr에 경로와 doctor hint를 내고 throw한다. [E10][E13]
- harness 결과: JSON/표시 report, arm별 output/check/duration/dispatchError, score 및 기록 파일. [E07][E09]

## 실패·재시도

- install은 concurrent install/update lock을 검사하며, stale lock 설명을 제공한다. global non-interactive CI install은 CI user의 HOME을 변경한다는 경고 경로가 있다. [E04]
- orchestration skill은 verification/QA 실패를 구현 agent로 되돌리고, retry limit 안에서 review history와 함께 재실행하며, clarification debt가 크면 pause/re-specification을 정의한다. 이는 skill 계약이며 실제 모든 vendor executor에서 관찰한 동작은 아니다. [E17]
- stop gate 실패는 event로 남고 재강제 횟수에 포함된다. budget 초과는 완료로 위장하지 않고 partial-stop 성격의 failed gate event를 남긴다. [E06]
- harness는 candidate path, symlink, protected agent execution controls, stale recording, coverage 부족, regression을 각각 오류·fail·insufficient·warn으로 구분한다. [E07][E08][E09]

## 관찰 증거

**완료로 볼 수 있는 증거(확인된 계약):** exit code 0인 allowlisted gate, required artifact verifier의 `ok: true`, 필요한 `decision.made` event가 있는 verifier 결과, agent result/plan files, hash가 일치하는 harness record, 그리고 CI에서는 declared lint/boundary/typecheck/test/build 단계다. [E06][E09][E11][E12][E20]

**이 아카이브에서 미검증인 것:** 이 fixed SHA에서 명령이 실제 실행·성공했는지, 외부 vendor가 실제로 agent를 받았는지, GitHub Action이 PR/commit을 만들었는지, npm package와 marketplace artifact가 source와 일치하는지. 특히 이 SHA는 `test.yml` CI run이 관찰되지 않았다. [E21]
