from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from app.config.config import config
from app.database.database import get_db_connection, generate_api_key

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

async def verify_api_key(apikey: str = Header(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT api_key FROM users WHERE api_key = %s", (apikey,))
    valid_key = cursor.fetchone()
    conn.close()
    if not valid_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return apikey

async def get_current_user(token: str = Depends(oauth2_scheme), apikey: str = Depends(verify_api_key)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, api_key FROM users WHERE username = %s AND api_key = %s", (username, apikey))
    user = cursor.fetchone()
    conn.close()
    if user is None:
        raise credentials_exception
    return {"username": user["username"], "role": user["role"], "api_key": user["api_key"]}

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user["username"] not in config.ADMIN_USERS:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
