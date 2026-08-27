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
    findings = []
    needed = fx.get("requires_override_key")
    have = needed in _override_keys(root)
    for f in _projected_skill_files(root):
        text = f.read_text(encoding="utf-8", errors="replace")
        for pat in fx["patterns"]:
            if pat in text and not have:
                findings.append((fx["id"], str(f.relative_to(root)),
                                 f"'{pat}' 를 가리키는데 bindings.yaml 에 overrides.{needed} 가 없다"))
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


CHECKERS = {"pattern_requires_override": _check_c1,
            "no_auto_trigger": _check_c2,
            "collision": _check_c3}


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


def observations(root):
    p = root / OBSERVATIONS_PATH
    return (load_any(p) or {}).get("runtime_load") or {} if p.exists() else {}


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
    for s in rep["skills"]:
        seen = observed.get(s["runtime"])
        mark = "관찰됨" if seen else "**미관찰**"
        out.append(f"  {s['runtime']:<7} {s['count']}개 · {s['dir']} · 런타임 로드 {mark}"
                   + (f" ({seen})" if seen else ""))
        for p in s["problems"]:
            out.append(f"      ✗ {p}")

    a = rep["attach"]
    out += ["", "## 부착 상태"]
    for key, label in (("compile", "컴파일 산출물"), ("vendor", "vendor 원문·출처"), ("notices", "제3자 고지")):
        n = len(a[key])
        out.append(f"  {'✓' if n == 0 else '✗'} {label}: {'일치' if n == 0 else f'{n}건 불일치'}")
        for f in a[key][:5]:
            out.append(f"      {f[0]} {f[1]} — {f[3] if len(f) > 3 else ''}")

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
