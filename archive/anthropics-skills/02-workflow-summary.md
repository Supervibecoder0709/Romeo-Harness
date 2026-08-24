# 02. 워크플로 요약

## 무엇을 하는가

`anthropics/skills`는 한 애플리케이션을 실행하는 저장소가 아니라 Claude가 특정 업무를 반복 가능하게 수행하도록 돕는 **Skill 폴더의 참조·배포 묶음**이다. 각 폴더의 `SKILL.md`가 '언제 이 지침을 읽을지'와 업무 절차를 정하고, 일부는 실행 script·template·reference를 함께 둔다. Claude Code에는 marketplace manifest가 Skill 묶음을 연결한다. [S3], [S4]

## 공통 흐름: 발견 → 지침 적용 → 작업 → 검증

| 단계 | 확인된 동작 | 입력 | 출력/상태 | 실패·재시도 | 관찰 증거 |
| --- | --- | --- | --- | --- | --- |
| 1. Skill 발견 | `SKILL.md`의 `description`이 사용 조건을 설명하고 README는 Claude가 Skill을 동적으로 로드한다고 설명 | 사용자 요청, 설치/사용 가능한 Skill | 어떤 지침을 읽을지의 선택 | 충돌 해결·선택 알고리즘은 미확인 | `SKILL.md` frontmatter, 실제 tool/read 로그(이 레포에는 없음) [S3], [S5]–[S19] |
| 2. 설치 또는 제공 | Claude Code는 marketplace의 plugin별 `skills` 경로를 사용. README는 Claude.ai/API의 사용 경로도 안내 | `/plugin ...` 명령 또는 해당 제품 UI/API | plugin/Skill 사용 가능 상태가 될 수 있음 | 설치 오류 처리·권한 요구·실제 성공은 미확인 | Claude Code의 설치 readback, 실제 available skills 목록 — 이 아카이브에는 미포함 [S3], [S4] |
| 3. 지침 적용 | 선택된 Skill의 Markdown 본문이 작업 순서·형식·주의사항을 제공 | 요청, 로컬 파일/프로젝트, 선택적으로 외부 문서 | 작업 계획·코드·문서·파일 등 업무별 결과 | 일반화된 재시도 정책은 없음; 개별 지침·script마다 다름 | 생성된 파일, 명령 exit code, 로그, 사용자 검토 |
| 4. 산출물 검증 | 일부 Skill은 QA/검증/평가를 명시. 예: PPTX QA, XLSX 재계산, Skill frontmatter 검사·trigger eval, Playwright 기반 로컬 웹 테스트 | 생성물, 기대조건, eval set, server command/port | 검사 결과, JSON 평가, 테스트 반환 코드, 수정 필요 항목 | `with_server.py`는 finally에서 서버 종료; `run_eval.py`는 임시 command file 정리 시도. 그 외 공통 재시도·rollback은 미확인 | validator exit code, eval JSON, screenshot/log, 산출물 열람 [S15], [S19]–[S22], [S28] |

## 대표 경로 A: 문서·파일 산출물

**입력:** `.docx`/`.pdf`/`.pptx`/스프레드시트 파일 또는 새 산출물 요청.  
**처리:** 해당 확장자 Skill이 작업 범위를 정하고, 지침은 Python/CLI/Office 보조 script 및 품질 점검을 사용하도록 안내한다.  
**출력/상태:** 변경·생성된 파일이 로컬 파일 시스템에 생길 수 있다. 문서 Skill 네 가지는 README상 source-available이며, file format별 지침의 실행 환경이 다르다.  
**실패·재시도:** `docx`/`pptx`/`xlsx` 보조 script와 PDF form scripts의 존재는 확인했지만, 모든 파일 형식을 아우르는 rollback 또는 자동 재시도 계약은 확인되지 않았다.  
**관찰 증거:** 파일 존재만으로는 충분하지 않다. 해당 파일을 다시 열고, PPTX는 visual/file QA, XLSX는 수식 재계산 결과, PDF는 form field·rendering을 확인해야 한다. 마지막 문장은 이 레포의 QA 지침을 운영 기준으로 해석한 것이며 실제 자동화 보장은 아니다. [S3], [S12], [S14], [S15], [S19]

## 대표 경로 B: Skill 작성과 품질 측정

**입력:** 새/기존 Skill 디렉터리, `SKILL.md`, trigger eval JSON, 선택적 description override, 로컬 Claude CLI.  
**처리:** `quick_validate.py`가 frontmatter 형식·필수 항목을 검사한다. `run_eval.py`는 프로젝트의 `.claude/commands/`에 임시 명령 파일을 만들고, `claude -p` stream event에서 해당 Skill/Read 호출을 관찰해 trigger rate를 계산한다. `run_loop.py`는 개선 과정에서 선택적으로 eval set을 train/test로 나눈다. [S20]–[S22]

**출력/상태:** validator의 성공/실패 exit code, trigger eval JSON, 그리고 실행 중 생성됐다가 종료 시 삭제하려는 임시 command file이다.  
**실패·재시도:** query 예외는 `False` trigger로 기록하고, child process가 남아 있으면 kill하려고 한다. timeout·모델·병렬 worker 수가 결과에 영향을 줄 수 있으므로, 한 번의 통과만으로 description 품질을 확정하면 안 된다. `run_loop`의 holdout 분할은 그 위험을 줄이려는 코드 구조일 뿐 이 작업에서 효능을 측정하지 않았다. [S21], [S22]  
**관찰 증거:** JSON의 query별 `should_trigger`, `trigger_rate`, runs, pass와 validator exit code를 보관한다. 사람이 실제 요청을 추가로 점검해야 올바른 trigger와 좋은 최종 업무 결과를 혼동하지 않을 수 있다. 이 마지막 판단은 코드가 제공하는 지표의 범위를 바탕으로 한 운영 해석이다. [S20], [S21]

## 대표 경로 C: 로컬 웹 artifact 준비·테스트

**입력:** React artifact의 프로젝트명/코드, Node.js·pnpm 환경, server command와 port, Playwright test command.  
**처리:** `init-artifact.sh`는 Node 버전을 검사하고 필요하면 pnpm을 전역 설치하며 Vite/Tailwind/shadcn 프로젝트를 만든다. `bundle-artifact.sh`는 개발 의존성을 설치하고 이전 `dist`·`bundle.html`을 제거한 후 Parcel build 결과를 단일 HTML로 inline한다. `with_server.py`는 port 준비를 기다린 뒤 test command를 실행하고 서버 프로세스를 정리한다. [S26]–[S28]  
**출력/상태:** 프로젝트 디렉터리, `bundle.html`, 테스트 process의 return code, 서버 시작/종료 로그.  
**실패·재시도:** Node 18 미만, 빠진 package/index file, server port timeout, test 반환 코드가 명시적 실패 경로다. bundle script의 삭제와 package 설치는 상태를 바꾸므로, 실행 전 대상 프로젝트와 의존성 변경을 승인·백업해야 한다. [S26]–[S28]  
**관찰 증거:** build exit code뿐 아니라 `bundle.html`의 존재·브라우저 렌더링, Playwright assertion·스크린샷·console log, 서버 종료 로그를 함께 확인해야 한다. 이 레포에는 이를 한 번에 강제하는 CI는 확인되지 않았다. [S2], [S27], [S28]

## 운영상 한계

- README도 예시·교육 목적이며 실제 Claude의 구현·동작은 다를 수 있고, 중요한 작업 전 자신의 환경에서 충분히 테스트하라고 명시한다. [S3]
- 이 저장소에는 root-level CI/workflow, 패키지 실행 명령, 중앙 secret/권한/감사 로그가 확인되지 않는다. 따라서 이 아카이브는 '설치하면 안전하게 자동 운영된다'고 결론 내리지 않는다. [S2]
- 각 Skill의 `description`은 trigger 힌트이지 접근 권한 승인서가 아니다. 외부 API, 설치, 파일 삭제, 전송 등의 부작용이 있는 script는 사람의 대상 확인과 실행 후 readback이 필요하다. 이는 코드에서 관찰한 부작용을 바탕으로 한 **추천**이다. [S21], [S26], [S27], [S28]
