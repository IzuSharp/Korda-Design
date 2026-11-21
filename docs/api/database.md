# Database API behavior — DB-Scope-01

[The current product mapping](../database/current-product.md) describes the retained implementation. [The reference index](reference.md) links exact compiled declarations and XML semantics. These authorities replace the old declaration-only API catalog for current consumption.

## Sources, sessions and transactions

`DataSourceBuilder` selects `UseSqlite` or `UsePostgreSql`, snapshots finite options, negotiates the precompiled module and builds an independently owned source. Provider convenience factories use the same implementation. Build starts the database's engine-local runtime and creates a lazy pool; it does not perform connection or migration I/O. `OpenSessionAsync` acquires actual database access. Dispose source/session owners with their documented asynchronous lifetime.

Transactions preserve their explicit commit/rollback/savepoint behavior. Public completion, confirmed durable outcome and cleanup disposition remain distinct. A failed or canceled commit can retain an unknown outcome; never turn it into an automatic replay or a confirmed rollback. The physical connection is not reusable until its protocol/transaction state is clean.

## Queries, models and DTOs

`session.From(Table<TEntity>)` creates a typed Fluent query backed by native SeaQuery state. Existing filters, ordering, joins, aggregates, pagination, projections and terminals retain their source-defined capabilities. Arguments are typed and snapshotted as specified; values are parameters, not SQL text interpolation. SQLite-incompatible operations fail explicitly before dispatch.

Static `Table<TEntity>`, typed columns/codecs and `Projection<T>` or the existing query generator provide AOT-friendly metadata and DTO construction. Ordinary model/DTO edits rebuild managed code, not Rust. Exact result count/shape/aliases/codecs/nullability are checked; missing columns are not silently NULL. SQL three-valued logic remains SQL behavior; no complete LINQ provider or hidden managed/client evaluation is added.

## Relations, changes and administration

Retain `InsertAsync`, `FindAsync`, explicit changesets, concurrency/version checks, upsert and relational operations already implemented. Nullable/composite foreign keys and tenant/key predicates remain covered. No transparent tracking, lazy loading or new graph persistence is introduced.

`source.Administration.MigrateAsync` retains existing provider-specific migration and schema behavior. PostgreSQL administrative lock/session cleanup and SQLite atomic migration behavior remain real-provider obligations. Preserve original errors together with rollback/cleanup errors.

## Streaming and errors

`AsAsyncEnumerable` retains bounded cursor/result storage and explicit early-break/disposal. A terminal that buffers results still obeys its row/byte budgets. Cancellation requests do not free memory still used by native operations. `CloseAsync` can report pending cleanup; `DisposeAsync` follows actual retirement.

Preserve argument/disposal/cancellation exceptions, structured provider diagnostics, unsupported-capability errors and unknown transaction outcomes. Do not log secret connection strings or parameter values by default. Database consumers acquire no NativeWeave Server/protocol runtime.
