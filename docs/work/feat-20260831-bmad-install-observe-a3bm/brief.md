---
id: feat-20260831-bmad-install-observe-a3bm
type: brief
title: G-M3 검증 — BMAD 실제 설치와 두 런타임 discovery 관측
unit: T1
mode: experiment
intent: mixed
facets: [tooling, docs, security]
gates: [privacy-security]
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
  fired_rules: ['profile:base:T1=standard', 'profile:gate.any=kept', 'profile:mode.experiment=kept', 'profile:uncertainty.medium=kept',
    'overlay:gate.any', 'overlay:mode.experiment', 'overlay:profile.standard-or-deeper', 'guard:production-deploy',
    'guard:deletion']
  history: []
created: '2026-08-31'
updated: '2026-08-31'
---

# G-M3 검증 — BMAD 실제 설치와 두 런타임 discovery 관측

> 깊이 **Standard** · 단위 T1 · 모드 experiment · 의도 mixed · 영역 tooling, docs, security · 게이트 privacy-security
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

BMAD 를 격리 워크트리에 실제로 설치해, 설치기가 romeo 스킬을 지우는지·프로브가 실제 설치본에서 `present` 를 내는지·두 런타임이 `bmad-*` 를 실제로 discovery 하는지를 관측하고 그 결과를 기록한다.

## 배경과 대상

- **왜 지금:** G-M3 의 1~4단계는 닫혔다(D-77 + `feat-20260831-bmad-attach-probe-tgnb`). 라우터는 이미 11종을 추천하고 doctor 는 프로브를 인쇄한다. 그러나 그 프로브의 `present` 분기는 **marker 를 흉내 낸 테스트로만** 확인됐고, 두 런타임이 `bmad-*` 를 실제로 로드하는지는 관측된 적이 없다. 남은 것은 설치가 있어야만 관측되는 것들이고, 그것이 §6.1 5단계의 나머지 절반이다.
- **누구를 위한 것:** 이 하네스를 쓰는 사람. 지금은 라우터가 "설치돼 있지 않다" 는 사실과 함께 11종을 추천하는데, 설치했을 때 실제로 쓸 수 있는지는 아무도 확인하지 않았다.
- **성공하면 무엇이 달라지나:** 추천이 **관측에 근거하게 된다.** `capabilities.yaml` 의 `unverified:` 가 실측 기록으로 바뀌고, `.harness/observations.yaml` 에 두 런타임의 로드 관측이 남는다. 반대로 공존이 불가능하다는 결과가 나오면 그것도 근거가 된다 — 그때는 추천을 내리는 근거가 생긴다.

## 방향

- **하려는 것:** 격리 워크트리에서 `npx bmad-method install` 을 **한 번에 한 런타임씩** 실행하고, 설치 전후의 스킬 디렉터리를 해시로 대조한다. 그 뒤 프로브·doctor·두 런타임 discovery·workflow 직접 호출 시작 여부를 관측해 기록한다.
- **하지 않는 것:** BMAD 파일을 저장소에 커밋하지 않는다(`adoption: install`, `local_path: null` — D-77). workflow 를 완주시키지 않는다 — 로드되어 **시작하는지**까지만 본다. `core/` 의 규칙·템플릿·라우터 로직을 바꾸지 않는다. deferred 5종을 재검토하지 않는다.
- **전달 메시지:** 설치는 저장소 상태가 아니라 **머신 상태**다. 이 단위가 저장소에 남기는 것은 설치본이 아니라 **관측 기록**이다.

## 열린 질문

- 설치기가 저장소 밖(전역 스킬 디렉터리)에 쓰는 것이 확인되면, 워크트리 격리로는 막을 수 없다. 그 경우 관측을 계속할지 멈출지는 사람이 정한다 — 중단 조건에 넣었다.

## 실험 설계

- **가설:** BMAD 설치기는 `.claude/skills`·`.agents/skills` 에 `bmad-*` 이름으로만 **덧쓰고**, 이미 있는 romeo 스킬(claude 11종·codex 12종)을 지우거나 바꾸지 않는다. 그리고 `--directory` 로 프로젝트를 지정하면 저장소 밖에 쓰지 않는다.
- **측정 방법:**
  1. 설치 **직전**에 두 스킬 디렉터리의 모든 파일에 대해 sha256 목록을 떠 `evidence/skills-before.sha256` 에 고정한다. 홈의 전역 스킬 디렉터리 파일 목록은 `$HOME` 을 `~` 로 치환해 `evidence/home-skills-before.txt` 에 고정한다(K-23 — 사용자 경로를 그대로 남기지 않는다).
  2. `--tools codex` 로 먼저 설치한다. `.agents/skills` 가 아카이브 [E09] 가 지목한 충돌 지점이기 때문이다. 대조 → 기록 → 그 다음에 `--tools claude-code`. **한 번에 하나씩** 해야 무엇이 원인인지 말할 수 있다.
  3. 각 설치 뒤 `shasum -a 256 -c` 로 baseline 을 대조하고, 전역 목록을 다시 떠 `diff` 한다.
  4. `bin/romeo doctor` 의 「능력 프로브」 줄과 `bin/romeo compile --check` 결과를 기록한다.
  5. 두 런타임을 각각 그 워크트리에서 띄워 스킬 목록을 받아 `bmad-*` 가 있는지 본다 — `.harness/observations.yaml` 의 `runtime_load` 가 이미 쓰는 방식과 같다.
  6. CIS workflow 1종을 agent 없이 직접 호출해 **첫 단계가 시작되는지**만 본다.
- **성공 기준:** ① baseline 대조가 **전부 OK**(romeo 스킬 무손상) ② `_bmad/_config/manifest.yaml` 이 생겨 프로브가 `present` ③ `compile --check`·`doctor`·하네스 테스트가 여전히 통과 ④ 저장소 밖 전역 목록에 **변화 없음** ⑤ 두 런타임 각각의 스킬 목록에 `bmad-*` 가 나타난 것이 실행 출력으로 기록됨 ⑥ workflow 직접 호출이 시작된 것이 기록됨.
- **중단 조건:**
  - **romeo 스킬이 하나라도 사라지거나 바뀌면** 즉시 멈추고, 무엇이 어떻게 바뀌었는지 기록한 뒤 `git checkout -- .claude/skills .agents/skills` 로 되돌린다. 그 다음 설치(claude-code)는 **실행하지 않는다.**
  - **저장소 밖 전역 목록에 변화가 관측되면** 멈추고 보고한다. 워크트리 격리는 저장소 안만 막는다(`WORKTREE_ISOLATES_CODE_ONLY`).
  - `npx` 가 패키지를 받지 못하거나 Node 버전이 모자라면 멈춘다 — 설치기를 우회해 손으로 파일을 놓지 않는다(그것은 `install` 이 아니라 벤더링이고 D-77 이 고른 방식이 아니다).
  - **중단 조건이 발동해 이 관통이 실패하면 재시도하지 않는다.** 그것은 산출물 결함이 아니라 "공존한다" 는 **전제 쪽 결과**다. 같은 목표를 다시 겨눈 반복은 끝나지 않는다(AGENTS §10). 결과를 들고 사람에게 돌아온다.

## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
