"""Fixed ordinary-test demonstration for the synthetic vulnerable fixture."""

import json

from veltryq.engine.scenarios import run_baseline

result = run_baseline()
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["verdict"] == "passed" else 1)
