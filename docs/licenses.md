# Dependency licenses

Reviewed from the installed distribution metadata and upstream package records
on October 26, 2026. Runtime and development versions/artifact hashes are pinned
in requirements.lock and requirements-dev.lock. A resolved inventory is exported
in artifacts/verification/dependencies.json.

| Dependency | Role | License |
|---|---|---|
| FastAPI, SQLAlchemy, Pydantic | Runtime | MIT |
| Uvicorn, HTTPX | Runtime / tests | BSD-3-Clause |
| Psycopg, psycopg-binary | PostgreSQL driver | LGPL-3.0-only |
| greenlet | SQLAlchemy runtime | MIT AND PSF-2.0 |
| pytest, Ruff, PyYAML, build, pip-tools | Development | MIT or upstream permissive notices |
| Bandit, pip-audit | Security checks | Apache-2.0 |

Veltryq's own source remains MIT licensed. Psycopg is a separately distributed
LGPL library; its license is not replaced by Veltryq's MIT license. Preserve
upstream license notices and applicable LGPL source/replacement rights when
distributing the image. The binary driver also bundles libpq and other
libraries whose licenses remain applicable.

The image preserves Python distribution license files and includes
THIRD_PARTY_NOTICES.md. Base image OS packages retain their own licenses.
Consult per-version license files in installed .dist-info directories for
complete notices. This table is a practical dependency review, not a claim
that every dependency is MIT licensed.

The Python vulnerability audit is separate from this license inventory.
