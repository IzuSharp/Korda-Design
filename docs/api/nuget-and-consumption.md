# Korda database packages and consumption

Install one independently usable top-level package: `Korda.Database.PostgreSql` or `Korda.Database.Sqlite`. DB-DotNet-01 preserves these IDs and C# public entry points while replacing the execution implementation. Use the exact candidate or published version recorded in Plan; .NET migration is not accepted merely by this document.

| Provider package | Provider namespace | Selected dependency |
| --- | --- | --- |
| `Korda.Database.PostgreSql` | `Korda.Database.PostgreSql` | Npgsql |
| `Korda.Database.Sqlite` | `Korda.Database.Sqlite` | Microsoft.Data.Sqlite and its standard SQLite engine dependencies |

Common public namespaces remain `Korda.Data`, `Korda.Database` and `Korda.Query`; ten database attributes keep their `Db` names. Bundle internal Korda managed components and generator/build integration so consumers do not install them as extra top-level products. Publish normal driver dependency metadata in the nupkg; the other database provider must not become a dependency. Remove Korda's old database-native libraries, ABI manifests and engine-build targets from current package assets.

## Ordinary C# and Native AOT consumption

Use normal PackageReference outside the source checkout, without repository imports or ProjectReference. The generator supplies static entity/DTO metadata and mapping; JSON keeps explicit source-generated metadata. A consumer entity or DTO edit only rebuilds C#. Native AOT requires the standard .NET native linker/toolchain prerequisites, but no Korda foreign-language engine build.

For every affected package independently, inspect the actual archive ID, version, README, description, DLL/XML APIs, analyzer/generator, build assets and resolved dependency closure. Publish `-c Release -r linux-x64 -p:PublishAot=true`, execute the binary against the real database, and capture loaded dependencies and engine version. Validate old schema/file/migration-history continuity and the frozen same-source consumer. Published-package acceptance repeats this from the actual automatically released NuGet archives.

Npgsql's incompatible dynamic features are not an implicit AOT fallback. SQLite native dependencies must resolve from the driver's supported standard NuGet deployment. Check that stale Korda database-native binaries are absent, rather than continuing the old native-image hash expectation. Plan records exact package/executable/dependency identities, PR/main CI and release URLs.

Applications may use ordinary DI and their own hosting. Database packages install no Korda server/protocol engine. Historical twelve-package distributions and old C++ assets retain historical identity only.
