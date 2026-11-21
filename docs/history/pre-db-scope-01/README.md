# Historical design before DB-Scope-01

The authoritative pre-scope snapshot is [Design c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9](https://github.com/IzuSharp/NativeWeave-Design/tree/c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9). Its acceptance, source pins and actual evidence remain historical facts. DB-Scope-01 does not rewrite their status or claim that their reviews cover changed current design.

The `api/` and `server/` directories here preserve every original byte of the former `docs/api/` and `docs/server/` specifications. Their relative links retain original locations and should be followed in the frozen snapshot; relocation does not rewrite accepted evidence. `docs/current-scope.json` records original/archive paths and hashes and current verification checks them against the frozen Git blobs.

Original contract registry/index, independent review reports, verification records, experiments and raw artifacts elsewhere in this repository also remain unchanged. They describe the original 21 contracts and research/declared API scope, including removed Server/protocol/extension products. They are not current product instructions or current package acceptance.

The complete unchanged historical gates execute in a detached checkout through `python3 tools/verify_db_scope_history.py`. Current requirements and consumer/API documentation are in [the root README](../../../README.md), [ADR-0005](../../decisions/ADR-0005-database-product-scope.md) and [the current API index](../../api/README.md). Current product acceptance belongs to Plan's DB-Scope-01 ledger.
