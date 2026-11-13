import os 
import jwt
from datetime import datetime, timedelta, timezone 
from jwt.exceptions import InvalidTokenError 
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from backend import crud
from backend.database import get_db 

# Working: 1. User logs in with username + password -> we return a JWT token.
         # 2. User sends the token in every later request (Authorization: Bearer <token>).
         # 3. get_current_user() reads the token and tells us who the user is.

load_dotenv() 

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30 

password_hash = PasswordHash.recommended() # secure hashing (argon 2)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

# passwords 
def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

# Tokens 
def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {'sub': username, 'exp': expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Use as a dependency on any endpoint that needs a logged-in user."""
    error = HTTPException(
        status_code=401, 
        detail='Invalid or expired token', 
        headers={"WWW-Authenticate": 'Bearer'},
    )
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except InvalidTokenError:
        raise error 

    if username is None:
        raise error 

    user = crud.get_user_by_username(db, username)
    if user is None:
        raise error 
    return user 


