# DB-Scope-01 requirements charter

Authority: the owner's 2026-11-21 instruction and [Plan PR24](https://github.com/IzuSharp/Plan/pull/24). This supersedes the general framework/Server charter for current work. The original remains at frozen Design commit `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.

## Product goal

Developers use a natural, strongly typed Fluent ORM in a normal C# application to operate PostgreSQL or SQLite. Native AOT is supported. Rust SeaQuery builds queries and dialects; SQLx executes database work. C# owns entities, DTOs, static mappings, business logic and public API composition. Ordinary model/DTO additions reuse precompiled native assets.

The application chooses its server. Standard ASP.NET Core HTTP and standard C# gRPC entry points may call the same C# query method. This is ordinary method reuse and introduces no NativeWeave transport abstraction, handler framework, server package or protocol runtime.

## Required retained behavior

| Requirement | Boundary |
| --- | --- |
| Both providers | Preserve PostgreSQL and SQLite implementations and real-provider tests |
| Database Host | Preserve database execution, engine-local runtime, pooling, sessions, admission and retirement |
| Transactions and migrations | Preserve commit/rollback/savepoint, administrative lifetime and durable-outcome semantics |
| Typed queries and mapping | Preserve parameters, Fluent operators, static metadata, generated or handwritten mapping, DTOs and AOT |
| ORM | Preserve existing relations, CRUD, version checks and explicit concurrency outcomes |
| Streaming | Preserve bounded results, cancellation, early disposal and session reuse rules |
| Core dependencies | Retain binding, ABI negotiation, callbacks, errors, buffers and lifetime machinery needed by the database |
| Packages | Ordinary PackageReference uses precompiled assets and no consumer Cargo invocation |
| Evidence | Run PostgreSQL and SQLite as JIT and AOT consumers outside the source tree; inspect packages, publish files and loaded libraries |

## Removed scope

NativeWeave's HTTP/gRPC servers, protocol bindings, route/handler framework, MCP, independent compression/proof engines, HelloWorld packages and exclusive examples are removed. Shared components are retained according to actual database dependency. Mixed server/database tests retain unique database checks as direct business-method consumers.

No new ORM feature, complete LINQ provider, managed SQL engine, new HTTP/gRPC wrapper, performance optimization, 30-minute load campaign or platform expansion is authorized. Linux x64 is the sole target. Public database release is not required; candidate creation and consumption are required.

## Delivery and history

Plan precedes Design; Design precedes code; actual regressions and independent review precede normal merges. Required checks, licenses and protection remain. Historical evidence and failed attempts retain their identities. Acceptance belongs to Plan's DB-Scope-01 record, not an old accepted contract or a document check. Stop when the pruned scope, real consumers, normal merges and merged-main CI are verified.
