"""M5 M1 — `doctor` 가 부착 정본을 읽는다. 확인란 AC-1~AC-9.

정본은 `scenarios/10-attach-payload.md` 의 「놓는 것」 절이고, 그것을 읽는 코드는
`romeo/attach.py` 다. 이 검사가 보는 것은 **`doctor` 가 그 정본을 읽어 판정하는가**이다 —
목록을 코드에 복사한 구현은 `TestTheRunbookIsWhatDoctorReads` 에서 걸린다.

이 파일이 있는 이유는 요구하는 자리와 보는 자리가 갈려 있었기 때문이다.
`tests/test_attach_runbook.py` 는 정본을 읽는데 `doctor` 는 읽지 않았고, 그 구멍을
런북의 「4번을 단독으로 쓰지 않는다」는 **주의**가 메우고 있었다. 주의는 집행이 아니다(§11).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from romeo import HARNESS_ROOT
from romeo import attach as A

from tests.test_attach_runbook import attach as place_payload

DOCTOR = ("doctor", "--strict", "--scope", "repository")


def run_doctor(root, harness=HARNESS_ROOT):
    """판정 명령. **하네스 저장소 안에서** 실행하고 `--root` 로 대상을 가리킨다."""
    r = subprocess.run([sys.executable, str(Path(harness) / "bin/romeo"), *DOCTOR, "--root", str(root)],
                       capture_output=True, text=True, cwd=str(harness))
    return r.returncode, r.stdout + r.stderr


def compiled_state(root):
    from romeo.util import load_any
    return load_any(Path(root) / ".harness/compiled.yaml") or {}


def write_compiled_state(root, state):
    from romeo.util import dump_yaml
    p = Path(root) / ".harness/compiled.yaml"
    p.write_text("---\n" + dump_yaml(state), encoding="utf-8")


class TestUnattachedRootIsRefused(unittest.TestCase):
    """AC-1 — 부재를 통과로 읽지 않는다. 그리고 **무엇 때문에** 실패했는지 말한다."""

    def test_empty_root_fails_with_the_finding_and_the_missing_paths(self):
        with tempfile.TemporaryDirectory() as td:
            code, out = run_doctor(td)
        self.assertNotEqual(code, 0, f"빈 루트가 통과했다 — 부재가 일치로 읽힌다(Q-53)\n{out}")
        self.assertIn("ATTACH_INCOMPLETE", out, f"실패 사유를 말하지 않는다 — 종료 코드만으로는 무엇 때문인지 모른다\n{out}")
        for rel in A.required_paths():
            self.assertIn(rel.rstrip("/"), out, f"빠진 경로 {rel} 가 출력에 없다\n{out}")


class TestAttachedRootsPass(unittest.TestCase):
    """AC-2·AC-3 — 하네스 저장소 자신과 부착 사본이 각각 통과한다."""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.payload = Path(cls.td.name) / "payload"
        place_payload(cls.payload)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_the_harness_repo_itself_passes(self):
        code, out = run_doctor(HARNESS_ROOT)
        self.assertEqual(code, 0, f"하네스 저장소 자신이 실패했다\n{out}")

    def test_an_attached_copy_passes(self):
        code, out = run_doctor(self.payload)
        self.assertEqual(code, 0, f"완전히 부착한 사본이 실패했다 — 거꾸로 판정한다(Q-55)\n{out}")


class TestRemovingARequiredPathFails(unittest.TestCase):
    """AC-4 — 요구된 경로 하나를 지우면 그 경로를 지목하며 막는다."""

    def test_each_required_path_is_actually_required(self):
        for rel in A.required_paths():
            with self.subTest(path=rel):
                with tempfile.TemporaryDirectory() as td:
                    payload = Path(td) / "payload"
                    place_payload(payload)
                    target = payload / rel.rstrip("/")
                    if target.is_dir():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                    code, out = run_doctor(payload)
                self.assertNotEqual(code, 0, f"{rel} 를 지웠는데 통과했다\n{out}")
                self.assertIn("ATTACH_INCOMPLETE", out)
                self.assertIn(rel.rstrip("/"), out, f"지워진 경로 {rel} 가 출력에 없다\n{out}")


class TestTheRunbookIsWhatDoctorReads(unittest.TestCase):
    """AC-5 — 정본을 바꾸면 판정이 따라온다. **양방향**으로 본다.

    한 방향만 보면 「문서가 달라지면 무조건 실패하는 구현」이 통과한다 — 그 구현은
    더한 경로를 사본에 놓아도 여전히 실패하므로 뒤쪽에서 걸린다.
    런북을 고치는 대상은 **하네스 사본**이다. 원본 저장소의 파일은 건드리지 않는다.
    """

    EXTRA = "docs/attach-marker.md"

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.harness = Path(cls.td.name) / "harness"
        cls.harness.mkdir(parents=True)
        for rel in ("bin", "romeo", "scenarios", "core", "adapters", "vendor", "provenance", "skills", "fixtures"):
            src = HARNESS_ROOT / rel
            if src.is_dir():
                shutil.copytree(src, cls.harness / rel)
        (cls.harness / ".harness").mkdir(exist_ok=True)
        shutil.copy2(HARNESS_ROOT / ".harness/bindings.yaml", cls.harness / ".harness/bindings.yaml")
        cls._add_line_to_runbook(cls.harness / "scenarios/10-attach-payload.md", cls.EXTRA)
        cls.payload = Path(cls.td.name) / "payload"
        place_payload(cls.payload)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    @staticmethod
    def _add_line_to_runbook(path, rel):
        lines = path.read_text(encoding="utf-8").splitlines()
        start = next(i for i, ln in enumerate(lines) if ln.strip() == A.PLACE_HEADING)
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        insert = max(i for i in range(start, end) if lines[i].startswith("- `")) + 1
        lines.insert(insert, f"- `{rel}` — 이 검사가 더한 줄. 정본을 읽는지 보기 위한 것이다")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_the_added_path_is_required_when_absent(self):
        self.assertIn(self.EXTRA, A.required_paths(self.harness / "scenarios/10-attach-payload.md"),
                      "더한 줄이 목록에 읽히지 않았다 — 이 검사 자체가 성립하지 않는다")
        code, out = run_doctor(self.payload, harness=self.harness)
        self.assertNotEqual(code, 0, f"정본에 더한 경로를 요구하지 않는다 — 목록을 코드에 복사한 구현이다\n{out}")
        self.assertIn(self.EXTRA, out, f"더한 경로가 출력에 없다\n{out}")

    def test_the_added_path_satisfies_when_present(self):
        with tempfile.TemporaryDirectory() as td:
            payload = Path(td) / "payload"
            place_payload(payload)
            marker = payload / self.EXTRA
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("이 검사가 놓은 파일이다.\n", encoding="utf-8")
            code, out = run_doctor(payload, harness=self.harness)
        self.assertEqual(code, 0, f"더한 경로를 놓았는데도 실패했다 — 문서 변경만으로 무조건 막는 구현이다\n{out}")


class TestSkillScopeIsWhatTheHarnessPlaced(unittest.TestCase):
    """AC-6 — 스킬 검사가 판정에 세는 것은 하네스가 놓은 것뿐이다.

    안팎을 **같은 오류 종류**(심링크)로 본다. 종류를 달리하면 「범위를 좁혔는가」와
    「그 검사를 없앴는가」가 구별되지 않는다.
    """

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.payload = Path(cls.td.name) / "payload"
        place_payload(cls.payload)
        cls.owned = cls._an_owned_skill(cls.payload)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    @staticmethod
    def _an_owned_skill(root):
        outputs = compiled_state(root).get("outputs") or []
        for rel in outputs:
            p = root / rel
            if p.name == "SKILL.md" and p.is_file():
                return rel
        raise AssertionError("outputs 에 SKILL.md 산출물이 없다 — 이 검사가 성립하지 않는다")

    @staticmethod
    def _make_symlink_in_place(path: Path):
        """내용은 그대로 두고 그 자리만 심링크로 바꾼다 — 내용 대조는 통과하고 심링크 검사만 걸린다."""
        real = path.with_name(path.name + ".real")
        shutil.move(str(path), str(real))
        path.symlink_to(real.name)

    def test_a_symlink_outside_the_outputs_does_not_change_the_verdict(self):
        d = self.payload / ".claude/skills/foreign-skill"
        d.mkdir(parents=True, exist_ok=True)
        real = d / "SKILL.real.md"
        real.write_text("---\nname: foreign-skill\ndescription: 대상이 원래 갖고 있던 스킬이다\n---\n\n본문\n",
                        encoding="utf-8")
        (d / "SKILL.md").symlink_to(real.name)
        try:
            code, out = run_doctor(self.payload)
        finally:
            shutil.rmtree(d)
        self.assertEqual(code, 0, f"목록 밖의 심링크 스킬이 부착 실패로 세어졌다(Q-55)\n{out}")

    def test_a_symlink_inside_the_outputs_does_change_the_verdict(self):
        path = self.payload / self.owned
        self._make_symlink_in_place(path)
        try:
            code, out = run_doctor(self.payload)
        finally:
            real = path.with_name(path.name + ".real")
            path.unlink()
            shutil.move(str(real), str(path))
        self.assertNotEqual(code, 0, f"목록 안의 심링크가 판정을 바꾸지 않았다 — 범위를 좁힌 것이 아니라 검사를 없앤 것이다\n{out}")


class TestHarnessRevisionIsRecorded(unittest.TestCase):
    """AC-7 — 부착된 저장소에서 어느 리비전이 붙었는지 읽을 수 있다.

    두 값을 **같은 실행 안에서** 읽어 비교한다. 검토 시점의 HEAD 와 비교하면
    그 사이에 커밋이 늘었을 때 당시의 일치를 확인할 수 없다.
    """

    def test_compile_records_the_head_it_ran_from(self):
        head = subprocess.run(["git", "-C", str(HARNESS_ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True)
        if head.returncode != 0:
            self.skipTest("하네스 저장소가 git 이 아니다")
        with tempfile.TemporaryDirectory() as td:
            payload = Path(td) / "payload"
            place_payload(payload)
            recorded = compiled_state(payload).get("harness_revision")
        self.assertEqual(recorded, head.stdout.strip(),
                         "부착 사본에 기록된 리비전이 그것을 만든 하네스 HEAD 와 다르다")


class TestRevisionIsChecked(unittest.TestCase):
    """AC-8·AC-9 — 리비전을 요구하는 자리와 보는 자리를 같게 둔다."""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.payload = Path(cls.td.name) / "payload"
        place_payload(cls.payload)
        cls.original = compiled_state(cls.payload)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def _with_revision(self, value):
        state = dict(self.original)
        if value is None:
            state.pop("harness_revision", None)
        else:
            state["harness_revision"] = value
        write_compiled_state(self.payload, state)
        try:
            return run_doctor(self.payload)
        finally:
            write_compiled_state(self.payload, self.original)

    def test_a_missing_key_is_refused(self):
        code, out = self._with_revision(None)
        self.assertNotEqual(code, 0, f"harness_revision 키가 없는데 통과했다\n{out}")
        self.assertIn("ATTACH_REVISION_MISSING", out)

    def test_an_empty_value_is_refused(self):
        code, out = self._with_revision("")
        self.assertNotEqual(code, 0, f"harness_revision 이 빈 값인데 통과했다\n{out}")
        self.assertIn("ATTACH_REVISION_MISSING", out)

    def test_a_commit_that_does_not_exist_here_is_refused(self):
        code, out = self._with_revision("0" * 39 + "1")
        self.assertNotEqual(code, 0, f"실재하지 않는 커밋인데 통과했다\n{out}")
        self.assertIn("ATTACH_REVISION_UNKNOWN", out)

    def test_an_uppercase_hex_that_does_not_exist_here_is_refused(self):
        """AC-9 의 「40자 hex」에는 대문자도 든다. 소문자만 받으면 그럴듯한 거짓 값이 조용히 통과한다."""
        code, out = self._with_revision("A" * 39 + "B")
        self.assertNotEqual(code, 0, f"대문자 hex 인 실재하지 않는 커밋이 통과했다\n{out}")
        self.assertIn("ATTACH_REVISION_UNKNOWN", out)


if __name__ == "__main__":
    unittest.main()
