# jOOQ execution inheritance and the Java Native Image alternative

Status: continuation research for Korda-Orm-01, observed 2026-11-28. The selected
execution composition is recorded in [execution-aot.md](execution-aot.md). This
document supplies concrete source inheritance rules and a **successful, bounded**
C# Native AOT to Java Native Image database experiment. Java is a technically
viable candidate; crossing languages is not treated as a reason to declare it
impossible. Product implementation remains unauthorized.

## 1. Conclusions and the decision boundary

jOOQ contributes mature execution semantics beyond SQL rendering: ordered binding,
typed NULL handling, explicit conversion, static constructor mapping, nested-row
presence rules and cursor/resource lifecycle. These can be translated to C# while
retaining mature .NET execution machinery. Porting those semantics does not require
copying jOOQ's Java reflection mapper or rebuilding a database protocol.

A second route also works: a C# Native AOT program can send its runtime SQL and
typed values through a C ABI into a GraalVM Native Image shared library, execute a
mature JDBC driver and receive a concrete C# DTO. The experiment below passed 27
checks on real SQLite. It did not require a JVM process, runtime code generation,
a worker scheduler or a spin loop. Its fixed Java transport record and C# DTO
have the same three fields; arbitrary new DTO shapes were not exercised.

That success does not eliminate the additional native boundary: explicit handle
ownership, two managed heaps, attached native threads, UTF-8 transfer, result
representation and native packaging still need maintaining. If the .NET mature
runtime route meets the same required semantics, it preserves direct .NET driver
and DTO integration with fewer maintained boundaries. This is a maintenance and
composition argument, not an unmeasured claim that every Java query is slower.

## 2. Fixed source evidence and reusable mechanisms

All jOOQ references below use version 3.21.10, commit
`3c58109e7ab69772de75e640852935ee7e284177`. Only the public bodies actually present
at this commit are source inputs. The full upstream private regression suite is
not assumed to be available.

| Source / actual symbol | Mature behavior to retain | C# implementation location and adaptation |
| --- | --- | --- |
| [Binding](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/Binding.java), [Converter](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/Converter.java) | SQL-facing representation and application-facing representation are distinct; conversions have explicit directions | Advanced-type descriptors and statically registered conversion functions; driver factories invoke them without runtime generic construction |
| [DefaultBindContext.bindValue0](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/DefaultBindContext.java) | Advance the physical bind index, invoke the field binding and retain the underlying driver error identity | Walk C03's already-rendered occurrence sequence; do not rediscover SQL placeholders or merge same-name logical slots |
| [DefaultBinding.InternalBinding.set/get](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/DefaultBinding.java) | Convert to the database representation before choosing typed NULL/set; read a typed value and convert back | Generated/provider-owned Dapper.AOT factories; SQL type/facets survive a NULL value |
| `DefaultIntegerBinding`, `DefaultLongBinding`, `DefaultStringBinding` in that file | Typed JDBC setters/getters and `wasNull` preserve the distinction between a zero value and SQL NULL | Explicit `DbType`/provider type; typed getters and `IsDBNull`, not `Convert.ChangeType` or a primitive default on NULL |
| `DefaultJSONBinding`, `DefaultJSONBBinding`, `DefaultArrayBinding`, `DefaultRecordBinding`, `DefaultResultBinding` | SQL representation and result decoding vary by dialect and nested value family | Advanced/nested tasks own neutral representations; dialects own SQL encoding; providers own actual wire codecs |
| [Records.mapping(FunctionN)](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/Records.java) | Call a known constructor/function with typed values in projection order | Emit direct C# constructor/object-initializer calls inside a mature `RowFactory<T>`; no per-row constructor discovery |
| [Functions.nullOnAllNull / nullOnAnyNull](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/Functions.java) | Null-presence mapping is an explicit policy | Preserve the policy in a nested descriptor; use a non-null key/presence column for nullable outer-join rows when all projected values may legitimately be NULL |
| [DefaultRecordMapper.init](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/DefaultRecordMapper.java) | A concrete ordered set of array, record, value, mutable POJO and constructor strategies | Move applicable type/constructor resolution to compilation; do not port runtime proxy creation, Kotlin reflection or arbitrary non-public construction into the required .NET AOT path |
| [DefaultRecordUnmapper.init](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/DefaultRecordUnmapper.java) | Source values are transferred by the target row's field order and conversion policy | Generate explicit typed getters for known arguments; a runtime dictionary is an alternate declared record model, not the mandatory path |
| [AbstractQuery.execute / cancel](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/AbstractQuery.java) | Prepare, set timeout, bind, execute, translate failures and clean up; cancellation delegates to the statement | Retain the lifecycle obligations while reusing Dapper.AOT/driver execution; do not transplant JDBC listeners or create a second scheduler |
| [AbstractResultQuery.fetchLazy](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/AbstractResultQuery.java), [CursorImpl.close](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/CursorImpl.java) | A lazy cursor keeps the statement/reader alive; cleanup uses `finally` even when a fetch listener throws | Ownership must survive early enumeration exit, conversion failure and cancellation; the underlying mature execution loop remains responsible for reader/command cleanup |
| [Multiset.acceptDefaultJSONEmulation / jsonxArrayaggEmulation](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/Multiset.java) | Arrays of positional rows avoid duplicate-name ambiguity; aggregation preserves bag semantics and coalesces an empty collection | Versioned positional nested encoding and a static decoder; exact ordering/precision/NULL preconditions must be checked before enabling a dialect lowering |

### 2.1 Binding algorithm to inherit

The implementation must follow these operations in this order:

1. Validate profile, occurrence count, logical slot identities, declared SQL types
   and statically reachable codecs before creating a command that can be sent.
2. For each occurrence, read its referenced typed invocation value. A repeated
   logical slot can appear several times; each occurrence still owns its physical
   parameter position. A matching display name is not evidence of shared identity.
3. Apply the declared application-to-database conversion once for that
   occurrence. Preserve the converter's specified NULL behavior; never infer it
   from `default(T)`. Default nullable conversions propagate SQL NULL.
4. Assign direction and type/facets before assigning the value. A converted NULL
   becomes a typed database NULL; it does not erase the type or become zero.
5. Use the selected provider's supported typed parameter path. A custom scalar
   conversion cannot silently become provider reflection or dynamic JSON mapping.
6. On failure, identify the logical slot/physical occurrence without logging its
   value; retain the provider exception/code as the inner failure.

The relevant mature code is reusable even when the public Dapper call interceptor
does not recognize Korda's Fluent method. Runtime execution reuse and interceptor
recognition are separate questions.

### 2.2 Result and nested mapping algorithm to inherit

Resolve a known C# projection at compilation: ordered constructor inputs,
accessible assignments, nullability and statically registered conversions. On a
nonempty reader, validate the actual column layout before constructing the first
row. Fetch each mapped value using its typed getter/codec, apply the reverse
conversion and invoke the selected constructor directly. This is the C# analogue
of `Records.mapping`, not a newly invented runtime POJO mapper.

For an outer-joined nested object, read its declared presence discriminator before
constructing it. All-null data fields are not sufficient to distinguish an absent
child from a present row whose selected fields are nullable. An explicit
`nullOnAllNull` policy is valid only when that ambiguity is intentionally accepted
or excluded by metadata.

For a nested collection, preserve duplicates; do not replace a bag with a set.
An empty correlated collection decodes to an empty collection, not a phantom row
of NULLs. A requested order needs an encoding with a proved ordering guarantee.
JSON numbers are decoded directly into the declared integral/decimal type rather
than passing through `double`; unsupported lossless encodings are diagnostics.
The exact required cases live in `ORM-NESTED` and `ORM-ADVANCED-TYPES`.

### 2.3 Separate SQL checks for the selected nested lowerings

The public jOOQ `JSONArrayAgg.accept0` takes its GROUP_CONCAT emulation for both
MySQL and MariaDB. `ListAgg.accept` can prepend/append statements changing
`group_concat_max_len`. That behavior cannot be copied unchanged into the selected
single-command, pure RenderedTemplate contract. The new ORM-NESTED packet fixes
native alternatives and the integrity check; this is a bounded source adaptation,
not a claim that the exact Java body is reused unmodified.

Separate local server probes (not the Java AOT probe and not product acceptance)
executed the following correlated SQL families on PostgreSQL 18.7, MySQL 8.4.11 and
MariaDB 11.8.10. A parent with three children including a duplicate and a SQL NULL
returned `[[1,"a",null],[1,"a",null],[3,"z",30]]` in that exact order; a second parent
with no children returned `[]`.

| Profile | Exercised ordered collection expression |
| --- | --- |
| PostgreSQL | `jsonb_agg(jsonb_build_array(cells...) ORDER BY id,seq)` with an empty-result coalesce |
| MySQL | `JSON_ARRAYAGG(JSON_ARRAY(cells...)) OVER (ORDER BY id,seq ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)` inside the correlated scalar SELECT, followed by LIMIT 1 and an empty-result coalesce |
| MariaDB | Native `JSON_ARRAYAGG(JSON_ARRAY(cells...) ORDER BY id,seq)` |

MySQL's [aggregate reference](https://dev.mysql.com/doc/refman/8.4/en/aggregate-functions.html)
allows the window form but does not give ordinary JSON_ARRAYAGG a row-order
guarantee. The full window frame is required; its default frame could return a
prefix. This exact window/full-frame/scalar-LIMIT shape passed the real MySQL
server probe. It does not accept arbitrary DISTINCT/grouping/pagination nested
sources; the packet explicitly rejects those initial source forms.

MariaDB's [aggregate reference](https://mariadb.com/docs/server/reference/sql-functions/aggregate-functions/json_arrayagg)
links output length to group_concat_max_len. Setting that session limit to 32 in a
disposable test actually returned truncated JSON and warning 1260. A JSON parser
alone is insufficient as an integrity guarantee because other truncations could
still form a syntactically valid value. The fixed single-statement guard is:

```sql
CASE WHEN COUNT(*) = 0 THEN JSON_ARRAY()
     WHEN SUM(OCTET_LENGTH(R)) + COUNT(*) + 1
          > LEAST(B, @@session.group_concat_max_len)
       THEN JSON_OBJECT('$korda_error', 'nested-budget')
     ELSE JSON_ARRAYAGG(R ORDER BY checked_order)
END
```

R is the actual JSON_ARRAY row expression and B the configured shape byte budget.
For N rows, encoded row lengths plus N-1 commas and two brackets give the byte
bound. The expression uses encoded UTF-8 byte lengths, not character counts, and
has an independent empty-input branch. The packet permits only stable row
expressions when evaluating R more than once and records every resulting parameter
occurrence. The decoder recognizes the reserved root object as KORM-NESTED-005;
a normal collection always has an array root. No implicit session SET is added.

The guard's first native server test used three rows including `猫`: computed
bound and actual complete result were both 46 bytes. Exactly 46 bytes in both
server cap and application budget succeeded; a cap or budget of 45 returned the
error object. Empty input with cap 4/budget 2 returned `[]`. Six boundary/shape
assertions passed. A further seven-value witness used empty text, an
embedded double quote, backslash, newline, NUL, emoji plus a CJK character, and the
text "null". Bound and actual result were both 88 bytes; cap 88 preserved every
value, cap 87 returned the error object. This proves the chosen byte calculation
for those witnesses, not every future server release or the generated DTO decoder. SQL/projection/decoder integration remains a product
gate with exact build pins.

A separate direct call to the same SQLite 3.53.4 native library used by the .NET
probe established two renderer constraints: a scalar subquery returning two rows
took its first ordered row, and `UPDATE u AS x ... RETURNING x.id` failed while
unqualified `RETURNING id` succeeded. SQLite therefore needs a static at-most-one
proof for the common scalar-cardinality contract and an unqualified target-column
RETURNING scope. Those checks are fixed in the SQLite/relational packets; they do
not justify a replacement execution engine.

## 3. Java Native Image support is real, but scoped

The reviewed GraalVM reachability repository is fixed at
[`ecaeaa437656b64914152c7dd80025328efbb013`](https://github.com/oracle/graalvm-reachability-metadata/tree/ecaeaa437656b64914152c7dd80025328efbb013).
Its metadata and test sources are evidence of maintained Java AOT paths, not
evidence that this research ran those suites.

| Candidate | Inspected primary evidence | What is and is not established here |
| --- | --- | --- |
| jOOQ 3.21.10 | [Index](https://github.com/oracle/graalvm-reachability-metadata/blob/ecaeaa437656b64914152c7dd80025328efbb013/metadata/org.jooq/jooq/index.json), [3.20 metadata](https://github.com/oracle/graalvm-reachability-metadata/blob/ecaeaa437656b64914152c7dd80025328efbb013/metadata/org.jooq/jooq/3.20.0/reachability-metadata.json), [test source](https://github.com/oracle/graalvm-reachability-metadata/blob/ecaeaa437656b64914152c7dd80025328efbb013/tests/src/org.jooq/jooq/3.18.2/src/test/java/org_jooq/jooq/JooqTest.java) | Indexed tested versions include 3.21.10; the test-version points to 3.18.2. Dynamic record/type paths need applicable metadata. No complete jOOQ native backend was built in this study |
| PostgreSQL JDBC | [Index](https://github.com/oracle/graalvm-reachability-metadata/blob/ecaeaa437656b64914152c7dd80025328efbb013/metadata/org.postgresql/postgresql/index.json), [42.7.13 metadata](https://github.com/oracle/graalvm-reachability-metadata/blob/ecaeaa437656b64914152c7dd80025328efbb013/metadata/org.postgresql/postgresql/42.7.13/reachability-metadata.json) | Indexed tested versions include 42.7.15; TLS/authentication/XML/custom factories introduce specific reachable classes. No local Java/PostgreSQL round trip is claimed |
| MySQL Connector/J | [Index](https://github.com/oracle/graalvm-reachability-metadata/blob/ecaeaa437656b64914152c7dd80025328efbb013/metadata/com.mysql/mysql-connector-j/index.json), [8.2 metadata](https://github.com/oracle/graalvm-reachability-metadata/blob/ecaeaa437656b64914152c7dd80025328efbb013/metadata/com.mysql/mysql-connector-j/8.2.0/reachability-metadata.json) | Configuration/connection URL and plugin classes are explicitly registered; indexed versions extend through 26.10.0. No local Java/MySQL execution or complete plugin coverage is claimed |
| MariaDB Connector/J | [Index](https://github.com/oracle/graalvm-reachability-metadata/blob/ecaeaa437656b64914152c7dd80025328efbb013/metadata/org.mariadb.jdbc/mariadb-java-client/index.json), [3.5.2 metadata](https://github.com/oracle/graalvm-reachability-metadata/blob/ecaeaa437656b64914152c7dd80025328efbb013/metadata/org.mariadb.jdbc/mariadb-java-client/3.5.2/reachability-metadata.json), [CONJ-1310](https://jira.mariadb.org/browse/CONJ-1310) | A real configuration-reflection failure was fixed with metadata/CI support; indexed versions include 4.0.0. A library-specific past failure is not a general Native Image limitation |
| SQLite JDBC 3.54.1.0 | [Source pin](https://github.com/xerial/sqlite-jdbc/tree/2b39e1f8b315fbe11cdd7271ee929ae8f9638e07), [SqliteJdbcFeature](https://github.com/xerial/sqlite-jdbc/blob/2b39e1f8b315fbe11cdd7271ee929ae8f9638e07/src/main/java9/org/sqlite/nativeimage/SqliteJdbcFeature.java) | Its hosted feature registers actual JNI callbacks and exports/includes the target native library. This exact driver was built and exercised through the C# native consumer below |

GraalVM's [library support list](https://www.graalvm.org/native-image/libraries-and-frameworks/)
distinguishes maintainer and community testing. The
[Micronaut SQL native guide](https://micronaut-projects.github.io/micronaut-sql/latest/guide/index.html)
also documents jOOQ record registration and SimpleFlatMapper integration. Neither
is a blanket guarantee for an arbitrary application model or authentication plugin.

## 4. Actual C# / Java / JDBC native experiment

### 4.1 Pinned inputs

| Input | Actual version / identification |
| --- | --- |
| C# host | Debian 13 Linux x64, .NET SDK 11.0.100, `net11.0`, C# 15; native GCC-linked executable |
| Java compiler/runtime image | GraalVM Community Edition 25.6.5.1+2.1; OpenJDK 25.0.5.1+2-jvmci-25.6-b29 |
| Official Graal archive | `graalvm-community-jdk-25i6-25.0.5.1_linux-x64_bin.tar.gz`; SHA-256 `d792848db26f1602f0a5cf2cd9279d9a652d32ab450d891ce616c9ca67e359d0` |
| SQLite JDBC | 3.54.1.0; release JAR SHA-256 `f8dce420a6016278497f4f0560f65602b9db858de141b541cf91a4644ebe4639` |
| Logging API/provider | SLF4J API and NOP 1.7.36, Maven-published checksums checked |
| Native Image compiler settings | Shared library, optimization level 2, compatibility CPU target, two compiler threads, 3 GiB builder maximum heap; final image maximum heap 128 MiB |

Archives were downloaded from their official release locations and checked before
execution. The Graal [25.6 release notes](https://www.graalvm.org/release-notes/25.6/)
identify this release. These pins are experiment inputs, not a promise that every
subsequent toolchain version behaves identically.

### 4.2 The exercised boundary

The C# caller constructed immutable `Field<T>`/condition/query records. Optional
predicates and `IN` arity changed the runtime AST. Rendering produced SQL plus
ordered parameter occurrences, tagged as signed 64-bit integer, UTF-8 text, or a
typed NULL. This small probe captures values in its query objects; it does not
claim to implement the complete reusable-template/sidecar contract.

The Java shared library exposed C entrypoints using GraalVM's
[C API](https://www.graalvm.org/jdk25.6/reference-manual/native-image/native-code-interoperability/C-API/).
It invoked the unmodified SQLite JDBC driver through `Connection`,
`PreparedStatement`, typed setters and `ResultSet`. The result projection was
fixed to `(long Id, string Name, long? Score)` and constructed a C# `Item` record.
The Java component did not inspect the C# type or generate it at runtime.

| Operation | Ownership and representation used in the actual probe |
| --- | --- |
| Isolate creation | C# calls `graal_create_isolate`; the creating thread gets a thread-context pointer |
| Connection open | Length-delimited UTF-8 path; Java owns the JDBC connection; C# owns an opaque numeric handle |
| Query / execute | Length-delimited SQL; ordered kind/numeric/text-pointer/text-length arrays; pointers are borrowed only during the call |
| Binding | Positive tags mean non-null typed values; negative tags retain the SQL type for `setNull`; prepared statements use positional JDBC indices |
| Pull next row | One C call returns integer fields, NULL flag and UTF-8 length into caller-owned buffers; no Java heap reference escapes |
| Insufficient text buffer | Return a distinct buffer-needed status and required size; retain the current row so retry does not skip it |
| Cursor close | Close `ResultSet`, then `PreparedStatement` in `finally`; release the cursor handle |
| Transaction | Explicit begin, commit, rollback and return-to-autocommit operations on the same connection |
| Error | Catch Java failures at the C entrypoint, return a status and copy a bounded diagnostic; never unwind a Java exception through .NET |
| Worker thread | Attach the actual calling native thread to the isolate, call, detach; the thread-context pointer is not reused on another thread |
| Shutdown | Release cursor/connection handles, assert handle count zero, then tear down the isolate |

The prototype's fixed result row and per-row UTF-8 byte array are deliberate scope
limits. A production generic row transport would need a versioned descriptor and
memory bounds; a batch transport would need independent semantics and performance
validation. Neither is silently assumed to exist.

### 4.3 Observed outcomes

The final .NET publish completed and its **native executable** passed **27
assertions**. The checks included:

- runtime-selected WHERE branches and mixed integer/text parameters;
- repeated bind occurrences, different `IN` lengths and empty `IN`;
- SQL NULL versus equality-to-NULL, nullable result mapping and explicit `IS NULL`;
- UTF-8 text containing both an embedded NUL and a non-ASCII character;
- a JOIN projection and an aggregate mapped into the known result record;
- retrying a too-small result buffer without skipping the pending row;
- pulling one row and disposing the cursor early;
- an explicit transaction rollback and absence of the rolled-back row;
- propagation of a real SQLite SQL error;
- a second managed thread attaching/calling/detaching; and
- cursor/connection cleanup, zero live handles and isolate teardown.

Native Image produced a **16.38 MiB** bridge shared library plus approximately
**1.1 MiB** `libsqlitejdbc.so`; the ELF library's inspected dependencies were libc
and zlib, with the separate JDBC native library loaded by its supported loader.
The initial build completed in 86 seconds at a reported peak RSS of 1.32 GiB;
the final build with explicit native access and heap settings completed in 97
seconds. These are host observations, not portable build-time budgets.

An initial invocation incorrectly supplied a Java main class to the shared-only
build; omitting that main-class operand resolved it. The initial runtime native
access warning was resolved using `--enable-native-access=ALL-UNNAMED`. The final
build retained one upstream deprecation warning from SQLite JDBC's embedded
`--enable-url-protocols` option. There was no fallback to a JVM executable.

A bounded transition probe warmed up 10,000 calls, then took five samples of
200,000 calls to a native entrypoint that returns its integer input plus one.
Observed samples were **22.78–24.32 ns/call**; a single local non-inlined C# control
observed **1.34 ns/call**. The timed native loops allocated zero bytes according
to the **C# thread allocation counter**. That counter does not measure the Java
heap. This experiment isolates a small crossing, not SQL execution, row mapping,
throughput, tail latency or an optimized Java backend's final cost. It is not a
Dapper performance comparison.

### 4.4 Concise reproduction method

Recreate the fixed three-column fixture with rows `(1,"Alice",10)`,
`(2,"Bob",NULL)`, `(3,"A\u0000猫",30)` and `(4,"Dora",40)`. Compile static Java
C entrypoints for the operations above using the pinned SDK and driver. Use
`--shared --enable-native-access=ALL-UNNAMED --parallelism=2 -J-Xmx3g
-R:MaxHeapSize=128m -march=compatibility` and SQLite JDBC's documented
`org.sqlite.lib.exportPath` setting. Include the classes/JARs on the classpath;
this shared-only build has no Java main-class operand.

Publish a separate `net11.0` C# consumer with `PublishAot=true`, unsafe code enabled
for the blittable boundary and `CppCompilerAndLinker=gcc`. Disable CLI telemetry
for these local research builds. Run the resulting ELF with the bridge and JDBC
shared library discoverable through the local native loader path. Assert
`RuntimeFeature.IsDynamicCodeSupported == false`, the listed row sets/resource
outcomes, and zero handles before isolate teardown. Keep all prototype source,
generated headers, build outputs and raw measurements outside the repositories.

### 4.5 What this does not prove

This experiment does not establish Java backend support for all four database
families, TLS/authentication modes, arbitrary result shapes, provider advanced
types, jOOQ's complete execution feature set, asynchronous JDBC I/O or in-flight
cancellation races. `Statement.cancel` ultimately delegates to the driver;
SQLite JDBC's [cancel implementation](https://github.com/xerial/sqlite-jdbc/blob/2b39e1f8b315fbe11cdd7271ee929ae8f9638e07/src/main/java/org/sqlite/jdbc3/JDBC3Statement.java)
calls its native interrupt mechanism, but that race was not exercised here.
The prototype has an exported cancel operation; export alone is not a passed test.

Adding JDBC calls behind a `Task` does not make blocking work asynchronous.
Virtual threads or a reactive Java driver could change that model, but would add
separate scheduling/cancellation/ownership contracts across the C boundary. They
are not needed to explain this direct synchronous experiment and were not tested.

## 5. Other mature combinations considered

| Combination | Specific useful mechanism | Selection implication |
| --- | --- | --- |
| Dapper.AOT runtime + jOOQ semantic port + .NET providers | Mature .NET command/reader loops, explicit factories, jOOQ type/conversion/nested semantics | Reuses complementary implementations without adding a second managed runtime; see the actual .NET candidate experiments |
| jOOQ static `Records.mapping` + JDBC + Graal | Known Java constructors and mature JDBC types/lifecycle | Feasible Java-side mapping; a C# application still needs an explicit transport and C# object construction boundary |
| Jdbi explicit `Argument` / `RowMapper` + JDBC | [Jdbi's documented functional row mapper](https://jdbi.org/releases/3.49.6/#_row_mappers) directly reads the current `ResultSet`; reflection mappers are separable | A useful mature Java execution option; it does not itself remove C# transport/ownership work. Its metadata exists at the fixed reachability snapshot; no Jdbi native application was run here |
| Micronaut SQL + jOOQ/SimpleFlatMapper | Compile-time framework metadata and configured native reflection support | A maintained integration option for a Java application, but importing an application/DI stack solely to map C# results adds unrelated dependencies |
| .NET runtime reuse with narrow jOOQ-derived advanced adapters | Static JSON metadata, explicit provider types, nested row/collection semantics | A gap in one advanced codec need not invalidate the mature execution runtime; add that codec/decoder as a scoped module |

The reasonable stopping rule is a verified mature composition satisfying the
required core, with explicit advanced-module contracts and product acceptance
gates. It is not necessary to implement every equivalent Java framework once
the required .NET composition is demonstrated. Conversely, public API limitations
alone are insufficient grounds to choose a new executor.

## 6. Maintenance, licensing and any future Java backend gate

The inspected jOOQ public implementation is governed by its recorded Apache 2.0
source/NOTICE rules. SQLite JDBC's pinned tree contains Apache 2.0 `LICENSE`, the
BSD-style `LICENSE.zentus` and `NOTICE`; its bundled SQLite/native dependencies
must remain in a distributed package's license inventory. GraalVM CE's downloaded
`LICENSE.txt` describes GPLv2 with the Classpath Exception for the distribution
and additional module licenses. This is identification of the inspected notices,
not a claim that one top-level label exhausts an eventual binary's obligations.

If a Java backend is later selected for a capability unavailable through the
verified .NET route, its separate implementation proposal must fix all of these
before implementation:

1. A versioned C ABI using fixed-width integers, explicit lengths and documented
   status codes; no Java or C# managed pointers may escape.
2. Handle kind/generation validation, single owner, exactly-once release and
   defined behavior for invalid/released handles. The small probe's numeric map
   is not the final lifetime design.
3. Per-isolate heap budgets and a thread attachment policy compatible with
   asynchronous .NET continuations; an attached-thread pointer is thread-affine.
4. A result transport that preserves SQL NULL, precision, order and ownership;
   batch size, memory budget and early-disposal behavior are explicit.
5. Driver-specific cancellation and transaction outcome rules, including commit
   uncertainty and cancellation/close races; no automatic retry by implication.
6. Exact RID/architecture/CPU/native dependency and license closure in an
   independently consumed NuGet package. Developers adding a C# DTO must not be
   forced to rebuild the native backend; demonstrate the generic descriptor path.
7. Same-driver, same-SQL, same-results performance comparisons that isolate
   transport from database and mapping costs. Do not treat the tiny ping
   measurement as acceptance or reintroduce an unmeasured scheduler/batch handoff.

Those are additional obligations of the Java option, not proof that it is
infeasible. This research does not authorize that backend or an ABI product.
