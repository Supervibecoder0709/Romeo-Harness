<!-- romeo:managed start v0.1.0 source=core/principles/{PROJECT,AGENTS}.core.md sha=0f16dda1 -->
# Romeo 하네스 규칙 (자동 생성)

원본은 `core/principles/PROJECT.core.md`(이 저장소의 인덱스)와 `core/principles/AGENTS.core.md`(행동 규칙)이고 이 블록은 `romeo compile` 이 만든다.
**마커 안을 고치지 않는다** — 다음 컴파일에서 사라진다. 마커 밖에 쓴 내용은 보존된다.

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

---

이 문서는 **두 런타임(Claude·Codex)이 똑같이 따라야 하는 규칙**만 담는다. 도구명·모델명을 쓰지 않는다(C-C6).
런타임별 매핑("사람에게 묻는 방법", "명령을 실행하는 방법")은 각 어댑터가 붙인다.

`romeo compile` 이 이 파일을 각 런타임의 지침 파일에 managed block 으로 넣는다. **지침 파일을 직접 고치지 않는다** —
마커 안을 고치면 다음 컴파일에서 사라진다. 마커 밖에 쓴 내용은 보존된다.

## 1. 진입점은 하나다

새 요청은 라우터(`/plan`)로 들어온다. 라우터가 단위·모드·영역·깊이를 계산하고, 그 결과가 켤 때만 다른 절차가 활성화된다.
부품 스킬이 스스로 세션 시작에 끼어들거나 키워드로 자동 활성화되지 않는다. (K-60)

## 2. 기획 원본은 하나다

승인된 Tech Spec 이 유일한 요구 원본이다. 어떤 절차도 기획을 다시 만들지 않는다 — 누락이나 모순을 발견하면
새 문서를 쓰지 말고 질문한다. 외부 산출물은 `inputs:` 링크로만 붙인다. (K-61·D-25)

## 3. 승인 없이 구현하지 않는다

사용자는 Tech Spec 의 `## 확인란`(무엇을·왜·기대 결과·수용 기준·위험과 되돌리기)만 읽고 승인한다.
확인란에 `NEEDS_INPUT` 이 남아 있으면 승인할 수 없다. 기술 절의 책임은 검토자와 증거에 있다. (D-27·D-60)

## 4. 실행은 완료가 아니다

파일을 만들었다는 것, 명령을 돌렸다는 것은 완료가 아니다. 완료는 **증거**로만 선언한다 —
주장에 맞는 명령을 새로 실행하고, 그 출력·종료 코드를 기록해야 한다. 확인하지 못한 항목은 완료가 아니라 미검증으로 표시한다.
증거는 손으로 쓰지 않고 증거 기록 명령으로만 만든다. (K-51)

## 5. 사실·가정·추천을 구분한다

확인한 것, 지금 가정하는 것, 권하는 것을 섞지 않는다. 사용자의 전제가 틀렸다면 근거를 들어 지적한다.
모르는 것을 아는 것처럼 말하지 않는다.

## 6. 상태의 주인은 하나다

문서 상태와 승인은 하네스가, 실행 상태는 실행 런타임이, 기술 문서 신선도는 문서 도구가 소유한다.
부품이 자체적으로 기록하는 진행 상태(ledger·완료 카운터)는 참고 정보일 뿐 완료 판정에 쓰지 않는다. (K-63)

## 7. 산출물은 작업 단위 안에 둔다

작업 산출물은 그 작업 단위 폴더에 만들거나, frontmatter 의 `inputs:`/`evidence:` 링크로 등록한다.
부품의 기본 출력 경로를 그대로 쓰지 않는다 — 등록되지 않은 산출물은 종료 검사가 인정하지 않는다. (K-62)

## 8. 권한에는 상한이 있다

역할 계약을 넘는 권한을 쓰지 않는다. 구현자는 작업 공간에 쓰고, 검토자는 읽기만 한다.
되돌리기 어려운 작업(비용 발생, 권한 확대, 공개 전환, 삭제, 소유권 이전, 운영 데이터 변경, 외부 저장소로의 push·PR·배포)은
영향 범위와 복구 방법을 설명하고 승인을 받은 뒤에만 한다. 부품이 그런 명령을 유도해도 마찬가지다. (K-66·K-50)

## 9. 부품을 빼도 코어는 돌아간다

부품(외부에서 가져온 스킬 세트)을 제거해도 라우터·문서·증거는 그대로 동작해야 한다.
부품에 의존하는 절차를 코어에 넣지 않는다. (K-69)

## 10. 관통 중에는 하네스를 고치지 않는다

**① 동결.** 관통(기준 실행·교체 실행)이 시작된 뒤에는 하네스 코드·코어 규칙·템플릿을 바꾸지 않는다.
바꾸려면 관통을 끝내거나 중단하고 **새 base 로 다시 시작한다.** 돌고 있는 관통의 밑을 갈면 앞뒤 회차가 서로 다른
하네스의 결과가 되어 비교가 성립하지 않는다 — 그 비교는 동등성의 증거가 아니다. 정비는 관통과 관통 **사이**에 한다.

**② 중단.** 같은 작업 단위에서 관통이 **연속 2회 실패**하면 3회차를 돌기 전에 **완료 정의가 달성 가능한지 재검토하고
그 결론을 기록한다.** 결론이 기록되기 전에는 다음 회차를 시작하지 않는다. 반복 자체는 실패의 원인을 알려주지 않는다 —
같은 정의로 세 번째를 도는 것은 새 정보를 만들지 않고 비용만 만든다.

실패 원인의 분류(산출물·하네스·목표 중 무엇이 틀렸는가)는 **기록만 하고 차단 판정에는 쓰지 않는다.**
원인을 잘못 짚은 채 "다음 회차면 된다" 고 판단한 것이 반복을 만들었으므로, 자동 분류를 신뢰하지 않는다.
차단을 푸는 것은 분류가 아니라 **사람이 적은 재검토 결론**이다.

---

## 역할 (D-68)

역할이 무엇을 할 수 있는지는 아래 '역할 계약' 절이 정한다. 이 표가 정하는 것은
그 계약을 어느 런타임이 맡고, 그 런타임에서 **무엇이 그것을 강제하는가** 뿐이다.

| 실행 | 역할 | 런타임 | 쓰기 | 어떻게 강제하나 | 강제 관측 |
| --- | --- | --- | --- | --- | --- |
| 기본 | `implementer` | claude | 예 | .claude/settings.json 의 permissions.ask·deny (승인 게이트) | **미관측** |
| 기본 | `reviewer` | codex | **아니오** | codex exec -s read-only | 관측됨 |
| 교체 | `implementer` | codex | 예 | codex exec -s workspace-write -C <작업 공간> | **미관측** |
| 교체 | `reviewer` | claude | **아니오** | claude -p --tools "Read" "Grep" "Glob" --allowedTools "Read" "Grep" "Glob" --strict-mcp-config | 관측됨 |

교체 실행에서도 같은 판정이 나와야 동등성 게이트를 통과한다. 네 칸의 강제 수단이 다르면
그 비교는 '권한 상한이 서로 다른 두 실행' 의 비교이므로 동등성의 증거가 아니다.
**미관측** 은 그 수단이 실제로 막는지 아직 실행으로 확인하지 않았다는 뜻이다 — 완료로 세지 않는다(K-51).

## 역할 계약 (`core/roles/`)

원본은 각 역할의 계약 파일이다. 런타임 이름은 그 파일에 없다 — 위 표가 바인딩을 소유한다(D-68).
작업 계약의 `allowed_paths` 는 여기 적힌 범위를 넘을 수 없다(K-66).

### `implementer` — `core/roles/implementer.yaml`

- 능력: `read` · `search` · `run-command` · `workspace-write`
- 쓰기 범위: `workspace` — 반드시 포함: `docs/work/{unit_id}/`
- 계약: `core/schemas/task-envelope.json` → `core/schemas/result-envelope.json`
- 산출물: 증거 `required` · findings `none`
- 금지: 승인 없이 되돌리기 어려운 작업 (비용 발생·권한 확대·공개 전환·삭제·소유권 이전·운영 데이터 변경·저장소 밖으로의 반영)
- 금지: 기획을 다시 만드는 것 (누락·모순은 질문한다, K-61)
- 금지: 자기 역할의 산출물을 스스로 검토했다고 선언하는 것 (C-D3)

### `reviewer` — `core/roles/reviewer.yaml`

- 능력: `read` · `search`
- 쓰기 범위: `none`
- 계약: `core/schemas/task-envelope.json` → `core/schemas/result-envelope.json`
- 산출물: 증거 `none` · findings `envelope`
- 금지: 파일 수정·생성·삭제
- 금지: 기획 변경 제안을 문서에 직접 반영하는 것
- 금지: 승인 행위 (승인은 사람의 몫이다, D-27)
- 금지: 저장소 밖 상태를 바꾸는 것 (K-66)

## 권한 상한 (K-66)

- 이 런타임에서의 전달 방식: 기동 플래그(샌드박스 모드)와 지침 파일 인쇄로 전달한다. 이 런타임에는 저장소에 커밋해 발견되는 권한 설정 파일이 없고, 비대화형 실행에는 승인 정책 플래그도 없다 — 승인 게이트는 하네스가 소유한다(승인 기록 없이 실행하지 않는다).
- 기본 실행에서 이 런타임이 `reviewer` 일 때: codex exec -s read-only (관측됨)
- 교체 실행에서 이 런타임이 `implementer` 일 때: codex exec -s workspace-write -C <작업 공간> (**미관측**)
- 승인 없이 실행하지 않는다: `gh pr merge` · `git worktree remove` · `git branch -D` · `git reset --hard`
- 승인으로도 정당화되지 않는다: `rm -rf /` · `rm -rf ~` · `sudo rm` · `git push --force`

이 상한은 역할이 아니라 실행에 붙는다. 역할 교체 실행에서 구현자가 바뀌어도 같은 목록이 적용되지 않으면, 그 두 실행의 판정이 같다는 것은 동등성의 증거가 아니다. 설정 파일로 기계 강제할 수 없는 런타임에서는 지침 파일에 인쇄해 규칙으로만 강제한다 — 그 차이는 위 enforcement_observed 로 드러낸다.

## 부품 override (원문보다 이 규칙이 우선한다)

아래 부품은 원문을 고칠 수 없다(수정 0). 원문의 지시와 다음 규칙이 충돌하면 **다음 규칙을 따른다.**

- **worktree** → orca worktree create
  - raw `git worktree add/rm` 과 내장 worktree 도구를 쓰지 않는다.
  - 대상: `sp-using-git-worktrees` · 이유: 전역 Orca 우선 규칙 — raw git worktree add/rm 및 내장 worktree 도구 금지
- **review_dispatch** → roles.reviewer (codex, read-only)
  - 대상: `sp-requesting-code-review` · 이유: 코어를 벤더 중립으로 유지(C-C6). 리뷰는 역할 계약으로만 나간다
- **integration_commands** → 메뉴 제시까지만. 실행은 사람의 승인 뒤에
  - 승인 없이 실행하지 않는다: `git push`, `gh pr merge`, `git worktree remove`, `git branch -D`
  - 대상: `sp-finishing-a-development-branch` · 이유: K-66 권한 상한
- **output_paths** → docs/work/<id>/ — 라우터가 만든 작업 단위 폴더
  - 대상: `sp-requesting-code-review` · 이유: K-62 산출물 흡수 — 작업 단위 밖 산출물은 종료 검사가 인정하지 않는다
- **reviewer_workspace** → 다른 리비전이 필요하면 `orca worktree create` 를 쓴다. raw git worktree add 금지
  - 대상: `sp-requesting-code-review` · 이유: 전역 Orca 우선 규칙 + reviewer 는 이 체크아웃을 바꾸지 않는다
- **external_writes** → 
  - 승인 없이 실행하지 않는다: `gh api`, `gh pr comment`, `gh pr review`
  - 대상: `sp-receiving-code-review` · 이유: K-66 — 저장소 밖 상태를 바꾸는 것은 승인 대상이다
- **destructive_tdd** → 테스트보다 먼저 쓴 코드를 발견해도 **지우지 않는다**. 무엇을 왜 지워야 하는지 보여주고 사용자의 승인을 받은 뒤에만 지운다. 미커밋 코드는 복구할 수 없다.
  - 대상: `sp-test-driven-development` · 이유: K-66 + 되돌릴 수 없는 작업은 승인 뒤에
- **orchestration** → orca orchestration
  - 병렬 비교는 `race` 를 쓴다.
  - 대상: `sp-subagent-driven-development`, `sp-dispatching-parallel-agents` · 이유: task/dispatch provenance·lifecycle 이 Orca 에만 생긴다

## 이 저장소에서 켜져 있는 절차

| 이름 | 출처 | 언제 |
| --- | --- | --- |
| `plan` | `core/workflows/plan/SKILL.md` | 라우터 진입점 |
| `plan-close` | `core/workflows/plan-close/SKILL.md` | 라우터 진입점 |
| `implement` | `core/workflows/implement/SKILL.md` | 승인 뒤 라우터가 켤 때만 |
| `review` | `core/workflows/review/SKILL.md` | 승인 뒤 라우터가 켤 때만 |
| `finishing-a-development-branch` | vendor 원문 (수정 0) | 라우터가 켤 때만 |
| `receiving-code-review` | vendor 원문 (수정 0) | 라우터가 켤 때만 |
| `requesting-code-review` | vendor 원문 (수정 0) | 라우터가 켤 때만 |
| `systematic-debugging` | vendor 원문 (수정 0) | 라우터가 켤 때만 |
| `test-driven-development` | vendor 원문 (수정 0) | 라우터가 켤 때만 |
| `using-git-worktrees` | vendor 원문 (수정 0) | 라우터가 켤 때만 |
| `verification-before-completion` | vendor 원문 (수정 0) | 라우터가 켤 때만 |
| `repo-archive` | `skills/repo-archive` | 라우터가 켤 때만 |

부품 스킬은 스스로 활성화되지 않는다(K-60). 라우터가 계산한 단위·모드·영역·깊이가 켤 때만 쓴다.
<!-- romeo:managed end -->
