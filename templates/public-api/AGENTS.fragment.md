## C# public API and documentation requirements

This repository explicitly adopts the Korda C# Public API Design and Documentation Standard identified by `public-api-standard.json`. Read the pinned standard and local API specifications before changing a public/protected symbol, native ABI, generator output or documented behavior.

- Verify current stable .NET/C# and relevant official public APIs; record exact inspected source and release identities. Do not require Preview features by accident.
- Use `Korda.<Domain>` packages/namespaces and capability-prefixed attributes: declare `DbTableAttribute`, write `[DbTable]`. `[QmlProperty]` and `[AgentTool]` are future naming examples only; keep public names independent of native implementation language.
- Design convenient, natural, strongly typed C# APIs with complete scenarios and exact signatures, defaults, nullability, errors, cancellation, ownership, concurrency and capability semantics.
- Keep domain algorithms and execution in the native engines. Do not duplicate a managed SQL/network engine or require rebuilding the native engine for ordinary entities, DTOs or handlers.
- Map every public feature to managed/native operations and an owning implementation task. Account for allocations, copies, pins, FFI crossings and runtime instances.
- Update XML documentation, generated API Reference, guides, examples and compatibility baselines in the same change. Compile minimal/advanced consumers and run the required real Native AOT tests.
- Record unsupported/deferred capabilities explicitly and distinguish design evidence from implemented/released behavior.
- Obtain independent API, usability, performance-cost and compatibility review. Preserve historical acceptance; bind changed versions to new exact inputs.

The template takes effect only after this repository adopts an exact standard version and installs its validation. It grants no implementation, publishing, permission or merge authorization.
