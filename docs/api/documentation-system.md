# Current Korda documentation and evidence system

## Current authority

The [Fluent ORM behavior contract](../database/fluent-orm.md) and [DB-Rename-01 naming contract](../database/db-attribute-names.md) describe the current database API. Korda's [AGENTS.md](https://github.com/IzuSharp/Korda/blob/task/DB-Rename-01-linux/AGENTS.md) owns product module registration, dependency-selected checks and direct Native AOT consumer execution. The [API reference index](reference.md) points to compiled product declarations and XML. Narrative documentation explains composition without maintaining a competing signature catalog.

[docs/current-scope.json](../current-scope.json) retains the historical DB-Scope-01 decision. Its earlier Rust mapping does not define the current C++ package implementation. DB-API-01 and DB-Rename-01 retain the behavior and explicit managed attribute compatibility decisions. Historical acceptance applies to the original inputs, not edited current bytes.

Preserve parameter names/defaults, nullability, constraints, ownership, cancellation, errors, concurrency, capability and cost semantics while changing the ten attribute identities. Regenerate exact API references from compiled source/XML. Keep API compatibility checks, XML/reference tooling, the Core configuration and documentation fixtures used by current modules. Changes to public names must update generator semantic matching, emitted and reverse-generated C#, diagnostics, maintained guides and compilable examples together.

## Evidence labels

Source inspection, static review, compilation, AOT publication and execution of an AOT binary are distinct observations. Record source/toolchain/platform, actual command, exit status and relevant artifacts for each claim. Candidate consumers use ordinary PackageReference outside the source tree. Real data assertions and loaded native paths/hashes are observed, not inferred from a package name or successful restore.

Design gates validate only their registered current structural rules. Plan's [DB-Rename-01 record](https://github.com/IzuSharp/Plan/tree/task/DB-Rename-01-linux/ledger/evidence/batches/DB-Rename-01) and the product PR own actual local checks, the independent SQLite/PostgreSQL candidate AOT lanes and current PR CI. Historical JIT results remain historical evidence; they are not required consumer runs for this task. No accepted old result transfers to changed source.

## Historical authority and document CI

The [history entry](../history/pre-db-scope-01/README.md) identifies the earlier
scope without storing a duplicate snapshot. The one historical declaration catalog
retains exact signatures and their semantic policies; current installable APIs
remain in the product's generated references. Raw output, input copies and recovery
receipts are not retained here.

[The CI registry](../../eng/ci/README.md) selects current structural checks by diff.
A prose-only change selects none. Schema changes revalidate their current consumers;
CI changes run self-tests. There is no acceptance replay against fixed old commits.

## Review and maintenance

Review current names, complete generator/materialization obligations, retained database behavior, package contents, examples and real test results together. Preserve failed attempts and limitations. Stop after passing PR checks awaiting maintainer review; DB-Rename-01 does not authorize merging or public publication. Older batch merge/release instructions apply only to their historical records.
