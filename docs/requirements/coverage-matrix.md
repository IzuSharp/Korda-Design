# DB-Scope-01 coverage and preservation matrix

This current scope map records inspected implementation ownership and required regressions; it does not mark tests passed. Actual execution is in the [Plan acceptance record](https://github.com/IzuSharp/Plan/blob/task/DB-Scope-01-linux/ledger/evidence/batches/DB-Scope-01/acceptance.json).

| Capability | C# product source | Rust product source | Required evidence |
| --- | --- | --- | --- |
| Source, pool, session | `src/Data.NativeHost`, `src/Data.Postgres`, `src/Data.Sqlite` | `native/database/host`, `postgres`, `sqlite` | Connections, admission, reuse, release and both providers |
| Transactions | `src/Data.Transactions` and Host | `native/database/transactions` | Commit, rollback, savepoints, cancellation, failed transactions, unknown durable effect |
| Migrations | `src/Data.Migrations` | `native/database/migrations` | Schema/ledger, checksum failures, cleanup and rollback |
| Parameters and values | `src/Data.Abstractions`, `Data.Codecs`, `Query.Binding` | `native/database/codecs`, `binding` | Ordered parameters, NULL/type mapping, invalid values and ownership |
| Fluent query | `src/Query.Fluent`, `Query.Native` | `native/database/query` | SeaQuery SQL/value behavior, capabilities and typed negative cases |
| Static model and DTO | `src/Query.Generator`, `src/Data.Materialization` | Existing metadata/query host operations | Static mapping, model/DTO edits, database generator diagnostics and AOT |
| Relations and CRUD | `src/Orm.Relations` | `native/database/relations` | Nullable/composite relations, tenant keys, version checks and affected rows |
| Result streams | `src/Data.Streaming` | `native/database/streaming` and Host | Bounded batches, early stop, cancellation and retirement |
| Interop | `src/NativeWeave.Core`, required `Interop.*`, database signature generator `tests/Query.Binding/generate.py` | Required `native/interop` crates and `native/database/binding/signatures-v1.json` | ABI, database signature generation, ownership, async/callback/error/buffer regression |
| NuGet/AOT | Retained packaging/build/compatibility tools | Precompiled provider libraries | Four external PackageReference executions and dependency/load closure |

## Explicit exclusions

| Removed product | Required reconciliation |
| --- | --- |
| NativeWeave HTTP Server and routing | Remove server facade/native host/handler generator, tests and examples |
| NativeWeave gRPC and MCP | Remove native/managed protocol adapters and package edges |
| Compression and proof engines | Remove SyncProof/AsyncProof/ExtensionProof components and exclusive consumers |
| HelloWorld | Remove managed/native packages, examples and automatic demo publication target |
| Old Perf-01 | Close old PRs unmerged; import no candidate code, binary or measurements |

Database Host remains mandatory. Host, Core, Streaming and Generator names are not deletion criteria. Packaging contains only the [database closure](../api/nuget-and-consumption.md); historical research and the old exact API inventory are separated in [history](../history/pre-db-scope-01/README.md).
