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

from romeo import HARNESS_ROOT, frontmatter
from romeo.cli import main
from romeo.close import close_unit, format_close
from romeo.docs import approve_unit, create_unit
from romeo.envelope import write_envelope
from romeo.evidence import (add_approval, command_log_state, parse_log_exit_code,
                            record_review_envelope, run_command, run_required_checks)
from romeo.policy import route
from romeo.util import dump_yaml, load_yaml, sha256_file
from romeo.validate import validate_doc

# 작업 계약의 쓰기 상한은 spec 의 「변경 범위」에서 온다(체크리스트 34) — 각 `·` 항목의 첫 백틱이 그 항목의 경로다.
# 템플릿의 NEEDS_INPUT 자리에 실제 경로가 없으면 계약을 만들지 않는다(K-66).
SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"
SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `scripts/` · `README.md`"



def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


def with_fail_reasons(env):
    """FAIL 봉투에 사유 코드를 채운다 — 종료 검사가 현재 산출물의 FAIL 봉투에 사유를 요구한다.

    표본을 만드는 자리마다 손으로 적으면 새 규칙이 표본 어디에 걸리는지 흩어진다. 사유 자체를 보는
    테스트는 `fail_reasons` 를 직접 넘겨 덮고, **`fail_reasons=None` 을 넘기면 그 필드가 없는 옛 형식 봉투**가 된다."""
    if "fail_reasons" in env and env["fail_reasons"] is None:
        del env["fail_reasons"]
    elif env.get("gate_verdict") == "FAIL" and "fail_reasons" not in env:
        env["fail_reasons"] = ["AC_UNMET"]
    return env



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
        body = body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
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
        # 승인 시점의 HEAD 는 승인을 담지 않는 커밋이다 — base_sha 를 적지 않는다(체크리스트 38). 승인 커밋은 이력에서 찾는다.
        self.assertIsNone(fm["base_sha"])
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
    def test_a_hand_written_guard_approval_does_not_open_the_guard(self):
        """가드 승인은 yaml 배열이었다 — 항목 하나를 손으로 써 넣으면 승인으로 보였다. 이제 승인 사건도 원시 로그로 봉인된다."""
        out = route({"unit": "T0", "mode": "delivery", "intent": "delete", "facets": ["docs"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        res = create_unit(out, "삭제 T0", "guard-t0", "가드 승인", project_root=self.root, date="20260829")
        unit, spec = res["id"], Path(res["files"][0])
        fm, body = frontmatter.read(spec)
        body = body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS).replace('command: "채움"', 'command: "true"')
        frontmatter.write(spec, fm, body.replace("- [ ] AC-1", "- [x] AC-1"))
        approve_unit(unit, "tester", project_root=self.root)
        (self.root / "gone.txt").write_text("x\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve+impl", cwd=self.root)
        run_command(unit, "true", run_name="run-g", project_root=self.root)
        r = close_unit(unit, project_root=self.root, dry_run=True)
        self.assertIn("GUARD_APPROVED", [c["id"] for c in r["checks"] if not c["ok"] and c["level"] == "error"])
        # 손으로 써 넣은 승인 항목
        path = spec.parent / "evidence" / "run-g.yaml"
        rec = load_yaml(path)
        rec["approvals"] = [{"guard": "deletion", "approved_at": "2026-08-29T00:00:00+09:00", "approved_by": "forger", "note": None}]
        path.write_text(dump_yaml(rec), encoding="utf-8")
        r = close_unit(self.unit if False else unit, project_root=self.root, dry_run=True)
        row = next(c for c in r["checks"] if c["id"] == "GUARD_APPROVED")
        self.assertEqual(row["level"], "unverified", row)
        self.assertEqual(r["verdict"], "FAIL")
        # 정식 기록은 로그와 함께 남고 통과한다
        rec["approvals"] = []
        path.write_text(dump_yaml(rec), encoding="utf-8")
        add_approval(unit, "deletion", "tester", note="gone.txt 를 지운다", run_name="run-g", project_root=self.root)
        rec = load_yaml(path)
        self.assertTrue(rec["approvals"][0]["log"].startswith(".harness/runs/"))
        self.assertTrue((self.root / rec["approvals"][0]["log"]).is_file())
        r = close_unit(unit, project_root=self.root, dry_run=True)
        self.assertTrue(next(c for c in r["checks"] if c["id"] == "GUARD_APPROVED")["ok"], r["checks"])
        # 기록 뒤 로그를 고치면 잡힌다
        log = self.root / rec["approvals"][0]["log"]
        log.write_text(log.read_text(encoding="utf-8").replace("by=tester", "by=forger"), encoding="utf-8")
        r = close_unit(unit, project_root=self.root, dry_run=True)
        row = next(c for c in r["checks"] if c["id"] == "GUARD_APPROVED")
        self.assertFalse(row["ok"]); self.assertEqual(row["level"], "error")

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

    # ── 검사 기록은 내용으로 고른다(체크리스트 41) ───────────────────────────────
    def _defensive_run(self, run_name):
        """검토자를 띄운 쪽이 남기는 방어 검사 전용 run(RUNBOOK §4·§6.6) — 계획의 검사를 하나도 담지 않는다."""
        for label in ("review-tree-before", "review-tree-after"):
            run_command(self.unit, "git status --porcelain", run_name=run_name, label=label, project_root=self.root)

    def _selected(self, r):
        return next(c for c in r["checks"] if c["id"] == "EVIDENCE_SELECTED")

    def test_close_reads_the_run_that_executed_the_check_plan_not_the_latest_file(self):
        """§6.6 뒤에 close 가 구조적으로 깨지던 자리(체크리스트 41). 마지막 evidence 파일은 검토자를 띄우며 남긴
        방어 검사 전용 run 이고, 거기에는 required_checks 가 없다 — 그것을 읽으면 6건 전부 '명령 없음' 이었다."""
        self._fill_spec(tick_ac=True)
        approve_unit(self.unit, "tester", project_root=self.root)
        self._implement_and_commit()
        run_required_checks(self.unit, run_name="run-impl", project_root=self.root)
        self._defensive_run("run-review-1")
        self._defensive_run("run-review-2")
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        self.assertEqual(r["verdict"], "PASS", r["checks"])
        sel = self._selected(r)
        self.assertTrue(sel["ok"])
        self.assertIn("run-impl", sel["detail"])
        self.assertIn("run-review-1", sel["detail"])
        self.assertIn("run-review-2", sel["detail"])
        # 실제 close 는 판정을 **검사 기록** run 에 적는다 — 마지막 파일이 아니라.
        r = close_unit(self.unit, project_root=self.root)
        self.assertEqual(r["verdict"], "PASS")
        impl = load_yaml(self.spec.parent / "evidence" / "run-impl.yaml")
        self.assertEqual(impl["verdict"], "PASS")
        self.assertIn("close", impl)
        self.assertNotIn("close", load_yaml(self.spec.parent / "evidence" / "run-review-2.yaml"))
        fm, body = frontmatter.read(self.spec)
        self.assertEqual(fm["status"], "done")
        self.assertIn("evidence/run-impl.yaml", fm["evidence"])   # 방어 검사 run 도 이 단위의 증거로 남는다
        self.assertIn("evidence/run-review-1.yaml", fm["evidence"])

    def test_close_prefers_the_latest_complete_check_record_and_names_the_others(self):
        self._fill_spec(tick_ac=True)
        approve_unit(self.unit, "tester", project_root=self.root)
        self._implement_and_commit()
        run_required_checks(self.unit, run_name="run-a", project_root=self.root)
        run_required_checks(self.unit, run_name="run-b", project_root=self.root)
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        self.assertEqual(r["verdict"], "PASS", r["checks"])
        sel = self._selected(r)
        self.assertRegex(sel["detail"], r"검사 기록 = run-b")
        self.assertIn("run-a", sel["detail"])

    def test_close_falls_back_to_the_most_covering_run_and_says_so(self):
        """계획을 전부 실행한 run 이 없으면 통과가 아니다 — 가장 많이 실행한 run 을 읽되 그 사실을 WARN 으로 인쇄하고,
        빠진 검사는 REQUIRED_CHECK 가 잡는다. 조용히 마지막 파일을 읽는 것과 구분돼야 한다."""
        self._fill_spec(tick_ac=True)
        fm, body = frontmatter.read(self.spec)
        body = body.replace('    command: "true"\n',
                            '    command: "true"\n  - id: check-2\n    command: "echo two"\n')
        frontmatter.write(self.spec, fm, body)
        approve_unit(self.unit, "tester", project_root=self.root)
        self._implement_and_commit()
        run_command(self.unit, "true", run_name="run-partial", label="check-1", project_root=self.root)
        self._defensive_run("run-review-1")
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        self.assertEqual(r["verdict"], "FAIL")
        sel = self._selected(r)
        self.assertFalse(sel["ok"])
        self.assertEqual(sel["level"], "warning")
        self.assertIn("run-partial", sel["detail"])
        self.assertIn("1/2", sel["detail"])
        missing = [c for c in r["checks"] if c["id"] == "REQUIRED_CHECK" and not c["ok"]]
        self.assertEqual(len(missing), 1)
        self.assertIn("echo two", missing[0]["detail"])


    def test_close_prefers_a_run_of_the_current_tree_over_a_newer_run_of_another_tree(self):
        """동등성 관측을 모으는 절차(RUNBOOK §6.3)는 다른 산출물의 완전한 run 을 같은 evidence/ 에 둔다 —
        최신 규칙만으로는 그쪽이 뽑혀 기준 산출물의 검토 판정이 전부 낡은 것이 된다. 지금 트리와 같은 run 이 먼저다."""
        self._fill_spec(tick_ac=True)
        approve_unit(self.unit, "tester", project_root=self.root)
        self._implement_and_commit()
        run_required_checks(self.unit, run_name="run-here", project_root=self.root)
        here = load_yaml(self.spec.parent / "evidence" / "run-here.yaml")
        # 다른 산출물에서 만든 완전한 run 을 모아 온 것처럼 — 그 파일의 head/tree 만 다르다.
        other = dict(here)
        other["run_id"] = "run-other"
        other["head_sha"] = "f" * 40
        other["dirty_tree_hash"] = "e" * 64
        other["finished_at"] = "2099-01-01T00:00:00+09:00"
        (self.spec.parent / "evidence" / "run-other.yaml").write_text(dump_yaml(other), encoding="utf-8")
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        sel = self._selected(r)
        self.assertRegex(sel["detail"], r"검사 기록 = run-here")
        self.assertIn("지금 트리와 같은 산출물의 run 1건/2건", sel["detail"])
        self.assertTrue(next(c for c in r["checks"] if c["id"] == "FRESH_TREE")["ok"])

    def test_a_check_that_ran_on_another_tree_is_unverified(self):
        """한 run 의 검사는 한 산출물 위에서 전부 돌아야 한다 — run 의 산출물은 마지막 명령의 것이므로,
        중간에 트리가 바뀌었으면 그 전에 돈 검사의 결과는 이 산출물의 결과가 아니다."""
        self._fill_spec(tick_ac=True)
        approve_unit(self.unit, "tester", project_root=self.root)
        self._implement_and_commit()
        run_required_checks(self.unit, run_name="run-a", project_root=self.root)
        (self.root / "z.txt").write_text("late\n", encoding="utf-8")      # 검사 뒤에 트리가 바뀐다
        run_command(self.unit, "git status --porcelain", run_name="run-a", label="review-tree-before", project_root=self.root)
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        row = next(c for c in r["checks"] if c["id"] == "REQUIRED_CHECK")
        self.assertEqual(row["level"], "unverified", row)
        self.assertIn("다른 트리에서 돌았다", row["detail"])
        self.assertEqual(r["verdict"], "FAIL")

    def test_changing_the_user_check_text_after_approval_is_rejected(self):
        """구현자는 체크박스를 채울 수 있다 — 그러나 확인란의 문장은 사용자가 승인한 것이다(D-27·D-60).
        체크 표시 외의 변경은 재승인 대상이다."""
        self._fill_spec(tick_ac=False)
        approve_unit(self.unit, "tester", project_root=self.root)
        self._implement_and_commit()
        run_required_checks(self.unit, run_name="run-a", project_root=self.root)
        fm, body = frontmatter.read(self.spec)
        frontmatter.write(self.spec, fm, body.replace("- [ ] AC-1", "- [x] AC-1"))
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        self.assertEqual(r["verdict"], "PASS", r["checks"])
        self.assertTrue(next(c for c in r["checks"] if c["id"] == "AC_TEXT_UNCHANGED")["ok"])
        fm, body = frontmatter.read(self.spec)
        frontmatter.write(self.spec, fm, body.replace("- [x] AC-1", "- [x] AC-1 (완화된 기준)"))
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        self.assertEqual(r["verdict"], "FAIL")
        row = next(c for c in r["checks"] if c["id"] == "AC_TEXT_UNCHANGED")
        self.assertFalse(row["ok"])
        self.assertIn("reapprove", row["detail"])

    def test_committing_an_edited_check_plan_without_reapproval_is_rejected(self):
        """종전의 '절반의 앵커': 실패하는 검사를 계획에서 지우고 **커밋**하면 HEAD 와 같아져 통과했다.
        원본은 승인 커밋의 계획이다 — 계획을 바꾸려면 재승인해야 하고 재승인은 승인 커밋을 옮긴다."""
        self._fill_spec(tick_ac=True)
        fm, body = frontmatter.read(self.spec)
        body = body.replace('    command: "true"\n',
                            '    command: "true"\n  - id: check-2\n    command: "false"\n')
        frontmatter.write(self.spec, fm, body)
        approve_unit(self.unit, "tester", project_root=self.root)
        self._implement_and_commit()
        fm, body = frontmatter.read(self.spec)
        body = body.replace('  - id: check-2\n    command: "false"\n', "")
        frontmatter.write(self.spec, fm, body)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "drop the failing check", cwd=self.root)
        run_required_checks(self.unit, run_name="run-a", project_root=self.root)
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        row = next(c for c in r["checks"] if c["id"] == "CHECK_PLAN_COMMITTED")
        self.assertFalse(row["ok"], row)
        self.assertIn("승인 커밋", row["detail"])
        self.assertEqual(r["verdict"], "FAIL")
        # 재승인하고 커밋하면 원본이 옮겨져 통과한다.
        approve_unit(self.unit, "tester", project_root=self.root, reapprove=True, reason="check-2 제거")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "reapprove", cwd=self.root)
        run_required_checks(self.unit, run_name="run-b", project_root=self.root)
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        self.assertEqual(r["verdict"], "PASS", r["checks"])


class TestEvidenceIsReExecuted(unittest.TestCase):
    """4차 리뷰 구멍 A — 증거 YAML 을 손으로 고치면 close 가 뒤집혔다.

    `required_checks` 의 명령이 `false`(exit 1)인 단위에서 `exit_code: 1` 을 `0` 으로 고치자
    전 항목 PASS · EXIT 0 이 났다. 로컬 파일은 위조 불가로 만들 수 없으므로 세 겹으로 닫는다:

    1. **재실행 대조(종점).** close 가 `required_checks` 를 다시 실행해 기록과 대조한다.
       기록을 고쳐도 명령을 다시 돌린 결과는 고칠 수 없다 — AGENTS.core §4 가 요구하는 것이 이것이다.
    2. **원시 로그의 종료 코드.** 같은 사실이 두 곳에 적혀 있으면 한 곳만 고친 것이 드러난다.
    3. **`log_sha256` 을 읽는다.** 지금까지 쓰기만 하고 아무도 읽지 않았다 — 로그까지 고친 것을 잡는다.

    재실행으로 확인할 수 없는 경우는 막지 않고 **미검증으로 인쇄한다** — 통과로 세지 않으므로 done 이 아니다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        out = route({"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        res = create_unit(out, "재실행 대조 T0", "rerun-t0", "실패하는 검사를 가진 단위",
                          project_root=self.root, date="20260828")
        self.unit = res["id"]
        self.spec = Path(res["files"][0])

    def tearDown(self):
        self.tmp.cleanup()

    def _prepare(self, command="false"):
        """검증 계획의 명령이 `command` 인 승인된 단위를 만들고 그 명령을 실제로 실행해 증거를 남긴다."""
        fm, body = frontmatter.read(self.spec)
        body = body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS).replace('command: "채움"', f'command: "{command}"')
        frontmatter.write(self.spec, fm, body.replace("- [ ] AC-1", "- [x] AC-1"))
        approve_unit(self.unit, "tester", project_root=self.root)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)
        (self.root / "x.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl", cwd=self.root)
        run_required_checks(self.unit, run_name="run-a", project_root=self.root)
        self.epath = self.spec.parent / "evidence" / "run-a.yaml"
        self.log = self.root / ".harness" / "runs" / self.unit / "run-a" / "01-check-1.log"

    def _close(self, **kw):
        r = close_unit(self.unit, project_root=self.root, dry_run=True, **kw)
        return r, {c["id"] for c in r["checks"] if not c["ok"] and c["level"] == "error"}, \
            {c["id"] for c in r["checks"] if c["level"] == "unverified"}

    def _tamper_yaml(self, exit_code=0):
        rec = load_yaml(self.epath)
        for c in rec["commands"]:
            c["exit_code"] = exit_code
        self.epath.write_text(dump_yaml(rec), encoding="utf-8")
        return rec

    def test_the_raw_log_records_the_exit_code(self):
        """로그에 종료 코드가 없으면 뒤의 두 겹이 설 자리가 없다."""
        self._prepare("false")
        self.assertEqual(parse_log_exit_code(self.log.read_text(encoding="utf-8")), 1)
        rec = load_yaml(self.epath)
        self.assertEqual(rec["commands"][0]["log_sha256"], sha256_file(self.log))

    def test_hand_edited_exit_code_no_longer_flips_close(self):
        """구멍 A 의 반례 그대로: evidence YAML 의 exit_code 1 → 0."""
        self._prepare("false")
        _r, failed, _u = self._close()
        self.assertIn("REQUIRED_CHECK", failed)          # 정직한 상태에서는 검사 자체가 실패다
        self._tamper_yaml(0)
        r, failed, _u = self._close()
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("REQUIRED_CHECK_RERUN", failed, r["checks"])
        self.assertIn("EVIDENCE_LOG", failed, r["checks"])
        self.assertIn("다시 실행하니 exit 1", format_close(r))

    def test_editing_the_log_too_is_caught_by_the_seal(self):
        """한 겹 옆: 원시 로그의 종료 코드 줄까지 고친다 — log_sha256 과 어긋난다."""
        self._prepare("false")
        self._tamper_yaml(0)
        self.log.write_text(self.log.read_text(encoding="utf-8").replace("--- exit 1 ---", "--- exit 0 ---"),
                            encoding="utf-8")
        r, failed, _u = self._close()
        self.assertIn("EVIDENCE_LOG", failed)
        self.assertIn("원시 로그가 기록 이후 바뀌었다", format_close(r))
        self.assertIn("REQUIRED_CHECK_RERUN", failed)

    def test_resealing_the_log_still_does_not_survive_re_execution(self):
        """또 한 겹 옆: 로그도 고치고 log_sha256 도 다시 계산한다. 세 겹을 다 맞춰도 재실행이 남는다."""
        self._prepare("false")
        rec = self._tamper_yaml(0)
        text = self.log.read_text(encoding="utf-8").replace("--- exit 1 ---", "--- exit 0 ---")
        self.log.write_text(text, encoding="utf-8")
        rec["commands"][0]["log_sha256"] = sha256_file(self.log)
        self.epath.write_text(dump_yaml(rec), encoding="utf-8")
        r, failed, _u = self._close()
        self.assertNotIn("EVIDENCE_LOG", failed, "봉인까지 맞췄으므로 로그 대조는 통과한다")
        self.assertIn("REQUIRED_CHECK_RERUN", failed, "그래도 재실행 결과는 고칠 수 없다")
        self.assertEqual(r["verdict"], "FAIL")

    def test_a_missing_log_is_unverified_not_passed(self):
        """`.harness` 는 커밋되지 않는다 — 로그가 없는 것은 어긴 것이 아니지만 통과도 아니다(K-51)."""
        self._prepare("true")
        self.log.unlink()
        r, failed, unverified = self._close()
        self.assertNotIn("EVIDENCE_LOG", failed)
        self.assertIn("EVIDENCE_LOG", unverified)
        self.assertIn("[UNVERIFIED] EVIDENCE_LOG", format_close(r))
        self.assertEqual(r["verdict"], "FAIL", "미검증은 완료가 아니다")

    def test_skipping_the_rerun_is_printed_not_counted_as_pass(self):
        """재실행 대조를 건너뛰면 '기록만 읽은 판정' 이다 — 미검증으로 인쇄하고 done 을 선언하지 않는다."""
        self._prepare("true")
        r, _f, unverified = self._close(rerun=False)
        self.assertIn("REQUIRED_CHECK_RERUN", unverified)
        self.assertNotIn("[PASS] REQUIRED_CHECK_RERUN", format_close(r))
        self.assertEqual(r["verdict"], "FAIL")

    def test_a_check_declared_unrerunnable_is_unverified_with_its_reason(self):
        """부작용·비결정 때문에 다시 돌릴 수 없는 검사는 검증 계획이 선언한다. 막지 않고 드러낸다 —
        선언했다고 통과가 되지는 않는다."""
        self._prepare("true")
        fm, body = frontmatter.read(self.spec)
        frontmatter.write(self.spec, fm, body.replace(
            '    command: "true"', '    command: "true"\n    rerun: false\n    rerun_reason: "배포는 두 번 하지 않는다"'))
        r, _f, unverified = self._close()
        self.assertIn("REQUIRED_CHECK_RERUN", unverified)
        self.assertIn("배포는 두 번 하지 않는다", format_close(r))
        self.assertEqual(r["verdict"], "FAIL")

    def test_an_honest_run_still_closes(self):
        """세 겹을 붙여도 실제로 실행하고 통과한 단위는 그대로 done 이 된다 — 검사를 막히게 하지 않았다."""
        self._prepare("true")
        r, failed, unverified = self._close()
        self.assertEqual((failed, unverified), (set(), set()), r["checks"])
        self.assertEqual(r["verdict"], "PASS")
        text = format_close(r)
        for cid in ("REQUIRED_CHECK", "EVIDENCE_LOG", "REQUIRED_CHECK_RERUN", "CHECK_PLAN_COMMITTED"):
            self.assertIn(f"[PASS] {cid}", text)

    def test_the_raw_log_seals_the_product_identity(self):
        """evidence yaml 의 head_sha·dirty_tree_hash 만 손으로 고치면 로그의 봉인 줄과 어긋난다(4차 리뷰 구멍 B 의 한 겹)."""
        self._prepare("true")
        path = self.spec.parent / "evidence" / "run-a.yaml"
        rec = load_yaml(path)
        cmd = rec["commands"][0]
        self.assertEqual(cmd["head_sha"], rec["head_sha"])
        self.assertEqual(cmd["dirty_tree_hash"], rec["dirty_tree_hash"])
        log = (self.root / cmd["log"]).read_text(encoding="utf-8")
        self.assertIn(f"--- head {rec['head_sha']} ---", log)
        self.assertIn(f"--- tree {rec['dirty_tree_hash']} ---", log)
        r, failed, _u = self._close()
        self.assertEqual(r["verdict"], "PASS", r["checks"])
        rec["commands"][0]["dirty_tree_hash"] = "0" * 64
        path.write_text(dump_yaml(rec), encoding="utf-8")
        r, failed, _u = self._close()
        self.assertIn("EVIDENCE_LOG", failed, r["checks"])
        self.assertIn("산출물 식별이 손으로 고쳐졌다", format_close(r))

    def test_editing_the_approved_check_plan_is_rejected(self):
        """재실행 대조를 붙이자 위조가 한 겹 옆으로 갔다 — 실패하는 검사를 지우고 통과하는 검사로 바꾼 뒤
        그것을 진짜로 실행하면 기록·로그·재실행이 전부 맞는다. 고쳐진 것은 증거가 아니라 주장이다.
        `docs/work/<unit>/` 는 신선도 계산에서 제외돼 있어 이 편집은 어디에도 걸리지 않았다."""
        self._prepare("false")
        fm, body = frontmatter.read(self.spec)
        frontmatter.write(self.spec, fm, body.replace('command: "false"', 'command: "true"'))
        run_required_checks(self.unit, run_name="run-a", project_root=self.root)
        r, failed, _u = self._close()
        self.assertIn("CHECK_PLAN_COMMITTED", failed, r["checks"])
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("승인 커밋", format_close(r))
        self.assertIn("의 것과 다르다", format_close(r))


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
        body = body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS).replace('command: "채움"', 'command: "true"')
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
        self._defensive("run-test")
        self.review = self.spec.parent / "review"
        self.review.mkdir()

    def _defensive(self, run):
        """검토자를 띄운 쪽이 검토 전후에 남기는 방어 검사(RUNBOOK §4) — 이 두 기록이 검토 시점의 산출물이다."""
        for label in ("review-tree-before", "review-tree-after"):
            run_command(self.unit, "git status --porcelain", run_name=run, label=label, project_root=self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def _envelope(self, verdict="PASS", run="run-test", **over):
        """실제 계약 산출물을 가리키는 봉투. sha256 은 손으로 쓰지 않고 그 파일에서 읽는다 —
        테스트가 손으로 쓴 값을 표준으로 박아 두면 느슨한 계약이 고정된다.
        검토자는 명령을 실행하지 않으므로 checks 는 비어 있다(core/roles/reviewer.yaml).
        `run` 은 이 봉투가 속한 검토 run — 그 run 의 계약(`task/<run>-reviewer.json`)과 증거(`evidence/<run>.yaml`)를 가리킨다."""
        task_rel = f"docs/work/{self.unit}/task/{run}-reviewer.json"
        task_path = self.root / task_rel
        task_sha = sha256_file(task_path) if task_path.is_file() else self.task_sha
        env = {
            "schema": "romeo/result-envelope@0.1.0",
            "unit_id": self.unit,
            "role": "reviewer",
            "task_envelope_ref": {"path": task_rel, "sha256": task_sha},
            "checks": [],
            "gate_verdict": verdict,
            "blocked_reason": None,
            "findings": [],
            "evidence_ref": f"docs/work/{self.unit}/evidence/{run}.yaml",
        }
        env.update(over)
        return with_fail_reasons(env)

    def _write_review(self, name, data, record=True):
        """검토 봉투를 남긴다. 기본은 하네스 명령(`review record`)으로 — 봉투를 쓰고 그 sha256 을 검토 run 의 증거에 봉인한다.
        손으로 쓴 봉투(기록 없음)가 필요한 테스트만 record=False 다."""
        if record and name.endswith("-reviewer.json"):
            run = name[:-len("-reviewer.json")]
            # 원본은 제외 경로(.harness/) 안에 둔다 — 저장소 루트에 두면 미추적 파일이 생겨 검사 기록의 트리가 바뀐다(그 검사가 실제로 잡았다).
            src = self.root / ".harness" / "review-src" / f"{name}.src"
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            record_review_envelope(self.unit, run, src, project_root=self.root)
            return
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
        """같은 산출물에 PASS 와 FAIL 이 함께 있으면 FAIL 이 이긴다 — 두 번째 검토 run(방어 검사·계약·기록 전부 정식)."""
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        self._defensive("run-r2")
        write_envelope(self.unit, "reviewer", project_root=self.root, base_sha=self.approval_sha, run_name="run-r2")
        self._write_review("run-r2-reviewer.json", self._envelope(
            "FAIL", run="run-r2", evidence_ref=f"docs/work/{self.unit}/evidence/run-test.yaml"))
        ids, r = self._failed()
        self.assertIn("REVIEW_VERDICT", ids, r["checks"])
        self.assertIn("run-r2-reviewer.json", self._row(r, "REVIEW_VERDICT")["detail"])

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
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "REVIEW_VERDICT")     # 어느 산출물을 본 판정인지 모른다 — FAIL 도 PASS 도 아닌 미검증
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

    # ── 봉투의 주장과 증거를 대조한다 (4차 리뷰 구멍 B) ─────────────────────────
    def test_close_uses_the_same_claim_check_as_the_parity_gate(self):
        """구멍 B 의 규칙은 한 곳(`close._evidence_anchor`)에 있고 종료 검사도 그것을 지나간다.
        실행된 적 없는 검사를 실은 봉투는 역할 계약뿐 아니라 **증거 대조**에서도 걸린다 —
        규칙이 두 벌이 되면 느슨한 쪽이 done 을 만든다(K-63)."""
        self._write_review("run-test-reviewer.json", self._envelope(
            checks=[{"id": "check-1", "command": "pytest -q tests/", "exit_code": 0}]))
        ids, r = self._failed()
        self.assertIn("REVIEW_EVIDENCE_ANCHORED", ids, r["checks"])
        self.assertIn("실행 기록이 없다", self._detail(r, "REVIEW_EVIDENCE_ANCHORED"))
        self.assertIn("REVIEW_ROLE_CONTRACT", ids)
        self.assertEqual(r["verdict"], "FAIL")

    def test_task_contract_copied_outside_the_units_task_place_is_rejected(self):
        """앵커가 파일 이름이 아니라 바이트에 묶여 있어 진짜 계약을 어디로 복사해 가리켜도 통과했다.
        증거 포인터와 같은 자리 규약(K-62)을 계약 포인터에도 건다."""
        copied = self.root / "계약복사본.json"
        copied.write_bytes(self.task_path.read_bytes())
        self._write_review("run-test-reviewer.json", self._envelope(
            task_envelope_ref={"path": "계약복사본.json", "sha256": self.task_sha}))
        ids, r = self._failed()
        self.assertIn("REVIEW_TASK_ANCHORED", ids)
        self.assertIn("밖이다", self._detail(r, "REVIEW_TASK_ANCHORED"))
        self._assert_unverified(r, "REVIEW_BASE_SHA")

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

    # ── 검토 판정은 현재 산출물에 대한 것만 센다(체크리스트 41 · D-73 의 close 적용) ────────
    def _new_product(self, run_name, filename="y.txt"):
        """산출물을 바꾸고(새 파일 커밋) 그 위에서 검사를 다시 기록한다 — 새 evidence 의 head_sha 가 달라진다.
        새 run 의 검토자 계약도 만든다(RUNBOOK §6.6 2번) — 검토 봉투는 자기 run 의 계약과 증거에 묶인다."""
        (self.root / filename).write_text("more\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", f"impl {filename}", cwd=self.root)
        run_command(self.unit, "true", run_name=run_name, project_root=self.root)
        self._defensive(run_name)
        write_envelope(self.unit, "reviewer", project_root=self.root, base_sha=self.approval_sha, run_name=run_name)
        return f"docs/work/{self.unit}/evidence/{run_name}.yaml"

    def _row(self, r, cid):
        return next(c for c in r["checks"] if c["id"] == cid)

    def test_a_fail_on_a_superseded_product_does_not_block_when_the_current_product_has_a_pass(self):
        """검토자의 판정은 자기가 본 산출물의 함수다(D-73). 고친 뒤 새 산출물이 PASS 를 받았으면 옛 산출물의 FAIL 은
        이 close 의 대상이 아니다 — 그 봉투는 지우지 않는다(동등성 게이트의 관측 표본이다)."""
        self._write_review("run-test-reviewer.json", self._envelope("FAIL", findings=[{"summary": "옛 산출물의 결함"}]))
        self._new_product("run-two")
        self._write_review("run-two-reviewer.json", self._envelope("PASS", run="run-two"))
        ids, r = self._failed()
        self.assertNotIn("REVIEW_VERDICT", ids, r["checks"])
        self.assertEqual(r["verdict"], "PASS", r["checks"])
        sup = self._row(r, "REVIEW_SUPERSEDED")
        self.assertEqual(sup["level"], "warning")
        self.assertIn("run-test-reviewer.json", sup["detail"])
        self.assertIn("FAIL", sup["detail"])
        self.assertIn("옛 산출물의 결함", sup["detail"], "뺀 판정의 findings 가 사람에게 보여야 한다")
        self.assertNotIn("run-test-reviewer.json", self._row(r, "REVIEW_VERDICT")["detail"])
        # PASS 가 1건뿐이면 D-74 의 표본 요구에 못 미친다 — 막지 않고 WARN 으로 드러낸다(D-75 미확정).
        sample = self._row(r, "REVIEW_SAMPLE")
        self.assertEqual(sample["level"], "warning")
        self.assertIn("D-75", sample["detail"])

    def test_a_pass_on_a_superseded_product_does_not_close_the_current_one(self):
        """이전에는 통과하던 구멍이다 — 옛 산출물의 PASS 하나로 새 산출물이 닫혔다."""
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        self._new_product("run-two")
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "REVIEW_VERDICT")
        self.assertIn("검토가 아직 없다", self._row(r, "REVIEW_VERDICT")["detail"])
        self.assertIn("run-test-reviewer.json", self._row(r, "REVIEW_SUPERSEDED")["detail"])

    def test_rerunning_the_checks_without_changing_the_product_keeps_the_standing_fail(self):
        """검사만 다시 기록하는 것으로는 FAIL 을 벗어날 수 없다 — 산출물(head_sha·dirty_tree_hash)이 같으면 같은 판정 대상이다."""
        self._write_review("run-test-reviewer.json", self._envelope("FAIL"))
        run_command(self.unit, "true", run_name="run-two", project_root=self.root)
        ids, r = self._failed()
        self.assertIn("REVIEW_VERDICT", ids)
        self.assertNotIn("REVIEW_SUPERSEDED", [c["id"] for c in r["checks"]])

    def test_an_envelope_whose_product_cannot_be_read_is_unverified_not_passed_over(self):
        """산출물을 식별하지 못하는 판정은 지나간 것으로도 현재 것으로도 접지 않는다 — 미검증이고 done 을 막는다(K-51).
        동등성 판정이 같은 봉투를 구조 오류로 빼는 것과 같은 강도다(K-63)."""
        self._write_review("blocked-reviewer.json", self._envelope(
            "BLOCKED", blocked_reason="BLOCKED_CAPABILITY", evidence_ref=None))
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "REVIEW_VERDICT")
        self.assertIn("blocked-reviewer.json", self._row(r, "REVIEW_VERDICT")["detail"])

    def test_retargeting_evidence_ref_cannot_move_a_verdict_to_another_product(self):
        """설계 검토가 재현한 가장 싼 위조: 증거는 건드리지 않고 검토 봉투의 evidence_ref 문자열만 옛 run 으로 돌리면
        FAIL 이 낡은 것으로 빠지고, 옛 PASS 를 현재 run 으로 돌리면 현재 PASS 가 된다. 판정이 본 산출물은 봉투의 포인터가
        아니라 **검토 run 자신의 증거**(방어 검사 기록)에서 읽고, 포인터의 산출물은 그것과 같아야 한다."""
        old_ref = f"docs/work/{self.unit}/evidence/run-test.yaml"
        self._new_product("run-two")
        # FAIL 은 run-two 의 검토인데 evidence_ref 만 옛 run 을 가리킨다 → 낡은 것이 아니라 미검증이다.
        self._write_review("run-two-reviewer.json", self._envelope("FAIL", run="run-two", evidence_ref=old_ref))
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "REVIEW_VERDICT")
        self.assertIn("검토 run run-two 이 기록한 산출물", self._row(r, "REVIEW_VERDICT")["detail"])
        self.assertNotIn("REVIEW_SUPERSEDED", [c["id"] for c in r["checks"]])
        # 반대 방향: 옛 run 의 PASS 가 evidence_ref 만 현재 run 으로 돌린다 → 현재 PASS 가 되지 않는다.
        (self.review / "run-two-reviewer.json").unlink()
        self._write_review("run-test-reviewer.json", self._envelope(
            "PASS", evidence_ref=f"docs/work/{self.unit}/evidence/run-two.yaml"))
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "REVIEW_VERDICT")

    def test_a_verdict_under_a_superseded_approval_does_not_count_even_on_the_same_product(self):
        """산출물 식별에는 spec 이 없다(docs/work/<id>/ 는 트리 해시에서 빠진다). 재승인으로 수용 기준이 바뀌어도 산출물은 그대로라,
        이전 승인의 계약으로 낸 PASS 가 현재 판정으로 세이면 새 수용 기준이 검토되지 않은 채 닫힌다."""
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        approve_unit(self.unit, "tester", project_root=self.root, reapprove=True, reason="수용 기준 변경")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "reapprove", cwd=self.root)
        run_command(self.unit, "true", run_name="run-two", project_root=self.root)
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self.assertTrue(self._row(r, "REVIEW_TASK_ANCHORED")["ok"], "이전 승인의 계약도 봉투로 식별은 된다")
        self._assert_unverified(r, "REVIEW_VERDICT")
        self.assertIn("재승인 전 승인", self._row(r, "REVIEW_SUPERSEDED")["detail"])

    def test_a_pass_whose_own_run_has_no_evidence_is_unverified(self):
        """검토 run 의 증거(방어 검사 기록)가 없으면 검토 시점의 산출물을 하네스가 기록하지 않은 것이다 — PASS 로 세지 않는다."""
        write_envelope(self.unit, "reviewer", project_root=self.root, base_sha=self.approval_sha, run_name="run-nolog")
        self._write_review("run-nolog-reviewer.json", self._envelope(
            "PASS", run="run-nolog", evidence_ref=f"docs/work/{self.unit}/evidence/run-test.yaml"))
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "REVIEW_VERDICT")
        self.assertIn("run-nolog", self._row(r, "REVIEW_VERDICT")["detail"])

    # ── 구현 diff 반박 검토(2026-08-29)가 잡은 위조 경로 — 회귀 고정 ───────────────
    def test_editing_the_verdict_word_after_recording_is_caught(self):
        """가장 싼 위조: 정직한 FAIL 봉투에서 gate_verdict 한 단어만 PASS 로 바꾼다. 판정 문자열은 어떤 앵커에도 묶이지 않으므로
        기록 명령이 남긴 sha256 봉인이 유일한 결박이다 — 기록 뒤 바뀐 봉투는 미검증이다."""
        self._write_review("run-test-reviewer.json", self._envelope("FAIL", findings=[{"summary": "결함"}]))
        ids, r = self._failed()
        self.assertIn("REVIEW_VERDICT", ids)
        path = self.review / "run-test-reviewer.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["gate_verdict"], data["findings"] = "PASS", []
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "REVIEW_VERDICT")
        self.assertIn("기록 시점의 값과 다르다", self._row(r, "REVIEW_VERDICT")["detail"])

    def test_a_hand_written_envelope_without_a_record_is_unverified(self):
        """record 명령을 거치지 않은 봉투(손으로 쓴 PASS)는 현재 산출물이어도 판정으로 세지 않는다."""
        self._write_review("run-test-reviewer.json", self._envelope("PASS"), record=False)
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "REVIEW_VERDICT")
        self.assertIn("review-record", self._row(r, "REVIEW_VERDICT")["detail"])

    def test_copying_the_contract_under_the_implementer_run_name_does_not_borrow_its_evidence(self):
        """'검토 run 자신의 증거' 규칙 우회: 검토자 계약을 구현 run 이름으로 복사하면 구현자의 진짜 증거가 '검토 run 의 증거' 가 됐다.
        검토 run 의 증거에는 방어 검사 두 기록이 실재하고 로그와 맞아야 한다 — 구현 run(run-impl)에는 그것이 없다."""
        (self.root / "y.txt").write_text("more\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl y", cwd=self.root)
        run_command(self.unit, "true", run_name="run-impl", project_root=self.root)     # 방어 검사 없는 구현 run
        import shutil
        shutil.copy(self.task_path, self.task_path.parent / "run-impl-reviewer.json")
        self._write_review("run-impl-reviewer.json", self._envelope("PASS", run="run-impl"))
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "REVIEW_VERDICT")
        self.assertIn("방어 검사", self._row(r, "REVIEW_VERDICT")["detail"])

    def test_editing_the_top_level_product_of_the_review_run_is_caught(self):
        """봉인은 명령별 값을 덮는데 판정은 최상위 값을 읽었다 — 최상위 두 줄만 고치면 판정이 다른 산출물로 옮겨졌다.
        최상위 값은 마지막 명령 기록(봉인된 자리)과 같아야 한다."""
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        path = self.spec.parent / "evidence" / "run-test.yaml"
        rec = load_yaml(path)
        rec["dirty_tree_hash"] = "e" * 64
        path.write_text(dump_yaml(rec), encoding="utf-8")
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("EVIDENCE_LOG", ids)
        self.assertIn("봉인되지 않은 자리만 고쳐졌다", self._row(r, "EVIDENCE_LOG")["detail"])

    def test_deleting_the_review_run_log_is_unverified_not_passed(self):
        """봉인 회피: 로그를 지우면 '없는 것은 어긴 것이 아니다' 로 통과하던 자리 — 검토 run 의 방어 검사는 로그로 확인될 때만 인정한다."""
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        import shutil
        shutil.rmtree(self.root / ".harness" / "runs" / self.unit / "run-test")
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "REVIEW_VERDICT")

    def test_stripping_the_seal_lines_from_the_log_is_caught(self):
        """옛 형식 흉내: 기록에는 head/tree 가 있는데 로그에서 봉인 줄만 지우고 log_sha256 을 다시 계산한다 — 어긴 것이다."""
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        path = self.spec.parent / "evidence" / "run-test.yaml"
        rec = load_yaml(path)
        last = rec["commands"][-1]
        log = self.root / last["log"]
        text = "\n".join(ln for ln in log.read_text(encoding="utf-8").splitlines()
                         if not ln.startswith("--- head ") and not ln.startswith("--- tree ")) + "\n"
        log.write_text(text, encoding="utf-8")
        from romeo.util import sha256_bytes
        last["log_sha256"] = sha256_bytes(text.encode("utf-8"))
        path.write_text(dump_yaml(rec), encoding="utf-8")
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("봉인 줄", format_close(r))

    def test_rolling_the_approval_back_in_the_working_tree_is_rejected(self):
        """승인 되돌리기: 재승인이 커밋된 뒤 작업 트리 frontmatter 만 옛 승인으로 되돌리면 옛 승인 커밋이 '승인 커밋' 이 됐다.
        작업 트리의 승인 기록은 HEAD 에 커밋된 것을 포함해야 한다 — 승인은 앞으로만 간다."""
        approve_unit(self.unit, "tester", project_root=self.root, reapprove=True, reason="검사 추가")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "reapprove", cwd=self.root)
        fm, body = frontmatter.read(self.spec)
        old_at = fm["approval_history"][0]["approved_at"]
        fm["approved_at"], fm["approval_history"] = old_at, []
        frontmatter.write(self.spec, fm, body)
        from romeo.docs import approval_commit
        with self.assertRaises(ValueError) as cm:
            approval_commit(self.root, self.unit)
        self.assertIn("어긋난다", str(cm.exception))
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "CHECK_PLAN_COMMITTED")

    def test_a_forged_reapproval_breaks_the_approval_chain_and_is_printed(self):
        """가짜 재승인: approve 명령 없이 approved_at 만 새 값으로 바꿔 커밋하면 그 커밋이 승인 커밋이 된다 — 사슬이 끊긴 것을 경고로 드러낸다.
        (차단은 아니다 — 옛 방식의 재승인도 같은 모양이고, 승인 사건을 기계가 확인할 형태는 사용자 결정이다.)"""
        fm, body = frontmatter.read(self.spec)
        fm["approved_at"] = "2030-01-01T00:00:00+09:00"
        frontmatter.write(self.spec, fm, body)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "forged reapprove", cwd=self.root)
        run_command(self.unit, "true", run_name="run-two", project_root=self.root)
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        chain = [c for c in r["checks"] if c["id"] == "APPROVAL_CHAIN"]
        self.assertEqual(len(chain), 1, r["checks"])
        self.assertEqual(chain[0]["level"], "warning")
        self.assertIn("거치지 않은 승인", chain[0]["detail"])

    def test_a_legacy_envelope_on_an_older_head_is_superseded_with_a_caveat(self):
        """봉인 이전 형식(방어 검사 기록에 명령별 head/tree 없음)의 봉투는 산출물을 증명하지 못한다 — 그러나 증거의 head_sha 가
        지금 HEAD 가 아니면 현재 산출물의 판정일 수 없으므로 낡은 것으로 분류한다(그 근거가 미봉인 값임을 인쇄). 옛 관통의 봉투가
        영원히 close 를 막지 않게 하는 규칙이다."""
        self._write_review("run-test-reviewer.json", self._envelope("FAIL"))
        path = self.spec.parent / "evidence" / "run-test.yaml"
        rec = load_yaml(path)
        for c in rec["commands"]:
            c.pop("head_sha", None); c.pop("dirty_tree_hash", None)          # 옛 형식 흉내
        path.write_text(dump_yaml(rec), encoding="utf-8")
        import shutil
        shutil.rmtree(self.root / ".harness" / "runs" / self.unit / "run-test")   # 로그도 없다(다른 체크아웃에서 모아 온 봉투)
        # 같은 HEAD 를 가리키는 동안은 미검증이다 — 위조 방향(현재 FAIL 을 옛 형식으로 위장)을 막는다.
        ids, r = self._failed()
        self._assert_unverified(r, "REVIEW_VERDICT")
        # 산출물이 새 커밋으로 바뀌면(HEAD 이동) 낡은 것으로 분류된다.
        self._new_product("run-two")
        self._write_review("run-two-reviewer.json", self._envelope("PASS", run="run-two"))
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "PASS", r["checks"])
        sup = self._row(r, "REVIEW_SUPERSEDED")
        self.assertIn("run-test-reviewer.json", sup["detail"])
        self.assertIn("봉인 이전 형식", sup["detail"])

    def test_stripping_seal_values_from_a_sealed_record_is_caught(self):
        """봉인 형식의 기록에서 명령별 값만 지워 옛 형식으로 위장한다 — 로그에 봉인 줄이 남아 있으므로 잡힌다."""
        self._write_review("run-test-reviewer.json", self._envelope("FAIL"))
        path = self.spec.parent / "evidence" / "run-test.yaml"
        rec = load_yaml(path)
        for c in rec["commands"]:
            c.pop("head_sha", None); c.pop("dirty_tree_hash", None)
        path.write_text(dump_yaml(rec), encoding="utf-8")
        self._new_product("run-two")
        self._write_review("run-two-reviewer.json", self._envelope("PASS", run="run-two"))
        ids, r = self._failed()
        self.assertEqual(r["verdict"], "FAIL")
        self._assert_unverified(r, "REVIEW_VERDICT")
        self.assertIn("봉인 값이 지워졌다", self._row(r, "REVIEW_VERDICT")["detail"])

    def test_superseded_envelopes_must_still_be_valid_envelopes(self):
        """낡은 봉투도 봉투다 — 앵커 검사는 산출물과 무관하게 모든 봉투에 걸린다."""
        self._write_review("run-test-reviewer.json", self._envelope(
            "FAIL", task_envelope_ref={"path": f"docs/work/{self.unit}/task/없는계약.json", "sha256": "0" * 64}))
        self._new_product("run-two")
        self._write_review("run-two-reviewer.json", self._envelope("PASS", run="run-two"))
        ids, r = self._failed()
        self.assertIn("REVIEW_TASK_ANCHORED", ids)
        self.assertEqual(r["verdict"], "FAIL")


class TestCloseRequiresFailReasonsOnFail(unittest.TestCase):
    """AC-2 뒷겹 — 종료 검사가 **지금 닫으려는 산출물**의 FAIL 봉투에 사유를 요구한다.

    앞겹(결과 계약 스키마)은 `fail_reasons` 의 값만 본다 — 그 필드가 생기기 전에 기록된 판정에도 같은 스키마가
    걸리므로 조건부 필수를 걸 수 없다(`fixtures/parity` 의 관측 케이스가 이미 `done` 인 단위의 봉투를 읽는다).
    그래서 '사유를 실제로 담았는가' 는 여기서만 요구하고, 대상은 현재 산출물의 FAIL 봉투뿐이다.

    검사 대상 fixture 는 `TestCloseReviewVerdict` 의 것을 그대로 쓴다 — 같은 자리를 두 번 세우면
    두 fixture 가 갈라지는 순간 두 검사가 서로 다른 것을 본다."""

    setUp = TestCloseReviewVerdict.setUp
    tearDown = TestCloseReviewVerdict.tearDown
    _defensive = TestCloseReviewVerdict._defensive
    _envelope = TestCloseReviewVerdict._envelope
    _write_review = TestCloseReviewVerdict._write_review
    _failed = TestCloseReviewVerdict._failed
    _row = TestCloseReviewVerdict._row
    _new_product = TestCloseReviewVerdict._new_product

    CID = "REVIEW_FAIL_REASONS"

    def _close(self):
        return close_unit(self.unit, project_root=self.root, dry_run=True)

    # ── 사유가 없으면 완료를 선언하지 않는다 ────────────────────────────────────
    def test_a_fail_without_the_field_blocks_close(self):
        self._write_review("run-test-reviewer.json",
                           self._envelope("FAIL", fail_reasons=None,
                                          findings=[{"summary": "수용 기준 2번의 근거가 없다"}]))
        ids, r = self._failed()
        self.assertIn(self.CID, ids, r["checks"])
        row = self._row(r, self.CID)
        self.assertEqual(row["level"], "error", row)
        self.assertIn("run-test-reviewer.json", row["detail"])
        self.assertIn("fail_reasons", row["detail"])
        self.assertEqual(r["verdict"], "FAIL")

    def test_a_fail_with_an_empty_list_blocks_close(self):
        """빈 배열은 스키마를 통과한다(앞겹은 값만 본다) — 막는 자리는 여기다."""
        self._write_review("run-test-reviewer.json", self._envelope("FAIL", fail_reasons=[]))
        ids, r = self._failed()
        self.assertIn(self.CID, ids, r["checks"])
        self.assertEqual(r["verdict"], "FAIL")

    # ── 대상이 아닌 것은 막지 않는다 ───────────────────────────────────────────
    def test_a_fail_that_names_its_reason_passes_this_check(self):
        """판정은 여전히 FAIL 이지만 그것을 막는 것은 REVIEW_VERDICT 이지 이 검사가 아니다 —
        두 사실을 한 검사에 묶으면 어느 쪽이 빠졌는지 구분되지 않는다."""
        self._write_review("run-test-reviewer.json",
                           self._envelope("FAIL", fail_reasons=["AC_UNMET"],
                                          findings=[{"summary": "수용 기준 2번의 근거가 없다"}]))
        ids, r = self._failed()
        self.assertNotIn(self.CID, ids, r["checks"])
        self.assertTrue(self._row(r, self.CID)["ok"])
        self.assertIn("REVIEW_VERDICT", ids, "FAIL 판정 자체는 여전히 완료를 막는다")

    def test_pass_and_blocked_envelopes_are_not_asked_for_a_reason(self):
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        r = self._close()
        self.assertTrue(self._row(r, self.CID)["ok"], r["checks"])
        self.assertEqual(r["verdict"], "PASS", r["checks"])

    def test_a_blocked_envelope_is_not_asked_for_a_reason(self):
        """보지 못한 것에는 사유 코드가 없다 — BLOCKED 를 FAIL 로 대신 적지 않는 것과 같은 이유다."""
        self._write_review("run-test-reviewer.json",
                           self._envelope("BLOCKED", blocked_reason="BLOCKED_CAPABILITY"))
        ids, r = self._failed()
        self.assertNotIn(self.CID, ids, r["checks"])
        self.assertTrue(self._row(r, self.CID)["ok"])
        self.assertIn("REVIEW_VERDICT", ids)

    def test_a_superseded_fail_is_not_asked_for_a_reason(self):
        """다른 산출물을 본 옛 판정에 사유를 소급해 요구하지 않는다 — 그러면 이 검사가 하는 말이
        '옛 판정이 옛 형식이다' 로 바뀌고, 고칠 수 없는 것으로 완료를 막게 된다."""
        self._write_review("run-test-reviewer.json",
                           self._envelope("FAIL", fail_reasons=None, findings=[{"summary": "옛 산출물의 결함"}]))
        self._new_product("run-two")
        self._write_review("run-two-reviewer.json", self._envelope("PASS", run="run-two"))
        r = self._close()
        self.assertTrue(self._row(r, self.CID)["ok"], r["checks"])
        self.assertEqual(self._row(r, "REVIEW_SUPERSEDED")["level"], "warning")
        self.assertEqual(r["verdict"], "PASS", r["checks"])

    def test_the_check_is_always_printed(self):
        """검사가 인쇄되지 않는 것과 통과한 것은 다르다 — 없는 검사는 사람이 통과로 읽는다."""
        self._write_review("run-test-reviewer.json", self._envelope("PASS"))
        self.assertIn(self.CID, {c["id"] for c in self._close()["checks"]})


class TestMultilineCommandAnchor(unittest.TestCase):
    """개행을 담은 명령이 원시 로그 앵커 대조를 통과하는가 (AC-9 · Q-25 다음의 다섯 번째 결함).

    `command_log_state` 는 로그의 **첫 물리 줄**만 기록된 명령과 비교했다. 그런데 로그는 명령 전체를
    `$ {command}` 로 한 번에 쓰므로, 명령이 개행을 담으면 첫 줄은 그 명령의 **첫 조각**일 뿐이고
    비교는 언제나 다르다 — 여러 줄 명령은 **어떤 구현으로도** `EVIDENCE_ANCHORED` 를 통과할 수 없었다.
    2026-08-31 이 단위의 2회차 관통이 정확히 여기서 막혔다(검사 14건이 전부 exit 0 인데도
    `close` 가 `EVIDENCE_LOG`·`EVIDENCE_ANCHORED` 두 항목을 FAIL 로 냈다).

    고치는 방향은 대조를 **약하게 만드는 것이 아니라 올바른 자리와 비교하는 것**이다 —
    `$ ` 뒤부터 `--- stdout ---` 표지 앞까지가 로그가 적은 명령 헤더다. 그래서 이 클래스는 짝으로 고정한다:

      ① 여러 줄 명령이 통과한다
      ② 로그를 손으로 고치면 **여전히 거부된다** — 봉인(`log_sha256`)까지 다시 맞춰 놓아도 명령 헤더에서 걸린다

    ② 가 없으면 ① 은 "대조를 지웠다" 와 구별되지 않는다."""

    MULTILINE = "python3 -c \"import sys\nfor i in (1, 2):\n    print(i)\n\""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        out = route({"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        res = create_unit(out, "여러 줄 명령 T0", "multiline-t0", "개행을 담은 검사 명령",
                          project_root=self.root, date="20260901")
        self.unit = res["id"]

    def tearDown(self):
        self.tmp.cleanup()

    def _record(self, command):
        """명령을 실제로 실행해 기록을 남기고 (기록, 로그 경로) 를 준다."""
        r = run_command(self.unit, command, run_name="run-a", project_root=self.root)
        rec = r["command"]
        return rec, self.root / rec["log"]

    def _reseal(self, log, rec, text):
        """로그를 고치고 **봉인까지 다시 맞춘다** — 위조 중 가장 성실한 것이다.

        여기까지 맞춘 위조를 잡는 것은 명령 헤더 대조뿐이므로, 이 도우미가 있어야 ② 가 성립한다."""
        log.write_text(text, encoding="utf-8")
        rec = dict(rec)
        rec["log_sha256"] = sha256_file(log)
        return rec

    # ── ① 여러 줄 명령이 통과한다 ───────────────────────────────────────────
    def test_a_multiline_command_passes_the_anchor(self):
        rec, log = self._record(self.MULTILINE)
        self.assertIn("\n", rec["command"], "표본이 개행을 담고 있어야 이 테스트가 의미가 있다")
        state, why = command_log_state(self.root, rec)
        self.assertIs(state, True, why)

    def test_a_single_line_command_still_passes(self):
        rec, _log = self._record("echo hello")
        state, why = command_log_state(self.root, rec)
        self.assertIs(state, True, why)

    def test_the_first_marker_ends_the_header_not_a_later_one(self):
        """명령의 **출력**이 표지와 같은 줄을 뱉어도 헤더가 늘어나지 않는다.

        종료 코드는 마지막 줄이 이기지만(기록자가 마지막에 쓴다) 헤더는 **첫** 표지에서 끝난다 —
        기록자가 그 줄을 먼저 쓰기 때문이다. 방향을 반대로 잡으면 출력이 헤더를 오염시킨다."""
        rec, _log = self._record("echo '--- stdout ---'")
        state, why = command_log_state(self.root, rec)
        self.assertIs(state, True, why)

    # ── ② 손으로 고친 로그는 여전히 거부된다 ────────────────────────────────
    def test_editing_the_log_breaks_the_seal(self):
        rec, log = self._record(self.MULTILINE)
        log.write_text(log.read_text(encoding="utf-8").replace("print(i)", "print(0)"), encoding="utf-8")
        state, why = command_log_state(self.root, rec)
        self.assertIs(state, False, why)
        self.assertIn("log_sha256", why)

    def test_a_resealed_edit_of_the_command_header_is_still_refused(self):
        """봉인까지 맞춰도 거부된다 — 이 자리가 느슨해지면 위조가 통과한다."""
        rec, log = self._record(self.MULTILINE)
        rec = self._reseal(log, rec, log.read_text(encoding="utf-8").replace("print(i)", "print(0)"))
        state, why = command_log_state(self.root, rec)
        self.assertIs(state, False, why)
        self.assertIn("손으로 고쳐졌다", why)

    def test_a_resealed_drop_of_a_header_line_is_still_refused(self):
        """헤더의 한 줄을 통째로 지운 것도 잡는다 — '첫 줄만 같으면 통과' 로 돌아가지 않는다."""
        rec, log = self._record(self.MULTILINE)
        lines = log.read_text(encoding="utf-8").split("\n")
        del lines[1]
        rec = self._reseal(log, rec, "\n".join(lines))
        state, why = command_log_state(self.root, rec)
        self.assertIs(state, False, why)
        self.assertIn("손으로 고쳐졌다", why)

    def test_a_resealed_edit_of_the_first_line_is_still_refused(self):
        """종전 구현이 유일하게 잡던 자리 — 고친 뒤에도 그대로 잡혀야 한다(회귀)."""
        rec, log = self._record(self.MULTILINE)
        lines = log.read_text(encoding="utf-8").split("\n")
        lines[0] = "$ python3 -c \"import os"
        rec = self._reseal(log, rec, "\n".join(lines))
        state, why = command_log_state(self.root, rec)
        self.assertIs(state, False, why)
        self.assertIn("손으로 고쳐졌다", why)

    def test_a_resealed_exit_code_edit_is_still_refused(self):
        """다른 겹이 살아 있는지 — 명령 헤더만 보게 되지 않았는지 확인한다."""
        rec, log = self._record(self.MULTILINE)
        rec = self._reseal(log, rec, log.read_text(encoding="utf-8").replace("--- exit 0 ---", "--- exit 1 ---"))
        state, why = command_log_state(self.root, rec)
        self.assertIs(state, False, why)
        self.assertIn("종료 코드", why)

    def test_a_resealed_log_without_the_stdout_marker_is_not_a_pass(self):
        """표지 줄을 **지우고** 명령을 바꾼 뒤 봉인까지 맞춘 로그 — 대조를 건너뛰면 이것이 통과한다(2026-09-01 검토 F2).

        헤더의 경계는 `--- stdout ---` 표지다. 그 표지가 없으면 헤더를 읽을 수 없는데, 종전에는 그때
        명령 대조를 **조용히 건너뛰고** 나머지 겹(종료 코드·봉인)만 봤다. 종료 코드 줄은 그대로 두고
        표지만 지운 뒤 `$ ` 줄에 다른 명령을 적고 `log_sha256` 을 다시 계산하면, 위조된 명령이 `True` 를 받았다.
        같은 우회는 이 단위가 만든 것이 아니다 — 첫 줄만 비교하던 옛 구현에서도 `$ ` 접두만 지우면 통과했다.

        고친 뒤의 판정은 `False` 가 아니라 **`None`(미검증)** 이다: 이 로그가 위조라는 것을 이 겹은 말할 수 없고,
        말할 수 있는 것은 '대조가 성립하지 않았다' 뿐이기 때문이다. 종료 코드 줄이 없을 때와 같은 처리이고,
        종료 검사는 미검증을 통과로 세지 않으므로(K-51) 그 로그는 더 이상 조용히 넘어가지 않는다."""
        rec, log = self._record(self.MULTILINE)
        forged = [ln for ln in log.read_text(encoding="utf-8").split("\n") if ln != "--- stdout ---"]
        forged[0] = "$ python3 -c \"print('pwned')\""
        rec = self._reseal(log, rec, "\n".join(forged))
        state, why = command_log_state(self.root, rec)
        self.assertIsNot(state, True, why)
        self.assertIsNone(state, why)
        self.assertIn("명령 헤더가 없다", why)


class TestTemplateBlankGuidanceToken(unittest.TestCase):
    """spec 템플릿의 「빈칸 금지」 안내가 **남아 있으면서** 자기 검사에 걸리지 않는가 (AC-3 · Q-20).

    종전 템플릿의 안내 줄은 종료 검사의 미완료 토큰을 **글자 그대로** 인용했다. 그래서 그 템플릿으로
    만든 문서는 작성자가 빈칸을 다 채워도 안내 줄 하나 때문에 `NO_OPEN_LOOP` 에 걸렸고, 닫힌 단위들은
    전부 그 줄을 손으로 지워서 넘겼다 — 지워야 통과하는 안내문이었다.

    고치는 방향은 검사를 무르게 하는 것이 아니라 **안내문이 토큰을 인용하지 않게 쓰는 것**이다.
    그래서 세 방향을 함께 고정한다:

      ① 안내 줄이 템플릿에 그대로 하나 있고, 그 줄이 토큰을 글자 그대로 담지 않는다
      ② 그 템플릿으로 만든 문서에서 **작성자가 채우는 빈칸만** 채우면 `NO_OPEN_LOOP` 가 통과한다
      ③ 안내 줄에 토큰을 되돌려 놓으면 `NO_OPEN_LOOP` 가 **다시 걸린다**(음성 방향)

    ③ 이 없으면 ①·② 는 "검사 쪽을 지웠다" 와 구별되지 않는다. 그리고 ② 를 채울 때 안내 줄까지 함께
    치환하면(사람이 손으로 하던 바로 그 일이다) 템플릿을 되돌려도 통과하므로, 채우는 도우미는 그 줄을 건드리지 않는다."""

    GUIDE = "빈칸 금지"
    TOKEN = "NEEDS_INPUT"
    TEMPLATE = HARNESS_ROOT / "core/templates/tech-spec.md"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        out = route({"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        # 제목·설명에 안내 줄의 글자를 쓰지 않는다 — 표본 자신이 그 줄을 늘리면 ② 가 무엇을 셌는지 알 수 없다.
        res = create_unit(out, "안내문 토큰 T0", "blank-guide-t0", "안내 문구가 자기 검사에 걸리던 자리",
                          project_root=self.root, date="20260901")
        self.unit = res["id"]
        self.spec = Path(res["files"][0])

    def tearDown(self):
        self.tmp.cleanup()

    def _guidance(self, text):
        return [ln for ln in text.split("\n") if self.GUIDE in ln]

    def _fill_but_keep_the_guidance(self):
        """작성자가 채우는 빈칸만 채운다 — **안내 줄은 건드리지 않는다.**"""
        fm, body = frontmatter.read(self.spec)
        kept = [ln if self.GUIDE in ln else ln.replace(self.TOKEN, "채움") for ln in body.split("\n")]
        body = "\n".join(kept).replace(SCOPE_TODO, SCOPE_PATHS)
        body = body.replace('command: "채움"', 'command: "true"').replace("- [ ] AC-1", "- [x] AC-1")
        frontmatter.write(self.spec, fm, body)

    def _prepare(self):
        """승인 → 구현 → 증거까지 만든다. `NO_OPEN_LOOP` 는 evidence 가 있어야 인쇄되기 때문이다."""
        self._fill_but_keep_the_guidance()
        approve_unit(self.unit, "tester", project_root=self.root)
        (self.root / "x.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl", cwd=self.root)
        run_command(self.unit, "true", run_name="run-test", label="check-1", project_root=self.root)

    def _open_loop_row(self):
        r = close_unit(self.unit, project_root=self.root, dry_run=True)
        return next(c for c in r["checks"] if c["id"] == "NO_OPEN_LOOP")

    # ── ① 안내는 남고, 토큰은 인용하지 않는다 ────────────────────────────────
    def test_the_template_keeps_the_guidance_without_quoting_the_token(self):
        lines = self._guidance(self.TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(len(lines), 1, lines)
        self.assertNotIn(self.TOKEN, lines[0], lines[0])

    def test_a_created_document_still_carries_the_guidance(self):
        """안내를 지워서 통과시키는 것은 AC-3 을 만족하지 않는다 — 문서에 그 줄이 실제로 실린다."""
        self.assertEqual(len(self._guidance(frontmatter.read(self.spec)[1])), 1)

    # ── ② 빈칸만 채우면 종료 검사를 통과한다 ────────────────────────────────
    def test_filling_only_the_authors_blanks_passes_the_open_loop_check(self):
        self._prepare()
        row = self._open_loop_row()
        self.assertTrue(row["ok"], row)
        self.assertIn(self.GUIDE, frontmatter.read(self.spec)[1], "안내 줄을 지우고 통과한 것이 아니어야 한다")

    # ── ③ 토큰을 되돌리면 다시 걸린다 ───────────────────────────────────────
    def test_putting_the_token_back_into_the_guidance_fails_again(self):
        """종전 템플릿으로 되돌린 모양 — 검사 쪽을 무르게 만들어 통과시킨 것이 아님을 고정한다."""
        self._prepare()
        self.assertTrue(self._open_loop_row()["ok"])
        fm, body = frontmatter.read(self.spec)
        lines = body.split("\n")
        i = next(n for n, ln in enumerate(lines) if self.GUIDE in ln)
        lines[i] = f"**{self.GUIDE}** — 채우지 않은 칸은 `{self.TOKEN}` 과 똑같이 취급한다."
        frontmatter.write(self.spec, fm, "\n".join(lines))
        row = self._open_loop_row()
        self.assertFalse(row["ok"], row)
        self.assertIn("1곳", row["detail"])


class TestValidateDirectoryTarget(unittest.TestCase):
    """`romeo validate` 에 **폴더**를 줄 수 있는가, 그리고 경계에서 크래시하지 않는가 (AC-4 · Q-22).

    종전에는 폴더를 주면 `IsADirectoryError` 트레이스백이 그대로 올라왔다 — 사용법 안내가 아니라 크래시였고,
    작업 단위 하나만 검사하려는 자연스러운 사용이 막혀 있었다.

    '트레이스백이 아니다' 만 보면 **아무것도 검사하지 않는 구현**도 통과한다. 그래서 폴더를 준 실행이
    그 폴더 안 문서를 실제로 판정했다는 것(망가뜨리면 FAIL 과 종료 코드 1 이 된다)까지 함께 본다.
    경계도 같이 고정한다: 파일 인자 · 없는 경로 · 문서가 없는 폴더 — 셋 다 트레이스백 없이 답해야 하고,
    특히 마지막은 **저장소 전체로 번지지 않아야** 한다(사용자가 지목하지 않은 문서의 판정이 종료 코드에 섞인다)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        out = route({"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        res = create_unit(out, "폴더 인자 T0", "validate-dir-t0", "폴더를 주면 트레이스백이 올라오던 자리",
                          project_root=self.root, date="20260901")
        self.unit = res["id"]
        self.spec = Path(res["files"][0])
        self.udir = self.spec.parent

    def tearDown(self):
        self.tmp.cleanup()

    def _validate(self, *paths):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["validate", *[str(p) for p in paths]])
        text = out.getvalue() + err.getvalue()
        self.assertNotIn("Traceback", text, text)
        return rc, text

    def test_a_unit_folder_is_expanded_and_checked(self):
        rc, text = self._validate(self.udir)
        self.assertEqual(rc, 0, text)
        self.assertIn(str(self.spec), text)
        self.assertIn("[PASS]", text)

    def test_the_folder_run_actually_judges_the_document(self):
        """폴더를 펴기만 하고 판정하지 않는 구현과 구별한다 — 망가진 문서는 FAIL 과 종료 코드 1 이다."""
        self.spec.write_text("frontmatter 가 없는 문서\n", encoding="utf-8")
        rc, text = self._validate(self.udir)
        self.assertEqual(rc, 1, text)
        self.assertIn("[FAIL]", text)

    def test_a_file_argument_still_works(self):
        """폴더를 받게 하면서 파일 인자가 깨지지 않았는지 — 종전의 유일한 사용법이다(회귀)."""
        rc, text = self._validate(self.spec)
        self.assertEqual(rc, 0, text)
        self.assertIn(str(self.spec), text)

    def test_only_document_files_are_picked_up(self):
        """작업 단위 폴더에는 계약·증거·결과가 함께 산다 — 문서 이름인 것만 검사 대상이다."""
        (self.udir / "notes.md").write_text("frontmatter 가 없는 메모\n", encoding="utf-8")
        (self.udir / "task").mkdir(exist_ok=True)
        (self.udir / "task" / "run-a.json").write_text("{}\n", encoding="utf-8")
        rc, text = self._validate(self.udir)
        self.assertEqual(rc, 0, text)
        self.assertNotIn("notes.md", text)
        self.assertNotIn("run-a.json", text)

    def test_a_missing_path_is_reported_not_a_traceback(self):
        rc, text = self._validate(self.root / "없는-경로")
        self.assertEqual(rc, 1, text)
        self.assertIn("NOT_A_FILE", text)

    def test_a_folder_without_documents_does_not_spread_to_the_repository(self):
        """빈 폴더를 준 실행이 저장소 전체 검사로 번지면, 사용자가 지목하지 않은 문서가 종료 코드를 만든다."""
        empty = self.root / "빈폴더"
        empty.mkdir()
        rc, text = self._validate(empty)
        self.assertEqual(rc, 0, text)
        self.assertIn("검사할 문서가 없다", text)
        self.assertNotIn(str(self.spec), text)


if __name__ == "__main__":
    unittest.main()
