---
name: plan-close
description: 작업 단위를 종료한다. 문서 스키마·링크·미체크 수용 기준·길이 예산·open loop·evidence 신선도(HEAD SHA·작업 트리 해시)·required_checks 를 검사해 통과하면 status 를 done 으로 확정한다. 사용자가 "/plan-close", "이 작업 마무리해", "완료 처리해줘"라고 할 때 사용한다. 검사가 실패하면 완료라고 하지 않는다.
provenance: []
---

# romeo:plan-close — 검증 → 상태 확정 → 승격 후보

"만들었다"를 "검증했다"로 바꾸는 유일한 장치다. 실행 자체는 완료가 아니다(K-51).

## 절차

1. **증거 확인.** `docs/work/<id>/evidence/*.yaml` 이 최소 1건 있어야 한다. 없으면 close 는 `HAS_EVIDENCE` 로 실패한다.
   증거는 `romeo evidence run --unit <id> -- <명령>` 으로만 만든다. 손으로 쓰지 않는다.
2. **검사 실행.** `romeo close --unit <id>` 는 아래를 순서대로 검사한다. 하나라도 실패하면 상태를 바꾸지 않는다.
   - frontmatter 스키마 유효, `status: active`, `approved_at` 존재
   - 수용 기준 체크박스가 전부 `[x]` (미체크가 있으면 `AC_ALL_CHECKED`), 그리고 확인란의 **문장**이 승인 커밋의 것과 같음(`AC_TEXT_UNCHANGED` — 체크 표시만 다를 수 있다 —
     확인란은 사용자가 승인한 면이므로 문장을 고쳤으면 재승인 대상이다). 검증 계획(`required_checks`)도 승인 커밋의 것과 같아야 한다 —
     계획을 고치고 커밋해도 재승인하지 않았으면 거부한다(`CHECK_PLAN_COMMITTED`). 승인 커밋은 파일에 적힌 값이 아니라 이력에서 찾는다(현재 승인이 처음 커밋된 자리)
   - `NEEDS_INPUT` 잔존 0 (`NO_OPEN_LOOP`), 길이 예산 이내(`BUDGET_EXCEEDED` 는 문서 경고)
   - 문서 안 상대 링크가 실제 파일을 가리킴(`BROKEN_LINK`)
   - **검사 기록을 내용으로 고른다** — 검증 계획의 검사를 전부 실행한 evidence run(여럿이면 최신)이 이 단위의 검사 기록이다.
     마지막 파일이 아니다: 검토자를 띄우며 남긴 방어 검사 전용 run 은 검사 기록이 아니고, run 들을 합치지도 않는다(검사는 한 산출물 위에서
     전부 돌아야 한다). 어느 run 을 골랐고 어느 run 을 제외했는지 인쇄한다
   - 그 검사 기록의 `head_sha` 가 현재 `git rev-parse HEAD` 와 같고 `dirty_tree_hash` 가 현재 작업 트리와 같음
     — 다르면 `FRESH_HEAD`/`FRESH_TREE`. 커밋 이동·tracked 수정·staged 변경·untracked 추가 네 경우 모두 거부한다
   - spec 의 `required_checks` 명령이 그 검사 기록의 `commands` 에 exit 0 으로 존재(`REQUIRED_CHECK`), 그 기록이 원시 로그·봉인과 맞음(`EVIDENCE_LOG`),
     그리고 **같은 명령을 그 체크아웃에서 다시 실행해** 종료 코드가 기록과 같음(`REQUIRED_CHECK_RERUN` — 기록은 믿지 않는다; `rerun: false`·`--no-rerun` 은 미검증)
   - `changed_files` 가 비어 있지 않음(`HAS_CHANGE`) — 아무것도 바뀌지 않았다면 done 이 아니다
   - 가드 대상 행동에 승인 기록이 있고 그 기록이 원시 로그와 맞음(`GUARD_APPROVED`) — 승인 없는 가드가 있으면 재실행도 하지 않는다(K-66)
   - 패키지가 검토자를 요구하면 `review/` 의 결과 계약을 읽는다(M2부터). 판정은 산출물에 묶인다 — 검토자가 본 산출물은 봉투의 포인터가
     아니라 **검토 run 자신의 증거**(검토자를 띄운 쪽이 그 run 에 남긴 방어 검사의 `head_sha`+`dirty_tree_hash`)에서 읽고, 봉투의 `evidence_ref` 가
     가리킨 산출물은 그것과 같아야 한다(다르면 미검증). 지금 닫는 산출물과 같고 **지금의 승인**으로 낸 판정만 세고, 다른 산출물·재승인 전 승인의
     판정은 PASS 든 FAIL 이든 대상이 아니라고 인쇄한다(`REVIEW_SUPERSEDED`, 지우지 않는다). 현재 산출물의 봉투는 기록 명령이 남긴 해시 봉인과 같아야 한다.
     현재 산출물에 대한 판정 중 PASS 가 아닌 것이 하나라도 있으면 실패(`REVIEW_VERDICT`), 산출물을 확인할 수 없는 봉투가 있거나 PASS 가 하나도 없으면
     미검증 — 어느 쪽이든 완료가 아니다. PASS 가 1건뿐이면 `REVIEW_SAMPLE` 로 드러낸다(차단 여부는 D-75)
3. **상태 확정.** 통과하면 `status: done`, `closed_at` 기록, `evidence` 링크를 frontmatter 와 "증거" 절에 채운다.
4. **승격 후보 제안.** 장기 재사용할 사실이 있으면 `docs/current/` 승격 후보와 `decisions.md` 항목을 제안한다(M4).
   자동으로 쓰지 않는다.
5. **보고.** 통과/실패 항목, 미검증 항목, 남은 위험, 다음 우선 작업을 보고한다.

## 실패 처리

- 실패는 정상 경로다. 문서는 옮기지 않고 `status` 만 남긴다. 포기하면 `dropped`, 대체되면 `superseded`.
- stale 이면 다시 evidence 를 만든다. 검증 상태는 저장하지 않고 close 시점에 계산한다(D-15 보완).
