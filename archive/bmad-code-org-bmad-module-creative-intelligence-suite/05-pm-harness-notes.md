# PM Harness 운영 메모

## 추천: host wrapper를 “대화형 초안 생성기”로 먼저 운영하고, 파일 쓰기·외부 행동은 checkpoint에서 분리 승인하라

이 모듈은 좋은 진행 프롬프트와 결과 template을 제공하지만, 실행 권한을 코드로 제한하는 독립 프로그램은 아니다. 가장 안전한 Harness는 skill을 바로 unrestricted agent로 실행하는 방식이 아니라, **(1) 읽기/대화, (2) 초안 미리보기, (3) 정확한 경로·diff 확인 후 저장 승인, (4) 결과 readback**의 네 단계 wrapper를 두는 방식이다. 이 방식은 추가 구현 비용은 들지만 데이터 덮어쓰기와 customization injection 위험을 낮추고, 결과 문서만 남겨 다른 호스트로 이전하기도 쉽다. [E05][E06]

추천이 달라지는 조건은 다음 하나다. 완전히 격리된 disposable 프로젝트에서 결과 파일 자동 저장이 중요한 경우에는 사용자가 선택한 `output_folder`의 sandbox만 쓰기 허용하는 자동 저장을 허용할 수 있다. 그래도 `_bmad/custom/**/*.toml`의 prepend/append/on_complete 지시는 검토 전 자동 실행하지 않는 것이 좋다. [E05][E06]

## 사실, 현재 가정, 추천

| 구분 | 내용 |
| --- | --- |
| 확인된 사실 | 모든 agent/workflow는 base→team→user customization 병합을 지시하고, activation prepend/append 및 workflow `on_complete` hook을 지원한다. workflow는 template output 후 즉시 default output file에 저장하라고 지시한다. [E05][E06] |
| 현재 가정 | Harness가 이 prompt 지시를 실제 shell/file action으로 해석할 수 있다. 이 repo에는 그 host executor가 없으므로 실제 권한 정책은 **미확인**이다. |
| 추천 | custom TOML, `data` 파일, template, output path를 모두 run manifest에 기록하고, activation hook 및 `on_complete`는 첫 배포에서는 `NEEDS_HUMAN_REVIEW`으로 차단한다. |

## 입력 계약

실행 전에 아래를 UI/form으로 분리해 받는 것이 좋다.

| 입력 | 필요한 이유 | 없거나 잘못되었을 때 영향 |
| --- | --- | --- |
| workflow ID와 버전/SHA | 동일한 prompt를 재현하기 위해 | “어떤 방법론으로 만든 문서인지” 추적 불가 |
| 문제/전략/스토리 문맥 | LLM이 임의의 빈칸을 채우지 않게 함 | 일반론적 산출물 또는 사실 오류 |
| `data` 파일의 allowlist 경로 | skill이 문맥 파일을 load하라고 지시 | 민감 파일의 과잉 로드 또는 경로 오류 |
| `output_folder`와 파일명 | overwrite 범위를 한정 | 기존 업무 문서 덮어쓰기 |
| 언어·사용자명 | 결과 언어와 대화 스타일 결정 | 산출물 언어/호칭 불일치 |
| custom TOML 상태 | persona/menu/hook이 바뀔 수 있음 | 승인하지 않은 instruction injection |

## 승인 지점

1. **시작 전:** `data` 파일 목록과 출력 디렉터리, loaded custom TOML diff를 표시한다.
2. **각 `<template-output>` 뒤:** 원본 skill도 pause를 지시하므로, 이때 “계속 / 수정 / 저장 보류”를 명시적으로 받는다. [E06]
3. **쓰기 직전:** 절대 경로, 새 파일인지 덮어쓰기인지, 이전 버전 백업 방법을 표시한다. 권장 복구 방식은 run ID 하위의 새 파일 생성 또는 기존 파일의 버전 관리다.
4. **종료 hook 전:** resolved `workflow.on_complete`가 비어 있지 않다면 전문과 예상 영향(명령, 네트워크, 파일)을 보여 주고 별도 승인을 받는다. [E06]
5. **외부 전송:** CIS workflow 자체에는 외부 발송이 없지만 repository 운영 CI의 Discord webhook과 release workflow는 외부 상태를 바꾼다. Harness 실행과 분리하고 자동 위임하지 않는다. [E08][E16]

## 증거·로그와 완료 정의

**완료로 볼 최소 증거:** skill ID+fixed SHA, 선택한 CSV/framework, 입력 파일의 이름·해시(내용 자체는 비밀 정책에 따름), checkpoint transcript, 승인 기록, 실제 저장 파일의 절대경로·해시·readback, 그리고 실패 시 오류 로그다.

`“saved”라는 agent 문구`, chat transcript, 또는 템플릿이 화면에 보인다는 사실만으로는 저장 완료가 아니다. write 권한이 주어진 run이라면 파일을 다시 열어 template placeholder가 남지 않았는지 확인하고, write 권한이 없는 run이라면 **DRAFT_ONLY**로 끝내야 한다.

## 재실행·복구 설계

- **재실행 단위:** 전체 workflow가 아니라 checkpoint별 snapshot. 같은 date 기반 기본 파일명은 같은 날 재실행 시 충돌 가능성이 있으므로 run ID 또는 순번을 추가하는 wrapper가 필요하다. 이는 source의 이름 규칙에서 도출한 운영상 추천이다. [E06]
- **복구:** 기존 산출물 overwrite 전 snapshot을 만들고, 선택한 framework·사용자 답변·customization version을 함께 보존한다.
- **idempotency:** “저장”은 동일 target에 덮어쓰기할 수 있으므로 idempotent하다고 가정하면 안 된다. 새 파일 작성 또는 expected hash 조건부 쓰기를 권장한다.
- **관찰성:** workflow의 회고/metrics 계획은 사용자 산출물 내용이지 Harness run의 성공 metric은 아니다. run 성공은 host readback으로, 업무 효과는 별도 metric으로 측정한다.

## 확장 지점과 경계

| 확장 | 확인된 연결점 | PM 판단 |
| --- | --- | --- |
| custom persona/menu | agent `customize.toml` 및 user/team override 병합 | 조직별 말투·menu는 확장 가능하지만 code review처럼 변경 검토 필요 [E05] |
| persistent facts | literal 또는 `file:` path/glob | 필요한 정책 문서만 allowlist로 load; glob은 넓은 범위가 될 수 있음 [E05][E06] |
| visual tools | `module.yaml`의 Mermaid/Excalidraw/Gemini Nano/other 선택 | 모델·비용·외부 이미지 전송 여부는 host integration 확인 전 자동 활성화 금지 [E04] |
| documentation build | Node script와 Pages workflow | 별도 CI pipeline으로 취급; app workflow 완료와 혼동하지 않음 [E09][E10] |
| Discord | GitHub event → webhook POST | 알림은 ledger/approval source-of-truth가 아니며, 전송 본문 최소화 필요 [E16] |

## 현재 보류해야 할 운영 판단

- 정확한 BMad install command와 `/cis-*` alias: 문서끼리도 표기가 다르고 source에 registrar가 없다. host documentation 또는 실제 sandbox install로 확인 전 운영 runbook에 고정하지 않는다. [E01][E12]
- `BMAD_*` 환경변수 지원: CIS 문서의 주장만으로 host behavior를 보장할 수 없다. [E13]
- Node 20 Pages build의 성공: package Node `>=22`와 맞지 않는다. CI run log가 필요하다. [E03][E09]
- Brainstorming workflow: 이 SHA에서 target skill source가 없다. core package가 제공한다고 확인될 때까지 `BLOCKED_EXTERNAL_SKILL`로 처리한다. [E02][E05]

