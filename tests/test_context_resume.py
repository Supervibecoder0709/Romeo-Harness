"""M4 두 번째 마일스톤 — 「1-hop 재개」 요구가 실제로 집행되는가(§11).

`/plan` 절차 1단계는 겹치는 단위가 있으면 「재개」를 제안하라고 **요구**하지만, 재개하는 세션이 무엇을
읽어야 하는지는 어디에도 없었다 — 요구만 있고 집행이 없는 모양이다. 이 검사가 셋을 같은 자리에서 본다.

| # | 어느 사건에서 보는가 | 어느 문서를 읽는가 | 무엇이 참이어야 충족인가 |
| --- | --- | --- | --- |
| AC-1 | `romeo context` 실행 | 단위 폴더의 파일 전부 | 폴더 안 파일 누락 0 · 역할은 정해진 어휘 · 정본(spec)이 먼저 |
| AC-2 | 같은 실행 | frontmatter 의 `parent`·`inputs` | 부모의 charter 와 입력의 각 경로는 있고, 그 너머(입력 단위의 다른 파일·부모의 증거)는 없다 |
| AC-3 | 없는 id 로 실행 | — | exit 1 · 한 줄 오류 · 스택 트레이스 없음 |
| AC-4 | git 이력 없는 루트에서 실행 | 없는 파일을 가리키는 frontmatter | `[없음]` 으로 인쇄하고 exit 0 — 숨기지도 막지도 않는다 |
| AC-5 | 같은 실행 | attempts·review·evidence 파일 | 회차 결과·판정·findings 수·등록 여부가 파일에 적힌 값 그대로다. 추천 문장은 없다 |
| AC-6 | 저장소의 모든 단위 | 31개 단위 폴더 | 전부 exit 0 이고 깨진 참조 0 |
| AC-7 | 절차 문서 로드 | `core/workflows/plan/SKILL.md` 의 **1단계 본문만** | 거기 적힌 이름으로 **실제로 실행해** 단위의 spec 경로가 목록에 나온다 |

**반례는 빈 값이 아니라 그럴듯한 거짓 값이다.** 여기서 그것은 「단위 폴더를 `ls` 한 목록」이다 — 형태는 파일
목록이지만 상위 문서와 입력이 없고(재개하는 세션이 charter 를 못 찾는다), 어느 증거가 검사 기록인지·어느
회차가 어떻게 끝났는지 말하지 않는다. AC-2·AC-5 가 겨누는 것이 그 상태다. AC-7 이 「이름이 CLI 에 있는가」로
만족되지 않는 이유는 M1 과 같다 — 1단계 본문에는 `romeo find` 도 있고, 그것은 폴더 경로까지만 낸다.

**전부 판별 검사다** — 명령이 없던 상태에서는 모듈 import 부터 실패한다.
"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from romeo.context import ROLES, UNIT_DOC_NOTES, unit_context

ROOT = Path(__file__).resolve().parents[1]

#: 회차 2·검토 봉투 2·계약 4·증거 2·등록된 입력 1 을 가진 닫힌 단위 — 목록이 무엇을 담아야 하는지의 기준점.
CLOSED_UNIT = "feat-20260907-judge-revision-base-sha-pwt8"
#: parent 와 inputs 를 둘 다 가진 단위 — 1-hop 의 경계를 가른다.
LINKED_UNIT = "feat-20260906-m3-close-foreign-repo-ik3u"
LINKED_PARENT = "init-20260904-attach-payload-manual-rreq"
LINKED_INPUT_UNIT = "feat-20260904-m2-router-foreign-repo-ct5h"
NO_SUCH_UNIT = "feat-20260101-no-such-unit-zzzz"
ORPHAN = "chg-20260101-orphan-abcd"
ORPHAN_PARENT = "init-20260101-gone-zzzz"
#: 정본 frontmatter 가 깨진 합성 단위 — 「읽을 수 없다」가 붙는 자리를 가른다.
BROKEN_UNIT = "chg-20260101-broken-abcd"


def _romeo(*argv, cwd=ROOT):
    return subprocess.run([sys.executable, str(ROOT / "bin" / "romeo"), *argv],
                          capture_output=True, text=True, cwd=str(cwd))


def _paths(res):
    return [f["path"] for f in res["files"]]


class TestContextCommand(unittest.TestCase):

    def test_lists_every_file_in_the_unit_folder_with_a_role(self):
        """AC-1 — 폴더 안 파일 누락 0, 역할은 정해진 어휘, 정본이 먼저."""
        res = unit_context(ROOT, CLOSED_UNIT)
        udir = ROOT / "docs" / "work" / CLOSED_UNIT
        on_disk = {p.relative_to(ROOT).as_posix() for p in udir.rglob("*") if p.is_file()}
        self.assertGreater(len(on_disk), 5, "기준 단위의 폴더가 비어 있으면 이 검사는 아무것도 확인하지 않는다")
        self.assertEqual(on_disk - set(_paths(res)), set(), "폴더 안 파일이 목록에서 빠졌다")
        self.assertTrue(all(f["role"] in ROLES for f in res["files"]), [f["role"] for f in res["files"]])
        self.assertEqual(res["files"][0]["path"], f"docs/work/{CLOSED_UNIT}/spec.md")
        self.assertEqual(res["files"][0]["role"], "정본")
        roles = {f["path"]: f["role"] for f in res["files"]}
        self.assertEqual(roles[f"docs/work/{CLOSED_UNIT}/attempts.yaml"], "회차")
        self.assertEqual(roles[f"docs/work/{CLOSED_UNIT}/inputs/probe-2026-09-07.patch"], "입력",
                         "frontmatter inputs 에 등록된 파일은 「기타」가 아니라 「입력」이다")
        self.assertEqual({roles[p] for p in roles if f"/{CLOSED_UNIT}/review/" in p}, {"검토"})
        # `docs/work/*/task/` 는 git 에 없다(.gitignore) — 새 체크아웃에는 없고 워커 트리에만 있으므로
        # 「계약」역할은 AC-4 의 합성 단위에서 본다. 여기서는 있으면 그 역할이어야 한다는 것만 본다.
        self.assertLessEqual({roles[p] for p in roles if f"/{CLOSED_UNIT}/task/" in p}, {"계약"})
        self.assertEqual(res["missing"], [])
        text = _romeo("context", CLOSED_UNIT)
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertEqual(text.stdout.splitlines()[2].split(" ")[1], f"docs/work/{CLOSED_UNIT}/spec.md",
                         "인쇄 첫 파일 줄은 spec 이어야 한다")

    def test_follows_parent_and_inputs_exactly_one_hop(self):
        """AC-2 — 부모의 charter 와 입력의 각 경로는 있고, 그 너머는 없다."""
        res = unit_context(ROOT, LINKED_UNIT)
        paths = _paths(res)
        roles = {f["path"]: f["role"] for f in res["files"]}
        parent_charter = f"docs/work/{LINKED_PARENT}/charter.md"
        input_spec = f"docs/work/{LINKED_INPUT_UNIT}/spec.md"
        self.assertIn(parent_charter, paths)
        self.assertIn(input_spec, paths)
        self.assertEqual(roles[parent_charter], "상위")
        self.assertEqual(roles[input_spec], "입력")
        beyond = [p for p in paths
                  if (p.startswith(f"docs/work/{LINKED_INPUT_UNIT}/") and p != input_spec)
                  or (p.startswith(f"docs/work/{LINKED_PARENT}/") and p != parent_charter)]
        self.assertEqual(beyond, [], "1-hop 을 넘었다 — 입력 단위의 다른 파일이나 부모의 증거가 목록에 있다")
        # 그 너머가 실제로 존재해야 위 단언이 무엇인가를 가른다.
        self.assertTrue((ROOT / "docs/work" / LINKED_INPUT_UNIT / "evidence").is_dir())
        self.assertTrue((ROOT / "docs/work" / LINKED_PARENT / "evidence").is_dir())
        self.assertEqual(res["missing"], [])

    def test_unknown_unit_is_refused_with_exit_1_and_no_traceback(self):
        """AC-3 — 없는 id 는 한 줄 오류와 exit 1 이다."""
        r = _romeo("context", NO_SUCH_UNIT)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("ERROR", r.stderr)
        self.assertIn(NO_SUCH_UNIT, r.stderr)
        self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_missing_reference_is_printed_not_hidden(self):
        """AC-4 — git 이력 없는 루트에서, parent·inputs 가 가리키는 파일이 없으면 [없음] 으로 인쇄하고 exit 0."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            udir = root / "docs" / "work" / ORPHAN
            udir.mkdir(parents=True)
            (udir / "spec.md").write_text(
                f"---\nid: {ORPHAN}\ntype: spec\ntitle: 고아 단위\nstatus: active\n"
                f"parent: {ORPHAN_PARENT}\ninputs: [../{ORPHAN_PARENT}/charter.md, notes/missing.md]\n"
                f"evidence: [evidence/run_reg.yaml]\n---\n# 고아\n",
                encoding="utf-8")
            # 워커 트리에만 있는 것들 — 계약(git 에 없다)·등록되지 않은 증거·결과 계약.
            (udir / "task").mkdir()
            (udir / "task" / "run_reg-implementer.json").write_text(
                json.dumps({"role": "implementer", "base_sha": "0123456789abcdef0123456789abcdef01234567"}), encoding="utf-8")
            (udir / "evidence").mkdir()
            (udir / "evidence" / "run_reg.yaml").write_text("head_sha: abcdef0123456789\ncommands: [{id: c1}, {id: c2}]\n", encoding="utf-8")
            (udir / "evidence" / "run_stray.yaml").write_text("head_sha: abcdef0123456789\ncommands: []\n", encoding="utf-8")
            (udir / "result").mkdir()
            (udir / "result" / "run_reg-implementer.json").write_text(
                json.dumps({"role": "implementer", "gate_verdict": "FAIL", "blocked_reason": None}), encoding="utf-8")
            self.assertFalse((root / ".git").exists(), "이 검사는 git 이력이 없는 루트를 겨눈다")
            r = _romeo("context", ORPHAN, "--root", str(root), "--json", cwd=root)
            self.assertEqual(r.returncode, 0, r.stderr)
            res = json.loads(r.stdout)
            self.assertEqual(set(res["missing"]),
                             {f"docs/work/{ORPHAN_PARENT}/charter.md", f"docs/work/{ORPHAN}/notes/missing.md"})
            self.assertTrue([f for f in res["files"] if f["path"].endswith("/spec.md") and f["exists"]])
            by = {f["path"].split(f"{ORPHAN}/", 1)[-1]: f for f in res["files"] if f["path"].startswith(f"docs/work/{ORPHAN}/")}
            self.assertEqual(by["task/run_reg-implementer.json"]["role"], "계약")
            self.assertIn("base 0123456789ab", by["task/run_reg-implementer.json"]["note"])
            self.assertIn("등록됨", by["evidence/run_reg.yaml"]["note"])
            self.assertIn("명령 2건", by["evidence/run_reg.yaml"]["note"])
            self.assertIn("미등록", by["evidence/run_stray.yaml"]["note"])
            self.assertEqual(by["result/run_reg-implementer.json"]["role"], "결과")
            self.assertIn("FAIL", by["result/run_reg-implementer.json"]["note"])
            text = _romeo("context", ORPHAN, "--root", str(root), cwd=root)
            self.assertEqual(text.returncode, 0, text.stderr)
            self.assertEqual(text.stdout.count("[없음]"), 2, text.stdout)
            self.assertIn("notes/missing.md", text.stdout)

    def test_facts_come_from_the_files_not_from_judgment(self):
        """AC-5 — 회차 결과·판정·findings 수·등록 여부는 파일에 적힌 값 그대로고, 추천 문장은 없다."""
        res = unit_context(ROOT, CLOSED_UNIT)
        notes = {f["path"]: f["note"] for f in res["files"]}
        base = f"docs/work/{CLOSED_UNIT}"
        self.assertIn("1 fail", notes[f"{base}/attempts.yaml"])
        self.assertIn("2 pass", notes[f"{base}/attempts.yaml"])
        self.assertIn("FAIL", notes[f"{base}/review/run_4db4be703188-reviewer.json"])
        self.assertIn("PASS", notes[f"{base}/review/run_ae9a7eac2c66-reviewer.json"])
        self.assertIn("findings 1", notes[f"{base}/review/run_ae9a7eac2c66-reviewer.json"])
        self.assertIn("등록됨", notes[f"{base}/evidence/run_ae9a7eac2c66.yaml"])
        self.assertIn("등록됨", notes[f"{base}/evidence/run_4db4be703188.yaml"])
        self.assertIn("head 3363f8d3005e", notes[f"{base}/evidence/run_ae9a7eac2c66.yaml"])
        self.assertEqual(res["unit"]["status"], "done")
        text = _romeo("context", CLOSED_UNIT).stdout
        self.assertIn("status done", text)
        for word in ("추천", "다음 행동"):
            self.assertNotIn(word, text)
        # 「파일 하나가 깨져도 목록은 나온다 — 그 줄만 「읽을 수 없다」가 붙는다」(AC-5).
        # 정본도 예외가 아니다: spec 이 깨지면 그 줄에 사실을 적고, 다음으로 읽힌 정본에서 parent·inputs 를 가져온다.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            udir = root / "docs" / "work" / BROKEN_UNIT
            udir.mkdir(parents=True)
            (udir / "spec.md").write_text("---\nid: [unclosed\n---\n# 깨진 정본\n", encoding="utf-8")
            (udir / "brief.md").write_text(
                f"---\nid: {BROKEN_UNIT}\ntype: brief\ntitle: 깨진 정본 단위\nstatus: active\n"
                f"parent: {ORPHAN_PARENT}\n---\n# 브리프\n", encoding="utf-8")
            r = _romeo("context", BROKEN_UNIT, "--root", str(root), "--json", cwd=root)
            self.assertEqual(r.returncode, 0, r.stderr)
            broken = json.loads(r.stdout)
            by = {f["path"]: f for f in broken["files"]}
            self.assertIn("읽을 수 없다", by[f"docs/work/{BROKEN_UNIT}/spec.md"]["note"],
                          "깨진 정본에 고정 설명이 붙으면 그 줄은 거짓을 말한다")
            self.assertEqual(by[f"docs/work/{ORPHAN_PARENT}/charter.md"]["role"], "상위",
                             "spec 이 깨져도 읽힌 정본(brief)의 parent 는 조용히 사라지지 않는다")
            # 정본이 전부 깨지면 parent·inputs 줄을 낼 수 없다 — 그 사실이 헤더에 보인다.
            (udir / "brief.md").write_text("---\nid: [also unclosed\n---\n# 깨짐\n", encoding="utf-8")
            t2 = _romeo("context", BROKEN_UNIT, "--root", str(root), cwd=root)
            self.assertEqual(t2.returncode, 0, t2.stderr)
            self.assertIn("정본 읽을 수 없음", t2.stdout.splitlines()[1], t2.stdout)

        # **깨짐의 종류를 열거하는 구현은 끝나지 않는다.** 1회차는 문법 오류만, 2회차는 매핑 아님만 막았다 —
        # 아래 넷은 전부 「YAML 로는 유효하지만 그 자리에 올 수 없는 값」이다. 파일 단위 격리·필드 정규화가
        # 서 있으면 exit 0 이고 그 줄만 사실을 말한다. 서 있지 않으면 AttributeError 로 목록 전체가 죽거나
        # 문자열이 글자 단위로 쪼개져 쓰레기 경로가 인쇄된다.
        spec_path = f"docs/work/{BROKEN_UNIT}/spec.md"

        def _one(fm_text):
            """합성 단위 하나를 세우고 텍스트·JSON 두 출력을 돌려준다. 둘 다 exit 0 이고 트레이스백이 없다."""
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                udir = root / "docs" / "work" / BROKEN_UNIT
                udir.mkdir(parents=True)
                (udir / "spec.md").write_text(fm_text, encoding="utf-8")
                out = []
                for argv in ((), ("--json",)):
                    r = _romeo("context", BROKEN_UNIT, "--root", str(root), *argv, cwd=root)
                    self.assertEqual(r.returncode, 0, r.stderr)
                    self.assertNotIn("Traceback", r.stdout + r.stderr)
                    out.append(r.stdout)
                return out[0], json.loads(out[1])

        def _spec_note(res):
            return next(f["note"] for f in res["files"] if f["path"] == spec_path)

        def _roles(res, role):
            return [f["path"] for f in res["files"] if f["role"] == role]

        # (a) 목록 frontmatter · (b) 문자열 frontmatter — 매핑이 아니면 정본으로 채택하지 않는다.
        for fm_text in ("---\n- a\n---\n# 목록 frontmatter\n", "---\nhello\n---\n# 문자열 frontmatter\n"):
            _, res = _one(fm_text)
            self.assertIn("읽을 수 없다", _spec_note(res),
                          "매핑이 아닌 frontmatter 를 정본으로 채택하면 fm.get 에서 목록 전체가 죽는다")

        # (c) inputs 가 문자열 — 글자 단위로 쪼개지지 않고, 그 필드는 빈 목록이 된다.
        text, res = _one(f"---\nid: {BROKEN_UNIT}\ntype: spec\ntitle: t\nstatus: active\ninputs: notes.md\n---\n# c\n")
        self.assertEqual(_roles(res, "입력"), [], text)
        self.assertIn("inputs 값이 목록이 아니다", _spec_note(res), text)

        # (d) parent 가 목록 — 상위 줄을 내지 않고, `['x'` 같은 쓰레기 경로를 만들지 않는다.
        text, res = _one(f"---\nid: {BROKEN_UNIT}\ntype: spec\ntitle: t\nstatus: active\nparent: [x, y]\n---\n# d\n")
        self.assertEqual(_roles(res, "상위"), [], text)
        self.assertIn("parent 값이 문자열이 아니다", _spec_note(res), text)
        self.assertNotIn("['x'", text + json.dumps(res, ensure_ascii=False))

        # **공유 파서가 전부 `{}` 로 접는 여섯 값**(Q-88). `romeo/frontmatter.py` 의 `yaml.safe_load(raw) or {}`
        # 때문에 `[]`·`{}`·`0`·`false`·`''`·빈 frontmatter 가 모두 빈 매핑으로 돌아온다 — 호출자가
        # `isinstance(dict)` 로 걸러도 정상 빈 매핑과 구별되지 않는다. 그러면 깨진 정본에 고정 설명이 붙고,
        # `fm` 이 그 빈 매핑에서 오므로 다음 정본(brief)의 `parent`·`inputs` 가 **조용히 사라진다**.
        # 그것이 3회차 finding 의 실제 피해이므로, 여기서는 목록이 계속 나오는지까지 본다.
        def _with_brief(fm_text):
            """깨진 spec 옆에 정상 brief 를 둔다 — 두 출력 다 exit 0 이고 트레이스백이 없다."""
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                udir = root / "docs" / "work" / BROKEN_UNIT
                udir.mkdir(parents=True)
                (udir / "spec.md").write_text(fm_text, encoding="utf-8")
                (udir / "brief.md").write_text(
                    f"---\nid: {BROKEN_UNIT}\ntype: brief\ntitle: 깨진 정본 단위\nstatus: active\n"
                    f"parent: {ORPHAN_PARENT}\ninputs: [notes.md]\n---\n# 브리프\n", encoding="utf-8")
                out = []
                for argv in ((), ("--json",)):
                    r = _romeo("context", BROKEN_UNIT, "--root", str(root), *argv, cwd=root)
                    self.assertEqual(r.returncode, 0, r.stderr)
                    self.assertNotIn("Traceback", r.stdout + r.stderr)
                    out.append(r.stdout)
                return out[0], json.loads(out[1])

        for label, fm_text in (("(e) 빈 목록 []", "---\n[]\n---\n# e\n"),
                               ("(f) 빈 매핑 {}", "---\n{}\n---\n# f\n"),
                               ("(g) 숫자 0", "---\n0\n---\n# g\n"),
                               ("(h) 불리언 false", "---\nfalse\n---\n# h\n"),
                               ("(i) 빈 문자열 ''", "---\n''\n---\n# i\n"),
                               ("(j) 빈 frontmatter", "---\n---\n# j\n")):
            text, res = _with_brief(fm_text)
            note = _spec_note(res)
            self.assertIn("읽을 수 없다", note, f"{label} — 공유 파서가 접은 값이 읽힌 정본으로 분류됐다:\n{text}")
            self.assertNotIn(UNIT_DOC_NOTES["spec.md"], note,
                             f"{label} — 깨진 정본에 고정 설명이 붙으면 그 줄은 거짓을 말한다:\n{text}")
            self.assertEqual(_roles(res, "상위"), [f"docs/work/{ORPHAN_PARENT}/charter.md"],
                             f"{label} — 읽힌 정본(brief)의 parent 가 조용히 사라졌다:\n{text}")
            self.assertEqual(_roles(res, "입력"), [f"docs/work/{BROKEN_UNIT}/notes.md"],
                             f"{label} — 읽힌 정본(brief)의 inputs 가 조용히 사라졌다:\n{text}")

    def test_every_unit_in_this_repo_resolves_without_a_missing_reference(self):
        """AC-6 — 저장소의 모든 단위에서 깨진 참조 0 (전수)."""
        units = sorted(p.name for p in (ROOT / "docs" / "work").iterdir() if p.is_dir())
        self.assertGreater(len(units), 20)
        broken = {u: unit_context(ROOT, u)["missing"] for u in units}
        self.assertEqual({u: m for u, m in broken.items() if m}, {})


class TestProcedureNamesTheCommandThatListsTheUnit(unittest.TestCase):
    """AC-7 — 요구하는 자리(절차 1단계)와 실제로 목록을 내는 것이 같은가."""

    def _step1(self):
        text = (ROOT / "core/workflows/plan/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## 절차", text)
        body = text.split("## 절차", 1)[1]
        # 1단계 본문만 읽는다 — 앞부분을 함께 읽으면 역할 분담 표의 다른 명령이 잡힌다(M1 AC-5 의 실측).
        return re.split(r"\n2\. ", body, maxsplit=1)[0]

    def test_step1_names_a_command_that_lists_the_units_spec(self):
        names = sorted(set(re.findall(r"`romeo ([a-z][a-z0-9-]*)", self._step1())))
        self.assertTrue(names, "1단계가 재개할 때 읽을 목록을 내는 명령을 지정해야 한다")
        target = f"docs/work/{CLOSED_UNIT}/spec.md"
        worked = [n for n in names
                  if (lambda r: r.returncode == 0 and target in r.stdout)(_romeo(n, CLOSED_UNIT, "--json"))]
        self.assertTrue(worked, f"1단계가 지정한 명령 {names} 중 어느 것도 단위의 spec 경로를 목록으로 내지 못한다")


if __name__ == "__main__":
    unittest.main()
