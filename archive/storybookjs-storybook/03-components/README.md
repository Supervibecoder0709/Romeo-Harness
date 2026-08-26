# Agent·skill 및 핵심 구성요소

## 구성요소 해석

- AGENTS.md는 coding agent의 canonical instruction source이며 CLAUDE.md는 한 줄 reference다. repository 구조, renderer/builder/framework 구분, 테스트 원칙, 환경 변수와 장기 실행 명령의 금지를 정한다. 이는 plugin skill과 별개로 repository contributor를 위한 계약이다. [E02] [E03] [E04]
- Codex plugin manifest는 skills directory와 .mcp.json을 선언하고 Interactive, Write capability를 표기한다. 하지만 고정 SHA의 .mcp.json은 빈 mcpServers object다. 즉 plugin package만으로 고정된 외부 MCP server 주소가 들어 있는 것은 아니며, 실제 project의 Storybook/addon-mcp 설정이 runtime surface를 결정한다. [E20]
- addon-mcp는 dev server에 MCP handler를 붙이고 feature/toolset gate를 반영한다. 이 addon은 project에 추가되고 Storybook이 실제로 기동되어야 tool이 노출된다. [E15] [E16] [E17]

## Codex plugin skill 판단

아래는 source에 있는 원문 skill의 한국어 번역이다. 번역은 실행 승인 자체가 아니다.

| skill | 역할 | 주요 상태 변경/외부 경계 | Harness 판정 |
| --- | --- | --- | --- |
| init | Storybook 미설치 프로젝트 초기화 | package install, addon install, config 생성 | 의존성·파일 변경 전 승인 필요 |
| setup | 실제 component용 preview/story 설정 | project scan, setup command, cache/output 가능 | config/file write 전에 범위 확정 |
| stories | 모든 UI 변경 전 workflow 지시 | addon install, dev server/port, UI file write 및 test | 작업 단위·server 재사용·검증 URL 필요 |
| upgrade | Storybook upgrade | dependency/config migration | version/lockfile 변경 전 승인 필요 |

## 사실·추론·미확인

**사실**

- storybook skills는 CLI에서 target config 기반 instruction을 제공한다.
- plugin의 setup skill은 npx storybook ai setup을 명시한다.
- core CLI는 같은 ai setup path를 deprecated로 표시하고 storybook skills get setup을 권한다. [E13] [E18] [E19]

**추론**

- PM Harness에서는 plugin skill이 제안하는 install/upgrade/server start를 자동 실행하기보다, 먼저 현재 Storybook version·configDir·package manager·변경 대상 파일을 read-only로 확인하고 승인 gate를 두는 편이 적합하다. 이 결론은 skill이 실제 write/network/port action을 지시하고 build가 output directory를 삭제할 수 있기 때문이다. [E11] [E21] [E22] [E23]

**미확인**

- Codex marketplace에서 이 plugin이 현재 실제로 설치 가능한지, plugin install이 어떤 파일을 쓰는지, ADE preview가 이 SHA에서 실제 열리는지는 실행하지 않았다.

원문 위치·세부 근거는 06-source-evidence.md를 참조한다.

