"""제안 카드 렌더링(≤ 30줄). 깊이와 이유를 먼저, 단위·모드·영역은 한 줄로. 사람이 1클릭으로 확정하는 화면."""
from .doctor import probe_capabilities
from .find import proposal_terms, search_units
from .policy import load_policy, profile_reasons

GATE_SHORT = {
    "payment": "결제", "privacy-security": "개인정보·보안", "legal": "법무", "ops-data-deletion": "운영데이터삭제",
    "migration": "마이그레이션", "public-api": "공개API", "irreversible-policy": "정책변경", "availability": "서비스중단",
}
FACTOR_KO = {"scope": "범위", "uncertainty": "불확실성", "impact": "영향", "reversibility": "되돌리기", "coordination": "조율"}
LEVEL_KO = {"low": "낮음", "medium": "중간", "high": "높음"}
SIZE_KO = {"small": "작음", "medium": "중간", "large": "큼"}
DOC_KO = {"spec": "Tech Spec", "brief": "Compact Brief", "charter": "Charter"}
REVIEWER_KO = {"none": "검토자 없음", "opposite-runtime-readonly": "반대 런타임 read-only 검토"}
ISOLATION_KO = {"none": "실행 없음", "current": "현재 작업 공간", "worktree": "격리 worktree"}


def _clip(s, n=110):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def _list(items, n, prefix="  - "):
    items = list(items or [])[:n]
    return [prefix + _clip(x, 100) for x in items]


def _wrap(prefix, items, width=88, sep=" · ", indent="      "):
    """목록을 잘라내지 않고 여러 줄로 접는다.

    추천 11종을 `_clip` 으로 자르면 사람이 본 목록과 정책표가 달라진다 — 카드가 결정을
    보여 주는 화면이므로 여기서는 줄 수를 늘리고 내용을 지키는 쪽을 고른다."""
    lines, cur = [], prefix
    for i, item in enumerate(items):
        piece = (sep if i else "") + str(item)
        if len(cur) + len(piece) > width and cur.strip() != prefix.strip():
            lines.append(cur)
            cur = indent + str(item)
        else:
            cur += piece
    lines.append(cur)
    return lines


def _parts_detail(parts, root=None, harness_root=None):
    """부품 절의 아래 줄 — 추천 목록 · 산출물 결합 규칙 · 설치 프로브 결과.

    추천을 인쇄하면서 설치 여부를 말하지 않으면 사람은 지금 쓸 수 있는 것으로 읽는다.
    그래서 셋을 한 자리에 둔다: 무엇을 권하는가 · 그 산출물을 어떻게 붙이는가 · 지금 있는가(K-51).
    """
    lines = []
    probes = None
    for p in parts:
        rec = p.get("recommends") or []
        if not rec:
            continue
        lines += _wrap(f"  {p['id']} 추천 {len(rec)}종: ", rec)
        if p.get("output_binding") == "inputs-link":
            lines.append("  산출물은 복사하지 않는다 — 문서 frontmatter 의 inputs: 링크로만 붙인다(K-62)")
        cap_id = p.get("capability")
        if not cap_id:
            continue
        if probes is None:
            probes = {c["id"]: c for c in probe_capabilities(root, harness_root)}
        c = probes.get(cap_id)
        lines.append(f"  설치: {cap_id} {c['label']} — {c['detail']}" if c
                     else f"  설치: {cap_id} 프로브 없음 — 확인되지 않았다")
    return lines


def _capabilities_detail(cap_ids, root=None, harness_root=None):
    """라우터가 요구한 능력마다 **프로브 결과와 대안**을 인쇄한다.

    부품에 붙지 않은 능력도 인쇄한다 — 부품 절에만 프로브를 매달아 두면, 부품 없이 요구되는 능력은
    카드에 한 줄도 나오지 않는다. 그러면 사람은 그 능력이 있는 것으로 읽고 계획에 넣는다(K-51).
    없는 것은 **없다고 인쇄하고 대안을 함께 준다** — 부재를 숨기지도 않고 막지도 않는다(Q-28).

    루트가 둘인 이유는 `doctor.probe_capabilities` 와 같다: 능력 카탈로그·어댑터 선언은 하네스의 내용이고
    흔적 파일은 **작업 대상 저장소**의 상태다. 부착한 프로젝트에서 하나로 뭉치면 카탈로그를 찾지 못해
    모든 능력이 「프로브 없음」 이 되고, 사람은 그것을 대상 프로젝트의 상태로 읽는다(K-51).
    부르는 쪽(`cli.cmd_card` · `cmd_route --card`)이 `--root` 를 대상 저장소로, `HARNESS_ROOT` 를
    하네스로 넘긴다 — 집행 쪽(`blocks.py`)은 이미 두 루트를 쓴다."""
    if not cap_ids:
        return []
    probes = {c["id"]: c for c in probe_capabilities(root, harness_root)}
    lines = [f"능력: {len(cap_ids)}종 — 없는 것은 없다고 인쇄한다(자동 설치 금지)"]
    for cid in cap_ids:
        c = probes.get(cid)
        if not c:
            lines.append(f"  {cid}: 프로브 없음 — 확인되지 않았다")
            continue
        row = f"  {cid}: {c['label']} — {_clip(c['detail'], 46)}"
        alts = c.get("alternatives") or []
        # 한 능력에 한 줄. 카드는 30줄 예산 안에서 사실·가정·미확인과 자리를 나눠 쓰므로,
        # 대안을 여러 줄로 펼치면 그 줄들이 예산에 밀려 잘린다(정책표는 그대로 남는다).
        if c["label"] != "present" and alts:
            row += f" · 대안 {_clip(alts[0], 44)}" + (f" 외 {len(alts) - 1}" if len(alts) > 1 else "")
        lines.append(row)
    return lines


def _reuse_line(said, found, width=96):
    """재사용 후보 줄 — 제안이 적어 준 것과 카드가 **스스로 찾은** 것을 한 줄에 둔다.

    id 는 자르지 않는다. 잘린 id 는 그 단위를 지목하지 못하므로 인쇄해도 아무것도 드러내지
    못한다 — 폭이 모자라면 뒤쪽 후보를 개수로 접는다. 카드가 찾은 것에는 `(검색)` 을 붙인다:
    사람이 적어 넣은 것과 기계가 찾은 것을 구별하지 못하면, 제안자가 1단계를 빠뜨렸다는 사실
    자체가 보이지 않는다.
    """
    items = list(said) + [f"{i}(검색)" for i in found]
    shown, sep = [], " · "
    used = 0
    for item in items:
        need = len(item) + (len(sep) if shown else 0)
        if shown and used + need > width:
            break
        shown.append(item)
        used += need
    rest = len(items) - len(shown)
    return "재사용 후보: " + sep.join(shown) + (f" 외 {rest}건" if rest else "")


def render_card(proposal, route_out, policy=None, root=None, harness_root=None):
    pol = policy or load_policy()
    pk = pol["packages"]
    cand = proposal["candidate"]
    lines = []
    lines.append(f"[romeo:plan 제안 카드] policy {route_out['policy_version']}")
    lines.append("요청: " + _clip(proposal["request"]["text"], 100))
    if route_out["profile"]:
        lines.append(f"깊이: {route_out['profile_label']} — " + " · ".join(profile_reasons(route_out, pol)[:2]))
    else:
        lines.append("깊이: 문서 없음 — 답변으로 종료(unit none)")
    facets = ", ".join(cand.get("facets") or []) or "없음"
    lines.append(f"단위 {route_out['unit']} {route_out['unit_name']} · 모드 {cand['mode']} · 의도 {cand['intent']} · 영역 {facets}")
    for label, key, n in (("사실", "facts", 3), ("가정", "assumptions", 2), ("미확인", "unknowns", 2)):
        items = proposal.get(key) or []
        if items:
            lines.append(f"{label}:")
            lines.extend(_list(items, n))
    f = proposal["factors"]
    lines.append("5요인: " + " · ".join(f"{FACTOR_KO[k]} {LEVEL_KO[f[k]['level']]}({_clip(f[k]['note'], 28)})" for k in ("scope", "uncertainty", "impact")))
    lines.append("       " + " · ".join(f"{FACTOR_KO[k]} {LEVEL_KO[f[k]['level']]}({_clip(f[k]['note'], 28)})" for k in ("reversibility", "coordination")))
    lines.append(f"2질문: 영향 반경 {SIZE_KO[cand['blast_radius']]} · 불확실성 {LEVEL_KO[cand['uncertainty']]}")
    checks = {c["gate"]: c for c in proposal.get("gate_checklist", [])}
    boxes = []
    for g in pol["classification"]["hard_gates"]:
        on = checks.get(g["id"], {}).get("checked") or g["id"] in route_out["gates"]
        boxes.append(f"[{'x' if on else ' '}]{GATE_SHORT[g['id']]}")
    lines.append("게이트: " + " ".join(boxes))
    fired = ", ".join(route_out["gates"]) or "없음"
    unchecked = route_out["gate_hints"]["unchecked"]
    lines.append(f"  → 발동 {fired}" + (f" · 힌트인데 미체크: {', '.join(unchecked)}" if unchecked else ""))
    if route_out["package"]:
        docs = " + ".join(DOC_KO[d] for d in route_out["package"])
        extra = [pk["sections"][s]["title"] for d in route_out["package"] for s in route_out["sections"].get(d, []) if not pk["sections"][s].get("always") and s != "capsule"]
        lines.append(f"문서: {docs}" + (" · 섹션 추가: " + ", ".join(extra) if extra else ""))
    else:
        lines.append("문서: 없음 (카드만 기록)")
    guards = ", ".join(g["name"] for g in route_out["guards"]) or "없음"
    lines.append(f"실행: {REVIEWER_KO[route_out['reviewer']]} · {ISOLATION_KO[route_out['isolation']]} · 차단 {', '.join(route_out['blocks']) or '없음'} · 가드 {guards}")
    lines.extend(_capabilities_detail(route_out.get("capabilities"), root, harness_root))
    if route_out["parts"]:
        lines.append("부품: " + " · ".join(f"{p['id']}({p['gate']} {'활성' if p['status']=='active' else '대기'})" for p in route_out["parts"]))
        lines.extend(_parts_detail(route_out["parts"], root, harness_root))
    warns = [w for w in route_out["warnings"] if w["id"] not in ("PART_PENDING_GATE",)]
    if warns:
        lines.append("경고:")
        lines.extend(_list([f"{w['id']}: {w['message']}" for w in warns], 3))
    if proposal.get("needs_decision"):
        lines.append("결정 필요:")
        lines.extend(_list(proposal["needs_decision"], 2))
    # 재사용 후보는 제안이 적어 준 것과 **카드가 직접 찾은 것**을 함께 인쇄한다.
    # 제안자가 1단계(재사용 검색)를 빠뜨려 `reuse_hits` 가 비어 있어도 중복이 보여야 한다 —
    # 요구를 절차에 적고 확인을 카드에 두지 않으면, 빠뜨린 것과 겹치는 것이 없는 것이 같은 화면이 된다.
    said = [str(x) for x in (proposal.get("reuse_hits") or [])]
    found = [h["id"] for h in search_units(root or ".", proposal_terms(proposal)) if h["id"] not in said]
    # 이 두 줄은 예산 축소에서 제외한다. 축소로 사라지면 이 요구는 인쇄만 되고 아무것도 드러내지 못한다.
    tail = []
    if said or found:
        tail.append(_reuse_line(said, found))
    tail.append("확정: [그대로 진행] 또는 단위·깊이·게이트를 고쳐 주세요 → human_correction 에 기록")
    limit = pk["budgets"]["card_max_lines"]
    if len(lines) + len(tail) > limit:
        # 사실·가정·미확인 부터 줄인다 (게이트·문서·실행 줄은 유지)
        keep = [ln for ln in lines if not ln.startswith("  - ")]
        lines = keep[:limit - len(tail)]
    return "\n".join(lines + tail)
