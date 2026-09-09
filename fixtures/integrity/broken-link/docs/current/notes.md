# 깨진 상대 링크를 담은 fixture

이 줄의 [없는 파일](../없는-파일.md) 은 실재하지 않는다 — `bin/romeo integrity` 가 인쇄해야 한다.

괄호 안에 무엇이 더 붙어도 같은 규칙이 판정한다 — 첫 공백 앞까지가 경로 후보다:
[제목이 붙은 없는 문서](없는-제목붙은.md "설명") · [공백만 붙은 없는 문서](없는-공백붙은.md ).

이 줄들은 대상이 아니다: [외부](https://example.com/x.md) · [메일](mailto:a@example.com) ·
[문서 안 앵커](#깨진-상대-링크를-담은-fixture) · [옆 문서](sibling.md) · [앵커가 붙은 옆 문서](sibling.md#절) ·
[제목이 붙은 옆 문서](sibling.md "설명") · [공백만 붙은 옆 문서](sibling.md ).
