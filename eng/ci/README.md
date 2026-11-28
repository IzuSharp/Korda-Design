# Document CI

[registry.py](registry.py) is the path → type → check entry point. [run.py](run.py)
classifies the Git diff, includes affected consumers, deduplicates checks and runs
their registered Python handlers. The workflow contains no document routing rules.

## Current registrations

| Paths | Types | Checks |
| --- | --- | --- |
| Root guides, `docs/**/*.md`, `templates/**/*.md`, this guide | Prose | None |
| Registered source catalogs and database decision JSON | Reference data | None; reviewed narrative has no machine contract |
| `docs/contracts/registry.json` | Contract index + contract dependencies | Nonempty/unique IDs, required fields; dependency existence/version/DAG and specification targets |
| `docs/api/*-coverage.json` | API coverage + coverage references | Draft 2020-12 JSON Schema; unique row IDs and specification targets |
| `schemas/public-api-coverage.schema.json` | Coverage schema | Revalidate the current coverage documents |
| `docs/api/public-api.json` | Historical declarations | Unique IDs, nonempty signatures and defined semantic policies; no product implementation claim |
| Python CI files, requirements, workflow | CI | Self-tests and all current structured checks |

Rules are additive, not exclusive. The same JSON legitimately has more than one
type. `RULES` patterns use Python `fnmatch`: `*` can span directory separators.
New prose inside an existing document directory needs no per-file registration.
An unregistered added or moved destination is an error. Deleted old raw files need
no new registration just to remove them.

`CHECKS` binds a check name to a callable, current input patterns and optional exact
package requirements. A selected check runs once across its current input set.
`dependencies()` registers real consumers: deleting a specification rechecks the
surviving contract/coverage references; changing or deleting the coverage schema
rechecks current coverage documents. Removing a contract from the index checks
every surviving dependency. CI changes also validate the current checks, covering
rules removed or reclassified by the same change.

## Diff semantics

The one Actions checkout uses `fetch-depth: 2` and `filter: blob:none`.

- PR: checkout GitHub's proposed merge. The runner verifies its two parents match
  the event's target and head SHAs, then compares target → proposed merge. Target
  branch changes alone do not select PR checks.
- Main push: verify checkout matches `event.after`, then compare `event.before` →
  `event.after`, including every commit in the push. If needed, fetch only the
  missing endpoint with depth 1 and blob filtering. The initial push compares
  against an explicitly created empty tree.
- `git diff --no-renames --name-status -z` routes a rename as old-path deletion and
  new-path addition. NUL-delimited paths handle spaces safely.

The GitHub event adapter supplies bounds to the same local runner. There are no
fixed historical commits, external repository checkouts, replay jobs, schedules,
manual archive workflows or artifact uploads. Selection reasons and elapsed times
appear in logs and the job summary. Only selected dependencies are installed, into
a temporary directory; a prose-only change does not install `jsonschema`.

## Local Linux commands

Use Python 3.10+ and Git. Install the declared test/check dependency once:

```bash
python3 -m pip install -r eng/ci/requirements.txt
python3 eng/ci/run.py --all
```

To use an isolated temporary dependency install instead:

```bash
python3 eng/ci/run.py --all --install-deps
```

The normal PR command uses the merge base of the target and checked-out head, so
it also works on a topic branch before GitHub creates its merge commit:

```bash
python3 eng/ci/run.py --base origin/main --head HEAD --event pull_request
python3 eng/ci/run.py --base origin/main --head HEAD --event pull_request --plan-only
```

For a main push, pass the actual before and after commits; check out the after
commit before validating its current documents:

```bash
python3 eng/ci/run.py --base BEFORE_SHA --head HEAD --event push
```

`--github-event` consumes `GITHUB_EVENT_NAME` and `GITHUB_EVENT_PATH`. Tests create
real temporary repositories and commits, exercise both CLI bounds and event
payloads, and cover divergent PRs, merged and multi-commit pushes, a shallow
checkout, additions/deletions/renames, multi-type selection, deduplication,
dependent schema/specification failures and valid/invalid checker samples.
Temporary test state is deleted when the test finishes.

## Add a document type

1. Confirm the destination and meaning. Reuse a correct directory rule for prose,
   including zero checks. For structured content, reuse an existing suitable type
   before adding another.
2. If an actual correctness rule requires automation, add its handler in
   [checks.py](checks.py), its `Check` entry and input patterns in `CHECKS`, its
   type's check names in `TYPES`, and the path/type rule in `RULES`.
3. Register only genuine consumer relationships in `dependencies()`. For example,
   a schema's consumers are current documents using that schema.
4. Add positive/negative fixtures and a real-Git selection test in
   [tests/test_ci.py](tests/test_ci.py). Run `--all` and the ordinary diff command.

No dispatcher or YAML edit is needed for another document type or check.
Documentation validation does not establish product, AOT, database or performance
acceptance.
