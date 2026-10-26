# Live evidence record

Observed **26 October 2026** from actual GitLab records. The project and both
MR pipelines/evidence endpoints returned HTTP 200 without authentication.
The notes API requires authentication; committed native-review snapshots below
provide readable copies alongside the original session and note links.

## Source and native flow

| Record | Actual link / result |
|---|---|
| Public MIT project | [gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq) |
| Published application commit | [b380d338fda8a237518a884d7cfe327b56b535d8](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/commit/b380d338fda8a237518a884d7cfe327b56b535d8) |
| Reporting/flow correction | [96c41bb284afe60998572a66dbb8e30a36b90686](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/commit/96c41bb284afe60998572a66dbb8e30a36b90686) |
| Main application pipeline | [2989968422 — success](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/pipelines/2989968422) |
| Correction pipeline | [2990849894 — success](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/pipelines/2990849894) |
| Compact native-output commit | [5e3d6ddf1ab89aec2285d3ab6ea77b64051414b7](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/commit/5e3d6ddf1ab89aec2285d3ab6ea77b64051414b7) |
| Compact-output pipeline | [2990899088 — success](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/pipelines/2990899088) |
| Enabled native flow | [Veltryq Financial Integrity Review, 1.0.2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/automate/flows/1019851) |
| Public flow catalog | [Flow 1019851](https://gitlab.com/explore/ai-catalog/flows/1019851) |

Actual mention account: `@ai-veltryq-financial-integrity-review-gitlab-ai-hackathon`.
The mention trigger creates a separate native flow session; CI does not claim
to have invoked Duo. The source was initially pushed into a new empty project;
there was no source merge request to merge.

## Vulnerable demonstration

- [Draft MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/1); source SHA `db1c0f316a56471ee5fa01d21f4555d4fbb2b7a7`.
- [MR pipeline 2990010876](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/pipelines/2990010876): **success with the
  candidate regression's expected allowed failure**. Infrastructure/unsupported
  errors are not allowed to fail.
- [PostgreSQL job 17471135560](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/jobs/17471135560): **success**, 26 tests and 6 subtests passed.
- [HTML evidence](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/jobs/17471135560/artifacts/file/artifacts/postgresql/evidence.html),
  [JSON evidence](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/jobs/17471135560/artifacts/file/artifacts/postgresql/evidence.json),
  [source/index patch](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/jobs/17471135560/artifacts/file/artifacts/postgresql/repair.patch),
  [regression contract](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/jobs/17471135560/artifacts/file/artifacts/postgresql/regression.json).
- Baseline passes; the candidate persists **2 refunds / 20,000 minor units**
  against 10,000 captured. The proposed repair persists **1 / 10,000**.
- Verdict: `confirmed_violation_repaired`. Idempotency and refund limit fail
  before the repair; ledger balance remains balanced and is not alone sufficient.

## Repaired demonstration

- [Draft MR !2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/2); source SHA `4d50b650b74e601311438fd90474a0b4f6b82aed`.
- [MR pipeline 2990010971](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/pipelines/2990010971): **success; all nine jobs pass**.
- [PostgreSQL job 17471136492](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/jobs/17471136492): **success**, 26 tests and 6 subtests passed.
- [HTML evidence](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/jobs/17471136492/artifacts/file/artifacts/postgresql/evidence.html),
  [JSON evidence](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/jobs/17471136492/artifacts/file/artifacts/postgresql/evidence.json),
  [regression contract](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/jobs/17471136492/artifacts/file/artifacts/postgresql/regression.json).
- The candidate already contains the repair: **1 refund / 10,000 minor units**
  both before and after. Correct verdict: `selected_checks_passed`, no new
  confirmed violation and no new repair.patch artifact.

## Completed native Duo reviews

- Vulnerable MR !1: [completed native session 10073722](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/automate/agent-sessions/10073722) · [agent review note](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/1#note_4092617506).
- Repaired MR !2: [completed native session 10073724](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/automate/agent-sessions/10073724) · [agent review note](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/2#note_4092615627).

Each session completed analysis, the literal deterministic test command,
evidence review, and publication of one note by the configured flow account.
The original reviews' individual access limitations remain visible. Flow 1.0.1
adds the structured test_report check and correct classification of repaired
candidates. Version 1.0.2 returns a compact complete deterministic-tool result
within the platform response limit. Session and note snapshots are preserved in
[native-sessions.json](evidence/native-sessions.json).

## Reproducibility and preservation

- Contract SHA-256, identical in both MRs and before/after:
  `a43cd55616c884a1e6e65d5c63bee0d78d8456009c87af27cd0155c6af0cae9f`.
- Vulnerable source SHA-256: `5e4124ea51d3cdd1fc41e063f7bddf3b51e740bb7c081695662f6c956a8dd846`.
- Repaired source SHA-256: `c58eb08706b0f471f65136d49b6a8c0ffa0557200add5a53f799867034c11498`.
- Actual downloaded patch SHA-256: `003faa4ce2c4067e1c4560dd252e7bca4f9c22c35ad413abf4ff8f275361c576`.

[Preserved CI reports and patch](evidence/README.md) retain their original
source SHAs and CI fields. [Independent API verification](evidence/verification.json)
confirms contract/patch hashes, repair-MR source agreement, and actual named
PostgreSQL test results. CI artifacts expire after 30 days; these committed
snapshots remain available. The records concern one known synthetic adapter,
not arbitrary code or a proof of financial safety.

## Remaining human/account actions

| Item | Status |
|---|---|
| Human remediation decision | Required; both MRs remain draft and unmerged |
| Video draft | [v0.2.0 release](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/releases/v0.2.0); 169.423 seconds, H.264/AAC, synthetic narration |
| Public YouTube URL | Upload the reviewed draft or your own recording from your account |
| Devpost entry and submission confirmation | Complete and submit from your account |

[HANDOFF.md](HANDOFF.md) contains the exact final steps. Deadline:
**27 October 2026, 16:00 Asia/Riyadh (13:00 UTC).**
