# Deliberately vulnerable refund adapter

The source is veltryq/fixtures/refund_vulnerable.py. Its
FixtureRefundService reads idempotency and balance state in one session, closes
that precheck session, then opens a separate locked write transaction. The
disposable vulnerable schema omits the unique idempotency index. A barrier
synchronizes two retries after their stale prechecks.

Run python -m veltryq.cli regression --implementation vulnerable. The expected
exit code is 1, with two persisted refunds totaling 20,000 minor units against
10,000 captured. This works on both the tested PostgreSQL and SQLite backends.

The API never selects this fixture. The prepared demo branch copies this exact
source into examples/demo/refund_candidate.py for the real GitLab MR.
