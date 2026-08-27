# Romeo-Harness

The harness "Romeo" for Julliette. Codex &amp; Claude Code only.

Romeo는 사용자가 직접 써보고 검증한 하네스들(BMAD/CIS·Superpowers·OpenWiki·디자인 스킬·Orca)을
**부품으로 그대로 두고**, 그 앞에서 요청을 이해해 어떤 부품을 어떤 깊이로 쓸지 정하고, 부품 사이의
산출물·상태·증거를 하나의 문서 체계로 이어 주며, Claude Code와 Codex 어느 쪽에서 실행해도 같은 판정이
나오게 하는 **개인용 라우터(요청 운영 체계)**입니다. 에이전트·스킬 카탈로그가 아니고, 부품을 다시 만드는
프로젝트도 아닙니다.

## 요구사항과 결정

원천 대화 25건을 정규화한 결과입니다. 새 작업은 여기서 시작하세요.

| 문서 | 내용 |
| --- | --- |
| [제품 브리프](docs/product/harness-brief.md) | 무엇을 왜 만드는가, 만드는 것/만들지 않는 것, 성공의 정의, 부품 조립표 |
| [능력 지도](docs/requirements/capability-map.md) | 필요 능력 A~J. A~I는 라우터·접착·동등성, J는 부품 조립 |
| [제약](docs/requirements/constraints.md) | 위반하면 설계가 깨지는 조건. 7절 = 부품 통합 규약 K-60~K-69 |
| [v1 범위](docs/requirements/v1-scope.md) | 구현됨 / v1 필수 / 짓지 않는 것과 도입 트리거 |
| [결정 등록부](docs/decisions/decision-register.md) | 확정·대체·미확정 결정과 폐기된 아이디어 |
| [열린 질문](docs/planning/open-questions.md) | 미검증 가정, 충돌, 승인이 필요한 결정 |
| [대화 커버리지](docs/traceability/conversation-coverage.md) | 각 판단이 어느 대화에서 왔는가 |

최종 권장 아키텍처는 **Thin Policy-Compiled Planning Spine** 입니다 — 이것이 라우터와 접착이고,
그 척추가 켜고 끄는 대상이 부품입니다. 도출 과정은 [`docs/council/`](docs/council/README.md), 원 논의는
[`docs/planning-harness-discussion.md`](docs/planning-harness-discussion.md) 에 있습니다.

구현 계획은 [`docs/planning/implementation-plan.md`](docs/planning/implementation-plan.md)(개정 4)이고, 진행 상태는 [`docs/planning/progress.md`](docs/planning/progress.md)이며,
부품을 어떻게 조립하는지·채택 확정 게이트·통합 규약의 근거는
[`docs/reviews/2026-08-27-assembly-redefinition/`](docs/reviews/2026-08-27-assembly-redefinition/summary.md)에 있습니다.

## 현재 구현 상태

- 참조 저장소 아카이브 파이프라인(`/repo`) — 동작.
- **M0 완료** (2026-08-27): 정책표 `core/policy/`, 스키마 `core/schemas/`, Tech Spec 템플릿, `/plan`·`/plan-close` 워크플로우 본문,
  `bin/romeo` CLI(route·card·new·validate·approve·evidence·close), fixture 33건(`fixtures/requests/`), 테스트 23개.
- **M1 완료** (2026-08-27): T0 2건이 `분류 → Tech Spec → 승인 → 구현 → evidence(HEAD SHA) → close PASS` 를 관통했다 (`docs/work/`).
- 미착수: M2(어댑터·역할·Orca 위임·Codex 교차 리뷰) 이후. 진행 상태는 [progress.md](docs/planning/progress.md), 자세한 구분은
  [v1 범위](docs/requirements/v1-scope.md).

```bash
bin/romeo route --fixtures fixtures/requests --report   # 정책표 일치율
python3 -m unittest discover -s tests                   # 회귀 테스트
bin/romeo validate                                      # docs/work 문서 검증
```

## 아카이브

`repo` 스킬로 GitHub 레포를 고정 커밋에 묶어 분석한 한국어 아카이브는
[`archive/`](archive/README.md) 에 있습니다. 목록·요약·고정 커밋은 그 인덱스에서 볼 수 있으며,
`scripts/generate-archive-index.py` 가 생성하고 CI가 최신 상태를 강제합니다.

## 원천 자료

요구사항의 근거가 된 Codex 세션 기록 25건은
[`docs/source-context/`](docs/source-context/project-conversations-compressed-2026-08-27/README.md) 에
있습니다. `SHA256SUMS` 로 무결성을 확인할 수 있습니다.
