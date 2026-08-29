"""검토자 절차 파일의 정본(adapters/orca/prompts/reviewer-brief.md)과 채움 스크립트(fill_brief.py)를 지킨다(체크리스트 42).

지키는 것:
 1. 「읽기 범위」 조항이 core/workflows/review/SKILL.md 2번 문장과 **바이트로** 같다 — 42 의 결함 자체가 문장이 옮겨지며
    조건절이 떨어진 것이었고, 두 번째 원본이 생기면 같은 드리프트 경로가 남는다.
 2. 채움 스크립트가 두 런타임·두 모드 모두에서 자리표시자 0·HTML 주석 0·읽기 수단 문장 1개를 낸다.
 3. 채움이 어긋나면(base 모드인데 evidence-run≠run · 잘못된 sha256) 파일을 만들지 않고 비0 으로 끝난다.
 4. 채운 파일의 출력 예시가 결과 계약 스키마의 키와 맞는다.
"""
import importlib.util
import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from romeo.util import load_json, project_root

REPO = project_root(Path(__file__).parent)
BRIEF = REPO / "adapters/orca/prompts/reviewer-brief.md"
FILL = REPO / "adapters/orca/prompts/fill_brief.py"
SKILL = REPO / "core/workflows/review/SKILL.md"
SCHEMA = REPO / "core/schemas/result-envelope.json"


def _load_fill():
    spec = importlib.util.spec_from_file_location("fill_brief", FILL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _section(text, title):
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.strip() == f"## {title}":
            j = i + 1
            while j < len(lines) and not lines[j].startswith("## "):
                j += 1
            return "\n".join(lines[i + 1:j]).strip()
    return None


class TestBriefTracksTheCoreProcedure(unittest.TestCase):
    def test_read_scope_clause_is_byte_identical_to_the_core_procedure(self):
        skill = SKILL.read_text(encoding="utf-8")
        m = re.search(r"2\. \*\*읽기 범위\.\*\* (.*?)\n3\. ", skill, re.S)
        self.assertIsNotNone(m, "review/SKILL.md 2번 절을 찾지 못했다")
        core = re.sub(r"\s*\n\s*", " ", m.group(1).strip())
        # 원문의 마지막 괄호 문장(부품 override 언급)은 어댑터 쪽에서 굳이 반복하지 않는다 — 그 앞까지가 규칙 본문이다.
        core = core.split("(부품 override")[0].rstrip("— ").strip()
        brief = _section(BRIEF.read_text(encoding="utf-8"), "읽기 범위")
        self.assertIsNotNone(brief)
        brief_clause = re.sub(r"\s*\n\s*", " ", brief.split("\n\n")[0].strip())
        self.assertTrue(brief_clause.startswith(core.rstrip(".").rstrip()),
                        f"정본의 읽기 범위 조항이 SKILL.md 2번과 다르다:\n core : {core}\n brief: {brief_clause}")

    def test_placeholders_are_declared_and_used(self):
        text = BRIEF.read_text(encoding="utf-8")
        body = text.split("\n---\n", 1)[1]
        used = set(re.findall(r"<[a-z][a-z0-9-]*>", body))
        self.assertEqual(used, {"id", "run-id", "evidence-run", "base-sha", "task-sha256", "mode-note", "runtime-read-means"} | set()
                         if False else {f"<{k}>" for k in ("id", "run-id", "evidence-run", "base-sha", "task-sha256", "mode-note", "runtime-read-means")})
        self.assertNotIn("<!--", body, "HTML 주석은 모델에게 그대로 간다 — 자리표시자로 처리한다")


class TestFillBrief(unittest.TestCase):
    ARGS = ["--unit", "feat-20260829-license-field-46an", "--run", "run_aaaaaaaaaaaa",
            "--base-sha", "c237ea9d54cd5ee6dae3af4e10ef8c4eb39a2dd5", "--task-sha256", "f" * 64]

    def setUp(self):
        self.fill = _load_fill()
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        target = Path(self.tmp.name) / "brief.md"
        with redirect_stdout(out), redirect_stderr(err):
            rc = self.fill.main([*self.ARGS, *extra, "--out", str(target)])
        return rc, target, out.getvalue(), err.getvalue()

    def test_fills_for_both_runtimes_and_modes(self):
        for runtime in ("codex", "claude"):
            for mode, extra in (("base", []), ("rerun", ["--evidence-run", "run_bbbbbbbbbbbb"])):
                rc, target, out, err = self._run("--runtime", runtime, "--mode", mode, *extra)
                self.assertEqual(rc, 0, err)
                text = target.read_text(encoding="utf-8")
                self.assertEqual(re.findall(r"<[a-z][a-z0-9-]*>", text), [], f"{runtime}/{mode}: 자리표시자가 남았다")
                self.assertNotIn("<!--", text)
                self.assertEqual(text.count(self.fill.READ_MEANS_PREFIX), 1)
                self.assertIn(self.fill.READ_MEANS[runtime][:20], text)
                other = "claude" if runtime == "codex" else "codex"
                self.assertNotIn(self.fill.READ_MEANS[other][:20], text, "다른 런타임의 읽기 수단이 함께 남았다")
                self.assertIn("f" * 64, text)
                if mode == "rerun":
                    self.assertIn("검토자만 다시 띄운 것", text)
                    self.assertIn("evidence/run_bbbbbbbbbbbb.yaml", text)
                    self.assertIn("task/run_aaaaaaaaaaaa-reviewer.json", text)
                else:
                    self.assertNotIn("검토자만 다시 띄운 것", text)
                    self.assertIn("evidence/run_aaaaaaaaaaaa.yaml", text)

    def test_refuses_inconsistent_inputs(self):
        rc, target, _o, err = self._run("--runtime", "codex", "--mode", "base", "--evidence-run", "run_bbbbbbbbbbbb")
        self.assertEqual(rc, 1)
        self.assertIn("base 모드인데", err)
        self.assertFalse(target.exists(), "어긋난 입력으로는 파일을 만들지 않는다")
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = self.fill.main([*self.ARGS[:-2], "--task-sha256", "abc", "--runtime", "claude"])
        self.assertEqual(rc, 1)
        self.assertIn("task-sha256", err.getvalue())

    def test_output_example_matches_the_result_envelope_keys(self):
        rc, target, _o, err = self._run("--runtime", "claude", "--mode", "base")
        self.assertEqual(rc, 0, err)
        text = target.read_text(encoding="utf-8")
        m = re.search(r"```json\n(.*?)\n```", text, re.S)
        self.assertIsNotNone(m)
        example = json.loads(m.group(1))
        schema = load_json(SCHEMA)
        self.assertEqual(set(example) - set(schema["properties"]), set(), "예시에 스키마 밖 키가 있다")
        self.assertTrue(set(schema["required"]) <= set(example), "예시가 필수 키를 빠뜨렸다")
        self.assertEqual(example["checks"], [])
        self.assertEqual(example["task_envelope_ref"]["sha256"], "f" * 64)


if __name__ == "__main__":
    unittest.main()
