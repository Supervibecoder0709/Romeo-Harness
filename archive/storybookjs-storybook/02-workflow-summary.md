# 워크플로 요약

## 1. 무엇을 하는가

Storybook은 UI 컴포넌트·페이지를 애플리케이션 전체와 분리해 개발, 문서화, 상호작용 테스트하는 개발 환경이다. 이 repository는 여러 framework/renderer/builder를 포함한 monorepo이며, core package storybook이 CLI와 개발 서버·manager·preview의 접점을 제공한다. [E01] [E03]

## 2. 입력

- 프로젝트의 .storybook/main.*: framework, builder, addons, stories 같은 main config.
- .storybook/preview.* 및 .storybook/manager.*: 각각 preview와 manager에 bundle될 설정.
- story source: *.stories.*. AST indexer가 runtime 이전에 읽는다.
- CLI option: config directory, port/host/HTTPS, output directory, preview-only, docs, test 등의 선택지.
- agent workflow에서는 target project directory/config directory, 설치된 addon, feature gate와 실행 중 dev server 상태.

## 3. 처리 단계

### 개발 모드: storybook dev

1. dispatcher가 dev를 core CLI에 보낸다.
2. CLI는 option을 검증하고, 기본 configDir인 ./.storybook와 DEVELOPMENT mode로 buildDevStandalone을 호출한다.
3. core는 main config를 읽고 framework/builder를 정한 뒤 preset을 두 차례 적용한다. 첫 번째는 builder 확인, 두 번째는 manager·preview builder와 renderer가 추가한 preset까지 반영하기 위한 것이다.
4. server는 host validation, access-control, cache middleware, index route를 붙이고 manager와 preview builder를 시작한다.
5. story index가 준비되고 listen이 성공하면 URL을 열 수 있다. configuration에 따라 component manifest 및 local MCP endpoint도 등록될 수 있다. [E05] [E06] [E07] [E08] [E09] [E15]

### 정적 생성: storybook build

1. CLI는 PRODUCTION mode와 기본 outputDir ./storybook-static을 정한다.
2. buildStaticStandalone은 빈 문자열과 root slash는 거부하지만, 그 밖의 지정 outputDir을 recursive force delete한 뒤 다시 만든다.
3. main config/preset/builder를 읽어 manager와 preview를 build한다.
4. static directory, core browser assets, index.json, project metadata, 조건부 open-service static file과 component/docs manifest를 outputDir에 쓴다.
5. preview build가 실패하면 error를 내고 exit code를 실패로 둔다. telemetry 실패는 build를 실패시키지 않도록 처리한다. [E10] [E11] [E12]

### agent instruction/tool 흐름

1. storybook skills list/get은 target project의 agent-facing instruction을 markdown으로 제공한다.
2. setup skill은 project probe만 사용하지만, stories/write-story 계열은 target Storybook config를 load하고 renderer·feature·test/docs availability에 맞춰 instruction을 조립한다.
3. storybook tools는 target configuration이 등록한 toolset을 local process에서 실행한다. experimental storybook ai passthrough는 일부 runtime command를 실행 중 dev server의 MCP로 전달할 수 있다.
4. @storybook/addon-mcp가 있으면 preset이 /mcp(기본값)를 dev server에 등록하고 docs/dev/test toolset을 feature와 addon option에 따라 선택적으로 노출한다. [E13] [E14] [E15] [E16] [E17]

## 4. 출력 또는 상태 변화

| 경로 | 관찰 가능한 출력/상태 |
| --- | --- |
| dev | listen한 local/network address, manager/preview, story index route, 선택적 manifest/MCP endpoint, runtime instance record |
| build | 지정 outputDir의 정적 사이트, index.json, project.json, static asset, 조건부 manifest/open-service 파일 |
| index | 지정 outputFile에 JSON story index |
| skills | stdout의 markdown instruction 또는 명확한 config-load 오류 |
| tools/MCP | markdown/JSON tool response, 상태 코드·MCP error content, 선택적 preview resource |

## 5. 실패·재시도

- dev: builder가 없으면 MissingBuilderError가 나며, preview build 실패 시 manager/preview와 change detection을 bail한다. port가 이미 사용 중이면 interactive 실행에서 대체 port를 물을 수 있고 CI/smoke-test에서는 그 대화 흐름이 다르다. [E08] [E09]
- build: outputDir 삭제가 build 초기에 일어난다. 따라서 build 실패 후에도 이전 산출물은 복구되지 않는다. retry 전에 outputDir이 disposable인지와 필요한 이전 artifact backup이 있는지 확인해야 한다. [E11]
- skills: 잘못된 skill ID, config load 실패는 exit code 1과 clean message로 반환한다. [E14]
- tools/MCP: 필요한 dev server가 없으면 왜 필요한지와 발견한 다른 instance를 안내한다. toolset 등록 불일치는 해당 tool을 drop하고 log를 남기되, 그 외 adapter failure는 재전파한다. [E16] [E17]

## 6. 관찰 증거

완료 판정은 명령을 실행했다는 사실이 아니라 다음을 readback해야 한다.

1. dev: 기대 project의 URL이 실제 응답하고 필요한 story/preview가 열리는지.
2. build: 예상 outputDir에 index.json·정적 파일·필요한 manifest가 생겼는지, exit code가 0인지.
3. story test: Storybook Vitest project 또는 scoped story test의 결과가 기대 범위를 통과하는지.
4. agent/MCP: skills get의 실제 instruction, tools list/response, endpoint의 인증 요구 여부와 feature gate 상태.
5. CI/release: workflow definition과 별도로 해당 SHA의 실제 run URL·결과를 확인해야 한다. 이 아카이브는 그 run을 실행하거나 조회하지 않았다.

