# Codex 독립 리뷰 — M2

## 요약

Critical 0건, Important 9건, Minor 1건이다. 가장 큰 문제는 컴파일러가 저장소 밖을 쓸 수 있고, 채택 취소된 스킬을 남긴 채 `--check`를 PASS시키는 것이다.
라우터 단일 진입·네임스페이스·reviewer read-only·override는 현재 실행 강제가 아니라 서로 어긋난 문구에 머물러 있다.
현재 63개 테스트와 공식 check는 모두 PASS하지만, 마커·출처·부분 실패·CI 경로 반례가 그 PASS의 범위를 넘는다.

## 발견

### F-01 어댑터 경로가 저장소 밖 파일을 덮어써도 컴파일 검사가 PASS한다

- **심각도:** Important
- **위치:** `romeo/compile.py:188`, `romeo/compile.py:208`, `adapters/claude/adapter.yaml:5`
- **무엇이 잘못됐나:** `instructions_file`·`settings_file`·`skills_dir`를 `root` 아래로 제한하는 경계 검사가 없다. 임시 저장소의 Claude adapter에서 `settings_file: ../outside.json`으로 바꾸자 `compile_all`이 부모 디렉터리 파일을 permissions JSON으로 덮어썼고, 이어서 `check_compiled`는 findings `[]`로 PASS했다. 현재 커밋의 실제 adapter 경로는 저장소 안이지만, 잘못된 입력을 검사기가 거부하지 않는다.
- **왜 문제인가:** adapter 오타나 악의적인 변경 하나로 작업 공간 밖의 사용자 파일을 무승인 변경·삭제할 수 있다. 이는 implementer의 쓰기 범위를 작업 공간으로 제한한 K-66과 `.harness/bindings.yaml`의 역할 계약을 우회한다.
- **근거:** `plan_outputs`는 YAML 값을 그대로 경로 결합하고(188~200행), `compile_all`은 이를 바로 `write_text`/`rmtree` 대상으로 쓴다(208~219행). 실행한 임시 트리 반례 출력은 `outside_original_survives=False`, `outside_replaced_with_permissions_json=True`, `compile_check_findings=[]`였다.
- **제안:** 모든 입력·출력 경로를 `resolve()`한 뒤 저장소 루트에 `relative_to` 가능한지 쓰기 전에 일괄 검증하고, `..`·절대경로·루트 자체를 거부한다. 경계 실패 시 쓰기 0건을 보장하는 회귀 테스트를 추가한다.

### F-02 채택 취소된 스킬이 재컴파일 뒤에도 남고 고아 검사도 PASS한다

- **심각도:** Important
- **위치:** `romeo/compile.py:204`, `romeo/compile.py:221`, `romeo/compile.py:273`, `.harness/compiled.yaml:6`
- **무엇이 잘못됐나:** `compile_all`은 현재 산출물만 덮어쓰고 새 `compiled.yaml`로 이전 목록을 교체할 뿐, 이전에 생성했으나 이제 대상이 아닌 경로를 지우지 않는다. `check_compiled`는 새 state의 `recorded - current`만 보므로 이미 state에서 잊힌 경로를 찾지 못한다. state 파일 자체가 없어도 오류를 내지 않는다.
- **왜 문제인가:** 사용자가 G-M2에서 스킬을 deferred/rejected로 되돌려도 예전 `.claude/skills/**`·`.agents/skills/**`가 계속 discovery될 수 있다. K-60의 활성화 게이트와 K-69의 분리 가능성을 동시에 깨뜨린다.
- **근거:** 임시 트리에서 `sp-test-driven-development`를 `deferred`로 바꾸고 정상 재컴파일했다. 두 런타임의 옛 스킬은 모두 `exists=True`, 새 state에는 기록되지 않았고 `check_findings=[]`였다. 별도 반례에서 `.harness/compiled.yaml`을 삭제한 뒤에도 `missing_state_check_findings=[]`였다. 기존 테스트는 같은 입력으로 두 번 컴파일하는 idempotence만 본다(`tests/test_compile.py:90`).
- **제안:** 쓰기 전에 이전 state를 필수로 읽고 `previous - planned`를 안전한 생성 경로로 검증한 뒤 제거한다. state 누락·손상은 FAIL시키고, accepted→deferred 전환 및 adapter/local skill 삭제 회귀 테스트를 둔다.

### F-03 벤더 스킬을 직접 노출해 K-60 라우터 게이트와 K-64 네임스페이스를 구현하지 못했다

- **심각도:** Important
- **위치:** `docs/requirements/constraints.md:108`, `docs/requirements/constraints.md:112`, `romeo/compile.py:61`, `romeo/compile.py:196`, `vendor/obra-superpowers@b36e082/skills/test-driven-development/SKILL.md:2`
- **무엇이 잘못됐나:** 컴파일러는 `local_path`의 디렉터리 basename을 그대로 skill 이름으로 사용해 두 런타임에 원문을 복사한다. 따라서 실제 이름은 `test-driven-development`, `systematic-debugging`, `plan`처럼 무접두어이고 K-64의 `superpowers:*`·`romeo:*` 구분이 없다. 원문 description도 “Use when implementing any feature…” 같은 직접 선택 조건을 유지한다. 라우터가 profile에 따라 호출해야 할 `core/workflows/implement`·`review` 껍데기는 현재 HEAD에 없다.
- **왜 문제인가:** Claude의 공식 skill 문서는 description을 discovery와 skill 선택에 쓰며 언제 사용할지를 적으라고 한다. 따라서 일반 기능 구현·버그·리뷰 요청이 `/plan`을 거치기 전에 벤더 skill을 직접 선택할 수 있고, 같은 이름의 전역/프로젝트 skill과 충돌할 수 있다. managed block의 “라우터가 켤 때만”이라는 문장만으로 native discovery를 차단하는 기계적 장치는 없다.
- **근거:** [Claude 공식 Skill 저작 문서](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)는 name/description 메타데이터가 선로딩되고 description이 선택에 중요하다고 설명한다. 실제 산출물의 frontmatter도 원문과 같은 무접두어다. `core/workflows/{implement,review}/SKILL.md`는 `MISSING`, `docs/planning/progress.md:40`도 해당 역할 실행을 미착수로 기록한다.
- **제안:** 실행 껍데기와 K-68 fixture가 준비되기 전에는 벤더 skill을 native discovery 경로에 투영하지 않는다. 두 런타임이 허용하는 이름 문법으로 충돌 없는 물리 이름을 정하고, K-64의 논리 id(`superpowers:*`)와 runtime name의 매핑을 명시·검사한다.

### F-04 override와 역할 계약이 실행 강제가 아니며 원문 쓰기 경로도 더 남아 있다

- **심각도:** Important
- **위치:** `provenance/imports.yaml:144`, `provenance/imports.yaml:186`, `provenance/imports.yaml:214`, `.harness/bindings.yaml:29`, `romeo/compile.py:87`, `vendor/obra-superpowers@b36e082/skills/requesting-code-review/code-reviewer.md:33`, `vendor/obra-superpowers@b36e082/skills/receiving-code-review/SKILL.md:203`, `vendor/obra-superpowers@b36e082/skills/test-driven-development/SKILL.md:37`
- **무엇이 잘못됐나:** override 기록과 실제 적용이 맞지 않는다. `sp-requesting-code-review`는 adapters가 `general-purpose`를 치환한다고 적지만 컴파일러는 원문을 verbatim 복사해 literal이 남는다. `sp-using-git-worktrees`는 존재하지 않는 `adapters/orca/RUNBOOK.md`가 적용한다고 적는다. `sp-finishing-a-development-branch`는 `.claude/settings.json deny`라고 적지만 실제 규칙은 ask다. reviewer의 `codex -s read-only`도 launcher가 아니라 managed 표에 문자열로 인쇄될 뿐이며, progress는 역할 실행이 미착수라고 기록한다. 읽은 원문에는 등록하지 않은 충돌도 있다. reviewer prompt는 별도 revision이 필요하면 raw `git worktree add`를 실행하라고 하고(`code-reviewer.md:35`), receiving skill은 `gh api .../replies`로 외부 댓글을 쓰라고 하며(`SKILL.md:205`), TDD는 test-first가 아니면 코드를 삭제하라고 강제한다(`SKILL.md:37-44,244`). 이 경로들은 현재 bindings/local_overrides와 Claude ask 목록에 없다.
- **왜 문제인가:** reviewer가 raw worktree로 Git 메타데이터를 바꾸거나, Claude가 GitHub 외부 상태를 확인 없이 변경하거나, 미커밋 사용자 코드를 지울 수 있다. 반대로 read-only sandbox에서 reviewer prompt가 그대로 실패할 수도 있다. D-67~D-71, imports, bindings 중 어느 것이 실제 권한 원본인지 판정할 수 없어 역할 교체 parity도 달라진다.
- **근거:** `.harness/bindings.yaml:30`은 imports와 “짝”이라고 하지만 자동 대조가 없다. `tests/test_compile.py:212-217`은 지침 파일에 `orca worktree create`와 `read-only` 문자열이 있는지만 검사해 실제 치환·sandbox 거부·권한 prompt를 증명하지 않는다. 현재 `.claude/settings.json:3-18`에도 `gh api`나 코드 삭제 guard는 없다.
- **제안:** `.harness/bindings.yaml` 한 곳을 실행 override의 정본으로 정하고 imports는 binding key만 참조하게 한다. 각 override가 실제 존재하는 launcher/adapter/permission rule에 연결되는지 schema로 검사하고, reviewer write·raw worktree·GitHub write·삭제를 시도해 거부/승인 gate를 관찰하는 K-68 fixture를 추가한다.

### F-05 생성된 `/plan`·`/plan-close` 절차에 실제 CLI가 받지 않는 명령형이 있다

- **심각도:** Important
- **위치:** `core/workflows/plan/SKILL.md:40`, `adapters/claude/workflows/plan-close.md:3`, `adapters/codex/workflows/plan-close.md:3`, `romeo/cli.py:254`, `romeo/cli.py:305`
- **무엇이 잘못됐나:** core plan은 `romeo new --from <route 출력>`을 지시하지만 CLI에는 `--classification` 또는 `--proposal`만 있다. 양쪽 plan-close adapter는 `bin/romeo close <id>`를 지시하지만 CLI는 `--unit`을 필수로 받는다. 생성된 `.agents/skills/plan-close/SKILL.md:15`에도 잘못된 형태가 그대로 들어갔다.
- **왜 문제인가:** 에이전트가 문서 생성 또는 유일한 완료 판정 명령을 절차대로 실행하면 argparse 단계에서 멈춘다. 테스트·compile check가 PASS해도 실제 `/plan-close` 수직 흐름은 닫히지 않는다.
- **근거:** `bin/romeo close example-unit` 실행 결과 exit 2와 `the following arguments are required: --unit`; `bin/romeo new --from /tmp/nonexistent-route.yaml` 결과 exit 2와 `one of the arguments --classification --proposal is required`였다. 현재 테스트는 생성된 명령을 CLI parser에 넣지 않는다.
- **제안:** core와 두 adapter를 실제 parser 계약으로 통일하고, 생성된 SKILL.md에서 명령 예제를 추출해 `--help`/argparse smoke test를 실행한다.

### F-06 managed block 정규식이 중복·CRLF를 허용하고 코드펜스의 사용자 텍스트를 덮어쓴다

- **심각도:** Important
- **위치:** `romeo/compile.py:20`, `romeo/compile.py:35`, `tests/test_compile.py:33`
- **무엇이 잘못됐나:** 정규식은 줄 시작/끝과 마커 개수를 검증하지 않고 첫 블록 한 개만 치환한다. 동일한 Romeo 블록 두 개가 있는 파일은 `check_compiled`가 findings `[]`로 통과시켰다. 기존 블록이 CRLF이면 인식하지 못해 두 번째 블록을 붙였다. Markdown 코드펜스 안의 가짜 Romeo 마커도 실제 소유 블록으로 보고 그 안의 사용자 예시를 삭제했다. 중첩·미완성 마커를 거부하는 단계도 없다.
- **왜 문제인가:** 중복 블록에 과거/상충 규칙이 남아 런타임마다 다른 지시를 읽거나, 사용자가 마커 사용법을 문서화한 텍스트가 컴파일로 손실될 수 있다. D-70이 OpenWiki 부착 전에 요구한 마커 규약으로 쓰기에는 안전하지 않다.
- **근거:** 임시 반례 출력은 `duplicate_blocks=2`, `duplicate_check_findings=[]`, CRLF `before_start_markers=1`→`after_start_markers=2`, 코드펜스 `user_example_survives=False`였다. 기존 테스트는 정상 단일 블록·다른 owner 블록만 확인한다(`tests/test_compile.py:36-63`).
- **제안:** 전체 줄에 고정된 parser로 owner별 블록을 먼저 열거하고 Romeo 블록이 정확히 0개 또는 1개일 때만 처리한다. 중복·중첩·미완성은 쓰기 전에 FAIL시키고 LF/CRLF, 코드펜스, 마커 내부 `-->`, 여러 owner 조합을 fixture로 추가한다.

### F-07 vendor 검사는 고정 upstream이 아니라 같은 파일의 자체 기록만 신뢰한다

- **심각도:** Important
- **위치:** `romeo/provenance.py:37`, `romeo/provenance.py:49`, `provenance/imports.yaml:14`, `tests/test_provenance.py:33`
- **무엇이 잘못됐나:** `check_vendor`는 `source_sha`를 한 번도 사용하지 않고, 변경 가능한 `imports.yaml.files` 해시와 로컬 bytes만 비교한다. vendor 파일을 변조한 뒤 같은 PR에서 manifest blob SHA를 다시 계산하면 고정 `source_sha`를 그대로 둔 채 findings `[]`로 PASS했다. `is_file()`/`read_bytes()`만 보므로 파일 심링크, 실행 비트 변경, 추가 빈 디렉터리도 모두 PASS했다.
- **왜 문제인가:** CI의 “원문 수정 0”은 pinned commit과의 출처 검증이 아니라 두 로컬 파일의 자기일관성 검사다. 실수나 공급망 변조가 vendor와 manifest에 함께 들어오면 검출하지 못하고, 심링크는 외부 파일 의존과 Windows 이식성 문제를 되살린다.
- **근거:** 임시 반례에서 변조+manifest 재해시 후 `source_sha_unchanged=b36e082...`, `check_findings=[]`였다. 별도 반례에서도 `symlink_is_symlink=True`, `non_script_is_executable=True`, `extra_empty_dir_exists=True`, `check_findings=[]`였다. 다만 현재 15파일은 별도 `git clone --filter=blob:none --no-checkout` 후 `git rev-parse <sha>:<path>`로 대조해 upstream/manifest/local mismatch 0임을 확인했다.
- **제안:** gate/update 시 pinned commit을 fetch해 `git ls-tree`의 blob·mode·type과 대조한 증거를 남기고, CI에서도 해당 commit 또는 검증된 git bundle/lock evidence를 신뢰 원본으로 사용한다. vendor 내부 모든 심링크를 거부하고 mode·파일/디렉터리 종류까지 manifest에 포함한다.

### F-08 컴파일이 원자적이지 않고 settings 기대값도 출력 파일에서 다시 만든다

- **심각도:** Important
- **위치:** `romeo/compile.py:144`, `romeo/compile.py:164`, `romeo/compile.py:204`
- **무엇이 잘못됐나:** compiler는 일반 파일을 먼저 덮어쓰고 각 skill destination을 `rmtree`한 뒤 복사하며 state는 마지막에 쓴다. 중간 실패 시 롤백이 없다. source에 깨진 심링크 하나를 둔 임시 반례에서 `FileNotFoundError`가 났지만 `AGENTS.md`·`CLAUDE.md`·settings와 첫 skill 일부는 이미 쓰였고 state는 없었다. `_render_settings`는 현재 산출물 `.claude/settings.json`을 입력으로 다시 읽는다. JSON이 잘못되면 예외를 숨기고 빈 객체로 간주해 사용자 키를 덮어쓰며, 반대로 임의의 비소유 키 변경은 그 변경 자체를 기대값으로 삼아 `check_compiled` findings `[]`가 된다. `plan_outputs`가 순수한 원본→산출물 계산이 아니다.
- **왜 문제인가:** disk full·권한·깨진 source·잘못된 settings 같은 현실적인 실패 뒤 두 런타임이 서로 다른 세대의 규칙을 읽는다. check가 어느 세대가 정본인지 복구할 state도 없을 수 있다.
- **근거:** 부분 실패 반례 출력은 `AGENTS_written_before_failure=True`, `CLAUDE_written_before_failure=True`, `settings_written_before_failure=True`, `first_tree_partially_written=True`, `state_written=False`였다. mode 변경+settings 비소유 키 추가+source 빈 디렉터리 반례도 `check_findings=[]`였다.
- **제안:** 모든 source·경로·JSON을 먼저 검증하고 임시 staging 트리에 완성본을 만든 뒤 파일 단위 atomic replace를 수행한다. 기존 state/출력 backup과 rollback을 보장하고, settings는 하네스 소유 subtree를 별도 파일 또는 명시적 merge 계약으로 분리해 expected 계산이 현재 output에 순환 의존하지 않게 한다.

### F-09 CI path filter가 권한 가드·compiled state·루트 라이선스 단독 변경을 실행하지 않는다

- **심각도:** Important
- **위치:** `.github/workflows/harness.yml:7`, `.github/workflows/harness.yml:24`, `.claude/settings.json:1`, `.harness/compiled.yaml:1`, `LICENSE:2`
- **무엇이 잘못됐나:** push와 pull_request `paths`에 `.claude/settings.json`, `.harness/compiled.yaml`, 루트 `LICENSE`가 없다. 이 파일들만 변경한 커밋/PR은 workflow 자체가 시작되지 않는다. 또한 state가 없어도 compile check가 PASS하는 문제는 F-02와 결합된다.
- **왜 문제인가:** K-66 승인 guard를 지우거나 산출물 소유 목록을 삭제해도 CI가 보지 않으며, D-41의 Apache-2.0 라이선스도 조용히 바뀔 수 있다. generated output과 안전 계약을 CI가 강제한다는 설명과 맞지 않는다.
- **근거:** workflow의 두 path 목록은 8~23행과 25~40행에 고정돼 있고 세 경로가 없다. 현재 루트 LICENSE 자체는 `Apache License Version 2.0`, 202줄, SHA-256 `270832ec...`로 확인했지만 이를 검증하는 테스트는 없다.
- **제안:** 세 경로를 push/PR filter에 추가하고, 가능하면 제외 목록보다 관련 루트 전체에 대한 명시적 검사 트리거를 사용한다. root license 식별, state 필수성, settings guard 신선도를 독립 테스트로 둔다.

### F-10 진행 상태 요약이 같은 문서 내부와 README에서 서로 다르다

- **심각도:** Minor
- **위치:** `docs/planning/progress.md:20`, `docs/planning/progress.md:34`, `docs/planning/progress.md:35`, `docs/planning/progress.md:38`, `README.md:39`
- **무엇이 잘못됐나:** milestone 행은 M2의 남은 진입 조건을 LICENSE 교체라고 쓰지만 같은 문서 35행은 LICENSE 완료, 38행은 adapter compile 완료라고 쓴다. README 43행은 adapter 투영·역할 바인딩이 남았다고 하지만 progress 38행과 bindings는 완료로 표시한다. progress 34행은 “7종 14파일”이 아니라 “14개 스킬”이라고 쓴다.
- **왜 문제인가:** PM이 첫 상태 표나 README만 보면 이미 끝난 일과 미착수 일을 반대로 판단한다. 실행 상태와 문서 상태의 소유자를 분리하려는 K-63 운영에서 derived 상태 문서가 신뢰를 잃는다.
- **근거:** 파일의 상기 행을 직접 대조했다. 실제로 없는 M2 후반 산출물은 roles/envelopes/Orca/parity이고 progress 40행은 이를 미착수로 올바르게 적고 있다.
- **제안:** milestone/README를 체크리스트 35~40행의 현재 사실로 갱신하고 “완료된 기반 / 미착수 실행 검증”을 분리한다. 파일 수와 skill 수를 별도 필드로 표시한다.

## 확인했으나 문제 없음

- `python3 -m unittest discover -s tests -v`를 새로 실행해 63 tests, exit 0을 확인했다.
- `bin/romeo route --fixtures fixtures/requests --report`는 33/33(100%), gate 누락 의심 0, exit 0이었다.
- `bin/romeo fixtures check`, `bin/romeo validate`, `bin/romeo compile --check`, `bin/romeo vendor check`, `bin/romeo notices --check`는 모두 exit 0이었다.
- 현재 vendor 15파일은 [upstream 고정 커밋 `b36e082`](https://github.com/obra/superpowers/tree/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/skills)의 blob과 15/15 일치했고, 포함 LICENSE는 MIT였다.
- vendor 및 양 런타임 투영본의 현재 트리에 심링크·빈 디렉터리·case-fold 경로 충돌·CRLF는 0이었다. 실행 비트는 `find-polluter.sh`에만 있었고, 투영본은 실제 파일이었다.
- 채택 7종의 `SKILL.md` 전문과 `code-reviewer.md`를 읽었다. Markdown 상대 링크 3개를 검사해 깨진 링크 0이었고, deferred/rejected skill은 현재 양쪽 산출물에 없었다.
- D-69의 인터페이스 열과 빈칸 금지 규율은 `core/templates/tech-spec.md:52-62`에 반영돼 있었다.
- 현재 `AGENTS.md`와 `CLAUDE.md`의 Romeo managed block은 각각 한 개였고, 다른 owner의 managed block은 없었다.
- M2 전체는 완료로 선언되지 않았다. 계획상 roles/envelopes/implement-review wrapper/Orca runbook/parity/doctor/compact brief/project config는 현재 없고, `docs/planning/progress.md:40`도 후반 작업을 미착수로 적는다. 부재 자체는 완료 허위 주장으로 분류하지 않았다.

## 확인하지 못한 것

- Claude·Codex가 실제 세션에서 각 skill을 자동 선택하는지, router 지시가 description 선택을 이기는지, override 충돌에서 어느 문구를 따르는지는 실행하지 않았다. progress의 Claude discovery 관찰도 독립 재현하지 않았다.
- Codex/Claude reviewer 쓰기 거부, 역할 교체 parity, NDJSON/structured output, Orca Run·Task·worktree·ResultEnvelope 수직 관통은 현재 HEAD에 launcher/schema/runbook이 없어 검증할 수 없었다.
- Windows 실제 checkout에서의 동작은 실행하지 않았다. CRLF와 심링크 문제는 임시 트리/문자열 반례로만 재현했다.
- Claude permission matcher가 ask/deny 패턴을 실제 명령 변형별로 어떻게 적용하는지는 런타임 실행 없이 정적 설정만 확인했다.
- 선택하지 않은 upstream 스킬 7종의 전문 및 visual companion 런타임은 이번 vendor 범위에 없으므로 다시 읽거나 실행하지 않았다.
