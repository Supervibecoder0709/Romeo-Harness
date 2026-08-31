"""제안 카드 렌더링(≤ 30줄). 깊이와 이유를 먼저, 단위·모드·영역은 한 줄로. 사람이 1클릭으로 확정하는 화면."""
from .doctor import probe_capabilities
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


def _parts_detail(parts, root=None):
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
            probes = {c["id"]: c for c in probe_capabilities(root)}
        c = probes.get(cap_id)
        lines.append(f"  설치: {cap_id} {c['label']} — {c['detail']}" if c
                     else f"  설치: {cap_id} 프로브 없음 — 확인되지 않았다")
    return lines


def render_card(proposal, route_out, policy=None, root=None):
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
    if route_out["parts"]:
        lines.append("부품: " + " · ".join(f"{p['id']}({p['gate']} {'활성' if p['status']=='active' else '대기'})" for p in route_out["parts"]))
        lines.extend(_parts_detail(route_out["parts"], root))
    warns = [w for w in route_out["warnings"] if w["id"] not in ("PART_PENDING_GATE",)]
    if warns:
        lines.append("경고:")
        lines.extend(_list([f"{w['id']}: {w['message']}" for w in warns], 3))
    if proposal.get("needs_decision"):
        lines.append("결정 필요:")
        lines.extend(_list(proposal["needs_decision"], 2))
    if proposal.get("reuse_hits"):
        lines.append("재사용 후보: " + _clip(", ".join(proposal["reuse_hits"]), 90))
    lines.append("확정: [그대로 진행] 또는 단위·깊이·게이트를 고쳐 주세요 → human_correction 에 기록")
    limit = pk["budgets"]["card_max_lines"]
    if len(lines) > limit:
        # 사실·가정·미확인 부터 줄인다 (게이트·문서·실행 줄은 유지)
        keep = [ln for ln in lines if not ln.startswith("  - ")]
        lines = keep[:limit]
    return "\n".join(lines)
