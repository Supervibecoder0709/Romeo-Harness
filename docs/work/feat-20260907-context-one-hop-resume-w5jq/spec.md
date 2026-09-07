---
id: feat-20260907-context-one-hop-resume-w5jq
type: spec
title: 1-hop 재개 — `romeo context <id>` 가 다음 세션이 읽을 파일 목록을 낸다
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: small
uncertainty: medium
status: active
approved_at: '2026-09-07T23:59:31+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: init-20260904-m4-doc-reuse-metrics-wr9m
inputs: [../init-20260904-m4-doc-reuse-metrics-wr9m/charter.md, inputs/probe-2026-09-07.patch]
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'profile:uncertainty.medium=kept', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-09-07'
updated: '2026-09-07'
---

# 1-hop 재개 — `romeo context <id>` 가 다음 세션이 읽을 파일 목록을 낸다

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260907-context-one-hop-resume-w5jq --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** M4 이니셔티브(`init-20260904-m4-doc-reuse-metrics-wr9m`)의 두 번째 마일스톤 — 하위 명령 `romeo context <id>` 를 더한다.
  한 단위 id 로 **다음 세션이 읽어야 할 파일 목록**을 역할과 함께 낸다: 그 단위 폴더의 파일 전부(정본 `spec`·`brief`·`charter` · 회차 `attempts.yaml` ·
  계약 `task/` · 증거 `evidence/` · 결과 `result/` · 검토 `review/` · 그 밖의 산출물)와 frontmatter 가 가리키는 것(`parent` 의 charter — 없으면 spec — 과
  `inputs` 의 각 경로)까지, **1-hop 만**이다(K-31). 파일마다 파일에 적힌 사실(회차 결과·판정·findings 수·등록 여부)을 붙이되 다음 행동을 추천하지 않는다.
  `/plan` 절차 1단계가 재개를 제안·선택할 때 이 목록을 읽는 범위로 삼는다.
- **왜 지금:** charter 의 M2 칸이고 progress 「다음 행동」이 ③ 을 지목했다. 절차 1단계는 겹치는 단위가 있으면 「재개」를 제안하라고 요구하지만
  **재개할 때 무엇을 읽는지는 어디에도 없다** — 요구만 있고 집행이 없는 모양(§11)이다. 31개 단위에 회차·검토 봉투·증거가 쌓여 폴더를 눈으로 훑는 방식은
  어느 증거가 검사 기록이고 어느 회차가 어떻게 끝났는지 말해 주지 않는다. D-81 ② 뒤 첫 단위라 종료 검사는 승인 커밋 스냅샷이 낸다 — 새 규칙이 처음으로 남을 판정한다.
- **기대 결과:** `bin/romeo context <id>` 한 줄이 그 단위의 재개에 필요한 파일을 역할·사실과 함께 인쇄한다 — 예: 마지막 단위 `feat-20260907-judge-revision-base-sha-pwt8` 은
  「파일 10 · 없음 0 · 정본 2 · 입력 1 · 회차(1 fail(goal) · 2 pass) · 증거 2(등록됨) · 결과 2 · 검토 2(FAIL findings 1 · PASS findings 1)」로 나온다(프로브 실측).
  깨진 참조는 `[없음]` 으로 보이고 종료 코드는 0 이다. 없는 id 는 한 줄 오류와 exit 1 이다. **재개하는 다음 세션 — 이 단위의 검토자 세션 — 이 그 목록만 받고 판정을 낸다(1회 실측).**
- **수용 기준:**
  - [ ] AC-1 `romeo context <id>` 가 단위 폴더 안의 파일을 **하나도 빠뜨리지 않고** 인쇄한다(폴더 안 파일 누락 0). 각 줄은 역할 한 낱말(`정본`·`상위`·`입력`·`회차`·`계약`·`증거`·`결과`·`검토`·`기타`)로 시작하고
        정본이 먼저다 — `spec.md` 가 있으면 그것이 첫 파일 줄이다. `--json` 은 `unit`(id·title·status·approved_at·closed_at·parent·dir)·`files`(path·role·exists·note)·`missing` 을 담는다. 경로는 프로젝트 루트 기준 상대 경로다.
  - [ ] AC-2 **1-hop.** frontmatter 의 `parent` 는 `docs/work/<parent>/charter.md`(없으면 `spec.md`) 한 파일로, `inputs` 의 각 항목은 단위 폴더 기준 상대 경로를 푼 한 파일로 목록에 든다.
        그 너머 — 입력 단위의 다른 파일, 부모의 증거·회차, 부모의 부모 — 는 들지 않는다. 같은 파일이 두 경로로 가리켜지면 한 번만, 먼저 온 역할(상위 → 입력)로 든다.
  - [ ] AC-3 없는 id 는 종료 코드 1 과 `ERROR` 로 시작하는 stderr 한 줄(id 포함)로 끝나고 `Traceback` 이 없다.
  - [ ] AC-4 git 이력이 없는 루트(`--root`)에서도 돈다. 없는 참조(`parent`·`inputs` 가 가리키지만 파일이 없는 것)는 `[없음]` 줄로 역할과 함께 인쇄하고 `missing` 에 그 경로를 넣되
        **종료 코드는 0** 이다 — 드러내되 막지 않는다. 워커 트리에만 있는 것들 — 계약(`task/` 는 git 에 없다)·등록되지 않은 증거·결과 계약 — 도 있으면 목록에 든다.
        증거는 spec frontmatter `evidence:` 에 있으면 「등록됨(검사 기록)」, 없으면 「미등록」이다.
  - [ ] AC-5 **사실만 붙인다.** 회차 파일은 `회차 N · <n> <result>(<failure_class>)…`, 검토 봉투는 `<gate_verdict> · findings <N>`, 결과 봉투는 `<role> · <gate_verdict>`,
        계약은 `<role> · base <SHA 앞 12자>`, 증거는 등록 여부와 `명령 <N>건 · head <SHA 앞 12자>`, 헤더는 status·승인일·종료일·parent 다 — 전부 그 파일에 적힌 값이다.
        명령이 **덧붙이는** 문장(역할·note·헤더 라벨)에는 「추천」·「다음 행동」 이 없다 — 파일에서 읽어 옮긴 제목·값은 그 파일의 것이다(제목에 「추천」이 든 단위가 실재한다).
        파일 하나가 깨져도 목록은 나온다 — 그 줄만 「읽을 수 없다」가 붙는다.
  - [ ] AC-6 이 저장소의 모든 단위(`docs/work/*`, 31개 이상)에서 종료 코드 0 이고 깨진 참조가 0 이다(전수).
  - [ ] AC-7 `core/workflows/plan/SKILL.md` 절차 1단계가 재개할 때 읽는 범위로 이 명령을 지정하고, 검사가 **`## 절차` 아래 1단계 본문만** 읽어 거기 적힌 `romeo <하위명령>` 이름을 뽑은 뒤
        **기존 단위 id 로 실제 실행해** 그 단위의 `spec.md` 경로가 출력에 나오는 것까지 확인한다 — `romeo find` 는 폴더까지만 내므로 이름 대조로는 부족하다.
        어댑터 산출물은 바뀌지 않고 `bin/romeo compile --check` 가 통과한다.
  - [ ] AC-8 **1회 실측의 자리.** 검토자를 띄우기 전에 코디네이터가 워커 트리에서 `bin/romeo context <이 단위 id> --root "$W"` 를 검토 run 의 증거로(`evidence run`, 라벨 `context-resume`) 기록하고,
        검토자 브리프에 그 출력을 「읽을 파일」로 그대로 넣는다 — 검토 run 의 `evidence/<run>.yaml` 의 `commands` 에 `context-resume` 가 exit 0 으로 있다.
        검토자는 판정의 `notes` 에 목록 밖에서 열어야 했던 파일이 있으면 그 경로를, 없으면 「목록 밖 파일 없음」을 적는다 — 그 관찰이 이 마일스톤의 실측이고 판정 조건이 아니다.
        이 항목의 체크는 구현자가 아니라 코디네이터가 `context-resume` 를 기록한 뒤 검토자 기동 전에 한다.
  - [ ] AC-9 이번 작업이 발견했으나 고치지 않은 것이 `docs/planning/open-questions.md` 새 행(Q-85~)으로 열린다 — 최소 둘: 재개 절차(구현자·검토자 브리프 정본)가 이 목록을 생성해 쓰게 하는 자리가
        아직 없다 · 계약(`task/`)은 git 에 없어 새 체크아웃의 목록에는 없다. `docs/planning/progress.md` 「지금 상태」가 이 단위를 활성 단위로 가리킨다.
- **위험과 되돌리기:** 읽기 전용 명령 하나와 절차 1단계의 문단 하나를 더한다 — 기존 동작 변경 0, 운영·외부 상태 없음. 되돌리기는 `git revert <통합 커밋>` —
  하위 명령·검사·문단이 사라진다(charter 의 「하위 명령 제거」). 알려진 한계 셋 — ① 계약(`task/`)은 git 에 없어 **새 체크아웃**의 목록에는 없다(목록은 있는 것만 말한다) ·
  ② 「재개된다」는 세션의 관찰이지 검사기의 판정이 아니다 — 이 단위는 검토자 세션 1회로 잰다 · ③ 깨진 참조를 막지 않는다(경고까지만 · charter 의 위험 「드러내기가 차단으로 자라는 것」).
- **결정 필요:** 없음


## 변경 범위

아래 「바뀌는 파일·모듈」 줄이 작업 계약의 쓰기 상한(`allowed_paths`)이 된다 — 집행 자리는 `romeo/envelope.py` 의 `change_scope_paths` 다(K-66). 그 줄은 다음 문법으로 읽힌다. 경로는 **백틱**으로 적고, 항목은 `·` 나 줄바꿈 목록으로 나눈다. 설명은 **괄호 안**에 적는다 — 괄호 안의 백틱은 경로로 읽지 않는다. `/` 도 `.` 도 없는 토큰(함수명·플래그)과 공백이 든 토큰은 경로로 읽지 않는다 — 계약을 만들 때 그 목록이 인쇄된다. 루트의 확장자 없는 파일은 `./LICENSE` 처럼 쓴다. 「영향을 받는 부분」·「바꾸지 않는 것」 은 상한에 들어가지 않는다.

- 바뀌는 파일·모듈: `romeo/context.py`(신규) · `romeo/cli.py` · `tests/test_context_resume.py`(신규) · `core/workflows/plan/SKILL.md` · `docs/planning/open-questions.md` · `docs/planning/progress.md` · `docs/work/feat-20260907-context-one-hop-resume-w5jq/`
- 영향을 받는 부분: `/plan` 절차 1단계의 재개 경로 · `romeo --help` 의 하위 명령 목록(18개가 된다) · 문서 예시 대조 검사(`tests/test_doc_commands.py` 가 새 예시 `romeo context <id>` 를 파서와 대조한다)
- 바꾸지 않는 것(비범위): `romeo/find.py`·`romeo/card.py`(M1 그대로) · `romeo/close.py`·`romeo/evidence.py`·`romeo/envelope.py`·`romeo/run_unit.py`(판정·증거·계약은 손대지 않는다) · 어댑터 산출물·`.harness/compiled.yaml`(코어 SKILL 의 description 이 그대로라 compile 산출물이 바뀌지 않는다) · 구현자·검토자 브리프 정본(`adapters/orca/prompts/`) — 브리프가 이 목록을 생성해 쓰게 하는 것은 다음 단위 · `core/principles/PROJECT.core.md` 세션 시작 표 · `docs/current/`(charter M3) · `attempts.yaml` 형식 · 다른 열린 질문(Q-64·69·70·82·83·84 …)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**빈칸 금지** — `TBD`·`나중에`·"적절한 에러 처리 추가"·"위 내용의 테스트 작성"처럼 *무엇을* 없이 *하겠다*고만 쓴 칸은 **위 자리표시자와 같은 미완료 표시**로 취급한다. 승인 전에 채워야 한다. 이 안내 줄이 그 토큰을 글자 그대로 담으면 안내문 자체가 종료 검사(`NO_OPEN_LOOP`)에 걸리므로 여기서는 풀어 쓴다(Q-20). (출처: `sp-writing-plans-absorbed`)

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다. 단위가 하나뿐이면 `해당 없음` 으로 둔다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | `romeo context <id>` 가 1-hop 목록을 낸다 | `romeo/context.py` 신규 — `ROLES`(9개 역할, 인쇄 순서) · `UNIT_DOCS`(spec·brief·charter) · `SUBDIR_ROLES`(task→계약·evidence→증거·result→결과·review→검토) · `unit_context(project_root, unit_id)`: `docs.find_unit_dir` 로 폴더를 찾고(없으면 FileNotFoundError 그대로), 정본 중 첫 문서의 frontmatter 를 읽어 `parent`(charter 없으면 spec, 둘 다 없으면 charter 자리를 exists False 로)·`inputs`(단위 폴더 기준 상대 경로)·`attempts.yaml`·폴더 안 나머지 파일(`rglob`, 하위 디렉터리 이름으로 역할, 그 밖은 `기타`, `inputs/` 아래 미등록 파일은 그 사실을 note 에)을 모아 같은 경로는 한 번만 넣고 `(역할 순서, 정본 순서, 경로)` 로 정렬한다. note 는 파일에서 읽은 값만이고 파일이 깨지면 「읽을 수 없다」다. `format_context(res)` 는 헤더 2줄(`romeo context <id> — <title>` · `status … · 승인 … · 종료 … · parent … · 파일 N · 없음 K`) 뒤에 `[역할] 경로 — note` 줄, 없는 파일은 `[없음] 경로 — 역할 · note`. `romeo/cli.py`: `cmd_context`(`--json` 이면 `json.dumps(res)`, 아니면 `format_context`), `sub.add_parser("context", …)` 에 위치 인자 `unit`·`--root`·`--json`, 모듈 docstring 목록에 `context` 추가. `main` 의 기존 `FileNotFoundError` 처리가 `ERROR …` 한 줄·exit 1 을 낸다 — 새 예외 처리를 두지 않는다 | 소비: `romeo.docs.find_unit_dir` · `romeo.frontmatter.read` · `romeo.util.load_yaml`·`load_json` → 생산: `romeo.context.unit_context(project_root, unit_id) -> {"unit": {...}, "files": [{path, role, exists, note}], "missing": [path]}` · `romeo.context.format_context(res) -> str` · `romeo.context.ROLES` · CLI `romeo context <id> [--root ROOT] [--json]` | check-1~6 · check-8 | `romeo/context.py` 삭제 + `cli.py` 등록 되돌리기 |
| 2 | 절차 1단계가 재개할 때 이 목록을 읽는 범위로 지정한다(§11) | `core/workflows/plan/SKILL.md` 절차 1 의 「유일한 관문이 아니다.」 뒤, 2단계 앞에 문단 하나: 「**재개**를 제안하거나 고를 때는 `romeo context <id>` 가 인쇄한 목록 — 그 단위의 정본 문서·상위 문서·입력·회차·계약·증거·결과·검토 — 을 읽는 범위로 삼는다. 그 밖의 파일은 목록의 파일이 가리킬 때만 연다(K-31 · 1-hop). 목록의 `[없음]` 은 깨진 참조다 — 숨기지 않고 카드에 적는다.」 frontmatter `description:` 은 건드리지 않는다(어댑터 산출물이 그것만 반영한다). 도구명·모델명을 쓰지 않는다(C-C6) | 소비: 1 의 CLI → 생산: 없음 | check-7 · check-9 · check-11 | `git revert` |
| 3 | 판별 검사를 더한다 | 새 파일 `tests/test_context_resume.py` — 클래스 `TestContextCommand` 6건: `test_lists_every_file_in_the_unit_folder_with_a_role`(기준 단위 `feat-20260907-judge-revision-base-sha-pwt8` 의 폴더 안 파일 집합 ⊆ 목록 · 역할 어휘 · 첫 줄 spec · `inputs/probe-2026-09-07.patch` 는 「입력」 · review 는 「검토」 · task 는 있으면 「계약」 · missing 0 · 인쇄 3번째 줄이 spec) · `test_follows_parent_and_inputs_exactly_one_hop`(`feat-20260906-m3-close-foreign-repo-ik3u` — 부모 `init-20260904-attach-payload-manual-rreq` 의 charter 는 「상위」, 입력 `feat-20260904-m2-router-foreign-repo-ct5h/spec.md` 는 「입력」, 그 두 단위의 다른 파일은 0건, 그 단위들에 evidence 가 실재함을 함께 확인) · `test_unknown_unit_is_refused_with_exit_1_and_no_traceback` · `test_missing_reference_is_printed_not_hidden`(임시 루트, git 없음 — 없는 parent·없는 inputs 항목 2건이 `missing` 이고 `[없음]` 이 정확히 2줄 · exit 0 · 합성한 `task/`·등록 증거·미등록 증거·결과 봉투의 역할과 note) · `test_facts_come_from_the_files_not_from_judgment`(기준 단위의 회차 `1 fail`·`2 pass` · 검토 FAIL/PASS·findings 1 · 증거 등록됨·head 12자 · status done · 「추천」「다음 행동」 없음) · `test_every_unit_in_this_repo_resolves_without_a_missing_reference`(전수). 클래스 `TestProcedureNamesTheCommandThatListsTheUnit` 1건: 1단계 본문의 `romeo <이름>` 을 기준 단위 id 로 실제 실행해 `docs/work/<id>/spec.md` 가 stdout 에 있는 것이 하나 이상. 기존 검사는 한 줄도 고치지 않는다 | 소비: 1·2 → 생산: 검사 7건 | check-1~7 · check-10 | 해당 검사만 되돌린다 |
| 4 | 발견했으나 고치지 않은 것을 열고 상태를 갱신한다 | `docs/planning/open-questions.md` 에 새 행(Q-85~) — ① 재개 절차(구현자·검토자 브리프 정본 `adapters/orca/prompts/`·RUNBOOK §3.4/§3.7)가 `romeo context` 목록을 생성해 넘기는 자리가 없다(코디네이터가 손으로 넣는다 — 이 관통의 AC-8 이 그 모양) · ② 작업 계약 `task/` 는 `.gitignore` 라 새 체크아웃의 재개 목록에 계약이 없다(워커 트리에만 있다 — 계약을 재계산해 보여 줄지, 없음을 인쇄할지). `docs/planning/progress.md` 「지금 상태」의 활성 단위·다음 행동 줄을 이 단위로 갱신한다(예산 30줄·2KB) | 소비: 없음 → 생산: 없음 | check-12 와 검토자 읽기(AC-9) | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**검사 대상은 이 작업 단위의 산출물뿐이다.** 페이로드(하네스를 부착한 프로젝트) 작업 단위의 `required_checks` 에
**하네스 자신의 테스트**를 넣지 않는다 — `python3 -m unittest discover -s tests`(하네스 저장소의 테스트),
`bin/romeo` 의 자기 검사(`compile --check` · `validate` · `doctor` · `fixtures …`)가 그것이다.
넣으면 하네스가 깨진 동안 그 페이로드 단위가 닫히지 못한다. 그 단위의 산출물은 멀쩡한데 완료가 서지 않는 것이고,
그때 고쳐야 할 것은 그 단위가 아니라 하네스다 — 두 판정을 한 검사에 묶으면 어느 쪽이 깨졌는지 구분되지 않는다
(근거: `feat-20260829-license-field-46an` 의 check-5 가 이 형태였다).
하네스 저장소 **자신**을 대상으로 하는 작업 단위에서는 그 검사들이 정당하다 — 그때는 그것이 이 단위의 산출물이기 때문이다.

**종료 코드 자체가 조건이다.** 검사에 적는 것은 `id` 와 `command` 둘뿐이고, 그 명령의 종료 코드 0 이 통과다.
기대를 문장으로 따로 적는 자리는 두지 않는다 — 사람은 그것을 조건으로 쓰는데 기계는 판정에 쓰지 않으므로,
그 검사는 무엇을 확인하는지 적혀 있는 채로 아무것도 확인하지 않는 **빈 검사**가 된다(2026-08-31 실측으로 제거).
확인하고 싶은 조건이 있으면 그 조건을 **명령으로** 쓴다.
같은 이유로 옵션이 판정을 만드는 명령은 그 옵션까지 적는다 — 예: `bin/romeo doctor` 는 옵션 없이 쓰면 항상 exit 0 이라 빈 검사이고,
부착 검증(K-68)을 실제로 판정하게 하려면 `bin/romeo doctor --strict --scope repository` 로 쓴다(Q-21).

그래서 `|| true` 를 붙이지 않는다 — 종료 코드를 항상 0 으로 만들어 위반을 통과시킨다.
부정 조건은 `!` 로 쓴다: `! grep -q '<있으면 안 되는 것>' <파일>`.

**판별 검사와 회귀 방지 검사의 구분** — §11 은 「어느 쪽인지는 검증 계획에 적는다, 적지 않으면 전부 판별 검사로 본다」고 한다.
**판별 검사는 check-1~check-8 이고**, 승인 전에 기존 상태·가상 완료 상태 양쪽에서 실행해 각각 실패·통과를 보였다(아래 「승인 전 실측」).
check-9~check-12 는 **회귀 방지 검사**이므로 양쪽 실측 대상이 아니다 — 양쪽에서 통과하는 것이 그 검사의 정의다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -m unittest tests.test_context_resume.TestContextCommand.test_lists_every_file_in_the_unit_folder_with_a_role"
  - id: check-2
    command: "python3 -m unittest tests.test_context_resume.TestContextCommand.test_follows_parent_and_inputs_exactly_one_hop"
  - id: check-3
    command: "python3 -m unittest tests.test_context_resume.TestContextCommand.test_unknown_unit_is_refused_with_exit_1_and_no_traceback"
  - id: check-4
    command: "python3 -m unittest tests.test_context_resume.TestContextCommand.test_missing_reference_is_printed_not_hidden"
  - id: check-5
    command: "python3 -m unittest tests.test_context_resume.TestContextCommand.test_facts_come_from_the_files_not_from_judgment"
  - id: check-6
    command: "python3 -m unittest tests.test_context_resume.TestContextCommand.test_every_unit_in_this_repo_resolves_without_a_missing_reference"
  - id: check-7
    command: "python3 -m unittest tests.test_context_resume.TestProcedureNamesTheCommandThatListsTheUnit"
  - id: check-8
    command: "bin/romeo context feat-20260907-context-one-hop-resume-w5jq --json | grep -q 'docs/work/feat-20260907-context-one-hop-resume-w5jq/spec.md'"
  - id: check-9
    command: "python3 -m unittest tests.test_find_reuse tests.test_doc_commands"
  - id: check-10
    command: "python3 -m unittest discover -s tests -q"
  - id: check-11
    command: "bin/romeo compile --check"
  - id: check-12
    command: "bin/romeo validate"
```

**각 검사가 무엇을 보는가**

| id | 종류 | 무엇이 참이어야 통과인가 | 반례(그럴듯한 거짓 값) |
| --- | --- | --- | --- |
| check-1 | **판별** | 기준 단위의 폴더 안 파일이 전부 목록에 있고 역할이 어휘 안이며 spec 이 첫 줄이다 | 폴더를 `ls` 한 목록 — 하위 디렉터리를 내려가지 않아 evidence·review 가 빠지고, 등록된 입력이 「기타」로 찍힌다 |
| check-2 | **판별** | 부모의 charter 와 입력의 spec 은 있고, 그 두 단위의 다른 파일은 0건이다 | 부모 폴더 전체를 따라 들어간 목록 — 부모의 증거·회차가 섞여 1-hop 이 2-hop 이 된다. 반대로 parent 를 아예 따라가지 않으면 charter 가 없어 실패한다 |
| check-3 | **판별** | 없는 id 는 exit 1 · `ERROR` 한 줄 · Traceback 없음 | `find_unit_dir` 의 예외를 잡지 않은 채 스택 트레이스로 죽거나, 빈 목록을 exit 0 으로 내는 것 |
| check-4 | **판별** | git 없는 루트에서 exit 0 · 없는 참조 2건이 `[없음]` 2줄과 `missing` 에 · 계약·미등록 증거·결과의 역할과 note | 없는 참조를 목록에서 빼거나(숨김) exit 1 로 막는 것(차단) · git 을 요구하는 구현 |
| check-5 | **판별** | 회차·판정·findings 수·등록·head 가 파일의 값 그대로고 추천 낱말이 없다 | 회차 파일을 읽지 않고 파일 이름만 찍는 목록, 또는 「다음 행동: 재검토」 같은 판정을 덧붙인 목록 |
| check-6 | **판별** | 31개 단위 전부 exit 0 · 깨진 참조 0 | 특정 단위 형태(charter 없음·inputs 없음·result 없음)에서 예외로 죽는 구현 |
| check-7 | **판별** | 1단계 본문이 지정한 이름으로 실제 실행해 spec 경로가 나온다 | 절차에 `romeo find` 만 있는 지금 상태 — 폴더까지만 내므로 실패한다. 이름만 대조하면 이 단위 없이도 통과한다 |
| check-8 | **판별** | 이 단위 자신에게 명령을 돌린 JSON 에 자기 spec 경로가 있다 | 하위 명령이 없는 지금 상태 — argparse 가 exit 2 로 끝나 grep 이 실패한다 |
| check-9 | 회귀 방지 | M1 의 절차 검사(1단계 본문에서 `romeo find` 를 뽑아 실제 검색)와 문서 예시 대조가 문단 추가 뒤에도 통과한다 | — |
| check-10 | 회귀 방지 | 기존 검사가 하나도 깨지지 않는다 | — |
| check-11 | 회귀 방지 | 코어 SKILL 본문 변경이 컴파일 산출물과 어긋나지 않는다(description 만 반영) | — |
| check-12 | 회귀 방지 | 문서 스키마·링크·예산이 전부 통과한다(이 단위의 문서 포함) | — |

**재실행 시간** — check-10 이 약 160초(프로브 실측 161초 · 929건), check-6 이 약 1초(31개 단위 전수), 나머지는 각 1초 안팎이다. `romeo close` 의 재실행 상한 600초 안이다.

**승인 전 실측(2026-09-07)** — 판별 검사 열(check-1~8)을 두 상태에서 실행했다. 기존 상태(이 체크아웃 `496bff0`, 이 단위의 문서만 더한 트리):
**여덟 건 전부 exit 1**(check-1~7 은 검사 모듈 없음, check-8 은 하위 명령 없음). 가상 완료 상태(프로브 워크트리 `probe-context-one-hop` = `496bff0` + 구현 단위 1~3 을
이 spec 대로 적용한 미커밋 시제품): **여덟 건 전부 exit 0**, 회귀 검사 check-9 15건 OK · check-11 PASS · check-12 PASS · check-10 929건 OK(161초).
프로브에서 잡아 spec 에 반영한 것 둘 — `task/` 는 `.gitignore` 라 새 체크아웃에 없다(AC-4 의 합성 단위에서 「계약」을 본다 · Q 로 연다) ·
기준 단위의 증거는 둘 다 등록돼 있어 「미등록」은 합성 단위에서만 볼 수 있다. 시제품은 `inputs/probe-2026-09-07.patch`(4개 파일)로 넘긴다 —
구현자의 출발점이지 판정 게이트가 아니다(게이트는 위 검사 그대로).


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
