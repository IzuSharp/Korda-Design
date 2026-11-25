# DB-DotNet-01 execution migration contract

The [decision](../decisions/ADR-0008-database-dotnet-execution.md) and [machine-readable overlay](dotnet-migration.json) define the selected .NET execution design. This contract is prospective until product receipts in [Plan](https://github.com/IzuSharp/Plan/tree/DB-DotNet-01/ledger/evidence/batches/DB-DotNet-01) establish implementation and acceptance. Preserve the [Fluent behavior](fluent-orm.md), [Db attribute names](db-attribute-names.md) and exact compiled public C# signatures from the starting product.

## Public-to-driver boundary

| Responsibility | .NET execution requirement |
| --- | --- |
| Provider creation and source options | Existing facade, immutable snapshots and lazy I/O; select Npgsql or Microsoft.Data.Sqlite |
| Connection/session admission | Driver connection pool plus bounded Korda admission where existing contracts require it; one active user operation per session |
| Fluent query, projection and capability checking | Typed managed descriptors/expressions; provider SQL rendering and ordered typed parameter binding; unsupported operations fail explicitly |
| Entity/DTO reading | Generated typed accessors over the .NET data reader, exact shape/nullability/codec checks; no unbounded reflection or object-array fallback |
| Relations and mutations | Existing key/tenant/version/NULL/omission semantics; batch relations retain input groups, duplicates and one-query/nonempty behavior |
| Transactions | Driver transactions/savepoints coordinated with retained outcome/cleanup state; no replay of an unknown commit |
| Migrations and schema workflows | Managed provider SQL/catalog operations, stable persisted checksums/history, reviewable draft and explicit destructive selections |
| Streaming and disposal | Bounded reader/connection ownership until enumeration and cleanup finish; early break/cancel/mapping errors release safely |
| Packages | Same top-level IDs and public managed API; standard driver dependency closure; generator installed by ordinary PackageReference |

The mapping is `public C# operation -> managed typed composition/admission -> driver command/reader/transaction -> generated DTO mapping`. There is no Korda-owned database native Host, ABI, P/Invoke or cross-language value format on this route. Standard driver/native-runtime internals remain their dependencies; SQLite's engine still executes in-process.

## Exact compatibility and data continuity

Freeze published package archives, APIs, XML, package assets and ordinary source-tree-external business consumers before migration. Run the same C# source with only PackageReference versions changed. Cover every public entry touched by source/generator/project-reference changes; inspect actual packed assemblies, not only loose build outputs. Preserve nullable/default parameter signatures, overload resolution, exceptions, result shape, lazy I/O, ownership and thread/concurrency behavior.

Use databases created by the original packages: PostgreSQL schema and SQLite file, existing rows/indexes and migration ledger/checksums. Read, write and migrate them with the new packages. Recreating an empty store cannot prove continuity. Preserve original physical names and persisted identifiers. Ordinary entity/DTO changes rebuild C# only.

Keep explicit JSON `JsonTypeInfo<T>` serialization and exact numeric/null policy. Do not enable Npgsql dynamic JSON/reflection to avoid implementing source-generated mapping. Map PostgreSQL JSON parameters as json/jsonb rather than accidental text; preserve checked integer narrowing, UUID/date/time encoding and SQLite fixed-scale money. SQLite-incompatible clauses never disappear silently. Expert SQL stays parameterized and its result is mapped under the same shape/codec rules.

## Cancellation, cleanup and transaction outcomes

Before-call token checks cover only pre-admission cancellation. Test cancellation after server/SQLite execution has started, including blocked commands and reader stepping, and then verify reader disposal, locks, connection return and next-use isolation. For SQLite 11.0.0, command Cancel is a no-op and async driver methods execute synchronously. Driver busy handling retries at command-timeout/150 ms boundaries; setting a raw SQLite busy timeout alone does not establish the existing millisecond contract. Source pin and research are in [Plan's driver review](https://github.com/IzuSharp/Plan/blob/DB-DotNet-01/ledger/evidence/batches/DB-DotNet-01/driver-source-review.md). Do not attribute newer upstream main code to a released package.

A managed compatibility adapter may use documented driver and standard dependency capabilities, but may not introduce another Korda-owned native execution layer. It must retain the active connection and operation until cancellation callbacks are unregistered/joined and driver work has stopped; late cancellation must not affect a subsequent lease. If a driver cannot support a retained contract, first investigate a .NET solution, then record the remaining difference and its acceptance impact honestly.

`CloseAsync` and `DisposeAsync` preserve their existing distinction. Timeout/abandoned await is not proof of cleanup. Rollback, failed transaction, savepoint, cleanup failure and connection discard/reuse have separate observed states. A PostgreSQL COMMIT whose acknowledgment is lost may be durable: retain Unknown, no automatic replay, and any recovery key. Prove this against independently observed persisted server state. Cleanup success never overwrites Unknown.

## Native removal and behavior coverage

Inventory old native tests before deleting sources/tools. Port SQL/value behavior, capability errors, parameter ordering, transaction/migration state, cancellation, bounded admission, stream cleanup and concurrency assertions to actual managed-provider behavior tests. Mark C ABI layout, native handle registry and removed wire corruption tests as obsolete only when their entire implementation boundary is gone. Keep equivalent result-shape/bounds/ownership safety tests where business relevance remains.

Remove orphan CMake, build scripts, native manifests, P/Invoke, exclusive test fixtures, package targets/assets and live docs after checking module dependencies. Register replacement source/test roots, checks and package outputs. Product AGENTS requires committed-diff impact selection and independent provider package runners. Do not disable a failing behavioral gate or run unrelated platforms to replace missing Linux evidence.

## Performance after compatibility

The first compatible .NET packages form an immutable internal baseline. Compare short interleaved baseline/candidate processes on at least 24 real business cases per provider, with a separately visible 100-DTO list. Korda uses official Fluent and generated mapping; Dapper.AOT must demonstrate active generated parameter binding/row mapping for every measured call site. Both routes are actually published Native AOT executables using identical drivers, engines, data/indexes, settings and output contracts. Dynamic composition and reusable query modes are separate.

The general design target is zero additional library-owned managed bytes per operation on steady-state common paths. Required business results count as results regardless of allocator. Report end-to-end bytes, attributable Korda bytes, business-result bytes and unresolved driver/runtime/tool bytes with original integer counters and whole-process Gen 0/1/2. Named 0 B claims require raw counts and attribution; runtime or object pooling is not an excuse for unbounded retained memory.

Record success throughput and rows, p50/p95/p99, errors/rejections/retries, client CPU/success, steady/peak RSS and post-drain retention, B/op and B/row. Fixed-arrival latency includes scheduling queue time; sustainable throughput is measured under common tail/error constraints. PostgreSQL server resources are separate; SQLite is in-process. Keep actual SQL/plan differences and use an additional same-SQL diagnostic to explain them.

Freeze final candidates before four sequential dedicated 30-minute effective mixed-load cells. Warmup/calibration/drain are extra; interrupted short runs do not add up to a long run. Keep exact source/packages/executables/dependencies, dataset/workload/environment and raw ledgers. Stop optimization at repeated noise or semantic compromise, retaining only reproducible bounded improvements. Normal merge, main CI, automatic previews and downloaded public NuGet consumption remain distinct final gates owned by Plan.
