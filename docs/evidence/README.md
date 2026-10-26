# Preserved execution evidence

These files were downloaded from the actual matching GitLab PostgreSQL jobs.
They preserve the original reports after the 30-day CI artifact retention
period. They contain synthetic financial records only.

- [vulnerable.json](vulnerable.json): MR !1, two refunds totaling 20,000 before
  the proposed repair; one refund totaling 10,000 afterward.
- [repaired.json](repaired.json): MR !2, one refund before and after; no new bug.
- [repair.patch](repair.patch): the original CI-generated source/index proposal.
- [vulnerable-regression.json](vulnerable-regression.json) and
  [repaired-regression.json](repaired-regression.json): identical contracts.
- [verification.json](verification.json): separately observed source/contract/
  patch hash checks, repair-MR source agreement, and actual named PostgreSQL
  test results obtained from GitLab's structured pipeline test report.
- [video-manifest.json](video-manifest.json): prepared video duration, file hash,
  and the actual source/session references used in the walkthrough.
- [public-access.json](public-access.json): signed-out endpoint observations.
- [native-sessions.json](native-sessions.json): actual native session statuses,
  linked bot-authored reviews, and the platform-recorded deterministic command
  and result. An individual review agent has no shell; the preceding
  deterministic flow component executes the test code.

The reports retain their original CI provenance and `gitlab_duo_execution:
not_recorded` field. Separate native session/review-note records are linked in
[the live evidence index](../evidence-links.md). The original reports' generic
`remediation.file` metadata names app/refunds.py; the concrete patch and
repair_proposal.target_path correctly name examples/demo/refund_candidate.py.
That metadata was corrected in source commit 96c41bb.

GitLab's notes API requires authentication even for this public project. The
native session interface can also require sign-in. The committed session and
review snapshots provide readable evidence alongside the original GitLab links.

These are finite checks of one reviewed synthetic adapter. Human review is
required; no remediation was merged or deployed.
