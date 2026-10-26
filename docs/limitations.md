# Scope and limitations

Implemented and exercised locally and in real GitLab CI:

- FastAPI synthetic payments, capture, refunds, retrieval, and history.
- SQLAlchemy persistence on PostgreSQL and SQLite.
- Transactional row locking, idempotency uniqueness, and atomic ledger writes.
- Reproducible concurrent duplicate-refund counterexample.
- Reviewed source repair recipe and a concrete unified patch.
- Identical declarative regression contract before and after repair.
- Per-refund/currency ledger-balance checks.
- HTML/JSON evidence, CI provenance mapping, and review/governance records.
- Pinned, hashed dependency sets and local security/quality checks.
- Container and Compose configuration.

See docs/verification.md for measured results and container verification status.

External execution completed:

- Public source, MIT detection, GitLab server CI Lint, and real MR pipelines.
- Native Duo flow registration, enablement, active mention trigger, and
  completed sessions with bot-authored reviews on both demo MRs.
- Signed-out public access to the repository, pipelines, and JSON evidence.

Remaining account actions:

- Review/upload the prepared video or record your own public YouTube demo.
- Team/eligibility details and final Devpost submission.
- Human remediation decisions; the demonstration MRs remain draft/unmerged.

See [live evidence](evidence-links.md) for exact records. An initial native
review could not independently read every non-JSON artifact through its tool;
those individual checks were labelled inconclusive. This does not expand the
supported adapter or claim general agent accuracy.

Intentional scope boundaries:

- One hash-matched synthetic refund adapter; no arbitrary source-code analysis.
- Repair uses a reviewed recipe rather than free-form generated code.
- Native agent quality/false-positive rates have not been measured.
- Index repair is verified with fresh schemas. Existing duplicate-row
  reconciliation, production migrations, and financial data recovery are excluded.
- API authentication, real processors, staging/production promotion, cloud
  deployment, telemetry, and the optional Google Cloud bonus are excluded.
- Python dependency audit and Bandit do not constitute an operating-system or
  complete container vulnerability assessment.
- Finite scenarios do not prove financial safety.
