# Agent·Skill 정의 상태

## 확인된 사실

고정 SHA의 전체 경로 인벤토리에는 `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, `.claude/agents/**`, `.claude/skills/**`, `.agents/skills/**`가 없다. 따라서 CC Switch 저장소 자체에 특정 agent의 역할·프롬프트·도구 권한을 선언한 파일은 이 분석 범위에서 발견되지 않았다. [E01]

여기서 **Skill**은 이 레포를 분석하기 위해 쓰는 Codex skill이 아니라, CC Switch 사용자가 외부 리포지토리에서 발견하여 로컬에 설치·활성화·백업·복원하는 확장 데이터다. `commands/skill.rs`는 발견, 설치, 제거, 복원, 앱별 활성화, 업데이트, 저장 위치 이동이라는 작업 인터페이스를 노출한다. [E17]

## 운영상 의미

- agent/skill 정의 파일 부재는 "AI agent 기능이 없다"는 뜻은 아니다. 이 앱은 여러 AI 클라이언트의 설정·MCP·Prompt·Skill·세션을 관리하는 UI와 backend를 구현한다. 다만 각 클라이언트의 실행 중 agent 정책은 해당 클라이언트와 사용자가 설치한 Skill에 속한다.
- Skill 설치는 외부 리포지토리 내용을 로컬 파일·DB 상태에 반영하는 쓰기 작업이다. 설치 전 원본 URL/branch/path/라이선스/내용을 검토하고, 설치 후 실제 대상 앱 디렉터리와 백업 생성 여부를 확인하는 절차가 필요하다.
- 삭제 backup command가 존재하므로 백업을 지우는 행위는 복구 지점을 없애는 별도의 비가역 작업으로 다뤄야 한다. [E17]

## 미확인

- 외부 Skill 리포지토리의 실제 다운로드 방식, 파일 검증/서명, 심사 기준, network failure 재시도 정책은 이 아카이브에서 끝까지 추적하지 않았다.
- AppType과 각 클라이언트 버전마다 실제 symlink/copy가 어떻게 적용되는지는 설치 결과 readback 없이 확정하지 않는다.
