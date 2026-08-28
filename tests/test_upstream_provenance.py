"""고정 upstream commit tree 대조는 네트워크 경계 밖의 샘플로 검증한다."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

import romeo.provenance as provenance
from romeo.cli import main


SOURCE_SHA = "a" * 40
TREE_SHA = "b" * 40
ONE_SHA = "1" * 40
RUN_SHA = "2" * 40


def require_api(name):
    value = getattr(provenance, name, None)
    if value is None:
        raise AssertionError(f"romeo.provenance.{name} 가 아직 없다")
    return value


class TestUpstreamTreeParsing(unittest.TestCase):
    def sample(self):
        return {
            "sha": TREE_SHA,
            "truncated": False,
            "tree": [
                {"path": "one.txt", "mode": "100644", "type": "blob", "sha": ONE_SHA},
                {"path": "run.sh", "mode": "100755", "type": "blob", "sha": RUN_SHA},
            ],
        }

    def test_parses_complete_github_tree_response(self):
        parsed = require_api("parse_upstream_tree")(self.sample())
        self.assertEqual(parsed["tree_sha"], TREE_SHA)
        self.assertEqual(parsed["entries"]["run.sh"], {
            "mode": "100755", "type": "blob", "sha": RUN_SHA,
        })

    def test_rejects_truncated_tree_instead_of_treating_it_as_complete(self):
        payload = self.sample()
        payload["truncated"] = True
        error = require_api("UpstreamVerificationError")
        with self.assertRaises(error):
            require_api("parse_upstream_tree")(payload)


class TestUpstreamComparison(unittest.TestCase):
    def setUp(self):
        self.vendor = {
            "id": "sample-vendor",
            "source_repo": "owner/repo",
            "source_sha": SOURCE_SHA,
            "local_root": "vendor/sample",
            "files": {"one.txt": ONE_SHA, "run.sh": RUN_SHA},
            "modes": {"one.txt": 100644, "run.sh": 100755},
        }
        self.entries = {
            "one.txt": {"mode": "100644", "type": "blob", "sha": ONE_SHA},
            "run.sh": {"mode": "100755", "type": "blob", "sha": RUN_SHA},
        }

    def test_matching_blob_shas_and_modes_pass(self):
        findings, comparisons = require_api("compare_vendor_to_upstream")(self.vendor, self.entries)
        self.assertEqual(findings, [])
        self.assertEqual([item["path"] for item in comparisons], ["one.txt", "run.sh"])
        self.assertTrue(all(item["result"] == "PASS" for item in comparisons))

    def test_blob_and_mode_mismatches_are_both_reported(self):
        entries = dict(self.entries)
        entries["one.txt"] = dict(entries["one.txt"], sha="f" * 40)
        entries["run.sh"] = dict(entries["run.sh"], mode="100644")
        findings, comparisons = require_api("compare_vendor_to_upstream")(self.vendor, entries)
        self.assertEqual(sorted(item[0] for item in findings),
                         ["UPSTREAM_BLOB_MISMATCH", "UPSTREAM_MODE_MISMATCH"])
        self.assertEqual([item["result"] for item in comparisons], ["FAIL", "FAIL"])


class TestUpstreamVerificationEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        (self.root / "provenance").mkdir(parents=True)
        self.vendor = {
            "id": "sample-vendor",
            "source_repo": "owner/repo",
            "source_sha": SOURCE_SHA,
            "local_root": "vendor/sample",
            "files": {"one.txt": ONE_SHA, "run.sh": RUN_SHA},
            "modes": {"one.txt": 100644, "run.sh": 100755},
        }
        (self.root / "provenance/imports.yaml").write_text(
            yaml.safe_dump({"schema_version": 1, "vendors": [self.vendor], "imports": []},
                           sort_keys=False), encoding="utf-8")
        self.payload = {
            "sha": TREE_SHA,
            "truncated": False,
            "tree": [
                {"path": "one.txt", "mode": "100644", "type": "blob", "sha": ONE_SHA},
                {"path": "run.sh", "mode": "100755", "type": "blob", "sha": RUN_SHA},
            ],
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_success_writes_commit_paths_and_result_as_evidence(self):
        def fixed_fetch(source_repo, source_sha):
            if (source_repo, source_sha) != ("owner/repo", SOURCE_SHA):
                raise AssertionError("manifest 의 고정 저장소·커밋을 fetcher 에 전달하지 않았다")
            return self.payload

        findings, evidence = require_api("verify_upstream")(
            self.root, fetcher=fixed_fetch, verified_at="2026-08-28T12:00:00+09:00")

        self.assertEqual(findings, [])
        self.assertEqual(evidence["status"], "PASS")
        self.assertEqual(evidence["vendors"][0]["source_sha"], SOURCE_SHA)
        self.assertEqual([item["path"] for item in evidence["vendors"][0]["comparisons"]],
                         ["one.txt", "run.sh"])
        saved = json.loads((self.root / require_api("UPSTREAM_EVIDENCE_PATH")).read_text(encoding="utf-8"))
        self.assertEqual(saved, evidence)

    def test_fetch_failure_is_error_and_records_unverified_evidence(self):
        def unavailable(_source_repo, _source_sha):
            raise OSError("rate limit")

        error = require_api("UpstreamVerificationError")
        with self.assertRaises(error):
            require_api("verify_upstream")(
                self.root, fetcher=unavailable, verified_at="2026-08-28T12:00:00+09:00")

        saved = json.loads((self.root / require_api("UPSTREAM_EVIDENCE_PATH")).read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "ERROR")
        self.assertEqual(saved["vendors"][0]["result"], "UNVERIFIED")
        self.assertIn("rate limit", saved["vendors"][0]["error"])

    def test_vendor_verify_upstream_cli_runs_the_separate_action(self):
        stderr = io.StringIO()
        stdout = io.StringIO()
        try:
            with mock.patch.object(provenance, "fetch_github_tree", return_value=self.payload):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    result = main(["vendor", "verify-upstream", "--root", str(self.root)])
        except (AttributeError, SystemExit) as exc:
            self.fail(f"vendor verify-upstream CLI 가 연결되지 않았다: {exc}")

        self.assertEqual(result, 0, stderr.getvalue())
        self.assertIn("upstream 검증 PASS", stdout.getvalue())
        self.assertTrue((self.root / require_api("UPSTREAM_EVIDENCE_PATH")).is_file())


if __name__ == "__main__":
    unittest.main()
