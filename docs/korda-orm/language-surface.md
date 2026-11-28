# Fixed language surface completion

Version: **0.2.0 proposed**, paired with [implementation-spec.md](implementation-spec.md).
These are deliberate C# representation/API decisions derived from the pinned
[source mapping](language-model.md) and [dialect mapping](dialects-and-generation.md),
not a claim of identical Java generic return types or an unchanged jOOQ object model.

This is the normative completion of the compact common declarations. The existing
single-field `Sql.Select<T>(Field<T>) -> Query<T>`, `LimitLiteral(int)`, Mutation /
ReturningMutation<T> split and Language-owned extension-class names remain unchanged.
All data handles/enums/nodes are Contracts; all factories/operators are Language.
Only Language's own Sql facade fragments are partial; no type spans assemblies.
The full construction/validation/fixture algorithms are fixed in ORM-QUERY,
ORM-RELATIONAL, ORM-DML and ORM-EXPRESSIONS. This section adds no product implementation.

## Query additions and payloads

The following methods are added to QueryOperations. Ordered node fields replace
the earlier abbreviated Select/Join/Set payloads. A join's left prefix is already
Select.From plus preceding joins; it is not stored or visited twice.

```csharp
// QueryOperations
public static Query<T> CrossJoin<T>(this Query<T> query, TableLike table);
public static Query<T> DistinctOn<T>(this Query<T> query, params IField[] keys);
public static Query<T> Qualify<T>(this Query<T> query, Condition predicate);
public static Query<T> IntersectAll<T>(this Query<T> query, Query<T> other);
public static Query<T> ExceptAll<T>(this Query<T> query, Query<T> other);
public static Query<T> ForUpdate<T>(this Query<T> query, params TableLike[] of);
public static Query<T> ForShare<T>(this Query<T> query, params TableLike[] of);
public static Query<T> NoWait<T>(this Query<T> query);
public static Query<T> SkipLocked<T>(this Query<T> query);

// Contracts: closed public policy values
public enum SelectDistinctKind { All, Distinct, On }
public enum LockStrength { Update, Share }
public enum LockWait { Wait, NoWait, SkipLocked }
public enum SetOperationKind { Union, UnionAll, Intersect, IntersectAll, Except, ExceptAll }

// Contracts/Nodes/Query.cs: ordered immutable data, no capture sidecars
internal sealed record SortNode(SqlNode Expression, SortDirection Direction, NullOrder Nulls);
internal sealed record ColumnNode(RelationId Relation, SqlName Name,
    SqlTypeDescriptor Type, string? ConversionId = null) : SqlNode(NodeKind.Column);
internal sealed record DistinctSpecNode(SelectDistinctKind Kind, ImmutableArray<SqlNode> Keys);
internal sealed record LockClauseNode(LockStrength Strength,
    ImmutableArray<RelationId> Of, LockWait Wait);
internal sealed record SelectNode(
    ImmutableArray<ProjectionItem> Projection,
    SqlNode? From, ImmutableArray<JoinNode> Joins, SqlNode? Where,
    ImmutableArray<SqlNode> GroupBy, SqlNode? Having,
    ImmutableArray<NamedWindowNode> Windows, SqlNode? Qualify,
    ImmutableArray<SortNode> OrderBy, SqlNode? Limit, SqlNode? Offset,
    DistinctSpecNode Distinct, ImmutableArray<CteDefinitionNode> Ctes,
    LockClauseNode? LockClause) : QueryNode(NodeKind.Select);
internal sealed record JoinNode(JoinKind JoinKind, SqlNode Right, SqlNode? On)
    : SqlNode(NodeKind.Join);
internal sealed record SetNode(SetOperationKind Operation, QueryNode Left,
    QueryNode Right, ImmutableArray<SortNode> OrderBy, SqlNode? Limit,
    SqlNode? Offset, ImmutableArray<CteDefinitionNode> Ctes)
    : QueryNode(NodeKind.Set);
```

DistinctOn replaces Distinct and retains ORDER; only PG supports it, with its pinned
sort-group rule (partial order by only distinct keys is legal). Qualify is explicit
but rejected by all four initial profiles. CrossJoin has no ON. Set operations
preserve the full binary tree; Order/Limit/Offset/With after composition affect the
root tail. Other Select-only operations on SetNode require an explicit outer query.
Set degree, logical shape, type/facets/nullability/carrier and effective conversion
IDs must match; no implicit widening. OF accepts only local physical relations.
NoWait/SkipLocked require a lock and are mutually exclusive. The baseline lockable
shape is physical FROM plus INNER/CROSS joins, with no distinct/group/window/set.
PG admits UPDATE/SHARE, OF and both wait modifiers; MySQL admits UPDATE/SHARE and
both modifiers with empty OF; Maria admits UPDATE/LOCK IN SHARE MODE with Wait and
empty OF; SQLite rejects locks. Execution never starts an implicit transaction.

## Relational additions and payloads

RelationalOperations additionally exposes these exact methods; Sql adds Rank and
DenseRank, both Field<long>. QueryOperations owns IntersectAll/ExceptAll above.

```csharp
public static Cte<T> Materialize<T>(this Cte<T> cte, CteMaterialization materialization);
public static WindowSpec GroupsBetween(this WindowSpec window, WindowBound start, WindowBound end);
public static WindowSpec Exclude(this WindowSpec window, WindowExclusion exclusion);
public static Field<long> Rank(); // Sql
public static Field<long> DenseRank(); // Sql
public readonly record struct CteId(long Value);
public enum CteMaterialization { Default, Materialized, NotMaterialized }
public enum WindowFrameUnit { Rows, Range, Groups }
public enum WindowBoundKind {
    UnboundedPreceding, Preceding, CurrentRow, Following, UnboundedFollowing
}
public enum WindowExclusion { NoOthers, CurrentRow, Group, Ties }
public sealed class WindowBound {
    public WindowBoundKind Kind { get; }
    public long Offset { get; }
    internal WindowBound(WindowBoundKind kind, long offset);
    public static WindowBound UnboundedPreceding { get; }
    public static WindowBound CurrentRow { get; }
    public static WindowBound UnboundedFollowing { get; }
    public static WindowBound Preceding(long offset);
    public static WindowBound Following(long offset);
}

internal sealed record CteDefinitionNode(CteId Id, string Name,
    ResultShape Columns, SqlNode Body, bool Recursive,
    CteMaterialization Materialization) : SqlNode(NodeKind.CteDefinition);
internal sealed record CteReferenceNode(CteId Cte, RelationId Relation,
    string Alias) : SqlNode(NodeKind.CteReference);
internal sealed record DerivedTableNode(QueryNode Query, RelationId Relation,
    string Alias) : SqlNode(NodeKind.DerivedTable);
internal sealed record WindowFrameNode(WindowFrameUnit Unit, WindowBound Start,
    WindowBound End, WindowExclusion? Exclusion);
internal sealed record WindowNode(ImmutableArray<SqlNode> Partition,
    ImmutableArray<SortNode> Order, WindowFrameNode? Frame)
    : SqlNode(NodeKind.Window);
internal sealed record NamedWindowNode(string Name, WindowNode Definition)
    : SqlNode(NodeKind.NamedWindow);
internal sealed record OverNode(SqlNode Function, WindowNode? InlineWindow,
    string? WindowName, SqlTypeDescriptor ResultType, string? ConversionId)
    : SqlNode(NodeKind.Over);
internal sealed record ExistsNode(QueryNode Query) : SqlNode(NodeKind.Exists);
internal sealed record ScalarSubqueryNode(QueryNode Query,
    SqlTypeDescriptor ResultType, string? ConversionId)
    : SqlNode(NodeKind.ScalarSubquery);
```

Materialization defaults to Default; Materialize returns a new snapshot of the same
CteId. Explicit hints are supported only for SELECT-body PG/SQLite CTEs. GROUPS and
EXCLUDE are PG/SQLite only; explicit NoOthers remains a capability-bearing clause.
Groups requires ORDER; RANGE offsets require one numeric ORDER key. Frame offsets
are nonnegative Int64 literals; compare conceptual signed positions without integer
overflow. Frame builders reset the exclusion; Exclude requires a frame. Ranking
functions require OVER and reject explicit frames in this bounded surface.
Over preserves aggregate result conversion IDs. Cte/derived Column<U> copies the
selected ResultColumn.ConversionId into its ColumnNode.

## DML additions and payloads

```csharp
// Sql facade additions
public static Field<T> Excluded<T>(Field<T> targetColumn);
public static Cte<T> Cte<T>(string name, ReturningMutation<T> command);
// DmlOperations additions
public static InsertBuilder With(this InsertBuilder command, params Cte[] definitions);
public static UpdateBuilder With(this UpdateBuilder command, params Cte[] definitions);
public static DeleteBuilder With(this DeleteBuilder command, params Cte[] definitions);
public static ReturningMutation<T> With<T>(this ReturningMutation<T> command, params Cte[] definitions);
public enum ConflictTargetKind { Columns, Constraint, AnyUniqueKey }
public enum ConflictAction { DoNothing, DoUpdate }
internal sealed record AssignmentNode(ColumnNode Target, SqlNode Value);
internal sealed record ConflictTargetNode(ConflictTargetKind Kind,
    ImmutableArray<ColumnNode> Columns, SqlName? Constraint, SqlNode? Predicate);
internal sealed record ConflictNode(ConflictTargetNode Target, ConflictAction Action,
    ImmutableArray<AssignmentNode> Assignments, SqlNode? UpdateWhere);
internal abstract record InsertSource;
internal sealed record ValuesSource(ImmutableArray<ImmutableArray<SqlNode>> Rows)
    : InsertSource;
internal sealed record QuerySource(QueryNode Query) : InsertSource;
internal sealed record DefaultValuesSource : InsertSource;
internal sealed record InsertNode(TableNode Target, ImmutableArray<ColumnNode> Columns,
    InsertSource? Source, ConflictNode? Conflict, ReturningProjectionNode? Returning,
    ImmutableArray<CteDefinitionNode> Ctes) : DmlNode(NodeKind.Insert);
internal sealed record UpdateNode(TableNode Target,
    ImmutableArray<AssignmentNode> Assignments, ImmutableArray<SqlNode> From,
    SqlNode? Where, bool AllowAllRows, ReturningProjectionNode? Returning,
    ImmutableArray<CteDefinitionNode> Ctes) : DmlNode(NodeKind.Update);
internal sealed record DeleteNode(TableNode Target, ImmutableArray<SqlNode> Using,
    SqlNode? Where, bool AllowAllRows, ReturningProjectionNode? Returning,
    ImmutableArray<CteDefinitionNode> Ctes) : DmlNode(NodeKind.Delete);
internal sealed record ExcludedNode(RelationId Target, SqlName Column,
    SqlTypeDescriptor Type) : SqlNode(NodeKind.Excluded);
internal sealed record ProjectionItem(SqlNode Expression, string Alias,
    SqlTypeDescriptor Type);
internal sealed record ReturningProjectionNode(RelationId Target,
    ImmutableArray<ProjectionItem> Items) : SqlNode(NodeKind.ReturningProjection);
```

Excluded is legal only in the matching insert's conflict-update RHS/predicate.
With appends in declared order. PG permits top-level nonrecursive returning DML CTEs;
a DML CTE nested in a scalar/derived/CTE body is rejected. SQLite mutation WITH may
contain only SELECT bodies. MySQL outer WITH is admitted for UPDATE/DELETE, not
Insert.With. Maria outer mutation WITH is excluded. MySQL/Maria QuerySource.With
is emitted after INSERT's target/column prefix, never moved before INSERT.
DefaultValues requires no target columns; other insert sources require columns.
Source=null and no update assignments are unfinished states rejected at render.

## Finite expression method patterns

FieldOperations retains Eq/Ne/Lt/Le/Gt/Ge/IsDistinctFrom/IsNotDistinctFrom, each with
T/Param<T>/Field<T> RHS. In/NotIn each have IEnumerable<T>, ListParam<T>, Query<T>
RHS; the query must be one Scalar logical member with matching carrier. Between /
NotBetween each have all 3x3 lower/upper combinations of T/Param<T>/Field<T> and
one native BetweenNode, preserving a single left operand occurrence.

```csharp
public static Field<TTarget> Cast<TSource,TTarget>(this Field<TSource> value, SqlType<TTarget> target);
public static Field<T?> Nullable<T>(this Field<T> value) where T : struct;
public static Field<T?> NullableReference<T>(this Field<T> value) where T : class;
```

NumericFields is finite: same-N inputs short/int/long promote to long; float/double
to double; decimal to decimal without inherited p/s. Add/Subtract/Multiply generate
four nullable operand pairs and value/Param/Field RHS (72 methods per name).
Negate/Abs generate nonnullable and nullable receivers (12 per name). IntegerDivide
and Modulo cover the three integral carriers and always return long? (36 per name);
Divide covers float/double/decimal and always returns the nullable promoted carrier
(36). There are no mixed-N overloads. Integer/floating operands are explicitly
widened before native operations. Integer division uses / on PG/SQLite and DIV on
MySQL/Maria; modulo uses %. Native zero-divisor errors/NULLs remain native; no
NULLIF rewrite. SQLite native INTEGER overflow producing REAL fails strict MAP-002.

TextFields exposes Like/NotLike/Concat with string/Param<string>/Field<string> RHS,
Lower/Upper and Length (long); a separately named Nullable set uses nullable text
and nullable results. This avoids signatures differing only by reference annotations.
Escape is explicit char (non-NUL, nonsurrogate). Concat uses PG/SQLite || and MySQL /
Maria CONCAT; Length uses native character length cast to Int64, including SQLite's
native stop-at-NUL behavior. Native lower/upper does not promise portable case fold.
The null helper and aggregate declarations are fixed as follows; comments specify
mechanical RHS additions, not optional overloads:

```csharp
// Sql facade: all inputs have one common declared SQL identity/facet set
public static Field<T> Coalesce<T>(params Field<T>[] values);
// FieldOperations: nonnull fallback gives a nonnullable value result
public static Field<T> Coalesce<T>(this Field<T?> value, Field<T> fallback) where T : struct;
public static Field<T> CoalesceReference<T>(this Field<T?> value, Field<T> fallback) where T : class;
// Each fallback also has T and Param<T> forms.
public static Field<T?> NullIf<T>(this Field<T> value, Field<T> other) where T : struct;
public static Field<T?> NullIf<T>(this Field<T?> value, Field<T?> other) where T : struct;
public static Field<T?> NullIfReference<T>(this Field<T> value, Field<T> other) where T : class?;
// Each NullIf RHS also has the corresponding value and Param forms.

// Sql facade: count and ordered aggregates
public static Field<long> Count();
public static Field<long> Count<T>(Field<T> value);
public static Field<long> CountDistinct<T>(Field<T> value);
public static Field<T?> Min<T>(Field<T> value) where T : struct;
public static Field<T?> Min<T>(Field<T?> value) where T : struct;
public static Field<T?> Max<T>(Field<T> value) where T : struct;
public static Field<T?> Max<T>(Field<T?> value) where T : struct;
public static Field<T?> MinReference<T>(Field<T> value) where T : class?;
public static Field<T?> MaxReference<T>(Field<T> value) where T : class?;
```

Sum/Avg generate six numeric carriers x two input nullabilities x two names: 24
methods. Integer/decimal Sum/Avg return decimal? except floating inputs return
double?; integer SUM and decimal SUM/AVG/floating aggregates retain their four
fixed conversion IDs. SQLite rejects exact decimal arithmetic and exact numeric
AVG; integer SUM retains its special native-Int64-to-decimal reader.

Contracts owns CaseBuilder<T>, SimpleCaseBuilder<TValue,TResult> and RowExpression
arities1..8, each with internal immutable node/capture construction. CASE signatures:

```csharp
// Sql facade
public static CaseBuilder<T> Case<T>(SqlType<T> resultType);
public static SimpleCaseBuilder<TValue,TResult> Case<TValue,TResult>(
    Field<TValue> value, SqlType<TResult> resultType);
// CaseOperations; each result operand also has TResult / Param<TResult> forms
public static CaseBuilder<T> When<T>(this CaseBuilder<T> c, Condition condition, Field<T> result);
public static Field<T> Else<T>(this CaseBuilder<T> c, Field<T> result);
public static SimpleCaseBuilder<TValue,TResult> When<TValue,TResult>(
    this SimpleCaseBuilder<TValue,TResult> c, Field<TValue> match, Field<TResult> result);
public static Field<TResult> Else<TValue,TResult>(
    this SimpleCaseBuilder<TValue,TResult> c, Field<TResult> result);
public static Field<T?> End<T>(this CaseBuilder<T> c) where T : struct;
public static Field<T?> End<T>(this CaseBuilder<T?> c) where T : struct;
public static Field<T?> EndReference<T>(this CaseBuilder<T> c) where T : class?;
public static Field<TResult?> End<TValue,TResult>(
    this SimpleCaseBuilder<TValue,TResult> c) where TResult : struct;
public static Field<TResult?> End<TValue,TResult>(
    this SimpleCaseBuilder<TValue,TResult?> c) where TResult : struct;
public static Field<TResult?> EndReference<TValue,TResult>(
    this SimpleCaseBuilder<TValue,TResult> c) where TResult : class?;
```

Searched When and either Else have value/Param/Field result forms. Simple When has
all 3x3 match/result forms. When appends; Else/End require >=1 branch. Explicit
result SQL type is mandatory. End omits ELSE and returns the nullable counterpart;
nullable reference helpers use separate names because constraints/annotations do
not define a CLR overload. Simple CASE keeps one base expression and normal NULL
comparison semantics.

For N=1..8, Sql.Row<T1,...,TN>(Field<T1>,...,Field<TN>) returns RowExpression of that
arity. RowOperations Eq/Ne/Lt/Le/Gt/Ge take same-arity row expression or Row value;
IsNull/IsNotNull take just the receiver; In/NotIn take Query<Row<T1,...,TN>> for
N>=2 and Query<T1> for N=1. No runtime row type synthesis, row-list parameter or
scalar composite projection is implied. NULL predicates are distinct ordered
conjunctions of component tests; native row comparisons are not expanded into an
unsafe repeated-prefix OR tree. Components also compare effective conversion IDs.

## Expression payloads and conversion lineage

```csharp
public enum ComparisonKind { Eq, Ne, Lt, Le, Gt, Ge, IsDistinctFrom, IsNotDistinctFrom }
public enum BooleanKind { And, Or }
public enum ArithmeticKind { Add, Subtract, Multiply, Negate, Abs, IntegerDivide, Divide, Modulo }
public enum CaseKind { Searched, Simple }
internal enum FunctionId {
    Count, Sum, Min, Max, Avg, Coalesce, NullIf, Concat, Lower, Upper, Length,
    RowNumber, Rank, DenseRank
}
internal sealed record BetweenNode(SqlNode Value, SqlNode Lower, SqlNode Upper,
    bool Negated) : SqlNode(NodeKind.Between);
internal sealed record ArithmeticNode(ArithmeticKind Operation, SqlNode Left,
    SqlNode? Right, SqlTypeDescriptor ResultType, string? ConversionId)
    : SqlNode(NodeKind.Arithmetic);
internal sealed record FunctionNode(FunctionId Function, ImmutableArray<SqlNode> Arguments,
    SqlTypeDescriptor ResultType, string? ConversionId, bool Distinct)
    : SqlNode(NodeKind.Function);
internal sealed record CastNode(SqlNode Value, SqlTypeDescriptor ResultType,
    string? ConversionId) : SqlNode(NodeKind.Cast);
internal sealed record NullabilityNode(SqlNode Value, SqlTypeDescriptor ResultType,
    string? ConversionId) : SqlNode(NodeKind.Nullability);
internal sealed record CaseBranchNode(SqlNode Test, SqlNode Result);
internal sealed record CaseNode(CaseKind CaseKind, SqlNode? Operand,
    ImmutableArray<CaseBranchNode> Branches, SqlNode? Else,
    SqlTypeDescriptor ResultType, string? ConversionId) : SqlNode(NodeKind.Case);
internal sealed record LikeNode(SqlNode Value, SqlNode Pattern, char Escape,
    bool Negated) : SqlNode(NodeKind.Like);
internal sealed record RowValueNode(ImmutableArray<SqlNode> Items,
    ImmutableArray<SqlTypeDescriptor> Types, ImmutableArray<string?> ConversionIds)
    : SqlNode(NodeKind.RowValue);
internal sealed record RowCompareNode(ComparisonKind Comparison,
    RowValueNode Left, RowValueNode Right) : SqlNode(NodeKind.RowCompare);
internal sealed record RowNullTestNode(RowValueNode Row, bool Negated)
    : SqlNode(NodeKind.RowNullTest);
internal sealed record RowInNode(RowValueNode Row, QueryNode Query, bool Negated)
    : SqlNode(NodeKind.RowIn);
```

Explicit target int16/int32 Cast nodes receive cast.int16.checked /
cast.int32.checked on all profiles. PG emits SMALLINT/INTEGER and reads that native
width; SQLite INTEGER and MySQL/Maria SIGNED read native Int64 then narrow checked.
Ordinary readers stay strict. Unknown/wrong-closed-type conversion is MAP-002,
conversion overflow TYPE-005, required physical DBNull MAP-003; native SQL cast
errors stay native. Int64/Double widening has null conversion ID.

Alias, CTE/derived columns, scalar-subquery and OVER wrappers retain conversion IDs.
CASE/Coalesce result branches and row components must have compatible effective
conversion IDs/physical representations (TYPE-003 otherwise); set columns require
matching IDs (QUERY-002). No reader choice depends on the first returned value.
Nested JSON leaves add one final optional data field:

```csharp
public sealed record NestedJsonMember(int CellIndex, string Name,
    ResultMemberKind Kind, SqlTypeDescriptor LogicalType,
    NestedShapeDescriptor? Nested = null, string? ConversionId = null);
```

Only Scalar JSON leaves may have a nonnull ID. Nested row columns already retain
ResultColumn.ConversionId. JSON encoding/decoding selects the fixed logical type
plus ID; cast IDs use checked integer tokens and decimal aggregates use decimal
strings. SQLite aggregate.int-sum.decimal explicitly casts its native INTEGER to
TEXT for this wire encoding. Unknown custom IDs without a fixed wire codec fail
NESTED-006 before dispatch. Nonidentity conversions never silently become ordinary
scalar readers through an alias, CTE, set, CASE or nested wrapper.

## Declaration check scope

The disposable surface-compile check expanded 694 added/finite declarations and
compiled Contracts, Types, Language and Rendering as separate assemblies with
nullable warnings as errors. Its positive consumer compiled numeric/CASE/row/lock/
GROUPS/materialization/DML-CTE combinations; negative Int32-result assignment and
mixed Int32/Int64 arithmetic failed as required. This verifies accessibility and
C# signature consistency, not runtime behavior, SQL correctness or production code.
