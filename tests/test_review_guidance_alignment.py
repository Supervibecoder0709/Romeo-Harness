"""검토자 절차를 **안내하는** 자리가 종료 검사가 **요구하는** 자리를 따라가는지 본다 — Q-96.

요구는 `romeo/close.py` 가 소유한다 — 방어 검사 라벨(`DEFENSIVE_LABELS`)과 봉인 명령(`SEAL_COMMAND`).
안내(절차 문서)가 그 둘을 모르면 **지시대로 따른 실행이 미검증으로 막히고, RUNBOOK 을 따로 찾아 읽은 실행만
통과한다** — 요구하는 자리와 보는 자리가 어긋난 AGENTS.core §11 의 모양이다.
2026-09-09 관통이 그 두 자리에서 각각 한 번씩 막혔다.

**라벨도 명령도 이 파일에 적지 않는다.** 정본에서 읽고, 종료 검사가 쓰는 것과 같은 값으로 대조한다 —
적는 순간 정본이 둘이 되고, 코드를 바꾼 커밋이 "요구는 이것인데 안내는 저것" 을 다시 만든다.
이름을 두 조각으로 나눠 고정하는 것도 같은 중복이다.

**반례는 빈 값이 아니라 그럴듯한 거짓 값이다**(§11). 여기 반례 넷은 형태가 그럴듯하고 내용이 거짓이다 —
라벨 한 줄이 빠진 안내 · 정본을 바꿔쳐도 통과하는 사본형 안내 · 실재하지 않는 명령을 가리키는 정본 ·
등록은 됐지만 안내에 없는 명령.
"""
import argparse
import os
import re
import unittest
from pathlib import Path

from romeo.cli import build_parser
from romeo.close import DEFENSIVE_LABELS, SEAL_COMMAND
from romeo.util import project_root

REPO = project_root(Path(__file__).parent)

#: 검토자 절차를 안내하는 자리. 코어 절차 하나와 두 런타임 매핑이다.
GUIDANCE_FILES = (
    "core/workflows/review/SKILL.md",
    "adapters/claude/workflows/review.md",
    "adapters/codex/workflows/review.md",
)
#: 루트 명령의 이름. 안내는 `bin/romeo` 또는 `romeo` 로 그것을 부른다.
ROOT_COMMAND = "romeo"


def registered(parser, command):
    """`command` 가 이 파서에 서브커맨드 경로로 실제 등록돼 있는가.

    정본이 실재하지 않는 이름을 가리키면 안내를 대조할 것도 없다 — 그때는 안내가 아니라 정본이 틀렸다."""
    node = parser
    for name in command:
        sub = next((a for a in node._actions
                    if isinstance(a, argparse._SubParsersAction)), None)
        if sub is None or name not in sub.choices:
            return False
        node = sub.choices[name]
    return True


def _ticks(text):
    """문서에서 백틱으로 감싼 조각 전부. 산문 언급이 아니라 **실행 지시**만 세기 위해서다."""
    return re.findall(r"`([^`]+)`", text)


#: 정본이 실재하지 않는 이름을 가리킬 때 대조 대신 돌려주는 값.
UNREGISTERED = "UNREGISTERED"


def missing(paths, labels, command, root=REPO):
    """안내가 담지 않은 `(문서, 빠진 것)` 쌍. 백틱 안에 있는 것만 담긴 것으로 본다."""
    want = list(labels) + [" ".join(command)]
    out = []
    for rel in paths:
        ticks = _ticks((root / rel).read_text(encoding="utf-8"))
        for item in want:
            if not any(item in tick for tick in ticks):
                out.append((rel, item))
    return sorted(out)


def check(paths, labels, command, parser=None, root=REPO):
    """**등록 확인을 먼저 하고, 실패하면 안내 대조로 넘어가지 않는다**(AC-2).

    정본이 CLI 에 없는 이름을 가리키면 안내를 대조할 것이 없다 — 그때 틀린 것은 안내가 아니라 정본이다.
    `(UNREGISTERED, 명령)` 한 건을 돌려주고 문서를 한 글자도 읽지 않는다."""
    if not registered(parser or build_parser(), command):
        return [(UNREGISTERED, " ".join(command))]
    return missing(paths, labels, command, root=root)


class TestSealCommandIsReal(unittest.TestCase):
    def test_registered_in_cli(self):
        """정본이 가리키는 명령이 CLI 에 실제로 있다."""
        self.assertTrue(registered(build_parser(), SEAL_COMMAND),
                        f"SEAL_COMMAND {SEAL_COMMAND} 가 CLI 파서에 등록돼 있지 않다")

    def test_unregistered_command_stops_before_reading_documents(self):
        """AC-2 — 등록 확인이 실패하면 안내 대조로 **넘어가지 않는다**.

        문서를 읽지 않았다는 것은 반환값이 아니라 **읽을 수 없는 루트**로 보인다 —
        `check` 가 문서를 열려 했다면 거기서 예외가 오른다."""
        absent = (SEAL_COMMAND[0], "zzz-no-such-sub")
        out = check(GUIDANCE_FILES, DEFENSIVE_LABELS, absent, root=Path("/zzz-no-such-root"))
        self.assertEqual([(UNREGISTERED, " ".join(absent))], out)

    def test_registered_command_does_read_documents(self):
        """여집합 — 등록된 명령이면 대조로 넘어간다(그래서 읽을 수 없는 루트에서는 실패한다)."""
        with self.assertRaises(OSError):
            check(GUIDANCE_FILES, DEFENSIVE_LABELS, SEAL_COMMAND, root=Path("/zzz-no-such-root"))

    def test_absent_command_is_caught(self):
        """AC-3 ③ — 등록되지 않은 이름은 등록 확인에서 걸린다."""
        self.assertFalse(registered(build_parser(), (SEAL_COMMAND[0], "zzz-no-such-sub")))
        self.assertFalse(registered(build_parser(), ("zzz-no-such-root",) + SEAL_COMMAND[1:]))


class TestGuidanceFollowsCode(unittest.TestCase):
    def test_current_guidance_is_complete(self):
        """AC-2 — 안내 셋이 라벨 둘과 봉인 명령을 백틱 안에 담는다."""
        self.assertEqual([], check(GUIDANCE_FILES, DEFENSIVE_LABELS, SEAL_COMMAND))

    def test_root_command_is_named(self):
        """봉인 명령이 루트 명령과 함께 적혀야 실행할 수 있다."""
        full = f"{ROOT_COMMAND} " + " ".join(SEAL_COMMAND)
        for rel in GUIDANCE_FILES:
            ticks = _ticks((REPO / rel).read_text(encoding="utf-8"))
            self.assertTrue(any(full in tick for tick in ticks),
                            f"{rel} 에 «{full}» 형태의 실행 지시가 없다")

    def test_removed_label_is_reported(self):
        """AC-3 ① — 한 문서에서 라벨 하나를 지운 사본은 그 문서의 쌍 하나를 낸다.

        줄 단위로 지우지 않는다 — 안내가 두 라벨을 한 문장에 담으면 줄 삭제가 둘 다 지워
        「하나가 빠졌을 때」를 보이지 못한다. 그 라벨 문자열만 지운다."""
        import shutil, tempfile
        target = GUIDANCE_FILES[0]
        gone = DEFENSIVE_LABELS[0]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in GUIDANCE_FILES:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(REPO / rel, root / rel)
            text = (root / target).read_text(encoding="utf-8")
            (root / target).write_text(text.replace(gone, "지운-자리"), encoding="utf-8")

            pairs = missing(GUIDANCE_FILES, DEFENSIVE_LABELS, SEAL_COMMAND, root=root)
            self.assertEqual([(target, gone)], pairs)
            shutil.copy(REPO / target, root / target)
            self.assertEqual([], missing(GUIDANCE_FILES, DEFENSIVE_LABELS, SEAL_COMMAND, root=root))

    def test_swapped_labels_report_every_document(self):
        """AC-3 ② — 정본을 안내에 없는 값으로 바꿔치면 문서 셋 전부가 쌍을 낸다.

        안내에 값을 복사해 둔 사본형 검사는 바꿔쳐도 통과한다 — 그것이 여기서 갈린다."""
        fake = ("zzz-tree-before-absent", "zzz-tree-after-absent")
        pairs = missing(GUIDANCE_FILES, fake, SEAL_COMMAND)
        self.assertEqual(sorted((rel, f) for rel in GUIDANCE_FILES for f in fake), pairs)

    def test_swapped_command_reports_every_document(self):
        """AC-3 ④ — 파서에 등록은 됐지만 안내에 없는 명령으로 바꿔치면 문서 셋 전부가 쌍을 낸다."""
        other = ("envelope", "build")
        self.assertTrue(registered(build_parser(), other), "이 사례는 등록된 다른 명령이라야 뜻이 있다")
        pairs = missing(GUIDANCE_FILES, DEFENSIVE_LABELS, other)
        self.assertEqual(sorted((rel, " ".join(other)) for rel in GUIDANCE_FILES), pairs)


class TestNoCopiedConstants(unittest.TestCase):
    def test_this_file_does_not_restate_the_source(self):
        """AC-1 — 정본을 이 파일에 적지 않는다. 두 조각으로 나눠 고정하는 것도 중복이다."""
        source = Path(__file__).read_text(encoding="utf-8")
        body = source.split(chr(34) * 3, 2)[2]    # 모듈 docstring 은 설명이다
        # 금지 목록도 **정본에서 만든다** — 여기 적으면 그것 자체가 사본이다.
        banned = [os.path.commonprefix(DEFENSIVE_LABELS),      # 라벨의 공통 접두
                  " ".join(SEAL_COMMAND)]                      # 명령 전체
        banned += [chr(34) + part + chr(34) for part in SEAL_COMMAND]   # 조각으로 나눠 고정하는 것
        found = [b for b in banned if b in body]
        self.assertEqual([], found, f"정본을 복사했다: {found}")


if __name__ == "__main__":
    unittest.main()
