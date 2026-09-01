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

#: 차단이 **막기 시작하는** 사건. 카탈로그의 `enforced_at` 은 이 값 중 **하나**만 쓴다.
#:
#: 어휘가 둘(`approve`·`close`)뿐이던 동안 차단 넷이 전부 `[approve, close]` 로 선언됐고, 그래서 이름이 말하는
#: 사건과 실제로 막는 사건이 갈라졌다 — `discovery-result` 는 "구현 위임을 막는다" 면서 **승인**을 막아
#: 조사 단위가 조사를 시작할 창구를 없앴다(2026-09-01 실측). 어휘를 생애주기 사건에 맞추면 그 갈라짐이 생기지 않는다.
#:
#: `dispatch` 는 작업 계약을 **쓰는** 자리다(`envelope.write_envelope`) — 어느 경로로 돌든 위임은 그것을 지나고,
#: 계약을 **계산만** 하는 `build_envelope` 는 지나지 않는다(종료 검사의 재계산 대조가 그것을 부른다).
#: 반복 중단 게이트가 이미 같은 이유로 같은 자리에 있다.
#:
#: **되돌리기 어려운 실행의 승인은 차단이 아니라 `guards` 가 소유한다**(`core/policy/execution-guards.yaml`) —
#: 승인 기록을 원시 로그로 봉인하고 `close` 가 `GUARD_APPROVED` 로 판정한다. 같은 일을 두 이름으로 하지 않는다.
ENFORCE_POINTS = ("approve", "dispatch", "close")

#: 문서 패키지의 파일 이름. 차단의 `reads:` 와 미완료 검사가 같은 목록을 본다.
DOC_FILES = {"charter": "charter.md", "brief": "brief.md", "spec": "spec.md"}

CHECKS_BLOCK_RE = re.compile(r"```yaml\s*\n(required_checks:.*?)\n```", re.S)


def required_checks(body):
    """spec 본문의 검증 계획 블록에서 required_checks 목록을 읽는다. 없으면 빈 목록."""
    m = CHECKS_BLOCK_RE.search(body or "")
    if not m:
        return []
    data = yaml.safe_load(m.group(1)) or {}
    return data.get("required_checks") or []


def unit_docs(unit_dir):
    """작업 단위 폴더에 **실제로 있는** 패키지 문서 → `[(이름, 경로)]`. 없는 것은 건너뛴다.

    미완료 검사가 spec 하나만 보던 동안 `brief.md` 는 승인·종료 어느 쪽도 읽지 않았고,
    라우터가 필수라고 판정한 절(조사 계획의 첫 마일스톤·UI 상태표·실험 설계)이 T1·T2 에서 그리로 가
    **아무도 읽지 않는 자리**가 됐다. 단위가 클수록 집행이 약해지는 역전이었다(2026-09-01 실측)."""
    out = []
    for name in ("charter", "brief", "spec"):
        p = Path(unit_dir) / DOC_FILES[name]
        if p.is_file():
            out.append((name, p))
    return out


def reads_doc(unit_dir, reads):
    """차단이 선언한 정본 입력 문서를 찾는다. `brief|charter` 는 앞의 것 우선 → `(이름, 경로)`."""
    for name in str(reads or "spec").split("|"):
        name = name.strip()
        p = Path(unit_dir) / DOC_FILES.get(name, "")
        if name in DOC_FILES and p.is_file():
            return name, p
    return None, None


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


def _spec_ready(unit_dir, fm, body, meta=None):
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


def _milestone_plan(unit_dir, fm, body, meta=None):
    """T2 는 Charter 의 「마일스톤 계획」이 채워진 뒤에만 열린다."""
    charter = Path(unit_dir) / "charter.md"
    if not charter.is_file():
        return False, "charter.md 가 없다 — T2 는 Charter 부터 만든다(문서 패키지 [charter, brief, spec])"
    cfm, cbody = frontmatter.split(charter.read_text(encoding="utf-8"))
    why = _section_state(section(cbody, "마일스톤 계획"), "charter.md", "마일스톤 계획")
    if why:
        return False, f"{why} — 마일스톤 없이 이니셔티브를 열지 않는다"
    return True, "charter.md 의 「마일스톤 계획」 절이 채워졌다"


#: 여기서 실재를 확인할 수 없는 바깥 주소. **`mailto:` 는 넣지 않는다** — 조사 산출물이 사는 자리가 아니다.
#: 확인할 수 없는 것과 확인할 필요가 없는 것을 같이 두면, 확인을 건너뛰는 구멍이 넓어진다.
URL_RE = re.compile(r"^https?://", re.I)


def _discovery_result(unit_dir, fm, body, meta=None):
    """조사 단위는 **실재하는** 조사 산출물이 붙기 전에는 구현 위임으로 넘어가지 않는다.

    두 가지가 이 판정의 요점이다.

    **어느 문서를 읽는가.** 카탈로그의 `reads:` 가 정한다(기본 `brief|charter`). 조사 계획이 사는 문서와
    그 결과를 읽는 문서가 같아야 한다 — 계획은 Brief 에 적으라고 하면서 검사는 spec 만 읽던 동안,
    지시대로 Brief 에 붙인 링크는 거부되고 spec 에 아무 문자열이나 넣으면 통과했다(2026-09-01 실측).

    **무엇이 충족인가.** 링크가 가리키는 경로가 실재해야 한다. `inputs:` 가 비었는지만 보던 동안
    `["ㅁㄴㅇㄹ"]` 로 승인이 통과했다 — 그 자리에 글자가 있는지를 본 것이지 그 문장이 참인지를 본 것이 아니다.
    바깥 주소(`http(s)://`)는 여기서 확인할 수 없으므로 통과시키되 이유에 그렇게 적는다.
    `mailto:` 는 통과시키지 않는다 — 조사 산출물이 사는 자리가 아니다."""
    where, path = reads_doc(unit_dir, (meta or {}).get("reads") or "brief|charter")
    if path is None:
        return False, (f"{(meta or {}).get('reads') or 'brief|charter'} 에 해당하는 문서가 작업 단위에 없다 — "
                       f"조사 결과를 어디에 적는지가 정해지지 않으면 무엇을 읽을지도 정해지지 않는다")
    dfm, _ = frontmatter.split(path.read_text(encoding="utf-8"))
    items = [str(x).strip() for x in ((dfm or {}).get("inputs") or []) if str(x).strip()]
    if not items:
        return False, (f"{DOC_FILES[where]} 의 inputs: 가 비어 있다 — 조사 결과가 기록되기 전에는 구현 위임을 막는다. "
                       f"조사 산출물은 작업 단위로 복사하지 않고 inputs: 링크로만 붙인다(K-62)")
    missing = [x for x in items if not URL_RE.match(x) and not (Path(unit_dir) / x.split("#")[0]).exists()]
    if missing:
        return False, (f"{DOC_FILES[where]} 의 inputs: 가 가리키는 경로가 없다: {', '.join(missing[:3])}"
                       + (" …" if len(missing) > 3 else "")
                       + " — 링크가 실재해야 조사 결과다. 있는 척하는 링크는 없는 것보다 나쁘다(K-51)")
    outside = [x for x in items if URL_RE.match(x)]
    note = f" (바깥 주소 {len(outside)}건은 여기서 확인하지 않는다)" if outside else ""
    return True, f"{DOC_FILES[where]} 의 inputs: {len(items)}건 실재 — {', '.join(items[:3])}" + (" …" if len(items) > 3 else "") + note


def _risk_plan_ready(unit_dir, fm, body, meta=None):
    """hard gate 영역은 영향 범위·백업·복구가 적힌 뒤에만 **승인 대상**이 된다(K-50).

    이 차단은 **문서가 준비됐는가**를 본다. 되돌리기 어려운 행동을 **실행해도 되는가**는 보지 않는다 —
    그것은 `guards` 가 승인 기록과 원시 로그 봉인으로 소유하고 `close` 가 `GUARD_APPROVED` 로 판정한다.
    두 가지를 「게이트 승인 준비」라는 한 이름으로 묶는 동안, 사람은 그 이름을 실행 승인으로 읽고
    기계는 절이 비었는지만 봤다."""
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
    "risk-plan-ready": _risk_plan_ready,
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
        for key in ("title", "enforced_at", "requires", "reads"):
            if not meta.get(key):
                defects.append(f"blocks.{bid}: {key} 가 없다")
        points = meta.get("enforced_at")
        if isinstance(points, list):
            for p in points:
                if p not in ENFORCE_POINTS:
                    defects.append(f"blocks.{bid}.enforced_at: 모르는 집행 지점 {p!r} (허용: {' · '.join(ENFORCE_POINTS)})")
            if len(points) != 1:
                defects.append(
                    f"blocks.{bid}.enforced_at: {points!r} — **막기 시작하는 사건 하나**만 적는다. "
                    f"일괄 배치는 이름이 말하는 사건과 실제로 막는 사건을 갈라 놓는다. "
                    f"종료 검사는 걸린 차단을 전부 다시 보므로(backstop) 여기에 close 를 더 적을 필요가 없다")
        elif points is not None:
            defects.append(f"blocks.{bid}.enforced_at: 목록이 아니다")
        reads = meta.get("reads")
        if reads and any(n.strip() not in DOC_FILES for n in str(reads).split("|")):
            defects.append(f"blocks.{bid}.reads: 모르는 문서 {reads!r} (허용: {' · '.join(DOC_FILES)}, 여러 개는 `brief|charter`)")
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


SECTION_ENFORCEMENT = ("open-loop", "advisory")


def section_defects(pk):
    """정책표의 절마다 **누가 그것을 집행하는가**가 선언돼 있고, 그 선언이 실제와 맞는가.

    라우터는 `add_sections` 로 절을 요구할 수 있는데 집행은 자기가 읽는 문서만 본다. 그래서
    "라우터가 필수라고 판정했는데 아무도 읽지 않는 절" 이 생겼다 — `blocks` 에서 닫은 결함이
    `sections` 로 자리만 옮겨 앉은 것이다. 요구하는 집합과 집행하는 집합을 **로드 시점에** 맞춰 본다.

    허용 값:

    - `open-loop` — 미완료 토큰 검사가 본다. 검사는 문서 패키지 전체를 보므로 어느 문서에 있어도 된다.
    - `block:<id>` — 그 차단이 본다. 그 차단의 `reads:` 가 이 절이 들어가는 문서를 포함해야 한다.
    - `advisory` — **아무도 읽지 않는다고 명시적으로 선언한다.** 안내일 뿐이라고 적는 것과
      적지 않아서 아무도 안 읽는 것은 다르다. 앞은 결정이고 뒤는 사고다."""
    cat, defects = catalog(pk), []
    for sid, meta in sorted(((pk or {}).get("sections") or {}).items()):
        if not isinstance(meta, dict):
            defects.append(f"sections.{sid}: 맵이 아니다")
            continue
        rules = meta.get("enforcement")
        if not rules:
            defects.append(f"sections.{sid}: enforcement 가 없다 — 누가 이 절을 집행하는지 적지 않으면 "
                           f"라우터가 요구해도 아무도 읽지 않는 절이 된다. "
                           f"허용: {' · '.join(SECTION_ENFORCEMENT)} · block:<차단 id>")
            continue
        if not isinstance(rules, list):
            defects.append(f"sections.{sid}.enforcement: 목록이 아니다")
            continue
        docs = {meta.get("doc"), meta.get("fallback_doc")} - {None}
        for r in rules:
            r = str(r)
            if r in SECTION_ENFORCEMENT:
                continue
            if not r.startswith("block:"):
                defects.append(f"sections.{sid}.enforcement: 모르는 값 {r!r} "
                               f"(허용: {' · '.join(SECTION_ENFORCEMENT)} · block:<차단 id>)")
                continue
            bid = r.split(":", 1)[1]
            bmeta = cat.get(bid)
            if bmeta is None:
                defects.append(f"sections.{sid}.enforcement: {r} — 그런 차단이 카탈로그에 없다")
                continue
            reading = {n.strip() for n in str(bmeta.get("reads") or "").split("|")}
            # 절이 **들어갈 수 있는 모든 문서**를 그 차단이 읽어야 한다(doc 과 fallback_doc 둘 다).
            # 하나라도 읽지 않으면 그 라우팅에서는 아무도 읽지 않는 절이 된다 — 정확히 이 결함의 모양이다.
            unread = docs - reading
            if unread:
                defects.append(f"sections.{sid}.enforcement: {r} — 그 차단은 {sorted(reading)} 를 읽는데 "
                               f"이 절은 {sorted(unread)} 에도 들어간다. 읽지 않는 차단은 집행이 아니다")
    return defects


def enforced_at(pk, block_ids, point):
    """이 집행 지점에서 **막는** 차단만 골라 순서대로.

    `close` 는 예외로 걸린 차단을 **전부** 돌려준다. 막기 시작하는 사건은 하나지만 종료는 backstop 이다 —
    승인이나 위임 뒤에 조건이 무너지는 것(조사 링크를 지우거나 마일스톤 절을 비우는 것)을 잡을 자리가
    그것 하나뿐이기 때문이다."""
    if point == "close":
        return list(block_ids or [])
    cat = catalog(pk)
    return [b for b in (block_ids or []) if point in ((cat.get(b) or {}).get("enforced_at") or [])]


def satisfied(block_id, unit_dir, fm, body, meta=None):
    """차단 하나의 충족 판정 → `(ok, reason)`. 집행 코드가 없는 id 는 조용히 통과시키지 않는다."""
    fn = BLOCK_CHECKS.get(block_id)
    if fn is None:
        raise KeyError(f"집행 코드가 없는 차단 id: {block_id}")
    return fn(Path(unit_dir), fm or {}, body or "", meta or {})


def evaluate(pk, block_ids, point, unit_dir, fm, body):
    """이 집행 지점에서 보는 차단 전부의 판정 → `[(block_id, ok, reason)]`."""
    cat = catalog(pk)
    return [(b, *satisfied(b, unit_dir, fm, body, cat.get(b))) for b in enforced_at(pk, block_ids, point)]
