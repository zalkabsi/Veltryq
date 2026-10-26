# Final video plan

Target 2:45–2:55, public YouTube, under three minutes. Real GitLab pipelines
and completed native sessions are linked in [evidence-links.md](evidence-links.md).
Use those actual pages, logs, and reports.

| Time | Capture |
|---|---|
| 0:00–0:20 | Veltryq title, API/history, and passing ordinary baseline |
| 0:20–0:40 | Vulnerable demo MR and native Duo session starting |
| 0:40–1:10 | Fixed test tool and evidence: two 100 USD refunds against 100 USD captured |
| 1:10–1:40 | Actual source patch: lock includes checks/writes, plus uniqueness proposal |
| 1:40–2:10 | Repair MR, identical contract hash, PostgreSQL and existing tests passing |
| 2:10–2:35 | HTML/JSON report, real commit/pipeline/artifact links, posted agent note |
| 2:35–2:55 | Human approval boundary and supported-adapter scope |

## Prepared video draft

The [v0.2.0 release](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/releases/v0.2.0) and handoff include a 2:49
Veltryq-Demo.mp4, matching captions, the full
transcript, and a manifest with the actual session links. The draft combines
actual CLI results, PostgreSQL CI evidence, original report footage, and native
review snapshots. Narration is synthetic. Review it before uploading; use the
shot list to replace it with your own recording if preferred.

## Narration

“Veltryq catches financial defects that ordinary tests can miss. This synthetic
service captures a hundred dollars and accepts refunds with idempotency keys.
Its sequential baseline passes, including replaying the same request.

Here is a merge request containing the deliberately vulnerable refund adapter.
GitLab Duo reads the diff and identifies the idempotency, refund-limit, and
ledger-balance checks.

The flow starts a fixed test command. Two concurrent retries pass the same
stale precheck. The database now contains two hundred dollars of refunds
against a hundred-dollar capture. These numbers come from persisted rows.

Veltryq generates a concrete repair proposal. The lock now covers the
idempotency lookup, balance check, insertion, and both ledger postings.
Database uniqueness provides an additional guard.

The regression contract is unchanged. Against the repaired source it persists
one refund, while legitimate partial refunds and replay behavior still pass.
The PostgreSQL pipeline also checks rollback after accounting failures.

This report connects the observed state, patch, test-contract hash, source
commit, and pipeline artifacts. Duo checks the evidence against the current
merge request and posts its review. A human decides whether to accept the fix.

This demonstration supports one reviewed synthetic adapter. It is a finite
regression check, not a proof that arbitrary financial software is safe.
Veltryq brings reproducible financial evidence into code review.”

## Capture checklist

- Use the actual service-account handle and real session/pipeline URLs.
- Show vulnerable and repaired source commits and an unchanged contract hash.
- Keep text readable; zoom the patch and report rather than scrolling quickly.
- Record the completed workflow and trim waiting time; describe edits honestly.
- Check the final duration is below 3:00 and the YouTube visibility is Public.
- Put the public repository link in the description and Devpost entry.
- Record and upload from your computer; a screen recorder and YouTube account
  are not connected here. GitLab configuration and native execution are complete.
