"""시크릿 마스킹(`romeo.util.mask_secrets`)의 양쪽 실패를 다 본다.

마스킹은 두 방향으로 틀릴 수 있고 **둘 다 조용하지 않다.**
- 놓치면(미탐) 크리덴셜이 증거에 남는다(K-23).
- 과하게 잡으면(오탐) 명령 문자열이 훼손된 채 증거에 저장되는데, 종료 검사는 검증 계획의
  **원문**으로 정확 조회하므로(`romeo/close.py`) 실제로 exit 0 인 검사가 "evidence 에 명령 없음"
  으로 떨어져 완료가 서지 않는다. 2026-08-31 `run_6165c4796868` 이 파일명 `skills-before` 하나로
  이렇게 막혔다 — 그때까지 이 함수에는 테스트가 하나도 없었다.
"""
import unittest

from romeo.util import mask_secrets

MASKED = "<masked-token>"


class TestMasksRealSecrets(unittest.TestCase):
    """진짜 크리덴셜은 반드시 가려진다. 접두사마다 실제 형태를 그대로 쓴다."""

    def test_prefixed_tokens_are_masked(self):
        for token in ("sk-proj-abcdefghijklmnop", "sk_live_abcdefghijklmnop",
                      "ghp_0123456789abcdefghij", "gho_0123456789abcdefghij",
                      "ghu_0123456789abcdefghij", "ghs_0123456789abcdefghij",
                      "xoxb-1234567890-abcdefghij", "xoxp-1234567890-abcdefghij"):
            with self.subTest(token=token):
                self.assertEqual(mask_secrets(token), MASKED)

    def test_aws_access_key_is_masked(self):
        # 구분자가 없는 유일한 형태다. 그래서 별도 규칙으로 두고, 여기서 그것을 확인한다.
        self.assertEqual(mask_secrets("AKIAIOSFODNN7EXAMPLE"), MASKED)

    def test_token_inside_a_command_is_masked(self):
        out = mask_secrets("curl -H 'X-Key: ghp_0123456789abcdefghij' https://example.test")
        self.assertNotIn("ghp_0123456789abcdefghij", out)
        self.assertIn(MASKED, out)

    def test_labelled_values_are_masked(self):
        for text in ("api_key: hunter2", "API-KEY=hunter2", "password: hunter2",
                     "secret=hunter2", "Authorization: Bearer zzz"):
            with self.subTest(text=text):
                self.assertNotIn("hunter2", mask_secrets(text))
                self.assertIn("<masked>", mask_secrets(text))


class TestDoesNotMaskOrdinaryText(unittest.TestCase):
    """평범한 경로·이름을 건드리지 않는다. 건드리면 증거의 명령 대조가 깨진다."""

    def test_filenames_that_merely_start_with_a_prefix_survive(self):
        # 'skills-before' 는 sk + 11자다. 구분자를 요구하지 않던 옛 패턴이 이것을 토큰으로 잡았다.
        for text in ("docs/work/u/evidence/skills-before.sha256",
                     "docs/work/u/evidence/home-skills-before.txt",
                     "docs/skeleton-first-notes.md", "sketchbook-layout.png",
                     "ghostwriter-config.yaml", "skips_validation_flag"):
            with self.subTest(text=text):
                self.assertEqual(mask_secrets(text), text)

    def test_the_exact_check_commands_of_a_real_unit_survive(self):
        # 종료 검사가 대조하는 것은 이 문자열들이다. 한 글자라도 바뀌면 조회가 실패한다.
        for cmd in ("shasum -a 256 -c docs/work/u/evidence/skills-before.sha256",
                    'find "$HOME/.codex/skills" -type f | sort | diff - '
                    "docs/work/u/evidence/home-skills-before.txt"):
            with self.subTest(cmd=cmd):
                self.assertEqual(mask_secrets(cmd), cmd)

    def test_harness_commands_survive(self):
        for cmd in ("bin/romeo doctor --strict --scope repository",
                    "python3 -m unittest discover -s tests", "bin/romeo compile --check"):
            with self.subTest(cmd=cmd):
                self.assertEqual(mask_secrets(cmd), cmd)


if __name__ == "__main__":
    unittest.main()
