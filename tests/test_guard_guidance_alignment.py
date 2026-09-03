"""가드 승인 명령을 **안내하는** 자리가 그 명령이 **요구하는** 자리를 따라가는지 본다 —
`feat-20260903-guard-guidance-vendor-drift-bvjz`.

요구는 `core/policy/execution-guards.yaml` 의 `required_explanation` 이 소유하고,
집행은 `romeo/evidence.py` 의 `parse_guard_explanation` 이 한다. 안내(절차 문서의 명령 예시)가
그 요구를 모르면 **지시대로 따른 실행이 exit 2 로 막히고 지시를 무시한 실행만 통과한다** —
요구하는 자리와 보는 자리가 어긋난 AGENTS.core §11 의 모양이다.

**라벨을 이 파일에 복사하지 않는다.** 정책표에서 읽고, 집행이 쓰는 것과 같은 매처로 대조한다 —
적는 순간 정본이 둘이 되고, 라벨을 바꾼 커밋이 "요구는 넷인데 안내는 셋" 을 다시 만든다.

**반례는 빈 값이 아니라 그럴듯한 거짓 값이다**(§11). 여기 반례 둘은 형태가 그럴듯하고 내용이 거짓이다 —
네 항목 중 **셋만** 적은 안내와, 설명은 산문으로 하면서 명령에서는 `--note` 를 뺀 안내.
"""
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from romeo.evidence import parse_guard_explanation, required_explanation
from romeo.util import dump_yaml, load_yaml, project_root

REPO = project_root(Path(__file__).parent)

#: 가드 승인·거부 명령을 안내하는 자리. 코어 절차 하나와 두 런타임 매핑이다.
GUIDANCE_FILES = [
    "core/workflows/implement/SKILL.md",
    "adapters/claude/workflows/implement.md",
    "adapters/codex/workflows/implement.md",
]

POLICY_REL = "core/policy/execution-guards.yaml"

#: 안내 줄 = 가드 결정 기록 명령이 나오는 줄. 승인과 거부 둘 다 같은 요구를 받는다.
COMMAND_RE = re.compile(r"evidence\s+(?:approve|reject)\b")
#: `--note` 와 그 인용된 값. 값을 따로 뽑는 이유는 같은 줄의 산문(예: "영향 범위와 복구 방법을 출력하고")이
#: 라벨로 오인되면 안 되기 때문이다 — 요구를 받는 것은 note 값이지 그 줄이 아니다.
NOTE_RE = re.compile(r'--note\s+"([^"]*)"')


def guidance_lines(text):
    """가드 결정 명령이 나오는 줄 → [(줄번호, 줄)]."""
    return [(i, line) for i, line in enumerate(text.splitlines(), 1) if COMMAND_RE.search(line)]


def violations(rel, text, items, harness_root=None):
    """안내가 요구를 따라가지 못하는 자리 → 사람이 읽는 사유 목록.

    `items` 는 `required_explanation()` 이 정책표에서 읽은 항목이고, 몇 개인지도 정책표가 정한다 —
    이 함수는 라벨도 개수도 모른다. 대조는 집행이 쓰는 `parse_guard_explanation` 이 그대로 하고,
    예외 없이 모든 안내 줄에 적용한다 — 라벨이 눈에 띄지 않는다는 이유로 대조를 건너뛰면, 정책이
    라벨을 바꿨을 때 옛 라벨로 적힌 안내가 「라벨 없음」으로 보여 규칙 대상에서 빠진다(AC-3)."""
    out = []
    for lineno, line in guidance_lines(text):
        m = NOTE_RE.search(line)
        if not m:
            where = "`--note` 값이 인용부호로 묶여 있지 않다" if "--note" in line else "`--note` 인자가 없다"
            out.append(f"{rel}:{lineno}: {where} — 지시대로 따르면 기록이 거부된다")
            continue
        note = m.group(1)
        try:
            parse_guard_explanation(note, harness_root)
        except ValueError as exc:
            out.append(f"{rel}:{lineno}: `--note` 값이 설명 요구를 채우지 못한다 — {exc}")
    return out


class TestGuidanceFollowsRequirement(unittest.TestCase):
    def setUp(self):
        self.items = required_explanation()
        self.texts = {rel: (REPO / rel).read_text(encoding="utf-8") for rel in GUIDANCE_FILES}

    def test_every_guidance_file_actually_carries_the_command(self):
        """대상 파일에서 안내 줄이 하나도 안 잡히면 이 검사는 아무것도 확인하지 않는다(빈 검사)."""
        self.assertEqual(len(GUIDANCE_FILES), 3, f"안내 자리가 3곳이 아니다: {GUIDANCE_FILES}")
        for rel, text in self.texts.items():
            self.assertTrue(guidance_lines(text),
                            f"{rel} 에 가드 결정 명령 안내가 없다 — 대상 목록이 낡았다")

    def test_guidance_commands_carry_note(self):
        """AC-1: 안내하는 명령 예시가 `--note` 인자를 담는다."""
        missing = [f"{rel}:{lineno}" for rel, text in self.texts.items()
                   for lineno, line in guidance_lines(text) if "--note" not in line]
        self.assertEqual(missing, [], f"`--note` 없이 안내하는 자리: {missing}")

    def test_note_value_lists_all_labels_or_none(self):
        """AC-2: `--note` 값이 설명 라벨을 일부만 나열하지 않는다."""
        found = [v for rel, text in self.texts.items() for v in violations(rel, text, self.items)]
        self.assertEqual(found, [], "안내가 요구를 따라가지 못한다:\n" + "\n".join(found))


class TestLabelsComeFromPolicy(unittest.TestCase):
    """AC-3: 라벨의 출처는 정책표다 — 정책의 라벨을 바꾸면 이 검사가 그 즉시 새 라벨로 대조한다(§11)."""

    def _harness_with(self, mutate):
        """정책표만 바꾼 임시 하네스 루트를 만든다 — 검사가 그 파일을 읽는지 실측하기 위해서다."""
        tmp = Path(tempfile.mkdtemp(prefix="guard-policy-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        dest = tmp / POLICY_REL
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = load_yaml(REPO / POLICY_REL)
        data["required_explanation"] = mutate(data["required_explanation"])
        dest.write_text(dump_yaml(data), encoding="utf-8")
        return tmp

    def test_a_fifth_requirement_makes_todays_guidance_insufficient(self):
        """요구가 하나 늘면, 네 항목만 적은 안내가 그 즉시 '일부만 나열' 로 잡힌다."""
        extra = {"key": "rollback_owner", "label": "되돌릴 사람", "why": "누가 되돌리는가"}
        tmp = self._harness_with(lambda items: items + [extra])
        items5 = required_explanation(tmp)
        self.assertEqual(len(items5), len(required_explanation()) + 1)

        items4 = required_explanation()
        note = " / ".join(f"{it['label']}: <{it['why']}>" for it in items4)
        line = f'`bin/romeo evidence approve --unit <id> --guard <가드> --note "{note}" --run <run>`'
        self.assertEqual(violations("안내.md", line, items4), [],
                         "네 항목을 다 적은 안내가 지금 요구에서는 통과해야 한다")
        found = violations("안내.md", line, items5, harness_root=tmp)
        self.assertEqual(len(found), 1, f"요구가 늘었는데 같은 안내가 통과했다 — 정책을 읽지 않는다: {found}")
        self.assertIn(extra["label"], found[0])

    def test_renaming_a_label_moves_the_verdict_with_it(self):
        """라벨 이름을 바꾸면, 옛 이름으로 적힌 안내가 새 요구에 못 미쳐 그 즉시 잡힌다."""
        tmp = self._harness_with(lambda items: [dict(it, label=it["label"] + "지수") for it in items])
        renamed = required_explanation(tmp)
        self.assertNotEqual([it["label"] for it in renamed],
                            [it["label"] for it in required_explanation()])
        text = (REPO / GUIDANCE_FILES[0]).read_text(encoding="utf-8")
        found = violations(GUIDANCE_FILES[0], text, renamed, harness_root=tmp)
        self.assertEqual(len(found), 1, f"라벨을 개명했는데 옛 라벨로 적힌 안내가 통과했다: {found}")
        self.assertIn("채우지 못한다", found[0])


class TestCounterexamples(unittest.TestCase):
    """AC-4: 반례는 빈 값이 아니라 그럴듯한 거짓 값이다."""

    def setUp(self):
        self.items = required_explanation()

    def test_note_listing_three_of_four_labels_fails(self):
        three = " / ".join(f"{it['label']}: <{it['why']}>" for it in self.items[:3])
        line = f'`bin/romeo evidence approve --unit <id> --guard <가드> --by <승인자> --note "{three}" --run <run>`'
        found = violations("반례-셋만.md", line, self.items)
        self.assertEqual(len(found), 1, f"셋만 적은 안내가 통과했다: {found}")
        self.assertIn(self.items[3]["label"], found[0])

    def test_note_dropped_while_prose_explains_fails(self):
        line = ("5. 가드 승인은 영향 범위와 복구 방법을 출력하고 승인을 기다린 뒤 "
                "`bin/romeo evidence approve --unit <id> --guard <가드> --by <사용자> --run <run>` 으로 기록한다.")
        found = violations("반례-note없음.md", line, self.items)
        self.assertEqual(len(found), 1, f"`--note` 없는 안내가 통과했다: {found}")
        self.assertIn("`--note` 인자가 없다", found[0])

    def test_pointing_to_the_core_format_without_labels_fails(self):
        """예외 없음(AC-3) — 라벨을 나열하지 않고 형식만 가리키는 안내도 이제는 잡힌다.
        `GUIDANCE_FILES` 3곳은 이미 라벨 네 개를 직접 적으므로(실측) 이 요구가 실제 안내를 막지 않는다."""
        line = '`bin/romeo evidence approve --unit <id> --guard <가드> --by <사용자> --note "<코어 절차 6번의 형식>" --run <run>`'
        found = violations("가리키는안내.md", line, self.items)
        self.assertEqual(len(found), 1, f"라벨을 가리키기만 한 안내가 통과했다: {found}")
        self.assertIn("채우지 못한다", found[0])


class TestPolicyKeepsNoEnforcementCopy(unittest.TestCase):
    """AC-5: 코어 정책표에 집행 수단 사본이 남지 않는다 — 정본은 `.harness/bindings.yaml` 이다(C-C6)."""

    def setUp(self):
        self.text = (REPO / POLICY_REL).read_text(encoding="utf-8")

    def test_no_top_level_enforcement_key(self):
        keys = re.findall(r"(?m)^([A-Za-z_][\w-]*):", self.text)
        self.assertNotIn("enforcement", keys,
                         f"{POLICY_REL} 에 최상위 enforcement 키가 있다 — 집행 수단의 정본은 .harness/bindings.yaml 이다")

    def test_canonical_pointer_is_written_where_the_copy_was(self):
        self.assertIn(".harness/bindings.yaml", self.text,
                      f"{POLICY_REL} 에 정본 위치가 적혀 있지 않다 — 걷어낸 값을 어디서 찾는지 알 수 없다")
