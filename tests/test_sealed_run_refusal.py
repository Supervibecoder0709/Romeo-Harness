"""봉인된 run 에는 더 쓰지 않는다 — Q-101 · `feat-20260910-sealed-run-worker-settle-37qi` AC-1~AC-4.

검토 봉투가 기록된 run(봉인 라벨의 명령 기록이 있는 run)에 `run_command`·`run_required_checks`·`record_review_envelope` 이
쓰려 하면 **아무것도 쓰지 않고 실행하지도 않은 채** `ValueError` 로 끝난다. 여집합(봉인 라벨 기록이 없는 run)에는 지금처럼 쓴다.

봉인 라벨은 이 파일에 적지 않는다 — `romeo.evidence.REVIEW_RECORD_LABEL` 에서 import 로만 읽는다(AC-3 ③).
적는 순간 정본이 둘이 되고, 라벨을 바꾼 커밋이 이 검사를 조용히 빈 검사로 만든다.

판별 상태는 **호출 전후의 바이트 대조**로 본다 — (a) `evidence/<run>.yaml` 의 바이트 · (b) `.harness/runs/<id>/<run>/` 의
파일 이름·sha256 목록 · (c) `review/<run>-reviewer.json` 의 바이트. 「거부됐다」 는 예외 하나로 끝나지 않는다 —
예외를 내고도 기록을 남긴 구현이 이 대조에서 갈린다.
"""
import io
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from romeo import frontmatter
from romeo.cli import main
from romeo.docs import approve_unit, create_unit
from romeo.evidence import (REVIEW_RECORD_LABEL, command_log_state, record_review_envelope, run_command,
                            run_required_checks)
from romeo.policy import route
from romeo.util import load_yaml, sha256_file

REPO = Path(__file__).resolve().parents[1]
SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"
SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `scripts/` · `README.md`"
#: 검증 계획의 검사 — **파일 하나를 만드는 명령**이다. 봉인된 run 에 `run_required_checks` 가 이 명령을 실행했는지는
#: 그 파일의 존재로 본다(AC-1 ②·AC-4). `.harness/` 아래에 두는 이유: 트리 해시의 제외 경로라 산출물 식별을 흔들지 않는다.
CHECK_MARKER = ".harness/probe/checks-marker"
CHECK_COMMAND = f"mkdir -p .harness/probe && touch {CHECK_MARKER}"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


class SealedRunFixture(unittest.TestCase):
    """임시 git 저장소에 검토자가 붙는 단위 하나. 봉인은 실제 절차 그대로 — 방어 검사 둘 + `record_review_envelope`."""

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
                     "gates": ["legal"], "blast_radius": "small", "uncertainty": "low"})
        self.assertNotEqual(out["reviewer"], "none")
        res = create_unit(out, "봉인 검사 T0", "sealed-t0", "봉인된 run 의 거부", project_root=self.root, date="20260910")
        self.unit = res["id"]
        self.spec = Path(res["files"][0])
        fm, body = frontmatter.read(self.spec)
        body = (body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
                .replace('command: "채움"', f'command: "{CHECK_COMMAND}"'))
        body = body.replace("- [ ] AC-1", "- [x] AC-1")
        frontmatter.write(self.spec, fm, body)
        approve_unit(self.unit, "tester", project_root=self.root)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)
        self.udir = self.spec.parent
        self.review_dir = self.udir / "review"

    def tearDown(self):
        self.tmp.cleanup()

    # ── 상태 만들기 ──────────────────────────────────────────────────────────
    def _defensive(self, run):
        for label in ("review-tree-before", "review-tree-after"):
            run_command(self.unit, "git status --porcelain", run_name=run, label=label, project_root=self.root)

    def _envelope(self, verdict="PASS"):
        return {"schema": "romeo/result-envelope@0.1.0", "unit_id": self.unit, "role": "reviewer",
                "task_envelope_ref": {"path": f"docs/work/{self.unit}/task/run-x-reviewer.json", "sha256": "0" * 64},
                "checks": [], "gate_verdict": verdict, "blocked_reason": None, "findings": [],
                "evidence_ref": f"docs/work/{self.unit}/evidence/run-x.yaml"}

    def _source(self, name, data):
        """봉투 원본은 제외 경로(.harness/) 안에 둔다 — 루트에 두면 미추적 파일이 트리 해시를 흔든다."""
        src = self.root / ".harness" / "review-src" / name
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return src

    def _seal(self, run, verdict="PASS"):
        """정상 검토 순서로 run 을 봉인한다: 방어 검사 둘 → 봉투 기록."""
        self._defensive(run)
        record_review_envelope(self.unit, run, self._source(f"{run}.json", self._envelope(verdict)), project_root=self.root)

    # ── 관측 ─────────────────────────────────────────────────────────────────
    def _evidence_path(self, run):
        return self.udir / "evidence" / f"{run}.yaml"

    def _log_dir(self, run):
        return self.root / ".harness" / "runs" / self.unit / run

    def _snapshot(self, run):
        """(a) 증거 yaml 바이트 · (b) 원시 로그 디렉터리의 {이름: sha256} · (c) 봉투 바이트. 없는 것은 None."""
        ep = self._evidence_path(run)
        ld = self._log_dir(run)
        rp = self.review_dir / f"{run}-reviewer.json"
        return (ep.read_bytes() if ep.is_file() else None,
                {p.name: sha256_file(p) for p in sorted(ld.iterdir())} if ld.is_dir() else None,
                rp.read_bytes() if rp.is_file() else None)

    def _rec(self, run):
        return load_yaml(self._evidence_path(run))

    def _assert_refusal(self, exc, run):
        msg = str(exc)
        self.assertIn(run, msg)
        self.assertIn("새 run", msg)

    def _assert_recorded(self, run, label, command, want_exit):
        """AC-2 의 「정상 기록」 관측 기준."""
        before = len(self._rec(run)["commands"]) if self._evidence_path(run).is_file() else 0
        run_command(self.unit, command, run_name=run, label=label, project_root=self.root)
        rec = self._rec(run)
        self.assertEqual(len(rec["commands"]), before + 1)
        last = rec["commands"][-1]
        self.assertEqual(last["id"], label)
        self.assertEqual(last["exit_code"], want_exit)
        self.assertEqual(rec["head_sha"], last["head_sha"])
        state, why = command_log_state(self.root, last)
        self.assertTrue(state, why)
        return rec


class TestSealedRunRefusesWrites(SealedRunFixture):
    """AC-1 — 봉인된 run 에는 세 자리 모두 쓰지 않고 실행하지도 않는다."""

    def test_run_command_on_sealed_run_writes_nothing_and_does_not_execute(self):
        self._seal("run-sealed")
        marker = self.root / ".harness" / "probe" / "run-marker"
        before = self._snapshot("run-sealed")
        with self.assertRaises(ValueError) as cm:
            run_command(self.unit, f"mkdir -p .harness/probe && touch {marker}", run_name="run-sealed",
                        label="check-1", project_root=self.root)
        self._assert_refusal(cm.exception, "run-sealed")
        self.assertEqual(self._snapshot("run-sealed"), before)
        self.assertFalse(marker.exists(), "넘긴 명령이 실행됐다 — 거부는 실행 전에 있어야 한다")

    def test_required_checks_on_sealed_run_stops_at_the_first_check(self):
        self._seal("run-sealed")
        marker = self.root / CHECK_MARKER
        before = self._snapshot("run-sealed")
        with self.assertRaises(ValueError) as cm:
            run_required_checks(self.unit, run_name="run-sealed", project_root=self.root)
        self._assert_refusal(cm.exception, "run-sealed")
        self.assertEqual(self._snapshot("run-sealed"), before)
        self.assertFalse(marker.exists())

    def test_rerecording_a_different_verdict_on_sealed_run_changes_nothing(self):
        self._seal("run-sealed", verdict="PASS")
        before = self._snapshot("run-sealed")
        self.assertIsNotNone(before[2])
        src = self._source("other.json", self._envelope("FAIL") | {"fail_reasons": ["AC_UNMET"]})
        with self.assertRaises(ValueError) as cm:
            record_review_envelope(self.unit, "run-sealed", src, project_root=self.root)
        self._assert_refusal(cm.exception, "run-sealed")
        self.assertEqual(self._snapshot("run-sealed"), before)
        self.assertEqual(json.loads(before[2])["gate_verdict"], "PASS")

    def test_command_that_seals_its_own_run_is_executed_but_not_recorded(self):
        """AC-1 ④ — 실행 도중 봉인. 봉인되지 않은 run 에 넘긴 명령 자체가 그 run 을 봉인하면
        명령은 돈다(실행 전에는 봉인이 아니었다). 그러나 결과는 기록되지 않는다 — 기록 직전에 디스크에서 다시 읽는다."""
        run = "run-mid"
        src = self._source("mid.json", self._envelope("PASS"))
        code = ("import sys; sys.path.insert(0, %r); from romeo.evidence import record_review_envelope; "
                "record_review_envelope(%r, %r, %r, project_root=%r)"
                % (str(REPO), self.unit, run, str(src), str(self.root)))
        command = f"{shlex.quote(sys.executable)} -c {shlex.quote(code)}"
        with self.assertRaises(ValueError) as cm:
            run_command(self.unit, command, run_name=run, label="outer-check", project_root=self.root)
        self._assert_refusal(cm.exception, run)
        rec = self._rec(run)
        self.assertEqual(len(rec["commands"]), 1, rec["commands"])
        self.assertEqual(rec["commands"][-1]["id"], REVIEW_RECORD_LABEL)
        self.assertNotIn("outer-check", [c["id"] for c in rec["commands"]])
        names = set(self._snapshot(run)[1] or {})
        self.assertEqual(len(names), 1, names)
        self.assertFalse(any("outer-check" in n for n in names), names)
        self.assertTrue((self.review_dir / f"{run}-reviewer.json").is_file())


class TestUnsealedRunsStillRecord(SealedRunFixture):
    """AC-2 — 봉인 판정의 여집합. 봉인 라벨 기록이 없는 run 넷에는 지금처럼 쓴다."""

    def test_fresh_run_with_no_commands(self):
        self._assert_recorded("run-fresh", "check-1", "true", 0)
        self._assert_recorded("run-fresh", "check-2", "false", 1)

    def test_run_with_only_ordinary_labels(self):
        run_command(self.unit, "true", run_name="run-plain", label="check-1", project_root=self.root)
        self._assert_recorded("run-plain", "check-2", "true", 0)
        self._assert_recorded("run-plain", "check-3", "false", 1)

    def test_run_with_only_defensive_labels_accepts_command_and_envelope(self):
        """③ 정상 검토 순서 — 방어 검사 둘 뒤에 봉투 기록이 들어온다. 이 길이 막히면 어떤 검토도 봉인되지 않는다."""
        self._defensive("run-review")
        self._assert_recorded("run-review", "extra", "true", 0)
        self._assert_recorded("run-review", "extra-fail", "false", 1)
        data = self._envelope("PASS")
        record_review_envelope(self.unit, "run-review", self._source("review.json", data), project_root=self.root)
        got = json.loads((self.review_dir / "run-review-reviewer.json").read_text(encoding="utf-8"))
        self.assertEqual(got, data)
        self.assertEqual(self._rec("run-review")["commands"][-1]["id"], REVIEW_RECORD_LABEL)

    def test_new_run_after_another_run_was_sealed(self):
        """④ 같은 단위의 다른 run 이 봉인된 **뒤에** 만든 새 run — 봉인은 run 단위다, 단위 단위가 아니다."""
        self._seal("run-1")
        self._assert_recorded("run-2", "check-1", "true", 0)
        self._assert_recorded("run-2", "check-2", "false", 1)
        self._defensive("run-2")
        data = self._envelope("FAIL") | {"fail_reasons": ["AC_UNMET"]}
        record_review_envelope(self.unit, "run-2", self._source("run-2.json", data), project_root=self.root)
        got = json.loads((self.review_dir / "run-2-reviewer.json").read_text(encoding="utf-8"))
        self.assertEqual(got, data)
        self.assertEqual(self._rec("run-2")["commands"][-1]["id"], REVIEW_RECORD_LABEL)


class TestSealMarkIsTheLabelConstant(SealedRunFixture):
    """AC-3 — 봉인 표지는 `REVIEW_RECORD_LABEL` 에서 읽고 문자열 **동일성**으로 판정한다."""

    def test_patched_label_moves_the_seal(self):
        patched = "sealed-by-this-test"
        self.assertNotIn(patched, REVIEW_RECORD_LABEL)
        self.assertNotIn(REVIEW_RECORD_LABEL, patched)
        run_command(self.unit, "true", run_name="run-orig", label=REVIEW_RECORD_LABEL, project_root=self.root)
        with mock.patch("romeo.evidence.REVIEW_RECORD_LABEL", patched):
            run_command(self.unit, "true", run_name="run-patched", label=patched, project_root=self.root)
            # 원래 라벨의 기록만 있는 run 은 바꿔친 상태에서 봉인이 아니다
            self._assert_recorded("run-orig", "after", "true", 0)
            # 바꿔친 라벨의 기록이 있는 run 은 봉인이다
            before = self._snapshot("run-patched")
            with self.assertRaises(ValueError) as cm:
                run_command(self.unit, "true", run_name="run-patched", label="after", project_root=self.root)
            self._assert_refusal(cm.exception, "run-patched")
            self.assertEqual(self._snapshot("run-patched"), before)
        # 되돌린 뒤에는 원래 라벨의 run 이 봉인이다
        with self.assertRaises(ValueError):
            run_command(self.unit, "true", run_name="run-orig", label="again", project_root=self.root)

    def test_substring_and_superstring_labels_do_not_seal(self):
        shorter = REVIEW_RECORD_LABEL[:6]
        longer = REVIEW_RECORD_LABEL + "-x"
        self.assertNotEqual(shorter, REVIEW_RECORD_LABEL)
        self.assertIn(shorter, REVIEW_RECORD_LABEL)
        self.assertIn(REVIEW_RECORD_LABEL, longer)
        run_command(self.unit, "true", run_name="run-short", label=shorter, project_root=self.root)
        run_command(self.unit, "true", run_name="run-long", label=longer, project_root=self.root)
        self._assert_recorded("run-short", "after", "true", 0)
        self._assert_recorded("run-long", "after", "true", 0)

    def test_this_file_does_not_spell_the_label(self):
        self.assertEqual(Path(__file__).read_text(encoding="utf-8").count(REVIEW_RECORD_LABEL), 0)


class TestCommandLinePaths(SealedRunFixture):
    """AC-4 — 명령줄 세 경로. 봉인된 run 은 exit 1 + stderr 에 run id 와 「새 run」, 봉인되지 않은 run 은 exit 0."""

    def _cli(self, argv):
        """`--root` 는 `--` 앞에 둔다 — `evidence run` 은 `--` 뒤를 전부 실행할 명령으로 삼는다."""
        cut = argv.index("--") if "--" in argv else len(argv)
        full = [*argv[:cut], "--root", str(self.root), *argv[cut:]]
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(full)
        return rc, out.getvalue(), err.getvalue()

    def _three(self, run, marker):
        src = self._source(f"cli-{run}.json", self._envelope("FAIL") | {"fail_reasons": ["AC_UNMET"]})
        return [
            ["evidence", "run", "--unit", self.unit, "--run", run, "--", f"mkdir -p .harness/probe && touch {marker}"],
            ["evidence", "checks", "--unit", self.unit, "--run", run],
            ["review", "record", "--unit", self.unit, "--run", run, str(src)],
        ]

    def test_sealed_run_refuses_all_three(self):
        self._seal("run-sealed")
        marker = self.root / ".harness" / "probe" / "cli-marker"
        check_marker = self.root / CHECK_MARKER
        for argv in self._three("run-sealed", marker):
            before = self._snapshot("run-sealed")
            rc, out, err = self._cli(argv)
            self.assertEqual(rc, 1, (argv, out, err))
            self.assertIn("run-sealed", err)
            self.assertIn("새 run", err)
            self.assertNotIn("Traceback", out + err)
            self.assertEqual(self._snapshot("run-sealed"), before, argv)
            self.assertFalse(marker.exists())
            self.assertFalse(check_marker.exists())

    def test_unsealed_run_accepts_all_three(self):
        self._defensive("run-open")
        marker = self.root / ".harness" / "probe" / "cli-marker"
        check_marker = self.root / CHECK_MARKER
        for argv in self._three("run-open", marker):
            n = len(self._rec("run-open")["commands"])
            rc, out, err = self._cli(argv)
            self.assertEqual(rc, 0, (argv, out, err))
            self.assertGreater(len(self._rec("run-open")["commands"]), n, argv)
        self.assertTrue(marker.exists())
        self.assertTrue(check_marker.exists())
        self.assertTrue((self.review_dir / "run-open-reviewer.json").is_file())


if __name__ == "__main__":
    unittest.main()
