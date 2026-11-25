# Korda-Design

Design specifications and preserved research for [Korda](https://github.com/IzuSharp/Korda), with execution evidence in [Plan](https://github.com/IzuSharp/Plan). Korda provides independently installable strongly typed C# Native AOT libraries. This batch covers PostgreSQL and SQLite only.

DB-DotNet-01 selects Npgsql and Microsoft.Data.Sqlite execution while retaining the existing C# Fluent ORM, package identities and behavior. Migration and validation precede optimization. Dapper.AOT is the sole external performance comparison. This is an authorized design; product compatibility, performance and publication remain pending until actual evidence exists.

| Start here | Purpose |
| --- | --- |
| [Current phase](CURRENT-PHASE.md) and [working rules](AGENTS.md) | New task authority and preserved historical boundaries |
| [ADR-0008](docs/decisions/ADR-0008-database-dotnet-execution.md) | .NET execution decision |
| [Migration contract](docs/database/dotnet-migration.md) and [overlay](docs/database/dotnet-migration.json) | Implementation/compatibility/measurement obligations |
| [Database product](docs/database/current-product.md) and [Fluent contract](docs/database/fluent-orm.md) | Retained application behavior and new execution map |
| [API index](docs/api/README.md) and [Db attribute names](docs/database/db-attribute-names.md) | Public declarations and mapping conventions |
| [Getting started](docs/api/getting-started.md) and [NuGet consumption](docs/api/nuget-and-consumption.md) | Ordinary C# models and independent packages |
| [Verification matrix](docs/verification/models-and-matrix.md) | Required observed product and delivery gates |
| [API standard](docs/standards/csharp-public-api-and-documentation.md) | Compatibility, ownership, documentation and allocation obligations |
| [Repository identity](docs/repository-identity.md) | Canonical URLs and preserved historical names |

## Documentation verification

```sh
python3 tools/verify_db_dotnet.py
python3 tools/verify_db_dotnet.py --verify-frozen-history
python3 tools/verify_db_scope_history.py
```

Use full Git history. The current overlay is checked independently; the unchanged previous naming/Fluent/C++/scope gates run at their frozen sources. Historical research contracts, `docs/current-scope.json`, previous migration/naming/Fluent JSON, graphs, reviews and raw evidence retain their bytes. DB-Perf-01 stays cancelled; its results are not transferred into DB-DotNet-01. No documentation gate establishes actual database execution or completes a long segment.
