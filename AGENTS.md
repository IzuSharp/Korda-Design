# Korda-Design working rules

## Current task — DB-Exec-02 complete execution-path refactor

The owner resumed the complete database execution-path refactor on 2026-11-26
(Asia/Shanghai), continuing Korda #37, this Design #20 and Plan #34. Preserve C#
Fluent public behavior, Native AOT, C++ execution and two independent provider
packages. Internal Host structure, command/parameter formats, ABI granularity,
batch construction and mapping may be rewritten or deleted. Read the
[current target](docs/database/query-semantics.md),
[current phase](CURRENT-PHASE.md) and
[Plan execution gates](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/execution-refactor/README.md).
Use task-marked DB-Exec-02 worktrees while continuing the existing open branches.

Plan and the selected Design target precede product edits. The target remains a
candidate until actual public-package correctness and local measurements exist.
The complete-command representation must pass its explicit direct-compilation
versus tape-replay gate; a serializer-only optimization is not task completion.
Keep prior candidate decisions, research, failure records and frozen gate inputs
under their original identities. The new user authority supersedes the old stop
below and permits normal reviewed merges after full verification.

Korda's existing Python diff/dependency planner and independent provider package
jobs govern CI. Benchmarks, profiling, calibration and all four final 1800-second
cells run locally on Linux. Do not add a performance workflow, job, manual button,
scheduled run or hidden benchmark invocation. Continue existing documentation
gates; they do not grant product or performance acceptance.

## Previous stop — final local evidence recorded

The owner instructed completing tests, recording results in the existing PRs and stopping without merging. All four local 1800-second cells and the 16-app/926-file input rehash are complete. Keep the remaining performance gaps and local-only final archive status explicit. No additional benchmark, optimization, merge or release is selected; the continuation below describes the frozen candidate and is not an instruction to restart work.

## Current task — DB-Perf-01 query optimization

The owner has resumed DB-Perf-01 on Linux x64 after the cancellation recorded in
the historical maintenance section below. Preserve the existing C# Fluent API,
`Db*` attributes, independently installable PostgreSQL and SQLite packages, and
C++20/libpq/sqlite3 execution. This authorization does not introduce a managed
provider migration. Read the [current query decision](docs/database/query-semantics.md),
[Fluent behavior](docs/database/fluent-orm.md), [generation boundary](docs/generators/query-generation.md)
and [current phase](CURRENT-PHASE.md) before implementation.

Use a task-marked worktree and branch. Continue implementation in
[Korda #37](https://github.com/IzuSharp/Korda/pull/37), this decision in
[Korda-Design #20](https://github.com/IzuSharp/Korda-Design/pull/20), and evidence in
[Plan #34](https://github.com/IzuSharp/Plan/pull/34). Design and Plan use
`task/DB-Perf-01-query-optimization`; the product uses `task/DB-Perf-01-linux`.
The active [Plan checkpoint](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/plan.md)
and [handoff](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/handoff-linux.md)
own gaps, exact candidate identities, executed checks and actual measurements.
The initial Plan and Design decisions preceded implementation. Continue that order
for a new scheme; do not restart from the old cancellation on `main`.

The current stage is an implementation candidate with local correctness evidence,
not final performance acceptance or a merged delivery. Its complete command path,
eager runtime preparation, scalar origin ownership and cache locking are described
in the current decision. Physical statement caching and fixed-query template
generation remain unimplemented. Keep historical contracts, evidence, frozen
tools and acceptance hashes unchanged.

Korda's current `main` AGENTS and Python module planner govern normal checks.
PostgreSQL and SQLite keep their existing independent package runners and execute
Native AOT consumers directly on Linux. Performance probes and the two-database
30-minute comparisons run locally on Linux when requested, never as PR/push,
manual, or scheduled benchmark CI. Do not add a benchmark job, runner environment,
JIT consumer, clean-image run or CPU-emulation check to this task. Keep benchmark
source ownership registered without an automatic benchmark execution action.

Run the existing documentation gates `python3 tools/verify_db_rename.py` and
`python3 tools/verify_db_scope_history.py`. These validate naming, links and
historical integrity; they cannot accept a new command protocol, a generated query
path, a database result or a performance claim. Product checks and actual local
measurements must establish those claims in Plan.

The canonical design repository is [IzuSharp/Korda-Design](https://github.com/IzuSharp/Korda-Design). It supports the [Korda product](https://github.com/IzuSharp/Korda) and the [Plan repository](https://github.com/IzuSharp/Plan). Read [the repository identity policy](docs/repository-identity.md) before changing an old repository-name reference.

## Previous repository maintenance (historical)

The owner has renamed `IzuSharp/NativeWeave-Design` to `IzuSharp/Korda-Design` and authorized the related README, documentation and repository-reference corrections, a PR and its normal merge. This is repository identity maintenance. DB-Perf-01 is cancelled; no performance or product implementation work is resumed by this maintenance task.

Use current canonical URLs for maintained navigation and live repository lookups. Preserve frozen source records, evidence keys, local replay aliases, historical product identifiers and their hashes. Existing workflow branch filters, permissions and historical inputs remain unchanged. Run `python3 tools/verify_db_rename.py` and `python3 tools/verify_db_scope_history.py` with full Git history.

## Earlier task authority (historical)

The sections below preserve earlier task instructions. Their task-specific branches, stop conditions and implementation authority apply to those recorded batches. Current database behavior and naming remain in the [API index](docs/api/README.md), [Fluent ORM contract](docs/database/fluent-orm.md) and [attribute naming contract](docs/database/db-attribute-names.md).

# Completed Design task — DB-Rename-01

Update Korda's ten database attributes to the `Db` names in the [naming contract](docs/database/db-attribute-names.md) and [exact mapping](docs/database/db-attribute-names.json). The [public API standard](docs/standards/csharp-public-api-and-documentation.md#3-public-surface-and-package-boundaries) defines domain names independent of implementation language. Preserve attribute namespaces, signatures, defaults, targets and behavior; keep C++20/libpq/sqlite3 execution and the existing JSON source-generation metadata.

Use `task/DB-Rename-01-linux` and a task-marked worktree. Current documentation and examples use the new names; frozen acceptance inputs, actual repository URLs, historical evidence and persisted database identifiers retain their identities. Run `python3 tools/verify_db_rename.py`, which checks this overlay and the original completed Design gates at the frozen baseline. Korda owns compiled/API/package/real-database Native AOT checks. Design checks do not establish product execution.

Push the reviewed changes and open the companion PR. Stop after its checks pass, awaiting maintainer review. **This task does not authorize merging or public publication.** Earlier merge/release instructions below apply only to their completed historical tasks.

## Earlier task authority (historical)

# Current task — DB-API-01

Korda's owner authorizes C# Fluent ORM experience enhancements on Linux x64. Read [ADR-0007](docs/decisions/ADR-0007-fluent-orm-experience.md), the [behavior contract](docs/database/fluent-orm.md), the [mapping overlay](docs/database/fluent-orm.json) and the [published Plan-first checkpoint](https://github.com/IzuSharp/Plan/blob/21e98f7591b4cf1f7fd5b7d5e791ab0be4271515/ledger/evidence/batches/DB-API-01/plan.md). Korda AGENTS.md governs current module registration, direct Native AOT checks and automatic release selection. Work uses `task/DB-API-01-linux` and `.worktree/DB-API-01-linux/`.

Preserve C++20/libpq/sqlite3 execution, database-only scope, compatible ABI and independent provider packages. Compare existing samples with the order/customer/detail journey and fill actual gaps. New contracts are prospective until Plan records implementation and real execution. Run `python3 tools/verify_fluent_orm.py`; it retains the unchanged completed migration gate at Design `de1f4796dc199250b405ea99f2129d611f17b1f6`. Continue the earlier immutable history checks. Old task exclusions below retain historical meaning and do not block DB-API-01. This batch authorizes normal merges and observing triggered releases, with no new performance campaign, clean-image/CPU-emulation campaign or other platform acceptance.

## Previous task authority (historical)

# NativeWeave Design working rules — DB-CPP-01

Read [CURRENT-PHASE.md](CURRENT-PHASE.md), [ADR-0006](docs/decisions/ADR-0006-database-cpp-native.md), [the migration overlay](docs/database/cpp-migration.json), and [Plan PR26](https://github.com/IzuSharp/Plan/pull/26) first. The owner now authorizes the existing database native implementation's migration from Rust to C++ on Linux x64, including implementation, tests, commits, PRs and normal merges. Preserve the public C# and C ABI contracts, package identities, historical data and retained database behavior. Use `task/DB-CPP-01-linux` and `ROOT/.worktree/DB-CPP-01-linux/`; update Plan's `ledger/evidence/batches/DB-CPP-01/handoff-linux.md`. DB-API-01 and DB-Perf-01 are separate tasks.

The rules below describe the accepted DB-Scope-01 baseline. Their Rust implementation mandate and previous task stop condition are superseded by ADR-0006; their retained database scope and compatibility obligations remain inputs. The frozen baseline is Design `8298dc4128b745cf1809bad0c3cf02c45eb7f522`. Do not rewrite its scope hashes or historical verifiers to accept changed current files. Run `python3 tools/verify_cpp_migration.py` for the current decision and the unchanged DB-Scope-01 gate at its frozen worktree. Continue `python3 tools/verify_db_scope_history.py` for the earlier immutable contract gates. A document gate never accepts product execution.

## Accepted DB-Scope-01 rules

Read [CURRENT-PHASE.md](CURRENT-PHASE.md), [the current scope](docs/current-scope.json), and [the Plan batch](https://github.com/IzuSharp/Plan/blob/task/DB-Scope-01-linux/ledger/evidence/batches/DB-Scope-01/plan.md) before changing current design.

1. The only current product is a strongly typed Fluent ORM for PostgreSQL and SQLite, backed by Rust SeaQuery and SQLx, usable in ordinary C# applications and Native AOT. The owner authorized DB-Scope-01 design and implementation pruning, regression repair, verification, PRs and normal merges. Earlier research-only and Server mandates are historical.
2. Preserve Database Host: `native/database/host` and `src/Data.NativeHost` own database execution, pools, sessions, native operation retirement and shared database composition. Their name does not make them HTTP servers.
3. Retain every implemented database capability: transactions, migrations, parameters, typed queries, static models/DTOs, relations, CRUD, streams, cancellation, errors, disposal, bindings and packaging. Trace dependencies before removing shared interop or verification code.
4. Remove NativeWeave-owned HTTP/gRPC/MCP servers, bindings, routing and protocol wrappers, independent compression/proof engines and HelloWorld products from current design and default product workflows. Standard ASP.NET Core endpoints and standard C# gRPC methods may call the same application query method; NativeWeave supplies no replacement server wrapper.
5. No new ORM features, performance optimization, benchmark campaign or 30-minute load work belongs in this batch. Linux x64 is its only validation target.
6. Follow the Plan-first, Design-before-product order. Use `task/DB-Scope-01-linux` under `ROOT/.worktree/DB-Scope-01-linux/`; never clear this new workspace when resuming. Record durable progress in Plan's `ledger/evidence/batches/DB-Scope-01/handoff-linux.md`.
7. Historical research, accepted contracts, exact reviews and raw evidence retain their identities. The old 21-contract registry and 34R/32D/48-task records do not accept changed current bytes. Run their unchanged gates at the frozen historical commit through `python3 tools/verify_db_scope_history.py`.
8. Run `python3 tools/verify_db_scope.py` for current design, archived-byte integrity, package/source mappings and negative controls. Actual database builds, JIT/AOT PackageReference consumers, native load closure and merged CI belong to Plan's current acceptance record. A document check is not product execution.
9. Keep exact public signatures and XML/reference checks in the product repository; use [the current API index](docs/api/README.md) and [the API standard](docs/standards/csharp-public-api-and-documentation.md). Ordinary model/DTO changes reuse precompiled assets without a consumer Rust toolchain.
10. Independent agents may review changes, but one GitHub account must not impersonate another approver. Preserve LICENSE, permissions, protection and required checks. Do not publish new domain packages merely because the old demo had automatic publication.
11. Write English documentation, keep secrets out of evidence, preserve failure states honestly and stop after the authorized pruning, verification and merges.
