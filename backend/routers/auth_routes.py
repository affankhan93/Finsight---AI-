from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend import crud, schemas
from backend.auth import hash_password, verify_password, create_access_token
from backend.database import get_db

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new account."""
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail='Username already take')
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Store only the hashed password, never the real one
    return crud.create_user(db, user.username, user.email, hash_password(user.password))

@router.post('/login', response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Log in with username + password and get a JWT token back. (sent as form data, which the OAuth2 stardard.)"""
    user = crud.get_user_by_username(db, form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Wrong username or password')
    
    return {'access_token': create_access_token(user.username), 'token_type' : 'bearer'}


