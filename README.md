# Veltryq

**Catch the financial bugs your tests can't see.**

Veltryq investigates a synthetic refund race: ordinary sequential tests pass, but
two concurrent retries can refund 20,000 minor units against a 10,000-unit payment.
A bounded financial adapter reproduces the discrepancy, generates a concrete
source patch, verifies the same regression contract against the repair, and
produces HTML/JSON evidence for human review.

## Current status

The project is public with a detected MIT license. Real GitLab CI pipelines
passed, the registered Duo flow ran natively, and the agent posted reviews on
both demonstration MRs. The vulnerable candidate produced two refunds; the
repaired candidate produced one. Both draft MRs remain open for human review.

- [Vulnerable MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/1) · [Repair MR !2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/2)
- [Demo video and portable handoff](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/releases/v0.2.0)
- [Enabled Duo flow](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/automate/flows/1019851) · [Live evidence](docs/evidence-links.md)
- [Verification](docs/verification.md) · [Final submission steps](docs/HANDOFF.md)
- [About the project / Devpost story](docs/about-project.md)

A narrated video draft is prepared. Public YouTube upload and final Devpost
submission still require your accounts. Deadline: **27 October 2026, 16:00 Asia/Riyadh (13:00 UTC).**

## Run the complete demonstration

Python 3.12:

~~~bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-deps --no-build-isolation -e .
python -m veltryq.cli workflow --out artifacts/sqlite
~~~

Open `artifacts/sqlite/evidence.html`. The output directory also contains:

- `evidence.json`: actual rows, invariant results, execution trace, and provenance.
- `regression.json`: a validated, non-executable test contract.
- `repair.patch`: source and uniqueness-index proposals for the known fixture.
- `proposal/`: the proposed source after applying the reviewed replacement.
- `review.md`: a factual human review handoff.

The contract SHA-256 must remain identical before and after repair. Unknown
candidate source hashes produce an inconclusive result and are never imported.

## PostgreSQL and Docker

~~~bash
mkdir -p artifacts
docker compose up --build -d db api
docker compose --profile tools run --rm workflow
~~~

The API is available at http://127.0.0.1:8000/docs. The database is internal to
Compose. The workflow writes `artifacts/postgresql/evidence.html` and creates
a separate disposable PostgreSQL schema for every scenario. The sample database
credentials are for this local synthetic sandbox.

For another host UID/GID, set `VELTRYQ_UID` and `VELTRYQ_GID` before running the
workflow service. Stop local services with `docker compose down`. The named
database volume persists until explicitly removed.

To use a disposable PostgreSQL database without Compose, configure
`VELTRYQ_TEST_DATABASE_URL` with a `postgresql+psycopg://` URL and run the same
workflow command. The user needs permission to create and drop the generated
`veltryq_<uuid>` test schemas. Existing application data is never used as a
scenario fixture.

## Synthetic API

~~~bash
uvicorn app.main:app --reload
~~~

Create a payment with `POST /payments` and
`{"amount_minor":10000,"currency":"USD"}`, then capture it with
`POST /payments/{id}/capture`. Request a refund through
`POST /payments/{id}/refunds` with an `Idempotency-Key` header and
`{"amount_minor":2500}`. View `GET /payments/{id}/history` or
`GET /refunds/{refund_id}`.

The API always uses the repaired service. PostgreSQL locks the payment row across
the checks and writes; SQLite uses `BEGIN IMMEDIATE`. Both use a database unique
index on payment/idempotency key. All amounts are bounded integer minor units.

Set `VELTRYQ_DATABASE_URL` for PostgreSQL, or `VELTRYQ_DB_PATH` for a persistent
SQLite file. Without either, the API uses a private temporary database that is
discarded at shutdown. The API is unauthenticated and intended for local
synthetic records.

## Test and inspect

~~~bash
pytest -q
ruff check app veltryq tests scripts
bandit -q -r app veltryq
pip-audit --require-hashes -r requirements-dev.lock
python scripts/verify_configs.py
~~~

`tests/test_postgresql.py` runs when the disposable PostgreSQL URL is configured.
It covers the same service contract as SQLite, including concurrent distinct
keys, uniqueness, conflicting replay, partial refunds, and rollback after a
ledger failure.

The vulnerable regression exits 1 after recording the confirmed discrepancy;
the repaired regression exits 0; incomplete execution exits 2:

~~~bash
python -m veltryq.cli regression --implementation vulnerable
python -m veltryq.cli regression --implementation repaired
python -m veltryq.cli regression --implementation repaired --spec artifacts/sqlite/regression.json
~~~

## GitLab Duo workflow

The registered flow has four steps:

1. A Duo agent reads the MR diff, identifies the supported operation, and selects invariants.
2. A deterministic `run_tests` step executes one literal command to reproduce,
   propose a bounded source repair, and verify the unchanged regression.
3. A Duo agent checks the patch, candidate blob identity, current MR SHA, and
   real PostgreSQL pipeline artifacts.
4. A Duo agent posts one evidence-based review note for a human decision.

The test executable is installed from the reviewed default branch into an
independent virtual environment. Python isolated mode prevents imports from the
MR checkout. Candidate files are read as data and must match a reviewed hash.
The model receives no shell, commit, merge, or deployment tool.

The fixed native command uses `workflow --summary` so the complete verdict and
source/contract hashes fit within GitLab's tool response limit. Full persisted
rows and the source patch remain in the report files. Ordinary CLI/CI commands
continue to print the complete JSON report.

See [GitLab setup](docs/gitlab-setup.md). Pushing YAML does not register a flow;
the project must enable it through GitLab. A local workflow execution does not
establish that a native Duo session ran.

~~~mermaid
flowchart LR
  MR[Merge request] --> A[Duo impact analysis]
  A --> T[Fixed deterministic test tool]
  MR --> CI[GitLab CI]
  CI --> PG[(Disposable PostgreSQL)]
  CI --> E[JUnit, patch, HTML and JSON evidence]
  T --> V[Duo evidence and repair review]
  E --> V
  V --> N[MR review note]
  N --> H[Human decision]
~~~

## Scope and submission

The supported adapter is a deliberate teaching fixture. Repair generation uses
a reviewed source recipe, not unrestricted LLM code generation. The result is a
finite executable counterexample and regression check, not a proof of arbitrary
financial safety. Schema repair is verified on a fresh sandbox; reconciliation
of pre-existing duplicate transactions is outside scope.

See [architecture](docs/architecture.md), [security](docs/security.md),
[limitations](docs/limitations.md), [demo](docs/demo.md), and
[submission material](docs/submission.md). Path A deployment is optional; cloud
deployment and observability are deferred.

## License

Veltryq source is MIT licensed. Dependencies retain their licenses, including
Psycopg's LGPL terms. See [LICENSE](LICENSE),
[third-party notices](THIRD_PARTY_NOTICES.md), and [license review](docs/licenses.md).
