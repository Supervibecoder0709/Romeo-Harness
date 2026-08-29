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
"""
import json
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


if __name__ == "__main__":
    unittest.main()
