import asyncio

from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

from lnbits.db import Database
from lnbits.helpers import template_renderer
from lnbits.tasks import catch_everything_and_restart

db = Database("ext_aiproxy")

aiproxy_ext: APIRouter = APIRouter(prefix="/aiproxy", tags=["aiproxy"])

aiproxy_static_files = [
    {
        "path": "/aiproxy/static",
        "app": StaticFiles(packages=[("lnbits", "extensions/aiproxy/static")]),
        "name": "aiproxy_static",
    }
]


def aiproxy_renderer():
    return template_renderer(["lnbits/extensions/aiproxy/templates"])


from .tasks import wait_for_paid_invoices
from .views import *  # noqa: F401,F403
from .views_api import *  # noqa: F401,F403


def tpos_start():
    loop = asyncio.get_event_loop()
    loop.create_task(catch_everything_and_restart(wait_for_paid_invoices))
