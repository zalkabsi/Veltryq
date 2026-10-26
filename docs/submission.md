# Devpost submission material

Paste [About Veltryq](about-project.md) into Devpost's **About the project**
field. It includes the inspiration, implementation, challenges, lessons, and
next steps in Markdown.

Real public GitLab pipelines and native Duo reviews are linked in
[evidence-links.md](evidence-links.md). Follow [HANDOFF.md](HANDOFF.md) to upload the prepared video or your own recording, add the public YouTube URL,
complete account details, and submit on Devpost.

## Entry fields

- Project name: Veltryq
- Tagline: Catch the financial bugs your tests can't see.
- Path: A — Start Fresh
- Autonomy: Supervised; the registered flow completed on both demonstration MRs
- Repository: https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq
- Demo: add the actual public YouTube URL, duration under three minutes
- Built with: Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, GitLab CI/CD,
  GitLab Duo Agent Platform, Docker

## Description

Refund code can pass ordinary tests and still duplicate money movement when
two network retries race a check-and-write sequence. Veltryq is a
financial-integrity workflow for synthetic payment applications.

The demonstration captures 10,000 minor units and synchronizes two identical
refund retries after the vulnerable precheck. Both persist, producing 20,000
minor units of refunds. A deterministic invariant engine records the actual
refund and ledger rows, identifies idempotency and refund-limit violations,
and generates a concrete source repair proposal.

The repair keeps the lookup, limit check, insertion, and accounting postings
inside one locked transaction and adds idempotency uniqueness. The exact same
declarative regression contract runs against the reviewed repaired source.
Ordinary scenarios, partial refunds, replay conflicts, concurrency, and
rollback behavior are checked as well.

The GitLab Duo custom flow inspects the MR, selects supported invariants,
starts a fixed deterministic test tool, reviews the source patch and matching
CI evidence, and posts one structured review note. The model cannot choose
shell commands or merge changes. A human reviews the outcome.

GitLab CI runs quality checks, unit/invariant tests, a real PostgreSQL scenario,
security checks, source/wheel packaging, and an evidence governance record.
HTML/JSON reports connect the observed state, source and contract hashes,
commit, pipeline, job, and artifacts.

## Technical differentiation

- Concrete counterexample from persisted state, with an unchanged regression.
- Hash-matched domain adapter and a reviewed, inspectable source repair recipe.
- PostgreSQL row locking, uniqueness, and atomic double-entry postings.
- Native Duo investigation and evidence review, with a fixed test command and
  human control over accepting the result.

## Scope and future work

This project supports one deliberately seeded refund adapter. It does not
generate or execute arbitrary patches, guarantee financial safety, migrate
populated ledgers, or connect to real payment services. Future work includes
additional domain adapters, precision/atomicity properties, broader measured
agent evaluation, and reviewed schema migration support.

## DevSecOps stage claims

Verify, Secure, Package, and Govern are implemented in the pipeline definition.
Duo performs MR impact analysis and reviews a generated repair proposal.
Real pipeline and native-session links are recorded in evidence-links.md.
Staging, cloud release, and telemetry are outside this submission.

## Evidence and remaining form fields

- Vulnerable MR: https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/1
- Repair MR: https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/2
- Native sessions, review notes, exact SHAs, pipelines and artifacts:
  [live evidence](evidence-links.md)
- Public YouTube URL
- Team information, eligibility confirmation, and final Devpost confirmation

## Optional form sections

Inspiration: financial business rules can fail across concurrent requests even
when individual functions pass ordinary tests.

Hardest technical issue: placing database locks around the complete decision
and write boundary while keeping a deterministic, reproducible counterexample.

What was learned: reproducible state and provenance make a financial review
more useful than an unverified suspicion or an unexplained generated patch.

Next steps: expand the explicit adapters and evaluate a larger native-agent
dataset before claiming broader detection coverage.
