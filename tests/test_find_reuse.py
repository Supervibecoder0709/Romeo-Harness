"""M4 첫 마일스톤 — 「재사용 검색」 요구가 실제로 집행되는가(§11).

`/plan` 절차 1단계는 재사용 검색을 **요구**하지만, 그것을 수행하는 명령도 수행 여부를 보는
자리도 없었다 — 요구만 있고 집행이 없는 모양이다. 이 검사가 셋을 같은 자리에서 본다.

| # | 어느 사건에서 보는가 | 어느 문서를 읽는가 | 무엇이 참이어야 충족인가 |
| --- | --- | --- | --- |
| AC-1 | `romeo find` 실행 | `docs/work/`·`docs/current/` 의 단위 문서 | 겹치는 단위의 id 가 나오고, 없으면 빈 결과 + exit 0 |
| AC-2 | 카드 렌더링 | 제안(`reuse_hits` 는 비어 있다) | 카드 본문에 그 단위의 id 가 **글자 그대로** 있다 |
| AC-3 | 30줄 예산 축소 | 같은 카드 | 축소가 실제로 발동한 뒤에도 그 id 가 남는다 |
| AC-4 | 카드 렌더링 | 겹치지 않는 제안 | 어떤 unit id 도 나타나지 않는다 (거짓 양성 0) |
| AC-5 | 절차 문서 로드 | `core/workflows/plan/SKILL.md` 의 **1단계 본문만** | 거기 적힌 이름으로 **실제 검색이 돌아** 기존 단위가 나온다 |

**반례는 빈 값이 아니라 그럴듯한 거짓 값이다.** 여기서 그것은 「재사용 검색을 빠뜨린 채
`reuse_hits: []` 로 제출된, 형태는 멀쩡한 제안」이다 — 고치기 전에는 그 제안이 카드에 아무것도
인쇄하지 않았고 사람은 중복을 보지 못한 채 확정했다. AC-2·AC-3 이 겨누는 것이 그 상태다.

AC-5 가 「이름이 CLI 에 있는가」로 만족되지 않는 이유도 같다 — 승인 전 프로브에서, 문서 앞부분을
함께 읽으면 역할 분담 표의 `romeo route` 가 잡혀 **이 단위 없이도 통과**했다. 그래서 읽는 자리를
1단계 본문으로 좁히고, 뽑은 이름으로 검색을 **실제로 돌려** 기존 단위가 나오는 것까지 본다.

**AC-4 만 회귀 방지다** — 구현 전에도 참이므로(카드가 아무 후보도 인쇄하지 않으니) 판별력이 없다.
나머지는 판별 검사이고, 이 단위가 없으면 실패한다.
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from romeo.card import render_card
from romeo.find import search_units
from romeo.policy import load_policy, load_project_state, route

ROOT = Path(__file__).resolve().parents[1]

#: 이 저장소에 실제로 있는 단위. 검색이 무엇을 찾아야 하는지의 기준점이다.
EXISTING_UNIT = "feat-20260904-gate-fixture-coverage-q3wy"
EXISTING_SLUG = "gate-fixture-coverage"
#: 디렉터리 이름에는 없고 **제목에만** 있는 낱말 — 제목까지 색인하는지 가른다.
TITLE_ONLY_TERM = "재실행"
TITLE_ONLY_UNIT = "chg-20260902-rerun-timeout-headroom-8dse"
#: 어느 단위와도 겹치지 않는 낱말.
NO_MATCH_TERM = "zzz-nonexistent-term-qqq"
UNIT_ID_RE = re.compile(r"\b(chg|feat|init)-\d{8}-")


def _romeo(*argv):
    return subprocess.run([sys.executable, str(ROOT / "bin" / "romeo"), *argv],
                          capture_output=True, text=True, cwd=str(ROOT))


def _proposal(text, slug, title, reuse_hits=None, extra_lists=False):
    """합성 제안. `reuse_hits` 는 기본이 **빈 목록**이다 — 그것이 반례의 모양이다."""
    p = {
        "request": {"text": text, "project": "Romeo-Harness", "context": None},
        "facts": [], "assumptions": [], "unknowns": [],
        "reuse_hits": list(reuse_hits or []),
        "candidate": {
            "unit": "T2", "mode": "delivery", "intent": "write",
            "facets": ["tooling", "docs"], "gates": [],
            "blast_radius": "medium", "uncertainty": "medium",
            "slug": slug, "title": title, "project_kind": "harness",
        },
        "factors": {k: {"level": "medium", "note": "합성"} for k in
                    ("scope", "uncertainty", "impact", "reversibility", "coordination")},
        "gate_checklist": [],
    }
    if extra_lists:
        # 예산 축소를 실제로 발동시키는 자리. 이 문자열이 카드에서 사라지는 것이
        # 「축소가 돌았다」 의 증거다 — 축소가 돌지 않으면 AC-3 은 아무것도 확인하지 못한다.
        p["facts"] = [f"TRIM-CANARY-사실-{i}" for i in range(1, 4)]
        p["assumptions"] = [f"TRIM-CANARY-가정-{i}" for i in range(1, 3)]
        p["unknowns"] = [f"TRIM-CANARY-미확인-{i}" for i in range(1, 3)]
        p["needs_decision"] = [f"TRIM-CANARY-결정-{i}" for i in range(1, 3)]
    return p


def _limit():
    return load_policy()["packages"]["budgets"]["card_max_lines"]


def _card(proposal):
    out = route(proposal["candidate"], project_state=load_project_state(ROOT))
    return render_card(proposal, out, root=ROOT, harness_root=ROOT)


class TestFindCommand(unittest.TestCase):
    """AC-1 — 명령이 기존 단위를 찾고, 없음을 오류로 만들지 않는다."""

    def test_finds_the_existing_unit_by_slug(self):
        r = _romeo("find", EXISTING_SLUG, "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(EXISTING_UNIT, r.stdout)

    def test_finds_a_unit_whose_only_overlap_is_in_the_title(self):
        """제목까지 색인하지 않으면 여기서 갈린다 — 이 낱말은 디렉터리 이름에 없다."""
        self.assertNotIn(TITLE_ONLY_TERM, TITLE_ONLY_UNIT)
        ids = [h["id"] for h in search_units(ROOT, [TITLE_ONLY_TERM])]
        self.assertIn(TITLE_ONLY_UNIT, ids)

    def test_no_match_is_an_empty_result_not_an_error(self):
        r = _romeo("find", NO_MATCH_TERM, "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout).get("hits"), [])

    def test_result_rows_carry_the_promised_keys(self):
        hits = search_units(ROOT, [EXISTING_SLUG])
        self.assertTrue(hits)
        for h in hits:
            self.assertLessEqual({"id", "title", "path", "score"}, set(h))
            self.assertGreater(h["score"], 0)

    def test_text_output_also_names_the_unit(self):
        r = _romeo("find", EXISTING_SLUG)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(EXISTING_UNIT, r.stdout)


class TestCardSearchesForItself(unittest.TestCase):
    """AC-2·AC-3 — 제안이 빠뜨려도 카드가 스스로 찾고, 축소가 그것을 지우지 않는다."""

    OVERLAP = ("hard gate 8 커버리지를 fixture 로 채운다", EXISTING_SLUG, "게이트 fixture 커버리지")

    def test_overlap_is_printed_though_reuse_hits_is_empty(self):
        prop = _proposal(*self.OVERLAP)
        self.assertEqual(prop["reuse_hits"], [], "반례는 빈 reuse_hits 를 단 그럴듯한 제안이다")
        self.assertIn(EXISTING_UNIT, _card(prop),
                      "제안이 재사용 검색을 빠뜨려도 카드가 겹치는 단위를 인쇄해야 한다")

    def test_the_line_survives_the_list_trim(self):
        """축소 1단계 — 사실·가정·미확인·결정 목록을 지운다."""
        card = _card(_proposal(*self.OVERLAP, extra_lists=True))
        self.assertLessEqual(len(card.splitlines()), _limit())
        self.assertNotIn("TRIM-CANARY", card, "축소가 발동하지 않았다면 이 검사는 아무것도 확인하지 않는다")
        self.assertIn(EXISTING_UNIT, card, "축소가 재사용 후보 줄을 지워서는 안 된다")

    def test_the_line_survives_when_the_kept_lines_alone_overflow(self):
        """축소 2단계 — 목록을 다 지워도 남는 줄이 예산을 넘을 때.

        여기가 이 요구의 진짜 자리다. 고치기 전 구현은 남은 줄을 **뒤에서부터** 잘랐고,
        재사용 후보와 확정은 카드의 맨 뒤에 있다 — 인쇄는 하면서 사람이 볼 때는 없는 상태다.
        능력 줄은 한 능력에 한 줄이므로(카드가 실제로 길어지는 경로) 개수만 합성해 발동시킨다.
        """
        prop = _proposal(*self.OVERLAP)
        out = route(prop["candidate"], project_state=load_project_state(ROOT))
        out = dict(out, capabilities=[f"synthetic.cap-{i}" for i in range(40)])
        lines = render_card(prop, out, root=ROOT, harness_root=ROOT).splitlines()
        self.assertEqual(len(lines), _limit(), "합성 능력 목록이 예산을 넘기지 못했다면 축소 2단계가 돌지 않았다")
        self.assertIn(EXISTING_UNIT, lines[-2], "축소가 뒤에서부터 자르면 재사용 후보 줄이 먼저 사라진다")
        self.assertTrue(lines[-1].startswith("확정:"), lines[-1])

    def test_what_the_proposal_said_is_kept_alongside_what_was_found(self):
        card = _card(_proposal(*self.OVERLAP, reuse_hits=["chg-20260827-rg-fallback-validate-245m"]))
        self.assertIn("chg-20260827-rg-fallback-validate-245m", card)
        self.assertIn(EXISTING_UNIT, card)

    def test_no_false_positive_on_an_unrelated_request(self):
        """AC-4(회귀 방지) — 겹치지 않는 제안에는 어떤 unit id 도 나타나지 않는다."""
        card = _card(_proposal("커피 머신 온도를 조절하는 기능", "coffee-temperature", "커피 온도"))
        hit = UNIT_ID_RE.search(card)
        self.assertIsNone(hit, f"거짓 양성: {hit.group(0) if hit else ''}")


class TestProcedureNamesTheCommandThatSearches(unittest.TestCase):
    """AC-5 — 요구하는 자리(절차 1단계)와 실제로 검색하는 것이 같은가."""

    def _step1(self):
        text = (ROOT / "core/workflows/plan/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## 절차", text)
        body = text.split("## 절차", 1)[1]
        # 1단계 본문만 읽는다. 앞부분을 함께 읽으면 역할 분담 표의 다른 명령이 잡혀
        # 이 단위 없이도 통과한다 — 이름이 말하는 사건과 실제로 보는 사건이 달라지는 자리다.
        return re.split(r"\n2\. ", body, maxsplit=1)[0]

    def test_step1_names_a_command_that_actually_finds_the_existing_unit(self):
        names = sorted(set(re.findall(r"`romeo ([a-z][a-z0-9-]*)", self._step1())))
        self.assertTrue(names, "1단계가 재사용 검색을 수행할 명령을 지정해야 한다")
        worked = [n for n in names
                  if (lambda r: r.returncode == 0 and EXISTING_UNIT in r.stdout)(
                      _romeo(n, EXISTING_SLUG, "--json"))]
        self.assertTrue(worked, f"1단계가 지정한 명령 {names} 중 어느 것도 기존 단위를 찾지 못한다")


if __name__ == "__main__":
    unittest.main()
