# Database C++ migration — source decisions and preserved boundaries

Task: DB-CPP-01. Status: design and first product implementation checkpoint recorded; actual product acceptance is owned by Plan. [ADR-0006](../decisions/ADR-0006-database-cpp-native.md) and [the overlay](cpp-migration.json) are current authority. The Rust behavioral reference is product [`465cd0f90e6af05ec50eb581156240377cf0825b`](https://github.com/IzuSharp/NativeWeave/tree/465cd0f90e6af05ec50eb581156240377cf0825b).

## Public entry to native ownership

| Existing contract and C# entry | Fixed Rust implementation to port | C++ responsibility and reusable tests |
| --- | --- | --- |
| Provider builders, sources and sessions: `src/Data.Postgres`, `src/Data.Sqlite`, `src/Data.NativeHost` | `native/database/host`; provider config/session modules | Source identity, lazy pool creation, admission, serialized connection ownership and close/drain; Data.NativeHost, Data.Postgres, Data.Sqlite |
| Fluent/query binding: `src/Query.Fluent`, `src/Query.Native`, `src/Query.Binding` | `native/database/binding`, `native/database/query` | Runtime arena, source/expression ownership, immutable plan/freeze/clone, ordered parameters and dialect rendering; Query.Binding, Query.Native, Query.Fluent |
| Static entity/DTO metadata and codecs: `src/Query.Generator`, `src/Data.Materialization`, `src/Data.Codecs` | `native/database/interfaces`, `native/database/codecs` | Exact canonical JSON, SHA-derived IDs, db-wire/1 descriptors/cells, scalar/NULL validation and source-bound codecs; Data.Codecs, Data.Materialization and cross-language goldens |
| Explicit parameterized SQL | Host SQL/plan/provider execution | Existing lexer/placeholder ordering, admitted parameter shape and prepare/reuse behavior; provider/host/query regressions |
| Relationships, CRUD, batching and concurrency: `src/Orm.Relations` | `native/database/relations` | Same-session mutation/relation plans, affected-row outcomes, bulk progress, optimistic concurrency; Orm.Relations and reference business oracles |
| Transactions/savepoints: `src/Data.Transactions` | `native/database/transactions` and provider transaction modules | Transaction outcome, cleanup outcome and reusable/discarded connection remain distinct; Data.Transactions and lost-COMMIT-ack oracles |
| Migrations/catalog: `src/Data.Migrations` | `native/database/migrations` | Existing migration records/checksums/idempotence, provider lock/history/catalog operations; Data.Migrations and old-data handover |
| Streaming: `src/Data.Streaming` | `native/database/streaming`, Host cursors | Bounded row batches, backpressure, early exit and independent batch release; Data.Streaming and resource oracles |
| Core/interop, errors, async/callbacks | `native/interop`, Host ABI/operation/error/control | Existing function tables, handles, alignment, buffers, completion and retirement; Interop.Abi/Negotiation/Lifetime/Memory/Callbacks/Async/Execution/Errors |
| Precompiled provider packages | `src/Packaging.Domain/model.py`, Linux/release/build tooling | Same package graph/RID/load names, CMake install and dependency/provenance closure; Packaging.Domain/Linux/Release and all four external consumer cells |

The binding authority remains the [fixed signature inventory](https://github.com/IzuSharp/NativeWeave/blob/465cd0f90e6af05ec50eb581156240377cf0825b/native/database/binding/signatures-v1.json), [database C header](https://github.com/IzuSharp/NativeWeave/blob/465cd0f90e6af05ec50eb581156240377cf0825b/native/database/binding/nativeweave_database_binding_v1.h) and [public interop header](https://github.com/IzuSharp/NativeWeave/blob/465cd0f90e6af05ec50eb581156240377cf0825b/native/interop/abi/include/nativeweave_abi_v1.h). The fixed [query execution guide](https://github.com/IzuSharp/NativeWeave/blob/465cd0f90e6af05ec50eb581156240377cf0825b/docs/guides/query-native.md) and [package graph](https://github.com/IzuSharp/NativeWeave/blob/465cd0f90e6af05ec50eb581156240377cf0825b/src/Packaging.Domain/model.py) explain the existing consumer boundary.

## Query semantics and upstream comparison

SeaQuery 1.0.2 and NativeWeave's own compiler/validator are the semantic reference. Inspect the locked upstream query/select, expression, value and backend builder implementations with the NativeWeave arena, clauses, expression, cache and plan modules. Preserve expression ownership and alias resolution, AST clones, frozen parameter descriptors, exact parameter emission order, dialect capability rejection and existing SQL golden strings. Runtime column/table metadata is data admitted by the native library, never a generated C++ business type. Ported code and assertions must keep their source/third-party attribution where applicable.

| Upstream reference | Inspected source/version | Selection |
| --- | --- | --- |
| KDb | [KDbNativeStatementBuilder.h at a5aea3048dcc36072e8283c460371b2ed5ebc540](https://github.com/KDE/kdb/blob/a5aea3048dcc36072e8283c460371b2ed5ebc540/src/KDbNativeStatementBuilder.h): runtime KDbQuerySchema/KDbTableSchema and QVariant parameters; LGPL-2.0-or-later file | Feasibility reference only; avoid adding Qt or a second schema contract |
| sqlpp11 | [8c05983a31272cf9740cb521500c66a032aad678](https://github.com/rbock/sqlpp11/tree/8c05983a31272cf9740cb521500c66a032aad678): typed C++ table/column DSL, dynamic clauses, BSD-2-Clause | Not selected; runtime clause support does not make arbitrary business schemas independent of compiled C++ types |
| sqlpp23 | [27a49397940debbce12688521a52901612ff7d91](https://github.com/rbock/sqlpp23/tree/27a49397940debbce12688521a52901612ff7d91): C++23 typed DSL, BSD-2-Clause | Not selected; preserve C# typing and runtime ABI metadata rather than adding a second business type system |
| Drogon | [v1.9.14 / 3aae769cc405cf5abb9d477675c6430924f02c7c](https://github.com/drogonframework/drogon/tree/3aae769cc405cf5abb9d477675c6430924f02c7c), `orm_lib/src/postgresql_impl/PgConnection.cc`, `sqlite3_impl/Sqlite3Connection.cc`; MIT | Architectural reference only: PG nonblocking I/O and SQLite workers. Its SQLite stmtStep collects all rows in result_, which does not satisfy this stream contract |
| ADBC | [canonical adbc.h at 7c221749b576fbb136e13cc523109b8d6687748d](https://github.com/apache/arrow-adbc/blob/7c221749b576fbb136e13cc523109b8d6687748d/c/include/arrow-adbc/adbc.h), Apache-2.0 and NOTICE.txt | Ownership reference only: stream and returned batches have independent releases; early stream release cancels. Preserve existing db-wire/1 ABI |
| WCDB | [v2.1.16 / df808591b9f9a9ab42156006819c3550d5af13a3](https://github.com/Tencent/wcdb/tree/df808591b9f9a9ab42156006819c3550d5af13a3), Apache-2.0 plus bundled dependency notices | SQLite/cross-language reference only; no encryption/mobile/framework dependency added |

## PostgreSQL execution

Use the mature libpq C API. The [async contract](https://www.postgresql.org/docs/18/libpq-async.html) and [chunk contract](https://www.postgresql.org/docs/18/libpq-single-row-mode.html) require sending a command, immediately enabling single-row or chunked mode, then draining PGresult objects to a final null return. Free each PGresult. A final empty PGRES_TUPLES_OK does not itself complete draining. Bound NativeWeave-owned outstanding batches and stop consumption when the reader applies backpressure. Already-delivered rows may be followed by a fatal error; propagate it.

Source review of the fixed provider (`native/database/postgres/src/stream.rs`) established that reader stop never opened a cancel-key connection: it dropped the SQLx stream and drained through a bounded ping. Preserve that behavior. The C++ path uses prepare/describe for metadata, starts execution on first fetch in single-row mode, and drains to the final null result on stop; it discards after the existing five-second cleanup deadline. Sending PQcancel during ordinary early reader disposal would newly abort an enclosing PostgreSQL transaction, so the available libpq cancellation API is not used for that path. Cancellation and deadlines end caller admission while the native owner retains the drain/retirement obligation. Do not return a still-busy or failed-transaction connection to the pool. Preserve [TLS configuration](https://www.postgresql.org/docs/18/libpq-ssl.html), certificate verification and [connection/transaction status](https://www.postgresql.org/docs/18/libpq-status.html). A connection loss while awaiting COMMIT acknowledgment yields the existing unknown outcome; it never permits automatic replay.

The selected libpq is PostgreSQL 18.0. A small, hash-locked private source patch prevents libpq from inheriting ambient `PG*` defaults, while the Host still rejects the original thirteen forbidden environment overrides. This preserves the fixed SQLx configuration boundary without changing the process environment. The patch and its upstream source/license ship in the dependency inventory.

libpq uses the [PostgreSQL license](https://www.postgresql.org/about/licence/). Record its selected version, source/hash, build flags and actual TLS/shared dependency closure in product packaging evidence. PostgreSQL 18 behavior is the baseline test target; both sides must run the same recorded server version/configuration. Selecting newer documentation is not evidence that a particular library/server binary was tested.

## SQLite execution

Use [sqlite3_prepare/bind/step/reset/finalize](https://sqlite.org/c3ref/stmt.html) on a connection worker with finite admission. Step only far enough to fulfill bounded batches. Copy or own values until the batch is released; SQLite column pointers cannot outlive the statement step/reset lifetime. Early exit finalizes or safely resets the statement and resolves its transaction/connection obligations.

Preserve [transaction modes and savepoints](https://sqlite.org/lang_transaction.html), lock conflicts and [busy timeouts](https://sqlite.org/c3ref/busy_timeout.html). [sqlite3_interrupt](https://sqlite.org/c3ref/interrupt.html) is cross-thread callable but must not race connection destruction. An interrupted DML operation in an explicit transaction may roll it back; [sqlite3_get_autocommit](https://sqlite.org/c3ref/get_autocommit.html) determines actual transaction state after errors. Do not collapse BUSY, LOCKED, interruption and successful rollback into one generic outcome.

SQLite 3.51.3 is selected: its amalgamation C/header bytes match the baseline bundled libsqlite3-sys 0.37.0 files. Preserve the baseline compile options, including foreign keys, metadata, FTS, URI, thread safety and unlock notification.

The shipped SQLite source is [public domain](https://sqlite.org/copyright.html). Lock the actual version and compile options and record provenance; use the same database version/options for reference and candidate comparisons. A library-language change must not quietly change persistence, journal or durability settings.

## C++ build and developer checks

Use LLVM 23.1.5 / clang-format 23.1.5 / clang-tidy 23.1.5 and C++20. [The official LLVM release](https://github.com/llvm/llvm-project/releases/tag/llvmorg-23.1.5) supplies Linux X64 tar.zst SHA-256 `c3107384835f788768f614db610e87fba7077f125ca950eb02a78bab0a308065` and tar.xz SHA-256 `f72edb0b36580ece7f52e23858f00c18fad4e87395ea7ad05d7e55c39f8fc78a`. The fixed pre-commit mirror is [`ce4bd7270237e95464b37d808b942f02785192c4`](https://github.com/pre-commit/mirrors-clang-format/commit/ce4bd7270237e95464b37d808b942f02785192c4).

Independently implement `.clang-format`, `.clang-tidy`, `.pre-commit-config.yaml`, incremental `.gitattributes`/`.gitignore` rules and shared CMake presets using [DesktopPlatform 6e109ef](https://github.com/ArcForges/DesktopPlatform/tree/6e109ef5d01855158c7ae3a63cd42c98db2647f3) as the requested reference. Its AGPL-marked implementation files are not copied. Filter only maintained native source/header/test paths; preserve tracked database/native binary attributes. Exclude third-party/generated sources from style checks and ignore local build/cache/user-preset state.

The product implementation defines presets `linux-x64-release` and `linux-x64-asan-ubsan`, both derived from a Ninja/C++20/compile-commands base with separate build/install locations. Source-bound receipts must record the exact product identity that supplies these presets:

```bash
pre-commit install
pre-commit run clang-format --all-files
cmake --preset linux-x64-release
cmake --build --preset linux-x64-release
ctest --preset linux-x64-release
cmake --preset linux-x64-asan-ubsan
cmake --build --preset linux-x64-asan-ubsan
ctest --preset linux-x64-asan-ubsan
```

Linux statically links the exact LLVM libc++/libc++abi runtime archives behind the C ABI, avoiding a new dynamic libstdc++ version requirement for NuGet consumers. Their Apache-2.0 WITH LLVM-exception notices accompany the packages. nlohmann/json 3.12.0 supplies checked JSON parsing; SeaQuery's MIT notice covers adapted query algorithms. OpenSSL 3 and zlib remain declared platform dynamic dependencies.

CI must execute these corresponding preset stages, record the actual compiler real path/version/target triple, reject GCC fallback, run format/tidy and assemble candidates from the Release install tree. Linux uses LLVM clang/clang++; macOS formal builds use the same upstream LLVM plus Apple SDK, with local Apple Clang separately identified; Windows uses LLVM clang-cl with MSVC ABI/runtime and Windows SDK. Only Linux x64 is verified here. Consumer PackageReference projects need none of these native maintenance tools.

## Compatibility proof and honest status

Keep one versioned C# consumer and run it unchanged against fixed old/new packages in separate processes and database copies. Compare schema/value/NULL/precision/date/text/binary behavior; Fluent and explicit SQL, joins/groups/CTEs/windows/sets/pagination/prepared execution; parameter order and capability refusals. Keep SQL goldens. Validate changes through independent SQL as well as old/new equality.

Create persistent databases with the old product, then read/write/migrate them with the candidate; preserve migration history/checksums and idempotence. Cover pool admission, concurrent operations/disposal, cancellation/timeout, SQLite conflicts, PostgreSQL disconnect/unknown commit, bounded large results, partial reads and deterministic shutdown. Do not replace streams with full-result buffering or weaken resource bounds.

Pack and build the candidate in a clean Linux environment without Rust. Run SQLite JIT/AOT and PostgreSQL JIT/AOT outside the source tree with ordinary PackageReference; inspect package IDs/dependency closure, exports, actual loaded libraries and separate old/new hashes. Change a C# model/DTO and verify that the native hash remains fixed. The existing public API and native binding checks remain gates.

The [Plan batch](https://github.com/IzuSharp/Plan/tree/task/DB-CPP-01-linux/ledger/evidence/batches/DB-CPP-01) records completed commands, outputs, reviews and CI. This document is a decision and acceptance specification. The [overlay](cpp-migration.json) binds the first published product checkpoint to its exact commit/tree and dependency-lock hash. That checkpoint is not a final acceptance claim: Plan retains actual failures, subsequent corrections, source-bound results and merges. A Design document check does not certify product execution or publication. Known old defects require separate evidence; missing capabilities or unverified cells remain incomplete.
