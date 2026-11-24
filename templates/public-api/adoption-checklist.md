# New repository adoption checklist

1. Record the immutable NativeWeave-Design commit, `docs/standards/csharp-public-api-and-documentation.md`, version and SHA-256 in a local `public-api-standard.json`; optionally vendor the exact standard bytes with source attribution.
2. Copy the AGENTS fragment, add the README navigation and appoint module, documentation, compatibility and package owners.
3. Pin stable SDK/language/package/native versions; install an API declaration/assembly baseline, XML checks, generated-reference build, consumer sample compilation and required-platform AOT CI.
4. Create a domain coverage matrix using the published schema, explicit support states and concrete managed/native operation mappings. Attach it to the project's existing planning system.
5. Provide getting started and advanced samples with package/using/configuration/disposal/error paths. Tag their evidence state and exact source.
6. Define supported platform/RID/capability and version-upgrade matrices. Measure package dependency closure and costs.
7. Independently review adoption and record exact inputs. Any subsequent standard upgrade is an explicit reviewed version change, not automatic inheritance.

For current Korda implementation, use the module owner and current task recorded in Plan. The original A13/A22/A24 and A16/B24 assignments remain historical planning inputs. A template grants no merge or publication authorization.
