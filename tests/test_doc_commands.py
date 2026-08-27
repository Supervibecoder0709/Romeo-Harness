"""문서에 적힌 romeo 명령이 실제 CLI 계약과 맞는지.

문서와 파서가 어긋나면 에이전트가 절차를 그대로 실행했을 때 argparse 단계에서 멈춘다.
테스트·compile check 가 전부 PASS 해도 수직 흐름은 닫히지 않는다 — 실제로 그 상태가 있었다.
(Codex 독립 리뷰 F-05, 2026-08-28)
"""
import re
import unittest
from pathlib import Path

from romeo.cli import build_parser
from romeo.util import project_root

REPO = project_root(Path(__file__).parent)

# 하네스가 소유한 문서만 본다. vendor/ 원문과 그 투영본은 romeo 명령을 쓰지 않는다.
DOC_GLOBS = [
    "core/workflows/*/SKILL.md",
    "adapters/*/workflows/*.md",
    "core/templates/*.md",
]
RUNTIME_SKILL_GLOBS = [".claude/skills/plan/SKILL.md", ".claude/skills/plan-close/SKILL.md",
                       ".agents/skills/plan/SKILL.md", ".agents/skills/plan-close/SKILL.md"]

# 백틱 안의 내용만 명령으로 본다. 산문 속 이름 언급까지 검사하면 오탐이 난다.
CODE_RE = re.compile(r"`([^`]+)`")
CMD_RE = re.compile(r"^(?:bin/)?romeo\s+([a-z-]+)\s*(.*)$")


def parser_map():
    """서브커맨드 → 허용 옵션 문자열 집합."""
    p = build_parser()
    subs = {}
    for action in p._actions:
        if not hasattr(action, "choices") or not action.choices:
            continue
        for name, sub in action.choices.items():
            opts = set()
            nested = {}
            for a in sub._actions:
                opts.update(a.option_strings)
                if hasattr(a, "choices") and a.choices and isinstance(a.choices, dict):
                    for n2, s2 in a.choices.items():
                        nested[n2] = {o for a2 in s2._actions for o in a2.option_strings}
            subs[name] = {"opts": opts, "nested": nested}
    return subs


def doc_files():
    files = []
    for g in DOC_GLOBS:
        files += sorted(REPO.glob(g))
    files += [REPO / r for r in RUNTIME_SKILL_GLOBS if (REPO / r).exists()]
    return files


def commands_in(path):
    """(서브커맨드, 플래그, 하위동작, 인자가 있는가, 원문줄)."""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        for snippet in CODE_RE.findall(line):
            m = CMD_RE.match(snippet.strip())
            if not m:
                continue
            sub, rest = m.group(1), (m.group(2) or "").strip()
            flags = re.findall(r"--[a-z-]+", rest)
            # <id> 같은 플레이스홀더와 값은 버리고, 하위 동작 이름만 남긴다
            words = [w for w in rest.split()
                     if re.fullmatch(r"[a-z-]+", w) and not w.startswith("--")]
            out.append((sub, flags, words, bool(rest), line.strip()))
    return out


class TestDocumentedCommands(unittest.TestCase):
    def test_documents_exist(self):
        self.assertGreater(len(doc_files()), 4)

    def test_subcommands_exist(self):
        subs = parser_map()
        bad = []
        for f in doc_files():
            for sub, _flags, _words, _has_args, line in commands_in(f):
                if sub not in subs:
                    bad.append(f"{f.relative_to(REPO)}: 'romeo {sub}' — 그런 서브커맨드가 없다 :: {line}")
        self.assertEqual(bad, [], "\n".join(bad))

    def test_flags_exist_on_their_subcommand(self):
        subs = parser_map()
        bad = []
        for f in doc_files():
            for sub, flags, words, _has_args, line in commands_in(f):
                if sub not in subs:
                    continue
                allowed = set(subs[sub]["opts"])
                for w in words:                      # evidence run / evidence checks 같은 하위 동작
                    if w in subs[sub]["nested"]:
                        allowed |= subs[sub]["nested"][w]
                for fl in flags:
                    if fl not in allowed:
                        bad.append(f"{f.relative_to(REPO)}: 'romeo {sub} {fl}' — 그 옵션이 없다 :: {line}")
        self.assertEqual(bad, [], "\n".join(bad))

    def test_required_options_are_documented(self):
        """필수 옵션을 빠뜨린 예시를 잡는다 — 'romeo close <id>' 가 실제로 그랬다."""
        p = build_parser()
        required = {}
        for action in p._actions:
            if not hasattr(action, "choices") or not action.choices:
                continue
            for name, sub in action.choices.items():
                req = {a.option_strings[0] for a in sub._actions
                       if getattr(a, "required", False) and a.option_strings}
                if req:
                    required[name] = req
        bad = []
        for f in doc_files():
            for sub, flags, _words, has_args, line in commands_in(f):
                # `romeo close` 처럼 인자 없이 이름만 쓴 것은 산문 언급이지 실행 예시가 아니다
                if not has_args:
                    continue
                for need in required.get(sub, set()):
                    if need not in flags:
                        bad.append(f"{f.relative_to(REPO)}: 'romeo {sub}' 에 필수 옵션 {need} 가 없다 :: {line}")
        self.assertEqual(bad, [], "\n".join(bad))


if __name__ == "__main__":
    unittest.main()
