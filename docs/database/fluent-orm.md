# Fluent ORM experience contract — DB-API-01

This is the behavior contract for the existing Korda PostgreSQL/SQLite product. [DB-Rename-01](db-attribute-names.md) supplies the current attribute spellings and the explicitly breaking managed-name change; all behavior below is retained. The completed DB-API-01 implementation evidence remains bound to its original names and source. DB-Rename-01 execution is recorded separately in Plan. [ADR-0007](../decisions/ADR-0007-fluent-orm-experience.md) records authority; [fluent-orm.json](fluent-orm.json) maps each behavior to owners and acceptance claims. Exact final public declarations and XML come from compiled Korda assemblies.

## Execution-path refactor contract — DB-Exec-02

The [current target](query-semantics.md)
reconstructs the complete implementation path while preserving this public
business contract. It is a design candidate, not an implemented or accepted
feature claim. Ordinary Fluent, `.Prepare()`, handwritten descriptors and
generated models/DTOs continue to use precompiled C++ provider packages.

Prepared shapes retain stable SQL/parameter/projection metadata; each execution
captures independent values and checks them against that layout. The target
resolves parameter ordinals once and passes validated typed arguments directly
to provider binding, removing redundant native frame encoding and parsing.
Dynamic command representation must pass the explicit direct-compiler versus
NWQC replay gate; the prior tape is not a public behavior requirement.

Keep validation and recoverable builder-error timing, source/profile checks,
clone/CTE/literal ownership and nonsealing `ToSql()`. PostgreSQL uses fresh
Parse/Describe in one preparation group; its cross-execution physical cache is
not selected because external DDL changes cached-result error semantics.
SQLite reuses one statement within the command, with no step at cursor open.
Public opening/execution side effects, transaction failure, cancellation,
backpressure and safe connection return remain observable acceptance conditions.

The existing borrowed native batch remains owned through reading. Direct native
batch construction and one-time managed layout matching may replace staging and
repeated cell checks only while preserving shape, codec, NULL, bounds and mapper
failure cleanup. Model/DTO-only edits must still rebuild locally without changing
native bytes. Actual package-consumer evidence, deletion inventory and matched
local performance belong to Plan; this contract grants no zero-allocation claim.

## Historical query optimization contract — resumed DB-Perf-01

The [current query decision](query-semantics.md) describes the implementation
candidate in [Korda #37](https://github.com/IzuSharp/Korda/pull/37), reviewed through
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20), while preserving the
business behavior below. The candidate uses a complete managed command and eager
runtime logical compilation. Physical statements are still prepared per provider
command. [Plan #34](https://github.com/IzuSharp/Plan/pull/34) owns exact source
identities and local correctness receipts; final performance and delivery remain
unaccepted at this checkpoint.

Fixed shapes reuse parameter order/codecs, projection and compiled query structure,
with changing values captured independently at each execution. The existing
`.Prepare()` remains the public entry and finishes SQL/slot compilation plus
parameter validation metadata before returning its source-bound plan. It neither
opens a connection nor prepares a physical database statement. Each execution still
validates its own values; the immutable schema/hash/descriptors are cached.
Optional generation of static command templates and direct binders requires an
independently defined supported
subset; existing entity/DTO generation does not already provide that feature.
Handwritten descriptors and ordinary Fluent remain supported without a generator.

For dynamic queries, C# records selected conditions, operators and projection in
bounded local slots before one complete NWQC submission. The candidate extension
uses capability bit 26 and separate compile, render and CTE entry points, replaying
the existing 22 clause operations and topological subquery blocks through C++.
Source-bound models/plans/CTEs use a validated owner sidecar; pointer values are
never serialized into command bytes. Missing extension support is an explicit
unsupported error, with no product fallback to individual native node calls.
C++ owns validation, dialect rendering and execution through the existing Host.
No C# SQL compiler, provider replacement or client evaluation is introduced.
One command means a complete logical query; results still arrive in bounded cursor
batches. Metadata registration and fetch/cancel/dispose remain distinct operations.

Clones and CTEs retain the identity of shared scalar origins through bounded owner
leases and native origin bindings. This preserves retained-literal budget and
lifetime behavior, including unused constructed expressions; it does not merge
independently constructed equal values or deduplicate SQL parameter occurrences.

Preserve immediate public validation, owner/source checks, recoverable mutation
failure and the nonsealing behavior of `ToSql()`. `.Prepare()` and
`CommonTable.Create` are explicit native compilation boundaries; `ToSql()` compiles
a diagnostic snapshot without changing the builder. Changing parameters still
snapshot and validate at execution, while provider errors retain their database
execution/cleanup boundary. Existing transaction, cancellation, streaming and
disposal guarantees remain. A future connection-local statement cache must be
bounded and protocol-clean; it is separate from this candidate's logical reuse.
Never replay a mutation after an unknown outcome.

Correctness and API/package acceptance continue through existing module-selected
checks and independent PostgreSQL/SQLite Native AOT package jobs. All performance
work runs locally on Linux, using the [measurement rules](../performance/methodology.md)
and [current validation matrix](../verification/models-and-matrix.md). Plan records
actual results. The implementation candidate and its local checks do not establish
final performance acceptance, a merged PR or a published package.

## Business journey and reuse

An application lists a page of orders with customer names and totals, optionally filters customer/status/date, and then loads the page's order lines in one bounded batch. It looks up one order by key, writes an explicitly selected subset of fields, detects an obsolete row version, inserts an order and returns its key, and commits an awaited transaction callback with an explicit failure outcome. The same immutable DTO can consume a Fluent projection or parameterized SQL. A model change yields a reviewable migration; an existing table can yield compilable attributed C# source.

The current query sample already demonstrates filters, joins, grouping, aggregate expressions, static DTO construction, prepared parameters, offset paging and single-key cursor paging. The current relation sample already demonstrates composite keys, NULL assignment, checked updates, lookup and individual relation loading. These are retained inputs. The initial gap audit identified projection boilerplate, convention opt-in, reusable codec declarations, composite cursors, batched relations and a transaction callback; schema generation/scaffolding requires new design. No row is accepted merely because its lower layer already exists.

## Model conventions and static projection

An opt-in parameterless `DbTableAttribute()` uses the exact CLR type name as table name and infers the unique nonnullable `Id` member as key. An explicit string constructor keeps existing behavior unless `InferPrimaryKey = true` is selected. Explicit `DbColumn` metadata overrides naming and flags. C# identifier casing is not silently changed by convention. Missing/ambiguous/inaccessible members and unsupported model shapes receive generator diagnostics before runtime; no broad reflection fallback is allowed.

`DbProjection` on an ordinary class or record emits a static `Projection<TDto> Row` for parameterized SQL and a typed `Bind<TEntity>(Query<TEntity>, SqlExpression<T1>, ...)` factory for Fluent expressions. Parameter names follow DTO member names so the caller can map repeated names and computed expressions explicitly. The generated projection includes exactly those expressions; it does not select the entity's entire row. `DbColumn` supplies exact result aliases. Duplicate aliases fail with a static diagnostic (NWQ0104). `DbConstructor` and `DbParameter(nameof(Member))` select the constructor and parameter/member association; existing NWQ0102/NWQ0103 ambiguity diagnostics remain meaningful. Nullability is part of the generated reader type and is validated for the selected constructor.

Illustrative expected composition, with exact compiled output owned by the product:

```csharp
using var orders = session.From(OrderMapping.Table);
var customer = orders.InnerJoin(CustomerMapping.Table, "customer",
    on => on.Left(OrderMapping.CustomerId).Equal(on.Right(CustomerMapping.Id)));
var row = OrderRows.Bind(orders,
    Id: orders.Column(OrderMapping.Id),
    Customer: orders.Column(customer, CustomerMapping.Name),
    Total: orders.Column(OrderMapping.Total));
var page = await orders.OrderBy(OrderMapping.CreatedAt).OrderBy(OrderMapping.Id)
    .Take(pageSize).Select(row).ToListAsync(cancellationToken);
```

This snippet is an intended call shape, not an executed sample. Final documentation must link the compiled business sample and use its exact signatures. Optional filtering and aggregates should compose through existing typed expressions; do not add redundant alternatives simply to shorten every line.

## Reusable value mapping

`[assembly: DbCodec(typeof(OrderId), typeof(OrderCodecs), nameof(OrderCodecs.Id))]` supplies a compilation-wide codec default. The declared member must be an accessible static value of exactly `ValueCodec<T>`. `DbUseCodec` overrides a property's default. A nullable member wraps the configured nonnullable codec. Conflicting defaults and incompatible values fail compilation instead of silently choosing one.

`Codecs.Convert<T,TStore>(ValueCodec<TStore>, Func<T,TStore>, Func<TStore,T>)` adapts a business value such as `OrderId` while preserving the store codec identity, encoding bounds and database type. Storage codecs must be nonnullable; nullable wrappers apply after conversion. Decimal precision/scale and JSON policies are reusable codec values, not provider guesses. Projections validate an explicitly expected codec ID, configuration and nullability against the expression's codec. A DTO can therefore share the same policy across Fluent, raw SQL, writing and model-driven schema. Conversion delegates are application code; their exceptions follow ordinary pre-admission/materialization behavior and never cross an unmanaged callback boundary.

## Composite cursor and batched relationships

`QueryCursor<TEntity>.Create<T>(Column<TEntity,T>, T).Then<T>(Column<TEntity,T>, T)` holds a copied ordered cursor value sequence. `Query<TEntity>.SeekAfter(QueryCursor<TEntity>)` validates exact correspondence with the query's complete ORDER BY sequence, including the full nonnullable root primary key as unique tie-breaker. Mixed ascending/descending columns form the corresponding lexicographic native predicate. Reject nullable cursor columns, missing/duplicate order keys, offsets and subsequent order changes. Boundary tests include equal leading values, first/last pages and empty continuation; a changing database does not acquire snapshot isolation merely by using a cursor.

`DataSession.LoadRelatedAsync<TParent,TChild>(IReadOnlyList<EntityKey<TParent>>, Relation<TParent,TChild>, CancellationToken = default)` returns groups aligned with input indices. Empty input performs no SQL. A nonempty admitted bounded batch performs one SQL execution, preserves duplicates and empty groups, and uses database comparison/collation semantics. Child order is unspecified unless separately modeled. The planned native tagged UNION ALL shape retains all configured row/byte limits, parameter typing and cancellation/retirement. It is not an N+1 loop hidden behind an asynchronous method. Verify actual provider query counts for a page of orders and for the empty case.

## Writes, concurrency and transactions

Reuse the existing key lookup, selective `Changes<T>`, checked mutation and insert-returning machinery wherever available. No change entry means untouched; an explicit nullable value means write SQL NULL. A concurrency check includes the expected token in the mutation predicate, and zero affected rows must not be reported as success. Existing buffer ownership, result bounds and capability rejection remain.

`DataSession.InTransactionAsync<T>(Func<DataSession,CancellationToken,Task<T>>, TransactionOptions? = null, CancellationToken = default)` and its non-generic Task overload await a business callback in one session transaction. Reject an active transaction; do not silently nest or replay. Pre-cancellation never calls the callback. Successful callback completion is followed by commit; the return value is published only after confirmed success. Every path joins native cleanup via `DisposeAsync`. Callback/cancellation/commit exceptions keep their original identity and stack; cleanup outcome is recorded separately.

A `TransactionFailure` snapshot records `TransactionOutcome`, whether commit was attempted, `DatabaseCloseResult` cleanup and optional recovery key; `TransactionFailure.TryGet(Exception, out TransactionFailure?)` retrieves it from the original failure. Unknown commit remains unknown even if cleanup succeeds, and is never automatically retried. A cancellation is not proof that no writes occurred. The callback must await its operations and preserve the session's existing single-command concurrency rules.

## Reviewable migrations and reverse scaffolding

The new migration design uses explicit immutable model snapshots built from static table metadata and a versioned persisted prior snapshot. Comparing them generates a provider-specific draft through the C++ dialect layer. It never runs on construction, DI registration or startup. The draft identifies operations and returns SQL for inspection; existing `Migration`/`MigrationBundle` and `MigrateAsync` remain the application path.

The initial supported diff must be narrow and honest. Unsupported type conversion, generated/default/backfill behavior or provider rebuild semantics is rejected with the offending table/column. Dropping a table/column or tightening a nullable/type constraint cannot become applyable without explicit per-change developer selection. A boolean permitting every destructive operation by default is not sufficient. No data movement or database introspection is hidden in a pure draft operation.

Reverse scaffolding consumes the existing `GetTablesAsync` catalog and explicit hints where catalog v1 cannot establish CLR/codec type, ordered composite key, generated flags or default semantics. It emits ordinary C# classes/records with public generator attributes, safe names and explicit column aliases. Unknown facts must remain actionable diagnostics or require a supplied hint. The implementation must compile generated entities in a source-tree-external provider consumer; emitting plausible-looking text is not acceptance.

## Ownership, diagnostics, compatibility and costs

Generated mappings/projections are immutable descriptors; mutable query builders retain their documented session/thread lifetime. Cursor values snapshot at composition. Batches copy keys before asynchronous retention, enforce configured bounds and release native plans/row batches on success, cancellation and exceptions. Mapping uses no unbounded reflection or dynamic code. Existing SQL parameters remain parameterized, and diagnostics exclude parameter values/credentials by default.

The intended boundary cost is generated managed metadata plus existing native composition calls; batch relations use one SQL execution for admitted nonempty input; PostgreSQL preparation, description and synchronization exchanges are counted separately. DTO-only changes require no native compiler or new native asset. These are contracts to measure/verify in the business sample, not unmeasured performance claims.

Additive signatures need binary/source compatibility, overload/nullability and XML/reference checks selected by the affected modules. Keep old C ABI layouts, action numbers and capability behavior; negotiate any extension explicitly. New module roots, test paths, dependencies, checks and package outputs must be registered. Internal libraries remain buildable/testable while only independent top-level providers are installable.

The schema-draft extension uses the existing `nw_db_admin_create_v1` entry point
with new action **4**, guarded by appended capability `db.schema.draft.v1` at bit
**25**. Existing actions 0–3, capability bits 0–24, ABI version and structure layouts
retain their meanings. The managed facade rejects a missing capability before
dispatch. Drafting never opens a database connection. Request control record kind
5 carries provider field 1 and bounded canonical previous/current model sequences
in fields 7/8. Result control record kind 19 carries action 4 and either change sequence field 2
or bounded rejection text field 6. Each change is kind 21 with its stable ID,
kind, schema/table/column, quoted SQL and destructive flag. An unsupported
difference preserves the offending table/column context; it cannot yield partial
applyable SQL.

The initial draft supports new tables, nullable nongenerated nonkey column
additions, nonkey column drops and table drops. An unchanged column must preserve
its type, codec configuration, nullability, key/generated policy, default,
collation and length metadata. Differences requiring conversion, backfill or
table rebuild reject. Each destructive operation has an exact stable digest and
must be individually selected; unknown/repeated selections reject. A no-op draft
cannot become an empty migration. Reverse scaffolding requires an explicit
generated-column list and complete ordered composite key, and emits bounded C#
source with safely escaped identifiers/literals and explicit ambiguous-type hints.

## Acceptance

Separate external PackageReference projects restore each exact provider package and run directly as Linux x64 Native AOT executables against real PostgreSQL and SQLite. Assert projected columns/business values, optional filters, join/aggregate DTO mapping, cursor boundaries, empty/grouped relations and SQL counts, NULL/omission and concurrency, rollback/cancellation/unknown-commit behavior, reviewed migration choice and generated-entity compilation. After editing only a DTO, recompile/re-run and compare the same native payload/loaded hashes. Record exact source/package/executable provenance.

The short English tutorial connects install, provider DI, one business query and diagnostics, and links both schema workflows. Evidence must distinguish source review, compilation and actual execution. Plan owns non-author review, exact PR checks, normal merges, merged-main CI and every triggered publication. This Design gate checks contracts/history only.
