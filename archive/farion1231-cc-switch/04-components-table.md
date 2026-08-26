# 구성요소 표

근거 상태는 고정 SHA의 원문을 실제로 열어 확인했는지 표시한다. `확인`은 이 표의 역할 범위가 코드/설정/테스트에 의해 뒷받침된다는 뜻이며, 외부 서비스의 실제 실행 성공까지 뜻하지 않는다.

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태 변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `main()` → `cc_switch_lib::run()` | Rust 진입점 | OS 프로세스를 Tauri runtime으로 연결 | OS 환경변수, 실행 인자 | 앱 runtime 시작 | Linux 환경변수, 데스크톱 프로세스 | [E04] | 확인 |
| `src/main.tsx` bootstrap | React 진입점 | backend 초기화 확인 후 정상/복구 화면 렌더링 | `get_init_error`, renderer 환경 | UI 렌더, startup pricing sync 시도 | Tauri IPC, browser localStorage | [E05] | 확인 |
| `Database` | 상태 저장소 | SQLite 생성, schema migration, DB 백업/정리 | 앱 설정 경로, 기존 DB | `cc-switch.db` 및 schema 상태 | 로컬 파일 시스템·SQLite | [E07] | 확인 |
| Provider commands | Tauri command API | 공급자 list/add/update/delete/switch를 service에 위임 | 앱 ID, `Provider`, `id`, `addToLive` | 공급자/라이브 설정 변경을 service에 요청 | 로컬 DB·클라이언트 설정 파일 가능성 | [E08] [E09] | 확인; 앱별 writer 결과는 미검증 |
| `ProxyService` | backend service | server 시작/정지, 앱별 takeover backup·restore | proxy 설정, 앱 타입, enabled | server 상태, DB 플래그, 라이브 설정 변경 | 로컬 TCP, DB, 클라이언트 인증/설정 파일 | [E10] [E11] [E12] | 확인 |
| `ProxyServer` | Axum/Hyper local server | 요청 경로별 handler routing, 상태 제공 | 로컬 HTTP 요청, DB 설정 | upstream handler 실행, `/health`·`/status` | loopback TCP 및 upstream network | [E13] [E14] | 확인; upstream 호환성 미검증 |
| circuit breaker + failover switch | 복구 제어 | 실패 상태를 판단하고 중복 없는 provider hot-switch 요청 | 요청 성공/실패, 큐, app takeover 상태 | Closed/Open/HalfOpen, provider-switched event | DB, proxy, tray, frontend event | [E15] [E16] | 확인 |
| `UsageLogger` | 관찰 저장소 | 요청/실패/비용 정보를 SQLite에 기록 | request ID, provider, 모델, 토큰, 응답 상태 | `proxy_request_logs`, UI notification | DB와 frontend event | [E19] | 확인 |
| `SkillService` commands | 확장 관리 API | discovery/install/uninstall/backup/restore/update/migrate | repo, Skill, current app, backup ID | local Skill/DB 상태 | 원격 Skill repo, 로컬 파일 시스템 | [E17] [E18] | 확인; 원격 검증 정책 미확인 |
| `.github/workflows/ci.yml` | CI 계약 | TS 검사·format·unit, Rust fmt·clippy·test를 OS matrix에서 실행 | push/PR의 변경 경로 | CI check 결과 | GitHub Actions runner | [E21] | 확인; 실행 성공 여부 미확인 |
| `.github/workflows/release.yml` | 릴리스 계약 | tag push에서 multi-OS build, signing/notarization, release upload 정의 | `v*` tag, GitHub/Apple secret | release artifact 및 GitHub Release | GitHub write permission, signing secrets, Apple 서비스 | [E22] | 확인; secret 값/실제 서명 결과 미확인 |
| 자체 agent 정의 | agent/skill 정의 파일 | 별도 선언 파일을 찾지 못함 | 해당 없음 | 해당 없음 | 해당 없음 | [E01] | 확인: 부재 |
