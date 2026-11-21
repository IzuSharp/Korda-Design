# Current database API — DB-Scope-01

The current API is the implemented PostgreSQL/SQLite database product. Its public signatures and XML documentation come from compiled product assemblies. The old 0.4.0 throwing declaration fixtures are [historical design evidence](../history/pre-db-scope-01/README.md), not the current SDK or product execution.

| Read | Authority |
| --- | --- |
| [Compiled reference index](reference.md) | Exact implemented C# signatures, defaults, nullability, constraints and XML policies |
| [Database behavior](database.md) and [implementation mapping](../database/current-product.md) | Ownership, provider behavior, Fluent/mapping and native execution |
| [Required interop](interop.md) | ABI/async/cancel/error/buffer/lifetime retained for database execution |
| [NuGet and consumption](nuget-and-consumption.md) | Twelve-package candidate closure and optional database DI |
| [Getting started](getting-started.md) and [guides](guides.md) | Ordinary application journeys and common business method reuse |
| [Documentation system](documentation-system.md) and [API standard](../standards/csharp-public-api-and-documentation.md) | Current reference/compatibility and evidence obligations |

The source-inspected baseline is product `ea5fa528035d025bd7a28698ee7c71194432236c`. Final pruned source and executed consumer identities are recorded in Plan's DB-Scope-01 acceptance. No new public database signature or ORM feature is introduced by this design pruning.

NativeWeave owns no current HTTP/gRPC/MCP server API. Applications choose their own server and call ordinary C# database business methods. Database Host is retained execution infrastructure. Linux x64 JIT/AOT verification is required; no other target is accepted by this batch.

## Frozen compatibility inputs

The non-Server JSON files retained at their original `docs/api/` paths, including `public-api.json`, are immutable pre-scope inputs used by existing database binding/API checks. They remain historical and do not define the current installable surface. Tests that pin old narrative/standard hashes must use a detached checkout of `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` via their existing `--design` or `--design-root` option. Current documents do not change those pins.
