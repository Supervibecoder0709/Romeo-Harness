---
name: write-connector
description: 새 built-in OpenWiki source connector를 추가합니다. user가 OpenWiki connector 생성 또는 구현을 요청할 때 사용합니다.
---

# OpenWiki Connector 작성

OpenWiki connector는 OSS repository의 built-in TypeScript module입니다. plugin marketplace, dynamic connector package, runtime-loaded untrusted connector를 만들지 마세요. 일반 source file과 test를 추가합니다.

## 임의 server에는 Custom MCP를 우선

knowledge source가 이미 read-only MCP server(HTTP 또는 stdio)를 제공한다면 새 ConnectorId를 추가하지 말고 built-in `custom-mcp` connector를 사용합니다.

- `~/.openwiki/connectors/custom-mcp/config.json`에 `enabled`, `transport`, optional `allowedTools`, optional `readOnlyOperations`를 구성합니다.
- secret은 `~/.openwiki/.env`에 두고 transport header/env에서는 `${ENV_NAME}`으로 참조합니다.
- agent tool `openwiki_list_mcp_tools` / `openwiki_call_mcp_tool`은 `custom-mcp`를 받습니다.

MCP가 표현할 수 없는 provider-specific auth, scoping UI, deterministic API pull이 필요할 때만 dedicated built-in connector를 추가합니다.

## 필수 형태

- connector를 `src/connectors/types.ts`, `src/connectors/registry.ts`에 추가합니다.
- `src/connectors/sources/<connector>.ts` 아래에 connector를 구현합니다.
- connector는 id, displayName, description, backend, requiredEnv, supportsAgenticDiscovery, ingest()가 있는 `ConnectorRuntime`을 노출해야 합니다.
- ingestion은 raw JSON/manifest를 `~/.openwiki/connectors/<id>/raw/<run-id>/`에 씁니다.
- state는 `~/.openwiki/connectors/<id>/state.json`에 둡니다.
- config는 `~/.openwiki/connectors/<id>/config.json`에 둡니다.
- secret은 `~/.openwiki/.env`에 두고 env var name으로만 참조합니다.

## 보안 규칙

- secret value를 읽거나 print/log/return/hardcode하지 않습니다.
- credential을 connector config, raw file, state, log, test에 저장하지 않습니다.
- connector ID와 raw file path를 검증해 read/write가 `~/.openwiki/connectors/<id>/` 안에 머물게 합니다.
- credential이 있는 external fetch에는 deterministic ingestion code를 사용합니다.
- MCP를 감쌀 때 MCP server를 read-only로 취급하고 connector config에서 allowlist된 read/dump operation만 호출합니다.
- untrusted connector manifest가 explicit built-in code review 없이 arbitrary command 또는 arbitrary network endpoint를 instantiate하게 하지 않습니다.
- `custom-mcp`에서는 user가 review된 built-in wrapper를 구성합니다. 그래도 agentic tool call에는 `allowedTools` 및/또는 MCP `readOnlyHint`가 필요합니다(Notion hosted endpoint 외에는 mutating-tool heuristic을 사용하지 않음).

## Ingestion 규칙

- Git/local repo는 compact manifest를 쓰고 agent가 local repo를 source of truth로 검사하게 합니다.
- timestamp가 있는 source는 stream별 cursor를 저장합니다.
- object metadata가 있는 source는 ID, last edited timestamp, content hash를 저장합니다.
- pagination이 있는 source는 전체를 다시 fetch하지 않고 계속할 수 있는 state를 충분히 저장합니다.
- raw dump에는 citation을 위해 source ID, timestamp, URL, author, 충분한 provenance를 보존합니다.

## User-facing 마무리

완료 시 user에게 다음을 알립니다.

- 바뀐 connector file,
- `~/.openwiki/.env`에 설정할 env var,
- 만들거나 편집할 config file,
- ingestion을 trigger할 `openwiki personal --update` 실행 방법,
- source provider에 필요한 scope/permission.
