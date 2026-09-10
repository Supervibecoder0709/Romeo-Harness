"""오분류 예시를 정책표에 두고 카드가 읽어 인쇄한다 · 충돌 우선순위를 안내에 적는다(Q-102).

요구하는 자리(정책표)와 보는 자리(카드·안내)가 한 문자열인가를 본다(§11). 고치기 전 상태는
예시를 둘 자리가 **어디에도 없는** 것이었다 — 오분류를 두 번 같은 유형으로 겪고도 그것을
적어 둘 곳이 없었다.

| # | 어느 사건에서 보는가 | 어느 문서를 읽는가 | 무엇이 참이어야 충족인가 |
| --- | --- | --- | --- |
| AC-1 | 정책표 로드 | `core/policy/classification.yaml` | 예시가 1건 이상이고 각 항목이 네 필드를 빈 값 아닌 채로 갖는다 |
| AC-2 | 같은 로드 | 예시가 지목한 `fixtures/requests/<id>.yaml` | 예시의 레벨이 그 fixture 가 기록한 교정 결과값과 같다 |
| AC-3 | 카드 렌더링 | 정책표 **사본**(문구만 바꾼다) | 카드가 바뀐 문구를 인쇄한다 — 문구는 코드에 없다 |
| AC-4 | 카드 렌더링 | 세 레벨을 모두 담은 사본 | 제안과 레벨이 다른 예시는 전부, 같은 예시는 하나도 인쇄되지 않는다 |
| AC-5 | 같은 렌더링 | `core/policy/packages.yaml` 의 줄 예산 | 한 예시당 한 줄 · 예산 이내 · 각 줄이 카드의 접기 폭 이내 |
| AC-6 | 같은 렌더링 | 착수 전 카드 출력(`inputs/card-before-20260910.txt`) | 그때 사람이 보던 줄이 지금도 전부 남는다 |
| AC-7 | 안내 문서 로드 | `core/workflows/plan/SKILL.md` 의 **표식 줄만** | 그 줄의 항목 목록이 정책표와 순서까지 같다 |

**반례는 빈 값이 아니라 그럴듯한 거짓 값이다.** 여기서 그것은 ① 형식은 멀쩡한데 고치려던 오분류를
정답으로 등록한 예시(AC-2 의 레벨 대조가 겨눈다), ② 카드가 정책표를 읽는 척하면서 문구는 코드에
복제해 둔 구현(AC-3 이 사본의 문구로 겨눈다), ③ 항목을 정책표 순서대로 적어 놓고 하나를 빼거나
둘을 맞바꾼 안내 줄(AC-7 의 두 변형이 겨눈다)이다.

**회귀 방지 검사** — 양쪽 상태에서 통과하는 것이 정의이므로 판별력이 없다:
`test_baseline_lines_survive`(AC-6) · `test_item_names_are_not_copied_into_this_file`(AC-7) ·
`test_policy_cue_text_is_not_copied_anywhere`(AC-3 의 문구 복제 금지 조항).
나머지는 판별 검사이고, 이 단위가 없으면 실패한다.

**이 파일은 정책표의 실제 `cue` 문구도, 충돌 우선순위 항목의 이름도 담지 않는다.** 담으면 정책표를
고칠 때 이 파일도 함께 고쳐야 하고, 그때 대조되는 것은 두 사본의 일치일 뿐 정책표와 산출물의
일치가 아니다. `test_item_names_are_not_copied_into_this_file` 이 그것을 자기 자신에게 건다.
"""
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from romeo import card as card_mod
from romeo.card import render_card
from romeo.policy import load_policy, load_project_state, route
from romeo.util import load_any, project_root

REPO = project_root(Path(__file__).parent)
UNIT_DIR = REPO / "docs/work/feat-20260910-router-fewshot-conflict-guidance-k8dd"
BASELINE_PROPOSAL = UNIT_DIR / "inputs/card-baseline.proposal.yaml"
BASELINE_CARD = UNIT_DIR / "inputs/card-before-20260910.txt"
GUIDANCE = REPO / "core/workflows/plan/SKILL.md"
# 안내 문서에서 대조할 **한 줄**을 특정하는 표식. 본문 아무 데나 나타나는 낱말을 세지 않는다.
GUIDANCE_MARKER = "<!-- romeo:conflict-priority -->"

# AC-6 의 제외 규칙. 저장소·설치 상태가 바뀌면 값이 달라지는 줄이라 두 시점의 카드를 대조할 수 없다.
# 양쪽에 **같은 규칙**을 적용하고, 실패하면 이 문장을 함께 인쇄한다.
EXCLUSION_RULE = (
    "제외 규칙(양쪽에 같게 적용): ① 「재사용 후보:」 줄 — 저장소의 다른 작업 단위 목록에 따라 달라진다 · "
    "② 「능력:」 절과 그 들여쓴 행 — 프로브가 실행 환경의 설치 상태를 읽는다 · "
    "③ 「부품:」 절과 그 들여쓴 행 — 부착 상태(.harness/romeo.project.yaml)에 따라 달라진다. "
    "들여쓴 행은 두 칸 이상 들여쓰고 목록 기호(- )로 시작하지 않는 줄이다."
)
_EXCLUDED_HEADERS = ("재사용 후보:", "능력:", "부품:")


def _allowed_levels():
    """허용 레벨의 정본은 제안 스키마의 어휘다 — 이 파일이 따로 정하지 않는다."""
    schema = load_any(REPO / "core/schemas/proposal.json")
    return list(schema["definitions"]["classification"]["properties"]["uncertainty"]["enum"])


def _classification(root=REPO):
    return load_any(Path(root) / "core/policy/classification.yaml")


def _examples(data=None):
    two = (data or _classification()).get("two_questions") or {}
    return ((two.get("uncertainty") or {}).get("examples")) or []


def _level_defects(examples, root=REPO):
    """예시의 레벨이 그 fixture 가 기록한 교정 결과값과 같은가(AC-2).

    반례를 형태가 아니라 **내용**에서 잡는 자리다 — 네 필드를 갖췄지만 고치려던 오분류를 정답으로
    등록한 예시는 형식 검사를 전부 통과한다. `source` 는 목록이고, 문자열로 잘못 다루면 정상
    정책표에서도 실패한다: `test_every_example_level_matches_its_fixture` 가 그것을 막는다.
    """
    defects = []
    for i, ex in enumerate(examples):
        level = ex.get("level")
        sources = ex.get("source")
        if not isinstance(sources, list) or not sources:
            defects.append(f"examples[{i}]: source 가 비어 있지 않은 목록이 아니다 ({sources!r})")
            continue
        for fid in sources:
            path = Path(root) / "fixtures/requests" / f"{fid}.yaml"
            if not path.is_file():
                defects.append(f"examples[{i}]: fixture 가 없다 — {path}")
                continue
            changes = ((load_any(path).get("human_correction") or {}).get("changes")) or []
            recorded = [c.get("to") for c in changes if c.get("field") == "classification.uncertainty"]
            if level not in recorded:
                defects.append(
                    f"examples[{i}]: level={level!r} 인데 {fid} 의 교정 결과값은 {recorded!r} 다")
    return defects


def _guidance_line(text=None):
    """표식이 붙은 줄 하나. 없으면 None, 둘 이상이면 목록 길이로 드러난다."""
    body = text if text is not None else GUIDANCE.read_text(encoding="utf-8")
    hits = [ln for ln in body.split("\n") if GUIDANCE_MARKER in ln]
    return hits


def _items_on(line):
    """그 줄에서 백틱으로 감싼 토큰만 뽑는다 — 항목 이름을 이 파일에 적지 않기 위해서다."""
    return re.findall("`([^`]+)`", line)


def _with_items(line, items):
    """표식 줄의 백틱 토큰만 순서대로 갈아 끼운다 — 반례를 **줄 위에서** 만들기 위해서다."""
    it = iter(items)
    return re.sub("`([^`]+)`", lambda m: "`" + next(it) + "`", line)


def _conflict_priority(root=REPO):
    return list(_classification(root)["conflict_priority"])


def _policy_copy(tmp, mutate):
    """정책표 사본을 만들어 고친 뒤 로드한다. 정본은 건드리지 않는다."""
    root = Path(tmp)
    shutil.copytree(REPO / "core/policy", root / "core/policy")
    shutil.copytree(REPO / "core/schemas", root / "core/schemas")
    path = root / "core/policy/classification.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return load_policy(root)


def _proposal(level=None):
    prop = load_any(BASELINE_PROPOSAL)
    if level is not None:
        prop["candidate"]["uncertainty"] = level
    return prop


def _card(prop, policy=None):
    pol = policy or load_policy()
    out = route(prop["candidate"], policy=pol, project_state=load_project_state(REPO))
    return render_card(prop, out, policy=pol, root=REPO, harness_root=REPO)


def _prefix():
    """접두는 구현이 소유한다 — 없으면 `None` 을 돌려주고 검사가 실패로 말한다(import 오류가 아니라)."""
    return getattr(card_mod, "EXAMPLE_PREFIX", None)


def _wrap_width():
    return getattr(card_mod, "WRAP_WIDTH", None)


def _example_lines(text):
    p = _prefix()
    return [ln for ln in text.split("\n") if p and ln.startswith(p)]


def _stable_lines(text):
    """두 시점에 대조할 수 있는 줄만 남긴다(AC-6). 규칙은 `EXCLUSION_RULE` 이 인쇄한다."""
    out, skipping = [], False
    for ln in text.split("\n"):
        indented = ln.startswith("  ") and not ln.lstrip().startswith("- ")
        if skipping and indented:
            continue
        skipping = any(ln.startswith(h) for h in _EXCLUDED_HEADERS)
        if skipping:
            continue
        out.append(ln)
    return out


class TestPolicyExamples(unittest.TestCase):
    """AC-1·AC-2 — 예시가 있는가, 그리고 그 예시가 기록과 맞는가."""

    def setUp(self):
        self.examples = _examples()

    def test_at_least_one_example(self):
        # 아래 두 검사는 예시가 0건이면 루프가 돌지 않아 **공전**한다. 판별력은 이 검사가 만든다.
        self.assertGreaterEqual(len(self.examples), 1, "정책표에 오분류 예시가 없다")

    def test_every_example_has_four_non_empty_fields(self):
        allowed = _allowed_levels()
        for i, ex in enumerate(self.examples):
            with self.subTest(i=i):
                self.assertIn(ex.get("level"), allowed, f"examples[{i}]: level 이 허용값이 아니다")
                for key in ("cue", "why"):
                    self.assertTrue(str(ex.get(key) or "").strip(), f"examples[{i}]: {key} 가 비어 있다")
                src = ex.get("source")
                self.assertIsInstance(src, list, f"examples[{i}]: source 가 목록이 아니다")
                self.assertTrue(src, f"examples[{i}]: source 가 비어 있다")
                for fid in src:
                    self.assertTrue(str(fid or "").strip(), f"examples[{i}]: source 에 빈 id 가 있다")

    def test_every_example_level_matches_its_fixture(self):
        self.assertEqual(_level_defects(self.examples), [], "예시의 레벨이 fixture 기록과 다르다")

    def test_wrong_level_is_rejected(self):
        # 그럴듯한 거짓 값 — 형식은 그대로 두고 레벨만 다른 허용값으로 바꾼다.
        self.assertTrue(self.examples, "예시가 없으면 이 반례를 만들 수 없다")
        allowed = _allowed_levels()
        for i, ex in enumerate(self.examples):
            for level in allowed:
                if level == ex.get("level"):
                    continue
                with self.subTest(i=i, level=level):
                    forged = [dict(e) for e in self.examples]
                    forged[i]["level"] = level
                    self.assertNotEqual(_level_defects(forged), [],
                                        f"examples[{i}] 의 레벨을 {level!r} 로 바꿔도 통과한다")


class TestCardPrintsExamples(unittest.TestCase):
    """AC-3·AC-4·AC-5 — 카드가 정책표에서 읽어 인쇄하는가."""

    def test_card_prints_the_cue_from_the_policy(self):
        # 기대 문구는 **사본에서만** 온다. 정본의 문구는 이 파일 어디에도 없다.
        real = _examples()
        self.assertTrue(real, "정책표에 예시가 없어 파생 여부를 볼 수 없다")
        marks = {i: f"CUE-SENTINEL-{i}" for i in range(len(real))}

        def mutate(data):
            for i, ex in enumerate(data["two_questions"]["uncertainty"]["examples"]):
                ex["cue"] = marks[i]

        prop = _proposal()
        level = prop["candidate"]["uncertainty"]
        with tempfile.TemporaryDirectory() as tmp:
            text = _card(prop, _policy_copy(tmp, mutate))
        plain = _card(prop)
        for i, ex in enumerate(real):
            if ex.get("level") == level:
                continue
            with self.subTest(i=i):
                self.assertIn(marks[i], text, f"사본의 cue 를 바꿨는데 카드가 옛 문구를 인쇄한다")
                self.assertNotIn(marks[i], plain, "정본 카드에 사본의 문구가 나온다")

    def test_policy_cue_text_is_not_copied_anywhere(self):
        # 자기 검사(회귀 방지) — 문구가 코드나 저장된 기대 출력에 있으면, 위 파생 검사가 대조하는 것은
        # 정책표와 산출물의 일치가 아니라 두 사본의 일치다. 읽는 자리는 정책표 하나여야 한다.
        cues = [str(ex.get("cue") or "") for ex in _examples()]
        self.assertTrue(cues, "정책표에 예시가 없어 이 검사가 공전한다")
        targets = {
            "이 검사 파일": Path(__file__),
            "카드 구현": REPO / "romeo/card.py",
            "AC-6 기준선 파일": BASELINE_CARD,
        }
        for label, path in targets.items():
            body = path.read_text(encoding="utf-8")
            for cue in cues:
                with self.subTest(where=label, n=len(cue)):
                    self.assertNotIn(cue, body, f"{label} 에 정책표의 문구가 복제돼 있다")

    def test_example_line_is_marked_as_an_example(self):
        prefix = _prefix()
        self.assertIsNotNone(prefix, "romeo.card 에 EXAMPLE_PREFIX 가 없다")
        self.assertTrue(prefix.strip(), "EXAMPLE_PREFIX 가 공백뿐이다")
        text = _card(_proposal())
        lines = text.split("\n")
        marked = [ln for ln in lines if ln.startswith(prefix)]
        self.assertTrue(marked, "참고 예시임이 드러나는 접두가 붙은 줄이 없다")
        # 접두가 다른 줄과 겹치면 사람은 예시를 제안의 확정값과 구별하지 못한다.
        for ln in lines:
            if ln in marked:
                continue
            with self.subTest(line=ln[:24]):
                self.assertFalse(ln.startswith(prefix), "예시가 아닌 줄이 같은 접두로 시작한다")

    def test_only_differing_levels_are_printed(self):
        levels = _allowed_levels()
        marks = {lv: f"CUE-SENTINEL-{lv}" for lv in levels}

        def mutate(data):
            data["two_questions"]["uncertainty"]["examples"] = [
                {"level": lv, "cue": marks[lv], "why": f"why-{lv}", "source": [f"fx-{lv}"]}
                for lv in levels
            ]

        with tempfile.TemporaryDirectory() as tmp:
            pol = _policy_copy(tmp, mutate)
            for chosen in levels:
                with self.subTest(chosen=chosen):
                    text = _card(_proposal(chosen), pol)
                    shown = {lv for lv in levels if marks[lv] in text}
                    self.assertEqual(shown, {lv for lv in levels if lv != chosen})
        # 정본에서도 같은 규칙이 성립한다 — 같은 레벨의 예시는 인쇄되지 않는다.
        for ex in _examples():
            with self.subTest(level=ex["level"]):
                same = _card(_proposal(ex["level"]))
                self.assertEqual(_example_lines(same), [],
                                 "제안과 같은 레벨의 예시가 인쇄됐다")

    def test_budget_and_line_width(self):
        width = _wrap_width()
        self.assertIsNotNone(width, "romeo.card 에 WRAP_WIDTH 가 없다")
        limit = load_policy()["packages"]["budgets"]["card_max_lines"]
        prop = _proposal()
        chosen = prop["candidate"]["uncertainty"]
        expected = sum(1 for ex in _examples() if ex.get("level") != chosen)
        text = _card(prop)
        lines = text.split("\n")
        self.assertEqual(len(_example_lines(text)), expected, "예시가 한 예시당 한 줄이 아니다")
        self.assertLessEqual(len(lines), limit, f"카드가 {limit}줄 예산을 넘었다")
        for ln in _example_lines(text):
            self.assertLessEqual(len(ln), width, f"예시 줄이 접기 폭 {width} 를 넘었다: {ln}")
        # 긴 문구를 넣어도 한 줄·폭 이내여야 한다 — 개행 없는 긴 한 줄로 도망갈 수 없다.

        def mutate(data):
            data["two_questions"]["uncertainty"]["examples"] = [
                {"level": lv, "cue": "가" * 400, "why": "w", "source": [f"fx-{lv}"]}
                for lv in _allowed_levels() if lv != chosen
            ]

        with tempfile.TemporaryDirectory() as tmp:
            long_text = _card(prop, _policy_copy(tmp, mutate))
        long_lines = _example_lines(long_text)
        self.assertEqual(len(long_lines), len(_allowed_levels()) - 1)
        self.assertLessEqual(len(long_text.split("\n")), limit)
        for ln in long_lines:
            self.assertLessEqual(len(ln), width, f"긴 문구가 접기 폭을 넘었다: {len(ln)}")


class TestBaselinePreserved(unittest.TestCase):
    """AC-6 — 착수 전 카드의 줄이 지금도 전부 남는가(회귀 방지)."""

    def test_baseline_lines_survive(self):
        raw = BASELINE_CARD.read_text(encoding="utf-8").split("\n")
        cut = raw.index("---")
        base = _stable_lines("\n".join(raw[cut + 1:]).strip("\n"))
        now = _stable_lines(_card(_proposal()))
        # 순서와 중복까지 보존하는지 본다 — 부분 수열이면 새 줄이 끼어들어도 옛 줄은 밀려나지 않았다.
        it = iter(now)
        missing = [ln for ln in base if not any(x == ln for x in it)]
        self.assertEqual(missing, [],
                         "착수 전 카드에 있던 줄이 지금 카드에 없거나 순서가 바뀌었다.\n"
                         + EXCLUSION_RULE + "\n기준: " + str(BASELINE_CARD))


class TestConflictPriorityGuidance(unittest.TestCase):
    """AC-7 — 안내의 표식 줄이 정책표와 순서까지 같은가."""

    def setUp(self):
        self.priority = _conflict_priority()
        self.hits = _guidance_line()

    def test_guidance_line_matches_the_policy_exactly(self):
        self.assertEqual(len(self.hits), 1,
                         f"안내에 표식 {GUIDANCE_MARKER} 이 붙은 줄이 정확히 하나가 아니다 ({len(self.hits)}건)")
        self.assertEqual(_items_on(self.hits[0]), self.priority,
                         "표식 줄의 항목 목록이 정책표와 다르다(순서 포함)")

    def test_dropping_an_item_from_the_guidance_fails(self):
        self.assertEqual(len(self.hits), 1, "표식 줄이 하나가 아니면 반례를 만들 수 없다")
        line = self.hits[0]
        for item in self.priority:
            with self.subTest(dropped=len(item)):
                forged = line.replace("`" + item + "`", "", 1)
                self.assertNotEqual(_items_on(forged), self.priority,
                                    "안내에서 항목을 하나 빼도 검사가 통과한다")

    def test_swapping_two_items_in_the_guidance_fails(self):
        self.assertEqual(len(self.hits), 1, "표식 줄이 하나가 아니면 반례를 만들 수 없다")
        line = self.hits[0]
        items = _items_on(line)
        self.assertEqual(items, self.priority, "정상 상태가 아니면 순서 반례를 만들 수 없다")
        for a in range(len(items)):
            for b in range(a + 1, len(items)):
                with self.subTest(a=a, b=b):
                    forged = list(items)
                    forged[a], forged[b] = forged[b], forged[a]
                    self.assertNotEqual(_items_on(_with_items(line, forged)), self.priority,
                                        "안내에서 두 항목의 순서를 바꿔도 검사가 통과한다")

    def test_item_names_are_not_copied_into_this_file(self):
        # 자기 검사 — 항목 이름을 여기 적으면 대조되는 것은 두 사본의 일치일 뿐이다.
        src = Path(__file__).read_text(encoding="utf-8")
        for item in self.priority:
            for quoted in ("`" + item + "`", '"' + item + '"', "'" + item + "'"):
                with self.subTest(n=len(item), q=quoted[0]):
                    self.assertNotIn(quoted, src, "항목 이름이 이 파일에 인용된 채로 있다")


if __name__ == "__main__":
    unittest.main()
