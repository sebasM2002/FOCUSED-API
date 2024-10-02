from jose import JWTError
import jwt  
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import secrets
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from typing import Optional
from models.Pydantic.usuario_Py import UsuarioCreate


SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/token/")

# Utility function for encrypting usernames
def encrypt_username(username: str):
    return pwd_context.hash(username)

# Utility function for hashing passwords
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user(user: str, db: AsyncSession):

    query = text("SELECT * FROM usuario WHERE nombre = :nombre")
    result = await db.execute(query, {"nombre": user})
    user_record = result.fetchone()

    if user_record:
        return UsuarioCreate(
            nombre= user,
            email= user_record.email,
            password= user_record.password,
            id_rol= user_record.id_rol

        )


async def authenticate_user (username: str, password: str, db: AsyncSession):
    user = await get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    
    return user


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(username, db)
    if user is None:
        raise credentials_exception
    return user