#!/usr/bin/env bash
# close 가 이 관통에서 **추가로 요구한 것**을 지금 다시 인쇄한다 (AC-5 · D-80).
#
# 대상 저장소의 단위는 이미 `status: done` 이라 그 상태를 되돌리지 않고는 같은 출력을 낼 수 없다.
# 닫힌 단위를 다시 열지 않으므로, 단위 폴더와 그 원시 로그를 **임시 루트로 복사해** 그 요구가
# 아직 충족되지 않은 상태를 재구성하고 거기에 close 를 건다. 과거 출력을 손으로 옮겨 적지 않는다(K-51).
#
#   사용법: reproduce-close-demands.sh <before-evidence|after-round3|met> [대상 루트]
#   종료 코드: 기대한 대로 인쇄되면 0, 아니면 1.
#
# `met` 은 이 재현의 **반례**다. 요구를 아무것도 되돌리지 않은 루트에서는 같은 검사 이름이
# FAIL 로 인쇄되지 **않아야** 한다 — 그것이 참일 때만 앞의 둘이 「요구를 되돌렸기 때문에」 FAIL 이다.
# 반례가 빈 루트가 아니라 **요구가 전부 충족된 그럴듯한 루트**인 이유는 Romeo §11 이다.
#
# 임시 루트는 mktemp -d 아래에 만들고 끝나면 지운다 — 이 저장소의 작업 트리도 대상 저장소도 바꾸지 않는다.
set -u

STATE="${1:-}"
TARGET="${2:-$HOME/orca/workspaces/My-Automated-Worker/instagram-dm-sender}"
UNIT="feat-20260904-claude-md-rule-conflicts-bbn8"
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

case "$STATE" in
  before-evidence|after-round3|met) ;;
  *) echo "usage: $(basename "$0") <before-evidence|after-round3|met> [대상 루트]" >&2; exit 2 ;;
esac
[ -d "$TARGET/docs/work/$UNIT" ] || { echo "대상 단위 폴더가 없다: $TARGET/docs/work/$UNIT" >&2; exit 2; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/docs/work" "$TMP/.harness/runs"
cp -R "$TARGET/docs/work/$UNIT" "$TMP/docs/work/"
[ -d "$TARGET/.harness/runs/$UNIT" ] && cp -R "$TARGET/.harness/runs/$UNIT" "$TMP/.harness/runs/"
U="$TMP/docs/work/$UNIT"

# ── 그 요구가 아직 충족되지 않은 상태로 되돌린다 ────────────────────────────────
if [ "$STATE" = "met" ]; then
  # 아무것도 되돌리지 않는다 — 요구는 전부 충족된 채다.
  EXPECT=()
  FORBID=("HAS_EVIDENCE" "AC_ALL_CHECKED" "REVIEW_VERDICT")
elif [ "$STATE" = "before-evidence" ]; then
  # 시나리오 11 이 끝난 시점 — 폴더에 brief.md·spec.md 둘뿐이고 증거가 0건이다.
  rm -rf "$U/evidence" "$U/result" "$U/review" "$U/task" "$TMP/.harness"
  EXPECT=("HAS_EVIDENCE"); FORBID=()
else
  # 3회차 뒤 — 증거 3건·검토자 판정 3건(FAIL 2·PASS 1)이 있고 확인란은 아직 미체크다.
  rm -f "$U/review/run_bbn8m3r4d80-reviewer.json" "$U/evidence/run_bbn8m3r4d80.yaml" \
        "$U/result/run_bbn8m3r4d80-implementer.json" "$U"/task/run_bbn8m3r4d80-*.json
  rm -rf "$TMP/.harness/runs/$UNIT/run_bbn8m3r4d80"
  EXPECT=("AC_ALL_CHECKED" "REVIEW_VERDICT"); FORBID=()
fi

python3 - "$U/spec.md" "$STATE" <<'PY'
import re, sys
path, state = sys.argv[1], sys.argv[2]
t = open(path).read()
t = t.replace("status: done", "status: active", 1)
t = re.sub(r"^closed_at: .*$", "closed_at: null", t, count=1, flags=re.M)
# 「## 증거」 절의 링크와 frontmatter 의 evidence: 목록은 **close 가 통과한 뒤에** 채운 자리다.
# close 전 상태를 재구성하므로 둘 다 승인 시점의 값(빈 목록·「(없음)」)으로 되돌린다.
t = re.sub(r"^evidence: \[.*?\]$", "evidence: []", t, count=1, flags=re.M | re.S)
t = re.sub(r"\n## 증거\n.*\Z", "\n## 증거\n\nclose 시 `evidence/<run>.yaml` 링크가 여기에 채워진다. 실행 자체는 완료가 아니다(K-51).\n\n- (없음)\n", t, flags=re.S)
if state == "after-round3":
    t = t.replace("- [x] AC-", "- [ ] AC-")
open(path, "w").write(t)
PY

# close 의 CHECK_PLAN_COMMITTED·TASK_ANCHORED 는 승인된 spec 을 **이력에서** 읽는다 —
# 임시 루트도 커밋 1건이 있어야 그 자리까지 간다(그 사실 자체가 이 관통의 관측이다).
git -C "$TMP" init -q .
git -C "$TMP" -c user.email=probe@local -c user.name=probe add -A >/dev/null
git -C "$TMP" -c user.email=probe@local -c user.name=probe commit -qm "재현: $STATE"

OUT="$TMP/close.out"
"$HARNESS/bin/romeo" close --unit "$UNIT" --root "$TMP" --dry-run >"$OUT" 2>&1
echo "close rc=$?"
cat "$OUT"

echo
echo "── 기대한 요구가 인쇄됐는가 ──"
rc=0
for name in ${EXPECT[@]+"${EXPECT[@]}"}; do
  if grep -qE "^  \[FAIL\] $name( |$)" "$OUT"; then
    echo "OK   [FAIL] $name  — $(grep -m1 -E "^  \[FAIL\] $name( |$)" "$OUT" | cut -c1-200)"
  else
    echo "MISS [FAIL] $name  — 인쇄되지 않았다"
    rc=1
  fi
done
for name in ${FORBID[@]+"${FORBID[@]}"}; do
  if grep -qE "^  \[FAIL\] $name( |$)" "$OUT"; then
    echo "MISS $name 이 FAIL 로 인쇄됐다 — 요구를 되돌리지 않았는데 막혔다"
    rc=1
  else
    echo "OK   $name 은 FAIL 로 인쇄되지 않았다 — $(grep -m1 -E "\] $name( |$)" "$OUT" | cut -c1-160)"
  fi
done
exit $rc
