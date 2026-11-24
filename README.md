# Current task — DB-Rename-01

Update Korda's ten database attributes to the `Db` names in the [naming contract](docs/database/db-attribute-names.md) and [exact mapping](docs/database/db-attribute-names.json). The [public API standard](docs/standards/csharp-public-api-and-documentation.md#3-public-surface-and-package-boundaries) defines domain names independent of implementation language. Preserve attribute namespaces, signatures, defaults, targets and behavior; keep C++20/libpq/sqlite3 execution and the existing JSON source-generation metadata.

Use `task/DB-Rename-01-linux` and a task-marked worktree. Current documentation and examples use the new names; frozen acceptance inputs, actual repository URLs, historical evidence and persisted database identifiers retain their identities. Run `python3 tools/verify_db_rename.py`, which checks this overlay and the original completed Design gates at the frozen baseline. Korda owns compiled/API/package/real-database Native AOT checks. Design checks do not establish product execution.

Push the reviewed changes and open the companion PR. Stop after its checks pass, awaiting maintainer review. **This task does not authorize merging or public publication.** Earlier merge/release instructions below apply only to their completed historical tasks.

## Earlier task authority (historical)

# Current task — DB-API-01

Korda's owner authorizes C# Fluent ORM experience enhancements on Linux x64. Read [ADR-0007](docs/decisions/ADR-0007-fluent-orm-experience.md), the [behavior contract](docs/database/fluent-orm.md), the [mapping overlay](docs/database/fluent-orm.json) and the [published Plan-first checkpoint](https://github.com/IzuSharp/Plan/blob/21e98f7591b4cf1f7fd5b7d5e791ab0be4271515/ledger/evidence/batches/DB-API-01/plan.md). Korda AGENTS.md governs current module registration, direct Native AOT checks and automatic release selection. Work uses `task/DB-API-01-linux` and `.worktree/DB-API-01-linux/`.

Preserve C++20/libpq/sqlite3 execution, database-only scope, compatible ABI and independent provider packages. Compare existing samples with the order/customer/detail journey and fill actual gaps. New contracts are prospective until Plan records implementation and real execution. Run `python3 tools/verify_fluent_orm.py`; it retains the unchanged completed migration gate at Design `de1f4796dc199250b405ea99f2129d611f17b1f6`. Continue the earlier immutable history checks. Old task exclusions below retain historical meaning and do not block DB-API-01. This batch authorizes normal merges and observing triggered releases, with no new performance campaign, clean-image/CPU-emulation campaign or other platform acceptance.

## Previous task authority (historical)

# NativeWeave Design

## Current task: DB-CPP-01

NativeWeave retains its strongly typed C# Fluent ORM for PostgreSQL and SQLite, with ordinary PackageReference consumption and Native AOT. The owner has authorized replacing the existing Rust native implementation with **C++20, libpq and sqlite3**, preserving the current C# API, C ABI, package identities and database state. This is a behavior-compatible migration of the delivered database product. **The first implementation checkpoint is published in [product PR21](https://github.com/IzuSharp/NativeWeave/pull/21). The Design overlay records its source and dependency lock; actual tests, corrections and final acceptance belong to Plan.**

Start with [CURRENT-PHASE.md](CURRENT-PHASE.md), [ADR-0006](docs/decisions/ADR-0006-database-cpp-native.md), [the source-backed migration specification](docs/database/cpp-migration.md), [the machine-readable overlay](docs/database/cpp-migration.json), and [Plan PR26](https://github.com/IzuSharp/Plan/pull/26). The database scope and API documents listed below are accepted baseline inputs; ADR-0006 supersedes their Rust-specific implementation mandate. They remain byte-identical historical inputs where their acceptance hashes require it.

```bash
python3 tools/verify_cpp_migration.py
python3 tools/verify_db_scope_history.py
```

The first command validates the migration decision and runs the unchanged DB-Scope-01 scope/hash gate in a detached checkout of `8298dc4128b745cf1809bad0c3cf02c45eb7f522`. The second retains the earlier complete historical contract gate. Product builds, PostgreSQL/SQLite JIT/AOT behavior, resource limits, sanitizer results and package provenance belong to [Plan's DB-CPP-01 handoff](https://github.com/IzuSharp/Plan/blob/task/DB-CPP-01-linux/ledger/evidence/batches/DB-CPP-01/handoff-linux.md) and its final migration report. DB-API-01 and DB-Perf-01 are not part of this task.

## Accepted baseline documentation

NativeWeave is a strongly typed Fluent ORM for **PostgreSQL and SQLite** in ordinary C# applications, with **Native AOT** support and database execution through Rust **SeaQuery and SQLx**. C# owns application logic, models, DTOs and mapping. Consumers use precompiled native assets and do not need a Rust toolchain.

## Current scope: DB-Scope-01

The owner narrowed the product and terminated Perf-01. [Plan PR24](https://github.com/IzuSharp/Plan/pull/24) records the scope before Design and implementation pruning. This batch retains database sources, pools, sessions, transactions, migrations, typed parameters, Fluent queries, static metadata/DTOs, relations, CRUD, result streaming and their required interop/lifetime/AOT machinery.

**Database Host is retained.** It is the Rust database execution host and its C# facade, not an HTTP server. NativeWeave-owned HTTP/gRPC/MCP servers, protocol wrappers, independent compression engines and HelloWorld packages leave the current product. Applications choose their server; a standard ASP.NET Core endpoint and a standard C# gRPC method can call one application query method.

| Read | Purpose |
| --- | --- |
| [Current phase](CURRENT-PHASE.md) and [ADR-0005](docs/decisions/ADR-0005-database-product-scope.md) | Authority, ordering and stop condition |
| [Scope manifest](docs/current-scope.json) and [requirements](docs/requirements/charter.md) | Exact retained and removed scope |
| [Database product](docs/database/current-product.md) and [architecture](docs/architecture/candidate-boundaries.md) | Actual implementation boundaries and behavior |
| [Public API](docs/api/README.md) and [compiled reference index](docs/api/reference.md) | Source-backed database API and documentation |
| [NuGet consumption](docs/api/nuget-and-consumption.md) and [getting started](docs/api/getting-started.md) | Independent C# applications and precompiled assets |
| [Verification](docs/verification/models-and-matrix.md) | PostgreSQL/SQLite JIT/AOT consumer cells and closure proof |
| [Plan handoff](https://github.com/IzuSharp/Plan/blob/task/DB-Scope-01-linux/ledger/evidence/batches/DB-Scope-01/handoff-linux.md) | Actual progress, logs, PRs and acceptance |

This is Linux x64 scope pruning and regression work. It adds no ORM feature or transport wrapper and makes no new performance claim. Candidate execution and source identities are recorded in Plan; documentation is not execution evidence or a public release announcement.

## Checks

```bash
python3 tools/verify_db_scope.py
python3 tools/verify_db_scope_history.py
```

The first command validates current scope, package/source mapping, current links, archived bytes and negative controls. The second requires full Git history and runs complete unchanged historical acceptance and mutation gates in a detached checkout of `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. Neither runs removed Server fixtures as a current product.

## Historical research and acceptance

The [history entry](docs/history/pre-db-scope-01/README.md) preserves pre-scope API/Server specifications and links the original snapshot. Original contract registry/index, reviews, experiments and raw evidence are historical records with exact identities. They remain available and verified; their accepted status does not transfer to changed DB-Scope-01 documents. The original 34 research, 32 documentation and 48 delivery records remain in Plan's historical graph.
