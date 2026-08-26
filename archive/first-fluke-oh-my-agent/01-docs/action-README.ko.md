# oh-my-agent update action

scheduled GitHub Action으로 저장소의 [oh-my-agent](https://github.com/first-fluke/oh-my-agent) skill을 자동 업데이트합니다.

> **Marketplace:** 이 Action은 [`first-fluke/oma-update-action`](https://github.com/first-fluke/oma-update-action)을 통해 [GitHub Marketplace](https://github.com/marketplace/actions/oh-my-agent-update)에서도 사용할 수 있습니다.

## 사용법

저장소에 `.github/workflows/update-oh-my-agent.yml`을 만듭니다.

```yaml
name: Update oh-my-agent

on:
  schedule:
    - cron: "0 9 * * 1" # 매주 월요일 09:00 UTC
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: first-fluke/oma-update-action@v1
```

## 입력

| 입력 | 설명 | 기본값 |
|:------|:-----|:-------|
| `mode` | `pr`은 pull request를 만들고, `commit`은 직접 push합니다. | `pr` |
| `base-branch` | PR base 또는 direct commit 대상 branch | `main` |
| `force` | 사용자 config file을 덮어쓰기 위해 `--force` 전달 | `false` |
| `pr-title` | 사용자 지정 PR title | `chore(deps): update oh-my-agent skills` |
| `pr-labels` | PR에 붙일 comma-separated label | `dependencies,automated` |
| `commit-message` | 사용자 지정 commit message | `chore(deps): update oh-my-agent skills` |
| `token` | PR 생성용 GitHub token | `${{ github.token }}` |

## 출력

| 출력 | 설명 |
|:------|:-----|
| `updated` | 변경이 감지되면 `true` |
| `version` | update 후 oh-my-agent version |
| `pr-number` | PR 번호(`pr` mode만) |
| `pr-url` | PR URL(`pr` mode만) |

## 예시

### Direct commit mode

```yaml
- uses: first-fluke/oma-update-action@v1
  with:
    mode: commit
    commit-message: "chore: sync oh-my-agent skills"
```

### Personal Access Token 사용(fork repository)

```yaml
- uses: first-fluke/oma-update-action@v1
  with:
    token: ${{ secrets.PAT_TOKEN }}
```

### 업데이트 시에만 실행하는 conditional job

```yaml
jobs:
  update:
    runs-on: ubuntu-latest
    outputs:
      updated: ${{ steps.oma.outputs.updated }}
    steps:
      - uses: actions/checkout@v4
      - uses: first-fluke/oma-update-action@v1
        id: oma

  notify:
    needs: update
    if: needs.update.outputs.updated == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "oh-my-agent was updated!"
```

## 작동 방식

1. Bun으로 `oh-my-agent` CLI를 설치합니다.
2. `oma update --ci`를 실행합니다(non-interactive mode).
3. `.agents/`와 `.claude/` directory의 변경을 감지합니다.
4. `mode` input에 따라 PR을 만들거나 직접 commit합니다.

원문: `action/README.md` [E19]
