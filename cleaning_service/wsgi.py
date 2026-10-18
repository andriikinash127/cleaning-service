
"""
WSGI config for cleaning_service project.
"""

import os

from django.core.wsgi import get_wsgi_application
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cleaning_service.settings")

application = get_wsgi_application()

try:
    connection.ensure_connection()
    print(
        f"DATABASE CHECK: vendor={connection.vendor}, connected=True",
        flush=True,
    )
except Exception as exc:
    print(
        f"DATABASE CHECK FAILED: vendor={connection.vendor}, "
        f"error={type(exc).__name__}",
        flush=True,
    )
