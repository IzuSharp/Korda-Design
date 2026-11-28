# R07: independent logical admission reproduction

Historical Linux x64 research: ordinary PackageReference consumption and actual
Native AOT execution were observed. This is a scoped prototype, not product
implementation or additional Windows acceptance.

## 1. The Specific Gap Addressed

NS-01 in the earlier [R03 native slice results](../R03/native-slice-validation.md) explicitly states that keeping an existing SafeHandle call alive during Dispose does not prove that new business calls are rejected after logical closure. This round examines that boundary separately, without rerunning the old consumer's 185 assertions or the old Rust unit tests.

The results agree with the existing [R07 source analysis](report.md) and [D04 admission protocol](../../../contracts/lifetime-v0.1.md): while a native held call maintains a physical reference, a new Sum can still execute after Dispose on a simple `OwnedBuffer`; the short managed-gate candidate rejects the new Sum, allows the previously admitted call to complete normally, and finally returns the native live counter to 0. Success of the negative control means the limitation was observed, not that SafeHandle itself violated its physical-lifetime contract.

The pinned source basis for the earlier R07-S01 is `src/libraries/System.Private.CoreLib/src/System/Runtime/InteropServices/SafeHandle.cs` at dotnet/runtime `deae2e32bf0e018e09d64597b7c59b62b73bb3ce`: See the research conclusions and limits in this report. This round does not relabel that source reading as new execution; the actual SDK/runtime identity used for this execution is separately recorded in this round's `dotnet-info.stdout`.

## 3. Controlled Execution Ordering and Oracle

Each execution mode sequentially runs 32 rounds of the simple SafeHandle negative control and 32 rounds of the short-gate candidate. Each round uses an independent owner, with lengths from 257 to 288; the consumer independently calculates the expected sum using the native data rule `i % 251`. Existing native test hooks are process-shared signals, so rounds run serially to avoid mistaking a previous round's signal for the next round's signal.

1. Confirm that the native live counter is 0 and reset the held signal.
2. A worker thread calls the real Rust `nw_buffer_sum_held`. The controller waits for the native entered flag; no step substitutes a fake managed task for native entry.
3. The worker holds a physical lease; the controller calls Dispose twice sequentially on the same thread, then checks that the worker is still in flight, the SafeHandle is not yet Closed, and the native live counter remains 1.
4. Before releasing the held call, the controller attempts a new Sum. The negative control must actually return the correct native sum; the candidate must throw ObjectDisposedException.
5. The controller releases the native held signal and joins the worker; the original call must return the correct value without error. It then checks that the owner is physically Closed and the native live counter is 0, remaining 0 after another Dispose.

The native held wait itself has a 10-second limit; the controller's entered wait and join each have a 5-second limit. A timeout is recorded as failure, not cancellation or success. No sleep is used to guess whether native code has acquired a lease. stdout retains every assertion with case, round, ID, expected, and actual.

## 4. Candidate Implementation and Semantics Supported by This Evidence

`AdmissionBuffer` privately holds the package's `OwnedBuffer`. A call checks `_closing` and acquires `DangerousAddRef` within the same short `lock`, then obtains the raw pointer, calls Sum or SumHeld outside the lock through an exact `LibraryImport` signature, and calls `DangerousRelease` in finally. Dispose sets `_closing` to true under the same gate and disposes the owner outside the lock; repeated Dispose returns inside the gate.

Closed and Closing therefore have clear responsibilities: physical references keep native memory valid for calls admitted earlier; Closing is the rejection point for new business admission. Before the candidate's new call throws, the test has already observed that the owner is not Closed and live=1, so rejection cannot be explained by "the old call has exited and the physical owner has been released." The code does not hold the gate while executing FFI, waiting for native code, calling user code, or executing native release.

This candidate addresses only the synchronous, read-only native summation in this experiment. It does not implement stop capability, callback quiescence, asynchronous retirement, mutable-owner serialization, parent-child ownership, finalizer/unload paths, or cancellation protocols; it cannot replace the remaining D04 clauses or D05/D06.

## Final observed results

| Mode | Actual execution result | Negative control | Gate candidate | Resources at completion |
|---|---|---|---|---|
| `dotnet build` / `dotnet run --no-build`, both without RID arguments | 931 assertions passed | 32/32 new Sum calls admitted after Dispose and returned the correct value | 32/32 new Sum calls rejected; old calls returned the correct value | live=0 in every round |
| Execute the published file after `dotnet publish -r linux-x64 -p:PublishAot=true` | 932 assertions passed; additionally checks that dynamic code is unsupported and not compiled | 32/32 as above | 32/32 as above | live=0 in every round |

The total is 64 real held-call/Dispose sequences in each of two execution modes, or 128 rounds; this is not presented as exhaustive coverage of all races or all .NET runtimes.

## Limitations

Rust was installed and used on this machine, so these results are not proof of deployment to a clean Rust-free host. The old Windows 185 assertions cannot replace a new Windows experiment for this candidate before one is run. There is no fault injection, GC/finalizer stress, exhaustive arbitrary scheduling, or product-load data; no claim is made of zero cost, higher speed, complete shutdown guarantees, or product deliverability.

This research adds a real counterexample for NS-01 and controlled validation of a candidate, retaining D04's independent review and formal acceptance gates. R07 status, registry acceptance, and A/B Delivery must not be upgraded automatically as a result.
