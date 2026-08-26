# Claude Code — Repo 안내

Repo: **@MengTo/Skills**

이 repo에는 재사용 가능한 agent workflow를 위한 designer-focused AgentSkills가 있다.

## 여기서 할 일

- 새 skill 추가: agent-skills 아래에 새 folder
- 기존 skill 개선: SKILL.md + REFERENCES.md
- 문서를 절차적으로 유지: checklist, recipe, pitfall, workflow

## Folder 계약

각 skill folder는 다음과 같아야 한다.

~~~txt
agent-skills/<category>/<skill-name>/
  SKILL.md            # 필수: frontmatter + 단계
  REFERENCES.md       # 선택: link만
  ARTICLE.md          # 선택: 긴 형식
  assets/             # 선택
  scripts/            # 선택
~~~

관례:

- SKILL.md는 간결하고 실행 가능해야 한다.
- REFERENCES.md는 link만 담는다. 큰 설명을 넣지 않는다.
- copy/paste snippet과 언제 사용할지의 trigger를 선호한다.

## 스타일

- Meng To처럼 쓴다: 훑기 쉽고, 실용적이며, 자신감 있게.
- duration, spacing, hierarchy 같은 constraint와 default를 선호한다.
- 군더더기를 피한다.

## 안전

- secret, API key, token을 포함하지 않는다.
- private client information을 붙여 넣지 않는다.

## 권장 workflow (Claude용)

1) 가장 구체적인 skill folder를 식별한다.
2) SKILL.md를 먼저 update한다.
3) REFERENCES.md의 link를 추가/갱신한다.
4) 변경을 작게 유지하고 명확한 message로 commit한다.

## Git

이 folder는 자체 git repo다. 다음에서 작업한다.

~~~bash
cd /Users/mengto/clawd/@MengTo/Skills
~~~
