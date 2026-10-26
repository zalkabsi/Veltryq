"""Exercise the real local container API using synthetic records only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://127.0.0.1:58000")
parser.add_argument("--out", type=Path, default=Path("artifacts/verification/container-smoke.json"))
args = parser.parse_args()
checks = []
with httpx.Client(base_url=args.url, timeout=10) as client:
    health = client.get("/health")
    checks.append(
        {"check": "health", "status": health.status_code, "passed": health.status_code == 200}
    )
    created = client.post("/payments", json={"amount_minor": 10000, "currency": "USD"})
    created.raise_for_status()
    payment = created.json()["id"]
    captured = client.post(f"/payments/{payment}/capture")
    captured.raise_for_status()
    headers = {"Idempotency-Key": "container-smoke"}
    endpoint = f"/payments/{payment}/refunds"
    first = client.post(endpoint, json={"amount_minor": 2500}, headers=headers)
    replay = client.post(endpoint, json={"amount_minor": 2500}, headers=headers)
    first.raise_for_status()
    replay.raise_for_status()
    checks.append(
        {"check": "idempotent_replay", "passed": first.json()["id"] == replay.json()["id"]}
    )
    conflict = client.post(endpoint, json={"amount_minor": 2000}, headers=headers)
    checks.append(
        {
            "check": "conflicting_payload",
            "status": conflict.status_code,
            "passed": conflict.status_code == 409,
        }
    )
    limit = client.post(
        endpoint, json={"amount_minor": 10000}, headers={"Idempotency-Key": "over-limit"}
    )
    checks.append(
        {"check": "refund_limit", "status": limit.status_code, "passed": limit.status_code == 409}
    )
    invalid = client.post("/payments", json={"amount_minor": True})
    checks.append(
        {
            "check": "strict_money",
            "status": invalid.status_code,
            "passed": invalid.status_code == 422,
        }
    )
    history = client.get(f"/payments/{payment}/history").json()
    checks.append(
        {
            "check": "persisted_state",
            "passed": len(history["refunds"]) == 1 and history["payment"]["refunded_minor"] == 2500,
        }
    )
result = {
    "verdict": "passed" if all(c["passed"] for c in checks) else "failed",
    "checks": checks,
    "history": history,
    "scope": "local container API, synthetic payment",
}
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"verdict": result["verdict"], "checks": len(checks), "report": str(args.out)}))
raise SystemExit(0 if result["verdict"] == "passed" else 1)
