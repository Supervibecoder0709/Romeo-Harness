# 00. 탐색 기록

## 결론

이 저장소의 중심은 실행 서버가 아니라 **에이전트에게 작업 방법을 주입하는 선언형·파일 기반 Skill 묶음**이다. 사용자는 Claude Code plugin marketplace로 묶음을 설치하거나, Claude.ai/API에서 skill을 사용·업로드한다. 실제 업무 처리의 품질과 산출물 검증은 각 `SKILL.md`가 가리키는 로컬 스크립트·템플릿·참조문서에 달려 있으며, 저장소 전체를 실행하는 단일 명령은 확인되지 않았다. [S3], [S4], [S5]

## 탐색 범위와 인벤토리

고정 SHA의 재귀 트리에서 blob 경로를 조회했다. 후보는 README와 marketplace 설정, `template/SKILL.md`, Agent Skills spec 포인터, `skills/*/SKILL.md`, 그리고 SKILL 지침이 실제로 지목하는 스크립트·agent 정의로 골랐다. 19개의 최상위 Skill 정의가 확인되어, 이름만 나열하지 않고 모든 트리거 설명을 [03-components/skill-definitions.ko.md](03-components/skill-definitions.ko.md)에 한국어로 옮겼다. [S2], [S5]–[S11]

### 실제로 연 핵심 파일

| 범주 | 연 파일 | 선정 이유 |
| --- | --- | --- |
| 사용·배포 계약 | `README.md`, `.claude-plugin/marketplace.json` | Skill의 정의, 설치 방법, marketplace의 플러그인→skill 매핑을 함께 확인 |
| 형식 기준 | `template/SKILL.md`, `spec/agent-skills-spec.md` | 최소 frontmatter 형식과 외부 명세의 위치 확인 |
| 모든 구성요소 정의 | 19개 `skills/*/SKILL.md` | 트리거, 업무 범위, 산출물·검증 지침의 1차 근거 |
| Skill 품질·평가 | `skills/skill-creator/scripts/quick_validate.py`, `run_eval.py`, `run_loop.py`, `agents/{analyzer,comparator,grader}.md` | frontmatter 검사와 trigger 평가, 독립 평가 역할을 실제 코드·정의로 확인 |
| 파일 산출물 | `docx`/`pptx`/`xlsx`의 검증·재계산 스크립트, PDF 폼 스크립트 | 생성만이 아니라 검증·형식 처리 경계가 존재하는지 확인 |
| 통합·테스트 | `web-artifacts-builder`의 초기화/번들 스크립트, `webapp-testing/scripts/with_server.py` | 개발 산출물의 준비·번들·서버 대기·정리 흐름 확인 |
| 기타 실행 보조 | MCP 평가·연결, Slack GIF builder/validator, p5.js template | 외부 연결·파일 기록·재현성의 실제 구현 확인 |

## 기술 스택과 경계

- **포장/발견:** Markdown `SKILL.md` + YAML frontmatter, Claude Code marketplace JSON. [S3]–[S6]
- **실행 보조:** Python, Bash, JavaScript/p5.js; 일부 skill은 `pnpm`, Node.js, Playwright, Office·PDF 도구를 지침으로 요구한다. 이는 각 Skill의 실행 환경이며 루트 공통 의존성 선언은 아니다. [S8], [S12]–[S17]
- **외부 경계:** Claude Code/Claude.ai/Claude API, `claude -p` subprocess, npm/pnpm 레지스트리·Node.js, 로컬 파일 시스템, localhost 서버 포트, MCP가 연결하는 외부 서비스. 이러한 경계의 권한·자격증명·가격은 이 저장소에서 중앙 관리되는 것으로 확인되지 않았다. [S3], [S9], [S16], [S17]

## 확인된 핵심 흐름

1. 작성자 또는 Anthropic이 Skill 폴더에 `SKILL.md`와 선택적 scripts/resources를 둔다.
2. Claude가 사용자 요청과 frontmatter `description`을 바탕으로 맞는 Skill을 동적으로 읽고, 해당 지침에 따라 파일·코드·도구를 다룬다.
3. Claude Code에서는 marketplace의 plugin 정의가 어느 skill 폴더를 설치하는지 결정한다. `document-skills`, `example-skills`, `claude-api`, `academy-guide`, `discernment-nudge` 다섯 묶음이 확인된다.
4. 일부 Skill은 산출물 후 검증을 지시하거나 검사 스크립트를 제공한다. 예: `skill-creator`의 frontmatter validator와 trigger evaluator, web test server lifecycle helper, 문서 도구의 검증·재계산 보조다. 다만 **이 저장소 전체의 공통 자동 검증은 미확인**이다. [S4], [S8]–[S17]

## 미확인 범위

- Skill 선택 알고리즘, 우선순위 충돌 해소, 실제 런타임 권한 모델, 설치 이후 파일 배치, 원격 분석/telemetry는 이 Git 트리에서 확인하지 못했다.
- `spec/agent-skills-spec.md`는 외부 URL 하나만 가리킨다. 외부 명세 내용은 이 아카이브의 사실 근거에 포함하지 않았다. [S6]
- 고정 트리 기준 CI/workflow와 repository-level 자동 테스트가 확인되지 않아, 각 script의 테스트 커버리지와 현재 성공률은 미검증이다. [S2]
