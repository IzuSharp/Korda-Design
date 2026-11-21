#!/usr/bin/env python3
"""Validate the migration decision and preserve the exact accepted scope gate."""
from pathlib import Path
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FROZEN = "8298dc4128b745cf1809bad0c3cf02c45eb7f522"


def git_bytes(path):
    return subprocess.check_output(["git", "show", FROZEN + ":" + path], cwd=ROOT)


def main():
    data = json.loads((ROOT / "docs/database/cpp-migration.json").read_text())
    assert data["schema_version"] == 1
    assert data["task"] == "DB-CPP-01" and data["branch"] == "task/DB-CPP-01-linux"
    assert data["baseline"] == {
        "product": "465cd0f90e6af05ec50eb581156240377cf0825b",
        "design": FROZEN,
        "plan": "1fe52a8bd792ccdbb4bbea17ba59b0ad0c24349d",
    }
    assert data["plan_first"] == {
        "pr": "https://github.com/IzuSharp/Plan/pull/26",
        "commit": "94ade5e6e7df2113be1a500d8ba33c0f0b8d8f11",
    }
    assert data["validation_targets"] == ["linux-x64"]
    assert data["native_language"] == "C++20" and data["llvm_version"] == "23.1.5"
    assert data["clang_format_hook_commit"] == "ce4bd7270237e95464b37d808b942f02785192c4"
    assert data["selected_execution_apis"] == {"postgresql": "libpq", "sqlite": "sqlite3"}
    assert set(data["consumer_cells"]) == {"postgresql-jit", "postgresql-aot", "sqlite-jit", "sqlite-aot"}
    assert data["product_acceptance"] == "owned_by_plan"
    for flag in ("current_checks_claim_product_execution", "performance_work_authorized",
                 "new_orm_features_authorized", "public_database_release_authorized"):
        assert data[flag] is False, flag
    assert data["status"] == "implementation_checkpoint_recorded"
    assert data["dependency_binary_lock_status"] == "locked_at_product_checkpoint"
    checkpoint = data["product_checkpoint"]
    assert checkpoint["repository"] == "https://github.com/IzuSharp/NativeWeave"
    assert checkpoint["pr"] == "https://github.com/IzuSharp/NativeWeave/pull/21"
    assert all(re.fullmatch(r"[0-9a-f]{40}", checkpoint[key]) for key in ("commit", "tree"))
    assert checkpoint["commit"] != data["baseline"]["product"]
    assert checkpoint["dependency_lock_path"] == "native/dependencies.lock.json"
    assert re.fullmatch(r"[0-9a-f]{64}", checkpoint["dependency_lock_sha256"])
    assert checkpoint["native_presets"] == ["linux-x64-release", "linux-x64-asan-ubsan"]
    assert "not final product acceptance" in checkpoint["meaning"]
    for path in ("docs/current-scope.json", "tools/verify_db_scope.py", "tools/verify_db_scope_history.py"):
        assert (ROOT / path).read_bytes() == git_bytes(path), ("Historical gate/input changed", path)
    for relative in data["current_documents"]:
        path = ROOT / relative
        text = path.read_text()
        assert "DB-CPP-01" in text, ("Missing current authority", relative)
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            assert (path.parent / target.split("#", 1)[0]).exists(), ("Broken link", relative, target)
    protected = ["docs/contracts", "docs/traceability/reviews", "verification", "experiments",
                 "docs/history", "docs/api"]
    changed = subprocess.check_output(["git", "diff", "--name-only", FROZEN, "--", *protected], cwd=ROOT, text=True)
    assert not changed.strip(), ("Historical accepted content changed", changed)
    with tempfile.TemporaryDirectory(prefix="db-cpp-scope-", dir=ROOT.parent) as temp:
        work = Path(temp) / "NativeWeave-Design"
        subprocess.run(["git", "worktree", "add", "--detach", str(work), FROZEN], cwd=ROOT, check=True)
        try:
            subprocess.run(["python3", "tools/verify_db_scope.py"], cwd=work, check=True)
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(work)], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--check", FROZEN], cwd=ROOT, check=True)
    print(json.dumps({"task": "DB-CPP-01", "decision_overlay": "passed",
                      "unchanged_db_scope_commit": FROZEN, "product_execution_claimed": False}, indent=2))


if __name__ == "__main__":
    main()
