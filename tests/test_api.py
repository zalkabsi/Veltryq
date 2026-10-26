from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

import httpx

from app.main import create_app
from app.storage import Storage


class ApiTests(unittest.TestCase):
    def test_payment_capture_idempotent_refund_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            api = create_app(Storage(Path(temporary_directory) / "api.db", repaired=True))

            async def exercise() -> None:
                transport = httpx.ASGITransport(app=api)
                async with httpx.AsyncClient(
                    transport=transport, base_url="http://testserver"
                ) as client:
                    created = await client.post(
                        "/payments", json={"amount_minor": 10_000, "currency": "USD"}
                    )
                    self.assertEqual(created.status_code, 201)
                    payment_id = created.json()["id"]
                    captured = await client.post(f"/payments/{payment_id}/capture")
                    self.assertEqual(captured.status_code, 200)
                    url = f"/payments/{payment_id}/refunds"
                    headers = {"Idempotency-Key": "api-retry"}
                    first = await client.post(url, json={"amount_minor": 2_500}, headers=headers)
                    second = await client.post(url, json={"amount_minor": 2_500}, headers=headers)
                    self.assertEqual(first.status_code, 201)
                    self.assertEqual(first.json()["id"], second.json()["id"])
                    history = await client.get(f"/payments/{payment_id}/history")
                    self.assertEqual(len(history.json()["refunds"]), 1)

            asyncio.run(exercise())

    def test_missing_idempotency_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            api = create_app(Storage(Path(temporary_directory) / "api.db"))

            async def exercise() -> None:
                transport = httpx.ASGITransport(app=api)
                async with httpx.AsyncClient(
                    transport=transport, base_url="http://testserver"
                ) as client:
                    payment = (await client.post("/payments", json={"amount_minor": 100})).json()
                    await client.post(f"/payments/{payment['id']}/capture")
                    response = await client.post(
                        f"/payments/{payment['id']}/refunds", json={"amount_minor": 1}
                    )
                    self.assertEqual(response.status_code, 422)

            asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
