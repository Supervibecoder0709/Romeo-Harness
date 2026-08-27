---
id: chg-20260827-gitignore-harness-runs-mj9p
type: spec
title: 하네스 원시 로그·캐시를 git 에서 제외 (.gitignore)
unit: T0
mode: delivery
intent: write
facets: [tooling]
gates: []
profile: quick
blast_radius: small
uncertainty: low
status: active
approved_at: '2026-08-27T16:38:12+09:00'
approved_by: Supervibecoder0709
base_sha: bac8cffe8f7e11e90a3c47ba9303f460888ae92c
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T0=quick']
  history: []
created: '2026-08-27'
updated: '2026-08-27'
---
# 하네스 원시 로그·캐시를 git 에서 제외 (.gitignore)

> 깊이 **Quick** · 단위 T0 · 모드 delivery · 의도 write · 영역 tooling · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve chg-20260827-gitignore-harness-runs-mj9p` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 저장소에 `.gitignore` 를 추가해 하네스가 만드는 원시 로그(`.harness/runs/`)와 캐시(`.harness/cache/`)가 git 에 올라가지 않게 한다. Python 캐시(`__pycache__/`, `*.pyc`)와 macOS `.DS_Store` 도 함께 제외한다.
- **왜 지금:** M1 부터 `romeo evidence` 가 명령 로그를 `.harness/runs/` 에 쓴다. 제외 규칙이 없으면 로그가 커밋 후보로 잡히고, 작업 트리 신선도 계산도 흐려진다(K-24).
- **기대 결과:** `git status` 에 `.harness/runs/`·`.harness/cache/` 아래 파일이 나타나지 않는다. evidence yaml 에는 로그 경로와 해시만 남는다.
- **수용 기준:**
  - [ ] AC-1 `.harness/runs/` 아래 임의 경로가 `git check-ignore` 에서 무시 대상으로 판정된다
  - [ ] AC-2 `.harness/cache/` 아래 임의 경로가 `git check-ignore` 에서 무시 대상으로 판정된다
  - [ ] AC-3 기존 테스트 23개가 그대로 통과한다
- **위험과 되돌리기:** 위험 거의 없음. 되돌리기는 `.gitignore` 삭제 또는 `git revert <커밋>`.
- **결정 필요:** 없음

## Planning Capsule

T0는 기획 파일이 없다. 이 절(≤ 20줄)이 기획을 대신한다.

- **문제:** 하네스 원시 로그·캐시가 git 에 잡힌다. 제약 K-24 위반 상태.
- **대상·상황:** 이 저장소(Romeo 하네스 자체). M1 evidence 기록부터 실제로 발생.
- **기대 결과:** 제외 규칙이 커밋돼 새 clone·worktree 에서도 같은 위생이 유지된다(K-25).
- **범위 / 비범위:** `.gitignore` 1개 추가 / 기존 tracked 파일 변경 없음, `.harness/*.yaml` 상태 파일(M2, 커밋 대상)은 제외하지 않음.
- **가정:** Python·macOS 캐시 제외는 관례라 별도 승인 불필요.
- **열린 질문:** 없음

## 변경 범위

- 바뀌는 파일·모듈: `.gitignore` (신규)
- 영향을 받는 부분: `git status`, `romeo evidence` 의 untracked 계산(이미 `.harness` 를 제외하지만 git 수준에서도 제외)
- 바꾸지 않는 것(비범위): `.harness/romeo.project.yaml`·`bindings.yaml` 같은 상태 파일은 M2 에서 커밋 대상이므로 제외 규칙에 넣지 않는다

## 구현 단위

| # | 목표 | 변경 | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- |
| 1 | 제외 규칙 추가 | `.gitignore` 에 `.harness/runs/`, `.harness/cache/`, `__pycache__/`, `*.pyc`, `.DS_Store` | `git check-ignore -q <경로>` 가 exit 0 | 파일 삭제 또는 `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

```yaml
required_checks:
  - id: check-1
    command: "git check-ignore -q .harness/runs/probe/x.log"
    expect: exit 0
  - id: check-2
    command: "git check-ignore -q .harness/cache/probe"
    expect: exit 0
  - id: check-3
    command: "python3 -m unittest discover -s tests"
    expect: exit 0
```

## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
