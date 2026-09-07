---
id: feat-20260908-ac-rebuttal-before-approval-2sct
type: brief
title: 승인 전 반대 독자 — 확인란의 수용 기준을 다른 런타임이 반박하고, 전칭 표현은 검사기가 경고한다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
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
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-08'
updated: '2026-09-08'
---

# 승인 전 반대 독자 — 확인란의 수용 기준을 다른 런타임이 반박하고, 전칭 표현은 검사기가 경고한다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.
> **착수 시점:** `feat-20260907-context-one-hop-resume-w5jq` 관통이 닫힌 뒤 — 정비 후보 순서의 맨 앞(사용자 지시 2026-09-08).

## 한 줄 요약

승인 요청 앞에 다른 런타임이 확인란의 AC 를 반례로 읽고(`inputs/ac-rebuttal-<날짜>.md`), `validate` 는 전칭 표현을 · `approve` 는 반박 누락을 경고한다 — 경고까지만

## 배경과 대상

- **왜 지금:** 최근 15개 단위 중 1회차에 닫힌 것은 3개(z5mv·wr9m·erc6)다. 1회차 FAIL 의 과반은 산출물이 아니라 **AC 문장의 결함**이었다 —
  과잉 명세(pwt8 AC-3), 검토 시점에 참일 수 없는 명제(rshi AC-2·q3wy AC-2), 반대 판정(w7tm AC-4), 확인란의 대상 고정(ct5h), 전칭 문장(w5jq AC-5 · 2회 연속).
  전부 D-80 재승인이나 재작업으로만 닫혔고 회차 하나(25~40분)가 매번 그 대가였다. 그 문장을 반대 입장에서 처음 읽는 사람이 검토자인데 그 자리는 구현 **뒤**다.
  승인 전 프로브는 검사의 판별력만 양쪽 실측하지 문장은 실측하지 않는다. 같은 손(코디네이터)이 AC·프로브·조율을 다 쓰므로 같은 사각지대가 세 번 복제된다.
  z5mv 는 승인 전에 「세 렌즈 반박」을 손으로 해 1회차에 닫혔지만, 절차도 기록 자리도 없어 재현되지 않았다.
- **누구를 위한 것:** 확인란을 쓰는 라우터 세션과 그것을 승인하는 사람. 검토자에게는 산출물 결함만 남는다.
- **성공하면 무엇이 달라지나:** 승인 직전에 AC 마다 반례·검토 시점·표현 세 줄이 붙은 파일이 서고, 고친 문장이 「반영」 절에 남는다. 전칭 표현은 쓰는 순간 경고로 보이고,
  반박이 빠진 AC 는 승인 시점에 이름으로 보인다. 효과(1회차 통과율)는 그 뒤 10개 단위의 관측이 말한다 — 이 단위는 자리를 만들 뿐이다.

## 방향

- **하려는 것:** `/plan` 절차에 「반박 읽기」 단계(내용 채우기 뒤·승인 요청 앞) · 브리프 정본 `adapters/orca/prompts/ac-rebuttal-brief.md` · 두 런타임 매핑에 반박 실행 한 줄 ·
  정책표 `packages.yaml` 에 `ac_lint`(전칭 패턴·기록 경로 접두)와 경고 카탈로그 2 코드 · `validate` 의 `AC_UNIVERSAL` · `approve` 의 `AC_UNREBUTTED` · 판별 검사 3 클래스 ·
  이 단위 자신이 첫 실사용(승인 전 반박 파일 등록). §11 의 셋(어느 사건·어느 문서·무엇이 참이어야)을 같은 커밋에서 정한다 — 사건은 `validate`(쓰는 시점)와 `approve`(승인 시점),
  문서는 확인란 AC 항목과 `inputs:` 의 반박 파일, 충족은 패턴 없음·AC 마다 절 있음.
- **하지 않는 것:** 승인을 **막지 않는다** — 경고까지만이다(K-31 · charter M4 위험 「드러내기가 차단으로 자라는 것」). 차단으로 올리는 것은 10건 관측 뒤 별도 결정.
  반박은 판정을 내지 않는다(PASS/FAIL 없음 — 승인은 사람의 몫, K-61). 산출물 결함을 잡지 않는다 — 그것은 검토자의 몫이다. 승인 전 프로브·검토자 절차·close 는 건드리지 않는다.
  코어에 도구명·모델명을 쓰지 않는다 — 어느 런타임이 반박하는지는 어댑터 매핑이 정한다(C-C6).
- **전달 메시지:** 「완료 정의는 쓰는 사람이 아닌 사람이 먼저 반례를 든다 — 구현 뒤가 아니라 승인 앞에서.」

## 열린 질문

- 전칭 패턴의 거짓 양성률 — 닫힌 집합을 명시한 문장(「A·B·C 셋 전부」)이 걸릴 수 있다. 경고라 막지 않고, 착수 후 관측으로 목록을 다듬는다.
- 반박 실행의 비용(5분 가정)과 T0 단위에도 절차를 요구할지 — 착수 시 첫 실행에서 실측하고 정한다.
- 경고를 차단(`blocks` 의 `ac-rebutted`)으로 올리는 조건 — 이 단위 밖. 10건 관측 뒤 결정 등록.


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
