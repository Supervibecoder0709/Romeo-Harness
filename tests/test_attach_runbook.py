"""부착 판정 — `scenarios/10-attach-payload.md` 의 「놓는 것」 목록을 **파일에서 읽어** 루트와 대조한다.

이 검사가 있는 이유는 부착 검증이 **부재를 통과로 읽었기** 때문이다. 아무것도 부착하지 않은 저장소에
`.harness/compiled.yaml`(`outputs: []`)과 빈 `THIRD_PARTY_NOTICES.md` 만 놓으면
`romeo doctor --strict --scope repository` 가 exit 0 을 낸다 — 산출물 0개가 목록 0개와 일치하고,
vendor import 0건이 0건과 일치하고, 충돌 fixture 0종에서 충돌이 0건이기 때문이다(2026-09-04 실측 · Q-53).
세 검사가 전부 참인데 그 저장소에는 하네스가 없다.

**목록의 주인은 이 파일이 아니라 런북이다.** 여기에 경로를 못 박으면 문서와 검사가 갈리고,
갈린 뒤에는 어느 쪽이 요구인지 말할 수 없다(§11 — 요구하는 자리와 보는 자리를 같게 둔다).
그래서 `required_paths()` 가 런북을 읽고, `TestTheListIsWhatIsCompared` 가 **목록을 바꿔 넣어**
바뀐 목록으로 대조된다는 것을 매번 재확인한다. 목록에서 한 항목을 빼면 그 항목은 조용히 건너뛰어지는 것이
아니라 요구에서 사라지고, 그럴듯한 거짓 항목을 더하면 그 자리에서 막힌다.
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from romeo import HARNESS_ROOT

RUNBOOK = HARNESS_ROOT / "scenarios/10-attach-payload.md"
PLACE_HEADING = "## 놓는 것"

#: 런북이 「놓는 것」 절에서 손으로 복사하라고 적는 소스 트리. 부착의 입력이다.
SOURCE_TREE = ["core/", "adapters/", "vendor/", "provenance/", "skills/repo-archive/", ".harness/bindings.yaml"]

#: `- ` 로 시작하고 백틱 경로가 첫 토큰인 줄만 필수 경로로 읽는다. 런북의 「목록의 문법」과 같은 규칙이다.
_ITEM = re.compile(r"^-\s+`([^`]+)`")


def required_paths(runbook_path):
    """런북의 「## 놓는 것」 절에서 필수 경로 목록을 읽는다. 문서가 목록의 주인이다."""
    text = Path(runbook_path).read_text(encoding="utf-8")
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == PLACE_HEADING)
    except StopIteration:
        raise AssertionError(f"{runbook_path}: '{PLACE_HEADING}' 절이 없다 — 목록을 읽을 자리가 없다")
    out = []
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        m = _ITEM.match(ln)
        if m:
            out.append(m.group(1))
    if not out:
        raise AssertionError(f"{runbook_path}: '{PLACE_HEADING}' 절에 백틱 경로 목록이 없다")
    return out


def _present(target: Path) -> bool:
    """**부재를 통과로 읽지 않는다.** 이름만 있는 빈 디렉터리·빈 파일은 놓인 것이 아니다."""
    if target.is_symlink() and not target.exists():
        return False
    if target.is_dir():
        return any(p.is_file() and p.stat().st_size > 0 for p in target.rglob("*"))
    if target.is_file():
        return target.stat().st_size > 0
    return False


def check(root, paths):
    """`paths` 중 `root` 에 놓이지 않은 것을 순서대로 돌려준다. 빈 목록이 부착됨이다."""
    root = Path(root)
    return [rel for rel in paths if not _present(root / rel.rstrip("/"))]


def _romeo(*args, root):
    return subprocess.run([sys.executable, str(HARNESS_ROOT / "bin/romeo"), *args, "--root", str(root)],
                          capture_output=True, text=True)


def attach(root: Path):
    """런북의 「놓는 것」 순서를 그대로 밟는다 — 소스 트리 여섯 → compile → notices."""
    root.mkdir(parents=True, exist_ok=True)
    for rel in SOURCE_TREE:
        src, dst = HARNESS_ROOT / rel.rstrip("/"), root / rel.rstrip("/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    for cmd in (("compile",), ("notices",)):
        r = _romeo(*cmd, root=root)
        if r.returncode != 0:
            raise AssertionError(f"부착 중 `romeo {cmd[0]}` 실패 (exit {r.returncode}): {r.stderr or r.stdout}")


class TestListComesFromTheRunbook(unittest.TestCase):
    """AC-2 앞부분 — 목록을 파일에서 읽는다."""

    def test_the_runbook_owns_the_list(self):
        paths = required_paths(RUNBOOK)
        # 소스 트리 여섯이 전부 목록에 있다. 하나라도 빠지면 그 저장소에서 compile 이 산출물 0개로 '성공'한다.
        for rel in SOURCE_TREE:
            self.assertIn(rel, paths, f"{rel} 이 런북 「놓는 것」 목록에 없다")
        # compile·notices 산출물도 부착의 일부다 — 소스만 놓고 컴파일하지 않은 상태는 부착이 아니다.
        for rel in [".harness/compiled.yaml", "CLAUDE.md", "AGENTS.md", ".claude/settings.json",
                    ".claude/agents/", ".claude/skills/", ".agents/skills/", "THIRD_PARTY_NOTICES.md"]:
            self.assertIn(rel, paths, f"{rel} 이 런북 「놓는 것」 목록에 없다")

    def test_a_runbook_without_the_section_is_refused(self):
        """그럴듯한 거짓 값 — 절 제목만 바꿔도 검사는 조용히 0건으로 통과하지 않는다."""
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "runbook.md"
            fake.write_text(RUNBOOK.read_text(encoding="utf-8").replace(PLACE_HEADING, "## 놓을 것"),
                            encoding="utf-8")
            with self.assertRaises(AssertionError):
                required_paths(fake)


class TestAttachedAndUnattachedRoots(unittest.TestCase):
    """AC-3 — 부착되지 않은 경로에서 실패하고 부착된 경로에서 통과한다. 두 루트를 여기서 각각 만든다."""

    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        cls.paths = required_paths(RUNBOOK)
        cls.attached = Path(cls._td.name) / "attached"
        attach(cls.attached)

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def test_unattached_root_fails(self):
        with tempfile.TemporaryDirectory() as td:
            missing = check(td, self.paths)
        self.assertEqual(missing, self.paths, "빈 루트에서 빠진 것이 목록 전체가 아니다")

    def test_attached_root_passes(self):
        self.assertEqual(check(self.attached, self.paths), [])

    def test_empty_placeholders_do_not_pass(self):
        """그럴듯한 거짓 값 — 이름만 만든 빈 디렉터리·빈 파일은 부착이 아니다(부재를 통과로 읽지 않는다)."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for rel in self.paths:
                target = root / rel.rstrip("/")
                if rel.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("", encoding="utf-8")
            self.assertEqual(check(root, self.paths), self.paths,
                             "빈 자리표시자가 부착으로 읽혔다")

    def test_the_runbook_rollback_covers_what_was_placed(self):
        """되돌리기 명령이 놓은 것을 전부 덮는가 — 어긋나면 부착분이 대상에 남는다."""
        text = RUNBOOK.read_text(encoding="utf-8")
        for rel in self.paths:
            top = rel.rstrip("/").split("/")[0]
            self.assertIn(top, text.split("## 되돌리기", 1)[1],
                          f"되돌리기 절이 '{top}' 를 지우지 않는다")


class TestTheListIsWhatIsCompared(unittest.TestCase):
    """AC-2 뒷부분 — 목록을 바꿔 넣어 **바뀐 목록으로 대조한다**는 것을 재확인한다."""

    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        cls.attached = Path(cls._td.name) / "attached"
        attach(cls.attached)
        cls.paths = required_paths(RUNBOOK)

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def _runbook_with(self, replace, into):
        td = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, td)
        fake = Path(td) / "runbook.md"
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn(replace, text, f"런북에 '{replace}' 줄이 없다 — 바꿔 넣을 자리가 사라졌다")
        fake.write_text(text.replace(replace, into, 1), encoding="utf-8")
        return fake

    def test_removing_an_item_removes_the_requirement(self):
        """`vendor/` 를 목록에서 빼면, vendor 가 없는 루트가 **통과한다** — 건너뛰는 것이 아니라 요구가 사라진다."""
        line = "- `vendor/` "
        mutated = required_paths(self._runbook_with(line, "그 줄을 지운다 — "))
        self.assertNotIn("vendor/", mutated)
        self.assertEqual(len(mutated), len(self.paths) - 1)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "no-vendor"
            shutil.copytree(self.attached, root)
            shutil.rmtree(root / "vendor")
            self.assertEqual(check(root, self.paths), ["vendor/"], "원래 목록이 vendor 부재를 잡지 못했다")
            self.assertEqual(check(root, mutated), [], "바뀐 목록이 여전히 vendor 를 요구한다")

    def test_adding_a_plausible_false_item_blocks(self):
        """그럴듯한 거짓 값 — 형태는 하네스 경로인데 존재하지 않는 항목을 더하면 부착된 루트가 막힌다."""
        fake_path = "core/principles/ATTACH.core.md"
        mutated = required_paths(
            self._runbook_with("- `.harness/bindings.yaml` ", f"- `{fake_path}` — 그럴듯한 거짓 값\n- `.harness/bindings.yaml` "))
        self.assertIn(fake_path, mutated)
        self.assertEqual(check(self.attached, self.paths), [], "부착된 루트가 원래 목록에서 막혔다")
        self.assertEqual(check(self.attached, mutated), [fake_path],
                         "더한 항목이 대조에 쓰이지 않았다")


if __name__ == "__main__":
    unittest.main()
