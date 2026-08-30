"""어댑터 컴파일 — 코어(벤더 중립) → 런타임별 산출물.

원본은 `core/` 와 `vendor/` 이고, 산출물(지침 파일 `CLAUDE.md`·`AGENTS.md`, 스킬 트리 `.claude/skills/**`·`.agents/skills/**`,
역할 투영 `.claude/agents/*.md`, 권한 상한 `.claude/settings.json`, 컴파일 상태 `.harness/compiled.yaml`)은
언제든 다시 만들 수 있어야 한다. 실제로 **건드릴** 경로 전부는 `list_outputs()`(CLI 로는 `romeo compile --list-outputs`)가
답한다 — 손으로 기억하지 않는다. 거기에는 이전 컴파일에만 있던 **제거 대상**도 들어가고(삭제도 작업 트리를 바꾼다),
컴파일 **중에만** 존재하는 staging(`.compile-*`, 저장소 루트, 실패 시 보존)은 이름이 매번 달라 패턴 한 줄로 붙는다.
두 가지 규칙이 이걸 보장한다.

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
# staging 디렉터리는 저장소와 같은 파일시스템이어야 원자 교체가 되므로 저장소 루트에 만든다.
# 이름은 mkdtemp 가 정해 매번 다르다 — 그래서 쓰기 상한에 적을 수 있는 것은 이름이 아니라 패턴이다.
# 두 값이 한 곳에서 나오게 묶어 둔다: 인쇄되는 패턴과 실제로 만들어지는 이름이 어긋나면 상한이 헛돈다.
STAGE_PREFIX = ".compile-"
STAGE_GLOB = STAGE_PREFIX + "*/"
ADAPTERS_DIR = "adapters"
ROLES_DIR = "core/roles"
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


def load_roles(root):
    """역할 계약(`core/roles/*.yaml`). 벤더 중립이므로 두 런타임이 같은 것을 받는다."""
    out = {}
    d = Path(root) / ROLES_DIR
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.yaml")):
        data = load_any(f) or {}
        if not isinstance(data, dict):
            raise CompileError(f"{ROLES_DIR}/{f.name}: 역할 계약은 매핑이어야 한다")
        rid = data.get("id") or f.stem
        data["_source"] = f"{ROLES_DIR}/{f.name}"
        out[rid] = data
    return out


def _binding_rows(bindings):
    """(실행 이름, 역할 이름, 바인딩) — 기본 실행과 역할 교체 실행을 한 목록으로 편다.

    옛 형식(`parity_swap: {implementer: codex}`)도 읽는다. 그때는 강제 수단이 비어 있고,
    표에 **선언 없음** 으로 인쇄된다 — 조용히 통과시키지 않는다.
    """
    rows = []
    for label, key in (("기본", "roles"), ("교체", "parity_swap")):
        for name, role in (bindings.get(key) or {}).items():
            rows.append((label, name, role if isinstance(role, dict) else {"runtime": role}))
    return rows


def _binding_for(bindings, runtime, role_name):
    for label, name, role in _binding_rows(bindings):
        if name == role_name and role.get("runtime") == runtime:
            return label, role
    return None, {}


def _fmt_items(values):
    if not values:
        return "없음"
    return " · ".join(f"`{v}`" for v in values)


def _render_role_table(bindings):
    lines = ["## 역할 (D-68)", "",
             "역할이 무엇을 할 수 있는지는 아래 '역할 계약' 절이 정한다. 이 표가 정하는 것은",
             "그 계약을 어느 런타임이 맡고, 그 런타임에서 **무엇이 그것을 강제하는가** 뿐이다.", "",
             "| 실행 | 역할 | 런타임 | 쓰기 | 어떻게 강제하나 | 강제 관측 |",
             "| --- | --- | --- | --- | --- | --- |"]
    for label, name, role in _binding_rows(bindings):
        enforce = role.get("enforcement") or "**선언 없음**"
        seen = "관측됨" if role.get("enforcement_observed") else "**미관측**"
        lines.append(f"| {label} | `{name}` | {role.get('runtime','?')} | "
                     f"{'예' if role.get('write') else '**아니오**'} | {enforce} | {seen} |")
    lines += ["",
              "교체 실행에서도 같은 판정이 나와야 동등성 게이트를 통과한다. 네 칸의 강제 수단이 다르면",
              "그 비교는 '권한 상한이 서로 다른 두 실행' 의 비교이므로 동등성의 증거가 아니다.",
              "**미관측** 은 그 수단이 실제로 막는지 아직 실행으로 확인하지 않았다는 뜻이다 — 완료로 세지 않는다(K-51).",
              ""]
    return lines


def _role_contract_lines(rid, role):
    allowed = role.get("allowed_paths") or {}
    outputs = role.get("outputs") or {}
    lines = [f"- 능력: {_fmt_items(role.get('capabilities'))}"]
    scope = f"- 쓰기 범위: `{allowed.get('scope', '?')}`"
    if allowed.get("must_include"):
        scope += f" — 반드시 포함: {_fmt_items(allowed.get('must_include'))}"
    lines.append(scope)
    lines.append(f"- 계약: `{role.get('consumes', '?')}` → `{role.get('produces', '?')}`")
    lines.append(f"- 산출물: 증거 `{outputs.get('evidence', '?')}` · findings `{outputs.get('findings', '?')}`")
    for item in (role.get("forbidden") or []):
        lines.append(f"- 금지: {' '.join(str(item).split())}")
    return lines


def _render_role_contracts(roles):
    if not roles:
        return []
    lines = ["## 역할 계약 (`core/roles/`)", "",
             "원본은 각 역할의 계약 파일이다. 런타임 이름은 그 파일에 없다 — 위 표가 바인딩을 소유한다(D-68).",
             "작업 계약의 `allowed_paths` 는 여기 적힌 범위를 넘을 수 없다(K-66).", ""]
    for rid, role in roles.items():
        lines += [f"### `{rid}` — `{role.get('_source', '?')}`", ""]
        lines += _role_contract_lines(rid, role)
        lines.append("")
    return lines


def _render_permission_ceiling(adapter, bindings):
    """권한 상한을 이 런타임의 관점으로 인쇄한다 — 어느 런타임이 구현자든 같은 상한이 걸려야 한다(K-66)."""
    ceiling = bindings.get("permission_ceiling") or {}
    delivery = (adapter.get("permission_ceiling") or {}).get("delivery")
    rows = [(label, name, role) for label, name, role in _binding_rows(bindings)
            if role.get("runtime") == adapter.get("id")]
    if not ceiling and not delivery and not rows:
        return []
    lines = ["## 권한 상한 (K-66)", "",
             f"- 이 런타임에서의 전달 방식: {' '.join((delivery or '**선언 없음**').split())}"]
    for label, name, role in rows:
        seen = "관측됨" if role.get("enforcement_observed") else "**미관측**"
        lines.append(f"- {label} 실행에서 이 런타임이 `{name}` 일 때: "
                     f"{role.get('enforcement') or '**선언 없음**'} ({seen})")
    if ceiling.get("approval_required"):
        lines.append("- 승인 없이 실행하지 않는다: " + _fmt_items(ceiling["approval_required"]))
    if ceiling.get("never"):
        lines.append("- 승인으로도 정당화되지 않는다: " + _fmt_items(ceiling["never"]))
    if ceiling.get("note"):
        lines += ["", " ".join(str(ceiling["note"]).split())]
    lines.append("")
    return lines


def _render_instructions(root, adapter, bindings, roles):
    """지침 파일 managed block 본문 — 프로젝트 인덱스·원칙·역할 계약은 두 런타임이 같은 것을 받고,
    강제 수단과 권한 상한은 그 런타임의 것만 인쇄한다.

    인덱스를 이 블록에 넣는 이유: 마커 밖에 손으로 유지하면 한쪽 런타임만 그것을 보는 상태가 만들어지고,
    그 어긋남을 검사하는 게이트가 없다. 같은 것을 보지 않는 두 실행의 판정이 같다는 것은 동등성의 증거가 아니다."""
    index_src = root / "core/principles/PROJECT.core.md"
    core = root / "core/principles/AGENTS.core.md"
    _, index = _strip_frontmatter(index_src.read_text(encoding="utf-8"))
    _, principles = _strip_frontmatter(core.read_text(encoding="utf-8"))

    lines = ["# Romeo 하네스 규칙 (자동 생성)", "",
             "원본은 `core/principles/PROJECT.core.md`(이 저장소의 인덱스)와 "
             "`core/principles/AGENTS.core.md`(행동 규칙)이고 이 블록은 `romeo compile` 이 만든다.",
             "**마커 안을 고치지 않는다** — 다음 컴파일에서 사라진다. 마커 밖에 쓴 내용은 보존된다.",
             "", index.rstrip(), "", "---", "",
             principles.rstrip(), "", "---", ""]
    lines += _render_role_table(bindings)
    lines += _render_role_contracts(roles)
    lines += _render_permission_ceiling(adapter, bindings)

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
        # 코어 워크플로가 전부 진입점인 것은 아니다. 언제 켜지는지는 어댑터의 `when` 이 정하고,
        # 없으면 진입점으로 본다(기존 항목의 출력은 바이트 단위로 그대로다).
        lines.append(f"| `{name}` | `core/workflows/{name}/SKILL.md` | {cfg.get('when') or '라우터 진입점'} |")
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


def _render_role_agent(adapter, rid, cfg, roles, bindings):
    """역할 계약을 이 런타임이 이해하는 에이전트 정의 형식으로 투영한다.

    형식(frontmatter 키·`tools` 목록)은 어댑터가 소유한다. 계약 본문은 `core/roles/` 원본에서 온다 —
    여기서 새로 쓰지 않는다.
    """
    role = roles.get(rid)
    if role is None:
        raise CompileError(f"{adapter['id']}.role_agents.{rid}: `{ROLES_DIR}/{rid}.yaml` 이 없다")
    desc = " ".join((cfg.get("description") or "").split())
    if not desc:
        raise CompileError(f"{adapter['id']}.role_agents.{rid}: description 이 없다 — "
                           "런타임이 언제 이 역할을 띄울지 판단할 근거가 사라진다")
    tools = cfg.get("tools")
    label, binding = _binding_for(bindings, adapter["id"], rid)

    body = _role_contract_lines(rid, role)
    if binding:
        body += ["", f"- 바인딩: {label} 실행 · 쓰기 {'허용' if binding.get('write') else '없음'}",
                 f"- 강제 수단: `{binding.get('enforcement') or '선언 없음'}`",
                 f"- 강제 관측: {'관측됨' if binding.get('enforcement_observed') else '**미관측**'}"]
        if binding.get("defensive_check"):
            body.append(f"- 방어 검사(강제 수단이 아니다): {binding['defensive_check']}")
        if binding.get("enforcement_note"):
            body.append(f"- 메모: {' '.join(str(binding['enforcement_note']).split())}")
    else:
        body += ["", "- 바인딩: **이 런타임에 이 역할이 바인딩돼 있지 않다**. "
                     "라우터가 배정하지 않으면 쓰지 않는다."]

    head = (f"---\nname: {rid}\ndescription: {desc}\n"
            + (f"tools: {tools}\n" if tools else "")
            + f"---\n\n{GENERATED_NOTE}\n\n"
            f"# {rid} ({adapter['name']} 어댑터)\n\n"
            f"역할 계약의 원본은 `{role.get('_source', '?')}` 이다. 이 파일은 그 계약을 "
            f"{adapter['name']} 에서 어떻게 맡는지만 적는다.\n")
    return replace_managed_block(head, "\n".join(body), source=role.get("_source", ROLES_DIR))


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
    roles = load_roles(root)
    files, trees = {}, []
    for adapter in load_adapters(root):
        instructions_file = _output_rel(
            root, adapter["instructions_file"], f"{adapter['id']}.instructions_file")
        skills_dir = _output_rel(root, adapter["skills_dir"], f"{adapter['id']}.skills_dir")
        settings_file = None
        if adapter.get("settings_file"):
            settings_file = _output_rel(
                root, adapter["settings_file"], f"{adapter['id']}.settings_file")
        files[instructions_file] = ("managed", _render_instructions(root, adapter, bindings, roles),
                                    "core/principles/{PROJECT,AGENTS}.core.md")
        if settings_file and (adapter.get("settings_deny") or adapter.get("settings_ask")):
            files[settings_file] = ("settings", _owned_settings(adapter), None)
        # 역할 계약의 런타임 투영. 형식이 확인되지 않은 런타임은 agents_dir 가 비어 있고,
        # 그 런타임은 지침 파일 managed block 의 역할 계약 절로만 역할을 받는다.
        role_agents = adapter.get("role_agents") or {}
        if role_agents:
            if not adapter.get("agents_dir"):
                raise CompileError(f"{adapter['id']}.role_agents 가 있는데 agents_dir 가 없다")
            agents_dir = _output_rel(root, adapter["agents_dir"], f"{adapter['id']}.agents_dir")
            for rid, cfg in role_agents.items():
                rel = _output_rel(root, f"{agents_dir}/{rid}.md",
                                  f"{adapter['id']}.role_agents.{rid}")
                files[rel] = ("full",
                              _render_role_agent(adapter, rid, cfg or {}, roles, bindings), None)
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


def compile_targets(root: Path, prune: bool = True):
    """compile 이 건드리는 경로를 계산한다. 쓰지 않는다 — 계획과 인쇄가 같은 것을 보게 하는 하나의 원본이다.

    돌려주는 것은 `(files, trees, planned, pruned)` 다. `planned` 는 이번 컴파일이 쓸 산출물이고,
    `pruned` 는 이전 상태(STATE_PATH)에만 남아 이번에 **지워질** 경로다 — 쓰기가 아니라 삭제지만
    작업 트리를 바꾸는 것은 같으므로 쓰기 상한을 정할 때 빠뜨리면 안 된다."""
    files, trees = plan_outputs(root)
    tree_rels = [str(dst.relative_to(root)) for _src, dst in trees]
    if len(tree_rels) != len(set(tree_rels)):
        raise CompileError("같은 skill destination 이 두 번 계획됐다")
    if set(files) & set(tree_rels):
        raise CompileError("파일 산출물과 tree 산출물 경로가 충돌한다")
    planned = set(files) | set(tree_rels)
    previous = _previous_outputs(root)
    pruned = sorted((previous or set()) - planned) if prune else []
    return files, trees, planned, pruned


def list_outputs(root=None, prune=True):
    """`romeo compile` 이 건드릴 경로 — 파일을 쓰지 않고 계산만 한다(읽기 전용).

    구현자가 spec 의 「변경 범위」를 쓸 때 컴파일 산출물을 손으로 기억하다 빠뜨리는 것(결함 ④,
    `.agents/`·`.harness/compiled.yaml` 누락)을 막는다. `compile_all()` 이 건드리는 대상과 같은
    집합이어야 한다 — 계획된 산출물·제거될 이전 산출물·컴파일 상태 파일(STATE_PATH) 셋 다다.

    **디렉터리 산출물은 끝에 `/` 를 붙여 인쇄한다.** 스킬 트리는 통째로 하나의 산출물이라 그 안의 파일
    이름은 vendor 내용에 따라 바뀐다 — 파일을 낱개로 세면 목록이 그때그때 달라지고, 그 목록을 옮겨 적은
    쓰기 상한은 다음 vendor 갱신에서 곧바로 모자란다. 그래서 이 목록의 디렉터리 항목은 **그 아래 전부**를
    뜻하고, 이것이 `allowed_paths` 를 읽는 방식과도 같다.

    `(산출물, 제거 대상, 임시 패턴)` 을 돌려준다. 앞의 둘은 **완료 뒤 작업 트리에 남는(또는 남지 않게 되는)**
    경로라 이름을 그대로 적을 수 있다. 세 번째는 **컴파일 중에만 존재하는** staging 이다 — `mkdtemp` 가
    이름을 정하므로 미리 적을 수 있는 것은 이름이 아니라 패턴(`STAGE_GLOB`)뿐이고, 성공하면 지워지지만
    반영과 rollback 이 모두 실패하면 저장소 루트에 남는다. 목록의 목적은 쓰기 상한을 정하는 것이고
    상한은 패턴으로 세울 수 있으므로, 이름을 못 적는다는 것이 빠뜨려도 된다는 뜻은 아니다."""
    root = Path(root) if root else _project_root()
    _files, trees, planned, pruned = compile_targets(root, prune)
    dirs = {str(dst.relative_to(root)) for _src, dst in trees}

    def mark(rel):
        # 계획 단계에서 트리로 잡힌 것, 또는 이전 산출물이 디스크에 디렉터리로 남아 있는 것.
        return f"{rel}/" if rel in dirs or (root / rel).is_dir() else rel

    outputs = sorted({mark(rel) for rel in planned | set(pruned) | {STATE_PATH}})
    return outputs, [mark(rel) for rel in pruned], [STAGE_GLOB]


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
    files, trees, planned, pruned = compile_targets(root, prune)
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
    stage = Path(tempfile.mkdtemp(prefix=STAGE_PREFIX, dir=str(root)))
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
