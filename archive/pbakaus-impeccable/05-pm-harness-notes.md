# PM Harness 운영 메모

## 결론

**추천 운영 방식은 project-local 설치, 명시적 hook 승인, `init`으로 shared context를 먼저 고정하고, 실제 화면·detector·finish review 증거를 분리해 확인하는 방식이다.** 이 레포는 단순 프롬프트 모음이 아니라 “설계 컨텍스트 → agent 작업 → hook/detector → screenshot review → 문서화”라는 운영 단위를 전제한다. 단, 이것은 source code에서 확인한 구조 추천이며, 이 분석만으로 어떤 프로젝트에도 품질 향상을 보장한다고 말할 수는 없다. [E1] [E7] [E8] [E9]

## 확인된 사실

- skill은 세션마다 context script를 한 번 실행하고, 작업 전 요청을 소유하는 playbook과 incumbent visual truth를 읽으라고 한다. 즉 같은 명령이라도 `PRODUCT.md`, `DESIGN.md`, surface brief 유무가 결과를 바꾸는 입력 계약이다. [E7]
- `init`은 terminal 명령이 아니라 harness chat command다. CLI는 이 혼동을 오류로 막는다. 설치와 작업 시작을 분리한 이유는 terminal이 skill의 사용자 대화 컨텍스트를 갖지 않기 때문이다. [E1] [E2]
- Codex의 skill 발견 위치와 hook 발견 위치는 다르다. `.agents/skills/`는 skill, `.codex/hooks.json`은 project-local hook이다. hook 신뢰/승인은 외부 코드가 edit event 때 실행되는 경계라서 자동으로 넘길 수 없는 플랫폼 단계다. [E1] [E4]
- hook은 “동작을 막지 않기” 위해 오류에도 exit 0 하도록 되어 있다. 따라서 hook을 켰다는 사실, 또는 terminal에 오류가 없다는 사실은 품질 검토 완료 증거가 아니다. detector JSON·audit log·캡처·review verdict를 별도로 확인해야 한다. [E10]
- finish reviewer는 screenshot이 없거나 유효하지 않으면 `recapture`로 끝내도록 하고, `ship`은 누락/모순 요소가 없을 때만 쓰도록 제한한다. 완료 정의가 “agent가 실행했다”가 아니라 “적합한 viewport 증거를 검토했다”에 가깝다. [E8]

## PM이 고정해야 할 입력 계약

1. **작업 단위**: surface와 target path, preserve/refine/redesign 범위, 기능/카피/접근성 제약을 명시한다. “예쁘게”만 주면 router가 처리할 수 있어도 승인 기준은 흐려진다.
2. **지속 context**: `PRODUCT.md`에는 제품 사실, `DESIGN.md`에는 실제로 쓰인 durable system, surface brief에는 해당 화면의 목표를 둔다. build artifact가 direction contract와 다르면 documenter는 build를 우선한다고 명시한다. [E8]
3. **이미지·asset**: comp-led이면 어떤 comp가 승인본인지 기록한다. asset producer는 mock crop을 shipping pixel로 쓰지 않고, CSS가 책임질 card chrome을 raster에 구워 넣지 않도록 구분한다. [E8]
4. **live target**: monorepo에서 app 선택은 사람의 결정 지점이다. `live.mjs`가 후보 JSON을 냈는데 임의 app을 고르면 잘못된 entry file에 injection할 위험이 있다. [E9]

## 승인 지점과 위험

| 지점 | 왜 사람 승인/확인이 필요한가 | 관찰 가능한 증거 | 되돌리기 |
| --- | --- | --- | --- |
| provider install scope | global은 다른 프로젝트도 영향을 받고, project는 현재 repo만 영향 | 설치 대상 provider/scope prompt 및 생성된 경로 | 설치 파일 제거/backup 복구가 필요, 구현 세부는 미확인 |
| Codex hook trust | edit event 시 script가 실행되는 권한 경계 | `/hooks`의 승인 상태와 `.codex/hooks.json` | hook disable/manifest 제거, 신뢰 UX는 Codex 버전에 따름 |
| comp-first vs code-first | `comp`은 image generation과 승인 comp를 전제하고 더 느리며, `code`는 비용/속도는 낮지만 시각 기준이 contract 중심 | `.impeccable/config.json`의 `buildPath`, surface brief/approved comp | config/default 또는 session toggle, 문서 설명 기준 [E1] |
| live target/app 선택 | 잘못된 app injection 및 잘못된 source 편집 위험 | target-selection JSON, `projectRoot`, `pageFiles` | injection/accept rollback의 실제 동작은 미확인 |
| manual copy apply | 사용자 Apply 이후 real source를 수정한다. agent는 event 단위 원자성, no commit/push를 계약으로 둔다 | canonical JSON의 `appliedEntryIds`, files, source diff | failed entry는 same-event change를 undo하도록 정의, 실제 recovery 실행은 미확인 [E8] |
| ship verdict | 기능 테스트 통과만으로 디자인/viewport 검토를 대체할 수 없음 | desktop/mobile screenshots, reviewer `disposition`, detector findings | `fix`/`rebuild`/`recapture` 후 다시 검토 |

## 재실행·복구 설계

- **안전하게 재실행 가능**: detector는 CLI로 명시적으로 다시 실행하고 JSON을 저장할 수 있다. live 준비는 config/context 부족을 시작 전에 JSON으로 보고하며, live server PID 정보가 stale이면 cleanup을 시도한다. [E9] [E11]
- **재실행 전에 확인할 것**: live에서 serverPort는 app URL이 아니다. `pageFiles`, target root, config drift warning, PRODUCT/DESIGN state를 readback한 뒤 browser URL을 열어야 한다. [E9]
- **generated output**: source change 뒤 root provider folder를 직접 고치기보다 source-first build를 쓴다. repo policy도 tracked provider folders를 hand-authored source로 보지 않는다. [E5]
- **release**: release script는 clean tree·pushed HEAD·build drift·changelog/artifact를 확인하지만, tag/push/release를 실제로 수행한다. 운영 자동화에서 이 단계는 명시적 final approval 뒤에만 둬야 한다. [E6]

## 모델/agent 역할의 해석

**확인됨**: 네 subagent 모두 `model: inherit`이다. asset producer/documenter/manual edit applier는 medium effort, finish reviewer는 high effort로 source frontmatter에 선언돼 있다. [E8]

**추론**: 이 설계는 한 모델 브랜드를 강제하기보다 역할별 입력/출력 계약을 고정하려는 것이다. PM 관점의 핵심은 “어느 모델인가”보다, 각 agent에 어떤 승인된 mock·contract·screenshot·source hint를 전달했는지와, 반환물이 표준 형식인지다.

## 추천 운영 대시보드 최소 항목

다음은 코드에 없는 **추천**이다. source가 요구하는 증거를 운영에서 잃지 않기 위한 최소 레코드다.

- 작업 ID, repository/app root, target surface, `buildPath`, 요청 범위와 승인자
- context 문서 경로/해시, approved comp 또는 “code-led/no comp” 표시
- detector 실행 시각/대상/결과, hook audit log 위치(설정한 경우)
- desktop/mobile 및 사용자 viewport 캡처 경로, finish reviewer disposition
- live session ID와 accept/apply JSON, 변경 source file 목록, 재검증 결과
- release는 별도 record로 분리하고 tag, CI run URL, artifact checksum, 최종 승인자를 남긴다.

이 레포는 로그를 항상 중앙 저장소에 전송하는 기능을 이 분석 범위에서 확인하지 않았다. 위 대시보드는 외부 운영 도구에 설계해야 하며, `.impeccable`의 ephemeral state를 공식 ledger로 취급하면 안 된다.
