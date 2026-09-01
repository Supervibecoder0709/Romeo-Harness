---
id: feat-20260901-charter-discovery-block-a3xs
type: spec
title: Charter(T2) 템플릿과 discovery 차단 집행을 세운다 — 계산만 되던 blocks 를 종료 검사에 붙인다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: active
approved_at: '2026-09-01T15:26:22+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-01'
updated: '2026-09-01'
---

# Charter(T2) 템플릿과 discovery 차단 집행을 세운다 — 계산만 되던 blocks 를 종료 검사에 붙인다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260901-charter-discovery-block-a3xs --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 라우터가 계산해 카드에 인쇄까지 하는 **차단**(`spec-ready`·`milestone-plan`·`discovery-result`·`approval-gate`)이
  실제로는 아무것도 막지 못하는 상태를 고친다. 차단마다 충족 조건을 정하고, 승인 시점과 완료 시점 두 곳에서 집행한다.
  함께 T2 가 요구하는 Charter 문서 템플릿을 만들고, 조사 없이 구현으로 넘어가는 것을 막는 시나리오 3 을 런북과 테스트로 고정한다.
- **왜 지금:** 구현 계획 §7 M3 이 요구하는 시나리오 3 을 세우려고 열어 보니 그보다 앞선 결함이 있었다 —
  `romeo/close.py` 는 실행 가드(`guards`)만 검사하고 **차단(`blocks`)은 한 번도 읽지 않는다.**
  정책표와 분류 카드에는 "차단 spec-ready" 라고 찍히는데 그 글자가 막는 것이 없다.
  Charter 템플릿도 없어서 T2 요청은 지금 charter 없이 brief+spec 만 만들어진다.
- **기대 결과:** 조사 결과 없이 discovery 단위를, 마일스톤 없이 T2 단위를 승인할 수 없게 된다.
  정책표에 새 차단을 적고 집행을 잊으면 정책 로드 자체가 실패한다 — 지금 이 결함이 같은 모양으로 재발하지 않는다.
  T2 요청이 Charter 부터 만들어진다.
- **수용 기준:**
  - [ ] AC-1 `core/templates/charter.md` 가 있고 「마일스톤 계획」 절을 갖는다. T2 분류로 문서를 만들면 charter.md 가 `NOT_AVAILABLE_YET` 없이 생성된다.
  - [ ] AC-2 정책표에 차단 카탈로그가 생기고, 기본 패키지·오버레이가 쓰는 모든 차단 id 가 카탈로그와 집행 코드 양쪽에 있어야 정책이 로드된다 — 한쪽이라도 없으면 로드가 실패한다.
  - [ ] AC-3 차단이 미충족이면 `romeo approve` 가 승인을 거부하고, 어느 차단이 무엇 때문에 막았는지가 메시지에 나온다.
  - [ ] AC-4 `romeo close` 가 그 단위에 걸린 차단마다 `BLOCK_SATISFIED` 판정을 낸다.
  - [ ] AC-5 `discovery-result` 는 discovery 단위의 frontmatter `inputs:` 가 비어 있으면 막는다 — 조사 산출물은 복사가 아니라 링크로만 붙는다(K-62).
  - [ ] AC-6 `milestone-plan` 은 T2 단위에 charter.md 가 없거나 마일스톤 절이 채워지지 않았으면 막는다.
  - [ ] AC-7 `scenarios/3-discovery-block.md` 런북이 있고, 그 단계를 자동 실행하는 테스트가 기존 discovery·T2 fixture 로 차단·부품 추천·`inputs:` 요구를 재현한다.
  - [ ] AC-8 차단은 소급하지 않는다 — 이미 `done` 인 단위를 다시 검사해도 판정(FAIL·`NOT_ALREADY_DONE`)과 문서가 그대로다.
- **위험과 되돌리기:** `romeo/close.py`·`romeo/docs.py` 는 이 저장소가 자기 작업을 닫는 데 쓰는 코드다.
  잘못 손대면 **이 단위 자신이 닫히지 않거나**, 반대로 막아야 할 것을 통과시킨다. 그래서 AC-8 이 소급 금지를 검사로 고정하고,
  차단 판정은 전부 반례 테스트(막아야 할 입력이 실제로 막히는지)로 확인한다. 전부 저장소 안 파일이고 외부 상태를 바꾸지 않는다 —
  되돌리기는 `git revert <통합 커밋>` 이다.
- **결정 필요:** 없음

## 변경 범위

- 바뀌는 파일·모듈:
  - `core/templates/charter.md` (신규) — T2 문서. 마일스톤 계획 절을 포함한다.
  - `core/policy/packages.yaml` — 차단 카탈로그 절 신설(`blocks:`). 각 차단의 이름·집행 지점·충족 조건 한 줄.
  - `romeo/blocks.py` (신규) — 차단 id 마다 충족 판정 함수. 카탈로그와 이 매핑이 어긋나면 로드 실패.
  - `romeo/policy.py` — 정책 로드 시 카탈로그·매핑 대조.
  - `romeo/docs.py` — `approve_unit` 이 승인 전에 차단을 검사하고 미충족이면 거부.
  - `romeo/close.py` — `BLOCK_SATISFIED` 검사 추가.
  - `scenarios/README.md`·`scenarios/3-discovery-block.md` (신규) — 시나리오 런북.
  - `tests/test_blocks_enforcement.py`·`tests/test_scenario_3.py` (신규).
- 영향을 받는 부분: 앞으로 만들어지는 모든 작업 단위의 승인·종료 판정. discovery 단위와 T2 단위가 특히 바뀐다.
- 바꾸지 않는 것(비범위):
  - 실행 가드 집행(`gate-create` 승인 흐름) — 시나리오 9 의 몫이다.
  - `romeo doctor` 의 MCP·브라우저 프로브와 `BLOCKED_CAPABILITY` — 시나리오 8 의 몫이다.
  - `fixtures/requests/*.yaml` 의 기대값 — 이미 차단을 기대값으로 갖고 있고, 그것이 이 단위의 **대조 대상**이라 고치지 않는다.
  - 이미 `status: done` 인 13개 단위의 문서·판정.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — *무엇을* 없이 *하겠다*고만 쓴 칸은 미완료 표시로 취급하고 승인 전에 채운다(Q-20). **인터페이스** 열은 앞 단위가 만든 이름을 뒤 단위가 알게 하는 칸이다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | Charter 템플릿 | `core/templates/charter.md` 신규 — 왜 이 이니셔티브인가 / 범위·비범위 / **마일스톤 계획** / 제약·전제 / 위험·중단 조건 / 연결. 자리표시자는 다른 템플릿과 같은 `{{id}}`·`{{title}}`·`{{extra_sections}}` 규약을 따른다 | 소비: `romeo/docs.py` 의 자리표시자 치환 → 생산: `## 마일스톤 계획` 절 제목(차단 `milestone-plan` 이 이 제목을 찾는다) | `check-1`·`check-2`·`check-9` | 파일 삭제 |
| 2 | 차단 카탈로그 | `core/policy/packages.yaml` 에 `blocks:` 절 — 차단 id → `{title, enforced_at, requires}`. base·overlay 가 쓰는 4개(`spec-ready`·`milestone-plan`·`discovery-result`·`approval-gate`)를 전부 적는다 | 소비: 없음 → 생산: `pk["blocks"]` 키 | `check-3` | yaml 절 삭제 |
| 3 | 집행 매핑과 로드 대조 | `romeo/blocks.py` 신규 — `BLOCK_CHECKS` 매핑과 `satisfied(block_id, ...) -> (ok, reason)`. `romeo/policy.py` 의 로드가 카탈로그·매핑·실사용 세 집합을 대조해 어긋나면 예외 | 소비: 2번의 `pk["blocks"]` → 생산: `romeo.blocks.BLOCK_CHECKS`·`satisfied()` | `check-4` | 모듈 삭제 + policy.py 대조 제거 |
| 4 | 승인 시점 집행 | `romeo/docs.py` `approve_unit` 이 라우팅을 재계산해 걸린 차단을 `satisfied()` 로 검사하고, 미충족이면 어느 차단이 왜 막았는지 담은 `ValueError` | 소비: 3번의 `satisfied()` → 생산: 승인 거부 경로 | `check-5`·`check-6`·`check-7` | 검사 호출 제거 |
| 5 | 종료 시점 집행 | `romeo/close.py` 가 차단마다 `BLOCK_SATISFIED` 검사를 낸다. `status: done` 인 단위는 기존대로 맨 앞에서 반환되므로 소급하지 않는다 | 소비: 3번의 `satisfied()` → 생산: `BLOCK_SATISFIED` 검사 이름 | `check-8`·`check-9` | 검사 호출 제거 |
| 6 | 시나리오 3 런북 | `scenarios/README.md`(런북 형식)·`scenarios/3-discovery-block.md`(기대 판단·산출물·증거). `tests/test_scenario_3.py` 가 그 단계를 fixture 로 자동 실행 | 소비: 1~5번 전부 → 생산: `scenarios/` 디렉터리 | `check-10`·`check-11` | 디렉터리·테스트 삭제 |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 이 단위는 하네스 저장소 **자신**이 대상이므로 `python3 -m unittest`·`bin/romeo` 자기 검사가 정당하다.
**종료 코드 자체가 조건이다** — `id` 와 `command` 둘만 적고 exit 0 이 통과다. `|| true` 를 붙이지 않고 부정 조건은 `!` 로 쓴다.
`check-1`~`check-11` 은 승인 시점의 현재 트리에서 **전부 exit 0 이 아니어야** 한다(빈 검사가 아니라는 음성 대조).
`check-12`~`check-17` 은 지금도 exit 0 인 회귀 검사다 — 이미 서 있는 것을 무너뜨리지 않았음을 본다.

```yaml
required_checks:
  - id: check-1
    command: "test -f core/templates/charter.md"
  - id: check-2
    command: "grep -q '^## 마일스톤 계획' core/templates/charter.md"
  - id: check-3
    command: "python3 -m unittest tests.test_blocks_enforcement.TestBlockCatalog"
  - id: check-4
    command: "python3 -m unittest tests.test_blocks_enforcement.TestCatalogMappingMismatch"
  - id: check-5
    command: "python3 -m unittest tests.test_blocks_enforcement.TestApproveRejectsUnsatisfied"
  - id: check-6
    command: "python3 -m unittest tests.test_blocks_enforcement.TestDiscoveryResultNeedsInputs"
  - id: check-7
    command: "python3 -m unittest tests.test_blocks_enforcement.TestMilestonePlanNeedsCharter"
  - id: check-8
    command: "python3 -m unittest tests.test_blocks_enforcement.TestCloseReportsBlockSatisfied"
  - id: check-9
    command: "python3 -m unittest tests.test_blocks_enforcement.TestNoRetroactiveEffect"
  - id: check-10
    command: "python3 -m unittest tests.test_scenario_3"
  - id: check-11
    command: "test -f scenarios/3-discovery-block.md && test -f scenarios/README.md"
  - id: check-12
    command: "bin/romeo close --unit feat-20260901-task-copy-brief-count-erc6 --dry-run --no-rerun > /dev/null; test $? -eq 1"
  - id: check-13
    command: "python3 -m unittest discover -s tests"
  - id: check-14
    command: "bin/romeo compile --check"
  - id: check-15
    command: "bin/romeo validate"
  - id: check-16
    command: "bin/romeo doctor --strict --scope repository"
  - id: check-17
    command: "bin/romeo fixtures check"
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
