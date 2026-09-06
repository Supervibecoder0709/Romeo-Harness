---
id: feat-20260906-m3-close-foreign-repo-ik3u-observations
type: notes
status: active
---

# M3 관통이 대상 저장소에서 실측한 것

이 파일은 **코디네이터가 별도 실행으로 밟은 대상 저장소 관통**의 원자료다. 런북
`scenarios/12-close-foreign-repo.md` 는 이것을 읽어 절차로 정리하고, 판정은 `tests/test_foreign_close.py` 가 한다.
여기 적힌 것은 전부 2026-09-06 실측이다 — 실측하지 않은 것은 적지 않는다(K-51).

대상: `~/orca/workspaces/My-Automated-Worker/instagram-dm-sender` · 단위 `feat-20260904-claude-md-rule-conflicts-bbn8`
· run `run_bbn8m3a1c14b`

## 밟은 순서와 종료 코드

| # | 명령 | rc | 무엇이 나왔나 |
| --- | --- | --- | --- |
| 0 | `bin/romeo close --unit <id> --root <대상> --dry-run` (착수 전) | 1 | `FRONTMATTER_VALID` PASS · `APPROVED` PASS · **`HAS_EVIDENCE` FAIL** 에서 멈춘다 — 남의 루트에서도 close 기계는 그대로 돈다 |
| 1 | `git -C <대상> add docs/work/<id>/ && git commit` | 0 | `33a1c14` — 승인된 spec 을 커밋한다. **이것이 없으면 `CHECK_PLAN_COMMITTED`·`TASK_ANCHORED` 가 판정할 원본이 없다** |
| 2 | `bin/romeo envelope build --role implementer --base-sha 33a1c14 --run <r> --root <대상>` | 0 | 계약 sha256 `858f31d3fd8d` · `allowed_paths ['docs/work/<id>/', 'CLAUDE.md']` · `guards []` · `required_checks 9건` |
| 3 | `bin/romeo envelope build --role reviewer …` | 0 | 계약 sha256 `2096f3941028` |
| 4 | (구현) `CLAUDE.md` 마커 시작 줄 앞에 「## 규칙 충돌 해소」 절 60줄 삽입 | — | 381줄 → 441줄. 절은 108행, 마커는 168행 — **절이 마커 앞에 있다** |
| 5 | `git -C <대상> add CLAUDE.md && git commit` | 0 | `c3b9eae`. **증거보다 먼저 커밋한다** — 증거가 기록한 `head_sha` 를 close 가 현재 HEAD 와 대조하므로(`FRESH_HEAD`), 증거 뒤에 커밋하면 그 자리에서 실패한다 |
| 6 | `bin/romeo evidence checks --unit <id> --run <r> --root <대상>` | 0 | **9/9 exit 0** |
| 7 | `bin/romeo envelope check --role implementer --root <대상> <절대경로>` | 0 | `ENVELOPE_VALID`·`TASK_ANCHORED`·`BASE_SHA`·`EVIDENCE_ANCHORED`·`ROLE_CONTRACT` 전부 PASS |
| 8 | `bin/romeo evidence run … --label review-tree-before` | 0 | 방어 검사 기준선 |
| 9 | `codex exec -s read-only -C <대상> -m sol …` | 400 | **거부** — `The 'sol' model is not supported when using Codex with a ChatGPT account` |
| 9' | 같은 명령에서 `-m sol` 을 빼고 `--output-schema <하네스>/core/schemas/result-envelope.json` 유지 | 400 | **거부** — `invalid_json_schema` · `anyOf` 하위 스키마에 `type` 이 없다. RUNBOOK §2:42-49 가 2026-08-29 에 이미 적어 둔 실패다 |
| 9'' | 두 플래그를 뺀 형태 (`-c model_reasoning_effort=xhigh -o <밖>`) | 0 | 검토자가 돌았다 |
| 10 | `evidence run … --label review-tree-after` | 0 | before/after `log_sha256` **동일** — 방어 검사 유효(검토자가 트리를 바꾸지 않았다) |
| 11 | `bin/romeo review record --root <대상>` | 0 | 봉투 sha256 `ac9709246ea9` 를 같은 run 의 증거에 봉인 |
| — | **1회차 검토자 판정** | — | **FAIL** · `fail_reasons: [AC_UNMET, OUT_OF_SCOPE_WRITE]` · findings 2건 |
| 12 | `bin/romeo run-unit record --result fail --failure-class outputs --root <대상>` | 0 | 회차 1 fail · 연속 실패 1회 |

## 1회차 검토자가 잡은 것 — 둘 다 뿌리가 같다

**F1 `AC_UNMET`.** AC-5 는 「마커 안(108~381줄)이 바뀌지 않았다 — `sha=08dc14bf` 가 그대로다」이고 check-9 가 그 문자열을 grep 한다.
검토자: **그 grep 은 그것을 증명하지 못한다.** base `33a1c14` 의 `CLAUDE.md` 에는 **마커 블록 자체가 없다**(부착 전 106줄) —
대조할 「이전」이 이력에 없기 때문이다. 옳다.

**F2 `OUT_OF_SCOPE_WRITE`.** 증거의 `changed_files` 가 계약의 `allowed_paths`(`CLAUDE.md`·이 단위 폴더)를 벗어나
`.claude/settings.json`·`AGENTS.md`·`core/`·`adapters/` 등 100여 개를 담는다. 그것이 부착분인지 이 단위가 쓴 것인지
가를 **착수 전 상태 증거가 없다**. 옳다.

**두 finding 의 원인은 하나다 — 부착이 미커밋이라는 것.** 부착이 커밋돼 있었으면 F1 은 `git diff` 한 줄로,
F2 는 `changed_files` 그 자체로 판정됐다. 이것이 이 관통이 M5 `attach` 에 넘기는 **가장 무거운 요구사항**이다.

## 코디네이터가 저지른 범위 이탈 1건

구현 커밋 `c3b9eae` 는 `git add CLAUDE.md` 로 파일 전체를 담아, 이 단위의 60줄과 함께
**부착이 넣은 managed block 275줄도 커밋했다**(`git diff --stat 33a1c14 c3b9eae` = 335 insertions).
대상 단위 spec 의 비범위는 「대상 저장소의 부착분을 커밋하는 것」이므로 이것은 이탈이다.
사용자가 2026-09-06 에 **「이력을 다시 쓰지 않고 증거로 닫는다」**로 확정했다 — 그 사실을 지우지 않고 여기 적는다(K-51).

## 2회차 — 산출물은 그대로, 증거만 더한다

`CLAUDE.md` 는 한 글자도 바뀌지 않았다(head `c3b9eae` 그대로). 더한 증거는 셋이다.

| 라벨 | 명령 | rc | 무엇을 닫나 |
| --- | --- | --- | --- |
| `marker-block-unchanged` | `bin/romeo compile --check --root <대상>` | 0 | **F1.** 마커 안 275줄이 `core/principles/{PROJECT,AGENTS}.core.md` 에서 컴파일한 산출물과 **바이트로 같다.** 이 단위가 한 줄이라도 고쳤으면 비0 이다 — 이력을 필요로 하지 않는 재생성 증거다 |
| `unit-commit-scope` | `git -C <대상> diff --name-only 33a1c14 c3b9eae` | 0 | **F2(a).** 이 단위가 커밋으로 바꾼 파일은 `CLAUDE.md` 하나 — `allowed_paths` 안이다 |
| `uncommitted-is-attach-file` | `python3 <단위>/attach-coverage.py <대상> <하네스>` | 0 | **F2(b).** 미커밋 27항목을 `scenarios/10-attach-payload.md` 「놓는 것」과 대조해 **목록 밖 0건** |

`uncommitted-is-attach`(파일이 아니라 여러 줄 `python3 -c` 를 REMAINDER 로 넘긴 첫 시도)는 **exit 2** 로 남아 있다 —
스크립트가 잘렸다. 지우지 않고 남기고 같은 판정을 파일로 옮겼다(K-51).

## 무엇이 더 필요했나 — M2 시점에 없던 것

M2 가 끝난 시점의 대상 저장소에는 `docs/work/<id>/` 의 `brief.md`·`spec.md` 둘뿐이었다.
close 까지 가는 데 **추가로 필요했던 것**은 다음이다. 전부 종료 코드로 확인했다.

1. **승인된 spec 의 커밋**(#1). 미추적이면 `CHECK_PLAN_COMMITTED` 가 읽을 원본이 없다.
2. **작업 계약 2종**(#2·#3). `docs/work/<id>/task/` 는 `envelope build` 만 만든다 — 손으로 쓰지 않는다.
3. **구현자 결과 계약**(`result/<run>-implementer.json`). 워커가 아니라 코디네이터가 구현했으므로 이 봉투를 구현자로서 직접 썼다. `envelope check` 가 재계산으로 앵커를 확인했다(#7).
4. **검토자 절차 파일과 그 출력**(#9·#11). 대상 저장소에 `core/workflows/review/SKILL.md` 와 `core/roles/reviewer.yaml` 이 부착돼 있어 검토자가 자기 루트에서 절차를 찾을 수 있었다.

**`bin/`·`romeo/` 는 끝까지 필요하지 않았다** — 모든 명령을 하네스의 `bin/romeo` 를 `--root <대상>` 으로 불러 돌렸다(Q-54 는 그대로 열려 있다).
정책표·역할 계약·스키마는 `HARNESS_ROOT`(=돌고 있는 `romeo` 패키지의 저장소)에서 읽고, 부착 상태와 문서는 `--root` 에서 읽는다.

## 이 관통이 새로 낸 관측

- **`changed_files` 가 부착분을 전부 담는다.** 부착이 미커밋이라 `git status` 가 100여 개를 내고, 증거의 `changed_files` 가 그것을 그대로 싣는다.
  `HAS_CHANGE` 는 통과하지만 **이 단위가 무엇을 바꿨는지 그 목록으로는 갈리지 않는다.** 부착을 커밋하면 사라지는 문제이므로 M5 `attach` 의 요구사항이다.
- **시나리오 11 의 인용 대조가 이 구현으로 깨진다.** `scenarios/11-router-foreign-repo.md` 의 인용은 대상 `CLAUDE.md` 의 **줄 번호**에 고정돼 있는데,
  이 단위가 마커 앞에 60줄을 넣어 Romeo 블록 인용(L126~L210)이 전부 60줄씩 밀렸다. 그 대조는 M2 의 증거였고 required_checks 가 아니라 CI 는 빨갛지 않지만,
  **「요구하는 자리와 보는 자리를 같게 둔다」(§11)를 줄 번호로 구현하면 대상 파일이 바뀌는 순간 깨진다**는 것이 이 관통의 실측이다.
  실측(2026-09-06 · `python3 tests/test_foreign_router.py --claude-md <대상>/CLAUDE.md`): **판정 FAIL · 불일치 9건**
  `[126, 127, 160, 178, 179, 188, 189, 209, 210]` — 전부 Romeo 블록 인용이고 전부 60줄씩 밀렸다.
  BMad 블록 인용(L42·65·67·76·104)은 삽입 지점 **앞**이라 그대로 일치한다. 고치지 않았다(§12).
- **`envelope check` 의 경로 인자는 `--root` 를 따르지 않는다.** 상대 경로를 주면 코디네이터의 cwd 에서 찾아 `결과 계약 파일이 없다` 로 끝난다 — 절대 경로를 줘야 한다.
- **`run-unit` 이 인쇄하는 검토자 기동 명령에 `--output-schema` 가 들어 있다 — RUNBOOK §2 가 쓰지 말라고 적어 둔 그 플래그다.**
  그대로 실행하면 HTTP 400(`invalid_json_schema` · `anyOf` 의 하위 스키마에 `type` 이 없다)으로 끝난다. RUNBOOK §2:42-49 와 §11.1 이
  2026-08-29 에 이미 그것을 실측해 적었는데, **명령을 인쇄하는 자리(`romeo/run_unit.py`)가 그 결론을 모른다.**
  요구하는 자리와 인쇄하는 자리가 갈린 §11 의 모양이다. 고치지 않았다(§12).
- **`codex -m sol` 은 ChatGPT 계정에서 거부된다** — `The 'sol' model is not supported when using Codex with a ChatGPT account` (HTTP 400).
  모델을 지정하지 않고 `-c model_reasoning_effort=xhigh` 만 준 형태로 돌렸다.

## 2회차 검토자 — 하나가 남았다

`AC_UNMET` 은 닫혔다: 검토자가 `marker-block-unchanged`(`compile --check` exit 0)를 AC-5 의 근거로 받아들였다.
남은 것은 `OUT_OF_SCOPE_WRITE` 하나이고, 지적이 더 날카로웠다 —

> `attach-coverage.py` 는 그 경로가 부착 목록에 **포함되는지**만 비교하며 착수 전 내용과의 동일성이나 변경 시점을
> 비교하지 않는다. 따라서 부착 경로 **안에서** 이번 작업 중 수정한 파일도 통과한다. 변경 주체가 미확인이다.

옳다. **경로 일치는 변경 주체를 말하지 못한다.** 2회차를 fail 로 기록했고 **연속 실패 2회 — §10 브레이크가 걸렸다**
(`다음 기동은 --after-review 없이는 거부된다`).

## §10 브레이크 — 사람 재검토

사용자가 **「달성 가능」**으로 확정했다(2026-09-06). 근거는 3회차 착수 전 실측이다.

| 확인 | 결과 |
| --- | --- |
| `diff -r -q` — `core/`·`adapters/`·`vendor/`·`provenance/`·`skills/repo-archive/`·`.harness/bindings.yaml` vs 하네스 | 전부 바이트 동일 |
| `bin/romeo compile --check --root <대상>` | rc=0 — `CLAUDE.md`·`AGENTS.md`·`.claude/settings.json`·`.claude/agents/`·`.claude/skills/`·`.agents/skills/` |
| `bin/romeo notices --check --root <대상>` | rc=0 — `THIRD_PARTY_NOTICES.md` |

**두 번의 실패는 산출물 결함이 아니라 「부착이 미커밋」이라는 환경에서 같은 뿌리로 나왔다** — 이 단위가 무엇을
바꿨는지를 커밋 이력으로 가를 수 없다는 것. 3회차는 그것을 **이력 없이** 우회한다.
`spec`·AC·`required_checks` 를 바꾸지 않았으므로 재승인은 없다(D-80 아님).

## 3회차 — 판정을 경로에서 내용으로 옮긴다

`attach-coverage.py` 를 고쳐 부착의 두 종류를 그대로 따라 대조한다.

1. **손으로 복사한 소스 트리 여섯** — 하네스 체크아웃과 `filecmp` 재귀 대조. 대상에만 있는 파일(그 저장소 원래 스킬들)은 대조 대상이 아니다.
2. **컴파일·notices 산출물 여덟** — `compile --check`·`notices --check` 가 **지금 다시 만들어** 바이트 비교한다. 스냅숏이 필요 없다.

**판별력 실측(2026-09-06).** 대상의 `core/policy/classification.yaml` 에 주석 한 줄을 더하자 판정이
`FAIL — 부착 소스 트리가 하네스와 다르다: core` 로 뒤집혔고, 원복(바이트 동일 확인) 뒤 다시 PASS 다.
빈 값이 아니라 **그럴듯한 거짓 값**으로 잡은 반례다(§11).

## 3회차 검토자 PASS — 그런데 close 가 막았다

3회차 검토자 판정은 **PASS**(findings 1건은 스스로 「비차단」이라 적었다). 그런데 `close` 가 두 자리에서 FAIL 했다.

- `AC_ALL_CHECKED — 미체크 5개` — 대상 spec 의 수용 기준 체크박스. 구현자가 체크하면 되는 자리다.
- **`REVIEW_VERDICT`** — 1·2회차의 FAIL 봉투가 **아직 살아 있다.**

## 이 관통이 찾은 가장 무거운 것 — 판정을 산출물만의 함수로 본다

`romeo/close.py:660` 의 규칙은 이렇다.

> 현재 산출물에 대한 판정 중 PASS 가 아닌 것이 하나라도 남아 있으면 close 는 done 을 선언하지 않는다(D-c).
> **검사만 다시 기록해도 산출물이 같으면 같은 판정 대상이다.**

산출물은 봉투가 지목한 증거의 `head_sha`+`dirty_tree_hash` 로 식별한다(D-73). 그런데 **검토자는 산출물만 보지 않는다 —
증거도 본다.** 이 관통의 1·2회차 FAIL 은 **전부 증거에 대한 지적**이었고 `CLAUDE.md` 는 한 글자도 바뀌지 않았다.
그래서 3회차가 그 지적에 정확히 답해 PASS 를 받아도, 옛 FAIL 두 건은 「같은 산출물의 판정」으로 남아 close 를 막는다.

**증거만으로 답할 수 있는 FAIL 은 이 설계에서 걷어낼 길이 없다.** 하네스가 인정하는 우회는 둘뿐이다 —
산출물을 바꾸거나(그러면 해시가 움직여 옛 판정이 `REVIEW_SUPERSEDED` 가 된다), **재승인하거나**
(이전 승인 아래 낸 판정이 같은 이유로 superseded 된다). 앞의 것은 판정을 지우려고 산출물을 건드리는 것이라 쓰지 않는다.

§10 동결이므로 `romeo/close.py` 는 이 관통 중에 고치지 않는다. 관측으로 열어 둔다(§12).

## 4회차 — D-80 재승인

재승인할 **정당한 사유가 실제로 있었다.** 1회차 검토자가 증명한 것은 AC-5 자체의 결함이다 —
`sha=08dc14bf` 문자열이 남아 있다는 것은 마커 **안**이 안 바뀌었다는 뜻이 아니다. 마커 줄만 남기고 안을 통째로
갈아도 그 grep 은 통과한다. 원인이 산출물이 아니라 **완료 정의**에 있으므로 AC-5 만 고쳐 재승인했다(D-80).

| 전 | 후 |
| --- | --- |
| 「마커 안(108~381줄)이 바뀌지 않았다 — 마커 줄의 `sha=08dc14bf` 가 그대로다. (check-9, 회귀 방지 검사)」 | 「마커 **안**이 이 단위 때문에 바뀌지 않았다 — 그 블록이 `romeo compile` 산출물과 **바이트로 같다**. 판정은 증거 `marker-block-unchanged`(`compile --check --root` exit 0)가 한다. check-9 는 이 기준이 아니다(마커가 지워지지 않았다는 것만 말한다)」 |

`required_checks` 9건과 산출물은 그대로다. 재승인 커밋 `3738240` 이 새 `base_sha` 이고, 수용 기준 5건을 체크했다.
이전 승인 아래 낸 판정 3건(FAIL·FAIL·PASS)은 지우지 않고 `REVIEW_SUPERSEDED` 로 남는다(K-51).

## 4회차 — close PASS

| 검사 | 결과 |
| --- | --- |
| `EVIDENCE_SELECTED` | `run_bbn8m3r4d80` — 검증 계획 9건 전부 실행 · 지금 트리와 같은 산출물의 run 1건/4건 중 |
| `FRESH_HEAD` · `FRESH_TREE` | `37382400d215` · `baf4797281bc` 일치 |
| `CHECK_PLAN_COMMITTED` | 검사 9건이 승인 커밋 `37382400d215` 의 spec.md 와 같다 |
| `AC_ALL_CHECKED` · `AC_TEXT_UNCHANGED` | 미체크 0개 · 확인란 문장 동일 |
| `BLOCK_SATISFIED` | `spec-ready` · `risk-plan-ready`(게이트 privacy-security) |
| `REVIEW_VERDICT` | `run_bbn8m3r4d80-reviewer.json: PASS` |
| `REVIEW_SUPERSEDED` (WARN) | 이전 승인 아래 낸 판정 3건 — **재승인 전 승인**이자 **다른 산출물**(`c3b9eae+baf479`)이라 이 close 의 대상이 아니다 |
| `REVIEW_SAMPLE` (WARN) | PASS 1건으로 닫는다(D-75 (b)) |

**판정: PASS · `status: done` · `closed_at: 2026-09-06T11:45:44+09:00`.**
회차는 `fail · fail · pass · pass` 이고 재검토 1건이다. **하네스가 처음으로 `tooling`·`docs` 가 아닌 영역
(`facets: [docs, security]`)의 작업을 판정했다.**

## 대상 저장소에 남은 것

- 커밋 3건 (전부 로컬 · **push 하지 않았다**): `33a1c14` 승인 spec · `c3b9eae` 구현 · `3738240` 재승인·AC 체크
- `docs/work/feat-20260904-claude-md-rule-conflicts-bbn8/` — spec·brief·task 8건·evidence 4건·result 4건·review 4건·attempts·`attach-coverage.py`
- 부착분은 **여전히 미커밋**이다(`CLAUDE.md` 의 managed block 275줄만 `c3b9eae` 에 딸려 들어갔다)

되돌리기: `git -C <대상> revert 3738240 c3b9eae 33a1c14` + `rm -rf <대상>/docs/work/feat-20260904-claude-md-rule-conflicts-bbn8`

