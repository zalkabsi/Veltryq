# Verification results — 26 October 2026

The local and container checks below were executed. Real GitLab CI and native
Duo sessions also completed; their records are listed separately below.

| Check | Observed result |
|---|---|
| Complete test suite with PostgreSQL configured | 44 passed, 12 subtests passed |
| PostgreSQL service contract | 12 tests, including raw uniqueness and transaction rollback |
| Repeated concurrent scenarios | 40/40 expected outcomes, no request errors |
| Ruff lint and formatting | Passed |
| Compact CLI and workflow change checks | 15 passed, 2 subtests passed; output below 3,600 bytes for both known sources |
| Bandit, app and engine | 0 findings |
| Pinned Python development/runtime dependency audit | 0 known vulnerabilities reported |
| Configured credential-pattern scan | No matches |
| Docker image | Built successfully as a non-root runtime |
| Real container API | 6 smoke checks passed |
| Compose PostgreSQL workflow | 20,000 minor units before / 10,000 after |
| SQLite workflow | 20,000 minor units before / 10,000 after |
| Standalone installed wheel, Python isolated mode | Workflow passed from a directory containing a shadow package |
| Exported source patch | Applied independently by tests; resulting source hash matched repair |
| Source and wheel package | Built successfully |
| Offline CI/flow structure and authority checks | Passed |
| Authenticated GitLab server CI Lint | valid: true; no errors or warnings |
| Real GitLab CI | Main and both MR pipelines succeeded |
| Native Duo | Both sessions finished and posted bot-authored MR reviews |
| Video draft | 169.423 seconds; H.264/AAC decoded to completion; 37 caption cues |
| Signed-out public API checks | Repository, both pipelines, and PostgreSQL evidence: HTTP 200 |

## Environment

- Local Python: 3.12.14.
- Container Python: 3.12.15.
- PostgreSQL: 17.11, disposable schemas in a local Docker service.
- SQLite: 3.53.1 in the local Python runtime.
- Package/runtime: Veltryq 0.2.0, pinned dependency hashes in both lockfiles.

The installed-runtime smoke demonstrated the executable and import isolation.
The later compact-output CLI checks preserve the full report while returning
complete verdicts/hashes within the native tool response limit. Local checks
do not invoke GitLab Duo or substitute for the separate native sessions.

The repeated scenario record contains ten vulnerable and ten repaired runs on
each backend. This is engine reliability evidence, not measured native-agent
accuracy or a general proof of financial safety.

## Detailed local records

The portable handoff includes these actual artifacts:

- artifacts/verification/junit.xml
- artifacts/verification/reliability.json
- artifacts/verification/bandit.json
- artifacts/verification/pip-audit.json
- artifacts/verification/dependencies.json
- artifacts/verification/container-smoke.json
- artifacts/verification/installed-runtime.json
- artifacts/verification/gitlab-ci-lint.json
- artifacts/packages/manifest.json
- artifacts/sqlite and artifacts/postgresql HTML/JSON/patch reports

The handoff bundle records the committed source and two demonstration branches.
The API uses the repaired path on every branch. The intentionally vulnerable
candidate is confined to a synthetic teaching adapter.

## Real GitLab execution

| Record | Observed result |
|---|---|
| Initial main pipeline 2989968422 | Success at b380d338fda8a237518a884d7cfe327b56b535d8 |
| Correction pipeline 2990849894 | Success at 96c41bb284afe60998572a66dbb8e30a36b90686 |
| Compact-output pipeline 2990899088 | Success at 5e3d6ddf1ab89aec2285d3ab6ea77b64051414b7 |
| MR !1 pipeline 2990010876 | Success; candidate_regression has the expected allowed failure |
| MR !2 pipeline 2990010971 | Success; all nine jobs passed |
| PostgreSQL service suite, each MR | 26 passed, 6 subtests passed |
| Structured combined test report, MR !1 | 58 passed, 12 skipped, 0 failures/errors |
| Vulnerable PostgreSQL job 17471135560 | 2 refunds / 20,000 before; 1 / 10,000 after |
| Repaired PostgreSQL job 17471136492 | 1 / 10,000 before and after; no new violation |
| Native sessions 10058926 and 10058927 | FINISHED; analysis, fixed tool, verification, and MR note observed |
| Updated repaired-candidate session 10073040 | FINISHED on flow 1.0.1; correct selected-check verdict and named PostgreSQL test results |
| Final native sessions 10073722 and 10073724 | FINISHED on flow 1.0.2; complete compact tool JSON, exact candidate blobs, and correct before/after verdicts |

The 12 skips belong to the unit job without a PostgreSQL service; the separate
PostgreSQL job executes those service cases. Named passing cases cover
conflicting replay, partial-refund limits, concurrent distinct keys, database
uniqueness, capture rollback, and refund/ledger rollback. GitLab's structured
pipeline test_report exposes those actual results.

The first native reviews reported some evidence-access limitations. Version
1.0.1 uses the structured test report and distinguishes an already repaired
candidate from a newly reproduced defect. See [live evidence](evidence-links.md)
for the latest native sessions and notes, immutable source SHAs, artifact
links, and durable evidence snapshots. CI reports are preserved as originally
generated; native-session records are separate.

## Remaining account steps

Record/upload the final public YouTube video and submit the prepared Devpost
entry. [HANDOFF.md](HANDOFF.md) gives the exact steps. No final video or Devpost
submission is claimed until those account actions produce actual records.
