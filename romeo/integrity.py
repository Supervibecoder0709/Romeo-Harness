"""무결성 검사 — 승격 문서가 코드를 따라잡고 있는가 · `docs/current/` 의 링크 · 작업 단위 id 중복.

승격 문서(`docs/current/enforcement.md`)는 **끝난 사실**이 모이는 자리다. 그 자리의 위험은 하나다 —
코드가 앞질러 가거나 문서가 코드에 없는 것을 적어도 아무도 모른다는 것. 그래서 이 모듈은 문서를 읽어서
**코드·정책표에서 다시 뽑은 것**과 대조한다. 문서를 코드에서 생성하지 않는 이유는 그 반대다:
생성하면 문서는 코드의 사본이 되어 어긋날 수 없고, 어긋날 수 없는 것은 아무것도 알리지 않는다.

**뽑는 규칙은 하나다.** 호출이나 `append` 의 문자열 인자가 **고정 텍스트로 시작**하면 그 선두의
첫 공백 앞까지를 id 로 본다(f-string 의 고정 선두를 포함한다). 문자열이 변수나 연결 표현이면 넣지 않는다 —
`check("REVIEW_" + cid, …)` 처럼 리터럴 연결로 만들어지는 판정은 **파생 판정**이고 대조 대상이 아니다.
그 규칙은 승격 문서의 「파생 판정」 절이 한 줄로 적는다.

수준이 조건에 따라 갈리는 호출(`level="error" if … else "warning"`)은 **더 강한 쪽**(error)으로 본다 —
경고로 적어 두면 실제로 막는 날 문서가 거짓이 된다.

**대조 단위는 `(id, 수준)` 쌍이다.** 양쪽을 id 로 키를 삼은 사전에 담으면 같은 id 의 다른 수준이 서로를
덮어써서, 실제로 다른 두 집합이 읽는 단계에서 같아진다. 그래서 두 쪽 모두 쌍을 키로 모으고
**쌍 집합의 대칭차**를 인쇄한다 — 수준만 다른 id 는 「코드에만 있다」와 「문서에만 있다」 두 줄로 나온다.

**한쪽이 비어도 대조는 성립한다.** 대조를 건너뛰는 것은 **양쪽이 다 없을 때**뿐이다 —
그때만 이 루트가 대조할 대상을 갖지 않았다고 말할 수 있다. 문서만 없는 루트는 판정이 남은 채
목록이 사라진 루트이고, 그것이야말로 이 검사가 보여야 하는 어긋남이다.
"""
import ast
import re
from pathlib import Path

from . import frontmatter
from .util import load_yaml

#: 승격 문서가 사는 루트. 이 자리는 규약이다 — 검사가 읽는 문서와 요구가 사는 문서가 같아야 한다(§11).
CURRENT_ROOT = "docs/current"
#: 작업 단위 폴더의 루트. id 중복을 세는 자리다.
WORK_ROOT = "docs/work"
#: 이 모듈이 저장소에서 읽는 루트 전부. **CI 트리거가 이 값을 덮어야 한다**(`tests/test_ci_trigger_coverage.py`).
#: 여기를 늘리면서 워크플로의 `paths:` 를 넓히지 않으면, 그 자리를 바꾼 커밋에서 이 검사가 돌지 않는다 —
#: 막는 자리에 있으면서 보는 사건이 좁은 상태다(AGENTS.core §11 ①). 아래 함수들은 이 값에서 경로를 만든다.
READ_ROOTS = (CURRENT_ROOT, WORK_ROOT)
#: 첫 승격 문서의 자리. 등록부(`PROMOTED`)의 키이고, 그 등록부는 `derive` 정의 뒤에 선다.
DOC_PATH = CURRENT_ROOT + "/enforcement.md"
#: 판정 id 를 뽑는 코드·정책표. 여기 없는 자리의 판정은 대조하지 않는다(승격 문서의 「범위」 절이 밝힌다).
CLOSE_SRC = "romeo/close.py"
VALIDATE_SRC = "romeo/validate.py"
POLICY_SRC = "core/policy/packages.yaml"

#: 인라인 링크. 대괄호로 텍스트, 이어지는 괄호로 대상. 괄호 안 내용을 **통째로** 잡는다 —
#: 경로를 잘라내는 것은 그 다음 자리(`_link_target`)의 일이다. 여기서 공백을 배제하면
#: 제목이 붙은 표기가 링크로 보이지도 않게 되어, 그 표기의 깨진 링크가 검사에서 통째로 빠진다.
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]*)\)")
#: 첫 공백. 경로 후보를 자르는 자리다(AC-4).
FIRST_SPACE_RE = re.compile(r"\s")
#: 표의 한 셀에서 백틱으로 감싼 첫 토큰.
BACKTICK_RE = re.compile(r"`([^`]+)`")

LEVELS = ("error", "warning")


def _lead(node):
    """문자열 노드의 **고정 선두**. 순수 리터럴과 f-string 의 고정 선두만 돌려준다.

    변수·연결 표현으로 시작하면 None 이다 — 그런 자리에서 만들어지는 id 는 파생 판정이고,
    한 자리의 문자열만 봐서는 실제 id 를 알 수 없다."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr) and node.values:
        first = node.values[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
    return None


def _id_of(text):
    """고정 선두에서 id 를 자른다 — 첫 공백 앞까지."""
    head = text.split()
    return head[0] if head else None


def _level_of(call):
    """`check(...)` 호출의 수준. `level=` 이 없으면 기본값 error 다.

    조건식이면 그 안의 문자열 상수를 전부 보고 error 가 하나라도 있으면 error 로 본다 —
    막을 수 있는 판정을 경고로 적어 두지 않는다."""
    for kw in call.keywords:
        if kw.arg != "level":
            continue
        consts = [n.value for n in ast.walk(kw.value)
                  if isinstance(n, ast.Constant) and n.value in LEVELS]
        if "error" in consts:
            return "error"
        return consts[0] if consts else "error"
    return "error"


def _check_call_pairs(source):
    """`check("<id>"` 리터럴 호출로 등록되는 `(id, 수준)` 쌍. `{(id, 수준): 출처}`.

    소스 **문자열**을 받는다 — 두 리비전의 같은 파일을 대조하는 자리가 파일 경로를 가질 수 없기 때문이다
    (`git show <sha>:romeo/close.py`)."""
    out = {}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "check" and node.args:
            text = _lead(node.args[0])
            cid = _id_of(text) if text is not None else None
            if cid:
                out.setdefault((cid, _level_of(node)), CLOSE_SRC)
    return out


def check_call_ids(source):
    """`check("<id>"` 리터럴 호출로 등록되는 판정. `{id: (수준, 출처)}`.

    한 id 가 여러 수준으로 등록되면 **더 강한 쪽**(error)을 남긴다 — 이 축약은 두 리비전의 **id 집합**을
    대조하는 자리(AC-7)의 것이고, 대조 자체는 축약하지 않은 쌍으로 한다."""
    out = {}
    for (cid, level), src in _check_call_pairs(source).items():
        if cid not in out or level == "error":
            out[cid] = (level, src)
    return out


def _envelope_tuple_pairs(source):
    """`ENVELOPE_CHECKS` 튜플에 실린 결과 계약 검사 id. 차단이므로 전부 error 다."""
    out = {}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "ENVELOPE_CHECKS" for t in node.targets):
            for elt in getattr(node.value, "elts", []):
                cid = _id_of(elt.value) if isinstance(elt, ast.Constant) and isinstance(elt.value, str) else None
                if cid:
                    out.setdefault((cid, "error"), CLOSE_SRC)
    return out


def _close_pairs(path):
    """`romeo/close.py` 의 `check("<id>"` 리터럴 호출과 `ENVELOPE_CHECKS` 튜플. `{(id, 수준): 출처}`."""
    source = Path(path).read_text(encoding="utf-8")
    out = _check_call_pairs(source)
    for pair, value in _envelope_tuple_pairs(source).items():
        out.setdefault(pair, value)
    return out


def _appends_to(node, names):
    """이 노드가 `names` 의 리스트에 넣는 문자열 노드들. `.append(...)` 과 `+= [...]` 둘 다 본다.

    이른 반환의 딕셔너리 리터럴(`{"errors": [...]}`)은 대상이 아니다 — 그 자리는 `errors` 변수에
    넣는 것이 아니라 새 리스트를 만드는 것이고, 담긴 것도 id 접두가 아니라 문장이다."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "append" and isinstance(node.func.value, ast.Name) \
            and node.func.value.id in names and node.args:
        return node.func.value.id, [node.args[0]]
    if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) \
            and node.target.id in names and isinstance(node.op, ast.Add):
        val = node.value
        if isinstance(val, ast.ListComp):
            return node.target.id, [val.elt]
        if isinstance(val, (ast.List, ast.Tuple)):
            return node.target.id, list(val.elts)
    return None, []


def _validate_pairs(path):
    """`romeo/validate.py` 가 `errors`/`warnings` 에 넣는 리터럴 접두. 넣는 리스트가 수준을 정한다."""
    out = {}
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        name, nodes = _appends_to(node, ("errors", "warnings"))
        if not name:
            continue
        level = "error" if name == "errors" else "warning"
        for n in nodes:
            text = _lead(n)
            cid = _id_of(text) if text is not None else None
            if cid:
                out.setdefault((cid, level), VALIDATE_SRC)
    return out


def _block_pairs(path):
    """`core/policy/packages.yaml` 의 `blocks:` 키. 차단이므로 전부 error 다."""
    data = load_yaml(path) or {}
    return {(str(k), "error"): POLICY_SRC for k in (data.get("blocks") or {})}


def derive(project_root="."):
    """코드·정책표에서 다시 뽑은 판정. `{(id, 수준): 출처}`.

    출처 파일이 없는 루트(하네스를 부착한 프로젝트)에서는 그 자리만 비운다."""
    root = Path(project_root)
    out = {}
    if (root / CLOSE_SRC).is_file():
        out.update(_close_pairs(root / CLOSE_SRC))
    if (root / VALIDATE_SRC).is_file():
        out.update(_validate_pairs(root / VALIDATE_SRC))
    if (root / POLICY_SRC).is_file():
        out.update(_block_pairs(root / POLICY_SRC))
    return out


def derive_ids(project_root="."):
    """코드·정책표에서 뽑은 `{id: 출처}`. 대조가 아니라 **훑어보는** 자리의 축약이다."""
    return {cid: src for (cid, _lv), src in derive(project_root).items()}


#: 승격 문서 등록부 — `{승격 문서 경로: 그 문서와 대조할 파생 함수}`.
#:
#: **소스에 리터럴로 적힌 키만 갖는다.** 디렉터리를 훑어 채우지 않는다 — 훑어서 채우면
#: 어떤 문서든 자동으로 등록되므로 `unregistered_promotions` 가 영영 아무것도 찾지 못하고,
#: 그 검사는 있으면서 아무것도 막지 않는 상태가 된다. 새 승격 문서를 세우는 단위는
#: 그 문서와 대조할 파생 함수를 **여기에 손으로 적는다** — 그 한 줄이 「이 문서는 무엇과 대조되는가」의 답이다.
PROMOTED = {DOC_PATH: derive}


def _rows(text):
    """문서의 표 중 **`수준` 열을 가진 표**의 데이터 행. `[(첫 열, {열이름: 값})]`.

    수준 열이 없는 표(안내표·범위표)는 판정 목록이 아니므로 지나간다."""
    rows, header = [], None
    for line in text.split("\n"):
        s = line.strip()
        if not (s.startswith("|") and s.endswith("|")):
            header = None
            continue
        cells = [c.strip() for c in s[1:-1].split("|")]
        if header is None:
            header = cells if "수준" in cells else []
            continue
        if not header or set("".join(cells)) <= set("- :"):     # 구분선
            continue
        rows.append((cells[0], dict(zip(header, cells))))
    return rows


def document(path):
    """승격 문서에서 읽은 판정. `{(id, 수준): 출처}`. 문서가 없으면 빈 사전이다.

    **행을 쌍으로 보존한다.** id 만 키로 삼으면 같은 id 의 다른 수준을 적은 행이 서로를 덮어써서
    문서에만 있는 쌍이 읽는 단계에서 사라진다 — 그러면 두 집합이 다른데도 대조가 일치로 끝난다."""
    path = Path(path)
    if not path.is_file():
        return {}
    out = {}
    for first, row in _rows(path.read_text(encoding="utf-8")):
        m = BACKTICK_RE.search(first)
        if not m:
            continue
        src = BACKTICK_RE.search(row.get("출처", "") or "")
        out.setdefault((m.group(1), row.get("수준", "")), src.group(1) if src else "")
    return out


def document_ids(path):
    """승격 문서에서 읽은 `{id: 출처}`. 대조가 아니라 **훑어보는** 자리의 축약이다."""
    return {cid: src for (cid, _lv), src in document(path).items()}


def compare(project_root="."):
    """등록부의 각 승격 문서를 그 파생원과 `(id, 수준)` 쌍 집합으로 대조한다. `(대조한 id 개수, 어긋난 줄들)`.

    **코드도 문서도 없을 때만** 그 문서의 대조가 성립하지 않는다 — 그 루트에는 올릴 것도 올린 것도 없다.
    **한쪽만** 없는 루트는 아무것도 없는 루트가 아니라 한쪽이 통째로 사라진 루트다 —
    그 차이를 건너뛰면 판정이 남은 채 목록만 없어진 저장소가 대조를 통과한다.

    그래서 `core/` 만 부착되고 승격 문서가 없는 저장소에서는 정책표 차단이 「코드에만 있다」로 인쇄된다.
    그 저장소가 실제로 그것을 집행하고 목록이 없는 것은 사실이지만, 승격 규약에 가입하지 않은 저장소를
    어긋났다고 볼 것인지는 정해지지 않았다 — 열어 두었다(Q-93). 예외를 두는 것은 새 요구다(§11).

    인쇄하는 것은 쌍 집합의 **대칭차**다(AC-2 — 한쪽에만 있는 쌍을 어느 쪽인지와 함께).
    수준만 다른 id 는 두 줄로 나온다 — 코드에만 있는 쌍 하나와 문서에만 있는 쌍 하나다.

    등록부의 **값이 실제로 호출되는 자리가 여기다.** 값을 부르지 않고 키만 세면 등록부는 이름표가 되고
    대조는 사라진다 — 그 구멍은 값을 어긋나게 하는 함수로 바꿔치면 바로 드러난다.
    """
    root = Path(project_root)
    compared, lines = None, []
    for doc_path, derive_fn in sorted(PROMOTED.items()):
        code = derive_fn(root)
        doc = document(root / doc_path)
        if not code and not doc:
            continue
        compared = (compared or 0) + len({cid for cid, _lv in set(code) | set(doc)})
        for pair in sorted(set(code) ^ set(doc)):
            cid, level = pair
            if pair in code:
                lines.append(f"PROMOTION_DRIFT 코드에만 있다: `{cid}` ({level}) — {code[pair]}")
            else:
                lines.append(f"PROMOTION_DRIFT 문서에만 있다: `{cid}` ({level}) — {doc_path}")
    return compared, lines


#: 검사하지 않는 대상 경로의 선두. 이 저장소 밖을 가리키므로 파일 존재로 판정할 수 없다.
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")


def _link_target(inner):
    """괄호 안 내용에서 **대상 경로**. 첫 공백 앞까지가 경로 후보이고, 그 후보에서 `#` 뒤를 잘라낸다.

    **표기를 하나씩 세어 더하지 않는다.** 경로뿐인 표기·따옴표 제목이 붙은 표기·공백만 붙은 표기를
    각각 세면 그 목록은 언제나 열려 있고, 다음 표기가 나올 때마다 검사가 조용히 비어 간다.
    규칙 하나가 전부를 판정하면 세지 않은 표기도 같은 자리로 떨어진다(AC-4).

    빈 문자열이 나오는 자리가 곧 검사하지 않는 자리다 — 괄호가 비었거나, 문서 안 앵커만 적혔거나,
    괄호 안이 공백으로 시작한 링크다."""
    return FIRST_SPACE_RE.split(inner, maxsplit=1)[0].split("#")[0]


def broken_links(project_root="."):
    """`docs/current/` 아래 `.md` 의 상대 인라인 링크 중 대상 파일이 없는 것."""
    base = Path(project_root) / CURRENT_ROOT
    out = []
    for md in sorted(base.rglob("*.md")) if base.is_dir() else []:
        for inner in LINK_RE.findall(md.read_text(encoding="utf-8")):
            target = _link_target(inner)
            if not target or target.startswith(EXTERNAL_PREFIXES):
                continue
            if not (md.parent / target).exists():
                out.append(f"BROKEN_LINK {md.relative_to(project_root)} → {inner}")
    return out


def unregistered_promotions(project_root="."):
    """`CURRENT_ROOT` 아래 `.md` 중 `PROMOTED` 의 키가 **아닌** 것.

    승격 문서가 늘어날 때 대조 없이 들어오는 것을 막는다. 링크 검사(`broken_links`)는 이 루트의 모든 문서를
    훑지만 대조는 등록된 문서에만 붙으므로, 등록을 잊은 문서는 링크만 검사받고 내용은 아무도 보지 않는다 —
    그것이 「검사 대상 밖의 문서」가 생기는 경로다(Q-91).

    판정은 **파일 이름이 아니라 등록부에 드는가**로만 갈린다. 이름을 특별 취급하는 자리를 두지 않는다."""
    root = Path(project_root)
    base = root / CURRENT_ROOT
    out = []
    for md in sorted(base.rglob("*.md")) if base.is_dir() else []:
        rel = md.relative_to(root).as_posix()
        if rel not in PROMOTED:
            out.append(f"UNCHECKED_PROMOTION {rel} — 대조할 파생원이 PROMOTED 에 등록되지 않았다")
    return out


def duplicate_unit_ids(project_root="."):
    """`docs/work/` **바로 아래** 폴더의 `spec.md` frontmatter `id` 중복. `spec.md` 가 없는 폴더는 건너뛴다."""
    base = Path(project_root) / WORK_ROOT
    seen = {}
    for d in sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []:
        spec = d / "spec.md"
        if not spec.is_file():
            continue
        try:
            fm, _body = frontmatter.read(spec)
        except Exception:
            continue
        uid = (fm or {}).get("id")
        if uid:
            seen.setdefault(str(uid), []).append(d.name)
    return [f"DUPLICATE_UNIT_ID {uid} — {WORK_ROOT}/{{{', '.join(dirs)}}}"
            for uid, dirs in sorted(seen.items()) if len(dirs) > 1]


def run(project_root="."):
    """세 검사를 한 번에. `(종료 코드, 인쇄할 줄들)`."""
    root = Path(project_root).resolve()
    compared, drift = compare(root)
    lines = [f"romeo integrity {root}"]
    if compared is None:
        lines.append(f"  대조 건너뜀 — {DOC_PATH} 도 판정을 뽑을 코드도 이 루트에 없다")
    else:
        lines.append(f"  대조 {compared}건 — {DOC_PATH} ↔ 코드·정책표")
    unregistered = unregistered_promotions(root)
    # 등록 검사가 **실제로 돌았다**는 것을 이 실행 자신의 출력으로 남긴다. 종료 코드 0 만으로는
    # 「돌고 위반이 없었다」와 「호출을 건너뛰었다」가 구분되지 않는다.
    registered = [k for k in sorted(PROMOTED) if (root / k).is_file()]
    lines.append(f"  등록 {len(registered)}건 · 미등록 {len(unregistered)}건 — {CURRENT_ROOT}/")
    violations = drift + unregistered + broken_links(root) + duplicate_unit_ids(root)
    lines += [f"  {v}" for v in violations]
    lines.append(f"  위반 {len(violations)}건")
    return (1 if violations else 0), lines


def main(project_root="."):
    code, lines = run(project_root)
    print("\n".join(lines))
    return code
