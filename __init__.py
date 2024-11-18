import asyncio

from fastapi import APIRouter
from lnbits.db import Database
from loguru import logger

from .tasks import wait_for_paid_invoices
from .views import ai_proxy_ext_generic
from .views_api import ai_proxy_ext_api

db = Database("ext_ai_proxy")

scheduled_tasks: list[asyncio.Task] = []

ai_proxy_ext: APIRouter = APIRouter(prefix="/ai_proxy", tags=["ai_proxy"])
ai_proxy_ext.include_router(ai_proxy_ext_generic)
ai_proxy_ext.include_router(ai_proxy_ext_api)

ai_proxy_static_files = [
    {
        "path": "/ai_proxy/static",
        "name": "ai_proxy_static",
    }
]


def ai_proxy_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def ai_proxy_start():
    from lnbits.tasks import create_permanent_unique_task

    task = create_permanent_unique_task("ext_testing", wait_for_paid_invoices)
    scheduled_tasks.append(task)
