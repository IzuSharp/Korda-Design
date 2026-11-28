# Mature execution reuse

Status: source-verified continuation of Korda-Orm-01. The first proposed independent
Korda execution engine is superseded as the default candidate. The unmodified
Dapper.AOT runtime and its generation protocol can execute the required dynamically
composed SQL; the adaptation boundary is substantially smaller than a replacement
binder, mapper and execution engine. Product implementation remains unauthorized.

This document distinguishes a **verified original-library route**, an **explicit
runtime route**, and the small policy differences Korda must enforce. The common
language, rendering and invocation contracts remain independent of Dapper and ADO.NET.
See [generation integration](generation-integration.md) for automatic consumer API
composition and [execution and AOT](execution-aot.md) for the consolidated decision.

## 1. Fixed source and reusable implementation

Dapper is 2.1.100 at `188094784256da61d7a37c43ea54c64213c2ce7c`.
Dapper.AOT is 1.1.0 at `0e071bf05e54caecfa98c885b075fa3e247f3ecc`.
The inspected NuGet packages and source pins are the same releases. These claims
refer to their actual public implementation, not every release with a similar API.

| Source symbol | What it establishes | Intended inheritance |
| --- | --- | --- |
| [Dapper `DynamicParameters.Add` and `AddParameters`](https://github.com/DapperLib/Dapper/blob/188094784256da61d7a37c43ea54c64213c2ce7c/Dapper/DynamicParameters.cs) | Explicit parameter entries carry value, DbType, direction and facets; the public identity-free entry can be called by generated code | Compatibility route uses the package implementation, with a controlled explicit-entry policy |
| [`DapperAnalyzer.SharedParseArgsAndFlags` and `SharedGetParametersToInclude`](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT.Analyzers/CodeAnalysis/DapperAnalyzer.cs) | A supported DynamicParameters bag defers its parameter map and is not rejected as an untyped anonymous object | Preserve concrete bag type at the Dapper call site |
| [`DapperInterceptorGenerator.WriteCommandFactory`](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT.Analyzers/CodeAnalysis/DapperInterceptorGenerator.cs) | `IsDynamicBag` emits `args.AddParameters(cmd.Command!)`, `RequirePostProcess`, and parameter callbacks; result factories are independently generated | Original call-site interception is a valid baseline; explicit adapters use the same public factory protocol |
| [`DapperAotExtensions.Command`](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/DapperAotExtensions.cs) | Public construction of `Command<TArgs>` accepts connection, transaction, SQL, command type, timeout and factory | Call this package API directly; no interceptor is required for explicit factories |
| [`CommandFactory<T>`](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandFactory.cs) | Public command construction, parameter creation/update, postprocessing and recycling hooks | Derive a small layout/provider adapter; retain the upstream executor |
| [`RowFactory<T>`](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/RowFactory.cs) | Tokenize once, read typed cells per row, scalar/dynamic-record alternatives and buffered/streaming reader helpers | Emit Korda projection-specific subclasses using the mature token/read protocol |
| [`Command<TArgs>`](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandT.cs) and [`CommandT.Query`](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandT.Query.cs) | Transaction association, buffered/single/streamed queries, token-buffer reuse, reader iteration and cleanup | Reuse the unmodified runtime package; do not implement equivalent Korda loops |
| [`SyncCommandState`](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/Internal/SyncCommandState.cs), [`AsyncCommandState`](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/Internal/AsyncCommandState.cs), [`AsyncQueryState`](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/Internal/AsyncQueryState.cs) | Connection-state restoration, async command/reader lifetime and leased tokens | Reuse as internal parts of the package, never bind Korda to their internal types |
| [`DapperAnalyzer.Diagnostics`](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT.Analyzers/CodeAnalysis/DapperAnalyzer.Diagnostics.cs) | Some non-intercepted paths produce Info-level diagnostics rather than errors | Explicitly elevate unsupported-path diagnostics in compatibility consumers and verify generated coverage |

These are public runtime extension APIs even though their main caller is the
upstream generator. API upgrade risk is handled by a pinned package and compiled
adapter/consumer tests. A source fork is not required by the demonstrated path.
Apache-2.0 notices and generated/source-derived code attribution follow
[upstream policy](upstream-policy.md); copying an entire upstream tree into the
product or documentation repository is unnecessary.

## 2. What the original library actually supports

A normal, non-generic method whose Dapper call names a concrete DTO can receive
runtime SQL and a dynamically sized `DynamicParameters` value. The original
Dapper.AOT generator emits a command factory for that bag and a concrete DTO row
factory. It does not need to enumerate every possible SQL string or WHERE subset.
The same DTO factory can read several query shapes that have the compatible
result columns. A different statically known DTO gets its own generated factory.

The verified path is:

1. A typed C# DSL builds an AST with optional conditions and typed slot identity.
2. Rendering visits that AST and assigns physical parameter names and occurrences.
3. Invocation binding supplies the values for the selected slots. An explicit bag
   receives only those entries, each with a DbType and input direction.
4. An ordinary concrete-DTO wrapper calls `connection.Query<TheDto>(sql, bag, ...)`,
   `QueryAsync<TheDto>`, `QueryUnbufferedAsync<TheDto>`, or `Execute`.
5. Original Dapper.AOT interceptors invoke its runtime with the generated command
   and row factories. The provider executes SQL; typed rows return to the caller.

The experiment's physical names are `p0`, `p1`, etc. Repeated logical slot identity
reuses a name; two slots with the same diagnostic label retain distinct identities.
Expanded lists become individual scalar entries during rendering, including an
explicit false predicate for an empty list. Dapper list expansion is not invoked
to rewrite an already validated Korda SQL template.

### 2.1 Controlled bag policy

Use `new DynamicParameters()` followed by explicit `Add(name, value, dbType,
ParameterDirection.Input, size, precision, scale)` calls. Do not accept an
arbitrary user-created bag through the core Korda API. In particular:

- Object templates (`new DynamicParameters(object)` and object-template
  `AddDynamicParams`) can reach `CreateParamInfoGenerator` and Reflection.Emit.
- Missing DbType may invoke runtime type lookup. Korda already has SQL/CLR type
  information and supplies the declared type or an explicit provider codec.
- `PackListParameters`, literal substitution and SQL-token discovery are not the
  authority for Korda's occurrence layout. Expand/render first, then bind.
- Output callbacks, TVPs, batches and arbitrary custom handlers are independent
  capabilities; success with scalar input bags does not accept them.
- A bag is invocation-owned and not reused concurrently. The upstream bag stores
  attached parameter state as part of its output protocol.
- A SQL character-length facet is validated independently of DbParameter.Size.
  Do not copy it blindly into Size: Npgsql's
  [HandleSizeTruncation](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlParameter.cs)
  truncates string input by UTF-16 length. The baseline provider adapters leave input text/binary Size
  at its default/unlimited value and reject an invalid value before dispatch.

The original explicit-entry path ran under Native AOT. The object-template path
also compiled without warnings, but failed natively with
`PlatformNotSupportedException` in `SqlMapper.CreateParamInfoGenerator`. Upstream
suppression annotations mean a warning-free publish alone cannot prove all bag
construction paths safe. The permitted path is established by source control,
actual generated code and the native positive/negative cases together.

### 2.2 Ordinary wrappers, generic wrappers and fail-closed diagnostics

A wrapper containing a concrete `Query<User>` call was intercepted in the actual
experiment. A wrapper containing `Query<T>` with an open method type parameter was
not intercepted. Its default DAP016 diagnostic is Info: ordinary
`TreatWarningsAsErrors=true` did not make that build fail. Setting
`dotnet_diagnostic.DAP016.severity = error` made the same negative case fail as
expected.

Compatibility consumers must explicitly treat DAP001, DAP013, DAP014, DAP015,
DAP016, DAP017, DAP052 and DAP057 as errors, and preserve compiler/generator error
checks and generated-call coverage tests. This is the initial reviewed list;
upstream upgrades require enumerating every `DoNotGenerate` path again. It is not
a claim that setting eight codes proves arbitrary future releases safe. Do not
silently leave vanilla Dapper calls in a Native AOT consumer.

A generic Korda facade need not call a generic vanilla Dapper method. It can call
`Command<TArgs>.QueryBuffered<TRow>` with explicit statically generated factories,
as the next section specifies. That removes the concrete-call-site restriction
without requiring a new execution engine.

## 3. Direct reuse of the mature runtime

The relevant public signatures in the pinned runtime are:

```csharp
Command<TArgs> DapperAotExtensions.Command<TArgs>(
    DbConnection connection, DbTransaction? transaction, string sql,
    CommandType commandType = 0, int timeout = 0,
    CommandFactory<TArgs>? handler = null);

List<TRow> Command<TArgs>.QueryBuffered<TRow>(
    TArgs args, RowFactory<TRow>? rowFactory = null, int rowCountHint = 0);

Task<List<TRow>> Command<TArgs>.QueryBufferedAsync<TRow>(
    TArgs args, RowFactory<TRow>? rowFactory = null, int rowCountHint = 0,
    CancellationToken cancellationToken = default);

IAsyncEnumerable<TRow> Command<TArgs>.QueryUnbufferedAsync<TRow>(
    TArgs args, RowFactory<TRow>? rowFactory = null,
    CancellationToken cancellationToken = default);
```

Factories override these operations:

```csharp
DbCommand CommandFactory<TArgs>.GetCommand(
    DbConnection connection, string sql, CommandType commandType, TArgs args);
void CommandFactory<TArgs>.AddParameters(in UnifiedCommand command, TArgs args);
void CommandFactory<TArgs>.UpdateParameters(in UnifiedCommand command, TArgs args);
object? RowFactory<TRow>.Tokenize(DbDataReader reader, Span<int> tokens, int columnOffset);
TRow RowFactory<TRow>.Read(
    DbDataReader reader, ReadOnlySpan<int> tokens, int columnOffset, object? state);
```

The Korda-facing facade preflights profile, result descriptor, argument layout,
transaction association and cancellation, resolves statically registered factories,
and calls these APIs. It passes `CommandType.Text` explicitly. Its optional timeout
maps `null` to **-1**, preserving the driver's default; explicit zero means no
command timeout, and positive values are seconds. A negative user-supplied timeout
is rejected before command creation. The runtime's own default zero must not be
mistaken for an unspecified Korda timeout.

The controlled-bag factory can delegate its AddParameters to the original bag.
A layout factory instead iterates the already known physical layout and configures
provider parameters directly, avoiding a second bag dictionary, per-entry ParamInfo,
identity creation and literal-token inspection. This is a bounded bridge between
Korda's mature language model and Dapper's mature execution protocol. Both routes
reuse the same command runtime and may reuse exactly the same upstream-generated
row-factory code for fair comparison. Provider-specific facets are handled in the
provider leaf, not a global runtime type registry.

### 3.1 Initialization failure ownership

The upstream base `GetCommand` creates a command and calls its parameter initializer
before the query state takes ownership. If that initializer throws, the command is
not disposed by the later query-state finally block. A tracking DbCommand with an
injected CreateDbParameter exception reproduced this boundary in the native probe.

The required adapter rule is exact:

1. Complete deterministic layout/codec/value validation before creating a command.
2. Call `connection.CreateCommand()` into a local variable.
3. In a try block, set SQL and explicit command type, then call the shared
   `Bind(DbCommand, TArgs)` implementation and return the command.
4. On an initialization failure, attempt to dispose that local command. If Dispose
   also fails, attach the second exception to the primary exception under
   `Data["KordaCleanupException"]`, then rethrow the primary with its original stack.
   Never replace the binding failure with the cleanup failure or record values.
5. Implement `AddParameters(in UnifiedCommand, TArgs)` by calling the same Bind
   operation with `command.Command!`. The `UnifiedCommand(DbCommand)` constructor
   is internal; an external adapter must not attempt to construct it.

The small override was compiled and executed natively. The injected baseline had
DisposeCount=0; the adapted path had DisposeCount=1 and retained the original
exception. A second injected failure in Dispose retained the binding exception,
attached the cleanup exception and still disposed exactly once. No upstream runtime
loop or package source was changed. This proves the initialization boundary; it
does not claim to repair every possible double failure in upstream reader cleanup.

The scope is deliberately precise. After the factory returns, upstream
Command<T>.GetCommand assigns Connection, Transaction and CommandTimeout before
its caller adopts the command. This local factory catch cannot cover exceptions
from those later setters. The selected driver adapters use fresh commands,
prevalidate provider/transaction/timeout compatibility and prohibit external
concurrent mutation; they do not claim arbitrary hostile DbCommand setter behavior
has been made exception-safe. No proxy command or replacement loop is introduced.

### 3.2 Rows, empty results and cleanup

The runtime calls Tokenize once after the first successful Read, then Read per row.
Korda's generated factory validates its declared ordinal/count/type/nullability
policy before materializing the first row. It must not inherit a permissive
missing-member default simply because an upstream compatibility mapper permits it.
These checks fuse into generated tokenization; they do not require a new reader loop.

An empty result does not call Tokenize in this runtime. Consequently the execution
contract promises shape validation before materializing any row, not a metadata
exception for every empty result. Renderer/oracle tests validate empty-result schema
separately with a direct reader. There is no extra schema-only database round trip.

The runtime owns commands, readers and leased token arrays. It opens a supplied
closed connection when needed and restores the closed state; an already-open
caller connection stays open. A data-source facade that creates the connection
owns its final disposal. The Korda invocation wrapper provides its own single-use
and no-concurrent-enumeration policy, while enumeration and cleanup remain in the
upstream async iterator. Cancellation reaches the provider; SQLite's pre-cancel
success does not imply interruption of an already-running native sqlite3 step.

Command caching/recycling is disabled initially (`TryRecycle` remains false).
Pooling is owned by the database driver. A future cache must have separately
measured benefit and exact compatibility/reset rules; it is not a prerequisite
for mature runtime reuse.

## 4. Provider-specific and nested values

The bag protocol tests `SqlMapper.ICustomQueryParameter` before ordinary type lookup
and calls its AddParameter operation. Its source is a valid extension point for
NpgsqlDbType.Jsonb, arrays/ranges and similar provider settings that DbType alone
cannot express. The [upstream custom-parameter generation cases](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/test/Dapper.AOT.Test/Interceptors/CustomParameters.input.cs)
show generated use and excluded combinations. A typed NpgsqlParameter<T> uses
TypedValue and explicit NpgsqlDbType; static codecs and registrations retain AOT
reachability. These are provider adapters, not grounds for replacing execution.

JSON text/document transport and System.Text.Json source-generated metadata offer
a mature typed decoding path for declared nested projections. The SQL language
layer defines nesting, presence, ordering and null semantics; the provider transports
the declared representation; generated static decoders construct known CLR types.
No runtime creation of new CLR types is needed. The actual four-provider tests
below prove selected JSON, array, range and known nested DTO paths. They do not
accept every advanced codec or the complete product nested contract.

## 5. Actual Native AOT evidence

The bounded probes used .NET SDK 11.0.100, C# 15, Linux x64, Dapper 2.1.100 and
Dapper.AOT 1.1.0. Driver pins were Microsoft.Data.Sqlite 11.0.0, Npgsql 11.0.0 and
MySqlConnector 3.0.0. Native executables checked
`RuntimeFeature.IsDynamicCodeSupported == false`. Positive native publishes had
zero warnings/errors with TreatWarningsAsErrors and no newly added global AOT or
trimming suppression. This is experimental evidence, not a product acceptance run.

| Evidence | Observed result | Limit |
| --- | --- | --- |
| Original bag + concrete DTO wrappers | Six original Dapper call sites intercepted; three concrete DTO factories and the dynamic-bag command factory inspected | An arbitrary open generic Dapper call is not intercepted |
| Common typed DSL cases | 90 assertions across original bag, runtime bag, runtime layout and direct-driver controls | A representative AST, not the complete Korda language |
| SQL/data coverage | Zero to three parameters, all four optional-WHERE combinations, repeated identity, same-label distinct identities, NULL equality/IS NULL, IN lengths 0/1/3, apostrophe-bearing value, join and aggregate DTOs | The probe reused repeated named slots; the product deliberately emits one physical parameter per textual occurrence |
| Common lifetime coverage | Buffered async, complete/early-exit streams, pre-cancel, enlisted commit/rollback and initially closed/open connection restoration | Session concurrency and strict product mappings are separate implementation gates |
| Initialization fault | Six fault assertions, 96 total in the final SQLite probe: upstream gap reproduced; local override disposes; Dispose double fault preserves primary | Targeted initialization ownership, not exhaustive driver fault injection |
| Open generic negative | Default DAP016 Info build compiled without interception; explicitly elevated DAP016 caused build failure | Coverage inspection remains required |
| Object-template negative | Native publish succeeded; execution failed in Reflection.Emit/CreateParamInfoGenerator as expected | Only controlled explicit-entry bags are accepted by this proof |

### 5.1 Real server matrix

Each row ran a native executable against an actual local database. The shared
90-case fixture was identical; extra counts below include the selected advanced,
nested and network lifetime cases. A second, separate native pass exercised the
generic typed-cell visitor, because the first layout carrier used an object value.

| Profile and actual server | Main assertions passed | Additional typed-cell assertions | Additional observed behavior |
| --- | ---: | ---: | --- |
| SQLite 3.53.4 | 92 | 3 | Known nested DTO decoded with generated JSON metadata; long/string/nullable cell dispatch |
| PostgreSQL 18.7 | 99 | 4 | Explicit integer array, Jsonb and integer range; generated nested DTO; typed generic array dispatch; in-flight cancellation and timeout followed by reuse |
| MySQL 8.4.11 | 97 | 3 | Explicit MySqlDbType.JSON; generated nested DTO; long/string/nullable dispatch; in-flight cancellation and timeout followed by reuse |
| MariaDB 11.8.10 | 97 | 3 | Separate MariaDB SQL profile with the shared driver; explicit JSON; generated nested DTO; cancellation/timeout and reuse |

The typed visitor pass used `ValueCell<T>.Accept` → `Visit<T>` → a generic provider
encoder. Long, string and nullable-long closures ran on all four profiles; a
statically rooted NpgsqlParameter<int[]> closure ran on PostgreSQL. This confirms
Native AOT generic dispatch without MakeGenericType or runtime IL. Its compact
name/DbType carrier is still a probe: final SqlTypeDescriptor validation,
ParameterOccurrence policy and frozen values are specified in implementation-spec
and ORM-EXECUTION, not claimed as already implemented by this experiment.

PostgreSQL custom bag parameters used `ICustomQueryParameter.AddParameter` to add
NpgsqlParameter<int[]> with Array|Integer `[2,4,8]`, NpgsqlParameter<string> with
Jsonb `{"n":17,"text":"O'Reilly"}`, and an explicit integer range `[1,5)`.
Their returned values matched. MySQL/MariaDB JSON extraction returned 17 and
`O'Reilly` using an explicit MySqlParameter JSON type. Four profiles decoded the
known Engineering/Alice/Bob nested group through a source-generated
JsonSerializerContext with reflection JSON disabled. This nested smoke verifies
transport, known types and membership, not every ordering/presence/null case;
[Java execution and nesting](java-execution-options.md) and the nested packet contain the
separate ordering and aggregation-budget evidence.

The network cancellation fixture requested cancellation after 250 ms while a
10-second operation was running. Observed completion was approximately 252 ms on
PostgreSQL, 268 ms on MySQL and 256 ms on MariaDB; each then executed a fresh query.
The one-second command timeout cases also failed and permitted a subsequent query.
PostgreSQL surfaced NpgsqlException with TimeoutException; the MySQL families
surfaced MySqlException. These times are one bounded functional observation, not
latency service-level promises.

The MySQL-family sleep fixture needed a correction: standalone `SLEEP(10)` may
return an interruption result instead of an error. The accepted test was
`SELECT id FROM users WHERE SLEEP(10)=0 ORDER BY id`; PostgreSQL used
`SELECT CAST(1 AS BIGINT) FROM pg_sleep(10)`. This follows the documented
[MySQL 8.4 SLEEP behavior](https://dev.mysql.com/doc/refman/8.4/en/miscellaneous-functions.html).
An initial standalone-sleep assertion failed and was replaced for that documented
reason; it is not hidden as a successful cancellation test.

The database wrapper started only task-owned local data directories and loopback
servers, ran the consumer in the same execution scope and stopped every server in
finally. PostgreSQL, MySQL and MariaDB all reported normal termination. No system
service or external database was changed; raw logs and temporary projects remain
outside documentation repositories.

### 5.2 Comparable execution and binding costs

The finite experiment used one already-open SQLite connection, pooling disabled,
the same SQL, two Int64 parameters, two User DTO rows and no preparation/cache.
The original and explicit runtime paths used the **same upstream-generated User
row-factory body**, with only class name/accessibility adapted. The direct-driver
control used typed ordinals. Thus the comparison isolates argument/execution
choices more closely than an unrelated mapper comparison.

Each execution path warmed for 1,000 operations; each of seven rounds measured
20,000 operations with rotating path order. The process was pinned to one CPU,
results were consumed and forced collections occurred outside each interval.
Allocations used GetAllocatedBytesForCurrentThread on these synchronous paths.
The first campaign compared six paths. A later seven-path campaign added the
actual generic typed-cell visitor. Both are shown because the later host timings
were visibly noisier; selecting only favorable observations would overstate them.

| Execution path | First campaign median ns/op | Typed-cell campaign median ns/op | Typed-cell campaign min–max ns/op | B/op |
| --- | ---: | ---: | ---: | ---: |
| Direct driver | 14,024.21 | 14,991.25 | 13,861.92–16,597.08 | 1,832 |
| Original Dapper.AOT, static parameter object | 15,259.12 | 15,961.83 | 14,849.88–22,809.81 | 2,104 |
| Original Dapper.AOT, explicit bag | 15,981.97 | 17,209.73 | 15,737.51–24,348.36 | 2,664 |
| Explicit runtime, explicit bag | 15,892.73 | 16,222.89 | 15,751.98–21,919.55 | 2,664 |
| Explicit runtime, prebound object layout | 14,864.42 | 16,051.00 | 14,597.58–19,868.47 | 2,024 |
| Explicit runtime, prebound typed cells | Not in this campaign | 15,015.27 | 14,786.90–22,194.67 | 2,072 |
| Small DSL construction/render/bind + object-layout runtime | 15,934.97 | 16,228.47 | 15,911.48–26,688.04 | 4,208 |

The last path is the full small DSL probe with its existing object layout. It does
not pretend the final product typed immutable sidecar and strict mapper were
already present. Prebound paths exclude query construction and immutable-cell
capture. The static-object baseline creates its original small anonymous argument
object per call, as its generated API expects. The bag paths include fresh explicit
bag conversion per invocation.

Isolated measurements in the typed-cell campaign used 2,000 warmup operations,
then seven rotating 20,000-operation rounds. Command-binding rows create, bind and
dispose an unexecuted driver command; the bag row includes constructing its fresh
bag. They are direct experiments, not residuals obtained by subtracting unrelated
end-to-end means.

| Isolated operation | Median ns/op | Min–max ns/op | B/op |
| --- | ---: | ---: | ---: |
| Small DSL construction + render + bind | 685.49 | 657.26–708.20 | 2,184 |
| Explicit bag conversion only | 126.06 | 120.44–149.54 | 440 |
| Object-layout command binding | 321.87 | 306.67–448.60 | 432 |
| Typed-cell command binding | 317.03 | 301.18–562.17 | 480 |
| Explicit-bag command binding | 739.89 | 724.40–775.05 | 960 |

The measured typed route avoids 592 B/op versus the bag in this end-to-end fixture,
and 480 B/op in the isolated binding fixture. That stable allocation distinction,
the direct known-layout mechanism and successful typed AOT dispatch support its
selection. The latency ranges overlap and host noise prevents a strict speed
ranking. No zero-allocation, universal Dapper parity, cross-provider throughput or
complete-product performance claim follows. The actual accepted implementation
must run the finite ORM-PERFORMANCE packet, including its strict mapping and
invocation wrappers, before a performance acceptance decision.

### 5.3 Reproduction without retaining temporary projects

Create disposable net11.0/C#15 console projects with the pinned packages above,
PublishAot=true, InterceptorsNamespaces including Dapper.AOT, generated-file
emission and the explicit diagnostic policy. Use `[module: DapperAot]` for original
controls; explicit runtime factories do not require original call interception.

Create departments `(1, Engineering), (2, Operations)` and users
`(1,Alice,32,1,1), (2,Bob,18,1,1), (3,Carol,NULL,0,2), (4,Dana,44,1,2),
(5,Eve,18,1,NULL)`, with BIGINT id/age/active/department and a non-null name.
Map known User, JoinedUser and DepartmentTotal DTOs. The active predicate returns
IDs 1/2/4/5, adding age>=20 returns 1/4, adding name=Alice returns 1. NULL equality
returns none; IS NULL returns 3; IN `[1,3,5]` returns 1/3/5. A left join keeps Eve
with a NULL department. Department groups have two users each and maximum ages
32/44. Compare every field against a direct provider reader. Reset fixtures between
functional lanes; the performance campaign has the same committed Alice age of
33 for every measured path.

Use section 3 APIs for the explicit factories and section 5.1 SQL for actual
network cancellation. Add the typed-cell generic visitor pass separately. Publish
and run the native executable, inspect generated original calls, and execute the
generic/object-template negatives separately. Inject CreateDbParameter and Dispose
faults into a tracking DbCommand to verify the exact initialization rule.

A restore may require explicit public package sources. Once assets and native
compiler packages are present, `dotnet publish --no-restore -c Release -r linux-x64
/p:UseSharedCompilation=false /p:NuGetAudit=false` avoids package discovery. This
study's safe cached-assets retry followed an environment network approval block;
that event is not a Dapper capability failure. Reproduction pins package content
and server versions; it does not commit temporary source trees, generated code,
projects, raw samples, logs, databases or native binaries.

A separate final declaration check compiled the Execution infrastructure against
the actual Dapper.AOT1.1.0 package: GetCommand/AddParameters/UpdateParameters,
CanPrepare/TryRecycle, the internal typed visitor, preflight/reader services,
RowFactory overrides and all five selected command endpoints. Neutral schema
interface declarations also compiled. This was a C# signature/accessibility check,
not another runtime or native test. Contracts and schema declarations had zero
warnings; bare csc with net11 reference assemblies reported two visible CS1701
framework-unification warnings for the package's net10 System.Runtime and
System.Data.Common references. Only that warning number was nonfatal; no diagnostic
was hidden and no trim/AOT warning policy was relaxed.

## 6. Selected boundary and maintenance obligations

The default is **unmodified Dapper.AOT runtime + a small typed-layout
CommandFactory + generated strict RowFactory implementations**. Original
Dapper.AOT interception with controlled explicit bags remains a working
compatibility route and maintained benchmark control. Runtime SQL and dynamic
parameter count do not require an independently designed execution engine.

The inherited package owns connection-state restoration, command/reader execution,
async operations, row iteration, token storage and ordinary cleanup. The generated
mapping retains its Tokenize/Read protocol. Korda owns pure AST/layout/value
contracts, static provider encoding and prebound typed read delegates, logical/
physical first-row shape checks, deterministic connection/value/profile preflight, the small GetCommand initialization catch and its public invocation
lease. Provider drivers retain network/native I/O, pooling, protocol and transaction
operations. None of those responsibilities migrate to a Korda scheduler or reader
engine.

The exact infrastructure types, signatures and ordered state transitions are in
Plan ORM-EXECUTION; implementation-spec fixes their assembly boundaries. Generated
mapping registration is one immutable CompiledMapping per known DTO; Bind returns
an immutable factory for this projection/provider, never a shared mutable reader
state or an unbounded global shape cache. Every textual parameter occurrence has
its own physical parameter. Scalars use ElementIndex=-1; expanded lists use their
frozen zero-based index. PostgreSQL uses unnamed positional parameters; other
profiles use p0 onward. These product rules deliberately strengthen the small
original probe's permissive mapping and repeated-name policies.

Maintenance is correspondingly bounded: pin and inspect the upstream public
factory/runtime API on upgrades, run compiled generic consumers, preserve negative
fallback coverage, compare generated token/read logic, and rerun provider-specific
codec/fault cases. Source-derived generated algorithms require upstream attribution
and license review. A package upgrade is not permission to absorb all upstream
fallbacks, silently loosen strict projections or grow a private executor. Complete
language, package and performance acceptance remains future authorized work.
