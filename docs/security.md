# Security boundaries

## Synthetic data and local access

The API is unauthenticated and handles generated payment IDs and integer
minor-unit amounts. It has no payment processor or real account data. Compose
binds the API to loopback and keeps PostgreSQL on its internal network. The API
always uses the repaired service; the insecure fixture runs only in the test
workflow.

## Transactions

PostgreSQL row locks serialize changes to the same payment. Refund lookup,
payload replay validation, limit checks, refund insertion, and both ledger
sides commit together. A unique database index protects the idempotency key.
SQLite uses an immediate write transaction for the same boundary.

Tests cover rollback after injected failures, conflicting replay, negative and
non-integer amounts, limits, unknown payments, and concurrent distinct keys.

## Agent authority

Repository files, diffs, descriptions, comments, patches, and tool results are
untrusted data. The flow's agents have read tools and one MR-note tool. They
have no general command, commit, branch, merge, or deployment tools.

A separate DeterministicStepComponent calls run_tests with a literal command.
The LLM cannot alter that argument. Its installed runtime comes from the
reviewed default branch, and Python isolated mode prevents importing MR-checkout
modules. Candidate source is hash-matched data; arbitrary candidate files or
LLM-generated patches are never imported.

The setup script is part of the default-branch trust boundary and runs before
GitLab's runtime restrictions. Review changes to agent-config.yml, lockfiles,
and the runtime before merging them. No secrets are embedded in the project.
Ordinary MR CI jobs should not receive protected write/deployment credentials.

## Evidence integrity

Unknown source, execution errors, missing artifacts, failed/pending CI, changed
MR heads, or unsupported runtime modifications must yield inconclusive review.
A confirmed result requires real persisted rows. The regression contract stays
byte-identical across candidate and repair execution. Reports contain hashes
and allow-listed CI provenance, not credential-bearing URLs.

The native agent compares the actual MR blob and source SHA with the evidence.
A built-in fixture result alone does not establish a defect in arbitrary MR
code. The final MR note requires human review before accepting any remediation.

## Checks and dependencies

Ruff, Bandit, dependency auditing, credential-pattern checks, functional tests,
and transaction/concurrency tests are configured. Their actual local results
are recorded in docs/verification.md. Lockfiles pin versions and artifact hashes.
The small credential-pattern script is not comprehensive secret detection.

Psycopg retains its LGPL license. See THIRD_PARTY_NOTICES.md before distributing
the image. The project does not claim full container/OS scanning or production
hardening.
