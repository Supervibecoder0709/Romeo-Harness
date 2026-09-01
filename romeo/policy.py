"""정책표 로더와 결정론 라우터 `route()`.

입력: 사람이 확정한 분류 {unit, mode, intent, facets, gates, blast_radius, uncertainty, actions?, project_kind?}
출력: profile·문서 패키지·섹션·검토·격리·차단·부품·가드·경고·fired_rules. 같은 입력 → 항상 같은 출력.
LLM 제안(proposal)은 candidate 만 여기로 넘어온다(D-06 3분할)."""
from pathlib import Path

import yaml

from . import HARNESS_ROOT
from .blocks import capability_defects, catalog_defects, section_defects
from .schema import validate as _validate
from .util import load_json, load_yaml
from .util import project_root as _cwd_project_root

LEVELS = ["quick", "standard", "deep"]
PROJECT_STATE_FILE = ".harness/romeo.project.yaml"
MODULE_STATUSES = ("active", "pending_gate")
_CACHE = {}


class RouteError(ValueError):
    pass


class PolicyError(ValueError):
    """정책표 자체가 성립하지 않는다. 라우팅 이전에, 로드에서 난다."""


def _load_capabilities(root):
    path = Path(root) / "core/policy/capabilities.yaml"
    if not path.is_file():
        return {}
    return (load_yaml(path) or {}).get("capabilities") or {}


def load_policy(harness_root=None):
    root = harness_root or HARNESS_ROOT
    key = str(root)
    if key not in _CACHE:
        pol = {
            "classification": load_yaml(root / "core/policy/classification.yaml"),
            "packages": load_yaml(root / "core/policy/packages.yaml"),
            "guards": load_yaml(root / "core/policy/execution-guards.yaml"),
            # 능력 카탈로그는 **없을 수 있다** — 프로브가 없는 저장소가 정상 상태다(doctor.load_capabilities 와 같은 규칙).
            # 없으면 빈 카탈로그로 읽고, 그때 능력을 요구하는 오버레이가 있으면 아래 대조가 그것을 잡는다.
            "capabilities": _load_capabilities(root),
            "fixture_schema": load_json(root / "core/schemas/fixture.json"),
        }
        pol["version"] = pol["classification"]["policy_version"]
        # 차단 카탈로그·집행 매핑·실사용을 대조한다. 어긋나면 **로드가 실패한다** — 아무것도 막지 않는
        # 차단이 카드에만 인쇄되던 것이 이 결함의 원래 모양이었으므로, 그 상태로는 정책을 읽지 않는다.
        defects = catalog_defects(pol["packages"])
        if defects:
            raise PolicyError([f"정책표의 차단 카탈로그가 성립하지 않는다 ({root}):"] + defects)
        # 절도 같은 대조를 받는다. 라우터는 오버레이로 절을 **요구**할 수 있는데 집행은 자기가 읽는 문서만 본다 —
        # 그래서 차단에서 닫은 결함(적어 놓고 집행을 잊는 것)이 절로 자리만 옮겨 앉아 있었다.
        # 요구하는 집합과 집행하는 집합을 여기서 맞춰 본다.
        defects = section_defects(pol["packages"])
        if defects:
            raise PolicyError([f"정책표의 절 집행 선언이 성립하지 않는다 ({root}):"] + defects)
        # 능력도 같은 대조를 받는다. 라우터가 능력을 **요구**할 수 있는데 그것을 정의하는 자리는 다른 파일이고,
        # 대조하는 자리는 또 다른 차단이다 — 셋이 어긋나면 카드는 '프로브 없음' 을 인쇄하고 차단은 채울 수 없는
        # 행을 요구한다. 차단·절에서 두 번 닫은 결함이 능력으로 자리만 옮겨 앉지 않게 여기서 본다(§11).
        defects = capability_defects(pol["packages"], pol["capabilities"])
        if defects:
            raise PolicyError([f"정책표의 능력 요구가 성립하지 않는다 ({root}):"] + defects)
        _CACHE[key] = pol
    return _CACHE[key]


def load_project_state(project_root=None):
    """프로젝트 부착 상태(`.harness/romeo.project.yaml`)를 읽어 라우터에 넘길 형태로 돌려준다.

    부품의 실제 부착 상태는 이 파일이 소유한다 — 부품 레지스트리(`core/policy/packages.yaml`)의
    `status` 는 부착 전 기본값일 뿐이다(K-63). 파일이 없으면 `None` 을 돌려주고 라우터는
    기본값(`pending_gate`)을 그대로 쓴다: 부착을 관찰하지 못한 것을 부착으로 세지 않는다(K-51).
    값이 잘못 적혀 있으면 조용히 무시하지 않고 거부한다 — 오타 하나가 규율 부품을 통째로 끄기 때문이다.
    캐시하지 않는다(파일이 바뀌면 다음 호출이 바로 반영된다)."""
    root = Path(project_root) if project_root else Path(_cwd_project_root())
    path = root / PROJECT_STATE_FILE
    if not path.is_file():
        return None
    try:
        data = load_yaml(path) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"{PROJECT_STATE_FILE} 를 읽을 수 없다: {e}")
    if not isinstance(data, dict):
        raise ValueError(f"{PROJECT_STATE_FILE} 의 최상위가 맵이 아니다")
    modules = data.get("modules") or {}
    if not isinstance(modules, dict):
        raise ValueError(f"{PROJECT_STATE_FILE}: modules 가 맵이 아니다")
    for pid, status in modules.items():
        if status not in MODULE_STATUSES:
            raise ValueError(f"{PROJECT_STATE_FILE}: 부품 {pid!r} 의 상태 {status!r} 를 모른다 "
                             f"(허용: {' · '.join(MODULE_STATUSES)})")
    return data


def _lvl(p):
    return LEVELS.index(p)


def _raise_to(current, minimum):
    if current is None:
        return None
    return current if _lvl(current) >= _lvl(minimum) else minimum


def normalize_classification(c):
    c = dict(c or {})
    c.setdefault("facets", [])
    c.setdefault("gates", [])
    c.setdefault("actions", [])
    c.setdefault("project_kind", "code")
    for key in ("facets", "gates", "actions"):
        seen = []
        for item in c[key] or []:
            if item not in seen:
                seen.append(item)
        c[key] = seen
    return c


def validate_classification(c, policy=None):
    pol = policy or load_policy()
    schema = pol["fixture_schema"]["definitions"]["classification"]
    check = {k: v for k, v in c.items() if k != "project_kind"}
    errors = _validate(check, schema, root=pol["fixture_schema"], path="classification")
    cls = pol["classification"]
    for f in c.get("facets", []):
        if f not in cls["facets"]:
            errors.append(f"classification.facets: 알 수 없는 facet {f!r}")
    known_gates = {g["id"] for g in cls["hard_gates"]}
    for g in c.get("gates", []):
        if g not in known_gates:
            errors.append(f"classification.gates: 알 수 없는 gate {g!r}")
    if c.get("project_kind") not in ("code", "non-code", "harness", "home"):
        errors.append(f"classification.project_kind: {c.get('project_kind')!r}")
    return errors


def classification_from_frontmatter(fm):
    return {
        "unit": fm.get("unit"),
        "mode": fm.get("mode"),
        "intent": fm.get("intent"),
        "facets": list(fm.get("facets") or []),
        "gates": list(fm.get("gates") or []),
        # actions 를 빠뜨리면 종료 검사에서 실행 가드가 한 번도 발동하지 않는다 —
        # GUARD_APPROVED 가 조용히 죽은 검사가 된다(K-66).
        "actions": list(fm.get("actions") or []),
        "blast_radius": fm.get("blast_radius"),
        "uncertainty": fm.get("uncertainty"),
    }


def _match(when, ctx):
    for key, val in (when or {}).items():
        if key in ("unit", "mode", "intent", "blast_radius", "uncertainty", "project_kind"):
            if ctx.get(key) not in val:
                return False
        elif key == "gates":
            if val == "any" and not ctx["gates"]:
                return False
            if val == "none" and ctx["gates"]:
                return False
        elif key == "gates_any":
            if not (set(val) & ctx["gates"]):
                return False
        elif key == "facets_any":
            if not (set(val) & ctx["facets"]):
                return False
        elif key == "facets_only":
            if not ctx["facets"] or not ctx["facets"] <= set(val):
                return False
        elif key == "actions_any":
            if not (set(val) & ctx["actions"]):
                return False
        elif key == "profile_min":
            if ctx.get("profile") is None or _lvl(ctx["profile"]) < _lvl(val):
                return False
        elif key == "any_of":
            if not any(ctx.get(k) in v for k, v in val.items()):
                return False
        else:
            raise RouteError([f"정책표 조건 키를 모른다: {key}"])
    return True


def route(classification, policy=None, project_state=None):
    pol = policy or load_policy()
    c = normalize_classification(classification)
    errors = validate_classification(c, pol)
    if errors:
        raise RouteError(errors)
    cls, pk, gd = pol["classification"], pol["packages"], pol["guards"]
    unit = c["unit"]
    ctx = {
        "unit": unit, "mode": c["mode"], "intent": c["intent"],
        "facets": set(c["facets"]), "gates": set(c["gates"]), "actions": set(c["actions"]),
        "blast_radius": c["blast_radius"], "uncertainty": c["uncertainty"],
        "project_kind": c["project_kind"], "profile": None,
    }
    fired, warnings = [], []
    wcat = pk.get("warnings", {})

    def warn(wid, message=None, detail=None):
        warnings.append({"id": wid, "message": message or wcat.get(wid, wid), "detail": detail})
        fired.append(f"warn:{wid}")

    # 1. hard gate 힌트 (facet × intent) — 사람이 체크하지 않은 힌트는 경고
    hinted = []
    for g in cls["hard_gates"]:
        if (set(g["hint_facets"]) & ctx["facets"]) and ("any" in g["applies_to"] or c["intent"] in g["applies_to"]):
            hinted.append(g["id"])
    unchecked = [g for g in hinted if g not in ctx["gates"]]
    if unchecked:
        warn("GATE_HINT_UNCHECKED", detail=unchecked)

    # 2. profile — unit 기본값에서 규칙으로 올리기만 한다
    prof_cfg = cls["profile"]
    profile = prof_cfg["base_by_unit"].get(unit)
    if profile:
        fired.append(f"profile:base:{unit}={profile}")
    for esc in prof_cfg["escalations"]:
        if profile is None:
            break
        if _match(esc["when"], ctx):
            new = _raise_to(profile, esc["min"])
            fired.append(f"profile:{esc['id']}" + (f"->{esc['min']}" if new != profile else "=kept"))
            profile = new
    ctx["profile"] = profile

    # 3. 일관성 경고
    for w in cls["consistency_warnings"]:
        if _match(w["when"], ctx):
            warn(w["id"], w["message"])
    out_of_scope = ctx["project_kind"] == "non-code"
    if out_of_scope:
        profile = None
        ctx["profile"] = None
        warn("OUT_OF_SCOPE_NON_CODE", "v1은 코드 프로젝트 전용이다(D-43). 코드가 없는 프로젝트에는 경량 AGENTS.md 부착만 가능하다. 분류 카드만 남기고 문서를 만들지 않는다.")

    # 4. 패키지 — 기본값 + 오버레이(충돌 우선순위 순)
    base = pk["base"][unit]
    package = list(base["package"]) if not out_of_scope else []
    reviewer = base["reviewer"] if package else "none"
    isolation = base["isolation"] if package else "none"
    blocks = list(base["blocks"]) if package else []
    sections = {doc: [] for doc in package}
    for sid, s in pk["sections"].items():
        if s.get("always") and s["doc"] in sections and sid not in sections[s["doc"]]:
            sections[s["doc"]].append(sid)
    if unit == "T0" and "spec" in sections:
        sections["spec"].insert(1, "capsule")

    def place(sid):
        if not package:
            return
        s = pk["sections"][sid]
        doc = s["doc"] if s["doc"] in sections else (s.get("fallback_doc") if s.get("fallback_doc") in sections else package[-1])
        if sid not in sections[doc]:
            # 증거 절은 항상 마지막
            if "evidence" in sections[doc]:
                sections[doc].insert(sections[doc].index("evidence"), sid)
            else:
                sections[doc].append(sid)

    parts, capabilities = [], []
    order = {tier: i for i, tier in enumerate(cls["conflict_priority"])}
    overlays = sorted(pk["overlays"], key=lambda o: order.get(o.get("tier"), 99))
    for o in overlays:
        if not _match(o["when"], ctx):
            continue
        fired.append(f"overlay:{o['id']}")
        for sid in o.get("add_sections", []):
            place(sid)
        if o.get("set_reviewer") and package:
            reviewer = o["set_reviewer"]
        for b in o.get("add_blocks", []):
            if package and b not in blocks:
                blocks.append(b)
        for pid in o.get("add_parts", []):
            if pid not in parts:
                parts.append(pid)
        # 능력은 부품과 별개다 — **부품에 붙지 않은 능력**도 라우터가 요구할 수 있고, 카드는 그것도 인쇄한다.
        # 문서 package 를 조건으로 걸지 않는다. 차단(add_blocks)은 **문서를 읽어서** 판정하므로 package 가
        # 없으면 볼 것이 없지만, 능력은 **카드가 인쇄하는 것**이라 문서를 만들지 않는 요청에서도 나와야 한다.
        # 오히려 문서 없이 답변으로 끝나는 요청(unit none)이야말로 카드가 유일한 기록이므로, 여기서 능력을
        # 비우면 사람은 그 능력이 있는 것으로 읽고 계획에 넣는다(K-51 · 시나리오 8).
        for cid in o.get("add_capabilities", []):
            if cid not in capabilities:
                capabilities.append(cid)
        for wid in o.get("add_warnings", []):
            warn(wid)

    # 5. 실행 가드 (execution-guards.yaml 단일 출처; 적힌 키가 모두 맞아야 발동)
    guards = []
    for g in gd["guards"]:
        t = g.get("triggers") or {}
        if not t:
            continue
        ok = True
        if "intent" in t and c["intent"] not in t["intent"]:
            ok = False
        if "facets" in t and not (set(t["facets"]) & ctx["facets"]):
            ok = False
        if "actions" in t and not (set(t["actions"]) & ctx["actions"]):
            ok = False
        if ok:
            guards.append({"id": g["id"], "name": g["name"]})
            fired.append(f"guard:{g['id']}")

    # 6. 부품 상태 — 프로젝트 부착 상태가 없으면 채택 게이트 대기로 정직하게 표시
    modules = (project_state or {}).get("modules") or {}
    parts_out, pending = [], []
    for pid in parts:
        meta = pk["parts"].get(pid, {})
        status = "active" if modules.get(pid) == "active" else meta.get("status", "pending_gate")
        # 추천 목록·산출물 결합·능력 프로브는 부품 레지스트리가 소유한다. 라우터는 그대로 실어 나른다 —
        # 카드가 정책표를 다시 읽지 않게 하려는 것이고, `route --json` 을 읽는 쪽도 같은 것을 본다.
        parts_out.append({"id": pid, "gate": meta.get("gate"), "status": status, "role": meta.get("role"),
                          "recommends": list(meta.get("recommends") or []),
                          "output_binding": meta.get("output_binding"),
                          "capability": meta.get("capability")})
        if status != "active":
            pending.append(pid)
    if pending:
        warn("PART_PENDING_GATE", detail=pending)

    return {
        "policy_version": pol["version"],
        "classification": c,
        "unit": unit,
        "unit_name": cls["units"][unit]["name"],
        "profile": profile,
        "profile_label": prof_cfg["labels"].get(profile) if profile else None,
        "gates": sorted(ctx["gates"]),
        "gate_hints": {"hinted": hinted, "unchecked": unchecked},
        "package": package,
        "sections": sections,
        "reviewer": reviewer,
        "isolation": isolation,
        "blocks": blocks,
        "parts": parts_out,
        "capabilities": capabilities,
        "guards": guards,
        "warnings": warnings,
        "fired_rules": fired,
        "budgets": pk["budgets"],
        "out_of_scope": out_of_scope,
    }


def profile_reasons(route_out, policy=None):
    """카드용: 깊이를 올린 규칙의 reason 문장 목록."""
    pol = policy or load_policy()
    reasons = []
    esc = {e["id"]: e for e in pol["classification"]["profile"]["escalations"]}
    for rule in route_out["fired_rules"]:
        if rule.startswith("profile:") and "->" in rule:
            rid = rule[len("profile:"):].split("->")[0]
            if rid in esc:
                reasons.append(esc[rid]["reason"])
    if not reasons and route_out["profile"]:
        reasons.append(f"{route_out['unit']} 기본값")
    return reasons
