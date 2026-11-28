# Design history before DB-Scope-01

The pre-scope design is recorded at
[commit c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9](https://github.com/IzuSharp/Korda-Design/tree/c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9).
It included Rust engine and Server/protocol proposals that were later narrowed by
[ADR-0005](../../decisions/ADR-0005-database-product-scope.md) and replaced for
database execution by [ADR-0006](../../decisions/ADR-0006-database-cpp-native.md).

The copied API/Server snapshot has been removed from the current tree. Useful
contract identities, decisions and research conclusions remain in their authored
documents and [the contract registry](../../contracts/registry.json). The single
historical declaration catalog in `docs/api/public-api.json` retains signatures
and their semantic policies; it does not describe the current installable API.
Historical acceptance applies to its original inputs, not edited current bytes.

Current guidance starts at [the API index](../../api/README.md). Normal CI checks
current structured content and never replays the historical snapshot.
