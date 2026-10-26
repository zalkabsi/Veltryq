# Reviewed repaired refund adapter

The source is veltryq/fixtures/refund_repaired.py; the normal API implementation
is app/refunds.py. The transaction includes the payment lock, idempotency lookup,
balance validation, refund insertion, and both ledger postings. PostgreSQL
uses FOR UPDATE; SQLite uses BEGIN IMMEDIATE. The repaired schema adds unique
(payment_id, idempotency_key).

Run python -m veltryq.cli regression --implementation repaired. The same
concurrent retry contract persists one refund and replays its prior result.
The workflow exports an actual source/index proposal in repair.patch and
checks the exact repaired source hash.

Verification uses fresh schemas. Existing duplicate rows require a reviewed
reconciliation/migration plan before adding uniqueness to a populated ledger.
