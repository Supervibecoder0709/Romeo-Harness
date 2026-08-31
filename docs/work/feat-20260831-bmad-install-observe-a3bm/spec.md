---
id: feat-20260831-bmad-install-observe-a3bm
type: spec
title: G-M3 검증 — BMAD 실제 설치와 두 런타임 discovery 관측
unit: T1
mode: experiment
intent: mixed
facets: [tooling, docs, security]
gates: [privacy-security]
profile: standard
blast_radius: medium
uncertainty: medium
status: active
approved_at: '2026-08-31T21:35:37+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:gate.any=kept', 'profile:mode.experiment=kept', 'profile:uncertainty.medium=kept',
    'overlay:gate.any', 'overlay:mode.experiment', 'overlay:profile.standard-or-deeper', 'guard:production-deploy',
    'guard:deletion']
  history: []
created: '2026-08-31'
updated: '2026-08-31'
approval_history:
- {approved_at: '2026-08-31T18:14:41+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-08-31T19:44:03+09:00',
  reason: '1회차 관통(run_67c238a254e1)이 검증 계획의 결함 2건을 드러내 재승인한다. check-4 는 bin/romeo doctor 였는데 --strict
    없이는 저장소 결함이 있어도 항상 exit 0 이라 빈 검사였다 — --strict --scope repository 로 바꿨다(그 결과 1회차가 남긴 K-62 위반 c7 을
    실제로 잡는다). check-8 은 전역 비교 대상에 codex CLI 가 소유한 ~/.codex/skills/.system/ 이 들어 있었는데, codex 런타임을 띄우는 것
    자체가 그 디렉터리를 다시 쓰고 이 단위는 codex 를 반드시 띄우므로 설계상 통과할 수 없는 검사였다 — 비교에서 */.system/* 을 빼고, 대신 설치 직후마다는 제외
    없이 전체로 대조하도록 했다. AC-2·AC-4 문장에 그 근거를 드러냈다. 하네스 테스트 4건의 환경 단언은 관통 사이 정비(c7c1b53)로 이미 걷어냈다.'}
- {approved_at: '2026-08-31T19:44:03+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-08-31T21:35:37+09:00',
  reason: '3회차 관통(run_923ba2a01bb4)의 검토자 findings 3건이 전부 산출물이 아니라 spec 문장을 겨눠 그 두 자리를 고치고 다시 승인한다. ① 확인란이
    설치 방법(「한 번에 하나씩(codex 먼저)」)을 못박았는데 BMAD 의 --tools 가 더하기가 아니라 교체라서 그 방법으로는 AC-5(두 런타임 각각에서 bmad-* 로드
    관측)를 달성할 수 없었다 — 확인란이 자기 수용 기준을 금지한 것이므로 방법을 확인란에서 빼 구현 단위 4행으로 옮기고, 그 행에 결합 설치(--tools codex,claude-code)와
    --action update 가 필요한 이유를 실측 근거와 함께 적었다(Q-24). ② ③ baseline 2건을 docs/work/<id>/ 안에 리다이렉트로 만들어 내용이
    어디에도 봉인되지 않았다 — romeo/evidence.py:37 의 exclusions() 가 그 폴더를 dirty_tree_hash·changed_files·artifact_hash
    에서 전부 빼기 때문이다(3회차 실측: stdout_tail 3건 전부 빈 문자열). 구현 단위 2행을 tee 로 바꾸고 stdout_tail 이 비어 있지 않은지를 확인 조건에
    넣었다(Q-23). 수용 기준 문장과 검증 계획 12건은 바꾸지 않았다 — 고친 것은 방법과 봉인 경로뿐이다.'}
---

# G-M3 검증 — BMAD 실제 설치와 두 런타임 discovery 관측

> 깊이 **Standard** · 단위 T1 · 모드 experiment · 의도 mixed · 영역 tooling, docs, security · 게이트 privacy-security
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260831-bmad-install-observe-a3bm --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 격리 워크트리에서 BMAD 를 **실제로 설치**하고, 설치기가 romeo 스킬을 지우는지 · 프로브가 실제 설치본에서 `present` 를 내는지 · 두 런타임이 `bmad-*` 를 실제로 discovery 하는지를 관측해 기록한다. 설치본은 저장소에 커밋하지 않는다 — 저장소에 남기는 것은 **관측 기록**뿐이다.
- **왜 지금:** 라우터는 이미 BMAD 스킬 11종을 추천하고 있는데, 그 스킬들이 설치했을 때 실제로 쓸 수 있는지는 아무도 확인하지 않았다. 프로브의 `present` 분기는 marker 파일을 흉내 낸 테스트로만 확인됐다. 추천을 관측에 근거하게 만드는 것이 G-M3 5단계의 남은 절반이다.
- **기대 결과:** ① romeo 스킬(claude 11종·codex 12종)이 설치 뒤에도 그대로다 ② 프로브가 실제 설치본에서 처음으로 `present` 를 낸다 ③ 두 런타임의 스킬 목록에 `bmad-*` 가 나타났는지가 실행 출력으로 기록된다 ④ `capabilities.yaml` 의 "테스트로만 확인했다" 가 실측 기록으로 바뀐다. **공존이 불가능하다는 결과도 유효한 결과다** — 그때는 되돌리고 멈춘 뒤 사람에게 돌아온다.
- **수용 기준:**
  - [ ] AC-1 설치 **직전**에 두 스킬 디렉터리의 sha256 목록을 파일로 고정하고, 설치 후 그 대조가 전부 통과한다 — romeo 스킬이 하나도 바뀌지 않았다.
  - [ ] AC-2 저장소 밖(홈의 전역 스킬 디렉터리)에 변화가 없다. 설치 직전에 뜬 목록과 설치 후 목록이 같다. **비교에서 `*/.system/*` 은 뺀다** — 1회차에서 codex 런타임을 띄우는 것 자체가 `~/.codex/skills/.system/` 을 통째로 다시 쓴다는 것이 관측됐고(설치기가 한 일이 아니다), 이 단위는 codex 를 반드시 띄우므로 그것을 넣은 채로는 통과할 수 없는 검사가 된다. 그 대신 설치 **직후마다** 대조해 설치기 자신의 쓰기를 잡는다.
  - [ ] AC-3 `_bmad/_config/manifest.yaml` 이 생기고 `romeo doctor` 의 능력 프로브가 `discovery.bmad: present` 를 인쇄한다.
  - [ ] AC-4 설치 뒤에도 `romeo compile --check` · `romeo doctor --strict --scope repository` · `romeo validate` · 하네스 테스트가 전부 통과한다. **`--strict` 가 붙어야 판정이 된다** — 1회차에서 `bin/romeo doctor` 만으로는 저장소 결함이 있어도 exit 0 이라 빈 검사였다(Q-21).
  - [ ] AC-5 두 런타임 각각의 스킬 목록에 `bmad-*` 가 나타났는지, CIS workflow 1종을 agent 없이 직접 호출했을 때 시작되는지가 실행 출력과 함께 `.harness/observations.yaml` 에 기록된다. **"나타나지 않았다" 도 유효한 기록**이며 그렇게 적는다.
  - [ ] AC-6 `core/policy/capabilities.yaml` 에서 "marker 파일을 흉내 낸 테스트로만 확인했다" 문장이 사라지고 실측 기록으로 대체된다. `provenance/imports.yaml` 의 `bmad-cis.unverified` 도 같은 시점에 갱신된다.
  - [ ] AC-7 설치 산출물이 git 에 들어가지 않는다 — `_bmad/` · `_bmad-output/` · 두 스킬 디렉터리의 `bmad-*` 가 무시되고, 추적 트리에 untracked 로 남지 않는다.
- **위험과 되돌리기:** 위험은 셋이다. ① `npx` 가 **외부 Node 코드를 받아 실행**한다 — 무엇을 쓰는지 사전에 알 수 없다. ② 설치 대상이 romeo 스킬이 사는 바로 그 두 디렉터리다 — 지워지면 `/plan` 자체가 안 돈다. ③ 아카이브 [E09] 는 codex 설치 경로에 **전역 `~/.codex/skills`** 를 적고 있다 — 저장소 밖이라 워크트리 격리로 막히지 않는다. 되돌리기: 저장소 안은 두 디렉터리가 git 추적이고 트리가 clean 이므로 `git checkout -- .claude/skills .agents/skills` 로 복원되고, `romeo compile` 로도 재생성된다. 작업 자체가 **버리는 워크트리**에서 일어나므로 메인 체크아웃은 처음부터 손대지 않는다. 저장소 밖은 되돌리지 않고 **먼저 관측해 멈춘다** — 설치 직전에 전역 목록을 떠 두고, 변화가 보이면 그 자리에서 중단하고 보고한다.
- **결정 필요:** 없음 — 설치 승인 자체가 이 확인란의 승인이다. **설치를 몇 번에 나눠 어떤 순서로 실행할지는 방법이므로 구현 단위 표가 정한다** — 확인란은 결과와 그 이유만 담는다. 3회차에서 확인란이 방법(「한 번에 하나씩」)을 못박는 바람에 그 방법으로는 AC-5 를 달성할 수 없다는 것이 실행 중에 드러났고, 구현자는 관측을 위해 결합 설치를 했으며 검토자는 그것을 승인되지 않은 행위로 정확히 잡았다 — 둘 다 옳았고 결함은 승인된 문장에 있었다(Q-24).

## 변경 범위

- 바뀌는 파일·모듈: `core/policy/capabilities.yaml` · `provenance/imports.yaml` · `.harness/observations.yaml` · `.gitignore` · `docs/work/feat-20260831-bmad-install-observe-a3bm/` · `_bmad/` · `_bmad-output/` · `.claude/skills/` · `.agents/skills/`
- 영향을 받는 부분: `romeo doctor` 의 「능력 프로브」 출력(설치된 머신에서만 `present`), 라우터가 discovery·T2 요청에 인쇄하는 추천 카드의 프로브 줄. 규칙·템플릿·라우터 로직은 그대로다.
- 바꾸지 않는 것(비범위): `core/` 의 규칙·워크플로·템플릿, `core/policy/packages.yaml` 의 추천 11종 목록, D-77 이 deferred 로 둔 5종, 충돌 fixture 7종, BMAD 파일의 저장소 커밋(벤더링), workflow 완주와 그 산출물 품질 평가.

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 설치 산출물이 git 에 새지 않게 막는다 | `.gitignore` 에 `_bmad/` · `_bmad-output/` · `.claude/skills/bmad-*` · `.agents/skills/bmad-*` 4줄을 더한다 | 소비: 없음 → 생산: 무시 규칙 4줄 | `git check-ignore -q _bmad && git check-ignore -q _bmad-output && git check-ignore -q .claude/skills/bmad-probe && git check-ignore -q .agents/skills/bmad-probe` 가 exit 0 | `git checkout -- .gitignore` |
| 2 | 설치 직전 상태를 **원시 로그에 봉인해** 고정한다 | `docs/work/feat-20260831-bmad-install-observe-a3bm/evidence/skills-before.sha256`(두 스킬 디렉터리 전 파일) 과 `evidence/home-skills-before.txt`(전역 목록, `*/.system/*` 제외 · `$HOME` 을 `~` 로 치환 — check-8 과 **같은 제외**로 떠야 대조가 성립한다) 를 만든다. **두 파일 다 `> 파일` 이 아니라 `\| tee 파일` 로 만들고, 그 명령을 `bin/romeo evidence run` 으로 실행한다** — `romeo/evidence.py:37` 의 `exclusions()` 가 `docs/work/<unit_id>/` 를 `dirty_tree_hash`·`changed_files`·`artifact_hash` 에서 전부 빼므로, 그 폴더 안에 리다이렉트로 만든 기준 파일은 **언제 어떤 내용이었는지 아무 데도 봉인되지 않는다**(3회차 실측: baseline 3건의 `stdout_tail` 이 전부 빈 문자열이었고 검토자가 이것을 findings 2건으로 잡았다, Q-23). `tee` 는 같은 내용을 stdout 에도 남기므로 원시 로그와 `log_sha256` 이 그 시점의 내용을 봉인한다 | 소비: 없음 → 생산: `evidence/skills-before.sha256` · `evidence/home-skills-before.txt` · **그 두 파일의 내용이 실린 원시 로그** | 두 파일이 존재하고 `shasum -a 256 -c evidence/skills-before.sha256` 이 설치 전에 exit 0. **그리고 그 두 생성 명령의 `stdout_tail` 이 비어 있지 않다** — 비어 있으면 `tee` 를 쓰지 않은 것이므로 다시 만든다 | 파일 삭제 후 재생성. 저장소 상태를 바꾸지 않는다 |
| 3 | codex 대상 설치를 관측한다 | `npx bmad-method install --directory . --modules core,bmm,cis --tools codex --yes` 를 실행하고 즉시 baseline 2건을 대조한다 | 소비: 2행의 baseline 2건 → 생산: `_bmad/_config/manifest.yaml`, `.agents/skills/bmad-*`, 설치 로그 | `shasum -a 256 -c` 가 exit 0 이고 전역 목록 `diff` 가 exit 0. **설치 직후 대조는 `.system/` 을 빼지 않고 전체로 한다** — 그 순간에는 codex 가 개입하지 않으므로 설치기 자신의 쓰기를 그대로 잡는다. 하나라도 실패하면 **중단 조건 발동** — 되돌리고 4행을 실행하지 않는다. `cis` 는 external official module 이라 비대화형 설치로 resolve 되지 않을 수 있다 — 그때는 `--modules core,bmm` 으로 한 번만 다시 시도하고, 그래도 안 되면 **그 사실을 관측으로 기록**하고 넘어간다(재시도 반복 금지) | `git checkout -- .agents/skills` · `rm -rf _bmad` · 워크트리 폐기 |
| 4 | 설치 대상을 **두 런타임으로 확장**해 관측한다 | 3행이 통과했을 때만. `npx bmad-method install --directory . --modules core,bmm,cis --tools codex,claude-code --action update --yes` 를 실행하고 같은 2건을 대조한다. **`--tools claude-code` 만 주지 않는다** — `--tools` 는 더하기가 아니라 **교체**라서 3행이 깐 `.agents/skills/bmad-*` 가 제거된다(1~3회차 실측). AC-5 는 두 런타임 **각각**에서 로드를 관측하라고 요구하므로 두 값을 함께 주는 것이 그 기준을 달성하는 유일한 경로다. **`--action update` 를 빼지 않는다** — 기존 설치본에 `--yes` 만 주면 quick-update 로 빠져 `--tools` 를 읽지 않고 exit 0 으로 끝난다(같은 실측). 3행을 단독으로 먼저 돌리는 이유는 그대로다: 그 순간의 대조가 설치기 **자신의** 쓰기를 잡는다 | 소비: 3행 통과 → 생산: `.claude/skills/bmad-*` · `.agents/skills/bmad-*`(유지됨) | 3행과 같은 대조가 exit 0 이고, **대조 뒤 두 디렉터리에 `bmad-*` 가 동시에 존재한다**(`ls .claude/skills/bmad-* .agents/skills/bmad-*` 가 exit 0) | `git checkout -- .claude/skills .agents/skills` |
| 5 | 프로브와 하네스 자기 검사가 설치 뒤에도 성립하는지 본다 | 없음(읽기 실행) | 소비: 3·4행의 설치 → 생산: `doctor` · `compile --check` · `validate` · 테스트 출력 | `bin/romeo doctor 2>&1 \| grep -q "discovery.bmad: present"` 가 exit 0 이고, `compile --check` · `validate` · 하네스 테스트가 exit 0 | 되돌릴 것 없음. 실패는 그대로 기록한다 |
| 6 | 두 런타임이 `bmad-*` 를 실제로 로드하는지 관측한다 | 없음(각 런타임을 그 워크트리에서 띄워 스킬 목록을 받는다) | 소비: 3·4행의 설치 → 생산: 각 런타임의 스킬 목록 원문 | 받은 목록에 `bmad-` 로 시작하는 이름이 있는지 없는지가 출력에 그대로 남는다. **없다는 결과도 기록한다** | 되돌릴 것 없음 |
| 7 | agent 없이 workflow SKILL 을 직접 호출하는 경로를 관측한다 | 없음(CIS workflow 1종을 한 번 호출한다. **완주시키지 않는다** — 첫 단계가 시작되는지까지만) | 소비: 4행의 설치 → 생산: 호출 출력 | 런타임이 그 SKILL 을 로드해 시작했는지 여부가 출력에 남는다 | `rm -rf _bmad-output` (무시 대상이라 저장소에 영향 없음) |
| 8 | 관측을 저장소에 기록한다 | `.harness/observations.yaml` 에 관측 항목을 더하고, `core/policy/capabilities.yaml` 의 `unverified:`·`expected_here:` 와 `provenance/imports.yaml` 의 `bmad-cis.unverified` 를 실측 결과로 바꾼다 | 소비: 3~7행의 관측 → 생산: 갱신된 3파일 | `! grep -q "흉내 낸 테스트로만 확인했다" core/policy/capabilities.yaml` 이 exit 0 이고 `romeo validate` 가 통과 | `git checkout -- .harness/observations.yaml core/policy/capabilities.yaml provenance/imports.yaml` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

이 작업 단위의 대상은 **하네스 저장소 자신**이므로 `bin/romeo` 의 자기 검사와 하네스 테스트가 이 단위의 산출물이고, 검사에 넣는 것이 정당하다.

**종료 코드 자체가 조건이다.** `|| true` 를 붙이지 않는다. 부정 조건은 `!` 로 쓴다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest discover -s tests"
  - id: check-2
    command: "bin/romeo validate"
  - id: check-3
    command: "bin/romeo compile --check"
  - id: check-4
    command: "bin/romeo doctor --strict --scope repository"
  - id: check-5
    command: "shasum -a 256 -c docs/work/feat-20260831-bmad-install-observe-a3bm/evidence/skills-before.sha256"
  - id: check-6
    command: "test -f _bmad/_config/manifest.yaml"
  - id: check-7
    command: "bin/romeo doctor 2>&1 | grep -q 'discovery.bmad: present'"
  - id: check-8
    command: "find \"$HOME/.codex/skills\" \"$HOME/.claude/skills\" -type f -not -path \"*/.system/*\" 2>/dev/null | sed \"s|^$HOME|~|\" | sort | diff - docs/work/feat-20260831-bmad-install-observe-a3bm/evidence/home-skills-before.txt"
  - id: check-9
    command: "git check-ignore -q _bmad && git check-ignore -q _bmad-output && git check-ignore -q .claude/skills/bmad-probe && git check-ignore -q .agents/skills/bmad-probe"
  - id: check-10
    command: "! git status --porcelain --untracked-files=all | grep -qE '^\\?\\? (_bmad|\\.claude/skills/bmad-|\\.agents/skills/bmad-)'"
  - id: check-11
    command: "! grep -q '흉내 낸 테스트로만 확인했다' core/policy/capabilities.yaml"
  - id: check-12
    command: "python3 -c \"import yaml; d=yaml.safe_load(open('.harness/observations.yaml')); assert 'bmad_install' in d\""
```

**대응:** AC-1→check-5 · AC-2→check-8 · AC-3→check-6·check-7 · AC-4→check-1·2·3·4 · AC-5→check-12 · AC-6→check-11 · AC-7→check-9·check-10.

check-12 는 기록의 **존재**만 본다. 그 안에 무엇이 적혔는지(로드됐다/안 됐다)는 검토자가 읽는다 — 기계가 판정하면 "관측이 유리하게 나왔는지" 를 완료 조건으로 만들게 된다.

## 위험·백업·복구

hard gate(privacy-security)가 발동했다. 승인 전 상태 변경 0건.

- **영향 범위:** 저장소 안에서는 `.claude/skills`(23 추적 파일) · `.agents/skills`(20 추적 파일) · 저장소 루트(`_bmad/`, `_bmad-output/`). 저장소 밖에서는 npm 캐시, BMAD 의 external module git 캐시, 그리고 **잠재적으로 전역 `~/.codex/skills`·`~/.claude/skills`**. 운영 환경·사용자 데이터·외부 서비스는 없다.
- **사전 백업:** 작업은 `orca worktree create` 로 만든 **버리는 워크트리**에서만 한다 — 메인 체크아웃은 처음부터 손대지 않는다. 그 안에서 설치 직전에 두 스킬 디렉터리의 sha256 목록(`evidence/skills-before.sha256`)과 전역 스킬 디렉터리 목록(`evidence/home-skills-before.txt`)을 고정한다. 설치 시작 조건은 `git status` clean 이다.
- **복구 방법:** 저장소 안 — `git checkout -- .claude/skills .agents/skills` 로 romeo 스킬을 복원하고 `rm -rf _bmad _bmad-output` 로 설치본을 지운다. 그래도 어긋나면 `bin/romeo compile` 이 두 디렉터리를 코어에서 다시 만든다. 최후 수단은 워크트리 폐기이고 메인 체크아웃은 영향받지 않는다. 저장소 밖 — 되돌리지 않는다. **관측해서 멈추는 것이 이 위험에 대한 대응이다**: 전역 목록에 변화가 보이면 그 자리에서 중단하고 사람에게 보고한다.
- **확인할 내용(승인자용):** 승인하는 것은 "**외부 Node 패키지를 내려받아 실행하고, 그것이 이 저장소의 두 스킬 디렉터리에 쓰게 하는 것**" 이다. 되돌릴 수 있는 범위는 저장소 안까지이고, 홈 디렉터리에 남을 수 있는 흔적은 관측해서 멈추는 것으로만 대응한다. 이 두 가지에 동의하는지가 승인의 내용이다.
- **승인 기록:** evidence.approvals 에 남긴다

## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
