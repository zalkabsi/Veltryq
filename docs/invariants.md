# Built-in invariants

| ID | Property | Deterministic check |
|---|---|---|
| `FIN-IDEMPOTENCY` | One refund posting per payment and idempotency key | Two synchronized retries; count persisted refund rows |
| `FIN-REFUND-LIMIT` | Cumulative refunds do not exceed capture | Compare persisted refund minor units with captured amount |
| `FIN-LEDGER-BALANCE` | Debits equal credits for each posting currency | Sum debit and credit minor units |

The checks are built-in and selected by an explicit source-path mapping. They
run against one synthetic concurrency scenario. A reproduced violation is
reported as confirmed for that scenario. Unmatched paths are inconclusive.
Passing these checks is not a proof that arbitrary financial code is safe.

All amounts are positive integers in currency minor units. The synthetic API
accepts USD, EUR, and SAR; this project does not implement currency conversion
or generalized ISO currency metadata.
