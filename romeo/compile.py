"""어댑터 컴파일 — 코어(벤더 중립) → 런타임별 산출물.

원본은 `core/` 와 `vendor/` 이고, 산출물(`CLAUDE.md`·`AGENTS.md`·`.claude/skills/**`·`.agents/skills/**`)은
언제든 다시 만들 수 있어야 한다. 두 가지 규칙이 이걸 보장한다.

- **지침 파일**(`CLAUDE.md`·`AGENTS.md`)은 managed 마커 안쪽만 하네스가 소유한다. 마커 밖 텍스트는 보존된다.
- **스킬 파일**은 전체가 산출물이다. 손으로 고치면 다음 컴파일에서 사라진다 — 고칠 것은 `core/` 나 어댑터 정의다.

vendor 스킬은 원문 그대로 복사한다(수정 0). 원문을 고쳐야 하는 부분은 `.harness/bindings.yaml` 의
override 로 적고, 컴파일이 그것을 지침 파일에 인쇄한다 — 그래야 원문을 건드리지 않고도 규칙이 실제로 읽힌다.
"""
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from . import __version__
from .util import load_any, dump_yaml, project_root as _project_root

MANAGED_START = "<!-- romeo:managed start"
MANAGED_END = "<!-- romeo:managed end -->"
# 줄 전체에 고정한다. 문서 중간이나 코드펜스 안의 마커 모양 텍스트를 소유 블록으로 오인하지 않는다.
START_LINE_RE = re.compile(r"^<!--\s*([a-z0-9_-]+):managed\s+start\b.*-->$", re.I)
END_LINE_RE = re.compile(r"^<!--\s*([a-z0-9_-]+):managed\s+end\s*-->$", re.I)
FENCE_RE = re.compile(r"^\s*(```|~~~)")


class CompileError(RuntimeError):
    """산출물을 쓰기 전에 멈춘다. 반쯤 쓴 상태를 만들지 않는다."""
STATE_PATH = ".harness/compiled.yaml"
ADAPTERS_DIR = "adapters"
GENERATED_NOTE = "<!-- 이 파일은 `romeo compile` 산출물이다. 직접 고치지 않는다 — 고칠 곳은 core/ 와 adapters/ 다. -->"


def _sha8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def scan_managed_blocks(text, owner="romeo"):
    """코드펜스 밖의 managed 블록을 줄 번호로 열거한다. 구조가 깨졌으면 예외를 던진다."""
    lines = text.split("\n")
    in_fence = False
    opened = None
    blocks = []
    for i, raw in enumerate(lines):
        line = raw.strip()
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = START_LINE_RE.match(line)
        if m:
            if opened is not None:
                raise CompileError(f"managed 마커가 중첩됐다 (줄 {opened[1] + 1}, {i + 1})")
            opened = (m.group(1).lower(), i)
            continue
        m = END_LINE_RE.match(line)
        if m:
            if opened is None:
                raise CompileError(f"짝 없는 managed end 마커 (줄 {i + 1})")
            blocks.append((opened[0], opened[1], i))
            opened = None
    if opened is not None:
        raise CompileError(f"닫히지 않은 managed 마커 (줄 {opened[1] + 1})")
    mine = [b for b in blocks if b[0] == owner.lower()]
    if len(mine) > 1:
        raise CompileError(f"{owner}:managed 블록이 {len(mine)}개다 — 하나만 있어야 한다")
    return blocks, (mine[0] if mine else None)


def replace_managed_block(text, content, source, version=None, owner="romeo"):
    """managed 블록만 교체한다. 마커 밖은 그대로 둔다. 블록이 없으면 끝에 붙인다."""
    version = version or __version__
    marker = f"{MANAGED_START} v{version} source={source} sha={_sha8(content)} -->"
    block = f"{marker}\n{content}\n{MANAGED_END}"

    crlf = "\r\n" in text                       # 원래 개행 스타일을 보존한다
    work = text.replace("\r\n", "\n") if crlf else text

    _all, mine = scan_managed_blocks(work, owner)
    if mine:
        lines = work.split("\n")
        out = "\n".join(lines[:mine[1]] + block.split("\n") + lines[mine[2] + 1:])
    else:
        sep = "" if work.endswith("\n\n") or not work else ("\n" if work.endswith("\n") else "\n\n")
        out = f"{work}{sep}{block}\n"
    return out.replace("\n", "\r\n") if crlf else out


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


def _owned_settings(adapter):
    """하네스가 소유하는 settings 부분. 사용자 파일을 읽지 않는 순수한 기대값이다."""
    return {
        "ask": list(adapter.get("settings_ask") or []),
        "deny": list(adapter.get("settings_deny") or []),
    }


def _load_settings(path: Path):
    """사용자 settings JSON 을 보존 병합용 입력으로 엄격하게 읽는다."""
    if not path.exists():
        if path.is_symlink():
            raise CompileError(f"{path}: 깨진 settings 심링크다")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CompileError(f"{path}: settings JSON 을 읽을 수 없다: {exc}") from exc
    if not isinstance(data, dict):
        raise CompileError(f"{path}: settings 최상위 값은 JSON object 여야 한다")
    permissions = data.get("permissions", {})
    if permissions is None:
        permissions = {}
    if not isinstance(permissions, dict):
        raise CompileError(f"{path}: permissions 는 JSON object 여야 한다")
    return data


def _render_settings(data, owned):
    """사용자 키는 보존하고 permissions.ask·deny 만 하네스 기대값으로 병합한다."""
    out = dict(data)
    permissions = dict(out.get("permissions") or {})
    permissions["ask"] = list(owned["ask"])
    permissions["deny"] = list(owned["deny"])
    out["permissions"] = permissions
    return json.dumps(out, ensure_ascii=False, indent=2) + "\n"


def _inside(root: Path, target: Path, what: str) -> Path:
    """저장소 밖으로 나가는 경로를 쓰기 전에 거부한다(K-66 — implementer 의 쓰기 범위는 작업 공간이다)."""
    joined = Path(target) if Path(target).is_absolute() else root / target
    # 검증만 resolve 로 한다. 반환은 원래 형태여야 호출부의 relative_to(root) 가 맞는다
    # (macOS 의 /var → /private/var 처럼 root 자체가 심링크일 수 있다).
    root_r, t_r = root.resolve(), joined.resolve()
    try:
        rel = t_r.relative_to(root_r)
    except ValueError:
        raise CompileError(f"{what}: '{target}' 이 저장소 밖을 가리킨다 ({t_r})")
    if not str(rel) or str(rel) == ".":
        raise CompileError(f"{what}: '{target}' 이 저장소 루트 자체다")
    return joined


def _output_rel(root: Path, target, what: str) -> str:
    """staging 결합을 우회하지 못하도록 출력 경로를 단순한 저장소 상대경로로 제한한다."""
    raw = Path(target)
    if raw.is_absolute() or not raw.parts or ".." in raw.parts:
        raise CompileError(f"{what}: '{target}' 은 저장소 상대경로여야 하고 '..'를 포함할 수 없다")
    _inside(root, raw, what)
    return str(raw)


def plan_outputs(root):
    """(파일 산출물 dict{path: text}, 트리 산출물 list[(src, dst)]) 를 계산한다. 쓰지는 않는다."""
    root = Path(root)
    bindings = load_any(root / ".harness/bindings.yaml") if (root / ".harness/bindings.yaml").exists() else {}
    files, trees = {}, []
    for adapter in load_adapters(root):
        instructions_file = _output_rel(
            root, adapter["instructions_file"], f"{adapter['id']}.instructions_file")
        skills_dir = _output_rel(root, adapter["skills_dir"], f"{adapter['id']}.skills_dir")
        settings_file = None
        if adapter.get("settings_file"):
            settings_file = _output_rel(
                root, adapter["settings_file"], f"{adapter['id']}.settings_file")
        files[instructions_file] = ("managed", _render_instructions(root, adapter, bindings),
                                    "core/principles/AGENTS.core.md")
        if settings_file and (adapter.get("settings_deny") or adapter.get("settings_ask")):
            files[settings_file] = ("settings", _owned_settings(adapter), None)
        for name, cfg in (adapter.get("workflows") or {}).items():
            rel = _output_rel(root, f"{skills_dir}/{name}/SKILL.md",
                              f"{adapter['id']}.workflows.{name}")
            files[rel] = ("full", _render_skill(root, adapter, name, cfg), None)
        if adapter.get("project_vendor_skills"):
            for sname, src in accepted_vendor_skills(root):
                rel = _output_rel(root, f"{skills_dir}/{sname}",
                                  f"{adapter['id']}.project_vendor_skills")
                trees.append((src, root / rel))
        for local in (adapter.get("local_skills") or []):
            src = _inside(root, local["source"], f"{adapter['id']}.local_skills.source")
            rel = _output_rel(root, f"{skills_dir}/{local['name']}",
                              f"{adapter['id']}.local_skills.name")
            trees.append((src, root / rel))
    return files, trees


def _previous_outputs(root):
    p = root / STATE_PATH
    if not p.exists():
        return None
    try:
        data = load_any(p) or {}
    except Exception as exc:
        raise CompileError(f"{STATE_PATH}: compiled state 를 읽을 수 없다: {exc}") from exc
    outputs = data.get("outputs")
    if not isinstance(outputs, list) or not all(isinstance(rel, str) and rel for rel in outputs):
        raise CompileError(f"{STATE_PATH}: outputs 는 비어 있지 않은 경로 문자열 목록이어야 한다")
    return set(outputs)


def _exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _remove_path(path: Path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _validate_parent_chain(root: Path, target: Path, what: str):
    parent = target.parent
    while parent != root:
        if _exists(parent) and not parent.is_dir():
            raise CompileError(f"{what}: 상위 경로 '{parent}' 가 디렉터리가 아니다")
        parent = parent.parent


def _read_source_tree(root: Path, src: Path):
    """source tree 를 메모리로 동결한다. 이후 staging 은 원본을 다시 읽지 않는다."""
    if src.is_symlink():
        raise CompileError(f"source tree '{src}' 가 디렉터리 심링크다")
    if not src.is_dir():
        raise CompileError(f"source tree '{src}' 가 디렉터리가 아니다")
    entries = []
    try:
        paths = sorted(src.rglob("*"))
        for path in paths:
            read_from = path
            if path.is_symlink():
                try:
                    read_from = path.resolve(strict=True)
                except (OSError, RuntimeError) as exc:
                    raise CompileError(f"source '{path}' 가 깨진 심링크다: {exc}") from exc
                _inside(root, read_from, "source symlink")
                if not read_from.is_file():
                    raise CompileError(f"source '{path}' 심링크가 일반 파일을 가리키지 않는다")
            elif path.is_dir():
                continue
            elif not path.is_file():
                raise CompileError(f"source '{path}' 가 일반 파일이 아니다")
            entries.append((str(path.relative_to(src)), read_from.read_bytes(),
                            bool(read_from.stat().st_mode & 0o111)))
    except CompileError:
        raise
    except OSError as exc:
        raise CompileError(f"source tree '{src}' 를 읽을 수 없다: {exc}") from exc
    return entries


def _state_bytes(written):
    state = {
        "schema_version": 1,
        "romeo_version": __version__,
        "outputs": sorted(written),
    }
    text = ("# `romeo compile` 산출물 목록. 손으로 고치지 않는다.\n"
            "# 여기 있는 경로는 언제든 다시 생성되므로, 고칠 곳은 core/ 와 adapters/ 다.\n"
            "---\n" + dump_yaml(state))
    return text.encode("utf-8")


def _prepare_compile(root: Path, prune: bool):
    """모든 입력·경로를 읽고 검증해 메모리 계획으로 만든다. 출력은 쓰지 않는다."""
    files, trees = plan_outputs(root)
    tree_rels = [str(dst.relative_to(root)) for _src, dst in trees]
    if len(tree_rels) != len(set(tree_rels)):
        raise CompileError("같은 skill destination 이 두 번 계획됐다")
    if set(files) & set(tree_rels):
        raise CompileError("파일 산출물과 tree 산출물 경로가 충돌한다")

    planned = set(files) | set(tree_rels)
    previous = _previous_outputs(root)
    pruned = sorted((previous or set()) - planned) if prune else []
    for rel in sorted(planned | set(pruned) | {STATE_PATH}):
        target = _inside(root, rel, "compile output")
        _validate_parent_chain(root, target, rel)

    rendered = {}
    for rel, (mode, content, source) in sorted(files.items()):
        path = root / rel
        if _exists(path) and path.is_dir() and not path.is_symlink():
            raise CompileError(f"{rel}: 파일 산출물 자리에 디렉터리가 있다")
        try:
            if mode == "managed":
                old = path.read_text(encoding="utf-8") if _exists(path) else ""
                text = replace_managed_block(old, content, source=source)
            elif mode == "settings":
                text = _render_settings(_load_settings(path), content)
            elif mode == "full":
                text = content
            else:
                raise CompileError(f"{rel}: 알 수 없는 산출물 mode '{mode}'")
        except CompileError:
            raise
        except (OSError, UnicodeError) as exc:
            raise CompileError(f"{rel}: 기존 산출물을 읽을 수 없다: {exc}") from exc
        rendered[rel] = text.encode("utf-8")

    frozen_trees = []
    for src, dst in trees:
        frozen_trees.append((str(dst.relative_to(root)), _read_source_tree(root, src)))

    return {
        "files": rendered,
        "trees": frozen_trees,
        "pruned": pruned,
        "written": sorted(planned),
        "state": _state_bytes(planned),
    }


def _stage_compile(root: Path, plan):
    """완성본과 파일 rollback 사본을 저장소와 같은 파일시스템에 만든다."""
    stage = Path(tempfile.mkdtemp(prefix=".compile-", dir=str(root)))
    try:
        new = stage / "new"
        for rel, data in {**plan["files"], STATE_PATH: plan["state"]}.items():
            path = new / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        for rel, entries in plan["trees"]:
            tree = new / rel
            tree.mkdir(parents=True, exist_ok=True)
            for item_rel, data, executable in entries:
                path = tree / item_rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                path.chmod(0o755 if executable else 0o644)

        old = stage / "old"
        for rel in list(plan["files"]) + [STATE_PATH]:
            source = root / rel
            if not _exists(source):
                continue
            backup = old / rel
            backup.parent.mkdir(parents=True, exist_ok=True)
            if source.is_symlink():
                backup.symlink_to(os.readlink(source))
            else:
                shutil.copy2(source, backup)
        return stage
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _ensure_parent(root: Path, parent: Path, created):
    missing = []
    cursor = parent
    while cursor != root and not _exists(cursor):
        missing.append(cursor)
        cursor = cursor.parent
    for path in reversed(missing):
        path.mkdir()
        created.append(path)


def _rollback(actions, created):
    errors = []
    for action in reversed(actions):
        try:
            target = action["target"]
            if action["kind"] == "file":
                if not action["installed"]:
                    continue
                if action["had_old"]:
                    os.replace(action["backup"], target)
                else:
                    _remove_path(target)
            elif action["kind"] == "tree":
                if action["installed"]:
                    _remove_path(target)
                if action["old_moved"]:
                    os.replace(action["displaced"], target)
            elif action["kind"] == "prune" and action["old_moved"]:
                os.replace(action["displaced"], target)
        except Exception as exc:
            errors.append(f"{action['target']}: {exc}")
    for path in sorted(created, key=lambda p: len(p.parts), reverse=True):
        try:
            path.rmdir()
        except OSError:
            pass
    return errors


def _commit_stage(root: Path, plan, stage: Path):
    actions = []
    created = []
    displaced_root = stage / "displaced"
    try:
        for rel in sorted(plan["files"]):
            target = root / rel
            _ensure_parent(root, target.parent, created)
            action = {
                "kind": "file", "target": target, "installed": False,
                "had_old": _exists(target), "backup": stage / "old" / rel,
            }
            actions.append(action)
            os.replace(stage / "new" / rel, target)
            action["installed"] = True

        for index, (rel, _entries) in enumerate(sorted(plan["trees"])):
            target = root / rel
            _ensure_parent(root, target.parent, created)
            displaced = displaced_root / f"tree-{index}"
            displaced.parent.mkdir(parents=True, exist_ok=True)
            action = {
                "kind": "tree", "target": target, "installed": False,
                "old_moved": False, "displaced": displaced,
            }
            actions.append(action)
            if _exists(target):
                os.replace(target, displaced)
                action["old_moved"] = True
            os.replace(stage / "new" / rel, target)
            action["installed"] = True

        for index, rel in enumerate(plan["pruned"]):
            target = root / rel
            displaced = displaced_root / f"prune-{index}"
            displaced.parent.mkdir(parents=True, exist_ok=True)
            action = {
                "kind": "prune", "target": target, "old_moved": False,
                "displaced": displaced,
            }
            actions.append(action)
            if _exists(target):
                os.replace(target, displaced)
                action["old_moved"] = True

        target = root / STATE_PATH
        _ensure_parent(root, target.parent, created)
        action = {
            "kind": "file", "target": target, "installed": False,
            "had_old": _exists(target), "backup": stage / "old" / STATE_PATH,
        }
        actions.append(action)
        os.replace(stage / "new" / STATE_PATH, target)
        action["installed"] = True
    except Exception as exc:
        rollback_errors = _rollback(actions, created)
        if rollback_errors:
            error = CompileError("compile 반영과 rollback 이 모두 실패했다; staging 보존: "
                                 f"{stage}; rollback={'; '.join(rollback_errors)}")
            error.preserve_stage = True
            raise error from exc
        raise CompileError(f"compile 반영 실패; 원래 상태로 rollback 했다: {exc}") from exc


def compile_all(root=None, prune=True):
    """완성본을 staging 한 뒤 원자 교체한다. 실패하면 모든 기존 산출물을 복구한다."""
    root = Path(root) if root else _project_root()
    try:
        plan = _prepare_compile(root, prune)
    except CompileError:
        raise
    except Exception as exc:
        raise CompileError(f"compile 입력 검증 실패: {exc}") from exc

    stage = None
    preserve_stage = False
    try:
        stage = _stage_compile(root, plan)
        _commit_stage(root, plan, stage)
    except CompileError as exc:
        preserve_stage = bool(getattr(exc, "preserve_stage", False))
        raise
    except Exception as exc:
        raise CompileError(f"compile staging 실패; 산출물은 바뀌지 않았다: {exc}") from exc
    finally:
        if stage is not None and not preserve_stage:
            shutil.rmtree(stage, ignore_errors=True)
    return plan["written"]


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
        if mode == "settings":
            try:
                data = _load_settings(path)
            except CompileError as exc:
                findings.append(("COMPILE_STALE", rel, "", str(exc)))
                continue
            permissions = data.get("permissions") or {}
            stale = (permissions.get("ask") != content["ask"]
                     or permissions.get("deny") != content["deny"])
        else:
            current = path.read_text(encoding="utf-8")
            expected = replace_managed_block(current, content, source=source) if mode == "managed" else content
            stale = current != expected
        if stale:
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

    recorded = _previous_outputs(root)
    if recorded is None:
        findings.append(("COMPILE_NO_STATE", STATE_PATH, "",
                         "산출물 목록이 없다 — 무엇이 하네스 소유인지 알 수 없다. `romeo compile` 로 재생성"))
    else:
        current = set(files) | {str(dst.relative_to(root)) for _s, dst in trees}
        for rel in sorted(recorded - current):
            if (root / rel).exists():
                findings.append(("COMPILE_ORPHAN", rel, "", "더 이상 산출물이 아닌데 남아 있다"))
    return findings
