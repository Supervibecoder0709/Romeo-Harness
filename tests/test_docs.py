"""문서 템플릿이 새 작업 단위에 실제로 도달하는가.

템플릿을 고치는 것과 **새 spec 이 그 문구를 갖는 것**은 다르다. 사이에는 `romeo new` 의 치환
(`{{...}}`)과 섹션 조립이 있고, 그 단계에서 사라지거나 잘려도 템플릿 파일만 grep 하면 통과한다.
그래서 여기서는 템플릿을 읽는 대신 **명령을 돌려 나온 결과물**을 본다(K-51).
"""
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
import io

from romeo import HARNESS_ROOT, frontmatter
from romeo.cli import main
from romeo.envelope import CHANGE_SCOPE_LABEL, change_scope_paths

TEMPLATE = Path(HARNESS_ROOT) / "core/templates/tech-spec.md"

# 「변경 범위」의 형식 제약(AC-2). 문장을 통째로 대조한다 — 낱말 하나만 보면 템플릿이 그 낱말을
# 다른 뜻으로 쓰는 순간 검사가 성립하지 않는다.
CONSTRAINT = (
    "**'바뀌는 파일·모듈' 은 한 줄이어야 하고, 각 항목의 경로는 백틱으로 감싼다.** "
    "이 줄이 작업 계약의 `allowed_paths` 가 된다"
)


class TestNewSpecCarriesChangeScopeConstraint(unittest.TestCase):
    """`bin/romeo new` 가 만든 spec 이 「변경 범위」의 한 줄·백틱 제약을 그대로 담는가 (AC-2).

    이 제약이 새 spec 에 없으면 구현자는 그 줄을 여러 줄로 나누거나 백틱 없이 적고, 그때
    `envelope build` 는 쓰기 상한을 만들지 못해 위임 입구에서 멈춘다 — 이번 정비가 고치는 결함 ② 다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        (self.root / "docs" / "work").mkdir(parents=True)
        self.cls = self.root / "classification.json"
        self.cls.write_text(json.dumps({
            "unit": "T1", "mode": "delivery", "intent": "write", "facets": ["tooling"],
            "gates": [], "blast_radius": "small", "uncertainty": "low",
        }, ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _new_spec(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["new", "--classification", str(self.cls), "--title", "제약 확인",
                       "--slug", "scope-constraint", "--one-line", "한 줄 제약이 새 spec 에 오는가",
                       "--root", str(self.root), "--json"])
        self.assertEqual(rc, 0, buf.getvalue())
        res = json.loads(buf.getvalue())
        specs = [f for f in res["files"] if f.endswith("spec.md")]
        self.assertTrue(specs, f"spec.md 가 만들어지지 않았다: {res}")
        return Path(specs[0])

    def test_template_states_the_constraint(self):
        """원본이 먼저 있어야 한다 — 없으면 아래 검사는 아무것도 지키지 못한다."""
        self.assertIn(CONSTRAINT, TEMPLATE.read_text(encoding="utf-8"),
                      "템플릿에 「변경 범위」 형식 제약 문장이 없다")

    def test_a_generated_spec_carries_it_verbatim(self):
        body = frontmatter.read(self._new_spec())[1]
        self.assertIn(CONSTRAINT, body,
                      "romeo new 가 만든 spec 에 형식 제약 문장이 오지 않았다")

    def test_the_constraint_states_why_it_matters(self):
        """제약만 있고 이유가 없으면 다음 구현자가 그것을 서식 취향으로 읽고 어긴다."""
        body = frontmatter.read(self._new_spec())[1]
        scope = body.split("## 변경 범위", 1)[1].split("\n## ", 1)[0]
        self.assertIn("allowed_paths", scope, "이 줄이 무엇이 되는지 적혀 있지 않다")
        self.assertIn("첫 백틱", scope, "무엇을 경로로 집는지 적혀 있지 않다")
        self.assertIn("여러 줄로 나누어 적으면", scope, "어기면 어떻게 되는지 적혀 있지 않다")

    def test_the_constraint_paragraph_is_not_read_as_the_scope_line(self):
        """제약 문단 자체가 「변경 범위」 파서에 걸리면 안 된다 — 문서가 자기 파서를 속이는 자리다."""
        spec = self._new_spec()
        fm, body = frontmatter.read(spec)
        self.assertEqual(change_scope_paths(body), [],
                         "채우지 않은 spec 에서 경로가 읽혔다 — 제약 문단을 범위 줄로 오인했다")

        filled = body.replace(f"- {CHANGE_SCOPE_LABEL} NEEDS_INPUT",
                              f"- {CHANGE_SCOPE_LABEL} `romeo/close.py` · `tests/`")
        self.assertNotEqual(filled, body, "「변경 범위」 줄의 형태가 바뀌었다 — 이 검사가 성립하지 않는다")
        self.assertEqual(change_scope_paths(filled), ["romeo/close.py", "tests/"])


if __name__ == "__main__":
    unittest.main()
