# AC-4 판별 검사의 양쪽 실측 — 3회차

`tests/test_integrity.py` 의 `Fixtures.test_broken_link_notations` 은 **판별 검사**다(§11) —
이 단위의 고침이 없으면 실패해야 한다. 그 성질을 두 상태에서 확인한 기록이다.
이 파일은 증거가 아니라 **메모**다 — 증거는 `evidence/run_748ddeba9896.yaml` 뿐이다(K-51).

## 무엇을 고쳤나

2회차의 `LINK_RE` 는 `\[[^\]]*\]\(([^)\s]+)\)` 였다 — 괄호 안에서 공백을 배제했으므로
`[없는 문서](missing.md "설명")` 과 `[없는 문서](missing.md )` 는 **링크로 보이지도 않았다**.
3회차는 괄호 안 내용을 통째로 잡고(`\[[^\]]*\]\(([^)]*)\)`), 그 다음 자리(`_link_target`)에서
AC-4 의 규칙 하나로 자른다 — 첫 공백 앞까지가 경로 후보, 그 후보에서 `#` 뒤를 잘라낸 것이 대상 경로.
표기를 하나씩 세어 더하지 않는다.

## 고치기 전 상태 — 실패

`romeo/integrity.py` 의 `LINK_RE`·`broken_links` 만 2회차 형태로 되돌린 사본에서 —
그 복원본이 `inputs/integrity-before-fix-3.py.txt` 이고, 사본을 만들어 돌리는 것이
`inputs/ac4-before-fix.sh` 다(fixture 와 검사는 3회차 그대로).
2회차 모듈은 커밋되지 않았어서 이력에서 꺼낼 수 없다 — 같은 한계를 Q-92 로 열어 두었다:

```
$ python3 -m unittest tests.test_integrity.Fixtures -v
test_broken_link_notations ... FAIL
AssertionError: '없는-제목붙은.md' not found in
  'romeo integrity …/before/fixtures/integrity/broken-link
     대조 건너뜀 — docs/current/enforcement.md 도 판정을 뽑을 코드도 이 루트에 없다
     BROKEN_LINK docs/current/notes.md → ../없는-파일.md
     위반 1건'
Ran 4 tests — FAILED (failures=1)
```

깨진 링크 셋 중 **하나만** 인쇄됐고 종료 코드는 그 하나 때문에만 1 이었다.
제목이 붙은 표기와 공백만 붙은 표기는 검사에서 통째로 빠졌다.

## 고친 뒤 — 통과

같은 검사를 이 작업 루트에서:

```
$ python3 -m unittest tests.test_integrity.Fixtures -v
test_broken_link ... ok
test_broken_link_notations ... ok
test_duplicate_unit_id ... ok
test_same_title_is_not_duplicate ... ok
Ran 4 tests — OK
```

`assertNotIn("sibling.md", out)` 이 같은 검사 안에 있다 — 같은 세 표기로 적힌 **실재하는** 대상은
잡히지 않는다. 통과만 보이는 빈 검사가 아니고, 실패만 보이는 통과 불가능한 검사도 아니다.
