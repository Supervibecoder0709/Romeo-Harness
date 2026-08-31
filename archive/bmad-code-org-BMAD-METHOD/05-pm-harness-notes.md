# PM / Harness 채택 메모

## 추천: G-M3는 “BMAD를 설치하라”가 아니라, discovery/T2에서 특정 SKILL을 추천하라

**추천:** Romeo router의 G-M3 discovery/T2 판정에는 아래 순서로 `SKILL.md`를 권한다.

1. **기본:** `bmad-product-brief` — 아이디어·문제·가설을 product brief로 대화형 정리한다. 출력은 재사용 가능한 run folder다.
2. **강한 반증 필요:** `bmad-prfaq` — customer/problem/stakes/solution을 필수 입력으로 받고, 기본 coaching 또는 `-H` first-draft 모드를 가진다.
3. **근거 부족:** `bmad-domain-research`, `bmad-market-research`, `bmad-technical-research` — 각각 고정된 research filename을 만든다.
4. **발산/숙성 보조:** `bmad-brainstorming` 또는 `bmad-forge-idea` — 전자는 아이디어 발산, 후자는 “harden/prove/die cheaply” 판단에 맞는다.

이것은 **추론/추천**이다. 원문은 SKILL별 prompt와 output 계약을 제공하지만, Romeo가 이 workflow의 web research, subagent, filesystem write, stop-at-menu를 동일하게 집행한다는 실행 증거는 없다. [E07][E08][E14]

## 채택 gate: router가 먼저 확인할 것

| gate | 확인된 사실 | PM 판단/권장 처리 |
| --- | --- | --- |
| 설치 probe | installer는 `_bmad/_config/manifest.yaml`을 만들고 module·IDE 정보를 기록한다. | 해당 파일이 없으면 “설치되지 않음”, 있으면 “설치 흔적 확인”까지만 말한다. workflow가 실행되었다고 승격하지 않는다. [E04][E05] |
| BMM presence | manifest와 `_bmad/bmm/`, selected IDE skill dir가 실제 install output이다. | G-M3 router는 `bmad-product-brief`의 actual `SKILL.md`가 selected runtime target에 있는지도 별도 probe할 수 있다. |
| output root | BMM 기본 planning/implementation root는 `_bmad-output/**`이나 project knowledge 기본값은 `docs`. | 모든 artifact가 `_bmad-output`에 있다고 hard-code하지 않는다. `project_knowledge` workflow는 `docs/**`를 우선 본다. [E06] |
| interactive guard | PRD/UX/architecture는 interactive/headless 양 경로가 있고, epics/readiness와 여러 implementation workflow는 menu에서 멈춘다. | human-in-loop workflow를 무인 job으로 dispatch하지 않는다. headless가 명시된 skill만 automation 후보로 좁힌다. [E11][E12][E13] |
| write risk | install, customize, shard-doc, dev/quick-dev/code-review 등은 project files를 변경한다. shard-doc에는 source delete/move choice, quick-dev present step에는 local commit branch가 있다. | router는 task contract에 write scope, git/commit prohibition, human approval point를 넣는다. [E13][E14] |
| completion evidence | source에는 output file write 지시가 있다. | gate 통과 기준은 실행 후 해당 artifact/readback(예: PRFAQ path, `SPEC.md`, report, `sprint-status.yaml`)이지 assistant의 완료 문구가 아니다. |

## 설치와 runtime 지원의 정확한 해석

### 확인된 사실

- 본체 자체는 npm package `bmad-method` v6.10.0이며 bin은 `tools/installer/bmad-cli.js`다. Node engine은 `>=20.12.0`이다. [E03]
- `--tools`는 CLI option이고 `platform-codes.yaml`이 platform별 target directory를 선언한다. `codex`는 preferred platform으로 선언되어 project target `.agents/skills`, global target `~/.codex/skills`를 갖는다. Claude Code는 `.claude/skills`, Cursor는 `.agents/skills`다. [E04][E09]
- config-driven installer는 `skill-manifest`의 canonical skill directory를 해당 target에 배치한다. Codex setup test는 `ideManager.setup('codex', ...)` success를 assert한다. [E09][E10]

### 해석 시 주의

- **“Claude만 지원한다”는 결론은 이 SHA에서 틀리다.** Codex entry와 setup test가 있다.
- 반대로 **“Codex가 모든 BMAD 능력을 보장한다”도 틀리다.** 확인된 것은 path-based skill installation과 installer test뿐이다. Agent team은 party-mode 설명상 Claude Code-only이며, subagent·interactive prompt·web/MCP 권한은 runtime마다 별도 capability다. [E09][E14]
- 따라서 G-M3는 runtime을 `claude-code`/`codex`처럼 installer platform code로 취급하고, skill semantics compatibility는 capability gate에서 재확인해야 한다.

## CIS와 본체의 결합

### 확인된 사실

- 본체 registry에서 `cis`는 `bmad-module-creative-intelligence-suite` URL, `src/module.yaml`, npm package, stable default channel을 가진 **external official module**이다. BMM은 source package에 포함된 built-in module이다. [E16][E17]
- `--modules` 문서는 “exact module set이며 core는 자동 추가”라고 명시한다. BMM을 입력하지 않고 CIS를 선택하는 설치 경로는 문서/registry 구조상 가능하며, 그런 설치에도 core는 포함된다. [E04][E17]
- 이미 아카이브된 CIS source에는 own agent/workflow SKILL이 있으나 activation/resolver와 `bmad-brainstorming` 같은 core skill에 연결되는 지시가 있다. 이는 CIS가 BMM 본체 없이도 **core host를 전제로** 한다는 근거다. [E18]

### 결론

`CIS만 설치`를 “BMM lifecycle module은 빼고 **core + CIS**만 선택”이라는 뜻으로는 가능하다고 판단한다. 그러나 “BMAD host 없이 CIS repo만 folder에 놓으면 독립 실행된다”는 뜻으로는 확인되지 않았고, CIS archive도 그 runtime을 보유하지 않는다고 기록한다. CIS-only install을 G-M3에서 권하려면 manifest에 `core,cis`가 실제 기록되었는지와 runtime skill target에 CIS SKILL이 있는지를 readback해야 한다.

## 라이선스와 재배포 boundary

**확인된 사실:** root code license와 package license는 MIT이며 tree에서 별도 `LICENSE`/`COPYING`/`NOTICE` path는 찾지 못했다. 단, `TRADEMARK.md`는 BMad/BMad Method/BMad Core 이름·로고·tagline이 MIT로 license되지 않는다고 명시한다. [E03][E19]

**권장:** Harness documentation은 “BMad-compatible” 같은 정확한 호환성 표현은 가능하더라도, 새 product/feature 이름, 도메인, logo/branding에 BMad을 쓰지 않는다. 이는 법률 자문이 아니라 source에 적힌 license/trademark boundary를 운영 규칙으로 옮긴 것이다.

## 미확인·제외

- npm install/upgrade/uninstall의 실제 filesystem diff, external CIS download, Codex/Claude actual discovery, CI pass, security/privacy of external integrations는 실행하지 않았다.
- existing install에서 module selection이 deselected module을 제거할 수 있는 code path가 있으므로, 실운영 업데이트는 target/backup/readback/승인이 필요한 write operation이다. 이 아카이브는 그러한 실행을 하지 않았다.
