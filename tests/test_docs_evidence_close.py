"""수직 슬라이스의 기계 부분: new → validate → approve → evidence → close, 그리고 stale 거부 4경우 + 미체크 AC 거부."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from romeo import frontmatter
from romeo.close import close_unit
from romeo.docs import approve_unit, create_unit
from romeo.evidence import run_command
from romeo.policy import route
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


if __name__ == "__main__":
    unittest.main()
