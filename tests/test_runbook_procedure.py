"""adapters/orca/RUNBOOK.md 의 위임 전 확인이 실제로 두 경우를 가르는지 반례로 고정한다.

명령 문자열은 **RUNBOOK 에서 뽑아** 쓴다. 문서와 테스트가 따로 놀면 문서를 고쳐도 테스트가 옛 명령을
계속 통과시키고, 그때 고정된 것은 절차가 아니라 테스트 자신의 사본이다.
"""

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNBOOK = REPO / "adapters" / "orca" / "RUNBOOK.md"

SECTION_31 = (r"^### 3\.1 ", r"^### 3\.2 ")


def _section(text, start_pat, end_pat):
    """`awk '/start/,/end/'` 와 같은 잘라내기 — 검증 계획의 문서 검사와 같은 범위를 본다."""
    lines = text.splitlines()
    out, on = [], False
    for line in lines:
        if not on and re.search(start_pat, line):
            on = True
        if on:
            out.append(line)
            if len(out) > 1 and re.search(end_pat, line):
                break
    return "\n".join(out)


def _fenced_blocks(text):
    return re.findall(r"^```(?:bash|sh)?\n(.*?)^```", text, re.S | re.M)


def attempts_check_command():
    """§3.1 의 재검토 기록 대조 명령을 RUNBOOK 에서 뽑는다."""
    body = _section(RUNBOOK.read_text(encoding="utf-8"), *SECTION_31)
    blocks = [b for b in _fenced_blocks(body) if "attempts.yaml" in b]
    if len(blocks) != 1:
        raise AssertionError(
            "§3.1 에서 attempts.yaml 을 담은 bash 블록이 정확히 1개여야 한다 — %d 개다" % len(blocks)
        )
    return blocks[0]


def _git(cwd, *args):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


class TestAttemptsCommittedCheck(unittest.TestCase):
    """§3.1 확인 4 — 커밋 안의 attempts.yaml 과 작업 트리의 것을 대조한다."""

    UNIT = "feat-19700101-fixture-unit-test"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.unit_dir = self.root / "docs" / "work" / self.UNIT
        self.unit_dir.mkdir(parents=True)
        _git(self.root, "init", "-q", "-b", "main")
        _git(self.root, "config", "user.email", "fixture@example.invalid")
        _git(self.root, "config", "user.name", "fixture")
        (self.unit_dir / "spec.md").write_text("---\nid: x\n---\n", encoding="utf-8")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "base")
        self.base_sha = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        self.addCleanup(self.tmp.cleanup)

    def run_check(self):
        cmd = attempts_check_command()
        cmd = cmd.replace("<base-sha>", self.base_sha).replace("<id>", self.UNIT)
        env = dict(os.environ)
        env.pop("GIT_DIR", None)
        env.pop("GIT_WORK_TREE", None)
        return subprocess.run(
            ["bash", "-c", cmd], cwd=self.root, capture_output=True, text=True, env=env
        )

    # (a) 시도 기록이 아직 없는 단위 — 통과시킨다
    def test_missing_on_both_sides_passes(self):
        self.assertFalse((self.unit_dir / "attempts.yaml").exists())
        proc = self.run_check()
        self.assertEqual(
            proc.returncode,
            0,
            "attempts.yaml 이 양쪽 다 없으면 통과해야 한다 — 첫 관통을 막으면 안 된다\n%s%s"
            % (proc.stdout, proc.stderr),
        )
        self.assertEqual(proc.stdout, "")

    # (b) 작업 트리에만 있고 커밋 밖에 있는 재검토 — 거부한다
    def test_uncommitted_new_file_is_rejected(self):
        (self.unit_dir / "attempts.yaml").write_text(
            "attempts:\n  - result: fail\nreviews:\n  - by: someone\n", encoding="utf-8"
        )
        proc = self.run_check()
        self.assertNotEqual(
            proc.returncode,
            0,
            "커밋되지 않은 attempts.yaml 은 거부돼야 한다 — 워커가 그 기록을 보지 못한다",
        )

    # (b') 커밋된 것과 작업 트리의 것이 다르다 — 거부한다 (재검토 결론만 덧붙인 3회차의 모양)
    def test_committed_but_modified_is_rejected(self):
        path = self.unit_dir / "attempts.yaml"
        path.write_text("attempts:\n  - result: fail\n", encoding="utf-8")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "attempts")
        self.base_sha = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        path.write_text(
            "attempts:\n  - result: fail\nreviews:\n  - by: someone\n", encoding="utf-8"
        )
        proc = self.run_check()
        self.assertNotEqual(
            proc.returncode,
            0,
            "커밋된 것과 작업 트리의 것이 다르면 거부돼야 한다",
        )

    # 대조군 — 커밋과 작업 트리가 같으면 통과한다. 그래야 위 둘이 '항상 실패' 가 아니다
    def test_committed_and_identical_passes(self):
        path = self.unit_dir / "attempts.yaml"
        path.write_text("attempts:\n  - result: fail\n", encoding="utf-8")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "attempts")
        self.base_sha = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        proc = self.run_check()
        self.assertEqual(
            proc.returncode, 0, "%s%s" % (proc.stdout, proc.stderr)
        )


class TestRunbookProcedureAnchors(unittest.TestCase):
    """문서 쪽 앵커 — 절차를 밟는 사람이 그 자리에서 만나는지 본다(파일 어딘가가 아니라)."""

    def setUp(self):
        self.text = RUNBOOK.read_text(encoding="utf-8")

    def test_ls_tree_check_still_lists_eight_paths(self):
        """확인 4 를 더해도 확인 2 의 8행 판정을 깨지 않는다."""
        body = _section(self.text, *SECTION_31)
        blocks = [b for b in _fenced_blocks(body) if "git ls-tree" in b]
        self.assertEqual(len(blocks), 1)
        after = blocks[0].split("--name-only --", 1)[1]
        paths = [tok for tok in after.replace("\\\n", " ").split() if tok]
        self.assertEqual(len(paths), 8, "확인 2 는 8행 판정이다 — 목록이 8개여야 한다: %r" % paths)

    def test_rework_branch_lives_inside_the_run_order_section(self):
        body = _section(self.text, r"^## 3\. 실행 순서", r"^## 4\.")
        self.assertRegex(body, r"(?m)^### 3\.[0-9.]+ .*재작업")

    def test_run_rebinding_commands_live_inside_the_run_order_section(self):
        body = _section(self.text, r"^## 3\. 실행 순서", r"^## 4\.")
        self.assertIn("run-use --id", body)
        self.assertIn("run-current", body)


if __name__ == "__main__":
    unittest.main()
