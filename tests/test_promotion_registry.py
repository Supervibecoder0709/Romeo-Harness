"""승격 문서 등록부 — 대조되지 않는 승격 문서를 지목하는가.

`docs/current/` 는 끝난 사실이 모이는 자리다. 그 자리의 문서는 **손으로 쓰고 기계가 대조한다** —
대조가 붙지 않은 문서는 검사받는 듯한 자리에 있으면서 아무도 보지 않는다(Q-91).
링크 검사는 이 루트의 모든 문서를 훑지만 내용 대조는 등록된 문서에만 붙으므로,
등록을 잊은 문서는 링크만 검사받고 그 안의 표는 아무 근거 없이 남는다.
"""
import time
import unittest
from pathlib import Path

from romeo import integrity

ROOT = Path(__file__).resolve().parents[1]


#: 판정을 뽑는 자리. 임시 루트에도 함께 두어야 대조가 성립한다 —
#: 없으면 코드 쪽이 빈 집합이 되어 문서의 모든 행이 「문서에만 있다」로 나온다.
DERIVE_SOURCES = (integrity.CLOSE_SRC, integrity.VALIDATE_SRC, integrity.POLICY_SRC)


def make_root(tmp, extra=()):
    """임시 루트에 지금의 승격 문서와 그 파생원을 두고, `extra` 이름의 문서를 더한다."""
    root = Path(tmp)
    (root / integrity.CURRENT_ROOT).mkdir(parents=True, exist_ok=True)
    for rel in sorted(integrity.PROMOTED) + list(DERIVE_SOURCES):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes((ROOT / rel).read_bytes())
    for name in extra:
        (root / integrity.CURRENT_ROOT / name).write_text(
            "# 승격을 가장한 문서\n\n대조원이 등록되지 않았다.\n", encoding="utf-8")
    return root


class TestRegistryIsLiteral(unittest.TestCase):
    """AC-5 ① — 등록부는 소스에 적힌 키만 갖는다."""

    def test_keys_do_not_follow_the_directory(self):
        """파일을 더하거나 지워도 등록부의 키 집합이 그대로다.

        디렉터리를 훑어 키를 채우는 구현이면 미등록 문서가 영영 생기지 않아
        아래 지목 검사가 공허하게 참이 된다."""
        import tempfile
        before = set(integrity.PROMOTED)
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp, extra=("decisions.md", "whatever.md"))
            integrity.run(root)
            self.assertEqual(before, set(integrity.PROMOTED))
            for f in (root / integrity.CURRENT_ROOT).glob("*.md"):
                f.unlink()
            integrity.run(root)
            self.assertEqual(before, set(integrity.PROMOTED))

    def test_registry_values_are_called_in_compare(self):
        """AC-5 ② — 등록부의 **값**이 실제 대조 경로에서 호출된다.

        어떤 키의 값을 반드시 어긋나게 하는 함수로 바꿔치면 `PROMOTION_DRIFT` 와 종료 코드 1 이 나온다.
        값을 부르지 않고 키만 세는 구현이면 여기서 통과하지 못한다."""
        import tempfile
        key = integrity.DOC_PATH
        original = integrity.PROMOTED[key]
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            code, lines = integrity.run(root)
            self.assertEqual(0, code, "\n".join(lines))
            try:
                integrity.PROMOTED[key] = lambda _root: {("ONLY_IN_CODE", "error"): "합성"}
                code, lines = integrity.run(root)
            finally:
                integrity.PROMOTED[key] = original
        self.assertEqual(1, code, "\n".join(lines))
        self.assertTrue([l for l in lines if "PROMOTION_DRIFT" in l and "ONLY_IN_CODE" in l],
                        "\n".join(lines))


class TestUncheckedPromotion(unittest.TestCase):
    """AC-6 — 지목 여부가 이름이 아니라 등록부에 드는가로 갈린다."""

    def names(self):
        """고정 이름 하나와 **실행할 때마다 달라지는 이름** 하나.

        두 번째가 있는 이유는 특정 이름을 특별 취급한 구현을 막기 위해서다 —
        유한한 이름 목록에 맞춘 구현은 실행 시각에서 나온 이름에서 걸린다."""
        return ("decisions.md", f"probe-{time.time_ns():x}.md")

    def test_pair_for_each_name(self):
        import tempfile
        for name in self.names():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = make_root(tmp, extra=(name,))
                code, lines = integrity.run(root)
                self.assertEqual(1, code, "\n".join(lines))
                hits = [l for l in lines if "UNCHECKED_PROMOTION" in l and name in l]
                self.assertEqual(1, len(hits), "\n".join(lines))

                (root / integrity.CURRENT_ROOT / name).unlink()
                code, lines = integrity.run(root)
                self.assertEqual(0, code, "\n".join(lines))
                self.assertEqual([], [l for l in lines if "UNCHECKED_PROMOTION" in l])

    def test_registered_document_is_not_flagged(self):
        """등록된 문서는 이름과 무관하게 지목되지 않는다 — 거짓 양성 배제."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            code, lines = integrity.run(root)
            self.assertEqual(0, code, "\n".join(lines))
            self.assertIn("등록 1건 · 미등록 0건", "\n".join(lines))


class TestThisRepository(unittest.TestCase):
    """AC-7 — 이 저장소에서 그 검사가 실제로 돌고 위반이 없다."""

    def test_counts_are_printed(self):
        code, lines = integrity.run(ROOT)
        self.assertEqual(0, code, "\n".join(lines))
        self.assertIn("등록 1건 · 미등록 0건", "\n".join(lines))


if __name__ == "__main__":
    unittest.main()
