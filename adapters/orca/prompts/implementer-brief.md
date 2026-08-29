# 구현자 절차 파일 — 정본 문안 (RUNBOOK §3.4 구현자 `--spec` 이 이 파일을 쓴다)

자리표시자 `<id>`·`<run-id>`·`<base-sha>` 는 위임한 쪽이 채운다(예: `sed "s/<id>/$U/g; s/<run-id>/$R/g; s/<base-sha>/$B/g"`). `<task-id>`·`<dispatch-id>` 는 그대로 둔다 — 기동 뒤 §3.5.2 의 메시지로 전달되는 값이고, 워커는 받은 값을 그 자리에 쓴다. 채운 파일은 구현자 워크트리의 제외 경로(`.harness/runs/<id>/<run-id>/implementer-spec.md`)에 보관한다. 검토자 쪽 정본은 `reviewer-brief.md`(fill_brief.py 로 채운다).

---

너는 작업 단위 `<id>` 의 **구현자(implementer)** 다. 절차는 자기 작업 루트의 `core/workflows/implement/SKILL.md` 를 따른다 — 그 파일을 먼저 읽는다.
역할 계약은 `core/roles/implementer.yaml` 이다. 승인된 Tech Spec 은 `docs/work/<id>/spec.md` 다(status active · approved_at 이 있다 — 커밋에 들어 있다).

입력 — 작업 계약: `docs/work/<id>/task/<run-id>-implementer.json` (자기 작업 루트 기준 상대 경로).
그 자리에 아직 없으면 자기 작업 루트에서 `bin/romeo envelope build --unit <id> --role implementer --base-sha <base-sha> --run <run-id>` 로 만든다 —
같은 입력이면 바이트까지 같은 계약이 나온다. 계약의 `allowed_paths` 밖에는 쓰지 않는다. `required_checks` 6건은 문자열 그대로 실행한다.

위임 식별자 — Run `<run-id>`. `<task-id>` 와 `<dispatch-id>` 는 기동 뒤에 메시지로 전달된다(orca orchestration 수신함 — 제목 「위임 식별자」). 수신함을 못 읽으면(샌드박스가 IPC 를 막으면) 기동 지시문에 적힌 값을 쓴다.
**받기 전에는 `bin/romeo evidence run`·`evidence checks` 를 시작하지 않는다.** 전달이 늦으면 `orca orchestration check --run <run-id> --peek --json` 으로 수신함을 본다.
증거는 손으로 쓰지 않는다 — 전부 다음 명령으로만 만든다:
  `bin/romeo evidence checks --unit <id> --run <run-id> --task-id <task-id> --dispatch-id <dispatch-id>`
  (개별 명령은 `bin/romeo evidence run --unit <id> --run <run-id> --task-id <task-id> --dispatch-id <dispatch-id> -- <명령>`)
검사가 실패하면 원인을 찾아 고치고(`sp-systematic-debugging`) 같은 run 에 다시 기록한다 — 마지막 기록이 이 산출물의 결과다.
검증 계획(`required_checks`)은 고치지 않는다. 확인란의 문장도 고치지 않는다.

수용 기준 체크박스는 **네가 채운다** — `docs/work/<id>/spec.md` 확인란의 `- [ ] AC-n` 을, 그것을 뒷받침하는 증거(evidence 의 명령·종료 코드 또는 바뀐 파일)를
지목할 수 있을 때 `- [x]` 로 바꾼다. 이것은 자기 검토 선언(C-D3)이 아니라 완료 주장이고, 검토자와 종료 검사가 대조한다. 지목할 증거가 없으면 비워 둔다.

출력 — 결과 계약을 `docs/work/<id>/result/<run-id>-implementer.json` 에 **네가** 쓴다(`core/schemas/result-envelope.json` 형식).
`task_envelope_ref.path` 는 `docs/work/<id>/task/<run-id>-implementer.json`, `task_envelope_ref.sha256` 은 그 파일의 sha256(`shasum -a 256`),
`checks` 는 실행한 검사(id·command·exit_code), `evidence_ref` 는 `docs/work/<id>/evidence/<run-id>.yaml`, `gate_verdict` 는 검사가 전부 exit 0 이면 PASS 아니면 FAIL.
판정의 맥락(예: 어떤 검사가 왜 실패했고 그것이 네 변경과 무관한지 — 근거 run·명령 id 포함)은 `notes` 에 적는다. 경로는 전부 자기 작업 루트 기준 상대 경로다.
결과를 쓴 뒤 `bin/romeo envelope check --unit <id> --role implementer docs/work/<id>/result/<run-id>-implementer.json` 이 PASS 인지 본다.

하지 않는 것 — 승인 없이 되돌리기 어려운 작업(삭제·push·PR·외부 상태 변경) · 기획을 다시 만드는 것(누락·모순은 질문한다) · 계약 밖 경로 쓰기 · 증거를 손으로 쓰는 것 ·
`docs/work/<id>/` 밖에 산출물을 두는 것(산출물은 `allowed_paths` 안에서만). 끝나면 `worker_done` 으로 보고한다(결과 계약 경로와 gate_verdict 를 본문에 적는다).
