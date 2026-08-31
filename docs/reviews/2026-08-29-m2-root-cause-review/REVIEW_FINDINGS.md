# M2 마일스톤 지연 근본 원인 리뷰

> 조사 기준: 현재 작업 루트 HEAD `57a2628a78ab318fd5eb8abae41dde7f1ad2c849` · 2026-08-29 KST  
> 조사 범위: M2 기본 기획, 구현 계획, 결정 등록부, 열린 질문, Orca RUNBOOK, `feat-20260829-license-field-46an`의 task/evidence/result/review, 3차 기준·교체 worktree의 현재 상태  
> 변경 범위: 이 보고서와 보고서 작업 단위의 evidence/result만 작성했다. 코드·정책·기존 계획·결정·RUNBOOK·라이선스 작업 단위·원격 상태는 바꾸지 않았다.

## 결론

M2가 오래 걸린 주원인은 라이선스 필드 기능의 난이도가 아니다. **아직 실전 검증되지 않은 하네스가 자기 측정 장치(계약·증거·리뷰·동등성·종료 검사)를 한꺼번에 만들면서, 동시에 그 장치로 자기 자신을 합격시키려 한 범위와 순서**가 1차 근본 원인이다.

그 결과 실제 관통을 할 때마다 제품 결함보다 먼저 측정 장치의 결함이 드러났다. 판정을 실재에 묶는 앵커, 두 검토자가 같은 산출물을 봤는지, 같은 런타임의 판정이 재현되는지, 어떤 검토가 현재 산출물에 대한 것인지가 관통 뒤에 차례로 정의됐다. 측정 기준이 바뀔 때마다 앞선 evidence와 review가 새 기준에서 낡아 재관통이 필요해졌다. 1차 리뷰 31건, 2차 리뷰 13건, 후속 반박 검증 28건과 잔여 결함 6건은 과잉 리뷰였기보다 **통합 불변조건을 실관통 전에 고정하지 못한 비용**이다. 근거: `docs/reviews/2026-08-28-m2-round1-review/README.md:1-18`, `docs/reviews/2026-08-28-m2-round2-review/README.md:10-21`, `docs/planning/progress.md:97-103`.

현재 M2는 완료가 아니다. 현재 체크아웃의 parity 명령은 exit 0이지만, 이는 과거 `c237ea9` 산출물에서 구현자 면이 같고 검토자들이 **실패하는 제품을 모두 FAIL로 판정한** 관측까지 포함한 결과다. 최신 3차 기준 산출물은 impl5 worktree에서 6개 필수 검사를 통과하고 구현자·검토자 모두 PASS지만 현재 체크아웃에 모이지 않았고, 교체 실행 impl6은 계약만 준비된 채 미기동이다. 실제 `close`도 실행되지 않았고 현재 HEAD의 원격 CI는 확인하지 못했다.

용어를 짧게 구분하면 다음과 같다.

- **제품 PASS:** 라이선스 필드의 수용 기준과 6개 검사가 통과했다는 뜻이다.
- **parity PASS:** 역할을 바꾼 두 실행의 계약·검사 목록·판정이 비교 가능한 면에서 같다는 뜻이다. 제품이 옳다는 뜻은 아니다.
- **close PASS:** 기록을 다시 실행해 현재 산출물·승인·리뷰까지 종료 조건을 만족했다는 뜻이다.
- **worker_done:** 실행 런타임이 오케스트레이터에 완료를 보고했다는 뜻이다. 산출물이나 close의 대체물이 아니다.

현재 상태를 한 표로 분리하면 혼동이 줄어든다.

| 판정 축 | 현재 확인된 사실 | 현재 판정 |
| --- | --- | --- |
| 제품 — 3차 기준 | impl5의 `run_42710f6ac93b`는 같은 `7f8ecd7`/트리 `7439ee6383d1…`에서 check-1~6이 모두 exit 0이고 구현자·검토자 봉투가 PASS다. 근거: `/Users/julliettelee/orca/workspaces/Romeo-Harness/impl5-feat-20260829-license-field-46an/docs/work/feat-20260829-license-field-46an/evidence/run_42710f6ac93b.yaml:98-165`, 같은 worktree의 `result/run_42710f6ac93b-implementer.json:41-44`, `review/run_42710f6ac93b-reviewer.json:10-13`. | 기준 실행 PASS |
| 제품 — 3차 교체 | impl6은 HEAD `7f8ecd7`이고 `run_e82929ee03da` 계약 두 파일만 미추적 상태다. evidence/result가 없다. 근거: 조사 evidence의 `impl6-status` 명령. | 미기동·미확인 |
| 동등성 | 현재 HEAD에서 `bin/romeo fixtures parity --report`는 exit 0과 `핵심 동등성 게이트: PASS — 관측 2건`을 냈다. 그러나 최신 3차 산출물이 아니라 `run_5a5…`/`run_ba40…`를 가리킨다. 근거: `fixtures/parity/pr-license-field-t1-observed.yaml:23-36`, `fixtures/parity/pr-license-field-t1-reviewer-observed.yaml:26-45`, 조사 evidence의 `current-parity` 로그. | 과거 관측 기준 PASS, 최신 3차 비교 미실행 |
| 종료 | impl5의 close 전 항목이 통과했다는 진행 기록은 있으나 실제 close는 하지 않았다고 명시돼 있다. 근거: `docs/planning/progress.md:26-36`, `docs/planning/progress.md:99`. | 미완료 |
| 정본 수집 | 최신 기준 evidence는 현재 체크아웃에 없고 impl5에만 있다. `test ! -f docs/work/.../evidence/run_42710f6ac93b.yaml`과 impl5 절대 경로의 `test -f ...`가 모두 exit 0이다. | 미수집 |
| Orca lifecycle | `orca status --json`은 `.result.app.running=false`, `runtime.state=stale_bootstrap`, `runtime.reachable=false`다. heartbeat 전송도 `Could not connect to the running Orca app`로 실패했다. | 현재 실행 차단 |
| CI | 진행 문서가 마지막 성공을 run `33237273401`/`b53f08c`로 기록하지만 이후 커밋은 push하지 않았다고 적는다. 현재 `gh run list --limit 1 ...`는 네트워크 연결 실패로 exit 1이었다. 근거: `docs/planning/progress.md:28`, 조사 evidence의 `current-ci-lookup`. | 현재 HEAD 원격 미확인 |

지연 구조는 다음처럼 연결된다.

```text
M2 한 단위
├─ 제품 기능: 라이선스 필드
├─ 실행 배관: Run·Task·worktree·worker lifecycle
├─ 권한 강제: 기본/교체 implementer·reviewer
├─ 증거 체계: 계약·로그·봉투·close·위조 저항
└─ 동등성 판정: 산출물 동일성·검토 재현성·CI
       │
       └─ 실관통에서 새 결함 발견 → 판정 규칙 변경 → 앞선 증거가 낡음 → 재관통
```

## 사용자 스토리

### US-1 — 움직이지 않는 합격선을 원한다

프로젝트 책임자로서, 한 번 실행을 시작하면 그 실행이 통과해야 할 기준이 끝날 때까지 고정돼 있어야 한다. 그래야 실패가 제품 문제인지 측정자 문제인지 구분하고 재작업 예산을 판단할 수 있다.

### US-2 — 안전한 권한과 완료 보고가 동시에 살아 있기를 원한다

운영자로서, 구현자와 검토자에게 필요한 권한 상한을 걸어도 heartbeat·질문·`worker_done`이 도착해야 한다. 보고 채널이 막혔다고 같은 제품 구현을 다시 시작하고 싶지 않다.

### US-3 — 같은 근거에는 재현 가능한 검토 판정을 원한다

의사결정자로서, 같은 산출물·같은 계약·같은 절차라면 PASS/FAIL 의미가 반복 실행에서도 일관되기를 원한다. 표본을 계속 늘려 원하는 PASS가 나올 때까지 돌리는 방식은 원하지 않는다.

### US-4 — 다음 세션이 한 곳에서 현재 사실을 찾기를 원한다

다음 작업자로서, 최신 evidence/result/review, 그 산출물의 worktree, close 결과, 원격 CI가 한 기준 SHA에 묶여 있어야 한다. 진행 문서의 문장과 여러 worktree를 조합해 현재 상태를 추론하고 싶지 않다.

### US-5 — 후속 보안 연구가 이미 합의한 사용자 가치의 전달을 무기한 막지 않기를 원한다

PM으로서, 승인 서명·검토 표본 정책·모델 비결정성 연구처럼 중요한 후속 강화는 보존하되, 원래 M2 종료 조건에 없던 항목이 승인 없이 선행조건으로 승격되지 않기를 원한다.

## 현재 관찰

### US-1 관찰 — 한 마일스톤이 제품과 측정자 전체를 함께 만들었다

- **사실:** M2의 `만들 것`은 코어 원칙·역할·두 envelope 스키마·두 workflow·두 런타임 adapter·Orca RUNBOOK·bindings·parity fixture·권한 설정·doctor·brief·provenance·실제 T1 페이로드·CI를 한 문단에 묶는다. 근거: `docs/planning/implementation-plan.md:502-510`.
- **사실:** 원래 관찰 가능한 종료 조건은 Run/Task/worktree, ResultEnvelope, evidence, review findings, close PASS, 역할 교체 parity, 라이선스 결과, CI PASS였다. 근거: `docs/planning/implementation-plan.md:508-511`, `docs/planning/implementation-plan.md:643-645`.
- **사실:** M2 진입 커밋 `0f10bfa`부터 3차 기준 기록 `ecb4819`까지 `git rev-list --count 0f10bfa^..ecb4819`은 44를 냈다. 이 수는 작업량의 완전한 계측이 아니라 범위가 여러 번 수정·관찰·기록됐다는 보조 지표다.
- **사실:** D-73(검토자 면의 산출물 동일성), D-74(면당 2개 표본과 일관성), D-75(현재 산출물/현재 승인에 대한 close 판정)는 실관통 이후 추가됐다. D-75의 표본 수는 아직 proposed다. 근거: `docs/decisions/decision-register.md:133-135`.
- **추론:** 핵심 지연은 구현 속도가 아니라 “측정자를 실관통하면서 설계”한 데서 발생했다. 이 추론은 각 리뷰가 서로 다른 파일에서 같은 자기신고/앵커 결함을 반복해 찾았다는 패턴에 근거한다.
- **미확인:** 44개 커밋 중 각 원인이 소비한 실제 인시·모델 비용 비율은 기록이 없어 계산할 수 없다.

### US-2 관찰 — 권한 강제와 lifecycle이 같은 경로에서 양립하지 않는다

- **사실:** 비대화형 `codex exec` 터미널 채택은 `dispatch_input`에서 실패하고, TUI는 입력을 받는다. 비대화형 경로에서는 `worker_done`·heartbeat·ask가 오지 않는다. 근거: `adapters/orca/RUNBOOK.md:390-412`.
- **사실:** 교체 구현자의 `-s workspace-write`는 Orca IPC를 막아 `worker_done`·heartbeat·ask를 보낼 수 없었고, 위임자가 `worker-abandon`과 `task-update`로 정리해야 했다. 근거: `adapters/orca/RUNBOOK.md:707-720`.
- **사실:** 3차 기준에서도 검토자 TUI 채택이 다시 `dispatch_input`에서 실패했으며, transcript로 판정을 회수하고 Task를 수동 정리했다. 근거: `docs/planning/progress.md:99`.
- **사실:** 이번 조사 시점에도 Orca 앱과 runtime이 연결되지 않아 heartbeat가 실패했다. 조사 evidence의 `orca-runtime-status`와 실제 heartbeat 명령이 근거다.
- **추론:** 안전 경계가 데이터 쓰기뿐 아니라 오케스트레이터 제어 채널까지 차단하는 구조여서, 권한을 강하게 걸수록 lifecycle 수동 복구 비용이 생긴다.
- **미확인:** 현재 Orca 중단의 최초 원인이 앱 종료, bootstrap 노후화, 샌드박스 또는 다른 로컬 장애 중 무엇인지는 이 기록만으로 확정할 수 없다.

### US-3 관찰 — 표본은 흔들림을 드러냈지만 판정 기준을 고치지 않았다

- **사실:** 같은 고정 산출물에서 codex는 `PASS(0)·FAIL(1)·FAIL(4)`, claude는 `FAIL(6)·PASS(8)`을 냈다. findings가 더 많은데 PASS인 경우도 있었다. 근거: `docs/planning/open-questions.md:66-68`, `adapters/orca/RUNBOOK.md:1134-1141`.
- **사실:** D-74는 면당 표본 2개와 내부 일관성을 요구하지만, 문서 스스로 이것이 흔들림을 줄이는 장치가 아니라고 기록한다. 근거: `docs/decisions/decision-register.md:134`, `docs/planning/progress.md:145-153`.
- **사실:** 현재 reviewer parity 관측은 네 검토가 모두 FAIL이라 일관됐다. 다만 그 산출물은 `check-5`가 exit 1인 명백한 실패 사례였다. 근거: `fixtures/parity/pr-license-field-t1-reviewer-observed.yaml:8-18`, `docs/work/feat-20260829-license-field-46an/evidence/run_5a5a894aa26d.yaml:61-62`.
- **추론:** 모호한 사례에서의 verdict 규칙과 검토 절차가 충분히 결정적이지 않다. 표본 수를 늘리는 것만으로는 근본 원인을 줄이지 못하고 “불안정”을 더 확실히 표시할 뿐이다.
- **미확인:** 흔들림의 기여도는 verdict 기준의 모호함, 미추적 파일 대조 누락, 모델 비결정성, TUI/비대화형 기동 차이 사이에서 분리되지 않았다. 이것이 Q-10이다.

### US-4 관찰 — 최신 사실이 현재 체크아웃·실행 worktree·수동 상태 문서에 분산됐다

- **사실:** 진행 요약은 기준 `ecb4819` 이후 커밋이 있으면 다시 실측하라고 한다. 현재 HEAD는 `57a2628…`이고 `git log --oneline ecb4819..HEAD`에는 `3639e69`, `12f56ec`, `57a2628` 세 커밋이 있다. 근거: `docs/planning/progress.md:20-24`, 조사 evidence의 `current-head`·`progress-drift-commits`.
- **사실:** 진행 문서가 최신 3차 기준 PASS로 지목한 `run_42710f6ac93b` evidence/result/review는 impl5에 있지만 현재 체크아웃에는 없다. 조사 evidence의 `current-baseline-missing`, `impl5-baseline-present`, `impl5-status`가 근거다.
- **사실:** 현재 체크아웃의 라이선스 spec은 `status: active`이고 AC 4개가 모두 미체크지만, impl5 사본에서는 네 AC가 체크돼 있다. 근거: `docs/work/feat-20260829-license-field-46an/spec.md:13-16`, `docs/work/feat-20260829-license-field-46an/spec.md:41-46`, impl5의 같은 파일 `:42-45`.
- **사실:** RUNBOOK은 원시 로그가 있는 실행 worktree에서 close를 해야 하고, 그 뒤 별도 체크아웃으로 산출물을 복사·계약 재생성·관측 등록하도록 한다. 근거: `adapters/orca/RUNBOOK.md:628-666`, `adapters/orca/RUNBOOK.md:868-915`.
- **사실:** RUNBOOK의 관측 절은 새 장치가 미검증이라고 남긴 오래된 문장과 이미 3차 실전 관측이 끝났다는 진행 기록이 함께 존재한다. 진행 문서도 해당 하단 절이 낡았다고 경고한다. 근거: `adapters/orca/RUNBOOK.md:1143-1161`, `docs/planning/progress.md:39`.
- **추론:** 실행·로그·정본 수집·상태 갱신이 원자적이지 않아 “실행은 성공했지만 정본에는 없는” 중간 상태가 정상 경로가 됐다. 다음 세션은 상태 복원에 반복 비용을 쓴다.
- **미확인:** 현재 접근할 수 없는 오케스트레이터 내부에 파일에 없는 추가 lifecycle 상태가 있는지는 확인하지 못했다.

### US-5 관찰 — 미확정 강화 과제가 M2의 선행 순서에 섞였다

- **사실:** 현재 진행 문서는 교체 실행 전에 D-75 표본 수, Q-11 승인 서명, push 승인을 먼저 확정하라고 한다. 근거: `docs/planning/progress.md:29-36`.
- **사실:** D-75의 산출물 결박 부분은 구현됐지만 표본 수는 `proposed`이며 현재 코드는 PASS 1건 + WARN이다. Q-11도 미결이다. 근거: `docs/decisions/decision-register.md:135`, `docs/planning/open-questions.md:69`, `docs/planning/open-questions.md:87`.
- **사실:** 원래 M2 종료 조건에는 서명된 승인이나 현재 산출물당 PASS 2건이 없었다. close PASS·역할 교체 parity·제품 결과·CI PASS가 기준이었다. 근거: `docs/planning/implementation-plan.md:508-511`.
- **사실:** reviewer 면을 측정하려면 한 고정 산출물을 두 런타임에 보여주면 된다. RUNBOOK §6.6은 기준 구현자 worktree 하나를 고정한다. 현재 진행 순서는 impl5와 impl6 양쪽에서 표본을 만들도록 적어 목적이 중복된다. 근거: `adapters/orca/RUNBOOK.md:976-1007`, `docs/planning/progress.md:35`.
- **추론:** 보안·품질 후속 연구가 “M2를 닫기 위한 최소 조건”과 분리되지 않아 완료선이 계속 뒤로 이동한다.
- **미확인:** 사용자가 M2의 핵심 약속을 “구현자 면까지의 동등성”으로 보는지, “통과 산출물에서 검토자 판정까지 재현”으로 보는지는 현재 결정 문서만으로 하나로 확정되지 않는다.

## 근본 원인

### RC-1 [최우선] — 수직 슬라이스가 아니라 검증 플랫폼 전체를 첫 실관통에 묶었다

M2는 작은 기능 하나로 배관을 검증하는 실험처럼 보이지만, 실제 범위는 배관·권한·증거 무결성·리뷰·동등성·CI와 제품을 동시에 완성하는 프로그램에 가깝다. 특히 “판정을 실재에 묶는다”는 불변조건이 최초 명세의 실행 가능한 계약으로 분해되지 않고 리뷰에서 사후 발견됐다. 그래서 실관통은 제품 확인이 아니라 검사기 개발의 다음 라운드가 됐다.

**불필요/순서 판단:** 독립 리뷰와 위조 반박은 필요했다. 잘못된 것은 이 검증을 전체 배관 구현 뒤, 실제 T1과 동시에 한 순서다. 계약 생성 → evidence 재실행 → review 결박 → close를 먼저 결정론적 fixture 한 건으로 닫고, 그다음 Orca lifecycle, 마지막에 역할 교체 T1을 했어야 했다.

### RC-2 — 권한 경계와 lifecycle 제어 채널이 분리되지 않았다

현재 강제 수단은 파일 쓰기 위험뿐 아니라 Orca IPC도 함께 막는다. 그래서 강한 샌드박스와 자동 lifecycle 중 하나를 포기해야 하는 조합이 생겼다. 실행 성공, 산출물 존재, Task 상태, `worker_done`이 서로 다른 사실인데 런북이 이를 수동 복구로 이어 붙인다.

**불필요/순서 판단:** `worker_done`이 없다는 이유만으로 같은 구현을 다시 돌리는 것은 불필요하다. evidence/result 실재와 envelope/close를 먼저 확인하고, 그것이 유효하면 Task 상태만 수동 정리하는 것이 맞다. 반대로 Orca `reachable=false`에서 새 worker를 기동하는 것은 순서 오류다. RUNBOOK §1대로 먼저 중단해야 한다.

### RC-3 — reviewer의 PASS/FAIL 의미가 실행 가능한 판정표로 고정되지 않았다

리뷰 절차는 무엇을 읽을지는 말하지만 어떤 finding이 FAIL이고 어떤 finding이 PASS+주의인지 충분히 고정하지 않는다. D-74는 불안정을 숨기지 않는 안전장치지만 판정 일관성을 만드는 장치는 아니다. 쉬운 실패 사례에서의 일치는 모호한 통과 사례의 재현성을 증명하지 않는다.

**불필요/순서 판단:** PASS가 나올 때까지 표본을 계속 추가하는 것은 불필요하고 보안상 “review roulette”을 만든다. 면당 사전 고정한 2건에서 갈리면 즉시 `VERDICT_UNSTABLE`로 중단하고, 그 뒤는 표본 추가가 아니라 verdict 규칙 보강을 별도 승인 단위로 해야 한다.

### RC-4 — 실행 원본, 감사 로그, 정본 문서의 승격이 하나의 원자적 종료 단계가 아니다

로그는 worktree에만 있고, 비교기는 한 체크아웃의 상대 경로만 읽으며, 진행 상태는 사람이 갱신한다. 이 셋이 순차 작업이라 중간에 멈추면 최신 성공 증거가 정본에서 사라지고 과거 관측만 게이트를 계속 통과시킨다. 현재 상태가 정확히 그 사례다.

**불필요/순서 판단:** progress를 “기준 실행 완료”로 먼저 갱신하고 산출물 수집·실제 close를 나중에 두는 순서는 잘못됐다. 실행 worktree의 actual close → 정본 수집 → envelope 재검증 → parity → progress 갱신을 한 종료 배치로 묶어야 한다. 낡은 worktree 정리는 승인 대상이고 M2 종료 전에 필요하지 않다.

### RC-5 — 발견된 모든 중요한 위험을 같은 마일스톤의 차단 조건으로 승격했다

Q-10·Q-11·D-75는 중요한 문제지만 원래 M2 사용자 가치와 동일한 종류가 아니다. 승인 사건의 외부 서명은 신뢰 모델 강화이고, reviewer 흔들림의 원인 분석은 연구이며, close의 표본 2건은 비용 정책이다. 셋을 교체 실행 앞에 두면 미확정 결정이 현재 전달을 막는다.

**불필요/순서 판단:** Q-11과 push를 교체 실행보다 먼저 두는 것은 순서 오류다. push는 로컬 close와 정본 수집 뒤, 명시적 승인 후 현재 SHA의 CI를 확인할 때 필요하다. Q-10·Q-11은 별도 단위가 맞다. D-75(a)는 사용자가 더 강한 종료 의미를 선택할 때만 M2에 소급 적용해야 하며, 미승인 추천을 현재 게이트처럼 취급하면 안 된다.

## 불필요·중복·순서가 잘못된 단계

| 현재 단계 후보 | 판단 | 이유와 조정 |
| --- | --- | --- |
| impl5와 impl6 **양쪽**에서 reviewer-only 표본을 런타임당 2건씩 추가 | 중복 | reviewer 동등성은 한 고정 산출물에서만 측정하면 된다. 한다면 통과한 산출물 하나를 고르고 런타임당 정확히 2건으로 고정한다. |
| Q-10 원인 연구를 M2 close 전에 수행 | 불필요한 선행 | 연구 결과가 현재 제품 check-1~6이나 이미 구현된 close 앵커를 바꾸지 않는다. 별도 discovery 단위로 보낸다. |
| Q-11 승인 서명을 교체 실행 전에 확정 | 불필요한 선행 | 현재 구현은 `APPROVAL_CHAIN` WARN으로 위험을 드러낸다. 원래 M2 조건이 아니며 신뢰 모델 변경이라 별도 사용자 결정이 필요하다. |
| push 승인과 원격 CI를 로컬 close보다 먼저 처리 | 순서 오류 | 외부 반영 전에 두 worktree의 로컬 제품·review·close가 먼저 서야 한다. push는 마지막 외부 게이트다. |
| lifecycle 보고 실패 시 제품 실행 재시도 | 불필요 | 산출물과 evidence가 유효하면 `task-update` 복구로 충분하다. 재실행은 제품 차이를 하나 더 만든다. |
| progress 갱신 후 실제 close·수집 | 순서 오류 | status가 실재보다 앞선다. close와 수집·검증이 끝난 뒤 같은 기준 SHA로 progress를 갱신한다. |
| 낡은 worktree 삭제 | M2 비범위 | 비용은 디스크뿐이고 증거 원본이다. 삭제는 승인 대상이며 종료에 필요하지 않다. |

## 권고

### 추천안 — M2를 “종료 배치”와 “reviewer 신뢰성 연구”로 지금 분리한다

가장 적합한 선택은 더 많은 표본을 바로 돌리는 것이 아니라, **현재 합의된 동작으로 M2의 제품·실행 배관을 닫고 reviewer 재현성/Q-10·승인 서명/Q-11·D-75(a)는 별도 승인 단위로 분리하는 것**이다.

M2 종료 배치에 남길 것은 다음뿐이다.

1. Orca가 `ready/reachable`로 복구된 뒤, impl5의 기존 `run_42710f6ac93b`를 다시 구현하지 않고 **actual close**한다.
2. 같은 base `7f8ecd7`의 준비된 impl6 `run_e82929ee03da`를 한 번 기동해 교체 구현·교차 리뷰·필수 검사·actual close를 끝낸다. lifecycle 메시지가 막혀도 유효한 evidence/result가 있으면 재구현하지 않고 수동 Task 정리만 한다.
3. 두 실행의 evidence/result/review를 정본 체크아웃으로 모으고 계약을 재생성한 뒤 `envelope check`와 parity를 실행한다.
4. 최신 산출물이 포함된 parity 결과와 두 close가 서면 progress를 갱신한다.
5. 그 뒤에만 push 대상을 보여주고 명시적 승인을 받아 원격 CI에서 **그 SHA**의 성공을 확인한다.

이 종료 배치에서는 통과 산출물 reviewer 표본을 추가로 수집하지 않는다. 따라서 최종 표현은 과장 없이 “구현자 면의 역할 교체 동등성과 각 제품의 독립 리뷰·close를 확인했다; 통과 산출물에서 reviewer 판정 재현성은 미확인”이어야 한다. reviewer 동등성까지 M2의 필수 약속으로 유지하려면 아래 ‘추천이 달라지는 조건’을 적용한다.

**비용:** 이미 끝난 impl5를 다시 만들지 않고 pending impl6 한 번에 집중한다. 동일 산출물 표본을 양쪽 worktree에서 중복 생성하는 모델 비용을 피한다.  
**운영:** 실제 close → 수집 → parity → progress의 단일 순서를 사용해 다음 세션 복원 비용을 줄인다.  
**보안:** 과거 FAIL·WARN·미봉인 기록은 삭제하지 않는다. D-75/Q-11을 없애는 것이 아니라 별도 승인 단위로 유지하고, push는 여전히 명시적 승인 뒤에만 한다.  
**이전 가능성:** Markdown·JSON·YAML·git SHA를 그대로 사용하므로 Orca 외 실행기로 옮겨도 산출물 계약은 유지된다. 바뀌는 것은 lifecycle adapter뿐이다.  
**후속 승인:** 필요하다. M2의 종료 표현을 “구현자 면 + 각 제품 review/close, reviewer 재현성은 별도”로 확정하고 Q-10·Q-11·D-75(a)를 분리하는 것은 진행 계획과 제품 수준 종료 의미를 바꾸기 때문이다. 이 보고서는 그 변경을 직접 반영하지 않았다.

### 추천이 달라지는 조건

사용자가 M2의 핵심 약속을 **“통과한 동일 산출물에서 두 reviewer 런타임의 verdict도 재현 가능해야 한다”**로 확정하면 M2를 지금 닫지 않는다. 대신 코드나 제품 재관통 전에 별도 reviewer-calibration spike를 승인해 다음 세 가지를 먼저 고정한다.

1. finding 심각도와 `gate_verdict`의 결정표.
2. 미추적 파일·증거 앵커·수용 기준별 필수 대조 목록.
3. TUI/비대화형 중 하나의 고정 기동 경로와 동일 프롬프트 해시.

그 후 한 **통과 산출물 하나**에서 런타임당 정확히 2건을 실행한다. 어느 면이든 갈리면 표본을 더 돌리지 않고 `VERDICT_UNSTABLE`로 중단한다. 이 경우 M2 비용은 늘지만, 무엇을 증명하려는지가 고정돼 재작업은 줄어든다.

## 다음 확인

다음 표는 원인별 가장 작은 검증과 중단 기준이다. “명령을 돌렸다”가 아니라 오른쪽 성공 신호까지 확인해야 한다.

| 우선 | 최소 다음 검증 | 완료 신호 | 즉시 중단 기준 | 승인 |
| --- | --- | --- | --- | --- |
| 1 | `orca status --json` | `runtime.state == "ready"`와 `runtime.reachable == true` | 지금처럼 `stale_bootstrap` 또는 `reachable=false`면 worker를 띄우지 않는다 | 앱 복구 자체가 외부 상태를 바꾸는 방식이면 사람 확인 후 |
| 2 | impl5에서 `bin/romeo close --unit feat-20260829-license-field-46an --root <impl5>` | exit 0, 첫 줄 PASS, 모든 차단 검사가 PASS | UNVERIFIED/FAIL 한 줄이라도 있으면 수집·push 중단; 제품 재구현은 하지 않고 그 검사만 원인 분리 | destructive 아님, 단 status 변경을 실제 반영하기 전 현재 작업 승인 경계 확인 |
| 3 | impl6의 기존 계약 두 개 해시를 impl5/정본 계약과 대조 후 한 번 기동 | 같은 base/spec/checks, evidence의 task/dispatch id 일치, check-1~6 exit 0, reviewer 봉투 1건 | 계약 바이트가 다르거나 dispatch 입력 실패 후 산출물이 없으면 재시도 전에 잔여 자원과 원인 보고 | 정상 위임은 기존 M2 범위; 외부/파괴 작업 없음 |
| 4 | impl6 actual close | exit 0과 재실행 대조 PASS | reviewer가 FAIL이면 PASS가 나올 때까지 재검토하지 않는다. finding을 별도 수정 단위로 보낸다 | 수정 필요 시 새 승인 단위 |
| 5 | §6.3 수집 후 4개 최신 봉투 `envelope check`, 최신 run으로 parity 등록 | envelope 검사 전부 PASS, parity exit 0, 보고서가 비교 불가 면을 명시 | 최신 run이 아니라 과거 run을 가리키거나 current checkout에 evidence가 없으면 progress 갱신 중단 | 정본 파일 반영·커밋 범위는 사람 확인 |
| 6 | push 전 `git diff --name-only <마지막 원격 SHA>..HEAD` 제시 | 사용자가 대상 SHA·변경 범위를 보고 승인 | 승인 전 `git push` 금지 | **명시적 승인 필수** |
| 7 | 승인 후 원격 CI 최신 1건 확인 | push한 정확한 SHA의 workflow success | 과거 `b53f08c` 성공이나 다른 SHA 성공을 현재 증거로 쓰지 않는다 | push 승인 뒤 |

이번 보고서 작성 시점의 중단 판단은 명확하다. **Orca runtime이 reachable하지 않으므로 교체 실행이나 외부 반영을 시작하면 안 된다.** 보고서·증거·결과 봉투 작성과 로컬 required checks까지만 수행한다.

## 근거 색인과 한계

핵심 명령은 `docs/work/feat-20260829-m2-root-cause-review-20260829-44hm/evidence/run_3589e602e8e0.yaml`에 task `task_7a4615906774`, dispatch `ctx_d15deb955498`로 기록했다.

| evidence label | 정확한 명령 | 해석 |
| --- | --- | --- |
| `current-head` | `git rev-parse HEAD` | 조사 기준 SHA `57a2628…` |
| `current-status` | `git status --short` | 조사 시작 시 허용 작업 단위의 task/evidence만 미추적 |
| `progress-drift-commits` | `git log --oneline ecb4819..HEAD` | 수동 상태 기준 뒤 커밋 3개 |
| `current-ci-lookup` | `gh run list --limit 1 --json databaseId,headSha,status,conclusion,workflowName,createdAt,updatedAt,url` | exit 1; 현재 원격 상태를 확인하지 못함 |
| `orca-runtime-status` | `orca status --json` | 앱 미실행·runtime unreachable |
| `current-parity` | `bin/romeo fixtures parity --report` | exit 0; 과거 관측 2건 기준, 한 면 비교 불가 |
| `m2-commit-count` | `git rev-list --count 0f10bfa^..ecb4819` | 44; 시간 비용 자체의 계측은 아님 |
| `impl5-status` | `git -C /Users/julliettelee/orca/workspaces/Romeo-Harness/impl5-feat-20260829-license-field-46an status --short` | 최신 기준 산출물과 22개 제품 변경이 그 worktree에 남음 |
| `impl6-status` | `git -C /Users/julliettelee/orca/workspaces/Romeo-Harness/impl6-feat-20260829-license-field-46an status --short` | 교체 계약 두 개만 준비됨 |
| `current-baseline-missing` | `test ! -f docs/work/feat-20260829-license-field-46an/evidence/run_42710f6ac93b.yaml` | 현재 체크아웃에 최신 evidence 없음 |
| `impl5-baseline-present` | `test -f /Users/julliettelee/orca/workspaces/Romeo-Harness/impl5-feat-20260829-license-field-46an/docs/work/feat-20260829-license-field-46an/evidence/run_42710f6ac93b.yaml` | impl5에는 존재 |

다음은 **미확인**으로 남긴다.

- 현재 HEAD의 GitHub Actions 최신 상태와 성공 여부.
- 현재 Orca 앱이 중단된 최초 원인과 coordinator가 보유한 최신 lifecycle 상태.
- impl6 실행 결과, 교체 제품의 실제 diff, reviewer 판정, close 결과.
- 통과 산출물에서 reviewer verdict가 재현되는지와 Q-10의 원인 분해.
- D-75 표본 수와 Q-11 승인 서명에 대한 사용자의 최종 결정.
- 독립 reviewer의 이 보고서 근거 링크·과장 여부 판정. 이 항목은 구현자가 스스로 완료로 선언하지 않는다.
