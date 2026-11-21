# Retained database product — DB-Scope-01

Source inspection begins at product main `ea5fa528035d025bd7a28698ee7c71194432236c`. This map identifies existing code to retain, not a claim that the pruned candidate has passed. Actual source/test identities are recorded in Plan.

## Public-to-native map

| Public operation | C# implementation | Native execution |
| --- | --- | --- |
| Provider factory / DataSourceBuilder | `src/Data.Postgres`, `src/Data.Sqlite`, `src/Data.NativeHost` | `native/database/host` with provider-specific SQLx composition |
| OpenSessionAsync, pool/session limits | `src/Data.NativeHost` | Host admission/pool/session state and provider I/O |
| BeginTransactionAsync, commit/rollback/savepoints | `src/Data.Transactions` plus Host | `native/database/transactions` and SQLx provider operations |
| Administration.MigrateAsync | `src/Data.Migrations` | `native/database/migrations` and SQLx migration/schema operations |
| Typed values and parameters | `src/Data.Abstractions`, `Data.Codecs`, `Query.Binding` | `native/database/codecs`, `binding`, ordered native parameter conversion |
| From / Where / ordering / query operators | `src/Query.Fluent`, `Query.Native` | `native/database/query`, SeaQuery native query/dialect state |
| Static models and DTO projections | `src/Query.Generator`, `Data.Materialization` | Existing metadata/projection ABI and Host registration |
| Relations and CRUD | `src/Orm.Relations` | `native/database/relations`, SeaQuery and SQLx |
| AsAsyncEnumerable and terminals | `src/Data.Streaming`, `Query.Fluent` | `native/database/streaming`, Host cursor and bounded result ownership |
| Cancellation, errors, disposal | Required Core/Interop modules | Required `native/interop` and database retirement |

The Database assembly includes the existing query, ORM, migration and materialization sources rather than adding new facade layers. Database Host is a required execution component. Its name is not a reason to delete it. Both `libnw_database_sqlite.so` and `libnw_database_postgresql.so` remain maintainer-precompiled provider assets.

The database model generator is `Query.Generator`. Exact database native prototypes come from `tests/Query.Binding/generate.py` and `native/database/binding/signatures-v1.json`. The initial scope inventory incorrectly included `Generators.Model`; the [source dependency audit](https://github.com/IzuSharp/Plan/blob/d74f6bcc8b0e6c4b04105449e8436335bf34bd47/ledger/evidence/batches/DB-Scope-01/dependency-audit.json) found that the generic Generators.Model/CSharp/Rust/Metadata and Analyzers products serve their own proof fixtures, not database projects or packages. Retire those orphan products and retain actual database generation, diagnostics and binding checks.

## Preserve behavior, including failure paths

Maintain existing immutable option snapshots, lazy source/pool creation, explicit connection/session acquisition and per-source resource budgets. Build negotiates a module and starts database-owned runtime state; it does not perform connection or migration I/O. Core itself starts no default global Rust runtime.

Maintain transaction outcome versus cleanup distinctions, failed-transaction rollback, savepoints, pre-admission cancellation and unknown COMMIT outcomes. Unknown does not permit automatic replay. Protocol-clean reuse is independent of local quiescence. Administrative/migration work must preserve lock/connection cleanup and errors; SQLite and PostgreSQL differ and are tested separately.

Maintain parameter binding order, scalar/NULL/UTF-8 and numeric semantics, real SeaQuery SQL rendering, capability checks and explicit unsupported-operation errors. No unsupported SQLite clause may disappear silently. Existing expert SQL remains explicit and parameterized; Fluent failures never fall back to managed execution.

Maintain typed fields, source-owned immutable metadata, exact result shape, static DTO materialization and handwritten/generated metadata routes. Ordinary C# entity/DTO changes reuse native bytes. A query builder's lifecycle and single-writer admission remain distinct from immutable shareable descriptors.

Maintain primary-key CRUD, explicit relations, tenant/composite keys, optional foreign keys, changesets, upsert and version/affected-row semantics. Do not introduce transparent lazy loading, new tracking or additional ORM features.

Maintain stream budgets, early-break/disposal, canceled operations, callback retirement and source/session close. Releasing an owner follows actual native obligations; a timeout is not permission to force-free. Errors retain structured provider diagnostics and cleanup failures without secret connection or parameter logging.

## Transport-independent business operations

A C# application owns its business query methods and calls these database APIs directly. The same method can be invoked by a console, ASP.NET Core HTTP endpoint or standard C# gRPC method. The database library has no dependency on those application transports and introduces no NativeWeave server wrapper.

The mixed `Reference.TaskService` and `Verification.EndToEnd` validation paths are retained only as internal direct database verification executables. Preserve their unique idempotent-create/replay, conflict lookup, pagination, recovery, optimistic CRUD/outbox, nullable/composite relation, same-session, early-cursor and lost-COMMIT-ack oracles. Remove own-server/protocol coupling and unrelated attachment/compression behavior.

## Required validation

Run retained Rust and C# workspace checks and real database/ORM regressions. Pack the [database candidates](../api/nuget-and-consumption.md), then execute external PostgreSQL JIT, PostgreSQL AOT, SQLite JIT and SQLite AOT consumers with typed Fluent and DTO assertions. Inspect dependency graphs, publish files and actual native mappings. Preserve failure attempts and independence of review. This batch measures correctness and scope closure, not performance superiority.
