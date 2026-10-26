"""Record actual package bytes and their source commit."""

import hashlib
import json
import os
from pathlib import Path

root = Path("artifacts/packages")
packages = [
    {
        "name": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": path.stat().st_size,
    }
    for path in sorted(root.iterdir())
    if path.suffix == ".whl" or path.name.endswith(".tar.gz")
]
if not packages:
    raise SystemExit("No built packages were found.")
(root / "manifest.json").write_text(
    json.dumps(
        {
            "source_commit_sha": os.getenv("CI_COMMIT_SHA"),
            "packages": packages,
        },
        indent=2,
    )
    + "\n"
)
