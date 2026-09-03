"""시나리오 9 자동 실행 — `scenarios/9-guard-approval.md` 의 12단계를 그대로 돌린다.

입력은 **기존 fixture** 다(`fixtures/requests/fx-repo-archive-delete.yaml` — `intent: delete` 라
라우터가 `deletion` 가드를 건다). 시나리오 전용 입력을 새로 만들면 그 입력이 시나리오에 맞춰져 있어
아무것도 증명하지 못한다.

**2·3·4·7·9·11 단계는 막히는 것이 통과다.** 통과만 보이는 런북은 빈 검사와 같다. 그리고 반례는
빈 값이 아니라 **그럴듯한 거짓 값**이어야 한다 — 4 단계(라벨은 넷 다 있고 값이 자리표시자)와
7 단계(원시 로그와 yaml 을 함께 손으로 만들어 봉인까지 맞춘 빈 승인)가 고치기 전에 통과하던 자리다.

**실제 삭제는 하지 않는다.** 이 시나리오는 가드가 막는 것을 보는 것이 정의다."""
import io
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from romeo import HARNESS_ROOT, frontmatter
from romeo.cli import main
from romeo.close import close_unit
from romeo.docs import approve_unit, create_unit
from romeo.evidence import (HEAD_LINE, TREE_LINE, add_approval, add_rejection, guard_decisions,
                            list_runs, parse_guard_explanation, required_explanation, run_command)
from romeo.policy import load_project_state, route
from romeo.util import dump_yaml, load_yaml, sha256_bytes

RUNBOOK = HARNESS_ROOT / "scenarios/9-guard-approval.md"
DELETE_FX = HARNESS_ROOT / "fixtures/requests/fx-repo-archive-delete.yaml"
GUARD_POLICY = HARNESS_ROOT / "core/policy/execution-guards.yaml"

SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"
SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `scripts/` · `README.md`"

#: 사실대로 적은 설명 넷. `사전 백업` 은 **정직한 부재**다 — 이유가 붙었으므로 막히지 않는다(AC-7).
HONEST_NOTE = ("영향 범위: archive/farion1231-cc-switch 디렉터리 하나. 다른 아카이브와 코드는 건드리지 않는다 / "
               "사전 백업: 없음 — 아직 커밋 전이라 스냅샷이 없다. 대신 삭제 전 파일 목록을 증거로 남긴다 / "
               "복구 방법: git checkout HEAD -- archive/farion1231-cc-switch / "
               "확인할 내용: 삭제 대상이 그 디렉터리 하나뿐이고 다른 곳에서 참조하지 않는지")
#: 그럴듯한 거짓 값 — 라벨은 넷 다 있고 값만 자리표시자다. 빈 값만 막는 검사는 이것을 통과시킨다.
PLACEHOLDER_NOTE = "영향 범위: TBD / 사전 백업: 없음 / 복구 방법: 해당 없음 / 확인할 내용: -"
#: 넷 중 셋만. 셋을 적은 것은 넷을 적은 것이 아니다.
THREE_OF_FOUR_NOTE = ("영향 범위: 아카이브 하나 / 사전 백업: 없음 — 커밋 전이다 / "
                      "복구 방법: git checkout HEAD -- <경로>")


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


def cli(*argv):
    """CLI 를 실제 진입점으로 부른다 — 종료 코드가 판정이다(`bin/romeo` 가 그대로 반환한다)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue() + err.getvalue()


class TestScenario9(unittest.TestCase):
    """단계 번호는 메서드 이름의 `stepN` 에 들어 있다 — 런북과 이 파일을 나란히 읽을 수 있게."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        self.fx = load_yaml(DELETE_FX)
        self.out = route(self.fx["classification"], project_state=load_project_state(HARNESS_ROOT))
        res = create_unit(self.out, "아카이브 삭제", "archive-delete", "삭제 가드",
                          project_root=self.root, date="20260902")
        self.unit = res["id"]
        self.spec = Path(res["files"][0])
        fm, body = frontmatter.read(self.spec)
        body = (body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
                    .replace('command: "채움"', 'command: "true"').replace("- [ ] AC-1", "- [x] AC-1"))
        frontmatter.write(self.spec, fm, body)
        approve_unit(self.unit, "tester", project_root=self.root)
        # 구현이 있어야 HAS_CHANGE 가 서고, 그래야 판정이 GUARD_APPROVED 하나에 걸린다.
        (self.root / "x.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl", cwd=self.root)
        run_command(self.unit, "true", run_name="run-9", label="check-1", project_root=self.root)

    def tearDown(self):
        self.tmp.cleanup()

    # ── 도구 ─────────────────────────────────────────────────────────────────
    def guard_row(self):
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        return r, next(c for c in r["checks"] if c["id"] == "GUARD_APPROVED")

    def record(self):
        return load_yaml(self.spec.parent / "evidence" / "run-9.yaml")

    def approve_logs(self):
        d = self.root / ".harness" / "runs" / self.unit / "run-9"
        return sorted(p.name for p in d.glob("approve-*.log")) if d.is_dir() else []

    # ── 전제 ─────────────────────────────────────────────────────────────────
    def test_premise_fixture_routes_to_the_deletion_guard(self):
        """전제: 시나리오 전용 입력을 만들지 않는다 — 기존 fixture 가 `deletion` 을 건다."""
        self.assertEqual([g["id"] for g in self.out["guards"]], ["deletion"])

    def test_premise_runbook_is_listed_and_has_the_five_sections(self):
        self.assertIn("9-guard-approval.md", (HARNESS_ROOT / "scenarios/README.md").read_text(encoding="utf-8"))
        text = RUNBOOK.read_text(encoding="utf-8")
        for title in ("## 전제", "## 단계", "## 기대 판단", "## 산출물", "## 증거"):
            self.assertIn(title, text)

    # ── 1 ────────────────────────────────────────────────────────────────────
    def test_step1_no_decision_yet_fails_as_never_asked(self):
        r, row = self.guard_row()
        self.assertFalse(row["ok"])
        self.assertIn("승인 기록 없음", row["detail"])
        self.assertIn("아직 묻지 않았다", row["detail"])
        self.assertEqual(r["verdict"], "FAIL")
        # 승인되지 않은 가드가 있으면 재실행하지 않는다 — 승인 없이 실행하지 않는다(K-66).
        self.assertTrue(any("승인되지 않은 실행 가드" in c["detail"] for c in r["checks"]))

    # ── 2·3·4 — 그럴듯한 거짓 값이 전부 막힌다 ────────────────────────────────
    def test_step2_approve_without_note_is_refused(self):
        code, text = cli("evidence", "approve", "--unit", self.unit, "--guard", "deletion",
                         "--by", "tester", "--run", "run-9", "--root", str(self.root))
        self.assertNotEqual(code, 0, text)
        for it in required_explanation():
            self.assertIn(it["label"], text)

    def test_step3_three_of_four_items_is_refused(self):
        code, text = cli("evidence", "approve", "--unit", self.unit, "--guard", "deletion",
                         "--by", "tester", "--note", THREE_OF_FOUR_NOTE, "--run", "run-9",
                         "--root", str(self.root))
        self.assertNotEqual(code, 0, text)
        self.assertIn("확인할 내용", text)
        self.assertIn("빠진 항목", text)

    def test_step4_all_four_labels_with_placeholder_values_is_refused(self):
        """**고치기 전에 통과하던 값이다.** 라벨은 넷 다 있고 내용이 거짓이다."""
        code, text = cli("evidence", "approve", "--unit", self.unit, "--guard", "deletion",
                         "--by", "tester", "--note", PLACEHOLDER_NOTE, "--run", "run-9",
                         "--root", str(self.root))
        self.assertNotEqual(code, 0, text)
        self.assertIn("자리표시자", text)

    # ── 5 — 반쪽 기록을 남기지 않는다 ────────────────────────────────────────
    def test_step5_refused_attempts_leave_no_record_at_all(self):
        before_logs = self.approve_logs()
        for note in (None, THREE_OF_FOUR_NOTE, PLACEHOLDER_NOTE):
            with self.assertRaises(ValueError):
                add_approval(self.unit, "deletion", "tester", note=note, run_name="run-9",
                             project_root=self.root)
        self.assertEqual(self.record().get("approvals") or [], [])
        self.assertEqual(self.approve_logs(), before_logs)
        _r, row = self.guard_row()
        self.assertFalse(row["ok"])           # 상태는 승인 전 그대로다

    # ── 6 — 사실대로 넷을 적으면 승인된다 ───────────────────────────────────
    def test_step6_an_honest_note_is_accepted_and_closes_the_guard(self):
        code, text = cli("evidence", "approve", "--unit", self.unit, "--guard", "deletion",
                         "--by", "tester", "--note", HONEST_NOTE, "--run", "run-9",
                         "--root", str(self.root))
        self.assertEqual(code, 0, text)
        rec = self.record()
        self.assertEqual(len(rec["approvals"]), 1)
        self.assertTrue(rec["approvals"][0]["log"].startswith(".harness/runs/"))
        _r, row = self.guard_row()
        self.assertTrue(row["ok"], row["detail"])
        # 정직한 부재("사전 백업: 없음 — 이유")가 막히지 않았다는 것을 값으로 확인한다(AC-7).
        self.assertTrue(parse_guard_explanation(HONEST_NOTE)["backup"].startswith("없음"))

    # ── 7 — 봉인을 손으로 맞춰도 종료 자리에서 잡힌다 ──────────────────────
    def hand_sealed_approval(self, log_note, yaml_note, seq=1):
        """승인 로그와 evidence yaml 을 **함께 손으로 만든다** — 봉인(`log_sha256`)까지 맞춘다.

        `log_note` 와 `yaml_note` 를 따로 받는 것이 이 도구의 요점이다. 둘을 같게 주면 7 단계
        (봉인은 맞고 설명 요구가 잡는다)이고, 다르게 주면 13 단계(로그는 빈 note, yaml 은 유효한 넷)다."""
        path = self.spec.parent / "evidence" / "run-9.yaml"
        rec = load_yaml(path)
        entry = {"guard": "deletion", "approved_at": "2026-09-02T09:00:00+09:00",
                 "approved_by": "forger", "note": yaml_note, "seq": seq,
                 "head_sha": rec["head_sha"], "dirty_tree_hash": rec["dirty_tree_hash"]}
        log_dir = self.root / ".harness" / "runs" / self.unit / "run-9"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "approve-01-deletion.log"
        text = (f"approve guard=deletion by=forger at={entry['approved_at']}\n"
                + f"seq: {seq}\nnote: {log_note}\n"
                + HEAD_LINE.format(sha=rec["head_sha"]) + "\n"
                + TREE_LINE.format(hash=rec["dirty_tree_hash"]) + "\n")
        log_path.write_text(text, encoding="utf-8")
        entry["log"] = f".harness/runs/{self.unit}/run-9/approve-01-deletion.log"
        entry["log_sha256"] = sha256_bytes(text.encode("utf-8"))
        rec["approvals"] = [entry]
        path.write_text(dump_yaml(rec), encoding="utf-8")

    def reseal(self, kind, idx, at):
        """이미 기록된 결정의 시각을 바꾸고 그 로그를 **다시 봉인한다**(seq 는 건드리지 않는다).

        14 단계가 보이려는 것은 '같은 시각에 들어온 두 결정' 에서 yaml 의 `seq` 만 바꾸는 것이다.
        `now_iso()` 는 초 단위라 두 결정이 같은 초에 들어오는지는 벽시계에 달려 있는데, 그것에
        기대면 이 반례가 시계에 따라 나타났다 사라진다 — 시각을 손으로 같게 맞춰 고정한다."""
        path = self.spec.parent / "evidence" / "run-9.yaml"
        rec = load_yaml(path)
        array, at_key = ("approvals", "approved_at") if kind == "approve" else ("rejections", "rejected_at")
        entry = rec[array][idx]
        entry[at_key] = at
        log_path = self.root / entry["log"]
        lines = log_path.read_text(encoding="utf-8").split("\n")
        head, _, rest = lines[0].partition(" at=")
        lines[0] = f"{head} at={at}"
        text = "\n".join(lines)
        log_path.write_text(text, encoding="utf-8")
        entry["log_sha256"] = sha256_bytes(text.encode("utf-8"))
        path.write_text(dump_yaml(rec), encoding="utf-8")

    def test_step7_a_hand_sealed_empty_approval_is_caught_at_close(self):
        """승인 로그와 yaml 을 **함께** 손으로 만들어 봉인을 맞춘다. 봉인은 통과하고 요구가 잡는다."""
        self.hand_sealed_approval(log_note="", yaml_note="")
        _r, row = self.guard_row()
        self.assertFalse(row["ok"], row["detail"])
        self.assertIn("봉인은 맞지만", row["detail"])       # 봉인은 통과했다 — 잡은 것은 설명 요구다
        self.assertIn("설명 요구", row["detail"])

    # ── 8·9·10·11 — 거부 ────────────────────────────────────────────────────
    def test_step8_reject_is_recorded_in_its_own_array(self):
        code, text = cli("evidence", "reject", "--unit", self.unit, "--guard", "deletion",
                         "--by", "tester", "--note", HONEST_NOTE, "--run", "run-9",
                         "--root", str(self.root))
        self.assertEqual(code, 0, text)
        rec = self.record()
        self.assertEqual(len(rec["rejections"]), 1)
        self.assertEqual(rec.get("approvals") or [], [])   # 승인 배열에 섞지 않는다
        e = rec["rejections"][0]
        self.assertEqual(e["rejected_by"], "tester")
        self.assertTrue((self.root / e["log"]).is_file())
        self.assertTrue(e["log"].endswith("reject-01-deletion.log"))
        self.assertEqual(sha256_bytes((self.root / e["log"]).read_bytes()), e["log_sha256"])

    def test_step9_a_rejected_guard_fails_close_with_blocked_approval(self):
        add_rejection(self.unit, "deletion", "사용자", note=HONEST_NOTE, run_name="run-9",
                      project_root=self.root)
        r, row = self.guard_row()
        self.assertFalse(row["ok"])
        self.assertIn("BLOCKED_APPROVAL", row["detail"])
        self.assertIn("사용자", row["detail"])
        self.assertNotIn("승인 기록 없음 — 아직 묻지 않았다", row["detail"])   # 다른 판정이다
        self.assertIn("답이 아니다", row["detail"])
        self.assertEqual(r["verdict"], "FAIL")

    def test_step10_a_later_approval_wins_over_an_earlier_rejection(self):
        add_rejection(self.unit, "deletion", "사용자", note=HONEST_NOTE, run_name="run-9",
                      project_root=self.root)
        add_approval(self.unit, "deletion", "사용자", note=HONEST_NOTE, run_name="run-9",
                     project_root=self.root)
        decisions = guard_decisions(list_runs(self.root, self.unit), "deletion")
        self.assertEqual([d["kind"] for d in decisions], ["reject", "approve"])
        _r, row = self.guard_row()
        self.assertTrue(row["ok"], row["detail"])

    def test_step11_reject_without_a_note_is_refused(self):
        code, text = cli("evidence", "reject", "--unit", self.unit, "--guard", "deletion",
                         "--by", "tester", "--run", "run-9", "--root", str(self.root))
        self.assertNotEqual(code, 0, text)
        self.assertEqual(self.record().get("rejections") or [], [])

    # ── 12 — 코어는 게이트 호출을 모른다 ────────────────────────────────────
    def test_step12_core_does_not_name_the_gate_command(self):
        for path in (HARNESS_ROOT / "core").rglob("*"):
            if path.is_file():
                self.assertNotIn("gate-create", path.read_text(encoding="utf-8", errors="replace"),
                                 f"{path} 에 게이트 호출 명령이 있다(C-C6)")
        runbook = (HARNESS_ROOT / "adapters/orca/RUNBOOK.md").read_text(encoding="utf-8")
        self.assertIn("gate-create", runbook)             # 호출은 어댑터가 소유한다
        self.assertIn("romeo evidence reject", runbook)   # 그리고 거부 명령으로 잇는다

    # ── 13·14 — 봉인이 note·seq 를 묶는가 ───────────────────────────────────
    def test_step13_a_valid_yaml_note_over_an_empty_sealed_note_is_caught(self):
        """**로그는 빈 note · yaml 은 유효한 넷 · 봉인은 일치.** 그럴듯한 거짓 값이다.

        7 단계는 로그와 yaml 이 **둘 다 빈** 경우였다 — 빈 값은 고치기 전에도 막혔다(§11).
        여기서는 봉인이 로그의 `note:` 줄을 yaml 과 대조하지 않는 한, 종료 시점의 설명 요구가
        **봉인되지 않은 yaml 을 읽고** 통과한다. 승인·종료 두 지점이 한 지점이 되는 자리다."""
        self.hand_sealed_approval(log_note="", yaml_note=HONEST_NOTE)
        _r, row = self.guard_row()
        self.assertFalse(row["ok"], row["detail"])
        self.assertIn("note", row["detail"])
        self.assertIn("원시 로그와 다르다", row["detail"])

    def test_step14_flipping_only_the_yaml_seq_reverses_the_last_decision(self):
        """**로그는 그대로 · yaml 의 `seq` 만 뒤집는다.** 같은 시각의 승인·거부 순서가 바뀐다.

        승인 뒤 거부이므로 마지막 결정은 거부이고 close 는 `BLOCKED_APPROVAL` 로 막아야 한다.
        `seq` 를 봉인해 놓고 대조하지 않으면, yaml 한 글자로 승인이 마지막이 되어 통과한다."""
        add_approval(self.unit, "deletion", "사용자", note=HONEST_NOTE, run_name="run-9",
                     project_root=self.root)
        add_rejection(self.unit, "deletion", "사용자", note=HONEST_NOTE, run_name="run-9",
                      project_root=self.root)
        same = "2026-09-02T09:00:00+09:00"
        self.reseal("approve", 0, same)
        self.reseal("reject", 0, same)
        path = self.spec.parent / "evidence" / "run-9.yaml"
        rec = load_yaml(path)
        self.assertEqual((rec["approvals"][0]["seq"], rec["rejections"][0]["seq"]), (1, 2))
        _r, row = self.guard_row()
        self.assertFalse(row["ok"], row["detail"])          # 뒤집기 전: 마지막은 거부다
        self.assertIn("BLOCKED_APPROVAL", row["detail"])
        rec["approvals"][0]["seq"] = 3                      # 로그는 그대로 두고 yaml 만 고친다
        path.write_text(dump_yaml(rec), encoding="utf-8")
        _r, row = self.guard_row()
        self.assertFalse(row["ok"], row["detail"])
        self.assertIn("seq", row["detail"])
        self.assertIn("원시 로그와 다르다", row["detail"])

    # ── 요구하는 자리와 보는 자리가 같은가 (AGENTS.core §11) ────────────────
    def test_the_explanation_requirement_has_exactly_one_source(self):
        """라벨을 코드에 복사하지 않았는가. 정책표를 늘리면 두 집행 자리가 함께 움직여야 한다."""
        items = required_explanation()
        self.assertEqual([it["key"] for it in items], ["scope", "backup", "recovery", "check"])
        for src in ("romeo/evidence.py", "romeo/close.py"):
            text = (HARNESS_ROOT / src).read_text(encoding="utf-8")
            for it in items:
                self.assertNotIn(f'"{it["label"]}"', text, f"{src} 에 라벨이 복사돼 있다 — 정본이 둘이 된다")
        self.assertIn("required_explanation", GUARD_POLICY.read_text(encoding="utf-8"))
