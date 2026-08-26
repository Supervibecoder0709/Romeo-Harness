# 구성요소 표

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
|---|---|---|---|---|---|---|---|
| `ui-ux-pro-max` | 주 Skill | UI/UX 설계·리뷰에 필요한 검색과 사용 규칙을 에이전트에 제공 | 자연어 요청, 프로젝트 stack 단서 | 검색/설계 시스템 명령과 안전 사용 계약 | 기본은 읽기; `--persist` 시 프로젝트 파일 쓰기 | `.claude/skills/ui-ux-pro-max/SKILL.md` | 확인됨 [E04] |
| `search.py` | Python CLI 진입점 | 도메인/stack 검색 또는 설계 시스템 생성으로 분기 | query, CLI flags | 텍스트 또는 JSON; 선택적 persistence 상태 | 로컬 data 읽기, persist 시 파일 쓰기 | `src/ui-ux-pro-max/scripts/search.py` | 확인됨 [E05] |
| `core.py` | 검색 엔진 | CSV domain/stack을 BM25·정규화·임계값으로 검색 | query, domain/stack, 결과 수 | 결과, 0건, diagnostic | 로컬 파일시스템 읽기 | `src/ui-ux-pro-max/scripts/core.py` | 확인됨 [E06] |
| `reasoning_contract.py` | 안전 계약 | 업종별 JSON decision rule을 허용된 조건/동작으로 제한 | raw JSON, query | activated rule, style/pattern/mode/constraint | 임의 명령을 실행하지 않음 | `src/ui-ux-pro-max/scripts/reasoning_contract.py` | 확인됨 [E12] |
| `design_system.py` | 추천 조합기 | 제품→추론→다중 도메인 결과를 하나의 설계 시스템으로 조립 | query, project, dials | color/style/type/pattern/source identities | data 읽기; persistence 호출로 이어질 수 있음 | `src/ui-ux-pro-max/scripts/design_system.py` | 확인됨 [E13] |
| `validate_data.py` | 데이터 검증기 | schema·참조·공식 출처 host·version/provenance를 fail-closed 검사 | 정본 data | 문제 목록 또는 exit 0/1 | 로컬 파일 읽기 | `src/ui-ux-pro-max/scripts/validate_data.py` | 확인됨 [E14] |
| `uipro` | npm CLI | assistant별 skill 설치/갱신/삭제 명령 라우터 | `init`, `update`, `uninstall`, `versions` | 파일 생성/덮어쓰기/삭제, exit status | CWD/home 쓰기; update 시 npm·GitHub API | `cli/src/index.ts`, `cli/package.json` | 확인됨 [E07] |
| template installer | TypeScript 모듈 | platform JSON으로 skill을 렌더하고 data/scripts/sub-skills 복사 | ai type, target, global, force | 디렉터리·skill 파일 생성/복사 | CWD 또는 home에 재귀 복사/일부 경로 정리 | `cli/src/utils/template.ts` | 확인됨 [E09] |
| uninstaller | TypeScript 모듈 | 설치된 skill과 동봉 sub-skills 제거 | ai type, global, interactive confirm | 대상 경로 재귀 삭제 | CWD/home 삭제; 확인 질문 있음 | `cli/src/commands/uninstall.ts` | 확인됨 [E10] |
| asset sync | build/CI 경계 | 정본에서 CLI/Claude 배포 복제본을 동기화·검사 | `sync:assets`, `check:assets` | hash 일치/불일치 | repository 파일 쓰기(동기화), CI는 검사 | `cli/scripts/sync-assets.mjs`, workflow | 확인됨 [E11] |
| data/relevance test set | 테스트 | data 계약, 검색 품질, 도메인/stack smoke, agent guide 문서를 검증 | 정본 data/scripts | 통과/실패 | 테스트 중 임시 파일 가능; 네트워크 독립 gate 표방 | `cli/package.json`, `scripts/*`, tests | 정의 확인, 실행 미확인 [E14] |
| bundled sub-skills 6종 | Skill | banner/brand/design-system/design/slides/ui-styling 보조 작업 | 각 SKILL의 자연어 argument | 지침, 일부는 asset/token/HTML 파일 작업 | 일부 정의는 외부 브라우저·AI/이미지 도구·파일 쓰기를 전제 | `.claude/skills/*/SKILL.md` | 정의 확인; 이 아카이브에서 실행 안 함 [E17] |
| `stack/design-review` | Claude subagent | 실제 페이지를 7단계로 관찰·등급화 | URL 또는 file path, browser MCP | screenshot/console 기반 finding | MCP 서버·브라우저·URL 접근 | `stack/.claude/agents/design-review.md` | 정의 확인; 실측 미확인 [E18] |
| `design-audit.mjs` | standalone audit | 6 viewports screenshot + DOM heuristic report | `--url` 또는 `--file`, `--out` | `report.md`, `report.json`, PNG, high면 exit 2 | Chromium 실행, target URL/file 읽기, output 쓰기 | `stack/scripts/design-audit.mjs` | 코드 확인; 실행 미확인 [E19] |

## 공개 메타데이터 주의

`plugin.json`/`skill.json`은 설명·버전·스타일/UX 수치를 담지만, 현재 주 skill의 실제 설명과 불일치한다. 자동 설치/선택 UI가 이 메타데이터를 사용한다면 사용자는 구버전 범위로 오해할 수 있으므로, 배포 전 정본·생성 템플릿·metadata를 함께 검증하는 것이 필요하다. [E04][E16]
