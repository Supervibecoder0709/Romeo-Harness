"""페이로드 작업 단위의 `required_checks` 에 하네스 자신의 테스트를 넣지 않는다.

규칙의 원본은 `core/templates/tech-spec.md` 의 검증 계획 절이다. 근거는 `feat-20260829-license-field-46an` 의
check-5 — 그 페이로드 단위의 검증 계획에 하네스 unittest 가 들어 있어서, 하네스가 깨진 동안 그 단위가 닫히지 못했다.
산출물은 멀쩡한데 완료가 서지 않았고, 어느 쪽이 깨졌는지 판정이 구분하지 못했다(체크리스트 31).

하네스 저장소 **자신**의 단위에서는 그 검사가 정당하다 — 그때는 그것이 이 단위의 산출물이기 때문이다.
그래서 검출기는 열거만 하고 차단하지 않는다. 페이로드인지 아닌지는 부르는 쪽이 안다(`romeo/run_unit.py` 1단계).
"""
import unittest
from pathlib import Path

from romeo import HARNESS_ROOT
from romeo.close import harness_own_checks, required_checks

TEMPLATE = HARNESS_ROOT / "core/templates/tech-spec.md"

# 부착 대상 프로젝트의 spec 예시. check-2 가 규칙 위반이다 — 이 단위의 산출물이 아니라 하네스를 검사한다.
PAYLOAD_SPEC = """## 검증 계획

```yaml
required_checks:
  - id: check-1
    command: "npm test"
    expect: exit 0
  - id: check-2
    command: "python3 -m unittest discover -s tests"
    expect: exit 0
  - id: check-3
    command: "./bin/romeo validate"
    expect: exit 0
```
"""

CLEAN_PAYLOAD_SPEC = """## 검증 계획

```yaml
required_checks:
  - id: check-1
    command: "npm test"
    expect: exit 0
  - id: check-2
    command: "npx tsc --noEmit"
    expect: exit 0
```
"""


class TestPayloadChecksRule(unittest.TestCase):
    def test_template_states_the_rule(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("하네스 자신의 테스트", text)
        self.assertIn("required_checks", text)
        # 예외도 함께 적혀 있어야 규칙이 과잉 적용되지 않는다
        self.assertIn("하네스 저장소 **자신**", text)

    def test_it_catches_a_payload_spec_that_runs_the_harness_tests(self):
        found = harness_own_checks(required_checks(PAYLOAD_SPEC))
        self.assertEqual([c["id"] for c in found], ["check-2", "check-3"])

    def test_it_leaves_a_clean_payload_spec_alone(self):
        self.assertEqual(harness_own_checks(required_checks(CLEAN_PAYLOAD_SPEC)), [])

    def test_it_catches_the_harness_self_checks_by_name(self):
        plan = [{"id": f"c{i}", "command": cmd} for i, cmd in enumerate([
            "./bin/romeo compile --check",
            "bin/romeo doctor",
            "romeo fixtures parity --report",
            "cd sub && ./bin/romeo validate",
            "python -m unittest tests.test_x",
        ])]
        self.assertEqual(len(harness_own_checks(plan)), 5)

    def test_it_does_not_flag_commands_that_merely_mention_the_words(self):
        plan = [{"id": "c1", "command": "echo 'romeo validate 는 하네스 검사다'"},
                {"id": "c2", "command": "pytest tests/"},
                {"id": "c3", "command": "make unittest-report"}]
        self.assertEqual(harness_own_checks(plan), [])

    def test_empty_plan_is_not_a_violation(self):
        self.assertEqual(harness_own_checks([]), [])
        self.assertEqual(harness_own_checks(None), [])


if __name__ == "__main__":
    unittest.main()
