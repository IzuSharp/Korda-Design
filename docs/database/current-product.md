# Current Korda database product

The existing product is the PostgreSQL/SQLite Fluent ORM with C# application models, DTOs and static mappings over the C++20 database engine. libpq and sqlite3 perform provider execution. [DB-API-01 behavior](fluent-orm.md) remains in force; [DB-Rename-01](db-attribute-names.md) changes the ten public attributes to `Db` names while preserving behavior. Exact current commands and module selection come from [Korda AGENTS](https://github.com/IzuSharp/Korda/blob/main/AGENTS.md); actual source/test identities belong to Plan and the product PR.

The current [DB-Exec-02 target](query-semantics.md#current-execution-path-target-db-exec-02)
rebuilds the complete driver-to-Fluent execution path while retaining this product
surface. The cursor pull/scoped-span route is implemented in a published source candidate;
final integrated package and performance acceptance remain pending. The
[actual path record](cursor-pull-execution.md) binds its published checkpoint, eight
exports, tests and remaining costs.
Selected targets are ordered typed native arguments without a second NWDB
encode/parse, fresh PostgreSQL Parse/Describe in one pipeline group, one SQLite
statement for description/binding, direct native batch writing and one validated
managed row layout. Native-batch borrowing now uses one stable scoped owner and
generation-checked synchronous span leases. Opening remains
nonexecuting; PostgreSQL cross-execution statement/column caching is not selected.
The command representation has an explicit direct-compilation-versus-replay
decision gate before completion. Plan owns actual deletion and package evidence.

### Starting implementation retained for comparison

The preceding [DB-Perf-01 query decision](query-semantics.md) describes the
implementation candidate in [Korda #37](https://github.com/IzuSharp/Korda/pull/37)
and [Design #20](https://github.com/IzuSharp/Korda-Design/pull/20). It adds complete
NWQC composition, eager runtime `.Prepare()` compilation, bounded shared scalar
origins and internal shape-cache locking while preserving this execution stack.
Its audit table remains the earlier starting point. Physical statement caching and
generated fixed-query templates remain unimplemented. [Plan #34](https://github.com/IzuSharp/Plan/pull/34)
owns the candidate's local correctness evidence and outstanding performance work;
this checkpoint does not claim merge, release or final performance acceptance.

## Public-to-native map

This table identifies the assembled source candidate described in the
[actual path record](cursor-pull-execution.md). Development Native AOT tests
exercise the changed entry; final external provider-package consumers and
candidate receipts still determine delivery acceptance. The earlier f0078da7
map remains available in Git history.

| Public operation | C# implementation | Existing native execution |
| --- | --- | --- |
| Provider factory / DataSourceBuilder | `src/Data.Postgres`, `src/Data.Sqlite`, `src/Data.NativeHost` | `host.cpp`, `host_abi.cpp`, `provider.cpp` with provider-specific composition |
| OpenSessionAsync and pool/session limits | `src/Data.NativeHost` | Host admission, pool/session state and provider I/O |
| BeginTransactionAsync, commit/rollback/savepoints | `src/Data.Transactions` plus Host | Host transaction state and provider operations |
| Administration and migrations | `src/Data.Migrations` | `administration.cpp`, native schema and migration operations |
| Typed values and parameters | `src/Data.Abstractions`, `src/Data.Codecs`, `src/Query.Binding` | `contracts.cpp`, `scalar.cpp`, ordered parameter conversion |
| From / Where / ordering / query operators | `src/Query.Fluent`, `src/Query.Binding`, `src/Query.Native` | One bounded NWQC graph; direct operand compilation in `query.cpp`, retaining native query/dialect state without the superseded replay adapter |
| Static models and immutable DTO projections | `src/Query.Generator`, `src/Data.Materialization` | Existing metadata/projection ABI and Host registration |
| Relations and CRUD | `src/Orm.Relations` | `mutations.cpp` and shared capture helpers; lazy relation/returning-mutation channels, with generic nonreturning controls retained |
| AsAsyncEnumerable and typed terminals | `src/Data.Streaming`, `src/Query.Fluent`, `src/Data.NativeHost/HostPullController.cs` | Lazy `CursorPull`, first-request open plus admitted fetch, generation-checked ready/take, bounded arenas and scoped native span ownership |
| Cancellation, errors and disposal | Required Core/Interop modules | `interop.cpp` and native database retirement |

Native filenames in the table are under `native/cpp/src`; their corresponding headers are under `native/cpp/include/nw`. The product [native build guide](https://github.com/IzuSharp/Korda/blob/task/DB-Rename-01-linux/docs/guides/cpp-native.md) records toolchain and implementation details. The Database assembly composes the existing query, ORM, migration and materialization sources. Database Host remains required execution infrastructure, not an HTTP server. Independent provider packages include `libnw_database_sqlite.so` or `libnw_database_postgresql.so` with their required managed closure.

The database model generator remains `Query.Generator`. Exact retained native prototypes come from `tests/Query.Binding/generate.py` and `native/database/binding/signatures-v1.json`. The rename changes neither those ABI signatures nor native execution ownership. JSON continues using existing source-generated metadata.

The query candidate adds capability bit 26 (`db.query.command.v1`) and three
separately negotiated compile/render/CTE declarations in
`native/database/binding/korda_query_command_v1.h` and `query-command-v1.json`.
Those additions preserve the frozen v1 signatures and fingerprint. The
[query decision](query-semantics.md#dynamic-queries-one-complete-command) explains
the typed owner sidecar, topology and preserved budgets; command bytes contain
no native pointer values. The current candidate also requires capability bit 27
(`db.cursor.pull.v1`) and all eight declarations in
`native/database/binding/korda_cursor_pull_v1.h` / `cursor-pull-v1.json`.
They replace the unpublished batch-result extension. Frozen cursor operations
and take-buffer remain compatible; they are exercised through test-local
fixtures rather than an unused production streaming fallback.

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
