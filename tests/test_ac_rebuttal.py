"""승인 전 반대 독자: 확인란 AC 의 전칭 표현 경고(AC_UNIVERSAL)와 반박 누락 경고(AC_UNREBUTTED).

둘 다 **경고까지만**이다 — 종료 코드를 바꾸지 않고 승인을 막지 않는다(K-31). 이 파일이 보는 것은
「경고가 나는가」가 아니라 「요구하는 자리(정책표·절차)와 보는 자리(검사)가 한 문자열인가」다(§11)."""
import io
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import yaml

from romeo import HARNESS_ROOT, frontmatter
from romeo.cli import main
from romeo.docs import approve_unit, create_unit, rebuttal_warnings
from romeo.policy import load_policy, route
from romeo.validate import ac_items, validate_doc

SCOPE_PATHS = "- 바뀌는 파일·모듈: `docs/work/` · `scripts/` · `README.md`"
SCOPE_TODO = "- 바뀌는 파일·모듈: 채움"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


def make_t0_unit(root, ac_lines):
    """임시 저장소에 T0 단위 하나. 확인란의 수용 기준을 넘겨받은 줄로 갈아 끼운다.

    `approve` 를 실제로 돌리려면 승인 가능한 단위가 필요하다 — 반박 누락 경고 검사와
    AC-5 의 「명령마다 각각」 검사가 같은 형태를 쓴다. 반환: (unit_id, spec 경로)."""
    git("init", "-q", cwd=root)
    git("config", "user.email", "t@example.com", cwd=root)
    git("config", "user.name", "t", cwd=root)
    (root / "README.md").write_text("hello\n", encoding="utf-8")
    git("add", ".", cwd=root)
    git("commit", "-q", "-m", "init", cwd=root)
    out = route({"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                 "gates": [], "blast_radius": "small", "uncertainty": "low"})
    res = create_unit(out, "테스트 T0", "test-t0", "테스트용 변경", project_root=root, date="20260827")
    spec = Path(res["files"][0])
    fm, body = frontmatter.read(spec)
    body = body.replace("NEEDS_INPUT", "채움").replace(SCOPE_TODO, SCOPE_PATHS)
    head, rest = body.split("## 확인란")[0], "## 변경 범위" + body.split("## 변경 범위", 1)[1]
    body = head + "## 확인란\n\n- **수용 기준:**\n" + "\n".join(ac_lines) + "\n\n" + rest
    frontmatter.write(spec, fm, body)
    return res["id"], spec


class TestUniversalLint(unittest.TestCase):
    """전칭 표현 경고. 패턴은 정책표가 소유한다 — 검사가 그것을 실측한다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _spec(self, ac_lines, harness=None):
        """확인란만 있는 최소 문서. validate_doc 는 frontmatter 스키마를 보므로 실물 spec 을 베껴 쓴다."""
        src = HARNESS_ROOT / "docs/work/feat-20260908-ac-rebuttal-before-approval-2sct/spec.md"
        fm, body = frontmatter.read(src)
        head = body.split("## 확인란")[0]
        rest = "## 변경 범위" + body.split("## 변경 범위", 1)[1]
        body = head + "## 확인란\n\n- **수용 기준:**\n" + "\n".join(ac_lines) + "\n\n" + rest
        p = self.root / "spec.md"
        frontmatter.write(p, fm, body)
        return p

    def test_universal_sentences_warn_each_matched_pattern(self):
        p = self._spec([
            "  - [ ] AC-1 어떤 입력이든 목록은 나온다.",
            "  - [ ] AC-2 파일 하나라도 깨지면 그 줄만 표시한다.",
            "  - [ ] AC-3 모든 호출자가 항상 같은 값을 본다.",
        ])
        r = validate_doc(p)
        warns = [w for w in r["warnings"] if w.startswith("AC_UNIVERSAL")]
        self.assertTrue(any(w.startswith("AC_UNIVERSAL AC-1") for w in warns), warns)
        self.assertTrue(any(w.startswith("AC_UNIVERSAL AC-2") for w in warns), warns)
        # AC-3 은 「모든」·「항상」 두 패턴에 맞는다 — 맞은 패턴마다 한 줄이다.
        ac3 = [w for w in warns if w.startswith("AC_UNIVERSAL AC-3")]
        self.assertEqual(len(ac3), 2, ac3)
        self.assertEqual(r["errors"], [], r)

    def test_closed_set_sentences_do_not_warn(self):
        p = self._spec([
            "  - [ ] AC-1 `a.py`·`b.py`·`c.py` 세 파일이 같은 접두를 담는다.",
            "  - [ ] AC-2 AC-1~7 의 id 가 출력에 그대로 인쇄된다.",
        ])
        r = validate_doc(p)
        self.assertEqual([w for w in r["warnings"] if w.startswith("AC_UNIVERSAL")], [])

    def test_pattern_comes_from_policy_not_code(self):
        """정책표에서 패턴 하나를 지우면 **그 경고만** 사라지고 나머지는 남는다.

        패턴을 코드에 하드코딩한 구현은 정책표를 고쳐도 경고가 그대로다 — 그 반례를 이 검사가 가른다."""
        p = self._spec(["  - [ ] AC-1 모든 호출자가 항상 같은 값을 본다."])
        before = {w for w in validate_doc(p)["warnings"] if w.startswith("AC_UNIVERSAL")}
        self.assertEqual(len(before), 2, before)

        copy = self.root / "harness"
        shutil.copytree(HARNESS_ROOT / "core", copy / "core")
        pol = copy / "core/policy/packages.yaml"
        d = yaml.safe_load(pol.read_text(encoding="utf-8"))
        d["ac_lint"]["universal_patterns"] = [x for x in d["ac_lint"]["universal_patterns"] if x != "항상"]
        pol.write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False), encoding="utf-8")

        after = {w for w in validate_doc(p, harness_root=copy)["warnings"] if w.startswith("AC_UNIVERSAL")}
        self.assertEqual(before - after, {"AC_UNIVERSAL AC-1 «항상»"}, (before, after))
        self.assertIn("AC_UNIVERSAL AC-1 «모든»", after)

    def test_exit_code_is_zero_with_warnings(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["validate", str(HARNESS_ROOT / "docs/work/feat-20260907-context-one-hop-resume-w5jq")])
        self.assertEqual(rc, 0)
        self.assertIn("AC_UNIVERSAL AC-5", buf.getvalue())


class TestApproveWarnsUnrebutted(unittest.TestCase):
    """반박 누락 경고. 세 경우(없음·일부·전부) 모두 **승인은 기록된다**."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        self.unit, self.spec = make_t0_unit(
            self.root, [f"  - [x] AC-{i} 무언가가 참이다." for i in (1, 2, 3)])

    def tearDown(self):
        self.tmp.cleanup()

    def _warns(self):
        fm, body = frontmatter.read(self.spec)
        return rebuttal_warnings(self.spec.parent, fm, body, load_policy())

    def _write_rebuttal(self, ids, name="inputs/ac-rebuttal-20260908.md"):
        p = self.spec.parent / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(f"### AC-{i}\n- 반례: 없음\n" for i in ids), encoding="utf-8")
        fm, body = frontmatter.read(self.spec)
        fm["inputs"] = [name]
        frontmatter.write(self.spec, fm, body)

    def test_no_file_lists_every_ac_and_approval_is_recorded(self):
        self.assertEqual(self._warns(), ["AC_UNREBUTTED AC-1, AC-2, AC-3"])
        fm = approve_unit(self.unit, "tester", project_root=self.root)
        self.assertEqual(fm["status"], "active")
        self.assertIsNotNone(fm["approved_at"])

    def test_partial_file_lists_only_missing(self):
        self._write_rebuttal([1, 2])
        self.assertEqual(self._warns(), ["AC_UNREBUTTED AC-3"])
        fm = approve_unit(self.unit, "tester", project_root=self.root)
        self.assertEqual(fm["status"], "active")

    def test_full_file_warns_nothing(self):
        self._write_rebuttal([1, 2, 3])
        self.assertEqual(self._warns(), [])
        fm = approve_unit(self.unit, "tester", project_root=self.root)
        self.assertEqual(fm["status"], "active")

    def test_only_the_first_matching_input_is_read(self):
        """접두에 맞는 **첫 항목**만 본다 — 그 파일이 없으면 뒤 항목이 있어도 전체가 경고된다(AC-2)."""
        self._write_rebuttal([1, 2, 3], name="inputs/ac-rebuttal-later.md")
        fm, body = frontmatter.read(self.spec)
        fm["inputs"] = ["inputs/ac-rebuttal-first.md", "inputs/ac-rebuttal-later.md"]
        frontmatter.write(self.spec, fm, body)
        self.assertEqual(self._warns(), ["AC_UNREBUTTED AC-1, AC-2, AC-3"])

    def test_cli_prints_warning_and_exits_zero(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["approve", self.unit, "--by", "tester", "--root", str(self.root)])
        self.assertEqual(rc, 0)
        self.assertIn("WARN AC_UNREBUTTED AC-1, AC-2, AC-3", buf.getvalue())


class TestProcedureAndAdapters(unittest.TestCase):
    """요구하는 자리와 보는 자리가 한 문자열인가(§11)."""

    def setUp(self):
        self.pol = load_policy()["packages"]
        self.skill = (HARNESS_ROOT / "core/workflows/plan/SKILL.md").read_text(encoding="utf-8")

    def _step_body(self, title):
        """절차 목록에서 그 단계 하나의 본문만. 다음 번호 항목이나 절 끝에서 끊는다."""
        lines = self.skill.split("\n")
        out, on = [], False
        for ln in lines:
            m = re.match(r"^(\d+)\. \*\*(.+?)\.\*\*", ln)
            if m:
                if on:
                    break
                on = m.group(2) == title
            elif ln.startswith("## ") and on:
                break
            if on:
                out.append(ln)
        return "\n".join(out)

    def test_rebuttal_step_prefix_equals_policy_prefix(self):
        body = self._step_body("반박 읽기")
        self.assertTrue(body, "절차에 「반박 읽기」 단계가 없다")
        found = re.findall(r"`docs/work/<id>/(inputs/ac-rebuttal-)", body)
        self.assertTrue(found, body)
        self.assertEqual(found[0], self.pol["ac_lint"]["rebuttal_prefix"])

    def test_rebuttal_step_comes_before_approval_request(self):
        i = self.skill.index("**반박 읽기.**")
        j = self.skill.index("**승인 요청.**")
        self.assertLess(i, j)

    def test_brief_has_one_placeholder_and_says_its_four_things(self):
        t = (HARNESS_ROOT / "adapters/orca/prompts/ac-rebuttal-brief.md").read_text(encoding="utf-8")
        self.assertEqual(sorted(set(re.findall(r"<[a-z_]+>", t))), ["<id>"])
        for phrase in ("반례", "검토 시점", "표현", "아무것도 쓰지 않고", "판정을 내지 않는다", "대신 써 주지 않는다"):
            self.assertIn(phrase, t)

    def test_adapters_and_compiled_carry_the_line(self):
        b = yaml.safe_load((HARNESS_ROOT / ".harness/bindings.yaml").read_text(encoding="utf-8"))
        enforce = b["roles"]["default"]["reviewer"]["enforcement"] if "default" in b.get("roles", {}) else None
        for rel in ("adapters/claude/workflows/plan.md", "adapters/codex/workflows/plan.md",
                    ".claude/skills/plan/SKILL.md", ".agents/skills/plan/SKILL.md"):
            t = (HARNESS_ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("ac-rebuttal", t, rel)
        claude_map = (HARNESS_ROOT / "adapters/claude/workflows/plan.md").read_text(encoding="utf-8")
        if enforce:
            self.assertIn(enforce, claude_map)

    def test_warning_codes_come_from_catalog_each_matching_its_command(self):
        """카탈로그의 두 코드를 **명령마다 각각** 대조한다 — 합집합은 통과해서는 안 된다(AC-5).

        두 코드가 **둘 다 날 만한** 단위 하나에서 두 명령을 돌린다 — 확인란에 전칭 표현이 있고 반박 파일은 없다.
        그래서 `approve` 가 두 코드를 모두 인쇄하는 구현(또는 `validate` 가 그러는 구현)이 여기서 걸린다.
        한쪽 출력만 보거나 두 출력을 합쳐서 보면 그 반례가 통과한다.
        코드 문자열은 카탈로그에서 **읽는다** — 카탈로그에서 지우면 이 검사가 실패한다."""
        cat = self.pol["warnings"]
        ac_codes = [c for c in cat if c.startswith("AC_")]
        self.assertEqual(len(ac_codes), 2, ac_codes)
        universal = next(c for c in ac_codes if "전칭" in cat[c])
        unrebutted = next(c for c in ac_codes if "반박" in cat[c])
        self.assertNotEqual(universal, unrebutted, ac_codes)

        with tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP")) as tmp:
            root = Path(tmp)
            unit, spec = make_t0_unit(root, ["  - [x] AC-1 모든 호출자가 항상 같은 값을 본다."])
            v, a = io.StringIO(), io.StringIO()
            with redirect_stdout(v):
                main(["validate", str(spec.parent)])
            with redirect_stdout(a):
                main(["approve", unit, "--by", "tester", "--root", str(root)])
        vout, aout = v.getvalue(), a.getvalue()
        self.assertIn(universal, vout, vout)         # validate 는 자기 코드만 낸다
        self.assertNotIn(unrebutted, vout, vout)
        self.assertIn(unrebutted, aout, aout)        # approve 도 자기 코드만 낸다
        self.assertNotIn(universal, aout, aout)

    def test_new_step_body_has_no_vendor_name(self):
        """이 단위가 코어에 **새로 넣은 문장**에만 도구명이 없어야 한다(C-C6).

        기존 C-C6 검사(`tests/test_roles_envelopes.py` 의 `TestVendorNeutral`)는 `core/roles/*.yaml` 과
        결과 계약 스키마만 보고 절차 파일은 대상이 아니다. 그리고 이 절차 파일에는 원래부터 「실행기(…)에
        중립이다」라는 문장이 있어 파일 전체를 보면 기존 상태에서도 실패한다 — 그래서 **새 단계 본문만** 본다."""
        body = self._step_body("반박 읽기")
        for name in ("codex", "claude", "orca", "anthropic", "openai"):
            self.assertNotIn(name, body.lower(), f"「반박 읽기」 단계 본문에 도구명 {name}")


if __name__ == "__main__":
    unittest.main()
