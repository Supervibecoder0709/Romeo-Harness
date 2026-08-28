# 작업 결과 — F-08 원자적 compile · F-07 upstream 고정 커밋 대조

## 바꾼 파일

- `romeo/compile.py`
  - 모든 소스·기존 settings JSON·출력 경로를 실제 산출물 쓰기 전에 검증한다.
  - 완성본과 rollback 사본을 저장소와 같은 파일시스템의 staging 디렉터리에 만든 뒤 `os.replace`로 반영한다.
  - 파일·skill tree·prune·compiled state 반영 중 예외가 나면 역순으로 원래 상태를 복구한다.
  - settings 기대값을 어댑터의 `permissions.ask`·`permissions.deny`만으로 계산하고, 컴파일할 때 사용자 키를 보존 병합한다.
  - `check_compiled`는 하네스 소유 settings 두 키만 비교한다.
- `romeo/provenance.py`
  - GitHub Git Trees API 응답 조회, 오프라인 파싱, manifest blob/mode 대조를 분리했다.
  - 네트워크 실패·HTTP/rate-limit·잘린 tree·잘못된 응답을 PASS로 취급하지 않는다.
  - 결과를 `provenance/upstream-verification.json`에 원자적으로 기록한다.
- `romeo/cli.py`
  - 네트워크 없는 기존 `romeo vendor check`와 별도로 `romeo vendor verify-upstream` 동작을 추가했다.
- `tests/test_compile.py`
  - F-08 회귀 테스트 5개와 산출물 스냅샷 helper를 추가했다. 기존 테스트의 기대값은 바꾸지 않았다.
- `tests/test_upstream_provenance.py`
  - F-07 오프라인 회귀 테스트 7개를 새로 추가했다.
- `provenance/upstream-verification.json`
  - 2026-08-28 실제 수동 upstream 대조의 경로별 blob/mode 증거다.
- `WORK_RESULT.md`
  - 이 작업의 변경·검증·미검증 기록이다.

`vendor/**`, `docs/**`, `README.md`, `progress.md`는 수정하지 않았다.

## 새 테스트가 증명하는 것

### F-08

- settings의 사용자 소유 키와 JSON 서식이 바뀌어도 `check_compiled`는 이를 stale로 오인하지 않는다.
- 같은 파일에서 하네스 소유 `permissions.ask` 또는 `permissions.deny`가 훼손되면 사용자 키 변경으로 가려지지 않고 stale로 검출된다.
- 재컴파일은 사용자 소유 settings 키를 보존하면서 하네스 소유 키만 복구한다.
- 깨진 source 심링크와 잘못된 기존 settings JSON은 기존 산출물을 한 건도 바꾸기 전에 거부된다.
- 세 번째 `os.replace`에서 `PermissionError`를 주입하면 앞서 교체된 파일도 원래 바이트·mode로 rollback되고 staging 잔여물이 남지 않는다.
- 저장소 내부를 가리키더라도 절대 출력 경로는 staging 우회를 막기 위해 쓰기 전에 거부된다.

### F-07

- 완전한 GitHub recursive tree 응답은 path별 `sha`·`mode`·`type`으로 파싱된다.
- `truncated: true` 응답은 완전한 tree로 오인하지 않고 실패한다.
- manifest의 blob SHA와 mode가 모두 맞아야 PASS이며, 각각의 불일치를 별도 finding으로 낸다.
- 성공 증거에는 확인 시각, 저장소, 고정 commit, 비교한 모든 경로, 기대값·실제값, 결과가 저장된다.
- fetch 실패는 `ERROR`/`UNVERIFIED` 증거를 남기고 예외로 종료된다.
- `romeo vendor verify-upstream` CLI가 별도 동작으로 연결되며, 단위 테스트는 고정 샘플만 사용해 네트워크 없이 돈다.

## TDD 실행 기록

- 변경 전 기준: `python3 -m unittest discover -s tests` → `Ran 95 tests`, `OK`, exit 0.
- F-08 RED: 새 테스트 4개 → `FAILED (failures=4)`, exit 1.
- F-08 GREEN: 같은 테스트 4개 → `Ran 4 tests`, `OK`, exit 0.
- F-07 RED: 새 테스트 7개 → `FAILED (failures=7)`, exit 1.
- F-07 GREEN: 같은 테스트 7개 → `Ran 7 tests`, `OK`, exit 0.
- 절대경로 RED: 새 테스트 1개가 실제 staging 우회 쓰기를 검출해 `FAILED (failures=1)`, exit 1.
- 절대경로 GREEN 및 compile 전체: `Ran 1 test`, `OK`; 이어서 `Ran 36 tests`, `OK`, exit 0.

## 실제 upstream 수동 대조

명령:

```text
bin/romeo vendor verify-upstream
```

출력:

```text
upstream 검증 PASS · vendors=1 files=15 findings=0 · commits=obra/superpowers@b36e0829c6d0140e93cfef2ca599b1b07d4a7797 · evidence=provenance/upstream-verification.json
exit_code=0
```

## 최종 검증

명령:

```text
python3 -m unittest discover -s tests
```

출력:

```text
...........................................................................................................
----------------------------------------------------------------------
Ran 107 tests in 16.085s

OK
exit_code=0
```

명령:

```text
bin/romeo compile --check
```

출력:

```text
compile 검사 PASS
exit_code=0
```

명령:

```text
bin/romeo vendor check
```

출력:

```text
vendor 검증 PASS · vendors=1 files=15 (수정 0 대조) · provenance id 를 쓴 코어 파일 1개
exit_code=0
```

명령:

```text
bin/romeo doctor --strict --scope repository
```

출력:

```text
# romeo doctor

## 런타임
  ✓ claude  2.1.248 (Claude Code)  — 구현자 런타임 (D-68)
  ✓ codex   codex-cli 0.147.0  — 검토자 런타임 (D-68)
  ✓ orca    orca  — worktree·위임 (전역 Orca 우선 규칙)
  ✓ gh      gh version 2.86.0 (2026-01-21)  — PR·CI 조회
  ✓ git     git version 2.39.5 (Apple Git-154)  — 증거 신선도 계산

## 스킬 파일 (파일 수준. 실제 로드는 이 검사로 증명되지 않는다)
  claude  9개 · .claude/skills · 런타임 로드 관찰됨 (2026-08-28 · romeo compile 직후 같은 세션의 스킬 목록에 채택 7종 (test-driven-development · systematic-debugging · verification-before-completion · requesting-code-review · receiving-code-review · using-git-worktrees · finishing-a-development-branch) + plan · plan-close 가 모두 나타났다. 보류·제외한 스킬(brainstorming · subagent-driven-development 등)은 나타나지 않았다.)
  codex   10개 · .agents/skills · 런타임 로드 관찰됨 (2026-08-28 · 별도 워크트리(codex-m2-review)의 독립 Codex 세션(gpt-5.6-sol, effort max)에게 "런타임이 실제로 제공한 스킬 목록" 을 물어 받은 답. .agents/skills/ 의 10개가 전부 나타났다 — finishing-a-development-branch · plan · plan-close · receiving-code-review · repo-archive · requesting-code-review · systematic-debugging · test-driven-development · using-git-worktrees · verification-before-completion. romeo doctor 가 센 목록과 이름까지 일치한다. 증거: docs/reviews/2026-08-28-codex-m2-review/SKILLS_SEEN.md)

## 부착 상태
  ✓ 컴파일 산출물: 일치
  ✓ vendor 원문·출처: 일치
  ✓ 제3자 고지: 일치

## 충돌 fixture (4종 실행)
  ✓ 충돌 0

결과 · 저장소: PASS · 이 머신의 런타임: PASS
exit_code=0
```

## 여전히 미검증인 것

- Python 예외로 관찰되는 반영 실패는 rollback 테스트로 검증했지만, 프로세스 강제 종료·전원 손실처럼 rollback 코드 자체가 실행되지 않는 crash recovery는 검증하지 않았다. 개별 파일 교체는 원자적이지만 여러 파일 전체를 하나의 OS 트랜잭션으로 만드는 것은 아니다.
- 실제 GitHub 정상 응답은 수동 확인했지만, 실제 rate limit이나 네트워크 단절을 의도적으로 발생시키지는 않았다. 해당 분기는 네트워크 없는 고정 실패 주입으로만 검증했다.
- 테스트와 수동 실행은 현재 macOS 및 현재 등록된 vendor 1개를 대상으로 했다. Windows 파일시스템과 복수 vendor 환경의 실동작은 미검증이다.
- push는 실행하지 않았다.

WORK_DONE
