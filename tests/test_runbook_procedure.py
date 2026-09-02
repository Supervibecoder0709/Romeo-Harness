"""adapters/orca/RUNBOOK.md 의 위임 전 확인이 실제로 두 경우를 가르는지 반례로 고정한다.

명령 문자열은 **RUNBOOK 에서 뽑아** 쓴다. 문서와 테스트가 따로 놀면 문서를 고쳐도 테스트가 옛 명령을
계속 통과시키고, 그때 고정된 것은 절차가 아니라 테스트 자신의 사본이다.
"""

import os
import re
import shlex
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
    """§3.1 의 재검토 기록 대조 명령을 RUNBOOK 에서 뽑는다 — 주석 줄을 뺀 **명령 한 줄**이다(Q-39).

    옛 확인 4 는 두 줄짜리 `diff <(git show …) <(cat …)` 였다. 새 확인 4 는 `bin/romeo run-unit check` 한 줄이고,
    블록의 주석이 무엇을 대조하는지(attempts.yaml 의 판정·재검토)를 말한다."""
    body = _section(RUNBOOK.read_text(encoding="utf-8"), *SECTION_31)
    blocks = [b for b in _fenced_blocks(body) if "attempts.yaml" in b]
    if len(blocks) != 1:
        raise AssertionError(
            "§3.1 에서 attempts.yaml 을 담은 bash 블록이 정확히 1개여야 한다 — %d 개다" % len(blocks)
        )
    lines = [l for l in blocks[0].splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if len(lines) != 1:
        raise AssertionError("§3.1 확인 4 의 bash 블록은 명령 한 줄이어야 한다 — %r" % lines)
    if not lines[0].startswith("bin/romeo run-unit check "):
        raise AssertionError("§3.1 확인 4 의 명령은 bin/romeo run-unit check 다 — %r" % lines[0])
    return lines[0]


def _git(cwd, *args):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


class TestAttemptsCommittedCheck(unittest.TestCase):
    """§3.1 확인 4 — 커밋 안의 attempts.yaml 과 작업 트리의 것을 **판정·재검토로만** 대조한다 (Q-39).

    명령은 RUNBOOK 에서 뽑아 `bin/romeo` 를 이 저장소의 절대 경로로 바꾸고 `--root <임시 저장소>` 를 붙여 실행한다.
    옛 `diff` 는 파일 전체를 비교해 첫 관통(작업 트리에 `started` 만 있는 상태)에서 항상 실패했다 —
    그 케이스가 **통과**하는 것이 이 개정의 본체다. 판정·재검토가 커밋 밖이면 여전히 거부한다."""

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
        # RUNBOOK 은 저장소 루트에서 `bin/romeo` 를 부른다 — 임시 저장소에는 하네스가 없으므로 이 저장소의 것을 절대 경로로 쓰고,
        # 대상 저장소는 --root 로 준다(§3.5.1 이 자식 워크트리에 대해 하는 것과 같은 모양).
        cmd = str(REPO / "bin" / "romeo") + cmd[len("bin/romeo"):] + " --root " + shlex.quote(str(self.root))
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
        self.assertIn("일치", proc.stdout)
        self.assertIn("started 는 대조하지 않는다", proc.stdout)

    # (a') 작업 트리에만 started 가 있다 — 첫 관통의 모양. 옛 diff 는 여기서 항상 실패했다(Q-39)
    def test_started_only_in_the_working_tree_passes(self):
        (self.unit_dir / "attempts.yaml").write_text(
            "attempts:\n  - n: 1\n    run: run_a\n    result: started\nreviews: []\n", encoding="utf-8"
        )
        proc = self.run_check()
        self.assertEqual(
            proc.returncode,
            0,
            "계약 생성이 막 남긴 started 는 커밋 밖이어도 통과해야 한다 — 첫 관통을 막으면 안 된다\n%s%s"
            % (proc.stdout, proc.stderr),
        )
        self.assertIn("판정 0건", proc.stdout)

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

    # (c) 커밋에만 있는 판정 — 작업 트리에서 지워졌다. 양방향이 아니면 여기서 통과한다(AC-6)
    def test_committed_verdict_missing_from_the_working_tree_is_rejected(self):
        path = self.unit_dir / "attempts.yaml"
        path.write_text("attempts:\n  - n: 1\n    run: run_a\n    result: fail\n", encoding="utf-8")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "attempts")
        self.base_sha = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        path.unlink()
        proc = self.run_check()
        self.assertNotEqual(
            proc.returncode,
            0,
            "커밋에는 있는 판정이 작업 트리에 없으면 거부돼야 한다 — 위임한 쪽과 워커가 다른 기록을 본다\n%s%s"
            % (proc.stdout, proc.stderr),
        )
        self.assertIn("커밋에만", proc.stdout)
        self.assertIn("run_a", proc.stdout)

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


class TestDelegationBlockMatchesRunUnit(unittest.TestCase):
    """§3.4 의 bash 블록과 `run-unit` 의 인쇄가 **문자열로 같다** (Q-40 · AGENTS.core §11).

    요구하는 자리(RUNBOOK 의 블록)와 만드는 자리(`romeo/run_unit.py` `delegation_commands`)가 어긋난 것이 Q-40 이었다.
    블록에서 `task-create` 두 명령을 뽑아(줄 연속 `\\` 를 합친다) 자리표시자 `<id>`·`<run-id>` 를 채운 것이 `delegation_commands`
    가 돌려주는 `task-create:implementer`·`task-create:reviewer` 와 같아야 한다 — 허용하는 정규화는 연속 공백→1개 뿐이다.
    `<implementer-task-id>` 는 양쪽 다 자리표시자로 남는다(이 시점에 아는 식별자는 둘뿐이다 — §3.4). 옛 RUNBOOK 의
    `"<작업 계약 경로와 실행 조건>"` 자리표시자에서는 실패한다."""

    SECTION_34 = (r"^### 3\.4 ", r"^### 3\.4\.1 ")
    UNIT = "feat-19700101-delegation-block-test"
    RUN = "run_0123456789ab"
    ALLOWED_PLACEHOLDERS = {"<id>", "<run-id>", "<implementer-task-id>"}

    @staticmethod
    def _normalize(command):
        return re.sub(r"[ \t]+", " ", command).strip()

    def _block_commands(self):
        body = _section(RUNBOOK.read_text(encoding="utf-8"), *self.SECTION_34)
        self.assertTrue(body.startswith("### 3.4 "), body[:40])
        blocks = [b for b in _fenced_blocks(body) if "task-create" in b]
        self.assertEqual(len(blocks), 1, "§3.4 에 task-create 를 담은 bash 블록이 정확히 1개여야 한다")
        joined = re.sub(r"\\\n\s*", " ", blocks[0])                      # 줄 연속을 합친다
        lines = [l for l in joined.splitlines() if l.strip() and not l.lstrip().startswith("#")]
        commands = [l for l in lines if l.startswith("orca orchestration task-create ")]
        self.assertEqual(len(commands), 2, lines)
        self.assertEqual(commands, lines, "블록의 명령은 task-create 둘뿐이다 — 다른 명령은 run-unit 의 인쇄가 소유한다")
        return commands

    def _printed(self):
        from romeo import HARNESS_ROOT
        from romeo.run_unit import delegation_commands
        cmds = dict(delegation_commands(self.UNIT, self.RUN, "a" * 40, "worktree", HARNESS_ROOT, "f" * 64))
        return cmds["task-create:implementer"], cmds["task-create:reviewer"]

    def test_the_block_uses_only_the_three_placeholders(self):
        found = set()
        for command in self._block_commands():
            found |= set(re.findall(r"<[^<>]+>", command))
        self.assertTrue(found, "자리표시자가 하나도 없으면 값을 박아 둔 것이다")
        self.assertEqual(found - self.ALLOWED_PLACEHOLDERS, set(), found)

    def test_task_create_commands_equal_the_run_unit_print_after_substitution(self):
        block_impl, block_rev = self._block_commands()
        printed_impl, printed_rev = self._printed()
        for block, printed, role in ((block_impl, printed_impl, "implementer"), (block_rev, printed_rev, "reviewer")):
            substituted = block.replace("<id>", self.UNIT).replace("<run-id>", self.RUN)
            self.assertEqual(self._normalize(substituted), self._normalize(printed), role)
            # 대조가 빈 검사가 아니다 — 치환 전에는 다르다(자리표시자가 실제로 값으로 바뀌었다)
            self.assertNotEqual(self._normalize(block), self._normalize(printed), role)


class TestReapprovalRuleIsConditional(unittest.TestCase):
    """§3.4·§3.4.1 — Run 재생성은 `--spec` 에 낡은 해시가 들어간 경우에만 (Q-41).

    §3.4.1 이 Run 재생성을 요구하는 근거는 `task-create --spec` 에 문자열로 복사된 낡은 계약 해시가 검토자에게 도달하는
    것이었다. `--spec` 에 해시를 넣지 않으면(검토자 프롬프트의 해시는 `fill_brief.py --task-sha256` 이 그 자리에서 계산한다)
    그 위험이 없다 — 2026-09-02 5회차가 Run 을 유지하고 봉투만 다시 만들어 close PASS 로 끝났다."""

    SECTION_34 = (r"^### 3\.4 ", r"^### 3\.4\.1 ")
    SECTION_341 = (r"^### 3\.4\.1 ", r"^### 3\.4\.2 ")

    def setUp(self):
        self.text = RUNBOOK.read_text(encoding="utf-8")

    def test_section_34_states_the_rule_that_the_spec_carries_no_hash(self):
        body = _section(self.text, *self.SECTION_34)
        self.assertTrue(body.startswith("### 3.4 "), body[:40])
        paragraphs = [p for p in body.split("\n\n") if "해시" in p and "넣지 않는다" in p]
        self.assertTrue(paragraphs, "§3.4 에 「해시」 와 「넣지 않는다」 가 같은 문단에 있어야 한다")
        self.assertTrue(any("fill_brief" in p and "§3.7" in p for p in paragraphs),
                        "그 문단이 해시가 어디서 계산되는지(§3.7 의 fill_brief.py)를 말해야 한다")

    def test_section_341_limits_run_recreation_to_the_stale_hash_case(self):
        body = _section(self.text, *self.SECTION_341)
        self.assertTrue(body.startswith("### 3.4.1 "), body[:40])
        self.assertTrue("경우에만" in body or "한정" in body, "Run 재생성은 해시가 들어간 경우로 한정돼야 한다")
        self.assertIn("2026-09-02", body, "5회차 관측(Run 유지 · 봉투 재생성)을 근거로 적는다")
        self.assertIn("§3.7", body)
        self.assertNotIn("무조건", body, "「무조건」 이 규칙으로 남아 있으면 안 된다")

    def test_the_reviewer_spec_sentence_no_longer_equates_the_spec_with_the_p_file(self):
        """「검토자 --spec 은 … P 파일과 같은 내용이다」 — 해시가 든 P 를 --spec 에 넣는 것이 §3.4.1 의 원인이었다."""
        body = _section(self.text, *self.SECTION_34)
        self.assertNotIn("P` 파일과 같은 내용", body)
        self.assertIn("복사하지 않는다", body)


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

    def test_section_342_points_at_run_unit_check(self):
        """§3.4.2 의 「확인 4 를 되살린다」 문단 — 새 명령(`run-unit check`)과 그 기준(`started` 는 보지 않는다)을 말하고,
        옛 `diff <(git show …)` 지시를 담지 않는다(Q-39). 재작업을 다시 위임하는 사람이 그 자리에서 옛 확인을 만나면 안 된다."""
        body = _section(self.text, r"^### 3\.4\.2 ", r"^### 3\.5 ")
        self.assertTrue(body.startswith("### 3.4.2 "), body[:40])
        self.assertIn("run-unit check", body)
        self.assertIn("started", body)
        self.assertNotIn("diff <(git show", body)


if __name__ == "__main__":
    unittest.main()
