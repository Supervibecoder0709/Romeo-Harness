---
id: capability-map
type: requirements
status: draft
updated: 2026-08-27
authority: canonical
---

# 능력 지도

원천 대화에서 언급된 **도구 이름이 아니라 필요 능력**으로 정규화했다.
"후보" 열은 요구가 아니라 참고 구현이다. 특정 저장소를 쓰라는 뜻이 아니다.

> **개정 3 (2026-08-27):** 위 원칙은 A~I(라우터·접착·동등성)에만 적용된다. 사용자가 직접 써보고 지목한
> 부품(BMAD/CIS·Superpowers·OpenWiki·디자인 스킬)은 "능력 후보"가 아니라 **조립 대상**이다.
> 그 능력은 [J. 부품 조립](#j-부품-조립-assembly)에 있고, 무엇을 어떻게 가져올지는
> [결정 D-50~D-58](../decisions/decision-register.md)과 [통합 규약 K-60~K-69](constraints.md)가 정한다.

`v1` 열: ✅ v1 필수 · 부분 = v1에 축소 도입 · v2/v3 = 이후 · **구현됨** = 현재 저장소에서 동작 확인됨.

인용 키는 [대화 커버리지](../traceability/conversation-coverage.md)를 따른다.

---

## A. 요청 분류 (Intake & Routing)

| ID | 능력 | 왜 필요한가 | 근거 | v1 |
| --- | --- | --- | --- | --- |
| C-A1 | 자연어 요청에서 사실·가정·미확인·분류 후보 분리 | 잘못된 전제로 문서가 생성되는 것을 막는다 | S10 §4, COUNCIL Consensus 4 | ✅ |
| C-A2 | planning unit 판정 (T0 Change / T1 Feature / T2 Initiative) | 문서 깊이를 요청 크기가 아니라 승인 단위로 결정한다 | COUNCIL §4 | ✅ |
| C-A3 | mode(discovery·delivery·experiment)와 facet(payment·privacy·migration·gtm…)을 unit과 **독립 축**으로 기록 | 축을 섞으면 조합 규칙이 폭발한다 | S10 §2, COUNCIL Consensus 1 | ✅ |
| C-A4 | Hard gate 8종 체크리스트 발동 | 버튼 문구 한 줄이라도 결제 약관에 걸리면 강도가 올라가야 한다 | PHD §1, COUNCIL | ✅ |
| C-A5 | 합산 점수 금지 + 정책 충돌 우선순위 적용 | 축마다 유발하는 행동이 다르다 | PHD §1, COUNCIL Consensus 5 | ✅ |
| C-A6 | 재분류(T0→T1→T2 승격)를 정상 경로로 처리하고 기록 보존 | 범위 확대는 예외가 아니라 상시 발생한다 | COUNCIL §3 | ✅ |
| C-A7 | 분류 결과를 사람이 1클릭으로 확정 (shadow mode 20건) | 의미적 사실의 확정은 결정론이 아니다 | COUNCIL Consensus 4·10 | ✅ |

### Hard gate 8종

결제·정산·가격 / 개인정보·보안·권한 / 법무·규제·약관 / 운영 데이터 삭제 /
데이터 마이그레이션 / 외부 공개 API / 되돌리기 어려운 정책 변경 / 서비스 중단 가능성. (PHD §1)

### 정책 충돌 우선순위

```text
Hard gate → 실행 차단 조건 → planning unit → 필수 overlay → 선택 overlay → 문서·토큰 예산
```

필수 gate가 예산을 초과하면 gate를 생략하는 것이 아니라 **예산 초과 경고**를 낸다. (COUNCIL Consensus 5)

---

## B. 문서 패키지 (Planning Artifacts)

| ID | 능력 | 근거 | v1 |
| --- | --- | --- | --- |
| C-B1 | 최소 충분 문서 패키지 조립. 공통 코어 + 조건부 오버레이, 템플릿 폭발 금지 | PHD §2, S10 §1 | ✅ |
| C-B2 | T0는 기획 파일 0개 — Tech Spec 안 Planning Capsule | COUNCIL Consensus 2 | ✅ |
| C-B3 | PRD/Brief(제품 의도)와 ADR(기술 결정 이유)의 목적 분리 | S01 사용자 원문, S01 plan §2 | ✅ |
| C-B4 | frontmatter ~7줄이 분류 기록 겸 재개 체크포인트 (`policy_version`·`fired_rules` 포함) | COUNCIL Consensus 3 | ✅ |
| C-B5 | 문서 상태·작성일·최신화일 상시 유지 | S01 사용자 원문 | ✅ |
| C-B6 | 분산 안전 ID `type-YYYYMMDD-slug-entropy` | S01 KEEL 리뷰, COUNCIL Consensus 6 | ✅ |
| C-B7 | 문서·토큰 예산 상한과 초과 경고 | S10 §7 | ✅ |
| C-B8 | current/(살아있는 사실)와 work/(당시 변경 의도) 분리 | PHD §4, COUNCIL | ✅ |
| C-B9 | 경로 불변 — 상태가 바뀌어도 파일을 옮기지 않는다 | COUNCIL "새로 닫힌 쟁점" | ✅ |
| C-B10 | 문서 유형별 자동 정리·인덱스 | S01 사용자 원문 | 부분 |

> C-B10과 C-B9는 **생성 시점 폴더링은 유지하되 상태 변화에 따른 이동만 금지**하는 방식으로
> 양립시킨다. 판단 근거는 [열린 질문 X-04](../planning/open-questions.md)에 있다.

### 상태 모델 (v1)

```text
draft → active → done
              ↘ dropped
              ↘ superseded
```

검증 상태(`unverified/verified/stale`)는 evidence 파이프라인이 실제로 생기면 분리 추가한다.
(COUNCIL "남은 이견 1", 결정 D-15)

---

## C. 벤더 중립 실행 계약 (Runtime Parity)

| ID | 능력 | 근거 | v1 |
| --- | --- | --- | --- |
| C-C1 | 하나의 canonical 정의에서 Claude/Codex 네이티브 형식 컴파일 | S01 사용자 원문, S04 | ✅ 최소 |
| C-C2 | "동일 워크플로우"를 같은 프롬프트가 아니라 **같은 schema·AC·권한·게이트·evidence**로 정의 | S01 KEEL 리뷰, S10 §9, COUNCIL Consensus 9 | ✅ |
| C-C3 | 공통 TaskEnvelope / ResultEnvelope로 두 CLI 출력 차이 흡수 | S10 §5 | ✅ |
| C-C4 | 생성물에 source hash + managed marker, marker 밖 사용자 내용 보존 | S01 plan §1 | ✅ |
| C-C5 | 양 런타임 semantic parity fixture | S10 최종, COUNCIL 우선순위 0 | ✅ |
| C-C6 | 스킬 본문에 도구명을 넣지 않고 adapter가 매핑 | S03 (Superpowers porting guide) | ✅ |

### 투영표

| 공통 자산 | Claude | Codex |
| --- | --- | --- |
| workflow / skill | `.claude/skills/*` | `.agents/skills/*` |
| 역할 계약 | `.claude/agents/*.md` | `.codex/agents/*.toml` |
| 프로젝트 지침 | `CLAUDE.md`에서 `@AGENTS.md` import | `AGENTS.md` |
| hook | `.claude/settings.json` | `.codex/hooks.json` |
| MCP | `.mcp.json` | `.codex/config.toml` |
| 실행 계약 | 동일 TaskEnvelope | 동일 TaskEnvelope |

근거: S01 KEEL 리뷰 "올바른 투영", S04 리뷰 #2. 사실 확인 사항은 [제약 K-02~K-05](constraints.md) 참조.

---

## D. 실행과 소유권 (Execution)

| ID | 능력 | 근거 | v1 |
| --- | --- | --- | --- |
| C-D1 | 실행 상태의 유일한 권위자는 Orca. 하네스는 task contract만 제공 | S01 KEEL 리뷰, S04 리뷰 #5 | ✅ |
| C-D2 | worktree당 writer 1명, reviewer는 read-only | S01 plan §3, S12 상태6 | ✅ |
| C-D3 | 구현자와 리뷰어 분리 (반대 런타임 교차 리뷰) | S01 KEEL 리뷰 §1 | ✅ |
| C-D4 | 실행계획 2단 분리: Delivery Map(개략) / Executable Plan(Spec 승인 후 컴파일) | S10 §3, COUNCIL | v2 |
| C-D5 | 전문가 병렬 협의 (독립 의견 → 반론 → 종합 → 결정 게이트) | S01 사용자 원문, S01 plan §3 | v2 |

---

## E. 검증과 증거 (Verification)

| ID | 능력 | 근거 | v1 |
| --- | --- | --- | --- |
| C-E1 | 완료 선언에 현재 HEAD SHA에 묶인 증거 필요 | S01 KEEL 리뷰 §3, S03 리뷰 #6 | ✅ |
| C-E2 | HEAD 또는 작업 트리가 바뀌면 이전 검증 자동 stale | S03 리뷰 #6 | ✅ |
| C-E3 | 결정적 차단 검사와 휴리스틱 경고 분리 | S01 KEEL 리뷰 §6, S03 리뷰 #7 | ✅ |
| C-E4 | 미확인 항목은 완료가 아니라 **미검증**으로 표기 | AGENTS-P, S07/S08 실사례 | ✅ |
| C-E5 | validation 5종 구분 (intake·product·document·implementation·outcome) | S10 §3, COUNCIL | 부분 |
| C-E6 | outcome gate는 측정 가능한 제품 가설에만 적용 | COUNCIL "5.3 대비 달라진 것" | v2 |

### Evidence 최소 필드

```text
repo_id, run_id, task_id, spec_ref
base_sha, head_sha, dirty_tree_hash
commands, exit_codes, environment
started_at, finished_at
artifact_hash, reviewer, verdict
```

근거: S01 KEEL 리뷰 §3.

---

## F. 기술 지식 유지 (Derived Knowledge)

| ID | 능력 | 근거 | v1 |
| --- | --- | --- | --- |
| C-F1 | 코드에서 파생되는 기술 문서를 에이전트가 자동 유지 | S12 사용자 원문 | v2 |
| C-F2 | 파생 계층이 기획 문서·결정·계획을 소유하지 않는다 | S12 최종 판단 | v2 |
| C-F3 | 파생 갱신은 기준 브랜치 반영 후 1건씩 순차 실행 | S12 "충돌할 수 있는 부분 2" | v2 |
| C-F4 | 코드 동작과 승인된 명세의 차이 검사 (converge) | S12 (Spec Kit `converge`) | v2 |

후보: OpenWiki. 단 **판정 기준이 아니라 비교 대상**이다.
잘못 구현된 코드가 테스트를 통과하면 파생 계층은 그것을 "현재 시스템의 사실"로 기록한다. (S12)

---

## G. 디자인 트랙 (Design)

| ID | 능력 | 근거 | v1 |
| --- | --- | --- | --- |
| C-G1 | UX 구조·상태(빈·로딩·오류·권한없음·성공)·접근성 설계 | S13 | v2 |
| C-G2 | 브랜드·랜딩 아트 디렉션 (레퍼런스 선행) | S01 사용자 원문, S13 | v2 |
| C-G3 | AI slop 안티패턴 카탈로그 (절대금지 / 기본금지+근거예외 / 프로젝트고유) | S01 KEEL 리뷰 §7, S13 | v2 |
| C-G4 | 실제 화면 기반 Visual QA (스크린샷·반응형·키보드·대비·콘솔) | S01 plan §3, S13 | v2 |

디자인 완료 기준은 코드 통과가 아니라 **디자인 문서 승인 → 구현 결과 스크린샷 확인 →
반응형·접근성·오류 상태 검증**으로 분리한다. (S13)

---

## H. 참조 자산 관리 (Provenance)

| ID | 능력 | 근거 | v1 |
| --- | --- | --- | --- |
| C-H1 | 참조 저장소를 고정 SHA로 묶어 근거 중심 한국어 아카이브 생성 | `skills/repo-archive/`, S23 | **구현됨** |
| C-H2 | 아카이브 스키마 검증 + 인덱스 자동 생성 + CI 강제 | `scripts/`, `.github/workflows/` | **구현됨** |
| C-H3 | 원본 버전·경로·checksum·라이선스·수정 여부 추적 | S01 plan §4 | 부분 |
| C-H4 | upstream 변경을 자동 추종하지 않고 update PR로 승인 | S01 plan §4 | v3 |

### 참조 저장소 채택·제외 5기준

1. **목적 적합성** — 기획 계약 / 실행 규율 / 벤더 중립 / 파생 지식 / 디자인 중 어느 빈칸을 채우는가.
2. **경계 충돌** — Orca의 실행 권위, 하네스의 명세 권위와 겹치는가.
3. **채택 단위** — 패턴·규칙·템플릿만인가, 런타임 설치가 필요한가. 런타임이 필요한 부품은 코어에 벤더링하지 않고 `install`로 연결한다(D-51·D-55). 채택 방식 5단계는 [J절](#j-부품-조립-assembly) 참조.
4. **유지비** — upstream 변경 속도와 포크 필요 여부.
5. **출처 추적 가능성** — 고정 SHA 아카이브가 가능한가, 라이선스가 명확한가.

스타 수와 유명세는 기준이 아니다. 판정 결과는 `archive/<owner>-<repo>/05-pm-harness-notes.md`에 기록한다.
근거: S01 plan §4, S13 최종, `archive/README.md`.

---

## I. 자기개선 (Self-improvement)

| ID | 능력 | 근거 | v1 |
| --- | --- | --- | --- |
| C-I1 | 실패 증거 → lesson 후보 → 재현 fixture → 개선안 → 양 런타임 평가 → 승인 → 새 버전 | S01 사용자 원문, S01 plan §4 | v3 |
| C-I2 | 작업 중 live skill 자동 수정 **금지** | S01 KEEL 리뷰 §8 | ✅ 규칙 |
| C-I3 | 하네스 자체 성공 지표 8종 계측 | COUNCIL §3 | v2 |

### 하네스 성공 지표 8종

사람이 분류를 수정한 비율 / 누락된 hard gate 수 / T0 처리 시간 /
생성 문서 중 실제로 다시 읽힌 비율 / 중복 문서 발생률 / stale·broken dependency 수 /
요청당 모델 호출과 토큰 사용량 / 실행 중 재분류된 비율. (COUNCIL §3)

---

## J. 부품 조립 (Assembly)

2026-08-27 사용자 재정의("잘 썼던 하네스들을 조립해서 나만의 라우터 체계로")에서 승격했다.
A~I가 "라우터와 접착이 무엇을 할 수 있는가"라면, J는 "부품을 어떻게 붙이고 떼는가"다.
근거 기록: [개정 3 요약](../reviews/2026-08-27-assembly-redefinition/summary.md).

| ID | 능력 | 왜 필요한가 | 근거 | v1 |
| --- | --- | --- | --- | --- |
| C-J1 | 라우터가 unit·mode·facet·profile로 **어떤 부품을 켤지** 결정하고 근거를 분류 카드에 인쇄 | 사용자 최초 요구: "어떤 bmad 워크플로우가 필요한지 자동 추천" | S01 사용자 원문, D-50 | ✅ |
| C-J2 | 채택 방식 5단계(`install`/`verbatim`/`rewrite`/`principle`/`excluded`)를 부품·**파일 단위**로 `provenance/imports.yaml`에 기록 | "원칙만 vs 원문" 이분법이 실사용 검증된 흐름을 탈락시켰다 | D-51 | ✅ |
| C-J3 | **채택 확정 게이트**: 마일스톤 진입 시 후보표 제시 → 사용자 확정 → `status: accepted` | 무엇을 가져올지는 제품 결정이다. 구현 세션이 즉흥 판단하면 안 된다 | D-52, 2026-08-27 사용자 요청 | ✅ |
| C-J4 | 부품 산출물을 접착 문서로 흡수 (frontmatter `inputs`/`evidence` 링크, `docs/work/<id>/`) | 부품 기본 경로가 제각각이라 링크 없이는 고아 문서가 된다 | K-62 | ✅ |
| C-J5 | 부착 검증: `doctor` 프로브(존재·버전·양 런타임 discovery) + 충돌 fixture 3종 | "설치됐다"와 "동작한다"는 다른 주장이다 (archive `05` 노트 전부) | K-68, K-51 | ✅ |
| C-J6 | 부품 업데이트 비교·선택 반영: `/repo` 재아카이브 → diff → 게이트 재통과 | 자동 추종은 조용한 드리프트를 만든다 | K-67, C-H4 | v2 |

### 부품 조립표 (후보)

파일 단위 확정은 게이트에서 한다. 이 표는 후보와 경계를 기록한다.

| 부품 | 담당 | 채택 방식(후보) | 켜는 조건 | 제외·조정 | 게이트 |
| --- | --- | --- | --- | --- | --- |
| Orca | 실행·worktree·dispatch·gate | `install` (사용 중) | 위임이 필요한 T1+ | — | — |
| Superpowers | 승인 이후 개발 규율 | `verbatim` 세트: `test-driven-development` · `systematic-debugging` · `verification-before-completion` · `requesting-code-review`(+`code-reviewer.md`) · `receiving-code-review` · `using-git-worktrees` · `finishing-a-development-branch` · `subagent-driven-development`(+프롬프트 템플릿) · `executing-plans` · `dispatching-parallel-agents` · `writing-plans`(출력 경로만 override) | `profile ≥ standard` 구현·리뷰 | `brainstorming`(→ `/plan`), `using-superpowers`(→ profile 라우팅), bootstrap hook, visual companion | G-M2 |
| BMAD 본체 + CIS | 발산·문제 정의·전략·스토리·PRD facilitation | `install` 프로젝트별 + `/plan` 링크 (v6.10.0 / CIS v0.2.1 고정) | `mode=discovery`, T2 | 벤더링·템플릿 재작성 없음; 산출물은 입력 링크; 사람 대화형이라 parity 비대상(Claude 전용 능력으로 정직 표기) | G-M3 |
| OpenWiki | 기술 문서 파생 | `install` | 기준 브랜치 반영 후 | 기획·상태 미소유(D-23); `docs/work/**`는 `.openwikiignore` | G-M7 |
| WIG | UI 감사 체크리스트·`file:line` 출력 계약 | `verbatim` (`AGENTS.md`·`command.md`) | `facet=ui` 리뷰 | `install.sh` 제외 | G-M6 |
| taste-skill | 랜딩·브랜드 생성 규칙 | `verbatim` (`design-taste-frontend` v2) | `facet=brand` 랜딩 | 제품 UI에는 적용 안 함 (D-37) | G-M6 |
| impeccable | `DESIGN.md`/`PRODUCT.md` 계약, finish-reviewer 판정 | `verbatim` 스킬 본문·판정 규칙 + `rewrite` 계약 스키마 | `facet=ui` | CLI·hook·4 서브에이전트 제외 | G-M6 |
| ui-ux-pro-max | 디자인 시스템 검색·`design-review` | 라이선스 확인 후 `verbatim`(`cli/` 제외) | `facet=ui` 신규 화면 | `--global`·`stack/` MCP `@latest` 제외 | G-M6 |
| `visual-qa` | 스크린샷·반응형·접근성 evidence 계약 | **자체 제작** (유일) | `facet=ui` close 전 | — | M6 |
