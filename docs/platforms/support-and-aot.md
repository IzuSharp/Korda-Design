# Linux x64 and Native AOT — DB-Scope-01

The only current validation target is **Linux x64**. Toolchain pins are read from the fresh product's `global.json` and `rust-toolchain.toml`; at the inspected baseline these are .NET SDK 11.0.100 and Rust 1.100.0. These are repository pins, not a new release survey. Existing Windows/research evidence retains its original identity and does not establish current candidate support.

## Required execution matrix

| Provider | JIT | Native AOT |
| --- | --- | --- |
| PostgreSQL | Actual external PackageReference query/DTO execution | Actual publish and native executable query/DTO execution |
| SQLite | Actual external PackageReference query/DTO execution | Actual publish and native executable query/DTO execution |

Every row uses the pruned candidate packages, precompiled native assets, real data and a consumer outside the source checkout. Record exact package/native/executable hashes, toolchain/platform, commands, exit statuses and independent data assertions. Source builds and historical probes do not replace external consumer rows.

## Runtime and build prerequisites

Native AOT execution needs no installed .NET runtime. Publishing still needs the .NET SDK and appropriate native linker/system prerequisites. The application consumer needs no Rust toolchain; maintainers compile Rust before packaging. Separate those claims and distinguish a command trap from an actually pristine no-Rust container.

The package's declared Linux ABI/CPU/dependency profile must match the built assets. Keep existing native dependency, exported-symbol, architecture and reproducibility checks. No implicit platform/architecture fallback, host-specific CPU tuning or new platform certification is introduced.

## Closure and lifetime

Inspect resolved NuGet dependencies, output manifests, final publish files and loaded libraries. The selected database assets are `libnw_database_sqlite.so` and/or `libnw_database_postgresql.so`; NativeWeave Server/protocol/proof/demo assets must be absent. Do not remove required OS libraries merely because a package has no managed dependency on them.

Both JIT and AOT preserve type/NULL/parameter semantics, cancellation/error handling, stream/transaction lifetime and actual retirement. AOT compilation alone cannot prove behavior, and bounded close alone cannot prove reclamation. See [the verification matrix](../verification/models-and-matrix.md).
