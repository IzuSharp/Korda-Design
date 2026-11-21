# Database NuGet and consumption — DB-Scope-01

This specification describes candidates produced from pruned source. It does not announce published database packages. A provider facade is an ordinary PackageReference; it includes the retained common closure and its maintainer-precompiled native asset. Application builds never invoke Cargo, rustc or rustup.

## Candidate package graph

Owned dependencies below are the inspected distribution graph in `src/Packaging.Domain/model.py`, reduced from its previous seventeen IDs by removing five Server/protocol IDs. Version closure and asset/provenance checks remain required.

| Package | Required owned dependencies |
| --- | --- |
| `NativeWeave.Interop.Abi` | None |
| `NativeWeave.Core` | Interop.Abi |
| `NativeWeave.Data` | None |
| `NativeWeave.Database.Transactions` | Data |
| `NativeWeave.Data.Streaming` | Data |
| `NativeWeave.Query.Binding` | Data, Interop.Abi |
| `NativeWeave.Query.Generator` | None; build-time tools only |
| `NativeWeave.Database` | Core, Data, Database.Transactions, Data.Streaming, Query.Binding |
| `NativeWeave.Database.Sqlite` | Core, Data, Database, Query.Generator, Database.Sqlite.Native |
| `NativeWeave.Database.PostgreSql` | Core, Data, Database, Query.Generator, Database.PostgreSql.Native |
| `NativeWeave.Database.Sqlite.Native` | None; SQLite native asset |
| `NativeWeave.Database.PostgreSql.Native` | None; PostgreSQL native asset |

Names in dependency cells carry the `NativeWeave.` prefix. The two native leaves contain `libnw_database_sqlite.so` and `libnw_database_postgresql.so`. Native asset metadata uses the normal `runtimes/linux-x64/native/` mechanism and retained output manifest validation. One provider must not pull the other provider's native package. Neither provider pulls NativeWeave Server, gRPC, MCP, proof/compression or HelloWorld.

The existing `NativeWeave.Database.DependencyInjection` project is retained as optional DI, with an existing Database reference and ordinary container-owned source lifetime. It is separate from the twelve-package B24 distribution closure; do not imply it was packaged or publicly released unless evidence says so. Installing either provider requires no Generic Host or DI container.

## Ordinary application behavior

Use the provider's `SqliteDataSource.Create` or `PostgreSqlDataSource.Create`, or the common `DataSourceBuilder` with provider extension methods. Open sessions explicitly and call typed Fluent/CRUD/migration APIs. Source/session/query/transaction/stream ownership stays unchanged. Ordinary entities and DTOs use existing static metadata/generation and the same native asset bytes.

A console application and an application with ASP.NET Core or standard C# gRPC can share one business query method. HTTP/gRPC packages are chosen by that application and are not dependencies of database NuGets. NativeWeave introduces no transport registration or wrapper.

## Build, publish and closure evidence

Maintainers compile Rust from the pruned source, build managed assemblies and pack fresh candidate versions with exact source, package and native hashes. Consumers restore the local candidate feed from outside the source tree with a separate cache and no ProjectReference/repository import. JIT build/run and Native AOT publish/executable execution are separate required observations.

Native AOT publication needs its normal native linker prerequisites; absence of a consumer Rust toolchain is a different requirement. Trap Rust tool invocation and record zero calls, and use an actual no-Rust container where available. Do not relabel a trap as a pristine machine.

Inspect every candidate nuspec, resolved `project.assets.json`, final publish directory and actual mapped native libraries. Fail on removed NativeWeave Server/protocol/proof/demo packages or assets, missing/duplicate provider assets, stale hashes or incompatible closure. Keep dependency/security/format/API/ABI/provenance gates; do not pass by suppressing failures. See [verification](../verification/models-and-matrix.md).

## Publication boundary

This batch requires candidate packages and actual consumption. The old HelloWorld automatic publication product is retired. Do not start a public database release on merge without a separate authorized release decision and its required identity/signature/registry checks. Existing historical versions and release records remain immutable.
