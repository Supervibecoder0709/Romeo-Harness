# 리뷰 의뢰 — Romeo 하네스 M2 (G-M2 게이트 ~ 어댑터 컴파일)

당신은 이 저장소를 처음 보는 **독립 검토자**다. 구현자(Claude)가 스스로 통과시킨 검사만 믿지 말고,
검사 자체가 틀렸을 가능성부터 의심해라. 칭찬은 쓰지 마라. 발견한 문제만 써라.

## 이 저장소가 무엇인가

여러 프로젝트에 붙일 **AI 작업 하네스**다. 핵심은 라우터(요청 분류 → 필요한 문서만 생성) +
접착(문서·상태·증거) + **동등성**(Claude가 구현하고 Codex가 리뷰하며, 역할을 바꿔도 같은 판정).

- 벤더 중립 원본은 `core/`, 런타임별 산출물은 `romeo compile` 이 만든다.
- 외부 부품은 `vendor/` 에 원문 그대로(수정 0) 담고 `provenance/imports.yaml` 로 추적한다.
- 규칙 체계: `docs/requirements/constraints.md` 의 **K-60~K-69 통합 규약**,
  `docs/decisions/decision-register.md` 의 **D-01~D-71 결정**, `docs/planning/implementation-plan.md` 의 계획.

## 리뷰 대상

커밋 범위 `fe27ff5..HEAD` (6개). 특히:

| 영역 | 파일 |
| --- | --- |
| 채택 게이트 결정 | `provenance/imports.yaml`, `docs/decisions/decision-register.md` D-67~D-71 |
| 외부 부품 원문 | `vendor/obra-superpowers@b36e082/` (15파일, 수정 0이어야 함) |
| 출처 검증 | `romeo/provenance.py`, `tests/test_provenance.py` |
| 어댑터 컴파일 | `romeo/compile.py`, `tests/test_compile.py`, `adapters/`, `core/principles/AGENTS.core.md`, `.harness/bindings.yaml` |
| 산출물 | `CLAUDE.md`·`AGENTS.md` 의 `romeo:managed` 블록, `.claude/skills/**`, `.agents/skills/**`, `.claude/settings.json` |
| CI | `.github/workflows/harness.yml` |

## 반드시 확인할 것 (구현자가 스스로 못 본 곳일 가능성이 높다)

1. **규약 위반.** `constraints.md` K-60~K-69 를 실제 산출물과 하나씩 대조해라.
   특히 K-60(진입점 단일)·K-62(산출물 흡수)·K-63(상태 소유권)·K-64(네임스페이스)·K-66(권한 상한).
   `vendor/` 에 넣은 superpowers 7종의 **본문 지시**와 `CLAUDE.md` managed block 의 Romeo 규칙이
   충돌하는 지점을 찾아라. 구현자는 4건만 override 로 적었다 — **빠진 충돌이 더 있는지** 원문을 읽고 확인해라.
   `vendor/obra-superpowers@b36e082/skills/*/SKILL.md` 전문을 실제로 읽어라.

2. **검사기의 구멍.** `romeo compile --check`·`romeo vendor check`·`romeo notices --check` 가
   **통과시키면 안 되는데 통과시키는 상태**를 찾아라. 구현자는 심링크 케이스를 뒤늦게 발견했다.
   같은 종류의 빈틈이 더 있는지 봐라 — 파일 권한, 대소문자, 개행, 빈 디렉터리, 부분 실패,
   `plan_outputs` 가 디스크를 읽어 만드는 `_render_settings` 의 순환성, `check` 와 `compile` 의 비대칭.

3. **컴파일 정확성.** `replace_managed_block` 의 정규식이 잘못 잡는 입력이 있는가?
   (중첩 마커, 마커가 여러 개, 마커 안에 `-->`, 코드펜스 안의 가짜 마커, CRLF, 마커 없는 파일 끝 공백)
   idempotent 가 실제로 보장되는가? `compiled.yaml` 의 고아 검출이 실제로 동작하는가?

4. **결정과 구현의 불일치.** D-67~D-71 과 `provenance/imports.yaml` 과 실제 파일 상태가 서로 맞는가?
   `imports.yaml` 의 `local_overrides` 와 `.harness/bindings.yaml` 의 `overrides` 가 **두 벌의 진실**이
   되어 있지 않은가? 어느 쪽이 원본인지 문서가 말하는가?

5. **테스트가 증명하지 못하는 것.** `tests/test_compile.py`·`test_provenance.py` 가 통과해도
   깨질 수 있는 시나리오를 구체적으로 제시해라. 테스트가 구현을 그대로 베낀 곳(동어반복)이 있는가?

6. **계획 대비 누락.** `docs/planning/implementation-plan.md` §7 의 M2 "만들 것"·"검증" 목록과
   실제 결과물을 대조해 **아직 없는데 있다고 말하는 것**이 있는지 찾아라.

## 출력

`REVIEW_FINDINGS.md` 파일 하나로 써라. 형식:

```markdown
# Codex 독립 리뷰 — M2

## 요약
(3줄 이내. 가장 심각한 것부터)

## 발견
### F-01 <한 줄 제목>
- **심각도:** Critical | Important | Minor
- **위치:** `파일:줄`
- **무엇이 잘못됐나:** (사실만)
- **왜 문제인가:** (어떤 상황에서 실제로 깨지는가 — 구체적 시나리오)
- **근거:** (읽은 파일·줄, 실행한 명령과 출력)
- **제안:** (고치는 방향 한두 줄. 코드를 다시 쓰지는 마라)

## 확인했으나 문제 없음
(무엇을 봤고 왜 괜찮은지 한 줄씩. 안 본 것을 봤다고 쓰지 마라)

## 확인하지 못한 것
(시간·권한·환경 때문에 못 본 영역을 정직하게)
```

## 규칙

- **파일을 고치지 마라.** `REVIEW_FINDINGS.md` 만 쓴다. 커밋·푸시하지 마라.
- 추측을 사실처럼 쓰지 마라. 읽지 않은 파일에 대해 단정하지 마라.
- 명령을 실행해 확인할 수 있는 것은 실행해라 (`python3 -m unittest discover -s tests`,
  `bin/romeo compile --check`, `bin/romeo vendor check` 등). 실행한 명령과 출력을 근거에 남겨라.
- 심각도를 부풀리지 마라. 진짜 깨지는 것만 Critical 이다.
- 한국어로 써라.

다 쓰면 마지막 줄에 `REVIEW_DONE` 이라고 출력해라.
