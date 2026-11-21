# Current documentation and evidence system — DB-Scope-01

## Current authority

[The scope manifest](../current-scope.json) lists active documents, provider/package mappings and required verification cells. [The API reference index](reference.md) points to actual compiled product references and XML. Narrative documentation explains composition without maintaining a second, conflicting signature catalog.

Product API changes retain exact namespace/type/member signatures, parameter names/defaults, nullability, constraints, ownership, cancellation, errors, concurrency, capability and cost semantics. Existing generated/API compatibility checks remain. This batch removes out-of-scope APIs and preserves the database surface; it introduces no new public feature.

Keep the actual `Build.Integration/ApiReference` and `compose_docs.py` tools, Core API configuration, documentation fixture data/project and `tests/Build.Integration/verify_docs.py`. Remove API configurations for the retired generic generators/Metadata/Analyzers products. Their absence does not remove the database `Query.Generator` diagnostics or SDK/compiler analysis. Generic native-build proof tooling is not required to generate database API references.

## Evidence labels

Source inspection, static review, compilation, JIT execution, AOT publication and AOT executable execution are different states. Record source/toolchain/platform/command/exit status and artifact identities for each claimed execution. Candidate package verification must use ordinary PackageReference outside the source tree. Runtime data and native mappings are observed, not inferred from package names.

Current Design checks prove structure, source mapping and history preservation only. Plan's DB-Scope-01 acceptance owns actual product regressions, four provider/runtime consumer results, package/load closure, independent review, protected merges and main CI. No old accepted research status or old successful test is transferred to new source.

## Historical authority

The original 0.4.0 API/Server specifications are archived under `docs/history/pre-db-scope-01/` byte-for-byte. Non-Server JSON compatibility inputs also remain byte-for-byte at their original paths for retained database API/binding checks. Their authority is historical; source-pinned test runs use the frozen complete checkout when they also require old narrative hashes. Original `docs/contracts/registry.json`, `acceptance-index.json`, reviews, experiments and raw evidence remain unchanged as historical records. Their original relative paths are interpreted at frozen commit `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`, not against replacement current pages.

Run `tools/verify_db_scope_history.py` to execute the unchanged complete historical API/English/contract gates and mutation checks at that frozen snapshot. Current CI runs database-scope checks instead of compiling obsolete Server declaration fixtures. This is explicit scope retirement, not suppression of a retained failing requirement.

## Review and maintenance

Independent review checks that all implemented database capabilities survive, Database Host is retained, removed components leave default chains, and active documentation agrees with actual package/source dependencies. Findings require source evidence and a corrected recheck. Keep failure logs, never impersonate a separate GitHub reviewer, and stop after the authorized current task is accepted.
