# DB-DotNet-01 verification and acceptance matrix

The [.NET contract](../database/dotnet-migration.md), retained [Fluent behavior](../database/fluent-orm.md), [Db names](../database/db-attribute-names.md) and product AGENTS govern this batch. All execution states are recorded in Plan; no row below is preaccepted.

| Gate | Required observed evidence |
| --- | --- |
| Published compatibility inputs | Both actual nupkgs, APIs/XML/assets and unchanged external business C# source are hashed |
| Native removal | All owned database C++/ABI/P/Invoke/Host/wire/build/test assets removed after per-test behavior mapping |
| SQL and values | Both-provider parameter order/types, complete row/shape, JSON/decimal/NULL, joins/relations/CRUD and capability errors |
| Generated mappings | All `Db*` attributes and entities/DTOs/scaffolding compile with retained diagnostics and static JSON |
| Data continuity | Old PostgreSQL schema and SQLite file continue reads/writes/migration history with original checksums/identities |
| Cancellation and streams | Real execution-start cancellation, SQLite execute/read/busy behavior, early break and connection/lock cleanup |
| Transactions | Rollback, savepoints, failed-transaction cleanup and lost-COMMIT-ack durable-state oracle; Unknown is preserved |
| Concurrency and bounds | Same-session rejection, source/pool bounds, concurrent read/write, saturation/recovery and safe reuse |
| Impact/API checks | Registered replacement modules; committed diff selects affected consumers; actual packed DLL/XML API comparison |
| PostgreSQL candidate AOT | Own runner, actual package, external PackageReference and real database execution |
| SQLite candidate AOT | Own runner, actual package, standard engine dependency and external real file execution |
| Internal .NET baseline | First compatible packages/dependencies/binaries frozen before optimizing |
| Business comparison | At least 24 cases per route/database, identical outputs/settings and active Dapper.AOT-generated call sites |
| Short optimization | Repeated interleaved baseline/candidate measurements, bounded resources, correct results and honest allocation attribution |
| Four long segments | Final candidates, same dedicated admitted resources, 4 × 1,800 continuous effective seconds, raw ledgers/metrics |
| Review/normal merges | Non-author technical review, resolved findings, successful actual required PR/main checks |
| Preview/public NuGet | Both automatic previews observed; downloaded real versions independently publish/run Native AOT consumers |

Whole-process allocation and Gen 0/1/2 are required. Lists, DTOs and strings needed by the business count as business-result allocation; attributable Korda overhead and unresolved driver/runtime/tool bytes remain separate. Zero claims require raw counts and attribution for one named path. PostgreSQL server resources are separate; SQLite is in-process. Fixed-rate latency includes queueing.

## History integrity

Run `python3 tools/verify_db_dotnet.py`. It checks this overlay, links, negative controls and preservation of prior inputs, then can replay the unchanged naming gate at frozen Design `dcf4cee8ed4d02a606733aec11bbb36a411d05a9` with `--verify-frozen-history`. Existing API/English/contract history gates retain their old commits. Previous verifiers and accepted JSON/hashes are not edited to admit new implementation semantics. Documentation checks do not accept product execution or a performance cell.
