# ADR-0008 — .NET database execution with retained C# behavior

Status: owner-authorized decision for DB-DotNet-01; product implementation and acceptance pending. Date: 2026-11-25. Plan-first input: [Plan 0ad57ad](https://github.com/IzuSharp/Plan/blob/0ad57adddd2ace06621ef8d263a7e444a8f25bcd/ledger/evidence/batches/DB-DotNet-01/plan.md).

## Context

Korda supplies independently installable strong-typed C# Native AOT database libraries. The current source baseline uses C++20/libpq/sqlite3 below the C# Fluent ORM. The owner now requires retaining business source, public API and observable behavior while removing Korda's own database cross-language execution layer. PostgreSQL and SQLite are the only products in this task.

## Decision

Use Npgsql for PostgreSQL and Microsoft.Data.Sqlite for SQLite. C# implements existing typed query composition and provider SQL rendering, binds parameters, orchestrates connection/transaction lifetime and materializes reader values through source-generated mappings. Reuse driver capabilities directly. Dapper is restricted to the Dapper.AOT benchmark applications. SQLite's native engine is supplied by the driver's standard NuGet dependency, not a Korda native build.

Preserve `Korda.Database.PostgreSql`, `Korda.Database.Sqlite`, their C# public declarations, the `Db*` attribute surface and retained behavior in [the Fluent contract](../database/fluent-orm.md). Delete Korda-owned database C++, C ABI/P/Invoke, native Host, wire transport and exclusive build/test/package infrastructure after translating still-relevant tests into behavior tests. ABI compatibility with the removed execution layer is no longer an acceptance obligation; upper-level compatibility and persisted database identities are.

Migrate and verify first. Freeze the first usable .NET implementation as the internal optimization baseline only after both provider compatibility lanes pass. Optimize measured hotspots while preserving semantics and bounded resources. Dapper.AOT is the only external performance comparator. The final campaign is exactly four required route/database cells, each at least 1,800 continuous effective mixed-load seconds in one admitted dedicated resource set; ordinary PR CI retains correctness, short regressions and AOT package consumption.

## Consequences

Existing business code and data need actual differential validation. Driver defaults, cancellation, parameter types, decimal/JSON/NULL, pooling, session concurrency, streaming disposal and unknown COMMIT outcomes are not assumed compatible. Published Microsoft.Data.Sqlite 11.0.0 has a no-op command Cancel and synchronous async execution; execution-time cancellation needs a compatible managed solution and real proof. Unresolved differences stay explicit and cannot be relabeled as passed.

The allocation target is 0 B of extra library-owned managed allocation on named steady-state common paths. Required lists, DTOs and strings are business result allocation even when created in the library. Report total allocation, attributable Korda overhead, business results and unclassified driver/runtime/tool costs using raw counters. No document or successful compile establishes zero allocation or performance superiority.

This decision supersedes ADR-0006's implementation-language requirement for the new database batch. ADR-0006, previous Fluent/naming JSON, all frozen contracts, research and measurements retain their original bytes and identities. New [migration contract](../database/dotnet-migration.md), [overlay](../database/dotnet-migration.json) and Plan batch govern new evidence. Normal merge and automatic-publication follow-through are explicitly authorized, subject to actual required checks and review.
