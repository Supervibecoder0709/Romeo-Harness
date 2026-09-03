---
id: feat-20260903-guard-guidance-vendor-drift-bvjz
type: brief
title: 안내하는 자리가 요구하는 자리를 따라간다 — 가드 --note 안내 3곳·코어에 남은 집행 수단
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
created: '2026-09-03'
updated: '2026-09-03'
---

# 안내하는 자리가 요구하는 자리를 따라간다 — 가드 --note 안내 3곳·코어에 남은 집행 수단

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 창구는 Tech Spec 의 확인란 하나다(D-60). 이 문서는 승인 대상이 아니다.

## 한 줄 요약

가드 승인을 **요구하는 자리**(정책 파일)와 그것을 **안내하는 자리**(절차 문서 3곳)가 어긋나
지시대로 따른 실행이 `exit 2` 로 막힌다. 같은 파일에는 아무도 읽지 않는 집행 수단 사본이 남아
정본과 값까지 다르다. 두 어긋남을 닫고, 다시 벌어지지 않도록 검사로 묶는다.

## 배경과 대상

- **왜 지금:** M3 의 남은 조각은 실제 T2 관통이다. 관통이 시작되면 §10 동결 때문에 그 안에서
  하네스를 고칠 수 없으므로, 관통 경로에 놓인 안내 결함은 관통 **전에** 닫아야 한다.
  관통 사이의 하네스 정비 5회차다.
- **누구를 위한 것:** 절차 문서를 그대로 따르는 실행자(두 런타임 모두). 지금은 지시를 지킨 쪽이
  막히고, 지시를 무시하고 CLI 도움말을 읽은 쪽만 통과한다.
- **성공하면 무엇이 달라지나:** 가드 승인 명령을 안내하는 모든 자리가 요구와 같은 형식을 말한다.
  그리고 그 일치가 사람의 성실함이 아니라 **검사**로 유지된다 — 라벨이 바뀌면 검사가 먼저 깨진다.

## 방향

- **하려는 것:** (1) 가드 승인·거부를 안내하는 절차 문서 3곳이 `--note` 를 요구와 같은 형식으로
  안내하게 한다. (2) `core/policy/execution-guards.yaml` 의 최상위 `enforcement:` 블록을 걷어낸다 —
  읽는 코드가 없고 값이 정본과 다르며 런타임 이름이 코어에 남는 자리다(C-C6).
  (3) 두 어긋남을 각각 겨누는 검사를 같은 커밋에 넣는다(§11).
- **하지 않는 것:** 코어 전체의 런타임 이름 정리. 실측하니 `core/` 7파일에 이름이 있고 다수는
  정당한 언급이다(설명문·출처 기록·파일명). 단순 grep 확대는 정당한 언급까지 막는다 — 별도 질문으로 연다.
  `adapters/orca/RUNBOOK.md` 도 고치지 않는다. 이미 새 형식이고 어긋난 자리가 아니다.
- **전달 메시지:** 요구를 적은 곳과 안내하는 곳이 다르면, 규칙을 지킨 사람이 막힌다.

## 열린 질문

- `core/` 의 나머지 런타임 이름(6파일)을 어떻게 다룰지 — 정당한 언급과 위반을 구분하는 기준이 없다.
  이 단위의 범위 밖이며 결과 보고에서 `open-questions.md` 에 새 항목으로 연다(§12).


## 연결

Tech Spec 은 같은 폴더의 `spec.md` 다. 수용 기준·검증 계획·증거는 그쪽이 원본이며 여기에 옮겨 적지 않는다(K-61).
외부 산출물은 본문 링크가 아니라 frontmatter 의 `inputs:` 로만 붙인다(K-62).
