# PM Harness 운영 메모

## 결론

**추천:** OpenWiki를 Harness에 넣을 때는 `호스트 에이전트가 조사·저작`, `OpenWiki lifecycle이 준비·Claims·완료`를 맡는 현재 분리를 유지하고, `begin` 전과 `finish` 전을 사람 승인 지점으로 둔다. 이유는 이 통합이 단순 문서 생성기가 아니라 repo `openwiki/`, Claims, metadata, managed instruction block, 그리고 init 시 workflow까지 바꿀 수 있는 실행 단위이기 때문이다. [E07][E08][E11]

이는 기능 채택 결정을 뜻하지 않으며, 고정 SHA의 설계에 맞춘 운영 통제 추천이다.

## 확인된 사실

### 입력 계약과 역할 분리

- host integration은 절대 Git top-level을 resolve한 뒤 `openwiki_begin(root, mode)`를 호출하고, 반환된 `runId`를 Claim inspection·mutation·finish에 전달하도록 정의한다. 상대 경로나 추정 root를 사용하면 안 된다. [E07][E08]
- host는 repository 조사, 계획, factual Markdown 저작을 native tool로 한다. OpenWiki는 deterministic setup, index/provenance/metadata/managed setup file finalization을 소유한다. 따라서 `openwiki/.claims`나 generated index·log·workflow를 host가 직접 고치는 계약은 아니다. [E07]
- MCP lifecycle 도구 수는 네 개이며, code의 protocol test도 정확히 네 개의 이름과 strict input validation을 확인한다. [E08][E19]

### 상태·복구 모델

- init은 기존 위키를 즉시 파괴하는 단일 write가 아니라 replacement를 시작하고, 성공 시 commit, 실패 시 rollback을 시도한다. rollback 실패는 이전 위키가 완전히 복구되지 않았을 수 있다는 오류로 올린다. [E04]
- host lifecycle의 `begin`은 준비 중 상태를 `interrupted`로 기록한다. `finish`는 finalization pre-commit 실패 시 session을 유지하므로 재시도 가능하며, 성공했을 때만 `complete` metadata와 finish status를 반환한다. [E08]
- code-mode update는 이전 run이 interrupted이면 no-op으로 건너뛰지 않도록 테스트돼 있다. 반대로 source 변경이 없고 조건이 맞으면 update를 skip할 수 있다. [E04][E10]

### 외부 경계와 비용·보안 영향

- 일반 code run은 선택한 model provider와 로컬 credential을 사용한다. ChatGPT login/OAuth token 및 다른 provider key의 실제 저장·회전은 이 작업에서 실행 검증하지 않았지만, README는 `~/.openwiki/.env`을 로컬 상태 경로로 설명한다. [E20]
- personal ingestion은 connector API/raw data/로컬 wiki 경계를 가진다. deterministic pull은 먼저 raw file을 쓰고 agent update가 뒤따른다. connector 결과를 그대로 지시로 따르지 말라는 메시지가 코드에 있다. [E06]
- 생성되는 schedule 예시는 `contents: write`와 `pull-requests: write`로 문서 PR을 만들 수 있다. 이 권한은 읽기 전용 조사가 아니며, 배포 권한과는 구분해 검토해야 한다. [E16]
- 공식 release workflow는 upstream 또는 명시 opt-in fork에서 contents/PR/id-token write로 version PR, tag, npm publish 경로를 열 수 있다. 일반 아카이브/문서 운영과 분리해 보호할 경계다. [E18]

## 권장 운영 설계

### 승인 지점

1. **`begin` 전 승인:** 정확한 repository root, `init` 대 `update`, 예상 변경 영역(`openwiki/`, root agent block, init이면 workflow)을 사람이 확인한다. `init`은 위키 교체를 시작하므로 update와 같은 무위험 명령으로 취급하면 안 된다.
2. **외부 연결 전 승인:** provider credential, OAuth, personal connector, LangSmith 같은 외부 데이터 연결은 API 비용·데이터 범위를 바꾸므로 source 종류·scope·보존 위치를 확정한다. README의 connector 목록만으로 실제 권한이 안전하다고 간주하지 않는다.
3. **`finish` 전 승인:** host가 만든 Markdown diff, unresolved/stale Claim, `.openwikiignore` 적용 수, 그리고 generated workflow가 있으면 그 권한을 읽고 승인한다. `finish`가 index/Claims/metadata를 확정하므로, 이 시점이 최종 write gate에 적합하다.
4. **schedule/PR 전 별도 승인:** scheduled update의 repo/PR write 권한은 agent run과 별도 위험이다. fork guard, provider secret, PR target branch, 중단 방법을 확인한 뒤 켠다.

### 실행 단위와 관찰 증거

- Harness run record에 `repository root`, `mode`, `runId`, 고정 source revision, 시작/완료 시간, `claimsIssueCount`, `ignoredPatterns`, provider의 **이름만**, `finish` 결과를 저장하는 것을 권장한다. `BeginResult`가 이 중 run context와 일부 수치를 실제 반환한다. [E08]
- 성공 표기는 `CLI 종료`나 파일 존재만으로 하지 말고, `openwiki_finish.status=complete`, metadata status, page diff, Claims sidecar finalization을 함께 읽어야 한다. host run의 경우 finish가 완료 증거의 가장 좁은 기준이다. [E08]
- 장애에는 원본 error, stage, output diff, rollback 결과를 남긴다. 단, credentials·raw private contents·model prompt는 로그에 복사하지 않는 보안 기준을 추가로 적용한다. 이 마지막 문장은 **추천**이며 코드의 모든 logging path를 전수 감사한 결론은 아니다.

### 재실행·복구

- update failure 뒤에는 `interrupted` metadata가 남는지 확인하고, next update가 no-op이 되지 않았는지 확인한다. [E05][E10]
- init failure는 rollback 성공 여부를 분리해 기록한다. rollback 실패라면 자동 재시도보다 기존 wiki와 backup 상태를 사람에게 보여 준 뒤 복구 계획을 결정하는 편이 안전하다. 이 문장은 **추천**이다.
- finish pre-commit failure는 동일 `runId`로 finish 재시도를 허용하는 구현이므로, 새 init을 성급히 시작해 replacement 경계를 바꾸지 않는 것이 좋다. [E08]

## 미확인·운영 전 검증 항목

- 실제 Codex/Claude에서 skill discovery와 MCP stdio 설정이 이 SHA의 설치 경로대로 동작하는지.
- 실제 target repo에서 docs-only backend가 어떤 파일을 허용·차단하는지, `.openwikiignore`가 기대대로 적용되는지.
- provider별 비용, rate limit, retry 결과, OAuth token refresh, connector scope 및 retained raw data.
- scheduled update가 target GitHub 조직의 branch protection·secret·fork 설정과 충돌하지 않는지.

위 항목은 이 정적 분석으로 완료라고 할 수 없으며, 선택한 target repository의 staged dry-run과 readback으로 검증해야 한다.
