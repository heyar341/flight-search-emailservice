from pydantic import BaseModel
from pydantic import EmailStr


class TokenIn(BaseModel):
    token: str
    manipulation: str


class TokenOut(BaseModel):
    email: EmailStr
