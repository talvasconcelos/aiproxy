from http import HTTPStatus

from fastapi import Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from lnbits.core.models import User
from lnbits.decorators import check_user_exists

from . import aiproxy_ext, aiproxy_renderer
from .crud import get_aiproxy_user, get_link

templates = Jinja2Templates(directory="templates")


@aiproxy_ext.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user: User = Depends(check_user_exists),
):
    return aiproxy_renderer().TemplateResponse(
        "aiproxy/index.html", {"request": request, "user": user.dict()}
    )

@aiproxy_ext.get("/pay/{link_id}")
async def pay(
    request: Request,
    link_id: str,
):
    link = await get_link(link_id)
    if not link:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Link does not exist."
        )
    return aiproxy_renderer().TemplateResponse(
        "aiproxy/display.html", {
            "request": request,
            "link_id": link.id,
            "description": link.description,
            "cost": link.cost,
            }
    )

@aiproxy_ext.get("/user/{user_id}")
async def user_page(user_id: str, request: Request):
    user = await get_aiproxy_user(user_id)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User does not exist."
        )
    return aiproxy_renderer().TemplateResponse("aiproxy/user.html", {"request": request, "user": user.dict()})