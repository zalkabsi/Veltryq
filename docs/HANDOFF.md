# Finish the Veltryq submission

Deadline: **27 October 2026, 16:00 Asia/Riyadh (13:00 UTC).**

## Completed

- Public [Veltryq project](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq) in your provisioned hackathon workspace.
- Source committed and pushed to main; root MIT license detected by GitLab.
- GitLab CI server validation passed with no errors or warnings.
- Real main, vulnerable, and repaired pipelines passed.
- PostgreSQL evidence reproduced 20,000 refunded against 10,000 captured,
  then verified one 10,000 refund using the unchanged regression contract.
- Native [Duo flow](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/automate/flows/1019851) registered, enabled, and triggered on both MRs.
- Agent review notes posted with current source SHAs and actual CI links.
- [Vulnerable MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/1) and [repair MR !2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/2)
  remain draft and unmerged for a human decision.
- Narrated video draft, captions, and the Devpost description are prepared.

See [live evidence](evidence-links.md) and [verification](verification.md).
The original welcome issue belongs to the separate showcase onboarding project.
Your submission repository is **veltryq** in the same workspace group.

## 1. Review and publish the video

A narrated video draft and captions are included in the handoff/release assets:
**Veltryq-Demo.mp4** (2:49) and **Veltryq-Demo.srt**.
Download them from the [v0.2.0 release](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/releases/v0.2.0).
It uses actual execution records,
source/contract checks, original HTML evidence, and native session snapshots.
Narration is synthetic, and the explanatory pseudocode panel is labelled.
Review the draft before uploading, or use the recording plan below to replace
it with your own screen recording and narration.

1. Open [docs/demo.md](demo.md) for the complete narration and timed shot list.
2. Open MR !1, its completed Duo session, PostgreSQL evidence, the source patch,
   and MR !2 using [evidence-links.md](evidence-links.md).
3. Use your screen recorder to capture those actual pages. Show the vulnerable
   result (2 refunds / 20,000 minor units), the repair (1 / 10,000), the unchanged
   contract hash, and the agent's review note.
4. Trim waiting and keep the final duration **under three minutes**.
5. Upload to YouTube and set visibility to **Public**. Add the public project
   link to the video description.
6. Open the video in a signed-out window. Copy its URL into the Devpost entry
   and the Public YouTube row in evidence-links.md.

Your YouTube account is needed to upload. You can use the prepared video or
record your own version; YouTube is not connected to this workspace.

## 2. Submit on Devpost

1. Sign in at https://gitlab-transcend.devpost.com/ and open your project entry.
2. Set the project name to **Veltryq** and choose **Path A — Start Fresh**.
3. Use [submission.md](submission.md) for the prepared tagline, description,
   tools, and scope. Describe autonomy as **supervised**.
4. Add this public repository: https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq
5. Add the actual public YouTube URL from step 1. Link the live evidence page
   if the form offers a project website or additional-links field.
6. Complete your team, eligibility, and required personal fields. Review the
   event's required questions and terms in your own account.
7. Press **Submit** before the deadline. Verify that the entry is marked
   submitted and save the project URL or confirmation.

Devpost is not connected here, so no entry or final submission is claimed.
Deployment and observability are optional for this Path A entry; the optional
Google Cloud bonus is not claimed. A remediation merge is not needed to submit
this draft-MR demonstration.

## Optional: continue development locally

~~~bash
git clone https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq.git
cd veltryq
~~~

Use README.md for the documented commands. The latest portable handoff ZIP
also contains source history, demonstration branches, local verification, and
snapshots of the real GitLab evidence. It contains no login credentials.
