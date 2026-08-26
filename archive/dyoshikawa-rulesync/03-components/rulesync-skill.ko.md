---
name: rulesync
description: >-
  단일 source에서 20개 이상의 코딩 도구에 걸쳐 AI 규칙 설정 파일
  (.cursorrules, CLAUDE.md, copilot-instructions.md)을 생성하고 동기화한다.
  AI 규칙을 동기화하거나, rulesync 명령을 실행하거나, 규칙 파일을 가져오거나 생성하거나,
  공유 AI 코딩 설정을 관리할 때 사용한다.
targets: ["*"]
---

# Rulesync

Rulesync는 `.rulesync/`의 통합 규칙 파일 집합 하나에서 Claude Code, Cursor, Copilot, Cline, Gemini CLI 등을 포함한 20개 이상의 코딩 도구에 걸쳐 AI 규칙 설정 파일을 생성하고 동기화한다.

## 빠른 시작

```bash
# 설치
npm install -g rulesync

# 새 프로젝트: 설정, 규칙, 디렉터리 구조 초기화
rulesync init

# 기존 AI 도구 설정을 통합 형식으로 가져오기
rulesync import --targets claudecode    # CLAUDE.md에서
rulesync import --targets cursor        # .cursorrules에서
rulesync import --targets copilot       # .github/copilot-instructions.md에서

# 통합 규칙에서 도구별 설정 생성
rulesync generate --targets "*" --features "*"
```

## 핵심 워크플로우

1. **Init** - `rulesync init`은 `rulesync.jsonc` 설정과 예제 규칙이 있는 `.rulesync/` 디렉터리를 만든다.
2. **규칙 작성** - `.rulesync/rules/`에 공유 AI 규칙을, `.rulesync/mcp/`에 MCP 설정을, `.rulesync/commands/`에 명령을 추가한다.
3. **Generate** - `rulesync generate`는 도구별 파일(CLAUDE.md, .cursorrules, .github/copilot-instructions.md 등)을 만든다.
4. **검증** - `rulesync generate --dry-run`은 변경을 미리 보고, `--check`는 파일이 최신인지 검증한다(CI에 유용).

## 주요 명령

| 명령 | 목적 |
| --- | --- |
| `rulesync init` | 설정과 예제 규칙으로 프로젝트 골격 생성 |
| `rulesync generate --targets "*" --features "*"` | 통합 규칙에서 모든 도구 설정 생성 |
| `rulesync import --targets <tool>` | 기존 도구 설정 가져오기 |
| `rulesync fetch owner/repo` | 원격 저장소에서 스킬 가져오기 |
| `rulesync install` | rulesync.jsonc에 선언된 스킬 source 설치 |
| `rulesync generate --check` | 생성 파일이 최신인지 CI에서 확인 |
| `rulesync generate --dry-run` | 파일을 쓰지 않고 변경 미리보기 |
| `rulesync generate --watch` | source 파일이 바뀔 때마다 재생성 |
| `rulesync docs [document]` | 번들 문서 출력 |
| `rulesync docs --search <text>` | 번들 문서 검색 |

## 상세 참조

완전한 Rulesync 문서는 CLI에 번들되어 있다. **Rulesync 관련 질문에 답하거나 익숙하지 않은 Rulesync 작업을 수행하기 전에 `rulesync docs`로 확인한다.** 이것이 정식 상세 참조다.

- `rulesync docs` — 모든 문서 식별자 나열
- `rulesync docs <document>` — 한 문서 출력. 예: `rulesync docs faq` 또는 `rulesync docs guide/configuration`
- `rulesync docs --search <text>` — 문서 전체에서 순위 기반 검색. 예: `rulesync docs --search "global mode"`

유용한 시작점: `getting-started/quick-start`, `guide/configuration`, `reference/cli-commands`, `reference/supported-tools`, `reference/file-formats`, `faq`.

> 번역 원문: `skills/rulesync/SKILL.md` at `c3acceacec5463efe14ebb1b8be5fed5fa835e65`. [S19]
