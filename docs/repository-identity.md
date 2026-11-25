# Korda-Design repository identity

The owner renamed the design repository from `IzuSharp/NativeWeave-Design` to [IzuSharp/Korda-Design](https://github.com/IzuSharp/Korda-Design). Use the canonical URL for new clones, current documentation links and live repository requests:

```text
https://github.com/IzuSharp/Korda-Design
https://github.com/IzuSharp/Korda-Design.git
```

The companion repositories are [Korda](https://github.com/IzuSharp/Korda) for the product and [Plan](https://github.com/IzuSharp/Plan) for execution and acceptance records. This change updates repository identity. The retained database contracts, C# package/API names, native assets and persisted database identifiers keep their existing meaning. DB-Perf-01 remains cancelled.

## Current references

The root README, working rules, phase entry and adoption checklist name Korda-Design. Links from maintained documentation to older Design snapshots use the canonical repository URL while retaining the same commit and file path.

Repository comparisons and live API/archive requests in the existing research workflows use the new remote identity. Their triggers, branch restrictions, permissions, commit pins, evidence keys and local directory layouts stay unchanged. This maintenance does not dispatch a workflow or restart a research task.

## Preserved historical identities

| Location or reference | Why the earlier name remains |
| --- | --- |
| `docs/contracts/`, `docs/traceability/`, `docs/research/`, `docs/history/`, `verification/` and experiment evidence | Accepted contracts, reviews, source snapshots and raw outputs bind their original names and bytes to commits and hashes. |
| `english-translation-manifest.json`, `docs/current-scope.json`, `docs/api/*.json` and completed database overlay JSON | These record exact earlier source or acceptance inputs. Repository maintenance does not rebind their acceptance to changed bytes. |
| `NativeWeave-Design:` references and JSON repository keys | These identify the repository within the recorded evidence format. They are historical identity keys rather than current clone instructions. |
| Temporary `NativeWeave-Design` worktrees in verification tools | The unchanged historical validators resolve paths and contract bindings using that directory name at their frozen commits. |
| Legacy checkout paths, archive prefixes and collection directories in research workflows | Historical scripts and snapshots depend on the established layout. Only the live remote lookup uses Korda-Design. |
| Archived workflow copies under experiment provenance | These are the workflow bytes observed for earlier executions. They retain their original repository references. |
| `schemas/public-api-coverage.schema.json` `$id` | This is the existing schema identifier for the historical API coverage format; it is preserved with that format. |
| Historical `NativeWeave` package, type, tool and database names | Renaming this repository does not rename the product's earlier source or physical identifiers. |

The previous task narratives in [AGENTS.md](../AGENTS.md) and [CURRENT-PHASE.md](../CURRENT-PHASE.md) remain explicitly historical. New maintenance authorization comes from the current task section, while product behavior remains in the current contracts.

## Verification

Run these existing lightweight documentation gates from a full-history checkout:

```bash
python3 tools/verify_db_rename.py
python3 tools/verify_db_scope_history.py
```

The naming gate validates current guidance and replays DB-API-01, C++ migration and DB-Scope-01 checks at their immutable inputs. The history gate runs the original API, English translation and 21-contract acceptance checks, including their negative controls. Keep their frozen commits and original worktree names. Documentation checks do not claim new compiler, package, database, Native AOT or performance results.
