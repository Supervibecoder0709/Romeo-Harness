"""출처 검증: vendor/ 수정 0 대조 · provenance id 존재 · THIRD_PARTY_NOTICES 신선도.

이 저장소 자체(HEAD 트리)를 한 번 검사하고, 나머지는 임시 트리를 훼손해 거부되는지 본다.
"""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from romeo.provenance import (blob_sha, check_notices, check_provenance_ids,
                              check_vendor, render_notices, write_notices)
from romeo.util import project_root

REPO = project_root(Path(__file__).parent)


def codes(findings):
    return sorted(f[0] for f in findings)


class TestBlobSha(unittest.TestCase):
    def test_matches_git_object_hash(self):
        # git hash-object 와 같은 정의: sha1("blob <len>\0" + content)
        self.assertEqual(blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_empty_file(self):
        self.assertEqual(blob_sha(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")


class TestRepoItself(unittest.TestCase):
    """실제 저장소 상태 — 여기가 깨지면 vendor 트리가 원문과 달라진 것이다."""

    def test_vendor_tree_unmodified(self):
        findings, counts = check_vendor(REPO)
        self.assertEqual(findings, [], f"vendor 수정 감지: {findings}")
        self.assertGreaterEqual(counts["files"], 15)

    def test_provenance_ids_all_known(self):
        findings, _ = check_provenance_ids(REPO)
        self.assertEqual(findings, [], f"미등록 provenance id: {findings}")

    def test_notices_up_to_date(self):
        self.assertEqual(check_notices(REPO), [], "THIRD_PARTY_NOTICES.md 가 imports.yaml 과 다르다")


class TestTamperDetection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        (self.root / "provenance").mkdir(parents=True)
        shutil.copy(REPO / "provenance/imports.yaml", self.root / "provenance/imports.yaml")
        data = yaml.safe_load((self.root / "provenance/imports.yaml").read_text(encoding="utf-8"))
        self.vendor_root = data["vendors"][0]["local_root"]
        shutil.copytree(REPO / self.vendor_root, self.root / self.vendor_root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_copy_passes(self):
        findings, _ = check_vendor(self.root)
        self.assertEqual(findings, [])

    def test_modified_file_is_rejected(self):
        target = self.root / self.vendor_root / "skills/test-driven-development/SKILL.md"
        target.write_text(target.read_text(encoding="utf-8") + "\n한 줄 덧붙임\n", encoding="utf-8")
        findings, _ = check_vendor(self.root)
        self.assertIn("FILE_MODIFIED", codes(findings))

    def test_deleted_file_is_rejected(self):
        (self.root / self.vendor_root / "skills/using-git-worktrees/SKILL.md").unlink()
        findings, _ = check_vendor(self.root)
        self.assertIn("FILE_MISSING", codes(findings))

    def test_extra_file_is_rejected(self):
        # 원문에 없는 파일을 vendor/ 에 몰래 넣는 경로를 막는다
        (self.root / self.vendor_root / "skills/NOTES.md").write_text("직접 쓴 메모\n", encoding="utf-8")
        findings, _ = check_vendor(self.root)
        self.assertIn("FILE_UNTRACKED", codes(findings))

    def test_missing_vendor_dir_is_rejected(self):
        shutil.rmtree(self.root / self.vendor_root)
        findings, _ = check_vendor(self.root)
        self.assertIn("VENDOR_MISSING", codes(findings))

    def test_unknown_provenance_id_is_rejected(self):
        skill = self.root / "core/workflows/plan/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: plan\nprovenance: [does-not-exist]\n---\n\n본문\n", encoding="utf-8")
        findings, counts = check_provenance_ids(self.root)
        self.assertIn("PROVENANCE_UNKNOWN", codes(findings))
        self.assertEqual(counts["files_with_provenance"], 1)

    def test_known_provenance_id_passes(self):
        skill = self.root / "core/workflows/plan/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: plan\nprovenance: [sp-writing-plans-absorbed]\n---\n\n본문\n",
                         encoding="utf-8")
        findings, _ = check_provenance_ids(self.root)
        self.assertEqual(findings, [])


class TestNotices(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("ROMEO_TEST_TMP"))
        self.root = Path(self.tmp.name)
        (self.root / "provenance").mkdir(parents=True)
        shutil.copy(REPO / "provenance/imports.yaml", self.root / "provenance/imports.yaml")

    def tearDown(self):
        self.tmp.cleanup()

    def test_generated_notices_lists_accepted_and_hides_files_of_deferred(self):
        text = write_notices(self.root)
        self.assertIn("sp-test-driven-development", text)
        self.assertIn("MIT", text)
        # deferred 는 후보표에만 있고 원문 경로 목록에는 없어야 한다
        self.assertIn("sp-subagent-driven-development", text)
        self.assertNotIn("scripts/sdd-workspace", text)

    def test_missing_file_is_rejected(self):
        self.assertEqual(codes(check_notices(self.root)), ["NOTICES_MISSING"])

    def test_stale_file_is_rejected(self):
        write_notices(self.root)
        p = self.root / "THIRD_PARTY_NOTICES.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n손으로 덧붙인 줄\n", encoding="utf-8")
        self.assertEqual(codes(check_notices(self.root)), ["NOTICES_STALE"])

    def test_regeneration_is_stable(self):
        self.assertEqual(render_notices(self.root), render_notices(self.root))


if __name__ == "__main__":
    unittest.main()
