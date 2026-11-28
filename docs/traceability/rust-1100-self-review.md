# Historical Rust integration review conclusions

These findings belong to the earlier Rust design. Current database implementation
uses C++ as recorded in [ADR-0006](../decisions/ADR-0006-database-cpp-native.md).

- **RV1100-03 — SQL three-valued logic:** nullable integer operands alone do not
  invalidate `NOT(x > y)` versus `x <= y` in SQL. C# compensation is a different
  semantic question. The finite SQLite cases did not establish a universal claim
  for NaN or custom orderings.
- **RV1100-04 — SeaORM dynamic support:** account for the dynamic module; do not
  infer that every integration requires statically compiled entity models.
- **RV1100-07 — stable feature boundaries:** stability of one allocator interface
  does not imply every related extension is stable. Native ownership, cancellation
  and async retirement still require explicit contracts.
- **Acceptance scope:** an amended design needs fresh review of its changes.
  Compiler/API probes are not C# AOT, PostgreSQL, Server or production evidence.

Raw probe output, recovery attempts and duplicate review receipts are not retained
in this documentation tree. The technical conclusions and limits remain above.
