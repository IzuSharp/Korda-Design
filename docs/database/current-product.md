# Current Korda database design — DB-DotNet-01

Korda's selected database design is a strongly typed C# Fluent ORM over Npgsql for PostgreSQL and Microsoft.Data.Sqlite for SQLite. [ADR-0008](../decisions/ADR-0008-database-dotnet-execution.md) changes the execution architecture while [the Fluent contract](fluent-orm.md) and [Db naming contract](db-attribute-names.md) retain application behavior. Migration implementation and compatibility are pending until [Plan](https://github.com/IzuSharp/Plan/tree/DB-DotNet-01/ledger/evidence/batches/DB-DotNet-01) records actual results; this design does not announce released .NET-backed packages.

## Execution map

| Public area | Selected implementation |
| --- | --- |
| DataSourceBuilder/provider factories | Existing C# facade/options, lazy driver-backed data source |
| OpenSessionAsync | Driver connection plus bounded source admission and one-command session rules |
| Fluent/parameters | Typed C# query construction, provider SQL and ordered driver parameters |
| Models/DTOs | Existing `Db*` metadata and generated typed reader mapping |
| Relations/CRUD | Existing composite keys, nullable relations, changesets/version checks and bounded batch semantics in .NET |
| Transactions | Driver transactions/savepoints with retained explicit outcome and cleanup |
| Migrations/drafts/scaffolding | Managed provider SQL/catalog operations and unchanged persisted history/checksums |
| Streams/errors/disposal | Bounded reader ownership, real cancellation, truthful failures and safe connection return |

The [migration contract](dotnet-migration.md) defines detailed compatibility, source removal, lifecycle and acceptance. Korda-owned database C++, C ABI/P/Invoke, native Host, wire transport and exclusive build/test assets are removed by this migration after business assertions are ported. SQLite's standard driver-supplied native engine is a normal NuGet dependency.

Preserve public package identities `Korda.Database.PostgreSql` and `Korda.Database.Sqlite`, all existing C# entry points and independently usable consumption. Entity/DTO changes require only a C# rebuild. Dapper is benchmark-only. The first compatible .NET version is frozen before optimization; the sole external performance comparison is Dapper.AOT.

Applications own their C# business query methods and optional ASP.NET Core/gRPC hosting. Database packages introduce no transport/server product. Historical native/Rust source maps, research and acceptance remain at their fixed commits and do not accept current implementation bytes.
