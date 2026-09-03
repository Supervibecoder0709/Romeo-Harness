#!/usr/bin/env bash
# AC-7 양쪽 실측의 '고치기 전' 쪽. 승인 base 커밋의 트리를 임시 디렉터리에 펼치고,
# **이 단위가 만든 검사 파일만** 얹어 돌린다 — 그 트리에서 판별 검사가 실패하는 것을 보인다.
# 통과하면 그것은 판별 검사가 아니므로 이 스크립트가 exit 1 로 끝난다.
# 작업 트리를 바꾸지 않고 재실행할 수 있다(§7 재실행 조건).
set -eu
BASE="${1:-a8bb36169576958a5be33a9decb84190a963547e}"
WANT="${2:-FAILED (failures=4)}"
d=$(mktemp -d)
git archive "$BASE" | tar -x -C "$d"
# 펼친 트리를 git 저장소로 만든다 — `project_root` 가 git 최상위로 루트를 잡으므로
# 이것이 없으면 검사가 정책표를 못 찾아 다른 이유로 실패한다(원인이 아닌 실패는 실측이 아니다).
git init -q "$d"
cp tests/test_guard_guidance_alignment.py "$d/tests/"
cd "$d"
if out=$(python3 -m unittest tests.test_guard_guidance_alignment 2>&1); then
  echo "$out"
  echo "base 트리($BASE)에서 통과했다 — 판별 검사가 아니다"
  exit 1
fi
echo "$out"
echo "$out" | grep -qF "$WANT"
echo "base 트리($BASE)에서 판별 검사가 실패한다 — 기대: $WANT"
