# 2026-08-28 M2 실행 검증 2차 리뷰

1차 리뷰([`../2026-08-28-m2-round1-review/`](../2026-08-28-m2-round1-review/README.md)) 반영분을 **다시 독립 리뷰에 넣어** 받은 2차 findings 와,
그 findings 를 3차 라운드에서 어떻게 반영했는지의 대조표다.

| 파일 | 내용 |
| --- | --- |
| `REVIEW_FINDINGS.md` | 2차 리뷰 findings 전문(G01~G13 · blocker 5 · important 5 · minor 3). 각 항목에 재현 명령과 실측 출력이 들어 있다 |

## 2차 리뷰가 잡은 하나의 패턴

blocker 5건은 대상 파일이 다르지만 결함의 형태가 같다 — **판정이 검사되지 않는 자기 신고 위에 서 있다.**

- 손으로 쓴 PASS 봉투 하나가 close 를 통과했다. 가리키는 작업 계약도 증거 파일도 존재하지 않았다(G05).
- `source.kind` 한 단어를 `authored` → `observed` 로 고치면 동등성 게이트가 열렸다. 실제 교차 실행은 한 번도 없어도 됐다(G10).
- 관찰 텍스트가 **존재한다는 것**만으로 doctor 가 12개 전부에 "런타임 로드 관찰됨" 을 인쇄했다. 이름도 개수도 대조하지 않았다(G09).
- 어댑터 지침이 지목한 작업 계약 경로에 파일을 쓰는 코드가 저장소에 0건이었다(G02). 승인 커밋에는 워커가 실행할 하네스가 들어 있지 않았다(G03).
- CI 의 게이트 스텝이 `|| echo` 로 끝나 어떤 판정이 나와도 초록불이었다(G06).

3차 라운드의 수정 기준은 여기서 나왔다: **모든 판정을 실재하는 것에 묶는다.**
문자열이 아니라 파일의 실재·해시 일치·이름 대조·기계 판독 출력으로 판정한다.

## 반영 대조 (3차 라운드)

각 행의 "관찰된 결과" 는 실제로 실행한 명령의 출력이다. 실행하지 않은 것은 아래 "반영하지 않은 것" 에 있다.

| # | 대상 | 반영 | 관찰된 결과 |
| --- | --- | --- | --- |
| G01 | `adapters/{claude,codex}/workflows/implement.md` | 계약을 손으로 쓰라는 지시를 `bin/romeo envelope build --unit … --role implementer --base-sha … --run <run-id>` 로 교체 | `./bin/romeo compile` 산출물 28개 EXIT=0 · `compile --check` PASS EXIT=0 |
| G02 | `adapters/{claude,codex}/workflows/review.md` | 입력 계약 경로를 생산자가 0건인 `.harness/runs/…/task-reviewer.json` → `docs/work/<id>/task/<run-id>-reviewer.json` 으로 교체 | `romeo/envelope.py:148-150` 이 쓰는 경로와 같은 값. `grep -rn "task-reviewer" adapters/ core/` → 0건 |
| G03 | `adapters/orca/RUNBOOK.md` §3.1 | 커밋 대상을 "승인된 spec.md **와 워커가 실행할 하네스 상태**" 로 고치고 확인 신호 3개를 §3.5·§3.7 기동 전 조건으로 걸었다 | 반례 재현: `git archive HEAD` 로 꺼낸 트리에서 `bin/romeo envelope build --help` → EXIT=2, 작업 트리에서는 EXIT=0 |
| G04 | `adapters/orca/RUNBOOK.md` §3.7·§4 | 검토자 기동을 `terminal create --command`(강제 수단) → `worker-start --terminal` 2단계로 분리. §4 표의 「실행으로 관찰했나」 한 칸을 **단독 프로브 / §3 기동 경로** 두 칸으로 쪼갰다 | `orca orchestration worker-start --help` 에 `-s/--sandbox`·passthrough 없음(EXIT=0). §4 표 검토자 두 행이 `예 / 아니오 — 미관측` 으로 인쇄된다 |
| G05 | `romeo/close.py` | `_check_review` 에 앵커 검사 4개(`REVIEW_TASK_ANCHORED`·`REVIEW_BASE_SHA`·`REVIEW_EVIDENCE_ANCHORED`·`REVIEW_ROLE_CONTRACT`). 역할 계약 규칙은 `romeo/parity.py` 의 것을 재사용했다 | 같은 반례 스크립트가 수정 전 `close verdict = PASS · EXIT=0` → 수정 후 `FAIL`. `python3 -m unittest tests.test_docs_evidence_close` → 29 OK |
| G06 | `.github/workflows/harness.yml` | `\|\| echo` 제거. `--json` 으로 `gate_verdict`·`checker_verdict`·`synthetic` 을 읽어 FAIL·구조오류·검사기FAIL·합성0건만 빨간불 | 스텝 4상태 실측: 기본 EXIT=0(미판정 경고) · 관측 일치 EXIT=0 · 관측 불일치 **EXIT=1** · 위조 observed **EXIT=1** |
| G07 | `adapters/{claude,codex}/workflows/review.md` | 방어 검사(`git status --porcelain` 전후 비교)의 주체를 검토자 → **이 절차를 부른 쪽**으로 되돌리고 「읽기 전용 셸」 문구를 삭제 | `core/roles/reviewer.yaml:12 capabilities: [read, search]` 와 일치. `compile --check` PASS |
| G08 | `romeo/cli.py` | `evidence checks` 가 `required_checks` 없는 spec 에서 `UnboundLocalError` 로 죽던 것을 메시지 + 종료 코드 2 로 교체 | 반례 재현: 수정 전 `UnboundLocalError … EXIT=1` → 수정 후 stderr 안내 · `rc=2` · 출력에 `Traceback` 없음 |
| G09 | `romeo/doctor.py` · `.harness/observations.yaml` | 관찰 기록을 `{observed_at, skills:[…], note}` 로 구조화하고, 실제 스킬 이름과의 **차집합**으로 판정 | `./bin/romeo doctor` → `codex 12개 · 런타임 로드 **부분 관찰** 10/12개 · 미관찰 implement · review`(EXIT=0) |
| G10 | `romeo/parity.py` | `observed` 케이스의 `source.ref`·`unit_id`·`evidence_ref` 실재 검사. 하나라도 어긋나면 `PARITY_INVALID` exit 1 | 반례 재현: `kind: authored → observed` 한 줄 조작이 수정 전 `게이트 PASS · EXIT=0` → 수정 후 `PARITY_INVALID … EXIT=1` |
| G11 | `docs/planning/progress.md` | 체크리스트 25행이 에이전트 파일 `tools:` frontmatter 를 "이 런타임의 강제 수단" 이라고 단정하던 것을 정정하고 미관측 항목으로 올렸다 | 관찰된 강제 수단은 기동 플래그다 — `PROBE_READONLY.md` 프로브 7건(A·B1·B2·C·C2·D·E)이 전부 `codex exec` / `claude -p` 플래그다 |
| G12 | `romeo/parity.py` | `checker_verdict` 를 합성 케이스만으로 계산하고, 합성 0건이면 `해당 없음` 으로 인쇄 | `./bin/romeo fixtures parity --report` → `검사기 자기 검증: PASS — 합성 5건이 …`(계산 대상과 설명 문장이 같은 집합) |
| G13 | `tests/test_doctor.py` | 하지 않은 관찰을 주장하던 테스트 이름을 `test_new_workflows_have_loadable_frontmatter_in_both_skill_dirs` 로 변경 | `python3 -m unittest tests.test_parity tests.test_doctor` → 94 OK |

## 반영하지 않은 것 (근거 있는 불일치)

- **G05 의 `base_sha == HEAD` 제안 → 「HEAD 이력의 조상인가」로 바꿨다.** 계약의 `base_sha` 는 승인 커밋이고 구현 커밋이 그 뒤에 쌓이므로,
  제안대로면 실제 흐름에서 절대 통과할 수 없다. 다른 이력에서 만든 계약은 orphan commit 반례가 잡는다.
- **G05 의 `result/` 구현자 봉투 검증 → 넣지 않았다.** 그 경로에 파일을 쓰는 코드가 저장소에 없다(`grep -rn '/result/' romeo/` → 0건).
  차단 검사로 넣으면 close 가 영영 통과할 수 없다. 별개 작업으로 남긴다.
- **G06 의 종료 코드 3값 분리 → 하지 않았다.** 같은 라운드에 다른 담당이 `romeo/cli.py` 를 쓰고 있었다.
  findings 가 제시한 두 번째 방법(기계 판독 출력)을 택했고, 결과적으로 **PASS=0 · 그 외=1** 규약은 그대로다.
- **G10 에 조건 하나를 더했다.** findings 는 "모든 `evidence_ref` 가 실재" 만 요구했는데, 그러면 양면이 전부 `evidence_ref: null` 인
  관측 케이스가 앵커 0개로 게이트를 열 수 있다. "실재하는 `evidence_ref` 최소 1개" 를 추가했다.

## 이 라운드에서 여전히 관측되지 않은 것

3차 라운드가 강제한 것은 **"관측이라고 선언하면 관측물이 있어야 한다"** 이지, 관측을 만든 것이 아니다.
남은 미관측 항목은 [`../../planning/progress.md`](../../planning/progress.md) 의 `## 미검증·남은 위험` 절이 정본이다.
