# Database build, packaging and release boundary — DB-Scope-01

The current default build/test/package product is the PostgreSQL/SQLite database closure. [The package graph](../api/nuget-and-consumption.md) and [scope manifest](../current-scope.json) replace the older multi-engine release design for this batch.

## Maintainer producer

Start from fresh product main and apply only DB-Scope-01 pruning/regression repairs. Reconcile Cargo workspace/lock, .NET solution/project references/lockfiles, bindings, assets, package inventories, scripts, CI and examples. Build the retained Rust/C# workspace and both native database providers. Database Host is required. Removed Server/protocol/compression/demo code leaves default build, tests and packaging.

Keep formatter, compiler/analyzer, locked dependency, API/XML/reference/compatibility, native ABI/dependency, security and provenance checks for retained scope. A failing retained check is fixed, not skipped. Source/package/version identity is exact; never relabel a Perf-01 binary or measurement as a DB-Scope candidate.

Retain shared tooling only where the actual database chain uses it. `Build.Integration/ApiReference`, `compose_docs.py`, the Core API configuration and documentation fixture checks remain; its generic `build_native.py`, `NativeWeave.Build.targets`, proof profiles and exclusive samples/fixtures retire. Actual database native assets use the explicit provider producer. Remove generic Generators.Model/CSharp/Rust/Metadata and Analyzers products and their obsolete API configurations; keep `Query.Generator`, database binding generation, SDK/compiler diagnostics and database API checks.

`Packaging.Release/release.py`, its MSBuild `BuildTasks`/`buildTransitive` and API checks remain dependencies of real `Packaging.Domain`. Retire the artificial package producer, conformance consumer/native sample and exclusive default CI chain after moving their relevant unique guards to the real database candidates. The retained MSBuild task must still reject invalid/duplicate JSON or schema, nonexact dependency edges, unsupported RID/CPU profiles, malformed ABI/identities, source/output traversal, missing/duplicate native selections, hash drift before compilation/build and native basename collisions. Retain applicable publication/recovery tests on the real database closure.

Pack fresh database candidates from the pruned source. Record clean/dirty producer state accurately, immutable source/tree identities, dependency closure and package/native hashes. Native assets are maintainer outputs selected through normal NuGet RID handling and retained manifest checks. No application target invokes Cargo.

## Independent consumer

Restore ordinary PackageReference from outside the source checkout with its own package cache. Block repository imports/ProjectReference and consumer Rust invocation. Use actual typed Fluent and DTO mapping for PostgreSQL and SQLite, in JIT and Native AOT. Verify data and actual native mappings, and inspect every nuspec/resolved graph/publish file for forbidden products.

Candidate verification is more than a build or package archive. Missing/duplicate assets, dependency overrides, hash/ABI/capability mismatch and unsupported profiles retain explicit failures. Ordinary entity/DTO changes reuse native assets.

## Release boundary

DB-Scope-01 requires candidates and actual consumption; it does not require public database publication. Retire the old HelloWorld automatic publication target. Normal PR merges must not unexpectedly publish new database packages merely because demo automation previously did so. Any retained publication tooling targets only the database closure and preserves identity/signature/provenance/review safeguards.

Historical package versions and release/evidence records are immutable. Actual new release authorization and its registry/readback requirements are separate. This batch ends after tests, independent review, normal protected merges and exact merged-main CI verification.
