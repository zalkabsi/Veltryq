# syntax=docker/dockerfile:1
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /workspace
COPY requirements.lock ./
RUN --mount=type=secret,id=proxy_ca,required=false \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    python -m pip install --disable-pip-version-check --no-cache-dir --require-hashes -r requirements.lock
COPY pyproject.toml README.md LICENSE THIRD_PARTY_NOTICES.md ./
COPY app ./app
COPY veltryq ./veltryq
RUN python -m pip install --disable-pip-version-check --no-index --no-cache-dir --no-deps --no-build-isolation . \
    && useradd --uid 10001 --create-home veltryq \
    && chmod -R a+rX /workspace \
    && mkdir -p /workspace/artifacts \
    && chown 10001:10001 /workspace/artifacts
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
