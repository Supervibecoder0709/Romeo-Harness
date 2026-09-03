#!/bin/sh
# AC-10 — **고치기 전 상태에서 실패하는 것**을 보인다. 성공 조건은 아래 둘이 **모두** 참인 것이다.
#
#   A. base 리비전(53fa828)의 트리에 `tests/test_scenario_9.py` **하나만** 얹으면 그 자리에서 실패한다.
#      실패하지 않으면 그 검사는 이 단위를 판별하지 못하는 빈 검사다.
#   B. 같은 base 트리에서 **빈 승인이 통과한다** — note 를 빈 문자열로 적은 가드 승인이 기록되고
#      `romeo close` 의 `GUARD_APPROVED` 가 그것을 승인으로 센다. A 의 실패가 "모듈이 없다" 로만 보이지
#      않게, 고치기 전 상태에서 **무엇이 통과했는지**를 같은 트리에서 직접 보인다.
#   C. 13·14 단계가 겨누는 구멍(봉인이 `note`·`seq` 를 대조하지 않는다)이 **그 두 단계가 더해지기 전
#      트리에서 열려 있다.** base 트리에는 그 단계를 실행할 코드 자체가 없으므로 base 로는 보일 수 없다 —
#      아래 C 절이 그 자리를 대신한다. 자세한 이유는 C 절의 주석에 있다.
#
# 이 단위의 산출물인 검사를 승인 전에 실행할 수는 없으므로(D-27), 승인 뒤 이 재현이 그 자리를 대신한다.
set -eu
REPO=$(pwd)
BASE=53fa8286698ea96fb52ed7dfdedb70f6d23bae78
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
git archive "$BASE" | tar -x -C "$WORK"
cp tests/test_scenario_9.py "$WORK/tests/test_scenario_9.py"

echo "=== A. base 트리 + 이 테스트만 ==="
cd "$WORK"
set +e
python3 -m unittest tests.test_scenario_9 > "$WORK/a.log" 2>&1
A=$?
set -e
tail -20 "$WORK/a.log"
echo "A exit=$A"

echo "=== B. base 트리에서 빈 승인이 통과하는가 ==="
set +e
python3 - <<'PY'
import subprocess, sys, tempfile
from pathlib import Path
from romeo import frontmatter
from romeo.close import close_unit
from romeo.docs import approve_unit, create_unit
from romeo.evidence import add_approval, run_command
from romeo.policy import load_project_state, route
from romeo.util import load_yaml
from romeo import HARNESS_ROOT

def git(*a, cwd):
    return subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()

fx = load_yaml(HARNESS_ROOT / "fixtures/requests/fx-repo-archive-delete.yaml")
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    git("init", "-q", cwd=root); git("config", "user.email", "t@e.com", cwd=root); git("config", "user.name", "t", cwd=root)
    (root / "README.md").write_text("hello\n", encoding="utf-8")
    git("add", ".", cwd=root); git("commit", "-q", "-m", "init", cwd=root)
    out = route(fx["classification"], project_state=load_project_state(HARNESS_ROOT))
    res = create_unit(out, "아카이브 삭제", "archive-delete", "삭제 가드", project_root=root, date="20260902")
    unit, spec = res["id"], Path(res["files"][0])
    fm, body = frontmatter.read(spec)
    body = (body.replace("NEEDS_INPUT", "채움")
                .replace("- 바뀌는 파일·모듈: 채움", "- 바뀌는 파일·모듈: `docs/work/` · `scripts/` · `README.md`")
                .replace('command: "채움"', 'command: "true"').replace("- [ ] AC-1", "- [x] AC-1"))
    frontmatter.write(spec, fm, body)
    approve_unit(unit, "tester", project_root=root)
    (root / "x.txt").write_text("impl\n", encoding="utf-8")
    git("add", ".", cwd=root); git("commit", "-q", "-m", "impl", cwd=root)
    run_command(unit, "true", run_name="run-9", label="check-1", project_root=root)
    # 빈 승인 — note 가 빈 문자열이다. 설명 네 항목 중 하나도 적히지 않았다.
    add_approval(unit, "deletion", "tester", note="", run_name="run-9", project_root=root)
    r = close_unit(unit, project_root=root, dry_run=True)
    row = next(c for c in r["checks"] if c["id"] == "GUARD_APPROVED")
    print("GUARD_APPROVED ok=%s detail=%s" % (row["ok"], row["detail"]))
    print("evidence approve reject 서브커맨드 있는가:",
          "reject" in subprocess.run([sys.executable, "-m", "romeo", "evidence", "--help"],
                                     cwd=str(HARNESS_ROOT), capture_output=True, text=True).stdout)
    sys.exit(0 if row["ok"] else 1)
PY
B=$?
set -e
echo "B exit=$B  (0 = 빈 승인이 통과했다 = 고치기 전 결함이 재현됐다)"

if [ "$A" -eq 0 ]; then
  echo "PROBE FAIL: base 트리에서 테스트가 통과했다 — 판별 검사가 아니다"; exit 1
fi
if [ "$B" -ne 0 ]; then
  echo "PROBE FAIL: base 트리에서 빈 승인이 막혔다 — 고치기 전 상태가 재현되지 않았다"; exit 1
fi
echo "PROBE OK: base 트리에서 이 테스트는 실패하고(A) 빈 승인은 통과한다(B)"

# ── C ─────────────────────────────────────────────────────────────────────────
#   C. 13·14 단계의 **고치기 전 상태**에서 구멍이 열려 있는가.
#
#      A·B 는 base 리비전(53fa828) 트리를 쓴다 — 거기에는 `romeo.evidence.add_rejection` 이 없어
#      13·14 단계를 실행할 수 없다. 이 두 단계가 겨누는 것은 base 의 구멍이 아니라 **1 회차 구현의
#      구멍**이기 때문이다(1 회차 findings 2건: 봉인이 `note` 와 `seq` 를 대조하지 않는다).
#      그래서 그 회차의 트리를 재현한다 — 지금 트리에서 2 회차가 더한 대조 블록 하나만 들어낸다.
#      들어내는 자리는 `romeo/evidence.py` 의 `approval_log_state` 안, 「seq·note 도 같은 대조를
#      받는다」 주석부터 그 함수의 `return True, ""` 앞까지다. 블록을 못 찾으면 이 프로브는 실패한다 —
#      찾지 못한 채 통과하면 "아무것도 들어내지 않고 통과했다" 와 구별되지 않는다.
#
#      성공 조건: 그 트리에서 13·14 단계가 **실패한다**. 실패의 내용이 곧 구멍이다 —
#      `assertFalse(row["ok"])` 가 `True is not false` 로 깨지는 것은, 위조된 승인을
#      `GUARD_APPROVED` 가 **승인으로 셌다**는 뜻이다.
#      고친 뒤 이 둘이 통과하는 것은 check-1 이 보인다(같은 두 단계를 현재 트리에서 실행한다).
echo "=== C. 1회차 트리(봉인이 note·seq 를 대조하지 않는다)에서 13·14 단계 ==="
W2=$(mktemp -d)
trap 'rm -rf "$WORK" "$W2"' EXIT
cd "$REPO"
git archive HEAD | tar -x -C "$W2"
# 커밋되지 않은 구현(수정·미추적)을 그대로 얹어 **지금 트리**를 만든다.
git ls-files -mo --exclude-standard -z | while IFS= read -r -d '' f; do
  [ -f "$f" ] || continue
  mkdir -p "$W2/$(dirname "$f")"
  cp "$f" "$W2/$f"
done

python3 - "$W2" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1]) / "romeo/evidence.py"
s = p.read_text(encoding="utf-8")
head = "    # ── seq·note 도 같은 대조를 받는다"
try:
    a = s.index(head)
    b = s.index('    return True, ""', a)
except ValueError:
    sys.exit("PROBE FAIL: 들어낼 대조 블록을 romeo/evidence.py 에서 찾지 못했다")
if b <= a:
    sys.exit("PROBE FAIL: 대조 블록의 경계가 뒤집혔다")
print("들어낸 줄 수: %d" % s[a:b].count("\n"))
p.write_text(s[:a] + s[b:], encoding="utf-8")
PY

cd "$W2"
set +e
python3 -m unittest -v \
  tests.test_scenario_9.TestScenario9.test_step13_a_valid_yaml_note_over_an_empty_sealed_note_is_caught \
  tests.test_scenario_9.TestScenario9.test_step14_flipping_only_the_yaml_seq_reverses_the_last_decision \
  > "$W2/c.log" 2>&1
C=$?
set -e
cat "$W2/c.log"
echo "C exit=$C  (0 이 아니어야 한다 = 13·14 단계가 그 트리에서 실패했다)"

if [ "$C" -eq 0 ]; then
  echo "PROBE FAIL: 대조 블록을 들어냈는데도 13·14 단계가 통과했다 — 판별 검사가 아니다"; exit 1
fi
if ! grep -q "True is not false" "$W2/c.log"; then
  echo "PROBE FAIL: 실패했지만 그 이유가 '위조된 승인이 승인으로 세어졌다' 가 아니다"; exit 1
fi
echo "PROBE OK: 봉인이 note·seq 를 대조하지 않는 트리에서 13·14 단계가 실패한다 —"
echo "          로그는 빈 note(13)·yaml 의 seq 한 글자(14)로 GUARD_APPROVED 가 통과했다"
