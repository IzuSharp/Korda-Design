# Current execution-path target — DB-Exec-02

## Recovered continuation and selected fixed-key path

The 2026-11-26 continuation starts from public
[`47fe650dfed5d7bba1c4d74c4a127c5d08b66082`](https://github.com/IzuSharp/Korda/commit/47fe650dfed5d7bba1c4d74c4a127c5d08b66082).
One-shot command completion is implemented there and existing CI passed. The
earlier completion proposal and candidate-specific measurements below retain
their original meaning. New final performance acceptance is still pending.

For `FindAsync`, select a Source-owned immutable fixed-key shape compiled once
from the model's ordered primary keys, with the existing terminal3 SQL and
Int64 LIMIT2. Reuse the C++ renderer, NativePlan parameter/projection validation,
lazy CursorPull channel, TypedStream single-or-default consumption and exact
Table.Row materializer. Repeated Find writes only a new independently owned
value frame. It must not reconstruct Fluent nodes or encode/replay the complete
command. Generated and handwritten table descriptors use the same private path.

The private shape uses model-key slots independent of the Source's public
ParameterRegistry. It must not consume public parameter identities, require the
public prepared capability, or turn arbitrary terminal3 plans into reusable
objects. Cache admission and hits retain the old logical node/parameter limits.
Both retained entry count and bytes are bounded; Source closure releases cache
ownership, while captured executions retain their own immutable references.
The exact Table/projection object identifies managed mapping: equal metadata
hashes do not imply equal materializers. No Session or physical statement is
stored in the cache. Key validation, caller-buffer snapshot, precancellation,
DDL/schema failure precedence, duplicate-row rejection and concurrent-session
behavior remain unchanged. Provider prepare/description remain per execution.

The cold private factory returns both the retained cache charge and the actual
fixed logical-query byte charge. These have different meanings. Before copying
the changing key values or returning asynchronous work, managed Find adds their
payload bytes to the fixed logical charge with checked bounds and preserves the
old synchronous rejection. Its exact exception type and category must come from
the original Find builder, which uses ExpressionValues and Binding.Value; a
WhereEqual helper can reject at a different boundary and is not that oracle.
At public 47fe650, QueryCommand.Capacity uses binding code11 (InvalidState),
whereas an individually oversized expression frame is an ArgumentException.
A native render check remains a second defense, including uncached oversized
shapes. Neither check may relax the
old Fluent node, parameter, byte or source-identity limits. The extra factory
output is a scalar in the same cold call, not another record or hot FFI call.

The isolated PostgreSQL commit-proof proposal is also selected for verification:
an already confirmed, healthy, nonblocking, non-pipeline physical connection in
PQTRANS_INTRANS, with no live statement and no savepoint, can supply the existing
pre-COMMIT state proof without SELECT1. Failure/unknown state retains the prior
probe/error path. Both post-COMMIT and safe-reuse confirmation obligations remain.
Source inspection alone does not establish the performance of either candidate.

The [continuation plan](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/plan.md)
owns implementation, exact package tests, source-bound local measurements and
the four final serial1800-second runs. No benchmark is added to CI.

## Prior selected target and evidence at its original checkpoint

Status: **cursor pull and direct final close measured; one-shot command
completion selected, with its implementation and final performance acceptance pending**. The owner resumed the complete database execution-path refactor on
2026-11-26 (Asia/Shanghai), continuing [Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34). This continuation starts from
[ada28311a384ad149fdc3f9db3b14473aedf0061](https://github.com/IzuSharp/Korda/commit/ada28311a384ad149fdc3f9db3b14473aedf0061).
The [actual cursor-path record](cursor-pull-execution.md) now binds public
[`933d16bf673dff5310db37cc444ba5019842d81d`](https://github.com/IzuSharp/Korda/commit/933d16bf673dff5310db37cc444ba5019842d81d),
including the accepted-cancellation correction, narrow request scheduling,
deleted unused retirement bridge, buffered row scope and primary-error
preservation. Its existing correctness/package CI passed. The current short
measurements bind the earlier public `31693e3` packages; they are not performance
credit for `933d16b` or an unbuilt successor. Final 1800-second credit remains
**0/4**. Earlier `0f3816c` and `bc6ba1a` evidence retains its original identities,
including the real cancellation failure at `bc6ba1a`.

The [one-shot command target](command-completion-execution.md) extends this
chain to Count/Any, nonreturning CRUD and transaction/savepoint controls. Current
`933d16b` still uses generic operations for those calls. Ordinary single-case
transaction tails and separate ABI counts select the new detached completion
work; a row-query-only zero-generic result does not establish this path is done.

The pre-refactor baseline remains
[f0078da720e07031bc56464995af6791c41aaae8](https://github.com/IzuSharp/Korda/commit/f0078da720e07031bc56464995af6791c41aaae8).
The earlier local candidate a27ff31 is publicly tree-identical to [c2df05ff01e90a92aa70884827735d7dfa1dbc3d](https://github.com/IzuSharp/Korda/commit/c2df05ff01e90a92aa70884827735d7dfa1dbc3d); its native
producer source dc82792 is publicly tree-identical to [1f93c5addeae962fee692f5d2a533c596efaa16c](https://github.com/IzuSharp/Korda/commit/1f93c5addeae962fee692f5d2a533c596efaa16c).
The intervening commits only fix a reference-consumer setup call and remove an
unused managed encoder wrapper; they do not change native producer inputs.
The [execution plan](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/execution-refactor/README.md)
owns exact before/candidate inputs, source review, measurements, deletion inventory
and completion gates. The earlier NWQC decision and final measurements below
remain historical; they do not constrain this task to keeping its Host internals.

Preserve developer Fluent usage, public validation/error/ownership behavior,
Native AOT, C++ execution and independent PostgreSQL/SQLite packages. Host layout,
command and parameter formats, ABI call granularity, batch production and managed
reading may change. The target is the lowest measured latency, CPU and memory for
the same SQL, typed parameters and complete business result. Source reuse must
follow a compatible responsibility and lifetime boundary.

## Target from driver to Fluent

| Boundary | Selected target | Existing guarantees |
| --- | --- | --- |
| Database driver | Reuse libpq 18.0 and sqlite3 3.51.3; keep provider conversion fallible | Real provider errors, connection identity, transaction state and explicit type-loss refusals |
| PostgreSQL command opening | Fresh unnamed Parse and Describe in one pipeline group and one Sync; validate the complete description | No Execute at open; fresh metadata, failure priority and protocol-safe cleanup |
| SQLite command opening | Prepare one statement, inspect its metadata and bind that same statement | No step at open; error order, borrowed-input lifetime, finalization on failure |
| Native execution parameters | Retain immutable ordered shape metadata; create one independently owned, once-validated typed argument set for each accepted execution | Snapshot values before retention; no mutable caller buffers or borrowed span across await |
| Native result production | Write converted values and offsets directly into one bounded owned batch arena | Complete shape and extent validation; field/row/byte limits; failure-atomic transfer |
| Native fetch scheduling | One cursor pull channel; first request opens and fetches, subsequent requests fetch directly | Complete open/shape validation precedes first Execute/step; each accepted request has one detached ready notification; final close joins every native tail |
| Native command completion — selected target | One typed request and independent result state for Count/Any, nonreturning CRUD, transactions/savepoints and child close; replace generic terminal/retirement polling on these formal entries | Existing business functions and error priority; input accessors and Source reservation released before ready; separate notification fences preserve unknown-acceptance and Source join proof; implementation acceptance pending |
| Managed batch and row access | One reusable channel controller and stable scoped native batch owner; bind a validated layout once and directly construct DTOs | No reader escapes its generation/lease; missing/duplicate/type/NULL/UTF-8/precision errors remain explicit |
| Prepared Fluent | Reuse compiled SQL, parameter ordinals/codecs and projection; repeated execution changes independently captured values | Source/profile/generation checks; independently disposable plan; concurrent executions use independent owners |
| Dynamic Fluent | Complete typed composition before submission; compile one validated representation directly if the command gate proves equivalence | Immediate recoverable builder checks, native capabilities, clones/CTEs, literal budgets and nonsealing ToSql |
| Retirement | Keep the actual provider, callback, batch and connection obligations accounted until they finish | Cancellation or public completion alone cannot free owners or return an unsafe connection |

Read the chain in reverse for a consumer call: Fluent selects the complete shape;
Binding snapshots and submits it or a prepared plan; Host admits one execution
with ordered typed values; libpq/sqlite3 supplies bounded results; the batch lease
retains native storage while the generated reader constructs the DTO. A complete
command is distinct from registration, fetch, cancel and disposal operations.
Changing their granularity requires the same observable lifecycle.

### One-shot commands and scalar results

The current [`DbOperation::run/complete`](https://github.com/IzuSharp/Korda/blob/933d16bf673dff5310db37cc444ba5019842d81d/native/cpp/src/host.cpp)
delivers a terminal callback before its generic work/callback leases and local
action capture have all retired. A later managed Pending retirement may wait
for the existing coordinator tick. The selected replacement reuses the
[existing capture and business adapters](https://github.com/IzuSharp/Korda/blob/933d16bf673dff5310db37cc444ba5019842d81d/native/cpp/src/host_abi.cpp),
then transfers a count, owner or existing snapshot buffer through a separate
ready state. It does not move the old terminal callback to a different line or
declare terminal delivery to be native quietness.

The [detailed target](command-completion-execution.md) fixes the 48-byte typed
request, 32-byte typed result, four private exports, existing owner/buffer
release and cold generic proof. It also defines cancellation, accepted queue
failure, primary/cleanup error retention, unclaimed owner cleanup and the
independent request/Source notification fences. Existing transaction Unknown
results must retain their early decision boundary while separately owned
cleanup continues. A new scalar count path uses provider conversion directly,
without encoding and reparsing a row batch; complete shape, cardinality,
NULL/width, late-error and retirement checks remain required. None of these
prospective guarantees is counted as an executed product test.

### PostgreSQL: one preparation group, fresh metadata

At PostgreSQL 18.0
[postgres.c](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/tcop/postgres.c),
`exec_parse_message`, `exec_bind_message`, `exec_execute_message` and
`exec_describe_statement_message` separate parsing/description from execution.
The matching
[libpq fe-exec.c](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/interfaces/libpq/fe-exec.c)
allows prepare and describe to be queued in pipeline mode before the group's
Sync. The ordinary send helpers add their own Sync outside pipeline mode.

The selected opening path uses fresh unnamed Parse + Describe + one Sync.
It must consume every result and the pipeline synchronization boundary before
leaving pipeline mode. A null `PQgetResult` between commands is not proof the
whole group is drained. Parse/description errors, aborted dependent commands,
transport errors, cancellation and cleanup retain their own classification.
Only the first permitted fetch dispatches Bind/Execute; receiving a cursor must
not advance a volatile function, write-returning statement or row iterator
earlier than the current public behavior.

Cross-execution physical statement and column-description caching is **not selected**.
`exec_describe_statement_message` calls `CachedPlanGetTargetList`; in
[plancache.c](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/utils/cache/plancache.c),
`RevalidateCachedQuery` can reject a changed fixed result type with 0A000.
Describing a cached statement again therefore does not restore fresh-Parse
behavior after external DDL, and an error can change an enclosing transaction's
state. A SQL-only key, cached RowDescription or automatic replay is not an
acceptable substitute. Keep fresh unnamed parsing for this candidate.

Npgsql 11.0.0
[NpgsqlCommand](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlCommand.cs)
and [NpgsqlDataReader](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlDataReader.cs)
are the send/wait/read references. Its
[statement manager](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/PreparedStatementManager.cs)
owns statements on a physical connector. Reuse the scheduling principles without
claiming that Npgsql's physical caching, cancellation or ExecuteReader timing is
already Korda's contract.

Candidate B removes the separate successful-prepare confirmation: the grouped
prepare has already consumed its pipeline synchronization boundary and exited
pipeline mode. It also removes a stream-close Sync after a **proven natural EOF**.
The proof belongs to this execution on this physical connection: its non-pipeline
Execute results have been consumed through terminal `PQgetResult == nullptr`,
and the connection is healthy, nonblocking, outside pipeline mode and in a known
transaction state. Close rechecks these conditions before reusing that proof.
A full batch without observed EOF has no such proof. Early stop, metadata-only
close, errors/unread results, transaction completion, pool check-in and next
acquisition retain their appropriate confirmation or rejection behavior.

The changed tests inject failures at the terminal reply and reuse boundaries,
including truncated ReadyForQuery and a backend killed after observed EOF.
`postgres_sync_tests.cpp` retains original SQLSTATE priority, Unknown commit
outcomes, cleanup snapshots and charged connection lifetime. Successful libpq
send-call counters are not FFI counts, protocol-message counts, socket polls or
measured RTTs. Plan records source-derived message groups and observed counters
separately from latency.

### SQLite: one statement within an execution

The references are Microsoft.Data.Sqlite 11.0.0
[SqliteCommand](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteCommand.cs),
[SqliteDataReader](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteDataReader.cs),
[SqliteDataRecord](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteDataRecord.cs)
and SQLite 3.51.3
[prepare.c](https://github.com/sqlite/sqlite/blob/a5333afb9ad1aa473f8963b92caeaa955f47dc74/src/prepare.c) /
[vdbeapi.c](https://github.com/sqlite/sqlite/blob/a5333afb9ad1aa473f8963b92caeaa955f47dc74/src/vdbeapi.c).

Prepare once for the same command, inspect columns on that statement, then bind
the admitted typed arguments and retain it for fetch. Eliminate a separate
description statement followed by another prepare for execution. Preserve the
current precedence of SQL preparation errors, shape refusals and parameter
conversion/physical-width errors. Opening a cursor must not call sqlite3_step;
Microsoft.Data.Sqlite's ExecuteReader/NextResult stepping cannot be copied
unchanged into that boundary.

Cross-execution reset/clear-bindings reuse is not part of the initial selected
path. SQLite's automatic schema reprepare does not establish Korda's metadata,
error-timing and owner equivalence. Any later cache needs a bounded connection
owner, verified reset outcome, cleared bindings, schema invalidation, active
reader exclusion and exact finalization/close behavior. Until demonstrated,
finalize the statement on completion or failure.

### Parameters: remove a round trip through NWDB

A prepared shape knows parameter identity, order, codec/nullability and provider
profile. Resolve stable identity-to-ordinal metadata once. Each execution still
captures and checks its supplied values, retaining existing missing/extra/foreign
parameter errors and conversion order. Structural validation once does not
remove fallible provider-specific encoding or boundary safety checks.

The selected native path passes its validated typed argument owner directly to
provider binding. Delete the second `NativePlan::render` NWDB serialization and
the following Host parse/decode on this production route. Do not reduce copies
by retaining mutable application arrays, aliasing two concurrent executions or
moving a borrowed pointer across await. Reuse stable prepared layout; measure
cold preparation and per-execution snapshots separately.

### Results: direct arena construction and one layout decision

Candidate B already borrows native batch memory through HostStreamTransport and
its retained SafeHandle/row lease. There is no proposed removal of a whole-batch
native-to-managed copy that this starting path does not perform. The current
replacement keeps scoped native borrowing and removes the per-batch wrapper and
generic operation lifetime through the cursor channel described below.

Rewrite native per-cell owning byte vectors, row staging and repeated batch
parsing into a checked writer for the final bounded batch arena. Validate the
complete provider column shape before interpreting values. Conversion writes
directly into reserved arena extents; invalid UTF-8, narrowing, numeric precision,
NULL, large-field and aggregate-budget errors remain explicit. Publish a batch
only after its complete frame is valid; failure must leave no transferable
partial result or uncharged owner.

On the managed side, match the accepted layout once per result and validate each
new batch's frame/extents once. Typed readers then use those established slots
within the active lease, without repeating schema matching and codec lookup for
every cell. Data-dependent validation and lifetime checks stay where required.
A user constructor or mapper failure releases the batch and joins the existing
cursor cleanup while preserving any transaction outcome.

Dapper.AOT 1.1.0
[CommandT.Query.cs](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandT.Query.cs)
tokenizes the reader layout before its per-row typed Read loop. The upstream
[Query generated fixture](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/test/Dapper.AOT.Test/Interceptors/Query.output.cs)
and [CacheCommand generated fixture](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/test/Dapper.AOT.Test/Interceptors/CacheCommand.output.cs)
show typed parameter construction/value updates and row tokens. The actual
pinned reference consumers have also been generated and inspected. The two-column
same-SQL `DapperQueryPhases` consumer uses two generated command-factory instances,
two ordinal Int64 parameter updates and `RowFactory0`: Tokenize matches Id/Note
once, then Read uses typed accessors/IsDBNull and directly constructs `PhaseRow`.
The mixed workload is a separate nine-column Order reader with decimal/JSON
handlers; its generated `RowFactory3` must not be substituted as evidence for the
two-column comparison. Plan retains actual generated bytes and hashes for both.
Business DTO/list/string/JSON allocations remain business output.

An EOF marker may eliminate an empty fetch only if completion is already known.
Do not step an extra row merely to set the marker, suppress a late provider error,
release a live batch or turn a cancellation request into a fabricated terminal
result. Candidate B transfers owner, borrowed bytes and observed EOF in the
additive `db.result.batch.v1` result record; the frozen ABI and NWDB reserved bits
stay unchanged. Once the final batch is fully consumed and released, a synchronous
`nw_db_cursor_check_read_admission_v1` preserves source poison, Session closure
and active-reader admission checks before returning false. This is one FFI call;
it creates no operation or buffer and executes no SQL or protocol send. It avoids
an empty fetch without suppressing the original errors. Transaction disposal
waiting for an existing cursor does not forbid that reader from finishing.
Measure wakeup, dispatch, retirement and mapping separately before attributing
read-complete latency to a timer or mapper. This paragraph records B's measured
implementation. Its unpublished bit-27 extension is replaced by the channel
contract below; it is not an additional compatibility obligation on the new path.

### Cursor pull channel: remove the per-batch operation lifetime

The paired C1/R4/R1ms experiments retained B's native images and varied bounded
queued retirement retries and the database coordinator interval. Mixed throughput
improved, but repeated 1000-row completion samples still varied materially. The
[raw decision evidence](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/execution-refactor/retirement-experiments/README.md)
does not establish that every slow sample is a timer wait. It justifies testing a
different lifetime boundary instead of accepting a shorter polling interval as
the complete refactor. None of those experiments establishes a 0 B framework path.

NpgsqlDataReader and Microsoft.Data.SqliteDataReader own a reader across its row
loop. Dapper.AOT tokenizes that reader once and constructs each DTO directly. The
implemented adaptation is one private C++ pull channel per typed cursor, retaining
the same driver, protocol, shape and result obligations. Public C# Fluent does
not expose HostStreamBatch or the internal IStreamBatch interfaces. In particular,
public QueryCursor<TEntity> is a pagination value, not a raw result-buffer API.
Do not retain an unused raw fallback to preserve a public API that does not exist.

The first MoveNext creates a lazy channel from the admitted Session, plan
or complete SQL, and independently captured parameter/options state. Creation
validates and captures its inputs without executing SQL. The first accepted
request uses the shared existing execution/open helpers, validates the complete
column shape, then performs a second logical Source/token/Session/close/read
admission before the first bounded fetch. This fuses private managed scheduling;
it does not send Execute before metadata validation or change the standalone
open-without-Execute ABI. PostgreSQL still needs its preparation/description and
first Execute response groups. SQLite still prepares/inspects/binds before step.

Each request carries a generation, row/byte bounds and a ready-only callback
record. There is at most one unconsumed request/result. Native rejection creates
no callback obligation; uncertain admission must quarantine its roots. Before
publishing readiness, the worker must finish every provider access and destroy
the CursorReadAdmission and Session/fetch guards. Under the channel mutex it
stores the complete owned Buffer or structured error and moves out and clears
that generation's callback record. Each accepted generation notifies exactly
once. After notification, independent native worker/callback tickets may remain,
but their tails cannot access the consumed cookie or mutate any later generation.

The synchronous take checks the exact generation and transfers the Buffer,
borrowed view and observed EOF once. A failed take retains structured SQLSTATE,
provider and cleanup errors for the error take. Read-admission checking at known
EOF remains explicit. A lightweight stop call provides cancellation/Dispose
control without constructing another operation. The measured `0f3816c` final
close uses zero or one generic operation. DB-Exec-03 replaces the normal close
with an independent generation-0 ready/take after the old fetch tickets and
cursor drain/discard obligations finish. Its own notification tail has separate
channel and Source fences. Public generic join and snapshots include that tail
so a cold fallback can prove an uncertain close cookie safe; direct final-close
work excludes its own tail to avoid self-wait. SafeHandle release remains nonblocking;
abandoning a managed cursor does not erase its native cleanup ledger.

The managed controller is reusable, but its GCHandle root, coordinator reservation
and per-request cancellation registration cover active setup/request obligations.
An idle controller has no permanent GCHandle or reserved slot. The enumerator's
separate cancellation registration remains during mapping and between refills,
then drains during stream cleanup. Before managed publication,
request setup has returned, actual controls and managed callback accesses are
zero, cancellation registration has drained, and the batch/error is safely taken.
The native detached one-shot notification contract then proves that this request's
cookie will never be used again. This new private readiness boundary does not
redefine generic AsyncSnapshot.NativeQuiet or publish RetiredValueTask early.
Per-cursor coordinator scheduling bits survive request reset, so an old queued
execution cannot clear a later generation's scheduling obligation.

Use a private ValueTask transport and one stable scoped batch owner. A generation
is readable only through a synchronous Span lease with full codec, ordinal,
projection and extent checks. Release invalidates new reads immediately; a reader
that already holds its lease keeps the physical native buffer until its final
access. The next batch cannot attach while that pointer is still retained. Do not
reopen a closed SafeHandle, rebind a MemoryManager, or expose borrowed Memory.
Public MoveNext keeps its existing pooled async behavior; the internal fetch
ValueTask does not escape and is consumed before the controller is reset.

The unpublished `db.result.batch.v1` bit 27 and its two exports are replaced by
`db.cursor.pull.v1`; preserve the frozen 42 declarations, the bit-26 complete
query command and original take-buffer API. Both independent package
capability/export inventories require the same eight fetch entries plus the two
DB-Exec-03 final-close entries. Superseded
HostStreamBatch, NativeHost.TakeBatch, Source.StartRetiredValueTask and raw
streaming interfaces are deleted after their production callers move to the
scoped channel. Keep general Interop async operations for their remaining Task
users and conformance tests.

A deterministic test must hold the independent native callback-return/worker tail
after readiness. Taking the result and requesting the next generation must work,
while final channel close remains pending until that tail exits. Also prove
rejected-request compensation, generation mismatch, cancellation and abandonment,
held-reader release, mapper failure with cleanup attachment, source poison and
transaction-disposal behavior. Public package consumers must establish that the
formal entry uses the channel and that the deleted path has no callers. This is an
implemented source candidate; its final integrated tests, allocation, FFI and
latency measurements require their own receipts. The
[actual path and ownership record](cursor-pull-execution.md) lists the fetch and
final-close exports, precise readiness/retirement proofs, cold generic fallback,
development test results and every retained wait/copy/format awaiting cost
attribution. It preserves the first exact-one-close test failure for its original
checkpoint. The DB-Exec-03 normal-path oracle is zero generic operations through
final close. Its development two-provider AOT matrix has passed that exact count;
public-package FFI/correctness and local timing receipts remain separate gates
rather than credit from the old snapshot race.

### Complete-command design gate

The prior NWQC command is an input implementation, not a mandatory architecture.
Compare a directly validated flat expression/query representation with encoding
an operation tape and replaying it into another native builder. Account for
construction, serialization, parse, node ownership, compilation and repeated
execution separately. The goal is one authoritative compiled representation
after the boundary, with no reconstruction that protects no remaining contract.

Candidate B retains NWQC as the single bounded cross-language command encoding
but removes its redundant replay adaptation. Native compilation consumes original
operand spans once, with a local-slot view; `command_clause`/`command_fields`,
rewritten copies and a second control-frame schema parse are deleted. Fresh,
unpublished command arenas use in-place `Impl::Edit`, replacing a whole QueryData
copy per clause. A failed private edit discards the poisoned arena and its shadow
parameter registry. Existing per-node ABI callers keep copy-on-success behavior;
private mode is reset before completed roots/clones escape. Immutable imported
block snapshots still protect query ownership. This is a retained encoded graph,
not a claim of zero parsing, zero construction or zero native allocation. The
three-lane public phase measurement must report its remaining construction cost.

The replacement preserves all 22 clause semantics, ordered
parameters, clone/snapshot/CTE ownership and scalar-origin/literal budgets,
unsupported-provider refusals, malformed-frame rejection, error precedence,
recoverable mutation and ToSql's diagnostic/nonsealing behavior. The compiler
must preserve authoritative C++ dialect/relational semantics and native owner
validation. No unmanaged pointer is accepted from command bytes.

The gate must either switch the public entry to a direct compiler path and delete
the replaced replay/wrappers, or document a concrete contract and measured reason
for each retained stage. Merely reducing allocations inside the current serializer
does not complete this gate. Preserve frozen public/C ABI compatibility through
explicitly scoped adapters where required; do not keep an unobserved fallback
that causes consumers to continue using the old path.

[SqlSugar's fixed query helper](https://github.com/DotNetNext/SqlSugar/blob/06789315fcea02f17901506b0cbf670a25192083/Src/Asp.NetCore2/SqlSugar/Abstract/QueryableProvider/QueryableHelper.cs)
is the complete-SQL/parameter construction reference, not a proposal for a
reflection mapper. [.NET 11 DbCommand](https://github.com/dotnet/runtime/blob/deae2e32bf0e018e09d64597b7c59b62b73bb3ce/src/libraries/System.Data.Common/src/System/Data/Common/DbCommand.cs)
delegates execution to providers; its base asynchronous wrappers do not prove
Npgsql or SQLite asynchronous I/O behavior.

## Verification and completion boundary

First prove one primary-key result and 100 DTOs through the public package entry,
then 1000-row batching, complex Fluent queries, transactions and streams.
Preserve actual open-time side effects, slow-consumer/backpressure, early stop,
cancellation, failed transaction and connection return. Existing native fault
oracles and managed lifetime tests are mapped in
[ported-tests.md](https://github.com/IzuSharp/Korda/blob/f0078da720e07031bc56464995af6791c41aaae8/native/cpp/tests/ported-tests.md);
historical experiments and inspected tests are not this candidate's execution.

Use the same local Linux host and matching before/candidate/reference inputs.
Record ABI-call counts, business SQL executions and actual required protocol
waits independently. Reuse the three same-Host routes and Dapper.AOT plus the
corresponding driver. After short calibration, run four serial uninterrupted
1800-second candidate/reference cells across the two databases. Offered-load and
closed-loop metrics must remain distinct; retain failures and actual rejection
counts. Full process allocations/GC and native costs cannot be replaced by a
zero in-row diagnostic. The warm framework path targets 0 B additional managed
allocation with separately observed operation, refill and concurrency coverage.
Public Task/one-shot lifetime costs are explicit residuals
when they remain, not evidence for whole-query zero allocation.

CI retains its existing dependency-selected build/correctness checks and
independent provider packages; all benchmarks, profiling and pressure run locally.
No new performance workflow or hidden benchmark action is selected. Complete
refactoring requires the full layer/deletion review, external package correctness,
reproducible measured evidence, normal reviewed delivery and an explicit stopping
basis. The source review and this target alone accept none of those outcomes.

---

## Historical candidate decision — DB-Perf-01 at f0078da7

The following describes the preceding candidate and its original stopping
instruction. It is preserved for comparison; DB-Exec-02 above governs the newly
authorized execution-path refactor.

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

**Implemented follow-up; measured allocation regression remains:** an exclusively admitted
command with one root, no dependencies and exactly one tape reference per
uncaptured origin uses a direct serializer to avoid generic temporary traversal
and indexing collections. Sealing also requires an empty origin-publication gate
set. The complete encoded frame and its single typed root-model dependency borrow
bounded stack storage only during the synchronous native call; no span survives
that call. A complete frame above 4096 bytes falls back to the existing generic
encoder after the same budget checks. `CreateCte`, shared or captured origins,
snapshots and imports retain the generic path. A captured origin remains generic
even after its reference count returns to one or its public owner is disposed.

The NWQC frame, dense scalar origin ordinals, typed sidecar, limits, source checks
and lifetime/error behavior are unchanged by this slice. Native code and callback
timing are unchanged. Local differential cases cover 4096/4097-byte boundaries,
private/shared command-byte parity, captured-owner lifetime and quota recovery;
they do not measure the final comparison. This implementation follows the
[published first SQLite observation](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/query-optimization/phase-sqlite-r0-034b40ea/README.md)
and preceding selection. The [implementation checkpoint](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/query-optimization/serializer-f0078da7/README.md)
binds source, local correctness and ordinary CI; the [final comparison record](https://github.com/IzuSharp/Plan/blob/bfe4aa3f074789dfac046412eff37fe6ba58b0f7/ledger/evidence/batches/DB-Perf-01/query-optimization/final-f0078da7/README.md)
owns measured outcomes. Across 18 phase processes, ordinary Fluent allocation
remains approximately 25.31% above recovered on both providers. Lower allocation
relative to the earliest baseline is a cumulative observation, not isolated proof
of this slice. Short-load memory/GC and Dapper.AOT gaps remain. All four final local 1800-second cells are validated, as is the unchanged 16-app/926-file post-run freeze. Candidate allocation is 4.7813×/5.2268× Dapper.AOT on SQLite/PostgreSQL, throughput is 3.5762%/12.4863%, and p99 is 44.8×/8.6244×. The final full archive remains local-only after upload rejection; public Plan summaries do not claim to expose all final histograms or traces. Record these gaps and stop without merging, as instructed by the owner.
Static entity/DTO metadata is generated. Arbitrary build-time Fluent SQL and
connection-level physical statement reuse remain unimplemented; neither follows
from the complete-command contract.

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
