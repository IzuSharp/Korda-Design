# Historical local Windows/Linux research conclusions

The 2026-11-14 supplement reproduced four research suites on existing Windows
and Linux developer hosts. Input Design revision was
`4c5c385779b753a4f06e59d07f80ad27ca10a841`. These were installed developer machines,
not pristine consumers or proof of production readiness.

| Existing fixture | Windows | Linux | What was actually exercised |
| --- | --- | --- | --- |
| `server-completion` protocol | 19 passed | 19 passed | Rust HTTP/1 and HTTP/2 loopback, TLS/ALPN positive and negative cases, Tonic message-cardinality handling and MCP cases. |
| `database-completion` metadata | 5 passed | 5 passed | Existing Rust runtime metadata and SQLite/query behavior; no C# ORM or PostgreSQL execution in this suite. |
| `engine-completion --aot` | Passed, 17 AOT checks | Passed, 17 AOT checks | Native codec tests/build, NuGet pack, separate RID-free consumer build/run, removal of Rust tool discovery, offline C# type addition with unchanged native asset, explicit-RID AOT publish and actual execution. Ordinary consumer: 16 checks per host. |
| `platform-completion --aot` | Passed on attempt 3 | Passed on attempt 2 | Ordinary execution: 9 checks; expected external closed-type compilation rejection; default and runtime-async actual AOT: 10 checks each; separate compiler-lowering inspection. |

The codec experiment supplies an end-to-end **research packaging and consumption**
path. Its filtered consumer PATH has no discoverable `cargo`, `rustc` or `rustup`,
but Rust remains installed elsewhere on the developer host. The protocol suite
does not execute a C# FFI Handler. These results do not establish the future
HTTP-to-C#-to-Rust-Database reference application, long-running resource stability,
performance advantages or release readiness.

## Findings and dispositions

| Finding | Impact and retained evidence | Resolution |
| --- | --- | --- |
| LH-LINUX-001 — native linker dependencies | Initial engine and platform AOT attempts failed to link `brotlienc`, `brotlidec`, `brotlicommon` and `zstd`. JIT success did not satisfy AOT. | Installed Debian `libbrotli-dev` 1.1.0-2+deb13u1 and `libzstd-dev` 1.5.7+dfsg-1. New output directories retain successful actual AOT runs. Existing zlib development files and Clang were sufficient otherwise. |
| LH-WINDOWS-001 — diagnostic language assumption | Platform attempt 1 emitted the intended CS9382 compiler rejection, but the research runner additionally expects the English word `closed`; the Chinese diagnostic failed that assertion. | Set `DOTNET_CLI_UI_LANGUAGE=en-US` in the research child environment. The source and negative test remain unchanged. |
| LH-WINDOWS-002 — inherited MSBuild platform | Platform attempt 2 published native code, then failed to find the compiler assembly: `vcvars64` injected `Platform=x64`, selecting `bin/x64/Release` while the fixture inspects `bin/Release`. It did not reach AOT execution. | Clear only the inherited `Platform` variable after MSVC initialization; retain the linker/SDK variables. Attempt 3 passed the negative case, both metadata checks and both actual AOT executions. |

The MCP service environment also required explicit selection of the installed
Scoop/Homebrew tools and matching `DOTNET_ROOT`; installation alone did not imply
that a long-running MCP process already had their PATH. These are scoped launcher
settings, not global SDK upgrades or changes to the accepted design.

The original failures remain failures; the corrections above explain the later
success. Temporary command output, launch receipts and snapshots are omitted from
the current tree. The [independent review](reviews/local-host-2026-11-14/independent-review.md)
retains the scope and limitations.
