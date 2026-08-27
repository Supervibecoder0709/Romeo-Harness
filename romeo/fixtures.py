"""fixture 로더·검사·리포트. `romeo route --fixtures DIR --report` 가 정책표 일치율과 gate 누락을 출력한다(V-0, M0 관찰 결과)."""
from collections import Counter
from pathlib import Path

from .policy import RouteError, load_policy, route
from .schema import validate as _validate
from .util import load_yaml


def load_fixtures(directory):
    directory = Path(directory)
    items = []
    for path in sorted(directory.glob("*.yaml")):
        data = load_yaml(path)
        data["_path"] = str(path)
        items.append(data)
    return items


def check_fixtures(fixtures, policy=None):
    pol = policy or load_policy()
    schema = pol["fixture_schema"]
    errors = {}
    ids = Counter(f.get("id") for f in fixtures)
    for f in fixtures:
        data = {k: v for k, v in f.items() if not k.startswith("_")}
        errs = _validate(data, schema)
        if ids[f.get("id")] > 1:
            errs.append(f"중복 id {f.get('id')}")
        if errs:
            errors[f["_path"]] = errs
    return errors


def _compare(expected, out):
    mism = []
    if "profile" in expected and expected["profile"] != out["profile"]:
        mism.append(f"profile {expected['profile']}≠{out['profile']}")
    if "package" in expected and list(expected["package"]) != list(out["package"]):
        mism.append(f"package {expected['package']}≠{out['package']}")
    actual_sections = {s for secs in out["sections"].values() for s in secs}
    for s in expected.get("sections", []):
        if s not in actual_sections:
            mism.append(f"section {s} 없음")
    for key in ("reviewer", "isolation"):
        if key in expected and expected[key] != out[key]:
            mism.append(f"{key} {expected[key]}≠{out[key]}")
    if "blocks" in expected and set(expected["blocks"]) != set(out["blocks"]):
        mism.append(f"blocks {expected['blocks']}≠{out['blocks']}")
    if "guards" in expected and set(expected["guards"]) != {g["id"] for g in out["guards"]}:
        mism.append(f"guards {expected['guards']}≠{[g['id'] for g in out['guards']]}")
    if "parts" in expected and set(expected["parts"]) != {p["id"] for p in out["parts"]}:
        mism.append(f"parts {expected['parts']}≠{[p['id'] for p in out['parts']]}")
    actual_warn = {w["id"] for w in out["warnings"]}
    for w in expected.get("warnings", []):
        if w not in actual_warn:
            mism.append(f"warning {w} 없음")
    if "out_of_scope" in expected and expected["out_of_scope"] != out["out_of_scope"]:
        mism.append(f"out_of_scope {expected['out_of_scope']}≠{out['out_of_scope']}")
    return mism


def run_report(fixtures, policy=None):
    pol = policy or load_policy()
    rows, fired_counter, warn_counter = [], Counter(), Counter()
    for f in fixtures:
        row = {"id": f["id"], "unit": f["classification"]["unit"], "expected_profile": f["expected"].get("profile"), "actual_profile": None,
               "ok": False, "alt": False, "mismatches": [], "gate_miss": False, "fired_rules": []}
        try:
            out = route(f["classification"], pol)
        except RouteError as e:
            row["mismatches"] = [f"ROUTE_ERROR {'; '.join(e.args[0])}"]
            rows.append(row)
            continue
        row["actual_profile"] = out["profile"]
        row["fired_rules"] = out["fired_rules"]
        fired_counter.update(r.split("->")[0].replace("=kept", "") for r in out["fired_rules"])
        warn_counter.update(w["id"] for w in out["warnings"])
        mism = _compare(f["expected"], out)
        expected_warns = set(f["expected"].get("warnings", []))
        if out["gate_hints"]["unchecked"] and "GATE_HINT_UNCHECKED" not in expected_warns:
            row["gate_miss"] = True
            mism.append(f"gate 누락 의심 {out['gate_hints']['unchecked']}")
        if mism:
            for alt in f.get("acceptable_alternatives") or []:
                if not _compare({**f["expected"], **alt}, out):
                    row["alt"] = True
                    break
        row["mismatches"] = mism
        row["ok"] = not mism or row["alt"]
        rows.append(row)
    total = len(rows)
    matched = sum(1 for r in rows if r["ok"])
    return {
        "total": total, "matched": matched, "match_rate": (matched / total) if total else 0.0,
        "gate_misses": sum(1 for r in rows if r["gate_miss"]), "alt_matches": sum(1 for r in rows if r["alt"]),
        "rows": rows, "fired_rules": fired_counter.most_common(), "warnings": warn_counter.most_common(),
        "policy_version": pol["version"],
    }


def format_report(rep):
    lines = [f"fixture 리포트 · policy {rep['policy_version']} · {rep['matched']}/{rep['total']} 일치 = {rep['match_rate']*100:.1f}% · gate 누락 의심 {rep['gate_misses']} · 대안 일치 {rep['alt_matches']}", ""]
    lines.append("| fixture | unit | 기대 profile | 실제 | 결과 | 불일치 |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for r in rep["rows"]:
        mark = "✓" if r["ok"] and not r["alt"] else ("≈" if r["alt"] else "✗")
        lines.append(f"| {r['id']} | {r['unit']} | {r['expected_profile']} | {r['actual_profile']} | {mark} | {'; '.join(r['mismatches'])} |")
    lines.append("")
    lines.append("발동 규칙 빈도: " + ", ".join(f"{k}×{v}" for k, v in rep["fired_rules"][:15]))
    lines.append("경고 빈도: " + (", ".join(f"{k}×{v}" for k, v in rep["warnings"]) or "없음"))
    return "\n".join(lines)
