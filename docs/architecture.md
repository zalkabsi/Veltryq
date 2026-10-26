# Architecture

## Financial application

FastAPI exposes a synthetic payment/capture/refund service. SQLAlchemy models
use integer minor units and explicit payment states. PostgreSQL is the primary
transaction backend; SQLite supports a portable local run.

The repaired service locks the payment row with SELECT FOR UPDATE before
idempotency lookup, refundable-balance validation, insertion, and ledger posting.
SQLite obtains its write transaction before those checks. A unique database
index on (payment_id, idempotency_key) is an additional guard. A failed posting
rolls back the refund, balance update, and ledger changes together.

The intentionally vulnerable source fixture performs the precheck in an earlier
session, then synchronizes callers at a barrier before opening the write
transaction. Its disposable schema omits idempotency uniqueness. Both calls
therefore approve against stale state and persist a refund. The API never
selects this fixture.

## Bounded workflow

`veltryq workflow` maps supported paths to invariants, validates the candidate
source hash, runs ordinary baseline assertions, serializes a regression
contract, and executes it against the candidate. A confirmed known defect
activates a reviewed source repair recipe. The proposal includes a unified
source diff and uniqueness-index SQL.

The proposed replacement is written to a separate tree and checked against the
reviewed repaired source hash. The same contract bytes then execute against the
identical installed repair template. Tests independently apply the exported
unified diff with git apply and check the resulting source hash. Unknown source
and incomplete execution yield inconclusive results.

This is deliberate domain adaptation, not general program synthesis. The
regression contract is data validated by Pydantic and cannot contain commands.

## Database isolation

Each PostgreSQL scenario creates a random veltryq_<uuid> schema and drops only
that generated schema afterward. SQLite scenarios use private temporary files.
No live payment or application database rows are used as scenario input. Tests
use READ COMMITTED PostgreSQL semantics and transaction-scoped row locks.

Schema initialization supports a fresh synthetic database. The emitted index
SQL is a proposal for review; it is not an automated migration of a populated
ledger. Alembic migrations are unnecessary for this fresh-schema demonstration.

## Native GitLab flow

The Flow Registry v1 definition chains impact analysis, a deterministic fixed
test tool, evidence review, and publication of one MR note. The setup script
installs code from origin/main into a separate environment. The fixed command
uses Python -I so code in the MR checkout cannot override that runtime.

The agents read the MR at a specific SHA, compare its candidate blob ID with the
tested source, and read actual pipeline/job artifacts at the matching commit.
They must mark other runtime modifications, stale evidence, unavailable jobs,
and unsupported sources inconclusive. No agent can merge or deploy.

The local CLI and CI jobs work independently of the LLM. The registered native
flow has completed on both demonstration MRs. Its session links and posted
notes are separate records from the CI-generated evidence; see evidence-links.md.

## CI and provenance

The pipeline runs quality checks, ordinary/unit tests, a targeted failure and
repaired regression, full workflows on SQLite and PostgreSQL, security checks,
wheel/source packaging, and an artifact-based governance summary.

Reports allow-list CI commit, MR, pipeline, job, and artifact URLs. Credentials
and database URLs are excluded. Local reports leave unavailable GitLab fields
empty. Governance records preserve hashes of the actual reports and packages
and leave the human decision pending.
