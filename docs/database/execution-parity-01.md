# DB-Exec-Parity-01: measured execution-path strategy

Status: prospective causal experiments after the measured Plan gate, not adopted
performance acceptance. The Plan gate was committed locally as
`da20dc395ca44a0430f933aeb7a45a3ee13aa447` (tree
`dd98f3d3d39b853ae19bf6e7a34d93b5f67cba6e`) before this Design change or product
implementation. The companion [Plan PR36](https://github.com/IzuSharp/Plan/pull/36)
owns actual receipts, source identities, raw archive publication, comparisons,
failed attempts and continuation. This document will record retained and rejected
strategies after evidence exists.

## Preserved boundary

Retain the C# Fluent API, Native AOT, C++ libpq/sqlite3 execution and independently
installable PostgreSQL/SQLite packages. Internal refactoring does not authorize
changes to input snapshot, fresh metadata/DDL behavior, failure ordering,
cancellation, row borrow, early stop, transaction-unknown, resource admission or
safe connection return. The original35-case workload and explicit batch32 limits
remain acceptance inputs. Larger-batch probes are diagnostic sensitivity only.
Runtime settings remain default in product measurements.

## Measured priority

Both engines execute the same narrow full-result query/row work. Hot Prepare's
1000-row client CPU is8.80× Dapper for SQLite and8.74× for PostgreSQL, with only
about802 B/550 B extra managed allocation. Complete Host SQL is similarly costly.
The actual generated mapper and list allocations are almost equal. SQLite does
not have a Dapper physical-statement reuse advantage in this contract. PostgreSQL
wire volume differs by only71 B for1000 identical DataRows; direct Korda poll
calls remain2 rather than scaling with row count.

Measured Korda batches/native jobs scale32/34→8/10→4/6 under the batch-size probe.
Sampled AOT spin leaves dominate the Korda CPU profile, and a repeated identical-
binary runtime sensitivity reduces CPU without consistent endpoint latency gain.
Actual native enqueue/worker/ready/managed-take spans show the repeated handoffs.
These facts support testing the common completion path first. They do not assign
all spin samples to one caller or justify changing global ThreadPool settings.

## Experiment A: completion after the coordinator's final scheduling tail

The native ready callback continues to do only bounded readiness bookkeeping and
offer a managed coordinator work item. User continuation code must never run on
the unmanaged callback stack. The first managed scheduling boundary remains.

Each coordinator Execute invocation prepares its own immutable, generation-bound
completion value. It completes all dirty/scheduled/retry bookkeeping and any
required rescheduling before invoking that value as the last action. An internal
stack-local publication value passed by reference is acceptable; a shared pending
publication slot is not, because an old Execute could steal a later generation's
publication after reentrancy. No delegate/Task allocation per batch is introduced.

HostPull may disable asynchronous continuation dispatch only after that boundary
is safe. Runtime rules for captured contexts and registration after completion
remain intact; there is no promise that every batch becomes inline. Other
coordinator subclasses retain their existing behavior. The unreserved local
setup-failure path needs the same final-publication boundary.

Before publication: accepted readiness/setup is known; cancellation registration
has drained; callback/control entries are zero; native result is taken once;
root/reservation are released once; observer failures and failed-result disposal
are settled; the exact generation/version/result/error are captured. No gate is
held while invoking completion.

After publication starts: no controller, scheduling, owner, root, generation,
batch or stop state may be accessed by that old invocation. A continuation or
SynchronizationContext.Post exception after the MRVTS completion sentinel is a
managed dispatch/execution exception. It must stay outside SchedulingFault and
must not trigger a second setter, dispose a delivered batch, poison the next
generation or cross back into native code. Preserve exception observation rather
than blanket swallowing or inventing successful dispatch.

Required regressions include early ready during setup, rejected scheduling/retry,
stale/duplicate generation, held row borrow plus Dispose, unreserved stop failure,
direct synchronous g1 consumption followed by g2 Request, delayed old publication,
captured Post that consumes/starts g2 and then throws, and registration after
completion. The old held-context test's meaningful ownership barriers remain;
only assumptions about the old scheduling implementation may change. Measure
fairness and retained publisher tails under concurrency before adoption.

The causal test must count actual eligible completion delivery and thread
boundaries, keep engine/protocol/batch counts unchanged, then measure ordinary
same-host alternating A/B at1/32/100/1000 and early stop. A drop in one counter
without repeatable endpoint/CPU benefit is insufficient reason to retain this
complexity. Prior rejected callback-inline and quiet-close patches remain
rejected evidence, not implementation templates.

## Experiment B: SQLite short-lived statement allocation

The measured current path prepares/finalizes one physical statement per business
request yet supplies SQLITE_PREPARE_PERSISTENT. The locked SQLite implementation
disables lookaside for that flag. A separate source identity may change only the
v3 flag to0, preserving SQL, parameter binding, v3 preparation, automatic schema
reprepare, metadata validation and effect ordering. Measure public allocator and
SQLite lookaside counters; do not label all process allocation as framework-only.
No statement cache is introduced by this experiment.

## PostgreSQL result granularity: unconditional chunking rejected before coding

The measured1000-row path allocates1000 PGRES_SINGLE_TUPLE results, so native
result-object allocation is a valid resource target. However pinned libpq18
chunked-row mode may clear an unfinished chunk when a later server error arrives,
where single-row mode already delivered earlier rows. The provider regression
requires earlier rows before a later error. Chunking also increases held provider
rows above the existing one-row lookahead/byte-admission guarantee. Therefore
unconditionally enabling chunk32 is rejected. No benchmark-specific SQL exception
or weakened failure order is permitted. A different implementation requires its
own complete contract proof and measured resource benefit.

## Remaining measured candidates

Per-row Cancel.install, built-in codec temporaries and full-batch offset rewriting
are observed repeated work. They may be tested individually after their ownership
and allocation boundaries are specified. Full-batch finish rescans are a lower-
risk but apparently small CPU target:2000 cells/1800 rewrites at1000 rows despite
only124 B partial-batch payload movement. Any skip must preserve non-NULL empty
cell offsets, partial/byte-limited batches and canonical frame bytes.

## Acceptance and delivery

All performance work runs locally on Linux x64. Existing module-routed CI keeps
compile, correctness, security, API and independent provider AOT package checks
and rule-selected release. No benchmark, profiling, calibration, pressure action
or indirect invocation is added to CI. Inspect the committed product diff with
`python3 eng/ci/impact.py origin/main --output artifacts/plan.json` before push.

Before adoption: independent review, required correctness/public API and actual
standalone package consumption, repeated ordinary A/B plus mechanism evidence,
zero-refusal cost and pressure onset, adequate comparable before data. Final
acceptance requires four serial1800-second ordinary Release Native AOT mixed35
cells with warmup separate. Only repeatedly supported metrics may be called
aligned. Report remaining gaps and bounded stopping reasons, then normal reviewed
merges, existing main CI/releases and real public NuGet AOT consumption. These
outcomes are all pending at this strategy checkpoint.
