# GitLab Duo integration

Source files:

- .gitlab/duo/flows/veltryq_financial_review.yml
- .gitlab/duo/agent-config.yml

The Flow Registry v1 definition chains impact analysis, one literal
DeterministicStepComponent calling run_tests, source/evidence review, and a
single MR note. LLM components receive no shell, branch, commit, merge, or
deployment tools. The fixed test command uses a default-branch installation
with Python isolated mode.

The public [Veltryq project](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq) has real passing pipelines and an enabled
[native flow](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43715013/veltryq/-/automate/flows/1019851). The mention account is
`@ai-veltryq-financial-integrity-review-gitlab-ai-hackathon`.
Both demonstration MRs have completed native sessions and bot-authored reviews.

See [live evidence](../../docs/evidence-links.md),
[GitLab setup](../../docs/gitlab-setup.md), and
[submission steps](../../docs/HANDOFF.md). Pushing a YAML definition alone does
not register a flow; catalog registration and project enablement were completed
separately through GitLab.
