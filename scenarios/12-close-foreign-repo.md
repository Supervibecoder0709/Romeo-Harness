# 시나리오 12 — 남의 저장소의 단위를 구현·검토·close 한다

시나리오 10 이 하네스를 **자기 저장소가 아닌 저장소**에 붙였고, 시나리오 11 이 그 저장소에서 라우터가 **분류**하는 것까지
참으로 만들었다. 이 런북은 그 다음 줄을 고정한다 — 붙인 하네스가 그 저장소의 일을 **판정**하는가.

「부착했다」·「분류했다」·「판정했다」는 서로 다른 세 주장이고, 시나리오 11 까지가 참으로 만든 것은 앞의 둘뿐이다.
판정은 구현자가 쓰고 검토자가 읽고 `close` 가 닫아야 성립하며, 그 세 자리가 남의 루트에서 도는지는 돌려 봐야 안다.

대상은 시나리오 10·11 과 같은 `My-Automated-Worker/instagram-dm-sender` 이고, 단위는 시나리오 11 이 그 저장소에
세운 `feat-20260904-claude-md-rule-conflicts-bbn8` 이다.

여기 적힌 것은 전부 2026-09-06 관통의 실측이다. 실측하지 않은 것은 적지 않는다(K-51) —
막힌 경로도 그대로 남긴다. 막힌 경로를 지우면 이 문서를 읽는 사람이 같은 곳에서 다시 막힌다.
원자료는 `docs/work/feat-20260906-m3-close-foreign-repo-ik3u/observations.md` 다.

## 무엇이 더 필요한가

시나리오 11 이 끝난 시점에 대상 저장소의 `docs/work/<id>/` 에는 `brief.md`·`spec.md` 둘뿐이었다.
그 상태에서 `close` 를 부르면 어디까지 가는지가 이 절의 출발점이다.

```
bin/romeo close --unit feat-20260904-claude-md-rule-conflicts-bbn8 --root <대상> --dry-run
```

rc=1 · `FRONTMATTER_VALID` PASS · `APPROVED` PASS · **`HAS_EVIDENCE` FAIL 에서 멈춘다.**
**남의 루트에서도 close 기계는 그대로 돈다** — 막힌 것은 `--root` 가 아니라 그 저장소에 증거가 없다는 사실이다.

그 뒤로 close 가 **추가로 요구한 것**은 넷이고, 전부 그것을 인쇄한 명령과 종료 코드로 확인했다.

| # | 무엇이 더 필요했나 | 요구를 인쇄한 명령 | rc |
| --- | --- | --- | --- |
| 1 | **승인된 spec 의 커밋.** `docs/work/<id>/` 가 미추적이면 `CHECK_PLAN_COMMITTED`·`TASK_ANCHORED` 가 대조할 원본이 이력에 없다 | `git -C <대상> add docs/work/<id>/ && git -C <대상> commit` → `33a1c14` | 0 |
| 2 | **작업 계약 2종**(구현자·검토자). `docs/work/<id>/task/` 는 `envelope build` 만 만든다 — 손으로 쓰지 않는다 | `bin/romeo envelope build --unit <id> --role implementer --base-sha 33a1c14 --run <run> --root <대상>` (검토자도 같은 형태) | 0 |
| 3 | **구현자 결과 계약.** `result/<run>-implementer.json` 은 구현한 쪽이 스스로 쓴다 — 회수해 주는 쪽이 없다(K-62) | `bin/romeo envelope check --unit <id> --role implementer --root <대상> <절대경로>` | 0 |
| 4 | **검토자 절차 파일과 그 출력.** 대상에 `core/workflows/review/SKILL.md` 와 `core/roles/reviewer.yaml` 이 부착돼 있어야 검토자가 자기 루트에서 절차를 찾는다 | `bin/romeo review record --unit <id> --run <run> --root <대상>` | 0 |

**`bin/`·`romeo/` 는 끝까지 필요하지 않았다.** 모든 명령을 하네스 저장소의 `bin/romeo` 를 `--root <대상>` 으로 불러 돌렸다.
정책표·역할 계약·스키마는 `HARNESS_ROOT`(돌고 있는 `romeo` 패키지의 저장소)에서 읽고, 부착 상태와 문서는 `--root` 에서 읽는다.
시나리오 10 의 「놓는 것」이 그 둘을 제외한 판단(Q-54)은 이 관통에서 **뒤집히지 않았다** — 그 질문은 그대로 열려 있다.

**순서에 조건이 하나 붙는다 — 구현 커밋은 증거보다 먼저다.** 증거는 기록 시점의 `head_sha` 를 담고 `close` 의 `FRESH_HEAD` 가
그것을 현재 HEAD 와 대조하므로, 증거를 남긴 뒤에 커밋하면 그 자리에서 실패한다. 실측 순서는
구현 → `git commit`(`c3b9eae`) → `evidence checks` 였다.

## 어디서 구현하는가

실행 위치와 권한은 시나리오 11 의 「어디서 실행하는가」와 같다 — 대상 디렉터리에서 비대화형 실행을 띄우고
`--allowedTools 'Bash(<하네스>/bin/romeo:*)'` 로 실행 권한을 연다. 이 런북이 더하는 것은 **쓰는 자리**다.

이 관통에서 대상 저장소에 **쓴 것은 둘뿐**이고, 그것이 그 단위 작업 계약의 `allowed_paths` 다.

```
allowed_paths = ['docs/work/feat-20260904-claude-md-rule-conflicts-bbn8/', 'CLAUDE.md']
```

`CLAUDE.md` 는 **마커 밖**에만 쓴다. 마커 안(`romeo:managed start` ~ `end`)은 `romeo compile` 의 산출물이라
고치면 다음 컴파일에서 사라지고, 고쳤는지는 `compile --check` 가 재생성 대조로 판정한다.
이 관통은 마커 시작 줄 **앞**에 「## 규칙 충돌 해소」 절 60줄을 넣었다(381줄 → 441줄 · 절은 108행, 마커는 168행).

**여기서 이 관통이 저지른 범위 이탈 1건을 지우지 않고 적는다.** 구현 커밋 `c3b9eae` 는 `git add CLAUDE.md` 로
파일 전체를 담아 이 단위의 60줄과 함께 **부착이 넣은 managed block 275줄도 커밋했다**(`git diff --stat 33a1c14 c3b9eae`
= 335 insertions). 대상 단위 spec 의 비범위는 「대상 저장소의 부착분을 커밋하는 것」이므로 이것은 이탈이다.
사용자가 「이력을 다시 쓰지 않고 증거로 닫는다」로 확정했다(2026-09-06).

**이 이탈의 뿌리는 부착이 미커밋이라는 것이고, 그것이 이 관통이 M5 `attach` 에 넘기는 가장 무거운 요구사항이다.**
부착이 미커밋이면 `git status` 가 100여 개를 내고 증거의 `changed_files` 가 그것을 그대로 싣는다 —
`HAS_CHANGE` 는 통과하지만 **이 단위가 무엇을 바꿨는지 그 목록으로는 갈리지 않는다.**
이 관통은 그것을 이력 없이 우회했다: 부착 소스 트리 여섯은 하네스 체크아웃과 `filecmp` 재귀 대조하고,
컴파일·notices 산출물 여덟은 `compile --check`·`notices --check` 가 **지금 다시 만들어** 바이트 비교한다.
스냅숏이 필요 없는 대조이고, 대상의 `core/policy/classification.yaml` 에 주석 한 줄을 더하자 판정이
`FAIL — 부착 소스 트리가 하네스와 다르다: core` 로 뒤집혔다(원복 뒤 다시 PASS).

## 검토자를 어떻게 붙이는가

역할 계약은 하네스와 같다 — 검토자는 읽기만 하고(`core/roles/reviewer.yaml`), 대상 저장소에 그 파일이 부착돼 있어
검토자가 자기 루트에서 절차를 찾는다. 강제는 런타임 인자로 건다.

**기동 명령에서 두 플래그를 뺀다.** 셋을 순서대로 실측했다.

| 시도 | 형태 | 결과 |
| --- | --- | --- |
| 1 | `codex exec -s read-only -C <대상> -m sol …` | **HTTP 400** — `The 'sol' model is not supported when using Codex with a ChatGPT account` |
| 2 | `-m sol` 만 빼고 `--output-schema <하네스>/core/schemas/result-envelope.json` 유지 | **HTTP 400** — `invalid_json_schema` · `anyOf` 하위 스키마에 `type` 이 없다 |
| 3 | 두 플래그를 다 빼고 `-c model_reasoning_effort=xhigh -o <계약 밖 임시 파일>` | **rc=0** — 검토자가 돌았다 |

2 번은 `adapters/orca/RUNBOOK.md` §2:42-49 가 2026-08-29 에 이미 실측해 적어 둔 실패다. 그런데
**`run-unit` 이 인쇄하는 검토자 기동 명령에 그 플래그가 들어 있다** — 요구하는 자리와 인쇄하는 자리가 갈린
§11 의 모양이고, 그대로 실행하면 400 으로 끝난다. 이 관통에서 고치지 않았다(§12 · Q-63).

**검토자가 트리를 바꾸지 않았다는 것은 방어 검사가 말한다.** 기동 전후로 같은 명령을 증거에 남기고
`log_sha256` 이 같은 것을 확인한다(라벨 `review-tree-before` · `review-tree-after`).

```
bin/romeo evidence run --unit <id> --run <run> --root <대상> --label review-tree-before -- <트리 인쇄 명령>
<검토자 기동>
bin/romeo evidence run --unit <id> --run <run> --root <대상> --label review-tree-after  -- <같은 명령>
bin/romeo review record --unit <id> --run <run> --root <대상>
```

`review record` 가 검토자 봉투의 sha256 을 같은 run 의 증거에 봉인한다 — 봉투를 나중에 고치면 그 봉인이 어긋난다.

**검토자 FAIL 은 증거만으로 답할 수 있어도 산출물을 다시 통과시키지 못한다.** 이 관통의 회차는
`fail · fail · pass · pass` 였고, 1·2회차 FAIL 은 **전부 증거에 대한 지적**이라 `CLAUDE.md` 는 한 글자도 바뀌지 않았다.
그런데 `close` 는 판정을 **산출물만의 함수**로 본다(`romeo/close.py:660` · D-73 — 산출물은 증거의
`head_sha`+`dirty_tree_hash` 로 식별한다). 그래서 3회차가 그 지적에 정확히 답해 PASS 를 받아도 옛 FAIL 두 건이
「같은 산출물의 판정」으로 남아 `REVIEW_VERDICT` 를 막았다. 하네스가 인정하는 우회는 둘뿐이다 —
산출물을 바꾸거나(해시가 움직여 옛 판정이 `REVIEW_SUPERSEDED` 가 된다), **재승인하거나**.
앞의 것은 판정을 지우려고 산출물을 건드리는 것이라 쓰지 않는다. 이 관통은 뒤의 것을 썼고,
**재승인할 정당한 사유가 실제로 있었다** — 1회차 검토자가 증명한 것이 AC-5 자체의 결함이었기 때문이다(D-80).
그 사유가 없었으면 이 자리는 막힌 채로 남는다. 고치지 않고 열어 둔다(§12 · Q-64).

## 검증

이 관통의 완료는 **대상 저장소의 상태**로 판정한다. 아래 표가 그 조건이고, 판정하는 것은
`tests/test_foreign_close.py` 다. 표의 문장이 아니라 **조건 id** 가 검사와 문서를 잇는다.

**목록의 문법.** 이 절의 표에서 첫 칸이 백틱 조건 id(소문자·숫자·하이픈) 하나뿐인 줄만 완료 조건으로 읽는다.
`tests/test_foreign_close.py` 의 `conditions()` 가 이 파일을 읽어 그 목록을 만들고, `check(root)` 가 주어진 루트와 대조한다.
**이 목록을 고치면 검사가 대조하는 것이 함께 바뀐다** — 한 줄을 지우면 그 조건은 조용히 건너뛰어지는 것이 아니라
요구에서 사라지고, 판정 코드가 없는 id 를 더하면 **그 자리에서 막힌다**. 검사가 매번 목록을 양쪽으로 바꿔 넣어 그 사실을 재확인한다.
시나리오 11 「검증」의 「목록의 문법」과 같은 패턴이고 같은 이유다(§11 — 요구하는 자리와 보는 자리를 같게 둔다).

| 조건 id | 무엇이 참이어야 하는가 |
| --- | --- |
| `unit-done` | 대상 루트의 `docs/work/<id>/spec.md` 가 `status: done` 이고 `closed_at` 이 비어 있지 않다 — `close` 가 그 저장소에서 판정을 끝냈다 |
| `unit-checks-passed` | 그 단위의 `evidence/*.yaml` 중, 검증 계획(`required_checks`)의 명령을 **전부** 담고 그 종료 코드가 **전부 0** 인 run 이 하나 이상 있다 — 검사가 한 산출물 위에서 전부 돌았다 |
| `unit-reviewed` | 그 단위의 `review/` 에 `role: reviewer` 결과 봉투가 있고 그중 `gate_verdict: PASS` 가 하나 이상 있다 — 자기 검토가 아니다(C-D3) |

세 조건은 **한 단위**가 전부 만족해야 한다. 서로 다른 단위가 하나씩 만족하는 것은 통과가 아니다 —
그러면 「닫혔다」·「검사가 통과했다」·「검토를 받았다」가 각각 다른 일을 가리키게 된다.

**반례는 빈 루트가 아니라 그럴듯한 거짓 루트다**(§11). 빈 루트는 고치기 전에도 막혔으므로 판별력을 증명하지 않는다.
검사가 만드는 거짓 루트 셋은 전부 **`status: done` 까지 간** 루트다 — ① 증거의 종료 코드 하나가 `1` 인 것 ·
② `review/` 에 검토자 봉투가 **없는** 것(자기 검토) · ③ 봉투는 있는데 판정이 `FAIL` 인 것.

`check(root)` 를 **실제 대상 루트**에 대해 돌린 결과가 증거 `foreign-close-verdict` 다.

```
python3 tests/test_foreign_close.py --verdict <대상 루트>
```

이 명령은 이 저장소 **밖**의 상태를 읽으므로 `required_checks` 에 넣지 않는다 —
넣으면 대상 저장소가 없는 머신(CI)에서 이 단위가 영원히 닫히지 않는다. 시나리오 11 의 `foreign-router-verdict` 와 같은 자리다.
대상 루트가 없는 환경에서도 판별력이 남도록, **합성 루트 양쪽**(만족하는 것 · 위 거짓 루트 셋)을 판정하는 것은
`python3 -m unittest tests.test_foreign_close` 안에 있다.

**2026-09-06 실측.** 대상 루트에 대해 `--verdict` 가 rc=0 · 세 조건 전부 참이다.
그 단위는 `status: done` · `closed_at: 2026-09-06T11:45:44+09:00` 이고, 검사 기록은 `run_bbn8m3r4d80`(검증 계획 9건 전부 exit 0),
검토자 봉투는 `run_bbn8m3r4d80-reviewer.json`(PASS)이다. 회차는 `fail · fail · pass · pass` 이고 §10 재검토 1건이 들어 있다.

**시나리오 11 의 인용 대조는 이 구현으로 깨졌다.** 그 런북의 인용은 대상 `CLAUDE.md` 의 **줄 번호**에 고정돼 있는데,
이 관통이 마커 앞에 60줄을 넣어 Romeo 블록 인용이 전부 60줄씩 밀렸다.
실측(`python3 tests/test_foreign_router.py --claude-md <대상>/CLAUDE.md`): **FAIL · 불일치 9건**
`[126, 127, 160, 178, 179, 188, 189, 209, 210]` — 전부 Romeo 블록 인용이다. BMad 블록 인용(L42·65·67·76·104)은
삽입 지점 **앞**이라 그대로 일치한다. 그 대조는 M2 의 증거였고 `required_checks` 가 아니라 CI 는 빨갛지 않다.
고치지 않았다(§12 · Q-62) — M1·M2 는 이미 닫혔고, 이 관통이 남기는 것은 「§11 을 줄 번호로 구현하면 대상 파일이
바뀌는 순간 깨진다」는 실측이다.

## 되돌리기

이 관통이 대상 저장소에 만든 것은 **로컬 커밋 3건**과 그 단위 폴더다. **push 하지 않았으므로 원격 상태는 바뀌지 않았다.**

| 커밋 | 무엇 |
| --- | --- |
| `33a1c14` | 승인된 spec 을 커밋한다 |
| `c3b9eae` | 구현 — `CLAUDE.md` 에 「규칙 충돌 해소」 절 (managed block 275줄이 딸려 들어갔다 · 위 「어디서 구현하는가」) |
| `3738240` | AC-5 재승인과 수용 기준 체크 (D-80) |

```
git -C <대상> revert 3738240 c3b9eae 33a1c14
rm -rf <대상>/docs/work/feat-20260904-claude-md-rule-conflicts-bbn8
```

되돌린 뒤 그 단위의 `check-1`~`check-8` 이 다시 rc=1 로 돌아오는 것으로 복구를 확인한다 —
`CLAUDE.md` 에 그 절이 없으면 아홉 grep 중 여덟이 실패하고, `check-9`(`sha=08dc14bf`)만 마커가 남아 통과한다.
부착분은 이 관통 전에도 미커밋이었고 되돌린 뒤에도 미커밋이므로,
`git -C <대상> status --porcelain` 이 **부착 직후 목록**(시나리오 10 의 「놓는 것」)으로 돌아가는 것으로 확인한다.

부착 자체를 되돌리는 것은 이 런북이 아니라 시나리오 10 의 「되돌리기」다 — 두 절차는 겹치지 않는다.
하네스 저장소 쪽은 `git revert <구현 커밋>` 이다. 운영 상태·외부 상태·비용은 이 절차가 건드리지 않는다.
