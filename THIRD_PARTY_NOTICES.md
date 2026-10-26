# Third-party notices

Veltryq source is MIT licensed. Dependencies retain their own licenses.
Installed Python distributions include their upstream license files.

- FastAPI, SQLAlchemy, Pydantic, pytest, Ruff, build, and PyYAML: MIT.
- Uvicorn, HTTPX, Psycopg's bundled libpq: BSD-style licenses.
- Psycopg and psycopg-binary 3.3.6: LGPL-3.0-only. They remain separate installed
  libraries and are not relicensed as MIT. Preserve their license notices and
  the applicable LGPL source/relinking rights when distributing containers.
  Upstream source: https://github.com/psycopg/psycopg
- Bandit and pip-audit: Apache-2.0.

The pinned dependency inventories and installed distribution metadata are the
authoritative per-version records. See docs/licenses.md. Container base images
also retain their own operating-system package licenses.
