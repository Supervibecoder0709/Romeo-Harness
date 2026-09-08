"""1-hop 재개 — 한 단위 id 로 다음 세션이 읽어야 할 파일 목록을 낸다.

`/plan` 절차 1단계는 겹치는 단위를 찾으면 「재개」를 제안한다(M1 · `romeo find`). 그런데 재개하는 세션이
**무엇을 읽어야 하는지**는 어디에도 없었다 — 사람은 단위 폴더를 눈으로 훑고, 상위 문서를 찾아 올라가고,
어느 증거가 검사 기록인지 종료 검사의 출력을 다시 읽어야 했다. 이 명령이 그 목록을 낸다.

**1-hop 만 간다(K-31).** 목록은 단위 폴더 안의 파일 전부와, frontmatter 가 가리키는 것 — `parent` 의
charter(없으면 spec)와 `inputs` 의 각 경로 — 까지다. 부모의 부모, 입력 단위의 다른 파일, 계획·결정 문서는
넣지 않는다. 저장소 수준의 진입점(progress 블록·git log·CI)은 따로 있고, 그 너머는 목록의 파일이
가리킬 때 연다.

**드러내되 판정하지 않는다.** 파일마다 역할 한 낱말과 그 파일에 적힌 사실(status·회차 결과·gate_verdict·
findings 수·등록 여부)만 붙인다. 다음 행동을 추천하지 않는다 — 그것은 사람과 라우터의 몫이다(K-61).
없는 참조는 숨기지 않고 `[없음]` 으로 인쇄하되 종료 코드는 0 이다 — 드러내기가 차단으로 자라지 않게 한다.
없는 단위 id 만 오류다(exit 1, 스택 트레이스 아님 — `romeo.docs.find_unit_dir` 의 FileNotFoundError 를
CLI 가 한 줄로 인쇄한다).
"""
from pathlib import Path

import yaml

from .docs import find_unit_dir
from .util import load_json, load_yaml

#: 인쇄 순서. 정본이 먼저다 — 승인·수용 기준·검증 계획이 거기 있다.
ROLES = ("정본", "상위", "입력", "회차", "계약", "증거", "결과", "검토", "기타")
#: 정본 문서. spec 이 앞이다 — id·title·승인의 정본이고, 나머지는 같은 분류의 다른 면이다.
UNIT_DOCS = ("spec.md", "brief.md", "charter.md")
#: 정본 frontmatter 를 읽지 못했을 때 그 줄이 시작하는 말. 헤더의 「정본 읽을 수 없음」이 이 접두로 센다.
UNREADABLE = "읽을 수 없다"
#: 읽히지 않은 세 갈래. **각 문장은 그 파일에 대해 참이어야 한다**(§11) — 「매핑이 아니다」를 빈 매핑(`{}`)에
#: 붙이면 그 줄이 거짓을 말하고, 「파싱하지 못했다」를 파싱된 `0`·`false` 에 붙여도 마찬가지다. 그래서 셋이다.
DOC_UNREADABLE = {
    "parse": UNREADABLE + " — frontmatter 를 파싱하지 못했다",
    "not-mapping": UNREADABLE + " — frontmatter 가 매핑이 아니다",
    "empty": UNREADABLE + " — frontmatter 가 비어 있다",
}
#: 그 파일에서 사실을 뽑다가 예외가 난 자리. 목록은 계속 나오고 그 줄만 이것을 말한다.
UNREADABLE_FACT = UNREADABLE
#: frontmatter 울타리. 공유 파서(`romeo/frontmatter.py`)와 같은 모양을 본다 — 그 문서들을 읽으므로.
FENCE = "---"
UNIT_DOC_NOTES = {
    "spec.md": "Tech Spec(승인·수용 기준·검증 계획)",
    "brief.md": "Compact Brief",
    "charter.md": "Charter(마일스톤 계획)",
}
#: 단위 폴더의 하위 디렉터리와 그 역할. 여기 없는 디렉터리의 파일은 「기타」다.
SUBDIR_ROLES = {"task": "계약", "evidence": "증거", "result": "결과", "review": "검토"}
ATTEMPTS = "attempts.yaml"


def _short(value, n=12):
    return str(value)[:n] if value else "-"


def _read(fn, path):
    """파일 하나가 깨졌다고 목록 전체가 멈추지 않는다 — 그 파일의 사실만 비운다."""
    try:
        return fn(path)
    except Exception:
        return None


def _canon_frontmatter(path):
    """정본 frontmatter 를 **이 모듈이 직접 판독한다.** 반환은 `(갈래, 매핑)`.

    공유 파서(`romeo/frontmatter.py` 의 `split`)는 `yaml.safe_load(raw) or {}` 라서 falsey 비매핑 여섯
    (`[]`·`{}`·`0`·`false`·`''`·빈 frontmatter)을 전부 빈 매핑으로 바꾼다. 그래서 호출자가 `isinstance(dict)`
    로 아무리 걸러도 그 여섯을 정상 빈 매핑과 구별할 수 없다 — 깨진 정본에 고정 설명이 붙고 `parent`·`inputs`
    가 조용히 사라진다(3회차 반례 · Q-88). 공유 파서는 고치지 않는다: 이 단위의 비범위이고 호출자 전부의
    동작이 함께 바뀐다(§12).

    **읽힌 것의 조건을 하나로 닫는다.** 「비어 있지 않은 매핑」만 읽힌 정본이고 나머지는 전부 읽히지 않은 것이다 —
    깨짐의 종류를 열거하면 반례가 하나씩 더 나오지만(1·2·3회차의 실측), 여집합에는 다음 반례가 없다.
    갈래는 `ok`(매핑) · `parse`(울타리 없음·닫는 울타리 없음·YAML 문법 오류) · `not-mapping`(파싱은 됐으나
    매핑이 아닌 값 — `null` 포함) · `empty`(빈 매핑) 넷이고, 뒤 셋의 문장은 `DOC_UNREADABLE` 이 소유한다.
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except Exception:
        return "parse", None
    if not text.startswith(FENCE + "\n"):
        return "parse", None
    end = text.find("\n" + FENCE + "\n", len(FENCE))
    if end == -1:
        return "parse", None
    try:
        parsed = yaml.safe_load(text[len(FENCE) + 1:end])
    except Exception:
        return "parse", None
    if not isinstance(parsed, dict):
        return "not-mapping", None
    return ("ok", parsed) if parsed else ("empty", None)


def _note_attempts(data):
    if not isinstance(data, dict):
        return "읽을 수 없다"
    attempts = data.get("attempts") or []
    parts = []
    for a in attempts:
        if not isinstance(a, dict):
            continue
        fc = a.get("failure_class")
        parts.append(f"{a.get('n')} {a.get('result')}" + (f"({fc})" if fc else ""))
    note = f"회차 {len(attempts)}" + (" · " + " · ".join(parts) if parts else "")
    reviews = data.get("reviews") or []
    if reviews:
        note += f" · 재검토 {len(reviews)}"
    return note


def _note_task(data):
    if not isinstance(data, dict):
        return "읽을 수 없다"
    return f"{data.get('role') or '?'} · base {_short(data.get('base_sha'))}"


def _note_result(data):
    if not isinstance(data, dict):
        return "읽을 수 없다"
    note = f"{data.get('role') or '?'} · {data.get('gate_verdict') or '?'}"
    if data.get("blocked_reason"):
        note += f" · blocked {data['blocked_reason']}"
    return note


def _note_review(data):
    if not isinstance(data, dict):
        return "읽을 수 없다"
    return f"{data.get('gate_verdict') or '?'} · findings {len(data.get('findings') or [])}"


def _note_evidence(data, registered):
    if not isinstance(data, dict):
        return ("등록됨(검사 기록)" if registered else "미등록") + " · 읽을 수 없다"
    n = len(data.get("commands") or [])
    return (f"등록됨(검사 기록)" if registered else "미등록") + f" · 명령 {n}건 · head {_short(data.get('head_sha'))}"


def _scalar(value):
    """frontmatter 에서 경로·id 로 쓸 수 있는 값인가. bool 은 제외한다 — `str(True)` 는 경로가 아니다."""
    return isinstance(value, (str, int)) and not isinstance(value, bool)


def _parent_of(fm, warns):
    """`parent` 는 스칼라일 때만 쓴다. 목록·매핑이면 상위 줄을 내지 않고 그 사실을 경고로 남긴다."""
    value = fm.get("parent")
    if value is None:
        return None
    if _scalar(value):
        return value
    warns.append("parent 값이 문자열이 아니다")
    return None


def _list_of(fm, key, warns):
    """`inputs`·`evidence` 는 목록일 때만 쓰고 그 안의 스칼라 항목만 쓴다. 아니면 빈 목록 + 경고."""
    value = fm.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        warns.append(f"{key} 값이 목록이 아니다")
        return []
    return [x for x in value if _scalar(x)]


def _rel(path, root):
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).resolve().as_posix()


def unit_context(project_root=".", unit_id=""):
    """한 단위의 1-hop 파일 목록. 단위 폴더가 없으면 FileNotFoundError(CLI 가 exit 1 로 인쇄한다).

    반환은 `unit`(id·title·status·승인·종료·parent·dir) · `files`(path·role·exists·note 목록, 인쇄 순서) ·
    `missing`(files 중 exists 가 거짓인 path) 이다. 없는 참조는 목록에 남는다 — 지우면 왜 재개가 막히는지 사라진다.
    """
    root = Path(project_root).resolve()
    udir = find_unit_dir(root, unit_id)
    # 정본을 전부 읽어 둔다 — 읽히지 않은 것은 그 줄이 사실을 말해야 하고(고정 설명은 거짓이 된다),
    # `fm` 은 **처음으로 읽힌** 정본에서 온다. spec 이 깨졌다고 brief 의 parent·inputs 가 사라지지 않는다.
    # **비어 있지 않은 매핑일 때만 읽힌 것이다**(`_canon_frontmatter`). 그 밖은 전부 읽히지 않은 것이고,
    # 그 줄이 어느 갈래인지 말한 뒤 다음 정본으로 간다.
    doc_kind = {}
    fm, fm_source = {}, None
    for name in UNIT_DOCS:
        doc = udir / name
        if not doc.is_file():
            continue
        kind, mapping = _canon_frontmatter(doc)
        doc_kind[name] = kind
        if kind == "ok" and fm_source is None:
            fm, fm_source = mapping, name

    files, seen = [], set()

    def add(path, role, note="", order=0):
        rel = _rel(path, root)
        if rel in seen:
            return
        seen.add(rel)
        files.append({"path": rel, "role": role, "exists": Path(path).is_file(), "note": note, "_order": order})

    # 정본 — 있는 것만, spec 이 앞. 읽히지 않은 것은 고정 설명 대신 그 갈래의 사실을 적는다.
    for i, name in enumerate(UNIT_DOCS):
        if name in doc_kind:
            kind = doc_kind[name]
            note = UNIT_DOC_NOTES[name] if kind == "ok" else DOC_UNREADABLE[kind]
            add(udir / name, "정본", note, order=i)

    # 읽힌 정본 안에서 값의 모양이 어긋난 것 — 그 필드를 쓰지 않고, 첫 정본 줄의 note 끝에 사실로 붙인다.
    warns = []
    parent = _parent_of(fm, warns)
    inputs = _list_of(fm, "inputs", warns)
    registered = {str(x) for x in _list_of(fm, "evidence", warns)}

    # 상위 — parent 의 charter, 없으면 spec. 둘 다 없으면 charter 자리를 [없음] 으로 남긴다.
    if parent:
        pdir = root / "docs" / "work" / str(parent)
        target = next((pdir / n for n in ("charter.md", "spec.md") if (pdir / n).is_file()), pdir / "charter.md")
        add(target, "상위", f"parent {parent} · " + ("Charter(마일스톤 계획)" if target.name == "charter.md" else "Tech Spec"))

    # 입력 — 단위 폴더 기준 상대 경로(K-62 의 등록 방식 그대로).
    for raw in inputs:
        add(udir / str(raw), "입력", f"inputs: {raw}")

    # 회차
    if (udir / ATTEMPTS).is_file():
        try:
            note = _note_attempts(_read(load_yaml, udir / ATTEMPTS))
        except Exception:
            note = UNREADABLE_FACT
        add(udir / ATTEMPTS, "회차", note)

    # 계약·증거·결과·검토·기타 — 폴더 안 파일 전부. 위에서 이미 넣은 것은 그 역할을 지킨다.
    # **파일 단위로 격리한다.** 사실을 뽑다가 어떤 예외가 나도 그 줄만 「읽을 수 없다」가 되고 목록은 계속 나온다 —
    # 깨짐의 종류를 열거하는 방식은 반례가 나올 때마다 끝나지 않는다(1·2회차의 실측).
    for p in sorted(x for x in udir.rglob("*") if x.is_file()):
        role = "기타"
        try:
            rel_u = p.relative_to(udir).as_posix()
            if rel_u in UNIT_DOCS or rel_u == ATTEMPTS:
                continue
            top = rel_u.split("/", 1)[0] if "/" in rel_u else None
            role = SUBDIR_ROLES.get(top, "기타")
            if role == "계약":
                note = _note_task(_read(load_json, p))
            elif role == "증거":
                note = _note_evidence(_read(load_yaml, p), rel_u in registered)
            elif role == "결과":
                note = _note_result(_read(load_json, p))
            elif role == "검토":
                note = _note_review(_read(load_json, p))
            else:
                note = "frontmatter 에 등록되지 않은 산출물" if top == "inputs" else ""
            add(p, role, note)
        except Exception:
            add(p, role, UNREADABLE_FACT)

    # 어긋난 필드는 첫 정본 줄에 적는다 — 그 값이 사는 자리가 거기다.
    if warns:
        first = next((f for f in files if f["role"] == "정본"), None)
        if first is not None:
            first["note"] = (first["note"] or "") + "".join(f" · {w}" for w in warns)

    files.sort(key=lambda f: (ROLES.index(f["role"]), f["_order"], f["path"]))
    for f in files:
        del f["_order"]
    unit = {
        "id": str(fm.get("id") or unit_id), "title": str(fm.get("title") or ""),
        "status": fm.get("status"), "approved_at": fm.get("approved_at"), "closed_at": fm.get("closed_at"),
        "parent": parent, "dir": _rel(udir, root),
    }
    return {"unit": unit, "files": files, "missing": [f["path"] for f in files if not f["exists"]]}


def format_context(res):
    u = res["unit"]
    # 정본이 하나도 읽히지 않았으면 parent·inputs 줄을 낼 수 없다 — 그 사실을 헤더에 드러낸다.
    canon = [f for f in res["files"] if f["role"] == "정본"]
    unreadable = bool(canon) and all(UNREADABLE in (f["note"] or "") for f in canon)
    lines = [f"romeo context {u['id']} — {u['title']}",
             f"status {u['status'] or '-'} · 승인 {_short(u['approved_at'], 10)} · 종료 {_short(u['closed_at'], 10)}"
             f" · parent {u['parent'] or '-'} · 파일 {len(res['files'])} · 없음 {len(res['missing'])}"
             + (" · 정본 읽을 수 없음" if unreadable else "")]
    for f in res["files"]:
        tag = f"[{f['role']}]" if f["exists"] else "[없음]"
        note = (f["role"] + " · " if not f["exists"] else "") + (f["note"] or "")
        lines.append(f"{tag} {f['path']}" + (f" — {note}" if note else ""))
    return "\n".join(lines)
