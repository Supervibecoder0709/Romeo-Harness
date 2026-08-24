# 워크플로우 요약

## 1. UI/UX 지식 검색 및 디자인 시스템 생성

### 무엇을 하는가

로컬 CSV/JSON에 들어 있는 UI 스타일, 제품 유형, 색상, 타이포그래피, UX, 아이콘, 모션, 차트, 스택 지침을 검색하고, 새 제품/페이지에는 이를 조합한 설계 시스템 추천을 만든다. 코드 생성기나 배포기가 아니라 **AI 에이전트가 참조할 설계 의사결정 데이터와 CLI**다. [E04][E05]

### 입력

- 필수: 2~5개의 의미 있는 단어로 된 `query`.
- 선택: `--domain`, `--stack`, `--max-results 1..20`, `--json`, `--full`.
- 새 페이지/제품 방향: `--design-system`, 프로젝트 이름, 그리고 1~10의 `--variance`/`--motion`/`--density` 다이얼.
- 파일 저장: `--persist`, 명시적 `--output-dir`, 선택적 `--page`, 기존 Master 덮어쓰기용 `--force`. [E04][E05]

### 처리 단계

1. `search.py`가 인수를 검증한다. `--design-system`이 있으면 일반 검색보다 우선한다. [E05]
2. 도메인 검색은 CSV 스냅샷을 안정적으로 읽고, BM25와 동의어 정규화/도메인 재작성으로 순위를 매긴다. 점수·coverage·margin 임계값을 통과하지 못하면 결과를 비워 `low-confidence` 진단을 남긴다. [E06]
3. 디자인 시스템 생성은 제품 도메인으로 업종을 찾고, 그 업종의 JSON decision rule을 안전한 고정 문법으로 파싱한다. 조건은 style/pattern/mode/constraint의 결정적 데이터 변형만 할 수 있으며 임의 실행을 하지 않는다. [E12]
4. style·color·landing·typography 검색을 결합한다. 다크 요구나 다크 우선 style이면 다크 팔레트를 선택하거나 접근성용 표면 토큰을 파생하고, 추천 결과와 source identity를 함께 출력한다. [E13]

### 출력/상태

- 기본은 사람이 읽는 터미널 텍스트, `--json`이면 구조화된 결과다. 일반 검색 결과에는 일치 건수·소스 파일·도메인이 포함된다. 0건은 빈 값을 가진 성공 결과가 아니라 “데이터베이스 일치 없음”으로 설명한다. [E05]
- `--persist`는 `design-system/<project-slug>/MASTER.md`와 선택적 page override를 쓴다. page 파일은 Master를 대체하지 않고 해당 페이지의 예외만 담도록 설계됐다. [E04]

### 실패·재시도

- 스킬 지침은 빈/부적합 결과 때 더 좁은 질의 또는 명시 도메인/스택으로 **한 번만** 재시도하고, 그래도 없으면 일반 지침임을 표시하라고 한다. [E04]
- 데이터 파일 부재·읽기 오류·비어 있음은 별도 reason으로 빈 결과가 된다. 데이터 검증기는 구조·참조·프로비넌스 오류를 모아 비영(0)이 아닌 종료 상태로 끝낸다. [E06][E14]
- `MASTER.md`가 있으면 기본 persist는 `skipped_exists`이며, `--force` 없이는 쓰지 않는다. 따라서 기존 의사결정을 실수로 바꾸지 않는 경계가 있다. [E04][E05]

### 관찰 증거

- 검색: JSON의 `count`, `results`, `diagnostics.reason`, `diagnostics.abstained`.
- 생성: `source_identities`, `reasoning_default`, `activated_rules`, `source_derivations`.
- 저장: CLI가 출력하는 persistence status와 created files, 그리고 실제 `MASTER.md`/page 파일을 다시 읽어 확인해야 한다. 이 아카이브는 이를 실제 실행하지 않았다. [E05][E13]

## 2. `uipro` 설치·갱신·제거

### 무엇을 하는가

npm CLI가 특정 AI 코딩 도구의 skill 경로에 템플릿 기반 스킬 파일·검색 데이터·스크립트·동봉 sub-skill을 생성, 새로고침 또는 제거한다. 이 흐름은 **사용자 파일 시스템을 변경**한다. [E07][E09]

### 입력

- `uipro init --ai <type>`: 설치 대상 플랫폼. 없으면 현재 디렉터리의 `.claude`, `.agents`, `.codex` 등 폴더로 감지하고 선택 프롬프트를 띄운다.
- `--global`: 현재 프로젝트 대신 사용자의 홈 디렉터리에 설치한다.
- `--force`: 이미 있는 skill 파일을 덮어쓴다.
- `uipro update`: GitHub 최신 릴리스와 현재 CLI 버전을 비교한다.
- `uipro uninstall`: 대상 감지/선택 후 명시적 confirmation 프롬프트를 요구한다. [E07][E08][E10]

### 처리 단계

1. 기본 init은 번들 `assets/templates/platforms/*.json`을 읽어 플랫폼별 skill 파일을 렌더하고, data/scripts 및 sibling sub-skills를 복사한다. 기본 경로는 `cwd`, 전역은 `homedir()`이다. [E08][E09]
2. 이미 핵심 skill 파일이 있고 `--force`가 없으면 스킵한다. 단, sub-skill은 존재할 때 force가 없으면 건너뛴다. [E09]
3. update는 릴리스 API로 최신 태그를 읽어 버전이 다르면 `npm install -g ui-ux-pro-max-cli@<semver>`를 실행한 후 `init --force` 재실행을 안내한다. 같은 버전이면 바로 force init으로 설치 파일을 새로고침한다. [E08]
4. uninstall은 플랫폼 config와 legacy 경로 양쪽에서 주 skill 및 번들 sub-skill을 재귀 삭제한다. [E10]

### 출력/상태

- 성공 메시지의 “Installed folders” 또는 “Removed” 목록은 CLI가 보고하는 증거일 뿐이다. 실제 대상 파일의 생성/삭제와 기존 파일 보존은 사용자가 읽어 확인해야 한다.
- GitHub 릴리스 내려받기 레거시 경로는 rate-limit/다운로드 실패 시 bundled assets 방식으로 fallback한다. 기본 init은 템플릿 방식이다. [E08][E15]

### 실패·재시도

- init 작업 중 예외는 실패 메시지와 exit 1로 끝난다. 레거시 다운로드 실패는 일부 경우 template/bundled install로 fallback한다. [E08]
- uninstall은 취소, 대상 없음, 권한 오류를 구분한다. 삭제는 삭제 후 복원 데이터가 남지 않는 코드 경로이므로, 승인·백업 없이 운영 프로젝트에 실행하면 안 된다. [E10]

### 관찰 증거

- 설치 전후: 정확한 project root 또는 home 경로에서 생성된 skill 파일, data/scripts 복사본, 파일 diff.
- 갱신 전후: `uipro --version`, 릴리스 태그, 파일 hash/자산 동기화 검사.
- 삭제 전후: `Removed` 목록과 대상 경로 부재, 필요하면 VCS/백업에서 복원 가능성. 이 아카이브는 어떠한 설치·삭제도 실행하지 않았다.

## 3. 배포 데이터 동기화·검증과 선택적 browser audit

`src/ui-ux-pro-max/` 변경은 `cli/assets/` 및 Claude skill의 data/scripts 복제본으로 동기화해야 하며, CI가 content hash 기반 동기화를 확인한다. `verify:data`는 CSV 구조, 의미 계약, 안내문 명령, catalog summary, Python 테스트, relevance, smoke, 자산 일치를 묶는다. [E03][E07][E11][E14]

별도 `stack/`은 URL/HTML을 Playwright로 360~1920px에서 촬영하고 overflow·초점·alt·tap target·메타·근사 contrast 등 휴리스틱을 보고한다. 정식 review agent는 실제 브라우저 관찰을 우선하며, 열지 못했으면 heuristic-only라고 표시하도록 정의한다. [E18][E19]
