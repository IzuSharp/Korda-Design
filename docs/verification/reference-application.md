# Direct database reference verification — DB-Scope-01

The former mixed reference service is reduced to internal direct database verification. Its database business logic and unique oracles are preserved; it is not a new public application framework or server package. `src/Reference.TaskService` and `src/Verification.EndToEnd/ApiProbe` may retain their existing internal paths while their NativeWeave Server/HTTP/protocol dependencies are removed.

## Required retained scenarios

| Scenario | Independent oracle |
| --- | --- |
| Idempotent typed create/replay | Persisted operation/item/outbox rows and response identity; mismatch rejection |
| PostgreSQL concurrent claim | Actual lock/conflict and next-statement ReadCommitted lookup, not an in-memory substitute |
| Typed pagination | Deterministic ordering/tie-breaker and expected typed DTO rows |
| Recovery and optimistic CRUD | Durable operation identity, affected-row/version checks and tenant/key predicates |
| Outbox transaction | Atomic business/outbox state and rollback behavior |
| Nullable/composite relationships | Expected native join/key/null behavior |
| Cancel/failure lifecycle | Pre-admission cancellation, failed transaction then rollback and usable clean session |
| Stream/source retirement | Early stop, session admission/release and actual zero outstanding owners |
| Lost COMMIT acknowledgement | Controlled PostgreSQL wire fault and separately observed durable state |

The PostgreSQL wire proxy and independent SQL queries can remain as test infrastructure. Their driver calls the ordinary C# business/query method directly. No HTTP listener, request routing, NativeWeave gRPC/MCP dispatch or compression engine is needed for these assertions.

## Application use

The same transport-independent C# business method may also be called by an application's standard ASP.NET Core endpoint or standard C# gRPC method. Application transport dependencies, serialization and response mapping remain the application's choice. This task creates no HTTP/gRPC wrapper and does not count a transport test as database package independence.

## Current acceptance

Both providers execute direct database regressions and out-of-tree candidate consumers under JIT and Native AOT. The package consumer verifies typed Fluent/DTO data and actual loaded native libraries. Preserve existing transaction/error/cleanup assertions and source identities; old server-era tests remain historical evidence for old commits. [Plan acceptance](https://github.com/IzuSharp/Plan/blob/task/DB-Scope-01-linux/ledger/evidence/batches/DB-Scope-01/acceptance.json) records actual current outcomes.
