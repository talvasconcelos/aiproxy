import asyncio

from fastapi import APIRouter
from lnbits.db import Database
from loguru import logger

from .tasks import wait_for_paid_invoices
from .views import aiproxy_ext_generic
from .views_api import aiproxy_ext_api

db = Database("ext_aiproxy")

scheduled_tasks: list[asyncio.Task] = []

aiproxy_ext: APIRouter = APIRouter(prefix="/aiproxy", tags=["aiproxy"])
aiproxy_ext.include_router(aiproxy_ext_generic)
aiproxy_ext.include_router(aiproxy_ext_api)

aiproxy_static_files = [
    {
        "path": "/aiproxy/static",
        "name": "aiproxy_static",
    }
]


def aiproxy_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def aiproxy_start():
    from lnbits.tasks import create_permanent_unique_task

    task = create_permanent_unique_task("ext_testing", wait_for_paid_invoices)
    scheduled_tasks.append(task)
