# 서브에이전트 정의 번역

아래는 고정 SHA에서 읽은 `.rulesync/subagents/*.md` 다섯 파일의 사람 언어를 한국어로 옮긴 것이다. frontmatter 키·값과 명령은 유지했다.

## `code-reviewer.md`

```yaml
---
name: code-reviewer
targets: ["*"]
description: >-
  DRY, SOLID, 유지보수성, 모범 사례 같은 일반 소프트웨어 공학 원칙에
  초점을 둔 포괄적 코드 리뷰가 필요할 때 이 에이전트를 사용한다.
claudecode:
  model: inherit
---
```

일반 소프트웨어 공학 관점에서 코드를 검토한다.

- DRY 원칙 준수
- 기능 개발에 따른 테스트 코드 추가 및 갱신
- `coding-guidelines.md` 준수

- 기능 변경이 있으면 구현과 문서가 `feature-change-guidelines.md`와 일치하는지 확인한다.

그 밖의 일반 모범 사례도 검토한다.

## `diff-analyzer.md`

```yaml
---
name: diff-analyzer
targets: ["*"]
description: >-
  현재 브랜치와 origin/main의 차이를 분석하고 현재 작업 진행 상황의
  요약이 필요할 때 이 에이전트를 사용한다.
claudecode:
  model: inherit
---
```

1. `git fetch origin/main`으로 최신 main 브랜치를 가져온다.
2. `git diff origin/main...HEAD`로 현재 브랜치와 main의 차이를 가져온다.
3. `git log origin/main..HEAD --oneline`으로 현재 브랜치의 커밋 이력을 가져온다.
4. 차이와 커밋 이력을 토대로 작업 내용을 요약한다.

## `pr-handler.md`

```yaml
---
name: pr-handler
targets: ["*"]
description: >-
  사용자가 현재 변경을 커밋·push하고 영어 요약으로 pull request를
  만들거나 갱신하길 원할 때 이 에이전트를 사용한다.
claudecode:
  model: inherit
---
```

현재 브랜치의 PR을 만들거나 갱신한다. PR 제목과 본문은 영어로 작성한다.

## `pr-merger.md`

```yaml
---
name: pr-merger
targets: ["*"]
description: GitHub pull request를 병합해야 할 때 이 에이전트를 사용한다.
claudecode:
  model: inherit
---
```

프로젝트 지침에 지정된 `gh pr merge {Number} --admin --squash` 명령 형식을 사용한다.

PR 번호가 제공되지 않았고 현재 브랜치에 연결된 PR이 있으면 그 PR을 병합한다.

주의: 한 번에 하나의 PR만 병합할 수 있다.

## `security-reviewer.md`

```yaml
---
name: security-reviewer
targets: ["*"]
description: >-
  취약점과 악성 코드에 특별히 초점을 둔 보안 코드 리뷰가 필요할 때
  이 에이전트를 사용한다. 이 에이전트는 사용자가 명시적으로 호출할 때만 사용할 수 있다.
claudecode:
  model: inherit
---
```

취약점과 악성 코드를 구체적으로 검토한다. GitHub PR URL이 제공되면 그 PR을 검토하고, 없으면 현재 브랜치에 연결된 PR을 검토한다.

다음을 유의한다.

- 이 프로젝트는 사용자의 로컬 머신에서 쓰는 CLI 도구다. 따라서 불특정 다수가 사용하는 웹 애플리케이션과 보안 고려사항이 다를 수 있다. 이 프로젝트의 성격에 맞게 보안 검토한다.
- `github-actions-security.md` 준수

> 번역 원문: `.rulesync/subagents/{code-reviewer,diff-analyzer,pr-handler,pr-merger,security-reviewer}.md`. [S18]
