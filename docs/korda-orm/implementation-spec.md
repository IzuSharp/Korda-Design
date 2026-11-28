# Implementation specification

Version: **0.2.0 proposed**. This specification fixes the choices left open by the
first research delivery. It is an implementation input, not an installed product.
The implementation packets in Plan must follow these decisions; a discovered
contradiction is returned to the contract owner rather than silently redesigned.
The shared declarations below are compiled as a disposable specification check.
Throw-only bodies in that check stand for the algorithms specified here and in the
owning packet; they are not product implementations or acceptable shipping stubs.

## 1. Decisions that implementers must not reopen

| Subject | Fixed implementation |
| --- | --- |
| Language model | Immutable C# record nodes and immutable arrays; one explicit node-tag dispatch visitor; no generated Java-style grammar-step interface hierarchy |
| Public query | `Query<TRow>` plus `Projection<TRow>`; typed fields and parameters; typed row arities 1–8, with a separate declared `DynamicRecord` for runtime-selected fields |
| Runtime SQL | Any supported runtime combination of the defined nodes; values are parameters by default, including `Eq(value)` convenience calls |
| Invocation values | Typed `BoundValue<T>` cells behind an immutable `ParameterValues` collection; no reflection, runtime type synthesis or required `object[]` argument protocol |
| Template | `RenderedTemplate<TRow>` has SQL, profile, occurrence layout and result shape, but no request values or reader factories |
| Physical parameters | Allocate one physical parameter per final emitted occurrence; repeated logical slots keep the same value identity; PG uses `$1` onward, the other three profiles `@p0` onward |
| Execution | Pinned, unmodified Dapper.AOT runtime; derived command and row factories; no Korda reader loop, scheduler, connection pool or retry engine |
| Mapping discovery | `[DbRow]` plus generated public registrar with a unique static constructor; declaring and final-consumer generators call EnsureRegistered; one generic static slot, no runtime member inspection |
| Generator composition | One normal incremental generator writes explicit Dapper factory subclasses; no dependency on generator-to-generator interception, preview Roslyn APIs or an extra default build stage |
| Strict mapping | Validate declared projection compatibility before dispatch and actual columns before materializing the first row; empty results follow the mature runtime's no-Tokenize behavior |
| Command initialization | Small `GetCommand` override disposes if local property assignment/binding fails before factory return; later upstream setters retain their documented preconditions |
| Timeout | `null` retains driver default by passing -1 to Dapper; explicit 0 is unlimited; positive integers are seconds; negative public input is invalid |
| Reuse/cache | Explicitly reusable templates; no global shape cache, command cache/recycling, speculative preparation or pooled invocation values in this baseline |
| Packages | Independently usable pure `Korda.Orm`, shared `Korda.Orm.Execution`, three provider products, analyzer product and explicit schema tool; no duplicated Execution DLL in provider packages |

The original Dapper.AOT + controlled explicit `DynamicParameters` route remains a
verified compatibility route and benchmark control. The default factory consumes
the known layout directly. It inherits upstream factory construction/binding and
token/read algorithms, with explicit Korda layout and strictness policies. These
policies are small adapters, not a replacement execution engine. The measured
comparison and exact inherited code responsibilities are in
[mature-execution.md](mature-execution.md).

## 2. Project and file boundary

All paths below refer to future authorized work in the product repository. They
do not authorize this research task to create those files there. Each project uses
net11.0/C#15, nullable enabled, deterministic builds and public XML documentation;
the analyzer is the specific netstandard2.0 exception in the generation design.

| Internal project / directory | Required initial files | References |
| --- | --- | --- |
| `src/Orm/Contracts/Korda.Orm.Contracts.csproj` | `SqlTypeDescriptor.cs`, `Identity.cs`, immutable handles, `Nodes/{Query,Expressions,Dml,Relational,Advanced,Nested}.cs`, `ParameterValues.cs`, `ResultShape.cs`, `ParameterLayout.cs`, `Diagnostics.cs`, `Rendering/IDialectRules.cs` | BCL only |
| `src/Orm/Types/Korda.Orm.Types.csproj` | `SqlTypes.cs`, `SqlType.cs`, `ConversionCatalog.cs` | Contracts |
| `src/Orm/Language/Korda.Orm.Language.csproj` | `Query/`, `Expressions/`, `Dml/`, `Relational/` containing operators, `Sql.*.cs` facade fragments and validators | Contracts, Types |
| `src/Orm/Rendering/Korda.Orm.Rendering.csproj` | `SqlRenderer.cs`, `RenderContext.cs`, `ScopeFrame.cs`, `TemplateFingerprint.cs`, `Capability.cs` | Contracts, Types, Language |
| `src/Orm/Dialects/{PostgreSql,Sqlite,MySql,MariaDb}/` | one project each, `Profile.cs`, `CapabilityTable.cs`, `Lowering.cs`, `TypeNames.cs` | Contracts, Types, Language, AdvancedTypes, Nested; never Rendering or provider drivers |
| `src/Orm/Schema/Korda.Orm.SchemaModel.csproj` | `Model/`, `Format/`, `Generation/` files fixed in ORM-SCHEMA | Contracts, Types |
| `src/Orm/Execution/` | `OrmSession.cs`, `QueryExecutionExtensions.cs`, `Mapping.cs`, `LayoutCommandFactory.cs`, `InvocationLease.cs`, `CommandOptions.cs`, `Metadata/ISchemaCatalogReader.cs` | Contracts, Types, Language, Rendering, Schema, Dapper.AOT 1.1.0 |
| `src/Orm/Providers/{PostgreSql,Sqlite,MySql}/` | provider project, `SessionFactory.cs`, `ParameterCodec.cs`, `ReaderCodec.cs`, `ServerProfile.cs`, `MetadataReader.cs` | Execution, Schema and only that provider's driver |
| `src/Orm/Generation/` | `OrmGenerator.cs`, `Models/`, `Emit/`, `Diagnostics.cs` | build-only Roslyn and JSON dependencies |
| `src/Orm/AdvancedTypes/`, `src/Orm/Nested/` | neutral descriptors/operations/decoders from their packets | pure language/types; provider encodings belong to providers |
| `src/Orm/SchemaTool/` | `Program.cs`, `AcquireCommand.cs`, `ValidateCommand.cs`, `GenerateCommand.cs` | Schema plus explicitly selected metadata adapters |

Foundation owns all shared immutable node/handle declarations in Contracts. Query,
expressions, DML and relational task owners have disjoint subdirectories under
Language and implement their operations/validation against those declarations;
they do not each edit the project file or move data types into Language. Foundation
creates project files and the initial solution/module entries;
the CI owner maintains shared root and registration files afterward. The language
project includes files by SDK default glob. Public facade fragments are partial
files (`Sql.Query.cs`, `Sql.Expressions.cs`, `Sql.Dml.cs`, `Sql.Relational.cs`) owned
by their respective task, not one shared `Sql.cs` edited by everyone.

## 3. Exact common declaration surface

This is the shared surface used by independent implementers. Constructors and
members marked internal are exposed to the named implementation assemblies using
explicit friend-assembly declarations; they are not made public to simplify tests.
The exact implementation friends are Korda.Orm.Types, Korda.Orm.Language,
Korda.Orm.Rendering, Korda.Orm.Execution, Korda.Orm.Dialects.PostgreSql,
Korda.Orm.Dialects.Sqlite, Korda.Orm.Dialects.MySql, Korda.Orm.Dialects.MariaDb,
Korda.Orm.AdvancedTypes, Korda.Orm.Nested, Korda.Orm.Parser,
Korda.Orm.SchemaModel, Korda.Orm.PostgreSql, Korda.Orm.Sqlite and Korda.Orm.MySql.
Add only explicitly named test assemblies for the described internal fake tests;
never wildcard access. Generators emit public infrastructure calls and need no
friend access from consumer-generated code.
The compile check uses those exact accessibility choices; the public consumer
uses factories and cannot construct unchecked nodes or invocation objects.

```csharp
using System.Collections.Immutable;

namespace Korda.Orm;

public enum SqlNullability { NonNull, Nullable, Unknown }
public enum DatabaseFamily { PostgreSql, Sqlite, MySql, MariaDb }
public enum PlaceholderStyle { Numbered, Named }
public enum SortDirection { Ascending, Descending }
public enum NullOrder { Unspecified, First, Last }
public enum JoinKind { Inner, Left, Right, Full, Cross, LateralInner, LateralLeft }
public readonly record struct SqlTypeId(string Value);
public readonly record struct SlotId(long Value);
public readonly record struct RelationId(long Value);
public readonly record struct TemplateId(string Value);
public sealed record SqlName(ImmutableArray<string> Segments);
public sealed record TypeFacets(int? Length = null, int? Precision = null,
    int? Scale = null, SqlTypeId? ElementType = null, string? Domain = null);
public sealed record SqlTypeDescriptor(SqlTypeId Id, Type ClrType,
    SqlNullability Nullability, TypeFacets Facets);
public sealed class SqlType<T>
{
    public SqlTypeDescriptor Descriptor { get; }
    internal SqlType(SqlTypeDescriptor descriptor) => Descriptor = descriptor;
}
public sealed class Param<T>
{
    public SlotId Id { get; }
    public string Name { get; }
    public SqlType<T> Type { get; }
    internal Param(SlotId id, string name, SqlType<T> type) => (Id, Name, Type) = (id, name, type);
}
public sealed class ListParam<T>
{
    public SlotId Id { get; }
    public string Name { get; }
    public SqlType<T> ElementType { get; }
    internal ListParam(SlotId id, string name, SqlType<T> elementType) => (Id, Name, ElementType) = (id, name, elementType);
}
public static class SqlTypes
{
    public static SqlType<T> Define<T>(SqlTypeDescriptor descriptor) => throw new NotImplementedException();
    public static SqlType<T?> Nullable<T>(SqlType<T> type) where T : struct => throw new NotImplementedException();
    public static SqlType<T?> NullableReference<T>(SqlType<T> type) where T : class => throw new NotImplementedException();
    public static SqlType<int> Int32 { get; } = new(new(new("int32"), typeof(int), SqlNullability.NonNull, new()));
    public static SqlType<long> Int64 { get; } = new(new(new("int64"), typeof(long), SqlNullability.NonNull, new()));
    public static SqlType<long?> NullableInt64 { get; } = new(new(new("int64"), typeof(long?), SqlNullability.Nullable, new()));
    public static SqlType<string> Text { get; } = new(new(new("text"), typeof(string), SqlNullability.NonNull, new()));
    public static SqlType<bool> Boolean { get; } = new(new(new("boolean"), typeof(bool), SqlNullability.NonNull, new()));
}

public sealed class ParameterValues
{
    public static ParameterValues Empty { get; } = new();
    public ParameterValues With<T>(Param<T> slot, T value) => throw new NotImplementedException();
    public ParameterValues WithList<T>(ListParam<T> slot, IEnumerable<T> values) => throw new NotImplementedException();
    public static ParameterValues Build(Action<ParameterValuesBuilder> add) => throw new NotImplementedException();
}
public sealed class ParameterValuesBuilder
{
    public void Add<T>(Param<T> slot, T value) => throw new NotImplementedException();
    public void AddList<T>(ListParam<T> slot, IEnumerable<T> values) => throw new NotImplementedException();
}
public interface IField { SqlTypeDescriptor TypeDescriptor { get; } }
public sealed class Field<T> : IField
{
    public SqlType<T> Type { get; }
    public SqlTypeDescriptor TypeDescriptor => Type.Descriptor;
    internal Field(SqlType<T> type) => Type = type;

}
public sealed class Condition { internal Condition() { } }
public static class FieldOperations
{
    public static Field<T> As<T>(this Field<T> field, string alias) => throw new NotImplementedException();
    public static Condition Eq<T>(this Field<T> field, T value) => throw new NotImplementedException();
    public static Condition Eq<T>(this Field<T> field, Param<T> value) => throw new NotImplementedException();
    public static Condition Eq<T>(this Field<T> field, Field<T> value) => throw new NotImplementedException();
    public static Condition Ge<T>(this Field<T> field, T value) => throw new NotImplementedException();
    public static Condition Ge<T>(this Field<T> field, Param<T> value) => throw new NotImplementedException();
    public static Condition IsNull<T>(this Field<T> field) => throw new NotImplementedException();
    public static Condition IsNotNull<T>(this Field<T> field) => throw new NotImplementedException();
    public static Condition In<T>(this Field<T> field, ListParam<T> values) => throw new NotImplementedException();
    public static Condition In<T>(this Field<T> field, IEnumerable<T> values) => throw new NotImplementedException();
    public static SortField Asc<T>(this Field<T> field, NullOrder nulls = NullOrder.Unspecified) => throw new NotImplementedException();
    public static SortField Desc<T>(this Field<T> field, NullOrder nulls = NullOrder.Unspecified) => throw new NotImplementedException();
}
public static class ConditionOperations
{
    public static Condition And(this Condition left, Condition right) => throw new NotImplementedException();
    public static Condition Or(this Condition left, Condition right) => throw new NotImplementedException();
    public static Condition Not(this Condition value) => throw new NotImplementedException();
}
public sealed record SortField(IField Field, SortDirection Direction, NullOrder Nulls);
public abstract class TableLike { public RelationId Id { get; protected init; } }
public sealed class Table : TableLike
{
    public static Table Define(SqlName name) => throw new NotImplementedException();
    public Field<T> Column<T>(string name, SqlType<T> type) => throw new NotImplementedException();
    public Table As(string alias) => throw new NotImplementedException();
}
public sealed record ResultColumn(int Ordinal, string Alias, SqlTypeDescriptor Type,
    string? ConversionId = null);
public enum ResultMemberKind { Scalar, RequiredRow, OptionalRow, Collection }
public enum NestedPresencePolicy { Required, Key, AllNull }
public sealed record NestedBudget(int MaxBytes, int MaxItems, int MaxDepth);
public sealed record ResultMember(string Name, int FirstOrdinal, int Width,
    ResultMemberKind Kind, SqlTypeDescriptor LogicalType,
    NestedShapeDescriptor? Nested = null);
public sealed record NestedJsonMember(int CellIndex, string Name,
    ResultMemberKind Kind, SqlTypeDescriptor LogicalType,
    NestedShapeDescriptor? Nested = null);
public sealed record NestedShapeDescriptor(string Id,
    ImmutableArray<ResultColumn> RowColumns,
    ImmutableArray<ResultMember> RowMembers,
    ImmutableArray<NestedJsonMember> JsonMembers,
    NestedPresencePolicy Presence, NestedBudget Budget, string MappingId);
public sealed record ResultShape(ImmutableArray<ResultColumn> Columns,
    ImmutableArray<ResultMember> Members)
{
    public static ResultShape Flat(ImmutableArray<ResultColumn> columns) => throw new NotImplementedException();
}
public abstract class DynamicCell
{
    public SqlTypeDescriptor Type { get; }
    internal DynamicCell(SqlTypeDescriptor type) => Type = type;
}
public sealed class DynamicCell<T> : DynamicCell
{
    public T Value { get; }
    internal DynamicCell(SqlType<T> type, T value) : base(type.Descriptor) => Value = value;
}
public static class DynamicCells
{
    public static DynamicCell Create<T>(SqlType<T> type, T value) => throw new NotImplementedException();
}
public sealed class DynamicRecord
{
    public ResultShape Shape { get; }
    public ImmutableArray<DynamicCell> Cells { get; }
    internal DynamicRecord(ResultShape shape, ImmutableArray<DynamicCell> cells) => (Shape, Cells) = (shape, cells);
    public T Get<T>(int ordinal, SqlType<T> type) => throw new NotImplementedException();
    public T Get<T>(string alias, SqlType<T> type) => throw new NotImplementedException();
}
public sealed class Projection<TRow>
{
    public ResultShape Shape { get; }
    internal ImmutableArray<IField> Fields { get; }
    internal Projection(ResultShape shape, ImmutableArray<IField> fields) => (Shape, Fields) = (shape, fields);
}
public readonly record struct Row<T1, T2>(T1 Value1, T2 Value2);
public sealed class Query<TRow>
{
    public Projection<TRow> Projection { get; }
    internal Query(Projection<TRow> projection) => Projection = projection;

}
public static class QueryOperations
{
    public static Query<TRow> From<TRow>(this Query<TRow> query, TableLike table) => throw new NotImplementedException();
    public static Query<TRow> Where<TRow>(this Query<TRow> query, Condition condition) => throw new NotImplementedException();
    public static Query<TRow> Join<TRow>(this Query<TRow> query, TableLike table, Condition on, JoinKind kind = JoinKind.Inner) => throw new NotImplementedException();
    public static Query<TRow> GroupBy<TRow>(this Query<TRow> query, params IField[] fields) => throw new NotImplementedException();
    public static Query<TRow> Having<TRow>(this Query<TRow> query, Condition condition) => throw new NotImplementedException();
    public static Query<TRow> OrderBy<TRow>(this Query<TRow> query, params SortField[] fields) => throw new NotImplementedException();
    public static Query<TRow> Distinct<TRow>(this Query<TRow> query) => throw new NotImplementedException();
    public static Query<TRow> Limit<TRow>(this Query<TRow> query, int count) => throw new NotImplementedException();
    public static Query<TRow> LimitLiteral<TRow>(this Query<TRow> query, int count) => throw new NotImplementedException();
    public static Query<TRow> Offset<TRow>(this Query<TRow> query, int count) => throw new NotImplementedException();
    public static Query<TRow> Union<TRow>(this Query<TRow> query, Query<TRow> other) => throw new NotImplementedException();
    public static Query<TRow> UnionAll<TRow>(this Query<TRow> query, Query<TRow> other) => throw new NotImplementedException();
    public static Query<TRow> Intersect<TRow>(this Query<TRow> query, Query<TRow> other) => throw new NotImplementedException();
    public static Query<TRow> Except<TRow>(this Query<TRow> query, Query<TRow> other) => throw new NotImplementedException();
}
public sealed record SqlProfile(DatabaseFamily Family, Version MinimumVersion,
    Version MaximumExclusive, PlaceholderStyle Placeholders,
    ImmutableDictionary<string, string> Settings)
{
    internal IDialectRules? Rules { get; init; }
}
// Full pure node/writer interfaces are fixed in section 6 and Contracts/Nodes.
// This surface excerpt declares their minimal reference names for compilation.
internal interface IDialectRules { }
public sealed class RenderShape
{
    public static RenderShape Empty { get; } = new();
    public RenderShape WithList<T>(ListParam<T> slot, int count) => throw new NotImplementedException();
}
public sealed record ParameterOccurrence(SlotId Slot, int ElementIndex, int Ordinal,
    string Name, SqlTypeDescriptor Type);
public sealed class RenderedTemplate<TRow>
{
    public TemplateId Id { get; }
    public string Sql { get; }
    public SqlProfile Profile { get; }
    public ImmutableArray<ParameterOccurrence> Parameters { get; }
    public ResultShape Result { get; }
    internal RenderedTemplate(TemplateId id, string sql, SqlProfile profile,
        ImmutableArray<ParameterOccurrence> parameters, ResultShape result)
        => (Id, Sql, Profile, Parameters, Result) = (id, sql, profile, parameters, result);
}
public static class TemplateBindingExtensions
{
    public static BoundCommand<TRow> Bind<TRow>(this RenderedTemplate<TRow> template, ParameterValues values) => throw new NotImplementedException();
}
public sealed class BoundCommand<TRow>
{
    public RenderedTemplate<TRow> Template { get; }
    public ParameterValues Values { get; }
    internal BoundCommand(RenderedTemplate<TRow> template, ParameterValues values) => (Template, Values) = (template, values);
}
public static partial class Sql
{
    public static Param<T> Param<T>(string name, SqlType<T> type) => throw new NotImplementedException();
    public static ListParam<T> ListParam<T>(string name, SqlType<T> elementType) => throw new NotImplementedException();
    public static Field<T> Literal<T>(T value, SqlType<T> type) => throw new NotImplementedException();
    public static Projection<T> Project<T>(params IField[] fields) => throw new NotImplementedException();
    public static Query<T> Select<T>(Projection<T> projection) => throw new NotImplementedException();
    public static Query<T> Select<T>(Field<T> field) => throw new NotImplementedException();
    public static Query<Row<T1, T2>> Select<T1, T2>(Field<T1> first, Field<T2> second) => throw new NotImplementedException();
    public static Query<DynamicRecord> SelectDynamic(params IField[] fields) => throw new NotImplementedException();
    public static Condition True() => throw new NotImplementedException();
    public static Condition False() => throw new NotImplementedException();
    public static Condition Unknown() => throw new NotImplementedException();
}
public static class SqlRenderer
{
    public static RenderedTemplate<T> Render<T>(Query<T> query, SqlProfile profile,
        RenderShape? shape = null) => throw new NotImplementedException();
    public static BoundCommand<T> RenderAndBind<T>(Query<T> query, SqlProfile profile,
        ParameterValues? explicitValues = null) => throw new NotImplementedException();
}
```

Constructors of `SqlType<T>`, `Field<T>`, `Query<T>` and templates are internal in the
shipping API. Public callers use SqlTypes, table/field factories, Sql.Select and
SqlRenderer. Foundation copies that accessibility and adds only the specified
friend assemblies; the disposable declaration consumer checks the generic surface
and cannot use the internal constructors. `Param<T>` and `ListParam<T>` constructors are internal and their
identity properties read-only; callers cannot fabricate a reused SlotId. Identity
allocation uses Interlocked.Increment per process; IDs are not persisted in schema,
SQL aliases or cross-process cache keys.

Fluent operations are extension methods in the Korda.Orm namespace, while the
immutable data handles live in Contracts. Language owns FieldOperations,
ConditionOperations, QueryOperations and Sql partial facade files; Rendering owns
SqlRenderer and TemplateBindingExtensions. This exact split avoids Contracts →
Language/Types cycles and does not attempt partial classes across assemblies. The
application syntax remains `field.Eq(value)` and `query.Where(condition)`.

The generic overload patterns are fixed, not left for invention: `Ne`, `Lt`, `Le`,
`Gt`, `Ge`, `IsDistinctFrom`, `IsNotDistinctFrom` each have `(T)`, `(Param<T>)`,
`(Field<T>)` forms. Numeric arithmetic is in `NumericFields` with concrete numeric
overloads; text matching/concatenation is in `TextFields`. No unconstrained generic
operator silently converts text to numeric SQL. Row arities 1–8 use the shown
`Row<T1,...,TN>` / `Select` pattern and generated tuple-member factories. The
expressions packet enumerates the exact initial operation set and type rules.

`SqlTypes.Define<T>` requires Descriptor.ClrType to equal typeof(T), a nonempty
stable SQL ID and valid facets. Nullable value representations require SQL Nullable;
a NonNull value type cannot represent SQL Nullable. NullableReference changes SQL
nullability while the runtime CLR Type remains typeof(T). These factories do not
invent provider encodings: a custom SQL ID still needs the statically registered
codec/snapshot contract. `Nullable` preserves ID/facets and changes CLR type to T?.

Scalar Select returns Query<T>. Execution supplies fixed BCL scalar mappings; one
result column is required and its declared alias is used unchanged. Closed Row
arities 1–8 use consumer-generator registrations: the generated module initializer
calls RowMappings<T1,...,TN>.EnsureRegistered(), whose unique closed generic static
constructor registers one RowCompiledMapping instance. Multiple assemblies can
request the same registration safely. An assembly-level DbCompileRow attribute
roots a known closed row hidden behind a generic helper. There is no attempt to
register every possible open generic combination or construct one by reflection.

ResultShape.Columns is physical and Members is logical. Flat validates contiguous
columns/unique aliases and creates one Scalar member of width1 per column. Nested
required/optional rows have explicit ranges; optional presence is first. Nested
RowColumns/RowMembers are relative to that group's start; outer ranges are absolute.
Collections have physical width1 and separate JSON member indices/arity. Bind checks
logical members against DTO metadata; Tokenize checks all physical columns once.
Only present children invoke their logical non-null read delegates.

SelectDynamic freezes an explicitly runtime-selected scalar field list into
Query<DynamicRecord>. Its shape is still typed and known at render/bind time; it
creates no CLR type. DynamicRecord owns one DynamicCell<T> per selected column.
Get<T> requires exact SQL descriptor/carrier agreement and a valid ordinal or unique
Ordinal alias; mismatch fails KORM-MAP-002. The provider prebinds closed dynamic
cell reader delegates for its supported scalar IDs; unsupported or nested dynamic
cells fail before dispatch. A generated DTO is not required for this explicit
allocation-bearing path. No ExpandoObject, runtime class emission or reflected
getter is involved. Result arrays/bytes are owned values, never borrowed reader
buffers.

`Sql.Project<T>` is the explicitly runtime-validated projection entry: it preserves
each field's typed descriptor and validates it against generated Mapping<T> before
execution. The generator also emits `<DtoName>Projection.Create` with one typed
Field parameter per member/constructor argument, giving a compile-time checked
entry without requiring the DTO to be partial or the caller to write a mapper.

### Mutation and declared-SQL surfaces

The exact mutation builders/extensions are fixed in Plan ORM-DML and are part of
this contract: Mutation is the abstract nonreturning base; InsertBuilder,
UpdateBuilder and DeleteBuilder derive from it. ReturningMutation<T> is separate
and carries Projection<T>. SqlRenderer.Render(Mutation,profile,shape) returns
RenderedMutationTemplate; RenderAndBind returns BoundMutation. Corresponding
ReturningMutation<T> overloads return the existing typed template/command.
RenderedMutationTemplate exposes Id/Sql/Profile/Parameters and Bind(values);
BoundMutation holds it, values and the same private single-consumption state.
Mutation/BoundMutation Execute/ExecuteAsync return int/Task<int> through Dapper's
nonquery endpoint. ReturningMutation<T> uses ToList/ToListAsync/StreamAsync through
the same typed factory path as Query<T>, never Execute that discards returned rows.

The independent explicit SQL entry is fixed in Rendering:
`SqlTemplates.Declare<T>(string sql, SqlProfile profile,
ImmutableArray<ParameterOccurrence> parameters, ResultShape result)` returns
RenderedTemplate<T>; `DeclareMutation(string sql, SqlProfile profile,
ImmutableArray<ParameterOccurrence> parameters)` returns RenderedMutationTemplate.
Validate nonempty SQL, profile, contiguous ordinals/names, slot/type consistency,
result ranges and declared limits. Do not parse SQL or claim the factory proves
placeholder correspondence, statement semantics or safe interpolation: the caller
explicitly owns those declarations. The executor still validates values/mapping/
provider/lifetime. Fingerprint domain declared-sql-v1 includes exact SQL plus its
profile/layout/result. This permits SQL + typed parameters + handwritten static
mapping without constructing a Fluent query or requiring a generator.

## 4. Values, snapshots and structural lists

### Internal handle construction boundary

Contracts owns the immutable payloads as well as the public handles, avoiding a
Contracts-to-Language dependency. In addition to the compact declarations above,
the implementation adds these internal constructors/properties, with the same
friend-assembly list: Field<T>(SqlType<T>, SqlNode, ParameterValues),
Condition(SqlNode, ParameterValues), Query<T>(Projection<T>, QueryNode,
ParameterValues), and Table(RelationId, SqlName, string? alias). Each has readonly
Node and Captured properties; Table exposes an internal TableNode. QueryNode is the
abstract base of SelectNode and SetNode; DmlNode is the base of the three mutation
nodes. Public methods never accept an arbitrary SqlNode. Table.Define allocates a
RelationId; As allocates a new one and Column constructs its ColumnNode against
that table instance. Projection stores frozen fields and the union of their values.
ParameterValues.MergeCaptured(left,right) is internal, rejects distinct cells for
one SlotId, and is the sole merge helper used by every language task. Explicit
invocation values cannot override a captured slot accidentally; conflicting cells
fail KORM-BIND-002. With on the final snapshot is the deliberate replacement API.

Every field/condition/query wrapper contains an immutable node reference and an
immutable captured-value sidecar. The node graph contains only logical slot IDs,
types and explicit SQL literals. `field.Eq(value)` allocates a fresh typed slot and
adds `BoundValue<T>(slot, value)` to that sidecar. Combining conditions unions their
sidecars by SlotId; the same captured cell can be shared, while incompatible cells
for the same identity fail. ParameterValues.With returns a new snapshot replacing
that slot; builder Add rejects a duplicate slot instead of silently choosing one. A renderer visits nodes only and never stores the sidecar in
the returned template. `RenderAndBind` joins captured and explicit values once,
derives list cardinalities, renders, and binds that snapshot. Only slots referenced
by the final layout are bound; unused values in a known argument superset are
allowed and never become DbParameters. A typo still fails if a required slot is
missing. This supports optional predicates without rebuilding an argument schema.

The implementation of ParameterValues uses an immutable array of typed cells plus
a SlotId-to-index lookup created during freeze. The mutable builder is single-owner
and never escapes. `With` is a small-copy convenience; large or generated argument
sets use `Build` and freeze once. A cell retains its typed SqlType<T> and T value.
Its internal `ParameterValues.Accept(ParameterOccurrence occurrence, IParameterValueVisitor visitor)` dispatches to the concrete cell, which invokes
`visitor.Visit<T>(type, value, occurrence)`; this dispatch requires no reflection or
MakeGenericType. Only the provider adapter converts to its DbParameter representation.
Normal ADO.NET Value assignment may box value types; typed NpgsqlParameter<T> can
retain T. Neither path is described as universally allocation-free.

Primitive/value types and strings are copied by value/reference as appropriate.
`byte[]`, arrays and IEnumerable list inputs are snapshotted on capture/binding;
the input enumerable is consumed once. Mutable custom reference payloads require a
registered snapshot converter. Missing converter is `KORM-BIND-005`; there is no
undocumented borrow-across-await mode in this baseline. An explicitly immutable
custom type may register identity snapshotting with its codec contract.

For an expanded list, ElementIndex identifies the element in its one frozen typed
list. The final occurrence ordinal increases for each emitted reference, including
duplicates introduced by a validated lowering. An empty IN emits FALSE; empty
NOT IN emits TRUE; a nonempty NULL-bearing list retains SQL three-valued semantics.
Render requires its structural arity; Bind compares exact actual length and fails
`KORM-BIND-003` before creating a command when it differs. A native array expression
uses a scalar typed array slot and an explicit array operation, not implicit IN
rewriting by Dapper or a provider.

## 5. Fixed node layout and semantic passes

All internal nodes derive from `SqlNode(NodeKind Kind)`. They are immutable sealed
records. Arrays are ImmutableArray values constructed from copies, never wrapped
mutable caller arrays. Use these node records and owning task paths:

The table's owner means the semantic implementation owner; Foundation places the
record declarations in the corresponding Contracts/Nodes file before parallel
work starts. That owner later proposes a reviewed contract edit if a missing field
is discovered instead of adding a second incompatible node type in its assembly.

| Owner | Node records and ordered fields |
| --- | --- |
| Types/query | `ColumnNode(RelationId, SqlName, SqlTypeDescriptor)`, `ParameterNode(SlotId, SqlTypeDescriptor)`, `LiteralNode(TypedLiteral, SqlTypeDescriptor)`, `AliasNode(SqlNode, string)` |
| Expressions | `CompareNode(ComparisonKind, left, right)`, `JunctionNode(BooleanKind, children)`, `NotNode(child)`, `NullTestNode(child, negated)`, `InNode(item, listOrQuery, negated)`, `ArithmeticNode(kind,left,right)`, `FunctionNode(FunctionId,args,type)`, `CaseNode(branches,else,type)`, `CastNode(value,type)` |
| Query | `SelectNode(projection,from,joins,where,groupBy,having,windows,orderBy,limit,offset,distinct,ctes,lockClause)` |
| Relational | `TableNode`, `DerivedTableNode(query,relationId,alias)`, `JoinNode(kind,left,right,on)`, `CteDefinitionNode(id,name,columns,query,recursive)`, `CteReferenceNode(id,relationId,alias)`, `SetNode(kind,left,right)`, `WindowNode(partition,order,frame)` |
| DML | `InsertNode(target,columns,source,conflict,returning)`, `UpdateNode(target,assignments,from,where,returning)`, `DeleteNode(target,using,where,returning)` |
| Advanced/nested | Typed nodes enumerated in their packets; they use the same parameter, scope, type and lowering visitors |

The common visitor uses a NodeKind switch and exhaustively dispatches the record's
fields. Unknown tags are `KORM-MODEL-001`, never arbitrary ToString output. No
reflection visitor, mutable parent pointer or active driver object is stored.

Pass order is fixed: (1) validate descriptor/slot consistency and lexical scopes;
(2) validate degree, aggregate/grouping and expression context; (3) select checked
profile lowerings; (4) validate the lowered graph again; (5) render SQL, occurrences
and result columns in one traversal; (6) freeze and publish the atomic template.
Failure at any pass returns no executable template. A lowering creates new nodes
and reuses immutable children; it does not mutate the caller's graph.

ScopeFrame contains a relation-ID set, CTE-ID map and parent pointer. An ordinary
subquery resolves local IDs then allowed parent IDs. A non-lateral derived table
cannot capture siblings; a lateral relation can capture preceding FROM bindings.
Alias text is an emitted name, not relation identity. Same-scope duplicate aliases
fail; self joins require distinct aliases/RelationIds. CTE names are allocated and
checked before visiting definitions; only a declared recursive reference can bind
the current recursive definition. Projection aliases resolve in allowed ORDER BY
contexts but are not automatically visible in WHERE.

Grouping is deliberately deterministic: every nonaggregate selected/having/ordered
expression must be a grouping expression or composed solely from grouping keys and
constants. This baseline does not infer functional dependencies from database keys.
Nested aggregates, aggregates in WHERE and window functions in forbidden contexts
fail before rendering. Explicit COUNT has Int64 result and non-null zero; SUM/MIN/
MAX and other nullable aggregates keep their declared SQL empty-set semantics.
Integer SUM has nullable decimal carrier and conversion ID aggregate.int-sum.decimal;
decimal SUM uses aggregate.decimal-sum.decimal, exact numeric AVG uses
aggregate.numeric-avg.decimal, and float/double SUM/AVG use aggregate.floating.double.
Provider closed conversions are checked. SQLite allows integer SUM(Int64 storage
converted exactly to decimal), rejects exact decimal SUM/AVG/integer AVG, and permits
an explicitly Double-cast approximation. Do not silently cast/clamp a wide sum.

## 6. Rendering algorithm and identity

The assembly seam is fixed in Contracts: internal IDialectRules has
`SqlNode Lower(SqlNode root, SqlProfile profile)` and
`void Write(SqlNode node, ISqlWriter writer, int parentPrecedence)`.
ISqlWriter exposes SqlProfile Profile {get;}, void Write(string),
void Visit(SqlNode,int), void VisitCore(SqlNode,int), string Quote(SqlName), and
string NextParameter(SlotId,int,SqlTypeDescriptor). RenderContext implements it.
Each Profile.Create() attaches its immutable static rules instance directly to
SqlProfile.Rules. Rendering consumes that interface and has no project reference
to any concrete dialect or Nested implementation. There is no assembly scan,
module initializer or global registration race. A metadata-only profile created
through its public record constructor can be used with declared SQL; Fluent Render
requires Rules and otherwise fails KORM-DIALECT-001 with the profile factory name.
Rules validate their family and fixed rules_version=0.2.0 setting. A dialect handles a special node
or calls VisitCore, which dispatches the common writer without calling that same
dialect method again. Recursive children use Visit and therefore regain dialect
dispatch. All shared interfaces/nodes live in Contracts; dialect projects never
reference Rendering. Each dialect Lower first invokes NestedLowering(root,profile),
a pure transform in Nested, then its own lowering. Nested accepts no RenderContext
and owns no connection. Templates copy profile metadata with Rules cleared; rules
instances are not retained by the execution boundary. These directions prevent
Rendering/Dialect/Nested reference cycles and allow renderer acceptance with a
fixed contract fake before concrete dialect implementations are ready.

RenderContext owns one StringBuilder, occurrence list, result list, immutable
profile and scope stack. It is created per call and discarded afterward; no shared
builder or pooled memory escapes. `Write(string)`, `Visit(SqlNode)`, `Quote(SqlName)`
and `NextParameter(slot, elementIndex, type)` are the only primitive emitter seams.
Precedence is represented by numeric levels; parenthesize a child when its level is
lower than its parent or when equal precedence would change associativity. Set
operations always preserve explicit child grouping, including mixed UNION/EXCEPT.

`NextParameter` appends exactly one occurrence and returns its placeholder. PG's
ordinal in text is index+1 and the provider binds positionally; the occurrence Name
is empty for PG and `p{index}` elsewhere. Named dialects emit `@` plus that name.
Parameter identity never depends on the user's diagnostic name. String literals
are allowed only through explicit Literal nodes and the dialect literal encoder;
ordinary scalar values never enter SQL text. Limit(int) captures an Int32 parameter;
LimitLiteral(int) is an explicit nonnegative structural literal, included in the
fingerprint. Only a literal0/1 can supply SQLite scalar-subquery cardinality proof;
a runtime limit parameter does not acquire that proof.

The result descriptor is built while emitting the final projection/RETURNING list.
Each output has an explicit quoted alias; the provider cannot case-fold it behind
the mapper. No SELECT * is generated for a typed projection. Ordinals are zero-based
and contiguous. Qualifiers/identifiers are separate segments and quote characters
are escaped by doubling according to the selected dialect.

TemplateId is a SHA-256 fingerprint of a versioned canonical binary description:
node tags, ordered children, normalized first-use slot numbers and SQL types/facets,
explicit literal values, aliases, profile/settings, list arities and result shape.
Use UTF-8 length-prefixed strings and little-endian numeric encodings; never CLR
GetHashCode, dictionary iteration order or debug SQL. It is diagnostic/compatibility
identity, not permission to bind another query's SlotIds. The baseline has no global
cross-query template cache. A caller explicitly holds one template and supplies its
declared slots for each invocation.

## 7. Execution facade and state transitions

The public execution namespace is `Korda.Orm.Execution`. ProviderServices adds
ValidateConnection(DbConnection,DbTransaction?), ValidateValue<T>(SqlType<T>,T,
ParameterOccurrence), BindReader<T>(SqlTypeDescriptor,string?) returning
Func<DbDataReader,int,T>, ValidateReaderColumn(DbDataReader,int,ResultColumn,RowMember),
and BindDynamicReader(SqlTypeDescriptor,string?) returning
Func<DbDataReader,int,DynamicCell>, alongside the packet's Profile/Capabilities/
Commands/ValidateParameter/ValidateResult declarations. Connection validation runs
at session construction and preflight; typed value validation runs before admission.
Static conversions are pure, deterministic and side-effect-free, so preflight and
parameter creation can share their validation without a hidden mutable cache.
Profile equality compares family/version interval/placeholders and settings sorted
Ordinal by content, never ImmutableDictionary reference equality.

Fixed endpoints are:

```csharp
public sealed record CommandOptions(int? TimeoutSeconds = null);
public sealed class OrmSession : IAsyncDisposable
{
    public static OrmSession Borrow(DbConnection connection, SqlProfile profile,
        ProviderServices services, DbTransaction? transaction = null,
        CommandOptions? options = null);
    public static OrmSession Own(DbConnection connection, SqlProfile profile,
        ProviderServices services, CommandOptions? options = null);
    public ValueTask DisposeAsync();
}
public static class QueryExecutionExtensions
{
    public static List<T> ToList<T>(this BoundCommand<T> command, OrmSession session);
    public static List<T> ToList<T>(this BoundCommand<T> command, OrmSession session, CompiledMapping<T> mapping);
    public static List<T> ToList<T>(this Query<T> query, OrmSession session);
    public static Task<List<T>> ToListAsync<T>(this Query<T> query,
        OrmSession session, CancellationToken cancellationToken = default);
    public static IAsyncEnumerable<T> StreamAsync<T>(this Query<T> query,
        OrmSession session, CancellationToken cancellationToken = default);
    public static Task<List<T>> ToListAsync<T>(this BoundCommand<T> command,
        OrmSession session, CancellationToken cancellationToken = default);
    public static IAsyncEnumerable<T> StreamAsync<T>(this BoundCommand<T> command,
        OrmSession session, CancellationToken cancellationToken = default);
}
```

The facade declarations above are the normative product signatures. Their bodies
are specified by the execution packet and mature Runtime calls; they are not
claimed to be the exact connection-only signatures of every research prototype.
ProviderServices is an immutable execution-infrastructure object containing the
profile matcher, CommandFactory<BoundArguments>, declared scalar/advanced codecs
and driver capabilities. Provider factories create it; ordinary applications do
not assemble its fields. Its precise factory members are fixed in ORM-EXECUTION.

For every call: reject a disposed session; honor pre-cancellation; render/bind if
given a Query; validate profile, slot set/types/list arity and projection mapping;
acquire the session's one-operation lease; construct the Dapper command with Text
and the specified timeout; invoke its buffered or streaming method. Release the
lease in a finally after the mature operation/enumerator disposes. No execution
path traverses AST after rendering or parses SQL to rediscover parameters.

An owned session disposes its connection on DisposeAsync; a borrowed session never
disposes the caller connection/transaction. Both preserve Dapper's initial
open/closed-state policy per operation. Concurrent use fails `KORM-EXEC-002` before
sending; it does not queue or create a private scheduler. The lease transitions are
Idle → Active → Idle, with Disposed terminal. DisposeAsync during Active fails
`KORM-EXEC-003`; callers must finish/dispose the active stream first. This avoids
silently cancelling another caller or racing driver disposal.

A streaming wrapper is lazy, single-use and single-enumerator. Its first
GetAsyncEnumerator atomically claims it; another attempt fails KORM-EXEC-004.
MoveNextAsync overlap fails KORM-EXEC-005. It forwards enumeration to the mature
Dapper iterator and forwards DisposeAsync exactly once. Buffered Query calls may be
invoked again; each call creates a fresh bound invocation. A reusable template may
bind again. BoundCommand contains one internal shared atomic InvocationState; after
preflight and session admission, its first 0→1 transition consumes it. A later
attempt fails KORM-EXEC-006 even after another session becomes idle. Pre-cancellation
and failed preflight do not consume it; failure after dispatch does. A failed
command admission releases any session lease it acquired. For a stream, command
admission occurs on first MoveNext, not when creating its wrapper.

Errors preserve the provider exception as the original exception whenever no
Korda-specific context is needed. A conversion/shape wrapper retains InnerException
and ordinal/alias/expected type, never the parameter value. Cancellation and timeout
are not rewritten into successful empty results. Commit failures can have unknown
outcome; there is no retry. Transactions/savepoints use explicit driver operations
through the session/provider APIs described in the provider packets.

## 8. Diagnostic vocabulary and required outcomes

| Code | Condition | Detection / required outcome |
| --- | --- | --- |
| KORM-MODEL-001 | Unknown node tag or inconsistent descriptor | Pure validation; no SQL template |
| KORM-SCOPE-001 | Unbound relation/CTE or forbidden correlation | Pure scope pass; identify offending expression path |
| KORM-SCOPE-002 | Duplicate alias or invalid qualified identifier | Construction/scope validation |
| KORM-QUERY-001 | Invalid grouping/aggregate/window context | Pure semantic pass |
| KORM-QUERY-002 | Incompatible set degree/type or DML assignment | Generic compilation where expressible, otherwise pure validation |
| KORM-QUERY-003 | Update/Delete has neither Where nor explicit AllRows | Pure validation; no executable mutation |
| KORM-QUERY-004 | Invalid window frame/order/bound combination | Pure validation before lowering |
| KORM-BIND-001 | Missing required slot | Bind/preflight, before DbCommand creation |
| KORM-BIND-002 | Conflicting slot/type or duplicate builder entry | Bind/preflight; same label alone is never a collision |
| KORM-BIND-003 | Expanded-list arity differs from template | Bind/preflight; SQL is unchanged |
| KORM-BIND-004 | Null supplied to a required slot | Bind/preflight, retaining declared SQL type for nullable NULL |
| KORM-BIND-005 | Missing codec/snapshot or invalid value facet | Preflight; no reflection fallback |
| KORM-EXEC-001 | Profile/transaction/timeout mismatch | Before sending SQL |
| KORM-EXEC-002..006 | Concurrent session, active disposal, repeated stream, overlapping MoveNext, reused BoundCommand | Exact transitions in section 7 |
| KORM-MAP-001 | Missing or duplicate static mapping registration | Get/Register; no dynamic mapper creation |
| KORM-MAP-002 | Projection mismatch or missing result codec/read conversion/closed type | Preflight; first-row Tokenize validates actual columns |
| KORM-MAP-003 | Required result NULL | Before returning that row; preserve underlying cause |
| KORM-TYPE-005 | Known value/conversion fails its checked representation | Preflight for inputs or before returning that row for outputs; retain cause |
| KORM-DIALECT-* | Unsupported clause/lowering precondition/version | Before rendering/execution, as enumerated by dialect packets |
| KORM-TYPE-*, KORM-NESTED-*, KORM-PARSER-* | Specialized type, nesting or optional parser violation | Defined by the corresponding packet and source mapping |
| ORMGEN* | Generator diagnostics | Exact IDs, source locations and fix instructions in generation-integration.md |

Exceptions use `KordaOrmException` with `Code`, `Operation`, optional `ExpressionPath`,
optional `ColumnOrdinal`/`ColumnAlias`, `Profile`, and InnerException. Invalid public
arguments use ArgumentException/ArgumentOutOfRangeException with the corresponding
code in Data["KordaCode"]. Cancellation uses OperationCanceledException. Error
messages contain type/shape metadata, not SQL values or credentials.

## 9. Required cross-module examples

The canonical fixture has departments `(1,Engineering),(2,Operations)` and users
`(1,Alice,32,1,1),(2,Bob,18,1,1),(3,Carol,NULL,0,2),(4,Dana,44,1,2),
(5,Eve,18,1,NULL)`. Columns are explicit BIGINT/text/nullability metadata; projection
members are `long Id`, `string Name`, `long? Age`. Individual dialects define exact
quoting and boolean transport, without changing these intended values.

| Case | Required input and result |
| --- | --- |
| Optional composition | Active=1 returns IDs 1/2/4/5; add Age>=20 returns 1/4; add Name=Alice returns 1; parameter order follows final SQL |
| Identity | Use the same slot in two predicates: two physical occurrences, one logical value; distinct slots both named `id` retain values 1/2 |
| NULL | `Age.Eq(nullableNull)` returns no rows; `Age.IsNull()` returns ID3; result Age for Carol remains null, never numeric zero |
| Lists | IN []→none, [2]→2, [1,3,5]→1/3/5; changed bound arity fails KORM-BIND-003 |
| JOIN | Left join returns five rows; Eve's department is NULL; absent nested department differs from a present row with nullable members |
| Aggregate | Department counts both 2; max ages Engineering32/Operations44; COUNT(empty)=0 and SUM(empty)=NULL |
| Reordered projection | SQL aliases Name/Id/Age map to the same known User DTO using generated tokens; unexpected alias/duplicate/missing member fails |
| Empty projection mismatch | Empty result returns empty collection; no claim of first-row Tokenize running; direct-reader oracle separately checks schema |
| Resource | Early stream break disposes reader/command, releases session lease and permits the next query; owned/borrowed connection disposition follows section 7 |
| Transaction | Insert ID6 inside a caller transaction is visible there, rollback restores five; committed age change persists; commit failure is not automatically retried |
| AOT | Known DTO classes, records/init and generic facade calls run from native executable; object-template DynamicParameters remains a required failing control |

The final consumer generator roots each referenced CompiledRow(rowType,registrarType)
marker by a direct registrar.EnsureRegistered call. That public registrar has one
explicit static constructor and a NoInlining entry; declaring and consumer module
initializers call the same entry. The observed library-only Native AOT failure is
recorded in generation-integration; merely referencing a DTO type does not promise
its library initializer ran. Without generation, callers use explicit static
registration/mapping. Built-in BCL scalars are rooted lazily by Mapping<T>.Get through
BuiltInMapping<T>'s explicit static initialization and a fixed typeof(T) equality
list, not an assembly scan. Preserve an already registered manual mapping.

The original-library probe used repeated named-parameter reuse. The product policy
here intentionally emits one physical occurrence per textual occurrence; do not
copy that probe's shortcut into the renderer. Likewise the probe's small AST and
permissive manually written row factory are not substitutes for the immutable
model, strict generated mapper or final packet acceptance.

## 10. What remains an implementation activity

Implementers write the specified files, port the cited algorithms, integrate the
pinned mature Runtime, run the stated local/native/database cases and correct bugs.
They do not choose another execution engine, change parameter identity, weaken NULL
semantics, invent API names or resolve packet dependency contradictions on their own.
A new requirement returns through a reviewed contract-version change and affected
packet update. Internal optimization may change storage only after measured evidence
and without changing these public/semantic contracts; no packet requires speculative
pooling or a new execution loop to pass its initial correctness gate.
