---
id: feat-20260902-scope-grammar-procedure-drift-z5mv
type: brief
title: 승인 산문이 쓰기 권한이 되지 않게 하고, 절차와 도구의 어긋남을 닫는다 — 시나리오 8 관통이 낸 결함 Q-36~Q-42
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: draft
approved_at: null
approved_by: null
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-02'
updated: '2026-09-02'
---

# 승인 산문이 쓰기 권한이 되지 않게 하고, 절차와 도구의 어긋남을 닫는다 — 시나리오 8 관통이 낸 결함 Q-36~Q-42

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

직전 관통(시나리오 8)이 낸 하네스 결함 7건을 닫는다 — 승인 문장의 설명이 쓰기 권한이 되던 구멍(Q-36), 불일치를 잡지 못하던 CI 의 fixture 스텝(Q-37), 그리고 위임 절차 원본(RUNBOOK)과 도구(`run-unit`)가 어긋나던 다섯 자리(Q-38~Q-42).

## 배경과 대상

- **왜 지금:** 코어 규칙 §10 이 관통 **중에는** 하네스를 못 고치게 한다. 지금은 정비 구간이고 M3 는 앞으로 관통을 더 돈다(시나리오 9 · 실제 T2 관통). 7건 중 Q-36 은 **권한 상한 계열**이다 — 「변경 범위」의 `·` 로 자른 조각마다 첫 백틱을 경로로 읽어 함수명 `cmd_card` 가 쓰기 상한에 실렸다. 이번엔 넓어진 쪽이 함수명이라 판정에 영향이 없었지만, 승인하지 않은 경로가 상한에 조용히 들어가는 구멍이 열려 있다. Q-37 은 fixture 30/33 이 맞아도 exit 0 이라 CI 초록불이 fixture 일치를 뜻하지 않는다. Q-39·Q-40 은 직전 관통에서 `started` 유령 회차 2건과 확인 4 의 반복 실패를 실제로 만들었다.
- **누구를 위한 것:** 이 하네스로 관통을 돌리는 사람(코디네이터)과 위임을 받아 구현·검토하는 워커. 그리고 spec 을 쓰는 사람 — 설명을 어떻게 써야 상한이 안전한지 지금은 코드를 읽어야만 안다.
- **성공하면 무엇이 달라지나:** 승인 문장의 설명을 아무렇게 써도 쓰기 상한은 승인한 경로만 담는다. fixture 가 하나라도 틀리면 로컬 명령도 CI 도 빨간불이다. `run-unit` 이 인쇄한 명령을 그대로 실행해도 RUNBOOK 과 어긋나지 않고, 첫 관통의 확인 4 가 통과하며, 재승인이 관통을 처음부터 다시 돌리게 하지 않는다.

## 방향

- **하려는 것:** ① `change_scope_paths` 가 괄호 안과 경로 모양이 아닌 토큰을 상한에서 빼고, 그 문법을 Tech Spec 템플릿에 적는다 ② `route --fixtures --report` 가 불일치 1건이면 exit 1 ③ `run-unit check` 로 §3.1 확인 4 를 판정·재검토 대조로 좁힌다 ④ `run-unit` 의 위임 명령을 정본 절차 파일에서 채우고 `--spec` 에 해시를 넣지 않는다 ⑤ §3.4.1 의 Run 재생성을 해시가 든 경우로 한정한다 ⑥ 회차 기록의 `base_sha` 가 재승인을 따라간다 ⑦ Q-38 을 D-80(재승인은 정상 경로)으로 닫고 Q-36~Q-42 를 해소한다.
- **하지 않는 것:** `romeo/evidence.py` 의 `_stamp_ids`·`_change_base`(한 run 은 한 위임이라는 방어) · `romeo/close.py` 의 판정 로직 · 코어 규칙 · 두 절차 파일 정본의 문안 · Orca CLI 자체 · 다른 park(Q-12·13·15·16·17·19·23·24·26·32·33·34·35) · `run-unit --spawn` 의 실제 실행 경로 · 시나리오 9 와 실제 T2 관통.
- **전달 메시지:** **쓰기 상한의 출처는 사람이 승인한 경로여야 한다 — 설명 산문이 아니다.** 그리고 요구하는 자리(RUNBOOK·템플릿·CI 스텝 이름)와 만드는 자리(`run-unit`·파서·종료 코드)가 어긋나면 그 규칙은 장식이다(§11). 이 단위는 그 어긋남 7개를 같은 커밋 안에서 맞춘다.

## 열린 질문

- `run-unit` 이 인쇄하는 `--spec "$(cat .harness/runs/<id>/<run>/implementer-spec.md)"` 형태가 실제 `orca orchestration task-create` 에서 따옴표·줄바꿈을 그대로 받는지는 다음 관통이 본다 — 이 단위는 인쇄를 고친다.
- 관통 도중 재승인 뒤 같은 run 에 증거를 이어 기록할 때 evidence 의 `base_sha`(첫 계약 값으로 고정)가 어떤 검사에 걸리는지는 따로 시험하지 않았다 — §3.4.1 은 5회차에서 관측된 것(Run 유지 · 봉투 재생성 · close PASS)만 적는다.

### 승인 전 양쪽 실측 (AGENTS.core §11)

실행 방식: 각 검사의 명령 문자열을 YAML 디코딩 값 그대로 `subprocess.run(shell=True)`(evidence·close 재실행과 같은 경로)로 실행. (a) 기존 상태 = `mvp_planning` 체크아웃 `d9a3b12`(이 단위의 문서만 untracked) · (b) 가상 완료 상태 = 프로브 워크트리 `probe-q36-q42`(`d9a3b12` + 프로토타입 변경, 2026-09-02). 새 테스트 자체는 프로브에서 옛 코드 위에 먼저 돌려 40건이 실패(FAIL 24 · ERROR 16)하는 것을 봤고, 옛 코드에서도 통과하는 8건은 대조군·회귀 고정용이다. 검증은 세 렌즈(빈 검사 감사 · AC 반박 · 변경 범위/앵커)로 독립 에이전트가 읽기 전용으로 했고, 그 결과로 check-1·3·5·6·8·10 과 AC-1·2·4·5·6 을 고쳤다.

| 검사 | (a) 기존 | (b) 프로브 | 성격 | 비고 |
| --- | --- | --- | --- | --- |
| check-1 | 1 | 0 (3.5s) | 양쪽 판별 | 기존: 새 클래스 없음(errors=2) |
| check-2 | 1 | 0 (0.1s) | 양쪽 판별 | 기존: 템플릿에 문법 문단 없음 |
| check-3 | 0 | 0 (0.1s) | 회귀 방지 | HEAD 에 이미 `|| true`·`continue-on-error` 없음 |
| check-4 | 0 | 0 (0.3s) | 회귀 방지 | 33/33 이라 옛 90% 규칙에서도 0 — 양성 증명은 check-10 |
| check-5 | 1 | 0 (6.4s) | 양쪽 판별 | 기존: errors=3 |
| check-6 | 1 | 0 (1.8s) | 양쪽 판별 | 기존: errors=2 |
| check-7 | 2 | 0 (0.2s) | 양쪽 판별 | 기존: `check` 선택지 없음(exit 2) · 프로브: 「일치 (판정 0건 · 재검토 0건)」 — 양쪽 없음 분기. 워커 워크트리에서는 §3.5.1 이 남긴 `started` 분기로 0 |
| check-8 | 1 | 0 (0.0s) | 양쪽 판별 | 기존: `해소(2026-09-02` 0행 · 프로브: 7행 |
| check-9 | 1 | 0 (0.0s) | 양쪽 판별 | 기존: D-80 없음 |
| check-10 | 1 | 0 (1.0s) | 양쪽 판별 | 기존: 새 클래스 없음(errors=1) |
| check-11 | 0 | 0 (248.4s) | 회귀 방지 | 기존 702건·208초 → 프로브 762건·248초. 종료 검사 재실행 상한(기본 300초)에 붙어 있어 close 는 `--rerun-timeout 900` 으로 돌린다 |
| check-12 | 0 | 0 (0.4s) | 회귀 방지 |  |
| check-13 | 0 | 0 (0.3s) | 회귀 방지 |  |
| check-14 | 0 | 0 (1.2s) | 회귀 방지 |  |
| check-15 | 0 | 0 (0.3s) | 회귀 방지 |  |
| check-16 | 0 | 0 (2.0s) | 회귀 방지 | 관측 케이스 46an 의 계약 재계산이 새 파서로도 바이트 동일 |

프로브 워크트리(`/Users/julliettelee/orca/workspaces/Romeo-Harness/probe-q36-q42`)는 구현자에게 **읽기 참조**로만 넘긴다 — 쓰지 않고, 그대로 믿지 않으며(승인된 spec 이 원본이고 판정은 구현자가 실행한 검사가 한다), 승인 커밋 기준으로 직접 만든다.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
