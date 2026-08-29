---
id: project-core
type: principles
status: active
updated: 2026-08-29
authority: canonical
provenance: []
---

이 문서는 **이 저장소가 무엇이고 어디에 무엇이 있는지**를 담는다. 행동 규범은 담지 않는다 —
그것은 `core/principles/AGENTS.core.md` 가 소유하고 이 블록 아래에 이어진다.

`romeo compile` 이 이 파일을 **두 런타임의 지침 파일에 같은 managed block 으로** 넣는다.
한쪽 런타임만 인덱스를 보는 상태를 만들지 않기 위해서다 — 같은 것을 보지 않는 두 실행의 판정이 같다는 것은
동등성의 증거가 아니다. 런타임 고유 매핑은 어댑터가 붙인다(C-C6).

이 저장소는 여러 프로젝트에 부착할 AI 작업 하네스를 만든다. 목표는 에이전트와 규칙을 쌓는 것이
아니라, 요청을 이해하고 필요한 작업 방식만 골라 계획·실행·검증·기록까지 일관되게 수행하는 체계다.

## 충돌 해소 순서

현재 사용자의 명시적 요청 → 승인된 현재 문서와 결정 → 프로젝트 인덱스 → 과거 대화·조사 자료 →
참고 저장소 → 일반적인 권고. 충돌을 임의로 해석하지 말고 차이와 추천안을 알린다.

## 세션을 시작할 때 — 세 번만 본다

| # | 무엇 | 어디 |
| --- | --- | --- |
| ① | 지금 상태·다음 작업 | `docs/planning/progress.md` 상단 「지금 상태」 블록 |
| ② | 그 블록이 최신인지 | `git log --oneline <기준SHA>..HEAD` — 그 사이 커밋이 상태를 바꿨으면 실측한다 |
| ③ | CI 빨간불 여부 | 저장소의 CI 실행 목록에서 최신 1건 |

## 문서 인덱스

| 알고 싶은 것 | 파일 |
| --- | --- |
| 진행 상태·마일스톤·미검증 위험 | `docs/planning/progress.md` |
| 구현 계획·§10 체크리스트 | `docs/planning/implementation-plan.md` |
| 확정된 결정 (D-xx·K-xx) | `docs/decisions/decision-register.md` |
| 열린 질문·미검증 가정 (A-xx·X-xx·Q-xx) | `docs/planning/open-questions.md` |
| v1 범위·능력 지도·제약 | `docs/requirements/` |
| 독립 리뷰 findings 원문 | `docs/reviews/<날짜>-<라운드>/` |
| 작업 단위 (spec·evidence·result·review) | `docs/work/<unit_id>/` |
| 이 인덱스의 원본 | `core/principles/PROJECT.core.md` |
| 코어 규칙 원본 (아래 규칙 절의 출처) | `core/principles/AGENTS.core.md` |
| 라우터 정책표 (분류·패키지·실행 가드) | `core/policy/*.yaml` |
| 역할 계약·스키마·템플릿 | `core/roles/` · `core/schemas/` · `core/templates/` |
| 부품 출처·라이선스·채택 판정 | `provenance/imports.yaml` |
| 위임 절차 (런타임 고유) | `adapters/orca/RUNBOOK.md` |
| 역할↔런타임 바인딩·권한 상한 정본 | `.harness/bindings.yaml` |
| 런타임 관찰 기록 (discovery·로드·재현성) | `.harness/observations.yaml` |
| 동등성 게이트 케이스 | `fixtures/parity/` |

## 이 저장소에만 해당하는 것

- **하네스가 하네스를 만든다.** 여기서 만든 규칙이 이 저장소 자신에게 적용된다 —
  권한 상한이나 종료 검사를 고치면 다음 작업이 바로 그 규칙 아래 돈다.
- **벤더 중립.** `core/` 에 도구명·모델명을 쓰지 않는다(C-C6). 런타임 고유 매핑은 어댑터에만 둔다.
- **참고 저장소는 통째로 복제하지 않는다.** 필요한 파일만 고정 SHA 로 가져오고
  출처·라이선스·기준 버전·수정 여부를 `provenance/imports.yaml` 에 남긴다.
- **조사 비용을 아낀다.** 큰 문서를 통째로 열지 말고 목차(`grep -n "^## "`)나 표의 특정 열부터 읽는다.
  `docs/planning/progress.md` 는 46KB 다.
