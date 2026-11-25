# Database execution lifetime — DB-DotNet-01

The selected database product uses .NET drivers and removes Korda-owned database ABI/P/Invoke, native Host and wire transport. Existing upper-level ownership, cancellation and error contracts remain. [The migration contract](../database/dotnet-migration.md) maps these obligations to the driver route.

| Concern | Required managed behavior |
| --- | --- |
| Source/session admission | Immutable options, bounded pools/waiters and one active user command per session |
| Reader and result ownership | Bounded results; disposal/early break joins active work before returning connection ownership |
| Cancellation | Pre-admission and in-flight behavior tested separately; unregister/join callbacks before connection reuse |
| Transactions | Confirmed commit, rollback, unknown outcome and cleanup remain distinct; no implicit replay |
| Errors | Stable upper-level categories/context; preserve original and cleanup failures without secret logging |
| Mapping | Generated static models/DTOs, exact result shape/nullability and explicit codecs |

Driver/native-library implementation details remain dependencies, including SQLite's standard engine package. Korda does not provide another raw-handle lifecycle or global foreign runtime. Old interop-only tests may retire only after tracing retained behavior and package dependencies. Historical cross-engine contracts remain immutable research/acceptance records; they do not require carrying removed product code.
