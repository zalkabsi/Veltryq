"""Allow-listed execution provenance, without credentials or arbitrary environment dumps."""

from __future__ import annotations

import os
import re
from pathlib import PurePosixPath
from urllib.parse import urlsplit


def public_url(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = urlsplit(value)
        if (
            parsed.scheme == "https"
            and parsed.hostname
            and not parsed.username
            and not parsed.password
        ):
            return value.rstrip("/")
    except ValueError:
        return None
    return None


def execution_context(output: str, env: dict[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    project = public_url(values.get("CI_PROJECT_URL"))
    job = public_url(values.get("CI_JOB_URL"))
    sha = values.get("CI_COMMIT_SHA", "")
    source_sha = values.get("CI_MERGE_REQUEST_SOURCE_BRANCH_SHA", "")
    iid = values.get("CI_MERGE_REQUEST_IID", "")
    relative = PurePosixPath(output)
    artifact_base = (
        f"{job}/artifacts/file/{relative.as_posix()}"
        if job and not relative.is_absolute() and ".." not in relative.parts
        else None
    )
    return {
        "source_commit_sha": sha if re.fullmatch(r"[0-9a-f]{40,64}", sha) else None,
        "merge_request_source_sha": source_sha
        if re.fullmatch(r"[0-9a-f]{40,64}", source_sha)
        else None,
        "merge_request_url": f"{project}/-/merge_requests/{iid}"
        if project and iid.isdigit()
        else None,
        "pipeline_url": public_url(values.get("CI_PIPELINE_URL")),
        "job_url": job,
        "execution_channel": "gitlab_ci" if values.get("GITLAB_CI") == "true" else "local",
        "artifact_urls": {
            name: f"{artifact_base}/{name}"
            for name in (
                "evidence.html",
                "evidence.json",
                "repair.patch",
                "regression.json",
                "review.md",
            )
        }
        if artifact_base
        else {},
        "gitlab_duo_execution": "not_recorded",
    }
