# M2 수정 작업 계획 — 뼈대를 세우고 일단 완성한다 (제안, 사용자 확정 대기)

> **상태:** 제안이다. 아직 승인·확정·구현되지 않았다. 특히 아래 완료 정의는 현재 `v1-scope.md`의 “역할 교체 후 동일 게이트 판정” 문구를 구체적으로 바꾸므로, PM의 명시 승인 없이 적용할 수 없다.

## 확인란

- **무엇을:** M2의 완료를 두 게이트로 다시 정의한다. **(A) 런타임 동등성 게이트**는 같은 승인 Spec에서 두 역할 바인딩이 기동되고, 같은 Task/Result 스키마·AC·`required_checks`·권한 상한·결정적으로 계산된 product gate를 사용하는지 확인한다. **(B) 제품 완료 게이트**는 canonical `impl5` 산출물 한 건이 라이선스 AC 네 개와 deterministic check 여섯 개를 통과하고, 현재 산출물에 대한 독립 review 한 건의 finding이 해소된 뒤 `close`되는지 확인한다. LLM이 자유 형식으로 쓴 `PASS/FAIL`의 런타임 간 일치는 M2 gate에서 빼고 Q-10의 품질 실험으로 남긴다. 기존 swap 관측은 역할·봉투 wiring smoke 증거로 재사용하고, `impl6`에서 payload를 다시 만드는 full swap은 중단한다.
- **왜:** 현재 관측은 같은 산출물·같은 런타임에서도 reviewer verdict가 바뀐다는 것을 보여준다. 표본을 늘리거나 불안정한 면을 제외해도 “같은 품질”의 참값은 생기지 않는다. 반면 schema·checks·권한·현재 산출물 재실행은 명령과 exit code로 닫을 수 있다. 목표를 이 경계로 나눠야 한 번의 정상 payload가 더 이상 새 hardening 때문에 낡지 않는다.
- **기대 결과:** PM은 (1) 어느 런타임이 역할을 맡아도 같은 계약과 검사 규칙이 투영된 리포트, (2) 18개 아카이브의 license 필드·README 열·검증기, (3) 여섯 check exit 0, (4) 현재 artifact 1건에 묶인 review와 `close` exit 0, (5) M2 완료와 아직 남은 v1 항목을 분리한 상태표를 눈으로 확인할 수 있다.
- **수용 기준:** 아래 6개가 모두 같은 최종 revision/작업 트리를 가리켜야 한다.
  1. `python3 -m unittest discover -s tests` → exit 0.
  2. `bin/romeo compile --check`와 `bin/romeo doctor` → exit 0. doctor의 reviewer 두 칸은 관측됨, implementer 미관측 칸은 숨기지 않고 별도 위험으로 출력.
  3. Spec의 `required_checks` 여섯 개(`docs/work/feat-20260829-license-field-46an/spec.md:70-90`) → 전부 exit 0. 특히 `python3 scripts/check-archive-licenses.py`가 18개 값을 계획 표와 대조하고, `python3 scripts/generate-archive-index.py --check`가 PASS.
  4. 현재 artifact에 대한 독립 review는 정확히 1건. FAIL이면 같은 artifact를 다시 돌려 PASS를 기다리지 않고 finding을 수정하거나 PM이 수용 여부를 결정한다. 변경된 artifact만 새 review를 받는다.
  5. `bin/romeo close --unit feat-20260829-license-field-46an --root <canonical-root> --dry-run`과 실제 close → exit 0, `FRESH_HEAD`, `FRESH_TREE`, `REQUIRED_CHECK_RERUN`, `EVIDENCE_LOG`, `REVIEW_VERDICT`가 현재 artifact를 가리키고 status가 `done`.
  6. 수정된 parity report가 두 역할의 schema·동일 check set·권한 profile·결정적 product gate를 PASS로 보여주고, `reviewer_verdict`는 `advisory/not-gated`라고 명시. `git status --short`에는 승인된 파일만 남고 push는 0건.
- **위험과 되돌리기:** 가장 큰 위험은 자유 형식 reviewer verdict를 gate에서 뺀 것이 실제 품질 차이를 숨길 수 있다는 점이다. 이를 줄이기 위해 review 자체와 finding 해소는 남기고, 결정적 AC/check를 제품 gate로 유지한다. 이 변경은 정책·문서·parity 판정의 작은 revision으로 분리해 한 커밋으로 되돌릴 수 있고, D-74 표본 코드는 삭제하지 않고 비활성 profile로 남겨 Q-10 실험에서 다시 켤 수 있다. `impl1`~`impl6` worktree는 별도 승인 전 삭제하지 않아 복구 근거를 보존한다.

## 잘라내거나 미루는 것 (항목 · 왜 · 어디에 기록하는가(open-questions/decision-register) · v1 요구 위반 여부)

| 항목 | 왜 지금 자르는가 | 기록 위치 | v1 요구 위반 여부 |
| --- | --- | --- | --- |
| D-74의 reviewer 런타임당 2표본과 추가 8회 재실행 | 같은 런타임 내부 verdict가 흔들려 표본 2개로 참값을 만들 수 없다. 불안정하면 비교 면을 제외할 뿐이다. | `open-questions.md` Q-10에 “review calibration experiment”로 유지하고, 새 결정 D-76에 M2 비게이트를 기록 | **현재 문구를 그대로 읽으면 위반 소지가 있다.** `v1-scope.md:64-67`의 “동일 게이트 판정”을 결정적 product gate로 명시하는 승인된 개정이 선행돼야 한다. |
| `impl6`의 full payload 재구현·재검토 | 역할과 envelope wiring은 기존 observed case로 확인됐고, 현재 제품 품질은 `impl5` 한 건으로 닫을 수 있다. 같은 기능을 다시 만드는 비용이 품질 보증으로 전환되지 않는다. | D-76에 “adapter smoke 증거 재사용, current payload full swap 미실행”과 한계를 기록 | **현 정본의 ‘같은 작업 역할 교체 재현’을 엄격히 해석하면 위반이다.** 따라서 이 절충안을 승인하지 않으면 impl6는 생략할 수 없다. |
| 새로운 로그 hash·봉인·옛 승인 위조 방어 | 현재 체계도 부주의·표류는 잡고 required check를 재실행한다. 일관된 로컬 위조는 로컬 hash를 늘려도 못 막는다. | Q-11에 외부 신뢰 anchor가 필요해지는 조건과 함께 기록 | 위반 아님. v1은 한 사람 로컬 사용이며 외부 공격자·서명을 요구하지 않는다(`docs/requirements/v1-scope.md:96-111`). |
| Q-11 외부 승인 서명/원격 ledger | 사용자·권한 관리와 외부 신뢰 기반이 없는 현재 로컬 v1에는 비용과 운영 복잡성이 더 크다. | Q-11을 `deferred`로 유지하고 “2인 이상/감사 요구/공유 CI”를 도입 trigger로 명시 | 위반 아님. V-8은 인증정보 없는 부착 상태만 요구한다. |
| unchanged artifact에 대한 PASS 재시도 | 판정 룰렛을 만들고 실패 finding을 지운다. | D-75 선택과 review workflow에 “artifact가 바뀌어야 재검토” 기록 | 위반 아님. 독립 review는 남는다. |
| Orca lifecycle 완전 자동화 | sandbox가 Orca IPC를 막아 현재 구조에서는 강제와 자동 `worker_done`을 동시에 만족시키지 못한다. | open question에 host-mediated relay 설계 후보와 `lifecycle: degraded`를 기록 | 위반 아님. v1은 실행 상태 주인과 권한 상한을 요구하지만 heartbeat 자동화를 요구하지 않는다. |
| 매 run의 live upstream 네트워크 대조 | pinned vendor의 출처 검증은 gate/update 시 필요하지만, payload 관통마다 네트워크에 의존하면 재현성과 속도가 나빠진다. | vendor 정책 결정에 “update/release 시 실행” 기록 | 위반 아님. provenance는 유지한다. |
| full attach/update·T2 Charter·shadow 20건 | 이 항목들은 v1에는 남지만 M2 core parity와 같은 단계가 아니다. | 기존 M3~release 계획과 V-0/V-2/V-10 추적에 유지 | **v1 전체에서 삭제하면 위반.** M2에서만 분리하며 v1 release 전에 별도로 완료해야 한다. |
| push | 외부 저장소 상태를 바꾸며 로컬 M2 완료의 증거가 아니다. | 별도 배포/통합 승인 항목 | 위반 아님. 로컬 close 뒤 별도 명시 승인을 받아야 한다. |

## 남기는 것과 순서 (단계 · 명령/행동 · 완료 신호 · 예상 소요)

> **예상 소요의 가정:** 현재 398개 테스트가 계속 통과하고 `impl5` 기록과 실제 파일이 일치하며, 새로운 acceptance-blocking finding이 없다는 조건이다. 이 조건이 깨지면 시간 예측보다 해당 사실을 먼저 보고한다.

### 세션 1 — 완료 정의를 고정하고 더 이상 spine을 움직이지 않는다 (약 60~90분)

| 단계 | 명령/행동 | 완료 신호 | 예상 소요 |
| --- | --- | --- | --- |
| 1. PM 결정 | 이 확인란을 승인하거나 “현 정본 유지”를 선택한다. | 승인 메시지에 새 M2 정의·impl6 생략·D-75 선택이 명시됨 | 10분 |
| 2. 정본 개정 | 승인 시 `v1-scope.md`, `decision-register.md`에 D-76, `open-questions.md` Q-10/Q-11, M2 checklist만 최소 수정한다. M2와 v1 release를 분리한다. | 정본에서 deterministic product gate와 advisory reviewer verdict가 서로 다른 필드/용어로 정의됨 | 20~30분 |
| 3. 최소 판정 변경 | parity가 schema·required checks·permission profile·결정적 product gate만 비교하고 reviewer verdict를 보고만 하게 한다. D-74 코드는 삭제하지 않고 비활성 실험 profile로 둔다. | 새 회귀 테스트: 같은 FAIL 네 건이더라도 “quality PASS”라고 인쇄하지 않고 `reviewer_verdict: advisory`; deterministic mismatch는 FAIL | 20~35분 |
| 4. spine 동결 검사 | `python3 -m unittest discover -s tests`; `bin/romeo compile --check`; `bin/romeo fixtures parity --report` | 모두 exit 0. 새 hardening finding을 이 세션 범위에 추가하지 않음 | 10~15분 |

### 세션 2 — 현재 payload 한 건을 끝까지 닫는다 (약 60~90분)

| 단계 | 명령/행동 | 완료 신호 | 예상 소요 |
| --- | --- | --- | --- |
| 5. canonical 선택 | `impl5`의 HEAD·dirty tree·22개 변경 파일을 현재 기록과 대조한다. 다른 impl worktree는 읽기만 하고 합치지 않는다. | 범위가 `archive/*/_source.md`, `archive/README.md`, 두 기존 script, 새 check script, 작업 단위 산출물로 제한됨 | 10분 |
| 6. 제품 검사 | Spec의 check-1~6을 `impl5`에서 evidence 명령으로 새로 실행한다. | 여섯 명령 exit 0, AC-1~4 체크, evidence의 HEAD/tree가 현재 값과 일치 | 15~25분 |
| 7. 독립 review 1회 | 현재 artifact를 read-only reviewer에게 한 번만 보낸다. unchanged artifact 재시도 금지. | result envelope schema PASS; finding 0 또는 각 finding의 수정/PM 수용 기록 | 15~25분 |
| 8. close | 같은 worktree에서 `close --dry-run`, 이어 실제 `close`. | 두 명령 exit 0, status `done`, current 갱신, WARN과 미검증 항목 0. 단 D-75 표본 수만 승인된 WARN 정책이면 예외로 명시 | 10~15분 |
| 9. 통합 전 점검 | 의도한 diff·`git status --short`·최종 test를 확인한다. 로컬 commit/현재 branch 반영은 승인된 통합 방식으로만 한다. | main 또는 승인된 integration revision에 payload와 작업 단위 evidence가 함께 존재; 불필요한 impl 파일 0 | 10~15분 |
| 10. M2 상태 갱신 | M2를 `done`, 아직 남은 V-0/V-2/V-10·attach 항목을 `not done`으로 분리 기록한다. | “M2 완료”가 “v1 release 완료”로 표현되지 않음 | 5분 |

### 이 순서에서 하지 않는 일

- `impl6` 기동, reviewer 8회 추가 표본, 새 adversarial review round, 새 hash layer, 외부 signing, push, PR, worktree 삭제를 섞지 않는다.
- 최종 검증에서 새 결함이 나오면 **현재 AC/권한/데이터 손상/close를 직접 막는가**만 판정한다. 맞으면 한 번 고치고 해당 검사만 재실행한다. 아니면 새 작업 단위로 기록하고 M2를 다시 열지 않는다.
- 한 세션에서 같은 artifact의 reviewer verdict가 달라졌다는 이유만으로 재시도하지 않는다. 그것은 Q-10의 관측이지 제품 수정 사유가 아니다.

## 지금 열려 있는 결정(D-75 · Q-11 · push)에 대한 추천 1개씩과 이유

### D-75 — **옵션 (b), 현재 artifact의 PASS 1건 + 표본 수 WARN**

추천 이유는 표본 2개가 신뢰도를 결정적으로 높이지 못한다는 실측이 이미 있기 때문이다. 같은 artifact에서 verdict가 달라지면 2개는 오히려 close를 영구 미판정으로 만든다. v1에서는 현재 artifact의 독립 review 1건을 요구하고, FAIL이면 unchanged artifact를 재시도하지 말고 finding을 처리한다. 표본 수 WARN은 남겨 한계를 숨기지 않는다. 다수 reviewer 합의가 필요한 조직 사용은 Q-10의 별도 실험으로 승격한다.

### Q-11 — **외부 승인 서명은 미룬다**

현재 위협 모델은 한 명이 로컬에서 쓰며 부주의·표류·손작성 허위 완료를 잡는 것이다. 동일 사용자가 YAML·로그·hash를 모두 다시 쓸 수 있다는 경계는 로컬 서명 파일로도 이동하지 않는다. 두 명 이상 승인, 감사 추적, 공유 CI, 규제 요구 중 하나가 생길 때 외부 append-only store나 서명자를 설계한다. 그 전에는 `APPROVAL_CHAIN WARN`과 현재 승인 1건 제한이 비용·운영·보안의 균형이 가장 낫다.

### push — **로컬 close 뒤 별도 명시 승인을 받아 한 번만 한다**

push는 M2를 완성하지 않고 외부 저장소 상태만 바꾼다. 먼저 canonical revision에서 tests·checks·review·close와 의도한 diff를 확인한다. 그 결과와 push 대상 branch/commit, 되돌리기 방법을 PM에게 보여준 뒤 별도 승인을 받는다. 이번 수정 계획 승인과 push 승인을 묶지 않는다.

## 이 계획이 틀릴 수 있는 조건

1. **PM이 “자연어 reviewer verdict까지 두 런타임에서 같아야 한다”를 제품의 핵심 가치로 고수하는 경우.** 그러면 이 계획의 cut은 요구 위반이다. 다만 현재 관측상 1~2 세션 완료 약속은 철회해야 하며, 반복 횟수·통계적 합격 기준·모델 버전 고정·비용 상한을 먼저 새 요구사항으로 정의해야 한다.
2. **`impl5` 파일이 기록과 다르거나 여섯 check 중 하나가 현재 실패하는 경우.** canonical 후보라는 가정이 틀린 것이다. 그 실패만 재현·수정한 뒤 새 evidence를 만들며, 과거 PASS를 사용하지 않는다.
3. **독립 review 1건이 AC 위반·잘못된 라이선스·데이터 손상 가능성을 찾는 경우.** 그 finding은 advisory가 아니라 제품 gate blocker다. 수정 뒤 artifact hash가 바뀌었을 때만 새 review를 한 번 받는다.
4. **외부 감사자·다중 사용자·공유 CI가 이미 v1의 실제 사용 조건인 경우.** 현재 “한 사람 로컬” 위협 모델이 틀렸으므로 Q-11 서명/외부 ledger와 권한 감사를 M2 전에 다시 설계해야 한다.
5. **Orca lifecycle 자동 완료가 사용자 가치의 필수 조건인 경우.** degraded lifecycle을 허용할 수 없으므로 host-mediated IPC relay 또는 allowlisted control channel이 선행 작업이 된다. 이 경우 1~2 세션 범위를 넘어갈 수 있다.
6. **기존 observed swap이 현재 adapter revision의 증거로 인정될 수 없는 경우.** `impl6` full swap을 생략할 수 없다. 그때는 새 요구사항 변경 없이 현 정본대로 한 번만 실행하되, reviewer 표본 8회와 새로운 hardening은 여전히 분리한다.

