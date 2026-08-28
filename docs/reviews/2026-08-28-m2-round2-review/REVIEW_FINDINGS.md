# 2차 리뷰 findings (워크플로 wf_3392dea0-077)

blocker 5 · important 5 · minor 3

## G01 [blocker] (실행가능성-재검사)
**대상:** `adapters/claude/workflows/implement.md`

**요약:** 구현자 런타임 지침 3번이 작업 계약을 손으로 JSON 으로 써서 git 제외 경로에 두라고 지시한다 — 같은 파일 1번이 따르라고 한 core 절차와 RUNBOOK 이 명시적으로 금지한 행동이다.

**증거:**

```
$ sed -n '1,3p' adapters/claude/workflows/implement.md
1. `core/workflows/implement/SKILL.md` 를 읽고 절차를 그대로 따른다. ...
3. 작업 계약은 `core/schemas/task-envelope.json` 형식의 JSON 으로 `.harness/runs/<id>/<run>/task-implementer.json` 에 쓴다(git 제외).
```
`adapters/codex/workflows/implement.md:3` 도 같은 문장이고, 투영본 `.claude/skills/implement/SKILL.md:15`·`.agents/skills/implement/SKILL.md:15` 에 그대로 들어가 있다.

그 1번이 따르라고 한 원본은 반대를 말한다:
- `core/workflows/implement/SKILL.md:27-29` 「계약은 손으로 쓰지 않는다 — 하네스가 계산한다. `romeo envelope build --unit <id> --role implementer --base-sha <승인 커밋 SHA> --run <run>` 로 만들고, 결과는 `docs/work/<id>/task/<run>-implementer.json` 이다」
- 같은 파일 :70 「**하지 않는 것** — 작업 계약을 손으로 쓰는 것」
- `adapters/orca/RUNBOOK.md:407` 「작업 계약 JSON 을 손으로 쓰는 것. 계약은 `bin/romeo envelope build` 만 만든다」

결과도 다르다. `.gitignore:2` 가 `.harness/runs/` 를 제외하고 `romeo/evidence.py:19 exclusions()` 가 `.harness` 를 `dirty_tree_hash`·`changed_files` 에서 빼므로, 지침 3번대로 만든 계약은 K-62 등록 대상이 되지 않는다. 반면 `romeo/envelope.py:145` 주석은 계약을 작업 단위 폴더 안에 두는 이유를 K-62 로 명시한다.

**제안된 수정:** `adapters/{claude,codex}/workflows/implement.md:3` 을 「작업 계약은 `bin/romeo envelope build --unit <id> --role implementer --base-sha <승인 커밋 SHA> --run <run-id>` 로 만든다. 손으로 쓰지 않는다. 결과는 `docs/work/<id>/task/<run-id>-implementer.json` 이다. 위임 실행이면 위임한 쪽이 이미 만들어 절대 경로로 넘겨준 것을 쓴다」로 고친다. 고친 뒤 `./bin/romeo compile && ./bin/romeo compile --check` 를 돌려 투영본 2개가 갱신되는지 확인한다.

## G02 [blocker] (실행가능성-재검사)
**대상:** `adapters/claude/workflows/review.md`

**요약:** 검토자 런타임이 실제로 로드하는 지침이 입력 계약 경로를 `.harness/runs/<id>/<run>/task-reviewer.json` 으로 지목하는데, 그 경로에 파일을 쓰는 코드·명령이 저장소에 없다. RUNBOOK §3.3·§3.4 는 `docs/work/<id>/task/<run-id>-reviewer.json` 을 넘긴다.

**증거:**

```
$ grep -rn "task-reviewer" --exclude-dir=.git .
adapters/claude/workflows/review.md:3
adapters/codex/workflows/review.md:3
.claude/skills/review/SKILL.md:15
.agents/skills/review/SKILL.md:15
```
→ 생산자 0건. 계약을 만드는 유일한 코드는 `romeo/envelope.py:148-150`:
```
tdir = find_unit_dir(project_root, unit_id) / "task"
path = tdir / (f"{run_name}-{role}.json" if run_name else f"{role}.json")
```
`$ ./bin/romeo envelope build --help` → `docs/work/<id>/task/[<run>-]<role>.json 을 만든다` (EXIT=0).
RUNBOOK §3.3:77·:81-82 와 §3.4:116 도 `<워크트리>/docs/work/<id>/task/<run-id>-<role>.json` 의 절대 경로를 `--spec` 으로 넘기라고 한다.

지시가 정면으로 어긋난다. 검토자 지침 1번은 `core/workflows/review/SKILL.md` 를 그대로 따르라고 하는데, 그 1번(:14-15)은 「`role: reviewer` 인 작업 계약을 받고 그 `base_sha` 가 구현자의 것과 같은지 본다. 다르면 ... `BLOCKED_CAPABILITY` 로 끝낸다」 이다. 지침 3번대로 `.harness/runs/.../task-reviewer.json` 을 찾으면 파일이 없고(그 디렉터리는 `.gitignore:2` 로 git 제외이며 `romeo evidence run` 만이 만든다), 검토는 시작조차 못 한다.

같은 문구가 컴파일 산출물에 그대로 투영돼 있고(`.claude/skills/review/SKILL.md:15` · `.agents/skills/review/SKILL.md:15`) `./bin/romeo compile --check` 는 PASS 다 — 투영이 충실하기 때문에 어떤 게이트도 이 모순을 잡지 못한다.

**제안된 수정:** `adapters/claude/workflows/review.md:3` 과 `adapters/codex/workflows/review.md:3` 의 경로를 `docs/work/<id>/task/<run-id>-reviewer.json`(위임 실행이면 위임한 쪽이 준 절대 경로)으로 고치고, 구현자 계약의 `base_sha` 를 어디서 읽는지도 같은 줄에 적는다(같은 디렉터리의 `<run-id>-implementer.json`). 고친 뒤 `./bin/romeo compile && ./bin/romeo compile --check` 로 투영본 두 개가 갱신되는지 확인한다. 재발 방지로는 `tests/test_doc_commands.py` 에 「어댑터 문서가 지목한 계약 경로가 `romeo/envelope.py` 가 쓰는 경로와 같다」 단언을 붙인다.

## G03 [blocker] (실행가능성-재검사)
**대상:** `adapters/orca/RUNBOOK.md`

**요약:** §3.1 이 커밋하라고 한 것은 spec.md 뿐인데, §3.5 가 그 커밋으로 만든 자식 워크트리 안에서 워커가 실행해야 하는 하네스(`bin/romeo` 의 envelope·--task-id, core/roles, core/schemas, .harness/romeo.project.yaml)가 그 커밋에 없다. N-1 단계가 N 단계에 필요한 상태를 만들지 않는다.

**증거:**

§3.1:58 「그 다음 **사람이** 승인된 `spec.md` 를 커밋한다」 · §3.5:131 `--base-branch <승인 커밋이 tip 인 브랜치>` · §3.5:140 「head 가 <base-sha> 와 같은지 확인한다. 다르면 계속하지 않는다」 → 자식 워크트리 트리는 그 커밋 그대로다.

그 커밋(=현재 HEAD d1891da)을 그대로 꺼내 워커가 지시받은 명령을 돌렸다:
```
$ git archive HEAD | tar -x -C $S            # EXIT=0
$ (cd $S && ./bin/romeo envelope build --unit x --role implementer)
romeo: error: argument cmd: invalid choice: 'envelope'
EXIT=2
$ (cd $S && ./bin/romeo evidence checks --unit x --task-id t --dispatch-id d)
romeo: error: unrecognized arguments: --task-id t --dispatch-id d
EXIT=2
$ (cd $S && ./bin/romeo evidence run --unit x --run r --task-id t -- true)
EXIT=2
$ ls $S/core/roles           → No such file or directory
$ ls $S/core/schemas         → fixture.json frontmatter.json proposal.json   (task-envelope.json 없음)
$ ls $S/.harness/romeo.project.yaml → No such file or directory
$ ls $S/core/workflows       → plan  plan-close                              (implement·review 없음)
```
이 세 명령은 RUNBOOK §2:39(`required_checks` → 워커 안에서 `bin/romeo evidence checks --unit <id> --run <run-id> --task-id <task-id> --dispatch-id <dispatch-id>`)·§5:298-300·`core/workflows/implement/SKILL.md`:28(`romeo envelope build ...`)·:57 이 워커에게 직접 지시한 것이다.

파급 두 가지가 더 있다.
(a) `romeo/policy.py:40 load_project_state` 는 **작업 트리**의 `.harness/romeo.project.yaml` 을 읽고 없으면 `None` 을 돌려준다(`:50-52` 주석 그대로). 자식 워크트리에 그 파일이 없으므로 라우터가 `superpowers: pending_gate` 를 돌려주고, `implement/SKILL.md:45` 「`status` 가 `active` 가 아닌 부품은 쓰지 않는다」에 걸려 :39-44 의 규율 부품 5종이 워커 안에서 전부 꺼진다.
(b) `romeo/envelope.py:111-112` 는 정책표를 `HARNESS_ROOT`(= 호출된 `bin/romeo` 의 체크아웃, `romeo/__init__.py:5`)에서, 부착 상태를 `project_root` 작업 트리에서 읽는다. 따라서 §3.3:99 「자식 워크트리 안에서 같은 명령을 다시 돌려도 같은 파일이 나온다」는 두 체크아웃의 하네스가 같을 때만 참이다.

RUNBOOK 은 이 문제를 **문서에 대해서만** 인지하고 있다 — §3.4:118 「자식 워크트리에는 커밋되지 않은 스킬 변경이 없을 수 있으므로 절차 문서의 절대 경로를 함께 넣는다」. 실행 가능한 하네스에 대해서는 같은 처리가 없다.

**제안된 수정:** §3.1 의 커밋 단계를 「승인된 spec.md **와, 워커가 실행할 하네스 상태**(`bin/romeo`·`romeo/`·`core/`·`.harness/romeo.project.yaml`)를 같은 커밋 또는 그 이전 커밋에 넣는다」로 고치고, 관찰 가능한 성공 신호를 §3.1 의 `git show <base-sha>:docs/work/<id>/spec.md` 옆에 추가한다 — 예: `git ls-tree <base-sha> core/roles core/schemas/task-envelope.json .harness/romeo.project.yaml` 가 3행을 내고, `git show <base-sha>:romeo/cli.py | grep -c task-id` 가 0 이 아닐 것. 그 다음 §3.5 의 기동 전 조건에 이 확인을 넣는다. 대안(더 약함)은 §2:39·§5·implement/SKILL.md 의 워커 명령을 상대 `bin/romeo` 대신 **위임한 쪽 체크아웃의 절대 경로**로 고정하는 것인데, 그 경우 `HARNESS_ROOT` 와 `--root` 가 서로 다른 체크아웃을 가리키게 되므로 §3.3 의 결정성 문장도 함께 정정해야 한다.

## G04 [blocker] (실행가능성-재검사)
**대상:** `adapters/orca/RUNBOOK.md`

**요약:** §3.7 이 검토자를 `worker-start --agent` 로 띄우는데, 그 명령에는 §4 가 정본이라고 선언한 강제 수단(`codex exec -s read-only`)을 넣을 자리가 없다. §3 을 그대로 따르면 검토자는 아무 샌드박스 없이 기동되고, §4 표의 「실행으로 관찰했나: 예」는 §3 이 실제로 실행하는 형태에 대한 관찰이 아니다.

**증거:**

§3.7:160-167 이 지시하는 기동 명령:
```
orca orchestration worker-start --run <run-id> --task <reviewer-task-id> \
  --worktree path:<구현자 워크트리 절대경로> --agent <bindings.roles.reviewer.runtime> \
  --timeout-ms 1800000 --json
```
실측 도움말에 샌드박스·인자 전달 플래그가 없다:
```
$ orca orchestration worker-start --help
Usage: orca orchestration worker-start --task <task_id> [--on <saved-environment>] [--worktree ...] (--agent <agent> | --terminal <handle>) [--model <id>] [--effort <level>] [--name] [--repo] [--base-branch] [--display-name] [--comment] [--setup] [--retry-of] [--timeout-ms] [--run] [--from] [--retry-request] [--json]
  --agent <id>   Launch a known TUI agent in the first terminal
```
→ `-s/--sandbox`·`--output-schema`·`-o`·passthrough(`--`) 없음. 즉 §4:220-227 의
```
codex exec -s read-only -C <검토 대상 워크트리 절대경로> --output-schema ... -o ... "$(cat "$T")"
```
형태는 §3.7 의 기동 경로로는 만들어지지 않는다.

§4:208-211 표는 그 형태를 「기본 · 검토자 · `roles.reviewer.enforcement` · `codex exec -s read-only` · 실행으로 관찰했나 **예**」로 인쇄하고, `.harness/bindings.yaml:33-35` 도 `enforcement_observed: true` 다. 그 관찰(:36-38)은 `codex exec` 단독 프로브였지 `worker-start` 로 기동한 워커에 대한 것이 아니다.

두 경로를 잇는 수단은 존재하지만 RUNBOOK 어디에도 없다:
```
$ orca terminal create --help
Usage: orca terminal create [--worktree <selector>] [--title <name>] [--command <text>] [--focus] [--json]
  --command <text>  Command to run in the terminal on startup
$ orca orchestration worker-start --help   →  --terminal <handle>  Runtime-issued terminal handle
```
`grep -n "terminal create\|--terminal" adapters/orca/RUNBOOK.md` → 히트 0건.

**제안된 수정:** §3.7 을 두 단계로 나눈다 — (1) `orca terminal create --worktree path:<구현자 워크트리> --command "codex exec -s read-only -C <구현자 워크트리> --output-schema <저장소>/core/schemas/result-envelope.json -o <위임한 쪽이 지정한 파일> \"$(cat \"$T\")\"" --json` 으로 강제 수단이 걸린 터미널 핸들을 만들고, (2) `worker-start --terminal <handle>` 로 그 터미널을 워커로 채택한다. 이 두 명령의 실제 반환 JSON 은 아직 관측하지 않았으므로 §11 에 「`terminal create --command` → `worker-start --terminal` 경로 미관측」으로 남긴다. 이 배관을 M3 로 미룰 거라면 §4 표의 「기본 · 검토자」 행 마지막 칸을 **아니오**로 내리고, §11 에 「§3.7 의 기동 경로에는 검토자 read-only 강제가 걸리지 않는다 — 지금 §4 의 방어 검사가 유일한 방어다」를 명시해야 K-51 에 맞다.

## G05 [blocker] (증거정직성-재검사)
**대상:** `romeo/close.py`

**요약:** close 는 검토자 판정이 '읽히지 않을 때'만 거부한다 — 아무 근거에도 매여 있지 않은 손으로 쓴 PASS 봉투는 그대로 done 을 만든다. 존재하지 않는 작업 계약(sha256 전부 0), 존재하지 않는 evidence_ref, 그리고 검토자 역할 계약이 금지한 checks 를 실은 봉투로 close 가 PASS 를 냈다.

**증거:**

`docs/work/<id>/review/` 에 파일을 쓰는 코드는 저장소에 없다(`grep -rn '/review/\|/result/' romeo/*.py` → 히트 0). 즉 검토자 봉투의 유일한 생성 경로는 에이전트가 JSON 을 손으로 쓰는 것이다.

격리 재현(tmp git repo, 저장소 무변경 — /private/tmp/.../scratchpad/probe_close.py):
```
task/ 존재: False
evidence_ref 가 가리키는 파일 존재: False
result/ 존재: False
close verdict = PASS
   HAS_REVIEW True 
   REVIEW_ENVELOPE_VALID True 
   REVIEW_VERDICT True run-test-reviewer.json: PASS
EXIT=0
```
쓴 봉투: `task_envelope_ref={'path':'docs/work/<id>/task/reviewer.json','sha256':'0'*64}`(그 파일 없음) · `evidence_ref='docs/work/없는단위/evidence/없는파일.yaml'` · `checks=[{'id':'check-1','command':'true','exit_code':0}]`.

같은 봉투를 parity 는 판정 불가로 떨어뜨린다 — 두 검사기가 '유효한 검토자 봉투'를 다르게 본다:
```
$ python3 -c "from romeo.parity import _envelope_defects, load_role_contracts; ..."
parity 판정: [('ROLE_CONTRACT_VIOLATION', "ROLE_CONTRACT_VIOLATION baseline.reviewer checks 1건 — 역할 계약의 capabilities ['read', 'search'] 에 run-command 가 없다")]
```
done 을 선언하는 쪽이 느슨한 쪽이다. 게다가 `tests/test_docs_evidence_close.py:248` 의 `_envelope` 헬퍼가 바로 이 형태(`sha256: "0"*64` + reviewer 의 checks)를 표준 케이스로 박아 두고 `test_reviewer_pass_closes` 가 close PASS 를 단언하므로, 테스트가 느슨한 계약을 고정한다.
또한 `romeo/close.py:79-118` 은 구현자 결과 계약(`docs/work/<id>/result/`)을 아예 보지 않는다(`grep -rn '/result/' romeo/` → 0건).

**제안된 수정:** `_check_review` 에 앵커 검사 3개를 추가한다. (1) `task_envelope_ref.path` 가 실제로 존재하고 `sha256` 이 그 파일의 해시와 같아야 한다 — `romeo/envelope.py` 가 이미 `docs/work/<id>/task/<role>.json` 에 쓰므로 대조 대상이 있다. (2) 그 작업 계약의 `base_sha` 가 현재 HEAD 와 같아야 한다(evidence 의 FRESH_HEAD 와 같은 이유 — 다른 리비전에서 낸 PASS 는 이 리비전의 검토가 아니다). (3) `evidence_ref` 가 실재하는 파일을 가리켜야 한다. 그리고 `romeo/parity.py:185-214` 의 `_envelope_defects` 를 close 에서도 재사용해 `ROLE_CONTRACT_VIOLATION`·`EVIDENCE_MISSING` 을 같은 기준으로 적용한다 — 규칙을 두 벌 쓰지 않는다. `tests/test_docs_evidence_close.py:248` 의 `_envelope` 는 실제 `envelope build` 산출물을 읽어 sha256 을 채우도록 고치고, 검토자 봉투의 `checks` 는 `[]` 로 바꾼다(현재 값은 역할 계약 위반이다). 여기에 F28 대로 `result/` 의 구현자 봉투 검증도 같이 넣는다.

## G06 [important] (증거정직성-재검사)
**대상:** `.github/workflows/harness.yml`

**요약:** CI 의 동등성 게이트 스텝이 `|| echo` 로 끝나 어떤 판정이 나와도 초록불이다. 지금 의도한 것은 '미판정(관측 0건)' 을 넘기는 것이지만, 같은 코드가 실제 교차 실행에서 나온 **게이트 FAIL** 도 똑같이 삼킨다 — 관측이 생긴 뒤 가장 중요한 신호가 경고 주석 한 줄로 사라진다.

**증거:**

`.github/workflows/harness.yml:93-96`:
```yaml
      - name: 동등성 게이트 판정 (관측 필요 — 지금은 인쇄)
        run: |
          bin/romeo fixtures parity --report \
            || echo "::warning::핵심 동등성 게이트가 PASS 가 아니다(관측 0건이면 미판정). 관측 케이스가 생기면 이 스텝을 강제로 바꾼다."
```
`romeo/cli.py:126` 은 `return 0 if rep["verdict"] == "PASS" else 1` — 미판정과 FAIL 이 같은 종료 코드 1 이므로 셸 수준에서 둘을 구분할 수 없다. 즉 '지금은 인쇄' 상태를 유지하는 방법이 'FAIL 도 인쇄' 밖에 없다.
실측으로 두 상태가 모두 exit 1 인 것을 확인했다 — 저장소 케이스는 `핵심 동등성 게이트: 미판정 … EXIT=1`, 관측 케이스를 넣은 디렉터리는 `EXIT=0`, 관측 불일치를 만들면 같은 exit 1 이다(`tests/test_parity.py:352 test_observed_divergence_fails_the_gate` 가 그 분기를 덮는다).

**제안된 수정:** 종료 코드를 세 값으로 나눈다 — PASS 0 · FAIL 1 · UNDETERMINED 2 — 하고 CI 스텝을 `bin/romeo fixtures parity --report; rc=$?; [ $rc -le 2 ] && [ $rc -ne 1 ]` 형태로 쓰거나, 더 단순하게 `--json` 을 받아 `gate_verdict == "FAIL"` 일 때만 실패시킨다. 어느 쪽이든 '관측이 생기면 사람이 이 줄을 지운다' 는 약속에 의존하지 않는다.

## G07 [important] (실행가능성-재검사)
**대상:** `adapters/claude/workflows/review.md`

**요약:** 검토자 런타임 지침 6번이 검토자 자신에게 실행 전후 `git status --porcelain` 비교를 시킨다. core 절차는 그 검사를 검토자가 하지 않는다고 못박고, 역할 계약에는 명령 실행 능력이 없다.

**증거:**

```
$ sed -n '6p' adapters/claude/workflows/review.md
6. 실행 전후 `git status --porcelain` 출력이 같아야 한다. 다르면 강제가 듣지 않은 것이므로 판정을 무효로 보고한다.
$ sed -n '6p' adapters/codex/workflows/review.md      → 동일 문장
```
반대 지시:
- `core/workflows/review/SKILL.md:33-35` 「검토자를 띄운 쪽이 검토 전후의 작업 트리 상태를 증거 기록 명령으로 남기고 비교한다. ... **이 검사는 검토자가 하지 않는다** — 검토자는 명령을 실행하지 않고, 자기가 만든 산출물로 자기 판정의 유효성을 증명할 수도 없다.」
- 같은 파일 :17 「아무것도 쓰지 않고 **검사·빌드 같은 명령을 실행하지 않는다**」
- `core/roles/reviewer.yaml:12` `capabilities: [read, search]` — `run-command` 없음. `romeo/parity.py:48 RUN_CAPABILITY = "run-command"` 가 이 값을 정본으로 읽는다.
- `adapters/orca/RUNBOOK.md:245-260` 은 이 검사를 위임한 쪽이 `bin/romeo evidence run --label review-tree-before/after` 로 돌리게 하고, :246-247 에서 셸 리다이렉션 산출물을 K-51·K-62 위반으로 금지한다.

부수로 `adapters/claude/workflows/review.md:2` 의 「Read·Grep·Glob 과 **읽기 전용 셸**만 쓴다」도 `review/SKILL.md:17` 의 「명령을 실행하지 않는다」와 어긋난다.

**제안된 수정:** `adapters/{claude,codex}/workflows/review.md:6` 을 「방어 검사(실행 전후 작업 트리 비교)는 이 절차를 부른 쪽이 증거 기록 명령으로 돌린다. 검토자는 명령을 실행하지 않는다」로 고치고, claude 쪽 2번의 「읽기 전용 셸」 문구를 지운다. 고친 뒤 `./bin/romeo compile && ./bin/romeo compile --check` 로 `.claude/skills/review/SKILL.md`·`.agents/skills/review/SKILL.md` 투영본이 갱신되는지 확인한다.

## G08 [important] (실행가능성-재검사)
**대상:** `romeo/cli.py`

**요약:** `bin/romeo evidence checks` 는 spec 에 `required_checks` 블록이 없으면 파이썬 트레이스백(UnboundLocalError)으로 죽는다. RUNBOOK §2·§5 와 implement/SKILL.md 7 번이 워커에게 조건 없이 지시하는 명령인데, 실패 신호가 「무엇이 없다」가 아니라 스택 트레이스다.

**증거:**

`romeo/cli.py:167-175` 의 `checks` 분기는 루프 변수 `res` 를 루프 밖(:174)에서 쓴다 — `run_required_checks` 가 빈 리스트를 돌려주면 `res` 가 바인딩되지 않는다. `UnboundLocalError` 는 `main()` 의 `except (ValueError, FileNotFoundError, RuntimeError)`(:431)에 걸리지 않는다.

격리 재현(scratchpad 임시 저장소, 이 저장소 무변경):
```
$ ./bin/romeo evidence checks --unit chg-20260828-noreqchecks-ab12 --root $S
Traceback (most recent call last):
  File ".../romeo/cli.py", line 174, in cmd_evidence
    print(f"  → {res['evidence']}  head {res['state']['head_sha'][:12]} ...")
UnboundLocalError: local variable 'res' referenced before assignment
EXIT=1
```
도달 가능성 확인: `romeo/close.py:20-25 required_checks(body)` 는 `` ```yaml ... required_checks: ... ``` `` 블록이 없으면 `[]` 를 돌려준다(`빈 body 의 required_checks = []` 실측). `grep -rn "required_checks" romeo/validate.py core/schemas/frontmatter.json` → 히트 0건 — 블록이 있어야 한다고 강제하는 검사가 없다. 즉 T0 처럼 검사 계획이 비어 있는 spec 이면 워커의 첫 검사 명령이 트레이스백으로 끝난다.

**제안된 수정:** `romeo/cli.py:167-175` 를 결과 리스트로 받아 분기한다 — `results = list(run_required_checks(...))` 로 받고, 비었으면 `print("required_checks 가 spec.md 에 없다 — 검사할 것이 없다. 검증 계획의 required_checks 블록을 채운다")` 후 종료 코드 2(또는 1)로 끝낸다. 회귀 테스트는 required_checks 블록이 없는 spec 에서 `cmd_evidence` 가 트레이스백 대신 메시지와 비0 종료 코드를 내는지 단언한다. 배정 밖 파일이므로 고치지 않았다.

## G09 [important] (증거정직성-재검사)
**대상:** `romeo/doctor.py`

**요약:** doctor 가 12개 스킬 전부에 대해 '런타임 로드 관찰됨' 을 인쇄한다. 실제 관찰은 10개 시점이고 새 스킬 implement·review 2종은 어느 codex 세션에서도 목록에 뜨는 것을 본 적이 없다. 1차 리뷰 F10 이 지적한 코드 경로가 그대로다 — 정직한 문장을 관찰 텍스트 안에 넣었을 뿐, 헤더의 판정 토큰은 여전히 '관찰됨' 이다.

**증거:**

```
$ ./bin/romeo doctor   (EXIT=0)
  codex   12개 · .agents/skills · 런타임 로드 관찰됨 (2026-08-28 … 그 시점 .agents/skills/ 의 10개가 전부 나타났다 … **이후 implement · review 가 투영되어 지금은 12개다. 새 스킬 2종이 이 런타임의 목록에 나타나는지는 아직 관찰하지 않았다(2026-08-28 기준 미관찰).**)
결과 · 저장소: PASS · 이 머신의 런타임: PASS
```
`romeo/doctor.py:230`: `mark = "관찰됨" if seen else "**미관찰**"` — 관찰 텍스트의 존재만 본다. 이름 대조도 개수 대조도 없다. 대조에 필요한 값은 이미 계산돼 있다(`probe_skill_files` 가 `s["skills"]` 로 이름 목록을 돌려준다, doctor.py:75-77). `.harness/observations.yaml:24-33` 의 `runtime_load.codex` 는 여전히 자유 문자열이다(F10 이 제안한 `{observed_at, skills: [...]}` 구조 미적용).
대조: claude 쪽 주장(11개 전부 확인)은 재현된다 — `ls .claude/skills/` 11개 이름이 이 세션의 스킬 목록과 일치한다. 즉 정직하지 않은 것은 기록이 아니라 doctor 의 인쇄 방식이다.
`docs/planning/progress.md:77` 이 이 사실을 스스로 적어 두었다("1차 리뷰 F10 의 코드 수정은 미반영") — 즉 알면서 남긴 자리다.

**제안된 수정:** `.harness/observations.yaml` 의 `runtime_load.<runtime>` 을 `{observed_at, skills: [이름…], note}` 로 바꾸고, `format_report` 가 `set(probe.skills) - set(observed.skills)` 를 계산해 차집합이 있으면 `부분 관찰 (implement·review 미관찰)` 로 인쇄한다. 차집합이 있는 동안 '관찰됨' 이라는 단어를 쓰지 않는다. 구조를 바꾸면 `tests/test_doctor.py:54` 의 `test_report_says_runtime_load_is_unproven` 옆에 '개수는 같고 이름이 다르면 부분 관찰로 인쇄한다' 케이스를 붙일 수 있다.

## G10 [important] (증거정직성-재검사)
**대상:** `romeo/parity.py`

**요약:** 게이트를 여는 조건이 손으로 고칠 수 있는 한 단어다. `source.kind: authored` 를 `observed` 로 바꾸고 아무 문자열이나 `ref` 에 넣으면 '핵심 동등성 게이트: PASS · EXIT=0' 이 나온다 — 실제 교차 실행은 한 번도 없어도 된다. D-b 가 옮긴 신뢰 경계가 검사되지 않는 자기 신고 필드 위에 있다.

**증거:**

`romeo/parity.py:105-108` 은 observed 케이스에 대해 `ref` 가 '비어 있지 않은 문자열'인지만 본다. 경로 실재도, 봉투의 `evidence_ref` 실재도 검사하지 않는다.

실측(저장소 fixture 를 scratchpad 로 복사해 `kind: authored` → `observed` 한 줄만 바꾸고 ref 를 실존하지 않는 경로로 둠):
```
$ ./bin/romeo fixtures parity /…/scratchpad/parityfake2 --report
parity 리포트 · 1건 · 관측 1건 · 합성 0건 · 검사기 자기 검증 PASS · 동일 1 · 불일치 0
| pr-fake-observed | feat-20260828-license-field-a1b2 | implementer, reviewer | observed | same | ✓ | 스키마 유효·required_checks 동일·gate 판정 동일 |
핵심 동등성 게이트: PASS — 관측 1건으로 판정했다.
EXIT=0
```
그 케이스의 source 는 `kind: observed` / `ref: 실행한적없음/아무문자열.md` 다.
덧붙여 저장소의 모든 parity 봉투가 가리키는 evidence 경로는 실재하지 않는다 — `feat-20260828-license-field-a1b2` · `chg-20260828-brief-render-7k2q` 는 `ls docs/work/` 에 없다(존재하는 단위는 chg-20260827 2건뿐). 합성 케이스로서는 정상이지만, 같은 파일을 observed 로 바꾸는 순간 아무 검사도 그것을 막지 못한다.

**제안된 수정:** `_source_errors` 의 observed 분기를 실재 검사로 바꾼다: `source.ref` 가 저장소 안의 실재 경로여야 하고(문장 주석은 `note:` 로 분리), 그 케이스 양면의 모든 `evidence_ref` 가 실재하는 `docs/work/<unit>/evidence/*.yaml` 을 가리켜야 하며, `unit_id` 가 `docs/work/` 에 실재하는 작업 단위여야 한다. 셋 중 하나라도 어긋나면 `PARITY_INVALID` 로 exit 1 — 관측이라고 선언했는데 관측물이 없으면 그것은 구조 오류다. `tests/test_parity.py` 에 '경로가 없는 observed 케이스는 게이트를 열지 못한다' 케이스를 넣는다.

## G11 [minor] (증거정직성-재검사)
**대상:** `docs/planning/progress.md`

**요약:** 체크리스트 25행이 관찰되지 않은 강제 수단을 관찰된 것처럼 단정한다 — `.claude/agents/reviewer.md` 의 `tools: Read, Grep, Glob` frontmatter 를 '이 런타임의 강제 수단' 이라고 쓰지만, 프로브 7건은 전부 CLI 기동 플래그를 시험했고 에이전트 파일 frontmatter 는 한 번도 시험하지 않았다.

**증거:**

`docs/planning/progress.md:54`: "`.claude/agents/{implementer,reviewer}.md` 생성(`reviewer` 의 `tools: Read, Grep, Glob` 이 이 런타임의 강제 수단)".
실제 관찰된 수단은 다른 것이다 — `.harness/bindings.yaml:61` `parity_swap.reviewer.enforcement: 'claude -p --tools … --allowedTools … --strict-mcp-config'`, `docs/reviews/2026-08-28-m2-round1-review/PROBE_READONLY.md` 프로브 표 7건(A·B1·B2·C·C2·D·E)은 전부 `codex exec` / `claude -p` 기동 플래그다. 에이전트 파일 frontmatter 로 서브에이전트를 띄워 쓰기가 막히는지는 프로브에도 `.harness/observations.yaml` 에도 없다.
컴파일 산출물은 오히려 정확하다 — `.claude/agents/reviewer.md` 의 managed block 은 강제 수단으로 CLI 3플래그를 적고 `강제 관측: 관측됨` 을 붙이며, `CLAUDE.md:87-92` 역할표는 `강제 관측` 열에 `미관측`/`관측됨` 을 나눠 인쇄한다. 진행 문서만 두 메커니즘을 하나로 합쳤다.
(나머지 근거는 재현됐다 — 20행의 부착 배선 주장을 직접 실행해 대조했다: `./bin/romeo route --classification <T1> --root <저장소> --json` → `parts: [('superpowers','active')] · warnings: []`, `--root <빈 디렉터리>` → `parts: [('superpowers','pending_gate')] · warnings: ['PART_PENDING_GATE']`. 19행의 프로브 로그 12개 파일도 실재한다.)

**제안된 수정:** 25행 괄호를 `(강제 수단은 기동 플래그다 — 에이전트 파일의 tools frontmatter 가 서브에이전트 실행에서 쓰기를 막는지는 미관측)` 로 고치고, 그 미관측 항목을 `## 미검증·남은 위험` 절에 한 줄로 올린다.

## G12 [minor] (증거정직성-재검사)
**대상:** `romeo/parity.py`

**요약:** 검사기 자기 검증 줄이 케이스 0건에서도 PASS 를 인쇄한다. 관측 케이스만 있는 디렉터리에서 '검사기 자기 검증: PASS — 합성 0건이 선언한 대로 판정되는지만 본다' 가 나온다 — 0건을 근거로 PASS 라고 말하는 문장이다.

**증거:**

위 parityfake2 실행 출력:
```
검사기 자기 검증: PASS — 합성 0건이 선언한 대로 판정되는지만 본다. 이것은 게이트를 통과시키지 못한다.
```
원인은 계산과 문장이 다른 집합을 가리키기 때문이다 — `romeo/parity.py:288` 의 `checker = "PASS" if executed and matched == len(executed)` 는 **실행된 전체**(관측 포함)로 계산하는데, `format_parity:333-334` 는 그 값을 `rep['synthetic']` 건수로 설명한다.

**제안된 수정:** `checker_verdict` 를 합성 케이스만으로 계산하도록 바꾸고(`synthetic` 집합에 대해 `matched`), 합성 0건이면 `해당 없음` 으로 인쇄한다. 계산 대상과 설명 문장이 같은 집합을 가리켜야 한다.

## G13 [minor] (증거정직성-재검사)
**대상:** `tests/test_doctor.py`

**요약:** 테스트 이름이 하지 않은 관찰을 주장한다. `test_new_workflows_are_discoverable_in_both_runtimes` 는 두 런타임의 discovery 를 확인하지 않고 디스크의 SKILL.md frontmatter 만 읽는다 — codex 쪽 discovery 는 이 저장소에서 아직 관찰된 적이 없는데도 CI 로그에는 이 이름이 ok 로 찍힌다.

**증거:**

`tests/test_doctor.py:75-84` 본문은 `probe_skill_files(REPO)` 결과에서 이름을 찾을 뿐이고, `probe_skill_files` 의 docstring 자체가 `romeo/doctor.py:51` 에서 "두 런타임의 스킬 디렉터리를 파일 수준으로 검사한다. **로드 여부는 알 수 없다**" 라고 못박는다. 테스트 안의 주석은 이 차이를 알고 있다("파일이 투영됐다는 것과 discovery 가 켤 근거를 갖는다는 것은 다르다") — 어긋난 것은 이름뿐이다.
doctor 의 스킬 절 헤더도 같은 말을 한다: "## 스킬 파일 (파일 수준. 실제 로드는 이 검사로 증명되지 않는다)".

**제안된 수정:** 이름을 `test_new_workflows_have_loadable_frontmatter_in_both_skill_dirs` 처럼 이 테스트가 실제로 보는 것으로 바꾼다. discovery 라는 단어는 `.harness/observations.yaml` 이 소유하게 두고, 테스트 이름에 쓰지 않는다.
