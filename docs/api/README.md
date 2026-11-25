# Current Korda database API

Korda provides the PostgreSQL/SQLite Fluent ORM. Public packages and namespaces use `Korda.<Domain>`; database attributes use `Db`. [DB-Rename-01](../database/db-attribute-names.md) records the complete rename and its source/binary compatibility boundary. The accepted DB-API-01 behavior remains in the [Fluent ORM contract](../database/fluent-orm.md).

| Read | Authority |
| --- | --- |
| [.NET execution migration](../database/dotnet-migration.md) | Driver boundary, compatibility, measurement and delivery obligations |
| [Compiled reference index](reference.md) | Actual public declarations, defaults, nullability and XML policies |
| [Database behavior](database.md) and [Fluent ORM contract](../database/fluent-orm.md) | Queries, models, immutable DTOs, codecs, transactions and schema workflows |
| [NuGet and consumption](nuget-and-consumption.md) | Independent `Korda.Database.Sqlite` and `Korda.Database.PostgreSql` packages |
| [Getting started](getting-started.md) and [guides](guides.md) | Current copyable models and full product examples |
| [Documentation system](documentation-system.md) and [API standard](../standards/csharp-public-api-and-documentation.md) | Generated references, naming and exact compatibility obligations |

DB-DotNet-01 changes execution to .NET drivers under [the migration contract](../database/dotnet-migration.md). Plan records actual implementation, compatibility, measurements and delivery; all are pending until observed. Normal merges, automatic preview and public-package verification are authorized.

## Frozen compatibility inputs

The non-Server JSON files retained at their original `docs/api/` paths, including `public-api.json`, are immutable pre-scope inputs used by existing binding/API checks. They describe historical declarations and do not define the current installable surface. Tests retain their pinned detached checkout of `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. The prior DB-API-01 `fluent-orm.json` retains its accepted source/hash; the new naming overlay explicitly translates only the ten managed attribute identities. Historical source evidence is not new execution evidence.
