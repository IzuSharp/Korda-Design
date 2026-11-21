# Implemented API reference index — DB-Scope-01

Exact signatures and XML are generated and checked in the product repository. These links pin the inspected pre-pruning main `ea5fa528035d025bd7a28698ee7c71194432236c`; final candidate source and reference verification are recorded in Plan. They are source evidence, not a claim of new execution.

| Public area | Compiled product reference |
| --- | --- |
| Data source/session and common Database | [src/Data.NativeHost/reference/database.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Data.NativeHost/reference/database.md) |
| SQLite facade | [src/Data.NativeHost/reference/sqlite.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Data.NativeHost/reference/sqlite.md) |
| PostgreSQL facade | [src/Data.NativeHost/reference/postgresql.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Data.NativeHost/reference/postgresql.md) |
| Optional database DI | [src/Data.NativeHost/reference/dependency-injection.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Data.NativeHost/reference/dependency-injection.md) |
| Fluent query | [src/Query.Fluent/api-reference.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Query.Fluent/api-reference.md) |
| Static data/codecs/models | [src/Data.Abstractions/api-reference.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Data.Abstractions/api-reference.md) |
| Streaming | [src/Data.Streaming/api-reference.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Data.Streaming/api-reference.md) |
| Transactions | [src/Data.Transactions/api-reference.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Data.Transactions/api-reference.md) |
| Migrations | [src/Data.Migrations/reference/database.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Data.Migrations/reference/database.md) |
| Relations/CRUD | [src/Orm.Relations/reference/database.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Orm.Relations/reference/database.md) |
| Model/query generator | [src/Query.Generator/api-reference.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Query.Generator/api-reference.md) |
| Query binding | [src/Query.Binding/api-reference.md](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Query.Binding/api-reference.md) |

The database surface is retained, with API compatibility checks rerun against the candidate. Removed NativeWeave Server/protocol/proof/demo APIs are outside the current reference. The former complete design-only inventory is preserved in [history](../history/pre-db-scope-01/README.md); its throwing declarations are not current implementation.

Every native-facing reference must retain lifetime, ownership, async/cancellation, errors, concurrency, capability, platform and cost explanations. See [the documentation system](documentation-system.md) and [database behavior](database.md).
