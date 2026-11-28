"""Small checks for actual document invariants; no historical replay or outputs."""
from pathlib import Path
import json
import subprocess
import sys


def read(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def contract_index(root, files):
    for path in files:
        data = read(root / path)
        rows = data.get("contracts")
        require(isinstance(rows, list) and rows, f"{path}: contracts must be a non-empty list")
        ids = []
        for row in rows:
            require(isinstance(row, dict), f"{path}: contract must be an object")
            for field in ("id", "version", "status", "title"):
                require(isinstance(row.get(field), str) and row[field].strip(), f"{path}: missing {field}")
            ids.append(row["id"])
            require(isinstance(row.get("dependencies"), list), f"{row['id']}: dependencies must be a list")
            require(bool(row.get("spec_path")) != bool(row.get("historical_specification")),
                    f"{row['id']}: choose a current specification or a historical source")
        require(len(ids) == len(set(ids)), f"{path}: duplicate contract ID")


def contract_links(root, files):
    for path in files:
        rows = read(root / path)["contracts"]
        by_id = {row["id"]: row for row in rows}
        graph = {}
        for row in rows:
            name = row["id"]
            if "spec_path" in row:
                target = Path(row["spec_path"])
                require(not target.is_absolute() and ".." not in target.parts, f"{name}: invalid spec_path")
                require((root / target).is_file(), f"{name}: missing specification {target}")
            else:
                require(row.get("historical_specification", "").startswith("https://github.com/"),
                        f"{name}: historical specification must identify a GitHub source")
            graph[name] = []
            for dep in row["dependencies"]:
                require(isinstance(dep, dict) and dep.get("id") in by_id, f"{name}: unknown contract dependency {dep}")
                require(dep.get("version") == by_id[dep["id"]]["version"], f"{name}: dependency version mismatch")
                graph[name].append(dep["id"])
        visiting, visited = set(), set()

        def visit(name):
            require(name not in visiting, f"contract dependency cycle at {name}")
            if name in visited:
                return
            visiting.add(name)
            for dependency in graph[name]:
                visit(dependency)
            visiting.remove(name)
            visited.add(name)

        for name in graph:
            visit(name)


def coverage_schema(root, files):
    from jsonschema import Draft202012Validator, SchemaError
    schema = read(root / "schemas/public-api-coverage.schema.json")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        raise ValueError(f"Invalid coverage schema: {error.message}") from error
    validator = Draft202012Validator(schema)
    for path in files:
        errors = sorted(validator.iter_errors(read(root / path)), key=lambda e: str(e.path))
        require(not errors, f"{path}: {errors[0].message if errors else ''}")


def coverage_links(root, files):
    ids = set()
    for path in files:
        for row in read(root / path)["rows"]:
            require(row["id"] not in ids, f"{path}: duplicate coverage ID {row['id']}")
            ids.add(row["id"])
            target = Path(row["specification"])
            require(not target.is_absolute() and ".." not in target.parts, f"{path}: invalid specification path")
            require((root / target).is_file(), f"{path}: missing specification {target}")


def declarations(root, files):
    for path in files:
        data = read(root / path)
        require(data.get("product_implemented") is False, f"{path}: historical catalog cannot claim product implementation")
        require(isinstance(data.get("semantic_policies"), dict), f"{path}: missing semantic policies")
        require(isinstance(data.get("symbols"), list) and data["symbols"], f"{path}: missing symbols")
        ids = set()
        for row in data["symbols"]:
            require(isinstance(row.get("id"), str) and row["id"], f"{path}: missing symbol ID")
            require(row["id"] not in ids, f"{path}: duplicate symbol {row['id']}")
            ids.add(row["id"])
            require(isinstance(row.get("signature"), str) and row["signature"].strip(), f"{row['id']}: empty signature")
            require(row.get("semantic_policy") in data["semantic_policies"], f"{row['id']}: unknown semantic policy")


def self_tests(root, files):
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "eng/ci/tests", "-v"], cwd=root, check=True)
