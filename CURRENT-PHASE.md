# Current phase — DB-Exec-02 complete database execution path

The owner has resumed complete Linux x64 path reconstruction in the existing
[Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34).
The [selected target](docs/database/query-semantics.md) preserves public Fluent
behavior, Native AOT, C++ execution and independent provider packages while
allowing internal Host, command/parameter, batch and reader replacement.
The cursor pull/scoped-span route is now a published source candidate.
Its [actual execution record](docs/database/cursor-pull-execution.md) binds the
published source `bc6ba1ae0ece02ecc2c0860776605f3c838f3ff8`, all ten exports,
readiness versus final-tail ownership, retained cost inventory and development
Native AOT results. The measured `0f3816c` checkpoint's EOF tail selected the
implemented DB-Exec-03 direct final-close continuation: two additional private
exports and an independent managed close controller. Both providers passed the
development close and full NativeHost AOT gates. New public-package and
performance acceptance remain pending; source review is not delivery acceptance.

The selected provider targets are fresh PostgreSQL Parse+Describe in one pipeline
group/Sync with no Execute at open, and one SQLite statement for description and
binding with no step at open. Cross-execution PG statement/column caching is not
selected because external DDL can change error and transaction semantics.
Parameters should enter execution as one validated typed owner; results should
be written directly to bounded native batches and read through one validated
layout. The native batch borrow now uses one stable owner with generation-scoped
span reads. The first request performs lazy open, complete shape validation and
a second Source/Session/token/channel admission before fetch. Later batches use
ready/take without a generic operation. DB-Exec-03 implements one independent final
close ready/take after actual provider cleanup, with zero generic operations on
the normal stream path. The previous zero-or-one generic close remains the
measured `0f3816c` baseline. A lazy generic fallback must include the new final
notification fence before releasing an uncertain cookie; Source close joins all
detached notifier tails. Application continuations remain asynchronous.

The command representation must independently justify direct compilation versus
NWQC replay, including removal of superseded stages. Full-path public consumers,
fault/lifetime behavior, same-host before measurements, four sequential local
1800-second candidate/Dapper.AOT cells and normal reviewed delivery remain
required. The [Plan gates and recovery](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/execution-refactor/README.md)
own current evidence. Keep existing CI/module routing, with no benchmark CI.

The previous candidate and its stop record below remain historical. The new
authorization permits normal merges once the requested end-to-end work is
verified; it does not turn old results into new-candidate credit.

## Previous candidate phase — DB-Perf-01 query optimization

# Current phase — DB-Perf-01 query optimization

The owner has resumed Linux x64 query optimization in [Korda #37](https://github.com/IzuSharp/Korda/pull/37).
The C# Fluent API and C++20/libpq/sqlite3 execution remain. The current stage is
an implemented candidate with completed phase, short-load, resource and all four local 1800-second observations. C# composes dynamic
Fluent queries into one bounded NWQC command; C++ validates and compiles the
existing operation inventory. `.Prepare()` compiles immutable SQL and parameter
validation metadata before repeated execution. Result batches, cancellation and
ownership remain streaming contracts. Physical statement reuse and optional
fixed-query template generation remain gaps, not delivered features.

The selected private single-root serializer is now implemented with a 4096-byte
stack limit and generic fallback. Dependency, origin capture/sharing and sealing
gate guards preserve the existing protocol and ownership boundary. Local
correctness and ordinary CI have passed. The [final comparison record](https://github.com/IzuSharp/Plan/blob/bfe4aa3f074789dfac046412eff37fe6ba58b0f7/ledger/evidence/batches/DB-Perf-01/query-optimization/final-f0078da7/README.md)
binds actual phase, short mixed-load and resource observations. Ordinary Fluent
still allocates about 25.31% more than recovered, despite lower cumulative
allocation than the earliest baseline. Dapper.AOT and retained-memory gaps remain;
these observations do not isolate the last serializer's causal effect. All four cells are validated and the 16-app/926-file post-run rehash is unchanged. Candidate throughput is 3.5762% of Dapper.AOT on SQLite and 12.4863% on PostgreSQL; performance parity is not claimed. The final full archive remains local-only after upload rejection; Plan publishes selected summaries and verification receipts. Earlier failures remain unexplained. The owner instructed recording results and stopping with PRs only, without merging.

Read the [current decision and implementation order](docs/database/query-semantics.md),
[Fluent contract](docs/database/fluent-orm.md), [generation boundary](docs/generators/query-generation.md)
and [measurement rules](docs/performance/methodology.md). Continue
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34) on
`task/DB-Perf-01-query-optimization`, with product work on `task/DB-Perf-01-linux`.
The active [Plan batch](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/plan.md)
and [handoff](https://github.com/IzuSharp/Plan/blob/task/DB-Perf-01-query-optimization/ledger/evidence/batches/DB-Perf-01/handoff-linux.md)
own exact candidate identities, unresolved gaps and observed test results. The
initial Plan and Design checkpoints are published; new schemes still follow the
Plan-first, Design-before-product order. Local correctness does not establish the
final candidate's performance, a merged PR or a release.

Normal validation retains Korda's committed-diff/module-dependency selection and
existing independent PostgreSQL/SQLite package jobs. Consumers execute directly
as Linux Native AOT binaries. All performance measurements, including the final
candidate and Dapper.AOT 30-minute segments for both databases, run locally on
Linux. There is no benchmark CI or extra benchmark package job in this scope.
Record actual environment versions and measure matched routes on the same local
host; do not require a hosted-runner image build number.

The cancellation and rename-only authority below remain historical. This resumed
task supersedes that stop state, without accepting any historical incomplete
measurement or changing the identity of old results. Existing documentation gates
and their frozen inputs remain unchanged. Design does not claim product delivery.

## Previous phase record — repository identity maintenance

# Current phase — Korda-Design repository identity

The design repository is now [IzuSharp/Korda-Design](https://github.com/IzuSharp/Korda-Design), alongside the [Korda product](https://github.com/IzuSharp/Korda) and [Plan](https://github.com/IzuSharp/Plan). This maintenance change updates repository identity, current navigation and live repository references. It does not change database behavior, source/package names or accepted historical evidence. DB-Perf-01 remains cancelled.

The DB-Rename-01 Design specification was merged at `d23fc89fb7436911b3f5a39995c7edb710a7be0a`. Use the [current API index](docs/api/README.md), [Fluent ORM contract](docs/database/fluent-orm.md) and [attribute naming contract](docs/database/db-attribute-names.md) for current database guidance. The product repository and Plan retain responsibility for product execution and acceptance.

Read [the repository identity policy](docs/repository-identity.md) for the boundary between canonical URLs and preserved historical names. The current documentation gates remain `python3 tools/verify_db_rename.py` and `python3 tools/verify_db_scope_history.py`.

## Earlier task authority (historical)

The following sections retain the original phase narratives and their task-specific authorization. They are historical context for the current design and do not restart completed or cancelled work.

# Completed Design task — DB-Rename-01

Update Korda's ten database attributes to the `Db` names in the [naming contract](docs/database/db-attribute-names.md) and [exact mapping](docs/database/db-attribute-names.json). The [public API standard](docs/standards/csharp-public-api-and-documentation.md#3-public-surface-and-package-boundaries) defines domain names independent of implementation language. Preserve attribute namespaces, signatures, defaults, targets and behavior; keep C++20/libpq/sqlite3 execution and the existing JSON source-generation metadata.

Use `task/DB-Rename-01-linux` and a task-marked worktree. Current documentation and examples use the new names; frozen acceptance inputs, actual repository URLs, historical evidence and persisted database identifiers retain their identities. Run `python3 tools/verify_db_rename.py`, which checks this overlay and the original completed Design gates at the frozen baseline. Korda owns compiled/API/package/real-database Native AOT checks. Design checks do not establish product execution.

Push the reviewed changes and open the companion PR. Stop after its checks pass, awaiting maintainer review. **This task does not authorize merging or public publication.** Earlier merge/release instructions below apply only to their completed historical tasks.

## Earlier task authority (historical)

# Current task — DB-API-01

Korda's owner authorizes C# Fluent ORM experience enhancements on Linux x64. Read [ADR-0007](docs/decisions/ADR-0007-fluent-orm-experience.md), the [behavior contract](docs/database/fluent-orm.md), the [mapping overlay](docs/database/fluent-orm.json) and the [published Plan-first checkpoint](https://github.com/IzuSharp/Plan/blob/21e98f7591b4cf1f7fd5b7d5e791ab0be4271515/ledger/evidence/batches/DB-API-01/plan.md). Korda AGENTS.md governs current module registration, direct Native AOT checks and automatic release selection. Work uses `task/DB-API-01-linux` and `.worktree/DB-API-01-linux/`.

Preserve C++20/libpq/sqlite3 execution, database-only scope, compatible ABI and independent provider packages. Compare existing samples with the order/customer/detail journey and fill actual gaps. New contracts are prospective until Plan records implementation and real execution. Run `python3 tools/verify_fluent_orm.py`; it retains the unchanged completed migration gate at Design `de1f4796dc199250b405ea99f2129d611f17b1f6`. Continue the earlier immutable history checks. Old task exclusions below retain historical meaning and do not block DB-API-01. This batch authorizes normal merges and observing triggered releases, with no new performance campaign, clean-image/CPU-emulation campaign or other platform acceptance.

## Previous task authority (historical)

# Current phase — DB-CPP-01

The current task is the owner's authorized Linux x64 database native migration from Rust to C++. [Plan PR26](https://github.com/IzuSharp/Plan/pull/26), published commit `94ade5e6e7df2113be1a500d8ba33c0f0b8d8f11`, precedes the Design decision and product implementation. [ADR-0006](docs/decisions/ADR-0006-database-cpp-native.md), [the migration specification](docs/database/cpp-migration.md), and [its overlay](docs/database/cpp-migration.json) define the change. The first C++ implementation checkpoint is published in [product PR21](https://github.com/IzuSharp/NativeWeave/pull/21). The overlay records its exact source and dependency lock; Plan owns subsequent corrections and product acceptance.

Merged inputs are product `465cd0f90e6af05ec50eb581156240377cf0825b`, Design `8298dc4128b745cf1809bad0c3cf02c45eb7f522`, and Plan `1fe52a8bd792ccdbb4bbea17ba59b0ad0c24349d`. The original Rust product is a detached reference; C++ must preserve its C# behavior and existing C ABI while removing Rust from normal product build, packaging and execution. C# models, DTOs, Fluent syntax and async/cancellation/disposal remain public contracts. The selected execution paths are libpq and sqlite3 beneath a C++20 runtime query/ownership layer. LLVM Clang 23.1.5 is the intended compiler/format/tidy lock. macOS and Windows toolchain conventions are recorded but not accepted in this batch.

Work uses `task/DB-CPP-01-linux` in the three requested worktrees. [The current handoff](https://github.com/IzuSharp/Plan/blob/task/DB-CPP-01-linux/ledger/evidence/batches/DB-CPP-01/handoff-linux.md) owns progress; the Plan acceptance record and final migration report own observed tests, merges and CI. Stop only after this batch is complete or accurately record a blocking gap. DB-API-01, DB-Perf-01, added ORM capabilities and public publication are outside this authorization.

Run `python3 tools/verify_cpp_migration.py`. It validates this overlay and runs the original DB-Scope-01 checks against their unchanged Design `8298dc4` inputs. The existing scope manifest and accepted historical records remain unchanged. The earlier DB-Scope narrative below is retained as baseline history, including its original source references; it does not describe completed C++ work.

## Accepted baseline — DB-Scope-01

The owner narrowed NativeWeave to a PostgreSQL/SQLite strongly typed Fluent ORM on 2026-11-21. C# owns application logic, static models, DTOs and the Fluent API. Rust SeaQuery and SQLx own query construction, dialects and database execution. Ordinary applications use precompiled native assets with normal PackageReference, JIT and Native AOT.

The owner terminated Perf-01 and authorized this sequence: close its old PRs, clean only old task workspaces, publish the new Plan PR, prune current Design, prune product code, run Linux x64 database and external-consumer regressions, review, merge and verify main CI. [Plan PR24](https://github.com/IzuSharp/Plan/pull/24) is the Plan-first checkpoint. Implementation changes start only after the Design pruning checkpoint is recorded.

The application chooses its server. ASP.NET Core HTTP endpoints and standard C# gRPC methods can call the same C# business query method. Installing database packages must not install NativeWeave Server, gRPC, MCP, compression/proof or demo packages. Database Host remains part of database execution.

Current authority is [the scope manifest](docs/current-scope.json), [ADR-0005](docs/decisions/ADR-0005-database-product-scope.md) and [current API documentation](docs/api/README.md). Plan's `delivery-graph.json.current_execution` and `ledger/evidence/batches/DB-Scope-01/acceptance.json` own execution and acceptance. Design documents do not announce a release or claim tests have run.

## Historical records

The pre-scope Design main is `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`; product main is `ea5fa528035d025bd7a28698ee7c71194432236c`; Plan main is `8afa0311f45ab8a8157fc45c51e95a0b17dd09f2`. Old 21-contract acceptance, reviews, experiments and 34R/32D/48-delivery records remain historical. Their Server/extension scope and research-only authorization do not govern this batch. Exact prior gates run unchanged at their original snapshot; historical source or execution is never relabeled as current acceptance.

The [history entry](docs/history/pre-db-scope-01/README.md) explains archived API/Server specifications and original evidence paths. Performance work, new features, broader platforms and public database publication are outside this batch. Stop after pruning, actual regressions, normal merges and merged-main CI verification.
