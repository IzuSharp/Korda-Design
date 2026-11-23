# ADR-0007 — Fluent ORM business experience

Status: owner-authorized DB-API-01 design; implementation and execution evidence remain pending.

## Inputs and authority

The owner authorizes enhancement of Korda's existing database ORM on Linux x64, normal repository checks and merges, and verification of resulting releases. The [published Plan-first checkpoint](https://github.com/IzuSharp/Plan/blob/21e98f7591b4cf1f7fd5b7d5e791ab0be4271515/ledger/evidence/batches/DB-API-01/plan.md) precedes this decision. Baselines are Korda `7275396176b928c8879d59f4bf20ad8fa7ffb62c`, Design `de1f4796dc199250b405ea99f2129d611f17b1f6` and Plan `5be447a868be78713ada52f46cee16409f0edc13`. No historical pass transfers to changed source.

The current Korda AGENTS.md owns module registration, diff-based CI selection, Native AOT consumer execution, independent package runners and publication. This supersedes only the prior task's exclusion of DB-API-01 and its task-specific consumer/release requirements. The database-only scope and C++20/libpq/sqlite3 decision remain. Historical contracts and recorded checks retain their exact bytes.

## Decision

Use ordinary C# class/record entities and immutable DTOs, source-generated static mapping and a small strong-typed Fluent surface. First compare the current query and relation samples with a complete order/customer/detail business journey; reuse existing filtering, joins, aggregation, CRUD, concurrency, migration apply and transaction semantics. Add conveniences only for demonstrated gaps. The [contract](../database/fluent-orm.md) and [machine-readable mappings](../database/fluent-orm.json) identify the new boundaries and required evidence.

The C++ kernel remains responsible for query and dialect semantics and provider execution. Managed code may validate arguments, compose native expressions, encode values, materialize DTOs, coordinate an awaited business callback and emit C# scaffold source. No full LINQ provider, managed SQL engine, native per-entity specialization or replacement database transport is introduced. Preserve existing C ABI layouts/actions; additions require explicit capability negotiation and old-call compatibility.

An ordinary DTO change rebuilds managed consumer code only. Independent `Korda.Database.PostgreSql` and `Korda.Database.Sqlite` PackageReference consumers run real services as Linux x64 Native AOT executables. Their business assertions, SQL counts, package/native hashes and DTO-edit reuse are recorded in Plan. Clean-image and CPU-emulation checks are not requested. Existing JIT consumer requirements in the older migration decision do not govern this batch.

## Schema and destructive behavior

Migration generation consumes explicit model snapshots and yields SQL for review. Creating a source/session never migrates. A potentially destructive change must be individually selected by the developer; no destructive-by-default inference or implicit data conversion is permitted. Unknown provider metadata is not fabricated during reverse scaffolding. Generated source must compile through the same public generator and external package workflow.

## Acceptance and history

Exact compiled public signatures, XML and API-reference compatibility remain in Korda. This document specifies behavior and prospective additions; it is not proof of implementation or publication. Follow the [Plan handoff](https://github.com/IzuSharp/Plan/blob/task/DB-API-01-linux/ledger/evidence/batches/DB-API-01/handoff-linux.md), record actual checks and scoped non-author review, then merge normally and inspect merged-main and triggered release results.

Run `python3 tools/verify_fluent_orm.py`. It validates this overlay and runs the unchanged DB-CPP-01 Design gate at `de1f4796dc199250b405ea99f2129d611f17b1f6`. The unchanged earlier history gate remains required. Old accepted hashes, evidence, the 21-contract registry and prior task claims are not rewritten. Stop after this authorized experience batch and its observed delivery.
