from  fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Annotated, Literal
from pydantic import Field, BaseModel
from database import SessionLocal, engine
from models import models
from models.models import Admin
from utlis.security import hash_password


admin_router = APIRouter()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbDep = Annotated[Session, Depends(get_db)]

class AdminCreate(BaseModel):
    fullname: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=8)



@admin_router.get("/")
async def get_users(db:dbDep):
    admin = db.query(Admin).order_by(Admin.id).all()
    return [
    {
        "id": u.id,
        "name": u.fullname,
        "email": u.email,
    }
    for u in admin
]

@admin_router.post("/")
async def users(db:dbDep, admin:AdminCreate):
    existing_admin = db.query(Admin).filter(Admin.fullname == admin.fullname).first()
    if existing_admin:
        raise HTTPException(status_code=404, detail="user already exists")

    user_credentials = admin.dict()
    user_credentials["password"] = hash_password(user_credentials["password"])
    

    new_admin = Admin(**user_credentials)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {
        "message": "user sucessfully added", 
        "user": {
            "id": new_admin.id,
            "name": new_admin.fullname,
            "email": new_admin.email,
        }
    }

@admin_router.delete("/")
async def admin(db:dbDep, admin:int):
    admin = db.query(Admin).filter(Admin.id == admin).first()

    db.delete(admin)
    db.commit()

    return{"delete successful"}





