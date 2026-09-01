---
id: progress
type: planning
status: active
updated: 2026-09-01
authority: derived
---

# 구현 진행 상태

[구현 계획](implementation-plan.md) §10 체크리스트 기준. 완료 판정은 관찰 가능한 결과로만 한다(K-51).
정지선·결정은 [decision-register](../decisions/decision-register.md) "구현 착수 결정"(D-59~D-71).

`계획 §10` 열은 이 표의 행이 계획 §10 의 어느 번호에 대응하는지다. 두 표의 번호가 어긋나
계획의 확인 기준이 조용히 사라지는 것을 막는다(1차 리뷰 F16). `—` 는 계획 §10 에 번호가 없는 항목이다.

독립 리뷰 findings 원문은 `docs/reviews/` 에 라운드별로 보관한다 —
[1차(F01~F31)](../reviews/2026-08-28-m2-round1-review/README.md) · [2차(G01~G13)](../reviews/2026-08-28-m2-round2-review/README.md).

## 지금 상태 (기준 `344fc7e` · 2026-09-01)

> 이 블록은 손으로 갱신한다. 위 SHA 는 **이 요약이 서술하는 상태의 기준 커밋**이지 블록을 쓴 커밋이 아니다.
> `git log --oneline 344fc7e..HEAD` 에 커밋이 있으면 그 커밋들이 아래 항목을 바꿨는지 먼저 본다 —
> 바꿨다면 블록을 믿지 말고 CI 최신 실행과 검사 재실행으로 실측하고, 이 블록을 갱신한다.

- **마일스톤:** M2 완료(2026-08-29 · D-76). **M3 진행 중** — G-M3 §6.1 1~5단계는 `a9e7af1` 로 닫혔다.
  **정비 3회를 마친 뒤 M3 본체로 돌아와 시나리오 3 을 세웠다**(`feat-20260901-charter-discovery-block-a3xs` · 승인 `86c17ef` · 통합 `344fc7e` · **관통 1회차 close PASS**).
  남은 M3 는 charter 를 쓰는 실제 T2 관통·MCP/브라우저 프로브(시나리오 8)·gate 집행(시나리오 9)이다.
  그 뒤 **관통 사이의 하네스 정비를 두 번 마쳤다** — 1회는 `feat-20260831-park-defects-actm`(park 결함 5건 · 통합 `fd7c7b9`),
  2회는 `feat-20260901-coordinator-procedure-gaps-y8fu`(코디네이터 위임 절차 결함 3건 · **2회차 `run_fc79c4267d1c` 에서 close 통과** · `status: done` · 통합 `c945686`),
  3회는 `feat-20260901-task-copy-brief-count-erc6`(`task/` 사본 병합 충돌 · 브리프 검사 개수 하드코딩 · **1회차 `run_e909a3e53aea` 에서 close 통과** · `status: done` · 통합 `045ea08`).
  남은 M3 는 charter(T2)·MCP/브라우저 프로브·gate·시나리오 3·8·9 다.
- **park 된 결함 5건이 닫혔다.** 넷은 승인된 범위였고 하나는 이 단위가 스스로 드러낸 것이다.
  | # | 무엇이 막고 있었나 | 고친 자리 | 회귀 테스트 |
  | --- | --- | --- | --- |
  | Q-18 | 작업 계약이 「바뀌는 파일·모듈」 선언을 **일부만 읽고 아무 말도 하지 않았다** — `bmad-attach-probe` 1회차를 통째로 실패시켰다(9개 중 2개만 실림) | `romeo/envelope.py` `change_scope_paths` — 다음 목록 항목·다음 제목·빈 줄까지 이어 읽는다 | `TestChangeScopeMultiline` |
  | Q-20 | spec 템플릿의 「빈칸 금지」 안내가 종료 검사의 미완료 토큰을 글자 그대로 담아 **자기 검사에 걸렸다** | `core/templates/tech-spec.md` — 안내는 남기고 토큰만 뺐다 | `TestTemplateBlankGuidanceToken` |
  | Q-22 | `romeo validate` 에 폴더를 주면 **파이썬 트레이스백**이 올라왔다 | `romeo/validate.py`·`romeo/cli.py` | `TestValidateDirectoryTarget` |
  | Q-25 | 반복 중단을 푸는 유일한 창구가 **시도까지 함께 시작**해 유령 기록과 이중 base_sha 를 만들었다 | `romeo/run_unit.py`·`romeo/cli.py` — 기록 전용 경로. 브레이크를 우회하지는 않는다 | `TestReviewOnlyRecord` |
  | (신규) | 원시 로그 앵커가 **첫 물리 줄 하나만** 기록된 명령 전체와 비교해, 개행을 담은 명령은 **어떤 구현으로도** `EVIDENCE_ANCHORED` 를 통과할 수 없었다 | `romeo/evidence.py` `log_command_header()` — `$ ` 뒤부터 첫 `--- stdout ---` 표지 앞까지. 로그 기록 형식은 바이트 그대로 | `TestMultilineCommandAnchor` |
  Q-21 은 **고칠 것이 없었다** — park 이 요구하던 CI 스텝이 이미 `4e47693`(2026-08-28)에 있었다. 문서 정정으로 닫고, 그 park 이 함께 지적한
  「옵션 없는 `bin/romeo doctor` 는 항상 exit 0 인 빈 검사」 사실은 남겼다.
- **위조 탐지는 약해지지 않았다.** 앵커 수정이 대조를 느슨하게 만들 수 있는 자리였다. 헤더를 읽지 못하면 **건너뛰지 않고 미검증**을 돌려주도록 해
  표지를 지우고 봉인을 다시 맞추는 우회를 막았다 — 그 우회는 **수정 전 코드에도 있었고**(`f2-prefix-bypass` 라벨이 옛 코드를 격리 로드해 재현했다),
  봉인까지 다시 맞춘 위조 4종이 전부 거부되는 것을 `check-15` 가 고정한다.
- **다섯 회차가 결함을 하나씩 드러내고 닫았다.** 게이트가 오탐을 낸 회차는 **없다**.
  | 회차 | 막은 것 | 성격 | 처리 |
  | --- | --- | --- | --- |
  | 1 | check-1·check-2 가 라벨의 한 글자를 틀리게 적어 **통과 불가능** | 검증 계획 | 재승인 `deae0aa` |
  | 2 | `evidence.py` 의 첫 줄 대조 — 개행 담은 check-9 이 통과 불가능 | 하네스 | 범위에 넣어 재승인 `448c9f8` |
  | 3 | 재검토 기록을 커밋하지 않고 위임해 자식 워크트리가 **브레이크를 못 풀었다** | 절차(런북 누락) | `8284f89` 로 커밋 후 재기동. 판정 없이 중단됐으므로 `started` 로 남겼다 |
  | 4 | check-16 이 `sorted(glob)` 의 **마지막 하나만** 대조 — 증거 파일이 둘이 되면 옛 run 을 검사 | 검증 계획 | 「모든 `check-9` 기록 대조」로 교체해 재승인 `120aa96` |
  | 5 | — | — | **pass** · 연속 실패 0 으로 리셋 |
- **5회차가 통과한 근거.** required_checks **16/16 exit 0** · AC-6 단독 실행 2건 exit 0 · 원시 로그 대조 **22건** · 재실행 대조 **16/16** ·
  봉투 앵커 **양쪽 5/5** · 방어 검사 **유효**(before/after `log_sha256` 동일 `1b7a3364afac`) · 검토자(codex `gpt-5.6-sol`, read-only) **PASS · findings 0**.
  유일한 WARN 은 `REVIEW_SAMPLE` 이고 **D-75 (b) 가 이미 1건으로 닫기로 확정한 것**이다.
  산출물 트리 `3a5ba01c58ff` 는 4회차와 **바이트로 같다** — 5회차는 코드를 새로 만들지 않고 검증 계획만 교체했다.
- **정비 중에 새로 드러난 코디네이터 절차 결함 셋을 `feat-20260901-coordinator-procedure-gaps-y8fu` 가 닫았다(재승인 `82a8191` · 통합 `c945686` · `status: done`).**
  셋을 park 으로 열지 않았다 — 여는 대신 **바로 그 단위에서 닫고 있기 때문**이다. 그 단위의 산출물이 추적 지점이고,
  실측으로도 닫히지 않은 잔여만 `Q-26` 으로 열었다(아래).
  ① RUNBOOK §3.1 의 위임 전 확인에 **재검토 기록(`attempts.yaml`) 대조가 없었다** — 없으면 자식 워크트리가 브레이크를 못 푼다(3회차가 겪었다).
  → §3.1 **확인 4** 신설(커밋과 작업 트리를 `diff` 로 대조 · 양쪽 다 없으면 통과) + 반례 테스트 `tests/test_runbook_procedure.py`.
  ② 한 관통에서 **재작업을 새 위임으로 붙이면 새 run 이 필요하다**(`_stamp_ids` 가 거부). 런북에 그 분기가 없었다. → **§3.4.2** 신설.
  ③ `orca orchestration run-create` 가 **코디네이터 터미널을 최신 run 에 재바인딩**해 옛 run 의 인박스를 못 읽는다(`consumer_fenced`).
  → **§3.2** 에 전환 절차(`run-use --id` · `run-current`)를 적고 2026-09-01 에 실측했다 —
  전환도 되고 전환 뒤 인박스 읽기도 된다. 거부는 **exit 1 · `.ok == false`** 다(2026-08-29 기록의 「종료 코드 0」 을 정정).
  펜싱되는 것은 `check --run`·`task-update` 뿐이고 `task-list --run` 은 바인딩과 무관하게 읽힌다.
  원문은 `.harness/observations.yaml` 의 `coordinator_run_rebinding`. **관측은 2회 돌았고 결론이 같다** —
  2회차(`run_fc79c4267d1c`)는 같은 스크립트를 다른 터미널·다른 Run 쌍으로 돌렸고 달라진 것은 id 뿐이다.
- **이 정비는 2회차에 닫혔고, 1회차 FAIL 이 검증 계획의 결함을 드러냈다.**
  1회차(`run_30aed12f8de0`)는 구현 쪽이 required_checks **14/14 exit 0** · 재실행 14/14 · 앵커 양쪽 5/5 · 방어 검사 유효였는데
  검토자(codex read-only)가 **FAIL**(findings 2건)을 냈고 close 가 `REVIEW_VERDICT` 하나에서 막혔다. 지적은 둘 다 정당했다 —
  `check-8` 이 관측 키의 **존재만** 보아 AC-5 의 「되는 것과 안 되는 것을 구분」을 대조하지 않았고,
  AC-5 의 근거 파일 둘(`.harness/observations.yaml` · `docs/work/<id>/observation/*.log`)이 **모두 `exclusions()` 제외 경로**라
  probe 를 증거 명령으로 돌리지 않으면 관측이 그 실행과 연결되지 않았다(Q-23 과 같은 계열).
  재승인(`82a8191`)으로 AC-5 에 봉인 요구를 더하고 `check-8` 을 세 결과 키 대조로 강화하고 `check-15`(probe 의 `stdout_tail`·`log_sha256`)를 더해 **15건**으로 만들었다.
  2회차는 1회차 워크트리를 시딩해 `exec > $OUT` 을 `main | tee $OUT` 으로 바꾸고 `evidence run --label run-rebinding-probe` 로 다시 돌린 것만으로 닫혔다.
- **2회차가 통과한 근거.** required_checks **15/15 exit 0** · 재실행 대조 **15/15** · 봉투 앵커 **양쪽 5/5** ·
  방어 검사 **유효**(before/after `log_sha256` 동일 `f2afce10760e`) · 검토자(codex, read-only) **PASS · findings 0** · close **PASS 52건 · FAIL 0**.
  WARN 은 둘 — `REVIEW_SUPERSEDED`(1회차 FAIL 봉투는 산출물 `a1bfeac+5588351d1e64` 를 본 판정이라 대상 밖)와 `REVIEW_SAMPLE`(D-75 (b) 가 1건으로 확정).
- **정비 3회가 그 둘을 닫았다 — 관통 1회차에 통과했다(`feat-20260901-task-copy-brief-count-erc6` · 승인 `dc7b161` · 통합 `045ea08`).**
  이전 두 정비는 5회차·2회차에 닫혔는데 이번은 **재승인 없이 1회차**다. 검사 14건을 승인 전에 두 방향으로 전부 돌린 것이
  그 차이를 만들었다 — 현재 트리에서 8건이 exit 1(빈 검사가 아니라는 음성 대조), 회귀 6건이 exit 0,
  그리고 `.gitignore` 규칙을 임시로 넣은 프로브로 핵심 3건이 exit 0 이 되는 것까지 확인하고 되돌렸다(통과 불가가 아니라는 양성 대조).
  ① **작업 계약(`docs/work/*/task/`)을 git 추적에서 뺐다.** 위임한 쪽(§3.3)과 워커 워크트리(§3.5.1)가 같은 경로에 계약을
  각각 만들어 양쪽이 커밋하면 `merge --ff-only` 가 거부되던 것(Q-14)이 원인 쪽에서 사라졌다 — **이번 통합이 `--ff-only` 로 그대로 지나갔고**,
  `git add -A` 를 해도 계약이 스테이지에 들어가지 않는 것을 실측했다.
  빼도 되는 근거는 **계약이 산출물이 아니라 파생물**이라는 것이다: `romeo/close.py` 의 `_task_anchor` 는 계약을 작업 트리에서 읽고,
  앵커는 `base_sha` 커밋의 승인된 `spec.md` 로 계약을 **다시 만들어 바이트 대조**하는 것이라 계약이 이력에 없어도 선다.
  그 전제를 `tests/test_task_artifact_policy.py` 가 반례로 고정한다 — 추적되지 않는 계약으로도 앵커가 서고, 작업 트리에 없으면 실패하며,
  제외 범위는 `task/` 뿐이고 `evidence/`·`result/`·`review/` 는 아니다. **이미 커밋된 계약 67개는 그대로 추적한다** —
  `git rm --cached` 를 쓰지 않았다. 규칙은 소급하지 않는다.
  ② **`adapters/orca/prompts/implementer-brief.md` 의 검사 개수 하드코딩을 지웠다.** 「`required_checks` 6건은」 이
  「계약에 실린 `required_checks` 를 문자열 그대로 실행한다 — 몇 건인지는 계약이 정한다」로 바뀌었다.
  이번 관통은 14건이어서 옛 문장이면 또 `sed` 로 고쳐야 했다.
- **정비 3회가 통과한 근거.** required_checks **14/14 exit 0** · 재실행 대조 **14/14** · 봉투 앵커 **양쪽 5/5** ·
  방어 검사 **유효**(before/after `log_sha256` 동일 `dfa9941120a9`) · 검토자(codex, read-only) **PASS · findings 0** · close 통과(`status: done`).
  WARN 은 `REVIEW_SAMPLE` 하나이고 **D-75 (b) 가 1건으로 닫기로 확정한 것**이다.
  **계획 중에 실측이 가정 둘을 뒤집었다** — ②를 「`fill_brief.py` 가 개수를 세도록」 고치려 했으나 그 스크립트는 **검토자 브리프만** 채운다(구현자 브리프는 `sed`),
  ①의 `.gitignore` 안이 「provenance 가 준다」고 보았으나 앵커가 커밋 조회가 아니라 재계산이어서 그 대가가 없다.
- **`Q-14` 는 정비 3회로 빠졌고, `Q-26` 은 실측으로도 닫히지 않은 부분이다** — 전환 뒤 인박스를 읽을 수 있다는 것까지는 봤지만,
  그 인박스에 워커가 실제로 보낸 메시지가 있을 때도 읽히는지는 보지 못했다(관측한 Run 은 비어 있었다).
- **CI:** `de3f758`(정비 3회 + 워크트리 정리 기록)까지 푸시돼 있다 — 2026-09-01 사용자 승인으로 `b19f753..de3f758` 을 밀었다. **`86c17ef`~`344fc7e`(시나리오 3 단위)는 아직 로컬에만 있다** — 푸시는 별도 승인 대상이다(K-66).
- **워크트리 2개** — 2026-09-01 에 여섯을 정리해 `mvp_planning` 과 원본 체크아웃(`main`) 만 남았고(495MB 회수), 그 뒤 이 단위의 `impl-feat-20260901-charter-discovery-block-a3xs` 가 생겼다(**아직 살아 있다** — 통합은 끝났고 tip `344fc7e` 는 도달 가능하다).
  `impl-`·`impl2-`·`impl4-`·`impl5-feat-20260831-park-defects-actm` · `impl-feat-20260901-coordinator-procedure-gaps-y8fu` ·
  `impl-feat-20260901-task-copy-brief-count-erc6` 이 지워졌다.
  **지우기 전에 두 가지를 본다 — 커밋이 다른 ref 로 도달 가능한가, 그리고 미커밋 산출물이 있는가.** 여섯 중 셋은 tip 이 이미 도달 가능하고
  미커밋도 0 이라 바로 지웠고, `actm` 계열 셋에는 **통합 이력에 없는** 잔여가 있었다 — 그 단위의 통합에는 5회차(`run_e3a4af18582c`)의
  evidence·result·review 만 들어갔고 1~4회차의 것은 워크트리에만 있었다. 그래서 WIP 커밋을 만들고 태그로 붙잡은 뒤에 지웠다:
  `preserve/park-defects-actm-run1`(1회차) · `run2`(2회차) · `run34`(3·4회차 — **검토자 봉투 2건 포함**).
  봉투를 남긴 것은 RUNBOOK §3.8 이 옛 산출물의 검토 봉투를 §6 의 관측 표본이라 지워서도 안 된다고 적기 때문이다.
  꺼내는 법은 `git show <태그>:<경로>` 이고, 삭제 **뒤에** 실제로 꺼내 읽어 확인했다(`run_43a8b64c0d69-reviewer.json` = FAIL · findings 1).
  이전 세션의 `preserve/bmad-install-observe-a3bm-run1`~`run3` 도 같은 방식이다.
  **`orca worktree rm` 이 브랜치도 지운다는 서술은 조건부다** — 2026-09-01 의 `actm` 계열 셋은 응답에 `preservedBranch` 가 실려 **브랜치가 남았고**,
  같은 날 먼저 지운 셋에는 그 필드가 없었다. 무엇이 그 차이를 만드는지는 **미확인**이다. 그래서 도달 가능성 확인은 그대로 한다.
- **시나리오 3 을 세우려고 열어 보니 그보다 앞선 결함이 있었다 — 차단이 계산만 되고 아무것도 막지 않았다.**
  `romeo/policy.py` 가 `blocks`(`spec-ready`·`milestone-plan`·`discovery-result`·`approval-gate`)를 계산하고 `romeo/card.py:108` 이 카드에 인쇄하고
  `romeo/fixtures.py:48` 이 fixture 와 대조하는데, **`romeo/close.py` 는 `guards` 만 읽고 `blocks` 는 한 번도 읽지 않았다.**
  정책표와 카드에는 「차단 spec-ready」 라고 찍히는데 그 글자가 막는 것이 없었다. 그래서 이 단위의 중심을 charter 템플릿이 아니라 **집행**으로 잡았다.
  | 무엇 | 어디 | 어떻게 |
  | --- | --- | --- |
  | 차단 카탈로그 | `core/policy/packages.yaml` 의 `blocks:` | 4건 각각 `title`·`enforced_at`·`requires`. 정책표를 읽으면 무엇이 언제 무엇을 요구하는지 한자리에 보인다 |
  | 집행 매핑 | `romeo/blocks.py` `BLOCK_CHECKS` | 카탈로그·매핑·실사용 **세 집합이 어긋나면 `load_policy` 가 실패한다** — 새 차단을 적고 집행을 잊는 재발이 구조적으로 막힌다 |
  | 승인 시점 | `romeo/docs.py` `approve_unit` | 미충족 차단을 이유와 함께 거부. 승인이 구현 착수의 유일한 선행 조건이므로(D-27) 여기가 「구현 dispatch 금지」의 정확한 자리다 |
  | 완료 시점 | `romeo/close.py` | 차단마다 `BLOCK_SATISFIED`. 이미 `done` 인 단위에는 **평가 자체를 건너뛴다**(소급 금지) |
  | T2 문서 | `core/templates/charter.md` | 「마일스톤 계획」 절이 `milestone-plan` 차단의 대상이다. 이 파일이 없어 그동안 T2 요청은 charter 없이 brief+spec 만 만들어졌다 |
  | 시나리오 3 | `scenarios/README.md`·`scenarios/3-discovery-block.md` + `tests/test_scenario_3.py` | 런북과 그것을 자동 실행하는 테스트. `scenarios/` 디렉터리가 그동안 없었다 |
- **구현자가 설계 두 곳을 근거와 함께 되돌렸다 — 둘 다 옳았다.**
  ① `spec-ready` 에 「`required_checks` 1건 이상」을 넣었다가 뺐다. 그대로 두면 `tests/test_docs_evidence_close.py` 의
  「검증 계획이 빈 spec 을 승인한 뒤 close 가 `REQUIRED_CHECK` 를 UNVERIFIED 로 인쇄하는지」 보는 검사가 **승인 단계에서** 깨진다 —
  그 파일은 계약의 `allowed_paths` 밖이고 고쳐서도 안 되는 정당한 검사다. 빈 검증 계획은 close 의 `REQUIRED_CHECK(UNVERIFIED)` 가 계속 판정한다.
  **같은 사실을 두 이름으로 막지 않는다.**
  ② spec 의 구현 단위 5번이 「close 는 `done` 에서 맨 앞에서 반환한다」 고 적었는데 **실제 코드는 `NOT_ALREADY_DONE` 을 기록하고 계속 진행한다.**
  소급 금지를 실제로 성립시키려면 차단 평가 자체를 건너뛰어야 했고 그렇게 구현했다. 계획의 서술이 틀렸던 것이다.
- **관통 1회차가 통과한 근거.** required_checks **17/17 exit 0** · 재실행 대조 **17/17** · 봉투 앵커 **양쪽 5/5** ·
  방어 검사 **유효**(before/after `log_sha256` 동일 `bc44db356ddc`) · 검토자(codex, read-only) **PASS · findings 0** · close **PASS**.
  WARN 은 `REVIEW_SAMPLE` 하나이고 **D-75 (b) 가 1건으로 닫기로 확정한 것**이다.
  `close` 출력에 **`BLOCK_SATISFIED — spec-ready: 확인란이 채워졌고 수용 기준 8건`** 이 실제로 찍혔다 — 이 단위가 만든 집행이 **자기 자신을 심사했다.**
  통합 트리 회귀도 확인했다: `python3 -m unittest discover -s tests` **620건 OK**(정비 3회 시점 579건에서 41건 증가) · `doctor --strict --scope repository`·`fixtures check`·`compile --check`·`validate` 전부 exit 0.
  **정비 3회가 `task/` 를 추적에서 뺀 효과가 두 번째로 확인됐다** — `git merge --ff-only` 가 이번에도 그대로 지나갔다.
- **검토자 채택은 예상대로 실패했고, 그 실패가 RUNBOOK 의 기록과 같았다(Q-12 재확인).**
  §3.7 (1) 의 TUI 터미널(`codex -s read-only -C <W> "$(cat 절차; cat 계약)"`)은 만들어졌으나 (2) 의 `worker-start --terminal` 이
  **`state: failed` · `stage: dispatch_input`** 로 끝났다 — RUNBOOK §3.7 표 3행(프롬프트가 argv 에 있으면 주입이 갈 곳이 없다) 그대로다.
  그런데 **검토 자체는 돌았다** — TUI 가 프롬프트를 argv 로 이미 받았기 때문이다. 그래서 채택을 포기하고 판정을 버리지 않았다:
  RUNBOOK 이 적어 둔 대체 회수 경로(`~/.codex/sessions/<날짜>/rollout-*.jsonl` 의 `last_agent_message`)로 결과 계약 JSON 688바이트를 받아
  `romeo review record` 로 봉인했고, 앵커 5개가 전부 PASS 였다. `worker-stop` 은 `alreadySettled: true` · `processAction: none` 을 냈다(터미널은 external 이라 건드리지 않는다).
- **회차가 기록되지 않았다 — `Q-27` 로 연다.** close PASS 뒤 `bin/romeo run-unit record --result pass` 가
  **「run 으로 시작한 시도가 attempts.yaml 에 없다 — 기동 기록 없이 판정만 남기지 않는다」** 로 거부했다(`romeo/run_unit.py:152`).
  기동 기록을 만드는 창구가 `run-unit` 의 시작 경로뿐이라 **RUNBOOK §3 을 손으로 밟은 관통은 성공해도 회차가 남지 않는다.**
  직전 단위(`feat-20260901-task-copy-brief-count-erc6`)에도 `attempts.yaml` 이 아예 없다 — 새 결함이 아니라 기존 구멍이다.
  그래서 `AGENTS.core.md` §10 의 연속 2회 실패 차단은 **손 관통 경로에서 한 번도 세지 않는다.**
- **park 은 `Q-12`·`Q-13`·`Q-15`~`Q-17`·`Q-19`·`Q-23`·`Q-24`·`Q-26`·`Q-27` 이다.**
- **문서 지연:** 「미검증·남은 위험」은 맨 위 소절(M2 close 이후)만 최신이다.


## 마일스톤

| 마일스톤 | 상태 | 근거 |
| --- | --- | --- |
| M0 정책표·fixture·분류 카드 | **완료** | [원문](archive/milestones.md) |
| M1 T0 최소 관통 (Claude 단독, 현재 작업 공간) | **완료** | [원문](archive/milestones.md) |
| M2 어댑터·역할·Orca 위임·T1 교차 관통 | **완료 (2026-08-29 · D-76)** | [원문](archive/milestones.md) |
| M3 기획 깊이 확장 (T2·discovery·gate·doctor) | **진행 중** — G-M3 는 §6.1 **1~5단계 전부 닫힘**(D-77 + `feat-20260831-bmad-attach-probe-tgnb` + `feat-20260831-bmad-install-observe-a3bm`). **5단계 결론은 「공존한다」**. 그 뒤 **관통 사이의 하네스 정비 3회**를 마쳤다 — 1회는 `feat-20260831-park-defects-actm`(park 결함 5건 · 5회차 `run_e3a4af18582c` close · 16/16), 2회는 `feat-20260901-coordinator-procedure-gaps-y8fu`(코디네이터 위임 절차 결함 3건 · 2회차 `run_fc79c4267d1c` close · required_checks 15/15 · 재실행 15/15 · 앵커 양쪽 5/5 · 검토자 PASS findings 0), 3회는 `feat-20260901-task-copy-brief-count-erc6`(`task/` 사본 병합 충돌 · 브리프 검사 개수 하드코딩 · **1회차** `run_e909a3e53aea` close · required_checks 14/14 · 재실행 14/14 · 앵커 양쪽 5/5 · 검토자 PASS findings 0). 그 뒤 **M3 본체로 돌아와 시나리오 3 을 세웠다** — `feat-20260901-charter-discovery-block-a3xs`(계산만 되던 `blocks` 를 승인·종료 두 지점에서 집행 · `core/templates/charter.md`(T2) · `scenarios/` 런북 · **관통 1회차** `run_d947edf2d24a` close PASS · required_checks 17/17 · 재실행 17/17 · 앵커 양쪽 5/5 · 검토자 PASS findings 0). M3 의 나머지(charter 를 쓰는 실제 T2 관통 · MCP/브라우저 프로브=시나리오 8 · gate 집행=시나리오 9)는 미착수 | D-77, `docs/work/feat-20260831-bmad-install-observe-a3bm/`(status done) 통합 `a9e7af1`, `docs/work/feat-20260831-park-defects-actm/`(status done) 통합 `fd7c7b9`, `docs/work/feat-20260901-coordinator-procedure-gaps-y8fu/`(status done) 통합 `c945686`, `docs/work/feat-20260901-task-copy-brief-count-erc6/`(status done) 통합 `045ea08`, `docs/work/feat-20260901-charter-discovery-block-a3xs/`(status done) 통합 `344fc7e` |
| M4 ~ M7 | 미착수 | [원문](archive/milestones.md) |

## §10 체크리스트

항목명·상태·근거 링크만 남긴 완료 표다. 각 행의 근거 원문은 [archive/checklist-8-48.md](archive/checklist-8-48.md) 에 문장 그대로 있다.

| # | 계획 §10 | 항목 | 상태 | 근거 |
| --- | --- | --- | --- | --- |
| 1 | #1 | §9.2 결정 1~5 확정 | 완료 | [원문](archive/checklist-8-48.md#c1) |
| 2 | #2 | fixture 15~20건 (사용자 3개월 요청 포함) | 완료 (33건) | [원문](archive/checklist-8-48.md#c2) |
| 3 | #3 | 정책표 3종 + 스키마 + Tech Spec 템플릿 + `/plan` SKILL | 완료 | [원문](archive/checklist-8-48.md#c3) |
| 4 | #4 | `romeo validate`·`new`·ID + unittest | 완료 | [원문](archive/checklist-8-48.md#c4) |
| 5 | #5 | `/plan --dry-run` 5건 shadow | 완료 | [원문](archive/checklist-8-48.md#c5) |
| 6 | #6 | M1: T0 2건 관통 | 완료 | [원문](archive/checklist-8-48.md#c6) |
| 7 | #7 | stale 거부·미체크 AC 거부 | 완료 (테스트 기준) | [원문](archive/checklist-8-48.md#c7) |
| 8 | #8b | G-M2 채택 게이트 | 완료 | [원문](archive/checklist-8-48.md#c8) |
| 9 | — | LICENSE Apache-2.0 교체 + `THIRD_PARTY_NOTICES.md` | 완료 | [원문](archive/checklist-8-48.md#c9) |
| 10 | #8b | `vendor/obra-superpowers@b36e082/` 원문 복사(수정 0) | 완료 | [원문](archive/checklist-8-48.md#c10) |
| 11 | — | CI(python 3.11) 하네스 검사 | 완료 (그 뒤의 워크플로 변경은 **CI 에서 미실행**) | [원문](archive/checklist-8-48.md#c11) |
| 12 | #9 | 어댑터 컴파일(`romeo compile`) | 완료 | [원문](archive/checklist-8-48.md#c12) |
| 13 | — | 실행 가드 `.claude/settings.json` | 완료 | [원문](archive/checklist-8-48.md#c13) |
| 14 | #9 | `romeo doctor` 부착 검증 | 완료 | [원문](archive/checklist-8-48.md#c14) |
| 15 | #8b | 충돌 fixture 3종 (K-68) | 완료 | [원문](archive/checklist-8-48.md#c15) |
| 16 | — | Codex 독립 리뷰 반영 | 완료 | [원문](archive/checklist-8-48.md#c16) |
| 17 | — | K-60 재정의(D-72) | 완료 | [원문](archive/checklist-8-48.md#c17) |
| 18 | — | F-08 원자적 컴파일 · F-07 upstream 대조 | 완료 | [원문](archive/checklist-8-48.md#c18) |
| 19 | **#8** | 검토자 런타임 read-only **쓰기 시도 거부 로그** | 완료 | [원문](archive/checklist-8-48.md#c19) |
| 20 | #9 | 부품 부착 배선 (`.harness/romeo.project.yaml` → 라우터) | 완료 | [원문](archive/checklist-8-48.md#c20) |
| 21 | #10 선행 | 승인 → 실행 순서 · 위임 식별자 | 완료 | [원문](archive/checklist-8-48.md#c21) |
| 22 | #10 선행 | 작업 계약 생성 (`romeo envelope build`) | 완료 | [원문](archive/checklist-8-48.md#c22) |
| 23 | #10 선행 | 검토자 판정 → 완료 판정 연결 | 완료 (실물 봉투로는 **미검증**) | [원문](archive/checklist-8-48.md#c23) |
| 24 | #11 | 동등성 게이트 정직화 + CI 스텝 | 완료 (게이트는 **미판정**) | [원문](archive/checklist-8-48.md#c24) |
| 25 | #8 | 역할 계약 투영 · 권한 상한 정본 | 완료 | [원문](archive/checklist-8-48.md#c25) |
| 26 | #10 | Orca 런북으로 T1 관통 (Claude 구현 / Codex 리뷰) | **완료** | [원문](archive/checklist-8-48.md#c26) |
| 27 | #11 | 역할 교체 재현 + parity **관측** | **완료 — 게이트 판정 FAIL** | [원문](archive/checklist-8-48.md#c27) |
| 28 | — | 2차 독립 리뷰 반영 (G01~G13) | 완료 | [원문](archive/checklist-8-48.md#c28) |
| 29 | — | 관통이 찾은 결함 반영 (RUNBOOK 3건 + 코어 모순 1건) | 완료 | [원문](archive/checklist-8-48.md#c29) |
| 30 | #11 | 동등성 게이트 정의 보완 | **완료 (D-73)** | [원문](archive/checklist-8-48.md#c30) |
| 31 | — | 작업 단위 `feat-20260829-license-field-46an` 완료 | **진행 중 — 3차 관통 기준 실행 완료(close 는 검토 표본만 남았다)** | [원문](archive/checklist-8-48.md#c31) |
| 32 | — | `AGENTS.md` 서문 비대칭 해소 | **완료** | [원문](archive/checklist-8-48.md#c32) |
| 33 | #11 | 검토자 면 동등성 관측 — 검토자-only 재실행(RUNBOOK §6.6) | **완료 — 게이트 FAIL** | [원문](archive/checklist-8-48.md#c33) |
| 34 | — | 작업 계약 `allowed_paths` 상한 — spec 변경 범위로 좁힌다 | **완료 (`c237ea9`)** | [원문](archive/checklist-8-48.md#c34) |
| 35 | — | Q-08 재현성 측정 — 같은 산출물에 같은 검토자 런타임 2회 추가 | **완료 — codex 의 PASS 는 재현되지 않았다** | [원문](archive/checklist-8-48.md#c35) |
| 36 | #11 | 동등성 게이트에 재현성 요구 (D-74) | **완료 — 게이트 PASS(관측 2건 · 비교 불가 면 2)** | [원문](archive/checklist-8-48.md#c36) |
| 37 | — | 승인된 spec 을 고쳤을 때 재승인하는 경로 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c37) |
| 38 | — | `approve` 의 `base_sha` 가 승인된 내용을 담지 않는 커밋을 가리킨다 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c38) |
| 39 | — | 결과 계약 스키마에 자유 서술 자리가 없다 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c39) |
| 40 | — | 두 런타임 모두 결과 계약 스키마를 CLI 로 강제할 수 없다 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c40) |
| 41 | — | `close` 가 evidence 를 하나만 읽어 §6.6 뒤에 구조적으로 깨진다 | **완료 (2026-08-29) — D-75 의 표본 수만 사용자 확정 대기** | [원문](archive/checklist-8-48.md#c41) |
| 42 | — | 검토자 프롬프트의 「명령 실행 금지」가 런타임에 따라 읽기까지 막는다 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c42) |
| 43 | — | 잔여 결함 설계의 반박 검토(세 렌즈) 와 반영 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c43) |
| 44 | — | 원시 로그가 산출물 식별을 봉인한다 (4차 리뷰 구멍 B 의 한 겹) | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c44) |
| 45 | — | 구현 diff 의 반박 검증(세 렌즈 + finding 별 반박 에이전트) 과 반영 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c45) |
| 46 | #10·#11 | 3차 관통 — 기준 실행(구현자 claude · 검토자 codex) 완료, 교체 실행 준비 | **완료 (2026-08-29) — 48 에서 close** | [원문](archive/checklist-8-48.md#c46) |
| 47 | — | M2 근본 원인 재검토 — "왜 3일째 안 닫히나, 설계·계획이 틀렸나" | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c47) |
| 48 | #11·#12 | D-76 실행 — 완료 정의 개정 · parity 판정 축소(advisory) · **impl5 close** · 페이로드 통합 | **완료 (2026-08-29)** | [원문](archive/checklist-8-48.md#c48) |

## 세션 기록

날짜별 서술은 [archive/session-log.md](archive/session-log.md) 로 옮겼다 — 이 문서는 상태를 담고, 이력은 거기 있다.

## 미검증·남은 위험

이 절의 항목은 **완료가 아니다.** 검사가 PASS 라는 것과 그 회로가 실제로 닫혔다는 것은 다르다(K-51).

### 2026-08-29 M2 close 이후 남은 것 (최신)

- **원격 CI 는 `144a676` 까지 초록이다**(run `33289382316`). 그 뒤 커밋은 이 CI 줄 갱신뿐이다 — CI 는 push 마다 다시 본다.
- **기본 구현자(claude)의 권한 강제는 여전히 미관측이다.** D-76 의 "권한 상한" 요소는 관측된 범위(검토자 read-only 두 런타임)로만 판정한다. 교체 구현자(codex `-s workspace-write`)의 외부 쓰기·승인 명령 차단도 부분 관측이다.
- **검토 판정이 왜 흔들리는지는 모른다(Q-10).** D-76 은 그것을 게이트에서 뺀 것이지 줄인 것이 아니다. 재료: `--judge-verdict strict` 프로파일과 같은 산출물 5실행의 봉투. 첫 손댈 자리는 `review/SKILL.md` 의 FAIL 사유 열거.
- **check-5 가 하네스 자신의 unittest 라 페이로드 close 가 하네스 리비전에 묶인다.** 이번엔 impl5(7f8ecd7)에서 닫아 문제없었지만, 다음 단위부터는 페이로드 검사와 하네스 검사를 분리하는 템플릿 규칙이 필요하다(다음 자리 3).
- **RUNBOOK 은 여전히 수동이다(1,164줄·최소 72 행동 묶음).** 이번 close 는 수동 절차 없이 `close` 한 명령으로 끝났지만, 다음 T1 의 위임·회수·모으기는 자동화 전까지 같은 비용이다.
- **impl6 교체 실행은 하지 않았다.** 현 base(7f8ecd7)에서의 교체 성공 여부는 미검증이다 — D-76 ① 에 따라 M2 게이트 조건이 아니다.
- **옛 봉투 11건은 REVIEW_SUPERSEDED WARN 으로 남아 있고 지우지 않는다**(관측 표본). `APPROVAL_CHAIN` WARN(옛 손 재승인)도 그대로다 — Q-11 미룸.
- **v1 릴리스 잔여:** T2 Charter(V-2)·shadow 20건(V-10)·attach/update(M5) — M2 완료가 이것들을 닫지 않는다.

### 위협 모델 — 무엇을 막고, 무엇을 막지 못하는가

원문은 [제약 K-56~K-59](../requirements/constraints.md)로 옮겼다 — 무엇을 막고(K-56), 무엇을 막지 못하며(K-57),
무엇에 의존하고(K-58), 재실행으로 확인할 수 없는 것을 어떻게 다루는가(K-59). 문장은 그대로다.
다음 라운드에서 "해시를 하나 더 걸면 닫힌다" 류의 제안이 나오면 K-57 을 먼저 읽는다.

### 그 이전 소절 (2026-08-29 이전)

4차 리뷰(위조 시도 2종 관통) · 게이트 정의 보완 · 잔여 결함 37~42 · 이전 라운드에서 이어지는 것은
[archive/risks-2026-08-29.md](archive/risks-2026-08-29.md) 에 있다. 각 소절은 그 날짜 기준이며,
상당수가 D-76 으로 닫혔거나 후속 단위로 넘어갔다 — 닫혔는지는 그 항목의 근거를 다시 실행해 확인한다(K-51).
