"""Self-contained HTML and JSON evidence, linked to genuine execution provenance."""

from __future__ import annotations

import html
import json
import platform
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from veltryq.engine.context import public_url
from veltryq.engine.remediation import REMEDIATION


def build_report(
    vulnerable: dict[str, Any],
    repaired: dict[str, Any],
    *,
    context: dict[str, object] | None = None,
) -> dict[str, Any]:
    confirmed = vulnerable["verdict"] == "confirmed_violation"
    passed = repaired["verdict"] == "passed" and not repaired["errors"]
    verdict = "inconclusive"
    if confirmed and passed:
        verdict = "confirmed_violation_repaired"
    elif vulnerable["verdict"] == "passed" and passed:
        verdict = "selected_checks_passed"
    return {
        "schema_version": "1.1",
        "project": "Veltryq",
        "generated_at": datetime.now(UTC).isoformat(),
        "analysis_scope": f"known synthetic refund adapter on {vulnerable['database']}",
        "overall_verdict": verdict,
        "invariants_tested": [
            "FIN-IDEMPOTENCY",
            "FIN-REFUND-LIMIT",
            "FIN-LEDGER-BALANCE",
        ],
        "violations_confirmed": vulnerable["violations"] if confirmed else [],
        "risk_level": "critical"
        if confirmed
        else "none_observed"
        if verdict == "selected_checks_passed"
        else "inconclusive",
        "remediation_status": "regression_passed" if confirmed and passed else "not_verified",
        "source_location": {
            "file": "veltryq/fixtures/refund_vulnerable.py",
            "function": "FixtureRefundService._refund_transaction",
            "mechanism": "prechecks occur outside the locked write transaction",
        },
        "remediation": {
            "file": "examples/demo/refund_candidate.py",
            "function": "FixtureRefundService._refund_transaction",
            "guidance": REMEDIATION["FIN-IDEMPOTENCY"],
        },
        "reproduction_commands": [
            "python -m veltryq.cli regression --implementation vulnerable",
            "python -m veltryq.cli regression --implementation repaired",
        ],
        "source_commit_sha": None,
        "merge_request_url": None,
        "pipeline_url": None,
        "artifact_urls": {},
        "gitlab_duo_execution": "not_recorded",
        "execution_environment": {
            "python": platform.python_version(),
            "database": vulnerable["database"] + " " + vulnerable["database_version"],
        },
        "limitations": [
            "One finite deterministic contract is not a formal proof of financial safety.",
            "Only the hash-matched synthetic source adapter is supported.",
            "Repair verification creates a fresh schema; existing duplicate rows require reviewed reconciliation.",
            "A local or CI run is not evidence that a native GitLab Duo flow executed.",
        ],
        "before": vulnerable,
        "after": repaired,
        **(context or {}),
    }


def write_report(report: dict[str, Any], output_directory: str | Path) -> tuple[Path, Path]:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    json_path, html_path = output / "evidence.json", output / "evidence.html"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    html_path.write_text(render_html(report), encoding="utf-8")
    return json_path, html_path


def render_html(report: dict[str, Any]) -> str:
    def esc(value: object) -> str:
        return html.escape(str(value if value is not None else "not recorded"))

    before, after = report.get("before", {}), report.get("after", {})
    metrics = (
        ("Refund rows", "refund_count"),
        ("Refunded (minor units)", "total_refunded_minor"),
        ("Ledger entries", "refund_ledger_entry_count"),
        ("Verdict", "verdict"),
    )
    rows = "".join(
        f"<tr><td>{esc(label)}</td><td>{esc(before.get(key))}</td>"
        f"<td>{esc(after.get(key))}</td></tr>"
        for label, key in metrics
    )
    urls = {key: report.get(key) for key in ("merge_request_url", "pipeline_url", "job_url")}
    urls.update(report.get("artifact_urls", {}))
    links = (
        "".join(
            f'<li>{esc(name)}: <a href="{esc(url)}" rel="noreferrer">{esc(url)}</a></li>'
            for name, url in urls.items()
            if public_url(url)
        )
        or "<li>No remote links recorded for this execution.</li>"
    )
    trace = "".join(
        f"<tr><td>{esc(item['stage'])}</td><td>{esc(item['status'])}</td>"
        f"<td>{esc(item['elapsed_seconds'])}</td></tr>"
        for item in report.get("trace", [])
    )
    patch = report.get("repair_proposal") or {}
    patch_html = (
        "<pre><code>" + esc(patch["diff"]) + "</code></pre>"
        if patch
        else "<p>No source repair proposed for this execution.</p>"
    )
    checks = (
        "".join(
            f"<li><code>{esc(item)}</code></li>" for item in report.get("violations_confirmed", [])
        )
        or "<li>No confirmed violations in this execution.</li>"
    )
    limitations = "".join(f"<li>{esc(item)}</li>" for item in report.get("limitations", []))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Veltryq · Financial integrity evidence</title><style>
:root{{--bg:#08111f;--panel:#111e30;--line:#29415d;--text:#edf4ff;--muted:#afc1d7;--cyan:#67e8f9}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 system-ui,sans-serif}}
main{{max-width:1120px;margin:auto;padding:38px 22px 70px}}header{{padding:12px 0 25px}}
h1{{font-size:clamp(30px,5vw,46px);line-height:1.1}}h2{{font-size:21px;margin-top:0}}
.eyebrow,code,a{{color:var(--cyan)}}.muted{{color:var(--muted)}}a{{overflow-wrap:anywhere}}
section,.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px;margin:16px 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:15px}}
.metric{{font-size:24px;font-weight:700}}table{{width:100%;border-collapse:collapse}}
th,td{{text-align:left;padding:10px;border-bottom:1px solid var(--line)}}pre{{overflow:auto;padding:15px;background:#070e18}}
.badge{{border:1px solid var(--cyan);border-radius:20px;padding:5px 12px;display:inline-block}}
@media(max-width:600px){{main{{padding:20px 12px}}section{{overflow:auto}}}}
</style></head><body><main><header><div class="eyebrow">VELTRYQ / EXECUTION EVIDENCE</div>
<h1>Refund integrity review</h1><span class="badge">{esc(report["overall_verdict"])}</span>
<p class="muted">{esc(report.get("analysis_scope"))}<br>Generated: {esc(report.get("generated_at"))}</p></header>
<div class="grid"><div class="card"><div class="muted">Invariants executed</div>
<div class="metric">{len(report.get("invariants_tested", []))}</div></div>
<div class="card"><div class="muted">Confirmed violations</div>
<div class="metric">{len(report.get("violations_confirmed", []))}</div></div>
<div class="card"><div class="muted">Repair status</div>
<div class="metric">{esc(report.get("remediation_status"))}</div></div></div>
<section><h2>Before and after</h2><p>Captured: {esc(before.get("captured_amount_minor"))} minor units.</p>
<table><thead><tr><th>Measure</th><th>Candidate</th><th>Verified repair</th></tr></thead><tbody>{rows}</tbody></table>
<ul>{checks}</ul><p>Baseline: {esc(report.get("baseline", {}).get("verdict"))}</p></section>
<section><h2>Concrete repair proposal</h2><p>Strategy: {esc(patch.get("strategy"))}. Human review required.</p>
{patch_html}<p>Unchanged regression contract SHA-256:
<code>{esc(report.get("regression_contract_sha256"))}</code></p></section>
<section><h2>Execution provenance</h2><p>Tested commit: <code>{esc(report.get("source_commit_sha"))}</code></p>
<p>Candidate source SHA-256: <code>{esc(report.get("candidate_source_sha256"))}</code></p>
<p>Environment: {esc(report.get("execution_environment"))}</p>
<p>Native Duo execution: {esc(report.get("gitlab_duo_execution"))}</p><ul>{links}</ul></section>
<section><h2>Measured execution trace</h2><table><thead><tr><th>Stage</th><th>Result</th>
<th>Elapsed seconds</th></tr></thead><tbody>{trace}</tbody></table></section>
<section><h2>Scope and limitations</h2><ul>{limitations}</ul>
<p>Amounts and records are synthetic. Finite checks do not prove arbitrary financial systems safe.</p></section>
</main></body></html>"""
