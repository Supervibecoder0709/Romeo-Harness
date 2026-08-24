# 실행 핵심 구성요소

아래는 별도 skill 정의 file은 없지만 실행 경로의 중심인 구성요소다. 설명은 고정 SHA에서 읽은 코드에 한정한다.

## CLI와 runner

`src/cli/cli.tsx`는 process 시작점이다. standard command에는 환경을 읽고 startup command를 resolve한 후 auth/ngrok/cron/ingest/visualize를 runner로 넘기거나, `--print`/non-TTY에는 text run, 그 외에는 Ink `App`을 시작한다. integration과 MCP는 별도 command path다. [E02]

## Agent graph와 문서 교체

`runOpenWikiAgent`는 bundled skill, `.openwikiignore`, Claims, model, stream을 묶는다. repository `init`은 `beginRepositoryWikiReplacement`를 사용하여 성공하면 commit, 오류면 rollback을 시도한다. graph에는 connector/Claims tool, optional translation, Claims/index middleware, repository review subagent, filesystem permission이 결합된다. [E04][E05]

## Claims

Claims는 repository code wiki의 fact와 evidence resource를 runtime으로 준비하고 finalization 시 동기화한다. host lifecycle은 agent가 직접 sidecar를 수정하는 대신 inspect/resolve operation을 통해 run-scoped Claims session을 사용하도록 한다. [E05][E08]

## Connector ingestion

personal ingestion은 config에서 target source instance를 골라 순차 처리한다. deterministic connector는 raw pull을 먼저 수행하고 결과를 agent update message에 넣으며, error state는 source 단위로 반환한다. code mode connector는 run을 깨지 않도록 fail-open으로 추가 context만 제공한다. [E06][E11]

## Host lifecycle MCP

MCP server는 transport-neutral session manager의 tool을 등록한다. manager는 한 번에 하나의 mutating operation만 허용하고, begin에서 root·ignore·snapshot·Claims·docs-only backend를 준비한 뒤, finish에서 deterministic artifact/Claims/metadata를 마무리한다. [E08][E13]
