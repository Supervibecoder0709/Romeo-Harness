# 실행 핵심 구성요소

## Tauri desktop host

`src-tauri/src/main.rs`는 OS별 Linux 환경 보정을 한 뒤 `cc_switch_lib::run()`을 호출한다. `lib.rs`는 single-instance, deep link, dialog, opener, store, window state, updater, tray, 로그, 앱 상태를 조립하고 Tauri command handler를 등록한다. [E04] [E06]

## React renderer

`src/main.tsx`는 backend 초기화 오류를 먼저 읽고 정상 앱 또는 DB 업그레이드 복구 화면을 렌더링한다. `App.tsx`는 선택 앱·화면·공급자·proxy 상태·Skill 화면 등을 관리하고 `@tauri-apps/api`로 backend 명령을 호출한다. [E05] [E09]

## SQLite와 라이브 설정 경계

`Database::init()`은 기본적으로 `~/.cc-switch/cc-switch.db`를 열고 schema migration과 일부 보수 작업을 수행한다. `config.rs`에는 JSON·텍스트 원자적 쓰기 함수가 있어, 외부 클라이언트의 설정 파일 수정이 필요한 서비스가 이를 사용할 수 있는 공통 경계를 제공한다. [E07] [E20]

## 공급자·로컬 프록시·장애 조치

공급자 명령은 list/add/update/delete/switch 인터페이스를 `ProviderService`로 전달한다. `ProxyService`는 로컬 server 생명주기와 라이브 설정 backup/takeover/restore를 책임지고, Axum 기반 `ProxyServer`는 요청 종류별 handler와 공유 provider router·circuit breaker·failover manager를 구성한다. [E08] [E10] [E11] [E13]

## Skill 관리

`SkillService` 명령은 DB의 Skill repository 목록을 입력으로 발견, 설치, 제거, 백업복원, 활성화, 업데이트, 저장소 이전을 수행한다. `InstalledSkill`은 앱별 활성화 상태와 원격 리포지토리 메타데이터·콘텐츠 hash 필드를 가진다. [E17] [E18]
