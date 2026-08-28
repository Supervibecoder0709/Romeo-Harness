"""수직 슬라이스의 기계 부분: new → validate → approve → evidence → close, 그리고 stale 거부 4경우 + 미체크 AC 거부."""
import io
import json
import os
import re
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from romeo import frontmatter
from romeo.cli import main
from romeo.close import close_unit, format_close
from romeo.docs import approve_unit, create_unit
from romeo.envelope import write_envelope
from romeo.evidence import add_approval, run_command
from romeo.policy import route
from romeo.util import load_yaml, sha256_file
from romeo.validate import validate_doc


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


class TestVerticalSlice(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        out = route({"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"], "gates": [], "blast_radius": "small", "uncertainty": "low"})
        res = create_unit(out, "테스트 T0", "test-t0", "테스트용 변경", project_root=self.root, date="20260827")
        self.unit = res["id"]
        self.spec = Path(res["files"][0])

    def tearDown(self):
        self.tmp.cleanup()

    def _fill_spec(self, tick_ac=True, command="true"):
        fm, body = frontmatter.read(self.spec)
        body = body.replace("NEEDS_INPUT", "채움")
        body = body.replace('command: "채움"', f'command: "{command}"')
        if tick_ac:
            body = body.replace("- [ ] AC-1", "- [x] AC-1")
        frontmatter.write(self.spec, fm, body)

    def _implement_and_commit(self):
        (self.root / "x.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl", cwd=self.root)

    def test_new_doc_validates_and_has_sections(self):
        r = validate_doc(self.spec)
        self.assertEqual(r["errors"], [], r)
        self.assertTrue(any(w.startswith("OPEN_LOOP") for w in r["warnings"]))
        body = self.spec.read_text(encoding="utf-8")
        for title in ("## 확인란", "## Planning Capsule", "## 변경 범위", "## 구현 단위", "## 검증 계획", "## 증거"):
            self.assertIn(title, body)

    def test_approve_requires_filled_user_check(self):
        with self.assertRaises(ValueError):
            approve_unit(self.unit, "tester", project_root=self.root)
        self._fill_spec(tick_ac=False)
        fm = approve_unit(self.unit, "tester", project_root=self.root)
        self.assertEqual(fm["status"], "active")
        self.assertEqual(fm["base_sha"], git("rev-parse", "HEAD", cwd=self.root))
        self.assertIsNotNone(fm["approved_at"])

    def test_close_rejects_unchecked_ac_and_passes_after_tick(self):
        self._fill_spec(tick_ac=False)
        approve_unit(self.unit, "tester", project_root=self.root)
        self._implement_and_commit()
        res = run_command(self.unit, "true", run_name="run-test", label="check-1", project_root=self.root)
        self.assertEqual(res["command"]["exit_code"], 0)
        self.assertEqual(res["state"]["changed_files"], ["x.txt"])
        self.assertEqual(res["state"]["head_sha"], git("rev-parse", "HEAD", cwd=self.root))
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("AC_ALL_CHECKED", [c["id"] for c in r["checks"] if not c["ok"]])
        # AC 체크(문서 디렉터리 편집)는 evidence 를 stale 로 만들지 않는다
        self._fill_spec(tick_ac=True)
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        self.assertEqual(r["verdict"], "PASS", r["checks"])
        r = close_unit(self.unit, project_root=self.root)
        self.assertEqual(r["verdict"], "PASS")
        fm, body = frontmatter.read(self.spec)
        self.assertEqual(fm["status"], "done")
        self.assertEqual(fm["evidence"], ["evidence/run-test.yaml"])
        self.assertIn("close PASS", body)
        self.assertEqual(close_unit(self.unit, project_root=self.root, dry_run=True)["verdict"], "FAIL")  # 이미 done

    def test_close_rejects_missing_required_check(self):
        self._fill_spec(tick_ac=True, command="echo required")
        approve_unit(self.unit, "tester", project_root=self.root)
        self._implement_and_commit()
        run_command(self.unit, "true", run_name="run-test", project_root=self.root)
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        self.assertIn("REQUIRED_CHECK", [c["id"] for c in r["checks"] if not c["ok"]])
        run_command(self.unit, "echo required", run_name="run-test", project_root=self.root)
        self.assertEqual(close_unit(self.unit, project_root=self.root, dry_run=True)["verdict"], "PASS")

    def test_stale_rejection_four_cases(self):
        self._fill_spec(tick_ac=True)
        approve_unit(self.unit, "tester", project_root=self.root)
        self._implement_and_commit()
        run_command(self.unit, "true", run_name="run-test", project_root=self.root)
        self.assertEqual(close_unit(self.unit, project_root=self.root, dry_run=True)["verdict"], "PASS")

        def failed_ids():
            r = close_unit(self.unit, project_root=self.root, dry_run=True)
            return {c["id"] for c in r["checks"] if not c["ok"] and c["level"] == "error"}

        # 1) tracked 파일 수정
        (self.root / "README.md").write_text("changed\n", encoding="utf-8")
        self.assertIn("FRESH_TREE", failed_ids())
        # 2) staged 변경
        git("add", "README.md", cwd=self.root)
        self.assertIn("FRESH_TREE", failed_ids())
        git("reset", "-q", "--hard", cwd=self.root)
        self.assertEqual(failed_ids(), set())
        # 3) untracked 추가
        (self.root / "new.txt").write_text("u\n", encoding="utf-8")
        self.assertIn("FRESH_TREE", failed_ids())
        (self.root / "new.txt").unlink()
        self.assertEqual(failed_ids(), set())
        # 4) 커밋 이동
        (self.root / "README.md").write_text("moved\n", encoding="utf-8")
        git("commit", "-q", "-am", "move", cwd=self.root)
        self.assertIn("FRESH_HEAD", failed_ids())
        # 제외 경로(.harness, 단위 문서 디렉터리)는 신선도에 영향 없음
        git("reset", "-q", "--hard", "HEAD~1", cwd=self.root)
        (self.root / ".harness" / "x").mkdir(parents=True)
        (self.root / ".harness" / "x" / "log").write_text("l", encoding="utf-8")
        (self.spec.parent / "note.md").write_text("n", encoding="utf-8")
        self.assertEqual(failed_ids(), set())

    def test_close_rejects_no_change(self):
        self._fill_spec(tick_ac=True)
        approve_unit(self.unit, "tester", project_root=self.root)
        run_command(self.unit, "true", run_name="run-test", project_root=self.root)  # 구현 없이 명령만 실행
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        self.assertIn("HAS_CHANGE", [c["id"] for c in r["checks"] if not c["ok"]])

    # ── 가드 승인은 실행보다 먼저 올 수 있다 (절차 순서: 승인 → 실행) ──────────────
    def test_approval_before_any_run_creates_approval_only_record(self):
        self._fill_spec(tick_ac=False)
        approve_unit(self.unit, "tester", project_root=self.root)
        path = add_approval(self.unit, "deletion", "tester", note="영향 범위·복구",
                            run_name="run-test", project_root=self.root)
        rec = load_yaml(path)
        self.assertEqual(rec["commands"], [])          # 승인 시점에 상태 변경 0건이라는 사실 자체가 증거다
        self.assertEqual(rec["run_id"], "run-test")
        self.assertEqual(rec["approvals"][0]["guard"], "deletion")
        self.assertIsNone(rec["head_sha"])             # 아직 아무 명령도 실행하지 않았다
        run_command(self.unit, "true", run_name="run-test", project_root=self.root)
        rec = load_yaml(path)
        self.assertEqual(len(rec["commands"]), 1)      # 같은 run 에 붙는다 — 승인 기록은 그대로
        self.assertEqual(len(rec["approvals"]), 1)
        self.assertIsNotNone(rec["head_sha"])

    def test_approval_after_run_still_appends_to_existing_run(self):
        self._fill_spec(tick_ac=False)
        approve_unit(self.unit, "tester", project_root=self.root)
        run_command(self.unit, "true", run_name="run-test", project_root=self.root)
        path = add_approval(self.unit, "deletion", "tester", project_root=self.root)
        rec = load_yaml(path)
        self.assertEqual(len(rec["commands"]), 1)
        self.assertEqual(len(rec["approvals"]), 1)

    # ── 위임 식별자 ─────────────────────────────────────────────────────────────
    def test_delegation_ids_are_recorded_once_per_run(self):
        self._fill_spec(tick_ac=False)
        approve_unit(self.unit, "tester", project_root=self.root)
        res = run_command(self.unit, "true", run_name="run-test", task_id="task_1a2b",
                          dispatch_id="dis_9f8e", project_root=self.root)
        rec = load_yaml(res["evidence"])
        self.assertEqual(rec["task_id"], "task_1a2b")
        self.assertEqual(rec["dispatch_id"], "dis_9f8e")
        run_command(self.unit, "true", run_name="run-test", task_id="task_1a2b", project_root=self.root)
        self.assertEqual(load_yaml(res["evidence"])["task_id"], "task_1a2b")
        with self.assertRaises(ValueError):   # 한 run 은 한 위임에 속한다
            run_command(self.unit, "true", run_name="run-test", task_id="task_other", project_root=self.root)

    def test_evidence_cli_accepts_delegation_flags(self):
        self._fill_spec(tick_ac=False)
        approve_unit(self.unit, "tester", project_root=self.root)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["evidence", "run", "--unit", self.unit, "--run", "run-cli",
                       "--task-id", "task_cli", "--dispatch-id", "dis_cli",
                       "--root", str(self.root), "--", "true"])
        self.assertEqual(rc, 0)
        rec = load_yaml(self.spec.parent / "evidence" / "run-cli.yaml")
        self.assertEqual((rec["task_id"], rec["dispatch_id"]), ("task_cli", "dis_cli"))
        with redirect_stdout(io.StringIO()):
            rc = main(["evidence", "approve", "--unit", self.unit, "--guard", "deletion",
                       "--by", "tester", "--run", "run-ap", "--task-id", "task_cli",
                       "--root", str(self.root)])
        self.assertEqual(rc, 0)
        rec = load_yaml(self.spec.parent / "evidence" / "run-ap.yaml")
        self.assertEqual(rec["task_id"], "task_cli")

    def test_close_prints_unverified_when_the_spec_has_no_check_plan(self):
        """검증 계획이 비어 있으면 evidence 와 대조할 검사가 하나도 없다. 아무 줄도 인쇄하지 않고 지나가면
        읽는 사람은 실행 대조가 있었다고 믿는다 — 검사 불가로 인쇄한다(K-51)."""
        self._fill_spec(tick_ac=True)
        fm, body = frontmatter.read(self.spec)
        frontmatter.write(self.spec, fm, re.sub(r"```yaml\s*\nrequired_checks:.*?\n```",
                                                "(검사 계획 없음)", body, flags=re.S))
        approve_unit(self.unit, "tester", project_root=self.root)
        self._implement_and_commit()
        run_command(self.unit, "true", run_name="run-test", project_root=self.root)
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        row = next(c for c in r["checks"] if c["id"] == "REQUIRED_CHECK")
        self.assertEqual(row["level"], "unverified", r["checks"])
        self.assertIn("[UNVERIFIED] REQUIRED_CHECK", format_close(r))
        self.assertNotIn("[PASS] REQUIRED_CHECK", format_close(r))
        # 어긴 검사는 하나도 없다. 그래도 대조하지 못한 것이 있으면 done 이 아니다(K-51).
        self.assertEqual({c["id"] for c in r["checks"] if not c["ok"] and c["level"] == "error"}, set())
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("미검증은 완료가 아니다", format_close(r))
        self.assertNotEqual(frontmatter.read(self.spec)[0]["status"], "done")

    def test_evidence_checks_without_required_checks_reports_and_exits_nonzero(self):
        """검사 계획이 비어 있으면 '무엇이 없다'를 말하고 비0 으로 끝난다 — 조건 없이 부르는 명령의 실패 신호가
        스택 트레이스면 워커는 무엇이 빠졌는지 알 수 없다."""
        fm, body = frontmatter.read(self.spec)
        body = re.sub(r"```yaml\s*\nrequired_checks:.*?\n```", "(검사 계획 없음)", body, flags=re.S)
        frontmatter.write(self.spec, fm, body)
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["evidence", "checks", "--unit", self.unit, "--root", str(self.root)])
        self.assertEqual(rc, 2)
        self.assertIn("required_checks", err.getvalue())
        self.assertNotIn("Traceback", out.getvalue() + err.getvalue())


class TestCloseReviewVerdict(unittest.TestCase):
    """검토자가 필요한 패키지에서 close 는 검토자의 게이트 판정을 읽는다(D-c).
    FAIL 이면 done 을 선언하지 않고, 판정을 읽을 수 없어도 통과가 아니다.
    스키마를 통과했다는 것도 검토가 아니다 — 봉투의 주장은 실재하는 계약·리비전·증거에 묶여야 한다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        self.init_sha = git("rev-parse", "HEAD", cwd=self.root)   # 승인 이전 커밋 — spec.md 가 아직 없다
        out = route({"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                     "gates": ["legal"], "blast_radius": "small", "uncertainty": "low"})
        self.assertNotEqual(out["reviewer"], "none")
        res = create_unit(out, "검토 필요 T0", "review-t0", "검토자가 붙는 변경",
                          project_root=self.root, date="20260828")
        self.unit = res["id"]
        self.spec = Path(res["files"][0])
        fm, body = frontmatter.read(self.spec)
        body = body.replace("NEEDS_INPUT", "채움").replace('command: "채움"', 'command: "true"')
        body = body.replace("- [ ] AC-1", "- [x] AC-1")
        frontmatter.write(self.spec, fm, body)
        approve_unit(self.unit, "tester", project_root=self.root)
        # 승인된 spec 을 커밋해야 계약을 만들 수 있다(D-a) — 위임된 실행 공간은 커밋된 것만 본다.
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)
        self.approval_sha = git("rev-parse", "HEAD", cwd=self.root)
        built = write_envelope(self.unit, "reviewer", project_root=self.root,
                               base_sha=self.approval_sha, run_name="run-test")
        self.task_path = Path(built["path"])
        self.task_rel = f"docs/work/{self.unit}/task/run-test-reviewer.json"
        self.task_sha = built["sha256"]
        (self.root / "x.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl", cwd=self.root)
        run_command(self.unit, "true", run_name="run-test", project_root=self.root)
        self.review = self.spec.parent / "review"
        self.review.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _envelope(self, verdict="PASS", **over):
        """실제 계약 산출물을 가리키는 봉투. sha256 은 손으로 쓰지 않고 그 파일에서 읽는다 —
        테스트가 손으로 쓴 값을 표준으로 박아 두면 느슨한 계약이 고정된다.
        검토자는 명령을 실행하지 않으므로 checks 는 비어 있다(core/roles/reviewer.yaml)."""
        env = {
            "schema": "romeo/result-envelope@0.1.0",
            "unit_id": self.unit,
            "role": "reviewer",
            "task_envelope_ref": {"path": self.task_rel, "sha256": self.task_sha},
            "checks": [],
            "gate_verdict": verdict,
            "blocked_reason": None,
            "findings": [],
            "evidence_ref": f"docs/work/{self.unit}/evidence/run-test.yaml",
        }
        env.update(over)
        return env

    def _write_review(self, name, data):
        (self.review / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def _failed(self):
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        return {c["id"] for c in r["checks"] if not c["ok"] and c["level"] == "error"}, r

    def test_empty_review_dir_fails(self):
        ids, _ = self._failed()
        self.assertIn("HAS_REVIEW", ids)

    def test_non_json_file_is_not_a_verdict(self):
        (self.review / "notes.txt").write_text("좋아 보임", encoding="utf-8")
        ids, _ = self._failed()
        self.assertIn("HAS_REVIEW", ids)

    def test_reviewer_fail_blocks_close(self):
        self._write_review("run-test-reviewer.json", self._envelope("FAIL"))
        ids, r = self._failed()
        self.assertIn("REVIEW_VERDICT", ids)
        self.assertEqual(r["verdict"], "FAIL")

    def test_unreadable_envelope_is_rejected_not_passed(self):
        (self.review / "run-test-reviewer.json").write_text("{ 깨진 json", encoding="utf-8")
        ids, _ = self._failed()
        self.assertIn("REVIEW_ENVELOPE_VALID", ids)
        self._write_review("run-test-reviewer.json", self._envelope(gate_verdict="MAYBE"))
        ids, _ = self._failed()
        self.assertIn("REVIEW_ENVELOPE_VALID", ids)

    def test_envelope_of_another_unit_is_rejected(self):
        self._write_review("run-test-reviewer.json", self._envelope(unit_id="chg-20260101-other-abcd"))
        ids, _ = self._failed()
        self.assertIn("REVIEW_ENVELOPE_VALID", ids)

    def test_reviewer_pass_closes(self):
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        ids, r = self._failed()
        self.assertEqual(ids, set(), r["checks"])
        self.assertEqual(r["verdict"], "PASS")

    def test_any_standing_fail_blocks_close(self):
        self._write_review("run-a-reviewer.json", self._envelope("PASS"))
        self._write_review("run-b-reviewer.json", self._envelope("BLOCKED", blocked_reason="BLOCKED_CAPABILITY"))
        ids, _ = self._failed()
        self.assertIn("REVIEW_VERDICT", ids)

    # ── 앵커 반례: 스키마를 통과한 PASS 봉투가 무엇에도 매여 있지 않을 때 ──────────────
    def test_task_envelope_ref_to_missing_file_is_rejected(self):
        """가리킨 계약 파일이 없으면 그 판정은 아무 계약에도 매여 있지 않다."""
        self._write_review("run-test-reviewer.json", self._envelope(
            task_envelope_ref={"path": f"docs/work/{self.unit}/task/없는계약.json", "sha256": "0" * 64}))
        ids, r = self._failed()
        self.assertIn("REVIEW_TASK_ANCHORED", ids)
        self.assertEqual(r["verdict"], "FAIL")

    def test_hand_written_task_envelope_hash_is_rejected(self):
        """계약은 실재하는데 봉투가 손으로 쓴 해시를 실었다 — 그 계약을 읽었다는 증거가 아니다."""
        self._write_review("run-test-reviewer.json", self._envelope(
            task_envelope_ref={"path": self.task_rel, "sha256": "0" * 64}))
        ids, r = self._failed()
        self.assertIn("REVIEW_TASK_ANCHORED", ids)
        self.assertEqual(r["verdict"], "FAIL")

    def test_task_envelope_ref_outside_the_repo_is_rejected(self):
        self._write_review("run-test-reviewer.json", self._envelope(
            task_envelope_ref={"path": "/etc/hosts", "sha256": sha256_file("/etc/hosts")}))
        ids, _ = self._failed()
        self.assertIn("REVIEW_TASK_ANCHORED", ids)

    def test_task_envelope_of_another_role_is_rejected(self):
        """구현자 계약을 가리킨 검토자 판정은 검토자에게 주어진 계약의 이행이 아니다."""
        other = write_envelope(self.unit, "implementer", project_root=self.root,
                               base_sha=self.approval_sha, run_name="run-test")
        self._write_review("run-test-reviewer.json", self._envelope(
            task_envelope_ref={"path": f"docs/work/{self.unit}/task/run-test-implementer.json",
                               "sha256": other["sha256"]}))
        ids, _ = self._failed()
        self.assertIn("REVIEW_TASK_ANCHORED", ids)

    def _retarget_base_sha(self, sha):
        """계약 파일의 base_sha 만 바꾸고 봉투의 해시를 그 파일에서 다시 읽는다 — 앵커 자체는 성립시킨 채
        '어느 리비전의 검토인가' 만 어긋나게 만든다."""
        task = json.loads(self.task_path.read_text(encoding="utf-8"))
        task["base_sha"] = sha
        self.task_path.write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return self._envelope(task_envelope_ref={"path": self.task_rel, "sha256": sha256_file(self.task_path)})

    def test_base_sha_that_is_not_a_commit_is_rejected(self):
        self._write_review("run-test-reviewer.json", self._retarget_base_sha("0" * 40))
        ids, r = self._failed()
        self.assertIn("REVIEW_BASE_SHA", ids)
        self.assertEqual(r["verdict"], "FAIL")

    def test_base_sha_outside_current_history_is_rejected(self):
        """다른 이력에서 만든 계약으로 낸 판정은 이 리비전의 검토가 아니다(evidence 신선도와 같은 이유)."""
        orphan = git("commit-tree", "HEAD^{tree}", "-m", "orphan", cwd=self.root)
        self.assertNotEqual(orphan, git("rev-parse", "HEAD", cwd=self.root))
        self._write_review("run-test-reviewer.json", self._retarget_base_sha(orphan))
        ids, _ = self._failed()
        self.assertIn("REVIEW_BASE_SHA", ids)

    def test_evidence_ref_to_missing_file_is_rejected(self):
        self._write_review("run-test-reviewer.json", self._envelope(
            evidence_ref="docs/work/없는단위/evidence/없는파일.yaml"))
        ids, r = self._failed()
        self.assertIn("REVIEW_EVIDENCE_ANCHORED", ids)
        self.assertEqual(r["verdict"], "FAIL")

    def test_evidence_ref_outside_the_unit_is_rejected(self):
        """실재하기만 하면 되는 것이 아니다 — 이 작업 단위에 등록된 증거여야 한다(K-62)."""
        self._write_review("run-test-reviewer.json", self._envelope(evidence_ref="README.md"))
        ids, _ = self._failed()
        self.assertIn("REVIEW_EVIDENCE_ANCHORED", ids)

    def test_reviewer_checks_violate_the_role_contract(self):
        """검토자는 명령을 실행하지 않는다 — checks 를 실은 봉투는 동등성 판정과 같은 기준으로 거부한다."""
        self._write_review("run-test-reviewer.json", self._envelope(
            checks=[{"id": "check-1", "command": "true", "exit_code": 0}]))
        ids, r = self._failed()
        self.assertIn("REVIEW_ROLE_CONTRACT", ids)
        self.assertIn("ROLE_CONTRACT_VIOLATION", "; ".join(
            c["detail"] for c in r["checks"] if c["id"] == "REVIEW_ROLE_CONTRACT"))

    def test_reviewer_pass_without_evidence_ref_is_rejected(self):
        """읽기만 하는 역할이 PASS 를 내면서 읽은 증거를 지목하지 못하면 뒷받침할 것이 하나도 없다(K-51)."""
        self._write_review("run-test-reviewer.json", self._envelope(evidence_ref=None))
        ids, _ = self._failed()
        self.assertIn("REVIEW_ROLE_CONTRACT", ids)

    # ── 검사할 수 없었던 것을 PASS 로 인쇄하지 않는다 (3차 리뷰 H06) ──────────────────
    def _row(self, r, cid):
        return next(c for c in r["checks"] if c["id"] == cid)

    def _assert_unverified(self, r, cid):
        """PASS 도 FAIL 도 아닌 세 번째 상태로 인쇄되고, 전체 판정에서 통과로 세지 않는다."""
        row = self._row(r, cid)
        self.assertEqual(row["level"], "unverified", row)
        self.assertFalse(row["ok"], row)
        text = format_close(r)
        self.assertNotIn(f"[PASS] {cid}", text)
        self.assertIn(f"[UNVERIFIED] {cid}", text)
        self.assertTrue(row["detail"], row)

    def test_base_sha_is_not_pass_when_the_task_contract_is_missing(self):
        """대조할 계약 파일이 없으면 base_sha 검사는 성립하지 않는다 — 그것을 PASS 로 인쇄하지 않는다."""
        self._write_review("run-test-reviewer.json", self._envelope(
            task_envelope_ref={"path": f"docs/work/{self.unit}/task/없는계약.json", "sha256": "0" * 64}))
        ids, r = self._failed()
        self.assertIn("REVIEW_TASK_ANCHORED", ids)
        self._assert_unverified(r, "REVIEW_BASE_SHA")
        self.assertEqual(r["verdict"], "FAIL")

    def test_unreadable_envelope_leaves_the_anchor_checks_unverified(self):
        """봉투를 읽지 못하면 앵커 네 검사 중 어느 것도 대조하지 못한다 — 넷 다 PASS 로 인쇄되지 않는다."""
        (self.review / "run-test-reviewer.json").write_text("{ 깨진 json", encoding="utf-8")
        ids, r = self._failed()
        self.assertIn("REVIEW_ENVELOPE_VALID", ids)
        for cid in ("REVIEW_TASK_ANCHORED", "REVIEW_BASE_SHA", "REVIEW_EVIDENCE_ANCHORED", "REVIEW_ROLE_CONTRACT"):
            self._assert_unverified(r, cid)

    def test_evidence_anchor_is_not_pass_when_the_envelope_points_at_nothing(self):
        """지목한 증거가 없으면 '증거가 이 단위 안에 있는가' 를 대조할 수 없다 — PASS 가 아니다."""
        self._write_review("run-test-reviewer.json", self._envelope("FAIL", evidence_ref=None))
        ids, r = self._failed()
        self.assertIn("REVIEW_VERDICT", ids)
        self._assert_unverified(r, "REVIEW_EVIDENCE_ANCHORED")

    def test_a_valid_envelope_still_prints_pass(self):
        """세 번째 상태를 넣어도 실제로 대조한 검사는 그대로 PASS 다 — 검사를 무디게 만들지 않았다."""
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        _ids, r = self._failed()
        text = format_close(r)
        for cid in ("REVIEW_TASK_ANCHORED", "REVIEW_BASE_SHA", "REVIEW_EVIDENCE_ANCHORED", "REVIEW_ROLE_CONTRACT"):
            self.assertIn(f"[PASS] {cid}", text)
        self.assertNotIn("[UNVERIFIED]", text)

    # ── 앵커는 해시가 아니라 재계산이다 (4차 리뷰 J01) ───────────────────────────
    def _forge_task(self, name, task):
        """계약 파일을 손으로 써 두고, 봉투에는 **그 파일의 진짜 해시**를 싣는다.
        해시 대조만 하는 검사는 이것을 통과시킨다 — 두 값 모두 봉투 작성자가 정하기 때문이다."""
        rel_path = f"docs/work/{self.unit}/task/{name}"
        path = self.root / rel_path
        path.write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return self._envelope(task_envelope_ref={"path": rel_path, "sha256": sha256_file(path)})

    def _detail(self, r, cid):
        return next(c["detail"] for c in r["checks"] if c["id"] == cid)

    def test_hand_written_task_contract_with_a_matching_hash_is_rejected(self):
        """4필드 JSON + 맞는 해시 — 이 형태가 close 를 PASS·exit 0 으로 통과시켰다(J01 반례)."""
        self._write_review("run-test-reviewer.json", self._forge_task(
            "run-forged-reviewer.json",
            {"unit_id": self.unit, "role": "reviewer", "base_sha": self.approval_sha,
             "workspace": "current"}))
        ids, r = self._failed()
        self.assertIn("REVIEW_TASK_ANCHORED", ids)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("task-envelope.json", self._detail(r, "REVIEW_TASK_ANCHORED"))
        self._assert_unverified(r, "REVIEW_BASE_SHA")

    def test_contract_pointing_before_the_approval_commit_is_rejected(self):
        """계약 생성 명령이 D-a 로 거부하는 입력이 종료 검사의 앵커를 통과하면 안 된다."""
        task = json.loads(self.task_path.read_text(encoding="utf-8"))
        task["base_sha"] = self.init_sha            # 승인된 spec.md 가 아직 커밋되지 않은 리비전
        self._write_review("run-test-reviewer.json", self._forge_task("run-old-reviewer.json", task))
        ids, r = self._failed()
        self.assertIn("REVIEW_TASK_ANCHORED", ids)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("다시 계산", self._detail(r, "REVIEW_TASK_ANCHORED"))

    def test_tampered_contract_with_a_matching_hash_is_rejected(self):
        """스키마도 맞고 해시도 맞지만 내용이 계약과 다르다 — 재계산이 바이트로 잡는다."""
        task = json.loads(self.task_path.read_text(encoding="utf-8"))
        task["allowed_paths"] = ["."]               # 검토자에게 쓰기 범위를 붙였다(K-66)
        self._write_review("run-test-reviewer.json",
                           self._forge_task("run-widened-reviewer.json", task))
        ids, r = self._failed()
        self.assertIn("REVIEW_TASK_ANCHORED", ids)
        self.assertIn("allowed_paths", self._detail(r, "REVIEW_TASK_ANCHORED"))
        self.assertEqual(r["verdict"], "FAIL")

    def test_recomputed_contract_still_passes_for_a_real_run(self):
        """재계산을 넣어도 실제 계약 생성 명령이 만든 계약은 그대로 통과한다 — 검사를 막히게 하지 않았다."""
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        _ids, r = self._failed()
        self.assertIn("[PASS] REVIEW_TASK_ANCHORED", format_close(r))
        self.assertEqual(r["verdict"], "PASS")

    # ── 증거는 그 작업 단위의 증거 산출물이어야 한다 (4차 리뷰 J04) ────────────────
    def test_reviewer_cannot_cite_its_own_input_as_evidence(self):
        """검토자가 판정 대상으로 받은 spec.md 를 '읽은 증거' 로 지목한다 — 실재하지만 증거가 아니다.
        같은 값을 동등성 판정은 거부해 왔다: 두 검사기가 같은 함수를 쓴다(K-62·K-63)."""
        self._write_review("run-test-reviewer.json", self._envelope(
            evidence_ref=f"docs/work/{self.unit}/spec.md"))
        ids, r = self._failed()
        self.assertIn("REVIEW_EVIDENCE_ANCHORED", ids)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("evidence/", self._detail(r, "REVIEW_EVIDENCE_ANCHORED"))

    def test_evidence_of_another_unit_is_rejected_even_if_it_exists(self):
        other = self.spec.parent.parent / "chg-20260101-other-abcd" / "evidence"
        other.mkdir(parents=True)
        (other / "run-x.yaml").write_text("run_id: run-x\n", encoding="utf-8")
        self._write_review("run-test-reviewer.json", self._envelope(
            evidence_ref="docs/work/chg-20260101-other-abcd/evidence/run-x.yaml"))
        ids, _ = self._failed()
        self.assertIn("REVIEW_EVIDENCE_ANCHORED", ids)

    # ── 여러 봉투를 합칠 때 PASS 가 UNVERIFIED 를 덮지 않는다 (4차 리뷰 J03) ────────
    def test_a_pass_envelope_does_not_cover_another_envelopes_unverified(self):
        """정상 봉투 1개 + 읽을 수 없는 봉투 1개. 대조하지 못한 검사를 PASS 로 인쇄하면
        인쇄와 계수가 이미 틀렸고, 같은 봉투를 `romeo envelope check` 는 UNVERIFIED 로 본다(K-51·K-63)."""
        self._write_review("run-a-reviewer.json", self._envelope("PASS"))
        (self.review / "run-b-reviewer.json").write_text("{ 깨진 json", encoding="utf-8")
        ids, r = self._failed()
        self.assertIn("REVIEW_ENVELOPE_VALID", ids)
        for cid in ("REVIEW_TASK_ANCHORED", "REVIEW_BASE_SHA",
                    "REVIEW_EVIDENCE_ANCHORED", "REVIEW_ROLE_CONTRACT"):
            self._assert_unverified(r, cid)
        self.assertEqual(r["verdict"], "FAIL")

    def test_fully_hand_written_pass_envelope_does_not_close(self):
        """2차 리뷰 G05 의 반례 그대로: 존재하지 않는 계약·존재하지 않는 증거·역할이 금지한 checks."""
        self._write_review("run-test-reviewer.json", self._envelope(
            task_envelope_ref={"path": f"docs/work/{self.unit}/task/reviewer.json", "sha256": "0" * 64},
            checks=[{"id": "check-1", "command": "true", "exit_code": 0}],
            evidence_ref="docs/work/없는단위/evidence/없는파일.yaml"))
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self.assertTrue({"REVIEW_TASK_ANCHORED", "REVIEW_EVIDENCE_ANCHORED", "REVIEW_ROLE_CONTRACT"} <= ids, ids)
        fm, _ = frontmatter.read(self.spec)
        self.assertNotEqual(fm["status"], "done")


if __name__ == "__main__":
    unittest.main()
