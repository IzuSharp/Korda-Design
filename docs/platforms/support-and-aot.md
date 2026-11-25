# Linux x64 Native AOT — DB-DotNet-01

Linux x64 is this task's validation target. Product `global.json`, resolved package lock and the actual build/runtime receipts own tool versions. The selected execution paths are Npgsql and Microsoft.Data.Sqlite. Old Rust/C++ and other-platform experiments do not certify the new packages.

| Top-level package | Required independent consumer |
| --- | --- |
| `Korda.Database.PostgreSql` | External ordinary PackageReference, Linux x64 Native AOT publish and direct real PostgreSQL read/write execution |
| `Korda.Database.Sqlite` | External ordinary PackageReference, Linux x64 Native AOT publish and direct real SQLite file read/write execution |

Run each affected package in its own runner. Preserve the same frozen business C# source across old/new packages, and test continuation of existing schema/file/migration history. After an entity/DTO edit, rebuild only C# and rerun; capture generated output and resolved/loaded dependencies. Standard .NET AOT linker prerequisites remain; Korda supplies no consumer-built native database engine.

Follow product AGENTS module impact selection. Consumer runs are Native AOT, without JIT consumers or unrequested clean-image/CPU-emulation campaigns. Ordinary PR CI runs selected correctness, short regression and AOT package acceptance. The four continuous performance segments require a separately admitted dedicated environment and do not run in ordinary PR CI.

Design structure and history checks establish no compilation or runtime result. Plan owns command/exit/source/package/binary/data evidence, independent review, normal merges, observed main checks, automatic preview and actual downloaded public-package consumers.
