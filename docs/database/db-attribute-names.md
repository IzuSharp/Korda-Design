# Database attribute names — DB-Rename-01

Korda database attributes use the capability prefix `Db`. Packages and namespaces use `Korda.<Domain>`; this change preserves the existing `Korda.Data` namespace. The [machine-readable mapping](db-attribute-names.json) records the complete authorized rename. The [Fluent ORM contract](fluent-orm.md) remains the behavior authority and the product's generated DLL/XML references own exact declarations.

## Upgrade mapping

| Previous declaration | Current declaration | Business-code spelling |
| --- | --- | --- |
| `WeaveTableAttribute` | `DbTableAttribute` | `[DbTable]` |
| `WeaveColumnAttribute` | `DbColumnAttribute` | `[DbColumn]` |
| `WeaveKeyAttribute` | `DbKeyAttribute` | `[DbKey]` |
| `WeaveVersionAttribute` | `DbVersionAttribute` | `[DbVersion]` |
| `WeaveIgnoreAttribute` | `DbIgnoreAttribute` | `[DbIgnore]` |
| `WeaveProjectionAttribute` | `DbProjectionAttribute` | `[DbProjection]` |
| `WeaveConstructorAttribute` | `DbConstructorAttribute` | `[DbConstructor]` |
| `WeaveParameterAttribute` | `DbParameterAttribute` | `[DbParameter]` |
| `WeaveCodecAttribute` | `DbCodecAttribute` | `[DbCodec]` |
| `WeaveUseCodecAttribute` | `DbUseCodecAttribute` | `[DbUseCodec]` |

Replace attribute spellings in entity and DTO source, assembly codec registrations, custom generator integrations and generated-source fixtures. Recompile consumers and regenerate reverse-scaffolded entities. This is a source and binary API break: the old attribute types leave the public API, with no compatibility aliases or type forwarders. Existing compiled consumers that reference the removed declarations must be rebuilt against the matching candidate packages. Namespace, constructor parameters, optional defaults, attribute targets and runtime semantics stay unchanged.

```csharp
using Korda.Data;

[DbTable("orders", DescriptorName = "Orders")]
public sealed record Order(
    [property: DbKey] long Id,
    [property: DbColumn("customer_name")] string Customer,
    [property: DbVersion] long Version);

[DbProjection(DescriptorName = "OrderRows")]
public sealed record OrderRow(long Id, string Customer);
```

This declaration excerpt follows the current product model syntax. Full independently compiled and executed acceptance comes from the [order sample](https://github.com/IzuSharp/Korda/tree/task/DB-Rename-01-linux/samples/api/orm-experience), not from rendering this document.

## Preserved meaning

`[assembly: DbCodec(...)]` registers a compilation-wide reusable conversion. `[DbUseCodec(...)]` selects a conversion for a member. Codec resolution, nullable wrapping and diagnostic rejection remain unchanged. JSON continues using the existing `JsonSerializerContext`/`JsonTypeInfo` source-generated metadata; the rename introduces no reflection fallback.

`[DbConstructor]` selects an immutable DTO constructor; `[DbParameter(nameof(Member))]` maps a parameter. Entity/projection generation, immutable DTO binding and reverse-scaffolded C# must all use the same new names. Existing ambiguity, nullability, duplicate alias and invalid codec cases retain their expected diagnostic IDs and behavior. The Roslyn semantic metadata names change with the declarations.

## Naming and verification

Use the [public API naming standard](../standards/csharp-public-api-and-documentation.md#3-public-surface-and-package-boundaries). Ordinary business types and methods are named for their responsibilities. `[QmlProperty]` and `[AgentTool]` illustrate future capability prefixes only.

Korda must scan both tracked content and filenames, update source and regenerate references, check selected module dependencies, build actual provider candidate packages, inspect their DLL/XML/README contents, and run the existing order workflow through external PackageReference projects against SQLite and PostgreSQL as Linux x64 Native AOT executables. No product pass is implied by this Design PR. The maintainer owns merge and public release.

## Preserved historical hits

The old names in the upgrade table are intentional. The pre-scope `docs/api/*.json` compatibility catalog, accepted contracts, research/experiments, immutable verification snapshots and completed Plan evidence retain their original bytes and source identities. Historical `IzuSharp/NativeWeave-Design` references and product URLs remain recorded provenance; current navigation uses [IzuSharp/Korda-Design](https://github.com/IzuSharp/Korda-Design) as described in the [repository identity policy](../repository-identity.md). `_nativeweave_migration_phases` is a persisted database table, not a public C# name, and is unchanged. The prior DB-API-01 JSON remains its accepted historical contract; this overlay supplies the explicit managed-name exception without rebinding old acceptance hashes.
