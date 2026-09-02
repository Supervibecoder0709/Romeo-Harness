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
from romeo.envelope import build_envelope, change_scope_paths, envelope_text, write_envelope
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


class TestChangeScopeMultiline(unittest.TestCase):
    """「바뀌는 파일·모듈」 선언이 **줄을 넘겨도 전부** 쓰기 상한에 실리는가 (Q-18).

    라벨 줄에서 곧바로 `return` 하던 종전 동작은 뒤 줄의 경로를 조용히 버렸다 — 빈 경우와 달리
    부분 읽기는 아무 경고도 내지 않아 계약이 정상으로 보였고, 구현자가 쓰려는 순간에야 막혔다
    (2026-08-31 `feat-20260831-bmad-attach-probe-tgnb` 1회차: 선언한 9개 중 2개만 실렸다).

    반례가 짝을 이룬다: 이어 읽되 **다음 항목은 삼키지 않는다.** 「영향을 받는 부분」 은 승인이
    쓰기 상한으로 정한 것이 아니므로 상한에 들어가면 K-66 위반이다."""

    HEAD = "## 변경 범위\n\n"

    def test_a_declaration_that_wraps_is_read_whole(self):
        got = change_scope_paths(
            self.HEAD + "- 바뀌는 파일·모듈: `a/x.py` · `a/y.py`\n  · `a/z.py` · `b/w.md`\n")
        self.assertEqual(got, ["a/x.py", "a/y.py", "a/z.py", "b/w.md"])

    def test_wrapping_over_three_lines_is_read_whole(self):
        got = change_scope_paths(
            self.HEAD + "- 바뀌는 파일·모듈: `a/x.py`\n  · `a/y.py`\n  · `a/z.py`\n")
        self.assertEqual(got, ["a/x.py", "a/y.py", "a/z.py"])

    def test_nested_bullets_are_read_too(self):
        """구분자 없이 하위 목록으로 적어도 버리지 않는다 — 조용히 잘리는 것이 이 결함의 본체다."""
        got = change_scope_paths(
            self.HEAD + "- 바뀌는 파일·모듈:\n  - `a/x.py`\n  - `a/y.py`\n")
        self.assertEqual(got, ["a/x.py", "a/y.py"])

    # ── 반례: 이어 읽기가 다음 항목을 삼키지 않는다 (K-66) ────────────────────
    def test_the_next_list_item_is_not_swallowed(self):
        got = change_scope_paths(
            self.HEAD + "- 바뀌는 파일·모듈: `a/x.py`\n- 영향을 받는 부분: `c/other.py`\n")
        self.assertEqual(got, ["a/x.py"])

    def test_a_blank_line_ends_the_declaration(self):
        got = change_scope_paths(
            self.HEAD + "- 바뀌는 파일·모듈: `a/x.py`\n\n  · `c/other.py`\n")
        self.assertEqual(got, ["a/x.py"])

    def test_the_next_section_is_not_swallowed(self):
        got = change_scope_paths(
            self.HEAD + "- 바뀌는 파일·모듈: `a/x.py`\n## 구현 단위\n\n`c/other.py`\n")
        self.assertEqual(got, ["a/x.py"])

    # ── 종전 동작이 그대로인가 ───────────────────────────────────────────────
    def test_single_line_declaration_is_unchanged(self):
        got = change_scope_paths(self.HEAD + "- 바뀌는 파일·모듈: `a/x.py` · `a/y.py`\n")
        self.assertEqual(got, ["a/x.py", "a/y.py"])

    def test_paths_outside_the_workspace_are_still_dropped(self):
        got = change_scope_paths(
            self.HEAD + "- 바뀌는 파일·모듈: `a/x.py`\n  · `/etc/passwd` · `~/.ssh/config` · `../out.py` · `a/x.py`\n")
        self.assertEqual(got, ["a/x.py"])

    def test_only_the_first_backtick_of_each_item_is_the_path(self):
        """이어 읽는 줄에서도 항목당 첫 백틱만 경로다 — 뒤따르는 백틱은 설명이다."""
        got = change_scope_paths(
            self.HEAD + "- 바뀌는 파일·모듈: `a/x.py`\n  · `b/y.py`(`collect` 에 들어 있는 함수)\n")
        self.assertEqual(got, ["a/x.py", "b/y.py"])

    def test_a_label_outside_the_section_is_still_ignored(self):
        got = change_scope_paths("## 다른 절\n\n- 바뀌는 파일·모듈: `a/x.py`\n  · `a/y.py`\n")
        self.assertEqual(got, [])


def change_scope_paths_at_d9a3b12(body):
    """이 단위 직전 하네스(`d9a3b12`)의 `change_scope_paths` — **참조 구현으로 고정**한 사본이다.

    새 규칙과의 차이가 곧 이 단위의 변경이다. 둘을 대조하는 자리가 둘이다 — 시나리오 8 의 문장에서 옛 규칙은 `cmd_card` 를
    읽고 새 규칙은 읽지 않는다는 것(부정 단언이 빈 검사가 아님을 보이는 대조군)과, 커밋된 계약 30건에서 두 규칙이 같은 목록을
    낸다는 것(AC-2). 저장소의 코드를 부르지 않는다 — 그 코드는 이 단위가 바꾸는 대상이다."""
    import re as _re
    inside = False
    lines = (body or "").split("\n")
    for i, line in enumerate(lines):
        if line.startswith("## "):
            inside = line.strip() == "## 변경 범위"
            continue
        if inside and "바뀌는 파일·모듈:" in line:
            declared = [line.split("바뀌는 파일·모듈:", 1)[1]]
            for nxt in lines[i + 1:]:
                if nxt.startswith("#") or nxt.startswith("- ") or not nxt.strip():
                    break
                declared.append(nxt)
            out = []
            for raw in declared:
                for chunk in raw.split("·"):
                    found = _re.search(r"`([^`]+)`", chunk)
                    if not found:
                        continue
                    text = found.group(1).strip().replace("\\", "/")
                    if not text or text.startswith("/") or text.startswith("~") or ".." in text.split("/"):
                        continue
                    if text not in out:
                        out.append(text)
            return out
    return []


class TestChangeScopeGrammar(_ApprovalRepo):
    """「변경 범위」 문법 (Q-36) — **설명 산문은 쓰기 상한에 들어가지 않는다.**

    시나리오 8 의 승인 문장 ``romeo/cli.py`(카드 렌더러에 `--root` 를 넘기는 호출부 — `cmd_card` 와 …)`` 에서
    `·` 로 자른 조각의 첫 백틱이 경로로 읽혀 **함수명 `cmd_card` 가 `allowed_paths` 에 실렸다**(2026-09-02 실측).
    상한이 넓어지는 방향이라 판정에 영향이 없었지만, 승인하지 않은 경로가 상한에 조용히 들어가는 구멍이다(K-66).

    규칙: 괄호 `(…)`·`（…）` 안은 줄 경계를 보존한 채 지운다(백틱 **밖** 구간에서만 — 경로 안의 괄호는 남는다) ·
    각 조각의 **첫 백틱만** 경로다 · 공백이 들었거나 `/` 도 `.` 도 없는 토큰은 경로가 아니라 「경로로 읽지 않은 토큰」 이다 ·
    앞의 `./` 는 벗긴다. 계약 JSON 의 필드는 바뀌지 않는다 — 앵커 재계산과 호환돼야 한다."""

    HEAD = "## 변경 범위\n\n"
    S8_SPEC = HARNESS_ROOT / "docs/work/feat-20260901-scenario-8-capability-probe-s7ny/spec.md"
    #: 시나리오 8 spec 의 「변경 범위」 선언 — 2026-09-02 그대로 **상수로도** 박아 둔다. 저장소 파일이 나중에 고쳐져도
    #: 아래 부정 단언(`cmd_card` 가 상한에 없다)이 빈 검사가 되지 않게 하기 위한 것이다.
    S8_DECLARATION = (
        "- 바뀌는 파일·모듈: `core/policy/capabilities.yaml` · `core/policy/packages.yaml`(절 enforcement ·\n"
        "  overlay · 차단 카탈로그) · `core/templates/sections/capability-check.md` · `adapters/*/adapter.yaml` ·\n"
        "  `romeo/doctor.py`(프로브) · `romeo/policy.py`(능력 계산) · `romeo/card.py`(인쇄) ·\n"
        "  `romeo/blocks.py`(집행) · `romeo/docs.py`(차단에 라우터 컨텍스트를 넘기는 배선) ·\n"
        "  `romeo/close.py`(같은 배선의 종료 검사 쪽 호출부) · `romeo/cli.py`(카드 렌더러에 `--root` 를\n"
        "  넘기는 호출부 — `cmd_card` 와 `cmd_route --card` 두 자리) · `scenarios/8-capability-absent.md` ·\n"
        "  `scenarios/README.md` · `tests/test_scenario_8.py` · 새 차단이 추가되면 따라와야 하는 기존 검사와 fixture:\n"
        "  `tests/test_scenario_3.py` · `tests/test_enforce_points.py` · `tests/test_blocks_enforcement.py` ·\n"
        "  `fixtures/requests/fx-discord-computer-use-automation.yaml` ·\n"
        "  `fixtures/requests/fx-s07-coupang-migration-initiative.yaml` ·\n"
        "  `fixtures/requests/fx-account-migration-continue.yaml`.\n"
    )
    TEMPLATE = HARNESS_ROOT / "core/templates/tech-spec.md"

    @staticmethod
    def _report(body):
        from romeo.envelope import change_scope_report   # 구현 전에는 이 이름이 없다 — 이 테스트만 실패한다
        return change_scope_report(body)

    # ── ① 저장소의 실제 승인 문장 ───────────────────────────────────────────
    def test_scenario_8_declaration_yields_paths_not_prose(self):
        _fm, body = frontmatter.read(self.S8_SPEC)
        got = change_scope_paths(body)
        for prose in ("cmd_card", "--root", "cmd_route --card"):
            self.assertNotIn(prose, got, got)
        self.assertIn("romeo/cli.py", got)
        self.assertIn("scenarios/8-capability-absent.md", got)

    # ── ⑩ 같은 문장을 상수로 — 저장소 파일과 무관하게, 그리고 옛 규칙과의 대조군을 함께 ───
    def test_scenario_8_sentence_as_a_constant_drops_cmd_card_that_the_old_rule_read(self):
        body = self.HEAD + self.S8_DECLARATION
        old = change_scope_paths_at_d9a3b12(body)
        self.assertIn("cmd_card", old, "대조군 — 옛 규칙은 이 문장에서 cmd_card 를 읽었다. 아니면 아래 부정 단언은 빈 검사다")
        new = change_scope_paths(body)
        for prose in ("cmd_card", "--root", "cmd_route --card"):
            self.assertNotIn(prose, new, new)
        self.assertIn("romeo/cli.py", new)
        self.assertIn("scenarios/8-capability-absent.md", new)
        self.assertEqual([p for p in old if p != "cmd_card"], new, "이 문장에서 두 규칙의 차이는 cmd_card 하나다")
        self.assertEqual(self._report(body)["ignored"], [], "cmd_card 는 괄호 안이라 ignored 에도 오르지 않는다")

    # ── ⑦ 조각의 첫 백틱만 경로다 — 뒤따르는 백틱은 괄호 밖이어도 상한이 아니다 ───
    def test_only_the_first_backtick_of_a_chunk_is_a_path(self):
        body = self.HEAD + "- 바뀌는 파일·모듈: `a/x.py` 는 `b/y.py` 를 부른다 · `c/z.py`\n"
        got = change_scope_paths(body)
        self.assertEqual(got, ["a/x.py", "c/z.py"])
        self.assertNotIn("b/y.py", got)

    # ── ⑧ `·` 없이 줄바꿈으로만 나눈 선언 — 닫는 괄호와 같은 줄의 다음 항목이 산다 ───
    def test_newline_separated_items_survive_a_wrapped_parenthesis(self):
        got = change_scope_paths(self.HEAD + "- 바뀌는 파일·모듈: `a/x.py`(설명\n  계속) `b/y.py`\n")
        self.assertEqual(got, ["a/x.py", "b/y.py"])

    # ── ⑨ 경로 안의 괄호는 지우지 않는다 — 괄호 제거는 백틱 밖 구간에만 ───
    def test_parentheses_inside_a_backtick_path_are_kept(self):
        body = self.HEAD + "- 바뀌는 파일·모듈: `app/(g)/page.tsx` · `b/y.py`(설명)\n"
        rep = self._report(body)
        self.assertEqual(rep["paths"], ["app/(g)/page.tsx", "b/y.py"])
        self.assertEqual(rep["ignored"], [])

    # ── ② 넓어지는 방향의 반례: 괄호 안의 경로 모양 백틱도 상한이 아니다 ─────
    def test_a_path_shaped_backtick_inside_parentheses_is_not_a_path(self):
        got = change_scope_paths(self.HEAD + "- 바뀌는 파일·모듈: `a/x.py`(설명 · `b/y.py` 는 그대로)\n")
        self.assertEqual(got, ["a/x.py"])

    # ── ③ 괄호가 줄을 넘겨도 다음 줄의 항목은 산다 ──────────────────────────
    def test_parentheses_that_wrap_a_line_do_not_eat_the_next_item(self):
        got = change_scope_paths(self.HEAD + "- 바뀌는 파일·모듈: `a/x.py`(설명 ·\n  다음 줄 · 계속) · `b/y.py`\n")
        self.assertEqual(got, ["a/x.py", "b/y.py"])

    # ── ④ 경로 모양이 아닌 토큰은 ignored 로 간다 ───────────────────────────
    def test_tokens_without_slash_or_dot_or_with_spaces_are_ignored_not_paths(self):
        body = self.HEAD + "- 바뀌는 파일·모듈: `cmd_card` · `--root` · `a b/c.py`\n"
        self.assertEqual(change_scope_paths(body), [])
        rep = self._report(body)
        self.assertEqual(rep["paths"], [])
        self.assertEqual(rep["ignored"], ["cmd_card", "--root", "a b/c.py"])

    # ── ⑤ 루트의 확장자 없는 파일은 ./ 로 쓴다 ─────────────────────────────
    def test_dot_slash_prefix_is_stripped(self):
        self.assertEqual(change_scope_paths(self.HEAD + "- 바뀌는 파일·모듈: `./LICENSE` · `./a/x.py`\n"),
                         ["LICENSE", "a/x.py"])

    def test_fullwidth_and_nested_parentheses_are_removed(self):
        got = change_scope_paths(
            self.HEAD + "- 바뀌는 파일·모듈: `a/x.py`（설명（중첩 `c/z.py`）） · `b/y.py`(x(`d/w.py`)z)\n")
        self.assertEqual(got, ["a/x.py", "b/y.py"])

    def test_paths_outside_the_workspace_are_dropped_not_reported_as_ignored(self):
        rep = self._report(self.HEAD + "- 바뀌는 파일·모듈: `a/x.py` · `/etc/passwd` · `../out.py` · `./../out.py`\n")
        self.assertEqual(rep["paths"], ["a/x.py"])
        self.assertEqual(rep["ignored"], [])

    def test_change_scope_paths_is_the_paths_of_the_report(self):
        body = self.HEAD + "- 바뀌는 파일·모듈: `a/x.py` · `cmd_card` · `b/y.py`(`--flag`)\n"
        rep = self._report(body)
        self.assertEqual(sorted(rep), ["ignored", "paths"])
        self.assertEqual(change_scope_paths(body), rep["paths"])
        self.assertEqual(rep["paths"], ["a/x.py", "b/y.py"])
        self.assertEqual(rep["ignored"], ["cmd_card"])

    # ── 계약 생성 — 목록은 인쇄하되 계약 JSON 은 그대로 ─────────────────────
    def _scope(self, declaration):
        fm, body = frontmatter.read(self.spec)
        frontmatter.write(self.spec, fm, body.replace(SCOPE_PATHS, "- 바뀌는 파일·모듈: " + declaration))
        approve_unit(self.unit, "tester", project_root=self.root)
        return self._commit("approve")

    def test_write_envelope_reports_ignored_tokens_but_the_contract_json_is_unchanged(self):
        sha = self._scope("`docs/work/` · `cmd_card` · `scripts/`(`collect` 를 고친다) · `--root`")
        res = write_envelope(self.unit, "implementer", project_root=self.root, base_sha=sha)
        self.assertEqual(res["scope_ignored"], ["cmd_card", "--root"])
        env = res["envelope"]
        self.assertEqual(env["allowed_paths"], [f"docs/work/{self.unit}/", "docs/work/", "scripts/"])
        self.assertNotIn("scope_ignored", env, "계약 JSON 의 필드는 바뀌지 않는다 — 앵커 재계산과 호환돼야 한다")
        self.assertNotIn("scope_ignored", Path(res["path"]).read_text(encoding="utf-8"))
        schema = load_json(HARNESS_ROOT / "core/schemas/task-envelope.json")
        self.assertEqual(validate(env, schema), [])

    def test_cli_build_prints_the_ignored_tokens_only_when_there_are_any(self):
        sha = self._scope("`docs/work/` · `cmd_card`")
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            rc = main(["envelope", "build", "--unit", self.unit, "--role", "implementer",
                       "--base-sha", sha, "--root", str(self.root)])
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertIn("경로로 읽지 않은 백틱 1개", buf.getvalue())
        self.assertIn("cmd_card", buf.getvalue())
        # --json 은 계약 JSON 만 표준 출력에 낸다 — 목록은 표준 오류로 간다
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["envelope", "build", "--unit", self.unit, "--role", "implementer",
                       "--base-sha", sha, "--root", str(self.root), "--json"])
        self.assertEqual(rc, 0, err.getvalue())
        self.assertNotIn("cmd_card", json.loads(out.getvalue())["allowed_paths"])
        self.assertIn("경로로 읽지 않은 백틱 1개", err.getvalue())

    def test_cli_build_is_silent_about_ignored_tokens_when_there_are_none(self):
        approve_unit(self.unit, "tester", project_root=self.root)
        sha = self._commit("approve")
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            rc = main(["envelope", "build", "--unit", self.unit, "--role", "implementer",
                       "--base-sha", sha, "--root", str(self.root)])
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertNotIn("경로로 읽지 않은", buf.getvalue())

    # ── 문법은 spec 을 쓰는 사람이 읽는 자리에 있다 ────────────────────────
    def test_the_template_states_the_grammar(self):
        text = self.TEMPLATE.read_text(encoding="utf-8")
        section = text.split("\n## 변경 범위\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("- 바뀌는 파일·모듈:", section)
        guide = section.split("- 바뀌는 파일·모듈:", 1)[0]          # 목록 **앞**의 안내 문단
        self.assertTrue(guide.strip(), "「변경 범위」 제목 아래, 목록 앞에 안내 문단이 있어야 한다")
        for element in ("백틱", "괄호", "경로로 읽지 않", "./LICENSE", "change_scope_paths"):
            self.assertIn(element, guide, element)
        self.assertIn("`/`", guide)
        self.assertIn("`.`", guide)
        # 라벨 문자열(콜론 포함)은 안내 문단에 쓰지 않는다 — 파서가 그 줄을 선언으로 읽는다
        self.assertNotIn("바뀌는 파일·모듈:", guide)
        self.assertNotIn("NEEDS_INPUT", guide)


class TestChangeScopeRegressionOnRecordedContracts(unittest.TestCase):
    """기존 승인의 상한은 그대로다 (AC-2) — 저장소에 커밋된 구현자 계약 30건 전부에서, 그 계약의 `base_sha` 커밋의
    spec 을 새 규칙으로 읽은 결과가 **이 단위 직전 하네스(`d9a3b12`)의 규칙**으로 읽은 결과와 순서까지 같다.

    기록된 `allowed_paths` 와의 대조는 **목록으로**(순서 포함) 한다 — 집합 비교는 순서가 바뀐 계약을 통과시키는데,
    앵커 재계산은 바이트로 대조하므로 순서도 계약의 일부다. 30건 중 3건은 이 단위와 무관한 이유로 지금 HEAD 의
    규칙과도 이미 다르다 — 46an 의 두 건은 상한이 `.`(작업 공간 전체)이던 시절의 계약이고(체크리스트 34 이전),
    tgnb 의 한 건은 줄을 넘긴 선언을 첫 줄에서 끊던 파서의 계약이다(Q-18 이전). 그 셋은 새 규칙이 아니라 이력이 만든
    차이이므로 **이름으로** 제외한다 — 예외가 조용히 늘지 않게 하려는 것이다. 나머지 27건은 `[must_include 치환] + new`
    가 기록과 목록으로 같아야 한다. `cmd_card` 는 커밋된 계약에는 없다 — 시나리오 8 의 계약은 `.gitignore` 로
    커밋되지 않았으므로 그 차이는 `TestChangeScopeGrammar` 가 spec 재계산으로만 본다(AC-1)."""

    #: 기록된 상한이 지금 HEAD 의 규칙으로도 재현되지 않는 계약 — 이 단위와 무관한 이력의 차이다.
    HISTORICAL = {
        "docs/work/feat-20260829-license-field-46an/task/run_31e175742892-implementer.json": "상한이 `.` 이던 시절",
        "docs/work/feat-20260829-license-field-46an/task/run_b5cdadaffcdc-implementer.json": "상한이 `.` 이던 시절",
        "docs/work/feat-20260831-bmad-attach-probe-tgnb/task/run_d7edd4884a83-implementer.json": "Q-18 이전 파서(첫 줄만 읽음)",
    }
    #: 이 단위가 시작한 시점에 커밋돼 있던 구현자 계약 수 — 줄어들면 대조 대상이 사라진 것이고, 늘면 새 계약이 이 검사 아래 들어온 것이다
    RECORDED = 30

    def _recorded_contracts(self):
        files = git("ls-files", "docs/work/*/task/*-implementer.json", cwd=HARNESS_ROOT).split("\n")
        return [f for f in files if f.strip()]

    @staticmethod
    def _spec_body_at(env):
        raw = subprocess.run(["git", "show", f"{env['base_sha']}:{env['spec_ref']['path']}"],
                             cwd=str(HARNESS_ROOT), capture_output=True, check=True).stdout.decode("utf-8")
        _fm, body = frontmatter.split(raw)
        return body

    def test_the_new_rule_and_the_d9a3b12_rule_agree_on_every_recorded_contract(self):
        """30건 전부 — 새 규칙 == 옛 규칙, 목록 동등(순서 포함). 부분집합 허용도 `cmd_card` 예외도 없다."""
        files = self._recorded_contracts()
        self.assertEqual(len(files), self.RECORDED, files)
        for rel_path in files:
            body = self._spec_body_at(load_json(HARNESS_ROOT / rel_path))
            self.assertEqual(change_scope_paths(body), change_scope_paths_at_d9a3b12(body), rel_path)

    def test_recorded_allowed_paths_are_reproduced_as_lists_except_the_three_historical_contracts(self):
        """이력 3건을 이름으로 제외한 27건 — `[must_include 치환] + new` 가 기록된 `allowed_paths` 와 **리스트로** 같다."""
        files = self._recorded_contracts()
        self.assertEqual(len(files), self.RECORDED, files)
        for missing in set(self.HISTORICAL) - set(files):
            self.fail(f"이름으로 제외한 이력 계약이 저장소에 없다: {missing}")
        compared = 0
        for rel_path in files:
            if rel_path in self.HISTORICAL:
                continue
            env = load_json(HARNESS_ROOT / rel_path)
            must = f"docs/work/{env['unit_id']}/"
            new = change_scope_paths(self._spec_body_at(env))
            self.assertEqual([must] + [p for p in new if p != must], env["allowed_paths"], rel_path)
            compared += 1
        self.assertEqual(compared, self.RECORDED - len(self.HISTORICAL))

    def test_the_three_historical_contracts_really_differ_from_the_recomputation(self):
        """제외한 셋이 정말 재현되지 않는 계약인지 본다 — 재현되는 것을 제외 목록에 두면 그 목록은 장식이다."""
        for rel_path in self.HISTORICAL:
            env = load_json(HARNESS_ROOT / rel_path)
            must = f"docs/work/{env['unit_id']}/"
            new = change_scope_paths(self._spec_body_at(env))
            self.assertNotEqual([must] + [p for p in new if p != must], env["allowed_paths"],
                                f"{rel_path}: 재현되는 계약은 이력 예외에 둘 수 없다 — 목록에서 뺀다")

    def test_the_parity_case_contracts_are_recomputed_identically(self):
        """동등성 관측 케이스(`fixtures/parity/pr-license-field-t1-observed.yaml`)가 재계산하는 46an 의 두 계약 —
        새 규칙으로도 기록과 같은 allowed_paths 다(`fixtures parity` 가 그대로 통과하는 근거)."""
        for run in ("run_5a5a894aa26d", "run_ba40ff663b44"):
            rel_path = f"docs/work/feat-20260829-license-field-46an/task/{run}-implementer.json"
            env = load_json(HARNESS_ROOT / rel_path)
            raw = subprocess.run(["git", "show", f"{env['base_sha']}:{env['spec_ref']['path']}"],
                                 cwd=str(HARNESS_ROOT), capture_output=True, check=True).stdout.decode("utf-8")
            _fm, body = frontmatter.split(raw)
            self.assertEqual([f"docs/work/{env['unit_id']}/"] + change_scope_paths(body), env["allowed_paths"], run)
