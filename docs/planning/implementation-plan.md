---
id: implementation-plan
type: planning
status: draft
updated: 2026-08-27
authority: derived
---

> 원 요청: [implementation-plan-request.md](implementation-plan-request.md) · PM용 브리프: [../explained/implementation-plan.html](../explained/implementation-plan.html) · Codex 리뷰: [../reviews/2026-08-27-codex-plan-review/](../reviews/2026-08-27-codex-plan-review/)
>
> **개정 2 (2026-08-27):** Codex(`gpt-5.6-sol`, fast) 리뷰 8건을 검증해 채택 6·부분 채택 2를 반영했다. 바뀐 곳은 §11에 정리했고 판정 근거는 [decisions.md](../reviews/2026-08-27-codex-plan-review/decisions.md)에 있다.
>
> **개정 4 (2026-08-27, M0 착수):** §9.2 의 사용자 결정 1~8 이 확정됐다(D-41·D-43·D-59~D-66, [decision-register](../decisions/decision-register.md) "구현 착수 결정"). 이번 세션 정지선은 M0+M1. M0 산출물은 `core/`·`romeo/`·`fixtures/`·`tests/`, 실행 기록은 `docs/work/` 와 `fixtures/shadow/`, 진행 상태는 [progress.md](progress.md).
>
> **개정 3 (2026-08-27):** 사용자 재정의("잘 썼던 하네스들을 조립해서 나만의 라우터 체계로")를 반영했다. 참고 저장소를 "원칙만 참고"하던 §6을 **채택 방식 5단계·채택 확정 게이트·통합 규약**으로 다시 썼고, 부품 연결을 M2·M3 안으로 당겼다. 바뀐 곳은 §12, 근거는 [assembly-redefinition/summary.md](../reviews/2026-08-27-assembly-redefinition/summary.md)에 있다.
>
> **개정 4 (2026-08-27, M2 진입):** G-M2 채택 게이트를 열고 닫았다. Superpowers 는 규율 코어 **7종만** 채택하고 오케스트레이션 4종은 보류했다(D-67) — 그 자리는 Romeo 라우터와 Orca 가 이미 차지하고 있기 때문이다. 역할 바인딩 확정(D-68), `writing-plans` 두 규율 흡수(D-69), OpenWiki 선행 조건 추가(D-70), §6 표의 "도구명 0건" 사실 정정(D-71). 결정 기록은 `provenance/imports.yaml`.

# Romeo 하네스 구현 계획 (조사·설계·순서 수립 단계)

작성 2026-08-27 · 작성 시점 HEAD `324d63e` · 브랜치 `Supervibecoder0709/mvp_planning` · 파일 변경 없음(조사·설계만)

## 0. 결론 먼저

**추천 구조는 정본 문서의 결정(D-02 *Thin Policy-Compiled Planning Spine*)을 그대로 뼈대로 쓰되, 이번 요청에서 추가된 네 가지 — 작업 깊이(Quick/Standard/Deep) 표시, 승인과 진행의 분리, 실행 시점 위험 행동 가드, 프로젝트 설치·업데이트 — 을 "정책표의 출력 필드 + frontmatter 필드 + 실행 계약 필드"로 흡수하는 것**이다. 새 상태 머신이나 새 저장 계층을 추가하지 않고도 요청한 능력을 모두 표현할 수 있고, 그래야 v1 인프라 제로(D-10)와 충돌하지 않는다.

첫 동작 흐름은 **T0 요청 1건을 Claude 단독으로 `분류 → Tech Spec(Planning Capsule) → 현재 작업 공간 구현 → HEAD SHA 증거 → /plan-close`까지 관통**시키는 것이고(M1), 그다음 **T1 요청 1건을 Orca로 위임해 Claude 구현·Codex read-only 리뷰 → 역할 교체 재현**(M2)이 하네스의 존재 이유를 증명하는 **핵심 동등성 게이트(core parity gate)** 다. **v1 릴리스 게이트**는 이것과 별도로 정본 V-0~V-10 충족(Charter 양식·최소 부착 상태 파일·shadow mode 20건 포함)으로 정의하고 M4 종료 시점에 판정한다. 이 순서는 이번 명령("작은 요청 하나가 먼저")과 정본(`v1-scope.md` "실제 T1 1건 + 역할 교체" + "v1에 반드시 들어가는 것 V-0~V-10")을 둘 다 만족한다. (Codex 리뷰 F-01 반영)

구현 전에 **사용자 결정이 필요한 항목 5개**를 §9에 모았다(라이선스, 사용자 정체성 persona 충돌, 상태 모델, 깊이 라벨 명명, v1 적용 대상). 나머지는 기술 결정으로 추천안을 정했고 구현하면서 검증한다.

**개정 3의 추가 결론:** Romeo가 만드는 것은 **라우터 + 접착(문서·상태·증거) + 동등성**이고, 기획 facilitation·개발 규율·기술 문서 파생·디자인 규칙·실행은 사용자가 검증한 **부품을 조립**한다(D-50). 부품은 `install`(BMAD/CIS·OpenWiki·Orca) 또는 `verbatim`(Superpowers 규율 세트·디자인 파일)으로 붙이며(D-51), **어느 파일을 가져올지는 계획에서 정하지 않고 M2·M3·M6·M7 진입 시 채택 확정 게이트에서 사용자가 정한다**(D-52). 충돌 없이 하나의 시스템이 되는 것은 채택 방식이 아니라 **통합 규약 K-60~K-69**(§6.2)가 보장하고, 부착 완료는 doctor 프로브 + 충돌 fixture PASS로만 선언한다(D-53). 동등성 게이트는 부품이 켜진 상태에서 판정한다(D-58).

---

## 1. 현재 저장소 조사 결과

### 1.1 확인된 폴더·문서·설정 (HEAD `324d63e`, 브랜치 `Supervibecoder0709/mvp_planning`, 작업 트리 clean)

| 영역 | 경로 (근거) | 확인 내용 |
| --- | --- | --- |
| 프로젝트 규칙 | `CLAUDE.md` | 구조 선확인·계획만이면 무수정·정보 충돌 우선순위·위험 작업 승인·실행≠완료 원칙 |
| 요구사항 정본 6종 | `docs/product/harness-brief.md`, `docs/requirements/capability-map.md`, `docs/requirements/constraints.md`, `docs/requirements/v1-scope.md`, `docs/decisions/decision-register.md`, `docs/planning/open-questions.md` | 전부 `authority: canonical`, `updated: 2026-08-27`, status는 draft(open-questions만 active) |
| 추적성 | `docs/traceability/conversation-coverage.md` | 인용 키 S01~S25·COUNCIL·PHD·AGENTS-P, 커버리지 공백 4건 |
| 도출 과정 | `docs/planning-harness-discussion.md`(PHD), `docs/council/01..03*.md`, `docs/council/README.md` | 최종 권장 *Thin Policy-Compiled Planning Spine*, Consensus 10개, 남은 이견 3개, 구현 우선순위 0~6 |
| 보조 문서 | `docs/explaining-tech-to-non-developers.md`, `docs/explained/planning-harness-discussion.html` | 비개발자 설명 원칙, PHD의 PM용 HTML 브리프 |
| 원천 대화 | `docs/source-context/project-conversations-compressed-2026-08-27/` — `README.md`, `INDEX.md`, `MANIFEST.json`, `SHA256SUMS`, `transcripts/` 25개 | **지시된 `project-conversations-compressed.md` 단일 파일은 없고 이 디렉터리가 실체**. 파일당 17KB~23MB(S11·S14는 base64 이미지 포함) |
| 기존 구현 | `.claude/commands/repo.md`, `.claude/agents/repo-archive-coordinator.md`, `skills/repo-archive/SKILL.md`, `skills/repo-archive/agents/openai.yaml`, `.agents/skills/repo-archive` → `../../skills/repo-archive` (git mode `120000` 심링크) | Claude 코디네이터 → Codex 작업자(`orca orchestration run-create/task-create/worker-start/check --wait/worker-release`) 아카이브 파이프라인. **현재 유일하게 동작하는 Orca 위임 실증** |
| 검증·CI | `scripts/validate-repo-archive.sh`, `scripts/generate-archive-index.py`, `.github/workflows/archive-index.yml` | 아카이브 스키마 검증(`rg` 의존), 결정적 인덱스 생성, CI는 검사 전용(`permissions: contents: read`) |
| 아카이브 | `archive/` 18개, 문서 202개, `archive/README.md`(생성물) | 각 `_source.md`에 40자 SHA·분석 시각·접근 한계 |
| 라이선스 | `LICENSE` | **GPL-3.0 실물** (정본 K-43/X-05/D-41이 충돌로 기록) |

**존재하지 않는 것(가정하지 않음):** `.gitignore`, 루트 `AGENTS.md`, `.codex/`, `.mcp.json`, `.claude/settings.json`, `.claude/skills/`, `tests/`, `THIRD_PARTY_NOTICES.md`, `docs/work/`, `docs/current/`, `/plan`·`/plan-close`·정책표·템플릿·어댑터·evidence 계약 — 즉 `v1-scope.md` V-1~V-10은 전부 미구현이며 README의 "동작하는 것은 `/repo`뿐"이 정확하다.

### 1.2 실행 환경 (읽기 전용으로 확인)

| 항목 | 확인 결과 | 계획에 미치는 영향 |
| --- | --- | --- |
| Claude Code `2.1.247` | `-p/--print`, `--output-format`, `--json-schema`, `--agents <json>`, `--allowedTools`, `--effort`, `--model` 존재 | 구조화 출력·헤드리스 역할 정의 가능(K-06: hook 비의존 유지) |
| Codex CLI `0.147.0` | `exec --json`(JSONL 스트림), `--output-schema`, `-o/--output-last-message`, `-m`, `-p`, `-s`; `codex features list`: `multi_agent stable true`, `hooks stable true`, `guardian_approval stable true` | K-02(서브에이전트 있음)·K-05(NDJSON) 재확인. `.codex/agents/*.toml` 형식 자체는 CLI 도움말로 검증 불가 → `doctor` 단계 재확인 대상 |
| Orca `1.4.188` runtime `ready` | `orchestration`: `run-create`, `task-create --spec --deps --parent`, `worker-start --agent --model --effort --worktree current|new-child|new-top-level`, `check --wait --types`, `gate-create --question --options`, `gate-resolve`, `ask`, `worker-release`; `worktree create --no-parent --agent --prompt`; `terminal read/send/wait` | K-10(실행 상태 권위자)·A-06 검증에 필요한 명령 전부 존재. 현재 worktree `repoId 706c419b…`, `projectId github:supervibecoder0709/romeo-harness` |
| gh `2.86.0` | `Supervibecoder0709` 로그인 | 참고 저장소 재고정·라이선스 조회 가능 |
| python3 `3.9.6`(시스템) + PyYAML `6.0.3`, python3.12(homebrew), `uv`, node `25.6`, `pnpm`, `jq` | CI는 python 3.11 | 검증 CLI는 표준 라이브러리 + PyYAML로 충분 (`yq` 없음) |
| `rg` | `/Applications/ChatGPT.app/Contents/Resources/rg` — **정식 설치 아님** | `validate-repo-archive.sh`가 우연히 동작 중. K-20("rg + 스크립트")의 전제가 취약 → M1의 첫 T0 후보 |
| 홈 레벨 자산 | `~/.claude/commands/race.md`, 스킬 `orca-cli`·`orchestration`·`skill-creator`·`explain`·`find-skills`·`computer-use`; `~/.codex/AGENTS.md`(persona), `~/.codex/config.toml`(model·effort·approval·sandbox 키 존재, 값 미열람) | 병렬 비교(`race`)·오케스트레이션은 이미 사용자 레벨에 존재 → 하네스가 재구현하지 않고 계약만 정의 |

### 1.3 참고 저장소 18개와 라이선스

아카이브 문서 자체에는 18개 중 2개만 라이선스가 적혀 있어(C-H3 "부분"이 사실) GitHub API(`license.spdx_id`, 현재 기본 브랜치)와 고정 SHA 트리의 LICENSE 파일을 읽기 전용으로 대조했다.

| 아카이브 (`archive/<name>`) | 고정 SHA | 라이선스 (API / 고정 SHA 실물) | `_source.md` 에 적는 값 (AC 대조용) |
| --- | --- | --- | --- |
| obra-superpowers | `b36e082` | MIT | `MIT` |
| first-fluke-oh-my-agent | `7a2b46e` | MIT | `MIT` |
| dyoshikawa-rulesync | `c3accea` | MIT | `MIT` |
| farion1231-cc-switch | `5ca9459` | MIT | `MIT` |
| langchain-ai-openwiki | `a525ed8` | MIT | `MIT` |
| bmad-…-creative-intelligence-suite | `0e4ff92` | API NOASSERTION / **실물 `LICENSE` = MIT (BMad Code, LLC)** | `MIT` |
| anthropics-skills | `3b3fad9` | API NONE / **루트 LICENSE 없음, 스킬별 `LICENSE.txt`** → 스킬 단위로 확인 필요 (단일 SPDX 값이 없다) | `루트 LICENSE 없음 · 스킬별 LICENSE.txt` |
| orca-cli-orca | `5beeefc` | MIT (K-13: 기반 삼지 않음) | `MIT` |
| sindresorhus-slugify | `7c318bd` | MIT | `MIT` |
| pbakaus-impeccable | `56f4452` | Apache-2.0 | `Apache-2.0` |
| Leonxlnx-taste-skill | `72e2995` | MIT | `MIT` |
| vercel-labs-web-interface-guidelines | `e3d624b` | MIT | `MIT` |
| w3c-aria-practices | `7e4034b` | API NOASSERTION / 실물 **W3C Software and Document License** | `W3C Software and Document License` |
| design-tokens-community-group | `16c902d` | API NOASSERTION / 실물 **W3C Software and Document License** | `W3C Software and Document License` |
| nextlevelbuilder-ui-ux-pro-max-skill | `bc826e2` | 루트 MIT, 단 `cli/README.md`는 CC-BY-NC-4.0 표기(아카이브 `05` 메모의 불일치 지적) → 코드 포함 보류(K-42) | `MIT` |
| nexu-io-open-design | `35a38ab` | Apache-2.0 | `Apache-2.0` |
| MengTo-Skills | `4c716b5` | MIT | `MIT` |
| storybookjs-storybook | `db12626` | MIT | `MIT` |

### 1.4 확인 범위와 미확인 항목

- **읽음:** 정본 6종 전문, PHD 전문, COUNCIL 03 전문(라운드1·반박·Synthesis), 18개 `05-pm-harness-notes.md` 전문, 18개 `_source.md` 헤더, 기존 구현물·스크립트·CI 전문, S23 transcript 도입부.
- **grep만:** transcripts 25개(명명·개념 출처 확인용). `Quick/Standard/Deep` 표현은 **어느 대화에도 없음**(이번 명령에서 처음 등장), `doc_status/work_status`는 S09·S10·S23에 등장, Spec Kit은 S12·S13에만 등장.
- **미확인:** `docs/council/01`·`02` 본문(요약·헤더만), 각 아카이브 `03-components/`·`06-source-evidence.md` 상세, Codex `.codex/agents/*.toml` 스키마(정본 K-02는 2026-08-05 문서 기준), `~/.claude/settings.json`·`~/.codex/config.toml`의 값, 참고 저장소가 고정 SHA 이후 바뀐 내용.

---

## 2. 요구사항 해석

### 2.1 한 문장 정의

> **Romeo는 자연어 요청을 "LLM이 사실·가정·분류 후보로 정리 → 사람이 1클릭 확정 → 정책표가 문서 패키지·게이트·실행 프로필을 계산 → 필요한 문서만 생성 → 승인된 Tech Spec을 계약으로 Orca가 Claude/Codex에 실행 위임 → 현재 HEAD SHA에 묶인 증거로 종료"까지 연결하되, 판단 기준·문서·증거를 어떤 실행기에도 종속시키지 않는 1인용 요청 운영 체계다.**

### 2.2 핵심 사용자와 주요 시나리오

- **운영자:** 사용자 본인 1인(PM 출신, 여러 프로젝트 병행). **주 소비자:** 다음 LLM 세션(A-08). **실행 환경:** Orca + Claude Code(주) + Codex(교차 검토).
- **대표 시나리오 10개**(§8과 동일): 문구·스타일 소수정 / 기존 제품 기능 추가 / 불확실성 높은 신규 프로젝트 / 랜딩페이지 / 제품 UI 다상태 / Claude·Codex 동일 규칙 / 큰 기능 worktree / 도구 부재 / 비용·운영 데이터 위험 요청 / 하네스 업데이트 충돌. 그리고 이미 동작 중인 0번째 시나리오: 참고 저장소 아카이브(`/repo`).

### 2.3 확인된 요구 / 현재 가정 / 설계상 추천

| 구분 | 내용 | 근거 |
| --- | --- | --- |
| **확인된 요구** | 3-tier planning unit(T0/T1/T2) + mode + facet 독립 축, hard gate 8, 합산 점수 금지, 충돌 우선순위 | D-03, D-07, C-A1~A7 |
| 확인된 요구 | LLM 제안 / 사람 확정 / 규칙 강제 3분할, 초기 20건 shadow mode, fixture 15~20건 선행 | D-06, D-13, V-0, V-10 |
| 확인된 요구 | T0는 기획 파일 0개(Tech Spec 내 Planning Capsule), 템플릿 3개, 커맨드 2개(`/plan`, `/plan-close`) | D-04, D-14, V-2~V-4 |
| 확인된 요구 | 벤더 중립 = 같은 schema·AC·게이트·evidence; TaskEnvelope/ResultEnvelope; managed marker + source hash | D-12, C-C1~C6 |
| 확인된 요구 | Orca가 실행 상태의 유일한 권위자, worktree당 writer 1, reviewer read-only, 반대 런타임 교차 리뷰 | D-20, C-D1~D3 |
| 확인된 요구 | HEAD SHA에 묶인 증거, 바뀌면 stale, 미확인은 "미검증" | C-E1~E4, K-51 |
| 확인된 요구 | 경로 불변·ID `type-YYYYMMDD-slug-entropy`·frontmatter가 분류 기록 | D-05, D-08, D-09 |
| 확인된 요구 | 참고 저장소 전체 포크 금지, 버전 고정, 출처·라이선스 추적, 업데이트는 승인 후 | D-30, K-40~K-42, C-H3/H4 |
| 확인된 요구(이번 명령) | Quick/Standard/Deep 깊이 표시, 승인 상태와 진행 상태 분리, 실행 시점 위험 행동 목록, 설치·업데이트·롤백, 능력 부족 시 정직 보고, worktree 격리 한계 인지 | 이번 프롬프트 |
| 확인된 요구(개정 3) | 검증된 부품을 그대로 조립하고 Romeo는 라우터·접착·동등성만 만든다 — "어떤 bmad 워크플로우가 필요한지 자동 추천", "딱 기획 범위까지만 카피", "한 패키지 모듈" | S01·S12 사용자 원문, REDEF-0827, D-50 |
| 확인된 요구(개정 3) | 무엇을 가져올지는 구현 단계 진입 시 사용자에게 물어 확정한다; 부품 추출물이 충돌하지 않고 하나의 시스템에 녹아드는 것이 최우선 | REDEF-0827, D-52·D-53 |
| **현재 가정** | 사용자는 코드 리뷰 가능한 PM(X-02 B) — **단 persona 파일은 "비개발자"** (§2.4 충돌 A2) | X-02 |
| 현재 가정 | 정책표+2질문 rubric으로 gate 누락 없이 패키지를 결정할 수 있다 (fixture 0건) | A-02 |
| 현재 가정 | Orca orchestration이 이 계약을 안정적으로 지원한다 (`/repo` 1건만 실증) | A-06 |
| 현재 가정 | 문서 100건까지 `rg`+스크립트로 버틴다 | A-05 |
| **설계상 추천** | 깊이 라벨은 planning unit이 아니라 **정책표의 출력**(`profile`)으로 둔다 | §2.4-B1 |
| 추천 | 승인은 별도 상태 머신이 아니라 **`approved_at` 사실 필드**로 기록하고, 검증 상태는 /plan-close 시점에 **계산**한다 | §2.4-B2 |
| 추천 | 위험 목록을 두 층위로 유지: 기획 시점 **hard gate 8**(facet) + 실행 시점 **execution guard**(행동) | §2.4-B3 |
| 추천 | 능력 레지스트리(`capabilities.yaml`) + `doctor` 프로브로 "도구 부재"를 판정하고 자동 설치는 하지 않는다 | K-54, 이번 프롬프트 |

### 2.4 충돌·과도한 범위 지적

**A. 정본 문서 ↔ 대화 압축본 (임의 선택하지 않고 보고)**

| # | 충돌 | 상태 | 추천 |
| --- | --- | --- | --- |
| A1 | S05 권고 Apache-2.0 vs `LICENSE` GPL-3.0 | 정본도 `conflict`(D-41) | 재사용 자유를 원하면 Apache-2.0(기여자가 본인뿐인 **지금**이 전환 최저 비용). 결정 후 `THIRD_PARTY_NOTICES.md` 작성 |
| A2 | **`~/.codex/AGENTS.md`(모든 Codex 세션에 주입되는 persona, transcripts 전부에 포함) = "PM 출신의 비개발자 바이브코더"** vs `open-questions.md` X-02 추천 "B(개발 암묵지 공유 1인 개발 PM)가 사실" | 정본은 "확인 필요"로 남김. 실물 persona는 A | 두 문장은 양립 가능: **설명 방식은 persona(역할·이유·영향까지 설명)**, **하네스가 가정하는 검토 능력은 B**. 단 이 해석을 사용자가 확정해야 문서 장황함(K-30)과 승인 UX가 정해짐 |
| A3 | S12 "Spec Kit 1순위" vs 정본 미채택(D-40 open) | open | 비채택 + `converge` 개념만 v2에서 차용(정본 추천과 동일) |
| A4 | S01 KEEL 계열(13역할·8계층·hook 강제·relay) vs S10 이후 Spine | 정본이 이미 Spine 채택 | 유지. KEEL은 폐기 초안으로만 표기 |
| A5 | 정본 정규화 원칙 2("도구 이름을 요구로 해석하지 않았다") vs S01 "bmad를 딱 기획 범위까지만 카피하고 싶어"·S12 "한 패키지로 묶어" | 원칙 2가 사용자의 조립 요구를 능력 후보로 강등 | **D-50으로 해결.** A~I 능력은 유지, 부품은 능력 지도 J절·조립표로 승격. 원칙 2는 "라우터·접착에만 적용"으로 한정(coverage 정규화 원칙 4) |

**B. 이번 명령 ↔ 정본 문서 (명령이 우선이지만, 그대로 동의하지 않는 부분)**

| # | 지점 | 판단 | 추천 |
| --- | --- | --- | --- |
| B1 | 명령의 **Quick/Standard/Deep**(깊이) vs 정본 **T0/T1/T2**(승인 단위) | 같은 축이 아님. "결제 약관에 걸린 버튼 문구 한 줄"은 unit=T0이지만 깊이는 Standard여야 함(C-A4) | `unit`은 T0/T1/T2 유지, `profile: quick|standard|deep`을 정책표 **출력**으로 추가. 사람에게는 profile을, 기계에는 unit을 보여준다 |
| B2 | 명령 "승인 여부와 진행 상태를 서로 다른 상태로 관리" vs D-15 "단일 5상태, 검증 상태는 나중" | 정면 충돌은 아니나 D-15가 "직교 3세트 동시 도입"을 보류함 | `status`(draft/active/done/dropped/superseded) 하나 + `approved_at`/`approved_by` 사실 필드 + evidence 참조. 검증(verified/stale)은 저장하지 않고 /plan-close가 HEAD 비교로 계산. **frontmatter 스키마라 나중에 바꾸면 전수 마이그레이션 → 지금 결정** |
| B3 | 명령의 위험 행동 목록(결제·권한 확대·공개·운영 배포·운영 데이터·마이그레이션·계정·삭제·**main 병합·다른 작업 공간 삭제**) vs hard gate 8(facet) | 층위가 다름: 전자는 "지금 하려는 행동", 후자는 "요청이 건드리는 영역" | 합치지 않고 `execution-guards.yaml`을 별도로 둠. 가드는 역할 계약 + Claude permission deny + Codex sandbox/approval + Orca `gate-create`로 집행 |
| B4 | 명령의 "필요한 스킬·외부 도구를 스스로 찾을 수 있다" | 무제한 탐색은 공급망·권한 위험(참고 메모 다수가 `@latest` 실행·전역 설치를 경고) | 레지스트리에 등록된 능력만 자동 선택, 미등록 도구는 **후보 제시 + 승인 후 등록** |
| B5 | 명령의 "품질·속도·비용을 고려해 모델 선택" vs K-12·D-44 | 비교할 측정치가 없고 provider ID 추정 금지 | v1은 역할별 바인딩(첫 등록 시 승인) + task override. 자동 선택은 fixture 축적 후 T0 저위험 한정 |
| B6 | 명령의 디자인·브라우저·파생 지식·자기개선 능력 전부 | 정본은 v2/v3. 명령도 "초기에 과다 도입 금지" | 단계 M5~M7로 배치. **DESIGN.md 계약과 `ui` facet 시 UI 상태표 섹션**만 v1 템플릿에 자리를 둠 |
| B7 | 명령 "Claude Code에서 먼저 완전히 작동" vs 정본 합격 기준 "역할 교체 재현" | 순서 문제 | M1(Claude 단독 T0) → M2(교차 T1). **M1 통과는 v1 완료가 아님**을 명시 |

**C. 정본 문서 ↔ 저장소 실물**

- K-20이 전제한 `rg`가 정식 설치가 아님(§1.2). — 수정 필요.
- K-24(`.harness/runs/` git 제외)를 지킬 `.gitignore`가 없음.
- K-41의 `THIRD_PARTY_NOTICES.md`, V-8의 부착 상태 파일, C-H3의 라이선스 필드가 없음.
- 투영표는 `.agents/skills/*`를 Codex 네이티브로 두는데 실물은 **심링크**. 이 저장소(macOS)에서는 동작하지만 폐기 아이디어("심볼릭 링크면 변환 버그 0")가 지적한 Windows·trust 문제는 남음 → 부착 대상 프로젝트에는 어댑터가 **실제 파일**을 씀.
- 원천 대화 77MB가 커밋됨(S11·S14 각 22~23MB). 하네스 기능과 무관하지만 clone 비용 → §9 저위험 항목.

### 2.5 책임 분배 (질문 1)

| 책임 | 소유자 | 하네스가 하지 않는 것 |
| --- | --- | --- |
| 요청 해석 프로토콜, 정책표, 템플릿, ID·frontmatter·상태 규약, 역할 계약, TaskEnvelope/ResultEnvelope/Evidence 스키마, 검증 스크립트, 어댑터, 부착·업데이트, 출처 추적, fixture·시나리오 | **Romeo(공통 하네스 저장소)** | 프로젝트의 전략·PRD 내용·결정을 소유하지 않음 |
| Brief/Spec/Charter 실물, `current/`, decisions, 작업 상태, evidence 기록, 프로젝트 override, `DESIGN.md`/`PRODUCT.md`, 코드·테스트 | **개별 프로젝트 저장소** | 하네스 규칙을 복제해 수정하지 않음(override만) |
| Run·Task·Dispatch·worktree·메시지·gate·재시도·대기 | **Orca** | 하네스는 두 번째 스케줄러가 아님(D-20) |
| LLM 실행, 네이티브 skill/agent/hook/MCP 로딩, 구조화 출력 | **Claude Code / Codex** | 워크플로우 상태를 프롬프트가 통제하지 않음 |
| 변경 이력·SHA | **git** |  |
| 파생 기술 지식 조회 | **OpenWiki(v2, 선택)** | 기획·상태의 원본이 아님(D-23) |
| 브라우저 실제 화면 | claude-in-chrome(개인 세션) / Playwright(반복) / Orca 내장 브라우저(장시간) | 하네스는 능력 이름만 정의 |
| 의미적 사실 확정, gate 승인, 최종 수락 | **사람** |  |

---

## 3. 추천 구조

### 3.1 구성요소와 역할·실패 시 영향

| 구성요소 | 왜 필요한가 | 전체에서의 역할 | 잘못 설계하면 |
| --- | --- | --- | --- |
| **공통 코어 `core/`** (정책표·스키마·템플릿·워크플로우 본문·역할·원칙) | 두 런타임이 "같은 의미"를 갖게 하는 유일한 원본 | 어댑터의 입력, 프로젝트의 규칙 출처 | 코어에 도구명·모델명이 스며들면 벤더 종속(C-C6 위반) |
| **정책표 + `romeo route`** (결정론) | 확정된 unit·mode·facet·gate에서 문서 패키지·차단·profile·역할 요구를 재현 가능하게 계산 | LLM 제안과 문서 생성 사이의 "컴파일러" | LLM이 패키지를 정하면 같은 입력에 다른 문서가 나오고 `fired_rules` 추적 불가 |
| **기획 모듈** (`/plan`, 템플릿 3, Planning Capsule) | 요청을 승인 가능한 최소 문서로 | 사용자와 하네스의 첫 접점 | PRD 강제·템플릿 폭발(C-B1 위반) |
| **개발 모듈** (implementer/reviewer 역할, TaskEnvelope, evidence, `/plan-close`) | 구현·리뷰·검증을 분리하고 증거를 SHA에 묶음 | "만들었다"를 "검증했다"로 바꾸는 장치 | 실행기 출력 그대로를 완료 근거로 쓰면 S07/S08형 오판 |
| **디자인 모듈** (v2: `DESIGN.md` 계약, 생성 규칙 1, 감사 규칙 2, visual-qa) | UI 산출물이 있을 때만 붙는 조건부 트랙 | `ui` facet이 켜질 때 브리프에 상태표·시각 증거 요구 | 모든 프로젝트에 취향을 강제(D-37 위반) |
| **모델·실행기 연결부 `adapters/claude`, `adapters/codex`** | 코어 → 네이티브 형식 컴파일 + CLI 출력 흡수 | 투영표(C-C 투영표) 구현체 | 심링크·복사에 의존하면 trust/Windows/경로 문제(폐기 아이디어) |
| **외부 도구 연결부** (`adapters/orca` 런북, `capabilities.yaml`, `doctor`) | 실행 위임과 능력 판정 | Orca 명령 호출 규약, 부재 능력 보고 | 하네스가 dispatch 상태를 자체 저장하면 이중 스케줄러 |
| **부품 조립 계층** (`vendor/<repo>@<sha>/`, `provenance/imports.yaml`, 채택 확정 게이트, 통합 규약 fixture) — 개정 3 | 검증된 부품을 원문 그대로(`verbatim`) 또는 설치·연결(`install`)로 붙이되 충돌을 규약으로 막는다 | 라우터가 켜는 대상; 어댑터가 투영하는 입력; 게이트가 확정하는 목록 | 부품이 자체 트리거·자체 기획·자체 경로를 가지면 이중 기획·고아 산출물·hook 종속이 생긴다(K-60~K-69) |
| **프로젝트별 설정** (`.harness/romeo.project.yaml`, `AGENTS.md` 프로젝트 블록) | 공통 기본값의 안전한 확장·일부 비활성화 | 업데이트 시 보존 대상 | override가 코어를 복제하면 드리프트 |
| **문서와 상태** (`docs/work/<id>/`, `docs/current/`, decisions, frontmatter) | 과거 의도와 현재 사실 분리, 경로 불변 | 다음 세션의 재개 체크포인트 | 상태별 폴더 이동 → 링크 파손·병렬 충돌 |
| **검증 체계** (fixture, parity fixture, 시나리오 런북, CI) | 하네스 자체를 대표 상황으로 반복 평가 | 규칙 정확도·벤더 동등성의 근거 | 단위 테스트만 있으면 "설치됐다"와 "동작했다"를 구분 못함 |

### 3.2 흐름 다이어그램 (질문 3·4의 답)

```text
[요청 입력]
   │
   ▼
┌───────────────────────── 공통 코어 core/ (벤더 중립) ─────────────────────────┐
│ ① /plan · 재사용 검색(rg) → LLM 제안 카드                                      │
│    사실 / 가정 / 미확인 / unit·mode·facet 후보 / 5요인(범위·불확실성·영향·      │
│    되돌리기·조율) 설명 / 2질문(blast radius·불확실성) / hard gate 8 체크리스트   │
│                          │ 사람 1클릭 확정 (shadow mode 20건)                  │
│ ② romeo route (정책표, 결정론) ── policy_version · fired_rules 기록             │
│    unit × mode × facet × gate → 문서 패키지 · 차단 상태 · profile(quick/standard/│
│    deep) · 리뷰 요구 · 격리 범위(코드만 / 환경 포함) · 필요 능력                 │
│ ③ 문서 생성 (템플릿 3 · ID · frontmatter) → docs/work/<id>/                     │
│ ④ 승인: Tech Spec approved_at 기록 = SPEC_READY (구현 착수의 유일한 강제 선행)   │
│ ⑤ 실행 프로필: 역할 바인딩(implementer/reviewer) · 능력 레지스트리 · 가드        │
│    + 부품 활성(K-60: 라우터가 켤 때만): profile≥standard → superpowers 규율 세트, │
│      mode=discovery/T2 → BMAD·CIS 링크, facet=ui/brand → 디자인 규칙            │
│    부족 능력 → BLOCKED_CAPABILITY 보고 (우회 금지)                               │
│ ⑥ TaskEnvelope 생성 (spec_ref+hash · base_sha · allowed_paths · guards ·        │
│    required_checks · output_schema)                                             │
└───────────────┬───────────────────────────────────────┬────────────────────────┘
                │                                       │
       ┌────────▼────────┐                     ┌────────▼────────┐
       │  Claude 어댑터   │                     │  Codex 어댑터    │
       │ .claude/skills·agents │               │ .agents/skills · .codex/agents │
       │ CLAUDE.md(@AGENTS.md) │               │ AGENTS.md                      │
       │ claude -p --json-schema │             │ codex exec --output-schema --json -o │
       └────────┬────────┘                     └────────┬────────┘
                │  실행 위임 — worktree·dispatch·gate·대기·재시도는 Orca 소유    │
                └───────────────────┬───────────────────┘
                                    ▼
                  [Orca run-create → task-create → worker-start
                   → check --wait → gate-create/resolve → worker-release]
                                    │ ResultEnvelope
                                    ▼
┌────────────────────────────── 검증 체계 ──────────────────────────────┐
│ ⑦ romeo evidence: HEAD SHA · dirty hash · commands · exit codes ·      │
│    artifact hash → docs/work/<id>/evidence/<run>.yaml (원시 로그는     │
│    .harness/runs/ git 제외)                                            │
│ ⑧ 반대 런타임 read-only 리뷰 → findings · gate 판정                    │
│ ⑨ /plan-close: 스키마·링크·미체크·예산·open-loop·stale·리뷰 존재 검사   │
│    → status 확정 → current/ 승격 후보 · decisions 추가                  │
└────────────────────────────────────────────────────────────────────────┘
```

**순서(질문 4):** 분류 → 정책 계산 → 문서 → 승인 → 실행 프로필(역할·도구·모델·작업 공간) → 실행 → 증거 → 리뷰 → 종료 판정 → 승격. 도구·모델 선택이 정책 계산 **뒤**에 오는 이유는, 무엇이 필요한지(profile·facet·능력)가 확정되어야 "누가·어디서" 실행할지 결정할 수 있기 때문이다.

**코어와 모듈의 연결(질문 3):** 모듈은 별도 코드가 아니라 **정책표의 조건부 행 + 템플릿의 조건부 섹션 + 워크플로우 본문**이다. 예: `ui` facet → Compact Brief에 "UI 상태표" 섹션 요구 + (디자인 모듈 활성 시) visual-qa 리뷰 요구. 프로젝트 부착 상태 파일의 `modules:`가 어떤 행을 켤지 결정한다. 그래서 모듈 추가 = 정책 행·섹션·스킬 본문 추가이지 새 실행 경로가 아니다.

### 3.3 분리해야 하는 것 (질문 5)

| 벤더 중립(코어·프로젝트 문서) | Claude 전용 | Codex 전용 | Orca 전용 |
| --- | --- | --- | --- |
| 정책표, 스키마, 템플릿, 워크플로우 본문(도구명 없음), 역할 계약(능력 선언), 원칙(`AGENTS.core.md`), evidence·fixture, `docs/**`, `.harness/romeo.project.yaml` | `.claude/skills/*`, `.claude/agents/*.md`, `CLAUDE.md`(`@AGENTS.md` import + Claude 주석), `.claude/settings.json`(permission deny만; 상태 hook 없음), `.mcp.json`, `claude -p` 플래그 매핑 | `.agents/skills/*`, `.codex/agents/*.toml`, `AGENTS.md`(managed block), `.codex/config.toml` 조각, `codex exec` 플래그·NDJSON 파싱 | `adapters/orca/` 런북(run/task/worker/gate 호출 규약). 다른 오케스트레이터로 바꿔도 TaskEnvelope는 불변 |
| (개정 3) `vendor/<repo>@<sha>/` 원문 스킬(도구명 없음을 확인한 것만, 수정 0), `provenance/imports.yaml`, 통합 규약 fixture | vendored 스킬을 `.claude/skills/superpowers-*`로 투영; deny 목록에 부품이 유도하는 외부 쓰기(K-66) | vendored 스킬을 `.agents/skills/superpowers-*`로 투영(실제 파일); BMAD discovery 능력은 Codex 미지원 시 `capabilities.yaml`에 정직 표기 | BMAD·OpenWiki는 Orca가 아니라 프로젝트에 설치되는 부품 — 런북 밖. Orca는 `install` 부품 |

### 3.4 추천이 달라지는 조건 (대안 최대 2개)

- **대안 1 — Codex 교차 리뷰를 6개월 이상 안 쓸 경우:** Codex 어댑터·parity fixture를 M2에서 빼고 reviewer를 Claude 서브에이전트(`--agents`)로 둔다. 단 TaskEnvelope/ResultEnvelope는 그대로 두어 나중에 붙일 수 있게 한다. 이 경우 v1 합격 기준(역할 교체)이 "같은 런타임 내 역할 분리"로 약해짐을 명시해야 한다.
- **대안 2 — A-06(Orca 안정성)이 M2에서 깨질 경우:** `adapters/orca` 대신 `claude -p`/`codex exec` 직접 호출 래퍼 + `orca worktree create`(worktree만)로 축소 운영. 이때도 dispatch 상태를 하네스가 저장하지 않고 evidence 파일만 남긴다.

### 3.5 상태 계약 (Codex 리뷰 F-01·F-04 반영)

문서 승인·실행 진행·검증의 소유권을 한 곳에 고정한다. 층을 섞으면 "승인됐다"와 "구현됐다"와 "검증됐다"가 다시 뒤섞인다.

| 층 | 값 | 소유자 | 저장 위치 |
| --- | --- | --- | --- |
| 문서 생명주기 | `status: draft → active → done / dropped / superseded` (5값) | Romeo(`/plan`, `/plan-close`) | 문서 frontmatter |
| 승인 사실 | `approved_at`, `approved_by` — 상태가 아니라 사건 기록. `active`는 `approved_at` 없이 될 수 없다 | 사람 | 문서 frontmatter |
| 실행 상태 | Run·Task·Dispatch·worktree·gate·재시도 | **Orca** | Orca. 하네스는 evidence에 `run_id`·`task_id`·`dispatch_id`만 기록 |
| 검증 상태 | 저장하지 않는다. `/plan-close`가 evidence의 `head_sha`·`dirty_tree_hash`를 현재 값과 비교해 **계산**한다 | Romeo(계산) | 없음(계산 결과는 close 로그) |

`dirty_tree_hash` 정의: tracked 파일의 수정분(`git diff`), staged 변경(`git diff --cached`), untracked 파일(ignored 제외)의 **경로와 내용**을 경로 순으로 정렬해 sha256 한 값. evidence 기록 시점 값과 close 시점 값이 다르면 stale. 따라서 stale 테스트는 네 경우다 — 커밋 이동, tracked 수정, staged 변경, untracked 추가 — 모두 close가 거부해야 정상이다.

**게이트 두 개:** 핵심 동등성 게이트(M2 종료: 역할 교체 parity PASS)와 v1 릴리스 게이트(M4 종료: 정본 V-0~V-10 전부 관찰 가능한 증거로 충족). "v1 완료"는 후자에서만 선언한다.

---

## 4. 첫 번째 버전의 범위 (질문 2)

### 4.1 끝까지 작동해야 하는 최소 흐름

```text
[M1 — Claude 단독, 현재 작업 공간]
T0 요청 "validate-repo-archive.sh의 rg 의존을 grep -E 폴백으로 보강" (실제 필요 작업)
 → /plan: 제안 카드(사실·가정·후보 T0·delivery·facet 없음·gate 없음·profile quick)
 → 사람 확정 → romeo route → 패키지 = Tech Spec 1개(Planning Capsule ≤ 20줄)
 → docs/work/chg-2026MMDD-rg-fallback-xxxx/spec.md (approved_at 기록)
 → 구현(현재 worktree) → romeo evidence (HEAD SHA·명령·종료코드·변경 파일 해시)
 → /plan-close PASS → status: done

[M2 — 교차 런타임, Orca 위임]  ← v1 유일 합격 기준
T1 요청 "아카이브 스키마에 라이선스 필드 추가(_source.md 줄 + 검증 스크립트 + 인덱스 열 + 기존 18개 backfill)"
 → /plan: T1·delivery·facet 없음(저장소 내부 문서 스키마 변경이라 hard gate 미발동 — M2는 게이트 없는 T1을 일부러 고른다, 리뷰 F-02)·profile standard
 → Compact Brief + Tech Spec → approved_at
 → TaskEnvelope(implementer) → orca run/task/worker-start --agent claude --worktree new-child
 → check --wait → ResultEnvelope → evidence
 → TaskEnvelope(reviewer, read-only) → Codex를 `-s read-only`로 실행 (같은 worktree; 쓰기 시도는 런타임이 거부 — 리뷰 F-03)
 → 리뷰 findings + gate 판정 → /plan-close PASS
 → 역할 교체(Codex 구현 / Claude 리뷰)로 같은 base SHA에서 재현
 → parity 보고: 두 ResultEnvelope 스키마 유효 · 같은 required_checks 실행 · 같은 gate 판정
```

### 4.2 포함 / 의도적 제외

| v1 포함 | v1 제외(도입 트리거) |
| --- | --- |
| fixture 15~20건(V-0), 정책표 3종(classification·packages·execution-guards), `capabilities.yaml` | 인덱스·catalog·SQLite(문서 100+) |
| 템플릿 3(Tech Spec+Capsule, Compact Brief, Charter) + 길이 캡 | 큐·DB(동시 요청자 2+) |
| `/plan`, `/plan-close`, `romeo` CLI(`route`·`new`·`validate`·`evidence`·`close`·`compile`·`attach`·`doctor`·`fixtures`) | hook 파이프라인(기각) |
| 역할 2(implementer/reviewer, reviewer는 런타임 read-only 강제) + 바인딩 파일 + task override | 전문 역할 확장·병렬 협의(C-D5 v2) |
| Claude 어댑터(전체) + Codex 어댑터(reviewer·parity 최소) + managed marker/source hash | 자동 모델 라우팅(fixture 축적 후) |
| Orca 연결 런북(`/repo` 패턴 재사용) + gate-create 승인 | 자체 DAG·relay·worktree 폴백(기각) |
| Evidence 계약(C-E1 필드) + stale 계산 | 검증 상태 저장(evidence 파이프라인 안정화 후) |
| 최소 부착 상태 파일 `.harness/romeo.project.yaml`(하네스 버전·활성 모듈만, V-8 — M2에서 하네스 자체에 생성) | `attach`·`update --dry-run`·롤백(M5 = v1.1, 릴리스 게이트 이후), 업데이트 자동 병합·upstream update PR(v3) |
| `ui` facet 시 UI 상태표 섹션, `DESIGN.md` 자리 | 디자인 트랙 4스킬·visual-qa(UI 프로젝트 발생 시) |
| T0 슬라이스(M1) + T1 교차 슬라이스(M2) + shadow mode 20건 | OpenWiki·converge(v1 통과 후), 지표 8종 대시보드(카운터 4개만 v1) |
|  | 비코드 프로젝트 지원(D-43: 경량 `AGENTS.md` 부착만) |

**게이트 두 개(리뷰 F-01 반영):** ① **핵심 동등성 게이트** = M2의 역할 교체 재현 통과 — 하네스가 존재할 이유의 증명. ② **v1 릴리스 게이트** = 정본 V-0~V-10 전부 관찰 가능한 증거로 충족(Charter 양식·최소 부착 상태 파일·shadow mode 20건 포함) — M4 종료 시점에 판정하며 여기서만 "v1 완료"를 선언한다. 문서·코드 존재는 완료가 아니다(K-51).

---

## 5. 예상 폴더와 파일 구조

### 5.1 공통 하네스 저장소 (이 저장소) — `[M0]`~`[M6]`는 생성 시점, 표시 없는 것은 기존

```text
Romeo-Harness/
├── README.md · CLAUDE.md · LICENSE(결정 대기)          기존
├── .gitignore                                          [M1] .harness/runs/, .harness/cache/
├── AGENTS.md                                           [M2] core/principles에서 컴파일(managed block) — 하네스 자체 dogfood
├── THIRD_PARTY_NOTICES.md                              [M2] provenance/imports.yaml에서 생성
├── core/                                               벤더 중립 원본
│   ├── policy/
│   │   ├── classification.yaml                         [M0] unit·mode·facet·hard gate 8·2질문 rubric·충돌 우선순위·profile 규칙
│   │   ├── packages.yaml                               [M0] (unit×gate×facet) → 문서·섹션·차단·리뷰 요구·격리 범위·예산
│   │   ├── execution-guards.yaml                       [M0] 실행 시점 위험 행동 → 승인 요구·설명 항목
│   │   └── capabilities.yaml                           [M2] 능력 이름 → 확인 방법(프로브) → 대안
│   ├── schemas/                                        [M0~M2] frontmatter · proposal · task-envelope · result-envelope · evidence · attach-state (JSON Schema)
│   ├── templates/                                      tech-spec.md(Capsule 포함)[M0] · compact-brief.md[M2] · charter.md[M3] · decision-entry.md[M4]
│   ├── workflows/                                      [M0~M2] plan/SKILL.md · plan-close/SKILL.md · implement/SKILL.md · review/SKILL.md (도구명 없음)
│   ├── roles/                                          [M2] implementer.yaml · reviewer.yaml (capability 선언·권한·출력)
│   └── principles/AGENTS.core.md                       [M2] 공통 원칙(사실/가정/추천 구분, 실행≠완료, 위험 승인 …)
├── adapters/
│   ├── claude/                                         [M2] 컴파일 규칙 + 출력 템플릿(.claude/*, CLAUDE.md import, settings deny)
│   ├── codex/                                          [M2] .agents/skills, .codex/agents/*.toml, AGENTS.md, NDJSON 파서
│   └── orca/RUNBOOK.md                                 [M2] run/task/worker/gate 호출 규약 (envelope ↔ --spec 매핑)
├── bin/romeo  +  romeo/ (Python 패키지)                [M0~] route · ids · frontmatter · validate · evidence[M1] · compile[M2] · attach[M5] · doctor[M3] · fixtures
├── fixtures/requests/*.yaml                            [M0] 요청 15~20건;  fixtures/parity/                 [M2]
├── tests/                                              [M0~] unittest(표준 라이브러리)
├── scenarios/                                          [M3~] §8의 시나리오 런북(기대 판단·산출물·증거)
├── vendor/<owner>-<repo>@<sha>/                        [M2~] verbatim 원문(수정 0) + LICENSE 사본. 어댑터가 두 런타임으로 투영 (개정 3)
├── provenance/imports.yaml                             [M2] 채택 요소별 출처·SHA·라이선스·adoption(5단계)·status(proposed→accepted)·게이트 결정 기록
├── skills/repo-archive/ · .claude/commands/repo.md · .agents/skills/  기존(심링크는 M2에서 컴파일 산출물로 대체 검토)
├── scripts/                                            기존 + validate 보강[M1]
├── archive/                                            기존 18개
└── docs/                                               기존 정본 + docs/work/<id>/ [M1] (하네스 자체 작업 단위)
```

### 5.2 개별 프로젝트 저장소 (부착 후)

```text
<project>/
├── AGENTS.md                      <!-- romeo:managed start v0.1.0 sha256:… --> 공통 원칙 … <!-- romeo:managed end --> + 프로젝트 블록(보존)
├── CLAUDE.md                      @AGENTS.md import + Claude 전용 메모
├── .claude/ skills/plan, skills/plan-close, agents/implementer.md, agents/reviewer.md, settings.json(permission deny만)
├── .agents/skills/plan, plan-close         (Codex, 실제 파일)
├── .codex/agents/implementer.toml, reviewer.toml
├── .mcp.json                      선택
├── .harness/
│   ├── romeo.project.yaml         harness_version · policy_version · modules · runtimes · overrides · managed_files(hash)
│   ├── bindings.yaml              역할 → 런타임/모델/effort (첫 등록 시 승인)
│   └── runs/                      git 제외(원시 로그·NDJSON)
├── docs/
│   ├── current/                   살아있는 사실(별도 저술)
│   ├── work/<unit-id>/            brief.md · spec.md · charter.md · evidence/<run>.yaml  (경로 불변)
│   ├── decisions.md               append-only
│   ├── PRODUCT.md · DESIGN.md     UI 프로젝트만
└── src/ …
```

**소유 분리 요약:** 하네스는 `core/`·`adapters/`·`bin/`·`fixtures/`·`provenance/`를 소유하고 프로젝트에는 **생성물(managed)** 과 **상태 파일**만 둔다. 프로젝트는 `docs/**`·`.harness/*.yaml`·`AGENTS.md` 프로젝트 블록·코드를 소유한다. 생성된 `.claude/`·`.codex/`·`.agents/` 파일은 커밋한다(K-25). `docs/work/` 안에 `PII·인터뷰 원본·크리덴셜`은 두지 않는다(K-23).

**아직 만들지 않는 것:** `openwiki/`, `docs/evidence/`(연구 근거 계층), `docs/releases/`, `core/design/`, `.romeo/index.*`, `catalog.yaml`, `adapters/<third-runtime>/`.

---

## 6. 참고 저장소 활용 계획 (개정 3)

먼저 §2에서 능력과 완료 기준을 정의했으므로, 각 저장소는 **그 빈칸을 채우는 부분만** 가져온다. 판정 기준은 capability-map의 5기준(목적 적합성·경계 충돌·채택 단위·유지비·출처 추적)과 **통합 규약 K-60~K-69**(§6.2)다.

개정 3에서 "전체 도입 / 일부 재작성 / 원칙만 참고 / 제외" 4단계를 **채택 방식 5단계**(D-51)로 바꿨다. 재작성은 기본값이 아니라 통합 규약을 못 지킬 때의 강등 경로다. 사용자가 직접 써보고 지목한 부품(BMAD/CIS·Superpowers·OpenWiki·디자인 스킬)은 능력 후보가 아니라 조립 대상이다(D-50).

| 방식 | 뜻 | 어디에 |
| --- | --- | --- |
| `install` | 외부 도구로 설치·연결. 코드 미복사. 라우터가 호출하고 산출물을 링크로 흡수 | Orca, BMAD 본체+CIS, OpenWiki, 홈 레벨 스킬 |
| `verbatim` | 고정 SHA 원문 복사, 수정 0. `vendor/<repo>@<sha>/`에 두고 어댑터가 두 런타임으로 투영 | Superpowers 규율 세트, WIG 파일 2개, taste v2, impeccable 스킬 본문·판정, ui-ux-pro-max(라이선스 확인 후) |
| `rewrite` | 원칙을 코어 형식으로 재작성 + 출처 주석 | writing-plans task 구조 → Tech Spec 템플릿, impeccable `DESIGN.md` 스키마, rulesync 5단계 → `romeo update`, slugify 규칙 |
| `principle` | 참고만, 미복사 | OMA, open-design, MengTo, ARIA, tokens, anthropics/skills |
| `excluded` | 채택 안 함 | cc-switch, orca-cli/orca, storybook |

**아래 표의 "방식"은 후보다.** 어느 파일을 가져올지는 계획에서 정하지 않고 §6.1 게이트에서 사용자가 파일 단위로 확정한다(D-52).

| 저장소 | 채택 후보 요소 | 방식(후보) | 채택 이유 | 충돌 지점 → 통합 규약 처리 | 라이선스 | 게이트 | 검증 방법 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| obra/superpowers | **채택 7종 14파일**: `test-driven-development`(+`writing-good-tests.md`) · `systematic-debugging`(+참고 4·`find-polluter.sh`) · `verification-before-completion` · `requesting-code-review`(+`code-reviewer.md`) · `receiving-code-review` · `using-git-worktrees` · `finishing-a-development-branch`. **보류 4종**: `writing-plans` · `executing-plans` · `subagent-driven-development` · `dispatching-parallel-agents` | **`verbatim`** 7종 (M2, G-M2 닫힘 2026-08-27) — D-67. 보류 4종은 `deferred`(M3 재검토), `brainstorming`·`using-superpowers`·`writing-skills`·visual companion 은 `rejected` | 승인 이후 개발 규율의 빈칸(D-33). 채택 7종은 **나가는 참조가 세트 안에서 닫혀 깨진 링크 0**(고정 SHA 실측); 공식 porting guide가 C-C6의 출처라 원문 그대로가 벤더 중립 | **보류 사유(실측)**: `writing-plans` 는 "Every plan MUST start with this header" 로 계획 원본을 2개로 만들고(K-61) 제외 확정된 `brainstorming` 을 전제(깨진 링크) · `executing-plans` 는 제외 확정된 `using-superpowers/references/` 를 읽으라 지시(깨진 링크) + 6·7번을 REQUIRED SUB-SKILL 로 요구 · `subagent-driven-development` 는 "A running plan does not wait on a human" 으로 D-60 승인 모델과 정반대이고 자체 ledger 로 K-63 침범 · `dispatching-parallel-agents` 는 `Subagent (general-purpose)` 리터럴 지시로 전역 Orca 규칙과 충돌. **채택분 override**: `using-git-worktrees` 의 도구 지목 → `orca worktree create`, `finishing-a-development-branch` 의 merge/push/삭제 → deny 목록(K-66), `requesting-code-review` 의 `general-purpose` → 역할 바인딩 치환 | MIT | G-M2 **닫힘** | doctor discovery 양 런타임(A-11); 충돌 fixture 3종(K-68); 깨끗한 세션에서 T0 요청 시 brainstorming이 안 뜨고 `/plan`만 뜨는 transcript; 구현 후 fresh command output |
| BMAD 본체 + CIS | 라우터가 추천할 스킬 후보: `bmad-brainstorming`, `bmad-product-brief`, `bmad-prd`, `bmad-cis-design-thinking` / `innovation-strategy` / `problem-solving` / `storytelling`; 산출물 `_bmad-output/**` | **`install`** 프로젝트별 + `/plan` 링크 (M3) — D-55 | 불확실성 축(D-32); 사용자 실사용("내가 써본 기획 하네스 중 가장 정교", `~/bmad-ordi` 6.10.0+CIS 0.2.1) | 매 template-output 뒤 체크포인트 대기·persona 인사 → K-60 라우터가 discovery/T2에서만 켬 · `_bmad/`+`customize.toml`+`uv run` = 3번째 SSOT → K-63 벤더링 없음 · `stepsCompleted` → K-63 참고용 · Claude 전용 설치(`ides: [claude-code]`) → K-68 정직 표기(A-12) · 본체 미아카이브 → Q-06 선행 | MIT (CIS 고정 SHA 실물; 본체는 아카이브 후 확인) | G-M3 | `capabilities.yaml` `discovery.bmad` 프로브; discovery fixture 카드가 스킬 추천 + 산출물 링크 요구; 링크 없는 산출물은 close 거부 |
| langchain-ai/openwiki | 도구 자체(`begin`/`finish` lifecycle, Claims, managed block) | **`install`** (v2, A-07) — D-56. 개정 2의 "원칙만 참고" 라벨은 오기 | 파생 지식 계층(D-23) | managed block 이름 → K-64 소유자 마커 · 계획 문서를 현재 기능으로 오해 → K-62 `.openwikiignore`에 `docs/work/**` · worktree마다 갱신 → D-24 기준 브랜치 반영 후 1건씩 | MIT | G-M7 | 실제 프로젝트 1건 부착 후 갱신 3회, `openwiki_finish.status=complete` |
| pbakaus/impeccable | 스킬 본문, finish-reviewer `recapture/ship` 판정, `PRODUCT.md`/`DESIGN.md` 계약 | **`verbatim`**(스킬·판정) + **`rewrite`**(계약 스키마) (M6) | 디자인 완료 기준(C-G4) | CLI·hook·4 서브에이전트 → K-65·K-66 제외; "hook exit 0은 증거 아님" | Apache-2.0 (NOTICE) | G-M6 | 375/768/1440 스크린샷 없이는 close 불가 |
| vercel-labs/web-interface-guidelines | `AGENTS.md`(MUST/SHOULD/NEVER), `command.md`(`file:line` 출력 계약) | **`verbatim`** 파일 2개 (M6) | UI 감사 규칙 | `install.sh`(전역 홈·`main` 비고정) → K-67 제외 | MIT | G-M6 | 감사 결과가 `file:line`으로 나오고 예외 승인 기록이 남는지 |
| Leonxlnx/taste-skill | `design-taste-frontend` v2(리디자인 안전선 포함), 실패 분류(`INPUT_GAP`·`DEPENDENCY_MISSING`·`VISUAL_QA_FAIL`…) | **`verbatim`** 1개, 랜딩·브랜드 한정(D-37) + 실패 분류는 `rewrite`(ResultEnvelope `blocked_reason`) | 랜딩 생성 규칙 1 | 취향 강제 → 프로젝트 `DESIGN.md` 우선 · 이미지 생성 비용 → K-66 guard | MIT | G-M6 | 시나리오 4 |
| nextlevelbuilder/ui-ux-pro-max-skill | skill/data(디자인 시스템 검색), `design-review` 서브에이전트("브라우저에서 본 것만 finding") | **라이선스 확인 트랙** → `verbatim`(`cli/` 제외) — D-57 | 사용자 실사용(`~/readly-sologis` v2.2.3, `design-system/sologis/MASTER.md`) | `cli/README.md` CC-BY-NC 표기 → K-42 확인 · `--global`·`stack/` MCP `@latest` → K-66·K-67 제외 · 메타데이터 드리프트 | 루트 MIT / `cli` 표기 충돌 | G-M6 | 라이선스 판정 기록; 검색 `diagnostics` 보존; UI 완료는 스크린샷·콘솔 증거 |
| (홈 레벨) `race`, `orca-cli`, `orchestration` 스킬 | 병렬 비교·worktree·dispatch 실행 | **`install`** (사용 중) | 이미 존재, Orca 우선 규칙 | 하네스는 계약(같은 base SHA·같은 TaskEnvelope)만 정의 | 사용자 자산 | — | M2에서 실제 호출 |
| first-fluke/oh-my-agent | `.agents` SSOT + adapter compiler 패턴, `gate.passed`, paired eval 개념 | **`principle`** (M2·M7) | 벤더 중립 투영의 선례(D-34) | 자체 dispatch·global install → K-63 런타임 미설치 | MIT | — | `romeo compile` 산출물이 두 런타임에서 discovery되는지 |
| dyoshikawa/rulesync | `doctor → dry-run → 사람 diff 승인 → generate → check` 5단계, managed 삭제 안전장치 | **`rewrite`** (M5 `romeo update`) | 업데이트 안전 절차 | Node CLI 런타임 = 3번째 SSOT → K-63 제외 | MIT | — | 시나리오 10 |
| anthropics/skills | SKILL.md frontmatter 규약, `quick_validate`, trigger eval | **`principle`** (M0) | 스킬 형식 표준 | 스킬별 라이선스·루트 LICENSE 없음 → K-42 텍스트 복사 금지 | 스킬별 `LICENSE.txt` | — | `romeo validate`가 SKILL frontmatter 검사 |
| sindresorhus/slugify | slug 정규화 규칙 | **`rewrite`** (M0, Python 표준 라이브러리) | ID 생성 규칙 | JS 의존 불필요 | MIT | — | ID 충돌 테스트 |
| nexu-io/open-design | run ledger 원칙("이번 run이 실제로 쓴 entry artifact"), 실패 분류 | **`principle`** (M2 evidence) | evidence 계약 정당화 | daemon 도입 제외 | Apache-2.0 | — | evidence에 `changed_files`가 비면 done 불가 |
| MengTo/Skills | iterate-until-verified(실행자/판정자 분리), publish guard | **`principle`** (M2 role) | reviewer 독립성 근거 | 130개 스킬 자동 발견 → K-60 금지 | MIT | — | reviewer의 `changed_files == []` 검사 |
| w3c/aria-practices | 키보드·ARIA 패턴 | **`principle`** (M6, 링크 참조) | 접근성 판단 근거 | 문서 복사 금지(W3C 고지) | W3C Software and Document License | — | 접근성 항목이 브리프 상태표에 포함 |
| design-tokens/community-group | 토큰 교환 형식 | **`principle`** (M6 `DESIGN.md` 토큰 표기) | 토큰 일관성 | 복사 금지 | W3C License | — | — |
| farion1231/cc-switch | (없음) | **`excluded`** | 공급자 전환·프록시는 범위 밖 | 라이브 설정 덮어쓰기 위험 | MIT | — | — |
| orca-cli/orca | (없음) | **`excluded`** (K-13) | 실제 Orca 제품과 다름 | — | MIT | — | — |
| storybookjs/storybook | (없음) | **`excluded`**; UI evidence surface로 v2 조건부 | — | 대형 런타임 | MIT | — | — |
| (미아카이브) GitHub Spec Kit | `converge` 개념 | **`principle`** v2 재검토 (D-40, Q-01) | — | — | 미확인 | — | — |

**조합 시 중복·충돌·과설계 위험** (각 항목의 규약 대응은 §6.2)

1. superpowers `brainstorming` + `/plan` = 이중 기획 → K-61, `brainstorming` 제외.
2. OMA/rulesync 컴파일러 + 자체 어댑터 = SSOT 3개 → 자체 어댑터 하나만(K-63).
3. impeccable hook + "핵심 전이 hook 비의존" → K-65, 판정 규칙만.
4. 디자인 3종(taste·impeccable·WIG)이 서로 다른 취향 → WIG=감사, impeccable=계약, taste=랜딩 한정; 프로젝트 `DESIGN.md`가 우선.
5. OpenWiki managed block + Romeo managed block이 같은 `AGENTS.md` → K-64 소유자 마커.
6. (개정 3 추가) 부품의 자체 트리거(`using-superpowers`·BMAD 자동 인사·ui-ux-pro-max 키워드 활성화) + `/plan` 라우터 → K-60, 라우터가 켤 때만 활성.
7. (개정 3 추가) 부품 산출물 경로 4종(`docs/superpowers/`, `_bmad-output/`, `openwiki/`, `.superpowers/`) + `docs/work/<id>/` → K-62 링크·override. `openwiki/`만 파생 계층으로 별도 유지.

### 6.1 채택 확정 게이트 (D-52)

계획 단계에서는 후보만 기록한다. **어느 파일을 어떻게 가져올지는 해당 마일스톤 진입 시 사용자가 확정한다.** 제품 결정(B)이므로 자율 진행하지 않는다.

1. **후보표 제시** — `archive/<repo>/03-components/`·`04-components-table.md`에서 파일 단위 후보 + 채택 방식 + 켜는 조건 + 충돌 지점 + 라이선스. ≤ 30행, 추천값을 기본 선택으로 채워 1클릭 확정이 가능하게.
2. **사용자 선택** — Q-07 "정말 좋았던 워크플로우" 명단이 있으면 우선순위에 반영.
3. **기록** — `provenance/imports.yaml`에 `status: accepted|rejected`, `decided_at`, `decided_by`, `source_sha`, `gate`.
4. **부착** — `vendor/` 복사(`verbatim`, 수정 0) 또는 설치 프로브(`install`) + 어댑터 투영.
5. **검증** — K-68 PASS(doctor 프로브 + 충돌 fixture 3종) → 게이트 닫힘. 실패 파일은 `rewrite` 강등 또는 `rejected`.

| 게이트 | 시점 | 부품 | 확정하는 것 |
| --- | --- | --- | --- |
| G-M2 | M2 진입(첫 작업) | Superpowers | **닫힘 2026-08-27 (D-67)** — 7종 14파일 `verbatim`, 4종 deferred, 3종+visual companion rejected, override 3건 |
| G-M3 | M3 진입 | BMAD 본체+CIS | 라우터가 추천할 스킬(discovery/T2별), 산출물 링크 규약, Codex 미지원 표기 |
| G-M6 | UI 프로젝트 발생 | WIG·taste·impeccable·ui-ux-pro-max | `verbatim` 파일 목록, `DESIGN.md` 스키마, ui-ux-pro-max 라이선스 판정 |
| G-M7 | v1 통과 후 **+ 어댑터 managed block 규약 K-68 통과 후**(D-70) | OpenWiki | 부착 대상 프로젝트, `.openwikiignore`, 갱신 시점, `AGENTS.md`·`CLAUDE.md` 블록 소유권 분리 |

### 6.2 통합 규약 적용표 (D-53)

규약 전문은 [`constraints.md` 7절](../requirements/constraints.md). 아래는 부품별 적용.

| 규약 | Superpowers | BMAD/CIS | OpenWiki | 디자인 4종 |
| --- | --- | --- | --- | --- |
| K-60 진입점 단일 | `using-superpowers`·hook **rejected**; `profile`이 켬. 승인 창구는 Tech Spec 확인란 하나(D-60) — 별도 3지선다를 띄우는 `writing-plans`·`executing-plans` 는 deferred | discovery/T2에서만 추천; 자동 인사 없음 | 기준 브랜치 반영 후 Romeo가 호출 | `facet=ui/brand`에서만; 키워드 자동 활성화 끔 |
| K-61 기획 원본 단일 | `brainstorming` **rejected** + `writing-plans` **deferred** — 계획 원본은 Romeo Tech Spec 하나. 원문의 두 규율(인터페이스·빈칸 금지)만 템플릿에 흡수(D-69) | 산출물은 `inputs:` 링크; Brief/Spec이 원본 | 기획 미소유(D-23) | `DESIGN.md`는 계약이지 기획이 아님 |
| K-62 산출물 흡수 | 채택 7종은 문서를 만들지 않아 경로 override 불필요. `docs/superpowers/**` 를 만드는 `writing-plans` 가 deferred 이기 때문 | `_bmad-output/**` 링크 | `openwiki/` 별도 계층; `docs/work/**` ignore | 스크린샷은 `.harness/runs/` + 해시만 evidence |
| K-63 상태 소유권 | SDD **deferred** — ledger·task-brief·review-package 스크립트가 상태를 따로 소유한다. 상태 원본은 `docs/work/<id>/` + evidence 단독 | `stepsCompleted` 참고용 | 신선도만 소유 | — |
| K-64 네임스페이스 | `superpowers:*` 유지 | `bmad-*` 유지 | `openwiki:managed` 마커 | 원본 이름 유지 |
| K-65 트리거 소유권 | session-start hook 미등록 | — | — | impeccable hook 미등록 |
| K-66 권한 상한 | `finishing-a-development-branch`의 merge/push/PR은 guard | `on_complete` hook은 검토 전 미실행 | schedule/PR write 권한 별도 승인 | 이미지 생성 비용·publish guard |
| K-67 버전 고정 | `b36e082` | 6.10.0 / CIS 0.2.1 | `a525ed8` | 각 고정 SHA |
| K-68 부착 검증 | discovery 프로브 + fixture 3종 | 설치 프로브 + discovery fixture | `finish=complete` | 스크린샷 evidence |
| K-69 분리 가능 | **7종 부분 채택**(D-67). 세트 단위 원칙은 "참조가 닫힌 묶음"으로 재해석 — 채택분의 나가는 참조가 세트 안에서 전부 닫힘을 실측으로 확인했다 | 제거해도 `/plan` 동작 | 제거해도 close 동작 | 제거 시 `BLOCKED_CAPABILITY(design)` |

**출처·변경 이력 장기 추적:** `provenance/imports.yaml`에 요소마다 `{id, source_repo, source_sha, source_path, license, license_verified_at, adoption(install|verbatim|rewrite|principle|excluded), status(proposed|accepted|rejected), decided_at, decided_by, gate, local_path, modifications(verbatim이면 none), reason, archive_ref}`를 기록하고, 코어 파일 frontmatter에 `provenance: [id]`를 둔다. `THIRD_PARTY_NOTICES.md`는 이 파일에서 생성하며, CI가 "frontmatter의 provenance id가 imports.yaml에 있는가"와 "`vendor/` 파일 해시가 `source_sha` 원문과 같은가(수정 0)"를 검사한다. 업데이트는 `/repo`로 새 SHA를 재아카이브 → 아카이브 diff 검토 → 게이트 재통과 → 채택 요소만 수정하는 PR(v3에서 자동화).

---

## 7. 단계별 구현 계획

각 단계는 "실제로 동작하는 흐름"으로 끝난다. 게이트는 둘이다 — **핵심 동등성 게이트**(M2 종료)와 **v1 릴리스 게이트**(M4 종료, 정본 V-0~V-10). M5부터는 v1.1이다. 개정 3에서 **채택 확정 게이트 G-M2·G-M3·G-M6·G-M7**이 추가됐다 — 각 마일스톤 진입 시 부품 후보표를 사용자가 확정해야 그 마일스톤의 부품 작업을 시작한다(D-52). 게이트 절차는 §6.1이다. 명령 순서(최소 흐름 → 기획 → 개발 → 디자인 → 문서 관리 → 모델·도구 → 설치·업데이트)를 따르되, **디자인은 UI 프로젝트가 있어야 검증할 수 있고 설치 기능이 있어야 그 프로젝트에 붙일 수 있으므로 설치(M5) 뒤(M6)로 옮겼다.** 문서 관리는 M1부터 조금씩 들어간다(/plan-close가 요구).

### M0 — 정책표·fixture·분류 카드 (기반)

- **사용자 가치:** 실제 요청 15~20건에 대해 "어떤 unit·gate·문서가 나와야 하는지"가 기계적으로 재현되고, 분류 카드가 사람이 확정할 수 있는 형태로 인쇄된다.
- **왜 지금:** 정본 우선순위 0("fixture가 아키텍처보다 먼저"). 정책표가 없으면 M1의 라우팅이 LLM 즉흥이 된다.
- **만들 것:** `fixtures/requests/*.yaml`(S07/S08 쿠팡 마이그레이션, S15 면접, S24 커머스, S11 이미지 편집, S16~22 교육 웹앱, `/repo` 요청들, 이 저장소의 T0/T1 후보 등 + **사용자 제공 최근 3개월 요청** — 이 부분은 사용자 입력 필요), `core/policy/classification.yaml`·`packages.yaml`·`execution-guards.yaml`, `core/schemas/{frontmatter,proposal}.json`, `core/templates/tech-spec.md`(compact-brief는 M2), `core/workflows/plan/SKILL.md` 초안, `bin/romeo`(`route`·`new`·`validate`·`fixtures`), `tests/`. provenance/NOTICE 골격은 만들지 않는다 — 첫 외부 자산을 채택하는 M2로 이동(리뷰 F-06).
- **선행 조건:** §9 "지금 결정" 중 B1(profile 라벨)·B2(상태 모델)만 있으면 됨. 라이선스·비코드 범위는 `NEEDS_DECISION`으로 기록만 하고, 그 값을 소비하는 단계(M2의 첫 자산 복사, 첫 비코드 부착) 직전에만 게이트로 승격한다(리뷰 F-07).
- **관찰 가능한 결과:** `romeo route --fixtures fixtures/requests --report`가 fixture별 기대 패키지 일치율(목표 ≥ 90%)과 `fired_rules`를 출력. `romeo validate`가 템플릿 샘플을 PASS/FAIL.
- **검증:** `python3 -m unittest`(정책표 규칙·ID 생성·frontmatter 파서), fixture 리포트, Claude 세션에서 `/plan --dry-run` 5건의 분류 카드를 사람이 읽고 수정 결과를 fixture `human_correction`에 기록.
- **실패 가능성·복구:** 정책표가 fixture를 못 덮으면 규칙 추가(축소 편향 경고). 전부 신규 파일이라 복구 = 삭제.
- **다음 단계 조건:** 일치율 ≥ 90%, hard gate 누락 0, 분류 카드 ≤ 30줄. M0는 단독 완료를 선언하지 않는다 — 같은 fixture가 M1의 입력으로 이어져 close PASS까지 도달해야 수직 슬라이스 1이 닫힌다(리뷰 F-06).

### M1 — T0 최소 관통 (Claude 단독, 현재 작업 공간)

- **사용자 가치:** 작은 요청 하나가 분류·계획·구현·증거·종료까지 기록으로 남는다. 명령의 "최소 동작 흐름".
- **왜 지금:** 정책표 검증 후 첫 실전. Orca·Codex 없이 코어와 검증 체계를 확인한다.
- **만들 것:** `core/workflows/plan-close/SKILL.md`, `romeo evidence`·`romeo close`, `core/schemas/evidence.json`, `.gitignore`, `.claude/skills/plan`·`plan-close`(M2 전까지는 수동 배치), `docs/work/`. **페이로드 = 실제 T0 2건 후보:** (a) `.gitignore` 추가(K-24), (b) `validate-repo-archive.sh`의 `rg` → `grep -E` 폴백 — 단 (b)는 M1 시작 시 `command -v rg`를 Claude 셸·Codex 셸·CI에서 재프로브해 여전히 앱 번들 바이너리에만 의존하면 채택하고, 아니면 관찰 가능한 가치가 있는 다른 T0로 교체한다(리뷰 F-08: Claude 셸은 ChatGPT.app, Codex 셸은 Codex 패키지 안의 rg를 쓰며 정식 설치는 없다).
- **선행 조건:** M0 통과.
- **관찰 가능한 결과:** `docs/work/chg-…-rg-fallback-…/spec.md`(frontmatter에 `policy_version`·`fired_rules`·`approved_at`), `evidence/<run>.yaml`(`head_sha`·`commands`·`exit_codes`·`changed_files`·`artifact_hash`), `/plan-close` PASS, `status: done`. 그리고 실제로 `rg` 없이 `bash scripts/validate-repo-archive.sh archive/obra-superpowers`가 PASS.
- **검증:** evidence의 `head_sha`가 `git rev-parse HEAD`와 일치; HEAD를 한 커밋 올린 뒤 `/plan-close`가 stale로 거부하는지; 커밋 없이 tracked 수정·staged 변경·untracked 파일 추가 각각에서 `dirty_tree_hash` 불일치로 거부하는지(§3.5, 리뷰 F-04); 미체크 AC가 있으면 거부하는지.
- **실패·복구:** 스크립트 변경은 `git revert`. 문서는 경로 불변이라 실패 시 `status: dropped`만.
- **다음 조건:** T0 2건 done + stale 거부 확인.

### M2 — 어댑터·역할·Orca 위임·T1 교차 관통 (핵심 동등성 게이트)

- **사용자 가치:** 같은 규칙으로 Claude가 구현하고 Codex가 검토하며, 역할을 바꿔도 같은 판정이 나온다.
- **왜 지금:** 하네스의 존재 이유(A-01). 이 전에 확장하면 근거 없는 확장(정본 명시).
- **만들 것:** `core/principles/AGENTS.core.md`, `core/roles/{implementer,reviewer}.yaml`, `core/schemas/{task-envelope,result-envelope}.json`, `core/workflows/{implement,review}/SKILL.md`, `adapters/claude`·`adapters/codex`(`romeo compile`: `AGENTS.md`·`CLAUDE.md`·`.claude/*`·`.agents/skills/*`·`.codex/agents/*.toml`, managed marker + source hash), `adapters/orca/RUNBOOK.md`, `.harness/bindings.yaml`, `fixtures/parity/`, `.claude/settings.json`(deny: `git push`, `gh pr merge`, worktree 삭제, 프로젝트 밖 `rm -rf`), `romeo doctor` 최소(Claude·Codex·Orca·gh 프로브). reviewer 역할 계약의 **런타임 read-only 강제** — Codex는 `-s read-only`, Claude는 `--allowedTools`(Read·Grep·Glob·읽기 전용 Bash)로 실행하고, 전후 `git status` 비교는 강제 수단이 아니라 방어 검사로 둔다(리뷰 F-03). `core/templates/compact-brief.md`, `provenance/imports.yaml`·`THIRD_PARTY_NOTICES.md`(superpowers·impeccable 원칙 재작성이 첫 항목), 하네스 자체용 최소 `.harness/romeo.project.yaml`(V-8). **페이로드 = 실제 T1:** 아카이브 라이선스 필드(§4.1) — 저장소 내부 문서 스키마 변경이라 hard gate가 없다. M2는 일부러 게이트 없는 T1로 동등성 경로만 검증하고, 게이트 발동 경로는 M3에서 검증한다(리뷰 F-02). **개정 3:** M2 진입 시 **G-M2 채택 게이트**를 먼저 연다 — Superpowers 후보표(§6.1)를 제시하고 사용자가 확정한 스킬만 `vendor/obra-superpowers@b36e082/`에 원문 복사(수정 0) → 어댑터가 `.claude/skills/`·`.agents/skills/`로 투영 → `core/workflows/implement`·`review`는 재작성본이 아니라 **profile별로 이 스킬을 호출하는 얇은 껍데기**가 된다(D-54). `provenance/imports.yaml`의 첫 항목은 이 게이트 결정이다. **개정 4 (게이트 결과, 2026-08-27):** G-M2 가 닫혔다(D-67) — `vendor/obra-superpowers@b36e082/skills/` 에 **7종 14파일**만 복사한다. 오케스트레이션 4종을 보류했으므로 `core/workflows/implement`·`review` 는 "스킬을 호출하는 얇은 껍데기" 로 두되 **실행 순서·상태·승인은 Romeo 가 소유한다** — superpowers 는 *무엇이 제대로 된 개발인가*(규율)만 제공하고, *누가 언제 실행하는가*(오케스트레이션)는 Romeo + Orca 다(D-50). 추가로 `core/templates/tech-spec.md` 에 **인터페이스 열·빈칸 금지 규칙**을 흡수했다(D-69). `adapters/*` 는 D-71 이 정정한 도구명 3건을 투영 시 치환해야 한다.
- **선행 조건:** M1 ✅, 사용자 결정 B1·B2 ✅, 역할 바인딩 **확정 ✅ D-68**(implementer=claude, reviewer=codex, 모델은 계정 기본값·K-12), **G-M2 채택 게이트 통과 ✅ D-67**(2026-08-27, `provenance/imports.yaml` 15항목). 남은 것은 **LICENSE Apache-2.0 교체(D-41)** — 첫 `vendor/` 복사 직전에 함께 처리한다.
- **관찰 가능한 결과:** `orca orchestration run-list`에 Run 1개·Task 2개(impl/review), 자식 worktree 1개, ResultEnvelope 2개, evidence 2개, 리뷰 findings, `/plan-close` PASS; 역할 교체 재실행 후 `romeo fixtures parity --report`가 "스키마 유효·required_checks 동일·gate 판정 동일"을 출력. `archive/README.md`에 라이선스 열, 18개 `_source.md`에 `License:` 줄, CI PASS.
- **검증:** reviewer 프로세스가 쓰기를 시도하면 런타임이 거부하는지(Codex read-only sandbox / Claude 도구 거부) + 실행 전후 `git status --porcelain` 동일(방어 검사); Codex `--json` NDJSON에서 최종 결과 추출이 `-o` 파일과 일치; Claude `--json-schema` `structured_output` 파싱; 컴파일 산출물의 managed 마커 밖 텍스트 보존 테스트; Windows 심링크 문제를 피하기 위해 `.agents/skills`가 실제 파일로 생성되는지(이 저장소의 기존 심링크는 유지·문서화); **vendored superpowers 스킬이 두 런타임에서 discovery되는지 doctor 프로브(A-11); 충돌 fixture 3종(K-68 — 이중 기획 0·자동 트리거 0·경로/마커 충돌 0) PASS. discovery가 실패한 스킬은 `rewrite`로 강등한다(D-53).**
- **실패·복구:** Orca dispatch 실패 → `worker-start` 종료코드·`recovery commands` 기록 후 대안 2(§3.4) 판단. 컴파일 산출물은 커밋 전 `git diff`로 검토, 실패 시 `git checkout --`.
- **다음 조건:** 역할 교체 parity PASS **(superpowers 규율 세트가 켜진 상태에서 — D-58)**, A-06 재검증 메모 작성. 이 시점은 핵심 동등성 게이트 통과이지 v1 완료가 아니다(리뷰 F-01).

### M3 — 기획 깊이 확장·차단·능력 부재 (T2·mode·gate·doctor)

- **사용자 가치:** 큰 요청은 Charter로, 불확실한 요청은 discovery로 라우팅되고, 위험 요청은 승인 없이는 진행되지 않으며, 없는 도구는 정직하게 보고된다.
- **왜 지금:** 정책표의 조건부 행이 실제로 발동하는지 확인. T2·discovery는 문서만으로 검증 가능(dry).
- **만들 것:** `core/templates/charter.md`, packages.yaml의 T2·discovery·gate 행, `core/policy/capabilities.yaml`, `romeo doctor` 확장(MCP·브라우저 3모드 프로브), Orca `gate-create` 승인 흐름, `scenarios/` 런북 3·8·9. 실행 가드 집행 규칙: `execution-guards.yaml` 항목이 걸리면 정확한 대상·영향·백업·복구를 채운 뒤에만 `gate-create`가 생성되고, 승인 전 상태 변경 0건을 검사한다. **개정 3 — G-M3:** BMAD 본체+CIS를 `install` 부품으로 연결한다(D-55) — `capabilities.yaml`에 `discovery.bmad` 프로브(`_bmad/_config/manifest.yaml` 존재, 6.10.0 / CIS 0.2.1 고정, Codex 지원 여부), `/plan`이 `mode=discovery` 또는 T2로 판정하면 분류 카드에 사용자가 G-M3에서 확정한 BMAD 스킬(예: `bmad-cis-design-thinking`, `bmad-product-brief`, `bmad-prd`)을 추천하고, 그 산출물(`_bmad-output/**`)을 Brief/Charter frontmatter `inputs:`로 링크(복사 아님, K-62). 벤더링·템플릿 재작성은 하지 않는다.
- **선행 조건:** M2, **G-M3 채택 게이트**(선행: Q-06 BMAD 본체 `/repo` 고정 SHA 아카이브 → 추천 스킬 후보표 → 사용자 확정).
- **관찰 가능한 결과:** (시나리오 3) discovery fixture가 `SPEC_READY` 차단 + 첫 마일스톤 spike + 분류 카드가 BMAD/CIS 스킬을 추천하고 산출물 링크를 요구(G-M3 결과); (9) "archive 1개 삭제" 요청에 deletion gate 발동 → `gate-create` → 거부 시 `BLOCKED_APPROVAL` evidence; (8) "iOS 시뮬레이터 스크린샷 검증" 요청에 `BLOCKED_CAPABILITY` + 대안 목록.
- **검증:** 각 시나리오 런북의 기대 판정과 실제 카드·evidence 대조; 재분류(T0→T1 승격) 경로에서 이전 frontmatter가 `routing.history`에 보존되는지.
- **실패·복구:** 문서·정책 변경뿐. 삭제 시나리오는 실제 삭제 없이 gate 거부로 종료(그래서 안전).
- **다음 조건:** 시나리오 3·8·9 PASS, hard gate 8 전부 fixture 1건 이상 보유.

### M4 — 문서 관리·재사용·승격 (current/·decisions·중복 방지·1-hop)

- **사용자 가치:** 같은 문서를 두 번 만들지 않고, 종료 시 현재 사실이 `current/`로 승격되며, 다음 세션이 1-hop만 읽어 재개한다.
- **왜 지금:** M2·M3에서 문서가 10건 이상 쌓인 뒤라야 실제 중복·링크 문제가 보인다.
- **만들 것:** `romeo find`(rg 기반 재사용 검색), `romeo context <id>`(1-hop 로드 목록), `/plan-close`의 `current/` 승격 후보 제안·`decisions.md` append, 링크·ID 무결성 검사, 하네스 지표 카운터 4개(분류 수정률·gate 누락·T0 처리 시간·재분류율)를 evidence/fixture에서 집계하는 `romeo metrics`.
- **선행 조건:** M3.
- **관찰 가능한 결과:** 중복 요청에 `/plan`이 기존 unit id를 제시; `docs/current/`에 승격 문서 1건 이상; `romeo metrics`가 표를 출력; 깨진 링크 0.
- **검증:** 의도적으로 깨진 링크·중복 slug fixture로 검사기 FAIL 확인.
- **실패·복구:** 검사기 오탐 시 규칙 완화(경고로 강등, K-31 "경고까지만" 정신).
- **다음 조건:** shadow mode 20건 도달 + 지표 첫 집계 + **v1 릴리스 게이트 판정** — 정본 V-0~V-10 체크리스트(§10 #1~#15)가 전부 관찰 가능한 증거로 충족되면 여기서 v1 완료를 선언한다(리뷰 F-01).

### M5 — 프로젝트 설치·업데이트·롤백 (v1.1 — 릴리스 게이트 이후)

- **사용자 가치:** 새 프로젝트에 필요한 모듈만 붙이고, 하네스 업데이트가 프로젝트 수정을 덮어쓰지 않으며, 문제 시 이전 버전으로 돌아간다.
- **왜 지금:** 이 저장소에서만 동작하는 하네스는 "여러 프로젝트 공통"이 아니다. 디자인 트랙(M6)을 실제 UI 프로젝트에 붙이려면 이 기능이 먼저 필요하다.
- **만들 것:** `romeo attach --modules plan,plan-close,implement,review [--design]`, `.harness/romeo.project.yaml` 전체 스키마(`attach-state.json`), `romeo update`(managed hash 3-way 비교) — **preflight**(대상 root·branch·dirty 상태·정확한 파일/블록·현재 hash 표시), dry-run 기본, 충돌은 **파일별 명시 승인**(`--accept-theirs`/`--keep-mine`은 전역이 아니라 파일 단위), 임시 staging 후 **원자적 교체**, 성공 후에만 상태 파일 갱신(리뷰 F-05), 하네스 버전 태그(`v0.1.0`), `romeo update --to <tag>` 롤백.
- **선행 조건:** M2 컴파일러, 부착 대상 = 로컬 샌드박스 저장소(원격 없음) 1개 + 실제 프로젝트 1개.
- **관찰 가능한 결과:** 샌드박스에 생성물·상태 파일 존재; 사용자가 `AGENTS.md` 프로젝트 블록과 managed 블록 안을 각각 수정한 뒤 `update --dry-run`이 "보존/충돌"을 정확히 분류; `--apply` 후 `git diff`가 managed 블록만 변경; `--to v0.1.0`으로 복귀.
- **검증:** 시나리오 10 런북; 두 런타임에서 부착 후 `/plan`이 discovery되는지 doctor.
- **실패·복구:** 적용 전 백업 디렉터리(관리 파일 원본 + 생성 예정 파일 목록)를 만들고, 실패 시 백업 복원 + 새로 생성된 untracked 파일 삭제로 되돌린다. 대상 저장소가 clean·committed 상태라고 가정하지 않는다(리뷰 F-05). 상태 파일은 성공 시에만 갱신.
- **다음 조건:** 실제 프로젝트 1건에서 T0 1건 관통.

### M6 — 디자인 트랙 최소 (UI 프로젝트가 생길 때)

- **사용자 가치:** 랜딩·제품 UI 요청이 문서 승인 → 구현 → 스크린샷·반응형·접근성·상태 검증으로 끝난다.
- **왜 지금(조건부):** 정본 트리거 "UI 산출물이 실제로 필요한 프로젝트". 그 전에는 `ui` facet 시 UI 상태표 섹션만 유지.
- **만들 것:** `DESIGN.md`·`PRODUCT.md` 계약 스키마(impeccable — 스키마는 `rewrite`, 스킬 본문·finish-reviewer `recapture/ship` 판정은 `verbatim`), 생성 규칙 1(taste `design-taste-frontend` v2 `verbatim`, 랜딩·브랜드 한정), 감사 규칙 2(WIG `AGENTS.md`·`command.md` `verbatim` + ARIA 링크 참조), ui-ux-pro-max는 D-57 라이선스 판정 결과에 따라 `cli/` 제외 `verbatim`, `visual-qa` 워크플로우(**유일한 자체 제작**)(375/768/1440 스크린샷·키보드·대비·콘솔 → evidence 첨부), 브라우저 3모드 매핑(개인 세션=claude-in-chrome, 반복=Playwright, 장시간=Orca 브라우저).
- **선행 조건:** M5, UI 프로젝트 1개, **G-M6 채택 게이트**(WIG·taste·impeccable `verbatim` 파일 목록 + ui-ux-pro-max 라이선스 판정 D-57). Q-03은 "`visual-qa`만 자체"로 결정됨.
- **관찰 가능한 결과:** 시나리오 4·5에서 evidence에 스크린샷 경로·뷰포트·감사 결과(`file:line`)가 있고, 없으면 `/plan-close`가 거부.
- **검증:** AI slop 안티패턴 카탈로그(절대금지/기본금지+근거예외/프로젝트고유) 3단 분리가 감사 출력에 반영.
- **실패·복구:** 디자인 문서·스킬만 변경. 스크린샷은 `.harness/runs/`(git 제외) + 해시만 evidence에.
- **다음 조건:** 랜딩 1건·제품 UI 1건 close.

### M7 — 파생 지식·지표·자기개선 (v2/v3)

- **G-M7 채택 게이트** 후 OpenWiki `install` 부착 실험 3회(A-07, D-56; `.openwikiignore`에 `docs/work/**`), `converge` 검사 개념, 지표 8종 완성, 실패 evidence → lesson → fixture → 양 런타임 평가 → 승격 루프(C-I1), upstream update PR. **v1 통과 전에는 시작하지 않는다.**

---

## 8. 검증 계획 (사용 시나리오 기준)

| # | 시나리오 | 기대 판단 (unit / mode / facet·gate / profile) | 생성 산출물 | 실행 제한 | 완료 증거 | 단계 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 문구·스타일 소수정 | T0 / delivery / 없음 / quick | Tech Spec 1개(Capsule ≤ 20줄) | 현재 작업 공간, Claude 단독, reviewer 없음, classifier 1회+writer 1회(K-32) | evidence(HEAD SHA·명령·종료코드·diff 해시), `/plan-close` PASS | M1 |
| 2 | 기존 제품에 일반 기능 추가 | T1 / delivery / 상황별 / standard | Compact Brief + Tech Spec | Orca 자식 worktree, implementer 1 + 반대 런타임 reviewer(read-only), `main` 병합은 guard | evidence 2건 + findings + gate 판정, current/ 승격 후보 | M2 |
| 3 | 불확실성 높은 신규 프로젝트 | T1 또는 T2 / **discovery** / 상황별 / deep | Charter(T2) 또는 Brief의 discovery 섹션 + 검증 계획, 첫 마일스톤 = spike | `SPEC_READY` 차단 → 구현 dispatch 금지 | discovery 결과 문서 + 진행/중단 결정 기록 | M3 |
| 4 | 랜딩페이지 디자인 | T1 / delivery / `ui`,`brand` / standard | Brief(디자인 방향·메시지·대상) + `DESIGN.md` 확인·생성 + Spec | 디자인 모듈 미설치 시 `BLOCKED_CAPABILITY(design)`으로 정직 보고 | 375/768/1440 스크린샷·감사 `file:line`·reduced-motion·대비 결과가 evidence에 | M6 |
| 5 | 제품 내부 UI·여러 화면 상태 | T1 / delivery / `ui` / standard | Brief에 **UI 상태표**(빈·로딩·오류·권한 없음·성공) 필수 섹션 | 상태표 미충족 시 문서 검증 실패 | 각 상태 스크린샷 또는 테스트 결과 매핑 | M3(섹션)·M6(시각) |
| 6 | Claude·Codex 같은 규칙 | (분류 동일) | `romeo compile` 산출물 양쪽 + `AGENTS.md`(managed) + `CLAUDE.md`(@import) | 프롬프트 동일성 요구 안 함 | 같은 fixture에 두 런타임이 같은 unit·gate; ResultEnvelope 스키마 유효; managed 마커 무결 | M2 |
| 7 | 큰 기능을 독립 worktree에서 | T1/T2 / delivery / 상황별 / standard·deep | Spec의 `base_sha` 고정, TaskEnvelope에 `workspace: worktree` | `orca worker-start --worktree new-child`; facet에 migration·ops-data 있으면 "worktree는 코드만 분리" 경고 + 환경 계획 요구; 병렬 비교는 `race` 계약(같은 base SHA·같은 envelope) | worktree id·branch·base SHA·evidence, 병합은 사람 승인 기록 | M2·M3 |
| 8 | 필요한 도구 없음 | (분류는 정상) | 능력 부재 카드: 필요 능력·프로브 결과·대안·비용 | 가능한 척 진행 금지, 자동 설치 금지 | `blocked_reason: BLOCKED_CAPABILITY` evidence + 사용자 결정 | M3 |
| 9 | 비용·운영 데이터 위험 요청 | 어떤 unit이든 hard gate 발동 → profile ≥ standard | 문서에 위험·백업·복구 섹션 강제; 실행 시 execution guard | `orca gate-create` 승인 전 실행 금지; 승인 없으면 `BLOCKED_APPROVAL` | gate id·질문·응답·시각이 evidence에; 예산 초과 시 gate 생략 아닌 경고 | M3 |
| 10 | 하네스 업데이트 ↔ 프로젝트 설정 충돌 | — | `update --dry-run` 보고(보존/갱신/충돌 파일 목록·diff) | 충돌 파일 자동 덮어쓰기 금지; `--accept-theirs/--keep-mine` 명시 | 적용 후 `git diff`가 managed 블록만, 상태 파일 버전 갱신, `--to` 롤백 성공 | M5 |
| 0 | 참고 저장소 아카이브 | — | `archive/<owner>-<repo>/` | 읽기 전용 GitHub, `--replace` 재승인 | `validate-repo-archive.sh` PASS(이미 동작) | 기존 |

**하네스 자체 회귀:** M0의 fixture 리포트(결정론, 무료)는 매 정책 변경마다, 시나리오 런북(LLM 실행, 유료)은 릴리스 태그마다 1회 — 비용 때문에 둘을 구분한다.

---

## 9. 위험과 미결정 사항

### 9.1 위험 평가

| 차원 | 위험 | 완화 |
| --- | --- | --- |
| 기술 | A-01 parity가 안 나올 수 있음(두 CLI 출력·권한 모델 차이) | parity를 "같은 코드"가 아니라 스키마·checks·gate 판정 동일성으로 정의(D-12); 어댑터가 흡수 |
| 기술 | Codex/Claude CLI가 빠르게 바뀜(K-02~K-05는 08-05 기준) | `romeo doctor`가 매 세션 capability probe; 어댑터에 버전 기록 |
| 기술 | `rg` 비정식 설치 | M1 T0로 `grep -E` 폴백; `brew install ripgrep` 권고 |
| 운영 복잡도 | 1인 주의력이 첫 병목(K-30): shadow mode 20건·분류 카드 확인 부담 | 카드 ≤ 30줄, T0는 1클릭, 카드 형식을 fixture로 튜닝 |
| 유지보수 | 정책표·템플릿·어댑터×2가 동시에 자람 | 모듈 = 정책 행+섹션(§3.2); 어댑터는 컴파일러 하나에 출력 템플릿만 |
| 보안·권한 | Orca는 reviewer read-only를 **강제하지 않음**; guard는 계약+permission으로만 집행 | 실행 전후 `git status` 비교로 사후 검증; Claude deny 목록·Codex sandbox; 위반 시 evidence 무효 |
| 보안 | evidence·로그에 크리덴셜 유입 | 원시 로그는 `.harness/runs/`(git 제외), evidence에는 해시·경로만; `romeo evidence`가 known secret 패턴 마스킹 |
| 모델 비용 | 교차 리뷰는 비용 2배, parity 재현은 4배 | T0는 reviewer 없음(K-32); parity는 태그당 1회 |
| 도구 종속 | Orca(실행), Claude 스킬 형식, PyYAML | Orca는 TaskEnvelope 뒤에 격리(대안 2); PyYAML은 1줄 설치 |
| 이전 가능성 | 프로젝트 지식은 Markdown+YAML+git이라 이식 가능; 생성물은 재컴파일 가능 | 부착 상태에 하네스 SHA 고정 |
| 저장소 위생 | 원천 대화 77MB 커밋(clone 비용) | 저위험; 나중에 git-lfs 또는 분리 검토 |

### 9.2 지금 결정해야 하는 것 (사용자 판단, 우선순위 순)

1. **라이선스(A1/X-05):** Apache-2.0 전환 vs GPL-3.0 유지. 추천 Apache-2.0(기여자가 본인뿐인 지금이 최저 비용; 문서·규칙 저장소에 GPL은 이례적). 어느 쪽이든 MIT/Apache 자산 채택은 가능, W3C·스킬별 라이선스는 복사 금지.
2. **사용자 정체성(A2/X-02):** persona "비개발자" 유지 + 하네스는 B를 가정 — 이 해석에 동의하는지. 문서 장황도·승인 UX가 달라진다.
3. **상태 모델(B2):** `status` 1개 + `approved_at` 필드 + 계산된 stale — 동의 여부. frontmatter라 나중에 바꾸면 전수 마이그레이션.
4. **깊이 라벨(B1):** `profile: quick|standard|deep`을 정책표 출력으로 두고 unit은 T0/T1/T2 유지 — 동의 여부.
5. **v1 적용 대상(D-43):** 코드 프로젝트 전용 선언, 비코드는 경량 `AGENTS.md` 부착만.
6. **fixture 출처(V-0):** transcripts에서 추출할 수 있는 것 외에 **최근 3개월 실제 요청**은 사용자만 제공 가능.
7. **Spec Kit(D-40):** 비채택 + `converge` 개념만(정본 추천 그대로) — 확인만.
8. **채택 매니페스트(D-52, 개정 3):** 게이트마다(G-M2·G-M3·G-M6·G-M7) 후보표를 보고 **파일 단위로** 확정한다. **지금은 결정하지 않는다** — 다만 Q-07 "정말 좋았던 워크플로우" 명단을 미리 주면 후보표 우선순위에 반영한다.

**차단 시점(리뷰 F-07 반영):** 3·4·6은 M0 전에 필요하다. 1(라이선스)은 M2의 첫 외부 자산 복사 전, 5(비코드 범위)는 첫 비코드 프로젝트 부착 전에 필요하다. 2·7은 비차단(문서 톤·확인). 8은 각 마일스톤 진입 시점에 차단한다 — G-M2는 M2의 첫 작업이며 1(라이선스)과 같은 시점이다. 미정 항목은 `NEEDS_DECISION`으로 기록하고 진행한다.

### 9.3 구현하면서 검증해도 되는 것

A-02(정책표 정확도), A-03(3-tier 충분성), A-04(경로 불변 탐색성), A-05(rg 100건), A-06(Orca 안정성), A-07(OpenWiki 가치), Codex `.codex/agents` 형식, 템플릿 길이 캡 수치, T0 자동 확정 임계, Q-03(디자인 자체 제작 최소안), Q-04(MCP registry), Python 실행 버전(3.9 stdlib+PyYAML로 시작, 문제 시 `uv`로 3.12 고정).

### 9.4 잘못 이해했거나 장기 유지가 어려운 요구

- **"스킬·도구를 스스로 찾는다"**는 그대로 두면 공급망 위험(참고 메모 다수가 `@latest`·전역 설치를 경고). 레지스트리+승인으로 좁혀야 한다.
- **"모델을 품질·속도·비용으로 선택"**은 측정치가 없는 상태에서는 추측이다. 역할 바인딩·override로 시작하고, 지표 8종 중 토큰/요청이 쌓인 뒤에만.
- **"기획부터 회고까지 하나의 연속 흐름"**에서 회고·성과 측정은 측정 가능한 제품 가설에만(C-E6). 내부 리팩터링에 outcome gate를 걸면 인위적 지표가 생긴다.
- **"하네스 자체를 반복 평가"**는 LLM 실행이 들어가면 비용이 크다. 결정론 fixture 리포트와 유료 시나리오를 분리해야 유지된다.
- **디자인 능력 목록 전체**는 v1에서 유지 불가. `DESIGN.md` 계약 + 규칙 3개 + visual-qa만이 현실적이다.
- **"참고 저장소 업데이트를 비교 후 선택 반영"**은 자동화(v3) 전에는 `/repo` 재아카이브 + 사람 diff로 충분하다.

---

## 10. 최종 실행 순서 (체크리스트)

| # | 항목 | 완료 확인 기준(관찰 가능) |
| --- | --- | --- |
| 1 | §9.2 결정 1~5 확정 | `decision-register.md`에 D-41·X-02·D-15 보완·profile·D-43 결정이 accepted로 기록 |
| 2 | fixture 15~20건 작성(사용자 3개월 요청 포함) | `fixtures/requests/*.yaml` ≥ 15, 각 파일에 기대 unit·gate·패키지·허용 대안 |
| 3 | 정책표 3종 + 스키마 + 템플릿 1종(Tech Spec) + `/plan` SKILL 초안 | `romeo route --fixtures --report` 일치율 ≥ 90%, gate 누락 0 |
| 4 | `romeo validate`·`new`·ID 생성 + unittest | `python3 -m unittest` 전부 PASS, 같은 날 같은 slug 2건 충돌 없음 |
| 5 | `/plan --dry-run` 5건 shadow | 5건의 분류 카드와 사람 수정 결과가 fixture에 반영 |
| 6 | M1: T0 2건 관통(.gitignore + `command -v rg` 재프로브 후 결정한 두 번째 T0) | `docs/work/chg-*/spec.md`+`evidence/*.yaml`, `/plan-close` PASS, M0 fixture가 M1 입력으로 이어짐 |
| 7 | stale 거부·미체크 AC 거부 확인 | HEAD 변경·tracked 수정·staged·untracked 추가 4경우 모두 close 거부 로그 |
| 8 | 역할 2(reviewer 런타임 read-only) + 바인딩 승인 + envelope 스키마 | `.harness/bindings.yaml` 승인 기록, 스키마 테스트 PASS, reviewer 쓰기 시도 거부 로그 |
| 8b | **G-M2 채택 게이트**(개정 3): superpowers 후보표 → 사용자 확정 → `provenance/imports.yaml` `accepted` + `vendor/obra-superpowers@b36e082/` 원문 복사 + 어댑터 투영 | imports.yaml에 `decided_at`·`decided_by`, 두 런타임 doctor discovery PASS, 충돌 fixture 3종 PASS(이중 기획 0·자동 트리거 0·경로/마커 충돌 0) |
| 9 | `romeo compile` (Claude·Codex) + managed marker + 최소 `.harness/romeo.project.yaml` + provenance 첫 항목·NOTICE | 생성 파일 커밋, 마커 밖 텍스트 보존 테스트 PASS, doctor에서 양쪽 discovery 확인 |
| 10 | Orca 런북으로 T1 관통(Claude 구현/Codex 리뷰) | Run·Task·worktree·evidence 2건·findings, close PASS, 리뷰 전후 `git status` 동일 |
| 11 | 역할 교체 재현 + parity 보고 = **핵심 동등성 게이트** — **개정 4(D-76):** 게이트는 결정적 요소(봉투 스키마·역할 계약·`required_checks`·구현자 판정)만 센다. 검토자의 자유 판정은 advisory | `romeo fixtures parity --report` EXIT 0 · "핵심 동등성 게이트: PASS" · 검토 판정은 advisory 로 인쇄(게이트 아님) |
| 12 | 라이선스 필드 T1 결과물 | `archive/README.md` 라이선스 열, 18개 `_source.md` `License:` 줄, CI PASS |
| 13 | M3: Charter·discovery·gate·capabilities·doctor | 시나리오 3·8·9 런북 PASS, hard gate 8 각 fixture ≥ 1 |
| 13b | **G-M3 채택 게이트**(개정 3): BMAD 본체 `/repo` 아카이브(Q-06) → 추천 스킬 후보표 → 사용자 확정 → `install` 프로브 + `/plan` 링크 | discovery fixture 카드에 BMAD 스킬 추천·산출물 링크 요구; `capabilities.yaml`에 `discovery.bmad` 프로브·Codex 지원 여부 표기 |
| 14 | M4: find·context·승격·metrics | 중복 제안 1건, `docs/current/` 1건, 지표 표 출력, 깨진 링크 0 |
| 15 | shadow mode 20건 완료 + **v1 릴리스 게이트 판정** | 분류 수정률·gate 누락 수 집계, V-0~V-10 전부 증거로 충족 → v1 완료 선언 |
| 16 | M5(v1.1): attach·update·rollback — preflight·파일별 승인·원자적 적용·백업 복원 | 샌드박스 + 실제 프로젝트 1건, dirty/untracked 충돌 fixture 포함 시나리오 10 PASS |
| 17 | 하네스 `v0.1.0` 태그(릴리스 게이트 통과 시점) | 태그 존재, provenance CI PASS |
| 18 | M6/M7은 트리거 발생 시 — 각각 **G-M6·G-M7 채택 게이트** 선행 | UI 프로젝트 발생 / v1 통과 후; 게이트 결정이 imports.yaml에 기록됨 |

### 첫 구현 단계(M0)에 Claude에게 보낼 프롬프트 초안

```text
Romeo 하네스 M0(정책표·fixture·분류 카드)를 구현해줘. 시작 전에 docs/product/harness-brief.md,
docs/requirements/{capability-map,constraints,v1-scope}.md, docs/decisions/decision-register.md,
docs/planning/open-questions.md를 읽고, 정본과 이 지시가 충돌하면 진행하지 말고 보고해.

전제(사용자 결정): profile 라벨=정책표 출력(quick/standard/deep), unit=T0/T1/T2 유지,
상태=status 1개+approved_at 필드(검증 상태는 저장하지 않고 close 시 계산).
라이선스와 비코드 프로젝트 범위는 미정이면 NEEDS_DECISION으로 기록만 하고 M0를 멈추지 마라
(각각 M2의 첫 외부 자산 복사 전, 첫 비코드 부착 전에 결정한다).

만들 것(모두 신규 파일, 기존 파일·archive/·docs 정본은 수정 금지):
1. fixtures/requests/*.yaml — 최소 15건. 출처: docs/source-context transcripts(S07/S08 마이그레이션,
   S15 면접 준비, S24 커머스 운영, S11 이미지 편집, S16~22 교육 웹앱, /repo 요청)와 내가 별도로 주는
   최근 요청 목록. 각 fixture: id, request_text, context, expected{unit,mode,facets,gates,package,profile},
   acceptable_alternatives, human_correction(null), source.
2. core/policy/classification.yaml(unit·mode·facet·hard gate 8·2질문 rubric·충돌 우선순위·profile 규칙),
   core/policy/packages.yaml(unit×gate×facet → 문서·필수 섹션·차단 상태·리뷰 요구·격리 범위·길이 예산),
   core/policy/execution-guards.yaml(결제·권한 확대·공개 전환·운영 배포·운영 데이터·마이그레이션·계정/소유권·
   삭제·main 병합·다른 작업 공간 삭제·외부 전송 → 승인 요구와 설명 항목).
3. core/schemas/frontmatter.json, proposal.json (JSON Schema). frontmatter: id(type-YYYYMMDD-slug-entropy),
   type, unit, mode, facets, gates, profile, status(draft|active|done|dropped|superseded), approved_at,
   parent, routing{policy_version,fired_rules}, updated.
4. core/templates/tech-spec.md(Planning Capsule 섹션 ≤20줄, 전체 ≤150줄). compact-brief.md는 M2에서 만든다.
   ui facet 시 "UI 상태표(빈·로딩·오류·권한 없음·성공)" 섹션 포함.
5. core/workflows/plan/SKILL.md 초안 — 도구명·모델명 없이: 재사용 검색 → 제안 카드(사실/가정/미확인/
   후보/5요인 설명/2질문/gate 8 체크리스트, ≤30줄) → 사람 확정 → `romeo route` → 문서 생성.
6. bin/romeo + romeo/ Python 패키지(표준 라이브러리 + PyYAML만, unittest): route, new, validate, fixtures.
   `romeo route --fixtures fixtures/requests --report`가 일치율과 fired_rules를 출력해야 한다.
7. provenance/imports.yaml·THIRD_PARTY_NOTICES.md는 만들지 않는다(첫 외부 자산을 채택하는 M2에서 생성).
   M0는 단독 완료가 아니다: fixture 하나를 골라 M1(/plan → 구현 → evidence → close)의 입력으로 바로 잇는다.

완료 보고 형식: 변경 파일 목록, 실행한 명령과 종료 코드, fixture 일치율, 미검증 항목, 남은 위험,
다음 단계(M1 T0 후보: .gitignore, 그리고 command -v rg를 Claude 셸·Codex 셸·CI에서 재프로브한 뒤 결정하는 rg 폴백). 파일을 만들었다는
사실만으로 완료라고 하지 말고 실제 실행 결과로 보고해.
```

---

## 11. Codex 리뷰 반영 기록 (2026-08-27, 개정 2)

리뷰어 Codex `gpt-5.6-sol`(fast 티어, xhigh) · 판정 "주요 수정 후 구현 가능" · BLOCKER 0 · MAJOR 5 · MINOR 3. 검증 근거와 기각 이유는 [decisions.md](../reviews/2026-08-27-codex-plan-review/decisions.md), 리뷰 원문은 [review.md](../reviews/2026-08-27-codex-plan-review/review.md).

| ID | 등급 | 판정 | 반영 위치 |
| --- | --- | --- | --- |
| F-01 v1 합격선과 v1 필수 산출물의 시점 모순 | MAJOR | 채택 | §0, §3.5, §4.1, §4.2, §7 intro, M2, M4, M5, §10 #11·#15·#17 |
| F-02 M2 페이로드가 gate 대상인데 gate 집행은 M3 | MAJOR | 부분 채택(backfill은 hard gate 아님; 라벨 모호함은 인정) | §4.1, M2, M3 |
| F-03 reviewer read-only가 런타임 강제 없음 | MAJOR | 채택 | §4.1, §4.2, M2, §10 #8 |
| F-04 stale 판정이 HEAD 중심 | MAJOR | 채택 | §3.5, M1, §10 #7 |
| F-05 attach/update 복구가 git clean 상태를 가정 | MAJOR | 채택 | M5 |
| F-06 M0의 수평 산출물·빈 골격 | MINOR | 채택 | §5.1, M0, §10 #3, 프롬프트 초안 |
| F-07 M0 선행 결정 불일치 | MINOR | 채택 | M0, §9.2, 프롬프트 초안 |
| F-08 `rg` 관찰의 환경 의존 | MINOR | 부분 채택(관찰은 정확, 고정 페이로드는 철회) | M1, §10 #6, 프롬프트 초안 |

---

## 12. 개정 3 반영 기록 (2026-08-27) — 부품 조립 재정의

계기: 사용자 질문 "원본 레포에서 원칙만 가져오게 되어 있는 것 같다 … 실제로 사용해보고 좋았던 워크플로우는 그대로 사용하고 싶다" → 원천 대화 25건 재독 → 사용자 재정의 "잘 썼던 하네스들을 조립해서 나만의 라우터 체계로" → "뭘 가져올지는 구현 단계에서 나한테 물어서 구체화", "충돌하지 않고 하나의 시스템에 녹아드는 것이 가장 중요". 근거·분석 전문은 [assembly-redefinition/summary.md](../reviews/2026-08-27-assembly-redefinition/summary.md).

| 바뀐 것 | 위치 | 결정 |
| --- | --- | --- |
| Romeo = 라우터 + 접착 + 동등성, 부품은 조립 | §0, §2.3, §2.4 A5, §3.1 | D-50 |
| 채택 방식 4단계 → 5단계(`install`/`verbatim`/`rewrite`/`principle`/`excluded`), §6 표 전면 재표기 | §6 | D-51 |
| 채택 확정 게이트 G-M2·G-M3·G-M6·G-M7 — 파일 목록은 마일스톤 진입 시 사용자가 확정 | §6.1, §7 intro·M2·M3·M6·M7, §9.2 #8, §10 #8b·#13b·#18 | D-52 |
| 통합 규약 K-60~K-69 + 부품별 충돌 지점 적용표 | §6.2, `constraints.md` 7절 | D-53 |
| Superpowers 규율 세트 `verbatim` 후보(`brainstorming`·`using-superpowers` 제외); implement/review 워크플로우는 호출 껍데기 | §6, M2 | D-54 |
| BMAD 본체+CIS `install` + `/plan` 링크(벤더링 없음), M3로 당김 | §6, M3 | D-55 (D-31 대체) |
| OpenWiki 라벨 정정("원칙만 참고" → `install`) | §6 | D-56 |
| ui-ux-pro-max "제외(보류)" → 라이선스 확인 트랙 | §6, M6 | D-57 |
| `install`·`verbatim`은 v1 안에서 허용, 동등성은 부품이 켜진 상태에서 판정 | §0, M2 다음 조건, `v1-scope.md` | D-58 |
| `vendor/` 디렉터리, `provenance/imports.yaml` 스키마에 `adoption` 5단계·`status`·`decided_at` | §3.3, §5.1, §6 | D-51 |

**바꾸지 않은 것:** Thin Policy-Compiled Planning Spine, unit/mode/facet, 3분할, 상태 계약(§3.5), 핵심 동등성 게이트·v1 릴리스 게이트의 존재, Codex 리뷰 반영(§11) 전부. 개정 3은 척추가 무엇을 라우팅하는지(부품)를 보탠 것이지 척추를 바꾼 것이 아니다.

**미검증:** A-11(vendored 스킬의 양 런타임 discovery), A-12(BMAD의 Codex 지원). 둘 다 G-M2·G-M3에서 실측한다.

## 13. 개정 4 반영 기록 (2026-08-29) — M2 완료 정의

3일째 닫히지 않던 M2 의 근본 원인 재검토([`docs/reviews/2026-08-29-codex-m2-rootcause-review/`](../reviews/2026-08-29-codex-m2-rootcause-review/README.md))를 받아
사용자가 다음을 확정했다([D-76](../decisions/decision-register.md)).

- **§4.1 M2 흐름의 마지막 줄 "같은 gate 판정"** 은 결정적 요소(봉투 스키마 · 역할 계약과 권한 상한 · `required_checks` · 구현자 면의 판정 — 수용 기준 AC 는 종료 검사가 본다)만 뜻한다.
  검토자(LLM)의 자유 서술 판정 일치는 게이트가 아니라 리포트의 advisory 항목이다 — 같은 산출물·같은 런타임에서도 판정이 흔들린다는 관측(D-74) 아래에서
  그 일치는 유한하게 닫히는 목표가 아니었다. §10 #11 의 확인 기준을 그에 맞게 고쳤다.
- **D-75 는 (b)** — close 는 현재 산출물의 PASS 1건으로 닫고 표본 수는 경고로만 드러낸다.
- **impl6 전체 교체 실행은 게이트 조건이 아니다** — 관측 케이스가 이미 교체 실행의 구현자 면을 담고 있다. **Q-11 승인 서명은 미룬다.** push 는 별도 승인이다.
- **M2 완료 ≠ v1 릴리스 완료.** §4.2 의 게이트 두 개 구분은 그대로다 — T2 Charter·shadow 20건·attach 는 v1 릴리스 게이트(M4)의 잔여다.
- 구현: `romeo/parity.py` `judge_mode`(기본 `advisory`, `strict` 는 D-73·D-74 결박 보존) · `fixtures/parity/*` `expect_advisory` · 테스트 398 → 419.
