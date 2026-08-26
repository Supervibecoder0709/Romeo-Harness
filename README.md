# Romeo-Harness

The harness "Romeo" for Julliette. Codex &amp; Claude Code only.

Romeo는 PM의 자연어 요청을 위험도와 규모에 맞는 최소 기획 문서·실행 계약·검증 증거로 바꿔
Claude Code와 Codex가 같은 의미로 수행하게 만드는 **요청 운영 체계**입니다.
에이전트·스킬 카탈로그가 아닙니다.

## 요구사항과 결정

원천 대화 25건을 정규화한 결과입니다. 새 작업은 여기서 시작하세요.

| 문서 | 내용 |
| --- | --- |
| [제품 브리프](docs/product/harness-brief.md) | 무엇을 왜 만드는가, 성공의 정의, 비목표, 진실 소유권 경계 |
| [능력 지도](docs/requirements/capability-map.md) | 필요 능력 A~I. 도구 이름이 아니라 능력 기준 |
| [제약](docs/requirements/constraints.md) | 위반하면 설계가 깨지는 조건 |
| [v1 범위](docs/requirements/v1-scope.md) | 구현됨 / v1 필수 / 짓지 않는 것과 도입 트리거 |
| [결정 등록부](docs/decisions/decision-register.md) | 확정·대체·미확정 결정과 폐기된 아이디어 |
| [열린 질문](docs/planning/open-questions.md) | 미검증 가정, 충돌, 승인이 필요한 결정 |
| [대화 커버리지](docs/traceability/conversation-coverage.md) | 각 판단이 어느 대화에서 왔는가 |

최종 권장 아키텍처는 **Thin Policy-Compiled Planning Spine** 입니다.
도출 과정은 [`docs/council/`](docs/council/README.md), 원 논의는
[`docs/planning-harness-discussion.md`](docs/planning-harness-discussion.md) 에 있습니다.

## 현재 구현 상태

동작하는 것은 참조 저장소 아카이브 파이프라인(`/repo`)뿐입니다.
기획 하네스(`/plan`, `/plan-close`)는 아직 구현되지 않았습니다. 자세한 구분은
[v1 범위](docs/requirements/v1-scope.md) 를 보세요.

## 아카이브

`repo` 스킬로 GitHub 레포를 고정 커밋에 묶어 분석한 한국어 아카이브는
[`archive/`](archive/README.md) 에 있습니다. 목록·요약·고정 커밋은 그 인덱스에서 볼 수 있으며,
`scripts/generate-archive-index.py` 가 생성하고 CI가 최신 상태를 강제합니다.

## 원천 자료

요구사항의 근거가 된 Codex 세션 기록 25건은
[`docs/source-context/`](docs/source-context/project-conversations-compressed-2026-08-27/README.md) 에
있습니다. `SHA256SUMS` 로 무결성을 확인할 수 있습니다.
