# 동작 요약

이 문서는 코드로 확인한 사실과 운영상 해석을 구분한다. 근거 ID는 [06-source-evidence.md](06-source-evidence.md)에 있다.

## 1. 무엇을 하는가

**확인된 사실:** CC Switch는 Claude Code, Codex 등을 포함한 여러 AI CLI/데스크톱 도구의 공급자 설정, MCP·Prompt·Skill·프로필·세션·사용량·로컬 라우팅을 한 데스크톱 UI에서 다루도록 만든 Tauri 앱이다. 가장 핵심적인 상태 변경은 앱의 로컬 설정 파일과 CC Switch의 SQLite 데이터베이스에 발생한다. [E06] [E07] [E08]

**해석:** 이것은 AI 모델을 직접 제공하는 SaaS가 아니라, 사용자의 컴퓨터에서 여러 AI 도구의 설정과 선택적 로컬 프록시를 관리하는 제어면(control plane)에 가깝다. 따라서 "공급자 전환"과 "라우팅 켜기"는 UI의 토글일 뿐 아니라 실제 로컬 상태를 바꾸는 운영 작업이다.

## 2. 입력

- 선택한 대상 앱과 공급자 데이터(식별자, endpoint·인증 등을 포함할 수 있는 `Provider`), 공급자 추가/수정/삭제/전환 요청. [E08] [E09]
- 앱별 로컬 라우팅 켜기/끄기, 프록시 포트·전역 설정, 장애 조치 큐와 circuit breaker 설정. [E10] [E11] [E15] [E16]
- Skill 리포지토리 목록, 발견된 Skill, 현재 앱, 설치·복원·활성화·저장소 이전 요청. [E17] [E18]
- 기존 `config.json`과 각 지원 앱의 라이브 설정 파일. 시작 시 DB가 없으면 이전/가져오기 후보가 될 수 있다. [E06] [E07]

## 3. 처리 단계

### A. 앱 시작과 상태 준비

1. Tauri `main()`이 Rust `run()`을 호출하고, React renderer는 backend 초기화 오류를 먼저 조회한다. [E04] [E05]
2. backend는 앱 설정 경로를 정하고 SQLite DB를 초기화한다. 새 DB에는 schema를 만들고, 기존 DB는 schema migration 전 백업을 시도한다. [E06] [E07]
3. 기존 JSON만 있고 DB가 없을 때는 JSON을 먼저 읽어 검증한 다음 DB로 이전한다. 성공한 옛 JSON은 삭제하지 않고 `config.json.migrated`로 이름을 바꾼다. [E06]
4. DB schema가 앱의 지원 버전보다 새면, schema 쓰기 전에 복구 상태를 설정하고 UI는 업그레이드 화면으로 분기한다. [E05] [E06]

### B. 일반 공급자 관리

1. 프런트엔드는 `get_providers`, `add_provider`, `update_provider`, `delete_provider`, `switch_provider`를 Tauri `invoke`로 호출한다. [E08] [E09]
2. Rust 명령은 앱 문자열을 `AppType`으로 검증하고 `ProviderService`에 위임한다. 추가에는 기본값으로 `addToLive=true`가 쓰인다. [E08]
3. **중요한 미확인:** 이번 범위에서는 `ProviderService`의 모든 앱별 writer·각 원격 endpoint 요청을 끝까지 실행하지 않았다. 따라서 특정 도구/버전에서 실제로 어느 파일의 어느 필드가 바뀌는지는 사용 전 해당 앱의 readback으로 확인해야 한다.

### C. 로컬 라우팅과 접수(takeover)

1. `ProxyService.start()`가 DB 프록시 설정을 읽어 `ProxyServer`를 시작한다. 포트가 `0`이면 OS가 정한 실제 포트를 DB에 저장한다. [E10]
2. 앱별 접수를 켤 때는 지원 여부를 검사하고, 기존 라이브 설정을 엄격하게 백업한 뒤 라이브 토큰을 DB 공급자 데이터로 동기화한다. [E11]
3. 이어서 그 앱의 라이브 설정을 로컬 프록시 대상으로 바꾸고, 완료 후 `proxy_config.enabled`를 저장한다. 중간 실패 시 이전 설정을 복구하려 하며, 복구도 실패하면 다음 시작 때 복구할 수 있도록 백업을 남긴다. [E10] [E11]
4. 프록시 server는 `/health`, `/status`, Claude Messages, Codex Chat/Responses, Gemini, Grok Build 등 경로를 handler로 라우팅한다. [E13] [E14]
5. 종료 또는 앱별 접수 해제 때는 라이브 설정을 복원하고, 성공 후 백업을 삭제한다. 백업이 없을 때 남은 프록시 placeholder를 정리하기 위한 fallback 경로도 있다. [E11] [E12]

### D. 장애 조치와 관찰

1. 장애 조치 큐는 앱별 `providers` 행의 `in_failover_queue`와 `sort_index`로 저장·정렬된다. [E16]
2. circuit breaker는 Closed/Open/HalfOpen 상태, 연속 실패/오류율/회복 대기를 관리한다. Open 상태는 대기 시간이 지나면 HalfOpen probe로 전환할 수 있다. [E15]
3. `FailoverSwitchManager`는 동일한 앱·공급자 전환의 중복을 막고, 앱이 프록시에 접수된 경우에만 hot-switch를 시도한 뒤 `provider-switched` event를 전송한다. [E15]
4. 요청 로그는 SQLite `proxy_request_logs`에 request ID, 공급자, 앱, 모델, 토큰·비용·응답 상태·오류 등을 기록하고 UI 알림 event를 낸다. [E19]

### E. Skill 관리

1. 저장된 Skill 리포지토리에서 설치 가능한 Skill을 발견하고, 선택한 앱에 설치한다. [E17]
2. 제거 전 백업 목록·복원을 위한 command가 별도로 있고, 앱별 활성화와 저장소 위치 이전도 command로 노출된다. [E17] [E18]
3. **확인된 경계:** 설치는 로컬 파일과 DB 상태를 바꾸는 작업이다. 원격 리포지토리의 신뢰성·라이선스·악성 내용 검사는 이 명령 인터페이스만으로 검증되지 않는다.

## 4. 출력과 상태 변화

| 출력/상태 | 확인된 근거 | 의미 |
| --- | --- | --- |
| `~/.cc-switch/cc-switch.db` (기본 경로) | [E07] | 공급자·프록시·Skill 등 핵심 상태가 저장되는 로컬 SQLite DB |
| 지원 앱의 라이브 설정 | [E08] [E11] | 일반 전환과 로컬 라우팅 접수 시 바뀔 수 있는 외부 경계 |
| proxy 상태와 active target | [E13] | 프록시 실행 주소·포트·UI용 현재 대상 표시 |
| 요청 로그와 `usage-log-recorded` event | [E19] | 실제 프록시가 로그를 기록한 경우의 관찰 증거 |
| 로그·crash log | [E06] | 초기화·복구 실패를 진단할 수 있는 로컬 증거 |

## 5. 실패·재시도·복구

- DB 초기화 실패는 시스템 대화상자를 통한 재시도를 제공하고, DB가 너무 새면 업그레이드 복구 화면으로 간다. [E05] [E06]
- 접수 시작 중 실패하면 원본 라이브 설정 복원을 시도한다. 복구 실패 시 백업을 보존해 다음 시작에서 회복하도록 설계했다. [E10] [E11]
- 시작 시 라이브 백업 또는 접수 흔적을 감지하면 `recover_from_crash()`를 호출한다. 이는 정상 종료가 아닌 경우의 안전장치이지만, 실제로 모든 파일 손상을 복구함은 이번 분석에서 검증하지 않았다. [E12]
- Codex 공식 인증은 갱신 토큰이 독립적으로 변할 수 있어, backup 복원이 최신 auth를 덮어쓰지 않도록 별도 처리를 시도한다. [E11]
- 공식 공급자를 proxy takeover로 쓸 때 지원되지 않는 경우 UI warning event를 낸다. 이는 차단이 아니라 경고이므로, 계정·약관·보안 책임을 자동으로 해결하지 않는다. [E11]

## 6. 관찰 가능한 완료 증거

**확인된 사실:** proxy UI 상태의 active target은 "현재 목표"이며 실제 요청을 이미 처리했다는 증명은 아니라고 코드가 명시한다. [E13]

**권장:** PM/운영 완료 기준은 다음 4개를 함께 사용한다.

1. 변경 전 설정·DB 백업의 존재를 확인한다.
2. 토글 후 `get_proxy_status` 또는 UI 상태에서 실행 주소·대상 앱을 읽어 본다.
3. 대상 CLI를 새 세션에서 한 번 실행하고, 실제 응답과 `proxy_request_logs`의 새 행을 함께 확인한다.
4. 해제 후 라이브 설정이 원래 endpoint/인증 상태로 돌아왔는지 readback한다.

이 네 단계 중 3번과 4번은 이 정적 아카이브에서 실행하지 않았으므로 **미검증**이다.
