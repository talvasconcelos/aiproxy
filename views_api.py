from http import HTTPStatus

import httpx
from fastapi import Depends, Query
from starlette.exceptions import HTTPException

from lnbits.core.crud import get_standalone_payment, get_user
from lnbits.core.services import create_invoice
from lnbits.decorators import WalletTypeInfo, get_key_type, require_admin_key

from . import aiproxy_ext
from .crud import (
    create_link,
    create_user,
    delete_link,
    get_aiproxy_user,
    get_link,
    get_links,
    update_aiproxy_user,
    update_link,
)
from .models import CreateLink, CreateUser, User


@aiproxy_ext.get("/api/v1/links")
async def api_links(all_wallets: bool = Query(False), wallet: WalletTypeInfo = Depends(get_key_type)):
    wallet_ids = [wallet.wallet.id]

    if all_wallets:
        user = await get_user(wallet.wallet.user)
        wallet_ids = user.wallet_ids if user else []

    return [event.dict() for event in await get_links(wallet_ids)]

@aiproxy_ext.post("/api/v1/links")
@aiproxy_ext.put("/api/v1/links/{link_id}")
async def api_link_create(
    data: CreateLink, link_id=None, wallet: WalletTypeInfo = Depends(get_key_type)
):
    if link_id:
        link = await get_link(link_id)
        if not link:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Link does not exist."
            )

        if link.wallet != wallet.wallet.id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="Not your link."
            )
        link = await update_link(link_id, **data.dict())
    else:
        link = await create_link(data=data)
        assert link

    return link.dict()

@aiproxy_ext.delete("/api/v1/links/{link_id}")
async def api_link_delete(link_id: str, wallet: WalletTypeInfo = Depends(require_admin_key)):
    link = await get_link(link_id)
    if not link:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Link does not exist."
        )

    if link.wallet != wallet.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your link."
        )

    await delete_link(link_id)

    return "", HTTPStatus.NO_CONTENT

## Users
@aiproxy_ext.get("/api/v1/payments/{link_id}/{uses}")
async def api_payment(link_id: str, uses: str):
    link = await get_link(link_id)
    if not link:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Link does not exist."
        )
    invoice_amount = link.cost * int(uses)
    try:
        payment_hash, payment_request = await create_invoice(
            wallet_id=link.wallet,
            amount=invoice_amount,
            memo=f"Payment for {link_id}",
            extra={"tag": "aiproxy", "link": link_id, "uses": uses},
        )
        
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
    
    return {"payment_hash": payment_hash, "payment_request": payment_request}

@aiproxy_ext.get("/api/v1/payment/{link_id}/{payment_hash}/{uses}")
async def api_payment_status(link_id: str, payment_hash: str, uses: str):
    link = await get_link(link_id)
    if not link:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Link does not exist."
        )

    payment = await get_standalone_payment(payment_hash)
    assert payment
    if not payment.pending and (int(uses) * link.cost) * 1000 == payment.amount:
        return {"paid": True}

    return {"paid": False}

@aiproxy_ext.post("/api/v1/users")
async def api_user_create(
    data: CreateUser
) -> User:
    link = await get_link(data.link)
    if not link:    
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Link does not exist."
        )
    user = await create_user(data=data)
    assert user
    return user.dict()


## PROXY ENDPOINTS
@aiproxy_ext.post("/api/v1/proxy/{user_id}")
async def api_proxy(user_id: str, data: str):
    user = await get_aiproxy_user(user_id)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User does not exist."
        )
    if user.uses == 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="No more uses left."
        )
    link = await get_link(user.link)
    assert link

    url = (f"{user.link}")
    
    if link.api_key:
        auth = f"Bearer {link.api_key}"
    else:
        auth = None

    header = {
        "Authorization": auth,
        "Content-Type": "application/json",
    }
    # Make the call to the API and return the response
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                url,
                headers=header,
                json={}, #TODO: Add data here
                timeout=None,
            )
            ai_response = r.json()

        except AssertionError:
            ai_response = {"error": "Error occured"}
        finally:
            #sutract one use
            user.uses -= 1 
            #update user
            await update_aiproxy_user(user_id, uses=user.uses)
    return ai_response #["choices"][0]["text"]

## sample response from OpenAI
# {
#   "choices": [
#     {
#       "finish_reason": "length",
#       "index": 0,
#       "logprobs": null,
#       "text": "\n\n\"Let Your Sweet Tooth Run Wild at Our Creamy Ice Cream Shack"
#     }
#   ],
#   "created": 1683130927,
#   "id": "cmpl-7C9Wxi9Du4j1lQjdjhxBlO22M61LD",
#   "model": "text-davinci-003",
#   "object": "text_completion",
#   "usage": {
#     "completion_tokens": 16,
#     "prompt_tokens": 10,
#     "total_tokens": 26
#   }
# }