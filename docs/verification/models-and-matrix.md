# DB-Scope-01 verification and acceptance matrix

Plan owns actual acceptance. This design defines required evidence without premarking execution. Current rows use fresh pruned source; original accepted research and old test results retain their original identities.

| Gate | Required observation |
| --- | --- |
| Stop/clean | Old PR19/23 closed unmerged, task-owned processes/timers/autopush stopped or access limitation recorded, old directories removed |
| Plan first | Plan commit/push/PR precedes Design edits; Design checkpoint precedes product edits |
| Rust workspace | Retained crates build/test with locked dependencies and native quality checks |
| C# workspace | Retained projects build; formatter/analyzers/API/XML/reference/compatibility and lock checks pass |
| PostgreSQL regressions | Real provider normal/error/cancel/transaction/migration/relations/stream/disposal assertions |
| SQLite regressions | Real provider normal/error/cancel/transaction/migration/relations/stream/disposal assertions |
| PostgreSQL JIT consumer | Out-of-tree PackageReference, typed Fluent/DTO and verified real data |
| PostgreSQL AOT consumer | Actual Native AOT publish and executable run, same correctness assertions |
| SQLite JIT consumer | Out-of-tree PackageReference, typed Fluent/DTO and verified real data |
| SQLite AOT consumer | Actual Native AOT publish and executable run, same correctness assertions |
| Closure | All nuspecs, project.assets, publish directories and actual native mappings exclude removed products |
| Consumer Rust independence | Precompiled assets; zero cargo/rustc/rustup calls; distinguish trap from pristine no-Rust image |
| Independent review | Retained coverage and real dependency pruning reviewed by a distinct executor; findings resolved |
| Completion | Required PR checks, normal merges and exact merged-main CI verified in all three repos |

## Unique database coverage in mixed tests

Preserve pre-admission commit cancellation with rollback/no durable row, actual failed transaction/rollback, same physical PostgreSQL session, early stream admission/release, and source/session/reference retirement. Preserve nullable/composite foreign-key checks, typed idempotent create/replay, ReadCommitted next-statement conflict lookup, pagination/recovery, optimistic changes and outbox atomicity. Keep real PostgreSQL conflict/lock and lost-COMMIT-ack durable-state oracles as direct database tests.

Remove their NativeWeave HTTP/gRPC/MCP coupling. Internal direct business-method validation is sufficient; writing a replacement transport wrapper is outside scope. See [reference verification](reference-application.md).

## Evidence and failure semantics

Each executed row records source/toolchain/platform, exact command, exit status, data assertions and relevant package/native/executable identities. Preserve failed attempts. An unknown transaction outcome is not a successful rollback; pending cleanup is not reclaimed resources. A non-executed provider/runtime row cannot be inferred from another row or historical CI.

No 30-minute workload, performance optimization or superiority result is required or claimed. Linux x64 is the sole target. Current Design structure/link/history checks are distinct from actual product execution and independent review.

## Historical checks

Original 21-contract/API/English acceptance and mutation gates run unchanged at Design `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` through `tools/verify_db_scope_history.py`. Current scope validation checks archived bytes and exact current requirements. Neither updates historical acceptance hashes to pass changed specifications.
