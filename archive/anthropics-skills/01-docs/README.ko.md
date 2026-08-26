> **참고:** 이 저장소에는 Claude용 Anthropic Skill 구현이 들어 있습니다. Agent Skills 표준 정보는 [agentskills.io](http://agentskills.io)를 보세요.

[![skills.sh](https://skills.sh/b/anthropics/skills)](https://skills.sh/anthropics/skills)

# Skills

Skill은 특화 작업의 성능을 높이기 위해 Claude가 동적으로 불러오는 지침, 스크립트, 리소스의 폴더입니다. Skill은 회사의 브랜드 가이드라인으로 문서를 만들거나, 조직 고유의 워크플로로 데이터를 분석하거나, 개인 작업을 자동화하는 등 특정 작업을 반복 가능한 방식으로 완료하는 방법을 Claude에게 가르칩니다.

자세한 정보:

- [Skill이란?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Claude에서 Skill 사용하기](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [사용자 정의 Skill 만들기](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Agent Skills로 실제 세계의 agent를 갖추게 하기](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

# 이 저장소 소개

이 저장소에는 Claude의 Skill 시스템으로 무엇을 할 수 있는지 보여 주는 Skill이 들어 있습니다. 이 Skill은 창의적 응용(예술, 음악, 디자인), 기술 작업(웹 앱 테스트, MCP 서버 생성), 기업 워크플로(커뮤니케이션, 브랜딩 등)를 아우릅니다.

각 Skill은 Claude가 사용하는 지침과 메타데이터가 든 `SKILL.md` 파일을 포함하는 자체 폴더에 있습니다. 이 Skill들을 살펴보며 자신만의 Skill을 위한 영감을 얻거나, 여러 패턴과 접근법을 이해할 수 있습니다.

이 저장소의 많은 Skill은 오픈 소스(Apache 2.0)입니다. 또한 Claude의 [문서 생성 기능](https://www.anthropic.com/news/create-files)을 내부적으로 구동하는 문서 생성·편집 Skill을 [`skills/docx`](./skills/docx), [`skills/pdf`](./skills/pdf), [`skills/pptx`](./skills/pptx), [`skills/xlsx`](./skills/xlsx) 하위 폴더에 넣었습니다. 이들은 오픈 소스가 아니라 source-available이지만, 실제 운영 중인 AI 애플리케이션에서 활발히 쓰이는 더 복잡한 Skill의 참고 자료를 개발자와 공유하고자 포함했습니다.

## 면책 사항

**이 Skill들은 시연 및 교육 목적으로만 제공됩니다.** 일부 기능은 Claude에서 사용할 수 있을 수 있으나, Claude에서 실제로 받는 구현과 동작은 이 Skill에 보이는 것과 다를 수 있습니다. 이 Skill들은 패턴과 가능성을 보여 주기 위한 것입니다. 중요한 작업에 의존하기 전에는 항상 자신의 환경에서 Skill을 충분히 테스트하세요.

# Skill 묶음

- [./skills](./skills): Creative & Design, Development & Technical, Enterprise & Communication, Document Skills의 Skill 예시
- [./spec](./spec): Agent Skills 명세
- [./template](./template): Skill 템플릿

# Claude Code, Claude.ai, API에서 사용해 보기

## Claude Code

Claude Code에서 다음 명령을 실행하여 이 저장소를 Claude Code Plugin marketplace로 등록할 수 있습니다.

```
/plugin marketplace add anthropics/skills
```

그런 다음 특정 Skill 묶음을 설치합니다.

1. `Browse and install plugins`를 선택합니다.
2. `anthropic-agent-skills`를 선택합니다.
3. `document-skills` 또는 `example-skills`를 선택합니다.
4. `Install now`를 선택합니다.

또는 다음으로 두 플러그인 중 하나를 직접 설치합니다.

```
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

플러그인을 설치한 뒤에는 Skill을 언급하기만 하면 사용할 수 있습니다. 예를 들어 marketplace에서 `document-skills` 플러그인을 설치했다면 Claude Code에 다음과 같이 요청할 수 있습니다. `Use the PDF skill to extract the form fields from path/to/some-file.pdf`

## Claude.ai

이 예시 Skill들은 모두 Claude.ai 유료 플랜에서 이미 사용할 수 있습니다.

이 저장소의 Skill을 사용하거나 사용자 정의 Skill을 업로드하려면 [Claude에서 Skill 사용하기](https://support.claude.com/en/articles/12512180-using-skills-in-claude#h_a4222fa77b)의 지침을 따르세요.

## Claude API

Anthropic의 사전 구축 Skill을 사용하고 사용자 정의 Skill을 업로드할 수 있습니다. [Skills API Quickstart](https://docs.claude.com/en/api/skills-guide#creating-a-skill)를 보세요.

# 기본 Skill 만들기

Skill은 만들기 쉽습니다. YAML frontmatter와 지침이 담긴 `SKILL.md` 파일이 있는 폴더 하나면 됩니다. 이 저장소의 **template-skill**을 시작점으로 사용할 수 있습니다.

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when Claude should use it
---

# My Skill Name

[Add your instructions here that Claude will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

frontmatter에는 두 필드만 필요합니다.

- `name` - Skill의 고유 식별자(소문자, 공백은 하이픈)
- `description` - Skill이 무엇을 하고 언제 사용해야 하는지에 대한 완전한 설명

그 아래 Markdown 본문에는 Claude가 따를 지침, 예시, 가이드라인이 들어갑니다. 자세한 내용은 [사용자 정의 Skill 만들기](https://support.claude.com/en/articles/12512198-creating-custom-skills)를 보세요.

# 파트너 Skill

Skill은 Claude가 특정 소프트웨어를 더 잘 사용하도록 가르치는 좋은 방법입니다. 파트너의 훌륭한 Skill 예시를 발견하면 이곳에 소개할 수 있습니다.

- **Notion** - [Notion Skills for Claude](https://www.notion.so/notiondevs/Notion-Skills-for-Claude-28da4445d27180c7af1df7d8615723d0)

> 번역 범위: 고정 커밋의 `README.md` 전체를 번역했다. 코드블록의 식별자·명령·URL은 원문 그대로 보존했다. 근거: [S3](../06-source-evidence.md#s3).
