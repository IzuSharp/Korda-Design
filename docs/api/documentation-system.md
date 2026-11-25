# Current Korda documentation and evidence system

## Current authority

The [Fluent ORM behavior contract](../database/fluent-orm.md) and [DB-Rename-01 naming contract](../database/db-attribute-names.md) describe the current database API. Korda's [AGENTS.md](https://github.com/IzuSharp/Korda/blob/DB-DotNet-01/AGENTS.md) owns product module registration, dependency-selected checks and direct Native AOT consumer execution. The [API reference index](reference.md) points to compiled product declarations and XML. Narrative documentation explains composition without maintaining a competing signature catalog.

[docs/current-scope.json](../current-scope.json) is the frozen DB-Scope-01 acceptance input, including its original document hashes, Rust mapping and four JIT/AOT cells. It is historical authority for that accepted batch, not the current package list or execution matrix. The completed DB-API-01 JSON likewise retains its accepted identity; DB-Rename-01 supplies the explicit managed attribute rename without rebinding either historical acceptance.

Preserve parameter names/defaults, nullability, constraints, ownership, cancellation, errors, concurrency, capability and cost semantics while replacing the execution layer; the ten Db attribute identities remain unchanged. Regenerate exact API references from compiled source/XML. Keep API compatibility checks, XML/reference tooling, the Core configuration and documentation fixtures used by current modules. Changes to public names must update generator semantic matching, emitted and reverse-generated C#, diagnostics, maintained guides and compilable examples together.

## Evidence labels

Source inspection, static review, compilation, AOT publication and execution of an AOT binary are distinct observations. Record source/toolchain/platform, actual command, exit status and relevant artifacts for each claim. Candidate consumers use ordinary PackageReference outside the source tree. Real data assertions and resolved/loaded dependency identities are observed, not inferred from a package name or successful restore.

Design gates prove structure, naming, links and history preservation. Plan's [DB-DotNet-01 record](https://github.com/IzuSharp/Plan/tree/DB-DotNet-01/ledger/evidence/batches/DB-DotNet-01) and the product PR own actual local checks, the independent SQLite/PostgreSQL candidate AOT lanes and current PR CI. Historical JIT results remain historical evidence; they are not required consumer runs for this task. No accepted old result transfers to changed source.

## Historical authority

The original 0.4.0 API/Server specifications remain archived under `docs/history/pre-db-scope-01/`. Non-Server JSON compatibility catalogs retain their original paths/bytes for pinned historical checks. `docs/contracts/registry.json`, `acceptance-index.json`, accepted reviews, experiments and raw evidence retain their source identities. Interpret their original relative paths at their frozen commit, not against rewritten current guides.

`python3 tools/verify_db_dotnet.py --verify-frozen-history` validates the current .NET overlay and runs the unchanged naming/Fluent/migration/scope checks at frozen inputs. `python3 tools/verify_db_scope_history.py` retains complete historical API/English/contract acceptance and mutation checks at `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. These checks neither certify runtime behavior nor alter old hashes to accept new documents.

## Review and maintenance

Review current names, complete generator/materialization obligations, retained database behavior, package contents, examples and real test results together. Preserve failed attempts and limitations. DB-DotNet-01 authorizes normal merges, observed main CI, automatic preview and actual public NuGet consumption after its required validation. Older task-specific stops apply only to their historical records.
