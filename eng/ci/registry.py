"""Repository path -> document type -> check registrations.

Add types and checks here; the runner and workflow do not contain path rules.
Patterns use fnmatch (a '*' can span directories). Rules are additive.
"""
from dataclasses import dataclass
from pathlib import Path
import json

from checks import contract_index, contract_links, coverage_schema, coverage_links, declarations, self_tests


@dataclass(frozen=True)
class Check:
    run: object
    inputs: tuple[str, ...] = ()
    requirements: tuple[str, ...] = ()


TYPES = {
    "prose": (),
    "reference-data": (),  # Source catalogs and narrative overlays have no machine contract.
    "contract-index": ("contract-index",),
    "contract-dependencies": ("contract-links",),
    "api-coverage": ("coverage-schema",),
    "coverage-references": ("coverage-links",),
    "coverage-schema": ("coverage-schema",),
    "declarations": ("declarations",),
    "ci": ("self-tests",),
}

# A new article under docs/ or templates/ is already covered. JSON is deliberately
# registered separately: a new structured format must be considered explicitly.
RULES = (
    (("README.md", "AGENTS.md", "CURRENT-PHASE.md", "docs/*.md", "templates/*.md",
      "eng/ci/README.md", "LICENSE", ".gitignore", ".gitattributes"), ("prose",)),
    (("docs/api/*-sources.json",
      "docs/database/*.json", "docs/current-scope.json", "docs/research/*/sources.json",
      "docs/research/*/evidence.json"), ("reference-data",)),
    (("docs/contracts/registry.json",), ("contract-index", "contract-dependencies")),
    (("docs/api/*-coverage.json",), ("api-coverage", "coverage-references")),
    (("schemas/public-api-coverage.schema.json",), ("coverage-schema",)),
    (("docs/api/public-api.json",), ("declarations",)),
    (("eng/ci/*.py", "eng/ci/requirements.txt", ".github/workflows/*.yml"), ("ci",)),
)

CHECKS = {
    "contract-index": Check(contract_index, ("docs/contracts/registry.json",)),
    "contract-links": Check(contract_links, ("docs/contracts/registry.json",)),
    "coverage-schema": Check(coverage_schema, ("docs/api/*-coverage.json",), ("jsonschema==4.23.0",)),
    "coverage-links": Check(coverage_links, ("docs/api/*-coverage.json",)),
    "declarations": Check(declarations, ("docs/api/public-api.json",)),
    "self-tests": Check(self_tests, requirements=("jsonschema==4.23.0",)),
}


def dependencies(root: Path):
    """Current references invalidate their consumer when a target disappears.

    Each tuple is (target paths, change kinds, consumer check). To add a different
    dependency, extend this data function; no dispatcher/YAML change is needed.
    """
    yield (("schemas/public-api-coverage.schema.json",), ("A", "M", "D"), "coverage-schema")
    registry = root / "docs/contracts/registry.json"
    if registry.is_file():
        # A malformed index is reported by its own selected checker.
        try:
            paths = tuple(r["spec_path"] for r in json.loads(registry.read_text())["contracts"] if "spec_path" in r)
        except (ValueError, KeyError, TypeError):
            paths = ()
        yield (paths, ("D",), "contract-links")
    paths = set()
    for file in (root / "docs/api").rglob("*-coverage.json"):
        try:
            paths.update(row["specification"] for row in json.loads(file.read_text())["rows"])
        except (ValueError, KeyError, TypeError):
            continue
    yield (tuple(sorted(paths)), ("D",), "coverage-links")
