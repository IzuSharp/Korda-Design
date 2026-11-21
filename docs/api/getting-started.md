# Getting started with the database product — DB-Scope-01

The current product is an ordinary C# database library for PostgreSQL and SQLite. It requires neither NativeWeave Server nor a Rust toolchain on the consuming machine. This page describes the existing API route; the [Plan handoff](https://github.com/IzuSharp/Plan/blob/task/DB-Scope-01-linux/ledger/evidence/batches/DB-Scope-01/handoff-linux.md) supplies the exact tested candidate version/feed and execution state. Do not substitute an invented published version.

## Select one provider

Create a normal C# project, add `NativeWeave.Database.Sqlite` or `NativeWeave.Database.PostgreSql` using ordinary PackageReference to the candidate feed, and import `NativeWeave.Database` plus that provider namespace. The package supplies its native closure; consumer build targets do not build Rust.

Use `SqliteDataSource.Create(path)` for an application-owned SQLite path or `PostgreSqlDataSource.Create(connectionString, configureOptions)` for PostgreSQL. Explicit options govern TLS, finite capacity and database behavior. Local-development TLS exceptions are never silently applied to remote PostgreSQL configurations. The alternative `DataSourceBuilder().UseSqlite(...)` / `.UsePostgreSql(...)` route configures the same implementation.

A source owns the database pool/runtime and should normally outlive individual operations. `await using` and `OpenSessionAsync` manage operation/session lifetime. Build alone is not a connection check or migration.

## Define models and query

Use existing static `Table<TEntity>`/typed columns and projections, or the existing query generator, to describe the application's entities and DTOs. Ordinary model/DTO additions compile as managed code and reuse the precompiled native asset. The [compiled API reference](reference.md) supplies exact declarations, and the product's runnable database/Fluent consumers supply full compilable examples.

The normal query chain is `session.From(table)`, typed filters, explicit ordering/pagination, a static projection and an asynchronous terminal such as `ToListAsync`. `AsAsyncEnumerable` is the existing streaming path. Every value is parameterized; unsupported provider operations fail explicitly. Do not pass arbitrary user SQL or build a managed SQL dialect to compensate for missing capabilities.

## Share business logic with a chosen server

Put the database operation in an ordinary application method accepting a cancellation token. A standard ASP.NET Core HTTP endpoint and a standard C# gRPC service method can call that same method. The application owns transport models, response conversion and server configuration. No NativeWeave HTTP/gRPC wrapper is needed or added.

## Run JIT and Native AOT

The acceptance fixture uses normal restore/build/run, then `dotnet publish -c Release -r linux-x64 -p:PublishAot=true` and executes the published binary on Linux x64. The consumer lives outside the source checkout, references candidate packages, uses a separate package cache and verifies actual returned/persisted data.

The exact candidate source, package/native/executable hashes, four provider/runtime outcomes and loaded-library closure are required evidence. A successful restore/build is not an executed query; a published binary is not an AOT runtime pass. Current product regressions are separate from the archived design-only fixtures.
