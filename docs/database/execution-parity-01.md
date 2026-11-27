# DB-Exec-Parity-01: measured execution-path strategy

**Current owner scope:** all long measurements and before-long supplements are
cancelled in this round. Continue finite diagnostics and ordinary short A/B.
[Plan Scope08](https://github.com/IzuSharp/Plan/blob/c7c66d56649192512204ca14fc2860ba99336b80/ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/phase-2/recovery-04/short-only-scope-08.md)
supersedes the unexecuted 1800-second requirements below. No long cell started;
the former0/4 is a cancelled plan, not an outstanding gate. A future long test is
only potentially useful after short results are very close to Dapper; this is
not automatic authorization to start one. Do not infer sustained parity from
short samples. All original evidence and failed experiments keep their identities.

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

## Experiment C: omit ineffective PostgreSQL interrupt hooks

The actual thousand-row path installs1002 cancellation hooks. The compiled
weak_ptr lambda is stored in std::function's small buffer; these calls are not
1002 proved allocations. Baseline source shows the PostgreSQL interrupt hook
only writes an interrupted flag that is never read. Its only engine side effect
is in the SQLite branch. PostgreSQL already observes cancellation through the
unchanged per-row and nonblocking receive/poll checks, then bounded cleanup.

An isolated candidate may install provider interrupt hooks only for SQLite and
remove the unused interrupted flag/stores. Preserve old-token detach, every
CallContext check/deadline, protocol drain/poisoning and Unknown commit semantics.
The prediction is PG install1002→0 with identical SQL/protocol/rows/batches and
unchanged SQLite behavior, not a promised malloc reduction. Actual cancellation,
late-row error, early stop, cleanup and unknown-commit regressions plus repeated
count/CPU A/B determine adoption. No cached Cancel identity or skipped external
detach is introduced.

## Remaining measured candidates

Per-row Cancel.install, built-in codec temporaries and full-batch offset rewriting
are observed repeated work. They may be tested individually after their ownership
and allocation boundaries are specified. Full-batch finish rescans are a lower-
risk but apparently small CPU target:2000 cells/1800 rewrites at1000 rows despite
only124 B partial-batch payload movement. Any skip must preserve non-NULL empty
cell offsets, partial/byte-limited batches and canonical frame bytes.

## Current causal outcomes and selected follow-up

The newer Plan checkpoint `b30caf8` records the completed isolated screens before
this strategy update. The main task product has not yet integrated a candidate.
Common completion A and PG cancel-hook C are not selected: the intended mechanism
was observed but ordinary endpoint benefit did not repeat. The lease-B zero-owner
Release bypass also did not deliver stable CPU improvement. Ready-row-C preserves
async contexts and passed its AOT checks, but is rejected because PG thousand-row
CPU and p50 regress in both reversed rounds. Those paths remain independent
experiment evidence and will not be layered into the next candidate.

SQLite's v3 flag change has repeated actual Host allocation benefit with unchanged
engine work. It is retained provisionally as a resource optimization, subject to
the final combined mixed regression gate. It does not establish query parity.

### Decimal configuration: retain exact valid-path parsing

PostgreSQL decimal decoding repeats the same canonical precision/scale JSON
configuration four times per value at three preserved validation positions. The
selected isolated implementation recognizes only the complete canonical valid
form without constructing general JSON trees. Every original validation call,
profile/OID check and precedence remains; malformed, overflowed, unsupported or
noncanonical input goes to the original JSON implementation and error path. No
mutable Codec cache, pointer identity shortcut or skipped validation is added.
SQLite decimal rejection remains ahead of this parser; other codecs are unchanged.

Repeated actual decode scopes show4000->0 JSON parses and48000->1000 public
allocations for1000 decimal values, while3000 validations remain. Ordinary two-
round screening shows useful decimal32/1000 and wide32 gains, but integer/control
paths and aggregation do not all improve, and the1000-decimal CPU remains about
8.5 times Dapper. Report the limited scope and small observed control regressions;
final combined mixed measurements decide full adoption and any alignment claim.

### Worker-D: admitted shared-ThreadPool pull execution experiment

Select a distinct isolated scheduling experiment based on the measured32 batches/
34 native jobs and queue/ready/managed-take timeline. Reuse the existing bounded
CallbackCoordinator reservation and never-inline shared ThreadPool worker. The
worker executes an already-admitted native cursor pull synchronously and then
performs the existing result take in the same work item. This tests whether
avoiding the native-queue round trip reduces the repeated ThreadPool idle/wakeup
cost. No sampled spin instruction is assumed to belong exclusively to this path.

This is a proposed private execution strategy, not product acceptance. Preserve
C# Fluent, public signatures, Native AOT, both independent packages, native C++
libpq/sqlite3 algorithms and all current workload/SQL/batch inputs. Native Source
admission, management, final cursor close, Source join and transaction workers
remain independent. The declared EngineLocalAsync model keeps native instance
admission/control; this hybrid pull scheduling must be documented accurately if
adopted. It does not create a dedicated managed pool or change runtime settings.

A new nonblocking native prepare/admit entry must perform original validation,
input snapshot, Session gate, generation/Cancel setup and source pending plus
channel/source retirement reservation before managed queue acceptance. Public
Async never waits for provider completion on its initiating thread. Deferred work
owns its references; synchronous OwnerLease/Span/raw borrowed pointers cannot
escape into the queue. Queued work has a unique run-versus-abandon claim. Source/
Session close, scheduler rejection and pre-run cancellation must settle accepted
work, release tickets and break any retained cycle without self-waiting.

Synchronous run reuses original CursorPull::run/open/full metadata validation/
second admission/fetch/Cancel detach/complete/error enrichment. It must not create
a separate provider execution algorithm or bypass fresh DDL checks. Old request
ABI semantics remain unchanged; a new private extension negotiates both providers.
The same worker may take only after native run returns and the original setup,
controls, callback and cancellation-registration drains permit it. Retain MRVTS
asynchronous continuation behavior and do not combine common-A. A bounded ready
callback may remain for state notification, with no user continuation on its
native stack; callback elimination is not a claimed causal outcome.

Retirement proof must cover the new exported-run frame's last accessor, not only
the inner Worker destructor. Source join cannot report quiet while any admitted
native frame still accesses channel/session/source/provider state. Ready, result
take and final native retirement remain different events. Preserve all original
rich errors, code/correlation, error priority, late PG failure, bounded drain,
connection poisoning and Unknown commit behavior. The experiment does not touch
transaction finish/deadline workers or redefine cancellation as native retirement.

Required new proof includes held native run with public Async returning, accepted
prepare plus rejected scheduler, pre-run abandonment and Source close, duplicate/
stale work, controls or registration draining during run, owner-adoption failure,
held row plus Dispose, and late old-generation work. Separate diagnostic identities
must show actual queue, callback, FFI, SQL/protocol, batch, byte and owner counts;
then matched ordinary A/B must show useful CPU or endpoint improvement. Retain the
original correct path until the replacement's gates pass, then remove superseded
internal routing while preserving public/frozen ABI compatibility. All performance
work remains local and no CI workload is added.

### Relation batch allocation: observe before selecting a strategy

The original related32 case allocates about686KB per Korda business on both
providers, versus74KB/51KB Dapper. This prioritizes shared managed construction.
An independent diagnostic first separates key snapshot, one IndexedChild
projection,32 From/SelectParent,31 Combine/dispose, final synchronous ToList prefix
and post-await grouping using bounded preallocated records and same-thread
allocation counters. Do not subtract counters across await or add inclusive nested
scopes. Hot model/projection metadata already has caching and stack encoding;
source counts alone do not prove the largest allocation site. No full relation-plan
cache or public prepared overload is selected at this checkpoint. Any later change
must preserve complete key snapshots, duplicate-position groups, native collation,
one SQL statement, shared bounded result budget, DDL and error ordering.

### Relation batch: private branch transfer selected from measured clones

Recovery 03 now measures first-layer scopes in both providers and nested clone/copy
scopes in SQLite. Each related32 business performs 31 clones: 120,776 B of managed
allocation and 54,932 tape bytes copied. Clone accounts for 17.6% of the roughly
686 KB total; SelectParent remains a larger independent cost. Combine is exactly
181,760 B in both providers. These are same-thread allocations and actual copy
events with zero-allocation controls, original 53-row digest, one SQL statement
and zero final owners. Build overlap makes their CPU/latency data ineligible.

Select an isolated internal consuming import only for RelationBatch's exclusively
owned temporary branch. Public Combine retains full snapshot/clone semantics and
source reuse. Under both existing fail-fast admission gates, invoke the original
command SnapshotAndImport with the actual source command. It must retain the
dependency, validate selection/seal/source, check finite quotas and parameter
collisions, append, and complete all metadata updates. Only successful return
commits consumption; mark the source binding disposed and context sealed without
any new allocating/fallible step. The existing source gate exit releases its
original reference, after destination retention is durable. Every pre-commit
validation/budget/admission failure leaves source ownership intact. Later union
failure is cleaned up by the private caller's existing disposal path.

Keep key collection/value snapshots, duplicate positions, native collation, one
SQL, shared row/byte limits, DDL and error ordering unchanged. Do not introduce
a full relation cache, public consuming API, mapper change or new native path.
Require equivalent submitted bytes, failed-import reuse, public snapshot reuse,
private invalidation, cross-source/self/direct/concurrent rejection and zero
owner leaks in actual Query.Binding AOT; run existing dual-provider Relations.
Then demonstrate Clone31->0 and CloneCopy54,932->0 with the same diagnostic scopes,
and repeated uninstrumented A/B with identical native bytes. These measurements
select an experiment; they do not establish acceptance or zero framework allocation.

## Recovery 04: provisional combined validation

[Plan selection `338d45f`](https://github.com/IzuSharp/Plan/blob/338d45fce50d454cb282a1557452cf247b9635c6/ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/phase-2/recovery-04/integration-selection.md)
selects integration of Worker-D, exact decimal configuration recognition,
short-lived SQLite prepare flags and private relation branch transfer. Each
retains its isolated evidence identity; combined performance must be measured
against matching unchanged-main binaries rather than added from those results.

This preserves all strategies and boundaries described above. Native queue-job
reduction is not a reduction in FFI entry count: the explicit admitted Run entry
adds a crossing per batch. Managed continuation scheduling remains asynchronous.
The decimal money1 CPU increase and public Combine tail variability remain open
regression gates. No unknown `RhSpinWait` caller or kernel scheduling cause is
assigned from leaf samples. Deep relation scopes decide whether any further
strategy merits a separate proposal; they do not authorize a cache or public API
change by themselves. This integration state is not final adoption or freeze.

### Private relation capacity: isolated follow-up hypothesis

Recovery04 deep scopes measure98 tape growth allocations/129,328 managed B per
related32 request after clone removal, on both providers. A separate experiment
may reserve at most2048 bytes for a fresh private branch, using the first completed
branch capacity only when immutable key component encoded lengths match. Different
lengths or an unsuitable builder use the original growth path. Public From and
Combine, snapshot, quotas, error order, original growth fallback and ownership
remain unchanged. No mutable data cache, graph-frame pooling, global initial size
or early quota failure is introduced. Count actual bytes copied if any command
prefix already exists. Actual dual-provider scope/oracle/ownership controls and
reversed ordinary A/B decide adoption; the predicted49,104 B saving is not a result.
This proposal follows Plan's `recovery-04/relation-capacity-hypothesis.md` and is
independent of the four-candidate integration state above.

### Capacity resource result and provisional integration

The isolated capacity source `6b872e3` completed both-provider scope, real AOT
correctness and reversed ordinary tests. Actual growth plus reserve allocation
fell from129,328 to80,224 B/business (49,104 B saved), and growth copying fell
from63,488 to7,936 B. The31 new reserve arrays are included. Public union controls,
original row/digest/SQL/protocol and zero-owner checks passed. Ordinary related32
process allocation fell about49KB in all four pairs; CPU/p50/p99 changes were
mixed between AB and BA. Gen0 increased while Gen1 decreased, and no idle-release
RSS or pause credit is available from this isolated screen.

Select the private hint for combined validation solely on the repeated resource
benefit, subject to the final mixed regression gate. Do not claim faster queries,
add this saving to another native-identity group, or include diagnostic scopes in
the product. Plan records the failed disk-exhaustion attempt and original error
mapping controls. The hint remains bounded and has no public API/cache/ownership
or quota semantic change. Integrated actual package consumers must be rebuilt.

## Acceptance and delivery

All performance work runs locally on Linux x64. Existing module-routed CI keeps
compile, correctness, security, API and independent provider AOT package checks
and rule-selected release. No benchmark, profiling, calibration, pressure action
or indirect invocation is added to CI. Inspect the committed product diff with
`python3 eng/ci/impact.py origin/main --output artifacts/plan.json` before push.

Before adoption: independent review, required correctness/public API and actual
standalone package consumption, repeated ordinary short A/B plus mechanism
evidence, zero-refusal cost and bounded short pressure observations, and adequate
comparable short before data. The owner cancelled the previously planned four
serial1800-second campaign and its long before supplements before any started.
Only repeatedly supported metrics may be called aligned. Report remaining gaps
and bounded stopping reasons, then normal reviewed merges, existing main
CI/releases and real public NuGet AOT consumption. A short pressure observation
does not establish long-duration sustainable capacity. Delivery outcomes remain
pending at this strategy checkpoint.
