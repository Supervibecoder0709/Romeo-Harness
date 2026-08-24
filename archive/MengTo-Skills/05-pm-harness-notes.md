# PM Harness 운영 노트

## 추천

이 레포는 전사 공용 자동 실행 도구로 한꺼번에 연결하기보다, 고정 SHA의 읽기 전용 playbook 라이브러리로 등록하고 작은 승인형 pilot부터 운영하는 것이 가장 적합하다. skill은 Markdown 절차로 구성돼 있고 공통 manifest, 권한 엔진, CI 실행 경로는 확인되지 않은 반면 일부 skill은 GitHub 공개/배포나 외부 API·파일 쓰기까지 안내하기 때문이다. [E01] [E03] [E09] [E16] [E17]

이 선택은 비용이 거의 없고, 원문 SHA와 실행 증거를 남기면 다른 도구로 옮기기도 쉽다. 반대로 skill을 자동 발견해 모두 실행하거나 문서의 명령을 곧바로 권한으로 해석하면 공개·배포·원격 API·로컬 파일 쓰기의 운영/보안 경계가 무너질 수 있다.

## 확인된 사실

- 라이브러리의 실제 단위는 SKILL.md이고 optional references, articles, scripts, assets, demos가 붙는다. [E03]
- Codex와 다른 에이전트 모두 가장 좁게 맞는 skill부터 읽으라는 사용 계약이 있다. [E02]
- iterate-until-verified는 task contract를 보존하고 실행자와 판정자를 분리하며 evidence 기반으로 종료하라고 명시한다. [E08]
- publish-project-to-github은 public repository, visibility, Pages 설정을 독립된 권한 gate로 다루며 성공한 push만으로 live를 주장하지 말라고 한다. [E09]
- top-level validator는 파일/정적 계약을 검사하지만 browser rendering이나 production website 동작은 수행하지 않는다. [E12]

## 현재 가정

- Harness가 skill frontmatter를 읽어 UI에 노출할 수는 있지만, 이 SHA에서 Codex/Claude/Cursor의 자동 discovery 설정은 확인하지 않았다.
- 현재 작업자는 raw 소스만 읽었으므로 node script의 실제 성공·실패, package/tool 설치, browser interaction은 이 아카이브의 증거가 아니다.

## 권장 운영 흐름

작업 요청 → 사람/라우터의 가장 좁은 skill 선택과 SHA 기록 → 입력 계약/허용 도구/외부 쓰기 추출 → read-only 또는 local-only 실행 → 별도 verifier의 원 요청 대조 → 외부 변경이면 target/권한 재확인 → read-back/URL/log/산출물로 완료 판정

### 입력 계약

| 필드 | 필요한 이유 |
| --- | --- |
| 원 요청과 완료 기준 | iterate skill의 task contract 보존 [E08] |
| 선택 skill 경로와 source SHA | 같은 이름의 skill이 바뀌어도 재현 가능한 실행 단위 유지 |
| 실제 입력(프로젝트 경로, reference, target URL) | 대상이 달라지면 위험과 결과가 달라짐 |
| 허용 도구와 외부 쓰기 범위 | Markdown 지시문이 자동 권한 위임이 되는 것을 방지 |
| 검증 gate와 증거 위치 | 실행했다가 아닌 관찰 가능한 완료를 만들기 위함 [E08] |

### 모델·에이전트 역할

- 라우터/PM: category명이 아니라 task의 실제 표면을 보고 하나의 좁은 skill을 먼저 선택한다.
- 실행자: skill 절차를 따르되 원 요청의 범위를 넓히지 않는다.
- 검증자: 원 요청, acceptance matrix, 결과물, reference만 보고 실패를 먼저 찾는다. 실행자의 자신감은 증거가 아니다. [E08]
- 승인자: 공개, push, Pages, 외부 API credential, 삭제/overwrite가 걸리면 exact target과 복구 방법을 검토한다.

## 승인 지점

| 상황 | 권장 gate | 근거 |
| --- | --- | --- |
| reference 조사/문서 번역/정적 분석 | read-only로 진행 | 일반 skill library 사용 범위 |
| local demo scaffold/galleries 재생성 | 대상 경로, force 여부, 기존 source-derived demo 보존 확인 | backfill은 local 파일과 DEMOS.md를 쓴다. [E13] |
| Neuform demo sync | API URL/key, 허용 host, dry-run, 변경될 skill 목록 승인 | credential과 외부 API/asset, demo write 필요. [E15] [E16] |
| GitHub repo 공개/Push/Pages | owner/repo, visibility, branch, Pages config, rollback commit 명시 승인 | skill이 명시 권한·사후 read-back 요구. [E09] |
| web game deploy | exact commit, deployment target, rollback target, production smoke test 승인 | release와 production proof 분리. [E10] |

## 증거·로그 설계

Harness source of truth에는 skill_path, skill_sha, agent_runtime, input_snapshot_hash, 시작/종료 시각, command와 exit code, 변경 파일 hash, validator/테스트 출력, browser screenshot/영상, public URL과 post-action read-back, PASS/FAIL/BLOCKED와 이유, 재실행 step, rollback target을 남기는 것을 추천한다.

validator가 제공하는 것은 static contract proof다. UI, 외부 API, 배포는 별도 검증 surface가 필요하다. [E12] [E09]

## 재시도·복구

- 문서/분석은 같은 SHA, 같은 input snapshot, 같은 skill path로 재실행한다.
- local demo generation은 기본값이 존재하는 파일을 보존하지만 force는 영향을 넓힌다. source-derived demo는 별도 보호 경로가 있다. [E13]
- production 변경은 release 전 exact commit과 rollback target을 기록하고 실패 시 그 target으로 복구한다. [E10]
- Neuform source는 외부 순위/응답에 따라 달라질 수 있다. manifest timestamp와 original/sandbox hash로 고정 source와 실제 결과를 구분한다. [E15] [E16]

## 확장 지점

1. Skill registry: tree에서 skill path, frontmatter name/description, 외부 쓰기 플래그를 추출해 approval policy를 붙인다. 미열람 126개에는 자동 권한을 추정하지 않고 review queue로 둔다.
2. Evidence adapter: validator, browser test, deployment read-back을 하나의 run record에 연결한다.
3. Doc-drift gate: tree count와 README/DEMOS index count를 비교해 오래된 목록을 release 전에 차단한다. 이 snapshot에서 이미 불일치가 관찰됐다. [E04] [E12] [E17]

## 추천과 확인 사항의 구분

- 추천: 위 approval/evidence registry는 이 레포에 구현돼 있지 않다. Harness 운영에서 추가할 통제 장치다.
- 확인됨: 고정 SHA에 quality loop, explicit publication guard, static demo validator/security test가 존재한다. [E08] [E09] [E12] [E15]
- 미확인: 전체 skill의 권한 분류, CI, 모든 demo validation pass, 현재 외부 service/API 상태.
