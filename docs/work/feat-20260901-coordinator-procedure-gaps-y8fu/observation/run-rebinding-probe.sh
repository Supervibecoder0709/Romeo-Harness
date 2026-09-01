#!/usr/bin/env bash
# AC-5 실측 — 코디네이터 터미널과 Run 의 바인딩 전환.
# 이 스크립트는 **별도 터미널**에서 돈다. run-create 가 그 터미널의 바인딩을 옮기기 때문이다.
#
# **출력은 stdout 으로 낸다.** 1회차는 `exec > "$OUT"` 로 전부 파일에 삼켰고, 그 파일은
# `romeo/evidence.py` 의 exclusions() 제외 경로라 어떤 실행에도 묶이지 않았다(1회차 검토자 findings 2).
# 2회차는 `bin/romeo evidence run --label run-rebinding-probe -- …` 로 감싸 stdout 이
# 원시 로그와 log_sha256·stdout_tail 에 봉인되게 한다. 인자로 파일을 주면 tee 로 사본을 하나 더 남길 뿐이다.
say() { echo; echo "=== $* ==="; }
run() { echo "\$ $*"; "$@"; echo "exit=$?"; }

main() {
say "0. 이 터미널의 handle 과 시작 시점 바인딩"
echo "ORCA_TERMINAL_HANDLE=$ORCA_TERMINAL_HANDLE"
run orca orchestration run-current --json

say "1. Run A 생성"
A=$(orca orchestration run-create --objective "feat-20260901-coordinator-procedure-gaps-y8fu · AC-5 관측 Run A" --json | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["run"]["id"])')
echo "A=$A"
run orca orchestration run-current --json

say "2. Run A 에 Task 를 하나 만들어 둔다 — 전환 뒤 '읽을 수 있는가' 의 대상"
run orca orchestration task-create --run "$A" --task-title "AC-5 probe task A" --spec "관측 전용. 배치하지 않는다" --json

say "3. Run B 생성 — 여기서 바인딩이 옮겨간다"
B=$(orca orchestration run-create --objective "feat-20260901-coordinator-procedure-gaps-y8fu · AC-5 관측 Run B" --json | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["run"]["id"])')
echo "B=$B"
run orca orchestration run-current --json

say "4. (c) 거부의 모양 — 옛 Run A 에 대한 명령 3종"
run orca orchestration check --run "$A" --peek --json
run orca orchestration task-list --run "$A" --brief --json
run orca orchestration task-update --id task_doesnotexist --run "$A" --status failed --json

say "5. (a) run-use --run 은 받지 않는다는 것"
run orca orchestration run-use --run "$A" --json

say "6. (a) run-use --id 로 전환"
run orca orchestration run-use --id "$A" --json
run orca orchestration run-current --json

say "7. (b) 전환 뒤 그 Run 의 상태·메시지를 실제로 읽을 수 있는가"
run orca orchestration check --run "$A" --peek --json
run orca orchestration task-list --run "$A" --brief --json
run orca orchestration run-show --id "$A" --json

say "8. 전환 뒤 새 Run B 는 어떻게 되는가 — 이제 B 가 옛 Run 이다"
run orca orchestration check --run "$B" --peek --json
run orca orchestration task-list --run "$B" --brief --json

say "9. run-list — 두 Run 이 다 남아 있는가"
run orca orchestration run-list --json

echo
echo "=== DONE A=$A B=$B ==="
}

OUT="${1:-}"
if [ -n "$OUT" ]; then
  main 2>&1 | tee "$OUT"
else
  main 2>&1
fi
