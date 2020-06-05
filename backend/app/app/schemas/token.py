from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str = None
    scopes: str = None
    exp: datetime = None

