# Database guides — DB-Scope-01

Current guides cover existing product behavior. Exact declarations and XML remain in [compiled product references](reference.md), and actual task evidence remains in Plan.

| Topic | Guide and invariant |
| --- | --- |
| Installation | [NuGet](nuget-and-consumption.md): select a provider, use precompiled assets, no consumer Rust or NativeWeave Server |
| First application | [Getting started](getting-started.md): ordinary C# source/session and typed query |
| Data source and pool | [Database product](../database/current-product.md): explicit owner, finite admission and clean reuse |
| Transactions | [Database behavior](database.md): outcome and cleanup are separate; unknown COMMIT does not authorize replay |
| Migrations | Existing administrative API preserves dedicated lifetime, checksum/ledger behavior and both providers |
| Fluent and DTOs | Native SeaQuery query state, parameters, static metadata and exact result shape; no full LINQ or reflection fallback |
| Relations and CRUD | Existing explicit relation/key/version semantics, nullable/composite keys and concurrency outcomes |
| Async and streaming | [Required interop](interop.md): bounded results, early disposal, cancellation and actual retirement |
| Native AOT | [Platforms](../platforms/support-and-aot.md): actual Linux x64 publish and execution for both databases |
| Errors and resources | Preserve structured provider errors, original/cleanup failures, ownership and use-after-close behavior |
| Verification | [Acceptance matrix](../verification/models-and-matrix.md): regressions, four external cells and package/load closure |
| Versions and packaging | [Build/release](../platforms/build-package-release.md): exact source/ABI/package identities and candidate-only boundary |

## Application transport integration

Standard HTTP and gRPC entry points call the same ordinary C# business query method. The application selects its server and transport dependencies. Database operations receive the caller's cancellation token and return typed DTOs; transport response mapping stays in the application. NativeWeave supplies no server, routing, protocol or transport wrapper.

## Scope of troubleshooting

Diagnose unsupported provider capability, incompatible native identity, model/DTO shape, canceled/unknown transaction outcome, and pending resource retirement through the existing typed errors/reference contracts. Do not conceal failures with managed providers, SQL interpolation, client evaluation, ignored unsupported clauses or forced release.

Performance optimization, long-load campaigns and new ORM behavior are deferred beyond DB-Scope-01. Original research studies remain available in [history](../history/pre-db-scope-01/README.md); their finite results are not current acceptance.
