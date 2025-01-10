from typing import List, Optional, Union
from uuid import uuid4

from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import CreateLink, CreateUser, Link, User


async def get_links(wallet_ids: Union[str, List[str]]) -> List[Link]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join([f"'{wallet_id}'" for wallet_id in wallet_ids])
    links = await db.fetchall(
        f"SELECT * FROM aiproxy.apilinks WHERE wallet IN ({q})",
        model=Link,
    )
    return links


async def create_link(data: CreateLink) -> Link:
    link_id = urlsafe_short_hash()
    api_link = Link(
        id=link_id,
        **data.dict(),
    )
    await db.insert("aiproxy.apilinks", api_link)
    return api_link


async def get_link(link_id: str) -> Optional[Link]:
    link = await db.fetchone(
        "SELECT * FROM aiproxy.apilinks WHERE id = :id", {"id": link_id}, Link
    )
    return link


async def update_link(link: Link) -> Link:
    await db.update("aiproxy.apilinks", link)
    return link


async def delete_link(link_id: str) -> None:
    await db.execute("DELETE FROM aiproxy.apilinks WHERE id = :id", {"id": link_id})


# USERS
async def get_aiproxy_user(user_id: str) -> Optional[User]:
    return await db.fetchone(
        "SELECT * FROM aiproxy.users WHERE id = :id", {"id": user_id}, User
    )


async def create_user(data: CreateUser) -> User:
    user_id = str(uuid4())
    user = User(id=user_id, **data.dict())
    await db.insert("aiproxy.users", user)
    return user


async def update_aiproxy_user(user: User) -> User:
    await db.update("aiproxy.users", user)
    return user
