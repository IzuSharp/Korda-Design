#!/usr/bin/env python3
"""Select and run document checks from the actual Git diff."""
import argparse
from collections import defaultdict
from fnmatch import fnmatchcase
from importlib import metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import registry

ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def matches(path, patterns):
    return any(fnmatchcase(path, pattern) for pattern in patterns)


def current_paths():
    paths = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode().split("\0")
    return sorted({path for path in paths if path and (ROOT / path).is_file()})


def validate_registry():
    for name, checks in registry.TYPES.items():
        if not isinstance(name, str) or not isinstance(checks, tuple):
            raise ValueError("Registry types must map names to check tuples")
        for check in checks:
            if check not in registry.CHECKS:
                raise ValueError(f"Registry type {name} names unknown check {check}")
    for patterns, kinds in registry.RULES:
        if not patterns or not kinds or any(kind not in registry.TYPES for kind in kinds):
            raise ValueError(f"Registry rule has missing paths or unknown types: {patterns}")
    for name, check in registry.CHECKS.items():
        if not callable(check.run):
            raise ValueError(f"Registry check {name} has no callable handler")


def changes(base, head):
    # --no-renames represents a rename as deletion + addition, including both
    # ownership paths without filename parsing or similarity heuristics.
    raw = subprocess.check_output(["git", "diff", "--no-renames", "--name-status", "-z", base, head], cwd=ROOT)
    fields = raw.decode("utf-8").split("\0")
    return [(fields[i][0], fields[i + 1]) for i in range(0, len(fields) - 1, 2)]


def select(root, changed):
    reasons = defaultdict(set)
    unknown = []
    for status, path in changed:
        types = {kind for patterns, kinds in registry.RULES if matches(path, patterns) for kind in kinds}
        if not types and status != "D":
            unknown.append(path)
        for kind in types:
            for check in registry.TYPES[kind]:
                reasons[check].add(f"{kind}: {path}")
    if unknown:
        raise ValueError("Unregistered current paths; update eng/ci/registry.py: " + ", ".join(unknown[:8]))
    for paths, statuses, check in registry.dependencies(root):
        for status, path in changed:
            if status in statuses and matches(path, paths):
                reasons[check].add(f"dependent document: {status} {path}")
    # Registry/checker/workflow changes test the infrastructure and the current
    # registered data, including consumers of rules removed in this diff.
    if "self-tests" in reasons:
        for check in registry.CHECKS:
            reasons[check].add("CI configuration changed")
    return {name: sorted(reason) for name, reason in sorted(reasons.items())}


def ensure_commit(value):
    try:
        return git("rev-parse", "--verify", value + "^{commit}")
    except subprocess.CalledProcessError:
        subprocess.run(["git", "fetch", "--no-tags", "--filter=blob:none", "--depth=1", "origin", value], cwd=ROOT, check=True)
        return git("rev-parse", "--verify", value + "^{commit}")


def event_bounds():
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as stream:
        event = json.load(stream)
    head = git("rev-parse", "HEAD")
    if event_name == "pull_request":
        parents = git("rev-list", "--parents", "-n", "1", "HEAD").split()[1:]
        expected = [event["pull_request"]["base"]["sha"], event["pull_request"]["head"]["sha"]]
        if parents != expected:
            raise ValueError("PR checkout must be the event's merge commit with its target and head parents (fetch-depth: 2)")
        return expected[0], head, "pull_request"
    if event_name == "push":
        if head != event["after"]:
            raise ValueError("Push checkout does not match event.after")
        before = event["before"]
        if before == "0" * 40:
            before = subprocess.check_output(["git", "hash-object", "-w", "-t", "tree", "--stdin"], input=b"", cwd=ROOT).decode().strip()
        else:
            before = ensure_commit(before)
        return before, head, "push"
    raise ValueError(f"Unsupported GitHub event: {event_name}")


def install_requirements(selected, enabled, directory):
    requirements = sorted({requirement for name in selected for requirement in registry.CHECKS[name].requirements})
    missing = []
    for requirement in requirements:
        package, version = requirement.split("==", 1)
        try:
            installed = metadata.version(package)
        except metadata.PackageNotFoundError:
            installed = None
        if installed != version:
            missing.append(requirement)
    if not missing:
        return
    if not enabled:
        raise ValueError("Missing selected-check dependency. Run: python3 -m pip install -r eng/ci/requirements.txt")
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--target", directory, *missing], check=True)
    sys.path.insert(0, directory)
    os.environ["PYTHONPATH"] = directory + os.pathsep + os.environ.get("PYTHONPATH", "")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--event", choices=("pull_request", "push"), default="pull_request")
    parser.add_argument("--github-event", action="store_true")
    parser.add_argument("--all", action="store_true", help="Run every current registered check locally")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--install-deps", action="store_true", help="Install only dependencies of selected checks into a temporary directory")
    args = parser.parse_args()
    start = time.monotonic()
    validate_registry()
    if args.all:
        select(ROOT, [("A", path) for path in current_paths()])
        selected = {name: ["explicit --all"] for name in sorted(registry.CHECKS)}
    else:
        if args.github_event:
            base, head, event = event_bounds()
        else:
            if not args.base:
                parser.error("use --base, --github-event or --all")
            base, head, event = args.base, args.head, args.event
        if git("rev-parse", head) != git("rev-parse", "HEAD"):
            raise ValueError("Check out --head before validating its documents")
        if event == "pull_request":
            base = git("merge-base", base, head)
        selected = select(ROOT, changes(base, head))
    print("Selected checks: " + (", ".join(selected) or "none"), flush=True)
    for name, reasons in selected.items():
        short = "; ".join(reasons[:3])
        extra = f" (+{len(reasons) - 3} more paths)" if len(reasons) > 3 else ""
        print(f"  {name}: {short}{extra}", flush=True)
    if args.plan_only:
        print(json.dumps({"checks": list(selected)}))
        return
    results = []
    with tempfile.TemporaryDirectory(prefix="korda-doc-ci-deps-") as directory:
        install_requirements(selected, args.install_deps, directory)
        for name in selected:
            check = registry.CHECKS[name]
            files = [path for path in current_paths() if matches(path, check.inputs)]
            # Literal required inputs must not silently disappear.
            for pattern in check.inputs:
                if not any(char in pattern for char in "*?[") and not (ROOT / pattern).is_file():
                    raise ValueError(f"{name}: missing required input {pattern}")
            tick = time.monotonic()
            check.run(ROOT, files)
            elapsed = time.monotonic() - tick
            results.append(f"| {name} | passed | {elapsed:.3f}s |")
            print(f"PASS {name} ({len(files)} documents, {elapsed:.3f}s)", flush=True)
    elapsed = time.monotonic() - start
    print(f"Completed {len(selected)} checks in {elapsed:.3f}s", flush=True)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write("## Document checks\n\n")
            if results:
                stream.write("| Check | Result | Time |\n| --- | --- | --- |\n" + "\n".join(results) + "\n")
            else:
                stream.write("No checks selected: ordinary documentation only.\n")
            stream.write(f"\nTotal: {elapsed:.3f}s.\n")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
