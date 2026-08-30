# 탐색 기록

## 결론

**확인된 사실:** BMAD v6.10.0 본체는 `npx bmad-method install`로 설치되는 Node CLI이며, 내장 모듈은 `core`와 `bmm`이다. 설치 후 실제로 runtime이 읽는 단위는 `SKILL.md`이고, BMM은 분석→계획→solutioning→구현 4단계에 걸쳐 6명의 persona agent와 27개 workflow/task skill을 제공한다. [E03][E06][E07]

이 아카이브를 Romeo G-M3 router에서 쓸 때에는 “BMAD 전체”를 추천하지 말고, `04-components-table.md`의 **추천 단위=각 `SKILL.md`**를 선택해야 한다. discovery/T2에는 기본적으로 `bmad-product-brief`, `bmad-prfaq`, `bmad-domain-research`, `bmad-market-research`, `bmad-technical-research`, 필요 시 `bmad-brainstorming`/`bmad-forge-idea`를 우선 후보로 삼는 것이 파일 근거상 맞다. 이는 아래 workflow의 목적과 산출물 경로에 근거한 **추천**이며, router가 이 repo의 대화형 지시를 완전히 실행할 수 있다는 뜻은 아니다. [E07][E08]

## 탐색 범위와 선정 이유

| 범위 | 연 파일·경로 | 선정 이유 |
| --- | --- | --- |
| source identity | `README.md`, `package.json`, Git commit/tree API | npm 이름·버전·고정 SHA·tree 완전성을 확인한다. |
| module structure | `src/core-skills/module.yaml`, `module-help.csv`; `src/bmm-skills/module.yaml`, `module-help.csv` | default output roots, module purpose, agent roster, user-facing workflow catalog를 확인한다. |
| skill contract | `src/{core,bmm}-skills/**/SKILL.md` 46개와 output path를 정하는 일부 `customize.toml`/step 파일 | prompt naming이 아니라 직접 설치될 파일, interactive/headless 지시, 입출력·상태 변경을 확인한다. |
| installer/runtime | `tools/installer/{commands/install.js,core/install-paths.js,core/manifest.js,ide/platform-codes.yaml,ide/_config-driven.js}`, `test/test-installation-components.js` | 설치 명령, probe 가능한 흔적, Codex 분기 위치와 정적 test 계약을 확인한다. |
| external linkage | `bmad-modules.yaml`, `tools/installer/modules/official-modules.js`, `docs/how-to/install-bmad.md` | BMM은 built-in, CIS는 external official module이라는 차이와 선택·복사 경로를 확인한다. |
| rights/quality | `LICENSE`, `TRADEMARK.md`, `.github/workflows/quality.yaml` | license 예외와 CI 정의(실행 결과가 아님)를 분리한다. |

## 확인된 구조

```text
npx bmad-method install
  ├─ built-in: core  (13 SKILL)
  ├─ built-in: bmm   (33 SKILL = agent 6 + workflow/task 27)
  ├─ external official registry: cis, bmb, gds, tea, ...
  └─ project write
       _bmad/{_config,core,bmm,scripts,custom}/
       _bmad/_config/manifest.yaml   ← 설치 probe의 기준
       <IDE target>/bmad-*/SKILL.md  ← 예: Codex .agents/skills/
```

`core.output_folder`의 기본값은 `_bmad-output`이고, BMM의 기본 `planning_artifacts`/`implementation_artifacts`는 각각 그 아래 `planning-artifacts`/`implementation-artifacts`다. 다만 `project_knowledge` 기본값은 프로젝트의 `docs`이므로 모든 산출물이 `_bmad-output/**`에 떨어진다는 해석은 틀리다. [E06]

## 미확인 범위

- runtime별 SKILL discovery, subagent spawning, filesystem permission, user prompt UI의 실제 동작은 실행하지 않았다.
- `platform-codes.yaml`은 supported target path를 선언하고 Codex test는 setup success를 assert하지만, 그것이 각 target runtime의 의미론적 호환성·품질을 보증하지는 않는다. [E09][E10]
- CI yaml과 test source를 읽었으나 특정 workflow run/coverage/pass 결과는 확인하지 않았다.
