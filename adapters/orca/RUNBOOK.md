# 위임 런북 — 작업 계약을 실제 실행으로 옮기는 방법

이 파일은 어댑터다. `core/` 는 이 파일을 읽지 않고, `romeo compile` 도 이 파일을 투영하지 않는다(`adapters/orca/` 에는 `adapter.yaml` 이 없다).
오케스트레이터를 바꿔도 TaskEnvelope 와 ResultEnvelope 는 그대로다 — 바뀌는 것은 이 문서뿐이다(계획 §3.3).

여기 적힌 플래그는 전부 `--help` 실측이다 — 오케스트레이션·런타임 CLI 도, `bin/romeo` 도 그렇다.
실측하지 못한 것은 §11 에 미검증으로 남긴다. 지어낸 명령은 없다(K-51).

## 1. 전제 확인

```bash
orca status --json
```

관찰 가능한 성공 신호: `.ok == true` 이고 `.result.runtime.state == "ready"`, `.result.runtime.reachable == true`. 종료 코드 0.
런타임 판은 `.result.runtime.appVersion` 에서만 읽는다 — `orca --version` 은 버전이 아니라 사용법을 인쇄한다(실측).
이 조건이 아니면 정확한 오류와 복구 방법만 보고하고 중단한다. 워커를 띄우지 않는다.

```bash
orca worktree current --json
```

관찰 가능한 성공 신호: `.result.worktree.repoId`(uuid), `.result.worktree.id`(= `<repoId>::<절대경로>`), `.result.worktree.head`(40자 SHA), `.result.worktree.branch`.
`worker-start --repo` 에는 `path:$PWD` 가 아니라 여기서 읽은 `id:<repoId>` 를 쓴다. `head` 값이 작업 계약의 `base_sha` 와 같아야 한다 — 그 값이 어디서 오는지는 §3.1·§3.3 이 정한다.

## 2. 계약 → 플래그 매핑

작업 계약 파일 자체는 손으로 쓰지 않는다. `bin/romeo envelope build` 가 승인된 Tech Spec 과 라우터 출력에서 계산해
`docs/work/<id>/task/<run-id>-<role>.json` 에 쓴다(§3.3). 아래 표는 **그 파일의 필드를 위임 명령으로 옮기는 방법**이다.

| TaskEnvelope 필드 | 위임 명령 / 런타임 플래그 | 근거 |
| --- | --- | --- |
| `workspace: worktree` | `worker-start --worktree new-child --repo id:<repoId> --setup inherit` | `worker-start --help` |
| `workspace: current` | `worker-start --worktree current` — 생성 플래그(`--name`·`--repo`·`--base-branch`·`--display-name`·`--comment`·`--setup`)는 거부된다 | `worker-start --help` Notes |
| `role` | 구현자는 `--agent <.harness/bindings.yaml 의 roles.implementer.runtime>`. 검토자는 `--agent` 를 쓰지 않는다 — 강제 수단을 걸어야 하므로 §3.7 의 `--terminal <handle>` 경로로 간다. 하드코딩하지 않고, 교체 실행은 `parity_swap.<role>` 을 쓴다 | D-68, `worker-start --help` |
| `base_sha` | 승인된 `spec.md` 가 들어 있는 커밋이다(§3.1). 새 워크트리는 `--base-branch <그 커밋이 tip 인 브랜치>`, 기존 워크트리는 `orca worktree current --json` 의 `head` 로 확인만 한다. 두 역할이 같은 값을 받아야 한다 | D-a, 계획 :573 |
| `allowed_paths: []` (검토자) | `roles.reviewer.enforcement` 의 명령형(`codex exec -s read-only`)을 `orca terminal create --command` 로 띄우고 그 핸들을 `worker-start --terminal` 로 채택한다(§3.7). `worker-start --agent` 에는 샌드박스 플래그도 명령 passthrough 도 없다(실측) | `codex exec --help`, `terminal create --help`, `worker-start --help`, D-68 |
| `output_schema` | **넘기지 않는다.** 형식 검증은 §3.8 의 `envelope check` 가 원본 스키마로 한다 — 그쪽이 더 강한 강제다(앵커 검사 5개). 출력 회수는 Codex `-o <파일>` · Claude `--output-format json` 으로만 한다 | 2026-08-29 관통 실측 — 아래 경고 |
| `required_checks` | 워커 안에서 `bin/romeo evidence checks --unit <id> --run <run-id> --task-id <task-id> --dispatch-id <dispatch-id>` 로 실행한다. 위임 계층이 대신 실행하지 않는다. **`<dispatch-id>` 는 §3.5 가 돌아온 뒤에야 존재한다** — 그 값을 돌고 있는 워커에게 넣는 자리는 §3.5.2 이고, 워커는 그 전에 증거 기록을 시작하지 않는다 | K-51, §3.5.2, §5 |
| `guards` | §8. M2 는 `bin/romeo evidence approve` 로 기록한다 | `core/policy/execution-guards.yaml` |

**`--output-schema` 를 쓰지 않는 이유 — 이 저장소의 스키마로는 실행이 거부된다(2026-08-29 실측).**
`codex exec --output-schema core/schemas/result-envelope.json` 은 HTTP 400 으로 끝난다:
`Invalid schema for response_format 'codex_output_schema': In context=('anyOf','0','properties','schema'), schema must have a 'type' key.`
`core/schemas/result-envelope.json` 의 `anyOf` 절은 역할별 제약을 표현하려고 `"schema": {}` 같은 **빈 하위 스키마**를 쓰는데,
그 런타임이 요구하는 형식은 모든 property 에 `type` 키를 요구한다. JSON Schema 로는 완전히 유효하므로
스키마 검사기로는 잡히지 않고 **그 CLI 를 실제로 호출해야만** 드러난다.
형식을 강제할 자리는 여기가 아니다 — §3.8 의 `envelope check` 가 같은 원본 스키마로 검증하고 앵커 검사 4개를 더 건다.
그래서 이 문서는 `--output-schema` 를 넘기지 않고, 출력 **형식**은 워커 프롬프트가 지시하고 **검증**은 종료 경로가 한다.

`--model` 과 `--effort` 는 **넘기지 않는다** — 계정 기본값을 쓴다(K-12). `--effort` 는 `--model` 을 요구하고, 둘 다 `--terminal` 과 결합할 수 없다(실측).

## 3. 실행 순서

### 3.0 경로 규약 — 계약 경로는 한 값이다

봉투(작업 계약·결과 계약) **안에 적히는 경로는 전부 그것을 읽거나 쓰는 워커의 작업 루트 기준 상대 경로**다.
역할에 따라 다르지 않다. 절대 경로는 적지 않는다.

| 무엇 | 값 |
| --- | --- |
| 작업 계약(워커의 입력) | `docs/work/<id>/task/<run-id>-<role>.json` |
| 결과 계약의 `task_envelope_ref.path` | 위와 같은 값 |
| 결과 계약의 `evidence_ref` | `docs/work/<id>/evidence/<run-id>.yaml` |
| 구현자 결과 계약(출력) | `docs/work/<id>/result/<run-id>-implementer.json` |
| 검토자 결과 계약(출력) | `docs/work/<id>/review/<run-id>-reviewer.json` |

이유는 종료 검사의 코드다. `romeo/close.py` 의 `_inside` 는 상대 경로를 `--root` 로 준 체크아웃에 붙여 풀고,
절대 경로는 그 체크아웃 **안**일 때만 받는다. 그 함수는 역할을 구분하지 않으므로 **구현자 봉투도 검토자 봉투와 같은 규칙에 걸린다.**
§3.8 이 두 봉투를 `--root "$W"`(구현자 워크트리)로 검사하므로, 위임한 쪽 체크아웃의 절대 경로를 적은 봉투는
역할과 무관하게 `TASK_ANCHORED` 에서 `저장소 밖이다` 로 FAIL 한다.

**셸에 넣는 값은 이 규약이 아니다.** `bin/romeo envelope check` 의 위치 인자, `orca terminal create --command` 안의
`-C`·`-o`·`$(cat …)` 는 셸이 자기 cwd 로 푸는 파일 경로일 뿐 봉투에 적히는 값이 아니다 — 그 자리에는 이 문서가
`$W` 절대 경로를 쓴다(어느 디렉터리에서 실행해도 같은 파일을 가리키게 하려는 것이다). 위 표는 **봉투 안**에만 적용된다.

### 3.1 승인 커밋 — 사람이 하는 단계가 여기 하나 있다

위임된 작업 공간은 **커밋된 것만** 본다. 승인 표시(`status: active`·`approved_at`)가 작업 트리에만 남아 있으면
자식 워크트리 안의 워커는 언제나 미승인 상태를 보고 `BLOCKED_APPROVAL` 로 끝난다. 그래서 순서가 정해져 있다(D-a).

```bash
bin/romeo approve <작업 단위 id> --by <승인자>
```

성공 신호: 종료 코드 0 과 `approved <id> at <시각> by <승인자> base_sha=<SHA>`.
이 명령은 승인 **사건**을 `spec.md` 에 기록할 뿐 커밋하지 않는다(D-61). 이어서 명령 자신이 다음 단계를 인쇄한다.

그 다음 **사람이** 승인된 `spec.md` **와 워커가 실행할 하네스 상태**를 커밋한다. 하네스는 커밋하지 않는다 —
무엇을 언제 커밋하는지는 사람의 판단이다. 이 커밋의 SHA 가 이후 모든 명령의 `<base-sha>` 이고,
이 커밋이 tip 인 브랜치 이름이 §3.5 의 `--base-branch` 다.

**커밋 범위가 spec 하나로는 부족하다.** 자식 워크트리는 이 커밋의 트리 그대로 만들어지는데(§3.5),
그 안의 워커는 계약 생성(§3.3 의 `bin/romeo envelope build`) · 검사 실행(§2·§5 의 `bin/romeo evidence checks --task-id --dispatch-id`) ·
역할 계약(`core/roles/`) · 스키마(`core/schemas/`) · 절차 문서(`core/workflows/{implement,review}/SKILL.md`) ·
부착 파일(`.harness/romeo.project.yaml`)을 **그 트리에서** 찾는다. 하나라도 커밋 밖에 있으면 워커의 첫 명령이 실패한다.
부착 파일이 없으면 라우터가 부품을 `pending_gate` 로 돌려주고, `core/workflows/implement/SKILL.md` 3번의
"`status` 가 `active` 가 아닌 부품은 쓰지 않는다" 에 걸려 규율 부품이 워커 안에서 전부 꺼진다.

관찰 가능한 성공 신호 — 셋을 **커밋 SHA 에 대고** 확인한다. 작업 트리에 파일이 있다는 것은 신호가 아니다.

1. 승인이 그 커밋 안에 있다 — `git show <base-sha>:docs/work/<id>/spec.md` 의 frontmatter 에
   `status: active` 와 `approved_at` 이 있다. 없으면 워커도 그것을 보지 못한다(다음 단계가 계약 생성을 거부한다).
2. 워커가 읽을 하네스 파일이 그 커밋 안에 있다 — 다음이 **8행**을 낸다. 커밋에 없는 경로는 인쇄되지 않으므로 행 수가 곧 판정이다.
   목록은 §3.4·§3.7 이 워커에게 실제로 넘기는 것과 같다 — 결과 계약 스키마와 두 역할의 절차 문서가 모두 들어 있어야
   워커가 출력 형식과 절차를 그 트리에서 찾을 수 있다.

```bash
git ls-tree <base-sha> --name-only -- \
  bin/romeo romeo/envelope.py core/roles/reviewer.yaml \
  core/schemas/task-envelope.json core/schemas/result-envelope.json \
  core/workflows/implement/SKILL.md core/workflows/review/SKILL.md .harness/romeo.project.yaml
```

3. 그 커밋의 `bin/romeo` 가 워커가 받을 명령을 실제로 갖고 있다 — 트리를 꺼내 `--help` 로 확인한다.
   `--help` 는 상태를 바꾸지 않으므로 안전하고, 임시 디렉터리라 이 체크아웃을 건드리지 않는다.

```bash
S=$(mktemp -d) && git archive <base-sha> | tar -x -C "$S"
"$S/bin/romeo" envelope build --help >/dev/null 2>&1;                  echo "envelope=$?"   # 0 이어야 한다
"$S/bin/romeo" evidence checks --help 2>&1 | grep -qs -- '--task-id';  echo "task-id=$?"    # 0 이어야 한다
rm -rf "$S"
```

셋 중 하나라도 어긋나면 워커를 띄우지 않는다 — 커밋을 보완하고 `<base-sha>` 를 다시 잡는다.
이 확인은 §3.5·§3.5.1·§3.7 의 기동 전 조건이다 — 특히 §3.5.1 은 자식 워크트리 안의 `bin/romeo` 로 계약을 다시 만드므로,
확인 2·3 이 통과하지 않았으면 그 명령이 실패하거나 다른 바이트를 낸다.

**이 셋은 §3.8 의 종료 검사 조건이기도 하다.** 종료 검사의 작업 계약 앵커는 봉투가 가리킨 계약을
**커밋된 원본에서 다시 계산해** 바이트로 대조한다(`romeo/close.py` 의 `_task_anchor` → `romeo/envelope.py` 의 `build_envelope`).
봉투가 주장하는 해시와 그 해시가 가리키는 파일은 둘 다 봉투 작성자가 정하는 값이라 해시 대조만으로는 앵커가 되지 않기 때문이다 —
재계산이라야 위조하려면 올바른 계약을 만들어야 하고, 그건 이미 올바른 계약이다.
재계산이 같은 바이트를 내려면 조건이 둘이고, **위 확인 1·2 가 정확히 그 둘이다.**

- (a) 종료 검사가 도는 체크아웃에서 `<base-sha>` 커밋 안의 `docs/work/<id>/spec.md` 가 **승인 상태**여야 한다
  (`status: active` · `approved_at`). 확인 1 이 그것이다. 승인 이전 커밋을 `base_sha` 로 쓴 계약은 재계산 자체가 거부된다(D-a).
- (b) 그 체크아웃의 하네스가 계약을 만들 때와 **같은 커밋**이어야 한다 — 정책표 · `core/roles/` · `core/schemas/` ·
  `.harness/romeo.project.yaml` 이 계약의 `allowed_paths`·`guards`·`required_checks`·`workspace` 를 계산하는 입력이기 때문이다.
  확인 2·3 이 그것이다.

그래서 §3.1 을 건너뛴 실행은 §3.8 에서 "해시는 맞는데 앵커가 열리지 않는다" 로 끝난다 —
계약 파일을 손으로 고쳐 맞출 수 있는 자리가 아니다. 커밋을 바로잡고 §3.3 부터 다시 돌린다.

### 3.2 Run 생성

```bash
orca orchestration run-create --objective "<작업 단위 id> · <한 줄 목표>" --json
```

성공 신호: `.ok == true`, `.result.run.id` 가 `run_` 접두 문자열(예: `run_7865ac0ae3e3`). 이 값이 이후 모든 명령의 `--run` 이다.
Run 은 이름 공간과 홈 인박스일 뿐 배치를 하지 않는다(실측 Notes).

### 3.3 작업 계약 생성 — 두 역할분

```bash
bin/romeo envelope build --unit <작업 단위 id> --role implementer --base-sha <base-sha> --run <run-id>
bin/romeo envelope build --unit <작업 단위 id> --role reviewer    --base-sha <base-sha> --run <run-id>
```

계약을 만드는 주체는 하네스다. 에이전트가 JSON 을 손으로 쓰면 "같은 입력이면 같은 계약" 이 성립하지 않는다.
`--run` 에는 §3.2 의 Run id 를 그대로 넣는다 — 그러면 `task/<run-id>-<role>.json` · `evidence/<run-id>.yaml` ·
`result/<run-id>-implementer.json` 의 `<run-id>` 가 한 값이 되어 세 산출물이 같은 이름으로 묶인다.

성공 신호: 종료 코드 0 과 `built implementer 계약 → docs/work/<id>/task/<run-id>-implementer.json`,
그 다음 줄에 `base_sha ... · spec ... · 계약 sha256 ... · workspace ... · guards [...] · required_checks N건`.
계약은 **커밋된 spec** 에서만 계산되므로 이후 작업 트리를 고쳐도 바이트가 바뀌지 않는다 — 같은 명령을 두 번 돌리면 같은 파일이 나온다.

실패 신호와 그 뜻:

| 메시지 | 무엇을 안 했나 |
| --- | --- |
| `base_sha 가 없다 — 승인 기록이 없다` | §3.1 의 `bin/romeo approve` 를 하지 않았다 |
| `<sha> 에 docs/work/<id>/spec.md 가 없다 — 승인된 spec.md 를 커밋한 뒤 --base-sha <커밋 SHA> 로 다시 만든다(D-a)` | 승인 커밋을 하지 않았다. HEAD 에 승인된 spec 이 있으면 메시지가 쓸 SHA 를 알려준다 |
| `<sha> 시점의 ... 는 승인 상태가 아니다` | 승인 이전 커밋을 지목했다 |

두 계약의 `base_sha` 는 같은 값이어야 한다. 다르면 두 역할이 같은 것을 보고 있지 않다(`review/SKILL.md` 1번이 그때 `BLOCKED_CAPABILITY` 로 끝낸다).

여기서 만든 계약은 **위임한 쪽의 체크아웃**에 놓인다 — 자식 워크트리는 §3.5 전에는 없기 때문이다.
이 사본은 **워커에게 넘기지 않는다**(§3.0). 쓰이는 곳은 하나다 — §3.5.1 확인 2 가 인쇄하는 `계약 sha256` 을
이 단계의 값과 대조하는 기준이다. §3.7(검토자 프롬프트)과 §3.8(종료 검사)은 계약을 **구현자 워크트리 안**에서 찾으므로,
워크트리가 생긴 직후 §3.5.1 이 같은 명령을 그 안에서 다시 돌려 계약을 거기에 실재시킨다.
증거와 결과 계약도 구현자 워크트리 안에 남는다(§3.8).

"자식 워크트리 안에서 같은 명령을 다시 돌려도 같은 파일이 나온다" 는 **조건부**다. `bin/romeo envelope build` 는
정책표를 호출된 `bin/romeo` 의 체크아웃에서 읽고, 부착 상태(`.harness/romeo.project.yaml`)는 대상 작업 트리에서 읽는다
(`romeo/envelope.py`). 그래서 두 체크아웃의 하네스가 같은 커밋일 때만 바이트가 같다 — §3.1 의 확인 2·3 이 그 전제를 보장한다.
전제를 눈으로 확인하는 자리가 §3.5.1 이다: 거기서 인쇄되는 `계약 sha256` 이 이 단계의 값과 다르면 두 체크아웃의
하네스가 다른 커밋이라는 뜻이므로, 계약을 고르지 말고 그 자리에서 중단한다.

### 3.4 Task 2개 생성 — 구현자와 검토자

```bash
orca orchestration task-create --run <run-id> \
  --task-title "<id> implementer" \
  --spec "<작업 계약 경로와 실행 조건>" --json

orca orchestration task-create --run <run-id> \
  --task-title "<id> reviewer" \
  --deps '["<implementer-task-id>"]' \
  --spec "<작업 계약 경로와 읽기 전용 조건>" --json
```

`--deps` 로 검토자가 구현자에 의존한다고 선언한다. 순서를 사람 기억에 맡기지 않는다.
`--spec` 에는 §3.0 표의 값을 그대로 넣는다 — **입력**(작업 계약 경로), **출력 경로**
(구현자 `docs/work/<id>/result/<run-id>-implementer.json` · 검토자 `docs/work/<id>/review/<run-id>-reviewer.json`),
그 출력의 **형식**(`core/schemas/result-envelope.json`), 그리고 봉투에 적을 `evidence_ref`
(`docs/work/<id>/evidence/<run-id>.yaml`). 여기에 검사를 증거 기록 명령으로 돌리라는 조건과 §5 의 식별자 플래그,
그리고 절차 문서(`core/workflows/{implement,review}/SKILL.md`)를 함께 넣는다 — 이것도 **자기 작업 루트 기준 상대 경로**다.

**이 시점에 아는 식별자는 둘뿐이다 — `<run-id>` 와 `<task-id>`.** `<dispatch-id>` 는 §3.5 의 `worker-start` 가
돌아오면서 발급하므로 지금 `--spec` 에 넣을 값이 없다. 없는 값을 자리표로 적어 넘기면 워커가 그 문자열을 그대로
증거에 기록하고, 그 증거는 어느 위임에서 나왔는지 말하지 못한다. 그래서 `--spec` 에는 값 대신 **받는 방법**을 적는다:

- 「`<dispatch-id>` 는 기동 뒤에 전달된다. 받기 전에는 `bin/romeo evidence run`·`evidence checks` 를 시작하지 않는다.」
- 「전달이 늦으면 `orca orchestration dispatch-show --task <task-id> --json` 으로 스스로 조회한다」
  (`dispatch-show --help` 실측: `--task <task_id>` 를 받는다. **반환 JSON 의 어느 필드가 dispatch id 인지는 미확인**이다 — §11).
- 「두 식별자는 증거 레코드에 run 당 한 번만 기록된다. 먼저 `--task-id` 만 붙은 실행이 있어도,
  나중 실행에 `--dispatch-id` 를 붙이면 같은 레코드에 채워진다」(`romeo/evidence.py` 의 `_stamp_ids` — 빈 자리는 채우고 다른 값만 거부한다).
이 단계에서는 자식 워크트리(`$W`)가 아직 없어 절대 경로를 쓸 수 없고, 쓸 필요도 없다: 워커는 그 워크트리 안에서 돌고
그 트리는 `<base-sha>` 의 체크아웃이라 미커밋 변경이 없다. 그 문서가 그 커밋 안에 있다는 것은 §3.1 확인 2 가 보장한다.

**출력 경로를 빼먹지 않는다.** 구현자 결과 계약을 만드는 것은 구현자 자신이고(§3.8), 그 파일을 §3.8 의
`envelope check` 가 `$W/docs/work/<id>/result/<run-id>-implementer.json` 에서 찾는다. 경로를 넘기지 않으면
그 자리에 파일이 없어 `ERROR 결과 계약 파일이 없다` 종료 코드 1 로 멈춘다.

**계약 경로는 두 역할이 같다(§3.0).** 두 역할 모두 **자기 작업 루트 기준 상대 경로**
(`docs/work/<id>/task/<run-id>-<role>.json`)를 받고, 결과 계약의 `task_envelope_ref.path` 에도 같은 값을 적는다.
그 자리의 파일은 §3.5.1 이 자식 워크트리 안에 만들고, 검토자는 `-C $W` 로(§3.7), 구현자는 그 워크트리 안에서 기동되므로
둘 다 자기 cwd 에서 같은 상대 경로로 그 파일에 닿는다. 위임한 쪽 체크아웃의 절대 경로를 주면 그 값이 그대로 봉투에 적혀
종료 검사가 "저장소 밖" 으로 거부한다(§3.8) — 역할과 무관하다.

**구현자는 §3.5.1 보다 먼저 기동된다.** `worker-start` 가 돌아온 직후에 §3.5.1 이 돌지만 워커는 이미 시작돼 있다.
그래서 구현자 `--spec` 에만 한 줄을 더 넣는다 — 「그 상대 경로에 계약이 아직 없으면 자기 작업 루트에서
`bin/romeo envelope build --unit <id> --role implementer --base-sha <base-sha> --run <run-id>` 로 만든다」.
같은 입력이면 바이트까지 같은 계약이 나오므로(§3.3) §3.5.1 과 경쟁하지 않는다 — 어느 쪽이 먼저 써도 같은 파일이다.
검토자에게는 이 줄을 넣지 않는다. 검토자에게는 쓰기가 없다(§4) — 계약이 그 자리에 없으면 §3.5.1 을 빠뜨린 것이고,
검토자는 만들지 말고 `BLOCKED_CAPABILITY` 로 끝낸다.
성공 신호: `.ok == true` 와 task id. 이후 `orca orchestration task-list --run <run-id> --brief --json` 으로 두 건이 보인다.

### 3.5 구현자 기동

**기동 전 조건.** §3.1 의 확인 3개(승인·`ls-tree` 8행·`--help` 프로브 2개)가 전부 통과해야 한다.
하나라도 실패한 채 띄우면 그 워커는 자기가 실행할 하네스가 없는 트리에서 시작한다 — 첫 명령이 실패한다.

```bash
orca orchestration worker-start \
  --run <run-id> \
  --task <implementer-task-id> \
  --worktree new-child \
  --agent <bindings.roles.implementer.runtime> \
  --name impl-<작업 단위 id> \
  --repo id:<repoId> \
  --base-branch <승인 커밋이 tip 인 브랜치> \
  --setup inherit \
  --timeout-ms 3600000 \
  --json
```

성공 신호: **종료 코드 0**. 실측 Notes 그대로 — `worker-start` 는 `ready` 일 때만 0 으로 끝나고, `failed` 와 `outcome_unknown` 은 1 로 끝나며 JSON 에 `stage`/`failedStage`·`setup`·`effects`·`residualResources` 와 복구 명령이 실린다. 1 이면 §7 로 간다.
반환 JSON 에서 `dispatch_id` 를 보관한다 — 이후 `worker-show`·`worker-read`·`worker-release` 와 §5 의 `--dispatch-id` 가 전부 이 값을 요구한다.

**여기서 만들어진 자식 워크트리의 절대 경로도 보관한다.** 이 값이 §3.5.1·§3.7·§4 의 `$W` 이고, 이후 세 단계가 전부 이 경로를 쓴다.
반환 JSON 의 어느 필드가 그 경로인지는 미관측이므로(§11), 확인되지 않으면 `orca worktree list --repo id:<repoId> --json` 에서
`--name impl-<작업 단위 id>` 로 준 이름의 행을 찾아 그 경로를 쓴다. 성공 신호는 그 경로가 디렉터리로 존재하고
`"$W/bin/romeo" --help` 가 종료 코드 0 을 내는 것이다 — 하네스가 없는 경로를 잡았으면 여기서 드러난다.

기동 뒤 자식 워크트리에서 `orca worktree current --json` 의 `head` 가 `<base-sha>` 와 같은지 확인한다(§1).
다르면 그 워커는 계약과 다른 리비전을 보고 있다 — 승인도 그 안에서 보이지 않는다. 계속하지 않는다.

### 3.5.1 계약을 구현자 워크트리에 실재시킨다 — 빼먹으면 이후 두 단계가 조용히 깨진다

§3.3 의 계약은 위임한 쪽 체크아웃에만 있다. 그런데 §3.7 은 그 파일을 `$W` 안에서 읽어 검토자 프롬프트로 넘기고,
§3.8 의 종료 검사도 그 체크아웃 안에서 계약을 찾는다(`romeo/close.py` 의 `_task_anchor`·`_inside`).
**두 실패 모두 조용하다.** `$(cat …)` 는 없는 파일에 대해 빈 문자열로 접히고 종료 코드도 0 이라 검토자가
**프롬프트 없이** 기동되며, 그것이 "검토는 돌았는데 할 말이 없었다" 와 구분되지 않는다. close 쪽은 조용하지 않지만
`REVIEW_TASK_ANCHORED` 가 **절대** 통과하지 못한다 — 저장소 밖 절대 경로도 거부되므로(§3.0)
위임한 쪽 체크아웃의 사본을 가리켜 대체할 수 없다.
자식 워크트리는 §3.5 전에는 없으니, 워크트리가 생긴 **직후인 여기서** 같은 명령을 그 안에서 다시 돌린다.

```bash
W=<구현자 워크트리 절대경로>      # §3.5 가 만든 자식 워크트리

"$W/bin/romeo" envelope build --unit <작업 단위 id> --role implementer --base-sha <base-sha> --run <run-id> --root "$W"
"$W/bin/romeo" envelope build --unit <작업 단위 id> --role reviewer    --base-sha <base-sha> --run <run-id> --root "$W"
```

`$W/bin/romeo` 와 `--root "$W"` 를 **둘 다** 자식 워크트리로 맞추는 것이 핵심이다. 앞은 정책표를 읽을 체크아웃을,
뒤는 부착 상태와 계약이 놓일 작업 트리를 정한다(§3.3 의 조건부 문단). 하나만 맞추면 다른 입력으로 계산한 계약이 나온다.

관찰 가능한 성공 신호 — 세 가지를 전부 본다.

1. 두 줄 모두 **종료 코드 0** 이고, 인쇄된 경로가 `$W` 아래다:
   `built <role> 계약 → <W>/docs/work/<id>/task/<run-id>-<role>.json`.
2. 그 다음 줄의 **`계약 sha256` 12자리가 §3.3 이 인쇄한 같은 역할의 값과 같다.** 다르면 두 체크아웃의 하네스가
   다른 커밋이라는 뜻이다(§3.1 확인 2·3 이 보장했어야 하는 전제가 깨졌다) — 검토자를 띄우지 말고 중단한다.
3. 파일이 실제로 거기 있다 — 다음이 **2행**을 내고 종료 코드 0 이다. 이 확인을 생략하면 위의 조용한 실패가 그대로 §3.7 로 넘어간다.

```bash
ls "$W/docs/work/<id>/task/<run-id>-implementer.json" \
   "$W/docs/work/<id>/task/<run-id>-reviewer.json"
```

셋 중 하나라도 어긋나면 §3.7 로 넘어가지 않는다. **복사로 대신하지 않는다.** 종료 검사는 계약을 이 체크아웃에서
다시 계산해 바이트로 대조하므로(§3.1), 다른 하네스 커밋에서 만든 계약을 복사해 두면 close 가
`지금 다시 계산한 계약과 바이트로 다르다` 로 거부한다. 두 체크아웃의 하네스가 같은 커밋이면 복사와 재실행이 같은 파일을
내지만, 그 전제를 눈으로 대조하는 자리가 위 2번이다 — 대조 없이 복사하면 그 전제를 믿기만 하는 것이다.

이 단계가 §3.5 **뒤**인 것은 자식 워크트리가 그전에 없기 때문이다. 구현자는 이미 돌고 있지만 문제가 되지 않는다 —
§3.4 가 구현자에게 "그 상대 경로에 없으면 같은 명령으로 만든다" 를 함께 넘겼고, 같은 입력이면 바이트까지 같은 계약이
나오므로 어느 쪽이 먼저 써도 같은 파일이다. 여기서 만드는 사본은 **검토자(§3.7)와 종료 검사(§3.8)를 위한 것**이고,
동시에 구현자 계약이 그 자리에 실재하는지 눈으로 대조하는 자리다(위 확인 3).
이 쓰기가 신선도 검사를 흔들지도 않는다 — `docs/work/<id>/` 는 evidence 의 `dirty_tree_hash`·`changed_files` 계산에서
빠지고(`romeo/evidence.py` 의 `exclusions()`), §4 의 방어 검사도 같은 경로를 명시적으로 제외한다.

### 3.5.2 위임 식별자를 돌고 있는 워커에게 전달한다 — §3.4 가 넘기지 못한 값

`<dispatch-id>` 는 §3.5 가 발급하므로 §3.4 의 `--spec` 에 들어갈 수 없었다(§3.4). 워커는 이미 돌고 있고,
그 값 없이 증거를 기록하면 그 증거는 어느 위임에서 나왔는지 말하지 못한다. 그래서 기동 직후에 전달한다.

```bash
orca orchestration send \
  --to dispatch:<구현자 dispatch-id> \
  --run <run-id> \
  --task-id <implementer-task-id> \
  --dispatch-id <구현자 dispatch-id> \
  --subject "위임 식별자 — <작업 단위 id>" \
  --body "evidence 기록에 --run <run-id> --task-id <implementer-task-id> --dispatch-id <구현자 dispatch-id> 를 붙인다" \
  --json
```

`--to dispatch:<id>` 는 그 시도에 한정된 조정 지시를 워커 쪽으로 durable 하게 중계하는 형식이다(`send --help` Notes 실측).
`--task-id`·`--dispatch-id` 는 payload JSON 에 그 값을 싣는 전용 플래그다(같은 Notes: raw `--payload` 보다 이쪽을 쓴다).

관찰 가능한 성공 신호: 종료 코드 0 과 `.ok == true`. **이것은 "보냈다" 의 신호이지 "워커가 읽고 반영했다" 의 신호가 아니다.**
반영됐는지는 §3.8 의 식별자 검사가 판정한다 — 그 검사가 이 단계의 게이트다. 그 전까지 이 단계는 미확인이다.

전달이 워커에 닿지 않으면 워커 쪽에서 스스로 조회하는 길이 있다 — `orca orchestration dispatch-show --task <task-id> --json`
(`--help` 실측: `--task <task_id>` 를 받는다). **두 명령 모두 반환 JSON 의 필드 이름은 미확인이다**(§11) —
첫 실행에서 §3.7 (1) 의 (a)~(c) 와 같은 방법으로 확인한다.

### 3.6 대기

```bash
orca orchestration check --run <run-id> --wait \
  --types worker_done,escalation,question --timeout-ms 900000 --json
```

`--wait` 는 15초마다 stderr 로 keepalive JSON 줄을 낸다. 스트림을 합칠 때는 `jq 'select(._keepalive|not)'` 로 거른다(실측 Notes).
성공 신호: `worker_done` 타입 메시지 1건. `question`·`escalation`·시간 초과를 성공으로 간주하지 않는다.
바인딩된 Run 은 `--ack <delivery_id>` 전까지 같은 Delivery 를 계속 되돌려준다 — 배치의 모든 메시지를 처리한 뒤에 ack 한다.
워커가 사람만 답할 수 있는 프롬프트에 멈춰 있는지는 `orca orchestration worker-show --dispatch <id> --json` 의 `observation.agentWait` 로 본다. `null` 은 "찾아봤고 없다", 필드 부재는 "보지 못했다" 이지 "대기 중이 아니다" 가 아니다(실측 Notes). 대기 중인 워커는 실패가 아니다.

### 3.7 검토자 기동 — 강제 수단을 걸고 띄우는 2단계

검토자는 구현자가 바꾼 코드를 봐야 하므로 **구현자의 워크트리를 그대로** 가리킨다. 기존 워크트리에는 생성 플래그를 붙이지 않는다(거부된다).

**왜 `--agent` 로 띄우지 않는가.** `worker-start --help` 의 인자 목록에는 `-s/--sandbox` 도, 모델이 실행할 명령을 그대로 넘기는
passthrough(`--`) 도 없다(실측). 즉 §4 가 정본이라고 선언한 강제 수단을 `--agent` 경로에는 넣을 자리가 없다.
`--agent` 로 띄우면 검토자는 아무 샌드박스 없이 기동된다. 그래서 **강제 수단이 걸린 명령을 터미널로 띄우고, 그 터미널을 워커로 채택**한다.
두 명령 모두 `--help` 실측이고, `worker-start` 는 `(--agent <agent> | --terminal <handle>)` 로 택일이다.

**`--command` 에 넣는 것은 비대화형 실행이 아니라 대화형(TUI) 실행이다 — 2026-08-29 관통에서 확정.**
같은 강제 수단(`-s read-only`)을 두 형태로 시험했고 결과가 정반대였다.

| `--command` 에 넣은 것 | `worker-start --terminal` 결과 |
| --- | --- |
| `codex exec -s read-only …` (비대화형) | **실패** — `state: failed` · `stage: dispatch_input` · `last_failure: agent_prompt_stalled` |
| `codex -s read-only` (TUI) | **성공** — `state: ready` · `stage: input_accepted` |

이유는 두 명령이 프롬프트를 받는 자리가 다르기 때문이다. `worker-start --terminal` 은 채택한 터미널에
**task spec 과 lifecycle 프리앰블을 입력으로 주입**한다. 비대화형 실행은 프롬프트를 argv 로 이미 받고 입력을 더 받지 않으므로
그 주입이 갈 곳이 없다. 그 실행은 계속 돌지만(argv 로 받은 일은 한다) **Dispatch 는 실패로 settle 되고
`worker_done`·heartbeat·`ask` 가 전부 없다** — 즉 §3.6 의 대기가 그 워커에게는 영원히 오지 않는다.

따라서 검토자는 **TUI 로 띄운다.** 그러면 세 가지가 동시에 성립한다.

1. 강제가 걸린다 — 그 런타임의 TUI 도 같은 `-s/--sandbox` 플래그를 받는다(`codex --help` 실측).
2. lifecycle 이 산다 — 주입을 받을 수 있으므로 `worker_done` 을 보낼 수 있고 §3.6 의 대기가 성립한다.
3. **§3.4 의 `--spec` 이 검토자에게 실제로 도달한다.** 비대화형 경로에서는 `--spec` 이 오케스트레이션 DB 에만 남고
   프롬프트로 가지 않아, 절차 문서(`core/workflows/review/SKILL.md`)를 가리키는 문장이 워커에 닿지 않았다.

비대화형 형태를 굳이 쓸 이유가 있다면(예: 그 실행 자체를 관측하고 싶을 때) 워커로 채택하지 말고
터미널만 만들어 `-o` 출력으로 회수한다. 그때 그 Task 는 orchestration 이 완료로 표시하지 못하므로
**`task-update` 로 사람이 정리해야 한다** — lifecycle 을 포기하는 선택임을 알고 해야 한다.

**기동 전 조건.** §3.1 의 확인 3개를 통과했고, **§3.5.1 의 확인 3개(종료 코드·sha256 일치·`ls` 2행)를 통과했으며**,
검토자 기동 **직전**의 §4 방어 검사(`review-tree-before`)를 이미 기록했다.
계약이 `$W` 안에 없으면 아래 `$(cat '$T')` 가 빈 문자열이 되어 검토자가 프롬프트 없이 돈다 — 그 실패는 조용하다.

(1) 강제 수단이 걸린 터미널을 만든다.

```bash
W=<구현자 워크트리 절대경로>
T=$W/docs/work/<id>/task/<run-id>-reviewer.json      # §3.5.1 이 이 워크트리 안에 실재시킨 검토자 계약

# 검토자에게 갈 프롬프트 = 절차 지시 + 계약 JSON. 두 파일을 이어 붙여 한 프롬프트로 넘긴다.
# 절차 파일은 검토 대상 워크트리 **밖**에 둔다 — 안에 두면 §4 방어 검사가 그 파일 때문에 무효가 된다.
P=<절차 지시 파일의 절대경로>                                # §3.4 의 검토자 --spec 과 같은 내용

# 그 절차 파일에는 계약의 sha256 을 **위임한 쪽이 계산해** 적어 둔다(아래 상자 참조).
shasum -a 256 "$T" | cut -d' ' -f1

CMD="codex -s read-only -C '$W' \"\$(cat '$P'; cat '$T')\""

orca terminal create \
  --worktree "path:$W" \
  --title "review-<작업 단위 id>-<run-id>" \
  --command "$CMD" \
  --json
```

`CMD` 의 앞부분은 `.harness/bindings.yaml` 의 `roles.reviewer.enforcement` 값(`codex exec -s read-only`)을 그대로 옮긴 것이다.
이 문서는 그 값을 옮겨 적을 뿐이다 — 두 값이 다르면 bindings 가 맞다. 역할 교체 실행(§6)이면 같은 자리에
`parity_swap.reviewer.enforcement` 를 넣는다: `claude -p --tools "Read" "Grep" "Glob" --allowedTools "Read" "Grep" "Glob" --strict-mcp-config`
(그 런타임의 스키마 전달 형태는 §4 의 두 번째 블록 그대로 — `--json-schema` 에는 파일 경로가 아니라 내용을 넣는다).

경로를 작은따옴표로 감싸는 것은 공백이 든 절대 경로가 터미널 쪽 셸에서 쪼개지지 않게 하기 위해서다.
`\$(cat '$T')` 의 `\$` 는 바깥 셸의 확장을 막는 것이다. 계약 JSON 을 여기서 펼치지 않고 **문자열 그대로** 넘겨,
터미널 쪽 셸이 자기 워크트리에서 그 파일을 읽게 한다. 바깥에서 펼치면 계약 본문의 따옴표가 명령 문자열을 깨뜨린다.

**핸들은 `.result.terminal.handle` 이다(2026-08-29 실측).** 반환 JSON 은
`{ok, result: {terminal: {handle, tabId, paneKey, ptyId, worktreeId, title, executionHostId, hostPlatform, surface}}}` 이고
`handle` 이 `term_<uuid>` 형태다. 확인 절차는 그대로 둔다 — 판이 바뀌면 필드도 바뀔 수 있고, 짐작해 넣은 실패는
"강제 없이 기동됨" 과 구분되지 않기 때문이다. (a) 그 값을 고른다. (b) `orca terminal show --terminal <값> --json` 에 넣어
방금 만든 터미널(같은 `--title`, 같은 워크트리)이 종료 코드 0 으로 돌아오는지 본다. 돌아오지 않으면
(c) `orca terminal list --worktree "path:$W" --json` 에서 같은 제목의 행을 찾아 다시 (b) 로 확인한다.
**확인되기 전에는 (2) 로 넘어가지 않는다.**

TUI 는 기동에 시간이 걸리므로 (2) 전에 준비를 기다린다 — 기다리지 않고 채택하면 주입이 기동과 경쟁한다.

```bash
orca terminal wait --terminal "$HANDLE" --for tui-idle --timeout-ms 90000 --json
```

성공 신호: `.result.wait.satisfied == true` 이고 `.result.wait.status == "running"`(실측).

**절차 파일에 계약 해시를 적어 준다 — 적지 않으면 두 런타임의 판정이 갈린다(2026-08-29 관통에서 확정).**

결과 계약 스키마는 검토자에게 `task_envelope_ref.sha256` 을 요구한다. 그런데 검토자의 역할 계약
(`core/roles/reviewer.yaml` 의 `capabilities: [read, search]`)과 절차 문서(`core/workflows/review/SKILL.md` 2번)는
**명령 실행을 금지**한다. 해시 계산은 명령 실행이므로, 계약을 지키는 검토자는 그 필드를 채울 수 없다.

두 실행에서 실제로 갈렸다.

| 검토자 | 강제 수단 | 명령 실행 | 역할 계약 | 결과 |
| --- | --- | --- | --- | --- |
| codex | `-s read-only` | **가능** — 샌드박스는 쓰기만 막고 읽기 명령은 막지 않는다(프로브로 확인: `shasum` 이 `succeeded in 0ms` 로 정확한 해시를 냈다) | **위반** | 해시를 스스로 계산해 판정을 냈다 |
| claude | `--tools "Read" "Grep" "Glob"` | 불가 — 도구 목록에 실행이 없다 | 준수 | 해시를 채우지 못해 `BLOCKED_CAPABILITY` · 그 봉투는 `TASK_ANCHORED` 에서 거부됐다 |

**계약을 지킨 쪽이 판정을 못 내고 어긴 쪽이 냈다.** 그 상태로는 동등성 비교가 성립하지 않는다 —
비교되는 것이 두 런타임의 판정이 아니라 **두 런타임의 권한 초과 여부**이기 때문이다.

그래서 해시는 **위임한 쪽이 계산해 프롬프트에 적어 준다.** 검토자에게는 "직접 계산하지 마라, 이 값을 옮겨 적어라" 를
명시한다. 이렇게 하면 역할 계약을 약화시키지 않고 앵커 검사(`TASK_ANCHORED` 의 재계산 대조)도 그대로 강하다 —
검토자가 옮겨 적은 값이 틀리면 §3.8 의 `envelope check` 가 잡는다.

**`-s read-only` 가 강제하지 못하는 것을 여기 적어 둔다.** 그 플래그는 **모델이 만든 셸 명령의 쓰기**를 막을 뿐,
명령 실행 자체를 막지 않는다. 역할 계약의 "명령을 실행하지 않는다" 는 그 수단으로 강제되지 않고 **지침으로만 존재한다**.
§4 표의 `강제 수단` 칸이 덮는 범위가 역할 계약보다 좁다는 뜻이다 — 그 차이를 아는 것이 이 문단의 목적이다.

(2) 그 터미널을 워커로 채택한다. `HANDLE` 은 (1) 에서 **확인이 끝난** 값이다.

```bash
HANDLE=<(1) 에서 확인한 핸들>

orca orchestration worker-start \
  --run <run-id> \
  --task <reviewer-task-id> \
  --worktree "path:$W" \
  --terminal "$HANDLE" \
  --timeout-ms 1800000 \
  --json
```

`--terminal` 을 명시하지 않으면 **새 에이전트 터미널이 생긴다**(실측 Notes) — 그 터미널에는 (1) 의 강제 수단이 걸려 있지 않다.
이 경로에서 `--terminal` 생략은 조용한 실패다. 기존 워크트리는 setup 을 다시 돌리지 않는다.
`--model`·`--effort` 는 `--terminal` 과 결합할 수 없고(실측 Notes) 어차피 넘기지 않는다(K-12 · §2). 대기는 §3.6 과 같다.

검토자 종료 **직후**에 §4 의 나머지 방어 검사(`review-tree-after`)를 돌린다.
두 방어 검사를 돌리는 것은 **위임한 쪽**이다 — 검토자는 명령을 실행하지 않는다(`core/workflows/review/SKILL.md` 6번).

### 3.8 결과 회수

구현자의 결과 계약: `docs/work/<id>/result/<run-id>-implementer.json`
검토자의 결과 계약: `docs/work/<id>/review/<run-id>-reviewer.json`

둘 다 **구현자 워크트리 안**의 작업 단위 폴더에 쓴다. 종료 검사(`bin/romeo close --unit <id>`)가 그 체크아웃에서 돌면서
거기 있는 evidence · `review/` · **`task/`** 를 읽고, 그 체크아웃의 **git 이력**으로 계약의 `base_sha` 를 대조하기 때문이다(K-62).
`task/` 까지 읽는다는 것이 §3.5.1 이 필요한 이유다 — 검토자 결과 계약의 `task_envelope_ref.path` 가 가리키는 파일이
이 체크아웃 안에 실재하고 sha256 이 맞아야 `REVIEW_TASK_ANCHORED` 가 통과하고, 그 계약의 `base_sha` 가 이 체크아웃의
HEAD 이력 안에 있어야 `REVIEW_BASE_SHA` 가 통과한다(`romeo/close.py` 의 `_task_anchor`·`_base_sha_anchor`).
그래서 `task_envelope_ref.path` 는 **이 워크트리 기준 상대 경로**(`docs/work/<id>/task/<run-id>-<role>.json`)로 쓴다 —
`_inside` 는 역할을 구분하지 않으므로 **구현자 봉투와 검토자 봉투에 똑같이 걸린다**(§3.0). 저장소 밖 절대 경로를 적으면
어느 쪽이든 `TASK_ANCHORED` 에서 거부된다. `evidence_ref` 도 같은 이유로 이 작업 단위 폴더 안을 상대 경로로 가리켜야 한다
(`_evidence_anchor`). 그 앵커가 무엇을 요구하는지는 §3.1 의 (a)·(b) 두 조건이다 — 계약은 커밋된 원본에서 다시 계산해 대조된다.
`result/` 는 종료 검사가 보지 않는다 — 구현자 결과 계약의 검증은 이 절 마지막 단계의
`bin/romeo envelope check` 가 전부다.

**구현자는 자기 결과를 스스로 쓴다.** 구현자에게는 작업 공간 쓰기가 있으므로(D-68) `core/workflows/implement/SKILL.md` 8번대로
결과 계약을 §3.0 의 출력 경로에 직접 쓴다. 회수 단계가 따로 없으니 **파일이 그 자리에 있는지부터 본다** — 1행·종료 코드 0 이다.

```bash
ls "$W/docs/work/<id>/result/<run-id>-implementer.json"
```

없으면 구현자가 결과 계약을 내지 않은 것이다. `orca orchestration worker-read --dispatch <구현자 dispatch-id> --source auto --json`
으로 그 워커의 출력을 읽어 무엇이 막혔는지(`BLOCKED_*`) 확인한다. **없는 파일을 손으로 만들지 않는다** —
계약은 실행이 만들고, 손으로 만든 파일은 §3.1 의 재계산 대조를 통과하지 못한다.

**검토자는 자기 결과를 스스로 쓰지 않는다.** 검토자를 띄운 쪽이 위 경로에 쓴다. 그래야 read-only 강제와 종료 검사와 K-62 가 동시에 성립한다.
받아오는 자리는 둘이고, §3.7 을 어느 형태로 띄웠는지가 어느 자리를 쓸지 정한다.

- **TUI 로 띄워 워커로 채택한 경우**(§3.7 의 권장 경로): 판정은 `worker_done` 과 함께 오고,
  본문은 `worker-read --dispatch <검토자 dispatch-id>` 로 회수한다.
- **비대화형으로 띄워 워커로 채택하지 않은 경우**: 판정은 `-o` 가 지정한 파일에 떨어진다.
  **그 파일은 read-only 아래에서도 만들어진다**(2026-08-29 실측 — 검토 대상 워크트리 **밖** 경로에 855바이트를 썼다).
  `-s` 는 **모델이 만든 셸 명령**에만 걸리고 CLI 자신이 여는 출력 파일에는 걸리지 않기 때문이다.
  그래서 `-o` 대상은 검토 대상 워크트리 **밖**에 둔다 — 안에 두면 §4 의 방어 검사가 그 파일 때문에 무효가 된다.

어느 자리에서 받았든 `review/` 경로에 쓰는 것은 위임한 쪽이다. 검토자가 그 파일을 쓰지 않는다.

```bash
orca orchestration worker-read --dispatch <검토자 dispatch-id> --source auto --limit 400 --json
```

`auto` 는 훅이 보고한 정확한 transcript 가 있으면 그것을, 없으면 라벨이 붙은 터미널 출력을 준다. 반환된 커서는 그 소스에 고정되므로 `source_changed` 가 나오면 처음부터 다시 읽는다(실측 Notes).
구현자 결과 계약이 그 자리에 있고(위 `ls`) 검토자 판정을 회수해 파일로 쓴 뒤, 결과 계약 두 개를 검사한다.
손으로 스키마를 대조하지 않는다 — 명령이 한다. 위치 인자는 봉투 안의 값이 아니라 셸이 푸는 파일 경로이므로 `$W` 절대 경로다(§3.0).

```bash
"$W/bin/romeo" envelope check --unit <작업 단위 id> --role implementer --root "$W" \
  "$W/docs/work/<id>/result/<run-id>-implementer.json"

"$W/bin/romeo" envelope check --unit <작업 단위 id> --role reviewer --root "$W" \
  "$W/docs/work/<id>/review/<run-id>-reviewer.json"
```

관찰 가능한 성공 신호: 두 줄 모두 **종료 코드 0** 이고
`romeo envelope check <경로> → PASS (unit <id> · role <role>)` 다음에 각 검사가 `[PASS]` 로 인쇄된다.
종료 코드 **1 은 위반**, **2 는 검사 불가**(대조가 성립하지 않은 검사가 있다)다 — 2 를 통과로 접지 않는다(K-51).
0 이 아니면 성공이라고 말하지 않고, 인쇄된 `[FAIL]`/`[UNVERIFIED]` 줄의 이유를 먼저 해소한다.

이 검사는 종료 검사가 검토자 봉투에 쓰는 함수를 그대로 부른다(`romeo/envelope.py` 의 `check_result_envelope`) —
그래서 §3.5.1 을 빠뜨린 경우가 close 까지 가지 않고 **여기서** 검토자 봉투의 앵커 검사로 드러난다.
`result/` 쪽은 close 가 보지 않으므로 이 명령이 구현자 결과 계약의 유일한 검증이다.

종료 검사가 이 파일들을 읽는다. `review/*.json` 이 없으면 `HAS_REVIEW` 가 FAIL 이고, 스키마·`unit_id`·`role` 이 맞지 않으면
`REVIEW_ENVELOPE_VALID` 가 FAIL 이며, **`gate_verdict` 가 `PASS` 가 아닌 판정이 하나라도 남아 있으면 `REVIEW_VERDICT` 가 FAIL 이다**(D-c).
빈 파일 하나로 통과하던 예전 동작이 아니다. 검토자가 FAIL 을 냈으면 고친 뒤 다시 검토받는다 — 낡은 FAIL 봉투를 남겨 두면 close 는 계속 거부한다.

**위임 식별자가 실제로 워커에 닿았는지 여기서 판정한다(§3.5.2 의 게이트).** §3.5.2 의 `send` 가 종료 코드 0 을 냈다는 것은
보냈다는 뜻일 뿐이다. 워커가 받아 반영했는지는 그 워커가 남긴 증거에만 나타난다.

```bash
python3 - "$W/docs/work/<id>/evidence/<run-id>.yaml" <implementer-task-id> <구현자 dispatch-id> <<'PY'
import sys, yaml
rec = yaml.safe_load(open(sys.argv[1]))
got = (rec.get("task_id"), rec.get("dispatch_id"))
print(f"task_id={got[0]} dispatch_id={got[1]}")
ok = got == (sys.argv[2], sys.argv[3])
print("일치" if ok else "불일치 — 워커가 위임 식별자를 받지 못했거나 다른 값을 기록했다")
sys.exit(0 if ok else 1)
PY
```

성공 신호: 종료 코드 0 과 `일치`. 둘 중 하나가 `None` 이면 §3.5.2 의 전달이 닿지 않은 것이다 —
그 증거는 실행되기는 했지만 **어느 위임에서 나왔는지 말하지 못한다.** 조용히 지나가지 않는다.
값이 다르면 그 run 이 두 위임에 걸쳐 있다는 뜻이므로(`_stamp_ids` 는 다른 값을 거부한다) 새 `--run` 으로 다시 돌린다.

**종료 검사를 실행한다.** 이 절이 여기서 끝나지 않는다 — 결과 계약이 검사를 통과했다는 것과 그 작업 단위가 완료라는 것은 다르다.
종료 검사는 **구현자 워크트리에서** 돈다. 거기에 evidence·`review/`·`task/` 가 있고, 그 체크아웃의 git 이력으로 `base_sha` 를 대조하기 때문이다.

```bash
"$W/bin/romeo" close --unit <작업 단위 id> --root "$W" --dry-run
"$W/bin/romeo" close --unit <작업 단위 id> --root "$W"
```

`close` 가 받는 플래그는 `--unit`·`--dry-run`·`--root`·`--no-rerun`·`--rerun-timeout` 이다(`--help` 실측).
`--dry-run` 은 판정만 인쇄하고 문서를 고치지 않는다.
`--root "$W"` 를 빼면 위임한 쪽 체크아웃을 검사한다 — 거기에는 이 실행의 evidence 도 `review/` 봉투도 없어 판정이 성립하지 않는다.

관찰 가능한 성공 신호: **종료 코드 0** 과 첫 줄 `romeo close <id> → PASS`, 그리고 각 검사가 `[PASS]` 로 인쇄되는 것.
`[FAIL]` 은 어긴 것이고 **`[UNVERIFIED]` 는 대조가 성립하지 않은 것**이다 — 어느 쪽이든 종료 코드 1 이고 `status: done` 은 붙지 않는다.
미검증을 통과로 접지 않는다(K-51).

**종료 검사는 기록을 믿지 않고 주장을 다시 실행해 대조한다.** 다시 실행되는 것은 `spec.md` 검증 계획의 `required_checks` 명령이다 —
evidence 에 적힌 종료 코드를 읽는 것으로 끝내지 않고, 같은 명령 문자열을 이 체크아웃에서 새로 실행해 그 종료 코드를 기록과 맞춰 본다
(`REQUIRED_CHECK_RERUN`). 그래서 이 단계에는 조건이 넷 붙는다.

- **워크트리가 살아 있어야 한다.** 그러니 §3.9 해제보다 **먼저** 돌린다. 해제는 워크트리를 지우지 않지만(§3.9),
  워크트리를 정리한 뒤에는 재실행할 자리가 없다.
- **재실행이 작업 트리를 바꾸면 안 된다.** 바뀌면 `REQUIRED_CHECK_RERUN` 이
  `재실행이 작업 트리를 바꿨다` 로 **미검증**이 된다 — 재실행 전에 계산한 신선도 판정이 더 이상 그 트리를 말하지 않기 때문이다.
  (`docs/work/<id>/` 와 `.harness/` 는 신선도 계산에서 빠지지만, 그 밖의 산출물은 빠지지 않는다.)
- **검증 계획이 그 체크아웃의 HEAD 에 커밋돼 있어야 한다**(`CHECK_PLAN_COMMITTED`). 지금 읽는 `required_checks` 와
  HEAD 에 커밋된 `spec.md` 의 것이 다르면 FAIL 이다 — 실행할 검사를 바꾸는 것은 증거가 아니라 **주장**을 바꾸는 것이다.
  구현자가 수용 기준 체크박스를 채우는 것은 문제가 없지만(대조는 `id`·`command`·`expect` 만 본다) 검증 계획 자체는 건드리지 않는다.
- **재실행할 수 없는 명령은 막지 않고 드러낸다.** 부작용이 있어 두 번 돌릴 수 없거나 돌릴 때마다 결론이 달라지는 검사는
  검증 계획에서 `rerun: false` 로 선언하고 `rerun_reason` 에 이유를 적는다. 그러면 `재실행으로 확인되지 않았다 (rerun: false — <이유>)` 로
  **미검증** 인쇄되고 통과로 세지 않는다 — close 는 done 을 선언하지 않는다. 대조하지 못했다는 사실을 PASS 로 인쇄하는 것보다 낫다.
  상한 시간(`--rerun-timeout`, 기본 300초)을 넘겨도 같다. `--no-rerun` 도 같다 — 그것은 "기록만 읽은 판정" 이라고 인쇄된다.
  이 세 자리 중 하나라도 걸리면 그 작업 단위는 done 이 되지 않는다. 그게 정직한 결과다.

같은 라운드에 붙은 검사가 하나 더 있다 — `EVIDENCE_LOG` 는 evidence YAML 의 명령들을 `.harness/runs/` 의 원시 로그
(종료 코드 줄 `--- exit N ---` 과 `log_sha256`)와 대조한다. `.harness/` 는 커밋되지 않으므로 **로그가 없는 체크아웃에서는
실패가 아니라 미검증**이다. 그래서 종료 검사는 로그가 남아 있는 그 워크트리에서 돌린다 — 다른 체크아웃에서 돌리면
이 검사가 미검증이 되어 done 이 서지 않는다.

**FRESH_HEAD·FRESH_TREE 때문에 순서가 있다.** 두 검사는 evidence 의 `head_sha`·`dirty_tree_hash` 를 지금의 `$W` 와 대조한다.
§3.8 의 회수·검사가 끝난 뒤 `$W` 를 건드리면 이 둘이 어긋난다. 검토자 판정 파일을 `review/` 에 쓰는 것과 계약을 만드는 것은
`docs/work/<id>/` 안이라 계산에서 빠지지만(`romeo/evidence.py` 의 `exclusions()`), 그 밖의 파일은 빠지지 않는다.

### 3.9 해제

```bash
orca orchestration worker-release --dispatch <dispatch-id> --json
```

성공 신호: `retained` · `release_pending` · `already_released` 는 전부 종료 코드 0 이고, `release_unknown` 만 1 이다(실측 Notes). 반복 호출은 멱등이다.
해제 전에 출력 아카이브가 보존되므로 해제 뒤에도 `worker-read` 는 계속 읽힌다. 그래도 **검증 결과와 결과 계약이 파일로 남은 뒤에** 해제한다.
**§3.8 의 종료 검사까지 끝낸 뒤에 해제한다** — 종료 검사는 기록을 믿지 않고 `required_checks` 를 그 체크아웃에서 다시 실행하므로,
그 체크아웃이 살아 있고 트리가 그대로일 때만 판정이 성립한다. 해제 자체는 워크트리를 지우지 않지만(위 실측),
워크트리 정리(§7 의 `orca worktree rm`, 승인 대상)까지 가 버리면 재실행할 자리가 없다.
`worker-release` 는 setup 터미널·설정된 탭·재사용된 터미널·사람이 넘겨받은 터미널·신원이 증명되지 않은 터미널을 건드리지 않는다.

## 4. 권한 상한을 실제로 거는 명령형

`.harness/bindings.yaml` 이 정본이다. 이 문서는 그 값을 옮겨 적을 뿐이다 — 두 값이 다르면 bindings 가 맞다.

관찰 여부는 두 가지를 따로 묻는다. **단독 프로브**는 그 명령형이 실제로 쓰기를 막는 것을 봤는가이고,
**§3 기동 경로**는 §3 이 실제로 실행하는 형태에 그 명령형이 걸린 것을 봤는가다. 앞이 예여도 뒤가 아니면 §3 은 강제 없이 돈다.

| 실행 | 역할 | 정본 키 | 강제 수단 | 단독 프로브 | §3 기동 경로 |
| --- | --- | --- | --- | --- | --- |
| 기본 | 검토자 | `roles.reviewer.enforcement` | `-s read-only` | 예 | **예 — 2026-08-29 관통** (§4 방어 검사가 `유효`) |
| 교체 | 검토자 | `parity_swap.reviewer.enforcement` | `claude -p --tools "Read" "Grep" "Glob" --allowedTools "Read" "Grep" "Glob" --strict-mcp-config` | 예 | 같은 관통의 교체 실행에서 방어 검사로 판정 |
| 기본 | 구현자 | `roles.implementer.enforcement` | `.claude/settings.json` 의 `permissions.ask`·`deny` | **아니오** | **아니오** |
| 교체 | 구현자 | `parity_swap.implementer.enforcement` | `-s workspace-write` | **부분** — 아래 | **부분** — 아래 |

검토자 두 행의 앞칸이 `예` 인 것은 `.harness/bindings.yaml` 의 `enforcement_observed: true` 와 같은 관찰이다 —
빈 디렉터리에 파일 생성을 지시한 단독 프로브였다.

**기본 검토자의 오른쪽 칸이 `예` 로 바뀐 근거**(2026-08-29): §3.7 로 기동한 검토자가 도는 동안
§4 의 방어 검사가 `유효` 를 냈다 — `review-tree-before` 와 `review-tree-after` 의 `log_sha256` 이 같은 값
(`2bc7dad48f31…`)이었다. 검토자가 그 워크트리에서 아무것도 바꾸지 않았다는 뜻이다. 이것은 **강제가 작동했다는 사후 확인**이지
강제 그 자체가 아니다 — 검토자가 쓰기를 시도했다가 막힌 것을 본 것은 단독 프로브 쪽이다.

**교체 구현자가 `부분` 인 이유 — 샌드박스는 걸렸지만 무엇을 막는지는 절반만 봤다.**
`codex -s workspace-write` 로 띄운 워커가 `orca orchestration send --type worker_done` 을 실행하자
`runtime_unavailable: Could not connect to the running Orca app.` 로 실패했다. 같은 명령이 위임한 쪽 셸에서는
정상 동작하므로, 이것은 **그 샌드박스가 실제로 프로세스에 적용됐다는 관측**이다(작업 공간 밖 IPC 를 막았다).
그러나 이 관통이 보지 못한 것이 둘 있다 — (a) 작업 공간 **밖 파일 쓰기**를 막는지, (b) 승인 대상 명령을 막는지.
두 구현자 모두 승인 대상 명령을 시도하지 않았으므로 그 칸은 여전히 미관측이다.

**그리고 이 관측은 대가를 드러낸다.** 구현자에게 샌드박스 강제를 걸면 그 워커는 오케스트레이터에게 보고할 수 없다 —
`worker_done`·heartbeat·`ask` 가 전부 같은 IPC 를 쓰기 때문이다. 그때 Task 는 스스로 완료되지 못하고
위임한 쪽이 `worker-abandon` → `task-update --status completed` 로 정리해야 한다(실측 경로).
`worker-stop` 은 `terminal create` 로 만든 터미널을 "external" 로 보아 정리하지 못한다
(`stop_unknown` · `The worker terminal is external; no terminal was closed.`).
즉 **강제와 lifecycle 은 이 조합에서 동시에 성립하지 않는다.** 어느 쪽을 포기할지는 역할 바인딩의 결정이고,
포기한 쪽은 `enforcement_observed` 와 이 문단이 드러낸다.
오른쪽 칸이 전부 `아니오` 인 지금, 강제가 실제로 걸렸는지 아는 유일한 수단은 아래 방어 검사다.
승인 대상 명령 목록(`permission_ceiling`)은 역할이 아니라 실행에 붙는다. 어느 런타임이 구현자든 같은 목록이 걸려야 한다(K-66).

기본 실행에서 검토자가 실행되는 형태다. 이 명령형은 §3.7 (1) 의 `orca terminal create --command` 에 그대로 들어가고,
(2) 가 그 터미널을 워커로 채택한다 — `worker-start --agent` 로는 이 형태가 만들어지지 않는다.

```bash
T=<§3.5.1 이 구현자 워크트리 안에 실재시킨 검토자 계약의 절대경로>   # $W/docs/work/<id>/task/<run-id>-reviewer.json

codex exec -s read-only -C <검토 대상 워크트리 절대경로> \
  --output-schema $W/core/schemas/result-envelope.json \
  -o <위임한 쪽이 지정한 파일> \
  "$(cat "$T")"
```

`-s` 는 **모델이 만든 셸 명령**에 적용되는 샌드박스 정책이고(`codex exec --help` 문구 그대로), 허용값은 `read-only`·`workspace-write`·`danger-full-access` 다. `-C/--cd` 는 작업 루트, `--output-schema <FILE>` 은 최종 응답 형태를 강제하는 JSON Schema 파일, `-o/--output-last-message <FILE>` 은 마지막 메시지를 떨어뜨릴 파일이다. `-o` 의 대상 경로는 검토자가 고르는 것이 아니라 위임한 쪽이 고른다.

역할을 교체하면 검토자가 다른 런타임이 된다(§6). 그쪽의 형태는 다음이다.

```bash
claude -p --tools "Read" "Grep" "Glob" --allowedTools "Read" "Grep" "Glob" --strict-mcp-config \
  --json-schema "$(cat "$W/core/schemas/result-envelope.json")" \
  --output-format json "$(cat "$T")"
```

플래그 **셋을 다 준다.** 프로브 3회 결과다(`.harness/bindings.yaml` 의 `parity_swap.reviewer.enforcement_note`):
`--allowedTools` 만 주면 쓰기 도구가 목록에 남아 비대화형이라 승인을 못 받아 실패할 뿐이고(약한 보장),
`--tools` 를 더하면 내장 쓰기 도구는 사라지지만 외부 연결 도구가 남는다. 셋을 다 준 실행에서만
사용 가능한 도구가 `Read`·`Grep`·`Glob` 3개로 관찰됐고 파일은 생성되지 않았다.
`--json-schema` 는 도움말 예시가 인라인 JSON 이므로 파일 경로 대신 내용을 넣어 전달한다.

**방어 검사 — 강제가 실패했을 때 그것을 아는 방법.** 강제 수단이 아니라 사후 확인이다(리뷰 F-03).
**이 검사를 돌리는 것은 검토자를 띄운 쪽이다 — 검토자가 아니다.** 검토자의 역할 계약에는 명령 실행 능력이 없고
(`core/roles/reviewer.yaml` 의 `capabilities: [read, search]`), 자기가 만든 산출물로 자기 판정의 유효성을 증명할 수도 없다
(`core/workflows/review/SKILL.md` 6번).
검사 산출물은 손으로 만들지 않는다. 셸 리다이렉션으로 만든 파일은 명령·종료 코드·HEAD SHA 가 남지 않고(K-51),
git 제외 경로에 떨어져 종료 검사가 인정하지도 않는다(K-62). 증거 기록 명령으로만 만든다.

```bash
W=<구현자 워크트리 절대경로>          # 검토 대상이자 evidence 를 남길 작업 공간

# 검토자 기동 직전
bin/romeo evidence run --unit <id> --run <run-id> --root "$W" --label review-tree-before -- \
  git status --porcelain -- . "':(exclude).harness'" "':(exclude)docs/work/<id>'"

# ... §3.7 검토자 기동 → 종료 ...

# 검토자 종료 직후
bin/romeo evidence run --unit <id> --run <run-id> --root "$W" --label review-tree-after -- \
  git status --porcelain -- . "':(exclude).harness'" "':(exclude)docs/work/<id>'"
```

두 실행에 대한 설명이 필요하다.

- 디렉터리를 미리 만들지 않는다. `.harness/runs/<id>/<run-id>/` 는 `evidence run` 이 스스로 만든다 —
  셸 리다이렉션은 그렇지 않아서 검토자 기동 직전에는 항상 "그런 파일이나 디렉터리가 없다" 로 실패했다.
- 제외 경로 두 개는 하네스가 신선도 계산에서 이미 빼는 것과 같다(`romeo/evidence.py` 의 `exclusions()`).
  증거 기록 자체가 `docs/work/<id>/evidence/` 와 `.harness/runs/` 를 건드리므로, 빼지 않으면 "이전" 과 "이후" 가
  검토자와 무관한 이유로 달라진다.
- 따옴표를 두 겹으로 쓴다. 이 명령은 문자열로 이어 붙여 셸에 다시 넘겨지므로 `:(exclude)...` 의 괄호가
  그대로 남으면 셸 문법 오류가 난다(실측: 따옴표 없이 쓰면 `syntax error near unexpected token '('` · exit 2).

판정은 evidence 에 기록된 해시로 한다. 두 실행의 명령 문자열이 같으므로, 로그 본문이 같으면 `log_sha256` 도 같다.

```bash
python3 - "$W/docs/work/<id>/evidence/<run-id>.yaml" <<'PY'
import sys, yaml
rec = yaml.safe_load(open(sys.argv[1]))
h = {c["id"]: c["log_sha256"] for c in rec["commands"]
     if c["id"] in ("review-tree-before", "review-tree-after")}
ok = len(h) == 2 and len(set(h.values())) == 1
print(h)
print("유효" if ok else "무효 — 검토자 실행 중 작업 트리가 바뀌었다")
sys.exit(0 if ok else 1)
PY
```

성공 신호: 종료 코드 0 과 `유효`. 두 실행 중 하나라도 없으면 종료 코드 1 이다 — 안 돌린 것을 통과로 세지 않는다.
`무효` 면 그 판정은 무효다. 결과 계약을 `review/` 에 기록하지 않고, 무엇이 바뀌었는지와 함께 사람에게 보고한다.
검토자가 만든 변경을 임의로 되돌리지 않는다 — 되돌리기는 삭제이고 삭제는 승인 대상이다(K-66).

## 5. evidence 에 남길 식별자

`run_id` · `task_id` · `dispatch_id` 세 개만 남긴다. 실행 상태 자체(재시도·터미널 생존·큐)는 하네스가 저장하지 않는다 — 오케스트레이터가 소유한다(K-63).
세 값을 넣는 플래그는 `evidence` 의 세 하위 명령에 모두 있다(`--help` 실측).

```bash
bin/romeo evidence run     --unit <id> --run <run-id> --task-id <task-id> --dispatch-id <dispatch-id> --label <이름> -- <명령>
bin/romeo evidence checks  --unit <id> --run <run-id> --task-id <task-id> --dispatch-id <dispatch-id>
bin/romeo evidence approve --unit <id> --guard <가드 id> --by <승인자> --note "<영향 범위·복구 방법>" --run <run-id> --task-id <task-id> --dispatch-id <dispatch-id>
```

- `--run` 은 evidence 파일 이름이자 `run_id` 다. **위임 실행이면 §3.2 의 Run id 를 그대로 넣는다.**
  생략하면 날짜 이름(`run-YYYYMMDD`)이 붙어 작업 계약·결과 계약의 `<run-id>` 와 다른 이름 공간이 된다.
  같은 값을 쓰면 `task/<run-id>-<role>.json` · `evidence/<run-id>.yaml` · `result/<run-id>-implementer.json` 이 한 이름으로 묶인다.
- `--task-id`·`--dispatch-id` 는 **그 evidence 를 남기는 워커의** 값이다 — 한 run 의 evidence 는 한 위임에 속하므로,
  구현자 run 에는 §3.4 의 구현자 task id 와 §3.5 의 구현자 dispatch id 두 값만 들어간다. 검토자는 명령을 실행하지 않아
  자기 run 이 없고(`core/workflows/review/SKILL.md` 6번), §4 의 방어 검사는 위임한 쪽이 두 식별자 없이 남긴다.
  검토자 dispatch 를 추적해야 하면 `orca orchestration dispatch-show --task <reviewer-task-id> --json`(실측: 존재)으로 보고,
  evidence 에는 넣지 않는다.
- 두 식별자는 run 당 한 번만 기록된다. 이미 다른 값이 있으면 덮어쓰지 않고 **종료 코드 1 로 거부**한다 —
  한 run 이 두 위임에 속한 것처럼 보이면 그 증거의 출처를 알 수 없기 때문이다. 다른 위임이면 `--run` 으로 새 run 을 만든다.
- 값은 `docs/work/<id>/evidence/<run-id>.yaml` 의 `run_id`·`task_id`·`dispatch_id` 에 들어가고, 원시 로그는 `.harness/runs/<id>/<run-id>/`(git 제외)에 남는다.

## 6. 역할 교체 재실행 (parity)

동등성 게이트는 **같은 작업 단위를 역할 바인딩만 바꿔 두 번** 돌려 같은 판정이 나오는지로 판정한다(D-68).

1. 기준 실행: `.harness/bindings.yaml` 의 `roles` 조합으로 §3 을 끝까지 돌린다.
2. 교체 실행: 같은 `<base-sha>`, 새 Run 과 새 자식 워크트리에서 **역할 바인딩만** `parity_swap.<role>` 로 바꿔 §3.2 부터 다시 돌린다 —
   구현자는 §3.5 의 `--agent` 값이, 검토자는 §3.7 (1) 의 `--command` 안 강제 수단 문자열이 바뀌는 자리다.
   검토자를 `--agent` 로 띄우는 경로는 교체 실행에서도 쓰지 않는다(§2 표 · §3.7 · §10).
   승인 커밋(§3.1)은 다시 하지 않는다 — 같은 커밋을 가리켜야 두 실행이 같은 것을 본다.
   작업 계약은 `--run` 이 달라 파일 이름이 다르지만, `--base-sha` 가 같으므로 **내용은 바이트까지 같다**. 다르면 그 비교는 성립하지 않는다.
3. **결과 계약 4개(기준 2 + 교체 2)를 한 체크아웃으로 모은다.** 이 단계를 빼면 뒤가 전부 실행 불가다 —
   4개는 서로 다른 두 자식 워크트리에 흩어져 있는데, 동등성 검사기는 **한 `project_root` 아래에서만** 파일을 찾는다
   (`romeo/parity.py` 의 `_repo_path` 는 저장소 안의 상대 경로만 앵커로 인정한다).
4. **관측 케이스를 등록한다.** 게이트는 케이스 파일을 통해서만 관측을 센다 — 모아 두기만 하면 게이트는 계속 미판정이다.
5. **판정을 실행한다.** 판정은 하네스의 동등성 검사기가 한다 — 사람이 눈으로 비교하지 않는다.
   검사기는 손으로 쓴 합성 케이스로 자기 자신만 검증한다. 게이트를 판정하려면 위 1~4 에서 나온 **관측 케이스가 1건 이상** 있어야 한다(D-b).

비교하는 것은 세 가지뿐이다: 결과 계약이 스키마를 통과하는가 · 같은 `required_checks` 를 실행했는가 · 같은 게이트 판정이 나왔는가. 프롬프트 동일성은 요구하지 않는다(C-C2).
교체 실행은 기준 실행의 워크트리를 재사용하지 않는다. 재사용하면 두 번째 실행이 첫 번째의 변경 위에서 돌아 같은 `base_sha` 라는 전제가 깨진다.

**검토자 면에는 전제가 하나 더 있다 — 두 검토자가 같은 산출물을 봤는가(D-73).** 두 구현자는 같은 계약에서도 다른 바이트를 만든다 —
그것은 정상이고 구현자 면은 계약·checks·판정만 비교한다. 그런데 검토자의 판정은 자기가 본 산출물의 함수라서, 산출물이 다르면
판정이 갈리는 것이 옳고 그 차이는 런타임의 차이를 말하지 않는다. 검사기는 검토자 봉투가 지목한 증거의 `head_sha`·`dirty_tree_hash`
(각 실행의 evidence YAML — 손으로 적지 않는다)를 두 면에서 읽어, 다르면 검토자 면을 `PRODUCT_DIFFERS` 로 분리해 **판정에서 빼고
'비교 불가' 로 인쇄한다.** 2026-08-29 관통이 정확히 이 경우였다. 이때 게이트는 구현자 면으로만 서고 리포트가 그 사실을 적는다 —
검토자 동등성을 판정하려면 **같은 산출물을 두 검토자에게 보인 관측**이 따로 필요하다(§6.6).

**여기서 비교하는 `required_checks` 는 두 실행의 주장이다.** 그 주장이 실제 실행과 맞는지는 §3.8 의 종료 검사가 재실행으로 대조한다 —
동등성 게이트와 종료 검사는 서로를 대신하지 않는다. 같은 거짓을 두 번 적으면 양면이 같아지므로, 동등성만으로는 참이 되지 않는다.

#### 6.3 모으기 — 어디로, 무엇을

모으는 자리는 **`fixtures/parity/` 가 있는 체크아웃**이다. 관측 케이스 파일이 거기 놓여야 하고,
케이스 목록은 `--root` 가 아니라 **호출된 `bin/romeo` 의 저장소**에서 읽히기 때문이다(`romeo/cli.py` 의
`load_parity_cases(HARNESS_ROOT/"fixtures/parity")`). 두 값을 같은 체크아웃으로 맞춘다.

모으는 것은 **실행이 남긴 산출물 3종뿐**이다. 작업 계약은 복사하지 않고 그 자리에서 다시 만든다(계약은 결정적이다 — §3.3).

```bash
P=<위임한 쪽 체크아웃 절대경로>          # fixtures/parity/ 가 있는 곳
U=docs/work/<작업 단위 id>
W1=<기준 실행의 구현자 워크트리>;  R1=<기준 실행 Run id>
W2=<교체 실행의 구현자 워크트리>;  R2=<교체 실행 Run id>

mkdir -p "$P/$U/evidence" "$P/$U/result" "$P/$U/review"
cp "$W1/$U/evidence/$R1.yaml"           "$P/$U/evidence/$R1.yaml"
cp "$W1/$U/result/$R1-implementer.json" "$P/$U/result/$R1-implementer.json"
cp "$W1/$U/review/$R1-reviewer.json"    "$P/$U/review/$R1-reviewer.json"
cp "$W2/$U/evidence/$R2.yaml"           "$P/$U/evidence/$R2.yaml"
cp "$W2/$U/result/$R2-implementer.json" "$P/$U/result/$R2-implementer.json"
cp "$W2/$U/review/$R2-reviewer.json"    "$P/$U/review/$R2-reviewer.json"
```

두 실행의 Run id 가 달라서(§6 2번) 파일 이름이 겹치지 않는다 — 같은 Run id 로 두 번 돌렸다면 여기서 서로를 덮어쓴다.
`cp` 는 덮어쓰기이므로 모으기 전에 `R1 != R2` 를 눈으로 확인한다.

작업 계약은 그 자리에서 다시 만든다. 복사하지 않는 이유는 §3.5.1 과 같다 — 앵커는 커밋된 원본에서 **다시 계산해** 바이트로 대조하므로,
다른 하네스 커밋에서 만든 계약을 복사해 두면 지금 여기서 그것이 드러난다.

```bash
for R in "$R1" "$R2"; do
  "$P/bin/romeo" envelope build --unit <작업 단위 id> --role implementer --base-sha <base-sha> --run "$R" --root "$P"
  "$P/bin/romeo" envelope build --unit <작업 단위 id> --role reviewer    --base-sha <base-sha> --run "$R" --root "$P"
done
```

모은 4개가 앵커 검사를 통과하는지 **여기서** 본다. 통과하지 못하는 봉투는 관측으로 세지 않으므로(`_resolve_face`),
케이스를 등록한 뒤에 알면 원인이 케이스인지 봉투인지 구분되지 않는다.

```bash
"$P/bin/romeo" envelope check --unit <작업 단위 id> --role implementer --root "$P" \
  "$P/$U/result/$R1-implementer.json" "$P/$U/result/$R2-implementer.json"

"$P/bin/romeo" envelope check --unit <작업 단위 id> --role reviewer --root "$P" \
  "$P/$U/review/$R1-reviewer.json" "$P/$U/review/$R2-reviewer.json"
```

관찰 가능한 성공 신호: 두 줄 모두 **종료 코드 0** 이고 파일마다 다섯 검사가 전부 `[PASS]` 다.
**2 는 검사 불가**이지 통과가 아니다(§3.8). `[FAIL]` 이 났을 때의 뜻:

| 검사 | 무엇이 어긋났나 | 무엇을 한다 |
| --- | --- | --- |
| `TASK_ANCHORED` … `바이트로 다르다` | `$P` 의 하네스(정책표·역할 계약·스키마·`.harness/romeo.project.yaml`)가 계약을 만들 때와 다르다 | `$P` 를 그 리비전 상태로 맞추거나, `orca worktree create --base-branch <승인 커밋이 tip 인 브랜치>` 로 그 리비전의 체크아웃을 만들어 거기로 모은다. raw `git worktree add` 는 쓰지 않는다(§10) |
| `BASE_SHA` | `<base-sha>` 가 `$P` 의 HEAD 이력에 없다 | 승인 커밋이 이력에 있는 브랜치에서 모은다 |
| `EVIDENCE_ANCHORED` | evidence YAML 을 빠뜨렸거나 다른 자리에 놓았다 | 위 `cp` 3줄 중 evidence 줄을 확인한다 |

#### 6.4 등록 — 관측 케이스 파일

자리표가 이미 있다: `fixtures/parity/pr-license-field-t1-observed.yaml`. 새 파일을 만들지 말고 그것을 채운다.
**봉투를 인라인으로 적지 않는다** — 게이트가 비교하는 값을 케이스 작성자가 타이핑할 수 있으면 게이트는 아무것도 지키지 않는다(D-b).
한 역할은 `{file: <상대 경로>}` 한 줄만 받는다.

```yaml
id: pr-<케이스 이름>-observed          # ^pr-[a-z0-9]+(-[a-z0-9]+)*$
title: <작업 단위 한 줄 설명> — 실제 교차 실행 관측
unit_id: <실제 T1 작업 단위 id>        # docs/work/ 에 실재해야 한다. 자리표의 값이 아니다
status: executed                       # pending 이 아니다. pending_reason 줄은 지운다
expect: same

baseline:
  runtimes: {implementer: <기준 구현자 런타임>, reviewer: <기준 검토자 런타임>}
  results:
    implementer: {file: docs/work/<작업 단위 id>/result/<R1>-implementer.json}
    reviewer:    {file: docs/work/<작업 단위 id>/review/<R1>-reviewer.json}
swapped:
  runtimes: {implementer: <교체 구현자 런타임>, reviewer: <교체 검토자 런타임>}
  results:
    implementer: {file: docs/work/<작업 단위 id>/result/<R2>-implementer.json}
    reviewer:    {file: docs/work/<작업 단위 id>/review/<R2>-reviewer.json}

source:
  kind: observed                       # planned 가 아니다 — 이 한 단어가 게이트를 여는 열쇠다
  ref: docs/work/<작업 단위 id>/evidence/<R1>.yaml   # 저장소 안의 실재 파일이어야 한다
  date: '<YYYY-MM-DD>'
```

`source.kind: observed` 로 바꾸면 검사기가 **관측물의 실재**를 함께 검사한다(`_anchor_errors`) —
`source.ref` 가 실재 파일이 아니거나 `unit_id` 가 `docs/work/` 에 없으면 미판정이 아니라 **구조 오류**(`PARITY_INVALID`)다.
`runtimes` 는 판정에 쓰이지 않는다 — 어느 런타임이 어느 역할을 맡았는지 사람이 읽는 기록이다.

**하네스는 이것들을 커밋하지 않는다.** 모아 온 산출물과 채운 케이스 파일을 커밋할지, 어느 브랜치에 올릴지는 사람이 정한다(§3.1 과 같은 이유).
커밋 전에도 `fixtures parity` 는 작업 트리를 읽으므로 판정은 난다 — 다만 커밋하지 않으면 그 관측은 다음 체크아웃에 남지 않는다.

#### 6.5 판정

```bash
"$P/bin/romeo" fixtures parity --report
```

관찰 가능한 성공 신호: **종료 코드 0** 과 게이트 줄
`핵심 동등성 게이트: PASS — 관측 1건으로 판정했다`, 그리고 그 앞줄의 `검사기 자기 검증: PASS`.
**두 층이 다 서야 종료 코드 0 이다** — 게이트가 관측으로 PASS 여도 검사기 자기 검증이 서지 않으면 1 이고, 리포트가 그 사실을 인쇄한다.
`핵심 동등성 게이트: 미판정 — 관측 케이스 0건` 이 계속 나오면 6.4 의 `status`·`source.kind` 둘 중 하나가 아직 자리표 값이다.

게이트 줄 다음에 `비교 불가 — 관측 케이스의 N개 면을 판정에서 뺐다(D-73)` 가 붙으면 **그 PASS 는 부분이다** — 표의 판정 칸도
`✓ 부분` 이다. 뺀 면(검토자)은 두 실행의 산출물이 달라 비교하지 못한 것이고, 그 역할의 동등성은 이 관측으로 증명되지 않았다.
`핵심 동등성 게이트: 미판정 — 관측 N건이 전부 비교 불가다` 는 비교할 면이 하나도 남지 않은 경우다(예: 검토자 면만 있는 관측).

#### 6.6 검토자 면을 판정하려면 — 같은 산출물을 두 검토자에게

산출물이 다른 두 관통으로는 검토자 면이 영원히 비교 불가다. 검토자 동등성의 관측은 **산출물을 고정**해야 나온다:
기준 실행의 구현자 워크트리(`$W1`)를 그대로 두고, 그 위에서 **검토자만** 교체 바인딩으로 한 번 더 띄운다(§3.7 의 절차 · 새 Run id ·
같은 `<base-sha>`). 그 검토자의 봉투가 지목할 증거는 `$W1` 의 evidence 라야 하고(그래야 `head_sha`·`dirty_tree_hash` 가 같다),
§4 의 `review-tree-before`/`after` 로 검토 중 트리가 바뀌지 않았음을 같은 evidence 에 남긴다. 이 절차는 **아직 실행한 적이 없다**(§11.2).

`--root` 는 스키마와 앵커를 찾는 루트이고, 케이스 목록은 호출된 `bin/romeo` 의 저장소에서 읽는다 —
그래서 위 명령은 `$P/bin/romeo` 로 부른다. 두 값이 갈리면 "케이스는 여기 있는데 관측물은 저기 있다" 가 된다.

## 7. 실패와 복구 — 남는 상태를 어떻게 정리하는가

`worker-start` 가 1 로 끝났다면 JSON 의 `residualResources` 와 복구 명령을 먼저 읽는다. 그 다음 상태를 눈으로 확인한다.

```bash
orca orchestration worker-list --run <run-id> --json
orca orchestration worker-list --run <run-id> --terminal-state active --json
orca orchestration task-list --run <run-id> --brief --json
orca worktree list --json
```

터미널 상태 값은 `active`·`reclaimable`·`retained`·`release_pending`·`release_unknown`·`released` 다(실측). 터미널 상태는 프로세스 회계이고 Task 상태와 별개다 — 완료된 Task 가 살아 있는 터미널을 가질 수 있다.

| 남은 상태 | 명령 | 무엇을 보장하나 |
| --- | --- | --- |
| 워커가 멈추지 않는다 | `orca orchestration worker-stop --dispatch <id> --json` | Dispatch 를 봉하고 그 워커 터미널만 멈춘다. **워크트리·setup 터미널·다른 프로세스는 지우지 않는다**(실측 Notes) |
| 멈췄는지 증명할 수 없다 | `orca orchestration worker-abandon --dispatch <id> --json` | 봉하기만 한다. 살아 있을 수 있는 자원을 그대로 두고 프로세스·파일 조작을 하지 않는다 |
| 디버깅하려고 살려둔다 | `orca orchestration worker-retain --dispatch <id> --json` | 해제 예외를 기록한다. 이후 명시적 `worker-release` 가 예외를 지우고 해제한다 |
| 터미널만 남았다 | `orca orchestration worker-release --dispatch <id> --json` | 멱등. `release_unknown` 만 1 |
| Task 상태가 실제와 다르다 | `orca orchestration task-update --id <task-id> --status failed --json` | 상태 값은 `pending`·`ready`·`dispatched`·`completed`·`failed`·`blocked` |
| 고아 워크트리가 남았다 | `orca worktree rm --worktree id:<repoId>::<절대경로> --json` | **승인 대상이다**(§9). 사람의 승인 전에는 실행하지 않는다 |
| 오케스트레이션 상태를 비운다 | `orca orchestration reset --tasks` / `--messages` / `--all` | **승인 대상이다**(§9). 되돌릴 수 없다 |

재시도는 `worker-start --retry-of <이전 dispatch_id>` 로 연결한다. `--retry-of` 는 배치를 물려받지 않으므로 `--worktree`·`--agent` 선택을 다시 적어야 한다(실측 Notes).
실패한 실행의 증거는 지우지 않는다. 실패도 관찰 결과이고, `.harness/runs/` 의 로그가 다음 판단의 근거다.

## 8. 승인이 필요할 때

M2 에서는 대화 승인을 증거로 기록한다.

```bash
bin/romeo evidence approve --unit <작업 단위 id> --guard <가드 id> --by <승인자> --note "<영향 범위·복구 방법>" --run <run-id>
```

승인 전 상태 변경 0건이다. **선행 실행이 없어도 이 명령은 동작한다** — 그 `--run` 의 레코드가 없으면
`commands: []` 인 승인 전용 레코드를 만든다. 승인 시점에 실행한 명령이 0건이라는 사실 자체가 '승인 전 상태 변경 0건' 의 증거다.
같은 `--run` 을 계속 쓰면 이후 `evidence run`·`evidence checks` 가 같은 레코드에 붙는다.

성공 신호: 종료 코드 0 과 `approval recorded → .../docs/work/<id>/evidence/<run-id>.yaml`.
그 파일의 `approvals[]` 에 `guard`·`approved_at`·`approved_by`·`note` 가 들어간다.
승인 없이 실행하면 `BLOCKED_APPROVAL` 로 끝내고 증거를 무효로 본다(`core/policy/execution-guards.yaml`).
종료 검사의 `GUARD_APPROVED` 는 라우터가 건 가드마다 이 기록을 찾는다 — 없으면 close 가 FAIL 이다.
설명해야 하는 네 가지는 영향 범위 · 사전 백업 · 복구 방법 · 확인할 내용이다.

**M3 범위.** 승인을 오케스트레이션 상태로 올리는 경로는 다음이다. M2 에서는 쓰지 않는다.

```bash
orca orchestration gate-create --task <task-id> --question "<설명>" --options '["approve","reject"]' --json
orca orchestration gate-resolve --id <gate-id> --resolution "<사람의 답>" --json
orca orchestration gate-list --json
```

## 9. 승인 없이 실행하지 않는 명령

`.harness/bindings.yaml` 이 정본이고, 그 안의 `permission_ceiling` 이 실행 전체에 걸리는 상한이다.
이 상한은 역할이 아니라 실행에 붙는다 — 역할 교체로 구현자가 바뀌어도 같은 목록이 걸려야 한다.
이 런북은 아래 명령을 **제시만** 하고 실행하지 않는다(K-66).

`permission_ceiling.approval_required`(승인 뒤에만):
`git push` · `gh pr create` · `gh pr merge` · `git worktree add` · `git worktree remove` · `git worktree prune` ·
`git branch -D` · `git reset --hard` · `git stash` · `gh api` · `gh pr comment` · `gh pr review`

`permission_ceiling.never`(승인으로도 정당화되지 않는다):
`rm -rf /` · `rm -rf ~` · `sudo rm` · `git push --force`

부품 원문을 덮는 `overrides` 쪽 목록(`integration_commands`·`external_writes`)은 위 상한의 부분집합이다.

이 런북이 다루는 명령 중 위와 같은 가드에 걸리는 것:

| 명령 | 걸리는 가드 |
| --- | --- |
| `orca worktree rm` | `workspace-deletion` (다른 작업 공간 삭제) — `git worktree remove` 와 같은 행동이다 |
| `orca orchestration reset --all` / `--tasks` / `--messages` | `deletion` (삭제) — 되돌릴 수 없다 |

`worker-stop`·`worker-abandon`·`worker-release` 는 워크트리와 파일을 지우지 않으므로(실측 Notes) 승인 대상이 아니다. 다만 사람이 넘겨받은 터미널을 끊지 않는지 `worker-show` 로 먼저 확인한다.

## 10. 하지 않는 것

- 위임 계층이 `required_checks` 를 대신 실행하고 통과했다고 말하는 것. 검사는 워커 안에서 증거 기록 명령으로만 돌린다(K-51).
- `--model`·`--effort` 를 지정해 계정 기본값을 우회하는 것(K-12).
- 검토자 워커에 쓰기 권한을 주는 것. 다른 리비전이 필요하면 `orca worktree create` 로 새 작업 공간을 만든다 — raw `git worktree add` 는 쓰지 않는다.
- 검토자를 `worker-start --agent` 로 띄우는 것. 그 경로에는 강제 수단을 넣을 자리가 없다 — §3.7 의 2단계로만 띄운다.
- 방어 검사를 검토자에게 시키는 것. 검토자는 명령을 실행하지 않고, 자기 산출물로 자기 판정의 유효성을 증명할 수도 없다(`core/workflows/review/SKILL.md` 6번).
- 승인 커밋에 `spec.md` 만 넣는 것. 워커가 실행할 하네스가 그 커밋에 없으면 워커의 첫 명령이 실패한다(§3.1).
- 실패·질문·시간 초과를 성공으로 간주하는 것.
- 작업 계약 JSON 을 손으로 쓰는 것. 계약은 `bin/romeo envelope build` 만 만든다 — 손으로 쓰면 "같은 입력이면 같은 계약" 이 성립하지 않는다(§3.3).
- 검사 결과 파일을 셸 리다이렉션으로 만드는 것. 증거는 증거 기록 명령으로만 만든다(K-51 · §4).
- 승인된 `spec.md` 를 커밋하지 않은 채 워커를 띄우는 것. 그 워커는 승인을 보지 못한다(D-a · §3.1).
- 위임 식별자를 자리표로 적어 `--spec` 에 넘기는 것. `<dispatch-id>` 는 기동 뒤에 생긴다 — 없는 값을 적으면 그 문자열이 그대로 증거에 남는다(§3.4 · §3.5.2).
- 기록된 종료 코드만 읽고 완료를 주장하는 것. 종료 검사는 그 주장을 **다시 실행해** 대조한다(§3.8).
- 다시 실행할 수 없는 명령(부작용·비결정·상한 시간 초과)을 `required_checks` 에 넣는 것. 그런 단계는 가드 승인(§8)과 증거로 남긴다.
- 결과 계약을 한 체크아웃으로 모으지 않은 채 동등성 게이트를 말하는 것. 모으고 등록하지 않으면 관측 케이스가 생기지 않고 게이트는 계속 미판정이다(§6.3·§6.4).

## 11. 관측된 것과 아직 미검증인 것

2026-08-29 에 이 문서의 §3 을 **두 번 관통했다** — 기준 실행(구현자 claude · 검토자 codex)과
역할 교체 실행(구현자 codex · 검토자 claude). 아래 목록은 그 실행 전후로 나뉜다.
`관측` 은 실행해서 봤다는 뜻이고, `미검증` 은 아직 실행으로 확인하지 못했다는 뜻이다(K-51).

### 11.1 관측된 것 (2026-08-29 관통)

| 무엇 | 관측 결과 |
| --- | --- |
| `run-create` 반환 구조 | `.result.run.id` = `run_<12hex>` |
| `task-create` 반환 구조 | `.result.task.{id,status,task_title,spec}` · `--deps` 를 준 태스크는 `status: pending`, 의존 없는 쪽은 `ready` |
| `worker-start` 반환 구조 | `.result.{dispatchId,state,stage,setup,launch,timeoutMs,effects,residualResources}`. **자식 워크트리 경로는 `effects[]` 의 `kind: worktree` 행 `id` 에 `<repoId>::<절대경로>` 로 실린다** |
| `terminal create` 반환 구조 | `.result.terminal.handle` = `term_<uuid>` (§3.7) |
| `terminal wait` 반환 구조 | `.result.wait.{satisfied,status,exitCode}` |
| `worker-read` 반환 구조 | `.result.{source,provider,transcript.messages[],cursor,fallbackReason}`. 훅 transcript 가 있으면 `source: "transcript"` |
| `check --wait` 반환 구조 | `.result.{deliveryId,messages[],count,timedOut,acknowledged}` · `worker_done` 의 `payload` 에 `taskId`·`dispatchId`·`outcome`·`filesModified` |
| `worker-release` | `retained` 로 종료 코드 0 — 워크트리는 지워지지 않는다 |
| `--base-branch` | 브랜치 이름을 받는다. 기동 뒤 자식 워크트리의 `head` 가 `<base-sha>` 와 일치했다 |
| **§3.5.2 의 식별자 전달이 워커에 닿는가** | **닿는다.** 두 실행 모두 워커의 evidence 에 `run_id`·`task_id`·`dispatch_id` 세 값이 그대로 기록됐고 §3.8 의 식별자 검사가 `일치` 를 냈다. TUI 로 띄운 워커에도 닿았다 |
| **종료 검사의 재실행 대조** | **성립한다.** `REQUIRED_CHECK_RERUN` 5건이 자식 워크트리에서 전부 재실행돼 기록과 일치했고, 재실행이 트리를 바꾸지 않았다. `EVIDENCE_LOG` 는 `.harness/runs/` 원시 로그와 14건을 대조해 PASS — 로그가 남아 있는 그 워크트리에서 돌렸기 때문이다 |
| **§3.1 의 (a)·(b) 가 실제 위임 실행에서 걸리는가** | **걸린다.** 두 체크아웃이 갈라진 상태에서 `REVIEW_TASK_ANCHORED`·`REVIEW_BASE_SHA`·`REVIEW_EVIDENCE_ANCHORED`·`REVIEW_ROLE_CONTRACT` 가 전부 PASS 로 인쇄됐다 — 실물 검토자 봉투로 이 앵커들이 작동한 첫 관측이다 |
| **`--output-schema` 로 이 저장소의 스키마를 넘길 수 있는가** | **없다.** HTTP 400 — `anyOf` 의 빈 하위 스키마 때문이다. §2 의 경고 문단 참조 |
| **`-o` 가 read-only 아래에서 파일을 쓰는가** | **쓴다.** 검토 대상 워크트리 **밖** 경로(`/private/tmp/...`)에 855바이트를 썼다. 샌드박스는 모델이 만든 셸 명령에만 걸리고 CLI 자신의 출력 파일에는 걸리지 않는다 |
| **`worker-start --terminal` 이 비대화형 실행을 워커로 채택하는가** | **못 한다.** `codex exec` → `state: failed` · `stage: dispatch_input` · `last_failure: agent_prompt_stalled`. TUI(`codex -s read-only`) → `state: ready` · `stage: input_accepted`. §3.7 의 표 참조 |
| **§3.7 로 기동한 검토자에 read-only 강제가 걸리는가** | **걸린다.** §4 의 방어 검사가 `유효` 를 냈다 — `review-tree-before` 와 `review-tree-after` 의 `log_sha256` 이 같은 값이었다. 검토자가 실행되는 동안 작업 트리가 바뀌지 않았다 |
| 자식 워크트리에서 close 를 돌릴 수 있는가 | **있다.** `--root "$W"` 로 돌렸고 신선도·재실행·로그 대조가 모두 그 체크아웃 기준으로 성립했다 |

### 11.2 아직 미검증인 것

- `check --types` 가 받는 값의 전체 목록. `worker_done`·`escalation`·`question` 만 실제로 썼다.
- `--agent` 가 받는 id 의 전체 목록, `--effort` 가 받는 값의 전체 목록.
- `--worktree` selector 형식 중 `path:` 만 썼다. `id:<repoId>::<path>`·`name:`·`branch:` 는 도움말이 나열한 것을 옮긴 것이다.
- `dispatch-show` 반환 JSON 의 어느 필드가 dispatch id 인지. 두 실행 모두 §3.5.2 의 `send` 가 닿아 이 폴백 경로를 쓰지 않았다.
- **구현자 쪽 권한 상한은 두 실행 모두 미관측이다.** §4 표의 구현자 두 칸(`.claude/settings.json` 의 승인 게이트 · `-s workspace-write`)이
  실제로 무엇을 막는지 이번 관통은 시험하지 않았다 — 두 구현자 모두 승인 대상 명령을 시도하지 않았기 때문이다.
  강제가 있었는지 없었는지 이 실행으로는 구분되지 않는다. **그 두 칸은 여전히 `enforcement_observed: false` 다.**
- 교체 실행의 검토자 강제(`claude -p --tools … --allowedTools … --strict-mcp-config`)가 **§3 기동 경로**에서 걸리는 것.
  단독 프로브는 관측했다(§4). 이번 관통에서의 관측 여부는 §4 표가 소유한다.
- **동등성 게이트가 이 관통으로 열리는지.** 관측 케이스 등록(§6.4)과 판정(§6.5)의 결과는 `fixtures/parity/` 와
  `docs/planning/progress.md` 가 소유한다 — 이 문서가 아니다.
- **§6.6 의 검토자-전용 재실행(같은 산출물을 두 검토자에게)은 한 번도 실행하지 않았다.** 2026-08-29 관통은 산출물이 달라
  검토자 면이 비교 불가였고(D-73), 검토자 동등성은 그 절차로만 관측할 수 있다. §6.6 은 §3.7·§4 의 명령형을 조합해 적은 것이지
  실행 신호를 관찰한 것이 아니다.
- 이 문서가 지시하는 실패·복구 경로(§7) 중 실제로 밟은 것은 `worker-start` 실패 1건(`agent_prompt_stalled`)뿐이다.
  `residualResources` 가 비어 있지 않은 경우, `worker-stop`·`worker-abandon` 은 밟지 않았다.
