# Cursor pull execution and scoped rows — DB-Exec-02

Status: **published source candidate; final package and performance acceptance
pending**. This continuation replaces the per-batch generic operation selected
for replacement in [the execution target](query-semantics.md). The source links
below bind the published source candidate
[`0f3816c4006488821f40afde91bbbd717d57ccd6`](https://github.com/IzuSharp/Korda/commit/0f3816c4006488821f40afde91bbbd717d57ccd6).
Its tree is `9935773d28b3043618285cf0ecd5c476539b2f8c`, matching local
`6da0074513d9cb1ff9f13748b058211ec706f230`. This fixes the reviewed source
input. Plan must separately bind its native images, packages, generated consumers
and measurements; source publication does not establish their acceptance.
Earlier candidate B and
retirement-interval experiments retain their own identities and results.

The public Fluent calls, result and error behavior, Native AOT requirement,
C++ execution and independently installable PostgreSQL/SQLite packages remain.
The frozen database v1 declarations and fingerprint remain byte-compatible.
The private channel changes who schedules and owns a result, not when a SQL
side effect is permitted or when a connection is safe to return.

## Actual consumer-to-driver path

| Step | Current implementation | Responsibility and retained boundary |
| --- | --- | --- |
| Compose or reuse a query | `QueryContext.Stream` / `PreparedQuery<T>.Stream` in [Query.Fluent][fluent] and [Terminals][terminals] | Ordinary Fluent submits one complete NWQC graph; C++ compiles its operand spans directly. Warm `.Prepare()` reuses SQL, immutable parameter ordinals/codecs and projection layout. Values remain independently captured per execution. |
| Open the private transport | `DataSession.OpenPlanStreamAsync`, `OpenSqlStream`, `InsertReturningAsync`, `LoadRelatedAsync` in [DataSession][session] and `Orm.Relations` | The start delegate returns `ValueTask<IStreamTransport>`. Ordinary/prepared/full-SQL, returning mutation and relation paths create their appropriate lazy channel directly. There is no intermediate generic open operation or from-cursor adapter on these paths. |
| Admit and capture | `capture_execution`, `capture_relation`, `capture_mutation`, `CursorPull::create` in [Host ABI][abi] and [Host][host] | Reuse the same plan, identity, capability, parameter, timeout and Session admission helpers as the retained ABI. Creation owns the Session command gate and immutable execution inputs; it performs no provider open/step/Execute. |
| Request the first batch | `HostStreamTransport.FetchAsync` → `HostPullController.Request` → `nw_db_cursor_pull_request_v1` | One reusable managed controller submits generation 1. The native worker opens the cursor, validates the entire column shape and rechecks Source, Session, cancellation and channel closure before fetching. This second admission preserves the former open/fetch side-effect boundary. |
| Send and read | `Session::open_cursor`, `Cursor::fetch`, `ProviderConnection::prepare`, `ProviderStatement::append_next` in [Host][host] and [provider][provider] | PostgreSQL sends fresh Parse+Describe+Sync, validates their replies, then permits Bind/Execute. SQLite prepares/inspects/binds the same statement before step. Later requests read the existing statement; requesting another batch does not execute the business SQL again. |
| Publish one batch | `BatchWriter`, `CursorPull::complete/take`, `NativeHost.TakePullBatch` in [contracts][contracts], [Host][host] and [NativeHost][managed-native] | A complete bounded arena is transferred as one native owner plus immutable view and observed EOF. Readiness detaches the callback. Take does not poll generic operation retirement or wait for an earlier worker tail. |
| Materialize rows | `ScopedStreamBatch`, `RowBatchLease`, `TypedStream`, `Projection<T>.ReadBatch`, `RowReader` in [stream ownership][batch], [TypedStream][stream] and [Rows][rows] | Validate each frame once, bind the projection proof to its exact fields/expectation, then invoke the existing static generated or handwritten constructor under one synchronous span lease. Each field still enforces ordinal, codec, NULL and value conversion semantics. |
| Release and reuse | `Dispose`, `check_read`, `stop`, `CloseController`, `CursorPull::join` | Releasing a batch invalidates new reads and defers physical buffer release until held reads finish. Final close joins channel tails and provider cleanup; a completed snapshot can avoid creating a generic close operation. |

Count/nonreturning commands, transaction controls, pool/session acquisition and
other remaining Task users retain generic Interop async operations. The scoped
channel is the production typed-result route; frozen-ABI compatibility tests may
call the original operation/take-buffer functions directly.

## Eight negotiated entries and ownership

Capability bit 27 is now `db.cursor.pull.v1`. Its
[C header][header] and [manifest][manifest] replace the unpublished
`db.result.batch.v1` extension. Both provider inventories must require the same
eight entries; the separate bit-26 query-command extension is unchanged.

| Entry | Input/result and exact role |
| --- | --- |
| `nw_db_cursor_pull_create_v1` | Session, plan and argument view → lazy channel; captures the ordinary/prepared/full-SQL execution. |
| `nw_db_cursor_pull_relation_create_v1` | Session, relation, key view and projection → lazy channel through the existing relation capture helpers. |
| `nw_db_cursor_pull_mutation_create_v1` | Session, model, mutation kind and payload view → lazy channel for a returning mutation through the existing mutation helpers. |
| `nw_db_cursor_pull_request_v1` | Channel, nonzero next generation, row/byte limits and callback record. `NW_OK` accepts exactly one notification obligation; non-OK rejects without any callback. |
| `nw_db_cursor_pull_take_v1` | Exact outstanding generation → one owned batch record. Before readiness it returns `NW_PENDING`; wrong/consumed generations reject. A terminal failure retains the rich error for the next entry. |
| `nw_db_cursor_pull_take_error_v1` | Exact failed generation → one existing provider/cleanup/bulk snapshot buffer; consumes that error once. |
| `nw_db_cursor_pull_check_read_v1` | After releasing an observed-EOF batch, rechecks Source poison, Session/channel closure and cursor read admission before returning false. It sends no SQL and creates no operation or result buffer. |
| `nw_db_cursor_pull_stop_v1` | Closes read admission and requests current cancellation/provider cleanup while idle or active. It does not create an operation or certify retirement. |

On Linux x64, the callback record is 24 bytes: `struct_size`, zero `reserved`,
context and a Cdecl `ready(context, uint64 generation)`. The result record is 32
bytes: owner at 0, `nw_bytes_view_v1` at 8, `known_end` at 24 and zero reserved at
28. `known_end` is only 0 or 1. No borrowed view escapes its owned buffer lifetime.
The creating module's existing `nw_db_buffer_release_v1` releases that owner.

`NativeHost.TakePullBatch` checks owner, flags, extent and minimum header before
`ScopedStreamBatch.Attach`. Successful attachment accepts the owner; rejection
leaves compensation with the caller. No per-batch SafeHandle or MemoryManager is
created. Error snapshots remain a cold owned-buffer path and preserve the main
status, provider code, correlation and any cleanup diagnostic. A failed error
take cannot justify reuse or invent a successful cleanup receipt.

The channel supports the existing `nw_db_close_create_v1`, `nw_db_snapshot_v1`
and `nw_db_owner_release_v1`. The managed `Cursor` owner tag is an internal
SafeHandle tag; native close/snapshot identify their own variant. This does not
change frozen take-owner kind numbers. Diagnostic slot 8 counts live channels;
slots 0–5 and SQL/protocol counters 6–7 retain their meanings.

## Readiness and final retirement are distinct proofs

Only one request/result may be outstanding. Native generations start at 1 and
increase exactly by one after acceptance. Limits, callback layout, generation,
Source/Session state and live-batch exclusion are checked before accepting a
request. Allocation or queue rejection before acceptance creates no callback
obligation. A queue failure after acceptance must complete that generation with
an error and one notification. The [cleanup containment follow-up][cleanup-seal]
handles pre-notification cleanup failures before clearing the callback record or
publishing ready. It preserves the original business error and attaches a shared
cleanup error initialized before the Source can accept any operation, including
the frozen generic cursor entry. Unknown cursor
retirement poisons Source admission, excludes its connection from reuse and
retains its bounded accessor without allocating a quarantine container entry.
Its snapshot remains failed and `released=false`; a cleanup-post failure cannot
escape the read-guard destructor. Failed Session/transaction cleanup launches
retain compensation and retry behavior. The corresponding isolated native tests
have passed; the final integrated package execution remains a separate gate.

The same error priority also applies inside `Session::open_cursor`: a failed
prepare/description remains primary even if finishing its gate then fails to
launch parent cleanup. The helper retains the original exception, attaches a
cleanup error to an existing native `Error`, and preserves its status, code and
correlation. An allocation failure or unexpected exception retains its respective
classification. The prior implementation failed the deterministic invalid-SQL
plus closing-transaction/worker-launch case. The local failed and repaired runs
remain distinct inputs for Plan's candidate receipts.

Before readiness, the worker has finished provider accesses and destroyed its
`CursorReadAdmission` and local fetch guards. Under the channel mutex it stores
the complete buffer/error, detaches and clears the callback record, then invokes
that callback once. After the invocation, the old worker cannot access the
cookie or mutate a later generation. Independent native tickets may still exist
after that invocation. They retain their own completion ledger; readiness is
not a claim that their thread or destructor has finished.

The managed [controller][controller] owns one reusable
`ManualResetValueTaskSourceCore<ScopedStreamBatch>` and coordinator work item.
Its GCHandle, coordinator reservation and per-request cancellation registration
cover active setup/request obligations only. Before publishing a ValueTask:

1. Setup has returned, so no new request or registration can still be installed.
2. The accepted ready callback is observed, and managed callback accesses and
   native controls are zero under the same gate.
3. The cancellation registration has actually drained, including a callback
   invoked inline during registration.
4. Result/error take has settled and any refused attachment has compensated its
   raw owner. A local failure after native acceptance still waits for readiness
   or a genuine final-close proof.
5. The GCHandle and coordinator reservation are released before publication.

The ValueTask is consumed once; the controller cannot reset before that result
is consumed and the stable batch can accept another generation. Coordinator
scheduling flags belong to the controller, not to one request, so an old queued
execution cannot erase a later request's signal. An uncertain native call or a
throwing registration without a drainable handle closes Source admission and
retains unknown obligations instead of declaring them quiet.

A setup failure before coordinator reservation has no timer retry slot. If it
overlaps a held stop control, the final stop/close proof resumes that local drain
synchronously outside the controller gate instead of relying on a new scheduler
offer. This also covers a stop failure whose final native close later succeeds.
A failed final close retains unknown obligations; it does not recursively retry
or publish a fabricated safety proof. The normal reserved request still uses the
shared coordinator.

The ordinary `TypedStream.Enumerator` cancellation registration has a different
lifetime: it remains during mapping and between batch refills so cancellation can
stop a reader at those points, then drains during stream cleanup. Thus “no idle
self-root” refers to the pull controller's GCHandle/reserved slot; it does not
claim that a live cancellable enumeration has no registration with its token.

`ScopedStreamBatch.Dispose` closes new reads immediately. A held
`ScopedBatchRead` keeps the physical immutable buffer until its final access;
`Attach` rejects while any old generation or release is still active. A new
generation never reopens a SafeHandle or rebinds an escaped `Memory<byte>`.
`RowBatchLease.Materialize` holds its span scope throughout the user constructor
or mapper. Disposing the stream during that callback cannot free the bytes it
already holds, and subsequent reads through the invalidated row lease reject.

Final close first stops the channel, waits for every channel worker ticket and
joins the actual cursor/provider cleanup. `Source::join` waits its pending work
and independent pull-worker fence before stopping the pools. A worker drops its
channel/Source captures and returns its Source reservation before publishing its
independent retirement tickets. Session closure also stops weakly tracked lazy
channels, including one that never opened a provider cursor.

There are **zero or one generic close operations per normal typed query**.
`CursorPull::snapshot` requires `closing`, no running request, no retained gate
and a completed channel fence; for an opened cursor its own cleanup snapshot must
also report actual retirement. If that proof already exists when
`CloseController.Request` reads it, owner release is immediate. Otherwise one
generic close joins the remaining work. A “one close operation exactly” assertion
is incorrect because it depends on whether cleanup wins that race. Neither path
permits a per-batch generic operation.

## Remaining waits, copies and formats

The table records current costs to measure, not presumed savings. **Pending**
means this assembled candidate lacks a separately attributed cost measurement.
Historical B or retry-interval samples cannot fill that cell. Business result
allocation and whole-process GC remain separately reported.

| Wait, copy or representation | Why it remains / corresponding oracle | Current candidate cost |
| --- | --- | --- |
| Bounded NWQC graph and owner sidecar | One language-boundary representation preserves 22 clauses, topology, typed owner validation and budgets. Native operand spans compile directly; the deleted replay adapter did not protect an extra contract. Query.Binding/Fluent command, clone, CTE and failure-atomicity tests. | Pending: composition, encoding, validation and compilation separately. |
| Immutable query blocks, literals and captured parameters | Snapshots preserve caller mutation, clone/CTE ownership, concurrent prepared execution and exact missing/extra/foreign parameter errors. Binding/Fluent snapshot and prepared tests. | Pending; values and immutable-block copies remain. |
| One input parameter frame and owned native typed values | Validate the FFI frame once against immutable ordinals/codecs, then own each execution's values beyond the call. `NativePlan::render` → `SqlPlan::rendered` moves typed values; its former second NWDB encode/Host decode is deleted. Host physical-width and error-order tests. | Pending: snapshot/validation/provider encoding. |
| Raw-SQL parameter frame retention | `SqlPlan::capture_parameters` retains the original frame and typed values for raw-command equality/single-submission checks; this is distinct from the removed Fluent re-encoding. Raw SQL mutation/submit tests. | Pending; retained bytes are an explicit residual. |
| Control/metadata records, canonical names and SQL text owners | Registration, raw commands, relations/mutations, diagnostics and cold error snapshots retain their existing bounded formats. Compiled SQL/result expectations and per-execution SQL owners cross different lifetimes; schema hashes and native ownership remain explicit. Registry, malformed-control, SQL rendering and failure snapshot tests. | Pending: cold registration versus repeated command copies separately. |
| Pool admission and per-Session command exclusion | Bounded waiters and a single active command prevent exceeding physical-connection budgets or overlapping a transaction/reader on one Session. Admission, timeout, concurrent-use and charged-lease tests. | Pending; benchmark connection policy must be identical across lanes. |
| PostgreSQL Parse+Describe+Sync reply group | Complete fresh metadata and error priority precede Execute; same physical connection owns all messages. `postgres_sync_tests`, metadata/open timing and external-DDL tests. | Pending; one source-derived reply group, not a measured RTT or poll count. |
| First Bind/Execute reply and later result availability | Side effects start only after full metadata and second admission. Subsequent fetches drain this execution rather than resend SQL. UDF/open tests, `pull_first_fetch_admission`, provider dispatch counts. | Pending; count SQL, protocol groups and socket waits independently. |
| PostgreSQL unfinished-reader drain/confirmation | Early stop, unread/error results and uncertain protocol state require actual drain or discard. Natural EOF may reuse its already consumed ReadyForQuery proof. PostgreSQL sync/fault/timeout/rollback tests. | Pending for early stop and natural EOF separately. |
| SQLite prepare/bind/step/finalize and busy handling | One statement preserves metadata and conversion order; no step at open. Reset/cross-execution statement caching remains unselected. SQLite UDF, lock, conversion and cleanup tests. | Pending; there is no network RTT to remove. |
| Native worker queue plus one ready dispatch | Moves blocking provider work off managed callers while preserving one accepted-result obligation and bounded Source accounting. Pull generation/abandonment tests. | Pending: queue, CPU and wakeup cost. |
| Controller callback/control and registration drain | A real cookie/registration may still access the controller until these finish. Fault boundaries and pre-reservation stop race tests. No normal per-batch generic `try_retire` polling remains. | Pending: normal and canceled paths separately. |
| Provider bytes/scalar scratch → bounded batch arena | Copy or scalar conversion supplies independent immutable output while the provider advances. Stack scratch handles fixed-width values; fallible text/numeric/JSON work remains. Scalar and batch conversion/limit tests. | Pending: conversion and arena writes. |
| NWDB result descriptors, cells and partial-batch compaction | Fixed framing protects shape, extents and budgets. `BatchWriter::finish` can move payload to remove unused cell-table space in a partial batch; arena growth can also copy existing bytes. Wire/large-field/partial-batch tests. | Pending; direct arena construction does not mean zero copying. |
| One managed `WireLayout` validation per attached batch | Full header/shape/extent checks precede any borrowed value; projection matching is reused only for the same fields/expectation. Malformed wire/projection/null/type tests. | Pending: layout validation/allocation by refill count. |
| Buffered-result row-byte accounting | Buffered terminals inspect cell lengths before admitting each DTO to the caller-owned result; streaming terminals avoid that aggregate-buffer obligation. Buffered row/byte limits and constructor-failure tests. | Pending: charge calculation versus actual materialization separately. |
| Synchronous span scope and held-reader release | Keep immutable native storage alive for the complete mapper call while closing later read admission. Scoped-generation and held-mapper tests. | Pending: locks/read scopes/release; no whole-batch managed copy. |
| Typed value decoding and DTO/list/string/JSON creation | Return the same independently owned business result; retain narrowing/UTF-8/NULL/precision errors. Generated/handwritten parity and actual 1/100/1000 DTO consumers. | Pending; business allocations are reported separately, not estimated away. |
| Final close, Source fences and transaction cleanup | Prove local safety and protocol-safe return independently of cancellation/public completion. Old-tail barrier, transaction epilogue, held-mapper and real PostgreSQL fault tests. | Pending: zero-close shortcut versus one actual join operation. |

Current objects still include query/transport/lease/layout state, active GCHandle
and cancellation bookkeeping, and cold Task/error/cleanup paths. Their existence
does not establish or disprove a measured steady-window result by itself. The
whole-framework 0 B target requires allocation evidence across real refills,
suspension and concurrency; an in-row zero is insufficient.

## Source references and test correspondence

The responsibility references remain the locked versions, not current default
branches: PostgreSQL/libpq 18.0 [`3d6a8289`][pg-source], Npgsql 11.0.0
[`4d174200`][npgsql-source], Microsoft.Data.Sqlite 11.0.0
[`9e685c7a`][sqlite-managed-source], SQLite 3.51.3 [`a5333afb`][sqlite-source],
Dapper.AOT 1.1.0 [`0e071bf0`][dapper-source], .NET 11
[`deae2e32`][dbcommand-source], and SqlSugar [`06789315`][sugar-source].
The [actual generated consumer record][generated] distinguishes the two-column
same-SQL row reader from the nine-column mixed-workload reader and its command
caching policy. Inspect the exact restored consumer graph and emitted source;
an upstream generated fixture is not the tested consumer. The maintained
[execution target](query-semantics.md) links the companion reader, cache,
libpq, scalar and protocol source files in full.

| Contract | Product oracle and relation to prior evidence |
| --- | --- |
| Lazy open and second admission | `native/cpp/tests/streaming_tests.cpp::pull_first_fetch_admission`, `bounded_batches`; `relations_abi_tests.cpp` exercises the actual relation/mutation entries. Retains the historical no-step/open obligation. |
| Generation, owned result and old native tails | `pull_generations_and_tail`, `pull_pending_and_active_abandonment`, `pull_end_and_abandonment`; hold an old tail after ready, consume/request the next generation, and prove final close remains pending. |
| Accepted request with queue/cleanup failure | `pull_queue_failure_completion`, `pull_cleanup_queue_failure`, `pull_parent_cleanup_failure` in the containment follow-up: exactly one ready, original error identity, no worker/request leak, truthful failed/unreleased snapshots and retryable parent cleanup. Unknown-retirement subprocesses preserve the intentionally retained native accessor instead of requiring a fabricated zero count. |
| C ABI and capability records | `native/cpp/tests/database_abi.c`, `relations_abi_tests.cpp`; `tests/Query.Binding/generate.py` keeps frozen declarations and negotiates all eight new entries. |
| Controller result, compensation and reuse | `tests/Data.NativeHost/Program.cs::PrivateFetchOwnerFailures`, `PrivatePullStopBeforeReservation`, `ReusablePullBatches`; exact original exceptions, single-consumption ValueTasks, same stable batch across generations and held-reader exclusion. |
| No retry slot and rejected scheduler | `RejectedPullScheduler`: two providers × BeforeRoot/RootAllocated × successful/failing held Stop. Setup returns pending with one control and no slot; every pull scheduler offer rejects. Releasing stop still publishes the original setup failure once, drains root/control/callback state and retains an independent stop failure through final join. |
| Raw transfer and actual typed route | `BatchResultTests.VerifyRecord/VerifyFetches`: invalid records and each missing export, attachment compensation, no `buffer_view` on batch take, 0/1/32/64/100/1000 rows with exact request/take/publication/SQL counts and no per-batch generic retirement. |
| Mapper/cancellation/parent close | `BorrowedBatchHostTests` retains its 16 × 2 scenarios with a held native buffer, actual native stop-return or parent-close proof, original mapping/token/error and cleanup assertions. `VerifyParentTransactions` preserves transaction-disposal completion. |
| Span and DTO lifetime | `tests/Data.Streaming` and `tests/Data.Abstractions` retain malformed/default/retired reader and generated/handwritten behavior; new scoped-generation tests retain physical owner release until the last span scope. |
| Transaction and Source retirement | `transaction_tests.cpp` epilogue/parent/last-Source/launch-compensation cases plus PostgreSQL protocol fault suites preserve the earlier [retirement experiment][retirement-experiment] and [PostgreSQL experiment][pg-experiment] guarantees, as mapped by `ported-tests.md`. Historical experiment execution is not current-candidate execution. |

The development Streaming Native AOT run passed its 60 cases and 615 primary
assertions. The development NativeHost run passed 590 primary assertions, 148
generic-retirement observations, 32 held-mapper scenarios, both providers' six
row counts and zero live owner counts 0–5 plus 8 after cleanup. Its first attempt
failed the incorrect exact-one-close assertion; the retained failure and the
source proof above explain the corrected zero-or-one requirement. These receipts
pre-date the integrated native cleanup-containment change and do not accept
that final candidate. The containment change separately passed isolated
`native.streaming` (265 checks), `native.transactions` (120),
`native.relations.abi` (469), and the C ABI compile gate; those four native targets
do not replace a rebuilt provider package and executed Native AOT consumer.

The subsequent rejected-scheduler Linux Native AOT gate passed both providers'
eight cases and 72 assertions. Each failed setup dispatched zero SQL and returned
all owner counts 0–5 plus 8 to zero; ordinary stop cases reused the same Session.
Its first attempt failed because the test left its injection hook installed for
that reuse probe; the test correction clears the hooks before the probe and
retains the failed log. No additional product change was needed for that fixture
correction. These targeted runs are development evidence for their specific
source/images, not a substitute for the assembled candidate's full package gate.

The preceding published checkpoint
[`e0b5bdfd6520a74a430a94f4b0ca0b903b1af75e`](https://github.com/IzuSharp/Korda/commit/e0b5bdfd6520a74a430a94f4b0ca0b903b1af75e)
passed existing [CI run 45733034030](https://github.com/IzuSharp/Korda/actions/runs/45733034030):
10 successful jobs including Linux correctness, Interop, both provider package
jobs and Verify; modules and publication skipped under the existing PR rules.
That green run predates the last cleanup fixes and is not credit for source
`0f3816c4006488821f40afde91bbbd717d57ccd6`. Its existing
[CI run 45734731584](https://github.com/IzuSharp/Korda/actions/runs/45734731584)
was still in progress at this documentation checkpoint.

Plan owns exact executable/log hashes and the required rerun, public package
tests and four serial local
1800-second candidate/reference cells. No performance claim or CI benchmark is
introduced by this design checkpoint.

[fluent]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/src/Query.Fluent/QueryContext.cs
[terminals]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/src/Query.Fluent/Terminals.cs
[session]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/src/Data.NativeHost/DataSession.cs
[abi]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/native/cpp/src/host_abi.cpp
[host]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/native/cpp/src/host.cpp
[provider]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/native/cpp/src/provider.cpp
[contracts]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/native/cpp/src/contracts.cpp
[managed-native]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/src/Data.NativeHost/NativeHost.cs
[controller]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/src/Data.NativeHost/HostPullController.cs
[batch]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/src/Data.Streaming/StreamTransport.cs
[stream]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/src/Data.Streaming/TypedStream.cs
[rows]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/src/Data.Abstractions/Rows.cs
[header]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/native/database/binding/korda_cursor_pull_v1.h
[manifest]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/native/database/binding/cursor-pull-v1.json
[cleanup-seal]: https://github.com/IzuSharp/Korda/blob/0f3816c4006488821f40afde91bbbd717d57ccd6/native/cpp/src/host.cpp
[pg-source]: https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/tcop/postgres.c
[npgsql-source]: https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlCommand.cs
[sqlite-managed-source]: https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteCommand.cs
[sqlite-source]: https://github.com/sqlite/sqlite/blob/a5333afb9ad1aa473f8963b92caeaa955f47dc74/src/prepare.c
[dapper-source]: https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandT.Query.cs
[dbcommand-source]: https://github.com/dotnet/runtime/blob/deae2e32bf0e018e09d64597b7c59b62b73bb3ce/src/libraries/System.Data.Common/src/System/Data/Common/DbCommand.cs
[sugar-source]: https://github.com/DotNetNext/SqlSugar/blob/06789315fcea02f17901506b0cbf670a25192083/Src/Asp.NetCore2/SqlSugar/Abstract/QueryableProvider/QueryableHelper.cs
[generated]: https://github.com/IzuSharp/Plan/blob/ad89b21681b5ebe3c044e7d6b4dc63b67c7fefed/ledger/evidence/batches/DB-Perf-01/execution-refactor/generated-consumers/README.md
[retirement-experiment]: https://github.com/IzuSharp/Korda-Design/blob/3db2d69/experiments/database-retirement/src/lib.rs
[pg-experiment]: https://github.com/IzuSharp/Korda-Design/blob/3db2d69/experiments/database-completion/tests/postgres.rs
