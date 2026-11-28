# R24 — Native SQL semantics, parameters and explicit relations

Research consolidation: 2026-11-12 (America/Los_Angeles); author `/root/database_research`. Baselines Design `ba21ecb5c2299b303584b120f2e6bd1c6d74783a`, Plan `5b346ebb5acdb387077d0faae16b00bbc77cb299`. **Independent acceptance review pending; no product implementation or performance acceptance claimed.** Current evidence and explicit stage obligations are in evidence.json, coverage.json, and completion record.

## Current design

SeaQuery is the SQL semantic constructor and renderer, SQLx the execution/codec authority. C# typing limits invalid composition but does not impose complete LINQ/CLR semantics on SQL. The source-driven contract covers explicit CRUD, comparisons, SQL3VL/null tests, join/group/aggregate/order, supported subquery/CTE/window/set operations and backend capability rejection. Native engine capability is exposed through versioned bindings; unsupported semantics fail before database send.

The previous managed AST/provider and compulsory static SeaORM model assumptions are superseded. Existing SQLite semantic results remain valid. R24's native engine evidence now also includes an executed SeaQuery LEFT JOIN/group/count/sum query compared with separately written SQL over the same actual SQLx SQLite connection. It preserves the distinction between an unmatched row, a matched nullable amount, COUNT(column)=0 and SUM=NULL. The test is finite, not universal relational equivalence.

## Parameters and identifiers

Values are native bound parameters. Identifier quoting prevents syntax confusion but does not authorize table/tenant access; metadata IDs and raw identifier imports require allowlists and native validation. SQLx's AssertSqlSafe is a provenance assertion only. Typed fallible binding propagates encoding errors and rejects overflow, invalid UTF8, mismatched null/type/codec and excess counts before dispatch; no string concatenation fallback.

The existing native-slices fixture already demonstrates the SQLite silent-row-lock negative control and explicit rejection, unsigned overflow before send, encoder rollback and runtime tables. Do not repeat it or promote only a renderer result into real execution. Each native backend/operator pair needs a declared capability and test oracle; SQLite's ignored FOR UPDATE/SELECT INTO/SEARCH/CYCLE and unsupported subquery operators cannot be accepted silently.

## Relational and mutation semantics

SQL3VL is normative. WHERE retains TRUE; NOT UNKNOWN stays UNKNOWN. NULL-safe comparison is a named operator; nullable integer NOT(x>y) versus x<=y equivalence does not justify NaN/custom-order rewrites. LIKE literal conveniences escape wildcard and escape bytes and declare collation; raw patterns are a separate API. LEFT JOIN ON predicates cannot be moved to WHERE. Paging with semantic guarantees requires a unique tie-breaker and explicit snapshot policy.

Rust changesets distinguish NotSet, Null and Value. Native UPDATE predicates always include the declared key, tenant and expected version; affected-row mismatch becomes an explicit concurrency conflict. A real SeaQuery/SQLx fixture performs a nullable update, preserves omitted fields and the other tenant, and observes 1 then 0 affected rows for repeated expected-version writes. This is a native capability binding, not managed tracking.

## Advanced native capabilities and limits

Validate CTE shape before native assertions. The pinned SelectStatement has one optional named-window slot; bind native inline/single-window capability and fail explicit unsupported multi-named-window requests until an upstream extension is adopted. Do not produce SQL in C# to fill gaps. Multiple statement/query features can be bound independently against the same native metadata without new Rust entity types.

Budget the operation count/depth/values before building and parameters before binding; output-length checks after allocating a SQL string are not allocation protection. SeaQuery uses clones/infallible allocations in inspected paths; a bounded operation envelope and conservative admission can limit requested work, not guarantee recovery from every allocator failure. Process-level availability and measured whole-memory limits remain R34/B22/B23 responsibilities.

D16 records the native method/lifetime boundary, supported semantics and explicit rejection table. B11/B13 implement differential SQL+ordered-values+actual-result cases for both PG/SQLite, not only text goldens. No performance superiority, complete EF compatibility or full arbitrary SQL validation is claimed.

## Historical source citations retained

The following original source observations are retained with their original reader identities. They do not restore superseded integration decisions or claim that this author reread every old range.

## Pinned Source Entry Points and Actual Reading

## CI confirmation at the published fixture commit

Historical CI corroborated the mapped native research cases on their stated platforms. This was not new product/AOT acceptance or an additional technical review.
