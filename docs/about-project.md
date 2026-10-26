# About Veltryq

## Inspiration

A passing test suite can still miss a financial bug. Two refund requests might
each look valid while, together, they refund more money than was captured.

Veltryq grew from that problem: how can code review include reproducible
evidence that financial rules hold under concurrent requests?

## What it does

Veltryq investigates a deliberately vulnerable synthetic refund service. Its
ordinary sequential baseline passes, but two concurrent retries produce
**200 USD in refunds against a 100 USD payment**.

The workflow checks three financial rules:

- The same retry key must not create duplicate refunds.
- Total refunds must not exceed the captured amount.
- Refund ledger entries must balance.

It records the persisted results, produces a concrete repair proposal, and runs
the **same regression contract** against the repaired implementation.

A native GitLab Duo flow reviews the merge request, starts a fixed verification
command, checks matching PostgreSQL CI evidence, and posts a review for a human
decision.

## How I built it

I used **Python, FastAPI, SQLAlchemy, PostgreSQL, SQLite, and Docker**. Monetary
values use integer minor units.

The repair places the idempotency lookup, refund-limit validation, refund
insertion, balance update, and ledger postings inside one transaction.
PostgreSQL row locking and database uniqueness provide additional protection.

GitLab CI runs quality checks, tests, PostgreSQL verification, security checks,
packaging, and an evidence governance step. HTML and JSON reports connect
results to the source commit, regression contract, patch, pipeline, and job.

The verification engine supports reviewed source adapters and repair recipes.
Duo's agent components cannot choose shell commands, commit changes, merge,
or deploy.

## Challenges I faced

Making the race reproducible required synchronizing both requests after the
vulnerable precheck. The repair then had to protect the complete
decision-and-write sequence while preserving legitimate partial refunds and
retry behavior.

Another challenge was keeping evidence tied to the exact merge request being
reviewed. Source hashes and commit-specific artifacts prevent unrelated results
from being treated as verification.

GitLab also truncated long tool responses. I added compact output containing
complete verdicts and hashes while preserving detailed records in the report
files.

## What I learned

A balanced ledger can still describe an incorrect financial outcome. Accounting
balance, refund limits, and retry safety need separate checks.

I also learned that useful AI-assisted review depends on reproducible
execution, precise source references, and clear limits on what the evidence
establishes.

## What's next

Veltryq currently covers one synthetic refund adapter. Next steps include more
reviewed financial adapters, broader concurrency scenarios, and a larger
evaluation of native agent reviews.

The working demonstration includes passing GitLab pipelines and completed Duo
reviews on both demonstration MRs. Both remain draft and unmerged: a human
owns the remediation decision.
