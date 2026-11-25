# Korda-Design

Design specifications, public API guidance and preserved research for [Korda](https://github.com/IzuSharp/Korda). The canonical repository is [IzuSharp/Korda-Design](https://github.com/IzuSharp/Korda-Design), renamed from `IzuSharp/NativeWeave-Design`.

Korda is a strongly typed C# Fluent ORM for PostgreSQL and SQLite, with ordinary PackageReference consumption and Native AOT support. Its current native implementation uses C++20, libpq and sqlite3. This repository records design and compatibility obligations; the [product repository](https://github.com/IzuSharp/Korda) and [Plan](https://github.com/IzuSharp/Plan) own implementation, execution evidence and acceptance.

## Start here

| Read | Purpose |
| --- | --- |
| [Current phase](CURRENT-PHASE.md) and [working rules](AGENTS.md) | Current query optimization scope and earlier task authority |
| [Current API index](docs/api/README.md) and [compiled reference index](docs/api/reference.md) | Current Korda database surface and source-backed declarations |
| [Database product](docs/database/current-product.md) and [Fluent ORM contract](docs/database/fluent-orm.md) | Retained database behavior and implementation boundaries |
| [Query semantics and optimization](docs/database/query-semantics.md) | Current C++ decision, fixed and dynamic query paths, and implementation priorities |
| [Database attribute names](docs/database/db-attribute-names.md) | The ten `Db` attribute names and their compatibility boundary |
| [Getting started](docs/api/getting-started.md), [guides](docs/api/guides.md) and [NuGet consumption](docs/api/nuget-and-consumption.md) | Models, examples and independent provider packages |
| [C# public API standard](docs/standards/csharp-public-api-and-documentation.md) | Naming, documentation and compatibility requirements |
| [Verification matrix](docs/verification/models-and-matrix.md) | Design gates and the separate product execution requirements |
| [Repository identity](docs/repository-identity.md) | Canonical URLs and intentionally preserved historical names |

The DB-Rename-01 Design specification is merged. Its naming overlay builds on the DB-API-01 Fluent ORM contract and [ADR-0006's C++ migration decision](docs/decisions/ADR-0006-database-cpp-native.md). Product results remain recorded in Plan. The owner has resumed DB-Perf-01 query optimization in [Korda #37](https://github.com/IzuSharp/Korda/pull/37), [Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and [Plan #34](https://github.com/IzuSharp/Plan/pull/34). The current stage is an implementation candidate with local correctness evidence, preserving C++ execution and the Fluent API. Physical statement caching and generated fixed-query templates remain gaps; final local Linux performance, merge and release are not claimed. The preceding repository-identity maintenance did not itself resume the task.

## Local documentation checks

```bash
git clone https://github.com/IzuSharp/Korda-Design.git
cd Korda-Design
python3 tools/verify_db_rename.py
python3 tools/verify_db_scope_history.py
```

Use a clone with full Git history. The first command checks current attribute guidance, local links and the unchanged completed Design gates at their frozen commits. The second replays the original API, English translation, 21-contract acceptance and mutation checks at their original inputs. These are also the current main and pull-request CI gates. Documentation checks do not establish database or Native AOT execution.

## Historical records

The [pre-scope history entry](docs/history/pre-db-scope-01/README.md) preserves the original API and Server specifications. Accepted contract registries, review manifests, research snapshots, experiments and raw verification outputs retain their recorded names, commits and hashes. The frozen `docs/current-scope.json` describes DB-Scope-01 and its original document hashes; current behavior is described by the later contracts linked above.

Historical `NativeWeave` product names, `NativeWeave-Design:` evidence keys and legacy replay directories remain where their exact identity matters. Current navigation uses Korda-Design. See the [repository identity policy](docs/repository-identity.md) before changing a remaining old-name reference.
