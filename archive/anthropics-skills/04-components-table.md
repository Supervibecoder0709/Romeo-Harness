# 04. 구성요소 표

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| README 사용 계약 | 안내 문서 | Skill 폴더·동적 로드, 사용 표면, 설치 방식을 설명 | 사용자 요청, Skill 폴더 | Claude가 따를 지침·선택적 산출물 | Claude Code/Claude.ai/API 안내; 실제 설치·권한은 이 레포에서 미검증 | `README.md:1-94` [S3] | 문서 설명 확인 |
| `anthropic-agent-skills` marketplace | plugin manifest | 5개 플러그인과 포함 Skill 경로를 선언 | Claude Code plugin 설치 | 설치 후보 Skill 묶음 | Claude Code marketplace; `strict: false`의 실제 의미는 미확인 | `.claude-plugin/marketplace.json:1-65` [S4] | 설정 확인 |
| `template-skill` | 형식 템플릿 | 이름·설명 frontmatter와 본문 지침의 최소 뼈대 제공 | 작성자의 Skill 내용 | `SKILL.md` 초안 | 파일 시스템에 새 Skill 작성 시 변경 발생 가능 | `template/SKILL.md:1-5` [S5] | 확인됨 |
| `academy-guide` | Skill | Claude Academy의 강하게 일치하는 학습 자료를 추천 | Claude 사용법·온보딩 요청 | 답변에 학습 추천 추가 가능 | `academy.claude.com`; 실시간 카탈로그·추천 결과 미검증 | `skills/academy-guide/SKILL.md:1-18` [S5] | 정의 확인 |
| `algorithmic-art` | Skill + p5.js template | seed 기반 생성 예술과 대화형 파라미터 탐색 안내 | 예술 요청·파라미터 | `.md`, `.html`, `.js` 산출물 지침 | 로컬 파일 쓰기·p5.js; 결과 저작권·렌더링은 개별 검증 필요 | `skills/algorithmic-art/SKILL.md:1-12,101-221`; `templates/generator_template.js:18-47,162-205` [S8], [S29] | 정의·템플릿 확인 |
| `brand-guidelines` | Skill | Anthropic 색·타이포그래피를 artifact에 적용 | 브랜드/시각 서식 요청 | 스타일 적용 지침 | Anthropic 브랜드 자산; 실제 최신 brand kit는 미확인 | `skills/brand-guidelines/SKILL.md:1-4,15-69` [S8] | 정의 확인 |
| `canvas-design` | Skill | 디자인 철학을 `.png`/`.pdf` 정적 디자인으로 표현 | 포스터·정적 예술 요청 | `.md`, `.pdf`, `.png` 지침 | 로컬 파일 생성; 원본성 지침은 있으나 생성 결과 미검증 | `skills/canvas-design/SKILL.md:1-12,100-128` [S8] | 정의 확인 |
| `claude-api` | Skill + 대형 참조 묶음 | Claude API/SDK 판단 전 최신 문서를 라우팅 | Claude/LLM 관련 요청 | 언어별·공유 참조 선택 | API/SDK·모델/가격은 시점 의존; 이 아카이브에서 현재성 미검증 | `skills/claude-api/SKILL.md:1-7,10-37,52-108,466-530` [S7] | 정의·목차 확인 |
| `discernment-nudge` | Skill | 실질적 답변 후 검증을 돕는 후속 질문 2~3개를 붙이도록 경계 설정 | 실행 가능한 조언·초안 | 후속 점검 질문 또는 skip | 사용자 대화; 자동 적용·대화당 횟수 집행은 미검증 | `skills/discernment-nudge/SKILL.md:1-19,44-72,165-189` [S9] | 정의 확인 |
| `doc-coauthoring` | Skill | 맥락 수집→구조화·개선→독자 테스트로 문서 공동 작성 안내 | 문서·제안서·명세 요청 | 문서 초안과 reader testing 흐름 | 사용자 제공 맥락, 선택적 sub-agent; 실제 agent 실행 미확인 | `skills/doc-coauthoring/SKILL.md:1-8,28-350` [S10] | 정의 확인 |
| `docx` | Skill + Office helpers | Word 생성·편집·분석 및 변경 추적/댓글 지침 | `.docx`/`.dotx` | 변경된 Word 문서 가능 | 로컬 파일·Office/Python 도구; 출력 검증 실행 미수행 | `skills/docx/SKILL.md:1-5,7-89`; `scripts/**` [S12], [S2] | 정의·자산 존재 확인 |
| `frontend-design` | Skill | 개성 있는 UI 미학·타이포그래피·레이아웃 판단 | 새/기존 UI 과제 | 디자인 방향·구현 지침 | 파일·프론트엔드 프로젝트; 결과 사용성·접근성 테스트 미확인 | `skills/frontend-design/SKILL.md:1-4,7-45` [S8] | 정의 확인 |
| `internal-comms` | Skill + 예시 | 사내 업데이트·뉴스레터·FAQ 등의 형식 안내 | 사내 커뮤니케이션 요청 | 커뮤니케이션 초안 | 조직 고유 정책/사실; 이 저장소는 검증된 전송 수단을 제공하지 않음 | `skills/internal-comms/SKILL.md:1-31`; `examples/*.md` [S8], [S2] | 정의·예시 존재 확인 |
| `mcp-builder` | Skill + scripts/reference | 조사·계획, 구현, 검토·테스트, evaluation으로 MCP 서버를 설계 | 외부 서비스/API와 연결할 MCP 요구 | MCP 서버·평가 설계 | 외부 API 자격증명·권한·네트워크; 중앙 승인/secret 관리 미확인 | `skills/mcp-builder/SKILL.md:1-4,15-230`; `scripts/**` [S13], [S2] | 정의·자산 존재 확인 |
| `pdf` | Skill + PDF scripts | PDF 읽기·추출·생성·폼·OCR 지침 | PDF 요청·`.pdf` | PDF 또는 추출 데이터 | 파일 시스템, OCR/CLI/Python 도구; 정확도·보안 암호 처리 실행 미검증 | `skills/pdf/SKILL.md:1-11,13-309`; `scripts/**` [S14], [S2] | 정의·자산 존재 확인 |
| `pptx` | Skill + Office helpers | PowerPoint 생성·편집·분석과 필수 QA 지침 | `.pptx`/`.potx`, deck 요청 | 수정/생성된 deck 가능 | 로컬 파일·Office 도구; visual QA 실제 통과 미검증 | `skills/pptx/SKILL.md:1-5,17-236`; `scripts/**` [S15], [S2] | 정의·자산 존재 확인 |
| `skill-creator` | Skill + evaluator + 역할 정의 | Skill 작성·개선·성능/trigger 평가 | Skill 경로, eval set, description | validation 결과·JSON 평가·개선 후보 | `claude -p`, `.claude/commands`, subprocess, 파일 생성·삭제 | `skills/skill-creator/SKILL.md:1-4,45-459`; `scripts/quick_validate.py:12-103`; `scripts/run_eval.py:35-280`; `agents/*.md` [S11], [S20]–[S25] | 코드·정의 확인, 실행 미검증 |
| `slack-gif-creator` | Skill + Python core | Slack용 GIF 생성·검사·최적화 | 프레임/이미지, 출력 경로, 옵션 | GIF 파일 및 크기·frame 정보 | 로컬 파일 쓰기; Slack 업로드/API 호출은 확인되지 않음 | `skills/slack-gif-creator/SKILL.md:1-4,11-250`; `core/gif_builder.py:160-265` [S16], [S30] | 코드·정의 확인 |
| `theme-factory` | Skill + theme assets | 10개 preset 또는 새 theme으로 artifact 스타일링 | 대상 artifact·theme 선택 | 색·글꼴 적용 지침 | 문서/슬라이드/HTML; 실제 asset 적용은 실행별 검증 필요 | `skills/theme-factory/SKILL.md:1-4,8-58`; `themes/*.md` [S8], [S2] | 정의·자산 존재 확인 |
| `web-artifacts-builder` | Skill + Bash scripts | React/Tailwind/shadcn artifact 초기화·번들 | 프로젝트명, 프론트엔드 코드 | React 프로젝트·`bundle.html` | Node/pnpm/npm, 패키지 레지스트리, 로컬 파일 삭제·설치 | `skills/web-artifacts-builder/SKILL.md:1-4,7-72`; `scripts/init-artifact.sh:1-279`; `bundle-artifact.sh:1-54` [S17], [S26], [S27] | 코드·정의 확인, 실행 미검증 |
| `webapp-testing` | Skill + Playwright helper | 로컬 웹앱 탐색·자동화·스크린샷·로그 확인 | server 명령, port, 테스트 명령 | 테스트 exit code; 서버 종료 | localhost socket, `shell=True` subprocess, 로컬 프로세스 | `skills/webapp-testing/SKILL.md:1-4,7-91`; `scripts/with_server.py:1-106` [S18], [S28] | 코드·정의 확인, 실행 미검증 |
| `xlsx` | Skill + Office helpers | 스프레드시트 생성·편집·검증·수식 재계산 지침 | `.xlsx`/`.xlsm`/`.xltx`/`.csv`/`.tsv` | 스프레드시트 파일 | 로컬 파일·Python/Office; formula 계산 결과 검증 미수행 | `skills/xlsx/SKILL.md:1-5,7-97`; `scripts/recalc.py`, `office/**` [S19], [S2] | 정의·자산 존재 확인 |

`원문 위치`은 모두 고정 SHA에서 읽은 파일·줄 범위다. 자세한 URL은 [06-source-evidence.md](06-source-evidence.md)에 있다.
