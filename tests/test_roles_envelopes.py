"""역할 계약(core/roles)과 실행/결과 계약 스키마(core/schemas/*envelope*.json)를 지킨다.

이 테스트가 지키는 계약:
 1. 두 역할 파일이 공통 필수 키를 갖는다 — 자유 형식으로 흘러가면 라우터·절차가 읽을 것이 없다.
 2. 쓰기 권한 선언이 역할 바인딩과 어긋나지 않는다(D-68). 같은 사실을 두 곳에 문자로 적지 않되 드리프트는 잡는다.
 3. 검토자에게는 쓰기 능력도, 쓰기 경로도 없다(K-66).
 4. 코어 산출물에 런타임명·도구명이 없다(C-C6).
 5. 두 계약의 유효 표본이 통과한다.
 6. 필수 키 누락·미등록 키·허용값 밖 값·패턴 불일치가 거부된다(중첩 object 포함).
 7. blocked_reason 허용값이 정본에서 실측된 3개 그대로다.
 8. 결과 계약이 증거 소유 필드를 복제하지 않는다(K-63).
 9. 스키마 파일 머리가 기존 스키마 3종의 관례를 따른다.
10. 검토자 FAIL 사유가 **닫힌 목록**이다 — 절차 파일의 코드 집합과 결과 계약 스키마의 enum 이 정확히 같다.
11. 스키마가 그 목록을 강제한다 — FAIL 인데 사유가 없거나 목록 밖이면 거부하고, PASS·BLOCKED 는 사유 없이 통과한다.
12. 확인란 체크로 생기는 spec_ref 지문 차이가 FAIL 사유가 아님이 절차 파일에 적혀 있다.
"""
import json
import re
import unittest
from pathlib import Path

from romeo.schema import validate
from romeo.util import load_json, load_yaml, project_root

REPO = project_root(Path(__file__).parent)

ROLE_FILES = {"implementer": REPO / "core/roles/implementer.yaml",
              "reviewer": REPO / "core/roles/reviewer.yaml"}
TASK_SCHEMA = REPO / "core/schemas/task-envelope.json"
RESULT_SCHEMA = REPO / "core/schemas/result-envelope.json"
BINDINGS = REPO / ".harness/bindings.yaml"

REQUIRED_ROLE_KEYS = ["schema_version", "updated", "id", "capabilities", "allowed_paths",
                      "consumes", "produces", "outputs", "guards", "selected_by", "forbidden"]

# 코어에 들어가면 안 되는 이름(C-C6). 소문자 변환 후 부분 문자열로 본다.
FORBIDDEN_NAMES = ["claude", "codex", "orca", "anthropic", "openai", "gemini"]

UNIT_ID = "feat-20260828-license-field-a1b2"
SHA64 = "0" * 64

REVIEW_SKILL = REPO / "core/workflows/review/SKILL.md"

# 절차 파일의 FAIL 사유 목록에서 코드를 뽑는 규칙. 문서가 정본이고 이 상수는 **뽑는 방법**일 뿐이다 —
# 코드 목록 자체를 여기 적으면 그 순간 정본이 둘이 되고, 테스트는 자기가 적은 것을 다시 읽는 동어반복이 된다.
FAIL_ITEM_RE = re.compile(r"^\d+\. \*\*.+?\*\* — `([A-Z][A-Z0-9_]*)`", re.M)
CLOSED_LIST_MARK = "이 목록에 없는 사유로"
ESCAPE_HATCH_MARK = "findings"


def fail_section(text):
    """절차 파일에서 'FAIL 이다' 목록 절만 잘라낸다. 경고 절의 코드가 섞이면 닫힌 목록이 흐려진다."""
    m = re.search(r"\*\*FAIL 이다.*?\n(.*?)\n\*\*경고에 그친다", text, re.S)
    return m.group(1) if m else None


def fail_codes_in_skill(text):
    """FAIL 목록 절의 각 항목 제목에 붙은 코드를 **문서 순서대로** 돌려준다."""
    section = fail_section(text)
    return FAIL_ITEM_RE.findall(section) if section is not None else []


def declares_closed_list(text):
    """목록 밖 사유를 금지하는 선언이 있고, 그 문단 언저리에 대신 갈 길(findings)이 함께 있는가.

    금지만 있고 길이 없으면 막다른 길이 된다 — 정당한 우려를 가진 검토자가 목록에 억지로 끼워 맞추게 된다."""
    section = fail_section(text)
    if section is None:
        return False
    paras = section.split("\n\n")
    hits = [i for i, para in enumerate(paras) if CLOSED_LIST_MARK in para]
    if not hits:
        return False
    return all(ESCAPE_HATCH_MARK in "\n\n".join(paras[i:i + 2]) for i in hits)


def task_sample(role="implementer"):
    return {
        "schema": "romeo/task-envelope@0.1.0",
        "unit_id": UNIT_ID,
        "role": role,
        "spec_ref": {"path": f"docs/work/{UNIT_ID}/spec.md", "sha256": SHA64},
        "base_sha": "d1891da",
        "allowed_paths": ["archive/", f"docs/work/{UNIT_ID}/"] if role == "implementer" else [],
        "guards": [],
        "required_checks": [{"id": "check-1", "command": "bash scripts/validate-repo-archive.sh archive/x",
                             "expect": "exit 0"}],
        "output_schema": "core/schemas/result-envelope.json",
        "workspace": "worktree",
    }


def result_sample(role="implementer"):
    return {
        "schema": "romeo/result-envelope@0.1.0",
        "unit_id": UNIT_ID,
        "role": role,
        "task_envelope_ref": {"path": f".harness/runs/{UNIT_ID}/run-a/task-{role}.json", "sha256": SHA64},
        "checks": [{"id": "check-1", "command": "bash scripts/validate-repo-archive.sh archive/x", "exit_code": 0}],
        "gate_verdict": "PASS",
        "blocked_reason": None,
        "findings": [] if role == "implementer" else [{"summary": "수용 기준 2번의 검사가 없다",
                                                       "file": "docs/work/x/spec.md", "line": 12}],
        "evidence_ref": f"docs/work/{UNIT_ID}/evidence/run-a.yaml" if role == "implementer" else None,
    }


def fail_sample(role="implementer", **over):
    """FAIL 판정을 담은 결과 계약 표본. `fail_reasons` 는 호출자가 정한다(없는 경우도 표본이다)."""
    sample = result_sample(role)
    sample.update({"gate_verdict": "FAIL", "blocked_reason": None})
    if role == "reviewer":
        sample["checks"] = []
    sample.update(over)
    return sample


class TestRoleFiles(unittest.TestCase):
    def test_role_files_declare_required_keys(self):
        for rid, path in ROLE_FILES.items():
            self.assertTrue(path.is_file(), f"{path} 가 없다")
            data = load_yaml(path)
            for key in REQUIRED_ROLE_KEYS:
                self.assertIn(key, data, f"{rid} 역할 파일에 필수 키 {key} 가 없다")
            self.assertEqual(data["id"], rid, "id 는 파일명과 같아야 한다")
            self.assertIsInstance(data["capabilities"], list)
            self.assertIn(data["allowed_paths"]["scope"], ("workspace", "none"))
            self.assertIsInstance(data["forbidden"], list)
            self.assertTrue(data["forbidden"], "forbidden 이 비면 권한 상한을 선언하지 않은 것이다")

    def test_capabilities_use_neutral_vocabulary(self):
        allowed = {"read", "search", "run-command", "workspace-write"}
        for rid, path in ROLE_FILES.items():
            caps = set(load_yaml(path)["capabilities"])
            self.assertTrue(caps <= allowed, f"{rid} 에 정의되지 않은 능력 {caps - allowed}")

    def test_write_capability_matches_bindings(self):
        bindings = load_yaml(BINDINGS)["roles"]
        for rid, path in ROLE_FILES.items():
            caps = load_yaml(path)["capabilities"]
            self.assertEqual("workspace-write" in caps, bool(bindings[rid]["write"]),
                             f"{rid} 의 쓰기 선언이 역할 바인딩과 어긋난다(D-68)")

    def test_reviewer_has_no_write(self):
        data = load_yaml(ROLE_FILES["reviewer"])
        self.assertNotIn("workspace-write", data["capabilities"], "검토자에게 쓰기 능력이 있다(K-66)")
        self.assertEqual(data["allowed_paths"]["scope"], "none", "검토자에게 쓰기 경로가 있다(K-66)")
        self.assertEqual(data["allowed_paths"]["must_include"], [])
        self.assertEqual(data["outputs"]["evidence"], "none")
        self.assertEqual(data["outputs"]["findings"], "envelope")

    def test_implementer_writes_into_unit_dir(self):
        data = load_yaml(ROLE_FILES["implementer"])
        self.assertIn("workspace-write", data["capabilities"])
        self.assertEqual(data["allowed_paths"]["scope"], "workspace")
        self.assertIn("docs/work/{unit_id}/", data["allowed_paths"]["must_include"],
                      "작업 단위 폴더가 쓰기 범위에 없다(K-62)")
        self.assertEqual(data["outputs"]["evidence"], "required")
        self.assertEqual(data["outputs"]["findings"], "none")

    def test_consumes_and_produces_point_at_real_schemas(self):
        for rid, path in ROLE_FILES.items():
            data = load_yaml(path)
            self.assertEqual(data["consumes"], "core/schemas/task-envelope.json")
            self.assertEqual(data["produces"], "core/schemas/result-envelope.json")
            for key in ("consumes", "produces"):
                self.assertTrue((REPO / data[key]).is_file(), f"{rid}.{key} 가 없는 파일을 가리킨다")

    def test_guards_reference_source_instead_of_copying(self):
        for rid, path in ROLE_FILES.items():
            guards = load_yaml(path)["guards"]
            self.assertEqual(guards["source"], "core/policy/execution-guards.yaml")
            self.assertEqual(guards["applies"], "all")
            self.assertTrue((REPO / guards["source"]).is_file())


class TestVendorNeutral(unittest.TestCase):
    def test_core_new_files_have_no_runtime_names(self):
        targets = sorted((REPO / "core/roles").glob("*.yaml")) + \
            sorted((REPO / "core/schemas").glob("*envelope*.json"))
        self.assertEqual(len(targets), 4, f"검사 대상이 4개가 아니다: {targets}")
        for path in targets:
            text = path.read_text(encoding="utf-8").lower()
            for name in FORBIDDEN_NAMES:
                self.assertNotIn(name, text, f"{path.name} 에 런타임·도구 이름 {name!r} 가 있다(C-C6)")


class TestSchemaConventions(unittest.TestCase):
    def test_schema_headers_follow_convention(self):
        expected = {TASK_SCHEMA: "romeo/task-envelope", RESULT_SCHEMA: "romeo/result-envelope"}
        for path, sid in expected.items():
            self.assertTrue(path.is_file(), f"{path} 가 없다")
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(list(data)[:8],
                             ["$schema", "$id", "title", "description", "type",
                              "required", "additionalProperties", "properties"],
                             f"{path.name} 의 키 순서가 기존 스키마와 다르다")
            self.assertEqual(data["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertEqual(data["$id"], sid)
            self.assertTrue(data["title"].startswith("Romeo "), data["title"])
            self.assertEqual(data["type"], "object")
            self.assertIs(data["additionalProperties"], False)

    def test_only_one_description_per_file(self):
        def count(node):
            if isinstance(node, dict):
                return ("description" in node) + sum(count(v) for v in node.values())
            if isinstance(node, list):
                return sum(count(v) for v in node)
            return 0
        for path in (TASK_SCHEMA, RESULT_SCHEMA):
            self.assertEqual(count(load_json(path)), 1,
                             f"{path.name}: description 은 파일당 하나다(개별 property 에 달지 않는다)")

    def test_every_nested_object_forbids_extra_keys(self):
        def walk(node, where):
            if isinstance(node, dict):
                if node.get("type") == "object" or "properties" in node:
                    self.assertIs(node.get("additionalProperties"), False,
                                  f"{where}: 중첩 object 에 additionalProperties:false 가 없다")
                for k, v in node.items():
                    walk(v, f"{where}.{k}")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{where}[{i}]")
        for path in (TASK_SCHEMA, RESULT_SCHEMA):
            walk(load_json(path), path.name)


class TestTaskEnvelope(unittest.TestCase):
    def setUp(self):
        self.schema = load_json(TASK_SCHEMA)

    def test_accepts_two_examples(self):
        for role in ("implementer", "reviewer"):
            self.assertEqual(validate(task_sample(role), self.schema), [],
                             f"{role} 표본이 거부됐다")

    def test_expect_field_is_optional(self):
        sample = task_sample()
        sample["required_checks"][0].pop("expect")
        self.assertEqual(validate(sample, self.schema), [])

    def test_rejects_missing_required(self):
        for key in self.schema["required"]:
            sample = task_sample()
            sample.pop(key)
            self.assertTrue(validate(sample, self.schema), f"필수 키 {key} 를 빼도 통과한다")

    def test_rejects_unknown_key(self):
        sample = task_sample()
        sample["prompt"] = "실행 지시문"
        self.assertTrue(validate(sample, self.schema), "미등록 최상위 키가 통과한다")

    def test_rejects_unknown_key_inside_nested_objects(self):
        sample = task_sample()
        sample["spec_ref"]["note"] = "메모"
        self.assertTrue(validate(sample, self.schema), "spec_ref 안의 미등록 키가 통과한다")
        sample = task_sample()
        sample["required_checks"][0]["timeout"] = 10
        self.assertTrue(validate(sample, self.schema), "required_checks 안의 미등록 키가 통과한다")

    def test_rejects_bad_values(self):
        bad = [("role", "auditor"), ("workspace", "none"), ("base_sha", "zz"),
               ("unit_id", "feat-license-field"), ("schema", "romeo/task-envelope@9")]
        for key, value in bad:
            sample = task_sample()
            sample[key] = value
            self.assertTrue(validate(sample, self.schema), f"{key}={value!r} 가 통과한다")
        sample = task_sample()
        sample["spec_ref"]["sha256"] = "abc"
        self.assertTrue(validate(sample, self.schema), "64자가 아닌 sha256 이 통과한다")

    def test_reviewer_allowed_paths_may_be_empty(self):
        sample = task_sample("reviewer")
        self.assertEqual(sample["allowed_paths"], [])
        self.assertEqual(validate(sample, self.schema), [])

    def test_does_not_carry_runtime_or_prompt_fields(self):
        props = load_json(TASK_SCHEMA)["properties"]
        for key in ("prompt", "model", "effort", "runtime", "run_id", "task_id", "dispatch_id"):
            self.assertNotIn(key, props, f"근거 없는 필드 {key} 가 실행 계약에 있다")


class TestResultEnvelope(unittest.TestCase):
    def setUp(self):
        self.schema = load_json(RESULT_SCHEMA)

    def test_accepts_two_examples(self):
        for role in ("implementer", "reviewer"):
            self.assertEqual(validate(result_sample(role), self.schema), [],
                             f"{role} 표본이 거부됐다")

    def test_accepts_blocked_result(self):
        sample = result_sample()
        sample.update({"checks": [], "gate_verdict": "BLOCKED",
                       "blocked_reason": "BLOCKED_CAPABILITY", "evidence_ref": None})
        self.assertEqual(validate(sample, self.schema), [])

    def test_rejects_missing_required(self):
        for key in self.schema["required"]:
            sample = result_sample()
            sample.pop(key)
            self.assertTrue(validate(sample, self.schema), f"필수 키 {key} 를 빼도 통과한다")

    def test_rejects_unknown_key(self):
        sample = result_sample()
        sample["duration_ms"] = 12
        self.assertTrue(validate(sample, self.schema), "미등록 최상위 키가 통과한다")

    def test_rejects_bad_values(self):
        bad = [("gate_verdict", "OK"), ("role", "auditor"), ("blocked_reason", "BLOCKED_SOMETHING")]
        for key, value in bad:
            sample = result_sample()
            sample[key] = value
            self.assertTrue(validate(sample, self.schema), f"{key}={value!r} 가 통과한다")

    def test_rejects_bad_checks_and_findings(self):
        sample = result_sample()
        sample["checks"][0]["exit_code"] = "0"
        self.assertTrue(validate(sample, self.schema), "exit_code 가 문자열인데 통과한다")
        sample = result_sample()
        sample["checks"][0].pop("command")
        self.assertTrue(validate(sample, self.schema), "command 없는 검사가 통과한다")
        sample = result_sample("reviewer")
        sample["findings"][0].pop("summary")
        self.assertTrue(validate(sample, self.schema), "summary 없는 finding 이 통과한다")
        sample = result_sample("reviewer")
        sample["findings"][0]["summary"] = ""
        self.assertTrue(validate(sample, self.schema), "빈 summary 가 통과한다")

    def test_blocked_reason_enum_is_exactly_canon(self):
        enum = self.schema["properties"]["blocked_reason"]["enum"]
        self.assertEqual(enum, [None, "BLOCKED_CAPABILITY", "BLOCKED_APPROVAL", "BLOCKED_DOCS"],
                         "정본에서 실측된 차단 사유는 3개다 — 늘리지도 줄이지도 않는다")

    def test_does_not_duplicate_evidence_fields(self):
        props = self.schema["properties"]
        owned_by_evidence = ["head_sha", "dirty_tree_hash", "commands", "environment",
                             "changed_files", "artifact_hash", "approvals",
                             "started_at", "finished_at", "run_id", "task_id", "dispatch_id"]
        for key in owned_by_evidence:
            self.assertNotIn(key, props, f"{key} 는 증거가 소유한다 — 결과 계약이 복제하면 안 된다(K-63)")
        self.assertIn("evidence_ref", props, "증거는 경로 참조 하나로만 연결한다")

    def test_evidence_ref_is_nullable(self):
        self.assertEqual(self.schema["properties"]["evidence_ref"]["type"], ["string", "null"])

    # ── notes — 판정에 쓰이지 않는 자유 서술 자리(체크리스트 39) ────────────────────
    def test_notes_is_an_optional_free_text_field_for_both_roles(self):
        """구현자는 findings 를 낼 수 없고(역할 계약 findings: none) 스키마에 서술 자리가 없어
        "이 FAIL 은 내 변경 때문이 아니다" 같은 판정의 맥락을 계약 밖 .md 로 뺐다 — 봉투만 읽는 검사기는 그것을 못 본다."""
        for role in ("implementer", "reviewer"):
            sample = result_sample(role)
            sample["notes"] = "check-5 의 실패 3건은 변경 없이 돌려도 같다 — 회귀가 아니다"
            self.assertEqual(validate(sample, self.schema), [], f"{role} 의 notes 가 거부됐다")
        blocked = result_sample()
        blocked.update({"checks": [], "gate_verdict": "BLOCKED", "blocked_reason": "BLOCKED_CAPABILITY",
                        "evidence_ref": None, "notes": "계약이 그 자리에 없다"})
        self.assertEqual(validate(blocked, self.schema), [])
        self.assertNotIn("notes", self.schema["required"], "notes 는 선택이다 — 없는 봉투도 유효하다")

    def test_notes_must_be_text(self):
        for bad in (12, ["a"], {"k": "v"}, None):
            sample = result_sample()
            sample["notes"] = bad
            self.assertTrue(validate(sample, self.schema), f"notes={bad!r} 가 통과한다")

    def test_notes_do_not_enter_any_verdict(self):
        """스키마 설명이 '판정에 쓰이지 않는다' 고 말하는 것을 코드로 고정한다 — 대조 로직이 이 필드를 읽으면
        서술 한 줄로 판정을 흔들 수 있다. 동등성 판정의 대표값과 역할 계약 검사가 notes 에 무관해야 한다."""
        from romeo.parity import _envelope_defects, _verdict_key
        roles = {r: load_yaml(p) for r, p in ROLE_FILES.items()}
        for role in ("implementer", "reviewer"):
            plain = result_sample(role)
            noted = dict(plain, notes="판정과 무관한 서술")
            self.assertEqual(_verdict_key(plain), _verdict_key(noted))
            self.assertEqual(_envelope_defects("baseline", role, plain, roles),
                             _envelope_defects("baseline", role, noted, roles))
        # description 은 파일당 하나다(위 관례 테스트) — 그래서 이 사실은 최상위 설명이 말한다.
        self.assertIn("notes", self.schema["description"])
        self.assertIn("판정에 쓰이지 않는다", self.schema["description"])


# ── FAIL 사유의 닫힌 목록(체크리스트: 검토자 판정 사유) ────────────────────────────
# 문제: 절차 파일이 사유 8개를 "정본" 이라고 선언하면서 "이 목록에 없으면 FAIL 이 아니다" 를 말하지 않아,
# 검토자가 목록 밖 사유로 게이트를 내릴 수 있었다(하네스가 허용하는 상태를 검토자가 FAIL 로 봤다).
# 해소: 각 사유에 코드를 붙이고, 결과 계약 스키마가 FAIL 봉투에 그 코드를 요구한다 — 목록 밖은 기계가 거른다.


class TestFailReasonsAreAClosedList(unittest.TestCase):
    """AC-1 — 절차 파일의 코드 집합과 스키마 enum 이 정확히 같고, 목록이 닫혀 있다."""

    def setUp(self):
        self.skill = REVIEW_SKILL.read_text(encoding="utf-8")
        self.schema = load_json(RESULT_SCHEMA)

    def test_the_skill_gives_every_fail_reason_a_code(self):
        codes = fail_codes_in_skill(self.skill)
        self.assertEqual(len(codes), 8, f"FAIL 사유 8개에 코드가 붙어 있어야 한다 — 뽑힌 것: {codes}")
        self.assertEqual(len(set(codes)), len(codes), f"코드가 중복된다: {codes}")

    def test_skill_codes_and_schema_enum_are_exactly_the_same_set(self):
        codes = fail_codes_in_skill(self.skill)
        enum = self.schema["properties"]["fail_reasons"]["items"]["enum"]
        self.assertEqual(sorted(codes), sorted(enum),
                         "절차 파일과 스키마의 코드가 어긋난다 — "
                         f"문서에만: {sorted(set(codes) - set(enum))} · 스키마에만: {sorted(set(enum) - set(codes))}")
        self.assertEqual(codes, enum, "두 정본의 코드 순서까지 같게 둔다 — 읽는 사람이 번호로 대조한다")

    def test_the_list_is_declared_closed_and_leaves_a_way_out(self):
        self.assertTrue(declares_closed_list(self.skill),
                        f"'{CLOSED_LIST_MARK}' 선언과 findings 로 가는 길이 FAIL 목록 절에 함께 있어야 한다")

    # ── 거부 케이스 — 추출기가 문서를 실제로 읽는지, 상수를 되읽는지 가른다 ──────────
    def test_extractor_reads_the_document_not_a_constant(self):
        synthetic = ("**FAIL 이다 (하나라도 해당하면 `gate_verdict: FAIL`).**\n\n"
                     "1. **가짜 사유 하나** — `ONLY_ONE`. 설명.\n"
                     "2. **가짜 사유 둘** — `AND_TWO`. 설명.\n\n"
                     "**경고에 그친다 (`findings` 에 담되).**\n")
        self.assertEqual(fail_codes_in_skill(synthetic), ["ONLY_ONE", "AND_TWO"])

    def test_a_code_without_a_backtick_title_is_not_counted(self):
        synthetic = ("**FAIL 이다 (하나라도 해당하면 `gate_verdict: FAIL`).**\n\n"
                     "1. **코드가 없는 항목.** 설명 안에 `LOOKS_LIKE_A_CODE` 가 있어도 세지 않는다.\n\n"
                     "**경고에 그친다 (`findings` 에 담되).**\n")
        self.assertEqual(fail_codes_in_skill(synthetic), [])

    def test_missing_closed_list_declaration_is_detected(self):
        without = self.skill.replace(CLOSED_LIST_MARK, "이 목록은 예시이고 다른 사유로도")
        self.assertFalse(declares_closed_list(without), "선언을 지웠는데도 닫힌 목록으로 읽힌다")

    def test_a_drifted_enum_is_detected(self):
        codes = fail_codes_in_skill(self.skill)
        for drifted in (codes[:-1], codes + ["NEW_REASON"]):
            self.assertNotEqual(sorted(codes), sorted(drifted),
                                "한쪽에만 있는 코드를 같은 집합으로 읽는다")


class TestSchemaRejectsUnknownFailReasons(unittest.TestCase):
    """AC-2 앞겹 — 스키마는 `fail_reasons` 의 **값**만 본다.

    목록 밖 코드는 여기서 거부되고, 유효한 코드는 통과하며, 이 필드가 없는 봉투는 그대로 통과한다.
    `gate_verdict` 로 조건부 필수를 걸지 않는 이유는 이 스키마가 **옛 판정 기록에도 걸리기** 때문이다 —
    `fixtures/parity` 의 관측 케이스 2건이 이미 `done` 인 단위의 봉투를 읽어 같은 스키마로 검증한다.
    사유를 실제로 담았는지는 뒷겹(종료 검사)이 지금 닫으려는 산출물의 봉투에 대해서만 요구한다."""

    def setUp(self):
        self.schema = load_json(RESULT_SCHEMA)
        self.codes = self.schema["properties"]["fail_reasons"]["items"]["enum"]

    def test_an_unlisted_code_is_rejected(self):
        for bad in ("NOT_A_REASON", "ac_unmet", "", "REVIEWER_DISLIKES_IT"):
            self.assertTrue(validate(fail_sample(fail_reasons=[bad]), self.schema),
                            f"목록 밖 코드 {bad!r} 가 통과한다")
        self.assertTrue(validate(fail_sample(fail_reasons=[self.codes[0], "NOT_A_REASON"]), self.schema),
                        "유효한 코드와 섞으면 목록 밖 코드가 통과한다")

    def test_a_non_array_value_is_rejected(self):
        for bad in ("AC_UNMET", {"code": "AC_UNMET"}, 7, None):
            self.assertTrue(validate(fail_sample(fail_reasons=bad), self.schema),
                            f"배열이 아닌 값 {bad!r} 가 통과한다")

    def test_listed_codes_are_accepted_for_both_roles(self):
        for role in ("implementer", "reviewer"):
            for reasons in ([self.codes[0]], self.codes, [self.codes[1], self.codes[-1]]):
                self.assertEqual(validate(fail_sample(role, fail_reasons=reasons), self.schema), [],
                                 f"{role}: 유효한 사유 {reasons} 를 담은 FAIL 이 거부됐다")

    def test_an_envelope_without_the_field_still_passes(self):
        """옛 판정 기록은 소급 수정하지 않는다 — 그 봉투에도 같은 스키마가 걸린다."""
        for role in ("implementer", "reviewer"):
            legacy = fail_sample(role)
            self.assertNotIn("fail_reasons", legacy)
            self.assertEqual(validate(legacy, self.schema), [],
                             f"{role}: 사유 필드가 없는 옛 FAIL 봉투가 거부됐다")
            self.assertEqual(validate(result_sample(role), self.schema), [],
                             f"{role}: PASS 표본이 거부됐다")
        blocked = result_sample()
        blocked.update({"checks": [], "gate_verdict": "BLOCKED",
                        "blocked_reason": "BLOCKED_CAPABILITY", "evidence_ref": None})
        self.assertEqual(validate(blocked, self.schema), [])

    def test_the_field_is_optional_and_the_gap_is_owned_by_the_closing_gate(self):
        self.assertNotIn("fail_reasons", self.schema["required"])
        self.assertEqual(validate(fail_sample(fail_reasons=[]), self.schema), [],
                         "빈 배열은 스키마가 통과시킨다 — 그 자리를 막는 것은 종료 검사다(뒷겹)")
        close_src = (REPO / "romeo/close.py").read_text(encoding="utf-8")
        self.assertIn("fail_reasons", close_src,
                      "앞겹이 값만 보므로 존재를 요구하는 뒷겹이 종료 검사에 있어야 한다")

    def test_duplicates_are_declared_meaningless(self):
        self.assertIs(self.schema["properties"]["fail_reasons"].get("uniqueItems"), True,
                      "같은 사유를 두 번 적는 것은 사유를 하나 더 대는 것이 아니다")

    def test_every_key_is_reachable_through_the_role_branches(self):
        """`anyOf` 세 갈래가 전부 additionalProperties 를 닫고 있다 — 한 갈래라도 키를 빠뜨리면
        그 갈래로 판정되는 봉투에서 이 필드가 '허용되지 않은 키' 가 된다."""
        for branch in self.schema["anyOf"]:
            self.assertIn("fail_reasons", branch["properties"])


class TestSpecHashDifferenceIsNotAFailReason(unittest.TestCase):
    """AC-3 — 확인란 체크로 생기는 spec_ref 지문 차이는 판정을 바꾸지 않는다는 조항이 절차 파일에 있다."""

    ANCHORS = ("AC_TEXT_UNCHANGED", "SPEC_UNCHANGED_SINCE_EVIDENCE")

    def setUp(self):
        self.skill = REVIEW_SKILL.read_text(encoding="utf-8")

    def _clause(self, text=None):
        text = self.skill if text is None else text
        m = re.search(r"\*\*판정을 바꾸지 않는 것\.\*\*(.*?)(?=\n## )", text, re.S)
        return m.group(1) if m else None

    def test_the_clause_exists_in_the_verdict_neutral_section(self):
        clause = self._clause()
        self.assertIsNotNone(clause, "'판정을 바꾸지 않는 것' 절을 찾지 못했다")
        self.assertIn("spec_ref", clause, "지문 차이가 무엇의 차이인지 지목하지 않는다")
        self.assertIn("확인란", clause, "무엇이 그 차이를 만드는지(확인란 체크) 적혀 있지 않다")

    def test_the_clause_names_both_harness_checks_as_grounds(self):
        clause = self._clause()
        for name in self.ANCHORS:
            self.assertIn(name, clause,
                          f"근거로 지목해야 할 {name} 가 조항에 없다 — 하네스가 이를 허용한다는 증거가 사라진다")

    def test_the_named_checks_exist_in_the_closing_gate(self):
        """지목한 이름이 실재해야 근거다 — 문서에만 있는 검사 이름은 주장일 뿐이다(K-51)."""
        close_src = (REPO / "romeo/close.py").read_text(encoding="utf-8")
        for name in self.ANCHORS:
            self.assertIn(name, close_src, f"{name} 가 종료 검사에 없다")

    # ── 거부 케이스 ──────────────────────────────────────────────────────────
    def test_a_clause_missing_an_anchor_is_detected(self):
        for name in self.ANCHORS:
            without = self.skill.replace(name, "다른_검사")
            self.assertNotIn(name, self._clause(without) or "",
                             f"{name} 를 지워도 조항이 그대로 읽힌다")

    def test_a_missing_section_reads_as_absent_not_as_pass(self):
        self.assertIsNone(self._clause("절이 없는 문서\n\n## 다른 절\n"))


if __name__ == "__main__":
    unittest.main()
