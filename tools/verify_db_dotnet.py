#!/usr/bin/env python3
"""Check the .NET migration overlay and replay prior gates at their original inputs."""
from pathlib import Path
import argparse
import copy
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FROZEN = "dcf4cee8ed4d02a606733aec11bbb36a411d05a9"
CURRENT = [
    "README.md", "AGENTS.md", "CURRENT-PHASE.md",
    "docs/database/dotnet-migration.md", "docs/database/current-product.md",
    "docs/database/fluent-orm.md", "docs/api/README.md", "docs/api/database.md",
    "docs/api/getting-started.md", "docs/api/guides.md", "docs/api/interop.md",
    "docs/api/nuget-and-consumption.md", "docs/api/reference.md",
    "docs/api/documentation-system.md", "docs/generators/query-generation.md",
    "docs/platforms/support-and-aot.md", "docs/verification/models-and-matrix.md",
    "docs/decisions/ADR-0008-database-dotnet-execution.md",
    "docs/standards/csharp-public-api-and-documentation.md",
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(data):
    require(data.get("schema_version") == 1 and data.get("task") == "DB-DotNet-01", "Wrong overlay schema/task")
    require(data.get("branch") == "DB-DotNet-01" and data["baseline"]["Korda-Design"] == FROZEN, "Wrong branch/baseline")
    require(data["packages"] == ["Korda.Database.PostgreSql", "Korda.Database.Sqlite"], "Package identities changed")
    require(data["platforms"] == ["linux-x64"] and data["consumer_modes"] == ["native-aot"], "Wrong execution matrix")
    require(data["execution"]["postgresql"] == "Npgsql" and data["execution"]["sqlite"] == "Microsoft.Data.Sqlite", "Wrong drivers")
    require(data["execution"]["dapper_product_dependency"] is False, "Dapper belongs only to comparison")
    require(data["external_performance_comparator"] == "Dapper.AOT", "Wrong external comparator")
    require(data["long_segments"] == 4 and data["seconds_per_segment"] == 1800, "Wrong long campaign")
    require(data["steady_state_extra_managed_bytes_target"] == 0 and data["business_results_counted"] is True and data["unattributed_bytes_reported"] is True, "Invalid allocation accounting")
    require(data["product_execution_claimed"] is False, "Design cannot claim product execution")
    require(data["merge_authorized"] is True and data["publication_authorized"] is True, "Current owner authorization missing")
    require(data["clean_image_requested"] is False and data["cpu_emulation_requested"] is False, "Unrequested execution scope")
    require(re.fullmatch(r"[0-9a-f]{40}", data["plan_first"]["commit"]) is not None, "Plan-first must use a full commit")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-frozen-history", action="store_true")
    args = parser.parse_args()
    data = json.loads((ROOT / "docs/database/dotnet-migration.json").read_text())
    validate(data)
    protected = [
        "docs/contracts", "docs/history", "docs/traceability", "docs/research", "verification", "experiments",
        "docs/current-scope.json", "docs/api/*.json", "docs/database/cpp-migration.json",
        "docs/database/cpp-migration.md", "docs/database/fluent-orm.json", "docs/database/db-attribute-names.json",
        "docs/database/drivers.md", "docs/database/transactions-and-pooling.md", "docs/database/query-semantics.md",
        "docs/decisions", "tools/verify_db_rename.py", "tools/verify_fluent_orm.py", "tools/verify_cpp_migration.py",
        "tools/verify_db_scope.py", "tools/verify_db_scope_history.py",
    ]
    changed = subprocess.check_output(["git", "diff", "--name-only", FROZEN, "--", *protected], cwd=ROOT, text=True).splitlines()
    require(set(changed) <= {"docs/decisions/ADR-0008-database-dotnet-execution.md"}, "Historical accepted inputs changed: " + repr(changed))
    old_attributes = re.compile(r"\bWeave(?:Table|Column|Key|Version|Ignore|Projection|Constructor|Parameter|Codec|UseCodec)(?:Attribute)?\b")
    for name in CURRENT:
        path = ROOT / name
        content = path.read_text()
        if name not in {"AGENTS.md", "CURRENT-PHASE.md"}:
            require(old_attributes.search(content) is None, "Old attribute in current docs: " + name)
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            require((path.parent / target.split("#", 1)[0]).exists(), "Broken local link: " + name + " -> " + target)
    invalid = []
    bad = copy.deepcopy(data); bad["execution"]["dapper_product_dependency"] = True; invalid.append(bad)
    bad = copy.deepcopy(data); bad["long_segments"] = 8; invalid.append(bad)
    bad = copy.deepcopy(data); bad["business_results_counted"] = False; invalid.append(bad)
    bad = copy.deepcopy(data); bad["product_execution_claimed"] = True; invalid.append(bad)
    bad = copy.deepcopy(data); bad["execution"]["sqlite"] = "custom native"; invalid.append(bad)
    for bad in invalid:
        try:
            validate(bad)
        except ValueError:
            continue
        raise ValueError("Invalid migration overlay was accepted")
    if args.verify_frozen_history:
        with tempfile.TemporaryDirectory(prefix="db-dotnet-design-history-", dir=ROOT.parent) as temp:
            work = Path(temp) / "NativeWeave-Design"
            subprocess.run(["git", "worktree", "add", "--detach", str(work), FROZEN], cwd=ROOT, check=True)
            try:
                subprocess.run(["python3", "tools/verify_db_rename.py"], cwd=work, check=True)
            finally:
                subprocess.run(["git", "worktree", "remove", "--force", str(work)], cwd=ROOT, check=True)
    print(json.dumps({"task": "DB-DotNet-01", "design_gate": "passed", "negative_controls": len(invalid), "product_execution_claimed": False}, indent=2))


if __name__ == "__main__":
    main()
