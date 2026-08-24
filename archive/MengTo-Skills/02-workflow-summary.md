# 워크플로우 요약

## 무엇을 하는가

이 레포는 디자이너·빌더가 Codex, Claude, Cursor 등에서 반복 가능한 제작·검증 작업을 수행하도록, 작고 이식 가능한 SKILL.md playbook을 모은다. 풍부한 UI, 웹/게임, 프런트엔드, 자동화, 재사용 workflow가 대상이지만, 레포 자체가 이 작업을 자동 실행하는 서버는 아니다. [E01]

## 입력

| 입력 | 누가 제공 | 처리 기준 |
| --- | --- | --- |
| 실제 작업 요청과 프로젝트 맥락 | 사용자/작업자 | 가장 구체적으로 맞는 skill 하나부터 선택한다. [E02] |
| 선택한 SKILL.md | 레포 | frontmatter의 trigger와 본문의 절차, guardrail, acceptance check를 읽는다. [E03] |
| 선택 입력 | skill별 | reference, local project, browser, API/credential, release target 등이 될 수 있다. 모든 skill에 공통 schema는 확인되지 않았다. |
| 데모 갱신 대상 | 유지보수자 | git이 추적하는 agent-skills 경로의 SKILL.md와 필요한 경우 Neuform API 환경 변수/.env. [E12] [E16] |

## 처리 단계

### A. 일반 skill 사용

1. 요청의 목적과 제약을 보존한다.
2. 가장 좁게 맞는 SKILL.md를 선택해 먼저 읽는다. [E02]
3. skill이 요구하는 참조·도구·단계를 수행한다.
4. skill에 정의된 산출물과 확인을 남긴다. iterate-until-verified는 task contract → 관찰 가능한 gate → 작업/판정 분리 → 실패 재작업 → 증거 기반 종료의 반복을 정의한다. [E08]

### B. 데모 관리

1. backfill-skill-demos.mjs가 git의 SKILL.md 목록을 읽고 demo 파일을 채운다.
2. source.json이 있는 source-derived demo는 일반 scaffold로 교체하지 않으며 기본 동작은 없는 파일만 쓴다. force 옵션일 때도 source-derived demo는 해당 generic 생성 경로에서 보존된다. [E13]
3. validate-skill-demos.mjs가 각 skill의 demo/index.html, PROMPT.md, preview.jpg와 선택적 provenance를 검사한다. codex category에는 input.md, expected-output.md도 요구한다. [E12]
4. gallery 스크립트가 preview 존재를 확인한 뒤 SCREENSHOTS.md와 SCREENSHOTS.html을 다시 쓴다. [E14]

### C. Neuform source-derived demo 갱신

1. 동기화 스크립트가 NEUFORM_API_URL, NEUFORM_ANON_KEY 또는 지정 .env에서 설정을 읽는다.
2. HTTPS, 허용 host, 차단 IP, sandbox/CSP, asset manifest 규칙을 적용한다.
3. dry-run이 아니면 demo/index.html, PROMPT.md, source.json을 쓴다. Security test는 주요 방어 규칙과 38개 source manifest를 검사한다. [E15] [E16]

## 출력/상태

- 사용자 작업: 선택된 skill이 지시하는 문서, 코드, 분석, preview, publish/deploy 증거 등. 공통 출력 포맷은 없다.
- 데모 작업: skill별 portable demo 파일, DEMOS.md, SCREENSHOTS.md, SCREENSHOTS.html. [E13] [E14]
- validator: 실패 목록과 exit code 1 또는 통계와 passed 출력. 이 아카이브에서는 실제 실행하지 않았으므로 통과 여부는 미확인이다. [E12]
- Neuform sync: source-derived demo 파일과 provenance manifest. 원격 API 응답/권한이 필요하다. [E16]

## 실패·재시도

- 공통 전역 재시도 엔진은 확인되지 않았다. 재시도 방식은 각 skill의 지시문과 호출자가 결정한다.
- iterate-until-verified는 failed/blocked를 증거와 함께 기록하고, 안전하고 범위 내인 조치가 가능할 때만 최소 수정 후 영향을 받는 gate를 다시 검사하라고 요구한다. [E08]
- demo validator는 누락 파일, preview 형식/크기, HTML 기본 구조, prompt 형식, source manifest 등을 failure로 모아 exit 1을 낸다. [E12]
- Neuform은 dry-run 경로가 있고 security test는 로컬/사설 IP, HTTP, 비허용 host, unsafe script/iframe을 거절하도록 설계돼 있다. 실제 원격 갱신의 retry/backoff 정책은 이 분석 범위에서 확정하지 못했다. [E15] [E16]

## 관찰 증거

| 완료 주장 | 최소 관찰 증거 | 이 아카이브의 상태 |
| --- | --- | --- |
| skill을 적용했다 | 선택한 skill SHA/경로, 실제 입력, 산출물, 그 skill의 acceptance check 결과 | 레포 구조만 확인 |
| demo가 유효하다 | node scripts/validate-skill-demos.mjs의 실제 exit 0·통계, browser rendering | 미검증 |
| gallery가 갱신됐다 | 생성된 SCREENSHOTS.md/HTML diff와 preview 존재 | 코드의 write path만 확인 |
| 공개/배포가 완료됐다 | 정확한 target 권한, push/Pages 상태, public URL read-back | publish skill의 요구사항만 확인; 실제 실행 미확인 [E09] |

## 중요한 경계

SKILL.md 지시문은 권한 위임이 아니다. GitHub 공개 repository, push, Pages 설정은 외부 상태를 바꾸며 publish-project-to-github도 명시 권한과 사후 읽기를 요구한다. Harness에서 skill 선택과 실행을 자동화해도 이 승인 gate를 별도로 유지해야 한다. [E09]
