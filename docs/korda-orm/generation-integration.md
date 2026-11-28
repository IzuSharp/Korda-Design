# Generator integration and executable implementation specification

Status: proposed revision for the reopened `Korda-Orm-01` study. This document
fixes the generator, mapping-discovery and offline-schema mechanisms for subsequent
implementation; it does not authorize product work. The shared names and session
boundary in [contracts.md](contracts.md) and
[implementation-spec.md](implementation-spec.md) are normative. The bounded
experiments below establish specific integration paths, not a complete generator
or packaged product.

## 1. Selected integration

Use a Korda incremental generator to emit concrete Dapper.AOT `RowFactory<T>`
implementations, mapping descriptors and static registration. Use Dapper.AOT's
unchanged runtime for commands, synchronous/asynchronous execution, buffering,
streaming and normal reader/command cleanup. The execution adapter supplies one
layout-driven `CommandFactory<BoundArguments>`; its parameters come from the
renderer's typed layout, not a second scan of the SQL string. The small defensive
command-initialization override is specified in [mature-execution.md](mature-execution.md).

This selects a mature runtime with a different compile-time frontend. It does
not create a second execution loop or make an interceptor fork a prerequisite.
Dapper.AOT's existing parameter and row planning/emission code is the source
baseline for the frontend; the exact deviations are enumerated below. The
existing Dapper generator remains an independently tested direct-use route.

The normal consumer writes a typed query, an ordinary known DTO/record and, when
the type is not already generated from schema, one `[DbRow]` annotation. The type
need not be `partial`, inherit a Korda base class, implement a mapping interface,
or contain Dapper calls. The generic execution terminal resolves the compiled
mapping automatically. The pure query and projection types have no Dapper or
provider dependency.

### Fixed mapping discovery

- `[DbRow]` is an execution-domain attribute in `Korda.Orm.Execution`. It applies
  directly to a concrete class or struct declared in the consuming compilation.
  It is not inherited, discovered through reflection or scanned across loaded
  assemblies.
- The generator emits one immutable compiled mapping per opted-in declared type
  in that type's assembly. A generated public registrar has an explicit static
  constructor that registers it in the generic `Mapping<T>` slot. Its parameterless
  `EnsureRegistered` method is the shared entry point for declaring-module and
  final-consumer generated initializers. `CompiledMapping<T>.Bind(ResultShape, ProviderServices)`
  validates a particular projection and returns an immutable bound Dapper row
  factory; no live reader or mutable shape state is stored in the global slot.
- `Mapping<T>.Register(CompiledMapping<T>)` uses `Interlocked.CompareExchange`
  against an initially null slot. Duplicate registration is an initialization
  error, never last-writer-wins. The registration path contains no application
  callbacks, database access, configuration lookup or connection creation.
- `Mapping<T>.Get()` returns the registered immutable mapping or fails with the
  missing-mapping diagnostic before a command is sent. There is no `Type`-keyed
  dictionary, reflection mapper, `MakeGenericType`, assembly scanning or runtime
  IL fallback.
- `Query<T>.ToListAsync(session, cancellationToken)` and
  `Query<T>.StreamAsync(session, cancellationToken)` use that same slot even when
  the call is inside an ordinary open-generic helper. The helper does not need an
  interceptor or access to the DTO's members.
- An external, inaccessible or intentionally hand-mapped DTO uses the explicit
  mapping terminal overload defined by C04. It supplies a static mapping value
  for that invocation; it does not replace a generated global registration.

The infrastructure declarations are fixed by `ORM-EXECUTION`; the generator emits
subclasses of this surface rather than a second local mapping API:

```csharp
public sealed record RowMember(int Index, string Alias, Type ClrType,
    bool IsNullable, string? ConversionId = null);
public abstract class CompiledMapping<T>
{
    protected CompiledMapping(ImmutableArray<RowMember> members);
    public ImmutableArray<RowMember> Members { get; }
    public abstract Dapper.RowFactory<T> Bind(ResultShape shape, ProviderServices services);
}
public static class Mapping<T>
{
    public static void Register(CompiledMapping<T> mapping);
    public static CompiledMapping<T> Get();
}
```

These are declaration signatures in `Korda.Orm.Execution`, not executable method
bodies. `Bind` calls `ProviderServices.ValidateResult` for each selected member;
explicit-mapping terminal overloads receive one `CompiledMapping<T>` per invocation.

Only the DTO-declaring compilation emits its default registrar/mapping. It also
emits `CompiledRow(typeof(T), typeof(Registrar))` assembly metadata. The final
consumer runs the generator, reads those markers as compiler symbols, and emits
direct calls to the same public registrar. Referencing a DTO must not generate a
second mapping or Register call. Its registrar's explicit static constructor runs
once even if several generated initializers request it.

The consumer root is required. A library-only native negative control lost its
registration while the same managed program succeeded; an assembly reference and
a marker are not sufficient reachability guarantees. The fixed protocol uses no
runtime attribute scan or reflection. A no-generator caller explicitly invokes a
public registrar or supplies a static mapping. Ordinary application code has no
handwritten registration because its own generator emits the root calls. A separately
compiled `Models` assembly, generic execution assembly and native consumer were
exercised in EXP-GEN-RUNTIME below.

## 2. Candidate generation mechanisms and decision

| Mechanism | Actual boundary and evidence | Decision |
| --- | --- | --- |
| Original Dapper call in ordinary source | The pinned generator recognizes supported `Dapper.SqlMapper` extension-method symbols and emits runtime factories/interceptors. Dynamic SQL and an explicit `DynamicParameters` bag were separately exercised. | Supported direct-use alternative; do not confuse a Korda method name with a recognized Dapper symbol. |
| Korda SG emits a Dapper call through ordinary `RegisterSourceOutput` | An actual Roslyn driver run produced zero Dapper interceptors for the generated call, while the final C# compilation had no errors. | Not a complete AOT integration. An apparently successful C# build does not prove interception. |
| One SG emits runtime factories directly | An actual incremental generator emitted row factories, a command factory and module initialization; the resulting whole path ran as a native executable. | Selected default. One compilation, no generator ordering and no custom interceptor protocol. |
| Physical source generation before `CoreCompile` | A local C# tool read a shape manifest and generated a DTO plus concrete Fluent terminal into `obj`; unmodified Dapper.AOT generated an interceptor and the native program executed both query shapes. | Feasible stable alternative when reusing the original Dapper frontend is more valuable than the additional build stage. Not required by the selected default. |
| Explicit two-pass Roslyn driver / separate assembly compilation | Pass 1 output can be fed into a new compilation before running the second generator; concrete calls in a referenced assembly are handled while that assembly is built. The physical-input driver case and separate-model-assembly runtime case were exercised. | Feasible composition rule. Do not recursively run arbitrary generators from inside another generator; use an explicit build/tool boundary if adopted. |
| `RegisterPostInitializationOutput` | Fixed declarations are visible before normal generation, but this callback has no schema/source inputs. | Use only for fixed helper declarations, not input-dependent DTO/SQL generation. |
| `RegisterPreCompilationSourceOutput` | SDK 11.0.100's Roslyn assembly reports version 5.12.0.0 and marks this API `RSEXPERIMENTAL007`. An actual AdditionalFiles-based run made the call visible and produced one Dapper interceptor. Compilation/syntax-dependent inputs are forbidden in that phase. | Technically viable experiment; not a production prerequisite. It does not solve arbitrary C#-symbol-dependent generator ordering. |
| Extend Dapper's interceptor frontend | Its symbol recognition, `ParamPlan`, `RowPlan`, emitter and tests are available source. A Korda-recognition branch can feed those plans. | A viable maintenance option if the chosen frontend becomes larger than a narrow adapter; no current core requirement justifies a fork. |
| Runtime reflection or dynamic IL | Not needed by any successful route above. | No fallback path. |

The original generator's supported `SqlMapper` overload selection is a library
implementation boundary. The ordinary-generator visibility rule is a compiler
pipeline boundary. Neither is a prohibition on dynamic SQL, dynamic parameter
counts or Native AOT.

## 3. Source inheritance and intentional deviations

Dapper.AOT is pinned to `0e071bf05e54caecfa98c885b075fa3e247f3ecc` / 1.1.0.
The implementation packets must retain these source links and review the
corresponding upstream tests when adapting an algorithm.

| Upstream source | Reused implementation or mechanism | Deliberate Korda difference |
| --- | --- | --- |
| [DapperInterceptorGenerator.Initialize/Parse](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT.Analyzers/CodeAnalysis/DapperInterceptorGenerator.cs) | Incremental input projection, separate parameter/row plans and source emission. | `[DbRow]` and schema models supply row plans; Korda does not pretend its terminals are `SqlMapper` methods. |
| [Inspection.IsDapperMethod](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT.Analyzers/Internal/Inspection.cs) | Exact method-symbol classification and explicit unsupported paths. | Korda has its own exact terminal-symbol diagnostics. A similar method name is insufficient. |
| [ParamPlan](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT.Analyzers/CodeAnalysis/Model/ParamPlan.cs) | Build-time type/member information projected into equatable data; explicit dynamic-bag distinction. | Runtime slot occurrence/type metadata is already supplied by C03, so the direct-runtime path does not rediscover used parameter names. |
| [RowPlan](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT.Analyzers/CodeAnalysis/Model/RowPlan.cs) and generator row emission | Direct constructor/init/member access, nullable handling and tokenized typed reads. | Strict declared projection matching; missing/duplicate/unexpected columns and unexpected NULL are errors rather than unspecified CLR defaults. |
| [RowFactory<T>](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/RowFactory.cs) | Public `Tokenize`/`Read` extension seam and runtime token-buffer handling. | Exact declared aliases use ordinal comparison. Do not silently normalize `UserId` and `User_Id` into one member. |
| [CommandFactory<T>](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandFactory.cs) | Command creation/binding/update lifecycle, cancellation and post-processing hooks. | Typed layout binding omits SQL `Include` searches; a local initialization-failure guard disposes a command that has not yet reached the runtime state object. |
| [CommandT.Query](https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandT.Query.cs) | The actual buffered, asynchronous and streaming execution implementations. | No replacement loop. Tokenization remains conditional on a first row existing. |
| jOOQ [JavaGenerator](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ-codegen/src/main/java/org/jooq/codegen/JavaGenerator.java), [DefaultGeneratorStrategy](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ-codegen/src/main/java/org/jooq/codegen/DefaultGeneratorStrategy.java), [GenerationUtil.convertToIdentifier](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ-codegen/src/main/java/org/jooq/codegen/GenerationUtil.java) | Separate metadata acquisition, semantic schema input, naming policy and typed declarations. | C# identifiers, nullable syntax and static factory registration replace Java/JDBC-specific generated machinery. |

The selected implementation reuses the Dapper.AOT package runtime directly.
Adapted generator source keeps its Apache-2.0 provenance and notices, and the
upstream file/symbol plus local modification reason are recorded as required by
[upstream-policy.md](upstream-policy.md). Do not copy the entire upstream tree into
the product or claim the bounded research generator is the complete upstream emitter.

## 4. Fixed generator pipeline

The product generator assembly targets **netstandard2.0** with C# 15 at build time.
Its compile-time Roslyn baseline is **Microsoft.CodeAnalysis.Common/CSharp 4.14.0**;
these dependencies are `PrivateAssets=all`. The initial qualified host is SDK
11.0.100 / Roslyn 5.12.0 on Linux. A target-framework choice is not proof of every
IDE or older compiler host; additional hosts require their declared host tests.
The default path calls no experimental Roslyn API and emits no interceptors.

Use these ordered stages; no implementation task chooses a replacement architecture:

1. `ForAttributeWithMetadataName("Korda.Orm.Execution.DbRowAttribute", ...)`
   selects explicit source DTO declarations. The transform reads symbols only
   here, validates accessibility/construction and produces a `RowPlan` value.
2. `AdditionalTextsProvider` selects only `.korda-schema.json` inputs. Parse and
   validate each against section 7; project the result into the same neutral
   generation models. File names/hashes, not absolute host paths, determine hint
   names. The Schema generator supplies its own generated DTO's `RowPlan` directly;
   it does not ask another SG to rediscover its output.
3. Models contain fully qualified type names, immutable equatable arrays, member
   alias/type/nullability/conversion data, constructor parameter order, stable
   source locations for diagnostics and explicit generation options. No output
   model retains `Compilation`, `ISymbol`, `SemanticModel` or syntax trees.
4. Validate each row/model independently before collecting registration entries.
   An invalid row emits diagnostics and no executable mapper. Valid independent
   rows may still emit their own files; the error prevents a successful consumer
   build.
5. Emit one stable source file per row, table/type descriptor and registration
   group. Ordering is ordinal by stable metadata identity. Use an indented text
   writer, deterministic newlines and escaped identifiers/string literals.
6. Collect only small registration descriptors; emit public per-row registrars
   and one module initializer per compilation, with EnsureRegistered calls sorted
   by fully qualified CLR metadata name. The final-consumer compilation also reads
   referenced CompiledRow(rowType,registrarType) metadata and emits direct registrar
   calls. Built-in closed Row arities use Execution's generic RowMappings registrar;
   consumer type/operation symbols or explicit DbCompileRow assembly hints supply
   their closed type arguments.
   Do not put every row's source behind a compilation-wide `Collect` stage.
7. A companion analyzer recognizes exact terminal symbols, reports missing or
   unsupported mappings, and makes known unsupported paths errors. Runtime
   `Mapping<T>.Get()` remains the guard for separately compiled generic code.
8. Generated factories refer only to core/execution contracts, Dapper.AOT runtime
   and statically registered codecs. Roslyn, schema discovery and generator
   dependencies are absent from the application's runtime dependency closure.

JSON parsing reuses **System.Text.Json 11.0.0**. The official package includes a
netstandard2.0 asset; do not write a custom JSON parser. Link the Schema module's
small format reader/model sources into the generator so validation rules have one
owner. Register that linked-source dependency in product CI. Package only required
private analyzer dependencies beside the generator, never the host's Roslyn
assemblies. The exact package closure is specified in `ORM-PACKAGE`.

## 5. DTO construction, result validation and diagnostics

### Construction plan

A supported DTO is a non-abstract, closed, accessible class or struct. Public or
internal nested types are supported only when the generated helper can name the
complete containing chain. Private/protected inaccessible types or members fail.
No `Activator`, private-access reflection, uninitialized object construction or
runtime constructor search is emitted.

Inspect directly declared mapped properties and explicitly supported inherited
public properties in base-to-derived order, rejecting hidden members with the
same effective alias. Fields are supported only when explicitly opted in by the
shared mapping attribute contract. A property must have an accessible getter for
metadata and an accessible setter/init if it is assigned after construction.

Constructor choice is deterministic:

1. If exactly one accessible constructor has `[DbConstructor]`, use it and validate
   every parameter/member correspondence. Two marked constructors are an error.
2. Otherwise, use the single valid accessible non-parameterless constructor.
   Every parameter must bind a unique mapped CLR member with a compatible type;
   every remaining member must be assignable. Ref/in/out parameters are excluded. A record's copy
   constructor is not a candidate. Multiple valid constructors are an error.
3. Otherwise, use an accessible parameterless constructor and a complete object
   initializer for required/init/settable mapped members. Missing required members
   are an error; defaults do not silently satisfy a required result column.
4. Parameter/member matching uses exact declared names first. A case-insensitive
   fallback is permitted only for constructor parameter spelling when it resolves
   to exactly one member. SQL result alias matching remains ordinal and explicit.
5. A constructor without SetsRequiredMembers requires initializer assignments for
   every C# required member, including a member also passed as an argument. Reject
   inaccessible required assignments. Constructor arguments follow constructor
   parameter order, independently of SQL column order. Remaining init/setter assignments appear in deterministic member
   order. Emit one construction per row after all values are read successfully.

A custom conversion must identify an explicit typed codec/conversion declaration.
Generation checks static symbols and declared CLR compatibility; execution preflight
checks that the selected provider actually has the closed codec. The schema CLI
does not load application plugins or execute user code to prove that registration.
Different SQL types can intentionally map to the same CLR type; compare the
registered conversion contract rather than rejecting every unequal SQL type ID.
An unregistered conversion is not an excuse for `object` or `Convert.ChangeType`.

### Strict mapping algorithm

Preflight matches the pure `Projection<T>.ResultShape` against the compiled member
descriptor: degree, aliases, SQL/CLR compatibility through the declared codec,
nullable-to-nonnullable rules and nested presence policy. This does not inspect
runtime DTO objects. Reject missing, duplicate, unknown or incompatible mappings
before sending a command.

`Bind` computes an immutable ordered read plan: expected aliases, member indexes
and typed codecs for that specific projection/provider. It checks all members
exactly once, with a local seen bitset (`ulong` through 64 members, temporary
bitset beyond that). Reordered projections produce a correspondingly reordered
plan; they never mutate the registered mapping.

At the first materialized row, generated `Tokenize` must:

1. Require the reader field count to match the bound plan's degree.
2. Require `reader.GetName(i)` to equal the plan's alias at the same ordinal using
   ordinal comparison. Generated SQL explicitly quotes aliases. A reader with the
   right alias set but a different order from the declared template fails.
3. Copy the prevalidated target member index into `tokens[readerOrdinal]`; do not
   rediscover DTO members or accept a different mapping merely because names fit.
4. Validate provider getter/codec compatibility with actual reader metadata and
   retain only immutable per-reader state where needed. A stateless scalar map
   returns null state.
5. Return only after all checks pass. Diagnostics identify shape/column/type;
   parameter values and connection strings are excluded.

`Bind` invokes ProviderServices.BindReader<TMember> once per known scalar member
and stores typed readonly Func<DbDataReader,int,TMember> delegates. Tokenize calls
ProviderServices.ValidateReaderColumn for the actual physical representation.
`Read` walks reader columns once in ordinal order, dispatches on cached tokens,
invokes those delegates and stores values in typed locals. The delegate owns
DBNull behavior: non-null descriptors fail KORM-MAP-003 and allowed nullable
representations return default(TMember). It then invokes the chosen constructor/object initializer. Any adapted direct-getter nullable value
emission must use `default(T?)` or an explicit `(T?)null`; the expression
`isNull ? default : reader.GetInt64(i)` can infer nonnullable `long` and produce
zero before lifting. That exact bug was found and corrected in the research
emitter, and is a mandatory regression fixture.

This uses Dapper.AOT's tokenization and row-loop seam. Its runtime does not call
`Tokenize` for an empty result. Therefore the guarantee is **validation before the
first materialized row**, not schema-drift detection for every empty query. Query
preflight still validates the declared descriptor before execution.

### Diagnostic contract

These are required product diagnostic IDs; the bounded prototype used its own
`KORMGEN001` marker and is not claimed to implement the complete catalogue.

| ID | Trigger | Required action/output |
| --- | --- | --- |
| ORMGEN001 | Inaccessible, open-generic, abstract or otherwise unsupported mapped type | Error at the type or explicit mapping request; no mapper emitted |
| ORMGEN002 | No valid constructor, ambiguous constructors, or inaccessible required assignment | Error listing the conflicting member/constructor signatures |
| ORMGEN003 | Duplicate effective SQL alias or identifier collision after an override | Error showing both source locations; no arbitrary winner |
| ORMGEN004 | Statically known SQL/CLR mismatch or missing explicit conversion declaration | Error naming the declared types/conversion; actual provider registration is checked during Bind |
| ORMGEN005 | Nullable source mapped to a nonnullable required member without an explicit checked policy | Error at the member/projection contract |
| ORMGEN006 | Known terminal requests a DTO without generated or explicit static mapping | Error at the terminal; runtime missing-map guard remains for generic boundaries |
| ORMGEN007 | Invalid/stale schema format or unresolved schema reference | Error at the AdditionalFile JSON pointer and source path |
| ORMGEN008 | Mapping generation requested without the execution reference | Error explaining the required package or `generateMappings=false` |
| ORMGEN009 | Two schema inputs declare the same stable object/type ID inconsistently | Error on both inputs; identical duplicates are still rejected to preserve ownership |
| ORMGEN010 | Unsupported runtime-only CLR type selection | Error; suggest a declared dynamic row or known static DTO |

## 6. Actual generator experiments and limits

All temporary projects, generated code, logs and binaries stay outside the two
document repositories. These are bounded research programs, not shipped code.

| Experiment | Observed result | Important limit |
| --- | --- | --- |
| EXP-GEN-RUNTIME | Four separate Core/Runtime/Models/Consumer assemblies; a real incremental generator emitted two DTO factories, a common command factory and module initialization. Linux native program passed 21 checks, including an immutable per-invocation bound row factory. | Small scalar whitelist and SQL node subset; not full C03 template/value separation or all codecs. |
| EXP-GEN-PORTABLE | The generator compiled against netstandard2.0 reference assemblies, Roslyn 4.14.0 and Immutable 9.0.0; SDK 11/Roslyn 5.12 loaded it and generated the Models assembly without warnings. Unsupported `Uri` produced the expected KORMGEN001 compiler failure. | Actual tested host only; no claimed IDE matrix or final analyzer nupkg consumer test. |
| EXP-GEN-VISIBILITY | One ordinary AdditionalFiles SG and unmodified Dapper.AOT ran in the same Roslyn driver: ordinary output produced 0 interceptors; experimental pre-compilation output and physical compiler input each produced 1. All resulting C# compilations had zero compiler errors. | Demonstrates visibility; ordinary C# compilation alone does not establish AOT safety. |
| EXP-GEN-PREBUILD | A C# tool read a JSON DTO manifest before `CoreCompile`; generated physical source was intercepted by unmodified Dapper.AOT. Native executable passed 3 checks, including two SQL shapes; publish produced no warnings. | A small manifest/tool, not a complete IDE-integrated prebuild product. |
| EXP-GEN-ROOTING | Library-only closed-Row registration passed managed execution but the native binary failed its missing-map guard. Adding final-consumer SG roots passed 7 native assertions, including two model assemblies sharing one generic registration and strict explicit duplicate rejection. The actual DTO/Dapper probe was then rebuilt with public registrars and consumer-generated calls and passed the same 21 native cases with zero publish warnings. | The 21 cases are one suite, not 42 independent assertions; the 7-case registration probe has no database and is separate from row/driver correctness. |
| EXP-SCHEMA-SURFACE | The exact portable schema declaration slice compiled against net11.0 and netstandard2.0 references with warnings-as-errors and zero warnings. | Signature/portability proof only; reader, validator, naming and CLI behavior remain product implementation tasks. |

EXP-GEN-RUNTIME covered dynamic typed predicates, changing parameter counts,
expanded and empty IN lists, nullable record construction, init-only DTOs,
reordered projections, an open-generic terminal helper, buffered async execution,
stream early disposal, pre-cancellation, a borrowed transaction/rollback, missing
mapping and invalid nonempty result shape. The added strict-plan cases reject an
actual reader whose aliases have the correct set but the wrong declared order,
reject duplicate declared aliases before execution, retain connection usability
after shape failure, and verify that an empty reader does not call Tokenize. Its
Native AOT publish produced no warnings. Provider-specific cancellation and full row-shape/constructor cases
remain the explicitly enumerated product fixtures.

The SDK-host research setup initially used a net11 generator. The portable-target
experiment then established the selected netstandard2.0/Roslyn 4.14 host path.
For local dependency isolation, libraries were compiled with the SDK compiler and
known reference assemblies; the native consumer used already-restored package
assets. No network restore is a generator requirement. The research did not
package this prototype as a production analyzer or reuse raw generated files as
formal documentation artifacts.

Reproduction: use SDK 11.0.100, Dapper.AOT 1.1.0 and Microsoft.Data.Sqlite 11.0.0;
create separate driver-free model, execution, DTO/generator and native consumer
projects. Emit compiler-generated files locally, inspect the actual `RowFactory`,
`CommandFactory` and module-initializer outputs, then publish `linux-x64` with
`PublishAot=true`, execute the native binary and require
`RuntimeFeature.IsDynamicCodeSupported == false`. The two-stage variant generates
physical input under `obj` before `CoreCompile` and enables the original Dapper
interceptor namespace. The visibility fixture runs actual generator drivers with
identical initial source and compares emitted interceptor counts.

## 7. Offline schema v1 contract

The public schema snapshot is UTF-8 JSON named `*.korda-schema.json`. The complete
portable C# record declarations and their property-order-to-wire mapping are fixed
in the companion `ORM-SCHEMA` implementation packet; they compile against both
net11.0 and netstandard2.0. That is a declaration compatibility check, not a claim
that the full reader/validator has been implemented. It is a
maintained input to generation, not a live connection specification. The root has
exactly these fields, in this serialization order:

| Field | Type and rule |
| --- | --- |
| `formatVersion` | Integer 1; any other value is an error, not a best-effort parse |
| `profile` | `{ id, family, serverVersion, settings }`; family is PostgreSql, Sqlite, MySql or MariaDb; settings are sorted name/value strings and contain only semantics-relevant nonsecret settings |
| `generation` | `{ namespace, generateRows, generateMappings }`; mappings require rows and an execution reference; false/false is a valid pure metadata input |
| `types` | Ordered type declarations: stable `id`, qualified `storeName`, semantic `kind`, optional base/element reference, ordered enum labels, dimensions/facets and optional typed `binding` (`clrTypeName`, `sqlTypeMember`, `codecId`) |
| `relations` | Ordered table/view declarations described below |
| `overrides` | Ordered explicit naming/type/codec overrides addressed by stable object/member IDs; unknown targets fail |

A qualified name contains nullable `catalog`, nullable `schema` and nonempty
`name` strings. Preserve exact text; do not lowercase database identifiers or
normalize Unicode into a potentially different SQL name. Stable IDs use kind
plus length-prefixed UTF-8 name segments; null is encoded as `-1:`, and a real
empty segment is distinct. IDs must be deterministic and cannot be fresh GUIDs.

Each relation has `id`, `kind` (`table` or `view`), `name`, `columns`, `keys`,
`foreignKeys` and `options`. Columns are ordered by zero-based ordinal and contain
`id`, `ordinal`, `name`, `typeId`, `nullable`, `facets`, `dimensions`,
`generation`, `hidden`, `options` and explicit nullable `clrName`. Column facets
retain typmods independently of physical type identity; two varchar lengths need
not fabricate two database type identities. Column generation is a tagged value:
`none`, `default`, `identityAlways`, `identityByDefault`, `computedStored` or
`computedVirtual`; SQL expression text is present only for default/computed
forms. The generation record also has an explicit nullable identity record
(start/increment/minimum/maximum/cache/cycle); exact integer metadata is serialized
as invariant strings. Identity attributes are structural metadata, not inferred
from rows or current sequence contents.

Keys have stable ID, name, kind (`primary` or `unique`) and an ordered column-ID
array. Foreign keys have ordered source/target column-ID arrays of equal length,
a target relation ID/name and explicit update/delete actions. An internal target
has `externalTarget=false` and must resolve within the snapshot. A deliberately
excluded target has `externalTarget=true` and retains its qualified name, ordered
column names/type references and identity; it is not a dangling internal reference.
Do not silently remove its FK or automatically reinclude an excluded relation.
Preserve declared order;
sorting the columns of a composite key changes semantics. SQLite relation options
include `withoutRowId` and `strict`; hidden/generated-column and INTEGER PRIMARY
KEY distinctions remain separate. Enums preserve declaration order. Domains and
arrays refer to their declared base/element type, retaining domain identity.

### Validation and canonicalization

1. Parse with `JsonDocument`/`Utf8JsonReader`, a depth limit of 64 and duplicate
   property detection. Reject comments, trailing commas, nonfinite numbers,
   unpaired Unicode surrogates and unknown fields for version 1. Report JSON
   pointer plus error code; do not echo arbitrary source values into diagnostics.
2. Validate required field kinds, supported version/profile IDs and nonempty names.
   Reject duplicate stable IDs and duplicate column ordinals in the same relation.
3. Resolve all type/key/foreign-key/override references. Array/domain cycles are
   invalid unless an explicitly supported recursive type contract is added later.
   Unknown SQL types remain unresolved requirements and block code generation;
   they do not become `object` or strings automatically.
4. Apply overrides to a copy, then validate again. A type override must name a
   statically registered SQL/CLR conversion/codec; a spelling override cannot
   change database identity or silently merge two members.
5. Sort types and relations by stable ID with `StringComparer.Ordinal`; sort keys,
   foreign keys and overrides by their stable IDs. Sort columns by ordinal.
   Preserve ordered enum labels, key columns and array dimensions.
6. Serialize through an explicit `Utf8JsonWriter` property order, two-space
   indentation, LF line endings, no BOM and one trailing LF. Omit no required
   properties; use explicit null for absent nullable fields. No acquisition
   timestamp, connection string, credentials, host name or machine path enters
   canonical content. Capture server/profile versions because they affect meaning.
7. A content fingerprint is SHA-256 of the canonical UTF-8 bytes. It is external
   build metadata, never a self-referential property in the snapshot.

### C# identifier algorithm

Explicit validated `clrName` overrides win. Otherwise retain legal C# identifier
characters and original spelling, escape each illegal Unicode scalar as
`_uXXXX_` (six uppercase hex digits for non-BMP values), and prefix `_` when the
first scalar cannot start an identifier. Prefix C# keywords with `@`; do not
change SQL text. Resolve a collision by appending `__` plus the first 12 lowercase
hex characters of SHA-256 of the stable schema ID. If that still collides, use
the full hash; an identical full identity is an input duplicate error. Generated
metadata always retains the original qualified SQL name, so naming is reversible
through the descriptor. Never use current-culture casing or a traversal counter.

A `.korda-schema.json` change regenerates C# only. Discovery, database migrations,
Java/Rust/native engine compilation and runtime type discovery are not part of
normal application compilation.

## 8. Explicit schema tool workflow

The fixed local tool package is `Korda.Orm.Schema`, command `korda-orm-schema`,
framework-dependent net11.0. It is a build/development tool, not part of the
application execution closure. Its adapters use the same pinned mature drivers;
its database access occurs only for an explicitly invoked `acquire` command.
The tool does not load arbitrary plugins or resolve provider types by reflection.
A closed provider switch selects the three built-in adapters and four profiles.

Commands are fixed:

```sh
korda-orm-schema acquire --provider postgresql --profile postgres-18 \
  --connection-env KORDA_SCHEMA_CONNECTION --output schema/app.korda-schema.json
korda-orm-schema validate --input schema/app.korda-schema.json
korda-orm-schema generate --input schema/app.korda-schema.json --output obj/korda-schema
```

`acquire` accepts explicit repeatable `--include`/`--exclude` qualified-name
filters, an optional `--overrides` file and `--unresolved error|record` (default
`error`). Error mode preserves the previous output when a type is unresolved;
explicit record mode writes a structurally valid unresolved snapshot with
ORMSCHEMA007 warnings. Generation still fails until its mappings are resolved. Each filter is one JSON
triple such as `'[null,"public","invoice*"]'`, with explicit null/empty catalog and
schema semantics. `*` matches within a non-null segment, `\*` and `\\` are the
only escapes, matching is ordinal, and exclusion wins. Dots within a segment are
literal. Filters are not SQL fragments or regular expressions. Acquisition uses
namespace `Korda.Generated`, rows=true and mappings=true unless explicit
`--namespace`, `--rows` or `--mappings` options override them; mappings without rows
is an error. The connection string is read from the named
process environment variable; never accept it in the CLI argument list, record
it in the snapshot or echo it in logs. Validate arguments/overrides before opening
a connection. Resolve credentials only after the selected command is known to
need a connection.

The provider implements the shared `ISchemaCatalogReader.ReadAsync(connection,
options, cancellationToken)` contract. The caller owns opening and disposal; the
adapter borrows the connection, reads catalog metadata only and returns a neutral
snapshot. The shared Schema module validates and canonicalizes it. Acquisition
must not execute migration DDL, infer a schema from sample rows, or make an
implicit write transaction. Provider tasks own exact catalog queries and the
profile-specific consistency checks. PostgreSQL reads one tagged-union statement;
SQLite compares schema_version plus two normalized complete reads; MySQL/MariaDB
compare two normalized complete reads. A mismatch is ORMSCHEMA008, with no output
replacement or implicit retry. Each adapter calls the shared transform once before returning the requested
snapshot; the CLI does not repeat it. Adapters preserve references needed for
selected types and external keys.

`validate` performs only offline parsing/validation. `generate` is an optional
physical-source alternative using the same deterministic generation models; the
normal incremental generator consumes the JSON directly. It must not bypass
invalid schema or silently invoke `acquire`. Output goes under a caller-selected
local directory such as `obj`, not into the user's source tree by default.

Write an acquired snapshot to a temporary sibling file, flush/close it, then
atomically replace the requested output after all validation succeeds. Cancellation
or failure preserves the previous output and removes the temporary sibling.
Return exit 0 on success, 2 for arguments/schema/mapping diagnostics, 3 for provider
connection/permission/catalog failures, and 130 for cancellation. Cancellation
messages do not assert that a provider stopped synchronously. A diagnostic prints
its stable code, object/JSON pointer and safe reason; provider exceptions are
redacted according to the adapter contract.

## Primary compiler references

The [runtime module-initialization guarantees](https://github.com/dotnet/runtime/blob/main/docs/design/specs/Ecma-335-Augments.md)
and [Native AOT RuntimeHelpers implementation](https://source.dot.net/System.Private.CoreLib/System/Runtime/CompilerServices/RuntimeHelpers.NativeAot.cs.html)
explain the startup boundary and why RunModuleConstructor is not a rooting repair.
The exact positive/negative evidence is EXP-GEN-ROOTING, not a general inference
that every library initializer is retained merely because an assembly is referenced.

The [Roslyn source-generator design](https://github.com/dotnet/roslyn/blob/main/docs/features/source-generators.md)
and [incremental cookbook](https://github.com/dotnet/roslyn/blob/main/docs/features/incremental-generators.cookbook.md)
explain ordinary generator visibility, value-equatable pipelines and explicit
attribute discovery. The current
[`IncrementalContexts` implementation](https://source.dot.net/Microsoft.CodeAnalysis/SourceGeneration/IncrementalContexts.cs.html)
and [API proposal #83089](https://github.com/dotnet/roslyn/issues/83089) identify
pre-compilation output as experimental and constrain its inputs. Their moving web
pages are explanatory references; the observed local Roslyn version/API attributes
and experiment results above are the fixed evidence for this study.
