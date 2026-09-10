"""`romeo metrics` — 네 지표의 정본·출력·출처·미집계·값·비차단을 대조한다.

AC-1~5(`docs/work/feat-20260909-metrics-four-counters-dyz2/spec.md` 확인란)를 그대로 겨눈다.

**정본을 이 파일에 옮겨 적지 않는다.** 지표 이름도 개수도 `romeo.metrics.METRICS` 에서 읽는다 —
사본을 두면 정본이 바뀌어도 이 검사는 옛 목록을 계속 덮고 통과한다(`tests/test_ci_trigger_coverage.py` 와 같은 이유).
그리고 **정본 자신도 대조 대상이다**: charter 원문(`docs/work/init-…-wr9m/charter.md` 의 M4 행)에서
네 이름을 뽑아 정본과 맞춘다. 이 축이 없으면 정본과 출력을 함께 고쳐 요청과 다른 지표를 세는 산출물이 통과한다.

**값의 정답은 계산식이 아니라 숫자로 적는다.** 아래 `TREE_A_ANSWERS`·`TREE_B_ANSWERS` 가 그것이다.
집계 코드의 식을 여기 옮겨 적으면 같은 오류가 양쪽에 생겨 대조가 아무것도 걸러내지 못한다(AC-4).
정답은 **검사가 스스로 만든 합성 트리**에 대한 것이라, 저장소 트리에 맞춘 상수를 넣은 산출물은 여기서 즉시 어긋난다.

이 검사는 **판별 검사**다 — 이 단위가 없으면 실패한다. 판별력은 아래 가상 상태로 재확인한다(AGENTS.core §11).

| 가상 상태 | 무엇이 바뀌나 | 기대 |
| --- | --- | --- |
| `romeo/metrics.py` 없음 · `metrics` 하위 명령 없음 | 이 단위 이전 상태 | import·명령 실패 |
| 정본에서 재분류율을 빼고 다른 지표를 등록 | 정본 쪽 | charter 대조 실패 |
| 재분류율을 「사건 없이 값을 주장하지 않는다」 표시에서 뺌 | 정본 쪽 | 빈 기록에서 `0%` 가 서고 AC-3 실패 |
| 저장소 트리에 맞춘 상수를 인쇄 | 구현 쪽 | 합성 트리 A 에서 값 불일치 |
| 원본 한 건만 보정하는 구현 | 구현 쪽 | 트리 B 의 네 값 중 보정하지 않은 것이 어긋난다 |
| 빈 `routing.history` 항목·`closed_at` 이 빈 T0 단위를 사건으로 셈 | 구현 쪽 | 트리 A 에서 재분류율이 숫자로 서고 T0 중앙값이 어긋난다 |
| 키만 있고 값이 빈 기록(`{"unit": null}` · `verdict: null`)을 사건으로 셈 | 구현 쪽 | 빈 기록 트리에서 그 지표가 숫자로 서고 미집계가 사라진다 |
| `needs_event` 지표 중 하나만 사건 0 을 보임 | 검사 쪽 | 빈 기록 트리 검사가 **정본에서 걸러 돌기** 때문에 나머지 지표에서 미집계를 요구한다 |
| gate 누락 1건에서 확인 입력을 기다림 | 구현 쪽 | AC-5 의 비대화형 실행이 시간 초과 |

**사건 0 을 보이는 입력은 파일이 없는 트리가 아니라 「기록할 자리는 있는데 아무도 쓰지 않은」 트리다**(`build_tree_blank`).
파일이 없으면 이 단위 이전 구현도 미집계를 인쇄하므로 그 통과는 판별력이 없다 — 반례는 빈 값이 아니라
**그럴듯한 거짓 값**이어야 한다(AGENTS.core §11).
"""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from romeo import HARNESS_ROOT
from romeo import metrics as M
from romeo.frontmatter import join as fm_join
from romeo.util import dump_yaml

CHARTER = HARNESS_ROOT / "docs/work/init-20260904-m4-doc-reuse-metrics-wr9m/charter.md"
ROMEO = HARNESS_ROOT / "bin/romeo"
#: 비대화형 실행의 상한. 사람의 입력을 기다리는 구현은 여기서 걸린다(AC-5).
RUN_TIMEOUT = 120

# --- 합성 트리 A 의 정답 (손으로 적었다 — 계산식이 아니라 숫자다) ------------------
#
# fixtures/requests 3건:
#   fx-syn-a  human_correction: null              → 검토 기록 아님
#   fx-syn-b  human_correction.verdict: corrected → 검토 기록 · 수정
#   fx-syn-c  human_correction.verdict: confirmed → 검토 기록 · 수정 아님
#             facets [payment] × intent write · gates [] → gate 힌트 미체크 1건
# docs/work 5건:
#   u-a T0  10:00:00 → 10:00:10  =  10초 · history []
#   u-b T0  11:00:00 → 11:00:30  =  30초 · history []
#   u-c T0  12:00:00 → 12:00:50  =  50초 · history []
#   u-d T1  (T0 아님)             · history [{}]   ← 빈 항목: 사건이 아니다
#   u-e T0  approved_at 만 있음   · history []     ← 자리가 빈 기록: 사건이 아니다
#
# 분류 수정률 = corrected 1 / verdict 기록 2 = 50.0%
# gate 누락   = 1건
# T0 처리 시간 = [10, 30, 50] 의 중앙값 = 30초   (u-e 는 closed_at 이 없어 표본이 아니다)
# 재분류율    = 채워진 routing.history 항목 0건 → 미집계  (u-d 의 `{}` 는 세지 않는다)
TREE_A_ANSWERS = {
    "classification-correction-rate": "50.0%",
    "gate-miss": "1건",
    "t0-lead-time": "중앙값 30초",
    "reclassification-rate": M.UNCOUNTED,
}
#: 트리 A 에서 각 지표가 읽어야 하는 파일 수. 검사가 독립적으로 세어 대조한다(AC-2).
TREE_A_SCANNED = {
    "classification-correction-rate": 3,
    "gate-miss": 3,
    "t0-lead-time": 5,
    "reclassification-rate": 5,
}

# --- 합성 트리 B 의 정답 (트리 A 의 원본을 네 자리에서 바꾼 것) --------------------
#
#   fx-syn-c 의 verdict  confirmed → corrected   ⇒ 분류 수정률 2/2
#   fx-syn-c 의 gates    []        → [payment]   ⇒ gate 누락 0건
#   u-b 의 closed_at     11:00:30  → 11:01:30    ⇒ T0 [10, 90, 50] 의 중앙값
#   u-a 의 routing.history 에 항목 1건 추가       ⇒ 재분류율 1/5
TREE_B_ANSWERS = {
    "classification-correction-rate": "100.0%",
    "gate-miss": "0건",
    "t0-lead-time": "중앙값 50초",
    "reclassification-rate": "20.0%",
}


# --- 합성 트리 BLANK 의 정답 (기록할 자리는 있는데 내용이 비어 있는 트리) ------------
#
# fixtures/requests 3건 — classification 은 트리 A 와 같고 human_correction 만 비어 있다:
#   fx-syn-a  human_correction: null                        → 검토 기록 아님
#   fx-syn-b  human_correction.verdict: null                 → 키만 있다 · 사건 아님
#   fx-syn-c  human_correction.verdict: "   " (공백)          → 키만 있다 · 사건 아님
#             facets [payment] × gates [] → gate 힌트 미체크 1건 (트리 A 와 같다)
# docs/work 5건 — 전부 unit T0 · closed_at 없음 · history 는 키만 있거나 비어 있다:
#   u-a  closed_at 없음 · history []
#   u-b  closed_at 없음 · history [{"unit": null}]                    ← 키만 있다
#   u-c  closed_at 없음 · history [{}]                                ← 빈 항목
#   u-d  closed_at 없음 · history [{"unit": "", "mode": "   "}]        ← 공백뿐이다
#   u-e  closed_at 없음 · history [{"policy_version": null, "changes": []}]  ← 값이 전부 비었다
#
# 분류 수정률 = verdict 가 채워진 기록 0건 → 미집계
# gate 누락   = 1건            (needs_event 가 거짓이라 0 도 값이다 — 여기서는 1건이 선다)
# T0 처리 시간 = 표본 0건 → 미집계
# 재분류율    = 채워진 항목 0건 → 미집계   (키만 있는 항목 4건을 세면 80.0% 가 선다)
TREE_BLANK_ANSWERS = {
    "classification-correction-rate": M.UNCOUNTED,
    "gate-miss": "1건",
    "t0-lead-time": M.UNCOUNTED,
    "reclassification-rate": M.UNCOUNTED,
}


# --- 합성 트리 만들기 -------------------------------------------------------------

def _fixture(fid, *, human_correction, facets, gates, intent="write"):
    return {
        "id": fid,
        "request_text": f"합성 요청 {fid} — 검사가 만든 트리다. 실제 세션 로그가 아니다.",
        "context": {"project": "synthetic", "kind": "code"},
        "classification": {
            "unit": "T0", "mode": "delivery", "intent": intent,
            "facets": list(facets), "gates": list(gates),
            "blast_radius": "small", "uncertainty": "low",
        },
        "expected": {"profile": "quick", "package": ["spec"]},
        "human_correction": human_correction,
        "source": {"kind": "authored", "ref": f"tests/test_metrics.py:{fid}", "date": "2026-09-10"},
    }


def _spec(uid, *, unit, approved_at, closed_at, history):
    fm = {
        "id": uid, "type": "spec", "title": f"합성 단위 {uid}", "unit": unit,
        "mode": "delivery", "intent": "write", "facets": ["tooling"], "gates": [],
        "profile": "quick", "blast_radius": "small", "uncertainty": "low",
        "status": "done" if closed_at else "active",
        "approved_at": approved_at, "approved_by": "synthetic",
        "closed_at": closed_at,
        "routing": {"policy_version": "0.1.0", "fired_rules": [], "history": history},
        "created": "2026-09-10", "updated": "2026-09-10",
    }
    return fm_join(fm, f"\n# 합성 단위 {uid}\n\n검사가 만든 트리다.\n")


def build_tree_a(root):
    """값이 미리 정해진 작은 합성 입력 트리. 위 `TREE_A_ANSWERS` 가 이 트리의 정답이다."""
    root = Path(root)
    fx = root / "fixtures" / "requests"
    fx.mkdir(parents=True, exist_ok=True)
    (fx / "fx-syn-a.yaml").write_text(dump_yaml(
        _fixture("fx-syn-a", human_correction=None, facets=["docs"], gates=[])), encoding="utf-8")
    (fx / "fx-syn-b.yaml").write_text(dump_yaml(
        _fixture("fx-syn-b", human_correction={
            "reviewed_at": "2026-09-10", "reviewed_by": "synthetic", "verdict": "corrected",
            "changes": [{"field": "classification.mode", "from": "discovery", "to": "delivery"}]},
            facets=["docs"], gates=[])), encoding="utf-8")
    (fx / "fx-syn-c.yaml").write_text(dump_yaml(
        _fixture("fx-syn-c", human_correction={
            "reviewed_at": "2026-09-10", "reviewed_by": "synthetic", "verdict": "confirmed",
            "changes": []},
            facets=["payment"], gates=[])), encoding="utf-8")

    work = root / "docs" / "work"
    for uid, unit, a, c, hist in (
        ("u-a", "T0", "2026-09-10T10:00:00+09:00", "2026-09-10T10:00:10+09:00", []),
        ("u-b", "T0", "2026-09-10T11:00:00+09:00", "2026-09-10T11:00:30+09:00", []),
        ("u-c", "T0", "2026-09-10T12:00:00+09:00", "2026-09-10T12:00:50+09:00", []),
        ("u-d", "T1", "2026-09-10T13:00:00+09:00", "2026-09-10T13:10:00+09:00", [{}]),
        ("u-e", "T0", "2026-09-10T14:00:00+09:00", None, []),
    ):
        d = work / uid
        d.mkdir(parents=True, exist_ok=True)
        (d / "spec.md").write_text(_spec(uid, unit=unit, approved_at=a, closed_at=c, history=hist),
                                   encoding="utf-8")
    return root


def build_tree_b(root):
    """트리 A 의 **원본을 네 자리에서 바꾼** 트리. `TREE_B_ANSWERS` 가 그 정답이다."""
    root = build_tree_a(root)
    fx = root / "fixtures" / "requests"
    c = _fixture("fx-syn-c", human_correction={
        "reviewed_at": "2026-09-10", "reviewed_by": "synthetic", "verdict": "corrected",
        "changes": [{"field": "classification.gates", "from": [], "to": ["payment"]}]},
        facets=["payment"], gates=["payment"])
    (fx / "fx-syn-c.yaml").write_text(dump_yaml(c), encoding="utf-8")

    work = root / "docs" / "work"
    (work / "u-b" / "spec.md").write_text(
        _spec("u-b", unit="T0", approved_at="2026-09-10T11:00:00+09:00",
              closed_at="2026-09-10T11:01:30+09:00", history=[]), encoding="utf-8")
    (work / "u-a" / "spec.md").write_text(
        _spec("u-a", unit="T0", approved_at="2026-09-10T10:00:00+09:00",
              closed_at="2026-09-10T10:00:10+09:00",
              history=[{"policy_version": "0.1.0", "unit": "T1", "mode": "delivery",
                        "reclassified_at": "2026-09-10T09:00:00+09:00"}]), encoding="utf-8")
    return root


def build_tree_blank(root):
    """**기록할 자리는 있는데 아무도 쓰지 않은** 트리. `TREE_BLANK_ANSWERS` 가 이 트리의 정답이다.

    `needs_event` 인 지표를 **한꺼번에** 사건 0 으로 만드는 입력이다 — 지표별로 다른 트리를 만들면
    지표가 늘 때마다 트리가 하나 더 필요해지고, 그 목록이 곧 정본의 사본이 된다.
    파일 수는 트리 A 와 같다(fixture 3 · 단위 5) — 파일이 없어서 사건이 0 인 것과
    **읽었는데 내용이 없어서** 0 인 것을 구별하기 위해서다.
    """
    root = Path(root)
    fx = root / "fixtures" / "requests"
    fx.mkdir(parents=True, exist_ok=True)
    (fx / "fx-syn-a.yaml").write_text(dump_yaml(
        _fixture("fx-syn-a", human_correction=None, facets=["docs"], gates=[])), encoding="utf-8")
    (fx / "fx-syn-b.yaml").write_text(dump_yaml(
        _fixture("fx-syn-b", human_correction={
            "reviewed_at": "2026-09-10", "reviewed_by": "synthetic", "verdict": None, "changes": []},
            facets=["docs"], gates=[])), encoding="utf-8")
    (fx / "fx-syn-c.yaml").write_text(dump_yaml(
        _fixture("fx-syn-c", human_correction={
            "reviewed_at": "2026-09-10", "reviewed_by": "synthetic", "verdict": "   ", "changes": []},
            facets=["payment"], gates=[])), encoding="utf-8")

    work = root / "docs" / "work"
    for uid, hist in (
        ("u-a", []),
        ("u-b", [{"unit": None}]),
        ("u-c", [{}]),
        ("u-d", [{"unit": "", "mode": "   "}]),
        ("u-e", [{"policy_version": None, "changes": []}]),
    ):
        d = work / uid
        d.mkdir(parents=True, exist_ok=True)
        (d / "spec.md").write_text(
            _spec(uid, unit="T0", approved_at="2026-09-10T10:00:00+09:00", closed_at=None,
                  history=hist), encoding="utf-8")
    return root


# --- 출력 읽기 --------------------------------------------------------------------

ROW = re.compile(r"^\|\s*(?P<name>[^|]+?)\s*\|\s*(?P<value>[^|]+?)\s*\|")


def table_rows(text):
    """표의 `| 지표 | 값 | …` 행만 {이름: 값} 으로. 머리글·구분선은 뺀다."""
    rows = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        m = ROW.match(line)
        if not m:
            continue
        name, value = m.group("name"), m.group("value")
        if name in ("지표", "---") or set(name) <= {"-", " "}:
            continue
        rows[name] = value
    return rows


def run_cli(root, *, stdin_closed=True):
    """`bin/romeo metrics --root <root>` 를 **표준 입력을 닫고** 별도 프로세스로 돌린다."""
    return subprocess.run(
        [sys.executable, str(ROMEO), "metrics", "--root", str(root)],
        stdin=subprocess.DEVNULL if stdin_closed else None,
        capture_output=True, text=True, timeout=RUN_TIMEOUT, cwd=str(HARNESS_ROOT))


def charter_metric_names():
    """charter M4 행이 이름 붙인 지표들. 이 파일에 사본을 두지 않기 위해 원문에서 뽑는다."""
    text = CHARTER.read_text(encoding="utf-8")
    m = re.search(r"`romeo metrics` 가 (?P<names>[^|]+?) (?P<count>\d+)개를 집계", text)
    assert m, f"charter 의 M4 행에서 지표 이름을 찾지 못했다: {CHARTER}"
    names = [n.strip() for n in m.group("names").split("·") if n.strip()]
    assert len(names) == int(m.group("count")), f"charter 가 말한 개수와 이름 수가 다르다: {names}"
    return names


class TreeCase(unittest.TestCase):
    """합성 트리를 만드는 검사들의 공통 자리."""

    def tree(self, build):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return build(Path(tmp.name))


class Ac1CanonAndRows(TreeCase):
    """AC-1 ① 출력 행의 집합 = 정본의 집합 · ② 정본 = charter 가 이름 붙인 네 지표."""

    def test_rows_match_canon_exactly(self):
        out = run_cli(HARNESS_ROOT)
        self.assertEqual(0, out.returncode, out.stderr)
        printed = set(table_rows(out.stdout))
        registered = {m.name for m in M.METRICS}
        self.assertEqual(registered, printed,
                         f"등록되지 않은 행 {printed - registered} · 빠진 행 {registered - printed}")

    def test_rows_match_canon_on_synthetic_tree(self):
        root = self.tree(build_tree_a)
        out = run_cli(root)
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertEqual({m.name for m in M.METRICS}, set(table_rows(out.stdout)))

    def test_canon_is_exactly_the_charter_four(self):
        self.assertEqual(set(charter_metric_names()), {m.name for m in M.METRICS})

    def test_canon_ids_are_unique(self):
        ids = [m.id for m in M.METRICS]
        self.assertEqual(len(ids), len(set(ids)), ids)


class Ac2Provenance(TreeCase):
    """AC-2 각 행마다 출처가 인쇄되고, 인쇄된 「읽은 파일 수」가 실재하는 파일 수와 같다."""

    def test_every_reading_names_where_it_read(self):
        for build in (build_tree_a, build_tree_b):
            root = self.tree(build)
            for r in M.collect(root):
                with self.subTest(tree=build.__name__, metric=r.metric.id):
                    self.assertTrue(r.metric.read_at.strip(), "읽는 자리가 비어 있다")
                    self.assertTrue(r.metric.scope_glob.strip(), "대상 범위가 비어 있다")
                    self.assertTrue(r.breakdown.strip(), "내역이 비어 있다")

    def test_scanned_count_matches_the_tree(self):
        root = self.tree(build_tree_a)
        for r in M.collect(root):
            with self.subTest(metric=r.metric.id):
                actual = len(list(root.glob(r.metric.scope_glob)))
                self.assertEqual(actual, r.scanned,
                                 f"{r.metric.scope_glob} 의 실재 {actual}건 ≠ 인쇄 {r.scanned}건")
                self.assertEqual(TREE_A_SCANNED[r.metric.id], r.scanned)

    def test_scanned_count_is_printed(self):
        root = self.tree(build_tree_a)
        out = run_cli(root)
        for r in M.collect(root):
            with self.subTest(metric=r.metric.id):
                self.assertIn(f"{r.scanned}건", out.stdout)

    def test_event_paths_exist_and_carry_what_was_read(self):
        for build in (build_tree_a, build_tree_b):
            root = self.tree(build)
            out = run_cli(root)
            for r in M.collect(root):
                with self.subTest(tree=build.__name__, metric=r.metric.id):
                    if r.events:
                        self.assertEqual(len(r.event_rows), r.events)
                        for path, read in r.event_rows:
                            self.assertTrue((root / path).exists(), f"인쇄된 경로가 트리에 없다: {path}")
                            self.assertTrue(read.strip(), "읽은 자리·값이 비어 있다")
                            self.assertIn(path, out.stdout)
                    else:
                        # 0건이면 읽은 범위(찾은 자리 · 읽은 파일 수)가 그 자리를 채운다.
                        self.assertIn(r.metric.scope_glob, out.stdout)
                        self.assertIn(r.metric.read_at, out.stdout)

    def test_repo_tree_prints_paths_that_exist(self):
        out = run_cli(HARNESS_ROOT)
        self.assertEqual(0, out.returncode, out.stderr)
        for r in M.collect(HARNESS_ROOT):
            for path, _read in r.event_rows:
                self.assertTrue((HARNESS_ROOT / path).exists(), path)


class Ac3Uncounted(TreeCase):
    """AC-3 표시 대상 지표는 사건 0 이면 미집계 + 사유, 사건 1건 이상이면 숫자."""

    #: 사유에 들어가면 안 되는 말 — 「기록이 없다」를 「일어난 적 없다」로 바꾸는 문장(관측이 아니다).
    FORBIDDEN = ("일어난 적", "발생한 적", "없었다", "한 번도")

    def test_reclassification_is_flagged(self):
        flagged = {m.id for m in M.METRICS if m.needs_event}
        self.assertIn("reclassification-rate", flagged,
                      "재분류율을 표시 대상에서 빼면 빈 기록에서 0% 가 선다")

    def test_zero_events_prints_uncounted_with_a_reason(self):
        root = self.tree(build_tree_a)
        out = run_cli(root)
        rows = table_rows(out.stdout)
        for r in M.collect(root):
            if r.metric.needs_event and r.events == 0:
                with self.subTest(metric=r.metric.id):
                    self.assertEqual(M.UNCOUNTED, rows[r.metric.name])
                    self.assertTrue(r.reason and r.reason.strip(), "사유가 비어 있다")
                    self.assertIn(r.reason, out.stdout)
        self.assertEqual(M.UNCOUNTED, rows["재분류율"])

    def test_one_or_more_events_prints_a_number(self):
        root = self.tree(build_tree_b)
        out = run_cli(root)
        rows = table_rows(out.stdout)
        for r in M.collect(root):
            if r.metric.needs_event:
                with self.subTest(metric=r.metric.id):
                    self.assertGreaterEqual(r.events, 1, "트리 B 는 네 지표 모두 사건이 있다")
                    self.assertNotEqual(M.UNCOUNTED, rows[r.metric.name])
                    self.assertRegex(rows[r.metric.name], r"\d")

    def test_reason_says_only_what_was_observed(self):
        root = self.tree(build_tree_a)
        for r in M.collect(root):
            if r.reason:
                with self.subTest(metric=r.metric.id):
                    for bad in self.FORBIDDEN:
                        self.assertNotIn(bad, r.reason, f"사유가 관측 밖을 주장한다: {r.reason}")
                    self.assertIn(str(r.scanned), r.reason)

    def test_blank_records_are_not_events(self):
        """빈 `routing.history` 항목과 `closed_at` 이 빈 T0 단위는 사건이 아니다."""
        root = self.tree(build_tree_a)
        by_id = {r.metric.id: r for r in M.collect(root)}
        self.assertEqual(0, by_id["reclassification-rate"].events, "빈 history 항목을 셌다")
        self.assertEqual(3, by_id["t0-lead-time"].events, "closed_at 이 빈 T0 단위를 표본으로 셌다")


class Ac3BothCasesForEveryFlaggedMetric(TreeCase):
    """AC-3 「두 경우를 각각 실행해 보인다」를 `needs_event` 인 **모든** 지표에서 본다.

    지표 목록을 여기 옮겨 적지 않고 **정본에서 `needs_event` 로 걸러 돌린다**(AC-1 과 같은 방식) —
    표시 대상이 늘어도 이 검사가 따라간다. 트리 A 하나로는 사건 0 을 보인 지표가 재분류율뿐이었고,
    나머지 둘은 트리 A 에 사건이 있어 그 경우에 들어가지 않았다.
    """

    def test_there_is_something_to_check(self):
        """걸러낸 목록이 비면 아래 두 검사는 아무것도 돌지 않고 통과한다 — 빈 검사를 막는다."""
        self.assertTrue([m for m in M.METRICS if m.needs_event],
                        "needs_event 인 지표가 하나도 없다 — AC-3 의 표시 대상이 사라졌다")

    def test_zero_event_input_prints_uncounted_for_every_flagged_metric(self):
        """사건 0 인 입력: 표시 대상 전부가 값 자리에 미집계와 사유를 인쇄한다."""
        root = self.tree(build_tree_blank)
        out = run_cli(root)
        self.assertEqual(0, out.returncode, out.stderr)
        rows, by_id = table_rows(out.stdout), {r.metric.id: r for r in M.collect(root)}
        covered = set()
        for m in [x for x in M.METRICS if x.needs_event]:
            with self.subTest(metric=m.id):
                r = by_id[m.id]
                self.assertEqual(0, r.events, f"내용이 빈 기록을 사건으로 셌다: {r.event_rows}")
                self.assertEqual(M.UNCOUNTED, rows[m.name])
                self.assertTrue(r.reason and r.reason.strip(), "미집계 사유가 비어 있다")
                self.assertIn(r.reason, out.stdout)
                covered.add(m.id)
        self.assertEqual({x.id for x in M.METRICS if x.needs_event}, covered)

    def test_one_or_more_event_input_prints_a_number_for_every_flagged_metric(self):
        """사건 1건 이상인 입력: 표시 대상 전부가 숫자를 인쇄한다."""
        root = self.tree(build_tree_b)
        out = run_cli(root)
        self.assertEqual(0, out.returncode, out.stderr)
        rows, by_id = table_rows(out.stdout), {r.metric.id: r for r in M.collect(root)}
        covered = set()
        for m in [x for x in M.METRICS if x.needs_event]:
            with self.subTest(metric=m.id):
                r = by_id[m.id]
                self.assertGreaterEqual(r.events, 1, "이 입력에 사건이 없으면 두 번째 경우를 보인 것이 아니다")
                self.assertNotEqual(M.UNCOUNTED, rows[m.name])
                self.assertRegex(rows[m.name], r"\d")
                covered.add(m.id)
        self.assertEqual({x.id for x in M.METRICS if x.needs_event}, covered)

    def test_blank_tree_reads_the_files_it_says_it_read(self):
        """사건 0 이 **파일이 없어서**가 아님을 보인다 — 파일 수는 트리 A 와 같다."""
        root = self.tree(build_tree_blank)
        for r in M.collect(root):
            with self.subTest(metric=r.metric.id):
                self.assertEqual(len(list(root.glob(r.metric.scope_glob))), r.scanned)
                self.assertEqual(TREE_A_SCANNED[r.metric.id], r.scanned)

    def test_key_only_records_are_not_events(self):
        """키는 있고 값이 비어 있는 기록을 세면 이 트리에서 숫자가 선다 — 그럴듯한 거짓 값이 반례다."""
        root = self.tree(build_tree_blank)
        rows = table_rows(run_cli(root).stdout)
        self.assertEqual(TREE_BLANK_ANSWERS, {m.id: rows[m.name] for m in M.METRICS})


class Ac4HandWrittenAnswers(TreeCase):
    """AC-4 ① 합성 트리의 값이 손으로 적어 둔 정답과 같다 · ② 원본을 바꾸면 두 번째 정답으로 바뀐다."""

    def _values(self, build):
        root = self.tree(build)
        out = run_cli(root)
        self.assertEqual(0, out.returncode, out.stderr)
        rows = table_rows(out.stdout)
        return {m.id: rows[m.name] for m in M.METRICS}

    def test_tree_a_matches_the_written_answers(self):
        self.assertEqual(TREE_A_ANSWERS, self._values(build_tree_a))

    def test_tree_b_matches_the_second_written_answers(self):
        self.assertEqual(TREE_B_ANSWERS, self._values(build_tree_b))

    def test_every_value_moved_between_the_two_trees(self):
        """네 값이 **전부** 달라진다 — 원본 한 건만 보정하는 구현은 여기서 남는다."""
        for mid, a in TREE_A_ANSWERS.items():
            self.assertNotEqual(a, TREE_B_ANSWERS[mid], mid)


class Ac5NeverBlocks(TreeCase):
    """AC-5 지표의 값을 이유로 실패하지도 멈추지도 않는다 — 다섯 입력에서 비대화형 exit 0."""

    def test_five_inputs_exit_zero_without_waiting(self):
        trees = {
            "미집계가 있는 트리 · gate 누락 1건": self.tree(build_tree_a),
            "숫자만 있는 트리 · gate 누락 0건": self.tree(build_tree_b),
            "저장소 트리": HARNESS_ROOT,
        }
        for label, root in trees.items():
            with self.subTest(input=label):
                out = run_cli(root)
                self.assertEqual(0, out.returncode, out.stdout + out.stderr)

    def test_the_two_trees_really_cover_both_gate_miss_cases(self):
        a = {r.metric.id: r for r in M.collect(self.tree(build_tree_a))}
        b = {r.metric.id: r for r in M.collect(self.tree(build_tree_b))}
        self.assertGreaterEqual(a["gate-miss"].events, 1)
        self.assertEqual(0, b["gate-miss"].events)
        self.assertEqual(M.UNCOUNTED, a["reclassification-rate"].value_text)
        self.assertNotEqual(M.UNCOUNTED, b["reclassification-rate"].value_text)


class CommandIsRegistered(unittest.TestCase):
    """`bin/romeo metrics` 가 실재하고, CI 가 그것을 실제로 돌린다."""

    def test_help_lists_metrics(self):
        out = subprocess.run([sys.executable, str(ROMEO), "--help"], stdin=subprocess.DEVNULL,
                             capture_output=True, text=True, timeout=RUN_TIMEOUT)
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertIn("metrics", out.stdout)

    def test_ci_runs_the_command(self):
        wf = (HARNESS_ROOT / ".github/workflows/harness.yml").read_text(encoding="utf-8")
        self.assertIn("bin/romeo metrics", wf)


if __name__ == "__main__":
    unittest.main()
