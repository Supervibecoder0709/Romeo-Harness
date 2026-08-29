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
        res = write_envelope(self.unit, "reviewer", project_root=self.root, base_sha=sha)
        self.assertEqual(Path(res["path"]).resolve(), task_dir / "reviewer.json")
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
