# ADR-0006 — C++ implementation of the existing database native contracts

Date: 2026-11-21. Status: owner-directed implementation decision for DB-CPP-01; the first product implementation checkpoint is recorded in the migration overlay. Plan owns current product acceptance.

## Authority and fixed inputs

[Plan PR26](https://github.com/IzuSharp/Plan/pull/26), published commit `94ade5e6e7df2113be1a500d8ba33c0f0b8d8f11`, precedes this Design checkpoint. The observed merged main inputs are product `465cd0f90e6af05ec50eb581156240377cf0825b`, Design `8298dc4128b745cf1809bad0c3cf02c45eb7f522`, and Plan `1fe52a8bd792ccdbb4bbea17ba59b0ad0c24349d`. Only the capabilities merged at these inputs form the reference. Unmerged PRs, other conversations and old performance experiments confer no additional acceptance.

This decision supersedes ADR-0003's Rust mandate for the retained database product and ADR-0005's implementation-language choice. It preserves ADR-0005's database-only scope. Database Host remains the execution/ownership layer. Applications select their own HTTP/gRPC host; NativeWeave supplies no transport wrapper. Qt/QML belongs to another project.

## Decision

Implement the project-maintained native database and required shared interop in C++20. Preserve the existing C# public surface and C ABI preferentially: exports, calling conventions, layout/alignment, capability negotiation, status/error categories, source/handle identity, owned buffers and callback retirement. Native exceptions terminate inside the ABI and become the existing bounded error representation. Unknown application tables remain runtime metadata; no user entity, DTO or ordinary query requires native recompilation.

Use a runtime query AST and dialect compiler that ports the existing NativeWeave validation, freeze/clone rules, parameter ordering and SeaQuery 1.0.2 behavior. Use libpq's asynchronous API and row/chunk mode for PostgreSQL. Use sqlite3 prepared statements on serialized connection workers for SQLite. This implementation controls bounded batches, resource admission, transactions and cleanup rather than changing the public query model.

The [migration specification](../database/cpp-migration.md) binds the decision to source files, upstream references, module responsibilities and verification. Its library comparison is finite: KDb demonstrates runtime schema descriptions; sqlpp11/23 primarily model schema in C++ types; Drogon informs the asynchronous provider split; ADBC informs independent batch ownership; WCDB informs SQLite bridging. None is a selected runtime dependency. The selected dependency lock must record the actual libpq, SQLite and TLS versions/hashes and licenses before packaging. A reference-only library is not part of the distributed closure.

## Toolchain

Use upstream LLVM 23.1.5 for the intended common compiler, clang-format and clang-tidy lock. Linux uses clang/clang++; formal macOS builds use the same upstream LLVM with an Apple SDK, while local Apple Clang records its distinct version and build number. Windows uses clang-cl with MSVC ABI, runtime and Windows SDK. All project native sources share C++20. This batch builds and accepts Linux x64 only.

The [DesktopPlatform fixed reference](https://github.com/ArcForges/DesktopPlatform/tree/6e109ef5d01855158c7ae3a63cd42c98db2647f3) informs independently written configuration. Preserve its fixed clang-format hook version without copying AGPL implementation text. NativeWeave uses repository-specific file filters, exports, install paths and shared CMake presets. Release and ASan/UBSan builds have separate trees. CI records actual compiler path/version/triple and rejects GCC fallback; it runs the same configure/build/test presets as local development.

## Compatibility and acceptance

The twelve existing package IDs and provider isolation remain fixed. Core and the two provider libraries retain their public loading identity. Private Rust-coupled build/adaptation code may change. Precompiled candidate packages are sufficient under the inherited publication policy; no new public release flow is authorized.

SQLite files, PostgreSQL state and migration history/checksums remain directly usable. The same versioned C# business source runs in separate old/new processes against equivalent snapshots with the same database versions and options. Existing SQL golden contracts remain gates; other equivalent SQL differences require an example and execution evidence. Independent SQL validates persistence so that identical old/new mistakes cannot count as correctness.

Preserve all already implemented queries, CRUD/relations, bulk writes, optimistic concurrency, transactions/savepoints, migration/catalog operations, streaming/backpressure, cancellation, finite pools and deterministic disposal. PostgreSQL keeps TLS, bounded drain-or-discard after caller cancellation, disconnect handling and unknown commit outcomes. Source review establishes that the old stream stop did not send a cancel-key request; preserve this to avoid newly aborting an enclosing transaction on early reader disposal. A locked libpq-only patch ignores ambient PG defaults while the original thirteen Host refusals remain. Linux links the pinned LLVM libc++/libc++abi archives behind the C ABI. SQLite keeps lock waiting, BUSY/LOCKED distinctions, transaction modes and durability. Full-result buffering cannot simulate a stream. Confirmed old defects are recorded separately without silently changing public behavior or weakening checks.

Acceptance requires both providers with source-tree-external PackageReference JIT and Linux Native AOT consumers, meaningful original regression assertions, sanitizer/resource evidence, export/dependency/load provenance, build/pack in an environment without Rust, and unchanged native hashes after a C# model/DTO change. Remove replaced Rust product code/build/maintenance paths only after their retained behavior is implemented and verified.

## Historical evidence

Current document checks use [the CI registry](../../eng/ci/README.md). Historical acceptance applies to its original revision; it is not replayed for ordinary document edits and does not establish product execution.

DB-API-01, DB-Perf-01, new ORM capabilities, a benchmark campaign, other platform acceptance and public publication are outside this batch. Stop after the authorized migration and acceptance; if a key capability or validation remains missing, report the task as incomplete.
