# 동작 요약

## 1. 설치와 관찰 가능한 흔적

**무엇을 하는가:** `bmad-method` npm CLI가 core/BMM을 포함한 선택 모듈을 프로젝트에 복사하고 IDE별 skill directory에 SKILL directory를 배치한다. 새 비대화형 설치에는 `--tools`가 요구되고, `--modules`는 유지할 정확한 module set이며 core는 자동 추가된다. [E03][E04]

| 단계 | 입력 | 처리 | 출력/상태 | 실패·재시도 | 관찰 증거 |
| --- | --- | --- | --- | --- | --- |
| install | `npx bmad-method install`, directory/modules/tools/config | installer가 프로젝트 root와 writable `_bmad` dirs를 준비하고 module copy 및 IDE setup | `_bmad/{core,bmm,...}`, `_bmad/_config/manifest.yaml`, config·script·custom dirs | permission/파일 유형 문제는 error; existing install은 update flow | `_bmad/_config/manifest.yaml` 존재, 선택 module dirs, `skill-manifest.csv` [E04][E05] |
| Codex integration | `--tools codex` | config-driven handler가 canonical skill directory를 설치 | 프로젝트 `.agents/skills/<skill>/SKILL.md`; global target은 `~/.codex/skills` | setup failure면 target을 claim하지 않아 다음 peer가 시도 가능 | `.agents/skills`에 BMAD-owned SKILL directories; test has Codex setup assertion [E09][E10] |
| config override | `--set module.key=value` | normal install 뒤 team/user TOML 및 module config patch | `_bmad/config.toml` 또는 `config.user.toml`, `_bmad/<module>/config.yaml` | schema 밖 key는 다음 install에 보존되지 않을 수 있음 | manifest/config readback [E03] |

설치는 프로젝트 파일을 쓰는 작업이다. G-M3의 “설치 여부 probe”는 **`_bmad/_config/manifest.yaml`의 존재와 기록된 module/IDE**를 먼저 보고, 필요한 경우 선택 runtime의 `.agents/skills/`까지 확인하는 편이 안전하다. 단, 존재 probe는 workflow 실행·완료 증거가 아니다.

## 2. BMM lifecycle

| 흐름 | 입력 | 처리 단계 | 출력/상태 | 대화형 여부 | 관찰 증거 |
| --- | --- | --- | --- | --- | --- |
| Analysis | idea, existing project, research topic | brainstorm/idea 검증, research, brief 또는 PRFAQ, brownfield documentation | 기본 `{planning_artifacts}` 또는 `{project_knowledge}`의 research/brief/PRFAQ | 대부분 대화형; PRFAQ는 `-H` headless가 명시됨 | 파일 생성·frontmatter·`.memlog.md` [E07][E08] |
| Planning | product intent, prior brief/research | PRD create/update/validate, UX contract create/update/validate | PRD/UX run folders, review files | PRD/UX는 headless path와 interactive path 모두 명시 | `prd.md`, `DESIGN.md`, `EXPERIENCE.md`, `.memlog.md` [E11] |
| Solutioning | PRD/UX/spec/codebase | architecture spine, epics/stories, readiness gate, project context | architecture run folder, `epics.md`, readiness report, project-context | gate/epic workflow는 메뉴에서 멈추는 대화형; architecture는 headless path 있음 | final report/frontmatter, output files [E12] |
| Implementation | stories, code, sprint status | sprint plan, story prep/dev/review/test, correction, retro | code/tests + implementation artifacts + `sprint-status.yaml` | Dev Auto만 무인 iteration, 나머지는 사람 checkpoint가 기본 | story status, review findings, test summary, retro [E13] |

## 3. Core cross-cutting skills

Core의 `bmad-help`, `bmad-party-mode`, `bmad-advanced-elicitation`, `bmad-spec` 등은 BMM workflow에 종속되지 않고 BMM 또는 외부 module과 함께 쓰인다. 그중 `bmad-spec`은 `{output_folder}/specs/spec-{slug}/`에 `SPEC.md`·companion·`.memlog.md`를 두는 명시적 계약을 가진다. `bmad-party-mode`는 기본 대화형이며 `--non-interactive`일 때만 자연 종료까지 자동 진행하도록 지시한다. [E14]

## 4. 실패·재시도와 경계

- workflow의 “완료”는 LLM 지시 속의 파일 저장/상태 변경이며, 이 아카이브는 실제 파일 생성이나 테스트 실행을 관찰하지 않았다.
- 일부 workflow는 source 파일에서 사용자 메뉴 선택을 기다리도록 강제한다. 따라서 G-M3가 이것을 무인 task로 추천하면 router가 입력 contract·write authority·멈춤 정책을 별도로 감싸야 한다. [E12][E13]
- external handoff/MCP, web research, subagent, git commit/push 제안은 skill별로 선택적이거나 runtime 의존이다. 설치된 SKILL 파일의 존재만으로 그러한 권한이 생기지 않는다.
