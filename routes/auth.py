from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from models import models
from models.models import Admin
from database import engine, SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv
from utlis.security import verify_password

load_dotenv()

auth_router = APIRouter()
models.Base.metadata.create_all(bind=engine)

bycrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth_bearer = OAuth2PasswordBearer("/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
def get_db():  
    db = SessionLocal()  
    try:  
        yield db  
    finally:  
        db.close() 
dbDep = Annotated[Session,Depends(get_db)]

def create_token(email:str, admin_id:int, expires:timedelta):
    #process the expire time
    exp = datetime.now()+expires
    ex = {'sub':email, 'id':admin_id, 'exp': exp}
    return jwt.encode(ex, SECRET_KEY, 'HS256')


@auth_router.post("/login")
async def login_access(requestForm:Annotated[OAuth2PasswordRequestForm, Depends()], db:dbDep):
    username = requestForm.username
    pas = requestForm.password

    #get staff from db
    admin = db.query(Admin).filter(Admin.email == username).first()
    if not admin:
        raise HTTPException( status_code=404, detail="staff cannot be recognized",)
    
    if  not verify_password(pas, admin.password):
        raise HTTPException(status_code=401, detail= "Invalid credentials")
    
    token = create_token(admin.email, admin.id, timedelta(minutes=30))
    return {
        "access_token": token,
        "token_type": "bearer",
        "staff_id": admin.id,
        "email":admin.email
    }