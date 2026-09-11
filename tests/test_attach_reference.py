"""M5 M2 — 부착은 참조다. 확인란 AC-1~AC-8.

하네스 명령이 **읽는 곳**(하네스 저장소)과 **쓰는 곳**(부착 대상)을 나눈다. 그래서 대상에는
산출물만 놓이고 소스 사본이 남지 않는다 — 낡을 사본이 없으면 드리프트도 없다.

같은 분리를 충돌 fixture 에도 적용한다. 대상의 `fixtures/` 를 읽으면 부착 대상에서는 **0종 실행으로
통과한다** — 산출물 0개가 목록 0개와 맞아떨어져 빈 저장소가 통과하던 Q-53 과 같은 모양이다.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from romeo import HARNESS_ROOT
from romeo import attach as A
from romeo.compile import CompileError, split_index_sections, _strip_frontmatter
from romeo.util import load_any

from tests.test_attach_runbook import attach as place_payload

INDEX = HARNESS_ROOT / "core/principles/PROJECT.core.md"
#: 블록이 경로로 가리키는 것. 백틱 토큰 중 `/` 를 담거나 확장자를 가진 것만 본다 —
#: 자리표시자(`<…>`)는 뺀다. 백틱은 이 저장소가 경로를 적는 관례이고, 넓히면 산문 속 낱말이 경로로 읽힌다.
_BACKTICK = re.compile(r"`([^`]+)`")


def romeo(*args, root=None, harness=HARNESS_ROOT):
    cmd = [sys.executable, str(Path(harness) / "bin/romeo"), *args]
    if root is not None:
        cmd += ["--root", str(root)]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(harness))


def files_under(root: Path):
    root = Path(root)
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() or p.is_symlink()}


def outputs_of(root: Path):
    return (load_any(Path(root) / ".harness/compiled.yaml") or {}).get("outputs") or []


def block_paths(text):
    """managed block 에서 경로로 읽을 토큰을 모은다."""
    out = set()
    for tok in _BACKTICK.findall(text):
        tok = tok.strip()
        if "<" in tok or ">" in tok or " " in tok:
            continue
        if "/" in tok or re.search(r"\.[a-z]{2,5}$", tok):
            out.add(tok.rstrip("/"))
    return out


def managed_block(path: Path):
    text = path.read_text(encoding="utf-8")
    start = text.index("<!-- romeo:managed start")
    end = text.index("<!-- romeo:managed end", start)
    return text[start:end]


class TestCompileWritesOnlyOutputs(unittest.TestCase):
    """AC-1 — 빈 디렉터리에 두 명령만 걸면 산출물만 남는다. 소스 사본은 남지 않는다."""

    def test_nothing_but_outputs_is_left_behind(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "payload"
            root.mkdir()
            for cmd in ("compile", "notices"):
                r = romeo(cmd, root=root)
                self.assertEqual(r.returncode, 0, f"{cmd} 실패: {r.stderr or r.stdout}")
            got = files_under(root)
            expected = set(outputs_of(root)) | {".harness/compiled.yaml", "THIRD_PARTY_NOTICES.md"}
            # **양방향으로 본다.** 한쪽만 보면 `outputs` 에 적힌 채 실재하지 않는 항목을 놓친다(검토자 finding).
            # outputs 에 디렉터리가 실리면 그 아래 파일이 개별로 잡힌다 — 접두로 덮는다.
            extra = {rel for rel in got
                     if rel not in expected and not any(rel.startswith(o.rstrip("/") + "/") for o in expected)}
            self.assertEqual(extra, set(),
                             f"산출물 밖의 파일이 남았다 — 소스를 복제하는 구현이다: {sorted(extra)}")
            absent = sorted(o for o in expected if not (root / o).exists())
            self.assertEqual(absent, [],
                             f"outputs 에 적혔는데 실재하지 않는다 — 두 집합이 같지 않다: {absent}")


class TestRootDecidesWhatIsChecked(unittest.TestCase):
    """AC-2 — 판정 명령이 **그 사본을** 본다."""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.payload = Path(cls.td.name) / "payload"
        place_payload(cls.payload)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_a_healthy_copy_passes(self):
        r = romeo("doctor", "--strict", "--scope", "repository", root=self.payload)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_breaking_the_copy_breaks_the_verdict(self):
        rel = next(o for o in outputs_of(self.payload) if (self.payload / o).is_file())
        target = self.payload / rel
        keep = target.read_bytes()
        target.unlink()
        try:
            r = romeo("doctor", "--strict", "--scope", "repository", root=self.payload)
        finally:
            target.write_bytes(keep)
        self.assertNotEqual(r.returncode, 0,
                            "사본의 산출물을 지웠는데 통과했다 — 하네스 저장소를 검사한 것이다")
        self.assertIn(rel, r.stdout + r.stderr)


class TestRequiredPathsMatchTheOutputs(unittest.TestCase):
    """AC-3 — 부착 정본의 목록과 실제 산출물 집합이 같다."""

    def test_the_two_sets_agree(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "payload"
            place_payload(root)
            required = {rel.rstrip("/") for rel in A.required_paths()}
            produced = {o.rstrip("/") for o in outputs_of(root)} | {".harness/compiled.yaml", "THIRD_PARTY_NOTICES.md"}
            # required 는 디렉터리 단위로 덮는다 — produced 의 각 항목은 required 의 어느 항목 아래여야 한다.
            uncovered = {o for o in produced
                         if o not in required and not any(o.startswith(r + "/") for r in required)}
            self.assertEqual(uncovered, set(), f"산출물인데 정본이 요구하지 않는다: {sorted(uncovered)}")
            missing = [rel for rel in required if not A.present(root / rel)]
            self.assertEqual(missing, [], f"정본이 요구하는데 사본에 없다: {missing}")
            self.assertEqual([r for r in required
                              if r in ("core", "adapters", "vendor", "provenance",
                                       "skills/repo-archive", ".harness/bindings.yaml")], [],
                             "소스 트리가 여전히 요구된다")


class TestTheHarnessItselfIsUnchanged(unittest.TestCase):
    """AC-4 — 읽는 곳과 쓰는 곳이 같은 경우의 동작은 그대로다."""

    def test_compile_check_and_doctor_pass_here(self):
        for args in (("compile", "--check"), ("doctor", "--strict", "--scope", "repository")):
            with self.subTest(cmd=args):
                r = romeo(*args)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class TestIndexScopeMarks(unittest.TestCase):
    """AC-5 — 표식을 요구하는 자리와 보는 자리가 같다. 세 가지 잘못된 입력을 각각 거부한다."""

    @staticmethod
    def _index_text():
        _, body = _strip_frontmatter(INDEX.read_text(encoding="utf-8"))
        return body

    def test_every_section_has_exactly_one_valid_mark(self):
        for title, scope, _lines in split_index_sections(self._index_text()):
            with self.subTest(section=title):
                self.assertIn(scope, ("all", "harness-only"))

    @classmethod
    def setUpClass(cls):
        """하네스 사본을 만들어 그 인덱스를 고친다 — AC-5 는 **명령의** 종료 코드와 출력을 요구한다.

        함수에 문자열을 넘겨 예외만 보는 것으로는 `bin/romeo compile` 이 그 문서를 읽는 경로를 지나지 않는다
        (검토자 finding). 원본 저장소의 파일은 건드리지 않는다.
        """
        cls.td = tempfile.TemporaryDirectory()
        cls.harness = Path(cls.td.name) / "harness"
        cls.harness.mkdir(parents=True)
        for rel in ("bin", "romeo", "scenarios", "core", "adapters", "vendor", "provenance", "skills", "fixtures"):
            src = HARNESS_ROOT / rel
            if src.is_dir():
                shutil.copytree(src, cls.harness / rel, symlinks=True)
        (cls.harness / ".harness").mkdir(exist_ok=True)
        shutil.copy2(HARNESS_ROOT / ".harness/bindings.yaml", cls.harness / ".harness/bindings.yaml")
        cls.index = cls.harness / "core/principles/PROJECT.core.md"
        cls.index_keep = cls.index.read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def _refuses(self, mutate, needle):
        """사본의 인덱스를 고치고 `compile` 을 돌려 종료 코드와 출력을 본다."""
        self.index.write_text(mutate(self.index_keep), encoding="utf-8")
        try:
            with tempfile.TemporaryDirectory() as td:
                r = romeo("compile", root=Path(td) / "out", harness=self.harness)
        finally:
            self.index.write_text(self.index_keep, encoding="utf-8")
        self.assertNotEqual(r.returncode, 0, f"잘못된 표식인데 compile 이 통과했다\n{r.stdout}{r.stderr}")
        self.assertIn(needle, r.stdout + r.stderr, f"절 제목이 출력에 없다\n{r.stdout}{r.stderr}")

    def test_a_missing_mark_is_refused(self):
        self._refuses(lambda b: b.replace("<!-- romeo:scope all -->\n", "", 1), "충돌 해소 순서")

    def test_a_value_outside_the_closed_list_is_refused(self):
        self._refuses(lambda b: b.replace("<!-- romeo:scope all -->", "<!-- romeo:scope sometimes -->", 1),
                      "충돌 해소 순서")

    def test_two_marks_in_one_section_are_refused(self):
        self._refuses(lambda b: b.replace("<!-- romeo:scope all -->",
                                          "<!-- romeo:scope all -->\n<!-- romeo:scope harness-only -->", 1),
                      "충돌 해소 순서")


class TestProjectionIsScoped(unittest.TestCase):
    """AC-6 — 부착 대상에는 `all` 절만 간다. 제목이 아니라 **본문 줄**로 본다."""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.payload = Path(cls.td.name) / "payload"
        place_payload(cls.payload)
        _, body = _strip_frontmatter(INDEX.read_text(encoding="utf-8"))
        cls.sections = split_index_sections(body)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    @staticmethod
    def _lines(sections, scope):
        return [ln for _t, s, lines in sections if s == scope for ln in lines if ln.strip()]

    @staticmethod
    def _is_formatting(line):
        """빈 줄·수평선·표 구분선. 어느 소스에도 없으면서 렌더러가 만드는 표에는 늘 나타나므로
        「샜다」와 「원래 거기 있다」를 구별하지 못한다 — 판별에 쓸 수 없다."""
        s = line.strip()
        return (not s) or s == "---" or re.fullmatch(r"\|?[\s|:-]+\|?", s) is not None

    @classmethod
    def _only_in_harness_sections(cls):
        """`harness-only` 절들의 **고유 내용 줄** — 서식 줄과, 다른 소스에도 있는 줄을 뺀 나머지."""
        _, agents = _strip_frontmatter((HARNESS_ROOT / "core/principles/AGENTS.core.md").read_text(encoding="utf-8"))
        elsewhere = ({ln for ln in cls._lines(cls.sections, "all") if not cls._is_formatting(ln)}
                     | {ln for ln in agents.splitlines() if not cls._is_formatting(ln)})
        return [ln for ln in cls._lines(cls.sections, "harness-only")
                if not cls._is_formatting(ln) and ln not in elsewhere]

    def test_harness_only_lines_do_not_reach_the_copy(self):
        unique = self._only_in_harness_sections()
        self.assertTrue(unique, "하네스 전용 절에만 있는 줄이 하나도 없다 — 이 검사가 성립하지 않는다")
        for name in ("CLAUDE.md", "AGENTS.md"):
            block = managed_block(self.payload / name)
            leaked = [ln for ln in unique if ln in block]
            self.assertEqual(leaked, [], f"{name}: 하네스 전용 줄이 대상에 샜다: {leaked[:2]}")

    def test_all_lines_do_reach_the_copy(self):
        for name in ("CLAUDE.md", "AGENTS.md"):
            block = managed_block(self.payload / name)
            missing = [ln for ln in self._lines(self.sections, "all")
                       if not self._is_formatting(ln) and ln not in block]
            self.assertEqual(missing, [], f"{name}: 모든 저장소용 줄이 빠졌다: {missing[:2]}")

    def test_the_harness_itself_gets_both(self):
        """AC-6 뒷절 — 자기 저장소에는 양쪽이 다 있다. 이 절이 없으면 「전부 빼는 구현」도 앞절을 충족한다."""
        for name in ("CLAUDE.md", "AGENTS.md"):
            block = managed_block(HARNESS_ROOT / name)
            for scope in ("all", "harness-only"):
                missing = [ln for ln in self._lines(self.sections, scope)
                           if not self._is_formatting(ln) and ln not in block]
                self.assertEqual(missing, [], f"{name}: 자기 저장소에서 {scope} 줄이 빠졌다: {missing[:2]}")


#: Q-60 이 2026-09-04 에 실측한 다섯 중 **인덱스 절이 가리키던 넷**. 대상 `CLAUDE.md` 가 세션 시작에 읽으라고
#: 지시했고 전부 없었다. 다섯째 `docs/planning/open-questions.md` 는 행동 규범(AGENTS.core.md §12)이 인용하므로
#: 인덱스를 가르는 것으로는 닫히지 않는다 — 이 검사가 요구하지 않고, 그 자리 문제는 발견으로 열려 있다.
Q60_FOUR = ("docs/planning/progress.md", "docs/decisions/decision-register.md",
            "docs/requirements/", "docs/reviews/")


class TestProjectedPathsExist(unittest.TestCase):
    """AC-7 — 인덱스가 가리키던 넷이 대상에 가지 않는다. 하네스 자신에는 그대로 남는다."""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.payload = Path(cls.td.name) / "payload"
        place_payload(cls.payload)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_the_four_do_not_reach_the_copy(self):
        for name in ("CLAUDE.md", "AGENTS.md"):
            block = managed_block(self.payload / name)
            leaked = [p for p in Q60_FOUR if p in block]
            self.assertEqual(leaked, [], f"{name}: 대상에 없는 것을 세션 시작에 읽으라고 한다: {leaked}")

    def test_the_four_stay_in_the_harness_itself(self):
        """검사가 「아무것도 없는 상태」를 통과로 읽지 않는지 — 자기 저장소에는 넷이 그대로 있어야 한다."""
        block = managed_block(HARNESS_ROOT / "CLAUDE.md")
        missing = [p for p in Q60_FOUR if p not in block]
        self.assertEqual(missing, [], f"자기 저장소의 인덱스에서 사라졌다: {missing}")


class TestConflictFixturesRunOnTheTarget(unittest.TestCase):
    """AC-8 — fixture 는 하네스에서 읽고 검사는 대상에 한다."""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.payload = Path(cls.td.name) / "payload"
        place_payload(cls.payload)
        cls.fixture_count = len(list((HARNESS_ROOT / "fixtures/conflicts").glob("*.yaml")))

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_the_copy_runs_every_harness_fixture(self):
        """`doctor` 를 통해 본다 — 함수를 직접 부르면 기본값(읽는 곳 = 쓰는 곳)을 타고, 그것은 부착 실행이 아니다."""
        self.assertFalse((self.payload / "fixtures").exists(), "사본에 fixtures 가 있으면 이 검사가 성립하지 않는다")
        r = romeo("doctor", "--json", root=self.payload)
        self.assertEqual(r.returncode, 0, r.stderr)
        ran = json.loads(r.stdout)["conflicts"]["fixtures_ran"]
        self.assertEqual(ran, self.fixture_count,
                         "사본에서 실행한 fixture 수가 하네스의 fixture 수와 다르다 — 0종 실행은 충돌 0 이 아니다")

    def test_a_conflict_planted_in_the_copy_is_detected(self):
        """대상의 **산출물만으로** 판정하는 fixture(`c2-no-auto-trigger`)를 쓴다.

        `c4-dangerous-instruction` 은 `pattern_requires_override` 라 하네스의 override 가 그 지시를 덮는다 —
        대상에 심어도 통과하는 것이 정상 동작이고, 그것으로는 「fixture 가 대상을 검사했다」를 보일 수 없다.
        """
        hooks = self.payload / ".claude/hooks.json"
        hooks.parent.mkdir(parents=True, exist_ok=True)
        hooks.write_text('{"hooks": {}}\n', encoding="utf-8")
        try:
            r = romeo("doctor", "--strict", "--scope", "repository", root=self.payload)
        finally:
            hooks.unlink()
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"대상에 심은 충돌이 잡히지 않았다\n{out}")
        self.assertIn("c2-no-auto-trigger", out, f"그 fixture 의 id 가 출력에 없다\n{out}")


if __name__ == "__main__":
    unittest.main()
