"""부착 검증 — 프로브 + 충돌 fixture (K-68).

"설치됐다" 와 "동작한다" 는 다르다. 이 모듈은 **파일과 설정 수준에서 확인 가능한 것만** 본다.
런타임이 스킬을 실제로 로드하는지는 여기서 증명할 수 없다 — 그 항목은 `runtime_load` 로 분류해
"미검증" 이라고 정직하게 표시하고, 사람이 세션에서 관찰한 결과를 `.harness/observations.yaml` 에 기록한다.

충돌 검사는 `fixtures/conflicts/*.yaml` 에 선언돼 있다. 부품 원문은 고칠 수 없으므로(verbatim)
"패턴 금지" 가 아니라 **"패턴이 있으면 대응 override 가 있어야 한다"** 로 검사한다.
"""
import re
import shutil
import subprocess
from pathlib import Path

from .util import load_any, project_root as _project_root

CONFLICTS_DIR = "fixtures/conflicts"
OBSERVATIONS_PATH = ".harness/observations.yaml"
CAPABILITIES_PATH = "core/policy/capabilities.yaml"

# manifest 가 같은 것을 다른 이름으로 적을 수 있다. 찾지 못하면 **비워 둔다** — 지어내지 않는다.
READ_ALIASES = {
    "modules": ("modules", "installed_modules"),
    "platform_codes": ("platform_codes", "platforms", "ides", "tools"),
}

RUNTIME_PROBES = [
    ("claude", ["claude", "--version"], "구현자 런타임 (D-68)"),
    ("codex", ["codex", "--version"], "검토자 런타임 (D-68)"),
    ("orca", ["orca", "--version"], "worktree·위임 (전역 Orca 우선 규칙)"),
    ("gh", ["gh", "--version"], "PR·CI 조회"),
    ("git", ["git", "--version"], "증거 신선도 계산"),
]


def _run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or r.stderr or "").strip().splitlines()[:1]
    except (OSError, subprocess.SubprocessError):
        return None, []


def probe_runtimes():
    out = []
    for name, cmd, why in RUNTIME_PROBES:
        path = shutil.which(cmd[0])
        if not path:
            out.append({"name": name, "ok": False, "detail": "PATH 에 없다", "why": why})
            continue
        code, first = _run(cmd)
        out.append({"name": name, "ok": code == 0, "why": why,
                    "detail": (first[0] if first else f"exit {code}")[:80]})
    return out


def load_capabilities(root):
    """능력 프로브 정책표를 읽는다. 파일이 없으면 프로브가 없는 것이다 — 만들어 내지 않는다."""
    p = Path(root) / CAPABILITIES_PATH
    if not p.is_file():
        return {}
    return (load_any(p) or {}).get("capabilities") or {}


def _read_recorded(data, field):
    """marker 파일이 실제로 기록한 값만 돌려준다. 기록이 없으면 None — '없음' 과 '못 읽었음' 은 다르다."""
    if not isinstance(data, dict):
        return None
    for key in READ_ALIASES.get(field, (field,)):
        if key in data:
            v = data[key]
            if isinstance(v, dict):
                return sorted(str(k) for k in v)
            if isinstance(v, (list, tuple)):
                return [str(x) for x in v]
            return [str(v)]
    return None


def _probe_install_trace(root, cap_id, spec):
    """설치기가 남긴 상태 파일 하나를 본다. 이것으로 말할 수 있는 것은 '설치 흔적' 뿐이다."""
    marker = str(spec.get("marker") or "")
    entry = {"id": cap_id, "kind": spec.get("kind"), "marker": marker,
             "label": "absent", "detail": str(spec.get("absent_detail") or "설치 흔적 없음"),
             "reads": {f: None for f in (spec.get("reads") or [])},
             "honesty": str(spec.get("honesty") or ""), "part": spec.get("part")}
    path = Path(root) / marker if marker else None
    if not marker or not path.is_file():
        return entry
    entry["label"] = "present"
    try:
        data = load_any(path)
    except Exception as exc:  # 손상된 manifest 도 '설치 흔적' 이다 — 없다고 말하지 않는다.
        entry["detail"] = f"설치 흔적 확인 — 다만 marker 를 읽을 수 없다: {str(exc).splitlines()[0][:80]}"
        return entry
    entry["detail"] = "설치 흔적 확인"
    for field in spec.get("reads") or []:
        entry["reads"][field] = _read_recorded(data, field)
    return entry


CAPABILITY_KINDS = {"install_trace": _probe_install_trace}


def probe_capabilities(root=None):
    """`core/policy/capabilities.yaml` 의 프로브를 실행한다.

    반환값의 `label` 은 정책표의 `result_labels` 안에서만 나온다(`present`·`absent`).
    **미설치는 결함이 아니다** — 부르는 쪽은 이 결과를 문제 수에 더하지 않는다.
    """
    root = Path(root) if root else _project_root()
    out = []
    for group, caps in sorted((load_capabilities(root) or {}).items()):
        for name, spec in sorted((caps or {}).items()):
            cap_id = f"{group}.{name}"
            fn = CAPABILITY_KINDS.get((spec or {}).get("kind"))
            if not fn:
                out.append({"id": cap_id, "kind": (spec or {}).get("kind"), "marker": "",
                            "label": "absent", "detail": f"모르는 프로브 kind: {(spec or {}).get('kind')}",
                            "reads": {}, "honesty": "", "part": (spec or {}).get("part")})
                continue
            out.append(_plain(fn(root, cap_id, spec)))
    return out


def probe_skill_files(root):
    """두 런타임의 스킬 디렉터리를 파일 수준으로 검사한다. 로드 여부는 알 수 없다."""
    from . import frontmatter as fm
    from .compile import load_adapters

    out = []
    for adapter in load_adapters(root):
        d = root / adapter["skills_dir"]
        skills, problems = [], []
        if not d.is_dir():
            out.append({"runtime": adapter["id"], "dir": adapter["skills_dir"],
                        "count": 0, "problems": ["디렉터리가 없다"], "skills": []})
            continue
        for sk in sorted(d.glob("*/SKILL.md")):
            name_dir = sk.parent.name
            meta, _ = fm.split(sk.read_text(encoding="utf-8"))
            if not meta:
                problems.append(f"{name_dir}: frontmatter 없음 — discovery 안 된다")
                continue
            if not meta.get("name"):
                problems.append(f"{name_dir}: name 없음")
            if not (meta.get("description") or "").strip():
                problems.append(f"{name_dir}: description 없음 — 라우터가 켤 근거가 없다")
            if sk.is_symlink() or sk.parent.is_symlink():
                problems.append(f"{name_dir}: 심링크 — Windows 에서 깨진다")
            skills.append(meta.get("name") or name_dir)
        out.append({"runtime": adapter["id"], "dir": adapter["skills_dir"],
                    "count": len(skills), "problems": problems, "skills": sorted(skills)})
    return out


def _projected_skill_files(root):
    from .compile import load_adapters
    files = []
    for adapter in load_adapters(root):
        d = root / adapter["skills_dir"]
        if d.is_dir():
            files += [f for f in sorted(d.rglob("*")) if f.is_file() and f.suffix == ".md"]
    return files


def _override_keys(root):
    b = root / ".harness/bindings.yaml"
    if not b.exists():
        return set()
    return set((load_any(b) or {}).get("overrides") or {})


def _check_c1(root, fx):
    """패턴이 있으면 대응 override 가 있어야 한다. 원문을 고칠 수 없으므로 금지가 아니라 흡수로 검사한다."""
    findings = []
    keys = _override_keys(root)
    pats = fx["patterns"]
    # 리스트면 fixture 하나가 단일 override 를 요구하고, 매핑이면 패턴마다 다른 override 를 요구한다.
    if isinstance(pats, dict):
        needed_for = dict(pats)
    else:
        needed_for = {p: fx.get("requires_override_key") for p in pats}
    for f in _projected_skill_files(root):
        text = f.read_text(encoding="utf-8", errors="replace")
        for pat, needed in needed_for.items():
            if pat in text and needed not in keys:
                findings.append((fx["id"], str(f.relative_to(root)),
                                 f"'{pat}' 를 지시하는데 bindings.yaml 에 overrides.{needed} 가 없다"))
    return findings


def _check_c2(root, fx):
    findings = []
    for rel in fx.get("forbidden_hook_files") or []:
        if (root / rel).exists():
            findings.append((fx["id"], rel, "부품 hook 파일이 저장소에 등록돼 있다 — 라우터를 우회한다"))
    settings = root / ".claude/settings.json"
    if settings.exists():
        import json
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
        except ValueError:
            data = {}
        for key in fx.get("forbidden_settings_keys") or []:
            if key in data:
                findings.append((fx["id"], ".claude/settings.json",
                                 f"'{key}' 키가 있다 — 트리거 소유권은 라우터에 있다(K-65)"))
    for f in _projected_skill_files(root):
        low = f.read_text(encoding="utf-8", errors="replace").lower()
        for phrase in fx.get("forbidden_phrases") or []:
            if phrase.lower() in low:
                findings.append((fx["id"], str(f.relative_to(root)),
                                 f"'{phrase}' — 스스로 켜지려는 지시가 남아 있다"))
    return findings


def _check_c3(root, fx):
    from .compile import MANAGED_START, load_adapters
    findings = []
    if fx.get("check_duplicate_skill_names"):
        for probe in probe_skill_files(root):
            seen = {}
            for name in probe["skills"]:
                seen[name] = seen.get(name, 0) + 1
            for name, n in sorted(seen.items()):
                if n > 1:
                    findings.append((fx["id"], f"{probe['dir']}/{name}",
                                     f"같은 스킬 이름이 {n} 번 — 어느 쪽이 로드될지 알 수 없다"))
    owner_re = re.compile(r"<!--\s*([a-z0-9_-]+):managed\s+start", re.I)
    allowed = set(fx.get("allowed_marker_owners") or [])
    for rel in fx.get("instructions_files") or []:
        p = root / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        owners = owner_re.findall(text)
        for owner in owners:
            if allowed and owner.lower() not in allowed:
                findings.append((fx["id"], rel, f"'{owner}:managed' 마커가 있다 — 소유자가 겹친다"))
        if owners.count("romeo") > 1:
            findings.append((fx["id"], rel, "romeo:managed 블록이 둘 이상이다 — 컴파일이 하나만 갱신한다"))
        if MANAGED_START in text and text.count("<!-- romeo:managed end -->") != owners.count("romeo"):
            findings.append((fx["id"], rel, "managed 마커의 start/end 개수가 맞지 않는다"))
    return findings


def _recommend_pairs(root, fx):
    """정책표의 **모든** 부품이 추천하는 (부품 id, 스킬 id) 쌍.

    한 부품만 보면 다음에 추가되는 부품이 같은 실수를 반복한다. 정책표 파일을 직접 읽는다 —
    로더 캐시를 거치면 같은 프로세스 안에서 파일을 고쳐 만든 위반이 반영되지 않는다."""
    data = load_any(root / fx.get("packages_file", "core/policy/packages.yaml")) or {}
    pairs = []
    for pid, part in sorted((data.get("parts") or {}).items()):
        for rid in ((part or {}).get("recommends") or []):
            pairs.append((str(pid), str(rid)))
    return pairs


def _check_c5(root, fx):
    """부품이 설치될 자리를 컴파일 산출물이 점유하고 있는가.

    prune 은 `.harness/compiled.yaml` 에 적힌 것만 지운다. 그래서 위험한 것은 두 가지다 —
    설치 디렉터리 **자체**(또는 그 조상)를 산출물로 적는 것, 그리고 설치될 스킬과 **같은 이름**을
    그 안에 두는 것. 앞은 남의 파일을 지우고, 뒤는 어느 쪽이 로드될지 알 수 없게 만든다."""
    findings = []
    state = load_any(root / fx.get("state_file", ".harness/compiled.yaml")) or {}
    outputs = [str(o).strip("/") for o in (state.get("outputs") or [])]
    install_dirs = [str(d).strip("/") for d in (fx.get("install_dirs") or [])]
    names = {rid for _pid, rid in _recommend_pairs(root, fx)}
    for d in install_dirs:
        for out in outputs:
            if out == d or d.startswith(out + "/"):
                findings.append((fx["id"], out,
                                 f"컴파일 산출물이 설치 디렉터리 '{d}' 를 통째로 소유한다 — "
                                 f"다음 prune 이 그 안의 설치물을 지운다"))
        for name in sorted(names):
            if f"{d}/{name}" in outputs:
                findings.append((fx["id"], f"{d}/{name}",
                                 f"추천하는 부품 스킬 '{name}' 과 같은 이름을 컴파일이 쓴다 — "
                                 f"설치하면 어느 쪽이 로드될지 알 수 없다"))
    return findings


def _check_c6(root, fx):
    """추천 목록의 각 id 가 accepted 판정의 출처에서 왔는가, 보류·기각된 것은 아닌가."""
    findings = []
    imports = (load_any(root / fx.get("imports_file", "provenance/imports.yaml")) or {}).get("imports") or []
    forbidden_statuses = set(fx.get("forbidden_statuses") or [])
    allowed_key = fx.get("allowed_from", "router_recommends")
    allowed_status = fx.get("allowed_status", "accepted")
    forbidden = {str(e.get("id")) for e in imports if e.get("status") in forbidden_statuses}
    allowed = {str(r) for e in imports if e.get("status") == allowed_status
               for r in (e.get(allowed_key) or [])}
    where = fx.get("packages_file", "core/policy/packages.yaml")
    for pid, rid in _recommend_pairs(root, fx):
        if rid in forbidden:
            findings.append((fx["id"], f"{where}:parts.{pid}",
                             f"'{rid}' 는 보류·기각 판정인데 추천 목록에 있다 — 기획 원본이 둘이 된다"))
        elif rid not in allowed:
            findings.append((fx["id"], f"{where}:parts.{pid}",
                             f"'{rid}' 의 출처가 없다 — {fx.get('imports_file')} 의 "
                             f"{allowed_status} 항목 {allowed_key} 에 없다"))
    return findings


def _check_c7(root, fx):
    """코어 안에 부품 기본 출력 경로가 박혀 있는가. 원문(c1)과 달리 여기는 흡수가 아니라 부재를 요구한다."""
    findings = []
    pats = [str(x) for x in (fx.get("patterns") or [])]
    for rel in fx.get("scope_dirs") or []:
        d = root / rel
        if not d.is_dir():
            continue
        for f in sorted(d.rglob("*")):
            if not f.is_file():
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            for pat in pats:
                if pat in text:
                    findings.append((fx["id"], str(f.relative_to(root)),
                                     f"'{pat}' 가 코어에 박혀 있다 — 경로를 아는 곳은 부품 설정과 inputs: 링크뿐이다"))
    return findings


CHECKERS = {"pattern_requires_override": _check_c1,
            "no_auto_trigger": _check_c2,
            "collision": _check_c3,
            "install_path_collision": _check_c5,
            "no_second_plan_origin": _check_c6,
            "no_hardcoded_output_path": _check_c7}


def check_conflicts(root=None):
    """fixtures/conflicts/*.yaml 을 실행한다. (findings, 실행한 fixture 수)."""
    root = Path(root) if root else _project_root()
    d = root / CONFLICTS_DIR
    findings, ran = [], 0
    for f in sorted(d.glob("*.yaml")) if d.is_dir() else []:
        fx = load_any(f) or {}
        fn = CHECKERS.get(fx.get("kind"))
        if not fn:
            findings.append(("?", str(f.relative_to(root)), f"모르는 kind: {fx.get('kind')}"))
            continue
        ran += 1
        findings += fn(root, fx)
    return findings, ran


def _plain(value):
    """YAML 이 만든 값을 JSON 으로 낼 수 있는 형태로 낮춘다.

    `observed_at: 2026-08-28` 처럼 따옴표 없는 날짜는 date 객체가 되어 `doctor --json` 을 죽인다.
    기록 파일은 사람이 손으로 쓰는 곳이므로, 읽는 쪽에서 막는다.
    """
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _evidence_is_real(root, ref):
    """관찰 기록이 지목한 증거가 저장소 안에 실재하는 파일인지 본다.

    저장소 밖(절대 경로·상위 탈출)은 이 저장소의 관찰 기록이 될 수 없다 — 읽는 사람이 따라갈 수 없다."""
    if not isinstance(ref, str) or not ref.strip():
        return False
    try:
        p = Path(ref.strip())
        if p.is_absolute() or ".." in p.parts:
            return False
        return (Path(root) / p).is_file()
    except (OSError, ValueError):
        return False


def observations(root):
    """관찰 기록을 읽고, 각 항목의 증거 포인터가 실재하는지 함께 기록한다(`evidence_exists`).

    '관찰됨' 은 사람이 손으로 적은 자기 신고 위에 선다. 최소한 그 신고가 가리키는 증거가 저장소에
    실재하는지는 검사한다 — 없거나 실재하지 않으면 대조할 수 없다(K-51)."""
    p = root / OBSERVATIONS_PATH
    data = _plain((load_any(p) or {}).get("runtime_load") or {}) if p.exists() else {}
    for entry in data.values():
        if isinstance(entry, dict):
            entry["evidence_exists"] = _evidence_is_real(root, entry.get("evidence"))
    return data


def _observed_entry(entry):
    """관찰 기록 한 항목을 (관찰한 스킬 이름 목록, 메모)로 읽는다.

    이름 목록이 없는 기록(구조 이전의 자유 문자열)은 **대조할 수 없다** — 그때는 목록을 None 으로
    돌려서 doctor 가 "관찰됨" 이라고 말하지 못하게 한다. 텍스트가 있다는 것은 관찰의 증거가 아니다.
    실재하지 않는 증거 경로는 그대로 인쇄하지 않고 실재하지 않는다는 사실을 붙여 인쇄한다.
    """
    if entry is None:
        return None, ""
    if isinstance(entry, dict):
        note = str(entry.get("note") or "").strip()
        ref = str(entry.get("evidence") or "").strip()
        if ref:
            mark = "" if entry.get("evidence_exists") else " — 실재하지 않는다"
            note = (note + f" (증거: {ref}{mark})").strip()
        names = entry.get("skills")
        if isinstance(names, list):
            return sorted(str(n) for n in names), note
        return None, note
    return None, str(entry).strip()


def runtime_load_mark(probe, entry):
    """스킬 파일 목록과 관찰 기록을 **이름으로 대조**해 인쇄할 판정 토큰을 만든다.

    관찰 기록이 덮지 못한 스킬이 하나라도 있으면 "관찰됨" 이라는 단어를 쓰지 않는다 —
    10개를 관찰한 기록으로 12개의 로드를 주장할 수는 없다(K-51). 정직한 문장을 메모 안에 적어 두는
    것으로는 부족하다: 한 줄 요약만 읽는 사람에게는 판정 토큰이 전부다.

    이름 목록만으로도 부족하다 — 이름 두 개를 손으로 더하면 '관찰됨' 이 된다. 그래서 기록이 가리키는
    증거(`evidence:`)를 요구하고 그 경로의 실재를 검사한다: 없거나 실재하지 않으면 대조 불가다.
    실재 여부는 `observations()` 가 읽을 때 계산해 `evidence_exists` 로 넣어 둔다.
    """
    names, note = _observed_entry(entry)
    if entry is None:
        return "**미관찰**", note
    if names is None:
        return "**대조 불가** — 관찰 기록에 스킬 이름 목록(skills:)이 없다", note
    ref = str((entry.get("evidence") if isinstance(entry, dict) else "") or "").strip()
    seen = sorted(set(names) & set(probe["skills"]))
    missing = sorted(set(probe["skills"]) - set(names))
    extra = sorted(set(names) - set(probe["skills"]))
    count = f"{len(seen)}/{probe['count']}개"
    if missing:
        mark = f"**부분 관찰** {count} · 미관찰 {' · '.join(missing)}"
    elif not ref:
        mark = f"**대조 불가** {count} — 이름은 다 덮지만 관찰 기록에 증거(evidence:)가 없다. 자기 신고뿐이다"
    elif not entry.get("evidence_exists"):
        mark = f"**대조 불가** {count} — 관찰 기록이 지목한 증거가 실재하지 않는다"
    else:
        mark = f"관찰됨 {count}"
    if extra:
        mark += f" · 기록에만 있는 이름 {' · '.join(extra)}"
    return mark, note


def doctor(root=None):
    """전체 진단. 반환값은 렌더링과 테스트가 함께 쓴다."""
    root = Path(root) if root else _project_root()
    from .compile import check_compiled
    from .provenance import check_notices, check_provenance_ids, check_vendor

    vendor_f, vendor_c = check_vendor(root)
    prov_f, _ = check_provenance_ids(root)
    conflicts, ran = check_conflicts(root)
    return {
        "runtimes": probe_runtimes(),
        "skills": probe_skill_files(root),
        "capabilities": probe_capabilities(root),
        "observed_load": observations(root),
        "attach": {
            "compile": [list(f) for f in check_compiled(root)],
            "vendor": [list(f) for f in vendor_f] + [list(f) for f in prov_f],
            "notices": [list(f) for f in check_notices(root)],
            "vendor_files": vendor_c["files"],
        },
        "conflicts": {"findings": [list(f) for f in conflicts], "fixtures_ran": ran},
    }


def format_report(rep):
    out = ["# romeo doctor", "", "## 런타임"]
    for r in rep["runtimes"]:
        out.append(f"  {'✓' if r['ok'] else '✗'} {r['name']:<7} {r['detail']}  — {r['why']}")

    out += ["", "## 스킬 파일 (파일 수준. 실제 로드는 이 검사로 증명되지 않는다)"]
    observed = rep.get("observed_load") or {}
    unproven = []
    for s in rep["skills"]:
        mark, note = runtime_load_mark(s, observed.get(s["runtime"]))
        if "관찰됨" not in mark:
            unproven.append(s["runtime"])
        out.append(f"  {s['runtime']:<7} {s['count']}개 · {s['dir']} · 런타임 로드 {mark}")
        if note:
            out.append(f"      기록: {note}")
        for p in s["problems"]:
            out.append(f"      ✗ {p}")

    a = rep["attach"]
    out += ["", "## 부착 상태"]
    for key, label in (("compile", "컴파일 산출물"), ("vendor", "vendor 원문·출처"), ("notices", "제3자 고지")):
        n = len(a[key])
        out.append(f"  {'✓' if n == 0 else '✗'} {label}: {'일치' if n == 0 else f'{n}건 불일치'}")
        for f in a[key][:5]:
            out.append(f"      {f[0]} {f[1]} — {f[3] if len(f) > 3 else ''}")

    caps = rep.get("capabilities") or []
    if caps:
        out += ["", "## 능력 프로브 (설치 흔적만 본다)"]
        for cap in caps:
            out.append(f"  · {cap['id']}: {cap['label']} — {cap['detail']}"
                       + (f" ({cap['marker']})" if cap.get("marker") else ""))
            if cap["label"] != "present":
                continue
            for field, values in (cap.get("reads") or {}).items():
                out.append(f"      {field}: " + (", ".join(values) if values else "marker 에 기록 없음"))
            if cap.get("honesty"):
                out.append(f"      {cap['honesty']}")
        out.append("  미설치는 결함이 아니다 — 이 절은 인쇄만 하고 아래 결과에 세지 않는다.")

    c = rep["conflicts"]
    out += ["", f"## 충돌 fixture ({c['fixtures_ran']}종 실행)"]
    if not c["findings"]:
        out.append("  ✓ 충돌 0")
    for fid, where, why in [tuple(x) for x in c["findings"]]:
        out.append(f"  ✗ [{fid}] {where} — {why}")

    env = doctor_problem_count(rep, "environment")
    repo = doctor_problem_count(rep, "repository")
    out += ["",
            f"결과 · 저장소: {'PASS' if repo == 0 else f'{repo}건'}"
            f" · 이 머신의 런타임: {'PASS' if env == 0 else f'{env}건 없음'}"]
    if env and not repo:
        out.append("저장소는 정상이다. 런타임 부재는 이 머신의 문제이지 저장소의 문제가 아니다(CI 러너에는 없는 것이 정상).")
    if not observed:
        out.append("주의: 런타임이 스킬을 실제로 로드하는지는 아직 관찰되지 않았다(A-11).")
    elif unproven:
        out.append(f"주의: {' · '.join(unproven)} 의 런타임 로드는 아직 대조되지 않았다 — "
                   f"위 줄의 '미관찰'·'대조 불가'·'미관찰 <이름>' 은 그 런타임에서 로드가 확인된 적이 "
                   f"없다는 뜻이다(A-11).")
    return "\n".join(out)


def doctor_problem_count(rep, scope="all"):
    """문제 수. 두 부류는 성격이 다르므로 합칠지 나눌지 부르는 쪽이 정한다.

    - environment: 이 머신에 런타임이 있는가. CI 러너에는 없는 것이 정상이다.
    - repository: 저장소 내용이 맞는가. 어느 머신에서든 같아야 한다.
    """
    a = rep["attach"]
    env = sum(1 for r in rep["runtimes"] if not r["ok"])
    repo = (sum(len(s["problems"]) for s in rep["skills"])
            + sum(len(a[k]) for k in ("compile", "vendor", "notices"))
            + len(rep["conflicts"]["findings"]))
    return {"environment": env, "repository": repo, "all": env + repo}[scope]
