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

from . import HARNESS_ROOT
from .attach import RUNBOOK_REL
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
             "honesty": str(spec.get("honesty") or ""), "part": spec.get("part"),
             "title": str(spec.get("title") or ""),
             "alternatives": [str(a) for a in (spec.get("alternatives") or [])]}
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


def adapter_markers(root):
    """어댑터가 선언한 능력 흔적 경로 → `{능력 id: [(런타임 id, 경로), ...]}`.

    **경로를 아는 곳은 어댑터뿐이다.** 코어(`core/policy/capabilities.yaml`)는 그 능력이 무엇이고
    없을 때 무엇으로 대신하는지만 안다 — 런타임 경로를 코어가 알면 그것이 곧 도구명이다(C-C6).
    어댑터가 그 능력에 경로를 주지 않으면 그 런타임에서는 `absent` 다. 빈 목록은 키를 지운 것과 다르다:
    앞은 '모른다고 적은 결정' 이고 뒤는 '적지 않아서 아무도 안 본 사고' 다."""
    from .compile import load_adapters

    out = {}
    for adapter in load_adapters(Path(root)):
        rid = str(adapter.get("id") or adapter["_dir"].name)
        for cap_id, paths in ((adapter.get("capability_markers") or {})).items():
            out.setdefault(str(cap_id), []).append((rid, [str(p) for p in (paths or [])]))
    return out


def _probe_adapter_marker(root, cap_id, spec, markers=None):
    """어댑터가 준 흔적 경로를 **읽기만** 한다. 만들지 않는다(자동 설치 금지).

    라벨은 여전히 `present`·`absent` 둘뿐이다. 한 런타임에서라도 흔적이 있으면 `present` 이고,
    어느 쪽에 있고 어느 쪽에 없는지는 `detail` 과 `by_runtime` 이 그대로 말한다 — 라벨 하나로
    두 런타임의 차이를 뭉개지 않는다(D-68)."""
    root = Path(root)
    entry = {"id": cap_id, "kind": spec.get("kind"), "marker": "",
             "label": "absent", "detail": str(spec.get("absent_detail") or "흔적 경로 없음"),
             "reads": {}, "honesty": str(spec.get("honesty") or ""), "part": spec.get("part"),
             "title": str(spec.get("title") or ""),
             "alternatives": [str(a) for a in (spec.get("alternatives") or [])],
             "by_runtime": {}}
    declared = (markers if markers is not None else adapter_markers(root)).get(cap_id) or []
    if not declared:
        entry["detail"] = "어댑터가 흔적 경로를 주지 않았다 — 이 저장소의 어느 런타임에서도 확인할 수 없다"
        return entry
    found, notes = [], []
    for rid, paths in sorted(declared):
        hit = next((p for p in paths if (root / p).is_file()), None)
        entry["by_runtime"][rid] = {"paths": paths, "label": "present" if hit else "absent",
                                    "marker": hit or ""}
        if hit:
            found.append(f"{rid}: {hit}")
        else:
            notes.append(f"{rid}: " + (" · ".join(paths) + " 없음" if paths else "경로 선언 없음"))
    if found:
        entry["label"] = "present"
        entry["marker"] = found[0].split(": ", 1)[1]
        entry["detail"] = "흔적 확인 — " + " · ".join(found) + (" · " + " · ".join(notes) if notes else "")
    else:
        entry["detail"] = " · ".join(notes)
    return entry


CAPABILITY_KINDS = {"install_trace": _probe_install_trace,
                    "adapter_marker": _probe_adapter_marker}


def probe_capabilities(root=None, harness_root=None):
    """`core/policy/capabilities.yaml` 의 프로브를 실행한다.

    반환값의 `label` 은 정책표의 `result_labels` 안에서만 나온다(`present`·`absent`).
    **미설치는 결함이 아니다** — 부르는 쪽은 이 결과를 문제 수에 더하지 않는다.

    루트가 둘인 이유: **무엇을 보는가**(능력 카탈로그·어댑터 선언)는 하네스의 내용이고,
    **거기 있는가**(흔적 파일)는 작업 대상 저장소의 상태다. 하네스를 부착한 프로젝트에서는 둘이 다르다 —
    한 루트로 뭉치면 부착된 프로젝트에서 카탈로그를 찾지 못해 모든 능력이 '프로브 없음' 이 된다.
    `harness_root` 를 주지 않으면 이 저장소처럼 둘이 같은 경우로 본다.
    """
    root = Path(root) if root else _project_root()
    harness_root = Path(harness_root) if harness_root else root
    caps_by_group = load_capabilities(harness_root) or {}
    markers = adapter_markers(harness_root) if caps_by_group else {}
    out = []
    for group, caps in sorted(caps_by_group.items()):
        for name, spec in sorted((caps or {}).items()):
            cap_id = f"{group}.{name}"
            kind = (spec or {}).get("kind")
            fn = CAPABILITY_KINDS.get(kind)
            if not fn:
                out.append({"id": cap_id, "kind": kind, "marker": "",
                            "label": "absent", "detail": f"모르는 프로브 kind: {kind}",
                            "reads": {}, "honesty": "", "part": (spec or {}).get("part"),
                            "title": str((spec or {}).get("title") or ""), "alternatives": []})
                continue
            kwargs = {"markers": markers} if kind == "adapter_marker" else {}
            out.append(_plain(fn(root, cap_id, spec, **kwargs)))
    return out


def harness_owned(root):
    """`.harness/compiled.yaml` 의 `outputs` — **하네스가 놓은 것**의 목록이다.

    부착 검사의 대상을 이 목록으로 좁힌다. 대상 저장소가 원래 갖고 있던 자산은 하네스의 판정에
    들어가지 않는다 — 2026-09-04 실측에서 대상의 기존 스킬 8개가 부착 실패로 세어졌다(Q-55).
    목록을 읽을 수 없으면 `None` 을 돌려주고, 그때는 **좁히지 않는다**(부재를 면제로 읽지 않는다).
    """
    p = Path(root) / ".harness/compiled.yaml"
    if not p.exists():
        return None
    try:
        data = load_any(p) or {}
    except Exception:
        return None
    outputs = data.get("outputs")
    if not isinstance(outputs, list):
        return None
    return [rel for rel in outputs if isinstance(rel, str) and rel]


def _is_owned(path: Path, root: Path, owned):
    """`path` 가 하네스가 놓은 산출물 안에 있는가. 심링크는 **놓인 자리**를 기준으로 본다."""
    if owned is None:
        return True
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return False
    for o in owned:
        o = o.rstrip("/")
        if rel == o or rel.startswith(o + "/"):
            return True
    return False


def probe_skill_files(root, harness_root=None):
    """두 런타임의 스킬 디렉터리를 파일 수준으로 검사한다. 로드 여부는 알 수 없다.

    **검사 종류는 하나도 줄이지 않는다** — 목록 밖의 것도 같은 검사를 돌린다. `problems` 는 그 전부를
    담고(이 자리의 뜻은 바뀌지 않는다), 판정에 세는 것은 `owned_problems` 뿐이다.
    범위를 좁히는 것과 검사를 없애는 것은 다르다.
    """
    from . import frontmatter as fm
    from .compile import load_adapters

    # **어댑터 선언은 하네스가 소유한다** — 대상에는 `adapters/` 가 복제되지 않으므로(참조 부착),
    # 거기서 읽으면 스킬 디렉터리를 하나도 찾지 못하고 「문제 0건」이 된다. 검사할 곳은 `root` 다.
    hr = Path(harness_root) if harness_root else root
    owned = harness_owned(root)
    out = []
    for adapter in load_adapters(hr):
        d = root / adapter["skills_dir"]
        skills, problems, foreign = [], [], []
        if not d.is_dir():
            out.append({"runtime": adapter["id"], "dir": adapter["skills_dir"], "count": 0,
                        "problems": ["디렉터리가 없다"], "owned_problems": ["디렉터리가 없다"],
                        "foreign_problems": [], "skills": []})
            continue
        for sk in sorted(d.glob("*/SKILL.md")):
            name_dir = sk.parent.name
            bucket = problems if _is_owned(sk, root, owned) else foreign
            meta, _ = fm.split(sk.read_text(encoding="utf-8"))
            if not meta:
                bucket.append(f"{name_dir}: frontmatter 없음 — discovery 안 된다")
                continue
            if not meta.get("name"):
                bucket.append(f"{name_dir}: name 없음")
            if not (meta.get("description") or "").strip():
                bucket.append(f"{name_dir}: description 없음 — 라우터가 켤 근거가 없다")
            if sk.is_symlink() or sk.parent.is_symlink():
                bucket.append(f"{name_dir}: 심링크 — Windows 에서 깨진다")
            skills.append(meta.get("name") or name_dir)
        out.append({"runtime": adapter["id"], "dir": adapter["skills_dir"], "count": len(skills),
                    "problems": problems + foreign, "owned_problems": problems,
                    "foreign_problems": foreign, "skills": sorted(skills)})
    return out


def _projected_skill_files(root, harness_root=None):
    """대상에 **투영된** 스킬 파일. 어댑터 선언은 하네스에서 읽고 파일은 `root` 에서 찾는다."""
    from .compile import load_adapters
    hr = Path(harness_root) if harness_root else root
    files = []
    for adapter in load_adapters(hr):
        d = root / adapter["skills_dir"]
        if d.is_dir():
            files += [f for f in sorted(d.rglob("*")) if f.is_file() and f.suffix == ".md"]
    return files


def _override_keys(root):
    """override 정본은 하네스가 소유한다 — 대상이 자기 override 를 선언해 검사를 피하지 못한다."""
    b = Path(root) / ".harness/bindings.yaml"
    if not b.exists():
        return set()
    return set((load_any(b) or {}).get("overrides") or {})


def _check_c1(root, fx, hr=None):
    hr = Path(hr) if hr else root
    """패턴이 있으면 대응 override 가 있어야 한다. 원문을 고칠 수 없으므로 금지가 아니라 흡수로 검사한다."""
    findings = []
    keys = _override_keys(hr)
    pats = fx["patterns"]
    # 리스트면 fixture 하나가 단일 override 를 요구하고, 매핑이면 패턴마다 다른 override 를 요구한다.
    if isinstance(pats, dict):
        needed_for = dict(pats)
    else:
        needed_for = {p: fx.get("requires_override_key") for p in pats}
    for f in _projected_skill_files(root, hr):
        text = f.read_text(encoding="utf-8", errors="replace")
        for pat, needed in needed_for.items():
            if pat in text and needed not in keys:
                findings.append((fx["id"], str(f.relative_to(root)),
                                 f"'{pat}' 를 지시하는데 bindings.yaml 에 overrides.{needed} 가 없다"))
    return findings


def _check_c2(root, fx, hr=None):
    hr = Path(hr) if hr else root
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
    for f in _projected_skill_files(root, hr):
        low = f.read_text(encoding="utf-8", errors="replace").lower()
        for phrase in fx.get("forbidden_phrases") or []:
            if phrase.lower() in low:
                findings.append((fx["id"], str(f.relative_to(root)),
                                 f"'{phrase}' — 스스로 켜지려는 지시가 남아 있다"))
    return findings


def _check_c3(root, fx, hr=None):
    hr = Path(hr) if hr else root
    from .compile import MANAGED_START, load_adapters
    findings = []
    if fx.get("check_duplicate_skill_names"):
        for probe in probe_skill_files(root, hr):
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


def _recommend_pairs(root, fx, hr=None):
    hr = Path(hr) if hr else root
    """정책표의 **모든** 부품이 추천하는 (부품 id, 스킬 id) 쌍.

    한 부품만 보면 다음에 추가되는 부품이 같은 실수를 반복한다. 정책표 파일을 직접 읽는다 —
    로더 캐시를 거치면 같은 프로세스 안에서 파일을 고쳐 만든 위반이 반영되지 않는다."""
    data = load_any(hr / fx.get("packages_file", "core/policy/packages.yaml")) or {}
    pairs = []
    for pid, part in sorted((data.get("parts") or {}).items()):
        for rid in ((part or {}).get("recommends") or []):
            pairs.append((str(pid), str(rid)))
    return pairs


def _check_c5(root, fx, hr=None):
    hr = Path(hr) if hr else root
    """부품이 설치될 자리를 컴파일 산출물이 점유하고 있는가.

    prune 은 `.harness/compiled.yaml` 에 적힌 것만 지운다. 그래서 위험한 것은 두 가지다 —
    설치 디렉터리 **자체**(또는 그 조상)를 산출물로 적는 것, 그리고 설치될 스킬과 **같은 이름**을
    그 안에 두는 것. 앞은 남의 파일을 지우고, 뒤는 어느 쪽이 로드될지 알 수 없게 만든다."""
    findings = []
    state = load_any(root / fx.get("state_file", ".harness/compiled.yaml")) or {}
    outputs = [str(o).strip("/") for o in (state.get("outputs") or [])]
    install_dirs = [str(d).strip("/") for d in (fx.get("install_dirs") or [])]
    names = {rid for _pid, rid in _recommend_pairs(root, fx, hr)}
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


def _check_c6(root, fx, hr=None):
    hr = Path(hr) if hr else root
    """추천 목록의 각 id 가 accepted 판정의 출처에서 왔는가, 보류·기각된 것은 아닌가."""
    findings = []
    imports = (load_any(hr / fx.get("imports_file", "provenance/imports.yaml")) or {}).get("imports") or []
    forbidden_statuses = set(fx.get("forbidden_statuses") or [])
    allowed_key = fx.get("allowed_from", "router_recommends")
    allowed_status = fx.get("allowed_status", "accepted")
    forbidden = {str(e.get("id")) for e in imports if e.get("status") in forbidden_statuses}
    allowed = {str(r) for e in imports if e.get("status") == allowed_status
               for r in (e.get(allowed_key) or [])}
    where = fx.get("packages_file", "core/policy/packages.yaml")
    for pid, rid in _recommend_pairs(root, fx, hr):
        if rid in forbidden:
            findings.append((fx["id"], f"{where}:parts.{pid}",
                             f"'{rid}' 는 보류·기각 판정인데 추천 목록에 있다 — 기획 원본이 둘이 된다"))
        elif rid not in allowed:
            findings.append((fx["id"], f"{where}:parts.{pid}",
                             f"'{rid}' 의 출처가 없다 — {fx.get('imports_file')} 의 "
                             f"{allowed_status} 항목 {allowed_key} 에 없다"))
    return findings


def _check_c7(root, fx, hr=None):
    hr = Path(hr) if hr else root
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


def check_conflicts(root=None, harness_root=None):
    """충돌 fixture 를 실행한다. (findings, 실행한 fixture 수).

    **fixture 는 하네스에서 읽고 대상은 `root` 를 검사한다.** 둘을 같은 곳에서 읽으면
    부착 대상에는 `fixtures/` 가 없으므로 **0종 실행으로 통과한다** — 부재가 일치로 읽히던
    Q-53 과 같은 모양이다. 읽는 곳을 옮기면 같은 fixture 가 어느 저장소에서든 돈다.
    """
    root = Path(root) if root else _project_root()
    hr = Path(harness_root) if harness_root else root
    d = hr / CONFLICTS_DIR
    findings, ran = [], 0
    for f in sorted(d.glob("*.yaml")) if d.is_dir() else []:
        fx = load_any(f) or {}
        fn = CHECKERS.get(fx.get("kind"))
        if not fn:
            findings.append(("?", str(f.relative_to(hr)), f"모르는 kind: {fx.get('kind')}"))
            continue
        ran += 1
        findings += fn(root, fx, hr)
    if ran == 0:
        # 충돌 finding 은 (id, where, why) 3-tuple 이다 — format_report 가 그 모양으로 읽는다.
        findings.append(("CONFLICT_FIXTURES_MISSING", str(CONFLICTS_DIR),
                         f"충돌 fixture 를 하나도 실행하지 못했다 ({hr / CONFLICTS_DIR}) — 0종 실행은 충돌 0 이 아니다"))
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


#: 40자 커밋 식별자. **대소문자를 모두 받는다** — git 은 소문자로 내지만 이 값은 손으로 쓸 수 있고,
#: 소문자만 받으면 대문자가 섞인 그럴듯한 거짓 값에서 실재성 검사를 조용히 건너뛴다(1회차 검토자 finding).
_HEX40 = re.compile(r"^[0-9a-fA-F]{40}$")


def _commit_lookup(sha, harness_root=None):
    """`sha` 가 **판정 명령을 실행한 하네스 저장소의 로컬 이력**에 있는가.

    셋을 구분한다 — `True`(있다) · `False`(없다) · `None`(확인할 수 없다).
    판정하는 하네스 자신이 git 이 아니면 실재 여부를 **모르는** 것이지 없는 것이 아니다.
    모르는 것을 아는 것처럼 말하지 않는다(AGENTS.core §5 · K-68).
    """
    from . import gitinfo

    root = Path(harness_root) if harness_root else HARNESS_ROOT
    if not gitinfo.is_repo(root):
        return None
    code, _ = _run(["git", "-C", str(root), "cat-file", "-e", f"{sha}^{{commit}}"])
    return None if code is None else code == 0


def check_attach_complete(root, harness_root=None):
    """부착 정본(`scenarios/10-attach-payload.md` 의 「놓는 것」)과 대조한다.

    **부재를 일치로 읽지 않는다.** 산출물 0개가 목록 0개와 맞아떨어져 빈 저장소가 통과하던 자리다(Q-53).
    요구는 이 함수가 아니라 그 문서가 소유하고, 여기서는 매번 읽는다 — 목록을 코드에 복사하면
    문서를 고쳐도 판정이 따라오지 않는다(AGENTS.core §11).
    """
    from . import attach as attach_mod

    root = Path(root)
    findings = []
    try:
        gone = attach_mod.missing(root, attach_mod.runbook_path(harness_root))
    except (AssertionError, OSError) as exc:
        return [("ATTACH_MANIFEST_UNREADABLE", attach_mod.RUNBOOK_REL, "", str(exc))]
    for rel in gone:
        findings.append(("ATTACH_INCOMPLETE", rel, "",
                         "부착 정본이 요구하는데 이 루트에 없다 — 붙지 않았거나 덜 붙었다"))

    state = root / ".harness/compiled.yaml"
    if state.exists():
        try:
            data = load_any(state) or {}
        except Exception:
            data = {}
        rev = data.get("harness_revision")
        if not isinstance(rev, str) or not rev.strip():
            findings.append(("ATTACH_REVISION_MISSING", ".harness/compiled.yaml", "",
                             "어느 하네스 리비전이 붙었는지 기록이 없다 — `romeo compile --root <대상>` 으로 다시 만든다"))
        elif _HEX40.match(rev.strip()) and _commit_lookup(rev.strip(), harness_root) is False:
            findings.append(("ATTACH_REVISION_UNKNOWN", ".harness/compiled.yaml", rev.strip(),
                             "기록된 리비전이 이 하네스 저장소의 로컬 이력에 없다"))
    return findings


def doctor(root=None, harness_root=None):
    """전체 진단. 반환값은 렌더링과 테스트가 함께 쓴다.

    **읽는 곳과 쓰는 곳이 다르다.** 정책표·출처·바인딩·fixture 는 `harness_root` 에서 읽고,
    검사 대상은 `root` 다. 둘을 같은 곳에서 읽으면 부착 대상에서는 원본이 없어 검사가
    0건으로 통과한다 — 부재가 일치로 읽히던 Q-53 과 같은 모양이다.
    """
    root = Path(root) if root else _project_root()
    hr = Path(harness_root) if harness_root else root
    from .compile import check_compiled
    from .provenance import check_notices, check_provenance_ids, check_vendor

    completeness = [list(f) for f in check_attach_complete(root, harness_root=hr)]
    # 시나리오 10 이 적은 순서 그대로다 — 「1번이 판정이고, 2~4번은 그 위에서만 의미가 있다」.
    # 붙지 않은 루트에서 산출물·vendor·고지를 대조하는 것은 없는 것을 없는 것과 맞춰 보는 일이고,
    # 실제로는 대조하다 예외로 죽는다(소스 트리가 없으므로).
    # 건너뛰는 조건은 **경로 부재**뿐이다 — 리비전이 없는 것은 그 대조를 막지 않는다.
    if any(f[0] == "ATTACH_INCOMPLETE" for f in completeness):
        return {
            "runtimes": probe_runtimes(),
            "skills": [],
            "capabilities": [],
            "observed_load": observations(root),
            "attach": {"completeness": completeness, "compile": [], "vendor": [], "notices": [],
                       "vendor_files": [], "skipped": "부착이 불완전해 산출물·vendor·고지·스킬 대조를 하지 않았다"},
            "conflicts": {"findings": [], "fixtures_ran": 0},
        }

    vendor_f, vendor_c = check_vendor(hr)
    prov_f, _ = check_provenance_ids(hr)
    conflicts, ran = check_conflicts(root, harness_root=hr)
    return {
        "runtimes": probe_runtimes(),
        "skills": probe_skill_files(root, hr),
        "capabilities": probe_capabilities(root),
        "observed_load": observations(root),
        "attach": {
            "completeness": completeness,
            "compile": [list(f) for f in check_compiled(root, harness_root=hr)],
            "vendor": [list(f) for f in vendor_f] + [list(f) for f in prov_f],
            "notices": [list(f) for f in check_notices(root, harness_root=hr)],
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
        for p in s.get("owned_problems", s["problems"]):
            out.append(f"      ✗ {p}")
        for p in s.get("foreign_problems") or []:
            out.append(f"      · {p}  (대상의 기존 자산 — 부착 판정에 세지 않는다)")

    a = rep["attach"]
    out += ["", "## 부착 상태"]
    comp = a.get("completeness") or []
    out.append(f"  {'✓' if not comp else '✗'} 부착 정본(`{RUNBOOK_REL}` 의 「놓는 것」): "
               + ("일치" if not comp else f"{len(comp)}건"))
    for f in comp:
        out.append(f"      {f[0]} {f[1]} — {f[3] if len(f) > 3 else ''}")
    if a.get("skipped"):
        out.append(f"      → {a['skipped']}")
    for key, label in (("compile", "컴파일 산출물"), ("vendor", "vendor 원문·출처"), ("notices", "제3자 고지")):
        if a.get("skipped"):
            out.append(f"  — {label}: 대조하지 않음")
            continue
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
                for alt in (cap.get("alternatives") or [])[:3]:
                    out.append(f"      대안: {alt}")
                continue
            for field, values in (cap.get("reads") or {}).items():
                out.append(f"      {field}: " + (", ".join(values) if values else "marker 에 기록 없음"))
            if cap.get("honesty"):
                out.append(f"      {cap['honesty']}")
        out.append("  미설치는 결함이 아니다 — 이 절은 인쇄만 하고 아래 결과에 세지 않는다.")

    c = rep["conflicts"]
    if a.get("skipped"):
        out += ["", "## 충돌 fixture", "  — 대조하지 않음"]
        c = {"findings": []}
    else:
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
    repo = (sum(len(s.get("owned_problems", s["problems"])) for s in rep["skills"])
            + sum(len(a[k]) for k in ("completeness", "compile", "vendor", "notices"))
            + len(rep["conflicts"]["findings"]))
    return {"environment": env, "repository": repo, "all": env + repo}[scope]
