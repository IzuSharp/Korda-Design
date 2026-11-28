# Shared contracts for parallel implementation

Version: **0.2.0 proposed; review pending**. This revision supersedes the first
own-executor proposal. No historical acceptance authorizes product work. The
implementation graph pins one immutable Design revision; changes to these
interfaces require a versioned contract/affected-packet update before integration.

[Implementation specification](implementation-spec.md) owns exact common C#
declarations, internal seams, algorithms and diagnostic vocabulary. The disposable
specification check compiled the initial public surface in separate Contracts,
Types, Language and Rendering assemblies and rejected incompatible generic operands.
That is signature evidence, not a shipped implementation. The Plan packets fix
remaining module-specific declarations and cases; Foundation compiles their complete
combined surface and must not invent different signatures or representation.

| Contract | Owner | Fixed responsibility |
| --- | --- | --- |
| ORM-C01 | Contracts/types/language | SQL/CLR identity, immutable nodes/values, scopes, typed composition |
| ORM-C02 | Rendering/dialects | Explicit capability checks and faithful SQL emission/lowering |
| ORM-C03 | Command boundary | Atomic value-free templates, exact occurrences and logical/physical results |
| ORM-C04 | Execution/providers | Mature runtime factories, strict mapping, admission, lifetime and errors |
| ORM-C05 | Schema/generation | Offline schema model, normal SG, closed static mapping and diagnostics |
| ORM-C06 | Verification/packages | Source traceability, native/database/package evidence and independent CI |

These are semantic dependencies, not a demand to finish all downstream code before
parallel work begins. Contracts holds the immutable shared data; task owners hold
operations in disjoint paths. No driver/Roslyn/Dapper type enters the pure contracts.

## ORM-C01 — language, type and ownership

SqlType<T> has stable SQL ID, typeof(T), SQL nullability and length/precision/scale/
element/domain facets. Same CLR carrier does not erase SQL domain or JSON/JSONB
identity. SqlTypes.Define<T> validates the descriptor; Nullable<T> and
NullableReference<T> apply the explicit representation rules. Closed provider
codecs must support the resulting ID; a new descriptor alone does not grant an
encoding or AOT mapping. No automatic arbitrary object fallback exists.

Field<T>, Param<T>, ListParam<T>, Condition, TableLike, Projection<T>, Query<T>,
Mutation and ReturningMutation<T> have the fixed signatures in implementation-spec
and their owning packets. Field/parameter operations reject incompatible generic
carriers at compilation where expressible; SQL domains, scopes, grouping and
runtime-selected degree/type errors fail the pure validation pass. SQL execution
constraints/cardinality/permissions may still fail at the database.

Immutable sealed record nodes, ImmutableArray collections and explicit NodeKind
visitors are fixed. Public fluent operations are Language extension methods;
Contracts owns handle/node payloads and internal constructors. No partial class is
split across assemblies. Extending a query cannot mutate another query. Alias
text is independent of RelationId; dialect-specific identifier equivalence is an
additional validation after common Ordinal collision checks.

TableKeyDefinition declares ordered key columns, primary/unique status,
AllNotNull and IsPartial. Table.Define(name) has no key assertions; its explicit
key overload freezes the metadata and As preserves it with a fresh RelationId.
Generated schemas provide declared keys. Partial/expression keys do not prove
presence or scalar cardinality; manually supplied metadata is a caller assertion,
not a runtime schema verification promise.

Ordinary values create captured typed slots in an immutable sidecar, not literals
inside the AST. Nodes/templates retain no request values. ParameterValues holds
BoundValue<T> cells plus frozen SlotId lookup; Accept calls a generic visitor,
never reflection or MakeGenericType. Builder Add rejects duplicate identities;
With deliberately replaces one slot in a new snapshot. Unused known superset
values are allowed and not bound. Arrays/bytes/lists are snapshotted once; custom
mutable payloads require an explicit static snapshot policy.

That policy is Contracts.SqlType<T>.Snapshot, supplied by the exact SqlTypes.Define
overloads; Contracts never consults a Types registry. Only the declared BCL
whitelist receives automatic identity, and byte[] receives copying. Unknown
structs/arrays/references remain result-only until an explicit callback is supplied.
Capture calls it once, Nullable lifts it, and Merge/Bind/Render never copy frozen
cells again. Generated code can copy a static type's policy through the public
snapshotSource overload without reading internal state.

Condition represents SQL TRUE/FALSE/UNKNOWN. Equality to a nullable NULL stays
`= parameter`; IsNull and null-safe distinctness are separate. Empty IN is FALSE,
empty NOT IN is TRUE; NULL entries in nonempty lists remain semantically present.
Row null predicates, grouping and scalar cardinality follow the source-linked
cases. SQLite cannot be advertised as throwing for an arbitrary multirow scalar;
that shape is rejected unless at most one row is proved.

COUNT returns nonnull Int64. Integer SUM returns nullable decimal through a checked
native result conversion; exact-decimal SUM/AVG and integer exact AVG are rejected
on SQLite. Float/double aggregates return nullable double. MIN/MAX preserve SQL type
with nullable empty-set result. A caller wanting approximate integer AVG explicitly
casts to Double. These rules and concrete numeric overloads are fixed by Expressions.

Same-width integer arithmetic widens operands/results to Int64; float/double
arithmetic uses Double; decimal remains decimal with unknown result facets unless
explicitly declared. Nullable operands preserve nullable results. Integer division
and modulo return nullable Int64 and retain each server's zero-division behavior.
Mixed widths require an explicit Cast. Explicit int16/int32 Cast results carry
cast.int16.checked/cast.int32.checked through aliases, derived/CTE outputs and
nested leaves; strict ordinary readers are not relaxed to accommodate those casts.

## ORM-C02 — pure rendering and capability contract

Input is immutable query/mutation, explicit family/version/settings profile and
structural list cardinalities. Output is one complete template or a diagnostic.
No connection, driver, scheduling or runtime code generation is required.

Pass order is descriptor/scope validation, semantic degree/context validation,
pure nested lowering, checked dialect lowering, revalidation, one traversal for
SQL/occurrences/result shape, then limit/fingerprint/freeze. Unknown nodes never
fall back to ToString. An emitter cannot publish a partially valid SQL/layout pair.
Each profile classifies a requested operation as native, equivalent under recorded
preconditions, unsupported or planned/unverified. Only the first two execute.

IDialectRules and ISqlWriter live in Contracts. Dialects depend inward on pure
contracts/types/language, and Profile.Create attaches the static implementation
through an internal Contracts interface. Rendering has no concrete dialect reference. Nested
lowering is pure and cannot depend back on RenderContext. Precedence, name quoting,
clause scopes, returning contexts and exact occurrence order are fixed in the
Rendering packet. One identifier segment containing a dot stays one segment.

No requested RETURNING, locking, ordering, materialization or conflict target is
silently removed. Volatile expressions cannot be duplicated by an equivalent
lowering. Native RETURNING is one command and operation/profile-specific; generated
keys/follow-up SELECT are outside this contract. MySQL/Maria assignment semantics
are checked rather than reordering written columns. Update/Delete without Where
require the explicit AllRows marker. LIMIT/OFFSET public values are nonnegative Int32.

Raw/function extension points require an explicit type, known parameter/result
layout and volatility/semantics declaration. They never parse user values into SQL
or weaken normal validation implicitly. Oversized SQL/list/parameter layouts fail
before sending; no truncation or automatic literal inlining is permitted.

## ORM-C03 — templates, physical occurrences and result shape

| Type | Exact content and ownership |
| --- | --- |
| RenderedTemplate<T> | Id, SQL, immutable profile, ordered ParameterOccurrence array, ResultShape; internal constructor, reusable, value-free |
| RenderedMutationTemplate | Same command data without row-result mapping; nonquery affected-row endpoint only |
| ParameterOccurrence | Logical SlotId, element index (-1 scalar), contiguous zero-based ordinal, physical name, exact SQL type descriptor |
| ResultShape.Columns | Actual physical output columns in order, with alias, SQL/CLR descriptor, nullability and conversion |
| ResultShape.Members | Logical DTO members with name, first physical ordinal, width, scalar/required-row/optional-row/collection kind, logical type and optional nested descriptor |
| BoundCommand<T>/BoundMutation | One template, frozen values and a private atomic invocation state; sealed classes, not publicly copyable records |

Every final textual occurrence becomes one parameter. PostgreSQL uses `$1` onward
and an empty Name; other profiles use `@p0` onward and Name `p0` onward. Repeated
logical slots keep the same value identity but have separate physical parameters.
Distinct slots with the same diagnostic label do not merge. Bind validates all
required slots/types/nullability/facets and exact list lengths. Typed NULL retains
its declared SQL type. The executor never appends placeholders or expands lists.

A logical scalar has physical width1. Nested required/optional rows can span
several columns; optional presence precedes payload. Collections occupy one JSON
column with a separately described element shape. Outer physical ordinals and
relative child ordinals are explicit, never recovered by splitting alias strings.
Logical child non-nullability is checked only when its presence discriminator is1.
[The nested packet](https://github.com/IzuSharp/Plan/blob/task/Korda-Orm-01-linux/docs/korda-orm/tasks/ORM-NESTED.md)
fixes the descriptor and bounded JSON decoder protocol.

Template identity is SHA-256 over a versioned canonical binary shape including
literal bytes, profile/settings, list arities, types/facets, lowerings and complete
result shape. Bound request values are excluded. Same hash does not substitute
slot identity. Initial reuse is explicit: no global unbounded cache or command
recycling. No pooled memory or mutable builder escapes into a template.

## ORM-C04 — mature execution, mapping and lifecycle

Dapper.AOT1.1.0 Runtime is the execution implementation. LayoutCommandFactory
consumes already known occurrences, visits typed cells and calls a closed provider
ParameterEncoder. It shares one binding helper between GetCommand/AddParameters.
If initialization fails inside LayoutCommandFactory.GetCommand before factory
return, it disposes its local command; a cleanup failure is attached to the primary exception and does not replace
its stack. The later upstream connection/transaction/timeout setters are outside that catch;
selected providers validate legal values/association first, with no concurrent
mutation of borrowed resources. No replacement reader loop/pool/scheduler/retry
machinery is added.

CompiledMapping<T> holds immutable logical RowMember metadata. Bind(ResultShape,
ProviderServices) validates logical compatibility and creates a projection-bound
RowFactory<T>. ProviderServices supplies ValidateParameter, ValidateResult,
BindReader<T>(SqlTypeDescriptor,string? conversionId), and
ValidateReaderColumn(DbDataReader,int,ResultColumn,RowMember). BindReader returns a
closed `Func<DbDataReader,int,T>`; no codec lookup occurs per row. Tokenize validates
actual physical count/order/aliases/accepted storage representations once before
materializing the first row. It does not infer provider representation from DTO T.

Execution owns the one immutable ProviderCodecCatalog/Builder with closed generic
write/read interfaces. Provider services take the catalog explicitly and ordinary
factories use their declared defaults. Pure Types/AdvancedTypes conversion helpers
do not introduce a second runtime registry. Missing write codec is BIND-005;
missing/wrong-closed read codec is MAP-002. Invalid or duplicate catalog entries
fail TYPE-001 at construction, without replacing an existing codec silently.

Bind combines member/column ConversionId: use the nonnull one, use equal IDs once,
and reject two different nonnull IDs with MAP-002. Alias/CTE/derived/nested wrappers
preserve this metadata. Collection physical reads use owned ReadOnlyMemory<byte>
with nested.payload.utf8, retaining the actual JSON/JSONB/TEXT SQL identity; hidden
optional-row presence uses an explicitly cast Int64 and a synthetic long reader.

The default mapping is strictly bound to the declared template. Declared projection
reordering is allowed and changes the immutable ordinal plan; unexpected reader
reordering fails. Generated constructors/initializers then consume typed delegates.
A required DBNull fails KORM-MAP-003; a known checked conversion failure is
KORM-TYPE-005. Both identify ordinal/alias/type and retain any underlying cause. Empty results skip upstream Tokenize and return empty;
no empty-schema mismatch guarantee, hidden schema query or runtime fork is implied.

Mapping<T>.Register uses a generic static slot and rejects a second registration.
Fixed BCL scalars have explicit registrations. Closed Row combinations use a unique
RowMappings<T...> static constructor plus EnsureRegistered; consumer SG discovers
or explicitly roots them. No Type dictionary, assembly scan or dynamic generic
construction fills a missing mapper. A deliberate handwritten CompiledMapping can
be passed to the manual terminal overload.

OrmSession.Borrow never disposes a caller connection/transaction. Own disposes its
connection once when idle. Session states are Idle, Active and Disposed; concurrent
use fails KORM-EXEC-002, active disposal fails KORM-EXEC-003, and neither queues work.
Pre-cancellation/argument/profile/shape validation occurs before lease/admission.
After acquiring the lease, consume BoundCommand atomically; a second execution
fails KORM-EXEC-006 and releases the attempted lease. Once admitted, failure still
consumes that invocation. Bind the reusable template again to create another one.

Streaming is lazy and single-use. GetAsyncEnumerator claims the wrapper; first
MoveNext validates/adopts the invocation and forwards the mature runtime iterator.
Overlapping MoveNext/active disposal is rejected. EOF/failure/early-break disposal
forwards cleanup exactly once, releases the lease and disposes any linked token
source. Rows are owned values and retain no reader. No background prefetch worker
or borrowed-row lifetime is part of the baseline.

Timeout null passes -1 to preserve driver default; explicit0 is unlimited; positive
values are seconds; negative public input fails. Cancellation after dispatch requests
the driver's actual behavior and does not prove no transaction effect. SQLite's
synchronous async facade and lack of in-flight cancellation are declared. Provider
errors propagate unchanged except specified contextual wrappers. Transactions and
savepoints remain explicit driver operations; commit failure is not automatically
retried. SQL values and credentials are excluded from diagnostics by default.

## ORM-C05 — offline schema and normal source generation

The version1 schema contract records stable schema IDs, qualified names, ordered
columns/keys/FKs, SQL facets/nullability, generated/default semantics, profile and
explicit unresolved representations. Schema IDs are not runtime RelationIds.
Filtered external FK targets remain explicit externalTarget references; they are
not silently deleted or pulled into the selection. The exact portable declarations,
canonical JSON, catalog queries and acquire/validate/generate CLI are fixed in the
Schema/SchemaTool/provider packets and generation-integration.

The generator targets netstandard2.0, uses Roslyn4.14 build-only dependencies and
has a validated private JSON dependency closure. It reads source symbols and
AdditionalFiles only. The default is a normal incremental generator producing
Dapper RowFactory subclasses and module-initializer registration. It does not need
generator-to-generator interception, experimental Roslyn PreCompilation output,
network access, live metadata discovery or a second production build stage.

DbRow, DbConstructor, DbColumn, DbIgnore, DbNested, DbCompileRow and CompiledRow
attributes have fixed owners/targets/diagnostics. Known public record constructors
and init members compile into direct calls. Unsupported/inaccessible/ambiguous
members fail ORMGEN diagnostics, not runtime reflection. Nested parent factories
construct known children explicitly; only the outer factory tokenizes a reader.
JSON collection readers use static typed cell readers and explicit depth/item/byte
budgets, preserving duplicates, ordering, SQL NULL and JSON null.

Generation emits typed table/column metadata and typed DTO projection helpers.
Handwritten metadata and static mapping remain valid. The schema tool is an
explicit framework-dependent local tool; normal builds are offline. Schema drift,
IDE compatibility and exact packaged analyzer hosting have their own acceptance
cases and are not proved by one successful source compilation.

## ORM-C06 — traceability, evidence and package acceptance

For every operation record upstream commit/path/symbol, semantic rule, adaptation
reason, local positive/negative cases, supported profile and evidence state. Reuse
available mature test algorithms; do not claim private jOOQ suites or unavailable
commercial transformations. Preserve license/NOTICE obligations for source
translation and actual package/native dependencies; see upstream-policy.

The fixed seven packages are listed in architecture. Each must be independently
restored from the exact candidate nupkg with an isolated cache and run through its
appropriate native/host consumer. One Execution DLL is shared by provider products.
No driver/Dapper/Roslyn dependency leaks into pure Korda.Orm. XML/API/default/
nullability/exception/ownership contracts and compilable examples evolve together.

Future product CI extends the existing module registry and Python selection,
including actual project dependencies and exact package inputs. Ordinary Markdown
selects no product checks; provider leaf changes select only themselves and real
consumers. Performance campaigns remain explicit. Document CI validates documents,
not prototypes, SQL correctness, AOT, release suitability or parity.

The reopened study has real native/database/generator/performance evidence in
mature-execution, generation-integration and java-execution-options. Full product
implementation, complete feature conformance, shipping packages, cross-platform
hosting and final public-path performance budgets remain future acceptance. A
positive research decision does not silently mark those gates passed.
