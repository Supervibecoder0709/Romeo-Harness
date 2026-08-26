# PM / Harness 운영 메모

## 결론

**추천: 이 도구는 처음에는 `project-local install + Codex 한 런타임 + 1개 팀 workflow`로 좁게 도입하고, “산출물과 게이트가 실제로 남는가”를 확인한 뒤 다른 vendor와 multi-agent fan-out을 늘리세요.** 이 구성이 비용·운영 복잡도·권한 범위를 가장 작게 유지하면서, 이 레포의 핵심 가치인 검증 trail을 실제로 평가할 수 있습니다. global install은 HOME과 여러 runtime 설정을 바꾸며, live harness는 agent dispatch 비용을 만들기 때문에 첫 실험의 기본값으로는 과합니다. [E04][E07]

## 확인된 사실

### 입력 계약과 역할 경계

- PM agent는 요구사항, 제약, 배포 대상에서 출발해 API contract와 priority/dependency/scope/test approach가 들어간 task를 만든다. `scope`는 병렬 실행에서 boundary violation을 잡는 용도라고 명시되어 있다. [E14]
- QA agent는 source를 수정하지 않고 file:line 근거와 severity·fix를 내야 하며, PASS/WARNING/FAIL 기준을 가진다. 따라서 구현자 자기평가와 QA 결과를 같은 증거로 취급하면 안 된다. [E15]
- orchestration skill은 native dispatch가 있으면 우선하고, 그렇지 않거나 vendor가 다르면 `oma agent:spawn` fallback을 쓰도록 정의한다. 이 “정의”가 모든 runtime에서 테스트되었는지는 이 아카이브 범위에서 미확인이다. [E17]

### 승인 지점

| 승인/판단 지점 | 왜 필요한가 | 코드·정의상 관찰한 장치 |
|---|---|---|
| global install | HOME과 `.claude/.codex` 등 여러 runtime 설정을 바꿈 | interactive consent와 범위 고지; CI `--yes`는 CI user HOME 변경 경고 [E04] |
| live harness | baseline+candidate arm을 task당 2회 dispatch하여 비용·시간 발생 | preview와 `Proceed? [y/N]`; `--yes`만 생략 [E07] |
| workflow plan | 구현 전에 작업 분해·scope·contract를 고정해야 병렬 충돌을 줄임 | PM plan artifact, required decision `ultrawork.plan-approved`/`impl-plan-locked` [E12][E14] |
| update Action mode | `pr`은 review 기회를 남기지만 `commit`은 base branch에 직접 push 가능 | Action default는 `pr`; `commit` path는 add/commit/push 실행 [E19] |
| force update | 사용자 config overwrite 가능 | Action input `force`; CLI update command의 `--force` [E19] |

### 실행 단위와 관찰 가능한 완료

- 실행 단위는 **task/agent run**, **workflow session**, **harness paired arm**으로 구분하는 것이 적합하다. 각각 result file, `events.jsonl`, arm check/score를 남긴다. [E09][E10][E14]
- 실제 완료 증거는 “agent summary”가 아니라 다음을 함께 읽었을 때 강해진다: required plan/QA/refactor artifacts, `gate.passed`, required decision verifier `ok`, test/lint/typecheck exit, 그리고 harness의 regression 없는 paired score. [E06][E09][E11][E12]
- event JSONL은 append-only이지만 raw file order 자체는 상태 순서가 아니다. consumer/dashboard는 `(ts,eventId)` 정렬이 필요하다. [E13]

### 재시도·복구

- Stop hook은 tests가 계속 실패해도 무한 차단하지 않도록 reinforcement를 5회로 제한하고, wall-clock budget 소진은 partial-stop event로 남긴다. 이는 “실패를 숨기지 않는 종료”를 돕지만, 코드 품질 자동 보증은 아니다. [E06]
- harness record는 suite/baseline/candidate hash가 바뀌면 stale로 거절한다. 재현성은 높이지만 실제 live vendor/model 환경의 변동까지 제거하지는 못한다. [E07]
- orchestration skill은 review history를 넣어 retry하도록 정의하지만, retry가 비즈니스 판단이나 승인된 변경을 대신할 수는 없다. [E17]

## 추천 운영안

1. **설치 전:** project-local root, 설치 대상 vendor, 생성·변경 예상 파일을 명시하고 global 모드는 보류합니다. 기존 `.agents/`가 있으면 backup/commit 상태를 먼저 확인해야 합니다. 이 레포의 설치 코드가 lock은 제공하지만, 사용자 프로젝트의 업무 정책까지 보장하지는 않습니다. [E04]
2. **첫 workflow:** PM plan 1개 → 구현 task 1~2개 → 독립 QA 1개로 시작하고, result files와 event log를 사람이 읽습니다. 중요한 product/API/배포 결정은 decision event에 실제 결정과 근거를 기록하도록 운영 규칙을 정합니다. [E12][E13][E14][E15]
3. **확장 전 gate:** `typecheck/test/lint` 중 프로젝트에 실제로 존재하고 신뢰할 수 있는 명령만 configure합니다. Stop hook allowlist는 임의 shell 실행을 줄이지만, 그 세 명령의 테스트 품질·coverage·production readiness는 별도 판단입니다. [E06]
4. **skill 변경 평가:** live harness는 비용 preview를 보고 승인한 뒤 실행하며, 최소 5 paired task와 regression 0개를 release gate로 삼습니다. score `pass`만으로 보안·UX·운영 적합성까지 완료라고 말하지 않고, task checks가 무엇을 놓치는지 함께 기록합니다. [E07][E09]
5. **업데이트:** GitHub Action은 `mode: pr`을 유지하고, `force: false`를 기본으로 둡니다. branch direct commit은 변경 diff/readback 및 repo branch policy 확인 후에만 사용합니다. [E19]

## 추천이 달라지는 조건

- 한 사람의 단일 runtime 실험이 아니라 이미 여러 vendor가 혼재하고 `.agents/` 정책을 팀 표준으로 유지할 운영자가 있을 때만 global install과 multi-vendor linking의 편익이 비용을 넘을 수 있습니다.
- live harness는 실제 agent model/skill 변경으로 인한 성능 차이를 의사결정해야 하고, fixture 5개 이상과 비용 승인자가 있을 때 유효합니다. 단순 문구 수정이나 기준 없는 fixture에서는 mock/static review가 낫습니다.
- GitHub Action의 direct commit은 protected branch, reviewer, rollback/PR 정책이 명확하게 자동화되어 있을 때만 검토할 수 있습니다. 이 아카이브는 target repository의 branch protection이나 Action 실제 실행 권한을 확인하지 않았습니다.

## 근거 공백

이 archive는 code/configuration을 읽었을 뿐 실제 install, `oma update`, vendor session, hook, live harness, CI, marketplace 배포를 실행하지 않았습니다. 따라서 “설치 가능”, “10개 이상 런타임 지원”, “검증 성공”, “비용/토큰 quota가 실제로 강제됨”과 같은 운영 결과는 이 기록만으로 확정할 수 없습니다. [E21]
