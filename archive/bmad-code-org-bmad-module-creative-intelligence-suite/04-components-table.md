# 구성요소 표

근거 상태: **확인됨**은 고정 SHA의 파일을 직접 읽어 확인한 사실, **외부 의존**은 이 repo 밖 runtime이 있어 이곳에서만 완결성을 확인할 수 없는 항목, **문서 불일치**는 문서 주장과 module source가 맞지 않는 항목이다.

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cis` | module manifest | BMad CIS 모듈 및 6 agent roster 선언 | installer의 module 선택, core config 변수, image-tool 선택 | 기본 미선택 module, `creative` team agent descriptor | 설치기·core config·Gemini Nano 연동은 외부 | `src/module.yaml` | 확인됨 / 외부 의존 [E04] |
| Carson | agent | brainstorming facilitator; `BS` 메뉴에서 `bmad-brainstorming` dispatch | 사용자 intent, merged agent config | persona 대화 또는 외부 skill dispatch | resolver, config, `bmad-brainstorming`은 이 repo 밖 | `src/skills/bmad-cis-agent-brainstorming-coach/{SKILL.md,customize.toml}` | 외부 의존 [E05] |
| Maya | agent | 인간 중심 design thinking의 입구 | 사용자 intent, merged agent config | `bmad-cis-design-thinking` dispatch | resolver와 config는 외부 | `src/skills/bmad-cis-agent-design-thinking-coach/{SKILL.md,customize.toml}` | 확인됨 / 외부 의존 [E05] |
| Victor | agent | disruption·business-model 관점의 전략 입구 | 사용자 intent, merged agent config | `bmad-cis-innovation-strategy` dispatch | resolver와 config는 외부 | `src/skills/bmad-cis-agent-innovation-strategist/{SKILL.md,customize.toml}` | 확인됨 / 외부 의존 [E05] |
| Dr. Quinn | agent | 체계적 문제 해결 입구 | 사용자 intent, merged agent config | `bmad-cis-problem-solving` dispatch | resolver와 config는 외부 | `src/skills/bmad-cis-agent-creative-problem-solver/{SKILL.md,customize.toml}` | 확인됨 / 외부 의존 [E05] |
| Sophia | agent | 내러티브 작업 입구 | 사용자 intent, merged agent config | `bmad-cis-storytelling` dispatch | resolver와 config는 외부 | `src/skills/bmad-cis-agent-storyteller/{SKILL.md,customize.toml}` | 확인됨 / 외부 의존 [E05] |
| Caravaggio | agent | presentation/visual communication coach | 사용자 intent, merged agent config | 7개 menu prompt를 직접 실행하도록 지시 | 이미지/Excalidraw 등 실제 도구 binding은 선언돼 있지 않음 | `src/skills/bmad-cis-agent-presentation-master/{SKILL.md,customize.toml}` | 확인됨 / 실행 도구 미확인 [E05] |
| Design Thinking | workflow skill | 공감~test~iteration | 과제, research `data`, methods CSV, config | `{output_folder}/design-thinking-{date}.md` | project filesystem write는 prompt 지시이며 host enforcement 미확인 | `src/skills/bmad-cis-design-thinking/` | 확인됨 / 실행 미확인 [E06] |
| Innovation Strategy | workflow skill | 시장/모델 분석과 전략 권고 | 사업 context, market `data`, frameworks CSV, config | `{output_folder}/innovation-strategy-{date}.md` | 같은 filesystem·resolver 경계 | `src/skills/bmad-cis-innovation-strategy/` | 확인됨 / 실행 미확인 [E06] |
| Problem Solving | workflow skill | root cause부터 implementation validation까지 | problem brief, methods CSV, config | `{output_folder}/problem-solution-{date}.md` | 같은 filesystem·resolver 경계 | `src/skills/bmad-cis-problem-solving/` | 확인됨 / 실행 미확인 [E06] |
| Storytelling | workflow skill | framework 기반 story development | brand/context `data`, sidecar memory, story CSV, config | `{output_folder}/story-{date}.md` | sidecar memory와 filesystem은 host 영역 | `src/skills/bmad-cis-storytelling/` | 확인됨 / 실행 미확인 [E06] |
| 방법론 CSV + template | workflow resources | 선택지와 출력 형식 제공 | workflow가 명시적으로 load | 생성 document 구조 | CSV의 방법론 품질/실제 parse 구현은 host에 의존 | 각 workflow 폴더의 `*.csv`, `template.md` | 파일 존재·참조 확인 [E06] |
| `tools/build-docs.mjs` | Node build entrypoint | docs를 LLM artifact + Astro site로 build | local `docs/`, Node env | `build/artifacts/{llms.txt,llms-full.txt}`, `build/site/` | 로컬 filesystem delete/write, `npx astro` | `tools/build-docs.mjs` | 확인됨 [E10][E11] |
| GitHub Pages workflow | CI/CD | 문서 build artifact를 Pages로 deploy | `main`의 docs/website/build file 변경 또는 수동 dispatch | GitHub Pages deployment | Pages write/id-token 권한, `SITE_URL` repo variable | `.github/workflows/docs.yaml` | 정의 확인 / 실제 실행 미확인 [E09] |
| Release workflow | CI/CD | 수동 version bump, tag, GitHub release, optional Discord message | maintainer dispatch, GitHub App and token secrets | main push, tag, release, Discord webhook POST | `contents: write`, `id-token: write`, secrets, Discord | `.github/workflows/release.yaml` | 정의 확인 / 실제 실행·secret 미확인 [E08] |
| Discord notification | CI/CD | PR/issue/comment/release/branch event 알림 | GitHub event payload, webhook secret | Discord HTTP POST (최대 title 100, body 250) | `DISCORD_WEBHOOK`, `curl`; payload body가 외부 전송됨 | `.github/workflows/discord.yaml`, helper | 정의 확인 / 수신 여부 미확인 [E16] |
| Quality workflow | CI | PR의 정적 품질 검사 | checkout, Node, npm dependency | format/lint/markdownlint 결과 | GitHub hosted runner/npm registry | `.github/workflows/quality.yaml` | 정의 확인 / workflow run 미확인 [E07] |

## 중요 차이

- `src/module-help.csv`에는 4개의 로컬 workflow와 `bmad-brainstorming`만 열거된다. Presentation은 표준 산출물 목록에 없다. [E04]
- 문서에는 Caravaggio workflow가 “coming soon”으로 적혀 있지만, 실제 agent TOML에는 7개 메뉴 prompt가 있다. 단, 이를 실제 이미지/slide 파일로 만드는 tool binding은 확인되지 않았다. [E05][E15]

