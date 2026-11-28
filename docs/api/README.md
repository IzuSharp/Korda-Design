# Current Korda database API

Korda provides the PostgreSQL/SQLite Fluent ORM. Public packages and namespaces use `Korda.<Domain>`; database attributes use `Db`. [DB-Rename-01](../database/db-attribute-names.md) records the complete rename and its source/binary compatibility boundary. The accepted DB-API-01 behavior remains in the [Fluent ORM contract](../database/fluent-orm.md).

| Read | Authority |
| --- | --- |
| [Compiled reference index](reference.md) | Actual public declarations, defaults, nullability and XML policies |
| [Database behavior](database.md) and [Fluent ORM contract](../database/fluent-orm.md) | Queries, models, immutable DTOs, codecs, transactions and schema workflows |
| [NuGet and consumption](nuget-and-consumption.md) | Independent `Korda.Database.Sqlite` and `Korda.Database.PostgreSql` packages |
| [Getting started](getting-started.md) and [guides](guides.md) | Current copyable models and full product examples |
| [Documentation system](documentation-system.md) and [API standard](../standards/csharp-public-api-and-documentation.md) | Generated references, naming and exact compatibility obligations |

Current source, execution and delivery conclusions belong to Korda and Plan.

## Historical design catalogs

The retained coverage matrices and declaration catalog describe earlier design
proposals. They preserve feature mappings, signatures and semantic policies, not
the current installable surface. Use the compiled reference above for current APIs.
CI validates the current catalog structure and schema without replaying historical
commits or claiming product acceptance.
