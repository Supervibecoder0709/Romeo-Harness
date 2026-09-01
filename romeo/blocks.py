"""차단(blocks) 집행 — 라우터가 계산한 차단 id 마다 **무엇이 충족인가**를 판정한다.

라우터는 분류에서 차단을 계산해 카드에 인쇄까지 했지만, 그 글자가 막는 것은 없었다(2026-09-01 실측).
집행 지점은 둘이다 — **승인**(`romeo approve`)과 **종료**(`romeo close`). 승인에서 막는 이유는
승인이 구현을 여는 사건이기 때문이고(D-27), 종료에서 다시 보는 이유는 승인 뒤에 조건이 무너질 수 있기 때문이다.

카탈로그(`core/policy/packages.yaml` 의 `blocks:`)와 이 파일의 `BLOCK_CHECKS` 는 **같은 집합**이어야 한다 —
`romeo.policy.load_policy` 가 로드 시점에 대조하고, 어긋나면 정책을 읽지 못한다. 정책표에 차단을 적고
집행을 잊으면(또는 그 반대) 조용히 아무것도 막지 않는 차단이 다시 생기기 때문이다.

이 모듈은 `romeo.policy` 를 import 하지 않는다 — policy 가 이 모듈을 import 하므로 순환이 된다.
필요한 정책 조각(`pk`)은 호출자가 넘긴다."""
import re
from pathlib import Path

import yaml

from . import frontmatter

#: 차단이 걸릴 수 있는 집행 지점. 카탈로그의 `enforced_at` 은 이 값만 쓸 수 있다.
ENFORCE_POINTS = ("approve", "close")

CHECKS_BLOCK_RE = re.compile(r"```yaml\s*\n(required_checks:.*?)\n```", re.S)


def required_checks(body):
    """spec 본문의 검증 계획 블록에서 required_checks 목록을 읽는다. 없으면 빈 목록."""
    m = CHECKS_BLOCK_RE.search(body or "")
    if not m:
        return []
    data = yaml.safe_load(m.group(1)) or {}
    return data.get("required_checks") or []


def section(body, title):
    """`## <title>` 절의 본문. 절이 없으면 None — '없다' 와 '비었다' 를 구분한다."""
    lines = (body or "").split("\n")
    for i, ln in enumerate(lines):
        if ln.strip() == f"## {title}":
            j = i + 1
            while j < len(lines) and not lines[j].startswith("## "):
                j += 1
            return "\n".join(lines[i + 1:j])
    return None


def _filled(text):
    return bool(text) and "NEEDS_INPUT" not in text and any(ln.strip() for ln in text.split("\n"))


def _section_state(text, where, title):
    """절 하나가 '있고 채워졌는가'. 충족이면 None, 아니면 막는 이유 한 문장."""
    if text is None:
        return f"{where} 에 「{title}」 절이 없다"
    if "NEEDS_INPUT" in text:
        return f"{where} 의 「{title}」 절에 NEEDS_INPUT 이 남아 있다"
    if not any(ln.strip() for ln in text.split("\n")):
        return f"{where} 의 「{title}」 절이 비어 있다"
    return None


AC_RE = re.compile(r"^\s*- \[[ xX]\]\s*\S", re.M)


def _spec_ready(unit_dir, fm, body):
    """승인 창구(확인란)가 채워졌고, 그 안에 수용 기준이 적혀 있다.

    검증 계획(`required_checks`)이 비어 있는 것은 여기서 막지 않는다 — 그것은 완료 판정의 문제이고
    `romeo close` 가 `REQUIRED_CHECK` 를 **UNVERIFIED** 로 인쇄해 done 을 세우지 않는다. 같은 사실을
    두 자리에서 서로 다른 이름으로 막으면 어느 쪽이 판정했는지 읽히지 않는다."""
    why = _section_state(section(body, "확인란"), "spec.md", "확인란")
    if why:
        return False, f"{why} — 사용자가 이것만 읽고 승인한다(D-60)"
    ac = AC_RE.findall(section(body, "확인란") or "")
    if not ac:
        return False, ("확인란에 수용 기준 항목이 없다 — 승인 창구에 '무엇이 되면 끝인가' 가 적혀 있지 않으면 "
                       "사용자가 승인할 대상이 없다(D-60)")
    return True, f"확인란이 채워졌고 수용 기준 {len(ac)}건"


def _milestone_plan(unit_dir, fm, body):
    """T2 는 Charter 의 「마일스톤 계획」이 채워진 뒤에만 열린다."""
    charter = Path(unit_dir) / "charter.md"
    if not charter.is_file():
        return False, "charter.md 가 없다 — T2 는 Charter 부터 만든다(문서 패키지 [charter, brief, spec])"
    cfm, cbody = frontmatter.split(charter.read_text(encoding="utf-8"))
    why = _section_state(section(cbody, "마일스톤 계획"), "charter.md", "마일스톤 계획")
    if why:
        return False, f"{why} — 마일스톤 없이 이니셔티브를 열지 않는다"
    return True, "charter.md 의 「마일스톤 계획」 절이 채워졌다"


def _discovery_result(unit_dir, fm, body):
    """조사 단위는 조사 산출물이 `inputs:` 로 붙기 전에는 구현으로 넘어가지 않는다."""
    items = [str(x).strip() for x in ((fm or {}).get("inputs") or []) if str(x).strip()]
    if not items:
        return False, ("frontmatter 의 inputs: 가 비어 있다 — 조사 결과가 기록되기 전에는 구현 dispatch 를 막는다. "
                       "조사 산출물은 작업 단위로 복사하지 않고 inputs: 링크로만 붙인다(K-62)")
    return True, f"inputs: {len(items)}건 — {', '.join(items[:3])}" + (" …" if len(items) > 3 else "")


def _approval_gate(unit_dir, fm, body):
    """hard gate 영역은 영향 범위·백업·복구가 적힌 뒤에만 승인 대상이 된다(K-50)."""
    why = _section_state(section(body, "위험·백업·복구"), "spec.md", "위험·백업·복구")
    if why:
        return False, f"{why} — 게이트가 걸린 단위는 영향 범위·사전 백업·복구 방법 없이 승인하지 않는다(K-50)"
    gates = ", ".join((fm or {}).get("gates") or []) or "없음"
    return True, f"게이트 {gates} — 「위험·백업·복구」 절이 채워졌다"


#: 차단 id → 충족 판정. 카탈로그와 **같은 집합**이어야 한다(load_policy 가 대조한다).
BLOCK_CHECKS = {
    "spec-ready": _spec_ready,
    "milestone-plan": _milestone_plan,
    "discovery-result": _discovery_result,
    "approval-gate": _approval_gate,
}


def catalog(pk):
    return (pk or {}).get("blocks") or {}


def used_blocks(pk):
    """기본 패키지와 오버레이가 실제로 거는 차단 id 전부."""
    pk = pk or {}
    ids = []
    for base in (pk.get("base") or {}).values():
        for b in (base or {}).get("blocks") or []:
            if b not in ids:
                ids.append(b)
    for o in pk.get("overlays") or []:
        for b in (o or {}).get("add_blocks") or []:
            if b not in ids:
                ids.append(b)
    return ids


def catalog_defects(pk):
    """카탈로그·집행 매핑·실사용 세 집합의 어긋남. 빈 목록이면 성립한다.

    `load_policy` 가 이것을 읽어 하나라도 있으면 정책을 읽지 않는다 — 차단을 적고 집행을 잊는 것이
    이 결함의 원래 모양이었으므로, 같은 모양이 다시 서지 않게 **로드 자체**를 막는다."""
    cat, defects = catalog(pk), []
    if not cat:
        return ["core/policy/packages.yaml 에 blocks: 카탈로그가 없다 — 차단마다 이름·집행 지점·충족 조건을 적는다"]
    for bid, meta in sorted(cat.items()):
        if not isinstance(meta, dict):
            defects.append(f"blocks.{bid}: 맵이 아니다")
            continue
        for key in ("title", "enforced_at", "requires"):
            if not meta.get(key):
                defects.append(f"blocks.{bid}: {key} 가 없다")
        points = meta.get("enforced_at")
        if isinstance(points, list):
            for p in points:
                if p not in ENFORCE_POINTS:
                    defects.append(f"blocks.{bid}.enforced_at: 모르는 집행 지점 {p!r} (허용: {' · '.join(ENFORCE_POINTS)})")
        elif points is not None:
            defects.append(f"blocks.{bid}.enforced_at: 목록이 아니다")
    for bid in sorted(set(cat) - set(BLOCK_CHECKS)):
        defects.append(f"blocks.{bid}: 카탈로그에는 있는데 집행 코드(romeo/blocks.py 의 BLOCK_CHECKS)가 없다 — "
                       f"아무것도 막지 않는 차단이 된다")
    for bid in sorted(set(BLOCK_CHECKS) - set(cat)):
        defects.append(f"BLOCK_CHECKS.{bid}: 집행 코드는 있는데 카탈로그(core/policy/packages.yaml 의 blocks:)에 없다 — "
                       f"무엇을 왜 막는지 읽을 자리가 없다")
    for bid in used_blocks(pk):
        if bid not in cat:
            defects.append(f"base·overlays 가 거는 차단 {bid!r} 가 카탈로그에 없다")
        if bid not in BLOCK_CHECKS:
            defects.append(f"base·overlays 가 거는 차단 {bid!r} 에 집행 코드가 없다")
    return defects


def enforced_at(pk, block_ids, point):
    """이 집행 지점에 걸리는 차단만 골라 순서대로."""
    cat = catalog(pk)
    return [b for b in (block_ids or []) if point in ((cat.get(b) or {}).get("enforced_at") or [])]


def satisfied(block_id, unit_dir, fm, body):
    """차단 하나의 충족 판정 → `(ok, reason)`. 집행 코드가 없는 id 는 조용히 통과시키지 않는다."""
    fn = BLOCK_CHECKS.get(block_id)
    if fn is None:
        raise KeyError(f"집행 코드가 없는 차단 id: {block_id}")
    return fn(Path(unit_dir), fm or {}, body or "")


def evaluate(pk, block_ids, point, unit_dir, fm, body):
    """이 집행 지점에 걸린 차단 전부의 판정 → `[(block_id, ok, reason)]`."""
    return [(b, *satisfied(b, unit_dir, fm, body)) for b in enforced_at(pk, block_ids, point)]
