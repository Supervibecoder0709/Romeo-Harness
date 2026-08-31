# BMM persona agent 구성요소

아래는 `src/bmm-skills/**/bmad-agent-*/SKILL.md`와 각 `customize.toml`의 `[agent]`를 한국어로 옮겨 놓은 실행 관점 요약이다. 이들은 독립 산출물 생성기가 아니라, 인사·설정 로드 뒤 menu의 다른 skill을 dispatch하는 **대화형 persona session**이다. agent 호출만으로 output file이 생긴다고 보면 안 된다. [E07][E15]

| Agent | 원문 skill | 역할(번역) | 기본 menu가 향하는 작업 |
| --- | --- | --- | --- |
| Mary — Business Analyst | `1-analysis/bmad-agent-analyst/SKILL.md` | 시장·경쟁·요구사항·도메인 지식을 증거 기반으로 정리하는 사업 분석가 | brainstorming, market/domain/technical research, product brief, PRFAQ, document project |
| Paige — Technical Writer | `1-analysis/bmad-agent-tech-writer/SKILL.md` | 복잡한 내용을 읽기 쉬운 구조·문서·다이어그램으로 만드는 기술 문서 담당 | document project, write document, Mermaid, validation, concept explanation |
| John — Product Manager | `2-plan-workflows/bmad-agent-pm/SKILL.md` | JTBD와 사용자 가치 관점에서 PRD·epic·change를 이끄는 PM | PRD, epics/stories, implementation readiness, correct course |
| Sally — UX Designer | `2-plan-workflows/bmad-agent-ux-designer/SKILL.md` | 사용자 요구와 edge case를 UX 계약으로 만드는 UX designer | `bmad-ux` |
| Winston — System Architect | `3-solutioning/bmad-agent-architect/SKILL.md` | 안정성·개발 생산성·사업 가치를 trade-off로 명시하는 architect | architecture, implementation readiness |
| Amelia — Senior Software Engineer | `4-implementation/bmad-agent-dev/SKILL.md` | AC·파일 경로·test-first 규율에 따라 구현을 진행하는 developer | dev story, quick dev, QA tests, code review, sprint plan, create story, retrospective |

공통 activation은 `_bmad/scripts/resolve_customization.py`로 base/team/user override를 합치고, `_bmad/bmm/config.yaml`의 language와 artifact roots를 읽으며, 명확한 intent가 없으면 menu를 표시하고 입력을 기다린다. 따라서 “agent 자동 실행”이 아니라 “agent를 사용자가 고른 뒤 다음 skill로 route”하는 구조다. [E15]
