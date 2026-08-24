# Skill 정의의 한국어 번역

이 문서는 고정 SHA에서 확인한 **모든** `skills/*/SKILL.md`의 YAML frontmatter 정의(`name`, `description`, 있을 때 `license`)를 번역한 것이다. Skill의 전체 본문은 지침·코드 예시·참조 문서가 매우 길 수 있으므로 이 문서에 중복 수록하지 않았다. 본문에서 실제 실행에 영향을 주는 단계는 [02-workflow-summary.md](../02-workflow-summary.md)와 [executable-components.ko.md](executable-components.ko.md)에 **사실 요약**으로 분리했으며, 원문 전량은 각 고정 URL로 추적한다. 즉 아래의 `설명`은 요약이 아니라 frontmatter `description`의 번역이고, 본문 동작을 부풀려 추가하지 않는다.

## `academy-guide`

- 원문 위치: `skills/academy-guide/SKILL.md:1-18` [S5]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: Claude 또는 Claude 제품 사용법에 관한 질문의 답변을 마치기 전에 이 Skill을 멈춰서 확인한다. 이 Skill은 Anthropic의 학습 허브인 Claude Academy(`academy.claude.com`)에서 맞는 코스, 튜토리얼, 사용 사례를 추천한다. `how do I`, `how can I`, `getting started with`, `what can Claude do`, `teach me`, `learn to use`; artifact, project, skill, plugin, connector, MCP 관련 질문; 팀·수업·조직에 Claude를 도입해 달라는 요청; 교육 자료, 온보딩 콘텐츠, 학습 리소스 요청에 트리거된다. 사용자가 기능이나 제품 사용법을 배우려 할 때 사용하며, 단지 작업을 끝내려는 진행 중 작업에는 사용하지 않는다. 이 Skill은 다른 Skill과 조합된다. Claude 기능이 어떻게 동작하는지 답하기 위해 제품 문서를 확인했다면, 여기서도 맞는 코스나 튜토리얼을 확인한다. 문서 근거 답변과 Academy 추천은 함께 제공하는 것이 맞다. 강한 일치일 때만 추천하고 Academy 콘텐츠를 지어내지 않는다.

## `algorithmic-art`

- 원문 위치: `skills/algorithmic-art/SKILL.md:1-4` [S8]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: seed를 고정한 무작위성과 대화형 파라미터 탐색을 사용하여 p5.js 알고리즘 예술을 만든다. 사용자가 코드로 예술, 생성 예술, 알고리즘 예술, flow field, particle system 제작을 요청할 때 사용한다. 저작권 침해를 피하기 위해 기존 작가의 작업을 복제하지 않고 독창적인 알고리즘 예술을 만든다.

## `brand-guidelines`

- 원문 위치: `skills/brand-guidelines/SKILL.md:1-4` [S8]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: Anthropic의 공식 브랜드 색상과 타이포그래피를 Anthropic의 분위기가 유익한 모든 종류의 artifact에 적용한다. 브랜드 색상 또는 스타일 가이드라인, 시각적 서식, 회사 디자인 표준이 적용될 때 사용한다.

## `canvas-design`

- 원문 위치: `skills/canvas-design/SKILL.md:1-4` [S8]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: 디자인 철학을 사용해 `.png`와 `.pdf` 문서로 아름다운 시각 예술을 만든다. 사용자가 포스터, 예술 작품, 디자인, 그 밖의 정적인 결과물을 요청할 때 사용한다. 저작권 침해를 피하기 위해 기존 작가의 작업을 복제하지 않고 독창적인 시각 디자인을 만든다.

## `claude-api`

- 원문 위치: `skills/claude-api/SKILL.md:1-8` [S7]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: Claude API / Anthropic SDK의 모델 ID, 가격, 파라미터, 스트리밍, tool use, MCP, agent, caching, token counting, model migration을 위한 참조다. **트리거:** 대상 파일을 열기 **전에** 읽는다. "한 줄처럼 보인다"는 이유로 건너뛰지 않는다. 프롬프트가 Claude/Anthropic을 어떤 형태로든(Claude, Anthropic, Fable, Opus, Sonnet, Haiku, `anthropic`, `@anthropic-ai`, `claude-*`, `us.anthropic.*`, `[1m]`) 언급할 때, 사용자가 LLM의 가격/모델 선택/제한/caching을 물을 때(기억으로 답하지 않는다), 또는 제공자가 명시되지 않은 LLM 형태 작업(agent/MCP/tool-definition/multi-agent/RAG/LLM-judge/computer-use, 자연어 생성/요약/추출/분류/재작성/대화, refusal/cutoff/streaming/tool-call/token 디버깅)일 때 사용한다. **건너뛰기:** 다른 제공자를 작업 중일 때만 모든 트리거를 무시한다. 즉 질문에 OpenAI/GPT/Gemini/Llama/Mistral/Cohere/Ollama가 있거나, 제공자가 명시되지 않았으면 파일을 읽기 전에 프로젝트에서 `grep -rE 'openai|langchain_openai|google.generativeai|genai|mistralai|cohere|ollama'`를 실행해 일치할 때다.

## `discernment-nudge`

- 원문 위치: `skills/discernment-nudge/SKILL.md:1-19` [S9]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: 사용자가 실행에 옮길 수 있는 실질적 답변 또는 초안(조언·추천, 목표·계획·피치·제안서·이메일 같은 초안 artifact, 추정·예측, 데이터 분석·해석, 사용자가 의존할 사실 주장, 여러 단계의 논증)을 제공한 뒤 답변을 최종화하기 **전** 이 Skill을 호출한다. 적용된다면 방금 만든 내용의 구체적 부분에 연결되어 핵심 사실, 추론·가정, 빠진 맥락을 점검하도록 돕는 짧은 후속 질문 2~3개를 붙인다. 대화당 최대 한 번 한다. 사용자가 사소한 사용법 또는 단순 조회를 요청했거나, 순수 교육 설명을 원하거나, 제공한 내용으로 파일을 서식화·변환·조립만 해 달라고 했거나, 직접 실행할 코드를 작성하거나, 창작 글쓰기·일상 대화를 하거나, 이미 재확인·인용·검토를 요청했다면 건너뛴다. 이 Skill 파일은 이 경계와 정확한 출력 형식을 설명한다.

## `doc-coauthoring`

- 원문 위치: `skills/doc-coauthoring/SKILL.md:1-4` [S10]
- 라이선스: 원문 frontmatter에 없음
- 설명: 문서를 공동 작성하는 구조화된 워크플로를 사용자가 밟도록 안내한다. 사용자가 문서, 제안서, 기술 명세, 의사결정 문서 또는 유사한 구조화된 콘텐츠를 쓰려 할 때 사용한다. 이 워크플로는 사용자가 맥락을 효율적으로 전달하고, 반복을 통해 콘텐츠를 다듬으며, 독자에게 문서가 작동하는지 검증하도록 돕는다. 문서 작성, 제안서 생성, 명세 초안 작성 또는 유사한 문서 작업을 언급하면 트리거한다.

## `docx`

- 원문 위치: `skills/docx/SKILL.md:1-5` [S12]
- 라이선스: `Proprietary. LICENSE.txt has complete terms`
- 설명: 사용자가 Word 문서(`.docx`) 또는 Word 템플릿(`.dotx`)을 만들고, 읽고, 편집하거나 조작하려 할 때마다 사용한다. `Word doc`, `word document`, `.docx`, `.dotx` 언급, 목차·제목·페이지 번호·레터헤드 같은 서식이 있는 전문 문서 생성 요청이 트리거다. `.docx`/`.dotx` 콘텐츠 추출·재구성, 문서 이미지 삽입·교체, Word 파일 찾기·바꾸기, 변경 내용 추적·댓글, 콘텐츠를 다듬어진 Word 문서로 변환하는 경우에도 사용한다. 사용자가 `report`, `memo`, `letter`, `template` 또는 유사한 납품물을 Word/.docx로 요청하면 사용한다. PDF, 스프레드시트, Google Docs, 문서 생성과 무관한 일반 코딩에는 사용하지 않는다.

## `frontend-design`

- 원문 위치: `skills/frontend-design/SKILL.md:1-4` [S8]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: 새 UI를 만들거나 기존 UI를 재구성할 때, 개성 있고 의도적인 시각 디자인을 위한 가이드다. 미적 방향, 타이포그래피, 템플릿 기본값처럼 보이지 않는 선택을 돕는다.

## `internal-comms`

- 원문 위치: `skills/internal-comms/SKILL.md:1-4` [S8]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: 우리 회사가 선호하는 형식을 사용하여 모든 종류의 사내 커뮤니케이션을 쓰도록 돕는 리소스 묶음이다. status report, 리더십 업데이트, 3P 업데이트, 회사 뉴스레터, FAQ, incident report, 프로젝트 업데이트 등 어떤 사내 커뮤니케이션 작성을 요청받아도 Claude가 이 Skill을 사용해야 한다.

## `mcp-builder`

- 원문 위치: `skills/mcp-builder/SKILL.md:1-4` [S13]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: 잘 설계된 도구를 통해 LLM이 외부 서비스와 상호작용하도록 하는 고품질 MCP(Model Context Protocol) 서버를 만들기 위한 가이드다. Python(FastMCP) 또는 Node/TypeScript(MCP SDK)로 외부 API·서비스를 통합할 MCP 서버를 만들 때 사용한다.

## `pdf`

- 원문 위치: `skills/pdf/SKILL.md:1-5` [S14]
- 라이선스: `Proprietary. LICENSE.txt has complete terms`
- 설명: 사용자가 PDF 파일로 무엇이든 하려 할 때마다 사용한다. PDF의 텍스트/표 읽기·추출, 여러 PDF 병합, 분할, 페이지 회전, 워터마크 추가, 새 PDF 생성, PDF 양식 채우기, 암호화/복호화, 이미지 추출, 스캔 PDF를 검색 가능하게 하는 OCR이 포함된다. 사용자가 `.pdf` 파일을 언급하거나 PDF 생성 요청을 하면 사용한다.

## `pptx`

- 원문 위치: `skills/pptx/SKILL.md:1-5` [S15]
- 라이선스: `Proprietary. LICENSE.txt has complete terms`
- 설명: `.pptx` 또는 `.potx` 파일이 입력·출력·양쪽 어느 방식으로든 관련될 때마다 사용한다. 슬라이드 덱, pitch deck, 프레젠테이션 생성; `.pptx`/`.potx`의 텍스트 읽기·파싱·추출(추출한 내용을 이메일·요약 등에 쓰는 경우도 포함); 기존 프레젠테이션 편집·수정·업데이트; 슬라이드 파일 병합·분할; 템플릿(`.potx`), 레이아웃, 발표자 노트, 댓글 작업이 포함된다. 사용자가 이후 콘텐츠를 어디에 쓰려는지와 무관하게 `deck`, `slides`, `presentation`을 언급하거나 `.pptx`/`.potx` 파일명을 참조하면 트리거한다. `.pptx`/`.potx`를 열거나, 만들거나, 손대야 하면 이 Skill을 사용한다.

## `skill-creator`

- 원문 위치: `skills/skill-creator/SKILL.md:1-4` [S11]
- 라이선스: 원문 frontmatter에 없음
- 설명: 새 Skill을 만들고, 기존 Skill을 수정·개선하고, Skill 성능을 측정한다. 사용자가 처음부터 Skill을 만들거나, 기존 Skill을 편집·최적화하거나, Skill을 테스트할 eval을 실행하거나, 분산 분석으로 benchmark를 실행하거나, 더 정확한 트리거를 위해 Skill 설명을 최적화하려 할 때 사용한다.

## `slack-gif-creator`

- 원문 위치: `skills/slack-gif-creator/SKILL.md:1-4` [S16]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: Slack에 최적화된 애니메이션 GIF를 만들기 위한 지식과 유틸리티다. 제약 조건, 검증 도구, 애니메이션 개념을 제공한다. 사용자가 `make me a GIF of X doing Y for Slack`처럼 Slack용 애니메이션 GIF를 요청할 때 사용한다.

## `theme-factory`

- 원문 위치: `skills/theme-factory/SKILL.md:1-4` [S8]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: theme로 artifact를 스타일링하기 위한 도구 모음이다. artifact는 슬라이드, 문서, 보고서, HTML 랜딩 페이지 등이 될 수 있다. 색상/글꼴이 있는 사전 설정 theme 10개가 있으며, 만든 모든 artifact에 적용하거나 즉석에서 새 theme를 생성할 수 있다.

## `web-artifacts-builder`

- 원문 위치: `skills/web-artifacts-builder/SKILL.md:1-4` [S17]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: 최신 프론트엔드 웹 기술(React, Tailwind CSS, shadcn/ui)을 써서 정교하고 여러 구성요소로 이루어진 claude.ai HTML artifact를 만드는 도구 모음이다. 상태 관리, routing, shadcn/ui 구성요소가 필요한 복잡한 artifact에 사용하며, 단순한 단일 파일 HTML/JSX artifact에는 사용하지 않는다.

## `webapp-testing`

- 원문 위치: `skills/webapp-testing/SKILL.md:1-4` [S18]
- 라이선스: `Complete terms in LICENSE.txt`
- 설명: Playwright로 로컬 웹 애플리케이션과 상호작용하고 테스트하는 도구 모음이다. 프론트엔드 기능 검증, UI 동작 디버깅, 브라우저 스크린샷 캡처, 브라우저 로그 보기를 지원한다.

## `xlsx`

- 원문 위치: `skills/xlsx/SKILL.md:1-5` [S19]
- 라이선스: `Proprietary. LICENSE.txt has complete terms`
- 설명: 스프레드시트 파일이 주 입력 또는 출력인 경우마다 사용한다. 기존 `.xlsx`, `.xlsm`, `.xltx`, `.csv`, `.tsv` 파일을 열고·읽고·편집·수정(열 추가, 수식 계산, 서식, chart, 지저분한 데이터 정리 등)하거나, 처음부터 또는 다른 데이터 소스에서 새 스프레드시트를 만들거나, 표 형식 파일 사이를 변환하는 작업을 뜻한다. 사용자가 스프레드시트 파일을 이름이나 경로로(예: `the xlsx in my downloads`) 가볍게라도 언급하고, 그 파일에 어떤 작업을 하거나 결과물을 만들고 싶어 하면 특히 트리거한다. 잘못된 행, 잘못 놓인 헤더, 불필요 데이터 등 지저분한 표 데이터를 제대로 된 스프레드시트로 정리·재구성할 때도 트리거한다. 납품물은 스프레드시트 파일이어야 한다. 표 데이터가 있더라도 주 납품물이 Word 문서, HTML 보고서, 독립 Python script, 데이터베이스 pipeline, Google Sheets API 통합이면 트리거하지 않는다.

## 템플릿

- 원문 위치: `template/SKILL.md:1-5` [S5]
- `name: template-skill`
- 설명: `Replace with description of the skill and when Claude should use it.` → 이 Skill이 무엇을 하고 Claude가 언제 사용해야 하는지에 대한 설명으로 바꾼다.
- 본문 제목: `# Insert instructions below` → 아래에 지침을 넣는다.

원문 위치·고정 URL의 전체 목록은 [06-source-evidence.md](../06-source-evidence.md)에 있다.
