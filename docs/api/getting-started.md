# Getting started with Korda database mappings

For this migration, use the exact validated candidate or published version of `Korda.Database.Sqlite` or `Korda.Database.PostgreSql`. The Plan receipts own exact package versions and observed release state; do not infer that the .NET migration has shipped. Import `Korda.Data` for mapping attributes, `Korda.Database` for the common facade and the chosen provider namespace.

Each top-level provider includes shared Korda managed assemblies and generator integration, and declares its standard .NET driver dependencies. An ordinary entity or DTO edit rebuilds C# only.

## Define an entity and immutable DTO

```csharp
using Korda.Data;

[DbTable("orders", DescriptorName = "Orders")]
public sealed record Order(
    [property: DbKey] long Id,
    string? Note,
    [property: DbVersion] long Version);

[DbProjection(DescriptorName = "OrderCards")]
public sealed record OrderCard(long Id, string? Note);
```

The explicit table name preserves an existing physical schema. `[DbColumn("store_name")]` supplies an exact column alias, and `[DbIgnore]` excludes a property. A parameterless `[DbTable]` preserves CLR spelling and opts into the documented `Id` convention. Use `[DbConstructor]` and `[DbParameter(nameof(Member))]` for explicit immutable constructor mapping.

Assembly `[DbCodec]` registrations and member `[DbUseCodec]` selections retain their existing roles. JSON policies still use source-generated `JsonTypeInfo`; no dynamic metadata path is introduced. See the [attribute upgrade table](../database/db-attribute-names.md#upgrade-mapping).

## Run the full workflow

The product [getting-started guide](https://github.com/IzuSharp/Korda/blob/DB-DotNet-01/docs/getting-started.md) supplies installation, ordinary DI, explicit schema creation, typed queries and checked writes. Its [order sample](https://github.com/IzuSharp/Korda/tree/DB-DotNet-01/samples/api/orm-experience) runs independently against both providers using the same business source. Source, session, query and stream owners retain their documented disposal and cancellation requirements.

Acceptance restores candidate PackageReference projects outside the source tree, compiles and runs Linux x64 Native AOT executables against real SQLite and PostgreSQL, and compiles reverse-scaffolded entities. A successful restore or publish alone is not an executed read/write result. Plan records actual source/package/dependency/executable identities and observed outcomes; this page does not claim the current candidate has passed.
