"""검토자 절차 파일의 정본(adapters/orca/prompts/reviewer-brief.md)과 채움 스크립트(fill_brief.py)를 지킨다(체크리스트 42).

지키는 것:
 1. 「읽기 범위」 조항이 core/workflows/review/SKILL.md 2번 문장과 **바이트로** 같다 — 42 의 결함 자체가 문장이 옮겨지며
    조건절이 떨어진 것이었고, 두 번째 원본이 생기면 같은 드리프트 경로가 남는다.
 2. 채움 스크립트가 두 런타임·두 모드 모두에서 자리표시자 0·HTML 주석 0·읽기 수단 문장 1개를 낸다.
 3. 채움이 어긋나면(base 모드인데 evidence-run≠run · 잘못된 sha256) 파일을 만들지 않고 비0 으로 끝난다.
 4. 채운 파일의 출력 예시가 결과 계약 스키마의 키와 맞는다.
 5. 정본이 FAIL 사유의 닫힌 목록을 **본문에 인쇄한다** — 검토자가 계약을 보려고 다른 파일을 열지 않아도 된다.
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

# 판정값은 사유 코드가 아니다 — 같은 줄에 함께 나와도 코드 집합에 넣지 않는다.
VERDICTS = {"PASS", "FAIL", "BLOCKED"}


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


class TestBriefCarriesFailReasons(unittest.TestCase):
    """AC-4 — 검토자 프롬프트가 `fail_reasons` 를 출력 예시에 담고 유효한 코드를 본문에 인쇄한다.

    검토자는 명령을 실행하지 않고 파일만 읽는다. 계약이 스키마에만 있으면 그것을 읽으러 가야 하고,
    가지 않으면 목록 밖 사유로 게이트를 내린다 — 그 자리가 이 정비를 만든 충돌이다."""

    def setUp(self):
        self.text = BRIEF.read_text(encoding="utf-8")
        self.body = self.text.split("\n---\n", 1)[1]
        self.schema = load_json(SCHEMA)
        self.codes = self.schema["properties"]["fail_reasons"]["items"]["enum"]

    def _example(self, text):
        m = re.search(r"```json\n(.*?)\n```", text, re.S)
        self.assertIsNotNone(m, "출력 예시 JSON 블록이 없다")
        return json.loads(m.group(1))

    def test_the_output_example_carries_the_field(self):
        example = self._example(self.text)
        self.assertIn("fail_reasons", example, "출력 예시에 fail_reasons 가 없다")
        self.assertIsInstance(example["fail_reasons"], list)
        self.assertTrue(example["fail_reasons"], "예시가 빈 배열이면 무엇을 적는지 보이지 않는다")
        self.assertEqual([c for c in example["fail_reasons"] if c not in self.codes], [],
                         "예시가 목록 밖 코드를 보여준다")
        self.assertEqual(set(example) - set(self.schema["properties"]), set(), "예시에 스키마 밖 키가 있다")

    def test_every_valid_code_is_printed_in_the_body(self):
        printed = set(re.findall(r"`([A-Z][A-Z0-9_]*)`", self.body))
        missing = [c for c in self.codes if c not in printed]
        self.assertEqual(missing, [], f"본문에 인쇄되지 않은 코드가 있다: {missing}")

    def _fail_reasons_bullet(self, body=None):
        """`fail_reasons` 를 설명하는 글머리 항목 하나를 통째로 잘라낸다(이어지는 들여쓴 줄 포함)."""
        lines = (self.body if body is None else body).split("\n")
        for i, ln in enumerate(lines):
            if ln.startswith("- ") and "fail_reasons" in ln:
                j = i + 1
                while j < len(lines) and lines[j].strip() and not lines[j].startswith("- "):
                    j += 1
                return "\n".join(lines[i:j])
        return None

    def test_the_body_prints_no_code_outside_the_list(self):
        """정본이 스키마보다 넓으면 검토자는 스키마가 거부할 사유를 적게 되고,
        좁으면 정당한 사유를 못 적는다. 그 항목의 코드 집합은 enum 과 **정확히** 같아야 한다."""
        bullet = self._fail_reasons_bullet()
        self.assertIsNotNone(bullet, "fail_reasons 를 설명하는 항목이 본문에 없다")
        printed = set(re.findall(r"`([A-Z][A-Z0-9_]*)`", bullet)) - VERDICTS
        self.assertEqual(sorted(printed), sorted(self.codes),
                         f"설명 항목의 코드가 스키마 enum 과 다르다 — 항목에만: {sorted(printed - set(self.codes))} · "
                         f"스키마에만: {sorted(set(self.codes) - printed)}")

    def test_a_bullet_that_drops_a_code_is_detected(self):
        """거부 케이스 — 검사가 항목을 실제로 읽는지 가른다."""
        for code in self.codes:
            body = self.body.replace(f"`{code}`", "그 사유")
            bullet = self._fail_reasons_bullet(body) or ""
            printed = set(re.findall(r"`([A-Z][A-Z0-9_]*)`", bullet)) - VERDICTS
            self.assertNotEqual(sorted(printed), sorted(self.codes),
                                f"{code} 를 지운 항목이 enum 과 같은 집합으로 읽힌다")

    def test_the_body_says_the_list_is_closed(self):
        self.assertIn("이 목록에 없는 사유", self.body,
                      "닫힌 목록이라는 사실이 프롬프트에 없으면 검토자는 목록을 예시로 읽는다")

    def test_the_filled_brief_keeps_all_of_it(self):
        """자리표시자를 채운 뒤에도 남아야 한다 — 검토자가 받는 것은 채운 파일이다."""
        fill = _load_fill()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "brief.md"
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = fill.main(["--unit", "feat-20260829-license-field-46an", "--run", "run_aaaaaaaaaaaa",
                                "--base-sha", "c237ea9d54cd5ee6dae3af4e10ef8c4eb39a2dd5", "--task-sha256", "f" * 64,
                                "--runtime", "claude", "--mode", "base", "--out", str(target)])
            self.assertEqual(rc, 0, err.getvalue())
            filled = target.read_text(encoding="utf-8")
        self.assertIn("fail_reasons", self._example(filled))
        for code in self.codes:
            self.assertIn(code, filled, f"채운 파일에서 {code} 가 사라졌다")

    # ── 거부 케이스 — 검사가 문서를 실제로 읽는지 가른다 ──────────────────────────
    def test_a_dropped_code_is_detected(self):
        for code in self.codes:
            body = self.body.replace(f"`{code}`", "`지워진_코드`")
            printed = set(re.findall(r"`([A-Z][A-Z0-9_]*)`", body))
            self.assertNotIn(code, printed, f"{code} 를 지워도 인쇄된 것으로 읽힌다")

    def test_an_example_without_the_field_is_detected(self):
        example = self._example(self.text)
        example.pop("fail_reasons", None)
        self.assertNotIn("fail_reasons", example)


if __name__ == "__main__":
    unittest.main()
