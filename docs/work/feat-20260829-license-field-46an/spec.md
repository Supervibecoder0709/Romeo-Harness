---
id: feat-20260829-license-field-46an
type: spec
title: 아카이브 스키마에 라이선스 필드 추가
unit: T1
mode: delivery
intent: write
facets: [docs, tooling]
gates: []
profile: standard
blast_radius: medium
uncertainty: low
status: active
approved_at: '2026-08-29T01:19:27+09:00'
approved_by: Supervibecoder0709
base_sha: 9d181a55095e3db36ad4aab5884bf91369d0bed1
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-08-29'
updated: '2026-08-29'
---

# 아카이브 스키마에 라이선스 필드 추가

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 docs, tooling · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260829-license-field-46an --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** 아카이브 스키마에 라이선스를 1급 필드로 넣는다 — `_source.md` 헤더에 `- License:` 줄, 검증 스크립트가 그 줄을 검사, 인덱스 표에 라이선스 열, 기존 아카이브 18개 전부 backfill.
- **왜 지금:** 지금은 18개 중 3개만 본문 어딘가에 라이선스를 언급하고, 헤더 필드로는 0개다. 부품을 가져올 때 라이선스를 매번 GitHub API로 다시 조회해야 하고(K-40~K-42가 요구하는 추적), 아카이브만 보고는 재사용 가능 여부를 알 수 없다. 값은 이미 `docs/planning/implementation-plan.md` §1.3에서 API와 고정 SHA 실물 대조로 확인해 두었다.
- **기대 결과:** `archive/<이름>/_source.md` 를 열면 헤더 5줄째에 라이선스가 보이고, `archive/README.md` 표에 라이선스 열이 생기며, 라이선스 줄이 없는 새 아카이브는 `validate-repo-archive.sh` 가 FAIL 시킨다.
- **수용 기준:**
  - [ ] AC-1 `archive/*/_source.md` 18개 전부에 `- License: <값>` 줄이 있고, 값이 계획 §1.3 표와 일치한다
  - [ ] AC-2 라이선스 줄이 없는 아카이브 사본은 `validate-repo-archive.sh` 가 FAIL 한다 (검사가 실제로 동작한다)
  - [ ] AC-3 `archive/README.md` 목록 표에 라이선스 열이 있고 `generate-archive-index.py --check` 가 PASS 한다
  - [ ] AC-4 기존 하네스 테스트가 그대로 통과한다 (회귀 없음)
- **위험과 되돌리기:** 문서와 검증 스크립트만 바뀐다. 운영 데이터·외부 상태·CI 권한은 건드리지 않는다. 되돌리기는 `git revert <커밋>` 하나. 잘못된 라이선스 값을 적는 것이 유일한 실질 위험이고, 근거를 계획 §1.3 한 곳으로 고정해 대조 가능하게 둔다.
- **결정 필요:** 없음

## 변경 범위

- 바뀌는 파일·모듈: `archive/*/_source.md` 18개(헤더 1줄 추가) · `scripts/validate-repo-archive.sh`(검사 1개 추가) · `scripts/generate-archive-index.py`(`collect` 에 license 추출, `render` 표에 열 추가) · `archive/README.md`(생성물, 재생성)
- 영향을 받는 부분: `/repo` 아카이브 파이프라인의 회수 검증 · CI `.github/workflows/archive-index.yml` 의 stale 검사
- 바꾸지 않는 것(비범위): 아카이브 본문(`00`~`06`, `01-docs/`, `03-components/`) · `THIRD_PARTY_NOTICES.md` 와 `provenance/imports.yaml`(vendor 채택물의 라이선스는 그쪽이 원본이고 여기는 아카이브 스키마다) · `.github/workflows/` 파일 자체 · `core/` 정책표

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 헤더 필드 backfill | `archive/*/_source.md` 18개의 `- Analysis timestamp:` 줄 **앞**에 `- License: <SPDX 또는 실물 이름>` 을 넣는다. 값은 `docs/planning/implementation-plan.md` §1.3 표 그대로 — 그 표의 "라이선스" 열에 API 값과 실물이 다르게 적힌 항목은 **실물** 값을 쓴다 | 소비: 계획 §1.3 표 → 생산: `- License:` 헤더 필드 18개 | `grep -c '^- License: ' archive/*/_source.md` 가 18줄 모두 1 | `git revert` |
| 2 | 검증 스크립트 검사 | `scripts/validate-repo-archive.sh` 에 `matches '^[-*] License: .+$'` 검사를 Commit SHA 검사 뒤에 추가하고, 실패 메시지는 기존 형식(`FAIL: _source.md ...`)을 따른다. `matches()` 폴백을 그대로 쓴다 | 소비: 1번의 헤더 필드 → 생산: 검사 1개 | 정상 아카이브 PASS · License 줄을 지운 사본 FAIL | `git revert` |
| 3 | 인덱스 열 | `scripts/generate-archive-index.py` 의 `collect()` 반환 dict 에 `license` 키를 추가한다 — 값은 기존 `field(src, "License")` 로 뽑아 백틱을 제거하고 공백을 다듬은 것, 비면 em dash. `render()` 의 목록 표는 헤더와 각 행 모두 `고정 커밋` 다음 `분석일` 앞에 라이선스 칸을 넣고, 값은 파이프 이스케이프 함수 `cell()` 을 거친다. 생성 시각을 넣지 않는 결정성은 유지한다 | 소비: 1번의 헤더 필드 → 생산: README 표의 라이선스 열 | `python3 scripts/generate-archive-index.py` 후 `--check` PASS | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조하고, 같은 명령을 그 체크아웃에서 **다시 실행**해 종료 코드를 맞춰 본다. 아래 넷은 모두 재실행해도 결론이 같고 작업 트리를 바꾸지 않는다.

```yaml
required_checks:
  - id: check-1
    command: "bash scripts/validate-repo-archive.sh archive/obra-superpowers"
    expect: exit 0
  - id: check-2
    command: "test \"$(grep -l '^- License: ' archive/*/_source.md | wc -l | tr -d ' ')\" = \"$(ls -d archive/*/ | wc -l | tr -d ' ')\""
    expect: exit 0
  - id: check-3
    command: "t=$(mktemp -d) && cp -R archive/obra-superpowers/. \"$t\" && grep -v '^- License: ' \"$t/_source.md\" > \"$t/_source.tmp\" && mv \"$t/_source.tmp\" \"$t/_source.md\" && ! bash scripts/validate-repo-archive.sh \"$t\""
    expect: exit 0 (License 줄이 없으면 검증기가 FAIL 해야 통과)
  - id: check-4
    command: "python3 scripts/generate-archive-index.py --check"
    expect: exit 0
  - id: check-5
    command: "python3 -m unittest discover -s tests"
    expect: exit 0
```

## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
