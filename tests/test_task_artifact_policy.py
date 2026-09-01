"""작업 계약 사본을 git 추적에서 뺀 규칙과, 그 규칙이 깨뜨리면 안 되는 것을 반례로 고정한다.

여기서 고정하는 것은 셋이다.

1. **제외 규칙의 범위** — `docs/work/<임의>/task/` 만 빠지고 `evidence/`·`result/`·`review/` 는 빠지지 않는다.
   계약만 파생물이기 때문이다. 증거·결과·검토 판정은 그 실행에서만 나오는 원본이라 이력에 있어야 한다.
2. **종료 검사가 그래도 성립한다** — `romeo/close.py` 의 작업 계약 앵커는 커밋 조회가 아니라
   **승인 원본에서의 재계산**이라, 계약이 추적되지 않아도 통과한다. 이것이 제외를 정당화하는 전제다.
3. **그렇다고 파일이 없어도 되는 것은 아니다** — 작업 트리에 계약이 없으면 앵커는 실패한다.
   제외는 "이력에 두지 않는다" 이지 "만들지 않는다" 가 아니다.

덧붙여 절차 문서 두 곳을 이 결론에 묶는다 — 구현자 브리프가 검사 **개수**를 다시 갖지 않는 것과,
RUNBOOK §3.3 이 위임한 쪽 사본을 커밋하지 않는다는 것과 그 이유를 적고 있는 것.
"""

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from romeo import frontmatter
from romeo.close import _task_anchor
from romeo.docs import approve_unit, create_unit
from romeo.envelope import write_envelope
from romeo.policy import route
from romeo.util import sha256_file

REPO = Path(__file__).resolve().parent.parent
GITIGNORE = REPO / ".gitignore"
BRIEF = REPO / "adapters" / "orca" / "prompts" / "implementer-brief.md"
RUNBOOK = REPO / "adapters" / "orca" / "RUNBOOK.md"

SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"
SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `scripts/` · `README.md`"

SECTION_33 = (r"^### 3\.3 ", r"^### 3\.4 ")


def _section(text, start_pat, end_pat):
    """`awk '/start/,/end/'` 와 같은 잘라내기 — 절차를 밟는 사람이 그 절에서 만나는 범위만 본다."""
    out, on = [], False
    for line in text.splitlines():
        if not on and re.search(start_pat, line):
            on = True
        if on:
            out.append(line)
            if len(out) > 1 and re.search(end_pat, line):
                break
    return "\n".join(out)


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, check=True).stdout.strip()


def check_ignore(path, cwd):
    """`git check-ignore -q` 의 종료 코드 — 0 이면 제외, 1 이면 제외가 아니다."""
    return subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=str(cwd),
                          capture_output=True, text=True).returncode


class TestTaskEnvelopeNotTracked(unittest.TestCase):
    """계약을 git 추적에서 뺀 규칙과, 그것이 종료 검사를 망가뜨리지 않는다는 것."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        # 저장소의 실제 규칙을 그대로 들여온다 — 테스트가 자기 사본을 만들면 고정되는 것은 규칙이 아니라 그 사본이다.
        (self.root / ".gitignore").write_text(GITIGNORE.read_text(encoding="utf-8"), encoding="utf-8")
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)

        out = route({"unit": "T1", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        res = create_unit(out, "계약 제외 고정", "task-ignore", "계약을 추적하지 않는다",
                          project_root=self.root, date="20260901")
        self.unit = res["id"]
        # 패키지가 spec 말고도 문서를 만든다 — 승인이 보는 자리는 spec 이지만 자리표시자는 전부 채운다.
        for f in res["files"]:
            path = Path(f)
            fm, body = frontmatter.read(path)
            body = (body.replace("NEEDS_INPUT", "채움")
                        .replace(SCOPE_TODO, SCOPE_PATHS)
                        .replace('command: "채움"', 'command: "true"')
                        .replace("- [ ] AC-1", "- [x] AC-1"))
            frontmatter.write(path, fm, body)
        approve_unit(self.unit, "tester", project_root=self.root)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)
        self.approval_sha = git("rev-parse", "HEAD", cwd=self.root)

        built = write_envelope(self.unit, "implementer", project_root=self.root,
                               base_sha=self.approval_sha, run_name="run-test")
        self.task_path = Path(built["path"])
        self.task_rel = f"docs/work/{self.unit}/task/run-test-implementer.json"
        self.task_sha = sha256_file(self.task_path)   # 파일을 지우는 테스트가 있으므로 여기서 잡아 둔다
        self.addCleanup(self.tmp.cleanup)

    def _envelope(self, **over):
        env = {"role": "implementer",
               "task_envelope_ref": {"path": self.task_rel, "sha256": self.task_sha}}
        env.update(over)
        return env

    # ── ① 추적되지 않는 계약으로도 앵커가 선다 ────────────────────────────────
    def test_the_contract_is_excluded_and_invisible_to_git(self):
        """실재하는 계약이 제외로 판정되고, ls-files 에도 status 에도 나오지 않는다."""
        self.assertTrue(self.task_path.is_file())
        self.assertEqual(check_ignore(self.task_rel, cwd=self.root), 0,
                         f"{self.task_rel} 가 제외로 판정돼야 한다")
        self.assertEqual(git("ls-files", f"docs/work/{self.unit}/task/", cwd=self.root), "")
        self.assertEqual(
            git("status", "--porcelain", "--untracked-files=all", f"docs/work/{self.unit}/task/",
                cwd=self.root), "",
            "제외된 계약이 untracked 목록에 남으면 통합이 다시 이 파일을 만난다")

    def test_task_anchor_passes_while_the_contract_is_untracked(self):
        """앵커는 커밋 조회가 아니라 승인 원본에서의 재계산이다 — 계약이 이력에 없어도 통과한다(AC-2)."""
        self.assertEqual(git("ls-files", f"docs/work/{self.unit}/task/", cwd=self.root), "",
                         "전제: 계약이 추적되고 있지 않다")
        task, why = _task_anchor(self.root, self.unit, self._envelope(), None)
        self.assertIsNone(why, f"추적되지 않는 계약으로도 앵커가 서야 한다 — {why}")
        self.assertIsNotNone(task)
        self.assertEqual(task["unit_id"], self.unit)
        self.assertEqual(task["role"], "implementer")

    # ── ② 제외가 '파일이 없어도 된다' 는 뜻은 아니다 ──────────────────────────
    def test_task_anchor_fails_when_the_contract_is_absent_from_the_worktree(self):
        """앵커는 작업 트리의 파일을 읽는다 — 제외했다고 지우면 대조할 것이 사라진다."""
        self.task_path.unlink()
        task, why = _task_anchor(self.root, self.unit, self._envelope(), None)
        self.assertIsNotNone(why, "계약 파일이 없으면 앵커가 실패해야 한다")
        self.assertIsNone(task)
        self.assertIn("실재하지 않는다", why)

    # ── ③ 제외 범위 — task/ 만이다 ────────────────────────────────────────
    def test_the_rule_excludes_task_but_not_the_other_unit_outputs(self):
        """계약만 파생물이다. 증거·결과·검토 판정은 그 실행에서만 나오는 원본이라 제외하지 않는다."""
        for rel in ("docs/work/feat-00000000-any-unit-zzzz/task/run_x-reviewer.json",
                    f"docs/work/{self.unit}/task/run-test-implementer.json"):
            self.assertEqual(check_ignore(rel, cwd=self.root), 0, f"{rel} 는 제외여야 한다")
        for rel in (f"docs/work/{self.unit}/evidence/run-test.yaml",
                    f"docs/work/{self.unit}/result/run-test-implementer.json",
                    f"docs/work/{self.unit}/review/run-test-reviewer.json",
                    f"docs/work/{self.unit}/spec.md"):
            self.assertEqual(check_ignore(rel, cwd=self.root), 1, f"{rel} 는 제외가 아니어야 한다")

    def test_the_rule_is_alive_in_this_repository_too(self):
        """복제본이 아니라 이 저장소의 `.gitignore` 로도 같은 판정이 나온다."""
        self.assertEqual(check_ignore("docs/work/feat-00000000-any-unit-zzzz/task/run_x-reviewer.json",
                                      cwd=REPO), 0)
        self.assertEqual(check_ignore("docs/work/feat-00000000-any-unit-zzzz/evidence/run_x.yaml",
                                      cwd=REPO), 1)

    # ── 이미 커밋된 계약은 빠지지 않는다 (AC-3) ────────────────────────────
    def test_an_already_tracked_contract_stays_tracked(self):
        """제외 규칙은 추적 중인 파일에 소급하지 않는다 — 이력을 다시 쓰지 않는다."""
        legacy = self.root / "docs" / "work" / self.unit / "task" / "legacy-implementer.json"
        legacy.write_text(json.dumps({"legacy": True}), encoding="utf-8")
        git("add", "-f", f"docs/work/{self.unit}/task/legacy-implementer.json", cwd=self.root)
        git("commit", "-q", "-m", "legacy contract", cwd=self.root)
        self.assertEqual(
            git("ls-files", f"docs/work/{self.unit}/task/legacy-implementer.json", cwd=self.root),
            f"docs/work/{self.unit}/task/legacy-implementer.json",
            "이미 커밋된 계약은 규칙을 넣어도 추적에서 빠지지 않는다")

    def test_the_rule_carries_its_reason(self):
        """규칙 옆에 왜 빼는지가 적혀 있다 — 이유 없는 제외는 다음 사람이 되돌린다."""
        lines = GITIGNORE.read_text(encoding="utf-8").splitlines()
        self.assertIn("docs/work/*/task/", lines, "규칙 줄이 그대로 한 줄이어야 한다")
        # 규칙 바로 앞의 주석 묶음 — 규칙 줄에서 위로 올라가며 `#` 가 이어지는 구간.
        i = lines.index("docs/work/*/task/")
        comment, j = [], i - 1
        while j >= 0 and lines[j].startswith("#"):
            comment.insert(0, lines[j])
            j -= 1
        comment = "\n".join(comment)
        self.assertTrue(comment, "규칙 앞에 이유 주석이 있어야 한다")
        self.assertIn("--ff-only", comment, "무엇이 막혔었는지가 주석에 있어야 한다")
        self.assertTrue(re.search(r"재계산|파생물", comment),
                        "왜 빼도 되는지(승인 원본에서 재계산되는 파생물)가 주석에 있어야 한다")


class TestImplementerBriefNoCheckCount(unittest.TestCase):
    """구현자 브리프는 검사 **개수**를 갖지 않는다 — 개수는 계약이 정한다(AC-4).

    개수를 문장에 박아 두면 관통마다 `sed` 로 그 숫자까지 고쳐야 하고, 고치지 않으면 계약과 어긋난 절차 문서가
    워커에게 간다. 가리키는 문장은 남긴다 — 개수를 지우는 것이 `required_checks` 자체를 지우는 것이면 안 된다."""

    def setUp(self):
        self.text = BRIEF.read_text(encoding="utf-8")

    def test_no_hardcoded_check_count(self):
        hits = [f"{i}: {line}" for i, line in enumerate(self.text.splitlines(), 1)
                if re.search(r"[0-9]+건", line)]
        self.assertEqual(hits, [], "브리프에 `<숫자>건` 이 남아 있다 — 개수는 계약이 정한다")

    def test_the_required_checks_sentence_survives(self):
        self.assertTrue("required_checks" in self.text,
                        "개수를 지우면서 `required_checks` 를 가리키는 문장까지 지우면 안 된다")
        pointing = [line for line in self.text.splitlines()
                    if "required_checks" in line and "그대로 실행" in line]
        self.assertTrue(pointing,
                        "계약의 required_checks 를 문자열 그대로 실행하라는 문장이 남아 있어야 한다")


class TestRunbookTaskCopyNotCommitted(unittest.TestCase):
    """RUNBOOK §3.3 이 위임한 쪽 사본을 커밋하지 않는다는 것과 그 이유를 적고 있다(AC-5)."""

    def setUp(self):
        self.body = _section(RUNBOOK.read_text(encoding="utf-8"), *SECTION_33)
        self.assertTrue(self.body.startswith("### 3.3 "), "§3.3 을 잘라내지 못했다")

    def test_says_the_copy_is_not_committed(self):
        self.assertTrue("커밋하지 않는다" in self.body,
                        "§3.3 이 위임한 쪽 사본을 커밋하지 않는다고 적어야 한다")

    def test_says_why_it_may_be_left_out_of_history(self):
        """계약은 승인 원본에서 재계산되는 파생물이라 이력에 없어도 앵커가 선다."""
        self.assertTrue(re.search(r"재계산|파생물", self.body),
                        "§3.3 이 계약을 파생물로 설명해야 한다")
        self.assertTrue(".gitignore" in self.body, "§3.3 이 무엇이 제외하는지 가리켜야 한다")

    def test_says_what_breaks_when_it_is_committed(self):
        self.assertTrue("--ff-only" in self.body,
                        "§3.3 이 커밋했을 때 무엇이 막히는지 적어야 한다")


if __name__ == "__main__":
    unittest.main()
