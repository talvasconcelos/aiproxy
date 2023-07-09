from typing import List, Optional, Union
from uuid import uuid4

from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import CreateLink, CreateUser, Link, User


async def get_links(wallet_ids: Union[str, List[str]]) -> List[Link]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM aiproxy.apilinks WHERE wallet IN ({q})", (*wallet_ids,)
    )
    return [Link(**row) for row in rows]

async def create_link(data: CreateLink) -> Link:
    link_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO aiproxy.apilinks (id, wallet, api_url, api_key, description, cost, webhook)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            link_id,
            data.wallet,
            data.api_url,
            data.api_key,
            data.description,
            data.cost,
            data.webhook,
        ),
    )
    return await get_link(link_id)

async def get_link(link_id: str) -> Optional[Link]:
    row = await db.fetchone("SELECT * FROM aiproxy.apilinks WHERE id = ?", (link_id,))
    return Link(**row) if row else None

async def update_link(link_id: str, **kwargs) -> Optional[Link]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(f"UPDATE aiproxy.apilinks SET {q} WHERE id = ?", (*kwargs.values(), link_id))
    link = await get_link(link_id)
    assert link, "Newly updated link couldn't be retrieved"
    return link

async def delete_link(link_id: str) -> None:
    await db.execute("DELETE FROM aiproxy.apilinks WHERE id = ?", (link_id,))


# USERS
async def get_aiproxy_user(user_id: str) -> Optional[User]:
    row = await db.fetchone("SELECT * FROM aiproxy.users WHERE id = ?", (user_id,))
    return User(**row) if row else None

async def create_user(data: CreateUser) -> User:
    user_id = str(uuid4())
    await db.execute(
        """
        INSERT INTO aiproxy.users (id, link, uses, paid)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            data.link,
            data.uses,
            data.paid,
        ),
    )
    return await get_aiproxy_user(user_id)

async def update_aiproxy_user(user_id: str, **kwargs) -> Optional[User]:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(f"UPDATE aiproxy.users SET {q} WHERE id = ?", (*kwargs.values(), user_id))
    user = await get_aiproxy_user(user_id)
    assert user, "Newly updated user couldn't be retrieved"
    return user