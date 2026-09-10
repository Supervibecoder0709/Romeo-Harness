"""부착 정본을 읽는 자리.

**정본은 이 파일이 아니다** — `scenarios/10-attach-payload.md` 의 「놓는 것」 절이다.
여기 있는 것은 그 문서를 읽는 코드뿐이고, 목록을 이 파일에 못 박으면 문서와 코드가 갈린다.
갈린 뒤에는 어느 쪽이 요구인지 말할 수 없다(AGENTS.core §11 — 요구하는 자리와 보는 자리를 같게 둔다).

이 코드는 원래 `tests/test_attach_runbook.py` 안에 있었다. 꺼낸 이유는 **읽는 자리가 하나 더 필요해서**다 —
`doctor` 가 같은 정본을 읽어야 부착 여부를 판정할 수 있는데, 프로덕션 코드가 테스트 모듈을 import 할 수는 없다.
목록 자체는 옮기지 않았다.
"""
import re
from pathlib import Path

from . import HARNESS_ROOT

#: 정본이 사는 자리. 하네스 저장소 기준의 상대 경로다.
RUNBOOK_REL = "scenarios/10-attach-payload.md"

#: 정본 안에서 목록이 사는 절.
PLACE_HEADING = "## 놓는 것"

#: `- ` 로 시작하고 백틱 경로가 첫 토큰인 줄만 필수 경로로 읽는다. 런북의 「목록의 문법」과 같은 규칙이다.
_ITEM = re.compile(r"^-\s+`([^`]+)`")


def runbook_path(harness_root=None):
    """정본 파일의 경로. `harness_root` 는 **명령을 실행한 하네스 저장소**다 — 판정 대상 루트가 아니다.

    대상 루트의 사본을 읽으면 대상이 자기 요구를 낮출 수 있다.
    """
    return Path(harness_root or HARNESS_ROOT) / RUNBOOK_REL


def required_paths(runbook=None):
    """정본의 「놓는 것」 절에서 필수 경로 목록을 읽는다. 문서가 목록의 주인이다."""
    path = Path(runbook) if runbook else runbook_path()
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == PLACE_HEADING)
    except StopIteration:
        raise AssertionError(f"{path}: '{PLACE_HEADING}' 절이 없다 — 목록을 읽을 자리가 없다")
    out = []
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        m = _ITEM.match(ln)
        if m:
            out.append(m.group(1))
    if not out:
        raise AssertionError(f"{path}: '{PLACE_HEADING}' 절에 백틱 경로 목록이 없다")
    return out


def present(target: Path) -> bool:
    """**부재를 통과로 읽지 않는다.** 이름만 있는 빈 디렉터리·빈 파일은 놓인 것이 아니다."""
    if target.is_symlink() and not target.exists():
        return False
    if target.is_dir():
        return any(p.is_file() and p.stat().st_size > 0 for p in target.rglob("*"))
    if target.is_file():
        return target.stat().st_size > 0
    return False


def missing(root, runbook=None):
    """`root` 에 놓이지 않은 필수 경로를 정본 순서 그대로 돌려준다. 빈 목록이 부착됨이다."""
    root = Path(root)
    return [rel for rel in required_paths(runbook) if not present(root / rel.rstrip("/"))]
