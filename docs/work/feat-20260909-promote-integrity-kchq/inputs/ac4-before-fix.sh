#!/usr/bin/env bash
# AC-4 판별 검사의 「고치기 전」 쪽. 2회차 모듈로 되돌린 사본에서 새 판별 검사가 **실패**하는지 본다.
#
# 성공(exit 0) = 고치기 전 상태에서 검사가 실패했다 = 그 검사에 판별력이 있다.
# 이 스크립트가 exit 1 을 내면 검사가 두 상태에서 모두 통과한다는 뜻이고, 그것은 빈 검사다(§11).
#
# 2회차 모듈은 커밋되지 않았어서 `git show <SHA>:romeo/integrity.py` 로 꺼낼 수 없다(Q-92) —
# 이번 수정의 역연산으로 복원한 사본이 inputs/integrity-before-fix-3.py.txt 다.
set -u
root="$(cd "$(dirname "$0")/../../../.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

(cd "$root" && tar cf - --exclude=.git .) | (cd "$tmp" && tar xf -)
cp "$root/docs/work/feat-20260909-promote-integrity-kchq/inputs/integrity-before-fix-3.py.txt" \
   "$tmp/romeo/integrity.py"

cd "$tmp"
python3 -m unittest tests.test_integrity.Fixtures.test_broken_link_notations -v 2>&1 | tail -12
status="${PIPESTATUS[0]}"
if [ "$status" -eq 0 ]; then
  echo "판별력 없음 — 고치기 전 상태에서도 통과했다"
  exit 1
fi
echo "고치기 전 상태에서 실패했다 (exit $status) — 판별 검사다"
