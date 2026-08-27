import unittest

from romeo import frontmatter
from romeo.ids import ID_RE, new_id, parse_id, slugify
from romeo.schema import validate


class TestIds(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("RG Fallback for validate.sh"), "rg-fallback-for-validate-sh")
        self.assertEqual(slugify("한글만 있으면"), "unit")
        self.assertEqual(slugify("  --a--b-- "), "a-b")
        self.assertLessEqual(len(slugify("x" * 100)), 40)

    def test_new_id_format_and_no_collision(self):
        ids = {new_id("T0", "rg-fallback", "20260827") for _ in range(300)}
        self.assertGreater(len(ids), 290)  # entropy 4자리(32^4)로 같은 날 같은 slug 충돌 없음
        one = next(iter(ids))
        self.assertRegex(one, ID_RE)
        self.assertEqual(parse_id(one)["unit"], "T0")
        self.assertTrue(new_id("T1", "x").startswith("feat-"))
        self.assertTrue(new_id("T2", "x").startswith("init-"))
        with self.assertRaises(ValueError):
            new_id("none", "x")


class TestSchema(unittest.TestCase):
    schema = {
        "type": "object", "required": ["a"], "additionalProperties": False,
        "properties": {"a": {"type": "string", "enum": ["x", "y"]}, "b": {"$ref": "#/definitions/n"}},
        "definitions": {"n": {"type": ["integer", "null"]}},
    }

    def test_validate(self):
        self.assertEqual(validate({"a": "x", "b": 1}, self.schema), [])
        self.assertTrue(any("필수" in e for e in validate({}, self.schema)))
        self.assertTrue(any("허용값" in e for e in validate({"a": "z"}, self.schema)))
        self.assertTrue(any("허용되지 않은 키" in e for e in validate({"a": "x", "c": 1}, self.schema)))
        self.assertTrue(any("타입" in e for e in validate({"a": "x", "b": "no"}, self.schema)))


class TestFrontmatter(unittest.TestCase):
    def test_roundtrip(self):
        data = {"id": "chg-20260827-x-ab2c", "facets": ["ui"], "routing": {"policy_version": "0.1.0", "fired_rules": ["a:b->c"]}}
        text = frontmatter.join(data, "# 제목\n본문\n")
        fm, body = frontmatter.split(text)
        self.assertEqual(fm, data)
        self.assertEqual(body, "# 제목\n본문\n")
        self.assertEqual(frontmatter.split("no frontmatter"), (None, "no frontmatter"))


if __name__ == "__main__":
    unittest.main()
