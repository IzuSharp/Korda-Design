# Current Korda database product

The existing product is the PostgreSQL/SQLite Fluent ORM with C# application models, DTOs and static mappings over the C++20 database engine. libpq and sqlite3 perform provider execution. [DB-API-01 behavior](fluent-orm.md) remains in force; [DB-Rename-01](db-attribute-names.md) changes the ten public attributes to `Db` names while preserving behavior. Exact current commands and module selection come from [Korda AGENTS](https://github.com/IzuSharp/Korda/blob/main/AGENTS.md); actual source/test identities belong to Plan and the product PR.

The resumed [DB-Perf-01 query decision](query-semantics.md) proposes complete-query
submission and greater fixed-shape reuse while preserving this execution stack.
Its source-status table distinguishes current per-node composition, logical
`.Prepare()` reuse and unimplemented physical statement caching. Product delivery
requires code and actual tests; a Design change does not supply those results.

## Public-to-native map

| Public operation | C# implementation | Existing native execution |
| --- | --- | --- |
| Provider factory / DataSourceBuilder | `src/Data.Postgres`, `src/Data.Sqlite`, `src/Data.NativeHost` | `host.cpp`, `host_abi.cpp`, `provider.cpp` with provider-specific composition |
| OpenSessionAsync and pool/session limits | `src/Data.NativeHost` | Host admission, pool/session state and provider I/O |
| BeginTransactionAsync, commit/rollback/savepoints | `src/Data.Transactions` plus Host | Host transaction state and provider operations |
| Administration and migrations | `src/Data.Migrations` | `administration.cpp`, native schema and migration operations |
| Typed values and parameters | `src/Data.Abstractions`, `src/Data.Codecs`, `src/Query.Binding` | `contracts.cpp`, `scalar.cpp`, ordered parameter conversion |
| From / Where / ordering / query operators | `src/Query.Fluent`, `src/Query.Native` | `query.cpp`, native query/dialect state |
| Static models and immutable DTO projections | `src/Query.Generator`, `src/Data.Materialization` | Existing metadata/projection ABI and Host registration |
| Relations and CRUD | `src/Orm.Relations` | `mutations.cpp`, query composition and provider execution |
| AsAsyncEnumerable and terminals | `src/Data.Streaming`, `src/Query.Fluent` | Host cursors, provider fetches and bounded result ownership |
| Cancellation, errors and disposal | Required Core/Interop modules | `interop.cpp` and native database retirement |

Native filenames in the table are under `native/cpp/src`; their corresponding headers are under `native/cpp/include/nw`. The product [native build guide](https://github.com/IzuSharp/Korda/blob/task/DB-Rename-01-linux/docs/guides/cpp-native.md) records toolchain and implementation details. The Database assembly composes the existing query, ORM, migration and materialization sources. Database Host remains required execution infrastructure, not an HTTP server. Independent provider packages include `libnw_database_sqlite.so` or `libnw_database_postgresql.so` with their required managed closure.

The database model generator remains `Query.Generator`. Exact retained native prototypes come from `tests/Query.Binding/generate.py` and `native/database/binding/signatures-v1.json`. The rename changes neither those ABI signatures nor native execution ownership. JSON continues using existing source-generated metadata.

## Preserve behavior, including failure paths

Preserve immutable option snapshots, lazy source/pool creation, explicit connection/session acquisition and per-source budgets. Build negotiates the module and starts database-owned runtime state; it does not perform connection or migration I/O. Core introduces no default global native runtime.

Keep transaction outcome separate from cleanup: failed-transaction rollback, savepoints, pre-admission cancellation and unknown COMMIT outcomes retain their contracts. Unknown never permits automatic replay. Protocol-clean reuse is independent of local quiescence. Administrative/migration operations preserve provider-specific locks, connection cleanup and errors.

Maintain ordered parameter binding, scalar/NULL/UTF-8/numeric semantics, native dialect rendering and explicit capability errors. An unsupported SQLite clause must not disappear silently. Expert SQL remains explicit and parameterized, without fallback to managed execution. Preserve typed fields, immutable metadata, complete result shape, static DTO materialization and handwritten/generated parity. Ordinary C# entity/DTO edits reuse native bytes.

Retain primary-key CRUD, explicit relations, tenant/composite keys, optional foreign keys, changesets, upsert and version/affected-row semantics. The rename adds no tracking, lazy loading or graph persistence. Preserve stream budgets, early-break/disposal, canceled operations, callback retirement and source/session close. A timeout is not permission to force-free an owner. Keep structured provider errors and cleanup failures without logging secrets.

## Transport-independent business operations

A C# application owns its business query methods. Console, ASP.NET Core HTTP and ordinary C# gRPC entry points may call the same method with cancellation; database packages introduce no transport wrapper. Internal `Reference.TaskService` and `Verification.EndToEnd` paths preserve their direct database idempotency/replay, conflict lookup, pagination/recovery, optimistic CRUD/outbox, nullable/composite relation, same-session, early-cursor and lost-COMMIT-ack oracles. Their continued database assertions are not new server product scope.

## Current validation and historical boundaries

Follow the [current matrix](../verification/models-and-matrix.md): dependency-selected managed/native/API checks, two separately built candidate packages, and real SQLite/PostgreSQL reads/writes through external PackageReference Native AOT order consumers. Inspect package contents and loaded native paths/hashes; preserve failure attempts and review evidence. The current task adds local Linux performance comparisons and final 30-minute
candidate/Dapper.AOT segments for both providers. It adds no benchmark CI, JIT
consumer, clean-image, CPU-emulation or additional platform acceptance. Normal CI
retains the existing independent provider package runners; main publication remains
the repository's package-input decision. Plan records observed checks and delivery
states without predicting a future merge or release.

The earlier Rust/SeaQuery/SQLx source map, pruning commands and four JIT/AOT cells remain available at the [immutable DB-Scope-01 snapshot](https://github.com/IzuSharp/Korda-Design/blob/8298dc4128b745cf1809bad0c3cf02c45eb7f522/docs/database/current-product.md). They retain their original meaning and are not the current implementation map. Frozen `docs/current-scope.json`, C++ migration records and completed DB-API-01 evidence are not rewritten by this task.
