#!/usr/bin/env python3
"""Check current database scope without accepting changed historical inputs."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FROZEN = "c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9"
EXPECTED = {
    "NativeWeave.Interop.Abi", "NativeWeave.Core", "NativeWeave.Data",
    "NativeWeave.Database.Transactions", "NativeWeave.Data.Streaming",
    "NativeWeave.Query.Binding", "NativeWeave.Query.Generator",
    "NativeWeave.Database", "NativeWeave.Database.Sqlite",
    "NativeWeave.Database.PostgreSql", "NativeWeave.Database.Sqlite.Native",
    "NativeWeave.Database.PostgreSql.Native",
}
FORBIDDEN = re.compile(r"NativeWeave\.(?:Server|Protocols|Engines|HelloWorld|Verification\.ExtensionProof)(?:\.|$)")
RETAIN = {
    "PostgreSQL", "SQLite", "Database Host", "data sources and pools", "sessions",
    "transactions", "migrations", "parameter binding", "strongly typed Fluent",
    "static models and DTO mapping", "relations and CRUD", "streaming results",
    "cancellation", "errors", "resource disposal", "C# to Rust bindings", "Native AOT packaging",
}
CELLS = {"postgresql-jit", "postgresql-aot", "sqlite-jit", "sqlite-aot"}
ORPHAN_TOOLING = {"src/Generators.Model", "src/Generators.CSharp", "src/Generators.Rust", "src/Analyzers",
                  "src/Build.Integration/build_native.py", "src/Build.Integration/NativeWeave.Build.targets",
                  "src/Packaging.Release/prepare.py"}
DATABASE_TOOLING = {"tests/Query.Binding/generate.py", "native/database/binding/signatures-v1.json",
                    "src/Build.Integration/ApiReference", "src/Build.Integration/compose_docs.py",
                    "src/Build.Integration/api/core.json", "tests/Build.Integration/ApiFixture",
                    "tests/Build.Integration/verify_docs.py", "src/Packaging.Release/release.py",
                    "src/Packaging.Release/BuildTasks", "src/Packaging.Release/buildTransitive",
                    "tests/Packaging.Release/ApiCheck", "src/Packaging.Domain", "tests/Packaging.Domain"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def validate(data):
    assert data["task"] == "DB-Scope-01"
    assert data["branch"] == "task/DB-Scope-01-linux"
    assert data["platforms"] == ["linux-x64"]
    assert data["historical_design_commit"] == FROZEN
    assert data["plan_first"]["pr"] == "https://github.com/IzuSharp/Plan/pull/24"
    assert data["plan_first"]["commit"] == "b56ef7a6d4fc8c38cf8da04d555f30bae4e0693a"
    assert set(data["retained_capabilities"]) == RETAIN
    assert set(data["consumer_cells"]) == CELLS
    assert data["product_acceptance"] == "owned_by_plan"
    assert data["performance_work_authorized"] is False
    assert data["new_orm_features_authorized"] is False
    assert data["public_database_release_authorized"] is False
    assert data["native_database_host"] == "native/database/host"
    assert data["managed_database_host"] == "src/Data.NativeHost"
    assert data["native_assets"] == {
        "database.sqlite": "libnw_database_sqlite.so",
        "database.postgresql": "libnw_database_postgresql.so",
    }
    graph = data["packages"]
    assert set(graph) == EXPECTED, "Unexpected database distribution product"
    for name, dependencies in graph.items():
        assert not FORBIDDEN.search(name)
        assert len(dependencies) == len(set(dependencies))
        assert set(dependencies) <= EXPECTED
    assert graph["NativeWeave.Database.Sqlite"][-1] == "NativeWeave.Database.Sqlite.Native"
    assert graph["NativeWeave.Database.PostgreSql"][-1] == "NativeWeave.Database.PostgreSql.Native"
    assert data["optional_packages"] == {
        "NativeWeave.Database.DependencyInjection": {
            "project": "src/Data.NativeHost/DependencyInjection/NativeWeave.Database.DependencyInjection.csproj",
            "dependencies": ["NativeWeave.Database"], "in_candidate_closure": False,
        }
    }
    def closure(name, stack=()):
        assert name not in stack, "Cyclic package closure"
        result = {name}
        for child in graph[name]:
            result |= closure(child, (*stack, name))
        return result
    sqlite = closure("NativeWeave.Database.Sqlite")
    postgres = closure("NativeWeave.Database.PostgreSql")
    assert "NativeWeave.Database.PostgreSql.Native" not in sqlite
    assert "NativeWeave.Database.Sqlite.Native" not in postgres
    assert sqlite | postgres == EXPECTED
    assert {"native/database/host", "src/Data.NativeHost"} <= set(data["retained_product_paths"])
    assert "src/Query.Generator" in data["retained_product_paths"]
    assert DATABASE_TOOLING <= set(data["retained_tooling_paths"])
    assert ORPHAN_TOOLING <= set(data["retired_product_paths"])
    for path in data["retained_product_paths"] + data["retained_tooling_paths"]:
        assert not any(path == retired or path.startswith(retired + "/") for retired in ORPHAN_TOOLING), "Orphan proof tooling was retained"
    assert data["dependency_scope_correction"]["plan_commit"] == "d74f6bcc8b0e6c4b04105449e8436335bf34bd47"
    required_proof = {"nuspecs", "project.assets.json", "publish_directory", "actual_loaded_native_libraries", "zero_consumer_rust_invocations", "verified_data"}
    assert set(data["consumer_proof"]) == required_proof
    assert data["current_checks_claim_product_execution"] is False


def verify_files(data, product_root=None):
    active = [row["path"] for row in data["active_documents"]]
    assert len(active) == len(set(active)) and len(active) >= 20
    assert {"AGENTS.md", "CURRENT-PHASE.md", "README.md", "docs/api/reference.md", "docs/database/current-product.md"} <= set(active)
    for row in data["active_documents"]:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        assert sha(raw) == row["sha256"], ("Current document identity changed", row["path"])
        for target in re.findall(r"\]\(([^)]+)\)", raw.decode()):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            target = target.split("#", 1)[0]
            assert (path.parent / target).is_file() or (path.parent / target).is_dir(), ("Broken current link", row["path"], target)
    for row in data["archived_specifications"]:
        original = subprocess.check_output(["git", "show", FROZEN + ":" + row["original_path"]], cwd=ROOT)
        assert sha(original) == row["sha256"]
        assert (ROOT / row["archive_path"]).read_bytes() == original, ("Historical archive changed", row["archive_path"])
    for row in data["historical_compatibility_inputs"]:
        original = subprocess.check_output(["git", "show", FROZEN + ":" + row["path"]], cwd=ROOT)
        assert (ROOT / row["path"]).read_bytes() == original and sha(original) == row["sha256"]
    for path in data["retired_active_paths"]:
        assert not (ROOT / path).exists(), ("Removed Server specification remains active", path)
    protected = ["docs/contracts/registry.json", "docs/contracts/acceptance-index.json", "docs/traceability/reviews", "verification", "experiments"]
    changed = subprocess.check_output(["git", "diff", "--name-only", FROZEN, "--", *protected], cwd=ROOT, text=True).strip()
    assert not changed, ("Historical accepted evidence/prototype changed", changed)
    if product_root is not None:
        for path in data["retained_product_paths"] + data["retained_tooling_paths"]:
            assert (product_root / path).exists(), ("Retained product path missing", path)
    # A relocated, byte-identical historical blob can contain old whitespace.
    # Only the exact archive paths whose frozen bytes were proved above are
    # excluded; current docs/code and every other new file remain checked.
    exclusions = [":(exclude)" + row["archive_path"] for row in data["archived_specifications"]]
    subprocess.run(["git", "diff", "--check", FROZEN, "--", ".", *exclusions], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product-root", type=Path)
    args = parser.parse_args()
    data = json.loads((ROOT / "docs/current-scope.json").read_text())
    validate(data)
    verify_files(data, args.product_root)
    rejected = []
    for case in ("removed_database_host", "server_package_added", "missing_provider_aot", "cross_provider_native_dependency", "performance_restarted", "unverified_product_acceptance", "orphan_generator_retained", "database_binding_generator_removed"):
        changed = copy.deepcopy(data)
        if case == "removed_database_host":
            changed["retained_capabilities"].remove("Database Host")
        elif case == "server_package_added":
            changed["packages"]["NativeWeave.Server"] = []
        elif case == "missing_provider_aot":
            changed["consumer_cells"].remove("postgresql-aot")
        elif case == "cross_provider_native_dependency":
            changed["packages"]["NativeWeave.Database.Sqlite"].insert(0, "NativeWeave.Database.PostgreSql.Native")
        elif case == "performance_restarted":
            changed["performance_work_authorized"] = True
        elif case == "unverified_product_acceptance":
            changed["product_acceptance"] = "accepted"
        elif case == "orphan_generator_retained":
            changed["retained_product_paths"].append("src/Generators.Model")
        else:
            changed["retained_tooling_paths"].remove("tests/Query.Binding/generate.py")
        try:
            validate(changed)
        except AssertionError:
            rejected.append(case)
        else:
            raise AssertionError(("Invalid current scope accepted", case))
    print(json.dumps({"task": data["task"], "current_scope": "passed", "active_documents": len(data["active_documents"]),
                      "archived_specifications": len(data["archived_specifications"]), "package_ids": len(data["packages"]),
                      "negative_controls": rejected, "product_execution_claimed": False}, indent=2))


if __name__ == "__main__":
    main()
