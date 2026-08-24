# Superpowers

> 원문: [`README.md`](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/README.md) — 고정 SHA `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`의 한국어 번역. 명령·경로·URL·식별자는 유지했다.

Superpowers는 조합 가능한 skill 묶음과, agent가 이 skill을 사용하도록 하는 초기 지침 위에 구축한 coding agent용 완전한 소프트웨어 개발 방법론이다.

## 목차

- [작동 방식](#작동-방식)
- [상업 서비스](#상업-서비스)
- [시작하기](#설치)
- [기본 워크플로우](#기본-워크플로우)
- [커뮤니티](#커뮤니티)
- [포함된 내용](#포함된-내용)
- [철학](#철학)
- [기여](#기여)
- [업데이트](#업데이트)
- [라이선스](#라이선스)
- [Visual companion telemetry](#visual-companion-telemetry)

## 작동 방식

coding agent를 실행하는 순간부터 시작한다. agent는 무엇인가를 만들고 있다는 것을 보면 곧바로 코드를 쓰려 들지 않고, 실제로 달성하려는 목적을 한 걸음 물러서서 묻는다.

대화에서 spec을 끌어낸 뒤, 실제로 읽고 소화할 수 있을 만큼 짧은 단위로 보여 준다.

설계를 승인하면 agent는 프로젝트 맥락도 판단력도 테스트 선호도도 부족한 열정적인 주니어 엔지니어가 따라갈 수 있을 정도로 명확한 구현 계획을 만든다. 이 계획은 진짜 RED/GREEN TDD, YAGNI(당장 필요하지 않은 기능은 만들지 않음), DRY를 강조한다.

그 다음 사용자가 "go"라고 하면 `subagent-driven-development` 절차를 시작한다. agents가 각 engineering task를 수행하고, 자신의 작업을 살피고 검토받으며 전진한다. 합의한 계획에서 벗어나지 않은 채 몇 시간 동안 자율 작업하는 일도 드물지 않다.

더 많은 내용이 있지만 이것이 시스템의 핵심이다. skill이 자동으로 trigger되므로 사용자가 특별히 할 일은 없다. coding agent가 Superpowers를 갖게 되는 것이다.

## 상업 서비스

기업에서 Superpowers를 사용하며 상업 지원, 추가 도구 또는 관리형 비용 운영이 필요하다면 `sales@primeradiant.com`으로 연락할 수 있다.

## 설치

설치는 harness마다 다르다. 둘 이상을 사용한다면 각 harness에 Superpowers를 따로 설치한다.

### Claude Code

Superpowers는 [공식 Claude plugin marketplace](https://claude.com/plugins/superpowers)에서 제공된다.

#### 공식 Marketplace

- Anthropic 공식 marketplace에서 plugin을 설치한다.

  ```bash
  /plugin install superpowers@claude-plugins-official
  ```

#### Superpowers Marketplace

Superpowers marketplace는 Claude Code용 Superpowers와 관련 plugin을 제공한다.

- marketplace를 등록한다.

  ```bash
  /plugin marketplace add obra/superpowers-marketplace
  ```

- 이 marketplace에서 plugin을 설치한다.

  ```bash
  /plugin install superpowers@superpowers-marketplace
  ```

### Antigravity

이 저장소에서 plugin으로 설치한다.

```bash
agy plugin install https://github.com/obra/superpowers
```

Antigravity는 plugin의 session-start hook을 실행하므로 Superpowers는 첫 메시지부터 활성화된다. 업데이트하려면 같은 명령을 다시 실행한다.

### Codex App

Superpowers는 [공식 Codex plugin marketplace](https://github.com/openai/plugins)에서 제공된다.

- Codex app sidebar에서 Plugins를 클릭한다.
- Coding 섹션의 `Superpowers`를 찾는다.
- Superpowers 옆 `+`를 클릭하고 안내를 따른다.

### Codex CLI

Superpowers는 [공식 Codex plugin marketplace](https://github.com/openai/plugins)에서 제공된다.

- plugin 검색 화면을 연다.

  ```bash
  /plugins
  ```

- Superpowers를 검색한다.

  ```bash
  superpowers
  ```

- `Install Plugin`을 선택한다.

### Cursor

- Cursor Agent chat에서 marketplace로 설치한다.

  ```text
  /add-plugin superpowers
  ```

- 또는 plugin marketplace에서 "superpowers"를 검색한다.

### Devin CLI

- 이 저장소에서 plugin을 설치한다.

  ```bash
  devin plugins install obra/superpowers
  ```

- 최신 버전으로 업데이트한다.

  ```bash
  devin plugins update superpowers
  ```

### Factory Droid

- marketplace를 등록한다.

  ```bash
  droid plugin marketplace add https://github.com/obra/superpowers
  ```

- plugin을 설치한다.

  ```bash
  droid plugin install superpowers@superpowers
  ```

### Gemini CLI

- extension을 설치한다.

  ```bash
  gemini extensions install https://github.com/obra/superpowers
  ```

- 나중에 업데이트한다.

  ```bash
  gemini extensions update superpowers
  ```

### GitHub Copilot CLI

- marketplace를 등록한다.

  ```bash
  copilot plugin marketplace add obra/superpowers-marketplace
  ```

- plugin을 설치한다.

  ```bash
  copilot plugin install superpowers@superpowers-marketplace
  ```

### Grok Build CLI

Superpowers는 [공식 Grok plugin marketplace](https://github.com/xai-org/plugin-marketplace)에서 제공된다.

- xAI 공식 marketplace에서 plugin을 설치한다.

  ```bash
  grok plugin install superpowers@xai-official --trust
  ```

- 또는 TUI에서 marketplace를 열어 Superpowers를 검색해 설치한다.

  ```text
  /marketplace
  ```

### Kimi Code

Superpowers는 Kimi Code plugin marketplace에서 제공된다.

- Kimi Code plugin manager를 연다.

  ```text
  /plugins
  ```

- `Marketplace` > `Superpowers`로 이동해 설치한다.
- 또는 이 저장소에서 직접 설치한다.

  ```text
  /plugins install https://github.com/obra/superpowers
  ```

- 상세 문서: [docs/README.kimi.md](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/docs/README.kimi.md)

### OpenCode

다른 harness에서 이미 사용하고 있더라도 OpenCode는 자체 plugin 설치를 사용하므로 Superpowers를 별도로 설치한다.

- OpenCode에 다음을 말한다.

  ```
  Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md
  ```

- 상세 문서: [docs/README.opencode.md](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/docs/README.opencode.md)

### Pi

이 저장소에서 Pi package로 설치한다.

```bash
pi install git:github.com/obra/superpowers
```

로컬 개발에서는 이 checkout을 임시 package로 로드한 Pi를 실행한다.

```bash
pi -e /path/to/superpowers
```

Pi package는 Superpowers skills와 작은 extension을 로드한다. 이 extension은 session 시작 시와 compaction 뒤에 `using-superpowers` bootstrap을 넣는다. Pi는 native skills를 가지므로 호환용 `Skill` tool은 필요하지 않다. subagent와 task-list tools는 선택적인 Pi companion package로 남는다.

### Hermes Agent

이 저장소에서 Hermes plugin으로 설치한다.

```bash
hermes plugins install obra/superpowers --enable
```

설치 후 활성 Hermes session은 다시 시작한다. Hermes에는 post-compaction hook이 없으므로, 첫 turn을 넘겨 compaction된 긴 session에서는 bootstrap을 잃는다. skill이 trigger되지 않으면 새 session을 시작한다.

## 기본 워크플로우

1. **brainstorming** — 코드를 쓰기 전에 활성화된다. 질문을 통해 거친 아이디어를 다듬고, 대안을 살피며, 검증할 수 있도록 구간별 설계를 제시한다. design document를 저장한다.
2. **using-git-worktrees** — 설계 승인 뒤 활성화된다. 새 branch의 격리 workspace를 만들고, project setup을 실행하며, 깨끗한 test baseline을 확인한다.
3. **writing-plans** — 승인된 design으로 활성화된다. 작업을 2~5분짜리 작은 task로 나눈다. 모든 task에는 정확한 file path, 완전한 코드, verification step이 있다.
4. **subagent-driven-development** 또는 **executing-plans** — plan과 함께 활성화된다. task마다 새 subagent를 dispatch하고 두 단계 검토(spec compliance, code quality)를 하거나, 사람 checkpoint가 있는 batch로 실행한다.
5. **test-driven-development** — 구현 중 활성화된다. RED-GREEN-REFACTOR를 강제한다. failing test 작성, 실패 관찰, 최소 코드 작성, 통과 관찰, commit 순서다. test보다 먼저 쓴 코드는 삭제한다.
6. **requesting-code-review** — task 사이에 활성화된다. plan 대비 검토하고 severity별 issue를 보고한다. Critical issue는 진행을 막는다.
7. **finishing-a-development-branch** — task가 끝나면 활성화된다. test를 확인하고 merge/PR/보존/폐기 선택지를 제시하며 worktree를 정리한다.

**agent는 모든 task 전에 관련 skill을 확인한다.** 제안이 아니라 의무 workflow다.

## 커뮤니티

Superpowers는 [Jesse Vincent](https://blog.fsck.com)과 [Prime Radiant](https://primeradiant.com)의 사람들이 만든다.

- **Discord**: [참여하기](https://discord.gg/35wsABTejz) — community support, 질문, 만드는 것 공유
- **Issues**: https://github.com/obra/superpowers/issues
- **Release announcements**: [알림 신청](https://primeradiant.com/superpowers/)

## 포함된 내용

### Skills Library

**Testing**

- **test-driven-development** — RED-GREEN-REFACTOR cycle(테스트 anti-pattern 참고 포함)

**Debugging**

- **systematic-debugging** — 4단계 root cause 절차(root-cause-tracing, defense-in-depth, condition-based-waiting 기법 포함)
- **verification-before-completion** — 실제로 고쳐졌는지 확인

**Collaboration**

- **brainstorming** — Socratic design refinement
- **writing-plans** — 상세 구현 계획
- **executing-plans** — checkpoint가 있는 batch 실행
- **dispatching-parallel-agents** — 동시 subagent workflow
- **requesting-code-review** — 사전 검토 checklist
- **receiving-code-review** — feedback에 대응
- **using-git-worktrees** — 병렬 개발 branch
- **finishing-a-development-branch** — merge/PR 의사결정 workflow
- **subagent-driven-development** — 두 단계 검토(spec compliance, code quality)가 있는 빠른 반복

**Meta**

- **writing-skills** — 모범 사례에 따라 새 skill 생성(테스트 방법론 포함)
- **using-superpowers** — skill system 소개

## 철학

- **Test-Driven Development** — 항상 test를 먼저 작성한다.
- **임기응변보다 체계** — 추측보다 절차를 택한다.
- **복잡성 감소** — 단순성을 최우선 목표로 둔다.
- **주장보다 근거** — 성공이라고 하기 전에 검증한다.

[원래 release announcement 읽기](https://blog.fsck.com/2025/10/09/superpowers/).

## 기여

일반적인 기여 절차는 아래와 같다. 일반적으로 새 skill 기여는 받지 않으며, skill 변경은 지원하는 모든 coding agent에서 작동해야 한다.

1. 저장소를 fork한다.
2. `dev` branch로 전환한다.
3. 작업 branch를 만든다.
4. 새 skill을 만들거나 수정하고 테스트할 때 `writing-skills` skill을 따른다.
5. pull request template을 모두 채워 PR을 제출한다.

Skill behavior test는 `evals/`에 clone한 [superpowers-evals](https://github.com/prime-radiant-inc/superpowers-evals)의 drill eval harness를 쓴다. setup은 `evals/README.md`를 본다. Plugin infrastructure test는 `tests/`에 있으며 해당 `run-*.sh` 또는 `npm test`로 실행한다.

전체 안내는 `skills/writing-skills/SKILL.md`를 본다.

## 업데이트

Superpowers의 업데이트 방식은 coding agent에 따라 다르지만, 종종 자동이다.

## 라이선스

MIT License — 자세한 내용은 `LICENSE` 파일을 본다.

## Visual companion telemetry

skill과 plugin은 제작자에게 feedback을 주지 않기 때문에 사용자가 얼마나 되는지 알 수 없다. 기본적으로 brainstorming의 선택적 visual companion 기능에서 Prime Radiant logo를 웹사이트에서 불러온다. 여기에는 사용 중인 Superpowers version이 포함된다. 프로젝트·prompt·coding agent의 세부 정보는 포함하지 않는다. 클릭이나 무엇을 만드는지도 보지 않는다. 이를 통해 대략적인 사용자 수와 version을 파악한다.

이 기능은 완전히 선택 사항이다. 비활성화하려면 environment variable `SUPERPOWERS_DISABLE_TELEMETRY`에 true 값 아무거나 설정한다. Claude Code의 `DISABLE_TELEMETRY`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` opt-out도 따른다.
