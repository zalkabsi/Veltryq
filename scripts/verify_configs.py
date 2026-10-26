"""Offline structure and authority checks; GitLab server validation is separate."""

from pathlib import Path

import yaml

flow = yaml.safe_load(Path(".gitlab/duo/flows/veltryq_financial_review.yml").read_text())
if flow.get("version") != "v1" or flow.get("environment") != "ambient":
    raise SystemExit("Unsupported flow version/environment.")
components = {component["name"]: component for component in flow["components"]}
prompts = {prompt["prompt_id"] for prompt in flow["prompts"]}
for component in components.values():
    if component["type"] == "AgentComponent":
        if component["prompt_id"] not in prompts:
            raise SystemExit("Missing prompt definition.")
        if any(
            tool in {"run_command", "run_tests", "create_commit", "create_branch"}
            for tool in component.get("toolset", [])
        ):
            raise SystemExit("LLM components must not receive command/commit tools.")
    elif component["type"] == "DeterministicStepComponent":
        bindings = component["inputs"]
        if component["tool_name"] != "run_tests" or len(bindings) != 1:
            raise SystemExit("Only the fixed deterministic test step is allowed.")
        expected = (
            "/tmp/veltryq-agent-runtime/bin/python -I -m veltryq.cli workflow "
            "--out /tmp/veltryq-agent-evidence --paths examples/demo/refund_candidate.py --summary"
        )
        if bindings[0] != {"from": expected, "as": "command", "literal": True}:
            raise SystemExit("Deterministic command is not the reviewed literal.")
    else:
        raise SystemExit("Unexpected component type.")
for router in flow["routers"]:
    if router["from"] not in components or router["to"] not in {*components, "end"}:
        raise SystemExit("Router refers to an unknown component.")
agent = yaml.safe_load(Path(".gitlab/duo/agent-config.yml").read_text())
if not isinstance(agent.get("image"), str) or not isinstance(agent.get("setup_script"), list):
    raise SystemExit("Invalid agent execution structure.")
ci = yaml.safe_load(Path(".gitlab-ci.yml").read_text())
if ci[".veltryq_job"].get("rules") != [{"when": "on_success"}]:
    raise SystemExit("The common job rules must include merge-request pipelines.")
for name, job in ci.items():
    if (
        isinstance(job, dict)
        and "script" in job
        and not name.startswith(".")
        and job.get("extends") != ".veltryq_job"
    ):
        raise SystemExit("CI job must inherit the explicit pipeline rules: " + name)
for name in ("financial_workflow_postgres", "financial_workflow_sqlite", "security_checks"):
    if ci[name]["stage"] not in ci["stages"]:
        raise SystemExit("Missing CI stage.")
print(
    "Offline YAML structure and tool authority checks passed. GitLab CI Lint/flow registration remain external checks."
)
