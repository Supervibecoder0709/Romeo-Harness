"""CI 가 도는 **사건**이 CI 가 읽는 **파일**을 덮는가.

검사가 막는 자리에 있어도 보는 사건이 좁으면 아무것도 막지 못한다(AGENTS.core §11 ①).
`bin/romeo integrity` 는 `docs/current/` 를 읽고 `bin/romeo validate` 는 `docs/work/` 를 읽는데,
워크플로의 `paths:` 에 그 루트가 없으면 문서만 바꾼 커밋에서 둘 다 돌지 않는다 —
판정 표에서 한 행을 지운 커밋이 초록불로 지나간다(Q-90).

**읽는 루트를 이 파일에 다시 적지 않는다.** 두 모듈의 `READ_ROOTS` 에서 가져온다 —
여기 사본을 두면 코드가 새 자리를 읽기 시작해도 이 검사는 옛 목록을 계속 덮고 통과한다.
"""
import ast
import unittest
from pathlib import Path

import yaml

from romeo import integrity, validate

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "harness.yml"
EVENTS = ("push", "pull_request")
#: 검사가 읽는 루트 — 두 모듈이 스스로 선언한 값의 합집합이다.
READ_ROOTS = tuple(sorted(set(validate.READ_ROOTS) | set(integrity.READ_ROOTS)))
#: 문서 변경에서 실제로 돌아야 하는 스텝의 명령.
REQUIRED_STEPS = ("bin/romeo integrity", "bin/romeo validate")
#: 루트를 선언하는 상수의 이름. 이 대입의 우변만 `docs` 리터럴을 담을 수 있다.
ROOT_CONSTANTS = ("WORK_ROOT", "CURRENT_ROOT", "READ_ROOTS", "DOC_PATH")


def load_on(path):
    """워크플로의 `on:` 매핑. YAML 에서 `on` 은 불리언 참으로 읽히므로 두 키를 다 본다."""
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return doc[True] if True in doc else doc["on"]


def covers(pattern, root):
    """패턴이 루트 아래 파일 변경을 덮는가.

    끝의 `/**` 를 떼어낸 문자열이 그 루트와 같거나 그 루트의 **조상 디렉터리**일 때만 참이다.
    `/**` 로 끝나지 않는 패턴은 덮지 않는 것으로 본다 — `docs/current` 는 그 이름의 파일 하나를 뜻하고
    그 아래 파일 변경을 트리거하지 않는다."""
    if not pattern.endswith("/**"):
        return False
    base = pattern[: -len("/**")]
    return root == base or root.startswith(base + "/")


def uncovered(on_mapping, roots=READ_ROOTS, events=EVENTS):
    """덮이지 않은 `(루트, 이벤트)` 쌍의 목록.

    인자로 매핑을 받는다 — 지금 워크플로에도, 그것에서 파생한 사본에도 **같은 판정**을 적용하기 위해서다.
    사본마다 기대값을 따로 적으면 이 함수를 부르지 않고도 원하는 값을 낼 수 있다."""
    out = []
    for event in events:
        paths = list((on_mapping.get(event) or {}).get("paths") or [])
        for root in roots:
            if not any(covers(p, root) for p in paths):
                out.append((root, event))
    return sorted(out)


def negated(on_mapping, events=EVENTS):
    """`!` 로 시작하는 제외 패턴이 실린 `(패턴, 이벤트)` 쌍.

    제외 패턴은 순서에 따라 앞의 포함을 무효로 만든다. 순서까지 해석하는 매처를 만드는 대신
    **이 워크플로에서는 쓰지 않는다**는 규약으로 닫는다 — 규약이 깨지면 여기서 걸린다."""
    return sorted((p, e) for e in events
                  for p in ((on_mapping.get(e) or {}).get("paths") or []) if p.startswith("!"))


def strip_doc_paths(on_mapping, events):
    """`events` 에서만 `docs/` 로 시작하는 패턴을 뺀 사본. 원본은 건드리지 않는다."""
    import copy
    out = copy.deepcopy(on_mapping)
    for e in events:
        out[e]["paths"] = [p for p in out[e]["paths"] if not p.startswith("docs/")]
    return out


class TestReadRootsAreTheSource(unittest.TestCase):
    """AC-1 — `READ_ROOTS` 가 사본이 아니라 실제 출처다."""

    def test_no_path_assembly_outside_root_constants(self):
        """두 모듈에 `docs` 로 시작하는 문자열 리터럴이 루트 상수 정의 밖에 없다.

        docstring 과 루트 상수 대입의 우변은 뺀다 — 앞은 설명이고 뒤는 이 값들의 정의 자체다.
        남는 자리에서 `docs` 로 시작하는 리터럴이 나오면 그것은 경로를 따로 조립했다는 뜻이고,
        곧 `READ_ROOTS` 가 실제 출처가 아니라 사본이라는 뜻이다."""
        offenders = []
        for mod in ("romeo/validate.py", "romeo/integrity.py"):
            path = ROOT / mod
            tree = ast.parse(path.read_text(encoding="utf-8"))
            skip = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign) and {
                        t.id for t in node.targets if isinstance(t, ast.Name)} & set(ROOT_CONSTANTS):
                    skip.update(id(n) for n in ast.walk(node.value))
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    head = node.body[0] if node.body else None
                    if (isinstance(head, ast.Expr) and isinstance(head.value, ast.Constant)
                            and isinstance(head.value.value, str)):
                        skip.add(id(head.value))
            for node in ast.walk(tree):
                if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                        and node.value.startswith("docs") and id(node) not in skip):
                    offenders.append(f"{mod}:{node.lineno} {node.value!r}")
        self.assertEqual([], offenders, "루트 상수 정의 밖에서 docs 경로를 조립한다 — 그것은 사본이다")

    def test_constants_are_actually_used(self):
        """루트 상수를 바꿔치면 두 함수가 **새 루트 아래**를 보고 원래 루트를 보지 않는다."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "work" / "u1").mkdir(parents=True)
            (root / "docs" / "work" / "u1" / "spec.md").write_text("x", encoding="utf-8")
            (root / "elsewhere" / "u2").mkdir(parents=True)
            (root / "elsewhere" / "u2" / "spec.md").write_text("x", encoding="utf-8")

            self.assertEqual(1, len(validate.find_docs(root)))
            original = validate.WORK_ROOT
            try:
                validate.WORK_ROOT = "elsewhere"
                found = [p.as_posix() for p in validate.find_docs(root)]
            finally:
                validate.WORK_ROOT = original
            self.assertEqual(1, len(found), found)
            self.assertIn("elsewhere/u2/spec.md", found[0])

            (root / "docs" / "current").mkdir(parents=True)
            (root / "docs" / "current" / "a.md").write_text("[x](missing.md)", encoding="utf-8")
            (root / "other").mkdir()
            (root / "other" / "b.md").write_text("[x](missing.md)", encoding="utf-8")
            self.assertEqual(1, len(integrity.broken_links(root)))
            original = integrity.CURRENT_ROOT
            try:
                integrity.CURRENT_ROOT = "other"
                links = integrity.broken_links(root)
            finally:
                integrity.CURRENT_ROOT = original
            self.assertEqual(1, len(links), links)
            self.assertIn("other/b.md", links[0])


class TestTriggerCoversReadRoots(unittest.TestCase):
    """AC-2·AC-3·AC-4 — 트리거가 읽는 루트를 덮는가."""

    def setUp(self):
        self.on = load_on(WORKFLOW)

    def test_covers_rule(self):
        """AC-2 — 「덮는다」의 판별 규칙."""
        self.assertTrue(covers("docs/current/**", "docs/current"))
        self.assertTrue(covers("docs/**", "docs/current"))
        self.assertFalse(covers("docs/current", "docs/current"))     # /** 가 없으면 파일 하나다
        self.assertFalse(covers("docs/work/**", "docs/current"))
        self.assertFalse(covers("docs/currently/**", "docs/current"))

    def test_current_workflow_covers_every_root(self):
        """AC-2 — 지금 워크플로는 읽는 루트를 두 이벤트 양쪽에서 덮는다."""
        self.assertEqual([], uncovered(self.on), "덮이지 않은 (루트, 이벤트) 쌍이 있다")

    def test_no_negated_patterns(self):
        """AC-2 ③ — 제외 패턴을 쓰지 않는다."""
        self.assertEqual([], negated(self.on))

    def test_discriminates_per_event(self):
        """AC-3 — 같은 판정 함수에 세 입력을 넣는다. 차이는 인자뿐이다."""
        push_only = uncovered(strip_doc_paths(self.on, ("push",)))
        pr_only = uncovered(strip_doc_paths(self.on, ("pull_request",)))
        self.assertTrue(push_only, "push 에서 문서 패턴을 빼면 미덮임이 나와야 한다")
        self.assertTrue(pr_only, "pull_request 에서 빼면 미덮임이 나와야 한다")
        self.assertEqual({"push"}, {e for _r, e in push_only})
        self.assertEqual({"pull_request"}, {e for _r, e in pr_only})
        self.assertEqual([], uncovered(self.on))

    def test_required_paths_present(self):
        """AC-4 ① — 네 항목이 실재한다."""
        for event in EVENTS:
            for path in ("docs/current/**", "docs/work/**"):
                self.assertIn(path, self.on[event]["paths"], f"{event}.paths 에 {path} 가 없다")

    def test_no_branch_filter(self):
        """AC-4 ③ — `branches`/`branches-ignore` 로 실행 브랜치를 좁히지 않는다."""
        for event in EVENTS:
            self.assertEqual([], [k for k in self.on[event] if k.startswith("branches")])

    def test_checks_run_unconditionally(self):
        """AC-4 ④ — 두 검사 스텝이 실재하고, 그 스텝과 job 에 `if:` 가 없다."""
        doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        for job_name, job in doc["jobs"].items():
            runs = {(s.get("run") or "").strip(): s for s in job["steps"]}
            hits = [c for c in REQUIRED_STEPS if c in runs]
            if not hits:
                continue
            self.assertEqual(sorted(REQUIRED_STEPS), sorted(hits), f"{job_name} 에 검사 스텝이 빠졌다")
            self.assertNotIn("if", job, f"job {job_name} 에 if: 가 있다 — 조건부로 건너뛸 수 있다")
            for cmd in hits:
                self.assertNotIn("if", runs[cmd], f"스텝 «{cmd}» 에 if: 가 있다")
            return
        self.fail(f"어느 job 에도 {REQUIRED_STEPS} 스텝이 없다")


if __name__ == "__main__":
    unittest.main()
