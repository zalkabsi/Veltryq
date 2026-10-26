"""Wait at most 30 seconds for the disposable CI database; never print its URL."""

import os
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

engine = create_engine(os.environ["VELTRYQ_TEST_DATABASE_URL"], connect_args={"connect_timeout": 2})
try:
    for attempt in range(15):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("Disposable PostgreSQL database is ready.")
            break
        except OperationalError:
            if attempt == 14:
                raise SystemExit("Disposable PostgreSQL database was unavailable.") from None
            time.sleep(1)
finally:
    engine.dispose()
