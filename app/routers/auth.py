from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import verify_password, create_access_token, get_db_connection, get_admin_user, verify_api_key, generate_api_key
from datetime import timedelta
from app.config.config import config

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), apikey: str = Depends(verify_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND api_key = %s", (form_data.username, apikey))
    user = cursor.fetchone()
    conn.close()
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username, password or API Key", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "Bearer", "api_key": user["api_key"]}

@router.post("/register", dependencies=[Depends(get_admin_user)])
async def register_user(username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = get_password_hash(password)
    new_api_key = generate_api_key()
    cursor.execute("INSERT INTO users (username, hashed_password, role, api_key) VALUES (%s, %s, %s, %s) RETURNING id, api_key", (username, hashed_password, "user", new_api_key))
    new_user = cursor.fetchone()
    conn.commit()
    conn.close()
    return {"id": new_user["id"], "username": username, "role": "user", "api_key": new_user["api_key"]}
