from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import models
from models.models import Category
from typing import Annotated
from pydantic import BaseModel, Field



category_router = APIRouter()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbDep = Annotated[Session, Depends(get_db)]

class CategoryCreate(BaseModel):
    title: str


@category_router.get("/")
async def events(db:dbDep):
    devotional = db.query(Category).all()
    return devotional


@category_router.post("/")
async def events(db:dbDep, category:CategoryCreate):
    existing_category = db.query(Category).filter(Category.title == category.title).first()
    if existing_category:
        raise HTTPException(status_code=404, detail="this category already exists")
    
    category_credentials = category.dict()
    new_category = Category(**category_credentials)

    db.add(new_category)
    db.commit()

    return{
        "message": "sucessfully added",
        "category": f"{new_category.title}"
    }
    
    
    
    
