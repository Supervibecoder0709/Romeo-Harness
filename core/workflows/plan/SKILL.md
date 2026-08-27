---
name: plan
description: 요청을 이해해 사실·가정·미확인·분류 후보를 제안 카드로 정리하고, 사람이 확정하면 정책표로 문서 패키지를 계산해 필요한 문서만 생성한다. 사용자가 새 요청을 가져오거나 "/plan", "이거 어떻게 진행할지 분류해줘", "계획 잡아줘"라고 할 때 사용한다. 구현은 하지 않는다.
provenance: [anthropics-skills-skill-format]
---

# romeo:plan — 요청 이해 → 제안 카드 → 사람 확정 → 정책 계산 → 문서 생성

이 본문은 실행기(Claude·Codex)에 중립이다. 도구명·모델명을 쓰지 않는다. 각 실행기의 어댑터가
"사람에게 묻는 방법"과 "명령을 실행하는 방법"만 매핑한다(C-C6).

## 역할 분담 (D-06)

| 단계 | 누가 | 무엇 |
| --- | --- | --- |
| 제안 | LLM | 요청을 읽고 사실 / 가정 / 미확인 / 분류 후보 / 5요인 / 2질문 / 게이트 체크리스트를 채운다 |
| 확정 | 사람 | 카드를 보고 1클릭으로 확정하거나 단위·깊이·게이트를 고친다 |
| 강제 | 정책표 | `romeo route` 가 profile·패키지·섹션·검토·격리·차단·부품·가드를 계산한다. 같은 입력이면 항상 같은 출력 |

## 절차

1. **재사용 검색.** `docs/work/` 와 `docs/current/` 에서 같은 slug·제목·핵심어를 검색한다. 이미 있는 단위가 있으면
   새로 만들지 말고 그 id 를 카드 `reuse_hits` 에 넣고 "재개 / 재분류 / 새 단위" 중 하나를 제안한다.
2. **제안 작성.** `core/schemas/proposal.json` 형식으로 채운다.
   - 사실은 요청·저장소에서 확인한 것만. 가정은 확인하지 않은 전제. 미확인은 확인이 필요한 것.
   - `candidate.unit` 은 `none / T0 / T1 / T2`, `mode` 는 `delivery / discovery / experiment`,
     `intent` 는 `read / write / delete / deploy / mixed`, `facets` 는 `core/policy/classification.yaml` 의 어휘.
   - 5요인(범위·불확실성·영향·되돌리기·조율)은 각각 level + 한 줄 이유. 합산하지 않는다.
   - 2질문(영향 반경 / 불확실성)은 카드의 핵심 확인 질문이다.
   - hard gate 8 체크리스트는 전부 인쇄하고 발동한 것만 `checked: true`.
   - 저장소 산출물이 없는 질문·조사는 `unit: none` 으로 제안한다. 문서를 만들지 않는다.
   - 코드가 없는 프로젝트(면접 준비·운영 메모 등)의 요청은 v1 범위 밖이다. `unit: none` + `needs_decision` 에
     "v1 코드 프로젝트 전용(D-43) — 경량 부착만 가능" 을 적는다. 아는 척 분류하지 않는다.
3. **카드 인쇄.** `romeo card --proposal <파일>` 로 ≤ 30줄 카드를 만든다. 카드는 깊이(Quick/Standard/Deep)와
   그 이유를 먼저 보여주고, 단위·모드·영역은 한 줄로 보여준다.
4. **사람 확정.** 카드를 보여주고 한 번에 확정받는다. 기본 선택은 제안값이다. 사람이 고치면 `human_correction` 으로
   기록한다(shadow mode 20건 동안은 T0도 전부 확인받는다, V-10).
5. **정책 계산.** 확정된 분류로 `romeo route --classification <파일>` 를 실행한다. 출력의 `policy_version`·`fired_rules`
   는 문서 frontmatter 에 그대로 기록된다.
6. **문서 생성.** `romeo new --from <route 출력>` 이 `docs/work/<unit-id>/` 에 패키지 문서를 만든다.
   - `unit: none` 이면 문서를 만들지 않고 답변으로 종료한다. 카드는 `.harness/runs/` 에 남긴다.
   - T0 는 Tech Spec 1개(Planning Capsule 포함). T1 은 Compact Brief + Tech Spec. T2 는 Charter 부터.
   - 아직 템플릿이 없는 문서(brief 는 M2, charter 는 M3)는 `NOT_AVAILABLE_YET` 으로 정직하게 보고한다.
7. **내용 채우기.** `NEEDS_INPUT` 자리를 요청·조사 결과로 채운다. 모르는 것은 `UNKNOWN` 또는 `NEEDS_VALIDATION`
   으로 남긴다(K-33). 길이 예산을 넘으면 게이트 섹션이 아니라 다른 절을 줄인다.
8. **승인 요청.** 사용자에게는 **확인란만** 읽고 승인하도록 안내한다. 승인되면 `romeo approve <id> --by <이름>` 이
   `approved_at` 을 기록하고 `status: active` 로 바꾼다. 구현 착수는 이 승인이 유일한 선행 조건이다(D-27).

## 하지 않는 것

- 구현·리뷰·배포. (implement / review 워크플로우의 몫, 승인 뒤에만)
- 부품(BMAD/CIS·Superpowers·디자인 스킬) 자동 실행. 라우터 출력 `parts` 에 이름만 적고, 채택 게이트를 통과한
  부품만 사용한다(K-60). 통과 전이면 `PART_PENDING_GATE` 로 표시한다.
- 존재하지 않는 도구를 가정. 필요한 능력은 `capability-check` 섹션에 적고 프로브 결과가 없으면 미확인으로 둔다.

## 재분류

실행 중 범위가 커지면 `/plan` 을 다시 실행한다. 새 분류는 같은 문서의 frontmatter 를 갱신하고
`routing.history` 에 이전 값을 append 한다. 파일은 옮기지 않는다(D-09·D-11).
