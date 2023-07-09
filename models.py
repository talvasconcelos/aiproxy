from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class Link(BaseModel):
    id: str
    wallet: str
    api_url: str = Query(...)
    api_key: str = Query(None)
    description: str = Query(...)
    cost: int = Query(..., ge=0)
    webhook: str = Query(None)

class CreateLink(BaseModel):
    wallet: str
    api_url: str
    api_key: Optional[str]
    description: str
    cost: int
    webhook: Optional[str]

class User(BaseModel):
    id: str
    link: str
    uses: int
    paid: bool

class CreateUser(BaseModel):
    link: str
    uses: int
    paid: bool