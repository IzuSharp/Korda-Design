#!/usr/bin/env python3
"""Run unchanged historical acceptance gates at their actual immutable inputs."""
from pathlib import Path
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FROZEN = "c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9"
COMMANDS = [
    ["python3", "tools/verify_public_api.py", "--history", "--require-acceptance"],
    ["python3", "tools/contract_acceptance_checks.py"],
]


def main():
    # Full history is supplied by checkout(fetch-depth: 0). Do not weaken the
    # historical verifier or silently omit a missing source object.
    subprocess.run(["git", "cat-file", "-e", FROZEN + "^{commit}"], cwd=ROOT, check=True)
    with tempfile.TemporaryDirectory(prefix="db-scope-history-", dir=ROOT.parent) as temp:
        work = Path(temp) / "NativeWeave-Design"
        subprocess.run(["git", "worktree", "add", "--detach", str(work), FROZEN], cwd=ROOT, check=True)
        try:
            for command in COMMANDS:
                subprocess.run(command, cwd=work, check=True)
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(work)], cwd=ROOT, check=True)
    print(json.dumps({"historical_design_commit": FROZEN, "unchanged_commands": COMMANDS,
                      "passed": True, "current_product_execution": False}, indent=2))


if __name__ == "__main__":
    main()
