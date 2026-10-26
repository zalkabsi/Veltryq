"""Join genuine local/CI artifacts without inventing an approval or Duo session."""

import hashlib
import json
from pathlib import Path

from veltryq.engine.context import execution_context

root = Path("artifacts")
records = {}
for relative in (
    "sqlite/evidence.json",
    "postgresql/evidence.json",
    "verification/bandit.json",
    "verification/pip-audit.json",
    "packages/manifest.json",
):
    path = root / relative
    if not path.is_file():
        raise SystemExit("Required execution artifact is missing: " + relative)
    records[relative] = {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "record": json.loads(path.read_text()),
    }
summary = {
    **execution_context("artifacts"),
    "records": records,
    "reviewer_decision": "required",
    "native_duo_session": "not_recorded",
    "pipeline_status": "consult live pipeline; report is generated before this job completes",
    "production_promotion": "not_requested",
}
candidate = root / "verification/candidate-regression.json"
if candidate.is_file():
    summary["candidate_regression"] = {
        "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "record": json.loads(candidate.read_text()),
    }
summary.pop("artifact_urls", None)
(root / "governance.json").write_text(json.dumps(summary, indent=2) + "\n")
print("Governance record written from actual artifacts; human review remains required.")
