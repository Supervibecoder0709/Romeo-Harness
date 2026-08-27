---
id: assembly-redefinition-20260827
type: decision_register
status: active
updated: 2026-08-27
authority: canonical
---

# 부품 조립 재정의 — 개정 3 기록 (2026-08-27)

> PM용 브리프: [summary.html](summary.html) · 반영된 계획: [implementation-plan.md](../../planning/implementation-plan.md) §6·§12

## 한 문장

Romeo는 **사용자가 직접 써보고 검증한 하네스들을 부품으로 그대로 두고**, 그 앞에서 요청을 이해해 어떤 부품을 어떤 깊이로 어떤 순서로 쓸지 정하고, 부품 사이의 산출물·상태·증거를 하나의 문서 체계로 이어 주며, Claude Code와 Codex 어느 쪽에서 실행해도 같은 판정이 나오게 하는 **개인용 라우터**다. 부품을 다시 만드는 프로젝트가 아니다.

## 사용자 발화 (2026-08-27, 이 세션 — 인용 키 `REDEF-0827`)

1. "개발 하네스는 superpower 모티브, 기획 하네스는 bmad cis, 개발 문서 관리 유지는 open wiki, 디자인은 여러 레포에서 스킬 추출해서 시스템화 … 이 부분은 다 원본 레포에서 원칙만 가져오게 되어 있는 것 같아. 이 중에서는 내가 실제로 사용해보고 정말 좋았던 워크플로우들도 있어서, 해당 레포지토리에 포함된 에이전트와 스킬을 그대로 사용하고 싶은 부분들도 있는데"
2. "사실 나는 내가 잘 썼던 하네스들을 **조립**해서 **나만의 라우터 체계**로 구축하고 싶은 거야."
3. "레포지토리에서 정확하게 뭘 가져올 건지는 해당 구현 단계가 됐을 때 나한테 다시 물어서 구체화 하는 방식으로 구현할 수 있어?"
4. "이 기획에서 가장 중요한 건 내가 원하는 체계를 구축하면서도 각 레포 추출물들이 충돌하지 않고 하나의 시스템에 잘 녹아드는 거야."

## 원천 대화 25건 재독 결과 — 이 정의의 근거

사용자 발화만 추출(참조 ChatGPT 대화 속 질문 포함, 상용구·이미지 제거 후 약 9만 자)해 전부 읽었다.

| 묶음 | 사용자 원문 (세션) | 정의에서의 자리 |
| --- | --- | --- |
| 라우터 | "어떤 bmad 워크플로우가 필요한지 자동으로 추천 … 난이도·크기를 분류한 다음 어느 수준의 기획이 필요한지 판단" (S01); "모든 기획에 동일한 포맷의 기획서가 필요하지 않다" (S09) | **목적** |
| 부품과 경계 | "bmad는 내가 써본 기획 하네스 중 가장 정교 … **딱 기획의 범위까지만** 카피" (S01); "superpower의 개발 방법론" (S01); "기획 하네스 별도 운영하면서 생성된 코드 결과물을 자동 관리 … 나는 기획과 명세에 집중" (S12, OpenWiki); "UI UX 전문가·랜딩 크리에이터·AI slop 안티패턴" (S01); "**한 패키지로 묶어 어떤 프로젝트에서나 공용으로 쓸 모듈**" (S12) | **조립 대상** |
| 접착 | "모든 문서에 작성일·업데이트·상태값(draft/진행중/SSOT)" (S01); "PRD와 ADR 구분" (S01); "SSOT 계층 확립 → 생성 → 작업 → 검증 루프" (S01); "산출물을 어떻게 저장·관리할지" (S09) | **Romeo가 만드는 것** |
| 동등성·모델 | "orca 위에서 codex와 claude가 동일한 워크플로우" (S01); "공통 워크플로우 + 명시적 선택 → 제한적 자동" (S01 참조 대화); "역할 난이도에 따라 모델 직접 선택" (S01) | **조건** |
| 운영 원칙 | persona 지시문(결론 먼저·사실/가정/추천·위험 승인·실행≠완료); 쿠팡 34건 마이그레이션 지시 "게이트 통과 시 재승인 없이 계속 … 증거와 함께 보고" (S07/08); 교육 웹앱 프롬프트 "확인 못 하면 미검증" (S20) | **모든 부품에 적용** |

S01(2026-08-04)의 계획 책임표가 이미 이 정의였다: BMAD·Superpowers·OMA·Orca는 각자 담당, **자체 하네스 = 라우팅·문서 상태·SSOT·모델 정책·도구 레지스트리·자기개선**. 3주간 규모(역할 수·인프라)는 줄었지만 "조립"이라는 성격은 바뀐 적이 없다.

## 정본이 어긋난 지점 세 가지와 원인

1. **부품이 "능력 후보"로 강등됐다.** `conversation-coverage.md` 정규화 원칙 2("도구 이름을 요구로 해석하지 않았다")를 부품에까지 적용해 X-03이 기획 코어를 자체 정책표로 정하고 BMAD를 v2로 밀었다. 사용자의 "딱 기획 범위까지만 카피"는 대체가 아니라 경계 설정이었다.
2. **조건이 목적 자리에 앉았다.** v1-scope "유일한 합격 기준 = 역할 교체 재현"은 S01 08-05 Codex 리뷰가 제안한 v0.1 기준이다. 라우터가 없는 동등성은 증명할 대상이 없다. 계획은 부품 조립을 M6·v2로 가장 뒤에 두었다.
3. **접착만 남고 부품이 빠졌다.** Thin Policy-Compiled Planning Spine은 정확히 "라우터 + 접착"인데, 그 척추가 무엇을 라우팅하는지(부품)가 능력 지도에 없었다. 그래서 계획 §6이 자연스럽게 "전부 원칙만 참고"가 됐다.

원인: 8/4~8/23 조사 세션마다 각 부품에 "설치만으로는 효과 보장 없음, 정적 분석뿐, hook·런타임 종속 주의"라는 보수적 결론이 나왔고, 정규화 때 그 보수성이 "능력 강등"으로 굳었다. 그 사이 **부품을 실제로 써본 사용자의 경험**(BMAD v6.0.4·v6.10.0+CIS, UI UX Pro Max v2.2.3 — `~/readly-sologis`, `~/bmad-ordi`)은 요구로 승격되지 않았다. council(`docs/council/03`)은 BMAD·Superpowers·OpenWiki를 한 번도 언급하지 않았고, Codex 리뷰(F-01~F-08)도 §6을 다루지 않았다.

## "원칙만"으로 판단했던 근거 7가지의 재평가

| # | 근거 | 재평가 |
| --- | --- | --- |
| 1 | 원 요청 "전체를 그대로 복제하지 않고 … 재작성하거나 연결" | 절반만. 원문은 "원칙, **스킬**, 검사 방법, **에이전트 구조**… 부분 선택"과 "**연결**"을 허용 |
| 2 | D-30·D-33·D-31/32·D-23·D-37 | 타당하되 범위 오독 — "포크 금지·선별"이지 "원문 복사 금지"가 아님 |
| 3 | C-C6(스킬 본문에 도구명 금지), K-06(hook 비의존), 5기준 #3(런타임 설치 제외) | superpowers에는 해당 없음. 고정 SHA `b36e082` 원문 확인: `verification-before-completion`·`test-driven-development` 본문 도구명 0건, SDD·code-review는 "dispatch a subagent" 추상 어휘만. 공식 porting guide가 C-C6의 출처 |
| 4 | 정적 분석 한계 | 타당. 단 재작성해도 똑같이 미검증 — 원문이든 재작성이든 doctor 실측 필요 |
| 5 | 라이선스 | superpowers·CIS·OpenWiki·WIG·taste MIT, impeccable Apache-2.0 → 원문 복사 가능. ui-ux-pro-max만 확인 필요 |
| 6 | 주의력 병목(`using-superpowers` 1% 규칙, BMAD 체크포인트 대기) | 타당. 그러나 특정 2~3개 파일의 문제 — 세트 전체의 문제가 아님 |
| 7 | S03 판정 | 계획이 S03보다 보수적. S03은 "TDD·systematic debugging·verification·code review는 **거의 그대로 재사용**"이라 했는데 §6은 전부 "일부 재작성" |

## 결정 (결정 등록부 D-50~D-58)

| ID | 요지 |
| --- | --- |
| D-50 | Romeo = 라우터 + 접착 + 동등성. 부품은 조립. 자체 제작·재작성은 강등 경로 |
| D-51 | 채택 방식 5단계 `install` / `verbatim` / `rewrite` / `principle` / `excluded` |
| D-52 | 채택 확정 게이트 — 파일 목록은 마일스톤 진입 시 사용자가 확정(G-M2·G-M3·G-M6·G-M7) |
| D-53 | 부착 완료 = 통합 규약 K-60~K-69 + 충돌 fixture 3종 + 양 런타임 discovery |
| D-54 | Superpowers 규율 세트 `verbatim` 후보, `brainstorming`·`using-superpowers` 제외 |
| D-55 | BMAD 본체+CIS `install` + `/plan` 링크, 벤더링 없음 (D-31 대체) |
| D-56 | OpenWiki `install` (라벨 정정) |
| D-57 | ui-ux-pro-max 라이선스 확인 트랙 |
| D-58 | `install`·`verbatim`은 v1 안에서 허용, 동등성은 부품이 켜진 상태에서 판정 |

## 채택 방식 5단계

| 방식 | 뜻 | 후보 |
| --- | --- | --- |
| `install` | 외부 도구로 설치·연결. 코드 미복사. 라우터가 호출하고 산출물을 링크로 흡수 | Orca, BMAD 본체+CIS, OpenWiki |
| `verbatim` | 고정 SHA 원문 복사, 수정 0, `vendor/`에 두고 어댑터가 두 런타임으로 투영 | Superpowers 규율 세트, WIG `AGENTS.md`·`command.md`, taste v2, impeccable 스킬 본문·판정, (라이선스 확인 후) ui-ux-pro-max |
| `rewrite` | 원칙을 코어 형식으로 재작성. 통합 규약을 못 지키는 파일의 강등 경로 | writing-plans task 구조 → Tech Spec 템플릿, impeccable `DESIGN.md` 스키마, rulesync 5단계 → `romeo update` |
| `principle` | 참고만, 미복사 | OMA, open-design, MengTo, ARIA, tokens, slugify, anthropics/skills |
| `excluded` | 채택 안 함 | cc-switch, orca-cli/orca, storybook |

## 채택 확정 게이트 절차 (D-52)

1. **후보표 제시** — `archive/<repo>/03-components/`·`04-components-table.md`에서 파일 단위 후보 + 채택 방식 + 켜는 조건 + 충돌 지점 + 라이선스
2. **사용자 선택** — 제품 결정(B). 자율 진행하지 않는다. Q-07 "좋았던 워크플로우" 명단이 있으면 우선순위에 반영
3. **기록** — `provenance/imports.yaml`에 `status: accepted|rejected`, `decided_at`, `decided_by`, `source_sha`
4. **부착** — `vendor/` 복사(`verbatim`) 또는 설치 프로브(`install`) + 어댑터 투영
5. **검증** — K-68 PASS → 게이트 닫힘. 실패 파일은 `rewrite` 강등 또는 `rejected`

| 게이트 | 시점 | 부품 | 확정하는 것 |
| --- | --- | --- | --- |
| G-M2 | M2 진입 | Superpowers | `verbatim` 파일 목록, 출력 경로 override, 제외 목록 |
| G-M3 | M3 진입 | BMAD 본체+CIS | 라우터가 추천할 스킬(discovery/T2별), 산출물 링크 규약, Codex 미지원 표기 |
| G-M6 | UI 프로젝트 발생 | WIG·taste·impeccable·ui-ux-pro-max | `verbatim` 파일 목록, `DESIGN.md` 스키마, 라이선스 판정 |
| G-M7 | v1 통과 후 | OpenWiki | 부착 대상, `.openwikiignore`, 갱신 시점 |

## 통합 규약 K-60~K-69 (D-53) — 요약

진입점 단일(K-60) · 기획 원본 단일(K-61) · 산출물 흡수(K-62) · 상태 소유권(K-63) · 네임스페이스(K-64) · 트리거 소유권(K-65) · 권한 상한(K-66) · 버전 고정·출처(K-67) · 부착 검증(K-68) · 분리 가능(K-69). 전문은 [`constraints.md` 7절](../../requirements/constraints.md).

## 부품별 충돌 지점과 처리

| 부품 | 충돌 지점 | 규약 | 처리 |
| --- | --- | --- | --- |
| Superpowers | `brainstorming`이 모든 창작 작업 전 설계·승인 강제 + 자체 `docs/superpowers/specs/` | K-61 | 제외. 기획은 `/plan` |
| Superpowers | `using-superpowers` "1% 규칙" + session-start hook | K-60·K-65 | 제외. profile 라우팅이 대체 |
| Superpowers | `docs/superpowers/plans/`, `.superpowers/sdd/` ledger(git-ignored) | K-62·K-63 | 출력 경로를 `docs/work/<id>/`로 override(스킬이 "사용자 선호 우선" 명시), ledger는 `.harness/runs/` |
| Superpowers | 스킬 간 이름 호출(`superpowers:test-driven-development` 등) | K-69 | 세트 단위 채택, 네임스페이스 유지 |
| Superpowers | Codex marketplace 버전 지연(6.2 vs 5.1.3) | K-67 | marketplace 대신 고정 SHA vendoring |
| BMAD/CIS | 매 `<template-output>` 뒤 `[a]/[c]/[p]/[y]` 대기, persona 인사 | K-60 | 라우터가 discovery/T2에서만 켬. 사람 대화형이라 parity 비대상 |
| BMAD/CIS | `_bmad/`·`customize.toml`·`uv run resolve_customization.py` = 3번째 SSOT | K-63 | 코어에 벤더링하지 않음. 산출물만 링크 |
| BMAD/CIS | `ides: [claude-code]`만 설치됨 | K-68 | Codex 설치 1회 시도(A-12), 미지원이면 정직 표기 |
| OpenWiki | `AGENTS.md` managed block 이름 | K-64 | 마커에 소유자 이름 |
| OpenWiki | 계획 문서를 현재 기능으로 오해 | K-62 | `.openwikiignore`에 `docs/work/**` |
| WIG | `install.sh`가 전역 홈·`main` 비고정 | K-67 | 파일만 `verbatim`, 스크립트 제외 |
| impeccable | hook·CLI·4 서브에이전트 | K-65·K-66 | 스킬 본문·판정 규칙만 |
| taste-skill | 취향 강제, 이미지 생성 비용 | K-66, D-37 | 랜딩·브랜드 한정, 이미지 비용은 guard |
| ui-ux-pro-max | `cli/README.md` CC-BY-NC 표기, `--global`, `stack/` MCP `@latest` | K-67·K-66 | 라이선스 확인 후 `cli/`·`stack/` 제외 |

## 바뀐 파일

| 파일 | 변경 |
| --- | --- |
| `docs/product/harness-brief.md` | 한 문장 교체, "만드는 것/만들지 않는 것", 사용자 맥락(운영 방식·실사용 흔적), 성공 정의에 "부품이 켜진 상태에서", 비목표 추가, 경계표 → 부품 조립표 |
| `docs/requirements/capability-map.md` | 개정 3 주석, 5기준 #3 수정, **J. 부품 조립** 절(C-J1~C-J6) + 부품 조립표 |
| `docs/requirements/constraints.md` | **7절 부품 통합 규약 K-60~K-69** |
| `docs/requirements/v1-scope.md` | V-11, 최소 흐름 문단 완화(D-58), 채택 게이트 절, 짓지 않는 것 3행, v2 순서 #2 |
| `docs/decisions/decision-register.md` | D-31 superseded, **부품 조립 절 D-50~D-58**, 폐기 아이디어 2행 |
| `docs/planning/open-questions.md` | A-11·A-12, X-03 결정, Q-03·Q-06 갱신, Q-07, 승인 필요 #8 갱신·#9·#10 |
| `docs/traceability/conversation-coverage.md` | S01 현행성, 인용 키 `REDEF-0827`, 정규화 원칙 4(정정) |
| `docs/planning/implementation-plan.md` | 개정 3: §0·§2.3·§2.4 A5·§3.1·§3.2·§3.3·§5.1·§6 전면·§7 intro·M2·M3·M6·M7·§9.2 #8·§10 #8b·#13b·#18·§12 |
| `docs/explained/implementation-plan.html` | "개정 3 반영 전" 안내 배너 (개정 2 기준 브리프임을 명시) |
| `README.md` | 한 문장, 문서 표, 아키텍처 문단, 개정 3 링크 |
| `docs/reviews/2026-08-27-assembly-redefinition/summary.md`·`summary.html` | 이 기록과 PM 브리프 (신규) |

## 확인된 사실 / 가정 / 미검증

- **사실:** 위 사용자 인용은 전부 transcript·이 세션 원문. 실사용 흔적은 BMAD와 UI UX Pro Max만 로컬에서 확인. superpowers 고정 SHA 원문 6개 파일을 GitHub API 읽기 전용으로 확인.
- **가정:** "잘 썼던 하네스"에 Superpowers·OpenWiki가 포함되는지는 로컬 자료로 확인되지 않음(다른 환경 사용 가능). Q-07로 남김.
- **미검증:** A-11(vendored 스킬 양 런타임 discovery), A-12(BMAD Codex 지원), ui-ux-pro-max 라이선스 범위. 모두 G-M2·G-M3·G-M6에서 실측.

## 남은 위험

- 통합 규약을 지키면서 superpowers 세트를 그대로 쓰면 `using-superpowers`가 없어 스킬 호출 시점을 Romeo 워크플로우 본문이 정확히 지정해야 한다 — M2에서 profile별 호출표를 fixture로 검증.
- BMAD 산출물 링크만으로는 Brief/Charter 길이 캡(K-30)을 넘길 수 있다 — 링크 + 요약 섹션으로 제한.
- 채택 게이트가 4개라 게이트마다 사용자 주의력이 든다 — 후보표는 ≤ 30행, 기본 선택값(추천)을 미리 채워 1클릭 확정이 가능하게.

## 다음 우선 작업

1. (사용자) Q-07 "정말 좋았던 워크플로우" 명단 — 있으면 G-M2·G-M3 후보표 우선순위에 반영. 없어도 진행 가능.
2. M0 착수(변경 없음 — 부품은 M0에서 만지지 않는다).
3. M2 진입 직전 G-M2 후보표 작성 → 사용자 확정.
