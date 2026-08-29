# M2 가 끝나지 않는 근본 원인 — 독립 재검토 (Codex, 2026-08-29)

## 한 줄 결론

**가장 큰 원인은 목표 설정 오류다.** 원래의 얇은 수직 슬라이스 계획 전체가 틀린 것은 아니지만, 비결정적인 LLM 검토자의 자연어 `PASS/FAIL`까지 “역할을 바꿔도 같은 판정”이어야 한다고 정의한 순간 M2는 유한한 검증 목표가 아니게 됐고, 이를 계획의 중단 규칙 없이 구현 결함처럼 다루면서 표본·봉인·재실행이 계속 늘어났다.

## 요약 (5줄 이내, 심각한 것부터)

1. 같은 산출물을 본 같은 런타임도 `PASS/FAIL`이 바뀌었다. 이 관측 아래에서 자연어 리뷰 판정의 일치는 결정적 게이트가 될 수 없다.
2. §10의 17행부터 원 계획 밖 보완이 들어왔고, 28행 이후에는 “수직 슬라이스를 닫는 데 필요한 결함”과 “로컬 위조까지 막는 일반 하드닝”을 나누는 중단 규칙이 사라졌다.
3. 현재 동등성 리포트의 PASS는 네 검토자가 모두 실패한 깨진 산출물에서도 성립한다. 이는 **같음**을 보여줄 뿐 **품질**을 보여주지 않는다.
4. 1,164줄 RUNBOOK은 실행 계약을 자동화하지 못해 한 번의 기준·교체·표본 경로를 최소 72개 수동 행동 묶음으로 만들고, 샌드박스는 같은 IPC를 막아 lifecycle과 충돌한다.
5. 기존 테스트·라우팅·컴파일·검토자 읽기 전용은 상당 부분 동작한다. 따라서 전면 재작성보다 판정 목표를 결정적 게이트와 리뷰 의견으로 분리하고 한 개의 현재 산출물을 닫는 것이 맞다.

## 유저스토리별 진단

### US-1 「PM 으로서 요청을 던지면 필요한 문서만 만들어지고 확인란만 읽고 승인하고 싶다」

- **이 이야기에서 하네스가 하는 일:** 요청을 `unit/mode/facet`으로 분류하고, 정책표가 필요한 Brief·Tech Spec만 계산해 만든 뒤, PM에게는 Tech Spec의 확인란만 승인 대상으로 보여준다. 이 흐름은 v1의 V-0~V-4와 최소 흐름 앞부분에 해당한다(`docs/requirements/v1-scope.md:34-38`, `docs/requirements/v1-scope.md:53-60`).
- **지금 상태:** 분류 계산기는 실측에서 `33/33` 픽스처를 통과했고 `bin/romeo --help`에도 `route`, `new`, `approve`가 노출됐다. 라이선스 작업의 확인란도 무엇·이유·기대 결과·AC·복구를 갖춘 승인 가능한 형태다(`docs/work/feat-20260829-license-field-46an/spec.md:34-47`). 다만 v1 전체 기준으로는 T2 Charter 템플릿이 없고 V-10 shadow 20건도 아직 끝나지 않았다(`docs/requirements/v1-scope.md:36-45`). 이것은 **M2 미완료의 직접 원인**은 아니며, M2를 v1 전체 완료와 혼동하면 생기는 별도 범위 문제다.
- **막히는 곳과 근본 원인:** 요청→문서→승인 자체가 막힌 것이 아니라, 승인 뒤 실행 경로가 계속 변하면서 승인된 `base_sha`, 현재 작업 트리, 증거가 반복해서 낡았다. 이는 분류 설계 결함보다 **M2 실행 중 계약을 계속 확장한 계획·프로세스 문제**다. 진행표도 승인·봉투·재승인·승인 사슬을 21·22·37·38·41·45행에서 연달아 보강했다(`docs/planning/progress.md:74-98`).
- **불필요했던 단계:** 깨끗한 새 작업 단위 하나를 끝내는 데 필요한 승인 기록은 1회다. 이미 승인된 작은 작업을 대상으로 재승인 호환성·옛 승인 위조·외부 승인 서명까지 함께 해결하려 한 것은 현재 유저스토리보다 넓었다.
- **권고:** M2와 v1 release를 분리한다. M2에서는 현재 승인 1건과 현재 산출물 1건만 닫고, T2 Charter·shadow 20건·일반 재승인 마이그레이션은 각 원래 마일스톤에 남긴다.

### US-2 「PM 으로서 구현이 끝났다는 말을 믿지 않고 증거로 완료를 확인하고 싶다」

- **이 이야기에서 하네스가 하는 일:** 구현자가 주장한 명령·종료 코드·산출물 식별자를 기록하고, `close`가 현재 체크아웃에서 같은 명령을 다시 실행해 주장과 실물을 맞춘다. Evidence는 “로그를 저장하는 기능”이 아니라 **현재 바이트가 AC를 만족한다는 완료 근거**다(`docs/requirements/capability-map.md:121-142`, `docs/work/feat-20260829-license-field-46an/spec.md:66-90`).
- **지금 상태:** 단위 테스트는 이번 리뷰에서 `398 tests`, exit 0이었다. 그러나 현재 루트에서 `bin/romeo close --unit feat-20260829-license-field-46an --root "$PWD" --dry-run`은 exit 1이었다. 현재 HEAD·트리와 선택된 evidence의 `head_sha`·`dirty_tree_hash`가 다르고, check-5 기록이 exit 1이며, 네 AC가 미체크이고, 원시 로그와 review run 로그가 이 체크아웃에 없기 때문이다. 이 거부는 오작동이 아니라 **현재 루트가 완료 증거를 갖지 않았다는 올바른 판정**이다.
- **막히는 곳과 근본 원인:** 최신 제품 변경과 원시 로그는 `impl5`에 있고, 정본 진행 문서·parity fixture·정책 코드는 현재 루트에 있다. `close`는 한 루트 안의 현재 트리와 로컬 `.harness/runs`를 요구한다. 즉 증거의 신선도 규칙은 맞지만, **상태를 여러 워크트리에 흩어 놓고 수동으로 모으는 실행 구조**가 그것을 계속 무효화한다. 현재 루트에는 라이선스 payload 커밋도 없다.
- **불필요했던 단계:** 기록 YAML·원시 로그·봉투·승인 커밋·현재 트리를 각각 다시 봉인하는 여러 겹 중, “현재 체크아웃에서 required checks 재실행”이 종점이다. 로컬 사용자가 모든 로컬 파일을 일관되게 위조하는 경우는 해시를 더 붙여도 막지 못한다는 뒤늦은 위협 모델 자체가 이를 인정한다(`docs/planning/progress.md:218-233`).
- **권고:** 한 canonical worktree를 고르고 그곳에서 6개 deterministic check→현재 산출물 1회 review→`close`를 연속 실행한다. 다른 워크트리의 옛 evidence를 현재 close의 입력으로 승격하지 않는다.

### US-3 「PM 으로서 두 AI 중 누가 구현·검토하든 같은 품질을 기대하고 싶다」 (동등성)

- **이 이야기에서 하네스가 하는 일:** 공통 Spec·AC·권한·결과 봉투를 두 런타임 형식으로 투영하고, 역할을 바꿔도 계약 형식과 결정적 검사가 유지되는지 확인한다. 이는 “같은 프롬프트”가 아니라 “같은 계약과 검증 규칙”을 요구하는 구조다(`docs/requirements/capability-map.md:83-105`).
- **지금 상태:** 역할 교체 실행 경로와 parity 검사기는 존재한다. 하지만 같은 산출물을 같은 계약으로 본 Codex 검토자가 `PASS(0)·FAIL(1)·FAIL(4)`, Claude 검토자가 `FAIL(6)·PASS(8)`을 냈다(`.harness/observations.yaml:169-241`, `adapters/orca/RUNBOOK.md:858-863`). `bin/romeo fixtures parity --report`는 현재 PASS지만, 관측 케이스의 네 reviewer가 모두 FAIL이고 해당 산출물의 unittest check도 exit 1인 케이스가 reviewer 동등성 PASS의 근거다(`fixtures/parity/pr-license-field-t1-reviewer-observed.yaml:1-46`). 따라서 이 PASS는 품질 성공이 아니라 **실패 문자열의 일치**다.
- **막히는 곳과 근본 원인:**
  - **목표 설정 오류(주원인):** 자유 형식 LLM 판정을 결정적 동등성 게이트로 삼았다. 표본을 두 개로 늘려도 참값이 생기지 않고 비용만 두 배가 된다. 표본이 흔들리면 그 면을 `VERDICT_UNSTABLE`로 제외하므로, 게이트는 통과할 수 있어도 처음 주장한 “두 검토자가 같은 판정”은 증명하지 못한다(`adapters/orca/RUNBOOK.md:858-866`).
  - **설계 결함(부원인):** 제품 품질과 런타임 동등성을 같은 `gate_verdict`에 담았다. 동등성은 계약·권한·검사 목록의 일관성을, 품질은 현재 산출물의 AC와 검사 결과를 봐야 한다.
  - **구현 결함(실재하지만 2차적):** 다른 산출물 비교, 낡은 evidence 선택, reviewer 봉투 결박 누락 등은 실제 버그였고 수정 가치가 있었다. 그러나 그것을 모두 고쳐도 자연어 판정의 비결정성은 남는다.
- **불필요했던 단계:** D-74 이후의 reviewer 표본 증설은 이미 관측된 불안정을 해결하지 않는다. 같은 artifact를 계속 재검토해 PASS를 기다리는 방식은 품질 검증이 아니라 룰렛이 된다.
- **권고:** “동일 gate 판정”을 **required checks·봉투 스키마·권한 가드에서 계산되는 결정적 product gate**로 한정하고, LLM review verdict/findings는 별도 품질 관찰로 표시한다. 이는 현재 v1 문구(`docs/requirements/v1-scope.md:64-67`)를 해석만으로 바꾸는 일이 아니라 요구사항 수정이므로 PM의 명시 승인이 먼저 필요하다.

#### 원래 M2와 §10 17~46행 대조

원래 M2의 최소 범위는 실제 T1 한 건, 같은 승인 Spec, 기준·교체 실행, implementer/reviewer 두 역할, 공통 봉투·증거·필수 검사, close, 역할 교체 비교였다(`docs/planning/implementation-plan.md:281-320`, `docs/planning/implementation-plan.md:476-511`). DB·큐·다수 전문 역할·자기학습은 명시적으로 뒤로 미뤘다(`docs/requirements/v1-scope.md:96-111`, `docs/requirements/capability-map.md:109-118`). 아래에서 **계획**은 §10에 직접 있던 일, **선행**은 그 경로를 실제로 연결하기 위한 최소 누락, **추가**는 원 계획 밖 확장이다.

| 행 | 관계 | 무엇이 정당화했나 / 제품 능력을 바꿨나 | 그때 가능한 더 작은 선택 |
| --- | --- | --- | --- |
| 17 | 추가 | F-03 뒤 D-72가 K-60의 금지 대상을 “부품 자동 발견”에서 “라우터 대체”로 재정의했다. discovery 정책은 바뀌었지만 라이선스 기능은 안 바뀌었다. | M2에서는 현재 두 절차만 allowlist하고, 코어 원칙 재정의는 별도 결정으로 뺄 수 있었다. **첫 원 계획 밖 유입점**이다. |
| 18 | 추가 | F-08 원자적 compile은 실제 부분쓰기 위험을 줄였다. F-07 upstream 대조는 출처 검증을 강화했다. | 원자성은 남기되 네트워크 upstream 대조는 vendor 갱신/release gate로 미룰 수 있었다. 또한 reviewer가 직접 구현·커밋한 것은 역할 경계를 어겼다(`docs/planning/progress.md:71`). |
| 19 | 계획 #8 | 두 reviewer의 쓰기 거부를 관찰했다. 안전 능력을 실제로 바꿨다. | 없음. 다만 7개 프로브 뒤 추가 봉인보다 “두 런타임에서 파일 0개”를 완료 신호로 고정할 수 있었다. |
| 20 | 계획 #9 | 부품 부착→라우터 연결을 증명했다. M2 wiring에 필요했다. | 없음. |
| 21 | 선행 #10 | 승인과 Orca 위임 식별자를 evidence에 연결했다. 실제 관통에 필요했다. | 승인 1건·run 1건만 지원하는 최소 경로로 제한 가능했다. |
| 22 | 선행 #10 | 손작성 계약을 없애는 `envelope build`를 만들었다. 재현 가능한 관통에 필요했다. | 없음. 이는 수동 RUNBOOK을 줄이는 방향의 필요한 자동화였다. |
| 23 | 선행 #10 | reviewer 결과를 close가 소비하게 연결했다. 실제 흐름에 필요했다. | PASS/FAIL 문자열이 아니라 review 존재와 findings 해소를 연결했으면 뒤의 판정 룰렛을 피할 수 있었다. |
| 24 | 계획 #11 | parity 케이스를 실측에 결박했다. 합성 fixture만으로 PASS하는 오류를 줄였다. | artifact·check·schema까지만 앵커하고 자유 형식 verdict는 제외할 수 있었다. |
| 25 | 계획 #8 | 역할 투영과 권한 상한을 런타임별로 명시했다. 안전 능력을 바꿨다. | 미관측 칸을 사실대로 남기고, 모든 lifecycle까지 동시에 해결하는 것은 미룰 수 있었다. |
| 26 | 계획 #10 | 첫 기준 관통. 제품 경로와 운영 결함을 실제로 드러낸 필요한 시도였다. | 이 시점부터 변경 동결 후 acceptance blocker만 고쳤어야 했다. |
| 27 | 계획 #11 | 첫 교체 관통. 서로 다른 산출물이라 reviewer 비교가 무의미함을 발견했다. | 이 한 번의 실패로 동등성 정의를 product/check 중심으로 수정할 수 있었다. |
| 28 | 추가 | 두 번째 독립 리뷰가 실제 결함을 더 찾았다. harness 코드는 바뀌었지만 payload 완료는 늦어졌다. | findings를 “현재 T1 close blocker / 후속 hardening”으로 나눠 전자만 반영할 수 있었다. |
| 29 | 추가 | 실제 관통에서 드러난 RUNBOOK·코어 연결 오류를 수정했다. 일부는 필요했다. | 현재 happy path를 막는 오류만 고치고 일반 복구·옛 형식 호환은 backlog로 보낼 수 있었다. |
| 30 | 추가 | D-73이 서로 다른 제품을 본 reviewer 면을 비교에서 제외했다. 잘못된 비교는 막았지만 게이트 의미를 줄였다. | “reviewer verdict parity는 M2에서 검증 불가”라고 결정하고 여기서 중단할 수 있었다. |
| 31 | 계획 #10의 반복 | 같은 라이선스 작업을 다시 통과시키려 했으나 harness가 계속 바뀌어 evidence가 낡았다. | spine을 먼저 동결하고 canonical worktree 하나만 유지할 수 있었다. |
| 32 | 추가 | 두 런타임 지침 인덱스 대칭을 보강했다. attach 신뢰도는 높였지만 현재 payload는 안 바뀌었다. | `compile --check`의 후속 개선으로 미룰 수 있었다. |
| 33 | 추가 실험 | 같은 산출물 reviewer-only 재실행이 런타임 간 판정 차이를 보였다. 목표 검증을 위해 **한 번은 필요했다**. | 차이를 관측한 즉시 목표 오류로 판정하고 추가 표본 전에 멈출 수 있었다. |
| 34 | 추가 | `allowed_paths`를 좁혀 권한 계약을 정확히 했다. 안전 능력은 바뀌었다. | 현재 unit 경로만 검사하는 최소 변경으로 끝낼 수 있었다. |
| 35 | 추가 실험 | 같은 Codex 재실행이 PASS→FAIL로 바뀌어 런타임 내부 불안정을 확인했다. | 이 반복으로 충분했다. 이후 같은 artifact 재실행은 연구 표본이지 M2 필수 작업이 아니다. |
| 36 | 추가 | D-74가 런타임당 표본 2개와 unstable 제외를 도입했다. 비용은 늘었지만 “같은 판정” 증명은 못 했다. | Q-10 실험으로 이관하고 deterministic parity만 M2 gate로 남길 수 있었다. |
| 37 | 추가 | 재승인 경로를 보강했다. 일반 운영에는 유용하지만 깨끗한 새 승인 1건의 M2에는 필수 아니었다. | 현재 unit은 재승인 없이 닫고 후속 운영 항목으로 미룰 수 있었다. |
| 38 | 추가 | 승인 commit/base SHA 동일성을 강화했다. 실수·표류 방지는 개선했다. | 최신 승인 1건만 허용하는 v1 제한으로 같은 효과를 더 작게 얻을 수 있었다. |
| 39 | 추가 | ResultEnvelope의 보조 설명 처리 등을 보강했다. schema 품질은 바뀌었지만 핵심 제품 기능은 안 바뀌었다. | 봉투 필수 필드만 M2에 남기고 표현 보강은 후속으로 미룰 수 있었다. |
| 40 | 추가 | 문서에 적힌 CLI flag가 실제 런타임에서 안 먹는 결함을 고쳤다. happy path를 막으므로 필요했다. | 문서 예제 전체가 아니라 실제 launch 명령 2개만 smoke test할 수 있었다. |
| 41 | 추가 | close가 현재 제품·현재 승인만 세게 했고 D-75를 열었다. 낡은 PASS 재사용을 막은 것은 필요했다. | 현재 artifact 1건만 허용하고 “PASS 표본 수” 정책은 별도 결정으로 분리할 수 있었다. |
| 42 | 추가 | reviewer prompt의 명령 실행/읽기 모순을 고쳤다. 실제 reviewer launch에 필요했다. | 현재 고정 prompt 한 개만 교정한 뒤 일반 prompt compiler는 미룰 수 있었다. |
| 43 | 추가 | 4개 에이전트·75만 토큰의 공격적 설계 리뷰가 12개 결함을 찾아 harness를 강화했다. payload 능력은 안 바뀌었다. | 한 사람 로컬 v1의 위협 모델을 먼저 정하고, acceptance blocker만 반영할 수 있었다. |
| 44 | 추가 | 원시 로그에 head/tree와 hash를 봉인했다. 부주의한 YAML 수정은 잡지만 로컬 행위자의 일관된 위조는 못 막는다. | required checks 재실행을 종점으로 두고 추가 봉인은 경고 수준으로 미룰 수 있었다. |
| 45 | 추가 | 31개 에이전트·275만 토큰이 28건을 재현해 많은 정확성·봉인 코드를 추가했다. 실제 결함은 맞았지만 v1 위협 경계 밖 항목이 섞였다. | “현재 T1을 거짓 PASS시키는 최소 반례”만 차단하고 외부 서명·옛 승인·일관된 로컬 위조는 Q-11 이후로 미룰 수 있었다. |
| 46 | 계획 #10·#11의 세 번째 반복 | `impl5`에 현재 6개 check PASS·review PASS 산출물을 만들었다. 제품 결과를 실제로 바꾼 반복이다. 그러나 main에는 아직 통합되지 않았고 `impl6`는 준비만 됐다. | `impl5`를 canonical로 고정해 close하고, 기존 swap 관측은 adapter smoke로 재사용하면 된다. 현재 문구 그대로의 full swap을 생략하려면 요구사항 수정 승인이 필요하다. |

**판정:** 17행이 최초의 원 계획 밖 유입이다. 다만 17~27의 보완 대부분은 M2를 실제로 실행하기 위한 정책 정리·배선·첫 관통이었다. 범위가 통제되지 않기 시작한 지점은 28행이고, 근본 목표 오류가 관측됐는데도 해결책을 표본과 봉인으로 바꾼 36행부터 비용이 구조적으로 반복됐다(`docs/planning/progress.md:70-99`).

### US-4 「PM 으로서 AI 가 승인 없이 위험한 일을 못 하게 하고 싶다」 (권한 상한)

- **이 이야기에서 하네스가 하는 일:** implementer는 지정 작업 공간에만 쓰고 reviewer는 읽기만 하며, 비용·삭제·외부 push 같은 되돌리기 어려운 행동은 사람 승인 전에는 실행하지 못하게 역할과 런타임 실행형을 묶는다(`.harness/bindings.yaml:15-100`).
- **지금 상태:** 두 reviewer의 읽기 전용은 단독 프로브와 실제 launch 경로에서 관측됐다. 반면 기본 implementer 강제는 미관측, 교체 implementer는 부분 관측이다(`adapters/orca/RUNBOOK.md:692-720`). 현재 `bin/romeo doctor`도 repo/machine 검사는 PASS지만 런타임 load는 Claude “대조 불가”, Codex `10/12`, implement/review discovery는 미관측으로 보고했다.
- **막히는 곳과 근본 원인:** 교체 implementer의 workspace sandbox는 작업 공간 밖 Orca IPC까지 막는다. 그래서 `worker_done`·heartbeat·`ask`를 보낼 수 없고, operator가 `worker-abandon` 뒤 task를 수동 완료해야 한다(`adapters/orca/RUNBOOK.md:707-720`). **근본 원인은 권한 경계와 제어 채널이 분리되지 않은 설계**다. worker가 써야 하는 유일한 외부 통신도 일반 외부 접근과 같은 IPC에 놓여 있다.
- **불필요했던 단계:** 이 충돌을 해결하기 전에 lifecycle까지 완전 자동이라는 증거를 만들려 한 반복. 파일 쓰기 상한과 작업 결과 회수는 중요하지만, v1 한 사람 로컬 사용에서 heartbeat 자동화가 제품 합격 조건일 필요는 없다.
- **권고:** v1에서는 sandbox를 유지하고 coordinator가 결과 파일을 읽어 task 상태를 정리하는 **명시적 degraded lifecycle**을 허용한다. 장기적으로는 host가 중계하는 좁은 `done/ask` 채널을 만들어 파일 권한과 IPC 권한을 분리한다.

### US-5 「PM 으로서 하네스를 다른 프로젝트에 붙이고 싶다」 (부착·컴파일)

- **이 이야기에서 하네스가 하는 일:** 코어 원본을 각 런타임의 지침·스킬 경로에 원자적으로 투영하고, managed marker 밖 사용자 내용을 보존하며, 부품을 빼도 코어가 작동하게 한다. 이는 V-5·V-8·V-11에 해당한다(`docs/requirements/v1-scope.md:39-45`).
- **지금 상태:** 이번 리뷰에서 `bin/romeo compile --check`, `bin/romeo validate`, `bin/romeo doctor`의 repo/machine 검사는 exit 0이었다. 부착 라우팅도 현재 프로젝트에서 active로 계산된다. 다만 실제 두 런타임 discovery의 모든 칸이 관측된 것은 아니고, 새 외부 프로젝트 attach/update·복구 전체는 M2가 아니라 후속 범위다.
- **막히는 곳과 근본 원인:** 컴파일 기능이 M2를 막는 핵심은 아니다. F-01·02·06·08 같은 실제 안전 결함을 고치는 동안 attach의 일반 안전성까지 M2 critical path에 섞인 것이 문제다. `v1-scope.md`는 최소 adapter를 요구하지만 범용 updater·모든 옛 상태 복구를 M2 합격 조건으로 쓰지 않는다.
- **불필요했던 단계:** 매 관통마다 instruction index와 upstream·옛 compiled state의 일반 반례까지 다시 여는 것. 현재 managed output의 `compile --check`와 한 번의 fresh fixture면 M2 wiring 증거로 충분하다.
- **권고:** M2에는 현재 저장소의 compile check와 두 runtime discovery smoke만 남긴다. full attach/update·dirty 프로젝트 복구는 기존 후속 마일스톤에서 검증하고, M2 완료와 v1 release 완료를 같은 말로 쓰지 않는다.

### US-6 「PM 으로서 작은 기능 하나를 에이전트에게 맡기고 결과만 확인하고 싶다」 (RUNBOOK·위임)

- **이 이야기에서 하네스가 하는 일:** 승인된 Spec을 TaskEnvelope로 만들고, Orca가 워크트리·task·dispatch를 소유하며, implementer 결과와 reviewer 결과를 수집해 close로 넘긴다. RUNBOOK은 이 계약을 실제 런타임 명령으로 옮기는 adapter다.
- **지금 상태:** RUNBOOK은 1,164줄이고 기준 실행 §3.1~3.9에 11개, 교체 실행에 10개, 결과 수집·등록·판정에 3개 행동 묶음이 필요하다. 브리프가 요구한 추가 reviewer 8회를 §6.6의 1~6 절차로 세면 48개가 더해져 **최소 72개 수동 행동 묶음**이다. 각 묶음 안에 여러 셸 명령이 있으므로 실제 클릭·명령 수는 더 많다(`adapters/orca/RUNBOOK.md:60-95`, `adapters/orca/RUNBOOK.md:830-866`, `adapters/orca/RUNBOOK.md:976-1006`).
- **막히는 곳과 근본 원인:** 일부는 미완성 자동화다. Envelope 생성기는 생겼지만 task 생성·launch prompt 채움·terminal 채택·로그 회수·review record·evidence 복사·parity case 등록이 하나의 실행 명령으로 연결되지 않았다. 일부는 설계다. 실행 상태의 주인을 Orca 하나로 정했지만 sandbox worker가 Orca IPC를 쓸 수 없게 해 adapter가 사람의 상태 보정에 의존한다.
- **불필요했던 단계:** 한 런타임당 reviewer 두 표본을 만들기 위해 매번 run/task/evidence/prompt/terminal/record/collect를 반복하는 절차. 비결정적 판정이 목표인 한 자동화해도 계산 비용과 불확실성만 더 빨리 반복한다.
- **권고:** 먼저 reviewer 표본 루프를 M2에서 제거한다. 남은 happy path는 후속으로 `romeo run-unit` 같은 coordinator 명령 하나가 TaskEnvelope 생성→Orca launch→결과 수집을 수행하게 자동화하되, 이번 M2를 그 새 자동화 구현에 다시 종속시키지는 않는다.

## 근본 원인 종합 (상위 3개 — 각각 근거·언제부터·무엇을 낳았는지)

### 1. 비결정적 리뷰 의견을 결정적 합격 조건으로 만든 목표 설정 오류

- **근거:** 정본은 역할 교체 뒤 “동일 artifact 스키마·게이트 판정”을 요구한다(`docs/requirements/v1-scope.md:64-67`). 구현은 이를 reviewer의 자유 형식 `gate_verdict` 일치까지 확장했다. D-74 실측은 같은 런타임 내부에서도 verdict가 바뀜을 보였다(`docs/decisions/decision-register.md:132-135`, `.harness/observations.yaml:169-241`).
- **언제부터:** 문구의 위험은 처음부터 있었지만, 33·35행 실측으로 검증 불가능성이 확인됐다. 36행에서 목표를 고치지 않고 표본 2개·unstable 제외를 택하면서 반복 구조가 확정됐다.
- **낳은 것:** reviewer-only 재실행, 런타임별 추가 표본, `PRODUCT_DIFFERS/UNSAMPLED/UNSTABLE` 상태, D-75, impl6, “PASS인데 reviewer 면은 제외”라는 해석 비용. 같은 FAIL 네 건도 PASS가 되므로 품질 게이트로서 의미가 없다.

### 2. acceptance blocker·위협 범위·중단 조건을 나누지 않은 계획·프로세스 오류

- **근거:** 원 계획은 한 T1 수직 슬라이스와 역할 교체 1회였다(`docs/planning/implementation-plan.md:281-320`). 그러나 진행표 28행 이후 모든 발견을 M2 안에서 해결했고, 43행은 4 agent/75만 token, 45행은 31 agent/275만 token을 투입했다(`docs/planning/progress.md:81-99`). 계획은 모델 비용이 cross-review 2배, parity 4배라고 이미 적었지만 release tag 외 반복의 최대 횟수·시간 예산·stop rule은 없었다(`docs/planning/implementation-plan.md:563-599`).
- **언제부터:** 17행부터 범위 밖 보완이 들어왔고, 28행부터 리뷰 finding 전량 반영이 관통보다 우선했다. 36행 이후에는 불안정 자체가 다음 표본을 요구했다.
- **낳은 것:** M2 구간 45개 커밋, 207개 파일, 약 27,151 insertions/864 deletions, `romeo/` 약 5,835줄·tests 약 5,368줄·RUNBOOK 1,164줄. 반면 실제 22파일 payload는 `impl5`에 남고 현재 branch에는 통합되지 않았다.
- **위협 모델 판정:** 정본 요구사항에는 공격자나 악의적 로컬 사용자가 정의돼 있지 않다. 위협 모델은 43~45행 이후 `progress.md`에야 생겼고, 로컬 파일은 로컬 행위자에게서 지킬 수 없다고 명시한다(`docs/planning/progress.md:206-244`). 한 사람 로컬 v1에서 필요한 것은 부주의·표류·손으로 쓴 허위 완료의 탐지까지다. 외부 서명 없이 일관된 로컬 위조를 막는 노력은 필요 수준을 넘는다.

### 3. 실행 계약이 자동화되지 않은 채 상태를 여러 소유 위치에 흩어 놓은 통합 설계·구현 문제

- **근거:** 실행 상태는 Orca, 승인/문서 상태는 Romeo, 원시 로그는 각 worktree의 gitignored `.harness`, 관측은 현재 branch의 fixtures/observations가 소유한다. parity는 네 봉투를 한 checkout으로 수동 수집해야 한다(`adapters/orca/RUNBOOK.md:830-856`). 현재 `close --dry-run`은 다른 worktree evidence의 로그와 현재 트리를 함께 확인할 수 없어 실패한다.
- **언제부터:** 첫 관통 26행에서 수동 연결의 누락이 드러났고, 29·31·40·42·46행에서 launch·명령형·수집·lifecycle 보정이 반복됐다.
- **낳은 것:** 6개 worktree, 서로 다른 HEAD와 dirty tree, main에서 재현되지 않는 PASS, 진행표/바인딩/RUNBOOK의 관측 상태 차이, 397로 적힌 테스트 수와 현재 398의 drift. 샌드박스가 Orca IPC를 막아 안전과 lifecycle을 동시에 자동화하지 못한다.

### 의뢰자의 “처음부터 설계나 계획이 전부 잘못됐다”는 전제에 대한 판정

그 전제는 **부분적으로 틀리다**. 얇은 정책 spine, 한 개 실제 T1 수직 슬라이스, 두 역할, 공통 계약, 현재 산출물에 묶인 evidence, reviewer read-only는 문제를 줄이는 올바른 뼈대였고 현재 테스트·실측도 그 일부를 뒷받침한다(`docs/planning/implementation-plan.md:23-31`, `docs/requirements/capability-map.md:109-142`). 잘못된 것은 (1) “같은 계약과 결정적 검사”에 “같은 LLM 리뷰 verdict”를 섞은 완료 정의, (2) 첫 실패 후 목표를 재검토하는 stop rule이 없었던 계획, (3) 수동 adapter를 임시 상태로 두지 않고 증거 하드닝을 그 위에 계속 얹은 실행 방식이다.

## 이전 Codex 리뷰 재리뷰 (F-01~F-10 · 계획 리뷰)

### 2026-08-28 M2 리뷰 F-01~F-10

| finding | 재판정 | 범위를 키웠는가 | 이 리뷰가 놓친 것 |
| --- | --- | --- | --- |
| F-01 저장소 밖 compile 경로 | **옳음.** 실제 파일 손상 가능성이 있는 Important였다. | 제한적. root 경계 검사와 회귀 테스트면 끝낼 수 있었다. | compile 안전만 보았고 M2의 검증 목표·비용은 보지 않았다. |
| F-02 취소된 skill 잔류 | **대체로 옳음.** stale discovery는 K-60/K-69를 깨뜨린다. | 일부. 모든 옛 상태 복구보다 현재 accepted→deferred 경로 하나로 제한 가능했다. | M2 happy path와 일반 updater 안전을 우선순위로 나누지 않았다. |
| F-03 직접 노출과 K-60 충돌 | **문구·native discovery 충돌 지적은 옳음.** 해결은 D-72의 정책 재정의였다. | **행 17을 직접 낳았지만 뒤 30행 전체의 원인은 아니다.** | 코어 의미를 바꾸기 전에 현재 M2에 필요한 allowlist만 둘 선택을 제시하지 않았다. |
| F-04 override·read-only 미강제 | **옳음.** 실제 권한 상한 관측은 v1 핵심이다. | 행 19·25와 일부 방어 검사를 정당화했다. 다만 로그 봉인·승인 사슬 전부를 요구한 것은 아니다. | sandbox와 Orca IPC가 충돌할 구조, lifecycle을 비게이트로 둘 선택을 놓쳤다. |
| F-05 잘못된 CLI 명령형 | **옳음.** 문서대로 실행하면 argparse에서 멈추는 실제 vertical-flow blocker였다. | 작게 고칠 수 있는 범위였다. | 생성된 명령 smoke test를 전체 RUNBOOK 자동화와 연결하지 못했다. |
| F-06 managed marker parser | **옳음.** 중복·CRLF·코드펜스 손상 반례가 있었다. | compile의 일반 견고성으로 범위가 늘었지만 안전상 합리적이었다. | M2 blocker와 attach 후속 개선을 분리하지 않았다. |
| F-07 upstream 자기일관성 | **부분적으로 옳음.** “원문 수정 0” 주장에 고정 SHA 대조가 필요한 것은 맞다. | **상대적으로 크게 키웠다.** 매 실행의 live upstream 대조까지 M2에 넣을 필요는 없었다. | 한 사람 로컬 v1에서 gate/update 시 1회 검증이면 충분하다는 비용 경계를 놓쳤다. |
| F-08 비원자 compile | **옳음.** 부분 실패가 기존 파일을 반쯤 바꾸는 반례가 있었다. | 필요한 안전 수정이었다. | 독립 reviewer가 직접 F-07/F-08을 구현·커밋해 review-only 역할 계약을 넘었다(`docs/planning/progress.md:71`). |
| F-09 CI 경로 | **옳음.** 검사가 실제 변경 경로에서 실행되지 않으면 PASS의 의미가 없다. | 작은 CI 수정 범위였다. | 최신 CI와 로컬 수직 close를 별개 증거로 다루는 기준이 없었다. |
| F-10 progress 상태 drift | **옳음.** 완료 선언과 실측 불일치는 PM 판단을 흐린다. | 작은 문서 정정 범위였다. | 상태 문서가 커질수록 새 drift를 만드는 구조와 단일 현재 상태 요약의 필요를 놓쳤다. |

**종합:** F-01~F-10은 대부분 실제 결함이었다. F-03·F-04가 이후 30행을 혼자 낳았다는 인과는 성립하지 않는다. 직접 연관된 것은 K-60 재정의·read-only probe·권한 투영이고, 큰 팽창은 그 뒤 실제 관통에서 발견된 연결 결함, D-73/D-74의 판정 문제, 그리고 “발견한 모든 반례를 M2에서 닫는다”는 stop rule 부재에서 생겼다. 또한 리뷰자가 F-07/F-08을 직접 구현한 것은 findings만 내야 하는 독립 검토의 신뢰 경계를 훼손했다.

### 2026-08-27 계획 리뷰

| 항목 | 재판정 |
| --- | --- |
| 얇은 spine·수직 슬라이스·두 역할을 유지 | **옳음.** 전면 재작성보다 실제 한 건을 잇는 방향이 맞았다(`docs/reviews/2026-08-27-codex-plan-review/review.md:154-186`). |
| M2 core parity와 v1 release gate 분리 | **옳음.** V-0~V-11 전체와 M2 한 단계는 같은 완료가 아니다. 이 구분은 지금도 필요하다. |
| reviewer read-only와 dirty-tree freshness를 M2 선행으로 올림 | **옳음.** 현재 관측된 안전·evidence 기반의 핵심이 됐다. |
| “같은 schema·AC·gate·evidence” parity는 변경 불필요 | **절반만 옳음.** schema·AC·권한·결정적 검사는 유지해야 하지만, `gate`를 자유 형식 reviewer verdict까지 포함하는지 정의하지 않았다(`docs/reviews/2026-08-27-codex-plan-review/review.md:205-210`). |
| 놓친 근본 문제 | LLM 판정의 검증 가능성, 같은 실패도 parity PASS가 되는 문제, 최대 반복/비용/stop rule, 한 사람 로컬 위협 모델, 수동 RUNBOOK의 조작 수를 검토하지 않았다. |

## 불필요했던 단계 목록 (단계 · 비용 · 결과를 바꿨는가 · 근거)

“불필요”는 결함이 거짓이었다는 뜻이 아니라, **M2의 사용자 능력을 닫기 전에 반드시 할 필요가 없었다**는 뜻이다.

| 단계 | 비용 | 제품이 할 수 있는 일을 바꿨는가 | 판정·근거 |
| --- | --- | --- | --- |
| 첫 기준 관통(26) | worktree 1·implement/review 1회 | 예. 실제 end-to-end 구멍을 발견 | 필요했다. 수직 슬라이스의 본래 목적이다. |
| 첫 교체 관통(27) | worktree 1·implement/review 1회 | 예. 다른 산출물끼리 reviewer를 비교할 수 없음을 발견 | 필요했다. 여기서 parity 정의를 줄였어야 했다. |
| 두 번째 관통 묶음(31) | 추가 worktree·payload 반복 | 제한적. harness 결함은 드러났으나 완료 산출물은 남지 않음 | 변경 동결 없이 재시도해 evidence가 다시 낡았다(`docs/planning/progress.md:84`). |
| reviewer-only 실험(33) | 같은 artifact 검토 2면 | 예. 런타임 간 verdict 차이를 발견 | 한 번은 필요했다. |
| 동일 Codex 반복(35) | 같은 artifact 추가 검토 | 예. 런타임 내부 불안정을 확인 | 여기까지가 목표 반증에 충분했다. 이후 표본 증설은 M2 필수 아님. |
| D-74 표본 2회/면과 향후 8 reviewer | 실행당 §6.6 수동 6단계, 모델 비용 최소 8회 | 아니오. 불안정이면 면을 제외할 뿐 품질 참값을 만들지 않음 | 삭제 대상. Q-10 실험으로 이동. |
| 3차 기준 관통(46) | impl5·implement/review·6 checks | 예. 현재 정상 payload와 close 가능한 상태를 만들었다 | 필요한 최종 후보. 이것을 canonical로 닫아야 한다. |
| impl6 full swap 준비와 향후 재구현 | 새 run/worktree/task 2개, 아직 미기동 | 아직 아니오 | 현재 문구를 수정한다면 중단 가능. 문구를 유지하면 해야 하므로 PM 결정 사항이다. |
| 2차 이후 독립 리뷰 전량 반영 | 여러 review/fix round | harness 신뢰도는 개선, 라이선스 사용자 기능은 거의 불변 | blocker만 반영하고 나머지는 후속 hardening으로 보냈어야 했다. |
| 4 agent·75만 token 반박 설계 리뷰(43) | 21분·75만 token | harness 위조 저항은 개선, payload 불변 | 위협 모델보다 먼저 실행됐다. 로컬 v1 범위에서는 과했다. |
| 로그 봉인(44) | code/test/runbook 증가 | 부주의한 기록 수정 탐지 개선 | 유지할 수 있지만 M2 completion blocker로 둘 필요는 없었다. 재실행이 종점이다. |
| 31 agent·275만 token·28 finding 반박(45) | 21분·275만 token | harness 정확성 다수 개선, payload 불변 | findings는 실재했다. 그러나 일관된 로컬 위조·외부 승인까지 M2에서 닫으려 한 범위가 과했다. |
| 11개의 `progress:` 커밋(8/29) | 리뷰·커밋·상태 갱신 attention | 실행 능력은 직접 바꾸지 않음 | 긴 상태표가 새 drift를 만들었다. 한 개의 “현재 상태/다음 1단계” 갱신으로 줄일 수 있었다. |
| 1,164줄 RUNBOOK 수동 재수행 | 기준+swap+표본 기준 최소 72 행동 묶음 | 자동화가 아니므로 반복할수록 제품보다 운영 비용 증가 | 현재 M2에서는 happy path 1회만 수행하고, 자동화는 별도 작업 단위로 둔다. |

## 실행한 읽기 전용 명령과 출력 요지

| 명령 | 종료 | 이번 리뷰에서 관측한 요지 |
| --- | --- | --- |
| `python3 -m unittest discover -s tests` | 0 | `Ran 398 tests in 77.669s`, `OK`. |
| `bin/romeo --help` | 0 | `route`, `card`, `new`, `validate`, `fixtures`, `approve`, `evidence`, `envelope`, `review`, `close`, `id`, `compile`, `doctor`, `vendor`, `notices`가 노출됨. |
| `bin/romeo close --unit feat-20260829-license-field-46an --root "$PWD" --dry-run` | 1 | evidence HEAD/tree가 현재 루트와 다름, check-5 기록 실패, required check 재실행 불일치, AC 4개 미체크, 현재 루트에 원시/review 로그 없음. 현재 루트 완료를 올바르게 거부함. |
| `git log --format='%h %ad %s' --date=short` | 0 | 총 70개. 날짜별 8/05 1, 8/12 1, 8/13 4, 8/24 1, 8/27 18, 8/28 17, 8/29 28. 8/29에는 `progress:` 11개, `ci:` 2개, 그 밖 15개. |
| `git log --stat --format='%h %s' -- romeo/ \| head -200` | 0 | M2 plumbing·anchor·parity·close hardening이 반복해서 `romeo/`를 키웠다. 대표적으로 M2 plumbing 약 +1,512/-76, atomic compile 약 +598/-91, 6개 hardening 묶음 약 +790/-80이었다. |
| `bin/romeo fixtures parity --report` | 0 | 11 cases, observed 2, synthetic 9, core parity PASS. reviewer-only observed case는 네 verdict가 모두 FAIL이고 unittest 기록도 실패한 artifact라서 “동일성 PASS ≠ 제품 품질 PASS”임을 확인. |
| `grep -rn "threat\|위협\|공격자\|위조" docs/ core/ \| head` 및 범위 제한 `rg` | 0 | 요구사항·코어 정본에는 사전 위협 모델이 없고, 43~45행 뒤 `progress.md:206-244`에 로컬 위조의 한계를 설명한 절이 생김. |
| `bin/romeo route --fixtures fixtures/requests --report` | 0 | 33/33, gate 누락 의심 0. `PART_PENDING_GATE` 20건은 부품 상태 경고. |
| `bin/romeo compile --check`; `bin/romeo validate`; `bin/romeo doctor` | 모두 0 | compile 정합·repo/machine 검사는 PASS. validate는 AC 미체크/stale를 경고했고 doctor는 runtime load 일부를 미관측으로 보고. |
| `gh run list --limit 1 --json ...` | 1 | `api.github.com` 연결 실패. 최신 CI는 확인하지 못함. |

## 확인했으나 문제 없음

- `python3 -m unittest discover -s tests`: exit 0, `Ran 398 tests`, `OK`. 기존 진행표의 397보다 1개 늘어 현재 문서 숫자는 낡았지만 테스트 자체는 통과했다.
- `bin/romeo --help`: exit 0. 계획·검증·승인·evidence·envelope·review·close·compile·doctor·vendor 명령이 현재 CLI에 연결돼 있다.
- `bin/romeo route --fixtures fixtures/requests --report`: exit 0, `33/33`, gate 누락 의심 0. `PART_PENDING_GATE` 20건은 의도된 부품 상태 경고다.
- `bin/romeo compile --check`: exit 0. 현재 managed 산출물은 정본과 맞는다.
- `bin/romeo validate`: exit 0. 다만 라이선스 Spec의 AC 네 개 미체크와 stale base SHA를 경고하므로 “작업 완료”를 뜻하지 않는다.
- `bin/romeo doctor`: repo/machine 검사는 exit 0. 런타임 discovery 일부 미관측은 아래에 별도로 남긴다.
- `bin/romeo fixtures parity --report`: 검사기 자체와 11개 fixture는 exit 0. 단, 관측 PASS의 의미가 품질 PASS가 아니라는 문제는 US-3에 적었다.
- reviewer read-only는 두 런타임에서 쓰기 0건으로 관측됐고, 실제 launch 경로에서도 before/after tree가 같았다(`docs/planning/progress.md:72`, `adapters/orca/RUNBOOK.md:692-705`).
- 이번 리뷰 동안 기존 파일, `impl*` worktree, 커밋, 외부 저장소는 변경하지 않았다. 작성 대상은 이 디렉터리의 새 보고서 두 개뿐이다.

## 확인하지 못한 것

- 최신 원격 CI 1건: `gh run list --limit 1 ...`은 `api.github.com` 연결 실패로 조회하지 못했다. `progress.md`에 적힌 과거 성공 run은 현재 CI 증거로 승격하지 않았다.
- `impl5`의 “6 checks PASS·review PASS·close WARN만 남음”은 파일과 진행 기록을 읽었지만, 이 리뷰 계약상 `impl*`를 읽기만 해야 하므로 그 worktree에서 명령을 재실행하지 않았다. 따라서 이 보고서에서는 **기록상 후보**, 현재 재검증은 미완료다.
- `impl6` 교체 실행은 준비만 됐고 기동되지 않았다. 현재 base의 full swap 성공은 미검증이다.
- 기본 implementer의 권한 강제, 교체 implementer의 외부 파일 쓰기 차단·승인 명령 차단은 bindings에도 미관측/부분 관측으로 남아 있다.
- `doctor`가 보고한 Claude runtime load 전체와 Codex implement/review discovery 전체는 현재 세션에서 확인되지 않았다.
- reviewer verdict 변동의 비율·원인은 모른다. Q-10이 열려 있으며, 관측만으로 prompt 모호성·모델 변동·launch 경로 중 하나를 원인으로 단정할 수 없다.
- 현재 branch에는 18개 license backfill·검증기·인덱스 변경이 통합되지 않았다. 따라서 main 기준 사용자 기능은 아직 완료가 아니다.

REVIEW_DONE
