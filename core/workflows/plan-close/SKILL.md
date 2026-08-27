---
name: plan-close
description: 작업 단위를 종료한다. 문서 스키마·링크·미체크 수용 기준·길이 예산·open loop·evidence 신선도(HEAD SHA·작업 트리 해시)·required_checks 를 검사해 통과하면 status 를 done 으로 확정한다. 사용자가 "/plan-close", "이 작업 마무리해", "완료 처리해줘"라고 할 때 사용한다. 검사가 실패하면 완료라고 하지 않는다.
provenance: []
---

# romeo:plan-close — 검증 → 상태 확정 → 승격 후보

"만들었다"를 "검증했다"로 바꾸는 유일한 장치다. 실행 자체는 완료가 아니다(K-51).

## 절차

1. **증거 확인.** `docs/work/<id>/evidence/*.yaml` 이 최소 1건 있어야 한다. 없으면 close 는 `NO_EVIDENCE` 로 실패한다.
   증거는 `romeo evidence run --unit <id> -- <명령>` 으로만 만든다. 손으로 쓰지 않는다.
2. **검사 실행.** `romeo close --unit <id>` 는 아래를 순서대로 검사한다. 하나라도 실패하면 상태를 바꾸지 않는다.
   - frontmatter 스키마 유효, `status: active`, `approved_at` 존재
   - 수용 기준 체크박스가 전부 `[x]` (미체크가 있으면 `UNCHECKED_AC`)
   - `NEEDS_INPUT` 잔존 0 (`OPEN_LOOP`), 길이 예산 이내(`BUDGET_EXCEEDED` 는 경고)
   - 문서 안 상대 링크가 실제 파일을 가리킴(`BROKEN_LINK`)
   - evidence 의 `head_sha` 가 현재 `git rev-parse HEAD` 와 같고 `dirty_tree_hash` 가 현재 작업 트리와 같음
     — 다르면 `STALE_EVIDENCE`. 커밋 이동·tracked 수정·staged 변경·untracked 추가 네 경우 모두 거부한다
   - spec 의 `required_checks` 명령이 evidence 의 `commands` 에 exit 0 으로 존재(`MISSING_CHECK`)
   - `changed_files` 가 비어 있지 않음(`NO_CHANGE`) — 아무것도 바뀌지 않았다면 done 이 아니다
   - 패키지가 검토자를 요구하면 `review/` findings 존재(M2부터)
3. **상태 확정.** 통과하면 `status: done`, `closed_at` 기록, `evidence` 링크를 frontmatter 와 "증거" 절에 채운다.
4. **승격 후보 제안.** 장기 재사용할 사실이 있으면 `docs/current/` 승격 후보와 `decisions.md` 항목을 제안한다(M4).
   자동으로 쓰지 않는다.
5. **보고.** 통과/실패 항목, 미검증 항목, 남은 위험, 다음 우선 작업을 보고한다.

## 실패 처리

- 실패는 정상 경로다. 문서는 옮기지 않고 `status` 만 남긴다. 포기하면 `dropped`, 대체되면 `superseded`.
- stale 이면 다시 evidence 를 만든다. 검증 상태는 저장하지 않고 close 시점에 계산한다(D-15 보완).
