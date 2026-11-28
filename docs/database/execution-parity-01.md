# DB-Exec-Parity-01: execution decisions and measured limits

This document consolidates the retained and rejected execution experiments. The
latest recorded selection contains five performance strategies and a separate
native-owner correctness repair. The final-frame pool, local queue preference and
completion-tail variants were rejected. It does not claim Dapper.AOT parity,
framework-only zero allocation or sustained capacity.

All measurements were local Linux x64 work. The proposed long campaign and its
long before-supplements were cancelled before they started. The short results
below do not authorize another campaign or further product changes. Plans and
observed delivery outcomes belong to [Plan](https://github.com/IzuSharp/Plan);
product correctness, Native AOT packages and release checks belong to
[Korda](https://github.com/IzuSharp/Korda).

## Preserved contract and measured priority

Retain C# Fluent, Native AOT, C++ libpq/sqlite3 execution and independent
PostgreSQL/SQLite packages. Input snapshots, fresh metadata/DDL behavior, failure
ordering, cancellation, row borrowing, early stop, Unknown transaction outcomes,
resource admission and safe connection return remain obligations. The measured
workloads use their original complete-result oracles and batch32 limits; larger
batches were diagnostic sensitivity, not a changed business contract.

At the initial measured boundary, hot Prepare's 1,000-row client CPU was about
8.80× Dapper for SQLite and 8.74× for PostgreSQL, despite only about 802/550 B
extra managed allocation. Mapper/list allocations were almost equal. SQLite had
no Dapper statement-reuse advantage in that comparison; PostgreSQL wire volume
differed by 71 B for identical DataRows, and Korda's direct poll count remained two.

A batch-size probe changed native batches/jobs from 32/34 to 8/10 to 4/6. Native
queue/worker/ready/managed-take observations supported investigating repeated
handoffs. Sampled spin leaves and runtime sensitivity did not identify one
exclusive caller, establish kernel wakeup cost or justify global runtime tuning.

## Retained strategies

| Strategy | Boundary and reason | Measured limits |
| --- | --- | --- |
| Admitted managed execution of native pulls (Worker-D) | Reuse bounded admission and the shared ThreadPool; execute an already admitted native pull and its result take in one managed work item | Fewer native queue jobs are not fewer FFI entries; the explicit run entry adds a crossing |
| Exact canonical decimal recognition | Recognize only the complete valid canonical precision/scale form, retaining all validation sites and the original JSON fallback | Decimal-specific benefit; integer/control cases and aggregate latency do not uniformly improve |
| SQLite short-lived prepare flags | Use flags appropriate to statements prepared/finalized per business operation, allowing SQLite lookaside | No statement cache or claim that every process allocation belongs to Korda |
| Private relation branch transfer | Consume an exclusively owned temporary RelationBatch branch after successful import instead of cloning it | Public Combine retains snapshot/reuse semantics; no public consuming API or relation cache |
| Bounded private relation capacity | Reserve at most 2,048 bytes for an eligible fresh private branch, otherwise retain original growth | Repeated resource benefit, with mixed CPU/tail results; cache and process RSS claims do not follow |

### Admitted pull execution and retirement

The existing bounded coordinator reservation and never-inline shared ThreadPool
worker provide the managed scheduling boundary. A nonblocking native admit entry
performs validation, input snapshot, Session admission, generation/cancellation
setup and Source/channel retirement reservation before managed queue acceptance.
The initiating public Async call never waits for provider completion. Deferred
work owns references; a synchronous OwnerLease, Span or borrowed pointer cannot
escape into the queue.

Queued work has one run-versus-abandon claim. Source/Session close, scheduler
rejection and pre-run cancellation must settle accepted work and release tickets
without self-waiting or a retained ownership cycle. Synchronous run reuses the
original open, complete metadata validation, second admission, fetch, cancellation
detach, completion and error enrichment. It does not create another provider
algorithm or bypass fresh DDL checks.

The same worker takes the result only after native run returns and setup, controls,
callbacks and cancellation-registration drains allow it. MRVTS continuations remain
asynchronous. Bounded readiness callbacks cannot run user continuation code on the
unmanaged stack. Native Source management, cursor final close, Source join and
transaction workers remain independent; no dedicated managed pool is introduced.

Retirement covers the exported run frame's final accessor, not only an inner
worker destructor. Source join cannot report quiescence while an admitted native
frame still accesses channel, session, source or provider state. Ready, result take
and final retirement are separate events. Preserve rich errors, correlation,
priority, late PostgreSQL failure, bounded drain, poisoning and Unknown COMMIT.

Required correctness boundaries include held native run with public Async return,
rejected scheduling after accepted admission, pre-run abandonment, Source close,
duplicate/stale work, draining controls, owner-adoption failure, held row plus
Dispose and late old-generation work. The old ABI retains its meaning; the private
extension is negotiated for both providers.

### Decimal configuration

Recognition is restricted to the exact canonical valid form. Malformed,
overflowing, unsupported or noncanonical input uses the original JSON/error path.
All original profile/OID checks, three validation positions and error precedence
remain. SQLite decimal rejection still precedes parsing; other codecs are unchanged.
There is no mutable codec cache or pointer-identity shortcut.

For 1,000 decimal values, the isolated diagnostic observed JSON parses fall from
4,000 to zero and public allocations from 48,000 to 1,000, while 3,000 validations
remained. Ordinary decimal32/decimal1000/wide32 screens improved in their recorded
scope; the 1,000-decimal CPU still remained about 8.5× Dapper. Control regressions
and later PostgreSQL queued-p99/idle-RSS risks remain part of the conclusion.

### SQLite preparation

The original per-request prepare/finalize path supplied `SQLITE_PREPARE_PERSISTENT`,
which disables lookaside in the inspected SQLite implementation. The retained
change uses v3 flags zero while preserving SQL, parameter binding, automatic schema
reprepare, metadata validation, effect ordering and finalization. Repeated Host
allocation benefit was observed with unchanged engine work. This is a resource
optimization, not parity or a cross-execution statement cache.

### Private relation ownership transfer

The isolated related32 construction showed 31 clones per business, 120,776 B of
managed clone allocation and 54,932 tape bytes copied. Clone accounted for about
17.6% of the approximately 686 KB total; SelectParent remained a larger separate
cost. Build overlap excluded those diagnostic timings from CPU/latency claims.

Only RelationBatch's exclusively owned temporary branch may use the consuming
import. Under the existing fail-fast gates, the original SnapshotAndImport keeps
dependency retention, selection/seal/source validation, finite quotas, parameter
collision checks and metadata updates. Only successful completion commits
consumption. Mark the source disposed/context sealed without a new allocating or
fallible step; release its original reference after destination retention is safe.
Every pre-commit failure leaves source ownership intact. The existing caller
cleans up a later union failure.

Public Combine still snapshots and permits source reuse. Key snapshots, duplicate
positions, native collation, one SQL statement, shared result budgets, DDL and error
ordering remain. Equivalent command bytes, failed-import reuse, public reuse,
private invalidation, invalid concurrent/self/cross-source cases and zero final
owners are required controls. No full relation plan cache or new native path is
implied by removing a clone.

### Bounded private capacity

After clone removal, the diagnostic measured 98 tape-growth allocations and
129,328 B per related32 request. The retained hint reserves at most 2,048 bytes
for a fresh private branch, using the first completed branch's capacity only when
immutable key-component encoded lengths match. Different lengths or unsuitable
builders use the original growth path. Public From/Combine, quotas, error order,
input snapshots and ownership are unchanged.

Actual growth plus reserve allocation fell to 80,224 B per business, saving
49,104 B; growth copying fell from 63,488 to 7,936 B. The 31 new reserve arrays
are counted. Original row/digest/SQL/protocol and zero-owner controls passed.
Ordinary related32 allocation fell by about 49 KB in all four comparison pairs,
while CPU/p50/p99 changes were mixed. Gen0 increased and Gen1 decreased. No
idle-release RSS or pause credit was established by this isolated screen, and
its saving must not be added to a different native-identity group.

## Separate correctness repair: metadata before native adoption

Plan/CTE object initializers previously adopted a native result into a finalizable
SafeHandle before allocating metadata. A metadata failure could cause both the
raw catch and a later finalizer to release the address. The native registry had
no generation protection for a subsequently reused address. This was a
source-confirmed risk, not an observed corruption or ABA incident.

Complete metadata inside the existing raw-owner try/catch before native-result
adoption. DatabaseOwner calls SetHandle last; the subsequent existing property
assignments do not allocate. Preserve native status/null checks, validation,
Compile/Cte and origin-publication order. The allocation/OOM order explicitly
changes. Synthetic failures were separate local tests, not shipping callbacks or
a claim of real OOM injection.

The reviewed source was Korda `106fe68b6f6c2537f478daf65a71ab97cc4b15ff`, tree
`f7660759bba43ae83324620e2fb731efd479c3b5`. Both sides of the final pool comparison
contained this repair, so its effect cannot be credited to the pool.

## Rejected alternatives and reasons

| Alternative | Outcome and retained reason |
| --- | --- |
| Common completion publication / later tail06 | The intended mechanism and correctness were observed, but a repeatable common CPU/tail/memory benefit was absent; keep asynchronous MRVTS completion |
| PostgreSQL interrupt-hook removal | The hook wrote an unused flag and its mechanism changed, but ordinary endpoint benefit did not repeat; hook count was not an allocation count |
| Lease zero-owner Release bypass | No stable CPU improvement |
| Ready-row completion | Context/correctness checks passed; PostgreSQL thousand-row CPU and p50 regressed in both reversed rounds |
| HostPull local queue preference (local07) | Default-scheduler correctness passed, but useful CPU reduction did not repeat; retain the existing queue policy |
| Private final-frame rental (frame08) | Repeated allocation saving came with an unacceptable/inconsistent common CPU, tail and idle-memory tradeoff |
| Unconditional PostgreSQL chunk32 | Rejected before implementation: unfinished chunks can hide earlier rows when a later server error arrives, and exceed the one-row lookahead/admission boundary |

### Completion-tail and queue findings

Tail06's mixed PostgreSQL CPU decreased in both reversed rounds (−3.85%/−2.25%),
but SQLite changed direction (−5.30%/+1.92%) and PostgreSQL released-idle RSS rose
in both rounds. SQLite thousand-row and early-stop risks remained. Correctness
alone did not justify adopting a more complex completion boundary.

The local07 comparison changed only HostPull's default queue preference. Relative
CPU changes were SQLite +17.42%/−0.68% and PostgreSQL +6.55%/+0.06%. A type-test or
queue primitive was not proved to be the exclusive regression cause. Runtime
stealing and a dispatch quantum do not establish bounded fairness. No
provider-specific switch, extra favorable rounds or combined tail variant was
selected after rejection.

### Final-frame rental and resource costs

The rejected pool covered only Seal's graph slow-path frames with
`4096 < logicalLength <= 65536`, using a lazy private
`ArrayPool<byte>.Create(65536, 4)`. The copyable encoded command remained a borrow;
Seal owned one local rental through synchronous Compile and metadata/origin
completion, returned exactly once with `clearArray:true`. Header/native views used
logical length, reserved bytes were initialized and bucket tails excluded. Public
snapshots, quotas, error order, stack path and smaller/larger fresh arrays remained.
Poison/re-rent execution tested that native literals/origins owned copied bytes.

The inspected configurable pool uses a bucket SpinLock and no automatic trimming.
Four reachable buckets can retain 491,520 B payload, with related32 alone retaining
262,144 B; these are cache bounds, not active-memory or RSS bounds. A miss allocates
instead of rejecting business work. Return clears the full actual array even if
the bucket subsequently discards it. Cold allocation, initialization, clear cost
and idle residency count against any allocation benefit.

All 24,576 measured businesses and 1,302,528 rows passed the original 53-row oracle.
Managed process allocation fell about 60.77–60.82 KB/business (11.77–11.78%). The
264–318 B difference from the earlier scoped target remained unassigned
process-level variation; no exclusive attribution was invented.

| Provider | CPU change, rounds 1 / 2 | p99 change, rounds 1 / 2 | Five-second released-idle RSS change, B |
| --- | --- | --- | --- |
| SQLite | +22.80% / −0.93% | +29.48% / −2.82% | +45,056 / +143,360 |
| PostgreSQL | +0.84% / −18.66% | −5.31% / −5.88% | +667,648 / +548,864 |

Process peak RSS and GC pause decreased while released-idle RSS increased. The
SQLite regression is an observation, not proof that locking or clearing alone
caused it. External scheduling was not proved to be exclusive either, so the bad
interval was not discarded. The pool and diagnostic hooks remain unadopted.

## Final limits

The retained ownership05 related32 CPU in that screen was still 3.22–4.56× Dapper
for SQLite and 7.61–10.05× for PostgreSQL; managed process bytes were about
6.97×/10.08×. The earlier text1000 CPU gap persisted with only about 1% allocation
difference. A final-frame buffer optimization cannot explain that whole gap.

Keep source inspection, instrumented diagnostics, ordinary PackageReference AOT
comparisons and actual delivery outcomes distinct. No exclusive RhSpinWait stage
time, zero framework allocation, full parity or long-duration capacity was proved.
Further optimization requires a new measured causal hypothesis. CI continues only
its current correctness/module/package responsibilities; this document adds no
benchmark, profiling, calibration or pressure workflow.
