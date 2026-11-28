# Korda.Orm execution, generation and Native AOT

Status: **proposed0.2.0, reopened research completed for architectural selection**.
The selected route reuses Dapper.AOT's mature runtime and normal generated factory
subclasses. This replaces the first delivery's own Binder/Projector default.
Product implementation/acceptance remains unauthorized and unexecuted.

## 1. Selected route and evidence authority

Keep the SQL language/renderer independent of execution. Export value-free typed
templates; execute them through pinned unmodified Dapper.AOT1.1.0 command/runtime
APIs, a small layout CommandFactory adapter, generated RowFactory<T> and mature
Npgsql/Microsoft.Data.Sqlite/MySqlConnector drivers. Explicit SQL/templates plus
manual static mapping also work without Fluent or a generator. Exact declarations,
ownership and algorithms are in [contracts](contracts.md) and
[implementation-spec](implementation-spec.md).

The substantive evidence is maintained in three focused documents:

- [Mature execution reuse](mature-execution.md): original-library DynamicParameters,
  runtime factories, initialization faults, typed values, four databases and fair
  comparison data with explicit limits.
- [Generator integration](generation-integration.md): actual incremental generator,
  generic facade, portable analyzer, consumer registration roots, strict mapping,
  same-compilation alternatives and a stable prebuild route.
- [Java/jOOQ execution options](java-execution-options.md): concrete Binding/Converter/
  Records.mapping inheritance and an actually executed C#/Graal/JDBC native path,
  including ownership, threads, deployment and boundary-cost evidence.

A clean AOT publish alone is insufficient: the object-template parameter control
published without warnings and failed when run. Conversely, 'DynamicParameters'
is not a reason to reject a route: explicit typed Add with no object template ran
successfully through the original Dapper.AOT generated path.

## 2. Source and version baseline

Source snapshots were inspected on 2026-11-28. These are research pins, not a claim
that every combination has been compiled, executed or performance-tested.

| Component | Stable release inspected | Commit | License at this snapshot |
| --- | --- | --- | --- |
| Dapper.AOT | 1.1.0 | [0e071bf05e54caecfa98c885b075fa3e247f3ecc](https://github.com/DapperLib/DapperAOT/tree/0e071bf05e54caecfa98c885b075fa3e247f3ecc) | Apache-2.0; separate branding restriction in `License.txt` |
| Dapper | 2.1.100 | [188094784256da61d7a37c43ea54c64213c2ce7c](https://github.com/DapperLib/Dapper/tree/188094784256da61d7a37c43ea54c64213c2ce7c) | Apache-2.0; separate logo notice |
| Npgsql | 11.0.0 | [4d174200ed48e3e3ab16419dbf84dd655da59de6](https://github.com/npgsql/npgsql/tree/4d174200ed48e3e3ab16419dbf84dd655da59de6) | PostgreSQL license |
| MySqlConnector | 3.0.0 | [95875a195369f0dd804f63ded2f95da3fed59ec2](https://github.com/mysql-net/MySqlConnector/tree/95875a195369f0dd804f63ded2f95da3fed59ec2) | MIT; inspect notices for selected optional dependencies |
| Microsoft.Data.Sqlite | 11.0.0, from EF Core | [9e685c7a52d1a344d133a3d370e458db97417b3f](https://github.com/dotnet/efcore/tree/9e685c7a52d1a344d133a3d370e458db97417b3f) | MIT; SQLitePCLRaw/native assets have their own provenance |

The [official SDK download page](https://dotnet.microsoft.com/en-us/download/dotnet/11.0)
identifies .NET 11.0.0 and SDK 11.0.100 as the stable baseline. The
[language version table](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-versioning)
maps `net11.0` to C# 15. Pin the SDK and language version in product implementation;
do not use a floating `latest` value or enable preview features by default.

Important distinctions between release availability and compatibility evidence:

- Dapper.AOT 1.1.0's own [package pins](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/Directory.Packages.props)
  use Dapper 2.1.79. Dapper 2.1.100 is newer; the reopened native matrix checked the declared combination and paths,
  not compatibility with every possible call shape.
- Npgsql 11.0.0 targets `net10.0`; MySqlConnector 3.0.0 includes `net11.0`.
  Microsoft.Data.Sqlite 11.0.0 is a stable package targeting `net10.0`, compatible
  with a `net11.0` consumer. Framework compatibility is not proof of every feature's
  AOT behavior. See their pinned project files and the
  [SQLite package](https://www.nuget.org/packages/Microsoft.Data.Sqlite/11.0.0).
- The EF Core repository also contains an ORM. Referencing Microsoft.Data.Sqlite
  does not require adopting EF Core's runtime or query model. Its
  [packaging project](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite/Microsoft.Data.Sqlite.csproj)
  references the SQLite provider core and `SQLitePCLRaw.bundle_e_sqlite3`.
- A source repository's build SDK may be a prerelease even when its published
  package is stable. Product consumers use the verified stable SDK; building an
  entire upstream repository is a different workflow.

## 3. What Dapper.AOT actually contributes

The following source review determines the design, rather than a general claim
that generated SQL automatically receives compile-time optimization.

| Pinned source and symbols | Observed behavior | Korda consequence |
| --- | --- | --- |
| [Inspection.cs](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT.Analyzers/Internal/Inspection.cs), `IsDapperMethod` | Recognizes selected extension methods on `Dapper.SqlMapper`; marks unsupported API families | An ordinary `Korda` execution method is not intercepted merely because it eventually uses SQL |
| [DapperAnalyzer.cs](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT.Analyzers/CodeAnalysis/DapperAnalyzer.cs), `SharedGetParametersToInclude` | Constant SQL can filter known members during generation; unknown SQL or command type defers selection | Runtime SQL is compatible with generated binding when the relevant parameter types are statically known |
| [NonConstant.input.cs](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/test/Dapper.AOT.Test/Interceptors/NonConstant.input.cs) and [expected generated output](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/test/Dapper.AOT.Test/Interceptors/NonConstant.output.cs) | A nonconstant SQL call generates member access and conditional parameter inclusion | Do not describe all runtime SQL as unsupported; distinguish dynamic SQL text from dynamic type discovery |
| [CommandFactory.cs](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandFactory.cs), `Include`, `AddParameters`, `UpdateParameters`, `TryRecycle` | The generic runtime can scan SQL for member names, create/update parameters, and optionally recycle commands | Korda already knows its layout and can avoid this rediscovery; command reuse needs explicit shape and ownership rules |
| [ParamPlan.cs](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT.Analyzers/CodeAnalysis/Model/ParamPlan.cs), `Create` | Projects Roslyn types into an equatable data model; separately recognizes a dynamic parameter bag | Use a deterministic generation model and separate a runtime value layout from compiler symbols |
| [DapperInterceptorGenerator.cs](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT.Analyzers/CodeAnalysis/DapperInterceptorGenerator.cs), `WriteTokenizeMethod`, `WriteArgs` | Emits parameter setup and column-name/type tokenization followed by typed reads; list expansion changes binding shape | Reuse the two-phase mapping design; record variable-arity list expansion in layout identity |
| [RowFactory.cs](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/RowFactory.cs) and [CommandT.Query.cs](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandT.Query.cs) | Tokenization happens per reader; typed reads process rows. Small synchronous token buffers use stack storage, while asynchronous paths lease storage | Retain the actual runtime loop/token storage; bind strict generated wrappers without replacing those mechanisms |
| [ApiSurface.expected.txt](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/test/Dapper.AOT.Test/ApiSurface.expected.txt) and generator `Parse` | API recognition is not full call-site acceptance. `CommandDefinition` overloads are diagnosed; type-based mapping and other families are refused; some parameter-shape combinations still skip generation | A bridge needs negative tests and actual generated-code inspection, not just a warning-free build |

### 3.1 Dynamic parameters are not one capability

Dapper.AOT 1.1.0 can delegate compatible dynamic parameter bags to an identity-free
`AddParameters(IDbCommand)` method. It also delegates supported list expansion to
Dapper. These paths preserve useful upstream behavior, but do not prove all bag
construction paths AOT-safe.

In Dapper 2.1.100, [DynamicParameters.cs](https://github.com/DapperLib/Dapper/blob/188094784256da61d7a37c43ea54c64213c2ce7c/Dapper/DynamicParameters.cs)
still processes object templates through `CreateParamInfoGenerator`; the corresponding
[SqlMapper.cs](https://github.com/DapperLib/Dapper/blob/188094784256da61d7a37c43ea54c64213c2ce7c/Dapper/SqlMapper.cs)
uses `DynamicMethod` for general parameter readers and object materializers.
Explicit typed values, arbitrary object templates, and runtime-selected DTO types
are separate cases. Korda's supported path cannot fall back to the latter two.

## 4. Reopened route comparison and final decision

| Route | Source-backed mechanism and actual evidence | Decision |
| --- | --- | --- |
| A Original Dapper.AOT | IsDynamicBag generates AddParameters; explicit typed bags/custom parameters plus known DTO callsites execute natively; open generic wrappers are not intercepted | Viable controlled compatibility/reference route; arbitrary caller bags/templates are excluded |
| B Generator integration | Normal SG writes explicit factories; physical prebuild-generated wrappers are also intercepted; experimental PreCompilation works in its restricted probe | Select ordinary SG to runtime factories; no preview API or second default build phase |
| C Mature runtime/source reuse | Public Command/CommandFactory/RowFactory, buffered/async/stream loops and disposal run representative DSL/known-DTO paths, plus supplemental typed-cell closures on four databases | Selected unmodified runtime with a small layout/strictness adapter; pin/upgrade tests contain API risk |
| D jOOQ execution source translation | DefaultBindContext, Binding/Converter, DefaultRecordMapper branches, Records.mapping and nested presence/JSON algorithms have concrete C# targets | Combine their type/conversion/constructor/nesting semantics with Dapper runtime; do not port JDBC execution loops unnecessarily |
| E Java AOT backend | C# Fluent to Graal shared library to real SQLite JDBC to known C# DTO passed27 native assertions, including cursor/transaction/thread ownership | Technically viable; no demonstrated advantage that warrants dual GC/ABI/deployment/async-cancel burden in this product |
| F Other mature combinations | EF Core compiled-query boundary, LinqToDB explicit raw-command/static-reader route, Jdbi/Micronaut/SimpleFlatMapper alternatives reviewed | Useful sources/alternatives; none demonstrated a simpler complete fit than the selected combination |
| G Own generated executor | First study established small pure-C# feasibility but did not prove reuse impossible | Retain only a diagnostic/control/fallback idea; no task implements a new execution engine |

### 4.1 Additional .NET alternatives, including attempted recovery

EF Core11's pinned [QueryCompiler](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/EFCore/Query/Internal/QueryCompiler.cs)
uses precompiled queries when available and otherwise gates runtime compilation
on RuntimeFeature.IsDynamicCodeSupported. The Native AOT failure branch is a
current library query-compiler policy, not a limit on dynamic SQL strings or known
typed parameters. Adopting EF's model/tracking/query pipeline adds responsibilities
that the SQL-first contract does not need; Microsoft.Data.Sqlite is independently
reused without the EF ORM.

LinqToDB6.4.0 source was inspected at
[82fbf0f91399cc8c9cea22d09dcae20e4d7568c6](https://github.com/linq2db/linq2db/tree/82fbf0f91399cc8c9cea22d09dcae20e4d7568c6).
Its CommandInfo accepts raw SQL, explicit DataParameter[] and a static
Func<DbDataReader,T>, including async buffered/streaming operations. That made it
a real candidate rather than a name-only comparison. A disposable typed-field DSL
produced two runtime predicate shapes for SQLite with explicit Int64 parameters
and a direct Item(long,string,long?) reader under SDK11 Native AOT.

Three progressively narrower attempts were made. First, strict native publication
failed IL2104/IL3053 aggregate warnings and IL3000 Assembly.Location use. Second,
explicit SQLiteProvider.Microsoft, ResolveSQLite(typeof(SqliteConnection).Assembly),
AutoDetectProvider=false and Compilation.SetExpressionCompiler using interpreted
expressions produced a native binary only after leaving warnings visible but not
fatal for this diagnostic experiment. There were254 IL2026 and106 IL3050 messages,
plus reflection/dataflow warnings; it failed at runtime because the reflective
provider adapter could not resolve SqliteTransaction. Third, explicitly rooting
the Microsoft.Data.Sqlite assembly moved past that failure but exposed a trimmed
reflection/static-initializer failure in Methods.LinqToDB.SqlExt/AsyncFactory.
No full native query success is claimed for these attempts.

These are concrete current-library reflection/reachability integration costs,
not proof LinqToDB or expression interpretation can never work in AOT. A statically
bound provider adapter, further precise roots or a source adaptation could be
investigated if this route offered a needed advantage. Here the selected Dapper
runtime already passes the representative path without these warning/rooting
burdens and without bringing a second LINQ/query model. A broad warning suppression
or a copied replacement executor is not an acceptable way to label the probe
clean. Further equivalent trials are not required to establish research condition A.

### 4.2 What Korda must implement, and why

The remaining code is the explicit product boundary: source-translated SQL nodes
and dialect rules; immutable typed values/layouts; provider codec selection from
already-known SQL IDs; a derived command factory; SG type/constructor analysis and
derived row factories; strict logical/physical shape validation; session admission
and lazy single-use iterator forwarding; offline schema/generation/packaging.
Every piece has a source/behavior mapping and concrete implementation packet.

These adapters cannot be replaced by simply changing a library namespace. jOOQ's
Java/JDBC object model cannot be referenced as C# types, and Dapper's callsite/SQL
member discovery does not consume Korda's typed layout or nested logical shape.
The translation changes those boundaries while retaining the mature algorithms
and runtime loops. It does not copy their ideas and then rebuild all execution.

## 5. Exact execution mechanism and constrained adaptations

The terminal performs pre-cancellation, profile/value/mapping/connection validation,
then acquires one session lease and consumes one invocation. It creates
DapperAotExtensions.Command(connection,transaction,sql,Text,timeout,CommandFactory)
and calls QueryBuffered/QueryBufferedAsync/QueryUnbufferedAsync or Execute/ExecuteAsync.
Return the lease only after upstream operation/iterator disposal. Sync uses sync
endpoints; there is no Task.Run or sync-over-async wrapper.

The parameter factory visits each final occurrence and its typed cell. A provider
ValidateValue<T> runs before admission; Create<T> returns one fully configured
parameter. No SQL/name scan or object-template discovery is needed. PG uses typed
positional parameters; SQLite/MySQL normal Value APIs may box. Static conversions
are pure/deterministic, and mutable input is snapshotted first. No universal zero
allocation claim follows from the typed visitor.

Mapping binds declared logical members to immutable typed read delegates, then
Tokenize validates actual physical metadata before the first row. Optional nested
payload is read only when its discriminator is present; collections use bounded
static JSON readers. Closed scalar/row/DTO registration is explicitly rooted,
including cross-assembly final-consumer roots. The mature runtime still owns row
iteration, token buffers and reader/command cleanup.

The defensive GetCommand override covers locally created command initialization
and parameter binding before returning the command. Preserve a primary exception
and attach a second disposal exception safely. Upstream also assigns connection/
transaction/timeout after the factory returns; this override does not promise to
repair arbitrary throwing custom DbCommand setters. The selected adapters validate
legal values/connection/transaction association first, and callers must not dispose
or mutate borrowed resources concurrently. A future adapter unable to satisfy that
precondition needs a separately reviewed narrow upstream fix, not an unreported
DbCommand proxy or second loop.

Command timeout null maps to -1 (driver default); explicit0 is unlimited. No command
recycling/prepare/global shape cache is enabled initially. Dapper's empty result
skips Tokenize; the contract deliberately promises strict validation before a
materialized row, not an exception for every empty schema mismatch. These policies
and the exact failure codes are normative in implementation-spec and ORM-EXECUTION.

## 6. Provider, AOT and future acceptance boundaries

Npgsql/SQLite/MySqlConnector retain their protocol, pool and transaction machinery.
Profiles distinguish PostgreSQL18, SQLite>=3.45, MySQL8.4 and MariaDB11.8. The actual
reopened research ran SQLite3.53.4, PostgreSQL18.7, MySQL8.4.11 and MariaDB11.8.10.
Each feature/profile still earns product support through its own implemented matrix.
Network cancellation/timeout behavior is separate from SQLite's synchronous async
facade and busy-timeout behavior. No private worker pretends to add cancellation.

Advanced codecs preserve JSON versus JSONB, SQL NULL versus JSON null, temporal
kind/precision, decimal range and array/range identity. PG arrays are explicitly
sequence-normalized because the inspected Npgsql reader discards lower bounds;
no false claim of detecting a discarded bound is made. Driver-specific types stay
inside provider leaves. Nested ordered SQL/MariaDB budget guards and SQLite scalar/
RETURNING boundaries have focused actual SQL evidence in java-execution-options.

Product acceptance still requires full immutable-model/strict-factory integration,
all promised operation/profile cells, lifecycle races, exact seven packages,
portable analyzer/IDE hosting, documented API/XML and preregistered public-path
performance budgets. The research measurements compare finite representative paths
and disclose missing final wrappers; they do not establish production parity or
zero framework GC. [Validation](validation.md) separates these evidence levels.

## 7. Source maintenance and distribution

Pin the exact upstream Runtime API and rerun generated-source/API/native/fault tests
on every upgrade. The original-interceptor compatibility route additionally audits
all generation-skipping diagnostics, generated coverage and the object-template
negative control. Do not maintain an unneeded Dapper runtime fork by default.

Preserve applicable license texts/notices and source adaptations. Dapper.AOT and
Dapper use the reviewed Apache-2.0 source licenses with separate branding notices;
Npgsql's PostgreSQL license, MySqlConnector/SQLite managed MIT and actual native
assets have separate provenance. The research Java backend is not shipped by the
selected package set. See [upstream-policy](upstream-policy.md) for exact linked
sources, attribution and the bounded upgrade procedure.
