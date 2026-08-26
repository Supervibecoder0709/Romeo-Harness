# PM·Harness 운영 메모

## 결론

**추천:** CC Switch를 "여러 AI 클라이언트의 로컬 설정과 선택적 로컬 라우팅을 바꾸는 데스크톱 운영 도구"로 다루고, 특히 공급자 전환·라우팅 접수·Skill 설치를 각각 별도의 쓰기 작업으로 승인·검증하는 운영 모델을 쓰는 것이 맞다. UI 클릭 성공이나 active target 표시만으로 완료 처리하면 안 되며, 대상 CLI의 실제 readback과 요청 로그가 필요하다. [E08] [E11] [E13] [E19]

## 확인된 사실

- 상태의 중심은 기본 `~/.cc-switch/cc-switch.db`이며, 시작 시 기존 JSON을 조건부로 이전하고 schema migration 전 백업을 시도한다. [E06] [E07]
- 로컬 라우팅을 켜면 대상 앱 라이브 설정을 백업하고 token을 DB에 동기화한 다음, 로컬 proxy 주소를 쓰는 흐름이다. 실패 시 복구를 시도하고 실패한 backup은 다음 시작에서 복구할 수 있게 남긴다. [E10] [E11] [E12]
- proxy의 `active_targets`는 UI 표시용 "현재 목표"일 뿐 요청 처리 완료 증거가 아니다. 요청 완료의 더 강한 증거는 `proxy_request_logs`에 남는 행이다. [E13] [E19]
- 공식 공급자 중 proxy takeover 미지원 경우 warning event가 나올 수 있다. 이것은 경고이지 공급자 약관/계정 위험을 자동으로 없애는 통제가 아니다. [E11]
- Skill에는 설치, 제거, backup 복원, backup 삭제, 외부 repository discovery가 있다. [E17]

## 입력 계약과 실행 단위

| 작업 | 최소 입력 | 바뀌는 범위 | 완료 증거 | 복구 |
| --- | --- | --- | --- | --- |
| 공급자 추가/수정/전환 | 대상 앱, 정확한 provider ID/endpoint/auth 값, `addToLive` 의도 | DB 및 앱 라이브 설정 가능성 | 해당 provider가 list/current readback에 보이고 대상 CLI를 새로 열어 실제 요청 성공 | 변경 전 export/DB backup 또는 이전 provider 재전환; 실제 writer 결과는 확인 필요 |
| 앱 routing takeover | 대상 앱, proxy 실행 여부, enabled 값 | 라이브 설정, DB backup·takeover flag, 로컬 server | `/status`/UI 상태 + 새 요청의 로그 행 | takeover 해제 후 라이브 설정 readback; crash 시 자동 복구 시도 [E11] [E12] |
| 장애 조치 큐 변경 | 대상 앱, queue 순서, circuit breaker 기준 | DB의 queue/health 상태 | queue readback 및 장애 재현 시 새 provider/로그 | queue 되돌리기, circuit breaker reset |
| Skill 설치/업데이트 | 정확한 repo/branch/path, 대상 앱 | 로컬 Skill 파일, DB, 앱별 활성화 | installed 목록, 실제 target directory, 앱에서 인식 | uninstall/backup restore; backup delete 후에는 복구 범위 축소 |

## 승인 지점

1. **API key·OAuth·endpoint를 새로 저장하거나 바꾸는 순간:** 사용자·계정·목적지의 정확한 확인이 필요하다. 잘못된 endpoint는 인증 정보를 의도치 않은 곳으로 보낼 수 있다. 코드에는 URL·known secret을 로그에서 redaction하려는 구현이 있지만, 이것만으로 모든 외부 목적지 검증을 보장하지 않는다. [E06]
2. **Routing takeover:** 원래 앱의 live config와 인증 흐름을 바꾸므로, 대상 앱 하나·proxy 포트·되돌릴 방법을 명확히 한 뒤 켠다. 특히 official account warning이 나오면 약관/계정 제재 위험을 사람이 판단해야 한다. [E11]
3. **Skill 설치와 특히 backup 삭제:** 신뢰할 수 있는 리포지토리인지 검토하고, backup 삭제는 영구 복구 지점을 제거하므로 별도 명시 승인을 받는다. [E17]
4. **import/export·WebDAV/S3 sync:** command는 존재하지만 이번 분석은 구현과 실제 권한 범위를 검증하지 않았다. 운영 설계에 넣기 전에는 암호화, 충돌, 원격 overwrite, 복구 테스트를 별도 확인해야 한다. [E06]

## 관찰과 로그

- 프로세스 시작 로그는 앱 설정 경로의 `logs/cc-switch.log`에 저장하도록 구성한다. panic hook은 crash log도 설정한다. [E06]
- routing 상태에는 `/health`, `/status`와 active target이 있으나, target 표시는 의도된 다음 대상의 UI 반영일 수 있다. [E13]
- 실제 proxy 경유 여부는 request log의 신규 행, 상태 코드, provider ID, request ID로 확인한다. 같은 request ID 충돌에 대해 deterministic fallback도 구현되어 있다. [E19]
- CI 파일은 코드 품질 계약을 정의할 뿐, 현재 SHA에서 녹색이었다는 증거는 아니다. 현 시점 실행 이력은 별도 확인이 필요하다. [E21]

## 재시도·복구 설계 평가

**확인된 사실:** DB 초기화·JSON 이전에는 사용자 재시도 경로가 있으며, proxy takeover는 backup→token sync→takeover→상태 저장 순서를 갖고 실패 시 restore를 시도한다. per-app 해제는 backup→SSOT→placeholder cleanup fallback을 사용한다. [E06] [E10] [E11]

**운영상 해석:** 이 설계는 단순 파일 덮어쓰기보다 안전하지만, 백업 자체가 인증 정보를 포함할 수 있고 다른 프로그램이 라이브 설정을 동시에 바꾸면 완전한 되돌림을 보장할 수 없다. 따라서 작업 전 snapshot과 작업 후 readback을 Harness의 필수 단계로 둬야 한다.

## 추천 Harness runbook

1. **Preflight (읽기 전용):** 로그인/대상 앱/현재 provider/현재 proxy 상태/기존 config와 backup 존재 여부를 수집한다. 값은 secret을 마스킹해 기록한다.
2. **Approval gate:** "어느 앱의 어떤 provider 또는 routing flag를 바꾸며, 어떤 파일/DB가 영향권이고, 무엇으로 되돌릴지"를 사람이 승인한다.
3. **단일 쓰기:** 한 번에는 한 앱만 변경한다. provider와 proxy takeover를 한 단계에서 동시에 대량 전환하지 않는다.
4. **Readback:** command 결과뿐 아니라 DB/UI 상태, 라이브 설정의 예상 endpoint, 대상 CLI 새 세션을 확인한다.
5. **실사용 검증:** 민감하지 않은 최소 prompt 하나를 보내고, proxy request log에 해당 시간·provider·상태가 남았는지 확인한다.
6. **Rollback gate:** 기대와 다르면 추가 변경 없이 takeover 해제/이전 provider 복귀/backup restore를 수행하고, 그 결과도 readback한다.

## 추천이 달라지는 조건

- 단순히 한 CLI의 설정을 바꾸고 사용량 집계·즉시 전환·장애 조치가 필요 없다면, 로컬 routing을 켜지 않는 편이 운영·보안 표면이 작다.
- 사용량 관찰, hot switch, failover가 필요할 때만 routing을 켜되, provider별 약관과 local proxy에 저장되는 인증 경계를 먼저 검토해야 한다.
- 팀 공유/자동화가 목표라면 CC Switch의 수동 UI만을 원장으로 삼기보다, 승인·감사·secret 관리가 가능한 별도 source of truth와 정해진 export/import 절차를 설계하는 편이 낫다. 이는 **추천**이며 현재 코드가 제공한다고 확인한 기능은 아니다.
