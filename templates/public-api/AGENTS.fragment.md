## C# public API and documentation requirements

This repository explicitly adopts the Korda C# Public API Design and Documentation Standard identified by `public-api-standard.json`. Read the pinned standard and local API specifications before changing a public/protected symbol, native ABI, generator output or documented behavior.

- Verify current stable .NET/C# and relevant official public APIs; record exact inspected source and release identities. Do not require Preview features by accident.
- Use `Korda.<Domain>` packages/namespaces and capability-prefixed attributes: declare `DbTableAttribute`, write `[DbTable]`. `[QmlProperty]` and `[AgentTool]` are future naming examples only; keep public names independent of native implementation language.
- Design convenient, natural, strongly typed C# APIs with complete scenarios and exact signatures, defaults, nullability, errors, cancellation, ownership, concurrency and capability semantics.
- Follow the current domain execution decision. DB-DotNet-01 uses .NET database drivers with managed typed query rendering and generated mapping; ordinary entities/DTOs rebuild C# only. Do not introduce a database engine or transport runtime.
- Map every public feature to actual managed/dependency operations and an owning implementation task. Target 0 B extra library-owned managed allocation on steady-state common paths; report total, business-result, attributable library and unresolved driver/runtime/tool bytes with raw counts. Account for copies and bounded retained resources.
- Update XML documentation, generated API Reference, guides, examples and compatibility baselines in the same change. Compile minimal/advanced consumers and run the required real Native AOT tests.
- Record unsupported/deferred capabilities explicitly and distinguish design evidence from implemented/released behavior.
- Obtain independent API, usability, performance-cost and compatibility review. Preserve historical acceptance; bind changed versions to new exact inputs.

The template takes effect only after this repository adopts an exact standard version and installs its validation. It grants no implementation, publishing, permission or merge authorization.
