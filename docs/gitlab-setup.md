# GitLab setup and live verification

## Configured project

- Project: [gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq)
- Project ID: 88110050; namespace ID: 145719960.
- Visibility: public. Default branch: main. License detected: MIT.
- Shared runners enabled; authenticated CI Lint returned valid with no warnings.
- [Registered catalog flow](https://gitlab.com/explore/ai-catalog/flows/1019851).
- [Enabled project flow](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/automate/flows/1019851); released version 1.0.2.
- Active mention trigger account:
  `@ai-veltryq-financial-integrity-review-gitlab-ai-hackathon`.

The workspace's actual permissions allowed catalog administration without a
role change. Onboarding project permissions and flow permissions are distinct.

## Demonstration

1. Open [MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/1) for the vulnerable candidate. Its pipeline
   succeeds with the candidate regression's expected allowed exit 1. Other
   execution errors remain blocking.
2. Open its native session and review note in [evidence-links.md](evidence-links.md).
   The deterministic command reproduces the known source adapter; the agent
   checks current source identity and the exact PostgreSQL CI evidence.
3. Open [MR !2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/merge_requests/2) for the repaired candidate. All its jobs pass.
   The correct result is selected_checks_passed with no new violation or patch.
4. Inspect the four native components: impact analysis, fixed test command,
   evidence review, and publication of one MR note.
5. Keep the draft demonstrations unmerged. A human owns remediation decisions.

To deliberately start another review, post the following in the relevant MR:

~~~text
@ai-veltryq-financial-integrity-review-gitlab-ai-hackathon Review this MR with Veltryq.
~~~

Each mention creates another native session. Existing completed sessions already
satisfy the demonstration; there is no need to rerun merely to record the video.

## Runtime and authority

GitLab reads .gitlab/duo/agent-config.yml from main. Its setup installs the
trusted default branch in an independent environment. The deterministic step
calls one literal Python command in isolated mode. Candidate source is read as
data and must match a reviewed hash. LLM components have no command, commit,
merge, or deployment tool. Unsupported source, stale evidence, or unavailable
required evidence is inconclusive.

A CI report's gitlab_duo_execution: not_recorded describes that CI execution.
The separate native session and bot-authored review are the Duo records.

Official references checked October 26, 2026:

- https://docs.gitlab.com/user/duo_agent_platform/flows/custom/
- https://docs.gitlab.com/user/duo_agent_platform/flows/custom_flows_schema/
- https://gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/-/blob/main/docs/flow_registry/v1.md
- https://docs.gitlab.com/user/duo_agent_platform/agents/tools/
- https://docs.gitlab.com/user/duo_agent_platform/flows/execution/agent-config-yaml/
