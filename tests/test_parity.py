"""동등성 판정(`romeo fixtures parity`)이 역할 교체 재실행의 결과 계약 쌍을 실제로 대조한다.

이 테스트가 지키는 계약:
 1. 저장소의 케이스 파일이 구조적으로 유효하다 — 필수 키·id 패턴·역할 일관성·출처(`source.kind`).
 2. 케이스가 선언한 기대(same/differ)와 실제 판정이 일치한다.
 3. differ 케이스가 선언한 실패 코드로 실패한다 — 다른 이유로 어긋나면 잡는다.
 4. 리포트가 정본 문장(스키마 유효·required_checks 동일·gate 판정 동일)을 인쇄한다.
 5. gate 판정만 다른 쌍을 잡는다.
 6. 스키마를 어긴 결과 계약을 잡는다 — G1 스키마와의 연결이 끊기면 실패한다.
 7. 한쪽에만 역할이 있는 쌍을 잡는다.
 8. 비0 종료 코드는 성공/실패로만 비교한다 — 1≠2 는 불일치가 아니고 0≠1 은 불일치다.
 9. 실행 결과가 없는 케이스는 일치로 세지 않고 미실행으로 인쇄한다. 미실행만 있으면 검사기 검증이 통과하지 않는다.
10. CLI 배선이 살아 있다 — 구조 오류와 판정 실패를 종료 코드로 구분해 낸다.
11. **판정이 두 층이다(D-b).** 손으로 쓴 합성 케이스(`source.kind: authored`)는 검사기 자기 검증만 하고
    게이트를 통과시키지 못한다. 게이트는 실제 교차 실행 관측(`source.kind: observed`)이 1건 이상일 때만 판정한다.
    관측 0건이면 게이트는 `UNDETERMINED`(미판정)이고 종료 코드는 1 이다(K-51).
    **2026-08-29 에 실제 T1 교차 관통으로 관측 1건이 생겨 게이트가 미판정을 벗어났다.**
    그래서 이 파일의 기대는 게이트 값을 고정하지 않고 **관측 건수와 게이트의 관계**만 본다 —
    관측 0건이면 반드시 미판정, 1건 이상이면 반드시 판정. 종료 코드는 어느 쪽이든 게이트를 따른다.
    값을 고정하면 관측이 늘 때마다 테스트가 깨지고, 그때 고치고 싶어지는 것은 테스트가 아니라
    케이스의 `expect` 다 — 그것이 D-b 가 막으려는 행동이다. 그래서 2번 계약(기대 대조)은
    **합성 케이스만** 본다. 관측의 expect 불일치는 검사기의 버그가 아니라 현실의 결과이고,
    그 자리는 `gate_verdict` 가 소유한다.
12. **증거 없는 PASS 는 '동일'이 아니라 '판정 불가'다.** checks 0건·evidence_ref 0건인 PASS 쌍은 양면이 똑같아도
    동등성을 판정하지 못한다(`EVIDENCE_MISSING`).
13. **역할 계약에 없는 능력을 쓴 봉투는 판정 불가다.** 실행 능력(`run-command`)이 없는 역할이 checks 를 실었으면
    `ROLE_CONTRACT_VIOLATION` 이다 — 케이스를 조용히 고치는 것으로는 다음에 또 들어온다.
14. 리포트가 관측/합성 건수를 인쇄한다 — 무엇으로 계산한 판정인지 읽는 사람이 알아야 한다.
15. **`observed` 라는 선언은 검사된다.** 게이트를 여는 유일한 열쇠가 손으로 고칠 수 있는 한 단어이면
    게이트는 아무것도 지키지 않는다. 관측 케이스는 `source.ref`·`unit_id` 가 저장소에 실재해야 하고,
    어긋나면 통과도 미판정도 아니라 구조 오류(`PARITY_INVALID`)다.
16. **검사기 자기 검증은 합성 케이스만으로 계산한다.** 합성 0건에서 PASS 를 인쇄하는 것은
    0건을 근거로 통과를 말하는 것이다 — 그런 실행은 `해당 없음` 이고, 종료 코드 0 을 내지 않는다.
17. **관측 케이스는 봉투를 파일로만 받는다.** 케이스 파일 안에 손으로 적은 봉투는 아무 검사도 받지 않는데
    게이트가 비교하는 값이 바로 그 봉투다. 파일로 받아 **종료 검사와 같은 앵커 검사**를 태운다 —
    규칙이 두 벌이 되면 느슨한 쪽이 게이트를 연다(K-63). 그러므로 이 테스트의 관측 케이스도
    손으로 만들 수 없다: 승인 커밋 · 계약 생성 명령 · 증거 기록 명령이 남긴 산출물로만 만든다.
18. **검토자 면은 두 면이 같은 산출물을 봤을 때만 비교한다(D-73).** 검토자의 판정은 자기가 본 산출물의 함수다 —
    산출물이 다르면 판정이 갈리는 것이 옳고 그 차이는 런타임의 차이가 아니다. 검사기는 그 면을 `PRODUCT_DIFFERS` 로
    분리해 게이트 판정에서 빼되 '비교 불가' 로 인쇄한다. 산출물이 같으면 지금처럼 비교한다(전제가 핑계가 되지 않는다).
    구현자 면은 산출물과 무관하게 비교한다. 산출물 식별은 관측 케이스에서는 증거의 `head_sha`·`dirty_tree_hash` 에서
    읽고(케이스 파일의 선언은 구조 오류), 합성 케이스에서는 면마다 `product:` 로 선언한다. 비교할 면이 하나도
    남지 않은 관측은 게이트를 열지 못한다(미판정).
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from romeo import frontmatter
from romeo.cli import main
from romeo.docs import approve_unit, create_unit
from romeo.envelope import write_envelope
from romeo.evidence import run_command
from romeo.parity import (ANCHOR_INVALID, CANON_REASON, INCOMPARABLE_TEXT, NOT_APPLICABLE,
                          PRODUCT_DIFFERS, PRODUCT_KEYS, PRODUCT_UNKNOWN, WORK_DIR,
                          check_parity_cases, compare_case, format_parity, load_parity_cases,
                          load_role_contracts, run_parity)
from romeo.policy import route
from romeo.schema import validate
from romeo.util import dump_yaml, load_json, load_yaml, project_root

REPO = project_root(Path(__file__).parent)
CASE_DIR = REPO / "fixtures/parity"
RESULT_SCHEMA = load_json(REPO / "core/schemas/result-envelope.json")

# 합성 케이스는 지어낸 단위를 써도 된다 — 게이트를 열지 못하기 때문이다.
UNIT_ID = "chg-20260827-rg-fallback-validate-245m"
SHA64 = "1" * 64
EVIDENCE = f"{WORK_DIR}/{UNIT_ID}/evidence/run-m1.yaml"
# 반례용 — docs/work/ 에 없는 단위와 그 안의 없는 증거 파일.
FAKE_UNIT = "feat-20260828-license-field-a1b2"
FAKE_EVIDENCE = f"{WORK_DIR}/{FAKE_UNIT}/evidence/run-a.yaml"

AUTHORED = {"kind": "authored", "ref": "tests/test_parity.py", "date": "2026-08-28"}
# 합성 케이스의 산출물 식별 — 검토자 면은 두 면이 같은 산출물을 봤을 때만 비교한다(D-73).
PRODUCT = {"head_sha": "a" * 40, "dirty_tree_hash": "b" * 64}
OTHER_PRODUCT = {"head_sha": "a" * 40, "dirty_tree_hash": "c" * 64}


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          check=True).stdout.strip()


class ObservedRun:
    """실제 교차 실행이 남기는 것과 같은 산출물을 가진 저장소를 만든다.

    관측 케이스의 봉투는 이제 종료 검사와 같은 앵커 검사를 받는다 — 그 중 하나가 **작업 계약 재계산**이라
    손으로는 만들 수 없다. 그래서 여기서도 승인 커밋 · `write_envelope` · `run_command` 로 만든다.
    실행 두 벌(run-a · run-b)이 baseline · swapped 두 면이 된다.
    """

    RUNS = ("run-a", "run-b")

    def __init__(self, reviewer=False):
        """`reviewer=True` 면 run 마다 검토자 계약도 만들고 `review/` 자리를 연다 — 검토자 면을 가진 관측 케이스용."""
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        shutil.copytree(REPO / "core", self.root / "core")   # 정책표·역할 계약·스키마가 있어야 계약을 계산한다
        git("init", "-q", cwd=self.root)
        git("config", "user.email", "t@example.com", cwd=self.root)
        git("config", "user.name", "t", cwd=self.root)
        (self.root / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "init", cwd=self.root)
        out = route({"unit": "T0", "mode": "delivery", "intent": "write", "facets": ["tooling"],
                     "gates": [], "blast_radius": "small", "uncertainty": "low"})
        res = create_unit(out, "관측 케이스", "parity-observed", "역할 교체 재실행",
                          project_root=self.root, harness_root=self.root, date="20260828")
        self.unit = res["id"]
        self.spec = Path(res["files"][0])
        fm, body = frontmatter.read(self.spec)
        body = body.replace("NEEDS_INPUT", "채움").replace('command: "채움"', 'command: "true"')
        frontmatter.write(self.spec, fm, body.replace("- [ ] AC-1", "- [x] AC-1"))
        approve_unit(self.unit, "tester", project_root=self.root)
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "approve", cwd=self.root)
        self.base_sha = git("rev-parse", "HEAD", cwd=self.root)
        (self.root / "x.txt").write_text("impl\n", encoding="utf-8")
        git("add", ".", cwd=self.root)
        git("commit", "-q", "-m", "impl", cwd=self.root)
        self.task_sha = {}
        self.review_sha = {}
        for run in self.RUNS:
            built = write_envelope(self.unit, "implementer", project_root=self.root,
                                   harness_root=self.root, base_sha=self.base_sha, run_name=run)
            self.task_sha[run] = built["sha256"]
            if reviewer:
                self.review_sha[run] = write_envelope(self.unit, "reviewer", project_root=self.root,
                                                      harness_root=self.root, base_sha=self.base_sha,
                                                      run_name=run)["sha256"]
            run_command(self.unit, "true", run_name=run, project_root=self.root)
        (self.root / "docs/work" / self.unit / "result").mkdir()
        if reviewer:
            (self.root / "docs/work" / self.unit / "review").mkdir()

    def cleanup(self):
        self.tmp.cleanup()

    def evidence(self, run):
        return f"{WORK_DIR}/{self.unit}/evidence/{run}.yaml"

    def product(self, run):
        """그 run 의 증거가 기록한 산출물 식별 — 검사기가 읽어야 하는 바로 그 값이다."""
        rec = load_yaml(self.root / self.evidence(run))
        return tuple(rec[k] for k in PRODUCT_KEYS)

    def diverge(self, run, name="diverged.txt"):
        """그 run 의 산출물을 다르게 만든다 — 작업 트리에 파일을 더하고 **증거 기록 명령**을 한 번 더 돌려
        트리 해시가 실행으로 갱신되게 한다. 케이스 파일에는 아무것도 적지 않는다(D-b)."""
        (self.root / name).write_text(f"{run}\n", encoding="utf-8")
        run_command(self.unit, "true", run_name=run, project_root=self.root)

    def review_envelope(self, run, **over):
        """검토자 봉투 — 검사를 실행하지 않고 그 run 의 증거를 지목한다(core/roles/reviewer.yaml)."""
        env = {
            "schema": "romeo/result-envelope@0.1.0",
            "unit_id": self.unit,
            "role": "reviewer",
            "task_envelope_ref": {"path": f"{WORK_DIR}/{self.unit}/task/{run}-reviewer.json",
                                  "sha256": self.review_sha[run]},
            "checks": [],
            "gate_verdict": "PASS",
            "blocked_reason": None,
            "findings": [],
            "evidence_ref": self.evidence(run),
        }
        env.update(over)
        return env

    def write_review(self, run, name=None, **over):
        """검토자 결과 계약 파일을 `review/` 에 쓰고 케이스가 지목할 상대 경로를 돌려준다."""
        rel_path = f"{WORK_DIR}/{self.unit}/review/{name or run}-reviewer.json"
        (self.root / rel_path).write_text(
            json.dumps(self.review_envelope(run, **over), ensure_ascii=False), encoding="utf-8")
        return rel_path

    def envelope(self, run, **over):
        env = {
            "schema": "romeo/result-envelope@0.1.0",
            "unit_id": self.unit,
            "role": "implementer",
            "task_envelope_ref": {"path": f"{WORK_DIR}/{self.unit}/task/{run}-implementer.json",
                                  "sha256": self.task_sha[run]},
            "checks": [{"id": "check-1", "command": "true", "exit_code": 0}],
            "gate_verdict": "PASS",
            "blocked_reason": None,
            "findings": [],
            "evidence_ref": self.evidence(run),
        }
        env.update(over)
        return env

    def write_result(self, run, name=None, **over):
        """결과 계약 파일을 쓰고 케이스가 지목할 상대 경로를 돌려준다."""
        rel_path = f"{WORK_DIR}/{self.unit}/result/{name or run}-implementer.json"
        (self.root / rel_path).write_text(
            json.dumps(self.envelope(run, **over), ensure_ascii=False), encoding="utf-8")
        return rel_path

    def case(self, base=None, swap=None, base_review=None, swap_review=None, implementer=True, **kw):
        """관측 케이스. `base_review`/`swap_review` 를 주면 검토자 면이 붙고, `implementer=False` 면 구현자 면을 뺀다."""
        results = {"baseline": {}, "swapped": {}}
        if implementer:
            results["baseline"]["implementer"] = {"file": base or self.write_result("run-a")}
            results["swapped"]["implementer"] = {"file": swap or self.write_result("run-b")}
        if base_review:
            results["baseline"]["reviewer"] = {"file": base_review}
        if swap_review:
            results["swapped"]["reviewer"] = {"file": swap_review}
        data = {
            "_path": "<메모리>", "id": "pr-observed", "title": "관측 케이스", "unit_id": self.unit,
            "expect": "same",
            "baseline": {"results": results["baseline"]},
            "swapped": {"results": results["swapped"]},
            "source": {"kind": "observed", "ref": self.evidence("run-a"), "date": "2026-08-28"},
        }
        data.update(kw)
        return data

    def check(self, case):
        return check_parity_cases([case], harness_root=self.root).get("<메모리>", [])

    def report(self, cases):
        return run_parity(cases, harness_root=self.root)


def envelope(role="implementer", verdict="PASS", blocked=None, checks=None, evidence=EVIDENCE,
             unit=UNIT_ID):
    return {
        "schema": "romeo/result-envelope@0.1.0",
        "unit_id": unit,
        "role": role,
        "task_envelope_ref": {"path": f".harness/runs/{unit}/run-a/task-{role}.json", "sha256": SHA64},
        "checks": [{"id": "check-1", "command": "python3 -m unittest tests.test_parity", "exit_code": 0}]
        if checks is None else checks,
        "gate_verdict": verdict,
        "blocked_reason": blocked,
        "findings": [],
        "evidence_ref": evidence,
    }


def reviewer_envelope(verdict="PASS", evidence=EVIDENCE):
    """검토자는 검사를 실행하지 않는다 — 능력 목록에 run-command 가 없다(core/roles/reviewer.yaml)."""
    return envelope(role="reviewer", verdict=verdict, checks=[], evidence=evidence)


def case(expect="same", base=None, swap=None, base_product=PRODUCT, swap_product=PRODUCT, **kw):
    """합성 케이스. 두 면은 기본으로 **같은 산출물**을 선언한다 — 검토자 면이 비교되려면 그래야 한다(D-73)."""
    data = {
        "_path": "<메모리>",
        "id": "pr-memory-case",
        "title": "메모리에서 구성한 케이스",
        "unit_id": UNIT_ID,
        "expect": expect,
        "baseline": {"results": base if base is not None else {"implementer": envelope()}},
        "swapped": {"results": swap if swap is not None else {"implementer": envelope()}},
        "source": dict(AUTHORED),
    }
    if base_product is not None:
        data["baseline"]["product"] = dict(base_product)
    if swap_product is not None:
        data["swapped"]["product"] = dict(swap_product)
    data.update(kw)
    return data


def write_cases(directory, cases):
    import yaml
    for i, data in enumerate(cases):
        body = {k: v for k, v in data.items() if not k.startswith("_")}
        path = Path(directory) / f"{body.get('id', f'pr-x{i}')}.yaml"
        path.write_text(yaml.safe_dump(body, allow_unicode=True, sort_keys=False), encoding="utf-8")


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class TestRepoCases(unittest.TestCase):
    """저장소에 실린 케이스 파일 자체를 본다."""

    @classmethod
    def setUpClass(cls):
        cls.cases = load_parity_cases(CASE_DIR)
        cls.rep = run_parity(cls.cases)

    def test_repo_cases_are_structurally_valid(self):
        self.assertGreaterEqual(len(self.cases), 3, "케이스가 3건 미만이면 게이트가 아무것도 증명하지 못한다")
        self.assertEqual(check_parity_cases(self.cases), {})

    def test_synthetic_outcome_matches_declared_expectation(self):
        """합성 케이스만 본다 — 그것이 검사기의 정확성을 재는 자리다(G12).

        관측 케이스의 expect 불일치는 검사기의 버그가 아니라 현실의 결과이고,
        그 자리는 gate_verdict 가 소유한다. 여기서 함께 보면 관측이 어긋날 때마다
        expect 를 고치고 싶어지고, 그것이 D-b 가 막으려는 행동이다.
        """
        checked = 0
        for row in self.rep["rows"]:
            if row["status"] == "pending" or row["kind"] == "observed":
                continue
            checked += 1
            self.assertTrue(row["ok"], f"{row['id']}: 기대 {row['expect']} · 실제 {row['actual']} · {row['detail']}")
        self.assertGreaterEqual(checked, 3, "합성 케이스가 3건 미만이면 검사기 자기 검증이 성립하지 않는다")
        self.assertEqual(self.rep["checker_verdict"], "PASS")

    def test_gate_is_determined_only_by_observed_cases(self):
        """D-b: 손으로 쓴 케이스만으로는 게이트를 판정하지 않는다.

        관측 0건이면 반드시 미판정이고, 1건 이상이면 반드시 판정이 선다.
        어느 쪽이든 종료 코드는 게이트를 따른다 — 이 관계가 D-b 의 전부다.
        2026-08-29 에 실제 T1 교차 관통으로 관측 1건이 생겨 게이트가 UNDETERMINED 를 벗어났다.
        """
        if self.rep["observed"] == 0:
            self.assertEqual(self.rep["gate_verdict"], "UNDETERMINED",
                             "관측이 0건인데 게이트가 판정을 냈다 — 합성 케이스가 게이트를 열고 있다")
        else:
            self.assertIn(self.rep["gate_verdict"], ("PASS", "FAIL"),
                          "관측이 있는데 게이트가 미판정이다 — 관측 케이스가 비교되지 않았다")
        self.assertEqual(self.rep["verdict"], self.rep["gate_verdict"], "명령의 종료 코드는 게이트를 따른다")

    def test_differ_cases_produce_declared_codes(self):
        declared = {c["id"]: set(c.get("expect_codes") or []) for c in self.cases if c["expect"] == "differ"}
        self.assertTrue(declared, "differ 케이스가 하나도 없으면 검사기가 실패를 잡는지 알 수 없다")
        for row in self.rep["rows"]:
            if row["id"] in declared:
                self.assertLessEqual(declared[row["id"]], set(row["codes"]),
                                     f"{row['id']} 가 선언한 코드가 아니라 {row['codes']} 로 어긋났다")

    def test_same_case_prints_canon_sentence(self):
        text = format_parity(self.rep)
        self.assertIn(CANON_REASON, text, "정본이 요구하는 관찰 가능한 문장이 리포트에서 사라졌다")
        self.assertIn("검사기 자기 검증: PASS", text)
        if self.rep["observed"] == 0:
            self.assertIn("핵심 동등성 게이트: 미판정", text)
        else:
            self.assertIn(f"핵심 동등성 게이트: {self.rep['gate_verdict']}", text)
            self.assertIn("관측 1건으로 판정했다" if self.rep["observed"] == 1
                          else f"관측 {self.rep['observed']}건으로 판정했다", text)

    def test_report_prints_observed_and_synthetic_counts(self):
        text = format_parity(self.rep)
        self.assertIn(f"관측 {self.rep['observed']}건", text)
        self.assertIn(f"합성 {self.rep['synthetic']}건", text)

    def test_report_counts_pending_apart_from_matched(self):
        """자리표(pending)와 실행된 케이스는 따로 센다.

        자리표가 1건 이상이어야 한다는 요구는 **관측이 0건일 때만** 성립한다 —
        자리표의 목적이 '실제 실행이 채울 자리' 이므로, 채워지고 나면 0건이 정상이다.
        """
        self.assertEqual(self.rep["total"], self.rep["executed"] + self.rep["pending"])
        if self.rep["observed"] == 0:
            self.assertGreaterEqual(self.rep["pending"], 1, "실제 실행이 채울 자리표 케이스가 있어야 한다")
            self.assertIn("미실행", format_parity(self.rep))

    def test_repo_cases_have_no_role_contract_violation(self):
        for row in self.rep["rows"]:
            self.assertNotIn("ROLE_CONTRACT_VIOLATION", row["codes"],
                             f"{row['id']}: 정본 케이스가 역할 계약에 없는 능력을 기록한다 — {row['detail']}")
            self.assertNotIn("EVIDENCE_MISSING", row["codes"],
                             f"{row['id']}: 정본 케이스에 증거 없는 PASS 가 있다 — {row['detail']}")


class TestComparison(unittest.TestCase):
    """메모리에서 구성한 쌍으로 비교기의 판정을 각각 깨본다."""

    def compare(self, c):
        return compare_case(c, RESULT_SCHEMA)

    def test_identical_pair_is_same(self):
        row = self.compare(case())
        self.assertEqual(row["actual"], "same")
        self.assertEqual(row["detail"], [])
        self.assertTrue(row["ok"])

    def test_verdict_mismatch_is_caught(self):
        row = self.compare(case(swap={"implementer": envelope(verdict="FAIL")}))
        self.assertEqual(row["actual"], "differ")
        self.assertIn("VERDICT_DIFFERS", row["codes"])
        self.assertFalse(row["ok"], "expect: same 인데 어긋났으면 통과가 아니다")

    def test_blocked_reason_mismatch_is_caught(self):
        base = {"implementer": envelope(verdict="BLOCKED", blocked="BLOCKED_APPROVAL", checks=[], evidence=None)}
        swap = {"implementer": envelope(verdict="BLOCKED", blocked="BLOCKED_CAPABILITY", checks=[], evidence=None)}
        row = self.compare(case(base=base, swap=swap))
        self.assertIn("VERDICT_DIFFERS", row["codes"])
        self.assertIn("blocked_reason", " ".join(row["detail"]))

    def test_checks_mismatch_is_caught(self):
        swap = {"implementer": envelope(checks=[
            {"id": "check-1", "command": "python3 -m unittest tests.test_parity", "exit_code": 0},
            {"id": "check-2", "command": "bin/romeo validate", "exit_code": 0}])}
        row = self.compare(case(swap=swap))
        self.assertIn("CHECKS_DIFFER", row["codes"])

    def test_invalid_envelope_is_caught(self):
        broken = envelope()
        del broken["gate_verdict"]
        row = self.compare(case(swap={"implementer": broken}))
        self.assertIn("SCHEMA_INVALID", row["codes"])

    def test_role_set_mismatch_is_caught(self):
        row = self.compare(case(base={"implementer": envelope(), "reviewer": reviewer_envelope()},
                                swap={"implementer": envelope()}))
        self.assertIn("ROLE_SET_DIFFERS", row["codes"])

    def test_nonzero_exit_codes_compare_as_pass_fail(self):
        chk = [{"id": "check-1", "command": "bin/romeo validate", "exit_code": 1}]
        chk2 = [{"id": "check-1", "command": "bin/romeo validate", "exit_code": 2}]
        row = self.compare(case(base={"implementer": envelope(verdict="FAIL", checks=chk)},
                                swap={"implementer": envelope(verdict="FAIL", checks=chk2)}))
        self.assertEqual(row["actual"], "same", "같은 실패에 런타임마다 다른 비0 코드를 낼 수 있다")
        zero = [{"id": "check-1", "command": "bin/romeo validate", "exit_code": 0}]
        row2 = self.compare(case(base={"implementer": envelope(verdict="FAIL", checks=chk)},
                                 swap={"implementer": envelope(verdict="FAIL", checks=zero)}))
        self.assertIn("CHECKS_DIFFER", row2["codes"], "성공과 실패는 같은 검사 결과가 아니다")

    def test_expected_differ_needs_declared_codes(self):
        c = case(expect="differ", expect_codes=["CHECKS_DIFFER"],
                 swap={"implementer": envelope(verdict="FAIL")})
        row = self.compare(c)
        self.assertEqual(row["actual"], "differ")
        self.assertFalse(row["ok"], "선언한 코드가 아니라 다른 이유로 어긋나면 통과가 아니다")


class TestEvidenceMissing(unittest.TestCase):
    """검사 0건·증거 0건의 PASS 쌍은 '동일'이 아니라 '판정 불가'다(K-51 · F06)."""

    def compare(self, c):
        return compare_case(c, RESULT_SCHEMA)

    def test_empty_pass_pair_is_undecidable_not_same(self):
        empty = envelope(checks=[], evidence=None)
        row = self.compare(case(base={"implementer": empty}, swap={"implementer": empty}))
        self.assertIn("EVIDENCE_MISSING", row["codes"])
        self.assertEqual(row["actual"], "undecidable", "양면이 똑같아도 뒷받침할 것이 없으면 동등성을 판정할 수 없다")
        self.assertFalse(row["ok"])

    def test_implementer_pass_without_checks_is_undecidable(self):
        no_checks = envelope(checks=[])
        row = self.compare(case(base={"implementer": no_checks}, swap={"implementer": no_checks}))
        self.assertIn("EVIDENCE_MISSING", row["codes"])
        self.assertIn("checks 0건", " ".join(row["detail"]))

    def test_reviewer_pass_without_any_anchor_is_undecidable(self):
        blind = reviewer_envelope(evidence=None)
        row = self.compare(case(base={"reviewer": blind}, swap={"reviewer": blind}))
        self.assertIn("EVIDENCE_MISSING", row["codes"])
        self.assertEqual(row["actual"], "undecidable")

    def test_reviewer_pass_citing_evidence_is_decidable(self):
        cited = reviewer_envelope()
        row = self.compare(case(base={"reviewer": cited}, swap={"reviewer": cited}))
        self.assertEqual(row["actual"], "same", "검토자는 검사를 실행하지 않아도 읽은 증거를 지목할 수 있다")

    def test_undecidable_pair_fails_the_checker_and_prints_why(self):
        empty = envelope(checks=[], evidence=None)
        rep = run_parity([case(base={"implementer": empty}, swap={"implementer": empty})])
        self.assertEqual(rep["undecidable"], 1)
        self.assertEqual(rep["checker_verdict"], "FAIL")
        self.assertIn("판정 불가", format_parity(rep))

    def test_schema_rejects_implementer_pass_without_evidence(self):
        self.assertEqual(validate(envelope(), RESULT_SCHEMA), [], "정상 봉투가 거부되면 스키마가 과하다")
        self.assertTrue(validate(envelope(checks=[], evidence=None), RESULT_SCHEMA),
                        "검사 0건·증거 0건의 PASS 가 스키마를 통과한다")
        self.assertTrue(validate(envelope(evidence=None), RESULT_SCHEMA), "증거 없는 PASS 가 통과한다")
        self.assertTrue(validate(envelope(checks=[]), RESULT_SCHEMA), "검사 0건 PASS 가 통과한다")

    def test_schema_still_accepts_blocked_and_failed_envelopes(self):
        self.assertEqual(validate(envelope(verdict="BLOCKED", blocked="BLOCKED_CAPABILITY",
                                           checks=[], evidence=None), RESULT_SCHEMA), [])
        self.assertEqual(validate(envelope(verdict="FAIL", checks=[], evidence=None), RESULT_SCHEMA), [])


class TestRoleContract(unittest.TestCase):
    """역할 계약에 없는 능력을 쓴 케이스를 잡는다(F19). 케이스를 고치는 것만으로는 다음에 또 들어온다."""

    def test_repo_contracts_load_and_declare_run_capability(self):
        roles = load_role_contracts()
        self.assertIn("implementer", roles)
        self.assertIn("reviewer", roles)
        self.assertIn("run-command", roles["implementer"]["capabilities"])
        self.assertNotIn("run-command", roles["reviewer"]["capabilities"],
                         "검토자에게 실행 능력이 생겼다 — 이 검사의 전제가 바뀐다")

    def test_reviewer_running_checks_is_a_contract_violation(self):
        ran = envelope(role="reviewer")  # checks 1건 — 계약에 없는 능력이다
        row = compare_case(case(base={"reviewer": ran}, swap={"reviewer": ran}), RESULT_SCHEMA)
        self.assertIn("ROLE_CONTRACT_VIOLATION", row["codes"])
        self.assertEqual(row["actual"], "undecidable", "양면이 똑같아도 계약 위반 위에서 동등성을 판정하지 않는다")
        self.assertIn("run-command", " ".join(row["detail"]))

    def test_repo_reviewer_case_does_not_run_checks(self):
        data = load_yaml(CASE_DIR / "pr-license-field-t1.yaml")
        for side in ("baseline", "swapped"):
            env = data[side]["results"]["reviewer"]
            self.assertEqual(env["checks"], [], f"{side}.reviewer 가 검사를 실행했다고 기록한다")
            self.assertTrue(env["evidence_ref"], f"{side}.reviewer 가 PASS 인데 지목한 증거가 없다")


class TestSourceKind(unittest.TestCase):
    """케이스의 출처를 강제한다 — 합성인지 관측인지 구분되지 않으면 게이트가 정직할 수 없다(D-b)."""

    def errs(self, c):
        return check_parity_cases([c]).get("<메모리>", [])

    def test_kind_must_be_in_enum(self):
        errs = self.errs(case(source={"kind": "guessed", "ref": "x", "date": "2026-08-28"}))
        self.assertTrue(any("source.kind" in e for e in errs), errs)

    def test_source_must_be_a_mapping(self):
        self.assertTrue(any("source" in e for e in self.errs(case(source="authored"))))

    def test_executed_case_cannot_be_planned(self):
        errs = self.errs(case(source={"kind": "planned", "ref": "x", "date": "2026-08-28"}))
        self.assertTrue(any("planned" in e for e in errs), errs)

    def test_pending_case_must_be_planned(self):
        pending = {"id": "pr-pending", "title": "자리표", "unit_id": UNIT_ID, "_path": "<메모리>",
                   "status": "pending", "expect": "same", "pending_reason": "미수행",
                   "baseline": {"results": {}}, "swapped": {"results": {}},
                   "source": dict(AUTHORED)}
        errs = self.errs(pending)
        self.assertTrue(any("planned" in e for e in errs), errs)

    def test_observed_case_must_point_at_the_observation(self):
        errs = self.errs(case(source={"kind": "observed", "ref": "", "date": "2026-08-28"}))
        self.assertTrue(any("observed" in e for e in errs), errs)

    def test_repo_cases_declare_a_known_kind(self):
        for c in load_parity_cases(CASE_DIR):
            kind = (c.get("source") or {}).get("kind")
            self.assertIn(kind, ("observed", "authored", "planned"), f"{c.get('id')}: {kind!r}")


class TestGateNeedsObservation(unittest.TestCase):
    """합성 데이터는 검사기를 검증할 뿐 게이트를 통과시키지 못한다(D-b · K-51)."""

    @classmethod
    def setUpClass(cls):
        cls.obs = ObservedRun()

    @classmethod
    def tearDownClass(cls):
        cls.obs.cleanup()

    def test_authored_only_is_undetermined(self):
        rep = run_parity([case()])
        self.assertEqual(rep["checker_verdict"], "PASS", "합성 케이스는 검사기가 도는지만 증명한다")
        self.assertEqual(rep["gate_verdict"], "UNDETERMINED")
        self.assertEqual(rep["verdict"], "UNDETERMINED")
        self.assertEqual((rep["observed"], rep["synthetic"]), (0, 1))

    def test_report_names_the_two_layers(self):
        text = format_parity(run_parity([case()]))
        self.assertIn("관측 0건", text)
        self.assertIn("합성 1건", text)
        self.assertIn("검사기 자기 검증: PASS", text)
        self.assertIn("핵심 동등성 게이트: 미판정", text)

    def test_one_observed_matching_case_decides_the_gate(self):
        rep = self.obs.report([case(), self.obs.case()])
        self.assertEqual((rep["observed"], rep["synthetic"]), (1, 1))
        self.assertEqual(rep["gate_verdict"], "PASS")
        self.assertIn("핵심 동등성 게이트: PASS", format_parity(rep))

    def test_observed_divergence_fails_the_gate(self):
        observed = self.obs.case(expect="differ", expect_codes=["VERDICT_DIFFERS"],
                                 swap=self.obs.write_result("run-b", gate_verdict="FAIL"),
                                 id="pr-observed-differ")
        # 합성 케이스를 함께 돌린다 — 검사기 자기 검증은 합성만으로 계산하므로, 합성이 없으면
        # "검사기 자체는 정상이다" 라고 말할 근거가 이 실행에 없다(해당 없음).
        rep = self.obs.report([case(), observed])
        self.assertEqual(rep["checker_verdict"], "PASS", "선언한 대로 어긋났으니 검사기 자체는 정상이다")
        self.assertEqual(rep["gate_verdict"], "FAIL", "관측된 불일치는 게이트 실패다")

    def test_observed_but_undecidable_does_not_pass_the_gate(self):
        blind = self.obs.write_result("run-b", checks=[], evidence_ref=None)
        rep = self.obs.report([self.obs.case(swap=blind)])
        self.assertEqual(rep["gate_verdict"], "FAIL", "증거 없는 관측은 게이트를 통과시키지 못한다")
        self.assertIn(ANCHOR_INVALID, rep["rows"][0]["codes"])

    def test_gate_pass_without_a_verified_checker_is_not_a_zero_exit(self):
        """검사기가 옳은지 확인하지 못한 실행은 게이트 통과를 주장할 수 없다(J08 · D-b)."""
        rep = self.obs.report([self.obs.case()])
        self.assertEqual(rep["gate_verdict"], "PASS")
        self.assertEqual(rep["checker_verdict"], NOT_APPLICABLE)
        self.assertIn("통과를 주장하지 않는다", format_parity(rep))


class TestObservedMustBeAnchored(unittest.TestCase):
    """게이트를 여는 한 단어가 검사되지 않으면 게이트는 아무것도 지키지 않는다(D-b·K-51).

    반례가 매 라운드 한 겹씩 깊어졌다 — `authored` 를 `observed` 로 바꾸기, 실재하는 아무 파일이나
    가리키기, 규약에 맞는 자리에 파일을 손으로 만들기. 마지막 겹을 닫는 것은 **작업 계약 재계산**이다:
    봉투를 파일로 받아 종료 검사와 같은 앵커 검사를 태우면, 위조하려면 올바른 계약을 만들어야 한다.
    아래 케이스들은 그 경로들이 통과가 아니라 **구조 오류**로 끝나는지 본다.
    """

    @classmethod
    def setUpClass(cls):
        cls.obs = ObservedRun()

    @classmethod
    def tearDownClass(cls):
        cls.obs.cleanup()

    def errs(self, c):
        return self.obs.check(c)

    def test_the_anchors_this_module_relies_on_are_real(self):
        # 이 테스트가 먼저 깨지면 관통 실행의 산출물이 만들어지지 않은 것이다.
        for run in ObservedRun.RUNS:
            self.assertTrue((self.obs.root / self.obs.evidence(run)).is_file())
            self.assertTrue((self.obs.root / WORK_DIR / self.obs.unit / "task"
                             / f"{run}-implementer.json").is_file())
        self.assertFalse((self.obs.root / WORK_DIR / FAKE_UNIT).exists())

    def test_fully_anchored_observed_case_has_no_structural_error(self):
        self.assertEqual(self.errs(self.obs.case()), [], "실제 실행이 남긴 관측 케이스는 통과해야 한다")

    def test_observed_ref_pointing_nowhere_is_a_structural_error(self):
        errs = self.errs(self.obs.case(source={"kind": "observed", "ref": "실행한적없음/아무문자열.md",
                                               "date": "2026-08-28"}))
        self.assertTrue(any("ref" in e and "실재 파일이 아니다" in e for e in errs), errs)

    def test_observed_ref_carrying_prose_is_a_structural_error(self):
        # 합성 케이스는 ref 에 설명을 붙여 왔다. 관측은 경로만 받는다 — 설명은 note 로 분리한다.
        ref = f"{self.obs.evidence('run-a')} (역할 교체 재실행)"
        errs = self.errs(self.obs.case(source={"kind": "observed", "ref": ref, "date": "2026-08-28"}))
        self.assertTrue(any("source.note" in e for e in errs), errs)

    def test_observed_ref_escaping_the_repo_is_a_structural_error(self):
        for ref in ("/etc/hosts", "../밖/관측.md"):
            errs = self.errs(self.obs.case(source={"kind": "observed", "ref": ref, "date": "2026-08-28"}))
            self.assertTrue(any("ref" in e for e in errs), f"{ref}: {errs}")

    def test_observed_unit_that_does_not_exist_is_a_structural_error(self):
        errs = self.errs(self.obs.case(unit_id=FAKE_UNIT))
        self.assertTrue(any(FAKE_UNIT in e and WORK_DIR in e for e in errs), errs)

    # ── 봉투는 파일로만 받는다 (4차 리뷰 J02) ────────────────────────────────────
    def test_inline_envelope_in_an_observed_case_is_a_structural_error(self):
        """게이트가 비교하는 값을 케이스 작성자가 그대로 타이핑할 수 있으면 게이트는 아무것도 지키지 않는다."""
        c = self.obs.case()
        c["baseline"] = {"results": {"implementer": envelope(unit=self.obs.unit)}}
        errs = self.errs(c)
        self.assertTrue(any("인라인" in e and "파일로만 받는다" in e for e in errs), errs)

    def test_result_file_outside_the_unit_is_a_structural_error(self):
        c = self.obs.case(base="README.md")
        self.assertTrue(any("results.implementer.file" in e and "밖이다" in e for e in self.errs(c)),
                        self.errs(c))

    def test_result_file_pointing_nowhere_is_a_structural_error(self):
        c = self.obs.case(base=f"{WORK_DIR}/{self.obs.unit}/result/없는실행-implementer.json")
        self.assertTrue(any("실재하지 않는다" in e for e in self.errs(c)), self.errs(c))

    def test_hand_written_result_file_in_the_right_place_is_a_structural_error(self):
        """3차 반례의 다음 겹 — 규약에 맞는 자리에 봉투를 손으로 만든다. 앵커 검사가 그대로 막는다."""
        rel_path = f"{WORK_DIR}/{self.obs.unit}/result/run-손으로쓴-implementer.json"
        forged = self.obs.envelope("run-a")
        forged["task_envelope_ref"] = {"path": f"{WORK_DIR}/{self.obs.unit}/task/손으로쓴계약.json",
                                       "sha256": "0" * 64}
        (self.obs.root / rel_path).write_text(json.dumps(forged, ensure_ascii=False), encoding="utf-8")
        errs = self.errs(self.obs.case(base=rel_path))
        self.assertTrue(any("TASK_ANCHORED" in e for e in errs), errs)

    def test_hand_written_task_contract_does_not_anchor_a_result_file(self):
        """계약 자체를 손으로 만들고 해시를 맞춰도 통과하지 않는다 — 앵커는 해시가 아니라 재계산이다(J01)."""
        task_rel = f"{WORK_DIR}/{self.obs.unit}/task/run-위조-implementer.json"
        (self.obs.root / task_rel).write_text(
            json.dumps({"unit_id": self.obs.unit, "role": "implementer",
                        "base_sha": self.obs.base_sha}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        import hashlib
        digest = hashlib.sha256((self.obs.root / task_rel).read_bytes()).hexdigest()
        rel_path = f"{WORK_DIR}/{self.obs.unit}/result/run-위조-implementer.json"
        forged = self.obs.envelope("run-a", task_envelope_ref={"path": task_rel, "sha256": digest})
        (self.obs.root / rel_path).write_text(json.dumps(forged, ensure_ascii=False), encoding="utf-8")
        errs = self.errs(self.obs.case(base=rel_path))
        self.assertTrue(any("TASK_ANCHORED" in e for e in errs), errs)

    # ── 증거 규약은 종료 검사와 같은 함수에서 온다 (J04) ────────────────────────
    def test_observed_evidence_ref_pointing_nowhere_is_a_structural_error(self):
        gone = f"{WORK_DIR}/{self.obs.unit}/evidence/run-없는실행.yaml"
        c = self.obs.case(swap=self.obs.write_result("run-b", name="run-gone", evidence_ref=gone))
        errs = self.errs(c)
        self.assertTrue(any("EVIDENCE_ANCHORED" in e and "실재하지 않는다" in e for e in errs), errs)

    def test_observed_evidence_ref_outside_the_unit_is_a_structural_error(self):
        # 실재하지만 그 작업 단위의 증거가 아닌 파일 — K-62 는 산출물이 작업 단위 안에 있기를 요구한다.
        c = self.obs.case(swap=self.obs.write_result("run-b", name="run-out", evidence_ref="README.md"))
        errs = self.errs(c)
        self.assertTrue(any("EVIDENCE_ANCHORED" in e and "밖이다" in e for e in errs), errs)

    def test_observed_case_without_any_evidence_is_a_structural_error(self):
        c = self.obs.case()
        c["baseline"] = {"results": {}}
        c["swapped"] = {"results": {}}
        errs = self.errs(c)
        self.assertTrue(any("관측물이 하나도 없다" in e for e in errs), errs)

    def test_malformed_face_does_not_crash_the_anchor_check(self):
        # 앵커 검사는 면의 타입 검사보다 먼저 돈다 — 깨진 케이스에서 트레이스백이 아니라 메시지가 나와야 한다.
        c = self.obs.case()
        c["baseline"] = "구조가 깨진 면"
        errs = self.errs(c)
        self.assertTrue(any("baseline" in e for e in errs), errs)

    def test_authored_case_is_not_required_to_be_anchored(self):
        # 합성 케이스는 지어낸 단위와 인라인 봉투를 써도 된다 — 게이트를 열지 못하기 때문이다.
        c = case(unit_id=FAKE_UNIT,
                 base={"implementer": envelope(unit=FAKE_UNIT, evidence=FAKE_EVIDENCE)},
                 swap={"implementer": envelope(unit=FAKE_UNIT, evidence=FAKE_EVIDENCE)})
        self.assertEqual(self.errs(c), [])


class TestCheckerCountsOnlySynthetic(unittest.TestCase):
    """검사기 자기 검증의 계산 대상과 설명 문장이 같은 집합을 가리켜야 한다.

    관측만 있는 디렉터리에서 '검사기 자기 검증: PASS — 합성 0건이 …' 이 나오면
    0건을 근거로 통과를 말하는 것이다.
    """

    @classmethod
    def setUpClass(cls):
        cls.obs = ObservedRun()

    @classmethod
    def tearDownClass(cls):
        cls.obs.cleanup()

    def test_observed_only_run_reports_not_applicable(self):
        rep = self.obs.report([self.obs.case()])
        self.assertEqual(rep["synthetic"], 0)
        self.assertEqual(rep["checker_verdict"], NOT_APPLICABLE)
        text = format_parity(rep)
        self.assertIn("검사기 자기 검증: 해당 없음", text)
        self.assertNotIn("검사기 자기 검증: PASS", text)

    def test_failing_synthetic_case_still_fails_the_checker(self):
        broken = {**case(swap={"implementer": envelope(verdict="FAIL")}), "id": "pr-broken"}
        rep = self.obs.report([broken, self.obs.case()])
        self.assertEqual(rep["checker_verdict"], "FAIL", "합성 케이스가 선언과 다르게 판정됐다")

    def test_observed_divergence_is_a_gate_failure_not_a_checker_failure(self):
        # 두 층이 섞이면 '검사기가 고장 났다' 와 '두 실행이 갈렸다' 를 읽는 사람이 구분할 수 없다.
        observed = self.obs.case(swap=self.obs.write_result("run-b", gate_verdict="FAIL"),
                                 id="pr-observed-differ")
        rep = self.obs.report([case(), observed])
        self.assertEqual(rep["checker_verdict"], "PASS")
        self.assertEqual(rep["gate_verdict"], "FAIL")


class TestPendingIsNotPass(unittest.TestCase):
    """미실행을 통과로 세면 게이트가 무의미해진다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def pending_case(self, cid="pr-pending"):
        return {"id": cid, "title": "실제 실행이 채울 자리표", "unit_id": UNIT_ID,
                "status": "pending", "expect": "same",
                "pending_reason": "두 런타임 교차 실행 미수행",
                "baseline": {"results": {}}, "swapped": {"results": {}},
                "source": {"kind": "planned", "ref": "tests", "date": "2026-08-28"}}

    def test_pending_case_is_not_counted_as_matched(self):
        cases = [self.pending_case(), {**case(), "id": "pr-executed"}]
        rep = run_parity(cases)
        self.assertEqual(rep["total"], 2)
        self.assertEqual(rep["executed"], 1)
        self.assertEqual(rep["pending"], 1)
        self.assertEqual(rep["matched"], 1, "미실행은 일치로 세지 않는다")
        self.assertEqual(rep["checker_verdict"], "PASS")
        self.assertEqual(rep["gate_verdict"], "UNDETERMINED", "합성 1건은 게이트를 판정하지 못한다")
        row = [r for r in rep["rows"] if r["id"] == "pr-pending"][0]
        self.assertFalse(row["ok"])
        self.assertIsNone(row["actual"])
        self.assertIn("미실행", format_parity(rep))

    def test_all_pending_does_not_pass(self):
        rep = run_parity([self.pending_case("pr-pending-a"), self.pending_case("pr-pending-b")])
        self.assertEqual(rep["matched"], 0)
        # 통과가 아니라는 것은 게이트가 말한다(UNDETERMINED → 종료 코드 1). 검사기 쪽은 판정 대상이
        # 0건이므로 PASS 도 FAIL 도 근거가 없다 — 0건을 근거로 한 주장을 인쇄하지 않는다.
        self.assertNotEqual(rep["checker_verdict"], "PASS", "미실행만 있는데 검사기가 통과를 주장하면 안 된다")
        self.assertEqual(rep["checker_verdict"], NOT_APPLICABLE)
        self.assertEqual(rep["gate_verdict"], "UNDETERMINED")
        text = format_parity(rep)
        self.assertIn("실행된 케이스가 없다", text)
        self.assertIn("검사기 자기 검증: 해당 없음", text)

    def test_empty_directory_does_not_pass(self):
        rep = run_parity([])
        self.assertNotEqual(rep["checker_verdict"], "PASS", "빈 fixture 를 통과로 처리하면 게이트가 무의미해진다")
        self.assertEqual(rep["checker_verdict"], NOT_APPLICABLE)
        self.assertEqual(rep["gate_verdict"], "UNDETERMINED")
        self.assertIn("실행된 케이스가 없다", format_parity(rep))

    def test_pending_case_with_results_is_structural_error(self):
        bad = self.pending_case()
        bad["baseline"] = {"results": {"implementer": envelope()}}
        bad["_path"] = "<메모리>"
        errs = check_parity_cases([bad])
        self.assertIn("<메모리>", errs)
        self.assertTrue(any("pending" in e for e in errs["<메모리>"]))

    def test_cli_reports_all_pending_as_failure(self):
        write_cases(self.dir, [self.pending_case()])
        code, out, _ = run_cli(["fixtures", "parity", str(self.dir)])
        self.assertEqual(code, 1)
        self.assertIn("미실행", out)


class TestStructuralChecks(unittest.TestCase):
    def test_missing_keys_and_bad_id_are_reported(self):
        bad = {"_path": "<메모리>", "id": "PR_Bad", "baseline": {}, "swapped": {}}
        errs = check_parity_cases([bad])["<메모리>"]
        self.assertTrue(any("title" in e for e in errs))
        self.assertTrue(any("패턴" in e for e in errs))

    def test_duplicate_id_is_reported(self):
        a, b = case(), case()
        a["_path"], b["_path"] = "<a>", "<b>"
        errs = check_parity_cases([a, b])
        self.assertTrue(any("중복 id" in e for e in errs["<a>"]))

    def test_role_key_and_unit_id_must_agree(self):
        bad = case(base={"reviewer": envelope(role="implementer")})
        errs = check_parity_cases([bad])["<메모리>"]
        self.assertTrue(any("role" in e for e in errs))

    def test_differ_case_must_declare_codes(self):
        errs = check_parity_cases([case(expect="differ")])["<메모리>"]
        self.assertTrue(any("expect_codes" in e for e in errs))


class TestEnvelopeClaimsAreComparedToEvidence(unittest.TestCase):
    """4차 리뷰 구멍 B — 결과 계약을 손으로 타이핑하되 **진짜** 작업 계약·**진짜** 증거를 가리키게 하면
    다섯 앵커 검사가 전부 통과하고 게이트가 교차 실행 0회로 열렸다. 실행된 적 없는 `pytest -q tests/` 를
    적어도 아무도 반박하지 않았다 — 앵커가 *파일이 진짜인지*만 보고 *봉투의 주장이 그 파일과 맞는지*는
    보지 않았기 때문이다.

    대조를 붙이는 자리는 **한 곳**이다(`close._evidence_anchor`). 종료 검사·`romeo envelope check`·
    동등성 판정이 모두 그 함수를 지나간다 — 규칙이 두 벌이 되면 느슨한 쪽이 게이트를 연다(K-63).
    """

    @classmethod
    def setUpClass(cls):
        cls.obs = ObservedRun()

    @classmethod
    def tearDownClass(cls):
        cls.obs.cleanup()

    def errs(self, c):
        return self.obs.check(c)

    def test_claiming_a_command_that_was_never_run_is_a_structural_error(self):
        """구멍 B 의 반례 그대로 — 진짜 증거를 가리키면서 실행된 적 없는 검사를 주장한다."""
        forged = self.obs.write_result("run-a", name="run-주장",
                                       checks=[{"id": "check-1", "command": "pytest -q tests/", "exit_code": 0},
                                               {"id": "check-2", "command": "npm run build", "exit_code": 0}])
        errs = self.errs(self.obs.case(base=forged))
        self.assertTrue(any("EVIDENCE_ANCHORED" in e and "실행 기록이 없다" in e for e in errs), errs)

    def test_claiming_a_different_exit_code_than_the_evidence_is_a_structural_error(self):
        """명령은 실제로 돌았지만 결과를 바꿔 적었다 — 종료 코드까지 대조해야 주장이 증거에 묶인다."""
        forged = self.obs.write_result("run-a", name="run-코드",
                                       checks=[{"id": "check-1", "command": "true", "exit_code": 1}])
        errs = self.errs(self.obs.case(base=forged))
        self.assertTrue(any("EVIDENCE_ANCHORED" in e and "종료 코드가 증거와 다르다" in e for e in errs), errs)

    def test_the_task_contract_must_sit_in_the_units_contract_place(self):
        """부수 사항 — 앵커가 바이트에 묶여 있어 진짜 계약을 어디로 복사해 두고 가리켜도 통과했다.
        증거 포인터와 같은 자리 규약(K-62)을 계약 포인터에도 건다."""
        outside = self.obs.root / "계약복사본.json"
        shutil.copy(self.obs.root / WORK_DIR / self.obs.unit / "task/run-a-implementer.json", outside)
        forged = self.obs.write_result("run-a", name="run-자리",
                                       task_envelope_ref={"path": "계약복사본.json",
                                                          "sha256": self.obs.task_sha["run-a"]})
        errs = self.errs(self.obs.case(base=forged))
        self.assertTrue(any("TASK_ANCHORED" in e and "밖이다" in e for e in errs), errs)

    def test_evidence_edited_to_match_the_claim_is_caught_by_the_raw_log(self):
        """또 한 겹 옆 — 봉투를 증거에 맞추는 대신 **증거를 봉투에 맞춰** 고친다.
        원시 로그가 그 체크아웃에 남아 있으면 명령 문자열이 어긋나는 것으로 드러난다."""
        epath = self.obs.root / self.obs.evidence("run-b")
        rec = load_yaml(epath)
        original = dump_yaml(rec)
        rec["commands"][0]["command"] = "pytest -q tests/"
        epath.write_text(dump_yaml(rec), encoding="utf-8")
        try:
            forged = self.obs.write_result("run-b", name="run-증거고침",
                                           checks=[{"id": "check-1", "command": "pytest -q tests/",
                                                    "exit_code": 0}])
            errs = self.errs(self.obs.case(swap=forged))
            self.assertTrue(any("EVIDENCE_ANCHORED" in e and "원시 로그" in e for e in errs), errs)
        finally:
            epath.write_text(original, encoding="utf-8")

    def test_an_honest_envelope_still_anchors(self):
        """대조를 붙여도 실제 실행이 남긴 봉투는 그대로 통과한다 — 앵커를 막히게 하지 않았다."""
        self.assertEqual(self.errs(self.obs.case()), [])

    def test_the_gate_does_not_open_on_typed_claims(self):
        """게이트 층에서 본다: 손으로 타이핑한 주장 하나로 관측 케이스가 서지 않는다."""
        forged = self.obs.write_result("run-a", name="run-게이트",
                                       checks=[{"id": "check-1", "command": "pytest -q tests/", "exit_code": 0}])
        rep = self.obs.report([self.obs.case(base=forged, id="pr-typed")])
        self.assertEqual(rep["gate_verdict"], "FAIL")
        self.assertIn(ANCHOR_INVALID, rep["rows"][0]["codes"])

    def test_the_report_says_the_gate_does_not_re_execute(self):
        """게이트가 통과할 때 무엇 위에 서 있는지 말한다 — 재실행 대조는 여기서 하지 않는다(K-51)."""
        text = format_parity(self.obs.report([case(), self.obs.case()]))
        self.assertIn("핵심 동등성 게이트: PASS", text)
        self.assertIn("여기서 명령을 다시 실행하지는 않는다", text)


class TestCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs = ObservedRun()

    @classmethod
    def tearDownClass(cls):
        cls.obs.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def parity(self, cases):
        """관측물이 있는 저장소를 --root 로 준다 — 케이스 파일이 어디에 있든 관측물은 그 저장소 안에 있다."""
        write_cases(self.dir, cases)
        return run_cli(["fixtures", "parity", str(self.dir), "--root", str(self.obs.root)])

    def test_repo_parity_exit_code_follows_the_gate(self):
        """종료 코드는 게이트를 따른다 — PASS 만 0, 미판정도 FAIL 도 1 이다(K-51).

        관측 0건(미판정)과 관측 있는 FAIL 은 **둘 다 1** 이지만 같은 뜻이 아니다.
        앞은 아무것도 증명하지 못한 것이고 뒤는 판정이 선 것이다 — 리포트 문장이 그것을 구분한다.
        """
        code, out, _ = run_cli(["fixtures", "parity", "--report"])
        self.assertIn(CANON_REASON, out)
        if "핵심 동등성 게이트: PASS" in out:
            self.assertEqual(code, 0, out)
        else:
            self.assertEqual(code, 1, out)
            self.assertTrue("핵심 동등성 게이트: 미판정" in out or "핵심 동등성 게이트: FAIL" in out,
                            "게이트 문장이 미판정도 FAIL 도 PASS 도 아니다 — 판정을 읽을 수 없다")

    def test_observed_with_a_verified_checker_exits_zero(self):
        code, out, err = self.parity([self.obs.case(), {**case(), "id": "pr-authored"}])
        self.assertEqual(code, 0, out + err)
        self.assertIn("핵심 동등성 게이트: PASS", out)
        self.assertIn("검사기 자기 검증: PASS", out)

    def test_observed_only_directory_does_not_exit_zero(self):
        """검사기 자기 검증이 '해당 없음' 인 실행은 아무것도 확인하지 않았다 — 0 을 내지 않는다(J08)."""
        code, out, err = self.parity([self.obs.case()])
        self.assertEqual(code, 1, out + err)
        self.assertIn("핵심 동등성 게이트: PASS", out)
        self.assertIn("검사기 자기 검증: 해당 없음", out)

    def test_renaming_authored_to_observed_does_not_open_the_gate(self):
        """저장소 케이스에서 한 단어만 바꿔 게이트를 여는 경로를 그대로 재현한다."""
        src = load_yaml(CASE_DIR / "pr-license-field-t1.yaml")
        forged = {k: v for k, v in src.items() if not k.startswith("_")}
        forged["id"] = "pr-forged-observed"
        forged["source"] = {"kind": "observed", "ref": "실행한적없음/아무문자열.md", "date": "2026-08-28"}
        code, out, err = self.parity([forged])
        self.assertEqual(code, 1, out)
        self.assertIn("PARITY_INVALID", err)
        self.assertNotIn("핵심 동등성 게이트: PASS", out)

    def test_observed_case_with_a_missing_evidence_file_exits_one(self):
        gone = f"{WORK_DIR}/{self.obs.unit}/evidence/run-없는실행.yaml"
        swap = self.obs.write_result("run-b", name="run-cli-gone", evidence_ref=gone)
        code, out, err = self.parity([self.obs.case(swap=swap, id="pr-observed-noevidence")])
        self.assertEqual(code, 1, out)
        self.assertIn("PARITY_INVALID", err)
        self.assertIn("EVIDENCE_ANCHORED", err)

    def test_hand_written_result_envelope_does_not_open_the_gate(self):
        """4차 반례 — 케이스는 규약대로 파일을 가리키는데 그 파일을 손으로 썼다."""
        rel_path = f"{WORK_DIR}/{self.obs.unit}/result/run-cli-forged-implementer.json"
        forged = self.obs.envelope("run-a")
        forged["task_envelope_ref"] = {"path": f"{WORK_DIR}/{self.obs.unit}/task/손으로쓴계약.json",
                                       "sha256": "0" * 64}
        (self.obs.root / rel_path).write_text(json.dumps(forged, ensure_ascii=False), encoding="utf-8")
        code, out, err = self.parity([self.obs.case(base=rel_path, id="pr-cli-forged")])
        self.assertEqual(code, 1, out)
        self.assertIn("PARITY_INVALID", err)
        self.assertIn("TASK_ANCHORED", err)
        self.assertNotIn("핵심 동등성 게이트: PASS", out)

    def test_drifted_directory_exits_one(self):
        swap = self.obs.write_result("run-b", name="run-cli-drift", gate_verdict="FAIL")
        code, out, _ = self.parity([self.obs.case(swap=swap, id="pr-drift")])
        self.assertEqual(code, 1)
        self.assertIn("VERDICT_DIFFERS", out)

    def test_structurally_invalid_directory_exits_one(self):
        write_cases(self.dir, [{"id": "pr-broken", "baseline": {}, "swapped": {}}])
        code, _, err = run_cli(["fixtures", "parity", str(self.dir)])
        self.assertEqual(code, 1)
        self.assertIn("PARITY_INVALID", err)

    def test_json_output_is_machine_readable(self):
        import json
        code, out, _ = run_cli(["fixtures", "parity", "--json"])
        self.assertIn(code, (0, 1))
        rep = json.loads(out)
        self.assertEqual(rep["schema"], "core/schemas/result-envelope.json")
        self.assertEqual(rep["checker_verdict"], "PASS")
        # 게이트 값은 저장소의 관측 건수에 달려 있다 — 값을 고정하지 않고 D-b 의 관계만 본다.
        if rep["observed"] == 0:
            self.assertEqual(rep["gate_verdict"], "UNDETERMINED")
        else:
            self.assertIn(rep["gate_verdict"], ("PASS", "FAIL"))
        self.assertEqual(rep["verdict"], rep["gate_verdict"])

    def test_fixtures_check_still_defaults_to_requests(self):
        code, out, _ = run_cli(["fixtures", "check"])
        self.assertEqual(code, 0, out)
        self.assertIn("PASS", out)


class TestProductPrecondition(unittest.TestCase):
    """검토자 면은 두 면이 같은 산출물을 봤을 때만 비교한다(D-73) — 메모리 케이스로 전제의 양쪽을 깨본다."""

    def compare(self, c):
        return compare_case(c, RESULT_SCHEMA)

    def pair(self, base_verdict, swap_verdict, base_product=PRODUCT, swap_product=PRODUCT, **kw):
        return case(base={"implementer": envelope(), "reviewer": reviewer_envelope(base_verdict)},
                    swap={"implementer": envelope(), "reviewer": reviewer_envelope(swap_verdict)},
                    base_product=base_product, swap_product=swap_product, **kw)

    def test_reviewer_drift_on_the_same_product_is_a_mismatch(self):
        """전제가 핑계가 되지 않는다 — 같은 것을 보고 갈렸으면 지금처럼 VERDICT_DIFFERS 다."""
        row = self.compare(self.pair("PASS", "FAIL"))
        self.assertIn("VERDICT_DIFFERS", row["codes"])
        self.assertEqual(row["actual"], "differ")
        self.assertEqual(row["incomparable"], [])
        self.assertEqual(row["compared"], ["implementer", "reviewer"])

    def test_reviewer_drift_on_different_products_is_incomparable_not_a_mismatch(self):
        row = self.compare(self.pair("PASS", "FAIL", swap_product=OTHER_PRODUCT))
        self.assertNotIn("VERDICT_DIFFERS", row["codes"], "다른 산출물에 대한 판정 차이는 런타임의 차이가 아니다")
        self.assertEqual(row["actual"], "same", "구현자 면은 비교됐고 같다")
        self.assertEqual(row["compared"], ["implementer"])
        self.assertEqual([(i["role"], i["code"]) for i in row["incomparable"]], [("reviewer", PRODUCT_DIFFERS)])
        self.assertIn(INCOMPARABLE_TEXT, row["incomparable"][0]["detail"])
        self.assertFalse(row["ok"], "합성 케이스가 비교 불가를 선언하지 않았으면 ok 가 아니다 — 검사기가 그것을 잡는지도 검증 대상이다")

    def test_declared_incomparable_face_makes_the_synthetic_case_ok(self):
        row = self.compare(self.pair("PASS", "FAIL", swap_product=OTHER_PRODUCT,
                                     expect_incomparable={"reviewer": PRODUCT_DIFFERS}))
        self.assertTrue(row["ok"])
        self.assertEqual(row["actual"], "same")

    def test_declaring_incomparable_that_did_not_happen_is_not_ok(self):
        row = self.compare(self.pair("PASS", "PASS", expect_incomparable={"reviewer": PRODUCT_DIFFERS}))
        self.assertEqual(row["actual"], "same")
        self.assertFalse(row["ok"], "선언한 비교 불가가 나오지 않았다 — 검사기가 빼지 말아야 할 면을 뺀 것이 아닌지 잡는다")

    def test_same_verdict_on_different_products_is_still_incomparable(self):
        """같은 판정도 증거가 아니다 — 다른 것을 보고 우연히 같았을 뿐이다."""
        row = self.compare(self.pair("PASS", "PASS", swap_product=OTHER_PRODUCT))
        self.assertEqual([i["code"] for i in row["incomparable"]], [PRODUCT_DIFFERS])
        self.assertEqual(row["compared"], ["implementer"])

    def test_implementer_face_ignores_the_product(self):
        """두 구현자가 다른 바이트를 만드는 것은 정상이다 — 구현자 면은 계약·checks·판정만 본다."""
        row = self.compare(case(base_product=PRODUCT, swap_product=OTHER_PRODUCT))
        self.assertEqual(row["actual"], "same")
        self.assertEqual(row["incomparable"], [])
        self.assertTrue(row["ok"])

    def test_reviewer_only_pair_on_different_products_compares_nothing(self):
        row = self.compare(case(base={"reviewer": reviewer_envelope()}, swap={"reviewer": reviewer_envelope()},
                                swap_product=OTHER_PRODUCT))
        self.assertEqual(row["actual"], "incomparable")
        self.assertEqual(row["compared"], [])
        self.assertFalse(row["ok"], "비교한 면이 없는 케이스는 어떤 기대로도 ok 가 되지 않는다")

    def test_unknown_product_is_incomparable_not_same(self):
        """구조 검사를 건너뛴 경로에서도 산출물을 모르는 검토자 면을 '같다' 로 세지 않는다."""
        row = self.compare(case(base={"reviewer": reviewer_envelope()}, swap={"reviewer": reviewer_envelope()},
                                base_product=None, swap_product=None))
        self.assertEqual([i["code"] for i in row["incomparable"]], [PRODUCT_UNKNOWN])
        self.assertEqual(row["actual"], "incomparable")

    def test_authored_case_with_reviewers_must_declare_products(self):
        errs = check_parity_cases([case(base={"reviewer": reviewer_envelope()},
                                        swap={"reviewer": reviewer_envelope()}, base_product=None)])
        self.assertTrue(any("baseline.product" in e for e in errs.get("<메모리>", [])), errs)

    def test_authored_case_without_reviewers_needs_no_product(self):
        self.assertEqual(check_parity_cases([case(base_product=None, swap_product=None)]), {})

    def test_expect_incomparable_must_name_roles_and_codes(self):
        errs = check_parity_cases([self.pair("PASS", "PASS", expect_incomparable={"janitor": "X"})])
        self.assertTrue(any("expect_incomparable" in e for e in errs.get("<메모리>", [])), errs)

    def test_repo_fixtures_cover_both_sides_of_the_precondition(self):
        """저장소 합성 케이스에 '산출물 다름 → 비교 불가' 와 '같은 산출물인데 갈림 → 불일치' 가 둘 다 있다."""
        rows = {r["id"]: r for r in run_parity(load_parity_cases(CASE_DIR))["rows"]}
        self.assertEqual([i["code"] for i in rows["pr-product-differs"]["incomparable"]], [PRODUCT_DIFFERS])
        self.assertTrue(rows["pr-product-differs"]["ok"])
        self.assertIn("VERDICT_DIFFERS", rows["pr-reviewer-drift"]["codes"])
        self.assertEqual(rows["pr-reviewer-drift"]["incomparable"], [])
        self.assertTrue(rows["pr-reviewer-drift"]["ok"])

    def test_report_prints_the_partial_row_and_the_excluded_face(self):
        rep = run_parity([self.pair("PASS", "FAIL", swap_product=OTHER_PRODUCT,
                                    expect_incomparable={"reviewer": PRODUCT_DIFFERS})])
        text = format_parity(rep)
        self.assertEqual(rep["incomparable_faces"], 1)
        self.assertEqual(rep["checker_verdict"], "PASS")
        self.assertIn("✓ 부분", text)
        self.assertIn(f"{INCOMPARABLE_TEXT} 면 1", text)
        self.assertIn(PRODUCT_DIFFERS, text)
        self.assertIn(f"implementer: {CANON_REASON}", text, "비교한 면과 뺀 면을 나란히 인쇄한다")


class TestObservedSameProduct(unittest.TestCase):
    """관측 케이스의 검토자 면 — 산출물이 같으면 지금처럼 비교하고, 식별은 케이스 파일이 아니라 증거에서 읽는다."""

    @classmethod
    def setUpClass(cls):
        cls.obs = ObservedRun(reviewer=True)

    @classmethod
    def tearDownClass(cls):
        cls.obs.cleanup()

    def test_evidence_of_both_runs_records_the_same_product(self):
        self.assertEqual(self.obs.product("run-a"), self.obs.product("run-b"), "같은 트리에서 기록했으니 같아야 한다")

    def test_reviewers_agreeing_on_the_same_product_compare_as_same(self):
        c = self.obs.case(base_review=self.obs.write_review("run-a"), swap_review=self.obs.write_review("run-b"))
        self.assertEqual(self.obs.check(c), [])
        rep = self.obs.report([c])
        row = rep["rows"][0]
        self.assertEqual(row["compared"], ["implementer", "reviewer"])
        self.assertEqual(row["incomparable"], [])
        self.assertEqual(rep["gate_verdict"], "PASS")

    def test_reviewers_disagreeing_on_the_same_product_fail_the_gate(self):
        """전제가 핑계가 되지 않는다 — 같은 산출물을 보고 갈린 검토자는 관측된 불일치다."""
        c = self.obs.case(base_review=self.obs.write_review("run-a"),
                          swap_review=self.obs.write_review("run-b", name="run-b-fail", gate_verdict="FAIL"),
                          id="pr-observed-review-drift")
        rep = self.obs.report([c])
        row = rep["rows"][0]
        self.assertIn("VERDICT_DIFFERS", row["codes"])
        self.assertIn("VERDICT_DIFFERS reviewer", " ".join(row["detail"]))
        self.assertEqual(row["incomparable"], [])
        self.assertEqual(rep["gate_verdict"], "FAIL")

    def test_observed_case_cannot_declare_its_product_inline(self):
        c = self.obs.case(base_review=self.obs.write_review("run-a"), swap_review=self.obs.write_review("run-b"))
        c["baseline"]["product"] = dict(PRODUCT)
        self.assertTrue(any("baseline.product" in e and "인라인" in e for e in self.obs.check(c)))

    def test_observed_case_cannot_expect_incomparable(self):
        c = self.obs.case(expect_incomparable={"reviewer": PRODUCT_DIFFERS})
        self.assertTrue(any("expect_incomparable" in e for e in self.obs.check(c)))


class TestObservedDivergedProduct(unittest.TestCase):
    """2026-08-29 관통의 모양 — 두 구현자가 다른 산출물을 만들었고 검토자 판정이 갈렸다.

    검토자 면은 증거의 산출물 식별로 비교 불가가 되어 판정에서 빠지고, 구현자 면만으로 게이트가 선다.
    빠졌다는 사실은 리포트·JSON 에 남는다.
    """

    @classmethod
    def setUpClass(cls):
        cls.obs = ObservedRun(reviewer=True)
        cls.obs.diverge("run-b")

    @classmethod
    def tearDownClass(cls):
        cls.obs.cleanup()

    def diverged_case(self, **kw):
        return self.obs.case(base_review=self.obs.write_review("run-a"),
                             swap_review=self.obs.write_review("run-b", name="run-b-fail", gate_verdict="FAIL",
                                                               findings=[{"summary": "표 구분선이 깨졌다"}]),
                             **kw)

    def test_evidence_records_different_products(self):
        self.assertNotEqual(self.obs.product("run-a"), self.obs.product("run-b"))

    def test_reviewer_face_is_excluded_and_the_gate_stands_on_the_implementer_face(self):
        c = self.diverged_case()
        self.assertEqual(self.obs.check(c), [], "케이스 파일에는 아무것도 더 적지 않았다 — 구조 오류가 없어야 한다")
        rep = self.obs.report([c])
        row = rep["rows"][0]
        self.assertEqual(row["compared"], ["implementer"])
        self.assertEqual([(i["role"], i["code"]) for i in row["incomparable"]], [("reviewer", PRODUCT_DIFFERS)])
        self.assertNotIn("VERDICT_DIFFERS", row["codes"])
        self.assertEqual(row["actual"], "same")
        self.assertTrue(row["ok"], "관측 케이스는 비교 불가를 기대로 선언할 수 없으므로 ok 에 넣지 않는다")
        self.assertEqual(rep["gate_verdict"], "PASS")
        self.assertEqual(rep["observed_incomparable_faces"], 1)

    def test_the_hashes_in_the_report_come_from_the_evidence(self):
        detail = self.obs.report([self.diverged_case()])["rows"][0]["incomparable"][0]["detail"]
        for run in self.obs.RUNS:
            head, tree = self.obs.product(run)
            self.assertIn(f"{head[:7]}+{tree[:12]}", detail)

    def test_the_report_says_the_pass_is_partial(self):
        text = format_parity(self.obs.report([self.diverged_case()]))
        self.assertIn("핵심 동등성 게이트: PASS", text)
        self.assertIn("✓ 부분", text)
        self.assertIn(f"{INCOMPARABLE_TEXT} — 관측 케이스의 1개 면을 판정에서 뺐다", text)
        self.assertIn("비교한 면으로만 섰다", text)

    def test_reviewer_only_observation_on_different_products_does_not_open_the_gate(self):
        c = self.diverged_case(implementer=False, id="pr-observed-review-only")
        rep = self.obs.report([c])
        self.assertEqual(rep["rows"][0]["actual"], "incomparable")
        self.assertEqual(rep["gate_verdict"], "UNDETERMINED", "비교한 면이 하나도 없는 관측은 판정 근거가 아니다")
        text = format_parity(rep)
        self.assertIn(f"관측 1건이 전부 {INCOMPARABLE_TEXT}", text)
        self.assertNotIn("핵심 동등성 게이트: PASS", text)

    def test_evidence_without_a_product_identity_is_a_structural_error(self):
        """손으로 만든 증거 — 증거 기록 명령이 항상 쓰는 head_sha·dirty_tree_hash 가 없다."""
        rec = load_yaml(self.obs.root / self.obs.evidence("run-b"))
        del rec["dirty_tree_hash"]
        edited = f"{WORK_DIR}/{self.obs.unit}/evidence/run-edited.yaml"
        (self.obs.root / edited).write_text(dump_yaml(rec), encoding="utf-8")
        swap = self.obs.write_review("run-b", name="run-b-edited", evidence_ref=edited)
        errs = self.obs.check(self.obs.case(base_review=self.obs.write_review("run-a"), swap_review=swap))
        self.assertTrue(any("산출물 식별" in e for e in errs), errs)

    def test_cli_exits_zero_and_prints_the_excluded_face(self):
        tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        try:
            write_cases(tmp.name, [self.diverged_case(), {**case(), "id": "pr-authored"}])
            code, out, err = run_cli(["fixtures", "parity", tmp.name, "--root", str(self.obs.root)])
        finally:
            tmp.cleanup()
        self.assertEqual(code, 0, out + err)
        self.assertIn("핵심 동등성 게이트: PASS", out)
        self.assertIn(PRODUCT_DIFFERS, out)
        self.assertIn("비교한 면으로만 섰다", out)


if __name__ == "__main__":
    unittest.main()
