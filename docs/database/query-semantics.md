# Current C++ query decision — DB-Perf-01

Status: implementation candidate and local correctness checkpoint for the resumed
Linux x64 task, continued in [Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34). Preserve the existing C# Fluent
API and C++20/libpq/sqlite3 execution. This section governs the current work; the
original D16 Rust/SeaQuery text below remains historical.
[ADR-0006](../decisions/ADR-0006-database-cpp-native.md) already changed the native
implementation language. This decision separates candidate behavior from remaining
work; it does not claim final performance acceptance, merge or release. Plan owns
exact candidate identities, executed checks, priorities and the
[continuation record](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/handoff-linux.md).

## Observed starting behavior

The source audit binds to Korda
[`c1aca12cadfe3f4e2431ded24c13f7afb58453a0`](https://github.com/IzuSharp/Korda/commit/c1aca12cadfe3f4e2431ded24c13f7afb58453a0).
It establishes implementation behavior, not measured cost:

| Layer | Observed behavior | Source |
| --- | --- | --- |
| Fluent composition | Columns, values, operators and clauses call native bindings individually | [QueryContext.cs](https://github.com/IzuSharp/Korda/blob/c1aca12cadfe3f4e2431ded24c13f7afb58453a0/src/Query.Fluent/QueryContext.cs), [QueryBinding.cs](https://github.com/IzuSharp/Korda/blob/c1aca12cadfe3f4e2431ded24c13f7afb58453a0/src/Query.Binding/QueryBinding.cs) |
| `.Prepare()` | Freezes a source-bound logical native plan and caches managed parameter/projection metadata; SQL compilation is lazy on first render | [Terminals.cs](https://github.com/IzuSharp/Korda/blob/c1aca12cadfe3f4e2431ded24c13f7afb58453a0/src/Query.Fluent/Terminals.cs), [query.cpp](https://github.com/IzuSharp/Korda/blob/c1aca12cadfe3f4e2431ded24c13f7afb58453a0/native/cpp/src/query.cpp) |
| Physical statements | SQLite prepares/finalizes per command; PostgreSQL prepares/describes an unnamed statement per command | [provider.cpp](https://github.com/IzuSharp/Korda/blob/c1aca12cadfe3f4e2431ded24c13f7afb58453a0/native/cpp/src/provider.cpp) |
| Parameterized SQL | Submits a complete template, parameter frame and options to the same C++ Host | [SqlSubmission.cs](https://github.com/IzuSharp/Korda/blob/c1aca12cadfe3f4e2431ded24c13f7afb58453a0/src/Data.NativeHost/SqlSubmission.cs), [host_abi.cpp](https://github.com/IzuSharp/Korda/blob/c1aca12cadfe3f4e2431ded24c13f7afb58453a0/native/cpp/src/host_abi.cpp) |
| Source generation | Generates table/projection metadata and typed DTO construction; does not compile arbitrary Fluent method bodies | [ModelGenerator.cs](https://github.com/IzuSharp/Korda/blob/c1aca12cadfe3f4e2431ded24c13f7afb58453a0/src/Query.Generator/ModelGenerator.cs) |

These rows describe the inspected starting point, not the resumed implementation
candidate. Earlier #37 allocation reductions retain their actual source identities.
The candidate changes composition, eager logical compilation and cache locking as
specified below; it does not add physical statement reuse. Logical shape caching,
provider statement reuse and the database server's execution-plan policy remain
separate mechanisms.

## Chosen ownership boundary

| Work | C# responsibility | C++ responsibility |
| --- | --- | --- |
| Composition | Existing typed Fluent calls, application conditions, owner/type checks and a bounded command representation | Authoritative query semantics, backend capability validation and dialect compiler |
| Fixed shape | Static descriptors, reusable parameter layout and optional generated command template | Validate and compile an immutable logical plan for the compatible source/profile |
| Execution | Snapshot changing values before asynchronous retention; submit the complete command or prepared plan | Admit on the selected session, bind physical parameters and execute through libpq/sqlite3 |
| Results | Validate the result shape and invoke typed DTO readers/constructors | Own the cursor and produce bounded result batches |
| Lifetime | Preserve cancellation, public disposal, stream backpressure and managed ownership | Preserve transaction outcome, physical connection state, drain/discard and native retirement |

C# does not gain a SQL dialect emitter, relational optimizer, client-side filter,
reflection mapper or managed provider fallback. Its representation records the
supported Fluent operations, not arbitrary serialized C# expressions.

## Fixed queries and advance compilation

Separate stable shape, parameter identities/order/codecs, projection and mapper
from changing values. Prepare stable work once and use independent value storage
for each execution. Values do not enter shape keys. Keys bind engine/ABI, source
generation, semantic profile, metadata content, operators, parameter codecs and
projection. A hash match never replaces equality. Bound retained entries and
bytes; eviction cannot invalidate in-use owners.

The candidate retains `.Prepare()` and its independently disposable, source-bound
plan. The complete-command compile entry now seals and compiles immutable SQL,
argument layout and execution-parameter validation metadata before returning the
plan. Preparation is a runtime, source/profile-aware boundary; it performs no
database I/O. Warm execution parses and validates each supplied value frame against
the cached expectation without rebuilding its schema, hash or descriptor vector.
Per-execution copying and wire encoding still exist and remain measurable costs.

Immediate managed argument/owner checks and recoverable builder errors stay at
their public call boundary. Native query compilation errors are reported at the
explicit compile/render boundary; changing-value errors remain execution checks,
and database description/execution errors remain provider work. Report preparation
as cold cost rather than moving it out of the measurements. Concurrent executions
use separate sessions of the same source and independent snapshots. Disposal
rejects new dispatch; already accepted operations keep their retained plan.

Optional source generation may later emit a fixed command template, direct typed
parameter writer and static result mapper for a demonstrably static supported
shape. It cannot evaluate arbitrary application methods, capture mutable closures,
contact a database or invoke the native compiler. Runtime-dependent condition
branches use the complete dynamic path. Unsupported static shapes need an explicit
diagnostic or a documented dynamic classification, never a claim of precompilation.
Generation remains optional; ordinary entity/DTO edits do not rebuild C++.

Build-time descriptor/template generation is not server-side preparation. Runtime
source/profile validation and connection acquisition remain necessary. No new
fixed-query generator API is claimed here: supported syntax, diagnostics and
handwritten parity require a concrete implementation and compiled examples first.

## Dynamic queries: one complete command

The candidate composes the complete query in managed memory and crosses the
query-composition ABI once at preparation or submission. Its additive extension
requires capability bit 26, `db.query.command.v1`, and all three entry points:

| Entry point | Compile boundary |
| --- | --- |
| `nw_db_query_command_compile_v1` | Seal and compile the complete query for its terminal, including `.Prepare()` |
| `nw_db_query_command_render_v1` | Compile a complete diagnostic snapshot for `ToSql()` without sealing the mutable builder |
| `nw_db_query_command_cte_v1` | Compile a complete body for `CommonTable.Create`, returning an immutable CTE owner |

The frozen database v1 declarations and fingerprint are unchanged. Product callers
require the complete extension and return a structured unsupported error when it
is unavailable; there is no silent per-node fallback. Retained direct C ABI calls
serve compatibility and differential fixtures.

NWQC v1 is a bounded little-endian operation tape with explicit lengths. It carries
the existing column/value/parameter, binary/unary/list and import records, and all
22 existing clause opcodes. Subquery snapshots form topological blocks: imports
refer only to earlier blocks, every block reaches the final root, and result slots
refer only to earlier records in their block. Projection tokens, JOIN aliases and
window snapshot order retain their existing semantics. It is a record of supported
Fluent operations, not a second SQL compiler or a general C# expression format.

Metadata models, immutable plans and CTEs travel in a typed owner sidecar. The Host
resolves and pins each owner through its registry, checking kind and source
generation. The bytes contain checked sidecar/block/slot indexes, never native
pointers or generation tokens. Existing node/depth/parameter/value budgets apply
while composing and during replay. A separately bounded envelope allows headers
and references without increasing the native expression or retained-value limits.
The product's [versioned protocol](https://github.com/IzuSharp/Korda/blob/task/DB-Perf-01-linux/native/database/binding/query-command-v1.md)
and separate extension header own exact wire layouts and C declarations.

C++ validates and replays the entire command through the existing native query
representation and compiler before publishing a plan or admitting provider I/O.
The same Host owns execution. Unknown versions/opcodes, invalid references, cycles, excessive limits,
wrong owners/codecs and unsupported clauses reject without partial publication or
a database send. Additive capability/version negotiation preserves old ABI layouts
and action meanings.

The native candidate's local differential checks cover the retained SQL/ordered
argument goldens, malformed input and capability rejection, snapshot/CTE budgets
and concurrent cache use. These checks establish their own tested cases; Plan
records managed, package and real-provider results separately. Native decoder
coverage alone is not final product or performance acceptance.

Preserve public type/owner/disposal/concurrent-use checks and builder recovery after
a rejected mutation. Checks observable at the mutating call remain there through
managed validation and negotiated capability/limit metadata. Native-dependent
checks remain authoritative at compile/submission before I/O. Delaying every invalid
mutation until execution, poisoning a formerly recoverable builder, changing
documented public-call error precedence or silently dropping unsupported SQLite
syntax is incompatible.
`ToSql()` remains a diagnostic clone with placeholders, no execution and no seal;
it may use one complete rendering command without changing subsequent composition.

Freeze/copy values at the existing call boundary before the first await. Later
`QueryParameters` edits cannot change accepted work. Synchronous C++ decoding must
finish before borrowed managed memory is released, or explicitly retain owned
immutable bytes. No borrowed span crosses await. A complete query submission does
not combine fetch/cancel/dispose into that command: bounded cursor batches,
backpressure, early stop and retirement remain independent operations.

### Scalar origins across clones and CTEs

Clones and immutable subquery snapshots retain scalar origin identity. A command
uses bounded origin IDs to reuse the same immutable literal/parameter slots across
its blocks. A successful plan or CTE retains an immutable origin map; a later
command can bind an origin to that same-source owner through the sidecar. Replay
checks kind, operation, identity bytes, codec and value before sharing a slot.
Independent construction of equal values remains a different origin.

This preserves clone/CTE retained-literal and expanded-graph budgets, including a
constructed but unused escaped text predicate. It is not SQL-placeholder or
parameter-occurrence deduplication. The local negative control creates a 6002-byte
escaped literal once; losing its shared identity across a CTE retains 12004 bytes
and incorrectly rejects an otherwise valid 9000-byte budget. The seeded candidate
matches the direct path's 6002-byte retention. Plan retains the measured counts and
source-bound receipts.

Managed origins retain bounded leases for their captured compiled owners while a
tape/snapshot still uses them; publication of a first shared capture is coordinated.
Capture is limited to shared/snapshot cases and CTE boundaries; an ordinary unique
terminal does not retain an extra compiled owner lease.
Native origin maps hold scalar data and do not point back to the plan or CTE owner.
No thread-local or source-global literal pool is introduced. Capturing an owner
can retain its body snapshot as well as its scalar slots; that cold cost must be
included in memory measurements. Disposal and concurrent snapshot tests remain
required, rather than assuming a matching SQL string proves lifetime correctness.

Native command parameters first enter a private registry. Only successful final
compilation atomically merges identities into the source registry, so a malformed
or rejected command cannot reserve a source parameter ID.

**Selected follow-up, pending implementation and measurement:** an exclusive
command with one root, no dependencies and exactly one tape reference per
uncaptured origin may use a direct serializer to avoid generic temporary traversal
and indexing collections. The NWQC frame, dense scalar origin ordinals, typed root
model sidecar, bounds, source checks and lifetime/error behavior remain unchanged.
`CreateCte`, shared or captured origins, snapshots and imports retain the generic
path. This is an implementation detail within the existing complete-command
contract, selected after the [first SQLite phase observation](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/query-optimization/phase-sqlite-r0-034b40ea/README.md);
it does not claim an implemented optimization or measured benefit.

## Parameters, physical statements and contention

A reusable parameter layout should write values directly in final slot order,
avoiding repeated sorting, schema/hash construction and intermediate cell/frame
encoding. Preserve missing/extra/foreign parameter errors, nullability, conversion
and exception order. Do not retain mutable caller buffers to reduce copies.

Physical statement reuse remains unimplemented in this candidate. It is a separate
proposed connection-local optimization.
SQLite may reset and clear bindings before returning a statement to a bounded
cache; PostgreSQL may retain named statements on their owning connection. A key
covers canonical SQL, ordered parameter types and relevant session/schema state.
Never share a live statement across connections or concurrent commands. Eviction,
source/connection close, schema invalidation and failed protocol cleanup release
or discard resources. Do not replay an accepted mutation or unknown transaction
to repair a cache entry. Existing SQLite error precedence, PostgreSQL description
checks and protocol synchronization remain validation requirements.

The candidate places synchronization inside `ShapeCache`: one mutex protects
lookup, collision checks, LRU mutation, byte accounting, `counts()` and `clear()`.
Immutable compilation and key calculation are outside that mutex. The Host no
longer holds a source-wide shape lock across execution parameter parsing, copying
and encoding. A returned shared shape remains alive through eviction or clear.
Local concurrent render/clear/evict checks verify SQL, actual parameter values and
cache bounds. Measure wait/hold and queueing before claiming a concurrency
improvement. Per-row, admission and retirement gates remain unchanged.

## Research inputs and implementation priority

| Input | Applicable mechanism |
| --- | --- |
| [SqlSugar conditional composition](https://github.com/DotNetNext/SqlSugar/blob/master/Src/Asp.NetCore2/SqlSugar/Abstract/QueryableProvider/QueryableProvider.cs) and [reader execution](https://github.com/DotNetNext/SqlSugar/blob/master/Src/Asp.NetCore2/SqlSugar/Abstract/QueryableProvider/QueryableExecuteSql.cs) | Compose selected conditions, then execute complete SQL/parameters. Adopt the boundary, not reflection-based mapping. |
| [EF Core compiled queries](https://learn.microsoft.com/en-us/ef/core/performance/advanced-performance-topics#compiled-queries) | Reuse stable shapes with changing parameters; distinguish expression matching, logical compilation and database preparation. A runtime compiled delegate is not build-time Korda SQL compilation. |
| [Dapper.AOT generated code](https://aot.dapperlib.dev/generatedcode.html) | Separate parameter structure from value updates and identify result columns once before typed row mapping. Dapper.AOT is the external performance comparator. |

The SqlSugar inspection observed blobs
`b15ef18c25b7602250b274ae2f7348f5a815e8a9` and
`e5e42a4c9419415b03ab9c9ecd9950245a2af7dc`, respectively. Moving branch links
above are navigation, not immutable reproduction identities.

| Priority | Work and completion criterion |
| --- | --- |
| P0 | Establish identical-SQL/parameter/result/connection local comparisons for ordinary Fluent, warmed `.Prepare()` and the same Host's parameterized SQL. Split construction, first row, remaining read and release. |
| P1 candidate | Complete-command composition/replay, early SQL and parameter-metadata compilation, and scalar-origin ownership are implemented for review; retain native/managed negative, lifetime and real-provider evidence before acceptance. |
| P1 candidate / gap | Cache locking is narrowed to internal LRU bookkeeping with local concurrent checks. Physical statement reuse remains a gap requiring hit, invalidation, cancellation and cleanup evidence. |
| P2 | Optimize batch conversion and mapper temporaries where measured costs remain; preserve bounded memory and complete-result correctness. |
| P2 | Consider optional generated fixed-query templates after the command contract is stable; ordinary Fluent remains fully supported without them. |
| Acceptance | Retest both real providers and actual Native AOT consumers, then run final candidate and Dapper.AOT local 30-minute mixed segments per provider; record remaining gaps and stopping reasons in Plan. |

Normal CI uses the existing module planner and independent provider package jobs.
All performance experiments and long segments run locally on Linux. No benchmark
workflow, CI job or automatic PR/push benchmark action is added. The
[current methodology](../performance/methodology.md) defines measurement and
attribution. Documentation checks do not establish product execution.

## Historical D16 research contract

The original text below retains Rust/SeaQuery findings, provisional API and original
evidence. Its implementation ownership and optional batching choice are superseded
for the C++ product by this decision. SQL NULL, parameterization, capability
rejection and ownership obligations remain applicable where retained by the current
Fluent contract. Historical accepted hashes refer to their unchanged snapshots.

# D16 — Native query semantics and typed Fluent contract

Contract: **C-QUERY-001@0.4.0**; design candidate. The registry records exact-content independent review and acceptance; product implementation/release gates remain in Delivery. Evidence: [R25](../research/topics/R25/source-driven-seaquery.md), [recovered AOT probe](../research/source-driven-evidence/README.md), existing R22/R24/R25 reports. This replaces full declaration-only LINQ capture, generic C# predicate compensation and required schema-specific SeaORM generation as the ordinary route. Historical SQL counterexamples remain valid; no arbitrary IQueryable compatibility is promised.

## Public API refinement 0.4.0

The exact public declarations and complete native operation inventory are now
[Database/ORM API 0.4.0](../api/database.md), its
[coverage matrix](../api/database-coverage.json), and
[Database.cs](../../experiments/public-api/NativeWeave.Api.Design/Database.cs).
They replace earlier provisional signature spellings; the lifecycle, native-source
findings and historical experiment identities below remain normative within that
explicit scope. Native AOT fixture compilation is separate from product execution.
Fresh exact-content review is required; prior accepted versions remain immutable.


## 1. Semantic owner and scope

Rust SeaQuery owns query construction, native Expr/Condition state and SQL dialect generation. SQLx executes parameterized results. C# contributes typed descriptors, Fluent method calls, static projection construction and application logic. Its transport encoding is not a second SQL AST, rewrite engine or dialect emitter. Compiling C# does not imply compiling arbitrary C# lambdas into Rust.

The initial domain includes explicit CRUD, scalar typed values/null, filters, ordering, grouping/having/aggregates, inner/left joins, subqueries and backend-supported CTE/window constructs. Capability coverage is enumerated per operation/backend/profile; “SeaQuery supports it” is not sufficient to claim a stable C# binding exists. Additional operators are bound rather than replaced by a large general-purpose query compiler.

## 2. Typed facade and runtime metadata

A table descriptor contains a stable metadata identifier, validated table/column name, codec, nullability and explicit primary keys. Independent post-Build Relation descriptors bind two immutable model identities and ordered key pairs through the source-bound registration/load ABI in `docs/api/database.md` §9.2.1; they do not mutate canonical table metadata. The C# type `Column<TEntity,TValue>` prevents accidental cross-entity/value use in supported APIs; joined scopes need explicit aliases and typed association, not a general unchecked string field. Dynamic external fields are resolved against an allowlist, and native code validates again. C# type safety alone is not a sandbox for raw ABI input.

Design consumer shape; its exact methods are covered by the declaration fixture:
```csharp
using var q = session.From(Students.Table);
q.WhereGreaterThanOrEqual(Students.Age, minAge)
 .WhereIsNotNull(Students.Email)
 .OrderBy(Students.Id, nullOrder: NullOrder.Last)
 .Take(100);
var rows = await q.SelectAll().ToListAsync(ct);
```

`Where(row => row.GreaterThanOrEqual(Students.Age, minAge))` executes an ordinary
synchronous builder delegate over native-backed expression proxies. `WhereIf`
skips callback/native construction when its condition is false. Neither translates
arbitrary `Func<Student,bool>`. Cross-query values must follow the documented
native clone/import route or reject. The earlier compiled research probe remains
evidence only for its narrower typed-column composition and wrong-entity rejection.

## 3. Native builder and value lifecycle

Builder states: Mutable → Sealed → Submitted → Closed, with Poisoned on unsafe partial mutation failure. A logical single-writer gate precedes extracting the native handle; SafeHandle lifetime references alone cannot prevent Rust `&mut` aliasing. Sealing freezes the query shape/owned values. Parameter values are snapshotted at an explicit call/submission point, never reread from a mutable closure after await. A prepared reusable shape and per-execution parameter storage must be distinct objects with explicit cache ownership.

The Adapter maps operations to public SeaQuery methods and retains the resulting native Expr/Condition/statement. It validates sizes, nesting/operation limits, CTE shape, typed values and backend capabilities. A batched operation representation is optional and must have a versioned decoder and bounded allocation; partial failures either commit no builder change or poison the builder. That local property is unrelated to database transaction atomicity.

No function pointer, Rust trait object, Vec layout or native enum discriminant becomes a public wire value. ABI constants are explicitly versioned. Upstream non-exhaustive enums and Cargo feature-gated values are checked during adapter upgrades.

## 4. NULL and Boolean semantics

The default is **SQL three-valued logic**. Equality with a NULL operand yields UNKNOWN unless an explicitly named null-safe operation is requested; `IS NULL`/`IS NOT NULL` are distinct methods. WHERE retains TRUE only. NOT UNKNOWN remains UNKNOWN; FALSE AND UNKNOWN is FALSE; TRUE OR UNKNOWN is TRUE. For compatible totally ordered operands, SQL `NOT(x > y)` and `x <= y` both yield UNKNOWN on NULL; nullable data alone does not invalidate that equivalence. Do not silently replace these with C# two-valued null compensation, or generalize the equivalence to NaN/custom partial-order operators. The focused R24 SQLite integer truth-table fixture records this correction.

An optional `NullSafeEqual` capability may use PostgreSQL `IS NOT DISTINCT FROM` or SQLite `IS` only within declared codec/collation domains and tests. It is not a promise that every .NET equality, NaN or mixed SQLite storage class has identical semantics. SQL `IN`/`NOT IN`, NULL-containing sets and empty sets have explicit operator behavior; do not label them LINQ `Contains` without an independently specified convenience rule. Empty-membership convenience may deliberately produce FALSE/TRUE, but must be named/documented and tested separately from native SQL rendering.

## 5. Values, arithmetic, strings and pagination

Every value is bound, never interpolated as SQL text. Identifiers are validated metadata, not values masquerading as identifier parameters. Collection length, total parameter count/bytes, query depth/node count and query result size have finite configurable limits from the selected backend profile. Reject or select an explicitly supported bulk-parameter mechanism when limits are exceeded; do not switch to literal concatenation.

Integer narrowing is checked. SQLite integer arithmetic can promote overflow to REAL; SQL arithmetic is not automatically C# checked arithmetic. Decimal PostgreSQL precision/scale/rounding are explicit. SQLite exact decimal-as-TEXT is a round-trip codec only, not automatic numeric SUM/order/range semantics. Fixed-scale checked Int64 is a separate money profile. NaN/Infinity, JSON/array/provider custom types and date/time precision need their own capability tests.

String comparison uses explicitly selected database collation. UTF-8 binary ordering is not arbitrary .NET UTF-16 ordinal or culture-sensitive equality. LIKE helpers that mean literal Contains/StartsWith/EndsWith escape `%`, `_` and the escape character before binding and state case/collation behavior. Raw SQL LIKE patterns remain a different API. No client-side filtering fallback.

Sort keys carry direction and explicit null order where promised. Paged business queries require a deterministic unique tie-breaker; native LIMIT without order may still exist as an explicitly nondeterministic low-level capability, not a guaranteed page API. Keyset cursor metadata binds query/profile/sort/codec and tenant scope, is tamper-resistant if exposed to clients and cannot remove authorization predicates. Keyset pagination alone does not give cross-request snapshot consistency; use an explicit snapshot/export policy when required. Offset/limit and export durations are bounded.

## 6. Join, aggregation, CTE and windows

Do not relocate a LEFT JOIN right-side predicate between ON and WHERE; that changes results. Use a non-null key or explicit match marker to distinguish an unmatched row from a matched nullable column. Projection nullability follows the selected join. Grouped projections contain declared keys/aggregates, not arbitrary in-memory groups. COUNT returns a checked documented integer width; SQL SUM on an empty set remains NULL unless the caller explicitly asks for a coalesced value. No hidden C# aggregate equivalence.

Expose native subqueries, CTEs and windows where the backend profile supports them. Validate empty/malformed CTEs before native renderer assertions. SQLite row locking, SELECT INTO and SEARCH/CYCLE must be rejected when requested because the inspected native paths can ignore them; unsupported ANY/SOME/ALL must return UnsupportedCapability before a panic or DB send. Multiple named-window definitions exceed the inspected SelectStatement's single optional slot: bind supported inline/single named windows now and require a source extension or revised upstream API before promising arbitrary named-window lists.

UNION/UNION ALL/EXCEPT/INTERSECT require compatible projection shapes and backend set/null/duplicate semantics. Unsupported clauses fail explicitly; do not synthesize another C# SQL dialect to fill the gap or silently drop a clause.

## 7. ORM policies: explicit, Rust-owned, not inherited by name

NativeWeave's ordinary profile specifies primary-key CRUD, explicit relationship joins, partial changesets, version-column compare-and-swap and migration integration. A changeset represents not-set versus explicitly-null versus value; updates always bind the intended key/tenant/version predicates. An affected-row mismatch is a concurrency result, not successful overwrite. Rust owns this policy over native query/execution capabilities; C# does not maintain a hidden query engine or identity map.

Transparent lazy loading, general graph persistence, arbitrary hooks, identity maps and full change tracking are not supplied merely by depending on SeaQuery. Add only required, separately designed policies. Static SeaORM Entity/ActiveModel/Relation behavior is a specialized native profile, with its own model build dependency and tests, not the default consumer obligation. SeaORM `save` choosing insert/update by whether keys are set is not an exists-based upsert guarantee.

## 8. Boundary errors and expert escape hatch

Shape mismatch, unsupported codec/operator/backend, overflow, invalid UTF-8, stale/mixed owner, disposed/poisoned builder, capacity exhaustion and database errors are distinct categories. Preserve structured provider information without exposing credentials or unrestricted SQL parameter logging. Failed operations must release or quarantine every owned native value/batch and must not overwrite an Unknown transaction outcome.

Expert parameterized SQL is explicitly named and audited, requires declared static result mapping and budgets, and remains executed in Rust. `AssertSqlSafe` is only a provenance assertion at that boundary, not validation of arbitrary user text. Ordinary Fluent failure never automatically falls back to raw SQL, managed providers, client evaluation or reflection/dynamic code.

## 9. Costs and verification

Compare direct native methods versus batched native commands and generated static fast paths. Count FFI/UTF-8/value copies, native AST/condition clones, descriptor/shape cache memory, body allocations, result bytes and DTO allocations. Cache keys include Engine ABI/profile, metadata content and query shape; eviction bounds bytes as well as entries and keeps in-use owners alive. No zero-allocation or throughput claim is made.

B09/B11 require direct-Rust versus C# differential SQL+parameters and real PG/SQLite result/error oracles. B10/B12 require generated and handwritten static descriptor/DTO parity plus actual Windows/Linux AOT. B13 requires dynamic typed composition without expression compilation, wrong-entity/value negatives, advanced-clause coverage and unsupported-backend rejection. B14 requires tenant/relationship/CAS tests and no accidental full ORM scope. B05/B06/B22 retain unknown commit, cancellation, early stream stop, decoder exception, race/fuzz/soak and bounded-resource obligations. The recovered probe is only the documented feasibility slice, not acceptance of this full contract.

## 10. Source-inspected native ORM capability boundary and concrete relation cases

The chosen ordinary native route is SeaQuery + SQLx with runtime metadata. SeaORM
public dynamic ModelType/FieldType decoding is a valid optional native capability;
it has an actual unchanged-code runtime-schema fixture, not merely an inference
from the library name. It does **not** automatically expose static EntityTrait,
ActiveModel hooks or LoaderTrait relationships for unknown schemas.

The inspected SeaORM loader extracts keys, builds native relation queries, collects
results and groups them by ValueTuple while preserving parent order. Its outer APIs
remain bounded by ModelTrait/EntityTrait associated types. For future bounded eager
loading, prefer generalizing those native algorithms through a controlled upstream
metadata extension; do not build a C# relationship engine. The initial ordinary
surface supports explicit native joins/projections and CAS changesets, with no
transparent lazy loading, hidden tracking or arbitrary graph persistence.

One-parent LoadRelatedAsync uses the separately registered relation owner, exact
parent key db-wire row and child projection ID to create one native child cursor
operation. Complete composite PK order, nullable FK compatibility, cache budgets,
source/engine retention and close/failure paths are fixed by the Public API §9.2.1;
the C# facade supplies static metadata and materializes bounded rows. Optional-FK
Fluent ON comparisons use AsNullable/AsNullableReference (unary opcode4) to retain
the original codec/value while widening result nullability. No COALESCE sentinel
or downward nullable projection is implicit.

`native_join_aggregate_matches_independent_sql_oracle` checks actual LEFT JOIN,
COUNT and SUM behavior against separately authored SQL. The changeset fixture
checks NotSet versus explicit NULL, tenant isolation and expected-version affected
rows. Existing R24 truth tables and native-slices negative controls remain separate
coverage. Every additional bound SeaQuery operation gets paired native-versus-ABI
SQL+ordered-values and PG/SQLite result/error tests; no complete upstream capability
coverage is claimed solely from these finite cases.

A native projection must validate exact shape before nullable decode. Missing or
duplicate columns are errors even when an upstream Option<T> decoder returns None.
This includes expert SQL, alias collisions, joined result nullability and descriptor
upgrade drift. Any poison/error cleanup follows the creating engine's owner rules;
transaction Unknown remains unchanged.

### Published research CI evidence

The [database CI confirmation](../../verification/database-completion/ci-confirmation.json) binds source `7ea84e11ee19e6dad4503a5872eb27c6c7f44e80` and run `43388468172` to actual Windows/Linux metadata/SQLite results (5/5 on each) and Linux PostgreSQL 18.0 results (6/6). Archived inputs/logs were checked byte-for-byte; Windows CRLF inputs remain separately identified. This confirms the finite native research oracles and leaves the specified C# product, TLS, concurrency, long-load and independent design-review obligations distinct.
