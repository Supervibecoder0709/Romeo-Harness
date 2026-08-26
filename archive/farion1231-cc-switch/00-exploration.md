# 탐색 기록

## 범위

고정 SHA `5ca9459d50ea4beea6a81bbc509de6ec5b6b09ca`의 blob 경로 1,230개를 인벤토리했다. 대형 Rust·TypeScript 데스크톱 애플리케이션이므로, 문서 제목만 근거로 삼지 않고 아래의 시작점·상태 저장소·로컬 프록시·명령 경계·테스트/CI를 열었다. 근거 ID는 [06-source-evidence.md](06-source-evidence.md)에서 확인한다.

## 실제로 연 파일과 선정 이유

| 파일 | 선정 이유 |
| --- | --- |
| `package.json`, `src-tauri/Cargo.toml`, `src-tauri/tauri.conf.json` | 개발/빌드 스크립트, 프런트엔드·Tauri·Rust 의존성, CSP·updater·번들 계약 확인 |
| `src-tauri/src/main.rs`, `src-tauri/src/lib.rs`, `src/main.tsx`, `src/App.tsx` | 데스크톱 프로세스와 React 화면의 실제 시작점 및 초기화 흐름 확인 |
| `src-tauri/src/config.rs`, `src-tauri/src/database/mod.rs` | 로컬 설정 경로, 원자적 쓰기, SQLite 초기화·마이그레이션·백업 경계 확인 |
| `src-tauri/src/commands/provider.rs`, `src/lib/api/providers.ts` | UI의 공급자 추가·수정·삭제·전환 요청이 어떤 Tauri 명령으로 이어지는지 확인 |
| `src-tauri/src/services/proxy.rs`, `src-tauri/src/proxy/server.rs`, `src-tauri/src/proxy/circuit_breaker.rs`, `src-tauri/src/proxy/failover_switch.rs`, `src-tauri/src/database/dao/failover.rs`, `src-tauri/src/proxy/usage/logger.rs` | 로컬 라우팅, 라이브 설정 접수(takeover), 복구, 장애 조치, 요청 로그의 실제 상태 변경 확인 |
| `src-tauri/src/commands/skill.rs`, `src-tauri/src/app_config.rs` | Skill 발견·설치·복원·저장소 이동과 앱별 활성화 계약 확인 |
| `tests/components/ProxyToggle.test.tsx`, `.github/workflows/ci.yml`, `.github/workflows/release.yml` | 프런트엔드 검증 예시, CI가 실제로 실행하도록 정의한 검사, 태그 기반 릴리스/서명 경계 확인 |
| `docs/user-manual/en/1-getting-started/1.4-quickstart.md`, `4-proxy/4.2-routing.md`, `4-proxy/4.3-failover.md` | 사용·운영 절차의 원문 번역 대상. 코드 근거와 충돌하지 않는 범위에서 별도 번역함 |

## 확인된 진입점과 기술 스택

- `pnpm tauri dev`와 `pnpm tauri build`가 개발·빌드 진입점이다. Tauri 설정은 Vite renderer를 개발 시 실행하고 build 시 `dist`를 사용한다. [E02] [E03]
- OS 프로세스는 `src-tauri/src/main.rs`의 `main()`에서 시작해 `cc_switch_lib::run()`을 호출한다. Rust 라이브러리는 Tauri 플러그인, SQLite 상태, 명령 handler를 설정한다. [E04] [E06]
- 화면은 `src/main.tsx`가 React 앱을 렌더링한다. 시작 전에 backend 초기화 오류를 조회하고, DB 버전이 앱보다 새 경우 정상 화면 대신 업그레이드 복구 화면을 렌더링한다. [E05]
- 프런트엔드는 React/TypeScript/Vite, backend는 Tauri 2/Rust, 상태 저장은 SQLite(`rusqlite`), 로컬 라우팅은 Axum·Hyper·Tokio 기반이다. 이는 manifest와 구현을 함께 연 결과다. [E02] [E03] [E07] [E13]

## 확인된 핵심 흐름

1. React 화면이 Tauri `invoke`로 명령을 호출하고, 공급자 명령은 `ProviderService`로 위임한다. [E05] [E08] [E09]
2. 앱 시작 시 `.cc-switch/cc-switch.db`를 열고 schema migration, 기존 JSON의 조건부 이전, 기본 Skill/공식 공급자 초기화를 수행한다. DB가 지원 버전보다 새면 쓰기 전에 복구 상태로 전환한다. [E06] [E07]
3. 로컬 라우팅은 `ProxyService`가 server를 만들고, Axum router가 Claude·Codex·Gemini·Grok Build 관련 경로를 handler로 연결한다. 앱별 접수를 켜면 원본 라이브 설정을 백업하고 토큰을 DB에 동기화한 뒤 로컬 프록시 주소로 바꾼다. [E10] [E11] [E13] [E14]
4. 장애 조치는 앱별 DB 큐와 circuit breaker를 이용한다. 전환은 중복 실행을 막고, 프록시가 실제 접수된 경우에만 hot-switch와 UI event를 요청한다. [E15] [E16]
5. Skill은 agent 정의가 아니라 사용자가 설치·동기화하는 확장 데이터다. 리포지토리에서 발견하고, 설치·제거·백업복원·업데이트·저장 위치 이동을 Tauri 명령으로 노출한다. [E17] [E18]

## 미확인 범위

- 인벤토리에 `.claude/agents/**`, `.claude/skills/**`, `.agents/skills/**`, `AGENTS.md`, `CLAUDE.md`, `SKILL.md`는 없었다. 따라서 이 레포가 자체 agent/skill 정의를 제공한다는 주장은 할 수 없다. [E01]
- 실제 GitHub Actions의 성공/실패, 릴리스 파일의 실제 서명·공증, updater 서버 가용성, 모든 외부 provider의 인증 방식과 약관 준수는 확인하지 않았다.
- 전체 handler·adapter·외부 API와 모든 1,230개 파일을 실행하거나 전수 검토하지 않았다. 특히 프록시가 특정 벤더의 최신 프로토콜과 항상 호환된다는 보장은 이 아카이브 범위 밖이다.
