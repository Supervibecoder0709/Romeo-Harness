"""판정하는 하네스는 승인 커밋 시점의 것이다(D-81 · 2026-09-07 진단 권고 1) — `JUDGE_REVISION`.

자기적용(판정 대상이 하네스 저장소 자신)에서는 판정을 낸 하네스의 `docs/` 밖 추적 파일 전부가 승인 커밋의 것과 같아야 한다.
워커 트리가 자기를 판정하면 거부되고, 승인 커밋을 `git archive` 로 꺼낸 스냅샷(git 저장소 아님)이 판정하면 통과한다.
남의 저장소(트리에 하네스가 없는 루트)는 「자기적용이 아니다」로 지나간다.

fixture: R = 이 체크아웃의 추적 파일을 **작업 트리 내용**으로 복사해 커밋한 저장소(하네스 저장소 자신) → T0 단위 생성·승인·커밋(승인 커밋 A)
→ `README.md` 를 바꿔 커밋(구현 — `docs/` 밖 추적 파일을 바꾼다) → 증거 1건. 각 검사는 R 의 사본과 A 의 스냅샷 J 를 자기 임시 폴더에 둔다."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from romeo import HARNESS_ROOT, frontmatter
from romeo.close import close_unit
from romeo.docs import approve_unit, create_unit
from romeo.evidence import run_command
from romeo.policy import route

SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"
SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `README.md`"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


def _copy_harness(dst):
    """이 체크아웃의 추적 파일을 작업 트리 내용으로 dst 에 복사한다 — 커밋되지 않은 변경도 함께 간다."""
    out = subprocess.run(["git", "ls-files", "-z"], cwd=str(HARNESS_ROOT), capture_output=True, check=True).stdout
    for rel in out.decode("utf-8").split("\0"):
        src = HARNESS_ROOT / rel
        if rel and src.is_file():
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)


def _archive(repo, rev, dst):
    """`git archive <rev> | tar -x` — RUNBOOK §3.1 확인 3·§3.8 과 같은 모양. git 저장소가 아닌 폴더가 된다."""
    proc = subprocess.run(["git", "archive", rev], cwd=str(repo), capture_output=True, check=True)
    dst.mkdir(parents=True, exist_ok=True)
    subprocess.run(["tar", "-x", "-C", str(dst)], input=proc.stdout, check=True)
    assert not (dst / ".git").exists()
    return dst


def _make_unit(root):
    out = route({"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"], "gates": [],
                 "blast_radius": "small", "uncertainty": "low"})
    res = create_unit(out, "판정 리비전 검사", "judge-t0", "테스트용 변경", project_root=root, date="20260907")
    spec = Path(res["files"][0])
    fm, body = frontmatter.read(spec)
    body = body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
    body = body.replace('command: "채움"', 'command: "true"').replace("- [ ] AC-1", "- [x] AC-1")
    frontmatter.write(spec, fm, body)
    return res["id"], spec


def _repo(root):
    git("init", "-q", cwd=root)
    git("config", "user.email", "t@example.com", cwd=root)
    git("config", "user.name", "t", cwd=root)


class TestJudgeRevision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        cls.base = Path(cls.tmp.name) / "R"
        cls.base.mkdir()
        _copy_harness(cls.base)
        _repo(cls.base)
        git("add", ".", cwd=cls.base)
        git("commit", "-q", "-m", "harness", cwd=cls.base)
        cls.unit, cls.spec = _make_unit(cls.base)
        approve_unit(cls.unit, "tester", project_root=cls.base)
        git("add", ".", cwd=cls.base)
        git("commit", "-q", "-m", "approve", cwd=cls.base)
        cls.approval = git("rev-parse", "HEAD", cwd=cls.base)
        with open(cls.base / "README.md", "a", encoding="utf-8") as fh:
            fh.write("\n구현 커밋 — docs/ 밖 추적 파일을 바꾼다\n")
        git("add", ".", cwd=cls.base)
        git("commit", "-q", "-m", "impl", cwd=cls.base)
        run_command(cls.unit, "true", run_name="run-test", label="check-1", project_root=cls.base)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name) / "R"
        shutil.copytree(self.base, self.root, symlinks=True)
        self.snap = _archive(self.root, self.approval, Path(self.tmp.name) / "J")

    def tearDown(self):
        self.tmp.cleanup()

    def _judge(self, harness_root, dry_run=True):
        r = close_unit(self.unit, project_root=self.root, harness_root=harness_root, dry_run=dry_run)
        row = next(c for c in r["checks"] if c["id"] == "JUDGE_REVISION")
        return r, row

    def test_the_tree_under_judgment_judging_itself_is_refused(self):
        r, row = self._judge(self.root)
        self.assertFalse(row["ok"])
        self.assertEqual(row["level"], "error")
        self.assertIn(self.approval[:12], row["detail"])
        self.assertIn("README.md", row["detail"])
        self.assertEqual(r["verdict"], "FAIL")

    def test_a_snapshot_of_the_approval_commit_passes_and_closes_the_unit(self):
        r, row = self._judge(self.snap)
        self.assertTrue(row["ok"], row)
        self.assertEqual(row["level"], "error")
        self.assertIn(self.approval[:12], row["detail"])
        self.assertEqual(r["verdict"], "PASS", r["checks"])
        r, _ = self._judge(self.snap, dry_run=False)
        self.assertEqual(r["verdict"], "PASS")
        fm, _ = frontmatter.read(self.root / "docs/work" / self.unit / "spec.md")
        self.assertEqual(fm["status"], "done")

    def test_a_snapshot_with_one_file_changed_is_refused_and_names_the_path(self):
        with open(self.snap / "romeo/close.py", "a", encoding="utf-8") as fh:
            fh.write("\n# 한 줄 — 거의 같은 스냅샷\n")
        _, row = self._judge(self.snap)
        self.assertFalse(row["ok"])
        self.assertIn("romeo/close.py", row["detail"])
        other = _archive(self.root, self.approval, Path(self.tmp.name) / "J2")
        (other / "README.md").unlink()
        _, row = self._judge(other)
        self.assertFalse(row["ok"])
        self.assertIn("README.md", row["detail"])

    def test_docs_are_not_compared(self):
        """`docs/`·`.harness/` 는 판정이 읽지 않는다 — 관통 중에도 바뀌는 곳이라 대조하면 늘 FAIL 이다."""
        with open(self.snap / "docs/planning/progress.md", "a", encoding="utf-8") as fh:
            fh.write("\n스냅샷의 문서는 대조하지 않는다\n")
        with open(self.snap / ".harness/observations.yaml", "a", encoding="utf-8") as fh:
            fh.write("\n# 런타임 기록도 대조하지 않는다\n")
        _, row = self._judge(self.snap)
        self.assertTrue(row["ok"], row)

    def test_a_root_without_the_harness_passes_as_not_self_applied(self):
        foreign = Path(self.tmp.name) / "F"
        foreign.mkdir()
        _repo(foreign)
        (foreign / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=foreign)
        git("commit", "-q", "-m", "init", cwd=foreign)
        unit, _ = _make_unit(foreign)
        approve_unit(unit, "tester", project_root=foreign)
        git("add", ".", cwd=foreign)
        git("commit", "-q", "-m", "approve", cwd=foreign)
        (foreign / "x.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=foreign)
        git("commit", "-q", "-m", "impl", cwd=foreign)
        run_command(unit, "true", run_name="run-test", label="check-1", project_root=foreign)
        r = close_unit(unit, project_root=foreign, harness_root=HARNESS_ROOT, dry_run=True)
        row = next(c for c in r["checks"] if c["id"] == "JUDGE_REVISION")
        self.assertTrue(row["ok"], row)
        self.assertIn("자기적용이 아니다", row["detail"])
        self.assertEqual(r["verdict"], "PASS", r["checks"])

    def test_the_snapshot_cli_judges_the_tree_with_root_and_prints_a_verdict(self):
        def run(binary):
            p = subprocess.run([sys.executable, str(binary), "close", "--unit", self.unit, "--root", str(self.root), "--dry-run"],
                               capture_output=True, text=True)
            self.assertNotIn("Traceback", p.stdout + p.stderr)
            return p
        p = run(self.snap / "bin/romeo")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("[PASS] JUDGE_REVISION", p.stdout)
        p = run(self.root / "bin/romeo")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("[FAIL] JUDGE_REVISION", p.stdout)
        # 스냅샷의 호출 한 번으로 done 이 된다 — dry-run 이 아닌 실제 종료.
        p = subprocess.run([sys.executable, str(self.snap / "bin/romeo"), "close", "--unit", self.unit, "--root", str(self.root)],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stdout + p.stderr)
        fm, _ = frontmatter.read(self.root / "docs/work" / self.unit / "spec.md")
        self.assertEqual(fm["status"], "done")

    def test_an_uncommitted_approval_leaves_the_judge_unverified(self):
        """승인 커밋을 이력에서 찾지 못하면 대조할 리비전이 없다 — 미검증이지 통과가 아니다(K-51)."""
        approve_unit(self.unit, "tester", project_root=self.root, reapprove=True, reason="커밋하지 않은 재승인")
        _, row = self._judge(self.snap)
        self.assertFalse(row["ok"])
        self.assertEqual(row["level"], "unverified")
        self.assertIn("승인 커밋을 이력에서 찾지 못해", row["detail"])


if __name__ == "__main__":
    unittest.main()
