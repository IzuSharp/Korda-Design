# Current query optimization validation — DB-Perf-01

The [query decision](../database/query-semantics.md), retained [Fluent contract](../database/fluent-orm.md)
and [Korda main AGENTS](https://github.com/IzuSharp/Korda/blob/main/AGENTS.md) govern
this resumed Linux x64 task. Tests below are requirements, not claims of completion.
The earlier naming matrix remains historical after this section.

| Area | Required observation |
| --- | --- |
| CI routing | Inspect the committed-diff plan; affected product checks run once, unrelated checks skip, and existing PostgreSQL/SQLite packages validate independently and in parallel |
| API and ownership | Existing Fluent signatures, `Db*` attributes, source/owner identity, errors, cancellation, concurrency and disposal behavior remain compatible |
| Complete command | Equivalent SQL/parameter order/results for every converted operator; malformed/version/limit/capability inputs reject before dispatch without partial publication |
| Fixed shape and parameters | `.Prepare()` reuses stable metadata; changed values snapshot independently; missing/extra/foreign parameters and lazy validation precedence retain behavior |
| Provider statements | Any new physical cache proves hits, bounded eviction, schema invalidation, transaction/session isolation, cancel reset/discard and close cleanup |
| Correctness | Both real providers cover dynamic filters, changing parameters, transaction/rollback/unknown outcomes, canceled operations, streaming and early disposal |
| Package consumers | Each actual provider package is independently consumed by an external Native AOT application directly on Linux; ordinary DTO edits preserve native payloads |
| Local comparison | Identical SQL/parameters/results/connections across Fluent, warm Prepare and same-Host SQL; construction/first row/read/release measured separately |
| Local long segments | Final candidate and Dapper.AOT each complete one 30-minute mixed segment per provider; actual source/environment-bound metrics and remaining gaps are recorded in Plan |

Performance runs are local Linux work, never benchmark CI. Do not add a performance
workflow, provider-aggregate benchmark job, JIT consumer, clean-image or emulation
run. Existing module ownership and package actions remain the normal CI entry.
Documentation gates continue unchanged and cannot accept database/performance
execution. [Plan's handoff](https://github.com/IzuSharp/Plan/blob/main/ledger/evidence/batches/DB-Perf-01/handoff-linux.md)
records the actual three PRs, tested source, evidence and unfinished work.

## Historical DB-Rename-01 matrix

# DB-Rename-01 verification and acceptance matrix

Plan and the product PR record actual execution. This document states requirements without premarking tests as passed. The [current naming contract](../database/db-attribute-names.md), retained [DB-API-01 behavior](../database/fluent-orm.md) and [Korda AGENTS](https://github.com/IzuSharp/Korda/blob/task/DB-Rename-01-linux/AGENTS.md) govern scope and dependency-selected checks. Frozen DB-Scope-01 JSON and its execution matrix remain historical inputs.

| Gate | Required observation |
| --- | --- |
| Current names | Ten `Db*Attribute` declarations in the preserved namespace; matching generator, diagnostics, generated C# and reverse scaffolding |
| Generator and mapping | Entities, immutable DTOs and reverse-scaffolded entities compile; ambiguity and other retained negatives produce expected diagnostics |
| Module-selected checks | Committed-diff routing includes affected consumers; required managed/native, formatter/analyzer, API/XML/reference, compatibility and lock checks pass |
| PostgreSQL regressions | Retained real-provider normal/error/cancellation/transaction/migration/relation/stream/disposal assertions selected by dependency |
| SQLite regressions | Retained real-provider normal/error/cancellation/transaction/migration/relation/stream/disposal assertions selected by dependency |
| PostgreSQL candidate AOT | Independently built actual package; external PackageReference order consumer publishes/runs Native AOT with real read/write assertions |
| SQLite candidate AOT | Independently built actual package; external PackageReference order consumer publishes/runs Native AOT with real read/write assertions |
| Packaged API and tutorials | Actual DLL/XML/README expose the new names and no old public attribute types; tutorial source compiles using the candidates |
| Native reuse and closure | Managed model/DTO edits retain packaged and loaded native hashes; assets/dependencies match the selected provider |
| Documentation and scans | Current README/guides/XML/reference/example/filename/link/anchor spellings agree; remaining historical/mapping/physical-name hits are classified |
| Review and PR CI | Diff reviewed, observed current PR checks pass, failures from this batch resolved; stop awaiting maintainer review |

Consumers run directly as Native AOT binaries. This task does not request JIT consumer execution, clean-image/CPU-emulation checks, new performance/platform acceptance, merge or public release. The existing native engine, C ABI, attribute defaults/targets, codec selection and source-generated JSON metadata remain unchanged.

## Retained database failure coverage

Preserve pre-admission commit cancellation with rollback/no durable row, failed-transaction rollback, same physical PostgreSQL session, early stream admission/release and source/session/reference retirement. Preserve nullable/composite foreign keys, typed idempotent create/replay, ReadCommitted next-statement conflict lookup, pagination/recovery, optimistic changes and outbox atomicity. Existing PostgreSQL conflict/lock and lost-COMMIT-ack durable-state oracles remain direct database tests selected through module dependencies.

The naming change does not remove error-path coverage or introduce a server wrapper. Internal direct business-method consumers continue to exercise their database behavior.

## Evidence and failure semantics

Every executed result records source/toolchain/platform, actual command/exit status, data assertions and relevant package/native/executable identities. Preserve failed attempts and real environment limitations. Unknown transaction outcome is not confirmed rollback; pending cleanup is not reclaimed memory. A failed or unexecuted provider lane cannot be inferred from another lane or old CI. An environment limitation does not justify weakening the repository's required checks.

Design structure/link/history checks are distinct from compiler, package, database, Native AOT execution and independent review. The current [Plan handoff](https://github.com/IzuSharp/Plan/blob/task/DB-Rename-01-linux/ledger/evidence/batches/DB-Rename-01/handoff-linux.md) and PRs bind actual outcomes to source identities. This task ends with passing PR checks for maintainer review; earlier merge/release conditions are historical.

## Historical checks

`python3 tools/verify_db_rename.py` checks the naming overlay and runs unchanged DB-API-01, C++ migration and DB-Scope-01 gates at their frozen inputs. `python3 tools/verify_db_scope_history.py` runs original 21-contract/API/English acceptance and mutations at Design `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. No historical acceptance hash is updated to accept a changed current document.

The original stop/clean, Rust workspace, four JIT/AOT consumer cells and merged-main conditions belong to the [immutable DB-Scope-01 matrix](https://github.com/IzuSharp/Korda-Design/blob/8298dc4128b745cf1809bad0c3cf02c45eb7f522/docs/verification/models-and-matrix.md). The frozen `docs/current-scope.json` still records that matrix and its original active-document hashes; it is not this task's current check plan.
