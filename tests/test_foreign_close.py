"""남의 저장소 close 판정 — `scenarios/12-close-foreign-repo.md` 「검증」 표의 **조건 id 목록을 파일에서 읽어** 루트와 대조한다.

이 검사가 있는 이유는 「남의 저장소에서 관통을 끝냈다」가 **낱말로는 언제나 참**이기 때문이다.
`close` 를 돌렸다는 것도, `status: done` 이 적혀 있다는 것도 그 주장을 만들지 못한다(K-51) —
무엇이 참이어야 하는가를 조건으로 적고 그 조건을 종료 코드로 판정해야 한다.
`status: done` 은 **손으로도 적힌다**. 그래서 이 검사는 그 낱말 옆에 두 가지를 더 요구한다:
검증 계획의 명령이 한 산출물 위에서 전부 exit 0 으로 돌았는가, 그리고 그것을 **다른 역할**이 읽고 PASS 를 냈는가.

**목록의 주인은 이 파일이 아니라 런북이다.** 여기에 조건을 못 박으면 문서와 검사가 갈리고,
갈린 뒤에는 어느 쪽이 요구인지 말할 수 없다(§11 — 요구하는 자리와 보는 자리를 같게 둔다).
그래서 `conditions()` 가 런북을 읽고, `TestTheListIsWhatIsCompared` 가 **목록을 양쪽으로 바꿔 넣어**
바뀐 목록으로 대조된다는 것을 매번 재확인한다. 한 줄을 빼면 그 조건은 조용히 건너뛰어지는 것이
아니라 요구에서 사라지고, 판정 코드가 없는 id 를 더하면 그 자리에서 막힌다.
시나리오 11 의 `tests/test_foreign_router.py` 와 같은 패턴이고 같은 이유다.

반례는 **빈 루트가 아니라 그럴듯한 거짓 루트**다(§11). 빈 루트는 고치기 전에도 막혔으므로
판별력을 증명하지 않는다. 여기서 만드는 거짓 루트 셋은 전부 **`status: done` 까지 간** 루트다 —
하나는 증거의 종료 코드가 하나 `1` 이고, 하나는 `review/` 가 비어 있고(자기 검토),
하나는 봉투가 있는데 판정이 `FAIL` 이다.

대상 저장소 자체는 이 검사가 읽지 않는다. 실제 루트 판정은 증거 `foreign-close-verdict` 이고 그 명령은

    python3 tests/test_foreign_close.py --verdict <대상 루트>

다 — `required_checks` 에 넣으면 대상 저장소가 없는 머신(CI)에서 이 단위가 영원히 닫히지 않는다.
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

if __package__ in (None, ""):  # 스크립트로 직접 부를 때 sys.path[0] 이 tests/ 다 — 저장소 루트를 넣는다
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml

from romeo import HARNESS_ROOT, frontmatter
from romeo.blocks import required_checks

RUNBOOK = HARNESS_ROOT / "scenarios/12-close-foreign-repo.md"
VERIFY_HEADING = "## 검증"

#: 런북이 담아야 하는 다섯 절. check-2 와 같은 것을 보지만 여기서는 어느 절이 빠졌는지 이름으로 말한다.
SECTIONS = ["## 무엇이 더 필요한가", "## 어디서 구현하는가", "## 검토자를 어떻게 붙이는가",
            "## 검증", "## 되돌리기"]

#: 검토가 성립하려면 봉투의 역할이 이것이어야 한다 — 구현자가 스스로 낸 봉투는 검토가 아니다(C-D3).
REVIEWER_ROLE = "reviewer"

#: 첫 칸이 백틱 조건 id 하나뿐인 표 줄만 조건으로 읽는다. 런북의 「목록의 문법」과 같은 규칙이다.
_ROW = re.compile(r"^\|\s*`([a-z0-9-]+)`\s*\|")


def conditions(runbook_path=RUNBOOK):
    """런북의 「## 검증」 절에서 완료 조건 id 목록을 읽는다. 문서가 목록의 주인이다."""
    lines = Path(runbook_path).read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == VERIFY_HEADING)
    except StopIteration:
        raise AssertionError(f"{runbook_path}: '{VERIFY_HEADING}' 절이 없다 — 목록을 읽을 자리가 없다")
    out = []
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        m = _ROW.match(ln)
        if m:
            out.append(m.group(1))
    if not out:
        raise AssertionError(f"{runbook_path}: '{VERIFY_HEADING}' 절에 백틱 조건 id 표가 없다")
    return out


# --- 대상 루트를 읽는 자리 ---------------------------------------------------


class UnitState:
    """작업 단위 폴더 하나의 상태. 판정 함수는 이것만 본다 — 파일을 다시 열지 않는다.

    **부재를 통과로 읽지 않는다** — spec 이 없거나 읽히지 않으면 `load()` 가 `None` 을 돌려주고
    그때 조건은 전부 거짓이다. 폴더 이름만 만든 것은 작업 단위가 아니다.
    """

    def __init__(self, path, fm, plan, runs, reviews):
        self.path, self.fm, self.plan, self.runs, self.reviews = path, fm, plan, runs, reviews

    @classmethod
    def load(cls, unit):
        unit = Path(unit)
        spec = unit / "spec.md"
        if not spec.is_file() or spec.stat().st_size == 0:
            return None
        try:
            fm, body = frontmatter.read(spec)
        except Exception:
            return None
        if fm is None:
            return None
        try:
            plan = required_checks(body)
        except Exception:
            plan = []
        return cls(unit, fm, plan, _runs(unit), _reviews(unit))


def _runs(unit):
    """`evidence/*.yaml` 을 읽어 `[{명령: 종료 코드}]` 로 만든다. 읽히지 않는 파일은 건너뛴다."""
    d = Path(unit) / "evidence"
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.glob("*.yaml")):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        cmds = {}
        for c in (data.get("commands") or []):
            if isinstance(c, dict) and c.get("command") is not None:
                cmds[str(c["command"])] = c.get("exit_code")
        out.append(cmds)
    return out


def _reviews(unit):
    """`review/*.json` 을 읽어 `(role, gate_verdict)` 목록으로 만든다. 읽히지 않는 파일은 건너뛴다."""
    d = Path(unit) / "review"
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict):
            out.append((data.get("role"), data.get("gate_verdict")))
    return out


def _unit_done(st):
    """`close` 가 그 저장소에서 판정을 끝냈는가. `status` 만으로는 아니다 — `closed_at` 이 함께 있어야 한다."""
    return bool(st) and st.fm.get("status") == "done" and bool(st.fm.get("closed_at"))


def _unit_checks_passed(st):
    """검증 계획의 명령을 **전부** 담고 그 종료 코드가 **전부 0** 인 run 이 하나 이상 있는가.

    run 을 합치지 않는다 — 검사는 **한 산출물 위에서** 전부 돌아야 무엇을 검사했는지 말할 수 있다
    (`romeo/close.py` 의 `select_check_record` 와 같은 이유). 계획이 비어 있으면 거짓이다:
    검사가 0건인 것은 통과가 아니라 **빈 검사**다.
    """
    if not st or not st.plan:
        return False
    wanted = [str((rc or {}).get("command", "")) for rc in st.plan]
    return any(all(cmds.get(cmd) == 0 for cmd in wanted) for cmds in st.runs)


def _unit_reviewed(st):
    """**다른 역할**이 읽고 PASS 를 냈는가. 봉투가 없는 것도, 있는데 FAIL 인 것도 검토가 아니다."""
    return bool(st) and any(r == REVIEWER_ROLE and v == "PASS" for r, v in st.reviews)


#: 조건 id → 판정 함수. 런북 목록에 있는데 여기 없는 id 는 `check` 가 **막는다**.
VERDICTS = {
    "unit-done": _unit_done,
    "unit-checks-passed": _unit_checks_passed,
    "unit-reviewed": _unit_reviewed,
}


def _units(root):
    """대상 루트의 작업 단위 폴더. 폴더가 하나도 없으면 조건은 전부 거짓이다."""
    work = Path(root) / "docs" / "work"
    if not work.is_dir():
        return []
    return sorted(p for p in work.iterdir() if p.is_dir())


def check(root, ids=None):
    """`ids` 중 `root` 가 만족하지 못한 조건을 순서대로 돌려준다. 빈 목록이 통과다.

    세 조건은 **한 단위**가 전부 만족해야 한다 — 서로 다른 단위가 하나씩 만족하는 것은 통과가 아니다.
    그래서 단위별로 실패 목록을 만들고 **가장 짧은 것**을 돌려준다. 통과한 단위가 있으면 빈 목록이다.
    """
    ids = conditions() if ids is None else list(ids)
    unknown = [i for i in ids if i not in VERDICTS]
    if unknown:
        raise AssertionError(
            f"판정 코드가 없는 조건 id: {unknown} — 런북에 조건을 더했으면 {Path(__file__).name} 의 "
            f"VERDICTS 에 판정 함수를 같은 커밋에서 함께 넣는다(§11)")
    units = _units(root)
    if not units:
        return list(ids)
    best = None
    for unit in units:
        st = UnitState.load(unit)
        failed = [i for i in ids if not VERDICTS[i](st)]
        if best is None or len(failed) < len(best):
            best = failed
        if not best:
            break
    return best


# --- 합성 루트 ---------------------------------------------------------------

#: 합성 단위의 검증 계획. `required_checks` 파서가 읽는 형태 그대로 spec 본문에 넣는다.
_PLAN = [{"id": "check-1", "command": "grep -q \"^## 합성\" CLAUDE.md"},
         {"id": "check-2", "command": "test -f CLAUDE.md"}]

_BODY = ("\n# 합성 단위\n\n## 확인란\n\n- **무엇을:** 합성 루트다.\n\n## 검증 계획\n\n```yaml\n"
         + yaml.safe_dump({"required_checks": _PLAN}, allow_unicode=True, sort_keys=False).strip()
         + "\n```\n")


def make_root(base, unit_id, status="done", closed=True, plan=_PLAN,
              exit_codes=None, missing_command=False, reviews=(("reviewer", "PASS"),), spec=True):
    """대상 저장소 모양의 합성 루트를 만든다.

    `exit_codes` 로 증거의 종료 코드를, `missing_command` 로 계획의 마지막 명령이 **기록에 없는** run 을,
    `reviews` 로 검토 봉투의 `(role, gate_verdict)` 목록을 정한다. `spec=False` 면 폴더만 서고 spec 이 없다.
    """
    root = Path(base)
    unit = root / "docs" / "work" / unit_id
    unit.mkdir(parents=True, exist_ok=True)
    if not spec:
        return root
    frontmatter.write(unit / "spec.md", {
        "id": unit_id,
        "type": "spec",
        "title": "합성 단위",
        "unit": "T1",
        "mode": "delivery",
        "intent": "write",
        "facets": ["docs", "security"],
        "status": status,
        "approved_at": "2026-09-04T23:44:05+09:00",
        "approved_by": "Supervibecoder0709",
        "closed_at": "2026-09-06T11:45:44+09:00" if closed else None,
    }, _BODY)

    cmds = list(plan)[:-1] if missing_command else list(plan)
    codes = list(exit_codes) if exit_codes is not None else [0] * len(cmds)
    ev = unit / "evidence"
    ev.mkdir(exist_ok=True)
    (ev / "run_synthetic.yaml").write_text(yaml.safe_dump({
        "schema": "romeo/evidence@0.1.0",
        "run_id": "run_synthetic",
        "unit_id": unit_id,
        "commands": [{"id": rc["id"], "command": rc["command"], "exit_code": code}
                     for rc, code in zip(cmds, codes)],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")

    rv = unit / "review"
    rv.mkdir(exist_ok=True)
    for n, (role, verdict) in enumerate(reviews, 1):
        (rv / f"run_synthetic-{n}-{role}.json").write_text(json.dumps({
            "schema": "romeo/result-envelope@0.1.0",
            "unit_id": unit_id,
            "role": role,
            "gate_verdict": verdict,
            "evidence_ref": f"docs/work/{unit_id}/evidence/run_synthetic.yaml",
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    return root


class TestConditionsComeFromTheRunbook(unittest.TestCase):
    """AC-2 앞부분 — 목록을 파일에서 읽는다."""

    def test_the_runbook_owns_the_list(self):
        ids = conditions()
        for cid in VERDICTS:
            self.assertIn(cid, ids, f"'{cid}' 가 런북 「검증」 표에 없다 — 판정 코드만 있고 요구가 없다(§11)")
        self.assertEqual(len(ids), len(set(ids)), f"런북 「검증」 표에 조건 id 가 중복된다: {ids}")

    def test_a_runbook_without_the_section_is_refused(self):
        """그럴듯한 거짓 값 — 절 제목만 바꿔도 검사는 조용히 0건으로 통과하지 않는다."""
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "runbook.md"
            fake.write_text(RUNBOOK.read_text(encoding="utf-8").replace(VERIFY_HEADING, "## 확인"),
                            encoding="utf-8")
            with self.assertRaises(AssertionError):
                conditions(fake)

    def test_the_runbook_carries_the_five_sections(self):
        """런북이 다섯 절을 담는가 — check-2 와 같은 것을 보지만 여기서는 어느 절이 빠졌는지 이름으로 말한다."""
        text = RUNBOOK.read_text(encoding="utf-8")
        for heading in SECTIONS:
            self.assertIn(heading, text, f"런북에 '{heading}' 절이 없다")

    def test_the_evidence_command_is_printed_in_the_runbook(self):
        """실제 대상을 판정하는 명령이 런북에 적혀 있는가 — 적히지 않으면 그 판정이 어디서 나왔는지 말할 수 없다."""
        self.assertIn("python3 tests/test_foreign_close.py --verdict",
                      RUNBOOK.read_text(encoding="utf-8"))


class TestSyntheticRoots(unittest.TestCase):
    """AC-3 — 조건을 만족하지 않는 합성 루트에서 실패하고 만족하는 합성 루트에서 통과한다.

    거짓 루트는 전부 **`status: done` 까지 간** 것이다. 빈 루트는 고치기 전에도 막혔으므로 판별력을 증명하지 않는다(§11).
    """

    def setUp(self):
        self.ids = conditions()

    def test_satisfying_root_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-pass")
            self.assertEqual(check(root, self.ids), [])

    def test_one_failing_exit_code_fails(self):
        """그럴듯한 거짓 루트 ① — `status: done` 까지 갔는데 증거의 종료 코드 하나가 `1` 이다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-rc1", exit_codes=[0, 1])
            self.assertEqual(check(root, self.ids), ["unit-checks-passed"])

    def test_no_reviewer_envelope_fails(self):
        """그럴듯한 거짓 루트 ② — 닫혔고 검사도 통과했는데 `review/` 에 검토자 봉투가 없다(자기 검토)."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-selfreview", reviews=())
            self.assertEqual(check(root, self.ids), ["unit-reviewed"])

    def test_failing_reviewer_verdict_fails(self):
        """그럴듯한 거짓 루트 ③ — 봉투는 있는데 판정이 `FAIL` 이다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-fail", reviews=(("reviewer", "FAIL"),))
            self.assertEqual(check(root, self.ids), ["unit-reviewed"])

    def test_implementer_envelope_is_not_a_review(self):
        """그럴듯한 거짓 루트 ④ — `review/` 에 PASS 봉투가 있는데 그것을 **구현자가 냈다**(C-D3)."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-selfpass",
                             reviews=(("implementer", "PASS"),))
            self.assertEqual(check(root, self.ids), ["unit-reviewed"])

    def test_a_failing_round_before_a_passing_one_still_passes(self):
        """실제 관통의 모양 — `fail · fail · pass` 회차. PASS 봉투가 하나라도 있으면 이 조건은 참이다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-rounds",
                             reviews=(("reviewer", "FAIL"), ("reviewer", "FAIL"), ("reviewer", "PASS")))
            self.assertEqual(check(root, self.ids), [])

    def test_active_unit_is_not_done(self):
        """그럴듯한 거짓 루트 ⑤ — 검사도 검토도 끝났는데 `close` 를 부르지 않아 아직 `active` 다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-active", status="active", closed=False)
            self.assertEqual(check(root, self.ids), ["unit-done"])

    def test_status_done_without_closed_at_fails(self):
        """그럴듯한 거짓 루트 ⑥ — `status: done` 만 손으로 적고 `closed_at` 이 비어 있다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-handwritten", closed=False)
            self.assertEqual(check(root, self.ids), ["unit-done"])

    def test_a_run_missing_one_planned_command_fails(self):
        """그럴듯한 거짓 루트 ⑦ — 기록된 것은 전부 exit 0 인데 **계획의 명령 하나가 기록에 없다**."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-partial", missing_command=True)
            self.assertEqual(check(root, self.ids), ["unit-checks-passed"])

    def test_two_runs_cannot_be_merged(self):
        """검사는 **한 산출물 위에서** 전부 돌아야 한다 — 두 run 이 반씩 통과한 것은 통과가 아니다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-split", exit_codes=[0, 1])
            unit = Path(root) / "docs" / "work" / "feat-20260904-synthetic-split"
            (unit / "evidence" / "run_synthetic2.yaml").write_text(yaml.safe_dump({
                "schema": "romeo/evidence@0.1.0", "run_id": "run_synthetic2",
                "commands": [{"id": "check-2", "command": _PLAN[1]["command"], "exit_code": 0}],
            }, allow_unicode=True, sort_keys=False), encoding="utf-8")
            self.assertEqual(check(root, self.ids), ["unit-checks-passed"],
                             "두 run 이 반씩 통과한 것을 합쳐서 통과로 읽었다")

    def test_an_empty_check_plan_is_not_a_pass(self):
        """검증 계획이 비어 있으면 통과가 아니다 — 검사 0건은 **빈 검사**다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-noplan", plan=[])
            unit = Path(root) / "docs" / "work" / "feat-20260904-synthetic-noplan"
            fm, _ = frontmatter.read(unit / "spec.md")
            frontmatter.write(unit / "spec.md", fm, "\n# 합성 단위\n\n검증 계획이 없다.\n")
            self.assertEqual(check(root, self.ids), ["unit-checks-passed"])

    def test_empty_root_fails_every_condition(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(check(td, self.ids), self.ids, "빈 루트에서 실패한 것이 목록 전체가 아니다")

    def test_folder_without_spec_is_not_a_unit(self):
        """**부재를 통과로 읽지 않는다** — 이름만 만든 폴더는 라우터가 세운 것이 아니다."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-empty", spec=False)
            self.assertEqual(check(root, self.ids), self.ids)

    def test_conditions_split_across_two_units_is_not_a_pass(self):
        """한 단위가 전부 만족해야 한다 — 나눠 가진 두 단위는 통과가 아니다."""
        with tempfile.TemporaryDirectory() as td:
            make_root(td, "feat-20260904-synthetic-a", reviews=())              # 닫혔고 검사는 통과, 검토 없음
            root = make_root(td, "feat-20260904-synthetic-b", exit_codes=[0, 1])  # 닫혔고 검토는 받았으나 검사 실패
            self.assertNotEqual(check(root, self.ids), [], "두 단위가 조건을 나눠 가졌는데 통과했다")


class TestTheListIsWhatIsCompared(unittest.TestCase):
    """AC-2 뒷부분 — 목록을 양쪽으로 바꿔 넣어 **바뀐 목록으로 대조한다**는 것을 재확인한다."""

    def setUp(self):
        self.ids = conditions()

    def _runbook_with(self, replace, into):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        fake = Path(td.name) / "runbook.md"
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn(replace, text, f"런북에 '{replace}' 줄이 없다 — 바꿔 넣을 자리가 사라졌다")
        fake.write_text(text.replace(replace, into, 1), encoding="utf-8")
        return fake

    def test_removing_a_row_removes_the_requirement(self):
        """`unit-reviewed` 줄을 지우면, 검토자 봉투가 없는 루트가 **통과한다** — 건너뛰는 것이 아니라 요구가 사라진다."""
        row = "| `unit-reviewed` |"
        mutated = conditions(self._runbook_with(row, "| 그 줄을 지운다 |"))
        self.assertNotIn("unit-reviewed", mutated)
        self.assertEqual(len(mutated), len(self.ids) - 1)

        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-selfreview", reviews=())
            self.assertEqual(check(root, self.ids), ["unit-reviewed"],
                             "원래 목록이 검토 없는 루트를 잡지 못했다")
            self.assertEqual(check(root, mutated), [], "바뀐 목록이 여전히 검토를 요구한다")

    def test_removing_the_checks_row_removes_the_requirement(self):
        """`unit-checks-passed` 도 같다 — 한 줄만 지워도 그 요구만 사라진다."""
        row = "| `unit-checks-passed` |"
        mutated = conditions(self._runbook_with(row, "| 그 줄을 지운다 |"))
        self.assertNotIn("unit-checks-passed", mutated)
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-rc1", exit_codes=[0, 1])
            self.assertEqual(check(root, self.ids), ["unit-checks-passed"])
            self.assertEqual(check(root, mutated), [], "바뀐 목록이 여전히 검사 통과를 요구한다")

    def test_adding_a_condition_without_verdict_code_blocks(self):
        """그럴듯한 거짓 값 — 형태는 조건 id 인데 판정 코드가 없는 항목을 더하면 그 자리에서 막힌다."""
        fake_id = "unit-pushed"
        mutated = conditions(self._runbook_with(
            "| `unit-reviewed` |",
            f"| `{fake_id}` | 판정 코드가 없는 그럴듯한 거짓 조건 |\n| `unit-reviewed` |"))
        self.assertIn(fake_id, mutated)
        with tempfile.TemporaryDirectory() as td:
            root = make_root(td, "feat-20260904-synthetic-pass")
            self.assertEqual(check(root, self.ids), [], "만족하는 루트가 원래 목록에서 막혔다")
            with self.assertRaises(AssertionError):
                check(root, mutated)


def _verdict(root):
    """실제 대상 루트를 판정한다 — 증거 `foreign-close-verdict` 가 부르는 자리다."""
    root = Path(root).expanduser()
    ids = conditions()
    print(f"대상 루트: {root}")
    print(f"런북: {RUNBOOK.relative_to(HARNESS_ROOT)} 「{VERIFY_HEADING}」 · 조건 {len(ids)}건 {ids}")
    if not root.is_dir():
        print("판정: FAIL — 그런 루트가 없다")
        return 1
    for unit in _units(root):
        st = UnitState.load(unit)
        got = {i: VERDICTS[i](st) for i in ids}
        print(f"  {unit.name}: " + " · ".join(f"{k}={'참' if v else '거짓'}" for k, v in got.items()))
        if st:
            print(f"    status={st.fm.get('status')!r} closed_at={st.fm.get('closed_at')!r} "
                  f"· 검증 계획 {len(st.plan)}건 · evidence run {len(st.runs)}건 · review 봉투 {len(st.reviews)}건")
            for cmds in st.runs:
                hit = [str((rc or {}).get('command', '')) for rc in st.plan
                       if cmds.get(str((rc or {}).get('command', ''))) is not None]
                bad = [c for c in hit if cmds.get(c) != 0]
                print(f"      run: 계획 {len(hit)}/{len(st.plan)}건 기록 · 비0 {len(bad)}건")
            for role, verdict in st.reviews:
                print(f"      review: role={role!r} gate_verdict={verdict!r}")
    failed = check(root, ids)
    print(f"판정: {'PASS' if not failed else 'FAIL — 만족하지 못한 조건: ' + ', '.join(failed)}")
    return 0 if not failed else 1


_EVIDENCE = {"--verdict": _verdict}

if __name__ == "__main__":
    for flag, fn in _EVIDENCE.items():
        if flag in sys.argv:
            i = sys.argv.index(flag)
            if i + 1 >= len(sys.argv):
                print(f"사용법: python3 tests/test_foreign_close.py {flag} <경로>", file=sys.stderr)
                sys.exit(2)
            sys.exit(fn(sys.argv[i + 1]))
    unittest.main()
