---
id: chg-20260827-rg-fallback-validate-245m
type: spec
title: validate-repo-archive.sh 에 grep -E 폴백 추가
unit: T0
mode: delivery
intent: write
facets: [tooling]
gates: []
profile: quick
blast_radius: small
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
  fired_rules: ['profile:base:T0=quick']
  history: []
created: '2026-08-27'
updated: '2026-08-27'
---
# validate-repo-archive.sh 에 grep -E 폴백 추가

> 깊이 **Quick** · 단위 T0 · 모드 delivery · 의도 write · 영역 tooling · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve chg-20260827-rg-fallback-validate-245m` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 아카이브 검증 스크립트가 `rg`(ripgrep) 없는 환경에서도 같은 검사를 하도록 `grep -E` 폴백을 넣는다. `rg` 가 있으면 그대로 `rg` 를 쓴다.
- **왜 지금:** 이 머신의 `rg` 는 정식 설치가 아니라 ChatGPT 앱 번들 바이너리뿐이고, Orca 워커 셸에서는 `command not found` 로 검증이 깨진 적이 있다(메모리 기록). M2 에서 Codex·Orca 워커가 이 스크립트를 실행해야 한다.
- **기대 결과:** `rg` 가 없는 PATH 에서도 `bash scripts/validate-repo-archive.sh archive/obra-superpowers` 가 PASS 하고, 깨진 아카이브(SHA 줄 훼손)는 여전히 FAIL 한다.
- **수용 기준:**
  - [ ] AC-1 `rg` 가 있는 기본 PATH 에서 obra-superpowers 아카이브 검증이 PASS
  - [ ] AC-2 `rg` 가 없는 PATH(`/usr/bin:/bin`)에서 같은 검증이 PASS
  - [ ] AC-3 `rg` 가 없는 PATH 에서 SHA 줄을 훼손한 사본은 FAIL (폴백이 실제로 검사한다)
- **위험과 되돌리기:** 검증 스크립트만 바뀌므로 아카이브·CI 에 영향 없음. 되돌리기는 `git revert <커밋>`.
- **결정 필요:** 없음

## Planning Capsule

T0는 기획 파일이 없다. 이 절(≤ 20줄)이 기획을 대신한다.

- **문제:** K-20("rg + 스크립트")의 전제가 `rg` 정식 설치에 기대고 있는데 실제 환경에는 없다.
- **대상·상황:** `scripts/validate-repo-archive.sh` 의 `rg -q` 호출 2곳(_source.md SHA, 04-components-table.md 원문 위치 열).
- **기대 결과:** `rg` 유무와 무관하게 같은 판정. ripgrep 정식 설치(`brew install ripgrep`)는 권고로만 남긴다.
- **범위 / 비범위:** 스크립트 1개의 매칭 함수 / 검사 규칙·정규식 의미는 바꾸지 않음, 다른 스크립트 미변경.
- **가정:** 두 정규식은 ERE 로 동일하다(백틱은 리터럴, `{40}` 간격, `|` 대안).
- **열린 질문:** 없음

## 변경 범위

- 바뀌는 파일·모듈: `scripts/validate-repo-archive.sh` — 매칭 함수 `matches()` 추가, `rg -q` 2곳을 `matches` 호출로 교체
- 영향을 받는 부분: `/repo` 파이프라인의 회수 검증, M2 Orca 워커 검증
- 바꾸지 않는 것(비범위): 검사 항목·정규식 의미, `generate-archive-index.py`, CI 워크플로

## 구현 단위

| # | 목표 | 변경 | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- |
| 1 | 폴백 함수 | `command -v rg` 가 있으면 `rg -q`, 없으면 `grep -Eq` 를 쓰는 `matches()` 정의 | PATH 제한 실행 PASS + 훼손 사본 FAIL | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

```yaml
required_checks:
  - id: check-1
    command: "bash scripts/validate-repo-archive.sh archive/obra-superpowers"
    expect: exit 0
  - id: check-2
    command: "env PATH=/usr/bin:/bin bash scripts/validate-repo-archive.sh archive/obra-superpowers"
    expect: exit 0
  - id: check-3
    command: "t=$(mktemp -d) && cp -R archive/obra-superpowers/. \"$t\" && sed -i '' 's/^- Commit SHA:/- Commit XXX:/' \"$t/_source.md\" && ! env PATH=/usr/bin:/bin bash scripts/validate-repo-archive.sh \"$t\""
    expect: exit 0 (검증기가 FAIL 해야 통과)
```

## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
