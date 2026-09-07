---
id: feat-20260907-judge-revision-base-sha-pwt8
type: brief
title: 종료 검사는 base_sha 시점의 하네스가 낸다 — 규칙을 만든 단위가 자기 규칙으로 닫히지 않는다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: low
status: draft
approved_at: null
approved_by: null
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-07'
updated: '2026-09-07'
---

# 종료 검사는 base_sha 시점의 하네스가 낸다 — 규칙을 만든 단위가 자기 규칙으로 닫히지 않는다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

close 를 base_sha 스냅샷의 bin/romeo 가 --root 로 돌리고, 판정 하네스가 그 리비전이 아니면 JUDGE_REVISION 으로 거부한다

## 배경과 대상

- **왜 지금:** 2026-09-07 진단이 자가봉착의 뿌리를 「판정하는 하네스와 판정받는 하네스가 같은 리비전」으로 지목했고(권고 1),
  D-81 이 그 처방을 M5 보다 앞에 두었다 — 선행 ①(Q-66·Q-67)은 닫혔다. 실측 사례가 Q-43 이다(검토자를 끄는 오버레이를
  추가한 단위가 그 오버레이에 걸려 검토 없이 닫혔다). 관통 도중에는 하네스를 고칠 수 없으므로(§10 동결) 관통 사이인 지금 닫는다.
- **누구를 위한 것:** 하네스 자신을 고치는 정비 단위를 닫는 사람 — 관통을 위임하고 결과를 회수하는 코디네이터(RUNBOOK §3.8),
  그리고 그 판정을 읽는 검토자·다음 세션. 남의 저장소를 닫는 사람에게는 아무것도 달라지지 않는다.
- **성공하면 무엇이 달라지나:** 종료 검사를 낸 하네스가 어느 리비전인지 판정 자체가 말한다(`JUDGE_REVISION`). 하네스를 바꾼 단위는
  승인 커밋 스냅샷의 `bin/romeo` 로만 닫히고, 자기 트리의 `bin/romeo` 로 닫으려 하면 어느 파일이 다른지와 함께 거부된다.
  새 규칙은 다음 단위부터 적용된다 — 이 단위 자신이 자기적용의 마지막 라운드다(D-81).

## 방향

- **하려는 것:** `romeo/close.py` 에 검사 `JUDGE_REVISION` 을 더한다 — 판정 대상의 승인 커밋 트리에 `romeo/__init__.py` 가 있으면
  (하네스 저장소 자신) 그 트리의 `docs/` 밖 추적 파일 전부가 판정을 낸 하네스의 같은 경로와 blob 해시로 같아야 PASS. 절차 문서 셋
  (plan-close 절차 · RUNBOOK §3.8/§3.1 · 두 런타임의 plan-close 매핑)을 「승인 커밋을 `git archive` 로 꺼낸 스냅샷의
  `bin/romeo close --root <구현 워크트리>`」로 같은 변경에서 바꾼다(§11). 판별 검사 6건을 더하고 Q-43 을 닫는다.
- **하지 않는 것:** 판정 루트가 git 이어야 한다는 요구(리비전 번호 대조)는 두지 않는다 — 스냅샷·워크트리·clone 을 한 기준(내용)으로
  판정한다. 더해진 파일은 보지 않는다(판정이 읽는 파일은 이름이 고정돼 있다). `envelope check`·`evidence checks` 가 어느 하네스로
  도는지는 손대지 않고 열린 질문으로 남긴다. AGENTS.core §10 동결·반복 중단은 D-81 대로 유지한다. `format_close` 첫 줄·다른
  검사 id·문장은 바꾸지 않는다. Q-23·34·35·64·69·70·71~82 는 이 단위에서 고치지 않는다(§12).
- **전달 메시지:** 판정하는 하네스는 승인 시점의 하네스다. 규칙을 바꾸는 단위는 바뀐 규칙 아래에서 닫히지 않고, 새 규칙은
  다음 단위부터 적용된다 — 컴파일러 부트스트랩과 같은 구조다. 판별은 승인 전 프로브가, 판정은 옛 리비전이 맡는다.

## 열린 질문

- 없음


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
