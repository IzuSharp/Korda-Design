# ADR-0005 — PostgreSQL and SQLite database product scope

Status: owner-directed scope decision for DB-Scope-01; implementation acceptance is separate in Plan. Date: 2026-11-21.

## Context

The project had implemented database, HTTP Server, gRPC/MCP and proof/demo engines, while current Design still described research-only work. The owner terminated Perf-01 and defined one product: strongly typed Fluent ORM in ordinary C#, using Rust SeaQuery and SQLx for PostgreSQL/SQLite, with Native AOT and precompiled assets.

[Plan PR24](https://github.com/IzuSharp/Plan/pull/24), initial head `b56ef7a6d4fc8c38cf8da04d555f30bae4e0693a`, preceded this Design pruning. Fresh inputs: Design `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`, product `ea5fa528035d025bd7a28698ee7c71194432236c`, Plan `8afa0311f45ab8a8157fc45c51e95a0b17dd09f2`.

## Decision

Preserve the complete existing database product and its actual interop dependencies. Database Host remains responsible for database execution. Preserve pools, sessions, transactions, migrations, parameters, typed Fluent operations, static models/DTOs, relationships, CRUD, streams, cancellation, errors, disposal and AOT packaging.

Remove NativeWeave-owned HTTP/gRPC/MCP server/protocol bindings, routing/wrappers, independent compression/proof engines and HelloWorld. Applications choose their server. Standard HTTP endpoints and C# gRPC methods can call the same C# query method; no transport wrapper is created.

The database candidate closure has twelve package IDs, with optional DI documented separately. Provider installations must not pull Server/protocol/proof/demo packages or libraries. Consumer builds never invoke Rust tools.

## Consequences

Current requirements, API/package docs, default build/test/pack/release paths and CI reflect the reduced scope. Mixed verification retains unique database assertions. Removing failing retained checks, suppressing security checks, changing protections or inventing results is not permitted.

Linux x64 is the only batch target. Both databases require actual retained regressions and external PackageReference JIT/AOT consumers. Dependency graphs, publish layout and actual native mappings demonstrate independence. Candidate production is required; unrequested public database publication is not.

Historical registry/index/reviews/evidence retain exact identity and run unchanged gates at the frozen pre-scope Design commit. Superseded API/Server bytes are archived without relabeling acceptance. Current scope checks/review remain separate from historical bindings and product acceptance.

No ORM feature, performance tuning, 30-minute load campaign or next task belongs here. Stop after regression, review, normal protected merges and merged-main CI verification.
