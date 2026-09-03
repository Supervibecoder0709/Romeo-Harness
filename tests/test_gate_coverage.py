"""hard gate 8 의 fixture 커버리지와 게이트 id 유효성을 **정책표에서 읽어** 대조한다.

두 가지를 본다.

1. **커버리지** — `core/policy/classification.yaml` 의 `hard_gates[].id` 각각에 대해
   `fixtures/requests/` 에 그 게이트를 확정한 fixture 가 1건 이상 있는가.
2. **id 유효성** — 모든 fixture 의 `classification.gates` 값이 그 id 집합 안에 있는가.

이 검사는 **판별 검사**다 — 이 단위(fixture 5건)가 없으면 실패한다. 판별력은 아래 네 가상 상태로
매번 재확인한다. 통과만 보이는 검사는 빈 검사이고, 실패만 보이는 검사는 통과 불가능한 검사다(AGENTS.core §11).

| 가상 상태 | 무엇이 바뀌나 | 기대 |
| --- | --- | --- |
| fixture 5건 제거 | fixture 쪽 | 커버리지 실패 |
| 정책표 게이트 id 개명 | 정책표 쪽 | 커버리지 실패 |
| fixture 에 정책표 밖 id 주입 | fixture 쪽 | id 유효성 실패 |
| **게이트 id 를 하드코딩한 구현 × 개명된 정책표** | 구현 쪽 | **통과해 버린다** (반례) |

마지막 줄이 이 검사의 핵심이다. 빈 값이 아니라 **그럴듯한 거짓 구현**에서 갈리는 것을 보인다 —
id 를 하드코딩한 구현은 개명된 정책표에서도 초록불이므로 「정책표에서 읽는가」 를 확인하지 못한다.
"""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from romeo import HARNESS_ROOT
from romeo.util import dump_yaml, load_yaml

POLICY = HARNESS_ROOT / "core/policy/classification.yaml"
FIXTURES = HARNESS_ROOT / "fixtures/requests"

#: 이 단위가 추가한 5건. 「이 단위 이전 상태」 를 만들 때 이것만 뺀다.
UNIT_FIXTURES = (
    "fx-payment-metric-schema.yaml",
    "fx-landing-consent-copy.yaml",
    "fx-ops-test-data-purge.yaml",
    "fx-public-kpi-endpoint.yaml",
    "fx-free-plan-retention-cut.yaml",
)

#: **반례 전용**. 정책표를 읽지 않고 id 를 박아 넣은 구현이 어떻게 생겼는지를 그대로 둔 것이다.
#: 실제 판정에는 쓰지 않는다 — 쓰면 이 파일이 곧 그 반례가 된다.
HARDCODED_GATE_IDS = (
    "payment", "privacy-security", "legal", "ops-data-deletion",
    "migration", "public-api", "irreversible-policy", "availability",
)


def gate_ids_from_policy(policy_path):
    """정책표의 `hard_gates[].id` 를 선언 순서대로 돌려준다."""
    data = load_yaml(Path(policy_path)) or {}
    return [g["id"] for g in data.get("hard_gates") or []]


def fixture_gates(fixture_dir):
    """{fixture 파일명: 그 fixture 가 확정한 게이트 id 목록}."""
    out = {}
    for path in sorted(Path(fixture_dir).glob("*.yaml")):
        data = load_yaml(path) or {}
        out[path.name] = list((data.get("classification") or {}).get("gates") or [])
    return out


def uncovered_gates(gate_ids, gates_by_fixture):
    """fixture 가 한 건도 없는 게이트 id."""
    covered = {g for gates in gates_by_fixture.values() for g in gates}
    return [gid for gid in gate_ids if gid not in covered]


def unknown_gate_uses(gate_ids, gates_by_fixture):
    """정책표 id 집합 밖의 게이트를 쓴 (fixture, id) 목록."""
    known = set(gate_ids)
    return sorted((name, g) for name, gates in gates_by_fixture.items()
                  for g in gates if g not in known)


class GateCoverageTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _copy_fixtures(self, drop=()):
        dst = self.root / "requests"
        shutil.copytree(FIXTURES, dst)
        for name in drop:
            target = dst / name
            self.assertTrue(target.is_file(), f"{name} 이 없다 — 파일명이 바뀌면 이 반례가 조용히 죽는다")
            target.unlink()
        return dst

    def _copy_policy_with_renamed_gate(self, index=0):
        """정책표 사본에서 게이트 id 하나를 개명한다. (경로, 원래 id, 새 id)."""
        dst = self.root / "classification.yaml"
        data = load_yaml(POLICY)
        original = data["hard_gates"][index]["id"]
        renamed = original + "-renamed"
        data["hard_gates"][index]["id"] = renamed
        dst.write_text(dump_yaml(data), encoding="utf-8")
        return dst, original, renamed


class TestGateCoverage(GateCoverageTestBase):
    """실제 상태 — 8개 각각에 fixture 가 1건 이상 있고, 쓰인 게이트 id 가 전부 정책표 안에 있다."""

    def test_policy_declares_eight_hard_gates(self):
        ids = gate_ids_from_policy(POLICY)
        self.assertEqual(len(ids), len(set(ids)), f"정책표에 중복 게이트 id 가 있다: {ids}")
        self.assertEqual(len(ids), 8, f"hard gate 는 8개다 — 지금 {len(ids)}개: {ids}")

    def test_every_hard_gate_has_at_least_one_fixture(self):
        ids = gate_ids_from_policy(POLICY)
        missing = uncovered_gates(ids, fixture_gates(FIXTURES))
        self.assertEqual(missing, [], f"fixture 가 0건인 게이트: {missing}")

    def test_no_fixture_uses_a_gate_outside_the_policy_table(self):
        ids = gate_ids_from_policy(POLICY)
        unknown = unknown_gate_uses(ids, fixture_gates(FIXTURES))
        self.assertEqual(unknown, [], f"정책표에 없는 게이트 id: {unknown}")


class TestGateCoverageDiscriminates(GateCoverageTestBase):
    """가상 상태 네 가지 — 이 검사가 무엇을 가르는지 매번 실행으로 보인다(AGENTS.core §11)."""

    # ── ① fixture 5건을 뺀 상태(= 이 단위 이전)에서 커버리지가 실패한다 ──────
    def test_without_this_units_fixtures_the_coverage_check_fails(self):
        ids = gate_ids_from_policy(POLICY)
        before = self._copy_fixtures(drop=UNIT_FIXTURES)
        missing = uncovered_gates(ids, fixture_gates(before))
        self.assertEqual(
            sorted(missing),
            ["irreversible-policy", "legal", "ops-data-deletion", "payment", "public-api"],
            "이 단위 이전 상태에서 비어 있어야 할 게이트 5개가 그대로 나와야 한다")

    # ── ② 같은 검사가 지금 상태에서는 통과한다 (①의 반대쪽) ──────────────────
    def test_with_this_units_fixtures_the_coverage_check_passes(self):
        ids = gate_ids_from_policy(POLICY)
        after = self._copy_fixtures()
        self.assertEqual(uncovered_gates(ids, fixture_gates(after)), [])

    # ── ③ 정책표의 게이트 id 를 개명하면 커버리지가 실패한다 ─────────────────
    def test_renaming_a_gate_in_the_policy_table_fails_the_coverage_check(self):
        policy, original, renamed = self._copy_policy_with_renamed_gate()
        ids = gate_ids_from_policy(policy)
        self.assertIn(renamed, ids)
        self.assertNotIn(original, ids)
        missing = uncovered_gates(ids, fixture_gates(FIXTURES))
        self.assertEqual(missing, [renamed],
                         "정책표에서 읽는 구현은 개명된 id 를 커버리지 0 으로 본다")

    # ── ④ 반례: id 를 하드코딩한 구현은 개명된 정책표에서도 통과해 버린다 ────
    def test_a_hardcoded_implementation_passes_the_renamed_policy_table(self):
        """빈 값이 아니라 **그럴듯한 거짓 구현**에서 갈리는 것을 보인다.

        같은 가상 상태(개명된 정책표)를 두 구현에 돌린다. 정책표를 읽는 구현은 실패하고,
        id 를 박아 넣은 구현은 통과한다 — 그 차이가 AC-3 이 요구하는 판별력이다."""
        policy, _original, renamed = self._copy_policy_with_renamed_gate()
        gates = fixture_gates(FIXTURES)

        reads_policy = uncovered_gates(gate_ids_from_policy(policy), gates)
        hardcoded = uncovered_gates(HARDCODED_GATE_IDS, gates)

        self.assertEqual(reads_policy, [renamed], "정책표를 읽는 구현은 이 상태에서 실패한다")
        self.assertEqual(hardcoded, [], "id 를 하드코딩한 구현은 같은 상태에서 통과해 버린다 — 그래서 반례다")

    # ── ⑤ 정책표 밖 게이트 id 를 fixture 하나에 넣으면 id 유효성이 실패한다 ──
    def test_injecting_an_unknown_gate_into_a_fixture_fails_the_validity_check(self):
        ids = gate_ids_from_policy(POLICY)
        directory = self._copy_fixtures()
        target = directory / UNIT_FIXTURES[0]
        data = load_yaml(target)
        data["classification"]["gates"] = list(data["classification"]["gates"]) + ["not-a-real-gate"]
        target.write_text(dump_yaml(data), encoding="utf-8")

        unknown = unknown_gate_uses(ids, fixture_gates(directory))
        self.assertEqual(unknown, [(UNIT_FIXTURES[0], "not-a-real-gate")])
        self.assertEqual(unknown_gate_uses(ids, fixture_gates(FIXTURES)), [],
                         "원본은 같은 검사에서 통과한다 — 한쪽만 보인 검사는 승인 대상이 아니다")


if __name__ == "__main__":
    unittest.main()
