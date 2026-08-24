# 05. PM Harness 운영 메모

## 추천: 전체 설치보다 '업무별 최소 Skill + 실행 전 승인 + 산출물 readback'으로 시작

이 레포는 좋은 참고 라이브러리이지만, 운영 Harness 자체는 아니다. 가장 적합한 도입 방법은 문서·슬라이드·스프레드시트처럼 명확한 업무 하나를 골라 필요한 Skill만 사용하고, 부작용이 있는 script는 실행 전 승인하며, 생성 후에는 실제 파일/로그/검증 결과를 읽어 완료를 판단하는 것이다.

이 추천의 이유는 세 가지다. 첫째, frontmatter `description`은 선택 힌트일 뿐 권한 정책이 아니며, 저장소에는 중앙 권한·secret 관리·감사 로그·CI가 확인되지 않는다. 둘째, 일부 helper는 전역 설치, 네트워크 의존성 설치, 파일 삭제, subprocess 실행을 실제로 수행한다. 셋째, README도 예시·교육 목적이고 실제 Claude 동작이 다를 수 있으므로 환경별 검증을 요구한다. [S2], [S3], [S21], [S26]–[S28]

## 확인된 사실

### 입력 계약

- 최소 Skill 형식은 YAML frontmatter의 `name`, `description`과 Markdown 지침이다. `quick_validate.py`는 이 두 필드를 요구하고 특정 허용 키·형식·길이를 검사한다. [S3], [S20]
- 실제 trigger는 description의 자연어 범위에 크게 의존한다. 예를 들어 `docx`, `pptx`, `xlsx`는 파일 확장자/산출물 종류를 넓게 포착하고, `claude-api`는 Claude/LLM 형태 과제면 작업 파일을 열기 전에 읽도록 지시한다. [S7], [S12], [S15], [S19]
- 더 정교한 trigger 검증은 `run_eval.py`가 query별 `should_trigger`와 반복 실행 결과를 비교하는 방식으로 지원한다. 이 측정은 Claude CLI·모델·프로젝트 파일 쓰기를 수반한다. [S21]

### 모델·에이전트 역할

- 이 고정 트리에는 모델을 선택·고정하는 중앙 orchestrator가 확인되지 않는다. `skill-creator`의 analyzer/comparator/grader는 역할 정의 문서이지 실행자가 아니다. [S2], [S23]–[S25]
- `claude-api`는 특정 모델/가격 등 외부 API 정보의 학습 기억을 신뢰하지 말고 관련 문서를 읽으라고 지시한다. 그러나 그 Skill 안의 'cached' 모델 정보가 현재도 맞는지는 이 아카이브에서 확인하지 않았다. [S7]

### 실행 단위와 증거

- 안전한 최소 실행 단위는 '한 사용자 요청 + 선택된 Skill + 제한된 입력 파일/프로젝트 + 하나의 검증 결과'다. 이 문장은 저장소가 명시한 단위가 아니라, 파일·subprocess·패키지 설치처럼 서로 다른 부작용을 분리하기 위한 **추천**이다.
- 관찰 가능한 증거는 업무별로 달라진다. Skill 형식은 validator exit code·오류 메시지·eval JSON, 웹은 test return code·screenshot·console log·server stop log, 문서는 실제 파일을 다시 열어 확인한 QA 결과가 적절하다. [S20], [S21], [S28]

## 사람이 승인해야 할 지점

| 지점 | 왜 승인해야 하나 | 확인할 것 | 복구/중단 기준 |
| --- | --- | --- | --- |
| plugin marketplace 추가·plugin 설치 | 개발 환경의 available skill과 동작 범위가 바뀔 수 있음 | 정확한 plugin 이름, 설치 대상, 현재 설치 목록 | 설치 전 목록 캡처; 문제가 나면 해당 plugin을 제거하고 readback |
| `init-artifact.sh` 실행 | 필요 시 `npm install -g pnpm`, 프로젝트 생성, 패키지 설치와 설정 파일 쓰기를 수행 | 대상 디렉터리, Node 버전, 전역 설치 허용, 네트워크 사용 | 빈/격리 디렉터리에서 실행; 대상이 틀리면 즉시 중단. 생성 전에는 rollback 자동화가 확인되지 않음 [S26] |
| `bundle-artifact.sh` 실행 | `pnpm add -D`와 `rm -rf dist bundle.html`을 수행 | 프로젝트 root, 기존 `dist`/`bundle.html` 보존 필요 여부, 의존성 lockfile 변화 | Git diff/백업을 먼저 남김; 성공 메시지만 말고 파일 readback·렌더링 확인 [S27] |
| `with_server.py`의 `--server` 전달 | `shell=True`로 문자열 명령을 실행하고 로컬 process를 시작 | 신뢰한 command, port 소유, 테스트 범위 | 의도치 않은 command이면 실행하지 않음; timeout/종료 로그와 남은 process 확인 [S28] |
| `run_eval.py` 실행 | `.claude/commands` 임시 파일을 쓰고 `claude -p`를 반복 실행 | 비용/사용량, 모델, worker 수, 프로젝트 권한, eval set | 전용 test project 사용; 실패/중단 후 command file 잔존 여부 확인 [S21] |
| 외부 API·MCP 연결 | `mcp-builder`는 외부 서비스 통합을 목표로 함 | 최소 권한 토큰, 대상 API, 데이터 송신 범위, rate/cost | test credential·sandbox 우선; 이 레포에 중앙 secret vault/approval layer 없음 [S13], [S2] |

## 재시도·복구 판단

- **확인된 재시도/정리:** `with_server.py`는 `finally`에서 시작한 process를 terminate/kill하고, `run_eval.py`는 끝날 때 임시 command file 삭제를 시도한다. 이는 해당 두 helper의 로컬 정리만 의미한다. [S21], [S28]
- **미확인:** 전역 rollback, dependency lockfile 복구, 파일 삭제 복구, MCP side effect 보상, plugin 제거의 실제 성공 보장, CI 기반 회귀 검증.
- **추천:** 실패했을 때 같은 입력을 무작정 재시도하지 말고, (1) 입력·대상·권한, (2) partial file/process, (3) 검증 로그, (4) 비용·외부 호출 여부를 먼저 기록한 뒤 재시도한다. 특히 `bundle-artifact.sh`와 eval은 상태·비용을 바꿀 수 있다.

## 비용·운영·보안·이전 가능성

| 관점 | 확인된 사실 | 운영 판단 |
| --- | --- | --- |
| 비용 | README는 API 사용을 안내하지만 가격 계약은 이 레포가 관리하지 않는다. `run_eval.py`는 병렬·반복 Claude CLI 실행 옵션을 둔다. [S3], [S21] | **추천:** eval을 소규모 고정 query set으로 시작하고 runs/worker/model을 기록한다. 비용 상한은 외부 제품 설정에서 별도로 둔다. |
| 운영 | root CI/workflow가 확인되지 않고, 모든 Skill에 공통된 실행 harness도 없다. [S2] | **추천:** 조직의 runner에서 skill별 input/output/validator를 등록하고, 원본 Skill SHA와 실행 로그를 함께 보관한다. |
| 보안 | 일부 script는 package install, file write/delete, `shell=True` subprocess를 쓴다. [S21], [S26]–[S28] | **추천:** read-only 분석과 writer runner를 분리한다. writer에는 workspace allowlist, 최소 권한 credential, 외부 전송 전 사람 승인, 실행 후 readback을 둔다. |
| 이전 가능성 | Skill은 Markdown·YAML·상대 파일 구조라 이식하기 쉽지만, `claude -p`, Claude Code plugin, Claude.ai artifact 등 Claude 고유 전제도 있다. [S3], [S4], [S21], [S17] | **추천:** 업무 절차는 provider-neutral Markdown으로 유지하고, Claude 고유 명령·모델·tool 호출은 adapter layer에 격리한다. |

## 추천이 달라지는 조건

- **다른 Claude 제품으로만 실험하고 외부 쓰기가 없다면:** marketplace 설치 뒤 문서형 Skill만 빠르게 평가해도 된다. 그래도 출력 파일 검증은 필요하다.
- **팀 공용 운영·고객 데이터·외부 API를 쓴다면:** 이 레포만으로는 부족하다. approval workflow, secret manager, audit log, 격리 runner, test/production 분리, rollback 절차를 먼저 구현해야 한다.
- **다른 LLM provider에도 같은 작업을 이식해야 한다면:** `SKILL.md`의 본문은 재사용하되 Claude 전용 설치·eval·artifact 지침은 별도 adapter로 분리하는 것이 비용과 이전 위험을 낮춘다.
