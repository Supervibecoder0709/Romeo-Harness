---
id: feat-20260831-park-defects-actm
type: spec
title: park 된 하네스 결함 4건 정비 — 계약 경로 잘림·안내문 토큰·디렉터리 크래시·유령 시도
unit: T1
mode: delivery
intent: write
facets: [tooling, docs]
gates: []
profile: standard
blast_radius: medium
uncertainty: low
status: active
approved_at: '2026-09-01T00:34:17+09:00'
approved_by: Supervibecoder0709
base_sha: null
closed_at: null
parent: null
inputs: []
evidence: []
routing:
  policy_version: 0.1.0
  fired_rules: ['profile:base:T1=standard', 'overlay:profile.standard-or-deeper']
  history: []
created: '2026-08-31'
updated: '2026-09-01'
approval_history:
- {approved_at: '2026-08-31T23:05:01+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-08-31T23:45:04+09:00',
  reason: 'check-1\u00b7check-2 \uc758 \uba85\ub839 \ubb38\uc790\uc5f4\uc774 \ub77c\ubca8 \u300c\ubc14\uafc0\ub294
    \ud30c\uc77c\u00b7\ubaa8\ub4c8\u300d\uc758 ''\uafc0'' \ub97c \ub610 \ub2e4\ub978 \uae00\uc790\ub85c
    \uc801\uc5b4 \uc874\uc7ac\ud558\uc9c0 \uc54a\ub294 \ub77c\ubca8\uc744 \ucc3e\uac8c \ud588\ub2e4 \u2014
    \uc5b4\ub5a4 \uad6c\ud604\uc73c\ub85c\ub3c4 \ud1b5\uacfc\ud560 \uc218 \uc5c6\ub294 \uac80\uc0ac\uc600\ub2e4.
    \ud55c \uae00\uc790\ub97c \ubc14\ub85c\uc7a1\ub294\ub2e4. \uac80\uc0ac\uac00 \ubb3b\ub294 \uc870\uac74(\uc5ec\ub7ec
    \uc904\uc744 \uc804\ubd80 \uc77d\ub294\ub2e4 \u00b7 \ub2e4\uc74c \ud56d\ubaa9\uc744 \uc0bc\ud0a4\uc9c0
    \uc54a\ub294\ub2e4)\uc740 \uadf8\ub300\ub85c\uc774\uace0 \uac80\uc0ac\ub97c \uc57d\ud558\uac8c \ub9cc\ub4e4\uc9c0
    \uc54a\ub294\ub2e4. \uadfc\uac70: \uace0\uce5c check-1 \uc744 \uc2b9\uc778 \ucee4\ubc0b b996d71 \uc758
    \ub9ac\ube44\uc804(\uc774 \uccb4\ud06c\uc544\uc6c3)\uc5d0\uc11c \ub3cc\ub9ac\uba74 [''a/x.py'', ''a/y.py'']
    \ub9cc \ub098\uc640 AssertionError \ub85c \ub5a8\uc5b4\uc9c4\ub2e4 \u2014 \ub77c\ubca8\uc744 \ucc3e\uc544
    \uccab \uc904\ub9cc \uc77d\uc740 \uac83\uc774\ubbc0\ub85c \uac80\uc0ac\uac00 \uc2e4\uc81c\ub85c \ub3d9\uc791\ud55c\ub2e4.
    \ud655\uc778\ub780\uacfc \uc218\uc6a9 \uae30\uc900\uc740 \ubb34\ubcc0\uacbd'}
- {approved_at: '2026-08-31T23:45:04+09:00', approved_by: Supervibecoder0709, superseded_at: '2026-09-01T00:34:17+09:00',
  reason: '2회차(run_e5c7c10f80aa)가 드러낸 다섯 번째 하네스 결함을 범위에 넣는다. romeo/evidence.py:389 의 앵커 대조가 원시 로그의 첫 물리
    줄 하나만 기록된 명령 전체와 비교해, 개행을 담은 명령은 어떤 구현으로도 EVIDENCE_ANCHORED 를 통과할 수 없다 — 이 단위의 check-9 이 그것이고, close
    는 EVIDENCE_LOG·EVIDENCE_ANCHORED 두 항목을 level=error 로 FAIL 시키므로 봉투만 내고 넘어갈 수 없다(close.py:155-166·597
    실측). 바꾼 것: 확인란 무엇을에 ⑤ 추가 · 왜 지금에 2회차가 직접 걸렸다는 근거 추가 · AC-9 신설 · 위험에 위조 탐지 대조식을 건드린다는 세 번째 위험 추가 ·
    변경 범위에 romeo/evidence.py 와 tests/test_docs_evidence_close.py 추가 · 구현 단위 7행 추가 · check-15(회귀 테스트)와
    check-16(이 관통 자신의 증거 대조) 추가. AC-9 의 달성 가능성은 승인 전에 실측했다 — ''$ '' 뒤부터 ''--- stdout ---'' 앞까지를 명령 헤더로
    보면 check-9 이 통과하고(True) 로그를 한 글자 고치면 여전히 거부된다(True). check-15·check-16 은 미수정 코드에서 실제로 실패하는 것을 확인했다
    — 빈 검사가 아니다. AC-1~AC-8 과 구현 단위 1~6 은 무변경.'}
---

# park 된 하네스 결함 4건 정비 — 계약 경로 잘림·안내문 토큰·디렉터리 크래시·유령 시도

> 깊이 **Standard** · 단위 T1 · 모드 delivery · 의도 write · 영역 tooling, docs · 게이트 없음
> 승인 전에는 구현을 시작하지 않는다(D-27). 승인은 `romeo approve feat-20260831-park-defects-actm --by <승인자>` 로 기록한다.

## 확인란

사용자는 이 절만 읽고 승인한다. 기술 절은 검토자 런타임과 evidence가 책임진다.

- **무엇을:** park 된 하네스 결함 네 개와 이 단위가 스스로 드러낸 하나를 고치고, 하나는 서술이 사실과 달라 고칠 것이 없으므로 문서 정정으로 닫는다. 고치는 넷은 ① 작업 계약이 승인된 「바뀌는 파일·모듈」 선언을 **일부만 읽고 아무 말도 하지 않는 것**, ② spec 템플릿의 안내 문구가 종료 검사의 미완료 토큰과 같은 글자를 담아 **자기 검사에 걸리는 것**, ③ `romeo validate` 에 폴더를 주면 **파이썬 트레이스백이 그대로 올라오는 것**, ④ 반복 중단을 푸는 유일한 창구가 재검토를 기록하면서 **시도까지 함께 시작해** 유령 기록과 이중 base_sha 를 만드는 것, ⑤ 증거의 원시 로그 대조가 **여러 줄에 걸친 명령을 첫 줄만 보고** 다르다고 판정해 종료 검사를 통과할 수 없게 만드는 것이다. 정정하는 하나는 Q-21 이다.
- **왜 지금:** 넷 다 **지난 두 단위의 관통을 실제로 막았거나 손작업을 강요한 것**이고, 다음 관통에서 같은 자리에 다시 걸린다. ① 은 2026-08-31 `feat-20260831-bmad-attach-probe-tgnb` 1회차를 통째로 실패시켰고(선언한 9개 중 2개만 계약에 실렸다), ② 는 닫힌 단위들이 전부 손으로 안내 줄을 지워서 넘겼고, ④ 는 방금 끝난 단위의 시도 기록에 유령 세 개를 남겼다. ⑤ 는 **이 단위의 2회차 관통이 직접 걸린 것**이다 — 검사 14건이 전부 종료 코드 0 인데도 개행을 담은 check-9 하나 때문에 `close` 가 `EVIDENCE_LOG`·`EVIDENCE_ANCHORED` 두 항목에서 FAIL 을 내 단위가 닫히지 않았다. 여러 줄 명령을 쓴 검증 계획은 **어떤 구현으로도** 닫히지 않고, 그 사실이 close 단계에서야 드러난다. 그리고 코어 규칙 §10 이 관통 중 하네스 수정을 금지하므로, 고칠 수 있는 구간은 관통과 관통 **사이**인 지금뿐이다 — 다음 단위를 열면 그것이 끝날 때까지 다시 잠긴다.
- **기대 결과:** 다음 관통의 위임이 이 네 가지 이유로는 중단되지 않는다. 구현자가 「바뀌는 파일·모듈」을 한 줄에 억지로 밀어 넣지 않아도 되고, spec 을 쓴 사람이 템플릿 안내문을 지우는 것을 잊어도 종료 검사가 그 이유로 막지 않으며, 반복 중단을 풀 때 시도 기록에 유령이 생기지 않는다.
- **수용 기준:**
  - [ ] AC-1 「바뀌는 파일·모듈」을 **여러 줄에 걸쳐** 선언해도 선언한 경로가 **전부** 계약의 쓰기 상한에 실린다 — 4개를 두 줄에 나눠 적었을 때 4개가 다 읽힌다.
  - [ ] AC-2 그 이어 읽기가 **다음 항목까지 삼키지 않는다** — 「영향을 받는 부분」 줄에 적힌 경로는 쓰기 상한에 들어가지 않는다. (승인이 정하지 않은 경로를 계약에 적지 않는다, K-66)
  - [ ] AC-3 `core/templates/tech-spec.md` 의 **「빈칸 금지」 안내 문구가 그대로 남아 있으면서**, 그 줄이 종료 검사의 미완료 토큰과 같은 글자를 담지 않는다. (안내를 지워서 통과시키는 것은 이 기준을 만족하지 않는다)
  - [ ] AC-4 `bin/romeo validate` 에 작업 단위 **폴더**를 주면 파이썬 트레이스백이 아니라 그 폴더 안 문서들의 검사 결과가 나오고, 종료 코드가 0 이다.
  - [ ] AC-5 재검토 결론을 **기록만 하고 시도를 시작하지 않는 경로**가 있고, 그 경로를 쓰면 `attempts.yaml` 의 시도 항목 수가 늘지 않는다.
  - [ ] AC-6 고친 네 자리마다 **그 결함을 재현하는 회귀 테스트**가 `tests/` 에 있고 통과한다 — 지정한 이름으로 단독 실행했을 때 종료 코드 0.
  - [ ] AC-7 `docs/planning/open-questions.md` 의 Q-18·Q-20·Q-21·Q-22·Q-25 다섯 행이 모두 해소 표시를 달고 있고, Q-21 행은 **왜 고칠 것이 없었는지**(CI 스텝이 이미 존재했다는 실측 근거)와, 그 park 이 함께 지적했으나 여전히 참인 사실(작업 단위 `required_checks` 에 `bin/romeo doctor` 만 쓰면 빈 검사다)이 어디로 갔는지를 담는다.
  - [ ] AC-8 기존 검사가 회귀하지 않는다 — unittest 전체와 `compile --check`·`validate`·`doctor --strict --scope repository`·`fixtures parity --report` 가 모두 종료 코드 0.
  - [ ] AC-9 **여러 줄에 걸친 검사 명령**이 원시 로그 앵커 대조를 통과한다 — 이 관통 자신의 `check-9`(개행을 담은 명령) 증거 기록이 대조에서 통과로 판정되고, 그러면서도 **로그를 손으로 고치면 여전히 거부된다**. (위조 탐지를 약하게 만들어 통과시키는 것은 이 기준을 만족하지 않는다)
- **위험과 되돌리기:** 가장 큰 위험은 AC-1·AC-2 가 건드리는 자리가 **모든 위임의 입구**라는 것이다 — 계약 생성이 여기서 쓰기 상한을 계산하므로, 잘못 고치면 계약이 아예 만들어지지 않거나(관통이 서지 않는다) 승인이 정하지 않은 경로가 상한에 들어간다(K-66 위반). 그래서 AC-2 가 경계 조건을 음성으로 대조하고 AC-8 이 기존 검사 전체를 다시 돌린다. 두 번째 위험은 AC-5 가 **반복 중단 브레이크의 해제 경로**를 바꾼다는 것이다 — 새 경로가 브레이크를 우회하면 연속 실패가 자동으로 풀린다. 세 번째 위험은 AC-9 가 **증거 위조 탐지의 대조식**을 건드린다는 것이다 — 느슨하게 고치면 로그를 고쳐도 통과한다. 그래서 회귀 테스트가 여러 줄 명령의 통과와 손으로 고친 로그의 **거부**를 함께 확인하고(check-15), check-16 이 이 관통 자신의 증거로 다시 대조한다. 원시 로그의 형식은 바꾸지 않는다 — 이미 봉인된 로그들이 그대로 대조돼야 한다. 전부 이 저장소 안의 로컬 변경이고 외부 상태를 바꾸지 않으므로 되돌리기는 `git revert <커밋>` 한 번이다. 워크트리에서 작업하므로 통합 전에는 브랜치가 그대로 남는다.
- **결정 필요:** 없음 — 범위 두 건은 라우터 확정 단계에서 정해졌다. Q-21 은 코드 수정 대상에서 빼고 문서 정정으로 닫는다. `feat-20260830-harness-defects-w3qu`(4회 연속 실패 park)는 재개하지 않고, AC-1 수정이 그 단위 AC-2 의 전제를 무효화한다는 사실만 기록한다.


## 변경 범위

- 바뀌는 파일·모듈: `romeo/envelope.py` · `romeo/validate.py` · `romeo/cli.py` · `romeo/run_unit.py` · `romeo/evidence.py` · `core/templates/tech-spec.md` · `tests/test_envelope.py` · `tests/test_run_unit.py` · `tests/test_docs_evidence_close.py` · `docs/planning/open-questions.md`
- 영향을 받는 부분: 작업 계약 생성(모든 위임의 입구) · 종료 검사의 미완료 토큰 판정 · 반복 중단 브레이크의 해제 경로 · 증거 위조 탐지의 명령 대조. 컴파일 산출물은 바뀌지 않는다 — `core/principles/` 를 건드리지 않기 때문이다.
- 바꾸지 않는 것(비범위): `core/principles/` 의 코어 규칙 · `.github/workflows/harness.yml`(Q-21 이 요구하던 스텝은 이미 있다) · `feat-20260830-harness-defects-w3qu` 단위의 문서와 브랜치 · Q-12~Q-17·Q-19·Q-23·Q-24 의 park · 원격 푸시(별도 승인 대상, K-66)

## 구현 단위

각 행은 **혼자서 검증할 수 있는 최소 단위**다. 앞뒤 행을 함께 봐야만 확인이 되면 한 행으로 합친다.

**인터페이스** 열은 앞 단위가 만든 이름·타입을 뒤 단위가 알게 하는 칸이다. 구현자가 자기 행만 보고 작업해도 이름이 어긋나지 않게 한다.

| # | 목표 | 변경 | 인터페이스 (소비 → 생산) | 확인 방법 | 복구 |
| --- | --- | --- | --- | --- | --- |
| 1 | 「바뀌는 파일·모듈」 선언을 여러 줄까지 이어 읽되 다음 항목은 삼키지 않는다 (AC-1·AC-2) | `romeo/envelope.py` 의 `change_scope_paths` — 라벨이 있는 줄에서 즉시 `return` 하는 대신, 다음 목록 항목(`- ` 로 시작하는 줄)이나 다음 절 제목(`## `)이 나올 때까지 이어 읽는다 | 소비: 없음 → 생산: `change_scope_paths(body)` 가 여러 줄 선언을 전부 반환 | check-1·check-2 | `git revert` |
| 2 | 안내 문구가 종료 검사에 걸리지 않게 한다 (AC-3) | `core/templates/tech-spec.md` 의 「빈칸 금지」 줄 — 미완료 토큰을 글자 그대로 쓰지 않고 검사에 걸리지 않는 표기로 바꾼다(안내 자체는 남긴다) | 소비: 없음 → 생산: 템플릿이 만든 문서가 안내문 때문에 `NO_OPEN_LOOP` 에 걸리지 않는다 | check-3 | `git revert` |
| 3 | `validate` 에 폴더를 줄 수 있게 한다 (AC-4) | `romeo/cli.py` 의 `cmd_validate` 또는 `romeo/validate.py` — 인자가 디렉터리면 그 아래 문서를 찾아 검사한다(`find_docs` 재사용) | 소비: 없음 → 생산: `bin/romeo validate <폴더>` 가 정상 종료 | check-4·check-5 | `git revert` |
| 4 | 재검토를 기록만 하는 경로를 만든다 (AC-5) | `romeo/run_unit.py` 와 `romeo/cli.py` — `run-unit` 의 action 에 재검토 기록 전용 값을 더하고, 그 경로에서는 `start_attempt` 를 부르지 않으며 `--run` 을 요구하지 않는다 | 소비: 없음 → 생산: 재검토만 기록하는 CLI 경로 | check-6 | `git revert` |
| 5 | 네 자리에 회귀 테스트를 붙인다 (AC-6) | `tests/test_envelope.py` 에 `TestChangeScopeMultiline`, `tests/test_run_unit.py` 에 `TestReviewOnlyRecord` 를 더한다. 나머지 둘은 check-3·check-4 가 명령으로 직접 확인한다 | 소비: 1·4 행의 산출물 → 생산: 지정한 이름의 테스트 클래스 | check-7·check-8 | `git revert` |
| 6 | park 다섯 건을 문서에서 닫는다 (AC-7) | `docs/planning/open-questions.md` — Q-18·Q-20·Q-22·Q-25 는 고쳤음을, Q-21 은 서술된 결함이 이미 존재하지 않았음을 근거와 함께 표시한다. Q-21 이 함께 지적한 '빈 검사' 사실은 남긴다 | 소비: 1~4 행의 결과 → 생산: 해소 표시된 다섯 행 | check-9 | `git revert` |
| 7 | 여러 줄 명령이 원시 로그 앵커를 통과하게 한다 (AC-9) | `romeo/evidence.py` 의 `command_log_state` — 로그의 **첫 물리 줄**이 아니라 `$ ` 뒤부터 `--- stdout ---` 표지 앞까지의 **명령 헤더 전체**를 기록된 명령과 비교한다. 로그를 쓰는 형식(`$ {command}`)은 바꾸지 않는다. `tests/test_docs_evidence_close.py` 에 `TestMultilineCommandAnchor` 를 더해 **여러 줄 명령이 통과하는 것**과 **로그를 고치면 거부되는 것**을 함께 확인한다 | 소비: 없음 → 생산: 여러 줄 명령의 앵커 대조 | check-15·check-16 | `git revert` |

## 검증 계획

required_checks — `romeo close` 가 evidence 의 commands·exit_codes 와 대조한다.

**이 단위는 하네스 저장소 자신을 대상으로 한다** — 그래서 `unittest`·`compile --check`·`validate`·`doctor`·`fixtures` 가 이 단위의 산출물이고, 페이로드 단위에 금지된 형태가 여기서는 정당하다.

**종료 코드 자체가 조건이다.** 확인하고 싶은 조건은 문장이 아니라 명령으로 쓴다. `|| true` 를 붙이지 않는다 — 종료 코드를 항상 0 으로 만들어 위반을 통과시킨다. 부정 조건은 `!` 로 쓴다.

```yaml
required_checks:
  - id: check-1
    command: "python3 -c \"from romeo.envelope import change_scope_paths as f; b='## \\ubcc0\\uacbd \\ubc94\\uc704\\n\\n- \\ubc14\\ub00c\\ub294 \\ud30c\\uc77c\\u00b7\\ubaa8\\ub4c8: \\u0060a/x.py\\u0060 \\u00b7 \\u0060a/y.py\\u0060\\n  \\u00b7 \\u0060a/z.py\\u0060 \\u00b7 \\u0060b/w.md\\u0060\\n'; got=f(b); assert got==['a/x.py','a/y.py','a/z.py','b/w.md'], got\""
  - id: check-2
    command: "python3 -c \"from romeo.envelope import change_scope_paths as f; b='## \\ubcc0\\uacbd \\ubc94\\uc704\\n\\n- \\ubc14\\ub00c\\ub294 \\ud30c\\uc77c\\u00b7\\ubaa8\\ub4c8: \\u0060a/x.py\\u0060\\n- \\uc601\\ud5a5\\uc744 \\ubc1b\\ub294 \\ubd80\\ubd84: \\u0060c/other.py\\u0060\\n'; got=f(b); assert got==['a/x.py'], got\""
  - id: check-3
    command: "python3 -c \"t=open('core/templates/tech-spec.md',encoding='utf-8').read().split(chr(10)); g=[l for l in t if '\\ube48\\uce78 \\uae08\\uc9c0' in l]; assert len(g)==1, g; assert 'NEEDS_'+'INPUT' not in g[0], g[0]\""
  - id: check-4
    command: "bin/romeo validate docs/work/feat-20260831-park-defects-actm"
  - id: check-5
    command: "! bin/romeo validate docs/work/feat-20260831-park-defects-actm 2>&1 | grep -q Traceback"
  - id: check-6
    command: "python3 -m unittest tests.test_run_unit.TestReviewOnlyRecord -v"
  - id: check-7
    command: "python3 -m unittest tests.test_envelope.TestChangeScopeMultiline -v"
  - id: check-8
    command: "python3 -m unittest tests.test_run_unit tests.test_envelope -v"
  - id: check-9
    command: "python3 -c \"t=open('docs/planning/open-questions.md',encoding='utf-8').read().split(chr(10));\nimport sys\nfor q in ('Q-18','Q-20','Q-21','Q-22','Q-25'):\n    r=[l for l in t if l.startswith('| '+q+' ')]\n    assert len(r)==1, (q,len(r))\n    assert ('\\ud574\\uc18c' in r[0]) or ('\\ub2f5\\ubcc0\\ub428' in r[0]), q\""
  - id: check-10
    command: "python3 -m unittest discover -s tests"
  - id: check-11
    command: "bin/romeo compile --check"
  - id: check-12
    command: "bin/romeo validate"
  - id: check-13
    command: "bin/romeo doctor --strict --scope repository"
  - id: check-14
    command: "bin/romeo fixtures parity --report"
  - id: check-15
    command: "python3 -m unittest tests.test_docs_evidence_close.TestMultilineCommandAnchor -v"
  - id: check-16
    command: "python3 -c \"import glob,pathlib,yaml; from romeo.evidence import command_log_state; rs=[c for f in sorted(glob.glob('docs/work/feat-20260831-park-defects-actm/evidence/*.yaml')) for c in (yaml.safe_load(open(f,encoding='utf-8')) or {}).get('commands',[]) if c.get('id')=='check-9']; assert rs, 'check-9 \\uae30\\ub85d\\uc774 \\uc5c6\\ub2e4'; st,why=command_log_state(pathlib.Path('.'), rs[-1]); assert st is True, why\""
```


## 증거

close 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).

- (없음)
