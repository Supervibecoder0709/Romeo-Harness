# Romeo 하네스 구현 계획 리뷰

검토일: 2026-08-27  
검토 대상: `/Users/julliettelee/orca/workspaces/Romeo-Harness/mvp_planning/docs/planning/implementation-plan.md` (`PLAN`)  
기준: 현재 worktree의 정본 요구사항 6종, `CLAUDE.md`, 저장소 실물, 사용자 구현 계획 요청 원문  
리뷰 전 확인 상태: `Supervibecoder0709/codex-plan-review`, HEAD `324d63e`, 작업 트리 clean, stash 없음

## 1. 최종 판정

**주요 수정 후 구현 가능**

얇은 정책 척추, Orca와의 소유권 경계, 두 런타임의 공통 계약이라는 핵심 구조는 요구사항과 잘 맞으므로 전면 재설계할 필요는 없다. 다만 계획은 M2를 v1 합격선으로 선언하면서 정본의 v1 필수인 Charter, 프로젝트 부착 상태, shadow mode 20건을 M3~M5로 미루어 완료 기준이 서로 충돌한다. 또한 M2의 migration 성격 작업보다 승인 가드가 늦고, reviewer read-only와 작업 트리 변경 후 evidence stale 판정이 사후 관찰 또는 부분 명세에 그쳐 핵심 안전·검증 요구를 아직 보장하지 못한다. 이 네 경계와 설치·업데이트의 복구 계약을 구현 전에 최소 수정하면 기존 단계 구조를 대부분 유지할 수 있다.

등급별 발견 사항: **BLOCKER 0 · MAJOR 5 · MINOR 3 · PREFERENCE 0 · HOLD 0**

## 2. 반드시 유지할 결정

### K-01. Thin Policy-Compiled Planning Spine을 공통 뼈대로 유지

- **결정:** unit(T0/T1/T2), mode, facet·hard gate를 독립 축으로 두고, 사람이 확정한 입력을 정책표가 문서 패키지와 실행 조건으로 계산한다.
- **잘한 이유:** 요청 크기와 위험을 한 점수로 섞지 않으면서도 같은 입력의 라우팅 근거를 `policy_version`과 `fired_rules`로 재현할 수 있다.
- **관련 요구사항:** C-A2~A7, D-02~D-07, K-20.
- **근거 파일 또는 계획 위치:** `docs/requirements/capability-map.md:20-43`, `docs/decisions/decision-register.md:23-36`, `PLAN:168-232`.

### K-02. LLM 제안 / 사람 확정 / 규칙 강제의 3분할 유지

- **결정:** LLM은 사실·가정·미확인·분류 후보를 만들고, 사람은 의미적 판단을 확정하며, 결정적 정책표가 패키지와 차단을 계산한다.
- **잘한 이유:** 의미 판단을 가짜 결정론으로 만들지 않으면서도 생성 이후의 규칙 집행은 테스트 가능하게 만든다.
- **관련 요구사항:** C-A1, C-A7, D-06, V-0, V-10.
- **근거 파일 또는 계획 위치:** `docs/requirements/v1-scope.md:34-44`, `docs/planning/open-questions.md:23-28`, `PLAN:100-120, 185-230`.

### K-03. Romeo와 Orca의 소유권 경계 유지

- **결정:** Romeo는 제품 의도·정책·실행 계약·evidence 형식을 소유하고, Run·Task·Dispatch·worktree·대기·재시도는 Orca가 소유한다.
- **잘한 이유:** 두 번째 스케줄러와 이중 상태 머신을 만들지 않으며 Orca 교체 시에도 TaskEnvelope 경계를 보존할 수 있다.
- **관련 요구사항:** C-D1, K-10, D-20.
- **근거 파일 또는 계획 위치:** `docs/product/harness-brief.md:52-63`, `docs/requirements/constraints.md:35-42`, `PLAN:153-164, 213-230`.

### K-04. 벤더 중립을 “같은 프롬프트”가 아닌 “같은 계약과 판정”으로 정의한 결정 유지

- **결정:** 공통 schema·Acceptance Criteria·권한·gate·evidence를 두 어댑터가 각 런타임 형식으로 투영하고 역할 교체로 parity를 검증한다.
- **잘한 이유:** Claude와 Codex의 네이티브 형식과 출력 차이를 인정하면서도 비교 가능한 합격 기준을 만든다.
- **관련 요구사항:** C-C1~C6, D-12, V-5, V-9.
- **근거 파일 또는 계획 위치:** `docs/requirements/capability-map.md:78-100`, `docs/requirements/v1-scope.md:52-67`, `PLAN:234-243, 260-270`.

### K-05. 역할·인프라·참고 자산의 확대를 트리거 뒤로 미룬 결정 유지

- **결정:** implementer/reviewer 두 역할로 시작하고, DB·큐·자동 모델 라우팅·OpenWiki·디자인 4스킬·자기개선은 관찰된 필요가 생길 때만 추가한다.
- **잘한 이유:** 에이전트·폴더 수를 진척으로 착각하지 않고 운영자 주의력과 유지비를 첫 제약으로 취급한다.
- **관련 요구사항:** K-20~K-21, K-30~K-32, V1 명시적 제외, D-30~D-37.
- **근거 파일 또는 계획 위치:** `docs/requirements/v1-scope.md:73-88`, `docs/decisions/decision-register.md:61-73`, `PLAN:272-288, 356-391`.

## 3. 발견 사항

### F-01

- **ID:** F-01
- **등급:** `MAJOR`
- **문제 또는 강점:** v1의 합격선과 v1 필수 산출물의 구현 시점이 서로 모순된다.
- **근거:** 정본은 V-0~V-10을 “v1에 반드시 들어가는 것”으로 두며 Charter(V-2), 부착 상태(V-8), shadow mode 20건(V-10)을 포함한다(`docs/requirements/v1-scope.md:30-45`). PLAN은 M2를 “v1 유일 합격 기준”으로 부르지만(`PLAN:260-270, 421-430`), Charter는 M3, shadow mode 완료는 M4, 부착 상태·업데이트는 M5에 둔다(`PLAN:432-463`). §4.2는 다시 M2와 shadow mode를 v1 완료 조건으로 적어(`PLAN:288`) 문서 안에서도 기준이 달라진다.
- **실제 영향:** M2 통과만으로 v1 완료를 선언하거나, 반대로 M5까지 끝났는데도 어느 gate가 릴리스 기준인지 알 수 없게 된다. 구현자·리뷰어·PM이 서로 다른 완료 정의를 사용하면 문서 승인과 실제 구현 상태가 다시 섞인다.
- **최소 수정안:** M2를 `core parity gate`로 이름만 바꾸고, `v1 release gate`는 V-0~V-10 충족으로 한 곳에 정의한다. 또는 정말 M2를 v1로 삼으려면 먼저 정본 `v1-scope.md`에서 Charter·V-8·V-10의 버전을 변경하는 별도 승인 결정을 받아야 한다.
- **확신도:** 높음

### F-02

- **ID:** F-02
- **등급:** `MAJOR`
- **문제 또는 강점:** M2의 실제 payload가 migration facet인데, 위험 승인 gate의 집행과 검증은 M3에서야 구현된다.
- **근거:** M2는 18개 `_source.md` backfill을 `migration(내부 데이터)`로 분류한다(`PLAN:260-269`). 그러나 `gate-create` 승인 흐름과 위험 시나리오 검증은 M3 산출물이다(`PLAN:432-441`). K-50은 마이그레이션·운영 데이터 변경 등 되돌리기 어려운 행동에 영향 범위·복구 방법·명시 승인을 실행 전에 요구한다(`docs/requirements/constraints.md:84-95`).
- **실제 영향:** 안전 게이트가 아직 없는 단계에서 게이트 대상이라고 스스로 분류한 변경을 실행하게 된다. M2가 v1 합격선이라는 선언과 결합하면 안전 요구를 검증하지 않고 핵심 목표 달성으로 오인할 수 있다.
- **최소 수정안:** M2 전에 `execution-guards`의 최소 집행(정확한 대상·영향·복구·승인 기록)을 넣거나, M2 payload를 hard gate가 없는 T1로 바꾼다. hard gate 8종 전체 시나리오 확장은 M3에 그대로 두어도 된다.
- **확신도:** 높음

### F-03

- **ID:** F-03
- **등급:** `MAJOR`
- **문제 또는 강점:** reviewer read-only가 런타임에서 강제되지 않고 `git status` 사후 비교에 주로 의존한다.
- **근거:** C-D2는 reviewer read-only를 v1 필수로 둔다(`docs/requirements/capability-map.md:104-113`). PLAN도 Orca가 이를 강제하지 못한다고 인정하고 전후 `git status` 비교로 완화한다(`PLAN:506-515`), M2 검증 역시 같은 비교가 중심이다(`PLAN:425-429`). 현재 로컬 CLI에는 Codex `-s read-only`와 Claude `--tools`·`--allowedTools`·`--disallowedTools`가 실제로 존재하지만 계획은 reviewer별 강제 프로필을 명시하지 않는다.
- **실제 영향:** reviewer가 tracked 파일을 되돌려 놓거나 ignored 파일·외부 서비스·브라우저 세션을 바꾸면 `git status`가 같아도 read-only 계약 위반을 놓친다. 독립 리뷰 증거 자체가 신뢰할 수 없게 된다.
- **최소 수정안:** Codex reviewer는 `-s read-only`, Claude reviewer는 Write/Edit와 상태 변경 Bash를 제외한 명시적 도구 허용 목록으로 실행하도록 어댑터 계약에 넣는다. 테스트가 쓰기 가능한 캐시를 요구하면 별도 임시 실행 환경에서 수행하고, 전후 diff/status 비교는 강제 수단이 아니라 방어적 검증으로 남긴다.
- **확신도:** 높음

### F-04

- **ID:** F-04
- **등급:** `MAJOR`
- **문제 또는 강점:** evidence 개념에는 `dirty_tree_hash`가 보이지만 실제 단계의 합격·stale 검증은 HEAD 변경 중심이라 작업 트리 변화를 완전히 묶지 못한다.
- **근거:** 정본 C-E2는 HEAD **또는 작업 트리**가 바뀌면 이전 검증을 stale로 요구한다(`docs/requirements/capability-map.md:116-135`). PLAN 다이어그램에는 dirty hash가 있으나(`PLAN:220-227`), M1의 관찰 결과와 검증은 `head_sha` 일치 및 “HEAD를 한 커밋 올린 뒤” 거부만 명시한다(`PLAN:410-419`). §4.1도 변경 파일 해시를 말하지만 작업 트리 전체의 정규화 범위와 재계산 규칙은 없다(`PLAN:251-269`).
- **실제 영향:** 검증 뒤 같은 HEAD에서 tracked 수정, staged 변경, untracked 파일 변화가 생겨도 close가 통과할 수 있다. 구현 중 HEAD가 유지되는 일반적인 dirty worktree에서는 SHA만으로 어떤 바이트를 검증했는지 재현할 수 없다.
- **최소 수정안:** Evidence 계약에 `base_sha`, `head_sha`, `dirty_tree_hash`, 포함·제외 경로와 해시 정규화 방식을 필수로 확정한다. stale 테스트를 commit 이동뿐 아니라 tracked·staged·untracked 변경 각각에 대해 추가한다.
- **확신도:** 높음

### F-05

- **ID:** F-05
- **등급:** `MAJOR`
- **문제 또는 강점:** 프로젝트 attach/update의 덮어쓰기 방지는 방향은 맞지만 복구 계약이 Git 추적 상태를 과도하게 가정한다.
- **근거:** 요청 원문은 프로젝트 설정을 무조건 덮어쓰지 않고 충돌 표시, 전후 검증, 이전 버전 복구를 요구한다(`implementation-plan-request.md:220-232`). PLAN은 managed hash 3-way 비교와 dry-run을 제안하지만 실패 복구를 “생성물은 git 추적 → git checkout”으로만 둔다(`PLAN:454-463`). 새 attach 직후의 untracked 파일, 이미 dirty인 대상, managed block 밖과 안이 함께 바뀐 파일, 중간 실패의 원자성은 정의하지 않았다.
- **실제 영향:** 실제 프로젝트가 clean·committed 상태가 아니면 `git checkout`만으로 새 파일 삭제나 사용자 변경 복원이 되지 않는다. 상태 파일만 갱신되거나 일부 파일만 교체된 반쪽 설치가 남을 수 있다.
- **최소 수정안:** M5에 preflight(대상 root·branch·dirty 상태·정확한 파일/블록·현재 hash), dry-run 기본, 파일별 명시 승인, 임시 staging 후 원자적 교체, 성공 후 상태 파일 갱신, 실패 시 생성 파일까지 포함한 백업 복원 절차를 추가한다. `--accept-theirs`는 전체 플래그가 아니라 충돌 파일별 승인으로 제한한다.
- **확신도:** 높음

### F-06

- **ID:** F-06
- **등급:** `MINOR`
- **문제 또는 강점:** M0가 실제 요청의 종단 흐름보다 많은 수평 산출물을 먼저 만들며, 폴더·스키마 생성이 첫 진척 신호가 될 여지가 있다.
- **근거:** M0는 정책표 3종, 스키마, 템플릿, workflow, Python CLI 4명령, tests, provenance와 NOTICE 골격을 한 번에 만든다(`PLAN:399-408`). 사용자가 요구한 첫 관찰 흐름은 요청 입력부터 검증·상태 기록까지이며(`implementation-plan-request.md:305-313, 340-357`), 정본도 실제 관통 결과를 유일한 합격 기준으로 둔다(`docs/requirements/v1-scope.md:48-67`).
- **실제 영향:** M0 PASS가 높아도 실제 `/plan → 실행 → evidence → close` 연결 실패가 늦게 드러날 수 있다. 특히 provenance 골격처럼 아직 채택 자산이 없는 파일은 “만들었다”는 진행감만 준다.
- **최소 수정안:** M0의 gate는 fixture·최소 정책·Tech Spec·`/plan --dry-run`까지만 두고, 그 산출물을 같은 fixture의 M1 입력으로 즉시 연결한다. provenance/NOTICE 골격과 범용 CLI 하위 명령은 실제 첫 소비자가 생길 때 추가하되 전체 단계 번호는 유지한다.
- **확신도:** 중간

### F-07

- **ID:** F-07
- **등급:** `MINOR`
- **문제 또는 강점:** M0의 선행 결정 설명과 마지막 실행 프롬프트가 서로 달라 되돌릴 수 있는 구현까지 불필요하게 멈출 수 있다.
- **근거:** M0 본문은 profile 라벨과 상태 모델만 있으면 되고 라이선스는 M0를 막지 않는다고 한다(`PLAN:403-405`). 반면 최종 프롬프트는 라이선스, profile, 상태 모델, v1 코드 프로젝트 범위를 모두 채운 전제로 요구한다(`PLAN:568-577`), PM 브리프도 다섯 결정을 먼저 답하라고 한다(`implementation-plan.html:308-351`).
- **실제 영향:** 라이선스나 비코드 범위가 미정이라는 이유로 신규·가역 파일만 만드는 M0 전체가 중단될 수 있고, 실제로 필요한 결정과 단순한 미결정 기록이 구분되지 않는다.
- **최소 수정안:** M0의 진짜 blocking decision을 frontmatter schema와 profile 표현 두 개로 제한한다. 라이선스·비코드 범위는 `UNKNOWN/NEEDS_DECISION`으로 기록하고 그 값을 사용하는 단계 직전에만 gate로 승격한다.
- **확신도:** 높음

### F-08

- **ID:** F-08
- **등급:** `MINOR`
- **문제 또는 강점:** 첫 T0 payload의 근거인 `rg` 설치 경로가 이미 바뀌어 예시의 필요성이 현재 상태와 어긋난다.
- **근거:** PLAN은 `rg`가 `/Applications/ChatGPT.app/Contents/Resources/rg`라서 취약하다고 기록한다(`PLAN:46-54, 147-150`). 이 리뷰 시점의 read-only probe에서 `command -v rg`는 `/Users/julliettelee/.codex/packages/standalone/releases/0.147.0-aarch64-apple-darwin/codex-path/rg`, `rg --version`은 `15.2.0`을 반환했다. 저장소 스크립트가 `rg`에 의존하는 사실은 맞다(`scripts/validate-repo-archive.sh:36-41`).
- **실제 영향:** 핵심 하네스 흐름의 첫 실제 작업이 이미 낡은 환경 관찰을 고치는 일로 고정된다. portability 문제는 남지만 “ChatGPT 앱 삭제 시 깨진다”는 복구 논리는 현재 증거가 아니다.
- **최소 수정안:** M1 시작 시 `command -v rg`와 CI 환경을 다시 probe하고, 실제 실패 fixture가 없으면 이 작업을 일반 T0 후보로만 남긴다. 첫 payload는 현재 관찰 가능한 사용자 가치가 있는 작은 요청으로 선택한다.
- **확신도:** 높음

## 4. 요구사항 누락 검사

| 요구사항 | 계획의 대응 위치 | 상태 | 검증 방법 |
|---|---|---|---|
| 사실·가정·미확인 분리와 분류 후보 제안(C-A1) | `PLAN:185-205`, M0 | 충분히 반영 | `/plan --dry-run` 카드 fixture에서 네 구획과 근거 존재 검사 |
| T0/T1/T2 + mode + facet 독립 축, hard gate 8, 합산 점수 금지(C-A2~A7) | `PLAN:185-205`, 정책표 3종 | 충분히 반영 | 15~20 fixture의 기대 unit·mode·facet·gate와 `fired_rules` 대조, gate 누락 0 |
| 사람 확정과 shadow mode 20건(V-10) | M0 카드 5건, M4에서 20건 완료 | 일부 반영 | 20건 모두 승인/수정 기록과 분류 수정률 집계; v1 gate 이전인지 확인 |
| 템플릿 3개와 최소 문서 패키지(V-2) | Tech Spec·Brief는 M0, Charter는 M3 | 일부 반영 | 세 템플릿 스키마·길이 cap 검사 후 T0/T1/T2 fixture 생성 비교 |
| `/plan` 재사용 검색→제안→사람 확정→필요 문서 생성(V-3) | M0, M4에서 재사용 검색 보강 | 일부 반영 | 같은 요청 재실행 시 중복 생성 없이 기존 unit 제시; 재분류 history 보존 |
| `/plan-close` 스키마·링크·미체크·예산·open-loop 검사(V-4) | M1, M4 보강 | 일부 반영 | 각 실패 fixture가 명시 사유로 거부되고 정상 건만 status 갱신 |
| 공통 정의→Claude/Codex 최소 어댑터, managed marker/hash(V-5) | M2 | 충분히 반영 | fresh project에서 양 런타임 discovery, marker 밖 사용자 텍스트 보존, source hash 불일치 감지 |
| implementer 1명 + reviewer read-only(V-6, C-D2) | M2 | 일부 반영 | reviewer 프로세스의 런타임 권한이 write를 거부하는지 확인하고 전후 diff/status 보조 검사 |
| HEAD와 작업 트리에 묶인 Evidence, 변경 시 stale(V-7, C-E1~E4) | M1/M2 | 일부 반영 | commit·tracked·staged·untracked 변경 각각에 close FAIL; 명령·종료코드·환경·artifact hash 재현 |
| 비용·권한·공개·운영 데이터·삭제의 승인·복구(K-50) | execution-guards M0, 실제 gate M3 | 일부 반영 | 정확한 대상·영향·백업·복구가 없는 gate는 생성 실패; 승인 전 상태 변경 0 |
| Orca가 실행 상태의 유일한 권위자(K-10, D-20) | 구조 §3, Orca RUNBOOK M2 | 충분히 반영 | Romeo 저장소에 Run/Dispatch 재시도 상태가 중복 저장되지 않는지 검사 |
| 부착 상태 파일(V-8)과 프로젝트 설정 보존·업데이트·롤백 | M5 | 일부 반영 | dirty/untracked/managed-block 충돌 fixture에서 dry-run·부분 실패·롤백을 실제 sandbox repo로 검증 |
| 기획·디자인·개발의 독립 호출, 구현만 승인 Spec 요구(D-27) | `PLAN:230-232`, M6 조건부 | 충분히 반영 | 비-UI T0/T1에 디자인 산출물 0, discovery가 필요할 때만 차단, 승인 없는 구현 dispatch 거부 |
| DB·큐·자동 모델 라우팅·OpenWiki·디자인 4스킬·자기개선 연기 | §4.2, M6/M7 | V1 이후로 합리적으로 연기 | v1 산출물 트리와 실행 로그에 해당 런타임·상태 저장소가 생기지 않았는지 검사 |

## 5. 구현 순서 검사

**판단:** 현재 계획은 M1에서 아래 최소 흐름을 처음 완성하므로 방향은 맞지만, M0의 수평 산출물이 앞에 크고 M2를 v1 완료로 부르는 시점이 정본 및 안전 gate와 맞지 않는다. 따라서 순서를 전면 재작성할 필요는 없고 다음 이동만 필요하다.

```text
요청 입력
→ 작업 깊이 판단
→ 필요한 워크플로우 선택
→ 계획 또는 실행 방식 결정
→ 실행 결과 검증
→ 상태와 증거 기록
```

### 앞당겨야 할 단계

- M2 전에 최소 execution guard와 승인 evidence를 둔다. gate가 없는 T1을 M2 payload로 고르면 전체 hard gate 시나리오는 M3에 남겨도 된다.
- reviewer별 런타임 read-only 강제와 dirty-tree hash/stale 검증을 M2의 선행 합격 조건으로 올린다.
- v1을 V-0~V-10으로 유지한다면 Charter, 최소 부착 상태 파일, shadow mode 20건의 **릴리스 gate**를 M2 뒤라도 v1 완료 선언 전으로 올린다.

### 늦춰야 할 단계

- M0의 `provenance/imports.yaml`·`THIRD_PARTY_NOTICES.md` 골격은 실제 외부 자산을 채택하는 첫 단계로 늦춘다.
- 범용 `doctor`, metrics, 디자인·OpenWiki 확장은 현재 계획처럼 관찰 트리거 뒤에 두되 v1 필수와 섞어 표기하지 않는다.

### 합쳐야 할 단계

- M0의 최소 정책·Tech Spec·`/plan --dry-run` 결과를 별도 “기반 완료”로 닫지 말고, 같은 fixture를 M1의 `/plan → 실행 → evidence → close` 입력으로 즉시 이어 하나의 수직 gate로 취급한다.
- `status`, `approved_at`, Orca 실행 상태, 계산된 stale의 소유권 설명을 하나의 상태 계약 절로 합쳐 문서 승인과 구현 진행의 의미를 고정한다.

### 제거하거나 V1 이후로 미뤄야 할 단계

- 현재 관찰 근거가 사라진 `rg` 폴백을 고정 첫 payload에서 제거하고 probe 결과에 따른 후보로 둔다.
- v1 합격 이전의 full attach/update 적용, metrics 4종, 디자인·파생 지식은 제거가 아니라 정본 트리거 뒤로 유지한다. 단 V-8의 **최소 부착 상태 파일**만 full updater와 분리해 v1에 남긴다.

## 6. 최종 수정 목록

### 구현 전에 반드시 수정

1. M2 `core parity gate`와 V-0~V-10 `v1 release gate`를 분리하고 문서 전체의 완료 표현을 하나로 통일한다.
2. M2의 gate 대상 payload를 바꾸거나 최소 실행 승인 가드를 M2 앞으로 옮긴다.
3. reviewer read-only를 Codex sandbox와 Claude 도구 허용 목록으로 런타임 강제하는 계약을 추가한다.
4. Evidence의 dirty-tree 정규화 범위와 commit·tracked·staged·untracked stale 테스트를 확정한다.
5. attach/update에 dirty preflight, 정확한 대상 diff, 파일별 승인, 원자적 적용, untracked 파일까지 포함한 복구 절차를 추가한다.

### 구현하면서 검증 가능

- Quick/Standard/Deep 임계와 표시명, T0/T1/T2 3-tier의 충분성, 템플릿 길이 cap.
- 정책표 정확도와 gate 누락률, 경로 불변의 탐색성, `rg` 의존성의 실제 portability.
- Orca dispatch 안정성, Codex/Claude 네이티브 projection 형식, 모델·effort 바인딩.
- OpenWiki 가치, 디자인 트랙 상세, MCP registry, 자동 모델 라우팅은 각 도입 트리거 뒤 실험으로 판단한다.

### 변경하지 않아도 됨

- Thin Policy-Compiled Planning Spine과 unit/mode/facet 분리.
- LLM 제안 / 사람 확정 / 정책 강제 3분할과 fixture·shadow mode 접근.
- Romeo는 계약, Orca는 실행 상태, 코드·테스트는 실제 동작이라는 소유권 경계.
- 같은 프롬프트가 아니라 같은 schema·AC·gate·evidence로 정의한 runtime parity.
- implementer/reviewer 두 역할로 시작하고 DB·큐·자동 라우팅·OpenWiki·디자인·자기개선을 트리거 뒤로 미루는 결정.
