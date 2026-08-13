---
name: repo-archive
description: GitHub repository URL을 근거 중심으로 탐색해, 핵심 코드·에이전트·스킬·워크플로우·운영 경계를 한국어 문서로 분석하고 `archive/<owner>-<repo>/`에 저장한다. 사용자가 GitHub 레포를 이해, 조사, 한국어 요약, agent/skill 동작 설명, Harness 구축 관점의 구조 분석 또는 레포 아카이브를 요청할 때 사용한다.
---

# Repository Archive

GitHub 레포 하나를 읽고 비개발자 PM도 의사결정에 쓸 수 있는 한국어 아카이브를 만든다. 문서 파일명만으로 결론 내리지 말고, 실제 실행 진입점·설정·테스트·CI를 교차 확인한다.

## 입력과 안전 경계

- 입력은 `https://github.com/<owner>/<repo>` URL 하나와 선택적 `--replace`다. URL의 브랜치/경로가 있으면 그 ref를 사용한다.
- `gh` CLI가 설치되고 해당 레포에 읽기 권한이 있는지 먼저 확인한다. private 레포도 현재 `gh` 인증 범위에서 읽기만 허용한다.
- 분석은 GitHub API 또는 raw 파일 읽기로 수행한다. 기본적으로 clone, issue/PR 작성, 설정 변경, secret 조회, 배포를 하지 않는다.
- 기존 `archive/<owner>-<repo>/`는 보존한다. `--replace`는 교체 의도 표시일 뿐이므로, 대상 경로와 복구 방법을 보여준 뒤 현재 대화에서 재승인받은 경우에만 해당 대상 전체를 교체한다. 실패 시 기존 아카이브는 건드리지 않는다.
- 사실, 추론, 미확인 항목을 분리한다. 코드나 설정을 열지 못한 내용은 추측으로 채우지 않는다.

## 모델과 단계

기본값은 현재 Orca 계정의 **기본 Codex 작업자 한 명**이다. 파일 근거와 해석을 한 컨텍스트에서 유지하므로 보통 가장 정확하고 운영도 단순하다. 이는 논리 역할로서의 `sol`에 해당하지만, Orca가 검증하지 않은 provider model ID를 추정해 넣지는 않는다.

대형 레포에서만 두 단계로 나눈다.

| 단계 | 담당 | 산출물 | 사용 조건 |
| --- | --- | --- | --- |
| 인벤토리 | `luna` 역할 | `_staging/discovery.md` | 후보 파일이 40개 이상이거나 여러 언어/패키지가 섞인 경우 |
| 판별·서술 | `sol` 역할 | 최종 아카이브 | 항상 |
| 번역 보조 | `terra` 또는 `luna` 역할 | 확정 문서의 번역 초안 | 번역 문서가 많을 때만 |

모델 분리는 독립 작업자 간 파일을 자동 공유하지 않는다. 따라서 단계형 실행에서는 이전 단계의 `_staging/` 산출물을 다음 작업자가 읽을 수 있는 동일 워크트리에 두거나, 오케스트레이터가 파일을 전달해야 한다. 세 모델을 동시에 실행해 같은 아카이브 경로에 쓰게 하지 않는다.

## 절차

### 1. 소스 고정

1. URL에서 owner, repo, ref를 파싱한다.
2. ref가 없으면 `gh api repos/<owner>/<repo>`에서 `default_branch`를 얻는다.
3. `gh api repos/<owner>/<repo>/commits/<ref> --jq .sha`로 분석 커밋 SHA를 고정한다.
4. `_source.md`에 URL, ref, SHA, 분석 시각, 접근 실패 항목을 기록할 준비를 한다.

브랜치 이름만 기록하면 이후 내용이 바뀌어 재현할 수 없다. SHA는 이 아카이브가 어떤 시점의 레포를 설명하는지 보장하는 기준점이다.

### 2. 파일 인벤토리와 후보 선정

`gh api repos/<owner>/<repo>/git/trees/<sha>?recursive=1`으로 경로 목록만 얻는다. 전체 clone이나 전체 파일 다운로드를 하지 않는다.

다음 순서로 후보를 고르고, 각 항목의 선정 이유를 `00-exploration.md`에 남긴다.

1. 안내와 에이전트 정의: `README*`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING*`, `SKILL.md`, `.claude/agents/**`, `.claude/skills/**`, `.agents/skills/**`.
2. 실행 계약: package manager manifest, lockfile, `Makefile`, `justfile`, `docker-compose*`, `Dockerfile`, `*.yaml` CI/workflow, `*.toml`/`*.json` 설정, `.env.example`.
3. 실제 진입점: manifest scripts가 가리키는 파일, `src/main.*`, `src/index.*`, `app.*`, `cmd/**/main.*`, 서버/CLI/worker 엔트리.
4. 핵심 흐름을 증명하는 코드: API/CLI handler, orchestration/agent runner, 저장소 adapter, 권한·네트워크·queue 경계, 주요 테스트 fixture와 integration test.
5. 제한된 `docs/` 문서: 사용법·아키텍처·운영 설명만. 생성물, 전체 API reference, lockfile, vendor/build output은 제외한다.

후보가 많으면 문서만 남기지 말고 실행 경로별로 최소 한 개의 진입점과 한 개의 검증 또는 설정 근거를 남긴다. 40개를 넘으면 중복 문서를 합치고 제외한 경로와 이유를 기록한다.

### 3. 내용 확보와 교차 검증

후보만 `gh api repos/<owner>/<repo>/contents/<path>?ref=<sha>` 또는 raw URL로 읽는다. 큰 파일은 필요한 함수/섹션만 읽고 이 제한을 기록한다.

다음 질문을 코드 근거로 답한다.

- 사용자는 무엇을 입력하고, 시스템은 어떤 출력 또는 상태 변경을 만드는가?
- 실제 시작점은 무엇이며 어느 모듈을 거쳐 핵심 작업이 실행되는가?
- agent와 skill은 각각 어떤 입력 계약, 권한, 도구, 산출물을 가지는가?
- 데이터·인증정보·외부 API·파일 시스템은 어디에서 드나드는가? 실패와 재시도는 어떻게 처리되는가?
- 테스트와 CI는 무엇을 보장하고, 무엇은 검증하지 않는가?
- Harness PM 관점에서 사람이 승인해야 하는 지점, 재실행 가능한 지점, 관찰 가능한 완료 증거는 무엇인가?

README의 주장과 코드가 다르면 코드를 현재 동작 근거로 우선하고 문서 불일치를 명시한다.

### 4. 중요도 판별과 한국어 문서 작성

중요도는 파일의 이름이나 줄 수가 아니라 다음으로 판단한다: 실행 경로의 중심성, 실패 시 영향, 외부 경계, 상태를 바꾸는 권한, 다른 구성요소의 의존도, PM의 의사결정 필요성.

아래 파일을 작성한다.

```text
archive/<owner>-<repo>/
  _source.md
  00-exploration.md
  01-docs/
  02-workflow-summary.md
  03-components/
  04-components-table.md
  05-pm-harness-notes.md
  06-source-evidence.md
```

- `_source.md`: `Origin URL`, `Ref`, `Commit SHA`, `Analysis timestamp`를 각각 한 줄로 기록하고, 접근 한계와 제외 후보·사유를 덧붙인다.
- `00-exploration.md`: 탐색 범위, 실제로 연 파일, 진입점, 기술 스택, 확인된 핵심 흐름, 미확인 범위.
- `01-docs/`: 확정한 사용·운영 문서의 한국어 번역. 원 파일명에 `.ko.md`를 붙인다.
- `02-workflow-summary.md`: `무엇을 하는가 → 입력 → 처리 단계 → 출력/상태 → 실패·재시도 → 관찰 증거` 순으로 쓴다. 코드 세부보다 동작 기전을 설명한다.
- `03-components/`: agent/skill 정의의 한국어 번역과, 정의 파일이 없지만 실행 핵심인 구성요소의 짧은 설명.
- `04-components-table.md`: 구성요소, 종류, 역할, 입력, 출력/상태변화, 권한·외부경계, 원문 위치, 근거 상태를 표로 정리한다.
- `05-pm-harness-notes.md`: Harness를 구축·운영하는 PM에게 중요한 입력 계약, 모델/에이전트 역할, 승인 지점, 실행 단위, 증거·로그, 재시도·복구, 확장 지점을 정리한다. 확인되지 않은 개선 제안은 `추천`으로 분리한다.
- `06-source-evidence.md`: 원문 URL, 고정 SHA, 파일·줄 범위, 해당 근거가 뒷받침하는 사실을 표로 기록한다. 분석 문서의 근거 ID는 이 파일에서 해석 가능해야 한다.

### 5. 번역 규칙

번역은 요약이 아니다. 제목, 목록, 표, 코드블록, 링크, 파일 경로, CLI 명령, 식별자, 라이브러리·제품 이름은 유지하고 사람 언어만 정확하게 한국어로 옮긴다. 링크 텍스트는 번역해도 URL은 바꾸지 않는다. 번역과 분석 문서를 섞지 않는다.

### 6. 완료 기준과 보고

다음을 확인한 경우에만 완료라고 말한다.

- `_source.md`에 고정 SHA가 있다.
- 각 핵심 워크플로우에 적어도 하나의 코드·설정·테스트 경로 근거가 있다.
- agent/skill 표에 원문 위치가 있다.
- 사실·추론·미확인이 구분되어 있다.
- 최종 디렉터리가 대상 위치에 존재한다.

최종 보고에는 아카이브 경로, 분석 SHA, 번역 문서 수, 핵심 구성요소 수, 제외/미확인 항목을 짧게 포함한다.
