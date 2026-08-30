---
id: open-questions
type: planning
status: active
updated: 2026-08-29
authority: canonical
---

# 열린 질문과 미검증 가정

확정 요구로 승격하지 않은 것들이다. 세 묶음으로 나눈다.

- **A. 미검증 가정** — 구현 전 실험이 필요하다.
- **B. 충돌** — 사용자 판단이 필요하다.
- **C. 결론 없는 질문** — 대화에서 제기됐으나 답이 남지 않았다.

---

## A. 검증되지 않은 가정

| ID | 가정 | 왜 위험한가 | 검증 방법 | 근거 |
| --- | --- | --- | --- | --- |
| A-01 | Claude와 Codex가 같은 계약에서 **의미적으로 동일한** 산출물·게이트 판정을 낸다 | 하네스 전체의 존재 이유인데 아직 한 번도 관통 실행되지 않았다 | v1 수직 슬라이스 + parity fixture | S01 KEEL 리뷰 §1 |
| A-02 | 정책 테이블 + 2질문 rubric으로 gate 누락 없이 문서 패키지를 결정할 수 있다 | fixture가 아직 0건이다 | fixture 15~20건에서 분류 수정률·gate 누락 수 측정 | COUNCIL 우선순위 0 |
| A-03 | T0/T1/T2 3-tier가 실제 요청 분포를 충분히 덮는다 | 축소 편향 가능성을 council 스스로 경고했다 | shadow mode 20건 | COUNCIL "전원이 틀릴 수 있는 지점" |
| A-04 | 경로 불변 + metadata view가 실사용 탐색성을 유지한다 | 5.6 단독 제안이며 로컬 카운슬이 반박할 기회가 없었다 | 문서 30건 시점에서 재평가 | COUNCIL "새로 닫힌 쟁점" |
| A-05 | `rg` + 구조 검증 스크립트만으로 문서 100건까지 버틴다 | 인덱스 부재의 첫 실패는 조용히 온다 | 문서 수·횡단 조회 빈도 계측 | COUNCIL Consensus 7 |
| A-06 | Orca orchestration이 이 계약을 안정적으로 지원한다 | 실검증은 `/repo` 파이프라인 1건뿐이다 | v1 슬라이스에서 dispatch·wait·release 재검증 | `archive/`, S23 |
| A-07 | OpenWiki가 유지비 대비 이득을 준다 | 실행 검증 없이 문서·아카이브 분석만 했다 | 실제 프로젝트 1건에 부착해 갱신 3회 관찰 | S12, `archive/langchain-ai-openwiki` |
| A-08 | 미래 소비자가 사람이 아니라 LLM 세션이다 | 사람 협업자가 생기면 무문서 T0와 대화 내 승인이 전부 재검토 대상이 된다 | 협업자 발생 시 재평가 | COUNCIL |
| A-09 | 자기학습 승격 루프의 회귀평가가 실현 가능하다 | 양 런타임 전후 평가 비용이 미측정이다 | v3 이전 파일럿 | S01 plan §4 |
| A-10 | 하네스 부착이 코드 프로젝트가 아닌 프로젝트에도 같은 분류로 작동한다 | 면접 준비·커머스 운영 사례는 T0/T1/T2와 매핑되지 않는다 | **v1 에서는 검증하지 않는다(D-43)**. 비코드 fixture 2건(S15·S24)은 `OUT_OF_SCOPE_NON_CODE` 정직 보고가 기대값 | S15, S24 |
| A-11 | 고정 SHA 원문(`verbatim`) 스킬이 어댑터 투영 후 Claude `.claude/skills`와 Codex `.agents/skills` **양쪽에서 실제로 discovery**된다 | 정적 분석뿐, 실행 미검증. 실패하면 해당 스킬은 `rewrite` 강등 | M2 doctor 프로브 + 충돌 fixture (K-68) | D-54, archive superpowers `05` |
| A-12 | BMAD 설치기가 Codex 대상으로도 동작하거나, 동작하지 않아도 "Claude 전용 discovery 능력"으로 정직 표기하면 동등성 게이트에 영향이 없다 | 현재 설치는 `ides: [claude-code]`뿐 | G-M3에서 Codex 설치 시도 1회 + capabilities.yaml 표기 검토 | D-55, `~/bmad-ordi/_bmad/_config/manifest.yaml` |
| A-13 | 정책표 fixture 일치율 100%(M0)가 실제 분류 정확도를 뜻한다 | **부분 반증(2026-08-27, shadow 1차 5건)**: 카드 수정률 2/5 = 40%. 단 수정된 것은 정책표 계산이 아니라 LLM 이 제안한 입력 분류값(mode 1·uncertainty 1)이고, unit·hard gate 는 5/5 정확했다. 일치율과 분류 정확도는 실제로 별개임이 확인됐다 | shadow mode 20건까지 15건 남음. 수정 유형(요청에 섞인 조사·판단 단계를 놓쳐 깊이를 낮게 잡음)이 반복되는지 관찰 | M0 리포트 2026-08-27, `fixtures/shadow/2026-08-27-cards.md` |

---

## B. 충돌 (사용자 판단 필요)

| ID | 충돌 | A안 | B안 | 추천 |
| --- | --- | --- | --- | --- |
| X-01 | 하네스의 성격 | 전문가 역할·스킬을 폭넓게 갖춘 카탈로그 (S01 사용자 원문의 13개 역할) | 얇은 척추 + 역할 2개로 시작 (COUNCIL) | **B**. A는 v2 이후 순차 추가. "필요할 때만 오케스트레이션"이 원 대화의 원칙이기도 하다 |
| X-02 | 사용자 정체성 | "코드를 볼 줄 모르는 비개발자" (S12) | "개발 암묵지를 공유하는 1인 개발 PM" (S14) | **해소(2026-08-27, D-60)**: persona(비개발자 PM)를 확정. 사용자는 Tech Spec 확인란만 읽고 승인하고, 기술 판단은 검토자 런타임·evidence 가 책임진다 |
| X-03 | 기획 코어의 출처 | BMAD 기획 자산 선별 벤더링(S01) 또는 Spec Kit 기반(S12) | 자체 얇은 정책표 + 템플릿 3개 (COUNCIL) | **양립 — D-50·D-55로 결정(2026-08-27).** 라우터·정책표·템플릿 3개는 Romeo 자체, BMAD/CIS는 discovery·T2 부품으로 `install`+링크. 벤더링은 하지 않는다. Spec Kit은 Q-01 유지 |
| X-04 | 문서 정리 방식 | "새로 생성되는 문서가 자동으로 유형별 폴더링" (S01) | 경로 불변, 폴더 이동 없음 (D-09) | **양립**. 생성 시점 폴더링은 유지하고 상태 변화에 따른 이동만 금지한다 |
| X-05 | 라이선스 | Apache-2.0 (S05 권고) | GPL-3.0 (현재 `LICENSE`) | **해소(2026-08-27, D-41)**: Apache-2.0 전환. 파일 교체는 M2 첫 외부 자산 복사 시 |
| X-06 | 모델 선택 | "역할 난이도에 따라 모델을 직접 선택하고 싶다" (S01) | "역할에 모델을 영구 고정하지 않는다" (S01 KEEL 리뷰 §7) | **양립**. 역할은 capability를 선언하고, 모델 바인딩은 첫 등록 시 승인 후 고정하며 task별 override를 허용한다 |
| X-07 | 즉석 생성 | "작업 도중 새 스킬·에이전트 생성" (S01) | 초안 → 검증 → 등록 → 배포 승격 절차 (S01) | **승격 절차**. 즉석 생성은 초안까지만 허용한다 |
| X-08 | 문서 원장 | `docs/` (기획) | `openwiki/` (기술) | **분리 유지**. 단 같은 사실을 두 곳에 두지 않는 규칙이 필요하다 |
| X-09 | 하네스 이름 | KEEL | Romeo | **Romeo**. KEEL은 폐기된 초안 명칭으로 표기한다 |

---

## C. 결론 없는 질문

| ID | 질문 | 마지막 언급 |
| --- | --- | --- |
| Q-01 | GitHub Spec Kit을 도입할 것인가, `converge` 개념만 차용할 것인가 | **확인됨(2026-08-27, D-40)**: 비채택 + `converge` 개념만 v2 재검토 |
| Q-02 | 하네스 자체 성공 지표 8종을 언제부터 계측하는가 | COUNCIL §3 |
| Q-03 | 디자인 트랙 4스킬(`ux-architect`·`creative-director`·`design-system-keeper`·`visual-qa`)을 자체 제작할 것인가, 외부 스킬을 선별 채택할 것인가 — **개정 3 추천: `visual-qa`만 자체, 나머지 3역할은 WIG·taste·impeccable·ui-ux-pro-max `verbatim` 파일 조합. 파일 확정은 G-M6** | S13, D-57 |
| Q-04 | MCP registry 공통 스키마(Claude JSON + Codex TOML 동시 생성)를 v2에 넣는가 | S01 plan §3 |
| Q-05 | `rulesync`, `cc-switch` 같은 후발 조사 대상을 어댑터 구현에 반영하는가 | `archive/` (분석만 완료) |
| Q-06 | BMAD 본체는 아직 아카이브되지 않았다(CIS만 있음). 기획 자산 판정을 위해 필요한가 — **G-M3 선행 조건으로 승격** | `archive/README.md` 목록, D-55 |
| Q-07 | 사용자가 "실제로 써보고 정말 좋았던" 워크플로우의 구체 목록 | **답변됨(2026-08-27, D-64)**: CIS 4종 최우선, BMAD PRD 흐름 후순위, Superpowers 개발 체계·OpenWiki 자동 문서 관리·impeccable/taste anti-slop·UI UX Pro Max 실사용. 상상 흐름 CIS → Romeo 문서 → Superpowers → OpenWiki |
| Q-08 | ~~같은 산출물에서 두 검토자의 판정이 갈렸다 — codex 의 `PASS` 는 우연인가 체계적인가.~~ **답변됨(2026-08-29, 재현성 측정 · 사용자 결정으로 선택지 (a) 실행)**: codex 의 PASS 는 **재현되지 않았다.** 산출물을 고정한 채(트리 `7b035490df84…` · 계약 sha256 `f79f4bc1…` 네 개 `cmp` identical · 방어 검사 `log_sha256` 여덟 스냅샷 전부 `2bc7dad48f31…`) codex 를 세 번 돌려 **PASS 1 · FAIL 2** 다 — 기준 `run_31e175742892`(TUI 경로) PASS findings 0, `run_241a35112ca3` FAIL findings 1, `run_5dd1b2c232c7` FAIL findings 4. 따라서 **(c) 기본 바인딩 재검토는 근거를 잃었다** — 그 PASS 는 런타임의 성질이 아니라 한 번의 누락이다. 그리고 FAIL 두 건 중 `run_5dd1b2c232c7` 의 findings 4건은 claude 검토자(`run_5fc794f15236`)의 6건과 실질적으로 겹친다(루트 오염 · 증거 결박 · `Varies by skill` · `bash -c` 결함) — 루트 오염을 **보는 능력의 차이가 아니다.** 남은 것은 (b) 검토 절차 보강 여부와, 이 측정이 새로 드러낸 **Q-09** 다. `expect` 는 고치지 않았다(D-b) | `.harness/observations.yaml` 의 `reviewer_verdict_reproducibility`, `docs/work/feat-20260829-license-field-46an/review/run_{241a35112ca3,5dd1b2c232c7}-reviewer.json`, RUNBOOK §11.1 |
| Q-09 | ~~검토자 판정이 같은 런타임 안에서도 흔들린다 — 게이트의 검토자 면을 1회 표본으로 판정할 수 있는가.~~ **답변됨(2026-08-29, 사용자 결정 → D-74)**: 없다. 표본을 더 모으자 **두 런타임 다 흔들리는 것**이 관측됐다 — codex 3회 `PASS`(0)·`FAIL`(1)·`FAIL`(4), claude 2회 `FAIL`(6)·`PASS`(8). claude 의 두 번째 실행은 findings 를 더 많이 내고도 판정은 `PASS` 였다. 선택지 (a) 를 채택해 판정 역할의 면에 **각 면 2건 이상의 표본**과 **면 내부 일관성**을 요구하고, 모자라면 `VERDICT_UNSAMPLED`, 갈리면 `VERDICT_UNSTABLE` 로 판정에서 빼되 '비교 불가' 로 인쇄한다(D-73 과 같은 형태). **남은 것**: 왜 흔들리는지는 이 다섯 실행으로 가려지지 않았다 — 판정 기준의 모호함인지, 검토 절차 문서의 빈자리인지, 모델의 비결정성인지. 그리고 기동 경로(TUI vs 비대화형)가 교란 변수로 남는다 → Q-10 | `docs/decisions/decision-register.md` D-74, `romeo/parity.py`, `.harness/observations.yaml` 의 `reviewer_verdict_reproducibility` |
| Q-10 | **검토자 판정은 왜 흔들리는가 — 그리고 줄일 수 있는가.** D-74 는 흔들림을 **드러내고 판정에서 빼는** 장치이지 흔들림을 줄이는 장치가 아니다. 다섯 실행이 가리지 못한 것: (a) 판정 기준의 모호함 — `core/workflows/review/SKILL.md` 는 "무엇이 FAIL 사유인가" 를 열거하지 않는다(같은 findings 를 내고도 한 실행은 PASS, 다른 실행은 FAIL 이었다) (b) 검토 절차의 빈자리 — 작업 트리 스냅샷의 미추적 파일을 대조하라는 지시가 없다(Q-08 의 선택지 (b), 아직 미실행) (c) 모델의 비결정성 (d) 기동 경로 — `PASS` 가 나온 codex 실행만 TUI 였고 나머지는 비대화형이다. (a)·(b) 는 절차 문서로 줄일 수 있고 (c)·(d) 는 측정으로만 분리된다. 어디부터 볼지는 미결. **D-76(2026-08-29):** 판정 일치가 게이트에서 빠졌으므로 이 질문은 M2 완료를 막지 않는다 — 실험 재료는 `romeo fixtures parity --judge-verdict strict` 프로파일과 관측 표본(같은 산출물 5실행)이다. 다음 손댈 자리는 (a) `review/SKILL.md` 의 FAIL 사유 열거 | `core/workflows/review/SKILL.md`, `.harness/observations.yaml` 의 `reviewer_verdict_reproducibility.what_this_does_not_say` |
| Q-11 | **승인 사건을 기계가 확인할 수 있는 형태로 만들 것인가.** 승인 키(approved_at·approval_history)의 원본은 spec frontmatter 이고 그것은 이 기계를 쓰는 사람이 고칠 수 있다. 작업 트리에서 되돌리는 것은 HEAD 대조로 막았고(`approval_rollback_error`), approve 명령을 거치지 않은 재승인(approved_at 만 손으로 바꿔 커밋)은 사슬 검사가 **경고**만 한다(`APPROVAL_CHAIN` — 옛 방식의 손 재승인도 같은 모양이라 차단하면 이 단위부터 막힌다). 근본 대책은 승인 커밋을 저장소 밖 사실에 묶는 것이다 — 서명된 커밋(`git log --format=%G?`)·특정 author·하네스 밖 승인 저장소 중 하나. D-27 의 '승인은 사람의 몫' 을 기계가 확인하는 형태로 바꾸는 것이므로 사용자 결정이다. **미룸(2026-08-29 사용자 확정)** — 한 사람 로컬 v1 에는 보호 대상이 없다(승인자=위조자). 도입 트리거: 승인자 2인 이상 · 감사 추적 요구 · 공유 CI · 규제. 그 전에는 `APPROVAL_CHAIN` WARN 으로 드러내는 것이 비용·운영의 균형이다 | `romeo/docs.py` `approval_chain_warnings`, 체크리스트 45 |

---

## 승인 또는 추가 검증이 필요한 결정 (우선순위 순)

| # | 결정 | 왜 사용자 판단인가 | 추천 |
| --- | --- | --- | --- |
| 1 | 저장소 라이선스: GPL-3.0 유지 vs Apache-2.0 전환 (X-05) | 되돌리기 어렵고 외부 채택 가능성을 바꾼다 | **결정됨 → Apache-2.0 (D-41, 2026-08-27)**. 파일 교체·`THIRD_PARTY_NOTICES.md`는 M2 |
| 2 | GitHub Spec Kit 도입 여부 (Q-01) | 채택하면 v1 범위가 바뀐다 | **확인됨 → 비채택 + `converge` 개념만 (D-40, 2026-08-27)** |
| 3 | 하네스 적용 대상 범위 (D-43, A-10) | T0/T1/T2와 hard gate 8은 소프트웨어를 전제한다 | **결정됨 → v1 코드 전용 (D-43, 2026-08-27)**. 비코드는 `OUT_OF_SCOPE_NON_CODE` 정직 보고 |
| 4 | 상태 모델: 단일 5상태 vs 직교 3세트 (D-15) | 나중에 바꾸면 모든 frontmatter를 마이그레이션해야 한다 | **구현됨 → 5상태 + `approved_at` 사실 필드 + close 시 계산 (D-61, 2026-08-27)** |
| 5 | 경로 불변 원칙 채택 (D-09, A-04) | 5.6 단독 제안이며 반박 기회가 없었다고 council이 명시했다 | 채택하되 A-04를 열린 가정으로 유지 |
| 6 | fixture 15~20건을 어디서 모으는가 (V-0) | 실제 요청 로그가 필요하고 이것이 v1의 첫 작업이다 | **결정·수집됨 → 로컬 세션 로그 24건 + 대화 압축본 5건 + 저장소 4건 = 33건 (D-63, 2026-08-27)**. 이후는 shadow mode 축적 |
| 7 | BMAD 본체 아카이브 필요 여부 (Q-06) | D-31의 근거가 3주 이상 지났다 | 필요. 템플릿을 실제로 가져올 때 다시 대조해야 한다 |
| 8 | 디자인 트랙: 자체 4스킬 제작 vs 외부 선별 채택 (Q-03) | v2 범위와 유지비가 크게 달라진다 | `DESIGN.md`를 계약으로, `visual-qa`만 자체 제작, 나머지는 `verbatim` 파일 조합. 파일 확정은 G-M6 |
| 9 | **채택 매니페스트 확정 — 게이트마다** (D-52: G-M2 Superpowers, G-M3 BMAD/CIS, G-M6 디자인, G-M7 OpenWiki) | 어느 파일을 가져올지는 제품 결정이다. 계획 단계에서 정하지 않고 마일스톤 진입 시 후보표를 보고 정한다 | 후보표는 `archive/<repo>/03-components/`·`04-components-table.md`에서 생성. Q-07 명단을 먼저 받으면 우선순위에 반영 |
| 10 | ui-ux-pro-max 라이선스 확인 액션 (D-57) | 실사용한 도구인데 `cli/README.md` CC-BY-NC 표기 때문에 보류돼 있었다 | `cli/` 제외 skill/data만 루트 MIT 범위로 채택 가능한지 maintainer 표기 확인. G-M6 전까지 |
| 11 | **확정(2026-08-29): (b) — D-75 accepted.** ~~종료 검사의 검토 표본 수 — 현재 산출물에 PASS 1건이면 닫을 것인가, D-74 처럼 2건을 요구할 것인가 (D-75)~~ | 같은 산출물에서도 검토 판정이 흔들리는 것이 관측됐고(D-74), 1건이면 산출물을 사소하게 바꿔 PASS 가 나올 때까지 검토를 반복하는 길이 열린다. 2건이면 일반 T1 의 검토 비용이 2배다 — 완료의 기준과 비용을 함께 바꾸는 제품 결정이다 | **확정: (b) 1건 + `REVIEW_SAMPLE` WARN**(2026-08-29 · 표본을 늘려도 참값이 생기지 않는다, D-74·D-76). ~~(a) 2건 요구~~ — §6.6 이 이미 런타임당 2건을 만들어 M2 흐름에서는 추가 비용이 없고, '한 번의 판정은 그 실행의 판정' 이라는 D-74 의 논리와 같다. 구현은 `romeo/close.py` 의 `REVIEW_SAMPLE` 검사에서 `level="warning"` 을 빼 차단 검사로 올리면 된다(상수 `REVIEW_PASS_SAMPLES` 는 이미 2). 지금은 (b) 1건 + `REVIEW_SAMPLE` WARN |
