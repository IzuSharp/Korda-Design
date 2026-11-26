# Implemented execution path at 17da — DB-Exec-10

## Identity and acceptance boundary

The formal product candidate is
[`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`][product], tree
`bc9087d843d8d741d83d44f53d0b2c5af26dcffc`, on Linux x64. This record describes
its implemented path and the contracts that constrain further changes. It is a
source review, not a new product execution or performance observation.

CursorPull, typed command completion, direct batch construction, prepared value
submission, fixed-key Find and the selected PostgreSQL state proof are
implemented in this candidate. Earlier proposal tables in
[query-semantics.md](query-semantics.md) that say implementation is pending
describe their original checkpoints. They are retained unchanged as history.
The [independent package receipt][packages] records successful builds and public
Native AOT consumption for both provider packages. **Final continuous
1800-second performance credit is still 0/4 at this checkpoint.** The
[current campaign selection][campaign] owns the remaining same-host baseline,
offered-load and final-run evidence; it does not inherit historical long runs.

The already-released close experiment at
[`92b923075952bac347619ee7817c372ee6e415cb`][close-source] is not selected.
Its finite correctness and independent package builds passed, but its two-round
ordinary comparison failed the predeclared performance rule. PostgreSQL
single-row read-complete did not improve consistently, and SQLite 1,000-row
pooled total p50 regressed 6.78%, beyond the 5% bound. The
[unchanged prospective rule and observed rejection][close-decision] preserve
both rounds. Formal 17da retains its queued final-close path. No best-of retry,
threshold adjustment or performance credit is transferred from that experiment.

## Public entry points and shared execution

| Public entry | Actual 17da path | What is reused on repetition |
| --- | --- | --- |
| Ordinary Fluent | `DataSession.From` creates `QueryBinding.CreateBuffered`; `QueryCommand` holds the complete bounded composition and typed dependency owners; native compile/seal produces a plan; `QueryContext.Stream` submits it | Registered model/projection metadata; ordinary one-shot composition and compilation still occur |
| `.Prepare()` | `QuerySelection.Prepare` seals terminal8 and saves the parameter layout and projection; `PreparedQuery.Stream` captures the current values before constructing its lazy stream | Compiled SQL, ordered parameter metadata and stable managed projection layout; each execution owns its values |
| `FindAsync` | `DataSession.FindAsync` in Crud.cs acquires the Source's exact-table fixed shape; `FindPlan.Execute` writes the captured key values and uses the existing single-or-default stream | NativePlan, compiled shape, key slots, full projection and managed mapper identity; no repeated Fluent/NWQC construction |
| Complete parameterized SQL | `QueryAsync` / `StreamAsync` capture the raw SQL submission through `SqlSubmission.Create` | The explicit SQL supplied by the caller; its own argument-capture contract remains distinct from Prepared |

All four row-producing entries reach
`DataSession.OpenPlanStreamAsync -> NativeHost.CreatePull -> HostStreamTransport
-> TypedStream -> generated or static RowReader -> owned DTO`.
The [session entry][session-entry], [binding entry][binding-entry],
[Fluent terminals][terminals], [Find implementation][find] and
[SQL/stream session implementation][data-session] establish that routing.
The first native pull opens and fetches in one request, but complete metadata
validation and a second execution admission still precede Execute/step.

[CommandOnlyTests][command-only] removes direct composition exports from its
resolver while the complete-command path still compiles, renders and creates
CTEs. This prevents an implicit per-node fallback from serving as the tested
formal entry. [BatchResultTests][batch-tests] exercises public streams at 1, 32,
64, 100 and 1,000 rows with exact pull counts, one SQL execution, one final close
and no generic fetch-operation retirement. Source routing and tests are separate
evidence: a consumer build alone does not prove a timed route executed.

## Decisions from the driver upwards

| Boundary | Reuse, rewrite or delete in 17da | Retained cost and reason |
| --- | --- | --- |
| PostgreSQL driver | Reuse libpq 18.0. Send fresh unnamed Parse and Describe in one pipeline group, followed by one Sync; consume the entire group before leaving pipeline mode | Fresh preparation/description still occurs per execution. Reusing a physical prepared statement or description can change external-DDL error and transaction semantics; that cache is not selected |
| PostgreSQL confirmation | Delete the redundant successful-prepare confirmation. Reuse actual natural-EOF proof to avoid a standalone close Sync. Use healthy `PQTRANS_INTRANS` proof to omit the pre-COMMIT SELECT1 only under the implemented exclusions | Early stop, unopened/failed readers and unknown or unhealthy protocol states retain drain/confirmation/discard. Post-COMMIT and safe-return/acquisition proofs remain |
| SQLite statement | Reuse sqlite3 3.51.3. Prepare one statement, inspect metadata and bind that same statement; delete the separate describe statement and second prepare | No step at open; completion/failure finalizes the statement. Cross-execution reset/clear-bindings reuse is not selected. `query_only` controls retain raw-PRAGMA and transaction semantics |
| Dynamic composition | Keep one bounded NWQC composition and typed owner sidecar. Delete command-clause/field rewrapping, token patching and repeated schema parsing. The private compiler edits in place; seal/CTE moves its owned arena | `QueryCommandReplay` record traversal and NativeQuery semantic compilation remain real work. C++ still constructs SQL. Public direct mutable ABI keeps copy-on-success for recoverable mutation errors |
| Execution values | Reuse compiled ordered parameter/projection metadata. Render typed Scalars once and move their ownership through `SqlPlan::rendered`; delete `QueryData.values` whole-frame retention, the native second NWDB encoding and Host re-decoding | C# captures a new value frame, and native values own the required bytes. Mutable caller buffers cannot be borrowed across await. Raw SQL retains its own captured input representation |
| Fixed-key Find | Compile ordered private key slots, full selection and terminal3/LIMIT2 once. Use Source-owned bounded LRU entries keyed by exact Table reference. Reuse Source projection metadata and bypass the general ShapeCache for this private plan | Each execution still checks sequential admission and writes independent values. Provider preparation is unchanged. Cache bounds are not a total Source/RSS bound; accepted leases can outlive eviction |
| Native batches | Convert directly into a bounded BatchWriter arena. Delete per-cell owning byte vectors, row staging and the corresponding repeated parsing | Each batch still needs descriptors/header/extent validation; partial-batch compaction can remain. Conversion must preserve field, row and aggregate limits and explicit loss refusals |
| Managed reading | Reuse a channel controller, scoped native batch owner and validated layout; generated readers construct DTOs directly | Data-dependent NULL/UTF-8/numeric checks and lease generation checks remain. Business DTO/string/list/JSON allocation is separate from framework overhead |
| Scalar/control completion | Use typed request/ready/take for Count/Any, nonreturning CRUD, transaction/savepoint and child-close entries; count values no longer roundtrip through a row batch | Source/admin/unknown-acceptance generic operations still have real callers. Early Unknown decisions and independent cleanup/notification ownership remain |
| Stream retirement | Reuse observed EOF, request generations, buffer ownership and independent final-close fences | 17da still dispatches each batch and queues final close. Fetch readiness is not proof that callback tails, cleanup, borrows or Source reservations are quiet |

The concrete C++ boundaries are [provider.cpp][provider], [query.cpp][query]
and [host.cpp][host]. A complete-command submission is not a claim that all
native traversal has disappeared. Likewise, a prepared shape does not imply
that the whole execution allocates zero bytes.

### Fixed-key ownership and compatibility

The private `find-shape-v1` factory is cold. Its key ordinals are independent of
the public ParameterRegistry and do not require the public prepared-query
capability. Equal metadata is not sufficient to share a managed materializer:
the cache uses the exact Table object, including its Row mapper. Source closure
drops cache ownership; active executions retain their own immutable reference.
Entry and byte eviction do not invalidate a captured execution.

The factory reports both cache charge and the actual fixed logical-query charge;
these are different quantities. Managed admission reproduces the original Find
builder's order before returning asynchronous work, including initial root-node
charge, model registration, each Column/Value/Binary/WHERE step and individual
wire-size rejection. Key values were already snapshotted independently of the
caller's mutable storage. Native render repeats source/schema/limit validation.
The former production Find builder is deleted; its exact retained test oracle
has a real differential-testing caller.

[FindShapes][find-tests] and [the fixed native query tests][query-tests] cover
same-metadata/different-mapper behavior, configured codecs, key snapshots,
invalid/closed/canceled ordering, entry and byte eviction, a lease held over
eviction, public registry isolation, cold/warm budgets and native foreign-source
refusal. Find render directly uses its already-owned compiled shape; ordinary
Fluent and public Prepare still invoke the general ShapeCache hash/LRU path.

### EOF, cancellation and quietness

A partial final batch already carries observed EOF. After consuming and releasing
it, TypedStream performs the existing synchronous read-admission check and joins
cleanup without an empty fetch. A full batch at the exact boundary may require
another pull to discover EOF; no extra provider step is introduced merely to
predict it. The public error order still includes Source/Session closure and
cancellation after the last row.

Neither EOF nor ready notification alone releases the Session gate. Native
cleanup, old fetch tickets, callback tails, batch borrows and final notification
fences remain separately owned. A mapper failure preserves its primary error
while releasing the batch and joining cleanup. These obligations explain the
retained final-close receipt and the decision to keep the 17da implementation
after the narrower dispatch experiment failed its performance rule.

## Contract-to-test map

| Guarantee | Maintained source/tests |
| --- | --- |
| Parse/Describe/Sync boundaries, complete metadata before Execute, actual EOF versus unfinished exact-row-limit reads | [postgres_sync_tests.cpp][pg-tests], [provider_tests.cpp][provider-tests] |
| No step at open, early-stop behavior, real connection reuse and unsafe connection retirement | provider tests, SQLite/PostgreSQL fixture families and [streaming_tests.cpp][stream-tests] |
| Failed transaction, known rollback versus Unknown, lost reply, late confirmation, last-parent retirement | [transaction_tests.cpp][transaction-tests], PostgreSQL protocol tests and the retained fixture families |
| Complete-command equivalence, immediate recoverable errors, clone/CTE and bounded ownership | [query_tests.cpp][query-tests], [CommandOnlyTests][command-only] and existing Fluent/Binding suites |
| Find identity, registry isolation, snapshots, error timing and budgets | [FindShapes][find-tests] and native query tests; [independent Find review][find-review] retains exact development-source receipts |
| Public pull routing, borrowed result lifetime, known EOF and final-close ownership | [BatchResultTests][batch-tests], native streaming and managed NativeHost/Streaming suites |
| Historical retirement and PostgreSQL completion guarantees | [ported-tests.md][ported-tests] maps actual retained C++ tests to earlier behavior; the [retirement experiment][retirement-experiment] and [PostgreSQL experiment][pg-experiment] remain fixed historical sources |
| Independent package, exports and Native AOT consumption | [17da package receipt][packages] and its original per-provider stage logs |

These are maintained test correspondences, not a new execution claim. Historical
assertion counts retain their original source and run identity. An old experiment
or development executable is not counted as the independently built 17da package.

## Fixed upstream and generated-consumer evidence

| Upstream | Exact source inspected for the selected boundary |
| --- | --- |
| PostgreSQL/libpq 18.0 | `3d6a828938a5fa0444275d3d2f67b64ec3199eb7`: [postgres.c][pg-server] Parse/Bind/Execute/Describe; [fe-exec.c][libpq-exec] send/wait/result/Sync; [plancache.c][pg-plancache] revalidation |
| Npgsql 11.0.0 | `4d174200ed48e3e3ab16419dbf84dd655da59de6`: [NpgsqlCommand][npgsql-command], [NpgsqlDataReader][npgsql-reader], [PreparedStatementManager][npgsql-prepared] and [NpgsqlTransaction][npgsql-transaction] |
| Dapper.AOT 1.1.0 | `0e071bf05e54caecfa98c885b075fa3e247f3ecc`: [CommandT.Query.cs][dapper-query], [Query output fixture][dapper-generated] and [CacheCommand output fixture][dapper-cache] |
| .NET 11 | `deae2e32bf0e018e09d64597b7c59b62b73bb3ce`: [DbCommand.cs][dbcommand], separating base API contracts from provider implementation |
| Microsoft.Data.Sqlite 11.0.0 | `9e685c7a52d1a344d133a3d370e458db97417b3f`: [SqliteCommand][sqlite-command], [SqliteDataReader][sqlite-reader] and [SqliteDataRecord][sqlite-record] |
| SQLite 3.51.3 | `a5333afb9ad1aa473f8963b92caeaa955f47dc74`: [prepare.c][sqlite-prepare] and [vdbeapi.c][sqlite-vdbe] |
| SqlSugar | `06789315fcea02f17901506b0cbf670a25192083`: [QueryableHelper.cs][sqlsugar], complete SQL/parameters before provider reader execution |

Upstream fixtures are not substitutes for the actual consumer generation. Three
different evidence sets must retain their identities:

1. The [original generated workload consumers][original-generated] contain the
   nine-column Order reader, decimal/JSON handlers and their original PK sites.
2. The [later matched-SQL audit][matched-sql] binds the lifecycle Find SQL with
   `tenant`, `id` and `take` as three Int64 parameters. The earlier two-parameter
   PK source is not evidence for this later command.
3. The current same-SQL phase uses two-column Id/Note DTOs. Its actual
   [preserved generated Phase source][phase-generated] has two command-factory
   instances, two ordinal Int64 parameter updates and `RowFactory0`: Tokenize
   matches names/types once, Read uses typed accessors/IsDBNull and directly
   constructs PhaseRow. The [current allocation/source audit][allocation]
   checks the reused generated-source identities against the current harness and
   records provider-specific consumers. It does not rewrite the older build's
   source identity or execution time.

The nine-column RowFactory3 must not be substituted for the two-column phase.
Current SQL contracts and execution receipts, rather than a familiar query name,
establish equivalent SQL, parameters, result and consumption.

## Independent providers and remaining acceptance

The [17da package/source audit][packages] binds both clean producers to the exact
commit/tree above. Each completes eight existing stages: impact planning,
provider native build, native correctness, bundle, public AOT consumption,
public validation and the two ordinary consumer builds. Each release contains
one independent top-level package with an empty package-dependency map and its
own Linux x64 native image: `Korda.Database.Sqlite` or
`Korda.Database.PostgreSql`. The earlier missing Find inventory failure is
preserved; 17da closes the bit29 export inventory without weakening the audit.

Source creation checks the private cursor-pull, command-completion and Find
capability/export contracts. Buffered query composition has its own
query-command binding checks. These entries do not silently choose an old
per-node or generic-fetch path when an asset lacks the selected protocol.
Frozen direct ABI entries and generic administrative/uncertain-acceptance paths
retain genuine compatibility or execution callers and are not dead-code claims.

The following limits remain explicit:

- **Additional managed framework allocation of 0 B is unproven.** The current
  allocation audit reports `FrameworkOnlyBytes=null`. It measures actual mapper
  and List scopes separately, without subtracting them from process allocation
  to invent a framework number. There is no current before-allocation overlay
  or standalone Find-allocation comparison.
- The exact CPU/latency cost of every surviving hash, copy, validation and queue
  is not independently isolated. Submit/read-complete phase timing does not
  prove which individual component dominates. Rejecting one close experiment
  does not establish that every possible improvement has disappeared.
- Arbitrary fixed Fluent method bodies are not compiled into SQL/templates by
  the source generator. Implemented generation covers static model/projection
  and DTO reading; runtime Prepare and private Find supply the selected fixed
  execution shapes. Physical statement caches also remain unselected.
- The allocation audit's GC observations are process-wide differences over its
  windows, not the entire process lifetime including setup/warmup/gaps. Final
  throughput/tails/errors/rejections/CPU/RSS/allocation/GC must retain the final
  runner's actual measurement scope.
- Same-host before evidence, offered-load validation, four final serial
  1800-second cells, normal reviewed merges and observed existing CI/release
  remain separately tracked. This checkpoint grants none of that unrun credit.

The stopping rationale must name completed work, observed gains or rejected
experiments, and remaining measured/unproven costs. It must not claim whole-path
zero allocation or exhaustion of all possible measurable gains. CI retains the
existing diff/module selection and independent provider package checks; all
benchmark, profile, calibration and pressure work remains local Linux work.

[product]: https://github.com/IzuSharp/Korda/commit/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa
[close-source]: https://github.com/IzuSharp/Korda/commit/92b923075952bac347619ee7817c372ee6e415cb
[packages]: https://github.com/IzuSharp/Plan/blob/9e4aad4c04c68dd30ab3bcad68a977000b4717e2/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-ci-review-evidence/completed-public-builds-17da-02.json
[campaign]: https://github.com/IzuSharp/Plan/blob/9e4aad4c04c68dd30ab3bcad68a977000b4717e2/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/local-load-tools/current-campaign-selection.md
[close-decision]: https://github.com/IzuSharp/Plan/blob/9e4aad4c04c68dd30ab3bcad68a977000b4717e2/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/close-quiet-experiment.md
[session-entry]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Query.Fluent/SessionQueries.cs
[binding-entry]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Query.Binding/QueryBinding.cs
[terminals]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Query.Fluent/Terminals.cs
[find]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Orm.Relations/FindPlan.cs
[data-session]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Data.NativeHost/DataSession.cs
[command-only]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/tests/Query.Binding/CommandOnlyTests.cs
[batch-tests]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/tests/Data.NativeHost/BatchResultTests.cs
[provider]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/src/provider.cpp
[query]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/src/query.cpp
[host]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/src/host.cpp
[pg-tests]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/tests/postgres_sync_tests.cpp
[provider-tests]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/tests/provider_tests.cpp
[stream-tests]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/tests/streaming_tests.cpp
[transaction-tests]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/tests/transaction_tests.cpp
[query-tests]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/tests/query_tests.cpp
[find-tests]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/tests/Orm.Relations/FindShapes.cs
[find-review]: https://github.com/IzuSharp/Plan/blob/9e4aad4c04c68dd30ab3bcad68a977000b4717e2/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/find-path-review.md
[ported-tests]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/tests/ported-tests.md
[retirement-experiment]: https://github.com/IzuSharp/Korda-Design/blob/3db2d69/experiments/database-retirement/src/lib.rs
[pg-experiment]: https://github.com/IzuSharp/Korda-Design/blob/3db2d69/experiments/database-completion/tests/postgres.rs
[pg-server]: https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/tcop/postgres.c
[libpq-exec]: https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/interfaces/libpq/fe-exec.c
[pg-plancache]: https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/utils/cache/plancache.c
[npgsql-command]: https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlCommand.cs
[npgsql-reader]: https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlDataReader.cs
[npgsql-prepared]: https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/PreparedStatementManager.cs
[npgsql-transaction]: https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlTransaction.cs
[dapper-query]: https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandT.Query.cs
[dapper-generated]: https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/test/Dapper.AOT.Test/Interceptors/Query.output.cs
[dapper-cache]: https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/test/Dapper.AOT.Test/Interceptors/CacheCommand.output.cs
[dbcommand]: https://github.com/dotnet/runtime/blob/deae2e32bf0e018e09d64597b7c59b62b73bb3ce/src/libraries/System.Data.Common/src/System/Data/Common/DbCommand.cs
[sqlite-command]: https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteCommand.cs
[sqlite-reader]: https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteDataReader.cs
[sqlite-record]: https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteDataRecord.cs
[sqlite-prepare]: https://github.com/sqlite/sqlite/blob/a5333afb9ad1aa473f8963b92caeaa955f47dc74/src/prepare.c
[sqlite-vdbe]: https://github.com/sqlite/sqlite/blob/a5333afb9ad1aa473f8963b92caeaa955f47dc74/src/vdbeapi.c
[sqlsugar]: https://github.com/DotNetNext/SqlSugar/blob/06789315fcea02f17901506b0cbf670a25192083/Src/Asp.NetCore2/SqlSugar/Abstract/QueryableProvider/QueryableHelper.cs
[original-generated]: https://github.com/IzuSharp/Plan/blob/ad89b21681b5ebe3c044e7d6b4dc63b67c7fefed/ledger/evidence/batches/DB-Perf-01/execution-refactor/generated-consumers/README.md
[matched-sql]: https://github.com/IzuSharp/Plan/blob/9e4aad4c04c68dd30ab3bcad68a977000b4717e2/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-6/sql-and-probe-audit.md
[phase-generated]: https://github.com/IzuSharp/Plan/blob/9e4aad4c04c68dd30ab3bcad68a977000b4717e2/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-3/allocation-recovery/consumers/allocation-dapper-sqlite-05/generated-original/Dapper.AOT.Analyzers/Dapper.CodeAnalysis.DapperInterceptorGenerator/DbPerf.DapperQueryPhases.generated.cs
[allocation]: https://github.com/IzuSharp/Plan/blob/9e4aad4c04c68dd30ab3bcad68a977000b4717e2/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-measurements/allocation/README.md
