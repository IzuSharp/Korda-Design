# Current phase — DB-Scope-01

The owner narrowed NativeWeave to a PostgreSQL/SQLite strongly typed Fluent ORM on 2026-11-21. C# owns application logic, static models, DTOs and the Fluent API. Rust SeaQuery and SQLx own query construction, dialects and database execution. Ordinary applications use precompiled native assets with normal PackageReference, JIT and Native AOT.

The owner terminated Perf-01 and authorized this sequence: close its old PRs, clean only old task workspaces, publish the new Plan PR, prune current Design, prune product code, run Linux x64 database and external-consumer regressions, review, merge and verify main CI. [Plan PR24](https://github.com/IzuSharp/Plan/pull/24) is the Plan-first checkpoint. Implementation changes start only after the Design pruning checkpoint is recorded.

The application chooses its server. ASP.NET Core HTTP endpoints and standard C# gRPC methods can call the same C# business query method. Installing database packages must not install NativeWeave Server, gRPC, MCP, compression/proof or demo packages. Database Host remains part of database execution.

Current authority is [the scope manifest](docs/current-scope.json), [ADR-0005](docs/decisions/ADR-0005-database-product-scope.md) and [current API documentation](docs/api/README.md). Plan's `delivery-graph.json.current_execution` and `ledger/evidence/batches/DB-Scope-01/acceptance.json` own execution and acceptance. Design documents do not announce a release or claim tests have run.

## Historical records

The pre-scope Design main is `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`; product main is `ea5fa528035d025bd7a28698ee7c71194432236c`; Plan main is `8afa0311f45ab8a8157fc45c51e95a0b17dd09f2`. Old 21-contract acceptance, reviews, experiments and 34R/32D/48-delivery records remain historical. Their Server/extension scope and research-only authorization do not govern this batch. Exact prior gates run unchanged at their original snapshot; historical source or execution is never relabeled as current acceptance.

The [history entry](docs/history/pre-db-scope-01/README.md) explains archived API/Server specifications and original evidence paths. Performance work, new features, broader platforms and public database publication are outside this batch. Stop after pruning, actual regressions, normal merges and merged-main CI verification.
