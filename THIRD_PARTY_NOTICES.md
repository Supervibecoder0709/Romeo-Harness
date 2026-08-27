# 제3자 고지 (THIRD PARTY NOTICES)

이 파일은 `provenance/imports.yaml` 에서 생성한다. **직접 고치지 않는다** —
`romeo notices` 로 다시 만들고, `romeo notices --check` 가 CI 에서 대조한다.

이 저장소 자체는 Apache-2.0 이다(`LICENSE`, D-41). 아래는 그와 별개로,
원문을 그대로 담았거나(`verbatim`) 원칙만 가져온(`principle`) 외부 자산의 출처다.

## 원문 포함 (verbatim — 수정 0)

### obra/superpowers

- 출처: `https://github.com/obra/superpowers`
- 고정 커밋: `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`
- 라이선스: **MIT** (사본: `vendor/obra-superpowers@b36e082/LICENSE`, 확인일 2026-08-27)
- 로컬 경로: `vendor/obra-superpowers@b36e082/`
- 채택 게이트: G-M2

| 채택 id | 원문 경로 | 로컬 override |
| --- | --- | --- |
| `sp-finishing-a-development-branch` | `skills/finishing-a-development-branch/SKILL.md` | Step 5·6 integration commands |
| `sp-receiving-code-review` | `skills/receiving-code-review/SKILL.md` | 없음 |
| `sp-requesting-code-review` | `skills/requesting-code-review/SKILL.md`<br>`skills/requesting-code-review/code-reviewer.md` | reviewer dispatch; SKILL.md:60 의 산출물 경로 예시 |
| `sp-systematic-debugging` | `skills/systematic-debugging/SKILL.md`<br>`skills/systematic-debugging/condition-based-waiting.md`<br>`skills/systematic-debugging/condition-based-waiting-example.ts`<br>`skills/systematic-debugging/defense-in-depth.md`<br>`skills/systematic-debugging/find-polluter.sh`<br>`skills/systematic-debugging/root-cause-tracing.md` | 없음 |
| `sp-test-driven-development` | `skills/test-driven-development/SKILL.md`<br>`skills/test-driven-development/writing-good-tests.md` | 없음 |
| `sp-using-git-worktrees` | `skills/using-git-worktrees/SKILL.md` | Step 1a native worktree tool; Step 1b git fallback |
| `sp-verification-before-completion` | `skills/verification-before-completion/SKILL.md` | 없음 |

## 원칙 채택 (principle — 재작성, 원문 복사 아님)

| 채택 id | 출처 | 반영 위치 |
| --- | --- | --- |
| `anthropics-skills-skill-format` | anthropics/skills `3b3fad9` | `core/workflows/plan/SKILL.md` |
| `sp-writing-plans-absorbed` | obra/superpowers `b36e082` | `core/templates/tech-spec.md` |

## 채택하지 않은 후보

저장소에 파일이 없다. 재검토 이력을 남기기 위해 적는다.

| 후보 id | 상태 | 게이트 |
| --- | --- | --- |
| `sp-dispatching-parallel-agents` | deferred | G-M2 |
| `sp-executing-plans` | deferred | G-M2 |
| `sp-subagent-driven-development` | deferred | G-M2 |
| `sp-writing-plans` | deferred | G-M2 |
| `sp-brainstorming` | rejected | G-M2 |
| `sp-using-superpowers` | rejected | G-M2 |
| `sp-writing-skills` | rejected | G-M2 |
