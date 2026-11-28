"""Exercise the normal CLI against real commits and minimal valid documents."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[3]


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="design-ci-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "CI Test")
        self.git("config", "user.email", "ci@example.invalid")
        self.git("config", "uploadpack.allowFilter", "true")
        self.write(".gitignore", "__pycache__/\n*.py[cod]\n")
        for name in ("run.py", "registry.py", "checks.py", "requirements.txt"):
            self.write("eng/ci/" + name, (SOURCE / "eng/ci" / name).read_text())
        # A selected self-test runs a real test in the fixture, without recursively
        # spawning this entire integration suite.
        self.write("eng/ci/tests/test_fixture.py", "import unittest\nclass Fixture(unittest.TestCase):\n def test_marker(self):\n  print('FIXTURE SELF TEST RAN')\n  self.assertTrue(True)\n")
        self.write("docs/spec.md", "# Specification\n")
        self.write("docs/api/one-coverage.json", self.coverage("ONE"))
        self.write("docs/api/two-coverage.json", self.coverage("TWO"))
        self.write("schemas/public-api-coverage.schema.json", (SOURCE / "schemas/public-api-coverage.schema.json").read_text())
        self.write("docs/contracts/registry.json", {"contracts": [
            {"id": "A", "version": "1", "status": "accepted", "title": "A", "spec_path": "docs/spec.md", "dependencies": [{"id": "B", "version": "1"}]},
            {"id": "B", "version": "1", "status": "accepted", "title": "B", "spec_path": "docs/spec.md", "dependencies": []},
        ]})
        self.write("docs/api/public-api.json", {"product_implemented": False, "semantic_policies": {"Policy": {}}, "symbols": [{"id": "T:Type", "signature": "public class Type", "semantic_policy": "Policy"}]})
        self.base = self.commit("baseline")

    @staticmethod
    def coverage(name):
        return {"schema_version": "1", "domain": "test", "baseline": {}, "rows": [{
            "id": name, "feature": "example", "reference_apis": ["API"], "reference_version": "1",
            "public_api": ["API"], "rust_engine": "historical", "adapter_operations": [],
            "support": "planned", "aot": "static", "cost": "bounded", "limitations": "design only",
            "specification": "docs/spec.md", "tasks": ["A01"], "product_implemented": False,
        }]}

    def write(self, path, value):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(value, indent=2) + "\n" if not isinstance(value, str) else value, encoding="utf-8")

    def edit_json(self, path, edit):
        value = json.loads((self.root / path).read_text())
        edit(value)
        self.write(path, value)

    def git(self, *args, cwd=None):
        return subprocess.check_output(["git", *args], cwd=cwd or self.root, text=True, stderr=subprocess.PIPE).strip()

    def commit(self, message):
        self.git("add", "--all")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def run_ci(self, *args, ok=True, event=None, root=None):
        env = os.environ.copy()
        for name in ("GITHUB_EVENT_NAME", "GITHUB_EVENT_PATH", "GITHUB_STEP_SUMMARY"):
            env.pop(name, None)
        if event:
            name, payload = event
            event_file = Path(self.temp.name) / "event.json"
            event_file.write_text(json.dumps(payload))
            env.update(GITHUB_EVENT_NAME=name, GITHUB_EVENT_PATH=str(event_file))
        result = subprocess.run([sys.executable, "eng/ci/run.py", *args], cwd=root or self.root,
                                env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=25)
        self.assertEqual(result.returncode == 0, ok, result.stdout)
        return result.stdout

    def planned(self, base=None):
        output = self.run_ci("--base", base or self.base, "--plan-only")
        return json.loads(output.splitlines()[-1])["checks"]

    def test_valid_all_checks(self):
        output = self.run_ci("--all")
        self.assertIn("Completed 6 checks", output)
        self.assertIn("FIXTURE SELF TEST RAN", output)

    def test_added_article_is_zero_checks(self):
        self.write("docs/new/topic.md", "# New ordinary document\n")
        self.commit("article")
        self.assertEqual(self.planned(), [])
        self.assertIn("Completed 0 checks", self.run_ci("--base", self.base))

    def test_coverage_selects_both_types_once(self):
        for name in ("one", "two"):
            self.edit_json(f"docs/api/{name}-coverage.json", lambda d: d["rows"][0].update(feature="changed"))
        self.commit("coverage")
        self.assertEqual(self.planned(), ["coverage-links", "coverage-schema"])
        output = self.run_ci("--base", self.base)
        self.assertEqual(output.count("PASS coverage-schema"), 1)
        self.assertEqual(output.count("PASS coverage-links"), 1)

    def test_contract_is_multiple_types(self):
        self.edit_json("docs/contracts/registry.json", lambda d: d["contracts"][0].update(title="changed"))
        self.commit("index")
        self.assertEqual(self.planned(), ["contract-index", "contract-links"])
        self.run_ci("--base", self.base)

    def test_invalid_coverage_rejected(self):
        self.edit_json("docs/api/one-coverage.json", lambda d: d["rows"][0].pop("feature"))
        self.commit("invalid coverage")
        self.assertIn("required property", self.run_ci("--base", self.base, ok=False))

    def test_nested_invalid_coverage_is_checked(self):
        self.write("docs/api/nested/invalid-coverage.json", {"rows": []})
        self.commit("nested invalid addition")
        self.run_ci("--base", self.base, ok=False)

    def test_rename_to_nested_invalid_coverage_is_checked(self):
        self.git("mv", "docs/api/one-coverage.json", "docs/api/renamed-coverage.json")
        self.edit_json("docs/api/renamed-coverage.json", lambda d: d["rows"][0].pop("feature"))
        (self.root / "docs/api/nested").mkdir()
        self.git("mv", "docs/api/renamed-coverage.json", "docs/api/nested/invalid-coverage.json")
        self.commit("nested invalid rename")
        self.assertIn("required property", self.run_ci("--base", self.base, ok=False))

    def test_nested_coverage_dependency_follows_spec_deletion(self):
        self.write("docs/nested-spec.md", "# Separate specification\n")
        document = self.coverage("NESTED")
        document["rows"][0]["specification"] = "docs/nested-spec.md"
        self.write("docs/api/nested/valid-coverage.json", document)
        before = self.commit("nested coverage")
        (self.root / "docs/nested-spec.md").unlink()
        self.commit("remove nested specification")
        self.assertEqual(self.planned(before), ["coverage-links"])
        self.assertIn("missing specification", self.run_ci("--base", before, ok=False))

    def test_duplicate_coverage_id_rejected(self):
        self.edit_json("docs/api/one-coverage.json", lambda d: d["rows"][0].update(id="TWO"))
        self.commit("duplicate coverage")
        self.assertIn("duplicate coverage ID", self.run_ci("--base", self.base, ok=False))

    def test_duplicate_contract_id_rejected(self):
        self.edit_json("docs/contracts/registry.json", lambda d: d["contracts"].append(d["contracts"][0]))
        self.commit("duplicate")
        self.assertIn("duplicate contract ID", self.run_ci("--base", self.base, ok=False))

    def test_removed_referenced_contract_rejected(self):
        self.edit_json("docs/contracts/registry.json", lambda d: d["contracts"].pop())
        self.commit("remove referenced B")
        self.assertIn("unknown contract dependency", self.run_ci("--base", self.base, ok=False))

    def test_dependency_cycle_rejected(self):
        self.edit_json("docs/contracts/registry.json", lambda d: d["contracts"][1].update(dependencies=[{"id": "A", "version": "1"}]))
        self.commit("cycle")
        self.assertIn("dependency cycle", self.run_ci("--base", self.base, ok=False))

    def test_dependency_version_rejected(self):
        self.edit_json("docs/contracts/registry.json", lambda d: d["contracts"][1].update(version="2"))
        self.commit("version mismatch")
        self.assertIn("version mismatch", self.run_ci("--base", self.base, ok=False))

    def test_deleted_spec_selects_surviving_consumers(self):
        (self.root / "docs/spec.md").unlink()
        self.commit("remove specification")
        self.assertEqual(self.planned(), ["contract-links", "coverage-links"])
        self.assertIn("missing specification", self.run_ci("--base", self.base, ok=False))

    def test_schema_edit_checks_unchanged_documents(self):
        self.edit_json("schemas/public-api-coverage.schema.json", lambda d: d["required"].append("new_field"))
        self.commit("schema")
        self.assertEqual(self.planned(), ["coverage-schema"])
        self.assertIn("new_field", self.run_ci("--base", self.base, ok=False))

    def test_schema_deletion_rejected(self):
        (self.root / "schemas/public-api-coverage.schema.json").unlink()
        self.commit("delete schema")
        self.assertEqual(self.planned(), ["coverage-schema"])
        self.run_ci("--base", self.base, ok=False)

    def test_invalid_schema_rejected(self):
        self.edit_json("schemas/public-api-coverage.schema.json", lambda d: d.update(type="imaginary"))
        self.commit("invalid schema")
        self.assertIn("Invalid coverage schema", self.run_ci("--base", self.base, ok=False))

    def test_declaration_invalid_policy_rejected(self):
        self.edit_json("docs/api/public-api.json", lambda d: d["symbols"][0].update(semantic_policy="missing"))
        self.commit("invalid policy")
        self.assertEqual(self.planned(), ["declarations"])
        self.assertIn("unknown semantic policy", self.run_ci("--base", self.base, ok=False))

    def test_declaration_duplicate_rejected(self):
        self.edit_json("docs/api/public-api.json", lambda d: d["symbols"].append(d["symbols"][0]))
        self.commit("duplicate declaration")
        self.assertIn("duplicate symbol", self.run_ci("--base", self.base, ok=False))

    def test_rename_considers_old_and_new_paths(self):
        self.git("mv", "docs/api/one-coverage.json", "docs/api/renamed-coverage.json")
        self.commit("rename")
        self.assertEqual(self.planned(), ["coverage-links", "coverage-schema"])
        output = self.run_ci("--base", self.base)
        self.assertIn("docs/api/one-coverage.json", output)
        self.assertIn("docs/api/renamed-coverage.json", output)
        self.assertEqual(output.count("PASS coverage-schema"), 1)

    def test_rename_ordinary_into_structured_path(self):
        self.write("docs/article.md", "not json\n")
        before = self.commit("article")
        self.git("mv", "docs/article.md", "docs/api/new-coverage.json")
        self.commit("move to structured type")
        self.assertEqual(self.planned(before), ["coverage-links", "coverage-schema"])
        self.run_ci("--base", before, ok=False)

    def test_unregistered_addition_rejected(self):
        self.write("new-format/data.csv", "unregistered")
        self.commit("unregistered")
        self.assertIn("Unregistered", self.run_ci("--base", self.base, ok=False))

    def test_non_ascii_unregistered_destination_rejected(self):
        self.write("unregistered/数据.json", {"value": 1})
        self.commit("Unicode addition")
        self.assertIn("Unregistered", self.run_ci("--base", self.base, ok=False))

    def test_whitespace_filename_is_one_path(self):
        self.write("docs/name with spaces\nand newline.md", "# Ordinary article\n")
        self.commit("whitespace path")
        self.assertEqual(self.planned(), [])

    def test_obsolete_raw_deletion_does_not_require_new_registration(self):
        self.write("old-outputs/run.log", "old log")
        before = self.commit("old raw material")
        (self.root / "old-outputs/run.log").unlink()
        self.commit("cleanup")
        self.assertEqual(self.planned(before), [])

    def test_registry_edit_runs_self_tests(self):
        with (self.root / "eng/ci/registry.py").open("a") as stream:
            stream.write("\n# registration change\n")
        self.commit("registry")
        self.assertIn("self-tests", self.planned())
        self.assertIn("FIXTURE SELF TEST RAN", self.run_ci("--base", self.base))

    def test_router_edit_runs_self_tests(self):
        with (self.root / "eng/ci/run.py").open("a") as stream:
            stream.write("\n# router change\n")
        self.commit("router")
        self.assertIn("FIXTURE SELF TEST RAN", self.run_ci("--base", self.base))

    def test_registry_unknown_type_rejected(self):
        with (self.root / "eng/ci/registry.py").open("a") as stream:
            stream.write("\nRULES += (((\"docs/new.json\",), (\"not-registered\",)),)\n")
        self.commit("bad registry")
        self.assertIn("unknown types", self.run_ci("--base", self.base, ok=False))

    def test_registry_unknown_check_rejected(self):
        with (self.root / "eng/ci/registry.py").open("a") as stream:
            stream.write("\nTYPES['new'] = ('not-registered',)\n")
        self.commit("bad check")
        self.assertIn("unknown check", self.run_ci("--base", self.base, ok=False))

    def test_all_rejects_unregistered_current_files(self):
        self.write("unknown.json", {})
        self.assertIn("Unregistered", self.run_ci("--all", ok=False))

    def test_new_type_and_check_do_not_change_dispatcher(self):
        with (self.root / "eng/ci/registry.py").open("a") as stream:
            stream.write("\nTYPES['new-format'] = ('custom',)\nRULES += (((\"docs/custom.json\",), (\"new-format\",)),)\nCHECKS['custom'] = Check(lambda root, files: print('CUSTOM CHECK RAN'), ('docs/custom.json',))\n")
        self.write("docs/custom.json", {"value": 1})
        self.commit("extension")
        self.assertIn("CUSTOM CHECK RAN", self.run_ci("--base", self.base))

    def merge_fixture(self):
        self.git("checkout", "-q", "-b", "topic")
        self.write("docs/new/article.md", "# Article\n")
        topic = self.commit("PR document")
        self.git("checkout", "-q", "main")
        self.edit_json("schemas/public-api-coverage.schema.json", lambda d: d.update(title="Target branch change"))
        target = self.commit("target changed independently")
        self.git("merge", "-q", "--no-ff", "topic", "-m", "Merge PR")
        merged = self.git("rev-parse", "HEAD")
        return target, topic, merged

    def test_pr_target_diff_and_merged_main_push_use_same_selection(self):
        target, topic, merged = self.merge_fixture()
        pr = ("pull_request", {"pull_request": {"base": {"sha": target}, "head": {"sha": topic}}})
        output = self.run_ci("--github-event", event=pr)
        self.assertIn("Completed 0 checks", output)
        push = ("push", {"before": target, "after": merged})
        self.assertIn("Completed 0 checks", self.run_ci("--github-event", event=push))

    def test_pr_explicit_head_uses_merge_base(self):
        target, topic, merged = self.merge_fixture()
        self.git("checkout", "-q", "topic")
        self.assertEqual(self.planned(target), [])

    def test_push_includes_all_commits_not_only_latest(self):
        self.edit_json("docs/api/one-coverage.json", lambda d: d["rows"][0].pop("feature"))
        self.commit("first push commit invalid")
        self.write("docs/latest.md", "# Last commit\n")
        after = self.commit("second push commit prose")
        event = ("push", {"before": self.base, "after": after})
        self.assertIn("required property", self.run_ci("--github-event", event=event, ok=False))

    def test_push_checkout_mismatch_rejected(self):
        self.write("docs/new.md", "# Change\n")
        self.commit("new")
        event = ("push", {"before": self.base, "after": self.base})
        self.assertIn("event.after", self.run_ci("--github-event", event=event, ok=False))

    def test_initial_push_uses_real_empty_tree(self):
        event = ("push", {"before": "0" * 40, "after": self.base})
        output = self.run_ci("--github-event", event=event)
        self.assertIn("Completed 6 checks", output)

    def test_pr_parent_mismatch_rejected(self):
        target, topic, merged = self.merge_fixture()
        event = ("pull_request", {"pull_request": {"base": {"sha": self.base}, "head": {"sha": topic}}})
        self.assertIn("merge commit", self.run_ci("--github-event", event=event, ok=False))

    def test_shallow_pr_checkout_and_missing_push_endpoint(self):
        target, topic, merged = self.merge_fixture()
        clone = Path(self.temp.name) / "shallow"
        self.git("clone", "-q", "--depth=2", "--filter=blob:none", self.root.as_uri(), str(clone))
        self.assertEqual(self.git("rev-parse", "--is-shallow-repository", cwd=clone), "true")
        pr = ("pull_request", {"pull_request": {"base": {"sha": target}, "head": {"sha": topic}}})
        self.assertIn("Completed 0 checks", self.run_ci("--github-event", event=pr, root=clone))
        # The baseline predates both shallow parents; push fetches just that
        # endpoint and does not expand to a full-history checkout.
        push = ("push", {"before": self.base, "after": merged})
        output = self.run_ci("--github-event", event=push, root=clone)
        self.assertIn("PASS coverage-schema", output)
        self.assertEqual(self.git("rev-parse", "--is-shallow-repository", cwd=clone), "true")


if __name__ == "__main__":
    unittest.main()
