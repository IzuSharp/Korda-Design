# Static entity and DTO generation

Current Korda source generation uses the ten database attributes in the [DB-Rename-01 contract](../database/db-attribute-names.md). Exact types live in `Korda.Data`; tutorial and business code omit the `Attribute` suffix. The product [generator guide](https://github.com/IzuSharp/Korda/blob/task/DB-Rename-01-linux/docs/guides/query-generator.md) and [compiled reference](https://github.com/IzuSharp/Korda/blob/task/DB-Rename-01-linux/src/Query.Generator/api-reference.md) own current declarations and complete examples. The rename preserves the generation and materialization requirements below.

## 1. Required application experience

An application references one Korda database provider package with its precompiled native asset. It defines ordinary C# entities and immutable DTOs, uses typed Fluent APIs and publishes Native AOT. Adding a model that uses existing codecs/operators must not require a native-engine rebuild or wait for CI. C++20/libpq/sqlite3 retain the existing SQL/query/database semantics.

No full IQueryable provider, runtime expression compilation, Reflection.Emit, dynamic proxy mapper, runtime generic construction or broad reflective setter path is required. Business code remains ordinary compiled C#. Handwritten static metadata remains supported through the same public API and native engine.

## 2. What is generated and what is not

The current [DB-Exec-02 target](../database/query-semantics.md#current-execution-path-target-db-exec-02)
selects one validated result layout and direct typed row access, using the actual
Dapper.AOT benchmark-generated command factory/reader as the comparison input.
Candidate B introduced the validated layout; the current
[cursor pull implementation](../database/cursor-pull-execution.md) carries it
through one stable scoped native batch owner and synchronous `RowReader` spans.
Existing generated and handwritten constructors use that same production
path; no per-cell borrowed `Memory` adapter is required. Actual pinned reference factories/readers and external Native AOT consumers
are bound in the [implemented 17da record](../database/execution-path-17da.md).
Both independent provider package gates passed, and the
[final local evidence](https://github.com/IzuSharp/Plan/blob/adcdc9172bf47a0df8fe5fcb8259357625526280/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/README.md)
records four complete serial 1,800-second cells. Normal merges, main CI and
public publication/consumption remain pending. Total measured managed allocation
includes business output, harness, framework and driver; framework-only 0 B is
not established. Stable parameter ordinals and value writing remain separate
from arbitrary Fluent-method capture. This refactor does not announce a new
public fixed-query generator API.

The following generation inventory describes retained public behavior. Its
changed internal result path is source- and test-bound in the cursor record;
this does not introduce fixed-query method-body capture.

The resumed [query decision](../database/query-semantics.md) distinguishes the NWQC
implementation candidate from future fixed-query templates. Current generation
covers model/projection declarations; it does not capture arbitrary Fluent method bodies
or precompile their SQL. Fixed-shape query generation is an optional later step,
with explicit syntax, diagnostics and handwritten parity required before support
can be claimed.

Generate typed table/column/projection descriptors, static readers and direct constructors, explicit nullable/value codec policies, AOT-visible closed generic mappings and compile diagnostics. Generated and handwritten forms preserve the same metadata, codecs, key/concurrency flags, nullability, projection order and execution path.

Do not generate C# SQL dialects, a query optimizer, hidden client evaluation or application-specific native model code. Generation must not contact a database/network, invoke a native compiler, change native libraries or execute application model getters. Maintainer build integration is separate from consumer source generation.

## 3. Incremental pipeline and deterministic inputs

Use syntax filtering followed by semantic symbols for explicitly opted-in model/projection declarations. Resolve property type/nullability, declared table/column names, keys, codecs and allowed constructor/member assignments. Resolve attributes through their actual semantic metadata names. Diagnostics bind to the offending source spans. Generated names and ordering derive from stable fully qualified metadata identities rather than dictionary iteration, timestamps or random GUIDs.

Preserve stable syntax/semantic equality and incremental behavior when unrelated or relevant model inputs change. Generate directly into the consumer compilation; do not expect to read another generator's generated syntax in the same pass. Shared declarations belong in an explicit versioned schema input or reusable generator model with tests. Build integration owns any explicit multistage maintainer operation. Analyzer/generator host compatibility is tested independently of application target-framework compatibility.

```csharp
using Korda.Data;

[DbTable("students", DescriptorName = "Students")]
public sealed record Student(
    [property: DbKey, DbColumn("id")] long Id,
    [property: DbColumn("name")] string Name,
    [property: DbColumn("age")] int Age);

[DbProjection(DescriptorName = "StudentRows")]
public sealed record StudentRow(long Id, string Name);
```

The CLR property spelling remains the default store name. `[DbColumn]` supplies an exact override without renaming the generated typed member. The lowercase names above are deliberate mappings, not an implicit casing convention. A parameterless `[DbTable]` uses the existing documented `Id` convention; the explicit-name constructor retains its existing defaults.

`[DbConstructor]` selects a constructor, and `[DbParameter(nameof(Member))]` selects its member association. `[assembly: DbCodec(...)]` registers a shared conversion default; `[DbUseCodec(...)]` selects a policy at a member. Preserve nullable wrapping and the same codec policy for writes, generated readers and Fluent projection binding. Reverse scaffolding emits these same names and preserves exact catalog names through safe identifiers/literals and explicit aliases.

## 4. Static materialization and errors

Projection descriptors carry ordered column/codec IDs, nullability and expected result shape. The native layer emits bounded typed batches; C# checks the complete expected shape and invokes direct typed readers/constructors. Validate count, order, aliases, codec/type and nullability before interpreting values. Missing or duplicate columns are errors; a missing nullable column must never be treated as SQL NULL. Static application typing cannot prove a malformed or schema-drifted native result is correct.

A mapping failure or user constructor exception stops iteration, releases the owned batch in `finally`, closes/drains the cursor through the existing asynchronous lifetime contract and preserves the transaction outcome. No reflection or stringification fallback is permitted. Non-null targets receiving SQL NULL, integer narrowing/precision loss, invalid UTF-8 and unknown codec IDs fail explicitly. Ordinary DTO strings/bytes own managed copies; separate lifetime-scoped zero-copy views cannot escape their owner by default.

JSON continues using explicitly supplied source-generated `JsonTypeInfo` and `JsonSerializerContext`. Closed generic mappings must be AOT-visible; arbitrary result types cannot be created from untrusted runtime names. Preserve dynamic-code/trimming checks. Boxing, descriptor initialization allocation and generated code size require evidence before a zero-cost claim.

## 5. Fluent binding without method-body capture

Fluent operators are ordinary C# calls. A convenience lambda over expression
proxies is a normal builder delegate, not an arbitrary domain predicate interpreted
later. The preceding DB-Perf-01 candidate records a complete bounded NWQC command in C# before
one native compile/render/CTE submission; C++ remains the SQL compiler and execution
owner. `.Prepare()` performs runtime SQL and parameter-layout compilation, not
build-time compilation of arbitrary method bodies. The generator does not rewrite
every method invocation or intercept arbitrary calls. Unknown application methods are outside static query
generation. Capability-gated operations resolve against the selected profile and
are validated again by C++ before provider dispatch.

Dynamic filtering resolves validated table/field/operator metadata and bound
parameters within finite node/depth/byte limits. The complete command represents
only supported Fluent operations, not a universal Core query IR or managed SQL
evaluator. Mutable ownership, native owner/generation validation and immutable
frozen plans retain their existing rules.

A future fixed-query template may precompute shape, parameter slot order and
projection mapping only when those inputs are statically known. Actual parameter
values, source generation, provider capabilities, session/transaction and cancellation
remain runtime inputs. Such generation must not execute user getters, invoke a
native compiler, depend on a live database or silently evaluate unsupported syntax.
Dynamic condition branches remain a supported ordinary composition path. Emitted
templates, runtime `.Prepare()` and physical connection statement caches must be
reported as separate layers; none proves the other two exist.

The selected runtime fixed-key Find cache is separate from that future generator
feature. It compiles model-key slots once per bounded Source cache entry and
uses the existing generated Table.Row reader. It does not capture C# method
bodies, call user getters during generation, or require generated descriptors;
handwritten tables keep the same behavior and exact mapper identity.

## 6. Diagnostics and compatibility

DB-Rename-01 changes the attribute names in matching, generated C# and diagnostic messages; it does not repurpose diagnostic IDs or silently change the negative cases.

| ID | Error and remedy |
| --- | --- |
| NWQ0101 | No static codec for a mapped member; use a supported scalar or exact accessible codec policy |
| NWQ0102 | Nullable column mapped to a non-null constructor/key; declare a consistent static policy |
| NWQ0103 | Ambiguous or inaccessible static construction; select an accessible constructor or writable/init properties |
| NWQ0104 | Duplicate/inconsistent metadata, alias, key or mapping policy; supply unique exact metadata |
| NWQ0105 | Required codec capability absent from the selected compile-time profile; choose a compatible profile |
| NWQ0106 | Unsupported source input/dependency shape; use explicit shared input or handwritten descriptors |
| NWQ0107 | Mapping would require dynamic code or runtime discovery; supply a closed static mapping |

Cross-entity/value type errors should fail through ordinary C# typing. Runtime profile mismatch remains a structured domain error rather than a fictitious compile diagnostic. Unknown metadata schemas or required codecs fail early without reflection/provider fallback. Metadata-schema and capability changes require explicit generator/package compatibility checks. A business model hash is distinct from ABI, package and capability versions.

## 7. Descriptor and operation invariants

DB-Exec-02 removes the redundant command replay adaptation and native parameter
re-encoding and uses generation-scoped spans for typed results. It keeps native
owner/profile validation, per-execution value snapshots and complete shape/extent
validation. Each new batch is validated once; projection proof is reused only
for the same fields and expectation, and each typed value retains its lifetime,
ordinal, codec and data-dependent checks. Ordinary DTO strings/bytes still own
their resulting managed data. Do not claim whole-query zero from generated row access or treat
an upstream generated fixture as the actual emitted consumer.

A table's canonical metadata includes schema-format version, logical identity, validated names, scalar codec/nullability, primary keys and ordered projection fields. The existing v1 table relations array stays reserved empty. An explicit relation has separate canonical metadata containing both table/model identities, ordered parent-key/child-key pairs and child nullability; registering a relation does not rewrite either table hash. Adding a supported entity registers another descriptor and does not change native assets.

| Phase | Required invariant |
| --- | --- |
| Generator input | Stable syntax/semantic equality; deterministic names/order; diagnostics point to source spans |
| Build | Generated and handwritten descriptors/readers use the same API; no native compiler or database calls |
| Query call | C# checks entity/value types and records bounded local operations; existing metadata registration keeps its native owner checks |
| Compile/render/CTE | C++ validates the complete command, source-bound owner sidecar and profile; explicit preparation caches SQL and immutable parameter metadata |
| Execution | Snapshot changing parameters; every reused shape receives independently validated values and provider execution retains its own error boundary |
| First result | Validate complete ordered shape; reject duplicates, missing columns and type mismatches before NULL handling |
| DTO construction | Invoke the selected typed constructor; failures release batches and close/drain cursors |
| Compatibility | Reject unknown metadata schema, codec and incompatible capability/profile without fallback |

## 8. Verification and evidence boundary

Retain generated-source goldens, deterministic/incremental checks for unrelated/model edits, compiler-host fixtures, diagnostic-span checks, and negative wrong entity/value/nullability/constructor/codec cases. Preserve generated-versus-handwritten parity, mixed-query alias rejection, Dispose/seal race checks, unknown dynamic field/operator rejection, missing/duplicate result-column tests, constructor-failure cleanup, schema/hash drift, native profile mismatch and bounded large-field/batch behavior. Existing semantic differential tests retain their source-bound oracles.

For this task, run dependency-selected Korda checks and the Linux x64 external PackageReference order consumers for the actual SQLite and PostgreSQL candidates. Compile generated entities, immutable DTOs and reverse-scaffolded entities; run real database reads/writes. Rebuild after a DTO/model change and verify the packaged and loaded native bytes remain identical. A generator unit test, successful compilation or AOT publication is not an executed consumer result. Product receipts and PR checks remain distinct from Design document checks.

The current Korda AGENTS controls check selection: consumer execution is Native AOT, with no JIT, clean-image, CPU-emulation or extra platform campaign unless separately requested. This preserves the invariants above without turning historical platform experiments into new task acceptance.

## Historical research

The accepted D17/C-QUERYGEN-001 research contract, original Rust/SeaORM implementation studies, provisional declarations, Windows/Linux research outputs and their exact hashes remain in the [immutable pre-scope snapshot](https://github.com/IzuSharp/Korda-Design/blob/c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9/docs/generators/query-generation.md). In particular, the original nullable-decoding research motivated the missing-column preflight that remains required above. Those experiments retain their identities and do not establish execution of this renamed candidate. Frozen acceptance gates still read the original bytes.
