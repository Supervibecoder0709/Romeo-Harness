# 탐색 기록

## 범위와 결과

고정 SHA의 blob 662개를 경로 수준에서 인벤토리했다. 실행 중심성·상태 변경 권한·외부 경계·검증 가능성을 기준으로 다음 경로를 열었다.

| 후보군 | 실제로 연 핵심 파일 | 선정 이유 |
|---|---|---|
| 사용자 안내/패키지 | `README.md`, `CLAUDE.md`, `SECURITY.md`, `skill.json`, `.claude-plugin/{plugin,marketplace}.json` | 설치 약속, 정본 위치, 보안 범위, 공개 메타데이터를 확인 |
| 주 스킬 | `.claude/skills/ui-ux-pro-max/SKILL.md`, `references/{quick-reference,pro-rules}.md` | 언제 실행하는지, 검색 계약, 데이터 저장/덮어쓰기 규칙을 확인 |
| 검색·추천 엔진 | `src/ui-ux-pro-max/scripts/{core,search,reasoning_contract,design_system,validate_data}.py`의 동기화본 | 검색/추론/저장 실제 진입점, 입력 제한, 실패 반환, 데이터 검증 확인 |
| CLI 설치기 | `cli/package.json`, `src/index.ts`, `commands/{init,update,uninstall,versions}.ts`, `utils/{detect,extract,github,template}.ts`, `types/index.ts` | 로컬/전역 설치, 덮어쓰기·삭제·네트워크 경계를 확인 |
| 배포 동기화·검증 | `cli/scripts/{build,sync-assets}.mjs`, `scripts/{validate-csv,validate-agent-guide,evaluate-relevance,generate-catalog-summary}.py`, `scripts/{smoke-domains,smoke-stacks}.sh`, Python/Playwright 테스트 | 정본→배포 복제, 계약·회귀 검증의 범위를 확인 |
| CI | `.github/workflows/{tests,check-asset-sync,refresh-catalogs,release,smoke-stacks,bump-versions}.yml` | 자동 검증, 후보 생성, 배포 권한을 분리해 확인 |
| 선택 stack | `stack/{README.md,package.json,.mcp.json}`, `stack/docs/{SETUP,WORKFLOW,STACK}.md`, `stack/.claude/{settings,agents/design-review,commands/*}`, `stack/scripts/design-audit.mjs`, CI | 실브라우저 검토와 외부 MCP 실행 경계를 확인 |

후보가 40개를 넘으므로, 동일 파일의 `src`/`cli/assets`/`.claude` 복제본은 정본 하나와 동기화 검증으로 묶었다. 대형 CSV/JSON은 스키마·행 수·프로비넌스 계약 및 테스트를 통해서만 읽었으며, 각 개별 권고의 사실성은 재검증하지 않았다. [E03][E11][E14]

## 확인된 기술 구성과 실제 진입점

- **정본:** `src/ui-ux-pro-max/`의 CSV/JSON, Python 검색·추천 스크립트, 플랫폼 템플릿이다. `CLAUDE.md`와 자산 동기화 스크립트가 이 위치를 정본이라고 명시한다. [E03]
- **주 실행:** `search.py`가 위치 인수 `query`와 `--domain`/`--stack`/`--design-system`/저장 옵션을 파싱해 `core.search`, `core.search_stack`, `design_system.generate_design_system` 중 하나를 호출한다. [E05]
- **설치 실행:** npm 패키지의 `uipro`가 `cli/src/index.ts`에서 `init`, `versions`, `update`, `uninstall` 명령으로 분기한다. 기본 `init`은 번들 템플릿을 렌더·복사한다. [E07][E08][E09]
- **선택 실행:** `stack/scripts/design-audit.mjs`는 URL 또는 파일을 Playwright Chromium으로 6개 viewport에서 열고, 휴리스틱 결과·스크린샷·JSON/Markdown 보고서를 쓴다. 이는 주 스킬의 필수 실행 경로가 아니다. [E19]

## 확인된 핵심 흐름

1. UI 작업 요청을 받은 AI 에이전트가 스킬 지침을 읽고, 새 페이지/제품 방향에는 `--design-system`, 국소 이슈에는 명시적 도메인, 프레임워크 구현에는 `--stack`을 사용한다. [E04]
2. 검색 엔진은 CSV 도메인별 BM25 인덱스, 질의 정규화·재작성·coverage/score threshold를 사용해 결과 또는 `low-confidence`의 0건을 돌려준다. [E06]
3. 디자인 시스템 생성은 제품 결과→192개 업종 추론 규칙→style/color/landing/typography 다중 검색→모드가 맞는 팔레트 선택→추천/추적 가능한 source identity 출력 순서다. [E12][E13]
4. 사용자가 `--persist`를 붙이면 프로젝트의 `design-system/<slug>/MASTER.md`와 선택적 `pages/<page>.md`에 파일을 쓴다. 기존 Master는 기본적으로 건너뛰고 `--force`여야 덮어쓴다. [E04][E05]
5. `uipro init`은 플랫폼 템플릿, 데이터, 스크립트, 동봉 sub-skill을 프로젝트 또는 `--global`이면 홈 디렉터리에 생성한다. `uninstall`은 확인 프롬프트 후 인식된 skill 경로를 재귀 삭제한다. [E08][E09][E10]

## 미확인 범위

- 현 시점에 어떤 데이터 추천이 실제로 정확하거나 최신인지, 모델이 스킬을 자동 활성화하는지, CI가 최근 녹색인지 미확인이다.
- `README.md` 및 메타데이터의 숫자·옵션 설명 중 일부가 현재 스킬/정본과 다르다. 이는 실행 테스트가 아닌 고정 SHA 정적 비교로 확인된 문서·메타데이터 불일치다. [E04][E16]
- `stack/`의 `design-review` 에이전트는 실제 URL·브라우저·MCP 환경이 있어야 증거 기반 판단이 가능하다. 파일만으로 감사를 완료했다고 볼 수 없다. [E18][E19]
