# Korda.Orm: source-translated C# SQL framework

Status: proposed architecture for `Korda-Orm-01`, pending user review. Product
implementation is not authorized by this study. The existing Korda product and
its historical acceptance records remain separate.

**A Native AOT-first, type-safe SQL framework for C#.** The core asset is a native
C# expression of jOOQ's mature SQL language and semantics. A driver-free query
model and renderer export SQL, typed binding layout and result metadata to an
independent execution layer that reuses Dapper.AOT Runtime and mature .NET drivers.
The reopened0.2 selection supersedes the earlier own Binder/Projector default.

| Document | Authority and purpose |
| --- | --- |
| [Architecture](architecture.md) | Module dependencies, package proposal, decisions and migration boundary |
| [Shared contracts](contracts.md) | Versioned semantic interfaces for parallel implementation |
| [Implementation specification](implementation-spec.md) | Fixed declarations, algorithms, lifecycle, diagnostics and shared fixtures |
| [Fixed language surface](language-surface.md) | Complete finite Fluent overloads, relational/mutation policies, exact node payloads and conversion lineage |
| [Mature execution reuse](mature-execution.md) | Original/runtime AOT paths, four databases, faults and performance evidence |
| [Generator integration](generation-integration.md) | Normal SG, portable host, static registration and build alternatives |
| [Java/jOOQ execution options](java-execution-options.md) | Execution-source translation, actual Graal/JDBC native route and tradeoffs |
| [Language model](language-model.md) | Pinned jOOQ core/type/NULL/ownership source mapping and inherited semantic rules |
| [Dialects and generation](dialects-and-generation.md) | Rendering, SQL families, capabilities, schema/codegen, parser and source gaps |
| [Execution and AOT](execution-aot.md) | Dapper.AOT/driver sources, binding, mapping, lifecycle and toolchain decisions |
| [Upstream policy](upstream-policy.md) | OSS/commercial boundaries, attribution and sustainable source updates |
| [Validation](validation.md) | Actual bounded experiments, limitations and future acceptance method |

The [Plan task branch](https://github.com/IzuSharp/Plan/tree/task/Korda-Orm-01-linux)
owns the independent implementation graph, task packets, progress and the single
[Linux handoff](https://github.com/IzuSharp/Plan/blob/task/Korda-Orm-01-linux/ledger/evidence/batches/Korda-Orm-01/handoff-linux.md).
Its graph pins an immutable Design revision before implementation starts; links
to a moving branch here are navigation, not acceptance pins.

No existing R/D/A/B task, native ABI, C++ execution path or historical Rust mandate
is an implementation prerequisite. Existing engineering conventions for naming,
API compatibility, package consumption and diff-based CI remain useful where
they fit this managed architecture. The task-specific contracts below take
precedence over incompatible historical architecture requirements.
