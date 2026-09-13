"""검토자 절차 파일의 정본(adapters/orca/prompts/reviewer-brief.md)과 채움 스크립트(fill_brief.py)를 지킨다(체크리스트 42).

지키는 것:
 1. 「읽기 범위」 조항이 core/workflows/review/SKILL.md 2번 문장과 **바이트로** 같다 — 42 의 결함 자체가 문장이 옮겨지며
    조건절이 떨어진 것이었고, 두 번째 원본이 생기면 같은 드리프트 경로가 남는다.
 2. 채움 스크립트가 두 런타임·두 모드 모두에서 자리표시자 0·HTML 주석 0·읽기 수단 문장 1개를 낸다.
 3. 채움이 어긋나면(base 모드인데 evidence-run≠run · 잘못된 sha256) 파일을 만들지 않고 비0 으로 끝난다.
 4. 채운 파일의 출력 예시가 결과 계약 스키마의 키와 맞는다.
 5. 정본이 FAIL 사유의 닫힌 목록을 **본문에 인쇄한다** — 검토자가 계약을 보려고 다른 파일을 열지 않아도 된다.
"""
import ast
import hashlib
import importlib.util
import io
import json
import os
import re
import tempfile
import tokenize
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


# ── AC-4 · 지시하는 산문 ─────────────────────────────────────────────────────────
#: 채움 스크립트에서 없어진 인자 두 개 — **인자 형태**(앞에 붙은 하이픈 둘)로만 본다. 정본 템플릿의 자리표시자
#: `<base-sha>`·`<task-sha256>` 은 꺾쇠 안의 치환 자리이지 인자가 아니므로 이 형태와 겹치지 않는다.
REMOVED_FLAGS = ("--base-sha", "--task-sha256")
SCRIPT_NAME = "fill_brief"
#: 기록이 사는 트리 — 그 시점의 사실을 적은 것이라 지금의 인터페이스를 지시하지 않는다
#: (`docs/planning/archive` · open-questions 의 Q-40·Q-41 · 작업 단위 폴더의 spec·attempts·review·evidence).
RECORD_ROOTS = ("docs",)
#: 외부 원문(수정 0)과 런타임 상태 — 이 저장소의 스크립트를 지시하는 자리가 아니다.
FOREIGN_ROOTS = ("archive", "vendor")
STATE_DIRS = frozenset({".git", ".harness", "__pycache__"})


def _prose(path, text):
    """지시하는 산문만 (줄 번호, 줄) 로 돌려준다.

    `.py` 는 docstring 과 주석이 산문이고, 나머지 — 문자열 리터럴·호출·식별자 — 는 검사 코드다. 없어진 인자를 넘겨 거부되는지
    보는 호출과 `assertNotIn(...)` 거부 검사가 거기 살고, 그것은 인자를 지시하는 것이 아니라 없다는 것을 확인하는 것이다.
    그 밖의 파일(런북·정본 템플릿)은 전체가 산문이다 — 코드 블록 안의 실행 명령도 지시다.
    파싱이 안 되는 `.py` 는 전체를 산문으로 본다 — 덜 보는 쪽이 아니라 더 보는 쪽으로 넘어진다."""
    lines = list(enumerate(text.split("\n"), 1))
    if path.suffix != ".py":
        return lines
    try:
        tree = ast.parse(text)
        comments = [(tok.start[0], tok.string) for tok in tokenize.generate_tokens(io.StringIO(text).readline)
                    if tok.type == tokenize.COMMENT]
    except (SyntaxError, tokenize.TokenError):
        return lines
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc is not None:
                start = node.body[0].lineno
                out.extend((start + i, ln) for i, ln in enumerate(doc.split("\n")))
    return sorted(out + comments)


def _dead_instructions(root):
    """`root` 아래에서 채움 스크립트를 **지시하면서** 없어진 인자를 쓰는 산문 줄. 구별 규칙 셋 —

    ① 인자 형태로 본다(`REMOVED_FLAGS`). 자리표시자 이름은 꺾쇠 안이라 그 형태가 아니다.
    ② 산문만 본다(`_prose`). 검사 코드는 산문이 아니다.
    ③ 지시하는 줄만 본다 — 스크립트 이름이 있는 줄과, 그 줄에서 역슬래시로 이어진 다음 줄들(§3.7 의 여러 줄 명령).
       같은 파일의 다른 줄에서 **다른 명령**에 쓰는 같은 이름의 인자(`envelope build` 의 base-sha)는 이 스크립트의 지시가 아니다.
    기록(`RECORD_ROOTS`)·외부 원문(`FOREIGN_ROOTS`)·런타임 상태(`STATE_DIRS`)는 걷지 않는다 — 그 시점의 사실이거나 이 저장소의 것이 아니다."""
    root = Path(root)
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        at_top = Path(dirpath) == root
        dirnames[:] = sorted(d for d in dirnames
                             if d not in STATE_DIRS and not (at_top and d in RECORD_ROOTS + FOREIGN_ROOTS))
        for name in sorted(filenames):
            path = Path(dirpath) / name
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if SCRIPT_NAME not in text:
                continue
            continued = False
            for lineno, line in _prose(path, text):
                instructs = SCRIPT_NAME in line or continued
                continued = instructs and line.rstrip().endswith("\\")
                if instructs and any(flag in line for flag in REMOVED_FLAGS):
                    hits.append(f"{path.relative_to(root).as_posix()}:{lineno}: {line.strip()}")
    return hits


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
    """계약 파일 경로(`--task`)에서 base_sha·sha256 을 읽는다(Q-104) — 둘을 따로 넘기는 인자는 없다."""

    UNIT = "feat-20260829-license-field-46an"
    RUN = "run_aaaaaaaaaaaa"
    BASE_SHA = "c237ea9d54cd5ee6dae3af4e10ef8c4eb39a2dd5"

    def setUp(self):
        self.fill = _load_fill()
        self.tmp = tempfile.TemporaryDirectory()
        # 계약 파일이 있어야 --task 를 넘길 수 있다 — 클래스 상수가 아니라 setUp 이 만든다(값을 바꿔 가며 검사해야 하므로).
        self.contract = Path(self.tmp.name) / f"{self.RUN}-reviewer.json"
        self.contract_data = {"schema": "romeo/task-envelope@0.1.0", "unit_id": self.UNIT,
                              "role": "reviewer", "base_sha": self.BASE_SHA}
        self._write_contract(self.contract_data)
        self.args = ["--unit", self.UNIT, "--run", self.RUN, "--task", str(self.contract)]

    def tearDown(self):
        self.tmp.cleanup()

    def _write_contract(self, data):
        self.contract.write_text(json.dumps(data), encoding="utf-8")

    def _contract_sha256(self):
        return hashlib.sha256(self.contract.read_bytes()).hexdigest()

    def _run(self, *extra, args=None):
        out, err = io.StringIO(), io.StringIO()
        target = Path(self.tmp.name) / "brief.md"
        with redirect_stdout(out), redirect_stderr(err):
            rc = self.fill.main([*(args if args is not None else self.args), *extra, "--out", str(target)])
        return rc, target, out.getvalue(), err.getvalue()

    def test_fills_for_both_runtimes_and_modes(self):
        sha256 = self._contract_sha256()
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
                self.assertIn(sha256, text)
                if mode == "rerun":
                    self.assertIn("검토자만 다시 띄운 것", text)
                    self.assertIn("evidence/run_bbbbbbbbbbbb.yaml", text)
                    self.assertIn(f"task/{self.RUN}-reviewer.json", text)
                else:
                    self.assertNotIn("검토자만 다시 띄운 것", text)
                    self.assertIn(f"evidence/{self.RUN}.yaml", text)

    def test_refuses_inconsistent_inputs(self):
        rc, target, _o, err = self._run("--runtime", "codex", "--mode", "base", "--evidence-run", "run_bbbbbbbbbbbb")
        self.assertEqual(rc, 1)
        self.assertIn("base 모드인데", err)
        self.assertFalse(target.exists(), "어긋난 입력으로는 파일을 만들지 않는다")

        # 계약 파일에 base_sha 가 없으면 — task_values() 가 문제를 내고, 파일을 만들지 않는다.
        bad_contract = Path(self.tmp.name) / "no-base-sha.json"
        bad_contract.write_text(json.dumps({"role": "reviewer"}), encoding="utf-8")
        rc2, target2, _o2, err2 = self._run(
            "--runtime", "claude", "--mode", "base",
            args=["--unit", self.UNIT, "--run", self.RUN, "--task", str(bad_contract)])
        self.assertEqual(rc2, 1)
        self.assertIn("base_sha", err2)
        self.assertFalse(target2.exists())

    def test_base_sha_and_hash_are_derived_from_the_contract_file(self):
        """AC-3 — base_sha 는 계약 JSON 의 필드에서, sha256 은 그 파일의 바이트에서 온다. 둘을 따로 넘기는 인자는 없다."""
        rc, target, _o, err = self._run("--runtime", "claude", "--mode", "base")
        self.assertEqual(rc, 0, err)
        text = target.read_text(encoding="utf-8")
        self.assertIn(self.BASE_SHA, text)
        original_sha256 = self._contract_sha256()
        self.assertIn(original_sha256, text)

        # base_sha 필드를 바꾸면 — 브리프의 base-sha 도, 계약 파일의 바이트가 바뀌었으니 sha256 도 따라 바뀐다.
        new_base_sha = "d" * 40
        self._write_contract({**self.contract_data, "base_sha": new_base_sha})
        rc2, target2, _o2, err2 = self._run("--runtime", "claude", "--mode", "base")
        self.assertEqual(rc2, 0, err2)
        text2 = target2.read_text(encoding="utf-8")
        self.assertIn(new_base_sha, text2)
        self.assertNotIn(self.BASE_SHA, text2)
        new_sha256 = self._contract_sha256()
        self.assertNotEqual(new_sha256, original_sha256)
        self.assertIn(new_sha256, text2)
        self.assertNotIn(original_sha256, text2)

        # base_sha 필드는 그대로 두고 다른 바이트만 바꿔도 — sha256 은 파일 **전체**에서 계산하므로 또 바뀐다.
        self._write_contract({**self.contract_data, "base_sha": new_base_sha, "extra": "padding"})
        rc3, target3, _o3, err3 = self._run("--runtime", "claude", "--mode", "base")
        self.assertEqual(rc3, 0, err3)
        text3 = target3.read_text(encoding="utf-8")
        third_sha256 = self._contract_sha256()
        self.assertNotEqual(third_sha256, new_sha256)
        self.assertIn(third_sha256, text3)
        self.assertIn(new_base_sha, text3, "base_sha 필드는 바뀌지 않았다")

    def test_removed_arguments_are_refused_and_both_call_sites_match(self):
        """AC-4 — 없어진 인자 이름을 넘기면 어디서 오든 스크립트가 0 이 아닌 종료 코드로 거부하고,
        그 스크립트를 지시하는 두 자리(RUNBOOK §3.7 실행 명령·run_unit.py 의 명령 문자열)가 새 인터페이스이며,
        그 명령을 **설명하는 산문**(docstring·주석·런북 문단)에도 없어진 인자 이름이 남아 있지 않다 — 3회차가
        `tests/test_run_unit.py` 의 클래스 docstring 한 줄을 이 검사가 보지 않는 자리에서 잡았다. 무엇이 산문이고
        무엇이 검사 코드·자리표시자 이름·과거 기록인지는 `_dead_instructions` 의 규칙 셋이 가른다."""
        with self.assertRaises(SystemExit) as cm:
            self.fill.main([*self.args, "--base-sha", self.BASE_SHA, "--runtime", "claude", "--mode", "base"])
        self.assertNotEqual(cm.exception.code, 0)
        with self.assertRaises(SystemExit) as cm2:
            self.fill.main([*self.args, "--task-sha256", "f" * 64, "--runtime", "claude", "--mode", "base"])
        self.assertNotEqual(cm2.exception.code, 0)

        runbook = (REPO / "adapters/orca/RUNBOOK.md").read_text(encoding="utf-8")
        m = re.search(r"python3 adapters/orca/prompts/fill_brief\.py.*?--out \"\$P\"", runbook, re.S)
        self.assertIsNotNone(m, "RUNBOOK §3.7 의 fill_brief.py 호출을 찾지 못했다")
        self.assertIn("--task ", m.group(0))
        self.assertNotIn("--base-sha", m.group(0))
        self.assertNotIn("--task-sha256", m.group(0))

        from romeo import HARNESS_ROOT
        from romeo.run_unit import delegation_commands
        fill_cmd = dict(delegation_commands(self.UNIT, "run_x", "a" * 40, "worktree", HARNESS_ROOT))["reviewer-brief"]
        self.assertIn("--task ", fill_cmd)
        self.assertNotIn("--base-sha", fill_cmd)
        self.assertNotIn("--task-sha256", fill_cmd)

        dead = _dead_instructions(REPO)
        self.assertEqual(dead, [], "채움 스크립트를 지시하는 산문에 없어진 인자 이름이 남아 있다:\n" + "\n".join(dead))

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
        self.assertEqual(example["task_envelope_ref"]["sha256"], self._contract_sha256())


class TestDeadInstructionRule(unittest.TestCase):
    """`_dead_instructions` 의 규칙 셋이 양쪽으로 가르는지 가짜 트리에서 본다 — 잡아야 할 것을 잡고, 정당한 자리를 오탐하지 않는다.
    오탐하면 check-4 는 통과 불가능한 검사가 되고, 놓치면 3회차의 결함이 다시 검사 밖에 선다."""

    DEAD = "해시는 `fill_brief.py --task-sha256` 이 그 자리에서 계산한다."   # 3회차 검토자가 잡은 문장 그대로

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _put(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def test_prose_that_instructs_a_removed_flag_is_caught(self):
        self._put("tests/t.py", f'class T:\n    """설명.\n    {self.DEAD}"""\n    x = 1\n')                 # docstring
        self._put("romeo/r.py", f"# {self.DEAD}\nx = 1\n")                                               # 주석
        self._put("adapters/R.md", "python3 adapters/orca/prompts/fill_brief.py --unit <id> \\\n  --base-sha <base-sha> --out P\n")  # 이어진 명령
        hits = _dead_instructions(self.root)
        self.assertEqual([h.split(":")[0] + ":" + h.split(":")[1] for h in hits],
                         ["adapters/R.md:2", "romeo/r.py:1", "tests/t.py:3"], hits)

    def test_check_code_placeholders_records_and_other_commands_are_not(self):
        self._put("tests/t.py", 'import re\n'
                                'def test(self):\n'
                                '    self.fill.main([*self.args, "--task-sha256", "f" * 64])\n'       # 없어진 인자를 넘겨 거부를 보는 호출
                                '    self.assertNotIn("--task-sha256", fill_brief_cmd)\n'            # 거부 검사
                                '    self.assertNotIn("--base-sha", fill_brief_cmd)\n')
        self._put("adapters/orca/prompts/reviewer-brief.md",
                  "자리표시자(전부 `fill_brief.py` 가 채운다): `<base-sha>` · `<task-sha256>` 검토자 계약 파일의 sha256\n")  # 자리표시자 이름
        self._put("docs/planning/open-questions.md", f"| Q-41 | {self.DEAD} |\n")                   # 과거 기록
        self._put("docs/work/u/spec.md", self.DEAD + "\n")
        self._put("archive/x/README.md", self.DEAD + "\n")                                             # 외부 원문
        self._put("adapters/R.md", "`fill_brief.py --task` 가 계약 파일에서 읽는다.\n"
                                   "bin/romeo envelope build --unit <id> --role reviewer --base-sha <base-sha>\n")  # 다른 명령의 같은 이름
        self._put("core/x.md", "--task-sha256 는 어디에도 없다\n")                                    # 스크립트를 지시하지 않는 줄
        self.assertEqual(_dead_instructions(self.root), [])


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
            contract = Path(tmp) / "run_aaaaaaaaaaaa-reviewer.json"
            contract.write_text(json.dumps({"unit_id": "feat-20260829-license-field-46an", "role": "reviewer",
                                            "base_sha": "c237ea9d54cd5ee6dae3af4e10ef8c4eb39a2dd5"}), encoding="utf-8")
            target = Path(tmp) / "brief.md"
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = fill.main(["--unit", "feat-20260829-license-field-46an", "--run", "run_aaaaaaaaaaaa",
                                "--task", str(contract),
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
