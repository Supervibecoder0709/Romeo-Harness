# PM Harness 운영 메모

## 추천

Storybook은 UI 작업 agent의 최종 산출물 자체가 아니라, 변경 전후 UI를 검증하고 사람에게 보여 주는 project-local evidence surface로 쓰는 것이 가장 적합하다. 즉 agent가 component·story·test를 바꾸기 전에 현재 Storybook config와 실행 중 instance를 read-only로 확인하고, 변경은 작은 작업 단위로 승인하며, 결과는 실제 preview URL·story test·정적 build readback으로 판정하는 구조를 권장한다.

이 추천은 Storybook이 code generation 도구라서가 아니라, 실제로 dev/build/tool/MCP 경로가 config, filesystem, port, package install, remote composition에 닿기 때문이다. 특히 build는 output directory를 지우고, init/upgrade는 dependency와 config를 바꾸며, MCP는 deployment 여부와 무관하게 agent에게 도구 표면을 열 수 있다. [E05] [E11] [E15] [E21] [E24]

## 확인된 사실

### 입력 계약

- UI 작업에는 target package의 working directory, configDir, 대상 component/story, 허용된 수정 파일, 원하는 검증 기준이 있어야 한다.
- dev는 port/host/HTTPS/configDir/preview-only 같은 CLI option을 받고, build는 outputDir을 받는다. configDir 기본값은 ./.storybook, build outputDir 기본값은 ./storybook-static이다. [E06] [E07] [E10]
- skills get은 대상 config를 실제로 load할 수 있어야 하며, setup을 제외한 skill은 해당 config의 availability에 맞춰 instruction을 조립한다. [E13] [E14]

### 모델·agent 역할

- Storybook 자체 source에는 특정 LLM 모델을 선택·권한부여하는 orchestrator가 없다. Codex plugin은 skill metadata와 prompt instruction bundle이다.
- core의 skills/tools/AI CLI와 addon-mcp가 agent-facing surface를 제공하지만, 어떤 tool을 보이는지는 target Storybook의 addon, builder, feature, 실행 중 server 상태에 따라 달라진다. [E14] [E15] [E16] [E20]

### 실행 단위와 완료 증거

- 작은 실행 단위 권장: 한 component 또는 한 user-visible state + 그 component의 story + 좁은 test/preview.
- dev 완료 증거: URL이 응답하는지, target story가 실제 표시되는지, manager/preview가 기대 config를 썼는지.
- build 완료 증거: exit code 0만으로 충분하지 않다. 지정 outputDir에서 index.json, 필요 static assets, 필요한 경우 manifest가 readback되어야 한다. [E09] [E12] [E30]
- component behavior test는 Storybook Vitest project가 Chromium browser를 쓰도록 설정되어 있지만, config만 읽었으므로 이번 SHA에서 실제 test pass를 뜻하지 않는다. [E25]

## 승인 지점

| 상황 | 왜 승인이 필요한가 | 안전한 사전 확인 | 실행 뒤 readback |
| --- | --- | --- | --- |
| init / addon install | dependency, lockfile, .storybook config를 바꿀 수 있음 | package manager, 현재 Storybook 유무, 예상 변경 파일 | package.json/lockfile/config diff, 설치된 addon |
| upgrade | version migration과 config transformation 가능 | 현재 version, migration guide, compatibility, rollback ref | diff, compile/test, target UI preview |
| dev server 시작 | local port를 점유하고 browser를 열 수 있음 | 기존 instance, package root, requested port/host | URL 응답, PID/port, target story URL |
| static build | outputDir을 recursive delete한 뒤 파일을 씀 | 절대 outputDir, disposable 여부, backup/restore 경로 | output tree/index.json/manifest와 exit code |
| remote MCP composition / auth | remote ref fetch와 Bearer/OAuth flow가 발생할 수 있음 | origin/endpoint/remote source와 credential owner | authenticated/unauthenticated response와 exposed tool list |
| release workflow | npm publish, GitHub write, external deployment registration 및 notification을 수행 | exact release branch/version/change log/approver | release URL, npm version, merge and deployment readback |

release는 repository의 GitHub Actions definition 안에 존재하지만 이 분석 작업의 권한·범위에는 전혀 포함되지 않는다. publish workflow가 normal release job에서 contents, pull-requests, actions, id-token write permission을 요구하고 npm publish/remote POST/GitHub release를 수행하도록 정의한 사실만 확인했다. [E29]

## 재시도와 복구

- dev: 먼저 기존 project instance를 찾고 재사용한다. 새 server를 시작했으면 URL·port를 기록한다. 오류가 나면 raw stack 대신 configDir, builder, feature gate, server log를 증거로 남긴다.
- build: retry 전에 outputDir을 새 artifact directory로 바꾸거나 기존 output을 백업한다. source는 빈 string과 root slash만 직접 거부하므로, 사람이 path를 보고 승인하지 않으면 안전하다고 볼 수 없다. [E11]
- tools/MCP: config load failure, unknown skill/tool, dev server 미실행은 다른 failure class다. tool이 requires-dev-server를 반환하면 무작정 재시도하지 말고 current project에 맞는 instance를 확인한다. [E14] [E16]
- CI: workflow YAML은 가능성만 보여 준다. run URL, commit SHA, 결과, 제외된 test를 readback하지 않으면 완료로 표시하지 않는다. Nx GitHub workflow는 고정 SHA에서 workflow_dispatch만 trigger로 두고 있다. [E27]

## 관찰·로그

- CLI는 debug/logfile option을 제공하고, command failure 때 debug log를 file로 쓸 수 있다. log file path는 local write이므로 target path를 명시해야 한다. [E06]
- dev는 성공 뒤 runtime instance record 쓰기를 시도하지만 실패를 warning으로 처리한다. 이 record의 존재만으로 UI 검증 완료를 뜻하지 않는다. [E08]
- MCP tool response는 structured content 또는 text/error를 줄 수 있다. tool availability와 실제 response를 함께 보존해야 한다. [E16] [E17]

## 확장 지점

- framework/builder/addon은 preset hook으로 확장되고, open services/toolsets는 같은 services preset hook과 feature gate 뒤에 등록하도록 agent guide가 요구한다. [E04] [E08]
- addon-mcp는 dev/docs/test toolset, component manifest, change detection, review availability를 각각 gate한다. 따라서 새로운 agent tool을 추가할 때 “도구를 등록했다”와 “모든 framework에서 사용 가능하다”를 분리해야 한다. [E15] [E16]

## 추천: Harness policy

1. 탐색 단계는 read-only: package.json, .storybook, existing dev server, target story, current Git diff를 먼저 읽는다.
2. 계획은 명시적: 바꿀 파일, 필요 설치, port, outputDir, 검증 method를 한 작업 카드에 고정한다.
3. write gate: init/addon/upgrade/config edit/build output delete/remote auth/release는 사람의 현재 승인 뒤에만 실행한다.
4. 검증 gate: component story URL, scoped interaction/a11y test, output artifact readback 중 작업에 맞는 최소 세트를 만족해야 완료로 표시한다.
5. 외부 상태: CI, MCP remote source, marketplace installation, release는 source code의 의도와 실제 live result를 절대 혼동하지 않는다.

## 미확인

- Codex plugin의 실제 installation location/permission prompt, marketplace availability, execution side effects.
- Storybook runtime instance registry의 retention/cleanup policy.
- target project별 MCP authentication configuration, remote source allowlist, browser exposure.
- CircleCI의 generated config와 현재 pipeline 결과, NX Cloud/remote cache의 실제 health.

