---
id: feat-20260831-bmad-attach-probe-tgnb
type: spec
title: G-M3 부착 — discovery.bmad 프로브와 /plan 추천·inputs 링크 요구
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: medium
status: active
approved_at: '2026-08-31T15:24:55+09:00'
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
created: '2026-08-31'
updated: '2026-08-31'
---

# G-M3 부착 — discovery.bmad 프로브와 /plan 추천·inputs 링크 요구

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260831-bmad-attach-probe-tgnb --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** D-77 이 고른 BMAD·CIS 스킬 11종을 라우터에 **연결**한다. 요청이 discovery 나 T2 로 분류되면 분류 카드가
  그 11종을 추천하고, 그 산출물은 복사하지 않고 문서 머리의 `inputs:` 링크로만 붙이라고 요구한다.
  동시에 `romeo doctor` 가 **BMAD 가 설치돼 있는지**를 확인해 결과를 인쇄한다. 지금 이 저장소에는 설치돼 있지 않으므로
  "설치 흔적 없음" 이 정답이다 — 없는 도구를 있는 것처럼 추천하지 않기 위해서다.
- **왜 지금:** G-M3 게이트의 1·2·3단계(아카이브·후보표·사용자 확정)는 2026-08-31 D-77 로 닫혔다.
  남은 것은 4단계(부착)와 5단계(검증)뿐이고, 그것이 §10 체크리스트 13b 의 미완 부분이다.
  확정만 해 두고 연결하지 않으면 D-77 은 문서 안에만 있는 결정으로 남는다.
- **기대 결과:** discovery/T2 요청 하나를 `/plan` 에 넣으면 카드에 11종 추천과 `inputs:` 요구가 인쇄되고,
  같은 카드가 "BMAD 미설치" 를 함께 알린다. `romeo doctor` 에 능력 프로브 절이 생긴다.
- **수용 기준:**
  - [ ] AC-1 `core/policy/capabilities.yaml` 이 생기고 `discovery.bmad` 프로브가 `_bmad/_config/manifest.yaml` 존재와
        거기 기록된 module·platform code 를 확인 대상으로 선언한다. 결과 라벨에 실행을 뜻하는 값이 없다.
  - [ ] AC-2 `romeo doctor` 가 그 프로브를 실행해 결과를 인쇄한다. 미설치는 **결함이 아니다** — doctor 종료 코드를 바꾸지 않는다.
  - [ ] AC-3 `packages.yaml` 의 `parts.bmad-cis` 가 `status: accepted`(G-M3) 로 바뀌고 D-77 의 11종을 `recommends` 로 열거한다.
        deferred 5종·excluded 40종은 그 목록에 없다.
  - [ ] AC-4 discovery 또는 T2 로 분류된 제안의 카드에 11종 추천과 `inputs:` 링크 요구가 인쇄된다.
  - [ ] AC-5 `core/` 어디에도 `_bmad-output` 경로가 하드코딩돼 있지 않다(K-62 · bmm 의 `project_knowledge` 기본값이 `docs` 다).
  - [ ] AC-6 K-68 충돌 fixture 가 3종 늘고 `romeo doctor` 의 충돌 검사가 전부 통과한다.
  - [ ] AC-7 기존 검사 6종(unittest · validate · vendor · notices --check · compile --check · fixtures check)이 그대로 exit 0 이다.
- **위험과 되돌리기:** 정책·문서·fixture 변경뿐이다. BMAD installer 는 **실행하지 않는다** — `.agents/skills/` 는 건드리지 않는다.
  잘못되면 `git revert <커밋>` 하나로 전부 돌아간다. 새 파일만 지우려면 `rm core/policy/capabilities.yaml` 로 충분하다.
- **결정 필요:** 없음 (범위는 2026-08-31 사용자 확정 — "부착 정의까지, 실제 설치는 다음 단위").

## 변경 범위

- 바뀌는 파일·모듈: `core/policy/capabilities.yaml`(신규) · `core/policy/packages.yaml`(`parts.bmad-cis`) ·
  `romeo/doctor.py`(능력 프로브 절) · `romeo/card.py` 또는 `romeo/policy.py`(추천·요구 인쇄) ·
  `core/templates/sections/discovery-plan.md` · `fixtures/conflicts/c5~c7` · `fixtures/proposals/`(discovery 제안 1건) · `tests/`
- 영향을 받는 부분: 앞으로 discovery/T2 로 분류되는 모든 요청의 분류 카드. `romeo doctor` 출력 형식.
- 바꾸지 않는 것(비범위): BMAD 실제 설치 · `.agents/skills/**` · `vendor/**` · BMAD 템플릿 재작성 ·
  `capabilities.yaml` 의 MCP·브라우저 3모드 프로브(M3 의 다른 조각) · deferred 5종의 보류 판정 · `charter.md` 템플릿.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 능력 프로브 정책표를 만든다 | `core/policy/capabilities.yaml` 신규. 최상위 `policy_version`·`capabilities:` 맵. 항목 `discovery.bmad` 는 `kind: install_trace`, `marker: _bmad/_config/manifest.yaml`, `reads: [modules, platform_codes]`, `result_labels: [present, absent]`, `honesty: 설치 흔적일 뿐 실행 증거가 아니다` 를 갖는다 | 소비: 없음 → 생산: 파일 `core/policy/capabilities.yaml`, 프로브 id `discovery.bmad`, 라벨 `present`·`absent` | `python3 -c "import yaml;d=yaml.safe_load(open('core/policy/capabilities.yaml'));c=d['capabilities']['discovery']['bmad'];assert c['marker']=='_bmad/_config/manifest.yaml';assert set(c['result_labels'])=={'present','absent'}"` exit 0 | `rm core/policy/capabilities.yaml` |
| 2 | doctor 가 그 프로브를 돌려 정직하게 인쇄한다 | `romeo/doctor.py` 에 `probe_capabilities(root)` 추가 — marker 파일이 있으면 `present` 와 함께 거기 적힌 module·platform code 를 읽어 인쇄하고, 없으면 `absent` 로 "설치 흔적 없음" 을 인쇄한다. `format_report` 에 「## 능력 프로브」 절 추가. **`absent` 는 problem 으로 세지 않는다** — `doctor_problem_count` 를 바꾸지 않는다 | 소비: 단위1 의 `discovery.bmad`·라벨 → 생산: 함수 `probe_capabilities`, 리포트 키 `capabilities`, 출력 절 제목 `## 능력 프로브` | `bin/romeo doctor` exit 0 이고 출력에 `설치 흔적 없음` 이 있다 | `git checkout romeo/doctor.py` |
| 3 | 라우터가 11종을 추천하고 `inputs:` 를 요구한다 | `core/policy/packages.yaml` 의 `parts.bmad-cis` 를 `status: accepted` · `gate: G-M3` · `decided: '2026-08-31'` 로 바꾸고 `recommends:` 에 D-77 의 11종(`bmad-product-brief`·`bmad-prfaq`·`domain-research`·`market-research`·`technical-research`·`bmad-brainstorming`·`bmad-forge-idea`·CIS `design-thinking`·`innovation-strategy`·`problem-solving`·`storytelling`)을 열거한다. `output_binding: inputs-link` 를 둔다. `romeo/card.py` 가 parts 를 인쇄할 때 `recommends` 와 "산출물은 frontmatter `inputs:` 로만" 한 줄, 그리고 단위2 의 프로브 결과를 함께 인쇄한다 | 소비: 단위2 의 `probe_capabilities` → 생산: `parts.bmad-cis.recommends`(11개), `output_binding`, 카드 부품 절 | `bin/romeo route --proposal fixtures/proposals/fx-bmad-discovery-recommend.yaml --card` 출력에 `bmad-product-brief` 와 `inputs:` 가 둘 다 있다 | `git checkout core/policy/packages.yaml romeo/card.py` |
| 4 | 빈칸에 규칙을 적고 충돌을 fixture 로 고정한다 | `core/templates/sections/discovery-plan.md` 의 「조사 방법·기간」 아래에 "부품 산출물은 경로를 본문에 적지 않고 frontmatter `inputs:` 로만 붙인다(K-62)" 를 넣는다. `fixtures/conflicts/` 에 3종 추가 — `c5-bmad-install-path`(설치 경로 `.agents/skills` 가 `.harness/compiled.yaml` 의 prune 대상과 겹치지 않는다, K-64) · `c6-no-second-plan-origin`(deferred 5종이 `recommends` 에 없다, K-61) · `c7-no-output-path-hardcode`(`core/` 에 `_bmad-output` 문자열 0, K-62). `romeo/doctor.py` 의 `check_conflicts` 가 셋을 실행한다. `fixtures/proposals/fx-bmad-discovery-recommend.yaml`(단위3 이 쓰는 discovery 제안)도 여기서 만든다 | 소비: 단위3 의 `recommends`·`output_binding` → 생산: fixture id `c5-bmad-install-path`·`c6-no-second-plan-origin`·`c7-no-output-path-hardcode`, 제안 fixture 경로 | `bin/romeo doctor` 출력의 충돌 fixture 개수가 7종이고 `충돌 0` | `git checkout core/templates/sections/discovery-plan.md romeo/doctor.py && rm fixtures/conflicts/c5-*.yaml fixtures/conflicts/c6-*.yaml fixtures/conflicts/c7-*.yaml fixtures/proposals/fx-bmad-discovery-recommend.yaml` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 이 단위는 하네스 저장소 **자신**을 대상으로 하므로
`unittest`·`validate`·`compile --check`·`doctor`·`fixtures check` 가 이 단위의 산출물에 대한 검사로서 정당하다.

**종료 코드 자체가 조건이다.** 검사에 적는 것은 `id` 와 `command` 둘뿐이고, 그 명령의 종료 코드 0 이 통과다.
`|| true` 를 붙이지 않는다 — 종료 코드를 항상 0 으로 만들어 위반을 통과시킨다.
부정 조건은 `!` 로 쓴다: `! grep -q '<있으면 안 되는 것>' <파일>`.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest discover -s tests"
  - id: check-2
    command: "bin/romeo validate"
  - id: check-3
    command: "bin/romeo compile --check"
  - id: check-4
    command: "bin/romeo fixtures check"
  - id: check-5
    command: "bin/romeo doctor"
  - id: check-6
    command: "python3 -c \"import yaml;c=yaml.safe_load(open('core/policy/capabilities.yaml'))['capabilities']['discovery']['bmad'];assert c['marker']=='_bmad/_config/manifest.yaml';assert sorted(c['result_labels'])==['absent','present']\""
  - id: check-7
    command: "bin/romeo doctor | grep -q '설치 흔적 없음'"
  - id: check-8
    command: "python3 -c \"import yaml;p=yaml.safe_load(open('core/policy/packages.yaml'))['parts']['bmad-cis'];assert p['status']=='accepted';assert len(p['recommends'])==11;assert not ({'bmad-prd','bmad-architecture','bmad-ux'} & set(p['recommends']))\""
  - id: check-9
    command: "bin/romeo route --proposal fixtures/proposals/fx-bmad-discovery-recommend.yaml --card | grep -q 'bmad-product-brief'"
  - id: check-10
    command: "bin/romeo route --proposal fixtures/proposals/fx-bmad-discovery-recommend.yaml --card | grep -q 'inputs:'"
  - id: check-11
    command: "! grep -rq '_bmad-output' core/"
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
