from http import HTTPStatus

import httpx
from fastapi import APIRouter, Depends, HTTPException
from lnbits.decorators import require_invoice_key

from .models import Example

# views_api.py is for you API endpoints that could be hit by another service

aiproxy_ext_api = APIRouter(
    prefix="/api/v1",
    tags=["aiproxy"],
)


@aiproxy_ext_api.get("/test/{aiproxy_data}", description="Example API endpoint")
async def api_aiproxy(aiproxy_data: str) -> Example:
    if aiproxy_data != "00000000":
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid aiproxy data",
        )
    # Do some python things and return the data
    return Example(id="2", wallet=aiproxy_data)


@aiproxy_ext_api.get(
    "/vetted",
    description="Get the vetted extension readme",
    dependencies=[Depends(require_invoice_key)],
)
async def api_get_vetted():
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://raw.githubusercontent.com/lnbits/lnbits-extensions/main/README.md"
        )
        return resp.text
