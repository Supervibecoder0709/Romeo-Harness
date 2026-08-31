"""페이로드 단위의 검증 계획에 하네스 자신의 테스트를 넣지 않는다 (단위 4 · AC-5).

근거: `feat-20260829-license-field-46an` 의 check-5 가 하네스 unittest 라서, 하네스가 깨진 동안
페이로드 작업 단위가 자기 산출물과 무관한 이유로 닫히지 못했다(체크리스트 31)."""
import unittest
from pathlib import Path

from romeo import HARNESS_ROOT
from romeo.close import (HARNESS_UNIT_MARKER, harness_self_checks,
                         payload_check_violations)

TEMPLATE = Path(HARNESS_ROOT) / "core/templates/tech-spec.md"


def _spec(checks, prose=""):
    rows = "\n".join(
        f'  - id: {cid}\n    command: "{cmd}"\n    expect: exit 0' for cid, cmd in checks)
    return f"## 검증 계획\n\n{prose}\n\n```yaml\nrequired_checks:\n{rows}\n```\n"


class TemplateRule(unittest.TestCase):
    """규칙이 템플릿에 실재한다 — 이것이 없으면 앞으로 만들어지는 spec 이 규칙을 보지 못한다."""

    def test_template_states_the_rule(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("페이로드 단위의 검사는 그 단위의 산출물만 대상으로 한다", text)
        self.assertIn("하네스 자신의 테스트나 자기 검사를 넣지 않는다", text)

    def test_template_names_the_exception(self):
        self.assertIn(HARNESS_UNIT_MARKER, TEMPLATE.read_text(encoding="utf-8"))


class PayloadSpecDetection(unittest.TestCase):
    """규칙을 어긴 페이로드 spec 예시를 잡아낸다."""

    def test_harness_unittest_in_payload_spec_is_caught(self):
        body = _spec([("check-1", "npm test"),
                      ("check-2", "python3 -m unittest discover -s tests")])
        self.assertEqual(payload_check_violations(body), ["check-2"])

    def test_harness_self_commands_are_caught(self):
        body = _spec([("check-1", "./bin/romeo compile --check"),
                      ("check-2", "./bin/romeo doctor"),
                      ("check-3", "./bin/romeo fixtures parity --report"),
                      ("check-4", "./bin/romeo vendor"),
                      ("check-5", "./bin/romeo notices --check"),
                      ("check-6", "python3 -m unittest tests.test_run_unit")])
        self.assertEqual(payload_check_violations(body),
                         ["check-1", "check-2", "check-3", "check-4", "check-5", "check-6"])

    def test_payload_own_checks_pass(self):
        body = _spec([("check-1", "npm test"),
                      ("check-2", "npm run lint"),
                      ("check-3", "pytest src/tests")])
        self.assertEqual(payload_check_violations(body), [])

    def test_harness_unit_declares_the_exception(self):
        """하네스 저장소 자신이 대상인 단위는 예외다 — 선언 한 줄이 있으면 위반이 아니다."""
        checks = [("check-1", "python3 -m unittest discover -s tests")]
        self.assertEqual(payload_check_violations(_spec(checks)), ["check-1"])
        declared = _spec(checks, prose="이 단위는 하네스 저장소 자신이 대상이므로 하네스 테스트가 정당한 검사다.")
        self.assertEqual(payload_check_violations(declared), [])

    def test_detector_is_independent_of_the_exception(self):
        """`harness_self_checks` 는 무엇이 하네스 검사인지만 말한다 — 예외 판정은 하지 않는다."""
        plan = [{"id": "check-1", "command": "python3 -m unittest discover -s tests"}]
        self.assertEqual(harness_self_checks(plan), ["check-1"])

    def test_no_checks_block_is_not_a_violation(self):
        self.assertEqual(payload_check_violations("## 검증 계획\n\n(없음)\n"), [])


class ThisRepoIsTheException(unittest.TestCase):
    """이 저장소의 이 작업 단위 자신이 예외를 선언했는지 — 규칙이 자기에게도 적용된다."""

    def test_tuneup_spec_declares_harness_unit(self):
        spec = (Path(HARNESS_ROOT)
                / "docs/work/feat-20260830-harness-tuneup-6xcq/spec.md")
        if not spec.exists():
            self.skipTest("이 작업 단위 문서가 없는 체크아웃")
        self.assertEqual(payload_check_violations(spec.read_text(encoding="utf-8")), [])


if __name__ == "__main__":
    unittest.main()
