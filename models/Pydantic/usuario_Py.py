from pydantic import BaseModel
from typing import Optional

class UsuarioBase(BaseModel):
    nombre: str
    password: str

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    password: str
    id_rol: int

class UsuarioEdit(BaseModel):
    id: int
    nombre: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    id_rol: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData (BaseModel):
    username: str


class UsuarioDelete(BaseModel):
    id: int


    class Config:
        from_attributes = True