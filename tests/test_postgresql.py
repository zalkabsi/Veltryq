"""Run the complete service contract against a disposable PostgreSQL schema."""

from __future__ import annotations

import os
import unittest
from uuid import uuid4

from app.refunds import RefundService
from app.storage import Storage
from tests import test_refunds as service_contract


@unittest.skipUnless(
    os.getenv("VELTRYQ_TEST_DATABASE_URL"), "disposable PostgreSQL URL not configured"
)
class PostgreSQLRefundTests(service_contract.RefundServiceTests):
    def setUp(self) -> None:
        self.storage = Storage(
            os.environ["VELTRYQ_TEST_DATABASE_URL"], schema="veltryq_" + uuid4().hex
        )
        self.storage.initialize()
        self.assertEqual(self.storage.dialect, "postgresql")
        self.service = RefundService(self.storage)

    def tearDown(self) -> None:
        self.storage.close(drop_test_schema=True)
