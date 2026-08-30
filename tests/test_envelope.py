"""작업 계약(TaskEnvelope) 생성 — 승인된 spec.md 와 라우터 출력에서 계산한다.

핵심 계약 두 가지만 검사한다: (1) 같은 입력이면 바이트 단위로 같은 계약이 나온다,
(2) 워커가 볼 수 없는 승인(커밋되지 않은 승인)으로는 계약을 만들지 않는다(D-a)."""
import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from romeo import HARNESS_ROOT, frontmatter
from romeo.cli import main
from romeo.docs import approve_unit, create_unit
from romeo.envelope import build_envelope, envelope_text, write_envelope
from romeo.evidence import run_command
from romeo.policy import route
from romeo.schema import validate
from romeo.util import load_json, sha256_file

# 작업 계약의 쓰기 상한은 spec 의 「변경 범위」에서 온다(체크리스트 34) — 각 `·` 항목의 첫 백틱이 그 항목의 경로다.
# 템플릿의 NEEDS_INPUT 자리에 실제 경로가 없으면 계약을 만들지 않는다(K-66).
SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"
SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `scripts/` · `README.md`"



def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


class TestEnvelope(unittest.TestCase):
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
        res = create_unit(out, "계약 테스트", "envelope-t0", "작업 계약 생성",
                          project_root=self.root, date="20260828")
        self.unit = res["id"]
        self.spec = Path(res["files"][0])
        fm, body = frontmatter.read(self.spec)
        body = body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS).replace('command: "채움"', 'command: "python3 -m unittest tests.test_envelope"')
        frontmatter.write(self.spec, fm, body)

    def tearDown(self):
        self.tmp.cleanup()

    def _approve_and_commit(self):
        approve_unit(self.unit, "tester", project_root=self.root)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)
        return git("rev-parse", "HEAD", cwd=self.root)

    def _build(self, role="implementer", **kw):
        return build_envelope(self.unit, role, project_root=self.root, **kw)

    # ── 결정성 ────────────────────────────────────────────────────────────────
    def test_same_input_gives_byte_identical_contract(self):
        sha = self._approve_and_commit()
        a = self._build(base_sha=sha)
        b = self._build(base_sha=sha)
        self.assertEqual(envelope_text(a), envelope_text(b))
        self.assertEqual(a, b)
        first = write_envelope(self.unit, "implementer", project_root=self.root, base_sha=sha)
        text = Path(first["path"]).read_text(encoding="utf-8")
        second = write_envelope(self.unit, "implementer", project_root=self.root, base_sha=sha)
        self.assertEqual(first["path"], second["path"])
        self.assertEqual(text, Path(second["path"]).read_text(encoding="utf-8"))

    def test_contract_reads_the_committed_spec_not_the_working_tree(self):
        sha = self._approve_and_commit()
        before = self._build(base_sha=sha)
        fm, body = frontmatter.read(self.spec)
        frontmatter.write(self.spec, fm, body.replace("- [ ] AC-1", "- [x] AC-1"))
        after = self._build(base_sha=sha)
        self.assertEqual(before, after)
        self.assertNotEqual(after["spec_ref"]["sha256"], sha256_file(self.spec))

    # ── 내용 ──────────────────────────────────────────────────────────────────
    def test_envelope_matches_schema_and_spec(self):
        sha = self._approve_and_commit()
        env = self._build(base_sha=sha)
        schema = load_json(HARNESS_ROOT / "core/schemas/task-envelope.json")
        self.assertEqual(validate(env, schema), [])
        self.assertEqual(env["unit_id"], self.unit)
        self.assertEqual(env["base_sha"], sha)
        self.assertEqual(env["spec_ref"]["path"], f"docs/work/{self.unit}/spec.md")
        self.assertEqual(env["spec_ref"]["sha256"], sha256_file(self.spec))
        self.assertEqual(env["workspace"], "current")          # T0 격리 = current
        self.assertEqual(env["guards"], [])
        self.assertEqual([c["command"] for c in env["required_checks"]],
                         ["python3 -m unittest tests.test_envelope"])
        self.assertEqual(env["output_schema"], "core/schemas/result-envelope.json")

    def test_roles_differ_only_in_role_and_allowed_paths(self):
        sha = self._approve_and_commit()
        impl = self._build("implementer", base_sha=sha)
        rev = self._build("reviewer", base_sha=sha)
        self.assertEqual(rev["allowed_paths"], [])             # 검토자는 어떤 경로에도 쓰지 않는다
        self.assertIn(f"docs/work/{self.unit}/", impl["allowed_paths"])
        for key in ("unit_id", "spec_ref", "base_sha", "guards", "required_checks", "workspace"):
            self.assertEqual(impl[key], rev[key], key)

    def test_guards_come_from_the_router(self):
        out = route({"unit": "T0", "mode": "delivery", "intent": "delete", "facets": ["docs"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        res = create_unit(out, "삭제 계약", "envelope-del", "삭제", project_root=self.root, date="20260828")
        unit = res["id"]
        spec = Path(res["files"][0])
        fm, body = frontmatter.read(spec)
        frontmatter.write(spec, fm, body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS).replace('command: "채움"', 'command: "true"'))
        approve_unit(unit, "tester", project_root=self.root)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve-del", cwd=self.root)
        env = build_envelope(unit, "implementer", project_root=self.root,
                             base_sha=git("rev-parse", "HEAD", cwd=self.root))
        self.assertEqual([g["id"] for g in env["guards"]], ["deletion"])

    # ── 승인 없이는 계약이 없다 ────────────────────────────────────────────────
    def test_refuses_before_approval(self):
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "draft", cwd=self.root)
        with self.assertRaises(ValueError) as cm:
            self._build(base_sha=git("rev-parse", "HEAD", cwd=self.root))
        self.assertIn("승인", str(cm.exception))

    def test_refuses_when_the_approval_is_not_committed(self):
        approve_unit(self.unit, "tester", project_root=self.root)   # 커밋하지 않는다
        with self.assertRaises(ValueError) as cm:
            self._build()
        self.assertIn("--base-sha", str(cm.exception))

    def test_refuses_unknown_role(self):
        sha = self._approve_and_commit()
        with self.assertRaises(ValueError):
            self._build("supervisor", base_sha=sha)

    # ── 출력 경로 · CLI ───────────────────────────────────────────────────────
    def test_written_path_is_inside_the_unit_folder(self):
        sha = self._approve_and_commit()
        task_dir = (self.spec.parent / "task").resolve()
        res = write_envelope(self.unit, "implementer", project_root=self.root, base_sha=sha)
        self.assertEqual(Path(res["path"]).resolve(), task_dir / "implementer.json")
        res = write_envelope(self.unit, "reviewer", project_root=self.root, base_sha=sha, run_name="run_7865ac")
        self.assertEqual(Path(res["path"]).resolve(), task_dir / "run_7865ac-reviewer.json")
        self.assertEqual(load_json(res["path"])["role"], "reviewer")

    def test_cli_build(self):
        sha = self._approve_and_commit()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["envelope", "build", "--unit", self.unit, "--role", "implementer",
                       "--base-sha", sha, "--root", str(self.root), "--json"])
        self.assertEqual(rc, 0)
        env = json.loads(buf.getvalue())
        self.assertEqual(env["role"], "implementer")
        self.assertEqual(env["base_sha"], sha)
        self.assertTrue((self.spec.parent / "task" / "implementer.json").is_file())


class TestResultEnvelopeCheck(unittest.TestCase):
    """`romeo envelope check` — 결과를 회수한 쪽이 결과 계약을 검사하는 명령(3차 리뷰 H02).

    검사 규칙은 종료 검사가 검토자 봉투에 쓰는 함수 하나에서만 온다(K-63). 판정은 셋이다:
    PASS(0) · FAIL(1) · 대조가 성립하지 않은 UNVERIFIED(2) — 마지막을 통과로 접지 않는다(K-51)."""

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
        res = create_unit(out, "결과 계약 검사", "result-check-t0", "결과 계약을 검사한다",
                          project_root=self.root, date="20260828")
        self.unit = res["id"]
        self.spec = Path(res["files"][0])
        fm, body = frontmatter.read(self.spec)
        body = body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS).replace('command: "채움"', 'command: "true"')
        frontmatter.write(self.spec, fm, body.replace("- [ ] AC-1", "- [x] AC-1"))
        approve_unit(self.unit, "tester", project_root=self.root)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)
        sha = git("rev-parse", "HEAD", cwd=self.root)
        built = write_envelope(self.unit, "implementer", project_root=self.root,
                               base_sha=sha, run_name="run-test")
        self.task_rel = f"docs/work/{self.unit}/task/run-test-implementer.json"
        self.task_sha = built["sha256"]
        (self.root / "x.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl", cwd=self.root)
        run_command(self.unit, "true", run_name="run-test", project_root=self.root)
        self.result_dir = self.spec.parent / "result"
        self.result_dir.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _result(self, **over):
        """구현자가 낸 결과 계약. 계약 해시는 손으로 쓰지 않고 실제 산출물에서 읽는다."""
        env = {
            "schema": "romeo/result-envelope@0.1.0",
            "unit_id": self.unit,
            "role": "implementer",
            "task_envelope_ref": {"path": self.task_rel, "sha256": self.task_sha},
            "checks": [{"id": "check-1", "command": "true", "exit_code": 0}],
            "gate_verdict": "PASS",
            "blocked_reason": None,
            "findings": [],
            "evidence_ref": f"docs/work/{self.unit}/evidence/run-test.yaml",
        }
        env.update(over)
        return env

    def _write(self, data, name="run-test-implementer.json"):
        path = self.result_dir / name
        if isinstance(data, str):
            path.write_text(data, encoding="utf-8")
        else:
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def _check(self, path, *extra):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["envelope", "check", str(path), "--unit", self.unit,
                       "--root", str(self.root), *extra])
        return rc, out.getvalue() + err.getvalue()

    def test_valid_result_envelope_passes(self):
        rc, text = self._check(self._write(self._result()), "--role", "implementer")
        self.assertEqual(rc, 0, text)
        for cid in ("ENVELOPE_VALID", "TASK_ANCHORED", "BASE_SHA", "EVIDENCE_ANCHORED", "ROLE_CONTRACT"):
            self.assertIn(f"[PASS] {cid}", text)
        self.assertIn("→ PASS", text)

    def test_schema_violation_is_rejected_with_a_reason(self):
        rc, text = self._check(self._write(self._result(gate_verdict="아마도")))
        self.assertEqual(rc, 1)
        self.assertIn("[FAIL] ENVELOPE_VALID", text)
        self.assertIn("gate_verdict", text)

    def test_unreadable_json_is_rejected(self):
        rc, text = self._check(self._write("{ 깨진 json"))
        self.assertEqual(rc, 1)
        self.assertIn("[FAIL] ENVELOPE_VALID", text)
        self.assertNotIn("Traceback", text)

    def test_other_unit_is_rejected(self):
        rc, text = self._check(self._write(self._result(unit_id="chg-20260101-other-abcd")))
        self.assertEqual(rc, 1)
        self.assertIn("다른 작업 단위", text)

    def test_role_mismatch_is_rejected(self):
        rc, text = self._check(self._write(self._result()), "--role", "reviewer")
        self.assertEqual(rc, 1)
        self.assertIn("[FAIL] ENVELOPE_VALID", text)
        self.assertIn("role", text)

    def test_role_contract_scope_is_checked(self):
        """검토자는 명령을 실행하지 않는다 — 종료 검사와 같은 기준으로 거부한다(K-63)."""
        rc, text = self._check(self._write(self._result(role="reviewer")), "--role", "reviewer")
        self.assertEqual(rc, 1)
        self.assertIn("[FAIL] ROLE_CONTRACT", text)
        self.assertIn("ROLE_CONTRACT_VIOLATION", text)

    def test_hand_written_task_ref_is_rejected_and_base_sha_is_not_pass(self):
        """가리킨 계약을 읽지 못하면 base_sha 대조는 성립하지 않는다 — PASS 로 인쇄하지 않는다(H06)."""
        rc, text = self._check(self._write(self._result(
            task_envelope_ref={"path": self.task_rel, "sha256": "0" * 64})))
        self.assertEqual(rc, 1)
        self.assertIn("[FAIL] TASK_ANCHORED", text)
        self.assertIn("[UNVERIFIED] BASE_SHA", text)
        self.assertNotIn("[PASS] BASE_SHA", text)

    def test_hand_written_task_contract_with_a_matching_hash_is_rejected(self):
        """앵커는 해시가 아니라 재계산이다(J01). 계약처럼 생긴 JSON 을 규약에 맞는 자리에 만들고
        봉투에 그 파일의 진짜 해시를 실어도, 커밋된 원본에서 다시 계산한 계약과 바이트가 달라 거부된다."""
        forged = self.spec.parent / "task" / "run-forged-implementer.json"
        forged.write_text(json.dumps(
            {"unit_id": self.unit, "role": "implementer",
             "base_sha": git("rev-parse", "HEAD", cwd=self.root), "workspace": "current"},
            ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        rel_path = f"docs/work/{self.unit}/task/run-forged-implementer.json"
        rc, text = self._check(self._write(self._result(
            task_envelope_ref={"path": rel_path, "sha256": sha256_file(forged)})))
        self.assertEqual(rc, 1, text)
        self.assertIn("[FAIL] TASK_ANCHORED", text)
        self.assertIn("[UNVERIFIED] BASE_SHA", text)

    def test_tampered_contract_with_a_matching_hash_is_rejected(self):
        """계약 생성 명령이 만든 계약을 한 필드만 고쳤다. 해시는 다시 맞췄다."""
        path = self.spec.parent / "task" / "run-test-implementer.json"
        task = json.loads(path.read_text(encoding="utf-8"))
        task["required_checks"] = []          # 실행할 검사를 없앤 계약
        tampered = self.spec.parent / "task" / "run-tampered-implementer.json"
        tampered.write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        rc, text = self._check(self._write(self._result(task_envelope_ref={
            "path": f"docs/work/{self.unit}/task/run-tampered-implementer.json",
            "sha256": sha256_file(tampered)})))
        self.assertEqual(rc, 1, text)
        self.assertIn("[FAIL] TASK_ANCHORED", text)
        self.assertIn("required_checks", text)

    def test_evidence_ref_must_point_at_the_units_evidence_output(self):
        """실재하는 아무 파일이나 증거가 아니다 — 자기 입력인 spec.md 를 지목할 수 없다(J04).
        종료 검사와 같은 함수가 이 자리 규약을 소유한다(K-62·K-63)."""
        rc, text = self._check(self._write(self._result(
            evidence_ref=f"docs/work/{self.unit}/spec.md")))
        self.assertEqual(rc, 1, text)
        self.assertIn("[FAIL] EVIDENCE_ANCHORED", text)
        self.assertIn("evidence/", text)

    def test_unverifiable_envelope_exits_two_not_zero(self):
        """어긋난 것은 없지만 대조할 증거를 지목하지 않았다 — 통과가 아니라 검사 불가다."""
        rc, text = self._check(self._write(self._result(
            gate_verdict="FAIL", checks=[], evidence_ref=None)))
        self.assertEqual(rc, 2, text)
        self.assertIn("[UNVERIFIED] EVIDENCE_ANCHORED", text)
        self.assertIn("→ UNVERIFIED", text)

    def test_missing_file_exits_nonzero_with_a_reason(self):
        rc, text = self._check(self.result_dir / "없는결과.json")
        self.assertEqual(rc, 1)
        self.assertIn("결과 계약 파일이 없다", text)
        self.assertNotIn("Traceback", text)

    def test_json_output_carries_the_same_verdict(self):
        rc, text = self._check(self._write(self._result()), "--json")
        self.assertEqual(rc, 0)
        rows = json.loads(text)
        self.assertEqual(rows[0]["verdict"], "PASS")
        self.assertEqual([c["id"] for c in rows[0]["checks"]],
                         ["ENVELOPE_VALID", "TASK_ANCHORED", "BASE_SHA", "EVIDENCE_ANCHORED", "ROLE_CONTRACT"])


if __name__ == "__main__":
    unittest.main()


class _ApprovalRepo(unittest.TestCase):
    """승인 커밋 테스트의 공통 저장소 — T0 단위 하나가 승인 전 상태로 준비된다."""

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
        res = create_unit(out, "승인 커밋", "approval-t0", "승인 커밋 파생", project_root=self.root, date="20260829")
        self.unit = res["id"]
        self.spec = Path(res["files"][0])
        self._set_command("true")

    def tearDown(self):
        self.tmp.cleanup()

    def _set_command(self, command):
        fm, body = frontmatter.read(self.spec)
        body = body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
        body = body.replace('command: "채움"', f'command: "{command}"').replace('command: "true"', f'command: "{command}"')
        frontmatter.write(self.spec, fm, body)

    def _commit(self, msg):
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", msg, cwd=self.root)
        return git("rev-parse", "HEAD", cwd=self.root)


class TestApprovalCommit(_ApprovalRepo):
    """승인 커밋은 파일의 주장이 아니라 이력의 사실이다(체크리스트 38·37).

    `approve` 가 승인 시점의 HEAD 를 base_sha 로 적으면 그 커밋의 spec 에는 승인이 없다 — 승인 표시는 그 다음 커밋에 들어가므로
    base_sha 는 언제나 승인 커밋의 **부모**를 가리켰다. 실제 단위에서 그 값으로 계약을 만들면 이전 승인본의 검증 계획(5건)이 나왔다.
    그래서 approve 는 base_sha 를 적지 않고, 계약 생성은 이력에서 승인 커밋을 스스로 찾는다."""

    def test_approve_does_not_record_a_base_sha(self):
        fm = approve_unit(self.unit, "tester", project_root=self.root)
        self.assertIsNone(fm["base_sha"], "승인 시점의 HEAD 는 승인을 담지 않는 커밋이다 — 적지 않는다")
        self.assertEqual(fm["status"], "active")

    def test_contract_without_base_sha_uses_the_approval_commit_not_its_parent(self):
        from romeo.docs import approval_commit
        parent = git("rev-parse", "HEAD", cwd=self.root)
        approve_unit(self.unit, "tester", project_root=self.root)
        approval = self._commit("approve")
        self.assertEqual(approval_commit(self.root, self.unit), approval)
        env = build_envelope(self.unit, "implementer", project_root=self.root)
        self.assertEqual(env["base_sha"], approval)
        self.assertNotEqual(env["base_sha"], parent)
        # 승인 뒤 커밋이 더 쌓여도 승인 커밋은 그대로다 — 최신 커밋이 아니라 승인이 처음 커밋된 자리다.
        (self.root / "x.txt").write_text("impl\n", encoding="utf-8")
        self._commit("impl")
        self.assertEqual(approval_commit(self.root, self.unit), approval)
        self.assertEqual(build_envelope(self.unit, "implementer", project_root=self.root)["base_sha"], approval)

    def test_contract_without_base_sha_is_refused_until_the_approval_is_committed(self):
        from romeo.docs import approval_commit
        approve_unit(self.unit, "tester", project_root=self.root)   # 커밋하지 않는다
        with self.assertRaises(ValueError) as cm:
            approval_commit(self.root, self.unit)
        self.assertIn("커밋", str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            build_envelope(self.unit, "implementer", project_root=self.root)
        self.assertIn("--base-sha", str(cm.exception))

    def test_unapproved_spec_has_no_approval_commit(self):
        from romeo.docs import approval_commit
        self._commit("draft")
        with self.assertRaises(ValueError) as cm:
            approval_commit(self.root, self.unit)
        self.assertIn("승인", str(cm.exception))

    def test_reapproval_needs_the_flag_and_a_reason_and_moves_the_approval_commit(self):
        from romeo.docs import approval_commit
        approve_unit(self.unit, "tester", project_root=self.root)
        first = self._commit("approve")
        first_fm, _ = frontmatter.read(self.spec)
        # 검증 계획이 바뀌었다 — 재승인 대상이다(D-27). status 를 손으로 내리는 경로 대신 명령이 있어야 한다.
        self._set_command("echo changed")
        with self.assertRaises(ValueError) as cm:
            approve_unit(self.unit, "tester", project_root=self.root)
        self.assertIn("--reapprove", str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            approve_unit(self.unit, "tester", project_root=self.root, reapprove=True)
        self.assertIn("--reason", str(cm.exception))
        fm = approve_unit(self.unit, "tester2", project_root=self.root, reapprove=True, reason="검증 계획 변경")
        self.assertEqual(fm["status"], "active")
        self.assertEqual(fm["approved_by"], "tester2")
        self.assertIsNone(fm["base_sha"])
        self.assertEqual(len(fm["approval_history"]), 1)
        self.assertEqual(fm["approval_history"][0]["approved_at"], first_fm["approved_at"])
        self.assertEqual(fm["approval_history"][0]["approved_by"], "tester")
        self.assertEqual(fm["approval_history"][0]["reason"], "검증 계획 변경")
        # 재승인이 커밋되기 전에는 승인 커밋이 없다 — 이전 승인 커밋으로 조용히 되돌아가지 않는다.
        with self.assertRaises(ValueError):
            approval_commit(self.root, self.unit)
        second = self._commit("reapprove")
        self.assertEqual(approval_commit(self.root, self.unit), second)
        self.assertNotEqual(second, first)
        env = build_envelope(self.unit, "implementer", project_root=self.root)
        self.assertEqual(env["base_sha"], second)
        self.assertEqual([c["command"] for c in env["required_checks"]], ["echo changed"],
                         "재승인 커밋의 계약은 새 검증 계획을 담는다 — 38 의 결함은 정확히 여기서 이전 계획이 나오던 것이다")
        # 문서 스키마가 재승인 이력을 받는다.
        from romeo.validate import validate_doc
        self.assertEqual(validate_doc(self.spec)["errors"], [])

    def test_reapprove_cli_flags(self):
        approve_unit(self.unit, "tester", project_root=self.root)
        self._commit("approve")
        self._set_command("echo changed")
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            rc = main(["approve", self.unit, "--by", "tester", "--root", str(self.root)])
        self.assertEqual(rc, 1, buf.getvalue())
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            rc = main(["approve", self.unit, "--by", "tester", "--root", str(self.root),
                       "--reapprove", "--reason", "검증 계획 변경"])
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertNotIn("base_sha=", buf.getvalue(), "승인 메시지가 더는 base_sha 를 인쇄하지 않는다")
        self.assertIn("커밋", buf.getvalue())

    def test_evidence_change_base_is_the_commit_before_the_approval(self):
        """증거의 변경 기준은 승인 직전 커밋이다 — 승인과 구현을 한 커밋에 넣는 T0 흐름에서도 구현이 변경으로 잡혀야 한다.
        approve 가 예전에 적던 값(승인 시점 HEAD)과 같은 의미이고, 계약의 base_sha(승인 커밋)와는 다른 것이다."""
        before = git("rev-parse", "HEAD", cwd=self.root)
        approve_unit(self.unit, "tester", project_root=self.root)
        (self.root / "x.txt").write_text("impl\n", encoding="utf-8")
        approval = self._commit("approve+impl")
        res = run_command(self.unit, "true", run_name="run-test", project_root=self.root)
        from romeo.util import load_yaml
        rec = load_yaml(res["evidence"])
        self.assertEqual(rec["base_sha"], before)
        self.assertNotEqual(rec["base_sha"], approval)
        self.assertEqual(rec["changed_files"], ["x.txt"])
        # 계약은 승인 커밋을 base 로 쓴다 — 두 값은 다른 것이다.
        self.assertEqual(build_envelope(self.unit, "implementer", project_root=self.root)["base_sha"], approval)


class TestApprovalIdentity(_ApprovalRepo):
    """명시한 --base-sha 도 지금의 승인을 담고 있어야 한다 — 재승인 전 커밋을 주면 이전 검증 계획의 계약이 만들어진다(체크리스트 38 의 본체).
    종료 검사의 재계산 대조는 식별만 하므로 이전 승인의 봉투도 봉투로는 인정한다(지우지 않는다 — 동등성 관측의 표본이다)."""

    def test_explicit_base_sha_of_a_superseded_approval_is_refused(self):
        approve_unit(self.unit, "tester", project_root=self.root)
        first = self._commit("approve")
        self._set_command("echo changed")
        approve_unit(self.unit, "tester", project_root=self.root, reapprove=True, reason="검증 계획 변경")
        second = self._commit("reapprove")
        with self.assertRaises(ValueError) as cm:
            build_envelope(self.unit, "implementer", project_root=self.root, base_sha=first)
        self.assertIn("재승인", str(cm.exception))
        self.assertIn(second[:12], str(cm.exception))
        env = build_envelope(self.unit, "implementer", project_root=self.root, base_sha=second)
        self.assertEqual([c["command"] for c in env["required_checks"]], ["echo changed"])
        # 재계산 대조(allow_superseded)는 이전 승인의 계약도 그대로 다시 계산한다 — 식별이지 판정이 아니다.
        old = build_envelope(self.unit, "implementer", project_root=self.root, base_sha=first, allow_superseded=True)
        self.assertEqual([c["command"] for c in old["required_checks"]], ["true"])

    def test_a_commit_holding_an_unknown_approval_is_refused(self):
        """다른 브랜치의 승인이거나 손으로 고친 spec — 이 작업 트리가 겪은 어느 승인과도 맞지 않으면 계약을 만들지 않는다."""
        approve_unit(self.unit, "tester", project_root=self.root)
        sha = self._commit("approve")
        fm, body = frontmatter.read(self.spec)
        fm["approved_at"] = "2020-01-01T00:00:00+09:00"     # 작업 트리의 승인을 손으로 바꿨다
        frontmatter.write(self.spec, fm, body)
        with self.assertRaises(ValueError) as cm:
            build_envelope(self.unit, "implementer", project_root=self.root, base_sha=sha)
        self.assertIn("어느 승인과도 맞지 않는다", str(cm.exception))


class TestSmallDefectsFromTheDiffReview(_ApprovalRepo):
    """구현 diff 반박 검토가 잡은 작은 결함들 — 각각 한 번씩 고정한다."""

    def test_reviewer_contract_requires_a_run(self):
        approve_unit(self.unit, "tester", project_root=self.root)
        self._commit("approve")
        with self.assertRaises(ValueError) as cm:
            write_envelope(self.unit, "reviewer", project_root=self.root)
        self.assertIn("--run", str(cm.exception))
        write_envelope(self.unit, "reviewer", project_root=self.root, run_name="run-r")   # --run 이 있으면 된다
        write_envelope(self.unit, "implementer", project_root=self.root)                  # 구현자 계약은 종전대로

    def test_unquoted_approved_at_still_identifies_the_approval(self):
        """따옴표 없이 적힌 approved_at 은 YAML 이 datetime 으로 읽는다 — 문자열과 같은 승인으로 식별돼야 한다."""
        from romeo.docs import approval_commit
        approve_unit(self.unit, "tester", project_root=self.root)
        sha = self._commit("approve")
        text = self.spec.read_text(encoding="utf-8")
        fm, _ = frontmatter.read(self.spec)
        quoted = f"approved_at: '{fm['approved_at']}'"
        self.assertIn(quoted, text)
        self.spec.write_text(text.replace(quoted, f"approved_at: {fm['approved_at']}"), encoding="utf-8")
        self.assertEqual(approval_commit(self.root, self.unit), sha)

    def test_non_ascii_paths_are_recorded_verbatim_in_changed_files(self):
        from romeo.gitinfo import changed_files
        base = git("rev-parse", "HEAD", cwd=self.root)
        (self.root / "한글파일.txt").write_text("x\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "korean", cwd=self.root)
        files = changed_files(self.root, base)
        self.assertIn("한글파일.txt", files)
        self.assertFalse(any(f.startswith('"') for f in files), files)

    def test_t0_with_a_contract_still_counts_the_implementation_as_change(self):
        """T0 는 승인과 구현을 한 커밋에 넣고도 계약을 만든다(implement 절차 2번) — 그 계약의 base(승인 커밋)를 변경 기준으로 쓰면
        구현이 변경으로 잡히지 않아 HAS_CHANGE 가 떨어졌다. 현재 작업 공간 계약은 첫 승인 직전 규칙을 쓴다."""
        from romeo.util import load_yaml
        before = git("rev-parse", "HEAD", cwd=self.root)
        approve_unit(self.unit, "tester", project_root=self.root)
        (self.root / "x.txt").write_text("impl\n", encoding="utf-8")
        self._commit("approve+impl")
        env = write_envelope(self.unit, "implementer", project_root=self.root, run_name="run-t0")
        self.assertEqual(env["envelope"]["workspace"], "current")
        res = run_command(self.unit, "true", run_name="run-t0", project_root=self.root)
        rec = load_yaml(res["evidence"])
        self.assertEqual(rec["base_sha"], before)
        self.assertEqual(rec["changed_files"], ["x.txt"])

    def test_runs_that_finish_in_the_same_second_are_ordered_by_recording_time(self):
        from romeo.evidence import list_runs
        approve_unit(self.unit, "tester", project_root=self.root)
        self._commit("approve")
        run_command(self.unit, "true", run_name="run-z-first", project_root=self.root)
        run_command(self.unit, "true", run_name="run-a-second", project_root=self.root)
        names = [r["run_id"] for r in list_runs(self.root, self.unit)]
        self.assertEqual(names[-1], "run-a-second", names)

    def test_a_colon_in_expect_gives_a_pointed_korean_error_not_a_traceback(self):
        """결함 ① 회귀 — `expect` 문구에 따옴표 없는 콜론이 들어가면 검증 계획 YAML 이 깨진다.
        `envelope build` 는 파이썬 traceback 대신 어느 검사·어느 줄·열이 깨졌는지 지목하는
        한국어 오류(ValueError)를 내야 하고, CLI 는 그것을 종료 코드가 0 이 아닌 것으로 끝내야 한다."""
        fm, body = frontmatter.read(self.spec)
        self.assertIn("expect: exit 0", body)
        body = body.replace("expect: exit 0", "expect: exit 0: 이유")
        frontmatter.write(self.spec, fm, body)
        approve_unit(self.unit, "tester", project_root=self.root)
        sha = self._commit("approve")

        with self.assertRaises(ValueError) as cm:
            build_envelope(self.unit, "implementer", project_root=self.root, base_sha=sha)
        msg = str(cm.exception)
        self.assertIn("check-1", msg)
        self.assertIn("행", msg)
        self.assertIn("열", msg)
        self.assertIn("콜론", msg)
        self.assertNotIn("Traceback", msg)
        self.assertNotIn("expect: exit 0: 이유", msg, "명령·값 문자열 전체를 싣지 않는다")

        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            rc = main(["envelope", "build", "--unit", self.unit, "--role", "implementer",
                       "--base-sha", sha, "--root", str(self.root)])
        self.assertNotEqual(rc, 0)
        self.assertNotIn("Traceback", buf.getvalue())
        self.assertIn("check-1", buf.getvalue())

    def test_the_pointed_error_names_the_right_check_not_a_colon_inside_a_command(self):
        """결함 ① 의 오류 메시지가 **어느 검사인지**를 틀리게 지목하지 않는가.

        검사 id 는 YAML 시퀀스 항목(`- id: ...`)에서만 온다. `id:` 를 아무 데서나 찾으면 바로 위
        command·expect 값에 든 `id:` 를 검사 이름으로 읽어, 사람을 엉뚱한 줄로 보낸다."""
        from romeo.close import required_checks
        body = ("```yaml\n"
                "required_checks:\n"
                "  - id: check-1\n"
                '    command: "true"\n'
                "    expect: exit 0\n"
                "  - id: check-2\n"
                "    command: \"grep 'id: 미끼' README.md\"\n"
                "    expect: exit 0: 이유\n"
                "```\n")
        with self.assertRaises(ValueError) as cm:
            required_checks(body)
        msg = str(cm.exception)
        self.assertIn("check-2", msg, "깨진 줄이 속한 검사를 지목하지 못했다")
        self.assertNotIn("미끼", msg, "command 값 안의 `id:` 를 검사 이름으로 오인했다")
