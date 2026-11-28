# Korda-Design contributor guidance

This repository stores design specifications, interface contracts, architecture
decisions and their reasons, research conclusions, and reusable document templates.
[Plan](https://github.com/IzuSharp/Plan) owns plans, task dependencies and progress;
[Korda](https://github.com/IzuSharp/Korda) owns product implementation and tests.
Read [the current phase](CURRENT-PHASE.md) and the relevant contracts before editing.

## Document placement and CI registration

Every new or moved document must be considered for its CI type, and its destination
path must be correctly registered in [eng/ci/registry.py](eng/ci/registry.py).
Reuse an existing directory rule when its type is correct; do not register every
ordinary article individually. Ordinary documentation is a valid type with zero
checks. For new structured documents, first look for a suitable existing type.
Only when a real programmable correctness rule is needed, add the type, paths,
check and tests. Types are additive: one file can have several types.

The [CI guide](eng/ci/README.md) explains the registry and local entry points.
Python selects checks from the actual Git diff. PRs compare the target parent with
GitHub's proposed merge; main pushes compare the event's before and after commits.
Deleted paths and both sides of renames participate. Registered dependencies select
surviving consumers, and each selected check runs once. YAML only starts the runner.

## Editing and validation

Write concise English. Preserve design decisions, their reasons, compatibility
boundaries and honest limitations. Historical design acceptance does not accept
changed specifications or establish product execution. Work in a task-named branch
and worktree; submit normal Git commits and a reviewable PR.

After changing CI, run on Linux:

```bash
python3 -m pip install -r eng/ci/requirements.txt
python3 eng/ci/run.py --all
```

For the normal PR selection, after fetching the target branch:

```bash
python3 eng/ci/run.py --base origin/main --head HEAD --event pull_request
```

The self-tests use temporary Git repositories and actual commits, including PR
merges, multi-commit pushes, additions, deletions, renames and invalid samples.
Registry, checker, router and workflow changes select those self-tests and validate
the current registered structured documents.

## Temporary material

Keep logs, benchmark samples, screenshots, command output, binaries, archives and
interruption/recovery state on the execution machine outside this repository.
Regenerate temporary material when needed. Retain only concise decisions and final
conclusions in the appropriate document. Do not upload documents or intermediate
material as Actions artifacts or copy deleted material to another storage service.
Review final links and the diff before opening the PR. Respect the requested review
stop point; a documentation check grants no product or merge authority.
