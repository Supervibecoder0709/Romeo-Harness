"""어댑터 컴파일 — 코어(벤더 중립) → 런타임별 산출물.

원본은 `core/` 와 `vendor/` 이고, 산출물(`CLAUDE.md`·`AGENTS.md`·`.claude/skills/**`·`.agents/skills/**`)은
언제든 다시 만들 수 있어야 한다. 두 가지 규칙이 이걸 보장한다.

- **지침 파일**(`CLAUDE.md`·`AGENTS.md`)은 managed 마커 안쪽만 하네스가 소유한다. 마커 밖 텍스트는 보존된다.
- **스킬 파일**은 전체가 산출물이다. 손으로 고치면 다음 컴파일에서 사라진다 — 고칠 것은 `core/` 나 어댑터 정의다.

vendor 스킬은 원문 그대로 복사한다(수정 0). 원문을 고쳐야 하는 부분은 `.harness/bindings.yaml` 의
override 로 적고, 컴파일이 그것을 지침 파일에 인쇄한다 — 그래야 원문을 건드리지 않고도 규칙이 실제로 읽힌다.
"""
import hashlib
import re
import shutil
from pathlib import Path

from . import __version__
from .util import load_any, dump_yaml, project_root as _project_root

MANAGED_START = "<!-- romeo:managed start"
MANAGED_END = "<!-- romeo:managed end -->"
MANAGED_RE = re.compile(
    re.escape(MANAGED_START) + r".*?-->\n(?P<body>.*?)\n?" + re.escape(MANAGED_END),
    re.DOTALL,
)
STATE_PATH = ".harness/compiled.yaml"
ADAPTERS_DIR = "adapters"
GENERATED_NOTE = "<!-- 이 파일은 `romeo compile` 산출물이다. 직접 고치지 않는다 — 고칠 곳은 core/ 와 adapters/ 다. -->"


def _sha8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def replace_managed_block(text, content, source, version=None):
    """managed 블록만 교체한다. 마커 밖은 그대로 둔다. 블록이 없으면 끝에 붙인다."""
    version = version or __version__
    marker = f"{MANAGED_START} v{version} source={source} sha={_sha8(content)} -->"
    block = f"{marker}\n{content}\n{MANAGED_END}"
    if MANAGED_RE.search(text):
        return MANAGED_RE.sub(lambda _: block, text, count=1)
    sep = "" if text.endswith("\n\n") or not text else ("\n" if text.endswith("\n") else "\n\n")
    return f"{text}{sep}{block}\n"


def _strip_frontmatter(text):
    from . import frontmatter as fm
    meta, body = fm.split(text)
    return meta or {}, body.lstrip("\n")


def load_adapters(root):
    out = []
    for f in sorted((root / ADAPTERS_DIR).glob("*/adapter.yaml")):
        data = load_any(f)
        data["_dir"] = f.parent
        out.append(data)
    return out


def accepted_vendor_skills(root):
    """채택(accepted)된 verbatim 스킬의 (이름, 원본 디렉터리) 목록."""
    from .provenance import load_imports
    _, data = load_imports(root)
    out = []
    for item in data["imports"]:
        if item.get("status") != "accepted" or item.get("adoption") != "verbatim":
            continue
        local = (item.get("local_path") or "").rstrip("/")
        if not local.startswith("vendor/"):
            continue
        src = root / local
        if src.is_dir():
            out.append((src.name, src))
    return sorted(out)


def _render_instructions(root, adapter, bindings):
    """지침 파일 managed block 본문 — 두 런타임이 같은 내용을 받는다."""
    core = root / "core/principles/AGENTS.core.md"
    _, principles = _strip_frontmatter(core.read_text(encoding="utf-8"))

    lines = ["# Romeo 하네스 규칙 (자동 생성)", "",
             f"원본은 `core/principles/AGENTS.core.md` 이고 이 블록은 `romeo compile` 이 만든다.",
             "**마커 안을 고치지 않는다** — 다음 컴파일에서 사라진다. 마커 밖에 쓴 내용은 보존된다.",
             "", principles.rstrip(), "", "---", "", "## 역할 (D-68)", "",
             "| 역할 | 런타임 | 쓰기 | 어떻게 강제하나 |", "| --- | --- | --- | --- |"]
    for name, role in (bindings.get("roles") or {}).items():
        enforce = role.get("enforcement") or ("작업 공간 쓰기 허용" if role.get("write") else "-")
        lines.append(f"| `{name}` | {role.get('runtime','?')} | "
                     f"{'예' if role.get('write') else '**아니오**'} | {enforce} |")
    swap = bindings.get("parity_swap") or {}
    if swap:
        lines += ["", f"역할 교체 재실행: implementer={swap.get('implementer')} · "
                      f"reviewer={swap.get('reviewer')}. 같은 판정이 나와야 동등성 게이트를 통과한다.", ""]

    overrides = bindings.get("overrides") or {}
    if overrides:
        lines += ["## 부품 override (원문보다 이 규칙이 우선한다)", "",
                  "아래 부품은 원문을 고칠 수 없다(수정 0). 원문의 지시와 다음 규칙이 충돌하면 **다음 규칙을 따른다.**", ""]
        for key, ov in overrides.items():
            targets = ", ".join(f"`{t}`" for t in (ov.get("applies_to") or [])) or "-"
            detail = (ov.get("native_tool") or ov.get("target") or ov.get("policy")
                      or ov.get("dispatch_tool") or "")
            lines.append(f"- **{key}** → {detail}")
            if ov.get("forbid_raw_git_worktree"):
                lines.append("  - raw `git worktree add/rm` 과 내장 worktree 도구를 쓰지 않는다.")
            if ov.get("denied_without_approval"):
                cmds = ", ".join(f"`{c}`" for c in ov["denied_without_approval"])
                lines.append(f"  - 승인 없이 실행하지 않는다: {cmds}")
            if ov.get("parallel_compare"):
                lines.append(f"  - 병렬 비교는 `{ov['parallel_compare']}` 를 쓴다.")
            lines.append(f"  - 대상: {targets} · 이유: {ov.get('reason','-')}")
        lines.append("")

    lines += ["## 이 저장소에서 켜져 있는 절차", "",
              "| 이름 | 출처 | 언제 |", "| --- | --- | --- |"]
    for name, cfg in (adapter.get("workflows") or {}).items():
        lines.append(f"| `{name}` | `core/workflows/{name}/SKILL.md` | 라우터 진입점 |")
    if adapter.get("project_vendor_skills"):
        for name, _src in accepted_vendor_skills(root):
            lines.append(f"| `{name}` | vendor 원문 (수정 0) | 라우터가 켤 때만 |")
    for local in (adapter.get("local_skills") or []):
        lines.append(f"| `{local['name']}` | `{local['source']}` | 라우터가 켤 때만 |")
    lines += ["", "부품 스킬은 스스로 활성화되지 않는다(K-60). 라우터가 계산한 단위·모드·영역·깊이가 켤 때만 쓴다."]
    return "\n".join(lines)


def _render_skill(root, adapter, name, cfg):
    """런타임 스킬 파일 전체. 코어 본문을 복제하지 않고 '읽고 따르라' 로 연결한다."""
    core_path = f"core/workflows/{name}/SKILL.md"
    core_text = (root / core_path).read_text(encoding="utf-8")
    meta, _ = _strip_frontmatter(core_text)
    desc = " ".join((cfg.get("description") or meta.get("description", "")).split())
    mapping = (root / cfg["mapping"]).read_text(encoding="utf-8").rstrip()

    head = (f"---\nname: {meta.get('name', name)}\ndescription: {desc}\n---\n\n"
            f"{GENERATED_NOTE}\n\n"
            f"# /{name} ({adapter['name']} 어댑터)\n\n"
            f"절차의 원본은 `{core_path}` 다. 이 파일은 그 절차를 {adapter['name']} 에서 어떻게 수행하는지만 적는다.\n")
    return replace_managed_block(head, mapping, source=cfg["mapping"])


def _render_settings(root, adapter):
    """permissions.deny 만 하네스가 소유한다. 나머지 키는 디스크의 것을 그대로 둔다."""
    import json
    ask = list(adapter.get("settings_ask") or [])
    deny = list(adapter.get("settings_deny") or [])
    path = root / adapter["settings_file"]
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8")) or {}
        except ValueError:
            data = {}
    perms = dict(data.get("permissions") or {})
    if ask:
        perms["ask"] = ask
    perms["deny"] = deny
    data["permissions"] = perms
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def _copy_tree_as_files(src: Path, dst: Path):
    """심링크를 따라가 실제 파일로 복사한다 — Windows 에서 심링크가 깨지기 때문."""
    # 디렉터리 심링크는 rmtree 로 지울 수 없다. 기존 심링크를 실제 파일로 바꾸는 것이 이 함수의 목적이므로
    # 링크 자체를 먼저 끊는다.
    if dst.is_symlink():
        dst.unlink()
    elif dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for f in sorted(src.rglob("*")):
        if f.is_dir():
            continue
        target = dst / f.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, target, follow_symlinks=True)
        if f.stat().st_mode & 0o111:
            target.chmod(target.stat().st_mode | 0o111)


def plan_outputs(root):
    """(파일 산출물 dict{path: text}, 트리 산출물 list[(src, dst)]) 를 계산한다. 쓰지는 않는다."""
    root = Path(root)
    bindings = load_any(root / ".harness/bindings.yaml") if (root / ".harness/bindings.yaml").exists() else {}
    files, trees = {}, []
    for adapter in load_adapters(root):
        files[adapter["instructions_file"]] = ("managed", _render_instructions(root, adapter, bindings),
                                               "core/principles/AGENTS.core.md")
        if adapter.get("settings_file") and (adapter.get("settings_deny") or adapter.get("settings_ask")):
            files[adapter["settings_file"]] = ("full", _render_settings(root, adapter), None)
        skills_dir = adapter["skills_dir"]
        for name, cfg in (adapter.get("workflows") or {}).items():
            files[f"{skills_dir}/{name}/SKILL.md"] = ("full", _render_skill(root, adapter, name, cfg), None)
        if adapter.get("project_vendor_skills"):
            for sname, src in accepted_vendor_skills(root):
                trees.append((src, root / skills_dir / sname))
        for local in (adapter.get("local_skills") or []):
            trees.append((root / local["source"], root / skills_dir / local["name"]))
    return files, trees


def compile_all(root=None):
    root = Path(root) if root else _project_root()
    files, trees = plan_outputs(root)
    written = []
    for rel, (mode, content, source) in sorted(files.items()):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if mode == "managed":
            old = path.read_text(encoding="utf-8") if path.exists() else ""
            path.write_text(replace_managed_block(old, content, source=source), encoding="utf-8")
        else:
            path.write_text(content, encoding="utf-8")
        written.append(rel)
    for src, dst in trees:
        _copy_tree_as_files(src, dst)
        written.append(str(dst.relative_to(root)))

    state = {
        "schema_version": 1,
        "romeo_version": __version__,
        "outputs": sorted(written),
    }
    state_path = root / STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "# `romeo compile` 산출물 목록. 손으로 고치지 않는다.\n"
        "# 여기 있는 경로는 언제든 다시 생성되므로, 고칠 곳은 core/ 와 adapters/ 다.\n---\n"
        + dump_yaml(state), encoding="utf-8")
    return sorted(written)


def check_compiled(root=None):
    """산출물이 현재 코어와 일치하는지. 마커 밖 사용자 텍스트는 보지 않는다."""
    root = Path(root) if root else _project_root()
    findings = []
    files, trees = plan_outputs(root)

    for rel, (mode, content, source) in sorted(files.items()):
        path = root / rel
        if not path.exists():
            findings.append(("COMPILE_MISSING", rel, "", "산출물이 없다"))
            continue
        current = path.read_text(encoding="utf-8")
        expected = replace_managed_block(current, content, source=source) if mode == "managed" else content
        if current != expected:
            findings.append(("COMPILE_STALE", rel, "",
                             "코어가 바뀌었거나 산출물을 손으로 고쳤다 — `romeo compile` 로 재생성"))

    for src, dst in trees:
        rel = str(dst.relative_to(root))
        if dst.is_symlink():
            # 링크가 가리키는 곳에 파일이 있어도 통과시키지 않는다 — Windows 에서 깨진다.
            findings.append(("COMPILE_SYMLINK", rel, "", "디렉터리가 심링크다 — 실제 파일이어야 한다"))
            continue
        if not dst.exists():
            findings.append(("COMPILE_MISSING", rel, "", "투영되지 않았다"))
            continue
        want = {str(f.relative_to(src)): f.read_bytes() for f in src.rglob("*") if f.is_file()}
        have = {str(f.relative_to(dst)): f for f in dst.rglob("*") if f.is_file()}
        for name in sorted(set(want) - set(have)):
            findings.append(("COMPILE_MISSING", f"{rel}/{name}", "", "원본에 있는 파일이 투영본에 없다"))
        for name in sorted(set(have) - set(want)):
            findings.append(("COMPILE_ORPHAN", f"{rel}/{name}", "", "원본에 없는 파일이 남아 있다"))
        for name in sorted(set(want) & set(have)):
            if have[name].is_symlink():
                findings.append(("COMPILE_SYMLINK", f"{rel}/{name}", "", "심링크다 — 실제 파일이어야 한다"))
            elif have[name].read_bytes() != want[name]:
                findings.append(("COMPILE_STALE", f"{rel}/{name}", "", "원본과 다르다"))

    state_path = root / STATE_PATH
    if state_path.exists():
        recorded = set((load_any(state_path) or {}).get("outputs") or [])
        current = set(files) | {str(dst.relative_to(root)) for _s, dst in trees}
        for rel in sorted(recorded - current):
            if (root / rel).exists():
                findings.append(("COMPILE_ORPHAN", rel, "", "더 이상 산출물이 아닌데 남아 있다"))
    return findings
