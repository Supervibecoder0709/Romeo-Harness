"""동등성 판정 — 같은 작업 단위를 역할 배치만 바꿔 두 번 실행한 결과 계약 쌍을 대조한다.
`romeo fixtures parity --report` 가 스키마 유효·required_checks 동일·gate 판정 동일 세 가지를 출력한다(C-C3·D-12).

**판정은 두 층이다(D-b).** 섞으면 손으로 쓴 데이터가 게이트를 통과시킨다 — K-51 이 막으려는 형태다.

- `checker_verdict` — **검사기 자기 검증**. 손으로 쓴 합성 케이스(`source.kind: authored`)가 선언한 기대대로
  판정되는지만 본다. 비교 로직이 살아 있다는 것만 증명하고, 두 런타임이 실제로 동등하다는 것은 증명하지 않는다.
- `gate_verdict` — **게이트 판정**. 실제 교차 실행에서 나온 관측 케이스(`source.kind: observed`)만으로 계산한다.
  관측이 0건이면 `UNDETERMINED`(미판정)이고, 통과가 아니므로 종료 코드는 1 이다.

**`observed` 라는 선언 자체는 증거가 아니다.** 그 한 단어가 게이트를 여는 유일한 열쇠이므로, 선언과 함께
**관측물의 실재**를 검사한다 — `source.ref` 가 실재하는 파일이어야 하고, `unit_id` 가 `docs/work/` 에 실재하는
작업 단위여야 한다. 하나라도 어긋나면 통과도 미판정도 아니라 **구조 오류**(`PARITY_INVALID`, 종료 코드 1)다 —
관측이라고 선언했는데 관측물이 없는 것은 미판정보다 나쁘다(K-51).

**관측 케이스는 봉투를 인라인으로 담지 않는다.** 케이스 파일 안에 손으로 적은 봉투는 아무 검사도 받지 않고,
게이트가 비교하는 값이 바로 그 봉투이기 때문이다. 관측 케이스의 한 면은 역할마다
`results.<역할>: {file: docs/work/<unit>/{result|review}/<run>-<역할>.json}` 한 줄만 받는다 —
그 파일을 읽어 **종료 검사와 같은 앵커 검사**(`close.envelope_checks`)를 태우고, 다섯 검사가 전부 통과한
봉투만 비교 대상이 된다. 규칙을 두 벌 적지 않는다: 느슨한 쪽이 게이트를 연다(K-63).
합성 케이스(`authored`)는 지금처럼 인라인으로 적는다 — 검사기 자기 검증용이고 게이트를 열지 못하기 때문이다.

`verdict` 는 `gate_verdict` 와 같은 값이다 — 리포트가 말하는 판정은 게이트이기 때문이다.
다만 **종료 코드 0 은 두 층이 모두 PASS 일 때만** 낸다: 검사기가 옳은지 확인하지 못한 실행(합성 0건)은
게이트 통과를 주장할 수 없다.

케이스의 `runtimes:` 는 판정에 쓰지 않는다 — 어느 런타임이 어느 역할을 맡았는지 읽는 사람을 위한 기록이다.
프롬프트 동일성은 비교하지 않는다(C-C2). 종료 코드는 숫자가 아니라 성공/실패로만 비교한다 —
같은 실패에 런타임마다 다른 비0 코드를 낼 수 있고, 물어야 할 것은 "같은 검사를 실행했고 같은 결론이 났는가" 다.

실행 결과가 아직 없는 케이스(`status: pending`)는 일치로 세지 않고 미실행으로 인쇄한다.
검사기 자기 검증은 **합성 케이스만으로** 계산한다 — 계산 대상과 설명 문장이 같은 집합을 가리켜야 한다.
합성이 0건이면 PASS 도 FAIL 도 아니라 `해당 없음` 이다: 0건을 근거로 검사기가 옳다고도 틀렸다고도 말할 수 없다.
합성 0건은 검사기가 검증되지 않았다는 뜻이므로 리포트가 그 사실을 따로 인쇄한다.

**판정 불가(undecidable)** 는 불일치와 다른 결과다. 봉투가 자기 역할 계약을 어겼거나(`ROLE_CONTRACT_VIOLATION`)
통과 주장을 뒷받침할 것이 하나도 없으면(`EVIDENCE_MISSING`), 양면이 글자까지 똑같아도 동등성을 판정하지 않는다.
같은 거짓을 두 번 적은 것은 동등성의 증거가 아니다.

**비교 불가(incomparable)** 는 불일치도 판정 불가도 아닌 세 번째 결과다(D-73). 산출물을 만들지 못하는 역할
(역할 계약에 `workspace-write` 가 없는 역할 — 검토자)의 판정은 **자기가 본 산출물의 함수**다. 두 검토자가
다른 산출물을 봤다면 판정이 갈리는 것이 정상이고, 그 차이는 런타임의 차이를 말하지 않는다. 그래서 검토자 면은
**두 면의 산출물이 같을 때만** 비교하고, 다르면 `PRODUCT_DIFFERS` 로 분리해 게이트 판정에서 뺀 뒤 '비교 불가' 로
인쇄한다 — 뺐다는 사실을 숨기지 않는다(K-51). 구현자 면(계약·checks·판정)은 산출물과 무관하게 지금처럼 비교한다:
두 구현자가 다른 바이트를 만드는 것은 정상이고, 물어야 할 것은 같은 계약에서 같은 검사를 돌려 같은 결론을 냈는가다.
산출물 식별은 관측 케이스에서는 봉투가 지목한 증거의 `head_sha`·`dirty_tree_hash` 에서 읽고(손으로 적지 않는다 — D-b),
합성 케이스에서는 면마다 `product:` 로 선언하며 `expect_incomparable:` 로 검사기가 그것을 잡는지 검증한다.
관측 케이스의 모든 면이 비교 불가이면 게이트는 PASS 도 FAIL 도 아니라 미판정이다 — 비교하지 않은 것을 통과로 세지 않는다.
"""
import re
from collections import Counter
from pathlib import Path

import yaml

from . import HARNESS_ROOT
from .schema import validate as _validate
from .util import load_json, load_yaml

SCHEMA_PATH = "core/schemas/result-envelope.json"
ROLES_DIR = "core/roles"
CANON_REASON = "스키마 유효·required_checks 동일·gate 판정 동일"
ROLES = ("implementer", "reviewer")
STATUSES = ("executed", "pending")
CASE_ID_PATTERN = r"^pr-[a-z0-9]+(-[a-z0-9]+)*$"
REQUIRED_KEYS = ("id", "title", "unit_id", "expect", "baseline", "swapped", "source")

# 케이스의 출처. 이 값이 게이트를 판정할 자격을 가른다(D-b).
SOURCE_KINDS = ("observed", "authored", "planned")
OBSERVED_KIND = "observed"
SYNTHETIC_KINDS = ("authored",)

# 이 코드가 붙은 쌍은 '불일치'가 아니라 '판정 불가'다 — 비교 자체가 성립하지 않는다.
UNDECIDABLE_CODES = ("EVIDENCE_MISSING", "ROLE_CONTRACT_VIOLATION")
# 관측 케이스의 봉투가 앵커 검사를 통과하지 못했다. 비교를 시작하지 않는다 — 무엇을 비교할지 모른다.
ANCHOR_INVALID = "OBSERVED_ANCHOR_INVALID"
# 검사를 실행하려면 역할 계약에 이 능력이 있어야 한다(core/roles/*.yaml).
RUN_CAPABILITY = "run-command"
# 산출물을 만들 수 있는 능력. 이 능력이 **없는** 역할(검토자)의 판정은 자기가 본 산출물의 함수다 —
# 같은 산출물을 봤을 때만 비교한다(D-73). 역할 이름이 아니라 계약에서 읽는다.
WRITE_CAPABILITY = "workspace-write"
# 산출물 식별 — 검토자가 본 것은 커밋(head_sha)과 그 위의 미커밋 변경(dirty_tree_hash)이다.
# 종료 검사의 신선도 검사(FRESH_HEAD·FRESH_TREE)가 보는 것과 같은 두 값이다(K-63). 증거 기록 명령이 쓴다.
PRODUCT_KEYS = ("head_sha", "dirty_tree_hash")
# 비교 불가 — 불일치도 판정 불가도 아니다. 그 면을 게이트 판정에서 빼고 뺐다는 사실을 인쇄한다.
PRODUCT_DIFFERS = "PRODUCT_DIFFERS"
PRODUCT_UNKNOWN = "PRODUCT_UNKNOWN"
INCOMPARABLE_CODES = (PRODUCT_DIFFERS, PRODUCT_UNKNOWN)
INCOMPARABLE_TEXT = "비교 불가"

# 관측 케이스의 앵커가 실재해야 하는 자리.
WORK_DIR = "docs/work"
EVIDENCE_SUFFIX = ".yaml"
# 작업 계약이 놓이는 자리(K-62). 계약 생성 명령이 여기에만 쓴다.
TASK_DIR = "task"
TASK_SUFFIX = ".json"
# 관측 케이스가 봉투를 받는 자리. 결과 계약도 그 작업 단위 안에 있다(K-62).
RESULT_DIRS = ("result", "review")
RESULT_SUFFIX = ".json"

GATE_TEXT = {"PASS": "PASS", "FAIL": "FAIL", "UNDETERMINED": "미판정"}
# 판정할 대상이 0건일 때. PASS 도 FAIL 도 0건을 근거로 한 주장이므로 쓰지 않는다.
NOT_APPLICABLE = "N/A"
CHECKER_TEXT = {"PASS": "PASS", "FAIL": "FAIL", NOT_APPLICABLE: "해당 없음"}


def load_parity_cases(directory):
    directory = Path(directory)
    items = []
    for path in sorted(directory.glob("*.yaml")):
        data = load_yaml(path)
        data["_path"] = str(path)
        items.append(data)
    return items


def load_role_contracts(harness_root=None):
    """역할 계약을 정본에서 읽는다. 능력 목록을 코드에 다시 적지 않는다 — 계약이 바뀌면 검사도 따라 바뀐다."""
    root = Path(harness_root) if harness_root else HARNESS_ROOT
    directory = root / ROLES_DIR
    contracts = {}
    if not directory.is_dir():
        return contracts
    for path in sorted(directory.glob("*.yaml")):
        data = load_yaml(path) or {}
        contracts[data.get("id") or path.stem] = data
    return contracts


def _where(case):
    return case.get("_path") or case.get("id") or "<이름 없음>"


def _results(case, side):
    """한 면의 결과 매핑. 면이 깨져 있으면 빈 매핑이다 — 구조 검사가 그 사실을 따로 보고한다."""
    face = case.get(side)
    if not isinstance(face, dict):
        return {}
    results = face.get("results")
    return results if isinstance(results, dict) else {}


def _kind(case):
    return (case.get("source") or {}).get("kind") if isinstance(case.get("source"), dict) else None


def _repo_path(root, ref):
    """저장소 안의 상대 경로만 앵커로 인정한다. 절대 경로·상위 탈출은 이 저장소의 관측물을 가리키지 못한다."""
    if not isinstance(ref, str) or not ref.strip():
        return None
    try:
        p = Path(ref.strip())
        if p.is_absolute() or ".." in p.parts:
            return None
        return root / p
    except (OSError, ValueError):
        return None


def _is_file(path):
    """경로 문자열이 파일 이름으로 쓸 수 없는 값이면 '실재하지 않는다' 와 같게 다룬다."""
    if path is None:
        return False
    try:
        return path.is_file()
    except (OSError, ValueError):
        return False


def evidence_ref_error(unit_id, ref):
    """증거 포인터가 **그 작업 단위의 증거 산출물**을 가리키는지 본다. 규칙은 여기 한 곳에만 있다.

    실재하기만 하면 되는 것이 아니다 — 저장소 안의 아무 파일이나 증거로 인정하면, 검토자가 자기 입력인
    spec.md 를 '읽은 증거' 로 지목해도 통과한다. 종료 검사(`close._evidence_anchor`)와 동등성 판정이
    이 함수를 함께 쓴다: 같은 필드를 두 검사기가 다르게 보면 느슨한 쪽이 done 을 만든다(K-62·K-63).
    어긋나면 이유 문장을, 맞으면 None 을 돌려준다."""
    prefix = f"{WORK_DIR}/{unit_id}/evidence/"
    text = str(ref).replace("\\", "/")
    if not text.startswith(prefix) or not text.endswith(EVIDENCE_SUFFIX):
        return (f"{prefix}*{EVIDENCE_SUFFIX} 밖이다 — 증거는 그 작업 단위 안에 있고 증거 기록 명령이 만든다"
                f"(K-62). 판정 대상으로 받은 문서는 '읽은 증거'가 아니다")
    return None


def task_ref_error(unit_id, ref):
    """작업 계약 포인터가 **그 작업 단위의 계약 자리**를 가리키는지 본다. 규칙은 여기 한 곳에만 있다.

    재계산 대조는 계약의 *바이트*에 묶여 있어서 파일 이름을 보지 않는다 — 진짜 계약을 다른 이름·다른
    디렉터리로 복사해 두고 그것을 가리켜도 통과한다. 위조로서는 값이 낮지만(내용이 이미 올바른 계약이다)
    '산출물은 작업 단위 안에 둔다'(K-62)를 증거 쪽에서만 강제하고 계약 쪽에서 놓아 둘 이유가 없다.
    증거 포인터와 같은 모양의 자리 규약을 계약 포인터에도 건다."""
    prefix = f"{WORK_DIR}/{unit_id}/{TASK_DIR}/"
    text = str(ref).replace("\\", "/")
    if not text.startswith(prefix) or not text.endswith(TASK_SUFFIX):
        return (f"{prefix}*{TASK_SUFFIX} 밖이다 — 작업 계약은 그 작업 단위 안에 있고 "
                f"계약 생성 명령이 만든다(K-62)")
    return None


def _result_ref(unit, role, ref):
    """관측 케이스가 지목한 결과 계약 파일의 상대 경로. (경로, 오류)

    인라인 봉투를 여기서 거부한다 — 게이트가 비교하는 값을 케이스 작성자가 그대로 타이핑할 수 있으면
    게이트는 아무것도 지키지 않는다(D-b)."""
    place = "|".join(RESULT_DIRS)
    if not isinstance(ref, dict) or list(ref) != ["file"]:
        return None, (f"results.{role} 이 봉투를 인라인으로 담고 있다 — 관측 케이스는 봉투를 파일로만 받는다"
                      f"({{file: {WORK_DIR}/{unit}/<{place}>/<run>-{role}{RESULT_SUFFIX}}}). "
                      f"인라인 봉투는 종료 검사의 앵커 검사를 받지 않는다(K-63)")
    raw = ref.get("file")
    if not isinstance(raw, str) or not raw.strip():
        return None, f"results.{role}.file 이 비어 있다 — 결과 계약 파일을 상대 경로로 지목한다"
    text = raw.strip()
    allowed = tuple(f"{WORK_DIR}/{unit}/{d}/" for d in RESULT_DIRS)
    if not text.startswith(allowed) or not text.endswith(RESULT_SUFFIX):
        return None, (f"results.{role}.file {text!r} 가 {WORK_DIR}/{unit}/<{place}>/*{RESULT_SUFFIX} 밖이다 — "
                      f"결과 계약도 그 작업 단위 안에 있다(K-62)")
    return text, None


def _judges_product(role, roles):
    """산출물을 만들지 못하는 역할인가 — 그 역할의 판정은 자기가 본 산출물의 함수다(D-73).

    역할 이름이 아니라 계약(core/roles/*.yaml)의 능력 목록에서 읽는다: `workspace-write` 가 없으면 판정 역할이다.
    계약이 없으면 False 다 — 관측 케이스는 어차피 역할 계약 앵커(`ROLE_CONTRACT`)를 통과해야 비교 대상이 된다."""
    contract = (roles or {}).get(role)
    if contract is None:
        return False
    return WRITE_CAPABILITY not in (contract.get("capabilities") or [])


def _product_of(mapping):
    """산출물 식별자 `(head_sha, dirty_tree_hash)`. 하나라도 비어 있으면 None — 반쪽 식별은 식별이 아니다."""
    if not isinstance(mapping, dict):
        return None
    vals = tuple(mapping.get(k) for k in PRODUCT_KEYS)
    if not all(isinstance(v, str) and v.strip() for v in vals):
        return None
    return tuple(v.strip() for v in vals)


def _product_text(product):
    return f"{product[0][:7]}+{product[1][:12]}"


def _inline_products(case):
    """합성 케이스의 면별 산출물 선언(`<면>.product`)을 그 면의 모든 역할에 붙인다. 없으면 None 이다."""
    out = {}
    for side in ("baseline", "swapped"):
        face = case.get(side) if isinstance(case.get(side), dict) else {}
        product = _product_of(face.get("product"))
        out[side] = {role: product for role in _results(case, side)}
    return out


def _evidence_product(project_root, ref):
    """관측 봉투가 지목한 증거에서 산출물 식별을 읽는다. (식별자, 오류)

    증거의 실재·자리는 앵커 검사(`EVIDENCE_ANCHORED`)가 이미 봤다. 여기서는 그 안에 `head_sha`·`dirty_tree_hash` 가
    있는지만 본다 — 증거 기록 명령이 항상 쓰는 값이라, 없다면 손으로 만든 증거다."""
    path = _repo_path(project_root, ref)
    try:
        ev = load_yaml(path) if _is_file(path) else None
    except (OSError, ValueError, yaml.YAMLError) as e:
        return None, f"evidence_ref {ref} 를 읽을 수 없다 ({e})"
    product = _product_of(ev)
    if product is None:
        return None, (f"evidence_ref {ref} 에 산출물 식별({'·'.join(PRODUCT_KEYS)})이 없다 — 판정 역할이 본 산출물을 "
                      f"식별하지 못하면 그 면은 비교할 수 없다. 증거는 증거 기록 명령이 만든다(K-51)")
    return product, None


def _resolve_face(case, side, project_root, harness_root, unit_dir, schema, roles):
    """관측 케이스의 한 면을 파일에서 읽고 **종료 검사와 같은 앵커 검사**를 태운다. (봉투 매핑, 산출물 매핑, 오류)

    다섯 검사가 전부 통과한 봉투만 비교 대상이 된다. 하나라도 FAIL·UNVERIFIED 면 그 면은 비교하지 않는다 —
    대조하지 못한 것을 관측으로 세지 않는다(K-51). 판정 역할의 봉투는 지목한 증거에서 산출물 식별을 함께 읽는다 —
    케이스 파일에 적힌 값이 아니라 실행이 남긴 값이다(D-b)."""
    from .close import envelope_checks  # close 가 이 모듈을 읽는다 — 순환 import 를 피해 여기서 부른다
    unit = case.get("unit_id")
    results = _results(case, side)
    out, products, errs = {}, {}, []
    if not isinstance(results, dict):
        return out, products, errs
    for role, ref in sorted(results.items()):
        rel_path, why = _result_ref(unit, role, ref)
        if why is not None:
            errs.append(f"{side}.{why}")
            continue
        path = _repo_path(project_root, rel_path)
        if not _is_file(path):
            errs.append(f"{side}.results.{role}.file {rel_path!r} 가 실재하지 않는다 — "
                        f"관측 케이스의 봉투는 실행이 남긴 파일이다")
            continue
        try:
            env = load_json(path)
        except (OSError, ValueError) as e:
            errs.append(f"{side}.results.{role}.file {rel_path} 를 JSON 으로 읽을 수 없다 ({e})")
            continue
        rows = envelope_checks(env, unit, role, project_root, unit_dir, roles, schema,
                               side=side, harness_root=harness_root)
        bad = [f"{cid} {'FAIL' if state is False else 'UNVERIFIED'}"
               + (f": {reason}" if reason else "") for cid, state, reason in rows if state is not True]
        if bad:
            errs.append(f"{side}.results.{role}.file {rel_path} 가 종료 검사와 같은 앵커 검사를 "
                        f"통과하지 못한다 — " + "; ".join(bad))
            continue
        if _judges_product(role, roles):
            product, why = _evidence_product(project_root, env.get("evidence_ref"))
            if why is not None:
                errs.append(f"{side}.results.{role}.file {rel_path} — {why}")
                continue
            products[role] = product
        out[role] = env
    return out, products, errs


def resolve_case(case, project_root, harness_root):
    """비교에 쓸 봉투와 산출물 식별을 면마다 확정한다. (면별 봉투 매핑, 면별 산출물 매핑, 오류 목록)

    합성·미실행 케이스의 인라인 봉투와 `product:` 선언은 그대로 쓴다 — 게이트를 열지 못하기 때문이다.
    관측 케이스만 파일에서 읽고 앵커 검사를 태우며, 산출물 식별도 증거에서 읽는다."""
    inline = {side: _results(case, side) for side in ("baseline", "swapped")}
    if _kind(case) != OBSERVED_KIND or case.get("status", "executed") != "executed":
        return inline, _inline_products(case), []
    empty = {"baseline": {}, "swapped": {}}
    unit = case.get("unit_id")
    unit_dir = _repo_path(project_root, f"{WORK_DIR}/{unit}") if isinstance(unit, str) and unit.strip() else None
    if unit_dir is None or not unit_dir.is_dir():
        return empty, dict(empty), []          # 앵커 검사가 '실재하는 작업 단위가 아니다' 로 따로 보고한다
    try:
        schema = load_json(Path(harness_root) / SCHEMA_PATH)
        roles = load_role_contracts(harness_root)
    except (OSError, ValueError) as e:
        return empty, dict(empty), [f"결과 계약 스키마를 읽을 수 없다 ({e}) — 앵커 검사를 태울 수 없다"]
    out, products, errs = {}, {}, []
    for side in ("baseline", "swapped"):
        out[side], products[side], side_errs = _resolve_face(case, side, project_root, harness_root,
                                                             unit_dir, schema, roles)
        errs.extend(side_errs)
    return out, products, errs


def _product_errors(case, status, observed, roles):
    """산출물 식별의 구조 검사. 관측 케이스는 선언을 거부하고, 합성 케이스는 판정 역할을 비교하려면 선언을 요구한다.

    관측 케이스의 `product:`·`expect_incomparable:` 은 봉투 인라인과 같은 이유로 거부한다 — 게이트가 비교를
    빼는 근거를 케이스 작성자가 타이핑할 수 있으면, 갈린 검토자 면을 '산출물이 달랐다' 로 지울 수 있다(D-b)."""
    errs = []
    expected = case.get("expect_incomparable")
    if observed:
        for side in ("baseline", "swapped"):
            face = case.get(side)
            if isinstance(face, dict) and "product" in face:
                errs.append(f"{side}.product 가 인라인이다 — 관측 케이스의 산출물 식별은 봉투가 지목한 증거의 "
                            f"{'·'.join(PRODUCT_KEYS)} 에서 읽는다(D-b)")
        if expected is not None:
            errs.append("expect_incomparable 는 관측 케이스에 쓰지 않는다 — 비교 불가는 증거에서 계산되는 결과이지 "
                        "기대가 아니다(D-b)")
        return errs
    if expected is not None and (
            not isinstance(expected, dict)
            or any(r not in ROLES or c not in INCOMPARABLE_CODES for r, c in expected.items())):
        errs.append(f"expect_incomparable 는 {{역할: 코드}} 매핑이다 — 역할 {list(ROLES)} · 코드 {list(INCOMPARABLE_CODES)}")
    if status == "pending":
        return errs
    base, swap = _results(case, "baseline"), _results(case, "swapped")
    judged = [r for r in sorted(set(base) & set(swap)) if _judges_product(r, roles)]
    if not judged:
        return errs
    for side in ("baseline", "swapped"):
        face = case.get(side)
        if isinstance(face, dict) and _product_of(face.get("product")) is None:
            errs.append(f"{side}.product 가 없거나 {'·'.join(PRODUCT_KEYS)} 가 비어 있다 — {', '.join(judged)} 면은 "
                        f"같은 산출물을 봤을 때만 비교하므로 합성 케이스는 면마다 산출물을 선언한다(D-73)")
    return errs


def _anchor_errors(case, root, resolved, resolve_errs):
    """`observed` 로 선언한 케이스의 관측물이 실재하는지 본다.

    `source.kind: observed` 는 게이트를 여는 유일한 열쇠다(D-b). 그 열쇠가 손으로 고칠 수 있는 한 단어이면
    게이트는 아무것도 지키지 않는다 — 케이스 파일에서 `authored` 를 `observed` 로 바꾸는 것만으로 PASS 가 난다.
    그래서 선언과 함께 실재를 검사한다. 어긋나면 미판정이 아니라 구조 오류다:
    관측이라고 선언했는데 관측물이 없는 것은 게이트를 열지 않은 것보다 나쁘다(K-51).
    """
    errs = []
    unit = case.get("unit_id")
    ref = (case.get("source") or {}).get("ref")
    if not _is_file(_repo_path(root, ref)):
        errs.append(f"source.kind: observed 인데 ref {ref!r} 가 저장소의 실재 파일이 아니다 — "
                    f"관측을 기록한 파일을 상대 경로로 지목한다(설명 문장은 source.note 로 분리한다)")
    unit_dir = _repo_path(root, f"{WORK_DIR}/{unit}") if isinstance(unit, str) and unit.strip() else None
    if unit_dir is None or not unit_dir.is_dir():
        errs.append(f"source.kind: observed 인데 unit_id {unit!r} 가 {WORK_DIR}/ 에 없다 — "
                    f"관측은 실재하는 작업 단위에서 나온다")
    anchored = sum(len(v) for v in resolved.values())
    if not errs and not resolve_errs and anchored == 0:
        errs.append(f"source.kind: observed 인데 양면 어디에도 앵커 검사를 통과한 결과 계약이 없다 — "
                    f"관측이라고 선언했는데 관측물이 하나도 없다")
    return errs


def _source_errors(case, status, root, resolved, resolve_errs):
    """출처가 없거나 상태와 어긋나면 게이트가 무엇으로 계산됐는지 말할 수 없다."""
    source = case.get("source")
    if source is None:
        return []  # 필수 키 검사가 이미 보고했다
    if not isinstance(source, dict):
        return ["source 가 매핑이 아님 — kind·ref 로 케이스의 출처를 선언한다"]
    errs = []
    kind = source.get("kind")
    if kind not in SOURCE_KINDS:
        errs.append(f"source.kind {kind!r} 는 {list(SOURCE_KINDS)} 밖 — 관측인지 합성인지 구분되어야 한다")
        return errs
    if status == "executed" and kind == "planned":
        errs.append("status: executed 인데 source.kind 가 planned — 실행했으면 observed 또는 authored 다")
    if status == "pending" and kind != "planned":
        errs.append(f"status: pending 인데 source.kind 가 {kind!r} — 미실행 자리표의 출처는 planned 다")
    if kind == OBSERVED_KIND:
        errs.extend(_anchor_errors(case, root, resolved, resolve_errs))
    return errs


def check_parity_cases(cases, harness_root=None, project_root=None):
    """케이스 파일 자체의 구조 오류만 본다. 판정 이전 문제이므로 리포트에 섞지 않는다.

    관측 케이스의 앵커(`source.ref`·`unit_id`·결과 계약 파일)는 관측물이 있는 저장소를 기준으로 찾는다 —
    `project_root` 를 생략하면 하네스 저장소가 그 자리다. `harness_root` 는 스키마·역할 계약·정책표를
    읽는 곳이다(계약 재계산이 그것을 쓴다).
    """
    hroot = Path(harness_root) if harness_root else HARNESS_ROOT
    root = Path(project_root) if project_root else hroot
    contracts = load_role_contracts(hroot)
    errors = {}
    ids = Counter(c.get("id") for c in cases)
    for case in cases:
        errs = []
        for key in REQUIRED_KEYS:
            if key not in case:
                errs.append(f"필수 키 {key} 없음")
        cid = case.get("id")
        if not isinstance(cid, str) or not re.match(CASE_ID_PATTERN, cid):
            errs.append(f"id {cid!r} 가 패턴 {CASE_ID_PATTERN} 과 맞지 않음")
        elif ids[cid] > 1:
            errs.append(f"중복 id {cid}")
        status = case.get("status", "executed")
        if status not in STATUSES:
            errs.append(f"status {status!r} 는 {list(STATUSES)} 밖")
        expect = case.get("expect")
        if expect not in ("same", "differ"):
            errs.append(f"expect {expect!r} 는 same 또는 differ 여야 함")
        if expect == "differ" and not case.get("expect_codes"):
            errs.append("expect: differ 인데 expect_codes 가 비어 있음")
        if status == "pending" and not case.get("pending_reason"):
            errs.append("status: pending 인데 pending_reason 이 없음 — 무엇을 기다리는지 적는다")
        resolved, _products, resolve_errs = resolve_case(case, root, hroot)
        errs.extend(_source_errors(case, status, root, resolved, resolve_errs))
        errs.extend(resolve_errs)
        observed = _kind(case) == OBSERVED_KIND
        errs.extend(_product_errors(case, status, observed, contracts))
        for side in ("baseline", "swapped"):
            if side not in case:
                continue
            if not isinstance(case.get(side), dict):
                errs.append(f"{side} 가 매핑이 아님")
                continue
            if not isinstance(case[side].get("results"), dict):
                errs.append(f"{side}.results 가 매핑이 아님")
                continue
            results = _results(case, side)
            if status == "pending":
                if results:
                    errs.append(f"status: pending 인데 {side}.results 에 결과가 있음 — 실행했으면 executed 로 바꾼다")
                continue
            if not results:
                errs.append(f"{side}.results 가 비어 있음 — 결과가 없으면 status: pending 으로 선언한다")
            for role, env in sorted(results.items()):
                if role not in ROLES:
                    errs.append(f"{side}.results 의 역할 {role!r} 은 {list(ROLES)} 밖")
                if observed:
                    continue      # 봉투는 파일에서 읽어 앵커 검사가 본다(resolve_case)
                if not isinstance(env, dict):
                    errs.append(f"{side}.results.{role} 이 매핑이 아님")
                    continue
                if env.get("role") != role:
                    errs.append(f"{side}.results.{role} 의 role 이 {env.get('role')!r}")
                if env.get("unit_id") != case.get("unit_id"):
                    errs.append(f"{side}.results.{role} 의 unit_id 가 케이스와 다름")
        if errs:
            errors[_where(case)] = errs
    return errors


def _check_key(env):
    return [(c.get("id"), c.get("command"), c.get("exit_code") == 0) for c in env.get("checks") or []]


def _checks_detail(role, base, swap):
    base_ids = [c[0] for c in base]
    swap_ids = [c[0] for c in swap]
    if base_ids != swap_ids:
        return f"CHECKS_DIFFER {role} 실행 목록 {base_ids}≠{swap_ids}"
    for (cid, base_cmd, base_ok), (_, swap_cmd, swap_ok) in zip(base, swap):
        if base_cmd != swap_cmd:
            return f"CHECKS_DIFFER {role} {cid} 명령 {base_cmd!r}≠{swap_cmd!r}"
        if base_ok != swap_ok:
            return f"CHECKS_DIFFER {role} {cid} 성공 {base_ok}≠{swap_ok}"
    return f"CHECKS_DIFFER {role} 실행 목록 {base_ids}≠{swap_ids}"


def _envelope_defects(side, role, env, roles):
    """봉투 하나가 역할 계약과 증거 규칙을 지켰는지 본다. 어기면 그 쌍은 동등성을 판정할 수 없다.

    능력 목록은 역할 계약(core/roles/*.yaml)에서 읽는다 — 여기에 역할 이름별 규칙을 다시 적지 않는다.
    """
    out = []
    contract = roles.get(role)
    checks = env.get("checks") or []
    can_run = contract is not None and RUN_CAPABILITY in (contract.get("capabilities") or [])
    evidence = env.get("evidence_ref")
    has_evidence = isinstance(evidence, str) and bool(evidence.strip())

    if contract is not None and checks and not can_run:
        caps = sorted(contract.get("capabilities") or [])
        out.append(("ROLE_CONTRACT_VIOLATION",
                    f"ROLE_CONTRACT_VIOLATION {side}.{role} checks {len(checks)}건 — "
                    f"역할 계약의 capabilities {caps} 에 {RUN_CAPABILITY} 가 없다"))

    if env.get("gate_verdict") == "PASS":
        if can_run and not checks:
            out.append(("EVIDENCE_MISSING",
                        f"EVIDENCE_MISSING {side}.{role} gate_verdict PASS 인데 checks 0건 — 실행 없이 통과를 주장한다"))
        elif not checks and not has_evidence:
            out.append(("EVIDENCE_MISSING",
                        f"EVIDENCE_MISSING {side}.{role} gate_verdict PASS 인데 checks 0건·evidence_ref 없음 — "
                        f"판정을 뒷받침할 것이 봉투에 하나도 없다"))
        if not has_evidence and can_run:
            out.append(("EVIDENCE_MISSING",
                        f"EVIDENCE_MISSING {side}.{role} gate_verdict PASS 인데 evidence_ref 가 비었다"))
    return out


def compare_case(case, schema, roles=None, results=None, products=None):
    """한 케이스의 두 면을 역할별로 짝지어 판정한다. 미실행 케이스는 비교하지 않는다.

    `results` 를 주면 그것을 비교한다 — 관측 케이스의 봉투는 케이스 파일이 아니라 앵커 검사를 통과한
    결과 계약 파일에서 온다(`resolve_case`). `products` 는 면별·역할별 산출물 식별이다 — 판정 역할
    (`_judges_product`)은 두 면의 산출물이 같을 때만 비교하고, 다르면 그 면을 `incomparable` 로 분리한다(D-73).
    관측 케이스는 비교 불가를 기대로 선언할 수 없으므로 `ok` 에 넣지 않고, 합성 케이스는 `expect_incomparable`
    과 정확히 같아야 `ok` 다 — 검사기가 비교 불가를 잡는지도 검증 대상이다."""
    roles = load_role_contracts() if roles is None else roles
    status = case.get("status", "executed")
    row = {"id": case.get("id"), "unit_id": case.get("unit_id"), "status": status,
           "kind": _kind(case), "roles": [], "expect": case.get("expect"), "actual": None,
           "ok": False, "codes": [], "detail": [], "compared": [], "incomparable": []}
    if status == "pending":
        row["detail"] = [case.get("pending_reason") or "실행 결과 없음"]
        return row
    if results is None:
        results = {side: _results(case, side) for side in ("baseline", "swapped")}
    if products is None:
        products = _inline_products(case)
    base = results.get("baseline") or {}
    swap = results.get("swapped") or {}
    row["roles"] = sorted(set(base) | set(swap))
    codes, detail = [], []
    compared, incomparable = [], []
    for side, face in (("baseline", base), ("swapped", swap)):
        for role in sorted(face):
            env = face[role]
            for err in _validate(env, schema):
                codes.append("SCHEMA_INVALID")
                detail.append(f"SCHEMA_INVALID {side}.{role} {err}")
            if isinstance(env, dict):
                for code, msg in _envelope_defects(side, role, env, roles):
                    codes.append(code)
                    detail.append(msg)
    if sorted(base) != sorted(swap):
        codes.append("ROLE_SET_DIFFERS")
        detail.append(f"ROLE_SET_DIFFERS {sorted(base)}≠{sorted(swap)}")
    for role in sorted(set(base) & set(swap)):
        base_env, swap_env = base[role], swap[role]
        if _judges_product(role, roles):
            # 판정 역할의 결론은 자기가 본 산출물의 함수다 — 같은 산출물을 봤을 때만 비교가 성립한다(D-73).
            base_product = (products.get("baseline") or {}).get(role)
            swap_product = (products.get("swapped") or {}).get(role)
            if base_product is None or swap_product is None:
                incomparable.append({"role": role, "code": PRODUCT_UNKNOWN,
                                     "detail": f"{PRODUCT_UNKNOWN} {role} 산출물을 식별하지 못했다 — {INCOMPARABLE_TEXT}"})
                continue
            if base_product != swap_product:
                incomparable.append({"role": role, "code": PRODUCT_DIFFERS,
                                     "detail": f"{PRODUCT_DIFFERS} {role} 산출물 {_product_text(base_product)}≠"
                                               f"{_product_text(swap_product)} — {INCOMPARABLE_TEXT}: 다른 산출물에 "
                                               f"대한 판정 차이는 런타임의 차이를 말하지 않는다"})
                continue
        compared.append(role)
        base_checks, swap_checks = _check_key(base_env), _check_key(swap_env)
        if base_checks != swap_checks:
            codes.append("CHECKS_DIFFER")
            detail.append(_checks_detail(role, base_checks, swap_checks))
        if base_env.get("gate_verdict") != swap_env.get("gate_verdict"):
            codes.append("VERDICT_DIFFERS")
            detail.append(f"VERDICT_DIFFERS {role} gate_verdict "
                          f"{base_env.get('gate_verdict')}≠{swap_env.get('gate_verdict')}")
        elif base_env.get("blocked_reason") != swap_env.get("blocked_reason"):
            codes.append("VERDICT_DIFFERS")
            detail.append(f"VERDICT_DIFFERS {role} blocked_reason "
                          f"{base_env.get('blocked_reason')}≠{swap_env.get('blocked_reason')}")
    row["codes"] = sorted(set(codes))
    row["detail"] = detail
    row["compared"] = compared
    row["incomparable"] = incomparable
    if set(row["codes"]) & set(UNDECIDABLE_CODES):
        # 양면이 똑같아도 비교의 전제가 깨졌다. 케이스가 이것을 기대로 선언할 수는 없다.
        row["actual"] = "undecidable"
        row["ok"] = False
        return row
    if not detail and not compared and incomparable:
        # 비교한 면이 하나도 없다. 같다고도 다르다고도 말할 수 없고, 어떤 기대로도 ok 가 되지 않는다.
        row["actual"] = "incomparable"
        row["ok"] = False
        return row
    row["actual"] = "differ" if detail else "same"
    # 합성 케이스는 검사기가 비교 불가를 **정확히** 선언대로 잡았는지도 본다. 관측 케이스는 그것을
    # 기대로 선언할 수 없으므로(D-b) 비교 불가 면을 ok 에 넣지 않는다 — 판정에서 뺀다는 뜻이 그것이다.
    found = {i["role"]: i["code"] for i in incomparable}
    incomparable_ok = (row["kind"] == OBSERVED_KIND) or found == (case.get("expect_incomparable") or {})
    if row["actual"] == "same":
        row["ok"] = row["expect"] == "same" and incomparable_ok
    else:
        row["ok"] = (row["expect"] == "differ"
                     and set(case.get("expect_codes") or []) <= set(row["codes"])
                     and incomparable_ok)
    return row


def _anchor_failure_row(case, errs):
    """봉투가 앵커 검사를 통과하지 못한 관측 케이스. 비교를 시작하지 않는다 — 무엇을 비교할지 모른다.

    구조 검사를 건너뛰고 이 함수만 부르는 경로에서도 게이트가 열리지 않아야 한다: 판정 불가는 게이트 실패다."""
    return {"id": case.get("id"), "unit_id": case.get("unit_id"),
            "status": case.get("status", "executed"), "kind": _kind(case), "roles": [],
            "expect": case.get("expect"), "actual": "undecidable", "ok": False,
            "codes": [ANCHOR_INVALID], "detail": list(errs), "compared": [], "incomparable": []}


def run_parity(cases, harness_root=None, project_root=None):
    root = Path(harness_root) if harness_root else HARNESS_ROOT
    proot = Path(project_root) if project_root else root
    schema = load_json(root / SCHEMA_PATH)
    roles = load_role_contracts(root)
    rows = []
    for c in cases:
        resolved, products, resolve_errs = resolve_case(c, proot, root)
        rows.append(_anchor_failure_row(c, resolve_errs) if resolve_errs
                    else compare_case(c, schema, roles, results=resolved, products=products))
    executed = [r for r in rows if r["status"] != "pending"]
    pending = [r for r in rows if r["status"] == "pending"]
    matched = sum(1 for r in executed if r["ok"])
    differ = [r for r in executed if r["actual"] == "differ"]
    undecidable = [r for r in executed if r["actual"] == "undecidable"]
    incomparable = [r for r in executed if r["actual"] == "incomparable"]
    observed = [r for r in executed if r["kind"] == OBSERVED_KIND]
    synthetic = [r for r in executed if r["kind"] in SYNTHETIC_KINDS]
    # 게이트 판정에서 뺀 면. 뺐다는 사실은 리포트와 JSON 에 남는다 — 판정이 무엇 위에 섰는지 읽는 사람이 알아야 한다.
    observed_incomparable_faces = [(r["id"], i) for r in observed for i in r["incomparable"]]
    # 비교한 면이 하나도 없는 관측은 판정 근거가 아니다. 그런 관측만 있으면 게이트는 미판정이다.
    decided = [r for r in observed if r["actual"] != "incomparable"]

    # 검사기 자기 검증 — 손으로 쓴 합성 케이스가 선언한 대로 판정되는가.
    # 계산 대상은 리포트 문장이 설명하는 집합과 같아야 한다(합성). 합성 0건에서 PASS 를 인쇄하면
    # 0건을 근거로 통과를 말하는 것이고, FAIL 도 마찬가지로 근거 없는 주장이다 — 그래서 '해당 없음' 이다.
    if not synthetic:
        checker = NOT_APPLICABLE
    else:
        checker = "PASS" if all(r["ok"] for r in synthetic) else "FAIL"
    # 게이트 판정 — 실제 교차 실행 관측만 본다. 관측이 없으면 통과도 실패도 선언하지 않는다(D-b).
    # 비교 불가 면은 판정에서 뺀다(D-73) — 남은 면이 하나도 없으면 미판정이다.
    if not decided:
        gate = "UNDETERMINED"
    elif all(r["actual"] == "same" and r["ok"] for r in decided):
        gate = "PASS"
    else:
        gate = "FAIL"
    return {
        "total": len(rows), "executed": len(executed), "pending": len(pending),
        "observed": len(observed), "synthetic": len(synthetic), "undecidable": len(undecidable),
        "incomparable": len(incomparable),
        "incomparable_faces": sum(len(r["incomparable"]) for r in executed),
        "observed_incomparable_faces": len(observed_incomparable_faces),
        "matched": matched, "checker_verdict": checker, "gate_verdict": gate, "verdict": gate,
        "same": sum(1 for r in executed if r["actual"] == "same"),
        "differ": len(differ), "expected_differ": sum(1 for r in differ if r["ok"]),
        "rows": rows, "schema": SCHEMA_PATH,
    }


def format_parity(rep):
    counts = f"{rep['total']}건"
    if rep["pending"]:
        counts += f"(실행 {rep['executed']} · 미실행 {rep['pending']})"
    differ = f"불일치 {rep['differ']}"
    if rep["differ"]:
        differ += "(전부 기대함)" if rep["differ"] == rep["expected_differ"] else f"(기대 {rep['expected_differ']})"
    checker = CHECKER_TEXT.get(rep["checker_verdict"], rep["checker_verdict"])
    head = (f"parity 리포트 · {counts} · 관측 {rep['observed']}건 · 합성 {rep['synthetic']}건 · "
            f"검사기 자기 검증 {checker} · 동일 {rep['same']} · {differ}")
    if rep["undecidable"]:
        head += f" · 판정 불가 {rep['undecidable']}"
    if rep.get("incomparable_faces"):
        head += f" · {INCOMPARABLE_TEXT} 면 {rep['incomparable_faces']}"
    lines = [head, ""]
    lines.append("| case | unit | 역할 | 출처 | 기대 | 판정 | 근거 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for r in rep["rows"]:
        excluded = [i["detail"] for i in r.get("incomparable") or []]
        if r["status"] == "pending":
            mark, reason, roles = "미실행", "; ".join(r["detail"]), "—"
        elif r["actual"] == "undecidable":
            mark, reason, roles = "판정 불가", "; ".join(r["detail"]), ", ".join(r["roles"])
        elif r["actual"] == "incomparable":
            mark, reason, roles = INCOMPARABLE_TEXT, "; ".join(excluded), ", ".join(r["roles"])
        else:
            # 비교 불가 면이 있는 행은 '부분' 이다 — 비교한 면의 결과와 뺀 면의 이유를 나란히 인쇄한다.
            mark = ("✓" if r["ok"] else "✗") + (" 부분" if excluded else "")
            compared = ", ".join(r.get("compared") or [])
            if r["detail"]:
                parts = ["; ".join(r["detail"])]
            elif excluded:
                parts = [f"{compared}: {CANON_REASON}"]
            else:
                parts = [CANON_REASON]
            reason = "; ".join(parts + excluded)
            roles = ", ".join(r["roles"])
        lines.append(f"| {r['id']} | {r['unit_id']} | {roles} | {r['kind']} | {r['expect']} | {mark} | {reason} |")
    lines.append("")
    if not rep["executed"]:
        lines.append("실행된 케이스가 없다 — 미실행만으로는 통과하지 않는다.")
    if rep["checker_verdict"] == NOT_APPLICABLE:
        lines.append(f"검사기 자기 검증: {CHECKER_TEXT[NOT_APPLICABLE]} — 합성 {rep['synthetic']}건. "
                     f"이 실행은 검사기가 선언대로 판정하는지 확인하지 않았다(합성 케이스가 있어야 확인한다).")
    else:
        lines.append(f"검사기 자기 검증: {rep['checker_verdict']} — 합성 {rep['synthetic']}건이 "
                     f"선언한 대로 판정되는지만 본다. 이것은 게이트를 통과시키지 못한다.")
    excluded_faces = [(r["id"], i) for r in rep["rows"]
                      if r["kind"] == OBSERVED_KIND and r["status"] != "pending" for i in r.get("incomparable") or []]
    if rep["gate_verdict"] == "UNDETERMINED" and rep["observed"] == 0:
        lines.append(f"핵심 동등성 게이트: 미판정 — 관측 케이스 0건"
                     f"(합성 {rep['synthetic']}건은 검사기 검증용이다). "
                     f"실제 교차 실행 관측이 1건 이상 있어야 판정한다(D-b·K-51).")
    elif rep["gate_verdict"] == "UNDETERMINED":
        lines.append(f"핵심 동등성 게이트: 미판정 — 관측 {rep['observed']}건이 전부 {INCOMPARABLE_TEXT}다. "
                     f"두 면이 다른 산출물을 봤고 비교할 다른 면이 없다: "
                     + "; ".join(f"{cid}: {i['detail']}" for cid, i in excluded_faces) + ". "
                     f"같은 산출물을 두 판정 역할에게 보인 관측이 있어야 판정한다(D-73·K-51).")
    else:
        lines.append(f"핵심 동등성 게이트: {GATE_TEXT[rep['gate_verdict']]} — 관측 {rep['observed']}건으로 판정했다.")
        if excluded_faces:
            # 뺀 면을 숨기지 않는다. 이 판정은 비교한 면 위에만 서 있다(K-51).
            lines.append(f"{INCOMPARABLE_TEXT} — 관측 케이스의 {len(excluded_faces)}개 면을 판정에서 뺐다(D-73): "
                         + "; ".join(f"{cid}: {i['detail']}" for cid, i in excluded_faces) + ". "
                         f"**이 판정은 비교한 면으로만 섰다** — 뺀 역할의 동등성은 이 관측으로 증명되지 않았고, "
                         f"같은 산출물을 그 역할의 두 런타임에게 보인 관측이 있어야 판정된다.")
        # 이 판정이 무엇 위에 서 있는지 말한다. 동등성 판정은 **다른 곳에서 끝난 실행**의 결과 계약을 비교한다 —
        # 그 명령들을 여기서 다시 실행할 수는 없다. 재실행 대조는 그 실행이 벌어진 체크아웃의 종료 검사가 한다.
        # 확인하지 못한 것을 확인한 것처럼 인쇄하지 않는다(K-51).
        lines.append("이 판정이 대조한 것은 봉투와 증거 기록이다 — 봉투가 주장한 검사는 evidence_ref 가 가리킨 "
                     "증거의 기록과 명령·종료 코드가 같아야 통과한다. 다만 **여기서 명령을 다시 실행하지는 "
                     "않는다**(다른 곳에서 끝난 실행이다): 증거 기록 자체의 재실행 대조는 그 실행이 벌어진 "
                     "체크아웃의 종료 검사(`romeo close`)가 한다.")
    if rep["gate_verdict"] == "PASS" and rep["checker_verdict"] != "PASS":
        # 두 층이 모두 서야 통과다. 검사기가 옳은지 확인하지 못한 실행은 게이트 통과를 주장할 수 없다(D-b).
        lines.append("게이트는 관측으로 PASS 이지만 검사기 자기 검증이 서지 않았다 — "
                     "검사기가 선언대로 판정하는지 확인하지 못한 실행은 통과를 주장하지 않는다(종료 코드 1).")
    return "\n".join(lines)
