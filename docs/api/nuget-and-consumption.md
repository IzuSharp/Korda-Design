# Korda database packages and consumption

Install one independently usable top-level provider: `Korda.Database.Sqlite` or `Korda.Database.PostgreSql`. Each package bundles the required managed assemblies, source generator, build integration and its provider-specific precompiled native library. Internal components remain independently buildable and testable; they are not extra packages the application must install.

## Names and native assets

| Provider package | Provider namespace | Native asset |
| --- | --- | --- |
| `Korda.Database.Sqlite` | `Korda.Database.Sqlite` | `libnw_database_sqlite.so` |
| `Korda.Database.PostgreSql` | `Korda.Database.PostgreSql` | `libnw_database_postgresql.so` |

Common public namespaces include `Korda.Data`, `Korda.Database` and `Korda.Query`. All ten database attributes use the `Db` prefix in `Korda.Data`; the [upgrade mapping](../database/db-attribute-names.md) is an explicit source/binary break. Update source and rebuild it with a matching candidate package rather than mixing old declarations with a new generator.

Use the exact version/feed recorded in the candidate manifest. The public preview can retain the preceding attribute names until maintainer publication. This task builds and consumes candidate packages and stops after passing PR checks for review. It does not publish to NuGet.

## Generator inclusion without hidden runtime work

Consumers use ordinary PackageReference outside the source checkout, with no repository imports or ProjectReference. Entity/DTO additions compile as C# and reuse the packaged native bytes. JSON continues using the existing source-generated metadata. The normal Native AOT compiler/linker prerequisites remain necessary; a consumer does not build Korda's native execution engine.

Maintainers build the existing C++20/libpq/sqlite3 implementation and pack the selected modules. Each provider candidate is checked independently: package ID/version/README, actual DLL/XML public API, resolved dependency closure, native assets and executed Linux x64 AOT read/write behavior. SQLite must not load PostgreSQL's native asset or vice versa. The [product packaging guide](https://github.com/IzuSharp/Korda/blob/task/DB-Rename-01-linux/docs/guides/packaging-domain.md) owns the current producer details.

Applications may use ordinary DI, ASP.NET Core or standard C# gRPC to call their own business methods. Database packages add no transport wrapper. Historical twelve-package distributions remain source-bound history, not current installation instructions.
