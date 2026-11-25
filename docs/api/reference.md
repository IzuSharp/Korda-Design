# Current compiled API reference index

Exact declarations and XML are generated and checked in Korda. These links freeze the pre-migration main declarations at e063f2eb6e2e857e3f19f96bf263cae372651a27 as compatibility inputs. DB-DotNet-01 must regenerate current references from the actual migrated compiled assemblies and preserve their public signatures; the old internal file paths do not mandate retaining native execution. The current attribute surface is the ten `Db*Attribute` types in `Korda.Data`; [the naming contract](../database/db-attribute-names.md) explains compatibility and the preserved behavior.

| Public area | Generated product reference |
| --- | --- |
| Data source/session and common Database | [src/Data.NativeHost/reference/database.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Data.NativeHost/reference/database.md) |
| SQLite facade | [src/Data.NativeHost/reference/sqlite.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Data.NativeHost/reference/sqlite.md) |
| PostgreSQL facade | [src/Data.NativeHost/reference/postgresql.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Data.NativeHost/reference/postgresql.md) |
| Optional database DI | [src/Data.NativeHost/reference/dependency-injection.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Data.NativeHost/reference/dependency-injection.md) |
| Fluent query | [src/Query.Fluent/api-reference.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Query.Fluent/api-reference.md) |
| Static data/codecs/models | [src/Data.Abstractions/api-reference.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Data.Abstractions/api-reference.md) |
| Streaming | [src/Data.Streaming/api-reference.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Data.Streaming/api-reference.md) |
| Transactions | [src/Data.Transactions/api-reference.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Data.Transactions/api-reference.md) |
| Migrations | [src/Data.Migrations/reference/database.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Data.Migrations/reference/database.md) |
| Relations/CRUD | [src/Orm.Relations/reference/database.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Orm.Relations/reference/database.md) |
| Model/query generator | [src/Query.Generator/api-reference.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Query.Generator/api-reference.md) |
| Query binding | [src/Query.Binding/api-reference.md](https://github.com/IzuSharp/Korda/blob/e063f2eb6e2e857e3f19f96bf263cae372651a27/src/Query.Binding/api-reference.md) |

Generated references must be regenerated from compiled source/XML, not edited into agreement by hand. API baselines, Roslyn matching, diagnostics and reverse scaffolding use the same current names. Full examples live beside the implementation and are tested with actual candidate packages.

The earlier pre-pruning reference remains an [immutable historical snapshot](https://github.com/IzuSharp/NativeWeave/tree/ea5fa528035d025bd7a28698ee7c71194432236c). Its old names and URLs identify historical evidence; they are not current copyable API instructions. Current Design preserves the frozen compatibility JSON and acceptance hashes.
