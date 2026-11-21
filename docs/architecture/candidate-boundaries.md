# Current database architecture — DB-Scope-01

This replaces the earlier framework/Server candidate boundary for current work. [ADR-0005](../decisions/ADR-0005-database-product-scope.md) fixes scope; [the database guide](../database/current-product.md) maps existing implementation.

| Boundary | Responsibilities | Dependency rule |
| --- | --- | --- |
| C# application | Business queries, entities, DTOs and caller-chosen transport | Console, ASP.NET Core or standard C# gRPC service |
| Typed database facade | Fluent calls, static metadata, validation, parameters and DTO construction | No owned HTTP/gRPC/MCP runtime or managed SQL dialect |
| Required interop | ABI, bindings, async/cancellation, callbacks, errors, buffers and retirement | Retain by database dependency; no global Core runtime |
| Rust Database Host | Per-source execution/runtime, pool/session, transactions, migrations, query/stream lifetime | Retained database component, not an HTTP server |
| SeaQuery and SQLx | Query construction/dialects and real provider I/O | Verify PostgreSQL and SQLite separately |

The managed Database assembly compiles `Query.Native`, `Query.Fluent`, `Orm.Relations`, `Data.Migrations` and `Data.Materialization`. Provider facades supply precompiled native identity and configuration. Normal applications require no raw handles, Rust syntax, native model compilation or native-library search configuration.

## Ownership and cancellation

A source owns its pool/runtime; sessions, transactions, cursors and streams have explicit lifetime and admission. Static metadata can be shared; mutable query builders, sessions, transactions and enumerators are not implicitly safe for concurrent mutation. Raw-handle nonzero checks do not replace logical admission.

Public completion, native quiescence, connection reuse and durable transaction outcome are separate facts. A canceled Task proves neither that COMMIT had no effect nor that callbacks are unreachable. Close timeouts report pending cleanup and cannot free active owners. Unconfirmed protocol state prevents pool reuse. Preserve original and cleanup failures.

## Query and mapping

C# transports validated metadata/operations; SeaQuery owns query state and rendering, and SQLx binds/execututes. SQL NULL, ordered parameters, capability checks and provider limits remain explicit. Unsupported SQLite clauses fail instead of being ignored. DTO mapping validates exact shape, type and nullability. No full LINQ translation, managed fallback or hidden client evaluation is introduced.

## Application server choice

Applications may implement one `SearchAsync(..., CancellationToken)` over a `DataSource` and call it from their ASP.NET Core endpoint or C# gRPC service. The caller maps cancellation and transport responses. NativeWeave supplies no server wrapper. Database installation/load closure contains only selected providers and required shared packages.

## Verification

Mixed reference and end-to-end tests retain unique database assertions: idempotent transactions, conflict/recovery, pagination, nullable/composite relations, outbox consistency and lost-COMMIT-ack oracles. Four real external-consumer cells prove PostgreSQL/SQLite JIT/AOT; package, publish and loaded-library inspection prove independence. This batch makes no performance claim.
