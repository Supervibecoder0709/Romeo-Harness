---
id: feat-20260904-m2-router-foreign-repo-ct5h-observations
type: note
title: M2 관통 실측 — 라우터를 남의 저장소에서 돌리며 관측한 것
status: active
created: '2026-09-04'
updated: '2026-09-04'
---

# M2 관통 실측 (2026-09-04)

이 문서는 `spec.md` 의 구현 단계 3(대상 저장소에서 라우터 실행)이 **실제로 겪은 것**을 적는다.
런북 `scenarios/11-router-foreign-repo.md` 는 이 실측 위에 쓴다 — 여기 없는 것을 런북에 적지 않는다(K-51).

대상: `~/orca/workspaces/My-Automated-Worker/instagram-dm-sender`
하네스: `~/orca/workspaces/Romeo-Harness/mvp_planning` (base `52d022c`)

## 1. 어디서 실행했는가 — 두 번 막히고 세 번째에 돌았다

| 시도 | 방법 | 결과 |
| --- | --- | --- |
| 1 | `orca terminal create --worktree <대상>` | **불가.** 대상 저장소가 Orca 에 등록돼 있지 않았다 — `worktree show --worktree path:<대상>` 이 `selector_not_found` |
| 2 | `orca repo add --path ~/orca/My-Automated-Worker` 뒤 같은 명령 | **불가.** repo 는 등록됐지만(`978af056-…`) Orca 가 인식하는 워크트리는 `main` 하나다. `instagram-dm-sender` 는 raw `git worktree add` 로 만들어진 **외부 워크트리**라 목록에 없고, 외부 워크트리 가시성을 켜는 CLI 명령이 없다(`orca repo` 의 하위 명령은 list·add·show·set-base-ref·search-refs 뿐) |
| 3 | 대상 디렉터리에서 `claude -p` (비대화형) | **성공.** 이것이 실제로 쓴 경로다 |

**부착과 실행 환경 등록은 별개다.** 부착은 파일을 놓았지만, 그 저장소에서 에이전트를 띄우는 수단은
부착이 만들어 주지 않는다. 새 Orca 워크트리를 만드는 길은 택하지 않았다 — 부착이 **미커밋**이라
새 워크트리는 그것을 보지 못하고 M1 을 다시 밟아야 한다.

## 2. `bin/romeo --root` — 1회차 미검증, 2회차 5종 전부 rc=0

**1회차(`--permission-mode acceptEdits` 만):** `bin/romeo` 가 **한 줄도 돌지 않았다.**
막은 것은 romeo 도 `--root` 도 아니라 **비대화형 세션의 Bash 허용목록**이다 —
허용목록 밖 실행 파일은 승인 프롬프트로 가는데 비대화형이라 자동 거부된다(`gh` 도 같은 이유로 거부).

원인은 부착이 놓은 `.claude/settings.json` 에 **`permissions.allow` 가 없다는 것**이다.
`romeo/compile.py` 의 `_render_settings` 는 `ask`·`deny` 만 만든다. 부착 전 파일에도 `allow` 는 없었다.

부착 후 대상의 `.claude/settings.json`:

```json
{"permissions": {"additionalDirectories": ["~/.coupang-auto"],
 "deny": ["Bash(rm -rf /)", …, "Bash(git push -f:*)"],
 "ask": ["Bash(gh pr merge:*)", "Bash(git worktree remove:*)", "Bash(git branch -D:*)", "Bash(git reset --hard:*)"]}}
```

**2회차(`--allowedTools` 로 `Bash(<하네스>/bin/romeo:*)` 를 명시):** 5종 전부 rc=0.

| 명령 | rc | 출력 |
| --- | --- | --- |
| `romeo find … --root <대상>` | 0 | 재사용 후보 없음 |
| `romeo card --proposal … --root <대상>` | 0 | 카드 30줄 |
| `romeo route --proposal … --root <대상>` | 0 | profile=standard · package=[brief,spec] |
| `romeo new --proposal … --root <대상>` | 0 | brief.md·spec.md 생성 · skipped=[] |
| `romeo validate --root <대상>` | 0 | PASS 2건 |

**Q-54 의 답:** 대상 저장소만으로는 라우터를 돌릴 수 없지만, 하네스 경로를 `--root` 로 참조하면 **돈다.**
막는 것은 `--root` 가 아니라 그 저장소에 실행 권한이 열려 있지 않다는 것이다.

## 3. 두 라우팅 규칙 — 공존하지 않는다. 충돌 3쌍 + 겹침 + 없는 파일

대상 `CLAUDE.md` 는 381줄. 1~107줄이 BMad 블록, 108~381줄이 `<!-- romeo:managed -->` 블록이다.

| # | BMad | Romeo | 같은 상황 |
| --- | --- | --- | --- |
| C-1 | §8(`:65-82`) 한국어 발화로 `bmad-*` 스킬 라우팅 | §1(`:178-179`) K-60 부품 스킬은 키워드로 자동 활성화되지 않는다 | 사용자가 "코드 리뷰해줘" |
| C-2 | §10(`:104`) BMad 산출물은 `_bmad-output/` 정본 경로를 **그대로 따른다** | §7(`:209-210`) K-62 부품의 기본 출력 경로를 **그대로 쓰지 않는다** | 부품이 산출물을 낼 때 |
| C-3 | §2(`:42`) 명시적 구현 요청이면 **되묻지 말고 착수** | §3(`:188-190`) D-27 확인란 승인이 **유일한 선행 조건** | 사용자가 "이거 구현해줘" |

**C-4 §번호 겹침:** 두 블록이 §1·§2·§4·§5·§8·§9·§10 을 각각 갖는다.
"§2 를 따르라"가 파일 안에서 구별되지 않는다.

**C-5 없는 파일을 읽으라는 지시:** Romeo 블록의 「세션을 시작할 때」·「문서 인덱스」가 지목하는
`docs/planning/progress.md`·`docs/decisions/decision-register.md`·`docs/planning/open-questions.md`·
`docs/requirements/`·`docs/reviews/` 가 **이 저장소에 없다**(`ls` 실측). 하네스 저장소용 인덱스가 그대로 이식됐다.
`CLAUDE.md:158-160` 의 "하네스가 하네스를 만든다. 여기서 만든 규칙이 이 저장소 자신에게 적용된다" 도
그 저장소에 대한 서술로는 거짓이다. **Romeo §11 이 스스로 금지한 모양 그대로다** —
요구는 인쇄됐고 그 요구가 가리키는 대상은 없다. BMad 가 가리키는 `docs/agent-rules/`·`_bmad-output/`·`skills/` 는 전부 실재한다.

**어느 쪽을 먼저 따랐는가:** Romeo. 그러나 **Romeo 가 이겨서가 아니라 호출자가 명시적으로 지목했기 때문**이다
(`CLAUDE.md:124-127` 「충돌 해소 순서」 1순위 = "현재 사용자의 명시적 요청").
지목이 없었으면 그 파일만 읽고는 어느 쪽이 먼저인지 정할 수 없다 —
BMad 블록은 Romeo 를 한 번도 언급하지 않고, Romeo 블록도 "마커 밖에 쓴 내용은 보존된다" 고만 할 뿐
마커 밖 규칙이 지는지 이기는지 말하지 않는다.

## 4. charter 전제 하나가 틀렸다 — 관통시킬 작업이 없었다

charter 의 「지금 참으로 가정하는 것」은 "대상 저장소에 M3 시점에 관통시킬 실제 작업이 있다" 였다.
**틀렸다.** 사용자가 처음 고른 GitHub issue 14번은 4개 sub-issue 의 산출물이 **전부 실재**한다
(`docs/secrets-policy.md` · `scripts/scan-secrets.sh` 16,793B · `skills/secrets-policy/` + 심볼릭 링크 ·
`_bmad/custom/bmad-dev-story.toml`·`bmad-quick-dev.toml` 의 정책 fact). 체크박스만 미체크다.
대체 후보 #36·#15·#51·#52 도 `skills/` 아래 SKILL.md 가 이미 있다.

그래서 관통 대상을 **이 관통이 방금 실측한 것**으로 바꿨다(사용자 확정 2026-09-04) —
위 C-1~C-5 를 대상 저장소의 `CLAUDE.md` 마커 밖에서 해소하는 단위다.

## 5. 대상 저장소에 선 단위

- id: `feat-20260904-claude-md-rule-conflicts-bbn8`
- `unit: T1` · `mode: delivery` · `intent: write` · `facets: [docs, security]` · `gates: [privacy-security]` · `profile: standard`
- `status: active` · `approved_at: 2026-09-04T23:44:05+09:00` · `approved_by: Supervibecoder0709`
- `security` 를 붙인 근거: `classification.yaml` 의 `security` 는 "시크릿·취약점·**권한 경계**" 이고,
  C-3(승인 없이 착수)이 승인 게이트를 무력화할 수 있으므로 권한 경계 문제다. 사람이 확정했다.

## 6. 이 관통이 낸 관측 (고치지 않고 열어 둔다 · §12)

1. 부착이 `.claude/settings.json` 에 `permissions.allow` 를 놓지 않아, 부착된 저장소에서 도는
   **비대화형 위임 실행이 `bin/romeo` 를 부를 수 없다.** M5 `attach` 가 다뤄야 한다.
2. 부착된 저장소가 실행 환경(Orca)에 등록돼 있지 않을 수 있고, raw `git worktree add` 로 만든 외부 워크트리는
   `orca repo add` 뒤에도 Orca 가 인식하지 못한다.
3. Romeo managed block 이 **부착 대상에 없는 문서 5종**을 세션 시작에 읽으라고 지시한다(C-5).
   컴파일이 하네스 저장소용 인덱스를 그대로 투영한다.
4. `romeo validate` 는 `NEEDS_INPUT` 이 17곳 남은 문서에도 `[PASS]` + `WARN` 을 낸다.
   Romeo §3 은 "확인란에 `NEEDS_INPUT` 이 남아 있으면 승인할 수 없다" 고 요구하는데
   `validate` 는 그것을 막지 않는다 — 차단이 `approve` 쪽에 있는지는 이번에 확인하지 않았다.
   **요구하는 자리와 보는 자리**를 점검할 지점이다(§11).
5. 대상 저장소에 `docs/planning/open-questions.md` 가 없어, 그 저장소에서 도는 실행은 §12 를 지킬 자리가 없다.
