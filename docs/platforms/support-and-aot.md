# Linux x64 and Native AOT — current Korda

Linux x64 is the validation target for DB-Rename-01. Read actual toolchain pins from Korda's `global.json` and `native/dependencies.lock.json`, and use the product [native build guide](https://github.com/IzuSharp/Korda/blob/task/DB-Rename-01-linux/docs/guides/cpp-native.md). The maintained engine is C++20/libpq/sqlite3. Prior Windows and Rust research evidence keeps its original identity and does not certify this candidate.

## Required execution matrix

| Actual provider candidate | Required consumer observation |
| --- | --- |
| `Korda.Database.PostgreSql` | External PackageReference, Native AOT publish and direct binary execution against a real PostgreSQL database |
| `Korda.Database.Sqlite` | External PackageReference, Native AOT publish and direct binary execution against a real SQLite database |

Each provider has its own package/consumer runner. Execute the existing order workflow with generated models, immutable DTOs, read/write assertions and compiled reverse-scaffolded entities. After the managed DTO edit, recompile/run and verify native asset hashes remain identical. Record exact source/package/native/executable identities, actual platform/toolchain, commands and exit results. Compilation alone is not an executed database result.

[Korda AGENTS](https://github.com/IzuSharp/Korda/blob/task/DB-Rename-01-linux/AGENTS.md) governs dependency-selected checks and direct AOT consumer execution. Skip JIT consumers for this task. Clean-image and CPU-emulation checks, extra platform certification and performance campaigns require a separate request; none is implied by this rename.

## Runtime and build prerequisites

Native AOT execution requires no installed .NET runtime. Publishing requires the .NET SDK and normal native linker/system prerequisites. Consumers reuse the bundled native assets and do not rebuild the database engine when an entity or DTO changes. Maintainers use the checksum-pinned native toolchain before packaging. An observed command trap is distinct from proof on a clean machine; do not claim a clean-image result without that execution.

The declared Linux ABI/CPU/dependency profile must match actual built assets. Preserve dependency, export, architecture and reproducibility checks selected by the affected modules. No implicit architecture fallback, host-specific CPU tuning or new platform support is introduced.

## Closure and lifetime

Inspect resolved NuGet dependencies, manifests, final publish output and actual loaded libraries. The selected native asset is `libnw_database_sqlite.so` or `libnw_database_postgresql.so`; each provider must retain its own independent dependency closure. Preserve required OS libraries. Consumer models use the current `Db` attributes in `Korda.Data`.

Type/NULL/parameter semantics, cancellation/errors, stream/transaction lifetime and actual retirement remain unchanged. AOT compilation alone proves neither behavior nor resource reclamation. See the [current verification matrix](../verification/models-and-matrix.md).

## Historical scope

The original Rust toolchain mandate and four JIT/AOT consumer cells are preserved in the [DB-Scope-01 platform snapshot](https://github.com/IzuSharp/Korda-Design/blob/8298dc4128b745cf1809bad0c3cf02c45eb7f522/docs/platforms/support-and-aot.md) and frozen `docs/current-scope.json`. They document that accepted batch. DB-API-01's retained behavior and current Korda instructions govern this task, with the DB-Rename-01 name/compatibility change layered explicitly on top. Historical acceptance is not transferred to changed candidate bytes.
