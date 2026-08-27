<!-- romeo:managed start v0.1.0 source=core/principles/AGENTS.core.md sha=252b6470 -->
# Romeo 하네스 규칙 (자동 생성)

원본은 `core/principles/AGENTS.core.md` 이고 이 블록은 `romeo compile` 이 만든다.
**마커 안을 고치지 않는다** — 다음 컴파일에서 사라진다. 마커 밖에 쓴 내용은 보존된다.

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

---

## 역할 (D-68)

| 역할 | 런타임 | 쓰기 | 어떻게 강제하나 |
| --- | --- | --- | --- |
| `implementer` | claude | 예 | 작업 공간 쓰기 허용 |
| `reviewer` | codex | **아니오** | codex -s read-only |

역할 교체 재실행: implementer=codex · reviewer=claude. 같은 판정이 나와야 동등성 게이트를 통과한다.

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
- **orchestration** → orca orchestration
  - 병렬 비교는 `race` 를 쓴다.
  - 대상: `sp-subagent-driven-development`, `sp-dispatching-parallel-agents` · 이유: task/dispatch provenance·lifecycle 이 Orca 에만 생긴다

## 이 저장소에서 켜져 있는 절차

| 이름 | 출처 | 언제 |
| --- | --- | --- |
| `plan` | `core/workflows/plan/SKILL.md` | 라우터 진입점 |
| `plan-close` | `core/workflows/plan-close/SKILL.md` | 라우터 진입점 |
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
