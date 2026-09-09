# fixtures/integrity — `bin/romeo integrity` 의 판별 fixture

각 폴더는 **검사할 루트 하나**다. `bin/romeo integrity --root fixtures/integrity/<폴더>` 로 돌린다.
루트에 `romeo/`·`docs/current/enforcement.md` 가 없으므로 승격 대조는 성립하지 않고 건너뛴다 —
이 fixture 들이 겨누는 것은 링크와 id 중복 두 검사뿐이다. 대조 쪽의 판별은 `tests/test_integrity.py` 의
위조 사본이 본다.

| 폴더 | 무엇을 보이는가 | 기대 종료 코드 |
| --- | --- | --- |
| `broken-link/` | `docs/current/` 문서의 상대 링크가 없는 파일을 가리킨다 | 1 |
| `duplicate-id/` | 폴더 이름은 다르고 frontmatter `id` 만 같다 | 1 |
| `same-title/` | `id` 는 다르고 `title` 만 같다 — 제목으로 막지 않는다 | 0 |
