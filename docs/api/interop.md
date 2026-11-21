# Required database interop — DB-Scope-01

Core and interop remain because the database consumes them. The public database path does not expose ABI pointers, raw handles or callback registration. Exact source/reference ownership is in [the reference index](reference.md) and [product mapping](../database/current-product.md).

| Mechanism | Database obligation |
| --- | --- |
| ABI/negotiation | Validate package/module identity, layout, versions and capabilities before publishing owners |
| Lifetime/memory | Preserve allocator pairing, owner/lease relationships, checked bounds and exact retirement |
| Async/callback | Support completion-before-start-return, cancellation races, revoke/drain and safe continuation delivery |
| Errors | Return structured ordinary failures, contain only recoverable unwind cases, reject poisoned state |
| Execution | Retain the database engine-local scheduler/admission requirements; Core has no default global runtime |
| Static generation | Preserve existing deterministic bindings and model/DTO tooling; no consumer Cargo or runtime code generation |

The two database asset basenames are `libnw_database_sqlite.so` and `libnw_database_postgresql.so` on Linux x64. Their descriptors and packaged assets bind hashes and ABI/capabilities. Libraries remain loaded for the documented process lifetime; disposing a source does not imply hot unload.

Cancellation, public completion, native quiescence, connection protocol recovery and confirmed durable effect are separate. No timeout authorizes freeing still-reachable native data or callbacks. Keep the existing Core regression suites required by database dependencies, including negative layout/ownership/cancel/error cases.

Server callbacks, protocol dispatch and proof-engine examples are outside current scope. The old cross-engine contracts and exact review records remain in [history](../history/pre-db-scope-01/README.md); they do not require retaining removed product runtimes.
